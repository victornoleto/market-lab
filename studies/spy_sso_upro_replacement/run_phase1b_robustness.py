from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from run_static_grid import (
    ASSETS,
    BATCH_SIZE,
    CAGR_SPREAD_TOLERANCE,
    EXACT_REBALANCE_FREQS,
    HIT_TOLERANCE,
    HORIZONS_YEARS,
    RESULTS,
    TRADING_DAYS,
    exact_evaluate,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    md_table,
    metrics_from_returns,
    rebalanced_returns,
    rolling_relative_stats,
    triage_grid,
    weight_label,
)


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "PHASE1B_REPORT.md"

FINE_UNITS = 100
DRAG_BPS = [0, 10, 25, 50, 100]
ROLLING_DRAWDOWN_HORIZONS = [3, 5, 10]
ROLLING_DRAWDOWN_STEP_DAYS = 21

LEAD_WEIGHTS = {
    "SPYSIM": 0.80,
    "SSOSIM": 0.05,
    "UPROSIM": 0.05,
    "ZROZSIM": 0.05,
    "GLDSIM": 0.05,
}


def fine_weight_label(weights: dict[str, float]) -> str:
    parts = []
    for asset in ASSETS:
        weight = weights.get(asset, 0.0)
        if weight > 0.0:
            parts.append(f"{weight * 100:.0f} {asset.replace('SIM', '')}")
    return " / ".join(parts)


def fine_weights_key(weights: dict[str, float]) -> tuple[int, ...]:
    return tuple(int(round(weights.get(asset, 0.0) * FINE_UNITS)) for asset in ASSETS)


def weights_from_summary_row(row: pd.Series) -> dict[str, float]:
    return {asset: float(row[f"w_{asset}"]) for asset in ASSETS if float(row[f"w_{asset}"]) > 0.0}


def generate_fine_local_grid() -> np.ndarray:
    """Generate a 1% local static grid around the Phase 1 lead.

    The local bounds keep the search focused on modest embedded S&P leverage and
    implementation sensitivity rather than another broad optimizer
    `[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.13]`.
    """

    rows: list[list[float]] = []
    base_units = np.array([80, 5, 5, 5, 5, 0, 0], dtype=np.int64)

    for spy in range(65, 91):
        for sso in range(0, 26):
            for upro in range(0, 21):
                return_units = spy + sso + upro
                if not 75 <= return_units <= 95:
                    continue

                effective_sp = spy + 2 * sso + 3 * upro
                if not 100 <= effective_sp <= 125:
                    continue

                diversifier_total = 100 - return_units
                if not 5 <= diversifier_total <= 25:
                    continue

                for zroz in range(0, min(20, diversifier_total) + 1):
                    for gld in range(0, min(20, diversifier_total - zroz) + 1):
                        if zroz + gld < 5:
                            continue
                        max_ief = min(10, diversifier_total - zroz - gld)
                        for ief in range(max_ief + 1):
                            cash = diversifier_total - zroz - gld - ief
                            if not 0 <= cash <= 5:
                                continue

                            units = np.array([spy, sso, upro, zroz, gld, ief, cash], dtype=np.int64)
                            if np.abs(units - base_units).sum() > 40:
                                continue
                            rows.append((units / FINE_UNITS).tolist())

    return np.array(rows, dtype=np.float64)


def select_fine_finalists(summary: pd.DataFrame, max_finalists: int = 420) -> dict[str, dict[str, float]]:
    buckets = [
        summary[summary["preferred_pass_monthly"]].head(220),
        summary.sort_values("monthly_score", ascending=False).head(260),
        summary.sort_values("min_hit_10p_monthly", ascending=False).head(180),
        summary.sort_values("min_p10_10p_monthly", ascending=False).head(180),
        summary.sort_values("cagr_monthly", ascending=False).head(140),
    ]
    finalists: dict[tuple[int, ...], dict[str, float]] = {}
    finalists[fine_weights_key(LEAD_WEIGHTS)] = LEAD_WEIGHTS
    for bucket in buckets:
        for _, row in bucket.iterrows():
            weights = weights_from_summary_row(row)
            key = fine_weights_key(weights)
            finalists.setdefault(key, weights)
            if len(finalists) >= max_finalists:
                break
        if len(finalists) >= max_finalists:
            break
    return {fine_weight_label(weights): weights for weights in finalists.values()}


def portfolio_return_with_annual_drag(returns: pd.Series, annual_drag_bps: int) -> pd.Series:
    if annual_drag_bps == 0:
        return returns.copy()
    daily_multiplier = (1.0 - annual_drag_bps / 10_000.0) ** (1.0 / TRADING_DAYS)
    return (1.0 + returns) * daily_multiplier - 1.0


def drag_stress_rows(daily_returns: pd.DataFrame, exact: pd.DataFrame, limit: int | None = None) -> pd.DataFrame:
    spy_returns = daily_returns["SPYSIM"]
    spy_metrics = metrics_from_returns(spy_returns)
    selected = exact.copy() if limit is None else exact.head(limit).copy()
    rows: list[dict[str, float | str | bool | int]] = []
    seen: set[tuple[str, str]] = set()
    for _, candidate in selected.iterrows():
        key = (str(candidate["name"]), str(candidate["rebalance"]))
        if key in seen:
            continue
        seen.add(key)
        weights = {asset: float(candidate[f"w_{asset}"]) for asset in ASSETS if float(candidate[f"w_{asset}"]) > 0.0}
        freq = EXACT_REBALANCE_FREQS[str(candidate["rebalance"])]
        gross_returns = rebalanced_returns(daily_returns, weights, freq)
        for drag_bps in DRAG_BPS:
            returns = portfolio_return_with_annual_drag(gross_returns, drag_bps)
            metrics = metrics_from_returns(returns)
            rolling = rolling_relative_stats(returns, spy_returns)
            min_hit_10p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 10)
            min_hit_5p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 5)
            min_p10_10p = min(rolling.get(f"p10_{h}y", 999.0) for h in HORIZONS_YEARS if h >= 10)
            cagr_spread = metrics.cagr - spy_metrics.cagr
            mdd_spread = metrics.mdd - spy_metrics.mdd
            preferred_pass = cagr_spread > CAGR_SPREAD_TOLERANCE and min_hit_10p >= 0.90 and (mdd_spread >= -0.05 or metrics.mdd >= -0.60)
            strict_pass = cagr_spread > CAGR_SPREAD_TOLERANCE and min_hit_5p >= 0.90 and mdd_spread >= 0.0
            rows.append(
                {
                    "name": candidate["name"],
                    "rebalance": candidate["rebalance"],
                    "weights": candidate["weights"],
                    "annual_drag_bps": drag_bps,
                    "preferred_pass": preferred_pass,
                    "strict_pass": strict_pass,
                    "cagr": metrics.cagr,
                    "cagr_spread": cagr_spread,
                    "mdd": metrics.mdd,
                    "mdd_spread": mdd_spread,
                    "min_hit_10p": min_hit_10p,
                    "min_hit_5p": min_hit_5p,
                    "min_p10_10p": min_p10_10p,
                    "terminal_vs_spy": metrics.terminal / spy_metrics.terminal,
                }
            )
    return pd.DataFrame(rows)


def rolling_window_mdd(returns: pd.Series, years: int) -> pd.Series:
    clean = returns.dropna().astype(float)
    window = years * TRADING_DAYS
    values: list[float] = []
    dates: list[pd.Timestamp] = []
    if len(clean) <= window:
        return pd.Series(dtype=float)
    for end in range(window, len(clean) + 1, ROLLING_DRAWDOWN_STEP_DAYS):
        subset = clean.iloc[end - window : end]
        equity = (1.0 + subset).cumprod()
        values.append(float((equity / equity.cummax() - 1.0).min()))
        dates.append(clean.index[end - 1])
    return pd.Series(values, index=pd.DatetimeIndex(dates), name=f"rolling_mdd_{years}y")


