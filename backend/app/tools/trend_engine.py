"""
trend_engine.py — Upgraded trend fetcher with:
  - [5] MongoDB document schema integration (saves crawl results as documents)
  - [6] Web crawling: BeautifulSoup scraper for platform-specific pages
  - Geo-aware trend filtering
  - Unified async fetch with caching hooks
  - Graceful fallback when APIs are missing
"""

import os
import asyncio
import hashlib
import logging
import time
from typing import Optional
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SERPAPI_KEY  = os.getenv("SERPAPI_KEY", "")
YOUTUBE_KEY  = os.getenv("YOUTUBE_API_KEY", "")


# ── MongoDB document schema ───────────────────────────────────────────────────

def make_trend_document(
    topic: str,
    platform: str,
    source: str,
    data: dict,
    geo_country: str = "global",
) -> dict:
    doc_id = hashlib.sha256(
        f"{topic}:{platform}:{source}:{int(time.time()//3600)}".encode()
    ).hexdigest()[:16]

    return {
        "_id":         doc_id,
        "topic":       topic,
        "platform":    platform,
        "source":      source,
        "geo":         geo_country,
        "data":        data,
        "crawled_at":  datetime.now(timezone.utc).isoformat(),
        "ttl_hours":   6,
        "schema_v":    2,
    }


def make_content_document(
    topic: str,
    platform: str,
    tone: str,
    audience: str,
    content_package: str,
    virality_score: int,
    geo_country: str = "global",
    model_used: str = "unknown",
) -> dict:
    return {
        "topic":           topic,
        "platform":        platform,
        "tone":            tone,
        "audience":        audience,
        "content_package": content_package,
        "virality_score":  virality_score,
        "geo":             geo_country,
        "model_used":      model_used,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "schema_v":        2,
    }


# ── Empty async fallback (replaces removed asyncio.coroutine) ─────────────────

async def _empty_crawl() -> dict:
    """Safe async no-op — returns empty hashtag suggestions."""
    return {"hashtag_suggestions": [], "extracted_keywords": []}


# ── Web crawler ───────────────────────────────────────────────────────────────

class PlatformCrawler:
    CRAWL_URLS = {
        "instagram": [
            "https://later.com/blog/instagram-trends/",
            "https://www.socialmediatoday.com/topic/instagram/",
        ],
        "tiktok": [
            "https://tokboard.com/",
            "https://www.tiktok.com/discover",
        ],
        "youtube": [
            "https://trends.google.com/trending?geo=US",
            "https://socialblade.com/youtube/top/50/mostsubscribed",
        ],
        "twitter": [
            "https://trends24.in/united-states/",
            "https://getdaytrends.com/united-states/",
        ],
        "linkedin": [
            "https://www.linkedin.com/pulse/topics/home/",
            "https://www.socialinsider.io/blog/linkedin-trends/",
        ],
    }

    GEO_CRAWL_URLS = {
        "IN": {
            "twitter": ["https://trends24.in/india/"],
            "youtube": ["https://trends.google.com/trending?geo=IN"],
        },
        "GB": {
            "twitter": ["https://trends24.in/united-kingdom/"],
        },
        "BR": {
            "twitter": ["https://trends24.in/brazil/"],
        },
    }

    async def crawl_platform(
        self,
        platform: str,
        topic: str = "",
        country_code: str = "US",
        max_pages: int = 2,
        rate_limit: float = 2.5,
    ) -> dict:
        urls = self._get_urls(platform, country_code)
        results = []

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; ContentResearchBot/1.0; "
                "+https://github.com/your-repo)"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers=headers,
        ) as client:
            for i, url in enumerate(urls[:max_pages]):
                try:
                    url = url.replace("{topic}", topic.replace(" ", "%20"))
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        logger.warning(f"Crawl {url}: HTTP {resp.status_code}")
                        continue

                    extracted = self._extract_text(resp.text, platform)
                    results.append({
                        "url":    url,
                        "data":   extracted,
                        "status": "ok",
                    })

                    if i < len(urls) - 1:
                        await asyncio.sleep(rate_limit)

                except Exception as e:
                    logger.warning(f"Crawl error [{url}]: {e}")
                    results.append({"url": url, "status": "error", "error": str(e)})

        all_text = " ".join(
            str(r.get("data", "")) for r in results if r.get("status") == "ok"
        )
        keywords = self._extract_keywords(all_text, topic)

        return {
            "platform":               platform,
            "topic":                  topic,
            "country_code":           country_code,
            "pages_crawled":          len([r for r in results if r.get("status") == "ok"]),
            "raw_results":            results,
            "extracted_keywords":     keywords,
            "hashtag_suggestions":    [f"#{k.replace(' ','')}" for k in keywords[:10]],
            "crawled_at":             datetime.now(timezone.utc).isoformat(),
        }

    def _get_urls(self, platform: str, country_code: str) -> list[str]:
        base = self.CRAWL_URLS.get(platform, [])
        geo_override = self.GEO_CRAWL_URLS.get(country_code, {}).get(platform, [])
        combined = geo_override + [u for u in base if u not in geo_override]
        return combined

    def _extract_text(self, html: str, platform: str) -> str:
        import re
        html = re.sub(r'<(script|style|nav|header|footer)[^>]*>.*?</\1>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]

    def _extract_keywords(self, text: str, seed_topic: str) -> list[str]:
        import re
        from collections import Counter

        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]{3,}\b', text.lower())

        STOP = {
            "this","that","with","from","have","been","will","your","more",
            "also","they","their","what","when","where","which","would",
            "about","just","into","than","then","some","each","there",
            "over","only","most","such","after","before","through","those",
        }
        words = [w for w in words if w not in STOP]

        counts = Counter(words)
        seed_words = seed_topic.lower().split()
        boosted = {
            w: count * (2 if any(s in w or w in s for s in seed_words) else 1)
            for w, count in counts.items()
        }

        top = sorted(boosted.items(), key=lambda x: -x[1])[:15]
        return [w for w, _ in top]


