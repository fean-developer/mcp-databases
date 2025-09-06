from setuptools import setup, find_packages

setup(
    name="mcp_databases",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary",
        "pyodbc",
        "pymssql",
        # Adicione outras dependências necessárias
    ],
    entry_points={
        "console_scripts": [
            "mcp-databases=mcp_databases.server:main"
        ]
    },
    author="fean-developer",
    description="MCP server para bancos de dados SQL Server, MySQL e PostgreSQL",
    python_requires=">=3.10",
)
