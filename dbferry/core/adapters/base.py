from abc import ABC, abstractmethod
from typing import Any, List
from dbferry.core.config import DBConfig


class BaseAdapter(ABC):
    """Abstract base class for all DB adapters."""

    def __init__(self, config: DBConfig):
        self.config = config
        self.conn: Any = None

    @abstractmethod
    def list_tables(self) -> List[str]:
        """Return a list of table names in the current database."""
        pass

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
