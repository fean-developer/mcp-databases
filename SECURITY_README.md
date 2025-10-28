# 🛡️ Sistema de Segurança SQL - MCP Databases

## ⚠️ AVISO IMPORTANTE

Este MCP implementa um **sistema de segurança rigoroso** que **NÃO PODE ser contornado**. Qualquer tentativa de executar comandos perigosos será automaticamente bloqueada.

## 🔒 Proteções Implementadas

### ❌ Comandos COMPLETAMENTE BLOQUEADOS:
- `DELETE` - Exclusão de dados
- `DROP` - Remoção de estruturas
- `TRUNCATE` - Limpeza de tabelas
- `ALTER` - Modificação de estruturas
- `CREATE` - Criação de estruturas
- `EXEC` / `EXECUTE` - Execução de procedimentos
- `INSERT` - Inserção de dados (use `insert_record` tool)
- `UPDATE` - Atualização de dados
- `MERGE` - Combinação de dados
- `BULK` - Operações em lote
- `OPENROWSET` / `OPENDATASOURCE` - Acesso externo
- `xp_` / `sp_` - Procedimentos de sistema
- `SHUTDOWN` / `KILL` - Comandos de sistema
- `BACKUP` / `RESTORE` - Operações de backup

### 🚫 Padrões PERIGOSOS Detectados:
- SQL dinâmico (`EXEC(...)`, `sp_executesql`)
- Variáveis de sistema (`@@version`, `@@servername`)
- Comandos de sistema (`xp_cmdshell`)
- Múltiplos comandos separados por `;`
- Comandos em comentários (tentativas de bypass)

### ⚡ Comandos CONDICIONAIS (Bloqueados por precaução):
- `UNION` / `UNION ALL` - Pode ser usado para SQL injection
- `INTERSECT` / `EXCEPT` - Pode expor dados sensíveis

### ✅ Comandos PERMITIDOS:
- `SELECT` - Consultas de leitura
- `WITH` - Common Table Expressions (CTEs)

## 🛡️ Arquitetura de Segurança Multi-Camadas

### 1. **Camada da Tool** (`execute_query`)
- Primeira validação antes da execução
- Retorna erro estruturado se query for insegura
- Log detalhado de tentativas bloqueadas

### 2. **Camada do Banco de Dados** (PostgreSQL, MySQL, MSSQL)
- Segunda validação na classe de banco
- Proteção redundante caso a primeira camada falhe
- Exceções específicas por tipo de banco

### 3. **Camada do Prompt** (`safe_query_prompt`)
- Análise de segurança com relatório detalhado
- Educação sobre riscos e boas práticas
- Validação programática integrada

## 📊 Tools de Segurança

### `security_check`
Verifica a segurança de uma query sem executá-la:
```python
security_check({"query": "SELECT * FROM users"})
```

### `get_security_config`
Retorna a configuração atual de segurança:
```python
get_security_config({})
```

## ⚙️ Como Usar Operações Seguras

### ✅ Para CONSULTAS (permitidas):
```sql
-- ✅ PERMITIDO
SELECT * FROM users WHERE active = 1;
SELECT COUNT(*) FROM orders;
WITH total_sales AS (SELECT SUM(amount) as total FROM sales) 
SELECT * FROM total_sales;
```

### ✅ Para INSERÇÕES (use a tool específica):
```python
# ✅ PERMITIDO - Use insert_record tool
insert_record({
    "db_type": "postgres",
    "conn_params": {...},
    "table": "users",
    "data": {"name": "João", "email": "joao@email.com"}
})
```

### ❌ Para MODIFICAÇÕES/EXCLUSÕES:
```sql
-- ❌ BLOQUEADO - Use ferramentas específicas ou acesso direto ao banco
DELETE FROM users WHERE id = 1;
UPDATE users SET status = 'inactive';
DROP TABLE old_table;
```

## 🔥 Tentativas de Bypass (TODAS BLOQUEADAS)

```sql
-- ❌ Múltiplos comandos
SELECT * FROM users; DROP TABLE users; --

-- ❌ Comentários maliciosos
SELECT * FROM users /* DROP TABLE users */

-- ❌ Case insensitive
delete from users where id = 1

-- ❌ SQL injection
SELECT * FROM users WHERE id = '1'; DELETE FROM users; --

-- ❌ UNION para bypass
SELECT name FROM users UNION SELECT password FROM admin

-- ❌ Variáveis de sistema
SELECT @@version

-- ❌ Comandos de sistema
EXEC xp_cmdshell 'dir'
```

## 🧪 Teste de Segurança

Execute o teste de segurança para verificar se todas as proteções estão funcionando:

```bash
python3 test_security.py
```

## 📋 Logs de Segurança

Todas as tentativas de execução são logadas:
- ✅ Queries seguras: Log de sucesso
- ❌ Queries perigosas: Log de erro com detalhes
- 🔍 Análises de segurança: Log informativo

## 🚨 Mensagens de Erro Comuns

### `COMANDO PERIGOSO DETECTADO`
Comando SQL perigoso foi identificado e bloqueado.

### `PADRÃO PERIGOSO DETECTADO`
SQL dinâmico ou padrão suspeito foi identificado.

### `COMANDOS CONDICIONAIS DETECTADOS`
UNION ou similar foi bloqueado por precaução.

### `COMANDO NÃO PERMITIDO`
Comando não está na whitelist de comandos permitidos.

## 🛠️ Para Desenvolvedores

### Modificar Configurações de Segurança

As configurações estão em `mcp_databases/security.py`:

```python
# Comandos perigosos (sempre bloqueados)
DANGEROUS_COMMANDS = {'DELETE', 'DROP', 'TRUNCATE', ...}

# Comandos permitidos (whitelist)
ALLOWED_COMMANDS = {'SELECT', 'WITH'}

# Comandos condicionais (bloqueados por precaução)
CONDITIONAL_COMMANDS = {'UNION', 'INTERSECT', 'EXCEPT'}
```

### Adicionar Novos Padrões Perigosos

```python
DANGEROUS_PATTERNS = [
    r'\bEXEC\s*\(',           # EXEC(
    r'@@\w+',                 # @@version
    # ... adicione novos padrões aqui
]
```

## ⚖️ Filosofia de Segurança

> **"Segurança por Design, Não por Acidente"**

1. **Negação por Padrão**: Tudo é bloqueado até ser explicitamente permitido
2. **Defesa em Profundidade**: Múltiplas camadas de proteção
3. **Princípio do Menor Privilégio**: Apenas operações de leitura são permitidas
4. **Transparência**: Logs detalhados de todas as operações
5. **Imutabilidade**: Configurações de segurança não podem ser contornadas

---

🔒 **Lembre-se**: Este sistema foi projetado para proteger seus dados. As restrições existem por uma boa razão!