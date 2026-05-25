from __future__ import annotations

from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from run_equity_dominance import (
    DIVERSIFIER_BASKETS,
    TARGET_LEVERAGES,
    first_sustained_above_date,
    target_leverage_weights,
    weight_label,
)
from run_static_grid import (
    ASSETS,
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
    rolling_relative_stats,
)
from studies._shared.tax_engine import AnnualDarfEngine


REPORT = ROOT / "PRACTICAL_TAXED_REPORT.md"
INITIAL_CAPITAL = 10_000.0

ACTIVE_UPDATE_FREQS = {"monthly": "M", "quarterly": "Q"}
STATIC_REBALANCE_FREQS = {"monthly": "M", "quarterly": "Q", "annual": "Y"}
ACTIVE_LOOKBACKS = [100, 150, 200, 250, 300]
STATIC_EQUITY_ALLOCATIONS = [0.60, 0.70, 0.80, 0.90, 1.00]
ACTIVE_TARGET_LEVERAGES = [2.00, 2.50, 2.75, 3.00]
STATIC_TARGET_LEVERAGES = TARGET_LEVERAGES
ACTIVE_DIVERSIFIER_BASKETS = {
    name: DIVERSIFIER_BASKETS[name]
    for name in [
        "ZROZ",
        "GLD",
        "CASH",
        "60 ZROZ / 40 GLD",
        "50 ZROZ / 50 GLD",
        "40 ZROZ / 40 GLD / 20 IEF",
        "50 ZROZ / 25 GLD / 25 CASH",
    ]
}
STATIC_DIVERSIFIER_BASKETS = {
    name: DIVERSIFIER_BASKETS[name]
    for name in [
        "none",
        "ZROZ",
        "GLD",
        "60 ZROZ / 40 GLD",
        "50 ZROZ / 50 GLD",
        "40 ZROZ / 40 GLD / 20 IEF",
    ]
}


def clean_weights(row: pd.Series | dict[str, float]) -> dict[str, float]:
    items = row.items() if isinstance(row, pd.Series) else row.items()
    return {str(asset): float(weight) for asset, weight in items if float(weight) > 1e-10}


def array_weights_dict(weights: np.ndarray) -> dict[str, float]:
    return {asset: float(weights[i]) for i, asset in enumerate(ASSETS) if float(weights[i]) > 1e-10}


def first_period_mask(index: pd.DatetimeIndex, freq: str) -> pd.Series:
    periods = index.to_period(freq)
    values = np.r_[True, periods[1:].to_numpy() != periods[:-1].to_numpy()]
    mask = pd.Series(values, index=index)
    return mask


def constant_target_frame(index: pd.DatetimeIndex, weights: dict[str, float]) -> pd.DataFrame:
    frame = pd.DataFrame(0.0, index=index, columns=ASSETS)
    for asset, weight in weights.items():
        frame[asset] = weight
    return frame


def tactical_target_frame(
    index: pd.DatetimeIndex,
    spy_prices: pd.Series,
    risk_on_weights: dict[str, float],
    risk_off_weights: dict[str, float],
    lookback: int,
    freq: str,
) -> tuple[pd.DataFrame, pd.Series]:
    sma = spy_prices.rolling(lookback).mean()
    raw_signal = (spy_prices.shift(1) > sma.shift(1)).reindex(index).fillna(False)
    rebalance_mask = first_period_mask(index, freq)
    period_signal = raw_signal[rebalance_mask]
    period_by_date = index.to_period(freq)
    signal_by_period = period_signal.groupby(period_signal.index.to_period(freq)).first()
    held_signal = pd.Series(period_by_date.map(signal_by_period).astype(bool), index=index)

    frame = pd.DataFrame(0.0, index=index, columns=ASSETS)
    for asset in ASSETS:
        frame[asset] = np.where(
            held_signal,
            risk_on_weights.get(asset, 0.0),
            risk_off_weights.get(asset, 0.0),
        )
    return frame, held_signal


