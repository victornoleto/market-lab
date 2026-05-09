"""Generate detailed reports for LETF rotation winner candidates.

Initial scope: render only the operative Sortino-first winner
``qld_voteK2_sma250_100_vol21_40_ar30_off_zroz``. The script is intentionally
data-first: every table and plot in the markdown is regenerated from daily
returns, SPY buy-and-hold, and the B4 original 25/25/25/25 benchmark.

Citations:
- Sortino as primary downside-risk metric: [advances_fin_ml, p.275]
- PBO / anti-curve-fit context: [advances_fin_ml, p.208-211]
- LETF trend-gating and long-duration OFF asset rationale:
  [leverage_for_the_long_run, p.5-6, p.16, p.21]
- B4 capital-efficient stacking benchmark: [risk_parity, ch.5, p.10]
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.run_iter_t5_extended import _run_single_extended
from studies.long_term_portfolio.run_iter import portfolio_returns_from_config


OUT_DIR = REPO / "studies/letf_rotation_hunt/reports/winners_deep_dive"
PLOTS_DIR = OUT_DIR / "plots"
DATA_DIR = OUT_DIR / "data"

TRADING_DAYS = 252
INITIAL_CAPITAL = 10_000.0
SLUG = "01_qld_voteK2_sma250_100_zroz"

STRATEGIES: list[dict] = [
    {
        "slug": "01_qld_voteK2_sma250_100_zroz",
        "title": "Winner Deep Dive 01 — QLD Vote-K2 SMA250/100 + ZROZ",
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
        "label": "Strategy",
        "rank_context": "vencedora operacional Sortino-first do estudo LETF",
        "family_note": "T3d Vote-K=2 com SMAs longas; melhor configuracao Sortino-first.",
        "engine": "composite",
        "cfg": {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
            "on_asset": "QLD",
            "off_asset": "ZROZ",
            "signal_type": "vote_of_k",
            "k": 2,
            "sma_long_period": 250,
            "sma_short_period": 100,
            "vol_window": 21,
            "vol_threshold": 0.40,
            "ar1_window": 30,
        },
    },
    {
        "slug": "02_qld_voteK2_sma200_50_zroz",
        "title": "Winner Deep Dive 02 — QLD Vote-K2 SMA200/50 + ZROZ",
        "name": "qld_voteK2_sma200_50_vol21_40_ar30_off_zroz",
        "label": "Strategy",
        "rank_context": "vencedora canonica historica sob Sharpe; supersedida por SMA250/100 sob Sortino",
        "family_note": "T3d Vote-K=2 canonica do estudo original, com SMA200/50.",
        "engine": "composite",
        "cfg": {
            "name": "qld_voteK2_sma200_50_vol21_40_ar30_off_zroz",
            "on_asset": "QLD",
            "off_asset": "ZROZ",
            "signal_type": "vote_of_k",
            "k": 2,
            "sma_long_period": 200,
            "sma_short_period": 50,
            "vol_window": 21,
            "vol_threshold": 0.40,
            "ar1_window": 30,
        },
    },
    {
        "slug": "03_t3d_k2_smabuf_5pct",
        "title": "Winner Deep Dive 03 — QLD Vote-K2 SMA Buffer 5% + ZROZ",
        "name": "t3d_k2_smabuf_5pct",
        "label": "Strategy",
        "rank_context": "melhor variante anti-whipsaw do threshold sweep",
        "family_note": "T3d Vote-K=2 com buffer simetrico de 5% nas SMAs para reduzir whipsaw.",
        "engine": "composite",
        "cfg": {
            "name": "t3d_k2_smabuf_5pct",
            "on_asset": "QLD",
            "off_asset": "ZROZ",
            "signal_type": "vote_of_k",
            "k": 2,
            "sma_long_buffer_on": 0.05,
            "sma_long_buffer_off": 0.05,
            "sma_short_buffer_on": 0.05,
            "sma_short_buffer_off": 0.05,
        },
    },
    {
        "slug": "04_tqqq_voteK2_zroz",
        "title": "Winner Deep Dive 04 — TQQQ Vote-K2 + ZROZ",
        "name": "tqqq_voteK2_off_zroz",
        "label": "Strategy",
        "rank_context": "alternativa agressiva nao-QLD com maior CAGR e risco maior",
        "family_note": "T3d Vote-K=2 aplicado a TQQQ 3x Nasdaq-100 com ZROZ como OFF.",
        "engine": "composite",
        "cfg": {
            "name": "tqqq_voteK2_off_zroz",
            "on_asset": "TQQQ",
            "off_asset": "ZROZ",
            "signal_type": "vote_of_k",
            "k": 2,
        },
    },
    {
        "slug": "05_erc_multi4_sigma030",
        "title": "Winner Deep Dive 05 — ERC Multi4 Sigma 30% + ZROZ",
        "name": "erc_multi4_sigma030",
        "label": "Strategy",
        "rank_context": "melhor configuracao T5 expandida, mas abaixo do threshold Sortino",
        "family_note": "Carver-style vol-target multi-asset com Equal Risk Contribution em UPRO/QLD/UGL/TMF.",
        "engine": "t5_extended",
        "cfg": {
            "name": "erc_multi4_sigma030",
            "pool": ["UPRO", "QLD", "UGL", "TMF"],
            "off_asset": "ZROZ",
            "sigma_target": 0.30,
            "idm": 1.0,
            "position_inertia": 0.1,
            "weighting_scheme": "erc",
        },
    },
]


@dataclass(frozen=True)
class SeriesBundle:
    name: str
    returns: pd.Series
    equity: pd.Series


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    spy_source = _bundle("SPY buy&hold", load_testfolio_series("SPYSIM").pct_change().dropna())
    b4_source = _bundle(
        "Plano C B4 original",
        portfolio_returns_from_config(
            {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
            "lh_56y",
        ),
    )

    for spec in STRATEGIES:
        _render_one(spec, spy_source, b4_source)

    (OUT_DIR / "STRUCTURE.md").write_text(_render_structure(), encoding="utf-8")
    print(f"wrote {len(STRATEGIES)} reports under {OUT_DIR}")
    return 0


def _render_one(spec: dict, spy_source: SeriesBundle, b4_source: SeriesBundle) -> None:
    global SLUG
    SLUG = spec["slug"]

    strategy_result = _load_strategy_result(spec)
    strategy = _bundle("Strategy", strategy_result["_strategy_returns"])
    spy = spy_source
    b4 = b4_source

    aligned = _align_bundles([strategy, spy, b4])
    strategy, spy, b4 = aligned

    signal = strategy_result["_signal"].reindex(strategy.returns.index).fillna(0.0)
    positions = strategy_result["_positions"].reindex(strategy.returns.index).dropna()

    daily = pd.DataFrame(
        {
            "strategy_ret": strategy.returns,
            "spy_ret": spy.returns,
            "b4_ret": b4.returns,
            "strategy_equity": strategy.equity,
            "spy_equity": spy.equity,
            "b4_equity": b4.equity,
            "signal_on_weight": signal,
        }
    )
    daily.to_csv(DATA_DIR / f"{SLUG}_daily_series.csv", index_label="date")

    metrics = _metrics_table([strategy, spy, b4])
    metrics.to_csv(DATA_DIR / f"{SLUG}_summary_metrics.csv", index=False)

    rolling = _rolling_summary(strategy, spy, b4)
    rolling.to_csv(DATA_DIR / f"{SLUG}_rolling_summary.csv", index=False)

    relative_windows = _rolling_relative_window_table(strategy, spy, b4)
    relative_windows.to_csv(DATA_DIR / f"{SLUG}_rolling_relative_windows.csv", index=False)

    forward = _forward_entry_table(strategy, spy, b4)
    forward.to_csv(DATA_DIR / f"{SLUG}_entry_forward_returns.csv", index=False)

    crisis = _crisis_table(strategy, spy, b4)
    crisis.to_csv(DATA_DIR / f"{SLUG}_crisis_windows.csv", index=False)

    regime = _regime_table(signal, positions)
    regime.to_csv(DATA_DIR / f"{SLUG}_regime_stats.csv", index=False)

    _plot_equity(strategy, spy, b4)
    _plot_relative(strategy, spy, b4)
    _plot_drawdown(strategy, spy, b4)
    _plot_rolling_cagr(strategy, spy, b4)
    _plot_rolling_relative_equity(relative_windows)
    _plot_rolling_psychology(relative_windows)
    _plot_rolling_winrate(rolling)
    _plot_entry_heatmap(forward)
    _plot_crisis_relative(strategy, spy, b4)

    (OUT_DIR / f"{SLUG}.md").write_text(
        _render_report(spec, metrics, rolling, relative_windows, forward, crisis, regime, strategy, spy, b4),
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR / f'{SLUG}.md'}")


def _load_strategy_result(spec: dict) -> dict:
    ffr_daily = load_ffr_daily()
    datasets = ["lh_56y", "modern_1990", "spy_real", "ndx_real"]
    if spec["engine"] == "composite":
        return _run_single_composite_config(
            spec["cfg"], datasets=datasets, ffr_daily=ffr_daily, n_trials_local=12,
        )
    if spec["engine"] == "t5_extended":
        return _run_single_extended(
            spec["cfg"], datasets=datasets, ffr_daily=ffr_daily, n_trials_local=4,
        )
    raise ValueError(f"unknown engine {spec['engine']!r}")


def _bundle(name: str, returns: pd.Series) -> SeriesBundle:
    returns = returns.dropna().sort_index()
    equity = (1.0 + returns).cumprod() * INITIAL_CAPITAL
    return SeriesBundle(name=name, returns=returns, equity=equity)


def _align_bundles(bundles: list[SeriesBundle]) -> list[SeriesBundle]:
    common = bundles[0].returns.index
    for bundle in bundles[1:]:
        common = common.intersection(bundle.returns.index)
    common = common.sort_values()
    out: list[SeriesBundle] = []
    for bundle in bundles:
        r = bundle.returns.reindex(common).dropna()
        out.append(_bundle(bundle.name, r))
    return out


def _ann_sharpe(returns: pd.Series) -> float:
    sd = returns.std(ddof=0)
    return float(returns.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def _ann_sortino(returns: pd.Series) -> float:
    downside = returns[returns < 0]
    sd = downside.std(ddof=0)
    return float(returns.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def _cagr(equity: pd.Series) -> float:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0)


def _mdd(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def _calmar(equity: pd.Series) -> float:
    dd = abs(_mdd(equity))
    return float(_cagr(equity) / dd) if dd > 0 else float("nan")


def _metrics(bundle: SeriesBundle) -> dict[str, float | str]:
    r = bundle.returns
    eq = bundle.equity
    return {
        "series": bundle.name,
        "start": str(r.index[0].date()),
        "end": str(r.index[-1].date()),
        "years": (r.index[-1] - r.index[0]).days / 365.25,
        "cagr": _cagr(eq),
        "mdd": _mdd(eq),
        "sharpe": _ann_sharpe(r),
        "sortino": _ann_sortino(r),
        "calmar": _calmar(eq),
        "vol_ann": float(r.std(ddof=0) * math.sqrt(TRADING_DAYS)),
        "skew": float(r.skew()),
        "kurt": float(r.kurt()),
        "final_equity": float(eq.iloc[-1]),
    }


def _metrics_table(bundles: list[SeriesBundle]) -> pd.DataFrame:
    return pd.DataFrame([_metrics(bundle) for bundle in bundles])


def _rolling_series(returns: pd.Series, years: int, metric: str) -> pd.Series:
    win = years * TRADING_DAYS
    if len(returns) < win:
        return pd.Series(dtype=float)
    if metric == "sharpe":
        mu = returns.rolling(win).mean()
        sd = returns.rolling(win).std(ddof=0)
        return (mu / sd * math.sqrt(TRADING_DAYS)).dropna()
    if metric == "sortino":
        mu = returns.rolling(win).mean()
        downside = returns.where(returns < 0, 0.0)
        semi = downside.rolling(win).std(ddof=0)
        return (mu / semi * math.sqrt(TRADING_DAYS)).replace([np.inf, -np.inf], np.nan).dropna()
    if metric == "cagr":
        eq = (1.0 + returns).cumprod()
        return (eq / eq.shift(win)) ** (1.0 / years) - 1.0
    raise ValueError(metric)


def _rolling_summary(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> pd.DataFrame:
    rows: list[dict] = []
    for years in [3, 5, 10, 15]:
        s = _rolling_series(strategy.returns, years, "sharpe")
        spy_s = _rolling_series(spy.returns, years, "sharpe")
        b4_s = _rolling_series(b4.returns, years, "sharpe")
        common_spy = s.index.intersection(spy_s.index)
        common_b4 = s.index.intersection(b4_s.index)

        cagr_s = _rolling_series(strategy.returns, years, "cagr").dropna()
        cagr_spy = _rolling_series(spy.returns, years, "cagr").dropna()
        cagr_b4 = _rolling_series(b4.returns, years, "cagr").dropna()
        common_cagr_spy = cagr_s.index.intersection(cagr_spy.index)
        common_cagr_b4 = cagr_s.index.intersection(cagr_b4.index)

        rows.append(
            {
                "window_years": years,
                "n_windows": int(len(s)),
                "median_sharpe": float(s.median()),
                "p10_sharpe": float(s.quantile(0.10)),
                "p90_sharpe": float(s.quantile(0.90)),
                "median_cagr": float(cagr_s.median()),
                "p10_cagr": float(cagr_s.quantile(0.10)),
                "p90_cagr": float(cagr_s.quantile(0.90)),
                "winrate_sharpe_vs_spy": _winrate(s.loc[common_spy], spy_s.loc[common_spy]),
                "winrate_sharpe_vs_b4": _winrate(s.loc[common_b4], b4_s.loc[common_b4]),
                "winrate_cagr_vs_spy": _winrate(cagr_s.loc[common_cagr_spy], cagr_spy.loc[common_cagr_spy]),
                "winrate_cagr_vs_b4": _winrate(cagr_s.loc[common_cagr_b4], cagr_b4.loc[common_cagr_b4]),
            }
        )
    return pd.DataFrame(rows)


def _rolling_relative_window_table(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> pd.DataFrame:
    """Monthly-start relative-equity windows against SPY and B4.

    For each start date and horizon, both strategy and benchmark are rebased to
    1.0. The resulting ratio answers the behavioral question: how often did the
    strategy's equity stay above the benchmark during that investor's holding
    window, how deep did relative underperformance get, and how long did the
    longest recovery spell last.
    """
    rows: list[dict] = []
    entry_dates = strategy.equity.resample("ME").last().index
    benchmarks = {"SPY": spy.equity, "B4": b4.equity}
    for entry in entry_dates:
        eligible = strategy.equity.index[strategy.equity.index <= entry]
        if len(eligible) == 0:
            continue
        start = eligible[-1]
        start_pos = strategy.equity.index.searchsorted(start)
        for years in [3, 5, 10, 15]:
            exit_pos = start_pos + years * TRADING_DAYS
            if exit_pos >= len(strategy.equity):
                continue
            end = strategy.equity.index[exit_pos]
            s = strategy.equity.loc[start:end]
            s_norm = s / float(s.iloc[0])
            for bench_name, bench_eq in benchmarks.items():
                b = bench_eq.loc[start:end]
                common = s_norm.index.intersection(b.index)
                if len(common) < 2:
                    continue
                ratio = s_norm.loc[common] / (b.loc[common] / float(b.loc[common].iloc[0]))
                under = ratio < 1.0
                rows.append(
                    {
                        "benchmark": bench_name,
                        "start_date": str(start.date()),
                        "end_date": str(end.date()),
                        "start_year": int(start.year),
                        "horizon_years": years,
                        "pct_days_above_benchmark": float((ratio > 1.0).mean()),
                        "pct_days_below_benchmark": float(under.mean()),
                        "final_relative_equity": float(ratio.iloc[-1]),
                        "min_relative_equity": float(ratio.min()),
                        "max_relative_drawdown_vs_benchmark": float(ratio.min() - 1.0),
                        "total_days_below_benchmark": int(under.sum()),
                        "max_consecutive_days_below_benchmark": int(_max_consecutive_true(under)),
                    }
                )
    return pd.DataFrame(rows)


def _max_consecutive_true(mask: pd.Series) -> int:
    best = current = 0
    for value in mask.astype(bool).to_numpy():
        if value:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _winrate(a: pd.Series, b: pd.Series) -> float:
    if len(a) == 0:
        return float("nan")
    return float((a > b).mean())


def _forward_entry_table(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> pd.DataFrame:
    rows: list[dict] = []
    eqs = {"strategy": strategy.equity, "spy": spy.equity, "b4": b4.equity}
    # Monthly entry dates keep the table readable while preserving entry-date path dependence.
    entry_dates = strategy.equity.resample("ME").last().index
    for entry in entry_dates:
        if entry not in strategy.equity.index:
            eligible = strategy.equity.index[strategy.equity.index <= entry]
            if len(eligible) == 0:
                continue
            entry = eligible[-1]
        for years in [1, 3, 5, 10]:
            exit_pos = strategy.equity.index.searchsorted(entry) + years * TRADING_DAYS
            if exit_pos >= len(strategy.equity):
                continue
            exit_date = strategy.equity.index[exit_pos]
            row: dict[str, float | str | int] = {
                "entry_date": str(entry.date()),
                "exit_date": str(exit_date.date()),
                "entry_year": int(entry.year),
                "horizon_years": years,
            }
            for name, eq in eqs.items():
                ratio = float(eq.loc[exit_date] / eq.loc[entry])
                row[f"{name}_cagr"] = ratio ** (1.0 / years) - 1.0
            row["strategy_edge_vs_spy"] = float(row["strategy_cagr"] - row["spy_cagr"])
            row["strategy_edge_vs_b4"] = float(row["strategy_cagr"] - row["b4_cagr"])
            rows.append(row)
    return pd.DataFrame(rows)


def _crisis_table(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> pd.DataFrame:
    windows = {
        "dotcom": ("2000-03-24", "2002-10-09"),
        "gfc": ("2007-10-09", "2009-03-09"),
        "covid": ("2020-02-19", "2020-06-30"),
        "rates_2022": ("2021-12-27", "2022-12-30"),
    }
    rows: list[dict] = []
    for name, (start, end) in windows.items():
        row: dict[str, float | str] = {"crisis": name, "start": start, "end": end}
        for bundle in [strategy, spy, b4]:
            r = bundle.returns.loc[start:end]
            if len(r) < 2:
                row[f"{bundle.name}_return"] = float("nan")
                row[f"{bundle.name}_mdd"] = float("nan")
                continue
            eq = (1.0 + r).cumprod()
            row[f"{bundle.name}_return"] = float(eq.iloc[-1] / eq.iloc[0] - 1.0)
            row[f"{bundle.name}_mdd"] = _mdd(eq)
        rows.append(row)
    return pd.DataFrame(rows)


def _regime_table(signal: pd.Series, positions: pd.DataFrame) -> pd.DataFrame:
    on = (signal >= 0.5).astype(int)
    switches = int(on.diff().abs().fillna(0).sum())
    runs = []
    if len(on) > 0:
        run_id = on.ne(on.shift()).cumsum()
        for _, values in on.groupby(run_id):
            runs.append({"state": int(values.iloc[0]), "days": int(len(values))})
    run_df = pd.DataFrame(runs)
    qld_weight = float(positions.get("QLD", pd.Series(dtype=float)).mean()) if not positions.empty else float("nan")
    zroz_weight = float(positions.get("ZROZ", pd.Series(dtype=float)).mean()) if not positions.empty else float("nan")
    return pd.DataFrame(
        [
            {"metric": "pct_days_on_qld", "value": float(on.mean())},
            {"metric": "pct_days_off_zroz", "value": float(1.0 - on.mean())},
            {"metric": "switch_count", "value": float(switches)},
            {"metric": "avg_qld_weight", "value": qld_weight},
            {"metric": "avg_zroz_weight", "value": zroz_weight},
            {"metric": "avg_on_run_days", "value": _safe_run_mean(run_df, 1)},
            {"metric": "avg_off_run_days", "value": _safe_run_mean(run_df, 0)},
        ]
    )


def _safe_run_mean(run_df: pd.DataFrame, state: int) -> float:
    if run_df.empty:
        return float("nan")
    vals = run_df.loc[run_df["state"] == state, "days"]
    return float(vals.mean()) if len(vals) else float("nan")


def _relative_psychology_summary(relative_windows: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (benchmark, years), group in relative_windows.groupby(["benchmark", "horizon_years"]):
        rows.append(
            {
                "benchmark": benchmark,
                "horizon_years": int(years),
                "n_windows": int(len(group)),
                "median_pct_days_above_benchmark": float(group["pct_days_above_benchmark"].median()),
                "p10_pct_days_above_benchmark": float(group["pct_days_above_benchmark"].quantile(0.10)),
                "median_min_relative_equity": float(group["min_relative_equity"].median()),
                "p10_min_relative_equity": float(group["min_relative_equity"].quantile(0.10)),
                "median_max_consecutive_days_below_benchmark": float(group["max_consecutive_days_below_benchmark"].median()),
                "p90_max_consecutive_days_below_benchmark": float(group["max_consecutive_days_below_benchmark"].quantile(0.90)),
            }
        )
    return pd.DataFrame(rows).sort_values(["benchmark", "horizon_years"])


def _plot_equity(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for bundle, color, lw in [(strategy, "#0b5fff", 2.0), (spy, "#555555", 1.5), (b4, "#1b9e77", 1.7)]:
        ax.plot(bundle.equity.index, bundle.equity, label=f"{bundle.name} (${bundle.equity.iloc[-1]:,.0f})", color=color, lw=lw)
    ax.set_yscale("log")
    ax.set_title("Equity growth: strategy vs SPY buy&hold vs Plano C B4 original")
    ax.set_ylabel("Equity from $10,000, log scale")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_equity_vs_spy_b4.png", dpi=120)
    plt.close(fig)


def _plot_relative(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> None:
    rel_spy = strategy.equity / spy.equity
    rel_b4 = strategy.equity / b4.equity
    rel_spy = rel_spy / rel_spy.iloc[0]
    rel_b4 = rel_b4 / rel_b4.iloc[0]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(rel_spy.index, rel_spy, label=f"Strategy / SPY ({rel_spy.iloc[-1]:.1f}x)", color="#0b5fff", lw=2.0)
    ax.plot(rel_b4.index, rel_b4, label=f"Strategy / B4 ({rel_b4.iloc[-1]:.1f}x)", color="#d95f02", lw=2.0)
    ax.axhline(1.0, color="black", ls="--", lw=1.0)
    ax.set_yscale("log")
    ax.set_title("Relative equity: strategy divided by each benchmark")
    ax.set_ylabel("Relative wealth, normalized to 1.0")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_relative_to_spy_b4.png", dpi=120)
    plt.close(fig)


def _plot_drawdown(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    for bundle, color in [(strategy, "#0b5fff"), (spy, "#555555"), (b4, "#1b9e77")]:
        dd = bundle.equity / bundle.equity.cummax() - 1.0
        ax.fill_between(dd.index, dd.values, 0, alpha=0.18, color=color)
        ax.plot(dd.index, dd.values, label=f"{bundle.name} ({dd.min():.0%})", color=color, lw=1.2)
    ax.set_title("Drawdown: strategy vs SPY vs B4")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_drawdown_vs_spy_b4.png", dpi=120)
    plt.close(fig)


def _plot_rolling_cagr(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False)
    for years, ax in zip([3, 5, 10, 15], axes.ravel()):
        for bundle, color in [(strategy, "#0b5fff"), (spy, "#555555"), (b4, "#1b9e77")]:
            rc = _rolling_series(bundle.returns, years, "cagr")
            ax.plot(rc.index, rc, label=bundle.name, color=color, lw=1.2)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(f"Rolling {years}y CAGR")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _pos: f"{x:.0%}"))
        ax.grid(True, alpha=0.25)
    axes.ravel()[0].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_rolling_cagr.png", dpi=120)
    plt.close(fig)


def _plot_rolling_relative_equity(relative_windows: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False)
    for years, ax in zip([3, 5, 10, 15], axes.ravel()):
        subset = relative_windows[relative_windows["horizon_years"] == years].copy()
        for bench, color in [("SPY", "#555555"), ("B4", "#1b9e77")]:
            b = subset[subset["benchmark"] == bench].copy()
            b["start_date"] = pd.to_datetime(b["start_date"])
            ax.plot(
                b["start_date"], b["final_relative_equity"],
                label=f"Strategy / {bench}", color=color, lw=1.2,
            )
        ax.axhline(1.0, color="black", ls="--", lw=0.9)
        ax.set_yscale("log")
        ax.set_title(f"Final relative equity by start date, {years}y hold")
        ax.set_ylabel("strategy equity / benchmark equity")
        ax.grid(True, which="both", alpha=0.25)
    axes.ravel()[0].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_rolling_relative_equity_vs_spy_b4.png", dpi=120)
    plt.close(fig)


def _plot_rolling_psychology(relative_windows: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False)
    for years, ax in zip([3, 5, 10, 15], axes.ravel()):
        subset = relative_windows[relative_windows["horizon_years"] == years].copy()
        for bench, color in [("SPY", "#555555"), ("B4", "#1b9e77")]:
            b = subset[subset["benchmark"] == bench].copy()
            b["start_date"] = pd.to_datetime(b["start_date"])
            ax.plot(
                b["start_date"], b["pct_days_above_benchmark"],
                label=f"% days above {bench}", color=color, lw=1.2,
            )
        ax.axhline(0.5, color="black", ls="--", lw=0.9)
        ax.set_ylim(0, 1.02)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _pos: f"{y:.0%}"))
        ax.set_title(f"Pct of days above benchmark, {years}y hold")
        ax.grid(True, alpha=0.25)
    axes.ravel()[0].legend(loc="lower left", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_rolling_pct_days_above_benchmark.png", dpi=120)
    plt.close(fig)


def _plot_rolling_winrate(rolling: pd.DataFrame) -> None:
    x = np.arange(len(rolling))
    width = 0.2
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x - width * 1.5, rolling["winrate_sharpe_vs_spy"], width, label="Sharpe vs SPY", color="#555555")
    ax.bar(x - width * 0.5, rolling["winrate_sharpe_vs_b4"], width, label="Sharpe vs B4", color="#1b9e77")
    ax.bar(x + width * 0.5, rolling["winrate_cagr_vs_spy"], width, label="CAGR vs SPY", color="#999999")
    ax.bar(x + width * 1.5, rolling["winrate_cagr_vs_b4"], width, label="CAGR vs B4", color="#66c2a5")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(v)}y" for v in rolling["window_years"]])
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _pos: f"{y:.0%}"))
    ax.set_title("Rolling-window win rate by metric and benchmark")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_rolling_winrate_vs_spy_b4.png", dpi=120)
    plt.close(fig)


def _plot_entry_heatmap(forward: pd.DataFrame) -> None:
    pivot = forward.pivot_table(index="entry_year", columns="horizon_years", values="strategy_edge_vs_b4", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 10))
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", vmin=-0.15, vmax=0.15)
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels([f"{int(c)}y" for c in pivot.columns])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([str(int(y)) for y in pivot.index])
    ax.set_title("Entry-date forward CAGR edge vs B4, average by entry year")
    ax.set_xlabel("Forward holding horizon")
    ax.set_ylabel("Entry year")
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _pos: f"{y:.0%}"))
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_entry_date_forward_returns_heatmap.png", dpi=120)
    plt.close(fig)


def _plot_crisis_relative(strategy: SeriesBundle, spy: SeriesBundle, b4: SeriesBundle) -> None:
    windows = {
        "dotcom": ("2000-03-24", "2002-10-09"),
        "gfc": ("2007-10-09", "2009-03-09"),
        "covid": ("2020-02-19", "2020-06-30"),
        "rates_2022": ("2021-12-27", "2022-12-30"),
    }
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, (name, (start, end)) in zip(axes.ravel(), windows.items()):
        s = strategy.equity.loc[start:end]
        spy_eq = spy.equity.loc[start:end]
        b4_eq = b4.equity.loc[start:end]
        if min(len(s), len(spy_eq), len(b4_eq)) < 2:
            continue
        rel_spy = (s / s.iloc[0]) / (spy_eq / spy_eq.iloc[0])
        rel_b4 = (s / s.iloc[0]) / (b4_eq / b4_eq.iloc[0])
        ax.plot(rel_spy.index, rel_spy, label="Strategy / SPY", color="#555555", lw=1.5)
        ax.plot(rel_b4.index, rel_b4, label="Strategy / B4", color="#1b9e77", lw=1.5)
        ax.axhline(1.0, color="black", ls="--", lw=0.8)
        ax.set_title(name)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{SLUG}_crisis_relative_equity.png", dpi=120)
    plt.close(fig)


def _pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x:.2%}"


def _num(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x:.3f}"


def _money(x: float) -> str:
    return "n/a" if pd.isna(x) else f"${x:,.0f}"


def _md_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None) -> str:
    formats = formats or {}
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in df.iterrows():
        vals = []
        for col in columns:
            val = row[col]
            fmt = formats.get(col)
            if fmt == "pct":
                vals.append(_pct(float(val)))
            elif fmt == "num":
                vals.append(_num(float(val)))
            elif fmt == "money":
                vals.append(_money(float(val)))
            elif fmt == "years":
                vals.append(f"{float(val):.1f}")
            elif fmt == "int":
                vals.append(str(int(round(float(val)))))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def _render_structure() -> str:
    return """# Winners Deep Dive — Structure

