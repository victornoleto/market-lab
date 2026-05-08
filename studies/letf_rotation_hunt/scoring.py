"""Scoring rubric + tier mapping for letf_rotation_hunt.

Per spec §3.2: 7-criterion rubric (0-100 + 5 bonus) tier-aware.

Scoring v2 (2026-05-06): criterion 2 swapped from MDD-vs-SPY to
**Underwater-vs-benchmark** per user observation 2026-05-06 — what matters for
deploy is whether the strategy ever dips below the buy-hold benchmark equity
curve (SPY), not the absolute drawdown magnitude. MDD remains warning-only
per mandate §2.3. Strict bar set updated: WINNER tier requires
pct_time_above_benchmark ≥ 0.95 (replaces old "MDD ≤ SPY" bar).

Citations:
  - [advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]
  - [leverage_for_the_long_run, p.13]
  - mandate §2.2/§2.3 (CAGR/MDD warning-only)
  - User observation 2026-05-06 (underwater-vs-benchmark thesis)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

# Underwater-vs-benchmark: how many post-warmup days does strategy need before
# the "is strategy above benchmark?" check is meaningful. Below this floor
# the metrics are noisy / pre-compounding artifacts.
_UNDERWATER_WARMUP_DAYS = TRADING_DAYS_PER_YEAR  # 1 trading year

# Strict bar threshold: WINNER requires pct_time_above_benchmark >= this.
WINNER_PCT_ABOVE_BENCH_BAR = 0.95

# Per-crisis windows for criterion 6 attribution. Per user observation
# 2026-05-06 (extending the underwater-vs-benchmark thesis to crisis windows):
# what matters is RELATIVE equity vs benchmark in the crisis, not absolute
# MDD. A LETF strategy can have deeper absolute MDD than SPY in a crisis but
# still "beat SPY" if it spent more time above SPY equity (renormalised).
#
# Window choices (peak-to-trough plus modest recovery for each event):
#   - 2000_02_dotcom: NDX peak Mar 2000, S&P trough Oct 2002 → 2000-03 to 2002-10
#   - 2008_gfc:       Lehman Sep 2008, S&P trough Mar 2009 → 2008-09 to 2009-06
#   - 2020_covid:     SPY peak Feb 2020, recovery Apr-Jun 2020 → 2020-02-19 to 2020-06-30
#   - 2022_rates:     Calendar year of Fed rate hikes + bond+equity drawdown
CRISIS_WINDOWS: dict[str, tuple[str, str]] = {
    "2000_02_dotcom": ("2000-03-01", "2002-10-31"),
    "2008_gfc":       ("2008-09-01", "2009-06-30"),
    "2020_covid":     ("2020-02-19", "2020-06-30"),
    "2022_rates":     ("2022-01-01", "2022-12-31"),
}

# Minimum aligned days per crisis window for the comparison to be meaningful.
_CRISIS_MIN_DAYS = 5
# Strategy "beats" benchmark in a crisis if pct_time_strategy_above_bench
# (renormalised, intra-window) ≥ this fraction.
_CRISIS_PCT_ABOVE_BAR = 0.50


def crisis_beats_benchmark(
    equity: pd.Series,
    benchmark_equity: pd.Series,
    crisis_windows: dict[str, tuple[str, str]] | None = None,
    pct_threshold: float = _CRISIS_PCT_ABOVE_BAR,
) -> dict[str, bool]:
    """For each crisis window, did the strategy spend > pct_threshold of the
    days above the benchmark (renormalised within the window)?

    This mirrors the underwater-vs-benchmark logic at the per-crisis level.
    Per user observation 2026-05-06: relative equity matters, not absolute
    drawdown. A 2× LETF strategy may have deeper absolute MDD in 2008 than
    SPY but still "beat SPY" if it stayed above SPY equity > half the days
    of the crisis window.

    Parameters
    ----------
    equity : pd.Series
        Strategy equity curve.
    benchmark_equity : pd.Series
        Benchmark equity curve (typically SPY).
    crisis_windows : dict[str, (start, end)] | None
        Per-crisis date windows. Defaults to CRISIS_WINDOWS.
    pct_threshold : float
        Threshold for "beats" (default 0.50).

    Returns
    -------
    dict[str, bool]
        Per-crisis boolean (matches the keys of crisis_windows).
    """
    windows = crisis_windows if crisis_windows is not None else CRISIS_WINDOWS
    out: dict[str, bool] = {}
    for name, (start, end) in windows.items():
        s = equity[(equity.index >= start) & (equity.index <= end)]
        b = benchmark_equity[
            (benchmark_equity.index >= start) & (benchmark_equity.index <= end)
        ]
        aligned = pd.concat({"s": s, "b": b}, axis=1, sort=True).dropna()
        if len(aligned) < _CRISIS_MIN_DAYS:
            out[name] = False
            continue
        s_norm = aligned["s"] / float(aligned["s"].iloc[0])
        b_norm = aligned["b"] / float(aligned["b"].iloc[0])
        ratio = s_norm / b_norm
        out[name] = bool((ratio > 1.0).mean() >= pct_threshold)
    return out


def compute_metrics(
    equity: pd.Series,
    returns: pd.Series,
    benchmark_equity: pd.Series | None = None,
) -> dict:
    """Compute CAGR / MDD / Sharpe / Calmar / vol / skew / kurt / underwater.

    Parameters
    ----------
    equity : pd.Series
        Equity curve (starts at $10k typically).
    returns : pd.Series
        Daily returns.
    benchmark_equity : pd.Series | None
        Optional benchmark equity curve. If provided, the function computes:
        - ``pct_time_above_benchmark`` (post 252-day warmup)
        - ``min_relative_equity`` (post warmup; ``strategy_eq / benchmark_eq``).
        Caller is responsible for windowing the benchmark to the same period
        as the strategy. Both series are renormalised to start at the same $
        on the first common date so the relative ratio is meaningful.

    Returns
    -------
    dict
        Standard metrics + ``pct_time_above_benchmark`` and
        ``min_relative_equity`` (NaN if benchmark not supplied or insufficient
        post-warmup data).
    """
    returns = returns.dropna()
    n = len(returns)
    base = {
        "cagr": np.nan, "mdd": np.nan, "sharpe": np.nan, "calmar": np.nan,
        "vol_annual": np.nan, "skew": np.nan, "kurt": np.nan,
        "turnover_annual": np.nan,
        "pct_time_above_benchmark": np.nan,
        "min_relative_equity": np.nan,
    }
    if n < 2:
        return base

    # CAGR
    total_return = equity.iloc[-1] / equity.iloc[0]
    years = n / TRADING_DAYS_PER_YEAR
    cagr = total_return ** (1 / years) - 1 if total_return > 0 else -1.0

    # MDD
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    mdd = float(drawdown.min())

    # Sharpe (annualized)
    mean_daily = returns.mean()
    std_daily = returns.std(ddof=1)
    sharpe = (mean_daily / std_daily) * np.sqrt(TRADING_DAYS_PER_YEAR) if std_daily > 0 else 0.0

    # Calmar
    calmar = cagr / abs(mdd) if mdd < 0 else np.inf

    out = {
        "cagr": float(cagr),
        "mdd": mdd,
        "sharpe": float(sharpe),
        "calmar": float(calmar),
        "vol_annual": float(std_daily * np.sqrt(TRADING_DAYS_PER_YEAR)),
        "skew": float(returns.skew()),
        "kurt": float(returns.kurtosis()),
        "turnover_annual": np.nan,  # caller fills via position changes
        "pct_time_above_benchmark": np.nan,
        "min_relative_equity": np.nan,
    }

    if benchmark_equity is not None:
        out.update(_underwater_metrics(equity, benchmark_equity))

    return out


def _underwater_metrics(
    equity: pd.Series, benchmark_equity: pd.Series,
    warmup_days: int = _UNDERWATER_WARMUP_DAYS,
) -> dict:
    """Compute pct_time_above_benchmark + min_relative_equity post-warmup.

    Aligns both series on the intersection of their indices, renormalises so
    both start at the same value on the first common date, and measures the
    ratio strategy_eq / benchmark_eq from day ``warmup_days`` onwards.

    Per the user observation 2026-05-06: a strategy with high absolute MDD is
    still acceptable if at every (post-warmup) point it sits above the
    buy-hold benchmark — what matters is "would I have been better off doing
    the strategy or just buying the benchmark?"
    """
    aligned = pd.concat({"s": equity, "b": benchmark_equity}, axis=1, sort=True).dropna()
    if len(aligned) < warmup_days + 2:
        return {
            "pct_time_above_benchmark": float("nan"),
            "min_relative_equity": float("nan"),
        }

    # Renormalize both so they start at the same value on first common date.
    s_norm = aligned["s"] / aligned["s"].iloc[0]
    b_norm = aligned["b"] / aligned["b"].iloc[0]
    ratio = s_norm / b_norm

    post_warmup = ratio.iloc[warmup_days:]
    if len(post_warmup) < 2:
        return {
            "pct_time_above_benchmark": float("nan"),
            "min_relative_equity": float("nan"),
        }
    return {
        "pct_time_above_benchmark": float((post_warmup > 1.0).mean()),
        "min_relative_equity": float(post_warmup.min()),
    }


def score_strategy(
    metrics_per_dataset: dict[str, dict[str, float]],
    anchors_sharpe_per_dataset: dict[str, float],
    spy_mdd_per_dataset: dict[str, float],
    gates: dict[str, float],
    crisis_beats_spy: dict[str, bool],
    bonus_pts: float = 0.0,
) -> dict:
    """Compute 0-100 score per spec §3.2 rubric (v2 with underwater-vs-bench).

    Scoring v2 changes (2026-05-06):
    - Criterion 2 swapped from MDD-vs-SPY to underwater-vs-benchmark
      (uses ``pct_time_above_benchmark`` + ``min_relative_equity`` per
      dataset, fed by ``compute_metrics(benchmark_equity=...)``).
    - WINNER strict bars: pct_time_above_benchmark ≥ 0.95 (averaged across
      datasets) replaces the old "MDD ≤ SPY" bar. MDD warning-only per
      mandate §2.3.

    Parameters
    ----------
    metrics_per_dataset : dict[str, dict]
        Per-dataset metrics including ``pct_time_above_benchmark`` and
        ``min_relative_equity`` (from compute_metrics with benchmark).
    anchors_sharpe_per_dataset : dict[str, float]
        Tier anchor Sharpe per dataset.
    spy_mdd_per_dataset : dict[str, float]
        Retained for backwards compatibility / diagnostic; no longer used in
        scoring (MDD warning-only per mandate §2.3).
    gates : dict[str, float]
        Gate values (G1-G7).
    crisis_beats_spy : dict[str, bool]
        Per-crisis flag (4 windows).
    bonus_pts : float
        Caller-provided bonus (0-5).

    Returns
    -------
    dict
        Score breakdown + total + tier_label + winner_conditions_met.
    """
    # Criterion 1: Sharpe edge (max 30)
    edge_per_dataset = {
        ds: metrics_per_dataset[ds]["sharpe"] - anchors_sharpe_per_dataset[ds]
        for ds in metrics_per_dataset
    }
    datasets_beat_anchor = sum(1 for e in edge_per_dataset.values() if e >= 0.05)
    pts_1 = min(datasets_beat_anchor, 2) * 10  # +10 per dataset, max first 2
    if datasets_beat_anchor >= 3:
        pts_1 += 5  # +5 if all 3 pass
    pts_1 = min(pts_1, 30)

    # Criterion 2 (v2): Underwater-vs-benchmark (max 15)
    # Two-axis tiering: combines pct_time_above_benchmark and min_relative_equity.
    # Caller of compute_metrics must have supplied benchmark_equity to populate
    # these; missing/NaN values yield 0 pts (warning only).
    pct_per_ds = []
    min_ratio_per_ds = []
    for ds, m in metrics_per_dataset.items():
        p = m.get("pct_time_above_benchmark", float("nan"))
        r = m.get("min_relative_equity", float("nan"))
        if p == p:  # not NaN
            pct_per_ds.append(p)
        if r == r:
            min_ratio_per_ds.append(r)

    if pct_per_ds:
        mean_pct = sum(pct_per_ds) / len(pct_per_ds)
        mean_min = sum(min_ratio_per_ds) / len(min_ratio_per_ds) if min_ratio_per_ds else float("nan")
    else:
        mean_pct = float("nan")
        mean_min = float("nan")

    pts_2 = _underwater_points(mean_pct, mean_min)

    # Criterion 3: Gates hard-pass (G1, G2, G3, G6, G7) — 4 pts each
    g1_ok = gates.get("g1_pbo", 1.0) < 0.5
    g2_ok = gates.get("g2_dsr_p_local", 1.0) < 0.05
    # G3 redesign 2026-05-06 (mandate §2.3 + user observation): benchmark-relative
    # pass = ≥5/8 walk-forward windows with strategy above benchmark > half the
    # time. Falls back to legacy Sharpe-positivity + MDD<50% when the new field
    # is absent (e.g. unit tests using minimal gate dicts).
    g3_pct_field = gates.get("g3_wf_windows_pass_pct_above_benchmark")
    if g3_pct_field is not None:
        g3_ok = int(g3_pct_field) >= 5
    else:
        g3_ok = (
            gates.get("g3_wf_windows_pass", 0) >= 5
            and gates.get("g3_wf_max_mdd", 1.0) < 0.5
        )
    g6_ok = gates.get("g6_bootstrap_99_low", -1.0) > 0
    g7_ok = abs(gates.get("g7_xlib_cagr_delta", 1.0)) <= 0.03
    pts_3 = 4 * sum([g1_ok, g2_ok, g3_ok, g6_ok, g7_ok])

    # Criterion 4: DSR (max 10)
    dsr_p = gates.get("g2_dsr_p_local", 1.0)
    if dsr_p < 0.05:
        pts_4 = 10
    elif dsr_p < 0.10:
        pts_4 = 7
    elif dsr_p < 0.20:
        pts_4 = 3
    else:
        pts_4 = 0

    # Criterion 5: OOS + FWD (max 10)
    pts_5 = 0
    if gates.get("g4_oos_sharpe", -1.0) > 0:
        pts_5 += 5
    if gates.get("g5_fwd_post2020_sharpe", -1.0) > 0:
        pts_5 += 5

    # Criterion 6: Crisis attribution vs SPY (max 10, 2.5 each)
    pts_6 = 2.5 * sum(1 for v in crisis_beats_spy.values() if v)

    # Criterion 7: Bonus (max 5)
    pts_7 = min(max(bonus_pts, 0), 5)

    total = pts_1 + pts_2 + pts_3 + pts_4 + pts_5 + pts_6 + pts_7
    total = max(0, min(100, total))

    # WINNER strict bars per spec §3.3 (v2):
    #   - G1, G2, G6, G7 pass
    #   - Sharpe edge >= +0.05 on at least one dataset
    #   - pct_time_above_benchmark >= 0.95 (averaged) — replaces MDD ≤ SPY
    sharpe_edge_passed = any(e >= 0.05 for e in edge_per_dataset.values())
    underwater_bar_passed = (mean_pct >= WINNER_PCT_ABOVE_BENCH_BAR
                              if mean_pct == mean_pct else False)
    winner_conditions_met = (
        g1_ok and g2_ok and g6_ok and g7_ok
        and sharpe_edge_passed
        and underwater_bar_passed
    )

    # Tier mapping
    if total >= 90 and winner_conditions_met:
        tier_label = "WINNER"
    elif total >= 90:
        tier_label = "STRONG"  # high score but strict bar failed
    elif total >= 75:
        tier_label = "STRONG"
    elif total >= 60:
        tier_label = "PROMISING"
    elif total >= 40:
        tier_label = "MARGINAL"
    elif total >= 20:
        tier_label = "NEAR_FAIL"
    else:
        tier_label = "FAIL"

    return {
        "1_sharpe_edge": pts_1,
        "2_underwater_vs_bench": pts_2,
        "3_gates": pts_3,
        "4_dsr": pts_4,
        "5_oos_fwd": pts_5,
        "6_crisis": pts_6,
        "7_bonus": pts_7,
        "total": float(total),
        "tier_label": tier_label,
        "winner_conditions_met": bool(winner_conditions_met),
        "underwater_diagnostics": {
            "mean_pct_time_above_benchmark": float(mean_pct) if mean_pct == mean_pct else None,
            "mean_min_relative_equity": float(mean_min) if mean_min == mean_min else None,
            "winner_strict_bar": WINNER_PCT_ABOVE_BENCH_BAR,
            "winner_strict_bar_passed": bool(underwater_bar_passed),
        },
    }


def _underwater_points(mean_pct: float, mean_min: float) -> int:
    """Two-axis tiering of underwater-vs-benchmark performance.

    Returns 0-15 pts per spec §3.2 v2:
        15 pts: 100% time > benchmark + min ratio ≥ 1.0× (never underwater)
        12 pts: ≥99% time + min ratio ≥ 0.8×
         9 pts: ≥95% time + min ratio ≥ 0.7×
         6 pts: ≥90% time
         0 pts: <90% time or NaN
    """
    if mean_pct != mean_pct:  # NaN
        return 0
    if mean_pct >= 1.0 - 1e-9 and (mean_min != mean_min or mean_min >= 1.0):
        return 15
    if mean_pct >= 0.99 and (mean_min != mean_min or mean_min >= 0.8):
        return 12
    if mean_pct >= 0.95 and (mean_min != mean_min or mean_min >= 0.7):
        return 9
    if mean_pct >= 0.90:
        return 6
    return 0
