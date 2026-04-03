"""
llm.py — Multi-model router with token guard, fallback chain, and per-task model selection.

Supported models (all free/low-cost):
  - groq/llama-3.1-8b-instant     → fast, low token cost (trend research, classification)
  - groq/llama-3.3-70b-versatile  → smart, analysis tasks
  - groq/mixtral-8x7b-32768       → long-context tasks
  - claude-haiku-4-5              → Anthropic fast+cheap (content writing)
  - claude-sonnet-4-5             → Anthropic smart (virality scoring, strategy)
  - pollinations (thumbnail)       → free, no key needed

Token limits per model (conservative, leaving 20% buffer):
  - llama-3.1-8b-instant   → 6,000 tokens max input
  - llama-3.3-70b-versatile → 6,000 tokens max input
  - mixtral-8x7b-32768     → 24,000 tokens max input
  - claude-haiku-4-5       → 150,000 tokens max input
  - claude-sonnet-4-5      → 150,000 tokens max input
"""

import os
import logging
import tiktoken
from typing import Optional, Literal
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()
logger = logging.getLogger(__name__)

# ── API Keys ──────────────────────────────────────────────────────────────────

GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")

# ── Model name constants ──────────────────────────────────────────────────────

ModelName = Literal[
    "groq-fast",       # llama-3.1-8b-instant — cheapest, fastest
    "groq-smart",      # llama-3.3-70b-versatile — balanced
    "groq-long",       # mixtral-8x7b-32768 — long context
    "claude-haiku",    # claude-haiku-4-5 — Anthropic fast
    "claude-sonnet",   # claude-sonnet-4-5 — Anthropic smart
    "auto",            # router picks best available
]

# ── Token limits (input, conservative) ───────────────────────────────────────

TOKEN_LIMITS: dict[str, int] = {
    "groq/llama-3.1-8b-instant":    6_000,
    "groq/llama-3.3-70b-versatile": 6_000,
    "groq/mixtral-8x7b-32768":     24_000,
    "claude-haiku-4-5-20251001":   150_000,
    "claude-sonnet-4-5-20251001":  150_000,
}

MAX_OUTPUT_TOKENS = 1_024  # safe for all models

# ── Token counter ─────────────────────────────────────────────────────────────

def count_tokens(text: str) -> int:
    """Approximate token count using cl100k_base (works for all models)."""
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Fallback: ~4 chars per token
        return len(text) // 4


def guard_token_limit(prompt: str, model_id: str, label: str = "") -> str:
    """
    Truncate prompt to fit within the model's token limit.
    Logs a warning if truncation happens.
    """
    limit = TOKEN_LIMITS.get(model_id, 6_000)
    tokens = count_tokens(prompt)
    if tokens <= limit:
        return prompt

    logger.warning(
        f"[TOKEN GUARD] {label or model_id}: {tokens} tokens > limit {limit}. Truncating."
    )
    # Binary search truncation point
    enc = tiktoken.get_encoding("cl100k_base")
    encoded = enc.encode(prompt)
    truncated = enc.decode(encoded[:limit])
    return truncated + "\n\n[... truncated to fit token limit ...]"


# ── LLM factory ───────────────────────────────────────────────────────────────

def _make_groq(model_slug: str, temperature: float = 0.7) -> Optional[LLM]:
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_your"):
        return None
    return LLM(
        model=f"groq/{model_slug}",
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=MAX_OUTPUT_TOKENS,
    )


def _make_anthropic(model_id: str, temperature: float = 0.7) -> Optional[LLM]:
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY.startswith("sk-ant-your"):
        return None
    return LLM(
        model=model_id,
        api_key=ANTHROPIC_API_KEY,
        temperature=temperature,
        max_tokens=MAX_OUTPUT_TOKENS,
    )


# ── Pre-built model instances ─────────────────────────────────────────────────

# Fast model — trend research, classification
GROQ_FAST = _make_groq("llama-3.1-8b-instant", temperature=0.7)

# Smart model — virality analysis, algo analysis
GROQ_SMART = _make_groq("llama-3.3-70b-versatile", temperature=0.7)

# Long-context — strategy, full content packages
GROQ_LONG = _make_groq("mixtral-8x7b-32768", temperature=0.8)

