"""
D3 — Donchian Channel Breakout on TQQQ+GLD (atomic lead, iter 7).

Strategy: Long TQQQ when close breaks above N-day Donchian upper channel;
switch to GLD when close breaks below M-day lower channel. Persistent position.

Citations:
  [trading_systems_methods, p.353]  — Donchian channel breakout mechanism
  [stocks_on_the_move, p.81]        — momentum entry timing (Clenow)
  [advances_fin_ml, p.208-211]      — PBO/CSCV gate
  [advances_fin_ml, p.298-299]      — DSR gate

Configs tested:
  dc20_10: entry=20, exit=10
  dc40_20: entry=40, exit=20
  dc60_30: entry=60, exit=30
  dc80_40: entry=80, exit=40

Window: 2004-11-18 → 2026-04-15 (longest TQQQ+GLD common window, ~21.4yr)
Off-leg: GLD only (TMF eliminated in D2, cash suboptimal vs GLD)
Signal ticker: TQQQ (price breakout on traded instrument directly)
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
REPORT_DIR = "reports/phase_3_5d/d3_donchian_tqqq_gld"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
WINDOW_START = "2004-11-18"   # Longest TQQQ+GLD common window
WINDOW_END = "2026-04-15"
TAX_RATE = 0.15               # 15% IR BR flat on CAGR [investment-mandate §1]
ITER_NUM = 7

# SPY B&H reference (from D1 baseline, recomputed for this window in run)
SPY_BH_CAGR_GROSS = 0.1222   # D1 reference; actual SPY for 2004-2026 computed in run
SPY_BH_CAGR_NET = SPY_BH_CAGR_GROSS * (1 - TAX_RATE)

CONFIGS = [
    ("dc20_10", 20, 10),
    ("dc40_20", 40, 20),
    ("dc60_30", 60, 30),
    ("dc80_40", 80, 40),
]


# ─── Signal ───────────────────────────────────────────────────────────────────

def donchian_signal(prices: pd.Series, entry_lookback: int, exit_lookback: int) -> pd.Series:
    """
    Persistent Donchian channel breakout signal on TQQQ close.

    Entry: close > max of previous entry_lookback closes → long (1.0)
    Exit: close < min of previous exit_lookback closes → flat (0.0)
    Position persists between signals. [trading_systems_methods, p.353]
    """
    shifted = prices.shift(1)
    upper = shifted.rolling(entry_lookback, min_periods=entry_lookback).max()
    lower = shifted.rolling(exit_lookback, min_periods=exit_lookback).min()

    buy = prices > upper
    sell = prices < lower

    raw = pd.Series(np.nan, index=prices.index)
    # Apply entry/exit; entry priority when both trigger simultaneously
    raw[sell] = 0.0
    raw[buy] = 1.0

    return raw.ffill().fillna(0.0)


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
    entry_lookback: int,
    exit_lookback: int,
) -> pd.Series:
    """
    TQQQ + GLD portfolio driven by Donchian breakout on TQQQ.
    Signal shifted 1 bar to avoid lookahead bias.
    """
    sig = donchian_signal(prices["TQQQ"], entry_lookback, exit_lookback).shift(1).fillna(0)

    ret_tqqq = prices["TQQQ"].pct_change()
    ret_gld = prices["GLD"].pct_change()

    port = sig * ret_tqqq + (1 - sig) * ret_gld
    return port.dropna()


def run_portfolio_bt(
    prices: pd.DataFrame,
    entry_lookback: int,
    exit_lookback: int,
) -> pd.Series | None:
    """Cross-lib concordance via bt library."""
    try:
        import bt  # type: ignore
    except ImportError:
        return None

    try:
        sig = donchian_signal(prices["TQQQ"], entry_lookback, exit_lookback).shift(1).fillna(0)
        exec_prices = prices[["TQQQ", "GLD"]].copy()

        weights = pd.DataFrame(0.0, index=prices.index, columns=["TQQQ", "GLD"])
        weights["TQQQ"] = sig
        weights["GLD"] = 1.0 - sig

        strat = bt.Strategy(
            "dc_tqqq_gld",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["dc_tqqq_gld"].rename("equity")
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
    sharpes = [compute_sharpe(returns.iloc[i * split_size:(i + 1) * split_size]) for i in range(n_splits)]
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

def run_stage2_validation(entry_lookback: int, exit_lookback: int) -> dict | None:
    """Fetch TQQQ/GLD from yfinance, run same config."""
    try:
        import yfinance as yf  # type: ignore

        raw = yf.download(
            ["TQQQ", "GLD"],
            start=WINDOW_START,
            end=WINDOW_END,
            progress=False,
            auto_adjust=True,
        )
        if raw.empty:
            return None
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
        close = close.dropna(how="all")
        port = run_portfolio(close, entry_lookback, exit_lookback)
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
        return {"dsr": float(result.dsr), "p_value": float(result.p_value), "pass": bool(result.p_value < 0.05)}
    except Exception as e:
        return {"dsr": float("nan"), "p_value": float("nan"), "pass": False, "error": str(e)}


# ─── Gate summary ──────────────────────────────────────────────────────────────

def gate_summary(result: dict, pbo: dict, dsr: dict, spy_cagr_net: float) -> dict:
    """Aggregate all 5 overfit gates + economic gates."""
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
        name for name, ok in [
            ("PBO", g1_pbo), ("DSR", g2_dsr), ("WF", g3_wf),
            ("OOS", g4_oos), ("FWD", g5_fwd),
            ("SPY_BEAT", e1_spy), ("CALMAR", e2_calmar), ("SHARPE_NET", e3_sharpe),
        ] if not ok
    ]

    return {
        "gate1_pbo": g1_pbo, "gate2_dsr": g2_dsr, "gate3_wf": g3_wf,
        "gate4_oos": g4_oos, "gate5_fwd": g5_fwd, "overfit_pass": overfit_pass,
        "eco1_beats_spy": e1_spy, "eco2_calmar": e2_calmar, "eco3_sharpe_net": e3_sharpe,
        "eco_pass": eco_pass, "ALL_PASS": all_pass,
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
        f"# D3 Donchian Breakout — TQQQ+GLD (iter {ITER_NUM}) [SWING BROKER]",
        "",
        f"**Strategy:** Long TQQQ on Donchian upper-channel breakout; GLD on lower-channel breakdown",
        f"**Window:** {window['start']} → {window['end']} ({window['years']:.1f}yr, reference_prices.parquet Stage 1)",
        f"**Portfolio:** TQQQ (on-regime) + GLD (off-regime); signal on TQQQ close",
        f"**Best config:** `{best_name}` — **{'✓ ALL PASS' if any_pass else 'NO PASS'}**",
        f"**PBO:** {pbo.get('pbo', float('nan')):.3f} ({'PASS' if pbo.get('pass') else 'FAIL'})",
        "",
        "Citations: [trading_systems_methods, p.353], [stocks_on_the_move, p.81],",
        "  [advances_fin_ml, p.208-211, p.298-299]",
        "",
        "## Results",
        "",
        "| Config | Entry | Exit | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar |"
        " WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |",
        "|--------|-------|------|-------|-----------|--------|------------|--------|--------|"
        "----|-------|-------|-----|-------|----------|---------|--------|------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | — | — | ERROR | — | — | — | — | — | — | — | — | — | — | — | — | — | ✗ |")
            continue
        m = r.get("metrics_is", {})
        wf = r.get("wf", {})
        oos = r.get("oos", {})
        fwd = r.get("fwd", {})
        gates = r.get("gates", {})
        dsr_r = r.get("dsr", {})

        lines.append(
            f"| {r['name']} | {r['entry_lookback']} | {r['exit_lookback']} |"
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

    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== D3 Donchian Breakout TQQQ+GLD — iter {ITER_NUM} ===")
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
    print(f"  SPY B&H: CAGR={spy_cagr_actual*100:.2f}% net={spy_cagr_net_actual*100:.2f}%"
          f" Sharpe={spy_sharpe_actual:.3f} MaxDD={spy_max_dd_actual*100:.1f}%")

    # 3. Run all 4 configs
    all_returns: dict[str, pd.Series] = {}
    results: list[dict] = []

    print(f"\n  Running {len(CONFIGS)} configs ...")
    for name, entry_lb, exit_lb in CONFIGS:
        print(f"  → {name} (entry={entry_lb}, exit={exit_lb})", end=" ")
        try:
            port = run_portfolio(prices, entry_lb, exit_lb)
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

            # Compute time-in-market
            sig_full = donchian_signal(prices["TQQQ"], entry_lb, exit_lb).shift(1).fillna(0)
            sig_full = sig_full.reindex(port.index)
            time_in_market = float(sig_full.mean())
            n_trades = int((sig_full.diff().abs() > 0).sum())

            # Cross-lib: bt
            bt_equity = run_portfolio_bt(prices, entry_lb, exit_lb)
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
            stage2 = run_stage2_validation(entry_lb, exit_lb)
            if stage2:
                stage2_delta = abs(cagr - stage2["cagr_stage2"]) * 100
                stage2_ok = bool(stage2_delta <= 3.0)
            else:
                stage2_delta = float("nan")
                stage2_ok = None

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}% "
                f"Sharpe={sharpe:.3f} SN={sharpe_net:.3f} "
                f"MaxDD={max_dd*100:.1f}% Calmar={calmar:.3f} WF={wf_positive}/8"
                f" TIM={time_in_market*100:.0f}%"
            )

            results.append({
                "name": name,
                "entry_lookback": entry_lb,
                "exit_lookback": exit_lb,
                "metrics_is": {
                    "cagr": cagr, "cagr_net": cagr_net,
                    "sharpe": sharpe, "sharpe_net": sharpe_net,
                    "max_dd": max_dd, "calmar": calmar,
                    "n_bars": len(port),
                    "time_in_market": time_in_market,
                    "n_trades": n_trades,
                },
                "wf": {"sharpes": wf_sharpes, "positive": wf_positive, "pass": bool(wf_positive >= 6)},
                "oos": oos,
                "fwd": fwd,
                "spy_benchmark": spy_bm,
                "cross_lib_bt": {
                    "bt_cagr": bt_cagr, "bt_sharpe": bt_sharpe,
                    "cagr_delta_pp": cagr_delta, "concordant": cross_lib_ok,
                },
                "stage2": {
                    "cagr_stage2": stage2["cagr_stage2"] if stage2 else float("nan"),
                    "cagr_delta_pp": stage2_delta, "concordant": stage2_ok,
                },
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append({
                "name": name, "entry_lookback": entry_lb, "exit_lookback": exit_lb,
                "error": str(e),
            })

    # 4. PBO [AFML p.208-211]
    pbo_result = compute_pbo_gate(all_returns)
    print(f"\n  PBO: {pbo_result['pbo']:.3f} ({'PASS' if pbo_result.get('pass') else 'FAIL'})")

    # 5. DSR + gates per config [AFML p.298-299]
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

    # 6. Best config
    valid = [r for r in results if "metrics_is" in r]
    best = max(valid, key=lambda r: r["metrics_is"].get("sharpe", -999), default=None)
    best_name = best["name"] if best else "N/A"
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    print(f"\n  Best config: {best_name}")
    print(f"  Any ALL_PASS: {any_pass}")
    if best:
        m = best["metrics_is"]
        print(f"  Best: CAGR_net={m['cagr_net']*100:.2f}% Sharpe={m['sharpe']:.3f}"
              f" SN={m['sharpe_net']:.3f} MaxDD={m['max_dd']*100:.1f}% Calmar={m['calmar']:.3f}")

    # 7. Write JSON (atomic)
    json_path = os.path.join(REPORT_DIR, "TQQQ.json")
    json_data = {
        "ticker": "TQQQ",
        "frequency": "daily",
        "strategy": "donchian_breakout",
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
            "trading_systems_methods, p.353",
            "stocks_on_the_move, p.81",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    # 8. Write Markdown (atomic)
    md_path = os.path.join(REPORT_DIR, "TQQQ.md")
    write_report_md(md_path, results, pbo_result, window_info, spy_cagr_net_actual)

    print("\n=== D3 complete ===")
    return json_data


if __name__ == "__main__":
    main()
