"""
Injecta — WebSocket security scanner
"""
import json
import re
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


WS_PAYLOADS = [
    "{'$ne': ''}",
    '{"$gt": ""}',
    "' OR '1'='1",
    "'; SELECT 1; --",
    "<script>alert(1)</script>",
    "../../../etc/passwd",
]


class WebSocketScanner:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger

    def scan(self, url: str) -> Dict[str, Any]:
        self.log.info("Scanning for WebSocket endpoints...")
        results = {"found": False, "endpoints": [], "vulnerable": False, "issues": []}

        ws_endpoints = self._discover_endpoints(url)
        if not ws_endpoints:
            self.log.info("No WebSocket endpoints found")
            return results

        results["found"] = True
        results["endpoints"] = ws_endpoints

        for ep in ws_endpoints:
            issues = self._test_endpoint(ep)
            if issues:
                results["vulnerable"] = True
                results["issues"].extend(issues)
                self.log.warn(f"WebSocket vulnerability at {ep}")

        return results

    def _discover_endpoints(self, url: str) -> List[str]:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        endpoints = set()

        resp, err = self.req.request(url)
        if resp and resp.text:
            ws_patterns = [
                r'new\s+WebSocket\s*\(\s*["\']([^"\']+)["\']',
                r'ws://[^"\']+',
                r'wss://[^"\']+',
                r'var\s+ws\s*=\s*["\']([^"\']+)["\']',
                r'socket\s*:\s*["\']([^"\']+)["\']',
                r'endpoint:\s*["\']([^"\']+)["\']',
            ]
            for pat in ws_patterns:
                for match in re.finditer(pat, resp.text, re.IGNORECASE):
                    ep = match.group(1) if match.lastindex else match.group(0)
                    if not ep.startswith("ws"):
                        ep = f"ws://{parsed.netloc}{'/' if not ep.startswith('/') else ''}{ep}"
                    endpoints.add(ep)

        common_ws_paths = ["/ws", "/socket", "/websocket", "/ws/", "/socket.io/",
                           "/chat", "/notifications", "/realtime", "/stream"]
        for p in common_ws_paths:
            ws_url = f"ws://{parsed.netloc}{p}"
            wss_url = f"wss://{parsed.netloc}{p}"
            endpoints.add(ws_url)
            endpoints.add(wss_url)

        return list(endpoints)[:10]

    def _test_endpoint(self, ws_url: str) -> List[Dict[str, str]]:
        issues = []
        for payload in WS_PAYLOADS:
            result = self._try_ws_payload(ws_url, payload)
            if result:
                issues.append({
                    "endpoint": ws_url,
                    "payload": payload,
                    "issue": result,
                })
        return issues

    def _try_ws_payload(self, ws_url: str, payload: str) -> Optional[str]:
        try:
            parsed = urlparse(ws_url.replace("ws://", "http://").replace("wss://", "https://"))
            host = parsed.hostname or "localhost"
            port = parsed.port or (443 if ws_url.startswith("wss") else 80)
            path = parsed.path or "/"

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))

            key = "dGhlIHNhbXBsZSBub25jZQ=="
            upgrade_req = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                f"Upgrade: websocket\r\n"
                f"Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                f"Sec-WebSocket-Version: 13\r\n"
                f"\r\n"
            )
            sock.send(upgrade_req.encode())
            resp = sock.recv(4096).decode("utf-8", errors="replace")

            if "101" in resp[:50]:
                try:
                    frame = self._build_ws_frame(payload)
                    sock.send(frame)
                except Exception:
                    pass

            sock.close()
            return None
        except Exception as e:
            return str(e)

    def _build_ws_frame(self, payload: str) -> bytes:
        masked_data = payload.encode("utf-8")
        masking_key = b'\x00\x00\x00\x00'
        mask = [masking_key[i % 4] ^ masked_data[i] for i in range(len(masked_data))]
        length = len(masked_data)
        if length < 126:
            frame = bytes([0x81, 0x80 | length]) + masking_key + bytes(mask)
        else:
            frame = bytes([0x81, 0x80 | 126]) + length.to_bytes(2, 'big') + masking_key + bytes(mask)
        return frame
