
from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
from mcp_databases.utils import ensure_valid_conn_params
from typing import Dict, Any

logger = MCPLogger.get_logger("mcp_databases.insert_record")

def insert_record(params: Dict[str, Any]):
    """
    Insere um registro em uma tabela.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},  # Obrigatório - se vazio/inválido, busca do .env automaticamente
        "table": "tabela",
        "data": {...}
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table = params["table"]
        data = params["data"]
        
        # Garante que conn_params seja válido, buscando do .env se necessário
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        logger.info(f"Inserindo registro na tabela: {table} do banco: {db_type}")
        
        db = get_db(db_type, conn_params)
        result = db.insert_record(table, data)
        
        logger.info(f"Registro inserido com sucesso na tabela {table}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao inserir registro: {e}", exc_info=True)
        raise

