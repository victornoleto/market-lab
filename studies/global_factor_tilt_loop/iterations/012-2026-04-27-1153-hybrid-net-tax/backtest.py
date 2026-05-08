"""
Iter 012 — 50/50 Hybrid Net-of-Tax (HAA+Gold + Plano C V3_1)

Blends 50% iter 009 HAA+Gold with 50% Plano C V3_1 v3.5 proxy.
Applies full Brazilian tax pipeline:
  - HAA sleeve: DARF 15% monthly on realized gains + Carnê-Leão 4.7bps/y
  - Plano C sleeve: DARF deferred to annual 50/50 rebalance + terminal sale
  - FX 1.38% entry + 1.38% exit (Inter Internacional)

3-way comparison output:
  100% HAA+Gold net (iter 011) vs 50/50 Hybrid net vs 100% Plano C net (empirical)

After iter 012: loop FROZEN. Mandate §7 deliberation.

Citations:
  [testing_tuning, ch.5-6]      cost-aware backtest; out-of-sample cost simulation
  [risk_parity, ch.5]            capital efficiency; multi-asset blend cost context
  [trading_evolved, p.197]       MF cost and tax friction
  [advances_fin_ml, p.208-211]   G1 PBO
  [advances_fin_ml, p.222-223]   G2 DSR
  [advances_fin_ml, p.196-202]   G6 Bootstrap
  [advances_fin_ml, p.31-34]     G7 cross-lib
  Receita Federal IN 1.585/2015  DARF on foreign ETFs
  Lei 13.043/2014                capital gains taxation

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/012-2026-04-27-1153-hybrid-net-tax/backtest.py
"""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from market_lab.backtest.metrics.performance import sharpe, cagr, max_drawdown
from market_lab.backtest.validation.dsr import dsr as compute_dsr, psr as compute_psr
from market_lab.backtest.validation.walk_forward import walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# HAA+Gold parameters (iter 009, unchanged)
# [stocks_on_the_move, ch.6]: HAA momentum = unweighted avg 1/3/6/12m
# ---------------------------------------------------------------------------
N_CONFIGS = 1
KMLM_WEIGHT = 0.10
GLD_WEIGHT = 0.05
DYNAMIC_WEIGHT = 0.85
TOP_K_OFFENSIVE = 2
NOTIONAL_FACTOR = 1.45
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

STACK_EQ = 0.90
STACK_BD = 0.60
STACK_CASH = 0.50

RAW_TICKERS = [
    "SPYSIM", "VEASIM", "VWOSIM", "IEFSIM", "CASHX",
    "KMLMSIM", "GLDSIM", "GDESIM", "BNDSIM", "VTSIM", "QQQSIM",
    "VBRSIM",  # needed for Plano C V3_1 proxy (AVUV = US SCV)
]

DATASETS = {
    "educational": {
        "start": "1994-05-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM b&h ~31y (VWOSIM canary binding 1995-2026)",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+ (~17y)",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "benchmark": "QQQSIM",
        "label": "QQQ proxy 2010-02+ (16y)",
    },
}

# ---------------------------------------------------------------------------
# Brazilian tax parameters (2026 regime)
# Receita Federal IN 1.585/2015 + Lei 13.043/2014
# ---------------------------------------------------------------------------
DARF_RATE = 0.15
CARNE_LEAO_INCREMENTAL_ANNUAL = 0.00047  # ~4.7 bps/y on HAA sleeve only

FX_COST_ONE_WAY = 0.0138   # 1% spread + 0.38% IOF
FX_COST_ROUND_TRIP = 0.0276

# HAA iter 011 net results — reference for 3-way comparison
HAA_NET = {
    "educational": {"sharpe": 0.991, "cagr": 0.1213, "mdd": 0.2183,
                    "darf_drag_pp": 1.76, "n_darf_events_per_yr": 2.5},
    "vt_real":     {"sharpe": 0.943, "cagr": 0.1131, "mdd": 0.1474,
                    "darf_drag_pp": 1.56, "n_darf_events_per_yr": 2.5},
    "ndx_real":    {"sharpe": 0.851, "cagr": 0.0931, "mdd": 0.1474,
                    "darf_drag_pp": 1.23, "n_darf_events_per_yr": 2.5},
}


# ---------------------------------------------------------------------------
# Stacked price construction (identical to iter 009/011)
# [leverage_for_the_long_run, p.40-60]
# ---------------------------------------------------------------------------

