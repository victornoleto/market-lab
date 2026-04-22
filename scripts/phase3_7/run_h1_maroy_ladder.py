"""Phase 3.7 H1.c runner — Maróy 2024 Ladder exit on Zarattini noise boundary.

Runs IS (2017-06-01 → 2021-12-31), OOS (2022-01-01 → 2024-12-31),
FWD (2025-01-01 → 2026-04-14) on SPY 1-min data; assembles 13-gate verdict
table; emits AGGREGATE.md with PASS/FAIL per mandate §2.4.

Citations
---------
* Signal: ``[paper.zarattini_2024_intraday_spy, §3]``
* Exit:   ``[paper.maroy_2024_intraday_improvements, §Ladder]``
* PBO/DSR: ``[advances_fin_ml, p.208-211, p.275]``
* Gates:  ``[docs/investment-mandate.md §2.4]``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ai_trade.backtest.strategies.phase3_7_h1_maroy_ladder import (  # noqa: E402
    MaroyLadderConfig,
    MaroyLadderResult,
    simulate_h1_maroy_ladder,
)
from ai_trade.backtest.validation import (  # noqa: E402
    dsr,
    pbo,
    walk_forward_gate,
)
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)

LOG_FMT = "%(asctime)s %(levelname)-5s %(name)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("h1_maroy_ladder")

SPY_PATH = REPO_ROOT / "data" / "phase3_7" / "intraday" / "SPY_1min.parquet"
QQQ_PATH = REPO_ROOT / "data" / "phase3_7" / "intraday" / "QQQ_1min.parquet"
REPORT_DIR = REPO_ROOT / "reports" / "phase_3_7" / "h1_maroy_ladder"

IS_START, IS_END = "2017-06-01", "2021-12-31"
OOS_START, OOS_END = "2022-01-01", "2024-12-31"
FWD_START, FWD_END = "2025-01-01", "2026-04-14"

TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# Metrics helpers on DAILY returns (Sharpe, CAGR, MDD are computed on the
# daily-compounded return series for honest comparability with other Phase
# 3.6/3.7 leads).
# ---------------------------------------------------------------------------

def _daily_from_bar(bar_returns: pd.Series) -> pd.Series:
    r = bar_returns.dropna()
    if r.empty:
        return pd.Series(dtype=float)
    day = pd.Index(pd.to_datetime(r.index).date, name="date")
    daily = (1.0 + r).groupby(day).prod() - 1.0
    daily.index = pd.to_datetime(daily.index)
    return daily


def _sharpe(daily: pd.Series) -> float:
    if daily.empty or daily.std(ddof=1) == 0:
        return 0.0
    return float(daily.mean() / daily.std(ddof=1) * np.sqrt(TRADING_DAYS))


def _cagr(daily: pd.Series) -> float:
    if daily.empty:
        return 0.0
    n = len(daily)
    eq = float((1.0 + daily).prod())
    if eq <= 0:
        return -1.0
    return eq ** (TRADING_DAYS / n) - 1.0


def _mdd(daily: pd.Series) -> float:
    if daily.empty:
        return 0.0
    eq = (1.0 + daily).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def _ir_vs_spy(daily: pd.Series, spy_daily: pd.Series) -> float:
    if daily.empty:
        return 0.0
    # Normalise both to tz-naive date index for alignment.
    d1 = daily.copy()
    d1.index = pd.to_datetime(d1.index).tz_localize(None) if d1.index.tz is not None else pd.to_datetime(d1.index)
    d2 = spy_daily.copy()
    d2.index = pd.to_datetime(d2.index).tz_localize(None) if d2.index.tz is not None else pd.to_datetime(d2.index)
    aligned = pd.concat([d1, d2], axis=1).dropna()
    if aligned.empty:
        return 0.0
    excess = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    if excess.std(ddof=1) == 0:
        return 0.0
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(TRADING_DAYS))


# ---------------------------------------------------------------------------
# Tier classification per mandate §2.2 / §2.3 (route A — Pepperstone CFD, no DARF)
# ---------------------------------------------------------------------------

def cagr_tier_A(cagr: float) -> str:
    if cagr < 0.13:
        return "Folclore"
    if cagr < 0.25:
        return "Marginal"
    if cagr < 0.50:
        return "Válido"
    if cagr < 1.00:
        return "Forte"
    return "Extraordinário (suspect)"


def mdd_tier_A(mdd: float) -> str:
    a = abs(mdd)
    if a <= 0.25:
        return "Excelente"
    if a <= 0.40:
        return "Válido"
    if a <= 0.75:
        return "Warning"
    return "Reject"


# ---------------------------------------------------------------------------
# Single-asset IS/OOS/FWD wrapper + 13-gate evaluation
# ---------------------------------------------------------------------------

def _slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    start_ts = pd.Timestamp(start, tz="UTC")
    end_ts = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    return df.loc[(df.index >= start_ts) & (df.index < end_ts)]


def run_window(
    df: pd.DataFrame, config: MaroyLadderConfig, label: str
) -> dict[str, Any]:
    res = simulate_h1_maroy_ladder(df, config)
    daily = _daily_from_bar(res.bar_returns)
    out = {
        "label": label,
        "n_bars": len(df),
        "n_entries": int(res.n_entries),
        "tp1_hits": int(res.tp1_hits),
        "tp2_hits": int(res.tp2_hits),
        "tp3_hits": int(res.tp3_hits),
        "trailing_exits": int(res.trailing_exits),
        "eod_exits": int(res.eod_exits),
        "median_hold_min": float(res.median_hold_minutes())
        if res.hold_lengths_bars else float("nan"),
        "cum_spread_pct": float(res.cum_spread_pct),
        "sharpe_daily": _sharpe(daily),
        "cagr": _cagr(daily),
        "mdd": _mdd(daily),
        "n_days": int(len(daily)),
    }
    return out, res, daily


def _short_hash(cfg: MaroyLadderConfig) -> str:
    payload = json.dumps(asdict(cfg), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:10]


def _git_sha() -> str:
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        return out[:10]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Cross-lib SIMPLIFIED check (single-TP 1×ATR) — pandas ref vs vectorbt
# We implement a single-TP 1×ATR + EOD flat version in both libs and compare
# CAGR. The Ladder itself cannot be honestly replicated in vbt (documented
# limitation); cross-lib gate is evaluated on the simplified control.
# ---------------------------------------------------------------------------

def _simplified_single_tp_pandas(
    df: pd.DataFrame, config: MaroyLadderConfig
) -> pd.Series:
    """Single-TP at 1×ATR entry, EOD-flat, same noise-boundary entry."""
    from ai_trade.backtest.strategies.phase3_7_h1_maroy_ladder import (
        _compute_noise_boundary,
        compute_atr_wilder_intraday,
    )
    df = df.sort_index()
    _, upper, lower = _compute_noise_boundary(df, config.noise_lookback_days)
    atr = compute_atr_wilder_intraday(
        df["high"], df["low"], df["close"], period=config.atr_period
    ).to_numpy()
    close = df["close"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    u = upper.to_numpy()
    lo = lower.to_numpy()
    idx = df.index
    day_id = pd.to_datetime(idx).normalize().to_numpy()
    next_day = np.empty(len(idx), dtype=object)
    next_day[:-1] = day_id[1:]
    next_day[-1] = None
    eod_mask = (day_id != next_day)

    n = len(idx)
    w = np.zeros(n)
    in_pos = False
    side = 0
    entry_price = np.nan
    atr_entry = np.nan
    for t in range(n):
        if in_pos:
            if side > 0:
                tp = entry_price + 1.0 * atr_entry
                if high[t] >= tp:
                    in_pos = False
                    w[t] = 0.0
                    continue
            else:
                tp = entry_price - 1.0 * atr_entry
                if low[t] <= tp:
                    in_pos = False
                    w[t] = 0.0
                    continue
            if eod_mask[t]:
                in_pos = False
                w[t] = 0.0
                continue
            w[t] = side
        else:
            if eod_mask[t]:
                w[t] = 0.0
                continue
            if not np.isfinite(u[t]) or not np.isfinite(atr[t]) or atr[t] <= 0:
                continue
            if close[t] > u[t]:
                in_pos = True
                side = 1
                entry_price = close[t]
                atr_entry = atr[t]
                w[t] = 1.0
            elif config.allow_short and close[t] < lo[t]:
                in_pos = True
                side = -1
                entry_price = close[t]
                atr_entry = atr[t]
                w[t] = -1.0
    ws = pd.Series(w, index=idx)
    prev_w = ws.shift(1).fillna(0.0)
    ret = df["close"].pct_change().fillna(0.0)
    gross = prev_w * ret
    spread_drag = (ws - ws.shift(1).fillna(0.0)).abs() * config.spread_one_way
    net = gross - spread_drag
    return net


def _simplified_single_tp_vbt(
    df: pd.DataFrame, config: MaroyLadderConfig
) -> pd.Series:
    """Simplified vbt implementation via from_signals (reference).

    Uses a manually-computed entries/exits signal + pct-fee model. The SL/TP
    engine in vbt doesn't accept per-trade atr_entry levels directly, so we
    precompute the TP exit signal outside vbt and hand it in as exit signals
    — this tests that the signal+alignment plumbing matches pandas ref.
    """
    import vectorbt as vbt
    from ai_trade.backtest.strategies.phase3_7_h1_maroy_ladder import (
        _compute_noise_boundary,
        compute_atr_wilder_intraday,
    )
    df = df.sort_index()
    _, upper, lower = _compute_noise_boundary(df, config.noise_lookback_days)
    atr = compute_atr_wilder_intraday(
        df["high"], df["low"], df["close"], period=config.atr_period
    )
    close = df["close"]

    # Precompute entry/exit signals using the same iterative logic as pandas.
    n = len(df)
    long_entries = np.zeros(n, dtype=bool)
    long_exits = np.zeros(n, dtype=bool)
    short_entries = np.zeros(n, dtype=bool)
    short_exits = np.zeros(n, dtype=bool)
    c_arr = close.to_numpy()
    h_arr = df["high"].to_numpy()
    l_arr = df["low"].to_numpy()
    u_arr = upper.to_numpy()
    lo_arr = lower.to_numpy()
    a_arr = atr.to_numpy()
    day_id = pd.to_datetime(df.index).normalize().to_numpy()
    next_day = np.empty(n, dtype=object)
    next_day[:-1] = day_id[1:]
    next_day[-1] = None
    eod_mask = (day_id != next_day)

    in_pos = False
    side = 0
    entry_price = np.nan
    atr_entry = np.nan
    for t in range(n):
        if in_pos:
            if side > 0:
                tp = entry_price + 1.0 * atr_entry
                if h_arr[t] >= tp:
                    long_exits[t] = True
                    in_pos = False
                    continue
            else:
                tp = entry_price - 1.0 * atr_entry
                if l_arr[t] <= tp:
                    short_exits[t] = True
                    in_pos = False
                    continue
            if eod_mask[t]:
                if side > 0:
                    long_exits[t] = True
                else:
                    short_exits[t] = True
                in_pos = False
                continue
        else:
            if eod_mask[t]:
                continue
            if not np.isfinite(u_arr[t]) or not np.isfinite(a_arr[t]) or a_arr[t] <= 0:
                continue
            if c_arr[t] > u_arr[t]:
                in_pos = True
                side = 1
                entry_price = c_arr[t]
                atr_entry = a_arr[t]
                long_entries[t] = True
            elif config.allow_short and c_arr[t] < lo_arr[t]:
                in_pos = True
                side = -1
                entry_price = c_arr[t]
                atr_entry = a_arr[t]
                short_entries[t] = True

    pf = vbt.Portfolio.from_signals(
        close=close,
        entries=pd.Series(long_entries, index=close.index),
        exits=pd.Series(long_exits, index=close.index),
        short_entries=pd.Series(short_entries, index=close.index),
        short_exits=pd.Series(short_exits, index=close.index),
        fees=config.spread_one_way,
        slippage=0.0,
        freq="1T",
        init_cash=100_000,
    )
    # Bar-level returns (close-to-close, prev_weight_fraction_of_equity * ret).
    eq = pf.value()
    ret = eq.pct_change().fillna(0.0)
    return ret


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-crosslib", action="store_true",
                        help="Skip vectorbt cross-lib comparison")
    parser.add_argument("--skip-pbo", action="store_true",
                        help="Skip PBO grid (for quick smoke)")
    args = parser.parse_args(argv)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Loading SPY 1-min")
    spy = pd.read_parquet(SPY_PATH).sort_index()
    log.info("Loading QQQ 1-min")
    qqq = pd.read_parquet(QQQ_PATH).sort_index()

    # Primary config = Maróy 2024 paper best ladder.
    cfg = MaroyLadderConfig(
        noise_lookback_days=14,
        atr_period=20,
        tp1_mult=0.5,
        tp2_mult=1.0,
        tp3_mult=2.0,
        trailing_atr_mult=1.0,
        allow_short=True,
        flat_at_close=True,
        spread_one_way=6.7e-5,
    )
    cfg_hash = _short_hash(cfg)
    log.info(f"config hash={cfg_hash}")

    # --- Windows (SPY primary) ---
    spy_is = _slice(spy, IS_START, IS_END)
    spy_oos = _slice(spy, OOS_START, OOS_END)
    spy_fwd = _slice(spy, FWD_START, FWD_END)

    log.info("Running SPY IS")
    is_stats, is_res, is_daily = run_window(spy_is, cfg, "SPY_IS")
    log.info(f"IS: {is_stats}")
    log.info("Running SPY OOS")
    oos_stats, oos_res, oos_daily = run_window(spy_oos, cfg, "SPY_OOS")
    log.info(f"OOS: {oos_stats}")
    log.info("Running SPY FWD")
    fwd_stats, fwd_res, fwd_daily = run_window(spy_fwd, cfg, "SPY_FWD")
    log.info(f"FWD: {fwd_stats}")

    # --- SPY daily (buy-hold) benchmark for IR ---
    spy_close = spy["close"].resample("1D").last().dropna()
    spy_bh_daily = spy_close.pct_change().dropna()

    ir_oos = _ir_vs_spy(oos_daily, spy_bh_daily)

    # --- Cost×2 stress (Gate 13) ---
    cfg_2x = MaroyLadderConfig(
        **{**asdict(cfg), "spread_one_way": cfg.spread_one_way * 2}
    )
    log.info("Running SPY OOS × 2 cost")
    cost2_stats, _, cost2_daily = run_window(spy_oos, cfg_2x, "SPY_OOS_2x_cost")
    log.info(f"OOS × 2 cost: sharpe={cost2_stats['sharpe_daily']:.3f} cagr={cost2_stats['cagr']:.3%}")

    # --- Walk-forward ---
    # 8 windows over IS+OOS (~2017-06 → 2024-12).
    all_daily = pd.concat([is_daily, oos_daily])
    n_windows = 8
    wf_returns: list[float] = []
    wf_dds: list[float] = []
    if len(all_daily) >= n_windows * 30:
        size = len(all_daily) // n_windows
        for k in range(n_windows):
            w = all_daily.iloc[k * size : (k + 1) * size]
            wf_returns.append(float((1.0 + w).prod() - 1.0))
            eq = (1.0 + w).cumprod()
            wf_dds.append(abs(float((eq / eq.cummax() - 1.0).min())))
    wf_verdict = walk_forward_gate(wf_returns, wf_dds, min_windows=8,
                                   min_profitable_ratio=6 / 8,
                                   max_drawdown=0.999) if wf_returns else "reject"

    # --- Bootstrap 99.9% CI low > 0 on OOS + full ---
    boot_results = {}
    for label, daily in (("OOS", oos_daily), ("FULL", pd.concat([is_daily, oos_daily, fwd_daily]))):
        trades = daily.to_numpy()
        if len(trades) < 50:
            boot_results[label] = {"ci_low_999": float("nan"), "passes": False}
            continue
        rs = stationary_bootstrap_trades(trades, block_mean=5, n_resamples=2000, seed=42)
        means = rs.mean(axis=1)
        lo_999 = float(np.quantile(means, 0.001))
        boot_results[label] = {"ci_low_999": lo_999, "passes": lo_999 > 0}
    log.info(f"bootstrap: {boot_results}")

    # --- PBO single-feature — grid of TP1 multipliers (10 configs) ---
    pbo_verdict = "n/a (skipped)"
    pbo_value = float("nan")
    if not args.skip_pbo:
        log.info("PBO grid — varying tp1_mult over 10 values")
        tp1_grid = np.linspace(0.2, 1.2, 10)
        cols = []
        for tp1 in tp1_grid:
            c = MaroyLadderConfig(
                **{**asdict(cfg), "tp1_mult": float(tp1), "tp2_mult": max(float(tp1) + 0.2, 1.0),
                   "tp3_mult": max(float(tp1) + 1.0, 2.0)}
            )
            _, _, d = run_window(pd.concat([spy_is, spy_oos]), c, f"pbo_{tp1:.2f}")
            cols.append(d.to_numpy())
        # Align to min length
        min_len = min(len(c) for c in cols)
        mat = np.column_stack([c[-min_len:] for c in cols])
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pres = pbo(mat, n_blocks=10)
        pbo_value = float(pres.pbo)
        pbo_verdict = "pass" if pbo_value < 0.3 else "reject"
        log.info(f"PBO = {pbo_value:.3f} (gate <0.3)")

    # --- DSR ---
    oos_trades = oos_daily.to_numpy()
    if len(oos_trades) >= 10:
        dsr_res = dsr(oos_trades, n_trials=10)
        dsr_p = float(dsr_res.p_value)
    else:
        dsr_p = float("nan")
    log.info(f"DSR p={dsr_p}")

    # --- Cross-lib (simplified single-TP) ---
    crosslib_note = "skipped"
    delta_pp_cagr = float("nan")
    if not args.skip_crosslib:
        log.info("Cross-lib — simplified single-TP 1×ATR pandas vs vectorbt")
        try:
            pandas_bar = _simplified_single_tp_pandas(spy_oos, cfg)
            pandas_daily = _daily_from_bar(pandas_bar)
            pandas_cagr = _cagr(pandas_daily)
            vbt_bar = _simplified_single_tp_vbt(spy_oos, cfg)
            vbt_daily = _daily_from_bar(vbt_bar)
            vbt_cagr = _cagr(vbt_daily)
            delta_pp_cagr = abs(pandas_cagr - vbt_cagr) * 100
            crosslib_note = (
                f"pandas_cagr={pandas_cagr:.3%}, vbt_cagr={vbt_cagr:.3%}, "
                f"|Δ|={delta_pp_cagr:.2f}pp — simplified control only (single-TP), "
                f"ladder-proper cross-lib is a KNOWN LIMITATION"
            )
        except Exception as e:
            crosslib_note = f"FAILED — {type(e).__name__}: {e}"
            log.warning(f"cross-lib failed: {e}")

    # --- Cross-asset QQQ OOS ---
    log.info("Running QQQ OOS (cross-asset)")
    qqq_oos = _slice(qqq, OOS_START, OOS_END)
    qqq_stats, _, qqq_daily = run_window(qqq_oos, cfg, "QQQ_OOS")
    log.info(f"QQQ OOS: sharpe={qqq_stats['sharpe_daily']:.3f} cagr={qqq_stats['cagr']:.3%}")

    # --- 13-gate verdict table ---
    is_sharpe_pass = is_stats["sharpe_daily"] > 0.5
    oos_sharpe_pass = oos_stats["sharpe_daily"] >= 1.3
    oos_cagr_t = cagr_tier_A(oos_stats["cagr"])
    oos_mdd_t = mdd_tier_A(oos_stats["mdd"])
    fwd_sharpe_pass = fwd_stats["sharpe_daily"] > 0
    wf_pass = wf_verdict == "pass"
    median_hold_pass = (
        (is_stats["median_hold_min"] or 0) >= 60  # 1h = 60 minutes
    )
    ir_pass = ir_oos >= 0.2
    # Ladder cross-lib is a known limitation — gate 9 is EVALUATED on the
    # simplified single-TP control. If we fall back on single-TP control
    # only, note as KNOWN LIMITATION.
    crosslib_pass = (
        np.isfinite(delta_pp_cagr) and delta_pp_cagr <= 3.0
    )
    boot_pass = boot_results.get("OOS", {}).get("passes", False) and \
        boot_results.get("FULL", {}).get("passes", False)
    pbo_pass = pbo_verdict == "pass"
    dsr_pass = np.isfinite(dsr_p) and dsr_p < 0.05
    cost2_pass = cost2_stats["sharpe_daily"] > 1.0

    hard_gates_pass = crosslib_pass and boot_pass and pbo_pass and dsr_pass
    all_other_pass = (
        is_sharpe_pass and oos_sharpe_pass and fwd_sharpe_pass and wf_pass
        and median_hold_pass and ir_pass and cost2_pass
    )
    final_verdict = "PASS" if hard_gates_pass and all_other_pass else "FAIL"

    gate_rows = [
        ("1 IS Sharpe > 0.5", f"{is_stats['sharpe_daily']:.3f}",
         "PASS" if is_sharpe_pass else "FAIL"),
        ("2 OOS Sharpe >= 1.3", f"{oos_stats['sharpe_daily']:.3f}",
         "PASS" if oos_sharpe_pass else "FAIL"),
        ("3 OOS CAGR tier (WARN)",
         f"{oos_stats['cagr']:.3%} — {oos_cagr_t}", "WARNING-ONLY"),
        ("4 OOS MDD tier (WARN)",
         f"{oos_stats['mdd']:.3%} — {oos_mdd_t}", "WARNING-ONLY"),
        ("5 FWD Sharpe > 0", f"{fwd_stats['sharpe_daily']:.3f}",
         "PASS" if fwd_sharpe_pass else "FAIL"),
        ("6 WF >= 6/8 positive",
         f"{sum(1 for r in wf_returns if r > 0)}/{len(wf_returns)} profitable",
         "PASS" if wf_pass else "FAIL"),
        ("7 Median hold >= 1h",
         f"{is_stats['median_hold_min']:.1f} min",
         "PASS" if median_hold_pass else "FAIL"),
        ("8 IR vs SPY >= 0.2", f"{ir_oos:.3f}",
         "PASS" if ir_pass else "FAIL"),
        ("9 Cross-lib CAGR <= 3pp (HARD)", crosslib_note,
         "PASS" if crosslib_pass else "FAIL"),
        ("10 Bootstrap 99.9% CI low > 0 (HARD)",
         f"OOS={boot_results.get('OOS', {}).get('ci_low_999', 'n/a'):.6g}; "
         f"FULL={boot_results.get('FULL', {}).get('ci_low_999', 'n/a'):.6g}",
         "PASS" if boot_pass else "FAIL"),
        ("11 PBO single-feature < 0.3 (HARD)",
         f"pbo={pbo_value:.3f}" if np.isfinite(pbo_value) else "n/a",
         "PASS" if pbo_pass else "FAIL"),
        ("12 DSR p < 0.05 (HARD)",
         f"p={dsr_p:.4f}" if np.isfinite(dsr_p) else "n/a",
         "PASS" if dsr_pass else "FAIL"),
        ("13 Cost×2 Sharpe > 1.0",
         f"{cost2_stats['sharpe_daily']:.3f} (cagr={cost2_stats['cagr']:.3%})",
         "PASS" if cost2_pass else "FAIL"),
    ]

    # --- Write AGGREGATE.md ---
    lines = [
        "# Phase 3.7 H1.c — Maróy 2024 Ladder — Honest Validation",
        "",
        f"**Verdict: {final_verdict}**",
        "",
        f"- **Config hash:** `{cfg_hash}`",
        f"- **Git SHA:** `{_git_sha()}`",
        f"- **Universe:** SPY (primary), QQQ (cross-asset)",
        f"- **Windows:** IS {IS_START} → {IS_END} | OOS {OOS_START} → {OOS_END} | FWD {FWD_START} → {FWD_END}",
        f"- **Cost model (mandate §2.4 / §4.8 no-DARF):** spread {cfg.spread_one_way*10000:.2f}bps/side paid per weight-change (captures Ladder's 4-flip drag), commission 0, swap 0 intraday, tax 0.",
        "",
        "## 13-Gate Table",
        "",
        "| Gate | Value | Verdict |",
        "|------|-------|---------|",
    ]
    for name, val, verdict in gate_rows:
        lines.append(f"| {name} | {val} | **{verdict}** |")

    lines += [
        "",
        "## Window Summaries",
        "",
        "### SPY IS",
        f"- bars={is_stats['n_bars']:,}, entries={is_stats['n_entries']}, "
        f"median_hold={is_stats['median_hold_min']} min",
        f"- tp1={is_stats['tp1_hits']}, tp2={is_stats['tp2_hits']}, "
        f"tp3={is_stats['tp3_hits']}, trailing={is_stats['trailing_exits']}, "
        f"eod={is_stats['eod_exits']}",
        f"- Sharpe(daily)={is_stats['sharpe_daily']:.3f}, "
        f"CAGR={is_stats['cagr']:.3%}, MDD={is_stats['mdd']:.3%}",
        f"- Cum spread drag: {is_stats['cum_spread_pct']:.3%}",
        "",
        "### SPY OOS",
        f"- bars={oos_stats['n_bars']:,}, entries={oos_stats['n_entries']}, "
        f"median_hold={oos_stats['median_hold_min']} min",
        f"- tp1={oos_stats['tp1_hits']}, tp2={oos_stats['tp2_hits']}, "
        f"tp3={oos_stats['tp3_hits']}, trailing={oos_stats['trailing_exits']}, "
        f"eod={oos_stats['eod_exits']}",
        f"- Sharpe(daily)={oos_stats['sharpe_daily']:.3f}, "
        f"CAGR={oos_stats['cagr']:.3%} (tier **{oos_cagr_t}**), "
        f"MDD={oos_stats['mdd']:.3%} (tier **{oos_mdd_t}**)",
        f"- IR vs SPY buy-hold: {ir_oos:.3f}",
        "",
        "### SPY FWD",
        f"- bars={fwd_stats['n_bars']:,}, entries={fwd_stats['n_entries']}",
        f"- Sharpe(daily)={fwd_stats['sharpe_daily']:.3f}, "
        f"CAGR={fwd_stats['cagr']:.3%}, MDD={fwd_stats['mdd']:.3%}",
        "",
        "### QQQ OOS (cross-asset)",
        f"- entries={qqq_stats['n_entries']}, "
        f"Sharpe(daily)={qqq_stats['sharpe_daily']:.3f}, "
        f"CAGR={qqq_stats['cagr']:.3%}, MDD={qqq_stats['mdd']:.3%}",
        "",
        "## Cost treatment (Ladder-specific)",
        "",
        "The Maróy Ladder generates up to **4 weight changes per round-trip** "
        "(entry + TP1 + TP2 + TP3 / trailing). We apply spread cost on "
        "**each** weight change in the `prev_weight × ret` pipeline — this is "
        "strictly more punitive than a single-TP or trail-only exit and is the "
        "honest way to capture the Ladder's structural cost. Cumulative spread "
        f"drag on IS alone: **{is_stats['cum_spread_pct']:.3%}**.",
        "",
        "## Known limitations",
        "",
        "- **Cross-lib gate (#9) is evaluated on a SIMPLIFIED control (single-TP "
        "at 1×ATR + EOD flat)** rather than the full Ladder. vectorbt's "
        "`Portfolio.from_signals` does not accept variable-fraction exit "
        "schedules per trade. A faithful vbt Ladder would require manual "
        "iteration that mirrors the pandas reference, defeating the purpose of "
        "cross-lib validation. The simplified control shares entry logic and "
        "F2-alignment with the Ladder, so it is a valid sanity check on "
        "signal+plumbing — but **NOT** a full Ladder cross-lib match. This is "
        "disclosed honestly per mandate §2.4.",
        "- Tick-data realism: parquet is Tiingo 1-min bars; intra-bar TP hits "
        "use bar `high`/`low`, which can overstate realism vs continuous "
        "tick. Maróy 2024 and Zarattini 2024 use the same convention; this "
        "is consistent with the literature but known to be optimistic.",
        "",
        "## Citations",
        "",
        "- `[paper.zarattini_2024_intraday_spy, §3]` — noise boundary signal",
        "- `[paper.maroy_2024_intraday_improvements, §Ladder]` — 3-level TP ladder exit",
        "- `[advances_fin_ml, p.31-34]` — F2-alignment lookahead audit",
        "- `[advances_fin_ml, p.208-211]` — PBO via CSCV",
        "- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio",
        "- `[docs/investment-mandate.md §2.4]` — 13-gate framework",
        "- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers warning-only",
        "- `[docs/investment-mandate.md §4.8]` — Pepperstone no-DARF",
    ]

    out_path = REPORT_DIR / "AGGREGATE.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info(f"wrote {out_path}")

    # JSON summary for programmatic use.
    json_payload = {
        "verdict": final_verdict,
        "config_hash": cfg_hash,
        "git_sha": _git_sha(),
        "is": is_stats,
        "oos": oos_stats,
        "fwd": fwd_stats,
        "qqq_oos": qqq_stats,
        "cost2_oos": cost2_stats,
        "ir_oos_vs_spy": ir_oos,
        "cagr_tier_oos": oos_cagr_t,
        "mdd_tier_oos": oos_mdd_t,
        "wf_verdict": wf_verdict,
        "wf_returns": wf_returns,
        "wf_dds": wf_dds,
        "bootstrap": boot_results,
        "pbo_value": pbo_value,
        "pbo_verdict": pbo_verdict,
        "dsr_p_value": dsr_p,
        "crosslib_delta_pp_cagr": delta_pp_cagr,
        "crosslib_note": crosslib_note,
        "gates": {
            "1_is_sharpe": is_sharpe_pass,
            "2_oos_sharpe": oos_sharpe_pass,
            "5_fwd_sharpe": fwd_sharpe_pass,
            "6_wf": wf_pass,
            "7_median_hold": median_hold_pass,
            "8_ir": ir_pass,
            "9_crosslib_hard": crosslib_pass,
            "10_bootstrap_hard": boot_pass,
            "11_pbo_hard": pbo_pass,
            "12_dsr_hard": dsr_pass,
            "13_cost2": cost2_pass,
        },
    }
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(json_payload, indent=2, default=float), encoding="utf-8"
    )
    log.info(f"verdict={final_verdict}")
    return 0 if final_verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
