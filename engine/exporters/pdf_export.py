"""Render a ReviewReport to a styled PDF using reportlab Platypus.

Imported lazily by the UI; if reportlab is missing, the UI offers a graceful
"export Word and Save-as-PDF" fallback instead.
"""

from __future__ import annotations

import io

from ..report import ReviewReport

_SEV_HEX = {"CRITICAL": "#b91c1c", "MAJOR": "#c2410c", "MINOR": "#a16207", "PRAISE": "#15803d"}
_REC_HEX = {"Accept": "#15803d", "Minor Revision": "#a16207",
            "Major Revision": "#c2410c", "Reject": "#b91c1c"}
_STATUS_HEX = {"PASS": "#15803d", "FAIL": "#b91c1c", "UNCLEAR": "#a16207", "NA": "#64748b",
               "VERIFIED": "#15803d", "NOT_FOUND": "#b91c1c", "MISMATCH": "#c2410c",
               "UNPARSEABLE": "#64748b", "UNCHECKED": "#64748b"}


def report_to_pdf(r: ReviewReport) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    def esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=18, spaceAfter=6, textColor=colors.HexColor("#0f172a"))
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=4, textColor=colors.HexColor("#1e3a8a"))
    H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=2, textColor=colors.HexColor("#334155"))
    BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=9.5, leading=13, alignment=TA_LEFT)
    QUOTE = ParagraphStyle("QUOTE", parent=BODY, fontSize=8.5, leftIndent=10, textColor=colors.HexColor("#475569"),
                           backColor=colors.HexColor("#f1f5f9"), borderPadding=4, leading=12)
    SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8, textColor=colors.HexColor("#94a3b8"))

    flow = []
    flow.append(Paragraph(esc(r.title or "Review Report"), H1))
    rec_color = _REC_HEX.get(r.recommendation, "#334155")
    flow.append(Paragraph(
        f'<font color="{rec_color}"><b>Recommendation: {esc(r.recommendation)}</b></font>'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;Overall score: <b>{r.overall_score:.1f}/10</b>', BODY))
    if r.verdict:
        flow.append(Paragraph(f'<i>{esc(r.verdict)}</i>', BODY))
    meta = f"Model: {esc(r.model)} · Depth: {esc(r.depth)}"
    if r.venue_id:
        meta += f" · Venue: {esc(r.venue_id)}"
    flow.append(Paragraph(meta, SMALL))
    flow.append(Spacer(1, 8))

    if r.headline_summary:
        flow.append(Paragraph("Summary", H2))
        flow.append(Paragraph(esc(r.headline_summary), BODY))

    # scorecard table
    flow.append(Paragraph("Scorecard", H2))
    data = [["Dimension", "Score"]]
    for d in r.dimensions:
        data.append([esc(d.label), f"{d.score:.1f} / 10"])
    tbl = Table(data, colWidths=[4.6 * inch, 1.4 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    flow.append(tbl)

    def bullets(items):
        return ListFlowable(
            [ListItem(Paragraph(esc(x), BODY), leftIndent=12) for x in items],
            bulletType="bullet", start="•",
        )

    if r.strengths:
        flow.append(Paragraph("Strengths", H2))
        flow.append(bullets(r.strengths))
    if r.weaknesses:
        flow.append(Paragraph("Key Weaknesses", H2))
        flow.append(bullets(r.weaknesses))

    if r.action_items:
        flow.append(Paragraph("Action Plan (prioritized)", H2))
        rows = []
        for it in r.action_items:
            col = _SEV_HEX.get(it.priority, "#334155")
            rows.append(Paragraph(f'<font color="{col}"><b>[{esc(it.priority)}]</b></font> {esc(it.text)}', BODY))
        flow.append(ListFlowable([ListItem(p, leftIndent=12) for p in rows], bulletType="1"))

    # venue fit
    if r.venue_fit:
        v = r.venue_fit
        flow.append(Paragraph(f"Venue Fit — {esc(v.venue_name)}", H2))
        flow.append(Paragraph(f"<b>Fit score: {v.fit_score}/100</b>", BODY))
        if v.scope_rationale:
            flow.append(Paragraph(esc(v.scope_rationale), BODY))
        if v.rejection_risks:
            flow.append(Paragraph("Top rejection risks:", H3))
            flow.append(bullets(v.rejection_risks))
        if v.checklist:
            flow.append(Paragraph("Submission checklist:", H3))
            for c in v.checklist:
                col = _STATUS_HEX.get(c.status, "#64748b")
                flow.append(Paragraph(
                    f'<font color="{col}"><b>[{esc(c.status)}]</b></font> {esc(c.text)}'
                    + (f' <font color="#64748b"><i>{esc(c.note)}</i></font>' if c.note else ""), BODY))

    # citations
    if r.citation_check and r.citation_check.enabled:
        cc = r.citation_check
        flow.append(Paragraph("Citation Verification", H2))
        flow.append(Paragraph(
            f"Checked {cc.n_refs} references · {cc.n_verified} verified · "
            f"{cc.n_suspicious} need attention", BODY))
        if cc.note:
            flow.append(Paragraph(f"<i>{esc(cc.note)}</i>", SMALL))
        for c in cc.items:
            if c.status in ("NOT_FOUND", "MISMATCH"):
                col = _STATUS_HEX.get(c.status, "#64748b")
                flow.append(Paragraph(
                    f'<font color="{col}"><b>[{esc(c.status)}]</b></font> {esc(c.title or c.raw[:120])} '
                    f'<font color="#64748b"><i>{esc(c.note)}</i></font>', BODY))

    # detailed findings
    flow.append(Paragraph("Detailed Findings", H2))
    for d in r.dimensions:
        flow.append(Paragraph(f"{esc(d.label)} — {d.score:.1f}/10", H3))
        if d.error:
            flow.append(Paragraph(f"<i>Could not evaluate: {esc(d.error)}</i>", SMALL))
            continue
        if d.summary:
            flow.append(Paragraph(esc(d.summary), BODY))
        for f in d.findings:
            col = _SEV_HEX.get(f.severity, "#334155")
            flow.append(Paragraph(f'<font color="{col}"><b>[{esc(f.severity)}] {esc(f.title)}</b></font>', BODY))
            if f.evidence:
                flow.append(Paragraph(f'"{esc(f.evidence[:500])}"', QUOTE))
            if f.issue:
                flow.append(Paragraph(esc(f.issue), BODY))
            if f.recommendation:
                flow.append(Paragraph(f'<font color="#047857"><b>Fix:</b></font> {esc(f.recommendation)}', BODY))
            flow.append(Spacer(1, 3))

    tok = r.prompt_tokens + r.completion_tokens
    cost = f"~${r.cost_usd:.3f}" if r.cost_usd is not None else "n/a"
    flow.append(Spacer(1, 10))
    flow.append(Paragraph(
        f"Generated by AI Paper Reviewer · {r.created_at[:19]}Z · {tok:,} tokens · "
        f"{r.n_calls} calls · cost {cost}", SMALL))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            title=f"Review — {r.title}")
    doc.build(flow)
    return buf.getvalue()
