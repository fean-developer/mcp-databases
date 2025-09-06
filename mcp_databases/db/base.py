from abc import ABC, abstractmethod

class BaseDB(ABC):
    def __init__(self, conn_params: dict):
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
