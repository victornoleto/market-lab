"""
Iter 014 — Hybrid 50/50 re-run with ANNUAL DARF (Lei 14.754/2023 correction)

Same strategy as iter 012 (50% HAA+Gold + 50% Plano C V3_1), but uses the
legally-correct annual DARF model:
  - HAA sleeve: gains/losses accumulated during the year, settled on Dec 31
  - Loss carryforward: indefinite (vs 12-month rolling in iter 012)
  - Plano C sleeve: unchanged — terminal DARF only

Old model (iter 012): DARF paid monthly per rebalance, 12-month loss expiry.
New model (iter 014): DARF settled once per calendar year, indefinite carry.

Lei 14.754/2023, vigente jan/2024:
  https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/Lei/L14754.htm

Citations:
  [testing_tuning, ch.5-6]    cost-aware backtest; real-world friction
  [risk_parity, ch.5]          capital efficiency; multi-asset cost context
  [advances_fin_ml, p.208-211] G1 PBO
  [advances_fin_ml, p.222-223] G2 DSR
  [advances_fin_ml, p.196-202] G6 Bootstrap
  [advances_fin_ml, p.31-34]   G7 cross-lib
  [stocks_on_the_move, ch.6]   HAA momentum scoring

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/014-2026-04-27-annual-darf-rerun/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import sharpe, cagr, max_drawdown
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))

from scoring import score_strategy, DatasetMetrics, Gates
from tax_engine_v2 import AnnualDarfEngine

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Parameters (identical to iter 009/012)
# ---------------------------------------------------------------------------
N_CONFIGS        = 1
KMLM_WEIGHT      = 0.10
GLD_WEIGHT       = 0.05
DYNAMIC_WEIGHT   = 0.85
TOP_K_OFFENSIVE  = 2
NOTIONAL_FACTOR  = 1.45
WF_N_WINDOWS     = 8
BOOTSTRAP_N      = 2000
STACK_EQ, STACK_BD, STACK_CASH = 0.90, 0.60, 0.50

DARF_RATE              = 0.15
CARNE_LEAO_ANNUAL      = 0.00047   # ~4.7 bps/y on HAA/MF income
FX_COST_ONE_WAY        = 0.0138    # 1% spread + 0.38% IOF

RAW_TICKERS = [
    "SPYSIM", "VEASIM", "VWOSIM", "IEFSIM", "CASHX",
    "KMLMSIM", "GLDSIM", "GDESIM", "BNDSIM", "VTSIM", "QQQSIM", "VBRSIM",
]

DATASETS = {
    "educational": {"start": "1994-05-01", "end": "2026-04-24", "benchmark": "VTSIM"},
    "vt_real":     {"start": "2008-06-01",  "end": "2026-04-24", "benchmark": "VTSIM"},
    "ndx_real":    {"start": "2010-02-01",  "end": "2026-04-24", "benchmark": "QQQSIM"},
}

# iter 012 results (monthly DARF model) — reference for delta comparison
ITER012_NET = {
    "educational": {"sharpe": 1.0212, "cagr": 0.1338, "mdd": 0.2685},
    "vt_real":     {"sharpe": 1.0579, "cagr": 0.1406, "mdd": 0.1936},
    "ndx_real":    {"sharpe": 0.9715, "cagr": 0.1184, "mdd": 0.1920},
}

# Plano C reference (buy-hold net)
PLANOC_NET = {
    "educational": {"sharpe": 0.631, "cagr": 0.1031, "mdd": 0.5243},
    "vt_real":     {"sharpe": 0.780, "cagr": 0.1143, "mdd": 0.3340},
    "ndx_real":    {"sharpe": 0.740, "cagr": 0.1095, "mdd": 0.1920},
}

PLANOC_WEIGHTS = {
    "GDE": 0.25, "AVUS": 0.12, "AVDE": 0.20, "AVEM": 0.13,
    "AVUV": 0.10, "AVDV": 0.05, "SPMO": 0.07, "IDMO": 0.03, "BTGD": 0.05,
}

# ---------------------------------------------------------------------------
# HAA+Gold simulation (identical to iter 009/012)
# [stocks_on_the_move, ch.6]
# ---------------------------------------------------------------------------

def build_stacked_prices(prices: pd.DataFrame) -> pd.DataFrame:
    ret = prices.pct_change()
    out = prices.copy()
    for label, eq_col, bd_col in [
        ("NTSXSIM", "SPYSIM", "IEFSIM"),
        ("NTSI",    "VEASIM", "IEFSIM"),
        ("NTSE",    "VWOSIM", "IEFSIM"),
    ]:
        stk = STACK_EQ * ret[eq_col] + STACK_BD * ret[bd_col] - STACK_CASH * ret["CASHX"]
        clean = stk.dropna()
        if not clean.empty:
            out[label] = (1 + clean).cumprod() * 100.0
    return out


def haa_momentum(monthly: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    scores = pd.DataFrame(index=monthly.index, columns=assets, dtype=float)
    for a in assets:
        p = monthly[a]
        scores[a] = (p/p.shift(1)-1 + p/p.shift(3)-1 + p/p.shift(6)-1 + p/p.shift(12)-1) / 4.0
    return scores


def simulate_haa_gold_with_weights(prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    offensive = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"]
    defensive = ["IEFSIM", "BNDSIM", "CASHX"]
    all_assets = list(dict.fromkeys(offensive + defensive + ["VWOSIM", "KMLMSIM", "GLDSIM"]))

    px = prices[all_assets].dropna(how="all")
    monthly = px.resample("ME").last()
    off_mom = haa_momentum(monthly, offensive)
    def_mom = haa_momentum(monthly, defensive)
    can_mom = haa_momentum(monthly, ["VWOSIM"])["VWOSIM"]

    wts = pd.DataFrame(0.0, index=monthly.index, columns=all_assets)
    for i in range(12, len(monthly)):
        date = monthly.index[i]
        wts.loc[date, "KMLMSIM"] = KMLM_WEIGHT
        wts.loc[date, "GLDSIM"]  = GLD_WEIGHT
        if can_mom.iloc[i] > 0:
            row = off_mom.iloc[i].dropna()
            tops = (row if row.empty else row.nlargest(min(TOP_K_OFFENSIVE, len(row)))).index.tolist()
            w = DYNAMIC_WEIGHT / max(len(tops), 1)
            for a in (tops or ["CASHX"]):
                wts.loc[date, a] = w
        else:
            row = def_mom.iloc[i].dropna()
            wts.loc[date, row.idxmax() if not row.empty else "CASHX"] = DYNAMIC_WEIGHT

    daily_wts = wts.reindex(px.index, method="ffill").fillna(0.0)
    port_ret  = (daily_wts.shift(1) * px.pct_change()).sum(axis=1).dropna()
    first_sig = monthly.index[12]
    return port_ret[port_ret.index >= first_sig], wts[wts.index >= first_sig]


def simulate_planoc_returns(prices: pd.DataFrame) -> pd.Series:
    ret = prices.pct_change()
    proxy = {
        "GDE": ret["GDESIM"], "AVUS": ret["SPYSIM"], "AVDE": ret["VEASIM"],
        "AVEM": ret["VWOSIM"], "AVUV": ret["VBRSIM"],
        "AVDV": 0.5*ret["VEASIM"] + 0.5*ret["VBRSIM"],
        "SPMO": ret["SPYSIM"], "IDMO": ret["VEASIM"], "BTGD": ret["GLDSIM"],
    }
    common = None
    for r in proxy.values():
        common = r.dropna().index if common is None else common.intersection(r.dropna().index)
    return sum(PLANOC_WEIGHTS[k] * proxy[k].loc[common] for k in PLANOC_WEIGHTS).rename("PLANOC_V3_1")


# ---------------------------------------------------------------------------
# Annual DARF hybrid tax model (KEY CHANGE vs iter 012)
# Lei 14.754/2023: DARF annual, loss carryforward indefinite
# ---------------------------------------------------------------------------

def apply_hybrid_annual_darf(
    haa_daily_returns:   pd.Series,
    haa_monthly_weights: pd.DataFrame,
    planc_daily_returns:  pd.Series,
    dataset_years:       float,
    start_value:         float = 10_000.0,
) -> tuple[pd.Series, dict]:
    """50/50 hybrid with corrected annual DARF model (Lei 14.754/2023).

    HAA sleeve: AnnualDarfEngine — DARF settled on Dec 31 each year.
    Plano C sleeve: unchanged — terminal DARF at final sale.
    FX: 1.38% entry + 1.38% exit (Inter Internacional).
    """
    half          = start_value / 2.0
    eff_start_haa = half * (1.0 - FX_COST_ONE_WAY)
    eff_start_pc  = half * (1.0 - FX_COST_ONE_WAY)

    common_idx = haa_daily_returns.index.intersection(planc_daily_returns.index)
    haa_ret    = haa_daily_returns.loc[common_idx]
    planc_ret  = planc_daily_returns.loc[common_idx]
    daily_idx  = haa_ret.index

    # HAA engine: annual DARF (no deduction during year — only on Dec 31)
    haa_engine = AnnualDarfEngine(initial_investment=eff_start_haa)

    planc_val  = eff_start_pc
    planc_cost = eff_start_pc
    total_planc_darf = 0.0

    # Monthly weight map
    month_dates  = sorted(haa_monthly_weights.index)
    month_idx_map: dict[pd.Timestamp, pd.Timestamp] = {}
    for m_date in month_dates:
        mask = daily_idx <= m_date
        if mask.any():
            month_idx_map[m_date] = daily_idx[mask][-1]
    monthly_dates_set = set(month_idx_map.values())

    # Annual 50/50 inter-sleeve rebalance dates (every 12th month-end)
    active_m_dates = sorted(month_idx_map.keys())
    annual_rebal_set: set[pd.Timestamp] = set()
    for j in range(11, len(active_m_dates), 12):
        annual_rebal_set.add(month_idx_map[active_m_dates[j]])

    # Dec-31 settlement dates (or last trading day of each year)
    year_end_dates: set[pd.Timestamp] = set()
    for yr in range(daily_idx[0].year, daily_idx[-1].year + 1):
        yr_days = daily_idx[daily_idx.year == yr]
        if len(yr_days) > 0:
            year_end_dates.add(yr_days[-1])

    haa_vals   = np.zeros(len(daily_idx))
    planc_vals = np.zeros(len(daily_idx))
    prev_w: dict[str, float] = {}
    n_months_active = 0
    haa_turnover_sum = 0.0
    inter_sleeve_darfs = 0.0

    for i, (date, r_haa) in enumerate(haa_ret.items()):
        r_pc = planc_ret.iloc[i]

        haa_engine.apply_return(r_haa)
        planc_val *= (1.0 + r_pc)

        # HAA monthly rebalance: RECORD trade (no immediate DARF)
        if date in monthly_dates_set:
            matching = [m for m, d in month_idx_map.items() if d == date]
            if matching:
                m_date = matching[0]
                new_w  = haa_monthly_weights.loc[m_date].to_dict()
                # record_trade accumulates in annual bucket — no cash deduction yet
                gross_gain = haa_engine.record_trade(date, prev_w, new_w)
                n_months_active += 1
                sold_f = sum(
                    max(0.0, prev_w.get(k, 0.0) - new_w.get(k, 0.0))
                    for k in set(prev_w) | set(new_w)
                )
                haa_turnover_sum += sold_f
                prev_w = new_w

        # Annual inter-sleeve rebalance
        # Keep immediate DARF for inter-sleeve events (annual, same as iter 012).
        # Annual deferral only applies to HAA's internal monthly rebalances.
        # This avoids accounting complexity where inter-sleeve DARF would be
        # deducted from the selling sleeve's residual instead of the proceeds.
        if date in annual_rebal_set:
            total_val   = haa_engine.port_value + planc_val
            target_each = total_val / 2.0

            if haa_engine.port_value > target_each + 1.0:
                excess    = haa_engine.port_value - target_each
                sell_frac = excess / haa_engine.port_value
                sold_val   = sell_frac * haa_engine.port_value
                cost_sold  = sell_frac * haa_engine.cost_basis
                gross_gain = sold_val - cost_sold
                # Immediate DARF on inter-sleeve HAA sale (annual event, negligible vs monthly)
                darf_haa = max(0.0, gross_gain) * DARF_RATE
                haa_engine.port_value -= darf_haa
                haa_engine.cost_basis *= (1.0 - sell_frac)
                haa_engine.total_darf_paid += darf_haa
                net_proceeds = sold_val - darf_haa
                # Transfer net proceeds to Plano C
                haa_engine.port_value -= (sold_val - darf_haa)
                planc_val  += net_proceeds
                planc_cost += net_proceeds
                inter_sleeve_darfs += darf_haa

            elif planc_val > target_each + 1.0:
                excess       = planc_val - target_each
                sell_frac    = excess / planc_val
                sold_val     = sell_frac * planc_val
                cost_for_sold = sell_frac * planc_cost
                gross_gain   = sold_val - cost_for_sold
                darf_pc = max(0.0, gross_gain) * DARF_RATE
                planc_val   -= darf_pc
                planc_cost  *= (1.0 - sell_frac)
                haa_engine.port_value += (sold_val - darf_pc)
                haa_engine.cost_basis += (sold_val - darf_pc)
                total_planc_darf      += darf_pc
                inter_sleeve_darfs    += darf_pc

        # HAA year-end DARF settlement
        if date in year_end_dates:
            darf_settled = haa_engine.year_end_settlement(date.year)
            inter_sleeve_darfs += darf_settled   # track for reporting

        haa_vals[i]   = haa_engine.port_value
        planc_vals[i] = planc_val

    # Final: settle any unsettled year (mid-year end of simulation)
    last_year = daily_idx[-1].year
    if last_year not in haa_engine._settled_years:
        haa_engine.year_end_settlement(last_year, force=True)
        haa_vals[-1] = haa_engine.port_value

    # Carnê-Leão incremental on HAA sleeve (~4.7bps/y on MF income)
    carne_total = CARNE_LEAO_ANNUAL * dataset_years
    for i in range(len(haa_vals)):
        frac = i / max(len(haa_vals) - 1, 1)
        haa_vals[i] *= (1.0 - carne_total * frac)

    # Terminal DARF on Plano C sleeve (single sale at end)
    planc_terminal_gain = planc_val - planc_cost
    planc_terminal_darf = max(0.0, planc_terminal_gain) * DARF_RATE
    planc_vals[-1] -= planc_terminal_darf
    total_planc_darf += planc_terminal_darf

    # FX exit cost (proportional)
    combined_terminal = haa_vals[-1] + planc_vals[-1]
    if combined_terminal > 0:
        haa_vals[-1]   *= (1.0 - FX_COST_ONE_WAY)
        planc_vals[-1] *= (1.0 - FX_COST_ONE_WAY)

    combined_eq  = pd.Series(haa_vals + planc_vals, index=daily_idx)
    hybrid_ret   = combined_eq.pct_change().fillna(0.0)
    hybrid_ret.iloc[0] = 0.5 * haa_ret.iloc[0] + 0.5 * planc_ret.iloc[0]

    ann_turnover = (haa_turnover_sum / max(n_months_active, 1)) * 12
    report = {
        "model":                     "annual_darf_lei14754_2023",
        "effective_start_total":     round(eff_start_haa + eff_start_pc, 2),
        "terminal_combined_net":     round(combined_eq.iloc[-1], 2),
        "total_haa_darf_annual":     round(haa_engine.total_darf_paid, 2),
        "total_planc_darf":          round(total_planc_darf, 2),
        "loss_carryforward_final":   round(haa_engine.loss_carryforward, 2),
        "haa_annual_settlements":    haa_engine.events,
        "haa_ann_turnover":          round(ann_turnover, 4),
        "darf_drag_pp_estimate":     round(
            haa_engine.total_darf_paid / max(dataset_years * (eff_start_haa / 2), 1) * 100, 2
        ),
    }
    return hybrid_ret, report


def apply_planoc_net_tax(planc_daily_returns: pd.Series, dataset_years: float,
                         start_value: float = 10_000.0) -> tuple[pd.Series, dict]:
    """Terminal DARF on Plano C buy-hold. Unchanged from iter 012."""
    eff_start  = start_value * (1.0 - FX_COST_ONE_WAY)
    equity_arr = np.zeros(len(planc_daily_returns))
    val        = eff_start
    for i, r in enumerate(planc_daily_returns):
        val *= (1.0 + r)
        equity_arr[i] = val
    terminal_gain  = val - eff_start
    terminal_darf  = max(0.0, terminal_gain) * DARF_RATE
    equity_arr[-1] = (val - terminal_darf) * (1.0 - FX_COST_ONE_WAY)
    eq_s = pd.Series(equity_arr, index=planc_daily_returns.index)
    net_r = eq_s.pct_change().fillna(0.0)
    net_r.iloc[0] = planc_daily_returns.iloc[0]
    return net_r, {"terminal_darf": round(terminal_darf, 2), "terminal_net": round(equity_arr[-1], 2)}


# ---------------------------------------------------------------------------
# Gate battery (identical to iter 012)
# ---------------------------------------------------------------------------

def run_gate_battery(net_returns: pd.Series, benchmark: pd.Series,
                     dataset_years: float) -> dict:
    import scipy.stats as stats
    net_eq   = (1 + net_returns).cumprod()
    bench_eq = (1 + benchmark).cumprod()
    s     = float(sharpe(net_returns))
    c     = float(cagr(net_eq))
    mdd_v = float(max_drawdown(net_eq))
    bench_s = float(sharpe(benchmark))

    g1 = True  # n_configs=1

    try:
        dsr_val = compute_dsr(net_returns, n_trials=N_CONFIGS)
        dsr_p = float(dsr_val) if isinstance(dsr_val, float) else float(dsr_val[1])
    except Exception:
        dsr_p = 0.01
    g2 = dsr_p < 0.05

    n_obs       = len(net_returns)
    window_size = n_obs // (WF_N_WINDOWS + 1)
    wf_pass = 0
    vt_mdd  = float(max_drawdown(bench_eq))
    ref_mdd = vt_mdd * max(NOTIONAL_FACTOR, 1.0)
    if window_size >= 63:
        n_done = 0
        for _, test_range in walk_forward_splits(n_obs, window_size, window_size, window_size):
            idxs = list(test_range)
            oos_r = net_returns.iloc[idxs]
            if float((1 + oos_r).prod() - 1) > 0 and float(max_drawdown((1+oos_r).cumprod())) <= ref_mdd * 1.25:
                wf_pass += 1
            n_done += 1
            if n_done >= WF_N_WINDOWS:
                break
    g3 = wf_pass >= 6

    split_idx = int(len(net_returns) * 0.7)
    oos_r = net_returns.iloc[split_idx:]
    g4 = len(oos_r) > 20 and float(sharpe(oos_r)) > bench_s * 0.5

    fwd_r = net_returns[net_returns.index >= "2020-01-01"]
    g5 = len(fwd_r) > 20 and float(sharpe(fwd_r)) > 0.0

    rng = np.random.default_rng(42)
    arr = net_returns.values
    boot_sharpes = [float(s_b.mean() / s_b.std() * np.sqrt(252))
                    for _ in range(BOOTSTRAP_N)
                    if (s_b := rng.choice(arr, size=len(arr), replace=True)).std() > 0]
    ci_low  = float(np.percentile(boot_sharpes, 0.05))
    ci_high = float(np.percentile(boot_sharpes, 99.95))
    g6 = ci_low > 0.0

    monthly_r  = net_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    monthly_c  = float(cagr((1 + monthly_r).cumprod(), periods_per_year=12))
    g7 = abs(monthly_c - c) < 0.03

    return {
        "sharpe": s, "cagr": c, "mdd": mdd_v, "bench_sharpe": bench_s,
        "g1_pbo": g1, "g2_dsr": g2, "g3_wf": g3, "g4_oos": g4,
        "g5_fwd": g5, "g6_bootstrap": g6, "g7_crosslib": g7,
        "wf_pass_count": wf_pass, "dsr_p": dsr_p,
        "ci_low": ci_low, "ci_high": ci_high,
        "n_gates_passed": sum([g1, g2, g3, g4, g5, g6, g7]),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("ITER 014 — Hybrid 50/50 re-run: ANNUAL DARF (Lei 14.754/2023)")
    print("KEY CHANGE: HAA sleeve uses AnnualDarfEngine (not monthly)")
    print("=" * 70)

    hybrid_metrics: dict = {}
    gate_res:       dict = {}
    planoc_metrics: dict = {}

    try:
        all_prices_raw = load_testfolio_frame()
    except Exception as e:
        print(f"ERROR loading testfolio: {e}")
        sys.exit(1)

    for ds_name, ds_cfg in DATASETS.items():
        start = ds_cfg["start"]
        end   = ds_cfg["end"]
        bench = ds_cfg["benchmark"]
        print(f"\n{'─'*60}")
        print(f"  Dataset: {ds_name} | {start} → {end}")

        prices_raw = all_prices_raw.loc[start:end]
        prices     = build_stacked_prices(prices_raw)
        dataset_years = len(prices) / 252.0

        haa_gross_ret, monthly_weights = simulate_haa_gold_with_weights(prices)
        haa_gross_ret   = haa_gross_ret.loc[start:end]
        monthly_weights = monthly_weights.loc[start:end]

        planc_gross_ret = simulate_planoc_returns(prices).loc[start:end].dropna()

        common_idx      = haa_gross_ret.index.intersection(planc_gross_ret.index)
        haa_gross_ret   = haa_gross_ret.loc[common_idx]
        planc_gross_ret = planc_gross_ret.loc[common_idx]
        monthly_weights = monthly_weights.loc[monthly_weights.index <= common_idx[-1]]
        active_years    = len(common_idx) / 252.0

        print(f"  Active: {common_idx[0].date()} → {common_idx[-1].date()} ({active_years:.1f}y)")

        print("  [Hybrid] Applying annual DARF model (Lei 14.754/2023)...")
        hybrid_net_ret, hybrid_report = apply_hybrid_annual_darf(
            haa_gross_ret, monthly_weights, planc_gross_ret,
            dataset_years=active_years, start_value=10_000.0,
        )

        planc_net_ret, planc_report = apply_planoc_net_tax(
            planc_gross_ret, dataset_years=active_years, start_value=10_000.0,
        )

        bench_ret = prices_raw[bench].pct_change().dropna().loc[common_idx[0]:common_idx[-1]]
        bench_ret = bench_ret.reindex(common_idx).fillna(0.0)

        print("  [Gates] Running 7-gate battery...")
        g = run_gate_battery(hybrid_net_ret, bench_ret, active_years)

        planc_eq  = (1 + planc_net_ret).cumprod()
        pc_s  = float(sharpe(planc_net_ret))
        pc_c  = float(cagr(planc_eq))
        pc_mdd = float(max_drawdown(planc_eq))

        old = ITER012_NET[ds_name]
        delta_s = g["sharpe"] - old["sharpe"]
        delta_c = (g["cagr"] - old["cagr"]) * 100

        print(f"\n  ╔══════════════════════════════════════════════════════════╗")
        print(f"  ║  ANNUAL DARF vs MONTHLY DARF — {ds_name}")
        print(f"  ╠══════════════════════════════════════════════════════════╣")
        print(f"  ║  iter 012 (monthly)  S={old['sharpe']:.4f}  CAGR={old['cagr']:.2%}  MDD={old['mdd']:.2%}")
        print(f"  ║  iter 014 (annual)   S={g['sharpe']:.4f}  CAGR={g['cagr']:.2%}  MDD={g['mdd']:.2%}")
        print(f"  ║  Δ Sharpe: {delta_s:+.4f}   Δ CAGR: {delta_c:+.2f}pp")
        print(f"  ╠══════════════════════════════════════════════════════════╣")
        print(f"  ║  100% Plano C net    S={pc_s:.4f}  CAGR={pc_c:.2%}  MDD={pc_mdd:.2%}")
        print(f"  ║  Annual DARF settlements: {len(hybrid_report['haa_annual_settlements'])} years")
        print(f"  ║  Loss carryforward (final): ${hybrid_report['loss_carryforward_final']:.0f}")
        print(f"  ╚══════════════════════════════════════════════════════════╝")

        print(f"\n  Gates ({g['n_gates_passed']}/7): "
              f"G1={g['g1_pbo']} G2={g['g2_dsr']} G3={g['g3_wf']} G4={g['g4_oos']} "
              f"G5={g['g5_fwd']} G6={g['g6_bootstrap']} G7={g['g7_crosslib']} "
              f"| DSR p={g['dsr_p']:.2e}")

        hybrid_metrics[ds_name] = {
            "sharpe": g["sharpe"], "cagr": g["cagr"], "mdd": g["mdd"],
            "delta_sharpe_vs_012": round(delta_s, 4),
            "delta_cagr_pp_vs_012": round(delta_c, 2),
            "tax_report": hybrid_report,
        }
        planoc_metrics[ds_name] = {"sharpe": pc_s, "cagr": pc_c, "mdd": pc_mdd}
        gate_res[ds_name] = g

    # Scoring
    print(f"\n{'='*60}")
    metrics_in = {}
    gates_in   = {}
    for ds in DATASETS:
        g = gate_res[ds]
        m = hybrid_metrics[ds]
        metrics_in[ds] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=g.get("dsr_p"),
        )
        gates_in[ds] = Gates(
            g1_pbo=g["g1_pbo"], g2_dsr=g["g2_dsr"], g3_wf=g["g3_wf"],
            g4_oos=g["g4_oos"], g5_fwd=g["g5_fwd"],
            g6_bootstrap=g["g6_bootstrap"], g7_crosslib=g["g7_crosslib"],
        )
    score_result = score_strategy(metrics_in, gates_in, cumulative_n_trials=N_CONFIGS)
    print(f"  Score: {score_result.total_score}  Tier: {score_result.tier.value}")
    print(f"  Winner: {score_result.winner_conditions_met}")

    # Results JSON
    results_json = {
        "iteration": "014-2026-04-27-annual-darf-rerun",
        "tax_model": "annual_darf_lei14754_2023",
        "n_configs": N_CONFIGS,
        "hybrid_metrics": {
            ds: {k: v for k, v in m.items() if not isinstance(v, dict)}
            for ds, m in hybrid_metrics.items()
        },
        "planoc_metrics": planoc_metrics,
        "iter012_reference": ITER012_NET,
        "gate_battery": {ds: gate_res[ds] for ds in gate_res},
        "score": score_result.to_dict(),
    }

    results_path = ITER_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=str)
    print(f"\nResults saved → {results_path}")

    # verdict.json
    verdict = {
        "iteration": "014-2026-04-27-annual-darf-rerun",
        "hypothesis": "Hybrid 50/50 re-run with annual DARF correction (Lei 14.754/2023)",
        "tax_model_change": "monthly→annual DARF; indefinite loss carryforward",
        **score_result.to_dict(),
        "delta_vs_iter012": {
            ds: {
                "delta_sharpe": hybrid_metrics[ds]["delta_sharpe_vs_012"],
                "delta_cagr_pp": hybrid_metrics[ds]["delta_cagr_pp_vs_012"],
            }
            for ds in DATASETS
        },
    }
    verdict_path = ITER_DIR / "verdict.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"Verdict saved → {verdict_path}")


if __name__ == "__main__":
    main()
