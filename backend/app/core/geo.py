"""
geo.py — Geo/location layer for location-aware content generation.

Features:
  - Resolve country/region/timezone from IP or user-provided location
  - Inject geo signals into agent context (local trends, language, peak hours)
  - Geographical scaling: adjusts content rules for regional audiences
  - Free APIs only (ip-api.com, restcountries.eu)

Usage:
    from app.core.geo import resolve_geo, geo_to_prompt_block

    geo = await resolve_geo(ip="8.8.8.8")
    geo = resolve_geo_from_string("Mumbai, India")
    block = geo_to_prompt_block(geo)
"""

import os
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


# ── Geo data model ────────────────────────────────────────────────────────────

@dataclass
class GeoContext:
    # Identity
    ip:          str = ""
    city:        str = ""
    region:      str = ""
    country:     str = ""
    country_code:str = ""   # ISO 3166-1 alpha-2
    continent:   str = ""
    latitude:    float = 0.0
    longitude:   float = 0.0
    timezone:    str = "UTC"

    # Content signals derived from location
    language:          str = "English"
    language_code:     str = "en"
    local_currency:    str = "USD"
    peak_hours_utc:    list[str] = field(default_factory=lambda: ["07:00","12:00","18:00"])
    regional_platforms:list[str] = field(default_factory=lambda: ["instagram","youtube","twitter"])
    content_style:     str = "global"   # global | western | south-asian | east-asian | latam | mena
    geo_hashtags:      list[str] = field(default_factory=list)

    # Meta
    resolved_from: str = "default"   # "ip" | "string" | "default"
    valid:         bool = False


# ── Region → content style mapping ───────────────────────────────────────────

COUNTRY_STYLE: dict[str, str] = {
    # South Asia
    "IN": "south-asian", "PK": "south-asian", "BD": "south-asian",
    "LK": "south-asian", "NP": "south-asian",
    # East Asia
    "CN": "east-asian", "JP": "east-asian", "KR": "east-asian",
    "TW": "east-asian", "HK": "east-asian",
    # MENA
    "SA": "mena", "AE": "mena", "EG": "mena", "TR": "mena",
    "IR": "mena", "IQ": "mena", "MA": "mena",
    # LatAm
    "BR": "latam", "MX": "latam", "AR": "latam", "CO": "latam",
    "CL": "latam", "PE": "latam",
    # Western / Anglophone (default)
    "US": "western", "GB": "western", "CA": "western",
    "AU": "western", "NZ": "western",
}

# Platform popularity by region
REGIONAL_PLATFORMS: dict[str, list[str]] = {
    "south-asian": ["instagram", "youtube", "twitter", "sharechat"],
    "east-asian":  ["youtube", "tiktok", "twitter", "line"],
    "mena":        ["instagram", "tiktok", "youtube", "twitter"],
    "latam":       ["instagram", "tiktok", "youtube", "twitter"],
    "western":     ["instagram", "tiktok", "youtube", "twitter", "linkedin"],
    "global":      ["instagram", "youtube", "twitter", "tiktok"],
}

# Content style descriptors for agent prompts
STYLE_DESCRIPTORS: dict[str, dict] = {
    "south-asian": {
        "tone_notes": "Use relatable everyday references, family values, local festivals, Bollywood/cricket angles when relevant. Mix English with occasional Hindi/Urdu phrases if audience expects it.",
        "trending_topics": ["cricket", "Bollywood", "startup India", "festivals", "street food"],
        "avoid": ["direct confrontation style", "overly individualistic messaging"],
    },
    "east-asian": {
        "tone_notes": "Polished, precise, collective-oriented. Value aesthetics and harmony. K-pop, anime, tech innovation resonate strongly.",
        "trending_topics": ["K-pop", "tech", "anime", "gaming", "food culture"],
        "avoid": ["aggressive humor", "controversial political references"],
    },
    "mena": {
        "tone_notes": "Family, community, tradition alongside modernism. Arabic phrases increase trust. Ramadan/Eid content peaks strongly.",
        "trending_topics": ["Ramadan", "Dubai lifestyle", "Arab entertainment", "halal food"],
        "avoid": ["alcohol references", "overly romantic content"],
    },
    "latam": {
        "tone_notes": "Warm, passionate, community-focused. Spanish/Portuguese. Football, music, carnival culture. Strong influencer-style voice.",
        "trending_topics": ["fútbol", "telenovelas", "carnival", "Latin music", "street food"],
        "avoid": ["overly formal language", "ignoring local slang"],
    },
    "western": {
        "tone_notes": "Direct, individual-focused, humor-forward. Meme culture, pop culture references, self-improvement narratives work well.",
        "trending_topics": ["self-improvement", "tech culture", "true crime", "streaming shows"],
        "avoid": ["assuming single culture", "US-only references for non-US audiences"],
    },
    "global": {
        "tone_notes": "Universal themes: hope, humor, curiosity, connection. Avoid slang, idioms, or cultural references that don't translate.",
        "trending_topics": ["AI", "environment", "mental health", "travel", "food"],
        "avoid": ["heavy slang", "country-specific references"],
    },
}

