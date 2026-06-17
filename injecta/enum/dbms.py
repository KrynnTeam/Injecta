"""
Injecta — Database enumeration (sqlmap-style extraction)
"""
from typing import Any, Dict, List
from injecta.enum.extract import extract_clean, split_groupped


class DBMSEnumerator:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "") if payloads else ""

    def enumerate(self, url: str, param: str) -> List[str]:
        databases = []
        queries = self.payloads.databases()
        cols = self.info.get("column_count", 1)
        pos = self.info.get("data_pos", 1)

        for q in queries:
            results = extract_clean(self.req, url, param, q, cols, pos, self.dbms)
            if results:
                for r in results:
                    databases.extend(split_groupped(r))
                break

        return list(set(databases))
