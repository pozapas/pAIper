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

import importlib.util
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
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
from engine.engine import ReviewOptions, run_citation_audit, run_review
from engine.llm import LLMClient
from engine.report import ReviewReport
from engine.exporters.md_export import report_to_markdown
from engine.exporters.docx_export import report_to_docx
from engine.exporters.branding import GENERATED_BY, GITHUB_ICON_URL, PAIPER_REPO_LABEL, PAIPER_REPO_URL
from ui import components as C
from ui.theme import inject as inject_theme

# Optional modules (land in later milestones); guard so the app always runs.
try:
    from engine.venues import list_venue_options  # type: ignore
except Exception:
    def list_venue_options():
        return [("", "No specific venue (general Q1 review)")]


# ─────────────────────────────────────────────────────────────────────────────

def _ocr_setup_error(ocr_method: str, ocr_api_key: str = "") -> str:
    """Return a user-facing setup error for forced optional PDF parsers."""
    if ocr_method == "mistral":
        if not (ocr_api_key.strip() or os.environ.get("MISTRAL_API_KEY")):
            return "Mistral OCR needs a Mistral API key. Paste it in Advanced under PDF parsing engine, or choose Auto/PyMuPDF."
        if importlib.util.find_spec("mistral_ocr") is None:
            return "Mistral OCR support is not installed in this environment. Install the optional `mistral-ocr-cli` package, or choose Auto/PyMuPDF."
    return ""


def _friendly_review_error(exc: Exception) -> str:
    msg = str(exc)
    if "No module named 'mistral_ocr'" in msg:
        return "Mistral OCR support is not installed. Install the optional `mistral-ocr-cli` package, or choose Auto/PyMuPDF."
    if "MISTRAL_API_KEY not set" in msg:
        return "Mistral OCR needs a Mistral API key. Paste it in Advanced under PDF parsing engine, or choose Auto/PyMuPDF."
    if "Ollama is not reachable" in msg:
        return msg
    if "Ollama request failed" in msg:
        return msg
    return msg


def _uploaded_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    data = uploaded_file.getvalue()
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _provider_requires_key(provider: dict) -> bool:
    return bool(provider.get("requires_key", True))


def _normalize_ollama_url(base_url: str) -> str:
    url = (base_url or "http://localhost:11434").strip()
    if url and "://" not in url:
        url = "http://" + url
    return url.rstrip("/")


