# 🛠️ Guia de Uso das Ferramentas Seguras - MCP Databases

## 📋 Visão Geral

O MCP Databases agora oferece ferramentas específicas para operações DDL e DML com **proteção total contra SQL injection**. Cada ferramenta implementa validações rigorosas e usa parâmetros seguros.

## 🏗️ Operações DDL (Data Definition Language)

### ✅ Criar Tabela (`create_table`)

```python
# Exemplo básico
create_table({
    "db_type": "postgres",
    "conn_params": {}, # Busca do .env automaticamente
    "table_name": "usuarios",
    "columns": [
        {
            "name": "id",
            "type": "INT",
            "constraints": ["PRIMARY KEY", "AUTO_INCREMENT"]
        },
        {
            "name": "nome",
            "type": "VARCHAR(255)",
            "constraints": ["NOT NULL"]
        },
        {
            "name": "email",
            "type": "VARCHAR(255)",
            "constraints": ["UNIQUE", "NOT NULL"]
        },
        {
            "name": "data_criacao",
            "type": "TIMESTAMP",
            "constraints": ["DEFAULT CURRENT_TIMESTAMP"]
        }
    ],
    "options": {
        "if_not_exists": True,
        "engine": "InnoDB",    # MySQL específico
        "charset": "utf8mb4"   # MySQL específico
    }
})
```

**Resultado esperado:**
```json
{
    "success": true,
    "message": "Tabela 'usuarios' criada com sucesso",
    "table_name": "usuarios",
    "sql_executed": "CREATE TABLE IF NOT EXISTS `usuarios` (...)",
    "columns_created": 4
}
```

### ✏️ Alterar Tabela (`alter_table`)

```python
# Adicionar coluna
alter_table({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "operation": "ADD_COLUMN",
    "column_spec": {
        "name": "telefone",
        "type": "VARCHAR(20)",
        "constraints": ["NULL"],
        "position": "AFTER email"  # MySQL específico
    }
})

# Modificar coluna
alter_table({
    "db_type": "postgres", 
    "conn_params": {},
    "table_name": "usuarios",
    "operation": "MODIFY_COLUMN",
    "column_spec": {
        "name": "nome",
        "type": "VARCHAR(500)"
    }
})

# Remover coluna
alter_table({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios", 
    "operation": "DROP_COLUMN",
    "column_spec": {
        "name": "telefone"
    }
})
```

### 🗑️ Remover Tabela (`drop_table`) - **CUIDADO!**

```python
# Confirmação dupla obrigatória
drop_table({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "tabela_temporaria",
    "confirmation": "DELETE_TABLE_tabela_temporaria", # Exato!
    "if_exists": True
})
```

## 📝 Operações DML (Data Manipulation Language)

### 🔄 Atualizar Registros (`update_records`)

```python
# Atualização segura com parâmetros
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "nome": "João Silva Santos",
        "email": "joao.santos@empresa.com",
        "data_atualizacao": "2025-10-28 10:30:00"
    },
    "where_conditions": {
        "id": 123,
        "status": "ativo"
    },
    "safety_limit": 1  # Máximo de registros afetados
})
```

**Proteções implementadas:**
- ✅ Parâmetros seguros (previne SQL injection)
- ✅ Validação de nomes de colunas
- ✅ Detecção de padrões maliciosos
- ✅ Limite de segurança (quantos registros podem ser afetados)
- ✅ Verificação prévia da quantidade de registros

### 🗑️ Excluir Registros (`delete_records`) - **CUIDADO!**

```python
# Exclusão com confirmação dupla
delete_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "where_conditions": {
        "id": 456,
        "status": "inativo"
    },
    "confirmation": "DELETE_FROM_usuarios_WHERE_id_456",
    "safety_limit": 5  # Máximo de registros que podem ser excluídos
})
```

### 📦 Inserção em Lote (`bulk_insert`)

```python
# Inserção eficiente de múltiplos registros
bulk_insert({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "records": [
        {
            "nome": "Maria Silva",
            "email": "maria@empresa.com",
            "departamento": "TI"
        },
        {
            "nome": "Pedro Santos", 
            "email": "pedro@empresa.com",
            "departamento": "RH"
        },
        {
            "nome": "Ana Costa",
            "email": "ana@empresa.com", 
            "departamento": "Financeiro"
        }
    ],
    "batch_size": 100  # Tamanho do lote
})
```

