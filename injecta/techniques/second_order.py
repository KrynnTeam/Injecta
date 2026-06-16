"""
Injecta — Second-order SQL injection detection
"""
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse


SECOND_ORDER_PATTERNS = {
    "register": {
        "path": ["/register", "/signup", "/create", "/sign-up", "/user/create"],
        "fields": ["username", "email", "name", "first_name", "last_name"],
        "trigger": ["/profile", "/user", "/account", "/dashboard"],
    },
    "comment": {
        "path": ["/comment", "/post/comment", "/submit-comment", "/add-comment"],
        "fields": ["comment", "message", "text", "body", "content"],
        "trigger": ["/post/", "/article/", "/blog/", "/forum/"],
    },
    "search": {
        "path": ["/search", "/find", "/query", "/lookup"],
        "fields": ["q", "search", "query", "keyword", "term"],
        "trigger": ["/search", "/results", "/find"],
    },
    "contact": {
        "path": ["/contact", "/form", "/submit", "/feedback"],
        "fields": ["name", "email", "message", "subject", "comments"],
        "trigger": ["/contact", "/form/", "/admin/contact"],
    },
    "review": {
        "path": ["/review", "/rate", "/feedback", "/product/review"],
        "fields": ["review", "rating", "title", "comment", "text"],
        "trigger": ["/product/", "/item/", "/reviews"],
    },
}


class SecondOrderInjector:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger
        self._results: Dict[str, Any] = {}

    def scan(self, url: str) -> Dict[str, Any]:
        self.log.info("Scanning for second-order injection points...")
        results = {"detected": False, "vectors": [], "vulnerable": False}

        base = self._extract_base(url)
        vectors = self._find_vectors(base)

        for v in vectors:
            self.log.debug2(f"Testing vector: {v['store_path']} -> {v['trigger_path']}")
            result = self._test_vector(base, v)
            if result.get("vulnerable"):
                results["vulnerable"] = True
                results["vectors"].append(result)
                self.log.warn(f"Second-order injection: {v['type']} via {v['field']}")

        results["detected"] = len(vectors) > 0
        if not results["vulnerable"]:
            self.log.info("No second-order injection confirmed")
        return results

    def _extract_base(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _find_vectors(self, base: str) -> List[Dict[str, str]]:
        vectors = []
        for vtype, cfg in SECOND_ORDER_PATTERNS.items():
            for path in cfg["path"]:
                store_url = urljoin(base, path)
                resp, err = self.req.request(store_url)
                if err or resp is None:
                    continue
                if resp.status_code < 500:
                    for field in cfg["fields"]:
                        for tpath in cfg["trigger"]:
                            vectors.append({
                                "type": vtype,
                                "field": field,
                                "store_path": store_url,
                                "trigger_path": urljoin(base, tpath),
                            })
                    break
        return vectors[:10]

    def _test_vector(self, base: str, vector: Dict[str, str]) -> Dict[str, Any]:
        payload = f"INJECTA' OR '1'='1"
        result = {
            "type": vector["type"],
            "field": vector["field"],
            "store_path": vector["store_path"],
            "trigger_path": vector["trigger_path"],
            "vulnerable": False,
            "evidence": None,
        }

        store_data = {vector["field"]: payload}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        store_body = urllib.parse.urlencode(store_data)

        resp, err = self.req.request(vector["store_path"], data=store_body,
                                     extra_headers=headers)
        if err or resp is None:
            return result

        triggers = self._find_triggers(vector["trigger_path"], payload)
        for trigger in triggers:
            trigger_url = urljoin(base, trigger)
            t_resp, t_err = self.req.request(trigger_url)
            if t_err or t_resp is None:
                continue
            if payload.rstrip("'") in t_resp.text or "1'='1" in t_resp.text:
                result["vulnerable"] = True
                result["evidence"] = f"Payload reflected in {trigger_url}"

        return result

    def _find_triggers(self, trigger_base: str, payload: str) -> List[str]:
        resp, err = self.req.request(trigger_base)
        if err or resp is None:
            return [trigger_base]
        links = re.findall(r'href=[\'"]?([^\'" >]+)', resp.text)
        return [l for l in links if len(l) > 3 and not l.startswith("#")][:5]

    def scan_target(self, url: str) -> Dict[str, Any]:
        return self.scan(url)