Cada relatório desta pasta deve ser gerado por `studies/letf_rotation_hunt/scripts/generate_winners_deep_dive.py` e seguir esta ordem:

1. `Resumo Executivo`
2. `Definicao Operacional`
3. `Benchmark Set`
4. `Metricas Principais`
5. `Equity E Relativo Aos Benchmarks`
6. `Rolling Windows`
7. `Entry-Date Analysis`
8. `Crises E Regimes`
9. `Comportamento ON/OFF`
10. `Limitacoes E Veredito`
11. `Artefatos Gerados`

Benchmarks obrigatorios:

- SPY buy-and-hold via `SPYSIM`.
- Plano C B4 original: `25% NTSXSIM / 25% GDESIM / 25% RSSTSIM / 25% ZROZSIM`.

Padrao de janela:

- Comparacao principal sempre usa a intersecao diaria entre estrategia, SPY e B4.
- Se a estrategia tiver historico maior que B4, mencionar como limitacao em vez de misturar janelas.

Metricas obrigatorias:

- CAGR, MDD, Sharpe, Sortino, Calmar, vol anualizada, skew, kurtosis, equity final.
- Rolling 3y/5y/10y/15y, com win-rate contra SPY e B4.
- Rolling relative equity 3y/5y/10y/15y por start date: equity da estrategia / equity do benchmark, percentual de dias acima, minimo relativo e maior sequencia abaixo do benchmark.
- Forward returns por data de entrada 1y/3y/5y/10y.
- Crises: dotcom, GFC, COVID, rates 2022.

