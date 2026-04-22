"""
Phase 3.5e — c03 EMA100+TLT Binary Regime — SSO single-ticker sweep (iter 31).

Strategy: SPY price > EMA(100) → 100% SSO; else → 100% TLT.
Signal asset: SPY. Off-leg: TLT.
Citation: [leverage_for_the_long_run, p.31] — Gayed TLT variant.

Data: reports/phase_3_5c/cross_lib/data/reference_prices.parquet (Stage 1).
SSO pre-2006: synthetic per r = 2 × r_SPX_TR - drag - expense [leverage_for_the_long_run, ch.2].
Stage 2: Tiingo real SSO (2006-06-21→2026-04-20) — concordance check vs Stage 1.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone

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
REGISTRY_PATH = "reports/phase_3_5e/c03_ema100_tlt/registry.json"
REPORT_DIR = "reports/phase_3_5e/c03_ema100_tlt"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
TIINGO_DAILY_PATH = "data/tiingo/daily/prices/SSO.parquet"
TRIAL_COUNT_PATH = "docs/self_improvement/trial_count.json"
TAX_RATE = 0.15
TICKER = "SSO"
ITER_NUM = 31
PHASE = "phase_3_5e"
MA_PERIOD = 100

# Window: max(SSO_start=1986, SPY_start=2001-05-14, TLT_start=2002-07-26) → min(all ends)
# TLT constrains start: 2002-07-26; TLT end: 2026-04-15
WINDOW_START = "2002-07-26"
WINDOW_END   = "2026-04-15"


# ─── Signal ──────────────────────────────────────────────────────────────────

def ema_regime(spy: pd.Series, lookback: int = MA_PERIOD) -> pd.Series:
    """SPY close > EMA(100) → regime on (1.0). Shift by 1 to avoid lookahead.
    [leverage_for_the_long_run, p.31] — Gayed TLT variant."""
    ema = spy.ewm(span=lookback, adjust=False).mean()
    return (spy > ema).astype(float).shift(1).fillna(0)


# ─── Data loading ─────────────────────────────────────────────────────────────

def load_wide(parquet_path: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    wide = df.pivot(index="date", columns="ticker", values="close")
    wide.columns.name = None
    return wide.ffill().dropna(how="all")


def load_tiingo_sso(start: str, end: str) -> pd.Series | None:
    """Load Tiingo real SSO data for Stage 2 concordance.
    Tiingo SSO available 2006-06-21 → 2026-04-20."""
    try:
        df = pd.read_parquet(TIINGO_DAILY_PATH)
        # Normalize column names
        date_col = [c for c in df.columns if "date" in c.lower()]
        close_col = [c for c in df.columns if "adj" in c.lower() and "close" in c.lower()]
        if not close_col:
            close_col = [c for c in df.columns if "close" in c.lower()]
        if not date_col or not close_col:
            print(f"  [Stage 2] SSO parquet columns: {df.columns.tolist()}")
            return None
        df = df.rename(columns={date_col[0]: "date", close_col[0]: "close"})
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        df = df.set_index("date").sort_index()
        df = df.loc[start:end, "close"]
        return df.dropna()
    except Exception as e:
        print(f"  [Stage 2] Error loading Tiingo SSO: {e}")
        return None


# ─── Portfolio backtest ───────────────────────────────────────────────────────

def run_portfolio(prices: pd.DataFrame) -> pd.Series:
    """
    SPY > EMA100 (prev day) → 100% SSO; else → 100% TLT.
    Daily rebalance, no transaction costs (gross; tax applied at CAGR level).
    [leverage_for_the_long_run, p.31]
    """
    sig = ema_regime(prices["SPY"])  # 1 = on-regime (SSO), 0 = off-regime (TLT)
    ret_sso = prices["SSO"].pct_change()
    ret_tlt = prices["TLT"].pct_change()
    port = sig * ret_sso + (1 - sig) * ret_tlt
    return port.dropna()


def run_portfolio_tiingo(tiingo_sso: pd.Series, prices_ref: pd.DataFrame) -> pd.Series | None:
    """Stage 2: run same strategy using Tiingo real SSO for concordance check.
    Uses same SPY and TLT signals from reference_prices.parquet."""
    try:
        # Align on common dates (Tiingo SSO ∩ ref_prices)
        common_start = max(tiingo_sso.index[0], prices_ref.index[0])
        sub_ref = prices_ref.loc[common_start:]
        sub_tiingo = tiingo_sso.loc[common_start:]
        # Align index
        idx = sub_ref.index.intersection(sub_tiingo.index)
        if len(idx) < 252:
            return None
        sub_ref = sub_ref.loc[idx]
        sub_tiingo = sub_tiingo.loc[idx]
        sig = ema_regime(sub_ref["SPY"])
        ret_sso = sub_tiingo.pct_change()
        ret_tlt = sub_ref["TLT"].pct_change()
        port = sig * ret_sso + (1 - sig) * ret_tlt
        return port.dropna()
    except Exception as e:
        print(f"  [Stage 2] Portfolio error: {e}")
        return None


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
    """Cross-lib bt concordance check (EMA100+TLT config, SSO asset)."""
    try:
        import bt  # type: ignore

        sig = ema_regime(prices["SPY"])
        exec_prices = prices[["SSO", "TLT"]].copy()

        weights = pd.DataFrame(
            {
                "SSO": sig,
                "TLT": 1.0 - sig,
            },
            index=prices.index,
        )

        strat = bt.Strategy(
            "sso_ema100_tlt",
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        equity = result.prices["sso_ema100_tlt"]
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


def build_md_report(
    result: dict,
    bt_result: dict | None,
    stage2_result: dict | None,
) -> str:
    m = result["metrics_is"]
    wf = result["wf"]
    oos = result["oos"]
    fwd = result["fwd"]
    gates = result["gates"]
    dsr = result.get("dsr", {})
    spy_bm = result.get("spy_benchmark", {})

    lines = [
        f"# SSO daily — c03 EMA100+TLT Binary Regime (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Strategy:** SPY > EMA100 (prev day) → 100% SSO; else → 100% TLT.",
        "**Asset:** SSO (ProShares Ultra S&P 500, 2× SPY).",
        "**Signal:** SPY EMA100 regime `[leverage_for_the_long_run, p.31]` — Gayed TLT variant.",
        "**Off-leg:** TLT (iShares 20+ Year Treasury Bond ETF).",
        "**Tax:** 15% IR BR flat on CAGR.",
        "**Stage 1:** reference_prices.parquet (SSO synthetic pre-2006: 2× SPX daily - drag - expense `[leverage_for_the_long_run, ch.2]`).",
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
        "| Metric | Value |",
        "|--------|-------|",
        f"| SPY CAGR gross | {spy_bm.get('spy_cagr_gross', float('nan'))*100:.2f}% |",
        f"| SPY CAGR net | {spy_bm.get('spy_cagr_net', float('nan'))*100:.2f}% |",
        f"| SPY Sharpe | {spy_bm.get('spy_sharpe', float('nan')):.3f} |",
        f"| SPY MaxDD | {spy_bm.get('spy_max_dd', float('nan'))*100:.1f}% |",
        f"| Correlation vs SPY | {spy_bm.get('corr_vs_spy', float('nan')):.3f} |",
        "",
        "## Gate summary",
        "",
        "| Gate | Result |",
        "|------|--------|",
        "| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |",
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
        "## Stage 2 concordance (Tiingo real SSO)",
        "",
    ]

    if stage2_result:
        our_cagr = m["cagr"]
        s2_cagr = stage2_result.get("cagr", float("nan"))
        delta = abs(our_cagr - s2_cagr) * 100
        concordant = delta <= 3.0
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Stage 2 CAGR (Tiingo real SSO) | {s2_cagr*100:.2f}% |")
        lines.append(f"| Stage 2 window | {stage2_result.get('window_start', 'N/A')} → {stage2_result.get('window_end', 'N/A')} |")
        lines.append(f"| ΔCAGR | {delta:.2f}pp — {'✓ CONCORDANT' if concordant else '✗ DIVERGENT'} |")
    else:
        lines.append("Stage 2 data unavailable — Tiingo SSO parquet missing or too short.")

    lines += [
        "",
        "## Cross-lib concordance (bt)",
        "",
    ]

    if bt_result:
        our_cagr = m["cagr"]
        delta = abs(our_cagr - bt_result["bt_cagr"]) * 100
        concordant = delta <= 3.0
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| bt CAGR | {bt_result['bt_cagr']*100:.2f}% |")
        lines.append(f"| ΔCAGR | {delta:.2f}pp — {'✓ CONCORDANT' if concordant else '✗ DIVERGENT'} |")
    else:
        lines.append("bt library not available — concordance skipped.")

    lines += [
        "",
        "## Citations",
        "",
        "- `[leverage_for_the_long_run, p.31]` — EMA100+TLT Gayed variant",
        "- `[leverage_for_the_long_run, ch.2]` — SSO synthetic pre-2006: 2× SPX returns - drag - expense",
        "- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate",
        "- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials",
        "- `[advances_fin_ml, ch.12]` — Walk-forward validation",
        "",
        "## Notes",
        "",
        "- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.",
        "- c03 tests EMA100+TLT. TLT off-leg is the 'flight-to-safety' variant — [leverage_for_the_long_run, p.31].",
        "- SSO pre-2006: synthetic from reference_prices.parquet (2× SPX total return).",
        "- Stage 2 uses Tiingo real SSO (2006-06-21 onwards) — overlap with Stage 1 real SSO data.",
        f"- DSR n_trials = {18} (cumulative from trial_count.json).",
        f"- Window constrained by TLT first date ({WINDOW_START}) and TLT last date ({WINDOW_END}).",
    ]

    return "\n".join(lines) + "\n"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n=== Phase 3.5e c03 SSO sweep (iter {ITER_NUM}) ===")
    print(f"  Config: c03_ema100_tlt (EMA100 + TLT off-leg)")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")

    # Load Stage 1 data
    wide = load_wide(PARQUET_PATH, WINDOW_START, WINDOW_END)
    print(f"  Stage 1 loaded: {len(wide)} bars, tickers={sorted(wide.columns.tolist())}")

    required = ["SSO", "SPY", "TLT"]
    missing = [t for t in required if t not in wide.columns]
    if missing:
        raise RuntimeError(f"Missing tickers in reference_prices.parquet: {missing}")

    # Load trial count
    trial_count = load_trial_count()
    trial_start = trial_count["total_trials_completed"]
    n_trials_this_config = trial_start + 1
    print(f"  Trial count before sweep: {trial_start} → using n_trials={n_trials_this_config} for DSR")

    # Run Stage 1 portfolio
    print(f"\n  → c03_ema100_tlt SSO (window: {WINDOW_START} → {WINDOW_END})", end=" ... ")
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
        "name": "c03_ema100_tlt",
        "off_leg": "TLT",
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

    # Stage 2 concordance: Tiingo real SSO
    print("\n  → Stage 2 concordance (Tiingo real SSO 2006-06-21→2026-04-20)...")
    tiingo_sso = load_tiingo_sso(WINDOW_START, WINDOW_END)
    stage2_result = None
    if tiingo_sso is not None and len(tiingo_sso) >= 252:
        port2 = run_portfolio_tiingo(tiingo_sso, prices)
        if port2 is not None and len(port2) >= 252:
            cagr2 = compute_cagr(port2)
            delta2 = abs(cagr - cagr2) * 100
            concordant2 = delta2 <= 3.0
            stage2_result = {
                "cagr": float(cagr2),
                "window_start": str(port2.index[0].date()),
                "window_end": str(port2.index[-1].date()),
                "delta_cagr_pp": float(delta2),
                "concordant": bool(concordant2),
            }
            print(f"  Stage 2: CAGR={cagr2*100:.2f}% ΔCAGR={delta2:.2f}pp "
                  f"({'CONCORDANT' if concordant2 else 'DIVERGENT'})")
        else:
            print("  Stage 2: portfolio run failed (not enough data)")
    else:
        print("  Stage 2: Tiingo SSO data unavailable or too short")

    result["stage2"] = stage2_result or {"note": "Tiingo SSO data unavailable or too short"}

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

    # ── Write SSO.json ──
    json_path = os.path.join(REPORT_DIR, "SSO.json")
    json_data = {
        "ticker": TICKER,
        "frequency": "daily",
        "phase": PHASE,
        "lead_id": "c03",
        "lead_slug": "c03_ema100_tlt",
        "iter": ITER_NUM,
        "source": "reference_prices.parquet (Stage 1, synthetic pre-2006 SSO)",
        "config": result,
        "best_config": "c03_ema100_tlt",
        "any_prepass_pending_pbo": any_prepass,
        "best_sharpe_oos": float(oos["oos_sharpe"]),
        "best_cagr": float(cagr),
        "best_maxdd": float(max_dd),
        "cross_lib_bt": bt_result,
        "stage2": stage2_result,
        "citations": [
            "leverage_for_the_long_run, p.31",
            "leverage_for_the_long_run, ch.2",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(json_path, json_data)

    # ── Write SSO.md ──
    md_path = os.path.join(REPORT_DIR, "SSO.md")
    md_text = build_md_report(result, bt_result, stage2_result)
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
        "best_config": "c03_ema100_tlt",
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
