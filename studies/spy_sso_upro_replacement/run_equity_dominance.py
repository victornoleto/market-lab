from __future__ import annotations

from pathlib import Path

import math

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from run_static_grid import (
    ASSETS,
    CAGR_SPREAD_TOLERANCE,
    EXACT_REBALANCE_FREQS,
    HIT_TOLERANCE,
    HORIZONS_YEARS,
    RESULTS,
    TRADING_DAYS,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    md_table,
    metrics_from_returns,
    rebalanced_returns,
    rolling_relative_stats,
)


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "EQUITY_DOMINANCE_REPORT.md"

TARGET_LEVERAGES = [1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]
STATIC_EQUITY_ALLOCATIONS = [0.60, 0.70, 0.80, 0.90, 1.00]
TACTICAL_LOOKBACKS = [100, 150, 200, 250, 300]
TACTICAL_UPDATE_MODES = ["daily", "monthly"]

DIVERSIFIER_BASKETS: dict[str, dict[str, float]] = {
    "none": {},
    "ZROZ": {"ZROZSIM": 1.00},
    "GLD": {"GLDSIM": 1.00},
    "IEF": {"IEFSIM": 1.00},
    "CASH": {"CASHX": 1.00},
    "50 ZROZ / 50 GLD": {"ZROZSIM": 0.50, "GLDSIM": 0.50},
    "50 ZROZ / 50 IEF": {"ZROZSIM": 0.50, "IEFSIM": 0.50},
    "50 GLD / 50 IEF": {"GLDSIM": 0.50, "IEFSIM": 0.50},
    "60 ZROZ / 40 GLD": {"ZROZSIM": 0.60, "GLDSIM": 0.40},
    "40 ZROZ / 40 GLD / 20 IEF": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20},
    "50 ZROZ / 25 GLD / 25 CASH": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25},
}


def target_leverage_weights(target_leverage: float, equity_allocation: float = 1.0) -> dict[str, float]:
    """Map target leverage to adjacent ETF sleeves only.

    This avoids optimizing redundant free mixes of SPY/SSO/UPRO while preserving
    the economic levered-equity ladder `[leverage_for_the_long_run, p.13]`.
    """

    if target_leverage < 1.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")

    if target_leverage <= 2.0:
        spy = 2.0 - target_leverage
        sso = target_leverage - 1.0
        weights = {"SPYSIM": spy, "SSOSIM": sso}
    else:
        sso = 3.0 - target_leverage
        upro = target_leverage - 2.0
        weights = {"SSOSIM": sso, "UPROSIM": upro}

    return {asset: weight * equity_allocation for asset, weight in weights.items() if weight > 0.0}


def combine_weights(
    target_leverage: float,
    equity_allocation: float,
    diversifier_basket: dict[str, float],
) -> dict[str, float]:
    weights = target_leverage_weights(target_leverage, equity_allocation)
    diversifier_allocation = 1.0 - equity_allocation
    if diversifier_allocation > 0.0:
        for asset, basket_weight in diversifier_basket.items():
            weights[asset] = weights.get(asset, 0.0) + diversifier_allocation * basket_weight
    return {asset: weight for asset, weight in weights.items() if weight > 0.0}


def weight_label(weights: dict[str, float]) -> str:
    return " / ".join(f"{weight * 100:.0f} {asset.replace('SIM', '')}" for asset, weight in weights.items() if weight > 0.0)


