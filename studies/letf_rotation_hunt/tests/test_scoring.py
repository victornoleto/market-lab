"""Unit tests for scoring.py — rubric per spec §3.2 (with v2 underwater-vs-bench update)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_compute_metrics_basic():
    """Compute CAGR/MDD/Sharpe from equity curve (no benchmark)."""
    from studies.letf_rotation_hunt.core.scoring import compute_metrics

    dates = pd.date_range("2020-01-01", periods=252 * 3, freq="B")
    equity = pd.Series((1 + 0.0005) ** np.arange(len(dates)) * 10000, index=dates)
    returns = equity.pct_change().fillna(0)

    m = compute_metrics(equity, returns)

    assert "cagr" in m and "mdd" in m and "sharpe" in m and "calmar" in m
    # ~12.7% annual CAGR, MDD ~0 (monotonic up), Sharpe high
    assert m["cagr"] == pytest.approx(0.135, abs=0.02)
    assert m["mdd"] >= -0.01
    assert m["sharpe"] > 5  # near-deterministic
    # New v2 metrics default to NaN when benchmark not provided
    assert "pct_time_above_benchmark" in m
    assert np.isnan(m["pct_time_above_benchmark"])
    assert "min_relative_equity" in m
    assert np.isnan(m["min_relative_equity"])


def test_compute_metrics_benchmark_strategy_dominates():
    """Strategy strictly above benchmark → pct=1.0, min ratio > 1."""
    from studies.letf_rotation_hunt.core.scoring import compute_metrics

    dates = pd.date_range("2010-01-01", periods=252 * 4, freq="B")
    strat_eq = pd.Series((1 + 0.0008) ** np.arange(len(dates)) * 10000, index=dates)
    bench_eq = pd.Series((1 + 0.0003) ** np.arange(len(dates)) * 10000, index=dates)
    returns = strat_eq.pct_change().fillna(0)

    m = compute_metrics(strat_eq, returns, benchmark_equity=bench_eq)
    # After 252-day warmup, strategy compounds faster, so always > bench
    assert m["pct_time_above_benchmark"] == pytest.approx(1.0)
    assert m["min_relative_equity"] >= 1.0


def test_compute_metrics_benchmark_strategy_underperforms():
    """Strategy below benchmark → pct=0.0, min < 1."""
    from studies.letf_rotation_hunt.core.scoring import compute_metrics

    dates = pd.date_range("2010-01-01", periods=252 * 4, freq="B")
    strat_eq = pd.Series((1 + 0.0001) ** np.arange(len(dates)) * 10000, index=dates)
    bench_eq = pd.Series((1 + 0.0008) ** np.arange(len(dates)) * 10000, index=dates)
    returns = strat_eq.pct_change().fillna(0)

    m = compute_metrics(strat_eq, returns, benchmark_equity=bench_eq)
    assert m["pct_time_above_benchmark"] < 0.05
    assert m["min_relative_equity"] < 1.0


def test_compute_metrics_benchmark_short_series_fallback():
    """Series shorter than warmup → NaN underwater metrics."""
    from studies.letf_rotation_hunt.core.scoring import compute_metrics

    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    strat_eq = pd.Series(np.linspace(10000, 11000, 100), index=dates)
    bench_eq = pd.Series(np.linspace(10000, 10500, 100), index=dates)
    returns = strat_eq.pct_change().fillna(0)

    m = compute_metrics(strat_eq, returns, benchmark_equity=bench_eq)
    # After 252-day warmup, no data left → NaN
    assert np.isnan(m["pct_time_above_benchmark"])
    assert np.isnan(m["min_relative_equity"])


def test_score_underwater_full_pass():
    """100% time above benchmark + min ratio ≥ 1.0 → 15 pts criterion 2."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y":   {"cagr": 0.15, "mdd": -0.30, "sharpe": 0.95,
                     "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.5},
        "spy_real": {"cagr": 0.16, "mdd": -0.30, "sharpe": 1.00,
                     "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.5},
    }
    anchors = {"lh_56y": 0.682, "spy_real": 0.671}
    spy_mdds = {"lh_56y": -0.55, "spy_real": -0.55}
    gates = {"g1_pbo": 0.30, "g2_dsr_p_local": 0.01, "g3_wf_windows_pass": 7,
             "g3_wf_max_mdd": 0.30, "g4_oos_sharpe": 0.6, "g5_fwd_post2020_sharpe": 0.5,
             "g6_bootstrap_99_low": 0.05, "g7_xlib_cagr_delta": 0.01}
    crisis = {"2000_02_dotcom": True, "2008_gfc": True, "2020_covid": True, "2022_rates": True}

    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)
    assert result["2_underwater_vs_bench"] == 15


