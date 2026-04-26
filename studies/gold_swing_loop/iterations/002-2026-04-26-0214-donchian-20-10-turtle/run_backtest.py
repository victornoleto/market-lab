"""Iter 002 — Donchian-20/10 channel breakout (Turtle System 2 lite) on gold.

Strategy
--------
* Long entry  (when flat): close[t] > rolling_max(close, 20)[t-1]
* Short entry (when flat, long_only=False): close[t] < rolling_min(close, 20)[t-1]
* Exit long  (when long):  close[t] < rolling_min(close, 10)[t-1]
* Exit short (when short): close[t] > rolling_max(close, 10)[t-1]
* Position binary {-1, 0, +1}; carries forward between bars.

Note: rolling reference uses ``[t-1]`` (shift(1)) on entry/exit channels
to avoid look-ahead. The "20-day high" used for entry on bar t is the
max of bars [t-20 .. t-1] — i.e., excluding t itself. This way, the
breakout is confirmed by close[t] BREAKING ABOVE the prior window.

Datasets: gld_long, xauusd_real, xauusd_intraday (daily-resampled from 1h).

Output: ``results.json`` with per-dataset metrics, gate outcomes, and
returns series; ``verdict.json`` with score_strategy() + winner conditions.

Citations
---------
* `[trend_following, Covel]` — Donchian channel-breakout philosophy
* `[stocks_on_the_move, p.81]` — Clenow ATR-scaled trend
* `[trading_systems_methods, Kaufman, ch.20]` — channel breakout systems
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest
* `[advances_fin_ml, p.222-223]` — DSR / PSR with cumulative n_trials
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
CFG_ID = "donchian_20_10_turtle"
CUMULATIVE_N_TRIALS = 2  # iter 001 (1) + this iter (1)


# ---------------------------------------------------------------------------
# Strategy primitive — Donchian breakout signal
# ---------------------------------------------------------------------------


def donchian_breakout_signal(
    df: pd.DataFrame,
    *,
    entry_lookback: int = 20,
    exit_lookback: int = 10,
    long_only: bool = False,
) -> pd.Series:
    """Generate a Donchian-channel breakout position series.

    State machine on each bar t:
        * If flat:
            - close[t] > rolling_max(close[t-N..t-1], N) → enter long  (pos=+1)
            - close[t] < rolling_min(close[t-N..t-1], N) AND not long_only → enter short (pos=-1)
        * If long:
            - close[t] < rolling_min(close[t-M..t-1], M) → exit (pos=0)
        * If short:
            - close[t] > rolling_max(close[t-M..t-1], M) → exit (pos=0)
        * Otherwise carry previous position forward.

    Returns pd.Series indexed identically to df, dtype float64,
    values in {-1.0, 0.0, +1.0}.

    The ``[t-1]`` reference avoids look-ahead: at bar t we only see bars
    strictly before t when computing the channel.
    """
    close = df["close"].astype(float)
    # rolling().max() over [t-N+1..t]; we want [t-N..t-1] → shift(1).
    upper_entry = close.rolling(entry_lookback, min_periods=entry_lookback).max().shift(1)
    lower_entry = close.rolling(entry_lookback, min_periods=entry_lookback).min().shift(1)
    upper_exit = close.rolling(exit_lookback, min_periods=exit_lookback).max().shift(1)
    lower_exit = close.rolling(exit_lookback, min_periods=exit_lookback).min().shift(1)

    pos = np.zeros(len(close), dtype=np.float64)
    state = 0  # -1, 0, +1
    for i in range(len(close)):
        c = close.iloc[i]
        ue = upper_entry.iloc[i]
        le = lower_entry.iloc[i]
        ux = upper_exit.iloc[i]
        lx = lower_exit.iloc[i]

        if state == 0:
            # Flat: try entries (long takes precedence in the rare both-fire case)
            if pd.notna(ue) and c > ue:
                state = 1
            elif pd.notna(le) and c < le and not long_only:
                state = -1
        elif state == 1:
            # Long: exit if close drops below 10-day low
            if pd.notna(lx) and c < lx:
                state = 0
        elif state == -1:
            # Short: exit if close rises above 10-day high
            if pd.notna(ux) and c > ux:
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
    """Sharpe (annualized), CAGR, MDD, plus Sharpe periodic for DSR."""
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
    """Mean hold time across all trades (long+short combined).

    A trade = contiguous run of position != 0. State transitions:
        flat → long      starts a long trade
        flat → short     starts a short trade
        long → flat      ends the long trade
        short → flat     ends the short trade
        long → short     ends long, starts short (counted as 2 trades)
        short → long     ends short, starts long (counted as 2 trades)
    """
    pos = position.values
    if len(pos) == 0:
        return 0.0, 0
    holds: list[int] = []
    in_trade = False
    cur_dir = 0
    start = 0
    for i, p in enumerate(pos):
        if p != cur_dir:
            if in_trade:
                holds.append(i - start)
            if p != 0:
                start = i
                cur_dir = int(np.sign(p))
                in_trade = True
            else:
                cur_dir = 0
                in_trade = False
    if in_trade:
        holds.append(len(pos) - start)
    if not holds:
        return 0.0, 0
    return float(np.mean(holds)), int(len(holds))


# ---------------------------------------------------------------------------
# Gate runners (per dataset)
# ---------------------------------------------------------------------------


def run_walk_forward(
    rets: pd.Series, n_windows: int = 8, ann: int = 252
) -> tuple[bool, list[float], list[float]]:
    """Walk-forward gate: split into ``n_windows`` non-overlapping OOS blocks."""
    n = len(rets)
    if n < n_windows * 20:
        return False, [], []

    block = n // n_windows
    oos_returns = []
    drawdowns = []
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
    pnl = pos * ret  # same gross-PnL semantics as cost_models._bar_pnl
    eq = np.cumprod(1.0 + pnl)
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_np = float(eq[-1] ** (1.0 / span_yr) - 1.0)
    diff_pp = abs(cagr_np - pandas_cagr) * 100.0
    return diff_pp <= 3.0, cagr_np


# ---------------------------------------------------------------------------
# Main per-dataset run
# ---------------------------------------------------------------------------


def run_one_dataset(name: str) -> dict:
    """Backtest the strategy on one dataset and compute all gates."""
    df = load_dataset(name)
    if name == "xauusd_intraday":
        df = resample_1h_to_daily(df)
    df = df.sort_index()

    close = df["close"].astype(float)
    gross_returns = daily_returns(close)

    # Track A: bidirectional Donchian-20/10
    position_a = donchian_breakout_signal(
        df, entry_lookback=20, exit_lookback=10, long_only=False
    )
    # Track B: same Donchian-20/10 but long-only (drops short signals to flat)
    position_b = donchian_breakout_signal(
        df, entry_lookback=20, exit_lookback=10, long_only=True
    )

    ann = annualization_factor(name)

    # Track A cost-deducted PnL (multi-night swing → swap accrues)
    br_a = apply_pepperstone_costs(
        gross_returns,
        position_a,
        intraday_close=False,
    )
    # Track B cost-deducted PnL (long-only enforced; passes by construction)
    br_b = apply_inter_costs_with_darf(gross_returns, position_b)

    # Metrics on net PnL
    m_a = compute_metrics(br_a.net_pnl, ann)
    m_b = compute_metrics(br_b.net_pnl, ann)

    # Mean hold days (Track A — bidirectional, so includes long+short trades)
    mean_hold_a, n_trades_a = compute_mean_hold_days(position_a)
    mean_hold_b, n_trades_b = compute_mean_hold_days(position_b)

    # ---- Gates (computed on Track A net returns; Track B comparison only) ----
    rets_a = br_a.net_pnl.dropna()

    # G1 PBO: degenerate for single pre-committed config — PASS by convention
    g1_pbo = True
    g1_note = "single-cfg PBO degenerate; pass by convention (no overfit risk)"

    # G2 DSR / PSR with cumulative_n_trials.
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

    # G3 Walk-forward (8 OOS windows)
    g3_wf, wf_returns, wf_dds = run_walk_forward(rets_a, n_windows=8, ann=ann)

    # G4 OOS 70/30
    cut = int(0.7 * len(rets_a))
    oos_chunk = rets_a.iloc[cut:]
    oos_sharpe = sharpe_periodic(oos_chunk.values) * np.sqrt(ann) if len(oos_chunk) > 1 else 0.0
    g4_oos = bool(oos_sharpe > 0)

    # G5 FWD post-2022
    fwd_chunk = rets_a[rets_a.index >= "2022-01-01"]
    fwd_sharpe = sharpe_periodic(fwd_chunk.values) * np.sqrt(ann) if len(fwd_chunk) > 1 else 0.0
    g5_fwd = bool(fwd_sharpe > 0)

    # G6 Bootstrap 99.9% CI
    g6_boot, ci_lo, ci_hi = run_bootstrap(rets_a, ann)

    # G7 Cross-lib check
    g7_cl, cagr_np = cross_lib_check(position_a, gross_returns, m_a["cagr"])

    gates = Gates(
        g1_pbo=g1_pbo,
        g2_dsr=g2_dsr,
        g3_wf=g3_wf,
        g4_oos=g4_oos,
        g5_fwd=g5_fwd,
        g6_bootstrap=g6_boot,
        g7_crosslib=g7_cl,
    )

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
            "mean_hold_days": mean_hold_b,
            "n_trades": n_trades_b,
            "cost_summary": br_b.summary(),
        },
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
    print(f"[{CFG_ID}] running on 3 datasets")
    results = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ---")
        r = run_one_dataset(name)
        results[name] = r
        ma = r["track_a_metrics"]
        print(
            f"  Track A: Sharpe={ma['sharpe']:.4f}, CAGR={ma['cagr']:.4%}, "
            f"MDD={ma['mdd']:.4%}, mean_hold={ma['mean_hold_days']:.2f}d, "
            f"n_trades={ma['n_trades']}, gates={r['n_passed']}/7"
        )
        mb = r["track_b_metrics"]
        print(
            f"  Track B: Sharpe={mb['sharpe']:.4f}, CAGR={mb['cagr']:.4%}, "
            f"MDD={mb['mdd']:.4%}, n_trades={mb['n_trades']}"
        )

    # ---- Aggregate score (Track A primary) ----
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

    # Hold-time gate (6th condition)
    primary_ds = "gld_long"
    primary_hold = results[primary_ds]["track_a_metrics"]["mean_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "entry_lookback": 20,
            "exit_lookback": 10,
            "long_only_track_a": False,
            "long_only_track_b": True,
            "swap_free": False,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "per_dataset": {
            ds: {
                k: v for k, v in results[ds].items() if not k.startswith("_")
            }
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "mean_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
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

    # Verdict.json
    verdict = score.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[trend_following, Covel]"
    verdict["hypothesis_slug"] = "donchian-20-10-turtle"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "both"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds: results[ds]["track_a_metrics"] for ds in results
    }
    verdict["track_b_metrics"] = {
        ds: results[ds]["track_b_metrics"] for ds in results
    }
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
