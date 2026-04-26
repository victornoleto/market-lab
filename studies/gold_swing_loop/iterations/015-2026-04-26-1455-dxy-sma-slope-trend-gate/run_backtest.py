"""Iter 015 — DXY SMA-slope trend regime gate, gold long-only.

Strategy
--------
* Single-asset, **LONG-ONLY**. Position[t] ∈ {0, 1}.
* Flag[t] = 1 iff SMA_200(DXY)[t] < SMA_200(DXY)[t - 20]
  (DXY 200d MA falling on 20-day window).
* Daily DXY signal forward-filled to each dataset's bar index.
* Position lagged 1 bar at execution; look-ahead-free.
* Pre-committed sma_window=200, slope_lookback=20 per IC-8 single-cfg.

Citations
---------
* `[stocks_on_the_move, p.100]` — 200-day SMA canonical trend filter (PRIMARY)
* `[trading_systems_methods, p.13-14]` — gold/USD inverse coupling
* `[ilmanen_expected_returns, ch.10]` — gold as USD-cycle hedge
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative_n_trials = 15
* DEAD_ENDS GS-5 — open: trend-continuation framings + FRED long-history data
* DEAD_ENDS GS-14 — corollary test: macro-generic vs rate-specific clock?
* IC-7 boundary (sister 045/046) — out-of-family ρ < 0.50 unlocks DSR uplift
* IC-8 — single pre-committed cfg per iter
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.dxy_trend_gold import (  # noqa: E402
    align_signal_to_index,
    dxy_sma_falling_flag,
    dxy_sma_falling_flag_numpy,
)
from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from cost_models import apply_inter_costs_with_darf, apply_pepperstone_costs  # noqa: E402
from scoring import (  # noqa: E402
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    score_strategy,
)

ITER_DIR = Path(__file__).resolve().parent
CFG_ID = "dxy_sma_slope_falling_200_20_long_only"

# Cumulative trial count: 14 prior + 1 (this) = 15.
CUMULATIVE_N_TRIALS = 15

SMA_WINDOW = 200       # Clenow canonical trend MA `[stocks_on_the_move, p.100]`
SLOPE_LOOKBACK = 20    # 1 month slope estimation (standard "is the trend developing")

DTWEXBGS_PATH = ROOT / "data" / "external" / "macro" / "dtwexbgs_daily.parquet"

DATA_PATHS = {
    "gld_long":        ROOT / "data" / "tiingo" / "daily" / "prices" / "GLD.parquet",
    "xauusd_real":     ROOT / "data" / "tiingo" / "daily" / "prices" / "xauusd.parquet",
    "xauusd_intraday": ROOT / "data" / "tiingo" / "1hour" / "prices" / "xauusd.parquet",
}

TF_PARAMS = {
    "gld_long":        {"tf": "1d", "ann": 252},
    "xauusd_real":     {"tf": "1d", "ann": 252},
    "xauusd_intraday": {"tf": "1h", "ann": 5119},
}


# ===========================================================================
# Helpers (mirror iter 014 patterns)
# ===========================================================================


def load_close(name: str) -> pd.Series:
    df = pd.read_parquet(DATA_PATHS[name]).sort_index()
    return df["close"].astype(float)


def load_dxy() -> pd.Series:
    df = pd.read_parquet(DTWEXBGS_PATH).sort_index()
    return df["close"].astype(float)


def _bar_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def compute_mean_hold(position: pd.Series, ann: int) -> tuple[float, int, float]:
    pos = position.values
    in_trade = False
    starts: list[int] = []
    ends: list[int] = []
    for i, p in enumerate(pos):
        if not in_trade and p > 0:
            starts.append(i)
            in_trade = True
        elif in_trade and p == 0:
            ends.append(i)
            in_trade = False
    if in_trade:
        ends.append(len(pos))
    if not starts:
        return 0.0, 0, 0.0
    holds_bars = [(e - s) for s, e in zip(starts, ends)]
    mean_bars = float(np.mean(holds_bars))
    bars_per_day = ann / 252.0
    mean_days = mean_bars / bars_per_day if bars_per_day > 0 else mean_bars
    return float(mean_days), int(len(starts)), mean_bars


def count_flips(position: pd.Series) -> int:
    return int((position.diff().abs() > 0).sum())


def compute_metrics(net_pnl: pd.Series, ann: int) -> dict[str, float]:
    rets = net_pnl.dropna()
    if rets.std() == 0 or len(rets) < 2:
        return {"sharpe": 0.0, "sharpe_periodic": 0.0, "cagr": 0.0, "mdd": 0.0}
    sharpe_per = sharpe_periodic(rets.values)
    sharpe_ann = float(sharpe_per * np.sqrt(ann))
    eq = (1.0 + rets).cumprod()
    span_yr = max((rets.index[-1] - rets.index[0]).days / 365.25, 1e-9)
    cagr = float(eq.iloc[-1] ** (1.0 / span_yr) - 1.0)
    cummax = eq.cummax()
    dd = (eq - cummax) / cummax
    mdd = float(-dd.min())
    return {"sharpe": sharpe_ann, "sharpe_periodic": float(sharpe_per),
            "cagr": cagr, "mdd": mdd}


def run_walk_forward(rets: pd.Series, n_windows: int = 8) -> tuple[bool, list[float], list[float]]:
    n = len(rets)
    if n < n_windows * 20:
        return False, [], []
    block = n // n_windows
    oos_returns: list[float] = []
    drawdowns: list[float] = []
    for i in range(n_windows):
        chunk = rets.iloc[i * block: (i + 1) * block]
        if len(chunk) < 5 or chunk.std() == 0:
            oos_returns.append(0.0)
            drawdowns.append(0.0)
            continue
        eq = (1.0 + chunk).cumprod()
        cummax = eq.cummax()
        dd = -((eq - cummax) / cummax).min()
        total_ret = float(eq.iloc[-1] - 1.0)
        oos_returns.append(total_ret)
        drawdowns.append(float(dd))
    verdict = walk_forward_gate(
        oos_returns_per_window=oos_returns,
        drawdowns_per_window=drawdowns,
        min_windows=n_windows,
        min_profitable_ratio=6.0 / n_windows,
        max_drawdown=0.25,
    )
    return verdict == "pass", oos_returns, drawdowns


def run_bootstrap(rets: pd.Series, ann: int) -> tuple[bool, float, float]:
    arr = rets.dropna().values
    if len(arr) < 50 or arr.std() == 0:
        return False, 0.0, 0.0
    block_mean = max(5, int(ann / 1000))
    samples = stationary_bootstrap_trades(
        arr, block_mean=block_mean, n_resamples=2000, seed=42
    )
    sharpes = []
    for row in samples:
        s = sharpe_periodic(row)
        sharpes.append(s * np.sqrt(ann))
    sharpes = np.array(sharpes)
    lo = float(np.percentile(sharpes, 0.05))
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_gross_check(position: pd.Series, returns: pd.Series) -> tuple[float, float]:
    pos_pd = position.shift(1).fillna(0.0)
    pnl_pd = pos_pd * returns
    eq_pd = (1.0 + pnl_pd).cumprod()
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_pd = float(eq_pd.iloc[-1] ** (1.0 / span_yr) - 1.0)
    pos_np = pos_pd.values.astype(np.float64)
    ret_np = returns.values.astype(np.float64)
    pnl_np = pos_np * ret_np
    eq_np = np.cumprod(1.0 + pnl_np)
    cagr_np = float(eq_np[-1] ** (1.0 / span_yr) - 1.0)
    return cagr_pd, cagr_np


def run_pre_val(close: pd.Series, position: pd.Series) -> dict:
    p_active = float(position.mean())
    n_total = int(len(position))
    n_active = int(position.sum())
    n_flips = count_flips(position)

    log_ret = np.log(close / close.shift(1))
    pos_lag = position.shift(1).fillna(0.0)
    active_returns = log_ret.where(pos_lag > 0).dropna()
    if len(active_returns) > 0:
        mu_per_bar = float(active_returns.mean())
        mu_per_bar_bps = mu_per_bar * 1e4
    else:
        mu_per_bar = 0.0
        mu_per_bar_bps = 0.0

    span_yr = max((close.index[-1] - close.index[0]).days / 365.25, 1e-9)

    p_active_pass = bool(0.10 <= p_active <= 0.90)
    mu_pass = bool(mu_per_bar > 0)
    flips_pass = bool(n_flips >= 5)

    passed = p_active_pass and mu_pass and flips_pass
    reason_parts = []
    if not p_active_pass:
        reason_parts.append(f"p_active={p_active:.3f} ∉ [0.10, 0.90] (signal degenerate)")
    if not mu_pass:
        reason_parts.append(f"mu_active_bps={mu_per_bar_bps:+.3f} ≤ 0 (no edge)")
    if not flips_pass:
        reason_parts.append(f"n_flips={n_flips} < 5 (insufficient trades)")
    reason = "passed all conditions" if passed else "; ".join(reason_parts)

    return {
        "p_active": p_active,
        "n_active_bars": n_active,
        "n_total_bars": n_total,
        "n_flips": n_flips,
        "mu_active_bps_per_bar": mu_per_bar_bps,
        "span_yr": span_yr,
        "p_active_pass": p_active_pass,
        "mu_pass": mu_pass,
        "flips_pass": flips_pass,
        "passed": passed,
        "reason": reason,
    }


# ===========================================================================
# Per-dataset run
# ===========================================================================


def build_position(close: pd.Series, dxy: pd.Series) -> pd.Series:
    flag_daily = dxy_sma_falling_flag(
        dxy, sma_window=SMA_WINDOW, slope_lookback=SLOPE_LOOKBACK
    )
    flag_aligned = align_signal_to_index(flag_daily, close.index)
    return flag_aligned.astype(float).rename("position")


def run_one_dataset(name: str, dxy: pd.Series) -> dict:
    params = TF_PARAMS[name]
    ann = params["ann"]
    tf = params["tf"]

    close = load_close(name)
    position = build_position(close, dxy)
    bar_ret = _bar_returns(close)

    pre_val = run_pre_val(close, position)

    if tf == "1d":
        swap_long = -1.0
        swap_short = 0.3
    elif tf == "1h":
        swap_long = -1.0 / 24.0
        swap_short = 0.3 / 24.0
    else:
        raise ValueError(f"unknown tf: {tf}")

    cost_a = apply_pepperstone_costs(
        bar_ret, position,
        spread_rt_bps=8.0,
        swap_long_bps=swap_long,
        swap_short_bps=swap_short,
        intraday_close=False,
    )
    m_a = compute_metrics(cost_a.net_pnl, ann)
    rets_a = cost_a.net_pnl.dropna()

    if tf == "1d":
        cost_b = apply_inter_costs_with_darf(
            bar_ret, position,
            fx_rt_bps=100.0,
            darf_rate=0.15,
        )
        m_b = compute_metrics(cost_b.net_pnl, ann)
        track_b_metrics = {
            **m_b,
            "n_swap_nights": cost_b.n_swap_nights,
            "cost_summary": cost_b.summary(),
        }
    else:
        track_b_metrics = {
            "note": "Track B not viable on intraday (T+1 settlement; daily-only)",
            "sharpe": 0.0, "cagr": 0.0, "mdd": 0.0,
        }

    mean_hold_days, n_trades, mean_hold_bars = compute_mean_hold(position, ann)

    g1_pbo = True
    g1_note = "single-cfg PBO degenerate (IC-8); pass by convention"

    if rets_a.std() > 0 and len(rets_a) > 30:
        dsr_res = dsr_func(rets_a.values, n_trials=CUMULATIVE_N_TRIALS)
        dsr_p = float(dsr_res.p_value)
        g2_dsr = bool(dsr_p < 0.05)
    else:
        dsr_p = 1.0
        g2_dsr = False

    g3_wf, wf_returns, wf_dds = run_walk_forward(rets_a, n_windows=8)

    cut = int(0.7 * len(rets_a))
    oos_chunk = rets_a.iloc[cut:]
    oos_sharpe = (
        sharpe_periodic(oos_chunk.values) * np.sqrt(ann)
        if len(oos_chunk) > 1 else 0.0
    )
    g4_oos = bool(oos_sharpe > 0)

    fwd_chunk = rets_a[rets_a.index >= "2022-01-01"]
    fwd_sharpe = (
        sharpe_periodic(fwd_chunk.values) * np.sqrt(ann)
        if len(fwd_chunk) > 1 else 0.0
    )
    g5_fwd = bool(fwd_sharpe > 0)

    g6_boot, ci_lo, ci_hi = run_bootstrap(rets_a, ann)

    cagr_pd_gross, cagr_np_gross = cross_lib_gross_check(position, bar_ret)
    g7_diff_pp = abs(cagr_pd_gross - cagr_np_gross) * 100.0
    g7_cl = bool(g7_diff_pp <= 3.0)

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    gross_pnl_total = float(cost_a.gross_pnl.sum())
    spread_total = float(-cost_a.spread_cost.sum())
    swap_total = float(-cost_a.swap_cost.sum())
    net_total = float(cost_a.net_pnl.sum())
    per_trade_gross_bps = (gross_pnl_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_cost_bps = (-(spread_total + swap_total) / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_net_bps = (net_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0

    return {
        "tf": tf,
        "params": {"sma_window": SMA_WINDOW, "slope_lookback": SLOPE_LOOKBACK, "ann": ann},
        "n_bars": int(len(close)),
        "date_range": [close.index[0].isoformat(), close.index[-1].isoformat()],
        "pre_val": pre_val,
        "track_a_metrics": {
            **m_a,
            "dsr_p_value": dsr_p,
            "mean_hold_days": mean_hold_days,
            "mean_hold_bars": mean_hold_bars,
            "n_trades": n_trades,
            "n_swap_nights": cost_a.n_swap_nights,
            "n_weekend_holds": cost_a.n_weekend_holds,
            "cost_summary": cost_a.summary(),
            "per_trade_gross_bps": per_trade_gross_bps,
            "per_trade_cost_bps": per_trade_cost_bps,
            "per_trade_net_bps": per_trade_net_bps,
        },
        "track_b_metrics": track_b_metrics,
        "gates": {
            "g1_pbo": g1_pbo, "g1_note": g1_note,
            "g2_dsr": g2_dsr, "dsr_p_value": dsr_p,
            "g3_wf": g3_wf, "wf_returns": wf_returns, "wf_dds": wf_dds,
            "g4_oos": g4_oos, "oos_sharpe": float(oos_sharpe),
            "g5_fwd": g5_fwd, "fwd_sharpe": float(fwd_sharpe),
            "g6_bootstrap": g6_boot, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "g7_crosslib": g7_cl,
            "g7_cagr_pd_gross": cagr_pd_gross,
            "g7_cagr_np_gross": cagr_np_gross,
            "g7_diff_pp": g7_diff_pp,
        },
        "n_passed": gates.n_passed,
        "_returns_series": {
            "index": [d.isoformat() for d in cost_a.net_pnl.index],
            "net_returns": [float(x) for x in cost_a.net_pnl.values],
        },
    }


# ===========================================================================
# IC-7 correlation diagnostic vs prior streams (inc. iter 014)
# ===========================================================================


def _load_returns_from_iter(iter_dir: Path, ds: str, cfg_id: str) -> pd.Series | None:
    rj = iter_dir / "results.json"
    if not rj.exists():
        return None
    try:
        data = json.loads(rj.read_text(encoding="utf-8"))
    except Exception:
        return None
    rs = data.get("returns_series", {}).get(ds, {})
    series = rs.get(cfg_id)
    if not series:
        return None
    idx = pd.DatetimeIndex(series["index"])
    return pd.Series(series["net_returns"], index=idx)


def ic7_diagnostic(results: dict) -> dict:
    iter_root = ITER_DIR.parent
    bases = [
        ("vs_iter_003", iter_root / "003-2026-04-26-0228-rsi2-sma200-filter", "connors_rsi2_sma200_filter"),
        ("vs_iter_011", iter_root / "011-2026-04-26-1334-vol-regime-gate-inverse", "vol_regime_inverse_60_252_long_only"),
        ("vs_iter_013", iter_root / "013-2026-04-26-1413-volregime-inverse-sma200", "vol_regime_inverse_sma200_long_only"),
        ("vs_iter_014", iter_root / "014-2026-04-26-1431-tips-dfii10-macro-stream", "macro_dfii10_falling_60d_long_only"),
    ]
    out: dict[str, dict] = {}
    for ds in ("gld_long", "xauusd_real", "xauusd_intraday"):
        idx = pd.DatetimeIndex(results[ds]["_returns_series"]["index"])
        cur = pd.Series(results[ds]["_returns_series"]["net_returns"], index=idx)
        ds_diag: dict[str, object] = {"n_bars": int(len(cur))}
        for label, base_dir, base_cfg in bases:
            base = _load_returns_from_iter(base_dir, ds, base_cfg)
            if base is None or len(base) == 0:
                ds_diag[label] = {"available": False}
                continue
            joined = pd.concat([cur, base], axis=1, join="inner").dropna()
            if joined.empty or joined.iloc[:, 0].std() == 0 or joined.iloc[:, 1].std() == 0:
                ds_diag[label] = {"available": True, "rho": None, "n_overlap": int(len(joined))}
            else:
                rho = float(joined.iloc[:, 0].corr(joined.iloc[:, 1]))
                ds_diag[label] = {"available": True, "rho": rho, "n_overlap": int(len(joined))}
        out[ds] = ds_diag
    return out


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}, "
        f"SMA_WINDOW={SMA_WINDOW}, SLOPE_LOOKBACK={SLOPE_LOOKBACK})"
    )

    dxy = load_dxy()
    print(
        f"  DTWEXBGS cache: {len(dxy)} bars, "
        f"{dxy.index.min().date()} → {dxy.index.max().date()}, "
        f"min={dxy.min():.2f}, max={dxy.max():.2f}, mean={dxy.mean():.2f}"
    )

    print("\n=== Stage 3a — pre-validation per dataset ===")
    pre_val_per_ds: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        close = load_close(name)
        position = build_position(close, dxy)
        pv = run_pre_val(close, position)
        pre_val_per_ds[name] = pv
        print(
            f"  {name:18s} p_active={pv['p_active']:.3f} "
            f"({pv['n_active_bars']}/{pv['n_total_bars']} bars), "
            f"μ={pv['mu_active_bps_per_bar']:+.3f}bps/bar, "
            f"flips={pv['n_flips']} → "
            f"{'✓' if pv['passed'] else '✗'} ({pv['reason']})"
        )

    n_pass = sum(1 for d in pre_val_per_ds.values() if d["passed"])
    print(f"\n  → {n_pass}/3 datasets pass pre-val gate")

    pre_val_path = ITER_DIR / "pre_val.json"
    pre_val_path.write_text(json.dumps(pre_val_per_ds, indent=2, default=str), encoding="utf-8")

    if n_pass == 0:
        print("!! PRE-VAL FAILED on all 3 datasets — AUTO-ABORTING.")
        verdict = {
            "config_id": CFG_ID,
            "status": "iterating",
            "tier": "FAIL",
            "total_score": 0,
            "winner_conditions_met": False,
            "hold_time_gate_pass": False,
            "is_winner": False,
            "auto_aborted_at_pre_val": True,
            "pre_val": pre_val_per_ds,
            "cumulative_n_trials": CUMULATIVE_N_TRIALS,
            "primary_citation": "[stocks_on_the_move, p.100]",
            "hypothesis_slug": "dxy-sma-slope-trend-gate",
            "broker_track": "pepperstone_cfd",
            "timeframes_used": ["1d", "1h"],
        }
        (ITER_DIR / "verdict.json").write_text(
            json.dumps(verdict, indent=2, default=str), encoding="utf-8"
        )
        return

    print("\n=== Stage 3b — full 3-dataset backtest (Track A primary) ===")
    results: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ({TF_PARAMS[name]['tf']}) ---")
        r = run_one_dataset(name, dxy)
        results[name] = r
        ma = r["track_a_metrics"]
        bench = BENCHMARKS[name]
        print(
            f"  Track A: Sharpe={ma['sharpe']:+.4f} (bench {bench.sharpe:+.4f}, Δ {ma['sharpe']-bench.sharpe:+.4f}), "
            f"CAGR={ma['cagr']:+.4%} (bench {bench.cagr:+.4%}), "
            f"MDD={ma['mdd']:.4%} (bench {bench.mdd:.4%}), "
            f"mean_hold={ma['mean_hold_days']:.2f}d, n_trades={ma['n_trades']}, gates={r['n_passed']}/7"
        )
        print(
            f"  Per-trade attribution: gross={ma['per_trade_gross_bps']:+.2f}bps, "
            f"cost={ma['per_trade_cost_bps']:+.2f}bps, net={ma['per_trade_net_bps']:+.2f}bps"
        )
        if "sharpe" in r["track_b_metrics"] and r["track_b_metrics"].get("note") is None:
            mb = r["track_b_metrics"]
            print(f"  Track B: Sharpe={mb['sharpe']:+.4f}, CAGR={mb['cagr']:+.4%}, MDD={mb['mdd']:.4%}")
        elif r["track_b_metrics"].get("note"):
            print(f"  Track B: {r['track_b_metrics']['note']}")

    print("\n=== IC-7 correlation diagnostic ===")
    ic7 = ic7_diagnostic(results)
    for ds, d in ic7.items():
        for label in ("vs_iter_003", "vs_iter_011", "vs_iter_013", "vs_iter_014"):
            v = d.get(label, {})
            if v.get("available") and v.get("rho") is not None:
                print(f"  {ds:18s} {label:12s} ρ = {v['rho']:+.3f} (n={v['n_overlap']})")
            else:
                print(f"  {ds:18s} {label:12s} N/A")

    metrics = {
        ds: DatasetMetrics(
            sharpe=results[ds]["track_a_metrics"]["sharpe"],
            cagr=results[ds]["track_a_metrics"]["cagr"],
            mdd=results[ds]["track_a_metrics"]["mdd"],
            dsr_p_value=results[ds]["track_a_metrics"]["dsr_p_value"],
        )
        for ds in results
    }
    gates_dict = {
        ds: Gates(
            g1_pbo=results[ds]["gates"]["g1_pbo"],
            g2_dsr=results[ds]["gates"]["g2_dsr"],
            g3_wf=results[ds]["gates"]["g3_wf"],
            g4_oos=results[ds]["gates"]["g4_oos"],
            g5_fwd=results[ds]["gates"]["g5_fwd"],
            g6_bootstrap=results[ds]["gates"]["g6_bootstrap"],
            g7_crosslib=results[ds]["gates"]["g7_crosslib"],
        )
        for ds in results
    }
    score = score_strategy(metrics, gates_dict, cumulative_n_trials=CUMULATIVE_N_TRIALS)

    primary_ds = "xauusd_intraday"
    primary_hold = results[primary_ds]["track_a_metrics"]["mean_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    sharpes = {ds: results[ds]["track_a_metrics"]["sharpe"] for ds in results}
    n_neg = sum(1 for v in sharpes.values() if v < 0)
    primary_neg = sharpes[primary_ds] <= 0
    sharpe_kill = bool(primary_neg or n_neg >= 2)

    gld_sharpe_kill = bool(sharpes["gld_long"] < 0.30)

    xauusd_real_negedge = sharpes["xauusd_real"] < BENCHMARKS["xauusd_real"].sharpe
    xauusd_intra_negedge = sharpes["xauusd_intraday"] < BENCHMARKS["xauusd_intraday"].sharpe
    cross_dataset_kill = bool(xauusd_real_negedge and xauusd_intra_negedge)

    gld_ntrades = results["gld_long"]["track_a_metrics"]["n_trades"]
    n_trades_kill = bool(gld_ntrades < 5)

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== HYPOTHESIS KILL CRITERIA ===\n"
        f"Sharpes (Track A net): {sharpes}\n"
        f"primary_neg ({primary_ds}): {primary_neg}, n_neg={n_neg}/3, sharpe_kill = {sharpe_kill}\n"
        f"gld_long Sh < 0.30 (family broken): {gld_sharpe_kill} (Sh={sharpes['gld_long']:.3f})\n"
        f"xauusd both Δ < 0 (gld-only edge): {cross_dataset_kill}\n"
        f"gld_long n_trades collapse < 5: {n_trades_kill} (n_trades={gld_ntrades})"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "sma_window": SMA_WINDOW,
            "slope_lookback": SLOPE_LOOKBACK,
            "tf_params": TF_PARAMS,
            "track_a_spread_rt_bps": 8.0,
            "track_a_swap_long_bps_per_night": -1.0,
            "track_a_swap_short_bps_per_night": 0.3,
            "track_b_fx_rt_bps": 100.0,
            "track_b_darf_rate": 0.15,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "dxy_cache": {
            "n_bars": int(len(dxy)),
            "date_range": [dxy.index.min().isoformat(), dxy.index.max().isoformat()],
            "min": float(dxy.min()),
            "max": float(dxy.max()),
            "mean": float(dxy.mean()),
        },
        "pre_val": pre_val_per_ds,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "ic7_diagnostic": ic7,
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "mean_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
            "note": "200d-MA slope persists multi-month; intentionally swing-extended",
        },
        "kill_criteria": {
            "sharpes": sharpes,
            "primary_dataset": primary_ds,
            "primary_negative": primary_neg,
            "n_negative_datasets": n_neg,
            "sharpe_kill_fired": sharpe_kill,
            "gld_sharpe_below_30_kill": gld_sharpe_kill,
            "xauusd_cross_dataset_kill": cross_dataset_kill,
            "n_trades_collapse_kill": n_trades_kill,
            "gld_n_trades": gld_ntrades,
        },
        "is_winner": is_winner,
        "returns_series": {
            ds: {CFG_ID: results[ds]["_returns_series"]} for ds in results
        },
        "benchmarks_snapshot": {
            ds: {
                "sharpe": BENCHMARKS[ds].sharpe,
                "cagr": BENCHMARKS[ds].cagr,
                "mdd": BENCHMARKS[ds].mdd,
                "label": BENCHMARKS[ds].label,
            }
            for ds in results
        },
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path}")

    verdict = score.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[stocks_on_the_move, p.100]"
    verdict["hypothesis_slug"] = "dxy-sma-slope-trend-gate"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d", "1h"]
    verdict["track_a_metrics"] = {ds: results[ds]["track_a_metrics"] for ds in results}
    verdict["track_b_metrics"] = {ds: results[ds]["track_b_metrics"] for ds in results}
    verdict["kill_criteria"] = out["kill_criteria"]
    verdict["pre_val"] = pre_val_per_ds
    verdict["ic7_diagnostic"] = ic7
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict["auto_aborted_at_pre_val"] = False
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(json.dumps(verdict, indent=2, default=str), encoding="utf-8")
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
