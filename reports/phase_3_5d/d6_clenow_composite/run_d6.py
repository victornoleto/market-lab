"""
D6 — Trend + Momentum Composite (Clenow) TQQQ+GLD (atomic lead, iter 11).

Hypothesis: D2 sma200_gld Sharpe_net=0.780 (gate=0.800, gap=-0.020).
A composite binary signal combining 3 z-scored components should filter
out false entries/exits → higher Sharpe while preserving low PBO.

Signal: score = w1·z(slope_MA200_SPY) + w2·z(mom_90d_SPY) + w3·z(inv_vol_20d_TQQQ)
Threshold: score > 0 → 100% TQQQ; score ≤ 0 → 100% GLD (binary, like D2 → PBO low)

slope_MA200: 20-day rate of change of SPY 200-day MA (momentum of the trend itself)
mom_90d:     SPY 90-day price return (medium-term momentum)
inv_vol:     1 / (TQQQ 20-day realized vol), z-scored (high when TQQQ is calm/trending)

3 weight triplets:
  1. equal_weight  (1/3, 1/3, 1/3) — balanced composite
  2. trend_heavy   (0.5, 0.3, 0.2) — slope_MA200 dominant  [stocks_on_the_move, ch.6]
  3. mom_heavy     (0.2, 0.6, 0.2) — momentum dominant     [stocks_on_the_move, p.81]

Z-score window: 252 bars (rolling, no lookahead).
Warmup: ~472 bars (slope_MA200 bottleneck = 200+20+252). Effective data: ~2011-12 onward.

Citations:
  [stocks_on_the_move, p.81, ch.6]  — Clenow composite trend+momentum score
  [leverage_for_the_long_run, p.13] — MA-based regime switching (binary switch)
  [advances_fin_ml, p.208-211]      — PBO/CSCV gate
  [advances_fin_ml, p.298-299]      — DSR gate

Window: 2010-02-11 → 2026-04-14 (post-TQQQ inception; apples-to-apples with D2)
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, "/var/www/pessoal/ai-trade")
sys.path.insert(0, "/var/www/pessoal/ai-trade/src")

from ai_trade.backtest.validation.pbo import pbo as compute_pbo_cscv
from ai_trade.backtest.validation.dsr import dsr as compute_dsr

# ─── Constants ────────────────────────────────────────────────────────────────
REPORT_DIR = "reports/phase_3_5d/d6_clenow_composite"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
WINDOW_START = "2010-02-11"
WINDOW_END = "2026-04-14"
TAX_RATE = 0.15
ITER_NUM = 11
ZSCORE_WINDOW = 252  # rolling normalization window (bars)
SLOPE_PERIOD = 20    # rate-of-change period for SMA200 slope
SMA_PERIOD = 200
MOM_PERIOD = 90
VOL_PERIOD = 20

# 3 weight triplets: (name, w_slope, w_mom, w_invvol)
# [stocks_on_the_move, p.81, ch.6]
CONFIGS = [
    ("equal_weight", 1 / 3, 1 / 3, 1 / 3),
    ("trend_heavy",  0.5,   0.3,   0.2),
    ("mom_heavy",    0.2,   0.6,   0.2),
]


# ─── Signal functions ──────────────────────────────────────────────────────────

def _rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    """Rolling z-score without lookahead. NaN during warmup."""
    m = series.rolling(window).mean()
    s = series.rolling(window).std(ddof=1)
    return (series - m) / s.replace(0, np.nan)


def compute_signals(prices: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Returns (z_slope, z_mom90, z_invvol) — all NaN-safe, no lookahead.

    z_slope:  z-score of 20d rate-of-change of SPY SMA200      [stocks_on_the_move, ch.6]
    z_mom90:  z-score of SPY 90d return                         [stocks_on_the_move, p.81]
    z_invvol: z-score of 1/TQQQ_20d_vol (higher = calmer)      [advances_fin_ml, ch.14]
    """
    spy = prices["SPY"]
    tqqq = prices["TQQQ"]

    # Component 1: slope of SMA200 (20d rate-of-change)
    sma200 = spy.rolling(SMA_PERIOD).mean()
    slope_raw = (sma200 - sma200.shift(SLOPE_PERIOD)) / sma200.shift(SLOPE_PERIOD)
    z_slope = _rolling_zscore(slope_raw, ZSCORE_WINDOW)

    # Component 2: 90-day momentum of SPY
    mom90_raw = spy.pct_change(MOM_PERIOD)
    z_mom = _rolling_zscore(mom90_raw, ZSCORE_WINDOW)

    # Component 3: inverse vol of TQQQ
    tqqq_ret = tqqq.pct_change()
    tqqq_vol = tqqq_ret.rolling(VOL_PERIOD).std() * np.sqrt(252)
    invvol_raw = 1.0 / tqqq_vol.replace(0, np.nan)
    z_invvol = _rolling_zscore(invvol_raw, ZSCORE_WINDOW)

    return z_slope, z_mom, z_invvol