# Claude Haiku — fast creative writing
CLAUDE_HAIKU = _make_anthropic("claude-haiku-4-5-20251001", temperature=0.8)

# Claude Sonnet 4.5 — smart analysis + strategy
CLAUDE_SONNET = _make_anthropic("claude-sonnet-4-5-20251001", temperature=0.7)

# ── Backward-compatible aliases (used by existing agents) ─────────────────────

GPT4O_MINI   = GROQ_FAST   or GROQ_SMART   # fallback
GPT4O        = GROQ_SMART  or GROQ_FAST
# CLAUDE_SONNET is already defined above; agents importing it get the real one


# ── Model router ──────────────────────────────────────────────────────────────

# Per-task recommended model (used by router)
TASK_MODEL_MAP: dict[str, ModelName] = {
    "trend_scout":       "groq-fast",    # high frequency, cheap
    "algorithm_analyst": "groq-smart",   # needs reasoning
    "content_optimizer": "claude-sonnet", # best creative writing
    "virality_predictor":"groq-smart",   # ML-style scoring
    "strategist":        "claude-sonnet", # planning + long output
}


def get_model_for_task(
    task: str,
    override: Optional[ModelName] = None,
    prompt: str = "",
) -> LLM:
    """
    Returns the best available LLM for a given task, with:
      - override: user-specified model name
      - automatic fallback if preferred model key is missing
      - token guard applied to prompt (logs warnings)

    Usage:
        llm = get_model_for_task("content_optimizer", prompt=my_prompt)
    """
    target: ModelName = override or TASK_MODEL_MAP.get(task, "auto")

    # Ordered preference for each target
    preference_order: dict[ModelName, list] = {
        "groq-fast":    [GROQ_FAST, GROQ_SMART, CLAUDE_HAIKU, CLAUDE_SONNET],
        "groq-smart":   [GROQ_SMART, GROQ_FAST, CLAUDE_SONNET, CLAUDE_HAIKU],
        "groq-long":    [GROQ_LONG, GROQ_SMART, CLAUDE_SONNET],
        "claude-haiku": [CLAUDE_HAIKU, GROQ_FAST, GROQ_SMART],
        "claude-sonnet":[CLAUDE_SONNET, CLAUDE_HAIKU, GROQ_SMART, GROQ_FAST],
        "auto":         [GROQ_SMART, CLAUDE_SONNET, GROQ_FAST, CLAUDE_HAIKU],
    }

    candidates = preference_order.get(target, preference_order["auto"])
    for llm in candidates:
        if llm is not None:
            # Log which model was selected
            model_label = getattr(llm, "model", str(llm))
            logger.info(f"[MODEL ROUTER] task={task} → {model_label}")

            # Token guard
            if prompt:
                model_id = getattr(llm, "model", "").replace("groq/", "groq/")
                guard_token_limit(prompt, model_id, label=task)

            return llm

    raise RuntimeError(
        "No LLM available. Set GROQ_API_KEY or ANTHROPIC_API_KEY in .env"
    )


def get_model_by_name(name: ModelName) -> LLM:
    """Direct model access by name — for user-facing model choice."""
    mapping = {
        "groq-fast":    GROQ_FAST,
        "groq-smart":   GROQ_SMART,
        "groq-long":    GROQ_LONG,
        "claude-haiku": CLAUDE_HAIKU,
        "claude-sonnet":CLAUDE_SONNET,
    }
    llm = mapping.get(name)
    if llm is None:
        logger.warning(f"Model '{name}' not available (key missing?). Falling back.")
        return get_model_for_task("auto")
    return llm


def describe_available_models() -> dict:
    """Returns which models are currently available (keys present)."""
    return {
        "groq-fast":     GROQ_FAST     is not None,
        "groq-smart":    GROQ_SMART    is not None,
        "groq-long":     GROQ_LONG     is not None,
        "claude-haiku":  CLAUDE_HAIKU  is not None,
        "claude-sonnet": CLAUDE_SONNET is not None,
    }


# ── Legacy key getter ─────────────────────────────────────────────────────────

def get_groq_key() -> str:
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_your"):
        raise ValueError("GROQ_API_KEY not set in .env")
    return GROQ_API_KEY