"""
Injecta — HTTP Requester with proxy, Tor, cookie, session support
"""
import random
import time
import urllib.parse
from typing import Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from injecta.utils.random_ua import get_random_ua


class VoidRequester:
    def __init__(self, config):
        self.config = config
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        s = requests.Session()

        retry_strategy = Retry(
            total=self.config.retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=50)
        s.mount("http://", adapter)
        s.mount("https://", adapter)

        if self.config.proxy:
            s.proxies.update({
                "http": self.config.proxy,
                "https": self.config.proxy,
            })

        if self.config.cookies:
            for c in self.config.cookies.split(";"):
                if "=" in c:
                    key, val = c.strip().split("=", 1)
                    s.cookies.set(key.strip(), val.strip())

        s.headers.update(self.config.headers)

        return s

    def _pick_ua(self) -> str:
        if self.config.user_agent:
            return self.config.user_agent
        if self.config.random_agent:
            return get_random_ua()
        return "Injecta/1.0"

    def request(self, url: str, data: Optional[str] = None,
                extra_headers: Optional[Dict[str, str]] = None,
                raw_response: bool = False) -> Tuple[Optional[requests.Response], Optional[str]]:
        headers = {"User-Agent": self._pick_ua()}
        if extra_headers:
            headers.update(extra_headers)

        if self.config.delay > 0:
            jitter = random.uniform(0, self.config.delay * 0.2)
            time.sleep(self.config.delay + jitter)

        method = self.config.method.upper()
        try:
            if method == "POST":
                payload = data or self.config.data
                resp = self.session.post(
                    url, data=payload, headers=headers,
                    timeout=self.config.timeout, allow_redirects=True
                )
            else:
                resp = self.session.get(
                    url, headers=headers, params=data,
                    timeout=self.config.timeout, allow_redirects=True
                )
            return (resp, None)
        except requests.exceptions.Timeout:
            return (None, "timeout")
        except requests.exceptions.ConnectionError:
            return (None, "connection_error")
        except Exception as e:
            return (None, str(e))

    def test_raw(self, url: str, payload: str, param: str = "",
                 method: Optional[str] = None) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        injected_url, injected_data = self._inject(url, payload, param)
        resp, err = self.request(injected_url, data=injected_data)
        if err:
            return (None, err, None)
        return (resp.status_code, resp.text, resp.elapsed.total_seconds())

    def _inject(self, url: str, payload: str, param: str) -> Tuple[str, Optional[str]]:
        if not param:
            if "?" in url and self.config.method == "GET":
                base, qs = url.split("?", 1)
                params = urllib.parse.parse_qs(qs)
                if params:
                    first_key = list(params.keys())[0]
                    params[first_key] = [payload]
                    new_qs = urllib.parse.urlencode(params, doseq=True)
                    return (f"{base}?{new_qs}", None)
            if self.config.data:
                return (url, payload)
            return (url + ("?" if "?" not in url else "&") + f"id={payload}", None)

        if self.config.method == "GET":
            base, qs = url.split("?", 1) if "?" in url else (url, "")
            params = urllib.parse.parse_qs(qs) if qs else {}
            if param in params:
                params[param] = [payload]
            else:
                params[param] = [payload]
            new_qs = urllib.parse.urlencode(params, doseq=True)
            return (f"{base}?{new_qs}", None)
        else:
            import re
            if self.config.data:
                data_str = self.config.data
                if param in data_str or param == "":
                    data_str = re.sub(rf'({re.escape(param)}=)[^&]*', rf'\g<1>{urllib.parse.quote(payload)}', data_str)
                else:
                    data_str += f"&{param}={urllib.parse.quote(payload)}"
                return (url, data_str)
            return (url, f"{param}={urllib.parse.quote(payload)}")

    def close(self):
        self.session.close()