# ── SerpAPI — Google Trends ───────────────────────────────────────────────────

async def fetch_google_trends(topic: str, geo: str = "") -> dict:
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY not set", "data": []}
    try:
        params = {
            "engine":    "google_trends",
            "q":         topic,
            "data_type": "RELATED_QUERIES",
            "api_key":   SERPAPI_KEY,
        }
        if geo:
            params["geo"] = geo

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://serpapi.com/search", params=params)
            resp.raise_for_status()
            data = resp.json()

        related = []
        for block in ["rising", "top"]:
            for q in data.get("related_queries", {}).get(block, [])[:5]:
                related.append({
                    "query": q.get("query", ""),
                    "type":  block,
                    "value": q.get("value", 0),
                })

        return {
            "source":             "google_trends",
            "topic":              topic,
            "geo":                geo,
            "related_queries":    related,
            "interest_over_time": data.get("interest_over_time", {}).get("timeline_data", [])[-5:],
        }
    except Exception as e:
        logger.warning(f"SerpAPI error: {e}")
        return {"source": "google_trends", "error": str(e), "data": []}


async def fetch_google_trends_interest(topic: str, geo: str = "") -> dict:
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY not set"}
    try:
        params = {
            "engine":    "google_trends",
            "q":         topic,
            "data_type": "RELATED_TOPICS",
            "api_key":   SERPAPI_KEY,
        }
        if geo:
            params["geo"] = geo

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://serpapi.com/search", params=params)
            resp.raise_for_status()
            data = resp.json()

        rising = data.get("related_topics", {}).get("rising", [])[:5]
        return {
            "source":        "google_trends_topics",
            "rising_topics": [t.get("topic", {}).get("title", "") for t in rising],
        }
    except Exception as e:
        logger.warning(f"SerpAPI topics error: {e}")
        return {"error": str(e)}


# ── YouTube Data API ──────────────────────────────────────────────────────────

async def fetch_youtube_trends(topic: str, max_results: int = 10) -> dict:
    if not YOUTUBE_KEY:
        return {"error": "YOUTUBE_API_KEY not set", "videos": []}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part":           "snippet",
                    "q":              topic,
                    "type":           "video",
                    "order":          "viewCount",
                    "publishedAfter": _days_ago(3),
                    "maxResults":     max_results,
                    "key":            YOUTUBE_KEY,
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

        videos = [
            {
                "title":       i.get("snippet", {}).get("title", ""),
                "channel":     i.get("snippet", {}).get("channelTitle", ""),
                "published":   i.get("snippet", {}).get("publishedAt", ""),
                "description": i.get("snippet", {}).get("description", "")[:120],
                "video_id":    i.get("id", {}).get("videoId", ""),
            }
            for i in items
        ]
        return {"source": "youtube", "topic": topic, "videos": videos}
    except Exception as e:
        logger.warning(f"YouTube API error: {e}")
        return {"source": "youtube", "error": str(e), "videos": []}


