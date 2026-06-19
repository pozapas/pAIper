"""Dark theme + CSS injection for pAIper."""

from __future__ import annotations

import streamlit as st

# Brand palette (dark)
PRIMARY = "#818cf8"     # indigo-400
PRIMARY_2 = "#a78bfa"   # violet-400
ACCENT = "#22d3ee"      # cyan-400

SEV_COLORS = {
    "CRITICAL": "#f87171",
    "MAJOR": "#fb923c",
    "MINOR": "#fbbf24",
    "PRAISE": "#34d399",
}
REC_COLORS = {
    "Accept": "#34d399",
    "Minor Revision": "#fbbf24",
    "Major Revision": "#fb923c",
    "Reject": "#f87171",
}
STATUS_COLORS = {
    "PASS": "#34d399", "FAIL": "#f87171", "UNCLEAR": "#fbbf24", "NA": "#64748b",
    "VERIFIED": "#34d399", "NOT_FOUND": "#f87171", "MISMATCH": "#fb923c",
    "UNPARSEABLE": "#64748b", "UNCHECKED": "#64748b",
}


def inject() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --bg:#0a0e1a; --bg2:#0f1525; --panel:#141b2e; --panel2:#1a2336;
  --border:#26304a; --border2:#323e5e; --text:#e7ecf5; --muted:#94a3b8; --faint:#64748b;
  --primary:#818cf8; --accent:#22d3ee;
}

html, body, [class*="css"], .stApp, .stMarkdown { font-family:'Inter',sans-serif; }
.stApp{ background:
   radial-gradient(900px 500px at 12% -8%, rgba(99,102,241,0.16), transparent 60%),
   radial-gradient(800px 500px at 100% 0%, rgba(34,211,238,0.10), transparent 55%),
   var(--bg); color:var(--text); }
.block-container{ padding-top:4rem; }