def test_score_underwater_t1c_like():
    """T1c-like profile: pct=99.83% + min=0.93 → 12 pts (tier 2)."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y": {"cagr": 0.23, "mdd": -0.75, "sharpe": 0.752,
                   "pct_time_above_benchmark": 0.9983, "min_relative_equity": 0.93},
    }
    anchors = {"lh_56y": 0.682}
    spy_mdds = {"lh_56y": -0.55}
    gates = {"g1_pbo": 0.56, "g2_dsr_p_local": 0.001, "g3_wf_windows_pass": 7,
             "g3_wf_max_mdd": 0.75, "g4_oos_sharpe": 0.95, "g5_fwd_post2020_sharpe": 0.94,
             "g6_bootstrap_99_low": 0.30, "g7_xlib_cagr_delta": 0.0}
    crisis = {"2000_02_dotcom": False, "2008_gfc": False, "2020_covid": False, "2022_rates": False}

    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)
    assert result["2_underwater_vs_bench"] == 12


def test_score_underwater_below_threshold():
    """pct < 90% → 0 pts."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y": {"cagr": 0.05, "mdd": -0.50, "sharpe": 0.30,
                   "pct_time_above_benchmark": 0.50, "min_relative_equity": 0.30},
    }
    anchors = {"lh_56y": 0.682}
    spy_mdds = {"lh_56y": -0.55}
    gates = {"g1_pbo": 0.70, "g2_dsr_p_local": 0.50, "g3_wf_windows_pass": 2,
             "g3_wf_max_mdd": 0.60, "g4_oos_sharpe": -0.1, "g5_fwd_post2020_sharpe": -0.2,
             "g6_bootstrap_99_low": -0.05, "g7_xlib_cagr_delta": 0.05}
    crisis = {"2000_02_dotcom": False, "2008_gfc": False, "2020_covid": False, "2022_rates": False}

    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)
    assert result["2_underwater_vs_bench"] == 0


