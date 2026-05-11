"""TDD coverage for tax_comparison sub-study.

Covers:
  - per_swing.py FIFO accounting (Model 1)
  - select_top10.py verdict scanning + dedup + T2 exclusion
  - reconstruct.py end-to-end smoke

Lei 14.754/2023 references the existing tax_layer.py for Model 2; no separate
tests added here for it (covered by test_tax_layer.py).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_package_imports():
    """Smoke: package importable."""
    import studies.letf_rotation_hunt.analyses.tax_comparison  # noqa: F401


def test_per_swing_buy_and_hold_pays_zero_tax():
    """Hold a single asset 100% across all bars — no swing, no tax.

    Convention: positions[t] is set at end of bar t (held going INTO bar t+1)
    and returns[t] is the return realised during bar t. Bar 0 is the initial
    deploy with no return earned, so a 10-bar buy-and-hold compounds 9 returns
    (matches dispatcher's `positions.shift(1) * returns` formula)."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing

    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    asset_returns = pd.DataFrame({"QLD": [0.01] * 10}, index=dates)  # +1%/day
    positions = pd.DataFrame({"QLD": [1.0] * 10}, index=dates)

    result = simulate_per_swing(
        positions=positions, asset_returns=asset_returns,
        initial_capital=10_000.0, tax_rate=0.15,
    )

    expected_final = 10_000.0 * (1.01 ** 9)  # 9 returns compounded over 10 bars
    assert result["net_equity"].iloc[-1] == pytest.approx(expected_final, rel=1e-6)
    assert result["net_equity"].iloc[0] == pytest.approx(10_000.0, rel=1e-6)
    assert result["tax_paid_total"] == pytest.approx(0.0, abs=1e-6)
    assert result["n_taxable_swings"] == 0


def test_per_swing_single_winning_trade_taxed_15pct():
    """Buy at $10k, asset doubles over 5 bars, sell on bar 6 — tax 15% on $10k gain."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing

    dates = pd.date_range("2020-01-01", periods=7, freq="D")
    # Asset doubles by bar 5 then flat; second column is OFF cash-equivalent
    rets_qld = [0.0, 0.1487, 0.1487, 0.1487, 0.1487, 0.1487, 0.0]  # ~2× by bar 5
    rets_off = [0.0] * 7
    asset_returns = pd.DataFrame({"QLD": rets_qld, "OFF": rets_off}, index=dates)

    # Hold QLD 100% bars 0..5, switch to OFF on bar 6
    positions = pd.DataFrame({
        "QLD": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        "OFF": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    }, index=dates)

    result = simulate_per_swing(
        positions=positions, asset_returns=asset_returns,
        initial_capital=10_000.0, tax_rate=0.15,
    )

    # Pre-tax NAV at bar 6 ≈ 10_000 × prod(1+rets) ≈ 20_000
    # PnL realized ≈ 10_000; tax ≈ 1_500; net ≈ 18_500
    final_net = result["net_equity"].iloc[-1]
    assert final_net == pytest.approx(18_500.0, rel=0.01)
    assert result["tax_paid_total"] == pytest.approx(1_500.0, rel=0.01)
    assert result["n_taxable_swings"] == 1


def test_per_swing_single_losing_trade_pays_zero_tax():
    """Buy at $10k, asset halves, sell at trough — no tax (loss)."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing

    dates = pd.date_range("2020-01-01", periods=7, freq="D")
    rets_qld = [0.0, -0.1294, -0.1294, -0.1294, -0.1294, -0.1294, 0.0]  # ~0.5× by bar 5
    rets_off = [0.0] * 7
    asset_returns = pd.DataFrame({"QLD": rets_qld, "OFF": rets_off}, index=dates)
    positions = pd.DataFrame({
        "QLD": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        "OFF": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    }, index=dates)

    result = simulate_per_swing(positions, asset_returns, 10_000.0, 0.15)

    final_net = result["net_equity"].iloc[-1]
    assert final_net == pytest.approx(5_000.0, rel=0.01)
    assert result["tax_paid_total"] == pytest.approx(0.0, abs=1e-6)
    assert result["n_taxable_swings"] == 0


def test_per_swing_no_loss_offset_across_swings():
    """First swing loses $1000; second swing gains $1000. Per-swing tax pays
    15% × 1000 = 150 on the win (no offset). Final net = 10000 - 150 = 9850."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing

    dates = pd.date_range("2020-01-01", periods=8, freq="D")
    # Bars 0-1: hold QLD; QLD drops 10% → loss 1000.  Bars 2-3: hold OFF (cash-equiv).
    # Bars 4-5: re-buy QLD; QLD rises ~11.11% → gain 1000.  Bar 6-7: exit.
    rets_qld = [0.0, -0.10, 0.0, 0.0, 0.0, 0.1111, 0.0, 0.0]
    rets_off = [0.0] * 8
    asset_returns = pd.DataFrame({"QLD": rets_qld, "OFF": rets_off}, index=dates)
    positions = pd.DataFrame({
        "QLD": [1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
        "OFF": [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
    }, index=dates)

    result = simulate_per_swing(positions, asset_returns, 10_000.0, 0.15)

    # First exit (bar 2): NAV 9000, no tax. Re-enter QLD with 9000.
    # QLD rises 11.11% → 9000 × 1.1111 ≈ 10000. Exit: PnL = 1000, tax = 150.
    # Net final ≈ 10000 - 150 = 9850.
    final_net = result["net_equity"].iloc[-1]
    assert final_net == pytest.approx(9_850.0, rel=0.01)
    assert result["tax_paid_total"] == pytest.approx(150.0, rel=0.01)
    assert result["n_taxable_swings"] == 1


def test_per_swing_partial_reduction_proportional_basis():
    """Hold QLD 100%, asset doubles, reduce to 50%. Half the position is sold;
    realized PnL = 0.5 × initial × (1) = 5000; tax = 750."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing

    dates = pd.date_range("2020-01-01", periods=7, freq="D")
    rets_qld = [0.0, 0.1487, 0.1487, 0.1487, 0.1487, 0.1487, 0.0]  # ~2× by bar 5
    rets_off = [0.0] * 7
    asset_returns = pd.DataFrame({"QLD": rets_qld, "OFF": rets_off}, index=dates)
    positions = pd.DataFrame({
        "QLD": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
        "OFF": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5],
    }, index=dates)

    result = simulate_per_swing(positions, asset_returns, 10_000.0, 0.15)

    # NAV at bar 5 ≈ 20000 (all QLD). On bar 6: rebalance to 50/50.
    # Sell QLD 10000; FIFO basis = 5000 (half of 10k cost); PnL = 5000; tax = 750.
    # Cash 10000 - 750 = 9250; buy OFF 9250; QLD remains 10000.
    # Net NAV bar 6 = 10000 (QLD) + 9250 (OFF) = 19250.
    final_net = result["net_equity"].iloc[-1]
    assert final_net == pytest.approx(19_250.0, rel=0.01)
    assert result["tax_paid_total"] == pytest.approx(750.0, rel=0.01)
    assert result["n_taxable_swings"] == 1


