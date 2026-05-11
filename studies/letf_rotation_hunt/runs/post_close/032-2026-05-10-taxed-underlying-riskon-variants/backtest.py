"""Iter 032 — taxed T3d-K2 underlying/risk-on variants.

Compares tax-aware T3d-K2 baseline and iter 030 proxy against three requested
variants: T3d-K2 with TQQQ risk-on, T3d-K2 with SPY/SSO, and T3d-K2 with
SPY/UPRO. Dynamic strategies use annual 15% realized net-gain tax. Static
SPY/NDX buy-and-hold benchmarks are left untaxed because there are no interim
sales.

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60]: leveraged risk-on variants.
- [advances_fin_ml, p.208-211]: rolling-window/overfit diagnostics.
- [advances_fin_ml, p.222-223]: cumulative trial accounting context.
"""
from __future__ import annotations

import importlib.util
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.core.scoring import compute_metrics
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import _annualised_sortino


ITER_DIR = Path(__file__).parent
LOOP_DIR = ITER_DIR.parent
ITER031_DIR = LOOP_DIR / "031-2026-05-10-tqqq-cash-proxy-annual-tax"
PLOTS_DIR = ITER_DIR / "plots"
TABLES_DIR = ITER_DIR / "tables"
LOG = logging.getLogger("iter032")

ITER_ID = "032-2026-05-10-taxed-underlying-riskon-variants"
INITIAL_CAPITAL = 10_000.0
DARF_RATE = 0.15


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


ITER011 = _load_module(
    LOOP_DIR / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter032_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2


@dataclass
class TaxEvent:
    date: str
    asset: str
    proceeds: float
    cost_basis_sold: float
    realized_pnl: float
    reason: str


def load_universe() -> dict[str, pd.Series]:
    return {
        "QLD": load_testfolio_series("QLDSIM"),
        "TQQQ": load_testfolio_series("TQQQSIM"),
        "SPY": load_testfolio_series("SPYSIM"),
        "SSO": load_testfolio_series("SSOSIM"),
        "UPRO": load_testfolio_series("UPROSIM"),
        "ZROZ": load_testfolio_series("ZROZSIM"),
        "CASHX": load_testfolio_series("CASHX"),
        "QQQ": load_testfolio_series("QQQSIM"),
    }


def read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    col = "return" if "return" in df.columns else "ret"
    return df.set_index("date")[col].astype(float).sort_index()


def equity(returns: pd.Series, initial: float = INITIAL_CAPITAL) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod() * initial


def max_drawdown(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1.0).min())


def metrics(returns: pd.Series) -> dict[str, float]:
    r = returns.dropna()
    eq = equity(r)
    out = compute_metrics(eq, r)
    out["sortino"] = _annualised_sortino(r)
    out["n_obs"] = float(len(r))
    return out


def build_weights(on_signal: pd.Series, index: pd.Index, risk_on: str, risk_off: str = "ZROZ") -> pd.DataFrame:
    on_lag = on_signal.shift(1).reindex(index).fillna(0.0)
    weights = pd.DataFrame(0.0, index=index, columns=sorted({risk_on, risk_off}))
    weights.loc[on_lag == 1.0, risk_on] = 1.0
    weights.loc[on_lag != 1.0, risk_off] = 1.0
    return weights


def current_prices(price_row: pd.Series) -> dict[str, float]:
    return {k: float(v) for k, v in price_row.items() if pd.notna(v)}


