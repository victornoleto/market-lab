#!/usr/bin/env python3
"""Extract iter 040 metrics + compare with iter 039 (Yearly, no ER).

Iter 039 metrics source: /tmp/testfolio_metrics_common_start.json
Iter 040 metrics source: testfolio_data/*.json (this dir)

Outputs:
  - metrics.json — iter 040 normalized metrics (CAGR, MDD, Sharpe, std, end_val)
  - comparison.json — iter 039 vs 040 deltas
  - SUMMARY.md — human-readable comparison report
"""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
ITER039_DATA = Path("/var/www/pessoal/ai-trade/studies/spy_beater_hunt/iterations/"
                    "039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack/testfolio_data")

# Slug -> human-readable name (matches iter 039 naming for delta comparison)
NAME_MAP = {
    "spy_1x": "SPY 1x",
    "popular_50_25_25": "Popular 50/25/25 SSO/GLD/ZROZ",
    "l1_sleeping_pills": "Sleeping Pills (L1 CEGB)",
    "l2_bogleheads": "Bogleheads 67 NTSX (L2)",
    "b4_conservative": "Conservative (B4 ZROZ)",
    "b2_balanced": "Balanced (B2)",
    "t1_aggressive": "Aggressive (T1)",
}


def load_iter039_metrics() -> dict:
    """Extract iter 039 buy-hold + LRS metrics directly from testfolio raw responses.

    Avoids /tmp/testfolio_metrics_common_start.json which had recomputed Sharpes
    (different from testfolio's native Rf-adjusted Sharpe).
    """
    out: dict[str, dict] = {}
    for letter in ("a", "b"):
        path = ITER039_DATA / f"backtest_buyhold_{letter}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        for portfolio, stat in zip(d["portfolios"], d["response"]["stats"]):
            name = NAME_MAP[portfolio["slug"]]
            out[name] = {
                "cagr": stat["cagr"],
                "mdd": stat["max_drawdown"],
                "sharpe": stat["sharpe"],
                "std": stat["std"],
                "end_val": stat["end_val"],
            }
    # LRS from tactical responses
    for slug, key in (("tactical_lrs_sso", "Gayed LRS 2x (SSO 200d)"),
                      ("tactical_lrs_upro", "Gayed LRS 3x (UPRO 200d)")):
        path = ITER039_DATA / f"{slug}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        s = d["stats"][3]
        out[key] = {
            "cagr": s["cagr"],
            "mdd": s["max_drawdown"],
            "sharpe": s["sharpe"],
            "std": s["std"],
            "end_val": s["end_val"],
        }
    return out


def extract_iter040_buyhold() -> dict:
    """Read both batch JSONs, build {name -> {cagr, mdd, sharpe, std, end_val}}."""
    out: dict[str, dict] = {}
    for letter in ("a", "b"):
        path = DATA_DIR / f"backtest_buyhold_{letter}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        for portfolio, stat in zip(d["portfolios"], d["response"]["stats"]):
            name = NAME_MAP[portfolio["slug"]]
            out[name] = {
                "cagr": stat["cagr"],
                "mdd": stat["max_drawdown"],
                "sharpe": stat["sharpe"],
                "sortino": stat["sortino"],
                "calmar": stat["calmar"],
                "std": stat["std"],
                "end_val": stat["end_val"],
                "drag_pct": portfolio["drag_pct"],
                "rebalance_freq": portfolio["rebalance_freq"],
            }
    return out


def extract_iter040_lrs() -> dict:
    """Both LRS files have the LRS strategy at stats[3]."""
    out: dict[str, dict] = {}
    for slug, key in (("tactical_lrs_sso", "Gayed LRS 2x (SSO 200d)"),
                      ("tactical_lrs_upro", "Gayed LRS 3x (UPRO 200d)")):
        path = DATA_DIR / f"{slug}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        s = d["stats"][3]
        out[key] = {
            "cagr": s["cagr"],
            "mdd": s["max_drawdown"],
            "sharpe": s["sharpe"],
            "sortino": s["sortino"],
            "calmar": s["calmar"],
            "std": s["std"],
            "end_val": s["end_val"],
            "drag_pct": "leg_drag_only",   # ERs applied per allocation_leg, not portfolio drag
            "rebalance_freq": "Daily (signal-driven)",
        }
    return out