Toda decisao de indicador, parametro, gate ou benchmark deve citar fonte no formato do projeto, quando aplicavel.
"""


def _render_report(
    spec: dict,
    metrics: pd.DataFrame,
    rolling: pd.DataFrame,
    relative_windows: pd.DataFrame,
    forward: pd.DataFrame,
    crisis: pd.DataFrame,
    regime: pd.DataFrame,
    strategy: SeriesBundle,
    spy: SeriesBundle,
    b4: SeriesBundle,
) -> str:
    worst_b4 = forward.sort_values("strategy_edge_vs_b4").head(10)
    worst_spy = forward.sort_values("strategy_edge_vs_spy").head(10)
    best_b4 = forward.sort_values("strategy_edge_vs_b4", ascending=False).head(10)
    strat_row = metrics.loc[metrics["series"] == "Strategy"].iloc[0]
    spy_row = metrics.loc[metrics["series"] == "SPY buy&hold"].iloc[0]
    b4_row = metrics.loc[metrics["series"] == "Plano C B4 original"].iloc[0]
    psych_summary = _relative_psychology_summary(relative_windows)
    worst_relative_b4 = relative_windows[relative_windows["benchmark"] == "B4"].sort_values("min_relative_equity").head(10)
    worst_recovery_b4 = relative_windows[relative_windows["benchmark"] == "B4"].sort_values("max_consecutive_days_below_benchmark", ascending=False).head(10)
    definition = _render_definition(spec)
    note = _sortino_window_note(spec, strat_row)
    method_note = _methodology_note(spec)
    verdict_line = _verdict_line(spec)

    return f"""# {spec['title']}

