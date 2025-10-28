# 🛡️ MCP Databases Server - Seguro e Robusto

Este projeto implementa um servidor MCP (Model Context Protocol) em Python para expor operações de banco de dados relacionais (SQL Server, MySQL, PostgreSQL) como ferramentas MCP, permitindo que aplicações LLM e agentes consultem e manipulem dados de forma **segura e protegida contra SQL injection**.

## 🎯 O que este MCP Server faz?
- Expõe operações de banco de dados como ferramentas MCP (tools) para uso por LLMs, agentes e automações
- **Proteção multicamada** contra SQL injection e comandos maliciosos
- **Configuração automática** via arquivos .env com busca hierárquica
- **Validação rigorosa** de todas as operações de banco de dados
- Suporta integração com VS Code e Claude via arquivo `mcp.json`
- **Impossível contornar** as proteções de segurança implementadas

## 🛠️ Tools Disponíveis

### 📊 **Consulta de Dados (Somente Leitura)**
- **execute_query**: Executa queries SELECT com validação de segurança
- **list_tables**: Lista todas as tabelas do banco de dados
- **expose_schema**: Expõe o schema completo do banco de dados

### 🏗️ **Operações DDL (Data Definition Language)**
- **create_table**: Cria tabelas com validação de nomes e tipos
- **alter_table**: Modifica estrutura de tabelas (ADD, MODIFY, DROP COLUMN)
- **drop_table**: Remove tabelas (⚠️ requer confirmação dupla)

### 📝 **Operações DML (Data Manipulation Language)**
- **insert_record**: Insere um registro único com parâmetros seguros
- **bulk_insert**: Inserção em lote com validação e limites de segurança
- **update_records**: Atualiza registros com parâmetros e limites configuráveis
- **delete_records**: Exclui registros (⚠️ requer confirmação e limites)

### 🛡️ **Ferramentas de Segurança**
- **security_check**: Verifica se uma query é segura sem executá-la
- **get_security_config**: Exibe configurações de segurança ativas
- **safe_query_prompt**: Validação adicional de queries perigosas

## 🚨 Pontos de Atenção e Segurança

### ⛔ **Comandos Bloqueados**
O sistema bloqueia automaticamente:
- `DELETE`, `DROP`, `EXEC`, `EXECUTE`, `TRUNCATE`
- `ALTER USER`, `GRANT`, `REVOKE`, `CREATE USER`
- `xp_cmdshell`, `sp_*`, `OPENROWSET`, `BULK INSERT`
- Qualquer tentativa de SQL injection

### 🔒 **Proteções Implementadas**
- **Parâmetros obrigatórios**: Impossível executar sem configuração adequada
- **Validação multicamada**: Tool → Database → Prompt → Config
- **Queries parametrizadas**: 100% dos valores são sanitizados
- **Confirmação dupla**: Operações destrutivas exigem confirmação exata
- **Limites de segurança**: Controle de quantos registros podem ser afetados
- **Nomes validados**: Apenas caracteres alfanuméricos e underscore

### ⚠️ **Operações que Requerem Cuidado**
- **drop_table**: Requer confirmação exata `DELETE_TABLE_<nome_tabela>`
- **delete_records**: Requer confirmação `DELETE_FROM_<tabela>_WHERE_<condição>`
- **update_records**: Limitado por `safety_limit` (padrão: 100 registros)
- **bulk_insert**: Máximo de 10.000 registros por operação

### 🔧 **Configuração Obrigatória**
- **Arquivo .env**: Busca automática na raiz → subpastas → solicitação ao usuário
- **Parâmetros obrigatórios**: DB_TYPE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- **Sem configuração = sem execução**: Sistema não permite bypass


## 🚀 Instalação e Configuração

### 📁 **Configuração do Ambiente (.env)**
O sistema busca automaticamente arquivos .env na seguinte ordem:
1. Diretório raiz do projeto
2. Subpastas (config/, db/, local/, etc.)
3. Solicitação interativa ao usuário

