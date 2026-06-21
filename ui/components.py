"""Reusable dark-theme Streamlit render components for pAIper.

Dependency-free SVG/HTML (no plotly/matplotlib). No emojis — icons come from ui.icons.
"""

from __future__ import annotations

import base64
import html
import math
from functools import lru_cache
from pathlib import Path

import streamlit as st

from engine.report import DimensionResult, Finding, ReviewReport
from .icons import DIM_ICON, SEV_ICON, STATUS_ICON, ic
from .theme import REC_COLORS, SEV_COLORS, STATUS_COLORS

_ASSET_DIR = Path(__file__).resolve().parent / "assets"


def esc(s: str) -> str:
    return html.escape(s or "")


@lru_cache(maxsize=8)
def _asset_data_uri(filename: str) -> str:
    path = _ASSET_DIR / filename
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


# ─────────────────────────────────────────────────────────────────────────────
def hero(subtitle: str = "") -> None:
    sub = esc(subtitle) or (
        "A multi-dimensional, venue-aware peer reviewer with citation verification "
        "for transportation, CS, computer vision, NLP &amp; ML manuscripts."
    )
    intro_uri = _asset_data_uri("paiper-intro.png")
    brand_mark = (
        f'<img src="{intro_uri}" alt="" />'
        if intro_uri else ic('logo', 26, '#0a0e1a')
    )
    pills = [
        ("gauge", "9-dimension Q1 rubric"),
        ("target", "Venue checklists"),
        ("link", "Citation verification"),
        ("cpu", "Ollama / local model"),
        ("file-text", "PDF · Word · LaTeX · Markdown"),
    ]
    pill_html = "".join(f'<span class="pill">{ic(n,14)}{esc(t)}</span>' for n, t in pills)
    st.markdown(
        f"""
<div class="hero">
  <div class="brand">
    <div class="mark">{brand_mark}</div>
    <h1>p<span class="ai">AI</span>per</h1>
  </div>
  <p>{sub}</p>
  <div class="pills">{pill_html}</div>
</div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
def score_ring_svg(score: float, size: int = 120, on_color: bool = False) -> str:
    pct = max(0.0, min(1.0, score / 10.0))
    r = size / 2 - 10
    c = 2 * math.pi * r
    off = c * (1 - pct)
    cx = cy = size / 2
    if on_color:                      # ring sits on a colored banner → dark ink
        track, prog, txt, sub = "rgba(10,14,26,0.25)", "#0a0e1a", "#0a0e1a", "rgba(10,14,26,0.7)"
    else:
        prog = "#34d399" if score >= 7.5 else "#fbbf24" if score >= 5 else "#fb923c" if score >= 3 else "#f87171"
        track, txt, sub = "#1a2336", "#e7ecf5", "#94a3b8"
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="11"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{prog}" stroke-width="11"
    stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}"
    transform="rotate(-90 {cx} {cy})"/>
  <text x="{cx}" y="{cy-1}" text-anchor="middle" font-size="30" font-weight="800" fill="{txt}"
    font-family="Inter">{score:.1f}</text>
  <text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="11" fill="{sub}" font-family="Inter">/ 10</text>
</svg>"""


def radar_svg(dims: list[DimensionResult], size: int = 340) -> str:
    dims = [d for d in dims if not d.error]
    n = len(dims)
    if n < 3:
        return ""
    canvas_w = size + 138
    canvas_h = size + 30
    cx = canvas_w / 2
    cy = canvas_h / 2
    R = size / 2 - 66
    rings = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = [f"{cx + R*frac*math.cos(-math.pi/2 + 2*math.pi*i/n):.1f},"
               f"{cy + R*frac*math.sin(-math.pi/2 + 2*math.pi*i/n):.1f}" for i in range(n)]
        rings.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="#26304a" stroke-width="1"/>')
    spokes, labels, data_pts = [], [], []
    for i, d in enumerate(dims):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        ex, ey = cx + R*math.cos(ang), cy + R*math.sin(ang)
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#26304a" stroke-width="1"/>')
        frac = max(0.04, d.score / 10.0)
        data_pts.append(f"{cx + R*frac*math.cos(ang):.1f},{cy + R*frac*math.sin(ang):.1f}")
        lx, ly = cx + (R+28)*math.cos(ang), cy + (R+28)*math.sin(ang)
        anchor = "middle" if abs(math.cos(ang)) < 0.3 else ("start" if math.cos(ang) > 0 else "end")
        short = {
            "contribution": "Contribution",
            "related_work": "Related Work",
            "methodology": "Methodology",
            "statistics": "Statistical Validity",
            "results_claims": "Results",
            "reproducibility": "Reproducibility",
            "writing": "Writing",
        }.get(d.key, d.label.split("&")[0].split(",")[0].strip())
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="10.5" fill="#d7dbe0" font-family="Inter">{esc(short)}</text>'
            f'<text x="{lx:.1f}" y="{ly+12:.1f}" text-anchor="{anchor}" font-size="10" font-weight="800" fill="#ff9f43" font-family="Inter">{d.score:.1f}</text>'
        )
    return f"""
<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" style="max-width:100%;height:auto">
  {''.join(rings)}{''.join(spokes)}
  <polygon points="{' '.join(data_pts)}" fill="rgba(255,159,67,0.16)" stroke="#ff9f43" stroke-width="2"/>
  {''.join(f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="2.6" fill="#ffd09a"/>' for p in data_pts)}
  {''.join(labels)}
</svg>"""