def test_per_swing_never_better_than_annual_when_losses_exist():
    """Pre-registered invariant from spec §9: Model 2 (annual) >= Model 1
    (per-swing) in final net equity, by construction (intra-year loss offset
    can only help). Tested with a strategy that has both winning and losing
    swings within the same calendar year."""
    from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing
    from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

    dates = pd.date_range("2020-01-01", periods=200, freq="D")
    # Whipsaw: alternating swings, mostly losing then winning within same year
    np_rng = np.random.default_rng(seed=42)
    rets_qld = np_rng.normal(0.0005, 0.02, 200)  # daily, mean ~0.05%
    rets_off = np.zeros(200)
    asset_returns = pd.DataFrame({"QLD": rets_qld, "OFF": rets_off}, index=dates)

    # Alternate ON/OFF every 20 bars
    pos_qld = [(1.0 if (i // 20) % 2 == 0 else 0.0) for i in range(200)]
    pos_off = [1.0 - p for p in pos_qld]
    positions = pd.DataFrame({"QLD": pos_qld, "OFF": pos_off}, index=dates)

    # Model 1
    m1 = simulate_per_swing(positions, asset_returns, 10_000.0, 0.15)

    # Model 2: gross equity → annual_realize
    strat_returns = (positions.shift(1) * asset_returns).sum(axis=1).dropna()
    gross_equity = (1.0 + strat_returns).cumprod() * 10_000.0
    m2_equity = apply_annual_darf(
        gross_equity, strat_returns, mode="annual_realize", initial=10_000.0,
    )

    m1_final = m1["net_equity"].iloc[-1]
    m2_final = m2_equity.iloc[-1]

    # Annual >= per-swing (loss offset can only help, never hurt)
    assert m2_final >= m1_final - 0.5  # tolerance for fp noise / single-year edge cases


def _write_fake_verdict(tmp_path, iter_id, tier, datetime_utc, configs_with_scores):
    """Helper: write a minimal verdict.json fixture under tmp_path."""
    import json
    iter_dir = tmp_path / "runs/original" / iter_id
    iter_dir.mkdir(parents=True, exist_ok=True)
    verdict = {
        "iter": iter_id,
        "tier": tier,
        "datetime_utc": datetime_utc,
        "results": [
            {
                "config_name": name,
                "score_breakdown": {"total": float(score), "tier_label": "STRONG"},
                "metrics_gross": {"lh_56y": {"sharpe": float(sharpe)}},
            }
            for name, score, sharpe in configs_with_scores
        ],
    }
    (iter_dir / "verdict.json").write_text(json.dumps(verdict))


def test_select_top10_excludes_t2_static(tmp_path):
    from studies.letf_rotation_hunt.analyses.tax_comparison.select_top10 import select_top10

    _write_fake_verdict(tmp_path, "001", "T1c", "2026-05-06T10:00:00+00:00",
                        [("qld_sma200_zroz", 61, 0.75)])
    _write_fake_verdict(tmp_path, "005", "T2a", "2026-05-06T11:00:00+00:00",
                        [("hfea_55_45", 70, 0.65)])  # T2 → excluded
    _write_fake_verdict(tmp_path, "014", "T3d", "2026-05-06T12:00:00+00:00",
                        [("qld_voteK2", 78, 0.85)])

    top = select_top10(iterations_root=tmp_path / "runs/original")
    names = [t["config_name"] for t in top]
    assert "hfea_55_45" not in names
    assert {"qld_sma200_zroz", "qld_voteK2"} <= set(names)


def test_select_top10_dedup_keeps_latest_iter(tmp_path):
    from studies.letf_rotation_hunt.analyses.tax_comparison.select_top10 import select_top10

    # Same config name in two iters; later iter has different (lower) score
    _write_fake_verdict(tmp_path, "014", "T3d", "2026-05-06T10:00:00+00:00",
                        [("qld_voteK2", 78, 0.85)])
    _write_fake_verdict(tmp_path, "022", "T3d", "2026-05-06T15:00:00+00:00",
                        [("qld_voteK2", 82, 0.85)])  # later, higher score

    top = select_top10(iterations_root=tmp_path / "runs/original")
    assert len(top) == 1
    assert top[0]["config_name"] == "qld_voteK2"
    assert top[0]["score"] == pytest.approx(82.0)
    assert top[0]["iter_id"] == "022"


def test_select_top10_ranks_by_score_desc_with_sharpe_tiebreaker(tmp_path):
    from studies.letf_rotation_hunt.analyses.tax_comparison.select_top10 import select_top10

    _write_fake_verdict(tmp_path, "001", "T1c", "2026-05-06T10:00:00+00:00",
                        [("a", 70, 0.80), ("b", 80, 0.70), ("c", 80, 0.90)])

    top = select_top10(iterations_root=tmp_path / "runs/original")
    names = [t["config_name"] for t in top]
    # Score 80 ties: c (sharpe 0.90) before b (sharpe 0.70); a last
    assert names == ["c", "b", "a"]


def test_select_top10_caps_at_ten(tmp_path):
    from studies.letf_rotation_hunt.analyses.tax_comparison.select_top10 import select_top10

    configs = [(f"cfg{i:02d}", 50 + i, 0.5 + 0.01*i) for i in range(15)]
    _write_fake_verdict(tmp_path, "001", "T1c", "2026-05-06T10:00:00+00:00", configs)

    top = select_top10(iterations_root=tmp_path / "runs/original")
    assert len(top) == 10
    # Top by score desc: cfg14 (64) ... cfg05 (55)
    assert top[0]["config_name"] == "cfg14"
    assert top[-1]["config_name"] == "cfg05"


def test_dispatcher_t3_exposes_positions_and_asset_returns():
    """Smoke: T3 dispatcher's _run_single_composite_config must return
    `_positions` (DataFrame) and `_asset_returns_aligned` (DataFrame) so that
    tax_comparison can simulate per-swing on the actual position trajectory."""
    from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily
    from studies.letf_rotation_hunt.runners.run_iter_t3 import _run_single_composite_config

    cfg = {
        "name": "qld_vote_k2_off_zroz",
        "on_asset": "QLD",
        "off_asset": "ZROZ",
        "signal_type": "vote_of_k",
        "k": 2,
    }
    ffr_daily = load_ffr_daily()
    result = _run_single_composite_config(
        cfg, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=1,
    )
    assert "_positions" in result, "dispatcher must return _positions DataFrame"
    assert "_asset_returns_aligned" in result, "dispatcher must return _asset_returns_aligned DataFrame"
    pos = result["_positions"]
    rets = result["_asset_returns_aligned"]
    assert set(pos.columns) == set(rets.columns)
    assert pos.index.equals(rets.index)
    assert {"QLD", "ZROZ"} <= set(pos.columns)


def test_reconstruct_t3_canonical_winner():
    """E2E: reconstruct the canonical T3d K=2 config from its verdict and
    return positions, asset_returns_aligned, gross strategy_returns, gross equity."""
    from pathlib import Path
    from studies.letf_rotation_hunt.analyses.tax_comparison.reconstruct import reconstruct_strategy

    selected = {
        "config_name": "qld_vote_k2_off_zroz",
        "tier": "T3d",
        "iter_id": "014-2026-05-06-T3d-vote-of-k",
        "source_iter_path": str(Path("studies/letf_rotation_hunt/runs/original/014-2026-05-06-T3d-vote-of-k").resolve()),
    }
    out = reconstruct_strategy(selected, datasets=["lh_56y"])
    assert "positions" in out
    assert "asset_returns_aligned" in out
    assert "strategy_returns" in out
    assert "gross_equity" in out
    assert {"QLD", "ZROZ"} <= set(out["positions"].columns)
    # Canonical winner Sharpe lh_56y ≈ 0.853
    sharpe = out["gross_equity"].pct_change().dropna().mean() / out["gross_equity"].pct_change().dropna().std() * (252 ** 0.5)
    assert sharpe > 0.7  # broad sanity, not exact match


def test_plot_per_strategy_smoke(tmp_path):
    from studies.letf_rotation_hunt.analyses.tax_comparison.plot_tax_comparison import (
        plot_per_strategy_equity, plot_per_strategy_ratio,
    )

    dates = pd.date_range("2010-01-01", periods=500, freq="B")
    idx = np.arange(500)
    eq_gross = pd.Series((1.0008 ** idx) * 10_000.0, index=dates)
    eq_m1 = eq_gross * 0.85
    eq_m2 = eq_gross * 0.92
    eq_spy = pd.Series((1.0004 ** idx) * 10_000.0, index=dates)

    out_eq = tmp_path / "01_test_equity.png"
    plot_per_strategy_equity(
        config_name="test_strategy",
        eq_gross=eq_gross, eq_per_swing=eq_m1, eq_annual_net=eq_m2,
        eq_spy=eq_spy, out_path=out_eq,
    )
    assert out_eq.exists()

    out_ratio = tmp_path / "01_test_ratio.png"
    plot_per_strategy_ratio(
        config_name="test_strategy",
        eq_gross=eq_gross, eq_per_swing=eq_m1, eq_annual_net=eq_m2,
        eq_spy=eq_spy, out_path=out_ratio,
    )
    assert out_ratio.exists()