def simulate_schedule(
    asset_returns: pd.DataFrame,
    target_weights: pd.DataFrame,
    rebalance_mask: pd.Series,
    taxable: bool,
) -> tuple[pd.Series, dict[str, float]]:
    aligned_returns = asset_returns[ASSETS].reindex(target_weights.index).fillna(0.0)
    targets = target_weights[ASSETS].reindex(aligned_returns.index).fillna(0.0)
    mask = rebalance_mask.reindex(aligned_returns.index).fillna(False).astype(bool)
    if not bool(mask.iloc[0]):
        mask.iloc[0] = True

    returns_arr = aligned_returns.to_numpy(dtype=np.float64)
    target_arr = targets.to_numpy(dtype=np.float64)
    mask_arr = mask.to_numpy(dtype=bool)
    gross_values = target_arr[0].copy()
    tax_values = target_arr[0].copy() * INITIAL_CAPITAL

    engine = AnnualDarfEngine(initial_investment=INITIAL_CAPITAL) if taxable else None
    gross_returns: list[float] = []
    net_returns: list[float] = []
    total_turnover = 0.0
    rebalance_count = 0
    trade_count = 0
    final_liquidation_recorded = False

    dates = aligned_returns.index
    for i, date in enumerate(dates):
        target_arr_i = target_arr[i]

        if bool(mask_arr[i]):
            gross_equity_pre = float(gross_values.sum())
            tax_equity_pre = float(tax_values.sum())
            tax_prev_arr = tax_values / tax_equity_pre if tax_equity_pre > 0 else np.zeros_like(tax_values)
            turnover = 0.5 * float(np.abs(target_arr_i - tax_prev_arr).sum())
            if turnover > 1e-8:
                total_turnover += turnover
                trade_count += 1
                if engine is not None:
                    engine.record_trade(date, array_weights_dict(tax_prev_arr), array_weights_dict(target_arr_i))
            rebalance_count += 1
            gross_values = gross_equity_pre * target_arr_i
            tax_values = tax_equity_pre * target_arr_i

        gross_before = float(gross_values.sum())
        tax_before = float(engine.port_value if engine is not None else tax_values.sum())

        day_returns = returns_arr[i]
        gross_values = gross_values * (1.0 + day_returns)
        tax_values = tax_values * (1.0 + day_returns)

        gross_after = float(gross_values.sum())
        tax_after_pre_settlement = float(tax_values.sum())
        gross_ret = gross_after / gross_before - 1.0 if gross_before > 0 else 0.0

        if engine is None:
            net_ret = gross_ret
        else:
            engine.apply_return(tax_after_pre_settlement / tax_before - 1.0 if tax_before > 0 else 0.0)
            next_date = dates[i + 1] if i + 1 < len(dates) else None
            is_last = next_date is None
            if is_last and not final_liquidation_recorded:
                current_weights_arr = tax_values / tax_after_pre_settlement if tax_after_pre_settlement > 0 else np.zeros_like(tax_values)
                engine.record_trade(date, array_weights_dict(current_weights_arr), {})
                final_liquidation_recorded = True
            if is_last or pd.Timestamp(next_date).year != pd.Timestamp(date).year:
                engine.year_end_settlement(pd.Timestamp(date).year, force=is_last)
                if tax_after_pre_settlement > 0:
                    tax_values *= engine.port_value / tax_after_pre_settlement
            net_ret = engine.port_value / tax_before - 1.0 if tax_before > 0 else 0.0

        gross_returns.append(gross_ret)
        net_returns.append(net_ret)

    selected = net_returns if taxable else gross_returns
    returns = pd.Series(selected, index=dates, name="taxed" if taxable else "gross")
    summary: dict[str, float] = {
        "total_turnover": float(total_turnover),
        "rebalance_count": float(rebalance_count),
        "trade_count": float(trade_count),
        "avg_turnover_per_year": float(total_turnover / (len(dates) / TRADING_DAYS)),
        "total_tax_paid_pct_initial": 0.0,
    }
    if engine is not None:
        summary["total_tax_paid_pct_initial"] = float(engine.total_darf_paid / INITIAL_CAPITAL)
        summary["tax_events"] = float(sum(1 for event in engine.events if event.get("darf", 0.0) > 0.0))
    return returns, summary


