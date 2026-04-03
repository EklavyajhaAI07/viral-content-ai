from crewai import Agent, Task, Crew, Process
from app.core.llm import GPT4O_MINI
from dotenv import load_dotenv

load_dotenv()

trend_scout = Agent(
    role="Trend Scout",
    goal="Analyze real social media trend data and extract actionable viral insights",
    backstory="""You are an expert social media analyst who interprets real-time 
    trend data from Google Trends and YouTube. You receive actual live data and 
    extract the most viral patterns, score velocity, and predict peak timing. 
    You classify trends by niche and give specific hashtag recommendations.""",
    verbose=False,
    allow_delegation=False,
    llm=GPT4O_MINI,
)


def create_trend_task(topic: str, platform: str = "all", real_data: dict = None, geo=None, shared_context: dict = None) -> Task:
    data_context = ""
    if real_data:
        yt_videos = real_data.get("youtube_trending", {}).get("videos", [])[:5]
        yt_titles = [v["title"] for v in yt_videos]
        rising    = real_data.get("rising_topics", [])
        hashtags  = real_data.get("suggested_hashtags", [])
        google_q  = [q["query"] for q in real_data.get("google_trends", {}).get("related_queries", [])]

        data_context = f"""
REAL-TIME DATA (use this as your primary source):

Google Trends Rising Queries: {', '.join(google_q[:10])}
Rising Topics: {', '.join(rising[:5])}
Suggested Hashtags from Google: {', '.join(hashtags[:10])}

YouTube Trending Videos (last 3 days):
{chr(10).join(f'- {t}' for t in yt_titles)}
"""

    # Inject the Orchestrator's new Geo and Context data
    geo_info = ""
    if geo:
        geo_info = f"\nGeo Target: {getattr(geo, 'country', 'global')} | Style: {getattr(geo, 'content_style', 'global')}"

    context_info = ""
    if shared_context:
        context_info = f"\nAudience: {shared_context.get('audience')} | Tone: {shared_context.get('tone')}"

    return Task(
        description=f"""Analyze trend data for: '{topic}' on {platform}.
{geo_info}{context_info}
{data_context}

Using the real data above, provide:
1. Top 10 trending hashtags (mix real ones from data + your analysis)
2. Viral content patterns emerging RIGHT NOW in this niche
3. Velocity score for each trend (0-100)
4. Which platforms each trend is strongest on
5. Predicted peak time in hours
6. Niche classification
7. Top 3 content angles with highest viral potential

Format as structured data.""",
        expected_output="""Structured trend report with 10 hashtags, velocity scores, 
        platform breakdown, peak predictions, and 3 viral content angles.""",
        agent=trend_scout,
    )


def run_trend_scout(
    topic: str, 
    platform: str = "all", 
    real_data: dict = None,
    geo=None,
    shared_context: dict = None,
    model_override: str = None
) -> dict:
    
    # Pass the new context down into the task
    task = create_trend_task(topic, platform, real_data, geo, shared_context)
    
    crew = Crew(
        agents=[trend_scout],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )
    
    result = crew.kickoff()
    
    return {
        "topic": topic,
        "platform": platform,
        "geo": getattr(geo, "country", "global") if geo else "global",
        "trends": str(result),
        "status": "completed",
    }