def rolling_drawdown_rows(daily_returns: pd.DataFrame, exact: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    spy_returns = daily_returns["SPYSIM"]
    selected = exact.head(limit).copy()
    rows: list[dict[str, float | str | int]] = []
    for _, candidate in selected.iterrows():
        weights = {asset: float(candidate[f"w_{asset}"]) for asset in ASSETS if float(candidate[f"w_{asset}"]) > 0.0}
        freq = EXACT_REBALANCE_FREQS[str(candidate["rebalance"])]
        returns = rebalanced_returns(daily_returns, weights, freq)
        for horizon in ROLLING_DRAWDOWN_HORIZONS:
            port_mdd = rolling_window_mdd(returns, horizon)
            spy_mdd = rolling_window_mdd(spy_returns, horizon)
            aligned = pd.concat({"portfolio": port_mdd, "spy": spy_mdd}, axis=1).dropna()
            if aligned.empty:
                continue
            spread = aligned["portfolio"] - aligned["spy"]
            rows.append(
                {
                    "name": candidate["name"],
                    "rebalance": candidate["rebalance"],
                    "weights": candidate["weights"],
                    "horizon_years": horizon,
                    "windows": int(len(aligned)),
                    "worst_mdd": float(aligned["portfolio"].min()),
                    "p10_mdd": float(aligned["portfolio"].quantile(0.10)),
                    "median_mdd": float(aligned["portfolio"].quantile(0.50)),
                    "latest_mdd": float(aligned["portfolio"].iloc[-1]),
                    "spy_worst_mdd": float(aligned["spy"].min()),
                    "worst_mdd_spread": float(spread.min()),
                    "median_mdd_spread": float(spread.quantile(0.50)),
                    "latest_mdd_spread": float(spread.iloc[-1]),
                    "pct_worse_than_spy_by_5pp": float((spread < -0.05).mean()),
                }
            )
    return pd.DataFrame(rows)


def formatted_drag_rows(frame: pd.DataFrame, limit: int = 40) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Rebal": row["rebalance"],
                "Drag": f"{int(row['annual_drag_bps'])} bps/yr",
                "CAGR": fmt_pct(row["cagr"]),
                "Spread": fmt_pp(row["cagr_spread"]),
                "MDD": fmt_pct(row["mdd"]),
                "MDD vs SPY": fmt_pp(row["mdd_spread"]),
                "10y+ hit min": fmt_pct(row["min_hit_10p"], 1),
                "5y+ hit min": fmt_pct(row["min_hit_5p"], 1),
                "10y+ p10 min": fmt_pct(row["min_p10_10p"], 1),
                "Terminal/SPY": fmt_x(row["terminal_vs_spy"]),
                "Preferred": "yes" if row["preferred_pass"] else "no",
                "Strict": "yes" if row["strict_pass"] else "no",
            }
        )
    return rows


def formatted_drawdown_rows(frame: pd.DataFrame, limit: int = 40) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Rebal": row["rebalance"],
                "Horizon": f"{int(row['horizon_years'])}y",
                "Worst MDD": fmt_pct(row["worst_mdd"]),
                "SPY Worst": fmt_pct(row["spy_worst_mdd"]),
                "Worst Spread": fmt_pp(row["worst_mdd_spread"]),
                "Median Spread": fmt_pp(row["median_mdd_spread"]),
                "Latest Spread": fmt_pp(row["latest_mdd_spread"]),
                "Worse >5pp": fmt_pct(row["pct_worse_than_spy_by_5pp"], 1),
            }
        )
    return rows


def formatted_exact_rows(frame: pd.DataFrame, limit: int = 20) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Rebal": row["rebalance"],
                "Weights": row["weights"],
                "CAGR": fmt_pct(row["cagr"]),
                "Spread": fmt_pp(row["cagr_spread"]),
                "MDD": fmt_pct(row["mdd"]),
                "MDD vs SPY": fmt_pp(row["mdd_spread"]),
                "10y+ hit min": fmt_pct(row["min_hit_10p"], 1),
                "5y+ hit min": fmt_pct(row["min_hit_5p"], 1),
                "10y+ p10 min": fmt_pct(row["min_p10_10p"], 1),
                "Terminal/SPY": fmt_x(row["terminal_vs_spy"]),
                "Preferred": "yes" if row["preferred_pass"] else "no",
                "Strict": "yes" if row["strict_pass"] else "no",
            }
        )
    return rows


