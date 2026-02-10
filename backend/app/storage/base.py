from abc import ABC, abstractmethod
from typing import Any


class Storage(ABC):
    """Abstract storage backend."""

    @abstractmethod
    def save(self, content: bytes, filename: str) -> str:
        """Save content and return unique name."""
        pass

    @abstractmethod
    def read(
        self,
        unique_name: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Read paginated CSV data."""
        pass