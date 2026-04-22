"""Smoke tests for Phase 3.8 B3 — Pauchlyova static+trend multi-asset allocation.

Four smoke tests enforce the plan B3 requirements:

1. ``test_base_allocation_sums_to_1`` — canonical UPRO + SSO base allocs sum to 1.0.
2. ``test_trend_overlay_redirects_off_component_to_shv`` — a component
   whose price < its SMA-200 has its weight redirected to SHV.
3. ``test_monthly_rebal_date_detection`` — rebal mask marks first
   trading day of each calendar month.
4. ``test_year_end_darf_is_reused_from_b1`` — B3 imports the exact
   same ``apply_darf_year_end`` helper as B1 (no copy).

Citations
---------

* ``[phase3_7_literature_sprint, §T1 paper 3]`` — Pauchlyova allocation.
* ``[leverage_for_the_long_run, p.13-17]`` — Gayed canonical SMA-200 trend.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment prev_weight × ret.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    apply_darf_year_end as b1_apply_darf_year_end,
)
from ai_trade.backtest.strategies.phase3_8_b3_pauchlyova_static_trend import (
    BASE_ALLOCATION_SSO,
    BASE_ALLOCATION_UPRO,
    B3Config,
    apply_darf_year_end as b3_apply_darf_year_end,
    compute_per_component_trend,
    simulate_b3,
    _rebal_day_mask,
)


def test_base_allocation_sums_to_1():
    """Both canonical UPRO and SSO base allocations sum to exactly 1.0."""
    assert abs(sum(BASE_ALLOCATION_UPRO.values()) - 1.0) < 1e-12
    assert abs(sum(BASE_ALLOCATION_SSO.values()) - 1.0) < 1e-12
    # Config __post_init__ must reject a bad allocation.
    import pytest

    with pytest.raises(ValueError, match="base_allocation must sum to 1.0"):
        B3Config(base_allocation={"LETF": 0.5, "TLT": 0.3, "SHV": 0.1})
    # Config default population works for both letf_kind choices.
    c_upro = B3Config(letf_kind="UPRO")
    c_sso = B3Config(letf_kind="SSO")
    assert c_upro.base_allocation == BASE_ALLOCATION_UPRO
    assert c_sso.base_allocation == BASE_ALLOCATION_SSO
    # Leverage property reflects the kind.
    assert c_upro.leverage == 3.0
    assert c_sso.leverage == 2.0


def test_trend_overlay_redirects_off_component_to_shv():
    """A component with close < its SMA-200 must route its weight to SHV.

    Construct a 3-year daily panel where GLD price is in a
    structural downtrend (price < SMA-200) while TLT/SPY/LETF/SHV are
    all flat (price stays > SMA-200). The target allocation on day ``t``
    must show SHV = 10% (base) + 10% (GLD redirect) = 20%, and GLD = 0.
    """
    idx = pd.bdate_range("2020-01-01", "2022-12-31")
    n = len(idx)

    # All trend-filtered assets in a steady uptrend (price > SMA-200 strictly),
    # EXCEPT GLD which steadily declines → price < SMA-200 → off-regime.
    # SHV is always on (no trend filter) so its price is irrelevant.
    up_line = pd.Series(np.linspace(100.0, 200.0, n), index=idx)
    spy_px = up_line.copy()
    tlt_px = up_line.copy()
    letf_px = up_line.copy()
    shv_px = pd.Series(100.0, index=idx)
    # Strong downtrend so price < SMA-200 shortly after warmup.
    gld_px = pd.Series(np.linspace(100.0, 50.0, n), index=idx)

    prices = pd.DataFrame(
        {
            "LETF": letf_px,
            "TLT": tlt_px,
            "SPY": spy_px,
            "GLD": gld_px,
            "SHV": shv_px,
        }
    )
    # Zero returns so we can inspect target weights cleanly.
    returns = pd.DataFrame(0.0, index=idx, columns=prices.columns)

    cfg = B3Config(
        letf_kind="UPRO",
        sma_period=200,
        trend_filter_on=True,
        rebal_cadence="monthly",
        tax_rate=0.0,
    )
    res = simulate_b3(returns, prices, cfg)

    # After warmup + a bit more, GLD should be off-regime and its
    # weight redirected to SHV. Check at the final bar.
    last = res.weights.iloc[-1]
    assert abs(last["GLD"]) < 1e-9, (
        f"expected GLD weight to be redirected, got {last['GLD']:.6f}"
    )
    # SHV holds its own 10% plus the redirected 10% from GLD.
    assert abs(last["SHV"] - 0.20) < 1e-9, (
        f"expected SHV=0.20, got {last['SHV']:.6f}"
    )
    # The other trend-on components are all flat at 100 → their SMA lines
    # up with their close, so (close > SMA) starts False and flips True
    # only after the first post-warmup up-tick. For a *flat* series, the
    # signal will be 0 (not strictly greater) — so the test only pins
    # the GLD-off + SHV-mass conservation property.
    # Weights must still sum to 1.0 (no mass leak).
    assert abs(last.sum() - 1.0) < 1e-9


def test_monthly_rebal_date_detection():
    """``_rebal_day_mask`` identifies the first trading day of each month."""
    idx = pd.bdate_range("2020-01-01", "2020-06-30")
    mask = _rebal_day_mask(idx, "monthly")

    # In pd.bdate_range for 2020-01-01 to 2020-06-30, the first trading
    # day of each month is:
    expected_months = [1, 2, 3, 4, 5, 6]
    rebal_dates = [idx[i] for i, m in enumerate(mask) if m]
    months_actual = sorted({d.month for d in rebal_dates})
    assert months_actual == expected_months, (
        f"expected months {expected_months}, got {months_actual}"
    )
    # Each marked day must be the first trading day of its month.
    by_month = {d.month: d for d in rebal_dates}
    for m, d in by_month.items():
        # There should be no earlier trading day in the same (year, month).
        earlier_same_month = [
            ts
            for ts in idx
            if ts.year == d.year and ts.month == m and ts < d
        ]
        assert earlier_same_month == [], (
            f"rebal date {d.date()} is not the first trading day of month {m}: "
            f"earlier {earlier_same_month}"
        )

    # Quarterly variant triggers only on Jan/Apr/Jul/Oct first bdays.
    qmask = _rebal_day_mask(idx, "quarterly")
    q_rebal_dates = [idx[i] for i, m in enumerate(qmask) if m]
    months_q = sorted({d.month for d in q_rebal_dates})
    assert months_q == [1, 4], (
        f"expected quarterly months [1, 4] in H1 2020, got {months_q}"
    )


def test_year_end_darf_is_reused_from_b1():
    """B3 must import apply_darf_year_end from the B1 module (no copy).

    This guards against a subtle divergence where the orchestrator
    evolves B1 tax semantics and B3 silently forks. Phase 3.8 mandates
    the two strategies apply DARF identically.
    """
    # Identity check on the imported object — same function object.
    assert b3_apply_darf_year_end is b1_apply_darf_year_end, (
        "B3 must reuse the B1 apply_darf_year_end function, not duplicate it"
    )
    # Functional equivalence on a small input.
    idx = pd.bdate_range("2021-01-01", "2023-12-31")
    gross = pd.Series(0.0008, index=idx)
    eq_a, _, tax_a = b1_apply_darf_year_end(gross, tax_rate=0.15)
    eq_b, _, tax_b = b3_apply_darf_year_end(gross, tax_rate=0.15)
    # Since they ARE the same function, equality is trivial — but assert
    # explicitly to make the intent clear.
    assert abs(tax_a - tax_b) < 1e-12
    assert (eq_a - eq_b).abs().max() < 1e-12


def test_simulate_b3_smoke_no_crash_no_trend():
    """A static (trend_filter_on=False) run finishes with normal output.

    Exercises the 'ablation' path — this is one of the 8 PBO cells and
    must not raise. Uses fabricated 3-year data.
    """
    idx = pd.bdate_range("2020-01-01", "2022-12-31")
    rng = np.random.default_rng(42)
    # Modest daily drift per asset so equity paths are well-defined.
    rets = pd.DataFrame(
        rng.normal(0.0002, 0.01, (len(idx), 5)),
        index=idx,
        columns=["LETF", "TLT", "SPY", "GLD", "SHV"],
    )
    # Price = cumprod(1+r) * 100 per asset.
    pxs = (1.0 + rets).cumprod() * 100.0
    cfg = B3Config(
        letf_kind="UPRO",
        sma_period=60,  # shortened to fit our 3y sample
        trend_filter_on=False,
        rebal_cadence="monthly",
        tax_rate=0.15,
    )
    res = simulate_b3(rets, pxs, cfg)
    assert len(res.equity) == len(idx)
    # Weights sum to 1.0 on every rebal day (before drift ambiguity).
    for ts in res.rebalance_dates:
        total = float(res.weights.loc[ts].sum())
        assert abs(total - 1.0) < 1e-6, (
            f"rebal weights at {ts.date()} sum to {total:.6f}"
        )
    # Equity finite + positive.
    assert res.equity.isna().sum() == 0
    assert (res.equity > 0).all()
    # At least one rebal day.
    assert len(res.rebalance_dates) >= 1
