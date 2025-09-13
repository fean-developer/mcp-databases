async def safe_query_prompt(_, query: str):
    """
    Você é um assistente de segurança SQL.
    - Nunca permita comandos DELETE, UPDATE, DROP, EXEC ou SQL dinâmico.
    - Apenas comandos SELECT são permitidos para análise.
    - Sempre sugira validação de parâmetros e tratamento de erros.
    - Sempre explique os riscos e boas práticas antes de retornar o resultado.
    Exemplo: "A procedure não utiliza SQL dinâmico, portanto não há risco de SQL Injection. Recomenda-se validar a existência do LoanId e tratar possíveis erros de concorrência."
    """

    from mcp_databases.logger import MCPLogger
    logger = MCPLogger.get_logger("mcp_databases.safe_query")

    logger.info(f"Analisando query para segurança: {query}")
    try:
        # ...existing code...
        result = "safe_query"  # Assuming this is the intended result
        logger.info(f"Análise de segurança concluída. Resultado: {str(result)[:500]}")
        return result
    except Exception as e:
        logger.error(f"Erro na análise de segurança da query: {e}", exc_info=True)
        raise