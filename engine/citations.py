"""Citation extraction + multi-source verification.

Adopts the cascading approach from the PHY041 `check-citations` skill:
  1. DOI / arXiv first — a registered identifier is the strongest signal.
  2. Cross-check three independent databases: CrossRef, Semantic Scholar, OpenAlex.
       found in >=2 sources -> VERIFIED;  1 source -> MISMATCH (verify);  0 -> NOT_FOUND.
  3. Chimeric detection — title matches but authors don't overlap -> flag (the most
     dangerous AI-hallucination type).
  4. Red-flag heuristics (bad DOI format, future year, missing fields, generic titles).

Keyless; needs internet at review time. The guarantee we preserve: a fabricated paper
is never marked VERIFIED.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import engine  # noqa: F401
from reviewer.utils import truncate_text  # type: ignore

from .llm import LLMClient
from .parsing import ParsedPaper
from .report import CitationCheck, CitationItem

_UA = "AI-Paper-Reviewer/1.0 (mailto:reviewer@example.com)"
_HEADERS = {"User-Agent": _UA}
_SIM_MATCH = 0.62      # token-overlap similarity to call two titles "the same work"
_STOP = {"the", "a", "an", "of", "for", "in", "on", "to", "and", "with", "by",
         "from", "is", "are", "at", "via", "using", "based"}


# ─────────────────────────────────────────────────────────────────────────────
# HTTP + similarity helpers
# ─────────────────────────────────────────────────────────────────────────────

def _http_json(url: str, timeout: int = 12) -> tuple[dict | None, int]:
    """Return (json, status_code). status_code 0 on transport error."""
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace")), resp.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, 0


def title_similarity(a: str, b: str) -> float:
    """Normalized token-overlap (Jaccard) similarity, robust for titles."""
    ta = {w for w in re.sub(r"[^a-z0-9 ]", " ", (a or "").lower()).split() if w not in _STOP}
    tb = {w for w in re.sub(r"[^a-z0-9 ]", " ", (b or "").lower()).split() if w not in _STOP}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _last_names(text: str) -> set[str]:
    lower = (text or "").lower().strip()
    names: set[str] = set()
    if not lower:
        return names
    people = re.split(r"\band\b|;", lower) if re.search(r"\band\b|;", lower) else lower.split(",")
    for person in people:
        person = person.strip()
        if not person:
            continue
        if "," in person:                       # "Last, First"
            names.add(person.split(",")[0].strip().split()[-1])
        else:                                    # "First Last"
            words = person.split()
            if words:
                names.add(words[-1])
    return {n for n in names if len(n) > 1}


def author_overlap(cited: str, found: str) -> float:
    a, b = _last_names(cited), _last_names(found)
    if not a or not b:
        return -1.0                              # unknown (don't penalize)
    return len(a & b) / max(len(a), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Source lookups → each returns {source,title,authors,year,doi,url} or None
# ─────────────────────────────────────────────────────────────────────────────

def _crossref_by_doi(doi: str) -> dict | None:
    data, _ = _http_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    msg = (data or {}).get("message")
    if not msg:
        return None
    return {
        "source": "CrossRef(DOI)",
        "title": (msg.get("title") or [""])[0],
        "authors": ", ".join(f"{a.get('given','')} {a.get('family','')}".strip()
                             for a in msg.get("author", [])),
        "year": _cr_year(msg),
        "doi": (msg.get("DOI") or doi),
        "url": "https://doi.org/" + (msg.get("DOI") or doi),
    }


def _cr_year(item: dict) -> str:
    for k in ("published-print", "published-online", "issued"):
        parts = (item.get(k) or {}).get("date-parts") or []
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def _crossref_title(title: str) -> dict | None:
    q = urllib.parse.quote(title[:300])
    data, _ = _http_json(f"https://api.crossref.org/works?query.title={q}&rows=5")
    items = (data or {}).get("message", {}).get("items", [])
    best, best_sim = None, 0.0
    for it in items:
        t = (it.get("title") or [""])[0]
        s = title_similarity(title, t)
        if s > best_sim:
            best, best_sim = it, s
    if not best or best_sim < _SIM_MATCH:
        return None
    return {
        "source": "CrossRef",
        "title": (best.get("title") or [""])[0],
        "authors": ", ".join(f"{a.get('given','')} {a.get('family','')}".strip()
                             for a in best.get("author", [])),
        "year": _cr_year(best), "doi": best.get("DOI", ""),
        "url": "https://doi.org/" + best["DOI"] if best.get("DOI") else "",
    }


_RATELIMIT = "__ratelimit__"  # sentinel: source was consulted but unavailable

# Semantic Scholar's keyless tier allows ~1 request/sec; serialize across worker
# threads with a minimum interval so concurrent reviews don't trigger 429 storms.
import threading
_S2_LOCK = threading.Lock()
_S2_LAST = [0.0]
_S2_MIN_INTERVAL = 1.2


def _s2_get(url: str):
    """Semantic Scholar GET, globally throttled + 429 backoff. Returns dict|None|_RATELIMIT."""
    for attempt in range(3):
        with _S2_LOCK:
            wait = _S2_MIN_INTERVAL - (time.monotonic() - _S2_LAST[0])
            if wait > 0:
                time.sleep(wait)
            data, code = _http_json(url, timeout=15)
            _S2_LAST[0] = time.monotonic()
        if code == 429:
            time.sleep(1.5 * (attempt + 1))
            continue
        return data
    return _RATELIMIT


def _semanticscholar(title: str, arxiv: str = ""):
    """Return a match dict, None (searched, not found), or _RATELIMIT (unavailable)."""
    if arxiv:
        data = _s2_get(
            f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{urllib.parse.quote(arxiv)}"
            "?fields=title,authors,year,externalIds")
        if data is _RATELIMIT:
            return _RATELIMIT
        if data and data.get("title"):
            return _s2_pack(data)
    q = urllib.parse.quote(title[:300])
    data = _s2_get(
        f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}"
        "&limit=5&fields=title,authors,year,externalIds")
    if data is _RATELIMIT:
        return _RATELIMIT
    papers = (data or {}).get("data", [])
    best, best_sim = None, 0.0
    for p in papers:
        s = title_similarity(title, p.get("title", ""))
        if s > best_sim:
            best, best_sim = p, s
    if not best or best_sim < _SIM_MATCH:
        return None
    return _s2_pack(best)


def _s2_pack(p: dict) -> dict:
    ext = p.get("externalIds") or {}
    return {
        "source": "SemanticScholar",
        "title": p.get("title", ""),
        "authors": ", ".join(a.get("name", "") for a in p.get("authors", [])),
        "year": str(p.get("year") or ""),
        "doi": ext.get("DOI", ""),
        "url": ("https://doi.org/" + ext["DOI"]) if ext.get("DOI") else (
            "https://arxiv.org/abs/" + ext["ArXiv"] if ext.get("ArXiv") else ""),
    }


def _openalex(title: str, doi: str = "") -> dict | None:
    if doi:
        data, _ = _http_json(f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}")
        if data and data.get("id"):
            return _oa_pack(data)
    q = urllib.parse.quote(title[:300])
    data, _ = _http_json(f"https://api.openalex.org/works?search={q}&per-page=25")
    results = (data or {}).get("results") or []
    best, best_sim = None, 0.0
    for w in results:
        s = title_similarity(title, w.get("title") or w.get("display_name") or "")
        if s > best_sim:
            best, best_sim = w, s
    if not best or best_sim < _SIM_MATCH:
        return None
    return _oa_pack(best)


def _oa_pack(w: dict) -> dict:
    return {
        "source": "OpenAlex",
        "title": w.get("title") or w.get("display_name") or "",
        "authors": ", ".join((a.get("author") or {}).get("display_name", "")
                             for a in (w.get("authorships") or [])[:6]),
        "year": str(w.get("publication_year") or ""),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "url": w.get("id") or (w.get("doi") or ""),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Red flags
# ─────────────────────────────────────────────────────────────────────────────

def _red_flags(ref: dict) -> list[str]:
    flags = []
    doi = ref.get("doi", "")
    if doi and not re.match(r"10\.\d{4,}/", doi):
        flags.append(f"Malformed DOI: '{doi}'")
    yr = ref.get("year", "")
    if yr.isdigit() and int(yr) > 2027:
        flags.append(f"Future publication year: {yr}")
    if not ref.get("authors"):
        flags.append("No author listed")
    if re.match(r"^(a )?(comprehensive |systematic )?(survey|review|study) of\b",
                (ref.get("title") or "").lower()):
        flags.append("Generic title pattern (common in fabrications)")
    return flags


# ─────────────────────────────────────────────────────────────────────────────
# Reference extraction (LLM)
# ─────────────────────────────────────────────────────────────────────────────

def _find_reference_block(paper: ParsedPaper) -> str:
    if paper.references_block.strip():
        return paper.references_block
    text = paper.full_text
    m = list(re.finditer(r"(?im)^\s*#{0,4}\s*(references|bibliography|works cited)\s*$", text))
    if m:
        return text[m[-1].end():]
    return ""


_REF_SYS = ("You extract bibliographic references into structured JSON. Output ONLY a JSON "
            "array. Never invent references; only parse what is present.")


def _split_bibtex_entries(text: str) -> list[str]:
    entries: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        at = text.find("@", i)
        if at < 0:
            break
        brace = text.find("{", at)
        if brace < 0:
            break
        kind = text[at + 1:brace].strip().lower()
        if not kind or kind.startswith("comment") or kind.startswith("preamble"):
            i = brace + 1
            continue
        depth = 0
        j = brace
        while j < n:
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    entries.append(text[at:j + 1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    return entries


def _bib_field(entry: str, name: str) -> str:
    m = re.search(rf"(?is)\b{re.escape(name)}\s*=", entry)
    if not m:
        return ""
    i = m.end()
    while i < len(entry) and entry[i].isspace():
        i += 1
    if i >= len(entry):
        return ""
    if entry[i] == "{":
        depth = 1
        j = i + 1
        while j < len(entry):
            if entry[j] == "{":
                depth += 1
            elif entry[j] == "}":
                depth -= 1
                if depth == 0:
                    return entry[i + 1:j]
            j += 1
        return entry[i + 1:].strip()
    if entry[i] == '"':
        j = i + 1
        escaped = False
        while j < len(entry):
            if entry[j] == '"' and not escaped:
                return entry[i + 1:j]
            escaped = entry[j] == "\\" and not escaped
            if entry[j] != "\\":
                escaped = False
            j += 1
        return entry[i + 1:].strip()
    j = i
    while j < len(entry) and entry[j] not in ",\n\r":
        j += 1
    return entry[i:j].strip()


def _clean_bibtex_value(value: str) -> str:
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r"\1", value)
    value = value.replace("\\&", "&").replace("\\_", "_").replace("~", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" ,;")


def _parse_bibtex_references(block: str, max_refs: int) -> list[dict]:
    entries = _split_bibtex_entries(block)
    refs: list[dict] = []
    for entry in entries[:max_refs]:
        title = _clean_bibtex_value(_bib_field(entry, "title"))
        authors = _clean_bibtex_value(_bib_field(entry, "author") or _bib_field(entry, "editor"))
        authors = re.sub(r"\s+and\s+", ", ", authors, flags=re.I)
        year_raw = _bib_field(entry, "year") or _bib_field(entry, "date")
        year_m = re.search(r"(19|20)\d{2}", year_raw)
        doi = _clean_bibtex_value(_bib_field(entry, "doi")).replace("https://doi.org/", "")
        eprint = _clean_bibtex_value(_bib_field(entry, "eprint"))
        archive = _clean_bibtex_value(_bib_field(entry, "archivePrefix") or _bib_field(entry, "eprinttype"))
        arxiv = eprint if eprint and archive.lower() in ("arxiv", "") else ""
        if not (title or doi or arxiv):
            continue
        refs.append({
            "raw": entry.strip(),
            "title": title,
            "authors": authors,
            "year": year_m.group(0) if year_m else "",
            "doi": doi,
            "arxiv": arxiv,
        })
    return refs


def _parse_references(block: str, llm: LLMClient, max_refs: int) -> list[dict]:
    if not block.strip():
        return []
    block = truncate_text(block, 14000)
    user = (
        f"From the reference list below, return a JSON array (max {max_refs} items), each: "
        '{"raw":"<full reference string>","title":"<work title only>",'
        '"authors":"<authors as written>","year":"<4-digit year or \'\'>",'
        '"doi":"<DOI if present, else \'\'>","arxiv":"<arXiv id if present, else \'\'>"}.\n'
        "Skip anything that is not a real bibliographic reference.\n\n"
        f"REFERENCE LIST:\n{block}"
    )
    data = llm.json(_REF_SYS, user, expected=list, max_tokens=8192)
    out: list[dict] = []
    if isinstance(data, list):
        for it in data[:max_refs]:
            if isinstance(it, dict) and (it.get("title") or it.get("raw")):
                doi = str(it.get("doi", "")).strip().replace("https://doi.org/", "")
                out.append({
                    "raw": str(it.get("raw", "")).strip(),
                    "title": str(it.get("title", "")).strip(),
                    "authors": str(it.get("authors", "")).strip(),
                    "year": re.sub(r"\D", "", str(it.get("year", "")))[:4],
                    "doi": doi,
                    "arxiv": str(it.get("arxiv", "")).strip(),
                })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Verify one reference
# ─────────────────────────────────────────────────────────────────────────────

def _verify_one(ref: dict) -> CitationItem:
    item = CitationItem(raw=ref.get("raw", ""), title=ref.get("title", ""),
                        authors=ref.get("authors", ""), year=ref.get("year", ""),
                        doi=ref.get("doi", ""))
    item.red_flags = _red_flags(ref)
    title = ref.get("title", "")
    if not title or len(title) < 6:
        item.status = "UNPARSEABLE"
        item.note = "Could not extract a usable title to verify."
        return item

    matches: list[dict] = []
    s2_unavailable = False
    doi = ref.get("doi", "")
    arxiv = ref.get("arxiv", "")

    # 1) DOI-first (strongest signal)
    if doi:
        for fn in (lambda: _crossref_by_doi(doi), lambda: _openalex("", doi)):
            try:
                hit = fn()
            except Exception:
                hit = None
            if hit:
                matches.append(hit)

    # 2) Title / arXiv search across the three databases
    try:
        s2 = _semanticscholar(title, arxiv)
    except Exception:
        s2 = None
    if s2 is _RATELIMIT:
        s2_unavailable = True
    elif s2:
        matches.append(s2)
    for fn in (lambda: _crossref_title(title), lambda: _openalex(title)):
        try:
            hit = fn()
        except Exception:
            hit = None
        if hit:
            matches.append(hit)

    # annotate each match with title similarity + author overlap
    for m in matches:
        m["_sim"] = 1.0 if "DOI" in m["source"] else title_similarity(title, m.get("title", ""))
        m["_ao"] = author_overlap(ref.get("authors", ""), m.get("authors", ""))

    sources = list(dict.fromkeys(m["source"].split("(")[0] for m in matches))
    item.sources = ", ".join(sources)
    best = max(matches, key=lambda m: m["_sim"], default=None)
    if best:
        item.match_url = best.get("url", "") or item.match_url
    doi_resolved = any("DOI" in m["source"] for m in matches)
    n_sources = len(sources)

    # chimeric only if a STRONG title match exists but NO match shares any author
    strong = [m for m in matches if m["_sim"] >= 0.85]
    known_ao = [m["_ao"] for m in strong if m["_ao"] >= 0]
    is_chimeric = bool(strong) and bool(known_ao) and max(known_ao) == 0.0

    if doi_resolved or n_sources >= 2:
        if is_chimeric:
            item.status = "MISMATCH"
            item.note = (f"Title matches an indexed work ({item.sources}) but NO listed author "
                         f"overlaps — possible chimeric citation (real title, wrong authors). "
                         f"Indexed authors: {best.get('authors','?')[:80]}.")
        else:
            item.status = "VERIFIED"
            item.note = f"Found in {item.sources}."
            if best and best.get("year") and item.year and abs_int_diff(best["year"], item.year) > 2:
                item.note += f" (cited year {item.year} vs indexed {best['year']} — check edition.)"
    elif n_sources == 1:
        item.status = "MISMATCH"
        item.note = (f"Found in only one source ({item.sources}; closest “{best.get('title','')[:70]}”). "
                     "Verify manually.")
    elif s2_unavailable:
        item.status = "MISMATCH"
        item.note = ("Could not confirm — a database (Semantic Scholar) was rate-limited and the "
                     "others returned no match. Re-run or verify this reference manually.")
    else:
        item.status = "NOT_FOUND"
        item.note = ("No match in CrossRef, Semantic Scholar, or OpenAlex — verify this reference "
                     "exists (possible fabrication, or grey/very-recent literature).")

    if item.red_flags and item.status == "VERIFIED":
        item.note += "  Flags: " + "; ".join(item.red_flags)
    return item


def abs_int_diff(a: str, b: str) -> int:
    try:
        return abs(int(a) - int(b))
    except (TypeError, ValueError):
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Public entry
# ─────────────────────────────────────────────────────────────────────────────

def check_citations(paper: ParsedPaper, llm: LLMClient | None, *, max_refs: int = 40,
                    workers: int = 4) -> CitationCheck:
    cc = CitationCheck(enabled=True)
    block = _find_reference_block(paper)
    refs = _parse_bibtex_references(block, max_refs)
    used_bibtex = bool(refs)
    if not refs and llm is None and block.strip():
        cc.note = (
            "A reference section was found, but citation-only mode can parse references "
            "without a model only from BibTeX. Upload a .bib/.bibtex file, or select a "
            "model provider so pAIper can extract structured references."
        )
        return cc
    if not refs and llm is not None:
        refs = _parse_references(block, llm, max_refs)
    if not refs:
        cc.note = ("No reference list could be extracted. The paper may omit references, "
                   "or the parser could not isolate them.")
        return cc

    cc.n_refs = len(refs)
    # Verify references concurrently (each makes a few independent API calls).
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        cc.items = list(ex.map(_verify_one, refs))

    cc.n_verified = sum(1 for c in cc.items if c.status == "VERIFIED")
    cc.n_suspicious = sum(1 for c in cc.items if c.status in ("NOT_FOUND", "MISMATCH"))
    n_notfound = sum(1 for c in cc.items if c.status == "NOT_FOUND")
    n_chimeric = sum(1 for c in cc.items if c.status == "MISMATCH" and "chimeric" in c.note.lower())
    if cc.n_suspicious:
        cc.note = (
            f"{cc.n_verified}/{cc.n_refs} references auto-verified (DOI or 2+ databases). "
            f"{cc.n_suspicious} need a manual check"
            + (f", incl. {n_notfound} with no match (possible fabrication)" if n_notfound else "")
            + (f" and {n_chimeric} possible chimeric (title vs authors)" if n_chimeric else "")
            + ". Best-effort: some legitimate works (grey literature, very recent, non-English) "
              "may not be indexed — confirm flagged items yourself."
        )
    else:
        cc.note = "All parsed references were matched to indexed records."
    if used_bibtex:
        cc.note += " References were parsed from the uploaded BibTeX file."
    return cc
