"""
extract_pdfs.py — PDF → text (pymupdf primary, pdfplumber fallback for tables).

For each PDF in books/raw/, produces:
  books/extracted/<slug>/
    ├── _full.txt           (entire book, concatenated, with [PAGE N] markers)
    ├── _metadata.json      (n_pages, est_tokens, n_chapters, is_scanned, mode)
    └── chapters/
        ├── 00_frontmatter.txt
        ├── 01_<detected_title>.txt
        └── ...

Sanity checks:
- ScannedPDFError raised if >20% of pages have <100 words (likely OCR-less scan).
- Recommended mode ("single_pass" | "map_reduce") set based on estimated tokens.

No LLM calls. Deterministic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import fitz  # pymupdf
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "books" / "raw"
EXTRACTED_DIR = ROOT / "books" / "extracted"

# Heuristic thresholds
MIN_WORDS_PER_PAGE = 100       # below this → page considered "sparse" (possibly scan)
# Different sparse-ratio thresholds depending on whether the PDF has an outline:
#   - No TOC: anything above SCANNED_NOTOC_RATIO is likely a scan without text.
#   - With TOC: we tolerate far more sparse pages (figures, tables, diagrams).
SCANNED_NOTOC_RATIO = 0.40     # PDF w/o TOC: >40% sparse → scanned
SCANNED_WITHTOC_RATIO = 0.80   # PDF w/ TOC:  >80% sparse → scanned (almost certain)
INCOMPLETE_MIN_PAGES = 50      # below this + no TOC → likely front matter / preview
CHAR_PER_TOKEN = 4             # rough token estimator (1 token ≈ 4 chars in English)
MAP_REDUCE_THRESHOLD = 400_000  # tokens; above this, book-reader uses map-reduce

# Chapter detection regexes (tried in order; first match wins per book)
CHAPTER_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "Chapter 1", "CHAPTER 12", optionally followed by colon/dash and title
    re.compile(r"^\s*Chapter\s+(\d{1,3})\b[.:\s\-–]*(.{0,120})$", re.IGNORECASE | re.MULTILINE),
    # "1. Introduction", "12. Something" at line start
    re.compile(r"^\s*(\d{1,3})\.\s+([A-Z][A-Za-z0-9 ,:\-–]{3,120})\s*$", re.MULTILINE),
    # "PART I", "PART 1", "SECTION 3"
    re.compile(r"^\s*(?:Part|PART|Section|SECTION)\s+([IVXLC\d]+)\b[.:\s\-–]*(.{0,120})$", re.MULTILINE),
)


class ScannedPDFError(RuntimeError):
    """Raised when a PDF appears to be a scan without an OCR text layer."""


class IncompleteBookError(RuntimeError):
    """Raised when a PDF is too short + has no outline — likely front matter / preview."""


@dataclass
class Chapter:
    index: int
    title: str
    start_page: int     # 1-based
    end_page: int       # 1-based, inclusive
    text: str = ""


@dataclass
class BookMetadata:
    slug: str
    source_filename: str
    n_pages: int
    n_chapters: int
    est_tokens: int
    is_scanned: bool
    sparse_pages: list[int] = field(default_factory=list)
    sparse_ratio: float = 0.0
    recommended_mode: str = "single_pass"  # or "map_reduce"
    chapter_index: list[dict] = field(default_factory=list)  # [{index, title, start, end}]


def estimate_tokens(text: str) -> int:
    return len(text) // CHAR_PER_TOKEN


def extract_pages_and_toc(pdf_path: Path) -> tuple[list[str], list[tuple[int, str, int]]]:
    """Return (pages, toc). toc is a list of (level, title, page_1based) from the
    PDF outline/bookmarks (empty list if the PDF has no outline)."""
    pages: list[str] = []
    toc: list[tuple[int, str, int]] = []
    with fitz.open(pdf_path) as doc:
        raw_toc = doc.get_toc()
        # pymupdf returns [[level, title, page1based], ...] with level >= 1
        toc = [(lvl, (title or "").strip(), page) for lvl, title, page in raw_toc if page >= 1]
        for page in doc:
            pages.append(page.get_text("text") or "")
    return pages, toc


def check_quality(
    pages: list[str], toc: list[tuple[int, str, int]]
) -> tuple[bool, bool, list[int], float]:
    """Return (is_scanned, is_incomplete, sparse_page_numbers_1based, sparse_ratio).

    - is_scanned: PDF likely lacks text layer (heavily OCR-less).
      threshold depends on presence of TOC (figures-heavy books with TOC need
      a higher bar).
    - is_incomplete: PDF is too short and has no TOC → probably front matter
      or a preview rather than a complete book.
    """
    sparse_pages: list[int] = []
    for i, text in enumerate(pages, start=1):
        wc = len(text.split())
        if wc < MIN_WORDS_PER_PAGE:
            sparse_pages.append(i)
    ratio = len(sparse_pages) / len(pages) if pages else 0.0
    has_toc = bool(toc)
    if has_toc:
        is_scanned = ratio > SCANNED_WITHTOC_RATIO
    else:
        is_scanned = ratio > SCANNED_NOTOC_RATIO
    is_incomplete = (not has_toc) and len(pages) < INCOMPLETE_MIN_PAGES
    return is_scanned, is_incomplete, sparse_pages, ratio


def detect_chapters(
    pages: list[str],
    toc: list[tuple[int, str, int]],
    override_path: Path | None = None,
) -> list[Chapter]:
    """Detect chapter boundaries. Resolution order:
    1. `_chapter_overrides.json` next to the PDF (manually curated; wins over TOC).
    2. PDF outline/bookmarks (most accurate when present).
    3. Regex heuristics (books without outline).
    4. Single-chapter fallback (whole book).

    Returns chapters sorted by start_page ascending.
    """
    chapters: list[Chapter] = []
    if override_path and override_path.exists():
        chapters = _chapters_from_overrides(pages, override_path)
    if not chapters and toc:
        chapters = _chapters_from_toc(pages, toc)
    if not chapters:
        chapters = _chapters_from_regex(pages)
    if not chapters:
        full = "\n".join(f"[PAGE {i + 1}]\n{t}" for i, t in enumerate(pages))
        return [
            Chapter(index=1, title="Full Text", start_page=1, end_page=len(pages), text=full)
        ]
    return chapters


def _chapters_from_overrides(pages: list[str], override_path: Path) -> list[Chapter]:
    """Build chapters from a manually curated `_chapter_overrides.json`.

    Schema:
        {"chapters": [{"index": int, "title": str, "start_page": int}, ...]}

    `start_page` is the 1-based PDF page where the chapter begins. End pages
    are derived automatically (next chapter start - 1; last chapter ends at
    the last page). A synthetic Frontmatter entry covers pages before the
    first listed chapter.
    """
    data = json.loads(override_path.read_text(encoding="utf-8"))
    entries = sorted(data["chapters"], key=lambda e: e["start_page"])
    if not entries:
        return []

    chapters: list[Chapter] = []
    first_page = entries[0]["start_page"]
    if first_page > 1:
        fm_parts = [_page_text_with_marker(pages, p) for p in range(1, first_page)]
        fm_text = "\n".join(filter(None, fm_parts)).strip()
        if fm_text:
            chapters.append(
                Chapter(
                    index=0,
                    title="Frontmatter",
                    start_page=1,
                    end_page=first_page - 1,
                    text=fm_text,
                )
            )

    for i, entry in enumerate(entries):
        start = entry["start_page"]
        end = entries[i + 1]["start_page"] - 1 if i + 1 < len(entries) else len(pages)
        if end < start:
            end = start
        text_parts = [_page_text_with_marker(pages, p) for p in range(start, end + 1)]
        text = "\n".join(filter(None, text_parts)).strip()
        chapters.append(
            Chapter(
                index=entry["index"],
                title=entry["title"],
                start_page=start,
                end_page=end,
                text=text,
            )
        )
    return chapters


def _page_text_with_marker(pages: list[str], page_1based: int) -> str:
    if 1 <= page_1based <= len(pages):
        return f"[PAGE {page_1based}]\n{pages[page_1based - 1]}"
    return ""


def _chapters_from_toc(
    pages: list[str], toc: list[tuple[int, str, int]]
) -> list[Chapter]:
    """Build chapters from the PDF's outline/bookmarks.

    Heuristic: use top-level entries (level 1) as chapter boundaries. If that
    produces too few or too many sections, try the most common level.

    Rejects TOCs whose titles look auto-generated (e.g., 'evi0001', 'ev0515')
    — those produce garbage chapter boundaries and should fall through to the
    regex fallback.
    """
    if not toc:
        return []

    # Detect garbage TOCs: titles that look like auto-generated IDs.
    garbage_id_pattern = re.compile(r"^[a-z]{1,4}\d{2,6}$", re.IGNORECASE)
    garbage_count = sum(1 for _, title, _ in toc if garbage_id_pattern.match(title or ""))
    if garbage_count > len(toc) * 0.5:
        return []  # > 50% of titles look auto-generated → TOC is useless

    # Count entries per level
    level_counts: dict[int, int] = {}
    for lvl, _, _ in toc:
        level_counts[lvl] = level_counts.get(lvl, 0) + 1

    # Pick a level that produces a reasonable number of chapters (5..80)
    candidate_levels = sorted(level_counts.keys())
    chosen_level: int | None = None
    for lvl in candidate_levels:
        if 5 <= level_counts[lvl] <= 80:
            chosen_level = lvl
            break
    if chosen_level is None:
        # If the shallowest level has too many entries (>100), TOC is too fine-grained
        # to be useful as chapter boundaries — let regex fallback handle it.
        shallowest = min(candidate_levels)
        if level_counts[shallowest] > 100:
            return []
        chosen_level = shallowest

    entries = [(title, page) for lvl, title, page in toc if lvl == chosen_level]
    if not entries:
        return []

    # De-duplicate by page (some TOCs repeat the same page for "Title"+"Part I" etc.)
    seen_pages: set[int] = set()
    dedup: list[tuple[str, int]] = []
    for title, page in entries:
        if page in seen_pages:
            continue
        seen_pages.add(page)
        dedup.append((title, page))

    dedup.sort(key=lambda tp: tp[1])
    chapters: list[Chapter] = []

    # Optional frontmatter (content before first TOC entry)
    first_page = dedup[0][1]
    if first_page > 1:
        fm_text_parts = [_page_text_with_marker(pages, p) for p in range(1, first_page)]
        fm_text = "\n".join(filter(None, fm_text_parts)).strip()
        if fm_text:
            chapters.append(
                Chapter(
                    index=0,
                    title="Frontmatter",
                    start_page=1,
                    end_page=first_page - 1,
                    text=fm_text,
                )
            )

    for i, (title, start_page) in enumerate(dedup):
        end_page = dedup[i + 1][1] - 1 if i + 1 < len(dedup) else len(pages)
        if end_page < start_page:
            end_page = start_page
        text_parts = [
            _page_text_with_marker(pages, p) for p in range(start_page, end_page + 1)
        ]
        text = "\n".join(filter(None, text_parts)).strip()
        chapters.append(
            Chapter(
                index=i + 1,
                title=title or f"Section {i + 1}",
                start_page=start_page,
                end_page=end_page,
                text=text,
            )
        )
    return chapters


def _chapters_from_regex(pages: list[str]) -> list[Chapter]:
    """Fallback: regex-based detection for PDFs without an outline.

    This is intentionally conservative:
    - Only matches near the start of a page (first 10 lines) or at the start
      of text after significant whitespace.
    - Rejects chapter numbers that skip backwards (detects false positives
      like "1. Introduction" inside a bullet list).
    - Requires headings to be followed by a reasonable title.
    """
    cursor = 0
    page_starts: list[int] = []
    joined_parts: list[str] = []
    for i, text in enumerate(pages):
        page_starts.append(cursor)
        chunk = f"\n[PAGE {i + 1}]\n{text}\n"
        joined_parts.append(chunk)
        cursor += len(chunk)
    joined = "".join(joined_parts)

    # Only match "Chapter N" patterns — the safest signal. We skip the "1. Title"
    # patterns entirely in fallback because they caused false positives.
    pattern = re.compile(
        r"\[PAGE\s+\d+\]\s*\n\s*Chapter\s+(\d{1,3})\b[.:\s\-–]*(.{0,120})$",
        re.IGNORECASE | re.MULTILINE,
    )

    matches: list[tuple[int, int, str]] = []
    for m in pattern.finditer(joined):
        try:
            num = int(m.group(1))
        except ValueError:
            continue
        title_raw = (m.group(2) or "").strip()
        title = re.sub(r"\s+", " ", title_raw).strip(" .:-–")
        matches.append((m.start(), num, title))

    # Reject regressions (chapter number must be non-decreasing)
    matches.sort(key=lambda t: t[0])
    filtered: list[tuple[int, int, str]] = []
    last_num = 0
    for off, num, title in matches:
        if num < last_num:
            continue
        filtered.append((off, num, title))
        last_num = num

    if not filtered:
        return []

    def offset_to_page(offset: int) -> int:
        page = 1
        for p, ps in enumerate(page_starts, start=1):
            if ps <= offset:
                page = p
            else:
                break
        return page

    chapters: list[Chapter] = []
    first_off = filtered[0][0]
    if first_off > 500:
        fm_text = joined[:first_off].strip()
        chapters.append(
            Chapter(
                index=0,
                title="Frontmatter",
                start_page=1,
                end_page=max(offset_to_page(first_off) - 1, 1),
                text=fm_text,
            )
        )

    for i, (off, num, title) in enumerate(filtered):
        next_off = filtered[i + 1][0] if i + 1 < len(filtered) else len(joined)
        text = joined[off:next_off].strip()
        chapters.append(
            Chapter(
                index=num,
                title=title or f"Chapter {num}",
                start_page=offset_to_page(off),
                end_page=offset_to_page(next_off - 1),
                text=text,
            )
        )
    return chapters


_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_to_int(s: str) -> int:
    s = s.upper()
    if not s or any(ch not in _ROMAN for ch in s):
        raise ValueError(f"not a roman numeral: {s!r}")
    total = 0
    prev = 0
    for ch in reversed(s):
        v = _ROMAN[ch]
        total += v if v >= prev else -v
        prev = v
    return total


def _sanitize(s: str, max_len: int = 60) -> str:
    s = re.sub(r"[^\w\s\-]+", "", s).strip().replace(" ", "_").lower()
    return s[:max_len] or "untitled"


def write_extraction(
    slug: str,
    source_filename: str,
    pages: list[str],
    chapters: list[Chapter],
    is_scanned: bool,
    sparse_pages: list[int],
    sparse_ratio: float,
) -> BookMetadata:
    out_dir = EXTRACTED_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir = out_dir / "chapters"
    if chapters_dir.exists():
        for old in chapters_dir.glob("*.txt"):
            old.unlink()
    chapters_dir.mkdir(exist_ok=True)

    # _full.txt: all pages with page markers (kept identical to what detect_chapters saw)
    full_parts: list[str] = []
    for i, text in enumerate(pages, start=1):
        full_parts.append(f"\n[PAGE {i}]\n{text.strip()}\n")
    full_text = "".join(full_parts)
    (out_dir / "_full.txt").write_text(full_text, encoding="utf-8")

    # Per-chapter files
    chapter_index: list[dict] = []
    for ch in chapters:
        safe_title = _sanitize(ch.title)
        filename = f"{ch.index:02d}_{safe_title}.txt"
        (chapters_dir / filename).write_text(ch.text, encoding="utf-8")
        chapter_index.append(
            {
                "index": ch.index,
                "title": ch.title,
                "start_page": ch.start_page,
                "end_page": ch.end_page,
                "file": f"chapters/{filename}",
                "est_tokens": estimate_tokens(ch.text),
            }
        )

    est_tokens = estimate_tokens(full_text)
    mode = "map_reduce" if est_tokens >= MAP_REDUCE_THRESHOLD else "single_pass"

    meta = BookMetadata(
        slug=slug,
        source_filename=source_filename,
        n_pages=len(pages),
        n_chapters=len(chapters),
        est_tokens=est_tokens,
        is_scanned=is_scanned,
        sparse_pages=sparse_pages,
        sparse_ratio=round(sparse_ratio, 3),
        recommended_mode=mode,
        chapter_index=chapter_index,
    )
    (out_dir / "_metadata.json").write_text(
        json.dumps(asdict(meta), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return meta


def extract_one(pdf_path: Path, skip_existing: bool) -> BookMetadata | None:
    slug = pdf_path.stem
    meta_path = EXTRACTED_DIR / slug / "_metadata.json"

    if skip_existing and meta_path.exists():
        console.print(f"[dim]skip[/dim]   {slug}: already extracted")
        return json.loads(meta_path.read_text(encoding="utf-8"))  # type: ignore[return-value]

    try:
        pages, toc = extract_pages_and_toc(pdf_path)
    except Exception as e:
        console.print(f"[red]ERROR[/red]  {slug}: pymupdf failed: {e}")
        return None

    if not pages:
        console.print(f"[red]ERROR[/red]  {slug}: no pages extracted")
        return None

    is_scanned, is_incomplete, sparse, ratio = check_quality(pages, toc)
    if is_incomplete:
        threshold = SCANNED_NOTOC_RATIO if not toc else SCANNED_WITHTOC_RATIO
        console.print(
            f"[red]INCOMPLETE BOOK DETECTED[/red]  {slug}: "
            f"only {len(pages)} pages and no TOC outline. "
            f"Likely a front matter / preview file, not the complete book."
        )
        raise IncompleteBookError(
            f"{slug}: {len(pages)} pages without TOC. "
            f"Replace PDF in books/raw/{slug}.pdf with the complete book and re-run."
        )
    if is_scanned:
        threshold = SCANNED_NOTOC_RATIO if not toc else SCANNED_WITHTOC_RATIO
        console.print(
            f"[red]SCANNED PDF DETECTED[/red]  {slug}: "
            f"{len(sparse)}/{len(pages)} pages are sparse ({ratio:.0%} > {threshold:.0%})."
        )
        sample = sparse[:20]
        console.print(f"  First sparse pages: {sample}{' ...' if len(sparse) > 20 else ''}")
        raise ScannedPDFError(
            f"{slug}: {len(sparse)} sparse pages (ratio={ratio:.0%}, no TOC={not toc}). "
            f"Replace PDF in books/raw/{slug}.pdf with an OCR'd version and re-run."
        )
    if ratio > 0.20 and toc:
        console.print(
            f"[yellow]NOTE[/yellow]   {slug}: {ratio:.0%} sparse pages (figures/tables "
            f"expected for technical books). Proceeding."
        )

    override_path = EXTRACTED_DIR / slug / "_chapter_overrides.json"
    chapters = detect_chapters(pages, toc, override_path=override_path)
    meta = write_extraction(slug, pdf_path.name, pages, chapters, is_scanned, sparse, ratio)
    if override_path.exists():
        source_label = "overrides"
    elif toc:
        source_label = "TOC"
    else:
        source_label = "regex-fallback"
    console.print(
        f"         [dim]└─ chapter source: {source_label}[/dim]",
        highlight=False,
    )
    console.print(
        f"[green]OK[/green]     {slug}: {meta.n_pages}pp, {meta.n_chapters}ch, "
        f"~{meta.est_tokens:,}tok, mode={meta.recommended_mode}"
    )
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", help="Process only this slug (e.g., systematic_trading).")
    parser.add_argument(
        "--force", action="store_true", help="Re-extract even if _metadata.json exists."
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing other books if one PDF is scanned/incomplete (default: abort).",
    )
    # Backwards-compat alias
    parser.add_argument(
        "--continue-on-scanned", action="store_true", help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    if args.continue_on_scanned:
        args.continue_on_error = True

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    if args.slug:
        targets = [RAW_DIR / f"{args.slug}.pdf"]
        if not targets[0].exists():
            console.print(f"[red]ERROR[/red]  PDF not found: {targets[0]}")
            return 1
    else:
        targets = sorted(RAW_DIR.glob("*.pdf"))

    if not targets:
        console.print(f"[yellow]WARN[/yellow]  no PDFs found in {RAW_DIR}")
        return 0

    scanned: list[str] = []
    incomplete: list[str] = []
    total_tokens = 0
    n_ok = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        t = progress.add_task("extracting", total=len(targets))
        for pdf_path in targets:
            try:
                meta = extract_one(pdf_path, skip_existing=not args.force)
                if meta:
                    n_ok += 1
                    total_tokens += meta["est_tokens"] if isinstance(meta, dict) else meta.est_tokens
            except ScannedPDFError:
                scanned.append(pdf_path.stem)
                if not args.continue_on_error:
                    progress.stop()
                    console.print(
                        "\n[red]Aborting.[/red] Replace the scanned PDF and re-run "
                        "(or pass --continue-on-error to skip and continue)."
                    )
                    return 2
            except IncompleteBookError:
                incomplete.append(pdf_path.stem)
                if not args.continue_on_error:
                    progress.stop()
                    console.print(
                        "\n[red]Aborting.[/red] Replace the incomplete PDF and re-run "
                        "(or pass --continue-on-error to skip and continue)."
                    )
                    return 2
            progress.update(t, advance=1)

    console.print(
        f"\n[bold]{n_ok}/{len(targets)}[/bold] extracted. "
        f"Total estimated tokens across corpus: {total_tokens:,}"
    )
    if scanned:
        console.print(
            f"[yellow]Scanned (skipped):[/yellow] {', '.join(scanned)}. "
            "Replace these PDFs with OCR'd versions and re-run."
        )
    if incomplete:
        console.print(
            f"[yellow]Incomplete (skipped):[/yellow] {', '.join(incomplete)}. "
            "These are likely front matter / preview files. Replace with complete books and re-run."
        )
    return 0 if not (scanned or incomplete) else 2


if __name__ == "__main__":
    sys.exit(main())
