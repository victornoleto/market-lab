"""Iter 017 — 12-1 top-1 cross-sectional rotation on 3 regional stacks.

Builds on iter 016's fixed-ratio × vol-target primitive
(``apply_static_stack_vol_managed`` with eq_weight=0.6 / bd_weight=0.4 /
target_vol=0.15 / lookback=21 / max_leverage=2.0). iter 017 adds a
cross-sectional selector: at each monthly rebalance (every 21 trading
days), rank the three regional equity legs by 12-1 skip-a-month
momentum and hold iter 016's primitive on the TOP-1 region's
(equity, bond) pair for the next 21-day window.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve fixed-weight risk-parity stack.
* `[systematic_trading, p.40, ch.2]` — volatility standardisation.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
* `[stocks_on_the_move, p.76-77]` — cross-sectional ranking framework.
* `[ml_for_algo_trading, ch.4, p.86]` — 12-1 skip-a-month canonical.
* `[advances_fin_ml, p.162-164]` — ``σ̂_{t-1}`` + ``momentum_{t-1}`` lag.
* Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling.
* Asness-Moskowitz-Pedersen (2013) "Value and Momentum Everywhere".
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ITER_DIR = Path(__file__).resolve().parent
_ITER_016_DIR = _ITER_DIR.parent / "016-2026-04-24-1729-static-stack-vm-hybrid"
sys.path.insert(0, str(_ITER_016_DIR))

from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402


def compute_12_1_momentum(
    prices: pd.Series,
    *,
    long_window: int = 252,
    skip: int = 21,
) -> pd.Series:
    """12-1 skip-a-month price momentum: ``p[t-skip] / p[t-long_window] - 1``.

    Canonical specification from Jegadeesh-Titman (1993) / Moskowitz-Ooi-
    Pedersen (2012): uses the price ratio over the 12-month window but
    excludes the most recent month (skip=21 bars) to avoid short-term
    reversal. The result at bar ``t`` uses ONLY prices up to bar
    ``t - skip`` (so decision at bar t is lookahead-free by construction
    given lag-1 execution).

    Returns a Series aligned to ``prices.index``, NaN for ``t < long_window``.
    """
    if long_window < 2:
        raise ValueError(f"long_window must be ≥ 2, got {long_window}")
    if skip < 0:
        raise ValueError(f"skip must be ≥ 0, got {skip}")
    if long_window <= skip:
        raise ValueError(
            f"long_window ({long_window}) must be > skip ({skip})"
        )

    # Numerator: price ``skip`` bars before t.
    # Denominator: price ``long_window`` bars before t.
    num = prices.shift(skip)
    den = prices.shift(long_window)
    mom = num / den - 1.0
    mom.name = f"mom_{long_window}_{skip}"
    return mom


def apply_regional_rotation_vm(
    regions: dict[str, pd.DataFrame],
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    long_window: int = 252,
    skip: int = 21,
    rebalance_every: int = 21,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
    switch_cost_bps: float = 0.0002,
) -> dict:
    """12-1 top-1 cross-sectional rotation on iter 016's primitive.

    Parameters
    ----------
    regions : dict[str, pd.DataFrame]
        Region name → DataFrame with columns ``['equity', 'bond']`` of
        daily simple returns. All regions must share the same DatetimeIndex.
    eq_weight, bd_weight : float
        Iter 016's fixed normalised weights (default 0.6, 0.4).
    target_vol, lookback, max_leverage : float, int, float
        Iter 016's vol-target parameters (default 0.15, 21, 2.0).
    long_window, skip : int
        12-1 momentum parameters (default 252, 21).
    rebalance_every : int
        Bars between region re-selections (default 21 = monthly).
    periods_per_year : int
        Annualisation factor (default 252).
    cost_bps_per_leg : float
        Per-bar per-leg transaction cost (default 2 bps, matching iter 016).
    switch_cost_bps : float
        One-off cost applied on region-transition days, as a fraction of
        the full-equity-leg notional at the transition (default 2 bps).

    Returns
    -------
    dict
        ``net`` : pd.Series of portfolio net daily returns.
        ``segments`` : list of per-hold-window dicts (region, start_date,
            length, sharpe within segment).
        ``selection_log`` : pd.Series mapping rebalance date → region.
        ``momentum_log`` : pd.DataFrame of 12-1 momenta at rebalance dates.
        ``turnover_annual_total`` : combined equity+bond turnover per year.
        ``switch_count`` : total region transitions.

    Raises
    ------
    ValueError
        On misaligned indices, invalid params, or insufficient bars.
    """
    if not regions:
        raise ValueError("regions must be non-empty")
    if eq_weight < 0 or bd_weight < 0:
        raise ValueError(
            f"weights must be non-negative; got eq={eq_weight} bd={bd_weight}"
        )
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if long_window < 2:
        raise ValueError(f"long_window must be ≥ 2, got {long_window}")
    if skip < 0:
        raise ValueError(f"skip must be ≥ 0, got {skip}")
    if long_window <= skip:
        raise ValueError(
            f"long_window ({long_window}) must be > skip ({skip})"
        )
    if rebalance_every < 1:
        raise ValueError(
            f"rebalance_every must be ≥ 1, got {rebalance_every}"
        )

    region_names = list(regions.keys())
    first = regions[region_names[0]]
    for name in region_names[1:]:
        if not regions[name].index.equals(first.index):
            raise ValueError(
                f"region {name!r} index does not match {region_names[0]!r}"
            )
        if list(regions[name].columns) != ["equity", "bond"]:
            raise ValueError(
                f"region {name!r} must have columns ['equity','bond']"
            )

    n_bars = len(first)
    min_bars = long_window + lookback + rebalance_every
    if n_bars < min_bars:
        raise ValueError(
            f"need ≥ {min_bars} bars for warmup+rebalance, got {n_bars}"
        )

    # ---- Step 1: run iter 016 primitive on each region independently ----
    per_region_net: dict[str, pd.Series] = {}
    per_region_pos_eq: dict[str, pd.Series] = {}
    per_region_pos_bd: dict[str, pd.Series] = {}
    per_region_scale: dict[str, pd.Series] = {}
    for name, df in regions.items():
        net, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
            df["equity"], df["bond"],
            eq_weight=eq_weight, bd_weight=bd_weight,
            target_vol=target_vol, lookback=lookback,
            max_leverage=max_leverage,
            periods_per_year=periods_per_year,
            cost_bps_per_leg=cost_bps_per_leg,
        )
        per_region_net[name] = net
        per_region_pos_eq[name] = pos_eq
        per_region_pos_bd[name] = pos_bd
        per_region_scale[name] = scale

    # All per-region streams should share the same index (iter 016 drops
    # first ``lookback`` bars identically for each region when data is aligned).
    base_idx = per_region_net[region_names[0]].index
    for name in region_names[1:]:
        if not per_region_net[name].index.equals(base_idx):
            raise ValueError(
                "per-region streams have different indices (should not happen)"
            )

    # ---- Step 2: compute 12-1 momentum per region (on equity PRICE level) ----
    # Reconstruct price level from equity returns (starting from 1.0).
    # `compute_12_1_momentum` uses price ratios shifted by ``skip`` and
    # ``long_window``, so at bar t it uses prices up to t-skip (no lookahead).
    momentum_by_region: dict[str, pd.Series] = {}
    for name, df in regions.items():
        price = (1.0 + df["equity"]).cumprod()
        momentum_by_region[name] = compute_12_1_momentum(
            price, long_window=long_window, skip=skip,
        )

    # ---- Step 3: build selection schedule ----
    # First usable rebalance is the first bar where BOTH the momentum is
    # defined AND the iter 016 primitive has a value (i.e. base_idx bar).
    # Momentum is NaN until bar `long_window - 1` of the original price;
    # base_idx starts at original bar `lookback`. The first valid bar is
    # max(long_window - 1, lookback).
    full_idx = regions[region_names[0]].index
    first_valid_ordinal = max(long_window, lookback + 1)
    # Rebalance dates: starting at first_valid_ordinal, stepping by
    # ``rebalance_every``.
    schedule_ordinals = list(
        range(first_valid_ordinal, len(full_idx), rebalance_every)
    )
    schedule_dates = [full_idx[o] for o in schedule_ordinals]

    # For each rebalance date, pick region with the highest momentum (at t-1
    # or earlier, because momentum series already uses shift(skip) with skip ≥ 1).
    selection_log: dict[pd.Timestamp, str] = {}
    momentum_at_rebalance: dict[pd.Timestamp, dict[str, float]] = {}
    for date in schedule_dates:
        # Use momentum value at date (which reflects prices ≤ date - skip).
        mom_at = {
            name: momentum_by_region[name].loc[date]
            for name in region_names
        }
        # If any momentum is NaN, skip and use first region alphabetically.
        if any(pd.isna(v) for v in mom_at.values()):
            winner = sorted(region_names)[0]
        else:
            # Pick max; tie-break alphabetical.
            sorted_pairs = sorted(
                mom_at.items(), key=lambda kv: (-kv[1], kv[0])
            )
            winner = sorted_pairs[0][0]
        selection_log[date] = winner
        momentum_at_rebalance[date] = mom_at

    # ---- Step 4: concatenate per-window streams, apply switch cost ----
    segments: list[dict] = []
    net_pieces: list[pd.Series] = []
    prev_region: str | None = None

    for i, (date, winner) in enumerate(selection_log.items()):
        # Window: [date, next_rebalance_date)
        if i + 1 < len(schedule_dates):
            next_date = schedule_dates[i + 1]
            window_mask = (
                (per_region_net[winner].index >= date)
                & (per_region_net[winner].index < next_date)
            )
        else:
            window_mask = per_region_net[winner].index >= date
        window_net = per_region_net[winner].loc[window_mask].copy()

        if prev_region is not None and prev_region != winner and len(window_net) > 0:
            # Apply one-off switch cost on the first bar: sell old region's
            # equity notional, buy new region's. Cost is twice the equity
            # leg notional at the transition bar, scaled by switch_cost_bps.
            # Approximate with the new region's pos_eq on the transition bar
            # (full turnover of equity leg).
            t0 = window_net.index[0]
            eq_notional = float(per_region_pos_eq[winner].loc[t0])
            transition_cost = 2.0 * eq_notional * switch_cost_bps
            window_net.iloc[0] = float(window_net.iloc[0]) - transition_cost

        segments.append({
            "region": winner,
            "start_date": str(date.date()),
            "length": int(len(window_net)),
            "end_date": (
                str(window_net.index[-1].date()) if len(window_net) else None
            ),
        })
        net_pieces.append(window_net)
        prev_region = winner

    if not net_pieces:
        raise ValueError("no hold windows produced (check warmup length)")

    net = pd.concat(net_pieces).sort_index()
    net.name = "net"

    # ---- Turnover accounting ----
    # Combine per-window pos_eq / pos_bd into a portfolio-level series.
    pos_eq_portfolio = pd.Series(0.0, index=net.index, dtype=float)
    pos_bd_portfolio = pd.Series(0.0, index=net.index, dtype=float)
    for i, (date, winner) in enumerate(selection_log.items()):
        if i + 1 < len(schedule_dates):
            next_date = schedule_dates[i + 1]
            net_mask = (net.index >= date) & (net.index < next_date)
            src_mask = (
                (per_region_pos_eq[winner].index >= date)
                & (per_region_pos_eq[winner].index < next_date)
            )
        else:
            net_mask = net.index >= date
            src_mask = per_region_pos_eq[winner].index >= date
        pos_eq_portfolio.loc[net_mask] = per_region_pos_eq[winner].loc[src_mask].values
        pos_bd_portfolio.loc[net_mask] = per_region_pos_bd[winner].loc[src_mask].values

    dpos_eq = pos_eq_portfolio.diff().abs().fillna(pos_eq_portfolio.iloc[0])
    dpos_bd = pos_bd_portfolio.diff().abs().fillna(pos_bd_portfolio.iloc[0])
    turnover_eq = float(dpos_eq.sum() * periods_per_year / len(dpos_eq))
    turnover_bd = float(dpos_bd.sum() * periods_per_year / len(dpos_bd))
    turnover_total = turnover_eq + turnover_bd

    switch_count = sum(
        1 for i in range(1, len(segments))
        if segments[i]["region"] != segments[i - 1]["region"]
    )

    return {
        "net": net,
        "segments": segments,
        "selection_log": pd.Series(selection_log, name="region"),
        "momentum_log": pd.DataFrame.from_dict(
            momentum_at_rebalance, orient="index"
        ),
        "pos_eq_portfolio": pos_eq_portfolio,
        "pos_bd_portfolio": pos_bd_portfolio,
        "turnover_annual_per_leg": {"EQ": turnover_eq, "BD": turnover_bd},
        "turnover_annual_total": turnover_total,
        "switch_count": switch_count,
    }
