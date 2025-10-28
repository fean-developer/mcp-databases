

from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
from mcp_databases.utils import ensure_valid_conn_params
from mcp_databases.security import validate_sql_security, SQLSecurityError
from typing import Dict, Any

logger = MCPLogger.get_logger("mcp_databases.execute_query")


def execute_query(params: Dict[str, Any]):
    """
    Executa uma query arbitrária no banco.
    IMPORTANTE: Apenas comandos SELECT são permitidos por razões de segurança.
    Comandos DELETE, DROP, EXEC e outros comandos perigosos são bloqueados.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},  # Obrigatório - se vazio/inválido, busca do .env automaticamente
        "query": "SELECT * FROM ..."  # Apenas comandos SELECT são permitidos
    }
    """
    try:
        db_type = params["db_type"]
        query = params["query"]
        conn_params = params["conn_params"]
        
        # VALIDAÇÃO DE SEGURANÇA - PRIMEIRA LINHA DE DEFESA
        # Esta validação NÃO PODE ser contornada ou ignorada
        try:
            validate_sql_security(query, allow_modifications=False)
        except SQLSecurityError as security_error:
            error_msg = f"EXECUÇÃO BLOQUEADA POR SEGURANÇA: {str(security_error)}"
            logger.error(f"Tentativa de execução de query insegura bloqueada: {error_msg}")
            logger.error(f"Query rejeitada: {query}")
            # Retorna erro em vez de levantar exceção para melhor feedback
            return {
                "error": "SEGURANÇA_SQL",
                "message": error_msg,
                "query_rejeitada": query,
                "comando_bloqueado": True
            }
        
        # Garante que conn_params seja válido, buscando do .env se necessário
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        logger.info(f"Executando query SEGURA: {query[:100]}... no banco: {db_type}")
        
        db = get_db(db_type, conn_params)
        result = db.execute_query(query)
        
        logger.info(f"Query executada com sucesso. {len(result)} registros retornados")
        return result
        
    except SQLSecurityError as security_error:
        # Segunda captura de segurança (redundância)
        error_msg = f"EXECUÇÃO BLOQUEADA POR SEGURANÇA: {str(security_error)}"
        logger.error(f"Validação de segurança falhou: {error_msg}")
        return {
            "error": "SEGURANÇA_SQL",
            "message": error_msg,
            "query_rejeitada": params.get("query", ""),
            "comando_bloqueado": True
        }
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}", exc_info=True)
        raise
