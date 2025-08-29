# MCP Databases Server

Este projeto implementa um servidor MCP (Model Context Protocol) em Python para expor operações de banco de dados relacionais (SQL Server, MySQL, PostgreSQL) como ferramentas MCP, permitindo que aplicações LLM e agentes consultem e manipulem dados de forma segura e eficiente.

## O que este MCP Server faz?
- Expõe operações de banco de dados como ferramentas MCP (tools) para uso por LLMs, agentes e automações.
- Permite executar queries, inserir registros, listar tabelas e expor o schema de bancos SQL Server, MySQL e PostgreSQL.
- Utiliza variáveis de ambiente para configuração segura de credenciais.
- Suporta integração com o VS Code e Claude via arquivo `mcp.json`.

## Tools disponíveis
- **execute_query**: Executa uma query SQL no banco de dados especificado.
- **insert_record**: Insere um registro em uma tabela do banco de dados especificado.
- **list_tables**: Lista todas as tabelas do banco de dados especificado.
- **expose_schema**: Expõe o schema do banco de dados especificado.

## Dependências
- Python 3.10+
- [MCP Python SDK >=1.2.0](https://github.com/modelcontextprotocol/python-sdk)
- [pyodbc](https://pypi.org/project/pyodbc/) (SQL Server)
- [pymysql](https://pypi.org/project/pymysql/) (MySQL)
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/) (PostgreSQL)
- Drivers ODBC:
  - SQL Server: `msodbcsql18` (Linux: `sudo apt-get install msodbcsql18`)
  - MySQL: `libmysqlclient-dev` (Linux: `sudo apt-get install libmysqlclient-dev`)
  - PostgreSQL: `libpq-dev` (Linux: `sudo apt-get install libpq-dev`)
- python-dotenv (opcional, para carregar variáveis de ambiente de um arquivo `.env`)

Instale as dependências Python com:
```sh
pip install -r requirements.txt
```

## Configuração de ambiente
Defina as variáveis de ambiente para o banco desejado. Exemplo para PostgreSQL:
```env
DB_TYPE=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=wlg48cd8
POSTGRES_DB=loan_pgsql
```

## Como rodar o servidor MCP
```sh
python3 server.py
```

## Gerando o arquivo mcp.json
No diretório do projeto, crie um arquivo `mcp.json` com o seguinte conteúdo:
```json
{
  "server": "http://localhost:8000", // ou o endpoint do seu MCP server
  "tools": [
    "execute_query",
    "insert_record",
    "list_tables",
    "expose_schema"
  ]
}
```

## Exemplo de settings para VS Code
No `settings.json` do VS Code, adicione:
```json
{
  "modelcontext.mcp.servers": [
    {
      "name": "MCP Databases",
      "url": "http://localhost:8000",
      "tools": [
        "execute_query",
        "insert_record",
        "list_tables",
        "expose_schema"
      ]
    }
  ]
}
```

---

Para dúvidas ou contribuições, consulte a documentação oficial do [Model Context Protocol](https://modelcontextprotocol.io/) ou abra uma issue neste repositório.