def main() -> int:
    iter039 = load_iter039_metrics()
    iter040 = {**extract_iter040_buyhold(), **extract_iter040_lrs()}

    metrics_out = SCRIPT_DIR / "metrics.json"
    metrics_out.write_text(json.dumps(iter040, indent=2))
    print(f"saved {metrics_out}")

    # Build comparison
    rows = []
    for name in [
        "SPY 1x",
        "Popular 50/25/25 SSO/GLD/ZROZ",
        "Sleeping Pills (L1 CEGB)",
        "Bogleheads 67 NTSX (L2)",
        "Conservative (B4 ZROZ)",
        "Balanced (B2)",
        "Aggressive (T1)",
        "Gayed LRS 2x (SSO 200d)",
        "Gayed LRS 3x (UPRO 200d)",
    ]:
        a = iter039.get(name)
        b = iter040.get(name)
        if not a:
            # iter 039 didn't have LRS metrics in /tmp file (only buy-hold);
            # use placeholder from Reddit Post 1 if needed
            a = None
        if not b:
            continue
        if a:
            row = {
                "name": name,
                "iter039_cagr": round(a["cagr"], 2),
                "iter040_cagr": round(b["cagr"], 2),
                "delta_cagr": round(b["cagr"] - a["cagr"], 2),
                "iter039_mdd": round(a["mdd"], 2),
                "iter040_mdd": round(b["mdd"], 2),
                "delta_mdd": round(b["mdd"] - a["mdd"], 2),
                "iter039_sharpe": round(a["sharpe"], 3),
                "iter040_sharpe": round(b["sharpe"], 3),
                "delta_sharpe": round(b["sharpe"] - a["sharpe"], 3),
                "drag_pct": b["drag_pct"],
                "rebalance_freq": b["rebalance_freq"],
            }
        else:
            row = {
                "name": name,
                "iter039_cagr": "N/A",
                "iter040_cagr": round(b["cagr"], 2),
                "delta_cagr": "N/A",
                "iter039_mdd": "N/A",
                "iter040_mdd": round(b["mdd"], 2),
                "delta_mdd": "N/A",
                "iter039_sharpe": "N/A",
                "iter040_sharpe": round(b["sharpe"], 3),
                "delta_sharpe": "N/A",
                "drag_pct": b["drag_pct"],
                "rebalance_freq": b["rebalance_freq"],
            }
        rows.append(row)

    comparison_out = SCRIPT_DIR / "comparison.json"
    comparison_out.write_text(json.dumps(rows, indent=2))
    print(f"saved {comparison_out}")

    # Print formatted
    print("\n" + "=" * 130)
    print(f"{'Portfolio':<35} {'CAGR_039':>9} {'CAGR_040':>9} {'ΔCAGR':>7} | "
          f"{'MDD_039':>9} {'MDD_040':>9} {'ΔMDD':>7} | "
          f"{'Sh_039':>7} {'Sh_040':>7} {'ΔSh':>7}")
    print("-" * 130)
    for r in rows:
        print(f"{r['name']:<35} "
              f"{r['iter039_cagr']!s:>9} {r['iter040_cagr']!s:>9} {r['delta_cagr']!s:>7} | "
              f"{r['iter039_mdd']!s:>9} {r['iter040_mdd']!s:>9} {r['delta_mdd']!s:>7} | "
              f"{r['iter039_sharpe']!s:>7} {r['iter040_sharpe']!s:>7} {r['delta_sharpe']!s:>7}")
    print("=" * 130)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
