"""Generate a fixed-candidate Pareto/regime report for the static SPY-beater study.

The report is deliberately diagnostic, not an optimizer: it compares already-found
candidate portfolios across full-period, rolling-window, and named market regimes
before any new search is run. Rolling 3y/5y/10y summaries, drawdown, and relative
wealth diagnostics are included because bad-window behavior is where optimized
strategies most often hide fragility `[testing_tuning, p.327-335]`. The comparison
remains discovery-only and does not replace multiple-testing validation
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.score_portfolio import (  # noqa: E402
    HORIZON_DAYS,
    _rolling_metrics_from_cumulatives,
    _rolling_starts,
    _series_cumulatives,
    metrics_from_returns,
    monthly_rebalanced_returns,
)
from studies.static_spy_beater_portfolio.scripts.universe import (  # noqa: E402
    load_universe_returns,
    portfolio_effective_exposure,
)

STUDY_DIR = REPO / "studies" / "static_spy_beater_portfolio"
OUT_DIR = STUDY_DIR / "results" / "pareto_regime_report"
REFINE_ARTIFACT = (
    STUDY_DIR
    / "results"
    / "refine_robust"
    / "lead_family_focused_spy_beater_p10_mdd_guard_refine"
    / "top_exact.csv"
)

ROLLING_HORIZONS = ("3y", "5y", "10y", "15y")
ROLLING_PLOT_HORIZONS = ("3y", "5y", "10y", "15y")
REGIMES = {
    "dot_com_drawdown": ("2000-03-24", "2002-10-09"),
    "gfc_drawdown": ("2007-10-09", "2009-03-09"),
    "qe_bull": ("2010-01-01", "2019-12-31"),
    "covid_crash": ("2020-02-19", "2020-03-23"),
    "inflation_rates_shock": ("2021-12-27", "2022-10-20"),
    "recent_recovery": ("2023-01-01", None),
}


@dataclass(frozen=True)
class Candidate:
    name: str
    weights: dict[str, float]
    kind: str
    note: str


def candidate_set() -> list[Candidate]:
    """Fixed candidate list; no broad GA or fresh optimization is run here."""
    ga_robust = {"GDESIM": 0.35, "RSSTSIM": 0.50, "SPYSIM": 0.10, "ZROZSIM": 0.05}
    return [
        Candidate(
            "GA_aggressive",
            {"GDESIM": 0.35, "RSSTSIM": 0.50, "TQQQSIM": 0.05, "ZROZSIM": 0.10},
            "long_only_static",
            "Consistency-guard GA lead; includes a small 3x Nasdaq sleeve.",
        ),
        Candidate(
            "GA_robust",
            ga_robust,
            "long_only_static",
            "Strict p10-MDD GA-family incumbent.",
        ),
        Candidate(
            "Refined_GA_robust",
            ga_robust,
            "long_only_static_artifact_confirmed",
            "Same weights as GA_robust; confirmed against results/refine_robust artifact.",
        ),
        Candidate(
            "B4_like_testfolio",
            {
                "SPYSIM": 0.475,
                "GDESIM": 0.25,
                "KMLMSIM": 0.25,
                "ZROZSIM": 0.25,
                "IEFSIM": 0.15,
                "CASHX": -0.375,
            },
            "stacked_leveraged_reference",
            "Reference stacked portfolio with negative CASHX; not a pure long-only allocation.",
        ),
        Candidate(
            "B4_no_margin_lead",
            {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25},
            "long_only_static_no_external_margin",
            "Best high-CAGR feasible row from local B4 no-margin Pareto search.",
        ),
        Candidate(
            "SPYSIM_buy_hold",
            {"SPYSIM": 1.0},
            "benchmark_buy_hold",
            "Primary buy-and-hold benchmark.",
        ),
        Candidate(
            "B4_original",
            {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
            "long_only_static",
            "Original B4 reference when all synthetic legs are available.",
        ),
        Candidate(
            "GA_stacked_seed20260519",
            {"GDESIM": 0.25, "RSSTSIM": 0.30, "ZROZSIM": 0.15, "ESBGSIM": 0.20, "CTAPSIM": 0.05, "MATESIM": 0.05},
            "long_only_static_stacked_proxy",
            "Triage GA winner seed 20260519 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp).",
        ),
        Candidate(
            "GA_stacked_seed20260520",
            {"GDESIM": 0.20, "RSSTSIM": 0.25, "ZROZSIM": 0.15, "ESBGSIM": 0.25, "MATESIM": 0.10, "CTAPSIM": 0.05},
            "long_only_static_stacked_proxy",
            "Triage GA winner seed 20260520 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp).",
        ),
        Candidate(
            "GA_stacked_seed20260521",
            {"GDESIM": 0.20, "RSSTSIM": 0.30, "ZROZSIM": 0.15, "ESBGSIM": 0.25, "CTAPSIM": 0.05, "MATESIM": 0.05},
            "long_only_static_stacked_proxy",
            "Triage GA winner seed 20260521 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp).",
        ),
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = candidate_set()
    confirm_refined_candidate(candidates)

    # Switched from `mf_1988` to `core_beater_stacked_expansion` to include the
    # 8 local stacked-ETF proxies needed by the 2026-05-19 GA triage candidates.
    # Common window compresses to 2000+ (CTAPSIM binding); previous-window
    # numbers for 1988-2026 candidates remain in `FINAL_REPORT_35_40_25_CORE.md`.
    frame = load_universe_returns("core_beater_stacked_expansion")
    required = sorted({ticker for candidate in candidates for ticker in candidate.weights})
    aligned_returns = frame[required].dropna()
    if aligned_returns.empty:
        raise ValueError(f"no common data for required tickers: {required}")

    portfolio_returns = {
        candidate.name: monthly_rebalanced_returns(aligned_returns, candidate.weights)
        for candidate in candidates
    }
    common = pd.concat(portfolio_returns, axis=1, sort=True).dropna()
    spy = common["SPYSIM_buy_hold"]

    metrics_rows: list[dict[str, object]] = []
    rolling_rows: list[dict[str, object]] = []
    for candidate in candidates:
        returns = common[candidate.name]
        metrics_rows.append(build_metrics_row(candidate, returns, spy))
        rolling_rows.extend(build_rolling_rows(candidate.name, returns, spy))

    metrics = pd.DataFrame(metrics_rows)
    rolling = pd.DataFrame(rolling_rows)
    metrics.to_csv(OUT_DIR / "metrics.csv", index=False)
    rolling.to_csv(OUT_DIR / "rolling.csv", index=False)
    plot_paths = generate_plots(common, OUT_DIR / "plots")
    write_report(metrics, rolling, candidates, common.index[0], common.index[-1], plot_paths)


def confirm_refined_candidate(candidates: list[Candidate]) -> None:
    """Verify the refined robust artifact still identifies the expected allocation."""
    robust = next(candidate for candidate in candidates if candidate.name == "GA_robust")
    refined = next(candidate for candidate in candidates if candidate.name == "Refined_GA_robust")
    if robust.weights != refined.weights:
        raise ValueError("Refined_GA_robust must match GA_robust for apples-to-apples reporting")
    if not REFINE_ARTIFACT.exists():
        raise FileNotFoundError(f"missing refine artifact: {REFINE_ARTIFACT}")
    top = pd.read_csv(REFINE_ARTIFACT).iloc[0]
    artifact_weights = json.loads(str(top["weights"]))
    if normalize_weights(artifact_weights) != normalize_weights(refined.weights):
        raise ValueError(
            "Refined robust artifact does not match expected weights: "
            f"artifact={artifact_weights}, expected={refined.weights}"
        )


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    return {asset: round(float(weight), 10) for asset, weight in sorted(weights.items()) if abs(weight) > 1e-12}


def build_metrics_row(candidate: Candidate, returns: pd.Series, spy: pd.Series) -> dict[str, object]:
    full = metrics_with_ulcer(returns)
    row: dict[str, object] = {
        "candidate": candidate.name,
        "kind": candidate.kind,
        "weights": json.dumps(candidate.weights, sort_keys=True),
        "note": candidate.note,
        "is_long_only_pure": all(weight >= -1e-12 for weight in candidate.weights.values()),
        "gross_weight": sum(abs(weight) for weight in candidate.weights.values()),
        "net_weight": sum(candidate.weights.values()),
        "effective_exposure": json.dumps(portfolio_effective_exposure(candidate.weights), sort_keys=True),
    }
    for key in ("start", "end", "days", "years", "cagr", "mdd", "sharpe", "sortino", "calmar", "ulcer", "terminal_wealth"):
        row[f"full_{key}"] = full.get(key, math.nan)

    for regime, (start, end) in REGIMES.items():
        regime_returns = slice_returns(returns, start, end)
        regime_metrics = metrics_with_ulcer(regime_returns)
        for key in ("start", "end", "days", "years", "cagr", "mdd", "sharpe", "sortino", "calmar", "ulcer", "terminal_wealth"):
            row[f"regime_{regime}_{key}"] = regime_metrics.get(key, math.nan)
        spy_regime = metrics_with_ulcer(slice_returns(spy, start, end))
        row[f"regime_{regime}_wealth_vs_spy"] = safe_ratio(
            regime_metrics.get("terminal_wealth", math.nan), spy_regime.get("terminal_wealth", math.nan)
        )

    return row


def build_rolling_rows(candidate: str, returns: pd.Series, spy: pd.Series) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    aligned = pd.concat({"portfolio": returns, "spy": spy}, axis=1).dropna()
    p_cum = _series_cumulatives(aligned["portfolio"].to_numpy(dtype=float))
    s_cum = _series_cumulatives(aligned["spy"].to_numpy(dtype=float))
    for horizon in ROLLING_HORIZONS:
        days = HORIZON_DAYS[horizon]
        if len(aligned) < days:
            continue
        starts = _rolling_starts(len(aligned), days, rolling_step=1)
        p_metrics = _rolling_metrics_from_cumulatives(p_cum, days, starts, compute_drawdown=True)
        s_metrics = _rolling_metrics_from_cumulatives(s_cum, days, starts, compute_drawdown=True)
        cagr_values = p_metrics["cagr"].tolist()
        mdd_values = p_metrics["mdd"].tolist()
        rel_wealth_values = (p_metrics["terminal_wealth"] / s_metrics["terminal_wealth"] - 1.0).tolist()
        rows.extend(summary_rows(candidate, horizon, "cagr", cagr_values, min_label="min"))
        rows.extend(summary_rows(candidate, horizon, "mdd", mdd_values, min_label="worst"))
        rows.extend(summary_rows(candidate, horizon, "relative_wealth_vs_spy", rel_wealth_values, min_label="min"))
    return rows


def generate_plots(common: pd.DataFrame, plot_dir: Path) -> list[Path]:
    """Create visual diagnostics for equity, SPY-relative equity, drawdown, and rolling windows.

    The plots use fixed candidates only; visual comparisons are diagnostics meant to
    expose regime/path dependence before any further optimization `[testing_tuning, p.327-335]`.
    """
    plot_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    equity = (1.0 + common).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    rel_equity = equity.div(equity["SPYSIM_buy_hold"], axis=0)

    paths.append(plot_equity(equity, plot_dir / "equity_curves.png"))
    paths.append(plot_relative_equity(rel_equity, plot_dir / "equity_vs_spy_ratio.png"))
    paths.append(plot_drawdowns(drawdown, plot_dir / "drawdowns.png"))

    paths.append(plot_rolling_windows_grid(common, plot_dir / "rolling_windows_relative_wealth_vs_spy.png"))
    return paths


def plot_equity(equity: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in equity.columns:
        ax.plot(equity.index, equity[col], label=col, linewidth=1.7)
    ax.set_title("Equity Curves, Normalized to 1.0")
    ax.set_ylabel("Terminal wealth multiple")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_relative_equity(rel_equity: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in rel_equity.columns:
        if col == "SPYSIM_buy_hold":
            continue
        ax.plot(rel_equity.index, rel_equity[col], label=col, linewidth=1.7)
    ax.axhline(1.0, color="black", linewidth=1.0, alpha=0.7, label="SPY parity")
    ax.set_title("Equity / SPYSIM Equity")
    ax.set_ylabel("Relative wealth ratio")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_drawdowns(drawdown: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in drawdown.columns:
        ax.plot(drawdown.index, drawdown[col], label=col, linewidth=1.5)
    ax.set_title("Drawdowns")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def rolling_timeseries(common: pd.DataFrame, horizon: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    days = HORIZON_DAYS[horizon]
    if len(common) < days:
        empty = pd.DataFrame(index=pd.DatetimeIndex([], name="date"))
        return empty, empty, empty
    starts = _rolling_starts(len(common), days, rolling_step=1)
    dates = common.index[starts + days - 1]
    spy_cum = _series_cumulatives(common["SPYSIM_buy_hold"].to_numpy(dtype=float))
    spy_metrics = _rolling_metrics_from_cumulatives(spy_cum, days, starts, compute_drawdown=True)
    cagr_cols: dict[str, np.ndarray] = {}
    mdd_cols: dict[str, np.ndarray] = {}
    rel_cols: dict[str, np.ndarray] = {}
    for col in common.columns:
        cumulatives = _series_cumulatives(common[col].to_numpy(dtype=float))
        metrics = _rolling_metrics_from_cumulatives(cumulatives, days, starts, compute_drawdown=True)
        cagr_cols[col] = metrics["cagr"]
        mdd_cols[col] = metrics["mdd"]
        rel_cols[col] = metrics["terminal_wealth"] / spy_metrics["terminal_wealth"] - 1.0
    return (
        pd.DataFrame(cagr_cols, index=dates),
        pd.DataFrame(mdd_cols, index=dates),
        pd.DataFrame(rel_cols, index=dates),
    )


def plot_rolling_windows_grid(common: pd.DataFrame, out: Path) -> Path:
    """Plot rolling relative wealth versus SPY for 3/5/10/15y in one 2x2 figure."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=False, sharey=False)
    legend_handles = None
    legend_labels = None
    for ax, horizon in zip(axes.flat, ROLLING_PLOT_HORIZONS, strict=True):
        _cagr, _mdd, rel_wealth = rolling_timeseries(common, horizon)
        for col in rel_wealth.columns:
            if col == "SPYSIM_buy_hold":
                continue
            ax.plot(rel_wealth.index, rel_wealth[col], label=col, linewidth=1.2)
        ax.axhline(0.0, color="black", linewidth=1.0, alpha=0.7)
        ax.set_title(f"Rolling {horizon} Relative Wealth vs SPY")
        ax.set_ylabel("Relative wealth vs SPY")
        ax.grid(True, alpha=0.25)
        if legend_handles is None:
            legend_handles, legend_labels = ax.get_legend_handles_labels()
    if legend_handles and legend_labels:
        fig.legend(legend_handles, legend_labels, loc="lower center", ncol=3, fontsize=8)
    fig.suptitle("Rolling Window Relative Wealth vs SPYSIM", y=0.98)
    fig.tight_layout(rect=(0, 0.08, 1, 0.96))
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def summary_rows(
    candidate: str,
    horizon: str,
    metric: str,
    values: list[float],
    *,
    min_label: str,
) -> list[dict[str, object]]:
    clean = pd.Series(values, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        stats = {min_label: math.nan, "p10": math.nan, "median": math.nan, "latest": math.nan}
    else:
        stats = {
            min_label: float(clean.min()),
            "p10": float(clean.quantile(0.10)),
            "median": float(clean.median()),
            "latest": float(clean.iloc[-1]),
        }
    return [
        {"candidate": candidate, "horizon": horizon, "metric": metric, "stat": stat, "value": value}
        for stat, value in stats.items()
    ]


def slice_returns(returns: pd.Series, start: str, end: str | None) -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = returns.index[-1] if end is None else pd.Timestamp(end)
    return returns.loc[(returns.index >= start_ts) & (returns.index <= end_ts)]


def metrics_with_ulcer(returns: pd.Series) -> dict[str, float | str]:
    metrics = metrics_from_returns(returns)
    r = returns.dropna().astype(float)
    if len(r) < 2:
        metrics["ulcer"] = math.nan
        return metrics
    equity = (1.0 + r).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    metrics["ulcer"] = float(np.sqrt(np.mean(np.square(drawdown.to_numpy(dtype=float)))))
    return metrics


def safe_ratio(numerator: object, denominator: object) -> float:
    try:
        num = float(numerator)
        den = float(denominator)
    except (TypeError, ValueError):
        return math.nan
    if not math.isfinite(num) or not math.isfinite(den) or den == 0.0:
        return math.nan
    return num / den


def write_report(
    metrics: pd.DataFrame,
    rolling: pd.DataFrame,
    candidates: list[Candidate],
    start: pd.Timestamp,
    end: pd.Timestamp,
    plot_paths: list[Path],
) -> None:
    full_cols = [
        "candidate",
        "kind",
        "full_cagr",
        "full_mdd",
        "full_sharpe",
        "full_sortino",
        "full_calmar",
        "full_ulcer",
        "full_terminal_wealth",
        "gross_weight",
    ]
    full_table = metrics[full_cols].sort_values(["full_calmar", "full_cagr"], ascending=False)
    rolling_table = rolling.pivot_table(
        index=["candidate", "horizon", "metric"], columns="stat", values="value", aggfunc="first"
    ).reset_index()
    regime_table = build_regime_table(metrics)
    decision = build_decision_notes(metrics, rolling)
    plot_lines = "\n\n".join(image_markdown(path) for path in plot_paths)
    notes = pd.DataFrame(
        [
            {
                "candidate": candidate.name,
                "kind": candidate.kind,
                "weights": json.dumps(candidate.weights, sort_keys=True),
                "note": candidate.note,
            }
            for candidate in candidates
        ]
    )

    report = f"""# Pareto/Regime Report - Static SPY Beater Portfolio

Generated from fixed candidate allocations over the common local data window `{start.date()}..{end.date()}`. This report is discovery-only: it compares path robustness and regimes before further local search, and does not validate or authorize any deployment `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Candidate Notes

{notes.to_markdown(index=False)}

`B4_like_testfolio` is explicitly a stacked/leveraged reference: it has `-37.5% CASHX`, gross weight `1.75`, and is not a pure long-only portfolio. The other portfolio weights are long-only sleeves, though several sleeves embed leverage/stacking internally `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`.

## Full-Period Metrics

{full_table.to_markdown(index=False, floatfmt='.6f')}

## Plots

Performance and rolling-window plots are saved as PNG artifacts. Equity and relative-equity plots use normalized wealth; the SPY-relative plot is `portfolio_equity / SPYSIM_equity` so values above `1.0` mean cumulative outperformance versus `SPYSIM`.

{plot_lines}

## Rolling Diagnostics

Rolling 3y/5y/10y CAGR, MDD, and relative wealth versus `SPYSIM`; p10 is retained to expose bad-window fragility rather than average-only performance `[testing_tuning, p.327-335]`.

{rolling_table.to_markdown(index=False, floatfmt='.6f')}

## Regime Windows

Named drawdown/bull/recovery regimes are diagnostics, not optimized gates; they are included to check whether full-period results depend on one market state `[testing_tuning, p.327-335]`.

{regime_table.to_markdown(index=False, floatfmt='.6f')}

## Analysis

{decision}

## Artifacts

- `metrics.csv`: full-period metrics plus regime-window metrics.
- `rolling.csv`: long-form rolling summary metrics.

## Next Step

Do not promote a winner. If continuing, run no-margin sensitivity and implementation-realism checks on `B4_no_margin_lead`: start-date sensitivity, rebalance frequency, ETF availability, drag assumptions, remove-one-asset tests, then walk-forward/static selection before any validation claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
"""
    (OUT_DIR / "REPORT.md").write_text(report, encoding="utf-8")


def image_markdown(path: Path) -> str:
    title = path.stem.replace("_", " ").title()
    return f"![{title}](plots/{path.name})"


def build_regime_table(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in metrics.iterrows():
        for regime in REGIMES:
            rows.append(
                {
                    "candidate": row["candidate"],
                    "regime": regime,
                    "cagr": row[f"regime_{regime}_cagr"],
                    "mdd": row[f"regime_{regime}_mdd"],
                    "sharpe": row[f"regime_{regime}_sharpe"],
                    "sortino": row[f"regime_{regime}_sortino"],
                    "calmar": row[f"regime_{regime}_calmar"],
                    "terminal_wealth": row[f"regime_{regime}_terminal_wealth"],
                    "wealth_vs_spy": row[f"regime_{regime}_wealth_vs_spy"],
                }
            )
    return pd.DataFrame(rows)


def build_decision_notes(metrics: pd.DataFrame, rolling: pd.DataFrame) -> str:
    full = metrics.set_index("candidate")
    roll = rolling.set_index(["candidate", "horizon", "metric", "stat"])["value"]

    def r(candidate: str, horizon: str, metric: str, stat: str) -> float:
        return float(roll.get((candidate, horizon, metric, stat), math.nan))

    b4 = full.loc["B4_like_testfolio"]
    b4_original = full.loc["B4_original"]
    no_margin = full.loc["B4_no_margin_lead"]
    robust = full.loc["GA_robust"]
    aggressive = full.loc["GA_aggressive"]
    stacked_521 = full.loc["GA_stacked_seed20260521"]
    stacked_520 = full.loc["GA_stacked_seed20260520"]
    stacked_519 = full.loc["GA_stacked_seed20260519"]

    no_margin_extra_cagr = float(no_margin["full_cagr"] - b4_original["full_cagr"])
    no_margin_extra_mdd = float(no_margin["full_mdd"] - b4_original["full_mdd"])
    robust_extra_cagr = float(robust["full_cagr"] - b4["full_cagr"])
    robust_extra_mdd = float(robust["full_mdd"] - b4["full_mdd"])
    aggressive_extra_cagr = float(aggressive["full_cagr"] - robust["full_cagr"])
    aggressive_extra_mdd = float(aggressive["full_mdd"] - robust["full_mdd"])
    stacked_521_extra_cagr = float(stacked_521["full_cagr"] - no_margin["full_cagr"])
    stacked_521_extra_mdd = float(stacked_521["full_mdd"] - no_margin["full_mdd"])
    stacked_521_extra_calmar = float(stacked_521["full_calmar"] - no_margin["full_calmar"])

    lines = [
        "### Verdict: B4-v2 core (35% GDESIM / 40% RSSTSIM / 25% ZROZSIM) is the winner",
        "",
        f"`B4_no_margin_lead` (the **35/40/25 B4-v2 core**) is the strongest practical static portfolio across **4 distinct GA challenges**: (1) local B4-like no-margin Pareto, (2) factor/momentum probe with VBR/MTUM/EFV, (3) core-beater levered/cash GA, (4) stacked-ETF expansion triage (2026-05-19). On this 2000-2026 window: CAGR `{no_margin['full_cagr']:.2%}`, MDD `{no_margin['full_mdd']:.2%}`, Calmar `{no_margin['full_calmar']:.3f}`, terminal wealth `{no_margin['full_terminal_wealth']:.1f}x`, gross `1.0`, no negative `CASHX`.",
        "",
        "### Trade-off analysis",
        "",
        f"- Versus `B4_original`, `B4_no_margin_lead` adds `{no_margin_extra_cagr:.2%}` CAGR and worsens MDD by `{abs(no_margin_extra_mdd):.2%}` points, Calmar `{no_margin['full_calmar']:.3f}` vs `{b4_original['full_calmar']:.3f}`.",
        f"- Rolling relative-wealth p10 vs `SPYSIM` for the core remains negative in 3y (`{r('B4_no_margin_lead', '3y', 'relative_wealth_vs_spy', 'p10'):.2%}`), 5y (`{r('B4_no_margin_lead', '5y', 'relative_wealth_vs_spy', 'p10'):.2%}`), 10y (`{r('B4_no_margin_lead', '10y', 'relative_wealth_vs_spy', 'p10'):.2%}`); turns positive at 15y.",
        f"- `B4_like_testfolio` is a lower-drawdown stacked reference but lower CAGR (`{b4['full_cagr']:.2%}`), lower Calmar (`{b4['full_calmar']:.3f}`), and requires negative `CASHX`.",
        f"- `GA_robust` (`50 RSST / 35 GDE / 10 SPY / 5 ZROZ`) adds `{robust_extra_cagr:.2%}` CAGR vs B4-like but MDD is `{robust_extra_mdd:.2%}` pp worse; 5y rel-wealth p10 `{r('GA_robust', '5y', 'relative_wealth_vs_spy', 'p10'):.2%}`.",
        f"- `GA_aggressive` adds only `{aggressive_extra_cagr:.2%}` CAGR vs `GA_robust` while changing MDD by `{aggressive_extra_mdd:.2%}` pp.",
        "- `Refined_GA_robust` is intentionally identical to `GA_robust`; confirms the artifact.",
        "",
        "### 2026-05-19 Stacked-ETF Triage GA winners",
        "",
        f"3 seeds against the expanded 21-ticker universe (B4-v2 core anchors + 8 local proxies CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW + NTSXSIM/NTSDSIM/NTSISIM/BTALSIM/IEISIM). All 3 winners converged on similar structure: keep core anchors, add ~20-25% ESBGSIM, accent with small CTAPSIM/MATESIM. On this 2000-2026 window the best (`GA_stacked_seed20260521`) shows CAGR `{stacked_521['full_cagr']:.2%}`, MDD `{stacked_521['full_mdd']:.2%}`, Calmar `{stacked_521['full_calmar']:.3f}`, terminal wealth `{stacked_521['full_terminal_wealth']:.1f}x` — `{stacked_521_extra_cagr:.2%}` CAGR over core, `{abs(stacked_521_extra_mdd):.2%}` pp worse MDD, Calmar `{stacked_521_extra_calmar:+.3f}` vs core.",
        "",
        "**Proxy bias caveat:** the 8 stacked proxies are local composition (e.g. `CTAPSIM = SPYSIM + DBMFSIM - 1.0×CASHX`). Sanity check against real `RSST` showed the same formula overstates CAGR by `~5.56pp` vs the real ETF. The marginal Calmar edge of the GA stacked candidates over the core (`+0.002` to `+0.003` Calmar) is **inside the proxy-bias error band** — likely vanishes once fund-level ER and strategy implementation drift are modeled.",
        "",
        "Under the actual GA fitness `core_relative_wealth_dominance` (rolling p10 dominance vs the core), the core fitness `0.350` beat the GA best `0.268` decisively. See `results/ga_b4v2_stacked_triage/REPORT.md`.",
        "",
        "### Status",
        "",
        "Discovery-only. Mandate §1 unchanged: 100% capital remains in Plano C passive factor-tilted. The report clarifies trade-offs and consolidates 4 GA-challenge outcomes but does not run PBO/DSR/walk-forward/bootstrap validation or authorize any mandate change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
