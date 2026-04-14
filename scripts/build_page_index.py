"""
build_page_index.py — Deterministic printed↔PDF page index for book-reader.

Generates books/extracted/<slug>/_page_index.json:
  - global_mode_offset:  most-frequent (pdf - printed) offset across the book
  - pdf_to_printed:      {pdf_page: printed_page}  — one entry per PDF page
                          detected directly or via nearest-neighbour interp.
  - printed_to_pdf:      reverse lookup (first PDF page per printed number)
  - unmapped_pdf_pages:  PDF pages where no reliable offset was found
                          (figures, blank pages, frontmatter — book-reader
                          should cite these as [p.?], never extrapolate).

Reuses detect_printed_pdf_offset/build_offset_table/local_offset from
check_citations.py so upstream (book-reader) and downstream (validator)
agree on page mapping by construction — no drift possible.

Usage:
  python scripts/build_page_index.py <slug>
  python scripts/build_page_index.py --all
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from check_citations import (
    EXTRACTED_DIR,
    build_offset_table,
    detect_printed_pdf_offset,
    load_metadata,
    load_page_index,
    local_offset,
)

NEAREST_MAX_DISTANCE = 30  # matches local_offset() fallback threshold
OUTLIER_WINDOW = 30        # ± pages used to compute local median offset
OUTLIER_MAX_DEVIATION = 4  # reject entries whose offset deviates more than this


def _filter_outliers(
    offset_table: dict[int, int],
) -> tuple[dict[int, int], list[int]]:
    """Discard offset_table entries whose offset deviates from the local
    median (over OUTLIER_WINDOW neighbours by sorted position) by more than
    OUTLIER_MAX_DEVIATION.

    Catches index-page noise (e.g., PDF p.814 of a book's alphabetical
    index happens to contain a line "199" — a sub-entry — which would
    otherwise be captured as printed page 199).
    """
    items = sorted(offset_table.items())  # [(pdf_p, offset), ...]
    offs = [o for _, o in items]
    filtered: dict[int, int] = {}
    outliers: list[int] = []
    for i, (pdf_p, off) in enumerate(items):
        lo = max(0, i - OUTLIER_WINDOW)
        hi = min(len(offs), i + OUTLIER_WINDOW + 1)
        neighbours = offs[lo:i] + offs[i + 1 : hi]
        if not neighbours:
            filtered[pdf_p] = off
            continue
        median = sorted(neighbours)[len(neighbours) // 2]
        if abs(off - median) > OUTLIER_MAX_DEVIATION:
            outliers.append(pdf_p)
        else:
            filtered[pdf_p] = off
    return filtered, outliers


def build_index(slug: str) -> dict:
    meta = load_metadata(slug)
    pages = load_page_index(slug, meta)
    if not pages:
        raise RuntimeError(f"no [PAGE N] markers found for {slug}")

    global_offset = detect_printed_pdf_offset(pages)
    raw_table = build_offset_table(pages)
    offset_table, outlier_detections = _filter_outliers(raw_table)

    pdf_to_printed: dict[int, int] = {}
    unmapped: list[int] = []

    pdf_pages_sorted = sorted(pages)
    table_keys = sorted(offset_table) if offset_table else []

    for pdf_p in pdf_pages_sorted:
        if pdf_p in offset_table:
            off = offset_table[pdf_p]
        elif table_keys:
            nearest = min(table_keys, key=lambda k: abs(k - pdf_p))
            if abs(nearest - pdf_p) > NEAREST_MAX_DISTANCE:
                unmapped.append(pdf_p)
                continue
            off = offset_table[nearest]
        else:
            unmapped.append(pdf_p)
            continue

        printed = pdf_p - off
        if printed <= 0:
            # Frontmatter — before printed p.1. No reliable citation target.
            unmapped.append(pdf_p)
            continue
        pdf_to_printed[pdf_p] = printed

    # Reverse: first PDF page encountered per printed number wins (deterministic
    # since pdf_pages_sorted is ascending). Later duplicates (e.g., renumbering
    # bugs) are silently dropped — book-reader should not rely on this side.
    printed_to_pdf: dict[int, int] = {}
    for pdf_p, printed_p in pdf_to_printed.items():
        printed_to_pdf.setdefault(printed_p, pdf_p)

    return {
        "slug": slug,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_pages_pdf": meta["n_pages"],
        "global_mode_offset": global_offset,
        "direct_detections": len(offset_table),
        "outlier_detections_rejected": outlier_detections,
        "mapped_pdf_pages": len(pdf_to_printed),
        "unmapped_pdf_pages": unmapped,
        "pdf_to_printed": {str(k): v for k, v in pdf_to_printed.items()},
        "printed_to_pdf": {str(k): v for k, v in printed_to_pdf.items()},
    }


def write_index(slug: str, index: dict) -> Path:
    out = EXTRACTED_DIR / slug / "_page_index.json"
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def summarise(index: dict) -> str:
    n = index["n_pages_pdf"]
    mapped = index["mapped_pdf_pages"]
    unmapped = len(index["unmapped_pdf_pages"])
    direct = index["direct_detections"]
    pct_mapped = 100.0 * mapped / n if n else 0.0
    return (
        f"{index['slug']}: {mapped}/{n} PDF pages mapped ({pct_mapped:.1f}%), "
        f"{direct} direct detections, {unmapped} unmapped, "
        f"global offset={index['global_mode_offset']}"
    )


def list_all_slugs() -> list[str]:
    return sorted(
        p.name
        for p in EXTRACTED_DIR.iterdir()
        if p.is_dir() and (p / "_metadata.json").exists()
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("slug", nargs="?", help="book slug (directory under books/extracted/)")
    g.add_argument("--all", action="store_true", help="process every extracted book")
    args = ap.parse_args()

    slugs = list_all_slugs() if args.all else [args.slug]
    rc = 0
    for slug in slugs:
        try:
            index = build_index(slug)
        except Exception as e:
            print(f"{slug}: ERROR — {e}", file=sys.stderr)
            rc = 1
            continue
        path = write_index(slug, index)
        print(summarise(index))
        print(f"  → {path.relative_to(EXTRACTED_DIR.parent.parent)}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
