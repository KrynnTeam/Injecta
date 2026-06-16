"""
Injecta — Example custom payload plugin
"""
from injecta.plugins.loader import BasePlugin
from typing import Any, Dict, Optional


class LogAllPayloadsPlugin(BasePlugin):
    name = "payload_logger"
    description = "Logs all payloads sent during scan"
    version = "1.0"
    author = "Kael / Krynn Team"

    def __init__(self):
        self.payloads_logged = 0

    def initialize(self, engine) -> None:
        self.engine = engine

    def on_scan_start(self, url: str) -> None:
        self.payloads_logged = 0
        if self.engine:
            self.engine.log.debug(f"[Plugin] Scan started: {url}")

    def on_payload(self, payload: str, dbms: str) -> str:
        self.payloads_logged += 1
        dbg = getattr(self, "engine", None)
        if dbg and hasattr(dbg, "log"):
            dbg.log.debug2(f"[Plugin] Payload #{self.payloads_logged}: {payload[:80]}...")
        return payload

    def on_scan_complete(self, url: str, results: Dict[str, Any]) -> None:
        dbg = getattr(self, "engine", None)
        if dbg and hasattr(dbg, "log"):
            dbg.log.info(f"[Plugin] Scan complete: {self.payloads_logged} payloads sent")
