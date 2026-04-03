"""
redis_client.py — Redis client with:
  - Async get/set/delete (existing)
  - Score memory cache: assign a virality score to a topic+platform key
  - Scalable cache model: tiered TTL, cache-miss callback, prefix namespacing
  - Sync fallback (for non-async contexts like run_crew.py)
"""

import json
import hashlib
import logging
import time
from typing import Any, Callable, Optional

import redis.asyncio as aioredis
import redis as sync_redis

logger = logging.getLogger(__name__)


# ── Cache key namespaces ──────────────────────────────────────────────────────

class NS:
    SCORE    = "score"      # virality score cache
    TREND    = "trend"      # trend data cache
    CONTENT  = "content"    # content package cache
    GEO      = "geo"        # geo-enriched data cache
    CRAWL    = "crawl"      # web crawl result cache
    SESSION  = "session"    # user session data


# ── TTL tiers (seconds) ───────────────────────────────────────────────────────

class TTL:
    SHORT    = 300       #  5 min — trend data (changes fast)
    MEDIUM   = 1_800     # 30 min — content packages
    LONG     = 86_400    # 24 hr  — virality scores (stable)
    EXTENDED = 604_800   #  7 days — geo static data


# ── Key builder ───────────────────────────────────────────────────────────────

def build_key(namespace: str, *parts: str) -> str:
    """
    Builds a namespaced cache key.
    Long strings are hashed to keep keys short.

    Examples:
        build_key(NS.SCORE, "AI trends", "instagram") → "score:ai_trends:instagram"
        build_key(NS.CONTENT, long_topic)             → "content:sha256_..."
    """
    slug = ":".join(
        p.lower().strip().replace(" ", "_")[:40]
        for p in parts
        if p
    )
    if len(slug) > 80:
        slug = hashlib.sha256(slug.encode()).hexdigest()[:16]
    return f"{namespace}:{slug}"


# ── Async Redis Client ────────────────────────────────────────────────────────

