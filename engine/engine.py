"""Review orchestrator: parse -> run passes -> synthesize -> ReviewReport.

This is the public entry point for the engine. The UI calls `run_review(...)`.
Venue and citation modules are optional and imported lazily so the engine still
runs if they are absent or disabled.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import engine  # noqa: F401
from reviewer.utils import truncate_text  # type: ignore

from .config import DEPTHS, DEFAULT_DEPTH
from .llm import LLMClient
from .parsing import ParsedPaper, parse_paper
from .passes import DIMENSION_SPECS, run_correctness, run_dimension, run_hallucination
from .report import (
    ActionItem,
    DimensionResult,
    Finding,
    ReviewReport,
)
from .rubric import build_system, recommendation_from_score, weighted_overall


# ─────────────────────────────────────────────────────────────────────────────
# Options
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReviewOptions:
    depth: str = DEFAULT_DEPTH
    venue_id: str = ""               # "" => no venue targeting
    check_citations: bool = False
    max_citations: int = 40
    concurrent: bool = True
    ocr_method: str = "auto"
    bibliography_text: str = ""


ProgressCB = Callable[[float, str], None]


def _noop(_p: float, _m: str) -> None:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Synthesis
# ─────────────────────────────────────────────────────────────────────────────

_SYNTH_JSON = """\
Return ONLY a JSON object with this shape:
{
  "headline_summary": "<3-5 sentences: what the paper does and your overall assessment, editor-to-author>",
  "verdict": "<1-2 sentences stating the recommendation and the single most important reason>",
  "strengths": ["<concrete strength>", ...],
  "weaknesses": ["<concrete weakness, most important first>", ...],
  "action_items": [
    {"text": "<specific, actionable step the authors should take>",
     "priority": "CRITICAL"|"MAJOR"|"MINOR", "dimension": "<dimension key or ''>"}
  ]
}
Order weaknesses and action_items by importance. 4-8 items each is typical."""


def _synthesize(paper: ParsedPaper, dims: list[DimensionResult], llm: LLMClient,
                max_output_tokens: int) -> dict:
    # Compact digest of dimension results to keep the synthesis prompt small.
    lines = []
    for d in dims:
        lines.append(f"## {d.label} — score {d.score:.1f}/10")
        if d.summary:
            lines.append(d.summary)
        for f in d.findings[:6]:
            lines.append(f"- [{f.severity}] {f.title}: {f.issue[:240]}")
    digest = "\n".join(lines)
    digest = truncate_text(digest, 8000)

    system = build_system(
        "You are writing the meta-review that synthesizes per-dimension reviews into a "
        "single editorial decision. Be decisive, specific, and constructive.\n\n" + _SYNTH_JSON
    )
    user = (
        f"PAPER TITLE: {paper.title}\n\n"
        f"PER-DIMENSION REVIEW DIGEST:\n{digest}\n\n"
        f"Write the synthesis JSON."
    )
    data = llm.json(system, user, expected=dict, max_tokens=max_output_tokens)
    return data if isinstance(data, dict) else {}


def _fallback_action_items(dims: list[DimensionResult]) -> list[ActionItem]:
    items: list[ActionItem] = []
    for d in dims:
        for f in d.findings:
            if f.severity in ("CRITICAL", "MAJOR") and f.recommendation:
                items.append(ActionItem(text=f.recommendation, priority=f.severity, dimension=d.key))
    # critical first, cap
    items.sort(key=lambda a: 0 if a.priority == "CRITICAL" else 1)
    return items[:10]


def _apply_bibliography(paper: ParsedPaper, bibliography_text: str) -> None:
    bib = (bibliography_text or "").strip()
    if bib:
        paper.references_block = bib


# ─────────────────────────────────────────────────────────────────────────────
# Main entry
# ─────────────────────────────────────────────────────────────────────────────

def run_review(
    file_path: str | Path,
    llm: LLMClient,
    options: ReviewOptions,
    *,
    title_override: str = "",
    progress: ProgressCB = _noop,
) -> ReviewReport:
    depth = DEPTHS.get(options.depth, DEPTHS[DEFAULT_DEPTH])

    progress(0.03, "Parsing document…")
    paper = parse_paper(file_path, ocr=options.ocr_method)
    _apply_bibliography(paper, options.bibliography_text)
    if title_override:
        paper.title = title_override

    report = ReviewReport(
        title=paper.title,
        model=llm.model,
        provider=llm.provider_id,
        depth=depth.key,
        venue_id=options.venue_id,
        parse_engine=paper.parse_engine,
        was_ocr=paper.was_ocr,
        paragraphs=paper.paragraphs,
    )

    # ── dimension passes ──────────────────────────────────────────────────────
    dim_keys = [k for k in depth.passes if k in DIMENSION_SPECS]
    special_keys = [k for k in depth.passes if k in ("correctness", "hallucination")]
    total_steps = len(dim_keys) + len(special_keys) + 2  # +citations/venue +synthesis
    done = 0

    def _tick(msg: str) -> None:
        nonlocal done
        done += 1
        progress(0.05 + 0.75 * (done / max(total_steps, 1)), msg)

    dims: list[DimensionResult] = []

    def _run_one(key: str) -> DimensionResult:
        if key == "correctness":
            return run_correctness(paper, llm, budget_tokens=depth.chunk_tokens,
                                   max_output_tokens=depth.max_output_tokens)
        if key == "hallucination":
            return run_hallucination(paper, llm, budget_tokens=depth.chunk_tokens,
                                     max_output_tokens=depth.max_output_tokens)
        return run_dimension(DIMENSION_SPECS[key], paper, llm,
                             budget_tokens=depth.chunk_tokens,
                             max_output_tokens=depth.max_output_tokens)

    all_keys = dim_keys + special_keys
    if options.concurrent and len(all_keys) > 1:
        progress(0.07, f"Reviewing {len(all_keys)} dimensions in parallel…")
        with ThreadPoolExecutor(max_workers=min(4, len(all_keys))) as ex:
            futures = {ex.submit(_run_one, k): k for k in all_keys}
            results = {}
            for fut in futures:
                k = futures[fut]
                results[k] = fut.result()
                _tick(f"Reviewed: {results[k].label}")
        ordered = [results[k] for k in all_keys]
    else:
        ordered = []
        for k in all_keys:
            r = _run_one(k)
            ordered.append(r)
            _tick(f"Reviewed: {r.label}")

    # hallucination findings live in their own report bucket; the rest are dimensions
    for r in ordered:
        if r.key == "hallucination":
            report.hallucinations = r.findings
            # still count its score as a dimension for the overall
            report.dimensions.append(r)
        else:
            report.dimensions.append(r)
    dims = report.dimensions

    # ── venue fit (optional) ──────────────────────────────────────────────────
    if options.venue_id:
        try:
            from .venues import evaluate_venue
            progress(0.82, "Checking venue fit & checklist…")
            report.venue_fit = evaluate_venue(options.venue_id, paper, llm)
        except Exception as exc:
            report.warnings.append(f"Venue evaluation failed: {exc}")
    _tick("Venue fit done")

    # ── citations (optional) ──────────────────────────────────────────────────
    if options.check_citations:
        try:
            from .citations import check_citations
            progress(0.88, "Verifying citations against scholarly databases…")
            report.citation_check = check_citations(
                paper, llm, max_refs=options.max_citations
            )
        except Exception as exc:
            report.warnings.append(f"Citation check failed: {exc}")

    # ── synthesis ─────────────────────────────────────────────────────────────
    progress(0.92, "Synthesizing the meta-review…")
    scores = {d.key: d.score for d in dims if not d.error}
    report.overall_score = weighted_overall(scores)
    n_critical = sum(1 for f in report.all_findings() if f.severity == "CRITICAL")
    report.recommendation = recommendation_from_score(report.overall_score, n_critical)

    synth = _synthesize(paper, dims, llm, depth.max_output_tokens)
    report.headline_summary = str(synth.get("headline_summary", "")).strip()
    report.verdict = str(synth.get("verdict", "")).strip()
    report.strengths = [str(s).strip() for s in synth.get("strengths", []) if str(s).strip()]
    report.weaknesses = [str(w).strip() for w in synth.get("weaknesses", []) if str(w).strip()]
    action_items = []
    for a in synth.get("action_items", []):
        if isinstance(a, dict) and str(a.get("text", "")).strip():
            action_items.append(ActionItem(
                text=str(a["text"]).strip(),
                priority=str(a.get("priority", "MAJOR")).strip().upper(),
                dimension=str(a.get("dimension", "")).strip(),
            ))
    report.action_items = action_items or _fallback_action_items(dims)

    if not report.strengths:
        report.strengths = [f.title for f in report.all_findings() if f.severity == "PRAISE"][:5]
    if not report.weaknesses:
        report.weaknesses = [f.title for f in report.all_findings()
                             if f.severity in ("CRITICAL", "MAJOR")][:6]

    # ── accounting ────────────────────────────────────────────────────────────
    report.prompt_tokens = llm.usage.prompt_tokens
    report.completion_tokens = llm.usage.completion_tokens
    report.n_calls = llm.usage.calls
    report.cost_usd = round(llm.usage.cost_usd, 4) if llm.usage.cost_known else None

    progress(1.0, "Review complete ✓")
    return report


def run_citation_audit(
    file_path: str | Path | None,
    llm: LLMClient | None,
    options: ReviewOptions,
    *,
    title_override: str = "",
    progress: ProgressCB = _noop,
) -> ReviewReport:
    progress(0.05, "Preparing citation audit...")

    if file_path is not None:
        paper = parse_paper(file_path, ocr=options.ocr_method)
    else:
        paper = ParsedPaper(
            title=title_override or "BibTeX citation audit",
            full_text=options.bibliography_text,
            was_ocr=False,
            parse_engine="bibtex",
            references_block=options.bibliography_text,
        )
    _apply_bibliography(paper, options.bibliography_text)
    if title_override:
        paper.title = title_override

    report = ReviewReport(
        title=paper.title,
        model=llm.model if llm else "No model used",
        provider=llm.provider_id if llm else "bibtex-direct",
        depth="citation-only",
        venue_id="",
        parse_engine=paper.parse_engine,
        was_ocr=paper.was_ocr,
        paragraphs=paper.paragraphs,
        recommendation="Citation Audit",
        headline_summary=(
            "Citation-only audit. pAIper verified the parsed references against "
            "CrossRef, Semantic Scholar, and OpenAlex without running a manuscript review."
        ),
    )

    try:
        from .citations import check_citations
        progress(0.35, "Verifying references against scholarly databases...")
        report.citation_check = check_citations(
            paper, llm, max_refs=options.max_citations
        )
    except Exception as exc:
        report.warnings.append(f"Citation check failed: {exc}")

    if llm:
        report.prompt_tokens = llm.usage.prompt_tokens
        report.completion_tokens = llm.usage.completion_tokens
        report.n_calls = llm.usage.calls
        report.cost_usd = round(llm.usage.cost_usd, 4) if llm.usage.cost_known else None

    progress(1.0, "Citation audit complete")
    return report
