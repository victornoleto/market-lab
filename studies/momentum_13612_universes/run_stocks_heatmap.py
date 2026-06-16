#!/usr/bin/env python3
"""Run US-stocks 13612 heatmap diagnostics.

This runner is exploratory, not a selector. It expands the stocks-only surface by
momentum lookback profile, mechanism, top-N, rebalance frequency and offset, then
writes an interactive local HTML heatmap. The tested lookbacks and offsets are
explicit grid dimensions, so the output is a diagnostic against timing/parameter
luck rather than a winner declaration `[advances_fin_ml, p.273-275]`. Momentum
ranking follows `[stocks_on_the_move, p.60]`; monthly review follows
`[stocks_on_the_move, p.98-99]`; inverse-volatility sizing follows
`[systematic_trading, p.137-148]`.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum_13612_universes.extensive import (  # noqa: E402
    ExtensiveConfig,
    apply_br_foreign_annual_tax,
    metrics_from_returns,
    precompute_scores,
    result_row,
    simulate_extensive_config,
)
from studies.momentum_13612_universes.run import (  # noqa: E402
    fmt_num,
    fmt_pct,
    json_safe,
    md_table,
    safe_filename,
)
from studies.momentum_13612_universes.run_extensive import (  # noqa: E402
    MECHANISMS,
    load_us_price_frame,
    parse_int_tuple,
)
from studies.momentum_13612_universes.universes import (  # noqa: E402
    drop_extreme_return_tickers,
    load_yfinance_price_frame,
    us_stock_tickers_with_membership,
)


STUDY_DIR = Path(__file__).resolve().parent
STOCKS_DIR = STUDY_DIR / "us" / "stocks"
RESULTS_DIR = STOCKS_DIR / "results"
PLOTS_DIR = STOCKS_DIR / "plots" / "heatmap"
FINALIST_PLOTS_DIR = PLOTS_DIR / "finalists"
REPORT_MD = STOCKS_DIR / "HEATMAP_REPORT.md"
REPORT_HTML = STOCKS_DIR / "HEATMAP.html"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

DEFAULT_TOP_N = (1, 3, 5, 10, 15, 20)
DEFAULT_REBALANCE_MONTHS = (1, 3, 6, 12)
DEFAULT_LOOKBACKS = "3,6,12,3_6_12,6_12,1_3_6_12"
DEFAULT_MECHANISMS = tuple(name for name, *_ in MECHANISMS)
CRISIS_WINDOWS = {
    # Stress windows are diagnostics, not fitted parameters `[testing_tuning, p.327-335]`.
    "dotcom": ("2000-03-01", "2002-10-31"),
    "gfc": ("2007-10-01", "2009-03-31"),
    "covid": ("2020-02-01", "2020-04-30"),
}


@dataclass(frozen=True)
class LookbackProfile:
    label: str
    months: tuple[int, ...]


def parse_lookback_profiles(raw: str) -> tuple[LookbackProfile, ...]:
    profiles: list[LookbackProfile] = []
    for token in (part.strip() for part in raw.split(",") if part.strip()):
        months = tuple(int(part) for part in token.split("_") if part)
        if not months or any(month <= 0 for month in months):
            raise ValueError(f"invalid lookback profile: {token!r}")
        if len(set(months)) != len(months):
            raise ValueError(f"lookback months must be unique: {token!r}")
        label = "lb" + "_".join(str(month) for month in months)
        profiles.append(LookbackProfile(label=label, months=months))
    if not profiles:
        raise ValueError("at least one lookback profile is required")
    return tuple(profiles)


def parse_mechanisms(raw: str) -> tuple[tuple[str, str, str, bool], ...]:
    requested = tuple(part.strip() for part in raw.split(",") if part.strip())
    by_name = {
        name: (name, score_mode, weight_mode, absolute_filter)
        for name, score_mode, weight_mode, absolute_filter in MECHANISMS
    }
    if not requested or any(name not in by_name for name in requested):
        raise ValueError(f"mechanisms must be a subset of {sorted(by_name)}")
    return tuple(by_name[name] for name in requested)


def make_heatmap_config_name(
    mechanism: str,
    lookback_label: str,
    top_n: int,
    rebalance_months: int,
    offset: int,
) -> str:
    return (
        f"mom13612_us_stocks_{mechanism}_{lookback_label}"
        f"_top{top_n}_reb{rebalance_months}_off{offset}"
    )


def window_metrics(returns: pd.Series, start: str, end: str, prefix: str) -> dict[str, float]:
    window = returns.loc[pd.Timestamp(start): pd.Timestamp(end)].dropna().astype(float)
    if window.empty:
        return {f"{prefix}_cagr": float("nan"), f"{prefix}_mdd": float("nan"), f"{prefix}_sharpe": float("nan")}
    metrics = metrics_from_returns(window)
    return {
        f"{prefix}_cagr": float(metrics["cagr"]),
        f"{prefix}_mdd": float(metrics["mdd"]),
        f"{prefix}_sharpe": float(metrics["sharpe"]),
    }


def regime_columns(strategy_returns: pd.Series, bench_returns: pd.Series) -> dict[str, float]:
    out: dict[str, float] = {}
    for label, (start, end) in CRISIS_WINDOWS.items():
        out.update(window_metrics(strategy_returns, start, end, label))
        bench = window_metrics(bench_returns, start, end, f"{label}_spy")
        out.update(bench)
        if math.isfinite(out[f"{label}_mdd"]) and math.isfinite(out[f"{label}_spy_mdd"]):
            out[f"{label}_mdd_delta"] = out[f"{label}_mdd"] - out[f"{label}_spy_mdd"]
        else:
            out[f"{label}_mdd_delta"] = float("nan")
    return out


def build_heatmap_rows(args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, pd.Series], pd.DataFrame]:
    lookbacks = parse_lookback_profiles(args.lookbacks)
    mechanisms = parse_mechanisms(args.mechanisms)
    top_values = parse_int_tuple(args.top_n)
    freq_values = parse_int_tuple(args.rebalance_months)
    tickers_list, eligible_by_date = us_stock_tickers_with_membership(
        TIINGO_ROOT,
        limit=args.max_us_stocks,
        universe=args.us_stock_universe,
        start=args.start,
        end=args.end,
    )
    tickers = tuple(tickers_list)
    prices, _source = load_us_price_frame(tickers, args)
    prices, dropped_extreme = drop_extreme_return_tickers(prices, args.max_abs_daily_return)
    tickers = tuple(ticker for ticker in tickers if ticker in prices.columns)
    if dropped_extreme:
        suffix = "..." if len(dropped_extreme) > 25 else ""
        print(
            f"dropped {len(dropped_extreme)} tickers with abs daily return > "
            f"{args.max_abs_daily_return}: {', '.join(dropped_extreme[:25])}{suffix}",
            flush=True,
        )
    benchmark_prices = load_yfinance_price_frame(("SPY",), args.start, args.end, allow_missing=False)

    bundles = {
        profile.label: precompute_scores(
            prices,
            tickers,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
            lookback_months=profile.months,
        )
        for profile in lookbacks
    }
    # Clenow does not use momentum lookback; keep it as one trend profile.
    trend_profile = LookbackProfile(label=f"trend{args.trend_window_days}d", months=())
    bundles[trend_profile.label] = precompute_scores(
        prices,
        tickers,
        vol_window_days=args.vol_window_days,
        trend_window_days=args.trend_window_days,
    )

    planned = []
    for mechanism, score_mode, weight_mode, absolute_filter in mechanisms:
        profile_iter = (trend_profile,) if score_mode == "clenow_trend" else lookbacks
        for profile in profile_iter:
            for top_n in top_values:
                for freq in freq_values:
                    for offset in range(freq):
                        planned.append((mechanism, score_mode, weight_mode, absolute_filter, profile, top_n, freq, offset))

    rows: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    n_trials = len(planned)
    for i, (mechanism, score_mode, weight_mode, absolute_filter, profile, top_n, freq, offset) in enumerate(planned, start=1):
        config = ExtensiveConfig(
            name=make_heatmap_config_name(mechanism, profile.label, top_n, freq, offset),
            universe="us_stocks",
            assets=tickers,
            top_n=top_n,
            rebalance_months=freq,
            rebalance_offset=offset,
            score_mode=score_mode,  # type: ignore[arg-type]
            weight_mode=weight_mode,  # type: ignore[arg-type]
            absolute_filter=absolute_filter,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
        )
        simulation = simulate_extensive_config(
            prices,
            bundles[profile.label],
            config,
            eligible_by_date=eligible_by_date,
        )
        if simulation.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
        row = result_row(
            config,
            simulation,
            benchmark_prices,
            n_trials=n_trials,
            ranked_returns=tax.returns,
            tax_summary=tax.summary,
        )
        strategy_returns, bench_returns = align_to_benchmark(tax.returns, benchmark_prices)
        row.update(regime_columns(strategy_returns, bench_returns))
        row.update(
            {
                "lookback_label": profile.label,
                "lookback_months": "/".join(str(month) for month in profile.months) or "trend",
                "lookback_max_months": max(profile.months) if profile.months else 0,
                "rebalance_cell": f"{freq}m_off{offset}",
                "heatmap_row": f"{mechanism} | {profile.label} | top{top_n}",
                "us_stock_universe": args.us_stock_universe,
                "dynamic_universe": eligible_by_date is not None,
                "max_abs_daily_return_filter": args.max_abs_daily_return,
                "dropped_extreme_tickers": len(dropped_extreme),
            }
        )
        rows.append(row)
        returns_by_name[config.name] = tax.returns
        if i == 1 or i % 250 == 0 or i == n_trials:
            print(f"simulated {i}/{n_trials}: {config.name}", flush=True)

    return pd.DataFrame(rows), returns_by_name, benchmark_prices


def align_to_benchmark(strategy_returns: pd.Series, benchmark_prices: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    from studies.momentum_13612_universes.extensive import benchmark_returns_for

    return benchmark_returns_for(strategy_returns, benchmark_prices)


def write_static_heatmaps(results: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    metrics = [
        ("after_tax_sharpe", "After-tax Sharpe", "heatmap_after_tax_sharpe.png", "viridis"),
        ("after_tax_cagr", "After-tax CAGR", "heatmap_after_tax_cagr.png", "viridis"),
        ("after_tax_mdd", "After-tax MDD", "heatmap_after_tax_mdd.png", "RdYlGn"),
        ("rolling_rel_score", "Rolling Relative Score", "heatmap_rolling_relative_score.png", "viridis"),
        ("gfc_mdd", "GFC MDD", "heatmap_gfc_mdd.png", "RdYlGn"),
        ("dotcom_mdd", "Dot-com MDD", "heatmap_dotcom_mdd.png", "RdYlGn"),
    ]
    for metric, title, filename, cmap in metrics:
        pivot = results.pivot_table(
            index=["mechanism", "lookback_label", "top_n"],
            columns=["rebalance_months", "rebalance_offset"],
            values=metric,
            aggfunc="max",
        ).sort_index()
        data = pivot.to_numpy(dtype=float)
        if metric.endswith("cagr") or metric.endswith("mdd") or metric.startswith("rolling_rel"):
            display_data = data * 100.0
        else:
            display_data = data
        height = max(9.0, 0.18 * len(pivot.index))
        fig, ax = plt.subplots(figsize=(18, height))
        finite = display_data[np.isfinite(display_data)]
        if finite.size:
            vmin = float(np.nanpercentile(finite, 3))
            vmax = float(np.nanpercentile(finite, 97))
        else:
            vmin = vmax = None
        im = ax.imshow(display_data, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(f"US stocks heatmap: {title}")
        ax.set_xticks(
            range(len(pivot.columns)),
            [f"{freq}m\noff{offset}" for freq, offset in pivot.columns],
            fontsize=7,
        )
        ax.set_yticks(
            range(len(pivot.index)),
            [f"{mech} | {lookback} | top{top}" for mech, lookback, top in pivot.index],
            fontsize=5,
        )
        ax.set_xlabel("Rebalance frequency / offset")
        fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
        fig.tight_layout()
        out = PLOTS_DIR / filename
        fig.savefig(out, dpi=140)
        plt.close(fig)
        outputs.append(str(out.relative_to(STOCKS_DIR)))
    return outputs


def write_finalist_plots(
    results: pd.DataFrame,
    returns_by_name: dict[str, pd.Series],
    benchmark_prices: pd.DataFrame,
) -> dict[str, str]:
    """Plot top Sharpe and top rolling-relative rows for report links."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FINALIST_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.concat(
        [
            results.nlargest(20, "after_tax_sharpe"),
            results.nlargest(20, "rolling_rel_score"),
        ]
    ).drop_duplicates("name")
    links: dict[str, str] = {}
    for name in selected["name"]:
        returns = returns_by_name.get(str(name))
        if returns is None:
            continue
        strategy_returns, bench_returns = align_to_benchmark(returns, benchmark_prices)
        if strategy_returns.empty or bench_returns.empty:
            continue
        strategy_eq = (1.0 + strategy_returns).cumprod()
        spy_eq = (1.0 + bench_returns).cumprod()
        aligned = pd.concat({"Strategy": strategy_eq, "SPY": spy_eq}, axis=1).dropna()
        drawdown = aligned / aligned.cummax() - 1.0
        relative = aligned["Strategy"] / aligned["SPY"]

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        aligned.plot(ax=axes[0], linewidth=1.1)
        axes[0].set_title(f"{name}: after-tax equity vs SPY")
        axes[0].set_ylabel("Growth of $1")
        axes[0].grid(True, alpha=0.3)
        drawdown.plot(ax=axes[1], linewidth=1.0)
        axes[1].set_title("Drawdown")
        axes[1].set_ylabel("Drawdown")
        axes[1].grid(True, alpha=0.3)
        relative.plot(ax=axes[2], color="black", linewidth=1.1)
        axes[2].axhline(1.0, color="gray", linestyle="--", linewidth=1.0)
        axes[2].set_title("Strategy / SPY relative equity")
        axes[2].set_ylabel("Ratio")
        axes[2].grid(True, alpha=0.3)
        fig.tight_layout()
        path = FINALIST_PLOTS_DIR / f"{safe_filename(str(name))}_vs_SPY.png"
        fig.savefig(path, dpi=140)
        plt.close(fig)
        links[str(name)] = str(path.relative_to(STOCKS_DIR))
    return links


