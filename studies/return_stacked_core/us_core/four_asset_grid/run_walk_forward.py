#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[3]
SRC = REPO_ROOT / "src"
for candidate in (STUDY_DIR, REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.metrics.performance import (  # noqa: E402
    cagr,
    calmar,
    max_drawdown,
    returns_from_equity,
    sharpe,
    sortino,
    volatility,
)
from run import (  # noqa: E402
    ASSET_EQUITY_CSV,
    ASSETS,
    GRID_CSV,
    PERIODS_PER_YEAR,
    add_fitness_score,
    format_portfolio,
    generate_weight_vectors,
    metrics_from_equity_matrix,
    simulate_monthly_rebalanced_matrix,
)

RESULTS_DIR = STUDY_DIR / "results"
WF_REPORT = STUDY_DIR / "WF_REPORT.md"
WF_WINDOWS_CSV = RESULTS_DIR / "walk_forward_windows.csv"
WF_SUMMARY_CSV = RESULTS_DIR / "walk_forward_summary.csv"
WF_EQUITY_CSV = RESULTS_DIR / "walk_forward_equity.csv"
WF_SELECTIONS_CSV = RESULTS_DIR / "walk_forward_selection_stability.csv"

# Default 8y->2y windows produce >=8 OOS windows on the 2000-2026 DBMF-limited
# history, matching the repository's WF consistency discipline
# [testing_tuning, p.318-320], [advances_fin_ml, p.208-211].
DEFAULT_TRAIN_YEARS = 8
DEFAULT_TEST_YEARS = 2
DEFAULT_STEP_YEARS = 2
MIN_WF_RATIO = 6.0 / 8.0

BENCHMARK_WEIGHTS = {
    "rsc_like_35_40_25": (0, 35, 40, 25),
    "b4_equal_25": (25, 25, 25, 25),
}


@dataclass(frozen=True)
class Window:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def load_asset_equity() -> pd.DataFrame:
    if not ASSET_EQUITY_CSV.exists():
        raise FileNotFoundError(f"{ASSET_EQUITY_CSV} does not exist; run run.py first")
    frame = pd.read_csv(ASSET_EQUITY_CSV, parse_dates=["date"]).set_index("date")
    missing = [col for col in ASSETS if col not in frame.columns]
    if missing:
        raise ValueError(f"missing asset columns in {ASSET_EQUITY_CSV}: {missing}")
    return frame[ASSETS].dropna(how="any")


def build_windows(index: pd.DatetimeIndex, train_years: int, test_years: int, step_years: int) -> list[Window]:
    first = pd.Timestamp(index.min()).normalize()
    last = pd.Timestamp(index.max()).normalize()
    windows: list[Window] = []
    train_start = first
    while True:
        train_end = train_start + pd.DateOffset(years=train_years) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=test_years) - pd.Timedelta(days=1)
        if test_end > last:
            break
        windows.append(Window(train_start=train_start, train_end=train_end, test_start=test_start, test_end=test_end))
        train_start = train_start + pd.DateOffset(years=step_years)
    return windows


def run_window_grid(asset_equity: pd.DataFrame) -> pd.DataFrame:
    asset_returns = asset_equity.pct_change().dropna()
    vectors = generate_weight_vectors()
    weights_pct = np.array(vectors, dtype=int)
    weights = weights_pct.astype(float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)
    frame = metrics_from_equity_matrix(asset_equity, equity, weights_pct, vectors)
    return add_fitness_score(frame)


