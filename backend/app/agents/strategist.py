from crewai import Agent, Task, Crew, Process
from app.core.llm import CLAUDE_SONNET
from dotenv import load_dotenv

load_dotenv()

strategist = Agent(
    role="Content Strategist",
    goal="Synthesize all agent outputs into a complete actionable content strategy with calendar and growth forecast",
    backstory="""You are a data-driven content strategist who has helped hundreds 
    of creators go from zero to viral. You take raw inputs — trends, virality scores, 
    optimized content, algorithm insights — and turn them into a crystal-clear 
    7-day content calendar with exact posting times, cross-platform repurposing plans, 
    content gaps, and growth forecasts. You think in systems, not single posts.""",
    verbose=True,
    allow_delegation=False,
    llm=CLAUDE_SONNET
)

def create_strategy_task(topic: str, platform: str = "instagram", virality_score: int = 75) -> Task:
    return Task(
        description=f"""Create a complete content strategy for:
        Topic: '{topic}'
        Primary Platform: {platform}
        Virality Score: {virality_score}/100

        Deliver ALL of the following:

        1. 7-DAY CONTENT CALENDAR
           - Day, platform, content type, topic, post time
           - At least 1 post per day across platforms

        2. CROSS-PLATFORM REPURPOSING PLAN
           - How to turn this 1 idea into 5 platform formats
           - Instagram Reel → TikTok → YouTube Short → LinkedIn → Twitter Thread

        3. FIRST WEEK GROWTH STRATEGY
           - Day 1: What to do in first 60 minutes after posting
           - Day 2-3: Follow-up engagement tactics
           - Day 4-7: Amplification strategies

        4. TOP 3 CONTENT GAPS
           - What competitors are NOT covering in this niche
           - Untapped angles with high viral potential

        5. 2 A/B TESTS TO RUN
           - Element to test, variant A vs B, success metric

        6. 30-DAY GROWTH FORECAST
           - Expected follower growth if strategy is followed
           - Expected total reach across all platforms

        Make it specific, actionable, and realistic.""",
        expected_output="Complete 7-day calendar, repurposing plan, growth strategy, content gaps, A/B tests, and 30-day forecast",
        agent=strategist
    )

def run_strategist(topic: str, platform: str = "instagram", virality_score: int = 75) -> dict:
    task = create_strategy_task(topic, platform, virality_score)
    crew = Crew(
        agents=[strategist],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()
    return {
        "topic": topic,
        "platform": platform,
        "strategy": str(result),
        "status": "completed"
    }
