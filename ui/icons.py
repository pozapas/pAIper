"""Inline SVG icon set (hand-authored, line style, 24×24 viewBox).

No emojis anywhere in the app — these are used instead. Icons inherit color via
`currentColor` by default, or accept an explicit color. Stroke-based (Lucide-like).
"""

from __future__ import annotations

# Each value is the inner markup of a 0 0 24 24 SVG. Stroke = currentColor unless the
# name is in _FILLED.
ICONS: dict[str, str] = {
    # brand / nav
    "logo": '<path d="M6 2h8l4 4v16H6z"/><circle cx="11.5" cy="13" r="3"/><line x1="13.7" y1="15.2" x2="16.5" y2="18"/>',
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.6" y2="16.6"/>',
    "upload": '<path d="M12 16V4"/><polyline points="7 9 12 4 17 9"/><path d="M5 20h14"/>',
    "key": '<circle cx="7.5" cy="8" r="3.5"/><line x1="10" y1="10.5" x2="20" y2="20"/><line x1="17" y1="17" x2="19.5" y2="14.5"/><line x1="20" y1="20" x2="22" y2="18"/>',
    "sliders": '<line x1="4" y1="8" x2="20" y2="8"/><circle cx="9" cy="8" r="2.2"/><line x1="4" y1="16" x2="20" y2="16"/><circle cx="15" cy="16" r="2.2"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4"/>',
    "book": '<path d="M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z"/><line x1="9" y1="8" x2="14" y2="8"/><line x1="9" y1="12" x2="14" y2="12"/>',
    "link": '<path d="M9.5 14.5l5-5"/><path d="M11 6.5l1.2-1.2a3.8 3.8 0 0 1 5.5 5.5L16.5 12"/><path d="M13 17.5l-1.2 1.2a3.8 3.8 0 0 1-5.5-5.5L7.5 12"/>',
    "file": '<path d="M6 2h8l4 4v16H6z"/><polyline points="14 2 14 6 18 6"/>',
    "file-text": '<path d="M6 2h8l4 4v16H6z"/><polyline points="14 2 14 6 18 6"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="15" y2="16"/>',
    "download": '<path d="M12 4v12"/><polyline points="7 11 12 16 17 11"/><path d="M5 20h14"/>',

    # severities / status
    "alert-triangle": '<path d="M12 3.5l9 16H3z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="16.8" r="0.7"/>',
    "alert-circle": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="7" x2="12" y2="13"/><circle cx="12" cy="16.3" r="0.7"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><polyline points="8 12.2 11 15 16 9.2"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>',
    "check": '<polyline points="5 12.5 10 17 19 7"/>',
    "x": '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>',
    "minus": '<line x1="6" y1="12" x2="18" y2="12"/>',
    "info": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="7.8" r="0.7"/>',

    # dimensions
    "lightbulb": '<path d="M9 17h6"/><path d="M10 20h4"/><path d="M12 3a6 6 0 0 0-4 10c.7.7 1 1.4 1 2h6c0-.6.3-1.3 1-2a6 6 0 0 0-4-10z"/>',
    "compare": '<line x1="12" y1="4" x2="12" y2="20"/><polyline points="7 8 4 11 7 14"/><polyline points="17 10 20 13 17 16"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6l-5 9a1.8 1.8 0 0 0 1.6 2.8h10.8A1.8 1.8 0 0 0 19 18l-5-9V3"/><line x1="8" y1="15" x2="16" y2="15"/>',
    "bar-chart": '<line x1="4" y1="20" x2="20" y2="20"/><rect x="6" y="11" width="3" height="7"/><rect x="11" y="6.5" width="3" height="11.5"/><rect x="16" y="13.5" width="3" height="4.5"/>',
    "scale": '<path d="M12 4v16"/><path d="M7 20h10"/><path d="M4 8l3-3 3 3"/><path d="M14 8l3-3 3 3"/><path d="M4 8a3 3 0 0 0 6 0"/><path d="M14 8a3 3 0 0 0 6 0"/>',
    "shield-check": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/><polyline points="8.5 12 11 14.5 15.5 9.5"/>',
    "pen": '<path d="M4 20l4-1L19 8l-3-3L5 16z"/><line x1="14" y1="7" x2="17" y2="10"/>',
    "scan-text": '<path d="M5 7V5a1 1 0 0 1 1-1h2"/><path d="M16 4h2a1 1 0 0 1 1 1v2"/><path d="M19 17v2a1 1 0 0 1-1 1h-2"/><path d="M8 20H6a1 1 0 0 1-1-1v-2"/><line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="14" y2="14"/>',
    "fingerprint": '<path d="M12 5a7 7 0 0 1 7 7"/><path d="M5 12a7 7 0 0 1 9.5-6.5"/><path d="M8 12a4 4 0 0 1 8 0v2"/><path d="M12 12v4"/><path d="M9 16c0 2 .5 3 .5 3"/><path d="M16 14c0 3-1 5-1 5"/>',

    # misc / landing
    "gauge": '<path d="M4.5 18a8 8 0 0 1 15 0"/><line x1="12" y1="18" x2="16.5" y2="11"/><circle cx="12" cy="18" r="1.1"/>',
    "list-checks": '<polyline points="3 6 4 7 6 5"/><line x1="9" y1="6" x2="20" y2="6"/><polyline points="3 12 4 13 6 11"/><line x1="9" y1="12" x2="20" y2="12"/><polyline points="3 18 4 19 6 17"/><line x1="9" y1="18" x2="20" y2="18"/>',
    "arrow-right": '<line x1="4" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/>',
    "graduation": '<path d="M2 9l10-4 10 4-10 4z"/><path d="M6 11v4.5c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V11"/><line x1="22" y1="9" x2="22" y2="14"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3c2.6 2.4 4 5.6 4 9s-1.4 6.6-4 9c-2.6-2.4-4-5.6-4-9s1.4-6.6 4-9z"/>',
    "zap": '<polygon points="13 2 5 13 11 13 10 22 19 10 13 10"/>',
    "layers": '<polygon points="12 3 21 8 12 13 3 8"/><polyline points="3 13 12 18 21 13"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><line x1="9" y1="3" x2="9" y2="6"/><line x1="15" y1="3" x2="15" y2="6"/><line x1="9" y1="18" x2="9" y2="21"/><line x1="15" y1="18" x2="15" y2="21"/><line x1="3" y1="9" x2="6" y2="9"/><line x1="3" y1="15" x2="6" y2="15"/><line x1="18" y1="9" x2="21" y2="9"/><line x1="18" y1="15" x2="21" y2="15"/>',
    "sparkles": '<path d="M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6z"/><path d="M18 15l.7 1.8L20.5 17.5l-1.8.7L18 20l-.7-1.8L15.5 17.5l1.8-.7z"/>',
    "quote": '<path d="M8 7H5a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h2v1a2 2 0 0 1-2 2"/><path d="M18 7h-3a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h2v1a2 2 0 0 1-2 2"/>',
    "rocket": '<path d="M5 15c-1 1-1 4-1 4s3 0 4-1l2-2-3-3z"/><path d="M14 4c3 0 6 3 6 6 0 2-5 7-9 9l-6-6c2-4 7-9 9-9z"/><circle cx="14.5" cy="9.5" r="1.6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="5" y1="5" x2="7" y2="7"/><line x1="17" y1="17" x2="19" y2="19"/><line x1="19" y1="5" x2="17" y2="7"/><line x1="7" y1="17" x2="5" y2="19"/>',
    "moon": '<path d="M20 14a8 8 0 0 1-10-10 8 8 0 1 0 10 10z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/>',
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
}