def test_score_winner_strict_bars_underwater_blocks():
    """WINNER tier requires pct_time_above_bench >= 0.95 (strict bar)."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y":   {"cagr": 0.20, "mdd": -0.30, "sharpe": 1.00,
                     "pct_time_above_benchmark": 0.85, "min_relative_equity": 0.5},
        "spy_real": {"cagr": 0.20, "mdd": -0.30, "sharpe": 1.00,
                     "pct_time_above_benchmark": 0.85, "min_relative_equity": 0.5},
    }
    anchors = {"lh_56y": 0.682, "spy_real": 0.671}
    spy_mdds = {"lh_56y": -0.55, "spy_real": -0.55}
    gates = {"g1_pbo": 0.30, "g2_dsr_p_local": 0.01, "g3_wf_windows_pass": 7,
             "g3_wf_max_mdd": 0.30, "g4_oos_sharpe": 0.6, "g5_fwd_post2020_sharpe": 0.5,
             "g6_bootstrap_99_low": 0.05, "g7_xlib_cagr_delta": 0.01}
    crisis = {"2000_02_dotcom": True, "2008_gfc": True, "2020_covid": True, "2022_rates": True}

    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis, bonus_pts=5.0)
    # pct 0.85 < 0.95 strict bar → winner_conditions_met must be False
    assert result["winner_conditions_met"] is False
    assert result["tier_label"] != "WINNER"


def test_score_strategy_full_pass():
    """Score >= 90 with all criteria maxed including underwater 100%."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y":   {"cagr": 0.15, "mdd": -0.10, "sharpe": 0.95,
                     "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.5},
        "ndx_real": {"cagr": 0.18, "mdd": -0.10, "sharpe": 1.10,
                     "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.5},
        "spy_real": {"cagr": 0.16, "mdd": -0.10, "sharpe": 1.00,
                     "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.5},
    }
    anchors = {"lh_56y": 0.682, "ndx_real": 0.900, "spy_real": 0.900}
    spy_mdds = {"lh_56y": -0.55, "ndx_real": -0.34, "spy_real": -0.55}
    gates = {"g1_pbo": 0.30, "g2_dsr_p_local": 0.01, "g3_wf_windows_pass": 7,
             "g3_wf_max_mdd": 0.30, "g4_oos_sharpe": 0.6, "g5_fwd_post2020_sharpe": 0.5,
             "g6_bootstrap_99_low": 0.05, "g7_xlib_cagr_delta": 0.01}
    crisis = {"2000_02_dotcom": True, "2008_gfc": True, "2020_covid": True, "2022_rates": True}

    # 30 (sharpe edge) + 15 (underwater) + 20 (gates) + 10 (dsr) + 10 (oos) + 10 (crisis) + 5 (bonus) = 100
    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis, bonus_pts=5.0)

    assert result["total"] >= 90
    assert result["tier_label"] in ("WINNER", "STRONG")


def test_crisis_beats_benchmark_strategy_dominates_all():
    """Strategy strictly above benchmark in every crisis → all 4 True."""
    from studies.letf_rotation_hunt.core.scoring import crisis_beats_benchmark

    # Construct a daily index covering all 4 canonical crisis windows
    dates = pd.date_range("1995-01-01", "2024-12-31", freq="B")
    # Strategy compounds 0.0005/day; benchmark 0.0001/day
    strat_eq = pd.Series((1 + 0.0005) ** np.arange(len(dates)) * 10000, index=dates)
    bench_eq = pd.Series((1 + 0.0001) ** np.arange(len(dates)) * 10000, index=dates)

    out = crisis_beats_benchmark(strat_eq, bench_eq)
    assert isinstance(out, dict)
    # All 4 canonical crises present
    assert set(out.keys()) == {"2000_02_dotcom", "2008_gfc", "2020_covid", "2022_rates"}
    assert all(v is True for v in out.values())


def test_crisis_beats_benchmark_strategy_below_all():
    """Strategy strictly below benchmark in every crisis → all 4 False."""
    from studies.letf_rotation_hunt.core.scoring import crisis_beats_benchmark

    dates = pd.date_range("1995-01-01", "2024-12-31", freq="B")
    strat_eq = pd.Series((1 + 0.0001) ** np.arange(len(dates)) * 10000, index=dates)
    bench_eq = pd.Series((1 + 0.0005) ** np.arange(len(dates)) * 10000, index=dates)

    out = crisis_beats_benchmark(strat_eq, bench_eq)
    assert all(v is False for v in out.values())


def test_crisis_beats_benchmark_pre_crisis_window_returns_false():
    """If equity series ends before a crisis window, that crisis is False."""
    from studies.letf_rotation_hunt.core.scoring import crisis_beats_benchmark

    # Series ends 1990 — all 4 canonical crises after it → all False
    dates = pd.date_range("1986-01-01", "1990-12-31", freq="B")
    strat = pd.Series((1 + 0.001) ** np.arange(len(dates)) * 10000, index=dates)
    bench = pd.Series((1 + 0.0001) ** np.arange(len(dates)) * 10000, index=dates)

    out = crisis_beats_benchmark(strat, bench)
    # Insufficient data within each crisis window → False for all
    assert all(v is False for v in out.values())


def test_crisis_beats_benchmark_mixed():
    """Strategy beats benchmark in 2 crises, loses in 2 → mixed dict."""
    from studies.letf_rotation_hunt.core.scoring import (
        CRISIS_WINDOWS, crisis_beats_benchmark,
    )

    # Build piecewise series: strategy strong before 2010, weak after
    dates = pd.date_range("1995-01-01", "2024-12-31", freq="B")
    strat_arr = np.zeros(len(dates))
    bench_arr = np.zeros(len(dates))
    cutoff = pd.Timestamp("2010-01-01")
    pre_cutoff = dates < cutoff
    post_cutoff = ~pre_cutoff
    # Pre-2010: strategy 0.0005, benchmark 0.0001
    strat_arr[pre_cutoff] = 0.0005
    bench_arr[pre_cutoff] = 0.0001
    # Post-2010: strategy 0.0001, benchmark 0.0005
    strat_arr[post_cutoff] = 0.0001
    bench_arr[post_cutoff] = 0.0005

    strat_eq = pd.Series((1 + strat_arr).cumprod() * 10000, index=dates)
    bench_eq = pd.Series((1 + bench_arr).cumprod() * 10000, index=dates)

    out = crisis_beats_benchmark(strat_eq, bench_eq)
    # 2000 dotcom + 2008 GFC are pre-cutoff → strategy beats
    assert out["2000_02_dotcom"] is True
    assert out["2008_gfc"] is True
    # 2020 covid + 2022 rates are post-cutoff → strategy loses
    assert out["2020_covid"] is False
    assert out["2022_rates"] is False


def test_crisis_windows_constant_has_4_entries():
    """The CRISIS_WINDOWS constant must have the 4 canonical crises with valid date strings."""
    from studies.letf_rotation_hunt.core.scoring import CRISIS_WINDOWS

    assert len(CRISIS_WINDOWS) == 4
    for name in ("2000_02_dotcom", "2008_gfc", "2020_covid", "2022_rates"):
        assert name in CRISIS_WINDOWS
        start, end = CRISIS_WINDOWS[name]
        assert pd.Timestamp(start) < pd.Timestamp(end)


def test_score_strategy_g3_benchmark_relative_pass():
    """G3 redesign 2026-05-06: scoring uses new key
    ``g3_wf_windows_pass_pct_above_benchmark`` when present and ignores
    ``g3_wf_max_mdd`` (warning-only per mandate §2.3)."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y": {"cagr": 0.20, "mdd": -0.74, "sharpe": 0.85,
                   "pct_time_above_benchmark": 1.0, "min_relative_equity": 1.4},
    }
    anchors = {"lh_56y": 0.682}
    spy_mdds = {"lh_56y": -0.55}
    # Note MDD 0.749 — would have failed the old G3 gate; new key passes G3.
    gates = {
        "g1_pbo": 0.30, "g2_dsr_p_local": 0.01,
        "g3_wf_windows_pass": 8,
        "g3_wf_windows_pass_pct_above_benchmark": 8,  # new key, passes
        "g3_wf_max_mdd": 0.749,                      # warning-only now
        "g4_oos_sharpe": 0.6, "g5_fwd_post2020_sharpe": 0.5,
        "g6_bootstrap_99_low": 0.30, "g7_xlib_cagr_delta": 0.0,
    }
    crisis = {"2000_02_dotcom": True, "2008_gfc": True,
              "2020_covid": True, "2022_rates": True}
    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)
    # 5 hard-gates × 4 pts each = 20 if G1+G2+G3+G6+G7 all pass
    assert result["3_gates"] == 20


def test_score_strategy_g3_benchmark_relative_fail_below_threshold():
    """New G3: pct_above_benchmark < 5/8 → G3 fails; MDD value irrelevant."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y": {"cagr": 0.05, "mdd": -0.20, "sharpe": 0.30,
                   "pct_time_above_benchmark": 0.40, "min_relative_equity": 0.30},
    }
    anchors = {"lh_56y": 0.682}
    spy_mdds = {"lh_56y": -0.55}
    gates = {
        "g1_pbo": 0.30, "g2_dsr_p_local": 0.01,
        "g3_wf_windows_pass": 8,                      # legacy says pass
        "g3_wf_windows_pass_pct_above_benchmark": 2,  # new gate fails (< 5)
        "g3_wf_max_mdd": 0.20,                       # legacy MDD passes
        "g4_oos_sharpe": 0.6, "g5_fwd_post2020_sharpe": 0.5,
        "g6_bootstrap_99_low": 0.30, "g7_xlib_cagr_delta": 0.0,
    }
    crisis = {"2000_02_dotcom": False, "2008_gfc": False,
              "2020_covid": False, "2022_rates": False}
    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)
    # G1+G2+G6+G7 pass; G3 fails (new key < 5) → 4×4 = 16
    assert result["3_gates"] == 16