## Resumo Executivo

Esta e a {spec['rank_context']}: `{spec['name']}`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **{_pct(float(strat_row['cagr']))}**, Sortino **{_num(float(strat_row['sortino']))}** e MDD **{_pct(float(strat_row['mdd']))}**. O SPY buy-and-hold fica em CAGR **{_pct(float(spy_row['cagr']))}** / Sortino **{_num(float(spy_row['sortino']))}**, enquanto o Plano C B4 original fica em CAGR **{_pct(float(b4_row['cagr']))}** / Sortino **{_num(float(b4_row['sortino']))}**.

{note}

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

{definition}

{method_note}

## Benchmark Set

- `SPY buy&hold`: `SPYSIM`, comprado e mantido.
- `Plano C B4 original`: 25% `NTSXSIM`, 25% `GDESIM`, 25% `RSSTSIM`, 25% `ZROZSIM`.
- Janela comum: `{strategy.returns.index[0].date()}` a `{strategy.returns.index[-1].date()}`.
- Capital inicial normalizado: `${INITIAL_CAPITAL:,.0f}`.

O B4 e capital-efficient stacking: NTSX empilha equity + Treasuries, GDE empilha equity + ouro, RSST empilha equity + managed futures, e ZROZ adiciona duration convexa `[risk_parity, ch.5, p.10]`.