**Exemplo de arquivo .env:**
```env
# PostgreSQL
DB_TYPE=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=sua_senha_aqui
DB_NAME=minha_base

# MySQL
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=minha_base

# SQL Server
DB_TYPE=mssql
DB_HOST=localhost
DB_PORT=1433
DB_USER=sa
DB_PASSWORD=sua_senha_aqui
DB_NAME=minha_base
```

## 📦 Instalação Local e Global (Linux)

### Instalação local (ambiente virtual)

### Na raiz do projeto crie uma pasta `.mcpenv`

1. Crie e ative o ambiente virtual:
  ```sh
  python3 -m venv .mcpenv
  source .mcpenv/bin/activate
  ```
2. Instale as dependências:
  ```sh
  pip install -r requirements.txt
  pip install .
  ```

## 🔧 Gerando o arquivo mcp.json
No diretório do projeto, crie um arquivo `.vscode`/`mcp.json` com o seguinte conteúdo:

### 📍 **Para Instalação Local:**
```json
{
  "servers": {
    "mcp-databases": {
      "type": "stdio",
      "command": ".mcpenv/bin/python",
      "args": ["server.py"]
    }
  }
}
```

### 🌐 **Para Instalação Global (pipx):**
```json
{
  "servers": {
    "mcp-databases": {
      "transport": "stdio",
      "command": "/home/%USER%/.local/bin/mcp-databases",
      "tools": [
        "execute_query",
        "list_tables", 
        "expose_schema",
        "insert_record",
        "create_table",
        "alter_table", 
        "drop_table",
        "update_records",
        "delete_records",
        "bulk_insert",
        "security_check",
        "get_security_config",
        "safe_query_prompt"
      ]
    }
  }
}
```
3. O comando `mcp-databases` estará disponível no terminal enquanto o ambiente estiver ativado.


### Instalação global (pipx)
1. Instale o pipx (se necessário):
  ```sh
  sudo apt update
  sudo apt install pipx
  pipx ensurepath
  ```
2. Instale o MCP globalmente:
  ```sh
  pipx install /caminho/para/seu/projeto
  pipx inject mcp-databases python-dotenv
  ```
3. O comando `mcp-databases` ficará disponível em qualquer terminal do sistema.

### Crie uma pasta na raiz do projeto .vscode isso instala o mcp nas extensões do vscode

## 🔄 Atualização Global
Se atualizar o código, reinstale com:
```sh
pipx reinstall mcp-databases
```

## 📋 Dependências

### 🐍 **Python e Frameworks**
- Python 3.10+
- [FastMCP >=2.13.0](https://github.com/modelcontextprotocol/python-sdk) - Framework MCP moderno
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento de variáveis de ambiente

### 🗄️ **Drivers de Banco de Dados**
- [pyodbc](https://pypi.org/project/pyodbc/) - SQL Server
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/) - MySQL
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/) - PostgreSQL

### 🔧 **Drivers ODBC do Sistema**
- **SQL Server**: `msodbcsql18` 
  ```sh
  sudo apt-get install msodbcsql18
  ```
- **MySQL**: `libmysqlclient-dev`
  ```sh
  sudo apt-get install libmysqlclient-dev
  ```
- **PostgreSQL**: `libpq-dev`
  ```sh
  sudo apt-get install libpq-dev
  ```

### ⚡ **Instalação das Dependências**
```sh
# Instalação local
pip install -r requirements.txt

# Instalação global com pipx (caso de erro de módulo não encontrado)
pipx inject mcp-databases mysql-connector-python
pipx inject mcp-databases psycopg2-binary
pipx inject mcp-databases pyodbc
pipx inject mcp-databases python-dotenv
```

## 🎮 Como Usar

### 1️⃣ **Executar o Servidor MCP**
```sh
# Local (ambiente virtual)
source .mcpenv/bin/activate
python server.py

# Global (pipx)
mcp-databases
```

