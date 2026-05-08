#!/usr/bin/env python3
"""Walk-forward portfolio simulation — final G8 test.

For each universe (B4, B2, T1), simulate a portfolio that rebalances monthly
using max-Sharpe weights computed on the prior 5y window. Compare resulting
portfolio metrics (CAGR, MDD, Sharpe) to STATIC.

If walk-forward outperforms static => optimization adds value despite drift.
If static outperforms walk-forward => static is robust (drift doesn't translate
to better realized performance — exactly laurenthu's "weights drift but
structural diversification holds" finding).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

WINDOW_DAYS = 5 * 252
REBAL_DAYS = 21  # monthly


def load_sleeve_history() -> dict[str, pd.Series]:
    sleeves = {}
    for letter in ("a", "b"):
        path = DATA_DIR / f"sleeves_{letter}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        ts = d["response"]["charts"]["history"][0]
        dates = pd.to_datetime(ts, unit="s")
        for i, p in enumerate(d["portfolios"]):
            vals = np.array(d["response"]["charts"]["history"][i + 1], dtype=float)
            sleeves[p["slug"].upper()] = pd.Series(vals, index=dates)
    return sleeves


def max_sharpe(returns: pd.DataFrame) -> np.ndarray:
    n = returns.shape[1]
    mu = returns.mean().values * 252
    cov = returns.cov().values * 252

    def neg_sharpe(w):
        port_vol = np.sqrt(w @ cov @ w)
        if port_vol < 1e-9:
            return 1e9
        return -(w @ mu) / port_vol

    result = minimize(neg_sharpe, np.ones(n) / n, method="SLSQP",
                      constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}],
                      bounds=[(0.0, 1.0)] * n,
                      options={"maxiter": 200, "ftol": 1e-10})
    return result.x if result.success else np.ones(n) / n


def simulate_portfolio(daily_returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Daily-returns to equity curve given fixed weights (no daily rebal — drift)."""
    # For our test we want monthly-rebal: weights reset every REBAL_DAYS
    # but here this function is called per-sub-period. Just return weighted daily returns.
    return daily_returns @ weights


def walkforward_portfolio(returns: pd.DataFrame, sleeves: list[str]) -> pd.Series:
    """Simulate portfolio rebalancing monthly to max-Sharpe weights from prior 5y."""
    n_periods = len(returns)
    portfolio_returns: list[float] = []
    portfolio_index: list[pd.Timestamp] = []

    next_rebal = WINDOW_DAYS
    current_weights = None
    for t in range(WINDOW_DAYS, n_periods):
        if t >= next_rebal:
            window_data = returns.iloc[t - WINDOW_DAYS:t]
            current_weights = max_sharpe(window_data)
            next_rebal = t + REBAL_DAYS
        if current_weights is None:
            continue
        daily_ret = (returns.iloc[t].values * current_weights).sum()
        portfolio_returns.append(daily_ret)
        portfolio_index.append(returns.index[t])

    return pd.Series(portfolio_returns, index=portfolio_index)


def static_portfolio(returns: pd.DataFrame, sleeves: list[str],
                     static_weights: dict[str, float]) -> pd.Series:
    """Static-weight portfolio (no rebal — wait, with monthly rebal for fair comparison).

    For monthly rebal, weights reset every REBAL_DAYS to static target.
    """
    weights_arr = np.array([static_weights[s] for s in sleeves])
    n_periods = len(returns)
    portfolio_returns = []
    for t in range(WINDOW_DAYS, n_periods):
        # Monthly rebal: same weights but compute daily return as weighted return
        # (since we're re-applying weights every day at the daily-return level,
        # this is approximately equivalent to monthly rebal for daily ret aggregation)
        daily_ret = (returns.iloc[t].values * weights_arr).sum()
        portfolio_returns.append(daily_ret)
    return pd.Series(portfolio_returns, index=returns.index[WINDOW_DAYS:])


def compute_metrics(daily_returns: pd.Series, label: str) -> dict:
    cum = (1 + daily_returns).cumprod()
    years = (cum.index[-1] - cum.index[0]).days / 365.25
    cagr = (cum.iloc[-1] ** (1 / years) - 1) * 100
    daily_mean = daily_returns.mean() * 252 * 100
    daily_std = daily_returns.std() * np.sqrt(252) * 100
    sharpe = daily_mean / daily_std if daily_std > 1e-9 else 0.0
    peak = cum.cummax()
    dd = (cum / peak - 1) * 100
    mdd = float(dd.min())
    return {
        "label": label,
        "cagr_pct": float(cagr),
        "mdd_pct": float(mdd),
        "std_pct": float(daily_std),
        "sharpe_raw": float(sharpe),
        "years": float(years),
        "end_val": float(cum.iloc[-1] * 10000),
    }


def main() -> None:
    sleeves = load_sleeve_history()

    universes = {
        "B4": (["NTSX", "GDE", "RSST", "ZROZ"],
               {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.25}),
        "B2": (["NTSX", "GDE", "RSST", "TMF"],
               {"NTSX": 0.30, "GDE": 0.30, "RSST": 0.30, "TMF": 0.10}),
        "T1": (["NTSX", "GDE", "RSST", "TMF"],
               {"NTSX": 0.20, "GDE": 0.35, "RSST": 0.25, "TMF": 0.20}),
    }

    all_results = {}
    for name, (sleeve_list, static_weights) in universes.items():
        print(f"\n{'='*70}\nUniverse: {name}")
        aligned = pd.concat(
            [sleeves[s].rename(s) for s in sleeve_list],
            axis=1, join="inner",
        )
        rets = aligned.pct_change().dropna()
        print(f"  daily returns shape: {rets.shape}")

        wf_rets = walkforward_portfolio(rets, sleeve_list)
        st_rets = static_portfolio(rets, sleeve_list, static_weights)

        # Align (start when both have data — i.e. both starting at WINDOW_DAYS)
        wf_metrics = compute_metrics(wf_rets, f"{name}_walkforward")
        st_metrics = compute_metrics(st_rets, f"{name}_static")

        print(f"  Static {name}:        CAGR={st_metrics['cagr_pct']:.2f}% "
              f"MDD={st_metrics['mdd_pct']:.2f}% Sharpe={st_metrics['sharpe_raw']:.4f}")
        print(f"  Walk-forward {name}:  CAGR={wf_metrics['cagr_pct']:.2f}% "
              f"MDD={wf_metrics['mdd_pct']:.2f}% Sharpe={wf_metrics['sharpe_raw']:.4f}")
        delta_sharpe = wf_metrics['sharpe_raw'] - st_metrics['sharpe_raw']
        delta_cagr = wf_metrics['cagr_pct'] - st_metrics['cagr_pct']
        delta_mdd = wf_metrics['mdd_pct'] - st_metrics['mdd_pct']
        print(f"  Δ:                    CAGR={delta_cagr:+.2f}pp "
              f"MDD={delta_mdd:+.2f}pp Sharpe={delta_sharpe:+.4f}")
        verdict = "static wins" if delta_sharpe < 0 else "walk-forward wins"
        print(f"  Verdict: {verdict}  (Sharpe Δ={delta_sharpe:+.4f})")

        all_results[name] = {
            "static": st_metrics,
            "walkforward": wf_metrics,
            "delta_sharpe": delta_sharpe,
            "delta_cagr": delta_cagr,
            "delta_mdd": delta_mdd,
            "verdict": verdict,
        }

    out = SCRIPT_DIR / "wf_portfolio_results.json"
    out.write_text(json.dumps(all_results, indent=2))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
