from mcp_databases.db.factory import get_db

def list_tables(params: dict):
    """
    Lista todas as tabelas disponíveis.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    db = get_db(params["db_type"], params["conn_params"])
    return db.list_tables()
def list_tables(params: dict):
    """
    Lista todas as tabelas disponíveis.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    db = get_db(params["db_type"], params["conn_params"])
    return db.list_tables()
