"""
AI Paper Reviewer — Q1 edition
==============================
Multi-dimensional, venue-aware peer review with external citation verification.

Upload a paper (PDF / Word / LaTeX / Markdown / TXT or an arXiv URL) → get a
structured, scored, actionable Q1-grade review, displayed in-app and exportable to
Word / Markdown / PDF / JSON.

The review logic lives in the `engine/` package (UI-agnostic). This file is only the
Streamlit front-end.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import streamlit as st

# Inline SVG favicon (a paper + magnifier mark) — no emoji.
_FAVICON = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>"
    "<rect width='24' height='24' rx='6' fill='%230a0e1a'/>"
    "<g fill='none' stroke='%2322d3ee' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='M7 4h6l4 4v12H7z'/><circle cx='12' cy='13' r='2.5'/><line x1='13.8' y1='14.8' x2='16' y2='17'/>"
    "</g></svg>"
)

st.set_page_config(
    page_title="pAIper — AI Paper Reviewer",
    page_icon=_FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

from engine.config import DEPTHS, OCR_METHODS, PROVIDERS, env_var_for
from engine.engine import ReviewOptions, run_review
from engine.llm import LLMClient
from engine.report import ReviewReport
from engine.exporters.md_export import report_to_markdown
from engine.exporters.docx_export import report_to_docx
from ui import components as C
from ui.theme import inject as inject_theme

# Optional modules (land in later milestones); guard so the app always runs.
try:
    from engine.venues import list_venue_options  # type: ignore
except Exception:
    def list_venue_options():
        return [("", "No specific venue (general Q1 review)")]


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> dict:
    with st.sidebar:
        C.sidebar_header("Model & API", "key")

        with st.expander("Get an API key in 2 minutes", expanded=False):
            st.markdown(
                """
**Free options first:**

