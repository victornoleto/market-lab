"""Iter 062 — Internal-LETF UPRO substitution preserving equity exposure.

Two pieces:

1. **Synth-UPRO** daily returns from SPY: r_synth_UPRO[t] = 3·r_SPY[t]
   - daily_expense, where daily_expense = expense_ratio / 252. The
   project's `_sharpe()` uses rf=0 convention, so we omit the swap-
   funding spread (T-bill + 0.95%) for the synth pre-real-inception
   series — consistent with iter 037 measuring SPY at rf=0. The real
   UPRO data from 2009-06-25 onward already has the swap-funding
   spread + expense ratio baked into the price path; we use real UPRO
   from inception forward and synth UPRO before. Hsiao & Williams
   (2017) daily-reset LETF formula `[leverage_for_the_long_run, p.20-25]`.

2. **3-leg static stack** at preserved 1.50× total NAV with weights
   0.20 UPRO + 0.65 IEF + 0.65 GLD. This preserves the SPY-equivalent
   equity exposure of iter 037's 0.60 (since 0.20 × 3 = 0.60) while
   doubling-down on the bond/gold diversifier legs. The 3-leg primitive
   is reused verbatim from iter 037's `apply_static_stack_3leg`
   (vendored under this iter for clarity); we just pass UPRO returns
   instead of SPY returns.

Citations
---------
* `[leverage_for_the_long_run, p.19-25]` — Hsiao & Williams 2017
  preserved-leverage zone + daily-reset LETF formula.
* `[risk_parity, ch.5]` — multi-leg risk-parity at preserved total
  leverage; bond/gold diversifier overweight reuses iter 037 architecture.
* `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082, static
  fixed-weight stack mechanism.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule (vacuous
  for static weights and prior-day-only synth formula).
* ProShares UPRO prospectus 2024-25 — expense ratio 0.91%/yr.
"""

from __future__ import annotations

import pandas as pd


# Default UPRO expense ratio per ProShares 2024-25 prospectus.
UPRO_EXPENSE_RATIO_DEFAULT = 0.0091
LETF_LEVERAGE_DEFAULT = 3.0


def synth_upro_returns(
    r_spy: pd.Series,
    *,
    leverage: float = LETF_LEVERAGE_DEFAULT,
    expense_ratio: float = UPRO_EXPENSE_RATIO_DEFAULT,
) -> pd.Series:
    """Synthetic daily-reset 3× LETF returns from SPY daily returns.

    Formula (rf=0 convention, project default)::

        r_synth_UPRO[t] = leverage · r_SPY[t] - expense_ratio / 252

    The swap-funding spread (T-bill + 0.95% per ProShares prospectus)
    is omitted because the project's `_sharpe()` uses rf=0 — consistent
    with iter 037 measuring SPY at rf=0 (its implicit rf=0 borrow on
    margin is also invisible). This formula matches Hsiao-Williams
    (2017) Eq. 1 with rf set to zero.

    Parameters
    ----------
    r_spy : pd.Series
        Daily simple returns of SPY (or similar 1× equity series),
        indexed by date.
    leverage : float, default 3.0
        Target daily leverage multiple (UPRO = 3, SSO = 2).
    expense_ratio : float, default 0.0091
        Annual expense ratio expressed as a decimal (UPRO = 0.91% / yr).

    Returns
    -------
    pd.Series
        Daily synth-LETF returns aligned to ``r_spy.index``.

    Raises
    ------
    ValueError
        If ``leverage`` ≤ 0 or ``expense_ratio`` < 0.
    """
    if leverage <= 0:
        raise ValueError(f"leverage must be > 0; got {leverage}")
    if expense_ratio < 0:
        raise ValueError(f"expense_ratio must be ≥ 0; got {expense_ratio}")
    daily_expense = expense_ratio / 252.0
    out = leverage * r_spy.astype(float) - daily_expense
    out.name = "synth_LETF"
    out.index = r_spy.index
    return out