# ─────────────────────────────────────────────────────────────────────────────
def recommendation_banner(r: ReviewReport) -> None:
    color = REC_COLORS.get(r.recommendation, "#64748b")
    st.markdown(
        f"""
<div class="rec-banner" style="background:linear-gradient(120deg,{color},{color}cc)">
  <div>{score_ring_svg(r.overall_score, 104, on_color=True)}</div>
  <div>
    <div class="rec-label">Editorial recommendation</div>
    <div class="rec-value">{esc(r.recommendation)}</div>
    <div class="rec-verdict">{esc(r.verdict)}</div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def stat_chips(r: ReviewReport) -> None:
    counts = r.counts_by_severity()
    tok = r.prompt_tokens + r.completion_tokens
    cost = f"${r.cost_usd:.3f}" if r.cost_usd is not None else "—"
    items = [
        ("x-circle", counts["CRITICAL"], "Critical", SEV_COLORS["CRITICAL"]),
        ("alert-triangle", counts["MAJOR"], "Major", SEV_COLORS["MAJOR"]),
        ("alert-circle", counts["MINOR"], "Minor", SEV_COLORS["MINOR"]),
        ("check-circle", counts["PRAISE"], "Strengths", SEV_COLORS["PRAISE"]),
        ("cpu", f"{tok:,}", "Tokens", "#a5b4fc"),
        ("zap", cost, "Est. cost", "#7dd3fc"),
    ]
    html_chips = "".join(
        f'<div class="chip"><div class="top">{ic(i,14,c)}'
        f'<span class="v" style="color:{c}">{esc(str(v))}</span></div>'
        f'<div class="l">{esc(l)}</div></div>'
        for i, v, l, c in items
    )
    st.markdown(f'<div class="chips">{html_chips}</div>', unsafe_allow_html=True)


def score_bars(dims: list[DimensionResult]) -> None:
    rows = []
    for d in dims:
        pct = max(0, min(100, d.score * 10))
        icon = ic(DIM_ICON.get(d.key, "info"), 16)
        rows.append(
            f'<div class="dim-row"><span class="ico">{icon}</span>'
            f'<div class="name">{esc(d.label)}</div>'
            f'<div class="dim-track"><div class="dim-fill" style="width:{pct:.0f}%"></div></div>'
            f'<div class="dim-score">{d.score:.1f}</div></div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def finding_card(f: Finding) -> None:
    color = SEV_COLORS.get(f.severity, "#64748b")
    badge_ic = ic(SEV_ICON.get(f.severity, "info"), 12, color)
    quote = f'<div class="quote">{esc(f.evidence[:600])}</div>' if f.evidence else ""
    fix = (f'<div class="fix">{ic("check",14,"#34d399")}<span><b>Fix:</b> {esc(f.recommendation)}</span></div>'
           if f.recommendation else "")
    sect = f'<span class="tag">{ic("file-text",12)}{esc(f.section)}</span>' if f.section else ""
    st.markdown(
        f"""
<div class="fcard" style="border-left-color:{color}">
  <div class="ftop">
    <span class="badge" style="background:{color}22;color:{color}">{badge_ic}{esc(f.severity)}</span>
    <span class="ftitle">{esc(f.title)}</span>{sect}
  </div>
  {quote}
  <div class="issue">{esc(f.issue)}</div>
  {fix}
</div>""",
        unsafe_allow_html=True,
    )


def checklist_row(text: str, status: str, note: str = "", link: str = "") -> None:
    color = STATUS_COLORS.get(status, "#64748b")
    icon = ic(STATUS_ICON.get(status, "minus"), 13, "#0a0e1a")
    note_html = f'<div class="cnote">{esc(note)}</div>' if note else ""
    if link:
        note_html = note_html[:-6] + f' · <a href="{esc(link)}" target="_blank">source</a></div>' if note else \
            f'<div class="cnote"><a href="{esc(link)}" target="_blank">source</a></div>'
    st.markdown(
        f"""<div class="crow"><div class="stat" style="background:{color}">{icon}{esc(status)}</div>
<div><div class="ctext">{esc(text)}</div>{note_html}</div></div>""",
        unsafe_allow_html=True,
    )


def section_header(text: str, icon: str = "") -> None:
    ico = ic(icon, 16) if icon else ""
    st.markdown(f'<div class="shead">{ico}{esc(text)}</div>', unsafe_allow_html=True)


def sidebar_header(text: str, icon: str) -> None:
    st.markdown(f'<div class="sb-head">{ic(icon,15)}{esc(text)}</div>', unsafe_allow_html=True)


def intro_popup() -> None:
    workflow = [
        ("01", "Readiness", "Editorial verdict and risk map."),
        ("02", "Venue Fit", "Rubric matched to target outlet."),
        ("03", "Evidence", "Citation and claim verification."),
        ("04", "Revision", "Ranked fixes for the next draft."),
    ]
    workflow_html = "".join(
        f'<article class="intro-flow-card"><span>{esc(n)}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></article>'
        for n, t, d in workflow
    )
    venues = ["TRR", "IEEE T-ITS", "CVPR", "ACL", "NeurIPS", "ICLR"]
    venue_html = "".join(f'<span class="intro-vchip">{esc(v)}</span>' for v in venues)
    hill_paths = []
    for row in range(18):
        y0 = 45 + row * 9
        amp = 4 + row * 1.15
        pts = []
        for i in range(34):
            x = 6 + i * 8.2
            y = (
                y0
                + math.sin(i * 0.52 + row * 0.42) * amp * 0.35
                + math.cos(i * 0.24 + row * 0.61) * amp * 0.22
                + (i - 16.5) ** 2 * 0.045
            )
            pts.append(f"{x:.1f},{y:.1f}")
        hill_paths.append(
            f'<polyline class="hill-line hill-line-{row % 4}" points="{" ".join(pts)}" />'
        )
    hill_html = "".join(hill_paths)
    st.markdown(
        f"""
<div class="intro-wrap">
  <aside class="intro-hills-art">
    <div class="hills-glow"></div>
    <div class="hills-float-title">
      <span>Manuscripts That Stand</span>
      <strong>Stronger In Review</strong>
      <em>with verified claims</em>
    </div>
    <svg class="hills-svg" viewBox="0 0 280 245" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="hillStroke" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#f5f5f5" stop-opacity=".62"/>
          <stop offset=".55" stop-color="#9aa1a9" stop-opacity=".34"/>
          <stop offset="1" stop-color="#ff9f43" stop-opacity=".2"/>
        </linearGradient>
      </defs>
      <g class="hills-grid">{hill_html}</g>
      <path class="hills-horizon" d="M26 87 C70 50 118 112 162 74 S242 54 274 94"/>
    </svg>
    <div class="hills-caption">
      <span>Venue</span><span>Claims</span><span>Citations</span>
    </div>
    <div class="hills-credit">
      <span>Developed by <a href="https://pozapas.github.io/" target="_blank" rel="noopener noreferrer">Amir Rafe</a></span>
      <a class="github-link" href="https://github.com/pozapas/pAIper" target="_blank" rel="noopener noreferrer" aria-label="pozapas pAIper GitHub repository">
        <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
          <path d="M8 .2A8 8 0 0 0 5.47 15.8c.4.07.55-.17.55-.38v-1.49c-2.23.49-2.7-.95-2.7-.95-.36-.92-.89-1.17-.89-1.17-.73-.5.06-.49.06-.49.8.06 1.23.83 1.23.83.72 1.22 1.88.87 2.34.66.07-.52.28-.87.51-1.07-1.78-.2-3.65-.89-3.65-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82A7.65 7.65 0 0 1 8 4.07c.68 0 1.36.09 2 .27 1.52-1.03 2.19-.82 2.19-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.88 3.75-3.66 3.95.29.25.54.73.54 1.48v2.2c0 .21.14.46.55.38A8 8 0 0 0 8 .2Z"/>
        </svg>
        <span>pozapas/pAIper</span>
      </a>
    </div>
    <div class="hills-brand">p<span>AI</span>per Review Console</div>
  </aside>
  <section class="intro-copy-mini">
    <span class="intro-kicker">AI Manuscript Review Console</span>
    <h2>Pressure-test before peer review.</h2>
    <p class="intro-lede">pAIper produces an editor-style readiness report: venue alignment,
    citation integrity, claim risk, method gaps, and ranked revision actions.</p>
    <div class="intro-note">{ic("lock",14)}<span>Session-only API key; citation checks use public scholarly indexes.</span></div>
    <div class="intro-flow">{workflow_html}</div>
    <div class="intro-venue-row">
      <span>Built for venues</span>
      <div>{venue_html}</div>
    </div>
  </section>
</div>""",
        unsafe_allow_html=True,
    )
    return

    intro_uri = _asset_data_uri("paiper-intro.png")
    art_html = (
        f'<img class="intro-art" src="{intro_uri}" alt="pAIper AI manuscript review visual" />'
        if intro_uri else f'<div class="intro-art-fallback">{ic("logo", 56)}</div>'
    )
    steps = [
        ("Add your key", "Choose a provider and paste an API key. Gemini and OpenRouter free options are supported."),
        ("Set the target", "Select review depth and, when relevant, the venue you are aiming for."),
        ("Upload", "Drop a PDF, Word, LaTeX, Markdown, or text file, or paste an arXiv URL."),
        ("Get the review", "Read verdicts, findings, venue fit, citations, and exports in one place."),
    ]
    steps_html = "".join(
        f'<div class="intro-step"><div class="n">{i}</div><div><h5>{esc(t)}</h5><p>{esc(d)}</p></div></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    venues = [
        "Transportation Research A-F", "Transportation Science", "TRR",
        "Accident Analysis & Prevention", "IEEE T-ITS", "IEEE T-IV",
        "TRBAM", "ITSC", "IV", "CVPR", "ICCV", "WACV",
        "ACL", "EMNLP", "NeurIPS", "ICLR", "ICML", "AAAI", "KDD",
        "SIGSPATIAL", "CoRL",
    ]
    venue_html = "".join(
        f'<span class="intro-vchip">{ic("graduation",13)}{esc(v)}</span>'
        for v in venues
    )
    st.markdown(
        f"""
<div class="intro-wrap">
  <div class="intro-hero">
    <div class="intro-copy">
      <div class="intro-kicker">{ic("sparkles",14)} Venue-aware AI peer review</div>
      <h2>Review manuscripts before reviewers do.</h2>
      <p>pAIper reads a manuscript like a demanding associate editor: it scores a Q1-grade rubric,
      checks venue fit, tests citation integrity, surfaces unsupported claims, and turns the result into
      a prioritized revision plan.</p>
    </div>
    <div class="intro-art-shell">{art_html}</div>
  </div>
  <div class="intro-panels">
    <div class="intro-panel">
      <div class="intro-panel-title">{ic("list-checks",16)} How it works</div>
      <div class="intro-steps">{steps_html}</div>
    </div>
    <div class="intro-panel">
      <div class="intro-panel-title">{ic("graduation",16)} Built for these venues</div>
      <div class="intro-venues">{venue_html}</div>
    </div>
  </div>
  <div class="intro-note">{ic("lock",15)}
    <span>Bring-your-own-key. Your key stays in the browser session and is sent only to the selected
    model provider and citation-check services.</span>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Landing page (shown before a review runs)
# ─────────────────────────────────────────────────────────────────────────────

def landing() -> None:
    features = [
        ("gauge", "Q1-grade rubric", "Nine scored dimensions — contribution, methodology, statistics, results, reproducibility, writing and more — with an editorial verdict and a prioritized action plan."),
        ("target", "Venue-aware", "Pick a target venue and get a venue-specific submission checklist, scope fit score, and the rejection risks reviewers will actually raise."),
        ("link", "Citation verification", "Every reference is checked against CrossRef, Semantic Scholar and OpenAlex to flag fabricated, missing, or chimeric (real title / wrong authors) citations."),
        ("fingerprint", "Claim integrity", "Finds unsupported claims, overclaiming, and internal contradictions between abstract, methods, results and conclusions."),
        ("cpu", "Cloud or local model", "Bring your own key for OpenAI, Anthropic, Gemini, Mistral or OpenRouter, or run the offline app with Ollama for private local review."),
        ("download", "Useful outputs", "Export a polished report to Word, PDF, Markdown or JSON — ready to hand to co-authors or attach to a revision."),
    ]
    fcells = "".join(
        f'<div class="fcell"><div class="ico">{ic(i,20)}</div><h4>{esc(t)}</h4><p>{esc(d)}</p></div>'
        for i, t, d in features
    )
    section_header("What pAIper does", "sparkles")
    st.markdown(f'<div class="land-grid">{fcells}</div>', unsafe_allow_html=True)
    return

    section_header("How it works", "list-checks")
    steps = [
        ("Add your key", "Pick a provider and paste an API key — free Gemini or OpenRouter options included."),
        ("Set the target", "Choose review depth and, optionally, the venue you're aiming for."),
        ("Upload", "Drop a PDF, Word, LaTeX or Markdown file — or paste an arXiv link."),
        ("Get the review", "Read it in-app across tabs, then export to Word / PDF / Markdown / JSON."),
    ]
    steps_html = "".join(
        f'<div class="step"><div class="n">{i}</div><h5>{esc(t)}</h5><p>{esc(d)}</p></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    st.markdown(f'<div class="steps">{steps_html}</div>', unsafe_allow_html=True)

    section_header("Built for these venues", "graduation")
    venues = ["Transportation Research A–F", "Transportation Science", "TRR", "Accident Analysis & Prevention",
              "IEEE T-ITS", "IEEE T-IV", "TRBAM", "ITSC", "IV", "CVPR", "ICCV", "WACV",
              "ACL", "EMNLP", "NeurIPS", "ICLR", "ICML", "AAAI", "KDD", "SIGSPATIAL", "CoRL"]
    vchips = "".join(f'<span class="vchip">{ic("graduation",13)}{esc(v)}</span>' for v in venues)
    st.markdown(f'<div class="vbar">{vchips}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="margin-top:1rem" class="privacy">{ic("lock",16)}'
        '<span>Bring-your-own-key. Your API key stays in this browser session and is sent only to the '
        'provider you choose (and to CrossRef / OpenAlex / Semantic Scholar for citation checks). '
        'It is never stored or logged.</span></div>',
        unsafe_allow_html=True,
    )
