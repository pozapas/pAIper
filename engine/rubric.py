"""The Q1 review rubric: reviewer persona, scoring scale, and per-dimension specs.

The criteria below are distilled from the AIT-Lab `paper-quality-checklist`
(full-paper-review / statistical-audit agents, universal + statistical + ML-model +
causal-inference docs) and standard journal/conference reviewing practice. This is the
"baked-in skill knowledge" — no skills are executed at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────────────
# Shared prompt building blocks
# ─────────────────────────────────────────────────────────────────────────────

REVIEWER_PERSONA = """\
You are a senior reviewer and associate editor for a top-tier (Q1) venue, with deep \
expertise across transportation engineering, traffic safety, autonomous vehicles, \
travel behavior, AI/ML, computer vision, NLP, and applied statistics. You review at the \
level of a program-committee meta-reviewer: rigorous, specific, fair, and constructive. \
You reward genuine contributions and you do not invent problems, but you hold claims to \
the evidentiary standard of a leading journal."""

SCORING_GUIDE = """\
Score this dimension from 0 to 10:
- 9-10: exemplary; among the best you have seen at a top venue.
- 7-8:  strong; minor improvements only.
- 5-6:  acceptable but with real weaknesses that need work.
- 3-4:  weak; major revision required on this dimension.
- 0-2:  unacceptable as-is; fundamental problems.
Calibrate honestly. Most submitted manuscripts score 4-7 on most dimensions."""

SEVERITY_GUIDE = """\
Classify each finding:
- CRITICAL: blocks acceptance (invalid method, unsupported central claim, broken proof, leakage).
- MAJOR:    must be fixed for acceptance (missing baseline, no uncertainty, weak positioning).
- MINOR:    improves the paper (clarity, a missing detail, presentation).
- PRAISE:   a genuine strength worth naming."""

JSON_INSTRUCTIONS = """\
Return ONLY a JSON object (no prose, no code fences) with EXACTLY this shape:
{
  "score": <number 0-10>,
  "summary": "<2-4 sentences: your overall judgment of this dimension>",
  "findings": [
    {
      "severity": "CRITICAL" | "MAJOR" | "MINOR" | "PRAISE",
      "title": "<short specific title>",
      "evidence": "<a SHORT verbatim quote from the paper, or '' if none>",
      "issue": "<what is wrong/right and WHY it matters at a Q1 venue>",
      "recommendation": "<concrete, actionable fix; '' for PRAISE>",
      "section": "<section name if identifiable, else ''>"
    }
  ]
}
Rules: 3-8 findings is typical. Be concrete and reference specifics. Quote real text in
"evidence". Do not flag issues that are clearly resolved elsewhere in the provided text.
If the dimension genuinely has no issues, return a high score with at least one PRAISE."""


def build_system(extra: str = "") -> str:
    base = f"{REVIEWER_PERSONA}\n\n{SCORING_GUIDE}\n\n{SEVERITY_GUIDE}"
    return f"{base}\n\n{extra}" if extra else base


# ─────────────────────────────────────────────────────────────────────────────
# Dimension specifications
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PassSpec:
    key: str
    label: str
    weight: float
    sections: tuple[str, ...]   # canonical sections to prioritize as context
    criteria: str               # the dimension-specific checklist (baked knowledge)


DIMENSION_SPECS: dict[str, PassSpec] = {
    "contribution": PassSpec(
        key="contribution",
        label="Contribution & Positioning",
        weight=1.4,
        sections=("abstract", "introduction", "conclusion"),
        criteria="""\
Evaluate the CONTRIBUTION and POSITIONING.
- Is there ONE clear, specific contribution, stateable as "We propose X, which achieves Y on Z, enabling W"?
- Is the novelty claim backed by comparison with the CLOSEST prior work (not just "no one has done this")?
- Do title, abstract, introduction, and conclusion describe the SAME contribution consistently?
- Are strong words ("first", "novel", "state-of-the-art", "causal", "robust", "safe", "generalizable")
  each directly supported by evidence in the paper?
- Is the gap/motivation real, or is it an application of existing methods presented as a method contribution?
- Is the scope of the claim matched to the evidence (narrow results not sold as broadly applicable)?""",
    ),
    "related_work": PassSpec(
        key="related_work",
        label="Related Work & Baselines",
        weight=1.0,
        sections=("related_work", "background", "introduction"),
        criteria="""\
Evaluate RELATED WORK and BASELINE COVERAGE.
- Does it explain the GAP, or merely summarize prior work?
- Are baselines/comparisons CURRENT (within ~3 years for fast-moving fields)? A neural net beating a 2015 method is insufficient.
- Domain coverage: a transportation paper must cite transportation literature; a CS paper must cite the relevant benchmark/SOTA papers and negative results.
- Are concurrent/very recent works acknowledged?
- Is the closest competing method identified and fairly characterized?""",
    ),
    "methodology": PassSpec(
        key="methodology",
        label="Methodology & Research Design",
        weight=1.4,
        sections=("methods", "background", "experiments"),
        criteria="""\
