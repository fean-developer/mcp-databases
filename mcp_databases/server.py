

from mcp_databases.logger import MCPLogger
from mcp_databases.config import load_env_config

# Carrega configurações do .env automaticamente na inicialização
load_env_config()

logger = MCPLogger.get_logger("mcp_databases.server")

from mcp.server.fastmcp import FastMCP

from mcp_databases.tools.execute_query import execute_query
from mcp_databases.tools.insert_record import insert_record
from mcp_databases.tools.list_tables import list_tables
from mcp_databases.tools.expose_schema import expose_schema
from mcp_databases.tools.security_admin import security_check, get_security_config
from mcp_databases.tools.ddl_operations import create_table, alter_table, drop_table
from mcp_databases.tools.dml_operations import update_records, delete_records, bulk_insert
from mcp_databases.resources.schema_snapshot import schema_snapshot
from mcp_databases.prompts.safe_query import safe_query_prompt

# Cria instância
mcp = FastMCP("mcp-databases")

# Tools
@mcp.tool("safe_query_prompt", description="Analisa uma query SQL e sugere melhorias de segurança. Apenas comandos SELECT são permitidos.")
def _safe_query_prompt(query: str):
    # Se safe_query_prompt for async, rodar com asyncio
    import asyncio
    return asyncio.run(safe_query_prompt(None, query))

@mcp.tool("execute_query", description="Executa uma query SQL no banco de dados especificado.")
def _execute_query(db_type: str, query: str, conn_params: dict):
    return execute_query({
        "db_type": db_type,
        "conn_params": conn_params,
        "query": query
    })

@mcp.tool("insert_record", description="Insere um registro em uma tabela do banco de dados especificado.")
def _insert_record(db_type: str, table: str, data: dict, conn_params: dict):
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

@mcp.tool("security_check", description="Verifica a segurança de uma query SQL sem executá-la. Retorna relatório detalhado de segurança.")
def _security_check(query: str):
    return security_check({
        "query": query
    })

@mcp.tool("get_security_config", description="Retorna a configuração atual de segurança do sistema MCP Databases.")
def _get_security_config():
    return get_security_config({})

# DDL Operations (Data Definition Language)
@mcp.tool("create_table", description="Cria uma nova tabela com validação de segurança. Permite definir colunas, tipos e constraints.")
def _create_table(db_type: str, conn_params: dict, table_name: str, columns: list, options: dict = {}):
    return create_table({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "columns": columns,
        "options": options
    })

@mcp.tool("alter_table", description="Altera uma tabela existente (adicionar/remover/modificar colunas) com validação de segurança.")
def _alter_table(db_type: str, conn_params: dict, table_name: str, operation: str, column_spec: dict):
    return alter_table({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "operation": operation,
        "column_spec": column_spec
    })

@mcp.tool("drop_table", description="Remove uma tabela com confirmação dupla de segurança. CUIDADO: operação irreversível!")
def _drop_table(db_type: str, conn_params: dict, table_name: str, confirmation: str, if_exists: bool = False):
    return drop_table({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "confirmation": confirmation,
        "if_exists": if_exists
    })

# DML Operations (Data Manipulation Language)
@mcp.tool("update_records", description="Atualiza registros com proteção contra SQL injection usando parâmetros seguros.")
def _update_records(db_type: str, conn_params: dict, table_name: str, set_values: dict, where_conditions: dict, safety_limit: int = 1000):
    return update_records({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "set_values": set_values,
        "where_conditions": where_conditions,
        "safety_limit": safety_limit
    })

@mcp.tool("delete_records", description="Exclui registros com confirmação dupla e proteção contra SQL injection. CUIDADO: operação irreversível!")
def _delete_records(db_type: str, conn_params: dict, table_name: str, where_conditions: dict, confirmation: str, safety_limit: int = 100):
    return delete_records({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "where_conditions": where_conditions,
        "confirmation": confirmation,
        "safety_limit": safety_limit
    })

@mcp.tool("bulk_insert", description="Insere múltiplos registros de forma eficiente e segura com proteção contra SQL injection.")
def _bulk_insert(db_type: str, conn_params: dict, table_name: str, records: list, batch_size: int = 100):
    return bulk_insert({
        "db_type": db_type,
        "conn_params": conn_params,
        "table_name": table_name,
        "records": records,
        "batch_size": batch_size
    })

# Resource
# @mcp.resource("schema_snapshot/{db_type}/{conn_params}")
# def schema_snapshot(db_type: str, conn_params: str):
#     return do_something(db_type, conn_params)

def main():
    logger.info("Inicializando MCP server...")
    try:
        mcp.run()
        logger.info("MCP server finalizado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao rodar MCP server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