**Proteções implementadas:**
- ✅ Todos os registros têm a mesma estrutura
- ✅ Validação contra SQL injection em todos os valores
- ✅ Limite máximo de 10.000 registros por operação
- ✅ Processamento em lotes para eficiência

## 🔍 Ferramentas de Segurança

### 🛡️ Verificar Segurança (`security_check`)

```python
# Analisa uma query sem executá-la
security_check({
    "query": "SELECT * FROM usuarios WHERE nome = 'João'"
})
```

**Resultado:**
```json
{
    "is_safe": true,
    "message": "Query validada com sucesso - segura para execução",
    "first_command": "SELECT",
    "dangerous_commands": [],
    "dangerous_patterns": [],
    "modification_commands": [],
    "cleaned_query": "SELECT * FROM usuarios WHERE nome = 'João'",
    "original_query": "SELECT * FROM usuarios WHERE nome = 'João'"
}
```

### ⚙️ Configuração de Segurança (`get_security_config`)

```python
get_security_config({})
```

**Resultado:**
```json
{
    "dangerous_commands_blocked": ["DELETE", "DROP", "EXEC", "..."],
    "allowed_commands": ["SELECT", "WITH"],
    "total_dangerous_patterns": 15,
    "security_level": "MÁXIMO",
    "modifications_allowed": false,
    "multilayer_protection": {
        "tool_level": true,
        "database_level": true,
        "prompt_level": true
    }
}
```

## ❌ Tentativas Bloqueadas (Exemplos)

### 🚫 SQL Injection Bloqueado:
```python
# ❌ ISSO SERÁ BLOQUEADO
update_records({
    "table_name": "usuarios",
    "set_values": {
        "nome": "'; DROP TABLE usuarios; --"  # SQL injection
    },
    "where_conditions": {"id": 1}
})
# Erro: "Valor suspeito detectado: possível SQL injection"
```

### 🚫 Nome Malicioso Bloqueado:
```python
# ❌ ISSO SERÁ BLOQUEADO
create_table({
    "table_name": "usuarios; DROP TABLE admin; --",  # Nome malicioso
    "columns": [...]
})
# Erro: "Nome da tabela deve começar com letra e conter apenas letras, números e underscore"
```

### 🚫 Operação Sem Confirmação Bloqueada:
```python
# ❌ ISSO SERÁ BLOQUEADO
delete_records({
    "table_name": "usuarios",
    "where_conditions": {"status": "inativo"},
    "confirmation": "confirmo"  # Confirmação incorreta
})
# Erro: "Confirmação de segurança incorreta"
```

## 🎯 Melhores Práticas

### ✅ DO (Faça):
- Use sempre nomes válidos (letras, números, underscore)
- Forneça confirmações exatas para operações destrutivas
- Configure limites de segurança apropriados
- Teste com `security_check` antes de executar
- Use parâmetros em vez de concatenar strings

### ❌ DON'T (Não faça):
- Nunca tente contornar as validações de segurança
- Não use caracteres especiais em nomes de tabelas/colunas
- Não coloque SQL dinâmico nos valores
- Não ignore os avisos de segurança
- Não use confirmações genéricas para operações destrutivas

## 🔧 Configuração de Limites

```python
# Aumente limites apenas se necessário
update_records({
    # ... outros parâmetros ...
    "safety_limit": 5000  # Máximo de registros afetados
})

delete_records({
    # ... outros parâmetros ...
    "safety_limit": 100   # Limite conservador para DELETE
})

bulk_insert({
    # ... outros parâmetros ...
    "batch_size": 500     # Tamanho do lote
})
```

## 🚨 Mensagens de Erro Comuns

| Erro | Significado | Solução |
|------|-------------|---------|
| `Valor suspeito detectado: possível SQL injection` | Valor contém padrões de SQL injection | Use valores limpos, sem comandos SQL |
| `Nome da tabela deve começar com letra` | Nome de tabela inválido | Use apenas letras, números e underscore |
| `Confirmação de segurança incorreta` | Confirmação para DELETE/DROP incorreta | Use a confirmação exata solicitada |
| `Operação cancelada: X registros seriam afetados` | Muitos registros afetados | Aumente safety_limit ou refine WHERE |
| `Tipo de coluna não permitido` | Tipo de dados não está na whitelist | Use tipos padrão (INT, VARCHAR, etc.) |

---

🛡️ **Lembre-se**: Todas essas ferramentas implementam **proteção automática contra SQL injection** e **não podem ser contornadas**. A segurança é garantida em múltiplas camadas!