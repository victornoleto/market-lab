#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
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

from market_lab.backtest.validation.cpcv import cpcv_splits  # noqa: E402
from market_lab.backtest.validation.pbo import pbo, pbo_gate  # noqa: E402
from run import (  # noqa: E402
    ASSETS,
    GRID_CSV,
    PERIODS_PER_YEAR,
    add_fitness_score,
    format_portfolio,
    generate_weight_vectors,
    simulate_monthly_rebalanced_matrix,
)
from run_walk_forward import (  # noqa: E402
    Window,
    build_windows,
    load_asset_equity,
    metrics_from_returns,
    run_walk_forward,
)

RESULTS_DIR = STUDY_DIR / "results"
REPORT_MD = STUDY_DIR / "ROBUSTNESS_REPORT.md"
WF_SENSITIVITY_CSV = RESULTS_DIR / "robustness_wf_sensitivity.csv"
STABILITY_PORTFOLIOS_CSV = RESULTS_DIR / "robustness_top_decile_portfolios.csv"
STABILITY_WEIGHTS_CSV = RESULTS_DIR / "robustness_top_decile_weight_distribution.csv"
CPCV_CSV = RESULTS_DIR / "robustness_cpcv_splits.csv"
FIXED_RULES_CSV = RESULTS_DIR / "robustness_fixed_rules.csv"
PBO_SUMMARY_CSV = RESULTS_DIR / "robustness_pbo_summary.csv"

TOP_DECILE = 0.10
WF_PASS_RATIO = 6.0 / 8.0
PBO_BLOCKS = 10
CPCV_GROUPS = 8
CPCV_TEST_GROUPS = 2

FULL_TOP_WEIGHTS = (0, 40, 25, 35)
RSC_WEIGHTS = (0, 35, 40, 25)
FIXED_RULES = {
    "rsc_like_35_40_25": RSC_WEIGHTS,
    "b4_equal_25": (25, 25, 25, 25),
    "full_grid_top_40_25_35": FULL_TOP_WEIGHTS,
    "defensive_35_30_35": (0, 35, 30, 35),
    "mf_tilt_30_40_30": (0, 30, 40, 30),
    "gde_tilt_40_30_30": (0, 40, 30, 30),
}


@dataclass(frozen=True)
class MatrixBundle:
    returns: np.ndarray
    dates: pd.DatetimeIndex
    vectors: list[tuple[int, int, int, int]]
    weights_pct: np.ndarray


