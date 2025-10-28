import pyodbc
from .base import BaseDB
from mcp_databases.security import validate_sql_security, SQLSecurityError

class MSSQLDB(BaseDB):
    def _connect(self):
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.conn_params['server']};"
                f"DATABASE={self.conn_params['database']};"
                f"UID={self.conn_params['user']};"
                f"PWD={self.conn_params['password']};"
                f"Encrypt=no;"
                f"TrustServerCertificate=yes;"
            )
            return pyodbc.connect(conn_str)

    def execute_query(self, query: str):
        # VALIDAÇÃO DE SEGURANÇA OBRIGATÓRIA - CAMADA DE PROTEÇÃO NO BANCO
        try:
            validate_sql_security(query, allow_modifications=False)
        except SQLSecurityError as e:
            raise SQLSecurityError(f"MSSQL: Execução bloqueada por segurança - {str(e)}")
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            try:
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
            except Exception:
                return []

    def insert_record(self, table: str, data: dict):
        cols = ",".join(data.keys())
        vals = ",".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()

    def list_tables(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES")
            return [row[0] for row in cursor.fetchall()]

    def get_schema(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                ORDER BY TABLE_NAME
            """)
            rows = cursor.fetchall()
            return "\n".join([f"{r.TABLE_NAME}.{r.COLUMN_NAME} ({r.DATA_TYPE})" for r in rows])
