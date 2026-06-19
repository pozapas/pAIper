"""
AI Paper Reviewer — review engine.

This package is fully decoupled from the Streamlit UI: nothing here imports
`streamlit`. A future FastAPI/Next.js frontend can wrap this package directly.

It reuses two battle-tested pieces of the bundled OpenAIReview project:
  * `reviewer.parsers`  — multi-format parsing (PDF/OCR, DOCX, TEX, MD, TXT, arXiv)
  * `reviewer.client`   — multi-provider chat client with retries

The path to that project is wired up here so `import reviewer...` works no matter
where the app is launched from.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── make the bundled OpenAIReview package importable ─────────────────────────
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE.parent.parent / "OpenAIReview-main" / "OpenAIReview-main" / "src",
    _HERE.parent.parent / "OpenAIReview-main" / "src",
    _HERE.parent / "OpenAIReview-main" / "src",
]
for _c in _CANDIDATES:
    if _c.exists() and str(_c) not in sys.path:
        sys.path.insert(0, str(_c))
        break

__all__ = ["__version__"]
__version__ = "1.0.0"
