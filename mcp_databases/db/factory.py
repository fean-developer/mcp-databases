
from .mssql import MSSQLDB
from .mysql import MySQLDB
from .postgres import PostgresDB
from mcp_databases.logger import MCPLogger


def get_db(db_type: str, conn_params: dict):
    logger = MCPLogger.get_logger("mcp_databases.db.factory")
    logger.info(f"get_db chamado com db_type={db_type}, conn_params=***")

    SUPPORTED_TYPES = {"mssql": MSSQLDB, "mysql": MySQLDB, "postgres": PostgresDB}
    if db_type not in SUPPORTED_TYPES:
        logger.error(f"Unsupported db_type: {db_type}")
        raise ValueError(f"Unsupported db_type: {db_type}")

    # Normaliza aliases de parâmetros de conexão
    def normalize_conn_params(params):
        if params is None:
            return params
        # server
        if "server" not in params and "host" in params:
            params["server"] = params["host"]
        # database
        if "database" not in params:
            if "db" in params:
                params["database"] = params["db"]
            elif "dbname" in params:
                params["database"] = params["dbname"]
        return params

    if conn_params is not None:
        conn_params = normalize_conn_params(conn_params)
    else:
        import os
        conn_params = {
            "server": os.getenv(f"{db_type.upper()}_SERVER") or os.getenv(f"{db_type.upper()}_HOST"),
            "database": os.getenv(f"{db_type.upper()}_DATABASE") or os.getenv(f"{db_type.upper()}_DB") or os.getenv(f"{db_type.upper()}_DBNAME"),
            "user": os.getenv(f"{db_type.upper()}_USER"),
            "password": os.getenv(f"{db_type.upper()}_PASSWORD"),
        }
        conn_params = normalize_conn_params(conn_params)

    db_class = SUPPORTED_TYPES[db_type]
    return db_class(conn_params)
