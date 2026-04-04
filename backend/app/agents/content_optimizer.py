"""
content_optimizer.py
One agent — three focused task runners.
Each runner has ONE prompt, ONE job, returns structured JSON.

run_hook_only()      → POST /api/content/hook
run_caption_only()   → POST /api/content/caption
run_hashtags_only()  → POST /api/content/hashtags
"""

import json
import re
from crewai import Agent, Task, Crew, Process
from app.core.llm import GROQ_SMART
from dotenv import load_dotenv

load_dotenv()

# ─── SHARED AGENT ─────────────────────────────────────────────────────────────
# One agent, different tasks per endpoint

content_optimizer = Agent(
    role="Content Optimizer",
    goal="Write high-converting social media content optimized for maximum reach",
    backstory="""You are a world-class copywriter who has helped creators grow from 
    0 to millions of followers. You write platform-native content that stops the 
    scroll. You always respond ONLY in valid JSON — no markdown, no extra text.""",
    verbose=False,
    allow_delegation=False,
    llm=GROQ_SMART,
)


# ─── TASK 1: HOOK ONLY ────────────────────────────────────────────────────────

def run_hook_only(
    topic: str,
    platform: str = "instagram",
    tone: str = "engaging",
    target_audience: str = "general",
) -> dict:
    """
    Single focused prompt: generate hooks only.
    Returns: { hook, alternative_hooks, cta, format_recommendation }
    """
    task = Task(
        description=f"""Write scroll-stopping hooks for this content.

Topic: '{topic}'
Platform: {platform}
Tone: {tone}
Target Audience: {target_audience}

Platform hook rules:
- Instagram/TikTok: Emotionally charged, curiosity gap, max 2 lines
- YouTube: Bold claim or question in first 5 seconds
- LinkedIn: Insight-led, contrarian or data-backed opener

Return ONLY this JSON (no markdown, no explanation):
{{
  "hook": "the single best hook line",
  "alternative_hooks": [
    "angle 1 — curiosity gap",
    "angle 2 — bold statement",
    "angle 3 — story opener"
  ],
  "cta": "one clear call-to-action sentence",
  "format_recommendation": "Reel|Post|Story|Short|Thread|Video"
}}""",
        expected_output='JSON with hook, alternative_hooks array, cta, format_recommendation',
        agent=content_optimizer,
    )

    crew = Crew(agents=[content_optimizer], tasks=[task], process=Process.sequential, verbose=False)
    raw = str(crew.kickoff())
    return _parse_json(raw, fallback={
        "hook": f"You won't believe what happened with {topic}...",
        "alternative_hooks": [
            f"The truth about {topic} nobody tells you",
            f"I tried {topic} for 30 days — here's what happened",
            f"Stop doing {topic} wrong. Here's why:",
        ],
        "cta": "Save this post and try it today!",
        "format_recommendation": "Reel",
    })


# ─── TASK 2: CAPTION ONLY ─────────────────────────────────────────────────────

def run_caption_only(
    topic: str,
    platform: str = "instagram",
    tone: str = "engaging",
    target_audience: str = "general",
    hook: str = "",
) -> dict:
    """
    Single focused prompt: generate a full platform-native caption.
    Accepts optional hook to continue from.
    Returns: { caption, best_posting_time, word_count }
    """
    hook_context = f"\nOpen with this hook: \"{hook}\"" if hook else ""

    platform_rules = {
        "instagram": "150-300 words, storytelling arc, 3-5 emojis, line breaks for readability",
        "tiktok": "50-100 words, punchy, trend-native slang, energetic",
        "youtube": "SEO-optimised title (60 chars) + 150-200 word description with keywords",
        "linkedin": "100-150 words, professional, insight-driven, no emojis",
        "twitter": "Under 280 chars, punchy, one strong opinion or hook",
    }
    rules = platform_rules.get(platform.lower(), platform_rules["instagram"])

    task = Task(
        description=f"""Write a full {platform} caption for this topic.

Topic: '{topic}'
Tone: {tone}
Target Audience: {target_audience}{hook_context}

Caption rules for {platform}: {rules}

Return ONLY this JSON (no markdown, no explanation):
{{
  "caption": "the full caption text here",
  "best_posting_time": "e.g. Tuesday 7-9pm",
  "word_count": 180
}}""",
        expected_output='JSON with caption, best_posting_time, word_count',
        agent=content_optimizer,
    )

    crew = Crew(agents=[content_optimizer], tasks=[task], process=Process.sequential, verbose=False)
    raw = str(crew.kickoff())
    return _parse_json(raw, fallback={
        "caption": f"Here's everything you need to know about {topic}. This changed how I think about content completely. Drop a 🔥 if you agree!",
        "best_posting_time": "Tuesday–Thursday, 7–9 PM",
        "word_count": 25,
    })


# ─── TASK 3: HASHTAGS ONLY ────────────────────────────────────────────────────

def run_hashtags_only(
    topic: str,
    platform: str = "instagram",
) -> dict:
    """
    Single focused prompt: generate a 3-tier hashtag strategy.
    Returns: { niche, trending, broad, total_count }
    """
    task = Task(
        description=f"""Create a 3-tier hashtag strategy for {platform}.

Topic: '{topic}'
Platform: {platform}

Tier rules:
- niche: 5 hashtags, under 500k posts, very specific to the topic
- trending: 5 hashtags, 500k–5M posts, currently popular in this niche
- broad: 5 hashtags, 5M+ posts, wide reach

Return ONLY this JSON (no markdown, no explanation):
{{
  "niche": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "trending": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "broad": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "total_count": 15
}}""",
        expected_output='JSON with niche, trending, broad arrays and total_count',
        agent=content_optimizer,
    )

    crew = Crew(agents=[content_optimizer], tasks=[task], process=Process.sequential, verbose=False)
    raw = str(crew.kickoff())
    slug = topic.lower().replace(" ", "")
    return _parse_json(raw, fallback={
        "niche": [f"#{slug}tips", f"#{slug}life", f"#{slug}hack", f"#{slug}daily", f"#{slug}101"],
        "trending": [f"#{slug}", f"#{platform}{slug.title()}", "#ContentCreator", "#Viral2025", "#TrendingNow"],
        "broad": ["#viral", "#explore", "#reels", "#trending", "#fyp"],
        "total_count": 15,
    })


# ─── JSON PARSER ──────────────────────────────────────────────────────────────

def _parse_json(raw: str, fallback: dict) -> dict:
    """Safely extract JSON from LLM output. Falls back to safe defaults."""
    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        # Find first { ... } block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return fallback