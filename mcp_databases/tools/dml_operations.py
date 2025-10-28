"""
Tools seguras para operações DML (Data Manipulation Language) no MCP Databases.
Permite atualização e exclusão de registros com validação rigorosa contra SQL injection.
"""
from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
from mcp_databases.utils import ensure_valid_conn_params
from typing import Dict, Any, List, Union
import re

logger = MCPLogger.get_logger("mcp_databases.dml_operations")


class DMLSecurityError(Exception):
    """Exceção para operações DML inseguras."""
    pass


def update_records(params: Dict[str, Any]):
    """
    Atualiza registros com validação de segurança contra SQL injection.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "users",
        "set_values": {
            "name": "João Silva",
            "email": "joao@email.com",
            "status": "active"
        },
        "where_conditions": {
            "id": 123,
            "department": "IT"
        },
        "safety_limit": 100  # Opcional: limite máximo de registros afetados
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        set_values = params["set_values"]
        where_conditions = params["where_conditions"]
        safety_limit = params.get("safety_limit", 1000)  # Limite padrão de segurança
        
        # Validação de segurança
        _validate_dml_operation(table_name, set_values, where_conditions, "UPDATE")
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        # Gera SQL seguro usando parâmetros
        update_sql, sql_params = _generate_update_sql(db_type, table_name, set_values, where_conditions)
        
        logger.info(f"Atualizando registros na tabela {table_name}")
        logger.info(f"SQL: {update_sql}")
        logger.info(f"Parâmetros: {len(sql_params)} valores")
        
        db = get_db(db_type, conn_params)
        
        # Primeiro, verifica quantos registros seriam afetados
        count_sql, count_params = _generate_count_sql(db_type, table_name, where_conditions)
        affected_count = _execute_count_query(db, count_sql, count_params)
        
        if affected_count > safety_limit:
            raise DMLSecurityError(f"Operação cancelada: {affected_count} registros seriam afetados (limite: {safety_limit})")
        
        # Executa a atualização
        result = _execute_dml_safely(db, update_sql, sql_params, "UPDATE")
        
        logger.info(f"Registros atualizados com sucesso: {affected_count}")
        return {
            "success": True,
            "message": f"{affected_count} registro(s) atualizado(s) com sucesso",
            "table_name": table_name,
            "affected_rows": affected_count,
            "sql_template": update_sql,
            "parameters_count": len(sql_params)
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar registros: {e}", exc_info=True)
        raise


def delete_records(params: Dict[str, Any]):
    """
    Exclui registros com validação de segurança e confirmação dupla.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "users",
        "where_conditions": {
            "id": 123,
            "status": "inactive"
        },
        "confirmation": "DELETE_FROM_users_WHERE_id_123",  # Confirmação obrigatória
        "safety_limit": 10  # Opcional: limite máximo de registros excluídos
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        where_conditions = params["where_conditions"]
        confirmation = params["confirmation"]
        safety_limit = params.get("safety_limit", 100)  # Limite padrão mais baixo para DELETE
        
        # Validação de confirmação dupla
        expected_confirmation = _generate_delete_confirmation(table_name, where_conditions)
        if confirmation != expected_confirmation:
            raise DMLSecurityError(f"Confirmação de segurança incorreta. Esperado algo como: 'DELETE_FROM_{table_name}_WHERE_...'")
        
        # Validação de segurança
        _validate_dml_operation(table_name, {}, where_conditions, "DELETE")
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        # Gera SQL seguro usando parâmetros
        delete_sql, sql_params = _generate_delete_sql(db_type, table_name, where_conditions)
        
        logger.warning(f"EXCLUINDO registros da tabela {table_name}")
        logger.warning(f"SQL: {delete_sql}")
        
        db = get_db(db_type, conn_params)
        
        # Primeiro, verifica quantos registros seriam afetados
        count_sql, count_params = _generate_count_sql(db_type, table_name, where_conditions)
        affected_count = _execute_count_query(db, count_sql, count_params)
        
        if affected_count > safety_limit:
            raise DMLSecurityError(f"Operação cancelada: {affected_count} registros seriam excluídos (limite: {safety_limit})")
        
        # Executa a exclusão
        result = _execute_dml_safely(db, delete_sql, sql_params, "DELETE")
        
        logger.warning(f"Registros EXCLUÍDOS: {affected_count}")
        return {
            "success": True,
            "message": f"{affected_count} registro(s) excluído(s) com sucesso",
            "table_name": table_name,
            "affected_rows": affected_count,
            "sql_template": delete_sql,
            "warning": "OPERAÇÃO DE EXCLUSÃO EXECUTADA - DADOS PERDIDOS PERMANENTEMENTE"
        }
        
    except Exception as e:
        logger.error(f"Erro ao excluir registros: {e}", exc_info=True)
        raise


