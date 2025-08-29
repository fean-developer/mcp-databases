# copilot-instructions.md for MCP Python SQL Server Project

## Project Overview
This project implements a Model Context Protocol (MCP) server in Python to interact with a Microsoft SQL Server database. The MCP server will expose database operations as MCP tools, enabling LLM applications and agentic workflows to query and manipulate SQL Server data securely and efficiently.

## References
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Server Quickstart (Python)](https://modelcontextprotocol.io/quickstart/server)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Example Servers](https://github.com/modelcontextprotocol/servers)

## Key Steps
1. Use the official MCP Python SDK to build the server.
2. Expose SQL Server operations (query, insert, update, delete) as MCP tools.
3. Use the `pyodbc` or `pymssql` package for SQL Server connectivity.
4. Follow MCP best practices: do not print to stdout, use logging to stderr.
5. Provide a `mcp.json` config for VS Code/Claude integration.
6. Document all tools and resources exposed by the server.

## Development Rules
- Use Python 3.10+ and MCP Python SDK >=1.2.0.
- All MCP messages must use JSON-RPC 2.0.
- For STDIO transport, never write to stdout except for protocol messages.
- Use environment variables for sensitive credentials.
- Follow OAuth 2.1 and MCP security best practices if exposing HTTP endpoints.

## Next Steps
- Scaffold the Python MCP server project.
- Add SQL Server tool implementations.
- Test with a local or remote SQL Server instance.
- Provide usage instructions in README.md.

---

Remove this section after project setup is complete.