class RedisClient:
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._url    = url
        self._client = None

    async def _get_client(self):
        if not self._client:
            self._client = aioredis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    # ── Core ops ──────────────────────────────────────────────────────────────

    async def ping(self) -> bool:
        try:
            client = await self._get_client()
            return await client.ping()
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            val = await client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.warning(f"Redis GET error [{key}]: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = TTL.MEDIUM) -> bool:
        try:
            client = await self._get_client()
            await client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning(f"Redis SET error [{key}]: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error [{key}]: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.exists(key))
        except Exception:
            return False

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Score memory cache ────────────────────────────────────────────────────

    async def assign_score(
        self,
        topic: str,
        platform: str,
        score: int,
        breakdown: Optional[dict] = None,
        ttl: int = TTL.LONG,
    ) -> str:
        """
        Persist a virality score for a topic+platform.
        Returns the cache key for reference.

        breakdown: optional dict with sub-scores (hook, timing, hashtags, etc.)
        """
        key = build_key(NS.SCORE, topic, platform)
        payload = {
            "topic":     topic,
            "platform":  platform,
            "score":     score,
            "breakdown": breakdown or {},
            "cached_at": int(time.time()),
        }
        await self.set(key, payload, ttl=ttl)
        logger.info(f"[SCORE CACHE] Assigned score={score} → {key}")
        return key

    async def recall_score(
        self,
        topic: str,
        platform: str,
    ) -> Optional[dict]:
        """
        Retrieve a previously assigned virality score.
        Returns None on cache miss.
        """
        key = build_key(NS.SCORE, topic, platform)
        data = await self.get(key)
        if data:
            age_seconds = int(time.time()) - data.get("cached_at", 0)
            logger.info(f"[SCORE CACHE] Hit → {key} (age={age_seconds}s)")
        else:
            logger.info(f"[SCORE CACHE] Miss → {key}")
        return data

    async def get_or_compute_score(
        self,
        topic: str,
        platform: str,
        compute_fn: Callable,
        ttl: int = TTL.LONG,
    ) -> dict:
        """
        Cache-aside pattern: try recall → on miss, call compute_fn → cache result.

        compute_fn must be async and return a dict with at least {"score": int}.
        """
        cached = await self.recall_score(topic, platform)
        if cached:
            cached["from_cache"] = True
            return cached

        result = await compute_fn(topic, platform)
        score  = result.get("score", 0)
        await self.assign_score(topic, platform, score, result.get("breakdown"), ttl=ttl)
        result["from_cache"] = False
        return result

    # ── Generic cache-aside ───────────────────────────────────────────────────

    async def get_or_set(
        self,
        key: str,
        compute_fn: Callable,
        ttl: int = TTL.MEDIUM,
    ) -> Any:
        """
        Generic cache-aside. compute_fn must be async and return a JSON-serializable value.
        """
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await compute_fn()
        await self.set(key, value, ttl=ttl)
        return value

    # ── Score leaderboard (sorted set) ───────────────────────────────────────

    async def update_leaderboard(
        self,
        platform: str,
        topic: str,
        score: int,
    ):
        """Maintain a sorted leaderboard of top topics per platform."""
        key = f"leaderboard:{platform}"
        try:
            client = await self._get_client()
            await client.zadd(key, {topic: score})
            await client.expire(key, TTL.LONG)
        except Exception as e:
            logger.warning(f"Leaderboard update error: {e}")

    async def get_top_topics(
        self,
        platform: str,
        limit: int = 10,
    ) -> list[dict]:
        """Return top N topics by virality score for a platform."""
        key = f"leaderboard:{platform}"
        try:
            client = await self._get_client()
            results = await client.zrevrange(key, 0, limit - 1, withscores=True)
            return [{"topic": t, "score": int(s)} for t, s in results]
        except Exception as e:
            logger.warning(f"Leaderboard fetch error: {e}")
            return []


# ── Sync Redis wrapper (for run_crew.py / non-async contexts) ─────────────────

class SyncRedisClient:
    """
    Synchronous wrapper — used by run_crew.py and Celery workers.
    All methods block; no async required.
    """
    def __init__(self, url: str = "redis://localhost:6379/0"):
        try:
            self._client = sync_redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
            )
        except Exception as e:
            logger.warning(f"Sync Redis unavailable: {e}")
            self._client = None

    def _ok(self) -> bool:
        return self._client is not None

    def get(self, key: str) -> Optional[Any]:
        if not self._ok():
            return None
        try:
            val = self._client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.warning(f"Sync GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = TTL.MEDIUM) -> bool:
        if not self._ok():
            return False
        try:
            self._client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning(f"Sync SET error: {e}")
            return False

    def recall_score(self, topic: str, platform: str) -> Optional[dict]:
        key = build_key(NS.SCORE, topic, platform)
        return self.get(key)

    def assign_score(
        self,
        topic: str,
        platform: str,
        score: int,
        breakdown: Optional[dict] = None,
        ttl: int = TTL.LONG,
    ) -> str:
        key = build_key(NS.SCORE, topic, platform)
        payload = {
            "topic":     topic,
            "platform":  platform,
            "score":     score,
            "breakdown": breakdown or {},
            "cached_at": int(time.time()),
        }
        self.set(key, payload, ttl=ttl)
        logger.info(f"[SYNC SCORE CACHE] {key} = {score}")
        return key

    def update_leaderboard(self, platform: str, topic: str, score: int):
        if not self._ok():
            return
        key = f"leaderboard:{platform}"
        try:
            self._client.zadd(key, {topic: score})
            self._client.expire(key, TTL.LONG)
        except Exception as e:
            logger.warning(f"Leaderboard error: {e}")

    def get_top_topics(self, platform: str, limit: int = 10) -> list[dict]:
        if not self._ok():
            return []
        key = f"leaderboard:{platform}"
        try:
            results = self._client.zrevrange(key, 0, limit - 1, withscores=True)
            return [{"topic": t, "score": int(s)} for t, s in results]
        except Exception as e:
            logger.warning(f"Leaderboard fetch error: {e}")
            return []


# ── Singletons ────────────────────────────────────────────────────────────────

def _get_redis_url() -> str:
    import os
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


# Async (FastAPI, background workers)
redis_client = RedisClient(url=_get_redis_url())

# Sync (run_crew.py, Celery tasks)
sync_cache = SyncRedisClient(url=_get_redis_url())