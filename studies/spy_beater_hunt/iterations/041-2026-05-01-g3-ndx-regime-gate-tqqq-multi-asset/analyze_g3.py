#!/usr/bin/env python3
"""Extract G3 metrics + compare against iter 040 baselines."""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
ITER040_METRICS = Path("/var/www/github/finances/market-lab/studies/spy_beater_hunt/iterations/"
                       "040-2026-05-01-baseline-monthly-rebal-explicit-ers/metrics.json")

VARIANTS = [
    ("g3a_funsundae",       "G3a (Fun-Sundae 33/33/33)"),
    ("g3b_heavy_ndx",       "G3b (NDX-heavy 50/25/25)"),
    ("g3c_with_bonds",      "G3c (with bonds 25/25/25/25)"),
    ("g3d_minimal",         "G3d (minimal 50/50)"),
    ("g3e_gayed_ndx",       "G3e (Gayed-NDX 100/IEF)"),
    ("g3f_pure_tqqq_qqq",   "G3f (pure TQQQ/QQQ swap)"),
]


def main() -> int:
    with open(ITER040_METRICS) as f:
        baseline = json.load(f)

    g3_metrics: dict[str, dict] = {}
    for slug, label in VARIANTS:
        path = DATA_DIR / f"{slug}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        # Find the combined strategy (last in stats, has full descriptive name)
        # Stats[0..N-2] are individual legs + benchmark. Last is the strategy.
        # Identify by name match (full strategy name has "G3" in it).
        strategy_stat = None
        for s in d.get("stats", []):
            if s.get("name", "").startswith("G3"):
                strategy_stat = s
                break
        if strategy_stat is None:
            print(f"warn: no strategy stat found for {slug}")
            continue
        g3_metrics[label] = {
            "cagr": strategy_stat["cagr"],
            "mdd": strategy_stat["max_drawdown"],
            "sharpe": strategy_stat["sharpe"],
            "sortino": strategy_stat["sortino"],
            "calmar": strategy_stat["calmar"],
            "std": strategy_stat["std"],
            "end_val": strategy_stat["end_val"],
        }

    out = SCRIPT_DIR / "metrics.json"
    out.write_text(json.dumps(g3_metrics, indent=2))
    print(f"saved {out}")

    # Pareto comparison
    print("\n" + "=" * 110)
    print(f"{'Strategy':<45} {'CAGR':>8} {'MDD':>9} {'Sharpe':>9} {'Sortino':>9} {'Calmar':>9}")
    print("-" * 110)

    rows = []
    for k, v in baseline.items():
        rows.append({
            "name": k, "kind": "baseline (iter 040)",
            "cagr": v["cagr"], "mdd": v["mdd"],
            "sharpe": v["sharpe"], "sortino": v.get("sortino", 0), "calmar": v.get("calmar", 0),
        })
    for k, v in g3_metrics.items():
        rows.append({
            "name": k, "kind": "G3 (iter 041)",
            "cagr": v["cagr"], "mdd": v["mdd"],
            "sharpe": v["sharpe"], "sortino": v["sortino"], "calmar": v["calmar"],
        })

    # Sort by Sharpe descending
    rows.sort(key=lambda r: -r["sharpe"])
    for r in rows:
        marker = "🆕" if "G3" in r["kind"] else "  "
        print(f"{marker} {r['name']:<43} {r['cagr']:>7.2f}% {r['mdd']:>8.2f}% "
              f"{r['sharpe']:>9.4f} {r['sortino']:>9.4f} {r['calmar']:>9.4f}")
    print("=" * 110)

    # Best G3 vs B4
    best_g3 = max(g3_metrics.items(), key=lambda x: x[1]["sharpe"])
    b4 = baseline["Conservative (B4 ZROZ)"]
    print(f"\nBest G3 variant: {best_g3[0]}")
    print(f"  Sharpe {best_g3[1]['sharpe']:.4f} vs B4 {b4['sharpe']:.4f}  "
          f"(Δ {best_g3[1]['sharpe']-b4['sharpe']:+.4f})")
    print(f"  CAGR {best_g3[1]['cagr']:.2f}% vs B4 {b4['cagr']:.2f}%  "
          f"(Δ {best_g3[1]['cagr']-b4['cagr']:+.2f}pp)")
    print(f"  MDD {best_g3[1]['mdd']:.2f}% vs B4 {b4['mdd']:.2f}%  "
          f"(Δ {best_g3[1]['mdd']-b4['mdd']:+.2f}pp)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
