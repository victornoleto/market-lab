"""Tests for the stop-loss variant expander."""

from __future__ import annotations

import pytest

from ai_trade.backtest.grid.stop_loss_variants import (
    DEFAULT_COOLDOWNS,
    DEFAULT_RECOVERY_PCTS,
    DEFAULT_STOP_LEVELS,
    Variant,
    expand_stop_loss_variants,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
)


def _top_k(k: int = 3) -> list[EMASMAThresholdConfig]:
    return [
        EMASMAThresholdConfig(
            filter="EMA", lookback=100 + i * 50, threshold_pct=0.05,
            buy_leverage=2.0 + (i % 2), sell_leverage=0.0,
        )
        for i in range(k)
    ]


class TestExpandCount:
    def test_default_axes_produce_43_variants_per_base(self):
        top = _top_k(3)
        variants = expand_stop_loss_variants(top)
        # 1 baseline + 6 stops × (1 next + 3 cooldowns + 3 recoveries)
        #   = 1 + 6 × 7 = 43 per base.
        assert len(DEFAULT_STOP_LEVELS) == 6
        assert len(DEFAULT_COOLDOWNS) == 3
        assert len(DEFAULT_RECOVERY_PCTS) == 3
        assert len(variants) == 3 * 43

    def test_unique_variant_ids_per_base(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(top)
        ids = [v.variant_id for v in variants]
        assert len(set(ids)) == len(ids)

    def test_first_variant_is_baseline_none_stop(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(top)
        assert variants[0].stop_cfg.stop_loss_pct is None
        assert variants[0].stop_tag == "baseline"

    def test_base_rank_is_one_indexed(self):
        top = _top_k(2)
        variants = expand_stop_loss_variants(top)
        ranks = {v.base_rank for v in variants}
        assert ranks == {1, 2}


class TestVariantIdTags:
    def test_next_signal_tag(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(top)
        # Filter out the None-stop baseline (which defaults to next_signal
        # mode but represents no stop at all).
        nexts = [
            v for v in variants
            if v.stop_cfg.reentry_mode == "next_signal"
            and v.stop_cfg.stop_loss_pct is not None
        ]
        tags = {v.stop_tag for v in nexts}
        assert tags == {f"sl{int(round(sl*100))}_next" for sl in DEFAULT_STOP_LEVELS}

    def test_cooldown_tag_includes_bars(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(top)
        cools = [v for v in variants if v.stop_cfg.reentry_mode == "time_cooldown"]
        # Expect 6 stops × 3 cooldowns = 18 variants.
        assert len(cools) == 18
        some = next(v for v in cools if v.stop_cfg.stop_loss_pct == 0.25
                    and v.stop_cfg.reentry_param == 63)
        assert some.stop_tag == "sl25_cool63"

    def test_recovery_tag_includes_pct(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(top)
        recs = [v for v in variants if v.stop_cfg.reentry_mode == "recovery_trigger"]
        assert len(recs) == 18
        some = next(v for v in recs if v.stop_cfg.stop_loss_pct == 0.30
                    and v.stop_cfg.reentry_param == 0.10)
        assert some.stop_tag == "sl30_rec10"


class TestCustomAxes:
    def test_custom_axes_produce_expected_count(self):
        top = _top_k(1)
        variants = expand_stop_loss_variants(
            top,
            stop_levels=(0.25,),
            cooldowns=(63,),
            recovery_pcts=(0.10,),
        )
        # 1 baseline + 1 stop × (1 next + 1 cooldown + 1 recovery) = 4.
        assert len(variants) == 4
