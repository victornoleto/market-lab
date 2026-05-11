"""Iter 031 — TQQQ/CASH proxy plus annual DARF tax for iter 030.

Tests whether the iter 030 `T35D60 + LRS1.20` research winner survives a
no-margin implementation proxy: ON normal = QLD, ON rearm/turbo = 80% TQQQ +
20% CASHX, OFF = ZROZ. Realized gains/losses are netted annually and taxed at
15% on the first trading day of the next year, matching Lei 14.754 annual
settlement semantics for foreign investments.

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60]: LRS leverage scaling and the
  economic target behind the 2.4x NDX proxy.
- [advances_fin_ml, p.208-211]: PBO / anti-overfit gate retained for comparison.
- [advances_fin_ml, p.222-223]: cumulative DSR n_trials accounting.
"""
from __future__ import annotations

import importlib.util
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.core.gates import (
    g1_pbo,
    g2_dsr_p_value,
    g3_walk_forward,
    g4_oos_70_30,
    g5_fwd_post_2020,
    g6_bootstrap_ci,
    g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.core.scoring import crisis_beats_benchmark, score_strategy


ITER_DIR = Path(__file__).parent
LOOP_DIR = ITER_DIR.parent
STUDY_DIR = LOOP_DIR.parent
LOG = logging.getLogger("iter031")

ITER_ID = "031-2026-05-10-tqqq-cash-proxy-annual-tax"
PRE_ITER_CUMULATIVE = 606
LOCAL_N_CONFIGS = 8
DARF_RATE = 0.15
INITIAL_CAPITAL = 10_000.0

WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_CAGR = 0.3108
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95
PHASE3_CAGR_FLOOR = 0.3108
PHASE3_END_EQ_RATIO_FLOOR = 1.05
PHASE3_SORTINO_FLOOR = 1.20
PHASE3_PBO_CEIL = 0.50
PHASE3_DSR_CEIL = 0.05

T3D_RETURNS = (
    STUDY_DIR
    / "runs/original"
    / "022-2026-05-06-T3d-extended-grid"
    / "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
)
ITER030_DIR = LOOP_DIR / "030-2026-05-10-tcrash-scan-lrs120-rearmonly"
ITER030_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120"

DATASET_WINDOWS = {
    "lh_56y": ("1970-01-01", "2026-04-30"),
    "modern_1990": ("1990-01-01", "2026-04-30"),
    "spy_real": ("2003-01-01", "2026-04-30"),
    "ndx_real": ("2010-02-01", "2026-04-30"),
}


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


ITER007 = _load_module(
    LOOP_DIR / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter031_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

ITER011 = _load_module(
    LOOP_DIR / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter031_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2

RI = _load_module(
    LOOP_DIR / "022-2026-05-10-rearm-only-indep-pfv-confirm" / "rearm_independent.py",
    "iter031_rearm_independent",
)
build_postcrash_rearm_gate_independent = RI.build_postcrash_rearm_gate_independent
diagnose_rearm_events_independent = RI.diagnose_rearm_events_independent


@dataclass
class TaxEvent:
    date: str
    asset: str
    proceeds: float
    cost_basis_sold: float
    realized_pnl: float
    reason: str


def read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    col = "return" if "return" in df.columns else "ret"
    return df.set_index("date")[col].astype(float).sort_index()


def load_universe() -> dict[str, pd.Series]:
    return {
        "QLD": load_testfolio_series("QLDSIM"),
        "TQQQ": load_testfolio_series("TQQQSIM"),
        "ZROZ": load_testfolio_series("ZROZSIM"),
        "CASHX": load_testfolio_series("CASHX"),
        "SPY": load_testfolio_series("SPYSIM"),
        "QQQ": load_testfolio_series("QQQSIM"),
    }


def equity(returns: pd.Series, initial: float = INITIAL_CAPITAL) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod() * initial


def build_proxy_weights(on_signal: pd.Series, rearm_gate: pd.Series, index: pd.Index) -> pd.DataFrame:
    on_lag = on_signal.shift(1).reindex(index).fillna(0.0)
    rearm_lag = rearm_gate.shift(1).reindex(index).fillna(0.0)
    weights = pd.DataFrame(0.0, index=index, columns=["QLD", "TQQQ", "ZROZ", "CASHX"])
    off = on_lag != 1.0
    turbo = (on_lag == 1.0) & (rearm_lag == 1.0)
    normal = (on_lag == 1.0) & ~turbo
    weights.loc[off, "ZROZ"] = 1.0
    weights.loc[normal, "QLD"] = 1.0
    weights.loc[turbo, "TQQQ"] = 0.80
    weights.loc[turbo, "CASHX"] = 0.20
    return weights


def build_t3d_weights(on_signal: pd.Series, index: pd.Index) -> pd.DataFrame:
    on_lag = on_signal.shift(1).reindex(index).fillna(0.0)
    weights = pd.DataFrame(0.0, index=index, columns=["QLD", "ZROZ"])
    weights.loc[on_lag == 1.0, "QLD"] = 1.0
    weights.loc[on_lag != 1.0, "ZROZ"] = 1.0
    return weights


def weights_to_returns(weights: pd.DataFrame, returns: pd.DataFrame) -> pd.Series:
    aligned_returns = returns.reindex(weights.index).fillna(0.0)
    return (weights * aligned_returns[weights.columns]).sum(axis=1).rename("return")


def _current_prices(price_row: pd.Series) -> dict[str, float]:
    return {k: float(v) for k, v in price_row.items() if pd.notna(v)}


def simulate_proxy_lots(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    tax_rate: float,
    rebalance_on_state_change_only: bool,
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    """Simulate daily returns with average-cost lots and annual 15% net-profit tax.

    Rebalances are performed at each day's start using the target weights that
    were already lagged outside this function. Annual tax for year Y is deducted
    on the first trading day of Y+1 before that day's rebalance and return.
    """
    idx = weights.index.intersection(prices.dropna(how="all").index)
    weights = weights.reindex(idx).fillna(0.0)
    prices = prices.reindex(idx).ffill()

    cash = INITIAL_CAPITAL
    qty = {asset: 0.0 for asset in weights.columns}
    cost = {asset: 0.0 for asset in qty}
    annual_pnl: dict[int, float] = {}
    loss_carryforward = 0.0
    settled_years: set[int] = set()
    tax_rows: list[dict] = []
    trade_rows: list[TaxEvent] = []
    values: list[float] = []
    prev_target_key: tuple[tuple[str, float], ...] | None = None

    def portfolio_value(px: dict[str, float]) -> float:
        return cash + sum(qty[a] * px[a] for a in qty)

    def settle_year(year: int, ts: pd.Timestamp, px: dict[str, float]) -> None:
        nonlocal cash, loss_carryforward
        if year in settled_years:
            return
        gross = annual_pnl.get(year, 0.0)
        taxable = gross + loss_carryforward
        if taxable > 0.0:
            tax = taxable * tax_rate
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
        px = _current_prices(prices.loc[ts])
        if i > 0:
            prev_year = pd.Timestamp(idx[i - 1]).year
            if ts.year != prev_year:
                settle_year(prev_year, pd.Timestamp(ts), px)

        total = portfolio_value(px)
        target = weights.loc[ts].to_dict()
        target_key = tuple(sorted((k, round(float(v), 10)) for k, v in target.items() if abs(float(v)) > 1e-10))
        should_rebalance = (not rebalance_on_state_change_only) or (target_key != prev_target_key)
        if not should_rebalance:
            values.append(portfolio_value(px))
            continue

        for asset in qty:
            target_value = total * float(target.get(asset, 0.0))
            current_value = qty[asset] * px[asset]
            delta_value = target_value - current_value
            if delta_value < -1e-7:
                sell_value = -delta_value
                sell_qty = min(qty[asset], sell_value / px[asset])
                if sell_qty > 1e-12:
                    avg_cost = cost[asset] / qty[asset] if qty[asset] > 0 else 0.0
                    cost_sold = avg_cost * sell_qty
                    proceeds = sell_qty * px[asset]
                    realized = proceeds - cost_sold
                    qty[asset] -= sell_qty
                    cost[asset] -= cost_sold
                    cash += proceeds
                    if asset != "CASHX":
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

        value_after = portfolio_value(px)
        values.append(value_after)
        prev_target_key = target_key

    if len(idx) > 0:
        settle_year(pd.Timestamp(idx[-1]).year, pd.Timestamp(idx[-1]), _current_prices(prices.loc[idx[-1]]))
        values[-1] = portfolio_value(_current_prices(prices.loc[idx[-1]]))

    value_s = pd.Series(values, index=idx, name="equity")
    returns = value_s.pct_change().fillna(0.0)
    returns.iloc[0] = value_s.iloc[0] / INITIAL_CAPITAL - 1.0
    tax_df = pd.DataFrame(tax_rows)
    trades_df = pd.DataFrame([e.__dict__ for e in trade_rows])
    return returns.rename("return"), tax_df, trades_df


def rolling_win_rates(candidate_eq: pd.Series, baseline_eq: pd.Series) -> dict[str, float]:
    out = {}
    joined = pd.concat([candidate_eq, baseline_eq], axis=1, join="inner").dropna()
    joined.columns = ["candidate", "baseline"]
    for years in (1, 3, 5, 10):
        window = years * 252
        if len(joined) <= window:
            out[f"{years}y"] = float("nan")
            continue
        ratio = ((joined["candidate"] / joined["candidate"].shift(window)) /
                 (joined["baseline"] / joined["baseline"].shift(window))).dropna()
        out[f"{years}y"] = float((ratio > 1.0).mean()) if len(ratio) else float("nan")
    return out


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
    LOG.info("Loading prices and signals...")
    prices = load_universe()
    price_df = pd.DataFrame({k: v for k, v in prices.items() if k in {"QLD", "TQQQ", "ZROZ", "CASHX", "SPY", "QQQ"}}).dropna(how="all").ffill()
    returns_df = price_df.pct_change().dropna()
    spy_ret = prices["SPY"].pct_change().dropna()

    qld_ret = prices["QLD"].pct_change().dropna()
    on_signal = entry_signal_K2(prices["QLD"], qld_ret)
    rearm_gate = build_postcrash_rearm_gate_independent(on_signal, t_crash=35, d_arm=60)
    rearm_diag = diagnose_rearm_events_independent(on_signal, t_crash=35, d_arm=60)

    idx = returns_df.index
    proxy_weights = build_proxy_weights(on_signal, rearm_gate, idx)
    proxy_gross = weights_to_returns(proxy_weights, returns_df)
    t3d_weights = build_t3d_weights(on_signal, idx)
    t3d_tax, t3d_tax_events, t3d_trades = simulate_proxy_lots(
        t3d_weights, price_df[["QLD", "ZROZ"]], tax_rate=DARF_RATE, rebalance_on_state_change_only=True,
    )
    proxy_daily_tax, daily_tax_events, daily_trades = simulate_proxy_lots(
        proxy_weights, price_df, tax_rate=DARF_RATE, rebalance_on_state_change_only=False,
    )
    proxy_state_gross, state_gross_tax_events, state_gross_trades = simulate_proxy_lots(
        proxy_weights, price_df, tax_rate=0.0, rebalance_on_state_change_only=True,
    )
    proxy_state_tax, state_tax_events, state_tax_trades = simulate_proxy_lots(
        proxy_weights, price_df, tax_rate=DARF_RATE, rebalance_on_state_change_only=True,
    )

    t3d = read_returns(T3D_RETURNS)
    iter030 = read_returns(ITER030_DIR / f"{ITER030_CONFIG}_strategy_returns.csv")
    spy_buyhold = prices["SPY"].pct_change().dropna()
    ndx_buyhold = prices["QQQ"].pct_change().dropna()
    per_cfg_returns = {
        "t3d_k2_gross_reference": t3d,
        "t3d_k2_state_annualtax": t3d_tax,
        "iter030_gross_reference": iter030,
        "spy_buyhold_static_notax": spy_buyhold,
        "ndx_qqq_buyhold_static_notax": ndx_buyhold,
        "t35d60_tqqq80_cash20_proxy_daily_gross": proxy_gross,
        "t35d60_tqqq80_cash20_proxy_daily_annualtax": proxy_daily_tax,
        "t35d60_tqqq80_cash20_proxy_state_gross": proxy_state_gross,
        "t35d60_tqqq80_cash20_proxy_state_annualtax": proxy_state_tax,
    }

    daily_tax_events.to_csv(ITER_DIR / "annual_tax_events_daily_rebalance.csv", index=False)
    daily_trades.to_csv(ITER_DIR / "realized_sale_events_daily_rebalance.csv", index=False)
    t3d_tax_events.to_csv(ITER_DIR / "annual_tax_events_t3d_k2.csv", index=False)
    t3d_trades.to_csv(ITER_DIR / "realized_sale_events_t3d_k2.csv", index=False)
    state_tax_events.to_csv(ITER_DIR / "annual_tax_events_state_change.csv", index=False)
    state_tax_trades.to_csv(ITER_DIR / "realized_sale_events_state_change.csv", index=False)
    state_gross_tax_events.to_csv(ITER_DIR / "annual_tax_events_state_change_gross.csv", index=False)
    state_gross_trades.to_csv(ITER_DIR / "realized_sale_events_state_change_gross.csv", index=False)
    proxy_weights.to_csv(ITER_DIR / "proxy_target_weights.csv", index_label="date")

    LOG.info("Computing gates and metrics...")
    spy_metrics = spy_anchor_metrics(spy_ret)
    g1_inputs = {
        name: windowed_returns(r, *DATASET_WINDOWS["lh_56y"])
        for name, r in per_cfg_returns.items()
        if "buyhold" not in name
    }
    g1_result = g1_pbo(g1_inputs)
    spy_lh = windowed_returns(spy_ret, *DATASET_WINDOWS["lh_56y"])
    baseline_lh_eq = equity(windowed_returns(t3d_tax, *DATASET_WINDOWS["lh_56y"]))

    results = []
    metrics_rows = []
    for name, returns in per_cfg_returns.items():
        metrics = compute_per_dataset(returns, spy_ret)
        r_lh = windowed_returns(returns, *DATASET_WINDOWS["lh_56y"])
        g2_local = g2_dsr_p_value(r_lh, n_trials=LOCAL_N_CONFIGS)
        g2_global = g2_dsr_p_value(r_lh, n_trials=PRE_ITER_CUMULATIVE + LOCAL_N_CONFIGS)
        g3 = g3_walk_forward(r_lh, benchmark_returns=spy_lh)
        g4 = g4_oos_70_30(r_lh)
        g5 = g5_fwd_post_2020(r_lh)
        g6 = g6_bootstrap_ci(r_lh)
        g7 = g7_xlib_cagr_delta(r_lh)
        gate_dict = {
            "g1_pbo": g1_result["pbo"],
            "g1_pbo_n_combinations": g1_result["n_combinations"],
            "g2_dsr_p_local": g2_local["p_value"],
            "g2_dsr_p_cumulative": g2_global["p_value"],
            "g2_observed_sharpe": g2_local["observed_sharpe"],
            "g3_wf_windows_pass": g3.get("windows_pass_sharpe_positive", 0),
            "g3_wf_windows_pass_pct_above_benchmark": g3.get("windows_pass_pct_above_benchmark", 0),
            "g3_wf_windows_pass_sharpe_positive": g3.get("windows_pass_sharpe_positive", 0),
            "g3_wf_n_windows": g3["n_windows"],
            "g3_wf_max_mdd": g3["max_mdd"],
            "g3_wf_warmup_used_days": g3["warmup_used_days"],
            "g4_oos_sharpe": g4["oos_sharpe"],
            "g5_fwd_post2020_sharpe": g5["fwd_sharpe"],
            "g5_fwd_n_obs": g5["n_obs_post_2020"],
            "g6_bootstrap_99_low": g6["ci_low_sharpe"],
            "g7_xlib_cagr_delta": g7.get("delta_pp", g7.get("delta", 0.0)),
        }
        strat_lh_eq = equity(r_lh)
        spy_lh_eq = equity(spy_lh)
        crisis_flags = crisis_beats_benchmark(strat_lh_eq, spy_lh_eq)
        score = score_strategy(
            metrics_per_dataset={ds: metrics[ds] for ds in DATASET_WINDOWS},
            anchors_sharpe_per_dataset={ds: spy_metrics[ds]["sharpe"] for ds in DATASET_WINDOWS},
            spy_mdd_per_dataset={ds: spy_metrics[ds]["mdd"] for ds in DATASET_WINDOWS},
            gates=gate_dict,
            crisis_beats_spy=crisis_flags,
            bonus_pts=0.0,
        )
        common = strat_lh_eq.index.intersection(baseline_lh_eq.index)
        end_ratio = float(strat_lh_eq.loc[common[-1]] / baseline_lh_eq.loc[common[-1]]) if len(common) else float("nan")
        sortino = metrics["lh_56y"]["sortino"]
        cagr = metrics["lh_56y"]["cagr"]
        pct_above = metrics["lh_56y"]["pct_time_above_benchmark"]
        beats_winner = bool(sortino > BEATS_THRESHOLD_SORTINO and score["winner_conditions_met"] and pct_above >= BEATS_PCT_ABOVE)
        phase3 = bool(cagr > PHASE3_CAGR_FLOOR and end_ratio > PHASE3_END_EQ_RATIO_FLOOR and sortino >= PHASE3_SORTINO_FLOOR and gate_dict["g1_pbo"] < PHASE3_PBO_CEIL and gate_dict["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL)
        if name == "t3d_k2_state_annualtax":
            tax_source = t3d_tax_events
            trade_source = t3d_trades
        elif "state" in name:
            tax_source = state_tax_events
            trade_source = state_tax_trades
        else:
            tax_source = daily_tax_events
            trade_source = daily_trades
        rec = {
            "config_name": name,
            "kind": name,
            "metrics_gross": {ds: metrics[ds] for ds in DATASET_WINDOWS},
            "metrics_net": {"annual_tax_model": name.endswith("annualtax")},
            "tax_summary": {
                "total_tax_paid": float(tax_source["tax_paid"].sum()) if not tax_source.empty and name.endswith("annualtax") else 0.0,
                "n_tax_years": int((tax_source["tax_paid"] > 0).sum()) if not tax_source.empty and name.endswith("annualtax") else 0,
                "n_sale_events": int(len(trade_source)) if name.endswith("annualtax") else 0,
            },
            "rearm_diag": rearm_diag,
            "gates": gate_dict,
            "score_breakdown": score,
            "tier_label": score["tier_label"],
            "winner_conditions_met": score["winner_conditions_met"],
            "sortino_lh56y": float(sortino),
            "cagr_lh56y": float(cagr),
            "pct_time_above_benchmark_lh56y": float(pct_above),
            "sortino_edge_vs_winner": float(sortino - WINNER_BENCHMARK_SORTINO),
            "cagr_edge_vs_winner": float(cagr - WINNER_BENCHMARK_CAGR),
            "end_equity_ratio_vs_baseline": end_ratio,
            "rolling_win_rates_vs_baseline": rolling_win_rates(strat_lh_eq, baseline_lh_eq),
            "beats_winner": beats_winner,
            "phase3_performance_candidate": phase3,
            "strict_superset": bool(beats_winner and phase3),
        }
        results.append(rec)
        for ds in DATASET_WINDOWS:
            row = {"config": name, "dataset": ds}
            row.update(metrics[ds])
            metrics_rows.append(row)
        returns.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    pd.DataFrame(metrics_rows).to_csv(ITER_DIR / "per_config_metrics.csv", index=False)
    pd.DataFrame([
        {"config": r["config_name"], **r["gates"]} for r in results
    ]).to_csv(ITER_DIR / "gates_pass_fail.csv", index=False)

    best = sorted(results, key=lambda r: (r["strict_superset"], r["phase3_performance_candidate"], r["sortino_lh56y"], r["cagr_lh56y"]), reverse=True)[0]
    t3d_tax_rec = next(r for r in results if r["config_name"] == "t3d_k2_state_annualtax")
    proxy_tax_rec = next(r for r in results if r["config_name"] == "t35d60_tqqq80_cash20_proxy_state_annualtax")
    iter030_rec = next(r for r in results if r["config_name"] == "iter030_gross_reference")
    proxy_gross_rec = next(r for r in results if r["config_name"] == "t35d60_tqqq80_cash20_proxy_state_gross")
    proxy_daily_tax_rec = next(r for r in results if r["config_name"] == "t35d60_tqqq80_cash20_proxy_daily_annualtax")
    spy_rec = next(r for r in results if r["config_name"] == "spy_buyhold_static_notax")
    ndx_rec = next(r for r in results if r["config_name"] == "ndx_qqq_buyhold_static_notax")

    kill_rule_status = "PASS" if proxy_tax_rec["phase3_performance_candidate"] else "FIRES"
    verdict = {
        "iter": ITER_ID,
        "tier": "loop_iter",
        "phase": 4,
        "phase_name": "execution realism / annual tax diagnostic",
        "hypothesis": "Replace iter 030's abstract LRS1.20 exposure with a no-margin 80% TQQQ + 20% CASHX turbo proxy and apply annual 15% Brazilian tax on realized net gains.",
        "primary_citation": "[leverage_for_the_long_run, ch.4-5, p.40-60]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_031",
        "configs_tested": [{"name": r["config_name"]} for r in results],
        "datasets": list(DATASET_WINDOWS),
        "windows_used": DATASET_WINDOWS,
        "results": results,
        "best_config": best["config_name"],
        "best_score": best["score_breakdown"]["total"],
        "best_tier": best["tier_label"],
        "kill_rule_status": kill_rule_status,
        "cumulative_n_trials_local": LOCAL_N_CONFIGS,
        "cumulative_n_trials_loop": 186,
        "cumulative_n_trials_global": PRE_ITER_CUMULATIVE + LOCAL_N_CONFIGS,
        "sortino_lh56y": best["sortino_lh56y"],
        "cagr_lh56y": best["cagr_lh56y"],
        "winner_conditions_met": best["winner_conditions_met"],
        "pct_time_above_benchmark_lh56y": best["pct_time_above_benchmark_lh56y"],
        "beats_winner": best["beats_winner"],
        "sortino_edge_vs_winner": best["sortino_edge_vs_winner"],
        "winner_benchmark_sortino": WINNER_BENCHMARK_SORTINO,
        "beats_winner_threshold_sortino": BEATS_THRESHOLD_SORTINO,
        "winner_benchmark_iter": "022-2026-05-06-T3d-extended-grid",
        "winner_benchmark_config": "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
        "proxy_tax_result": proxy_tax_rec,
        "t3d_tax_result": t3d_tax_rec,
        "proxy_daily_tax_result": proxy_daily_tax_rec,
        "proxy_gross_result": proxy_gross_rec,
        "iter030_gross_reference_result": iter030_rec,
        "spy_buyhold_result": spy_rec,
        "ndx_qqq_buyhold_result": ndx_rec,
        "t3d_annual_tax_total_paid": float(t3d_tax_events["tax_paid"].sum()) if not t3d_tax_events.empty else 0.0,
        "t3d_annual_tax_years_paid": int((t3d_tax_events["tax_paid"] > 0).sum()) if not t3d_tax_events.empty else 0,
        "t3d_realized_sale_events": int(len(t3d_trades)),
        "annual_tax_total_paid": float(state_tax_events["tax_paid"].sum()) if not state_tax_events.empty else 0.0,
        "annual_tax_years_paid": int((state_tax_events["tax_paid"] > 0).sum()) if not state_tax_events.empty else 0,
        "realized_sale_events": int(len(state_tax_trades)),
        "daily_rebalance_annual_tax_total_paid": float(daily_tax_events["tax_paid"].sum()) if not daily_tax_events.empty else 0.0,
        "daily_rebalance_realized_sale_events": int(len(daily_trades)),
        "rearm_diag_t35d60": rearm_diag,
    }
    verdict = json_clean(verdict)
    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, allow_nan=False))
    write_summary(verdict)
    LOG.info("Best=%s score=%.1f", best["config_name"], best["score_breakdown"]["total"])
    return verdict


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def write_summary(verdict: dict) -> None:
    rows = []
    for r in verdict["results"]:
        rows.append(
            f"| `{r['config_name']}` | {r['sortino_lh56y']:.4f} | {fmt_pct(r['cagr_lh56y'])} | "
            f"{fmt_pct(r['metrics_gross']['lh_56y']['mdd'])} | {r['end_equity_ratio_vs_baseline']:.3f}x | "
            f"{r['gates']['g1_pbo']:.4f} | {r['gates']['g2_dsr_p_cumulative']:.2e} | "
            f"{r['score_breakdown']['total']:.1f} | {r['tier_label']} |"
        )
    proxy_tax = verdict["proxy_tax_result"]
    t3d_tax = verdict["t3d_tax_result"]
    proxy_daily_tax = verdict["proxy_daily_tax_result"]
    proxy_gross = verdict["proxy_gross_result"]
    iter030 = verdict["iter030_gross_reference_result"]
    spy = verdict["spy_buyhold_result"]
    ndx = verdict["ndx_qqq_buyhold_result"]
    text = f"""# Iter 031 — TQQQ/CASH proxy plus annual DARF tax

**Iter:** `{ITER_ID}`
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`
**Cumulative global trials:** {verdict['cumulative_n_trials_global']}

## TL;DR

This iteration tests the execution concern that exiting turbo requires selling
TQQQ and buying QLD, creating realized P&L that is taxed annually at 15% if the
calendar-year net is positive. The fair panel also taxes T3d-K2 state changes and
keeps SPY/NDX buy-and-hold untaxed because there are no interim sale events.

Proxy tested:

| State | Weight |
|---|---:|
| OFF | 100% ZROZ |
| ON normal | 100% QLD |
| ON rearm/turbo | 80% TQQQ + 20% CASHX |

Tax model: all realized sale P&L is netted by calendar year; positive annual net
profit is taxed at 15% on the first trading day of the next year. Losses carry
forward.

## Results

| Config | Sortino | CAGR | MDD | End equity vs taxed T3d-K2 | PBO | DSR global | Score | Tier |
|---|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## Implementation Drag

| Comparison | CAGR | Sortino | End equity vs taxed T3d-K2 |
|---|---:|---:|---:|
| Iter 030 gross reference | {fmt_pct(iter030['cagr_lh56y'])} | {iter030['sortino_lh56y']:.4f} | {iter030['end_equity_ratio_vs_baseline']:.3f}x |
| T3d-K2 state-change annual-tax | {fmt_pct(t3d_tax['cagr_lh56y'])} | {t3d_tax['sortino_lh56y']:.4f} | {t3d_tax['end_equity_ratio_vs_baseline']:.3f}x |
| TQQQ/CASH proxy state-change gross | {fmt_pct(proxy_gross['cagr_lh56y'])} | {proxy_gross['sortino_lh56y']:.4f} | {proxy_gross['end_equity_ratio_vs_baseline']:.3f}x |
| TQQQ/CASH proxy state-change annual-tax | {fmt_pct(proxy_tax['cagr_lh56y'])} | {proxy_tax['sortino_lh56y']:.4f} | {proxy_tax['end_equity_ratio_vs_baseline']:.3f}x |
| TQQQ/CASH proxy daily-rebalance annual-tax | {fmt_pct(proxy_daily_tax['cagr_lh56y'])} | {proxy_daily_tax['sortino_lh56y']:.4f} | {proxy_daily_tax['end_equity_ratio_vs_baseline']:.3f}x |
| SPY buy-and-hold static no-tax | {fmt_pct(spy['cagr_lh56y'])} | {spy['sortino_lh56y']:.4f} | {spy['end_equity_ratio_vs_baseline']:.3f}x |
| NDX/QQQ buy-and-hold static no-tax | {fmt_pct(ndx['cagr_lh56y'])} | {ndx['sortino_lh56y']:.4f} | {ndx['end_equity_ratio_vs_baseline']:.3f}x |

T3d-K2 tax paid: `${verdict['t3d_annual_tax_total_paid']:.2f}` on initial `${INITIAL_CAPITAL:.0f}` scale across `{verdict['t3d_annual_tax_years_paid']}` tax years.
T3d-K2 realized sale events recorded: `{verdict['t3d_realized_sale_events']}`.

State-change tax paid: `${verdict['annual_tax_total_paid']:.2f}` on initial `${INITIAL_CAPITAL:.0f}` scale across `{verdict['annual_tax_years_paid']}` tax years.
State-change realized sale events recorded: `{verdict['realized_sale_events']}`.

Daily-rebalance stress tax paid: `${verdict['daily_rebalance_annual_tax_total_paid']:.2f}` with `{verdict['daily_rebalance_realized_sale_events']}` realized sale events.

## Verdict

`kill_rule_status`: **{verdict['kill_rule_status']}**.

The annual-tax proxy remains research-only and does not authorize deploy. It is
an execution-realism diagnostic for a future monitoring app; mandate §1 remains
100% Plano C.

## Files

- `verdict.json`
- `per_config_metrics.csv`
- `gates_pass_fail.csv`
- `annual_tax_events_state_change.csv`
- `realized_sale_events_state_change.csv`
- `annual_tax_events_t3d_k2.csv`
- `realized_sale_events_t3d_k2.csv`
- `annual_tax_events_daily_rebalance.csv`
- `realized_sale_events_daily_rebalance.csv`
- `proxy_target_weights.csv`
"""
    (ITER_DIR / "SUMMARY.md").write_text(text)


if __name__ == "__main__":
    main()
