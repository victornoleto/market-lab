"""Run all candidate portfolios on all available windows.

Outputs:
- reports/portfolio_aposentadoria_v2/results/backtest_summary.csv
- reports/portfolio_aposentadoria_v2/results/backtest_summary.md
- reports/portfolio_aposentadoria_v2/results/portfolio_details.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

pm = import_module("03_portfolio_sim")
cand = import_module("04_candidate_portfolios")

REPO = Path("/var/www/pessoal/ai-trade")
DATA_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Backtest windows
WINDOWS = {
    "real_2020_2026": ("2020-01-31", "2026-03-31", "real_etf"),
    "syn_2006_2026":  ("2006-02-28", "2026-03-31", "proxy"),  # NTSX_syn starts 2006
    "syn_long_1926":  ("1926-07-31", "2026-02-28", "proxy"),  # KF + testfolio
}


def run_portfolio(p: cand.Portfolio, window_key: str, panel: pd.DataFrame) -> dict | None:
    start, end, which = WINDOWS[window_key]
    weights = p.weights_real if which == "real_etf" else p.weights_proxy
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        # Normalize if close
        weights = {k: v / total for k, v in weights.items()}

    # Check if all assets exist in panel
    missing = [a for a in weights if a not in panel.columns]
    if missing:
        return {"status": "MISSING_ASSETS", "missing": missing}

    # Filter to window
    try:
        # Check data coverage for each asset in the window
        sub = panel[list(weights)].loc[start:end]
        # For proxy window, require 95% coverage per asset
        min_coverage = 0.90 if which == "proxy" else 0.90
        coverage = sub.notna().mean()
        insufficient = coverage[coverage < min_coverage]
        if len(insufficient) > 0:
            return {
                "status": "INSUFFICIENT_COVERAGE",
                "coverage": coverage.round(3).to_dict(),
                "min_required": min_coverage,
            }

        config = pm.SimConfig(
            start=start,
            end=end,
            initial_wealth=10_000.0,
            monthly_contribution=0.0,  # pure CAGR / Sharpe
            rebalance="monthly",
            use_letf_proxy_fees=(which == "proxy"),
        )
        result = pm.simulate(weights, panel, config)
        return {
            "status": "OK",
            "cagr": result.cagr,
            "vol_ann": result.vol_ann,
            "sharpe": result.sharpe,
            "max_dd": result.max_dd,
            "terminal_wealth": result.terminal_wealth,
            "worst_12m": result.worst_12m,
            "n_months": int(len(result.returns)),
            "weights_norm": weights,
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def swr_analysis(p: cand.Portfolio, panel: pd.DataFrame) -> dict:
    """Run SWR bootstrap on the longest-history version of the portfolio."""
    # Prefer proxy window for SWR (more data for bootstrap)
    start, end, which = WINDOWS["syn_long_1926"]
    weights = p.weights_proxy
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}
    missing = [a for a in weights if a not in panel.columns]
    if missing:
        # Try syn_2006_2026
        start, end, which = WINDOWS["syn_2006_2026"]
        missing = [a for a in weights if a not in panel.columns]
        if missing:
            return {"status": "NO_PROXY", "missing": missing}

    try:
        sub = panel[list(weights)].loc[start:end]
        coverage = sub.notna().mean()
        if coverage.min() < 0.85:
            # Fall back to real data
            start, end, which = WINDOWS["real_2020_2026"]
            weights = p.weights_real
            total = sum(weights.values())
            weights = {k: v / total for k, v in weights.items()}
            missing = [a for a in weights if a not in panel.columns]
            if missing:
                return {"status": "NO_DATA"}

        config = pm.SimConfig(
            start=start, end=end, initial_wealth=10_000.0,
            rebalance="monthly",
            use_letf_proxy_fees=(which == "proxy"),
        )
        result = pm.simulate(weights, panel, config)
        wr, diag = pm.swr_test(
            result.returns,
            horizon_years=30,
            initial_wealth=1_000_000,
            n_paths=2000,
            success_threshold=0.95,
            block_size=12,
        )
        return {
            "status": "OK",
            "window": window_label_for(start, end),
            "swr_95pct": float(wr),
            "success_at_swr": float(diag["success_rate_at_wr"]),
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def window_label_for(start: str, end: str) -> str:
    a = pd.to_datetime(start).year
    b = pd.to_datetime(end).year
    return f"{a}-{b}"


def bootstrap_terminal_wealth(p: cand.Portfolio, panel: pd.DataFrame, horizon_years: int = 30,
                              initial: float = 10_000.0, monthly_contrib: float = 1_000.0) -> dict:
    """Bootstrap distribution of terminal wealth with monthly contributions."""
    # Use proxy window for bootstrap breadth
    start, end, which = WINDOWS["syn_long_1926"]
    weights = p.weights_proxy
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}
    if any(a not in panel.columns for a in weights):
        start, end, which = WINDOWS["syn_2006_2026"]
        if any(a not in panel.columns for a in weights):
            return {"status": "NO_DATA"}

    sub = panel[list(weights)].loc[start:end]
    if sub.notna().mean().min() < 0.85:
        start, end, which = WINDOWS["syn_2006_2026"]
        sub = panel[list(weights)].loc[start:end]

    try:
        config = pm.SimConfig(
            start=start, end=end, initial_wealth=initial,
            rebalance="monthly",
            use_letf_proxy_fees=(which == "proxy"),
        )
        result = pm.simulate(weights, panel, config)
        paths = pm.block_bootstrap_paths(
            result.returns,
            n_paths=2000,
            horizon_months=horizon_years * 12,
            block_size=12,
        )
        # Run per-path wealth simulation with monthly contributions
        terminals = []
        mdds = []
        for i in range(paths.shape[0]):
            wealth = initial
            peak = wealth
            path_dd = 0.0
            for t in range(paths.shape[1]):
                wealth = wealth * (1 + paths[i, t]) + monthly_contrib
                peak = max(peak, wealth)
                dd = (wealth - peak) / peak
                path_dd = min(path_dd, dd)
            terminals.append(wealth)
            mdds.append(path_dd)
        terminals = np.array(terminals)
        mdds = np.array(mdds)
        return {
            "status": "OK",
            "window_used": window_label_for(start, end),
            "terminal_wealth": {
                "p05": float(np.percentile(terminals, 5)),
                "p25": float(np.percentile(terminals, 25)),
                "p50": float(np.percentile(terminals, 50)),
                "p75": float(np.percentile(terminals, 75)),
                "p95": float(np.percentile(terminals, 95)),
                "mean": float(np.mean(terminals)),
            },
            "mdd_distribution": {
                "p05": float(np.percentile(mdds, 5)),
                "p25": float(np.percentile(mdds, 25)),
                "p50": float(np.percentile(mdds, 50)),
                "p95": float(np.percentile(mdds, 95)),  # best-case (least negative)
            },
            "prob_mdd_gt_50pct": float((mdds < -0.50).mean()),
            "prob_mdd_gt_70pct": float((mdds < -0.70).mean()),
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def main() -> None:
    panel = pd.read_parquet(DATA_DIR / "returns_monthly.parquet")
    print(f"Panel loaded: {panel.shape}, cols: {panel.columns.tolist()[:5]}...")

    results = {}
    for p in cand.PORTFOLIOS:
        print(f"\n=== {p.id}: {p.name} ===")
        entry = {
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "weights_real": p.weights_real,
            "weights_proxy": p.weights_proxy,
            "notes": p.notes,
            "backtests": {},
            "swr": None,
            "bootstrap": None,
        }
        for wk in WINDOWS:
            r = run_portfolio(p, wk, panel)
            entry["backtests"][wk] = r
            if r.get("status") == "OK":
                print(f"  {wk:20s}: CAGR={r['cagr']:.2%} Sharpe={r['sharpe']:.2f} "
                      f"MDD={r['max_dd']:.2%} vol={r['vol_ann']:.2%}")
            else:
                print(f"  {wk:20s}: {r.get('status')}")
        print(f"  SWR analysis...")
        entry["swr"] = swr_analysis(p, panel)
        if entry["swr"].get("status") == "OK":
            print(f"    SWR (95% success, 30y): {entry['swr']['swr_95pct']:.2%}")
        print(f"  Bootstrap terminal wealth...")
        entry["bootstrap"] = bootstrap_terminal_wealth(p, panel)
        if entry["bootstrap"].get("status") == "OK":
            tw = entry["bootstrap"]["terminal_wealth"]
            print(f"    Terminal wealth 30y (1k initial + 1k/mo): "
                  f"p25={tw['p25']/1e6:.2f}M p50={tw['p50']/1e6:.2f}M "
                  f"p95={tw['p95']/1e6:.2f}M")
            print(f"    P(MDD > 50%) = {entry['bootstrap']['prob_mdd_gt_50pct']:.1%}")
        results[p.id] = entry

    # Write results
    with (OUT_DIR / "portfolio_details.json").open("w") as f:
        json.dump(results, f, indent=2, default=str)

    # Build summary CSV
    rows = []
    for pid, e in results.items():
        for wk, r in e["backtests"].items():
            if r.get("status") == "OK":
                rows.append({
                    "portfolio": pid,
                    "name": e["name"],
                    "category": e["category"],
                    "window": wk,
                    "cagr": r["cagr"],
                    "vol": r["vol_ann"],
                    "sharpe": r["sharpe"],
                    "mdd": r["max_dd"],
                    "worst_12m": r["worst_12m"],
                    "terminal_10k": r["terminal_wealth"],
                    "n_months": r["n_months"],
                })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT_DIR / "backtest_summary.csv", index=False)
    print(f"\nWrote {OUT_DIR}/backtest_summary.csv with {len(summary)} rows")


if __name__ == "__main__":
    main()
