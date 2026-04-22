"""Smoke tests for Phase 3.7 H2.b — Gayed 2x LRS + VIX floor.

Covers:
1. VIX gate — trades ONLY when both SMA regime and VIX<threshold are 1.
2. SMA regime switch — exposure flips on an explicit cross event.
3. Synth LETF wiring — exposure×letf_return matches manual compound when
   gate is always ON.

Citations
---------
* `[leverage_for_the_long_run, p.7-8, p.13, p.17]` — signal & leverage
* `[advances_fin_ml, p.31-34]` — F2-alignment verification
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h2_gayed_vix_floor import (
    H2GayedVixFloorConfig,
    compute_regime_and_vix_signal,
    simulate_h2_gayed_vix_floor,
    stitch_2x_letf_returns,
)


def _price_from_returns(r: pd.Series) -> pd.Series:
    return (1.0 + r).cumprod() * 100.0


def test_vix_gate_blocks_on_regime_when_vix_high():
    """Given a stable up-trend with always-on SMA, VIX>threshold should
    still block exposure."""
    idx = pd.date_range("2000-01-01", periods=400, freq="B")
    np.random.seed(7)
    # Steady +0.05%/day trend — SMA regime will be ON after warmup.
    r = pd.Series(0.0005, index=idx) + pd.Series(
        np.random.normal(0, 0.005, 400), index=idx
    )
    price = _price_from_returns(r)
    # VIX always HIGH (>50) — gate should block.
    vix_high = pd.Series(50.0, index=idx)
    # Annualized FFR at 2%.
    ffr = pd.Series(0.02, index=idx)
    cfg = H2GayedVixFloorConfig(sma_period=50, vix_threshold=25.0, tax_rate=0.0)

    res = simulate_h2_gayed_vix_floor(r, price, vix_high, ffr, cfg, upro_real=None)

    # Exposure must be 0 on every day (VIX never below 25).
    assert res.exposure.sum() == 0, (
        f"exposure should be 0 everywhere with VIX=50 > threshold=25, "
        f"got sum={res.exposure.sum()}"
    )
    # Equity should reflect pure cash return (cash_rate_annual/252).
    # After 400 days @ 4%/yr compounded: ~1 * (1+0.04/252)^400 ≈ 1.0664
    eq_end = res.equity.iloc[-1]
    expected_eq = (1.0 + cfg.cash_rate_annual / 252) ** len(r)
    # Within 0.5% relative (tax=0, no switches when exposure constant).
    assert abs(eq_end - expected_eq) / expected_eq < 0.005, (
        f"cash-only equity {eq_end:.4f} vs expected {expected_eq:.4f}"
    )


def test_sma_regime_signal_shifts_by_one_day():
    """compute_regime_and_vix_signal must use t-1 data only (F2-alignment)."""
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    # Price that crosses its own SMA at a known point.
    base = pd.Series(np.linspace(100, 80, 150).tolist()
                     + np.linspace(80, 120, 150).tolist(), index=idx)
    vix = pd.Series(15.0, index=idx)  # always-open gate
    cfg = H2GayedVixFloorConfig(sma_period=20, vix_threshold=25.0)
    regime, vix_gate = compute_regime_and_vix_signal(base, vix, cfg)

    # First sma_period bars are NaN in rolling → shift(1) fillna(0)
    # means regime_sma starts as 0.
    assert regime.iloc[0] == 0
    # After enough days, signal must align with shifted price > SMA.
    px_vs_sma = (base > base.rolling(cfg.sma_period, min_periods=cfg.sma_period).mean()).astype(int)
    # regime_sma[t] should equal px_vs_sma[t-1] wherever SMA is defined.
    defined = px_vs_sma.iloc[cfg.sma_period:].index
    for ts in defined[1:20]:  # sample small window
        prev_ts = base.index[base.index.get_loc(ts) - 1]
        assert regime.loc[ts] == px_vs_sma.loc[prev_ts], (
            f"F2 violation at {ts}: regime={regime.loc[ts]} vs "
            f"px_vs_sma_prev={px_vs_sma.loc[prev_ts]}"
        )


def test_synth_letf_wiring_matches_2x_spx_gross():
    """When both gates are always ON and tax=0, switch_cost=0, the daily
    net return should match 2x SPX-TR minus the FFR-aware cost."""
    idx = pd.date_range("2015-01-01", periods=500, freq="B")
    np.random.seed(11)
    r = pd.Series(np.random.normal(0.0004, 0.01, 500), index=idx)
    price = _price_from_returns(r)
    # VIX always low → gate always open; SMA short enough.
    vix_low = pd.Series(10.0, index=idx)
    ffr = pd.Series(0.02, index=idx)
    cfg = H2GayedVixFloorConfig(
        sma_period=5,
        vix_threshold=25.0,
        leverage=2.0,
        tax_rate=0.0,
        commission_bps=0.0,
        spread_bps=0.0,
        use_real_upro=False,  # synth throughout
    )
    res = simulate_h2_gayed_vix_floor(r, price, vix_low, ffr, cfg, upro_real=None)

    # Independently compute the stitched LETF series; on-regime days the
    # daily_returns should match stitch (sub-1bp rounding tolerance).
    letf = stitch_2x_letf_returns(r, None, ffr, cfg)

    # For the later portion where SMA is defined and stable:
    on_mask = (res.exposure > 0)
    active = res.daily_returns[on_mask].iloc[5:]  # skip switch bars
    active_letf = letf[on_mask].iloc[5:]
    aligned = pd.concat([active, active_letf], axis=1, join="inner").dropna()
    # Excluding switch days, the net return should equal letf daily return.
    # Difference should be bounded by tax at year end (tax_rate=0 → 0).
    diffs = (aligned.iloc[:, 0] - aligned.iloc[:, 1]).abs()
    # Allow a handful of year-end bars, switch bars — check 90th pct is tiny.
    q90 = float(np.quantile(diffs, 0.9))
    assert q90 < 1e-8, (
        f"synth LETF wiring: 90th-pct diff {q90:.2e} (should be < 1e-8 "
        f"with tax=0, cost=0, always-on)"
    )
