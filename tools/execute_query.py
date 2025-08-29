from db.factory import get_db

def execute_query(params: dict):
    """
    Executa uma query arbitrária no banco.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "query": "SELECT * FROM ..."
    }
    """
    db = get_db(params["db_type"], params["conn_params"])
    return db.execute_query(params["query"])
