"""Tests for the DSR cumulative re-computation script.

Citation: spec §5.3 (docs/specs/2026-05-08-t5-expansion-design.md);
[advances_fin_ml, p.208-211].
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import dsr_recompute_cumulative as dsr_rc


def _make_iter_dir(tmp: Path, name: str, returns: pd.Series, p_old: float) -> Path:
    d = tmp / name
    d.mkdir(parents=True)
    returns.to_csv(d / "strategy_returns.csv", header=["ret"])
    verdict = {
        "results": [{
            "config_name": name,
            "_strategy_returns_csv": "strategy_returns.csv",
            "gates": {"g2_dsr_p_cumulative": p_old},
        }],
    }
    (d / "verdict.json").write_text(json.dumps(verdict))
    return d


def test_recompute_writes_v2_key_and_increases_p(tmp_path):
    rng = np.random.default_rng(0)
    rets = pd.Series(
        rng.normal(0.0005, 0.012, 1000),
        index=pd.date_range("2010-01-04", periods=1000, freq="B"),
    )
    iter_a = _make_iter_dir(tmp_path / "iters", "iter_001", rets, p_old=0.04)
    dsr_rc.recompute_all(
        iters_root=tmp_path / "iters", n_trials_new=426,
        v2_key="g2_dsr_p_cumulative_v2_post_t5_expansion",
    )
    new_verdict = json.loads((iter_a / "verdict.json").read_text())
    p_v2 = new_verdict["results"][0]["gates"]["g2_dsr_p_cumulative_v2_post_t5_expansion"]
    assert p_v2 >= 0.04, "expected p-value to grow when N grows"
    assert new_verdict["results"][0]["gates"]["g2_dsr_p_cumulative"] == 0.04, "old key preserved"