## Metricas Principais

{_md_table(metrics, ['series', 'start', 'end', 'years', 'cagr', 'mdd', 'sharpe', 'sortino', 'calmar', 'vol_ann', 'final_equity'], {'years': 'years', 'cagr': 'pct', 'mdd': 'pct', 'sharpe': 'num', 'sortino': 'num', 'calmar': 'num', 'vol_ann': 'pct', 'final_equity': 'money'})}

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/{SLUG}_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/{SLUG}_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/{SLUG}_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/{SLUG}_rolling_cagr.png)

![Rolling relative equity](plots/{SLUG}_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/{SLUG}_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/{SLUG}_rolling_winrate_vs_spy_b4.png)

{_md_table(rolling, ['window_years', 'n_windows', 'median_sharpe', 'p10_sharpe', 'p90_sharpe', 'median_cagr', 'p10_cagr', 'p90_cagr', 'winrate_sharpe_vs_spy', 'winrate_sharpe_vs_b4', 'winrate_cagr_vs_spy', 'winrate_cagr_vs_b4'], {'window_years': 'int', 'n_windows': 'int', 'median_sharpe': 'num', 'p10_sharpe': 'num', 'p90_sharpe': 'num', 'median_cagr': 'pct', 'p10_cagr': 'pct', 'p90_cagr': 'pct', 'winrate_sharpe_vs_spy': 'pct', 'winrate_sharpe_vs_b4': 'pct', 'winrate_cagr_vs_spy': 'pct', 'winrate_cagr_vs_b4': 'pct'})}

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

