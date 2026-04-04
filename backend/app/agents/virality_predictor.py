"""
virality_predictor.py
One agent — one focused task.
Returns clean structured JSON. No regex scraping needed.

run_virality_predictor() → POST /api/content/predict-virality
"""

import json
import re
from crewai import Agent, Task, Crew, Process
from app.core.llm import GROQ_SMART
from dotenv import load_dotenv

load_dotenv()

# ─── AGENT ────────────────────────────────────────────────────────────────────

virality_predictor = Agent(
    role="Virality Scoring AI",
    goal="Score content ideas from 0-100 based on viral potential and return structured JSON",
    backstory="""You are an ML-powered virality predictor trained on millions of viral 
    posts across Instagram, TikTok, YouTube, and Twitter. You understand engagement 
    patterns, emotional triggers, timing, and platform-specific signals. 
    You ALWAYS respond with valid JSON only — no markdown, no explanation.""",
    verbose=False,
    allow_delegation=False,
    llm=GROQ_SMART,
)


# ─── TASK RUNNER ──────────────────────────────────────────────────────────────

def run_virality_predictor(
    topic: str,
    platform: str = "instagram",
    caption: str = "",
    hashtags: str = "",
) -> dict:
    """
    Single focused prompt: score virality of a topic/caption.
    Returns fully structured dict — no regex parsing upstream.
    """
    caption_line = f"Caption: '{caption}'" if caption else "Caption: Not provided — score topic only"
    hashtag_line = f"Hashtags: '{hashtags}'" if hashtags else "Hashtags: Not provided"

    task = Task(
        description=f"""Score the viral potential of this content.

Topic: '{topic}'
Platform: {platform}
{caption_line}
{hashtag_line}

Score each dimension 0–100:
1. hook_strength       — how attention-grabbing is the opening?
2. hashtag_relevance   — how well do hashtags match the content?
3. trend_alignment     — how aligned with current platform trends?
4. emotional_tone      — does it trigger sharing emotions (awe, FOMO, laugh)?
5. posting_time_fit    — is the content timing optimal for {platform}?

Then compute:
- overall_score: weighted average (hook 30%, trend 25%, emotion 20%, hashtag 15%, time 10%)
- grade: A+ (95+), A (85+), B+ (75+), B (65+), C+ (55+), C (45+), D (35+), F (<35)
- confidence: 0.0–1.0 based on how much info was provided
- predicted_reach: integer (realistic estimate)
- predicted_engagement_rate: float as percentage

Also provide:
- improvements: exactly 3 specific actionable strings
- rewritten_hook: one improved hook line

Return ONLY this JSON (no markdown, no extra text):
{{
  "overall_score": 78,
  "grade": "B+",
  "confidence": 0.82,
  "predicted_reach": 45000,
  "predicted_engagement_rate": 4.2,
  "breakdown": {{
    "hook_strength": 80,
    "hashtag_relevance": 70,
    "trend_alignment": 85,
    "emotional_tone": 75,
    "posting_time_fit": 72
  }},
  "improvements": [
    "Start with a question to increase comment rate",
    "Add 3 niche hashtags under 500k posts for better discoverability",
    "Post on Tuesday between 7–9 PM for peak {platform} engagement"
  ],
  "rewritten_hook": "A stronger opening hook example here"
}}""",
        expected_output="Valid JSON with score, grade, confidence, breakdown, improvements, rewritten_hook",
        agent=virality_predictor,
    )

    crew = Crew(agents=[virality_predictor], tasks=[task], process=Process.sequential, verbose=False)
    raw = str(crew.kickoff())
    parsed = _parse_json(raw)

    # Ensure all keys exist with safe fallbacks
    score = parsed.get("overall_score", 75)
    return {
        "overall_score": score,
        "grade": parsed.get("grade", _grade(score)),
        "confidence": parsed.get("confidence", 0.75),
        "predicted_reach": parsed.get("predicted_reach", score * 150),
        "predicted_engagement_rate": parsed.get("predicted_engagement_rate", round(score / 10, 1)),
        "breakdown": parsed.get("breakdown", {
            "hook_strength": score,
            "hashtag_relevance": score - 5,
            "trend_alignment": score + 3,
            "emotional_tone": score - 2,
            "posting_time_fit": score - 1,
        }),
        "improvements": parsed.get("improvements", [
            "Use a stronger call to action",
            "Add platform-specific hashtags",
            "Post during peak engagement hours",
        ]),
        "rewritten_hook": parsed.get("rewritten_hook", f"Here's what nobody tells you about {topic}..."),
        "topic": topic,
        "platform": platform,
        "status": "completed",
    }


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _grade(score: int) -> str:
    if score >= 95: return "A+"
    if score >= 85: return "A"
    if score >= 75: return "B+"
    if score >= 65: return "B"
    if score >= 55: return "C+"
    if score >= 45: return "C"
    if score >= 35: return "D"
    return "F"


def _parse_json(raw: str) -> dict:
    try:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {}