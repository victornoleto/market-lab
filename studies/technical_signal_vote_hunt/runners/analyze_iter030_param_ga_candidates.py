"""Economic diagnostics for the iter030 parameter-GA candidates.

The GA is an economic-first exploration over the T3d-K2/iter030 lineage, not a
mandate pass. This report checks whether apparent Pareto improvements survive
rolling-window and crisis-regime diagnostics before treating them as candidates
for formal PBO/DSR validation `[advances_fin_ml, p.208-211]`,
`[leverage_for_the_long_run, p.5-7]`.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/iter030_param_ga"
TABLES_DIR = REPORT_DIR / "tables"
PLOTS_DIR = REPORT_DIR / "plots"

BASELINE = "iter030_baseline"
REGIMES = {
    "1990_1994_whipsaw": ("1990-01-01", "1994-12-31"),
    "2000_2002_bear": ("2000-01-01", "2002-12-31"),
    "2008_2009_gfc": ("2008-01-01", "2009-12-31"),
    "2010_2026_modern": ("2010-01-01", "2026-04-17"),
}
ROLLING_YEARS = (3, 5, 10, 15)


def main() -> int:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    candidates = pd.read_csv(TABLES_DIR / "top_candidates.csv")
    equity = pd.read_csv(TABLES_DIR / "top_equity_curves.csv", parse_dates=["date"]).set_index("date")
    returns = equity.pct_change().dropna(how="all")

    base = candidates[candidates["label"].eq(_ga_label_for_baseline())].iloc[0]
    strict_labels = _strict_pareto_labels(candidates, base)
    selected = [BASELINE] + [label for label in strict_labels if label in equity.columns]
    selected_equity = equity[selected].dropna(how="all")
    selected_returns = returns[selected].dropna(how="all")

    regime_rows = _regime_metrics(selected_equity)
    rolling_rows = _rolling_metrics(selected_equity)
    annual_rows = _annual_metrics(selected_returns)

    regime_rows.to_csv(TABLES_DIR / "candidate_regime_metrics.csv", index=False)
    rolling_rows.to_csv(TABLES_DIR / "candidate_rolling_metrics.csv", index=False)
    annual_rows.to_csv(TABLES_DIR / "candidate_annual_metrics.csv", index=False)

    _plot_relative(selected_equity, PLOTS_DIR / "pareto_relative_to_iter030.png")
    _plot_rolling_10y(selected_equity, PLOTS_DIR / "pareto_rolling_10y_cagr.png")
    _write_report(candidates, base, strict_labels, regime_rows, rolling_rows, annual_rows)
    print(f"wrote {REPORT_DIR / 'CANDIDATE_DIAGNOSTICS.md'}")
    return 0


def _ga_label_for_baseline() -> str:
    return "ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D60_w1.00_lrs1.20_g0.25_rv60_0.70"


def _strict_pareto_labels(candidates: pd.DataFrame, base: pd.Series) -> list[str]:
    strict = candidates[
        (candidates["cagr"] > float(base["cagr"]))
        & (candidates["sortino"] >= float(base["sortino"]))
        & (candidates["mdd"] >= float(base["mdd"]))
    ]
    return strict["label"].tolist()


def _regime_metrics(equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (start, end) in REGIMES.items():
        window = equity.loc[start:end].dropna(how="all")
        if len(window) < 2:
            continue
        for label in equity.columns:
            s = window[label].dropna()
            if len(s) < 2:
                continue
            years = (s.index[-1] - s.index[0]).days / 365.25
            cagr = (s.iloc[-1] / s.iloc[0]) ** (1.0 / years) - 1.0
            dd = s / s.cummax() - 1.0
            rows.append({"regime": name, "label": label, "cagr": cagr, "mdd": dd.min(), "end_mult": s.iloc[-1] / s.iloc[0]})
    return pd.DataFrame(rows)


def _rolling_metrics(equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in equity.columns:
        s = equity[label].dropna()
        for years in ROLLING_YEARS:
            days = years * 252
            cagr = (s / s.shift(days)) ** (1.0 / years) - 1.0
            cagr = cagr.dropna()
            rows.append(
                {
                    "label": label,
                    "window_years": years,
                    "count": int(cagr.count()),
                    "pct_positive": float((cagr > 0.0).mean()),
                    "min_cagr": float(cagr.min()),
                    "median_cagr": float(cagr.median()),
                    "p10_cagr": float(cagr.quantile(0.10)),
                }
            )
    return pd.DataFrame(rows)


def _annual_metrics(returns: pd.DataFrame) -> pd.DataFrame:
    annual = (1.0 + returns).resample("YE").prod() - 1.0
    rows = []
    for label in annual.columns:
        s = annual[label].dropna()
        rows.append(
            {
                "label": label,
                "years": int(s.count()),
                "positive_years_pct": float((s > 0.0).mean()),
                "min_year": int(s.idxmin().year),
                "min_return": float(s.min()),
                "median_return": float(s.median()),
            }
        )
    return pd.DataFrame(rows)


def _plot_relative(equity: pd.DataFrame, path: Path) -> None:
    rel = equity.div(equity[BASELINE], axis=0)
    fig, ax = plt.subplots(figsize=(13, 7))
    rel.drop(columns=[BASELINE]).plot(ax=ax, logy=True, linewidth=1.4)
    ax.axhline(1.0, color="black", linewidth=0.8, alpha=0.6)
    ax.set_title("Strict Pareto Candidates Relative to iter030")
    ax.set_ylabel("Relative equity")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_rolling_10y(equity: pd.DataFrame, path: Path) -> None:
    rolling = (equity / equity.shift(10 * 252)) ** 0.1 - 1.0
    fig, ax = plt.subplots(figsize=(13, 7))
    rolling.plot(ax=ax, linewidth=1.2)
    ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.6)
    ax.set_title("10-Year Rolling CAGR")
    ax.set_ylabel("CAGR")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(
    candidates: pd.DataFrame,
    base: pd.Series,
    strict_labels: list[str],
    regime_rows: pd.DataFrame,
    rolling_rows: pd.DataFrame,
    annual_rows: pd.DataFrame,
) -> None:
    strict = candidates[candidates["label"].isin(strict_labels)].copy()
    strict["delta_cagr"] = strict["cagr"] - float(base["cagr"])
    strict["delta_sortino"] = strict["sortino"] - float(base["sortino"])
    strict["delta_mdd"] = strict["mdd"] - float(base["mdd"])

    rolling_pivot = rolling_rows.pivot(index="label", columns="window_years", values="min_cagr").reset_index()
    rolling_pivot.columns = ["label"] + [f"min_{int(c)}y_cagr" for c in rolling_pivot.columns[1:]]
    annual_compact = annual_rows[["label", "positive_years_pct", "min_year", "min_return", "median_return"]]

    lines = [
        "# Iter030 Parameter GA Candidate Diagnostics",
        "",
        "Status: economic-first diagnostics for the strict Pareto candidates from the small GA run.",
        "",
        "## Verdict",
        "",
        "The best GA candidate is an economic improvement over iter030 on full-period CAGR and terminal equity, but the evidence is not yet robust enough to replace the baseline.",
        "The main reason is that the improvement is a narrow mutation of the same mechanism (`T35D60` to longer `D120`, sometimes lower LRS/TQQQ weight), found after optimization on the same full history; it still requires formal OOS/WF/bootstrap/PBO/DSR validation before any mandate claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
        "",
        "## Strict Pareto Set",
        "",
        strict[["label", "cagr", "sortino", "mdd", "calmar", "end_mult", "delta_cagr", "delta_sortino", "delta_mdd", "t_crash", "d_arm", "tqqq_weight", "lrs_factor", "vol_threshold"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Min CAGR",
        "",
        rolling_pivot.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Annual Diagnostics",
        "",
        annual_compact.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Regime Metrics",
        "",
        regime_rows.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plots",
        "",
        "![Pareto relative to iter030](plots/pareto_relative_to_iter030.png)",
        "",
        "![10-year rolling CAGR](plots/pareto_rolling_10y_cagr.png)",
        "",
        "## Next Validation",
        "",
        "- Treat `ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70` as the primary candidate, not a winner.",
        "- Run a locked-candidate validation over OOS/FWD/WF/bootstrap and then PBO/DSR with cumulative trial accounting before promoting any conclusion.",
        "- If the candidate only wins because of `D120`, prefer an explicit local sensitivity table around `T{20,35,45}D{60,90,120}` before expanding the GA.",
    ]
    (REPORT_DIR / "CANDIDATE_DIAGNOSTICS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
