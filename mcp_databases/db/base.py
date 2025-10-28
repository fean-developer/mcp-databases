from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDB(ABC):
    def __init__(self, conn_params: dict):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            conn_params: Parâmetros de conexão obrigatórios
        """
        if not conn_params:
            raise ValueError("conn_params é obrigatório e não pode ser None ou vazio")
        self.conn_params = conn_params

    @abstractmethod
    def execute_query(self, query: str) -> list[dict]:
        pass

    @abstractmethod
    def insert_record(self, table: str, data: dict) -> None:
        pass

    @abstractmethod
    def list_tables(self) -> list[str]:
        pass

    @abstractmethod
    def get_schema(self) -> str:
        pass
