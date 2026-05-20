"""Local Pareto search around the B4-like stability branch.

This is a constrained deterministic grid, not a broad GA. It searches the B4-like
family after the Pareto/regime report showed that path robustness is concentrated in
SPY/GDE/managed-futures/duration stacks. The grid uses 5% steps to match the study's
discrete static-portfolio convention, while adding the 2.5%-granularity Testfol.io
reference as a non-grid anchor `[testing_tuning, p.327-335]`.

Promotion remains blocked without separate PBO/DSR/walk-forward/bootstrap validation
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Iterator
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.score_portfolio import (  # noqa: E402
    GrowthCache,
    HORIZON_DAYS,
    _rolling_metrics_from_cumulatives,
    _rolling_starts,
    _series_cumulatives,
    metrics_from_returns,
    monthly_rebalanced_returns,
    precompute_growth_matrix,
)
from studies.static_spy_beater_portfolio.scripts.universe import (  # noqa: E402
    load_universe_returns,
    portfolio_effective_exposure,
)

STUDY_DIR = REPO / "studies" / "static_spy_beater_portfolio"

GRID_ASSETS = ("SPYSIM", "GDESIM", "KMLMSIM", "RSSTSIM", "ZROZSIM", "IEFSIM", "TLTSIM", "CASHX")
STEP = 0.05
MDD_TARGET = -0.32
CHUNK_SIZE = 400
MAX_ACTIVE_ASSETS = 6

REFERENCE_WEIGHTS = {
    "B4_like_testfolio_reference": {
        "SPYSIM": 0.475,
        "GDESIM": 0.25,
        "KMLMSIM": 0.25,
        "ZROZSIM": 0.25,
        "IEFSIM": 0.15,
        "CASHX": -0.375,
    },
    "B4_original_reference": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
    "SPYSIM_buy_hold": {"SPYSIM": 1.0},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-margin",
        action="store_true",
        help="Require CASHX >= 0 and gross weight <= 1.0 for implementation without margin.",
    )
    args = parser.parse_args()

    out_dir = STUDY_DIR / "results" / ("local_pareto_b4_no_margin" if args.no_margin else "local_pareto_b4_like")
    plot_dir = out_dir / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    cash_min = 0.0 if args.no_margin else -0.40
    cash_max = 0.10 if args.no_margin else 0.0

    frame = load_universe_returns("mf_1988")
    required = sorted(set(GRID_ASSETS) | {asset for weights in REFERENCE_WEIGHTS.values() for asset in weights})
    returns = frame[required].dropna()
    if returns.empty:
        raise ValueError(f"no common data for {required}")
    growth_cache = precompute_growth_matrix(returns)

    rows: list[dict[str, object]] = []
    feasible_rows: list[dict[str, object]] = []
    pareto_rows: list[dict[str, object]] = []
    for name, weights in REFERENCE_WEIGHTS.items():
        row = score_candidate(name, weights, returns, growth_cache, is_grid=False, compute_rolling=True)
        rows.append(row)

    batch: list[tuple[str, dict[str, float]]] = []
    scored = 0
    for i, weights in enumerate(iter_grid_weights(cash_min=cash_min, cash_max=cash_max), start=1):
        batch.append((f"grid_{i:05d}", weights))
        if len(batch) < CHUNK_SIZE:
            continue
        new_rows, feasible_rows, pareto_rows = score_grid_batch(
            batch, returns, growth_cache, feasible_rows, pareto_rows
        )
        rows.extend(new_rows)
        scored += len(batch)
        batch = []
        if scored % 15000 == 0:
            print(
                f"scored={scored} feasible={len(feasible_rows)} pareto={len(pareto_rows)}",
                flush=True,
            )
    if batch:
        new_rows, feasible_rows, pareto_rows = score_grid_batch(
            batch, returns, growth_cache, feasible_rows, pareto_rows
        )
        rows.extend(new_rows)
        scored += len(batch)
    print(f"scored={scored} feasible={len(feasible_rows)} pareto={len(pareto_rows)}", flush=True)

    candidates = pd.DataFrame(rows)
    candidates.to_csv(out_dir / "candidates.csv", index=False)

    feasible = pd.DataFrame(feasible_rows, columns=candidates.columns)
    pareto = pd.DataFrame(pareto_rows, columns=candidates.columns)
    if not pareto.empty:
        pareto = pareto.sort_values(["full_calmar", "full_cagr"], ascending=False)
    feasible.to_csv(out_dir / "feasible.csv", index=False)
    pareto.to_csv(out_dir / "pareto.csv", index=False)

    write_report(
        candidates,
        feasible,
        pareto,
        returns.index[0],
        returns.index[-1],
        out_dir=out_dir,
        no_margin=args.no_margin,
        cash_min=cash_min,
        cash_max=cash_max,
    )
    plot_results(candidates, feasible, pareto, plot_dir)


def iter_grid_weights(*, cash_min: float = -0.40, cash_max: float = 0.0) -> Iterator[dict[str, float]]:
    """Enumerate B4-like constrained weights in 5% units.

    Constraints follow `NEXT_STEPS.md`: GDE 15-35%, managed futures 15-40%,
    duration 25-45%, and explicit documentation of negative CASHX as stacked
    exposure `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`.
    """
    vals = [round(i * STEP, 10) for i in range(0, 13)]
    cash_vals = [round(cash_min + i * STEP, 10) for i in range(int(round((cash_max - cash_min) / STEP)) + 1)]
    seen: set[tuple[tuple[str, float], ...]] = set()
    for gde in [0.15, 0.20, 0.25, 0.30, 0.35]:
        for kmlm in vals:
            for rsst in vals:
                mf = kmlm + rsst
                if mf < 0.15 - 1e-12 or mf > 0.40 + 1e-12:
                    continue
                for zroz in vals:
                    for ief in vals:
                        for tlt in vals:
                            duration = zroz + ief + tlt
                            if duration < 0.25 - 1e-12 or duration > 0.45 + 1e-12:
                                continue
                            for cash in cash_vals:
                                spy = 1.0 - (gde + kmlm + rsst + zroz + ief + tlt + cash)
                                if spy < -1e-12 or spy > 0.70 + 1e-12:
                                    continue
                                weights = clean_weights(
                                    {
                                        "SPYSIM": spy,
                                        "GDESIM": gde,
                                        "KMLMSIM": kmlm,
                                        "RSSTSIM": rsst,
                                        "ZROZSIM": zroz,
                                        "IEFSIM": ief,
                                        "TLTSIM": tlt,
                                        "CASHX": cash,
                                    }
                                )
                                if len(weights) > MAX_ACTIVE_ASSETS:
                                    continue
                                key = tuple(sorted(weights.items()))
                                if key not in seen:
                                    seen.add(key)
                                    yield weights


def clean_weights(weights: dict[str, float]) -> dict[str, float]:
    return {asset: round(weight, 10) for asset, weight in weights.items() if abs(weight) > 1e-12}


def score_candidate(
    name: str,
    weights: dict[str, float],
    returns: pd.DataFrame,
    growth_cache: object,
    *,
    is_grid: bool,
    compute_rolling: bool,
) -> dict[str, object]:
    series = monthly_rebalanced_returns(returns, weights, growth_cache=growth_cache)
    full = metrics_from_returns(series)
    rolling = rolling_5y_summary(series, returns["SPYSIM"]) if compute_rolling else empty_rolling_summary()
    exposure = portfolio_effective_exposure(weights)
    return {
        "candidate": name,
        "is_grid": is_grid,
        "weights": json.dumps(weights, sort_keys=True),
        "cash_weight": weights.get("CASHX", 0.0),
        "gross_weight": sum(abs(v) for v in weights.values()),
        "net_weight": sum(weights.values()),
        "is_pure_long_only": all(v >= -1e-12 for v in weights.values()),
        "effective_exposure": json.dumps(exposure, sort_keys=True),
        "full_start": full["start"],
        "full_end": full["end"],
        "full_cagr": full["cagr"],
        "full_mdd": full["mdd"],
        "full_sharpe": full["sharpe"],
        "full_sortino": full["sortino"],
        "full_calmar": full["calmar"],
        "full_terminal_wealth": full["terminal_wealth"],
        **rolling,
    }


def score_grid_batch(
    batch: list[tuple[str, dict[str, float]]],
    returns: pd.DataFrame,
    growth_cache: GrowthCache,
    feasible_rows: list[dict[str, object]],
    pareto_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    full_rows = score_full_batch(batch, growth_cache)
    out_rows: list[dict[str, object]] = []
    for row, (_name, weights) in zip(full_rows, batch, strict=True):
        if row["full_mdd"] >= MDD_TARGET:
            series = monthly_rebalanced_returns(returns, weights, growth_cache=growth_cache)
            rolling = rolling_5y_summary(series, returns["SPYSIM"])
            row.update(rolling)
            if row["rolling_5y_cagr_p10"] > 0.0:
                feasible_rows.append(row.copy())
                pareto_rows = update_pareto(pareto_rows, row)
        out_rows.append(row)
    return out_rows, feasible_rows, pareto_rows


def score_full_batch(batch: list[tuple[str, dict[str, float]]], growth_cache: GrowthCache) -> list[dict[str, object]]:
    weights_matrix = np.zeros((len(growth_cache.columns), len(batch)), dtype=float)
    for col_idx, (_name, weights) in enumerate(batch):
        for asset, weight in weights.items():
            weights_matrix[growth_cache.column_index[asset], col_idx] = weight
    daily_combined = growth_cache.growth @ weights_matrix
    month_end_factors = daily_combined[growth_cache.month_ends, :]
    cum_prev = np.vstack([np.ones((1, len(batch))), np.cumprod(month_end_factors, axis=0)[:-1, :]])
    lengths = (growth_cache.month_ends - growth_cache.month_starts + 1).astype(np.int64)
    equity = np.repeat(cum_prev, lengths, axis=0) * daily_combined
    returns_arr = np.empty_like(equity)
    returns_arr[0, :] = equity[0, :] - 1.0
    returns_arr[1:, :] = equity[1:, :] / equity[:-1, :] - 1.0
    years = equity.shape[0] / 252.0
    terminal = equity[-1, :]
    cagr = np.power(terminal, 1.0 / years) - 1.0
    running_max = np.maximum.accumulate(equity, axis=0)
    drawdown = equity / running_max - 1.0
    mdd = np.min(drawdown, axis=0)
    mean = np.mean(returns_arr, axis=0)
    vol = np.std(returns_arr, axis=0)
    downside = np.array(
        [np.std(col[col < 0.0]) if np.any(col < 0.0) else np.nan for col in returns_arr.T],
        dtype=float,
    )
    sharpe = np.divide(mean * math.sqrt(252.0), vol, out=np.full_like(mean, np.nan), where=vol > 0.0)
    sortino = np.divide(
        mean * math.sqrt(252.0), downside, out=np.full_like(mean, np.nan), where=downside > 0.0
    )
    calmar = np.divide(cagr, np.abs(mdd), out=np.full_like(cagr, np.nan), where=mdd < 0.0)

    rows: list[dict[str, object]] = []
    start = str(growth_cache.index[0].date())
    end = str(growth_cache.index[-1].date())
    for i, (name, weights) in enumerate(batch):
        exposure = portfolio_effective_exposure(weights)
        rows.append(
            {
                "candidate": name,
                "is_grid": True,
                "weights": json.dumps(weights, sort_keys=True),
                "cash_weight": weights.get("CASHX", 0.0),
                "gross_weight": sum(abs(v) for v in weights.values()),
                "net_weight": sum(weights.values()),
                "is_pure_long_only": all(v >= -1e-12 for v in weights.values()),
                "effective_exposure": json.dumps(exposure, sort_keys=True),
                "full_start": start,
                "full_end": end,
                "full_cagr": float(cagr[i]),
                "full_mdd": float(mdd[i]),
                "full_sharpe": float(sharpe[i]),
                "full_sortino": float(sortino[i]),
                "full_calmar": float(calmar[i]),
                "full_terminal_wealth": float(terminal[i]),
                **empty_rolling_summary(),
            }
        )
    return rows


def empty_rolling_summary() -> dict[str, float]:
    return {
        "rolling_5y_cagr_p10": math.nan,
        "rolling_5y_cagr_median": math.nan,
        "rolling_5y_mdd_p10": math.nan,
        "rolling_5y_mdd_worst": math.nan,
        "rolling_5y_relative_wealth_spy_p10": math.nan,
        "rolling_5y_relative_wealth_spy_median": math.nan,
    }


def rolling_5y_summary(portfolio: pd.Series, spy: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"portfolio": portfolio, "spy": spy}, axis=1).dropna()
    days = HORIZON_DAYS["5y"]
    starts = _rolling_starts(len(aligned), days, rolling_step=1)
    p = _rolling_metrics_from_cumulatives(
        _series_cumulatives(aligned["portfolio"].to_numpy(dtype=float)), days, starts, compute_drawdown=False
    )
    s = _rolling_metrics_from_cumulatives(
        _series_cumulatives(aligned["spy"].to_numpy(dtype=float)), days, starts, compute_drawdown=False
    )
    rel_wealth = p["terminal_wealth"] / s["terminal_wealth"] - 1.0
    return {
        "rolling_5y_cagr_p10": float(np.nanquantile(p["cagr"], 0.10)),
        "rolling_5y_cagr_median": float(np.nanmedian(p["cagr"])),
        "rolling_5y_mdd_p10": math.nan,
        "rolling_5y_mdd_worst": math.nan,
        "rolling_5y_relative_wealth_spy_p10": float(np.nanquantile(rel_wealth, 0.10)),
        "rolling_5y_relative_wealth_spy_median": float(np.nanmedian(rel_wealth)),
    }


PARETO_OBJECTIVES = (
    "full_cagr",
    "full_mdd",
    "full_calmar",
    "rolling_5y_cagr_p10",
    "rolling_5y_relative_wealth_spy_p10",
)


def update_pareto(frontier: list[dict[str, object]], row: dict[str, object]) -> list[dict[str, object]]:
    if any(dominates(existing, row) for existing in frontier):
        return frontier
    return [existing for existing in frontier if not dominates(row, existing)] + [row]


def dominates(left: dict[str, object], right: dict[str, object]) -> bool:
    left_values = [float(left[obj]) for obj in PARETO_OBJECTIVES]
    right_values = [float(right[obj]) for obj in PARETO_OBJECTIVES]
    return all(left_value >= right_value for left_value, right_value in zip(left_values, right_values, strict=True)) and any(
        left_value > right_value for left_value, right_value in zip(left_values, right_values, strict=True)
    )


def write_report(
    candidates: pd.DataFrame,
    feasible: pd.DataFrame,
    pareto: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    *,
    out_dir: Path,
    no_margin: bool,
    cash_min: float,
    cash_max: float,
) -> None:
    refs = candidates[~candidates["is_grid"]].copy()
    top = pareto.head(20).copy()
    high_return = feasible.sort_values(["full_cagr", "full_calmar"], ascending=False).head(20).copy()
    ref_table = display_cols(refs).to_markdown(index=False, floatfmt=".6f")
    top_table = display_cols(top).to_markdown(index=False, floatfmt=".6f") if not top.empty else "No feasible Pareto rows."
    high_return_table = (
        display_cols(high_return).to_markdown(index=False, floatfmt=".6f") if not high_return.empty else "No feasible rows."
    )
    best = top.iloc[0] if not top.empty else None
    best_return = high_return.iloc[0] if not high_return.empty else None
    if best is None:
        decision = "No grid candidate passed the MDD and rolling 5y CAGR guards. Keep B4-like as the stability anchor."
    else:
        decision = (
            f"Top Pareto-by-Calmar candidate `{best['candidate']}` reached CAGR `{best['full_cagr']:.2%}`, "
            f"MDD `{best['full_mdd']:.2%}`, Calmar `{best['full_calmar']:.3f}`, and 5y CAGR p10 "
            f"`{best['rolling_5y_cagr_p10']:.2%}`. It remains discovery-only."
        )
        if best_return is not None:
            decision += (
                f" The highest-CAGR feasible row `{best_return['candidate']}` reached CAGR "
                f"`{best_return['full_cagr']:.2%}`, MDD `{best_return['full_mdd']:.2%}`, Calmar "
                f"`{best_return['full_calmar']:.3f}`, and 5y relative-wealth p10 vs SPY "
                f"`{best_return['rolling_5y_relative_wealth_spy_p10']:.2%}`."
            )
    title = "B4-Like No-Margin Local Pareto Search" if no_margin else "B4-Like Local Pareto Search"
    implementation_note = (
        "This mode is implementation-constrained: `CASHX >= 0`, no negative cash, and gross weight is capped by non-negative weights."
        if no_margin
        else "This mode allows negative `CASHX`; rows with `CASHX < 0` are stacked/leverage references, not pure long-only."
    )
    report = f"""# {title}

