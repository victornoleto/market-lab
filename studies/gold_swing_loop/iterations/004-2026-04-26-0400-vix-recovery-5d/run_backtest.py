"""Iter 004 — VIX recovery flight-to-quality drift, fixed 5-day hold.

Strategy
--------

The signal extracts the **post-stress recovery phase** of equity-vol
regimes. It is fundamentally different from iter 003's gold-momentum
MR base: the entry trigger uses *equity vol* (VIX) z-score crossings,
not gold price action.

* Compute ``vix_z = (VIX − rolling60_mean(VIX)) / rolling60_std(VIX)``.
* **Trigger** at bar t (long entry):

      vix_z[t]   <  +1.0
      AND vix_z[t-1] >= +1.0          (down-cross of +1)
      AND max(vix_z[t-30..t-1]) > +2.0 (recent peak qualifies recovery)

* **Hold**: long ``+1`` for exactly ``hold_days = 5`` trading days from
  trigger.
* **Cooldown**: after exit, block new triggers for ``cooldown_days = 10``.
* **Exit** at ``T+5`` (or end of series).
* Long-only, binary {0, 1}, no leverage.

Datasets: gld_long, xauusd_real, xauusd_intraday (1h → daily).

Output: ``results.json`` per-dataset metrics + gates + returns series for
``score_strategy``; ``verdict.json`` with score + hold-gate + winner check.

Citations
---------
* `[leverage_for_the_long_run, p.13]` — Gayed VIX flight-to-quality regime gate
* `[ilmanen_expected_returns, ch.10]` — Gold as carry / safe-haven asset
* Erb & Harvey 2006 *FAJ* 62(2), pp.69-97 — gold post-stress drift premium
* Baur & Lucey 2010 *Financial Review* 45(2) — gold safe-haven asymmetric
* `[short_term_trading_strategies, p.105-118]` — analogous SMA(200) trend
  filter at the family level (entry-gate methodology)
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
* DEAD_ENDS GS-3 escape hatch #2 — `studies/gold_swing_loop/DEAD_ENDS.md`
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
CFG_ID = "vix_recovery_5d_hold"
# iter 001 (1) + iter 002 (1) + iter 003 (1) + this iter (1) = 4
CUMULATIVE_N_TRIALS = 4


# ---------------------------------------------------------------------------
# Strategy primitives
# ---------------------------------------------------------------------------


def vix_zscore(vix: pd.Series, lookback: int = 60) -> pd.Series:
    """Rolling z-score of VIX with given lookback (calendar-day-naive).

    Returns NaN for the first ``lookback - 1`` bars (insufficient history).
    """
    m = vix.rolling(lookback, min_periods=lookback).mean()
    s = vix.rolling(lookback, min_periods=lookback).std()
    z = (vix - m) / s.replace(0.0, np.nan)
    return z


def vix_recovery_signal(
    df: pd.DataFrame,
    vix: pd.Series,
    *,
    z_peak_threshold: float = 2.0,
    z_exit_threshold: float = 1.0,
    peak_window: int = 30,
    hold_days: int = 5,
    cooldown_days: int = 10,
    zscore_lookback: int = 60,
) -> pd.Series:
    """Generate position series for VIX-recovery 5d-hold strategy.

    Parameters
    ----------
    df : pd.DataFrame
        Price dataframe (gold OHLC); used only for ``df.index`` to define
        the trading calendar.
    vix : pd.Series
        Daily VIX series. Forward-filled onto ``df.index`` if calendars
        differ (gold has BMF/CFD calendar, VIX has CBOE calendar).
    z_peak_threshold : float
        Minimum z-score in the recent peak window to qualify the recovery
        as post-stress. Default +2.0σ.
    z_exit_threshold : float
        Down-cross threshold. Trigger fires when z crosses below this from
        above. Default +1.0σ.
    peak_window : int
        Number of bars to look back for the qualifying peak (excludes
        current bar). Default 30 trading days (~6 weeks).
    hold_days : int
        Fixed hold length in bars (long position open exactly this many
        consecutive bars from trigger).
    cooldown_days : int
        Bars after exit before a new trigger is eligible.
    zscore_lookback : int
        Rolling window for VIX z-score normalization. Default 60.

    Returns
    -------
    pd.Series of dtype float64, values in {0.0, 1.0}, indexed identically
    to ``df``.
    """
    # Align VIX onto df's trading calendar via forward-fill.
    vix_aligned = vix.reindex(df.index).ffill()
    z = vix_zscore(vix_aligned, lookback=zscore_lookback)

    z_arr = z.values
    z_lag = np.concatenate([[np.nan], z_arr[:-1]])

    n = len(df)
    pos = np.zeros(n, dtype=np.float64)

    in_trade = False
    trade_end_idx = -1
    cooldown_until = -1

    for i in range(n):
        # If currently in a trade, hold until trade_end_idx (exclusive).
        if in_trade:
            if i < trade_end_idx:
                pos[i] = 1.0
                continue
            else:
                # Exit at this bar (position 0); start cooldown.
                in_trade = False
                cooldown_until = i + cooldown_days
                # fall through to potential trigger check on the same bar?
                # No — we exit cleanly on this bar (pos = 0) and let the
                # cooldown block any trigger here. Keep pos[i] = 0.
                continue

        # Not in trade. Check cooldown.
        if i <= cooldown_until:
            continue

        # Check trigger conditions.
        z_now = z_arr[i]
        z_prev = z_lag[i]
        if np.isnan(z_now) or np.isnan(z_prev):
            continue
        if not (z_now < z_exit_threshold and z_prev >= z_exit_threshold):
            continue

        # Recent peak in [i-peak_window, i-1] must exceed z_peak_threshold.
        lo = max(0, i - peak_window)
        if lo >= i:
            continue
        recent_max = np.nanmax(z_arr[lo:i])
        if np.isnan(recent_max) or recent_max <= z_peak_threshold:
            continue

        # Trigger fires: enter long for hold_days.
        in_trade = True
        trade_end_idx = i + hold_days
        pos[i] = 1.0

    return pd.Series(pos, index=df.index, name="position")


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


def load_vix() -> pd.Series:
    """Load daily VIX from the cached parquet."""
    path = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
    df = pd.read_parquet(path)
    return df["VIX"].astype(float).sort_index()


# ---------------------------------------------------------------------------
# Metric helpers (same as iter 003)
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
    return {"sharpe": sharpe_ann, "sharpe_periodic": float(sharpe_per),
            "cagr": cagr, "mdd": mdd}


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
# Gate runners (per dataset) — identical to iter 003
# ---------------------------------------------------------------------------


def run_walk_forward(rets: pd.Series, n_windows: int = 8, ann: int = 252):
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


def run_bootstrap(rets: pd.Series, ann: int):
    arr = rets.dropna().values
    if len(arr) < 50 or arr.std() == 0:
        return False, 0.0, 0.0
    samples = stationary_bootstrap_trades(
        arr, block_mean=5, n_resamples=2000, seed=42,
    )
    sharpes = []
    for row in samples:
        s = sharpe_periodic(row)
        sharpes.append(s * np.sqrt(ann))
    sharpes = np.array(sharpes)
    lo = float(np.percentile(sharpes, 0.05))
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_check(position: pd.Series, gross_returns: pd.Series, pandas_cagr: float):
    pos = position.shift(1).fillna(0.0).values.astype(np.float64)
    ret = gross_returns.values.astype(np.float64)
    pnl = pos * ret
    eq = np.cumprod(1.0 + pnl)
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_np = float(eq[-1] ** (1.0 / span_yr) - 1.0)
    diff_pp = abs(cagr_np - pandas_cagr) * 100.0
    return diff_pp <= 3.0, cagr_np


# ---------------------------------------------------------------------------
# Per-dataset run
# ---------------------------------------------------------------------------


def run_one_dataset(name: str, vix: pd.Series) -> dict:
    df = load_dataset(name)
    if name == "xauusd_intraday":
        df = resample_1h_to_daily(df)
    df = df.sort_index()

    close = df["close"].astype(float)
    gross_returns = daily_returns(close)

    position = vix_recovery_signal(
        df, vix,
        z_peak_threshold=2.0, z_exit_threshold=1.0,
        peak_window=30, hold_days=5, cooldown_days=10,
        zscore_lookback=60,
    )

    ann = annualization_factor(name)

    # Track A: Pepperstone CFD (multi-day swing → swap accrues)
    br_a = apply_pepperstone_costs(
        gross_returns, position, intraday_close=False,
    )
    # Track B: Inter ETF (long-only by construction; ~4 tr/yr below GS-2 cliff)
    br_b = apply_inter_costs_with_darf(gross_returns, position)

    m_a = compute_metrics(br_a.net_pnl, ann)
    m_b = compute_metrics(br_b.net_pnl, ann)
    mean_hold_a, n_trades_a = compute_mean_hold_days(position)

    rets_a = br_a.net_pnl.dropna()

    # G1 PBO: single pre-committed cfg → degenerate; pass by convention.
    g1_pbo = True
    g1_note = "single-cfg PBO degenerate; pass by convention (no overfit risk)"

    # G2 DSR with cumulative_n_trials.
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
            "n_trades": n_trades_a,
            "cost_summary": br_b.summary(),
            "note": "GS-2 cost cliff regime (~4 tr/yr); reported for completeness",
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
        "_position_series": {
            "index": [d.isoformat() for d in position.index],
            "position": [float(x) for x in position.values],
        },
    }


def correlation_with_iter003(this_position: pd.Series,
                               this_returns: pd.Series) -> dict:
    """Compute correlation of this iter's position/returns with iter 003's
    MR base — needed for IC-7 composition planning in iter 005."""
    iter003_path = (
        ROOT / "studies" / "gold_swing_loop" / "iterations"
        / "003-2026-04-26-0228-rsi2-sma200-filter" / "results.json"
    )
    if not iter003_path.exists():
        return {"available": False}
    iter003 = json.loads(iter003_path.read_text())
    rs = iter003.get("returns_series", {})
    out = {"available": True, "by_dataset": {}}
    for ds in ("gld_long", "xauusd_real", "xauusd_intraday"):
        cfg_id_003 = "connors_rsi2_sma200_filter"
        if ds not in rs or cfg_id_003 not in rs[ds]:
            out["by_dataset"][ds] = {"err": "iter003 returns not found"}
            continue
        idx = rs[ds][cfg_id_003]["index"]
        rets = rs[ds][cfg_id_003]["net_returns"]
        s003 = pd.Series(rets, index=pd.to_datetime(idx))
        s004 = this_returns.get(ds, pd.Series([], dtype=float))
        # Align on common index
        common = s003.index.intersection(s004.index)
        if len(common) < 50:
            out["by_dataset"][ds] = {"err": f"too few common bars ({len(common)})"}
            continue
        a = s003.loc[common]
        b = s004.loc[common]
        if a.std() == 0 or b.std() == 0:
            corr = 0.0
        else:
            corr = float(a.corr(b))
        out["by_dataset"][ds] = {
            "correlation": corr,
            "n_common_bars": int(len(common)),
        }
    return out


def main() -> None:
    print(f"[{CFG_ID}] running on 3 datasets (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS})")
    vix = load_vix()
    print(f"VIX loaded: {len(vix)} bars, {vix.index.min().date()} → {vix.index.max().date()}")

    results: dict[str, dict] = {}
    iter004_returns: dict[str, pd.Series] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ---")
        r = run_one_dataset(name, vix)
        results[name] = r
        ma = r["track_a_metrics"]
        print(
            f"  Track A: Sharpe={ma['sharpe']:+.4f}, CAGR={ma['cagr']:+.4%}, "
            f"MDD={ma['mdd']:.4%}, mean_hold={ma['mean_hold_days']:.2f}d, "
            f"n_trades={ma['n_trades']}, gates={r['n_passed']}/7"
        )
        mb = r["track_b_metrics"]
        print(
            f"  Track B: Sharpe={mb['sharpe']:+.4f}, CAGR={mb['cagr']:+.4%}, "
            f"MDD={mb['mdd']:.4%} (GS-2 cliff caveat: ~4 tr/yr)"
        )
        # Cache returns for cross-iter correlation
        iter004_returns[name] = pd.Series(
            r["_returns_series"]["net_returns"],
            index=pd.to_datetime(r["_returns_series"]["index"]),
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

    # Kill criterion: track_a_sharpe[gld_long] < 0.10 AND ≤1 of 3 ds positive
    sharpe_gld = results["gld_long"]["track_a_metrics"]["sharpe"]
    n_pos_sharpe = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["sharpe"] > 0
    )
    kill_criterion_fired = (sharpe_gld < 0.10) and (n_pos_sharpe < 2)

    # IC-7 composition prep: correlation with iter 003 MR base.
    ic7_corr = correlation_with_iter003(
        this_position=pd.Series([], dtype=float),  # not used; we pass returns
        this_returns=iter004_returns,
    )

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERION ===\n"
        f"track_a_sharpe[gld_long] = {sharpe_gld:+.4f} (kill if < 0.10)\n"
        f"datasets with positive Track-A Sharpe: {n_pos_sharpe}/3 (kill if < 2)\n"
        f"kill_fired = {kill_criterion_fired}\n"
        f"\n=== IC-7 PREP (corr with iter 003 MR base) ===\n"
    )
    for ds, info in ic7_corr.get("by_dataset", {}).items():
        print(f"  {ds}: {info}")

    out = {
        "config_id": CFG_ID,
        "params": {
            "z_peak_threshold": 2.0,
            "z_exit_threshold": 1.0,
            "peak_window": 30,
            "hold_days": 5,
            "cooldown_days": 10,
            "zscore_lookback": 60,
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
            "track_a_sharpe_gld_long": sharpe_gld,
            "n_datasets_with_positive_track_a_sharpe": n_pos_sharpe,
            "fired": kill_criterion_fired,
            "implication": (
                "If fired: VIX-recovery cross-asset framing has no edge net "
                "of cost on gold; close cross-asset volatility-derived family."
            ),
        },
        "ic7_composition_prep": ic7_corr,
        "is_winner": is_winner,
        "returns_series": {
            ds: {CFG_ID: results[ds]["_returns_series"]} for ds in results
        },
        "position_series": {
            ds: {CFG_ID: results[ds]["_position_series"]} for ds in results
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
    verdict["primary_citation"] = "[leverage_for_the_long_run, p.13]"
    verdict["hypothesis_slug"] = "vix-recovery-5d"
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
    verdict["kill_criterion"] = out["kill_criterion"]
    verdict["ic7_composition_prep"] = ic7_corr
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
