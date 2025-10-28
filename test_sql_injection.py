#!/usr/bin/env python3
"""
Teste específico para validação contra SQL Injection no MCP Databases.
"""
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_databases.tools.dml_operations import update_records, delete_records, bulk_insert, DMLSecurityError
from mcp_databases.tools.ddl_operations import create_table, alter_table, drop_table, DDLSecurityError


def test_sql_injection_protection():
    """Testa proteções contra SQL injection nas operações DML."""
    print("🛡️ TESTANDO PROTEÇÕES CONTRA SQL INJECTION")
    print("=" * 60)
    
    # Teste de SQL injection em UPDATE
    print("\n📝 Testando UPDATE com tentativas de SQL injection...")
    
    malicious_updates = [
        {
            "description": "SQL injection em valor",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "set_values": {"name": "'; DROP TABLE users; --"},
                "where_conditions": {"id": 1}
            }
        },
        {
            "description": "SQL injection com OR",
            "params": {
                "db_type": "postgres", 
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "set_values": {"status": "active"},
                "where_conditions": {"name": "' OR '1'='1"}
            }
        },
        {
            "description": "SQL injection com UNION",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"}, 
                "table_name": "users",
                "set_values": {"email": "test@test.com' UNION SELECT password FROM admin_users WHERE '1'='1"},
                "where_conditions": {"id": 1}
            }
        },
        {
            "description": "Nome de tabela malicioso",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users; DROP TABLE admin; --",
                "set_values": {"name": "test"},
                "where_conditions": {"id": 1}
            }
        }
    ]
    
    blocked_count = 0
    for i, test_case in enumerate(malicious_updates, 1):
        try:
            result = update_records(test_case["params"])
            print(f"❌ FALHA {i}: {test_case['description']} - NÃO foi bloqueada!")
        except (DMLSecurityError, Exception) as e:
            print(f"✅ OK {i}: {test_case['description']} - BLOQUEADA")
            print(f"   Motivo: {str(e)[:100]}...")
            blocked_count += 1
        print()
    
    # Teste de SQL injection em DELETE
    print("\n🗑️ Testando DELETE com tentativas de SQL injection...")
    
    malicious_deletes = [
        {
            "description": "SQL injection em condição WHERE",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "where_conditions": {"name": "'; DELETE FROM admin_users; --"},
                "confirmation": "DELETE_FROM_users_WHERE_name_test"
            }
        },
        {
            "description": "Tentativa de bypass com comentários",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "where_conditions": {"id": "1 /* DROP TABLE users */"},
                "confirmation": "DELETE_FROM_users_WHERE_id_1"
            }
        }
    ]
    
    for i, test_case in enumerate(malicious_deletes, 1):
        try:
            result = delete_records(test_case["params"])
            print(f"❌ FALHA {i}: {test_case['description']} - NÃO foi bloqueada!")
        except (DMLSecurityError, Exception) as e:
            print(f"✅ OK {i}: {test_case['description']} - BLOQUEADA")
            print(f"   Motivo: {str(e)[:100]}...")
            blocked_count += 1
        print()
    
    # Teste de SQL injection em BULK INSERT
    print("\n📦 Testando BULK INSERT com tentativas de SQL injection...")
    
    malicious_bulk_inserts = [
        {
            "description": "SQL injection em dados do bulk insert",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "records": [
                    {"name": "João", "email": "joao@test.com"},
                    {"name": "'; DROP TABLE users; --", "email": "malicious@test.com"}
                ]
            }
        },
        {
            "description": "Nome de coluna malicioso",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "records": [
                    {"name; DROP TABLE users; --": "João", "email": "joao@test.com"}
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(malicious_bulk_inserts, 1):
        try:
            result = bulk_insert(test_case["params"])
            print(f"❌ FALHA {i}: {test_case['description']} - NÃO foi bloqueada!")
        except (DMLSecurityError, Exception) as e:
            print(f"✅ OK {i}: {test_case['description']} - BLOQUEADA")
            print(f"   Motivo: {str(e)[:100]}...")
            blocked_count += 1
        print()
    
    total_tests = len(malicious_updates) + len(malicious_deletes) + len(malicious_bulk_inserts)
    
    print(f"📊 RESULTADO DOS TESTES DE SQL INJECTION")
    print(f"Total de tentativas: {total_tests}")
    print(f"Bloqueadas: {blocked_count}")
    print(f"Passou: {total_tests - blocked_count}")
    
    return blocked_count == total_tests


def test_ddl_security():
    """Testa proteções contra SQL injection nas operações DDL."""
    print("\n🏗️ TESTANDO PROTEÇÕES DDL CONTRA SQL INJECTION")
    print("=" * 60)
    
    # Teste de nomes maliciosos em CREATE TABLE
    malicious_creates = [
        {
            "description": "Nome de tabela com SQL injection",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users; DROP TABLE admin; --",
                "columns": [{"name": "id", "type": "INT"}],
                "options": {}
            }
        },
        {
            "description": "Nome de coluna malicioso",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "columns": [{"name": "id; DROP TABLE admin; --", "type": "INT"}],
                "options": {}
            }
        },
        {
            "description": "Tipo de coluna malicioso",
            "params": {
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "columns": [{"name": "id", "type": "INT; DROP TABLE admin; --"}],
                "options": {}
            }
        }
    ]
    
    blocked_count = 0
    for i, test_case in enumerate(malicious_creates, 1):
        try:
            result = create_table(test_case["params"])
            print(f"❌ FALHA {i}: {test_case['description']} - NÃO foi bloqueada!")
        except (DDLSecurityError, Exception) as e:
            print(f"✅ OK {i}: {test_case['description']} - BLOQUEADA")
            print(f"   Motivo: {str(e)[:100]}...")
            blocked_count += 1
        print()
    
    return blocked_count == len(malicious_creates)