def write_report(
    summary: pd.DataFrame,
    exact: pd.DataFrame,
    drag: pd.DataFrame,
    drawdown: pd.DataFrame,
    daily_returns: pd.DataFrame,
) -> None:
    spy_metrics = metrics_from_returns(daily_returns["SPYSIM"])
    exact_preferred = exact[exact["preferred_pass"]]
    exact_strict = exact[exact["strict_pass"]]
    monthly_preferred = summary[summary["preferred_pass_monthly"]]
    best = exact.iloc[0]
    best_preferred = exact_preferred.iloc[0] if not exact_preferred.empty else None
    drag_preferred = drag[drag["preferred_pass"]]
    drag_10_preferred = drag[(drag["annual_drag_bps"] == 10) & (drag["preferred_pass"])]
    drag_25_preferred = drag[(drag["annual_drag_bps"] == 25) & (drag["preferred_pass"])]
    drag_50_preferred = drag[(drag["annual_drag_bps"] == 50) & (drag["preferred_pass"])]
    drag_display_names = set(exact.head(8)["name"])
    drag_display = drag[drag["name"].isin(drag_display_names)].sort_values(["name", "rebalance", "annual_drag_bps"])

    if best_preferred is None:
        conclusion = "Phase 1b did not find a preferred-target candidate in the fine local grid. "
    elif exact_strict.empty:
        conclusion = "Phase 1b improved the local static search but still did not solve the strict 5y+ target. "
    else:
        conclusion = "Phase 1b found at least one strict 5y+ candidate, requiring independent validation before any promotion. "
    conclusion += (
        f"The top exact row is `{best['weights']}` with `{best['rebalance']}` rebalance: CAGR {fmt_pct(best['cagr'])}, "
        f"MDD {fmt_pct(best['mdd'])}, minimum 10y+ hit rate {fmt_pct(best['min_hit_10p'], 1)}, "
        f"minimum 5y+ hit rate {fmt_pct(best['min_hit_5p'], 1)} and terminal wealth {fmt_x(best['terminal_vs_spy'])} versus SPY."
    )

    sections = [
        "# SPY/SSO/UPRO Replacement - Phase 1b Robustness Report\n\n"
        "Status: research-only focused robustness. This report does not authorize deployment, paper trading or mandate changes.\n\n"
        "Method references: fine-grid parameter sensitivity, implementation drag and rolling-window diagnostics are robustness checks, not proof of future performance `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. LETF exposure remains an embedded-leverage caveat `[leverage_for_the_long_run, p.13]`.\n\n"
        "## Executive Conclusion\n\n"
        f"{conclusion}\n\n"
        "Practical conclusion: treat the static branch as a robust near-miss if it keeps preferred 10y+ behavior under reasonable drag, but do not claim near-always SPY replacement unless 5y+ rolling behavior improves materially.\n\n"
        "## Source Data\n\n"
        "| Item | Value |\n|---|---|\n"
        f"| Testfol.io cache | `data/testfolio/cache/history.parquet` |\n"
        f"| Daily common window | `{daily_returns.index[0].date()}` to `{daily_returns.index[-1].date()}` |\n"
        f"| Assets | `{', '.join(ASSETS)}` |\n"
        f"| SPY baseline | CAGR {fmt_pct(spy_metrics.cagr)}, MDD {fmt_pct(spy_metrics.mdd)}, Sharpe {fmt_num(spy_metrics.sharpe)} |\n"
        f"| Fine local grid rows | `{len(summary):,}` |\n"
        f"| Monthly fine-grid preferred rows | `{len(monthly_preferred):,}` |\n"
        f"| Exact finalist rows | `{len(exact):,}` including cadence variants |\n"
        f"| Exact preferred rows | `{len(exact_preferred):,}` |\n"
        f"| Exact strict rows | `{len(exact_strict):,}` |\n"
        f"| Drag stress rows | `{len(drag):,}` |\n"
        f"| Drag preferred rows | `{len(drag_preferred):,}` total; `{len(drag_10_preferred):,}` at 10 bps; `{len(drag_25_preferred):,}` at 25 bps; `{len(drag_50_preferred):,}` at 50 bps |\n\n"
    ]

    sections.append(
        "## Top Fine-Grid Exact Finalists\n\n"
        "Analysis: These portfolios were found by 1% local-grid monthly triage and recomputed with daily exact monthly/quarterly/annual rebalancing. `Strict=yes` requires the 5y+ hit-rate target and no worse MDD than SPY.\n\n"
        + (
            "Conclusion: The focused static family still fails strict 5y+ robustness; any viable static interpretation remains a 10y+ preferred-target result only.\n\n"
            if exact_strict.empty
            else "Conclusion: Strict candidates appeared in Phase 1b, but they are still same-family optimized candidates and need out-of-family validation.\n\n"
        )
        + md_table(
            formatted_exact_rows(exact, 25),
            ["Name", "Rebal", "Weights", "CAGR", "Spread", "MDD", "MDD vs SPY", "10y+ hit min", "5y+ hit min", "10y+ p10 min", "Terminal/SPY", "Preferred", "Strict"],
        )
    )

    sections.append(
        "## Drag Stress\n\n"
        "Analysis: Drag is applied to candidate portfolio returns only, not to SPY, so this is a conservative implementation haircut. The stress is generic bps/year drag rather than a claim about exact ETF expense ratios.\n\n"
        "Conclusion: Candidates that only barely clear the 10y+ target under zero drag should not be promoted; survival at 25-50 bps is the minimum practical robustness signal. Counts above stress every exact preferred finalist; the table below shows the leading names only.\n\n"
        + md_table(
            formatted_drag_rows(drag_display, 60),
            ["Name", "Rebal", "Drag", "CAGR", "Spread", "MDD", "MDD vs SPY", "10y+ hit min", "5y+ hit min", "10y+ p10 min", "Terminal/SPY", "Preferred", "Strict"],
        )
    )

    sections.append(
        "## Rolling Drawdown Diagnostics\n\n"
        "Analysis: This table computes 3y/5y/10y rolling within-window max drawdowns at roughly monthly steps. `Worst Spread` is portfolio rolling MDD minus SPY rolling MDD; negative values mean the candidate was worse.\n\n"
        "Conclusion: Full-period MDD near SPY can hide rolling windows where the static LETF mix is meaningfully worse, especially around rate shocks and early-crash timing.\n\n"
        + md_table(
            formatted_drawdown_rows(drawdown.sort_values(["name", "rebalance", "horizon_years"]), 60),
            ["Name", "Rebal", "Horizon", "Worst MDD", "SPY Worst", "Worst Spread", "Median Spread", "Latest Spread", "Worse >5pp"],
        )
    )

    sections.append(
        "## Phase 1b Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did finer 1% weights preserve preferred 10y+ candidates? | {'Yes' if not exact_preferred.empty else 'No'}. |\n"
        f"| Did Phase 1b solve strict 5y+ 90% hit with no worse MDD than SPY? | {'Yes' if not exact_strict.empty else 'No'}. |\n"
        f"| Did any stressed row pass preferred at 10 bps/year drag? | {'Yes' if not drag_10_preferred.empty else 'No'}. |\n"
        f"| Did any stressed row pass preferred at 25 bps/year drag? | {'Yes' if not drag_25_preferred.empty else 'No'}. |\n"
        f"| Did any stressed row pass preferred at 50 bps/year drag? | {'Yes' if not drag_50_preferred.empty else 'No'}. |\n"
        "| Is this deployment-ready? | No. It remains research-only under maintenance mode. |\n\n"
        "Recommended next step: if the user still wants a near-always SPY replacement, move to Phase 2 low-turnover tactical/LRS overlay; otherwise keep the static result as a simple 10y+ near-miss reference.\n"
    )

    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = load_testfolio_frame()
    daily_prices = frame[ASSETS].dropna()
    daily_returns = daily_prices.pct_change().dropna()
    monthly_prices = daily_prices.resample("ME").last().dropna()
    monthly_returns = monthly_prices.pct_change().dropna()

    grid = generate_fine_local_grid()
    summary = triage_grid(monthly_returns, grid)
    summary.to_csv(RESULTS / "phase1b_fine_local_summary.csv", index=False)

    finalists = select_fine_finalists(summary)
    exact, _regimes = exact_evaluate(daily_returns, finalists)
    exact.to_csv(RESULTS / "phase1b_exact_finalists.csv", index=False)

    drag_source = exact[exact["preferred_pass"]]
    if drag_source.empty:
        drag_source = exact.head(40)
    drag = drag_stress_rows(daily_returns, drag_source)
    drag.to_csv(RESULTS / "phase1b_drag_stress.csv", index=False)

    drawdown = rolling_drawdown_rows(daily_returns, exact)
    drawdown.to_csv(RESULTS / "phase1b_rolling_drawdown.csv", index=False)

    write_report(summary, exact, drag, drawdown, daily_returns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
