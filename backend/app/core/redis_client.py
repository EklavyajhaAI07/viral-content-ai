import json
import logging
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._client = None

    async def _get_client(self):
        if not self._client:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    async def ping(self):
        client = await self._get_client()
        return await client.ping()

    async def get(self, key: str):
        try:
            client = await self._get_client()
            val = await client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.warning(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: dict, ttl: int = 300):
        try:
            client = await self._get_client()
            await client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis SET error: {e}")

    async def delete(self, key: str):
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


redis_client = RedisClient()
