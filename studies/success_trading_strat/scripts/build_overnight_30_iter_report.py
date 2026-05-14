"""Build the consolidated report for success_trading_strat iterations 001-030.

The report is descriptive, not promotional: it compares the overnight loop's
best candidates, records gate failures, and plots equity/drawdown/rolling-window
diagnostics against SPY buy-and-hold. The validation interpretation keeps the
original strict gates intact while adding a pragmatic watchlist layer for future
paper-trading review `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "studies/success_trading_strat"
ITERS = STUDY / "iters/phase01"
OUT = STUDY / "reports/overnight_30_iter_review"
PLOTS = OUT / "plots"
PRICE_DIR = ROOT / "data/tiingo/daily/prices"


@dataclass(frozen=True)
class CurveSpec:
    iteration: str
    module: str
    label: str
    benchmark_label: str
    loader: str
    returns_builder: Callable[[Any, dict[str, Any]], pd.Series]
    benchmark_builder: Callable[[Any, dict[str, Any], pd.Index], pd.Series]


def _load_module(path: Path) -> Any:
    name = "_" + path.parent.name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _patch_moved_phase_paths(module: Any, iteration: str) -> None:
    """Fix runner constants after moving phase-1 dirs under `iters/phase01`.

    Phase-1 runners computed ROOT from a fixed directory depth. Moving them one
    level deeper makes that local constant point at `studies/`; patching keeps the
    historical scripts readable without editing each archived runner.
    """
    if hasattr(module, "ROOT"):
        module.ROOT = ROOT
    if hasattr(module, "OUT_DIR"):
        module.OUT_DIR = ITERS / iteration
    if hasattr(module, "PRICE_DIR"):
        module.PRICE_DIR = PRICE_DIR
    if hasattr(module, "VIX_PATH"):
        module.VIX_PATH = ROOT / "data/phase3_7/vix/VIXCLS.parquet"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float) and math.isfinite(float(value)):
            return float(value)
    return None


def _gate_pass(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict) and "pass" in value:
        return bool(value["pass"])
    return None


def _gate_value(value: Any, key: str = "value") -> float | None:
    if isinstance(value, dict):
        return _first_number(value.get(key), value.get("p_value"))
    return _first_number(value)


def summarize_results() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted(ITERS.glob("*/RESULTS.json")):
        data = _read_json(path)
        gates = data.get("gates") or {}
        metrics = data.get("metrics") or {}
        best_metrics = metrics.get("best") if isinstance(metrics.get("best"), dict) else {}
        best_config = data.get("best_config")
        if isinstance(best_config, dict):
            best_name = best_config.get("name") or best_config.get("config")
        else:
            best_name = best_config

        is_mcpt = gates.get("is_mcpt")
        wf_mcpt = gates.get("wf_mcpt")
        pbo_value = _first_number(gates.get("pbo_value"), _gate_value(gates.get("pbo")))
        dsr_p = _first_number(gates.get("dsr_p_value"), _gate_value(gates.get("dsr"), "p_value"))
        fwd = gates.get("fwd_stress") or gates.get("fwd_63d")
        bootstrap = gates.get("bootstrap") or gates.get("bootstrap_999_mean_daily_low")

        rows.append({
            "iteration": path.parent.name,
            "status": data.get("status") or data.get("verdict"),
            "winner": bool(data.get("winner", False)),
            "n_trials": data.get("n_trials", data.get("n_strategy_trials", 0)),
            "best_config": best_name,
            "cagr": _first_number(best_metrics.get("cagr"), metrics.get("cagr"), metrics.get("strategy_cagr")),
            "sharpe": _first_number(best_metrics.get("sharpe"), metrics.get("sharpe"), metrics.get("strategy_sharpe")),
            "mdd": _first_number(best_metrics.get("mdd"), metrics.get("mdd"), metrics.get("max_drawdown"), metrics.get("strategy_mdd")),
            "is_mcpt_p": _gate_value(is_mcpt, "p_value"),
            "is_mcpt_pass": _gate_pass(is_mcpt),
            "wf_mcpt_p": _gate_value(wf_mcpt, "p_value"),
            "wf_mcpt_pass": _gate_pass(wf_mcpt),
            "pbo": pbo_value,
            "pbo_pass": bool(gates.get("pbo")) if isinstance(gates.get("pbo"), bool) else _gate_pass(gates.get("pbo")),
            "dsr_p": dsr_p,
            "dsr_pass": bool(gates.get("dsr")) if isinstance(gates.get("dsr"), bool) else _gate_pass(gates.get("dsr")),
            "fwd_pass": _gate_pass(fwd),
            "bootstrap_pass": _gate_pass(bootstrap),
            "kill_switches": ",".join(data.get("kill_switches") or data.get("failed_gates") or []),
            "notes": data.get("notes", ""),
        })
    df = pd.DataFrame(rows)
    return df


def _strategy_from_kwargs(module: Any, data: Any, config: dict[str, Any]) -> pd.Series:
    kwargs = {k: v for k, v in config.items() if k not in {"name", "config"}}
    return module.strategy_returns(data, **kwargs)


def _strategy_from_config(module: Any, data: Any, config: dict[str, Any]) -> pd.Series:
    return module.strategy_returns(data, config=config)


def _strategy_from_components(module: Any, data: Any, config: dict[str, Any]) -> pd.Series:
    return module.strategy_returns(module.component_returns(data), config=config)


def _same_asset_benchmark(_module: Any, data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    asset = str(config["asset"])
    return data[asset].pct_change().fillna(0.0).loc[index]


def _runner_benchmark(module: Any, data: Any, config: dict[str, Any], index: pd.Index) -> pd.Series:
    try:
        out = module.benchmark_returns(data, config, index)
    except TypeError:
        out = module.benchmark_returns(data, str(config["asset"]), index)
    if isinstance(out, tuple):
        return out[0]
    return out


def _component_benchmark(module: Any, data: Any, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return module.benchmark_returns(module.component_returns(data), config, index)


def _spy_buy_hold(index: pd.Index) -> pd.Series:
    spy = _load_price("SPY")
    return spy.pct_change().fillna(0.0).reindex(index).fillna(0.0)


def _load_price(ticker: str) -> pd.Series:
    path = PRICE_DIR / f"{ticker}.parquet"
    df = pd.read_parquet(path)
    if "date" in df.columns:
        df = df.set_index("date")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    col = "adj_close" if "adj_close" in df.columns else "close"
    return df[col].astype(float).sort_index().rename(ticker)


def selected_curve_specs() -> list[CurveSpec]:
    return [
        CurveSpec("011-2026-05-14-vix-managed-exposure", "run_iter011.py", "011 qqq_vix15_w21", "QQQ B&H", "load_data", _strategy_from_kwargs, _same_asset_benchmark),
        CurveSpec("013-2026-05-14-crypto-donchian-trend", "run_iter013.py", "013 eth_don20", "ETH B&H", "load_prices", _strategy_from_kwargs, _runner_benchmark),
        CurveSpec("014-2026-05-14-crypto-vol-target-momentum", "run_iter014.py", "014 btc_mom63_vt20", "BTC B&H", "load_prices", _strategy_from_config, _runner_benchmark),
        CurveSpec("018-2026-05-14-ehlers-cycle-mode", "run_iter018.py", "018 qqq_ehlers_c30_t15", "QQQ B&H", "load_prices", _strategy_from_config, _runner_benchmark),
        CurveSpec("021-2026-05-14-intraday-overnight-decomposition", "run_iter021.py", "021 qqq_close_to_open", "QQQ B&H", "load_inputs", _strategy_from_components, _component_benchmark),
        CurveSpec("023-2026-05-14-obv-volume-confirmation", "run_iter023.py", "023 qqq_obv21", "QQQ B&H", "load_data", _strategy_from_config, _runner_benchmark),
        CurveSpec("028-2026-05-14-gayed-letf-qqq-rotation", "run_iter028.py", "028 qld_qqq_sma200_rv70", "QLD B&H", "load_data", _strategy_from_config, _runner_benchmark),
    ]


def load_selected_curves() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    strategy: dict[str, pd.Series] = {}
    local_bench: dict[str, pd.Series] = {}
    spy_bench: dict[str, pd.Series] = {}
    for spec in selected_curve_specs():
        module = _load_module(ITERS / spec.iteration / spec.module)
        _patch_moved_phase_paths(module, spec.iteration)
        results = _read_json(ITERS / spec.iteration / "RESULTS.json")
        config = results["best_config"]
        if not isinstance(config, dict):
            config = next(c for c in module.CONFIGS if c.get("name") == config)
        data = getattr(module, spec.loader)()
        returns = spec.returns_builder(module, data, config).dropna()
        returns.name = spec.label
        bench = spec.benchmark_builder(module, data, config, returns.index).dropna()
        bench = bench.reindex(returns.index).fillna(0.0)
        strategy[spec.label] = returns
        local_bench[f"{spec.label} vs {spec.benchmark_label}"] = bench
        spy_bench[spec.label] = _spy_buy_hold(returns.index)
    return pd.DataFrame(strategy), pd.DataFrame(local_bench), pd.DataFrame(spy_bench)


def metrics_from_returns(returns: pd.Series, periods: int = 252) -> dict[str, float]:
    r = returns.dropna().astype(float)
    if r.empty:
        return {"cagr": np.nan, "sharpe": np.nan, "mdd": np.nan, "terminal_multiple": np.nan}
    equity = (1.0 + r).cumprod()
    years = len(r) / periods
    terminal = float(equity.iloc[-1])
    cagr = terminal ** (1.0 / years) - 1.0 if years > 0 and terminal > 0 else np.nan
    std = float(r.std(ddof=1))
    sharpe = float(r.mean() / std * np.sqrt(periods)) if std > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    return {"cagr": cagr, "sharpe": sharpe, "mdd": mdd, "terminal_multiple": terminal}


def rolling_table(strategy_returns: pd.DataFrame, spy_returns: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label in strategy_returns.columns:
        pair = pd.concat([strategy_returns[label], spy_returns[label]], axis=1, join="inner").dropna()
        pair.columns = ["strategy", "spy"]
        for years in [1, 3, 5, 10, 15]:
            n = 252 * years
            if len(pair) < n:
                continue
            strat_roll = pair["strategy"].rolling(n).apply(lambda x: (1.0 + x).prod() ** (252.0 / len(x)) - 1.0, raw=False).dropna()
            spy_roll = pair["spy"].rolling(n).apply(lambda x: (1.0 + x).prod() ** (252.0 / len(x)) - 1.0, raw=False).dropna()
            aligned = pd.concat([strat_roll, spy_roll], axis=1, join="inner").dropna()
            aligned.columns = ["strategy", "spy"]
            rows.append({
                "label": label,
                "window_years": years,
                "strategy_median_cagr": float(aligned["strategy"].median()),
                "strategy_min_cagr": float(aligned["strategy"].min()),
                "spy_median_cagr": float(aligned["spy"].median()),
                "spy_min_cagr": float(aligned["spy"].min()),
                "share_beating_spy": float((aligned["strategy"] > aligned["spy"]).mean()),
            })
    return pd.DataFrame(rows)


def equity(returns: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return (1.0 + returns.fillna(0.0)).cumprod()


def drawdown_from_equity(eq: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return eq / eq.cummax() - 1.0


def plot_equity(strategy_returns: pd.DataFrame, spy_returns: pd.DataFrame) -> None:
    eq = equity(strategy_returns)
    spy_eq = equity(spy_returns)
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in eq.columns:
        ax.plot(eq.index, eq[col], label=col)
    ax.plot(spy_eq.index, spy_eq.mean(axis=1), label="SPY B&H aligned avg", color="black", linewidth=2.5, linestyle="--")
    ax.set_yscale("log")
    ax.set_title("Best Overnight Candidates - Equity Curves vs SPY B&H")
    ax.set_ylabel("Growth of $1, log scale")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS / "equity_vs_spy.png", dpi=160)
    plt.close(fig)


def plot_drawdowns(strategy_returns: pd.DataFrame) -> None:
    dd = drawdown_from_equity(equity(strategy_returns))
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in dd.columns:
        ax.plot(dd.index, dd[col], label=col)
    ax.set_title("Best Overnight Candidates - Drawdowns")
    ax.set_ylabel("Drawdown")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS / "drawdowns.png", dpi=160)
    plt.close(fig)


def plot_equity_ratio(strategy_returns: pd.DataFrame, spy_returns: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in strategy_returns.columns:
        pair = pd.concat([strategy_returns[col], spy_returns[col]], axis=1, join="inner").fillna(0.0)
        ratio = equity(pair.iloc[:, 0]) / equity(pair.iloc[:, 1])
        ax.plot(ratio.index, ratio, label=col)
    ax.axhline(1.0, color="black", linewidth=1, linestyle="--")
    ax.set_title("Strategy Equity / SPY B&H Equity")
    ax.set_ylabel("Relative wealth")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS / "equity_over_spy.png", dpi=160)
    plt.close(fig)


def plot_rolling(strategy_returns: pd.DataFrame, spy_returns: pd.DataFrame) -> None:
    for years in [1, 3, 5, 10, 15]:
        n = 252 * years
        fig, ax = plt.subplots(figsize=(13, 7))
        plotted = False
        for col in strategy_returns.columns:
            pair = pd.concat([strategy_returns[col], spy_returns[col]], axis=1, join="inner").dropna()
            if len(pair) < n:
                continue
            strat = pair.iloc[:, 0].rolling(n).apply(lambda x: (1.0 + x).prod() ** (252.0 / len(x)) - 1.0, raw=False)
            spy = pair.iloc[:, 1].rolling(n).apply(lambda x: (1.0 + x).prod() ** (252.0 / len(x)) - 1.0, raw=False)
            ax.plot(strat.index, strat, label=f"{col}")
            if not plotted:
                ax.plot(spy.index, spy, label="SPY B&H", color="black", linewidth=2.0, linestyle="--")
            plotted = True
        ax.axhline(0.0, color="grey", linewidth=1)
        ax.set_title(f"Rolling {years}Y CAGR")
        ax.set_ylabel("CAGR")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(PLOTS / f"rolling_{years}y_cagr.png", dpi=160)
        plt.close(fig)


def plot_gate_fail_counts(summary: pd.DataFrame) -> None:
    gate_cols = ["is_mcpt_pass", "wf_mcpt_pass", "pbo_pass", "dsr_pass", "fwd_pass", "bootstrap_pass"]
    counts = {col.replace("_pass", ""): int((summary[col] == False).sum()) for col in gate_cols}  # noqa: E712
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(counts.keys(), counts.values(), color="#994455")
    ax.set_title("Gate Fail Counts Across Parsed Results")
    ax.set_ylabel("Failures")
    fig.tight_layout()
    fig.savefig(PLOTS / "gate_fail_counts.png", dpi=160)
    plt.close(fig)


def pragmatic_classification(row: pd.Series) -> str:
    if bool(row.get("winner")):
        return "strict_winner"
    good_shape = (
        (row.get("sharpe") is not None and pd.notna(row.get("sharpe")) and row.get("sharpe") >= 0.9)
        and (row.get("mdd") is not None and pd.notna(row.get("mdd")) and row.get("mdd") > -0.40)
    )
    hardish_passes = sum(bool(row.get(c)) for c in ["pbo_pass", "dsr_pass", "fwd_pass", "bootstrap_pass"])
    if good_shape and hardish_passes >= 3:
        return "candidate_watchlist"
    if row.get("status") == "data_blocked":
        return "data_blocked"
    if row.get("status") == "infrastructure_only":
        return "infrastructure_only"
    return "reject"


def write_report(summary: pd.DataFrame, curve_metrics: pd.DataFrame, rolling: pd.DataFrame) -> None:
    watchlist = summary[summary["classification"] == "candidate_watchlist"].copy()
    lines = [
        "# Overnight 30-Iteration Review",
        "",
        "## Verdict",
        "",
        "The 30-iteration loop closed with `closed_no_winner`: 100 strategy configs were tested and zero strict winners were found. This report is descriptive and does not authorize live deployment. Strict gates remain informative, but the report also adds a pragmatic `candidate_watchlist` layer so good but imperfect strategies are not discarded automatically `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "## Files",
        "",
        "- `summary_table.csv`: one row per iteration result.",
        "- `curve_metrics.csv`: recomputed metrics for plotted candidates and aligned SPY benchmark.",
        "- `rolling_windows.csv`: rolling 1/3/5/10/15y CAGR diagnostics versus SPY.",
        "- `plots/equity_vs_spy.png`: selected candidate equity curves versus aligned SPY.",
        "- `plots/equity_over_spy.png`: relative wealth versus SPY.",
        "- `plots/drawdowns.png`: drawdown curves.",
        "- `plots/rolling_*y_cagr.png`: rolling CAGR windows.",
        "- `plots/gate_fail_counts.png`: parsed gate failure counts.",
        "",
        "## Classification Rules",
        "",
        "- `strict_winner`: original `winner=true`; none found.",
        "- `candidate_watchlist`: Sharpe >= 0.9, MDD better than -40%, and at least three of PBO/DSR/FWD/bootstrap parsed as passing.",
        "- `infrastructure_only`: data/scaffold/audit iterations.",
        "- `data_blocked`: pre-registered inputs unavailable.",
        "- `reject`: everything else.",
        "",
        "## Watchlist",
        "",
    ]
    if watchlist.empty:
        lines.append("No pragmatic watchlist candidates were identified under the report rule.")
    else:
        for _, row in watchlist.sort_values(["sharpe", "cagr"], ascending=False).iterrows():
            lines.append(f"- `{row['iteration']}` / `{row['best_config']}`: CAGR `{row['cagr']:.2%}` Sharpe `{row['sharpe']:.3f}` MDD `{row['mdd']:.2%}`; failed `{row['kill_switches']}`.")
    lines.extend([
        "",
        "## Top Recomputed Curves",
        "",
        curve_metrics.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Window Summary",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f") if not rolling.empty else "No rolling windows available.",
        "",
        "## Interpretation",
        "",
        "The strongest strict-gate near miss remains `011 qqq_vix15_w21`: it passed IS MCPT, WF MCPT, PBO, DSR, WF, OOS, bootstrap and cross-lib, but failed the latest 63-day forward stress. `013 eth_don20` and `023 qqq_obv21` are economically interesting, but each failed at least one non-negotiable validation gate. Future work should separate strict research proof from pragmatic paper-trading triage, then evaluate candidates forward without retrofitting thresholds.",
    ])
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    summary = summarize_results()
    summary["classification"] = summary.apply(pragmatic_classification, axis=1)
    summary.to_csv(OUT / "summary_table.csv", index=False)

    strategy_returns, _local_bench, spy_returns = load_selected_curves()
    strategy_returns.to_csv(OUT / "selected_candidate_returns.csv")
    spy_returns.to_csv(OUT / "selected_spy_returns.csv")

    metric_rows: list[dict[str, Any]] = []
    for col in strategy_returns.columns:
        m = metrics_from_returns(strategy_returns[col])
        sm = metrics_from_returns(spy_returns[col].reindex(strategy_returns[col].index).fillna(0.0))
        metric_rows.append({"label": col, **{f"strategy_{k}": v for k, v in m.items()}, **{f"spy_{k}": v for k, v in sm.items()}})
    curve_metrics = pd.DataFrame(metric_rows)
    curve_metrics.to_csv(OUT / "curve_metrics.csv", index=False)

    rolling = rolling_table(strategy_returns, spy_returns)
    rolling.to_csv(OUT / "rolling_windows.csv", index=False)

    plot_equity(strategy_returns, spy_returns)
    plot_equity_ratio(strategy_returns, spy_returns)
    plot_drawdowns(strategy_returns)
    plot_rolling(strategy_returns, spy_returns)
    plot_gate_fail_counts(summary)
    write_report(summary, curve_metrics, rolling)


if __name__ == "__main__":
    main()