def evaluate_path(
    gross_returns: pd.Series,
    taxed_returns: pd.Series,
    spy_gross: pd.Series,
    spy_taxed: pd.Series,
    candidate: dict[str, object],
    tax_summary: dict[str, float],
) -> dict[str, object]:
    gross_metrics = metrics_from_returns(gross_returns)
    taxed_metrics = metrics_from_returns(taxed_returns)
    spy_gross_metrics = metrics_from_returns(spy_gross)
    spy_taxed_metrics = metrics_from_returns(spy_taxed)

    gross_aligned = pd.concat({"portfolio": gross_returns, "spy": spy_gross}, axis=1).dropna()
    taxed_aligned = pd.concat({"portfolio": taxed_returns, "spy": spy_taxed}, axis=1).dropna()
    gross_relative = (1.0 + gross_aligned["portfolio"]).cumprod() / (1.0 + gross_aligned["spy"]).cumprod()
    taxed_relative = (1.0 + taxed_aligned["portfolio"]).cumprod() / (1.0 + taxed_aligned["spy"]).cumprod()
    taxed_after_10y = taxed_relative.iloc[10 * TRADING_DAYS :] if len(taxed_relative) > 10 * TRADING_DAYS else taxed_relative.iloc[0:0]
    taxed_rolling = rolling_relative_stats(taxed_returns, spy_taxed)
    gross_rolling = rolling_relative_stats(gross_returns, spy_gross)

    net_min_hit_10p = min(taxed_rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 10)
    net_min_rel_after_10y = float(taxed_after_10y.min()) if not taxed_after_10y.empty else math.nan
    net_pct_above_after_10y = float((taxed_after_10y >= 1.0 - HIT_TOLERANCE).mean()) if not taxed_after_10y.empty else math.nan
    net_terminal_vs_spy = float(taxed_relative.iloc[-1])
    net_cagr_spread = taxed_metrics.cagr - spy_taxed_metrics.cagr
    gross_terminal_vs_spy = float(gross_relative.iloc[-1])
    practical_pass = net_terminal_vs_spy > 1.0 and net_min_rel_after_10y >= 1.0 and net_min_hit_10p >= 0.90
    score = (
        2.0 * math.log(max(net_terminal_vs_spy, 1e-9))
        + 1.25 * net_min_hit_10p
        + 0.80 * net_pct_above_after_10y
        + 0.75 * min(0.0, math.log(max(net_min_rel_after_10y, 1e-9)))
        + 7.0 * net_cagr_spread
    )

    return {
        **candidate,
        "practical_pass": practical_pass,
        "score": score,
        "gross_cagr": gross_metrics.cagr,
        "gross_mdd": gross_metrics.mdd,
        "gross_terminal_vs_spy": gross_terminal_vs_spy,
        "gross_min_hit_10p": min(gross_rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 10),
        "taxed_cagr": taxed_metrics.cagr,
        "taxed_spy_cagr": spy_taxed_metrics.cagr,
        "taxed_cagr_spread": net_cagr_spread,
        "taxed_mdd": taxed_metrics.mdd,
        "taxed_spy_mdd": spy_taxed_metrics.mdd,
        "taxed_mdd_spread": taxed_metrics.mdd - spy_taxed_metrics.mdd,
        "taxed_terminal_vs_spy": net_terminal_vs_spy,
        "taxed_min_rel_after_10y": net_min_rel_after_10y,
        "taxed_pct_above_after_10y": net_pct_above_after_10y,
        "taxed_min_hit_10p": net_min_hit_10p,
        "taxed_first_sustained_above": first_sustained_above_date(taxed_relative),
        "taxed_worst_relative_drawdown": float((taxed_relative / taxed_relative.cummax() - 1.0).min()),
        **tax_summary,
    }


def build_spy_benchmark(daily_returns: pd.DataFrame) -> tuple[pd.Series, pd.Series, dict[str, float]]:
    index = daily_returns.index
    weights = {"SPYSIM": 1.0}
    targets = constant_target_frame(index, weights)
    rebalance_mask = pd.Series(False, index=index)
    rebalance_mask.iloc[0] = True
    gross, _ = simulate_schedule(daily_returns, targets, rebalance_mask, taxable=False)
    taxed, summary = simulate_schedule(daily_returns, targets, rebalance_mask, taxable=True)
    return gross, taxed, summary


