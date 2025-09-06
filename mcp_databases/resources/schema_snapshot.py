from mcp_databases.db.factory import get_db

def schema_snapshot(params: dict):
    """
    Gera um snapshot do schema atual (útil como recurso MCP).
    """
    db = get_db(params["db_type"], params["conn_params"])
    return {
        "name": f"{params['db_type']}_schema",
        "content": db.get_schema()
    }
