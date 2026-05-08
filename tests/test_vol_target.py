"""Unit tests for ``backtest.metrics.vol_target`` — Phase 3.5b Task 7f."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.metrics.vol_target import (
    CANONICAL_LOOKBACKS,
    CANONICAL_MAX_LEVERAGES,
    CANONICAL_TARGET_VOL,
    VolTargetComparison,
    VolTargetConfig,
    VolTargetRow,
    apply_vol_target,
    compare_vol_target_configs,
    render_vol_target_markdown,
    select_default_sizing,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _bdate_index(n: int, start: str = "2010-01-04") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n, freq="B")


def _gaussian_returns(n: int, seed: int, sigma_daily: float = 0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(
        rng.normal(0.0, sigma_daily, size=n),
        index=_bdate_index(n),
        name="r",
    )


# ---------------------------------------------------------------------------
# Canonical knobs
# ---------------------------------------------------------------------------


def test_canonical_knobs_match_spec() -> None:
    assert CANONICAL_TARGET_VOL == 0.10
    assert CANONICAL_LOOKBACKS == (63, 126, 252)
    assert CANONICAL_MAX_LEVERAGES == (1.5, 2.0, 3.0)


# ---------------------------------------------------------------------------
# apply_vol_target
# ---------------------------------------------------------------------------


class TestApplyVolTarget:
    def test_rejects_non_positive_target(self) -> None:
        r = _gaussian_returns(300, 0)
        with pytest.raises(ValueError, match="target_vol"):
            apply_vol_target(r, target_vol=0.0, lookback=63, max_leverage=2.0)
        with pytest.raises(ValueError, match="target_vol"):
            apply_vol_target(r, target_vol=-0.1, lookback=63, max_leverage=2.0)

    def test_rejects_small_lookback(self) -> None:
        r = _gaussian_returns(300, 0)
        with pytest.raises(ValueError, match="lookback"):
            apply_vol_target(r, target_vol=0.10, lookback=1, max_leverage=2.0)

    def test_rejects_non_positive_cap(self) -> None:
        r = _gaussian_returns(300, 0)
        with pytest.raises(ValueError, match="max_leverage"):
            apply_vol_target(r, target_vol=0.10, lookback=63, max_leverage=0.0)

    def test_rejects_too_few_bars(self) -> None:
        r = _gaussian_returns(30, 0)
        with pytest.raises(ValueError, match="need >"):
            apply_vol_target(r, target_vol=0.10, lookback=63, max_leverage=2.0)

    def test_no_lookahead_first_lookback_dropped(self) -> None:
        r = _gaussian_returns(400, 0)
        scaled, scale = apply_vol_target(
            r, target_vol=0.10, lookback=63, max_leverage=2.0
        )
        # Output starts at bar index 63 (0-indexed) of the input.
        assert len(scaled) == len(r) - 63
        assert scaled.index[0] == r.index[63]
        assert scale.index[0] == r.index[63]
        # No NaN in output.
        assert not scaled.isna().any()
        assert not scale.isna().any()

    def test_scale_targets_vol_on_stationary_input(self) -> None:
        # With stationary σ_daily = 0.01, realised ann vol ≈ 0.1587.
        # Target 0.10 → scale should cluster around 0.10/0.1587 ≈ 0.63.
        r = _gaussian_returns(5000, 42, sigma_daily=0.01)
        scaled, scale = apply_vol_target(
            r, target_vol=0.10, lookback=252, max_leverage=3.0
        )
        # Scale clustered near the target ratio.
        expected_ratio = 0.10 / (0.01 * np.sqrt(252))
        assert abs(float(scale.median()) - expected_ratio) < 0.1
        # Realised ann vol of the scaled series approaches 0.10.
        realised = float(scaled.std(ddof=0) * np.sqrt(252))
        assert abs(realised - 0.10) < 0.015

    def test_cap_hit_frac_when_input_is_quiet(self) -> None:
        # Very low vol → scale wants to be large → should hit cap.
        r = _gaussian_returns(5000, 123, sigma_daily=0.001)
        scaled, scale = apply_vol_target(
            r, target_vol=0.10, lookback=252, max_leverage=2.0
        )
        # Almost every scale should be capped.
        hit = np.isclose(scale.to_numpy(float), 2.0, atol=1e-9).mean()
        assert hit > 0.95

    def test_zero_vol_window_maps_to_cap(self) -> None:
        # 300 zeros then a spike: rolling std = 0 over the zeros,
        # so scale should be set to cap for the spike bar.
        idx = _bdate_index(301)
        vals = np.zeros(301)
        vals[-1] = 0.01
        r = pd.Series(vals, index=idx, name="r")
        # Append one extra bar so we can observe scale for a post-zero bar.
        # Our guarantee: when σ̂_{t-1} == 0, scale = max_leverage.
        scaled, scale = apply_vol_target(
            r, target_vol=0.10, lookback=100, max_leverage=2.5
        )
        # The first valid scale corresponds to bar 100; σ̂_{99} over [0..99]
        # is 0, so scale[100] must equal the cap.
        assert np.isclose(float(scale.iloc[0]), 2.5)

    def test_scale_is_bounded_by_cap(self) -> None:
        r = _gaussian_returns(500, 7, sigma_daily=0.0005)
        scaled, scale = apply_vol_target(
            r, target_vol=0.10, lookback=63, max_leverage=1.5
        )
        assert float(scale.max()) <= 1.5 + 1e-12
        assert float(scale.min()) >= 0.0


# ---------------------------------------------------------------------------
# compare_vol_target_configs
# ---------------------------------------------------------------------------


class TestCompareVolTargetConfigs:
    def test_row_count_matches_grid(self) -> None:
        r = _gaussian_returns(800, 1, sigma_daily=0.01)
        is_end = r.index[400]
        configs = (
            VolTargetConfig(0.10, 63, 2.0),
            VolTargetConfig(0.10, 252, 3.0),
        )
        cmp = compare_vol_target_configs(r, is_end=is_end, configs=configs)
        # baseline + 2 challengers.
        assert len(cmp.rows) == 3
        assert cmp.rows[0].label == "baseline_ew"
        assert cmp.rows[1].label == "vt_target=0.10_L63_cap2.0"
        assert cmp.rows[2].label == "vt_target=0.10_L252_cap3.0"

    def test_canonical_default_grid(self) -> None:
        r = _gaussian_returns(800, 1, sigma_daily=0.01)
        is_end = r.index[400]
        cmp = compare_vol_target_configs(r, is_end=is_end)
        # 1 baseline + 3 lookbacks × 3 caps = 10 rows.
        assert len(cmp.rows) == 1 + len(CANONICAL_LOOKBACKS) * len(
            CANONICAL_MAX_LEVERAGES
        )

    def test_baseline_has_scale_one(self) -> None:
        r = _gaussian_returns(500, 2, sigma_daily=0.01)
        is_end = r.index[250]
        cmp = compare_vol_target_configs(r, is_end=is_end)
        baseline = cmp.rows[0]
        assert baseline.scale_mean == 1.0
        assert baseline.scale_median == 1.0
        assert baseline.scale_cap_hit_frac == 0.0

    def test_dict_roundtrip_is_serialisable(self) -> None:
        r = _gaussian_returns(500, 3, sigma_daily=0.01)
        is_end = r.index[250]
        cmp = compare_vol_target_configs(r, is_end=is_end)
        payload = cmp.to_dict()
        import json

        # Must JSON-serialise — no NaN/∞ sneaking through dict-level.
        json.dumps(payload, allow_nan=False)


# ---------------------------------------------------------------------------
# select_default_sizing
# ---------------------------------------------------------------------------


def _make_row(
    label: str,
    oos_sharpe: float,
    oos_cagr_pct: float,
    **overrides: float,
) -> VolTargetRow:
    """Helper to build a row with only the fields the selector inspects."""
    base = dict(
        label=label,
        target_vol=0.10,
        lookback=63,
        max_leverage=2.0,
        bars=500,
        scale_mean=1.0,
        scale_median=1.0,
        scale_min=1.0,
        scale_max=1.0,
        scale_cap_hit_frac=0.0,
        full_sharpe=1.0,
        full_cagr_pct=10.0,
        full_volatility_ann_pct=10.0,
        full_max_drawdown_pct=10.0,
        is_sharpe=1.0,
        is_cagr_pct=10.0,
        oos_sharpe=oos_sharpe,
        oos_cagr_pct=oos_cagr_pct,
        oos_max_drawdown_pct=10.0,
        final_equity=2.0,
    )
    base.update(overrides)
    return VolTargetRow(**base)


class TestSelectDefaultSizing:
    def test_baseline_kept_when_no_challenger(self) -> None:
        rows = (_make_row("baseline_ew", 2.0, 25.0),)
        label, reason = select_default_sizing(rows)
        assert label == "baseline_ew"
        assert "kept" in reason

    def test_baseline_kept_when_sharpe_margin_missed(self) -> None:
        rows = (
            _make_row("baseline_ew", 2.0, 25.0),
            _make_row("vt_target=0.10_L63_cap2.0", 2.03, 30.0),  # ΔS=0.03 < 0.05
        )
        label, _ = select_default_sizing(rows)
        assert label == "baseline_ew"

    def test_baseline_kept_when_cagr_margin_missed(self) -> None:
        rows = (
            _make_row("baseline_ew", 2.0, 25.0),
            _make_row("vt_target=0.10_L63_cap2.0", 2.10, 25.5),  # ΔCAGR=0.5 < 1.0
        )
        label, _ = select_default_sizing(rows)
        assert label == "baseline_ew"

    def test_challenger_promoted_when_both_margins_exceeded(self) -> None:
        rows = (
            _make_row("baseline_ew", 2.0, 25.0),
            _make_row("vt_target=0.10_L63_cap2.0", 2.10, 27.0),
            _make_row("vt_target=0.10_L63_cap3.0", 2.20, 28.0),
        )
        label, reason = select_default_sizing(rows)
        assert label == "vt_target=0.10_L63_cap3.0"  # best among passers
        assert "promoted" in reason

    def test_unknown_incumbent_raises(self) -> None:
        rows = (_make_row("other", 2.0, 25.0),)
        with pytest.raises(ValueError, match="incumbent"):
            select_default_sizing(rows)

    def test_custom_margins_respected(self) -> None:
        rows = (
            _make_row("baseline_ew", 2.0, 25.0),
            _make_row("vt_target=0.10_L63_cap2.0", 2.02, 25.3),
        )
        # Loosen margins — should promote.
        label, _ = select_default_sizing(
            rows, sharpe_margin=0.01, cagr_margin_pct=0.2
        )
        assert label == "vt_target=0.10_L63_cap2.0"


# ---------------------------------------------------------------------------
# render_vol_target_markdown
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    def test_markdown_contains_title_and_default_block(self) -> None:
        r = _gaussian_returns(500, 9, sigma_daily=0.01)
        is_end = r.index[250]
        cmp = compare_vol_target_configs(r, is_end=is_end)
        md = render_vol_target_markdown(cmp)
        assert "Phase 3.5b Task 7f" in md
        assert "Default sizing" in md
        assert f"`{cmp.default_label}`" in md
        # One row for each config + baseline + header + separator.
        n_rows = len(cmp.rows)
        # Count data lines (after separator ---).
        lines = md.splitlines()
        sep_ix = next(i for i, l in enumerate(lines) if l.startswith("| ---"))
        data_rows = [l for l in lines[sep_ix + 1 :] if l.startswith("|")]
        assert len(data_rows) == n_rows
