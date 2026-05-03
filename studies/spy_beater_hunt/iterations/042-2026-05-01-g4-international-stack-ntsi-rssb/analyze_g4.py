#!/usr/bin/env python3
"""Extract G4 metrics + compare against iter 040 baselines."""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
ITER040_METRICS = Path("/var/www/pessoal/ai-trade/studies/spy_beater_hunt/iterations/"
                       "040-2026-05-01-baseline-monthly-rebal-explicit-ers/metrics.json")


def main() -> int:
    with open(ITER040_METRICS) as f:
        baseline = json.load(f)

    with open(DATA_DIR / "backtest_g4.json") as f:
        d = json.load(f)

    g4_metrics: dict[str, dict] = {}
    for portfolio, stat in zip(d["portfolios"], d["response"]["stats"]):
        slug = portfolio["slug"]
        # Use a clean label
        label_map = {
            "g4a_ntsd_swap": "G4a (NTSD swap)",
            "g4b_rssb_heavy": "G4b (RSSB-heavy)",
            "g4c_mixed_us_intl": "G4c (mixed US/Intl)",
            "g4d_global_4sleeve": "G4d (4-sleeve global)",
            "g4e_full_intl": "G4e (full intl)",
        }
        g4_metrics[label_map[slug]] = {
            "cagr": stat["cagr"], "mdd": stat["max_drawdown"],
            "sharpe": stat["sharpe"], "sortino": stat["sortino"],
            "calmar": stat["calmar"], "std": stat["std"],
            "end_val": stat["end_val"],
        }

    out = SCRIPT_DIR / "metrics.json"
    out.write_text(json.dumps(g4_metrics, indent=2))
    print(f"saved {out}")

    rows = []
    for k, v in baseline.items():
        rows.append({
            "name": k, "kind": "baseline (iter 040)",
            "cagr": v["cagr"], "mdd": v["mdd"],
            "sharpe": v["sharpe"], "sortino": v.get("sortino", 0),
            "calmar": v.get("calmar", 0),
        })
    for k, v in g4_metrics.items():
        rows.append({
            "name": k, "kind": "G4 (iter 042)",
            "cagr": v["cagr"], "mdd": v["mdd"],
            "sharpe": v["sharpe"], "sortino": v["sortino"],
            "calmar": v["calmar"],
        })

    rows.sort(key=lambda r: -r["sharpe"])

    print("\n" + "=" * 110)
    print(f"{'Strategy':<45} {'CAGR':>8} {'MDD':>9} {'Sharpe':>9} {'Sortino':>9} {'Calmar':>9}")
    print("-" * 110)
    for r in rows:
        marker = "🆕" if "G4" in r["kind"] else "  "
        print(f"{marker} {r['name']:<43} {r['cagr']:>7.2f}% {r['mdd']:>8.2f}% "
              f"{r['sharpe']:>9.4f} {r['sortino']:>9.4f} {r['calmar']:>9.4f}")
    print("=" * 110)

    best_g4 = max(g4_metrics.items(), key=lambda x: x[1]["sharpe"])
    b4 = baseline["Conservative (B4 ZROZ)"]
    print(f"\nBest G4 (by Sharpe): {best_g4[0]}")
    print(f"  Sharpe {best_g4[1]['sharpe']:.4f} vs B4 {b4['sharpe']:.4f}  "
          f"(Δ {best_g4[1]['sharpe']-b4['sharpe']:+.4f})")
    print(f"  CAGR {best_g4[1]['cagr']:.2f}% vs B4 {b4['cagr']:.2f}%  "
          f"(Δ {best_g4[1]['cagr']-b4['cagr']:+.2f}pp)")
    print(f"  MDD {best_g4[1]['mdd']:.2f}% vs B4 {b4['mdd']:.2f}%  "
          f"(Δ {best_g4[1]['mdd']-b4['mdd']:+.2f}pp)")

    # Lowest MDD across all
    best_mdd = max(rows, key=lambda r: r["mdd"])  # closest to 0
    print(f"\nLowest MDD across all (best in MDD): {best_mdd['name']} = {best_mdd['mdd']:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
