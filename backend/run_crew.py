"""
run_crew.py — Orchestrates all CrewAI agents into a single JSON output.

Usage (Git Bash):
    python run_crew.py "Write a post about AI trends"
    python run_crew.py "Fitness morning routine" instagram motivational "gen z"
    python run_crew.py "Python tips" linkedin professional "developers"

Arguments:
    topic           (required) — The content topic/idea
    platform        (optional, default: instagram) — instagram | tiktok | youtube | linkedin | twitter
    tone            (optional, default: engaging)  — engaging | motivational | professional | funny | educational
    target_audience (optional, default: general)   — Any string describing your audience
"""

import sys
import json
import time
from datetime import datetime

# ── Path setup so imports work from any directory ─────────────────────────────
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.agents.trend_scout import run_trend_scout
from app.agents.virality_predictor import run_virality_predictor
from app.agents.content_optimizer import run_content_optimizer
from app.agents.algorithm_analyst import run_algorithm_analyst
from app.agents.strategist import run_strategist


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_step(step: str, index: int, total: int):
    bar = "█" * index + "░" * (total - index)
    print(f"\n[{bar}] Step {index}/{total} — {step}", flush=True)


def extract_virality_score(virality_result: dict) -> int:
    """
    Pull out a numeric overall virality score (0-100) from the raw LLM text.
    Falls back to 75 if parsing fails.
    """
    text = virality_result.get("virality_analysis", "")
    import re
    # Look for patterns like "Overall Virality Score: 82" or "Overall Score: 82/100"
    patterns = [
        r"overall\s+virality\s+score[:\s]+(\d{1,3})",
        r"overall\s+score[:\s]+(\d{1,3})",
        r"virality\s+score[:\s]+(\d{1,3})",
        r"(\d{1,3})\s*/\s*100",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score
    return 75  # sensible fallback


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_full_crew(
    topic: str,
    platform: str = "instagram",
    tone: str = "engaging",
    target_audience: str = "general",
) -> dict:

    total_steps = 5
    started_at = datetime.utcnow().isoformat() + "Z"
    t0 = time.time()

    print(f"\n{'='*60}")
    print(f"  🚀  CrewAI Content Engine")
    print(f"  Topic    : {topic}")
    print(f"  Platform : {platform}")
    print(f"  Tone     : {tone}")
    print(f"  Audience : {target_audience}")
    print(f"{'='*60}")

    # ── Step 1 — Trend Scout ──────────────────────────────────────────────────
    print_step("Trend Scout — finding trending signals", 1, total_steps)
    trend_result = run_trend_scout(topic, platform)

    # ── Step 2 — Content Optimizer ────────────────────────────────────────────
    print_step("Content Optimizer — writing caption & hooks", 2, total_steps)
    content_result = run_content_optimizer(topic, platform, tone, target_audience)

    # ── Step 3 — Virality Predictor ───────────────────────────────────────────
    print_step("Virality Predictor — scoring viral potential", 3, total_steps)
    virality_result = run_virality_predictor(
        topic=topic,
        caption=content_result.get("content_package", ""),
        hashtags="",
        platform=platform,
    )
    virality_score = extract_virality_score(virality_result)

    # ── Step 4 — Algorithm Analyst ────────────────────────────────────────────
    print_step("Algorithm Analyst — optimizing for the feed", 4, total_steps)
    algo_result = run_algorithm_analyst(topic, platform)

    # ── Step 5 — Strategist ───────────────────────────────────────────────────
    print_step("Strategist — building 7-day calendar & forecast", 5, total_steps)
    strategy_result = run_strategist(topic, platform, virality_score)

    elapsed = round(time.time() - t0, 1)

    # ── Assemble final JSON ───────────────────────────────────────────────────
    output = {
        "meta": {
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "target_audience": target_audience,
            "generated_at": started_at,
            "elapsed_seconds": elapsed,
        },
        "trends": trend_result.get("trends"),
        "content_package": content_result.get("content_package"),
        "virality": {
            "score": virality_score,
            "full_analysis": virality_result.get("virality_analysis"),
        },
        "algorithm_guide": algo_result.get("algo_analysis"),
        "strategy": strategy_result.get("strategy"),
        "status": "completed",
    }

    return output


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "\nUsage:\n"
            '  python run_crew.py "<topic>" [platform] [tone] [target_audience]\n\n'
            "Examples:\n"
            '  python run_crew.py "AI trends in 2026"\n'
            '  python run_crew.py "Morning fitness routine" instagram motivational "gen z"\n'
            '  python run_crew.py "Python async tips" linkedin professional "backend devs"\n'
        )
        sys.exit(1)

    topic           = sys.argv[1]
    platform        = sys.argv[2] if len(sys.argv) > 2 else "instagram"
    tone            = sys.argv[3] if len(sys.argv) > 3 else "engaging"
    target_audience = sys.argv[4] if len(sys.argv) > 4 else "general"

    result = run_full_crew(topic, platform, tone, target_audience)

    # ── Pretty-print JSON to stdout ───────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  ✅  FINAL OUTPUT JSON")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # ── Optionally save to file ───────────────────────────────────────────────
    out_file = f"crew_output_{int(time.time())}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾  Saved to: {out_file}")