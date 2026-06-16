"""
Injecta — Shared utility helpers
"""
import hashlib
import re
import textwrap
from typing import Dict, List, Optional, Any


def content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()


def extract_dbms_from_error(text: str) -> Optional[str]:
    patterns = {
        "mysql": r"(SQL syntax.*MySQL|mysql_fetch|Warning.*mysql_.*|Incorrect.*key file|MariaDB)",
        "postgresql": r"(PostgreSQL.*ERROR|psycopg2|pg_|PG::)",
        "mssql": r"(MSSQL|SQL Server|Driver.*SQL Server|Microsoft OLE DB|Unclosed quotation|Line \d+)",
        "oracle": r"(ORA-\d{5}|Oracle.*Driver|oracle\.jdbc|PL/SQL)",
        "sqlite": r"(SQLite/JDBCDriver|sqlite3\.OperationalError|unrecognized token|SQLite\.Exception)",
    }
    for dbms, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return dbms
    return None


def clean_value(value: str) -> str:
    value = re.sub(r'<[^>]+>', '', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def format_table(data: List[Dict[str, Any]], headers: List[str]) -> str:
    if not data:
        return "[empty]"

    col_widths = {h: len(h) for h in headers}
    for row in data:
        for h in headers:
            val = str(row.get(h, ""))
            col_widths[h] = max(col_widths[h], len(val))

    sep = "+" + "+".join("-" * (w + 2) for w in col_widths.values()) + "+"
    header_row = "| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |"
    lines = [sep, header_row, sep]

    for row in data:
        vals = []
        for h in headers:
            vals.append(str(row.get(h, "")).ljust(col_widths[h]))
        lines.append("| " + " | ".join(vals) + " |")
    lines.append(sep)

    return "\n".join(lines)
