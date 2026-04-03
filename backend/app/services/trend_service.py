"""
Trend Service — merges real API data with CrewAI agent analysis
"""
import logging
from app.tools.trend_engine import fetch_all_trends
from app.agents.trend_scout import run_trend_scout

logger = logging.getLogger(__name__)


async def get_trends(topic: str, platform: str = "all") -> dict:
    """
    Fetches real trend data and passes it to the Trend Scout agent.
    Falls back to AI-only if APIs are unavailable.
    """
    # Step 1 — fetch real data
    real_data = await fetch_all_trends(topic, platform)

    has_real_data = (
        real_data.get("google_trends", {}).get("related_queries") or
        real_data.get("youtube_trending", {}).get("videos")
    )

    if has_real_data:
        logger.info(f"✅ Real trend data fetched for '{topic}'")
    else:
        logger.warning(f"⚠️ No real data available for '{topic}' — using AI only")

    # Step 2 — pass to agent
    agent_result = run_trend_scout(
        topic=topic,
        platform=platform,
        real_data=real_data if has_real_data else None
    )

    # Step 3 — merge and return
    return {
        "topic": topic,
        "platform": platform,
        "ai_analysis": agent_result.get("trends"),
        "real_data": {
            "google_trends": real_data.get("google_trends", {}),
            "rising_topics": real_data.get("rising_topics", []),
            "youtube_trending": real_data.get("youtube_trending", {}).get("videos", [])[:5],
            "suggested_hashtags": real_data.get("suggested_hashtags", []),
        },
        "has_real_data": bool(has_real_data),
        "status": "completed"
    }


async def get_quick_trends(topic: str, platform: str = "all") -> dict:
    """
    Returns only real API data — no AI agent, much faster.
    Used for raw=True in /api/trends endpoint.
    """
    real_data = await fetch_all_trends(topic, platform)
    return {
        "topic": topic,
        "platform": platform,
        "google_trends": real_data.get("google_trends", {}),
        "rising_topics": real_data.get("rising_topics", []),
        "youtube_trending": real_data.get("youtube_trending", {}).get("videos", [])[:5],
        "suggested_hashtags": real_data.get("suggested_hashtags", []),
        "status": "completed"
    }