def simulate_annual_tax(weights: pd.DataFrame, prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    idx = weights.index.intersection(prices.dropna(how="all").index)
    weights = weights.reindex(idx).fillna(0.0)
    prices = prices.reindex(idx).ffill()
    cash = INITIAL_CAPITAL
    qty = {asset: 0.0 for asset in weights.columns}
    cost = {asset: 0.0 for asset in weights.columns}
    annual_pnl: dict[int, float] = {}
    loss_carryforward = 0.0
    settled_years: set[int] = set()
    tax_rows: list[dict] = []
    trade_rows: list[TaxEvent] = []
    values: list[float] = []
    prev_key: tuple[tuple[str, float], ...] | None = None

    def portfolio_value(px: dict[str, float]) -> float:
        return cash + sum(qty[a] * px[a] for a in qty)

    def settle_year(year: int, ts: pd.Timestamp, px: dict[str, float]) -> None:
        nonlocal cash, loss_carryforward
        if year in settled_years:
            return
        gross = annual_pnl.get(year, 0.0)
        taxable = gross + loss_carryforward
        if taxable > 0.0:
            tax = taxable * DARF_RATE
            cash -= tax
            loss_carryforward = 0.0
        else:
            tax = 0.0
            loss_carryforward = taxable
        settled_years.add(year)
        tax_rows.append({
            "settlement_date": ts.date().isoformat(),
            "tax_year": year,
            "annual_realized_pnl": gross,
            "taxable_after_carry": taxable,
            "tax_paid": tax,
            "loss_carryforward_out": loss_carryforward,
            "portfolio_value_after_tax": portfolio_value(px),
        })

    for i, ts in enumerate(idx):
        px = current_prices(prices.loc[ts])
        if i > 0:
            prev_year = pd.Timestamp(idx[i - 1]).year
            if ts.year != prev_year:
                settle_year(prev_year, pd.Timestamp(ts), px)
        target = weights.loc[ts].to_dict()
        key = tuple(sorted((k, round(float(v), 10)) for k, v in target.items() if abs(float(v)) > 1e-10))
        if key == prev_key:
            values.append(portfolio_value(px))
            continue

        total = portfolio_value(px)
        for asset in qty:
            target_value = total * float(target.get(asset, 0.0))
            current_value = qty[asset] * px[asset]
            delta = target_value - current_value
            if delta < -1e-7:
                sell_value = -delta
                sell_qty = min(qty[asset], sell_value / px[asset])
                if sell_qty > 1e-12:
                    avg_cost = cost[asset] / qty[asset] if qty[asset] > 0 else 0.0
                    cost_sold = avg_cost * sell_qty
                    proceeds = sell_qty * px[asset]
                    realized = proceeds - cost_sold
                    qty[asset] -= sell_qty
                    cost[asset] -= cost_sold
                    cash += proceeds
                    annual_pnl[ts.year] = annual_pnl.get(ts.year, 0.0) + realized
                    trade_rows.append(TaxEvent(ts.date().isoformat(), asset, proceeds, cost_sold, realized, "rebalance_sell"))

        total = portfolio_value(px)
        investable_cash = cash
        for asset in qty:
            target_value = total * float(target.get(asset, 0.0))
            current_value = qty[asset] * px[asset]
            buy_value = target_value - current_value
            if buy_value > 1e-7 and investable_cash > 0.0:
                spend = min(buy_value, investable_cash)
                qty[asset] += spend / px[asset]
                cost[asset] += spend
                cash -= spend
                investable_cash -= spend
        values.append(portfolio_value(px))
        prev_key = key

    if len(idx) > 0:
        settle_year(pd.Timestamp(idx[-1]).year, pd.Timestamp(idx[-1]), current_prices(prices.loc[idx[-1]]))
        values[-1] = portfolio_value(current_prices(prices.loc[idx[-1]]))
    eq = pd.Series(values, index=idx, name="equity")
    ret = eq.pct_change().fillna(0.0)
    ret.iloc[0] = eq.iloc[0] / INITIAL_CAPITAL - 1.0
    return ret.rename("return"), pd.DataFrame(tax_rows), pd.DataFrame([e.__dict__ for e in trade_rows])


def rolling_stats(candidate: pd.Series, benchmark: pd.Series) -> list[dict[str, float | str | int]]:
    joined = pd.concat([equity(candidate), equity(benchmark)], axis=1, join="inner").dropna()
    joined.columns = ["candidate", "benchmark"]
    out = []
    for years in (1, 3, 5, 10):
        window = years * 252
        if len(joined) <= window:
            out.append({"window_years": years, "win_rate": np.nan, "mean_end_ratio": np.nan, "min_end_ratio": np.nan})
            continue
        ratio = ((joined["candidate"] / joined["candidate"].shift(window)) / (joined["benchmark"] / joined["benchmark"].shift(window))).dropna()
        out.append({
            "window_years": years,
            "win_rate": float((ratio > 1.0).mean()),
            "mean_end_ratio": float(ratio.mean()),
            "min_end_ratio": float(ratio.min()),
        })
    return out


def plot_equity(series: dict[str, pd.Series]) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    for name, returns in series.items():
        lw = 2.6 if "iter30" in name or "t3d_k2_taxed" in name else 1.7
        ax.plot(equity(returns).index, equity(returns), label=name, linewidth=lw)
    ax.set_yscale("log")
    ax.set_title("Tax-aware T3d-K2 variants: equity curves")
    ax.set_ylabel("Growth of $10,000, log scale")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_equity_curves.png", dpi=160)
    plt.close(fig)


def plot_relative(series: dict[str, pd.Series], benchmarks: dict[str, pd.Series]) -> None:
    for bench_name, bench in benchmarks.items():
        fig, ax = plt.subplots(figsize=(14, 8))
        beq = equity(bench)
        for name, returns in series.items():
            joined = pd.concat([equity(returns), beq], axis=1, join="inner").dropna()
            joined.columns = ["candidate", "benchmark"]
            ax.plot(joined.index, joined["candidate"] / joined["benchmark"], label=name, linewidth=1.8)
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_yscale("log")
        ax.set_title(f"Relative equity vs {bench_name}")
        ax.set_ylabel("Relative equity, log scale")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        slug = bench_name.lower().replace("/", "_").replace(" ", "_")
        fig.savefig(PLOTS_DIR / f"02_relative_vs_{slug}.png", dpi=160)
        plt.close(fig)


def plot_rolling_heatmap(rolling_df: pd.DataFrame) -> None:
    for bench in rolling_df["benchmark"].unique():
        sub = rolling_df[rolling_df["benchmark"] == bench]
        pivot = sub.pivot(index="config", columns="window_years", values="win_rate")
        fig, ax = plt.subplots(figsize=(9, 5.5))
        im = ax.imshow(pivot.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
        ax.set_xticks(range(len(pivot.columns)), [f"{c}y" for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)), pivot.index)
        ax.set_title(f"Rolling win rate vs {bench}")
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.values[i, j]
                ax.text(j, i, "" if np.isnan(val) else f"{val:.0%}", ha="center", va="center", color="white" if val < 0.65 else "black")
        fig.colorbar(im, ax=ax, label="Win rate")
        fig.tight_layout()
        slug = bench.lower().replace("/", "_").replace(" ", "_")
        fig.savefig(PLOTS_DIR / f"03_rolling_winrate_vs_{slug}.png", dpi=160)
        plt.close(fig)


def pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x * 100:.2f}%"


