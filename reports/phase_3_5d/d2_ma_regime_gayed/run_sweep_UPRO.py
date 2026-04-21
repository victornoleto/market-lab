"""
D2 MA Regime Filter — UPRO single-ticker sweep iter (iter 5).

Citations:
  [leverage_for_the_long_run, p.13]  — SMA200 regime canonical
  [leverage_for_the_long_run, p.16]  — EMA100 regime variant
  [leverage_for_the_long_run, p.60]  — TMF off-leg optional hedge
  [advances_fin_ml, p.208-211]       — PBO/CSCV gate
  [advances_fin_ml, p.298-299]       — DSR gate

Portfolio: 100% UPRO, MA regime filter on SPY.
Signal ticker: SPY (SPY→UPRO; homogeneous indicator same family as EW run).
Off-leg: cash (0%) / TMF / GLD when flat.
Window: 2010-02-11 → 2026-04-17 (TQQQ seam constraint, Stage 1).
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

# ─── Constants ───────────────────────────────────────────────────────────────
REGISTRY_PATH = "reports/phase_3_5d/d2_ma_regime_gayed/registry.json"
REPORT_DIR = "reports/phase_3_5d/d2_ma_regime_gayed"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
WINDOW_START = "2010-02-11"   # TQQQ seam gap: skip 2010-02-09/10
WINDOW_END = "2026-04-17"
TAX_RATE = 0.15               # 15% IR BR flat on CAGR
TICKER = "UPRO"
ITER_NUM = 5

# SPY B&H reference from D1 baseline
SPY_BH_CAGR_GROSS = 0.1222
SPY_BH_CAGR_NET = SPY_BH_CAGR_GROSS * (1 - TAX_RATE)   # ~10.38%


# ─── Signal functions ────────────────────────────────────────────────────────

def sma_regime(prices: pd.Series, lookback: int = 200) -> pd.Series:
    """SMA-based regime: True when close > SMA(lookback). [lftlr, p.13]"""
    sma = prices.rolling(lookback, min_periods=lookback).mean()
    return (prices > sma).astype(float)


def ema_regime(prices: pd.Series, lookback: int = 100) -> pd.Series:
    """EMA-based regime: True when close > EMA(lookback). [lftlr, p.16]"""
    ema = prices.ewm(span=lookback, adjust=False).mean()
    return (prices > ema).astype(float)


# ─── Data loading ────────────────────────────────────────────────────────────

def load_wide_prices(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    """Load parquet → wide format (index=date, columns=tickers)."""
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


# ─── Portfolio backtest ───────────────────────────────────────────────────────

def run_upro_portfolio(
    prices: pd.DataFrame,
    indicator: str,   # "SMA" or "EMA"
    lookback: int,    # 200 for SMA, 100 for EMA
    off_leg: str,     # "cash", "TMF", or "GLD"
) -> pd.Series:
    """
    Single-asset UPRO with MA regime filter.

    Signal: SPY SMA/EMA regime [leverage_for_the_long_run, p.13,p.16].
    When signal=FLAT, allocation shifts to off_leg (cash/TMF/GLD).
    Signal is shifted by 1 bar to avoid lookahead bias.
    """
    if indicator == "SMA":
        sig = sma_regime(prices["SPY"], lookback).shift(1).fillna(0)
    else:  # EMA
        sig = ema_regime(prices["SPY"], lookback).shift(1).fillna(0)

    ret_upro = prices["UPRO"].pct_change()

    if off_leg == "cash":
        ret_off = pd.Series(0.0, index=prices.index)
    elif off_leg == "TMF":
        ret_off = prices["TMF"].pct_change()
    elif off_leg == "GLD":
        ret_off = prices["GLD"].pct_change()
    else:
        raise ValueError(f"Unknown off_leg: {off_leg}")

    port = sig * ret_upro + (1 - sig) * ret_off
    return port.dropna()


def run_upro_portfolio_bt(
    prices: pd.DataFrame,
    indicator: str,
    lookback: int,
    off_leg: str,
) -> pd.Series | None:
    """Cross-lib: run same strategy in bt library for concordance check."""
    try:
        import bt  # type: ignore
    except ImportError:
        return None

    try:
        if indicator == "SMA":
            sig = sma_regime(prices["SPY"], lookback).shift(1).fillna(0)
        else:
            sig = ema_regime(prices["SPY"], lookback).shift(1).fillna(0)

        exec_tickers = ["UPRO"]
        if off_leg != "cash":
            exec_tickers.append(off_leg)

        exec_prices = prices[exec_tickers].copy()

        weights = pd.DataFrame(0.0, index=prices.index, columns=exec_tickers)
        weights["UPRO"] = sig
        if off_leg != "cash":
            weights[off_leg] = 1 - sig

        strat = bt.Strategy(
            "upro_regime",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["upro_regime"].rename("equity")
        return equity
    except Exception as e:
        print(f"  [bt cross-lib] error: {e}", file=sys.stderr)
        return None


# ─── Metrics ─────────────────────────────────────────────────────────────────

def compute_cagr(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years < 0.5:
        return float("nan")
    return float((equity.iloc[-1]) ** (1 / years) - 1)


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
    """Sharpe per split, count of positive. [AFML, ch.12 — WF gate]"""
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
    """Single-block OOS: last 20% of data reserved. Gate: OOS Sharpe ≥ 0.5×IS."""
    n = len(returns)
    split = int(n * 0.8)
    is_ret = returns.iloc[:split]
    oos_ret = returns.iloc[split:]
    is_sharpe = compute_sharpe(is_ret)
    oos_sharpe = compute_sharpe(oos_ret)
    oos_pass = np.isfinite(oos_sharpe) and np.isfinite(is_sharpe) and oos_sharpe >= 0.5 * is_sharpe
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


# ─── SPY benchmark ───────────────────────────────────────────────────────────

def compute_spy_benchmark(prices: pd.DataFrame, port_returns: pd.Series) -> dict:
    spy = prices["SPY"].pct_change().reindex(port_returns.index).dropna()
    spy_cagr = compute_cagr(spy)
    spy_cagr_net = spy_cagr * (1 - TAX_RATE)
    spy_sharpe = compute_sharpe(spy)
    spy_max_dd = compute_max_dd(spy)
    corr = float(port_returns.corr(spy)) if len(spy) == len(port_returns) else float("nan")
    return {
        "spy_cagr": spy_cagr,
        "spy_cagr_net": spy_cagr_net,
        "spy_sharpe": spy_sharpe,
        "spy_max_dd": spy_max_dd,
        "corr_vs_spy": corr,
    }


# ─── Stage 2 — yfinance independent fetch ────────────────────────────────────

def run_stage2_validation(
    indicator: str, lookback: int, off_leg: str
) -> dict | None:
    """Fetch UPRO/SPY/TMF/GLD from yfinance, run same config."""
    try:
        import yfinance as yf  # type: ignore

        tickers_needed = ["UPRO", "SPY"]
        if off_leg != "cash":
            tickers_needed.append(off_leg)

        raw = yf.download(
            tickers_needed,
            start=WINDOW_START,
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
        port = run_upro_portfolio(close, indicator, lookback, off_leg)
        cagr2 = compute_cagr(port)
        return {"cagr_stage2": float(cagr2)}
    except Exception as e:
        print(f"  [Stage 2] error: {e}", file=sys.stderr)
        return None


# ─── Main backtest loop ───────────────────────────────────────────────────────

def run_all_configs(prices: pd.DataFrame) -> dict[str, Any]:
    """Run all 6 D2 configs on UPRO single-ticker. Return per-config results."""
    configs = [
        ("sma200_cash", "SMA", 200, "cash"),
        ("ema100_cash", "EMA", 100, "cash"),
        ("sma200_tmf",  "SMA", 200, "TMF"),
        ("ema100_tmf",  "EMA", 100, "TMF"),
        ("sma200_gld",  "SMA", 200, "GLD"),
        ("ema100_gld",  "EMA", 100, "GLD"),
    ]

    all_returns: dict[str, pd.Series] = {}
    results: list[dict] = []

    print(f"  Running {len(configs)} configs on UPRO ...")
    for name, indicator, lookback, off_leg in configs:
        print(f"  → {name}", end=" ")
        try:
            port = run_upro_portfolio(prices, indicator, lookback, off_leg)
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

            # Cross-lib: bt
            bt_equity = run_upro_portfolio_bt(prices, indicator, lookback, off_leg)
            if bt_equity is not None:
                bt_rets = bt_equity.pct_change().dropna()
                bt_cagr = compute_cagr(bt_rets)
                bt_sharpe = compute_sharpe(bt_rets)
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = cagr_delta <= 3.0
            else:
                bt_cagr = float("nan")
                bt_sharpe = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            # Stage 2 yfinance
            stage2 = run_stage2_validation(indicator, lookback, off_leg)
            if stage2:
                stage2_delta = abs(cagr - stage2["cagr_stage2"]) * 100
                stage2_ok = stage2_delta <= 3.0
            else:
                stage2_delta = float("nan")
                stage2_ok = None

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}% "
                f"Sharpe={sharpe:.3f} MaxDD={max_dd*100:.1f}% "
                f"Calmar={calmar:.3f} WF={wf_positive}/8"
            )

            results.append({
                "name": name,
                "indicator": indicator,
                "lookback": lookback,
                "off_leg": off_leg,
                "metrics_is": {
                    "cagr": cagr,
                    "cagr_net": cagr_net,
                    "sharpe": sharpe,
                    "sharpe_net": sharpe_net,
                    "max_dd": max_dd,
                    "calmar": calmar,
                    "n_bars": len(port),
                },
                "wf": {
                    "sharpes": wf_sharpes,
                    "positive": wf_positive,
                    "pass": wf_pass,
                },
                "oos": oos,
                "fwd": fwd,
                "spy_benchmark": spy_bm,
                "cross_lib_bt": {
                    "bt_cagr": bt_cagr,
                    "bt_sharpe": bt_sharpe,
                    "cagr_delta_pp": cagr_delta,
                    "concordant": cross_lib_ok,
                },
                "stage2": {
                    "cagr_stage2": stage2["cagr_stage2"] if stage2 else float("nan"),
                    "cagr_delta_pp": stage2_delta,
                    "concordant": stage2_ok,
                },
                "economic_gates": {
                    "beats_spy_net": bool(cagr_net > SPY_BH_CAGR_NET),
                    "calmar_pass": bool(calmar > 0.5),
                    "sharpe_net_pass": bool(sharpe_net > 0.8),
                },
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append({
                "name": name,
                "indicator": indicator,
                "lookback": lookback,
                "off_leg": off_leg,
                "error": str(e),
            })

    return {"configs": results, "all_returns": all_returns}


def compute_pbo_gate(all_returns: dict[str, pd.Series]) -> dict:
    """PBO across all valid configs. [advances_fin_ml, p.208-211]"""
    names = [k for k, v in all_returns.items() if len(v) > 0]
    if len(names) < 2:
        return {"pbo": float("nan"), "pass": None, "note": "< 2 configs"}

    dfs = [all_returns[n].rename(n) for n in names]
    combined = pd.concat(dfs, axis=1).dropna()
    if combined.shape[1] < 2 or len(combined) < 100:
        return {"pbo": float("nan"), "pass": None, "note": "insufficient data"}

    matrix = combined.values  # T×N
    result = compute_pbo_cscv(matrix, n_blocks=10)
    pbo_val = float(result.pbo)
    return {
        "pbo": pbo_val,
        "n_combinations": result.n_combinations,
        "pass": bool(pbo_val < 0.5),
        "note": f"PBO={pbo_val:.3f} ({'PASS' if pbo_val < 0.5 else 'FAIL'})",
    }


def compute_dsr_per_config(port: pd.Series, n_configs: int) -> dict:
    """DSR: deflated Sharpe for multiple testing. [advances_fin_ml, p.298-299]"""
    try:
        result = compute_dsr(port.values, n_trials=max(n_configs, 2))
        return {
            "dsr": float(result.dsr),
            "p_value": float(result.p_value),
            "pass": bool(result.p_value < 0.05),
        }
    except Exception as e:
        return {"dsr": float("nan"), "p_value": float("nan"), "pass": False, "error": str(e)}


# ─── Gate summary ─────────────────────────────────────────────────────────────

def gate_summary(result: dict, pbo: dict, dsr: dict) -> dict:
    """Aggregate all 5 overfit gates + economic gates."""
    wf = result.get("wf", {})
    oos = result.get("oos", {})
    fwd = result.get("fwd", {})
    eco = result.get("economic_gates", {})

    gate1_pbo = pbo.get("pass", False) or False
    gate2_dsr = dsr.get("pass", False) or False
    gate3_wf = wf.get("pass", False) or False
    gate4_oos = oos.get("oos_pass", False) or False
    gate5_fwd = fwd.get("fwd_pass", False) or False
    overfit_pass = gate1_pbo and gate2_dsr and gate3_wf and gate4_oos and gate5_fwd

    eco1_spy = eco.get("beats_spy_net", False) or False
    eco2_calmar = eco.get("calmar_pass", False) or False
    eco3_sharpe = eco.get("sharpe_net_pass", False) or False
    eco_pass = eco1_spy and eco2_calmar and eco3_sharpe

    all_pass = overfit_pass and eco_pass

    fail_parts = []
    if not gate1_pbo: fail_parts.append("PBO")
    if not gate2_dsr: fail_parts.append("DSR")
    if not gate3_wf: fail_parts.append("WF")
    if not gate4_oos: fail_parts.append("OOS")
    if not gate5_fwd: fail_parts.append("FWD")
    if not eco1_spy: fail_parts.append("SPY_BEAT")
    if not eco2_calmar: fail_parts.append("CALMAR")
    if not eco3_sharpe: fail_parts.append("SHARPE_NET")

    return {
        "gate1_pbo": gate1_pbo,
        "gate2_dsr": gate2_dsr,
        "gate3_wf": gate3_wf,
        "gate4_oos": gate4_oos,
        "gate5_fwd": gate5_fwd,
        "overfit_pass": overfit_pass,
        "eco1_beats_spy": eco1_spy,
        "eco2_calmar": eco2_calmar,
        "eco3_sharpe_net": eco3_sharpe,
        "eco_pass": eco_pass,
        "ALL_PASS": all_pass,
        "fail_reason": "PASS" if all_pass else ", ".join(fail_parts),
    }


# ─── File writers ──────────────────────────────────────────────────────────────

def write_ticker_json(path: str, data: dict) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


def write_ticker_md(path: str, results: list[dict], pbo: dict, window: dict) -> None:
    """Human-readable Markdown report."""
    best = max(
        (r for r in results if "metrics_is" in r),
        key=lambda r: r["metrics_is"].get("sharpe", -999),
        default=None,
    )
    best_name = best["name"] if best else "N/A"
    any_all_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    lines = [
        f"# UPRO daily — D2 MA Regime Gayed (iter {ITER_NUM}) [SWING BROKER]",
        "",
        f"**Window:** {window['start']} → {window['end']} ({window['years']:.1f}y, reference_prices.parquet Stage 1)",
        f"**Portfolio:** 100% UPRO, MA regime filter on SPY",
        f"**Best config:** `{best_name}` — **{'PASS' if any_all_pass else 'NO PASS'}**",
        f"**PBO:** {pbo.get('pbo', float('nan')):.3f} ({'PASS' if pbo.get('pass') else 'FAIL'})",
        "",
        "Citations: [leverage_for_the_long_run, p.13, p.16, p.60]",
        "  [advances_fin_ml, p.208-211, p.298-299]",
        "",
        "## All configs tested",
        "",
        "| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Calmar>0.5 | Sharpe_net>0.8 | PASS |",
        "|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|-----------|----------------|------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | ERROR | — | — | — | — | — | — | — | — | — | — | — | — | — | ✗ |")
            continue
        m = r.get("metrics_is", {})
        wf = r.get("wf", {})
        oos = r.get("oos", {})
        fwd = r.get("fwd", {})
        eco = r.get("economic_gates", {})
        gates = r.get("gates", {})
        dsr_r = r.get("dsr", {})

        cagr_pct = m.get("cagr", float("nan")) * 100
        cagr_net_pct = m.get("cagr_net", float("nan")) * 100
        sharpe = m.get("sharpe", float("nan"))
        sharpe_net = m.get("sharpe_net", float("nan"))
        maxdd_pct = m.get("max_dd", float("nan")) * 100
        calmar = m.get("calmar", float("nan"))
        wf_str = f"{wf.get('positive', 0)}/8"
        oos_s = f"{oos.get('oos_sharpe', float('nan')):.2f}"
        fwd_s = f"{fwd.get('fwd_sharpe', float('nan')):.2f}"
        pbo_str = f"{pbo.get('pbo', float('nan')):.3f}"
        dsr_str = f"{dsr_r.get('p_value', float('nan')):.3f}"
        beat = "✓" if eco.get("beats_spy_net") else "✗"
        cal_p = "✓" if eco.get("calmar_pass") else "✗"
        sh_p = "✓" if eco.get("sharpe_net_pass") else "✗"
        all_p = "✓" if gates.get("ALL_PASS") else "✗"

        lines.append(
            f"| {r['name']} | {cagr_pct:.2f} | {cagr_net_pct:.2f} | {sharpe:.3f} | {sharpe_net:.3f} |"
            f" {maxdd_pct:.1f} | {calmar:.3f} | {wf_str} | {oos_s} | {fwd_s} |"
            f" {pbo_str} | {dsr_str} | {beat} | {cal_p} | {sh_p} | {all_p} |"
        )

    lines += [
        "",
        "## SPY Benchmark (D1 reference)",
        "",
        f"| SPY CAGR% | SPY CAGR_net% | SPY Sharpe | SPY MaxDD% |",
        f"|-----------|--------------|------------|-----------|",
        f"| {SPY_BH_CAGR_GROSS*100:.2f} | {SPY_BH_CAGR_NET*100:.2f} | 0.756 | 34.1 |",
        "",
        "## Cross-lib concordance (bt library)",
        "",
    ]

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

    lines += [
        "",
        "## Stage 2 — yfinance independent validation",
        "",
    ]
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

    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== D2 UPRO sweep iter {ITER_NUM} ===")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")

    # 1. Load data
    prices = load_wide_prices(PARQUET_PATH, WINDOW_START, WINDOW_END)
    print(f"  Prices loaded: {len(prices)} bars, tickers={list(prices.columns)}")

    required = ["UPRO", "SPY", "TMF", "GLD"]
    missing = [t for t in required if t not in prices.columns]
    if missing:
        raise RuntimeError(f"Missing tickers in reference_prices.parquet: {missing}")

    window_info = {
        "start": WINDOW_START,
        "end": WINDOW_END,
        "n_bars": len(prices),
        "years": (prices.index[-1] - prices.index[0]).days / 365.25,
    }

    # 2. Run all 6 configs
    outcome = run_all_configs(prices)
    results = outcome["configs"]
    all_returns = outcome["all_returns"]

    # 3. PBO (multi-config) [AFML p.208-211]
    pbo_result = compute_pbo_gate(all_returns)
    print(f"  PBO: {pbo_result}")

    # 4. DSR per config + attach gates [AFML p.298-299]
    n_configs = len(results)
    for r in results:
        if "error" in r or r["name"] not in all_returns:
            r["dsr"] = {"dsr": float("nan"), "p_value": float("nan"), "pass": False}
            r["gates"] = {"ALL_PASS": False, "fail_reason": "error"}
            continue
        port = all_returns[r["name"]]
        r["dsr"] = compute_dsr_per_config(port, n_configs)
        r["gates"] = gate_summary(r, pbo_result, r["dsr"])
        print(
            f"  {r['name']}: gates={r['gates']['fail_reason']} "
            f"DSR_p={r['dsr']['p_value']:.3f}"
        )

    # 5. Find best config by IS Sharpe
    valid = [r for r in results if "metrics_is" in r]
    best = max(valid, key=lambda r: r["metrics_is"].get("sharpe", -999), default=None)
    best_name = best["name"] if best else "N/A"
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)
    best_sharpe_oos = best["oos"]["oos_sharpe"] if best else float("nan")
    best_cagr = best["metrics_is"]["cagr"] if best else float("nan")
    best_maxdd = best["metrics_is"]["max_dd"] if best else float("nan")

    print(f"\n  Best config: {best_name}")
    print(f"  Any ALL_PASS: {any_pass}")

    # 6. Write UPRO.json (atomic)
    json_path = os.path.join(REPORT_DIR, "UPRO.json")
    json_data = {
        "ticker": TICKER,
        "frequency": "daily",
        "window": window_info,
        "stage": 1,
        "source": "reference_prices.parquet (seam-corrected)",
        "pbo": pbo_result,
        "configs": results,
        "best_config": best_name,
        "any_pass_5gate": any_pass,
        "best_sharpe_oos": best_sharpe_oos,
        "best_cagr": best_cagr,
        "best_maxdd": best_maxdd,
        "citations": [
            "leverage_for_the_long_run, p.13",
            "leverage_for_the_long_run, p.16",
            "leverage_for_the_long_run, p.60",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_ticker_json(json_path, json_data)

    # 7. Write UPRO.md (atomic)
    md_path = os.path.join(REPORT_DIR, "UPRO.md")
    write_ticker_md(md_path, results, pbo_result, window_info)

    # 8. Update registry: pop UPRO from pending, advance status
    reg = load_registry(REGISTRY_PATH)
    ticker_popped, reg = pop_pending(reg)
    assert ticker_popped == TICKER, f"Expected {TICKER}, got {ticker_popped}"

    summary = {
        "ticker": TICKER,
        "frequency": "daily",
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
        "iter": ITER_NUM,
        "n_configs_tested": n_configs,
        "best_config": best_name,
        "best_sharpe_oos": float(best_sharpe_oos),
        "best_cagr": float(best_cagr),
        "best_maxdd": float(best_maxdd),
        "any_pass_5gate": bool(any_pass),
        "pbo": float(pbo_result.get("pbo", float("nan"))),
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