# Timezone → peak hours in local time (converted to UTC offset approximations)
TIMEZONE_PEAKS: dict[str, list[str]] = {
    "Asia/Kolkata":       ["02:30", "06:30", "13:30"],  # IST +5:30
    "Asia/Tokyo":         ["22:00", "03:00", "10:00"],  # JST +9
    "Asia/Shanghai":      ["23:00", "04:00", "11:00"],  # CST +8
    "America/New_York":   ["12:00", "17:00", "22:00"],  # EST -5
    "America/Los_Angeles":["15:00", "20:00", "01:00"],  # PST -8
    "Europe/London":      ["07:00", "12:00", "17:00"],  # GMT/BST
    "Europe/Berlin":      ["06:00", "11:00", "16:00"],  # CET +1
    "America/Sao_Paulo":  ["10:00", "15:00", "20:00"],  # BRT -3
    "Asia/Dubai":         ["04:00", "09:00", "15:00"],  # GST +4
    "UTC":                ["07:00", "12:00", "18:00"],
}


# ── IP-based resolution (free: ip-api.com) ───────────────────────────────────

async def resolve_geo(ip: str = "") -> GeoContext:
    """
    Resolve geo context from an IP address using ip-api.com (free, no key).
    Falls back to default GeoContext on failure.
    """
    if not ip or ip in ("127.0.0.1", "localhost", "::1"):
        return _default_geo()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,country,countryCode,region,regionName,city,lat,lon,timezone,currency,lang"},
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "success":
            logger.warning(f"ip-api failed for {ip}: {data.get('message')}")
            return _default_geo()

        country_code = data.get("countryCode", "US")
        timezone     = data.get("timezone", "UTC")
        style        = COUNTRY_STYLE.get(country_code, "global")

        return GeoContext(
            ip=ip,
            city=data.get("city", ""),
            region=data.get("regionName", ""),
            country=data.get("country", ""),
            country_code=country_code,
            timezone=timezone,
            latitude=data.get("lat", 0.0),
            longitude=data.get("lon", 0.0),
            language=_language_from_code(country_code),
            language_code=_lang_code(country_code),
            local_currency=data.get("currency", "USD"),
            peak_hours_utc=TIMEZONE_PEAKS.get(timezone, TIMEZONE_PEAKS["UTC"]),
            regional_platforms=REGIONAL_PLATFORMS.get(style, REGIONAL_PLATFORMS["global"]),
            content_style=style,
            geo_hashtags=_geo_hashtags(data.get("city",""), data.get("country","")),
            resolved_from="ip",
            valid=True,
        )
    except Exception as e:
        logger.warning(f"Geo resolution failed for IP {ip}: {e}")
        return _default_geo()