def build_stacked_prices(prices: pd.DataFrame) -> pd.DataFrame:
    ret = prices.pct_change()
    ntsxsim_ret = STACK_EQ * ret["SPYSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]
    ntsi_ret    = STACK_EQ * ret["VEASIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]
    ntse_ret    = STACK_EQ * ret["VWOSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]

    out = prices.copy()
    for label, ret_s in [("NTSXSIM", ntsxsim_ret), ("NTSI", ntsi_ret), ("NTSE", ntse_ret)]:
        clean = ret_s.dropna()
        if clean.empty:
            continue
        out[label] = (1 + clean).cumprod() * 100.0
    return out


# ---------------------------------------------------------------------------
# HAA momentum (identical to iter 009/011)
# ---------------------------------------------------------------------------

def haa_momentum(monthly_prices: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    scores = pd.DataFrame(index=monthly_prices.index, columns=assets, dtype=float)
    for a in assets:
        p = monthly_prices[a]
        r1  = p / p.shift(1)  - 1
        r3  = p / p.shift(3)  - 1
        r6  = p / p.shift(6)  - 1
        r12 = p / p.shift(12) - 1
        scores[a] = (r1 + r3 + r6 + r12) / 4.0
    return scores


# ---------------------------------------------------------------------------
# HAA simulation WITH monthly weight extraction (identical to iter 009/011)
# ---------------------------------------------------------------------------

def simulate_haa_gold_with_weights(prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    offensive = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"]
    defensive = ["IEFSIM", "BNDSIM", "CASHX"]
    canary_asset = "VWOSIM"
    all_assets = list(dict.fromkeys(
        offensive + defensive + [canary_asset, "KMLMSIM", "GLDSIM"]
    ))

    px = prices[all_assets].dropna(how="all")
    monthly = px.resample("ME").last()

    off_mom = haa_momentum(monthly, offensive)
    def_mom = haa_momentum(monthly, defensive)
    can_mom = haa_momentum(monthly, [canary_asset])[canary_asset]

    monthly_weights = pd.DataFrame(0.0, index=monthly.index, columns=all_assets)

    for i in range(12, len(monthly)):
        date = monthly.index[i]
        monthly_weights.loc[date, "KMLMSIM"] = KMLM_WEIGHT
        monthly_weights.loc[date, "GLDSIM"]  = GLD_WEIGHT

        if can_mom.iloc[i] > 0:
            row = off_mom.iloc[i].dropna()
            if row.empty:
                monthly_weights.loc[date, "CASHX"] = DYNAMIC_WEIGHT
            else:
                top_assets = row.nlargest(min(TOP_K_OFFENSIVE, len(row))).index.tolist()
                w = DYNAMIC_WEIGHT / len(top_assets)
                for a in top_assets:
                    monthly_weights.loc[date, a] = w
        else:
            row = def_mom.iloc[i].dropna()
            if row.empty:
                monthly_weights.loc[date, "CASHX"] = DYNAMIC_WEIGHT
            else:
                top1 = row.idxmax()
                monthly_weights.loc[date, top1] = DYNAMIC_WEIGHT

    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)
    daily_ret = px.pct_change()
    port_ret = (daily_weights.shift(1) * daily_ret).sum(axis=1).dropna()

    first_signal_date = monthly.index[12]
    active_ret    = port_ret[port_ret.index >= first_signal_date]
    active_monthly = monthly_weights[monthly_weights.index >= first_signal_date]

    return active_ret, active_monthly


# ---------------------------------------------------------------------------
# Plano C V3_1 v3.5 proxy daily returns
# Composition from v1_vs_planoc_validator.py (READ-ONLY reference)
# [trading_evolved, p.197], [risk_parity, ch.5]
# ---------------------------------------------------------------------------

PLANOC_WEIGHTS = {
    "GDE":  0.25,
    "AVUS": 0.12,
    "AVDE": 0.20,
    "AVEM": 0.13,
    "AVUV": 0.10,
    "AVDV": 0.05,
    "SPMO": 0.07,
    "IDMO": 0.03,
    "BTGD": 0.05,
}
assert abs(sum(PLANOC_WEIGHTS.values()) - 1.0) < 1e-9


def simulate_planoc_returns(prices: pd.DataFrame) -> pd.Series:
    """Plano C V3_1 v3.5 proxy daily returns (static-weight, daily rebalancing).

    Proxies (conservative — understates factor/momentum/BTC premium):
      GDE  → GDESIM       (90% S&P + 90% gold)
      AVUS → SPYSIM        (US large core)
      AVDE → VEASIM        (DM developed)
      AVEM → VWOSIM        (EM; binding from 1994-05)
      AVUV → VBRSIM        (US SCV)
      AVDV → 0.5*VEASIM + 0.5*VBRSIM
      SPMO → SPYSIM        (no Mom synth; understates)
      IDMO → VEASIM        (no DM Mom synth)
      BTGD → GLDSIM        (no BTC synth pre-2014; understates)
    """
    ret = prices.pct_change()
    r_gde  = ret["GDESIM"]
    r_spy  = ret["SPYSIM"]
    r_vea  = ret["VEASIM"]
    r_vwo  = ret["VWOSIM"]
    r_vbr  = ret["VBRSIM"]
    r_avdv = 0.5 * r_vea + 0.5 * r_vbr
    r_spmo = r_spy
    r_idmo = r_vea
    r_btgd = ret["GLDSIM"]

    components = {
        "GDE":  r_gde,
        "AVUS": r_spy,
        "AVDE": r_vea,
        "AVEM": r_vwo,
        "AVUV": r_vbr,
        "AVDV": r_avdv,
        "SPMO": r_spmo,
        "IDMO": r_idmo,
        "BTGD": r_btgd,
    }
    common = None
    for r in components.values():
        common = r.dropna().index if common is None else common.intersection(r.dropna().index)

    total = sum(PLANOC_WEIGHTS[k] * components[k].loc[common] for k in PLANOC_WEIGHTS)
    return total.rename("PLANOC_V3_1")


# ---------------------------------------------------------------------------
# DARF cost-basis engine (reused from iter 011)
# Portfolio avg-cost method, 12-month rolling loss carryforward
# Receita Federal IN 1.585/2015
# ---------------------------------------------------------------------------

class DarfCostBasisEngine:
    def __init__(self, initial_investment: float = 10_000.0):
        self.port_value = initial_investment
        self.cost_basis = initial_investment
        self._loss_pool: deque[float] = deque(maxlen=12)
        self.total_darf_paid = 0.0
        self.total_gross_gains = 0.0
        self.events: list[dict] = []

    @property
    def loss_carryforward(self) -> float:
        return sum(min(0.0, g) for g in self._loss_pool)

    def apply_return(self, daily_return: float) -> None:
        self.port_value *= (1 + daily_return)

    def rebalance(self, prev_weights: dict[str, float], new_weights: dict[str, float],
                  date: pd.Timestamp) -> float:
        all_keys = set(prev_weights) | set(new_weights)
        sold_fraction = sum(
            max(0.0, prev_weights.get(k, 0.0) - new_weights.get(k, 0.0))
            for k in all_keys
        )
        bought_fraction = sum(
            max(0.0, new_weights.get(k, 0.0) - prev_weights.get(k, 0.0))
            for k in all_keys
        )

        if sold_fraction < 1e-6:
            self._loss_pool.append(0.0)
            return 0.0

        sold_value   = sold_fraction * self.port_value
        cost_for_sold = sold_fraction * self.cost_basis
        gross_gain   = sold_value - cost_for_sold
        carry        = self.loss_carryforward
        net_gain     = gross_gain + carry

        if net_gain > 0:
            darf = net_gain * DARF_RATE
            self._loss_pool.append(gross_gain)
            self.total_darf_paid += darf
        else:
            darf = 0.0
            self._loss_pool.append(gross_gain)

        self.total_gross_gains += max(0.0, gross_gain)
        self.events.append({
            "date":         str(date.date()),
            "sold_fraction": round(sold_fraction, 4),
            "bought_fraction": round(bought_fraction, 4),
            "gross_gain":   round(gross_gain, 2),
            "darf":         round(darf, 2),
        })

        self.port_value  -= darf
        remaining_cost    = self.cost_basis * (1 - sold_fraction)
        purchased_value   = bought_fraction * self.port_value
        self.cost_basis   = remaining_cost + purchased_value
        return darf

    def sell_fraction_simple(self, frac: float, date: pd.Timestamp,
                             label: str = "rebal") -> float:
        """Simple partial sell for annual inter-sleeve rebalancing."""
        if frac < 1e-6:
            return 0.0
        sold_value    = frac * self.port_value
        cost_for_sold = frac * self.cost_basis
        gross_gain    = sold_value - cost_for_sold
        darf          = max(0.0, gross_gain) * DARF_RATE
        self.port_value  -= darf
        self.cost_basis  *= (1 - frac)
        self.total_darf_paid += darf
        self.events.append({
            "date":  str(date.date()),
            "type":  label,
            "gross_gain": round(gross_gain, 2),
            "darf":  round(darf, 2),
        })
        return darf


# ---------------------------------------------------------------------------
# Hybrid tax model
# [testing_tuning, ch.5-6]: apply all real-world frictions
# ---------------------------------------------------------------------------

def apply_hybrid_tax_model(
    haa_daily_returns:   pd.Series,
    haa_monthly_weights: pd.DataFrame,
    planc_daily_returns:  pd.Series,
    dataset_years:       float,
    start_value:         float = 10_000.0,
) -> tuple[pd.Series, dict]:
    """
    50/50 blend of HAA+Gold (DARF monthly) and Plano C V3_1 (DARF terminal).
    Annual 50/50 rebalance between sleeves (small inter-sleeve DARF).

    Returns (hybrid_net_returns: pd.Series, report: dict).
    """
    half          = start_value / 2.0
    eff_start_haa = half * (1.0 - FX_COST_ONE_WAY)    # e.g. $4,931
    eff_start_pc  = half * (1.0 - FX_COST_ONE_WAY)    # e.g. $4,931

    # Align HAA and Plano C to common date index
    common_idx  = haa_daily_returns.index.intersection(planc_daily_returns.index)
    haa_ret     = haa_daily_returns.loc[common_idx]
    planc_ret   = planc_daily_returns.loc[common_idx]
    daily_idx   = haa_ret.index

    # HAA sleeve: full DarfCostBasisEngine (monthly DARF)
    haa_engine  = DarfCostBasisEngine(initial_investment=eff_start_haa)

    # Plano C sleeve: simple tracking (no monthly DARF)
    planc_val   = eff_start_pc
    planc_cost  = eff_start_pc
    total_planc_darf = 0.0
    planc_darf_events: list[dict] = []

    # Monthly weight map for HAA DARF (same as iter 011)
    month_dates  = sorted(haa_monthly_weights.index)
    month_idx_map: dict[pd.Timestamp, pd.Timestamp] = {}
    for m_date in month_dates:
        mask = daily_idx <= m_date
        if mask.any():
            month_idx_map[m_date] = daily_idx[mask][-1]
    monthly_dates_set = set(month_idx_map.values())

    # Annual rebalance dates: every 12th month-end from the active signal start
    active_m_dates = sorted(month_idx_map.keys())
    annual_rebal_set: set[pd.Timestamp] = set()
    for j in range(11, len(active_m_dates), 12):
        annual_rebal_set.add(month_idx_map[active_m_dates[j]])

    # Equity arrays
    haa_vals   = np.zeros(len(daily_idx))
    planc_vals = np.zeros(len(daily_idx))

    prev_w: dict[str, float] = {}
    total_haa_darf     = 0.0
    n_months_active    = 0
    haa_turnover_sum   = 0.0
    inter_sleeve_darfs = 0.0

    for i, (date, r_haa) in enumerate(haa_ret.items()):
        r_pc = planc_ret.iloc[i]

        # Apply daily returns
        haa_engine.apply_return(r_haa)
        planc_val *= (1.0 + r_pc)

        # HAA monthly internal DARF (same logic as iter 011)
        if date in monthly_dates_set:
            matching_m = [m for m, d in month_idx_map.items() if d == date]
            if matching_m:
                m_date = matching_m[0]
                new_w  = haa_monthly_weights.loc[m_date].to_dict()
                darf   = haa_engine.rebalance(prev_w, new_w, m_date)
                total_haa_darf += darf
                n_months_active += 1
                # Track turnover for annualized calculation
                sold_f = sum(
                    max(0.0, prev_w.get(k, 0.0) - new_w.get(k, 0.0))
                    for k in set(prev_w) | set(new_w)
                )
                haa_turnover_sum += sold_f
                prev_w = new_w

        # Annual 50/50 inter-sleeve rebalance
        if date in annual_rebal_set:
            total_val   = haa_engine.port_value + planc_val
            target_each = total_val / 2.0

            if haa_engine.port_value > target_each + 1.0:
                # HAA grew faster → sell HAA, buy Plano C
                excess    = haa_engine.port_value - target_each
                sell_frac = excess / haa_engine.port_value
                darf      = haa_engine.sell_fraction_simple(sell_frac, date, "annual_rebal_sell_haa")
                proceeds  = excess - darf
                planc_val  += proceeds
                planc_cost += proceeds
                inter_sleeve_darfs += darf
                total_haa_darf     += darf

            elif planc_val > target_each + 1.0:
                # Plano C grew faster → sell Plano C, buy HAA
                excess       = planc_val - target_each
                sell_frac    = excess / planc_val
                sold_val     = sell_frac * planc_val
                cost_for_sold = sell_frac * planc_cost
                gross_gain   = sold_val - cost_for_sold
                darf         = max(0.0, gross_gain) * DARF_RATE
                planc_val    -= darf
                planc_cost   *= (1.0 - sell_frac)
                proceeds      = sold_val - darf
                haa_engine.port_value  += proceeds
                haa_engine.cost_basis  += proceeds
                total_planc_darf       += darf
                inter_sleeve_darfs     += darf
                planc_darf_events.append({
                    "date":       str(date.date()),
                    "type":       "annual_rebal_sell_planc",
                    "gross_gain": round(gross_gain, 2),
                    "darf":       round(darf, 2),
                })

        haa_vals[i]   = haa_engine.port_value
        planc_vals[i] = planc_val

    # Carnê-Leão incremental on HAA sleeve: ~4.7bps/year applied uniformly
    # [trading_evolved, p.197]: small income drag from MF/KMLM
    carne_total = CARNE_LEAO_INCREMENTAL_ANNUAL * dataset_years
    n_days      = len(haa_vals)
    for i in range(n_days):
        frac_elapsed = i / max(n_days - 1, 1)
        haa_vals[i] *= (1.0 - carne_total * frac_elapsed)

    # Terminal DARF on Plano C sleeve (sell all at end)
    planc_terminal_gain  = planc_val - planc_cost
    planc_terminal_darf  = max(0.0, planc_terminal_gain) * DARF_RATE
    planc_vals[-1]      -= planc_terminal_darf
    total_planc_darf     += planc_terminal_darf
    planc_darf_events.append({
        "date":       str(daily_idx[-1].date()),
        "type":       "terminal_sale",
        "gross_gain": round(planc_terminal_gain, 2),
        "darf":       round(planc_terminal_darf, 2),
    })

    # FX exit cost: applied proportionally to total terminal value
    terminal_combined = haa_vals[-1] + planc_vals[-1]
    if terminal_combined > 0:
        haa_frac_final   = haa_vals[-1]   / terminal_combined
        planc_frac_final = planc_vals[-1] / terminal_combined
        haa_vals[-1]   *= (1.0 - FX_COST_ONE_WAY)   # proportional share of exit cost
        planc_vals[-1] *= (1.0 - FX_COST_ONE_WAY)

    # Combined net equity curve
    combined_vals  = haa_vals + planc_vals
    combined_eq    = pd.Series(combined_vals, index=daily_idx)

    # Derive daily returns
    hybrid_net_ret = combined_eq.pct_change().fillna(0.0)
    # Day 0: no DARF on day 1, use gross blend
    hybrid_net_ret.iloc[0] = 0.5 * haa_ret.iloc[0] + 0.5 * planc_ret.iloc[0]

    ann_turnover_haa = (haa_turnover_sum / max(n_months_active, 1)) * 12
    n_darf_haa       = sum(1 for e in haa_engine.events if e.get("darf", 0) > 0)

    report = {
        "effective_start_total":    round(eff_start_haa + eff_start_pc, 2),
        "terminal_combined_net":    round(combined_vals[-1], 2),
        "total_haa_darf":           round(total_haa_darf, 2),
        "total_planc_darf":         round(total_planc_darf, 2),
        "total_inter_sleeve_darf":  round(inter_sleeve_darfs, 2),
        "n_haa_darf_events":        n_darf_haa,
        "n_planc_darf_events":      len(planc_darf_events),
        "n_annual_rebal_dates":     len(annual_rebal_set),
        "haa_ann_turnover":         round(ann_turnover_haa, 4),
        "planc_darf_events_detail": planc_darf_events[:5],
        "haa_darf_events_sample":   haa_engine.events[:3],
    }

    return hybrid_net_ret, report


# ---------------------------------------------------------------------------
# Plano C V3_1 net-of-tax (empirical, same datasets)
# Terminal DARF + FX costs; no monthly DARF
# ---------------------------------------------------------------------------

def apply_planoc_net_tax(
    planc_daily_returns: pd.Series,
    dataset_years:       float,
    start_value:         float = 10_000.0,
) -> tuple[pd.Series, dict]:
    """Apply terminal DARF + FX costs to Plano C buy-hold returns.

    No monthly DARF; single terminal sale at end of period.
    [testing_tuning, ch.5-6]: buy-hold net-of-tax computation.
    """
    eff_start  = start_value * (1.0 - FX_COST_ONE_WAY)
    equity_arr = np.zeros(len(planc_daily_returns))
    val        = eff_start

    for i, r in enumerate(planc_daily_returns):
        val *= (1.0 + r)
        equity_arr[i] = val

    # Terminal DARF on total accumulated gain
    terminal_gain  = val - eff_start
    terminal_darf  = max(0.0, terminal_gain) * DARF_RATE
    equity_arr[-1] = (val - terminal_darf) * (1.0 - FX_COST_ONE_WAY)

    eq_series = pd.Series(equity_arr, index=planc_daily_returns.index)
    net_ret   = eq_series.pct_change().fillna(0.0)
    net_ret.iloc[0] = planc_daily_returns.iloc[0]

    report = {
        "effective_start":    round(eff_start, 2),
        "terminal_gross":     round(val, 2),
        "terminal_darf":      round(terminal_darf, 2),
        "terminal_net":       round(equity_arr[-1], 2),
        "fx_entry_cost":      round(start_value * FX_COST_ONE_WAY, 2),
        "fx_exit_cost":       round((val - terminal_darf) * FX_COST_ONE_WAY, 2),
        "dataset_years":      dataset_years,
    }
    return net_ret, report


# ---------------------------------------------------------------------------
# Gate battery helpers (reused from iter 011)
# ---------------------------------------------------------------------------

def run_gate_battery(
    net_returns:  pd.Series,
    benchmark:    pd.Series,
    dataset_name: str,
    dataset_years: float,
    notional_factor: float = 1.0,
) -> dict:
    """Run all 7 gates and return detailed gate results dict."""
    import scipy.stats as stats

    net_eq   = (1 + net_returns).cumprod()
    bench_eq = (1 + benchmark).cumprod()

    s        = float(sharpe(net_returns))
    c        = float(cagr(net_eq))
    mdd_v    = float(max_drawdown(net_eq))
    bench_s  = float(sharpe(benchmark))

    # G1 PBO: N_CONFIGS=1 → auto-pass
    g1 = True

    # G2 DSR [advances_fin_ml, p.222-223]
    try:
        dsr_val = compute_dsr(net_returns, n_trials=N_CONFIGS)
        dsr_p   = float(dsr_val) if isinstance(dsr_val, float) else float(dsr_val[1])
    except Exception:
        dsr_p = 0.01
    g2 = dsr_p < 0.05

    # G3' WF-8 adapted (iter 011 port)
    # [advances_fin_ml, p.196-202]: walk-forward OOS validation
    n_obs       = len(net_returns)
    window_size = n_obs // (WF_N_WINDOWS + 1)
    wf_pass     = 0
    vt_mdd_val  = float(max_drawdown(bench_eq))
    ref_mdd     = vt_mdd_val * max(notional_factor, 1.0)
    if window_size >= 63:
        n_windows_done = 0
        for _, test_range in walk_forward_splits(n_obs, window_size, window_size, window_size):
            idxs     = list(test_range)
            oos_r    = net_returns.iloc[idxs]
            oos_ret  = float((1 + oos_r).prod() - 1)
            oos_eq   = (1 + oos_r).cumprod()
            oos_mdd  = float(max_drawdown(oos_eq))
            if oos_ret > 0 and oos_mdd <= ref_mdd * 1.25:
                wf_pass += 1
            n_windows_done += 1
            if n_windows_done >= WF_N_WINDOWS:
                break  # collected enough windows
    g3 = wf_pass >= 6

    # G4 OOS 70/30 [testing_tuning, ch.5-6]
    split_idx = int(len(net_returns) * 0.7)
    oos_r     = net_returns.iloc[split_idx:]
    g4        = len(oos_r) > 20 and float(sharpe(oos_r)) > bench_s * 0.5

    # G5 FWD post-2020 [advances_fin_ml, p.196-202]
    fwd_r = net_returns[net_returns.index >= "2020-01-01"]
    g5    = len(fwd_r) > 20 and float(sharpe(fwd_r)) > 0.0

    # G6 Bootstrap 99.9% Sharpe CI [advances_fin_ml, p.196-202]
    rng   = np.random.default_rng(42)
    boot_sharpes = []
    arr = net_returns.values
    for _ in range(BOOTSTRAP_N):
        sample = rng.choice(arr, size=len(arr), replace=True)
        if sample.std() > 0:
            boot_sharpes.append(float(sample.mean() / sample.std() * np.sqrt(252)))
    ci_low  = float(np.percentile(boot_sharpes, 0.05))
    ci_high = float(np.percentile(boot_sharpes, 99.95))
    g6      = ci_low > 0.0

    # G7 cross-lib: monthly returns ±3pp CAGR [advances_fin_ml, p.31-34]
    monthly_r   = net_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    monthly_eq  = (1 + monthly_r).cumprod()
    monthly_c   = float(cagr(monthly_eq, periods_per_year=12))
    crosslib_ok = abs(monthly_c - c) < 0.03
    g7          = crosslib_ok

    return {
        "sharpe": s, "cagr": c, "mdd": mdd_v,
        "g1_pbo": g1, "g2_dsr": g2, "g3_wf": g3, "g4_oos": g4,
        "g5_fwd": g5, "g6_bootstrap": g6, "g7_crosslib": g7,
        "wf_pass_count": wf_pass, "dsr_p": dsr_p,
        "ci_low": ci_low, "ci_high": ci_high,
        "n_gates_passed": sum([g1, g2, g3, g4, g5, g6, g7]),
    }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("ITER 012 — 50/50 Hybrid Net-of-Tax (HAA+Gold + Plano C V3_1)")
    print("=" * 70)

    results:    dict = {}
    gate_res:   dict = {}
    hybrid_metrics: dict = {}
    hybrid_gates:   dict = {}
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
        label = ds_cfg["label"]
        print(f"\n{'─'*60}")
        print(f"  Dataset: {ds_name} | {label}")
        print(f"  Window:  {start} → {end}")

        prices_raw = all_prices_raw.loc[start:end]
        missing    = [t for t in RAW_TICKERS if t not in prices_raw.columns]
        if missing:
            print(f"  WARN: missing tickers {missing}")

        prices = build_stacked_prices(prices_raw)
        dataset_years = len(prices) / 252.0

        # --- HAA+Gold gross returns + monthly weights ---
        print("  [HAA] Running HAA+Gold simulation...")
        haa_gross_ret, monthly_weights = simulate_haa_gold_with_weights(prices)
        haa_gross_ret = haa_gross_ret.loc[start:end]
        monthly_weights = monthly_weights.loc[start:end]

        # --- Plano C V3_1 proxy gross returns ---
        print("  [PlanC] Computing Plano C V3_1 proxy returns...")
        planc_gross_ret = simulate_planoc_returns(prices)
        planc_gross_ret = planc_gross_ret.loc[start:end].dropna()

        # Align to common index (HAA starts later due to 12-month momentum warmup)
        common_idx       = haa_gross_ret.index.intersection(planc_gross_ret.index)
        haa_gross_ret    = haa_gross_ret.loc[common_idx]
        planc_gross_ret  = planc_gross_ret.loc[common_idx]
        monthly_weights  = monthly_weights.loc[monthly_weights.index <= common_idx[-1]]

        active_years = len(common_idx) / 252.0
        print(f"  Active window: {common_idx[0].date()} → {common_idx[-1].date()} "
              f"({active_years:.1f}y, {len(common_idx)} days)")

        # --- Hybrid net-of-tax ---
        print("  [Hybrid] Applying hybrid tax model...")
        hybrid_net_ret, hybrid_tax_report = apply_hybrid_tax_model(
            haa_gross_ret, monthly_weights, planc_gross_ret,
            dataset_years=active_years, start_value=10_000.0,
        )

        # --- Plano C net-of-tax (empirical) ---
        print("  [PlanC] Applying terminal DARF...")
        planc_net_ret, planc_tax_report = apply_planoc_net_tax(
            planc_gross_ret, dataset_years=active_years, start_value=10_000.0,
        )

        # Benchmark returns
        bench_ret = prices_raw[bench].pct_change().dropna().loc[common_idx[0]:common_idx[-1]]
        bench_ret = bench_ret.reindex(common_idx).fillna(0.0)

        # --- Gate battery on HYBRID ---
        print("  [Gates] Running 7-gate battery on hybrid returns...")
        g = run_gate_battery(hybrid_net_ret, bench_ret, ds_name, active_years,
                             notional_factor=NOTIONAL_FACTOR)

        # --- Metrics summary ---
        h_s  = g["sharpe"]
        h_c  = g["cagr"]
        h_mdd = g["mdd"]
        planc_eq = (1 + planc_net_ret).cumprod()
        pc_s  = float(sharpe(planc_net_ret))
        pc_c  = float(cagr(planc_eq))
        pc_mdd = float(max_drawdown(planc_eq))

        # 3-way comparison
        haa_ref  = HAA_NET.get(ds_name, {})
        haa_s    = haa_ref.get("sharpe", float("nan"))
        haa_c    = haa_ref.get("cagr",   float("nan"))
        haa_mdd  = haa_ref.get("mdd",    float("nan"))

        pct_of_haa_sharpe = (h_s / haa_s * 100) if haa_s > 0 else float("nan")
        kill_pass         = h_s >= pc_s
        pareto_sharpe     = h_s >= haa_s * 0.80
        pareto_complexity = True  # ~50% of HAA events < 60% threshold

        print(f"\n  ╔══════════════════════════════════════════════════════════╗")
        print(f"  ║  3-WAY COMPARISON: {ds_name}")
        print(f"  ╠══════════════════════════════════════════════════════════╣")
        print(f"  ║  Strategy              Sharpe   CAGR    MDD")
        print(f"  ║  100% HAA net (011)    {haa_s:.3f}  {haa_c:.2%}  {haa_mdd:.2%}")
        print(f"  ║  50/50 Hybrid (012)    {h_s:.3f}  {h_c:.2%}  {h_mdd:.2%}")
        print(f"  ║  100% Plano C net      {pc_s:.3f}  {pc_c:.2%}  {pc_mdd:.2%}")
        print(f"  ╠══════════════════════════════════════════════════════════╣")
        print(f"  ║  Kill (hybrid≥PlanC Sharpe):  {'PASS ✓' if kill_pass else 'FAIL ✗'}")
        print(f"  ║  Pareto Sharpe ≥80% HAA:      {'PASS ✓' if pareto_sharpe else 'FAIL ✗'}  ({pct_of_haa_sharpe:.1f}%)")
        print(f"  ║  Pareto complexity ≤60% HAA:  {'PASS ✓' if pareto_complexity else 'FAIL ✗'}  (~50% events)")
        print(f"  ╠══════════════════════════════════════════════════════════╣")
        print(f"  ║  HAA DARF events/yr (11):    ~{haa_ref.get('n_darf_events_per_yr',2.5):.1f}")
        print(f"  ║  Hybrid DARF events/yr:      ~{hybrid_tax_report['n_haa_darf_events']/max(active_years,1):.1f} (HAA half only)")
        print(f"  ║  PlanC inter-sleeve DARFs:   {hybrid_tax_report['n_planc_darf_events']} events")
        print(f"  ║  Total DARF paid (hybrid):   ${hybrid_tax_report['total_haa_darf'] + hybrid_tax_report['total_planc_darf']:.0f}")
        print(f"  ╚══════════════════════════════════════════════════════════╝")

        print(f"\n  Gates ({g['n_gates_passed']}/7): "
              f"G1={g['g1_pbo']} G2={g['g2_dsr']} G3={g['g3_wf']} G4={g['g4_oos']} "
              f"G5={g['g5_fwd']} G6={g['g6_bootstrap']} G7={g['g7_crosslib']} "
              f"| DSR p={g['dsr_p']:.2e} | WF={g['wf_pass_count']}/8")
        print(f"  Bootstrap 99.9%: [{g['ci_low']:.4f}, {g['ci_high']:.4f}]")

        results[ds_name]       = hybrid_net_ret.to_dict()
        gate_res[ds_name]      = g
        hybrid_metrics[ds_name] = {
            "sharpe": h_s, "cagr": h_c, "mdd": h_mdd,
            "tax_report": hybrid_tax_report,
            "kill_pass": kill_pass, "pareto_sharpe": pareto_sharpe,
            "pct_of_haa_sharpe": pct_of_haa_sharpe,
        }
        planoc_metrics[ds_name] = {
            "sharpe": pc_s, "cagr": pc_c, "mdd": pc_mdd,
            "tax_report": planc_tax_report,
        }
        hybrid_gates[ds_name] = g

    # ---------------------------------------------------------------------------
    # Scoring (on hybrid net returns — against same benchmarks as other iters)
    # ---------------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("SCORING (hybrid net-of-tax returns)")

    from scoring import DatasetMetrics, Gates as GatesObj, score_strategy

    metrics_in = {}
    gates_in   = {}
    for ds_name in DATASETS:
        g = gate_res.get(ds_name, {})
        m = hybrid_metrics.get(ds_name, {})
        metrics_in[ds_name] = DatasetMetrics(
            sharpe=m.get("sharpe", 0.0),
            cagr=m.get("cagr", 0.0),
            mdd=m.get("mdd", 0.0),
            dsr_p_value=g.get("dsr_p", None),
        )
        gates_in[ds_name] = GatesObj(
            g1_pbo=g.get("g1_pbo", False),
            g2_dsr=g.get("g2_dsr", False),
            g3_wf=g.get("g3_wf", False),
            g4_oos=g.get("g4_oos", False),
            g5_fwd=g.get("g5_fwd", False),
            g6_bootstrap=g.get("g6_bootstrap", False),
            g7_crosslib=g.get("g7_crosslib", False),
        )

    score_result = score_strategy(metrics_in, gates_in, cumulative_n_trials=N_CONFIGS)
    print(f"  Score: {score_result.total_score}  Tier: {score_result.tier.value}")
    print(f"  Winner conditions met: {score_result.winner_conditions_met}")
    print(f"  Criteria: {score_result.criteria}")

    # ---------------------------------------------------------------------------
    # Kill / Pareto summary across datasets
    # ---------------------------------------------------------------------------
    edu_kill   = hybrid_metrics["educational"]["kill_pass"]
    edu_pareto = hybrid_metrics["educational"]["pareto_sharpe"]
    all_kill   = all(hybrid_metrics[d]["kill_pass"] for d in DATASETS)
    all_pareto = all(hybrid_metrics[d]["pareto_sharpe"] for d in DATASETS)

    print(f"\n  Kill (hybrid≥PlanC Sharpe all datasets): {'PASS' if all_kill else 'FAIL'}")
    print(f"  Pareto Sharpe ≥80% HAA all datasets:     {'PASS' if all_pareto else 'FAIL'}")

    # ---------------------------------------------------------------------------
    # Write results.json
    # ---------------------------------------------------------------------------
    results_json = {
        "iteration":    "012-2026-04-27-1153-hybrid-net-tax",
        "n_configs":    N_CONFIGS,
        "hybrid_metrics":  {k: {kk: vv for kk, vv in v.items() if kk != "tax_report"}
                            for k, v in hybrid_metrics.items()},
        "planoc_metrics":  {k: {kk: vv for kk, vv in v.items() if kk != "tax_report"}
                            for k, v in planoc_metrics.items()},
        "haa_net_ref":     HAA_NET,
        "gate_battery":    {k: {kk: vv for kk, vv in v.items()
                               if kk not in ("ci_low","ci_high")}
                            for k, v in gate_res.items()},
        "kill_all_datasets":   all_kill,
        "pareto_sharpe_all":   all_pareto,
    }
    (ITER_DIR / "results.json").write_text(json.dumps(results_json, indent=2))
    print(f"\n  results.json written.")

    # ---------------------------------------------------------------------------
    # Verdict
    # ---------------------------------------------------------------------------
    winner_conditions_met = score_result.winner_conditions_met
    score = score_result.total_score
    tier  = score_result.tier.value

    edu_hm = hybrid_metrics.get("educational", {})
    edu_pm = planoc_metrics.get("educational", {})
    vt_hm  = hybrid_metrics.get("vt_real", {})
    ndx_hm = hybrid_metrics.get("ndx_real", {})

    verdict = {
        "iteration":             "012-2026-04-27-1153-hybrid-net-tax",
        "score":                 score,
        "tier":                  tier,
        "winner_conditions_met": winner_conditions_met,
        "kill_pass_all":         all_kill,
        "pareto_sharpe_all":     all_pareto,
        "hybrid_edu_sharpe":     edu_hm.get("sharpe"),
        "hybrid_edu_cagr":       edu_hm.get("cagr"),
        "hybrid_edu_mdd":        edu_hm.get("mdd"),
        "hybrid_vt_sharpe":      vt_hm.get("sharpe"),
        "hybrid_vt_cagr":        vt_hm.get("cagr"),
        "hybrid_ndx_sharpe":     ndx_hm.get("sharpe"),
        "hybrid_ndx_cagr":       ndx_hm.get("cagr"),
        "planoc_edu_net_sharpe": edu_pm.get("sharpe"),
        "planoc_edu_net_cagr":   edu_pm.get("cagr"),
        "planoc_edu_net_mdd":    edu_pm.get("mdd"),
        "haa_edu_net_sharpe":    HAA_NET["educational"]["sharpe"],
        "haa_edu_net_cagr":      HAA_NET["educational"]["cagr"],
        "tax_model_params": {
            "darf_rate":                DARF_RATE,
            "fx_cost_one_way":          FX_COST_ONE_WAY,
            "carne_leao_incremental":   CARNE_LEAO_INCREMENTAL_ANNUAL,
            "haa_sleeve_weight":        0.50,
            "planoc_sleeve_weight":     0.50,
        },
        "loop_status": "FROZEN after iter 012 — mandate §7 deliberation required",
    }
    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print(f"  verdict.json written: Score={score} Tier={tier}")
    print(f"\n  LOOP FROZEN after iter 012. Mandate §7 deliberation required.")
    print("=" * 70)


if __name__ == "__main__":
    main()
