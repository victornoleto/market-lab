"""Smoke tests for Phase 3.8 B1 — Gayed canonical SMA-200 LETF rotation.

Four smoke tests enforce the plan §5 requirements:

1. ``test_signal_no_lookahead`` — SMA regime at bar t uses only t-1 data.
2. ``test_darf_year_end_applied_once_per_year`` — tax hits the last trading
   day of each year and is proportional to the year's net gain.
3. ``test_synth_upro_matches_real_within_5pp_2020`` — synth 3x CAGR for
   calendar-year 2020 is within ±5pp of real UPRO 2020 CAGR (mandate §4.1
   tracking-error caveat). Skipped gracefully if the Tiingo cache is
   absent; the honest-gate runner also enforces this at runtime.
4. ``test_simulate_b1_smoke_1985_run`` — a single short run finishes
   without exception and produces at least one regime switch.

Citations
---------

* ``[leverage_for_the_long_run, p.7-8, p.13-17]`` — canonical signal + table.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment prev_weight × ret.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.helpers.synthetic_letf import (
    synthesize_letf_returns_ffr_aware,
)
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    B1Config,
    apply_darf_year_end,
    compute_regime_signal,
    simulate_b1,
)

UPRO_PARQUET = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "tiingo"
    / "daily"
    / "prices"
    / "UPRO.parquet"
)


def _price_from_returns(r: pd.Series, start: float = 100.0) -> pd.Series:
    return (1.0 + r).cumprod() * start


def test_signal_no_lookahead():
    """At every bar t, ``regime_t`` equals ``close_{t-1} > SMA_{t-1}``.

    Construct a price series that crosses its SMA at a known timestamp;
    the regime flag must flip **on the day after** the underlying cross
    — not the same day (that would be a 1-bar look-ahead).
    """
    idx = pd.date_range("2020-01-01", periods=250, freq="B")
    # Down-then-up V-shape so the SMA(20) is crossed both ways.
    legs = np.concatenate(
        [np.linspace(100.0, 80.0, 125), np.linspace(80.0, 120.0, 125)]
    )
    price = pd.Series(legs, index=idx)

    regime = compute_regime_signal(price, sma_period=20)

    # Before warmup (20 bars), regime must be 0 (shift(1) of NaN → 0).
    assert int(regime.iloc[0]) == 0
    assert int(regime.iloc[19]) == 0

    # For t >= sma_period + 1, regime_t must match (close > SMA) at t-1.
    sma = price.rolling(20, min_periods=20).mean()
    raw = (price > sma).astype(int)
    # Sample 50 timestamps after warmup; regime[t] == raw[t-1].
    for t in range(25, 245, 5):
        assert int(regime.iloc[t]) == int(raw.iloc[t - 1]), (
            f"lookahead violation at t={t}: regime={int(regime.iloc[t])} "
            f"raw_{{t-1}}={int(raw.iloc[t - 1])}"
        )


def test_darf_year_end_applied_once_per_year():
    """DARF must hit exactly the last trading day of each calendar year,
    taxing only the year's net positive gain."""
    # 3 full years of business days with a flat +0.10%/day return → each
    # year's equity grows ~28.8%, tax should deduct 15% of that gain.
    idx = pd.bdate_range("2020-01-01", "2022-12-31")
    gross = pd.Series(0.001, index=idx)
    equity, daily_net, cum_tax = apply_darf_year_end(gross, tax_rate=0.15)

    # Identify the last trading day of each calendar year in the sample.
    ye_days = [
        group.index.max() for _, group in gross.groupby(gross.index.year)
    ]
    # On a year-end day, daily_net[t] should be materially **lower** than
    # the surrounding days because a 15%-of-yearly-gain deduction just
    # landed there. On non-YE days, daily_net ≈ gross (0.001).
    for ts in ye_days:
        assert daily_net.loc[ts] < 0.0, (
            f"year-end day {ts.date()} must see tax deduction (net < 0), "
            f"got {daily_net.loc[ts]:.5f}"
        )

    # Non-YE days should track the gross input closely.
    non_ye = [ts for ts in idx if ts not in set(ye_days)]
    non_ye_net = daily_net.loc[non_ye]
    # Each non-YE day is ~+0.1%, within 1e-9 of gross (pct_change of a
    # product is exact on a single bar).
    assert (non_ye_net - gross.loc[non_ye]).abs().max() < 1e-9

    # Cumulative tax must be >0 for three profitable years.
    assert cum_tax > 0.0

    # Idempotent zero-tax path → no year-end deduction.
    eq0, _, tax0 = apply_darf_year_end(gross, tax_rate=0.0)
    assert tax0 == 0.0
    assert abs(float(eq0.iloc[-1]) - float((1 + gross).prod())) < 1e-9