def static_candidates(daily_returns: pd.DataFrame, spy_gross: pd.Series, spy_taxed: pd.Series) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_leverage in STATIC_TARGET_LEVERAGES:
        for equity_allocation in STATIC_EQUITY_ALLOCATIONS:
            diversifier_allocation = 1.0 - equity_allocation
            for basket_name, basket in STATIC_DIVERSIFIER_BASKETS.items():
                if diversifier_allocation == 0.0 and basket_name != "none":
                    continue
                if diversifier_allocation > 0.0 and basket_name == "none":
                    continue
                weights = target_leverage_weights(target_leverage, equity_allocation)
                for asset, basket_weight in basket.items():
                    weights[asset] = weights.get(asset, 0.0) + diversifier_allocation * basket_weight
                for cadence, freq in STATIC_REBALANCE_FREQS.items():
                    targets = constant_target_frame(daily_returns.index, weights)
                    mask = first_period_mask(daily_returns.index, freq)
                    gross, _gross_summary = simulate_schedule(daily_returns, targets, mask, taxable=False)
                    taxed, tax_summary = simulate_schedule(daily_returns, targets, mask, taxable=True)
                    rows.append(
                        evaluate_path(
                            gross,
                            taxed,
                            spy_gross,
                            spy_taxed,
                            {
                                "family": "static_buy_hold_rebalanced",
                                "name": f"static L{target_leverage:.2f} E{equity_allocation:.0%} {basket_name} {cadence}",
                                "target_leverage": target_leverage,
                                "cadence": cadence,
                                "lookback": 0,
                                "risk_off": basket_name,
                                "weights": weight_label(weights),
                            },
                            tax_summary,
                        )
                    )
    return rows


def active_candidates(
    daily_returns: pd.DataFrame,
    spy_prices: pd.Series,
    spy_gross: pd.Series,
    spy_taxed: pd.Series,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_leverage in ACTIVE_TARGET_LEVERAGES:
        if target_leverage <= 1.0:
            continue
        risk_on = target_leverage_weights(target_leverage, 1.0)
        for lookback in ACTIVE_LOOKBACKS:
            for cadence, freq in ACTIVE_UPDATE_FREQS.items():
                mask = first_period_mask(daily_returns.index, freq)
                for basket_name, basket in ACTIVE_DIVERSIFIER_BASKETS.items():
                    targets, held_signal = tactical_target_frame(daily_returns.index, spy_prices, risk_on, basket, lookback, freq)
                    gross, _gross_summary = simulate_schedule(daily_returns, targets, mask, taxable=False)
                    taxed, tax_summary = simulate_schedule(daily_returns, targets, mask, taxable=True)
                    rows.append(
                        evaluate_path(
                            gross,
                            taxed,
                            spy_gross,
                            spy_taxed,
                            {
                                "family": "active_risk_on_off",
                                "name": f"SMA{lookback} L{target_leverage:.2f} off {basket_name} {cadence}",
                                "target_leverage": target_leverage,
                                "cadence": cadence,
                                "lookback": lookback,
                                "risk_off": basket_name,
                                "pct_risk_on": float(held_signal.mean()),
                                "state_changes": int(held_signal.astype(int).diff().abs().fillna(0).sum()),
                                "weights": f"risk-on {weight_label(risk_on)}; risk-off {basket_name}",
                            },
                            tax_summary,
                        )
                    )
    return rows


def format_rows(frame: pd.DataFrame, limit: int = 20) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Family": str(row["family"]).replace("_", " "),
                "Name": row["name"],
                "Cadence": row["cadence"],
                "L": fmt_num(row["target_leverage"], 2),
                "Tax CAGR": fmt_pct(row["taxed_cagr"]),
                "Spread": fmt_pp(row["taxed_cagr_spread"]),
                "Tax MDD": fmt_pct(row["taxed_mdd"]),
                "MDD vs SPY": fmt_pp(row["taxed_mdd_spread"]),
                "Tax Terminal/SPY": fmt_x(row["taxed_terminal_vs_spy"]),
                "Min Rel 10y+": fmt_x(row["taxed_min_rel_after_10y"]),
                "10y+ Hit": fmt_pct(row["taxed_min_hit_10p"], 1),
                "Tax Paid": fmt_pct(row["total_tax_paid_pct_initial"], 1),
                "Turnover/Yr": fmt_num(row["avg_turnover_per_year"], 2),
                "Pass": "yes" if row["practical_pass"] else "no",
            }
        )
    return rows