def sleeve_returns(daily_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    aligned = daily_returns[list(weights)].dropna()
    target = np.array([weights[col] for col in aligned.columns], dtype=np.float64)
    out = pd.Series(aligned.to_numpy(dtype=np.float64) @ target, index=aligned.index, name="portfolio")
    return out


def tactical_returns(
    daily_returns: pd.DataFrame,
    spy_prices: pd.Series,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    lookback: int,
    update_mode: str,
) -> tuple[pd.Series, float, int]:
    risk_on = sleeve_returns(daily_returns, target_leverage_weights(target_leverage, 1.0))
    risk_off = sleeve_returns(daily_returns, risk_off_weights)
    sma = spy_prices.rolling(lookback).mean()
    signal = (spy_prices.shift(1) > sma.shift(1)).reindex(daily_returns.index).fillna(False)
    if update_mode == "monthly":
        period = signal.index.to_period("M")
        signal = signal.groupby(period).transform("first").astype(bool)
    elif update_mode != "daily":
        raise ValueError(f"unknown update mode: {update_mode}")

    aligned = pd.concat({"risk_on": risk_on, "risk_off": risk_off, "signal": signal.astype(float)}, axis=1).dropna()
    returns = aligned["signal"] * aligned["risk_on"] + (1.0 - aligned["signal"]) * aligned["risk_off"]
    states = aligned["signal"].astype(int)
    state_changes = int(states.diff().abs().fillna(0).sum())
    pct_risk_on = float(states.mean())
    returns.name = "portfolio"
    return returns, pct_risk_on, state_changes


def first_sustained_above_date(relative_equity: pd.Series) -> str:
    above_from_here = (relative_equity >= 1.0 - HIT_TOLERANCE)[::-1].cummin()[::-1]
    candidates = above_from_here[above_from_here]
    if candidates.empty:
        return "never"
    return str(candidates.index[0].date())


def after_years(relative_equity: pd.Series, years: int) -> pd.Series:
    offset = years * TRADING_DAYS
    if len(relative_equity) <= offset:
        return relative_equity.iloc[0:0]
    return relative_equity.iloc[offset:]


def evaluate_candidate(
    returns: pd.Series,
    spy_returns: pd.Series,
    candidate: dict[str, object],
) -> dict[str, object]:
    aligned = pd.concat({"portfolio": returns, "spy": spy_returns}, axis=1).dropna()
    portfolio_returns = aligned["portfolio"]
    benchmark_returns = aligned["spy"]
    metrics = metrics_from_returns(portfolio_returns)
    spy_metrics = metrics_from_returns(benchmark_returns)
    rolling = rolling_relative_stats(portfolio_returns, benchmark_returns)

    peq = (1.0 + portfolio_returns).cumprod()
    seq = (1.0 + benchmark_returns).cumprod()
    relative = peq / seq
    relative_drawdown = relative / relative.cummax() - 1.0
    rel_after_5y = after_years(relative, 5)
    rel_after_10y = after_years(relative, 10)
    rel_after_20y = after_years(relative, 20)

    min_hit_5p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 5)
    min_hit_10p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 10)
    min_p10_10p = min(rolling.get(f"p10_{h}y", 999.0) for h in HORIZONS_YEARS if h >= 10)
    cagr_spread = metrics.cagr - spy_metrics.cagr
    mdd_spread = metrics.mdd - spy_metrics.mdd

    min_rel_after_10y = float(rel_after_10y.min()) if not rel_after_10y.empty else math.nan
    pct_above_after_10y = float((rel_after_10y >= 1.0 - HIT_TOLERANCE).mean()) if not rel_after_10y.empty else math.nan
    terminal_vs_spy = float(relative.iloc[-1])
    dominance_pass = terminal_vs_spy > 1.0 and min_hit_10p >= 0.90 and min_rel_after_10y >= 1.0
    strict_full_dominance = bool(terminal_vs_spy > 1.0 + CAGR_SPREAD_TOLERANCE and float(relative.min()) >= 1.0 - HIT_TOLERANCE)

    score = (
        2.0 * math.log(max(terminal_vs_spy, 1e-9))
        + 1.5 * min_hit_10p
        + 1.0 * pct_above_after_10y
        + 0.75 * min(0.0, math.log(max(min_rel_after_10y, 1e-9)))
        + 8.0 * cagr_spread
        + 0.25 * min_p10_10p
    )

    row: dict[str, object] = {
        **candidate,
        "dominance_pass": dominance_pass,
        "strict_full_dominance": strict_full_dominance,
        "score": score,
        "start": metrics.start,
        "end": metrics.end,
        "years": metrics.years,
        "cagr": metrics.cagr,
        "spy_cagr": spy_metrics.cagr,
        "cagr_spread": cagr_spread,
        "mdd": metrics.mdd,
        "spy_mdd": spy_metrics.mdd,
        "mdd_spread": mdd_spread,
        "sharpe": metrics.sharpe,
        "sortino": metrics.sortino,
        "calmar": metrics.calmar,
        "terminal_vs_spy": terminal_vs_spy,
        "pct_time_above_spy": float((relative >= 1.0 - HIT_TOLERANCE).mean()),
        "min_relative_equity": float(relative.min()),
        "min_relative_after_5y": float(rel_after_5y.min()) if not rel_after_5y.empty else math.nan,
        "min_relative_after_10y": min_rel_after_10y,
        "min_relative_after_20y": float(rel_after_20y.min()) if not rel_after_20y.empty else math.nan,
        "pct_above_after_10y": pct_above_after_10y,
        "worst_relative_drawdown": float(relative_drawdown.min()),
        "latest_relative_equity": terminal_vs_spy,
        "first_sustained_above_date": first_sustained_above_date(relative),
        "min_hit_5p": min_hit_5p,
        "min_hit_10p": min_hit_10p,
        "min_p10_10p": min_p10_10p,
    }
    row.update(rolling)
    return row


