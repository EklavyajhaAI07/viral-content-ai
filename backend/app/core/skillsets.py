"""
skillsets.py — Platform-aware skillset resolver.

Maps (platform, tone, audience) → structured content rules that every agent
receives as context. Also defines which website subsets to crawl per platform.

Usage:
    from app.core.skillsets import resolve_skillset, get_platform_crawl_targets

    skillset = resolve_skillset("instagram", "motivational", "gen z")
    targets  = get_platform_crawl_targets("instagram")
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class ContentSkillset:
    platform: str
    tone: str
    audience: str

    # Format rules
    ideal_length: str          # e.g. "15-30 seconds" or "150-220 words"
    format_type: str           # Reel | Short | Thread | Post | Article
    aspect_ratio: str          # "9:16" | "1:1" | "16:9"
    caption_max_chars: int
    hashtag_count: int
    cta_style: str             # Direct | Soft | Question | Emoji-heavy

    # Content rules
    hook_style: str            # First-word hook rule
    tone_rules: list[str]      # Do's for this tone
    avoid: list[str]           # Don'ts
    audience_signals: list[str]# What this audience responds to
    viral_patterns: list[str]  # Platform-specific viral content patterns

    # Algorithm signals
    algo_priority: list[str]   # Top signals this platform's algo rewards
    best_post_times: list[str] # UTC time windows

    # Thumbnail guidance (for thumbnail generator)
    thumbnail_style: str       # "bold text overlay" | "face reaction" | "minimal clean"
    thumbnail_colors: list[str]


@dataclass
class CrawlTarget:
    platform: str
    urls: list[str]            # Seed URLs to crawl
    selectors: dict            # CSS selectors for content extraction
    rate_limit_seconds: float  # Polite delay between requests
    max_pages: int


# ── Platform skillset definitions ─────────────────────────────────────────────

_SKILLSETS: dict[str, dict] = {

    "instagram": {
        "default_tone": "engaging",
        "format_type": "Reel",
        "aspect_ratio": "9:16",
        "ideal_length": "15-30 seconds",
        "caption_max_chars": 2_200,
        "hashtag_count": 10,
        "algo_priority": [
            "Saves", "Shares to Stories", "Watch rate >80%",
            "Comments with replies", "Profile visits from Reel"
        ],
        "best_post_times": ["08:00", "12:00", "19:00"],  # UTC
        "thumbnail_style": "bold text overlay with face",
        "thumbnail_colors": ["#FF6B6B", "#4ECDC4", "#FFE66D"],
        "tones": {
            "engaging":    {"cta": "Question", "hook": "Start with a surprising stat or question"},
            "motivational":{"cta": "Soft",     "hook": "Start with 'The day I realized...' or 'Nobody tells you that...'"},
            "funny":       {"cta": "Emoji-heavy","hook": "Start with a relatable fail scenario"},
            "educational": {"cta": "Direct",   "hook": "Start with 'Most people don't know...'"},
            "professional":{"cta": "Soft",     "hook": "Start with a bold industry insight"},
        },
        "audiences": {
            "gen z":       ["lo-fi aesthetic", "irony", "quick cuts", "trending audio", "raw authenticity"],
            "millennials": ["nostalgia", "self-improvement", "budget tips", "real talk"],
            "professionals":["career growth", "productivity", "industry news", "networking"],
            "fitness":     ["transformation", "before/after", "workout clips", "nutrition"],
            "general":     ["relatable humor", "life hacks", "inspirational quotes"],
        },
        "viral_patterns": [
            "Expectation vs Reality reveal",
            "Quick tutorial (3 steps in 30s)",
            "Hot take + debate bait",
            "Behind the scenes / day in the life",
            "Trending audio + niche topic",
        ],
        "avoid": [
            "Long text captions without line breaks",
            "Hashtags in first comment (hurts reach)",
            "Watermarked TikTok reposts",
            "Blurry or portrait-mode thumbnails",
        ],
    },

    "tiktok": {
        "default_tone": "funny",
        "format_type": "Short",
        "aspect_ratio": "9:16",
        "ideal_length": "21-34 seconds",
        "caption_max_chars": 2_200,
        "hashtag_count": 5,
        "algo_priority": [
            "Watch rate to completion", "Replay rate",
            "Shares", "Duets/Stitches", "Comments"
        ],
        "best_post_times": ["06:00", "14:00", "22:00"],
        "thumbnail_style": "face reaction close-up",
        "thumbnail_colors": ["#010101", "#FF0050", "#FFFFFF"],
        "tones": {
            "funny":       {"cta": "Emoji-heavy","hook": "POV: / Tell me you're a ___ without telling me"},
            "educational": {"cta": "Direct",    "hook": "Things school never taught you about..."},
            "motivational":{"cta": "Soft",      "hook": "If you're watching this, it's not a coincidence"},
            "engaging":    {"cta": "Question",  "hook": "This might be controversial but..."},
            "professional":{"cta": "Soft",      "hook": "I made $X doing this one thing"},
        },
        "audiences": {
            "gen z":       ["chaotic energy", "niche humor", "authenticity over polish", "trending sounds"],
            "millennials": ["adulting struggles", "nostalgia", "parenting", "finance"],
            "professionals":["career hacks", "side hustles", "corporate humor"],
            "fitness":     ["gym fails", "form checks", "progress videos"],
            "general":     ["animals", "food", "satisfying content", "life hacks"],
        },
        "viral_patterns": [
            "Trend + niche topic mashup",
            "Storytelling with cliffhanger",
            "Response to viral video",
            "Day in the life with voiceover",
            "'I tried X for 30 days' results",
        ],
        "avoid": [
            "Low audio quality",
            "No hook in first 1-2 seconds",
            "Posting landscape videos",
            "Ignoring comment replies (kills algo)",
        ],
    },

    "youtube": {
        "default_tone": "educational",
        "format_type": "Short or Long-form",
        "aspect_ratio": "16:9",
        "ideal_length": "7-15 minutes (long) / 30-60 seconds (Short)",
        "caption_max_chars": 5_000,
        "hashtag_count": 3,
        "algo_priority": [
            "Click-through rate (CTR)", "Average view duration",
            "Session time", "Likes-to-views ratio", "Subscriber conversion"
        ],
        "best_post_times": ["15:00", "17:00", "20:00"],
        "thumbnail_style": "bold text + surprised face + high contrast",
        "thumbnail_colors": ["#FF0000", "#FFFF00", "#FFFFFF"],
        "tones": {
            "educational": {"cta": "Direct",  "hook": "In the next X minutes you'll learn..."},
            "engaging":    {"cta": "Question","hook": "What if I told you..."},
            "motivational":{"cta": "Soft",    "hook": "This changed everything for me"},
            "professional":{"cta": "Direct",  "hook": "Most people get this completely wrong"},
            "funny":       {"cta": "Emoji-heavy","hook": "I can't believe this actually worked"},
        },
        "audiences": {
            "gen z":       ["quick entertainment", "gaming", "reacts", "trends"],
            "millennials": ["finance", "home improvement", "travel", "tech reviews"],
            "professionals":["tutorials", "case studies", "industry analysis"],
            "fitness":     ["workout programs", "nutrition science", "gear reviews"],
            "general":     ["documentaries", "how-to", "vlogs", "news"],
        },
        "viral_patterns": [
            "X things I wish I knew before...",
            "I tried X for Y days (results)",
            "The truth about X (controversy angle)",
            "Full tutorial: X in under 10 min",
            "Reaction / Response to viral content",
        ],
        "avoid": [
            "Clickbait with no delivery",
            "No chapter markers (hurts watch time)",
            "Inconsistent upload schedule",
            "Ignoring end-screen CTAs",
        ],
    },

    "twitter": {
        "default_tone": "engaging",
        "format_type": "Thread",
        "aspect_ratio": "16:9",
        "ideal_length": "280 chars (tweet) / 8-12 tweets (thread)",
        "caption_max_chars": 280,
        "hashtag_count": 2,
        "algo_priority": [
            "Replies", "Retweets/Quotes", "Bookmarks",
            "Link clicks (punished by algo — use replies instead)",
            "Early engagement velocity"
        ],
        "best_post_times": ["07:00", "12:00", "17:00"],
        "thumbnail_style": "minimal clean with bold stat",
        "thumbnail_colors": ["#1DA1F2", "#FFFFFF", "#000000"],
        "tones": {
            "engaging":    {"cta": "Question","hook": "Hot take: "},
            "funny":       {"cta": "Emoji-heavy","hook": "Me explaining to my boss why..."},
            "professional":{"cta": "Direct",  "hook": "After X years in Y, here's what I learned: 🧵"},
            "educational": {"cta": "Direct",  "hook": "Most people get X wrong. Here's why: 🧵"},
            "motivational":{"cta": "Soft",    "hook": "Nobody talks about this enough:"},
        },
        "audiences": {
            "gen z":       ["meme culture", "gaming", "stan culture", "social justice"],
            "millennials": ["tech", "politics", "pop culture", "finance"],
            "professionals":["startup", "VC", "tech", "marketing insights"],
            "fitness":     ["training logs", "nutrition debates", "gear"],
            "general":     ["news commentary", "humor", "life observations"],
        },
        "viral_patterns": [
            "Contrarian hot take",
            "List thread (X things about Y)",
            "Personal story with lesson",
            "Quote tweet + analysis",
            "Poll with controversy bait",
        ],
        "avoid": [
            "External links in main tweet (use replies)",
            "Posting image-only with no text",
            "Long thread without hook tweet",
            "Posting at off-peak hours without scheduling",
        ],
    },

    "linkedin": {
        "default_tone": "professional",
        "format_type": "Post or Article",
        "aspect_ratio": "1:1",
        "ideal_length": "150-300 words",
        "caption_max_chars": 3_000,
        "hashtag_count": 5,
        "algo_priority": [
            "Comments (esp. with 5+ words)", "Early engagement (first hour)",
            "Dwell time", "Profile views", "Connection growth"
        ],
        "best_post_times": ["07:30", "12:00", "17:30"],
        "thumbnail_style": "professional headshot or clean infographic",
        "thumbnail_colors": ["#0077B5", "#FFFFFF", "#F3F6F8"],
        "tones": {
            "professional":{"cta": "Question","hook": "I was wrong about X for 5 years. Here's what changed:"},
            "educational": {"cta": "Direct",  "hook": "3 things nobody teaches you about X:"},
            "motivational":{"cta": "Soft",    "hook": "A year ago I was [struggle]. Today I [win]:"},
            "engaging":    {"cta": "Question","hook": "Unpopular opinion: X is actually better than Y"},
            "funny":       {"cta": "Emoji-heavy","hook": "Things I say vs what I mean in meetings:"},
        },
        "audiences": {
            "professionals":["career stories", "leadership", "industry news", "salary transparency"],
            "gen z":       ["first job tips", "internship stories", "startup culture"],
            "millennials": ["management", "remote work", "personal brand"],
            "fitness":     ["mental health at work", "work-life balance"],
            "general":     ["business tips", "entrepreneurship", "self-improvement"],
        },
        "viral_patterns": [
            "Personal failure → lesson learned",
            "Salary / compensation transparency",
            "Hiring post or 'we're growing'",
            "Industry stat that surprises",
            "Day in the life of [unusual role]",
        ],
        "avoid": [
            "Hashtag spam (>10 hashtags)",
            "Pure self-promotion without value",
            "Walls of text without line breaks",
            "Posting external links without context",
        ],
    },
}

# ── Crawl targets per platform (website subsets) ──────────────────────────────

_CRAWL_TARGETS: dict[str, CrawlTarget] = {
    "instagram": CrawlTarget(
        platform="instagram",
        urls=[
            "https://www.instagram.com/explore/tags/{topic}/",
            "https://later.com/blog/instagram-trends/",
            "https://www.socialinsider.io/blog/instagram-trends/",
        ],
        selectors={"hashtag": "span._aacl", "post_text": "div._a9zs"},
        rate_limit_seconds=2.0,
        max_pages=3,
    ),
    "tiktok": CrawlTarget(
        platform="tiktok",
        urls=[
            "https://ads.tiktok.com/business/creativecenter/trends/pc/en",
            "https://www.tiktok.com/tag/{topic}",
            "https://tokboard.com/",
        ],
        selectors={"trending": "div[class*='trend']", "hashtag": "h2[class*='title']"},
        rate_limit_seconds=3.0,
        max_pages=2,
    ),
    "youtube": CrawlTarget(
        platform="youtube",
        urls=[
            "https://trends.google.com/trending?geo=US&hl=en",
            "https://www.youtube.com/results?search_query={topic}&sp=CAISBAgBEAE%3D",
        ],
        selectors={"title": "yt-formatted-string#video-title", "views": "span.ytd-video-meta-block"},
        rate_limit_seconds=2.5,
        max_pages=2,
    ),
    "twitter": CrawlTarget(
        platform="twitter",
        urls=[
            "https://trends24.in/",
            "https://getdaytrends.com/",
        ],
        selectors={"trend": "li.trend-item", "hashtag": "a.trend-link"},
        rate_limit_seconds=2.0,
        max_pages=2,
    ),
    "linkedin": CrawlTarget(
        platform="linkedin",
        urls=[
            "https://www.linkedin.com/news/",
            "https://www.socialinsider.io/blog/linkedin-trends/",
        ],
        selectors={"headline": "h3.headline", "topic": "span.topic-entity-link"},
        rate_limit_seconds=3.0,
        max_pages=2,
    ),
}


# ── Public API ────────────────────────────────────────────────────────────────

def resolve_skillset(
    platform: str,
    tone: str = "engaging",
    audience: str = "general",
) -> ContentSkillset:
    """
    Returns a fully resolved ContentSkillset for the given platform/tone/audience.
    Falls back gracefully for unknown values.
    """
    platform = platform.lower().strip()
    tone     = tone.lower().strip()
    audience = audience.lower().strip()

    cfg = _SKILLSETS.get(platform, _SKILLSETS["instagram"])

    # Resolve tone-specific rules
    tone_data = cfg["tones"].get(tone, cfg["tones"].get(cfg["default_tone"], {}))

    # Resolve audience signals
    audience_data = cfg["audiences"].get(
        audience,
        cfg["audiences"].get("general", [])
    )

    return ContentSkillset(
        platform=platform,
        tone=tone,
        audience=audience,
        ideal_length=cfg["ideal_length"],
        format_type=cfg["format_type"],
        aspect_ratio=cfg["aspect_ratio"],
        caption_max_chars=cfg["caption_max_chars"],
        hashtag_count=cfg["hashtag_count"],
        cta_style=tone_data.get("cta", "Question"),
        hook_style=tone_data.get("hook", "Start with a hook"),
        tone_rules=[f"Use a {tone} tone throughout"],
        avoid=cfg["avoid"],
        audience_signals=audience_data,
        viral_patterns=cfg["viral_patterns"],
        algo_priority=cfg["algo_priority"],
        best_post_times=cfg["best_post_times"],
        thumbnail_style=cfg["thumbnail_style"],
        thumbnail_colors=cfg["thumbnail_colors"],
    )


def skillset_to_prompt_block(skillset: ContentSkillset) -> str:
    """
    Converts a ContentSkillset into a structured prompt block
    that can be prepended to any agent's task description.
    """
    return f"""
