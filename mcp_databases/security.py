"""
Sistema de segurança SQL para o MCP Databases.
Implementa validações rigorosas para prevenir execução de comandos perigosos.
"""
import re
from typing import Dict, Any, List, Tuple
from mcp_databases.logger import MCPLogger

logger = MCPLogger.get_logger("mcp_databases.security")


class SQLSecurityError(Exception):
    """Exceção levantada quando uma query SQL é considerada insegura."""
    pass


class SQLSecurityValidator:
    """
    Validador de segurança SQL que implementa múltiplas camadas de proteção.
    """
    
    # Comandos SQL perigosos que são completamente bloqueados
    DANGEROUS_COMMANDS = {
        'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE',
        'INSERT', 'UPDATE', 'MERGE', 'BULK', 'OPENROWSET', 'OPENDATASOURCE',
        'xp_', 'sp_', 'SHUTDOWN', 'KILL', 'RESTORE', 'BACKUP'
    }
    
    # Padrões regex para detectar SQL dinâmico e comandos perigosos
    DANGEROUS_PATTERNS = [
        r'\bEXEC\s*\(',                    # EXEC(
        r'\bEXECUTE\s*\(',                 # EXECUTE(
        r'\bsp_executesql\b',              # sp_executesql
        r'\bEVAL\s*\(',                    # EVAL(
        r'@@\w+',                          # @@version, @@servername, etc.
        r'\bxp_\w+',                       # xp_cmdshell, etc.
        r'\bOPENROWSET\b',                 # OPENROWSET
        r'\bOPENDATASOURCE\b',             # OPENDATASOURCE
        r'\bBULK\s+INSERT\b',              # BULK INSERT
        r'\bSHUTDOWN\b',                   # SHUTDOWN
        r'\bKILL\b',                       # KILL
        r';.*\s*(DELETE|DROP|TRUNCATE|ALTER|CREATE|INSERT|UPDATE)',  # Múltiplos comandos
        r'--.*\s*(DELETE|DROP|TRUNCATE|ALTER|CREATE|INSERT|UPDATE)', # Comandos em comentários
        r'/\*.*\s*(DELETE|DROP|TRUNCATE|ALTER|CREATE|INSERT|UPDATE).*\*/', # Comandos em comentários de bloco
    ]
    
    # Comandos permitidos (whitelist) - mais restritivo
    ALLOWED_COMMANDS = {'SELECT', 'WITH'}
    
    # Comandos que precisam de análise especial (podem ser perigosos em contextos específicos)
    CONDITIONAL_COMMANDS = {'UNION', 'INTERSECT', 'EXCEPT'}
    
    @classmethod
    def validate_query(cls, query: str, allow_modifications: bool = False) -> Tuple[bool, str]:
        """
        Valida se uma query SQL é segura para execução.
        
        Args:
            query: Query SQL a ser validada
            allow_modifications: Se True, permite comandos de modificação (INSERT, UPDATE, DELETE) - CUIDADO!
            
        Returns:
            Tuple[bool, str]: (é_segura, mensagem_de_erro_ou_aviso)
        """
        if not query or not isinstance(query, str):
            return False, "Query vazia ou inválida"
        
        # Remove comentários e normaliza a query
        cleaned_query = cls._clean_query(query)
        
        if not cleaned_query.strip():
            return False, "Query vazia após limpeza"
        
        # 1. Verificação de comandos perigosos (sempre bloqueados)
        dangerous_found = cls._check_dangerous_commands(cleaned_query)
        if dangerous_found:
            error_msg = f"COMANDO PERIGOSO DETECTADO: {', '.join(dangerous_found)}. Execução BLOQUEADA por segurança."
            logger.error(f"Tentativa de execução de comando perigoso bloqueada: {dangerous_found} na query: {query[:100]}...")
            return False, error_msg
        
        # 2. Verificação de padrões perigosos via regex
        dangerous_patterns = cls._check_dangerous_patterns(cleaned_query)
        if dangerous_patterns:
            error_msg = f"PADRÃO PERIGOSO DETECTADO: SQL dinâmico ou comando suspeito. Execução BLOQUEADA por segurança."
            logger.error(f"Padrão perigoso detectado na query: {query[:100]}...")
            return False, error_msg
        
        # 3. Verificação de comandos de modificação (se não permitidos)
        if not allow_modifications:
            modification_commands = cls._check_modification_commands(cleaned_query)
            if modification_commands:
                error_msg = f"COMANDOS DE MODIFICAÇÃO DETECTADOS: {', '.join(modification_commands)}. Apenas comandos SELECT são permitidos."
                logger.warning(f"Tentativa de execução de comando de modificação bloqueada: {modification_commands}")
                return False, error_msg
        
        # 4. Verificação de comandos condicionais (UNION, etc.)
        conditional_commands = cls._check_conditional_commands(cleaned_query)
        if conditional_commands:
            # UNION e similares podem ser perigosos se mal usados, então vamos ser mais cautelosos
            logger.warning(f"Comandos condicionais detectados: {conditional_commands}")
            # Por segurança, vamos bloquear por padrão - pode ser relaxado se necessário
            error_msg = f"COMANDOS CONDICIONAIS DETECTADOS: {', '.join(conditional_commands)}. Bloqueado por precaução de segurança."
            return False, error_msg
        
        # 5. Verificação de whitelist (apenas comandos permitidos)
        first_command = cls._get_first_command(cleaned_query)
        if first_command and first_command not in cls.ALLOWED_COMMANDS:
            if not allow_modifications or first_command in cls.DANGEROUS_COMMANDS:
                error_msg = f"COMANDO NÃO PERMITIDO: '{first_command}'. Apenas comandos SELECT e WITH são permitidos."
                logger.warning(f"Comando não permitido detectado: {first_command}")
                return False, error_msg
        
        # Query passou em todas as validações
        logger.info(f"Query validada com sucesso: {query[:100]}...")
        return True, "Query validada com sucesso - segura para execução"
    
    @classmethod
    def _clean_query(cls, query: str) -> str:
        """Remove comentários e normaliza a query."""
        # Remove comentários de linha
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        
        # Remove comentários de bloco
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Normaliza espaços em branco
        query = ' '.join(query.split())
        
        return query.strip()
    
    @classmethod
    def _check_dangerous_commands(cls, query: str) -> List[str]:
        """Verifica se a query contém comandos perigosos."""
        query_upper = query.upper()
        found_dangerous = []
        
        for dangerous_cmd in cls.DANGEROUS_COMMANDS:
            # Verifica se o comando aparece como palavra completa
            pattern = r'\b' + re.escape(dangerous_cmd.upper()) + r'\b'
            if re.search(pattern, query_upper):
                found_dangerous.append(dangerous_cmd)
        
        return found_dangerous
    
    @classmethod
    def _check_dangerous_patterns(cls, query: str) -> List[str]:
        """Verifica se a query contém padrões perigosos."""
        found_patterns = []
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                found_patterns.append(pattern)
        
        return found_patterns
    
    @classmethod
    def _check_modification_commands(cls, query: str) -> List[str]:
        """Verifica se a query contém comandos de modificação."""
        modification_commands = {'INSERT', 'UPDATE', 'DELETE', 'MERGE'}
        query_upper = query.upper()
        found_modifications = []
        
        for mod_cmd in modification_commands:
            pattern = r'\b' + re.escape(mod_cmd) + r'\b'
            if re.search(pattern, query_upper):
                found_modifications.append(mod_cmd)
        
        return found_modifications
    
    @classmethod
    def _check_conditional_commands(cls, query: str) -> List[str]:
        """Verifica se a query contém comandos condicionais que podem ser perigosos."""
        query_upper = query.upper()
        found_conditional = []
        
        for cond_cmd in cls.CONDITIONAL_COMMANDS:
            pattern = r'\b' + re.escape(cond_cmd) + r'\b'
            if re.search(pattern, query_upper):
                found_conditional.append(cond_cmd)
        
        return found_conditional
    
    @classmethod
    def _get_first_command(cls, query: str) -> str:
        """Extrai o primeiro comando SQL da query."""
        query_upper = query.upper().strip()
        if not query_upper:
            return ""
        
        # Extrai a primeira palavra que parece ser um comando SQL
        match = re.match(r'^(\w+)', query_upper)
        if match:
            return match.group(1)
        
        return ""


