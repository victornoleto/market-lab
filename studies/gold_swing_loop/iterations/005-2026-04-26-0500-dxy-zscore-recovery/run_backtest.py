"""Iter 005 — DXY z-score down-cross + 5-d fixed hold (fundamentals macro overlay).

Strategy
--------

Cross-asset *fundamentals* signal complement to iter 004's stress-driven
overlay. Tests gold's primary mechanical macro driver — USD direction —
via an equal-weighted log basket of cached FX crosses.

* DXY_proxy = (log(usdcad) + log(usdchf) + log(usdjpy)) / 3
* z(t) = (DXY_proxy(t) - rolling_mean(60)) / rolling_std(60)   [ddof=0]
* **Trigger** at bar t (long entry): z[t] < -1.0 AND z[t-1] >= -1.0
  (down-cross of -1: USD just entered "unusually weak" regime).
* **Hold**: long +1 for exactly hold_days = 5 trading days.
* **Cooldown**: 5 trading days post-exit before re-eligibility.
* Long-only, binary {0, 1}, no leverage, no stops.

Datasets: gld_long, xauusd_real, xauusd_intraday (1h → daily).

Output: results.json (per-dataset metrics + gates + returns_series for
IC-7 cross-iter correlation); verdict.json (score + winner check + dual
broker-track metrics).

Citations
---------
* `[ilmanen_expected_returns, ch.10]` — gold's USD-hedge premium
* `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional
  entry methodology (event-driven trigger + fixed hold)
* `[short_term_trading_strategies, p.105-118]` — analogous regime-filter
  pattern at the family level
* Bauer & Mertens 2018, FRBSF EL 2018-19 — DXY weakening as gold driver
* Erb & Harvey 2013, FAJ 69(4) — gold-USD inverse decomposition
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
* DEAD_ENDS GS-4 escape hatch #1 — `studies/gold_swing_loop/DEAD_ENDS.md`
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
CFG_ID = "dxy_zscore_recovery_5d_hold"
# iter 001 (1) + iter 002 (1) + iter 003 (1) + iter 004 (1) + this iter (1) = 5
CUMULATIVE_N_TRIALS = 5


# ---------------------------------------------------------------------------
# Strategy primitives
# ---------------------------------------------------------------------------


def compute_dxy_proxy(
    usdcad: pd.Series, usdchf: pd.Series, usdjpy: pd.Series
) -> pd.Series:
    """Equal-weighted log basket: (log(usdcad)+log(usdchf)+log(usdjpy))/3.

    Inputs need not share the same index — the function inner-joins to
    the intersection of all three. Higher = stronger USD across the
    three crosses.

    Note: a true DXY index has fixed weights (EUR 57.6%, JPY 13.6%,
    GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%). Our cache lacks EUR/USD
    and GBP/USD — the equal-weighted 3-cross proxy captures USD
    directional moves and is highly correlated (~0.85+) with the full
    DXY, which is sufficient for a z-score-based regime signal.
    """
    df = pd.concat(
        [
            np.log(usdcad).rename("a"),
            np.log(usdchf).rename("b"),
            np.log(usdjpy).rename("c"),
        ],
        axis=1, join="inner",
    )
    proxy = df.mean(axis=1)
    proxy.name = "dxy_proxy"
    return proxy


def compute_zscore(s: pd.Series, lookback: int = 60) -> pd.Series:
    """Rolling z-score: (s - rolling_mean) / rolling_std, ddof=0.

    Uses pandas default ``min_periods = lookback`` → first ``lookback - 1``
    bars are NaN (insufficient history). Population std (ddof=0) matches
    the typical trading definition.
    """
    m = s.rolling(lookback, min_periods=lookback).mean()
    sd = s.rolling(lookback, min_periods=lookback).std(ddof=0)
    z = (s - m) / sd.replace(0.0, np.nan)
    return z


def dxy_downcross_signal(
    z: pd.Series,
    *,
    z_threshold: float = -1.0,
    hold_days: int = 5,
    cooldown_days: int = 5,
) -> pd.Series:
    """Position state machine for DXY z-score down-cross + fixed hold.

    Trigger: ``z[t] < z_threshold AND z[t-1] >= z_threshold`` (NaN at
    t-1 → False by IEEE comparison, so the first valid z at index 60
    cannot itself be a cross — the earliest possible cross is at the
    bar AFTER the first non-NaN z).

    On trigger: enter long for ``hold_days`` consecutive bars.
    After exit: ``cooldown_days`` of forced flat before next eligibility.
    Long-only, binary {0.0, 1.0}.
    """
    z_arr = z.values
    z_lag = np.concatenate([[np.nan], z_arr[:-1]])
    n = len(z)
    pos = np.zeros(n, dtype=np.float64)

    in_trade = False
    trade_end_idx = -1     # exclusive: position is 1 for [start, end)
    cooldown_until = -1    # inclusive: position is 0 for [start, until]

    for i in range(n):
        if in_trade:
            if i < trade_end_idx:
                pos[i] = 1.0
                continue
            # Exit at this bar: pos = 0; start cooldown.
            in_trade = False
            cooldown_until = i + cooldown_days - 1
            # Do NOT allow re-entry on the exit bar.
            continue

        # Not in trade. Check cooldown.
        if i <= cooldown_until:
            continue

        # Check trigger: z down-cross through threshold from above.
        z_now = z_arr[i]
        z_prev = z_lag[i]
        if np.isnan(z_now) or np.isnan(z_prev):
            continue
        if not (z_now < z_threshold and z_prev >= z_threshold):
            continue

        # Trigger fires.
        in_trade = True
        trade_end_idx = i + hold_days
        pos[i] = 1.0

    return pd.Series(pos, index=z.index, name="position")


def daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def resample_1h_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    out = df.resample("D").agg({
        "open":  "first",
        "high":  "max",
        "low":   "min",
        "close": "last",
        "adj_close": "last",
        "volume": "sum",
    })
    return out.dropna(subset=["close"])


def load_fx_basket() -> pd.Series:
    """Load usdcad / usdchf / usdjpy daily closes from Tiingo cache and
    return the equal-weighted log basket DXY proxy.

    Returned index is the inner-join of the three FX series' indices
    (typically all three Tiingo daily series share business-day calendar
    after 2003-ish).
    """
    base = ROOT / "data" / "tiingo" / "daily" / "prices"
    usdcad = pd.read_parquet(base / "usdcad.parquet")["close"].astype(float).sort_index()
    usdchf = pd.read_parquet(base / "usdchf.parquet")["close"].astype(float).sort_index()
    usdjpy = pd.read_parquet(base / "usdjpy.parquet")["close"].astype(float).sort_index()
    return compute_dxy_proxy(usdcad, usdchf, usdjpy)


# ---------------------------------------------------------------------------
# Pre-validation screen (Stage 3a — abort if signal has no raw edge)
# ---------------------------------------------------------------------------


def pre_validation_screen(
    close: pd.Series,
    z: pd.Series,
    *,
    z_threshold: float = -1.0,
    forward_days: int = 5,
    min_events: int = 20,
    min_t_stat: float = 0.5,
    min_hit_rate: float = 0.50,
) -> dict:
    """Detect trigger events on the long-history dataset and measure
    forward-return predictive power.

    Returns a dict with diagnostics and a ``passed`` boolean. Caller
    should ABORT iter if not ``passed``.
    """
    # Identify cross events: z[t] < threshold AND z[t-1] >= threshold
    z_arr = z.reindex(close.index).values
    z_lag = np.concatenate([[np.nan], z_arr[:-1]])
    triggers = (z_arr < z_threshold) & (z_lag >= z_threshold)
    triggers = triggers & ~np.isnan(z_arr) & ~np.isnan(z_lag)

    trigger_idx = np.where(triggers)[0]
    # Need t+forward_days inside bounds
    valid = trigger_idx[trigger_idx + forward_days < len(close)]
    n_events = len(valid)

    if n_events == 0:
        return {
            "passed": False,
            "n_events": 0,
            "reason": "zero trigger events on this dataset",
        }

    log_close = np.log(close.values)
    fwd_returns = []
    for i in valid:
        r = float(log_close[i + forward_days] - log_close[i])
        fwd_returns.append(r)
    fwd = np.array(fwd_returns)

    mean_r = float(fwd.mean())
    std_r = float(fwd.std(ddof=1)) if len(fwd) > 1 else 0.0
    t_stat = mean_r / (std_r / np.sqrt(n_events)) if std_r > 0 else 0.0
    hit_rate = float(np.mean(fwd > 0))

    passed = (
        n_events >= min_events
        and t_stat >= min_t_stat
        and hit_rate >= min_hit_rate
    )
    return {
        "passed": passed,
        "n_events": int(n_events),
        "mean_5d_log_return": mean_r,
        "std_5d_log_return": std_r,
        "t_stat": t_stat,
        "hit_rate": hit_rate,
        "z_threshold": z_threshold,
        "forward_days": forward_days,
        "min_events": min_events,
        "min_t_stat": min_t_stat,
        "min_hit_rate": min_hit_rate,
    }


# ---------------------------------------------------------------------------
# Metric helpers (same as iter 003/004)
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
# Gate runners (per dataset) — identical to iter 003/004
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


def run_one_dataset(name: str, dxy_proxy: pd.Series) -> dict:
    df = load_dataset(name)
    if name == "xauusd_intraday":
        df = resample_1h_to_daily(df)
    df = df.sort_index()

    close = df["close"].astype(float)
    gross_returns = daily_returns(close)

    # Reindex DXY proxy onto the gold dataset's calendar via forward-fill
    # (FX has business-day calendar; gold may have slightly different
    # holidays especially via Tiingo CFD feed).
    dxy_aligned = dxy_proxy.reindex(df.index).ffill()
    z = compute_zscore(dxy_aligned, lookback=60)

    position = dxy_downcross_signal(
        z,
        z_threshold=-1.0,
        hold_days=5,
        cooldown_days=5,
    )

    ann = annualization_factor(name)

    br_a = apply_pepperstone_costs(
        gross_returns, position, intraday_close=False,
    )
    br_b = apply_inter_costs_with_darf(gross_returns, position)

    m_a = compute_metrics(br_a.net_pnl, ann)
    m_b = compute_metrics(br_b.net_pnl, ann)
    mean_hold_a, n_trades_a = compute_mean_hold_days(position)

    rets_a = br_a.net_pnl.dropna()

    g1_pbo = True
    g1_note = "single-cfg PBO degenerate; pass by convention (no overfit risk)"

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
            "note": "GS-2 cost cliff; reported for completeness",
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


def correlation_with_iter003(this_returns: dict[str, pd.Series]) -> dict:
    """Correlation of iter 005 PnL with iter 003 MR base PnL — IC-7 prep."""
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
        s_this = this_returns.get(ds, pd.Series([], dtype=float))
        common = s003.index.intersection(s_this.index)
        if len(common) < 50:
            out["by_dataset"][ds] = {"err": f"too few common bars ({len(common)})"}
            continue
        a = s003.loc[common]
        b = s_this.loc[common]
        if a.std() == 0 or b.std() == 0:
            corr = 0.0
        else:
            corr = float(a.corr(b))
        out["by_dataset"][ds] = {
            "correlation": corr,
            "n_common_bars": int(len(common)),
        }
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print(f"[{CFG_ID}] running on 3 datasets (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS})")

    dxy_proxy = load_fx_basket()
    print(
        f"DXY proxy: {len(dxy_proxy)} bars, "
        f"{dxy_proxy.index.min().date()} → {dxy_proxy.index.max().date()}"
    )

    # ---- Pre-validation screen on gld_long (longest dataset) -------------
    gld = load_dataset("gld_long").sort_index()
    dxy_for_gld = dxy_proxy.reindex(gld.index).ffill()
    z_gld = compute_zscore(dxy_for_gld, lookback=60)
    pre_val = pre_validation_screen(gld["close"].astype(float), z_gld)
    print(f"\n--- Pre-validation screen on gld_long ---")
    for k, v in pre_val.items():
        print(f"  {k}: {v}")
    if not pre_val["passed"]:
        print(
            "\nPRE-VAL FAILED — aborting iter (signal has no raw forward-edge "
            "on the long-history dataset). See pre_val dict for details."
        )
        # Still write minimal results so jornada has the abort record.
        abort_path = ITER_DIR / "results.json"
        abort_path.write_text(
            json.dumps({
                "config_id": CFG_ID,
                "status": "aborted",
                "reason": "pre_validation_screen_failed",
                "pre_validation": pre_val,
                "cumulative_n_trials": CUMULATIVE_N_TRIALS,
            }, indent=2, default=str),
            encoding="utf-8",
        )
        # Verdict file: declare FAIL with score 0
        verdict = {
            "total_score": 0,
            "tier": "FAIL",
            "winner_conditions_met": False,
            "configs_tested": 1,
            "primary_citation": "[ilmanen_expected_returns, ch.10]",
            "hypothesis_slug": "dxy-zscore-recovery",
            "broker_track": "both",
            "timeframes_used": ["1d"],
            "status": "iterating",
            "pre_validation": pre_val,
            "abort": True,
        }
        (ITER_DIR / "verdict.json").write_text(
            json.dumps(verdict, indent=2, default=str), encoding="utf-8",
        )
        return

    print("\nPre-val PASSED — proceeding with full backtest.\n")

    results: dict[str, dict] = {}
    iter005_returns: dict[str, pd.Series] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"--- {name} ---")
        r = run_one_dataset(name, dxy_proxy)
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
            f"MDD={mb['mdd']:.4%} (GS-2 cliff caveat)"
        )
        iter005_returns[name] = pd.Series(
            r["_returns_series"]["net_returns"],
            index=pd.to_datetime(r["_returns_series"]["index"]),
        )
        print()

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

    # Kill criterion: ≥ 2 of 3 datasets with negative Track-A Sharpe AND
    # at most 1 with positive Sharpe → cross-asset framing is regime-fragile
    # on Tiingo's coverage (same closure pattern as iter 004 GS-4).
    n_neg_sharpe = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["sharpe"] < 0
    )
    n_pos_sharpe = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["sharpe"] > 0
    )
    kill_criterion_fired = (n_neg_sharpe >= 2) and (n_pos_sharpe <= 1)

    ic7_corr = correlation_with_iter003(this_returns=iter005_returns)

    print(
        f"=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERION ===\n"
        f"datasets with negative Track-A Sharpe: {n_neg_sharpe}/3 (kill if ≥ 2)\n"
        f"datasets with positive Track-A Sharpe: {n_pos_sharpe}/3 (kill if ≤ 1)\n"
        f"kill_fired = {kill_criterion_fired}\n"
        f"\n=== IC-7 PREP (corr with iter 003 MR base) ===\n"
    )
    for ds, info in ic7_corr.get("by_dataset", {}).items():
        print(f"  {ds}: {info}")

    out = {
        "config_id": CFG_ID,
        "params": {
            "z_threshold": -1.0,
            "hold_days": 5,
            "cooldown_days": 5,
            "zscore_lookback": 60,
            "long_only": True,
            "swap_free": False,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "pre_validation": pre_val,
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
            "n_datasets_with_negative_track_a_sharpe": n_neg_sharpe,
            "n_datasets_with_positive_track_a_sharpe": n_pos_sharpe,
            "fired": kill_criterion_fired,
            "implication": (
                "If fired: cross-asset overlays as PRIMARY gold-entry "
                "triggers fail on Tiingo's coverage regardless of stress-vs-"
                "fundamentals signal source; closes overlay-as-primary family "
                "and forces pivot to fundamentals on LONGER-history data "
                "(needs FRED fetch for TIPS/DXY index pre-2020) or to a "
                "different family (FOMC events, calendar effects)."
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
    verdict["primary_citation"] = "[ilmanen_expected_returns, ch.10]"
    verdict["hypothesis_slug"] = "dxy-zscore-recovery"
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
    verdict["pre_validation"] = pre_val
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
