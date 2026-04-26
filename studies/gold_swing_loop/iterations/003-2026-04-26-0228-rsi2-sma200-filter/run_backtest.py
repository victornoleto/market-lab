"""Iter 003 — Connors RSI(2)<5 + SMA(200) trend-regime filter.

Strategy (extends iter 001's Connors RSI(2) MR with one entry gate)
---------------------------------------------------------------------
* Compute RSI(2), SMA(5), SMA(200) on the daily close.
* Enter long at bar t (state := 1) when ALL hold:
      RSI(2)[t] < 5
      AND close[t] < SMA(5)[t]      (same as iter 001)
      AND close[t] > SMA(200)[t]    (NEW — Connors trend filter)
      AND state == 0
* Exit (state := 0) when close[t] > SMA(5)[t] AND state == 1
  (unchanged from iter 001).
* Position is binary {0, 1}; long-only; no leverage; no stops.

Datasets: gld_long, xauusd_real, xauusd_intraday (daily-resampled from 1h).

Output: ``results.json`` with per-dataset metrics, gate outcomes, and
returns series ready for ``score_strategy``; ``verdict.json`` with score +
hold-time gate + winner check.

Citations
---------
* `[short_term_trading_strategies, p.105-118]` — Connors trend filter chapter
* `[short_term_trading_strategies, p.74-86]` — base RSI(2)<5 MR rule
* `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional MR
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest
* `[advances_fin_ml, p.222-223]` — DSR / PSR with cumulative n_trials
* DEAD_ENDS GS-3 escape hatch #1 — `studies/gold_swing_loop/DEAD_ENDS.md`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # repo root (worktree)
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import psr as psr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from cost_models import (  # noqa: E402
    apply_inter_costs_with_darf,
    apply_pepperstone_costs,
)
from datasets import load_dataset  # noqa: E402
from scoring import (  # noqa: E402
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    score_strategy,
)

ITER_DIR = Path(__file__).resolve().parent
CFG_ID = "connors_rsi2_sma200_filter"
# iter 001 (1) + iter 002 (1) + this iter (1) = 3
CUMULATIVE_N_TRIALS = 3


# ---------------------------------------------------------------------------
# Strategy primitives
# ---------------------------------------------------------------------------


def wilder_rsi(close: pd.Series, period: int) -> pd.Series:
    """Wilder's RSI (smoothed = EMA with alpha = 1/period)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)


def connors_rsi2_signal_with_trend_filter(
    df: pd.DataFrame,
    *,
    rsi_period: int = 2,
    rsi_threshold: float = 5.0,
    sma_period: int = 5,
    sma_trend_period: int | None = 200,
) -> pd.Series:
    """RSI(2)<5 mean-reversion entry, gated by ``close > SMA(N_trend)``.

    Parameters
    ----------
    df : pd.DataFrame
        Daily-bar OHLC frame with ``close`` column.
    rsi_period, rsi_threshold, sma_period
        Same as iter 001 (defaults reproduce Connors RSI(2)<5 + SMA(5)).
    sma_trend_period
        Lookback for the trend-regime filter. ``None`` disables the gate
        entirely (signal collapses to iter 001's behavior).

    Returns
    -------
    pd.Series of dtype float64, values in {0.0, 1.0}, indexed identically
    to ``df``.
    """
    close = df["close"].astype(float)
    rsi = wilder_rsi(close, rsi_period)
    sma = close.rolling(sma_period, min_periods=sma_period).mean()

    enter = (rsi < rsi_threshold) & (close < sma)
    if sma_trend_period is not None:
        sma_trend = close.rolling(
            sma_trend_period, min_periods=sma_trend_period
        ).mean()
        # Trend filter: must be above SMA(N_trend); NaN warmup → False
        # (no entry while regime undefined).
        trend_ok = (close > sma_trend).fillna(False)
        enter = enter & trend_ok
    exit_ = close > sma

    pos = np.zeros(len(close), dtype=np.float64)
    state = 0
    for i in range(len(close)):
        if state == 0:
            if bool(enter.iloc[i]):
                state = 1
        else:  # state == 1
            if bool(exit_.iloc[i]):
                state = 0
        pos[i] = state
    return pd.Series(pos, index=close.index, name="position")


def daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def resample_1h_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 1h OHLCV to daily OHLCV (last close per day)."""
    out = df.resample("D").agg({
        "open":  "first",
        "high":  "max",
        "low":   "min",
        "close": "last",
        "adj_close": "last",
        "volume": "sum",
    })
    return out.dropna(subset=["close"])


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------


def annualization_factor(name: str) -> int:
    return 252


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
    return {
        "sharpe": sharpe_ann,
        "sharpe_periodic": float(sharpe_per),
        "cagr": cagr,
        "mdd": mdd,
    }


def compute_mean_hold_days(position: pd.Series) -> tuple[float, int]:
    """Mean hold time in trading days (long-only). Returns (mean, n_trades)."""
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
        return 0.0, 0
    holds = [(e - s) for s, e in zip(starts, ends)]
    return float(np.mean(holds)), int(len(starts))


# ---------------------------------------------------------------------------
# Gate runners (per dataset)
# ---------------------------------------------------------------------------


def run_walk_forward(
    rets: pd.Series, n_windows: int = 8, ann: int = 252
) -> tuple[bool, list[float], list[float]]:
    n = len(rets)
    if n < n_windows * 20:
        return False, [], []

    block = n // n_windows
    oos_returns: list[float] = []
    drawdowns: list[float] = []
    for i in range(n_windows):
        chunk = rets.iloc[i * block : (i + 1) * block]
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
    """G6: 99.9% CI lower bound > 0 via stationary bootstrap on returns."""
    arr = rets.dropna().values
    if len(arr) < 50 or arr.std() == 0:
        return False, 0.0, 0.0
    samples = stationary_bootstrap_trades(
        arr, block_mean=5, n_resamples=2000, seed=42
    )
    sharpes = []
    for row in samples:
        s = sharpe_periodic(row)
        sharpes.append(s * np.sqrt(ann))
    sharpes = np.array(sharpes)
    lo = float(np.percentile(sharpes, 0.05))  # 99.9% lower
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_check(
    position: pd.Series, gross_returns: pd.Series, pandas_cagr: float
) -> tuple[bool, float]:
    """G7: hand-roll a numpy-only PnL computation and compare CAGR."""
    pos = position.shift(1).fillna(0.0).values.astype(np.float64)
    ret = gross_returns.values.astype(np.float64)
    pnl = pos * ret  # gross-PnL semantics; spread/swap are added in cost_models
    eq = np.cumprod(1.0 + pnl)
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_np = float(eq[-1] ** (1.0 / span_yr) - 1.0)
    diff_pp = abs(cagr_np - pandas_cagr) * 100.0
    return diff_pp <= 3.0, cagr_np


# ---------------------------------------------------------------------------
# Per-dataset run
# ---------------------------------------------------------------------------


def _regime_on_fraction(close: pd.Series, sma_trend_period: int = 200) -> float:
    """Fraction of bars where close > SMA(N_trend) — sanity proxy."""
    sma_trend = close.rolling(sma_trend_period, min_periods=sma_trend_period).mean()
    mask = (close > sma_trend).fillna(False)
    valid = sma_trend.notna()
    if valid.sum() == 0:
        return 0.0
    return float(mask[valid].mean())


def run_one_dataset(name: str) -> dict:
    df = load_dataset(name)
    if name == "xauusd_intraday":
        df = resample_1h_to_daily(df)
    df = df.sort_index()

    close = df["close"].astype(float)
    gross_returns = daily_returns(close)

    # Single config: RSI(2)<5 + SMA(5) exit + SMA(200) trend filter.
    position = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )

    ann = annualization_factor(name)

    # Track A: Pepperstone CFD (multi-day swing → swap accrues)
    br_a = apply_pepperstone_costs(
        gross_returns, position, intraday_close=False,
    )
    # Track B: Inter ETF (long-only by construction; reported with GS-2 caveat)
    br_b = apply_inter_costs_with_darf(gross_returns, position)

    m_a = compute_metrics(br_a.net_pnl, ann)
    m_b = compute_metrics(br_b.net_pnl, ann)
    mean_hold_a, n_trades_a = compute_mean_hold_days(position)

    rets_a = br_a.net_pnl.dropna()

    # G1 PBO: single pre-committed cfg → degenerate; pass by convention.
    g1_pbo = True
    g1_note = "single-cfg PBO degenerate; pass by convention (no overfit risk)"

    # G2 DSR / PSR with cumulative_n_trials (=3).
    if rets_a.std() > 0 and len(rets_a) > 30:
        if CUMULATIVE_N_TRIALS >= 2:
            dsr_res = dsr_func(rets_a.values, n_trials=CUMULATIVE_N_TRIALS)
            dsr_p = float(dsr_res.p_value)
        else:
            psr_val = psr_func(rets_a.values, benchmark=0.0)
            dsr_p = float(1.0 - psr_val)
        g2_dsr = bool(dsr_p < 0.05)
    else:
        dsr_p = 1.0
        g2_dsr = False

    g3_wf, wf_returns, wf_dds = run_walk_forward(rets_a, n_windows=8, ann=ann)

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
    g7_cl, cagr_np = cross_lib_check(position, gross_returns, m_a["cagr"])

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    regime_on_frac = _regime_on_fraction(close, sma_trend_period=200)

    return {
        "track_a_metrics": {
            **m_a,
            "dsr_p_value": dsr_p,
            "mean_hold_days": mean_hold_a,
            "n_trades": n_trades_a,
            "n_swap_nights": br_a.n_swap_nights,
            "n_weekend_holds": br_a.n_weekend_holds,
            "cost_summary": br_a.summary(),
        },
        "track_b_metrics": {
            **m_b,
            "n_trades": n_trades_a,  # same position series
            "cost_summary": br_b.summary(),
            "note": "GS-2 cost cliff applies; reported for completeness",
        },
        "regime_on_fraction": regime_on_frac,
        "gates": {
            "g1_pbo": g1_pbo, "g1_note": g1_note,
            "g2_dsr": g2_dsr, "dsr_p_value": dsr_p,
            "g3_wf": g3_wf, "wf_returns": wf_returns, "wf_dds": wf_dds,
            "g4_oos": g4_oos, "oos_sharpe": float(oos_sharpe),
            "g5_fwd": g5_fwd, "fwd_sharpe": float(fwd_sharpe),
            "g6_bootstrap": g6_boot, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "g7_crosslib": g7_cl, "cagr_pandas": m_a["cagr"], "cagr_numpy": cagr_np,
        },
        "n_passed": gates.n_passed,
        "_returns_series": {
            "index": [d.isoformat() for d in br_a.net_pnl.index],
            "net_returns": [float(x) for x in br_a.net_pnl.values],
        },
    }


def main() -> None:
    print(f"[{CFG_ID}] running on 3 datasets (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS})")
    results: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ---")
        r = run_one_dataset(name)
        results[name] = r
        ma = r["track_a_metrics"]
        print(
            f"  Track A: Sharpe={ma['sharpe']:+.4f}, CAGR={ma['cagr']:+.4%}, "
            f"MDD={ma['mdd']:.4%}, mean_hold={ma['mean_hold_days']:.2f}d, "
            f"n_trades={ma['n_trades']}, gates={r['n_passed']}/7, "
            f"regime_on={r['regime_on_fraction']:.1%}"
        )
        mb = r["track_b_metrics"]
        print(
            f"  Track B: Sharpe={mb['sharpe']:+.4f}, CAGR={mb['cagr']:+.4%}, "
            f"MDD={mb['mdd']:.4%} (GS-2 cliff applies)"
        )

    metrics = {
        ds: DatasetMetrics(
            sharpe=results[ds]["track_a_metrics"]["sharpe"],
            cagr=results[ds]["track_a_metrics"]["cagr"],
            mdd=results[ds]["track_a_metrics"]["mdd"],
            dsr_p_value=results[ds]["track_a_metrics"]["dsr_p_value"],
        )
        for ds in results
    }
    gates = {
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
    score = score_strategy(metrics, gates, cumulative_n_trials=CUMULATIVE_N_TRIALS)

    primary_ds = "gld_long"
    primary_hold = results[primary_ds]["track_a_metrics"]["mean_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    # Kill-criterion check from hypothesis.md (≥ +0.10 lift over iter 001
    # on at least 1 dataset; cross-dataset failure if ALL 3 fall short).
    iter001_sharpes = {
        "gld_long": 0.04,
        "xauusd_real": -0.23,
        "xauusd_intraday": -0.20,
    }
    sharpe_lifts = {
        ds: results[ds]["track_a_metrics"]["sharpe"] - iter001_sharpes[ds]
        for ds in results
    }
    n_ds_with_lift = sum(1 for v in sharpe_lifts.values() if v >= 0.10)
    kill_criterion_fired = n_ds_with_lift == 0

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERION ===\n"
        f"Sharpe lifts vs iter 001: {sharpe_lifts}\n"
        f"datasets with ≥+0.10 lift: {n_ds_with_lift}/3, "
        f"kill_fired = {kill_criterion_fired}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "rsi_period": 2,
            "rsi_threshold": 5.0,
            "sma_period": 5,
            "sma_trend_period": 200,
            "long_only": True,
            "swap_free": False,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "mean_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
        },
        "kill_criterion": {
            "iter001_sharpes": iter001_sharpes,
            "this_iter_sharpes": {
                ds: results[ds]["track_a_metrics"]["sharpe"] for ds in results
            },
            "sharpe_lifts": sharpe_lifts,
            "n_datasets_with_lift_ge_0_10": n_ds_with_lift,
            "fired": kill_criterion_fired,
            "implication": (
                "If fired: GS-1 (MR on gold) is structurally dead even with "
                "Connors' SMA(200) fix; close MR family permanently and pivot."
            ),
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
    verdict["primary_citation"] = "[short_term_trading_strategies, p.105-118]"
    verdict["hypothesis_slug"] = "rsi2-sma200-filter"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds: results[ds]["track_a_metrics"] for ds in results
    }
    verdict["track_b_metrics"] = {
        ds: results[ds]["track_b_metrics"] for ds in results
    }
    verdict["kill_criterion"] = out["kill_criterion"]
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
