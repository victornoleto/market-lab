#!/usr/bin/env python3
"""Iter 058 — B4 core plus GA repair satellites.

Research question: if the long-term portfolio uses a defensive B4-like core,
does a 20-30% active LETF repair sleeve improve the full portfolio while staying
operationally simple? The primary candidate is 75% B4 + 25% evo02, with monthly
rebalance and monthly contributions.

The satellite candidates come from the repair GA discovery suite. They remain
research-only; PBO/DSR/OOS validation is still required before deployment
claims `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`. B4 stacking follows the capital-efficient
portfolio rationale `[risk_parity, ch.5, p.10]`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.long_term_portfolio.run_iter import portfolio_returns_from_config


ITER_DIR = Path(__file__).parent
TABLES_DIR = ITER_DIR / "tables"
PLOTS_DIR = ITER_DIR / "plots"
STARTING_CAPITAL = 10_000.0
MONTHLY_CONTRIBUTION = 1_000.0
TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class StrategyConfig:
    slug: str
    label: str
    weights: dict[str, float]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GA = _load_module(
    REPO / "studies/technical_signal_vote_hunt/runners/run_repair_ga_evolutions.py",
    "iter058_repair_ga",
)


def main() -> int:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    components = _component_returns()
    configs = _configs()
    strategy_returns = {
        cfg.slug: _monthly_rebalanced_returns(components, cfg.weights)
        for cfg in configs
    }
    strategy_returns["SPY"] = _bench_returns("SPYSIM", strategy_returns)
    strategy_returns["QQQ"] = _bench_returns("QQQSIM", strategy_returns)
    strategy_returns["VT"] = _bench_returns("VTSIM", strategy_returns)

    contribution_curves = {
        cfg.slug: _simulate_contribution_account(components, cfg.weights)
        for cfg in configs
    }

    perf = _performance_table(strategy_returns, contribution_curves, [c.slug for c in configs])
    rolling = _rolling_table(strategy_returns, [c.slug for c in configs], ["b4_100", "SPY", "QQQ", "VT"])

    _write_tables(perf, rolling, strategy_returns, contribution_curves)
    _write_plots(strategy_returns, contribution_curves, [c.slug for c in configs])
    _write_report(perf, rolling, configs)
    _write_results_json(strategy_returns, contribution_curves, perf, rolling, configs)

    print(f"wrote {ITER_DIR / 'REPORT.md'}")
    print(perf[["strategy", "cagr", "mdd", "sharpe", "sortino", "final_value", "xirr"]].to_string(index=False))
    return 0


def _component_returns() -> dict[str, pd.Series]:
    ctx = GA._prepare_context()
    genes = {
        "evo01": GA.Gene("QQQ", 180, 75, 10, 0.25, 20, 4, 30, 45, 1.00, 1.20, 0.50, 60, 0.70),
        "evo02": GA.Gene("QQQ", 225, 50, 42, 0.25, 30, 3, 20, 60, 1.00, 1.00, 0.50, 60, 0.70),
        "evo05": GA.Gene("QLD", 225, 100, 21, 0.50, 40, 2, 15, 120, 1.00, 1.00, 0.25, 90, 0.80),
    }
    b4 = portfolio_returns_from_config(
        {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
        dataset="lh_56y",
    )
    out = {"b4": b4}
    for name, gene in genes.items():
        out[name] = GA._returns_for_gene(ctx, gene).dropna()
    return out


def _configs() -> list[StrategyConfig]:
    return [
        StrategyConfig("b4_100", "100% B4 core", {"b4": 1.00}),
        StrategyConfig("b4_75_evo02_25", "75% B4 + 25% evo02", {"b4": 0.75, "evo02": 0.25}),
        StrategyConfig("b4_80_evo02_20", "80% B4 + 20% evo02", {"b4": 0.80, "evo02": 0.20}),
        StrategyConfig("b4_70_evo02_30", "70% B4 + 30% evo02", {"b4": 0.70, "evo02": 0.30}),
        StrategyConfig("b4_75_evo01_25", "75% B4 + 25% evo01", {"b4": 0.75, "evo01": 0.25}),
        StrategyConfig("b4_75_evo05_25", "75% B4 + 25% evo05", {"b4": 0.75, "evo05": 0.25}),
    ]


def _monthly_rebalanced_returns(components: dict[str, pd.Series], weights: dict[str, float]) -> pd.Series:
    aligned = pd.concat({k: components[k] for k in weights}, axis=1, sort=True).dropna()
    holdings = pd.Series({k: weights[k] for k in weights}, dtype=float)
    current_month = None
    values: list[float] = []
    dates: list[pd.Timestamp] = []
    portfolio_value = 1.0
    for date, row in aligned.iterrows():
        month = (date.year, date.month)
        if month != current_month:
            holdings = pd.Series({k: portfolio_value * weights[k] for k in weights}, dtype=float)
            current_month = month
        holdings = holdings * (1.0 + row[holdings.index])
        portfolio_value = float(holdings.sum())
        values.append(portfolio_value)
        dates.append(date)
    equity = pd.Series(values, index=pd.DatetimeIndex(dates), name="equity")
    return equity.pct_change().dropna()


def _simulate_contribution_account(components: dict[str, pd.Series], weights: dict[str, float]) -> pd.Series:
    aligned = pd.concat({k: components[k] for k in weights}, axis=1, sort=True).dropna()
    holdings = pd.Series({k: STARTING_CAPITAL * weights[k] for k in weights}, dtype=float)
    current_month = (aligned.index[0].year, aligned.index[0].month)
    values: list[float] = []
    for date, row in aligned.iterrows():
        month = (date.year, date.month)
        if month != current_month:
            total = float(holdings.sum()) + MONTHLY_CONTRIBUTION
            holdings = pd.Series({k: total * weights[k] for k in weights}, dtype=float)
            current_month = month
        holdings = holdings * (1.0 + row[holdings.index])
        values.append(float(holdings.sum()))
    return pd.Series(values, index=aligned.index, name="account_value")


def _bench_returns(ticker: str, strategy_returns: dict[str, pd.Series]) -> pd.Series:
    first = min(r.index[0] for r in strategy_returns.values())
    last = max(r.index[-1] for r in strategy_returns.values())
    return load_testfolio_series(ticker).pct_change().dropna().loc[first:last]


def _performance_table(
    returns: dict[str, pd.Series],
    contribution_curves: dict[str, pd.Series],
    strategy_slugs: list[str],
) -> pd.DataFrame:
    rows = []
    for slug in strategy_slugs:
        r = returns[slug].dropna()
        eq = (1.0 + r).cumprod()
        drawdown = eq / eq.cummax() - 1.0
        downside = r[r < 0.0].std(ddof=0)
        years = len(r) / TRADING_DAYS_PER_YEAR
        final_value = float(contribution_curves[slug].iloc[-1])
        total_contributed = STARTING_CAPITAL + MONTHLY_CONTRIBUTION * (_month_count(contribution_curves[slug]) - 1)
        rows.append({
            "strategy": slug,
            "start": str(r.index[0].date()),
            "end": str(r.index[-1].date()),
            "years": years,
            "cagr": float(eq.iloc[-1] ** (1.0 / years) - 1.0),
            "mdd": float(drawdown.min()),
            "sharpe": float(r.mean() / r.std(ddof=0) * np.sqrt(TRADING_DAYS_PER_YEAR)),
            "sortino": float(r.mean() / downside * np.sqrt(TRADING_DAYS_PER_YEAR)) if downside > 0 else np.nan,
            "calmar": float((eq.iloc[-1] ** (1.0 / years) - 1.0) / abs(drawdown.min())),
            "end_multiple": float(eq.iloc[-1]),
            "final_value": final_value,
            "total_contributed": float(total_contributed),
            "profit": final_value - float(total_contributed),
            "xirr": _xirr(contribution_curves[slug]),
        })
    return pd.DataFrame(rows).sort_values("sharpe", ascending=False)


def _month_count(curve: pd.Series) -> int:
    return len(pd.Series(1, index=curve.index).resample("MS").first().dropna())


def _xirr(curve: pd.Series) -> float:
    dates = [curve.index[0]]
    cashflows = [-STARTING_CAPITAL]
    month_starts = pd.Series(1, index=curve.index).resample("MS").first().dropna().index[1:]
    for date in month_starts:
        dates.append(date)
        cashflows.append(-MONTHLY_CONTRIBUTION)
    dates.append(curve.index[-1])
    cashflows.append(float(curve.iloc[-1]))
    t0 = dates[0]

    def npv(rate: float) -> float:
        return sum(cf / ((1.0 + rate) ** ((d - t0).days / 365.25)) for cf, d in zip(cashflows, dates, strict=True))

    lo, hi = -0.99, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return float((lo + hi) / 2.0)


def _rolling_table(
    returns: dict[str, pd.Series],
    strategies: list[str],
    benchmarks: list[str],
) -> pd.DataFrame:
    rows = []
    for strategy in strategies:
        for benchmark in benchmarks:
            if strategy == benchmark:
                continue
            common = returns[strategy].index.intersection(returns[benchmark].index)
            s = returns[strategy].loc[common]
            b = returns[benchmark].loc[common]
            for years in (3, 5, 10, 15, 20, 30):
                win = years * TRADING_DAYS_PER_YEAR
                if len(common) < win:
                    continue
                s_eq = (1.0 + s).rolling(win).apply(np.prod, raw=True).dropna()
                b_eq = (1.0 + b).rolling(win).apply(np.prod, raw=True).dropna()
                idx = s_eq.index.intersection(b_eq.index)
                s_cagr = s_eq.loc[idx] ** (1.0 / years) - 1.0
                b_cagr = b_eq.loc[idx] ** (1.0 / years) - 1.0
                rows.append({
                    "strategy": strategy,
                    "benchmark": benchmark,
                    "window_years": years,
                    "n_windows": int(len(idx)),
                    "pct_win_cagr": float((s_cagr > b_cagr).mean()),
                    "mean_cagr_edge": float((s_cagr - b_cagr).mean()),
                    "min_strategy_cagr": float(s_cagr.min()),
                    "min_benchmark_cagr": float(b_cagr.min()),
                })
    return pd.DataFrame(rows)


def _write_tables(
    perf: pd.DataFrame,
    rolling: pd.DataFrame,
    returns: dict[str, pd.Series],
    contribution_curves: dict[str, pd.Series],
) -> None:
    perf.to_csv(TABLES_DIR / "performance.csv", index=False)
    rolling.to_csv(TABLES_DIR / "rolling_windows.csv", index=False)
    pd.DataFrame({k: (1.0 + v).cumprod() for k, v in returns.items()}).to_csv(TABLES_DIR / "equity_curves.csv")
    pd.DataFrame(contribution_curves).to_csv(TABLES_DIR / "contribution_account_values.csv")


def _write_plots(returns: dict[str, pd.Series], contribution_curves: dict[str, pd.Series], strategies: list[str]) -> None:
    equity = pd.DataFrame({k: (1.0 + v).cumprod() for k, v in returns.items()})
    _plot_equity(equity, strategies + ["SPY", "QQQ", "VT"], PLOTS_DIR / "equity_curves.png", "Pure strategy equity, growth of $1")
    _plot_equity(pd.DataFrame(contribution_curves), strategies, PLOTS_DIR / "contribution_account_values.png", "$10k initial + $1k monthly contributions")
    _plot_drawdowns(equity[strategies + ["SPY", "QQQ", "VT"]], PLOTS_DIR / "drawdowns.png")
    _plot_relative(equity, strategies, "b4_100", PLOTS_DIR / "relative_to_b4.png")
    _plot_relative(equity, strategies, "SPY", PLOTS_DIR / "relative_to_spy.png")
    _plot_rolling_cagr(returns, strategies + ["b4_100", "SPY", "QQQ", "VT"], PLOTS_DIR / "rolling_cagr.png")
    _plot_rolling_sharpe(returns, strategies + ["b4_100", "SPY", "QQQ", "VT"], PLOTS_DIR / "rolling_sharpe.png")


def _plot_equity(equity: pd.DataFrame, cols: list[str], path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    for col in dict.fromkeys(cols):
        if col in equity:
            ax.plot(equity.index, equity[col], label=col, lw=1.5)
    ax.set_yscale("log")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_drawdowns(equity: pd.DataFrame, path: Path) -> None:
    dd = equity / equity.cummax() - 1.0
    fig, ax = plt.subplots(figsize=(14, 7))
    for col in dd.columns:
        ax.plot(dd.index, dd[col], label=col, lw=1.1)
    ax.set_title("Drawdowns")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_relative(equity: pd.DataFrame, strategies: list[str], benchmark: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 7))
    for slug in strategies:
        common = equity[slug].dropna().index.intersection(equity[benchmark].dropna().index)
        rel = equity.loc[common, slug] / equity.loc[common, benchmark]
        ax.plot(rel.index, rel, label=f"{slug}/{benchmark}", lw=1.4)
    ax.axhline(1.0, color="black", lw=0.8)
    ax.set_yscale("log")
    ax.set_title(f"Relative equity vs {benchmark}")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_rolling_cagr(returns: dict[str, pd.Series], cols: list[str], path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    for ax, years in zip(axes.flatten(), (3, 5, 10, 15), strict=True):
        win = years * TRADING_DAYS_PER_YEAR
        for col in dict.fromkeys(cols):
            r = returns[col]
            if len(r) < win:
                continue
            vals = (1.0 + r).rolling(win).apply(np.prod, raw=True).dropna()
            ax.plot(vals.index, vals ** (1.0 / years) - 1.0, label=col, lw=1.0)
        ax.axhline(0, color="black", lw=0.7)
        ax.set_title(f"{years}y rolling CAGR")
        ax.grid(True, alpha=0.25)
    axes.flatten()[0].legend(fontsize=7)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_rolling_sharpe(returns: dict[str, pd.Series], cols: list[str], path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    for ax, years in zip(axes.flatten(), (3, 5, 10, 15), strict=True):
        win = years * TRADING_DAYS_PER_YEAR
        for col in dict.fromkeys(cols):
            r = returns[col]
            if len(r) < win:
                continue
            sh = r.rolling(win).mean() / r.rolling(win).std(ddof=0) * np.sqrt(TRADING_DAYS_PER_YEAR)
            ax.plot(sh.index, sh, label=col, lw=1.0)
        ax.axhline(0, color="black", lw=0.7)
        ax.set_title(f"{years}y rolling Sharpe")
        ax.grid(True, alpha=0.25)
    axes.flatten()[0].legend(fontsize=7)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _write_report(perf: pd.DataFrame, rolling: pd.DataFrame, configs: list[StrategyConfig]) -> None:
    primary = perf.loc[perf["strategy"] == "b4_75_evo02_25"].iloc[0]
    b4 = perf.loc[perf["strategy"] == "b4_100"].iloc[0]
    lines = [
        "# Iter 058 — B4 Core + GA Satellite",
        "",
        "Status: research backtest of B4-like core plus repair-GA LETF satellites.",
        "",
        "## Premises",
        "",
        f"- Initial contribution: `${STARTING_CAPITAL:,.0f}`.",
        f"- Monthly contribution: `${MONTHLY_CONTRIBUTION:,.0f}` on the first trading day after each month starts.",
        "- Portfolio sleeve rebalance: monthly.",
        "- Primary candidate: `75% B4 core + 25% evo02`.",
        "- Research-only: GA candidates still require hard validation before deployment claims `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "## Configs",
        "",
        pd.DataFrame([{"slug": c.slug, "label": c.label, "weights": c.weights} for c in configs]).to_markdown(index=False),
        "",
        "## Performance",
        "",
        _format_perf_table(perf),
        "",
        "## Primary Read",
        "",
        f"`b4_75_evo02_25` CAGR `{primary.cagr:.2%}` vs B4 `{b4.cagr:.2%}`; MDD `{primary.mdd:.2%}` vs B4 `{b4.mdd:.2%}`; final contributed account `${primary.final_value:,.0f}` vs B4 `${b4.final_value:,.0f}`.",
        "",
        "## Rolling Windows",
        "",
        _format_primary_rolling(rolling),
        "",
        "## Plots",
        "",
        "- `plots/equity_curves.png`",
        "- `plots/contribution_account_values.png`",
        "- `plots/drawdowns.png`",
        "- `plots/relative_to_b4.png`",
        "- `plots/relative_to_spy.png`",
        "- `plots/rolling_cagr.png`",
        "- `plots/rolling_sharpe.png`",
        "",
    ]
    (ITER_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def _format_perf_table(perf: pd.DataFrame) -> str:
    view = perf.copy()
    for col in ("cagr", "mdd", "sharpe", "sortino", "calmar", "xirr"):
        view[col] = view[col].map(lambda x: f"{x:.4f}")
    for col in ("final_value", "total_contributed", "profit"):
        view[col] = view[col].map(lambda x: f"{x:,.0f}")
    return view[["strategy", "years", "cagr", "mdd", "sharpe", "sortino", "calmar", "final_value", "xirr"]].to_markdown(index=False)


def _format_primary_rolling(rolling: pd.DataFrame) -> str:
    view = rolling[(rolling["strategy"] == "b4_75_evo02_25") & (rolling["benchmark"].isin(["b4_100", "SPY", "QQQ", "VT"]))].copy()
    view["pct_win_cagr"] = view["pct_win_cagr"].map(lambda x: f"{x:.1%}")
    view["mean_cagr_edge"] = view["mean_cagr_edge"].map(lambda x: f"{x:.2%}")
    view["min_strategy_cagr"] = view["min_strategy_cagr"].map(lambda x: f"{x:.2%}")
    return view.to_markdown(index=False)


def _write_results_json(
    returns: dict[str, pd.Series],
    contribution_curves: dict[str, pd.Series],
    perf: pd.DataFrame,
    rolling: pd.DataFrame,
    configs: list[StrategyConfig],
) -> None:
    payload = {
        "premises": {
            "starting_capital": STARTING_CAPITAL,
            "monthly_contribution": MONTHLY_CONTRIBUTION,
            "rebalance": "monthly",
        },
        "configs": [{"slug": c.slug, "label": c.label, "weights": c.weights} for c in configs],
        "performance": perf.to_dict("records"),
        "rolling_windows": rolling.to_dict("records"),
        "returns_series": {
            slug: {"index": [str(x.date()) for x in r.index], "returns": [float(x) for x in r]}
            for slug, r in returns.items()
        },
        "contribution_curves": {
            slug: {"index": [str(x.date()) for x in c.index], "value": [float(x) for x in c]}
            for slug, c in contribution_curves.items()
        },
    }
    (ITER_DIR / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
