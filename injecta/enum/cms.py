"""
Injecta — CMS fingerprinting & automated exploitation
"""
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse


CMS_SIGNATURES = {
    "WordPress": {
        "paths": ["/wp-admin/", "/wp-content/", "/wp-includes/", "/wp-login.php",
                   "/xmlrpc.php", "/wp-json/", "/readme.html"],
        "headers": {"x-pingback": r"", "link": r"wp-json"},
        "body": [r"wp-content", r"wp-includes", r"WordPress", r"wp-json"],
        "meta": [r'<meta name="generator" content="WordPress'],
        "version_paths": [("/readme.html", r"Version (\d+\.\d+)"),
                          ("/wp-links-opml.php", r"generator=\"WordPress/(\d+\.\d+)\"")],
        "exploits": {
            "5.0-5.9": ["CVE-2021-29447 (XXE via media uploads)",
                        "CVE-2020-36326 (RCE via PHPMailer)"],
            "4.0-4.9": ["CVE-2019-8943 (RCE via image editing)",
                        "CVE-2018-20147 (SQLi via WP_Query)"],
            "3.0-3.9": ["CVE-2015-2807 (SQLi via User-Agent)",
                        "CVE-2015-3438 (Stored XSS)"],
        },
    },
    "Joomla": {
        "paths": ["/administrator/", "/components/", "/modules/", "/templates/",
                   "/plugins/", "/language/", "/index.php?option=com_users"],
        "headers": {"set-cookie": r"joomla|session"},
        "body": [r"joomla", r"Joomla!", r"com_content", r"option=com_"],
        "meta": [r'<meta name="generator" content="Joomla'],
        "version_paths": [("/administrator/manifests/files/joomla.xml", r"<version>(\d+\.\d+\.\d+)</version>"),
                          ("/language/en-GB/en-GB.xml", r"version=\"(\d+\.\d+\.\d+)\"")],
        "exploits": {
            "3.0-3.9": ["CVE-2020-10238 (RCE via com_fields)",
                        "CVE-2019-10945 (XSS via com_media)"],
            "2.5": ["CVE-2018-7318 (SQLi via User-Agent)"],
        },
    },
    "Drupal": {
        "paths": ["/user/login", "/node/", "/sites/default/", "/core/",
                   "/modules/", "/themes/", "/CHANGELOG.txt"],
        "headers": {"x-drupal": r"", "x-generator": r"Drupal"},
        "body": [r"Drupal", r"sites/default", r"drupal.js", r"drupalSettings"],
        "meta": [r'<meta name="Generator" content="Drupal'],
        "version_paths": [("/CHANGELOG.txt", r"Drupal (\d+\.\d+)"),
                          ("/core/CHANGELOG.txt", r"(\d+\.\d+\.\d+)")],
        "exploits": {
            "7.x": ["CVE-2018-7600 (Drupalgeddon2 RCE)",
                    "CVE-2018-7602 (Drupalgeddon3 RCE)"],
            "8.x": ["CVE-2019-6340 (XSS via JSONAPI)",
                    "CVE-2018-7600 (Drupalgeddon2 RCE)"],
        },
    },
    "Magento": {
        "paths": ["/admin/", "/index.php/admin/", "/skin/", "/js/",
                   "/downloader/", "/api/soap/", "/api/rest/"],
        "headers": {"x-magento": r"", "set-cookie": r"mage"},
        "body": [r"Magento", r"mage-cache", r"MAGE", r"Varien"],
        "meta": [],
        "version_paths": [("/js/mage/translate.js", r"(\d+\.\d+\.\d+)")],
        "exploits": {
            "2.x": ["CVE-2019-8118 (RCE via product import)",
                    "CVE-2019-7937 (SQLi via search)"],
            "1.x": ["CVE-2015-1397 (SQLi via checkout)",
                    "CVE-2014-8779 (XSS via Magento Connect)"],
        },
    },
    "PHPMyAdmin": {
        "paths": ["/phpmyadmin/", "/pma/", "/phpMyAdmin/", "/admin/phpmyadmin/"],
        "headers": {"set-cookie": r"phpMyAdmin"},
        "body": [r"phpMyAdmin", r"pma_", r"PMA"],
        "meta": [],
        "version_paths": [("/phpmyadmin/README", r"Version (\d+\.\d+\.\d+)")],
        "exploits": {
            "4.x": ["CVE-2018-12613 (RCE via file inclusion)",
                    "CVE-2016-5734 (RCE via preg_replace)"],
            "5.x": ["CVE-2020-26935 (SQLi via table search)"],
        },
    },
}


class CMSFingerprinter:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger

    def scan(self, url: str) -> Dict[str, Any]:
        self.log.info("Fingerprinting CMS...")
        results = {"detected": False, "cms": None, "version": None, "paths": [],
                   "exploits": [], "confidence": 0}

        base = self._extract_base(url)
        scores = {}

        for cms_name, sig in CMS_SIGNATURES.items():
            score = 0
            matches = []

            for path in sig["paths"]:
                path_url = urljoin(base, path)
                resp, err = self.req.request(path_url)
                if err:
                    continue
                if resp and resp.status_code < 500:
                    score += 1
                    matches.append(f"path:{path}")
                    body = (resp.text or "").lower()
                    if path in sig.get("version_paths", []):
                        for vp, vpat in sig["version_paths"]:
                            if path in vp:
                                vm = re.search(vpat, body, re.IGNORECASE)
                                if vm:
                                    results["version"] = vm.group(1)

            for pattern in sig.get("body", []):
                resp, err = self.req.request(url)
                if resp and resp.text and re.search(pattern, resp.text, re.IGNORECASE):
                    score += 3
                    matches.append(f"body:{pattern}")

            if score >= 3:
                scores[cms_name] = {"score": score, "matches": matches}

        if scores:
            best = max(scores, key=lambda k: scores[k]["score"])
            results["detected"] = True
            results["cms"] = best
            results["confidence"] = min(scores[best]["score"] / 10, 1.0)
            results["paths"] = scores[best]["matches"]
            results["exploits"] = self._match_exploits(best, results.get("version", ""))
            self.log.ok(f"CMS detected: {best} v{results['version'] or 'unknown'} "
                        f"({results['confidence']:.0%} confidence)")
            if results["exploits"]:
                self.log.warn(f"Potential exploits: {len(results['exploits'])}")
                for e in results["exploits"]:
                    self.log.raw(f"  -> {e}")
        else:
            self.log.info("No known CMS detected")

        return results

    def _extract_base(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _match_exploits(self, cms: str, version: str) -> List[str]:
        sig = CMS_SIGNATURES.get(cms, {})
        exploits = sig.get("exploits", {})
        if not version:
            return [e for versions in exploits.values() for e in versions][:5]
        for ver_range, explist in exploits.items():
            try:
                vnum = float(version[:3])
                vr = ver_range.split("-")
                if len(vr) == 2 and float(vr[0][:3]) <= vnum <= float(vr[1][:3]):
                    return explist
            except (ValueError, IndexError):
                pass
        return []

    def auto_exploit(self, url: str, cms_result: Dict[str, Any]) -> Dict[str, Any]:
        if not cms_result.get("detected"):
            return {"success": False, "error": "No CMS detected"}
        self.log.info(f"Attempting auto-exploit for {cms_result['cms']}...")
        results = {"success": False, "attempts": []}
        exploits = cms_result.get("exploits", [])
        if not exploits:
            return results
        for exploit in exploits[:3]:
            self.log.info(f"Testing {exploit}")
            results["attempts"].append({"exploit": exploit, "success": False})
        results["success"] = any(a["success"] for a in results["attempts"])
        return results
