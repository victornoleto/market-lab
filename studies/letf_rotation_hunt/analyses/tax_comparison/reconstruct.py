"""Reconstruct a swing-rotation strategy's positions + returns from a verdict.

Given a select_top10 record (config_name + iter_id + tier), load the original
verdict.json + the matching configs_tested entry, then re-invoke the
appropriate tier dispatcher's `_run_single_*_config` to obtain the full per-bar
DataFrames needed for the tax simulators.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily

# Tier prefix → (module_name, function_name) — keep in sync with run_iter.py dispatch table.
_DISPATCHER_FOR_TIER: dict[str, tuple[str, str]] = {
    "T1": ("studies.letf_rotation_hunt.runners.run_iter_t1", "_run_single_config"),
    "T3": ("studies.letf_rotation_hunt.runners.run_iter_t3", "_run_single_composite_config"),
    "T4": ("studies.letf_rotation_hunt.runners.run_iter_t4", "_run_single_xs_config"),
    "T5": ("studies.letf_rotation_hunt.runners.run_iter_t5", "_run_single_voltarget_config"),
}


def reconstruct_strategy(
    selected_record: dict, datasets: list[str] | None = None,
) -> dict:
    """Rebuild a strategy's positions, asset returns, and gross equity curve.

    Parameters
    ----------
    selected_record : dict
        One entry from select_top10 output (must contain `config_name`, `tier`,
        `source_iter_path`).
    datasets : list[str] | None
        Datasets to compute metrics for; defaults to ["lh_56y"].

    Returns
    -------
    dict with keys:
        positions : pd.DataFrame
        asset_returns_aligned : pd.DataFrame
        strategy_returns : pd.Series
        gross_equity : pd.Series
        config_name : str
        tier : str
    """
    if datasets is None:
        datasets = ["lh_56y"]

    iter_path = Path(selected_record["source_iter_path"])
    verdict_path = iter_path / "verdict.json"
    verdict = json.loads(verdict_path.read_text())

    # Find config dict in configs_tested
    cfg_name = selected_record["config_name"]
    cfg = next(
        (c for c in verdict.get("configs_tested", []) if c.get("name") == cfg_name),
        None,
    )
    if cfg is None:
        raise ValueError(
            f"config {cfg_name!r} not found in {verdict_path} configs_tested"
        )

    tier = str(verdict.get("tier", ""))
    tier_prefix = tier[:2] if len(tier) >= 2 else tier
    if tier_prefix not in _DISPATCHER_FOR_TIER:
        raise ValueError(
            f"No dispatcher available for tier {tier!r} (expected T1/T3/T4/T5)"
        )

    module_name, func_name = _DISPATCHER_FOR_TIER[tier_prefix]
    import importlib
    mod = importlib.import_module(module_name)
    fn = getattr(mod, func_name)

    ffr_daily = load_ffr_daily()
    result = fn(cfg, datasets=datasets, ffr_daily=ffr_daily, n_trials_local=1)

    if "_positions" not in result or "_asset_returns_aligned" not in result:
        raise RuntimeError(
            f"Dispatcher {module_name}.{func_name} did not expose _positions / "
            f"_asset_returns_aligned. Run task 7 first."
        )

    return {
        "positions": result["_positions"],
        "asset_returns_aligned": result["_asset_returns_aligned"],
        "strategy_returns": result["_strategy_returns"],
        "gross_equity": result["_equity"],
        "config_name": cfg_name,
        "tier": tier,
    }
