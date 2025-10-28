from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
from mcp_databases.utils import ensure_valid_conn_params
from typing import Dict, Any

logger = MCPLogger.get_logger("mcp_databases.expose_schema")

def expose_schema(params: Dict[str, Any]):
    """
    Exibe o schema do banco de dados.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}  # Obrigatório - se vazio/inválido, busca do .env automaticamente
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        
        # Garante que conn_params seja válido, buscando do .env se necessário
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        logger.info(f"Expondo schema do banco: {db_type}")
        
        db = get_db(db_type, conn_params)
        result = db.get_schema()
        
        logger.info(f"Schema exposto com sucesso para {db_type}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao expor schema: {e}", exc_info=True)
        raise
