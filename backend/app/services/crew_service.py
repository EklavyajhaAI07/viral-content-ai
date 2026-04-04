"""
crew_service.py
Each function = one agent call = one focused job.
All sync CrewAI calls are wrapped in run_in_executor so they
don't block the async event loop.
"""

import time
import uuid
import logging
import asyncio
from functools import partial

from app.agents.trend_scout import run_trend_scout
from app.agents.virality_predictor import run_virality_predictor
from app.agents.content_optimizer import run_hook_only, run_caption_only, run_hashtags_only
from app.agents.strategist import run_strategist
from app.core.redis_client import redis_client, build_key, NS, TTL
from app.tools.trend_engine import fetch_all_trends
from app.services.thumbnail_service import generate_thumbnail

logger = logging.getLogger(__name__)


# ─── Helper — run sync function in threadpool ─────────────────────────────────

async def _run_sync(fn, *args, **kwargs):
    """Run a blocking synchronous function in a threadpool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(fn, *args, **kwargs))


# ─── TRENDS ───────────────────────────────────────────────────────────────────

async def service_get_trends(topic: str, platform: str) -> dict:
    job_id = str(uuid.uuid4())
    cache_key = build_key(NS.TREND, topic, platform)

    cached = await redis_client.get(cache_key)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # fetch_all_trends does async HTTP — run directly but with a timeout
    try:
        real_data = await asyncio.wait_for(
            fetch_all_trends(topic, platform),
            timeout=15.0  # don't wait more than 15s for external APIs
        )
    except asyncio.TimeoutError:
        logger.warning(f"fetch_all_trends timed out for topic={topic}, proceeding without real data")
        real_data = {}

    # run_trend_scout is sync CrewAI — run in threadpool
    result = await _run_sync(run_trend_scout, topic, platform, real_data)

    payload = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "hashtags": result.get("hashtags", []),
        "viral_angles": result.get("viral_angles", []),
        "niche_classification": result.get("niche_classification", ""),
        "overall_trend_velocity": result.get("overall_trend_velocity", 0),
        "has_real_data": result.get("has_real_data", False),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, payload, ttl=TTL.SHORT)
    return payload


# ─── HOOKS ────────────────────────────────────────────────────────────────────

async def service_generate_hook(
    topic: str, platform: str, tone: str, target_audience: str
) -> dict:
    job_id = str(uuid.uuid4())
    cache_key = build_key(NS.CONTENT, f"hook_{topic}_{tone}", platform)

    cached = await redis_client.get(cache_key)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # run_hook_only is sync CrewAI — run in threadpool
    result = await _run_sync(run_hook_only, topic, platform, tone, target_audience)

    payload = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "hook": result.get("hook", ""),
        "alternative_hooks": result.get("alternative_hooks", []),
        "cta": result.get("cta", ""),
        "format_recommendation": result.get("format_recommendation", ""),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, payload, ttl=TTL.MEDIUM)
    return payload


# ─── CAPTION ──────────────────────────────────────────────────────────────────

async def service_generate_caption(
    topic: str, platform: str, tone: str, target_audience: str, hook: str = ""
) -> dict:
    job_id = str(uuid.uuid4())
    cache_key = build_key(NS.CONTENT, f"caption_{topic}_{tone}", platform)

    cached = await redis_client.get(cache_key)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # run_caption_only is sync CrewAI — run in threadpool
    result = await _run_sync(run_caption_only, topic, platform, tone, target_audience, hook)

    payload = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "caption": result.get("caption", ""),
        "best_posting_time": result.get("best_posting_time", ""),
        "word_count": result.get("word_count", 0),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, payload, ttl=TTL.MEDIUM)
    return payload


# ─── HASHTAGS ─────────────────────────────────────────────────────────────────

async def service_generate_hashtags(topic: str, platform: str) -> dict:
    job_id = str(uuid.uuid4())
    cache_key = build_key(NS.CONTENT, f"hashtags_{topic}", platform)

    cached = await redis_client.get(cache_key)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # run_hashtags_only is sync CrewAI — run in threadpool
    result = await _run_sync(run_hashtags_only, topic, platform)

    payload = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "niche": result.get("niche", []),
        "trending": result.get("trending", []),
        "broad": result.get("broad", []),
        "total_count": result.get("total_count", 15),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, payload, ttl=TTL.MEDIUM)
    return payload


# ─── VIRALITY SCORE ───────────────────────────────────────────────────────────

async def service_predict_virality(
    topic: str, platform: str, caption: str = "", hashtags: str = ""
) -> dict:
    job_id = str(uuid.uuid4())

    cached = await redis_client.recall_score(topic, platform)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # run_virality_predictor is sync CrewAI — run in threadpool
    result = await _run_sync(run_virality_predictor, topic, platform, caption, hashtags)

    await redis_client.assign_score(
        topic, platform,
        score=result["overall_score"],
        breakdown=result["breakdown"],
    )
    await redis_client.update_leaderboard(platform, topic, result["overall_score"])

    return {
        **result,
        "job_id": job_id,
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }


# ─── STRATEGY ─────────────────────────────────────────────────────────────────

async def service_generate_strategy(
    topic: str, platform: str, virality_score: int = 75
) -> dict:
    job_id = str(uuid.uuid4())
    cache_key = build_key(NS.CONTENT, f"strategy_{topic}", platform)

    cached = await redis_client.get(cache_key)
    if cached:
        return {**cached, "job_id": job_id, "cached": True}

    t0 = time.time()

    # run_strategist is sync CrewAI — run in threadpool
    result = await _run_sync(run_strategist, topic, platform, virality_score)

    payload = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "strategy": result.get("strategy", ""),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, payload, ttl=TTL.MEDIUM)
    return payload


# ─── THUMBNAIL ────────────────────────────────────────────────────────────────

async def service_generate_thumbnail(
    topic: str, platform: str, tone: str = "engaging"
) -> dict:
    job_id = str(uuid.uuid4())
    t0 = time.time()

    result = await generate_thumbnail(topic, platform)

    return {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "thumbnail": result,
        "status": "completed" if result.get("status") == "ok" else "failed",
        "elapsed_seconds": round(time.time() - t0, 1),
    }