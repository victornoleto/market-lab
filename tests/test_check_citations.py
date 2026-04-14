import json
from pathlib import Path

import pytest

from scripts.check_citations import load_canonical_offset_map, resolve_printed_to_pdf


def test_load_canonical_offset_map_reads_page_index(tmp_path, monkeypatch):
    extracted = tmp_path / "books" / "extracted" / "fake_slug"
    extracted.mkdir(parents=True)
    (extracted / "_page_index.json").write_text(json.dumps({
        "slug": "fake_slug",
        "pdf_to_printed": {"15": 1, "16": 2, "17": 3},
        "printed_to_pdf": {"1": 15, "2": 16, "3": 17},
        "unmapped_pdf_pages": [1, 2, 3],
        "global_mode_offset": 14,
    }))
    monkeypatch.setattr("scripts.check_citations.EXTRACTED_DIR", tmp_path / "books" / "extracted")

    m = load_canonical_offset_map("fake_slug")
    assert m is not None
    assert m["printed_to_pdf"]["1"] == 15
    assert m["global_mode_offset"] == 14


def test_resolve_printed_to_pdf_uses_canonical_map(tmp_path, monkeypatch):
    extracted = tmp_path / "books" / "extracted" / "fake_slug"
    extracted.mkdir(parents=True)
    (extracted / "_page_index.json").write_text(json.dumps({
        "printed_to_pdf": {"1": 15, "100": 114},
        "global_mode_offset": 14,
    }))
    monkeypatch.setattr("scripts.check_citations.EXTRACTED_DIR", tmp_path / "books" / "extracted")

    pdf_p = resolve_printed_to_pdf("fake_slug", printed=100)
    assert pdf_p == 114


def test_load_canonical_offset_map_returns_none_when_missing(tmp_path, monkeypatch):
    extracted = tmp_path / "books" / "extracted" / "legacy_slug"
    extracted.mkdir(parents=True)
    monkeypatch.setattr("scripts.check_citations.EXTRACTED_DIR", tmp_path / "books" / "extracted")

    assert load_canonical_offset_map("legacy_slug") is None


def test_check_summary_prefers_canonical_map_over_heuristic(monkeypatch):
    """When _page_index.json exists, check_summary must use printed_to_pdf
    directly — not re-derive offset via detect_printed_pdf_offset."""
    from scripts import check_citations

    calls = []
    original_detect = check_citations.detect_printed_pdf_offset

    def spy(pages):
        calls.append("detect_called")
        return original_detect(pages)

    monkeypatch.setattr(check_citations, "detect_printed_pdf_offset", spy)
    # Use an existing real slug that has _page_index.json
    rep = check_citations.check_summary("cybernetic_trading")  # known-passing slug
    assert "detect_called" not in calls, "should have used canonical map"
    assert rep.offset >= 0
