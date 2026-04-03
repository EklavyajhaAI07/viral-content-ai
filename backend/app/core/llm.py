import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# LLM identifiers for CrewAI + Groq
GPT4O = "groq/llama-3.3-70b-versatile"
GPT4O_MINI = "groq/llama-3.1-8b-instant"
CLAUDE_SONNET = "groq/mixtral-8x7b-32768"

def get_groq_key():
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_your"):
        raise ValueError("❌ GROQ_API_KEY not set in .env")
    return GROQ_API_KEY
