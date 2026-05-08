# studies/letf_rotation_hunt/tests/test_run_iter_t5_extended.py
"""Tests for run_iter_t5_extended (T5b/T5d dispatcher).

Citation: spec §3.4 (docs/specs/2026-05-08-t5-expansion-design.md).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from studies.letf_rotation_hunt import run_iter_t5, run_iter_t5_extended


def _minimal_config(name: str, extra: dict | None = None) -> dict:
    cfg = {
        "name": name,
        "pool": ["QLD"],
        "off_asset": "ZROZ",
        "sigma_target": 0.25,
        "idm": 1.0,
        "position_inertia": 0.10,
    }
    if extra:
        cfg.update(extra)
    return cfg


def test_extended_with_default_kwargs_matches_baseline(tmp_path):
    """Without forecast_type/weighting_scheme keys, extended dispatch routes to
    baseline _run_single_voltarget_config and produces equivalent verdict."""
    cfg = {
        "iter": "test_t5_compat",
        "tier": "T5a",
        "configs_tested": [_minimal_config("baseline")],
        "datasets": ["lh_56y"],
        "cumulative_n_trials_at_iter": 0,
    }
    verdict_a: dict = {"results": []}
    verdict_b: dict = {"results": []}
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    out_a.mkdir(parents=True, exist_ok=True)
    out_b.mkdir(parents=True, exist_ok=True)
    run_iter_t5.run(cfg, verdict_a, out_a)
    run_iter_t5_extended.run(cfg, verdict_b, out_b)
    sharpe_a = verdict_a["results"][0]["metrics_gross"]["lh_56y"]["sharpe"]
    sharpe_b = verdict_b["results"][0]["metrics_gross"]["lh_56y"]["sharpe"]
    assert abs(sharpe_a - sharpe_b) < 1e-9, (sharpe_a, sharpe_b)


def test_extended_carry_only_runs(tmp_path):
    cfg = {
        "iter": "test_t5b_carry",
        "tier": "T5b",
        "configs_tested": [_minimal_config(
            "carry_only_qld",
            {"forecast_type": "carry_only"},
        )],
        "datasets": ["lh_56y"],
        "cumulative_n_trials_at_iter": 0,
    }
    verdict: dict = {"results": []}
    run_iter_t5_extended.run(cfg, verdict, tmp_path)
    res = verdict["results"][0]
    assert "error" not in res, res.get("error")
    assert res["metrics_gross"]["lh_56y"]["sharpe"] is not None


def test_extended_hrp_weighting_runs(tmp_path):
    cfg = {
        "iter": "test_t5d_hrp",
        "tier": "T5d",
        "configs_tested": [_minimal_config(
            "hrp_multi4",
            {"pool": ["UPRO", "QLD", "UGL", "TMF"], "weighting_scheme": "hrp"},
        )],
        "datasets": ["lh_56y"],
        "cumulative_n_trials_at_iter": 0,
    }
    verdict: dict = {"results": []}
    run_iter_t5_extended.run(cfg, verdict, tmp_path)
    res = verdict["results"][0]
    assert "error" not in res, res.get("error")
