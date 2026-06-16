from __future__ import annotations

import pandas as pd

from studies.return_stacked_core.factor_core_comparison.run import (
    US_SHORT_LABELS,
    aligned_equity,
    build_us_short_payload,
    extract_equity_frame,
)


def test_us_short_payload_is_sanitized_and_preserves_rsc_tracking_formula() -> None:
    payload = build_us_short_payload("Yearly")

    assert "authorization" not in payload
    assert "Bearer" not in str(payload)
    assert payload["backtests"][3]["allocation"] == {"AVUS": 60, "AVUV": 20, "SPMO": 20}

    rsc = payload["backtests"][4]["allocation"]
    assert rsc["SPY"] == 40
    assert rsc["GDE"] == 35
    assert rsc["ZROZ"] == 25
    assert rsc["DBMF"] == 28
    assert rsc["KMLM"] == 12
    assert rsc["CASHX?E=-2"] == -40
    assert sum(rsc.values()) == 100


def test_extract_equity_frame_from_testfolio_history_shape() -> None:
    dates = pd.to_datetime(["2024-01-02", "2024-01-03"], utc=True).astype("int64") // 10**9
    response = {
        "charts": {
            "history": [
                dates.tolist(),
                [100.0, 101.0],
                [100.0, 99.0],
                [100.0, 102.0],
                [100.0, 103.0],
                [100.0, 98.0],
            ]
        }
    }

    frame = extract_equity_frame(response, US_SHORT_LABELS)

    assert list(frame.columns) == US_SHORT_LABELS
    assert frame.iloc[1]["AVUS_AVUV_SPMO_60_20_20"] == 103.0


def test_aligned_equity_drops_to_common_window_and_normalizes() -> None:
    idx = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    raw = pd.DataFrame({"a": [100.0, 110.0, 121.0], "b": [None, 100.0, 90.0]}, index=idx)

    aligned = aligned_equity(raw)

    assert list(aligned.index) == list(idx[1:])
    assert aligned.iloc[0]["a"] == 1.0
    assert aligned.iloc[0]["b"] == 1.0
    assert aligned.iloc[1]["b"] == 0.9
