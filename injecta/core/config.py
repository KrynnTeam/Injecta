"""
Injecta — Configuration & CLI argument parser
"""
import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    _HAVE_COLOR = True
except ImportError:
    _HAVE_COLOR = False
    class Fore:
        CYAN = BLUE = GREEN = YELLOW = RED = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


@dataclass
class VoidConfig:
    target: str = ""
    method: str = "GET"
    data: str = ""
    cookies: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    proxy: str = ""
    tor: bool = False
    threads: int = 1
    delay: float = 0.0
    timeout: int = 10
    retries: int = 3
    user_agent: str = ""
    random_agent: bool = True

    dbms: str = ""
    technique: str = "BEUST"
    level: int = 1
    risk: int = 1

    dbs: bool = False
    tables: bool = False
    columns: bool = False
    dump: bool = False
    db: str = ""
    table: str = ""
    column: str = ""
    search: bool = False
    query: str = ""

    file_read: str = ""
    file_write: str = ""
    file_write_content: str = ""
    file_write_local: str = ""
    os_cmd: str = ""
    nosql: bool = False
    graphql: bool = False

    privesc: bool = False
    oob_host: str = ""
    report: bool = False

    cms: bool = False
    second_order: bool = False
    ws: bool = False
    plugins: bool = False

    verbose: int = 0
    output_dir: str = ""
    batch: bool = False
    flush: bool = False
    no_color: bool = False

    interactive: bool = False
    web_port: int = 8080
    web_mode: bool = False
    api_mode: bool = False


BANNER = r"""
 ____  _____   ______           ____      ______         _____   _________________       ____   
|    ||\    \ |\     \         |    | ___|\     \    ___|\    \ /                 \ ____|\   \  
|    | \\    \| \     \        |    ||     \     \  /    /\    \\______     ______//    /\    \ 
|    |  \|    \  \     |       |    ||     ,_____/||    |  |    |  \( /    /  )/  |    |  |    |
|    |   |     \  |    | ____  |    ||     \--'\_|/|    |  |____|   ' |   |   '   |    |__|    |
|    |   |      \ |    ||    | |    ||     /___/|  |    |   ____      |   |       |    .--.    |
|    |   |    |\ \|    ||    | |    ||     \____|\ |    |  |    |    /   //       |    |  |    |
|____|   |____||\_____/||\____\|____||____ '     /||\ ___\/    /|   /___//        |____|  |____|
|    |   |    |/ \|   ||| |    |    ||    /_____/ || |   /____/ |  |`   |         |    |  |    |
|____|   |____|   |___|/ \|____|____||____|     | / \|___|    | /  |____|         |____|  |____|
  \(       \(       )/      \(   )/    \( |_____|/    \( |____|/     \(             \(      )/  
   '        '       '        '   '      '    )/        '   )/         '              '      '   
                                              '             ' 
"""


class _HelpAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help="show this help message and exit")

    def __call__(self, parser, namespace, values, option_string=None):
        c = Fore.CYAN if _HAVE_COLOR else ""
        g = Fore.GREEN if _HAVE_COLOR else ""
        r = Fore.RED if _HAVE_COLOR else ""
        b = Style.BRIGHT if _HAVE_COLOR else ""
        rs = Style.RESET_ALL if _HAVE_COLOR else ""
        print(f"{c}{BANNER}{rs}")
        print(f"{g}{b}           Made by Kael / Krynn Team{rs}")
        print()
        parser.print_help()
        print()
        print(f"{r}Use with precision. One mistake and you're the one getting owned.{rs}")
        parser.exit()


def parse_args(argv: Optional[List[str]] = None) -> VoidConfig:
    parser = argparse.ArgumentParser(
        prog="injecta",
        description=None,
        epilog=None,
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-h", "--help", action=_HelpAction)

    target_group = parser.add_argument_group("Target")
    target_group.add_argument("-u", "--url", dest="target", help="Target URL")
    target_group.add_argument("-m", "--method", default="GET", choices=["GET", "POST"], help="HTTP method")
    target_group.add_argument("-d", "--data", help="POST data body")
    target_group.add_argument("--cookie", dest="cookies", help="HTTP cookies")
    target_group.add_argument("-H", "--header", dest="headers_raw", action="append",
                              help="Custom headers (Can be repeated: -H 'X-Forwarded-For: 127.0.0.1')")

    request_group = parser.add_argument_group("Request")
    request_group.add_argument("--proxy", help="Proxy (http://127.0.0.1:8080)")
    request_group.add_argument("--tor", action="store_true", help="Use Tor SOCKS proxy")
    request_group.add_argument("--threads", type=int, default=1, help="Max threads")
    request_group.add_argument("--delay", type=float, default=0.0, help="Delay between requests (s)")
    request_group.add_argument("--timeout", type=int, default=10, help="Request timeout (s)")
    request_group.add_argument("--retries", type=int, default=3, help="Max retries on failure")
    request_group.add_argument("--user-agent", dest="user_agent", help="Custom User-Agent")
    request_group.add_argument("--random-agent", action="store_true", default=True,
                               help="Use random User-Agent per request")

    injection_group = parser.add_argument_group("Injection")
    injection_group.add_argument("--dbms", choices=["mysql", "postgresql", "mssql", "oracle", "sqlite", "auto"],
                                 default="auto", help="Force DBMS type")
    injection_group.add_argument("--technique", default="BEUST",
                                 help="Techniques: B(boolean), E(error), U(union), T(time), S(stacked)")
    injection_group.add_argument("--level", type=int, default=1, choices=[1, 2, 3, 4, 5],
                                 help="Test intensity level")
    injection_group.add_argument("--risk", type=int, default=1, choices=[1, 2, 3],
                                 help="Risk of payloads (1=low, 3=high)")

    enum_group = parser.add_argument_group("Enumeration")
    enum_group.add_argument("--dbs", action="store_true", help="Enumerate databases")
    enum_group.add_argument("--tables", action="store_true", help="Enumerate tables")
    enum_group.add_argument("--columns", action="store_true", help="Enumerate columns")
    enum_group.add_argument("--dump", action="store_true", help="Dump data")
    enum_group.add_argument("-D", "--db", dest="db", help="Database name")
    enum_group.add_argument("-T", "--table", dest="table", help="Table name")
    enum_group.add_argument("-C", "--column", dest="column", help="Column name(s), comma separated")
    enum_group.add_argument("--search", action="store_true", help="Search column(s) / table(s)")
    enum_group.add_argument("--query", help="Run raw SQL query")

    file_group = parser.add_argument_group("File & OS")
    file_group.add_argument("--file-read", dest="file_read", help="Read file from DB server")
    file_group.add_argument("--file-write", dest="file_write", help="Write file TO DB server (path)")
    file_group.add_argument("--file-write-content", dest="file_write_content", help="Content for file-write (default: path)")
    file_group.add_argument("--file-write-local", dest="file_write_local", help="Local file to read content from for --file-write")
    file_group.add_argument("--os-cmd", dest="os_cmd", help="Execute OS command on DB server")

    extra_group = parser.add_argument_group("NoSQL / GraphQL")
    extra_group.add_argument("--nosql", action="store_true", help="Test NoSQL injection")
    extra_group.add_argument("--graphql", action="store_true", help="Test GraphQL introspection & injection")

    phase3_group = parser.add_argument_group("Phase 3 — OOB, Privesc, Reports")
    phase3_group.add_argument("--privesc", action="store_true", help="Run privilege escalation detection")
    phase3_group.add_argument("--oob-host", dest="oob_host", help="OOB exfiltration target (IP/domain)")
    phase3_group.add_argument("--report", action="store_true", help="Generate HTML+JSON report after scan")

    extra2_group = parser.add_argument_group("Advanced Features — CMS, Second-Order, WebSocket, Plugins")
    extra2_group.add_argument("--cms", action="store_true", help="Fingerprint CMS (WordPress, Joomla, etc.)")
    extra2_group.add_argument("--second-order", action="store_true", dest="second_order", help="Test second-order SQL injection")
    extra2_group.add_argument("--ws", action="store_true", dest="ws", help="Scan WebSocket endpoints")
    extra2_group.add_argument("--plugins", action="store_true", dest="plugins", help="Load custom payload plugins from plugins/")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level")
    output_group.add_argument("-o", "--output-dir", dest="output_dir", help="Output directory")
    output_group.add_argument("--batch", action="store_true", help="Never ask for input, use defaults")
    output_group.add_argument("--flush", action="store_true", help="Flush cached results")
    output_group.add_argument("--no-color", action="store_true", help="Disable colored output")

    web_group = parser.add_argument_group("Web Dashboard & API")
    web_group.add_argument("--web", action="store_true", dest="web_mode", help="Launch web dashboard")
    web_group.add_argument("--api", action="store_true", dest="api_mode", help="Run in REST API mode")
    web_group.add_argument("--interactive", action="store_true", help="Launch interactive console")
    web_group.add_argument("--web-port", type=int, default=8080, help="Web dashboard / API port")

    args = parser.parse_args(argv)

    cfg = VoidConfig()
    for key, val in vars(args).items():
        if hasattr(cfg, key):
            setattr(cfg, key, val)

    if args.headers_raw:
        for h in args.headers_raw:
            if ":" in h:
                k, v = h.split(":", 1)
                cfg.headers[k.strip()] = v.strip()

    if cfg.tor:
        cfg.proxy = "socks5://127.0.0.1:9050"

    return cfg