def build_signal(
    z_slope: pd.Series,
    z_mom: pd.Series,
    z_invvol: pd.Series,
    w1: float,
    w2: float,
    w3: float,
) -> pd.Series:
    """
    Binary composite signal. score > 0 → 1.0 (TQQQ), else 0.0 (GLD).
    NaN composite → 0.0 (GLD default during warmup).  [leverage_for_the_long_run, p.13]
    """
    composite = w1 * z_slope + w2 * z_mom + w3 * z_invvol
    # NaN (warmup) → GLD (False → 0.0)
    signal = (composite > 0).astype(float)
    return signal


def run_portfolio(
    prices: pd.DataFrame, w1: float, w2: float, w3: float
) -> tuple[pd.Series, pd.Series]:
    """Portfolio returns + weight series. Signal shifted 1 bar (no lookahead)."""
    z_slope, z_mom, z_invvol = compute_signals(prices)
    signal = build_signal(z_slope, z_mom, z_invvol, w1, w2, w3)
    w = signal.shift(1).fillna(0.0)  # execute next bar

    ret_tqqq = prices["TQQQ"].pct_change()
    ret_gld = prices["GLD"].pct_change()
    port = w * ret_tqqq + (1.0 - w) * ret_gld
    port = port.dropna()
    w_aligned = w.reindex(port.index).fillna(0.0)
    return port, w_aligned


