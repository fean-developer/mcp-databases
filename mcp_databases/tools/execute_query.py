

from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
logger = MCPLogger.get_logger("mcp_databases.execute_query")


def execute_query(params: dict):
    """
    Executa uma query arbitrária no banco.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "query": "SELECT * FROM ..."
    }
    """
    try:
        logger.info(f"Executando query: {params.get('query')} no banco: {params.get('db_type')}")
        db = get_db(params["db_type"], params["conn_params"])
        result = db.execute_query(params["query"])
        logger.info(f"Query executada com sucesso. Resultado: {str(result)[:500]}")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}", exc_info=True)
        raise
