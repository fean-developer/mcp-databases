from db.factory import get_db
from db.factory import get_db
from logger import MCPLogger
logger = MCPLogger.get_logger("mcp_databases.list_tables")

def list_tables(params: dict):
    """
    Lista todas as tabelas disponíveis.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    logger.info(f"Listando tabelas do banco: {params.get('db_type')}")
    db = get_db(params["db_type"], params["conn_params"])
    return db.list_tables()