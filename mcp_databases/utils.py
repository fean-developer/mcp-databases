"""
Utilitários comuns para as tools do MCP Databases.
"""
from typing import Dict, Any
from mcp_databases.config import get_db_config
from mcp_databases.logger import MCPLogger

logger = MCPLogger.get_logger("mcp_databases.utils")


def ensure_valid_conn_params(db_type: str, conn_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garante que os parâmetros de conexão sejam válidos.
    Se não forem, busca automaticamente do .env.
    
    Args:
        db_type: Tipo do banco de dados
        conn_params: Parâmetros de conexão fornecidos
        
    Returns:
        Dict: Parâmetros de conexão válidos
        
    Raises:
        ValueError: Se não conseguir obter configurações válidas
    """
    # Se conn_params está vazio, None ou inválido, busca automaticamente do .env
    if not conn_params or not is_valid_conn_params(conn_params):
        logger.info(f"Parâmetros de conexão não fornecidos ou inválidos. Buscando configurações do .env para {db_type}")
        env_params = get_db_config(db_type, interactive=True)
        if not env_params:
            raise ValueError(f"Não foi possível obter configurações válidas para o banco {db_type}")
        return env_params
    
    return conn_params


def is_valid_conn_params(conn_params: Dict[str, Any]) -> bool:
    """
    Verifica se os parâmetros de conexão são válidos.
    
    Args:
        conn_params: Parâmetros de conexão
        
    Returns:
        bool: True se válidos, False caso contrário
    """
    if not isinstance(conn_params, dict):
        return False
    
    # Verifica se tem pelo menos server/host e database
    has_server = bool(conn_params.get('server') or conn_params.get('host'))
    has_database = bool(conn_params.get('database') or conn_params.get('db') or conn_params.get('dbname'))
    
    return has_server and has_database