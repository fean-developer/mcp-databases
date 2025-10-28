# copilot-instructions.md para Projeto MCP Python SQL Server

## Visão Geral do Projeto
Este projeto implementa um servidor Model Context Protocol (MCP) em Python para interagir com um banco de dados Microsoft SQL Server. O servidor MCP irá expor operações de banco de dados como ferramentas MCP, permitindo que aplicações LLM e fluxos de trabalho agentivos consultem e manipulem dados do SQL Server de forma segura e eficiente.

## Referências
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Documentação do Protocolo MCP](https://modelcontextprotocol.io/)
- [Guia Rápido do Servidor MCP (Python)](https://modelcontextprotocol.io/quickstart/server)
- [Especificação MCP](https://spec.modelcontextprotocol.io/)
- [Servidores de Exemplo MCP](https://github.com/modelcontextprotocol/servers)

## Etapas Principais
1. Use o SDK oficial MCP Python para construir o servidor.
2. Exponha operações do SQL Server (consulta, inserção, atualização, exclusão) como ferramentas MCP.
3. Use o pacote `pyodbc` ou `pymssql` para conectividade com SQL Server.
4. Siga as melhores práticas do MCP: não imprima no stdout, use logging no stderr.
5. Forneça uma configuração `mcp.json` para integração com VS Code/Claude.
6. Documente todas as ferramentas e recursos expostos pelo servidor.

## Regras de Desenvolvimento
- Use Python 3.10+ e MCP Python SDK >=1.2.0.
- Todas as mensagens MCP devem usar JSON-RPC 2.0.
- Para transporte STDIO, nunca escreva no stdout exceto para mensagens de protocolo.
- Use variáveis de ambiente para credenciais sensíveis.
- Siga OAuth 2.1 e melhores práticas de segurança MCP se expondo endpoints HTTP.

## Próximos Passos
- Estruture o projeto do servidor MCP Python.
- Adicione implementações de ferramentas SQL Server.
- Teste com uma instância local ou remota do SQL Server.
- Forneça instruções de uso no README.md.

---

Remova esta seção após a conclusão da configuração do projeto.
