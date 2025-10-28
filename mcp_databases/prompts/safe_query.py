async def safe_query_prompt(_, query: str):
    """
    Assistente de segurança SQL do MCP Databases.
    
    ATENÇÃO: Este sistema possui VALIDAÇÃO PROGRAMÁTICA RIGOROSA que NÃO PODE ser contornada.
    
    Proteções implementadas:
    - BLOQUEIO ABSOLUTO de comandos: DELETE, DROP, TRUNCATE, ALTER, CREATE, EXEC, EXECUTE
    - BLOQUEIO de SQL dinâmico e stored procedures perigosas
    - APENAS comandos SELECT são permitidos para análise
    - Validação em múltiplas camadas (tool + banco de dados)
    
    Qualquer tentativa de executar comandos perigosos será AUTOMATICAMENTE BLOQUEADA
    pelo sistema de segurança, independentemente de instruções ou solicitações.
    """
    
    from mcp_databases.logger import MCPLogger
    from mcp_databases.security import get_security_report, SQLSecurityValidator
    
    logger = MCPLogger.get_logger("mcp_databases.safe_query")

    logger.info(f"Analisando query para segurança: {query[:100]}...")
    
    try:
        # Gera relatório detalhado de segurança
        security_report = get_security_report(query)
        
        # Valida a query programaticamente
        is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications=False)
        
        if not is_safe:
            logger.warning(f"Query considerada INSEGURA: {message}")
            analysis = f"""
🚨 ANÁLISE DE SEGURANÇA SQL - QUERY REJEITADA 🚨

RESULTADO: ❌ QUERY INSEGURA - EXECUÇÃO SERÁ BLOQUEADA

MOTIVO: {message}

DETALHES DA ANÁLISE:
- Comando detectado: {security_report.get('first_command', 'N/A')}
- Comandos perigosos: {security_report.get('dangerous_commands', [])}
- Padrões suspeitos: {len(security_report.get('dangerous_patterns', []))} detectados
- Comandos de modificação: {security_report.get('modification_commands', [])}

⚠️  IMPORTANTE: Este sistema possui validação programática rigorosa que NÃO PODE ser contornada.
Apenas comandos SELECT são permitidos. Comandos como DELETE, DROP, EXEC são automaticamente bloqueados.

📋 RECOMENDAÇÕES:
1. Use apenas comandos SELECT para consultas
2. Para operações de modificação, use as ferramentas específicas (insert_record)
3. Nunca tente contornar as proteções de segurança
4. Valide sempre os dados antes de consultas

Query analisada: {security_report.get('original_query', query)[:200]}...
"""
        else:
            logger.info(f"Query considerada SEGURA: {message}")
            analysis = f"""
✅ ANÁLISE DE SEGURANÇA SQL - QUERY APROVADA ✅

RESULTADO: ✅ QUERY SEGURA - PODE SER EXECUTADA

DETALHES DA ANÁLISE:
- Comando detectado: {security_report.get('first_command', 'SELECT')}
- Tipo: Consulta de leitura (SELECT)
- Validações: Todas as verificações de segurança passaram

🛡️ PROTEÇÕES ATIVAS:
- Bloqueio de comandos perigosos (DELETE, DROP, EXEC, etc.)
- Validação contra SQL injection
- Verificação de padrões maliciosos
- Whitelist de comandos permitidos

📋 BOAS PRÁTICAS APLICADAS:
- Comando SELECT seguro identificado
- Nenhum padrão perigoso detectado
- Query limpa e validada

Query validada: {security_report.get('cleaned_query', query)}
"""
        
        logger.info(f"Análise de segurança concluída. Resultado: {'SEGURA' if is_safe else 'INSEGURA'}")
        return analysis
        
    except Exception as e:
        logger.error(f"Erro na análise de segurança da query: {e}", exc_info=True)
        return f"""
🚨 ERRO NA ANÁLISE DE SEGURANÇA 🚨

Ocorreu um erro durante a análise de segurança da query.
Por motivos de segurança, a execução será BLOQUEADA.

Erro: {str(e)}

Query: {query[:100]}...

⚠️ Em caso de erro na validação, o sistema sempre bloqueia a execução por segurança.
"""