Fixed local grid over `{start.date()}..{end.date()}`. This search is constrained around the B4-like stability branch, not a broad GA. It uses 5% grid weights plus the original 2.5%-step Testfol.io reference as an anchor; negative `CASHX` means stacked/leverage reference, not pure long-only `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`.

{implementation_note}

## Search Rules

- Grid assets: `{', '.join(GRID_ASSETS)}`.
- GDESIM: `15-35%`.
- KMLMSIM + RSSTSIM: `15-40%`.
- ZROZSIM + IEFSIM + TLTSIM: `25-45%`.
- CASHX: `{cash_min:.0%}..{cash_max:.0%}` in 5% steps.
- Max active assets: `{MAX_ACTIVE_ASSETS}` sleeves, to keep the search local around the compact B4-like stack.
- Feasible filter: full-period MDD no worse than `{MDD_TARGET:.0%}` and rolling 5y CAGR p10 > `0`.
- Pareto objectives: maximize CAGR, MDD, Calmar, rolling 5y CAGR p10, and rolling 5y relative wealth p10 versus SPY `[testing_tuning, p.327-335]`.
- Rolling 5y MDD is not computed in this local screen; full-period MDD is the drawdown constraint. Use the separate Pareto/regime report for exact rolling MDD diagnostics.

## Counts

