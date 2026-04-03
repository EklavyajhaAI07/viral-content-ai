from crewai import Agent, Task, Crew, Process
from app.core.llm import GPT4O_MINI
from dotenv import load_dotenv
import os

load_dotenv()

# ─── AGENT ────────────────────────────────────────────

trend_scout = Agent(
    role="Trend Scout",
    goal="Find the latest trending topics, hashtags, and viral content patterns on social media",
    backstory="""You are an expert social media analyst who tracks viral trends 
    across Instagram, TikTok, YouTube, and Twitter in real time. You know what 
    content is blowing up right now and why. You classify trends by niche and 
    score them by velocity — how fast they are growing.""",
    verbose=True,
    allow_delegation=False,
    llm=GPT4O_MINI
)

# ─── TASK FACTORY ─────────────────────────────────────

def create_trend_task(topic: str, platform: str = "all") -> Task:
    return Task(
        description=f"""Research current trending topics related to: '{topic}'
        Platform focus: {platform}
        
        Find and return:
        1. Top 10 trending hashtags related to this topic right now
        2. Current viral content patterns in this niche
        3. Velocity score for each trend (0-100, how fast it's growing)
        4. Which platforms each trend is strongest on
        5. Predicted peak time in hours (when will it peak?)
        6. Niche classification (tech/fashion/food/fitness/finance/entertainment)
        
        Format your response as structured data.""",
        expected_output="""A structured list of 10 trends, each with:
        - topic name
        - hashtags (list)
        - platforms (list) 
        - velocity_score (0-100)
        - niche
        - peak_prediction_hours (number)""",
        agent=trend_scout
    )

# ─── RUNNER ───────────────────────────────────────────

def run_trend_scout(topic: str, platform: str = "all") -> dict:
    task = create_trend_task(topic, platform)
    
    crew = Crew(
        agents=[trend_scout],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    
    return {
        "topic": topic,
        "platform": platform,
        "trends": str(result),
        "status": "completed"
    }
