"""Iter 022 — Turn-of-Month (TOM) seasonality overlay on iter 016 base.

Generalises iter 016's ``apply_static_stack_vol_managed`` so that the
equity / bond per-leg weights switch between two preset regimes driven
by a calendar flag (TOM window = last N + first M business days of
each month). On non-TOM bars the primitive uses ``eq_weight_mid /
bd_weight_mid``; on TOM bars it uses ``eq_weight_tom / bd_weight_tom``.

The σ̂²_{t-1} machinery is unchanged from iter 016 — variance is
computed on the unconditional return stream, shifted one bar. Only the
per-leg weights become time-varying. When
``eq_weight_tom == eq_weight_mid`` and
``bd_weight_tom == bd_weight_mid`` the primitive reproduces iter 016
exactly (asserted in tests).

Mechanism rationale
-------------------

Empirically (Lakonishok-Smidt 1988; Etula et al 2020 JF; Kunkel et al
2003) the last 3 + first 3 business days of each month capture a
structurally-disproportionate share of monthly equity returns due to
institutional liquidity-sensitive flows (pension rebalancing, Treasury
auction settlements, month-end marking). This conditional drift
premium is **orthogonal to σ²_port** — it is a calendar property of
the bar, not a variance property — and is therefore expected to
survive the variance-target scale feedback that locked iter 020/021
to Sharpe parity.

Citations
---------
* `[trading_systems_methods, p.479-481]` — turn-of-month / holiday /
  Hirsch strategies (Kaufman, 2013).
* `[trading_systems_methods, p.418]` — seasonal/calendar primitive catalog.
* `[risk_parity, p.10-11, ch.1]` — iter 016 static-stack base.
* `[systematic_trading, p.40, ch.2]` — volatility standardisation
  primitive (inherited unchanged).
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline.
* Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling.

Papers:
* Lakonishok & Smidt (1988) RFS 1(4), 403-425 — original TOM study.
* Etula, Rinne, Suominen & Vaittinen (2020) JF 75(6), 3157-3203 —
  institutional-flow mechanism.
* Kunkel, Compton & Beyer (2003) IRFA 12(2), 207-221 — post-2000
  persistence, 19-country evidence.
* Ariel (1987) JFE 18(1), 161-174 — seminal monthly effect.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_tom_flag(
    index: pd.DatetimeIndex,
    *,
    last_n: int = 3,
    first_n: int = 3,
) -> pd.Series:
    """Return a boolean Series indicating TOM bars on the given index.

    A bar is TOM if its calendar position within its (year, month) is
    either within the last ``last_n`` or the first ``first_n`` bars of
    that month. Uses rank from both ends, so months with any number of
    business days get the correct window.

    Parameters
    ----------
    index : pd.DatetimeIndex
        Trading-day index to annotate.
    last_n : int
        Number of bars at the end of each month to flag (default 3).
    first_n : int
        Number of bars at the start of each month to flag (default 3).

    Returns
    -------
    pd.Series[bool]
        Same index as input, True on TOM bars.
    """
    if last_n < 0 or first_n < 0:
        raise ValueError(f"last_n/first_n must be ≥ 0; got {last_n}/{first_n}")

    # Compute the canonical (calendar) set of business days for each month
    # touched by the index, and rank each input bar against it. This is
    # robust to index subsetting (e.g. a backtest that starts mid-month)
    # and matches "turn of calendar month" semantics.
    idx = pd.DatetimeIndex(index)
    flags = np.zeros(len(idx), dtype=bool)
    yms = set(zip(idx.year.tolist(), idx.month.tolist()))
    # Cache ym → (first_n_days, last_n_days) as Timestamp sets.
    month_windows: dict[tuple[int, int], tuple[set, set]] = {}
    for y, m in yms:
        start = pd.Timestamp(year=y, month=m, day=1)
        end = start + pd.offsets.MonthEnd(1)
        bdays = pd.bdate_range(start, end)
        first_set = set(bdays[:first_n]) if first_n > 0 else set()
        last_set = set(bdays[-last_n:]) if last_n > 0 else set()
        month_windows[(y, m)] = (first_set, last_set)
    for i, ts in enumerate(idx):
        first_set, last_set = month_windows[(ts.year, ts.month)]
        if ts in first_set or ts in last_set:
            flags[i] = True
    out = pd.Series(flags, index=idx, name="is_tom")
    return out


def apply_tom_static_stack_vm(
    r_eq: pd.Series,
    r_bd: pd.Series,
    *,
    eq_weight_tom: float,
    eq_weight_mid: float,
    bd_weight_tom: float,
    bd_weight_mid: float,
    tom_last_n: int,
    tom_first_n: int,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Two-leg stack with TOM-conditional weights + iter-016 vol-target.

    Weights switch between (eq_weight_tom, bd_weight_tom) and
    (eq_weight_mid, bd_weight_mid) based on a calendar TOM flag. The
    variance-target scale computes σ²_port[t-1] using the PROJECTED
    weights at bar t — i.e. the σ² that the portfolio will realise
    today given today's weights, estimated from yesterday's per-leg
    σ̂². This keeps the scale consistent with today's actual exposure.

    Parameters
    ----------
    r_eq, r_bd : pd.Series
        Aligned daily simple-return streams. Must share the same index.
    eq_weight_tom, eq_weight_mid : float
        Equity weights for TOM and mid-month bars respectively. Must
        be non-negative.
    bd_weight_tom, bd_weight_mid : float
        Bond weights for TOM and mid-month bars respectively. Must be
        non-negative. Each (tom_pair) and (mid_pair) must sum to > 0;
        they are normalised internally so the pair sums to 1.
    tom_last_n, tom_first_n : int
        TOM window — last_n + first_n business days of each month.
    target_vol : float
        Target annualised portfolio volatility (e.g. 0.15 for 15%).
    lookback : int
        Rolling window for σ̂² (≥ 2).
    max_leverage : float
        Upper bound on total gross exposure scale[t] (> 0).
    periods_per_year : int
        Annualisation factor. Default 252.
    cost_bps_per_leg : float
        Per-leg transaction cost per unit ∆position. Default 2 bps.

    Returns
    -------
    (net_returns, pos_eq, pos_bd, scale, tom_flag)
        All indexed on valid bars (first ``lookback`` dropped).

    Raises
    ------
    ValueError
        If params are out of domain, indices misaligned, or fewer than
        ``lookback + 1`` overlapping bars.
    """
    if any(
        w < 0
        for w in (eq_weight_tom, eq_weight_mid, bd_weight_tom, bd_weight_mid)
    ):
        raise ValueError("all weights must be non-negative")
    if (eq_weight_tom + bd_weight_tom) <= 0:
        raise ValueError("tom-window weights must sum to > 0")
    if (eq_weight_mid + bd_weight_mid) <= 0:
        raise ValueError("mid-window weights must sum to > 0")
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if not r_eq.index.equals(r_bd.index):
        raise ValueError(
            "r_eq and r_bd must share the same index "
            f"(eq {len(r_eq)} bars vs bd {len(r_bd)} bars)"
        )

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    mask = a.notna() & b.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    if len(a) <= lookback:
        raise ValueError(f"need > {lookback} overlapping bars, got {len(a)}")

    # Normalise weight pairs.
    sum_tom = eq_weight_tom + bd_weight_tom
    sum_mid = eq_weight_mid + bd_weight_mid
    w_eq_tom = eq_weight_tom / sum_tom
    w_bd_tom = bd_weight_tom / sum_tom
    w_eq_mid = eq_weight_mid / sum_mid
    w_bd_mid = bd_weight_mid / sum_mid

    # TOM flag on the valid (post-mask) index.
    tom_full = compute_tom_flag(a.index, last_n=tom_last_n, first_n=tom_first_n)

    # Per-bar weights.
    w_eq = pd.Series(
        np.where(tom_full.to_numpy(), w_eq_tom, w_eq_mid),
        index=a.index, dtype=float,
    )
    w_bd = pd.Series(
        np.where(tom_full.to_numpy(), w_bd_tom, w_bd_mid),
        index=a.index, dtype=float,
    )

    # Rolling σ̂² lagged by 1 bar (same as iter 016).
    ann_var_eq = (
        a.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_var_bd = (
        b.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_cov = (
        a.rolling(lookback, min_periods=lookback).cov(b, ddof=0)
        * periods_per_year
    ).shift(1)

    # σ²_port[t] with the PROJECTED weights for bar t (known ex-ante
    # from calendar), using yesterday's per-leg σ̂².
    ann_var_port = (
        w_eq ** 2 * ann_var_eq
        + w_bd ** 2 * ann_var_bd
        + 2.0 * w_eq * w_bd * ann_cov
    ).clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=a.index, dtype=float)
    mask_valid = ann_var_port.notna()
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage
    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()

    pos_eq = (scale * w_eq.loc[scale.index]).astype(float)
    pos_bd = (scale * w_bd.loc[scale.index]).astype(float)

    a_v = a.loc[scale.index]
    b_v = b.loc[scale.index]
    gross = pos_eq * a_v + pos_bd * b_v

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    tom_out = tom_full.loc[scale.index]
    net.name = "net"
    pos_eq.name = "pos_eq"
    pos_bd.name = "pos_bd"
    scale.name = "scale"
    tom_out.name = "tom"
    return net, pos_eq, pos_bd, scale, tom_out