def test_synth_upro_matches_real_within_5pp_2020():
    """Synth-3x UPRO CAGR for 2020 must be within ±5pp of real UPRO 2020 CAGR.

    Mandate §4.1 tracking-error caveat: our FFR-aware synth is a
    theoretical model and real UPRO has small daily tracking errors
    — the 5pp band is the smoke-gate defined in the Plano B prompt.
    """
    if not UPRO_PARQUET.exists():
        pytest.skip(f"UPRO Tiingo cache missing at {UPRO_PARQUET}")

    real_df = pd.read_parquet(UPRO_PARQUET)
    real_df.index = pd.to_datetime(real_df.index)
    real_daily = real_df["adj_close"].astype(float).sort_index().pct_change()

    # Build SPX-TR 2020 from SPY via Tiingo. We rely on the shared loader
    # but only for 2020 to keep this unit test fast.
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(
        Path(__file__).resolve().parents[1] / "data" / "tiingo"
    )
    spy_df = storage.read("SPY", frequency="daily")
    spy_df.index = pd.to_datetime(spy_df.index)
    spy_daily = spy_df["adj_close"].astype(float).sort_index().pct_change()

    year = 2020
    spy_2020 = spy_daily.loc[spy_daily.index.year == year].dropna()
    real_2020 = real_daily.loc[real_daily.index.year == year].dropna()
    # Align on common dates
    common = spy_2020.index.intersection(real_2020.index)
    spy_2020 = spy_2020.loc[common]
    real_2020 = real_2020.loc[common]

    # FFR proxy — Ken French rf × 252; fallback to flat 0.5% if absent.
    try:
        from ai_trade.backtest.data.spx_tr_loader import fetch_ken_french_daily

        kf = fetch_ken_french_daily()
        ffr = (kf["rf"] * 252.0).reindex(common).ffill().bfill()
    except Exception:
        ffr = pd.Series(0.005, index=common)

    synth = synthesize_letf_returns_ffr_aware(
        spy_2020,
        leverage=3.0,
        ffr_annualized=ffr,
        expense_ratio=0.0095,
    )

    def _cagr(r: pd.Series) -> float:
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        n = len(r)
        if n < 2:
            return 0.0
        return eq ** (252.0 / n) - 1.0

    synth_cagr = _cagr(synth)
    real_cagr = _cagr(real_2020)
    delta_pp = abs(synth_cagr - real_cagr) * 100.0

    assert delta_pp <= 5.0, (
        f"synth 3x CAGR 2020={synth_cagr:.3%} real UPRO 2020={real_cagr:.3%} "
        f"|Δ|={delta_pp:.2f}pp — exceeds 5pp smoke gate"
    )


def test_simulate_b1_smoke_1985_run():
    """Single short run finishes without exception and produces >= 1 switch.

    This is a smoke test — we use a fabricated SPX-TR-like series long
    enough to exercise the 200-bar SMA and yield at least one regime
    change.
    """
    # ~2 years of business days with a sinusoidal drift → multiple
    # SMA-200 crossings.
    idx = pd.bdate_range("1985-01-01", "1986-12-31")
    n = len(idx)
    # Drift that crosses zero → price oscillates around SMA-200.
    t = np.linspace(0, 4 * np.pi, n)
    daily = 0.0004 * np.cos(t) + 0.0002
    returns = pd.Series(daily, index=idx)
    price = _price_from_returns(returns)
    ffr = pd.Series(0.05, index=idx)

    cfg = B1Config(
        leverage=3.0,
        letf_kind="UPRO",
        sma_period=200,
        tax_rate=0.15,
        use_real_letf=False,
    )
    res = simulate_b1(returns, price, ffr, cfg, real_letf_returns=None)

    assert len(res.equity) == n
    assert int(res.switches.sum()) >= 1, (
        f"expected >= 1 regime switch in a smoke run, got {int(res.switches.sum())}"
    )
    # Equity path must be finite, positive.
    assert res.equity.isna().sum() == 0
    assert (res.equity > 0).all()
