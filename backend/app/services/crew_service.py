import re
import time
import uuid
import logging
from app.agents.trend_scout import run_trend_scout
from app.agents.virality_predictor import run_virality_predictor
from app.agents.content_optimizer import run_content_optimizer
from app.agents.algorithm_analyst import run_algorithm_analyst
from app.agents.strategist import run_strategist
from app.core.redis_client import redis_client
from app.tools.trend_engine import fetch_all_trends

logger = logging.getLogger(__name__)


def _cache_key(prefix: str, topic: str, platform: str) -> str:
    slug = re.sub(r"\W+", "_", topic.lower())[:60]
    return f"{prefix}:{platform}:{slug}"


def _extract_virality_score(text: str) -> int:
    patterns = [
        r"overall\s+virality\s+score[:\s]+(\d{1,3})",
        r"overall\s+score[:\s]+(\d{1,3})",
        r"virality\s+score[:\s]+(\d{1,3})",
        r"(\d{1,3})\s*/\s*100",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            score = int(m.group(1))
            if 0 <= score <= 100:
                return score
    return 75


async def run_full_analyze(topic, platform, tone, target_audience, caption="", hashtags=""):
    job_id = str(uuid.uuid4())
    cache_key = _cache_key("analyze", topic, platform)

    cached = await redis_client.get(cache_key)
    if cached:
        cached["job_id"] = job_id
        cached["cached"] = True
        return cached

    t0 = time.time()

    # Fetch real trend data first
    real_data = await fetch_all_trends(topic, platform)

    trend_result    = run_trend_scout(topic, platform, real_data=real_data)
    content_result  = run_content_optimizer(topic, platform, tone, target_audience)
    virality_result = run_virality_predictor(
        topic=topic,
        caption=caption or content_result.get("content_package", ""),
        hashtags=hashtags,
        platform=platform,
    )
    virality_score  = _extract_virality_score(virality_result.get("virality_analysis", ""))
    algo_result     = run_algorithm_analyst(topic, platform)
    strategy_result = run_strategist(topic, platform, virality_score)

    result = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "status": "completed",
        "virality_score": virality_score,
        "virality_analysis": virality_result.get("virality_analysis"),
        "content_package": content_result.get("content_package"),
        "trends": trend_result.get("trends"),
        "real_trend_data": real_data,
        "algorithm_guide": algo_result.get("algo_analysis"),
        "strategy": strategy_result.get("strategy"),
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, result, ttl=600)
    return result


async def run_generate(topic, platform, tone, target_audience):
    job_id = str(uuid.uuid4())
    cache_key = _cache_key("generate", f"{topic}_{tone}_{target_audience}", platform)

    cached = await redis_client.get(cache_key)
    if cached:
        cached["job_id"] = job_id
        cached["cached"] = True
        return cached

    t0 = time.time()
    content_result  = run_content_optimizer(topic, platform, tone, target_audience)
    algo_result     = run_algorithm_analyst(topic, platform)
    strategy_result = run_strategist(topic, platform)

    result = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "content_package": content_result.get("content_package"),
        "algorithm_guide": algo_result.get("algo_analysis"),
        "strategy": strategy_result.get("strategy"),
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, result, ttl=600)
    return result


async def run_trends(topic, platform):
    job_id = str(uuid.uuid4())
    cache_key = _cache_key("trends", topic, platform)

    cached = await redis_client.get(cache_key)
    if cached:
        cached["job_id"] = job_id
        cached["cached"] = True
        return cached

    t0 = time.time()

    # Fetch real data
    real_data    = await fetch_all_trends(topic, platform)
    trend_result = run_trend_scout(topic, platform, real_data=real_data)

    result = {
        "job_id": job_id,
        "topic": topic,
        "platform": platform,
        "trends": trend_result.get("trends"),
        "real_data": {
            "google_trends":      real_data.get("google_trends", {}),
            "rising_topics":      real_data.get("rising_topics", []),
            "youtube_trending":   real_data.get("youtube_trending", {}).get("videos", [])[:5],
            "suggested_hashtags": real_data.get("suggested_hashtags", []),
        },
        "status": "completed",
        "cached": False,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    await redis_client.set(cache_key, result, ttl=300)
    return result