def run_portfolio_bt(
    prices: pd.DataFrame, w1: float, w2: float, w3: float
) -> pd.Series | None:
    """Cross-lib concordance check via bt library."""
    try:
        import bt  # type: ignore
    except ImportError:
        return None

    try:
        z_slope, z_mom, z_invvol = compute_signals(prices)
        signal = build_signal(z_slope, z_mom, z_invvol, w1, w2, w3)
        weights = pd.DataFrame(0.0, index=prices.index, columns=["TQQQ", "GLD"])
        weights["TQQQ"] = signal.shift(1).fillna(0.0)
        weights["GLD"] = 1.0 - weights["TQQQ"]

        exec_prices = prices[["TQQQ", "GLD"]].copy()
        strat = bt.Strategy(
            "d6_composite",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["d6_composite"].rename("equity")
        return equity
    except Exception as exc:
        print(f"  [bt cross-lib] error: {exc}", file=sys.stderr)
        return None


def run_stage2_validation(w1: float, w2: float, w3: float) -> dict | None:
    """Stage 2: yfinance independent fetch, same signal logic."""
    try:
        import yfinance as yf  # type: ignore

        raw = yf.download(
            ["TQQQ", "GLD", "SPY"],
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
        port, _ = run_portfolio(close, w1, w2, w3)
        return {"cagr_stage2": float(compute_cagr(port))}
    except Exception as exc:
        print(f"  [Stage 2] error: {exc}", file=sys.stderr)
        return None


# ─── Metrics ──────────────────────────────────────────────────────────────────

def compute_cagr(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return float("nan") if years < 0.5 else float(equity.iloc[-1] ** (1 / years) - 1)


def compute_sharpe(returns: pd.Series) -> float:
    if returns.std() < 1e-12 or len(returns) < 30:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(252))


def compute_max_dd(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    running_max = equity.expanding().max()
    return float(((equity - running_max) / running_max).min())


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
        compute_sharpe(returns.iloc[i * split_size: (i + 1) * split_size])
        for i in range(n_splits)
    ]
    positive = sum(1 for s in sharpes if np.isfinite(s) and s > 0)
    return sharpes, positive


def compute_oos_holdout(returns: pd.Series) -> dict:
    """Single-block OOS: last 20% reserved."""
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
        "is_end": str(returns.index[split - 1].date()),
        "oos_start": str(returns.index[split].date()),
    }


def compute_fwd_stress(returns: pd.Series) -> dict:
    """Forward-window stress: last 63 trading days."""
    fwd = returns.iloc[-63:]
    fwd_sharpe = compute_sharpe(fwd)
    return {
        "fwd_sharpe": float(fwd_sharpe),
        "fwd_pass": bool(np.isfinite(fwd_sharpe) and fwd_sharpe > 0),
    }


def compute_pbo_gate(all_returns: dict[str, pd.Series]) -> dict:
    """CSCV PBO across 3 configs. [advances_fin_ml, p.208-211]"""
    names = [k for k, v in all_returns.items() if len(v) > 0]
    if len(names) < 2:
        return {"pbo": float("nan"), "pass": None, "note": "< 2 configs"}
    combined = pd.concat([all_returns[n].rename(n) for n in names], axis=1).dropna()
    if combined.shape[1] < 2 or len(combined) < 100:
        return {"pbo": float("nan"), "pass": None, "note": "insufficient data"}
    result = compute_pbo_cscv(combined.values, n_blocks=10)
    pbo_val = float(result.pbo)
    return {"pbo": pbo_val, "n_combinations": result.n_combinations, "pass": bool(pbo_val < 0.5)}


def compute_dsr_gate(port: pd.Series, n_configs: int) -> dict:
    """DSR: deflated Sharpe for multiple testing. [advances_fin_ml, p.298-299]"""
    try:
        result = compute_dsr(port.values, n_trials=max(n_configs, 2))
        return {
            "dsr": float(result.dsr),
            "p_value": float(result.p_value),
            "pass": bool(result.p_value < 0.05),
        }
    except Exception as exc:
        return {"dsr": float("nan"), "p_value": float("nan"), "pass": False, "error": str(exc)}


def gate_summary(result: dict, pbo: dict, dsr: dict, spy_cagr_net: float) -> dict:
    m = result.get("metrics_is", {})
    wf = result.get("wf", {})
    oos = result.get("oos", {})
    fwd = result.get("fwd", {})

    cagr_net = m.get("cagr_net", 0.0)
    calmar = m.get("calmar", 0.0)
    sharpe_net = m.get("sharpe_net", 0.0)

    g1 = bool(pbo.get("pass", False))
    g2 = bool(dsr.get("pass", False))
    g3 = bool(wf.get("pass", False))
    g4 = bool(oos.get("oos_pass", False))
    g5 = bool(fwd.get("fwd_pass", False))
    overfit_pass = g1 and g2 and g3 and g4 and g5

    e1 = bool(np.isfinite(cagr_net) and cagr_net > spy_cagr_net)
    e2 = bool(np.isfinite(calmar) and calmar > 0.5)
    e3 = bool(np.isfinite(sharpe_net) and sharpe_net > 0.8)
    eco_pass = e1 and e2 and e3

    all_pass = overfit_pass and eco_pass

    fail_parts = [
        name
        for name, ok in [
            ("PBO", g1), ("DSR", g2), ("WF", g3), ("OOS", g4), ("FWD", g5),
            ("SPY_BEAT", e1), ("CALMAR", e2), ("SHARPE_NET", e3),
        ]
        if not ok
    ]
    return {
        "gate1_pbo": g1, "gate2_dsr": g2, "gate3_wf": g3,
        "gate4_oos": g4, "gate5_fwd": g5, "overfit_pass": overfit_pass,
        "eco1_beats_spy": e1, "eco2_calmar": e2, "eco3_sharpe_net": e3,
        "eco_pass": eco_pass, "ALL_PASS": all_pass,
        "fail_reason": "PASS" if all_pass else ", ".join(fail_parts),
    }


# ─── File writers ──────────────────────────────────────────────────────────────

def atomic_write_json(path: str, data: dict) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
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
        key=lambda r: r["metrics_is"].get("sharpe_net", -999),
        default=None,
    )
    best_name = best["name"] if best else "N/A"
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    lines = [
        f"# D6 Clenow Composite — TQQQ+GLD (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** Binary composite signal (z-scored slope_MA200 + mom_90d + inv_vol).",
        "  Score > 0 → 100% TQQQ; Score ≤ 0 → 100% GLD.",
        "  Binary switch (like D2) → PBO expected low (~0.115). Composite should improve Sharpe.",
        f"**Window:** {window['start']} → {window['end']} ({window['years']:.1f}yr, effective from ~2011-12)",
        f"**Portfolio:** TQQQ (signal-weight 0 or 1) + GLD (complement); daily rebalance",
        f"**Best config:** `{best_name}` — **{'✓ ALL PASS' if any_pass else 'NO PASS'}**",
        f"**PBO:** {pbo.get('pbo', float('nan')):.3f} ({'PASS' if pbo.get('pass') else 'FAIL'})",
        "",
        "**Citations:** [stocks_on_the_move, p.81, ch.6], [leverage_for_the_long_run, p.13],",
        "  [advances_fin_ml, p.208-211, p.298-299]",
        "",
        "## Signal components (all z-scored, 252-bar rolling window)",
        "",
        "| Component | Formula | Warmup bars | Bullish when |",
        "|-----------|---------|-------------|--------------|",
        "| slope_MA200 | (SMA200_t − SMA200_{t−20}) / SMA200_{t−20}, z-scored | 472 | MA accelerating up |",
        "| mom_90d | SPY.pct_change(90), z-scored | 342 | 90d return positive |",
        "| inv_vol | 1/TQQQ_vol_20d, z-scored | 272 | TQQQ is calm/trending |",
        "",
        "## Weight triplets",
        "",
        "| # | Config | w_slope | w_mom | w_invvol |",
        "|---|--------|---------|-------|----------|",
        "| 1 | equal_weight | 1/3 | 1/3 | 1/3 |",
        "| 2 | trend_heavy | 0.5 | 0.3 | 0.2 |",
        "| 3 | mom_heavy | 0.2 | 0.6 | 0.2 |",
        "",
        "## Results vs D2 baseline",
        "",
        "D2 sma200_gld (iter 4): Sharpe=0.918 Sharpe_net=0.780 MaxDD=-60.3% Calmar=0.608 WF=7/8",
        "D6 target: Sharpe_net > 0.800 (need gross > 0.941, gap +0.023 from D2)",
        "",
        "| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar |"
        " WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |",
        "|--------|-------|-----------|--------|------------|--------|--------"
        "|----|-------|-------|-----|-------|----------|---------|--------|------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | ERROR |" + " — |" * 14)
            continue
        m = r.get("metrics_is", {})
        wf_r = r.get("wf", {})
        oos_r = r.get("oos", {})
        fwd_r = r.get("fwd", {})
        gates_r = r.get("gates", {})
        dsr_r = r.get("dsr", {})
        lines.append(
            f"| {r['name']} |"
            f" {m.get('cagr', float('nan'))*100:.2f} | {m.get('cagr_net', float('nan'))*100:.2f} |"
            f" {m.get('sharpe', float('nan')):.3f} | {m.get('sharpe_net', float('nan')):.3f} |"
            f" {m.get('max_dd', float('nan'))*100:.1f} | {m.get('calmar', float('nan')):.3f} |"
            f" {wf_r.get('positive', 0)}/8 |"
            f" {oos_r.get('oos_sharpe', float('nan')):.2f} |"
            f" {fwd_r.get('fwd_sharpe', float('nan')):.2f} |"
            f" {pbo.get('pbo', float('nan')):.3f} |"
            f" {dsr_r.get('p_value', float('nan')):.3f} |"
            f" {'✓' if gates_r.get('eco1_beats_spy') else '✗'} |"
            f" {'✓' if gates_r.get('eco2_calmar') else '✗'} |"
            f" {'✓' if gates_r.get('eco3_sharpe_net') else '✗'} |"
            f" {'✓' if gates_r.get('ALL_PASS') else '✗'} |"
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
        "## TQQQ time-in-market (% of days in TQQQ)",
        "",
        "| Config | Avg TQQQ weight% |",
        "|--------|-----------------|",
    ]
    for r in results:
        if "error" in r or "weight_stats" not in r:
            continue
        ws = r["weight_stats"]
        lines.append(f"| {r['name']} | {ws['mean']*100:.1f}% |")

    lines += [
        "",
        "## Analysis",
        "",
        "D6 hypothesis: adding momentum + inverse-vol z-scores to the pure SMA200 signal",
        "produces a smarter binary switch. In regimes where SPY is just barely above SMA200",
        "but momentum is negative or vol is high, the composite score goes negative → stays",
        "in GLD → avoids whipsaw losses. The net effect should be +0.020 Sharpe_net.",
        "",
        "Key difference from D2: D2 uses a single binary signal (SPY > SMA200).",
        "D6 uses a composite of 3 signals, each z-scored for comparability.",
        "Both are binary switches → should produce similar low PBO.",
    ]

    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