def plot_link(row: pd.Series, plot_links: dict[str, str]) -> str:
    path = plot_links.get(str(row["name"]))
    if not path:
        return ""
    return f"[{Path(path).name}]({path})"


def write_html_report(results: pd.DataFrame, plot_paths: list[str], args: argparse.Namespace) -> None:
    records = json.dumps(json_safe(results.to_dict(orient="records")), ensure_ascii=False)
    metric_options = [
        ("after_tax_sharpe", "After-tax Sharpe", "num"),
        ("after_tax_cagr", "After-tax CAGR", "pct"),
        ("after_tax_mdd", "After-tax MDD", "pct"),
        ("after_tax_vol", "After-tax Vol", "pct"),
        ("after_tax_calmar", "After-tax Calmar", "num"),
        ("excess_cagr", "Excess CAGR vs SPY", "pct"),
        ("rolling_rel_score", "Rolling Relative Score", "pct"),
        ("rolling_rel_p25_score", "Rolling Relative P25", "pct"),
        ("rolling_rel_min_score", "Rolling Relative Min", "pct"),
        ("rel_20y_above_mean", "20y Relative Above Mean", "pct"),
        ("annual_turnover", "Turnover/year", "num"),
        ("dotcom_mdd", "Dot-com MDD", "pct"),
        ("gfc_mdd", "GFC MDD", "pct"),
        ("covid_mdd", "COVID MDD", "pct"),
    ]
    best_sharpe = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_mdd = results.nlargest(1, "after_tax_mdd").iloc[0]
    best_gfc = results.nlargest(1, "gfc_mdd").iloc[0]
    best_relative = results.nlargest(1, "rolling_rel_score").iloc[0]
    source_note = (
        "Research-only yfinance + Wikipedia selected-changes PIT-ish S&P 500 diagnostic. "
        "The ranking universe is masked by reconstructed month-end constituents, but "
        "results remain non-promotable without true delisted-price validation "
        "[advances_fin_ml, p.208-211]."
        if args.us_stock_universe == "sp500_wikipedia_pit"
        else "Research-only yfinance/current S&P 500 diagnostic. This expands the stocks-only "
        "surface by mechanism, momentum lookback, top-N, rebalance frequency and offset. "
        "Current-universe results remain non-promotable without PIT/delisted validation "
        "[advances_fin_ml, p.208-211]."
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>US Stocks Momentum 13612 Heatmap</title>
<style>
body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; color: #1f2933; background: #f7f8fa; }}
h1, h2 {{ margin-bottom: 0.25rem; }}
.note {{ color: #52606d; max-width: 1100px; line-height: 1.45; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin: 18px 0; }}
.card {{ background: white; border: 1px solid #d9e2ec; border-radius: 12px; padding: 14px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06); }}
.controls {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin: 18px 0; padding: 14px; background: white; border: 1px solid #d9e2ec; border-radius: 12px; }}
label {{ font-size: 12px; font-weight: 700; color: #334e68; display: block; margin-bottom: 4px; }}
select, input {{ width: 100%; padding: 7px; border: 1px solid #bcccdc; border-radius: 8px; background: white; }}
.heatwrap {{ overflow: auto; border: 1px solid #d9e2ec; border-radius: 12px; background: white; max-height: 75vh; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #e4e7eb; padding: 5px 7px; font-size: 12px; text-align: right; white-space: nowrap; }}
th {{ position: sticky; top: 0; background: #f0f4f8; z-index: 2; }}
td:first-child, th:first-child {{ position: sticky; left: 0; text-align: left; background: #f0f4f8; z-index: 3; }}
.plots a {{ margin-right: 14px; display: inline-block; }}
.small {{ font-size: 12px; color: #627d98; }}
</style>
</head>
<body>
<h1>US Stocks Momentum 13612 Heatmap</h1>
<p class="note">{html.escape(source_note)}</p>
<div class="cards">
  <div class="card"><b>Rows</b><br>{len(results):,} configs<br><span class="small">start {html.escape(args.start)}, max stocks {args.max_us_stocks}</span></div>
  <div class="card"><b>Best Sharpe</b><br>{html.escape(str(best_sharpe['name']))}<br>{fmt_pct(float(best_sharpe['after_tax_cagr']))} CAGR / {fmt_pct(float(best_sharpe['after_tax_mdd']))} MDD / {fmt_num(float(best_sharpe['after_tax_sharpe']))} Sharpe</div>
  <div class="card"><b>Best MDD</b><br>{html.escape(str(best_mdd['name']))}<br>{fmt_pct(float(best_mdd['after_tax_cagr']))} CAGR / {fmt_pct(float(best_mdd['after_tax_mdd']))} MDD</div>
  <div class="card"><b>Best GFC MDD</b><br>{html.escape(str(best_gfc['name']))}<br>{fmt_pct(float(best_gfc['gfc_mdd']))} GFC MDD / {fmt_pct(float(best_gfc['after_tax_mdd']))} full MDD</div>
  <div class="card"><b>Best Rolling Relative</b><br>{html.escape(str(best_relative['name']))}<br>{fmt_pct(float(best_relative['rolling_rel_score']))} score / {fmt_pct(float(best_relative['rolling_rel_p25_score']))} p25</div>
</div>
<div class="controls">
  <div><label>Metric</label><select id="metric"></select></div>
  <div><label>Mechanism</label><select id="mechanism"><option value="">All</option></select></div>
  <div><label>Lookback</label><select id="lookback"><option value="">All</option></select></div>
  <div><label>Top-N</label><select id="topn"><option value="">All</option></select></div>
  <div><label>Rebalance</label><select id="reb"><option value="">All</option></select></div>
  <div><label>Search name</label><input id="search" placeholder="raw_inverse top10"></div>
</div>
<div class="heatwrap"><table id="heatmap"></table></div>
<h2>Static PNG Heatmaps</h2>
<p class="plots">{''.join(f'<a href="{html.escape(path)}">{html.escape(Path(path).name)}</a>' for path in plot_paths)}</p>
<h2>Full Rows</h2>
<p class="small">The table below follows the active filters and sorts by the selected metric descending.</p>
<div class="heatwrap"><table id="rows"></table></div>
<script>
const DATA = {records};
const METRICS = {json.dumps(metric_options)};
const COLS = [];
[1,3,6,12].forEach(freq => {{ for (let off = 0; off < freq; off++) COLS.push(`${{freq}}m_off${{off}}`); }});
const fmt = (value, kind) => {{
  if (value === null || Number.isNaN(value)) return '';
  if (kind === 'pct') return `${{(value * 100).toFixed(2)}}%`;
  return Number(value).toFixed(3);
}};
function unique(key) {{ return [...new Set(DATA.map(row => row[key]).filter(v => v !== null && v !== undefined))].sort(); }}
function fillSelect(id, values) {{
  const el = document.getElementById(id);
  values.forEach(v => {{ const opt = document.createElement('option'); opt.value = v; opt.textContent = v; el.appendChild(opt); }});
}}
METRICS.forEach(([key, label]) => {{ const opt = document.createElement('option'); opt.value = key; opt.textContent = label; document.getElementById('metric').appendChild(opt); }});
fillSelect('mechanism', unique('mechanism'));
fillSelect('lookback', unique('lookback_label'));
fillSelect('topn', unique('top_n'));
fillSelect('reb', unique('rebalance_months'));
function filtered() {{
  const mechanism = document.getElementById('mechanism').value;
  const lookback = document.getElementById('lookback').value;
  const topn = document.getElementById('topn').value;
  const reb = document.getElementById('reb').value;
  const search = document.getElementById('search').value.toLowerCase();
  return DATA.filter(row =>
    (!mechanism || row.mechanism === mechanism) &&
    (!lookback || row.lookback_label === lookback) &&
    (!topn || String(row.top_n) === topn) &&
    (!reb || String(row.rebalance_months) === reb) &&
    (!search || String(row.name).toLowerCase().includes(search))
  );
}}
function color(value, min, max) {{
  if (value === null || Number.isNaN(value) || min === max) return 'transparent';
  const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const hue = 8 + t * 120;
  return `hsl(${{hue}}, 72%, 82%)`;
}}
function renderHeatmap() {{
  const metric = document.getElementById('metric').value;
  const kind = METRICS.find(([key]) => key === metric)[2];
  const rows = filtered();
  const values = rows.map(row => row[metric]).filter(v => v !== null && !Number.isNaN(v));
  const min = Math.min(...values), max = Math.max(...values);
  const byRow = new Map();
  rows.forEach(row => {{
    const key = row.heatmap_row;
    if (!byRow.has(key)) byRow.set(key, {{}});
    byRow.get(key)[row.rebalance_cell] = row;
  }});
  let html = '<thead><tr><th>Mechanism | Lookback | Top-N</th>' + COLS.map(c => `<th>${{c}}</th>`).join('') + '</tr></thead><tbody>';
  [...byRow.keys()].sort().forEach(key => {{
    html += `<tr><td>${{key}}</td>`;
    COLS.forEach(col => {{
      const row = byRow.get(key)[col];
      if (!row) {{ html += '<td></td>'; return; }}
      const value = row[metric];
      html += `<td title="${{row.name}}" style="background:${{color(value, min, max)}}">${{fmt(value, kind)}}</td>`;
    }});
    html += '</tr>';
  }});
  html += '</tbody>';
  document.getElementById('heatmap').innerHTML = html;
  renderRows(rows, metric, kind);
}}
function renderRows(rows, metric, kind) {{
  const cols = ['name','mechanism','lookback_label','top_n','rebalance_months','rebalance_offset','after_tax_cagr','after_tax_mdd','after_tax_sharpe','after_tax_calmar','rolling_rel_score','rolling_rel_p25_score','rel_20y_above_mean','gfc_mdd','dotcom_mdd','annual_turnover'];
  const sorted = [...rows].sort((a,b) => (b[metric] ?? -999) - (a[metric] ?? -999)).slice(0, 500);
  let html = '<thead><tr>' + cols.map(c => `<th>${{c}}</th>`).join('') + '</tr></thead><tbody>';
  sorted.forEach(row => {{
    html += '<tr>' + cols.map(c => {{
      const value = row[c];
      const cellKind = c.includes('cagr') || c.includes('mdd') || c.includes('vol') || c.includes('rel_') || c.includes('above') ? 'pct' : 'num';
      const shown = typeof value === 'number' ? fmt(value, cellKind) : value;
      return `<td>${{shown ?? ''}}</td>`;
    }}).join('') + '</tr>';
  }});
  html += '</tbody>';
  document.getElementById('rows').innerHTML = html;
}}
['metric','mechanism','lookback','topn','reb','search'].forEach(id => document.getElementById(id).addEventListener('input', renderHeatmap));
renderHeatmap();
</script>
</body>
</html>
"""
    REPORT_HTML.write_text(html_text, encoding="utf-8")


def write_markdown_report(
    results: pd.DataFrame,
    plot_paths: list[str],
    args: argparse.Namespace,
    finalist_plot_links: dict[str, str],
) -> None:
    top = results.nlargest(20, "after_tax_sharpe")
    top_relative = results.nlargest(20, "rolling_rel_score")
    rows = []
    for _, row in top.iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Mechanism": row["mechanism"],
                "Lookback": row["lookback_label"],
                "Top-N": int(row["top_n"]),
                "Reb": int(row["rebalance_months"]),
                "Off": int(row["rebalance_offset"]),
                "CAGR": fmt_pct(float(row["after_tax_cagr"])),
                "MDD": fmt_pct(float(row["after_tax_mdd"])),
                "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
                "RollRel": fmt_pct(float(row["rolling_rel_score"])),
                "RollP25": fmt_pct(float(row["rolling_rel_p25_score"])),
                "GFC MDD": fmt_pct(float(row["gfc_mdd"])),
                "Dotcom MDD": fmt_pct(float(row["dotcom_mdd"])),
                "Turnover": fmt_num(float(row["annual_turnover"])),
                "Plot": plot_link(row, finalist_plot_links),
            }
        )
    relative_rows = []
    for _, row in top_relative.iterrows():
        relative_rows.append(
            {
                "Name": row["name"],
                "Mechanism": row["mechanism"],
                "Lookback": row["lookback_label"],
                "Top-N": int(row["top_n"]),
                "Reb": int(row["rebalance_months"]),
                "Off": int(row["rebalance_offset"]),
                "RollRel": fmt_pct(float(row["rolling_rel_score"])),
                "RollP25": fmt_pct(float(row["rolling_rel_p25_score"])),
                "RollMin": fmt_pct(float(row["rolling_rel_min_score"])),
                "CAGR": fmt_pct(float(row["after_tax_cagr"])),
                "MDD": fmt_pct(float(row["after_tax_mdd"])),
                "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
                "Terminal/SPY": fmt_num(float(row["terminal_relative"])),
                "20y Above": fmt_pct(float(row["rel_20y_above_mean"])),
                "Plot": plot_link(row, finalist_plot_links),
            }
        )
    best = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_relative = results.nlargest(1, "rolling_rel_score").iloc[0]
    source_line = (
        "- Source caveat: yfinance + Wikipedia selected-changes PIT-ish S&P 500; "
        "`promotion_eligible=false` until true PIT/delisted prices validate the result "
        "`[advances_fin_ml, p.208-211]`.\n\n"
        if args.us_stock_universe == "sp500_wikipedia_pit"
        else "- Source caveat: yfinance/current-universe screen; `promotion_eligible=false` "
        "until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.\n\n"
    )
    REPORT_MD.write_text(
        "# US Stocks 13612 Heatmap Diagnostics\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Scope\n\n"
        f"- Start: `{args.start}`\n"
        f"- US stock universe: `{args.us_stock_universe}`\n"
        f"- Max US stocks: `{args.max_us_stocks}`\n"
        f"- Max abs daily return filter: `{args.max_abs_daily_return}`\n"
        f"- Rows: `{len(results)}`\n"
        f"- Lookbacks: `{args.lookbacks}`\n"
        f"- Top-N: `{args.top_n}`\n"
        f"- Rebalance months: `{args.rebalance_months}` with all offsets\n"
        + source_line
        + "## Best After-Tax Sharpe\n\n"
        f"`{best['name']}`: CAGR `{fmt_pct(float(best['after_tax_cagr']))}`, "
        f"MDD `{fmt_pct(float(best['after_tax_mdd']))}`, Sharpe "
        f"`{fmt_num(float(best['after_tax_sharpe']))}`, GFC MDD "
        f"`{fmt_pct(float(best['gfc_mdd']))}`.\n\n"
        "## Best Rolling Relative Dominance\n\n"
        f"`{best_relative['name']}`: score `{fmt_pct(float(best_relative['rolling_rel_score']))}`, "
        f"p25 `{fmt_pct(float(best_relative['rolling_rel_p25_score']))}`, min "
        f"`{fmt_pct(float(best_relative['rolling_rel_min_score']))}`.\n\n"
        "## Interactive Output\n\n"
        f"- [HEATMAP.html]({REPORT_HTML.name})\n"
        + "\n".join(f"- [{Path(path).name}]({path})" for path in plot_paths)
        + "\n\n## Top 20 By After-Tax Sharpe\n\n"
        + md_table(
            rows,
            [
                "Name",
                "Mechanism",
                "Lookback",
                "Top-N",
                "Reb",
                "Off",
                "CAGR",
                "MDD",
                "Sharpe",
                "RollRel",
                "RollP25",
                "GFC MDD",
                "Dotcom MDD",
                "Turnover",
                "Plot",
            ],
        )
        + "\n\n## Top 20 By Rolling Relative Score\n\n"
        + md_table(
            relative_rows,
            [
                "Name",
                "Mechanism",
                "Lookback",
                "Top-N",
                "Reb",
                "Off",
                "RollRel",
                "RollP25",
                "RollMin",
                "CAGR",
                "MDD",
                "Sharpe",
                "Terminal/SPY",
                "20y Above",
                "Plot",
            ],
        )
        + "\n## Notes\n\n"
        "- Dot-com/GFC/COVID windows are stress diagnostics, not fitted gates "
        "`[testing_tuning, p.327-335]`.\n"
        + (
            "- `sp500_wikipedia_pit` reduces current-constituent leakage, but Wikipedia "
            "changes are incomplete and yfinance still does not provide delisting returns "
            "`[advances_fin_ml, p.208-211]`.\n"
            if args.us_stock_universe == "sp500_wikipedia_pit"
            else "- Re-running to 1990 with current S&P 500 constituents is more biased than a "
            "PIT universe because delisted losers are absent `[advances_fin_ml, p.208-211]`.\n"
        ),
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run US-stocks 13612 heatmap diagnostics")
    parser.add_argument("--us-source", choices=["yfinance", "tiingo"], default="yfinance")
    parser.add_argument("--allow-biased-yfinance", action="store_true")
    parser.add_argument(
        "--us-stock-universe",
        choices=["sp500", "tiingo_manifest", "sp500_wikipedia_pit"],
        default="sp500",
    )
    parser.add_argument("--max-us-stocks", type=int, default=9999)
    parser.add_argument("--max-us-etfs", type=int, default=0)
    parser.add_argument("--top-n", default=",".join(str(value) for value in DEFAULT_TOP_N))
    parser.add_argument(
        "--rebalance-months",
        default=",".join(str(value) for value in DEFAULT_REBALANCE_MONTHS),
    )
    parser.add_argument("--lookbacks", default=DEFAULT_LOOKBACKS)
    parser.add_argument("--mechanisms", default=",".join(DEFAULT_MECHANISMS))
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--vol-window-days", type=int, default=126)
    parser.add_argument("--trend-window-days", type=int, default=126)
    parser.add_argument(
        "--max-abs-daily-return",
        type=float,
        default=None,
        help="drop tickers whose adjusted-close daily return exceeds this absolute value; data-quality diagnostic only",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    results, returns_by_name, benchmark_prices = build_heatmap_rows(args)
    results_path = RESULTS_DIR / "heatmap_results.csv"
    results.to_csv(results_path, index=False)
    (RESULTS_DIR / "heatmap_results.json").write_text(
        json.dumps(json_safe(results.to_dict(orient="records")), indent=2, allow_nan=False),
        encoding="utf-8",
    )
    plot_paths = write_static_heatmaps(results)
    finalist_plot_links = write_finalist_plots(results, returns_by_name, benchmark_prices)
    write_html_report(results, plot_paths, args)
    write_markdown_report(results, plot_paths, args, finalist_plot_links)
    print(f"wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    print(f"wrote {REPORT_HTML.relative_to(REPO_ROOT)}")
    print(f"wrote {results_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
