"""
Módulo de configuração para o MCP Databases.
Busca configurações em arquivos .env seguindo a hierarquia:
1. Raiz do projeto
2. Subpastas
3. Solicita ao usuário se não encontrar
"""
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv, find_dotenv
from mcp_databases.logger import MCPLogger

logger = MCPLogger.get_logger("mcp_databases.config")

class ConfigManager:
    """Gerenciador de configurações do MCP Databases"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            project_root: Caminho para a raiz do projeto. Se None, usa o diretório atual.
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Tenta encontrar a raiz do projeto baseado no arquivo atual
            current_file = Path(__file__).parent.parent
            self.project_root = current_file
        
        self._env_loaded = False
        self._config_cache = {}
        
    def load_env_config(self) -> bool:
        """
        Carrega configurações de arquivos .env seguindo a hierarquia:
        1. Raiz do projeto
        2. Subpastas
        
        Returns:
            bool: True se encontrou e carregou um arquivo .env, False caso contrário
        """
        if self._env_loaded:
            return True
            
        # 1. Busca na raiz do projeto
        root_env = self.project_root / '.env'
        if root_env.exists():
            logger.info(f"Carregando configurações de {root_env}")
            load_dotenv(root_env)
            self._env_loaded = True
            return True
        
        # 2. Busca em subpastas
        env_file = self._search_env_in_subfolders()
        if env_file:
            logger.info(f"Carregando configurações de {env_file}")
            load_dotenv(env_file)
            self._env_loaded = True
            return True
        
        # 3. Tenta usar find_dotenv do python-dotenv como fallback
        dotenv_path = find_dotenv()
        if dotenv_path:
            logger.info(f"Carregando configurações de {dotenv_path}")
            load_dotenv(dotenv_path)
            self._env_loaded = True
            return True
            
        logger.warning("Nenhum arquivo .env encontrado")
        return False
    
    def _search_env_in_subfolders(self) -> Optional[Path]:
        """
        Busca recursivamente por arquivos .env nas subpastas do projeto.
        
        Returns:
            Path: Caminho para o primeiro arquivo .env encontrado, ou None
        """
        for root, dirs, files in os.walk(self.project_root):
            # Ignora pastas comuns que não devem conter .env
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            if '.env' in files:
                env_path = Path(root) / '.env'
                logger.info(f"Arquivo .env encontrado em: {env_path}")
                return env_path
                
        return None
    
    def get_db_config(self, db_type: str, interactive: bool = True) -> Dict[str, Any]:
        """
        Obtém configurações de banco de dados para o tipo especificado.
        
        Args:
            db_type: Tipo do banco (postgres, mysql, mssql)
            interactive: Se True, permite interação com o usuário para inserir configurações
            
        Returns:
            Dict: Configurações do banco de dados
        """
        # Tenta carregar do .env primeiro
        self.load_env_config()
        
        config_key = f"{db_type.upper()}_CONFIG"
        
        # Verifica se já tem no cache
        if config_key in self._config_cache:
            return self._config_cache[config_key]
        
        # Tenta obter do ambiente
        config = self._get_config_from_env(db_type)
        
        # Se não encontrou e modo interativo está habilitado, solicita ao usuário
        if not config and interactive:
            config = self._get_config_from_user(db_type)
        
        # Cache da configuração
        if config:
            self._config_cache[config_key] = config
            
        return config or {}
    
    def _get_config_from_env(self, db_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtém configurações do banco de dados das variáveis de ambiente.
        
        Args:
            db_type: Tipo do banco (postgres, mysql, mssql)
            
        Returns:
            Dict: Configurações encontradas ou None
        """
        prefix = db_type.upper()
        
        # Mapeamento comum de variáveis
        env_mapping = {
            'server': [f'{prefix}_HOST', f'{prefix}_SERVER', f'DB_HOST', f'DB_SERVER'],
            'database': [f'{prefix}_DATABASE', f'{prefix}_DB', f'DB_NAME', f'DATABASE'],
            'user': [f'{prefix}_USER', f'{prefix}_USERNAME', f'DB_USER', f'DB_USERNAME'],
            'password': [f'{prefix}_PASSWORD', f'{prefix}_PASS', f'DB_PASSWORD', f'DB_PASS'],
            'port': [f'{prefix}_PORT', f'DB_PORT']
        }
        
        config = {}
        for key, env_vars in env_mapping.items():
            for env_var in env_vars:
                value = os.getenv(env_var)
                if value:
                    config[key] = value
                    break
        
        # Configurações específicas por tipo de banco
        if db_type.lower() == 'postgres':
            config.setdefault('port', os.getenv('POSTGRES_PORT', '5432'))
        elif db_type.lower() == 'mysql':
            config.setdefault('port', os.getenv('MYSQL_PORT', '3306'))
        elif db_type.lower() == 'mssql':
            config.setdefault('port', os.getenv('MSSQL_PORT', '1433'))
            config.setdefault('driver', os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server'))
        
        # Retorna apenas se tem pelo menos server/host e database
        if config.get('server') and config.get('database'):
            logger.info(f"Configurações do {db_type} carregadas do ambiente")
            return config
        
        return None
    
    def _get_config_from_user(self, db_type: str) -> Optional[Dict[str, Any]]:
        """
        Solicita configurações do banco de dados ao usuário via input.
        
        Args:
            db_type: Tipo do banco (postgres, mysql, mssql)
            
        Returns:
            Dict: Configurações inseridas pelo usuário
        """
        logger.info(f"Solicitando configurações do {db_type} ao usuário...")
        
        print(f"\n=== Configuração do Banco {db_type.upper()} ===")
        print("Nenhum arquivo .env encontrado com as configurações.")
        print("Por favor, insira as configurações do banco de dados:")
        
        try:
            config = {}
            config['server'] = input(f"Host/Servidor do {db_type}: ").strip()
            config['database'] = input(f"Nome do banco de dados: ").strip()
            config['user'] = input(f"Usuário: ").strip()
            config['password'] = input(f"Senha: ").strip()
            
            # Porta com valor padrão
            default_ports = {'postgres': '5432', 'mysql': '3306', 'mssql': '1433'}
            default_port = default_ports.get(db_type.lower(), '5432')
            port = input(f"Porta (padrão {default_port}): ").strip()
            config['port'] = port if port else default_port
            
            # Configurações específicas para MSSQL
            if db_type.lower() == 'mssql':
                driver = input("Driver ODBC (padrão: ODBC Driver 17 for SQL Server): ").strip()
                config['driver'] = driver if driver else 'ODBC Driver 17 for SQL Server'
            
            # Validação básica
            if not all([config.get('server'), config.get('database'), config.get('user')]):
                logger.error("Configurações incompletas fornecidas")
                return None
            
            # Pergunta se quer salvar as configurações
            save = input("\nDeseja salvar essas configurações em um arquivo .env? (s/N): ").strip().lower()
            if save in ['s', 'sim', 'y', 'yes']:
                self._save_config_to_env(db_type, config)
            
            return config
            
        except KeyboardInterrupt:
            print("\nConfiguração cancelada pelo usuário.")
            return None
        except Exception as e:
            logger.error(f"Erro ao solicitar configurações: {e}")
            return None
    
    def _save_config_to_env(self, db_type: str, config: Dict[str, Any]) -> None:
        """
        Salva as configurações em um arquivo .env na raiz do projeto.
        
        Args:
            db_type: Tipo do banco
            config: Configurações a serem salvas
        """
        try:
            env_file = self.project_root / '.env'
            prefix = db_type.upper()
            
            # Lê o conteúdo existente se o arquivo já existe
            existing_content = ""
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Adiciona as novas configurações
            new_lines = []
            new_lines.append(f"\n# Configurações do {db_type.upper()}")
            new_lines.append(f"{prefix}_HOST={config.get('server', '')}")
            new_lines.append(f"{prefix}_DATABASE={config.get('database', '')}")
            new_lines.append(f"{prefix}_USER={config.get('user', '')}")
            new_lines.append(f"{prefix}_PASSWORD={config.get('password', '')}")
            new_lines.append(f"{prefix}_PORT={config.get('port', '')}")
            
            if 'driver' in config:
                new_lines.append(f"{prefix}_DRIVER={config['driver']}")
            
            # Escreve o arquivo
            with open(env_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(new_lines) + '\n')
            
            logger.info(f"Configurações salvas em {env_file}")
            print(f"Configurações salvas em {env_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            print(f"Erro ao salvar configurações: {e}")

# Instância global do gerenciador de configurações
config_manager = ConfigManager()

def get_db_config(db_type: str, interactive: bool = True) -> Dict[str, Any]:
    """
    Função utilitária para obter configurações de banco de dados.
    
    Args:
        db_type: Tipo do banco (postgres, mysql, mssql)
        interactive: Se True, permite interação com o usuário
        
    Returns:
        Dict: Configurações do banco de dados
    """
    return config_manager.get_db_config(db_type, interactive)

def load_env_config() -> bool:
    """
    Função utilitária para carregar configurações de .env
    
    Returns:
        bool: True se carregou com sucesso
    """
    return config_manager.load_env_config()