async def fetch_youtube_video_stats(video_ids: list) -> dict:
    if not YOUTUBE_KEY or not video_ids:
        return {}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics",
                    "id":   ",".join(video_ids[:10]),
                    "key":  YOUTUBE_KEY,
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

        return {
            item["id"]: {
                "views":    int(item.get("statistics", {}).get("viewCount", 0)),
                "likes":    int(item.get("statistics", {}).get("likeCount", 0)),
                "comments": int(item.get("statistics", {}).get("commentCount", 0)),
            }
            for item in items
        }
    except Exception as e:
        logger.warning(f"YouTube stats error: {e}")
        return {}


# ── Master aggregator ─────────────────────────────────────────────────────────

async def fetch_all_trends(
    topic: str,
    platform: str = "all",
    country_code: str = "US",
    enable_crawl: bool = True,
) -> dict:
    """
    Master trend fetch with:
      - Google Trends (geo-aware)
      - YouTube trending
      - Platform web crawl
      - Unified hashtag suggestions
    """
    crawler = PlatformCrawler()

    # Launch all fetches concurrently
    tasks = [
        fetch_google_trends(topic, geo=country_code),
        fetch_google_trends_interest(topic, geo=country_code),
        fetch_youtube_trends(topic),
    ]

    # ✅ FIXED: replaced removed asyncio.coroutine with a proper async function
    if enable_crawl and platform != "all":
        tasks.append(crawler.crawl_platform(platform, topic, country_code))
    else:
        tasks.append(_empty_crawl())

    google_data, google_topics, youtube_data, crawl_data = await asyncio.gather(*tasks)

    # Attach YouTube stats
    video_ids = [v["video_id"] for v in youtube_data.get("videos", [])[:5] if v.get("video_id")]
    yt_stats  = await fetch_youtube_video_stats(video_ids) if video_ids else {}
    for v in youtube_data.get("videos", []):
        if v.get("video_id") in yt_stats:
            v.update(yt_stats[v["video_id"]])

    # Merge hashtags from all sources
    hashtags = []
    for q in google_data.get("related_queries", []):
        hashtags.append("#" + q["query"].replace(" ", "").lower()[:30])
    hashtags += crawl_data.get("hashtag_suggestions", [])
    hashtags = list(dict.fromkeys(hashtags))[:15]

    result = {
        "topic":              topic,
        "platform":           platform,
        "geo":                country_code,
        "google_trends":      google_data,
        "rising_topics":      google_topics.get("rising_topics", []),
        "youtube_trending":   youtube_data,
        "crawl_data":         crawl_data,
        "extracted_keywords": crawl_data.get("extracted_keywords", []),
        "suggested_hashtags": hashtags,
        "sources":            ["google_trends", "youtube", "web_crawl"],
    }

    result["_mongo_doc"] = make_trend_document(
        topic=topic,
        platform=platform,
        source="aggregated",
        data={k: v for k, v in result.items() if k != "_mongo_doc"},
        geo_country=country_code,
    )

    return result


# ── Pytrends fallback (no API key needed) ─────────────────────────────────────

async def fetch_pytrends_fallback(topic: str, geo: str = "US") -> dict:
    """Fallback trend data using pytrends (Google Trends unofficial)."""
    try:
        from pytrends.request import TrendReq

        def _sync_fetch():
            pt = TrendReq(hl="en-US", tz=0)
            pt.build_payload([topic], geo=geo, timeframe="now 7-d")
            related = pt.related_queries()
            rising = related.get(topic, {}).get("rising")
            if rising is not None and not rising.empty:
                return rising.head(10).to_dict("records")
            return []

        data = await asyncio.get_event_loop().run_in_executor(None, _sync_fetch)
        return {"source": "pytrends", "topic": topic, "geo": geo, "data": data}
    except Exception as e:
        logger.warning(f"Pytrends fallback failed: {e}")
        return {"source": "pytrends", "error": str(e)}


# ── Helper ────────────────────────────────────────────────────────────────────

def _days_ago(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Singleton crawler ─────────────────────────────────────────────────────────
crawler = PlatformCrawler()