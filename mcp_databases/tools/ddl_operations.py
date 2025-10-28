"""
Tools seguras para operações DDL (Data Definition Language) no MCP Databases.
Permite criação de tabelas com validação rigorosa de segurança.
"""
from mcp_databases.db.factory import get_db
from mcp_databases.logger import MCPLogger
from mcp_databases.utils import ensure_valid_conn_params
from typing import Dict, Any, List
import re

logger = MCPLogger.get_logger("mcp_databases.ddl_operations")


class DDLSecurityError(Exception):
    """Exceção para operações DDL inseguras."""
    pass


def create_table(params: Dict[str, Any]):
    """
    Cria uma nova tabela com validação de segurança.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "nome_da_tabela",
        "columns": [
            {"name": "id", "type": "INT", "constraints": ["PRIMARY KEY", "AUTO_INCREMENT"]},
            {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
            {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE"]}
        ],
        "options": {
            "if_not_exists": true,  # Opcional
            "engine": "InnoDB",     # MySQL específico
            "charset": "utf8mb4"    # MySQL específico
        }
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        columns = params["columns"]
        options = params.get("options", {})
        
        # Validação de segurança
        _validate_table_creation(table_name, columns, options)
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        # Gera o SQL de criação de forma segura
        create_sql = _generate_create_table_sql(db_type, table_name, columns, options)
        
        logger.info(f"Criando tabela {table_name} no banco {db_type}")
        logger.info(f"SQL gerado: {create_sql}")
        
        db = get_db(db_type, conn_params)
        
        # Executa usando método específico para DDL (sem validação de SELECT)
        result = _execute_ddl_safely(db, create_sql, "CREATE TABLE")
        
        logger.info(f"Tabela {table_name} criada com sucesso")
        return {
            "success": True,
            "message": f"Tabela '{table_name}' criada com sucesso",
            "table_name": table_name,
            "sql_executed": create_sql,
            "columns_created": len(columns)
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar tabela: {e}", exc_info=True)
        raise


def alter_table(params: Dict[str, Any]):
    """
    Altera uma tabela existente com validação de segurança.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "nome_da_tabela",
        "operation": "ADD_COLUMN|DROP_COLUMN|MODIFY_COLUMN|RENAME_COLUMN",
        "column_spec": {
            "name": "nova_coluna",
            "type": "VARCHAR(100)",
            "constraints": ["NOT NULL"],
            "position": "AFTER existing_column"  # MySQL específico
        }
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        operation = params["operation"]
        column_spec = params["column_spec"]
        
        # Validação de segurança
        _validate_table_alteration(table_name, operation, column_spec)
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        # Gera o SQL de alteração de forma segura
        alter_sql = _generate_alter_table_sql(db_type, table_name, operation, column_spec)
        
        logger.info(f"Alterando tabela {table_name} no banco {db_type}")
        logger.info(f"SQL gerado: {alter_sql}")
        
        db = get_db(db_type, conn_params)
        
        # Executa usando método específico para DDL
        result = _execute_ddl_safely(db, alter_sql, "ALTER TABLE")
        
        logger.info(f"Tabela {table_name} alterada com sucesso")
        return {
            "success": True,
            "message": f"Tabela '{table_name}' alterada com sucesso",
            "table_name": table_name,
            "operation": operation,
            "sql_executed": alter_sql
        }
        
    except Exception as e:
        logger.error(f"Erro ao alterar tabela: {e}", exc_info=True)
        raise