def main() -> int:
    asset_equity = load_asset_equity()
    bundle = build_returns_matrix(asset_equity)

    wf_sensitivity = run_wf_sensitivity(asset_equity)
    stability_portfolios, stability_weights = run_stability_map(asset_equity)
    cpcv_df, pbo_summary = run_cpcv_pbo(bundle)
    fixed_rules = run_fixed_rules(asset_equity)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    wf_sensitivity.to_csv(WF_SENSITIVITY_CSV, index=False)
    stability_portfolios.to_csv(STABILITY_PORTFOLIOS_CSV, index=False)
    stability_weights.to_csv(STABILITY_WEIGHTS_CSV, index=False)
    cpcv_df.to_csv(CPCV_CSV, index=False)
    fixed_rules.to_csv(FIXED_RULES_CSV, index=False)
    pbo_summary.to_csv(PBO_SUMMARY_CSV, index=False)
    write_report(wf_sensitivity, stability_portfolios, stability_weights, cpcv_df, pbo_summary, fixed_rules)

    print(f"wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    print(pbo_summary.to_string(index=False))
    print(wf_sensitivity[["scenario", "n_windows", "wf_cagr", "wf_mdd", "wf_sharpe", "windows_beat_rsc_like", "pass_vs_rsc_like_75pct"]].to_string(index=False))
    return 0


def build_returns_matrix(asset_equity: pd.DataFrame) -> MatrixBundle:
    asset_returns = asset_equity.pct_change().dropna()
    vectors = generate_weight_vectors()
    weights_pct = np.array(vectors, dtype=int)
    weights = weights_pct.astype(float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)
    returns = equity[1:] / equity[:-1] - 1.0
    return MatrixBundle(returns=returns, dates=asset_returns.index, vectors=vectors, weights_pct=weights_pct)


def build_expanding_windows(index: pd.DatetimeIndex, min_train_years: int = 8, test_years: int = 2, step_years: int = 2) -> list[Window]:
    first = pd.Timestamp(index.min()).normalize()
    last = pd.Timestamp(index.max()).normalize()
    windows: list[Window] = []
    train_start = first
    test_start = first + pd.DateOffset(years=min_train_years)
    while True:
        test_end = test_start + pd.DateOffset(years=test_years) - pd.Timedelta(days=1)
        if test_end > last:
            break
        train_end = test_start - pd.Timedelta(days=1)
        windows.append(Window(train_start=train_start, train_end=train_end, test_start=test_start, test_end=test_end))
        test_start = test_start + pd.DateOffset(years=step_years)
    return windows


def run_wf_sensitivity(asset_equity: pd.DataFrame) -> pd.DataFrame:
    scenarios: list[tuple[str, list[Window]]] = [
        ("rolling_5y_1y", build_windows(asset_equity.index, train_years=5, test_years=1, step_years=1)),
        ("rolling_8y_2y", build_windows(asset_equity.index, train_years=8, test_years=2, step_years=2)),
        ("rolling_10y_2y", build_windows(asset_equity.index, train_years=10, test_years=2, step_years=2)),
        ("rolling_12y_3y", build_windows(asset_equity.index, train_years=12, test_years=3, step_years=3)),
        ("expanding_8y_2y", build_expanding_windows(asset_equity.index, min_train_years=8, test_years=2, step_years=2)),
    ]
    rows: list[dict[str, object]] = []
    for scenario, windows in scenarios:
        windows_df, summary, _equity, selections = run_walk_forward(asset_equity, windows)
        wf = summary[summary["strategy"] == "wf_selected"].iloc[0]
        rsc = summary[summary["strategy"] == "rsc_like_35_40_25"].iloc[0]
        required = int(math.ceil(WF_PASS_RATIO * len(windows_df)))
        rows.append(
            {
                "scenario": scenario,
                "n_windows": int(len(windows_df)),
                "required_windows": required,
                "wf_cagr": float(wf["cagr"]),
                "wf_mdd": float(wf["mdd"]),
                "wf_sharpe": float(wf["sharpe"]),
                "wf_calmar": float(wf["calmar"]),
                "wf_terminal": float(wf["terminal"]),
                "rsc_cagr": float(rsc["cagr"]),
                "rsc_mdd": float(rsc["mdd"]),
                "rsc_sharpe": float(rsc["sharpe"]),
                "rsc_calmar": float(rsc["calmar"]),
                "rsc_terminal": float(rsc["terminal"]),
                "windows_beat_rsc_like": int(windows_df["beat_rsc_like"].sum()),
                "pass_vs_rsc_like_75pct": bool(int(windows_df["beat_rsc_like"].sum()) >= required),
                "unique_selected_portfolios": int(len(selections)),
                "median_oos_rank_pct": float(windows_df["test_rank_pct"].median()),
                "mean_train_test_fitness_spearman": float(windows_df["train_test_fitness_spearman"].mean()),
            }
        )
    return pd.DataFrame(rows)


def run_stability_map(asset_equity: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    windows = build_windows(asset_equity.index, train_years=8, test_years=2, step_years=2)
    rows: list[dict[str, object]] = []
    for i, window in enumerate(windows, start=1):
        train_equity = asset_equity.loc[window.train_start : window.train_end]
        grid = run_segment_grid(train_equity).reset_index(drop=True)
        top_n = int(math.ceil(len(grid) * TOP_DECILE))
        for rank, row in enumerate(grid.head(top_n).itertuples(index=False), start=1):
            weights = (int(row.ntsx_pct), int(row.gde_pct), int(row.rsst70_30_pct), int(row.zroz_pct))
            rows.append(
                {
                    "window": i,
                    "rank": rank,
                    "portfolio": format_portfolio(weights),
                    "ntsx_pct": weights[0],
                    "gde_pct": weights[1],
                    "rsst70_30_pct": weights[2],
                    "zroz_pct": weights[3],
                    "fitness_score": float(row.fitness_score),
                    "cagr": float(row.cagr),
                    "mdd": float(row.mdd),
                    "sharpe": float(row.sharpe),
                    "calmar": float(row.calmar),
                }
            )
    top_decile = pd.DataFrame(rows)

    grouped = top_decile.groupby("portfolio", as_index=False).agg(
        n_top_decile_windows=("window", "nunique"),
        n_top_decile_rows=("window", "size"),
        avg_rank=("rank", "mean"),
        median_rank=("rank", "median"),
        avg_fitness=("fitness_score", "mean"),
        ntsx_pct=("ntsx_pct", "first"),
        gde_pct=("gde_pct", "first"),
        rsst70_30_pct=("rsst70_30_pct", "first"),
        zroz_pct=("zroz_pct", "first"),
    )
    grouped["share_windows"] = grouped["n_top_decile_windows"] / len(windows)
    grouped = grouped.sort_values(["n_top_decile_windows", "avg_rank"], ascending=[False, True]).reset_index(drop=True)

    weight_rows: list[dict[str, object]] = []
    for sleeve in ["ntsx_pct", "gde_pct", "rsst70_30_pct", "zroz_pct"]:
        values = top_decile[sleeve].astype(float)
        weight_rows.append(
            {
                "sleeve": sleeve.removesuffix("_pct"),
                "mean": float(values.mean()),
                "p10": float(values.quantile(0.10)),
                "p25": float(values.quantile(0.25)),
                "median": float(values.quantile(0.50)),
                "p75": float(values.quantile(0.75)),
                "p90": float(values.quantile(0.90)),
            }
        )

    rsc_mask = (
        (top_decile["ntsx_pct"] == RSC_WEIGHTS[0])
        & (top_decile["gde_pct"] == RSC_WEIGHTS[1])
        & (top_decile["rsst70_30_pct"] == RSC_WEIGHTS[2])
        & (top_decile["zroz_pct"] == RSC_WEIGHTS[3])
    )
    weight_rows.append(
        {
            "sleeve": "rsc_like_top_decile_windows",
            "mean": float(top_decile.loc[rsc_mask, "window"].nunique()),
            "p10": float(top_decile.loc[rsc_mask, "rank"].mean()) if rsc_mask.any() else float("nan"),
            "p25": float("nan"),
            "median": float("nan"),
            "p75": float("nan"),
            "p90": float("nan"),
        }
    )
    return grouped, pd.DataFrame(weight_rows)


def run_segment_grid(asset_equity: pd.DataFrame) -> pd.DataFrame:
    asset_returns = asset_equity.pct_change().dropna()
    vectors = generate_weight_vectors()
    weights_pct = np.array(vectors, dtype=int)
    weights = weights_pct.astype(float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)
    frame = metrics_from_matrix_returns(equity[1:] / equity[:-1] - 1.0, weights_pct, vectors)
    return add_fitness_score(frame)


def run_cpcv_pbo(bundle: MatrixBundle) -> tuple[pd.DataFrame, pd.DataFrame]:
    pbo_result = pbo(bundle.returns, n_blocks=PBO_BLOCKS)
    pbo_summary = pd.DataFrame(
        [
            {
                "pbo": float(pbo_result.pbo),
                "pbo_gate": pbo_gate(float(pbo_result.pbo)),
                "n_blocks": int(pbo_result.n_blocks),
                "n_combinations": int(pbo_result.n_combinations),
                "logit_mean": float(np.mean(pbo_result.logits)),
                "logit_median": float(np.median(pbo_result.logits)),
                "logit_p10": float(np.quantile(pbo_result.logits, 0.10)),
                "logit_p90": float(np.quantile(pbo_result.logits, 0.90)),
            }
        ]
    )

    times = pd.Series(bundle.dates, index=bundle.dates)
    cpcv_rows: list[dict[str, object]] = []
    rsc_idx = vector_index(bundle.vectors, RSC_WEIGHTS)
    full_top_idx = vector_index(bundle.vectors, FULL_TOP_WEIGHTS)
    for split_id, (train_idx, test_idx) in enumerate(
        cpcv_splits(times, n_groups=CPCV_GROUPS, n_test_groups=CPCV_TEST_GROUPS, embargo_pct=0.0), start=1
    ):
        train_grid = score_matrix_returns(bundle.returns[train_idx], bundle.weights_pct, bundle.vectors)
        test_grid = score_matrix_returns(bundle.returns[test_idx], bundle.weights_pct, bundle.vectors).reset_index(drop=True)
        test_grid["oos_rank"] = np.arange(1, len(test_grid) + 1)
        selected = train_grid.iloc[0]
        selected_weights = weights_from_row(selected)
        selected_idx = vector_index(bundle.vectors, selected_weights)
        selected_oos = row_for_vector(test_grid, selected_weights)
        rsc_oos = row_for_vector(test_grid, RSC_WEIGHTS)
        full_top_oos = row_for_vector(test_grid, FULL_TOP_WEIGHTS)
        merged = train_grid.merge(
            test_grid,
            on=["ntsx_pct", "gde_pct", "rsst70_30_pct", "zroz_pct"],
            suffixes=("_train", "_test"),
        )
        cpcv_rows.append(
            {
                "split": split_id,
                "train_obs": int(len(train_idx)),
                "test_obs": int(len(test_idx)),
                "selected_portfolio": format_portfolio(selected_weights),
                "selected_idx": int(selected_idx),
                "test_cagr": float(selected_oos["cagr"]),
                "test_mdd": float(selected_oos["mdd"]),
                "test_sharpe": float(selected_oos["sharpe"]),
                "test_calmar": float(selected_oos["calmar"]),
                "test_terminal": float(selected_oos["terminal"]),
                "test_rank_pct": float(selected_oos["oos_rank"] / len(test_grid)),
                "rsc_terminal": float(rsc_oos["terminal"]),
                "full_top_terminal": float(full_top_oos["terminal"]),
                "beat_rsc_like": bool(float(selected_oos["terminal"]) > float(rsc_oos["terminal"])),
                "beat_full_top": bool(float(selected_oos["terminal"]) > float(full_top_oos["terminal"])),
                "rsc_idx": int(rsc_idx),
                "full_top_idx": int(full_top_idx),
                "train_test_fitness_spearman": float(merged["fitness_score_train"].corr(merged["fitness_score_test"], method="spearman")),
            }
        )
    return pd.DataFrame(cpcv_rows), pbo_summary


def run_fixed_rules(asset_equity: pd.DataFrame) -> pd.DataFrame:
    default_windows = build_windows(asset_equity.index, train_years=8, test_years=2, step_years=2)
    oos_parts: dict[str, list[pd.Series]] = {name: [] for name in FIXED_RULES}
    rows: list[dict[str, object]] = []
    for name, weights in FIXED_RULES.items():
        full_returns = portfolio_returns(asset_equity, weights)
        full_metrics = metrics_from_returns(full_returns)
        for window in default_windows:
            test_equity = asset_equity.loc[window.test_start : window.test_end]
            oos_parts[name].append(portfolio_returns(test_equity, weights))
        oos_returns = pd.concat(oos_parts[name]).sort_index().dropna()
        oos_returns = oos_returns[~oos_returns.index.duplicated(keep="first")]
        oos_metrics = metrics_from_returns(oos_returns)
        rows.append(
            {
                "rule": name,
                "portfolio": format_portfolio(weights),
                "full_cagr": full_metrics["cagr"],
                "full_mdd": full_metrics["mdd"],
                "full_sharpe": full_metrics["sharpe"],
                "full_calmar": full_metrics["calmar"],
                "oos_cagr": oos_metrics["cagr"],
                "oos_mdd": oos_metrics["mdd"],
                "oos_sharpe": oos_metrics["sharpe"],
                "oos_calmar": oos_metrics["calmar"],
                "oos_terminal": oos_metrics["terminal"],
            }
        )
    return pd.DataFrame(rows).sort_values(["oos_terminal", "oos_cagr"], ascending=False)


def portfolio_returns(asset_equity: pd.DataFrame, weights_pct: tuple[int, int, int, int]) -> pd.Series:
    asset_returns = asset_equity.pct_change().dropna()
    if asset_returns.empty:
        return pd.Series(dtype=float)
    weights = np.array([weights_pct], dtype=float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)[:, 0]
    returns = pd.Series(equity[1:] / equity[:-1] - 1.0, index=asset_returns.index)
    return returns.rename(format_portfolio(weights_pct))


def score_matrix_returns(returns: np.ndarray, weights_pct: np.ndarray, vectors: list[tuple[int, int, int, int]]) -> pd.DataFrame:
    frame = metrics_from_matrix_returns(returns, weights_pct, vectors)
    return add_fitness_score(frame)


def metrics_from_matrix_returns(returns: np.ndarray, weights_pct: np.ndarray, vectors: list[tuple[int, int, int, int]]) -> pd.DataFrame:
    returns = np.asarray(returns, dtype=float)
    equity = np.vstack([np.ones(returns.shape[1]), np.cumprod(1.0 + returns, axis=0)])
    terminal = equity[-1]
    n_periods = max(returns.shape[0], 1)
    cagr_values = np.where(terminal > 0, terminal ** (PERIODS_PER_YEAR / n_periods) - 1.0, -1.0)
    running_peak = np.maximum.accumulate(equity, axis=0)
    drawdowns = (running_peak - equity) / running_peak
    mdd_abs = drawdowns.max(axis=0)
    std = returns.std(axis=0, ddof=0)
    mean = returns.mean(axis=0)
    vol_values = std * np.sqrt(PERIODS_PER_YEAR)
    sharpe_values = np.divide(mean, std, out=np.zeros_like(mean), where=std > 1e-12) * np.sqrt(PERIODS_PER_YEAR)
    downside = np.minimum(returns, 0.0)
    downside_dev = np.sqrt(np.mean(downside**2, axis=0))
    sortino_values = np.divide(mean, downside_dev, out=np.full_like(mean, np.inf), where=downside_dev > 1e-12) * np.sqrt(PERIODS_PER_YEAR)
    calmar_values = np.divide(cagr_values, mdd_abs, out=np.full_like(cagr_values, np.inf), where=mdd_abs > 1e-12)
    return pd.DataFrame(
        {
            "portfolio": [format_portfolio(vector) for vector in vectors],
            "n_assets": (weights_pct > 0).sum(axis=1),
            "ntsx_pct": weights_pct[:, 0],
            "gde_pct": weights_pct[:, 1],
            "rsst70_30_pct": weights_pct[:, 2],
            "zroz_pct": weights_pct[:, 3],
            "cagr": cagr_values,
            "mdd": -mdd_abs,
            "mdd_abs": mdd_abs,
            "vol": vol_values,
            "sharpe": sharpe_values,
            "sortino": sortino_values,
            "calmar": calmar_values,
            "terminal": terminal,
        }
    )


def vector_index(vectors: list[tuple[int, int, int, int]], weights: tuple[int, int, int, int]) -> int:
    try:
        return vectors.index(weights)
    except ValueError as exc:
        raise KeyError(f"weights not found: {weights}") from exc


def weights_from_row(row: pd.Series) -> tuple[int, int, int, int]:
    return (int(row["ntsx_pct"]), int(row["gde_pct"]), int(row["rsst70_30_pct"]), int(row["zroz_pct"]))


def row_for_vector(frame: pd.DataFrame, weights: tuple[int, int, int, int]) -> pd.Series:
    mask = (
        (frame["ntsx_pct"] == weights[0])
        & (frame["gde_pct"] == weights[1])
        & (frame["rsst70_30_pct"] == weights[2])
        & (frame["zroz_pct"] == weights[3])
    )
    matched = frame.loc[mask]
    if matched.empty:
        raise KeyError(f"weights not found in frame: {weights}")
    return matched.iloc[0]


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
                cells.append("PASS" if bool(value) else "FAIL")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(
    wf_sensitivity: pd.DataFrame,
    stability_portfolios: pd.DataFrame,
    stability_weights: pd.DataFrame,
    cpcv_df: pd.DataFrame,
    pbo_summary: pd.DataFrame,
    fixed_rules: pd.DataFrame,
) -> None:
    pbo_row = pbo_summary.iloc[0]
    cpcv_required = int(math.ceil(WF_PASS_RATIO * len(cpcv_df)))
    cpcv_beat_rsc = int(cpcv_df["beat_rsc_like"].sum())
    cpcv_unique = int(cpcv_df["selected_portfolio"].nunique())
    best_fixed = fixed_rules.iloc[0]
    rsc_fixed = fixed_rules[fixed_rules["rule"] == "rsc_like_35_40_25"].iloc[0]

    report = (
        "# Four-Asset Grid Robustness: WF Sensitivity, Stability, CPCV/PBO\n\n"
        "Status: research-only diagnostic. No deployment, paper-trade label or mandate change.\n\n"
        "## Summary\n\n"
        f"- PBO over the full `1,771`-portfolio grid: `{float(pbo_row['pbo']):.3f}` -> `{pbo_row['pbo_gate']}`. Gate reference: reject when PBO >= 0.5 `[advances_fin_ml, p.208-211]`.\n"
        f"- CPCV split selection beat fixed RSC-like `35/40/25` in `{cpcv_beat_rsc}/{len(cpcv_df)}` splits; 75% consistency would require `{cpcv_required}/{len(cpcv_df)}`.\n"
        f"- CPCV selected `{cpcv_unique}` unique portfolios across `{len(cpcv_df)}` splits; median OOS rank percentile `{_fmt_pct(cpcv_df['test_rank_pct'].median())}`; mean train/test Spearman `{_fmt_num(cpcv_df['train_test_fitness_spearman'].mean())}`.\n"
        f"- WF sensitivity does not rescue optimization: no scenario reaches the 75% beat-RSC consistency threshold.\n"
        f"- Best fixed rule in default OOS comparison is `{best_fixed['rule']}` with OOS CAGR `{_fmt_pct(best_fixed['oos_cagr'])}` and MDD `{_fmt_pct(best_fixed['oos_mdd'])}`; RSC-like is OOS CAGR `{_fmt_pct(rsc_fixed['oos_cagr'])}`, MDD `{_fmt_pct(rsc_fixed['oos_mdd'])}`.\n\n"
        "Interpretation: the grid is useful as a neighborhood/stress screen, but the weight optimizer itself is unstable. The robust action is to keep a simple fixed allocation thesis rather than reselecting weights from the same grid `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`.\n\n"
        "## WF Sensitivity\n\n"
        + _markdown_table(
            wf_sensitivity,
            [
                "scenario",
                "n_windows",
                "wf_cagr",
                "wf_mdd",
                "wf_sharpe",
                "rsc_cagr",
                "rsc_mdd",
                "windows_beat_rsc_like",
                "pass_vs_rsc_like_75pct",
                "unique_selected_portfolios",
                "mean_train_test_fitness_spearman",
            ],
            {
                "n_windows": "int",
                "wf_cagr": "pct",
                "wf_mdd": "pct",
                "wf_sharpe": "num",
                "rsc_cagr": "pct",
                "rsc_mdd": "pct",
                "windows_beat_rsc_like": "int",
                "pass_vs_rsc_like_75pct": "bool",
                "unique_selected_portfolios": "int",
                "mean_train_test_fitness_spearman": "num",
            },
        )
        + "\n\n## CPCV/PBO\n\n"
        + _markdown_table(
            pbo_summary,
            ["pbo", "pbo_gate", "n_blocks", "n_combinations", "logit_mean", "logit_median", "logit_p10", "logit_p90"],
            {"pbo": "num", "n_blocks": "int", "n_combinations": "int", "logit_mean": "num", "logit_median": "num", "logit_p10": "num", "logit_p90": "num"},
        )
        + "\n\n"
        + _markdown_table(
            cpcv_df.head(12),
            ["split", "selected_portfolio", "test_cagr", "test_mdd", "test_rank_pct", "beat_rsc_like", "train_test_fitness_spearman"],
            {"split": "int", "test_cagr": "pct", "test_mdd": "pct", "test_rank_pct": "pct", "beat_rsc_like": "bool", "train_test_fitness_spearman": "num"},
        )
        + "\n\n## Top-Decile Stability Map\n\n"
        "Top-decile stability uses the default `8y` IS windows and records portfolios that land in the train top 10%. This asks for a stable region, not a single lucky argmax.\n\n"
        + _markdown_table(
            stability_weights,
            ["sleeve", "mean", "p10", "p25", "median", "p75", "p90"],
            {"mean": "num", "p10": "num", "p25": "num", "median": "num", "p75": "num", "p90": "num"},
        )
        + "\n\nMost frequent exact top-decile portfolios:\n\n"
        + _markdown_table(
            stability_portfolios.head(15),
            ["portfolio", "n_top_decile_windows", "share_windows", "avg_rank", "ntsx_pct", "gde_pct", "rsst70_30_pct", "zroz_pct"],
            {"n_top_decile_windows": "int", "share_windows": "pct", "avg_rank": "num", "ntsx_pct": "int", "gde_pct": "int", "rsst70_30_pct": "int", "zroz_pct": "int"},
        )
        + "\n\n## Fixed Rules\n\n"
        + _markdown_table(
            fixed_rules,
            ["rule", "portfolio", "full_cagr", "full_mdd", "oos_cagr", "oos_mdd", "oos_sharpe", "oos_terminal"],
            {"full_cagr": "pct", "full_mdd": "pct", "oos_cagr": "pct", "oos_mdd": "pct", "oos_sharpe": "num", "oos_terminal": "num"},
        )
        + "\n\n## Artifacts\n\n"
        f"- WF sensitivity: `{WF_SENSITIVITY_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Top-decile portfolios: `{STABILITY_PORTFOLIOS_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Top-decile weight distribution: `{STABILITY_WEIGHTS_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- CPCV splits: `{CPCV_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- PBO summary: `{PBO_SUMMARY_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Fixed rules: `{FIXED_RULES_CSV.relative_to(REPO_ROOT)}`.\n"
    )
    REPORT_MD.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