{_md_table(psych_summary, ['benchmark', 'horizon_years', 'n_windows', 'median_pct_days_above_benchmark', 'p10_pct_days_above_benchmark', 'median_min_relative_equity', 'p10_min_relative_equity', 'median_max_consecutive_days_below_benchmark', 'p90_max_consecutive_days_below_benchmark'], {'horizon_years': 'int', 'n_windows': 'int', 'median_pct_days_above_benchmark': 'pct', 'p10_pct_days_above_benchmark': 'pct', 'median_min_relative_equity': 'num', 'p10_min_relative_equity': 'num', 'median_max_consecutive_days_below_benchmark': 'int', 'p90_max_consecutive_days_below_benchmark': 'int'})}

Piores janelas contra B4 por profundidade relativa:

{_md_table(worst_relative_b4, ['start_date', 'end_date', 'horizon_years', 'pct_days_above_benchmark', 'final_relative_equity', 'min_relative_equity', 'max_consecutive_days_below_benchmark'], {'horizon_years': 'int', 'pct_days_above_benchmark': 'pct', 'final_relative_equity': 'num', 'min_relative_equity': 'num', 'max_consecutive_days_below_benchmark': 'int'})}

Janelas contra B4 com maior sequencia abaixo do benchmark:

{_md_table(worst_recovery_b4, ['start_date', 'end_date', 'horizon_years', 'pct_days_above_benchmark', 'final_relative_equity', 'min_relative_equity', 'max_consecutive_days_below_benchmark'], {'horizon_years': 'int', 'pct_days_above_benchmark': 'pct', 'final_relative_equity': 'num', 'min_relative_equity': 'num', 'max_consecutive_days_below_benchmark': 'int'})}

