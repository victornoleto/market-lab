from __future__ import annotations

from lrs.top20_by_cagr import collect_candidates


def test_collect_candidates_sorts_by_cagr_descending() -> None:
    frame = collect_candidates()

    assert len(frame) >= 20
    top = frame.head(20)
    assert top["cagr"].is_monotonic_decreasing
    assert top["mdd"].notna().all()
    assert (top["rank_basis"] == "cagr_desc_no_drawdown_filter").all()
