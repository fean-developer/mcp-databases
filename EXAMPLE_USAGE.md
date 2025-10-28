# 🚀 Exemplo Prático - Sistema de Usuários

## 📋 Cenário
Vamos criar um sistema completo de usuários usando as ferramentas seguras do MCP Databases.

## 🏗️ 1. Criando a Tabela Principal

```python
# Criar tabela de usuários
create_table({
    "db_type": "postgres",
    "conn_params": {},  # Busca automaticamente do .env
    "table_name": "usuarios",
    "columns": [
        {
            "name": "id",
            "type": "SERIAL",
            "constraints": ["PRIMARY KEY"]
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
            "name": "departamento",
            "type": "VARCHAR(100)"
        },
        {
            "name": "status",
            "type": "VARCHAR(20)",
            "constraints": ["DEFAULT 'ativo'"]
        },
        {
            "name": "data_criacao",
            "type": "TIMESTAMP",
            "constraints": ["DEFAULT CURRENT_TIMESTAMP"]
        },
        {
            "name": "salario",
            "type": "DECIMAL(10,2)"
        }
    ],
    "options": {
        "if_not_exists": True
    }
})
```

**Resposta esperada:**
```json
{
    "success": true,
    "message": "Tabela 'usuarios' criada com sucesso",
    "table_name": "usuarios",
    "sql_executed": "CREATE TABLE IF NOT EXISTS usuarios (...)",
    "columns_created": 7
}
```

## 📝 2. Adicionando Dados de Teste

```python
# Inserir múltiplos usuários de uma vez
bulk_insert({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "records": [
        {
            "nome": "Maria Silva",
            "email": "maria.silva@empresa.com",
            "departamento": "TI",
            "status": "ativo",
            "salario": 5500.00
        },
        {
            "nome": "João Santos",
            "email": "joao.santos@empresa.com", 
            "departamento": "RH",
            "status": "ativo",
            "salario": 4800.00
        },
        {
            "nome": "Ana Costa",
            "email": "ana.costa@empresa.com",
            "departamento": "Financeiro", 
            "status": "ativo",
            "salario": 6200.00
        },
        {
            "nome": "Pedro Lima",
            "email": "pedro.lima@empresa.com",
            "departamento": "TI",
            "status": "inativo",
            "salario": 5200.00
        }
    ],
    "batch_size": 100
})
```

**Resposta esperada:**
```json
{
    "success": true,
    "message": "4 registros inseridos com sucesso na tabela 'usuarios'",
    "records_inserted": 4,
    "table_name": "usuarios",
    "batch_size": 100,
    "total_batches": 1
}
```

## 🔄 3. Atualizações Seguras

### Promoção de Salário
```python
# Aumentar salário do João
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "salario": 5300.00
    },
    "where_conditions": {
        "email": "joao.santos@empresa.com"
    },
    "safety_limit": 1
})
```

### Mudança de Departamento
```python
# Transferir Ana para TI
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios", 
    "set_values": {
        "departamento": "TI"
    },
    "where_conditions": {
        "email": "ana.costa@empresa.com"
    },
    "safety_limit": 1
})
```

### Reativar Usuário
```python
# Reativar Pedro
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "status": "ativo"
    },
    "where_conditions": {
        "email": "pedro.lima@empresa.com",
        "status": "inativo"
    },
    "safety_limit": 1
})
```

## 🏗️ 4. Modificando a Estrutura

### Adicionar Nova Coluna
```python
# Adicionar campo telefone
alter_table({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "operation": "ADD_COLUMN",
    "column_spec": {
        "name": "telefone",
        "type": "VARCHAR(20)"
    }
})
```

### Atualizar com Telefones
```python
# Adicionar telefones usando bulk update (simulação)
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "telefone": "(11) 99999-1111"
    },
    "where_conditions": {
        "email": "maria.silva@empresa.com"
    },
    "safety_limit": 1
})

update_records({
    "db_type": "postgres", 
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "telefone": "(11) 99999-2222"
    },
    "where_conditions": {
        "email": "joao.santos@empresa.com"
    },
    "safety_limit": 1
})
```

## 🗑️ 5. Limpeza de Dados

