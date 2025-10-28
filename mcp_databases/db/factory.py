
from .mssql import MSSQLDB
from .mysql import MySQLDB
from .postgres import PostgresDB
from mcp_databases.logger import MCPLogger
from typing import Dict, Any


def get_db(db_type: str, conn_params: dict):
    """
    Cria uma instância de banco de dados do tipo especificado.
    
    Args:
        db_type: Tipo do banco (mssql, mysql, postgres)
        conn_params: Parâmetros de conexão obrigatórios
        
    Returns:
        Instância da classe de banco de dados correspondente
    """
    logger = MCPLogger.get_logger("mcp_databases.db.factory")
    logger.info(f"get_db chamado com db_type={db_type}, conn_params={'***' if conn_params else 'None'}")

    SUPPORTED_TYPES = {"mssql": MSSQLDB, "mysql": MySQLDB, "postgres": PostgresDB}
    if db_type not in SUPPORTED_TYPES:
        logger.error(f"Tipo de banco não suportado: {db_type}")
        raise ValueError(f"Tipo de banco não suportado: {db_type}. Tipos suportados: {list(SUPPORTED_TYPES.keys())}")

    if not conn_params:
        raise ValueError("conn_params é obrigatório e não pode ser None ou vazio")

    # Normaliza aliases de parâmetros de conexão
    conn_params = normalize_conn_params(conn_params)
    
    # Validação básica dos parâmetros
    validate_conn_params(conn_params, db_type)

    db_class = SUPPORTED_TYPES[db_type]
    return db_class(conn_params)


def normalize_conn_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os parâmetros de conexão para um formato padrão.
    
    Args:
        params: Parâmetros de conexão originais
        
    Returns:
        Parâmetros normalizados
    """
    if params is None:
        return params
    
    normalized = params.copy()
    
    # Normaliza server/host
    if "server" not in normalized and "host" in normalized:
        normalized["server"] = normalized["host"]
    
    # Normaliza database
    if "database" not in normalized:
        if "db" in normalized:
            normalized["database"] = normalized["db"]
        elif "dbname" in normalized:
            normalized["database"] = normalized["dbname"]
    
    return normalized


def validate_conn_params(params: Dict[str, Any], db_type: str) -> None:
    """
    Valida se os parâmetros de conexão estão completos.
    
    Args:
        params: Parâmetros de conexão
        db_type: Tipo do banco de dados
        
    Raises:
        ValueError: Se parâmetros obrigatórios estiverem faltando
    """
    required_params = ["server", "database", "user"]
    missing_params = [param for param in required_params if not params.get(param)]
    
    if missing_params:
        raise ValueError(f"Parâmetros obrigatórios faltando para {db_type}: {missing_params}")
