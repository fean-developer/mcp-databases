from mcp.server.fastmcp import FastMCP

from tools.execute_query import execute_query
from tools.insert_record import insert_record
from tools.list_tables import list_tables
from tools.expose_schema import expose_schema
from resources.schema_snapshot import schema_snapshot

# Cria instância
mcp = FastMCP("mcp-databases")

# Tools
@mcp.tool("execute_query", description="Executa uma query SQL no banco de dados especificado.")
def _execute_query(db_type: str, conn_params: dict, query: str):
    return execute_query({
        "db_type": db_type,
        "conn_params": conn_params,
        "query": query
    })

@mcp.tool("insert_record", description="Insere um registro em uma tabela do banco de dados especificado.")
def _insert_record(db_type: str, conn_params: dict, table: str, data: dict):
    return insert_record({
        "db_type": db_type,
        "conn_params": conn_params,
        "table": table,
        "data": data
    })

@mcp.tool("list_tables", description="Lista todas as tabelas do banco de dados especificado.")
def _list_tables(db_type: str, conn_params: dict):
    return list_tables({
        "db_type": db_type,
        "conn_params": conn_params
    })

@mcp.tool("expose_schema", description="Expõe o schema do banco de dados especificado.")
def _expose_schema(db_type: str, conn_params: dict):
    return expose_schema({
        "db_type": db_type,
        "conn_params": conn_params
    })

# Resource
@mcp.resource("schema_snapshot/{db_type}/{conn_params}")
def schema_snapshot(db_type: str, conn_params: str):
    return do_something(db_type, conn_params)

if __name__ == "__main__":
    mcp.run()
