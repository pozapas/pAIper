"""Review passes: generic dimension passes + specialized correctness/hallucination.

Each pass is a single focused LLM call returning strict JSON, parsed defensively.
A failed/unparseable pass degrades gracefully into a DimensionResult with `error`
set — it never raises into the orchestrator.
"""

from __future__ import annotations

import engine  # noqa: F401
from reviewer.utils import count_tokens, truncate_text  # type: ignore

from .llm import LLMClient
from .parsing import ParsedPaper
from .report import DimensionResult, Finding
from .rubric import (
    DIMENSION_SPECS,
    JSON_INSTRUCTIONS,
    PassSpec,
    build_system,
)

# Minimum chars of focused-section text before we fall back to full text.
_MIN_SECTION_CHARS = 600


def _context_for(paper: ParsedPaper, spec: PassSpec, budget_tokens: int) -> str:
    """Assemble the most relevant text for a dimension, with full-text fallback."""
    focused = paper.section_text(*spec.sections)
    if len(focused) < _MIN_SECTION_CHARS:
        focused = paper.full_text
    if count_tokens(focused) > budget_tokens:
        focused = truncate_text(focused, budget_tokens)
    return focused


def _findings_from(items: list, default_dim: str) -> list[Finding]:
    out: list[Finding] = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        out.append(
            Finding(
                title=str(it.get("title", "")).strip() or "(untitled)",
                issue=str(it.get("issue", it.get("explanation", ""))).strip(),
                severity=str(it.get("severity", "MAJOR")).strip().upper(),
                dimension=default_dim,
                section=str(it.get("section", "")).strip(),
                evidence=str(it.get("evidence", it.get("quote", ""))).strip(),
                recommendation=str(it.get("recommendation", "")).strip(),
                confidence=float(it.get("confidence", 0.7) or 0.7),
            )
        )
    return out


def run_dimension(
    spec: PassSpec,
    paper: ParsedPaper,
    llm: LLMClient,
    *,
    budget_tokens: int,
    max_output_tokens: int,
) -> DimensionResult:
    """Run one rubric dimension. Always returns a DimensionResult."""
    context = _context_for(paper, spec, budget_tokens)
    system = build_system(spec.criteria + "\n\n" + JSON_INSTRUCTIONS)
    user = (
        f"PAPER TITLE: {paper.title}\n\n"
        f"--- PAPER TEXT (relevant sections) ---\n{context}\n--- END ---\n\n"
        f"Review the dimension described in your instructions and return the JSON object."
    )
    result = DimensionResult(key=spec.key, label=spec.label, weight=spec.weight)
    try:
        data = llm.json(system, user, expected=dict, max_tokens=max_output_tokens)
    except Exception as exc:  # network/provider error inside a pass
        result.error = f"pass failed: {exc}"
        result.summary = "This dimension could not be evaluated (model/API error)."
        result.score = 0.0
        return result

    if not isinstance(data, dict):
        result.error = "model did not return parseable JSON"
        result.summary = "This dimension could not be evaluated (unparseable model output)."
        result.score = 0.0
        return result

    try:
        result.score = max(0.0, min(10.0, float(data.get("score", 0) or 0)))
    except (TypeError, ValueError):
        result.score = 0.0
    result.summary = str(data.get("summary", "")).strip()
    result.findings = _findings_from(data.get("findings", []), spec.key)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Specialized passes
# ─────────────────────────────────────────────────────────────────────────────

_CORRECTNESS_CRITERIA = """\
Perform a PASSAGE-LEVEL CORRECTNESS check, like a meticulous technical reviewer.
Look ONLY for concrete errors a careful reader could verify:
- Mathematical errors (wrong formulas, sign errors, missing factors, bad derivations, index/subscript errors).
- Notation inconsistencies (symbol used differently than defined; undefined notation).
- Numerical inconsistencies (a stated value contradicts a table, equation, or another section).
- Definition/theorem contradictions; a skipped non-trivial derivation step.
First try to resolve each concern from context; flag only what genuinely remains wrong.
Do NOT flag style, formatting, capitalization, or standard field shorthand.
Score 10 = no detectable correctness errors; lower as concrete errors accumulate."""

_HALLUCINATION_CRITERIA = """\
Perform an INTERNAL-CONSISTENCY and CLAIM-SUPPORT check (a "hallucination" audit of the
paper's own logic — NOT about the language model).
- Find claims asserted without any supporting result, citation, derivation, or stated assumption.
- Find places where a cited source is used to support a claim it plausibly does not support (overreach on a citation).
- Find numbers/statistics that appear fabricated or unsupported (no source, no method to derive them).
- Find contradictions between sections (abstract vs results, methods vs results, claims vs limitations).
Mark each as a finding with the offending verbatim quote in "evidence".
Score 10 = every claim is traceable to evidence; lower as unsupported/contradictory claims accumulate."""


def run_correctness(paper: ParsedPaper, llm: LLMClient, *, budget_tokens: int, max_output_tokens: int) -> DimensionResult:
    spec = PassSpec("correctness", "Technical Correctness", 1.1,
                    ("methods", "results", "background"), _CORRECTNESS_CRITERIA)
    return run_dimension(spec, paper, llm, budget_tokens=budget_tokens, max_output_tokens=max_output_tokens)


def run_hallucination(paper: ParsedPaper, llm: LLMClient, *, budget_tokens: int, max_output_tokens: int) -> DimensionResult:
    spec = PassSpec("hallucination", "Claim Integrity & Consistency", 1.1,
                    ("abstract", "results", "discussion", "conclusion", "introduction"),
                    _HALLUCINATION_CRITERIA)
    return run_dimension(spec, paper, llm, budget_tokens=budget_tokens, max_output_tokens=max_output_tokens)
