"""Grid construction for momentum strategy families."""

from __future__ import annotations

from typing import Any

from studies.momentum.config import as_bool_list, as_int_list, as_str_list
from studies.momentum.strategies import StrategyConfig


def build_strategy_grid(
    config: dict[str, Any], universe_assets: dict[str, tuple[str, ...]]
) -> list[StrategyConfig]:
    """Build explicit strategy configs from YAML settings and filtered assets."""
    grid = config.get("grid", {})
    universes = as_str_list(grid.get("universes", []))
    top_values = as_int_list(grid.get("top_n", [10]))
    rebalance_values = as_int_list(grid.get("rebalance_months", [1]))
    score_modes = as_str_list(grid.get("score_modes", ["raw_13612"]))
    weight_modes = as_str_list(grid.get("weight_modes", ["equal"]))
    absolute_values = as_bool_list(grid.get("absolute_filter", [False]))
    staggered_values = as_bool_list(grid.get("staggered_offsets", [False]))
    weight_cap = float(grid.get("weight_cap", 0.25))
    out: list[StrategyConfig] = []
    for universe in universes:
        assets = universe_assets.get(universe, ())
        if not assets:
            continue
        for score_mode in score_modes:
            for weight_mode in weight_modes:
                for absolute in absolute_values:
                    for top_n in top_values:
                        if top_n > len(assets):
                            continue
                        for rebalance_months in rebalance_values:
                            for staggered in staggered_values:
                                offsets = [0] if staggered else offsets_for(grid, rebalance_months)
                                for offset in offsets:
                                    name = make_strategy_name(
                                        universe,
                                        score_mode,
                                        weight_mode,
                                        top_n,
                                        rebalance_months,
                                        offset,
                                        absolute,
                                        staggered,
                                    )
                                    out.append(
                                        StrategyConfig(
                                            name=name,
                                            universe=universe,
                                            assets=assets,
                                            score_mode=score_mode,  # type: ignore[arg-type]
                                            top_n=top_n,
                                            rebalance_months=rebalance_months,
                                            rebalance_offset=offset,
                                            weight_mode=weight_mode,  # type: ignore[arg-type]
                                            absolute_filter=absolute,
                                            staggered_offsets=staggered,
                                            weight_cap=weight_cap,
                                        )
                                    )
    return out


def offsets_for(grid: dict[str, Any], rebalance_months: int) -> list[int]:
    raw = grid.get("rebalance_offsets", "all")
    if raw == "all":
        return list(range(rebalance_months))
    values = as_int_list(raw)
    return [value for value in values if 0 <= value < rebalance_months]


def make_strategy_name(
    universe: str,
    score_mode: str,
    weight_mode: str,
    top_n: int,
    rebalance_months: int,
    offset: int,
    absolute: bool,
    staggered: bool,
) -> str:
    suffix = []
    if absolute:
        suffix.append("abs")
    if staggered:
        suffix.append("stag")
    tail = "_" + "_".join(suffix) if suffix else ""
    return (
        f"mom_{universe}_{score_mode}_{weight_mode}_top{top_n}_"
        f"reb{rebalance_months}_off{offset}{tail}"
    )
