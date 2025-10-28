import psycopg2
import psycopg2.extras
from .base import BaseDB
from mcp_databases.security import validate_sql_security, SQLSecurityError

class PostgresDB(BaseDB):
    def _connect(self):
        return psycopg2.connect(
            host=self.conn_params['server'],
            dbname=self.conn_params['database'],
            user=self.conn_params['user'],
            password=self.conn_params['password']
        )

    def execute_query(self, query: str):
        # VALIDAÇÃO DE SEGURANÇA OBRIGATÓRIA - CAMADA DE PROTEÇÃO NO BANCO
        try:
            validate_sql_security(query, allow_modifications=False)
        except SQLSecurityError as e:
            raise SQLSecurityError(f"PostgreSQL: Execução bloqueada por segurança - {str(e)}")
        
        conn = self._connect()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query)
        # Commit se não for SELECT (mas já foi validado que só SELECT passa)
        if not query.strip().lower().startswith('select'):
            conn.commit()
        try:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        except Exception:
            result = []
        conn.close()
        return result

    def insert_record(self, table: str, data: dict):
        cols = ",".join(data.keys())
        vals = ",".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        conn.close()

    def list_tables(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_schema(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
        """)
        rows = cursor.fetchall()
        conn.close()
        return "\n".join([f"{r[0]}.{r[1]} ({r[2]})" for r in rows])
