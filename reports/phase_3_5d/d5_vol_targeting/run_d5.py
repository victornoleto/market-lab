"""
D5 — Volatility Targeting on TQQQ+GLD (atomic lead, iter 9).

Strategy: Continuous vol-scaled exposure to TQQQ.
  weight_TQQQ = min(1.0, target_vol_annual / realized_vol_TQQQ_annual)
  weight_GLD  = 1 - weight_TQQQ
Rebalance daily. Signal shifted 1 bar to avoid lookahead.

For combo config: SMA200 overlay zeroes TQQQ weight when SPY < SMA200.

Citations:
  [advances_fin_ml, ch.14]       — risk-adjusted sizing / volatility targeting
  [volatility_trading]           — realized vol estimation, target vol mechanics
  [leverage_for_the_long_run, p.13] — SMA200 regime overlay rationale
  [advances_fin_ml, p.208-211]   — PBO/CSCV gate
  [advances_fin_ml, p.298-299]   — DSR gate

Configs tested (6 base + 1 overlay):
  vol15_lk10:      target=15%, lookback=10d
  vol15_lk20:      target=15%, lookback=20d
  vol15_lk30:      target=15%, lookback=30d
  vol20_lk10:      target=20%, lookback=10d
  vol20_lk20:      target=20%, lookback=20d
  vol20_lk30:      target=20%, lookback=30d
  best_sma200:     best base config + SMA200(SPY) on/off overlay

Window: 2004-11-18 → 2026-04-15 (longest TQQQ+GLD common window, ~21.4yr)
Off-leg: GLD only (TMF eliminated in D2, cash suboptimal vs GLD per D2 results)
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

# ─── Constants ────────────────────────────────────────────────────────────────
REPORT_DIR = "reports/phase_3_5d/d5_vol_targeting"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
WINDOW_START = "2004-11-18"   # Longest TQQQ+GLD common window
WINDOW_END = "2026-04-15"
TAX_RATE = 0.15               # 15% IR BR flat on CAGR [investment-mandate §1]
ITER_NUM = 9

# Base configs: (name, target_vol_annual, lookback_days)
BASE_CONFIGS = [
    ("vol15_lk10", 0.15, 10),
    ("vol15_lk20", 0.15, 20),
    ("vol15_lk30", 0.15, 30),
    ("vol20_lk10", 0.20, 10),
    ("vol20_lk20", 0.20, 20),
    ("vol20_lk30", 0.20, 30),
]
# SMA200 overlay config key — determined dynamically from best base config
SMA200_OVERLAY_NAME = "best_sma200"
SMA200_LOOKBACK = 200


# ─── Signal ───────────────────────────────────────────────────────────────────

def vol_target_weight(tqqq_prices: pd.Series, target_vol: float, lookback: int) -> pd.Series:
    """
    Compute continuous TQQQ allocation weight via volatility targeting.
    [advances_fin_ml, ch.14], [volatility_trading]

    realized_vol = rolling std of daily returns * sqrt(252)
    weight = min(1.0, target_vol / realized_vol)
    Returns are NOT shifted here; caller shifts by 1 bar for execution.
    """
    daily_ret = tqqq_prices.pct_change()
    # Use 'population' std (ddof=1 is fine for daily) * sqrt(252) for annualized vol
    realized_vol = daily_ret.rolling(lookback, min_periods=lookback).std() * np.sqrt(252)
    # Avoid division by near-zero (dead markets / startup)
    realized_vol = realized_vol.replace(0, np.nan)
    weight = (target_vol / realized_vol).clip(upper=1.0)
    return weight.fillna(0.0)


def sma200_regime_mask(spy_prices: pd.Series, sma_period: int = 200) -> pd.Series:
    """
    Regime mask: 1.0 when SPY is above its SMA, 0.0 otherwise.
    [leverage_for_the_long_run, p.13]
    Not shifted here; caller shifts with weight.
    """
    sma = spy_prices.rolling(sma_period, min_periods=sma_period).mean()
    mask = (spy_prices > sma).astype(float)
    mask = mask.where(sma.notna(), other=0.0)
    return mask


# ─── Data loading ─────────────────────────────────────────────────────────────

def load_wide_prices(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


# ─── Portfolio backtest ────────────────────────────────────────────────────────

def run_portfolio(
    prices: pd.DataFrame,
    target_vol: float,
    lookback: int,
    sma200_overlay: bool = False,
) -> tuple[pd.Series, pd.Series]:
    """
    Returns (portfolio_returns, weight_series).
    Signal shifted 1 bar to avoid lookahead bias.
    """
    weight = vol_target_weight(prices["TQQQ"], target_vol, lookback)

    if sma200_overlay:
        regime = sma200_regime_mask(prices["SPY"], SMA200_LOOKBACK)
        weight = weight * regime

    # Execute on next bar (shift 1)
    w = weight.shift(1).fillna(0.0)

    ret_tqqq = prices["TQQQ"].pct_change()
    ret_gld = prices["GLD"].pct_change()

    port = w * ret_tqqq + (1.0 - w) * ret_gld
    return port.dropna(), w.reindex(port.index).fillna(0.0)


def run_portfolio_bt(
    prices: pd.DataFrame,
    target_vol: float,
    lookback: int,
    sma200_overlay: bool = False,
) -> pd.Series | None:
    """Cross-lib concordance via bt library."""
    try:
        import bt  # type: ignore
    except ImportError:
        return None

    try:
        weight = vol_target_weight(prices["TQQQ"], target_vol, lookback)
        if sma200_overlay:
            regime = sma200_regime_mask(prices["SPY"], SMA200_LOOKBACK)
            weight = weight * regime

        exec_prices = prices[["TQQQ", "GLD"]].copy()
        weights = pd.DataFrame(0.0, index=prices.index, columns=["TQQQ", "GLD"])
        weights["TQQQ"] = weight.shift(1).fillna(0.0)
        weights["GLD"] = 1.0 - weights["TQQQ"]

        strat = bt.Strategy(
            "vol_tgt",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["vol_tgt"].rename("equity")
        return equity
    except Exception as e:
        print(f"  [bt cross-lib] error: {e}", file=sys.stderr)
        return None


# ─── Metrics ──────────────────────────────────────────────────────────────────

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
    """Walk-forward: count splits with positive Sharpe. [AFML ch.12]"""
    n = len(returns)
    if n < n_splits * 63:
        return [], 0
    split_size = n // n_splits
    sharpes = [
        compute_sharpe(returns.iloc[i * split_size : (i + 1) * split_size])
        for i in range(n_splits)
    ]
    positive = sum(1 for s in sharpes if np.isfinite(s) and s > 0)
    return sharpes, positive


def compute_oos_holdout(returns: pd.Series) -> dict:
    """Single-block OOS: last 20% reserved. Gate: OOS Sharpe ≥ 0.5×IS."""
    n = len(returns)
    split = int(n * 0.8)
    is_ret = returns.iloc[:split]
    oos_ret = returns.iloc[split:]
    is_sharpe = compute_sharpe(is_ret)
    oos_sharpe = compute_sharpe(oos_ret)
    oos_pass = (
        np.isfinite(oos_sharpe) and np.isfinite(is_sharpe) and oos_sharpe >= 0.5 * is_sharpe
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
        "spy_cagr": spy_cagr,
        "spy_cagr_net": spy_cagr_net,
        "spy_sharpe": spy_sharpe,
        "spy_max_dd": spy_max_dd,
        "corr_vs_spy": corr,
    }


# ─── Stage 2 — yfinance ────────────────────────────────────────────────────────

def run_stage2_validation(
    target_vol: float, lookback: int, sma200_overlay: bool = False
) -> dict | None:
    """Fetch TQQQ/GLD/SPY from yfinance, run same config."""
    try:
        import yfinance as yf  # type: ignore

        tickers = ["TQQQ", "GLD", "SPY"] if sma200_overlay else ["TQQQ", "GLD"]
        raw = yf.download(
            tickers,
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
            close = raw[["Close"]]
        close = close.dropna(how="all")
        port, _ = run_portfolio(close, target_vol, lookback, sma200_overlay=sma200_overlay)
        return {"cagr_stage2": float(compute_cagr(port))}
    except Exception as e:
        print(f"  [Stage 2] error: {e}", file=sys.stderr)
        return None


# ─── PBO / DSR gates ──────────────────────────────────────────────────────────

def compute_pbo_gate(all_returns: dict[str, pd.Series]) -> dict:
    """PBO across all valid configs. [advances_fin_ml, p.208-211]"""
    names = [k for k, v in all_returns.items() if len(v) > 0]
    if len(names) < 2:
        return {"pbo": float("nan"), "pass": None, "note": "< 2 configs"}
    combined = pd.concat([all_returns[n].rename(n) for n in names], axis=1).dropna()
    if combined.shape[1] < 2 or len(combined) < 100:
        return {"pbo": float("nan"), "pass": None, "note": "insufficient data"}
    result = compute_pbo_cscv(combined.values, n_blocks=10)
    pbo_val = float(result.pbo)
    return {"pbo": pbo_val, "n_combinations": result.n_combinations, "pass": bool(pbo_val < 0.5)}


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


# ─── Gate summary ──────────────────────────────────────────────────────────────

def gate_summary(result: dict, pbo: dict, dsr: dict, spy_cagr_net: float) -> dict:
    """Aggregate all overfit + economic gates."""
    m = result.get("metrics_is", {})
    wf = result.get("wf", {})
    oos = result.get("oos", {})
    fwd = result.get("fwd", {})

    cagr_net = m.get("cagr_net", 0.0)
    calmar = m.get("calmar", 0.0)
    sharpe_net = m.get("sharpe_net", 0.0)

    g1_pbo = bool(pbo.get("pass", False))
    g2_dsr = bool(dsr.get("pass", False))
    g3_wf = bool(wf.get("pass", False))
    g4_oos = bool(oos.get("oos_pass", False))
    g5_fwd = bool(fwd.get("fwd_pass", False))
    overfit_pass = g1_pbo and g2_dsr and g3_wf and g4_oos and g5_fwd

    e1_spy = bool(np.isfinite(cagr_net) and cagr_net > spy_cagr_net)
    e2_calmar = bool(np.isfinite(calmar) and calmar > 0.5)
    e3_sharpe = bool(np.isfinite(sharpe_net) and sharpe_net > 0.8)
    eco_pass = e1_spy and e2_calmar and e3_sharpe

    all_pass = overfit_pass and eco_pass

    fail_parts = [
        name
        for name, ok in [
            ("PBO", g1_pbo),
            ("DSR", g2_dsr),
            ("WF", g3_wf),
            ("OOS", g4_oos),
            ("FWD", g5_fwd),
            ("SPY_BEAT", e1_spy),
            ("CALMAR", e2_calmar),
            ("SHARPE_NET", e3_sharpe),
        ]
        if not ok
    ]

    return {
        "gate1_pbo": g1_pbo,
        "gate2_dsr": g2_dsr,
        "gate3_wf": g3_wf,
        "gate4_oos": g4_oos,
        "gate5_fwd": g5_fwd,
        "overfit_pass": overfit_pass,
        "eco1_beats_spy": e1_spy,
        "eco2_calmar": e2_calmar,
        "eco3_sharpe_net": e3_sharpe,
        "eco_pass": eco_pass,
        "ALL_PASS": all_pass,
        "fail_reason": "PASS" if all_pass else ", ".join(fail_parts),
    }


# ─── File writers ──────────────────────────────────────────────────────────────

def atomic_write_json(path: str, data: dict) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


def write_report_md(
    path: str,
    results: list[dict],
    pbo: dict,
    window: dict,
    spy_cagr_net: float,
) -> None:
    best = max(
        (r for r in results if "metrics_is" in r),
        key=lambda r: r["metrics_is"].get("sharpe", -999),
        default=None,
    )
    best_name = best["name"] if best else "N/A"
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    lines = [
        f"# D5 Volatility Targeting — TQQQ+GLD (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** Continuous vol-scaled TQQQ exposure; GLD fills remainder",
        "  weight_TQQQ = min(1.0, target_vol / realized_vol_TQQQ)",
        f"**Window:** {window['start']} → {window['end']} ({window['years']:.1f}yr,"
        " reference_prices.parquet Stage 1)",
        "**Portfolio:** TQQQ (vol-scaled on-regime) + GLD (complement); daily rebalance",
        f"**Best config:** `{best_name}` — **{'✓ ALL PASS' if any_pass else 'NO PASS'}**",
        f"**PBO:** {pbo.get('pbo', float('nan')):.3f} ({'PASS' if pbo.get('pass') else 'FAIL'})",
        "",
        "Citations: [advances_fin_ml, ch.14], [volatility_trading],",
        "  [leverage_for_the_long_run, p.13], [advances_fin_ml, p.208-211, p.298-299]",
        "",
        "## Results",
        "",
        "| Config | TV% | LB | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar |"
        " WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |",
        "|--------|-----|-----|-------|-----------|--------|------------|--------|--------"
        "|----|-------|-------|-----|-------|----------|---------|--------|------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(
                f"| {r['name']} | — | — | ERROR | — | — | — | — | — | — | — | — | — | — | — | — | — | ✗ |"
            )
            continue
        m = r.get("metrics_is", {})
        wf = r.get("wf", {})
        oos = r.get("oos", {})
        fwd = r.get("fwd", {})
        gates = r.get("gates", {})
        dsr_r = r.get("dsr", {})

        tv_pct = r.get("target_vol", 0.0) * 100
        lb = r.get("lookback", 0)

        lines.append(
            f"| {r['name']} | {tv_pct:.0f} | {lb} |"
            f" {m.get('cagr', float('nan'))*100:.2f} | {m.get('cagr_net', float('nan'))*100:.2f} |"
            f" {m.get('sharpe', float('nan')):.3f} | {m.get('sharpe_net', float('nan')):.3f} |"
            f" {m.get('max_dd', float('nan'))*100:.1f} | {m.get('calmar', float('nan')):.3f} |"
            f" {wf.get('positive', 0)}/8 | {oos.get('oos_sharpe', float('nan')):.2f} |"
            f" {fwd.get('fwd_sharpe', float('nan')):.2f} |"
            f" {pbo.get('pbo', float('nan')):.3f} | {dsr_r.get('p_value', float('nan')):.3f} |"
            f" {'✓' if gates.get('eco1_beats_spy') else '✗'} |"
            f" {'✓' if gates.get('eco2_calmar') else '✗'} |"
            f" {'✓' if gates.get('eco3_sharpe_net') else '✗'} |"
            f" {'✓' if gates.get('ALL_PASS') else '✗'} |"
        )

    lines += [
        "",
        f"**SPY B&H net CAGR threshold:** {spy_cagr_net*100:.2f}% (15% IR BR applied)",
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
        "## Average TQQQ weight (time-in-market proxy)",
        "",
        "| Config | Avg TQQQ weight% | Min weight% | Max weight% |",
        "|--------|------------------|-------------|-------------|",
    ]
    for r in results:
        if "error" in r or "weight_stats" not in r:
            continue
        ws = r["weight_stats"]
        lines.append(
            f"| {r['name']} | {ws['mean']*100:.1f} | {ws['min']*100:.1f} | {ws['max']*100:.1f} |"
        )

    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main() -> dict:
    print(f"\n=== D5 Volatility Targeting TQQQ+GLD — iter {ITER_NUM} ===")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")

    # 1. Load data
    prices = load_wide_prices(PARQUET_PATH, WINDOW_START, WINDOW_END)
    print(f"  Prices loaded: {len(prices)} bars, tickers={list(prices.columns)}")

    required = ["TQQQ", "GLD", "SPY"]
    missing = [t for t in required if t not in prices.columns]
    if missing:
        raise RuntimeError(f"Missing tickers in reference_prices.parquet: {missing}")

    window_info = {
        "start": WINDOW_START,
        "end": WINDOW_END,
        "n_bars": len(prices),
        "years": (prices.index[-1] - prices.index[0]).days / 365.25,
    }
    print(f"  Window: {window_info['years']:.2f} years")

    # 2. Compute SPY B&H benchmark for this window
    spy_ret = prices["SPY"].pct_change().dropna()
    spy_cagr_actual = compute_cagr(spy_ret)
    spy_cagr_net_actual = spy_cagr_actual * (1 - TAX_RATE)
    spy_sharpe_actual = compute_sharpe(spy_ret)
    spy_max_dd_actual = compute_max_dd(spy_ret)
    print(
        f"  SPY B&H: CAGR={spy_cagr_actual*100:.2f}% net={spy_cagr_net_actual*100:.2f}%"
        f" Sharpe={spy_sharpe_actual:.3f} MaxDD={spy_max_dd_actual*100:.1f}%"
    )

    # 3. Run 6 base configs
    all_returns: dict[str, pd.Series] = {}
    results: list[dict] = []

    print(f"\n  Running {len(BASE_CONFIGS)} base configs ...")
    for name, target_vol, lookback in BASE_CONFIGS:
        print(f"  → {name} (target_vol={target_vol*100:.0f}%, lb={lookback}d)", end=" ")
        try:
            port, w_series = run_portfolio(prices, target_vol, lookback, sma200_overlay=False)
            all_returns[name] = port

            cagr = compute_cagr(port)
            cagr_net = cagr * (1 - TAX_RATE)
            sharpe = compute_sharpe(port)
            sharpe_net = sharpe * (1 - TAX_RATE)
            max_dd = compute_max_dd(port)
            calmar = compute_calmar(cagr, max_dd)

            wf_sharpes, wf_positive = compute_wf(port, n_splits=8)
            oos = compute_oos_holdout(port)
            fwd = compute_fwd_stress(port)
            spy_bm = compute_spy_benchmark(prices, port)

            weight_stats = {
                "mean": float(w_series.mean()),
                "min": float(w_series.min()),
                "max": float(w_series.max()),
                "std": float(w_series.std()),
            }

            # Cross-lib: bt
            bt_equity = run_portfolio_bt(prices, target_vol, lookback, sma200_overlay=False)
            if bt_equity is not None:
                bt_rets = bt_equity.pct_change().dropna()
                bt_cagr = compute_cagr(bt_rets)
                bt_sharpe = compute_sharpe(bt_rets)
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = bool(cagr_delta <= 3.0)
            else:
                bt_cagr = float("nan")
                bt_sharpe = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            # Stage 2 yfinance
            stage2 = run_stage2_validation(target_vol, lookback, sma200_overlay=False)
            if stage2:
                stage2_delta = abs(cagr - stage2["cagr_stage2"]) * 100
                stage2_ok = bool(stage2_delta <= 3.0)
            else:
                stage2_delta = float("nan")
                stage2_ok = None

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%"
                f" Sharpe={sharpe:.3f} SN={sharpe_net:.3f}"
                f" MaxDD={max_dd*100:.1f}% Calmar={calmar:.3f} WF={wf_positive}/8"
                f" AvgW={weight_stats['mean']*100:.0f}%"
            )

            results.append(
                {
                    "name": name,
                    "target_vol": target_vol,
                    "lookback": lookback,
                    "sma200_overlay": False,
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
                        "pass": bool(wf_positive >= 6),
                    },
                    "oos": oos,
                    "fwd": fwd,
                    "spy_benchmark": spy_bm,
                    "weight_stats": weight_stats,
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
                }
            )

        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append(
                {
                    "name": name,
                    "target_vol": target_vol,
                    "lookback": lookback,
                    "sma200_overlay": False,
                    "error": str(e),
                }
            )

    # 4. Determine best base config for SMA200 overlay
    valid_base = [r for r in results if "metrics_is" in r]
    best_base = max(
        valid_base, key=lambda r: r["metrics_is"].get("sharpe", -999), default=None
    )
    best_base_name = best_base["name"] if best_base else None

    # 5. Run SMA200 overlay on best base config
    if best_base_name:
        best_tv = best_base["target_vol"]
        best_lb = best_base["lookback"]

        print(
            f"\n  → {SMA200_OVERLAY_NAME} (base={best_base_name},"
            f" tv={best_tv*100:.0f}%, lb={best_lb}d, SMA200_overlay)",
            end=" ",
        )
        try:
            port_sma, w_sma = run_portfolio(
                prices, best_tv, best_lb, sma200_overlay=True
            )
            all_returns[SMA200_OVERLAY_NAME] = port_sma

            cagr = compute_cagr(port_sma)
            cagr_net = cagr * (1 - TAX_RATE)
            sharpe = compute_sharpe(port_sma)
            sharpe_net = sharpe * (1 - TAX_RATE)
            max_dd = compute_max_dd(port_sma)
            calmar = compute_calmar(cagr, max_dd)

            wf_sharpes, wf_positive = compute_wf(port_sma, n_splits=8)
            oos = compute_oos_holdout(port_sma)
            fwd = compute_fwd_stress(port_sma)
            spy_bm = compute_spy_benchmark(prices, port_sma)

            weight_stats = {
                "mean": float(w_sma.mean()),
                "min": float(w_sma.min()),
                "max": float(w_sma.max()),
                "std": float(w_sma.std()),
            }

            bt_equity = run_portfolio_bt(prices, best_tv, best_lb, sma200_overlay=True)
            if bt_equity is not None:
                bt_rets = bt_equity.pct_change().dropna()
                bt_cagr = compute_cagr(bt_rets)
                bt_sharpe = compute_sharpe(bt_rets)
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = bool(cagr_delta <= 3.0)
            else:
                bt_cagr = float("nan")
                bt_sharpe = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            stage2 = run_stage2_validation(best_tv, best_lb, sma200_overlay=True)
            if stage2:
                stage2_delta = abs(cagr - stage2["cagr_stage2"]) * 100
                stage2_ok = bool(stage2_delta <= 3.0)
            else:
                stage2_delta = float("nan")
                stage2_ok = None

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%"
                f" Sharpe={sharpe:.3f} SN={sharpe_net:.3f}"
                f" MaxDD={max_dd*100:.1f}% Calmar={calmar:.3f} WF={wf_positive}/8"
                f" AvgW={weight_stats['mean']*100:.0f}%"
            )

            results.append(
                {
                    "name": SMA200_OVERLAY_NAME,
                    "target_vol": best_tv,
                    "lookback": best_lb,
                    "sma200_overlay": True,
                    "base_config": best_base_name,
                    "metrics_is": {
                        "cagr": cagr,
                        "cagr_net": cagr_net,
                        "sharpe": sharpe,
                        "sharpe_net": sharpe_net,
                        "max_dd": max_dd,
                        "calmar": calmar,
                        "n_bars": len(port_sma),
                    },
                    "wf": {
                        "sharpes": wf_sharpes,
                        "positive": wf_positive,
                        "pass": bool(wf_positive >= 6),
                    },
                    "oos": oos,
                    "fwd": fwd,
                    "spy_benchmark": spy_bm,
                    "weight_stats": weight_stats,
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
                }
            )

        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append(
                {
                    "name": SMA200_OVERLAY_NAME,
                    "target_vol": best_tv,
                    "lookback": best_lb,
                    "sma200_overlay": True,
                    "error": str(e),
                }
            )

    # 6. PBO [AFML p.208-211]
    pbo_result = compute_pbo_gate(all_returns)
    print(f"\n  PBO: {pbo_result['pbo']:.3f} ({'PASS' if pbo_result.get('pass') else 'FAIL'})")

    # 7. DSR + gates per config [AFML p.298-299]
    n_configs = len(results)
    for r in results:
        if "error" in r or r["name"] not in all_returns:
            r["dsr"] = {"dsr": float("nan"), "p_value": float("nan"), "pass": False}
            r["gates"] = {"ALL_PASS": False, "fail_reason": "error"}
            continue
        port = all_returns[r["name"]]
        r["dsr"] = compute_dsr_per_config(port, n_configs)
        r["gates"] = gate_summary(r, pbo_result, r["dsr"], spy_cagr_net_actual)
        print(
            f"  {r['name']}: {r['gates']['fail_reason']}"
            f" DSR_p={r['dsr']['p_value']:.3f}"
            f" SN={r['metrics_is']['sharpe_net']:.3f}"
        )

    # 8. Best config (overall, by Sharpe)
    valid = [r for r in results if "metrics_is" in r]
    best = max(valid, key=lambda r: r["metrics_is"].get("sharpe", -999), default=None)
    best_name = best["name"] if best else "N/A"
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    print(f"\n  Best config: {best_name}")
    print(f"  Any ALL_PASS: {any_pass}")
    if best:
        m = best["metrics_is"]
        print(
            f"  Best: CAGR_net={m['cagr_net']*100:.2f}% Sharpe={m['sharpe']:.3f}"
            f" SN={m['sharpe_net']:.3f} MaxDD={m['max_dd']*100:.1f}% Calmar={m['calmar']:.3f}"
        )

    # 9. Write JSON (atomic)
    json_path = os.path.join(REPORT_DIR, "TQQQ.json")
    json_data = {
        "ticker": "TQQQ",
        "frequency": "daily",
        "strategy": "volatility_targeting",
        "window": window_info,
        "stage": 1,
        "source": "reference_prices.parquet (seam-corrected)",
        "spy_benchmark": {
            "cagr": spy_cagr_actual,
            "cagr_net": spy_cagr_net_actual,
            "sharpe": spy_sharpe_actual,
            "max_dd": spy_max_dd_actual,
        },
        "pbo": pbo_result,
        "configs": results,
        "best_config": best_name,
        "any_pass_all_gates": any_pass,
        "best_sharpe": best["metrics_is"]["sharpe"] if best else float("nan"),
        "best_sharpe_net": best["metrics_is"]["sharpe_net"] if best else float("nan"),
        "best_cagr_net": best["metrics_is"]["cagr_net"] if best else float("nan"),
        "best_calmar": best["metrics_is"]["calmar"] if best else float("nan"),
        "citations": [
            "advances_fin_ml, ch.14",
            "volatility_trading",
            "leverage_for_the_long_run, p.13",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    # 10. Write Markdown (atomic)
    md_path = os.path.join(REPORT_DIR, "TQQQ.md")
    write_report_md(md_path, results, pbo_result, window_info, spy_cagr_net_actual)

    print("\n=== D5 complete ===")
    return json_data


if __name__ == "__main__":
    main()