def _is_loopback_url(base_url: str) -> bool:
    host = (urllib.parse.urlparse(_normalize_ollama_url(base_url)).hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _fetch_ollama_models(base_url: str, timeout: float = 2.5) -> tuple[list[str], str]:
    url = _normalize_ollama_url(base_url)
    req = urllib.request.Request(f"{url}/api/tags", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        return [], f"Ollama returned HTTP {exc.code} at {url}."
    except Exception:
        return [], f"Ollama is not reachable at {url}."

    models = []
    for item in data.get("models", []):
        name = str(item.get("name", "")).strip()
        if name:
            models.append(name)
    return list(dict.fromkeys(models)), ""
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> dict:
    with st.sidebar:
        C.sidebar_header("Workflow", "sliders")
        run_mode_label = st.radio(
            "Run mode",
            ["Full review", "Citation check only"],
            index=0,
            horizontal=True,
            help=(
                "Full review scores the manuscript and can also verify citations. "
                "Citation check only verifies references without running the review rubric."
            ),
        )
        run_mode = "citation_only" if run_mode_label == "Citation check only" else "full"

        use_ai_reference_extraction = False
        if run_mode == "citation_only":
            C.sidebar_header("Citation audit", "link")
            st.caption(
                "BibTeX citation audits do not need an AI API key. Upload a .bib/.bibtex "
                "file and pAIper verifies references directly against public scholarly indexes."
            )
            use_ai_reference_extraction = st.toggle(
                "Use AI to extract references from manuscript",
                value=False,
                help=(
                    "Only needed when you do not have a BibTeX file. This sends manuscript "
                    "reference text to the selected model so pAIper can structure references before verification."
                ),
            )

        show_model_controls = run_mode == "full" or use_ai_reference_extraction
        provider_name = list(PROVIDERS.keys())[0]
        prov = PROVIDERS[provider_name]
        api_key = ""
        base_url = ""
        custom_model = ""
        model = ""

        if show_model_controls:
            C.sidebar_header(
                "Model & Privacy" if run_mode == "full" else "AI reference extraction",
                "key",
            )

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

**Private local option:** install [Ollama](https://ollama.com), run a model on your
own machine, then choose **Ollama / Local**. On the hosted Streamlit app, `localhost`
belongs to the cloud server, not your device; use the offline app for real local privacy
or provide a reachable Ollama-compatible endpoint.

*Your key stays in this browser session only. It is sent solely to the provider you
choose (and to CrossRef / OpenAlex / Semantic Scholar for citation checks). It is never
stored or logged by this app. Reviews use tokens billed to your own account.*
"""
                )

            provider_name = st.selectbox("Provider", list(PROVIDERS.keys()), index=0)
            prov = PROVIDERS[provider_name]
            st.caption(prov["note"])

            if _provider_requires_key(prov):
                api_key = st.text_input(
                    f"{provider_name} API key",
                    type="password",
                    value=os.environ.get(prov["key_env"], ""),
                    placeholder="paste your key...",
                )
                st.markdown(f"[Get a {provider_name} key]({prov['signup_url']})")
                model = st.selectbox("Model", prov["models"])
                custom_model = st.text_input(
                    "Custom model ID (optional)",
                    placeholder="e.g. anthropic/claude-opus-4.7",
                    help="Overrides the dropdown. Use the provider's exact model ID.",
                )
            else:
                base_url = st.text_input(
                    "Ollama endpoint",
                    value=os.environ.get(prov.get("base_url_env", "OLLAMA_BASE_URL"), "http://localhost:11434"),
                    placeholder="http://localhost:11434",
                    help=(
                        "Offline app: keep the default. Hosted app: use a reachable "
                        "Ollama-compatible HTTPS endpoint; the cloud server cannot see localhost on your device."
                    ),
                )
                st.markdown("[Install Ollama](https://ollama.com)")
                st.info(
                    "For private paper review, run pAIper locally with Ollama. "
                    "On paiper.streamlit.app, uploaded files still pass through Streamlit Cloud.",
                    icon=":material/privacy_tip:",
                )
                ollama_models, ollama_error = _fetch_ollama_models(base_url)
                if ollama_error:
                    if _is_loopback_url(base_url):
                        st.info(
                            "pAIper cannot reach Ollama at `localhost`. If you are using "
                            "`paiper.streamlit.app`, this is expected because the cloud app cannot "
                            "see Ollama on your device. For private local models, run pAIper locally "
                            "and start Ollama. To use Ollama from the hosted app, enter a reachable "
                            "Ollama-compatible endpoint.",
                            icon=":material/cloud_off:",
                        )
                    else:
                        st.warning(
                            f"{ollama_error} Enter a reachable Ollama-compatible endpoint.",
                            icon=":material/power_settings_new:",
                        )
                    model = ""
                elif ollama_models:
                    model = st.selectbox(
                        "Model",
                        ollama_models,
                        help="Loaded from your Ollama model registry via /api/tags.",
                    )
                    st.caption(f"{len(ollama_models)} installed Ollama model(s) detected.")
                else:
                    model = ""
                    st.warning(
                        "No Ollama models found. First install a model, for example: "
                        "`ollama pull llama3.1:8b`, then refresh this app.",
                        icon=":material/download:",
                    )
        elif run_mode == "citation_only":
            st.info(
                "No AI model is needed for BibTeX citation checks.",
                icon=":material/verified:",
            )

        if run_mode == "full":
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
        else:
            depth = "standard"
            venue_id = ""

        C.sidebar_header("Options", "sliders")
        if run_mode == "citation_only":
            check_citations = st.toggle(
                "Verify citations online",
                value=True,
                disabled=True,
                help="Citation-only mode always verifies references against public scholarly indexes.",
            )
        else:
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
            ocr_info = OCR_METHODS[ocr_method]
            ocr_api_key = ""
            if ocr_info.get("needs_key"):
                key_env = ocr_info["needs_key"]
                key_value = os.environ.get(key_env, "")
                if not key_value and key_env == prov["key_env"]:
                    key_value = api_key.strip()
                ocr_api_key = st.text_input(
                    ocr_info.get("key_label", "OCR API key"),
                    type="password",
                    value=key_value,
                    placeholder="paste your OCR key...",
                    help="Used only for PDF parsing. Stored in this browser session only.",
                    key="ocr_api_key_input",
                )
                if ocr_info.get("key_url"):
                    st.markdown(f"[Get a Mistral OCR key]({ocr_info['key_url']})")
            if show_model_controls:
                reasoning = st.selectbox(
                    "Reasoning effort", ["(none)", "low", "medium", "high"], index=0,
                    help="For models that support extended thinking (o-series, Claude, Gemini).",
                )
            else:
                reasoning = "(none)"
            if run_mode == "full":
                concurrent = st.checkbox("Run dimensions in parallel", value=True,
                                         help="Faster. Turn off if your provider rate-limits.")
            else:
                concurrent = False
            max_citations = st.number_input("Max references to verify", 5, 200, 40, step=5)

        return {
            "provider_id": prov["provider_id"],
            "provider_name": provider_name,
            "api_key": api_key.strip(),
            "base_url": _normalize_ollama_url(base_url) if prov["provider_id"] == "ollama" else base_url.strip(),
            "model": (custom_model.strip() or model),
            "run_mode": run_mode,
            "depth": depth,
            "venue_id": venue_id,
            "check_citations": check_citations,
            "use_ai_reference_extraction": use_ai_reference_extraction,
            "ocr_method": ocr_method,
            "ocr_api_key": ocr_api_key.strip(),
            "reasoning": None if reasoning == "(none)" else reasoning,
            "concurrent": concurrent,
            "max_citations": int(max_citations),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────

def _render_citations(r: ReviewReport) -> None:
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


def _render_export(r: ReviewReport) -> None:
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
    st.markdown(
        f"""
        <div style="display:inline-flex;align-items:center;gap:.42rem;margin:.72rem 0 .2rem;
                    color:#9aa1a9;font-size:.78rem;font-weight:800;">
          <img src="{GITHUB_ICON_URL}" alt="GitHub" width="14" height="14" />
          <span>{GENERATED_BY}</span>
          <span style="color:#424952">&middot;</span>
          <a href="{PAIPER_REPO_URL}" target="_blank" rel="noopener noreferrer"
             style="color:#ff9f43;text-decoration:none;">{PAIPER_REPO_LABEL}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    with st.expander("Preview Markdown report"):
        st.markdown(md)


def render_results(r: ReviewReport) -> None:
    if r.depth == "citation-only":
        cc = r.citation_check
        verified = cc.n_verified if cc else 0
        total = cc.n_refs if cc else 0
        flagged = cc.n_suspicious if cc else 0
        note = (cc.note if cc and cc.note else r.headline_summary) or ""
        st.markdown(
            f"""
<div class="citation-audit-banner">
  <div>
    <span>Citation audit</span>
    <h2>{C.esc(r.title or "Reference check")}</h2>
    <p>{C.esc(note)}</p>
  </div>
  <div class="citation-audit-metrics">
    <strong>{verified}/{total}</strong>
    <small>verified</small>
    <strong>{flagged}</strong>
    <small>need attention</small>
  </div>
</div>""",
            unsafe_allow_html=True,
        )
        tabs = st.tabs(["Citations", "Export"])
        with tabs[0]:
            _render_citations(r)
        with tabs[1]:
            _render_export(r)
        return

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
        st.markdown(
            f"""
            <div style="display:inline-flex;align-items:center;gap:.42rem;margin:.72rem 0 .2rem;
                        color:#9aa1a9;font-size:.78rem;font-weight:800;">
              <img src="{GITHUB_ICON_URL}" alt="GitHub" width="14" height="14" />
              <span>{GENERATED_BY}</span>
              <span style="color:#424952">&middot;</span>
              <a href="{PAIPER_REPO_URL}" target="_blank" rel="noopener noreferrer"
                 style="color:#ff9f43;text-decoration:none;">{PAIPER_REPO_LABEL}</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
    bib_uploaded = st.file_uploader(
        "Bibliography file for citation checks",
        type=["bib", "bibtex"],
        help=(
            "Recommended for LaTeX manuscripts and citation-only audits. "
            "When provided, pAIper verifies BibTeX entries directly without sending them to a model."
        ),
        key="bib_upload",
    )
    bibliography_text = _uploaded_text(bib_uploaded).strip()
    uploaded_ext = Path(uploaded.name).suffix.lower() if uploaded is not None else ""
    citation_requested = cfg["run_mode"] == "citation_only" or cfg["check_citations"]
    if uploaded_ext == ".tex" and citation_requested and not bibliography_text:
        st.warning(
            "LaTeX files usually contain citation keys, not full reference metadata. "
            "Upload the matching .bib/.bibtex file so pAIper can verify citations accurately.",
            icon=":material/library_books:",
        )
    elif bibliography_text:
        st.success(
            f"Bibliography attached: {bib_uploaded.name}. Citation checks will use these BibTeX entries.",
            icon=":material/task_alt:",
        )
    arxiv_url = st.text_input("…or paste an arXiv URL", placeholder="https://arxiv.org/abs/2401.00001")

    run_label = "Run Citation Check" if cfg["run_mode"] == "citation_only" else "Run Review"
    can_run = bool(uploaded or arxiv_url.strip() or (cfg["run_mode"] == "citation_only" and bibliography_text))
    run = st.button(run_label, type="primary", use_container_width=False, disabled=not can_run)

    if run:
        citation_only = cfg["run_mode"] == "citation_only"
        if citation_only and not bibliography_text and not cfg["use_ai_reference_extraction"]:
            st.error(
                "Citation-only mode does not need an AI API key when you upload a .bib/.bibtex file. "
                "Upload the bibliography file, or enable AI reference extraction in the sidebar "
                "if you only have a manuscript/reference list."
            )
            return
        needs_llm = (not citation_only) or (
            citation_only and cfg["use_ai_reference_extraction"] and not bibliography_text
        )
        prov = PROVIDERS[cfg["provider_name"]]
        if needs_llm and _provider_requires_key(prov) and not cfg["api_key"]:
            st.error(f"Please enter your {cfg['provider_name']} API key in the sidebar.")
            return
        if needs_llm and cfg["provider_id"] == "ollama" and not cfg["base_url"]:
            st.error("Please enter an Ollama endpoint, for example http://localhost:11434.")
            return
        if needs_llm and cfg["provider_id"] == "ollama" and not cfg["model"]:
            st.error("No Ollama models were found. First install a model with `ollama pull <model-name>`.")
            return
        if uploaded_ext == ".tex" and citation_requested and not bibliography_text:
            st.error("Please upload the matching .bib or .bibtex file before running citation verification.")
            return

        if uploaded is not None and Path(uploaded.name).suffix.lower() == ".pdf":
            ocr_error = _ocr_setup_error(cfg["ocr_method"], cfg.get("ocr_api_key", ""))
            if ocr_error:
                st.error(ocr_error)
                return
            ocr_key_env = OCR_METHODS[cfg["ocr_method"]].get("needs_key")
            if ocr_key_env and cfg.get("ocr_api_key"):
                os.environ[ocr_key_env] = cfg["ocr_api_key"]

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
            source = arxiv_url.strip() or None
            display_name = source or (bib_uploaded.name if bib_uploaded is not None else "citation audit")

        llm = None
        if needs_llm:
            llm = LLMClient(
                provider_id=cfg["provider_id"],
                model=cfg["model"],
                api_key=cfg["api_key"],
                base_url=cfg["base_url"],
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
            bibliography_text=bibliography_text,
        )

        bar = st.progress(0.0)
        status = st.empty()

        def progress(p: float, msg: str) -> None:
            bar.progress(min(max(p, 0.0), 1.0))
            status.markdown(f"<div style='color:#7dd3fc;font-size:.85rem'>{C.esc(msg)}</div>",
                            unsafe_allow_html=True)

        try:
            if citation_only:
                report = run_citation_audit(source, llm, options,
                                            title_override=title_override, progress=progress)
            else:
                if llm is None:
                    st.error("Full review needs a model provider.")
                    return
                report = run_review(source, llm, options,
                                    title_override=title_override, progress=progress)
            st.session_state.report = report
            st.session_state.reviewed_name = display_name
            bar.empty()
            status.empty()
        except Exception as exc:
            bar.empty()
            st.error(f"Review failed: {_friendly_review_error(exc)}")
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
