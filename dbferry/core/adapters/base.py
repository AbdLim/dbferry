from abc import ABC, abstractmethod
from typing import Any, List, Dict
from dbferry.core.config import DBConfig


class BaseAdapter(ABC):
    """Abstract base class for all DB adapters."""

    def __init__(self, config: DBConfig):
        self.config = config
        self.conn: Any = None

    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Perform a lightweight connection test."""
        pass

    @abstractmethod
    def list_tables(self) -> List[str]:
        """Return a list of table names in the current database."""
        pass

    @abstractmethod
    def fetch_rows(self, table_name: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch rows from a table as a list of dicts."""
        pass

    @abstractmethod
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into a table."""
        pass
