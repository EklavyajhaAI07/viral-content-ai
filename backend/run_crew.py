"""
run_crew.py — Orchestrates all CrewAI agents into a single JSON output.

Upgraded with:
  [1] Platform skillset injection into every agent
  [2] Website subset crawling per platform
  [3] Score memory cache (assign + recall via Redis sync)
  [4] Geo/location-aware content signals
  [5] MongoDB document schema (output includes _mongo_doc for storage)
  [6] Web crawling integrated into trend engine
  [7] Shared context bus — each agent receives previous agents' outputs
  [8] Multi-model selection (user can choose or auto-route)
  [9] Token limit guard (built into llm.py)
  [10] Free thumbnail generation via Pollinations.ai

Usage:
    python run_crew.py "Write a post about AI trends"
    python run_crew.py "Fitness routine" instagram motivational "gen z" "Mumbai, India" groq-smart
    python run_crew.py "Python tips" linkedin professional "developers" "US" claude-sonnet

Arguments:
    topic           (required)
    platform        (optional, default: instagram)
    tone            (optional, default: engaging)
    target_audience (optional, default: general)
    location        (optional, default: global) — e.g. "Mumbai, India" or "US"
    model           (optional, default: auto)   — groq-fast | groq-smart | claude-sonnet | auto
"""

import sys
import json
import time
import asyncio
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime

# ── Core modules ──────────────────────────────────────────────────────────────
from app.core.llm import describe_available_models
from app.core.skillsets import resolve_skillset, skillset_to_prompt_block
from app.core.geo import resolve_geo_from_string
from app.core.redis_client import sync_cache, build_key, NS

# ── Agents ────────────────────────────────────────────────────────────────────
from app.agents.trend_scout import run_trend_scout
from app.agents.virality_predictor import run_virality_predictor
from app.agents.content_optimizer import run_content_optimizer
from app.agents.algorithm_analyst import run_algorithm_analyst
from app.agents.strategist import run_strategist

# ── Services ──────────────────────────────────────────────────────────────────
from app.services.thumbnail_service import generate_thumbnail


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_step(step: str, index: int, total: int, cached: bool = False):
    bar    = "█" * index + "░" * (total - index)
    suffix = " [CACHED]" if cached else ""
    print(f"\n[{bar}] Step {index}/{total} — {step}{suffix}", flush=True)


