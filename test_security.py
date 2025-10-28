#!/usr/bin/env python3
"""
Script de teste para validar o sistema de segurança SQL do MCP Databases.
"""
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_databases.security import SQLSecurityValidator, validate_sql_security, SQLSecurityError

def test_dangerous_queries():
    """Testa queries perigosas que devem ser bloqueadas."""
    dangerous_queries = [
        "DROP TABLE users",
        "DELETE FROM users WHERE id = 1",
        "TRUNCATE TABLE logs",
        "EXEC xp_cmdshell 'dir'",
        "EXECUTE sp_configure 'xp_cmdshell', 1",
        "ALTER TABLE users ADD COLUMN password VARCHAR(255)",
        "CREATE TABLE hackers (id INT)",
        "INSERT INTO users VALUES (1, 'hacker')",
        "UPDATE users SET password = 'hacked' WHERE id = 1",
        "SELECT * FROM users; DROP TABLE users; --",
        "SELECT * FROM users UNION ALL SELECT * FROM passwords",
        "SELECT @@version",
        "BULK INSERT users FROM 'file.txt'",
        "OPENROWSET('SQLNCLI', 'server=.;uid=sa;pwd=;', 'SELECT * FROM master.sys.tables')"
    ]
    
    print("🧪 TESTANDO QUERIES PERIGOSAS (devem ser BLOQUEADAS)")
    print("=" * 60)
    
    all_blocked = True
    for i, query in enumerate(dangerous_queries, 1):
        try:
            is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications=False)
            if is_safe:
                print(f"❌ FALHA {i}: Query perigosa passou na validação!")
                print(f"   Query: {query}")
                print(f"   Mensagem: {message}")
                all_blocked = False
            else:
                print(f"✅ OK {i}: Query bloqueada corretamente")
                print(f"   Query: {query[:50]}...")
                print(f"   Motivo: {message[:100]}...")
        except Exception as e:
            print(f"✅ OK {i}: Query bloqueada com exceção")
            print(f"   Query: {query[:50]}...")
            print(f"   Erro: {str(e)[:100]}...")
        print()
    
    return all_blocked

def test_safe_queries():
    """Testa queries seguras que devem ser permitidas."""
    safe_queries = [
        "SELECT * FROM users",
        "SELECT id, name FROM users WHERE active = 1",
        "SELECT COUNT(*) FROM orders WHERE date > '2023-01-01'",
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
        "SELECT DISTINCT category FROM products ORDER BY category",
        "WITH total_sales AS (SELECT SUM(amount) as total FROM sales) SELECT * FROM total_sales",
        "SELECT * FROM users WHERE name LIKE '%admin%' AND status = 'active'"
    ]
    
    print("🧪 TESTANDO QUERIES SEGURAS (devem ser PERMITIDAS)")
    print("=" * 60)
    
    all_passed = True
    for i, query in enumerate(safe_queries, 1):
        try:
            is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications=False)
            if is_safe:
                print(f"✅ OK {i}: Query segura permitida")
                print(f"   Query: {query}")
                print(f"   Mensagem: {message}")
            else:
                print(f"❌ FALHA {i}: Query segura foi bloqueada!")
                print(f"   Query: {query}")
                print(f"   Motivo: {message}")
                all_passed = False
        except Exception as e:
            print(f"❌ FALHA {i}: Query segura gerou exceção")
            print(f"   Query: {query}")
            print(f"   Erro: {str(e)}")
            all_passed = False
        print()
    
    return all_passed

def test_edge_cases():
    """Testa casos especiais e tentativas de contorno."""
    edge_cases = [
        ("Query vazia", ""),
        ("Apenas espaços", "   "),
        ("Comentário com comando perigoso", "-- DROP TABLE users\nSELECT * FROM users"),
        ("Comentário de bloco", "/* DELETE FROM users */ SELECT * FROM users"),
        ("Case insensitive", "select * from users"),
        ("Case mixed", "SeLeCt * FrOm UsErS"),
        ("SQL injection tentative", "SELECT * FROM users WHERE id = '1'; DROP TABLE users; --"),
        ("Union com comando perigoso", "SELECT name FROM users UNION SELECT 'test'; DELETE FROM users; --")
    ]
    
    print("🧪 TESTANDO CASOS ESPECIAIS")
    print("=" * 60)
    
    for description, query in edge_cases:
        try:
            is_safe, message = SQLSecurityValidator.validate_query(query, allow_modifications=False)
            status = "✅ PERMITIDA" if is_safe else "🚫 BLOQUEADA"
            print(f"{status} - {description}")
            print(f"   Query: {repr(query)}")
            print(f"   Resultado: {message[:100]}...")
        except Exception as e:
            print(f"🚫 BLOQUEADA - {description}")
            print(f"   Query: {repr(query)}")
            print(f"   Erro: {str(e)[:100]}...")
        print()

def main():
    """Executa todos os testes."""
    print("🔒 TESTE DO SISTEMA DE SEGURANÇA SQL - MCP DATABASES")
    print("=" * 70)
    print()
    
    # Testa queries perigosas
    dangerous_blocked = test_dangerous_queries()
    print()
    
    # Testa queries seguras
    safe_passed = test_safe_queries()
    print()
    
    # Testa casos especiais
    test_edge_cases()
    print()
    
    # Resultado final
    print("📊 RESULTADO FINAL")
    print("=" * 30)
    if dangerous_blocked and safe_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Queries perigosas foram bloqueadas corretamente")
        print("✅ Queries seguras foram permitidas corretamente")
        print("🛡️ Sistema de segurança funcionando perfeitamente!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        if not dangerous_blocked:
            print("❌ Algumas queries perigosas não foram bloqueadas")
        if not safe_passed:
            print("❌ Algumas queries seguras foram bloqueadas incorretamente")
        print("🔧 Revise a configuração de segurança")

if __name__ == "__main__":
    main()