def json_clean(value):
    if isinstance(value, dict):
        return {k: json_clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_clean(v) for v in value]
    if isinstance(value, tuple):
        return [json_clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return value


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_universe()
    price_df = pd.DataFrame(prices).ffill()
    ret_df = price_df.pct_change().dropna()

    qld_signal = entry_signal_K2(prices["QLD"], ret_df["QLD"])
    spy_signal = entry_signal_K2(prices["SPY"], ret_df["SPY"])
    idx = ret_df.index

    variants = {
        "t3d_k2_taxed": (build_weights(qld_signal, idx, "QLD"), ["QLD", "ZROZ"]),
        "iter30_proxy_taxed": (None, []),
        "t3d_k2_tqqq_taxed": (build_weights(qld_signal, idx, "TQQQ"), ["TQQQ", "ZROZ"]),
        "t3d_k2_spy_sso_taxed": (build_weights(spy_signal, idx, "SSO"), ["SSO", "ZROZ"]),
        "t3d_k2_spy_upro_taxed": (build_weights(spy_signal, idx, "UPRO"), ["UPRO", "ZROZ"]),
    }

    series: dict[str, pd.Series] = {}
    tax_summaries = []
    for name, (weights, cols) in variants.items():
        if name == "iter30_proxy_taxed":
            returns = read_returns(ITER031_DIR / "t35d60_tqqq80_cash20_proxy_state_annualtax_strategy_returns.csv")
            series[name] = returns
            continue
        returns, tax_events, trades = simulate_annual_tax(weights, price_df[cols])
        series[name] = returns
        returns.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])
        tax_events.to_csv(ITER_DIR / f"annual_tax_events_{name}.csv", index=False)
        trades.to_csv(ITER_DIR / f"realized_sale_events_{name}.csv", index=False)
        tax_summaries.append({
            "config": name,
            "tax_paid": float(tax_events["tax_paid"].sum()) if not tax_events.empty else 0.0,
            "tax_years_paid": int((tax_events["tax_paid"] > 0).sum()) if not tax_events.empty else 0,
            "sale_events": int(len(trades)),
        })

    benchmarks = {
        "SPY buyhold": ret_df["SPY"],
        "NDX/QQQ buyhold": ret_df["QQQ"],
        "taxed T3d-K2": series["t3d_k2_taxed"],
    }
    report_series = {**series, "SPY buyhold": ret_df["SPY"], "NDX/QQQ buyhold": ret_df["QQQ"]}

    metric_rows = []
    base_eq = equity(series["t3d_k2_taxed"])
    for name, returns in report_series.items():
        row = {"config": name, **metrics(returns)}
        joined = pd.concat([equity(returns), base_eq], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "baseline"]
        row["end_eq_vs_taxed_t3d"] = float(joined["candidate"].iloc[-1] / joined["baseline"].iloc[-1])
        metric_rows.append(row)
    metrics_df = pd.DataFrame(metric_rows)
    metrics_df.to_csv(TABLES_DIR / "metrics_summary.csv", index=False)
    pd.DataFrame(tax_summaries).to_csv(TABLES_DIR / "tax_summary.csv", index=False)

    rolling_rows = []
    for name, returns in series.items():
        for bench_name, bench in benchmarks.items():
            for row in rolling_stats(returns, bench):
                rolling_rows.append({"config": name, "benchmark": bench_name, **row})
    rolling_df = pd.DataFrame(rolling_rows)
    rolling_df.to_csv(TABLES_DIR / "rolling_window_stats.csv", index=False)

    plot_equity(report_series)
    plot_relative(series, benchmarks)
    plot_rolling_heatmap(rolling_df)

    verdict = {
        "iter": ITER_ID,
        "primary_citation": "[leverage_for_the_long_run, ch.4-5, p.40-60]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "configs_tested": list(series),
        "benchmarks": list(benchmarks),
        "metrics": metric_rows,
        "tax_summary": tax_summaries,
        "rolling_window_stats_path": "tables/rolling_window_stats.csv",
        "best_by_cagr": metrics_df.sort_values("cagr", ascending=False).iloc[0]["config"],
        "best_by_sortino": metrics_df.sort_values("sortino", ascending=False).iloc[0]["config"],
    }
    (ITER_DIR / "verdict.json").write_text(json.dumps(json_clean(verdict), indent=2, allow_nan=False))
    write_report(metrics_df, rolling_df, pd.DataFrame(tax_summaries))
    LOG.info("Wrote %s", ITER_DIR)
    return verdict


