"""
algorithm_analyst.py — Platform algorithm analyst agent.

Upgraded with:
  - [1] Skillset-aware prompting (platform rules injected)
  - [4] Geo-aware algorithm signals
  - [7] Receives shared context from previous agents (trend data, content)
  - [8] Uses model router for LLM selection
"""

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

from app.core.llm import get_model_for_task, GPT4O
from app.core.skillsets import resolve_skillset, skillset_to_prompt_block
from app.core.geo import GeoContext, geo_to_prompt_block

load_dotenv()


# ── Agent definition ──────────────────────────────────────────────────────────

algorithm_analyst = Agent(
    role="Algorithm Analyst",
    goal="Analyze platform-specific algorithm signals and optimize content for maximum algorithmic reach",
    backstory="""You are a deep expert in social media algorithms — Instagram Reels, 
    TikTok FYP, YouTube Shorts, Twitter/X feed, and LinkedIn feed. You know exactly 
    what signals each algorithm rewards: watch time, saves, shares, comments, CTR, 
    and early engagement windows. You reverse-engineer why content goes viral and 
    give specific, actionable optimization tips.""",
    verbose=True,
    allow_delegation=False,
    llm=GPT4O,  # falls back gracefully if not available
)


# ── Task factory (with shared context support) ────────────────────────────────

def create_algo_task(
    topic: str,
    platform: str = "instagram",
    geo: GeoContext = None,
    shared_context: dict = None,
    model_override: str = None,
) -> Task:
    """
    Creates an algorithm analysis task, injecting:
      - Skillset rules for the platform
      - Geo context (peak hours, regional platform preferences)
      - Shared context from previous agents (trend data etc.)
    """
    skillset      = resolve_skillset(platform, audience=getattr(geo, "content_style", "global"))
    skillset_block = skillset_to_prompt_block(skillset)
    geo_block     = geo_to_prompt_block(geo) if geo else ""

    # Build shared context summary if previous agents ran
    context_summary = ""
    if shared_context:
        trends   = shared_context.get("trends", {})
        hashtags = trends.get("suggested_hashtags", []) if isinstance(trends, dict) else []
        context_summary = f"""
=== CONTEXT FROM PREVIOUS AGENTS ===
Trending hashtags already identified: {', '.join(hashtags[:8]) or 'none'}
Rising topics: {', '.join(trends.get('rising_topics', [])[:5]) if isinstance(trends, dict) else 'none'}
=== END CONTEXT ===
"""

    description = f"""
{skillset_block}
{geo_block}
{context_summary}

Analyze how to maximize algorithmic reach for this content on {platform}:
Topic: '{topic}'

Provide ALL of the following:
1. TOP 5 algorithm signals to optimize for on {platform} (specific to 2026)
2. CONTENT FORMAT the algorithm currently favors (Reel/Short/Thread/etc.)
3. OPTIMAL LENGTH — duration in seconds (video) or word count (text)
4. FIRST 60 MINUTES strategy — exactly what to do after posting
5. ENGAGEMENT TRIGGERS to embed in the content itself
6. 5 things to AVOID that hurt algorithmic reach on {platform}
7. BEST DAY + TIME to post (use peak hours from geo context above if provided)
8. Estimated organic reach multiplier if all tips followed
9. HOOK format that the {platform} algorithm currently boosts

Ground your analysis in the platform skillset rules above.
Be specific to {platform}'s current algorithm behavior in 2026.
"""

    return Task(
        description=description,
        expected_output=(
            "Structured algorithm optimization guide with: signals, format, "
            "timing, engagement triggers, avoids, reach estimate. "
            "Format as numbered sections matching the 9 points above."
        ),
        agent=algorithm_analyst,
    )


# ── Runner ────────────────────────────────────────────────────────────────────

def run_algorithm_analyst(
    topic: str,
    platform: str = "instagram",
    geo: GeoContext = None,
    shared_context: dict = None,
    model_override: str = None,
) -> dict:
    """
    Run the algorithm analyst agent.

    Args:
        topic:          Content topic
        platform:       Target platform
        geo:            GeoContext from geo.py (optional)
        shared_context: Output dict from earlier agents (trend_scout etc.)
        model_override: "groq-fast" | "groq-smart" | "claude-sonnet" | None
    """
    # Dynamic model selection
    if model_override:
        from app.core.llm import get_model_by_name
        algorithm_analyst.llm = get_model_by_name(model_override)
    else:
        algorithm_analyst.llm = get_model_for_task("algorithm_analyst")

    task = create_algo_task(topic, platform, geo, shared_context, model_override)

    crew = Crew(
        agents=[algorithm_analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "topic":        topic,
        "platform":     platform,
        "algo_analysis": str(result),
        "geo":          geo.country if geo else "global",
        "status":       "completed",
    }