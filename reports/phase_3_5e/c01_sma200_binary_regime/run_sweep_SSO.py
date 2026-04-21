"""
Phase 3.5e — c01 SMA200 Binary Regime — SSO single-ticker sweep (iter 16).

Strategy: SPY price > SMA(200) → 100% SSO; else → off-leg (cash/GLD/TLT).
Signal asset: SPY [leverage_for_the_long_run, ch.2].
Asset: SSO (2× SPX, ProShares Ultra S&P 500).
Off-legs: cash (0%), GLD, TLT.

SSO data: reference_prices.parquet synthetic pre-2006 via r = L × r_SPX_TR - drag - expense.
SPY signal limits effective window start to 2001-05-14.

Citations:
  [leverage_for_the_long_run, ch.2]   — SMA200 binary regime canonical (Gayed)
  [advances_fin_ml, p.208-211]        — PBO/CSCV gate
  [advances_fin_ml, p.298-299]        — DSR gate (n_trials = cumulative)

Data: reports/phase_3_5c/cross_lib/data/reference_prices.parquet (Stage 1).
Stage 2: yfinance independent validation.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
import warnings
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

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
REGISTRY_PATH = "reports/phase_3_5e/c01_sma200_binary_regime/registry.json"
REPORT_DIR = "reports/phase_3_5e/c01_sma200_binary_regime"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
TRIAL_COUNT_PATH = "docs/self_improvement/trial_count.json"
TAX_RATE = 0.15         # 15% IR BR flat on CAGR
TICKER = "SSO"
ITER_NUM = 16
PHASE = "phase_3_5e"

# Data windows per ticker (from reference_prices.parquet inspection)
# SSO:  1986-01-02 → 2026-04-17 (synthetic pre-2006)
# SPY:  2001-05-14 → 2026-04-14  (signal — limits window start)
# GLD:  2004-11-18 → 2026-04-15  (off-leg)
# TLT:  2002-07-26 → 2026-04-15  (off-leg)
WINDOW_CASH_START = "2001-05-14"   # max(SSO_in_parquet, SPY) = SPY start
WINDOW_GLD_START  = "2004-11-18"   # max(SSO, SPY, GLD)
WINDOW_TLT_START  = "2002-07-26"   # max(SSO, SPY, TLT)
WINDOW_END        = "2026-04-14"   # min of all available ends (SPY limits)


# ─── Signal ──────────────────────────────────────────────────────────────────

def sma_regime(spy: pd.Series, lookback: int = 200) -> pd.Series:
    """SPY close > SMA(200) → regime on (1). Shift by 1 to avoid lookahead.
    [leverage_for_the_long_run, ch.2]"""
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

def run_portfolio(prices: pd.DataFrame, off_leg: str) -> pd.Series:
    """
    100% SSO when SPY > SMA200 (prev day), else 100% off_leg.
    Daily rebalance, no transaction costs (gross returns; tax applied at CAGR level).
    """
    sig = sma_regime(prices["SPY"])
    ret_sso = prices["SSO"].pct_change()

    if off_leg == "cash":
        ret_off = pd.Series(0.0, index=prices.index)
    elif off_leg in ("GLD", "TLT"):
        ret_off = prices[off_leg].pct_change()
    else:
        raise ValueError(f"Unknown off_leg: {off_leg}")

    port = sig * ret_sso + (1 - sig) * ret_off
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


# ─── Per-ticker PBO (informational only) ──────────────────────────────────────

def compute_local_pbo(all_returns: dict[str, pd.Series]) -> dict:
    """PBO on the common window across all 3 off-leg configs.
    N=3 < 4 → UNRELIABLE per Phase 3.5d E1 rejection lesson.
    Real PBO computed at aggregator across all 144 trials.
    [advances_fin_ml, p.208-211]"""
    if len(all_returns) < 2:
        return {"pbo": float("nan"), "pass": None, "note": "< 2 configs"}

    dfs = [v.rename(k) for k, v in all_returns.items()]
    combined = pd.concat(dfs, axis=1).dropna()
    if combined.shape[1] < 2 or len(combined) < 100:
        return {"pbo": float("nan"), "pass": None, "note": "insufficient common data"}

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = compute_pbo_cscv(combined.values, n_blocks=10)

    pbo_val = float(result.pbo)
    warn_msgs = [str(w.message) for w in caught]
    return {
        "pbo": pbo_val,
        "n_configs": combined.shape[1],
        "n_combinations": result.n_combinations,
        "pass_local": bool(pbo_val < 0.5),
        "note": f"N={combined.shape[1]} — INFORMATIONAL ONLY (N<4, real PBO at aggregator). "
                f"PBO={pbo_val:.3f}",
        "warnings": warn_msgs,
    }


# ─── DSR per config ────────────────────────────────────────────────────────────

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


# ─── Gate summary ─────────────────────────────────────────────────────────────

def gate_summary(result: dict, pbo_local: dict, dsr: dict, spy_bm: dict, cagr_net: float) -> dict:
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
        "fail_reason": "PRE-PASS (PBO pending aggregator)" if (overfit_pass_no_pbo and eco_pass) else (", ".join(fail_parts) if fail_parts else "unknown"),
    }


# ─── Cross-lib (bt) ───────────────────────────────────────────────────────────

def run_bt_crosslib(prices: pd.DataFrame, off_leg: str) -> dict | None:
    """Run same strategy in bt library for concordance check."""
    try:
        import bt  # type: ignore

        sig = sma_regime(prices["SPY"])
        exec_tickers = ["SSO"] if off_leg == "cash" else ["SSO", off_leg]
        exec_prices = prices[exec_tickers].copy()

        weights = pd.DataFrame(0.0, index=prices.index, columns=exec_tickers)
        weights["SSO"] = sig
        if off_leg != "cash":
            weights[off_leg] = 1 - sig

        strat = bt.Strategy(
            f"sso_sma200_{off_leg}",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices[f"sso_sma200_{off_leg}"].rename("equity")
        bt_rets = equity.pct_change().dropna()
        return {
            "bt_cagr": float(compute_cagr(bt_rets)),
            "bt_sharpe": float(compute_sharpe(bt_rets)),
        }
    except Exception as e:
        print(f"  [bt cross-lib] error: {e}", file=sys.stderr)
        return None


def run_stage2(off_leg: str, window_start: str) -> dict | None:
    """Stage 2: yfinance independent fetch to validate CAGR ≤ ±3pp."""
    try:
        import yfinance as yf  # type: ignore

        tickers_needed = ["SSO", "SPY"]
        if off_leg not in ("cash",):
            tickers_needed.append(off_leg)

        raw = yf.download(
            tickers_needed,
            start=window_start,
            end=WINDOW_END,
            progress=False,
            auto_adjust=True,
        )
        if raw.empty:
            return None

        if isinstance(raw.columns, pd.MultiIndex):
            close = raw["Close"]
        else:
            close = raw[["Close"]].rename(columns={"Close": tickers_needed[0]})

        close = close.dropna(how="all")
        port = run_portfolio(close, off_leg)
        return {"cagr_stage2": float(compute_cagr(port))}
    except Exception as e:
        print(f"  [Stage 2] error: {e}", file=sys.stderr)
        return None


# ─── Main backtest loop ────────────────────────────────────────────────────────

CONFIGS = [
    {"name": "c01_sma200_cash", "off_leg": "cash", "window_start": WINDOW_CASH_START},
    {"name": "c01_sma200_gld",  "off_leg": "GLD",  "window_start": WINDOW_GLD_START},
    {"name": "c01_sma200_tlt",  "off_leg": "TLT",  "window_start": WINDOW_TLT_START},
]


def run_all_configs(all_prices_wide: pd.DataFrame, trial_start: int) -> tuple[list[dict], dict[str, pd.Series]]:
    """Run 3 c01 configs on SSO. Returns per-config results + return series."""
    results: list[dict] = []
    all_returns: dict[str, pd.Series] = {}

    for i, cfg in enumerate(CONFIGS):
        name = cfg["name"]
        off_leg = cfg["off_leg"]
        w_start = cfg["window_start"]
        print(f"\n  → {name} (window: {w_start} → {WINDOW_END})", end=" ... ")

        try:
            prices = all_prices_wide.loc[w_start:WINDOW_END]
            port = run_portfolio(prices, off_leg)
            all_returns[name] = port

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

            n_trials_cumulative = trial_start + i + 1
            dsr = compute_dsr_gate(port, n_trials_cumulative)

            bt_result = run_bt_crosslib(prices, off_leg)
            if bt_result:
                bt_cagr = bt_result["bt_cagr"]
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = cagr_delta <= 3.0
            else:
                bt_cagr = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            stage2 = run_stage2(off_leg, w_start)
            if stage2:
                s2_cagr = stage2["cagr_stage2"]
                s2_delta = abs(cagr - s2_cagr) * 100
                s2_ok = s2_delta <= 3.0
            else:
                s2_cagr = float("nan")
                s2_delta = float("nan")
                s2_ok = None

            res = {
                "name": name,
                "off_leg": off_leg,
                "window_start": w_start,
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
                "cross_lib_bt": {
                    "bt_cagr": float(bt_cagr),
                    "cagr_delta_pp": float(cagr_delta),
                    "concordant": cross_lib_ok,
                },
                "stage2": {
                    "cagr_stage2": float(s2_cagr),
                    "cagr_delta_pp": float(s2_delta),
                    "concordant": s2_ok,
                },
            }

            res["gates"] = gate_summary(res, {}, dsr, spy_bm, cagr_net)

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%  "
                f"Sharpe={sharpe:.3f} net={sharpe_net:.3f}  "
                f"MaxDD={max_dd*100:.1f}%  Calmar={calmar:.3f}  "
                f"WF={wf_positive}/8  OOS_S={oos['oos_sharpe']:.2f}  "
                f"FWD_S={fwd['fwd_sharpe']:.2f}  DSR_p={dsr['p_value']:.4f}"
            )
            g = res["gates"]
            print(
                f"    Gates (no PBO): DSR={'✓' if g['gate2_dsr'] else '✗'}  "
                f"WF={'✓' if g['gate3_wf'] else '✗'}  "
                f"OOS={'✓' if g['gate4_oos'] else '✗'}  "
                f"FWD={'✓' if g['gate5_fwd'] else '✗'}  "
                f"Eco={'✓' if g['eco_pass'] else '✗'}  "
                f"→ {g['fail_reason']}"
            )

            results.append(res)
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
            results.append({"name": name, "off_leg": off_leg, "error": str(e)})

    return results, all_returns


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


def build_md_report(results: list[dict], pbo_local: dict) -> str:
    lines = [
        f"# SSO daily — c01 SMA200 Binary Regime (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** SPY > SMA200 (prev day) → 100% SSO; else → off-leg.",
        "**Asset:** SSO (ProShares Ultra S&P 500, 2× SPX).",
        "**Signal:** SPY SMA200 regime `[leverage_for_the_long_run, ch.2]`.",
        "**Off-legs:** cash (0%), GLD, TLT.",
        "**Tax:** 15% IR BR flat on CAGR.",
        "**Note:** SSO pre-2006 data is synthetic via r = L × r_SPX_TR - drag - expense.",
        "",
        f"**Per-ticker local PBO (informational, N=3 unreliable):** {pbo_local.get('pbo', float('nan')):.3f}",
        f"  Note: {pbo_local.get('note', '')}",
        "",
        "## Results table",
        "",
        "| Config | Window | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | Pre-pass |",
        "|--------|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-------|----------|---------|--------|----------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | — | ERROR | — | — | — | — | — | — | — | — | — | — | — | — | ✗ |")
            continue
        m = r["metrics_is"]
        wf = r["wf"]
        oos = r["oos"]
        fwd = r["fwd"]
        gates = r["gates"]
        dsr = r.get("dsr", {})
        spy_bm = r.get("spy_benchmark", {})

        years_str = f"{r['window_years']:.1f}y"
        cagr_pct = m["cagr"] * 100
        cagr_net_pct = m["cagr_net"] * 100
        sharpe = m["sharpe"]
        sharpe_net = m["sharpe_net"]
        maxdd_pct = m["max_dd"] * 100
        calmar = m["calmar"]
        wf_str = f"{wf['positive']}/8"
        oos_s = f"{oos['oos_sharpe']:.2f}"
        fwd_s = f"{fwd['fwd_sharpe']:.2f}"
        dsr_p = f"{dsr.get('p_value', float('nan')):.4f}"
        beat = "✓" if gates.get("eco1_beats_spy") else "✗"
        cal_p = "✓" if gates.get("eco2_calmar") else "✗"
        sh_p = "✓" if gates.get("eco3_sharpe_net") else "✗"
        pre_p = "✓" if gates.get("pre_pass_pending_pbo") else "✗"

        lines.append(
            f"| {r['name']} | {years_str} | {cagr_pct:.2f} | {cagr_net_pct:.2f} |"
            f" {sharpe:.3f} | {sharpe_net:.3f} | {maxdd_pct:.1f} | {calmar:.3f} |"
            f" {wf_str} | {oos_s} | {fwd_s} | {dsr_p} | {beat} | {cal_p} | {sh_p} | {pre_p} |"
        )

    lines += ["", "## SPY benchmark (per-config, same window)", ""]
    for r in results:
        if "error" in r or "spy_benchmark" not in r:
            continue
        bm = r["spy_benchmark"]
        lines.append(
            f"- **{r['name']}** ({r['window_years']:.1f}y): "
            f"SPY CAGR={bm['spy_cagr_gross']*100:.2f}% "
            f"net={bm['spy_cagr_net']*100:.2f}% "
            f"Sharpe={bm['spy_sharpe']:.3f} "
            f"MaxDD={bm['spy_max_dd']*100:.1f}%"
        )

    lines += ["", "## Cross-lib concordance (bt library)", ""]
    for r in results:
        if "error" in r or "cross_lib_bt" not in r:
            continue
        cl = r["cross_lib_bt"]
        if cl.get("concordant") is None:
            lines.append(f"- {r['name']}: bt NOT AVAILABLE")
        elif cl.get("concordant"):
            lines.append(f"- {r['name']}: ✓ CONCORDANT (ΔCAGR={cl['cagr_delta_pp']:.2f}pp)")
        else:
            lines.append(f"- {r['name']}: ✗ DIVERGENT (ΔCAGR={cl['cagr_delta_pp']:.2f}pp)")

    lines += ["", "## Stage 2 — yfinance independent validation", ""]
    for r in results:
        if "error" in r or "stage2" not in r:
            continue
        s2 = r["stage2"]
        if s2.get("concordant") is None:
            lines.append(f"- {r['name']}: Stage 2 UNAVAILABLE")
        elif s2.get("concordant"):
            lines.append(f"- {r['name']}: ✓ CONCORDANT (ΔCAGR={s2['cagr_delta_pp']:.2f}pp)")
        else:
            lines.append(f"- {r['name']}: ✗ DIVERGENT (ΔCAGR={s2['cagr_delta_pp']:.2f}pp)")

    lines += [
        "",
        "## Citations",
        "",
        "- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical",
        "- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate",
        "- `[advances_fin_ml, p.298-299]` — DSR gate",
        "",
        "## Notes",
        "",
        "- PBO gate is aggregate-level (144 trials across Phase 3.5e). Per-ticker PBO with N=3 is",
        "  unreliable (see Phase 3.5d E1 rejection — grid shrinkage artifact). Real PBO at aggregator.",
        "- Pre-pass = all gates except PBO pass. Confirm at aggregator.",
        "- SSO pre-2006 synthetic data per mandate §4: r = L × r_SPX_TR - drag - expense.",
        f"- DSR n_trials = cumulative trial count from trial_count.json at sweep time.",
    ]

    return "\n".join(lines) + "\n"


# ─── trial_count.json update ──────────────────────────────────────────────────

def load_trial_count() -> dict:
    with open(TRIAL_COUNT_PATH) as f:
        return json.load(f)


def update_trial_count(count: dict, n_new: int) -> dict:
    count = count.copy()
    count["total_trials_completed"] += n_new
    count["last_updated"] = datetime.now(timezone.utc).date().isoformat()
    return count


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== Phase 3.5e c01 SSO sweep (iter {ITER_NUM}) ===")
    print(f"  Configs: {[c['name'] for c in CONFIGS]}")
    print(f"  Windows: cash={WINDOW_CASH_START}, GLD={WINDOW_GLD_START}, TLT={WINDOW_TLT_START} → {WINDOW_END}")

    wide = load_wide(PARQUET_PATH, WINDOW_CASH_START, WINDOW_END)
    print(f"  Data loaded: {len(wide)} bars, tickers={sorted(wide.columns.tolist())}")

    required = ["SSO", "SPY", "GLD", "TLT"]
    missing = [t for t in required if t not in wide.columns]
    if missing:
        raise RuntimeError(f"Missing tickers in reference_prices.parquet: {missing}")

    trial_count = load_trial_count()
    trial_start = trial_count["total_trials_completed"]
    print(f"  Trial count before this sweep: {trial_start}")

    results, all_returns = run_all_configs(wide, trial_start)

    pbo_local = compute_local_pbo(all_returns)
    print(f"\n  Per-ticker local PBO (informational): {pbo_local}")

    valid = [r for r in results if "metrics_is" in r]
    if not valid:
        raise RuntimeError("All configs errored out")
    best = max(valid, key=lambda r: r["metrics_is"].get("sharpe", -999))
    best_name = best["name"]
    any_prepass = any(r.get("gates", {}).get("pre_pass_pending_pbo", False) for r in results)

    print(f"\n  Best config: {best_name}")
    print(f"  Any pre-pass (pending PBO): {any_prepass}")
    print(f"  Best Sharpe_IS: {best['metrics_is']['sharpe']:.3f}")
    print(f"  Best Sharpe_net: {best['metrics_is']['sharpe_net']:.3f}")
    print(f"  Best OOS Sharpe: {best['oos']['oos_sharpe']:.3f}")

    best_sharpe_oos = best["oos"]["oos_sharpe"]
    best_cagr = best["metrics_is"]["cagr"]
    best_maxdd = best["metrics_is"]["max_dd"]

    json_path = os.path.join(REPORT_DIR, "SSO.json")
    json_data = {
        "ticker": TICKER,
        "frequency": "daily",
        "phase": PHASE,
        "lead_id": "c01",
        "lead_slug": "c01_sma200_binary_regime",
        "iter": ITER_NUM,
        "source": "reference_prices.parquet (Stage 1, cross_lib copy)",
        "pbo_local": pbo_local,
        "configs": results,
        "best_config": best_name,
        "any_prepass_pending_pbo": bool(any_prepass),
        "best_sharpe_oos": float(best_sharpe_oos),
        "best_cagr": float(best_cagr),
        "best_maxdd": float(best_maxdd),
        "citations": [
            "leverage_for_the_long_run, ch.2",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    md_path = os.path.join(REPORT_DIR, "SSO.md")
    md_text = build_md_report(results, pbo_local)
    atomic_write_text(md_path, md_text)

    n_new = len([r for r in results if "error" not in r])
    new_trial_count = update_trial_count(trial_count, n_new)
    atomic_write_json(TRIAL_COUNT_PATH, new_trial_count)
    print(f"  trial_count updated: {trial_start} → {new_trial_count['total_trials_completed']}")

    reg = load_registry(REGISTRY_PATH)
    ticker_popped, reg = pop_pending(reg)
    assert ticker_popped == TICKER, f"Expected {TICKER}, got {ticker_popped}"

    summary = {
        "ticker": TICKER,
        "frequency": "daily",
        "window_start": WINDOW_CASH_START,
        "window_end": WINDOW_END,
        "iter": ITER_NUM,
        "n_configs_tested": len(CONFIGS),
        "best_config": best_name,
        "best_sharpe_oos": float(best_sharpe_oos),
        "best_cagr": float(best_cagr),
        "best_maxdd": float(best_maxdd),
        "any_pass_5gate": bool(any_prepass),
        "pbo_local": float(pbo_local.get("pbo", float("nan"))),
        "result_file_md": md_path,
        "result_file_json": json_path,
    }
    reg = append_done(reg, summary)
    reg = advance_status(reg)
    atomic_write_registry(REGISTRY_PATH, reg)
    print(f"  Registry updated: status={reg['status']}, pending={reg['tickers_pending']}")
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