# ─── Main ──────────────────────────────────────────────────────────────────────

def load_wide_prices(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


def main() -> dict:
    print(f"\n=== D6 Clenow Composite TQQQ+GLD — iter {ITER_NUM} ===")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")
    print(f"  Configs: {len(CONFIGS)} weight triplets (all binary switch)")
    print(f"  Z-score window: {ZSCORE_WINDOW} bars | Warmup: ~472 bars (~1.9yr)")
    print(f"  Target: Sharpe_net > 0.800 (D2 baseline = 0.780, gap +0.020)")

    prices = load_wide_prices(PARQUET_PATH, WINDOW_START, WINDOW_END)
    print(f"  Prices: {len(prices)} bars, tickers={list(prices.columns)}")

    for t in ["TQQQ", "GLD", "SPY"]:
        if t not in prices.columns:
            raise RuntimeError(f"Missing ticker {t} in reference_prices.parquet")

    window_info = {
        "start": WINDOW_START,
        "end": WINDOW_END,
        "n_bars": len(prices),
        "years": (prices.index[-1] - prices.index[0]).days / 365.25,
    }

    spy_ret = prices["SPY"].pct_change().dropna()
    spy_cagr = compute_cagr(spy_ret)
    spy_cagr_net = spy_cagr * (1 - TAX_RATE)
    spy_sharpe = compute_sharpe(spy_ret)
    spy_max_dd = compute_max_dd(spy_ret)
    print(
        f"  SPY B&H: CAGR={spy_cagr*100:.2f}% net={spy_cagr_net*100:.2f}%"
        f" Sharpe={spy_sharpe:.3f} MaxDD={spy_max_dd*100:.1f}%"
    )

    # Precompute signals once for diagnostic
    z_slope, z_mom, z_invvol = compute_signals(prices)
    n_valid_slope = z_slope.notna().sum()
    n_valid_mom = z_mom.notna().sum()
    n_valid_invvol = z_invvol.notna().sum()
    print(
        f"  Signal valid bars: slope={n_valid_slope} mom={n_valid_mom} invvol={n_valid_invvol}"
        f" (total={len(prices)})"
    )

    all_returns: dict[str, pd.Series] = {}
    results: list[dict] = []

    for name, w1, w2, w3 in CONFIGS:
        print(f"\n  → {name} (w_slope={w1:.2f}, w_mom={w2:.2f}, w_invvol={w3:.2f})", end=" ")
        try:
            port, w_series = run_portfolio(prices, w1, w2, w3)
            all_returns[name] = port

            cagr = compute_cagr(port)
            cagr_net = cagr * (1 - TAX_RATE)
            sharpe = compute_sharpe(port)
            sharpe_net = sharpe * (1 - TAX_RATE)
            max_dd = compute_max_dd(port)
            calmar = compute_calmar(cagr, max_dd)

            wf_sharpes, wf_positive = compute_wf(port, n_splits=8)
            oos_r = compute_oos_holdout(port)
            fwd_r = compute_fwd_stress(port)

            weight_stats = {
                "mean": float(w_series.mean()),
                "min": float(w_series.min()),
                "max": float(w_series.max()),
            }

            # Cross-lib concordance via bt
            bt_equity = run_portfolio_bt(prices, w1, w2, w3)
            if bt_equity is not None:
                bt_ret = bt_equity.pct_change().dropna()
                bt_cagr = compute_cagr(bt_ret)
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = bool(cagr_delta <= 3.0)
            else:
                bt_cagr = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            # Stage 2: yfinance
            s2 = run_stage2_validation(w1, w2, w3)
            if s2:
                s2_delta = abs(cagr - s2["cagr_stage2"]) * 100
                s2_ok = bool(s2_delta <= 3.0)
            else:
                s2_delta = float("nan")
                s2_ok = None

            print(
                f"CAGR={cagr*100:.1f}% net={cagr_net*100:.1f}%"
                f" Sharpe={sharpe:.3f} SN={sharpe_net:.3f}"
                f" MaxDD={max_dd*100:.1f}% Calmar={calmar:.3f} WF={wf_positive}/8"
                f" AvgW={weight_stats['mean']*100:.0f}%"
            )

            results.append({
                "name": name,
                "weights": {"w_slope": w1, "w_mom": w2, "w_invvol": w3},
                "metrics_is": {
                    "cagr": cagr, "cagr_net": cagr_net,
                    "sharpe": sharpe, "sharpe_net": sharpe_net,
                    "max_dd": max_dd, "calmar": calmar,
                    "n_bars": len(port),
                },
                "wf": {"sharpes": wf_sharpes, "positive": wf_positive, "pass": bool(wf_positive >= 6)},
                "oos": oos_r,
                "fwd": fwd_r,
                "weight_stats": weight_stats,
                "cross_lib_bt": {
                    "bt_cagr": bt_cagr,
                    "cagr_delta_pp": cagr_delta,
                    "concordant": cross_lib_ok,
                },
                "stage2": {
                    "cagr_stage2": s2["cagr_stage2"] if s2 else float("nan"),
                    "cagr_delta_pp": s2_delta,
                    "concordant": s2_ok,
                },
            })

        except Exception as exc:
            print(f"  ERROR: {exc}")
            traceback.print_exc()
            results.append({"name": name, "error": str(exc)})

    # ── Gates ──────────────────────────────────────────────────────────────────
    pbo_result = compute_pbo_gate(all_returns)
    print(
        f"\n  PBO (3 configs): {pbo_result.get('pbo', float('nan')):.3f}"
        f" ({'PASS' if pbo_result.get('pass') else 'FAIL'})"
    )
    print("  Expected: PBO < 0.5 (binary switch → IS-best stable across CSCV blocks)")

    n_configs = len(results)
    for r in results:
        if "error" in r or r["name"] not in all_returns:
            r["dsr"] = {"p_value": float("nan"), "pass": False}
            r["gates"] = {"ALL_PASS": False, "fail_reason": "error"}
            continue
        port = all_returns[r["name"]]
        r["dsr"] = compute_dsr_gate(port, n_configs)
        r["gates"] = gate_summary(r, pbo_result, r["dsr"], spy_cagr_net)
        print(
            f"  {r['name']}: {r['gates']['fail_reason']}"
            f" (DSR_p={r['dsr']['p_value']:.3f}"
            f" SN={r['metrics_is']['sharpe_net']:.3f})"
        )

    valid = [r for r in results if "metrics_is" in r]
    best = max(valid, key=lambda r: r["metrics_is"].get("sharpe_net", -999), default=None)
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)

    print(f"\n  Best config: {best['name'] if best else 'N/A'}")
    print(f"  Any ALL_PASS: {any_pass}")
    if best:
        m = best["metrics_is"]
        print(
            f"  Best: Sharpe={m['sharpe']:.3f} SN={m['sharpe_net']:.3f}"
            f" CAGR_net={m['cagr_net']*100:.2f}% MaxDD={m['max_dd']*100:.1f}%"
            f" Calmar={m['calmar']:.3f}"
        )

    os.makedirs(REPORT_DIR, exist_ok=True)

    json_data = {
        "ticker": "TQQQ",
        "frequency": "daily",
        "strategy": "clenow_composite_binary",
        "lead": "D6",
        "iter": ITER_NUM,
        "window": window_info,
        "stage": 1,
        "source": "reference_prices.parquet",
        "n_configs": len(CONFIGS),
        "signal_params": {
            "sma_period": SMA_PERIOD, "slope_period": SLOPE_PERIOD,
            "mom_period": MOM_PERIOD, "vol_period": VOL_PERIOD,
            "zscore_window": ZSCORE_WINDOW,
        },
        "spy_benchmark": {
            "cagr": spy_cagr, "cagr_net": spy_cagr_net,
            "sharpe": spy_sharpe, "max_dd": spy_max_dd,
        },
        "pbo": pbo_result,
        "configs": results,
        "best_config": best["name"] if best else "N/A",
        "best_sharpe": best["metrics_is"]["sharpe"] if best else float("nan"),
        "best_sharpe_net": best["metrics_is"]["sharpe_net"] if best else float("nan"),
        "best_cagr_net": best["metrics_is"]["cagr_net"] if best else float("nan"),
        "best_calmar": best["metrics_is"]["calmar"] if best else float("nan"),
        "any_pass_all_gates": any_pass,
        "citations": [
            "stocks_on_the_move, p.81, ch.6",
            "leverage_for_the_long_run, p.13",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    json_path = os.path.join(REPORT_DIR, "TQQQ.json")
    atomic_write_json(json_path, json_data)

    md_path = os.path.join(REPORT_DIR, "TQQQ.md")
    write_report_md(md_path, results, pbo_result, window_info, spy_cagr_net)

    print("\n=== D6 complete ===")
    return json_data


if __name__ == "__main__":
    main()