def extract_virality_score(virality_result: dict) -> int:
    import re
    text = virality_result.get("virality_analysis", "")
    patterns = [
        r"overall\s+virality\s+score[:\s]+(\d{1,3})",
        r"overall\s+score[:\s]+(\d{1,3})",
        r"virality\s+score[:\s]+(\d{1,3})",
        r"(\d{1,3})\s*/\s*100",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            s = int(m.group(1))
            if 0 <= s <= 100:
                return s
    return 75


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_full_crew(
    topic: str,
    platform: str = "instagram",
    tone: str = "engaging",
    target_audience: str = "general",
    location: str = "global",
    model: str = "auto",
) -> dict:

    total_steps = 7   # 5 agents + thumbnail + assembly
    started_at  = datetime.utcnow().isoformat() + "Z"
    t0          = time.time()

    # ── Resolve skillset + geo ────────────────────────────────────────────────
    skillset = resolve_skillset(platform, tone, target_audience)
    geo      = resolve_geo_from_string(location)

    # Model override (None = auto)
    model_override = None if model == "auto" else model

    print(f"\n{'='*60}")
    print(f"  🚀  CrewAI Content Engine — Phase 5 Upgraded")
    print(f"  Topic    : {topic}")
    print(f"  Platform : {platform}  ({skillset.format_type})")
    print(f"  Tone     : {tone}")
    print(f"  Audience : {target_audience}")
    print(f"  Location : {geo.country} ({geo.content_style})")
    print(f"  Model    : {model}")
    print(f"  Available: {describe_available_models()}")
    print(f"{'='*60}")

    # ── Shared context bus — accumulates agent outputs ────────────────────────
    shared_ctx = {
        "topic":       topic,
        "platform":    platform,
        "tone":        tone,
        "audience":    target_audience,
        "geo":         {
            "country":      geo.country,
            "country_code": geo.country_code,
            "timezone":     geo.timezone,
            "style":        geo.content_style,
            "peak_hours":   geo.peak_hours_utc,
            "language":     geo.language,
        },
        "skillset":    {
            "format":          skillset.format_type,
            "ideal_length":    skillset.ideal_length,
            "hashtag_count":   skillset.hashtag_count,
            "algo_priority":   skillset.algo_priority,
            "viral_patterns":  skillset.viral_patterns,
            "best_post_times": skillset.best_post_times,
        },
    }

    # ── Step 1 — Trend Scout (with geo + crawl) ───────────────────────────────
    print_step("Trend Scout — geo-aware trends + web crawl", 1, total_steps)
    trend_result = run_trend_scout(
        topic, platform,
        geo=geo,
        shared_context=shared_ctx,
        model_override=model_override,
    )
    shared_ctx["trends"] = trend_result

    # ── Step 2 — Algorithm Analyst (reads trends from ctx) ────────────────────
    print_step("Algorithm Analyst — platform algo signals", 2, total_steps)
    algo_result = run_algorithm_analyst(
        topic, platform,
        geo=geo,
        shared_context=shared_ctx,
        model_override=model_override,
    )
    shared_ctx["algo"] = algo_result

    # ── Step 3 — Content Optimizer (reads trends + algo) ─────────────────────
    print_step("Content Optimizer — caption, hooks, hashtags", 3, total_steps)
    content_result = run_content_optimizer(
        topic, platform, tone, target_audience,
        geo=geo,
        shared_context=shared_ctx,
        model_override=model_override,
    )
    shared_ctx["content"] = content_result

    # ── Step 4 — Virality Predictor (check score cache first) ────────────────
    print_step("Virality Predictor — score with cache check", 4, total_steps)

    cached_score = sync_cache.recall_score(topic, platform)
    if cached_score and not cached_score.get("from_cache") is False:
        print(f"  ✓ Score cache hit: {cached_score['score']}/100 (skipping LLM call)")
        virality_score   = cached_score["score"]
        virality_result  = {
            "virality_analysis": f"[Cached] Score: {virality_score}",
            "from_cache": True,
        }
    else:
        virality_result = run_virality_predictor(
            topic=topic,
            caption=content_result.get("content_package", ""),
            hashtags=", ".join(
                shared_ctx.get("trends", {}).get("trends", {}).get("suggested_hashtags", [])[:5]
                if isinstance(shared_ctx.get("trends", {}).get("trends"), dict) else []
            ),
            platform=platform,
            geo=geo,
            shared_context=shared_ctx,
            model_override=model_override,
        )
        virality_score = extract_virality_score(virality_result)
        virality_result["from_cache"] = False

        # Persist score to cache + leaderboard
        sync_cache.assign_score(topic, platform, virality_score)
        sync_cache.update_leaderboard(platform, topic, virality_score)
        print(f"  ✓ Score computed + cached: {virality_score}/100")

    shared_ctx["virality_score"] = virality_score
    shared_ctx["virality"]       = virality_result

    # ── Step 5 — Strategist (reads everything) ────────────────────────────────
    print_step("Strategist — 7-day calendar + forecast", 5, total_steps)
    strategy_result = run_strategist(
        topic, platform, virality_score,
        geo=geo,
        shared_context=shared_ctx,
        model_override=model_override,
    )
    shared_ctx["strategy"] = strategy_result

    # ── Step 6 — Thumbnail generation (free, async) ───────────────────────────
    print_step("Thumbnail Generator — free image via Pollinations", 6, total_steps)
    caption_hint = ""
    pkg = content_result.get("content_package", "")
    if pkg and len(pkg) > 10:
        # Use first line of caption as text hint
        caption_hint = pkg.split("\n")[0][:40]

    thumbnail = asyncio.run(
        generate_thumbnail(
            topic=topic,
            platform=platform,
            tone=tone,
            caption_hint=caption_hint,
            colors=skillset.thumbnail_colors,
        )
    )

    # ── Step 7 — Assemble output ──────────────────────────────────────────────
    print_step("Assembling final JSON", 7, total_steps)
    elapsed = round(time.time() - t0, 1)

    # Top topics leaderboard snapshot
    top_topics = sync_cache.get_top_topics(platform, limit=5)

    output = {
        "meta": {
            "topic":           topic,
            "platform":        platform,
            "tone":            tone,
            "target_audience": target_audience,
            "location":        geo.country,
            "geo_style":       geo.content_style,
            "language":        geo.language,
            "model":           model,
            "generated_at":    started_at,
            "elapsed_seconds": elapsed,
        },
        "skillset": {
            "format":          skillset.format_type,
            "ideal_length":    skillset.ideal_length,
            "hashtag_count":   skillset.hashtag_count,
            "best_post_times": geo.peak_hours_utc or skillset.best_post_times,
            "thumbnail_style": skillset.thumbnail_style,
        },
        "trends":          trend_result.get("trends"),
        "content_package": content_result.get("content_package"),
        "virality": {
            "score":        virality_score,
            "from_cache":   virality_result.get("from_cache", False),
            "full_analysis":virality_result.get("virality_analysis"),
        },
        "algorithm_guide": algo_result.get("algo_analysis"),
        "strategy":        strategy_result.get("strategy"),
        "thumbnail":       thumbnail,
        "leaderboard":     top_topics,
        "status":          "completed",
    }

    return output


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "\nUsage:\n"
            '  python run_crew.py "<topic>" [platform] [tone] [audience] [location] [model]\n\n'
            "Examples:\n"
            '  python run_crew.py "AI trends"\n'
            '  python run_crew.py "Morning fitness" instagram motivational "gen z" "Mumbai, India"\n'
            '  python run_crew.py "Python tips" linkedin professional "backend devs" "US" claude-sonnet\n\n'
            "Models: groq-fast | groq-smart | groq-long | claude-haiku | claude-sonnet | auto\n"
        )
        sys.exit(1)

    topic           = sys.argv[1]
    platform        = sys.argv[2] if len(sys.argv) > 2 else "instagram"
    tone            = sys.argv[3] if len(sys.argv) > 3 else "engaging"
    target_audience = sys.argv[4] if len(sys.argv) > 4 else "general"
    location        = sys.argv[5] if len(sys.argv) > 5 else "global"
    model           = sys.argv[6] if len(sys.argv) > 6 else "auto"

    result = run_full_crew(topic, platform, tone, target_audience, location, model)

    print(f"\n{'='*60}")
    print("  ✅  FINAL OUTPUT JSON")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    out_file = f"crew_output_{int(time.time())}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾  Saved to: {out_file}")