def bulk_insert(params: Dict[str, Any]):
    """
    Insere múltiplos registros de forma eficiente e segura.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "users",
        "records": [
            {"name": "João", "email": "joao@email.com"},
            {"name": "Maria", "email": "maria@email.com"},
            {"name": "Pedro", "email": "pedro@email.com"}
        ],
        "batch_size": 100  # Opcional: tamanho do lote
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        records = params["records"]
        batch_size = params.get("batch_size", 100)
        
        # Validação de segurança
        _validate_table_name(table_name)
        
        if not records or not isinstance(records, list):
            raise DMLSecurityError("Lista de registros é obrigatória")
        
        if len(records) > 10000:  # Limite de segurança
            raise DMLSecurityError(f"Muitos registros para inserção em lote: {len(records)} (máximo: 10000)")
        
        # Valida estrutura dos registros
        _validate_bulk_records(records)
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        logger.info(f"Inserindo {len(records)} registros na tabela {table_name}")
        
        db = get_db(db_type, conn_params)
        
        # Processa em lotes
        total_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Gera SQL seguro para o lote
            insert_sql, sql_params = _generate_bulk_insert_sql(db_type, table_name, batch)
            
            # Executa o lote
            _execute_dml_safely(db, insert_sql, sql_params, "BULK INSERT")
            total_inserted += len(batch)
            
            logger.info(f"Lote {i//batch_size + 1}: {len(batch)} registros inseridos")
        
        logger.info(f"Inserção em lote concluída: {total_inserted} registros")
        return {
            "success": True,
            "message": f"{total_inserted} registro(s) inserido(s) com sucesso",
            "table_name": table_name,
            "total_inserted": total_inserted,
            "batches_processed": (len(records) + batch_size - 1) // batch_size
        }
        
    except Exception as e:
        logger.error(f"Erro na inserção em lote: {e}", exc_info=True)
        raise


def _validate_dml_operation(table_name: str, set_values: Dict, where_conditions: Dict, operation: str) -> None:
    """Valida operação DML."""
    _validate_table_name(table_name)
    
    if operation == "UPDATE" and not set_values:
        raise DMLSecurityError("Valores para atualização são obrigatórios")
    
    if not where_conditions:
        raise DMLSecurityError(f"Condições WHERE são obrigatórias para {operation} por segurança")
    
    # Valida nomes de colunas
    for key in set_values.keys():
        _validate_column_name(key)
    
    for key in where_conditions.keys():
        _validate_column_name(key)
    
    # Valida valores para prevenir SQL injection
    _validate_parameter_values(set_values)
    _validate_parameter_values(where_conditions)


def _validate_table_name(table_name: str) -> None:
    """Valida nome de tabela."""
    if not table_name or not isinstance(table_name, str):
        raise DMLSecurityError("Nome da tabela é obrigatório")
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', table_name):
        raise DMLSecurityError("Nome da tabela deve começar com letra e conter apenas letras, números e underscore")


def _validate_column_name(column_name: str) -> None:
    """Valida nome de coluna."""
    if not column_name or not isinstance(column_name, str):
        raise DMLSecurityError("Nome da coluna é obrigatório")
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', column_name):
        raise DMLSecurityError("Nome da coluna deve começar com letra e conter apenas letras, números e underscore")


def _validate_parameter_values(values: Dict) -> None:
    """Valida valores de parâmetros para prevenir SQL injection."""
    for key, value in values.items():
        if isinstance(value, str):
            # Detecta padrões suspeitos que podem indicar SQL injection
            suspicious_patterns = [
                r"';.*--",           # Terminação de string e comentário
                r"'\s*or\s*'.*'",   # OR injection
                r"'\s*and\s*'.*'",  # AND injection
                r"union\s+select",   # UNION injection
                r"drop\s+table",     # DROP injection
                r"delete\s+from",    # DELETE injection
                r"insert\s+into",    # INSERT injection
                r"update\s+\w+\s+set", # UPDATE injection
                r"exec\s*\(",        # EXEC injection
                r"@@\w+",            # Variáveis de sistema
                r"xp_\w+",           # Procedimentos perigosos
            ]
            
            value_lower = value.lower()
            for pattern in suspicious_patterns:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    raise DMLSecurityError(f"Valor suspeito detectado na coluna '{key}': possível SQL injection")


def _validate_bulk_records(records: List[Dict]) -> None:
    """Valida registros para inserção em lote."""
    if not records:
        return
    
    # Verifica se todos os registros têm a mesma estrutura
    first_keys = set(records[0].keys())
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise DMLSecurityError(f"Registro {i+1} deve ser um dicionário")
        
        if set(record.keys()) != first_keys:
            raise DMLSecurityError(f"Registro {i+1} tem estrutura diferente do primeiro")
        
        # Valida nomes de colunas
        for key in record.keys():
            _validate_column_name(key)
        
        # Valida valores
        _validate_parameter_values(record)


def _generate_update_sql(db_type: str, table_name: str, set_values: Dict, where_conditions: Dict):
    """Gera SQL seguro para UPDATE usando parâmetros."""
    escaped_table = _escape_identifier(table_name, db_type)
    
    # SET clause
    set_clauses = []
    sql_params = []
    for key, value in set_values.items():
        escaped_key = _escape_identifier(key, db_type)
        set_clauses.append(f"{escaped_key} = {_get_parameter_placeholder(db_type)}")
        sql_params.append(value)
    
    # WHERE clause
    where_clauses = []
    for key, value in where_conditions.items():
        escaped_key = _escape_identifier(key, db_type)
        where_clauses.append(f"{escaped_key} = {_get_parameter_placeholder(db_type)}")
        sql_params.append(value)
    
    sql = f"UPDATE {escaped_table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
    
    return sql, sql_params


def _generate_delete_sql(db_type: str, table_name: str, where_conditions: Dict):
    """Gera SQL seguro para DELETE usando parâmetros."""
    escaped_table = _escape_identifier(table_name, db_type)
    
    # WHERE clause
    where_clauses = []
    sql_params = []
    for key, value in where_conditions.items():
        escaped_key = _escape_identifier(key, db_type)
        where_clauses.append(f"{escaped_key} = {_get_parameter_placeholder(db_type)}")
        sql_params.append(value)
    
    sql = f"DELETE FROM {escaped_table} WHERE {' AND '.join(where_clauses)}"
    
    return sql, sql_params


def _generate_count_sql(db_type: str, table_name: str, where_conditions: Dict):
    """Gera SQL para contar registros afetados."""
    escaped_table = _escape_identifier(table_name, db_type)
    
    # WHERE clause
    where_clauses = []
    sql_params = []
    for key, value in where_conditions.items():
        escaped_key = _escape_identifier(key, db_type)
        where_clauses.append(f"{escaped_key} = {_get_parameter_placeholder(db_type)}")
        sql_params.append(value)
    
    sql = f"SELECT COUNT(*) FROM {escaped_table} WHERE {' AND '.join(where_clauses)}"
    
    return sql, sql_params


def _generate_bulk_insert_sql(db_type: str, table_name: str, records: List[Dict]):
    """Gera SQL seguro para inserção em lote."""
    if not records:
        raise DMLSecurityError("Nenhum registro para inserir")
    
    escaped_table = _escape_identifier(table_name, db_type)
    
    # Colunas (baseado no primeiro registro)
    columns = list(records[0].keys())
    escaped_columns = [_escape_identifier(col, db_type) for col in columns]
    
    # Valores
    value_placeholders = []
    sql_params = []
    
    for record in records:
        row_placeholders = [_get_parameter_placeholder(db_type) for _ in columns]
        value_placeholders.append(f"({', '.join(row_placeholders)})")
        
        for col in columns:
            sql_params.append(record[col])
    
    sql = f"INSERT INTO {escaped_table} ({', '.join(escaped_columns)}) VALUES {', '.join(value_placeholders)}"
    
    return sql, sql_params


def _generate_delete_confirmation(table_name: str, where_conditions: Dict) -> str:
    """Gera uma string de confirmação para DELETE."""
    conditions_str = "_".join([f"{k}_{v}" for k, v in where_conditions.items()])
    return f"DELETE_FROM_{table_name}_WHERE_{conditions_str}"


def _escape_identifier(identifier: str, db_type: str) -> str:
    """Escapar identificadores SQL de forma segura."""
    if db_type.lower() == "mysql":
        return f"`{identifier}`"
    elif db_type.lower() == "postgres":
        return f'"{identifier}"'
    elif db_type.lower() == "mssql":
        return f"[{identifier}]"
    else:
        return identifier


def _get_parameter_placeholder(db_type: str) -> str:
    """Retorna o placeholder de parâmetro para o tipo de banco."""
    if db_type.lower() == "mysql":
        return "%s"
    elif db_type.lower() == "postgres":
        return "%s"
    elif db_type.lower() == "mssql":
        return "?"
    else:
        return "?"


def _execute_count_query(db, sql: str, params: List) -> int:
    """Executa query de contagem."""
    if hasattr(db, '_connect'):
        conn = db._connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    else:
        raise Exception("Método de conexão não encontrado")


def _execute_dml_safely(db, sql: str, params: List, operation_type: str):
    """Executa DML de forma segura usando parâmetros."""
    try:
        if hasattr(db, '_connect'):
            conn = db._connect()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            affected_rows = cursor.rowcount if hasattr(cursor, 'rowcount') else 0
            conn.commit()
            conn.close()
            
            return {"status": "success", "operation": operation_type, "affected_rows": affected_rows}
        else:
            raise Exception("Método de conexão não encontrado")
            
    except Exception as e:
        logger.error(f"Erro ao executar {operation_type}: {e}")
        raise