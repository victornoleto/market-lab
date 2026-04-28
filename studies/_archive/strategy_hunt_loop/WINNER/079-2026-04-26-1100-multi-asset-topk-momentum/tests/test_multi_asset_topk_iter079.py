"""Iter 079 — TDD spec for Multi-asset Top-K relative+absolute momentum.

Tests top-K rotation, per-leg AGG routing on abs-mom failure, T-1 lag,
transaction cost, and pandas/numpy parity.

Citations:
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[stocks_on_the_move, p.21-30, p.81]` — momentum framework + lookback.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from multi_asset_topk_momentum import (  # noqa: E402
    SELECTABLE_ASSETS,
    compute_lookback_returns_multi,
    compute_topk_returns,
    top_k_signal,
)
from numpy_reference_iter079 import compute_topk_returns_np  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def monthly_prices_5_assets() -> dict[str, pd.Series]:
    """13-month prices for SPY/QQQ/EFA/TLT/GLD/AGG with deterministic regimes.

    Designed so the top-K selector cycles through:
    - QQQ leads early (tech bull)
    - GLD/TLT lead during a fake "drawdown" period
    - SPY leads late (broad recovery)
    AGG drifts slowly and never wins on lookback.
    """
    dates = pd.date_range("2020-01-31", periods=13, freq="ME")
    return {
        "SPY": pd.Series([100, 102, 105, 108, 110, 105, 95, 100, 110, 115, 122, 128, 135], index=dates, dtype=float),
        "QQQ": pd.Series([100, 105, 112, 120, 128, 130, 122, 130, 142, 150, 155, 158, 162], index=dates, dtype=float),
        "EFA": pd.Series([100, 101, 103, 105, 107, 102, 95, 97, 100, 103, 105, 107, 110], index=dates, dtype=float),
        "TLT": pd.Series([100, 101, 102, 103, 104, 110, 115, 113, 110, 108, 106, 104, 102], index=dates, dtype=float),
        "GLD": pd.Series([100, 102, 105, 107, 108, 115, 122, 120, 118, 116, 114, 112, 110], index=dates, dtype=float),
        "AGG": pd.Series([100, 100.4, 100.8, 101.2, 101.6, 102.0, 102.4, 102.8, 103.2, 103.6, 104.0, 104.4, 104.8], index=dates, dtype=float),
    }


# ---------------------------------------------------------------------------
# 1. Multi-asset lookback returns
# ---------------------------------------------------------------------------


def test_compute_lookback_returns_multi_3m_shape(monthly_prices_5_assets):
    """3-month lookback DataFrame: rows=months, cols=selectable assets."""
    df = compute_lookback_returns_multi(monthly_prices_5_assets, lookback_months=3)
    # Should have one column per selectable asset (5: SPY, QQQ, EFA, TLT, GLD)
    assert set(df.columns) == set(SELECTABLE_ASSETS)
    assert len(df.columns) == 5
    # First 3 rows NaN (insufficient history)
    assert df.iloc[0:3].isna().all().all()
    # Row at idx=3 (Apr-2020): SPY 3m = 108/100 - 1 = 0.08
    assert pytest.approx(df.loc[df.index[3], "SPY"], abs=1e-9) == 0.08
    # QQQ 3m = 120/100 - 1 = 0.20
    assert pytest.approx(df.loc[df.index[3], "QQQ"], abs=1e-9) == 0.20


def test_compute_lookback_returns_multi_excludes_agg(monthly_prices_5_assets):
    """AGG must NOT appear in the lookback DataFrame (it's only the fallback)."""
    df = compute_lookback_returns_multi(monthly_prices_5_assets, lookback_months=3)
    assert "AGG" not in df.columns


# ---------------------------------------------------------------------------
# 2. Top-K signal — ranking + abs-mom
# ---------------------------------------------------------------------------


def test_top_k_signal_k1_picks_single_winner():
    """K=1: highest lookback gets weight 1.0; others 0."""
    idx = pd.date_range("2020-01-31", periods=2, freq="ME")
    lb = pd.DataFrame(
        {
            "SPY": [0.10, 0.05],
            "QQQ": [0.20, 0.30],  # winner row 0 and row 1
            "EFA": [0.05, 0.10],
            "TLT": [0.02, -0.01],
            "GLD": [0.08, 0.15],
        },
        index=idx,
    )
    sig = top_k_signal(lb, top_k=1, abs_threshold=0.0)
    # QQQ should be 1.0 on both rows
    assert pytest.approx(sig.loc[idx[0], "QQQ"], abs=1e-9) == 1.0
    assert pytest.approx(sig.loc[idx[1], "QQQ"], abs=1e-9) == 1.0
    # All other selectable assets and AGG = 0
    for col in ["SPY", "EFA", "TLT", "GLD", "AGG"]:
        assert sig.loc[idx[0], col] == 0.0
        assert sig.loc[idx[1], col] == 0.0
    # Row sums = 1.0
    assert pytest.approx(sig.loc[idx[0]].sum(), abs=1e-9) == 1.0


def test_top_k_signal_k2_equal_weight():
    """K=2: top 2 assets each get 0.5."""
    idx = pd.date_range("2020-01-31", periods=1, freq="ME")
    lb = pd.DataFrame(
        {"SPY": [0.10], "QQQ": [0.20], "EFA": [0.05], "TLT": [0.02], "GLD": [0.15]},
        index=idx,
    )
    sig = top_k_signal(lb, top_k=2, abs_threshold=0.0)
    # QQQ (0.20) and GLD (0.15) are top-2
    assert pytest.approx(sig.loc[idx[0], "QQQ"], abs=1e-9) == 0.5
    assert pytest.approx(sig.loc[idx[0], "GLD"], abs=1e-9) == 0.5
    assert sig.loc[idx[0], "SPY"] == 0.0
    assert pytest.approx(sig.loc[idx[0]].sum(), abs=1e-9) == 1.0


def test_top_k_signal_k3_equal_weight():
    """K=3: top 3 each get 1/3."""
    idx = pd.date_range("2020-01-31", periods=1, freq="ME")
    lb = pd.DataFrame(
        {"SPY": [0.10], "QQQ": [0.20], "EFA": [0.05], "TLT": [0.02], "GLD": [0.15]},
        index=idx,
    )
    sig = top_k_signal(lb, top_k=3, abs_threshold=0.0)
    # QQQ, GLD, SPY are top-3
    assert pytest.approx(sig.loc[idx[0], "QQQ"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig.loc[idx[0], "GLD"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig.loc[idx[0], "SPY"], abs=1e-9) == 1 / 3
    assert sig.loc[idx[0], "EFA"] == 0.0
    assert sig.loc[idx[0], "TLT"] == 0.0
    assert pytest.approx(sig.loc[idx[0]].sum(), abs=1e-9) == 1.0


# ---------------------------------------------------------------------------
# 3. Per-leg abs-mom routing
# ---------------------------------------------------------------------------


def test_top_k_signal_per_leg_routes_negative_lb_to_agg():
    """K=2 with one positive + one negative leg → 0.5 to positive, 0.5 to AGG."""
    idx = pd.date_range("2020-01-31", periods=1, freq="ME")
    lb = pd.DataFrame(
        {"SPY": [-0.05], "QQQ": [0.10], "EFA": [-0.10], "TLT": [-0.20], "GLD": [-0.15]},
        index=idx,
    )
    # Top-2: QQQ (0.10), SPY (-0.05). QQQ passes abs-mom (>0); SPY fails (<0).
    sig = top_k_signal(lb, top_k=2, abs_threshold=0.0)
    assert pytest.approx(sig.loc[idx[0], "QQQ"], abs=1e-9) == 0.5
    assert sig.loc[idx[0], "SPY"] == 0.0  # routed to AGG instead
    assert pytest.approx(sig.loc[idx[0], "AGG"], abs=1e-9) == 0.5
    assert pytest.approx(sig.loc[idx[0]].sum(), abs=1e-9) == 1.0


def test_top_k_signal_all_legs_fail_abs_mom_routes_all_to_agg():
    """K=2 with both top-2 legs failing abs-mom → 100% AGG."""
    idx = pd.date_range("2020-01-31", periods=1, freq="ME")
    lb = pd.DataFrame(
        {"SPY": [-0.05], "QQQ": [-0.02], "EFA": [-0.10], "TLT": [-0.20], "GLD": [-0.15]},
        index=idx,
    )
    sig = top_k_signal(lb, top_k=2, abs_threshold=0.0)
    assert pytest.approx(sig.loc[idx[0], "AGG"], abs=1e-9) == 1.0
    for col in SELECTABLE_ASSETS:
        assert sig.loc[idx[0], col] == 0.0


def test_top_k_signal_threshold_above_zero():
    """abs_threshold = 0.05 means any leg with lb ≤ 0.05 routes to AGG."""
    idx = pd.date_range("2020-01-31", periods=1, freq="ME")
    lb = pd.DataFrame(
        {"SPY": [0.03], "QQQ": [0.10], "EFA": [0.04], "TLT": [0.06], "GLD": [0.08]},
        index=idx,
    )
    # Top-3: QQQ (0.10), GLD (0.08), TLT (0.06). All > 0.05 → all kept.
    sig = top_k_signal(lb, top_k=3, abs_threshold=0.05)
    assert pytest.approx(sig.loc[idx[0], "QQQ"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig.loc[idx[0], "GLD"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig.loc[idx[0], "TLT"], abs=1e-9) == 1 / 3
    assert sig.loc[idx[0], "AGG"] == 0.0
    # Same lb but threshold=0.07: only QQQ + GLD pass; TLT routes to AGG
    sig2 = top_k_signal(lb, top_k=3, abs_threshold=0.07)
    assert pytest.approx(sig2.loc[idx[0], "QQQ"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig2.loc[idx[0], "GLD"], abs=1e-9) == 1 / 3
    assert pytest.approx(sig2.loc[idx[0], "AGG"], abs=1e-9) == 1 / 3


# ---------------------------------------------------------------------------
# 4. T-1 lag — signal at end-of-month-M applies to month-M+1 returns
# ---------------------------------------------------------------------------


def test_t_minus_1_lag_with_k2():
    """K=2 signal at Jan-31 close drives Feb returns; K=2 signal at Feb-29 → Mar."""
    daily_idx = pd.date_range("2020-01-01", "2020-04-30", freq="B")
    rets = {asset: pd.Series(0.0, index=daily_idx) for asset in SELECTABLE_ASSETS + ["AGG"]}
    rets["SPY"] = pd.Series(0.001, index=daily_idx)
    rets["QQQ"] = pd.Series(0.002, index=daily_idx)
    rets["GLD"] = pd.Series(-0.001, index=daily_idx)
    monthly_idx = pd.date_range("2020-01-31", periods=4, freq="ME")
    sig = pd.DataFrame(0.0, index=monthly_idx, columns=SELECTABLE_ASSETS + ["AGG"])
    # Jan-31: K=2 SPY+QQQ each 0.5
    sig.loc[monthly_idx[0], ["SPY", "QQQ"]] = 0.5
    # Feb-29: K=2 GLD+QQQ each 0.5
    sig.loc[monthly_idx[1], ["QQQ", "GLD"]] = 0.5
    # Mar-31: 100% AGG
    sig.loc[monthly_idx[2], "AGG"] = 1.0
    # Apr: same as Mar
    sig.loc[monthly_idx[3], "AGG"] = 1.0
    out = compute_topk_returns(rets, sig, trans_cost_bps=0.0)
    # Pre-Feb (Jan): no signal yet → 0
    jan = out.loc[out.index < "2020-02-01"]
    assert np.allclose(jan.values, 0.0, atol=1e-12)
    # Feb returns: 0.5*SPY + 0.5*QQQ = 0.5*0.001 + 0.5*0.002 = 0.0015
    feb = out.loc[(out.index >= "2020-02-01") & (out.index < "2020-03-01")]
    assert np.allclose(feb.values, 0.0015, atol=1e-12)
    # Mar returns: 0.5*GLD + 0.5*QQQ = 0.5*(-0.001) + 0.5*(0.002) = 0.0005
    mar = out.loc[(out.index >= "2020-03-01") & (out.index < "2020-04-01")]
    assert np.allclose(mar.values, 0.0005, atol=1e-12)


# ---------------------------------------------------------------------------
# 5. Transaction cost across 6 sleeves
# ---------------------------------------------------------------------------


def test_transaction_cost_l1_norm_across_6_sleeves():
    """L1 turnover across all 6 sleeves charged on first day of new month."""
    daily_idx = pd.date_range("2020-01-01", "2020-03-31", freq="B")
    rets = {asset: pd.Series(0.0, index=daily_idx) for asset in SELECTABLE_ASSETS + ["AGG"]}
    monthly_idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    sig = pd.DataFrame(0.0, index=monthly_idx, columns=SELECTABLE_ASSETS + ["AGG"])
    sig.loc[monthly_idx[0], "SPY"] = 1.0
    sig.loc[monthly_idx[1], ["QQQ", "GLD"]] = 0.5  # K=2 split
    sig.loc[monthly_idx[2], ["QQQ", "GLD"]] = 0.5
    out_no_cost = compute_topk_returns(rets, sig, trans_cost_bps=0.0)
    out_with_cost = compute_topk_returns(rets, sig, trans_cost_bps=10.0)
    # Feb-3: turn from cash (0,0,0,0,0,0) to (1,0,0,0,0,0) → L1 = 1.0 → cost 0.001
    feb_first = out_with_cost.loc["2020-02-03"]
    assert pytest.approx(feb_first, abs=1e-9) == 0.0 - 0.001
    # Mar-2: turn from (1,0,0,0,0,0) to (0,0.5,0,0,0.5,0) → L1 = 1.0 + 0.5 + 0.5 = 2.0 → cost 0.002
    mar_first = out_with_cost.loc["2020-03-02"]
    assert pytest.approx(mar_first, abs=1e-9) == 0.0 - 0.002
    # Mid-Feb intra-month: no cost
    feb_mid = out_with_cost.loc["2020-02-14"]
    assert pytest.approx(feb_mid, abs=1e-12) == out_no_cost.loc["2020-02-14"]


# ---------------------------------------------------------------------------
# 6. Numpy reference parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_to_1e9():
    """Numpy-pure implementation matches pandas element-wise to 1e-9."""
    rng = np.random.default_rng(20260426)
    daily_idx = pd.date_range("2010-01-04", "2024-12-31", freq="B")
    n = len(daily_idx)
    asset_order = SELECTABLE_ASSETS + ["AGG"]
    rets = {
        a: pd.Series(rng.normal(3e-4, 0.012, n), index=daily_idx) for a in asset_order
    }
    monthly_idx = pd.DatetimeIndex(
        sorted(set(daily_idx.to_period("M").to_timestamp("M").map(
            lambda t: daily_idx[daily_idx <= t].max() if (daily_idx <= t).any() else None
        )))
    ).dropna()
    monthly_idx = monthly_idx[monthly_idx.notna()]
    # Random signals (each row = one of K∈{1,2,3} assets each 1/K weight, occasionally AGG)
    sig = pd.DataFrame(0.0, index=monthly_idx, columns=asset_order)
    for i, ts in enumerate(monthly_idx):
        choice = rng.choice(["k1", "k2", "k3", "agg"], p=[0.4, 0.3, 0.2, 0.1])
        if choice == "agg":
            sig.loc[ts, "AGG"] = 1.0
        else:
            k = int(choice[1])
            picks = rng.choice(SELECTABLE_ASSETS, size=k, replace=False)
            for p in picks:
                sig.loc[ts, p] = 1.0 / k
    pd_out = compute_topk_returns(rets, sig, trans_cost_bps=5.0)
    np_out = compute_topk_returns_np(
        asset_returns={a: rets[a].values for a in asset_order},
        asset_order=asset_order,
        daily_dates=daily_idx.values,
        signal_dates=sig.index.values,
        signal_weights=sig[asset_order].values,
        trans_cost_bps=5.0,
    )
    assert pd_out.shape[0] == np_out.shape[0]
    max_abs = float(np.max(np.abs(pd_out.values - np_out)))
    assert max_abs < 1e-9, f"max_abs_diff={max_abs:.3e}"


# ---------------------------------------------------------------------------
# 7. Selectable assets contract
# ---------------------------------------------------------------------------


def test_selectable_assets_contract():
    """SELECTABLE_ASSETS = SPY, QQQ, EFA, TLT, GLD (5 assets, AGG-fallback excluded)."""
    assert SELECTABLE_ASSETS == ["SPY", "QQQ", "EFA", "TLT", "GLD"]
    assert "AGG" not in SELECTABLE_ASSETS
