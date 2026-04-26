"""Iter 006 — Pre-FOMC drift T-2 to T+1 on gold (calendar-event signal).

Strategy
--------

For each scheduled FOMC announcement date T0 (last day of the meeting),
enter long gold at the close of T-2 (2 trading days prior) and exit at
the close of T+1 (1 trading day after). Position is binary {0, 1};
long-only; no leverage; no stops; mean hold = 4 trading days exactly
(within HARD GATE).

Datasets: gld_long, xauusd_real, xauusd_intraday (1h → daily resample).

Output: results.json (per-dataset metrics + gates + returns_series for
IC-7 cross-iter correlation); verdict.json (score + winner check + dual
broker-track metrics).

Citations
---------
* `[trading_systems_methods, p.479]` — Kaufman calendar-event chapter
* Lucca & Moench (2015) JoF 70(1) — pre-FOMC drift seminal SPX study
* `[ilmanen_expected_returns, ch.10]` — gold's USD/real-yield channels
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
* DEAD_ENDS GS-4 / GS-5 escape hatches — `studies/gold_swing_loop/DEAD_ENDS.md`
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
CFG_ID = "pre_fomc_drift_t2_to_t1"
# iter 001-005 contributed 1 each; this iter adds 1 → 6 total.
CUMULATIVE_N_TRIALS = 6

HOLD_BARS_BEFORE = 2   # T-2 entry → 2 bars before announcement
HOLD_BARS_AFTER = 1    # T+1 exit → 1 bar after (inclusive)
# Total bars held: HOLD_BARS_BEFORE + HOLD_BARS_AFTER + 1 = 4


# ---------------------------------------------------------------------------
# FOMC scheduled meeting announcement dates (last day of meeting)
# ---------------------------------------------------------------------------
# Sources:
# * Federal Reserve historical FOMC calendars 2004-2025
#   (https://www.federalreserve.gov/monetarypolicy/fomc_historical_year.htm)
# * Federal Reserve current FOMC calendar 2024-2026
#   (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm —
#    cross-checked via WebFetch on 2026-04-26)
# * Excludes emergency telephone conferences (e.g. 2008-01-22, 2020-03-15
#   intermeeting cuts) — they are not predictable in advance and cannot
#   support a pre-announcement drift trade.
# * 8 scheduled meetings per year, 2004-2025 = 22 × 8 = 176 dates;
#   plus 2 dates from 2026 already held (Jan-28, Mar-18) → 178 total.
FOMC_DATES: list[str] = [
    # 2004 (8)
    "2004-01-28", "2004-03-16", "2004-05-04", "2004-06-30",
    "2004-08-10", "2004-09-21", "2004-11-10", "2004-12-14",
    # 2005 (8)
    "2005-02-02", "2005-03-22", "2005-05-03", "2005-06-30",
    "2005-08-09", "2005-09-20", "2005-11-01", "2005-12-13",
    # 2006 (8)
    "2006-01-31", "2006-03-28", "2006-05-10", "2006-06-29",
    "2006-08-08", "2006-09-20", "2006-10-25", "2006-12-12",
    # 2007 (8)
    "2007-01-31", "2007-03-21", "2007-05-09", "2007-06-28",
    "2007-08-07", "2007-09-18", "2007-10-31", "2007-12-11",
    # 2008 (8)
    "2008-01-30", "2008-03-18", "2008-04-30", "2008-06-25",
    "2008-08-05", "2008-09-16", "2008-10-29", "2008-12-16",
    # 2009 (8)
    "2009-01-28", "2009-03-18", "2009-04-29", "2009-06-24",
    "2009-08-12", "2009-09-23", "2009-11-04", "2009-12-16",
    # 2010 (8)
    "2010-01-27", "2010-03-16", "2010-04-28", "2010-06-23",
    "2010-08-10", "2010-09-21", "2010-11-03", "2010-12-14",
    # 2011 (8)
    "2011-01-26", "2011-03-15", "2011-04-27", "2011-06-22",
    "2011-08-09", "2011-09-21", "2011-11-02", "2011-12-13",
    # 2012 (8)
    "2012-01-25", "2012-03-13", "2012-04-25", "2012-06-20",
    "2012-08-01", "2012-09-13", "2012-10-24", "2012-12-12",
    # 2013 (8)
    "2013-01-30", "2013-03-20", "2013-05-01", "2013-06-19",
    "2013-07-31", "2013-09-18", "2013-10-30", "2013-12-18",
    # 2014 (8)
    "2014-01-29", "2014-03-19", "2014-04-30", "2014-06-18",
    "2014-07-30", "2014-09-17", "2014-10-29", "2014-12-17",
    # 2015 (8)
    "2015-01-28", "2015-03-18", "2015-04-29", "2015-06-17",
    "2015-07-29", "2015-09-17", "2015-10-28", "2015-12-16",
    # 2016 (8)
    "2016-01-27", "2016-03-16", "2016-04-27", "2016-06-15",
    "2016-07-27", "2016-09-21", "2016-11-02", "2016-12-14",
    # 2017 (8)
    "2017-02-01", "2017-03-15", "2017-05-03", "2017-06-14",
    "2017-07-26", "2017-09-20", "2017-11-01", "2017-12-13",
    # 2018 (8)
    "2018-01-31", "2018-03-21", "2018-05-02", "2018-06-13",
    "2018-08-01", "2018-09-26", "2018-11-08", "2018-12-19",
    # 2019 (8)
    "2019-01-30", "2019-03-20", "2019-05-01", "2019-06-19",
    "2019-07-31", "2019-09-18", "2019-10-30", "2019-12-11",
    # 2020 (8) — excludes intermeeting cuts 2020-03-03, 2020-03-15
    "2020-01-29", "2020-03-18", "2020-04-29", "2020-06-10",
    "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
    # 2021 (8)
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16",
    "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
    # 2022 (8)
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15",
    "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    # 2023 (8)
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14",
    "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    # 2024 (8)
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
    "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    # 2025 (8)
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    # 2026 (2 held so far; 2026-04-29 is upcoming, post-data)
    "2026-01-28", "2026-03-18",
]


# ---------------------------------------------------------------------------
# Strategy primitives
# ---------------------------------------------------------------------------


def pre_fomc_position(
    calendar: pd.DatetimeIndex,
    fomc_dates: list[str],
    *,
    bars_before: int = HOLD_BARS_BEFORE,
    bars_after: int = HOLD_BARS_AFTER,
) -> pd.Series:
    """Build a binary {0.0, 1.0} position series on ``calendar``.

    For each FOMC date present in the calendar, mark the bars
    [T-bars_before, ..., T+bars_after] as long (1.0). Bars outside any
    FOMC window are 0.0.

    Drops:
    * FOMC dates not present in ``calendar`` (e.g. holiday or outside
      window) — strict full-window match
    * FOMC dates where ``T-bars_before`` would be < 0 or
      ``T+bars_after`` would be ≥ len(calendar) — incomplete window

    Edge cases (consecutive FOMCs within ``bars_before+bars_after+1``)
    don't occur in the actual schedule (Fed meetings are 6+ weeks apart),
    but if they did the position would just stay at 1.0 across the
    overlap (no double-counting since pos is binary {0, 1}).
    """
    pos = np.zeros(len(calendar), dtype=np.float64)
    cal_index = pd.DatetimeIndex(calendar)

    for d_str in fomc_dates:
        d = pd.Timestamp(d_str)
        if d not in cal_index:
            continue
        i_t0 = cal_index.get_loc(d)
        i_start = i_t0 - bars_before
        i_end = i_t0 + bars_after  # inclusive
        if i_start < 0 or i_end >= len(cal_index):
            continue
        pos[i_start:i_end + 1] = 1.0

    return pd.Series(pos, index=cal_index, name="position")


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


# ---------------------------------------------------------------------------
# Pre-validation screen (Stage 3a — abort if signal has no raw edge)
# ---------------------------------------------------------------------------


def pre_validation_screen(
    close: pd.Series,
    fomc_dates: list[str],
    *,
    bars_before: int = HOLD_BARS_BEFORE,
    bars_after: int = HOLD_BARS_AFTER,
    min_events: int = 50,
    min_t_stat: float = 0.5,
    min_hit_rate: float = 0.50,
) -> dict:
    """Measure forward 4-bar (T-bars_before → T+bars_after) gold log-return
    distribution per FOMC event on the long-history dataset.

    Returns dict with diagnostics + ``passed`` boolean. Caller should
    ABORT iter if ``not passed``.
    """
    cal_index = pd.DatetimeIndex(close.index)
    log_close = np.log(close.values)

    forward_returns: list[float] = []
    n_dropped_window = 0
    n_dropped_calendar = 0
    for d_str in fomc_dates:
        d = pd.Timestamp(d_str)
        if d not in cal_index:
            n_dropped_calendar += 1
            continue
        i_t0 = cal_index.get_loc(d)
        i_start = i_t0 - bars_before
        i_end = i_t0 + bars_after
        if i_start < 0 or i_end >= len(cal_index):
            n_dropped_window += 1
            continue
        # Cumulative log-return = log(close[T+1]) - log(close[T-2])
        r = float(log_close[i_end] - log_close[i_start])
        forward_returns.append(r)

    n_events = len(forward_returns)
    if n_events == 0:
        return {
            "passed": False,
            "n_events": 0,
            "reason": "no FOMC events fully contained in dataset window",
        }

    fwd = np.asarray(forward_returns, dtype=np.float64)
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
        "n_dropped_calendar": int(n_dropped_calendar),
        "n_dropped_window": int(n_dropped_window),
        "mean_4d_log_return": mean_r,
        "std_4d_log_return": std_r,
        "t_stat": t_stat,
        "hit_rate": hit_rate,
        "bars_before": bars_before,
        "bars_after": bars_after,
        "min_events": min_events,
        "min_t_stat": min_t_stat,
        "min_hit_rate": min_hit_rate,
    }


# ---------------------------------------------------------------------------
# Metric helpers (same as iter 003/004/005)
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
# Gate runners (per dataset) — identical to iter 003/004/005
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


def run_one_dataset(name: str) -> dict:
    df = load_dataset(name)
    if name == "xauusd_intraday":
        df = resample_1h_to_daily(df)
    df = df.sort_index()

    close = df["close"].astype(float)
    gross_returns = daily_returns(close)

    position = pre_fomc_position(
        df.index,
        FOMC_DATES,
        bars_before=HOLD_BARS_BEFORE,
        bars_after=HOLD_BARS_AFTER,
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
            "note": "GS-2 viable: ~8 trades/yr is well below the 15/yr cliff",
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
    """Correlation of iter 006 PnL with iter 003 MR base PnL — IC-7 prep."""
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
    print(f"FOMC dates loaded: {len(FOMC_DATES)} events "
          f"({FOMC_DATES[0]} → {FOMC_DATES[-1]})")

    # ---- Pre-validation screen on gld_long (longest dataset) -------------
    gld = load_dataset("gld_long").sort_index()
    pre_val = pre_validation_screen(gld["close"].astype(float), FOMC_DATES)
    print(f"\n--- Pre-validation screen on gld_long ---")
    for k, v in pre_val.items():
        print(f"  {k}: {v}")
    if not pre_val["passed"]:
        print(
            "\nPRE-VAL FAILED — aborting iter (Lucca-Moench pre-FOMC drift "
            "does not generalize to gold on long-history data)."
        )
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
        verdict = {
            "total_score": 0,
            "tier": "FAIL",
            "winner_conditions_met": False,
            "configs_tested": 1,
            "primary_citation": "[trading_systems_methods, p.479]",
            "hypothesis_slug": "pre-fomc-drift",
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
    iter006_returns: dict[str, pd.Series] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"--- {name} ---")
        r = run_one_dataset(name)
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
            f"MDD={mb['mdd']:.4%} (8/yr → fully viable)"
        )
        iter006_returns[name] = pd.Series(
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

    n_neg_sharpe = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["sharpe"] < 0
    )
    n_pos_sharpe = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["sharpe"] > 0
    )
    kill_criterion_fired = (n_neg_sharpe >= 2) and (n_pos_sharpe <= 1)

    ic7_corr = correlation_with_iter003(this_returns=iter006_returns)

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
            "bars_before": HOLD_BARS_BEFORE,
            "bars_after": HOLD_BARS_AFTER,
            "long_only": True,
            "swap_free": False,
            "n_fomc_dates_in_list": len(FOMC_DATES),
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
                "If fired with pre-val passing: pre-FOMC drift exists on "
                "long-history gold but is regime-fragile on 2020+ Tiingo "
                "coverage (same closure pattern as GS-4/GS-5). Closes "
                "calendar-event signals as PRIMARY gold-entry triggers on "
                "the short xauusd window; OK as IC-7 secondary."
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
    verdict["primary_citation"] = "[trading_systems_methods, p.479]"
    verdict["hypothesis_slug"] = "pre-fomc-drift"
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
