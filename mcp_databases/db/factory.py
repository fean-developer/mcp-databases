from .mssql import MSSQLDB
from .mysql import MySQLDB
from .postgres import PostgresDB
import os

def get_db(db_type: str, conn_params: dict):

    if db_type not in ["mssql", "mysql", "postgres"]:
        raise ValueError(f"Unsupported db_type: {db_type}")
    
    if db_type is None:
        db_type = os.getenv("DB_TYPE")

        # Adiciona suporte para 'host' como alias de 'server'
        if conn_params is not None:
            if "host" in conn_params and "server" not in conn_params:
                conn_params["server"] = conn_params["host"]
            if "dbname" in conn_params and "database" not in conn_params:
                conn_params["database"] = conn_params["dbname"]
        else:
            conn_params = {
                "server": os.getenv(f"{db_type.upper()}_SERVER"),
                "database": os.getenv(f"{db_type.upper()}_DATABASE"),
                "user": os.getenv(f"{db_type.upper()}_USER"),
                "password": os.getenv(f"{db_type.upper()}_PASSWORD"),
            }

    if db_type == "mssql":
        return MSSQLDB(conn_params)
    elif db_type == "mysql":
        return MySQLDB(conn_params)
    elif db_type == "postgres":
        return PostgresDB(conn_params)
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")