def write_report(metrics_df: pd.DataFrame, rolling_df: pd.DataFrame, tax_df: pd.DataFrame) -> None:
    ordered = metrics_df.sort_values("cagr", ascending=False)
    metric_lines = []
    for _, row in ordered.iterrows():
        metric_lines.append(
            f"| `{row['config']}` | {pct(row['cagr'])} | {row['sortino']:.4f} | {pct(row['mdd'])} | {row['end_eq_vs_taxed_t3d']:.3f}x |"
        )
    tax_lines = []
    for _, row in tax_df.iterrows():
        tax_lines.append(
            f"| `{row['config']}` | ${row['tax_paid']:.2f} | {int(row['tax_years_paid'])} | {int(row['sale_events'])} |"
        )
    if not tax_lines:
        tax_lines.append("| n/a | n/a | n/a | n/a |")

    rolling_focus = rolling_df[(rolling_df["benchmark"] == "taxed T3d-K2") & (rolling_df["window_years"].isin([1, 3, 5, 10]))]
    rolling_pivot = rolling_focus.pivot(index="config", columns="window_years", values="win_rate")
    rolling_lines = []
    for config, row in rolling_pivot.iterrows():
        rolling_lines.append(
            f"| `{config}` | {pct(row.get(1))} | {pct(row.get(3))} | {pct(row.get(5))} | {pct(row.get(10))} |"
        )

    text = f"""# Iter 032 — Taxed Underlying/Risk-On Variant Report

**Iter:** `{ITER_ID}`
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`

## TL;DR

This report compares tax-aware T3d-K2 baseline and iter 30 proxy against three
requested variants: always-TQQQ risk-on, SPY/SSO risk-on, and SPY/UPRO risk-on.
Dynamic variants pay annual 15% tax on realized net gains; SPY and NDX/QQQ
buy-and-hold benchmarks are static and have no interim tax events.

## Metrics

| Config | CAGR | Sortino | MDD | End equity vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
{chr(10).join(metric_lines)}

## Tax Summary

| Config | Tax paid on $10k scale | Tax years paid | Sale events |
|---|---:|---:|---:|
{chr(10).join(tax_lines)}

## Rolling Win Rates vs Taxed T3d-K2

| Config | 1y | 3y | 5y | 10y |
|---|---:|---:|---:|---:|
{chr(10).join(rolling_lines)}

## Plots

- ![Equity curves](plots/01_equity_curves.png)
- ![Relative vs SPY](plots/02_relative_vs_spy_buyhold.png)
- ![Relative vs NDX](plots/02_relative_vs_ndx_qqq_buyhold.png)
- ![Relative vs taxed T3d](plots/02_relative_vs_taxed_t3d-k2.png)
- ![Rolling vs taxed T3d](plots/03_rolling_winrate_vs_taxed_t3d-k2.png)
- ![Rolling vs SPY](plots/03_rolling_winrate_vs_spy_buyhold.png)
- ![Rolling vs NDX](plots/03_rolling_winrate_vs_ndx_qqq_buyhold.png)

## Tables

- `tables/metrics_summary.csv`
- `tables/tax_summary.csv`
- `tables/rolling_window_stats.csv`

## Caveat

These are tax-aware research diagnostics, not deployment authorization. Mandate
§1 remains 100% Plano C.
"""
    (ITER_DIR / "REPORT.md").write_text(text)


if __name__ == "__main__":
    main()
