#!/usr/bin/env python3
"""Drawdown-reduction sweep for the manual-friendly top_n 3-10 picks.

For each recommended base strategy, compares after-tax MDD / CAGR / Sharpe /
Calmar + crisis MDD across drawdown levers: baseline, SPY SMA200 overlays, and
portfolio vol-targeting. Reference rows (low-vol composite, inverse-vol weighting,
top_n diversification) are pulled straight from ``broad_results.csv`` — alternative
strategies, not overlays on the pick. Research-only / ``promotion_eligible=false``.

    uv run python studies/momentum_v2/drawdown_sweep.py --universe us_stocks --start 1990-01-01
"""

from __future__ import annotations

import argparse
import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[1]
for _candidate in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from studies.momentum_v2 import config as cfg  # noqa: E402
from studies.momentum_v2 import plots as plotlib  # noqa: E402
from studies.momentum_v2 import run  # noqa: E402
from studies.momentum_v2.core import (  # noqa: E402
    apply_br_foreign_annual_tax,
    benchmark_returns_for,
    metrics_from_returns,
    precompute_scores,
    simulate_config,
)
from studies.momentum_v2.dominance import crisis_columns  # noqa: E402
from studies.momentum_v2.overlays import (  # noqa: E402
    market_regime,
    simulate_evolved,
    stock_trend_ok,
    vol_target_returns,
)
from studies.momentum_v2.util import fmt_num, fmt_pct, md_table  # noqa: E402

DEFAULT_PICKS = (
    "clenow_trend_lb1_3_6_12_top10_reb1",
    "clenow_trend_lb1_3_6_12_top5_reb1",
    "raw_13612_lb6_top5_reb6",
)
SMA_OVERLAYS = (
    "market_sma200_monthly",
    "market_sma200_daily",
    "stock_sma100",
    "market_sma200_monthly_stock_sma100",
    "market_sma200_daily_stock_sma100",
)
COLS = ["Variante", "CAGR", "MDD full", "GFC MDD", "Dotcom MDD", "Vol", "Sharpe", "Calmar"]


def _metric_row(label: str, returns: pd.Series, benchmark: pd.DataFrame, benchmark_symbol: str) -> dict:
    srt, brt = benchmark_returns_for(returns, benchmark, benchmark_symbol)
    m = metrics_from_returns(srt)
    crisis = crisis_columns(srt, brt)
    return {
        "Variante": label,
        "_cagr": float(m["cagr"]),
        "_mdd": float(m["mdd"]),
        "_gfc": float(crisis["gfc_mdd"]),
        "_dotcom": float(crisis["dotcom_mdd"]),
        "_vol": float(m["vol"]),
        "_sharpe": float(m["sharpe"]),
        "_calmar": float(m["calmar"]),
        "_returns": srt,
    }


def _fmt_row(r: dict) -> dict:
    return {
        "Variante": r["Variante"],
        "CAGR": fmt_pct(r["_cagr"]),
        "MDD full": fmt_pct(r["_mdd"]),
        "GFC MDD": fmt_pct(r["_gfc"]),
        "Dotcom MDD": fmt_pct(r["_dotcom"]),
        "Vol": fmt_pct(r["_vol"]),
        "Sharpe": fmt_num(r["_sharpe"]),
        "Calmar": fmt_num(r["_calmar"]),
    }


def sweep_pick(stem: str, df: pd.DataFrame, prices: pd.DataFrame, benchmark: pd.DataFrame,
               benchmark_symbol: str, features: dict, regime: tuple, target_vols: list[int]) -> tuple | None:
    """Return (config, lever_rows) for one base pick, or None if absent."""
    daily_market_ok, monthly_market_ok, monthly_stock_ok = regime
    full = f"momv2_us_stocks_{stem}_off0"
    match = df[df["name"] == full]
    if match.empty:
        return None
    assets = tuple(prices.columns)
    config = run._config_from_row(match.iloc[0], assets, features)
    bundle = precompute_scores(
        prices, assets, vol_window_days=config.vol_window_days,
        trend_window_days=config.trend_window_days, lookback_months=config.lookback.months,
    )
    base_sim = simulate_config(prices, bundle, config)
    base_tax = apply_br_foreign_annual_tax(base_sim.returns, base_sim.daily_weights).returns
    rows = [_metric_row("baseline (sem overlay)", base_tax, benchmark, benchmark_symbol)]
    for overlay in SMA_OVERLAYS:
        sim = simulate_evolved(
            prices, bundle, config, overlay, "fixed",
            daily_market_ok, monthly_market_ok, monthly_stock_ok,
        )
        if sim.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(sim.returns, sim.daily_weights).returns
        rows.append(_metric_row(f"SMA200: {overlay}", tax, benchmark, benchmark_symbol))
    for tv in target_vols:
        rows.append(_metric_row(f"vol-target {tv}%", vol_target_returns(base_tax, tv / 100.0), benchmark, benchmark_symbol))
    return config, rows


def reference_rows(stem: str, df: pd.DataFrame) -> list[dict]:
    """Alternative strategies (low-vol composite, inverse-vol, diversification) from broad."""
    full = f"momv2_us_stocks_{stem}_off0"
    r = df[df["name"] == full].iloc[0]
    score, lb, top_n, reb = r["score_mode"], r["lookback_label"], int(r["top_n"]), int(r["rebalance_months"])
    eq = (df["weight_mode"] == "equal") & (~df["absolute_filter"].astype(bool))
    frames = {
        f"low-vol composite (top{top_n})": df[(df["score_mode"] == "composite_mom_lowvol") & (df["lookback_label"] == lb) & (df["top_n"] == top_n) & (df["rebalance_months"] == reb) & eq],
        f"peso inverse-vol ({score})": df[(df["score_mode"] == score) & (df["lookback_label"] == lb) & (df["top_n"] == top_n) & (df["rebalance_months"] == reb) & (df["weight_mode"] == "inverse_vol")],
    }
    out: list[dict] = []
    for label, frame in frames.items():
        if not frame.empty:
            out.append(_csv_row(label, frame.iloc[0]))
    # diversification: same score/lookback/reb, equal weight, top_n in 3/5/10
    div = df[(df["score_mode"] == score) & (df["lookback_label"] == lb) & (df["rebalance_months"] == reb) & eq & (df["top_n"].isin([3, 5, 10]))]
    for _, row in div.sort_values("top_n").iterrows():
        out.append(_csv_row(f"diversificação top{int(row['top_n'])}", row))
    return out


