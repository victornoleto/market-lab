"""
Phase 3.5e — c02 SMA150+Cash Binary Regime — QLD single-ticker sweep (iter 24).

Strategy: SPY price > SMA(150) → 100% QLD; else → cash (0%).
Signal asset: SPY [leverage_for_the_long_run, p.30].
Asset: QLD (2× QQQ, ProShares).
Off-leg: cash (0%) only — c02 is the SMA150+cash config slot in the 144-trial grid.

Citations:
  [leverage_for_the_long_run, p.30]  — SMA150 regime sensitivity test
  [advances_fin_ml, p.208-211]       — PBO/CSCV gate
  [advances_fin_ml, p.298-299]       — DSR gate (n_trials = cumulative)

Data: reports/phase_3_5c/cross_lib/data/reference_prices.parquet (Stage 1, Tiingo-first).
Stage 2: N/A for QLD (no QQQSIM from testfol.io; yfinance forbidden per spec §3.1).
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import warnings

sys.path.insert(0, "/var/www/pessoal/ai-trade")
sys.path.insert(0, "/var/www/pessoal/ai-trade/src")

from ai_trade.backtest.validation.pbo import pbo as compute_pbo_cscv
from ai_trade.backtest.validation.dsr import dsr as compute_dsr
from ai_trade.backtest.sweeps.registry import (
    load_registry,
    pop_pending,
    append_done,
    advance_status,
    atomic_write_registry,
)

# ─── Constants ────────────────────────────────────────────────────────────────
REGISTRY_PATH = "reports/phase_3_5e/c02_sma150_cash/registry.json"
REPORT_DIR = "reports/phase_3_5e/c02_sma150_cash"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
TRIAL_COUNT_PATH = "docs/self_improvement/trial_count.json"
TAX_RATE = 0.15         # 15% IR BR flat on CAGR
TICKER = "QLD"
ITER_NUM = 24
PHASE = "phase_3_5e"
MA_PERIOD = 150

# Data windows — max(QLD_start, SPY_start) from parquet; parquet end
WINDOW_START = "2001-05-15"   # max(QLD, SPY) in reference_prices.parquet
WINDOW_END   = "2026-04-17"   # last date in reference_prices.parquet


# ─── Signal ──────────────────────────────────────────────────────────────────

def sma_regime(spy: pd.Series, lookback: int = MA_PERIOD) -> pd.Series:
    """SPY close > SMA(150) → regime on (1). Shift by 1 to avoid lookahead.
    [leverage_for_the_long_run, p.30]"""
    sma = spy.rolling(lookback, min_periods=lookback).mean()
    return (spy > sma).astype(float).shift(1).fillna(0)


# ─── Data loading ─────────────────────────────────────────────────────────────

def load_wide(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


# ─── Portfolio backtest ───────────────────────────────────────────────────────

def run_portfolio(prices: pd.DataFrame) -> pd.Series:
    """
    100% QLD when SPY > SMA150 (prev day), else 100% cash (0%).
    Daily rebalance, no transaction costs (gross returns; tax at CAGR level).
    [leverage_for_the_long_run, p.30]
    """
    sig = sma_regime(prices["SPY"])
    ret_qld = prices["QLD"].pct_change()
    port = sig * ret_qld  # cash leg = 0%, so (1-sig)*0 = 0
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
    """WF gate: Sharpe per walk-forward split; pass if ≥6/8 positive.
    [advances_fin_ml, ch.12]"""
    n = len(returns)
    if n < n_splits * 63:
        return [], 0
    split_size = n // n_splits
    sharpes = []
    for i in range(n_splits):
        chunk = returns.iloc[i * split_size : (i + 1) * split_size]
        sharpes.append(compute_sharpe(chunk))
    positive = sum(1 for s in sharpes if np.isfinite(s) and s > 0)
    return sharpes, positive


def compute_oos_holdout(returns: pd.Series) -> dict:
    """Single-block OOS: last 20% reserved. Gate: OOS Sharpe ≥ 0.5 × IS Sharpe."""
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
    """Forward-window stress: last 63 trading days (~1 quarter). Gate: Sharpe > 0."""
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
    """DSR with cumulative trial count (honest multiple-testing correction).
    [advances_fin_ml, p.298-299]"""
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


def run_bt_crosslib(prices: pd.DataFrame) -> dict | None:
    """Cross-lib bt concordance check (single config: cash off-leg)."""
    try:
        import bt  # type: ignore

        sig = sma_regime(prices["SPY"])
        exec_prices = prices[["QLD"]].copy()
        weights = pd.DataFrame({"QLD": sig}, index=prices.index)

        strat = bt.Strategy(
            "qld_sma150_cash",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["qld_sma150_cash"]
        bt_rets = equity.pct_change().dropna()
        return {
            "bt_cagr": float(compute_cagr(bt_rets)),
            "bt_sharpe": float(compute_sharpe(bt_rets)),
        }
    except Exception as e:
        print(f"  [bt cross-lib] error: {e}", file=sys.stderr)
        return None


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


def build_md_report(result: dict, bt_result: dict | None) -> str:
    m = result["metrics_is"]
    wf = result["wf"]
    oos = result["oos"]
    fwd = result["fwd"]
    gates = result["gates"]
    dsr = result.get("dsr", {})
    spy_bm = result.get("spy_benchmark", {})

    lines = [
        f"# QLD daily — c02 SMA150+Cash Binary Regime (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** SPY > SMA150 (prev day) → 100% QLD; else → cash (0%).",
        "**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).",
        "**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.",
        "**Off-leg:** cash (0%) — shorter MA sensitivity test vs c01 SMA200.",
        "**Tax:** 15% IR BR flat on CAGR.",
        "**Stage 2:** N/A — no QQQSIM from testfol.io; yfinance forbidden per spec §3.1.",
        f"**Window:** {WINDOW_START} → {WINDOW_END} ({result['window_years']:.1f}y)",
        "",
        "## Results",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| CAGR gross | {m['cagr']*100:.2f}% |",
        f"| CAGR net (15% IR) | {m['cagr_net']*100:.2f}% |",
        f"| Sharpe gross | {m['sharpe']:.3f} |",
        f"| Sharpe net | {m['sharpe_net']:.3f} |",
        f"| MaxDD | {m['max_dd']*100:.1f}% |",
        f"| Calmar | {m['calmar']:.3f} |",
        f"| WF | {wf['positive']}/8 |",
        f"| OOS Sharpe | {oos['oos_sharpe']:.3f} (IS={oos['is_sharpe']:.3f}) |",
        f"| FWD Sharpe | {fwd['fwd_sharpe']:.3f} |",
        f"| DSR p-value | {dsr.get('p_value', float('nan')):.4f} (n_trials={dsr.get('n_trials_used', 'N/A')}) |",
        f"| n_bars | {result['n_bars']} |",
        "",
        "## SPY benchmark (same window)",
        "",
        f"| SPY CAGR gross | {spy_bm.get('spy_cagr_gross', float('nan'))*100:.2f}% |",
        f"| SPY CAGR net | {spy_bm.get('spy_cagr_net', float('nan'))*100:.2f}% |",
        f"| SPY Sharpe | {spy_bm.get('spy_sharpe', float('nan')):.3f} |",
        f"| SPY MaxDD | {spy_bm.get('spy_max_dd', float('nan'))*100:.1f}% |",
        f"| Correlation vs SPY | {spy_bm.get('corr_vs_spy', float('nan')):.3f} |",
        "",
        "## Gate summary",
        "",
        f"| Gate | Result |",
        f"|------|--------|",
        f"| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |",
        f"| Gate 2 — DSR p<0.05 | {'✓ PASS' if gates['gate2_dsr'] else '✗ FAIL'} (p={dsr.get('p_value', float('nan')):.4f}) |",
        f"| Gate 3 — WF ≥6/8 | {'✓ PASS' if gates['gate3_wf'] else '✗ FAIL'} ({wf['positive']}/8) |",
        f"| Gate 4 — OOS holdout | {'✓ PASS' if gates['gate4_oos'] else '✗ FAIL'} (OOS_S={oos['oos_sharpe']:.3f}) |",
        f"| Gate 5 — FWD stress | {'✓ PASS' if gates['gate5_fwd'] else '✗ FAIL'} (FWD_S={fwd['fwd_sharpe']:.3f}) |",
        f"| Eco 1 — beats SPY net | {'✓ PASS' if gates['eco1_beats_spy'] else '✗ FAIL'} |",
        f"| Eco 2 — Calmar>0.5 | {'✓ PASS' if gates['eco2_calmar'] else '✗ FAIL'} (Cal={m['calmar']:.3f}) |",
        f"| Eco 3 — Sharpe_net>0.8 | {'✓ PASS' if gates['eco3_sharpe_net'] else '✗ FAIL'} (SN={m['sharpe_net']:.3f}) |",
        f"| **Pre-pass (no PBO)** | **{'✓ PRE-PASS' if gates['pre_pass_pending_pbo'] else '✗ ' + gates['fail_reason']}** |",
        "",
        "## WF split Sharpes",
        "",
        f"{' | '.join([f'{s:.3f}' for s in wf['sharpes']])}",
        "",
        f"OOS window: {oos['oos_start']} → {oos['oos_end']}",
        f"FWD window: {fwd['fwd_start']} → {fwd['fwd_end']}",
        "",
        "## Cross-lib concordance (bt)",
        "",
    ]

    if bt_result:
        our_cagr = m["cagr"]
        delta = abs(our_cagr - bt_result["bt_cagr"]) * 100
        concordant = delta <= 3.0
        lines.append(
            f"| bt CAGR | {bt_result['bt_cagr']*100:.2f}% |"
        )
        lines.append(
            f"| ΔCAGR | {delta:.2f}pp — {'✓ CONCORDANT' if concordant else '✗ DIVERGENT'} |"
        )
    else:
        lines.append("bt library not available — concordance skipped.")

    lines += [
        "",
        "## Citations",
        "",
        "- `[leverage_for_the_long_run, p.30]` — SMA150 regime test (shorter MA sensitivity)",
        "- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate",
        "- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials",
        "- `[advances_fin_ml, ch.12]` — Walk-forward validation",
        "",
        "## Notes",
        "",
        "- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.",
        "- c02 tests only the cash off-leg for SMA150. c03 tests EMA100+TLT as a separate lead.",
        "- Stage-2 is N/A for QLD (QQQ 2× — no QQQSIM in testfol.io; yfinance forbidden by spec §3.1).",
        f"- DSR n_trials = {dsr.get('n_trials_used', 'N/A')} (cumulative from trial_count.json).",
    ]

    return "\n".join(lines) + "\n"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== Phase 3.5e c02 QLD sweep (iter {ITER_NUM}) ===")
    print(f"  Config: c02_sma150_cash (SMA150 + cash off-leg)")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")

    # Load data
    wide = load_wide(PARQUET_PATH, WINDOW_START, WINDOW_END)
    print(f"  Data loaded: {len(wide)} bars, tickers={sorted(wide.columns.tolist())}")

    required = ["QLD", "SPY"]
    missing = [t for t in required if t not in wide.columns]
    if missing:
        raise RuntimeError(f"Missing tickers in reference_prices.parquet: {missing}")

    # Load trial count
    trial_count = load_trial_count()
    trial_start = trial_count["total_trials_completed"]
    n_trials_this_config = trial_start + 1  # this is trial #(trial_start + 1)
    print(f"  Trial count before sweep: {trial_start} → using n_trials={n_trials_this_config} for DSR")

    # Run portfolio
    print(f"\n  → c02_sma150_cash (window: {WINDOW_START} → {WINDOW_END})", end=" ... ")
    prices = wide.loc[WINDOW_START:WINDOW_END]
    port = run_portfolio(prices)

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
    dsr = compute_dsr_gate(port, n_trials_this_config)

    print(
        f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%  "
        f"Sharpe={sharpe:.3f} net={sharpe_net:.3f}  "
        f"MaxDD={max_dd*100:.1f}%  Calmar={calmar:.3f}  "
        f"WF={wf_positive}/8  OOS_S={oos['oos_sharpe']:.2f}  "
        f"FWD_S={fwd['fwd_sharpe']:.2f}  DSR_p={dsr['p_value']:.4f}"
    )

    result = {
        "name": "c02_sma150_cash",
        "off_leg": "cash",
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
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
        "stage2": {"note": "N/A — QLD is QQQ-based 2×; no QQQSIM in testfol.io; yfinance forbidden per spec §3.1"},
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

    # Cross-lib bt
    bt_result = run_bt_crosslib(prices)
    if bt_result:
        delta = abs(cagr - bt_result["bt_cagr"]) * 100
        print(f"  bt cross-lib: CAGR={bt_result['bt_cagr']*100:.1f}% ΔCAGR={delta:.2f}pp "
              f"({'CONCORDANT' if delta <= 3.0 else 'DIVERGENT'})")
    else:
        print("  bt cross-lib: UNAVAILABLE")

    any_prepass = bool(g.get("pre_pass_pending_pbo", False))
    print(f"\n  Pre-pass (pending PBO): {any_prepass}")

    # ── Write QLD.json ──
    json_path = os.path.join(REPORT_DIR, "QLD.json")
    json_data = {
        "ticker": TICKER,
        "frequency": "daily",
        "phase": PHASE,
        "lead_id": "c02",
        "lead_slug": "c02_sma150_cash",
        "iter": ITER_NUM,
        "source": "reference_prices.parquet (Stage 1, Tiingo-first post-2026-04-21)",
        "config": result,
        "best_config": "c02_sma150_cash",
        "any_prepass_pending_pbo": any_prepass,
        "best_sharpe_oos": float(oos["oos_sharpe"]),
        "best_cagr": float(cagr),
        "best_maxdd": float(max_dd),
        "cross_lib_bt": bt_result,
        "citations": [
            "leverage_for_the_long_run, p.30",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    # ── Write QLD.md ──
    md_path = os.path.join(REPORT_DIR, "QLD.md")
    md_text = build_md_report(result, bt_result)
    atomic_write_text(md_path, md_text)

    # ── Update trial_count.json ──
    new_trial_count = update_trial_count(trial_count, 1)
    atomic_write_json(TRIAL_COUNT_PATH, new_trial_count)
    print(f"  trial_count: {trial_start} → {new_trial_count['total_trials_completed']}")

    # ── Update registry ──
    reg = load_registry(REGISTRY_PATH)
    ticker_popped, reg = pop_pending(reg)
    assert ticker_popped == TICKER, f"Expected {TICKER}, got {ticker_popped}"

    summary = {
        "ticker": TICKER,
        "frequency": "daily",
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
        "iter": ITER_NUM,
        "n_configs_tested": 1,
        "best_config": "c02_sma150_cash",
        "best_sharpe_oos": float(oos["oos_sharpe"]),
        "best_cagr": float(cagr),
        "best_maxdd": float(max_dd),
        "any_pass_5gate": any_prepass,
        "pbo_local": float("nan"),  # N=1 config, PBO meaningless
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