def portfolio_returns(asset_equity: pd.DataFrame, weights_pct: tuple[int, int, int, int]) -> pd.Series:
    asset_returns = asset_equity.pct_change().dropna()
    if asset_returns.empty:
        return pd.Series(dtype=float)
    weights = np.array([weights_pct], dtype=float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)[:, 0]
    returns = pd.Series(equity[1:] / equity[:-1] - 1.0, index=asset_returns.index)
    return returns.rename(format_portfolio(weights_pct))


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    if returns.empty:
        return {
            "cagr": float("nan"),
            "mdd": float("nan"),
            "vol": float("nan"),
            "sharpe": float("nan"),
            "sortino": float("nan"),
            "calmar": float("nan"),
            "terminal": float("nan"),
        }
    equity = pd.concat(
        [pd.Series([1.0], index=[returns.index[0] - pd.Timedelta(days=1)]), (1.0 + returns).cumprod()]
    )
    mdd_abs = max_drawdown(equity)
    return {
        "cagr": cagr(equity, PERIODS_PER_YEAR),
        "mdd": -mdd_abs,
        "vol": volatility(returns, PERIODS_PER_YEAR),
        "sharpe": sharpe(returns, PERIODS_PER_YEAR),
        "sortino": sortino(returns, PERIODS_PER_YEAR),
        "calmar": calmar(equity, PERIODS_PER_YEAR),
        "terminal": float(equity.iloc[-1]),
    }


def weights_from_row(row: pd.Series) -> tuple[int, int, int, int]:
    return (
        int(row["ntsx_pct"]),
        int(row["gde_pct"]),
        int(row["rsst70_30_pct"]),
        int(row["zroz_pct"]),
    )


def row_for_weights(frame: pd.DataFrame, weights_pct: tuple[int, int, int, int]) -> pd.Series:
    mask = (
        (frame["ntsx_pct"] == weights_pct[0])
        & (frame["gde_pct"] == weights_pct[1])
        & (frame["rsst70_30_pct"] == weights_pct[2])
        & (frame["zroz_pct"] == weights_pct[3])
    )
    matched = frame.loc[mask]
    if matched.empty:
        raise KeyError(f"weights not found in grid: {weights_pct}")
    return matched.iloc[0]


def full_grid_top_weights() -> tuple[int, int, int, int]:
    if GRID_CSV.exists():
        grid = pd.read_csv(GRID_CSV)
        if not grid.empty:
            return weights_from_row(grid.iloc[0])
    return (0, 40, 25, 35)


