"""Provider / model / depth configuration for the review engine.

Pure data + small helpers. No Streamlit, no network.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────────────────────
# Providers
# ─────────────────────────────────────────────────────────────────────────────

PROVIDERS: dict[str, dict] = {
    "OpenRouter": {
        "key_env": "OPENROUTER_API_KEY",
        "provider_id": "openrouter",
        "note": "One key for 300+ models. Free models available — best for getting started.",
        "signup_url": "https://openrouter.ai/keys",
        "free_models_url": "https://openrouter.ai/models?q=free",
        "models": [
            # ── strong (paid) ──
            "anthropic/claude-opus-4.7",
            "anthropic/claude-sonnet-4.6",
            "openai/gpt-5.5",
            "openai/gpt-5.4",
            "google/gemini-3.1-pro-preview",
            "google/gemini-2.5-pro",
            "deepseek/deepseek-r1",
            # ── free / cheap ──
            "deepseek/deepseek-chat-v3.1:free",
            "google/gemini-2.5-flash",
            "openai/gpt-oss-120b:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-small-latest",
        ],
    },
    "Gemini": {
        "key_env": "GEMINI_API_KEY",
        "provider_id": "gemini",
        "note": "Google Gemini. Generous FREE tier — great no-cost option.",
        "signup_url": "https://aistudio.google.com/app/apikey",
        "free_models_url": "https://aistudio.google.com/app/apikey",
        "models": [
            "gemini-3.1-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ],
    },
    "OpenAI": {
        "key_env": "OPENAI_API_KEY",
        "provider_id": "openai",
        "note": "Direct OpenAI API. Pay-as-you-go.",
        "signup_url": "https://platform.openai.com/api-keys",
        "free_models_url": "",
        "models": ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-4.1", "gpt-4.1-mini", "o4-mini", "o3"],
    },
    "Anthropic": {
        "key_env": "ANTHROPIC_API_KEY",
        "provider_id": "anthropic",
        "note": "Direct Anthropic (Claude) API. Pay-as-you-go.",
        "signup_url": "https://console.anthropic.com/settings/keys",
        "free_models_url": "",
        "models": [
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            "claude-sonnet-4-5",
            "claude-haiku-4-5-20251001",
        ],
    },
    "Mistral": {
        "key_env": "MISTRAL_API_KEY",
        "provider_id": "mistral",
        "note": "Mistral AI API. Pay-as-you-go. Also powers high-quality PDF OCR.",
        "signup_url": "https://console.mistral.ai/api-keys",
        "free_models_url": "",
        "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
    },
    "Ollama / Local": {
        "key_env": "",
        "provider_id": "ollama",
        "note": (
            "Runs against an Ollama-compatible endpoint. Private when pAIper is "
            "running on your own machine; hosted Streamlit still receives uploads."
        ),
        "signup_url": "https://ollama.com",
        "free_models_url": "",
        "requires_key": False,
        "base_url_env": "OLLAMA_BASE_URL",
        "models": [
            "llama3.1:8b",
            "qwen2.5:7b-instruct",
            "mistral:7b",
            "gemma3:12b",
            "deepseek-r1:8b",
        ],
    },
}


def env_var_for(provider_id: str) -> str:
    for v in PROVIDERS.values():
        if v["provider_id"] == provider_id:
            return v["key_env"]
    return "OPENAI_API_KEY"


# ─────────────────────────────────────────────────────────────────────────────
# OCR / parsing engines (PDF only)
# ─────────────────────────────────────────────────────────────────────────────

OCR_METHODS: dict[str, dict] = {
    "auto": {
        "label": "Auto",
        "desc": "Mistral OCR if a Mistral key is set, otherwise the built-in PyMuPDF extractor.",
        "needs_key": None,
    },
    "pymupdf": {
        "label": "PyMuPDF (built-in, free, offline)",
        "desc": "Fast built-in extractor. No key, works offline. Best for text-based PDFs.",
        "needs_key": None,
    },
    "mistral": {
        "label": "Mistral OCR (cloud, ~$0.001/page)",
        "desc": "Best quality for scanned PDFs, tables, equations. Needs a Mistral API key.",
        "needs_key": "MISTRAL_API_KEY",
        "key_label": "Mistral OCR API key",
        "key_url": "https://console.mistral.ai/api-keys",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Review depth presets
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Depth:
    key: str
    label: str
    desc: str
    passes: tuple[str, ...]
    chunk_tokens: int          # per-pass context budget for long papers
    max_output_tokens: int


DEPTHS: dict[str, Depth] = {
    "fast": Depth(
        key="fast",
        label="Fast",
        desc="Core dimensions only. Fastest / cheapest. Good for an early draft check.",
        passes=("contribution", "methodology", "results_claims", "writing"),
        chunk_tokens=12000,
        max_output_tokens=4096,
    ),
    "standard": Depth(
        key="standard",
        label="Standard",
        desc="All review dimensions. Recommended balance of depth and cost.",
        passes=(
            "contribution", "related_work", "methodology", "statistics",
            "results_claims", "reproducibility", "writing",
        ),
        chunk_tokens=14000,
        max_output_tokens=6144,
    ),
    "deep": Depth(
        key="deep",
        label="Deep (Q1)",
        desc="Every dimension + passage-level correctness + hallucination check. Most thorough.",
        passes=(
            "contribution", "related_work", "methodology", "statistics",
            "results_claims", "reproducibility", "writing",
            "correctness", "hallucination",
        ),
        chunk_tokens=16000,
        max_output_tokens=8192,
    ),
}

DEFAULT_DEPTH = "standard"

# Approx prices ($/1M tokens) for the cost meter. Best-effort; "" => unknown.
APPROX_PRICE_PER_MTOK: dict[str, tuple[float, float]] = {
    # (prompt, completion)
    "opus": (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku": (0.8, 4.0),
    "gpt-5": (1.25, 10.0),
    "gpt-4.1": (2.0, 8.0),
    "gemini-2.5-pro": (1.25, 10.0),
    "gemini-2.5-flash": (0.3, 2.5),
    "gemini-3": (2.0, 12.0),
    "mistral-large": (2.0, 6.0),
    "mistral-small": (0.2, 0.6),
    "deepseek": (0.5, 2.0),
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    """Rough USD cost estimate, or None if the model is unknown/free."""
    m = (model or "").lower()
    if ":free" in m:
        return 0.0
    for key, (pin, pout) in APPROX_PRICE_PER_MTOK.items():
        if key in m:
            return prompt_tokens / 1e6 * pin + completion_tokens / 1e6 * pout
    return None
