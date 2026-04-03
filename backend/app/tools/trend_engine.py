"""
Trend Engine — fetches real-time trend data from:
  - SerpAPI  → Google Trends (interest over time + related queries)
  - YouTube  → trending videos for a topic
  - Pytrends → hashtag velocity (fallback if SerpAPI quota exceeded)
"""
import os
import logging
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SERPAPI_KEY   = os.getenv("SERPAPI_KEY", "")
YOUTUBE_KEY   = os.getenv("YOUTUBE_API_KEY", "")


# ── SerpAPI — Google Trends ───────────────────────────

async def fetch_google_trends(topic: str) -> dict:
    """Fetch Google Trends interest + related queries via SerpAPI."""
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY not set", "data": []}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_trends",
                    "q": topic,
                    "data_type": "RELATED_QUERIES",
                    "api_key": SERPAPI_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            related = []
            for block in ["rising", "top"]:
                queries = (
                    data.get("related_queries", {})
                        .get(block, [])
                )
                for q in queries[:5]:
                    related.append({
                        "query": q.get("query", ""),
                        "type": block,
                        "value": q.get("value", 0),
                    })

            return {
                "source": "google_trends",
                "topic": topic,
                "related_queries": related,
                "interest_over_time": data.get("interest_over_time", {}).get("timeline_data", [])[-5:],
            }
    except Exception as e:
        logger.warning(f"SerpAPI error: {e}")
        return {"source": "google_trends", "error": str(e), "data": []}


async def fetch_google_trends_interest(topic: str) -> dict:
    """Fetch interest over time + related topics."""
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY not set"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_trends",
                    "q": topic,
                    "data_type": "RELATED_TOPICS",
                    "api_key": SERPAPI_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            rising = data.get("related_topics", {}).get("rising", [])[:5]
            return {
                "source": "google_trends_topics",
                "rising_topics": [t.get("topic", {}).get("title", "") for t in rising],
            }
    except Exception as e:
        logger.warning(f"SerpAPI topics error: {e}")
        return {"error": str(e)}


# ── YouTube Data API — Trending Videos ───────────────

async def fetch_youtube_trends(topic: str, max_results: int = 10) -> dict:
    """Search YouTube for trending videos on a topic."""
    if not YOUTUBE_KEY:
        return {"error": "YOUTUBE_API_KEY not set", "videos": []}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": topic,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": _days_ago(3),
                    "maxResults": max_results,
                    "key": YOUTUBE_KEY,
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

            videos = []
            for item in items:
                snip = item.get("snippet", {})
                videos.append({
                    "title": snip.get("title", ""),
                    "channel": snip.get("channelTitle", ""),
                    "published": snip.get("publishedAt", ""),
                    "description": snip.get("description", "")[:120],
                    "video_id": item.get("id", {}).get("videoId", ""),
                })

            return {"source": "youtube", "topic": topic, "videos": videos}
    except Exception as e:
        logger.warning(f"YouTube API error: {e}")
        return {"source": "youtube", "error": str(e), "videos": []}


async def fetch_youtube_video_stats(video_ids: list) -> dict:
    """Get view counts and likes for a list of video IDs."""
    if not YOUTUBE_KEY or not video_ids:
        return {}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics,snippet",
                    "id": ",".join(video_ids[:10]),
                    "key": YOUTUBE_KEY,
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            stats = {}
            for item in items:
                vid_id = item["id"]
                s = item.get("statistics", {})
                stats[vid_id] = {
                    "views": int(s.get("viewCount", 0)),
                    "likes": int(s.get("likeCount", 0)),
                    "comments": int(s.get("commentCount", 0)),
                }
            return stats
    except Exception as e:
        logger.warning(f"YouTube stats error: {e}")
        return {}


# ── Aggregated Trend Report ───────────────────────────

async def fetch_all_trends(topic: str, platform: str = "all") -> dict:
    """
    Master function — pulls from all sources and returns
    a unified trend report ready for the CrewAI agent.
    """
    import asyncio

    google_task  = fetch_google_trends(topic)
    google_topic = fetch_google_trends_interest(topic)
    youtube_task = fetch_youtube_trends(topic)

    google_data, google_topics, youtube_data = await asyncio.gather(
        google_task, google_topic, youtube_task
    )

    # Pull video stats for top 5 YouTube results
    video_ids = [v["video_id"] for v in youtube_data.get("videos", [])[:5] if v.get("video_id")]
    yt_stats  = await fetch_youtube_video_stats(video_ids) if video_ids else {}

    # Attach stats to videos
    for v in youtube_data.get("videos", []):
        vid_id = v.get("video_id", "")
        if vid_id in yt_stats:
            v.update(yt_stats[vid_id])

    # Build hashtag suggestions from related queries
    hashtags = []
    for q in google_data.get("related_queries", []):
        tag = "#" + q["query"].replace(" ", "").lower()[:30]
        hashtags.append(tag)

    return {
        "topic": topic,
        "platform": platform,
        "google_trends": google_data,
        "rising_topics": google_topics.get("rising_topics", []),
        "youtube_trending": youtube_data,
        "suggested_hashtags": hashtags[:15],
        "sources": ["google_trends", "youtube"],
    }


# ── Helpers ───────────────────────────────────────────

def _days_ago(days: int) -> str:
    from datetime import datetime, timedelta, timezone
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
