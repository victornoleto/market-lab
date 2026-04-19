"""Tests for screener.universe — orchestration + ranking."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.screener.universe import Candidate, screen_universe


def _write_synth(
    storage: TiingoStorage,
    ticker: str,
    asset_class: str,
    *,
    n: int = 1000,
    base: float = 100.0,
    seed: int = 0,
    volume: float = 1e6,
):
    rng = np.random.default_rng(seed)
    closes = base + np.cumsum(rng.normal(0.0, 0.5, size=n))
    closes = np.clip(closes, base / 2, None)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    df = pd.DataFrame(
        {
            "open": closes,
            "high": closes + 1.0,
            "low": closes - 1.0,
            "close": closes,
            "volume": np.full(n, volume),
        },
        index=idx,
    )
    storage.write(ticker, df, frequency="daily", asset_class=asset_class)


@pytest.fixture
def storage(tmp_path: Path) -> TiingoStorage:
    s = TiingoStorage(root=tmp_path / "tiingo")
    _write_synth(s, "AAA", "etf", n=800, seed=1, volume=2e6)
    _write_synth(s, "BBB", "etf", n=800, seed=2, volume=5e6)
    _write_synth(s, "CCC", "crypto", n=800, seed=3, volume=0.0)
    return s


class TestScreenUniverse:
    def test_returns_dataframe_with_expected_columns(self, storage: TiingoStorage):
        cands = [
            Candidate("AAA", "etf"),
            Candidate("BBB", "etf"),
            Candidate("CCC", "crypto"),
        ]
        df = screen_universe(cands, storage, frequency="daily")
        for col in [
            "ticker",
            "asset_class",
            "frequency",
            "n_bars",
            "first_dt",
            "last_dt",
            "hurst",
            "atr_pct",
            "realized_vol",
            "dollar_volume",
            "mr_score",
            "liquidity_rank",
            "composite_rank",
            "notes",
        ]:
            assert col in df.columns, f"missing column {col}"
        assert len(df) == 3

    def test_missing_ticker_recorded_with_note(self, storage: TiingoStorage):
        cands = [Candidate("ZZZ", "etf")]
        df = screen_universe(cands, storage, frequency="daily")
        assert df.loc[0, "notes"] == "not_in_storage"
        assert df.loc[0, "n_bars"] == 0

    def test_insufficient_history_recorded(self, tmp_path: Path):
        s = TiingoStorage(root=tmp_path / "tiingo")
        _write_synth(s, "TINY", "etf", n=50, seed=0)
        df = screen_universe([Candidate("TINY", "etf")], s)
        assert df.loc[0, "notes"] == "insufficient_history"

    def test_zero_volume_falls_back_to_atr_for_liquidity(self, tmp_path: Path):
        s = TiingoStorage(root=tmp_path / "tiingo")
        _write_synth(s, "ZVOL", "crypto", n=600, seed=0, volume=0.0)
        df = screen_universe([Candidate("ZVOL", "crypto")], s)
        # No volume → fallback path (ATR-based ranking) used; row still ranked.
        assert pd.notna(df.loc[0, "liquidity_rank"])

    def test_ranking_is_sorted_ascending(self, storage: TiingoStorage):
        cands = [
            Candidate("AAA", "etf"),
            Candidate("BBB", "etf"),
            Candidate("CCC", "crypto"),
        ]
        df = screen_universe(cands, storage, frequency="daily")
        composite = df["composite_rank"].dropna().to_list()
        assert composite == sorted(composite)

    def test_mr_score_is_one_minus_hurst(self, storage: TiingoStorage):
        df = screen_universe([Candidate("AAA", "etf")], storage)
        h = df.loc[0, "hurst"]
        if pd.notna(h):
            expected = max(0.0, min(1.0, 1.0 - h))
            assert df.loc[0, "mr_score"] == pytest.approx(expected)

    def test_uses_longest_window_available(self, tmp_path: Path):
        # Phase 3 hard rule: always longest window. Verify n_bars ≈ written length.
        s = TiingoStorage(root=tmp_path / "tiingo")
        _write_synth(s, "LONG", "etf", n=1500, seed=0)
        df = screen_universe([Candidate("LONG", "etf")], s)
        assert df.loc[0, "n_bars"] == 1500
