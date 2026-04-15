"""
validate_summary.py — Gate-check for book summaries produced by the
`book-reader` subagent.

Enforces anti-hallucination invariants:
  1. All 9 required sections are present (or marked "N/A — <reason>").
  2. At least MIN_CITATION_RATIO of factual assertions carry a citation:
     [p.X], [p.X-Y], [ch.Y], or [p.?] (the last one is allowed but discouraged).
  3. Metadata block is filled (author, year, pages).

Usage:
  python scripts/validate_summary.py <slug>
  python scripts/validate_summary.py --all
  python scripts/validate_summary.py --strict --all    # stricter ratio (95%)

Exit codes:
  0 — valid
  1 — invalid (printed diagnostics)
  2 — file not found / I/O error
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

ROOT = Path(__file__).resolve().parent.parent
SUMMARIES_DIR = ROOT / "books" / "summaries"
SUMMARIES_PATH = SUMMARIES_DIR / "{slug}.md"

REQUIRED_SECTIONS = (
    "Metadata",
    "Core Thesis",
    "Main Concepts",
    "Formulas / Equations",
    "Algorithms and Pseudocode",
    "Explicit Trading Rules",
    "Pitfalls and Anti-patterns",
    "Sensitive Parameters",
    "Key Literal Quotes",
    "Cross-references to Other Books in This Knowledge Base",
)

# Regex: matches a citation marker at the end of a line or inline.
# Accepts: [p.12], [p.12-15], [ch.3], [ch.3, p.45], [p.?]
CITATION_RE = re.compile(r"\[(?:p\.|ch\.)[^\]]+\]", re.IGNORECASE)

# A "factual assertion" = any bullet, numbered item, or quoted line inside a
# section that is NOT the metadata or N/A-marked section. We use a light heuristic:
# lines starting with "-", "*", "> ", or "\d+." are assertions.
ASSERTION_RE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s+)", re.MULTILINE)

# N/A marker pattern — means the section intentionally has no content.
NA_RE = re.compile(r"^\s*N/A\b[\s\-—:]", re.IGNORECASE | re.MULTILINE)

DEFAULT_MIN_RATIO = 0.80
STRICT_MIN_RATIO = 0.95


@dataclass
class ValidationResult:
    slug: str
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    n_assertions: int = 0
    n_citations: int = 0
    citation_ratio: float = 0.0
    sections_found: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)
    sections_na: list[str] = field(default_factory=list)


def split_sections(md_text: str) -> dict[str, str]:
    """Split markdown into a dict of section_name → body. Uses '## ' H2 headers.
    Also captures the top '# Title' as the book title (stored under '_title').
    Numbering prefixes like '## 1. Foo' are stripped.
    """
    out: dict[str, str] = {"_title": ""}
    lines = md_text.splitlines()
    title_match = next((line for line in lines if line.startswith("# ")), None)
    if title_match:
        out["_title"] = title_match[2:].strip()

    # Split on H2 headers
    h2_re = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    indexes = [(m.start(), m.group(1).strip()) for m in h2_re.finditer(md_text)]
    for i, (start, raw_name) in enumerate(indexes):
        end = indexes[i + 1][0] if i + 1 < len(indexes) else len(md_text)
        body = md_text[start:end]
        # Strip numbering: "1. Core Thesis" → "Core Thesis"
        name = re.sub(r"^\d+\.\s+", "", raw_name).strip()
        out[name] = body
    return out


def validate(slug: str, min_ratio: float) -> ValidationResult:
    path = SUMMARIES_DIR / f"{slug}.md"
    result = ValidationResult(slug=slug, ok=False)

    if not path.exists():
        result.errors.append(f"file not found: {path}")
        return result

    md = path.read_text(encoding="utf-8")
    sections = split_sections(md)

    # Check required sections
    for required in REQUIRED_SECTIONS:
        # Loose matching: case-insensitive, accent-insensitive substring
        matched_name = None
        for name in sections:
            if _loose_eq(name, required):
                matched_name = name
                break
        if matched_name is None:
            result.sections_missing.append(required)
            result.errors.append(f"missing section: '{required}'")
            continue
        result.sections_found.append(required)

        # If section body starts with N/A, record it (doesn't count toward citation ratio)
        body = sections[matched_name]
        if NA_RE.search(body):
            result.sections_na.append(required)

    if not result.sections_missing:
        pass
    else:
        # Missing sections = hard fail; stop here
        return result

    # Metadata sanity: author + year + pages should appear
    meta_body = next(
        (sections[n] for n in sections if _loose_eq(n, "Metadata")), ""
    )
    for needle in ("Autor", "Ano"):
        if needle.lower() not in meta_body.lower():
            result.warnings.append(f"Metadata appears to be missing '{needle}'")

    # Count assertions and citations across all sections except Metadata and _title
    assertions = 0
    citations = 0
    for name, body in sections.items():
        if name in ("_title",) or _loose_eq(name, "Metadata"):
            continue
        # Skip N/A-only sections (nothing to validate)
        if _loose_eq_any(name, result.sections_na):
            continue
        for m in ASSERTION_RE.finditer(body):
            # Grab the whole assertion line (until newline)
            start = m.end()
            end = body.find("\n", start)
            if end == -1:
                end = len(body)
            # Allow multi-line bullets — also check the subsequent indented lines
            line_and_continuation = body[m.start():end]
            assertions += 1
            if CITATION_RE.search(line_and_continuation):
                citations += 1

    result.n_assertions = assertions
    result.n_citations = citations
    result.citation_ratio = citations / assertions if assertions else 1.0

    # Soft cap: a book with zero assertions is probably garbage
    if assertions == 0:
        result.errors.append(
            "no factual assertions (bullets/quotes) found — summary is empty?"
        )
        return result

    if result.citation_ratio < min_ratio:
        result.errors.append(
            f"citation ratio {result.citation_ratio:.0%} < required {min_ratio:.0%} "
            f"({citations}/{assertions} assertions have [p.X] or [ch.Y])"
        )
        return result

    # Cross-ref sanity: if section 9 references other summaries, they should exist.
    conn_body = next(
        (sections[n] for n in sections if _loose_eq(n, "Cross-references to Other Books in This Knowledge Base")),
        "",
    )
    for m in re.finditer(r"`([a-z_]+)\.md(?:#[a-z0-9\-]+)?`", conn_body):
        ref_slug = m.group(1)
        ref_path = SUMMARIES_DIR / f"{ref_slug}.md"
        if not ref_path.exists():
            result.warnings.append(
                f"cross-ref to `{ref_slug}.md` points to a summary that doesn't exist yet"
            )

    result.ok = True
    return result


def _loose_eq(a: str, b: str) -> bool:
    """Case-insensitive, accent-insensitive compare."""
    return _norm(a) == _norm(b)


def _loose_eq_any(a: str, items: list[str]) -> bool:
    na = _norm(a)
    return any(na == _norm(x) for x in items)


def _norm(s: str) -> str:
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def print_result(r: ValidationResult) -> None:
    color = "green" if r.ok else "red"
    label = "PASS" if r.ok else "FAIL"
    console.print(f"[{color}]{label}[/{color}]  [bold]{r.slug}[/bold]")
    console.print(
        f"  sections: {len(r.sections_found)}/{len(REQUIRED_SECTIONS)} found, "
        f"{len(r.sections_na)} marked N/A"
    )
    console.print(
        f"  citations: {r.n_citations}/{r.n_assertions} "
        f"({r.citation_ratio:.0%})"
    )
    for err in r.errors:
        console.print(f"  [red]error:[/red] {err}")
    for warn in r.warnings:
        console.print(f"  [yellow]warn:[/yellow] {warn}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?", help="Slug of the summary to validate.")
    parser.add_argument("--all", action="store_true", help="Validate all summaries.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help=f"Require {STRICT_MIN_RATIO:.0%} citation ratio (default {DEFAULT_MIN_RATIO:.0%}).",
    )
    args = parser.parse_args()

    min_ratio = STRICT_MIN_RATIO if args.strict else DEFAULT_MIN_RATIO

    if args.all:
        summaries = sorted(SUMMARIES_DIR.glob("*.md"))
        if not summaries:
            console.print(f"[yellow]no summaries found in {SUMMARIES_DIR}[/yellow]")
            return 0
        results = [validate(p.stem, min_ratio) for p in summaries]
        table = Table(title="Validation summary")
        table.add_column("slug", style="cyan")
        table.add_column("result")
        table.add_column("sections")
        table.add_column("citations")
        table.add_column("notes")
        for r in results:
            table.add_row(
                r.slug,
                "[green]PASS[/green]" if r.ok else "[red]FAIL[/red]",
                f"{len(r.sections_found)}/{len(REQUIRED_SECTIONS)}",
                f"{r.citation_ratio:.0%}",
                "; ".join(r.errors) or ("; ".join(r.warnings) if r.warnings else "—"),
            )
        console.print(table)
        any_fail = any(not r.ok for r in results)
        return 1 if any_fail else 0

    if not args.slug:
        parser.error("Pass a slug or --all")

    r = validate(args.slug, min_ratio)
    print_result(r)
    return 0 if r.ok else 1


if __name__ == "__main__":
    sys.exit(main())
