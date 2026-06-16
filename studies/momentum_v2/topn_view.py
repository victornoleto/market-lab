#!/usr/bin/env python3
"""Top-K view of broad results filtered by holdings count (`top_n`).

High `top_n` (15/20) tends to dominate the unconstrained tops but is harder to
run by hand. This re-ranks an existing window's ``broad_results.csv`` restricted
to a `top_n` range (default 3..10) by rolling dominance, after-tax Sharpe and
after-tax Calmar, and writes a markdown report. Pure post-processing — no
re-simulation. Everything stays research-only / ``promotion_eligible=false``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[1]
for candidate in (REPO_ROOT, REPO_ROOT / "src"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum_v2.util import fmt_num, fmt_pct, md_table  # noqa: E402

RANKINGS = [
    ("rolling_rel_score", "rolling dominance"),
    ("after_tax_sharpe", "after-tax Sharpe"),
    ("after_tax_calmar", "after-tax Calmar"),
]


def filter_by_topn(df: pd.DataFrame, min_top_n: int, max_top_n: int) -> pd.DataFrame:
    """Rows whose holdings count is within [min_top_n, max_top_n]."""
    return df[(df["top_n"] >= min_top_n) & (df["top_n"] <= max_top_n)].copy()


def select_plot_targets(sub: pd.DataFrame, k: int) -> pd.DataFrame:
    """Headline picks to plot: union of top-k by each lens, with identical curves
    (e.g. ``abs_cash`` variants that don't bind) collapsed to one."""
    picks = pd.concat([sub.nlargest(k, column) for column, _ in RANKINGS]).drop_duplicates("name")
    sig = picks.apply(
        lambda r: (round(float(r["after_tax_cagr"]), 4), round(float(r["after_tax_mdd"]), 4),
                   round(float(r["after_tax_sharpe"]), 4)),
        axis=1,
    )
    return picks.loc[~sig.duplicated()].copy()


def _table(frame: pd.DataFrame) -> str:
    rows = [
        {
            "Name": r["name"],
            "Mechanism": r["mechanism"],
            "LB": r["lookback_label"],
            "Top-N": int(r["top_n"]),
            "Reb": int(r["rebalance_months"]),
            "CAGR": fmt_pct(float(r["after_tax_cagr"])),
            "MDD": fmt_pct(float(r["after_tax_mdd"])),
            "Sharpe": fmt_num(float(r["after_tax_sharpe"])),
            "Calmar": fmt_num(float(r["after_tax_calmar"])),
            "RollRel": fmt_pct(float(r["rolling_rel_score"])),
        }
        for _, r in frame.iterrows()
    ]
    return md_table(rows, ["Name", "Mechanism", "LB", "Top-N", "Reb", "CAGR", "MDD", "Sharpe", "Calmar", "RollRel"])


def build_report(df: pd.DataFrame, *, universe: str, window: str, min_top_n: int, max_top_n: int, k: int) -> str:
    sub = filter_by_topn(df, min_top_n, max_top_n)
    out = [
        f"# Top-{k} by lens — `{universe}` `{window}`, top_n in [{min_top_n}, {max_top_n}]\n",
        "Research-only, `promotion_eligible=false`. Post-processing of `broad_results.csv` "
        "restricted to hand-manageable holdings counts; after-tax (BR 15%), gross of costs, "
        "benchmark SPY `[advances_fin_ml, p.208-211]`.\n",
        f"- Configs in range: `{len(sub)}` of `{len(df)}`.\n",
    ]
    if sub.empty:
        out.append("\n_No configs in range._\n")
        return "\n".join(out)
    for column, label in RANKINGS:
        out.append(f"\n## Top {k} by {label}\n")
        out.append(_table(sub.nlargest(k, column)))
    return "\n".join(out)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filtered top-N view of momentum_v2 broad results")
    parser.add_argument("--universe", default="us_stocks")
    parser.add_argument("--start", default="1990-01-01", help="Window start (maps to from_<year>)")
    parser.add_argument("--min-top-n", type=int, default=3)
    parser.add_argument("--max-top-n", type=int, default=10)
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--plots", action="store_true", help="Re-simulate headline picks and plot vs SPY")
    parser.add_argument("--plot-k", type=int, default=4, help="Top-k per lens to plot when --plots")
    return parser.parse_args(argv)


def _generate_plots(df: pd.DataFrame, *, universe: str, start: str, base: Path, min_top_n: int, max_top_n: int, plot_k: int) -> list[str]:
    """Re-simulate the constrained headline picks (cached panel) and plot them."""
    from argparse import Namespace

    from studies.momentum_v2 import config as cfg
    from studies.momentum_v2 import plots as plotlib
    from studies.momentum_v2 import run
    from studies.momentum_v2.core import apply_br_foreign_annual_tax, precompute_scores, simulate_config

    conf = cfg.load_config(universe)
    load_args = Namespace(start=start, end=None, max_symbols=None, cache_panels=True, refresh_cache=False)
    _source, _total, result, benchmark, benchmark_symbol, _start, _window = run._load_panel(conf, universe, load_args)
    assets = tuple(result.prices.columns)
    features = conf.get("features", {})
    out_dir = base / "plots" / f"topn_{min_top_n}_{max_top_n}"
    targets = select_plot_targets(filter_by_topn(df, min_top_n, max_top_n), plot_k)
    links: list[str] = []
    for _, row in targets.iterrows():
        config_i = run._config_from_row(row, assets, features)
        bundle = precompute_scores(
            result.prices, assets, vol_window_days=config_i.vol_window_days,
            trend_window_days=config_i.trend_window_days, lookback_months=config_i.lookback.months,
        )
        sim = simulate_config(result.prices, bundle, config_i)
        if sim.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(sim.returns, sim.daily_weights)
        path = plotlib.plot_strategy_vs_benchmark(
            config_i.name, tax.returns, benchmark, out_dir, base, benchmark_symbol
        )
        if path:
            links.append(path)
    return links


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    window = f"from_{str(args.start)[:4]}"
    base = STUDY_DIR / "universes" / args.universe / window
    broad_path = base / "results" / "broad_results.csv"
    if not broad_path.exists():
        print(f"[topn] missing {broad_path}; run --phase broad first.")
        return 1
    df = pd.read_csv(broad_path)
    report = build_report(
        df, universe=args.universe, window=window,
        min_top_n=args.min_top_n, max_top_n=args.max_top_n, k=args.k,
    )
    if args.plots:
        links = _generate_plots(
            df, universe=args.universe, start=args.start, base=base,
            min_top_n=args.min_top_n, max_top_n=args.max_top_n, plot_k=args.plot_k,
        )
        report += "\n## Plots dos headline picks (re-simulados, vs SPY)\n\n" + (
            "\n".join(f"- [{Path(p).name}](../{p})" for p in links) or "_none_"
        ) + "\n"
        print(f"[topn] wrote {len(links)} plots")
    out_path = base / "reports" / f"TOPN_{args.min_top_n}_{args.max_top_n}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"[topn] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
