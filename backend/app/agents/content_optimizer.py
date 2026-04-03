from crewai import Agent, Task, Crew, Process
from app.core.llm import CLAUDE_SONNET
from dotenv import load_dotenv

load_dotenv()

# ─── AGENT ────────────────────────────────────────────

content_optimizer = Agent(
    role="Content Optimizer",
    goal="Write high-converting captions, hooks, and hashtags optimized for maximum reach on every platform",
    backstory="""You are a world-class copywriter and content strategist who has 
    helped creators grow from 0 to millions of followers. You write captions that 
    stop the scroll, hooks that demand attention, and build hashtag strategies that 
    maximize discoverability. You adapt your tone and format natively for each 
    platform — Instagram, TikTok, YouTube, and LinkedIn all have different languages 
    and you speak all of them fluently.""",
    verbose=True,
    allow_delegation=False,
    llm=CLAUDE_SONNET
)

# ─── TASK FACTORY ─────────────────────────────────────

def create_content_task(topic: str, platform: str = "instagram", tone: str = "engaging", target_audience: str = "general") -> Task:
    return Task(
        description=f"""Create fully optimized content for this topic:

        Topic: '{topic}'
        Primary Platform: {platform}
        Tone: {tone}
        Target Audience: {target_audience}

        Deliver ALL of the following:

        1. HOOK (first 1-2 lines that stop the scroll)
        2. FULL CAPTION optimized for {platform}
           - Instagram: 150-300 words, storytelling style, emojis
           - TikTok: 50-100 words, punchy, trend-native language
           - YouTube: SEO title + 200 word description
           - LinkedIn: Professional tone, insight-driven, 100-150 words
        3. HASHTAG STRATEGY (15 total):
           - 5 niche hashtags (under 500k posts)
           - 5 trending hashtags (500k-5M posts)
           - 5 broad hashtags (5M+ posts)
        4. CTA (call to action — what should the viewer do?)
        5. 3 ALTERNATIVE HOOKS (different angles)
        6. BEST POSTING TIME for {platform}
        7. CONTENT FORMAT recommendation (Reel/Post/Story/Short/Thread)

        Make it authentic, platform-native, and conversion-focused.""",
        expected_output="""Complete content package with hook, full caption, 
        15 hashtags in 3 tiers, CTA, 3 alternative hooks, best posting time, 
        and format recommendation.""",
        agent=content_optimizer
    )

# ─── RUNNER ───────────────────────────────────────────

def run_content_optimizer(topic: str, platform: str = "instagram", tone: str = "engaging", target_audience: str = "general") -> dict:
    task = create_content_task(topic, platform, tone, target_audience)

    crew = Crew(
        agents=[content_optimizer],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return {
        "topic": topic,
        "platform": platform,
        "content_package": str(result),
        "status": "completed"
    }
