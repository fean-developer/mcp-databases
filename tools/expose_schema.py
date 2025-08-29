from db.factory import get_db

def expose_schema(params: dict):
    """
    Retorna o schema das tabelas (colunas + tipos).
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...}
    }
    """
    db = get_db(params["db_type"], params["conn_params"])
    return db.get_schema()
