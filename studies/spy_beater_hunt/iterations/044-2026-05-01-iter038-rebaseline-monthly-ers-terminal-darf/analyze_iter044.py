#!/usr/bin/env python3
"""Analyze iter 044 — apply terminal-DARF tax model + build unified 14-config ranking.

Tax model (per user 2026-05-01):
  - User does lazy rebal via aportes only — never sells during accumulation
  - Therefore NO realized gains during year → DARF = 0 each year
  - DARF only at terminal liquidation: 15% × cumulative profit

Formula:
  gross_final = end_val from testfol.io (initial $10k → end_val)
  profit = gross_final - 10000
  darf = 0.15 × profit (only positive profit; negative → 0)
  net_final = gross_final - darf  =  0.85 × gross_final + 0.15 × 10000
  net_CAGR = (net_final / 10000)^(1/years) - 1

For SPY 1x benchmark (reused from iter 040 — same Monthly + ER methodology).
"""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
ITER040_DATA = Path("/var/www/github/finances/market-lab/studies/spy_beater_hunt/iterations/"
                    "040-2026-05-01-baseline-monthly-rebal-explicit-ers/testfolio_data")

BATCHES = ["a", "b", "c", "d"]   # d = 26y window (DBMF-containing)
INITIAL = 10000.0


def load_batch(letter: str) -> tuple[list[dict], dict]:
    path = DATA_DIR / f"backtest_{letter}.json"
    if not path.exists():
        return [], {}
    with open(path) as f:
        d = json.load(f)
    # Get start/end timestamps for window length
    ts = d["response"]["charts"]["history"][0]
    import datetime
    start = datetime.datetime.fromtimestamp(ts[0])
    end = datetime.datetime.fromtimestamp(ts[-1])
    years = (end - start).days / 365.25
    return d["portfolios"], {
        "stats": d["response"]["stats"],
        "years": years,
        "start": start.date(),
        "end": end.date(),
    }


def apply_terminal_darf(gross_final: float, years: float) -> tuple[float, float]:
    """Returns (net_final, net_cagr_pct)."""
    profit = max(0.0, gross_final - INITIAL)
    darf = 0.15 * profit
    net_final = gross_final - darf
    net_cagr = ((net_final / INITIAL) ** (1.0 / years) - 1.0) * 100.0
    return net_final, net_cagr


def fetch_spy_benchmark() -> dict:
    """Get SPY 1x metrics from iter 040 (same Monthly + ER methodology)."""
    with open(ITER040_DATA / "backtest_buyhold_a.json") as f:
        d = json.load(f)
    spy_idx = next(i for i, p in enumerate(d["portfolios"]) if p["slug"] == "spy_1x")
    s = d["response"]["stats"][spy_idx]
    ts = d["response"]["charts"]["history"][0]
    import datetime
    start = datetime.datetime.fromtimestamp(ts[0])
    end = datetime.datetime.fromtimestamp(ts[-1])
    years = (end - start).days / 365.25
    return {
        "slug": "spy_1x",
        "label": "SPY 1× buy-hold",
        "gross_cagr_pct": s["cagr"],
        "mdd_pct": s["max_drawdown"],
        "sharpe": s["sharpe"],
        "sortino": s.get("sortino", 0),
        "calmar": s.get("calmar", 0),
        "gross_end_val": s["end_val"],
        "years": years,
        "window_label": f"{start.date()} → {end.date()} ({years:.2f}y)",
    }


def main() -> int:
    rows: list[dict] = []
    for letter in BATCHES:
        portfolios, batch_meta = load_batch(letter)
        if not portfolios:
            continue
        for p, s in zip(portfolios, batch_meta["stats"]):
            net_final, net_cagr = apply_terminal_darf(s["end_val"], batch_meta["years"])
            rows.append({
                "slug": p["slug"],
                "label": p["label"],
                "gross_cagr_pct": s["cagr"],
                "mdd_pct": s["max_drawdown"],
                "sharpe": s["sharpe"],
                "sortino": s["sortino"],
                "calmar": s["calmar"],
                "gross_end_val": s["end_val"],
                "net_end_val": net_final,
                "net_cagr_pct": net_cagr,
                "years": batch_meta["years"],
                "window_label": f"{batch_meta['start']} → {batch_meta['end']} ({batch_meta['years']:.2f}y)",
                "drag_pct": p["drag_pct"],
            })

    # Add SPY 1x benchmark
    spy = fetch_spy_benchmark()
    spy_net_final, spy_net_cagr = apply_terminal_darf(spy["gross_end_val"], spy["years"])
    rows.append({
        "slug": spy["slug"],
        "label": spy["label"],
        "gross_cagr_pct": spy["gross_cagr_pct"],
        "mdd_pct": spy["mdd_pct"],
        "sharpe": spy["sharpe"],
        "sortino": spy["sortino"],
        "calmar": spy["calmar"],
        "gross_end_val": spy["gross_end_val"],
        "net_end_val": spy_net_final,
        "net_cagr_pct": spy_net_cagr,
        "years": spy["years"],
        "window_label": spy["window_label"],
        "drag_pct": 0.0945,
    })

    # Save unified
    out = SCRIPT_DIR / "unified_metrics.json"
    out.write_text(json.dumps(rows, indent=2, default=str))
    print(f"saved {out}")

    # Print sorted by Sharpe
    rows.sort(key=lambda r: -r["sharpe"])
    print("\n" + "=" * 130)
    print(f"{'Strategy':<35} {'window':<28} {'gross CAGR':>10} {'net CAGR':>10} "
          f"{'MDD':>9} {'Sharpe':>7} {'Sortino':>8} {'Calmar':>8}")
    print("-" * 130)
    for r in rows:
        # Mark 26y window with *
        win_marker = " ⚠26y" if "(26" in r["window_label"] else ""
        print(f"{r['slug']:<35} {r['window_label'][:25]:<28} "
              f"{r['gross_cagr_pct']:>9.2f}% {r['net_cagr_pct']:>9.2f}% "
              f"{r['mdd_pct']:>8.2f}% {r['sharpe']:>7.4f} {r['sortino']:>8.4f} {r['calmar']:>8.4f}{win_marker}")
    print("=" * 130)

    # Pareto frontier (CAGR > SPY net AND |MDD| < |SPY MDD|)
    spy_row = next(r for r in rows if r["slug"] == "spy_1x")
    spy_net = spy_row["net_cagr_pct"]
    spy_mdd_abs = abs(spy_row["mdd_pct"])
    print(f"\nSPY benchmark: net CAGR {spy_net:.2f}% / |MDD| {spy_mdd_abs:.2f}%")
    print("Beats SPY on BOTH net CAGR AND |MDD|:")
    for r in rows:
        if r["slug"] == "spy_1x":
            continue
        if r["net_cagr_pct"] > spy_net and abs(r["mdd_pct"]) < spy_mdd_abs:
            print(f"  ✅ {r['slug']:<35s} net_CAGR={r['net_cagr_pct']:.2f}% MDD={r['mdd_pct']:.2f}% Sharpe={r['sharpe']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
