from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
logger = MCPLogger.get_logger("mcp_databases.list_tables")

def list_tables(params: dict):
    """
    Lista todas as tabelas do banco.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    try:
       
        logger.info(f"Listando tabelas do banco: {params.get('db_type')}")
        db = get_db(params["db_type"], params["conn_params"])
        result = db.list_tables()
        logger.info(f"Tabelas listadas com sucesso. Resultado: {str(result)[:500]}")
        return result
    except Exception as e:
        logger.error(f"Erro ao listar tabelas: {e}", exc_info=True)
        raise