"""Report data model — the single source of truth for UI + every exporter.

All dataclasses are JSON-serializable via `to_dict()` / `as_dict()` helpers.
No Streamlit, no network.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── severities / statuses ────────────────────────────────────────────────────
SEVERITIES = ("CRITICAL", "MAJOR", "MINOR", "PRAISE")
SEVERITY_RANK = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "PRAISE": 3}

RECOMMENDATIONS = ("Accept", "Minor Revision", "Major Revision", "Reject")


@dataclass
class Finding:
    title: str
    issue: str
    severity: str = "MAJOR"          # CRITICAL | MAJOR | MINOR | PRAISE
    dimension: str = "general"
    section: str = ""
    evidence: str = ""               # verbatim quote from the paper
    recommendation: str = ""
    confidence: float = 0.7          # 0..1
    id: str = ""

    def __post_init__(self) -> None:
        sev = (self.severity or "MAJOR").upper()
        self.severity = sev if sev in SEVERITIES else "MAJOR"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DimensionResult:
    key: str
    label: str
    score: float = 0.0               # 0..10
    weight: float = 1.0
    summary: str = ""
    findings: list[Finding] = field(default_factory=list)
    error: str = ""                  # set if the pass failed to parse

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "score": round(self.score, 1),
            "weight": self.weight,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
            "error": self.error,
        }


@dataclass
class ChecklistItem:
    text: str
    status: str = "UNCLEAR"          # PASS | FAIL | UNCLEAR | NA
    evidence: str = ""
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VenueFit:
    venue_id: str = ""
    venue_name: str = ""
    fit_score: int = 0               # 0..100
    scope_rationale: str = ""
    rejection_risks: list[str] = field(default_factory=list)
    checklist: list[ChecklistItem] = field(default_factory=list)
    checklist_generated: bool = False  # True if not hand-curated

    def to_dict(self) -> dict:
        return {
            "venue_id": self.venue_id,
            "venue_name": self.venue_name,
            "fit_score": self.fit_score,
            "scope_rationale": self.scope_rationale,
            "rejection_risks": self.rejection_risks,
            "checklist": [c.to_dict() for c in self.checklist],
            "checklist_generated": self.checklist_generated,
        }


@dataclass
class CitationItem:
    raw: str
    title: str = ""
    authors: str = ""
    year: str = ""
    doi: str = ""
    status: str = "UNCHECKED"        # VERIFIED | NOT_FOUND | MISMATCH | UNPARSEABLE | UNCHECKED
    match_url: str = ""
    sources: str = ""                # which databases confirmed it
    red_flags: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CitationCheck:
    enabled: bool = False
    n_refs: int = 0
    n_verified: int = 0
    n_suspicious: int = 0            # NOT_FOUND + MISMATCH
    items: list[CitationItem] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "n_refs": self.n_refs,
            "n_verified": self.n_verified,
            "n_suspicious": self.n_suspicious,
            "items": [c.to_dict() for c in self.items],
            "note": self.note,
        }


@dataclass
class ActionItem:
    text: str
    priority: str = "MAJOR"          # mirrors severity
    dimension: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReviewReport:
    title: str = ""
    # meta
    model: str = ""
    provider: str = ""
    depth: str = ""
    venue_id: str = ""
    parse_engine: str = ""
    was_ocr: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # headline
    recommendation: str = "Major Revision"
    verdict: str = ""                # one/two-sentence editor verdict
    overall_score: float = 0.0       # 0..10 weighted
    headline_summary: str = ""       # short abstract-level assessment

    # body
    dimensions: list[DimensionResult] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    venue_fit: VenueFit | None = None
    citation_check: CitationCheck | None = None
    hallucinations: list[Finding] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)

    # debug / accounting
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float | None = None
    n_calls: int = 0
    warnings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)  # for annotated view

    # ── derived helpers ───────────────────────────────────────────────────────
    def all_findings(self) -> list[Finding]:
        # The hallucination pass is stored as a dimension AND mirrored in
        # `self.hallucinations`; iterate dimensions only to avoid double-counting.
        out: list[Finding] = []
        seen: set[int] = set()
        for d in self.dimensions:
            for f in d.findings:
                if id(f) not in seen:
                    seen.add(id(f))
                    out.append(f)
        for f in self.hallucinations:  # in case it ran but wasn't added as a dimension
            if id(f) not in seen:
                seen.add(id(f))
                out.append(f)
        return out

    def counts_by_severity(self) -> dict[str, int]:
        counts = {s: 0 for s in SEVERITIES}
        for f in self.all_findings():
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "meta": {
                "model": self.model,
                "provider": self.provider,
                "depth": self.depth,
                "venue_id": self.venue_id,
                "parse_engine": self.parse_engine,
                "was_ocr": self.was_ocr,
                "created_at": self.created_at,
            },
            "recommendation": self.recommendation,
            "verdict": self.verdict,
            "overall_score": round(self.overall_score, 1),
            "headline_summary": self.headline_summary,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "venue_fit": self.venue_fit.to_dict() if self.venue_fit else None,
            "citation_check": self.citation_check.to_dict() if self.citation_check else None,
            "hallucinations": [f.to_dict() for f in self.hallucinations],
            "action_items": [a.to_dict() for a in self.action_items],
            "accounting": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.prompt_tokens + self.completion_tokens,
                "cost_usd": self.cost_usd,
                "n_calls": self.n_calls,
            },
            "warnings": self.warnings,
        }