def drop_table(params: Dict[str, Any]):
    """
    Remove uma tabela com confirmação dupla de segurança.
    
    Espera:
    {
        "db_type": "mssql|mysql|postgres",
        "conn_params": {...},
        "table_name": "nome_da_tabela",
        "confirmation": "DELETE_TABLE_nome_da_tabela",  # Confirmação obrigatória
        "if_exists": true  # Opcional
    }
    """
    try:
        db_type = params["db_type"]
        conn_params = params["conn_params"]
        table_name = params["table_name"]
        confirmation = params["confirmation"]
        if_exists = params.get("if_exists", False)
        
        # Validação de segurança com confirmação dupla
        expected_confirmation = f"DELETE_TABLE_{table_name}"
        if confirmation != expected_confirmation:
            raise DDLSecurityError(f"Confirmação de segurança incorreta. Esperado: '{expected_confirmation}'")
        
        _validate_table_name(table_name)
        
        # Garante que conn_params seja válido
        conn_params = ensure_valid_conn_params(db_type, conn_params)
        
        # Gera o SQL de remoção de forma segura
        drop_sql = _generate_drop_table_sql(db_type, table_name, if_exists)
        
        logger.warning(f"REMOVENDO tabela {table_name} no banco {db_type}")
        logger.warning(f"SQL gerado: {drop_sql}")
        
        db = get_db(db_type, conn_params)
        
        # Executa usando método específico para DDL
        result = _execute_ddl_safely(db, drop_sql, "DROP TABLE")
        
        logger.warning(f"Tabela {table_name} REMOVIDA com sucesso")
        return {
            "success": True,
            "message": f"Tabela '{table_name}' removida com sucesso",
            "table_name": table_name,
            "sql_executed": drop_sql,
            "warning": "OPERAÇÃO DE REMOÇÃO EXECUTADA - DADOS PERDIDOS PERMANENTEMENTE"
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover tabela: {e}", exc_info=True)
        raise


def _validate_table_creation(table_name: str, columns: List[Dict], options: Dict) -> None:
    """Valida parâmetros para criação de tabela."""
    _validate_table_name(table_name)
    
    if not columns or not isinstance(columns, list):
        raise DDLSecurityError("Lista de colunas é obrigatória e deve ser uma lista")
    
    for col in columns:
        if not isinstance(col, dict) or "name" not in col or "type" not in col:
            raise DDLSecurityError("Cada coluna deve ter 'name' e 'type'")
        
        _validate_column_name(col["name"])
        _validate_column_type(col["type"])
        
        if "constraints" in col:
            _validate_column_constraints(col["constraints"])


def _validate_table_alteration(table_name: str, operation: str, column_spec: Dict) -> None:
    """Valida parâmetros para alteração de tabela."""
    _validate_table_name(table_name)
    
    allowed_operations = ["ADD_COLUMN", "DROP_COLUMN", "MODIFY_COLUMN", "RENAME_COLUMN"]
    if operation not in allowed_operations:
        raise DDLSecurityError(f"Operação não permitida: {operation}. Permitidas: {allowed_operations}")
    
    if "name" not in column_spec:
        raise DDLSecurityError("Nome da coluna é obrigatório")
    
    _validate_column_name(column_spec["name"])
    
    if operation in ["ADD_COLUMN", "MODIFY_COLUMN"] and "type" not in column_spec:
        raise DDLSecurityError(f"Tipo da coluna é obrigatório para operação {operation}")


def _validate_table_name(table_name: str) -> None:
    """Valida nome de tabela."""
    if not table_name or not isinstance(table_name, str):
        raise DDLSecurityError("Nome da tabela é obrigatório")
    
    # Apenas caracteres alfanuméricos e underscore
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', table_name):
        raise DDLSecurityError("Nome da tabela deve começar com letra e conter apenas letras, números e underscore")
    
    # Evita nomes reservados perigosos
    dangerous_names = ['admin', 'root', 'sys', 'system', 'master', 'information_schema']
    if table_name.lower() in dangerous_names:
        raise DDLSecurityError(f"Nome de tabela '{table_name}' não é permitido por segurança")


def _validate_column_name(column_name: str) -> None:
    """Valida nome de coluna."""
    if not column_name or not isinstance(column_name, str):
        raise DDLSecurityError("Nome da coluna é obrigatório")
    
    # Apenas caracteres alfanuméricos e underscore
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', column_name):
        raise DDLSecurityError("Nome da coluna deve começar com letra e conter apenas letras, números e underscore")


def _validate_column_type(column_type: str) -> None:
    """Valida tipo de coluna."""
    if not column_type or not isinstance(column_type, str):
        raise DDLSecurityError("Tipo da coluna é obrigatório")
    
    # Lista de tipos permitidos (pode ser expandida)
    allowed_types_patterns = [
        r'^INT(\(\d+\))?$',
        r'^VARCHAR\(\d+\)$',
        r'^CHAR\(\d+\)$',
        r'^TEXT$',
        r'^DECIMAL\(\d+,\d+\)$',
        r'^FLOAT(\(\d+,\d+\))?$',
        r'^DOUBLE(\(\d+,\d+\))?$',
        r'^DATE$',
        r'^DATETIME$',
        r'^TIMESTAMP$',
        r'^BOOLEAN$',
        r'^BOOL$',
        r'^TINYINT(\(\d+\))?$',
        r'^BIGINT(\(\d+\))?$',
        r'^MEDIUMTEXT$',
        r'^LONGTEXT$'
    ]
    
    column_type_upper = column_type.upper()
    if not any(re.match(pattern, column_type_upper) for pattern in allowed_types_patterns):
        raise DDLSecurityError(f"Tipo de coluna não permitido: {column_type}")


def _validate_column_constraints(constraints: List[str]) -> None:
    """Valida constraints de coluna."""
    if not isinstance(constraints, list):
        raise DDLSecurityError("Constraints devem ser uma lista")
    
    allowed_constraints = [
        'NOT NULL', 'NULL', 'PRIMARY KEY', 'UNIQUE', 'AUTO_INCREMENT', 
        'DEFAULT', 'CHECK', 'FOREIGN KEY', 'INDEX'
    ]
    
    for constraint in constraints:
        if not any(constraint.upper().startswith(allowed) for allowed in allowed_constraints):
            raise DDLSecurityError(f"Constraint não permitida: {constraint}")


def _generate_create_table_sql(db_type: str, table_name: str, columns: List[Dict], options: Dict) -> str:
    """Gera SQL seguro para criação de tabela."""
    # Escapar nome da tabela
    escaped_table = _escape_identifier(table_name, db_type)
    
    # Construir colunas
    column_definitions = []
    for col in columns:
        col_def = f"{_escape_identifier(col['name'], db_type)} {col['type']}"
        
        if "constraints" in col:
            col_def += " " + " ".join(col["constraints"])
        
        column_definitions.append(col_def)
    
    # Construir SQL base
    sql = f"CREATE TABLE"
    
    if options.get("if_not_exists"):
        sql += " IF NOT EXISTS"
    
    sql += f" {escaped_table} (\n  " + ",\n  ".join(column_definitions) + "\n)"
    
    # Opções específicas por banco
    if db_type.lower() == "mysql":
        if options.get("engine"):
            sql += f" ENGINE={options['engine']}"
        if options.get("charset"):
            sql += f" CHARACTER SET {options['charset']}"
    
    return sql


def _generate_alter_table_sql(db_type: str, table_name: str, operation: str, column_spec: Dict) -> str:
    """Gera SQL seguro para alteração de tabela."""
    escaped_table = _escape_identifier(table_name, db_type)
    escaped_column = _escape_identifier(column_spec["name"], db_type)
    
    sql = f"ALTER TABLE {escaped_table}"
    
    if operation == "ADD_COLUMN":
        sql += f" ADD COLUMN {escaped_column} {column_spec['type']}"
        if "constraints" in column_spec:
            sql += " " + " ".join(column_spec["constraints"])
        if "position" in column_spec and db_type.lower() == "mysql":
            sql += f" {column_spec['position']}"
    
    elif operation == "DROP_COLUMN":
        sql += f" DROP COLUMN {escaped_column}"
    
    elif operation == "MODIFY_COLUMN":
        if db_type.lower() == "mysql":
            sql += f" MODIFY COLUMN {escaped_column} {column_spec['type']}"
        else:
            sql += f" ALTER COLUMN {escaped_column} TYPE {column_spec['type']}"
    
    elif operation == "RENAME_COLUMN":
        new_name = _escape_identifier(column_spec.get("new_name", ""), db_type)
        if db_type.lower() == "mysql":
            sql += f" CHANGE COLUMN {escaped_column} {new_name} {column_spec['type']}"
        else:
            sql += f" RENAME COLUMN {escaped_column} TO {new_name}"
    
    return sql


def _generate_drop_table_sql(db_type: str, table_name: str, if_exists: bool) -> str:
    """Gera SQL seguro para remoção de tabela."""
    escaped_table = _escape_identifier(table_name, db_type)
    
    sql = "DROP TABLE"
    if if_exists:
        sql += " IF EXISTS"
    sql += f" {escaped_table}"
    
    return sql


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


def _execute_ddl_safely(db, sql: str, operation_type: str):
    """Executa DDL de forma segura sem passar pela validação de SELECT."""
    import psycopg2
    import mysql.connector
    import pyodbc
    
    try:
        if hasattr(db, '_connect'):
            conn = db._connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            
            if hasattr(conn, 'close'):
                conn.close()
            
            return {"status": "success", "operation": operation_type}
        else:
            raise Exception("Método de conexão não encontrado")
            
    except Exception as e:
        logger.error(f"Erro ao executar {operation_type}: {e}")
        raise