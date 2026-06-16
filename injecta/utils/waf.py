"""
Injecta — WAF fingerprinting & dynamic tamper selection
"""
import re
from typing import Dict, List, Optional, Tuple
from injecta.utils.tamper import AUTO_CHAINS


WAF_SIGNATURES = {
    "Cloudflare": {
        "headers": ["cf-ray", "cf-cache-status", "__cfduid"],
        "cookies": ["__cfduid"],
        "body": [r"cloudflare", r"cf-ray", r"attention required", r"challenge platform"],
        "status": [403, 503],
        "tamper": ["randomcase", "commentkeywords"],
    },
    "ModSecurity": {
        "headers": ["x-mod-security", "x-powered-by: ModSecurity"],
        "cookie": [],
        "body": [r"mod_security", r"not acceptable", r"blocked by mod_security", r"error code 406"],
        "status": [406, 403],
        "tamper": ["space2comment", "hexencode"],
    },
    "AWS WAF": {
        "headers": ["x-amzn-requestid", "x-amzn-trace-id", "x-amz-cf-id"],
        "cookies": ["aws-waf-token"],
        "body": [r"request blocked", r"404 Not Found.*AWS", r"waf"],
        "status": [403, 404],
        "tamper": ["space2comment", "lowercase"],
    },
    "Akamai": {
        "headers": ["x-akamai-transformed", "x-akamai-request-id"],
        "cookies": ["_abck", "bm_sz"],
        "body": [r"akamai", r"reference number", r"page not found"],
        "status": [403],
        "tamper": ["randomcase", "space2comment"],
    },
    "F5 BIG-IP ASM": {
        "headers": ["x-asm-version", "x-asm-policy", "x-wa-identity"],
        "cookies": ["ASM", "LastMRH_Session"],
        "body": [r"the requested url was rejected", r"support id", r"asm"],
        "status": [403, 500],
        "tamper": ["commentkeywords", "hexencode"],
    },
    "Sucuri": {
        "headers": ["x-sucuri-id", "x-sucuri-cache"],
        "cookies": ["sucuri_cloudproxy"],
        "body": [r"sucuri", r"cloudproxy", r"access denied"],
        "status": [403],
        "tamper": ["space2comment", "randomcase"],
    },
    "Barracuda": {
        "headers": ["x-barracuda", "barracuda"],
        "cookies": [],
        "body": [r"barracuda", r"blocked by barracuda"],
        "status": [403, 500],
        "tamper": ["space2comment", "eq2like"],
    },
    "WordPress WAF": {
        "headers": [],
        "cookies": [],
        "body": [r"wordfence", r"blocked by wordfence", r"firewall"],
        "status": [403, 503],
        "tamper": ["lowercase", "space2comment"],
    },
    "Generic WAF": {
        "headers": ["x-waf", "x-firewall", "x-blocked"],
        "cookies": [],
        "body": [r"waf", r"firewall", r"blocked", r"malicious", r"attack detected",
                 r"illegal character", r"suspicious", r"rejected"],
        "status": [403, 406, 429, 500],
        "tamper": ["space2comment", "randomcase", "commentkeywords"],
    },
}


class WAFDetector:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger
        self.detected_wafs: List[str] = []

    def scan(self, url: str) -> Dict[str, any]:
        self.log.info("Probing for WAF/IDS...")
        resp, err = self.req.request(url)
        if err or resp is None:
            self.log.debug2(f"WAF scan baseline failed: {err}")
            return {"detected": False, "wafs": [], "tamper": []}

        status = resp.status_code
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.text.lower()

        for waf_name, sig in WAF_SIGNATURES.items():
            score = 0
            matches = []

            for h in sig.get("headers", []):
                if h.lower() in headers:
                    score += 2
                    matches.append(f"header:{h}")

            for c in sig.get("cookies", []):
                if c in resp.cookies or c in headers.get("set-cookie", ""):
                    score += 2
                    matches.append(f"cookie:{c}")

            for pattern in sig.get("body", []):
                if re.search(pattern, body, re.IGNORECASE):
                    score += 3
                    matches.append(f"body:{pattern}")

            if status in sig.get("status", []):
                score += 1
                matches.append(f"status:{status}")

            if score >= 3:
                self.detected_wafs.append(waf_name)
                self.log.warn(f"WAF detected: {waf_name} (score={score})")
                return {"detected": True, "wafs": [waf_name],
                        "tamper": sig.get("tamper", []), "matches": matches}

        if self.config.verbose >= 2 and self.detected_wafs:
            self.log.debug(f"WAFs detected: {', '.join(self.detected_wafs)}")
        return {"detected": len(self.detected_wafs) > 0,
                "wafs": self.detected_wafs,
                "tamper": self._merge_tampers()}

    def _merge_tampers(self) -> List[str]:
        merged = []
        seen = set()
        for waf in self.detected_wafs:
            sig = WAF_SIGNATURES.get(waf, {})
            for t in sig.get("tamper", []):
                if t not in seen:
                    merged.append(t)
                    seen.add(t)
        return merged

    def get_recommended_tamper(self) -> List[str]:
        if self.detected_wafs:
            return self._merge_tampers()
        return ["space2comment"]

    def has_waf(self) -> bool:
        return len(self.detected_wafs) > 0
