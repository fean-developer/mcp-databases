from db.factory import get_db

def insert_record(params: dict):
    """
    Insere um registro em uma tabela.
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table": "Usuarios",
        "data": { "nome": "Joao", "idade": 25 }
    }
    """
    db = get_db(params["db_type"], params["conn_params"])
    db.insert_record(params["table"], params["data"])
    return {"status": "ok"}
