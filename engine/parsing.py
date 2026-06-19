"""Document parsing + lightweight section segmentation.

Wraps `reviewer.parsers.parse_document` (reused as-is) and adds heuristic
segmentation into labeled sections, plus isolation of the reference list and tables.
No Streamlit. No LLM calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import engine  # noqa: F401 — sys.path bootstrap
from reviewer.parsers import parse_document  # type: ignore
from reviewer.utils import count_tokens, split_into_paragraphs  # type: ignore


# Canonical section buckets we try to map headings into.
CANONICAL = [
    "abstract", "introduction", "related_work", "background", "methods",
    "experiments", "results", "discussion", "conclusion", "references", "appendix",
]

_HEADING_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("abstract", re.compile(r"\babstracts?\b", re.I)),
    ("introduction", re.compile(r"\bintroduction\b", re.I)),
    ("related_work", re.compile(r"(related work|literature review|prior work|related studies|background and related)", re.I)),
    ("background", re.compile(r"\b(background|preliminaries|notations?)\b", re.I)),
    ("methods", re.compile(r"(methodolog|\bmethods?\b|\bapproach\b|\bmodel(s|ing|ling)?\b|\bframework\b|proposed|materials and methods|study design|data and methods)", re.I)),
    ("experiments", re.compile(r"(experiment|experimental setup|evaluation setup|study area|case study|data collection|datasets?)", re.I)),
    ("results", re.compile(r"(\bresults?\b|\bfindings?\b|\banalysis\b|empirical results)", re.I)),
    ("discussion", re.compile(r"(discussion|implications)", re.I)),
    ("conclusion", re.compile(r"(conclusion|concluding remarks|future work)", re.I)),
    ("references", re.compile(r"(references|bibliography|works cited|literature cited)", re.I)),
    ("appendix", re.compile(r"(appendix|supplementary|supplemental)", re.I)),
]

_MD_HEADING = re.compile(r"^\s{0,3}(#{1,4})\s+(.+?)\s*#*\s*$")
# numbered headings like "3. Methods" / "III. Methods" / "3 Methods"
_NUM_HEADING = re.compile(r"^\s*((?:\d{1,2}(?:\.\d{1,2})*)|(?:[IVXivx]{1,5}))[\.\)]?\s+([A-Z][A-Za-z].{0,60})$")


@dataclass
class Section:
    label: str            # canonical bucket or "other"
    heading: str          # original heading text
    text: str = ""

    @property
    def tokens(self) -> int:
        return count_tokens(self.text)


@dataclass
class ParsedPaper:
    title: str
    full_text: str
    was_ocr: bool
    parse_engine: str
    sections: list[Section] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    references_block: str = ""
    tables: list[str] = field(default_factory=list)

    @property
    def tokens(self) -> int:
        return count_tokens(self.full_text)

    def section_text(self, *labels: str) -> str:
        """Concatenated text for the given canonical labels (in document order)."""
        wanted = set(labels)
        parts = [s.text for s in self.sections if s.label in wanted]
        return "\n\n".join(p for p in parts if p.strip())

    def has(self, label: str) -> bool:
        return any(s.label == label and s.text.strip() for s in self.sections)


def _classify_heading(heading: str) -> str:
    h = heading.strip()
    for label, pat in _HEADING_PATTERNS:
        if pat.search(h):
            return label
    return "other"


def _iter_heading_lines(text: str):
    """Yield (line_index, heading_text) for markdown or numbered headings."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = _MD_HEADING.match(line)
        if m:
            yield i, m.group(2).strip()
            continue
        # numbered heading: short line, title-cased, not ending with a period sentence
        if len(line) < 70:
            m2 = _NUM_HEADING.match(line)
            if m2 and len(m2.group(2).split()) <= 8:
                yield i, m2.group(2).strip()


def segment_sections(text: str) -> list[Section]:
    """Heuristically split a document into labeled sections by headings."""
    lines = text.split("\n")
    heading_idx = list(_iter_heading_lines(text))
    if not heading_idx:
        return [Section(label="other", heading="(document)", text=text.strip())]

    sections: list[Section] = []
    # preamble before the first heading
    first = heading_idx[0][0]
    pre = "\n".join(lines[:first]).strip()
    if pre:
        sections.append(Section(label="abstract" if len(pre) < 4000 else "other",
                                heading="(front matter)", text=pre))

    for k, (li, htext) in enumerate(heading_idx):
        end = heading_idx[k + 1][0] if k + 1 < len(heading_idx) else len(lines)
        body = "\n".join(lines[li + 1:end]).strip()
        sections.append(Section(label=_classify_heading(htext), heading=htext, text=body))
    return sections


def _extract_references(sections: list[Section]) -> str:
    refs = [s.text for s in sections if s.label == "references"]
    return "\n\n".join(refs).strip()


_TABLE_RE = re.compile(r"(?:^\|.*\|$\n?)+", re.M)


def _extract_tables(text: str) -> list[str]:
    return [m.group(0).strip() for m in _TABLE_RE.finditer(text)][:25]


def parse_paper(file_path: str | Path, ocr: str | None = None) -> ParsedPaper:
    """Parse a file or URL into a ParsedPaper with sections + references + tables."""
    ocr_arg = None if ocr in (None, "auto") else ocr
    title, full_text, was_ocr = parse_document(file_path, ocr=ocr_arg)
    engine_used = getattr(parse_document, "_last_ocr_engine", "")

    sections = segment_sections(full_text)
    paragraphs = split_into_paragraphs(full_text)
    return ParsedPaper(
        title=title,
        full_text=full_text,
        was_ocr=was_ocr,
        parse_engine=engine_used or ("direct" if not was_ocr else "ocr"),
        sections=sections,
        paragraphs=paragraphs,
        references_block=_extract_references(sections),
        tables=_extract_tables(full_text),
    )
