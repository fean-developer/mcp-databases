from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
logger = MCPLogger.get_logger("mcp_databases.expose_schema")

def expose_schema(params: dict):
    """
    Exibe o schema do banco de dados.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    try:
        logger.info(f"Expondo schema do banco: {params.get('db_type')}")
        db = get_db(params["db_type"], params["conn_params"])
        result = db.get_schema()
        logger.info(f"Schema exposto com sucesso. Resultado: {str(result)[:500]}")
        return result
    except Exception as e:
        logger.error(f"Erro ao expor schema: {e}", exc_info=True)
        raise
