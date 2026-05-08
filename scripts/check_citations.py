"""
check_citations.py — Deterministic citation checker (layer 2 of validation).

For every [p.X], [p.X-Y], [ch.Y] marker in a summary, verifies against the
extracted source text in books/extracted/<slug>/ that:
  1. The page number falls within n_pages (no fabricated pages).
  2. A [PAGE X] marker for that page actually exists in the chapter files.
  3. At least one non-trivial token from the cited assertion appears in the
     cited page (±1 page tolerance). Catches blatant mis-citations without
     requiring semantic understanding.

[p.?] is counted as a "soft" citation (logged, not failed — the book-reader
is allowed to use it when a fact is clearly from the book but page is unknown).

Usage:
  python scripts/check_citations.py <slug>
  python scripts/check_citations.py <slug> --json
  python scripts/check_citations.py <slug> --max-soft 10

Exit codes:
  0 — all citations verified
  1 — one or more citations failed deterministic checks
  2 — I/O error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = ROOT / "books" / "extracted"
SUMMARIES_DIR = ROOT / "books" / "summaries"

# Citation forms recognised:
#   [p.45]            → page 45
#   [p.45-47]         → pages 45-47
#   [p.?]             → soft (unknown page)
#   [ch.3]            → chapter 3
#   [ch.3, p.45]      → chapter 3 + page 45
#   [cap. 4, p.89]    → same, Portuguese variant (used in book-reader template)
CITATION_RE = re.compile(
    r"\["
    r"(?:"
        # Branch A — chapter-first (legacy): [ch.Y, p.X-Y]
        r"(?:ch|cap)\.?\s*(?P<ch_a>\d+)\s*,?\s*"
        r"(?:p\.?\s*(?P<p1_a>\d+|\?)(?:\s*[-\u2013\u2014]\s*(?P<p2_a>\d+))?)?"
      r"|"
        # Branch B — page-first with optional chapter via comma OR parens:
        # [p.X-Y], [p.X, ch.Y], [p.X (ch.Y)], [p.X\u20133, ch.Y]
        r"p\.?\s*(?P<p1_b>\d+|\?)(?:\s*[-\u2013\u2014]\s*(?P<p2_b>\d+))?"
        r"(?:\s*[,(]\s*(?:ch|cap)\.?\s*(?P<ch_b>\d+)\s*\)?)?"
    r")"
    r"\]",
    re.IGNORECASE,
)


def _coalesce_citation(m: re.Match) -> tuple[str | None, str | None, str | None]:
    """Return (ch, p1, p2) from a CITATION_RE match, coalescing branch-specific
    groups. Also accepts legacy hand-rolled matches that use the plain names
    `ch`, `p1`, `p2` (see test_chapter_intro_terms_are_warn_not_fail)."""
    groups = m.groupdict()
    ch = groups.get("ch_a") or groups.get("ch_b") or groups.get("ch")
    p1 = groups.get("p1_a") or groups.get("p1_b") or groups.get("p1")
    p2 = groups.get("p2_a") or groups.get("p2_b") or groups.get("p2")
    return ch, p1, p2

PAGE_MARKER_RE = re.compile(r"\[PAGE\s+(\d+)\]", re.IGNORECASE)

# Bare 1-4 digit line (candidate "printed page number" at top/bottom of a page)
BARE_PAGE_NUM_RE = re.compile(r"^\s*(\d{1,4})\s*$")
# Bracketed banner like "[ 188 ]" — Packt and similar publishers' running header/footer
BANNER_PAGE_NUM_RE = re.compile(r"^\s*\[\s*(\d{1,4})\s*\]\s*$")

# Tokens we strip from "key tokens" — too generic to prove presence.
STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "by", "is",
    "are", "was", "were", "be", "been", "with", "as", "at", "it", "this",
    "that", "these", "those", "from", "but", "not", "no", "so", "if", "then",
    "o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "no",
    "na", "nos", "nas", "para", "por", "com", "um", "uma", "que", "se", "ao",
    "como", "mais", "muito", "pode", "onde", "qual", "quais", "entre",
    "pitfall", "cite", "citado", "usa", "uso", "usar",
    "note", "notes", "nota", "notas", "obs", "observacao", "observation",
    # Greek letter names: summaries use LaTeX (`$\theta$` → token "theta") but
    # the source PDF renders the actual Greek symbol, which PDF-to-text either
    # preserves as non-ASCII (filtered by [a-z]{4,}) or OCR-mangles into
    # digits/latin lookalikes (θ→0, α→a). The name never survives as a reliable
    # fingerprint, so treating it as a stopword prevents false-positive misses.
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "omicron", "rho",
    "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
    "varepsilon", "varphi", "vartheta", "varsigma", "varrho", "varpi",
}

# PT→EN keyword map. Summaries are written in Portuguese; source texts are
# usually English — so single-token overlap fails on translated content words
# even when the citation is correct. We expand each PT assertion token with
# its EN counterpart; if either appears in the cited page window, we accept.
# Scope is intentionally focused on finance/stats/ML/book-structure vocabulary
# that recurs across the library.
PT_TO_EN: dict[str, str] = {
    # time / quantity
    "anos": "years", "ano": "year",
    "dias": "days", "dia": "day",
    "meses": "months", "mes": "month",
    "tempo": "time",
    "ultimos": "last", "ultimo": "last",
    "primeiros": "first", "primeiro": "first",
    "durante": "during",
    "duas": "two", "dois": "two",
    "tres": "three", "quatro": "four", "cinco": "five",
    "todas": "all", "todos": "all",
    "cada": "each",
    # book structure
    "livro": "book",
    "capitulos": "chapters", "capitulo": "chapter",
    "partes": "parts", "parte": "part",
    "secao": "section", "secoes": "sections",
    "dividido": "divided", "divididos": "divided",
    "apresenta": "presents", "apresentado": "presented",
    # finance / stats
    "regras": "rules", "regra": "rule",
    "binarias": "binary", "binaria": "binary",
    "retorno": "return", "retornos": "returns",
    "medio": "average", "media": "mean", "medias": "means",
    "testadas": "tested", "testado": "tested", "teste": "test",
    "melhor": "best", "pior": "worst",
    "observado": "observed", "observada": "observed",
    "valor": "value", "valores": "values",
    "maximo": "max", "minimo": "min",
    "serie": "series", "series": "series",
    "distribuicao": "distribution", "distribuicoes": "distributions",
    "inferiores": "lowest", "superiores": "highest",
    "inferior": "lower", "superior": "upper",
    "obter": "obtain", "obtido": "obtained",
    "remover": "remove", "removido": "removed",
    "otimizados": "optimized", "otimizado": "optimized",
    "otimizacao": "optimization",
    "capturar": "capture",
    "escalas": "scales", "escala": "scale",
    "extremos": "extremes",
    "divergencias": "divergences",
    "aumentar": "increase", "diminuir": "decrease",
    "suavizaria": "smooth", "suavizar": "smooth",
    "alteraria": "alter", "alterar": "alter",
    "conclusao": "conclusion",
    "replicacoes": "replications", "replicacao": "replication",
    "amostras": "samples", "amostra": "sample",
    "janela": "window", "janelas": "windows",
    "passado": "past", "futuro": "future",
    "preco": "price", "precos": "prices",
    "mercado": "market",
    "risco": "risk",
    "volatilidade": "volatility",
    "correlacao": "correlation",
    "significancia": "significance",
    "hipotese": "hypothesis",
    "nula": "null",
    "alternativa": "alternative",
    "amostragem": "sampling",
    "viés": "bias", "vies": "bias",
    "ruido": "noise",
    # logic / philosophy
    "argumento": "argument",
    "contem": "contains", "contendo": "containing",
    "contradicao": "contradiction", "contradicoes": "contradictions",
    "eficacia": "efficacy",
    "informacoes": "information", "informacao": "information",
    "justificativa": "justification",
    "logica": "logical", "logico": "logical",
    "premissa": "premise", "premissas": "premises",
    "verdadeiro": "true", "falso": "false",
    "evidencia": "evidence",
    "crenca": "belief", "crencas": "beliefs",
    "conhecimento": "knowledge",
    # H&S / technical patterns
    "picos": "peaks", "pico": "peak",
    "vales": "troughs", "vale": "trough",
    "simetria": "symmetry",
    "distancia": "distance",
    "ombro": "shoulder", "ombros": "shoulders",
    "esquerdo": "left", "direito": "right",
    "passo": "step", "passos": "steps",
    "identificar": "identify",
    "anterior": "prior", "anteriores": "prior",
    "tendencia": "trend",
    # MA / indicators
    "simples": "simple",
    "ponderada": "weighted", "ponderado": "weighted",
    "exponencial": "exponential",
    "movel": "moving",
}


def _strip_thousand_seps(text: str) -> str:
    """Normalise PT-style thousand separators so numbers tokenise correctly.

    In PT, "6.402" means 6,402 (six thousand four hundred and two). Without
    this step, the regex splits it into "6" and "402", both too short to
    become tokens — and the assertion loses its strongest fingerprint
    (a specific number that proves the claim).
    """
    # X.YYY where Y is exactly 3 digits — collapse the separator
    return re.sub(r"(\d)\.(\d{3})(?=\D|$)", r"\1\2", text)


@dataclass
class CitationCheck:
    assertion: str           # first 120 chars of the line
    raw: str                 # the literal [p.X] text
    ch: int | None = None
    p_start: int | None = None
    p_end: int | None = None
    soft: bool = False       # [p.?]
    verdict: str = "pending"  # pending|ok|fail|warn
    reason: str = ""
    actual_pdf_page: int | None = None  # where tokens cluster if initial match failed


@dataclass
class SystemicOffsetFinding:
    detected: bool
    offset: int | None = None
    coverage: float | None = None
    n_failures_explained: int = 0


def detect_systemic_offset(failures: list["CitationCheck"]) -> "SystemicOffsetFinding":
    """Given failures with `actual_pdf_page` recorded (wide search match),
    compute offset = actual_pdf_page - p_start.

    If ≥70% of failures with recorded actual_pdf_page share the same offset,
    declare SYSTEMIC_OFFSET.
    """
    from collections import Counter

    diffs = []
    for f in failures:
        actual = getattr(f, "actual_pdf_page", None)
        if actual is None or f.p_start is None:
            continue
        diffs.append(actual - f.p_start)

    if len(diffs) < 5:
        return SystemicOffsetFinding(detected=False)

    mode, count = Counter(diffs).most_common(1)[0]
    coverage = count / len(diffs)
    if coverage >= 0.70:
        return SystemicOffsetFinding(
            detected=True,
            offset=mode,
            coverage=coverage,
            n_failures_explained=count,
        )
    return SystemicOffsetFinding(detected=False)


@dataclass
class Report:
    slug: str
    n_total: int = 0
    n_ok: int = 0
    n_fail: int = 0
    n_soft: int = 0
    n_warn: int = 0
    offset: int = 0
    failures: list[CitationCheck] = field(default_factory=list)
    warnings: list[CitationCheck] = field(default_factory=list)
    soft_refs: list[CitationCheck] = field(default_factory=list)
    systemic_offset_detected: bool = False
    systemic_offset_value: int | None = None
    systemic_offset_coverage: float | None = None
    systemic_offset_n_explained: int = 0

    @property
    def ok(self) -> bool:
        return self.n_fail == 0


def _norm(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _tokens(text: str, expand_pt: bool = False) -> set[str]:
    text = _strip_thousand_seps(text)
    text = _norm(text)
    # Word tokens: alpha, length >= 4 (skip stopwords).
    words = {
        t for t in re.findall(r"[a-z]{4,}", text) if t not in STOPWORDS
    }
    # Numeric tokens: digits, length >= 2 — short numbers like "15", "60",
    # "1999", "6402" are strong fingerprints that transcend language.
    numbers = set(re.findall(r"\d{2,}", text))
    tokens = words | numbers
    if expand_pt:
        tokens = tokens | {PT_TO_EN[t] for t in tokens if t in PT_TO_EN}
    return tokens


def load_metadata(slug: str) -> dict:
    path = EXTRACTED_DIR / slug / "_metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"metadata not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_canonical_offset_map(slug: str) -> dict | None:
    """Read _page_index.json for slug (generated by build_page_index.py).

    Returns the parsed JSON if present (canonical source of truth for
    printed <-> pdf page mapping), else None (caller must fall back to
    heuristic detection).
    """
    path = EXTRACTED_DIR / slug / "_page_index.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def resolve_printed_to_pdf(
    slug: str,
    printed: int,
    canonical: dict | None = None,
) -> int | None:
    """Resolve a printed page number to its PDF page index using the
    canonical _page_index.json when available.

    Returns the PDF page or None if the mapping cannot be resolved.
    """
    cmap = canonical if canonical is not None else load_canonical_offset_map(slug)
    if cmap is None:
        return None
    printed_to_pdf = cmap.get("printed_to_pdf") or {}
    direct = printed_to_pdf.get(str(printed))
    if direct is not None:
        return int(direct)
    global_offset = cmap.get("global_mode_offset")
    if global_offset is not None:
        return int(printed) + int(global_offset)
    return None


def load_page_index(slug: str, meta: dict) -> dict[int, str]:
    """Return {pdf_page: page_text} built from all chapter files via
    [PAGE N] markers. Page text is everything between [PAGE N] and next marker.
    """
    pages: dict[int, str] = {}
    ch_index = meta["chapter_index"]
    extract_root = EXTRACTED_DIR / slug
    for ch in ch_index:
        ch_path = extract_root / ch["file"]
        if not ch_path.exists():
            continue
        text = ch_path.read_text(encoding="utf-8", errors="replace")
        markers = list(PAGE_MARKER_RE.finditer(text))
        for i, m in enumerate(markers):
            page_n = int(m.group(1))
            start = m.end()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
            pages[page_n] = text[start:end]
    return pages


def detect_printed_pdf_offset(pages: dict[int, str]) -> int:
    """Detect the offset between book-printed page numbers and PDF page
    indices by sampling bare-digit lines at the top/bottom of each page.

    Returns the most frequent (pdf_page - printed_page) offset. If no
    reliable signal, returns 0.

    The book-reader agent cites using printed page numbers (what readers
    see), but [PAGE N] markers in extracted text are 1-indexed PDF pages.
    The offset = (length of frontmatter before printed p.1). Typically 10-30.
    """
    from collections import Counter
    offsets: list[int] = []
    for pdf_p, body in pages.items():
        lines = [ln.strip() for ln in body.strip().split("\n")]
        if len(lines) < 2:
            continue
        candidates: list[int] = []
        # Bracketed banner ("[ 188 ]") can appear anywhere on the page —
        # scan all lines.
        for ln in lines:
            m = BANNER_PAGE_NUM_RE.match(ln)
            if m:
                candidates.append(int(m.group(1)))
        # Bare digit line — only top-3 / bottom-3 (otherwise too many false
        # positives from in-body numbers like equation refs).
        for ln in lines[:3] + lines[-3:]:
            m = BARE_PAGE_NUM_RE.match(ln)
            if m:
                candidates.append(int(m.group(1)))
        if not candidates:
            continue
        # Accept candidate only if offset is non-negative and < pdf_p
        # (printed page can't exceed PDF page index).
        for c in candidates:
            off = pdf_p - c
            if 0 <= off < pdf_p:
                offsets.append(off)

    if not offsets:
        return 0
    # Use mode; require at least 5 supporting samples to trust it
    mode_offset, count = Counter(offsets).most_common(1)[0]
    if count < 5:
        return 0
    return mode_offset


def build_offset_table(pages: dict[int, str]) -> dict[int, int]:
    """Build a per-PDF-page offset lookup table.

    Some PDFs have a gradually drifting offset (blank backs of chapter
    openers, full-page figures, etc.) rather than a fixed frontmatter
    offset. This function samples each page individually so callers can
    use a local offset instead of the global mode.

    Returns {pdf_page: offset}. Pages whose offset could not be detected
    are absent; callers should fall back to the global mode offset.
    """
    table: dict[int, int] = {}
    for pdf_p, body in pages.items():
        lines = [ln.strip() for ln in body.strip().split("\n")]
        if len(lines) < 2:
            continue
        candidates: list[int] = []
        for ln in lines:
            m = BANNER_PAGE_NUM_RE.match(ln)
            if m:
                candidates.append(int(m.group(1)))
        for ln in lines[:3] + lines[-3:]:
            m = BARE_PAGE_NUM_RE.match(ln)
            if m:
                candidates.append(int(m.group(1)))
        for c in candidates:
            off = pdf_p - c
            if 0 <= off < pdf_p:
                table[pdf_p] = off
                break  # first valid candidate per page
    return table


def local_offset(
    offset_table: dict[int, int],
    target_pdf_p: int,
    fallback: int,
) -> int:
    """Return the best offset for *target_pdf_p* using nearest-neighbour
    lookup in *offset_table*.  Falls back to *fallback* when the table is
    empty or the nearest neighbour is more than 30 pages away (unreliable).
    """
    if not offset_table:
        return fallback
    if target_pdf_p in offset_table:
        return offset_table[target_pdf_p]
    keys = sorted(offset_table)
    # Binary-search nearest key
    lo, hi = 0, len(keys) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if keys[mid] < target_pdf_p:
            lo = mid + 1
        else:
            hi = mid
    nearest_candidates = []
    if lo > 0:
        nearest_candidates.append(keys[lo - 1])
    if lo < len(keys):
        nearest_candidates.append(keys[lo])
    nearest = min(nearest_candidates, key=lambda k: abs(k - target_pdf_p))
    if abs(nearest - target_pdf_p) > 30:
        return fallback  # too far away to trust
    return offset_table[nearest]


def compute_n_chapters_effective(meta: dict, summary_md: str) -> int:
    """Effective upper bound for chapter numbers in citations.

    Why: ``meta["n_chapters"]`` is derived at PDF-extraction time from the TOC
    or regex heuristic (see ``scripts/extract_pdfs.py``). When that detector
    misses chapters — e.g. the fallback ``Chapter(index=1, title="Full Text")``
    for books without parseable markers (``math_money_mgmt``), or a TOC that
    only captures top-level Parts (``advances_fin_ml`` reports 10 parts while
    the book has ~22 chapters) — legitimate ``[ch.N]`` citations get rejected
    as ``chapter N > n_chapters``.

    Fix: take the max of three signals:
      1. ``meta["n_chapters"]`` (the declared count).
      2. ``declared_max + 1`` from ``chapter_index`` (handles non-contiguous
         parsing like Hamilton ``[0,5,9,10,20,22]`` — 6 indices but max=22).
      3. Max ``ch.N`` actually cited in the summary — the summary author read
         the book; if they wrote ``[ch.20]`` the book has ≥20 chapters.

    Scan (3) only covers citations outside the Metadata section (bibliographic
    ``ch.N`` in Metadata is not trustworthy), mirroring ``extract_citations``.
    """
    ch_idx = meta.get("chapter_index") or []
    declared_max = max((c.get("index", 0) for c in ch_idx), default=0)
    max_cited_ch = 0
    for _line, m in extract_citations(summary_md):
        ch, _p1, _p2 = _coalesce_citation(m)
        if ch is not None:
            max_cited_ch = max(max_cited_ch, int(ch))
    return max(meta.get("n_chapters", 0), declared_max + 1, max_cited_ch)


def extract_citations(summary_md: str) -> list[tuple[str, re.Match]]:
    """Return [(assertion_line, match), ...] pairs — one per citation.
    Skips the Metadata section (citations there are bibliographic, not factual).
    """
    # Find Metadata section boundaries (## Metadata ... next ## header)
    meta_match = re.search(
        r"^##\s+Metadata\s*$", summary_md, re.MULTILINE | re.IGNORECASE
    )
    meta_span: tuple[int, int] | None = None
    if meta_match:
        next_h2 = re.search(
            r"^##\s+", summary_md[meta_match.end():], re.MULTILINE
        )
        end = meta_match.end() + (next_h2.start() if next_h2 else len(summary_md))
        meta_span = (meta_match.start(), end)

    out: list[tuple[str, re.Match]] = []
    for m in CITATION_RE.finditer(summary_md):
        _ch, _p1, _p2 = _coalesce_citation(m)
        if not (_ch or _p1):
            continue
        if meta_span and meta_span[0] <= m.start() < meta_span[1]:
            continue  # skip bibliographic citations in Metadata section
        line_start = summary_md.rfind("\n", 0, m.start()) + 1
        line_end = summary_md.find("\n", m.end())
        if line_end == -1:
            line_end = len(summary_md)
        line = summary_md[line_start:line_end].strip()
        out.append((line, m))
    return out


def check_one(
    line: str,
    m: re.Match,
    pages: dict[int, str],
    n_pages: int,
    n_chapters: int,
    page_tolerance: int = 1,
    offset: int = 0,
    offset_table: dict[int, int] | None = None,
    canonical: dict | None = None,
) -> CitationCheck:
    raw = m.group(0)
    ch_raw, p1_raw, p2_raw = _coalesce_citation(m)

    chk = CitationCheck(
        assertion=line[:200],
        raw=raw,
        ch=int(ch_raw) if ch_raw else None,
    )

    # Soft: [p.?] — accepted, flagged separately
    if p1_raw == "?":
        chk.soft = True
        chk.verdict = "warn"
        chk.reason = "soft [p.?] — unknown page"
        return chk

    if p1_raw:
        chk.p_start = int(p1_raw)
        chk.p_end = int(p2_raw) if p2_raw else chk.p_start

    # Validate chapter index if present
    if chk.ch is not None and chk.ch > n_chapters:
        chk.verdict = "fail"
        chk.reason = f"chapter {chk.ch} > n_chapters ({n_chapters})"
        return chk

    # If only [ch.X] with no page, we can't do page-level checks
    if chk.p_start is None:
        chk.verdict = "ok"
        chk.reason = "chapter-only ref"
        return chk

    # Resolve printed→PDF pages. The book-reader cites printed page numbers;
    # [PAGE N] markers are PDF page indices.
    #
    # Canonical path: _page_index.json.printed_to_pdf is authoritative.
    if canonical is not None:
        pdf_start = resolve_printed_to_pdf(slug="", printed=chk.p_start, canonical=canonical)
        pdf_end = resolve_printed_to_pdf(slug="", printed=chk.p_end, canonical=canonical)
        if pdf_start is None or pdf_end is None:
            chk.verdict = "fail"
            chk.reason = (
                f"printed page {chk.p_start}-{chk.p_end} not resolvable "
                "via canonical _page_index.json (unmapped)"
            )
            return chk
    else:
        # Legacy heuristic path. Use a local offset when available: some PDFs
        # have a gradually drifting offset (blank chapter-opener backs,
        # full-page figures) so the global mode can be wrong by several pages
        # near the extremes.  We approximate the target PDF page with the
        # global offset first, then refine.
        approx_pdf = chk.p_start + offset
        # Only apply local-offset refinement when a reliable global offset was
        # detected (offset > 0).  For PDFs where printed == PDF page (offset=0)
        # the offset_table contains noise (random bare-digit lines) that would
        # produce false-positive mis-citations.
        effective_offset = (
            local_offset(offset_table, approx_pdf, offset)
            if offset_table is not None and offset > 0
            else offset
        )
        pdf_start = chk.p_start + effective_offset
        pdf_end = chk.p_end + effective_offset

    # Validate page range (check the resolved PDF pages)
    if pdf_start < 1 or pdf_end > n_pages:
        # Legacy heuristic may need frontmatter fallback; canonical map is
        # authoritative so a printed page outside [1,n_pages] after canonical
        # resolution is a legitimate fail.
        if canonical is None and chk.p_start >= 1 and chk.p_end <= n_pages:
            pdf_start, pdf_end = chk.p_start, chk.p_end
        else:
            chk.verdict = "fail"
            chk.reason = (
                f"page {chk.p_start}-{chk.p_end} (→PDF {pdf_start}-{pdf_end}) "
                f"out of range [1, {n_pages}]"
            )
            return chk

    # Validate every cited page has a [PAGE N] marker in the extracted text
    missing = [p for p in range(pdf_start, pdf_end + 1) if p not in pages]
    if missing:
        chk.verdict = "fail"
        chk.reason = f"pages {missing} (PDF) have no [PAGE N] marker in extracted text"
        return chk

    # Key-token overlap: strip the citation, extract tokens, compare to page text.
    # Assertion is PT (summary) → expand with EN equivalents; window is the
    # source text (usually EN) — don't expand.
    assertion_text = CITATION_RE.sub("", line)
    assertion_tokens = _tokens(assertion_text, expand_pt=True)

    if not assertion_tokens:
        # Short line (e.g., formula label) — nothing to compare, accept
        chk.verdict = "ok"
        chk.reason = "no content tokens to match (short assertion)"
        return chk

    # Build the "allowed" page window with tolerance
    windows = []
    for p in range(pdf_start, pdf_end + 1):
        for q in range(p - page_tolerance, p + page_tolerance + 1):
            if q in pages:
                windows.append(pages[q])
    window_text = "\n".join(windows)
    window_tokens = _tokens(window_text)

    overlap = assertion_tokens & window_tokens
    # Accept if at least 1 token OR >= 20% of assertion tokens appear in window
    ratio = len(overlap) / max(1, len(assertion_tokens))
    if overlap:
        # Chapter-intro softener: if ALL overlapping tokens appear only in
        # the first 5 non-empty lines (chapter heading) of the cited pages
        # and none in the body, downgrade verdict from "ok" to "warn". This
        # reduces false-positives in books where chapter titles echo cited
        # terms but the page body discusses tangential content.
        body_tokens: set[str] = set()
        heading_tokens_all: set[str] = set()
        for p in range(pdf_start, pdf_end + 1):
            body = pages.get(p, "")
            non_empty = [ln for ln in body.split("\n") if ln.strip()]
            heading_text = "\n".join(non_empty[:5])
            body_text = "\n".join(non_empty[5:])
            heading_tokens_all |= _tokens(heading_text)
            body_tokens |= _tokens(body_text)

        body_matches = overlap & body_tokens
        heading_matches = overlap & heading_tokens_all
        if not body_matches and heading_matches:
            chk.verdict = "warn"
            chk.reason = (
                f"chapter_intro — {len(overlap)} tokens match in chapter "
                f"heading of p.{chk.p_start}-{chk.p_end} only, not body"
            )
            return chk

        chk.verdict = "ok"
        chk.reason = (
            f"{len(overlap)}/{len(assertion_tokens)} tokens "
            f"({ratio:.0%}) in cited window"
        )
        return chk

    # No immediate overlap — wide search (±30 pages) to record where the
    # assertion tokens actually cluster. Enables systemic offset detection.
    wide_match_page: int | None = None
    best_overlap_count = 0
    for q in range(max(1, pdf_start - 30), min(n_pages, pdf_end + 30) + 1):
        if q in pages:
            q_tokens = _tokens(pages[q])
            q_overlap = len(assertion_tokens & q_tokens)
            if q_overlap > best_overlap_count:
                best_overlap_count = q_overlap
                wide_match_page = q
    if wide_match_page is not None and best_overlap_count >= 2:
        chk.actual_pdf_page = wide_match_page

    chk.verdict = "fail"
    chk.reason = (
        f"0/{len(assertion_tokens)} assertion tokens found in printed "
        f"pages {chk.p_start}-{chk.p_end} (PDF {pdf_start}-{pdf_end}, "
        f"±{page_tolerance}) — possible mis-citation. "
        f"Tokens looked for: {sorted(assertion_tokens)[:8]}"
    )
    return chk


def check_summary(
    slug: str,
    page_tolerance: int = 1,
    max_soft: int | None = None,
) -> Report:
    summary_path = SUMMARIES_DIR / f"{slug}.md"
    if not summary_path.exists():
        raise FileNotFoundError(f"summary not found: {summary_path}")

    meta = load_metadata(slug)
    pages = load_page_index(slug, meta)
    md = summary_path.read_text(encoding="utf-8")

    # Prefer canonical map from _page_index.json (Tier 2 deterministic).
    # Fall back to heuristic detection only for legacy books without it.
    canonical = load_canonical_offset_map(slug)
    if canonical is not None:
        offset = canonical.get("global_mode_offset") or 0
        off_table = None  # canonical mapping replaces the per-page table
    else:
        offset = detect_printed_pdf_offset(pages)
        off_table = build_offset_table(pages)

    n_chapters_effective = compute_n_chapters_effective(meta, md)

    rep = Report(slug=slug)
    rep.offset = offset
    for line, m in extract_citations(md):
        chk = check_one(
            line, m, pages,
            n_pages=meta["n_pages"],
            n_chapters=n_chapters_effective,
            page_tolerance=page_tolerance,
            offset=offset,
            offset_table=off_table,
            canonical=canonical,
        )
        rep.n_total += 1
        if chk.verdict == "ok":
            rep.n_ok += 1
        elif chk.verdict == "fail":
            rep.n_fail += 1
            rep.failures.append(chk)
        elif chk.verdict == "warn":
            rep.n_warn += 1
            if chk.soft:
                rep.n_soft += 1
                rep.soft_refs.append(chk)
            else:
                rep.warnings.append(chk)

    # Systemic offset detection: re-frame bulk failures as 1 root cause
    if rep.n_fail >= 5:
        finding = detect_systemic_offset(rep.failures)
        if finding.detected:
            rep.systemic_offset_detected = True
            rep.systemic_offset_value = finding.offset
            rep.systemic_offset_coverage = finding.coverage
            rep.systemic_offset_n_explained = finding.n_failures_explained

    if max_soft is not None and rep.n_soft > max_soft:
        # Promote to failure: too many soft [p.?] is abuse
        fake = CitationCheck(
            assertion=f"(meta) {rep.n_soft} soft [p.?] citations exceed max_soft={max_soft}",
            raw="[p.?]×N",
            verdict="fail",
            reason=f"too many soft citations: {rep.n_soft} > {max_soft}",
        )
        rep.n_fail += 1
        rep.failures.append(fake)
    return rep


def print_report(rep: Report) -> None:
    color = "green" if rep.ok else "red"
    label = "PASS" if rep.ok else "FAIL"
    console.print(f"[{color}]{label}[/{color}]  [bold]{rep.slug}[/bold]  (citation-check)")
    console.print(
        f"  printed→PDF offset={rep.offset}  total={rep.n_total}  ok={rep.n_ok}  "
        f"fail={rep.n_fail}  warn={rep.n_warn}  soft[p.?]={rep.n_soft}"
    )
    if rep.systemic_offset_detected:
        console.print(
            f"[bold yellow]⚠ SYSTEMIC_OFFSET detected[/bold yellow] "
            f"offset={rep.systemic_offset_value:+d} "
            f"coverage={rep.systemic_offset_coverage:.0%} "
            f"({rep.systemic_offset_n_explained}/{rep.n_fail} failures explained). "
            f"Root cause: book-reader emitted wrong page numbers; "
            f"suggest re-running self-audit or patch-offset."
        )
    if rep.failures:
        from rich.markup import escape
        console.print("[bold red]Failures:[/bold red]")
        for f in rep.failures:
            console.print(
                f"  [cyan]{escape(f.raw)}[/cyan] — [red]{escape(f.reason)}[/red]"
            )
            console.print(f"    ↳ {escape(f.assertion)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Summary slug to check")
    parser.add_argument("--json", action="store_true", help="Emit JSON report on stdout")
    parser.add_argument(
        "--tolerance", type=int, default=1,
        help="Page window tolerance for token overlap (default 1)",
    )
    parser.add_argument(
        "--max-soft", type=int, default=None,
        help="Fail if more than N [p.?] soft citations (default: unlimited)",
    )
    args = parser.parse_args()

    try:
        rep = check_summary(args.slug, args.tolerance, args.max_soft)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        return 2

    if args.json:
        out = {
            "slug": rep.slug,
            "ok": rep.ok,
            "n_total": rep.n_total,
            "n_ok": rep.n_ok,
            "n_fail": rep.n_fail,
            "n_warn": rep.n_warn,
            "n_soft": rep.n_soft,
            "failures": [asdict(f) for f in rep.failures],
            "warnings": [asdict(w) for w in rep.warnings],
            "systemic_offset": {
                "detected": rep.systemic_offset_detected,
                "value": rep.systemic_offset_value,
                "coverage": rep.systemic_offset_coverage,
                "n_explained": rep.systemic_offset_n_explained,
            },
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print_report(rep)

    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
