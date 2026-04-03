import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Fast model — for trend research, classification
GPT4O_MINI = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0.7
)

# Smart model — for virality scoring, analysis
GPT4O = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.7
)

# Creative model — for content writing, strategy
CLAUDE_SONNET = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.9
)

def get_groq_key():
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_your"):
        raise ValueError("❌ GROQ_API_KEY not set in .env")
    return GROQ_API_KEY