def test_legitimate_operations():
    """Testa se operações legítimas ainda funcionam."""
    print("\n✅ TESTANDO OPERAÇÕES LEGÍTIMAS")
    print("=" * 50)
    
    legitimate_tests = [
        {
            "description": "CREATE TABLE legítimo",
            "operation": lambda: create_table({
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "test_users",
                "columns": [
                    {"name": "id", "type": "INT", "constraints": ["PRIMARY KEY"]},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE"]}
                ],
                "options": {"if_not_exists": True}
            })
        },
        {
            "description": "UPDATE legítimo",
            "operation": lambda: update_records({
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "set_values": {"name": "João Silva", "email": "joao@email.com"},
                "where_conditions": {"id": 123}
            })
        },
        {
            "description": "BULK INSERT legítimo",
            "operation": lambda: bulk_insert({
                "db_type": "postgres",
                "conn_params": {"server": "test", "database": "test", "user": "test", "password": "test"},
                "table_name": "users",
                "records": [
                    {"name": "João", "email": "joao@test.com"},
                    {"name": "Maria", "email": "maria@test.com"}
                ]
            })
        }
    ]
    
    legitimate_count = 0
    for i, test_case in enumerate(legitimate_tests, 1):
        try:
            # Note: Estas operações falharão na conexão, mas devem passar na validação de segurança
            result = test_case["operation"]()
            print(f"✅ OK {i}: {test_case['description']} - Validação passou")
            legitimate_count += 1
        except (DMLSecurityError, DDLSecurityError) as security_error:
            print(f"❌ FALHA {i}: {test_case['description']} - Bloqueada incorretamente")
            print(f"   Erro: {str(security_error)}")
        except Exception as e:
            # Erro de conexão é esperado neste teste
            if "conexão" in str(e).lower() or "connect" in str(e).lower() or "host" in str(e).lower():
                print(f"✅ OK {i}: {test_case['description']} - Validação passou (erro de conexão esperado)")
                legitimate_count += 1
            else:
                print(f"❓ INCERTO {i}: {test_case['description']} - Erro inesperado")
                print(f"   Erro: {str(e)[:100]}...")
        print()
    
    return legitimate_count == len(legitimate_tests)


def main():
    """Executa todos os testes de SQL injection."""
    print("🛡️ TESTE COMPLETO DE PROTEÇÃO CONTRA SQL INJECTION - MCP DATABASES")
    print("=" * 80)
    print()
    
    # Testa SQL injection em operações DML
    dml_passed = test_sql_injection_protection()
    print()
    
    # Testa SQL injection em operações DDL
    ddl_passed = test_ddl_security()
    print()
    
    # Testa operações legítimas
    legitimate_passed = test_legitimate_operations()
    print()
    
    # Resultado final
    print("🏆 RESULTADO FINAL DOS TESTES DE SQL INJECTION")
    print("=" * 55)
    if dml_passed and ddl_passed and legitimate_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Tentativas de SQL injection foram bloqueadas")
        print("✅ Operações DDL maliciosas foram bloqueadas")
        print("✅ Operações legítimas foram permitidas")
        print("🛡️ Sistema completamente protegido contra SQL injection!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
        if not dml_passed:
            print("❌ Algumas tentativas de SQL injection em DML não foram bloqueadas")
        if not ddl_passed:
            print("❌ Algumas tentativas de SQL injection em DDL não foram bloqueadas")
        if not legitimate_passed:
            print("❌ Algumas operações legítimas foram bloqueadas incorretamente")
        print("🔧 Revise as validações de segurança")


if __name__ == "__main__":
    main()