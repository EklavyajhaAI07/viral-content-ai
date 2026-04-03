from crewai import Agent, Task, Crew, Process
from app.core.llm import GPT4O
from dotenv import load_dotenv

load_dotenv()

virality_predictor = Agent(
    role="Virality Scoring AI",
    goal="Analyze content ideas and score them from 0-100 based on viral potential",
    backstory="""You are an ML-powered virality predictor trained on millions of 
    viral posts across Instagram, TikTok, YouTube, and Twitter. You understand 
    engagement patterns, emotional triggers, timing, and platform-specific signals 
    that make content go viral. You always return structured scores with specific 
    reasoning and actionable improvements.""",
    verbose=True,
    allow_delegation=False,
    llm=GPT4O
)

def create_virality_task(topic: str, caption: str = "", hashtags: str = "", platform: str = "instagram") -> Task:
    return Task(
        description=f"""Analyze this content for viral potential:

        Topic: '{topic}'
        Caption: '{caption if caption else "Not provided - analyze topic only"}'
        Hashtags: '{hashtags if hashtags else "Not provided"}'
        Platform: {platform}

        Score each of these dimensions from 0-100:
        1. Hook Strength — how attention-grabbing is the opening?
        2. Hashtag Relevance — how well do hashtags match the content?
        3. Trend Alignment — how aligned is this with current trends?
        4. Emotional Tone — does it trigger sharing emotions?
        5. Posting Time Fit — is the timing optimal for this platform?

        Then calculate:
        - Overall Virality Score (weighted average)
        - Confidence level (0.0 to 1.0)
        - Grade (A+, A, B+, B, C+, C, D, F)
        - Predicted reach (number)
        - Predicted engagement rate (percentage)

        Finally provide:
        - 3 specific improvements to increase the score
        - 1 rewritten hook that would score higher""",
        expected_output="""Structured virality analysis with scores, grade, predicted reach, improvements and rewritten hook""",
        agent=virality_predictor
    )

def run_virality_predictor(topic: str, caption: str = "", hashtags: str = "", platform: str = "instagram") -> dict:
    task = create_virality_task(topic, caption, hashtags, platform)
    crew = Crew(
        agents=[virality_predictor],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()
    return {
        "topic": topic,
        "platform": platform,
        "virality_analysis": str(result),
        "status": "completed"
    }