def generate_static_candidates(daily_returns: pd.DataFrame, spy_returns: pd.Series) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_leverage in TARGET_LEVERAGES:
        for equity_allocation in STATIC_EQUITY_ALLOCATIONS:
            diversifier_allocation = 1.0 - equity_allocation
            for basket_name, basket in DIVERSIFIER_BASKETS.items():
                if diversifier_allocation == 0.0 and basket_name != "none":
                    continue
                if diversifier_allocation > 0.0 and basket_name == "none":
                    continue
                weights = combine_weights(target_leverage, equity_allocation, basket)
                for rebalance_name, freq in EXACT_REBALANCE_FREQS.items():
                    returns = rebalanced_returns(daily_returns, weights, freq)
                    candidate = {
                        "family": "static_target_leverage",
                        "name": f"static L{target_leverage:.2f} E{equity_allocation:.0%} {basket_name} {rebalance_name}",
                        "target_leverage": target_leverage,
                        "equity_allocation": equity_allocation,
                        "diversifier_basket": basket_name,
                        "rebalance_or_update": rebalance_name,
                        "lookback": 0,
                        "pct_risk_on": 1.0,
                        "state_changes": 0,
                        "weights": weight_label(weights),
                    }
                    rows.append(evaluate_candidate(returns, spy_returns, candidate))
    return rows


def generate_tactical_candidates(daily_returns: pd.DataFrame, spy_prices: pd.Series, spy_returns: pd.Series) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_leverage in TARGET_LEVERAGES:
        if target_leverage <= 1.0:
            continue
        for lookback in TACTICAL_LOOKBACKS:
            for update_mode in TACTICAL_UPDATE_MODES:
                for basket_name, basket in DIVERSIFIER_BASKETS.items():
                    if basket_name == "none":
                        continue
                    returns, pct_risk_on, state_changes = tactical_returns(
                        daily_returns,
                        spy_prices,
                        target_leverage,
                        basket,
                        lookback,
                        update_mode,
                    )
                    candidate = {
                        "family": "tactical_sma_target_leverage",
                        "name": f"SMA{lookback} L{target_leverage:.2f} off {basket_name} {update_mode}",
                        "target_leverage": target_leverage,
                        "equity_allocation": 1.0,
                        "diversifier_basket": basket_name,
                        "rebalance_or_update": update_mode,
                        "lookback": lookback,
                        "pct_risk_on": pct_risk_on,
                        "state_changes": state_changes,
                        "weights": f"risk-on {weight_label(target_leverage_weights(target_leverage))}; risk-off {basket_name}",
                    }
                    rows.append(evaluate_candidate(returns, spy_returns, candidate))
    return rows


