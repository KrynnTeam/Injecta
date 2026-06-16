"""
Injecta — Output & logging system
"""
import sys
from datetime import datetime
from typing import Optional


class VoidLogger:
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "reset": "\033[0m",
    }

    PREFIXES = {
        "info": "[*]",
        "ok": "[+]",
        "warn": "[!]",
        "error": "[-]",
        "debug": "[d]",
        "result": "[#]",
    }

    def __init__(self, verbose: int = 0, no_color: bool = False, output_file: Optional[str] = None):
        self.verbose = verbose
        self.no_color = no_color
        self.output_file = output_file
        self._buffer = []
        self._start_time = datetime.now()

    def _c(self, code: str) -> str:
        if self.no_color:
            return ""
        return self.COLORS.get(code, "")

    def _r(self) -> str:
        if self.no_color:
            return ""
        return self.COLORS["reset"]

    def _fmt(self, level: str, msg: str, color: str = "white") -> str:
        prefix = self.PREFIXES.get(level, "[*]")
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{self._c('dim')}[{ts}]{self._r()} {self._c(color)}{prefix}{self._r()} {msg}"

    def info(self, msg: str):
        line = self._fmt("info", msg, "cyan")
        self._write(line)

    def ok(self, msg: str):
        line = self._fmt("ok", msg, "green")
        self._write(line)

    def warn(self, msg: str):
        line = self._fmt("warn", msg, "yellow")
        self._write(line)

    def error(self, msg: str):
        line = self._fmt("error", msg, "red")
        self._write(line)

    def result(self, msg: str):
        line = self._fmt("result", msg, "magenta")
        self._write(line)

    def debug(self, msg: str):
        if self.verbose >= 1:
            line = self._fmt("debug", msg, "gray")
            self._write(line)

    def debug2(self, msg: str):
        if self.verbose >= 2:
            line = self._fmt("debug", msg, "dim")
            self._write(line)

    def raw(self, msg: str):
        self._write(msg)

    def get_logs_since(self, index: int = 0) -> dict:
        buf = self._buffer
        return {"logs": buf[index:], "total": len(buf)}

    def _write(self, line: str):
        print(line, file=sys.stdout)
        self._buffer.append(line)
        if self.output_file:
            from pathlib import Path
            Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def elapsed(self) -> str:
        delta = datetime.now() - self._start_time
        return str(delta).split(".")[0]

    def banner(self):
        target_str = self._c('reset')
        b = f"""{self._c('red')}
    ===============================================
    |            I N J E C T A   v 1 . 0          |
    |   Full-stack SQL injection platform         |
    |            Forged by Krynn Team              |
    ===============================================
    {self._c('dim')}Target: {self._c('cyan')}%s{self._r()}
        """ % (target_str)
        try:
            print(b, file=sys.stdout)
        except UnicodeEncodeError:
            safe = b.encode('ascii', errors='replace').decode('ascii')
            print(safe, file=sys.stdout)