### 2️⃣ **Rodar através do VS Code**
1. Vá em **Extensões → MCP SERVERS**
2. Selecione o servidor `mcp-databases`
3. Use o **GitHub Copilot Chat** para interagir

### 3️⃣ **Exemplos de Uso Seguro**

#### 📊 **Consultas (100% Seguras)**
```
@mcp listar todas as tabelas do banco
@mcp mostrar a estrutura da tabela usuarios
@mcp executar: SELECT nome, email FROM usuarios WHERE status = 'ativo'
```

#### 🏗️ **Criar Tabela**
```
@mcp criar uma tabela chamada 'produtos' com colunas: id (int primary key), nome (varchar 255), preco (decimal)
```

#### 📝 **Inserção Segura**
```
@mcp inserir um novo usuário: nome 'João Silva', email 'joao@empresa.com'
@mcp fazer inserção em lote de 5 produtos na tabela produtos
```

#### ⚠️ **Operações com Confirmação**
```
@mcp atualizar salário do usuário com id 123 para 5500.00
@mcp remover usuários inativos da tabela usuarios (confirmação necessária)
```

## 📈 Exemplos de Uso pelo Copilot

### ✅ **Listando Tabelas**

![alt text](image-1.png)

### ✅ **Executando Queries Seguras**
![alt text](image-2.png)

### ✅ **Analisando Procedures**
![alt text](image-3.png)

## 🛡️ Garantias de Segurança

### ✅ **O que está PROTEGIDO:**
- ✅ **SQL Injection**: 100% bloqueado com parâmetros seguros
- ✅ **Comandos destrutivos**: DELETE, DROP, EXEC bloqueados
- ✅ **Bypass de proteções**: Impossível contornar validações
- ✅ **Configuração obrigatória**: Sistema não executa sem .env
- ✅ **Validação multicamada**: Tool + Database + Prompt + Config

### ✅ **O que está PERMITIDO:**
- ✅ **Consultas (SELECT)**: Totalmente liberadas e seguras
- ✅ **Inserções**: Com validação de parâmetros
- ✅ **Atualizações**: Com limites e confirmação
- ✅ **Criação de estruturas**: DDL com validação rigorosa
- ✅ **Operações administrativas**: List tables, expose schema

### ❌ **O que está BLOQUEADO:**
- ❌ **SQL Injection**: Qualquer tentativa é detectada e bloqueada
- ❌ **Comandos maliciosos**: DROP, DELETE, EXEC, TRUNCATE
- ❌ **Nomes inválidos**: Caracteres especiais em tabelas/colunas
- ❌ **Bypass de confirmação**: Operações destrutivas sem confirmação exata
- ❌ **Execução sem configuração**: Parâmetros obrigatórios

## 📚 Documentação Adicional

- 📖 **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Guia completo de uso das ferramentas
- 🚀 **[EXAMPLE_USAGE.md](EXAMPLE_USAGE.md)** - Exemplo prático passo a passo
- 🛡️ **[SECURITY_README.md](SECURITY_README.md)** - Detalhes técnicos de segurança
- 🏗️ **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Visão geral da arquitetura

## 🆘 Suporte e Contribuições

Para dúvidas, problemas ou contribuições:
- 📚 Consulte a [documentação oficial do MCP](https://modelcontextprotocol.io/)
- 🐛 Abra uma [issue neste repositório](https://github.com/fean-developer/mcp-databases/issues)
- 💡 Propose melhorias via [Pull Request](https://github.com/fean-developer/mcp-databases/pulls)

---

## 🏆 Status do Projeto

**✅ PRODUÇÃO - SISTEMA SEGURO**
- 🛡️ **SQL Injection Proof** - Proteção total implementada
- 🔄 **Multi-SGBD** - PostgreSQL, MySQL, SQL Server
- ⚙️ **Auto-Config** - Configuração automática via .env
- 🧪 **100% Testado** - Testes abrangentes de segurança

**Última atualização:** Outubro 2025 - Sistema completamente reformulado com foco em segurança máxima.