def validate_sql_security(query: str, allow_modifications: bool = False) -> None:
    """
    Função utilitária para validar segurança SQL.
    Levanta SQLSecurityError se a query for considerada insegura.
    
    Args:
        query: Query SQL a ser validada
        allow_modifications: Se True, permite comandos de modificação
        
    Raises:
        SQLSecurityError: Se a query for considerada insegura
    """
    is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications)
    
    if not is_safe:
        raise SQLSecurityError(message)
    
    logger.info(f"Validação de segurança passou: {message}")


def get_security_report(query: str) -> Dict[str, Any]:
    """
    Gera um relatório detalhado de segurança para uma query.
    
    Args:
        query: Query SQL a ser analisada
        
    Returns:
        Dict com informações detalhadas sobre a segurança da query
    """
    is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications=False)
    
    cleaned_query = SQLSecurityValidator._clean_query(query)
    dangerous_commands = SQLSecurityValidator._check_dangerous_commands(cleaned_query)
    dangerous_patterns = SQLSecurityValidator._check_dangerous_patterns(cleaned_query)
    modification_commands = SQLSecurityValidator._check_modification_commands(cleaned_query)
    first_command = SQLSecurityValidator._get_first_command(cleaned_query)
    
    return {
        "is_safe": is_safe,
        "message": message,
        "first_command": first_command,
        "dangerous_commands": dangerous_commands,
        "dangerous_patterns": dangerous_patterns,
        "modification_commands": modification_commands,
        "cleaned_query": cleaned_query[:200] + "..." if len(cleaned_query) > 200 else cleaned_query,
        "original_query": query[:200] + "..." if len(query) > 200 else query
    }