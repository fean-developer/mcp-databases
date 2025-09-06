# Como tornar o MCP global/local

## Instalação global

1. Instale o pacote localmente:
   ```sh
   pip install .
   ```
   Isso adiciona o comando `mcp-databases` ao seu PATH.

2. Configure o arquivo `.env` com os dados do banco desejado.

3. Execute o MCP de qualquer lugar:
   ```sh
   mcp-databases
   ```

## Uso em múltiplos projetos/VS Code
- Qualquer instância do VS Code pode acessar o MCP rodando localmente.
- Basta apontar para o endereço/porta do serviço MCP ou usar o comando global.

## Dicas
- Para rodar como serviço, use um gerenciador como systemd, pm2 ou Docker.
- Para CLI, edite o `setup.py` para expor comandos personalizados.
- Para HTTP, adapte o MCP para rodar com FastAPI ou Flask.

## Exemplo de comando global
```sh
mcp-databases --help
```

---
Se quiser um exemplo de CLI ou serviço HTTP, peça aqui!
