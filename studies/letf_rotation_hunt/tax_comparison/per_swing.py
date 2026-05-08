"""Model 1 — per-swing 15% tax via FIFO per-asset cost-basis accounting.

Per pre-publication spec §3.2; agent specs were removed from the public tree.

Algorithm (per bar t):
  1. Mark to market: position_value[a] *= (1 + asset_returns[t, a]).
  2. Compute target_value[a] = positions[t, a] * total_nav for each asset.
  3. Process sells (target < current): realize PnL on the reduced portion via
     FIFO proportional cost basis. Tax = 15% × max(0, PnL); deducted from cash.
  4. Process buys (target > current): clamp by available cash; cost basis
     updated to weighted-average of held + new.
  5. Record net_equity[t] = cash + sum(position_value).

Citations:
  - Lei 14.754/2023 (15% flat, no intra-trade loss offset under per-swing).
  - [advances_fin_ml, p.275] — net-of-cost evaluation rationale.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_TAX_RATE = 0.15
DEFAULT_INITIAL_CAPITAL = 10_000.0


def simulate_per_swing(
    positions: pd.DataFrame,
    asset_returns: pd.DataFrame,
    initial_capital: float = DEFAULT_INITIAL_CAPITAL,
    tax_rate: float = DEFAULT_TAX_RATE,
) -> dict:
    """Simulate Model 1 (per-swing tax) on a daily-rebalanced strategy.

    Parameters
    ----------
    positions : pd.DataFrame
        Daily target weights per asset, indexed by date. Columns are assets.
        Each row should sum to <= 1.0 (remainder treated as cash).
    asset_returns : pd.DataFrame
        Daily simple returns per asset, same columns as positions, same index.
    initial_capital : float
        Starting cash balance.
    tax_rate : float
        Flat tax rate on positive realized PnL per swing (default 15%).

    Returns
    -------
    dict with keys:
        - net_equity : pd.Series (date-indexed) — net-of-tax equity curve
        - tax_paid_total : float — total $ deducted as tax
        - n_taxable_swings : int — count of sell events with PnL > 0
    """
    if not positions.index.equals(asset_returns.index):
        raise ValueError("positions and asset_returns must share the same index")
    if not set(positions.columns) == set(asset_returns.columns):
        raise ValueError("positions and asset_returns must have the same columns")

    assets = sorted(positions.columns.tolist())
    cash = float(initial_capital)
    position_value: dict[str, float] = {a: 0.0 for a in assets}
    cost_basis: dict[str, float] = {a: 0.0 for a in assets}
    tax_paid_total = 0.0
    n_taxable_swings = 0

    net_equity = pd.Series(index=positions.index, dtype=float)
    pos_arr = positions[assets].values
    ret_arr = asset_returns[assets].values

    # Convention: positions[t] is set at end of bar t (held going INTO bar t+1)
    # and returns[t] is the return realised during bar t. Therefore the first
    # bar (t=0) is the initial deploy of capital into positions[0]; no return
    # has been earned yet. From bar 1 onward, MTM applies returns[t] against
    # the position held entering bar t (which is positions[t-1] from prior
    # rebalance — captured by the running position_value state).
    #
    # This mirrors the dispatcher's `positions.shift(1) * returns` convention
    # so that net_equity at index t (t >= 1) is comparable date-by-date with
    # `_run_single_*_config(...)['_equity']`.

    for t in range(len(positions)):
        # 1. Mark to market (skip on bar 0 — no return earned on initial deploy)
        if t > 0:
            for i, a in enumerate(assets):
                if position_value[a] > 0:
                    position_value[a] *= 1.0 + ret_arr[t, i]

        # 2. Compute target $ allocation for this bar
        total_nav = cash + sum(position_value.values())
        target = {a: total_nav * float(pos_arr[t, i]) for i, a in enumerate(assets)}

        # 3. Process sells first
        for a in assets:
            current = position_value[a]
            if target[a] < current:
                sold = current - target[a]
                if current > 0:
                    cb_sold = cost_basis[a] * (sold / current)
                else:
                    cb_sold = 0.0
                pnl = sold - cb_sold
                cash += sold
                position_value[a] -= sold
                cost_basis[a] -= cb_sold
                if pnl > 0:
                    tax = tax_rate * pnl
                    cash -= tax
                    tax_paid_total += tax
                    n_taxable_swings += 1

        # 4. Process buys
        for a in assets:
            current = position_value[a]
            if target[a] > current:
                bought = min(target[a] - current, cash)
                cash -= bought
                position_value[a] += bought
                cost_basis[a] += bought

        # 5. Record net equity
        net_equity.iloc[t] = cash + sum(position_value.values())

    return {
        "net_equity": net_equity,
        "tax_paid_total": tax_paid_total,
        "n_taxable_swings": n_taxable_swings,
    }