**Google Gemini — free tier (easiest free):**
1. Open [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in → **Create API key** → copy it.
3. Pick provider **Gemini** here and paste it.

**OpenRouter — one key, many models (incl. free):**
1. [openrouter.ai/keys](https://openrouter.ai/keys) → sign up → **Create Key**.
2. Browse [free models](https://openrouter.ai/models?q=free) (IDs end in `:free`).

**Paid:** [OpenAI](https://platform.openai.com/api-keys) ·
[Anthropic](https://console.anthropic.com/settings/keys) ·
[Mistral](https://console.mistral.ai/api-keys)

*Your key stays in this browser session only. It is sent solely to the provider you
choose (and to CrossRef / OpenAlex / Semantic Scholar for citation checks). It is never
stored or logged by this app. Reviews use tokens billed to your own account.*
"""
            )

        provider_name = st.selectbox("Provider", list(PROVIDERS.keys()), index=0)
        prov = PROVIDERS[provider_name]
        st.caption(prov["note"])

        api_key = st.text_input(
            f"{provider_name} API key",
            type="password",
            value=os.environ.get(prov["key_env"], ""),
            placeholder="paste your key…",
        )
        st.markdown(f"[Get a {provider_name} key]({prov['signup_url']})")

        model = st.selectbox("Model", prov["models"])
        custom_model = st.text_input(
            "Custom model ID (optional)",
            placeholder="e.g. anthropic/claude-opus-4.7",
            help="Overrides the dropdown. Use the provider's exact model ID.",
        )

        C.sidebar_header("Review depth", "layers")
        depth = st.radio(
            "Depth",
            list(DEPTHS.keys()),
            format_func=lambda k: DEPTHS[k].label,
            index=list(DEPTHS.keys()).index("standard"),
            label_visibility="collapsed",
        )
        st.caption(DEPTHS[depth].desc)

        C.sidebar_header("Target venue (optional)", "target")
        venue_opts = list_venue_options()
        venue_id = st.selectbox(
            "Venue",
            [v[0] for v in venue_opts],
            format_func=lambda vid: dict(venue_opts).get(vid, vid),
            label_visibility="collapsed",
            help="Get a venue-specific submission checklist and rejection-risk analysis.",
        )

        C.sidebar_header("Options", "sliders")
        check_citations = st.toggle(
            "Verify citations online",
            value=False,
            help="Check each reference against CrossRef, Semantic Scholar and OpenAlex to "
                 "catch fabricated, missing, or chimeric citations. Requires internet; no extra key.",
        )

        with st.expander("Advanced", expanded=False):
            ocr_method = st.selectbox(
                "PDF parsing engine",
                list(OCR_METHODS.keys()),
                format_func=lambda k: OCR_METHODS[k]["label"],
                help="Only affects PDF inputs.",
            )
            st.caption(OCR_METHODS[ocr_method]["desc"])
            reasoning = st.selectbox(
                "Reasoning effort", ["(none)", "low", "medium", "high"], index=0,
                help="For models that support extended thinking (o-series, Claude, Gemini).",
            )
            concurrent = st.checkbox("Run dimensions in parallel", value=True,
                                     help="Faster. Turn off if your provider rate-limits.")
            max_citations = st.number_input("Max references to verify", 5, 200, 40, step=5)

        return {
            "provider_id": prov["provider_id"],
            "provider_name": provider_name,
            "api_key": api_key.strip(),
            "model": (custom_model.strip() or model),
            "depth": depth,
            "venue_id": venue_id,
            "check_citations": check_citations,
            "ocr_method": ocr_method,
            "reasoning": None if reasoning == "(none)" else reasoning,
            "concurrent": concurrent,
            "max_citations": int(max_citations),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────

def render_results(r: ReviewReport) -> None:
    C.recommendation_banner(r)
    C.stat_chips(r)

    tabs = st.tabs([
        "Verdict", "Findings", "Venue Fit",
        "Citations", "Action Plan", "Annotated", "Export",
    ])

    # ── Verdict ───────────────────────────────────────────────────────────────
    with tabs[0]:
        if r.headline_summary:
            st.markdown(f"#### Summary\n{r.headline_summary}")
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            C.section_header("Dimension scores", "bar-chart")
            C.score_bars(r.dimensions)
        with col2:
            radar = C.radar_svg(r.dimensions)
            if radar:
                C.section_header("Profile", "target")
                st.markdown(f'<div style="text-align:center">{radar}</div>', unsafe_allow_html=True)
        cs, cw = st.columns(2, gap="large")
        with cs:
            C.section_header("Strengths", "check-circle")
            for s in r.strengths or ["—"]:
                st.markdown(f"- {s}")
        with cw:
            C.section_header("Key weaknesses", "alert-triangle")
            for w in r.weaknesses or ["—"]:
                st.markdown(f"- {w}")
        if r.warnings:
            st.warning("  \n".join(f"- {w}" for w in r.warnings))

    # ── Findings ──────────────────────────────────────────────────────────────
    with tabs[1]:
        all_f = r.all_findings()
        if not all_f:
            st.info("No findings were produced.")
        else:
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                sev = st.multiselect("Severity", ["CRITICAL", "MAJOR", "MINOR", "PRAISE"],
                                     default=["CRITICAL", "MAJOR", "MINOR"])
            with c2:
                dim_labels = {d.key: d.label for d in r.dimensions}
                dims_sel = st.multiselect("Dimension", list(dim_labels.keys()),
                                          format_func=lambda k: dim_labels.get(k, k))
            with c3:
                q = st.text_input("Search", placeholder="keyword…")
            shown = [
                f for f in all_f
                if f.severity in sev
                and (not dims_sel or f.dimension in dims_sel)
                and (not q or q.lower() in (f.title + f.issue + f.evidence).lower())
            ]
            order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "PRAISE": 3}
            shown.sort(key=lambda f: order.get(f.severity, 9))
            st.caption(f"Showing {len(shown)} of {len(all_f)} findings")
            for f in shown:
                C.finding_card(f)

    # ── Venue Fit ─────────────────────────────────────────────────────────────
    with tabs[2]:
        v = r.venue_fit
        if not v:
            st.info("No venue selected. Pick a target venue in the sidebar to get a "
                    "submission checklist and rejection-risk analysis.")
        else:
            st.markdown(f"### {v.venue_name}")
            st.progress(v.fit_score / 100, text=f"Fit score: {v.fit_score}/100")
            if v.scope_rationale:
                st.markdown(v.scope_rationale)
            if v.rejection_risks:
                C.section_header("Top rejection risks", "alert-triangle")
                for risk in v.rejection_risks:
                    st.markdown(f"- {risk}")
            if v.checklist:
                lbl = "Submission checklist" + (" · model-generated" if v.checklist_generated else "")
                C.section_header(lbl, "list-checks")
                for c in v.checklist:
                    C.checklist_row(c.text, c.status, c.note)

    # ── Citations ─────────────────────────────────────────────────────────────
    with tabs[3]:
        cc = r.citation_check
        if not cc or not cc.enabled:
            st.info("Citation verification was off. Enable “Verify citations online” in the "
                    "sidebar to check references against CrossRef, Semantic Scholar and OpenAlex.")
        elif cc.n_refs == 0:
            st.warning(cc.note or "No references could be extracted from this document.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("References", cc.n_refs)
            m2.metric("Verified", cc.n_verified)
            m3.metric("Need attention", cc.n_suspicious)
            if cc.note:
                st.caption(cc.note)
            show_only = st.checkbox("Show only references needing attention", value=False)
            for c in cc.items:
                if show_only and c.status == "VERIFIED":
                    continue
                label = c.title or c.raw[:160]
                if c.year:
                    label += f"  ({c.year})"
                C.checklist_row(label, c.status, c.note, link=c.match_url)

    # ── Action Plan ───────────────────────────────────────────────────────────
    with tabs[4]:
        if not r.action_items:
            st.info("No action items.")
        from ui.theme import SEV_COLORS as _SC
        for i, a in enumerate(r.action_items, 1):
            color = _SC.get(a.priority, "#94a3b8")
            st.markdown(
                f'<div style="display:flex;gap:.6rem;align-items:baseline;margin:.45rem 0">'
                f'<span style="font-weight:800;color:#64748b">{i}.</span>'
                f'<span class="badge" style="background:{color}22;color:{color}">{C.esc(a.priority)}</span>'
                f'<span style="font-size:.92rem;color:#dbe3f0">{C.esc(a.text)}</span></div>',
                unsafe_allow_html=True,
            )

    # ── Annotated ─────────────────────────────────────────────────────────────
    with tabs[5]:
        st.caption("Findings with quoted evidence, grouped by dimension.")
        for d in r.dimensions:
            anchored = [f for f in d.findings if f.evidence]
            if not anchored:
                continue
            st.markdown(f"**{d.label}**")
            for f in anchored:
                C.finding_card(f)

    # ── Export ────────────────────────────────────────────────────────────────
    with tabs[6]:
        slug = "".join(ch if ch.isalnum() else "-" for ch in (r.title or "review").lower())[:50]
        md = report_to_markdown(r)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Word (.docx)", report_to_docx(r),
                               file_name=f"{slug}-review.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               use_container_width=True)
        with c2:
            st.download_button("Markdown", md, file_name=f"{slug}-review.md",
                               mime="text/markdown", use_container_width=True)
        with c3:
            st.download_button("JSON", json.dumps(r.to_dict(), indent=2, ensure_ascii=False),
                               file_name=f"{slug}-review.json", mime="application/json",
                               use_container_width=True)
        with c4:
            try:
                from engine.exporters.pdf_export import report_to_pdf
                st.download_button("PDF", report_to_pdf(r), file_name=f"{slug}-review.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception:
                st.button("PDF (use Word → Save as PDF)", disabled=True, use_container_width=True)
        st.markdown("---")
        with st.expander("Preview Markdown report"):
            st.markdown(md)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    inject_theme()
    st.session_state.setdefault("intro_seen", False)

    def mark_intro_seen() -> None:
        st.session_state.intro_seen = True

    if not st.session_state.intro_seen:
        if hasattr(st, "dialog"):
            @st.dialog(
                "pAIper Review Console",
                width="medium",
                dismissible=False,
                icon=":material/rate_review:",
                on_dismiss=mark_intro_seen,
            )
            def _intro_dialog() -> None:
                C.intro_popup()
                _, intro_btn_col = st.columns([5.4, 1.35])
                with intro_btn_col:
                    if st.button("Start Review", type="primary", use_container_width=True, key="intro_start"):
                        mark_intro_seen()
                        st.rerun()

            _intro_dialog()
        else:
            C.intro_popup()
            _, intro_btn_col = st.columns([5.4, 1.35])
            with intro_btn_col:
                if st.button("Start Review", type="primary", use_container_width=True, key="intro_start_fallback"):
                    mark_intro_seen()
                    st.rerun()

    C.hero()
    cfg = render_sidebar()

    st.session_state.setdefault("report", None)
    st.session_state.setdefault("reviewed_name", None)

    C.section_header("Upload your manuscript", "upload")
    uploaded = st.file_uploader(
        "Drop a file",
        type=["pdf", "docx", "tex", "md", "markdown", "txt"],
        label_visibility="collapsed",
        help="PDF, Word (.docx), LaTeX (.tex), Markdown (.md), or plain text (.txt).",
    )
    arxiv_url = st.text_input("…or paste an arXiv URL", placeholder="https://arxiv.org/abs/2401.00001")

    run = st.button("Run Review", type="primary", use_container_width=False,
                    disabled=not (uploaded or arxiv_url.strip()))

    if run:
        if not cfg["api_key"]:
            st.error(f"Please enter your {cfg['provider_name']} API key in the sidebar.")
            return

        # Build the input path
        tmp_path = None
        title_override = ""
        if uploaded is not None:
            ext = Path(uploaded.name).suffix.lower()
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = Path(tmp.name)
            source = tmp_path
            title_override = Path(uploaded.name).stem
            display_name = uploaded.name
        else:
            source = arxiv_url.strip()
            display_name = source

        llm = LLMClient(
            provider_id=cfg["provider_id"],
            model=cfg["model"],
            api_key=cfg["api_key"],
            reasoning_effort=cfg["reasoning"],
            default_max_tokens=DEPTHS[cfg["depth"]].max_output_tokens,
        )
        options = ReviewOptions(
            depth=cfg["depth"],
            venue_id=cfg["venue_id"],
            check_citations=cfg["check_citations"],
            max_citations=cfg["max_citations"],
            concurrent=cfg["concurrent"],
            ocr_method=cfg["ocr_method"],
        )

        bar = st.progress(0.0)
        status = st.empty()

        def progress(p: float, msg: str) -> None:
            bar.progress(min(max(p, 0.0), 1.0))
            status.markdown(f"<div style='color:#7dd3fc;font-size:.85rem'>{C.esc(msg)}</div>",
                            unsafe_allow_html=True)

        try:
            report = run_review(source, llm, options,
                                title_override=title_override, progress=progress)
            st.session_state.report = report
            st.session_state.reviewed_name = display_name
            bar.empty()
            status.empty()
        except Exception as exc:
            bar.empty()
            st.error(f"Review failed: {exc}")
            import traceback
            with st.expander("Technical details"):
                st.code(traceback.format_exc())
            return
        finally:
            if tmp_path:
                tmp_path.unlink(missing_ok=True)

    if st.session_state.report:
        C.section_header(f"Review — {st.session_state.reviewed_name or 'paper'}", "check-circle")
        render_results(st.session_state.report)
    elif not run:
        C.landing()


if __name__ == "__main__":
    main()
