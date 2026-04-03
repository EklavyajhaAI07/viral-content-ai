import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                self._client = aioredis.from_url(
                    settings.REDIS_URL, encoding="utf-8",
                    decode_responses=True, socket_connect_timeout=2,
                )
            except Exception as e:
                logger.warning(f"Redis init failed: {e}")
        return self._client

    async def ping(self):
        client = await self._get_client()
        if client:
            return await client.ping()
        raise ConnectionError("Redis not available")

    async def get(self, key: str):
        try:
            client = await self._get_client()
            if not client: return None
            value = await client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Redis GET failed: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None):
        try:
            client = await self._get_client()
            if not client: return False
            await client.setex(key, ttl or settings.CACHE_TTL, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed: {e}")
            return False

    async def delete(self, key: str):
        try:
            client = await self._get_client()
            if not client: return False
            await client.delete(key)
            return True
        except Exception as e:
            return False

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

redis_client = RedisClient()
