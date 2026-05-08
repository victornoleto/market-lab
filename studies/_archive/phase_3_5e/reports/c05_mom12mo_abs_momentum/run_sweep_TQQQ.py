"""
Phase 3.5e — c05 Absolute Momentum 12-month (Antonacci) — TQQQ sweep (iter 38).

Strategy: 12-month trailing return of TQQQ > 0 → 100% TQQQ; else → 100% off-leg.
Signal asset: TQQQ (self). Off-legs tested: cash, GLD, TLT.
Monthly rebalancing, signal shifted 1 day to prevent lookahead bias.
Citation: [dual_momentum, ch.6] — Antonacci absolute momentum filter.

Data Stage 1: reports/phase_3_5c/cross_lib/data/reference_prices.parquet (Tiingo-first).
  TQQQ synthetic pre-2010: 3× QQQ daily - drag - expense [leverage_for_the_long_run, ch.2].
Data Stage 2: data/tiingo/daily/prices/TQQQ.parquet (Tiingo real, 2010-02-11 onwards).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, "/var/www/github/finances/market-lab")
sys.path.insert(0, "/var/www/github/finances/market-lab/src")

from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.sweeps.registry import (
    load_registry,
    pop_pending,
    append_done,
    advance_status,
    atomic_write_registry,
)

# ─── Constants ────────────────────────────────────────────────────────────────
REGISTRY_PATH = "reports/phase_3_5e/c05_mom12mo_abs_momentum/registry.json"
REPORT_DIR = "reports/phase_3_5e/c05_mom12mo_abs_momentum"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
TIINGO_TQQQ_PATH = "data/tiingo/daily/prices/TQQQ.parquet"
TRIAL_COUNT_PATH = "docs/self_improvement/trial_count.json"
TAX_RATE = 0.15
TICKER = "TQQQ"
ITER_NUM = 38
PHASE = "phase_3_5e"
LOOKBACK_MONTHS = 12

# Windows per off-leg (constrained by off-leg availability in parquet)
# TQQQ in parquet: 2001-05-15→2026-04-17; GLD: 2004-11-18→2026-04-15; TLT: 2002-07-26→2026-04-15
# Note: seam gap 2010-02-09/10 in Tiingo real TQQQ; synthetic parquet clean from 2001-05-15.
WINDOWS = {
    "cash": ("2001-05-15", "2026-04-17"),
    "GLD":  ("2004-11-18", "2026-04-15"),
    "TLT":  ("2002-07-26", "2026-04-15"),
}

CONFIGS = [
    {"name": "c05_mom12mo_cash", "off_leg": "cash"},
    {"name": "c05_mom12mo_gld",  "off_leg": "GLD"},
    {"name": "c05_mom12mo_tlt",  "off_leg": "TLT"},
]


# ─── Signal ──────────────────────────────────────────────────────────────────

def absolute_momentum_signal(prices: pd.DataFrame, lookback_months: int) -> pd.Series:
    """
    Antonacci 12-month absolute momentum on TQQQ (self).
    r_12m > 0 → 1 (invest); else → 0 (move to off-leg).
    Monthly rebalance; signal shifted 1 trading day to avoid lookahead.
    [dual_momentum, ch.6]
    """
    monthly = prices["TQQQ"].resample("ME").last()
    trailing_ret = monthly.pct_change(lookback_months)
    signal = (trailing_ret > 0).astype(float)
    daily_signal = signal.reindex(prices.index).ffill().shift(1).fillna(0)
    return daily_signal


# ─── Data loading ─────────────────────────────────────────────────────────────

def load_wide(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


# ─── Portfolio backtest ───────────────────────────────────────────────────────

def run_portfolio(prices: pd.DataFrame, off_leg: str) -> pd.Series:
    """
    12-month abs momentum: signal > 0 → 100% TQQQ; else → 100% off-leg.
    [dual_momentum, ch.6]
    """
    sig = absolute_momentum_signal(prices, LOOKBACK_MONTHS)
    ret_tqqq = prices["TQQQ"].pct_change()

    if off_leg == "cash":
        ret_off = pd.Series(0.0, index=prices.index)
    else:
        ret_off = prices[off_leg].pct_change()

    port = sig * ret_tqqq + (1.0 - sig) * ret_off
    return port.dropna()


# ─── Metrics ─────────────────────────────────────────────────────────────────

def compute_cagr(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years < 0.5:
        return float("nan")
    return float(equity.iloc[-1] ** (1 / years) - 1)


def compute_sharpe(returns: pd.Series) -> float:
    if returns.std() < 1e-12 or len(returns) < 30:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(252))


def compute_max_dd(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    running_max = equity.expanding().max()
    dd = (equity - running_max) / running_max
    return float(dd.min())


def compute_calmar(cagr: float, max_dd: float) -> float:
    if max_dd == 0 or not np.isfinite(max_dd):
        return float("nan")
    return float(cagr / abs(max_dd))


def compute_wf(returns: pd.Series, n_splits: int = 8) -> tuple[list[float], int]:
    """WF gate: Sharpe per split; pass if ≥6/8 positive. [advances_fin_ml, ch.12]"""
    n = len(returns)
    if n < n_splits * 63:
        return [], 0
    split_size = n // n_splits
    sharpes = [compute_sharpe(returns.iloc[i * split_size:(i + 1) * split_size])
               for i in range(n_splits)]
    positive = sum(1 for s in sharpes if np.isfinite(s) and s > 0)
    return sharpes, positive


def compute_oos_holdout(returns: pd.Series) -> dict:
    """Single-block OOS: last 20%. Gate: OOS Sharpe ≥ 0.5 × IS Sharpe."""
    n = len(returns)
    split = int(n * 0.8)
    is_ret = returns.iloc[:split]
    oos_ret = returns.iloc[split:]
    is_sharpe = compute_sharpe(is_ret)
    oos_sharpe = compute_sharpe(oos_ret)
    oos_pass = (
        np.isfinite(oos_sharpe)
        and np.isfinite(is_sharpe)
        and oos_sharpe >= 0.5 * is_sharpe
    )
    return {
        "is_sharpe": float(is_sharpe),
        "oos_sharpe": float(oos_sharpe),
        "oos_pass": bool(oos_pass),
        "is_start": str(returns.index[0].date()),
        "is_end": str(returns.index[split - 1].date()),
        "oos_start": str(returns.index[split].date()),
        "oos_end": str(returns.index[-1].date()),
    }


def compute_fwd_stress(returns: pd.Series) -> dict:
    """Forward-window stress: last 63 trading days. Gate: Sharpe > 0."""
    fwd = returns.iloc[-63:]
    fwd_sharpe = compute_sharpe(fwd)
    return {
        "fwd_sharpe": float(fwd_sharpe),
        "fwd_pass": bool(np.isfinite(fwd_sharpe) and fwd_sharpe > 0),
        "fwd_start": str(fwd.index[0].date()),
        "fwd_end": str(fwd.index[-1].date()),
    }


def compute_spy_benchmark(prices: pd.DataFrame, port_returns: pd.Series) -> dict:
    spy = prices["SPY"].pct_change().reindex(port_returns.index).dropna()
    spy_cagr = compute_cagr(spy)
    spy_cagr_net = spy_cagr * (1 - TAX_RATE)
    spy_sharpe = compute_sharpe(spy)
    spy_max_dd = compute_max_dd(spy)
    corr = float(port_returns.corr(spy)) if len(spy) == len(port_returns) else float("nan")
    return {
        "spy_cagr_gross": float(spy_cagr),
        "spy_cagr_net": float(spy_cagr_net),
        "spy_sharpe": float(spy_sharpe),
        "spy_max_dd": float(spy_max_dd),
        "corr_vs_spy": float(corr),
    }


def compute_dsr_gate(port: pd.Series, n_trials_cumulative: int) -> dict:
    """DSR with cumulative trial count. [advances_fin_ml, p.298-299]"""
    try:
        result = compute_dsr(port.values, n_trials=max(n_trials_cumulative, 2))
        return {
            "dsr": float(result.dsr),
            "p_value": float(result.p_value),
            "pass": bool(result.p_value < 0.05),
            "n_trials_used": n_trials_cumulative,
        }
    except Exception as e:
        return {
            "dsr": float("nan"),
            "p_value": float("nan"),
            "pass": False,
            "n_trials_used": n_trials_cumulative,
            "error": str(e),
        }


def gate_summary(result: dict, dsr: dict, spy_bm: dict, cagr_net: float) -> dict:
    wf = result.get("wf", {})
    oos = result.get("oos", {})
    fwd = result.get("fwd", {})

    gate2_dsr = dsr.get("pass", False)
    gate3_wf = wf.get("pass", False)
    gate4_oos = oos.get("oos_pass", False)
    gate5_fwd = fwd.get("fwd_pass", False)
    overfit_pass_no_pbo = gate2_dsr and gate3_wf and gate4_oos and gate5_fwd

    spy_cagr_net = spy_bm.get("spy_cagr_net", 0)
    eco1_beats_spy = bool(cagr_net > spy_cagr_net)
    eco2_calmar = bool(result["metrics_is"].get("calmar", 0) > 0.5)
    eco3_sharpe_net = bool(result["metrics_is"].get("sharpe_net", 0) > 0.8)
    eco_pass = eco1_beats_spy and eco2_calmar and eco3_sharpe_net

    fail_parts = []
    if not gate2_dsr: fail_parts.append("DSR")
    if not gate3_wf: fail_parts.append("WF")
    if not gate4_oos: fail_parts.append("OOS")
    if not gate5_fwd: fail_parts.append("FWD")
    if not eco1_beats_spy: fail_parts.append("SPY_BEAT")
    if not eco2_calmar: fail_parts.append("CALMAR")
    if not eco3_sharpe_net: fail_parts.append("SHARPE_NET")

    return {
        "gate1_pbo": "AGGREGATE_LEVEL",
        "gate2_dsr": gate2_dsr,
        "gate3_wf": gate3_wf,
        "gate4_oos": gate4_oos,
        "gate5_fwd": gate5_fwd,
        "overfit_pass_no_pbo": overfit_pass_no_pbo,
        "eco1_beats_spy": eco1_beats_spy,
        "eco2_calmar": eco2_calmar,
        "eco3_sharpe_net": eco3_sharpe_net,
        "eco_pass": eco_pass,
        "pre_pass_pending_pbo": bool(overfit_pass_no_pbo and eco_pass),
        "fail_reason": (
            "PRE-PASS (PBO pending aggregator)"
            if (overfit_pass_no_pbo and eco_pass)
            else (", ".join(fail_parts) if fail_parts else "UNKNOWN")
        ),
    }


def run_bt_crosslib(prices: pd.DataFrame, off_leg: str) -> dict | None:
    """Cross-lib bt concordance for best config."""
    try:
        import bt  # type: ignore

        sig = absolute_momentum_signal(prices, LOOKBACK_MONTHS)

        if off_leg == "cash":
            exec_prices = prices[["TQQQ"]].copy()
            weights = pd.DataFrame({"TQQQ": sig}, index=prices.index)
        else:
            exec_prices = prices[["TQQQ", off_leg]].copy()
            weights = pd.DataFrame(
                {"TQQQ": sig, off_leg: 1.0 - sig},
                index=prices.index,
            )

        strat = bt.Strategy(
            f"tqqq_mom12mo_{off_leg.lower()}",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices[f"tqqq_mom12mo_{off_leg.lower()}"]
        bt_rets = equity.pct_change().dropna()
        return {
            "bt_cagr": float(compute_cagr(bt_rets)),
            "bt_sharpe": float(compute_sharpe(bt_rets)),
        }
    except Exception as e:
        print(f"  [bt cross-lib] error: {e}", file=sys.stderr)
        return None


def run_stage2_concordance(off_leg: str, stage1_cagr: float, w_start: str, w_end: str,
                           df_full: pd.DataFrame) -> dict:
    """
    Stage 2: Tiingo real TQQQ vs Stage 1 synthetic parquet.
    Run same strategy on Tiingo TQQQ (adj_close) + off-leg from parquet.
    Gate: |CAGR_stage2 - CAGR_stage1_overlap| ≤ 3pp.
    [leverage_for_the_long_run, ch.2]
    """
    try:
        tiingo_tqqq = pd.read_parquet(TIINGO_TQQQ_PATH)["adj_close"]
        tiingo_tqqq.index = pd.to_datetime(tiingo_tqqq.index)
        tiingo_tqqq.name = "TQQQ"

        # Stage 2 window: Tiingo TQQQ starts 2010-02-11 (seam gap: 2010-02-09/10 missing)
        s2_start = max(pd.Timestamp("2010-02-11"), pd.Timestamp(w_start))
        s2_end = pd.Timestamp(w_end)
        tiingo_slice = tiingo_tqqq.loc[s2_start:s2_end]

        if len(tiingo_slice) < 252:
            return {"status": "skip", "note": "Tiingo TQQQ too short for Stage 2"}

        # Build prices DataFrame for Stage 2 using parquet off-leg data
        mask = (df_full["date"] >= str(s2_start.date())) & (df_full["date"] <= w_end)
        df_s2 = df_full[mask]
        wide_s2 = df_s2.pivot(index="date", columns="ticker", values="close")
        wide_s2.columns.name = None
        wide_s2 = wide_s2.ffill().dropna(how="all")
        tiingo_aligned = tiingo_slice.reindex(wide_s2.index).ffill()
        wide_s2["TQQQ"] = tiingo_aligned
        wide_s2 = wide_s2.dropna(subset=["TQQQ"])

        port_s2 = run_portfolio(wide_s2, off_leg)
        cagr_s2 = compute_cagr(port_s2)

        # Stage 1 on same overlap window for fair comparison
        mask1 = (df_full["date"] >= str(s2_start.date())) & (df_full["date"] <= w_end)
        df_s1 = df_full[mask1]
        wide_s1 = df_s1.pivot(index="date", columns="ticker", values="close")
        wide_s1.columns.name = None
        wide_s1 = wide_s1.ffill().dropna(how="all")
        port_s1_overlap = run_portfolio(wide_s1, off_leg)
        cagr_s1_overlap = compute_cagr(port_s1_overlap)
        delta_overlap_pp = abs(cagr_s2 - cagr_s1_overlap) * 100

        return {
            "status": "done",
            "stage2_cagr": float(cagr_s2),
            "stage1_cagr_full": float(stage1_cagr),
            "stage1_cagr_overlap": float(cagr_s1_overlap),
            "delta_vs_full_pp": float(abs(cagr_s2 - stage1_cagr) * 100),
            "delta_vs_overlap_pp": float(delta_overlap_pp),
            "concordant": bool(delta_overlap_pp <= 3.0),
            "window_start": str(s2_start.date()),
            "window_end": w_end,
            "n_bars": len(port_s2),
        }
    except Exception as e:
        return {"status": "error", "note": str(e)}


# ─── Trial count helpers ──────────────────────────────────────────────────────

def load_trial_count() -> dict:
    with open(TRIAL_COUNT_PATH) as f:
        return json.load(f)


def update_trial_count(count: dict, n_new: int) -> dict:
    count = count.copy()
    count["total_trials_completed"] += n_new
    count["last_updated"] = datetime.now(timezone.utc).date().isoformat()
    return count


# ─── Atomic file writers ──────────────────────────────────────────────────────

def atomic_write_json(path: str, data: dict) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


def atomic_write_text(path: str, text: str) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


def build_md_report(
    all_results: list[dict],
    best_result: dict,
    best_bt: dict | None,
    best_off_leg: str,
    stage2: dict | None,
) -> str:
    m_best = best_result["metrics_is"]
    gates = best_result["gates"]
    dsr = best_result["dsr"]
    oos = best_result["oos"]
    fwd = best_result["fwd"]
    wf = best_result["wf"]
    spy_bm = best_result["spy_benchmark"]

    lines = [
        f"# TQQQ daily — c05 Absolute Momentum 12-month (Antonacci) (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** 12-month trailing return of TQQQ > 0 → 100% TQQQ; else → off-leg.",
        "**Asset:** TQQQ (ProShares UltraPro QQQ, 3× QQQ).",
        "**Signal:** Absolute momentum on TQQQ (self) `[dual_momentum, ch.6]`.",
        "**Off-legs tested:** cash (0%), GLD, TLT.",
        "**Tax:** 15% IR BR flat on CAGR.",
        "**Stage 1:** reference_prices.parquet (TQQQ synthetic pre-2010: 3× QQQ daily - drag - expense"
        " `[leverage_for_the_long_run, ch.2]`).",
        "",
        "## Summary across 3 off-legs",
        "",
        "| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |",
        "|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|",
    ]

    for r in all_results:
        m = r["metrics_is"]
        g = r["gates"]
        d = r["dsr"]
        o = r["oos"]
        fw = r["fwd"]
        wf_r = r["wf"]
        marker = " ← BEST" if r["name"] == best_result["name"] else ""
        lines.append(
            f"| {r['off_leg']} | {r['window_start']}→{r['window_end']} "
            f"| {m['cagr_net']*100:.1f}% | {m['sharpe_net']:.3f} "
            f"| {m['max_dd']*100:.1f}% | {m['calmar']:.3f} "
            f"| {wf_r.get('positive',0)}/8 | {o.get('oos_sharpe',float('nan')):.3f} "
            f"| {fw.get('fwd_sharpe',float('nan')):.3f} | {d.get('p_value',float('nan')):.4f} "
            f"| {'✓' if g['pre_pass_pending_pbo'] else '✗'}{marker} |"
        )

    lines += [
        "",
        f"## Best config: {best_result['name']} (off-leg: {best_off_leg})",
        "",
        f"**Window:** {best_result['window_start']} → {best_result['window_end']} ({best_result['window_years']:.1f}y)",
        "",
        "### Results",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| CAGR gross | {m_best['cagr']*100:.2f}% |",
        f"| CAGR net (15% IR) | {m_best['cagr_net']*100:.2f}% |",
        f"| Sharpe gross | {m_best['sharpe']:.3f} |",
        f"| Sharpe net | {m_best['sharpe_net']:.3f} |",
        f"| MaxDD | {m_best['max_dd']*100:.1f}% |",
        f"| Calmar | {m_best['calmar']:.3f} |",
        f"| WF | {wf['positive']}/8 |",
        f"| OOS Sharpe | {oos['oos_sharpe']:.3f} (IS={oos['is_sharpe']:.3f}) |",
        f"| FWD Sharpe | {fwd['fwd_sharpe']:.3f} |",
        f"| DSR p-value | {dsr.get('p_value', float('nan')):.4f} (n_trials={dsr.get('n_trials_used', 'N/A')}) |",
        f"| n_bars | {best_result['n_bars']} |",
        "",
        "### SPY benchmark (same window)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| SPY CAGR gross | {spy_bm.get('spy_cagr_gross', float('nan'))*100:.2f}% |",
        f"| SPY CAGR net | {spy_bm.get('spy_cagr_net', float('nan'))*100:.2f}% |",
        f"| SPY Sharpe | {spy_bm.get('spy_sharpe', float('nan')):.3f} |",
        f"| SPY MaxDD | {spy_bm.get('spy_max_dd', float('nan'))*100:.1f}% |",
        f"| Correlation vs SPY | {spy_bm.get('corr_vs_spy', float('nan')):.3f} |",
        "",
        "### Gate summary (best config)",
        "",
        "| Gate | Result |",
        "|------|--------|",
        "| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |",
        f"| Gate 2 — DSR p<0.05 | {'✓ PASS' if gates['gate2_dsr'] else '✗ FAIL'} (p={dsr.get('p_value', float('nan')):.4f}) |",
        f"| Gate 3 — WF ≥6/8 | {'✓ PASS' if gates['gate3_wf'] else '✗ FAIL'} ({wf['positive']}/8) |",
        f"| Gate 4 — OOS holdout | {'✓ PASS' if gates['gate4_oos'] else '✗ FAIL'} (OOS_S={oos['oos_sharpe']:.3f}) |",
        f"| Gate 5 — FWD stress | {'✓ PASS' if gates['gate5_fwd'] else '✗ FAIL'} (FWD_S={fwd['fwd_sharpe']:.3f}) |",
        f"| Eco 1 — beats SPY net | {'✓ PASS' if gates['eco1_beats_spy'] else '✗ FAIL'} |",
        f"| Eco 2 — Calmar>0.5 | {'✓ PASS' if gates['eco2_calmar'] else '✗ FAIL'} (Cal={m_best['calmar']:.3f}) |",
        f"| Eco 3 — Sharpe_net>0.8 | {'✓ PASS' if gates['eco3_sharpe_net'] else '✗ FAIL'} (SN={m_best['sharpe_net']:.3f}) |",
        f"| **Pre-pass (no PBO)** | **{'✓ PRE-PASS' if gates['pre_pass_pending_pbo'] else '✗ ' + gates['fail_reason']}** |",
        "",
        "### WF split Sharpes",
        "",
        f"{' | '.join([f'{s:.3f}' for s in wf['sharpes']])}",
        "",
        f"OOS window: {oos['oos_start']} → {oos['oos_end']}",
        f"FWD window: {fwd['fwd_start']} → {fwd['fwd_end']}",
        "",
        "## Stage 2 concordance (Tiingo real TQQQ vs Stage 1 synthetic)",
        "",
    ]

    if stage2 and stage2.get("status") == "done":
        delta = stage2["delta_vs_overlap_pp"]
        concordant = stage2["concordant"]
        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Stage 1 CAGR (full window) | {stage2['stage1_cagr_full']*100:.2f}% |",
            f"| Stage 1 CAGR (overlap 2010+) | {stage2['stage1_cagr_overlap']*100:.2f}% |",
            f"| Stage 2 CAGR (Tiingo TQQQ real) | {stage2['stage2_cagr']*100:.2f}% |",
            f"| ΔCAGR (Stage2 vs Stage1 overlap) | {delta:.2f}pp — {'✓ CONCORDANT' if concordant else '✗ DIVERGENT'} |",
            f"| Stage 2 window | {stage2['window_start']} → {stage2['window_end']} ({stage2['n_bars']} bars) |",
        ]
    else:
        note = stage2.get("note", "unavailable") if stage2 else "not run"
        lines.append(f"Stage 2 data unavailable — {note}")

    lines += [
        "",
        "## Cross-lib concordance (bt) — best config",
        "",
    ]

    if best_bt:
        delta = abs(m_best["cagr"] - best_bt["bt_cagr"]) * 100
        concordant = delta <= 3.0
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| bt CAGR | {best_bt['bt_cagr']*100:.2f}% |")
        lines.append(f"| ΔCAGR | {delta:.2f}pp — {'✓ CONCORDANT' if concordant else '✗ DIVERGENT'} |")
    else:
        lines.append("bt library not available — concordance skipped.")

    lines += [
        "",
        "## Citations",
        "",
        "- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter",
        "- `[leverage_for_the_long_run, ch.2]` — TQQQ synthetic pre-2010: 3× QQQ returns - drag - expense",
        "- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate",
        "- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials",
        "- `[advances_fin_ml, ch.12]` — Walk-forward validation",
        "",
        "## Notes",
        "",
        "- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.",
        "- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.",
        "- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.",
        f"- DSR n_trials: cash={all_results[0]['dsr'].get('n_trials_used','?')}, "
        f"GLD={all_results[1]['dsr'].get('n_trials_used','?')}, "
        f"TLT={all_results[2]['dsr'].get('n_trials_used','?')} (cumulative from trial_count.json).",
        "- TQQQ seam gap: 2010-02-09/10 missing in Tiingo real; synthetic parquet clean from 2001-05-15.",
        "- Stage 2 uses Tiingo real TQQQ from 2010-02-11; Stage 1 window extends to 2001-05-15 via synthetic.",
    ]

    return "\n".join(lines) + "\n"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== Phase 3.5e c05 TQQQ sweep (iter {ITER_NUM}) ===")
    print(f"  Strategy: Antonacci 12-month absolute momentum [dual_momentum, ch.6]")
    print(f"  Configs: {[c['name'] for c in CONFIGS]}")

    # Load full parquet once; filter per config
    df_full = pd.read_parquet(PARQUET_PATH)

    # Load trial count
    trial_count = load_trial_count()
    trial_start = trial_count["total_trials_completed"]
    print(f"  Trial count before sweep: {trial_start}")

    all_results: list[dict] = []
    current_trial = trial_start

    for cfg in CONFIGS:
        off_leg = cfg["off_leg"]
        w_start, w_end = WINDOWS[off_leg]
        current_trial += 1
        n_trials_this = current_trial

        print(f"\n  → {cfg['name']} (off-leg={off_leg}, window={w_start}→{w_end}) "
              f"[n_trials={n_trials_this}]", end=" ... ")

        # Filter data for this config's window
        mask = (df_full["date"] >= w_start) & (df_full["date"] <= w_end)
        df_w = df_full[mask]
        wide = df_w.pivot(index="date", columns="ticker", values="close")
        wide.columns.name = None
        wide = wide.ffill().dropna(how="all")

        # Verify required tickers
        required = ["TQQQ", "SPY"] + ([] if off_leg == "cash" else [off_leg])
        missing = [t for t in required if t not in wide.columns]
        if missing:
            print(f"SKIP — missing tickers: {missing}")
            continue

        prices = wide.loc[w_start:w_end]

        # Run portfolio
        port = run_portfolio(prices, off_leg)

        cagr = compute_cagr(port)
        cagr_net = cagr * (1 - TAX_RATE)
        sharpe = compute_sharpe(port)
        sharpe_net = sharpe * (1 - TAX_RATE)
        max_dd = compute_max_dd(port)
        calmar = compute_calmar(cagr, max_dd)

        wf_sharpes, wf_positive = compute_wf(port, n_splits=8)
        wf_pass = wf_positive >= 6

        oos = compute_oos_holdout(port)
        fwd = compute_fwd_stress(port)
        spy_bm = compute_spy_benchmark(prices, port)
        dsr = compute_dsr_gate(port, n_trials_this)

        print(
            f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%  "
            f"Sharpe={sharpe:.3f} net={sharpe_net:.3f}  "
            f"MaxDD={max_dd*100:.1f}%  Calmar={calmar:.3f}  "
            f"WF={wf_positive}/8  OOS_S={oos['oos_sharpe']:.2f}  "
            f"FWD_S={fwd['fwd_sharpe']:.2f}  DSR_p={dsr['p_value']:.4f}"
        )

        result = {
            "name": cfg["name"],
            "off_leg": off_leg,
            "window_start": w_start,
            "window_end": w_end,
            "window_years": float((port.index[-1] - port.index[0]).days / 365.25),
            "n_bars": len(port),
            "metrics_is": {
                "cagr": float(cagr),
                "cagr_net": float(cagr_net),
                "sharpe": float(sharpe),
                "sharpe_net": float(sharpe_net),
                "max_dd": float(max_dd),
                "calmar": float(calmar),
            },
            "wf": {
                "sharpes": [float(s) for s in wf_sharpes],
                "positive": wf_positive,
                "total": 8,
                "pass": bool(wf_pass),
            },
            "oos": oos,
            "fwd": fwd,
            "spy_benchmark": spy_bm,
            "dsr": dsr,
        }
        result["gates"] = gate_summary(result, dsr, spy_bm, cagr_net)
        g = result["gates"]
        print(
            f"  Gates (no PBO): DSR={'✓' if g['gate2_dsr'] else '✗'}  "
            f"WF={'✓' if g['gate3_wf'] else '✗'}  "
            f"OOS={'✓' if g['gate4_oos'] else '✗'}  "
            f"FWD={'✓' if g['gate5_fwd'] else '✗'}  "
            f"Eco={'✓' if g['eco_pass'] else '✗'}  "
            f"→ {g['fail_reason']}"
        )
        all_results.append(result)

    if not all_results:
        raise RuntimeError("No configs completed successfully")

    # Select best config (highest Sharpe_net)
    best_result = max(all_results, key=lambda r: r["metrics_is"]["sharpe_net"])
    best_off_leg = best_result["off_leg"]
    best_w_start, best_w_end = WINDOWS[best_off_leg]
    print(f"\n  Best config: {best_result['name']} (Sharpe_net={best_result['metrics_is']['sharpe_net']:.3f})")

    # Stage 2 on best config
    print(f"\n  Running Stage 2 concordance for best config ({best_off_leg} off-leg)...")
    stage2 = run_stage2_concordance(
        best_off_leg,
        best_result["metrics_is"]["cagr"],
        best_w_start,
        best_w_end,
        df_full,
    )
    if stage2.get("status") == "done":
        print(f"  Stage 2: CAGR={stage2['stage2_cagr']*100:.1f}%  "
              f"ΔCAGR_overlap={stage2['delta_vs_overlap_pp']:.2f}pp  "
              f"{'CONCORDANT' if stage2['concordant'] else 'DIVERGENT'}")
    else:
        print(f"  Stage 2: {stage2}")

    # Cross-lib bt on best config
    mask = (df_full["date"] >= best_w_start) & (df_full["date"] <= best_w_end)
    df_best = df_full[mask]
    wide_best = df_best.pivot(index="date", columns="ticker", values="close")
    wide_best.columns.name = None
    wide_best = wide_best.ffill().dropna(how="all")
    prices_best = wide_best.loc[best_w_start:best_w_end]

    bt_result = run_bt_crosslib(prices_best, best_off_leg)
    if bt_result:
        delta = abs(best_result["metrics_is"]["cagr"] - bt_result["bt_cagr"]) * 100
        print(f"  bt cross-lib: CAGR={bt_result['bt_cagr']*100:.1f}% "
              f"ΔCAGR={delta:.2f}pp ({'CONCORDANT' if delta <= 3.0 else 'DIVERGENT'})")

    any_prepass = any(r["gates"].get("pre_pass_pending_pbo", False) for r in all_results)
    best_sharpe_oos = best_result["oos"]["oos_sharpe"]

    print(f"\n  Any pre-pass (pending PBO): {any_prepass}")

    # ── Write TQQQ.json ──
    json_path = os.path.join(REPORT_DIR, "TQQQ.json")
    json_data = {
        "ticker": TICKER,
        "frequency": "daily",
        "phase": PHASE,
        "lead_id": "c05",
        "lead_slug": "c05_mom12mo_abs_momentum",
        "iter": ITER_NUM,
        "source": "reference_prices.parquet (Stage 1, Tiingo-first synthetic pre-2010)",
        "configs": all_results,
        "best_config": best_result["name"],
        "any_prepass_pending_pbo": any_prepass,
        "best_sharpe_oos": float(best_sharpe_oos),
        "best_cagr": float(best_result["metrics_is"]["cagr"]),
        "best_maxdd": float(best_result["metrics_is"]["max_dd"]),
        "cross_lib_bt": bt_result,
        "stage2": stage2,
        "citations": [
            "dual_momentum, ch.6",
            "leverage_for_the_long_run, ch.2",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
            "advances_fin_ml, ch.12",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    # ── Write TQQQ.md ──
    md_path = os.path.join(REPORT_DIR, "TQQQ.md")
    md_text = build_md_report(all_results, best_result, bt_result, best_off_leg, stage2)
    atomic_write_text(md_path, md_text)

    # ── Update trial_count.json ──
    n_new_trials = len(all_results)
    new_trial_count = update_trial_count(trial_count, n_new_trials)
    atomic_write_json(TRIAL_COUNT_PATH, new_trial_count)
    print(f"  trial_count: {trial_start} → {new_trial_count['total_trials_completed']}")

    # ── Update registry ──
    reg = load_registry(REGISTRY_PATH)
    ticker_popped, reg = pop_pending(reg)
    assert ticker_popped == TICKER, f"Expected {TICKER}, got {ticker_popped}"

    summary = {
        "ticker": TICKER,
        "frequency": "daily",
        "window_start": best_w_start,
        "window_end": best_w_end,
        "iter": ITER_NUM,
        "n_configs_tested": len(all_results),
        "best_config": best_result["name"],
        "best_sharpe_oos": float(best_sharpe_oos),
        "best_cagr": float(best_result["metrics_is"]["cagr"]),
        "best_maxdd": float(best_result["metrics_is"]["max_dd"]),
        "any_pass_5gate": any_prepass,
        "pbo_local": float("nan"),  # N=3 configs, local PBO not meaningful
        "result_file_md": md_path,
        "result_file_json": json_path,
    }
    reg = append_done(reg, summary)
    reg = advance_status(reg)
    atomic_write_registry(REGISTRY_PATH, reg)
    print(f"  Registry: status={reg['status']}, pending={reg['tickers_pending']}")
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
