"""Venue registry + LLM-driven venue-fit evaluation.

Venue definitions live in `data/venues/*.yaml`. Each venue has a scope, evidence bar,
top rejection reasons, and a (hand-curated) submission checklist. `evaluate_venue`
asks the model to (1) score scope fit, (2) run the checklist against the paper, and
(3) surface this paper's specific rejection risks at this venue.
"""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

import engine  # noqa: F401
from reviewer.utils import count_tokens, truncate_text  # type: ignore

from .llm import LLMClient
from .parsing import ParsedPaper
from .report import ChecklistItem, VenueFit
from .rubric import REVIEWER_PERSONA

_VENUES_DIR = Path(__file__).resolve().parent.parent / "data" / "venues"

# Order families appear in the dropdown + their display labels.
_FAMILY_ORDER = ["general", "transportation", "cv", "nlp", "robotics", "spatial", "ml", "cs", "hci"]
_FAMILY_DISPLAY = {
    "general": "General",
    "transportation": "Transportation",
    "cv": "Computer Vision",
    "nlp": "NLP",
    "robotics": "Robotics",
    "spatial": "Spatial/Mobility",
    "ml": "ML",
    "cs": "CS/AI",
    "hci": "HCI",
}


@functools.lru_cache(maxsize=1)
def _load_registry() -> dict[str, dict]:
    """venue_id -> venue dict, plus '_family_labels'."""
    registry: dict[str, dict] = {}
    family_labels: dict[str, str] = {}
    if _VENUES_DIR.exists():
        for fp in sorted(_VENUES_DIR.glob("*.yaml")):
            try:
                data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            for v in data.get("venues", []):
                if isinstance(v, dict) and v.get("id"):
                    registry[v["id"]] = v
                    fam = v.get("family", "other")
                    family_labels.setdefault(fam, data.get("family_label", fam.title()))
    registry["_family_labels"] = family_labels  # type: ignore
    return registry


def get_venue(venue_id: str) -> dict | None:
    return _load_registry().get(venue_id)


def list_venue_options() -> list[tuple[str, str]]:
    """[(venue_id, "Family · Name"), …] for a selectbox. First entry = no venue."""
    reg = _load_registry()
    venues = [v for k, v in reg.items() if k != "_family_labels"]

    def fam_rank(v: dict) -> int:
        fam = v.get("family", "other")
        return _FAMILY_ORDER.index(fam) if fam in _FAMILY_ORDER else len(_FAMILY_ORDER)

    venues.sort(key=lambda v: (fam_rank(v), v.get("name", "")))
    opts: list[tuple[str, str]] = [("", "No specific venue (general Q1 review)")]
    for v in venues:
        if v.get("id") == "general_q1":
            label = "⭐ General Q1 Journal"
        else:
            fam = _FAMILY_DISPLAY.get(v.get("family", ""), v.get("family", "").title())
            label = f"{fam} · {v.get('name', v['id'])}"
        opts.append((v["id"], label))
    return opts


_VENUE_JSON = """\
Return ONLY a JSON object with this exact shape:
{
  "fit_score": <integer 0-100: how well this paper fits the venue's scope and bar>,
  "scope_rationale": "<2-4 sentences on scope/topic fit and the most important gap vs the venue's bar>",
  "rejection_risks": ["<this paper's most likely rejection reasons AT THIS VENUE>", ...],
  "checklist": [
    {"text": "<the checklist item, copied>", "status": "PASS"|"FAIL"|"UNCLEAR"|"NA",
     "note": "<short evidence/justification from the paper>"}
  ]
}
Judge each checklist item against the paper text. Use UNCLEAR when the paper does not
provide enough information. Be specific in notes; cite what the paper does or omits."""


def evaluate_venue(venue_id: str, paper: ParsedPaper, llm: LLMClient,
                   *, budget_tokens: int = 16000, max_output_tokens: int = 6144) -> VenueFit | None:
    venue = get_venue(venue_id)
    if not venue:
        return None

    checklist_items = list(venue.get("checklist") or [])
    generated = False
    checklist_block = "\n".join(f"- {c}" for c in checklist_items)
    if not checklist_items:
        generated = True
        checklist_block = (
            "(No fixed checklist provided — GENERATE 6-9 venue-appropriate checklist items "
            "from the scope and field norms below, then judge each against the paper.)"
        )

    context = paper.full_text
    if count_tokens(context) > budget_tokens:
        context = truncate_text(context, budget_tokens)

    system = (
        f"{REVIEWER_PERSONA}\n\nYou are assessing fit for a SPECIFIC venue and running its "
        f"submission checklist against the manuscript.\n\n{_VENUE_JSON}"
    )
    user = (
        f"VENUE: {venue.get('name')}\n"
        f"TYPE: {venue.get('type', '')}\n"
        f"SCOPE: {venue.get('scope', '')}\n"
        f"EVIDENCE BAR: {venue.get('evidence_bar', '')}\n"
        f"KNOWN TOP REJECTION REASONS: {'; '.join(venue.get('top_rejection_reasons', []))}\n\n"
        f"CHECKLIST:\n{checklist_block}\n\n"
        f"--- PAPER TITLE: {paper.title} ---\n{context}\n--- END PAPER ---\n\n"
        f"Return the venue-fit JSON."
    )
    data = llm.json(system, user, expected=dict, max_tokens=max_output_tokens)

    fit = VenueFit(
        venue_id=venue_id,
        venue_name=venue.get("name", venue_id),
        checklist_generated=generated,
    )
    if not isinstance(data, dict):
        fit.scope_rationale = "Venue evaluation could not be parsed from the model output."
        # still surface the static checklist so the user sees the criteria
        fit.checklist = [ChecklistItem(text=c, status="UNCLEAR") for c in checklist_items]
        fit.rejection_risks = list(venue.get("top_rejection_reasons", []))
        return fit

    try:
        fit.fit_score = max(0, min(100, int(round(float(data.get("fit_score", 0) or 0)))))
    except (TypeError, ValueError):
        fit.fit_score = 0
    fit.scope_rationale = str(data.get("scope_rationale", "")).strip()
    fit.rejection_risks = [str(x).strip() for x in data.get("rejection_risks", []) if str(x).strip()]
    if not fit.rejection_risks:
        fit.rejection_risks = list(venue.get("top_rejection_reasons", []))

    items = []
    for it in data.get("checklist", []):
        if not isinstance(it, dict):
            continue
        status = str(it.get("status", "UNCLEAR")).strip().upper()
        if status not in ("PASS", "FAIL", "UNCLEAR", "NA"):
            status = "UNCLEAR"
        items.append(ChecklistItem(
            text=str(it.get("text", "")).strip() or "(item)",
            status=status,
            note=str(it.get("note", "")).strip(),
        ))
    # if the model dropped the checklist, fall back to static items
    if not items and checklist_items:
        items = [ChecklistItem(text=c, status="UNCLEAR") for c in checklist_items]
    fit.checklist = items
    return fit
