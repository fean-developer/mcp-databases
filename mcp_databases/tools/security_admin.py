"""
Tool para administração de segurança do MCP Databases.
Permite verificar o status de segurança e gerar relatórios detalhados.
"""
from mcp_databases.logger import MCPLogger
from mcp_databases.security import get_security_report, SQLSecurityValidator
from typing import Dict, Any

logger = MCPLogger.get_logger("mcp_databases.security_admin")


def security_check(params: Dict[str, Any]):
    """
    Verifica o status de segurança de uma query sem executá-la.
    Espera:
    {
        "query": "SQL query a ser analisada"
    }
    """
    try:
        query = params["query"]
        
        logger.info(f"Verificando segurança da query: {query[:100]}...")
        
        # Gera relatório completo de segurança
        security_report = get_security_report(query)
        
        logger.info(f"Relatório de segurança gerado para query")
        return security_report
        
    except Exception as e:
        logger.error(f"Erro ao verificar segurança: {e}", exc_info=True)
        raise


def get_security_config(params: Dict[str, Any]):
    """
    Retorna a configuração atual de segurança do sistema.
    Espera:
    {
        # Sem parâmetros necessários
    }
    """
    try:
        logger.info("Obtendo configuração de segurança do sistema")
        
        config = {
            "dangerous_commands_blocked": list(SQLSecurityValidator.DANGEROUS_COMMANDS),
            "allowed_commands": list(SQLSecurityValidator.ALLOWED_COMMANDS),
            "total_dangerous_patterns": len(SQLSecurityValidator.DANGEROUS_PATTERNS),
            "security_level": "MÁXIMO",
            "modifications_allowed": False,
            "interactive_mode_blocks_dangerous": True,
            "multilayer_protection": {
                "tool_level": True,
                "database_level": True,
                "prompt_level": True
            },
            "description": "Sistema de segurança com proteção em múltiplas camadas. Apenas comandos SELECT são permitidos."
        }
        
        logger.info("Configuração de segurança retornada")
        return config
        
    except Exception as e:
        logger.error(f"Erro ao obter configuração de segurança: {e}", exc_info=True)
        raise