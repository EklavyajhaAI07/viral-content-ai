from crewai import Agent, Task, Crew, Process
from app.core.llm import GPT4O
from dotenv import load_dotenv

load_dotenv()

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
    llm=GPT4O
)

def create_algo_task(topic: str, platform: str = "instagram") -> Task:
    return Task(
        description=f"""Analyze how to maximize algorithmic reach for this content on {platform}:
        Topic: '{topic}'

        Provide:
        1. TOP 5 algorithm signals to optimize for on {platform}
        2. CONTENT FORMAT that algorithm currently favors (Reel/Short/Thread etc.)
        3. OPTIMAL LENGTH (duration in seconds or word count)
        4. FIRST 60 MINUTES strategy (what to do right after posting)
        5. ENGAGEMENT TRIGGERS to include in the content
        6. 5 things to AVOID that hurt algorithmic reach
        7. BEST DAY + TIME to post for maximum initial push
        8. Estimated organic reach multiplier if all tips are followed

        Be specific to {platform}'s current algorithm behavior in 2026.""",
        expected_output="Complete algorithm optimization guide with signals, format, timing, and engagement strategy",
        agent=algorithm_analyst
    )

def run_algorithm_analyst(topic: str, platform: str = "instagram") -> dict:
    task = create_algo_task(topic, platform)
    crew = Crew(
        agents=[algorithm_analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()
    return {
        "topic": topic,
        "platform": platform,
        "algo_analysis": str(result),
        "status": "completed"
    }