def test_score_strategy_zero_edge():
    """Score is low when Sharpe edge fails AND underwater fails on all datasets."""
    from studies.letf_rotation_hunt.core.scoring import score_strategy

    metrics = {
        "lh_56y":   {"cagr": 0.05, "mdd": -0.50, "sharpe": 0.30,
                     "pct_time_above_benchmark": 0.40, "min_relative_equity": 0.20},
        "ndx_real": {"cagr": 0.05, "mdd": -0.50, "sharpe": 0.40,
                     "pct_time_above_benchmark": 0.40, "min_relative_equity": 0.20},
        "spy_real": {"cagr": 0.05, "mdd": -0.50, "sharpe": 0.30,
                     "pct_time_above_benchmark": 0.40, "min_relative_equity": 0.20},
    }
    anchors = {"lh_56y": 0.682, "ndx_real": 0.900, "spy_real": 0.900}
    spy_mdds = {"lh_56y": -0.55, "ndx_real": -0.34, "spy_real": -0.55}
    gates = {"g1_pbo": 0.70, "g2_dsr_p_local": 0.50, "g3_wf_windows_pass": 2,
             "g3_wf_max_mdd": 0.60, "g4_oos_sharpe": -0.1, "g5_fwd_post2020_sharpe": -0.2,
             "g6_bootstrap_99_low": -0.05, "g7_xlib_cagr_delta": 0.05}
    crisis = {"2000_02_dotcom": False, "2008_gfc": False, "2020_covid": False, "2022_rates": False}

    result = score_strategy(metrics, anchors, spy_mdds, gates, crisis)

    assert result["total"] < 40
    assert result["tier_label"] in ("FAIL", "NEAR_FAIL")
