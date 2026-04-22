"""Smoke tests for Phase 3.8 B2 — Gayed MA-robustness sweep.

Four smoke tests enforce the B2 prompt §5 deliverable checklist:

1. ``test_b2_config_validates_enum_filter`` — B2Config __post_init__
   rejects invalid ``filter``/``leg``/``ma_period`` and accepts valid.
2. ``test_b2_signal_no_lookahead`` — both SMA and EMA regime flags at
   bar ``t`` use **only** data through ``t-1``.
3. ``test_b2_uses_shared_darf_helper`` — the B2 module reuses the
   exact ``apply_darf_year_end`` function imported from the B1
   module (no duplicated tax logic).
4. ``test_b2_smoke_16_config_grid_single_year_runs`` — all 16 configs
   run end-to-end on a short fabricated series without exception.

Citations
---------

* ``[leverage_for_the_long_run, p.14, Table 6; p.16]`` — Gayed MA
  robustness 10d-200d.
* ``[cycle_analytics, p.9-10, ch.1-2]`` — EMA IIR recursion.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment prev_weight × ret.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies import (
    phase3_8_b1_gayed_canonical as b1_mod,
)
from ai_trade.backtest.strategies import (
    phase3_8_b2_ma_robustness as b2_mod,
)
from ai_trade.backtest.strategies.phase3_8_b2_ma_robustness import (
    B2Config,
    compute_regime_signal_b2,
    simulate_b2,
)


def _price_from_returns(r: pd.Series, start: float = 100.0) -> pd.Series:
    return (1.0 + r).cumprod() * start


def test_b2_config_validates_enum_filter():
    """B2Config rejects invalid filter/leg/ma_period; accepts valid combos."""
    # Valid cases — all 16 grid combos construct fine.
    for flt in ("SMA", "EMA"):
        for n in (100, 125, 150, 200):
            for leg in ("UPRO", "SSO"):
                cfg = B2Config(filter=flt, ma_period=n, leg=leg)
                assert cfg.filter == flt
                assert cfg.ma_period == n
                assert cfg.leg == leg
                # Leverage property derives from leg.
                assert cfg.leverage == (3.0 if leg == "UPRO" else 2.0)

    # Invalid filter.
    with pytest.raises(ValueError, match="filter must be"):
        B2Config(filter="WMA", ma_period=100, leg="UPRO")  # type: ignore[arg-type]

    # Invalid leg.
    with pytest.raises(ValueError, match="leg must be"):
        B2Config(filter="SMA", ma_period=100, leg="TQQQ")  # type: ignore[arg-type]

    # Invalid ma_period (must be > 1).
    with pytest.raises(ValueError, match="ma_period"):
        B2Config(filter="SMA", ma_period=1, leg="UPRO")
    with pytest.raises(ValueError, match="ma_period"):
        B2Config(filter="EMA", ma_period=0, leg="SSO")


def test_b2_signal_no_lookahead():
    """SMA and EMA regime flags at t must equal ``close_{t-1} > MA_{t-1}``.

    Both branches are tested on a V-shaped price series that crosses
    the MA in both directions.
    """
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    legs = np.concatenate(
        [np.linspace(100.0, 80.0, 150), np.linspace(80.0, 120.0, 150)]
    )
    price = pd.Series(legs, index=idx)
    n = 20

    # --- SMA branch ---
    regime_sma = compute_regime_signal_b2(price, filter="SMA", ma_period=n)
    sma = price.rolling(n, min_periods=n).mean()
    raw_sma = (price > sma).astype(int)
    assert int(regime_sma.iloc[0]) == 0  # warmup → 0
    assert int(regime_sma.iloc[n - 1]) == 0  # still warmup shifted
    for t in range(n + 5, len(idx) - 5, 7):
        assert int(regime_sma.iloc[t]) == int(raw_sma.iloc[t - 1]), (
            f"SMA lookahead violation at t={t}"
        )

    # --- EMA branch ---
    regime_ema = compute_regime_signal_b2(price, filter="EMA", ma_period=n)
    ema = price.ewm(span=n, adjust=False).mean()
    ema.iloc[: n - 1] = np.nan
    raw_ema = (price > ema).astype(int)
    assert int(regime_ema.iloc[0]) == 0
    for t in range(n + 5, len(idx) - 5, 7):
        assert int(regime_ema.iloc[t]) == int(raw_ema.iloc[t - 1]), (
            f"EMA lookahead violation at t={t}"
        )


def test_b2_uses_shared_darf_helper():
    """B2 module must reuse B1's :func:`apply_darf_year_end` (no copy).

    Hard constraint from the B2 prompt: 'REUSE apply_darf_year_end
    from phase3_8_b1_gayed_canonical.py (do NOT reimplement)'. We
    verify by **identity** (same function object).
    """
    # 1) The names are bound to the same function object.
    assert b2_mod.apply_darf_year_end is b1_mod.apply_darf_year_end, (
        "B2 must import apply_darf_year_end from B1, not redefine it"
    )

    # 2) Calling it through the B2 re-export matches B1 output exactly.
    idx = pd.bdate_range("2020-01-01", "2022-06-30")
    gross = pd.Series(0.0005, index=idx)
    eq_b2, net_b2, tax_b2 = b2_mod.apply_darf_year_end(gross, tax_rate=0.15)
    eq_b1, net_b1, tax_b1 = b1_mod.apply_darf_year_end(gross, tax_rate=0.15)
    pd.testing.assert_series_equal(eq_b2, eq_b1)
    pd.testing.assert_series_equal(net_b2, net_b1)
    assert abs(tax_b2 - tax_b1) < 1e-12


def test_b2_smoke_16_config_grid_single_year_runs():
    """All 16 configs (2 filters × 4 MA periods × 2 legs) run cleanly.

    Uses a fabricated SPX-TR-like series of ~500 business days long
    enough to exercise the longest MA (200). Asserts each config
    produces a finite post-tax equity curve with at least one regime
    switch.
    """
    idx = pd.bdate_range("2018-01-01", "2020-12-31")
    n = len(idx)
    # Drift that oscillates → multiple MA crossings for all periods.
    t = np.linspace(0, 6 * np.pi, n)
    daily = 0.0004 * np.cos(t) + 0.0001
    returns = pd.Series(daily, index=idx)
    price = _price_from_returns(returns)
    ffr = pd.Series(0.03, index=idx)

    filters = ("SMA", "EMA")
    periods = (100, 125, 150, 200)
    legs = ("UPRO", "SSO")

    n_configs = 0
    for flt in filters:
        for p in periods:
            for leg in legs:
                cfg = B2Config(
                    filter=flt,
                    ma_period=p,
                    leg=leg,
                    tax_rate=0.15,
                    use_real_letf=False,
                )
                res = simulate_b2(
                    returns, price, ffr, cfg, real_letf_returns=None
                )
                assert len(res.equity) == n
                assert res.equity.isna().sum() == 0
                assert (res.equity > 0).all(), (
                    f"equity non-positive for cfg={cfg}"
                )
                # At least one regime switch with oscillating price.
                assert int(res.switches.sum()) >= 1, (
                    f"no regime switch for cfg={cfg} (switches={int(res.switches.sum())})"
                )
                n_configs += 1

    assert n_configs == 16, f"expected 16 configs, ran {n_configs}"