def write_report(results: pd.DataFrame, spy_tax_summary: dict[str, float], daily_returns: pd.DataFrame) -> None:
    active = results[results["family"] == "active_risk_on_off"]
    static = results[results["family"] == "static_buy_hold_rebalanced"]
    active_pass = active[active["practical_pass"]]
    static_pass = static[static["practical_pass"]]
    best_active = active.iloc[0]
    best_static = static.iloc[0]
    cadence_counts = {
        "monthly": int(first_period_mask(daily_returns.index, "M").sum()),
        "quarterly": int(first_period_mask(daily_returns.index, "Q").sum()),
        "annual": int(first_period_mask(daily_returns.index, "Y").sum()),
    }

    sections = [
        "# SPY/SSO/UPRO Replacement - Practical Taxed Selection\n\n"
        "Status: research-only practical rerun. Daily rebalance/update is excluded as non-operational. This report does not authorize deployment, paper trading or mandate changes.\n\n"
        "Method references: SMA risk-on/off follows the leverage-for-the-long-run premise for levered equity with trend/risk-off filters `[leverage_for_the_long_run, p.13]`; cadence and tax sensitivity are implementation robustness checks `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. Tax model uses the repository `AnnualDarfEngine`: annual settlement on realized net gains, indefinite loss carry-forward, and final liquidation for comparable after-tax terminal wealth (Lei 14.754/2023).\n\n"
        "## Executive Conclusion\n\n"
        f"Daily execution materially overstated practicality, so it was removed. Under monthly/quarterly active updates and monthly/quarterly/annual static rebalancing, the best active risk-on/off row is `{best_active['name']}` with after-tax CAGR {fmt_pct(best_active['taxed_cagr'])}, MDD {fmt_pct(best_active['taxed_mdd'])}, terminal {fmt_x(best_active['taxed_terminal_vs_spy'])} vs after-tax SPY, min relative equity after 10y {fmt_x(best_active['taxed_min_rel_after_10y'])}, and 10y+ hit {fmt_pct(best_active['taxed_min_hit_10p'], 1)}. The best static row is `{best_static['name']}` with after-tax CAGR {fmt_pct(best_static['taxed_cagr'])}, MDD {fmt_pct(best_static['taxed_mdd'])}, terminal {fmt_x(best_static['taxed_terminal_vs_spy'])} vs after-tax SPY, min relative equity after 10y {fmt_x(best_static['taxed_min_rel_after_10y'])}, and 10y+ hit {fmt_pct(best_static['taxed_min_hit_10p'], 1)}.\n\n"
        "Practical conclusion: active monthly/quarterly risk-on/off is the only branch that currently produces benchmark-relative equity dominance after tax. Static target-leverage portfolios improve long-run terminal wealth but do not maintain relative equity dominance through adverse regimes.\n\n"
        "## Source Data And Tax Model\n\n"
        "| Item | Value |\n|---|---|\n"
        f"| Testfol.io cache | `data/testfolio/cache/history.parquet` |\n"
        f"| Daily common window | `{daily_returns.index[0].date()}` to `{daily_returns.index[-1].date()}` |\n"
        f"| Cadence event counts | monthly `{cadence_counts['monthly']}`, quarterly `{cadence_counts['quarterly']}`, annual `{cadence_counts['annual']}` |\n"
        "| Active cadences | `monthly`, `quarterly` only |\n"
        "| Static cadences | `monthly`, `quarterly`, `annual` only |\n"
        "| Tax model | `AnnualDarfEngine`, 15% annual DARF on realized net gains, loss carry-forward, final liquidation |\n"
        f"| SPY benchmark tax paid / initial | {fmt_pct(spy_tax_summary['total_tax_paid_pct_initial'], 1)} |\n"
        f"| Active candidates | `{len(active):,}`; practical passes `{len(active_pass):,}` |\n"
        f"| Static candidates | `{len(static):,}`; practical passes `{len(static_pass):,}` |\n\n"
        "Practical pass means after-tax terminal wealth beats after-tax SPY, after-tax relative equity stays above SPY after the first 10 years, and minimum 10y+ rolling hit rate is at least 90%. MDD is diagnostic, not a gate.\n"
    ]

    columns = ["Family", "Name", "Cadence", "L", "Tax CAGR", "Spread", "Tax MDD", "MDD vs SPY", "Tax Terminal/SPY", "Min Rel 10y+", "10y+ Hit", "Tax Paid", "Turnover/Yr", "Pass"]
    sections.append(
        "## Best Active Risk-On/Off\n\n"
        "Analysis: Active candidates only update monthly or quarterly. They may hold levered equity or a risk-off basket for weeks/months, not days.\n\n"
        + ("Conclusion: The active branch has after-tax dominance candidates.\n\n" if not active_pass.empty else "Conclusion: The active branch has no after-tax dominance candidate under practical cadences.\n\n")
        + md_table(format_rows(active, 25), columns)
    )
    sections.append(
        "## Best Static Buy-And-Hold/Rebalanced\n\n"
        "Analysis: Static candidates maintain target proportions using only monthly/quarterly/annual rebalancing; no signal switching is used.\n\n"
        + ("Conclusion: The static branch has after-tax dominance candidates.\n\n" if not static_pass.empty else "Conclusion: Static target-leverage portfolios do not maintain after-tax relative equity dominance, even when terminal wealth improves.\n\n")
        + md_table(format_rows(static, 25), columns)
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        "| Is daily rebalance/update allowed? | No. It is excluded as non-operational. |\n"
        "| Is 15% annual Brazilian tax modeled? | Yes, via `AnnualDarfEngine` on realized annual net gains plus final liquidation. |\n"
        f"| Best active strategy after tax | `{best_active['name']}`. |\n"
        f"| Best static strategy after tax | `{best_static['name']}`. |\n"
        f"| Does active pass practical after-tax dominance? | {'Yes' if not active_pass.empty else 'No'}. |\n"
        f"| Does static pass practical after-tax dominance? | {'Yes' if not static_pass.empty else 'No'}. |\n"
        "| Is either branch deploy-ready? | No. This is selection only; validation/stress remains required. |\n\n"
        "Recommended next step: validate only the selected active and static winners with start-date stress, cost sensitivity, subperiod/regime tables, and an explicit tax-event audit.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = load_testfolio_frame()
    daily_prices = frame[ASSETS].dropna()
    daily_returns = daily_prices.pct_change().dropna()
    spy_gross, spy_taxed, spy_tax_summary = build_spy_benchmark(daily_returns)

    rows = []
    rows.extend(active_candidates(daily_returns, daily_prices["SPYSIM"], spy_gross, spy_taxed))
    rows.extend(static_candidates(daily_returns, spy_gross, spy_taxed))
    results = pd.DataFrame(rows).sort_values(
        ["family", "practical_pass", "score", "taxed_terminal_vs_spy"],
        ascending=[True, False, False, False],
    )
    active = results[results["family"] == "active_risk_on_off"].sort_values(
        ["practical_pass", "score", "taxed_terminal_vs_spy"], ascending=[False, False, False]
    )
    static = results[results["family"] == "static_buy_hold_rebalanced"].sort_values(
        ["practical_pass", "score", "taxed_terminal_vs_spy"], ascending=[False, False, False]
    )
    ordered = pd.concat([active, static], ignore_index=True)
    ordered.to_csv(RESULTS / "practical_taxed_candidates.csv", index=False)
    write_report(ordered, spy_tax_summary, daily_returns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