Evaluate METHODOLOGY and RESEARCH DESIGN.
- Is the research question/hypothesis explicit?
- Is the method TYPE appropriate for the question (explanatory / predictive / causal / descriptive / simulation / evaluation)?
- Is the unit of analysis stated and consistent?
- Are key ASSUMPTIONS named and, where possible, tested? Are alternative explanations addressed?
- Data & protocol: are source, collection period, geography, sampling frame, and exclusion criteria documented?
- Is the train/validation/test (or spatial/temporal) split described and JUSTIFIED?
- Is DATA LEAKAGE prevented (preprocessing fit on train only; test untouched until final eval; spatial/temporal leakage for mobility/CV/video)?
- For causal claims: is there a valid identification strategy (design, DAG, IV/DiD/RDD/matching), not association dressed as causation?""",
    ),
    "statistics": PassSpec(
        key="statistics",
        label="Statistical Validity",
        weight=1.2,
        sections=("methods", "experiments", "results"),
        criteria="""\
Perform a STATISTICAL AUDIT.
- Is the statistical test appropriate for the data structure (paired/unpaired, parametric/non-parametric, count/continuous, ordinal)?
- Are assumptions checked (normality, equal variance, independence, proportional hazards, overdispersion)?
- Is multiple-comparison correction applied where needed?
- Are EFFECT SIZES and CONFIDENCE INTERVALS reported in addition to p-values? Are results given in domain units?
- For ML: are results over MULTIPLE seeds/folds with mean±std or error bars? Is the test set used only once? Are comparison tests appropriate (e.g. paired bootstrap, not raw single-run deltas)?
- Domain-specific (if applicable): correct exposure denominator (VMT/AADT/person-trips) for safety; ordinal models (not OLS) for crash severity; regression-to-the-mean handled in before/after designs; spatial clustering modeled (NB/HGLM/GEE).
- Are sample sizes adequate and is power discussed where relevant?""",
    ),
    "results_claims": PassSpec(
        key="results_claims",
        label="Results & Claim Support",
        weight=1.3,
        sections=("results", "experiments", "discussion", "conclusion"),
        criteria="""\
Evaluate whether RESULTS support the CLAIMS.
- Does every major claim have a corresponding result, citation, proof, or stated limitation?
- Do reported numbers in text match tables/figures? Any internal numeric inconsistencies?
- Are baselines fair, current, and tuned under a comparable budget? Any cherry-picking?
- Are negative/null results reported, or is there selective reporting?
- Is uncertainty reported on the MAIN results?
- Is there overclaiming relative to what the experiments actually show? Does the conclusion generalize beyond the evidence?""",
    ),
    "reproducibility": PassSpec(
        key="reproducibility",
        label="Reproducibility & Ethics",
        weight=0.9,
        sections=("methods", "experiments", "appendix", "conclusion"),
        criteria="""\
Evaluate REPRODUCIBILITY and RESEARCH ETHICS.
- Are data availability, code availability, random seeds, software/hardware, and hyperparameters stated?
- Could an independent expert reproduce the main result from what is described?
- For human-subjects/user studies: IRB/ethics approval, consent, compensation, recruitment reported?
- Privacy/data-access restrictions handled and disclosed?
- AI-use / LLM-in-the-loop disclosure where relevant; conflicts of interest and funding statements.
- Are artifacts (models, datasets, configs) described well enough to be useful?""",
    ),
    "writing": PassSpec(
        key="writing",
        label="Writing, Structure & Presentation",
        weight=0.8,
        sections=("abstract", "introduction", "results", "conclusion"),
        criteria="""\
Evaluate WRITING, STRUCTURE, and PRESENTATION.
- Is the abstract a faithful, self-contained summary that matches the body?
- Is the narrative logically ordered (problem -> gap -> approach -> evidence -> implication)?
- Are figures/tables self-explanatory, captioned, referenced, and necessary? Are axes/units/legends clear?
- Is notation consistent and defined before use?
- Is the prose precise (no vague claims, hedging that hides weakness, or undefined jargon)?
- Are length, section balance, and signposting appropriate for a Q1 venue?""",
    ),
}


# Weighted overall score helper -------------------------------------------------

def weighted_overall(scores: dict[str, float]) -> float:
    """scores: {dimension_key: score0-10}. Returns weighted mean over known dims."""
    num = 0.0
    den = 0.0
    for key, score in scores.items():
        w = DIMENSION_SPECS[key].weight if key in DIMENSION_SPECS else 1.0
        num += w * score
        den += w
    return (num / den) if den else 0.0


def recommendation_from_score(overall: float, n_critical: int) -> str:
    """Map overall score + critical count to an editorial recommendation."""
    if n_critical >= 2 or overall < 3.0:
        return "Reject"
    if n_critical >= 1 or overall < 5.0:
        return "Major Revision"
    if overall < 7.5:
        return "Minor Revision"
    return "Accept"