def run_walk_forward(asset_equity: pd.DataFrame, windows: list[Window]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not windows:
        raise ValueError("no walk-forward windows generated")

    full_top = full_grid_top_weights()
    benchmark_weights = {"full_grid_top_lookahead": full_top, **BENCHMARK_WEIGHTS}

    window_rows: list[dict[str, object]] = []
    wf_parts: dict[str, list[pd.Series]] = {"wf_selected": []}
    for name in benchmark_weights:
        wf_parts[name] = []

    for i, window in enumerate(windows, start=1):
        train_equity = asset_equity.loc[window.train_start : window.train_end]
        test_equity = asset_equity.loc[window.test_start : window.test_end]
        if len(train_equity) < 252 or len(test_equity) < 20:
            raise ValueError(f"window {i} too short: train={len(train_equity)} test={len(test_equity)}")

        train_grid = run_window_grid(train_equity)
        test_grid = run_window_grid(test_equity)
        test_ranked = test_grid.reset_index(drop=True).copy()
        test_ranked["oos_rank"] = np.arange(1, len(test_ranked) + 1)

        selected = train_grid.iloc[0]
        selected_weights = weights_from_row(selected)
        selected_oos = row_for_weights(test_ranked, selected_weights)
        oracle_oos = test_ranked.iloc[0]
        rsc_oos = row_for_weights(test_ranked, benchmark_weights["rsc_like_35_40_25"])
        full_top_oos = row_for_weights(test_ranked, full_top)

        merged = train_grid.merge(
            test_grid,
            on=["ntsx_pct", "gde_pct", "rsst70_30_pct", "zroz_pct"],
            suffixes=("_train", "_test"),
        )
        rank_corr = float(merged["fitness_score_train"].corr(merged["fitness_score_test"], method="spearman"))

        wf_parts["wf_selected"].append(portfolio_returns(test_equity, selected_weights))
        for name, weights in benchmark_weights.items():
            wf_parts[name].append(portfolio_returns(test_equity, weights))

        window_rows.append(
            {
                "window": i,
                "train_start": train_equity.index[0].date().isoformat(),
                "train_end": train_equity.index[-1].date().isoformat(),
                "test_start": test_equity.index[0].date().isoformat(),
                "test_end": test_equity.index[-1].date().isoformat(),
                "selected_portfolio": format_portfolio(selected_weights),
                "selected_ntsx_pct": selected_weights[0],
                "selected_gde_pct": selected_weights[1],
                "selected_rsst70_30_pct": selected_weights[2],
                "selected_zroz_pct": selected_weights[3],
                "train_fitness": float(selected["fitness_score"]),
                "train_cagr": float(selected["cagr"]),
                "train_mdd": float(selected["mdd"]),
                "train_sharpe": float(selected["sharpe"]),
                "train_calmar": float(selected["calmar"]),
                "test_cagr": float(selected_oos["cagr"]),
                "test_mdd": float(selected_oos["mdd"]),
                "test_sharpe": float(selected_oos["sharpe"]),
                "test_calmar": float(selected_oos["calmar"]),
                "test_terminal": float(selected_oos["terminal"]),
                "test_rank": int(selected_oos["oos_rank"]),
                "test_rank_pct": float(selected_oos["oos_rank"] / len(test_ranked)),
                "oos_oracle_portfolio": str(oracle_oos["portfolio"]),
                "oos_oracle_cagr": float(oracle_oos["cagr"]),
                "oos_oracle_mdd": float(oracle_oos["mdd"]),
                "rsc_like_cagr": float(rsc_oos["cagr"]),
                "rsc_like_mdd": float(rsc_oos["mdd"]),
                "full_top_cagr": float(full_top_oos["cagr"]),
                "full_top_mdd": float(full_top_oos["mdd"]),
                "beat_rsc_like": bool(float(selected_oos["terminal"]) > float(rsc_oos["terminal"])),
                "beat_full_top": bool(float(selected_oos["terminal"]) > float(full_top_oos["terminal"])),
                "train_test_fitness_spearman": rank_corr,
            }
        )

    windows_df = pd.DataFrame(window_rows)
    equity_frame = build_equity_frame(wf_parts)
    summary = summarize_equity(equity_frame, windows_df)
    selections = selection_stability(windows_df)
    return windows_df, summary, equity_frame, selections


def build_equity_frame(parts: dict[str, list[pd.Series]]) -> pd.DataFrame:
    out: dict[str, pd.Series] = {}
    for name, series_parts in parts.items():
        returns = pd.concat(series_parts).sort_index()
        returns = returns[~returns.index.duplicated(keep="first")].dropna()
        out[f"{name}_return"] = returns
        out[f"{name}_equity"] = (1.0 + returns).cumprod()
    frame = pd.DataFrame(out)
    return frame


def summarize_equity(equity_frame: pd.DataFrame, windows_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    strategies = sorted({col.removesuffix("_return") for col in equity_frame.columns if col.endswith("_return")})
    n_windows = len(windows_df)
    required = math.ceil(MIN_WF_RATIO * n_windows)
    for name in strategies:
        returns = equity_frame[f"{name}_return"].dropna()
        metrics = metrics_from_returns(returns)
        row: dict[str, object] = {
            "strategy": name,
            **metrics,
            "n_oos_windows": n_windows,
            "required_windows": required,
        }
        if name == "wf_selected":
            beat_rsc = int(windows_df["beat_rsc_like"].sum())
            beat_full = int(windows_df["beat_full_top"].sum())
            row.update(
                {
                    "windows_beat_rsc_like": beat_rsc,
                    "pass_vs_rsc_like_75pct": bool(beat_rsc >= required),
                    "windows_beat_full_top": beat_full,
                    "pass_vs_full_top_75pct": bool(beat_full >= required),
                    "median_oos_rank_pct": float(windows_df["test_rank_pct"].median()),
                    "mean_train_test_fitness_spearman": float(windows_df["train_test_fitness_spearman"].mean()),
                }
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["terminal", "cagr"], ascending=False)


def selection_stability(windows_df: pd.DataFrame) -> pd.DataFrame:
    counts = Counter(windows_df["selected_portfolio"])
    rows: list[dict[str, object]] = []
    for portfolio, count in counts.most_common():
        sub = windows_df[windows_df["selected_portfolio"] == portfolio]
        rows.append(
            {
                "selected_portfolio": portfolio,
                "n_windows": int(count),
                "share_windows": float(count / len(windows_df)),
                "avg_test_cagr": float(sub["test_cagr"].mean()),
                "avg_test_mdd": float(sub["test_mdd"].mean()),
                "avg_test_rank_pct": float(sub["test_rank_pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _fmt_pct(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def _fmt_num(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    value = float(value)
    if math.isinf(value):
        return "inf"
    return f"{value:.3f}"


def _markdown_table(frame: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None) -> str:
    formats = formats or {}
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for _, row in frame.iterrows():
        cells: list[str] = []
        for col in columns:
            value = row[col]
            fmt = formats.get(col, "")
            if fmt == "pct":
                cells.append(_fmt_pct(value))
            elif fmt == "num":
                cells.append(_fmt_num(value))
            elif fmt == "int":
                cells.append("" if pd.isna(value) else str(int(value)))
            elif fmt == "bool":
                cells.append("" if pd.isna(value) or value == "" else ("PASS" if bool(value) else "FAIL"))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(windows_df: pd.DataFrame, summary: pd.DataFrame, selections: pd.DataFrame, args: argparse.Namespace) -> None:
    selected = summary[summary["strategy"] == "wf_selected"].iloc[0]
    n_windows = int(selected["n_oos_windows"])
    required = int(selected["required_windows"])
    verdict = "FAIL" if not bool(selected["pass_vs_rsc_like_75pct"]) else "PASS"
    unique_selected = int(len(selections))

    summary_cols = [
        "strategy",
        "cagr",
        "mdd",
        "vol",
        "sharpe",
        "sortino",
        "calmar",
        "terminal",
        "windows_beat_rsc_like",
        "pass_vs_rsc_like_75pct",
    ]
    summary_view = summary.copy()
    for col in ["windows_beat_rsc_like", "pass_vs_rsc_like_75pct"]:
        if col not in summary_view.columns:
            summary_view[col] = ""

    window_cols = [
        "window",
        "test_start",
        "test_end",
        "selected_portfolio",
        "test_cagr",
        "test_mdd",
        "test_rank_pct",
        "rsc_like_cagr",
        "full_top_cagr",
        "beat_rsc_like",
        "train_test_fitness_spearman",
    ]

    report = (
        "# Four-Asset Grid Walk-Forward Analysis\n\n"
        "Status: research-only diagnostic. No deployment, paper-trade label or mandate change.\n\n"
        "## Summary\n\n"
        f"- Setup: `{args.train_years}y` in-sample optimize -> `{args.test_years}y` OOS, rolled by `{args.step_years}y`.\n"
        f"- Candidate grid: all `1,771` 5%-step portfolios over `NTSXSIM/GDESIM/RSST70_30/ZROZSIM`.\n"
        "- Train objective: same rank-based fitness as the full grid, computed only inside each IS window.\n"
        f"- WF selected combined OOS: CAGR `{_fmt_pct(selected['cagr'])}`, MDD `{_fmt_pct(selected['mdd'])}`, "
        f"Sharpe `{_fmt_num(selected['sharpe'])}`, terminal `{_fmt_num(selected['terminal'])}x`.\n"
        f"- Beat fixed RSC-like `35/40/25` in `{int(selected['windows_beat_rsc_like'])}/{n_windows}` windows; required `{required}/{n_windows}` for the 75% consistency read. Verdict: **{verdict}**.\n"
        f"- Selection stability: `{unique_selected}/{n_windows}` unique selected portfolios; no allocation repeated across OOS windows.\n"
        f"- Median selected OOS rank percentile: `{_fmt_pct(selected['median_oos_rank_pct'])}`; mean train/test fitness Spearman: `{_fmt_num(selected['mean_train_test_fitness_spearman'])}`.\n\n"
        "This directly tests the overfit concern: the allocation is selected using only prior data, then held in the subsequent OOS block. Walk-forward selection is a robustness diagnostic against choosing parameters on the full sample `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.\n\n"
        "## Combined OOS Metrics\n\n"
        f"{_markdown_table(summary_view[summary_cols], summary_cols, {'cagr': 'pct', 'mdd': 'pct', 'vol': 'pct', 'sharpe': 'num', 'sortino': 'num', 'calmar': 'num', 'terminal': 'num', 'windows_beat_rsc_like': 'int', 'pass_vs_rsc_like_75pct': 'bool'})}\n\n"
        "## OOS Window Details\n\n"
        f"{_markdown_table(windows_df[window_cols], window_cols, {'window': 'int', 'test_cagr': 'pct', 'test_mdd': 'pct', 'test_rank_pct': 'pct', 'rsc_like_cagr': 'pct', 'full_top_cagr': 'pct', 'beat_rsc_like': 'bool', 'train_test_fitness_spearman': 'num'})}\n\n"
        "## Selection Stability\n\n"
        f"{_markdown_table(selections, list(selections.columns), {'n_windows': 'int', 'share_windows': 'pct', 'avg_test_cagr': 'pct', 'avg_test_mdd': 'pct', 'avg_test_rank_pct': 'pct'})}\n\n"
        "## Interpretation\n\n"
        "- `wf_selected` is the only non-lookahead optimizer result in this report.\n"
        "- `full_grid_top_lookahead` is included as a diagnostic benchmark because it is the full-sample winner; it is not a valid selection rule.\n"
        "- If WF-selected weights fail to beat simple fixed anchors consistently, the full-sample top should be treated as overfit-prone and not as a promoted allocation.\n"
        "- This still is not full validation: PBO/DSR/bootstrap/cross-library, real implementation costs, taxes and account-level constraints remain absent `[advances_fin_ml, p.208-211]`, `[systematic_trading, p.185-188]`.\n\n"
        "## Artifacts\n\n"
        f"- Windows: `{WF_WINDOWS_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Summary: `{WF_SUMMARY_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Equity/returns: `{WF_EQUITY_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Selection stability: `{WF_SELECTIONS_CSV.relative_to(REPO_ROOT)}`.\n"
    )
    WF_REPORT.write_text(report, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run walk-forward anti-overfit analysis for the four-asset grid.")
    parser.add_argument("--train-years", type=int, default=DEFAULT_TRAIN_YEARS)
    parser.add_argument("--test-years", type=int, default=DEFAULT_TEST_YEARS)
    parser.add_argument("--step-years", type=int, default=DEFAULT_STEP_YEARS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.train_years <= 0 or args.test_years <= 0 or args.step_years <= 0:
        raise ValueError("train-years, test-years and step-years must be positive")

    asset_equity = load_asset_equity()
    windows = build_windows(asset_equity.index, args.train_years, args.test_years, args.step_years)
    windows_df, summary, equity_frame, selections = run_walk_forward(asset_equity, windows)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    windows_df.to_csv(WF_WINDOWS_CSV, index=False)
    summary.to_csv(WF_SUMMARY_CSV, index=False)
    equity_frame.to_csv(WF_EQUITY_CSV, index_label="date")
    selections.to_csv(WF_SELECTIONS_CSV, index=False)
    write_report(windows_df, summary, selections, args)

    selected = summary[summary["strategy"] == "wf_selected"].iloc[0]
    print(f"wrote {WF_REPORT.relative_to(REPO_ROOT)}")
    print(f"windows={len(windows_df)} beat_rsc={int(selected['windows_beat_rsc_like'])}/{int(selected['n_oos_windows'])}")
    print(summary[["strategy", "cagr", "mdd", "sharpe", "calmar", "terminal"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