## Entry-Date Analysis

![Entry heatmap](plots/{SLUG}_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

{_md_table(worst_b4, ['entry_date', 'exit_date', 'horizon_years', 'strategy_cagr', 'b4_cagr', 'strategy_edge_vs_b4'], {'horizon_years': 'int', 'strategy_cagr': 'pct', 'b4_cagr': 'pct', 'strategy_edge_vs_b4': 'pct'})}

Piores entradas contra SPY, por CAGR forward:

{_md_table(worst_spy, ['entry_date', 'exit_date', 'horizon_years', 'strategy_cagr', 'spy_cagr', 'strategy_edge_vs_spy'], {'horizon_years': 'int', 'strategy_cagr': 'pct', 'spy_cagr': 'pct', 'strategy_edge_vs_spy': 'pct'})}

Melhores entradas contra B4:

{_md_table(best_b4, ['entry_date', 'exit_date', 'horizon_years', 'strategy_cagr', 'b4_cagr', 'strategy_edge_vs_b4'], {'horizon_years': 'int', 'strategy_cagr': 'pct', 'b4_cagr': 'pct', 'strategy_edge_vs_b4': 'pct'})}

## Crises E Regimes

![Crise relativa](plots/{SLUG}_crisis_relative_equity.png)

{_md_table(crisis, list(crisis.columns), {col: 'pct' for col in crisis.columns if col.endswith('_return') or col.endswith('_mdd')})}

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

{_md_table(regime, ['metric', 'value'], {'value': 'num'})}

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: {verdict_line}

## Artefatos Gerados

- `data/{SLUG}_daily_series.csv`
- `data/{SLUG}_summary_metrics.csv`
- `data/{SLUG}_rolling_summary.csv`
- `data/{SLUG}_rolling_relative_windows.csv`
- `data/{SLUG}_entry_forward_returns.csv`
- `data/{SLUG}_crisis_windows.csv`
- `data/{SLUG}_regime_stats.csv`
- `plots/{SLUG}_equity_vs_spy_b4.png`
- `plots/{SLUG}_relative_to_spy_b4.png`
- `plots/{SLUG}_drawdown_vs_spy_b4.png`
- `plots/{SLUG}_rolling_cagr.png`
- `plots/{SLUG}_rolling_relative_equity_vs_spy_b4.png`
- `plots/{SLUG}_rolling_pct_days_above_benchmark.png`
- `plots/{SLUG}_rolling_winrate_vs_spy_b4.png`
- `plots/{SLUG}_entry_date_forward_returns_heatmap.png`
- `plots/{SLUG}_crisis_relative_equity.png`
"""


def _render_definition(spec: dict) -> str:
    cfg = spec["cfg"]
    if spec["engine"] == "composite":
        sma_long = int(cfg.get("sma_long_period", 200))
        sma_short = int(cfg.get("sma_short_period", 50))
        vol_window = int(cfg.get("vol_window", 21))
        vol_threshold = float(cfg.get("vol_threshold", 0.40))
        ar1_window = int(cfg.get("ar1_window", 30))
        buf = float(cfg.get("sma_long_buffer_on", 0.0))
        buffer_line = ""
        if buf > 0:
            buffer_line = f"\n- Buffer: sinal de SMA exige margem simetrica de {buf:.0%} para reduzir whipsaw."
        return f"""- Familia: {spec['family_note']}
- Risk-on: `{cfg['on_asset']}`.
- Risk-off: `{cfg['off_asset']}`.
- Sinal: Vote-of-K com `K={cfg['k']}` sobre quatro sinais diarios.
- Sinal 1: preco do QQQ/NDX acima da SMA{sma_long}.
- Sinal 2: preco do QQQ/NDX acima da SMA{sma_short}.
- Sinal 3: volatilidade realizada de {vol_window} dias abaixo de {vol_threshold:.0%} anualizado.
- Sinal 4: AR(1) de {ar1_window} dias acima de 0.{buffer_line}
- Regra ON: ficar 100% `{cfg['on_asset']}` quando pelo menos {cfg['k']} dos 4 sinais estao ON.
- Regra OFF: ficar 100% `{cfg['off_asset']}` caso contrario."""
    if spec["engine"] == "t5_extended":
        return f"""- Familia: {spec['family_note']}
- Pool risk-on: `{', '.join(cfg['pool'])}`.
- Risk-off/cash defensivo: `{cfg['off_asset']}`.
- Forecast: EWMAC padrao do dispatcher T5 com vol targeting.
- Weighting: Equal Risk Contribution (`erc`) sobre o pool.
- Sigma target anual: {float(cfg['sigma_target']):.0%}.
- Position inertia: {float(cfg['position_inertia']):.0%}.
- Regra: alocar continuamente nos ativos do pool conforme forecast/vol alvo; excedente fica em `{cfg['off_asset']}` `[systematic_trading, ch.7-12 p.98-202]`, `[advances_fin_ml, ch.16 p.221-228]`."""
    raise ValueError(f"unknown engine {spec['engine']!r}")


def _sortino_window_note(spec: dict, strat_row: pd.Series) -> str:
    if spec["slug"] == "01_qld_voteK2_sma250_100_zroz":
        return (
            f"Nota de leitura: o estudo final reportou Sortino **1.325** para esta estrategia no dataset `lh_56y` completo. "
            f"Aqui, a metrica cai para **{_num(float(strat_row['sortino']))}** porque a comparacao principal e forçada para a intersecao com B4 (`1988-2026`). "
            "Isso evita comparar a estrategia em uma janela e o Plano C em outra."
        )
    return (
        "Nota de leitura: as metricas deste relatorio sao recalculadas na janela comum contra B4 (`1988-2026`). "
        "Elas podem divergir dos numeros do `STUDY_FINAL_REPORT.md`, que por vezes usa `lh_56y` completo ou janelas especificas por sub-estudo."
    )


def _methodology_note(spec: dict) -> str:
    if spec["engine"] == "t5_extended":
        return (
            "O uso de Sortino como metrica primaria e adequado porque LETF rotation busca capturar upside convexo e nao deve penalizar volatilidade positiva simetricamente como Sharpe `[advances_fin_ml, p.275]`. "
            "Esta configuracao pertence a familia Carver de forecast + vol targeting, onde forecast, volatilidade realizada, diversificacao e inertia governam sizing `[systematic_trading, ch.7-12 p.98-202]`. "
            "O peso ERC substitui IDM uniforme por contribuicao igual de risco, inspirado em alocacao hierarquica/risk-based `[advances_fin_ml, ch.16 p.221-228]`."
        )
    return (
        "O uso de Sortino como metrica primaria e adequado porque LETF rotation busca capturar upside convexo e nao deve penalizar volatilidade positiva simetricamente como Sharpe `[advances_fin_ml, p.275]`. "
        "A familia SMA/LETF vem da tese de trend-following aplicada a leveraged ETFs `[leverage_for_the_long_run, p.5-6, p.16]`. "
        "ZROZ como OFF asset preserva a convexidade defensiva de duration longa, com ressalva de choque de juros como 2022 `[leverage_for_the_long_run, p.21]`."
    )


def _verdict_line(spec: dict) -> str:
    if spec["slug"] == "01_qld_voteK2_sma250_100_zroz":
        return "excelente candidata de pesquisa e a melhor configuracao Sortino-first encontrada, mas ainda deve ser tratada como monitoramento/paper research, nao como carteira real."
    if spec["slug"] == "02_qld_voteK2_sma200_50_zroz":
        return "forte baseline canonico e referencia historica do estudo, mas a variante SMA250/100 melhora a robustez de cauda e tomou o posto operacional sob Sortino."
    if spec["slug"] == "03_t3d_k2_smabuf_5pct":
        return "variante interessante para reduzir whipsaw e friccao, especialmente se imposto/slippage forem centrais, mas ainda precisa revalidacao completa antes de qualquer consideracao operacional."
    if spec["slug"] == "04_tqqq_voteK2_zroz":
        return "alternativa agressiva com maior potencial de CAGR e maior carga psicologica; util para comparacao, nao como substituta automatica da QLD winner."
    return "melhor representante da familia T5 expandida, util como diversificador metodologico, mas inferior ao threshold Sortino que manteria a familia viva como candidata principal."


if __name__ == "__main__":
    raise SystemExit(main())
