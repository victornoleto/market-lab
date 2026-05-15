"""Generate Top 10 Phase 1/2/3 strategies by relative wealth versus SPY.

Ranking is economic-only: terminal `strategy_equity / SPY_equity` on aligned
available dates. It is not a validation override; PBO/DSR/MCPT remain hard gates
for promotion `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`,
`[testing_tuning, p.318-320]`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / "studies" / "success_trading_strat"
OUT_DIR = STUDY / "reports" / "top10_phase123_spy_relative"
PLOTS_DIR = OUT_DIR / "plots"
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252


@dataclass(frozen=True)
class Candidate:
    phase: str
    iteration: str
    status: str
    best_config: str
    n_trials: int
    start: str
    end: str
    cagr: float | None
    sharpe: float | None
    max_drawdown: float | None
    terminal_wealth: float | None
    spy_terminal_wealth: float | None
    equity_over_spy_terminal: float | None
    equity_over_spy_cagr: float | None
    spy_cagr: float | None
    spy_max_drawdown: float | None
    pbo: float | None
    dsr_p: float | None
    failed_gates: str
    returns_source: str


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    old_returns = load_old_phase1_returns()
    candidates, returns_by_key = collect_candidates(old_returns)
    table = pd.DataFrame([c.__dict__ for c in candidates])
    table = table.sort_values("equity_over_spy_terminal", ascending=False, na_position="last")
    top10 = table.dropna(subset=["equity_over_spy_terminal"]).head(10).copy()
    table.to_csv(OUT_DIR / "all_phase123_spy_relative_candidates.csv", index=False)
    top10.to_csv(OUT_DIR / "top10_spy_relative.csv", index=False)

    selected_returns = {key: returns_by_key[key] for key in top10["iteration"] + "::" + top10["best_config"] if key in returns_by_key}
    if selected_returns:
        pd.concat(selected_returns, axis=1, sort=False).to_csv(OUT_DIR / "top10_returns.csv")

    rolling = compute_rolling(top10, selected_returns)
    rolling.to_csv(OUT_DIR / "top10_rolling_relative.csv", index=False)

    plot_top10_bar(top10)
    plot_equity(selected_returns)
    plot_relative(selected_returns)
    plot_drawdowns(selected_returns)
    plot_rolling(rolling)
    write_report(table, top10, rolling, selected_returns)


def collect_candidates(old_returns: dict[str, pd.Series]) -> tuple[list[Candidate], dict[str, pd.Series]]:
    candidates: list[Candidate] = []
    returns_by_key: dict[str, pd.Series] = {}
    for phase_dir in [STUDY / "iters" / "phase01", STUDY / "iters" / "phase02", STUDY / "iters" / "phase03"]:
        phase = phase_dir.name
        for result_path in sorted(phase_dir.glob("*/RESULTS.json")):
            data = json.loads(result_path.read_text(encoding="utf-8"))
            iteration = data.get("iteration") or result_path.parent.name
            best_config = best_config_name(data.get("best_config"))
            if not best_config:
                continue
            returns = load_returns_for_candidate(result_path, best_config, iteration, old_returns)
            metrics = best_metrics(data)
            pbo, dsr_p, failed_gates = parse_gates(data.get("gates") or {})
            if returns is not None and not returns.empty:
                spy = load_spy_returns(returns.index)
                key = f"{iteration}::{best_config}"
                returns_by_key[key] = returns
                candidates.append(candidate_from_returns(phase, iteration, data, best_config, returns, spy, pbo, dsr_p, failed_gates, result_path))
            else:
                candidate = candidate_from_metrics(phase, iteration, data, best_config, metrics, pbo, dsr_p, failed_gates, result_path)
                if candidate.equity_over_spy_terminal is not None:
                    candidates.append(candidate)
    return candidates, returns_by_key


def best_config_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "")
    if isinstance(value, str):
        return value
    return ""


def best_metrics(data: dict[str, Any]) -> dict[str, Any]:
    metrics = data.get("metrics") or {}
    if isinstance(metrics.get("best"), dict):
        return metrics["best"]
    return metrics


def load_old_phase1_returns() -> dict[str, pd.Series]:
    path = STUDY / "reports" / "overnight_30_iter_review" / "selected_candidate_returns.csv"
    if not path.exists():
        return {}
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    out: dict[str, pd.Series] = {}
    for col in frame.columns:
        series = frame[col].dropna().astype(float)
        if not series.empty:
            out[col] = series
    return out


def load_returns_for_candidate(result_path: Path, best_config: str, iteration: str, old_returns: dict[str, pd.Series]) -> pd.Series | None:
    returns_csv = result_path.parent / "returns.csv"
    if returns_csv.exists():
        frame = pd.read_csv(returns_csv, index_col=0, parse_dates=True)
        if best_config in frame.columns:
            return frame[best_config].dropna().astype(float)
    for label, series in old_returns.items():
        if label.startswith(iteration[:3] + " ") and best_config in label:
            return series
    returns_matrix = result_path.parent / "returns_matrix.csv"
    if returns_matrix.exists():
        frame = pd.read_csv(returns_matrix, index_col=0, parse_dates=True)
        if best_config in frame.columns:
            return frame[best_config].dropna().astype(float)
    return None


def candidate_from_returns(
    phase: str,
    iteration: str,
    data: dict[str, Any],
    best_config: str,
    returns: pd.Series,
    spy: pd.Series,
    pbo: float | None,
    dsr_p: float | None,
    failed_gates: str,
    result_path: Path,
) -> Candidate:
    strategy_terminal = terminal(returns)
    spy_terminal = terminal(spy)
    ratio = strategy_terminal / spy_terminal if spy_terminal else None
    strategy_cagr = cagr(returns)
    spy_cagr_value = cagr(spy)
    return Candidate(
        phase=phase,
        iteration=iteration,
        status=str(data.get("status") or ""),
        best_config=best_config,
        n_trials=int(data.get("n_trials") or 0),
        start=str(returns.index.min().date()),
        end=str(returns.index.max().date()),
        cagr=strategy_cagr,
        sharpe=sharpe(returns),
        max_drawdown=max_drawdown(returns),
        terminal_wealth=strategy_terminal,
        spy_terminal_wealth=spy_terminal,
        equity_over_spy_terminal=ratio,
        equity_over_spy_cagr=strategy_cagr - spy_cagr_value,
        spy_cagr=spy_cagr_value,
        spy_max_drawdown=max_drawdown(spy),
        pbo=pbo,
        dsr_p=dsr_p,
        failed_gates=failed_gates,
        returns_source=str(result_path.parent / "returns.csv") if (result_path.parent / "returns.csv").exists() else "overnight_30_iter_review selected returns",
    )


def candidate_from_metrics(
    phase: str,
    iteration: str,
    data: dict[str, Any],
    best_config: str,
    metrics: dict[str, Any],
    pbo: float | None,
    dsr_p: float | None,
    failed_gates: str,
    result_path: Path,
) -> Candidate:
    terminal_wealth = first_float(metrics, ["terminal_wealth", "terminal_multiple"])
    spy_terminal = first_float(metrics, ["spy_bh_terminal_wealth", "spy_bh_terminal_multiple"])
    start = str(metrics.get("start") or "")
    end = str(metrics.get("end") or "")
    if spy_terminal is None:
        spy_terminal = spy_terminal_from_dates(start, end)
    ratio = terminal_wealth / spy_terminal if terminal_wealth is not None and spy_terminal else None
    cagr_value = first_float(metrics, ["cagr"])
    spy_cagr_value = first_float(metrics, ["spy_bh_cagr"])
    return Candidate(
        phase=phase,
        iteration=iteration,
        status=str(data.get("status") or ""),
        best_config=best_config,
        n_trials=int(data.get("n_trials") or 0),
        start=start,
        end=end,
        cagr=cagr_value,
        sharpe=first_float(metrics, ["sharpe"]),
        max_drawdown=first_float(metrics, ["max_drawdown", "mdd"]),
        terminal_wealth=terminal_wealth,
        spy_terminal_wealth=spy_terminal,
        equity_over_spy_terminal=ratio,
        equity_over_spy_cagr=(cagr_value - spy_cagr_value) if cagr_value is not None and spy_cagr_value is not None else None,
        spy_cagr=spy_cagr_value,
        spy_max_drawdown=first_float(metrics, ["spy_bh_max_drawdown"]),
        pbo=pbo,
        dsr_p=dsr_p,
        failed_gates=failed_gates,
        returns_source="metrics_only",
    )


def parse_gates(gates: dict[str, Any]) -> tuple[float | None, float | None, str]:
    failed: list[str] = []
    pbo = None
    dsr_p = None
    for key, value in gates.items():
        if isinstance(value, bool):
            if not value:
                failed.append(key)
        elif isinstance(value, dict):
            if value.get("pass") is False:
                failed.append(key)
            if key == "pbo":
                pbo = first_float(value, ["value"])
            if key == "dsr":
                dsr_p = first_float(value, ["p_value"])
    pbo = pbo if pbo is not None else first_float(gates, ["pbo_value"])
    dsr_p = dsr_p if dsr_p is not None else first_float(gates, ["dsr_p_value"])
    return pbo, dsr_p, ";".join(failed)


def compute_rolling(top10: pd.DataFrame, returns_by_key: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for _, row in top10.iterrows():
        key = f"{row['iteration']}::{row['best_config']}"
        series = returns_by_key.get(key)
        if series is None:
            continue
        spy = load_spy_returns(series.index)
        rel = (1.0 + series).cumprod() / (1.0 + spy).cumprod()
        for years in [1, 3, 5, 10, 15]:
            window = years * TRADING_DAYS
            if len(rel) < window:
                continue
            end_ratio = rel / rel.shift(window)
            end_ratio = end_ratio.dropna()
            rows.append(
                {
                    "label": f"{row['phase']} {row['iteration'][:3]} {row['best_config']}",
                    "window_years": years,
                    "median_relative_end_ratio": float(end_ratio.median()),
                    "min_relative_end_ratio": float(end_ratio.min()),
                    "share_windows_beating_spy": float((end_ratio > 1.0).mean()),
                }
            )
    return pd.DataFrame(rows)


def plot_top10_bar(top10: pd.DataFrame) -> None:
    data = top10.sort_values("equity_over_spy_terminal", ascending=True)
    labels = data["phase"] + " " + data["iteration"].str[:3] + " " + data["best_config"]
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(labels, data["equity_over_spy_terminal"], color="#4C78A8")
    ax.axvline(1.0, color="black", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_title("Top 10 Terminal Relative Wealth vs SPY")
    ax.set_xlabel("strategy terminal equity / SPY terminal equity, log scale")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "top10_equity_over_spy_bar.png", dpi=160)
    plt.close(fig)


def plot_equity(returns_by_key: dict[str, pd.Series]) -> None:
    if not returns_by_key:
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    for key, series in returns_by_key.items():
        label = short_label(key)
        ax.plot(series.index, (1.0 + series).cumprod(), label=label, linewidth=1.4)
    ax.set_yscale("log")
    ax.set_title("Top 10 Available Equity Curves")
    ax.set_ylabel("growth of $1, log scale")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "top10_equity_log.png", dpi=160)
    plt.close(fig)


def plot_relative(returns_by_key: dict[str, pd.Series]) -> None:
    if not returns_by_key:
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    for key, series in returns_by_key.items():
        spy = load_spy_returns(series.index)
        rel = (1.0 + series).cumprod() / (1.0 + spy).cumprod()
        ax.plot(rel.index, rel, label=short_label(key), linewidth=1.5)
    ax.axhline(1.0, color="black", linewidth=0.8)
    ax.set_yscale("log")
    ax.set_title("Top 10 Equity / SPY Equity")
    ax.set_ylabel("relative wealth, log scale")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "top10_equity_over_spy.png", dpi=160)
    plt.close(fig)


def plot_drawdowns(returns_by_key: dict[str, pd.Series]) -> None:
    if not returns_by_key:
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    for key, series in returns_by_key.items():
        equity = (1.0 + series).cumprod()
        dd = equity / equity.cummax() - 1.0
        ax.plot(dd.index, dd * 100, label=short_label(key), linewidth=1.2)
    ax.set_title("Top 10 Drawdowns")
    ax.set_ylabel("drawdown (%)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "top10_drawdowns.png", dpi=160)
    plt.close(fig)


def plot_rolling(rolling: pd.DataFrame) -> None:
    if rolling.empty:
        return
    for years in sorted(rolling["window_years"].unique()):
        data = rolling[rolling["window_years"] == years].sort_values("share_windows_beating_spy", ascending=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(data["label"], data["share_windows_beating_spy"] * 100, color="#54A24B")
        ax.set_title(f"Top 10 Rolling {years}Y Windows Beating SPY")
        ax.set_xlabel("share of windows (%)")
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / f"rolling_{years}y_beating_spy.png", dpi=160)
        plt.close(fig)


def write_report(table: pd.DataFrame, top10: pd.DataFrame, rolling: pd.DataFrame, returns_by_key: dict[str, pd.Series]) -> None:
    lines = [
        "# Top 10 Strategies By Equity / SPY",
        "",
        "## Verdict",
        "",
        "This is an economic ranking across `success_trading_strat` Phases 1, 2 and 3. The score is terminal relative wealth, `strategy_equity / SPY_equity`, on aligned available dates. It is not a validation ranking and does not override failed MCPT/PBO/DSR gates `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "No strategy in this Top 10 is deploy-authorized. Mandate remains 100% Plano C.",
        "",
        "## Files",
        "",
        "- `all_phase123_spy_relative_candidates.csv`: all candidates with computable SPY-relative wealth.",
        "- `top10_spy_relative.csv`: selected Top 10.",
        "- `top10_returns.csv`: return series for Top 10 members with saved curves.",
        "- `top10_rolling_relative.csv`: rolling relative-window diagnostics.",
        "- `plots/top10_equity_over_spy_bar.png`: terminal relative wealth ranking.",
        "- `plots/top10_equity_log.png`: available Top 10 equity curves.",
        "- `plots/top10_equity_over_spy.png`: available Top 10 relative wealth curves.",
        "- `plots/top10_drawdowns.png`: available Top 10 drawdowns.",
        "",
        "## Ranking Method",
        "",
        "For candidates with saved `returns.csv`, SPY is recomputed over the exact strategy return dates. For Phase 1 candidates without per-iteration returns, the script uses the saved `overnight_30_iter_review` selected-return curves when available. Metrics-only rows without an aligned SPY terminal are excluded from the Top 10 because the requested criterion is explicitly `equity/equity_spy`.",
        "",
        "## Top 10",
        "",
        markdown_table(format_table(top10)),
        "",
        "## Plots",
        "",
        "![Top 10 terminal relative wealth](plots/top10_equity_over_spy_bar.png)",
        "",
        "![Top 10 equity curves](plots/top10_equity_log.png)",
        "",
        "![Top 10 equity over SPY](plots/top10_equity_over_spy.png)",
        "",
        "![Top 10 drawdowns](plots/top10_drawdowns.png)",
        "",
        "## Rolling Relative Diagnostics",
        "",
        markdown_table(format_rolling(rolling.head(80))),
        "",
        "## Interpretation",
        "",
        "The ranking is dominated by high-upside engines: crypto trend/momentum from Phase 1 and LETF/high-beta mechanisms from Phase 3. That is expected because relative terminal wealth rewards convex upside and high beta. It also means the ranking must be read with drawdown and gate failures visible: several high-ranked candidates failed FWD, WF MCPT, PBO or DSR, so they remain research diagnostics only `[leverage_for_the_long_run, p.13]`, `[testing_tuning, p.327-335]`.",
        "",
        "## Recommendation",
        "",
        "Use this Top 10 as a research shortlist for visual comparison only. Do not paper trade or deploy from this ranking; any future continuation must pre-register a new validation/stress question and keep cumulative trial accounting.",
        "",
    ]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def format_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["phase", "iteration", "status", "best_config", "start", "end", "equity_over_spy_terminal", "terminal_wealth", "spy_terminal_wealth", "cagr", "spy_cagr", "max_drawdown", "sharpe", "pbo", "dsr_p", "failed_gates"]
    out = df[cols].copy()
    for col in ["cagr", "spy_cagr", "max_drawdown"]:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.2%}")
    for col in ["equity_over_spy_terminal", "terminal_wealth", "spy_terminal_wealth", "sharpe", "pbo", "dsr_p"]:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    return out.fillna("")


def format_rolling(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in ["median_relative_end_ratio", "min_relative_end_ratio"]:
        out[col] = out[col].map(lambda x: f"{x:.3g}")
    out["share_windows_beating_spy"] = out["share_windows_beating_spy"].map(lambda x: f"{x:.1%}")
    return out


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "None."
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("|", "\\|") for col in headers) + " |")
    return "\n".join(lines)


def load_spy_returns(index: pd.Index) -> pd.Series:
    df = pd.read_parquet(PRICE_DIR / "SPY.parquet")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    close_col = "adj_close" if "adj_close" in df.columns else "close"
    return df[close_col].astype(float).sort_index().pct_change().fillna(0.0).reindex(index).fillna(0.0)


def spy_terminal_from_dates(start: str, end: str) -> float | None:
    if not start or not end:
        return None
    df = pd.read_parquet(PRICE_DIR / "SPY.parquet")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    close_col = "adj_close" if "adj_close" in df.columns else "close"
    close = df[close_col].astype(float).sort_index().loc[start:end]
    if close.empty:
        return None
    returns = close.pct_change().fillna(0.0)
    return terminal(returns)


def first_float(mapping: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = mapping.get(key)
        if value is None or value == "":
            continue
        try:
            if pd.isna(value):
                continue
        except TypeError:
            pass
        return float(value)
    return None


def terminal(returns: pd.Series) -> float:
    return float((1.0 + returns).prod())


def cagr(returns: pd.Series) -> float:
    total = terminal(returns) - 1.0
    years = len(returns) / TRADING_DAYS
    return float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and total > -1.0 else -1.0


def sharpe(returns: pd.Series) -> float:
    std = float(returns.std(ddof=1))
    return 0.0 if std == 0 else float(returns.mean() / std * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns).cumprod()
    return float((equity / equity.cummax() - 1.0).min())


def short_label(key: str) -> str:
    iteration, config = key.split("::", 1)
    return f"{iteration[:3]} {config}"


if __name__ == "__main__":
    main()