### Remover Usuário Específico
```python
# Remover usuário inativo (com confirmação dupla)
delete_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "where_conditions": {
        "email": "usuario.antigo@empresa.com",
        "status": "inativo"
    },
    "confirmation": "DELETE_FROM_usuarios_WHERE_email_usuario.antigo@empresa.com",
    "safety_limit": 1
})
```

## 🔍 6. Verificações de Segurança

### Testar Query Antes de Executar
```python
# Verificar se uma query é segura
security_check({
    "query": "SELECT nome, email, departamento FROM usuarios WHERE status = 'ativo'"
})
```

**Resposta:**
```json
{
    "is_safe": true,
    "message": "Query validada com sucesso - segura para execução",
    "first_command": "SELECT",
    "dangerous_commands": [],
    "dangerous_patterns": [],
    "modification_commands": []
}
```

### Verificar Configuração de Segurança
```python
# Ver configurações ativas de segurança
get_security_config({})
```

## ⚠️ 7. Exemplos de Tentativas Bloqueadas

### ❌ Tentativa de SQL Injection
```python
# ISSO SERÁ BLOQUEADO!
update_records({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "usuarios",
    "set_values": {
        "nome": "Hacker'; DROP TABLE usuarios; --"  # SQL injection
    },
    "where_conditions": {
        "id": 1
    }
})
```

**Erro esperado:**
```
❌ OPERAÇÃO BLOQUEADA: Valor suspeito detectado: possível SQL injection
Padrão perigoso encontrado: DROP
```

### ❌ Tentativa de Bypass
```python
# ISSO SERÁ BLOQUEADO!
create_table({
    "db_type": "postgres",
    "conn_params": {},
    "table_name": "temp; DROP TABLE usuarios; --",  # Nome malicioso
    "columns": [{"name": "id", "type": "INT"}]
})
```

**Erro esperado:**
```
❌ OPERAÇÃO BLOQUEADA: Nome da tabela deve começar com letra e conter apenas letras, números e underscore
```

## 📊 8. Consultas de Dados

```python
# Listar todos os usuários ativos
execute_query({
    "db_type": "postgres",
    "conn_params": {},
    "query": "SELECT id, nome, email, departamento, salario FROM usuarios WHERE status = 'ativo' ORDER BY nome"
})

# Estatísticas por departamento
execute_query({
    "db_type": "postgres",
    "conn_params": {},
    "query": "SELECT departamento, COUNT(*) as total_usuarios, AVG(salario) as salario_medio FROM usuarios WHERE status = 'ativo' GROUP BY departamento ORDER BY total_usuarios DESC"
})

# Usuários com salário acima da média
execute_query({
    "db_type": "postgres",
    "conn_params": {},
    "query": "SELECT nome, email, salario FROM usuarios WHERE salario > (SELECT AVG(salario) FROM usuarios WHERE status = 'ativo') AND status = 'ativo' ORDER BY salario DESC"
})
```

## 🎯 Resultados Esperados

Após executar todos esses comandos, você terá:

1. ✅ **Tabela criada** com estrutura completa
2. ✅ **4 usuários inseridos** com dados de teste
3. ✅ **Atualizações seguras** de salários e departamentos
4. ✅ **Estrutura modificada** com nova coluna telefone
5. ✅ **Dados limpos** de usuários inativos
6. ✅ **Proteção total** contra SQL injection
7. ✅ **Validações rigorosas** em todas as operações

## 🛡️ Proteções Ativadas

Durante todo o processo, as seguintes proteções estão ativas:

- 🔒 **Validação de nomes** (tabelas, colunas)
- 🔒 **Detecção de SQL injection** em todos os valores
- 🔒 **Parâmetros obrigatórios** para conexão
- 🔒 **Confirmações duplas** para operações destrutivas
- 🔒 **Limites de segurança** para atualizações/exclusões
- 🔒 **Análise de padrões perigosos** em tempo real
- 🔒 **Proteção multicamada** (tool + database + prompt)

---

🎉 **Parabéns!** Você agora tem um sistema completamente seguro contra SQL injection e outras vulnerabilidades, mantendo todas as funcionalidades necessárias para operações legítimas!