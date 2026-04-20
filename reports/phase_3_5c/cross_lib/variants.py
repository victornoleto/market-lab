"""Declarative variants registry — all Plano B variants the harness can run."""
from __future__ import annotations

from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)

CANONICAL = ("2004-10-01", "2026-04-18")
EXTENDED = ("1986-01-02", "2026-04-18")
POST_2009 = ("2009-01-01", "2026-04-18")

_V4_LEGS = (
    LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
    LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
    LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
)

_V1_LEGS = (
    LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
    LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QQQ"),
    LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "GLD"),
)


def _make_threshold_variant(pp: float) -> VariantConfig:
    """Factory for threshold sweep variants."""
    return VariantConfig(
        variant_id=f"threshold_sweep_{int(pp)}pp",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=pp),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    )


VARIANTS: dict[str, VariantConfig] = {
    # --- Wave 1: flagship + legs ---
    "plano_b_v4_threshold_10": VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL, EXTENDED, POST_2009),
    ),
    "plano_b_v4_daily": VariantConfig(
        variant_id="plano_b_v4_daily",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    ),
    "leg_sso_only": VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[0],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL, EXTENDED, POST_2009),
    ),
    "leg_qld_only": VariantConfig(
        variant_id="leg_qld_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[1],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL,),
    ),
    "leg_ugl_only": VariantConfig(
        variant_id="leg_ugl_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[2],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL,),
    ),
    # --- Wave 2: decision validation ---
    "v1_fallback": VariantConfig(
        variant_id="v1_fallback",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V1_LEGS,
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    ),
    "2leg_ew": VariantConfig(
        variant_id="2leg_ew",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS[:2],  # SSO + QLD
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(0.5, 0.5),
        windows=(CANONICAL,),
    ),
    "threshold_sweep_5pp": _make_threshold_variant(5.0),
    "threshold_sweep_15pp": _make_threshold_variant(15.0),
    "threshold_sweep_25pp": _make_threshold_variant(25.0),
}


def wave_1_variants() -> list[VariantConfig]:
    return [
        VARIANTS["plano_b_v4_threshold_10"],
        VARIANTS["plano_b_v4_daily"],
        VARIANTS["leg_sso_only"],
        VARIANTS["leg_qld_only"],
        VARIANTS["leg_ugl_only"],
    ]


def wave_2_variants() -> list[VariantConfig]:
    return [
        VARIANTS["v1_fallback"],
        VARIANTS["2leg_ew"],
        VARIANTS["threshold_sweep_5pp"],
        VARIANTS["threshold_sweep_15pp"],
        VARIANTS["threshold_sweep_25pp"],
    ]


def wave_3_variants() -> list[VariantConfig]:
    """Populated in Task 27 when Wave 3 becomes active."""
    return []