_FILLED = {"zap", "sparkles", "logo"}


def ic(name: str, size: int = 18, color: str = "currentColor", sw: float = 2.0,
       cls: str = "") -> str:
    """Return an inline <svg> string for the named icon."""
    inner = ICONS.get(name, ICONS["info"])
    fill = color if name in _FILLED else "none"
    stroke = "none" if name in _FILLED else color
    cls_attr = f' class="{cls}"' if cls else ""
    return (
        f'<svg{cls_attr} width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;flex-shrink:0">{inner}</svg>'
    )


# severity / status → icon name
SEV_ICON = {"CRITICAL": "x-circle", "MAJOR": "alert-triangle",
            "MINOR": "alert-circle", "PRAISE": "check-circle"}
STATUS_ICON = {"PASS": "check-circle", "FAIL": "x-circle", "UNCLEAR": "alert-circle",
               "NA": "minus", "VERIFIED": "check-circle", "NOT_FOUND": "x-circle",
               "MISMATCH": "alert-triangle", "UNPARSEABLE": "minus", "UNCHECKED": "minus"}
DIM_ICON = {"contribution": "lightbulb", "related_work": "compare",
            "methodology": "flask", "statistics": "bar-chart",
            "results_claims": "scale", "reproducibility": "shield-check",
            "writing": "pen", "correctness": "scan-text", "hallucination": "fingerprint"}
