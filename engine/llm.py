"""Robust LLM wrapper around reviewer.client.chat.

Key responsibilities:
  * Hold provider/model/key/reasoning config and accumulate token usage.
  * `complete()` — plain text completion.
  * `json()` — completion that MUST return JSON, with fence-stripping, balanced-brace
    extraction, trailing-comma tolerance, and a single "repair" retry. It NEVER raises
    on a parse failure — it returns a sentinel so one bad pass can't kill the review.

This module imports nothing from Streamlit.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

import engine  # noqa: F401 — ensures reviewer.* is on sys.path
from reviewer.client import chat as _chat  # type: ignore

from .config import env_var_for, estimate_cost


# ─────────────────────────────────────────────────────────────────────────────
# Safe JSON parsing
# ─────────────────────────────────────────────────────────────────────────────

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def _strip_fences(text: str) -> str:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```\s*$", "", t)
    return t.strip()


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",(\s*[}\]])", r"\1", text)


def safe_json(text: str, expected: type = dict) -> Any | None:
    """Best-effort parse of LLM output into a dict or list.

    Strategy:
      1. Strip code fences and parse directly.
      2. Scan for the first balanced JSON object/array via JSONDecoder.raw_decode.
      3. Retry after removing trailing commas.
    Returns the parsed value matching `expected` (dict or list), else None.
    """
    if not text or not text.strip():
        return None

    candidates: list[str] = []
    stripped = _strip_fences(text)
    candidates.append(stripped)
    candidates.append(_remove_trailing_commas(stripped))

    opener = "{" if expected is dict else "["
    decoder = json.JSONDecoder()

    for cand in candidates:
        # direct parse
        try:
            val = json.loads(cand)
            if isinstance(val, expected):
                return val
        except json.JSONDecodeError:
            pass
        # scan for first balanced structure of the expected kind
        for i, ch in enumerate(cand):
            if ch == opener:
                try:
                    val, _ = decoder.raw_decode(cand, i)
                except json.JSONDecodeError:
                    continue
                if isinstance(val, expected):
                    return val
        # also accept a dict when a list was requested if it wraps a list
        if expected is list:
            try:
                val = json.loads(cand)
                if isinstance(val, dict):
                    for v in val.values():
                        if isinstance(v, list):
                            return v
            except json.JSONDecodeError:
                pass

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Client
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0
    cost_usd: float = 0.0
    cost_known: bool = True

    def add(self, model: str, prompt: int, completion: int) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.calls += 1
        c = estimate_cost(model, prompt, completion)
        if c is None:
            self.cost_known = False
        else:
            self.cost_usd += c

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMClient:
    """Configured client for a single review run."""

    provider_id: str
    model: str
    api_key: str = ""
    reasoning_effort: str | None = None
    temperature: float = 0.0
    default_max_tokens: int = 6144
    base_url: str = ""
    usage: Usage = field(default_factory=Usage)

    def __post_init__(self) -> None:
        if self.provider_id == "ollama":
            if self.base_url:
                os.environ["OLLAMA_BASE_URL"] = self.base_url
            os.environ["REVIEW_PROVIDER"] = self.provider_id
            return
        # The underlying reviewer.client reads keys from env vars.
        if self.api_key:
            os.environ[env_var_for(self.provider_id)] = self.api_key
        os.environ["REVIEW_PROVIDER"] = self.provider_id

    # ── core call ────────────────────────────────────────────────────────────
    def complete(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        if self.provider_id == "ollama":
            return self._complete_ollama(
                messages,
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=self.temperature if temperature is None else temperature,
            )
        text, usage = _chat(
            messages,
            model=self.model,
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=max_tokens or self.default_max_tokens,
            reasoning_effort=self.reasoning_effort,
            provider=self.provider_id,
        )
        self.usage.add(
            usage.get("model", self.model),
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )
        return text or ""

    def _complete_ollama(
        self,
        messages: list[dict],
        *,
        max_tokens: int,
        temperature: float,
    ) -> str:
        base_url = (self.base_url or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Ollama request failed ({exc.code}): {details}") from exc
        except Exception as exc:
            raise RuntimeError(
                f"Ollama is not reachable at {base_url}. Start Ollama locally, "
                "or use a reachable Ollama-compatible endpoint."
            ) from exc

        prompt_tokens = int(data.get("prompt_eval_count") or 0)
        completion_tokens = int(data.get("eval_count") or 0)
        self.usage.add(self.model, prompt_tokens, completion_tokens)
        message = data.get("message") or {}
        return str(message.get("content") or data.get("response") or "")

    # ── JSON call with repair retry ───────────────────────────────────────────
    def json(
        self,
        system: str,
        user: str,
        *,
        expected: type = dict,
        max_tokens: int | None = None,
    ) -> Any | None:
        raw = self.complete(system, user, max_tokens=max_tokens)
        parsed = safe_json(raw, expected=expected)
        if parsed is not None:
            return parsed

        # One repair attempt: hand the model its own broken output back.
        repair_sys = "You convert text into STRICT, valid JSON. Output ONLY JSON, no prose, no code fences."
        kind = "object" if expected is dict else "array"
        repair_user = (
            f"The following should be a single JSON {kind} but is malformed or wrapped in prose. "
            f"Return ONLY the corrected JSON {kind}.\n\n{raw[:12000]}"
        )
        raw2 = self.complete(repair_sys, repair_user, max_tokens=max_tokens)
        return safe_json(raw2, expected=expected)
