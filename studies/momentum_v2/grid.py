"""Build the broad-phase strategy grid from a config mapping.

Each axis is an explicit, accounted-for degree of freedom `[advances_fin_ml,
p.273-275]`. Score modes that ignore the lookback profile (``mom_12_1``,
``clenow_trend``) are emitted once instead of duplicated across profiles, so the
grid does not over-count trivially identical configs.
"""

from __future__ import annotations

from typing import Any

from studies.momentum_v2.core import (
    LookbackProfile,
    StrategyConfig,
    make_config_name,
    parse_lookback_profile,
)

# Score modes whose value does not depend on the lookback profile.
_LOOKBACK_INDEPENDENT = {"mom_12_1", "clenow_trend"}


def _as_list(value: Any) -> list:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _offsets_for(rebalance_months: int, raw: Any) -> list[int]:
    if isinstance(raw, str) and raw.strip().lower() == "all":
        return list(range(rebalance_months))
    return [int(off) % rebalance_months for off in _as_list(raw)]


def lookback_profiles(config_grid: dict[str, Any]) -> list[LookbackProfile]:
    raw = config_grid.get("lookback_profiles", ["1_3_6_12"])
    return [parse_lookback_profile(token) for token in _as_list(raw)]


def build_strategy_grid(
    config_grid: dict[str, Any],
    *,
    universe: str,
    assets: tuple[str, ...],
    vol_window_days: int = 126,
    trend_window_days: int = 126,
) -> list[StrategyConfig]:
    """Expand the cross-product of grid axes into StrategyConfig objects."""
    score_modes = _as_list(config_grid.get("score_modes", ["raw_13612"]))
    profiles = lookback_profiles(config_grid)
    top_ns = [int(x) for x in _as_list(config_grid.get("top_n", [5]))]
    rebalance_months = [int(x) for x in _as_list(config_grid.get("rebalance_months", [3]))]
    weight_modes = _as_list(config_grid.get("weight_modes", ["equal"]))
    abs_filters = [bool(x) for x in _as_list(config_grid.get("absolute_filter", [False]))]
    offsets_raw = config_grid.get("rebalance_offsets", [0])

    configs: list[StrategyConfig] = []
    seen: set[str] = set()
    for score_mode in score_modes:
        score_profiles = profiles[:1] if score_mode in _LOOKBACK_INDEPENDENT else profiles
        for profile in score_profiles:
            for top_n in top_ns:
                for months in rebalance_months:
                    for offset in _offsets_for(months, offsets_raw):
                        for weight_mode in weight_modes:
                            for absolute_filter in abs_filters:
                                mechanism = _mechanism(score_mode, weight_mode, absolute_filter)
                                name = make_config_name(
                                    universe, mechanism, profile.label, top_n, months, offset
                                )
                                if name in seen:
                                    continue
                                seen.add(name)
                                configs.append(
                                    StrategyConfig(
                                        name=name,
                                        universe=universe,
                                        assets=assets,
                                        top_n=top_n,
                                        rebalance_months=months,
                                        rebalance_offset=offset,
                                        score_mode=score_mode,  # type: ignore[arg-type]
                                        lookback=profile,
                                        weight_mode=weight_mode,  # type: ignore[arg-type]
                                        absolute_filter=absolute_filter,
                                        vol_window_days=vol_window_days,
                                        trend_window_days=trend_window_days,
                                    )
                                )
    return configs


def _mechanism(score_mode: str, weight_mode: str, absolute_filter: bool) -> str:
    if absolute_filter:
        return f"{score_mode}_abs_cash"
    if weight_mode == "inverse_vol":
        return f"{score_mode}_inverse_vol"
    return score_mode
