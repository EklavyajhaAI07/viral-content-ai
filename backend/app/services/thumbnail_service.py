import os
import re
import httpx
import logging
import tempfile
import urllib.parse
import random
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────
STABILITY_API_KEY = "sk-p8hwXR82EXldrBWwD2xPYyA5Vgin6svQGYUjNIP9NEnVvp3h"

PLATFORM_STYLES = {
    "instagram": "cinematic fitness influencer, luxury gym Mumbai, 8k, vertical 9:16",
    "tiktok": "viral aesthetic, neon vaporwave lighting, futuristic tech, 9:16",
    "youtube": "high contrast, dramatic wide shot, vibrant colors, 16:9",
}

# ── Method 1: Stability AI (Premium) ──────────────────

async def generate_via_stability(prompt: str, aspect_ratio: str = "1:1") -> dict:
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY.strip()}",
        "accept": "image/*"
    }
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "aspect_ratio": (None, aspect_ratio),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, files=files)
            
            # If 402 (No Credits), return specific error for fallback
            if response.status_code == 402:
                return {"error": "402", "msg": "Insufficient Credits"}
            
            if response.status_code != 200:
                return {"error": str(response.status_code)}
            
            return save_local_image(response.content, "stability")
    except Exception as e:
        return {"error": "connection_fail", "msg": str(e)}

# ── Method 2: Pollinations (Stable Fallback) ──────────

async def generate_via_pollinations(prompt: str, platform: str) -> dict:
    aspect_params = "&width=1024&height=1024" # Default
    if platform == "youtube": aspect_params = "&width=1280&height=720"
    elif platform in ["instagram", "tiktok"]: aspect_params = "&width=720&height=1280"

    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 999999)
    # Using 'flux' model for high quality and stability
    url = f"https://image.pollinations.ai/prompt/{encoded}?seed={seed}{aspect_params}&model=flux&nologo=true"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            return save_local_image(res.content, "pollinations")
    except Exception as e:
        return {"error": str(e)}

# ── Utilities ─────────────────────────────────────────

def save_local_image(content: bytes, source: str) -> dict:
    output_dir = "outputs"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/{source}_{ts}.png"
    filepath = os.path.abspath(filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
        
    return {"url": f"file://{filepath}", "path": filepath, "status": "ok", "source": source}

# ── Main Entry Point ──────────────────────────────────

async def generate_thumbnail(topic: str, platform: str = "instagram", **kwargs) -> dict:
    style = PLATFORM_STYLES.get(platform, PLATFORM_STYLES["instagram"])
    full_prompt = f"Professional viral thumbnail for '{topic}'. {style}. High detail, 8k."
    
    # Map aspect ratio for Stability
    target_aspect = "16:9" if platform == "youtube" else "9:16" if platform in ["instagram", "tiktok"] else "1:1"

    # Step 1: Try Stability
    logger.info("Attempting Stability AI...")
    result = await generate_via_stability(full_prompt, target_aspect)

    # Step 2: Check for 402 (Credits) or other errors
    if "error" in result:
        error_type = result.get("error")
        logger.warning(f"Stability failed ({error_type}). Falling back to Pollinations FLUX...")
        
        # Step 3: Use the robust Pollinations-Flux fallback
        result = await generate_via_pollinations(full_prompt, platform)

    return result

'backend\app\services\thumbnail_service.py'