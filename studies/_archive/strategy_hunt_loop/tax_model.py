"""Brazilian offshore-investment tax model (Lei 14.754/2023 regime).

Applies annual mark-to-market 15% taxation on positive year-end variation
of returns. This mirrors the post-2024 BR tax regime for offshore
investments held by individuals (PF).

Conservative assumption: rate=15%, no loss carryforward across years
(losses only offset within the same year). For PJ controlled offshore
entity, the regime differs slightly (allows full carryforward) — not
modeled here.

Also includes one-time entry costs:
  * IOF câmbio
  * FX spread (broker-dependent)
  * IBKR fixed conversion fee
  * ETF bid-ask on initial purchase

Citation: **Lei 14.754/2023** (BR), effective 2024-01-01. See
`docs/investment-mandate.md` §2 for plano-c specific implications.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

LEI_14754_RATE = 0.15  # 15% on annual offshore mark-to-market gain


# --- Annual mark-to-market tax ----------------------------------------------


def apply_annual_mtm_tax(returns: pd.Series, rate: float = LEI_14754_RATE) -> pd.Series:
    """Apply 15%/yr Lei 14.754 mark-to-market tax to a daily returns series.

    Algorithm:
      1. Compute equity curve from daily returns
      2. At each year-end, compute gain = year_end - year_start
      3. If gain > 0: deduct (rate × gain) from the equity (as a one-day
         negative return on the next trading day)
      4. Re-derive daily returns from the post-tax equity

    Loss years pay no tax. Loss does NOT carry forward.

    Returns the post-tax daily returns series, same index.
    """
    if len(returns) < 2:
        return returns.copy()

    eq = (1.0 + returns).cumprod()
    eq.name = returns.name
    # Identify year-end positions
    years = returns.index.year
    year_changes = np.where(np.diff(years) != 0)[0]  # positions of year change
    # Apply tax at each year-end position
    eq_post = eq.copy()
    cum_factor = 1.0  # multiplicative running factor for post-tax adjustment

    last_year_start_eq = eq.iloc[0] / (1.0 + returns.iloc[0])  # roughly initial value
    last_year_start_idx = -1  # before first day

    for change_idx in year_changes:
        year_end_eq = eq_post.iloc[change_idx]
        year_start_eq = (eq_post.iloc[last_year_start_idx]
                         if last_year_start_idx >= 0 else 1.0)
        gain = year_end_eq - year_start_eq
        if gain > 0:
            tax = rate * gain
            tax_factor = 1.0 - (tax / year_end_eq)
            # apply tax on year-end position and propagate to all subsequent
            eq_post.iloc[change_idx:] *= tax_factor
        last_year_start_idx = change_idx

    # Convert post-tax equity back to daily returns
    post_returns = eq_post.pct_change().fillna(returns.iloc[0])
    post_returns.iloc[0] = eq_post.iloc[0] - 1.0
    return post_returns


# --- One-time entry costs ----------------------------------------------------


@dataclass
class EntryCosts:
    """One-time costs for a single BRL→USD remessa + ETF purchase."""

    iof_pct: float = 0.0038       # 0.38% IOF (operação simbólica, Lei 14.754)
    fx_spread_pct: float = 0.0030  # 0.30% TransferBank (use 0.0125 for Inter)
    ibkr_fixed_usd: float = 2.0    # $2 per conversion (zero at Inter)
    etf_bid_ask_pct: float = 0.0002  # 0.02% on broad ETFs (SPY/VTI)

    def total_pct_drag(self, usd_amount: float) -> float:
        """Return total cost as a fraction of the invested USD amount."""
        pct_costs = self.iof_pct + self.fx_spread_pct + self.etf_bid_ask_pct
        fixed_pct = self.ibkr_fixed_usd / usd_amount if usd_amount > 0 else 0
        return pct_costs + fixed_pct


def apply_entry_costs(initial_usd: float, monthly_aporte_usd: float,
                       costs: EntryCosts, n_years: int) -> dict:
    """Compute total cost drag over n_years given a monthly aporte schedule."""
    initial_drag = initial_usd * costs.total_pct_drag(initial_usd)
    monthly_drag_per_aporte = monthly_aporte_usd * costs.total_pct_drag(monthly_aporte_usd)
    total_aporte_drag = monthly_drag_per_aporte * 12 * n_years
    total_invested = initial_usd + monthly_aporte_usd * 12 * n_years
    return {
        "initial_drag_usd": initial_drag,
        "annual_aporte_drag_usd": monthly_drag_per_aporte * 12,
        "total_drag_usd": initial_drag + total_aporte_drag,
        "total_invested_usd": total_invested,
        "drag_pct_of_invested": (initial_drag + total_aporte_drag) / total_invested,
    }


# --- Convenience wrapper -----------------------------------------------------


def post_tax_metrics(returns: pd.Series, rate: float = LEI_14754_RATE) -> dict:
    """Apply Lei 14.754 MTM and return (Sharpe, CAGR, MDD) metrics."""
    post = apply_annual_mtm_tax(returns, rate)
    eq = (1.0 + post).cumprod()
    years = len(post) / 252.0
    sd = post.std(ddof=1)
    sharpe = float(np.sqrt(252) * post.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"sharpe": sharpe, "cagr": cagr, "mdd": mdd, "n_bars": len(post)}


if __name__ == "__main__":
    # Quick sanity check
    rng = np.random.default_rng(42)
    n_days = 252 * 10  # 10 years
    daily_r = pd.Series(rng.normal(0.0005, 0.012, n_days),
                        index=pd.date_range("2015-01-01", periods=n_days, freq="B"))
    pre = post_tax_metrics(daily_r, rate=0.0)  # no tax
    post = post_tax_metrics(daily_r, rate=0.15)
    print(f"Pre-tax:  Sharpe {pre['sharpe']:.3f}  CAGR {pre['cagr']*100:.2f}%  MDD {pre['mdd']*100:.2f}%")
    print(f"Post-tax: Sharpe {post['sharpe']:.3f}  CAGR {post['cagr']*100:.2f}%  MDD {post['mdd']*100:.2f}%")
    print(f"CAGR drag: {(pre['cagr'] - post['cagr'])*100:.2f}pp ({(pre['cagr'] - post['cagr'])/pre['cagr']*100:.1f}% of pre-tax)")
