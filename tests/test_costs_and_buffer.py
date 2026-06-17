"""Transaction-cost model + ranking-buffer (hysteresis) in the momentum_v2 engine."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from studies.momentum_v2.core import (  # noqa: E402
    ScoreBundle,
    StrategyConfig,
    _returns_from_daily_weights,
    monthly_weights,
)


def test_cost_bps_zero_is_identical_and_positive_charges_turnover():
    idx = pd.date_range("2020-01-01", periods=4, freq="D")
    dw = pd.DataFrame([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], index=idx, columns=["A", "B"])
    ar = pd.DataFrame([[0.0, 0.0], [0.02, 0.0], [0.0, 0.03], [0.0, 0.01]], index=idx, columns=["A", "B"])
    gross = _returns_from_daily_weights(dw, dw, "x", asset_returns=ar, cost_bps=0.0)
    netted = _returns_from_daily_weights(dw, dw, "x", asset_returns=ar, cost_bps=50.0)
    # cost_bps=0 leaves returns untouched
    assert float((gross - _returns_from_daily_weights(dw, dw, "x", asset_returns=ar)).abs().max()) == 0.0
    # traded notional per day = |Δw| summed; day2 buys A (1.0), day3 sells A buys B (2.0), day4 none
    traded = dw.diff().abs().sum(axis=1).fillna(0.0)
    expected = gross - (50.0 / 10000.0) * traded
    assert float((netted - expected.loc[netted.index]).abs().max()) < 1e-15
    # net <= gross whenever there is trading
    assert (netted <= gross.loc[netted.index] + 1e-15).all()


def _bundle(scores_by_date, assets):
    idx = pd.to_datetime(list(scores_by_date))
    mp = pd.DataFrame(1.0, index=idx, columns=assets)
    sc = pd.DataFrame([[scores_by_date[d][a] for a in assets] for d in scores_by_date], index=idx, columns=assets)
    return ScoreBundle(monthly_prices=mp, scores={"raw_13612": sc}, monthly_vol=pd.DataFrame(1.0, index=idx, columns=assets))


def test_rank_buffer_holds_through_minor_rank_churn():
    assets = ("A", "B", "C", "D", "E")
    scores = {
        "2020-01-31": {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1},  # top2 = A,B
        "2020-02-29": {"C": 5, "A": 4, "B": 3, "D": 2, "E": 1},  # no-buffer -> C,A ; buffer(1) keeps A,B
    }
    bundle = _bundle(scores, assets)
    base = dict(name="t", universe="u", assets=assets, top_n=2, rebalance_months=1, rebalance_offset=0, score_mode="raw_13612")
    w_nobuf = monthly_weights(bundle, StrategyConfig(**base, rank_buffer=0))
    w_buf = monthly_weights(bundle, StrategyConfig(**base, rank_buffer=1))
    d2 = pd.Timestamp("2020-02-29")
    held_nobuf = set(w_nobuf.columns[w_nobuf.loc[d2] > 0])
    held_buf = set(w_buf.columns[w_buf.loc[d2] > 0])
    assert held_nobuf == {"C", "A"}      # fresh top-2 swaps B->C
    assert held_buf == {"A", "B"}        # buffer holds B (still within top_n+buffer=3) -> zero turnover


def test_rank_buffer_zero_matches_baseline_selection():
    assets = ("A", "B", "C", "D")
    scores = {"2020-01-31": {"A": 4, "B": 3, "C": 2, "D": 1}, "2020-02-29": {"D": 4, "C": 3, "B": 2, "A": 1}}
    bundle = _bundle(scores, assets)
    base = dict(name="t", universe="u", assets=assets, top_n=2, rebalance_months=1, rebalance_offset=0, score_mode="raw_13612")
    w0 = monthly_weights(bundle, StrategyConfig(**base, rank_buffer=0))
    # baseline picks fresh top-2 each month: {A,B} then {D,C}
    assert set(w0.columns[w0.loc[pd.Timestamp("2020-01-31")] > 0]) == {"A", "B"}
    assert set(w0.columns[w0.loc[pd.Timestamp("2020-02-29")] > 0]) == {"D", "C"}