def join_real_and_synth_letf(
    r_spy: pd.Series,
    r_real_letf: pd.Series,
    *,
    leverage: float = LETF_LEVERAGE_DEFAULT,
    expense_ratio: float = UPRO_EXPENSE_RATIO_DEFAULT,
) -> pd.Series:
    """Join real LETF returns with synth LETF returns derived from SPY pre-inception.

    Returns a series spanning ``r_spy.index`` where dates strictly
    before ``r_real_letf.index[0]`` use the synth formula and dates
    on/after that boundary use the real LETF data (which has all
    swap funding + expense baked in). The boundary day uses real data.

    Parameters
    ----------
    r_spy : pd.Series
        SPY daily returns over the FULL desired window (inclusive).
    r_real_letf : pd.Series
        Real LETF daily returns from inception onward. Must be a
        subset (date-wise) of r_spy.
    leverage, expense_ratio : floats
        Forwarded to ``synth_upro_returns``.

    Returns
    -------
    pd.Series
        Joined daily LETF return series spanning the union of indexes,
        sorted by date. No overlap; real data takes precedence at the
        boundary.

    Raises
    ------
    ValueError
        If r_real_letf is empty, or if ``r_real_letf.index[0]`` is not
        within ``r_spy.index`` range.
    """
    if len(r_real_letf) == 0:
        raise ValueError("r_real_letf must be non-empty")
    if r_spy.index.min() > r_real_letf.index.min():
        raise ValueError(
            "r_spy must start on or before r_real_letf inception "
            f"(spy starts {r_spy.index.min()}, letf starts {r_real_letf.index.min()})"
        )

    real_start = r_real_letf.index[0]
    synth = synth_upro_returns(
        r_spy, leverage=leverage, expense_ratio=expense_ratio,
    )
    pre = synth.loc[synth.index < real_start]
    real = r_real_letf.loc[r_real_letf.index >= real_start]
    joined = pd.concat([pre, real]).sort_index()
    joined.name = "joined_LETF"
    return joined


def apply_static_stack_3leg(
    r_eq: pd.Series,
    r_bd_short: pd.Series,
    r_bd_long: pd.Series,
    *,
    eq_w: float = 0.20,
    bd_short_w: float = 0.65,
    bd_long_w: float = 0.65,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Three-leg static return-stack with daily-rebalanced fixed weights.

    Vendored verbatim from iter 037's primitive. Default weights are
    iter 062's pre-committed cfg (0.20 UPRO + 0.65 IEF + 0.65 GLD,
    total 1.50 NAV — preserves iter 037's total leverage while
    re-allocating notional to diversifier legs).

    Reduces to iter 037's canonical stack when called with weights
    (0.60, 0.45, 0.45) — verified by regression test.

    Parameters
    ----------
    r_eq, r_bd_short, r_bd_long : pd.Series
        Aligned daily simple-return streams. Must share identical
        DatetimeIndex.
    eq_w, bd_short_w, bd_long_w : float
        Per-leg fixed weights. Defaults: 0.20 / 0.65 / 0.65 (iter 062).
    cost_bps_per_leg : float
        Linear cost per unit of per-leg position change. Default 2 bps.

    Returns
    -------
    (net_returns, positions_df, scale)
    """
    if eq_w < 0 or bd_short_w < 0 or bd_long_w < 0:
        raise ValueError(
            f"weights must be non-negative; got eq={eq_w} bd_s={bd_short_w} bd_l={bd_long_w}"
        )
    if not (r_eq.index.equals(r_bd_short.index) and r_eq.index.equals(r_bd_long.index)):
        raise ValueError(
            "r_eq, r_bd_short, r_bd_long must share identical indices "
            f"(eq={len(r_eq)}, bd_s={len(r_bd_short)}, bd_l={len(r_bd_long)})"
        )

    a = r_eq.astype(float)
    b = r_bd_short.astype(float)
    c = r_bd_long.astype(float)
    mask = a.notna() & b.notna() & c.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    c = c.loc[mask]
    if len(a) == 0:
        raise ValueError("no overlapping non-NaN bars across the three return streams")

    idx = a.index
    pos_eq = pd.Series(eq_w, index=idx, dtype=float)
    pos_bd_s = pd.Series(bd_short_w, index=idx, dtype=float)
    pos_bd_l = pd.Series(bd_long_w, index=idx, dtype=float)
    scale = pos_eq + pos_bd_s + pos_bd_l
    scale.name = "scale"

    gross = pos_eq * a + pos_bd_s * b + pos_bd_l * c

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_s = pos_bd_s.diff().abs().fillna(pos_bd_s.iloc[0])
    dpos_l = pos_bd_l.diff().abs().fillna(pos_bd_l.iloc[0])
    cost = (dpos_eq + dpos_s + dpos_l) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame(
        {"EQ": pos_eq, "BD_S": pos_bd_s, "BD_L": pos_bd_l}, index=idx,
    )
    return net, positions, scale
