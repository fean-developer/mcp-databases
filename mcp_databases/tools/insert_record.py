
from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
logger = MCPLogger.get_logger("mcp_databases.insert_record")

def insert_record(params: dict):
    """
    Insere um registro em uma tabela.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table": "tabela",
        "record": {...}
    }
    """
    try:
        logger.info(f"Inserindo registro na tabela: {params.get('table')} do banco: {params.get('db_type')}")
        db = get_db(params["db_type"], params["conn_params"])
        result = db.insert_record(params["table"], params["data"])
        logger.info(f"Registro inserido com sucesso. Resultado: {str(result)[:500]}")
        return result
    except Exception as e:
        logger.error(f"Erro ao inserir registro: {e}", exc_info=True)
        raise