def resolve_geo_from_string(location: str) -> GeoContext:
    """
    Resolve geo context from a plain-text location string like "Mumbai, India".
    Synchronous — uses simple lookup table.
    """
    if not location or location.lower() in ("general", "global", "worldwide", ""):
        return _default_geo()

    location_lower = location.lower()

    # Country/city → country_code mapping (common cases)
    LOCATION_MAP: dict[str, str] = {
        "india": "IN", "mumbai": "IN", "delhi": "IN", "bangalore": "IN",
        "pakistan": "PK", "karachi": "PK",
        "usa": "US", "united states": "US", "new york": "US", "los angeles": "US",
        "uk": "GB", "london": "GB", "united kingdom": "GB",
        "japan": "JP", "tokyo": "JP",
        "china": "CN", "beijing": "CN", "shanghai": "CN",
        "brazil": "BR", "sao paulo": "BR",
        "uae": "AE", "dubai": "AE",
        "saudi arabia": "SA", "riyadh": "SA",
        "germany": "DE", "berlin": "DE",
        "france": "FR", "paris": "FR",
        "australia": "AU", "sydney": "AU",
        "canada": "CA", "toronto": "CA",
        "mexico": "MX",
        "indonesia": "ID", "jakarta": "ID",
        "nigeria": "NG", "lagos": "NG",
        "egypt": "EG", "cairo": "EG",
        "turkey": "TR", "istanbul": "TR",
        "south korea": "KR", "seoul": "KR",
        "thailand": "TH", "bangkok": "TH",
    }

    country_code = "US"
    for keyword, code in LOCATION_MAP.items():
        if keyword in location_lower:
            country_code = code
            break

    style = COUNTRY_STYLE.get(country_code, "global")
    tz_map = {
        "IN": "Asia/Kolkata", "JP": "Asia/Tokyo", "CN": "Asia/Shanghai",
        "US": "America/New_York", "GB": "Europe/London", "DE": "Europe/Berlin",
        "BR": "America/Sao_Paulo", "AE": "Asia/Dubai", "AU": "Australia/Sydney",
    }
    timezone = tz_map.get(country_code, "UTC")

    return GeoContext(
        city=location.split(",")[0].strip() if "," in location else "",
        country=location,
        country_code=country_code,
        timezone=timezone,
        language=_language_from_code(country_code),
        language_code=_lang_code(country_code),
        peak_hours_utc=TIMEZONE_PEAKS.get(timezone, TIMEZONE_PEAKS["UTC"]),
        regional_platforms=REGIONAL_PLATFORMS.get(style, REGIONAL_PLATFORMS["global"]),
        content_style=style,
        geo_hashtags=_geo_hashtags(location.split(",")[0] if "," in location else "", location),
        resolved_from="string",
        valid=True,
    )


# ── Prompt block builder ──────────────────────────────────────────────────────

def geo_to_prompt_block(geo: GeoContext) -> str:
    """
    Converts a GeoContext into a structured prompt block for agents.
    """
    if not geo.valid:
        return "=== GEO: Global audience — no location targeting ==="

    style = STYLE_DESCRIPTORS.get(geo.content_style, STYLE_DESCRIPTORS["global"])

    return f"""
=== GEO CONTEXT: {geo.country or 'Global'} ({geo.content_style.upper()}) ===
Location        : {geo.city or 'N/A'}, {geo.region or ''}, {geo.country}
Timezone        : {geo.timezone}
Language        : {geo.language}
Content style   : {geo.content_style}
Peak hours (UTC): {', '.join(geo.peak_hours_utc)}
Top platforms   : {', '.join(geo.regional_platforms[:4])}
Geo hashtags    : {', '.join(geo.geo_hashtags[:6]) or 'none'}

Tone notes for this region:
  {style['tone_notes']}

Locally trending topic angles:
{chr(10).join(f"  - {t}" for t in style['trending_topics'])}

Avoid for this audience:
{chr(10).join(f"  - {x}" for x in style['avoid'])}
=== END GEO ===
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _default_geo() -> GeoContext:
    return GeoContext(
        country="Global",
        country_code="US",
        timezone="UTC",
        language="English",
        language_code="en",
        peak_hours_utc=["07:00", "12:00", "18:00"],
        regional_platforms=["instagram", "youtube", "twitter", "tiktok"],
        content_style="global",
        resolved_from="default",
        valid=False,
    )


def _language_from_code(cc: str) -> str:
    MAP = {
        "IN": "Hindi/English", "PK": "Urdu/English", "BD": "Bengali",
        "CN": "Mandarin", "JP": "Japanese", "KR": "Korean",
        "SA": "Arabic", "AE": "Arabic", "EG": "Arabic", "TR": "Turkish",
        "BR": "Portuguese", "MX": "Spanish", "AR": "Spanish",
        "DE": "German", "FR": "French", "IT": "Italian",
        "RU": "Russian", "ID": "Indonesian",
    }
    return MAP.get(cc, "English")


def _lang_code(cc: str) -> str:
    MAP = {
        "IN": "hi", "PK": "ur", "BD": "bn", "CN": "zh", "JP": "ja",
        "KR": "ko", "SA": "ar", "AE": "ar", "EG": "ar", "TR": "tr",
        "BR": "pt", "MX": "es", "AR": "es", "DE": "de", "FR": "fr",
        "RU": "ru", "ID": "id",
    }
    return MAP.get(cc, "en")


def _geo_hashtags(city: str, country: str) -> list[str]:
    tags = []
    if city:
        tags.append(f"#{city.lower().replace(' ','')}")
        tags.append(f"#{city.lower().replace(' ','')}life")
    if country and country != "Global":
        tags.append(f"#{country.lower().replace(' ','').replace(',','')}")
    return tags