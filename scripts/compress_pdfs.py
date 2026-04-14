"""
compress_pdfs.py — shrink books/raw/*.pdf without changing what extract_pdfs.py sees.

Strategy
--------
Ghostscript `pdfwrite` with image downsampling. Text layer is preserved; only
raster images (typically OCR scan pages at 300–600 dpi) are recompressed down
to 200 dpi color/gray / 300 dpi mono.

Safety
------
Every candidate is verified BEFORE the original is replaced:

  1. Extract pages of the original via pymupdf.
  2. Compress to a temp file via ghostscript.
  3. Extract pages of the compressed file.
  4. Reject unless:
       - page count matches exactly, and
       - each page's word sequence matches (whitespace-normalized).
  5. On success, original is moved to books/raw/.backup/<slug>.pdf and the
     compressed file takes its place. On failure, the original is untouched.

No LLM calls. Deterministic.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import fitz  # pymupdf
from rich.console import Console
from rich.table import Table

# Reuse the extractor's page reader so verification matches the pipeline exactly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_pdfs import extract_pages_and_toc  # noqa: E402

console = Console()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "books" / "raw"
BACKUP_DIR = RAW_DIR / ".backup"
STAGING_DIR = RAW_DIR / ".compressed"

# Any file smaller than this is skipped by default (gains rarely worth the risk).
DEFAULT_MIN_SIZE_MB = 3.0

# Only accept the compressed result if it's at most this fraction of the original.
# Above this, savings are too small to justify replacement.
MAX_ACCEPTABLE_RATIO = 0.95

# Ghostscript image resolution targets (dpi).
COLOR_DPI = 200
GRAY_DPI = 200
MONO_DPI = 300


@dataclass
class Result:
    slug: str
    original_bytes: int
    compressed_bytes: int | None
    status: str  # "ok" | "skipped" | "too-small-saving" | "verify-failed" | "gs-error"
    detail: str = ""

    @property
    def ratio(self) -> float:
        if not self.compressed_bytes:
            return 1.0
        return self.compressed_bytes / self.original_bytes


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def run_ghostscript(src: Path, dst: Path) -> tuple[bool, str]:
    """Invoke ghostscript. Returns (ok, stderr_tail)."""
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        "-dPDFSETTINGS=/ebook",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dDownsampleColorImages=true",
        f"-dColorImageResolution={COLOR_DPI}",
        "-dDownsampleGrayImages=true",
        f"-dGrayImageResolution={GRAY_DPI}",
        "-dDownsampleMonoImages=true",
        f"-dMonoImageResolution={MONO_DPI}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={dst}",
        str(src),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not dst.exists() or dst.stat().st_size == 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
        return False, "\n".join(tail)
    return True, ""


def page_signature(text: str) -> tuple[str, ...]:
    """Whitespace-normalized word tuple. Tolerant to reflowed text streams,
    strict about content."""
    return tuple(text.split())


def verify_equivalence(original: Path, compressed: Path) -> tuple[bool, str]:
    """Both files must produce the same page count and the same word sequence
    per page when read by pymupdf."""
    orig_pages, _ = extract_pages_and_toc(original)
    comp_pages, _ = extract_pages_and_toc(compressed)

    if len(orig_pages) != len(comp_pages):
        return False, f"page count mismatch: {len(orig_pages)} vs {len(comp_pages)}"

    mismatched: list[int] = []
    for i, (a, b) in enumerate(zip(orig_pages, comp_pages), start=1):
        if page_signature(a) != page_signature(b):
            mismatched.append(i)

    if mismatched:
        sample = mismatched[:5]
        return False, (
            f"{len(mismatched)}/{len(orig_pages)} pages differ in word sequence "
            f"(first: {sample})"
        )
    return True, ""


def compress_one(pdf: Path, dry_run: bool, keep_backup: bool) -> Result:
    original_bytes = pdf.stat().st_size
    slug = pdf.stem

    STAGING_DIR.mkdir(exist_ok=True)
    staged = STAGING_DIR / pdf.name

    # Ghostscript → staging file
    with tempfile.TemporaryDirectory() as tmp:
        tmp_out = Path(tmp) / pdf.name
        ok, err = run_ghostscript(pdf, tmp_out)
        if not ok:
            return Result(slug, original_bytes, None, "gs-error", err[:500])

        compressed_bytes = tmp_out.stat().st_size

        if compressed_bytes >= original_bytes * MAX_ACCEPTABLE_RATIO:
            return Result(
                slug,
                original_bytes,
                compressed_bytes,
                "too-small-saving",
                f"{compressed_bytes / original_bytes:.1%} of original",
            )

        ok, reason = verify_equivalence(pdf, tmp_out)
        if not ok:
            return Result(slug, original_bytes, compressed_bytes, "verify-failed", reason)

        if dry_run:
            return Result(slug, original_bytes, compressed_bytes, "ok", "dry-run")

        # Commit: move compressed into place, back up the original.
        shutil.copy2(tmp_out, staged)

    BACKUP_DIR.mkdir(exist_ok=True)
    backup_path = BACKUP_DIR / pdf.name
    shutil.move(str(pdf), backup_path)
    shutil.move(str(staged), pdf)

    if not keep_backup:
        backup_path.unlink()

    return Result(slug, original_bytes, pdf.stat().st_size, "ok", "")


def summarize(results: list[Result]) -> int:
    table = Table(title="compression results")
    table.add_column("slug")
    table.add_column("status")
    table.add_column("before", justify="right")
    table.add_column("after", justify="right")
    table.add_column("ratio", justify="right")
    table.add_column("detail")

    before_total = 0
    after_total = 0
    any_fail = False

    for r in results:
        before_total += r.original_bytes
        after = r.compressed_bytes if r.status == "ok" else r.original_bytes
        after_total += after
        color = {
            "ok": "green",
            "skipped": "dim",
            "too-small-saving": "yellow",
            "verify-failed": "red",
            "gs-error": "red",
        }.get(r.status, "white")
        if r.status in ("verify-failed", "gs-error"):
            any_fail = True
        table.add_row(
            r.slug,
            f"[{color}]{r.status}[/{color}]",
            human_size(r.original_bytes),
            human_size(r.compressed_bytes) if r.compressed_bytes else "—",
            f"{r.ratio:.1%}",
            r.detail,
        )

    console.print(table)
    saved = before_total - after_total
    console.print(
        f"[bold]Total:[/bold] {human_size(before_total)} → "
        f"{human_size(after_total)} (saved {human_size(saved)}, "
        f"{(saved / before_total * 100 if before_total else 0):.1f}%)"
    )
    return 2 if any_fail else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", help="Compress only this slug (e.g., evidence_based_ta).")
    parser.add_argument(
        "--min-size-mb",
        type=float,
        default=DEFAULT_MIN_SIZE_MB,
        help=f"Skip files below this size. Default {DEFAULT_MIN_SIZE_MB} MB.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compress to a temp file and report savings, but do not replace originals.",
    )
    parser.add_argument(
        "--keep-backup",
        action="store_true",
        help="Keep books/raw/.backup/<slug>.pdf after successful replacement.",
    )
    args = parser.parse_args()

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

    min_bytes = int(args.min_size_mb * 1024 * 1024)
    results: list[Result] = []

    for pdf in targets:
        size = pdf.stat().st_size
        if args.slug is None and size < min_bytes:
            results.append(
                Result(pdf.stem, size, None, "skipped", f"< {args.min_size_mb}MB")
            )
            console.print(f"[dim]skip[/dim]   {pdf.stem} ({human_size(size)})")
            continue

        console.print(f"[bold]work[/bold]   {pdf.stem} ({human_size(size)})")
        try:
            r = compress_one(pdf, dry_run=args.dry_run, keep_backup=args.keep_backup)
        except Exception as e:  # pragma: no cover
            r = Result(pdf.stem, size, None, "gs-error", f"exception: {e!r}")
        results.append(r)
        if r.status == "ok":
            console.print(
                f"  [green]ok[/green]   {human_size(r.original_bytes)} → "
                f"{human_size(r.compressed_bytes or 0)} ({r.ratio:.1%})"
            )
        elif r.status == "too-small-saving":
            console.print(f"  [yellow]keep[/yellow] {r.detail}")
        else:
            console.print(f"  [red]{r.status}[/red] {r.detail}")

    # Clean up staging dir (safe to remove; contents were moved on success).
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR, ignore_errors=True)

    return summarize(results)


if __name__ == "__main__":
    sys.exit(main())
