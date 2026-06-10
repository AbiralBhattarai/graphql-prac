from typing import Any
from abc import ABC, abstractmethod


class RedisPort(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict[str, Any]:
        pass
    @abstractmethod
    async def set(self, key: str, value: dict[str, Any]) -> None:
        pass
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
    @abstractmethod
    async def update(self, key: str, value: dict[str, Any]) -> None:
        pass