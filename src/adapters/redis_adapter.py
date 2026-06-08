import redis.asyncio as redis
from typing import Any
from src.ports.output.redis_port import RedisPort

class RedisAdapter(RedisPort):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> dict[str, Any]:
        return await self.redis_client.hgetall(key)

    async def set(self, key: str, value: dict[str, Any]) -> None:
        await self.redis_client.hset(key, mapping=value)

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)

    async def update(self, key: str, value: dict[str, Any]) -> None:
        await self.redis_client.hset(key, mapping=value)