- Total rows scored: `{len(candidates)}`.
- Grid rows: `{int(candidates['is_grid'].sum())}`.
- Feasible grid rows: `{len(feasible)}`.
- Pareto rows: `{len(pareto)}`.

## References

{ref_table}

## Top Pareto Rows

{top_table}

## Highest-CAGR Feasible Rows

{high_return_table}

## Plots

![CAGR vs MDD](plots/cagr_vs_mdd.png)

![Calmar vs CAGR](plots/calmar_vs_cagr.png)

## Reading

{decision}

Status remains discovery-only: this is a local decision-quality screen, not PBO/DSR/walk-forward/bootstrap validation `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")


def display_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "candidate",
        "full_cagr",
        "full_mdd",
        "full_sharpe",
        "full_sortino",
        "full_calmar",
        "full_terminal_wealth",
        "rolling_5y_cagr_p10",
        "rolling_5y_relative_wealth_spy_p10",
        "cash_weight",
        "gross_weight",
        "weights",
    ]
    return df.reindex(columns=cols)


def plot_results(candidates: pd.DataFrame, feasible: pd.DataFrame, pareto: pd.DataFrame, plot_dir: Path) -> None:
    plot_scatter(
        candidates,
        feasible,
        pareto,
        x="full_mdd",
        y="full_cagr",
        out=plot_dir / "cagr_vs_mdd.png",
        xlabel="Full MDD (less negative is better)",
        ylabel="Full CAGR",
        title="B4-like Local Search: CAGR vs MDD",
    )
    plot_scatter(
        candidates,
        feasible,
        pareto,
        x="full_cagr",
        y="full_calmar",
        out=plot_dir / "calmar_vs_cagr.png",
        xlabel="Full CAGR",
        ylabel="Full Calmar",
        title="B4-like Local Search: Calmar vs CAGR",
    )


def plot_scatter(
    candidates: pd.DataFrame,
    feasible: pd.DataFrame,
    pareto: pd.DataFrame,
    *,
    x: str,
    y: str,
    out: Path,
    xlabel: str,
    ylabel: str,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    grid = candidates[candidates["is_grid"]]
    ax.scatter(grid[x], grid[y], s=10, alpha=0.20, label="grid")
    if not feasible.empty:
        ax.scatter(feasible[x], feasible[y], s=16, alpha=0.45, label="feasible")
    if not pareto.empty:
        ax.scatter(pareto[x], pareto[y], s=36, alpha=0.95, label="pareto")
    refs = candidates[~candidates["is_grid"]]
    ax.scatter(refs[x], refs[y], marker="x", s=70, label="references")
    for _, row in refs.iterrows():
        ax.annotate(str(row["candidate"]), (row[x], row[y]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