/* sidebar */
[data-testid="stSidebar"]{ background:linear-gradient(180deg,#0c1222,#0a0e1a); border-right:1px solid var(--border); }
[data-testid="stSidebar"] *{ color:var(--text); }
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small{ color:var(--muted)!important; }
.sb-head{ display:flex; align-items:center; gap:.5rem; color:#cbd5e1; font-size:.74rem;
  font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin:1.1rem 0 .5rem;
  padding-bottom:.35rem; border-bottom:1px solid var(--border); }
.sb-head svg{ color:var(--primary); }

/* inputs */
[data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] textarea{
  background:#0c1222!important; border:1px solid var(--border2)!important; color:var(--text)!important; }
.stTextInput input, .stNumberInput input{ background:#0c1222; color:var(--text); }

/* hero / brand */
.hero{ background:linear-gradient(120deg,#1b1145 0%, #1e1b4b 38%, #0e2a3a 100%);
  border:1px solid #2e2a66; border-radius:20px; padding:2rem 2.3rem; margin:.8rem 0 1.3rem;
  position:relative; overflow:hidden; box-shadow:0 18px 60px rgba(49,46,129,0.45);}
.hero::after{content:'';position:absolute;right:-80px;top:-80px;width:340px;height:340px;
  background:radial-gradient(circle,rgba(34,211,238,0.22),transparent 70%);}
.hero::before{content:'';position:absolute;left:-60px;bottom:-120px;width:300px;height:300px;
  background:radial-gradient(circle,rgba(129,140,248,0.22),transparent 70%);}
.brand{ display:flex; align-items:center; gap:.8rem; position:relative; z-index:1; }
.brand .mark{ width:48px;height:48px;border-radius:13px;display:grid;place-items:center;
  background:linear-gradient(135deg,#6366f1,#22d3ee); color:#0a0e1a; box-shadow:0 8px 24px rgba(34,211,238,.35);}
.brand .mark img{ width:100%; height:100%; object-fit:cover; border-radius:13px; }
.brand h1{ margin:0; font-size:2.2rem; font-weight:800; letter-spacing:-.03em; color:#fff; }
.brand h1 .ai{ background:linear-gradient(90deg,#a5b4fc,#22d3ee); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
.hero p{ position:relative; z-index:1; margin:.6rem 0 0; color:#c7d2e5; font-size:.98rem; max-width:760px; line-height:1.55;}
.hero .pills{ position:relative; z-index:1; margin-top:1rem; display:flex; gap:.5rem; flex-wrap:wrap; }
.hero .pill{ display:inline-flex; align-items:center; gap:.35rem; background:rgba(255,255,255,0.08);
  border:1px solid rgba(255,255,255,0.16); border-radius:999px; padding:.28rem .75rem; font-size:.73rem;
  font-weight:600; color:#e2e8f0; }
.hero .pill svg{ color:#7dd3fc; }

/* recommendation banner */
.rec-banner{ border-radius:18px; padding:1.3rem 1.6rem; margin-bottom:1rem; display:flex; align-items:center;
  gap:1.5rem; border:1px solid var(--border2); box-shadow:0 12px 40px rgba(0,0,0,.35); }
.rec-banner .rec-label{ font-size:.72rem; text-transform:uppercase; letter-spacing:.14em; opacity:.85; color:#0a0e1a; }
.rec-banner .rec-value{ font-size:1.8rem; font-weight:800; line-height:1.05; color:#0a0e1a; }
.rec-banner .rec-verdict{ font-size:.92rem; line-height:1.5; color:#0a0e1a; opacity:.92; }

/* stat chips */
.chips{ display:flex; gap:.7rem; flex-wrap:wrap; margin:.2rem 0 1rem; }
.chip{ background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:.65rem 1rem;
  min-width:96px; display:flex; flex-direction:column; gap:.2rem; }
.chip .top{ display:flex; align-items:center; gap:.35rem; }
.chip .v{ font-size:1.4rem; font-weight:800; line-height:1; }
.chip .l{ font-size:.66rem; color:var(--faint); text-transform:uppercase; letter-spacing:.06em; }

/* dimension bars */
.dim-row{ display:flex; align-items:center; gap:.7rem; margin:.45rem 0; }
.dim-row .ico{ color:var(--primary); display:flex; }
.dim-row .name{ flex:0 0 200px; font-size:.85rem; font-weight:600; color:#cbd5e1; }
.dim-track{ flex:1; height:11px; background:#0c1222; border:1px solid var(--border); border-radius:999px; overflow:hidden; }
.dim-fill{ height:100%; border-radius:999px; background:linear-gradient(90deg,#6366f1,#22d3ee); }
.dim-score{ flex:0 0 52px; text-align:right; font-weight:800; font-size:.85rem; color:#e7ecf5; }

/* finding card */
.fcard{ background:var(--panel); border:1px solid var(--border); border-left:4px solid #64748b;
  border-radius:14px; padding:1rem 1.2rem; margin-bottom:.8rem; transition:.15s; }
.fcard:hover{ border-color:var(--border2); box-shadow:0 8px 30px rgba(0,0,0,.3); }
.fcard .ftop{ display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; margin-bottom:.45rem; }
.fcard .ftitle{ font-weight:700; font-size:.95rem; color:#f1f5f9; }
.badge{ display:inline-flex; align-items:center; gap:.3rem; border-radius:999px; padding:.14rem .55rem;
  font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.tag{ display:inline-flex; align-items:center; gap:.25rem; border-radius:6px; padding:.1rem .45rem;
  font-size:.66rem; font-weight:600; background:#0c1222; color:#93a3bb; border:1px solid var(--border); }
.fcard .quote{ background:#0c1222; border-left:3px solid var(--border2); border-radius:0 8px 8px 0;
  padding:.5rem .8rem; font-family:'JetBrains Mono',monospace; font-size:.77rem; color:#a8b6cf;
  margin:.45rem 0; white-space:pre-wrap; word-break:break-word; }
.fcard .issue{ font-size:.88rem; color:#cdd7e6; line-height:1.6; }
.fcard .fix{ font-size:.85rem; color:#6ee7b7; background:rgba(16,185,129,.10); border:1px solid rgba(16,185,129,.25);
  border-radius:8px; padding:.45rem .7rem; margin-top:.5rem; display:flex; gap:.4rem; align-items:flex-start; }
.fcard .fix b{ color:#34d399; }

/* checklist / citation rows */
.crow{ display:flex; align-items:flex-start; gap:.7rem; background:var(--panel); border:1px solid var(--border);
  border-radius:11px; padding:.6rem .85rem; margin-bottom:.5rem; }
.crow .stat{ flex:0 0 96px; font-size:.66rem; font-weight:700; text-transform:uppercase; letter-spacing:.04em;
  text-align:center; border-radius:7px; padding:.28rem .2rem; display:flex; align-items:center; justify-content:center; gap:.3rem; }
.crow .ctext{ font-size:.85rem; color:#dbe3f0; line-height:1.5; }
.crow .cnote{ font-size:.76rem; color:var(--muted); margin-top:.22rem; }
.crow a{ color:#7dd3fc; }

/* section header */
.shead{ display:flex; align-items:center; gap:.5rem; font-size:.78rem; font-weight:700; color:#9fb0c9;
  text-transform:uppercase; letter-spacing:.1em; margin:1.3rem 0 .7rem; padding-bottom:.4rem;
  border-bottom:1px solid var(--border); }
.shead svg{ color:var(--primary); }

/* landing */
.land-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem; margin:.4rem 0 1.2rem; }
.fcell{ background:var(--panel); border:1px solid var(--border); border-radius:16px; padding:1.15rem 1.2rem; }
.fcell .ico{ width:40px;height:40px;border-radius:11px;display:grid;place-items:center; margin-bottom:.6rem;
  background:rgba(129,140,248,.14); color:#a5b4fc; }
.fcell h4{ margin:0 0 .3rem; font-size:.98rem; font-weight:700; color:#f1f5f9; }
.fcell p{ margin:0; font-size:.83rem; color:var(--muted); line-height:1.55; }
.steps{ display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; }
.step{ background:var(--panel2); border:1px solid var(--border); border-radius:14px; padding:1rem; }
.step .n{ width:26px;height:26px;border-radius:50%; background:linear-gradient(135deg,#6366f1,#22d3ee);
  color:#0a0e1a; font-weight:800; font-size:.8rem; display:grid; place-items:center; margin-bottom:.5rem; }
.step h5{ margin:0 0 .25rem; font-size:.86rem; color:#e7ecf5; font-weight:700;}
.step p{ margin:0; font-size:.78rem; color:var(--muted); line-height:1.5; }
.vbar{ display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.4rem; }
.vchip{ display:inline-flex; align-items:center; gap:.3rem; background:var(--panel); border:1px solid var(--border);
  border-radius:999px; padding:.25rem .7rem; font-size:.74rem; color:#cbd5e1; }
.vchip svg{ color:#7dd3fc; }

/* intro dialog */
[data-testid="stDialog"]{
  background:linear-gradient(145deg,#0b1020 0%, #101a2d 52%, #08151d 100%)!important;
  border:1px solid rgba(129,140,248,.32)!important;
  box-shadow:0 28px 100px rgba(0,0,0,.62), 0 0 80px rgba(34,211,238,.16)!important;
}
[data-testid="stDialog"] [data-testid="stMarkdownContainer"]{ color:var(--text); }
[data-testid="stDialog"] h2, [data-testid="stDialog"] p{ margin:0; }
.intro-wrap{ padding:.2rem 0 .3rem; }
.intro-hero{ display:grid; grid-template-columns:minmax(0,1.08fr) 260px; gap:1rem; align-items:stretch; }
.intro-copy{ background:linear-gradient(135deg,rgba(129,140,248,.16),rgba(34,211,238,.08));
  border:1px solid rgba(148,163,184,.18); border-radius:16px; padding:1.25rem; position:relative; overflow:hidden; }
.intro-copy::after{ content:''; position:absolute; right:-80px; top:-80px; width:180px; height:180px;
  background:radial-gradient(circle,rgba(34,211,238,.24),transparent 68%); }
.intro-kicker{ display:inline-flex; align-items:center; gap:.4rem; font-size:.72rem; font-weight:800;
  color:#a5f3fc; text-transform:uppercase; letter-spacing:.11em; margin-bottom:.6rem; position:relative; z-index:1; }
.intro-copy h2{ color:#f8fafc; font-size:1.55rem; line-height:1.1; font-weight:900; letter-spacing:0; margin-bottom:.6rem; position:relative; z-index:1; }
.intro-copy p{ color:#cbd5e1; font-size:.9rem; line-height:1.6; position:relative; z-index:1; }
.intro-art-shell{ border-radius:16px; overflow:hidden; min-height:230px; border:1px solid rgba(34,211,238,.26);
  background:#0c1222; box-shadow:inset 0 0 0 1px rgba(255,255,255,.03); }
.intro-art{ width:100%; height:100%; min-height:230px; display:block; object-fit:cover; }
.intro-art-fallback{ height:230px; display:grid; place-items:center; color:#22d3ee; }
.intro-panels{ display:grid; grid-template-columns:1fr 1fr; gap:.85rem; margin-top:.85rem; }
.intro-panel{ background:rgba(20,27,46,.92); border:1px solid var(--border); border-radius:14px; padding:.95rem; }
.intro-panel-title{ display:flex; align-items:center; gap:.45rem; color:#e2e8f0; font-size:.78rem;
  font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.65rem; }
.intro-panel-title svg{ color:#7dd3fc; }
.intro-steps{ display:grid; gap:.55rem; }
.intro-step{ display:grid; grid-template-columns:26px minmax(0,1fr); gap:.55rem; align-items:start; }
.intro-step .n{ width:24px;height:24px;border-radius:50%; background:linear-gradient(135deg,#818cf8,#22d3ee);
  color:#06121b; font-weight:900; font-size:.75rem; display:grid; place-items:center; }
.intro-step h5{ color:#f1f5f9; font-size:.82rem; font-weight:800; margin:0 0 .12rem; }
.intro-step p{ color:#aebbd0; font-size:.74rem; line-height:1.45; }
.intro-venues{ display:flex; flex-wrap:wrap; gap:.36rem; }
.intro-vchip{ display:inline-flex; align-items:center; gap:.28rem; background:#0c1222; border:1px solid rgba(148,163,184,.22);
  border-radius:999px; padding:.22rem .58rem; font-size:.68rem; color:#dbeafe; }
.intro-vchip svg{ color:#7dd3fc; }
.intro-note{ display:flex; gap:.45rem; align-items:flex-start; margin-top:.8rem; color:#9fb0c9;
  background:rgba(34,211,238,.07); border:1px solid rgba(34,211,238,.18); border-radius:11px; padding:.58rem .7rem;
  font-size:.74rem; line-height:1.45; }
.intro-note svg{ color:#7dd3fc; margin-top:1px; }

/* buttons */
.stButton>button{ background:linear-gradient(135deg,#4f46e5,#0891b2); color:#f8fafc!important; border:1px solid rgba(165,180,252,.45);
  font-weight:900; border-radius:11px; padding:.6rem 1.7rem; transition:.2s; text-shadow:0 1px 2px rgba(0,0,0,.45); }
.stButton>button p, .stButton>button span{ color:inherit!important; font-weight:900; letter-spacing:0; }
.stButton>button:not(:disabled), .stButton>button:not(:disabled) p, .stButton>button:not(:disabled) span{ color:#f8fafc!important; }
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled),
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled) *,
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled) [data-testid="stMarkdownContainer"] p{
  color:#f8fafc!important;
}
.stButton>button:hover{ box-shadow:0 8px 28px rgba(34,211,238,.4); transform:translateY(-1px); }
.stButton>button:disabled, .stButton>button:disabled:hover{ background:#182235!important; color:#cbd5e1!important;
  border:1px solid #35415f!important; box-shadow:none; transform:none; opacity:1; text-shadow:none; }
.stButton>button:disabled p, .stButton>button:disabled span{ color:#cbd5e1!important; }
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled,
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled *,
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled [data-testid="stMarkdownContainer"] p{
  color:#cbd5e1!important;
}
.stDownloadButton>button{ background:var(--panel); color:#a5b4fc; border:1px solid var(--border2);
  font-weight:600; border-radius:10px; }
.stDownloadButton>button:hover{ border-color:var(--primary); color:#fff; }

/* tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"]{ gap:.4rem; border-bottom:1px solid var(--border); }
[data-testid="stTabs"] [data-baseweb="tab"]{ color:var(--muted); font-weight:600; font-size:.85rem; }
[data-testid="stTabs"] [aria-selected="true"]{ color:#fff!important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{ background:var(--accent)!important; }

/* progress */
.stProgress > div > div > div{ background:linear-gradient(90deg,#6366f1,#22d3ee); }

/* misc */
hr{ border-color:var(--border); }
.privacy{ display:flex; gap:.5rem; align-items:flex-start; font-size:.74rem; color:var(--muted);
  background:rgba(34,211,238,.06); border:1px solid var(--border); border-radius:10px; padding:.55rem .7rem; }
.privacy svg{ color:#7dd3fc; margin-top:1px; }

@media (max-width: 780px){
  .block-container{ padding-top:3.4rem; }
  .hero{ padding:1.5rem; border-radius:16px; }
  .brand h1{ font-size:1.85rem; }
  .intro-hero, .intro-panels{ grid-template-columns:1fr; }
  .intro-art-shell, .intro-art{ min-height:180px; }
}

/* compact xAI-inspired redesign override */
:root{
  --bg:#0a0a0a; --bg2:#0a0a0a; --panel:#191919; --panel2:#1a1c20;
  --border:#212327; --border2:#363a3f; --text:#f5f5f5; --muted:#dadbdf; --faint:#7d8187;
  --primary:#f5f5f5; --accent:#ff7a17;
}
html, body, [class*="css"], .stApp, .stMarkdown{ font-family:'Inter',system-ui,-apple-system,sans-serif; }
.stApp{ background:var(--bg)!important; color:var(--text); }
.block-container{ max-width:980px; padding-top:4.7rem; padding-left:2rem; padding-right:2rem; }

[data-testid="stSidebar"]{ background:#0a0a0a!important; border-right:1px solid var(--border); }
[data-testid="stSidebar"] *{ color:var(--text); font-weight:400; }
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small{ color:var(--faint)!important; }
.sb-head{ color:var(--text); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem;
  font-weight:500; letter-spacing:.12em; margin:1rem 0 .5rem; padding-bottom:.45rem; border-bottom:1px solid var(--border); }
.sb-head svg{ color:var(--muted); }

[data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] textarea, .stTextInput input, .stNumberInput input{
  background:var(--panel2)!important; border:1px solid var(--border)!important; color:var(--text)!important; border-radius:8px!important;
}

.hero{ max-width:720px; background:var(--panel)!important; border:1px solid var(--border); border-radius:8px;
  padding:1rem 1.1rem; margin:1rem 0 1.15rem; box-shadow:none; }
.hero::before, .hero::after{ display:none; }
.brand{ gap:.65rem; }
.brand .mark{ width:34px; height:34px; border-radius:8px; background:var(--panel2); border:1px solid var(--border);
  color:var(--text); box-shadow:none; overflow:hidden; }
.brand .mark img{ border-radius:7px; }
.brand h1{ font-size:1.45rem; font-weight:500; letter-spacing:-.03em; color:var(--text); }
.brand h1 .ai{ background:none; -webkit-background-clip:initial; background-clip:initial; color:var(--accent); }
.hero p{ margin:.5rem 0 0; color:var(--muted); font-size:.84rem; max-width:600px; line-height:1.55; }
.hero .pills{ margin-top:.75rem; gap:.4rem; }
.hero .pill{ background:transparent; border:1px solid var(--border); border-radius:999px; padding:.2rem .58rem;
  font-size:.66rem; font-weight:400; color:var(--muted); }
.hero .pill svg{ color:var(--faint); }

.shead{ max-width:720px; color:var(--muted); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem;
  font-weight:500; letter-spacing:.12em; margin:1.1rem 0 .55rem; padding-bottom:.45rem; border-bottom:1px solid var(--border); }
.shead svg{ color:var(--muted); }

.mini-landing{ max-width:560px; background:var(--panel); border:1px solid var(--border); border-radius:8px;
  padding:1rem; margin:.35rem 0 1rem; }
.mini-eyebrow{ color:var(--faint); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem;
  letter-spacing:.12em; text-transform:uppercase; margin-bottom:.45rem; }
.mini-landing h3{ color:var(--text); font-size:1.15rem; font-weight:500; letter-spacing:-.02em; margin:0 0 .35rem; }
.mini-lede{ color:var(--muted); font-size:.82rem; line-height:1.55; margin:0 0 .65rem; }
.mini-rows{ border-top:1px solid var(--border); }
.mini-row{ display:grid; grid-template-columns:92px minmax(0,1fr); gap:.7rem; align-items:start;
  padding:.55rem 0; border-bottom:1px solid var(--border); }
.mini-row:last-child{ border-bottom:0; padding-bottom:0; }
.mini-row span{ color:var(--text); font-size:.8rem; font-weight:500; }
.mini-row p{ margin:0; color:var(--faint); font-size:.78rem; line-height:1.45; }

.fcell, .chip, .fcard, .crow, .step, .intro-panel, .privacy{
  background:var(--panel)!important; border:1px solid var(--border)!important; border-radius:8px!important; box-shadow:none!important;
}
.chip{ min-width:88px; padding:.55rem .75rem; }
.chip .v{ font-size:1.05rem; font-weight:500; }
.chip .l{ color:var(--faint); font-family:'JetBrains Mono',ui-monospace,monospace; letter-spacing:.08em; }
.fcard{ border-left-width:1px!important; padding:.85rem .95rem; }
.fcard:hover{ box-shadow:none; border-color:var(--border2); }
.fcard .ftitle{ color:var(--text); font-weight:500; }
.fcard .issue, .crow .ctext{ color:var(--muted); }
.fcard .quote{ background:#0f1011; border-left:1px solid var(--border2); border-radius:8px; color:#a6a8ad; }
.badge, .tag, .vchip{ border-radius:999px; background:transparent!important; border:1px solid var(--border)!important; font-weight:500; }
.dim-track{ background:#101112; border:1px solid var(--border); }
.dim-fill{ background:linear-gradient(90deg,#f5f5f5,#7d8187); }
.dim-row .name, .dim-score{ color:var(--muted); font-weight:500; }
.dim-row .ico{ color:var(--faint); }

[data-testid="stDialog"]{ background:rgba(10,10,10,.96)!important; border:1px solid var(--border)!important; box-shadow:none!important; }
.intro-wrap{ max-width:560px; margin:0 auto; padding:.15rem 0 .2rem; color:var(--text); }
.intro-head{ display:flex; align-items:center; gap:.75rem; margin-bottom:.8rem; }
.intro-mark{ width:42px; height:42px; border:1px solid var(--border); border-radius:8px; background:var(--panel); display:grid; place-items:center; overflow:hidden; }
.intro-mark-img{ width:100%; height:100%; object-fit:cover; }
.intro-kicker{ color:var(--faint); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem; letter-spacing:.12em; text-transform:uppercase; margin:0; }
.intro-wrap h2{ color:var(--text); font-size:1.32rem; line-height:1.18; font-weight:500; letter-spacing:-.03em; margin:.12rem 0 0; }
.intro-lede{ color:var(--muted); font-size:.86rem; line-height:1.55; margin:0 0 .85rem; }
.intro-block{ border-top:1px solid var(--border); padding:.75rem 0; }
.intro-panel-title{ color:var(--text); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem; font-weight:500; letter-spacing:.12em; margin:0 0 .55rem; }
.intro-steps, .intro-venues{ display:flex; flex-wrap:wrap; gap:.42rem; }
.intro-step, .intro-vchip{ display:inline-flex; align-items:center; gap:.35rem; border:1px solid var(--border); border-radius:999px;
  padding:.25rem .6rem; color:var(--muted); background:transparent; font-size:.76rem; }
.intro-step span{ color:var(--text); font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.68rem; }
.intro-note{ color:var(--faint); background:transparent; border-top:1px solid var(--border); border-radius:0; padding:.75rem 0 0; font-size:.76rem; }

.stButton>button, [data-testid="stButton"] [data-testid="stBaseButton-primary"]{
  border-radius:999px!important; box-shadow:none!important; text-shadow:none!important; transition:none!important;
  background:var(--text)!important; border:1px solid var(--text)!important; color:#0a0a0a!important; font-weight:500!important;
  padding:.45rem 1rem!important;
}
.stButton>button:hover{ transform:none; box-shadow:none!important; }
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled) *,
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled) [data-testid="stMarkdownContainer"] p{
  color:#0a0a0a!important; font-weight:500!important;
}
.stButton>button:disabled, .stButton>button:disabled:hover,
[data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled{
  background:transparent!important; border:1px solid var(--border)!important; color:var(--faint)!important; opacity:1!important;
}
.stButton>button:disabled *, [data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled *{ color:var(--faint)!important; }
.stDownloadButton>button{ background:transparent!important; color:var(--text)!important; border:1px solid var(--border)!important;
  border-radius:999px!important; font-weight:400!important; box-shadow:none!important; }

[data-testid="stTabs"] [data-baseweb="tab-list"]{ border-bottom:1px solid var(--border); }
[data-testid="stTabs"] [data-baseweb="tab"]{ color:var(--faint); font-weight:400; }
[data-testid="stTabs"] [aria-selected="true"]{ color:var(--text)!important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{ background:var(--text)!important; }
.stProgress > div > div > div{ background:var(--text)!important; }

[data-testid="stHeader"], [data-testid="stToolbar"]{ background:var(--bg)!important; color:var(--text)!important; }
[data-testid="stFileUploaderDropzone"]{
  background:var(--panel)!important; border:1px solid var(--border)!important; border-radius:8px!important;
  color:var(--text)!important; box-shadow:none!important;
}
[data-testid="stFileUploaderDropzone"] *{ color:var(--muted)!important; }
[data-testid="stFileUploaderDropzone"] svg{ color:var(--faint)!important; }
[data-testid="stFileUploaderDropzone"] button, [data-testid="stBaseButton-secondary"]{
  background:transparent!important; color:var(--text)!important; border:1px solid var(--border)!important;
  border-radius:999px!important; box-shadow:none!important; font-weight:400!important;
}
.intro-wrap + [data-testid="stButton"]{ margin:.75rem auto 0!important; }

@media (max-width: 780px){
  .block-container{ padding-top:4rem; padding-left:1rem; padding-right:1rem; }
  .hero{ padding:.9rem; border-radius:8px; max-width:100%; }
  .brand h1{ font-size:1.35rem; }
  .hero .pills{ display:none; }
  .mini-row{ grid-template-columns:1fr; gap:.15rem; }
}

/* restore the previous full UI, only recolored to the attached palette */
:root{
  --bg:#0d1117; --bg2:#111720; --panel:#171c25; --panel2:#202731;
  --border:#2a3038; --border2:#424952; --text:#f5f5f5; --muted:#9aa1a9; --faint:#6f767f;
  --primary:#f5f5f5; --accent:#9aa1a9;
}
html, body, [class*="css"], .stApp, .stMarkdown{ font-family:'Inter',sans-serif!important; }
.stApp{ background:
   radial-gradient(900px 500px at 12% -8%, rgba(245,245,245,0.055), transparent 60%),
   radial-gradient(800px 500px at 100% 0%, rgba(111,118,127,0.12), transparent 55%),
   var(--bg)!important; color:var(--text); }
.block-container{ max-width:none!important; width:100%!important; padding-top:4rem!important; padding-left:5rem; padding-right:5rem; }

[data-testid="stSidebar"]{ background:linear-gradient(180deg,#111720,#0d1117)!important; border-right:1px solid var(--border)!important; }
[data-testid="stSidebar"] *{ color:var(--text); font-weight:500; }
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small{ color:var(--muted)!important; }
.sb-head{ color:#d9dde2!important; font-family:'Inter',sans-serif!important; font-size:.74rem!important; font-weight:800!important;
  letter-spacing:.12em; margin:1.1rem 0 .5rem!important; padding-bottom:.35rem!important; border-bottom:1px solid var(--border)!important; }
.sb-head svg{ color:var(--muted)!important; }

[data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] textarea, .stTextInput input, .stNumberInput input{
  background:#111720!important; border:1px solid var(--border2)!important; color:var(--text)!important; border-radius:10px!important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"]>div{
  background:#111720!important; border:1px solid var(--border2)!important; color:var(--text)!important; border-radius:10px!important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"]>div:focus-within{
  border-color:rgba(255,159,67,.72)!important; box-shadow:0 0 0 1px rgba(255,159,67,.28)!important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"]{
  background:linear-gradient(180deg,#ffb15c,#ff9f43)!important; border:1px solid rgba(255,189,122,.9)!important;
  border-radius:8px!important; box-shadow:0 6px 18px rgba(255,159,67,.16)!important; color:#0d1117!important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span,
[data-testid="stMultiSelect"] [data-baseweb="tag"] p{
  color:#0d1117!important; font-weight:900!important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] svg{
  color:#0d1117!important; fill:#0d1117!important; opacity:.82!important;
}

.hero{ max-width:none!important; background:linear-gradient(120deg,#161b24 0%, #1f2630 46%, #111720 100%)!important;
  border:1px solid var(--border2)!important; border-radius:20px!important; padding:2rem 2.3rem!important; margin:.8rem 0 1.3rem!important;
  position:relative; overflow:hidden; box-shadow:0 18px 60px rgba(0,0,0,.38)!important; }
.hero::after{ display:block!important; content:''; position:absolute; right:-80px; top:-80px; width:340px; height:340px;
  background:radial-gradient(circle,rgba(245,245,245,0.12),transparent 70%)!important; }
.hero::before{ display:block!important; content:''; position:absolute; left:-60px; bottom:-120px; width:300px; height:300px;
  background:radial-gradient(circle,rgba(154,161,169,0.15),transparent 70%)!important; }
.brand{ display:flex; align-items:center; gap:.8rem!important; position:relative; z-index:1; }
.brand .mark{ width:48px!important; height:48px!important; border-radius:13px!important; display:grid; place-items:center;
  background:linear-gradient(135deg,#2f3540,#f5f5f5)!important; border:1px solid rgba(245,245,245,.16)!important; box-shadow:0 8px 24px rgba(0,0,0,.32)!important; }
.brand .mark img{ width:100%; height:100%; object-fit:cover; border-radius:13px!important; }
.brand h1{ margin:0; font-size:2.2rem!important; font-weight:800!important; letter-spacing:-.03em; color:#fff!important; }
.brand h1 .ai{ background:none!important; -webkit-background-clip:initial!important; background-clip:initial!important; color:#ff9f43!important; text-shadow:0 0 18px rgba(255,159,67,.42); }
.hero p{ position:relative; z-index:1; margin:.6rem 0 0!important; color:#d8dce1!important; font-size:.98rem!important; max-width:760px!important; line-height:1.55!important; }
.hero .pills{ position:relative; z-index:1; margin-top:1rem!important; display:flex!important; gap:.5rem!important; flex-wrap:wrap; }
.hero .pill{ display:inline-flex; align-items:center; gap:.35rem; background:rgba(245,245,245,0.06)!important;
  border:1px solid rgba(245,245,245,0.14)!important; border-radius:999px!important; padding:.28rem .75rem!important;
  font-size:.73rem!important; font-weight:700!important; color:#eef0f2!important; }
.hero .pill svg{ color:#c9ced4!important; }

.shead{ display:flex; align-items:center; gap:.5rem; max-width:none!important; font-family:'Inter',sans-serif!important;
  font-size:.78rem!important; font-weight:800!important; color:#c5cad0!important; text-transform:uppercase; letter-spacing:.1em;
  margin:1.3rem 0 .7rem!important; padding-bottom:.4rem!important; border-bottom:1px solid var(--border)!important; }
.shead svg{ color:#d9dde2!important; }

.land-grid{ display:grid!important; grid-template-columns:repeat(3,1fr)!important; gap:.9rem!important; margin:.4rem 0 1.2rem!important; }
.fcell{ background:var(--panel)!important; border:1px solid var(--border)!important; border-radius:16px!important; padding:1.15rem 1.2rem!important; box-shadow:none!important; }
.fcell .ico{ width:40px!important; height:40px!important; border-radius:11px!important; display:grid!important; place-items:center!important; margin-bottom:.6rem!important;
  background:rgba(245,245,245,.08)!important; color:#f5f5f5!important; }
.fcell h4{ margin:0 0 .3rem!important; font-size:.98rem!important; font-weight:800!important; color:#f5f5f5!important; }
.fcell p{ margin:0!important; font-size:.83rem!important; color:var(--muted)!important; line-height:1.55!important; }

.chip, .fcard, .crow, .step, .privacy{ background:var(--panel)!important; border:1px solid var(--border)!important; border-radius:14px!important; box-shadow:none!important; }
.chip{ min-width:96px!important; padding:.65rem 1rem!important; }
.chip .v{ font-size:1.4rem!important; font-weight:800!important; }
.chip .l{ color:var(--faint)!important; font-family:'Inter',sans-serif!important; }
.fcard{ border-left-width:4px!important; padding:1rem 1.2rem!important; }
.fcard:hover{ border-color:var(--border2)!important; box-shadow:0 8px 30px rgba(0,0,0,.26)!important; }
.fcard .ftitle{ color:#f5f5f5!important; font-weight:800!important; }
.fcard .issue, .crow .ctext{ color:#d7dbe0!important; }
.fcard .quote{ background:#111720!important; border-left:3px solid var(--border2)!important; border-radius:0 8px 8px 0!important; color:#aeb5bd!important; }
.badge, .tag, .vchip{ border-radius:999px!important; background:rgba(245,245,245,.06)!important; border:1px solid var(--border)!important; }
.dim-track{ background:#111720!important; border:1px solid var(--border)!important; }
.dim-fill{ background:linear-gradient(90deg,#f5f5f5,#9aa1a9)!important; }
.dim-row .name, .dim-score{ color:#d7dbe0!important; font-weight:700!important; }
.dim-row .ico{ color:#d9dde2!important; }

[data-testid="stFileUploaderDropzone"]{
  background:var(--panel)!important; border:1px solid var(--border)!important; border-radius:11px!important; color:var(--text)!important; box-shadow:none!important;
}
[data-testid="stFileUploaderDropzone"] *{ color:#d7dbe0!important; }
[data-testid="stFileUploaderDropzone"] svg{ color:#f5f5f5!important; }
[data-testid="stFileUploaderDropzone"] button, [data-testid="stBaseButton-secondary"]{
  background:rgba(245,245,245,.05)!important; color:#f5f5f5!important; border:1px solid var(--border2)!important;
  border-radius:10px!important; box-shadow:none!important; font-weight:700!important;
}

.stButton>button, [data-testid="stButton"] [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#f5f5f5,#9aa1a9)!important; color:#0d1117!important; border:1px solid rgba(245,245,245,.55)!important;
  font-weight:900!important; border-radius:11px!important; padding:.6rem 1.7rem!important; transition:.2s!important; text-shadow:none!important; box-shadow:none!important;
}
.stButton>button:hover{ box-shadow:0 8px 28px rgba(245,245,245,.16)!important; transform:translateY(-1px)!important; }
.stButton>button:not(:disabled) *, [data-testid="stButton"] [data-testid="stBaseButton-primary"]:not(:disabled) *{ color:#0d1117!important; font-weight:900!important; }
.stButton>button:disabled, .stButton>button:disabled:hover, [data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled{
  background:#202731!important; color:#d7dbe0!important; border:1px solid #424952!important; box-shadow:none!important; transform:none!important; opacity:1!important;
}
.stButton>button:disabled *, [data-testid="stButton"] [data-testid="stBaseButton-primary"]:disabled *{ color:#d7dbe0!important; }
.stDownloadButton>button{ background:var(--panel)!important; color:#f5f5f5!important; border:1px solid var(--border2)!important; border-radius:10px!important; font-weight:700!important; }

[data-testid="stTabs"] [data-baseweb="tab-list"]{
  gap:.72rem!important; align-items:center!important; padding:.18rem .1rem .7rem!important; margin-bottom:.9rem!important;
  border-bottom:0!important; overflow-x:auto!important; scrollbar-width:thin!important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"]{ display:none!important; }
[data-testid="stTabs"] [data-baseweb="tab-list"]::before,
[data-testid="stTabs"] [data-baseweb="tab-list"]::after{ content:none!important; display:none!important; }
[data-testid="stTabs"] [data-baseweb="tab"]{
  min-height:34px!important; height:auto!important; padding:.42rem .82rem!important; border:1px solid rgba(154,161,169,.26)!important;
  border-radius:999px!important; background:rgba(245,245,245,.035)!important; color:#aeb5bd!important;
  font-weight:800!important; font-size:.82rem!important; line-height:1!important; letter-spacing:0!important;
  transition:background .16s ease,border-color .16s ease,color .16s ease,box-shadow .16s ease,transform .16s ease!important;
}
[data-testid="stTabs"] [data-baseweb="tab"] p{ color:inherit!important; font-weight:inherit!important; line-height:1!important; margin:0!important; white-space:nowrap!important; }
[data-testid="stTabs"] [data-baseweb="tab"]:hover{
  color:#f5f5f5!important; border-color:rgba(255,159,67,.54)!important; background:rgba(255,159,67,.08)!important;
  transform:translateY(-1px)!important;
}
[data-testid="stTabs"] [aria-selected="true"]{
  color:#f5f5f5!important; border-color:rgba(255,159,67,.72)!important;
  background:linear-gradient(180deg,rgba(255,159,67,.18),rgba(255,159,67,.075))!important;
  box-shadow:inset 0 0 0 1px rgba(255,159,67,.18),0 8px 22px rgba(255,159,67,.12)!important;
}
[data-testid="stTabs"] [aria-selected="true"] p{ color:#f5f5f5!important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{ background:#ff9f43!important; height:2px!important; border-radius:999px!important; }
.stProgress > div > div > div{ background:linear-gradient(90deg,#f5f5f5,#9aa1a9)!important; }
[data-testid="stHeader"], [data-testid="stToolbar"]{ background:transparent!important; color:var(--text)!important; }

/* compact intro popup, borrowing the causal explorer lab card language */
.brand h1 .ai{ color:#ff9f43!important; text-shadow:0 0 18px rgba(255,159,67,.42)!important; }
[data-testid="stDialog"]{ background:rgba(8,10,11,.94)!important; border:1px solid rgba(245,245,245,.14)!important;
  box-shadow:0 28px 80px rgba(0,0,0,.62)!important; backdrop-filter:blur(14px)!important; }
[data-testid="stDialog"] [data-testid="stVerticalBlock"]{ gap:.65rem!important; }
.intro-wrap{ max-width:430px!important; margin:0 auto!important; padding:0!important; color:#f5f5f5!important;
  background:#101315!important; border:1px solid rgba(245,245,245,.12)!important; border-radius:12px!important;
  overflow:hidden!important; box-shadow:0 18px 56px rgba(0,0,0,.34)!important; }
.intro-lab-visual{ position:relative!important; min-height:132px!important; overflow:hidden!important; border-bottom:1px solid rgba(245,245,245,.12)!important;
  background:
    linear-gradient(rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(145deg,#0b0f11,#171c20)!important;
  background-size:26px 26px,26px 26px,auto!important; }
.intro-lab-visual::before{ content:''; position:absolute; inset:14px; border:1px solid rgba(245,245,245,.08); border-radius:10px; }
.intro-route-line{ position:absolute; left:52px; right:52px; top:22px; height:72px; border:1px solid rgba(255,159,67,.54);
  border-left-color:transparent; border-bottom-color:transparent; border-radius:50%; transform:rotate(-8deg); }
.intro-route-line::before,.intro-route-line::after{ content:''; position:absolute; width:7px; height:7px; border-radius:999px; background:#ff9f43;
  box-shadow:0 0 18px rgba(255,159,67,.7); }
.intro-route-line::before{ left:18%; top:4px; }
.intro-route-line::after{ right:14%; top:18px; }
.intro-mark{ position:absolute!important; left:50%!important; top:50%!important; transform:translate(-50%,-50%)!important; z-index:2!important;
  width:50px!important; height:50px!important; border:1px solid rgba(245,245,245,.18)!important; border-radius:13px!important;
  background:#171c25!important; display:grid!important; place-items:center!important; overflow:hidden!important; box-shadow:0 14px 36px rgba(0,0,0,.42)!important; }
.intro-mark-img{ width:100%!important; height:100%!important; object-fit:cover!important; }
.intro-signal{ position:absolute!important; z-index:3!important; min-width:62px!important; padding:.34rem .44rem!important; border-radius:8px!important;
  background:rgba(16,19,21,.88)!important; border:1px solid rgba(245,245,245,.14)!important; box-shadow:0 12px 30px rgba(0,0,0,.28)!important; }
.intro-signal strong{ display:block!important; color:#ff9f43!important; font-size:.9rem!important; line-height:1!important; font-weight:900!important; }
.intro-signal span{ display:block!important; margin-top:.12rem!important; color:#a7aea8!important; font-size:.55rem!important; font-weight:800!important; letter-spacing:.08em!important; text-transform:uppercase!important; }
.signal-a{ left:18px!important; top:20px!important; }
.signal-b{ right:18px!important; top:32px!important; }
.signal-c{ left:50%!important; bottom:12px!important; transform:translateX(-50%)!important; }
.intro-copy-mini{ padding:.86rem .95rem .92rem!important; }
.intro-kicker{ display:block!important; color:#a7aea8!important; font-size:.66rem!important; font-weight:900!important; letter-spacing:.14em!important; text-transform:uppercase!important; margin:0 0 .28rem!important; }
.intro-wrap h2{ color:#f5f5f5!important; font-size:1.05rem!important; line-height:1.16!important; font-weight:900!important; letter-spacing:-.02em!important; margin:0!important; }
.intro-lede{ color:#d7dbe0!important; font-size:.74rem!important; line-height:1.42!important; margin:.4rem 0 .56rem!important; }
.intro-note{ display:flex!important; align-items:center!important; gap:.42rem!important; color:#f4d5b0!important; background:rgba(255,159,67,.1)!important;
  border:1px solid rgba(255,159,67,.24)!important; border-radius:9px!important; padding:.38rem .5rem!important; font-size:.64rem!important; margin:0!important; }
.intro-note svg{ color:#ff9f43!important; flex:0 0 auto!important; }
.intro-dataset-cards{ display:grid!important; grid-template-columns:repeat(4,minmax(0,1fr))!important; gap:.35rem!important; margin-top:.56rem!important; }
.intro-dataset-card{ background:#171c25!important; border:1px solid rgba(245,245,245,.1)!important; border-radius:8px!important; padding:.42rem .45rem!important; }
.intro-dataset-card h3{ margin:0 0 .12rem!important; color:#f5f5f5!important; font-size:.66rem!important; font-weight:900!important; letter-spacing:0!important; }
.intro-dataset-card p{ margin:0!important; color:#a7aea8!important; font-size:.58rem!important; line-height:1.25!important; }
.intro-venue-row{ display:flex!important; align-items:flex-start!important; gap:.52rem!important; margin-top:.56rem!important; padding-top:.5rem!important; border-top:1px solid rgba(245,245,245,.1)!important; }
.intro-venue-row>span{ flex:0 0 auto!important; padding-top:.22rem!important; color:#a7aea8!important; font-size:.58rem!important; font-weight:900!important; letter-spacing:.14em!important; text-transform:uppercase!important; }
.intro-venue-row>div{ display:flex!important; flex-wrap:wrap!important; gap:.34rem!important; }
.intro-vchip{ display:inline-flex!important; align-items:center!important; border:1px solid rgba(245,245,245,.12)!important;
  border-radius:999px!important; padding:.22rem .48rem!important; color:#d7dbe0!important; background:rgba(245,245,245,.045)!important; font-size:.64rem!important; font-weight:800!important; }
[data-testid="stDialog"] .stButton>button, [data-testid="stDialog"] [data-testid="stBaseButton-primary"]{
  background:#ff9f43!important; border-color:#ffb261!important; color:#0d1117!important; border-radius:10px!important; box-shadow:0 10px 26px rgba(255,159,67,.18)!important; }
[data-testid="stDialog"] .stButton>button *, [data-testid="stDialog"] [data-testid="stBaseButton-primary"] *{ color:#0d1117!important; }

@media (max-width: 780px){
  .intro-wrap{ max-width:360px!important; }
  .intro-lab-visual{ min-height:126px!important; }
  .intro-signal{ min-width:66px!important; padding:.36rem .46rem!important; }
  .intro-dataset-cards{ grid-template-columns:repeat(2,minmax(0,1fr))!important; }
}

/* product-style intro popup with attached bucket artwork adapted for Streamlit */
[data-testid="stDialog"]{ background:rgba(8,10,11,.94)!important; border:1px solid rgba(245,245,245,.14)!important;
  box-shadow:0 30px 92px rgba(0,0,0,.66)!important; backdrop-filter:blur(16px)!important; }
.intro-wrap{ width:min(700px,calc(100vw - 64px))!important; max-width:700px!important; display:grid!important;
  grid-template-columns:minmax(275px,.86fr) minmax(0,1.14fr)!important; gap:0!important; padding:0!important;
  background:#101315!important; border:1px solid rgba(245,245,245,.13)!important; border-radius:14px!important;
  overflow:hidden!important; box-shadow:0 22px 64px rgba(0,0,0,.4)!important; }
.intro-bucket-art{ position:relative!important; min-height:330px!important; padding:.9rem!important; overflow:hidden!important;
  border-right:1px solid rgba(245,245,245,.11)!important; background:
    radial-gradient(circle at 50% 18%, rgba(255,159,67,.22), transparent 38%),
    linear-gradient(rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(155deg,#080a0b 0%,#11171a 58%,#191d22 100%)!important;
  background-size:auto,26px 26px,26px 26px,auto!important; }
.bucket-glow{ position:absolute; inset:12% 8% auto; height:150px; border-radius:999px; background:rgba(255,159,67,.12);
  filter:blur(22px); }
.bucket-svg{ position:absolute; left:50%; top:54%; width:106%; max-width:340px; transform:translate(-50%,-50%); filter:drop-shadow(0 18px 34px rgba(0,0,0,.45)); }
.bucket-wing{ fill:rgba(245,245,245,.24); stroke:rgba(245,245,245,.25); stroke-width:1; }
.bucket-lid{ fill:rgba(245,245,245,.18); stroke:rgba(245,245,245,.26); stroke-width:1; }
.bucket-body{ fill:rgba(255,255,255,.16); stroke:rgba(245,245,245,.26); stroke-width:1; }
.bucket-front{ fill:#171c25; stroke:rgba(245,245,245,.12); stroke-width:1.5; }
.bucket-core{ display:none!important; }
.bucket-chip{ position:absolute; z-index:4; display:flex; align-items:center; gap:.42rem; min-width:150px; padding:.42rem .5rem; border-radius:999px;
  color:#f5f5f5; background:rgba(16,19,21,.9); border:1px solid rgba(245,245,245,.14); box-shadow:0 12px 34px rgba(0,0,0,.32);
  backdrop-filter:blur(12px); animation:bucketFloat 4.2s ease-in-out infinite; }
.bucket-chip span{ display:grid; place-items:center; flex:0 0 auto; width:28px; height:28px; border-radius:999px; color:#ff9f43; background:rgba(255,159,67,.12); }
.bucket-chip strong{ display:block; color:#f5f5f5; font-size:.68rem; font-weight:900; line-height:1.1; }
.bucket-chip small{ display:block; margin-top:.05rem; color:#a7aea8; font-size:.56rem; line-height:1.1; }
.bucket-chip-main{ left:26px; top:84px; }
.bucket-chip-alt{ right:22px; top:112px; animation-delay:-1.5s; }
.bucket-metrics{ position:absolute; left:50%; bottom:120px; transform:translateX(-50%); z-index:5; display:flex; gap:.32rem; width:min(226px,80%); }
.bucket-metrics span{ flex:1; display:grid; place-items:center; min-height:28px; border-radius:999px; color:#f4d5b0; background:rgba(255,159,67,.085);
  border:1px solid rgba(255,159,67,.18); font-size:.56rem; font-weight:900; letter-spacing:.04em; text-transform:uppercase; white-space:nowrap; }
.intro-copy-mini{ padding:.88rem .95rem .8rem!important; display:flex!important; flex-direction:column!important; justify-content:flex-start!important; }
.intro-kicker{ color:#ffbd7a!important; font-size:.64rem!important; font-weight:900!important; letter-spacing:.12em!important; text-transform:uppercase!important; margin:0 0 .34rem!important; }
.intro-wrap h2{ color:#f5f5f5!important; font-size:1.16rem!important; line-height:1.12!important; font-weight:900!important; letter-spacing:0!important; margin:0!important; }
.intro-lede{ color:#d7dbe0!important; font-size:.72rem!important; line-height:1.36!important; margin:.4rem 0 .48rem!important; }
.intro-note{ display:flex!important; align-items:flex-start!important; gap:.42rem!important; color:#f4d5b0!important; background:rgba(255,159,67,.1)!important;
  border:1px solid rgba(255,159,67,.24)!important; border-radius:10px!important; padding:.36rem .46rem!important; font-size:.62rem!important; line-height:1.25!important; margin:0!important; }
.intro-note svg{ color:#ff9f43!important; flex:0 0 auto!important; margin-top:.05rem!important; }
.intro-flow{ display:grid!important; grid-template-columns:repeat(2,minmax(0,1fr))!important; gap:.42rem!important; margin-top:.58rem!important; }
.intro-flow-card{ display:grid!important; grid-template-columns:24px minmax(0,1fr)!important; column-gap:.38rem!important; align-items:start!important;
  background:#171c25!important; border:1px solid rgba(245,245,245,.1)!important; border-radius:9px!important; padding:.4rem!important; }
.intro-flow-card span{ color:#ff9f43!important; font-size:.54rem!important; font-weight:900!important; letter-spacing:.12em!important; }
.intro-flow-card h3{ color:#f5f5f5!important; margin:0 0 .1rem!important; font-size:.66rem!important; font-weight:900!important; letter-spacing:0!important; }
.intro-flow-card p{ color:#a7aea8!important; grid-column:2!important; margin:0!important; font-size:.55rem!important; line-height:1.22!important; }
.intro-venue-row{ display:grid!important; gap:.3rem!important; margin-top:.46rem!important; padding-top:.42rem!important; border-top:1px solid rgba(245,245,245,.1)!important; }
.intro-venue-row>span{ color:#a7aea8!important; font-size:.58rem!important; font-weight:900!important; letter-spacing:.13em!important; text-transform:uppercase!important; padding:0!important; }
.intro-venue-row>div{ display:flex!important; flex-wrap:wrap!important; gap:.36rem!important; }
.intro-vchip{ display:inline-flex!important; align-items:center!important; border:1px solid rgba(245,245,245,.12)!important;
  border-radius:999px!important; padding:.2rem .45rem!important; color:#d7dbe0!important; background:rgba(245,245,245,.045)!important; font-size:.59rem!important; font-weight:800!important; }
[data-testid="stDialog"] .stButton>button, [data-testid="stDialog"] [data-testid="stBaseButton-primary"]{
  background:#ff9f43!important; border-color:#ffb261!important; color:#0d1117!important; border-radius:11px!important;
  box-shadow:0 10px 28px rgba(255,159,67,.18)!important; min-height:34px!important; width:132px!important; min-width:132px!important;
  padding:.36rem .72rem!important; font-size:.78rem!important; }
[data-testid="stDialog"] [data-testid="stButton"]{ display:flex!important; justify-content:flex-end!important; }
[data-testid="stDialog"] .stButton>button *, [data-testid="stDialog"] [data-testid="stBaseButton-primary"] *{ color:#0d1117!important; }
@keyframes bucketFloat{
  0%,100%{ transform:translateY(0); }
  50%{ transform:translateY(-8px); }
}
@media (max-width: 820px){
  .intro-wrap{ width:min(340px,calc(100vw - 64px))!important; grid-template-columns:1fr!important; }
  .intro-bucket-art{ min-height:230px!important; border-right:0!important; border-bottom:1px solid rgba(245,245,245,.11)!important; }
  .bucket-svg{ width:82%!important; top:45%!important; }
  .bucket-chip-alt{ right:14px!important; bottom:76px!important; }
  .bucket-metrics{ grid-template-columns:repeat(3,1fr)!important; }
  .intro-copy-mini{ padding:1rem!important; }
  .intro-wrap h2{ font-size:1.14rem!important; }
  .intro-flow{ grid-template-columns:repeat(2,minmax(0,1fr))!important; }
  .intro-flow-card{ padding:.52rem!important; }
}

/* attached GLSL-hills-inspired side graphic */
div[role="dialog"] > div:first-child{ display:none!important; }
div[role="dialog"] > button[aria-label="Close"]{ display:none!important; }
.intro-dialog-brand{ display:none!important; }
.hills-brand{ position:absolute; right:1rem; bottom:.9rem; z-index:4; display:flex!important; align-items:baseline!important; justify-content:flex-end!important; gap:.05rem!important;
  color:#f5f5f5!important; font-size:.9rem!important; line-height:1.08!important; font-weight:900!important; letter-spacing:-.01em!important; text-align:right!important;
  text-shadow:0 8px 22px rgba(0,0,0,.7)!important; }
.hills-brand span{ color:#ff9f43!important; text-shadow:0 0 18px rgba(255,159,67,.45)!important; }
.hills-credit{ position:absolute; left:1rem; bottom:.8rem; z-index:5; display:grid!important; gap:.16rem!important; max-width:8.8rem!important;
  color:#9aa1a9!important; font-size:.55rem!important; line-height:1.22!important; font-weight:800!important; letter-spacing:.01em!important; }
.hills-credit a{ color:#f4d5b0!important; text-decoration:none!important; }
.hills-credit a:hover{ color:#ff9f43!important; text-decoration:underline!important; text-underline-offset:2px!important; }
.github-link{ display:inline-flex!important; align-items:center!important; gap:.25rem!important; width:max-content!important; max-width:100%!important;
  color:#d7dbe0!important; overflow:hidden!important; white-space:nowrap!important; }
.github-link svg{ width:12px!important; height:12px!important; flex:0 0 12px!important; fill:currentColor!important; opacity:.92!important; }
.github-link span{ overflow:hidden!important; text-overflow:ellipsis!important; }
.intro-hills-art{ position:relative!important; min-height:370px!important; overflow:hidden!important; border-right:1px solid rgba(245,245,245,.11)!important;
  background:
    radial-gradient(circle at 52% 38%, rgba(255,159,67,.2), transparent 33%),
    linear-gradient(rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(245,245,245,.045) 1px, transparent 1px),
    linear-gradient(160deg,#080a0b 0%,#101315 54%,#171c25 100%)!important;
  background-size:auto,28px 28px,28px 28px,auto!important; }
.hills-glow{ position:absolute; left:9%; right:9%; bottom:16%; height:42%; border-radius:50%; background:rgba(255,159,67,.15); filter:blur(26px); }
.hills-svg{ position:absolute; inset:-18% -18% -10% -18%; width:136%; height:126%; transform:perspective(440px) rotateX(58deg) translateY(-8px) scale(1.28);
  transform-origin:center 70%; overflow:visible; }
.hills-grid{ animation:hillsDrift 5.8s ease-in-out infinite alternate; }
.hill-line{ fill:none; stroke:url(#hillStroke); stroke-width:.78; vector-effect:non-scaling-stroke; opacity:.68; }
.hill-line-1{ opacity:.55; }
.hill-line-2{ opacity:.45; }
.hill-line-3{ opacity:.34; }
.hills-horizon{ fill:none; stroke:#ff9f43; stroke-width:1; opacity:.7; filter:drop-shadow(0 0 14px rgba(255,159,67,.45)); }
.hills-caption{ display:none!important; }
.hills-caption span{ display:inline-flex; min-height:28px; align-items:center; border:1px solid rgba(255,159,67,.2); border-radius:999px;
  padding:0 .68rem; color:#f4d5b0; background:rgba(255,159,67,.08); font-size:.62rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
.hills-float-title{ position:absolute; z-index:3; left:1.05rem; right:1.05rem; top:5.4rem; display:grid; justify-items:center; text-align:center;
  pointer-events:none; animation:headlineFloat 5.2s ease-in-out infinite; }
.hills-float-title span{ color:rgba(245,245,245,.88); font-family:Georgia,'Times New Roman',serif; font-size:1.48rem; font-style:italic; font-weight:300;
  line-height:1; letter-spacing:.01em; text-shadow:0 8px 28px rgba(0,0,0,.62); }
.hills-float-title strong{ color:#f5f5f5; font-size:2.06rem; line-height:.98; font-weight:900; letter-spacing:-.04em;
  text-shadow:0 10px 34px rgba(0,0,0,.68),0 0 24px rgba(255,159,67,.14); }
.hills-float-title em{ margin-top:.18rem; color:#ffbd7a; font-size:.68rem; font-style:normal; font-weight:900; letter-spacing:.16em;
  text-transform:uppercase; text-shadow:0 6px 18px rgba(0,0,0,.55); }
.intro-flow-card{ grid-template-columns:40px minmax(0,1fr)!important; align-content:center!important; min-height:98px!important; padding:.82rem .86rem!important; }
.intro-flow-card span{ font-size:.9rem!important; line-height:1.1!important; align-self:start!important; padding-top:.08rem!important; }
.intro-flow-card h3{ font-size:1.04rem!important; line-height:1.16!important; margin:0 0 .34rem!important; align-self:end!important; }
.intro-flow-card p{ font-size:.82rem!important; line-height:1.38!important; align-self:start!important; }
.intro-lede{ font-size:.88rem!important; line-height:1.48!important; }
[data-testid="stDialog"] [data-testid="stButton"]{ display:flex!important; justify-content:flex-end!important; margin-top:.72rem!important; }
@keyframes hillsDrift{
  0%{ transform:translate3d(0,-3px,0); }
  100%{ transform:translate3d(0,8px,0); }
}
@keyframes headlineFloat{
  0%,100%{ transform:translateY(0); opacity:.96; }
  50%{ transform:translateY(-8px); opacity:1; }
}
@media (max-width: 820px){
  .hills-brand{ right:.82rem!important; bottom:.62rem!important; font-size:.75rem!important; }
  .hills-credit{ left:.82rem!important; bottom:.58rem!important; max-width:8rem!important; font-size:.5rem!important; }
  .intro-hills-art{ min-height:230px!important; border-right:0!important; border-bottom:1px solid rgba(245,245,245,.11)!important; }
  .hills-svg{ transform:perspective(380px) rotateX(58deg) translateY(-2px) scale(1.2); }
  .hills-caption{ display:none!important; }
  .hills-float-title{ top:2.1rem!important; left:.85rem!important; right:.85rem!important; }
  .hills-float-title span{ font-size:1.18rem!important; }
  .hills-float-title strong{ font-size:1.62rem!important; }
  .hills-float-title em{ font-size:.58rem!important; }
  .intro-flow-card{ grid-template-columns:34px minmax(0,1fr)!important; min-height:88px!important; padding:.68rem!important; }
}

@media (max-width: 780px){
  .block-container{ padding-top:3.4rem!important; padding-left:1rem!important; padding-right:1rem!important; }
  .hero{ padding:1.5rem!important; border-radius:16px!important; }
  .brand h1{ font-size:1.85rem!important; }
  .land-grid{ grid-template-columns:1fr!important; }
}
</style>
""",
        unsafe_allow_html=True,
    )