def format_rows(frame: pd.DataFrame, limit: int = 20) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Family": row["family"].replace("_", " "),
                "Name": row["name"],
                "L": fmt_num(row["target_leverage"], 2),
                "CAGR": fmt_pct(row["cagr"]),
                "Spread": fmt_pp(row["cagr_spread"]),
                "MDD": fmt_pct(row["mdd"]),
                "MDD vs SPY": fmt_pp(row["mdd_spread"]),
                "Terminal/SPY": fmt_x(row["terminal_vs_spy"]),
                "Min Rel 10y+": fmt_x(row["min_relative_after_10y"]),
                "Above 10y+": fmt_pct(row["pct_above_after_10y"], 1),
                "10y+ Hit": fmt_pct(row["min_hit_10p"], 1),
                "Rel DD": fmt_pct(row["worst_relative_drawdown"]),
                "Sustained Above": row["first_sustained_above_date"],
                "Pass": "yes" if row["dominance_pass"] else "no",
            }
        )
    return rows


def write_report(results: pd.DataFrame, daily_returns: pd.DataFrame) -> None:
    spy_metrics = metrics_from_returns(daily_returns["SPYSIM"])
    dominance = results[results["dominance_pass"]]
    strict = results[results["strict_full_dominance"]]
    static = results[results["family"] == "static_target_leverage"]
    tactical = results[results["family"] == "tactical_sma_target_leverage"]
    top = results.iloc[0]
    top_static = static.iloc[0]
    top_tactical = tactical.iloc[0]

    conclusion = (
        f"The equity-dominance objective changes the picture materially. The top ranked row is `{top['name']}`: "
        f"CAGR {fmt_pct(top['cagr'])}, MDD {fmt_pct(top['mdd'])}, terminal wealth {fmt_x(top['terminal_vs_spy'])} vs SPY, "
        f"minimum relative equity after 10y {fmt_x(top['min_relative_after_10y'])}, and 10y+ rolling hit {fmt_pct(top['min_hit_10p'], 1)}. "
        f"Drawdown is reported as diagnostic only."
    )
    if dominance.empty:
        conclusion += " No candidate met the dominance pass definition."
    else:
        conclusion += f" `{len(dominance):,}` candidates met the dominance pass definition."

    sections = [
        "# SPY/SSO/UPRO Replacement - Equity Dominance Report\n\n"
        "Status: research-only objective pivot. This report does not authorize deployment, paper trading or mandate changes.\n\n"
        "Method references: this phase ranks benchmark-relative equity curves and rolling-window dominance rather than max-drawdown gates; rolling diagnostics remain robustness checks `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. The explicit target-leverage ladder follows the LETF leverage premise `[leverage_for_the_long_run, p.13]`.\n\n"
        "## Executive Conclusion\n\n"
        f"{conclusion}\n\n"
        "Practical conclusion: using target leverage directly is the right abstraction. Static and tactical candidates are now judged by whether their portfolio equity stays ahead of SPY equity, especially after a long warmup, while absolute MDD is no longer a hard blocker.\n\n"
        "## Source Data And Objective\n\n"
        "| Item | Value |\n|---|---|\n"
        f"| Testfol.io cache | `data/testfolio/cache/history.parquet` |\n"
        f"| Daily common window | `{daily_returns.index[0].date()}` to `{daily_returns.index[-1].date()}` |\n"
        f"| SPY baseline | CAGR {fmt_pct(spy_metrics.cagr)}, MDD {fmt_pct(spy_metrics.mdd)}, Sharpe {fmt_num(spy_metrics.sharpe)} |\n"
        f"| Target leverage ladder | `{', '.join(f'{x:.2f}x' for x in TARGET_LEVERAGES)}` |\n"
        f"| Static candidates | `{len(static):,}` |\n"
        f"| Tactical candidates | `{len(tactical):,}` |\n"
        f"| Dominance pass rows | `{len(dominance):,}` |\n"
        f"| Strict full-period dominance rows | `{len(strict):,}` |\n\n"
        "Dominance pass means terminal wealth beats SPY, minimum 10y+ rolling hit rate is at least 90%, and relative equity stays at or above SPY after the first 10 years. Full-period MDD can be worse than SPY.\n"
    ]

    columns = ["Family", "Name", "L", "CAGR", "Spread", "MDD", "MDD vs SPY", "Terminal/SPY", "Min Rel 10y+", "Above 10y+", "10y+ Hit", "Rel DD", "Sustained Above", "Pass"]
    sections.append(
        "## Top Equity-Dominance Candidates\n\n"
        "Analysis: This is the primary ranking. It rewards benchmark-relative equity dominance and allows higher absolute drawdown if the relative equity curve remains ahead.\n\n"
        + (
            "Conclusion: At least one candidate maintains benchmark-relative dominance after the warmup; inspect relative drawdown before treating it as practical.\n\n"
            if not dominance.empty
            else "Conclusion: No candidate maintained benchmark-relative dominance after the warmup; leverage alone is insufficient under this definition.\n\n"
        )
        + md_table(format_rows(results, 25), columns)
    )

    sections.append(
        "## Static Target-Leverage Candidates\n\n"
        "Analysis: Static rows use explicit target leverage with adjacent ETFs, plus optional diversifier baskets. This removes the redundant free mix of SPY/SSO/UPRO.\n\n"
        f"Conclusion: Best static row is `{top_static['name']}` with terminal/SPY {fmt_x(top_static['terminal_vs_spy'])}, min relative equity after 10y {fmt_x(top_static['min_relative_after_10y'])}, and MDD {fmt_pct(top_static['mdd'])}.\n\n"
        + md_table(format_rows(static, 20), columns)
    )

    sections.append(
        "## Tactical SMA Candidates\n\n"
        "Analysis: Tactical rows hold the target-leverage risk-on sleeve only when lagged SPY is above its SMA; risk-off is a diversifier basket. Signals are lagged to avoid same-close lookahead.\n\n"
        f"Conclusion: Best tactical row is `{top_tactical['name']}` with terminal/SPY {fmt_x(top_tactical['terminal_vs_spy'])}, min relative equity after 10y {fmt_x(top_tactical['min_relative_after_10y'])}, and MDD {fmt_pct(top_tactical['mdd'])}.\n\n"
        + md_table(format_rows(tactical, 20), columns)
    )

    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        "| Did we remove redundant free SPY/SSO/UPRO mixing? | Yes; all equity sleeves use an explicit adjacent target-leverage ladder. |\n"
        f"| Did any candidate pass equity dominance after 10y warmup? | {'Yes' if not dominance.empty else 'No'}. |\n"
        f"| Did any candidate stay above SPY for the full period? | {'Yes' if not strict.empty else 'No'}. |\n"
        "| Is worse absolute MDD allowed in this phase? | Yes; MDD is diagnostic only. |\n"
        "| Is this deployment-ready? | No. This is an objective pivot and still research-only. |\n\n"
        "Recommended next step: inspect the top dominance rows manually, then run a narrow validation/stress pass on only the selected static and tactical families.\n"
    )

    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = load_testfolio_frame()
    daily_prices = frame[ASSETS].dropna()
    daily_returns = daily_prices.pct_change().dropna()
    spy_returns = daily_returns["SPYSIM"]

    rows = []
    rows.extend(generate_static_candidates(daily_returns, spy_returns))
    rows.extend(generate_tactical_candidates(daily_returns, daily_prices["SPYSIM"], spy_returns))
    results = pd.DataFrame(rows).sort_values(
        ["dominance_pass", "score", "terminal_vs_spy", "min_relative_after_10y"],
        ascending=[False, False, False, False],
    )
    results.to_csv(RESULTS / "equity_dominance_candidates.csv", index=False)
    write_report(results, daily_returns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