=== PLATFORM SKILLSET: {skillset.platform.upper()} ===
Format      : {skillset.format_type} ({skillset.aspect_ratio})
Length      : {skillset.ideal_length}
Caption max : {skillset.caption_max_chars} chars
Hashtags    : {skillset.hashtag_count} tags
CTA style   : {skillset.cta_style}
Hook style  : {skillset.hook_style}

Target audience signals:
{chr(10).join(f'  - {s}' for s in skillset.audience_signals)}

Viral patterns for {skillset.platform}:
{chr(10).join(f'  - {p}' for p in skillset.viral_patterns)}

Algorithm priorities:
{chr(10).join(f'  - {a}' for a in skillset.algo_priority)}

Best post times (UTC): {', '.join(skillset.best_post_times)}

AVOID:
{chr(10).join(f'  - {x}' for x in skillset.avoid)}
=== END SKILLSET ===
"""


def get_platform_crawl_targets(platform: str) -> Optional[CrawlTarget]:
    """Returns the crawl target config for a given platform."""
    return _CRAWL_TARGETS.get(platform.lower())


def list_platforms() -> list[str]:
    return list(_SKILLSETS.keys())


def list_tones(platform: str) -> list[str]:
    cfg = _SKILLSETS.get(platform.lower(), {})
    return list(cfg.get("tones", {}).keys())


def list_audiences(platform: str) -> list[str]:
    cfg = _SKILLSETS.get(platform.lower(), {})
    return list(cfg.get("audiences", {}).keys())