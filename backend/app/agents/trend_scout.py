"""
trend_scout.py
One agent — one focused task.
Returns structured JSON trend data.

run_trend_scout() → GET /api/trends?topic=&platform=
"""

import json
import re
from crewai import Agent, Task, Crew, Process
from app.core.llm import GPT4O_MINI
from dotenv import load_dotenv

load_dotenv()

# ─── AGENT ────────────────────────────────────────────────────────────────────

trend_scout = Agent(
    role="Trend Scout",
    goal="Analyze real social media trend data and return structured viral insights as JSON",
    backstory="""You are an expert social media analyst who interprets real-time trend data 
    from Google Trends and YouTube. You extract viral patterns, velocity scores, and predict 
    peak timing. You ALWAYS respond with valid JSON only — no markdown, no explanation.""",
    verbose=False,
    allow_delegation=False,
    llm=GPT4O_MINI,
)


# ─── TASK RUNNER ──────────────────────────────────────────────────────────────

def run_trend_scout(
    topic: str,
    platform: str = "all",
    real_data: dict = None,
) -> dict:
    """
    Single focused prompt: analyse trends for a topic.
    Injects real API data when available.
    Returns fully structured dict.
    """
    # Build real-data context block
    data_context = ""
    if real_data:
        yt_videos = real_data.get("youtube_trending", {}).get("videos", [])[:5]
        yt_titles = [v.get("title", "") for v in yt_videos]
        rising    = real_data.get("rising_topics", [])
        hashtags  = real_data.get("suggested_hashtags", [])
        google_q  = [q["query"] for q in real_data.get("google_trends", {}).get("related_queries", [])]

        data_context = f"""
REAL-TIME DATA (use as primary source):
Google Trending Queries: {', '.join(google_q[:10]) or 'none'}
Rising Topics: {', '.join(rising[:5]) or 'none'}
Suggested Hashtags: {', '.join(hashtags[:10]) or 'none'}
YouTube Trending Titles: {', '.join(yt_titles) or 'none'}
"""

    task = Task(
        description=f"""Analyse trend data for topic: '{topic}' on platform: {platform}.
{data_context}
Using the data above (or your knowledge if no data), provide:
- top 10 trending hashtags relevant to this topic
- 3 viral content angles with highest potential
- velocity score per hashtag (0–100, how fast it's growing)
- which platform each trend is strongest on
- predicted peak hours from now (integer)

Return ONLY this JSON (no markdown, no extra text):
{{
  "hashtags": [
    {{"tag": "#example", "velocity": 87, "strongest_on": "instagram", "peak_in_hours": 12}},
    {{"tag": "#example2", "velocity": 72, "strongest_on": "tiktok", "peak_in_hours": 6}}
  ],
  "viral_angles": [
    {{"angle": "angle title", "description": "1-sentence description", "virality_score": 85}},
    {{"angle": "angle title", "description": "1-sentence description", "virality_score": 78}},
    {{"angle": "angle title", "description": "1-sentence description", "virality_score": 71}}
  ],
  "niche_classification": "fitness|tech|food|travel|finance|lifestyle|other",
  "overall_trend_velocity": 80,
  "has_real_data": {"true" if real_data else "false"}
}}""",
        expected_output="Valid JSON with hashtags array, viral_angles array, niche_classification, overall_trend_velocity",
        agent=trend_scout,
    )

    crew = Crew(agents=[trend_scout], tasks=[task], process=Process.sequential, verbose=False)
    raw = str(crew.kickoff())
    parsed = _parse_json(raw)

    # Safe fallback structure
    slug = topic.lower().replace(" ", "")
    return {
        "topic": topic,
        "platform": platform,
        "hashtags": parsed.get("hashtags", [
            {"tag": f"#{slug}", "velocity": 75, "strongest_on": platform, "peak_in_hours": 8},
        ]),
        "viral_angles": parsed.get("viral_angles", [
            {"angle": f"Why {topic} is trending", "description": "Explore the reasons behind the surge", "virality_score": 75},
        ]),
        "niche_classification": parsed.get("niche_classification", "lifestyle"),
        "overall_trend_velocity": parsed.get("overall_trend_velocity", 70),
        "has_real_data": bool(real_data),
        "status": "completed",
    }


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _parse_json(raw: str) -> dict:
    try:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {}