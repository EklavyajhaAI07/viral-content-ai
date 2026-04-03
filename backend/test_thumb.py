import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# 1. Manually resolve the .env path to the current working directory
env_path = Path('.') / '.env'
print(f"🔍 DEBUG: Looking for .env at: {env_path.absolute()}")

# 2. Check if file exists and load it
if not env_path.exists():
    print("❌ ERROR: The .env file was NOT found in the current directory.")
    print(f"Directory Contents: {os.listdir('.')}")
else:
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file loaded successfully.")

from app.services.thumbnail_service import generate_thumbnail

async def main():
    print("🚀 Initializing Thumbnail Generator...")
    
    # 3. Retrieve the key
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY is still empty in the environment.")
        # Show all loaded keys containing 'API' to check for typos
        loaded_keys = [k for k in os.environ.keys() if "API" in k]
        print(f"🔍 Loaded API keys found: {loaded_keys}")
        return

    # 4. Run the generator using your OpenRouter Key
    print(f"📡 Connecting to OpenRouter using key: {api_key[:10]}***")
    
    result = await generate_thumbnail(
        topic="AI fitness trends",
        platform="instagram",
        tone="motivational"
    )
    
    print("\n🎬 === FINAL RESULT ===")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())