def _csv_row(label: str, row: pd.Series) -> dict:
    return {
        "Variante": label,
        "CAGR": fmt_pct(float(row["after_tax_cagr"])),
        "MDD full": fmt_pct(float(row["after_tax_mdd"])),
        "GFC MDD": fmt_pct(float(row["gfc_mdd"])),
        "Dotcom MDD": fmt_pct(float(row["dotcom_mdd"])),
        "Vol": fmt_pct(float(row["after_tax_vol"])),
        "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
        "Calmar": fmt_num(float(row["after_tax_calmar"])),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drawdown-reduction sweep for momentum_v2 top_n 3-10 picks")
    parser.add_argument("--universe", default="us_stocks")
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--target-vols", default="15,20,25", help="Comma-separated annualized vol targets (%)")
    parser.add_argument("--picks", default=",".join(DEFAULT_PICKS), help="Comma-separated base pick name stems")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    window = f"from_{str(args.start)[:4]}"
    base = STUDY_DIR / "universes" / args.universe / window
    broad_path = base / "results" / "broad_results.csv"
    if not broad_path.exists():
        print(f"[drawdown] missing {broad_path}; run --phase broad first.")
        return 1
    df = pd.read_csv(broad_path)
    target_vols = [int(x) for x in str(args.target_vols).split(",") if x.strip()]
    picks = [p.strip() for p in str(args.picks).split(",") if p.strip()]

    conf = cfg.load_config(args.universe)
    load_args = Namespace(start=args.start, end=None, max_symbols=None, cache_panels=True, refresh_cache=False)
    _source, _total, result, benchmark, benchmark_symbol, _start, _window = run._load_panel(conf, args.universe, load_args)
    prices = result.prices
    features = conf.get("features", {})
    daily_market_ok, monthly_market_ok = market_regime(benchmark, pd.DatetimeIndex(prices.sort_index().index))
    monthly_stock_ok = stock_trend_ok(prices)
    regime = (daily_market_ok, monthly_market_ok, monthly_stock_ok)

    plot_dir = base / "plots" / "drawdown_sweep"
    sections: list[str] = []
    for i, stem in enumerate(picks):
        result_sweep = sweep_pick(stem, df, prices, benchmark, benchmark_symbol, features, regime, target_vols)
        if result_sweep is None:
            sections.append(f"\n## `{stem}` — ausente no broad_results\n")
            continue
        _config, rows = result_sweep
        ranked = sorted(rows, key=lambda r: r["_mdd"], reverse=True)  # best (shallowest) MDD first
        best = ranked[0]
        baseline = next(r for r in rows if r["Variante"].startswith("baseline"))
        section = [
            f"\n## `{stem}`\n",
            f"Baseline MDD `{fmt_pct(baseline['_mdd'])}` / CAGR `{fmt_pct(baseline['_cagr'])}`. "
            f"Melhor MDD full: **{best['Variante']}** -> `{fmt_pct(best['_mdd'])}` "
            f"(CAGR `{fmt_pct(best['_cagr'])}`, Sharpe `{fmt_num(best['_sharpe'])}`, Calmar `{fmt_num(best['_calmar'])}`).\n",
            "\n### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)\n",
            md_table([_fmt_row(r) for r in ranked], COLS),
            "\n### Referência: estratégias alternativas (do broad_results)\n",
            md_table(reference_rows(stem, df), COLS),
        ]
        # plots only for the headline pick to keep the doc focused
        if i == 0:
            for r in rows:
                if r["Variante"].startswith("baseline") or r["Variante"] == "SMA200: market_sma200_monthly" or r["Variante"] == f"vol-target {target_vols[0]}%":
                    label = r["Variante"].replace(":", "").replace(" ", "_").replace("%", "pct")
                    plotlib.plot_strategy_vs_benchmark(
                        f"{stem}__{label}", r["_returns"], benchmark, plot_dir, base, benchmark_symbol
                    )
            section.append(f"\nPlots das variantes do headline em `plots/drawdown_sweep/` (baseline, SMA200 mensal, vol-target {target_vols[0]}%).\n")
        sections.append("".join(section))

    report = (
        f"# Sweep de redução de drawdown — `{args.universe}` `{window}`\n\n"
        "Research-only, `promotion_eligible=false`. After-tax (BR 15%), bruto de custos, "
        "benchmark SPY. Alavancas: SPY SMA200 (Clenow/Gayed) e vol-targeting (escala a "
        "exposição pela vol da carteira, só de-risk, lag anti-look-ahead) "
        "`[systematic_trading, p.137-148]`, `[advances_fin_ml, p.31-34]`, "
        "`[stocks_on_the_move, p.66-67]`, `[leverage_for_the_long_run, p.9, p.13, p.16]`. "
        "Vol-targeting é aplicado sobre a série after-tax (aproximação de diagnóstico).\n"
        + "".join(sections)
    )
    out_path = base / "reports" / "DRAWDOWN_SWEEP.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"[drawdown] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
