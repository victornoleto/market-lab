from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.lib.validation import (
    gate_bootstrap,
    gate_cross_lib,
    gate_dsr,
    gate_fwd_stress,
    gate_oos,
    gate_pbo,
    gate_walk_forward,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1990-01-01", periods=n)


def _drift_series(n: int, mu: float, sigma: float, seed: int) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(mu + sigma * rng.standard_normal(n), index=_days(n))


def test_gate_cross_lib_pandas_vs_numpy_agree() -> None:
    s = _drift_series(2000, 0.0004, 0.01, seed=0)

    g = gate_cross_lib(s)

    # Two independent CAGR computations of the SAME series must agree to ~0.
    assert g["delta_pp"] < 1e-6
    assert g["pass_gate"] is True


def test_gate_dsr_fails_at_large_n_trials() -> None:
    # A mediocre-Sharpe series that is "significant" at 2 trials but not after
    # correcting for thousands of trials (selection bias).
    s = _drift_series(4000, 0.0004, 0.01, seed=1)

    few = gate_dsr(s, n_trials=2)
    many = gate_dsr(s, n_trials=1_000_000)

    assert many["p_value"] > few["p_value"]
    assert many["pass_gate"] is False


def test_gate_walk_forward_passes_when_strategy_beats_benchmark() -> None:
    n = 1200
    bench = _drift_series(n, 0.0002, 0.005, seed=2)
    strat = bench + 0.0010  # strategy beats benchmark every day -> every window

    g = gate_walk_forward(strat, bench, is_size=60, oos_size=30, step=30)

    assert g["n_windows"] >= 8
    assert g["windows_beat_benchmark"] == g["n_windows"]
    assert g["pass_gate"] is True


def test_gate_walk_forward_rejects_when_strategy_lags_benchmark() -> None:
    n = 1200
    bench = _drift_series(n, 0.0006, 0.005, seed=3)
    strat = bench - 0.0010  # strategy loses to benchmark every window

    g = gate_walk_forward(strat, bench, is_size=60, oos_size=30, step=30)

    assert g["windows_beat_benchmark"] == 0
    assert g["pass_gate"] is False


def test_gate_oos_pass_and_fail() -> None:
    n = 1000
    bench = pd.Series(0.0, index=_days(n))
    good = _drift_series(n, 0.0008, 0.006, seed=4)
    bad = _drift_series(n, -0.0008, 0.006, seed=5)

    assert gate_oos(good, bench)["pass_gate"] is True
    assert gate_oos(bad, bench)["pass_gate"] is False


def test_gate_fwd_stress_uses_post_cutoff_block() -> None:
    idx = pd.bdate_range("2015-01-01", periods=3000)
    pre = np.full(1500, -0.001)        # bad before cutoff
    post = np.full(1500, 0.001)        # good after cutoff
    s = pd.Series(np.concatenate([pre, post]), index=idx)

    g = gate_fwd_stress(s, cutoff="2020-01-01")

    assert g["n_obs"] > 0
    assert g["pass_gate"] is True


def test_gate_bootstrap_ci_low_sign() -> None:
    strong = _drift_series(3000, 0.0010, 0.004, seed=6)   # high, stable Sharpe
    noise = _drift_series(3000, 0.0, 0.01, seed=7)         # zero-mean

    assert gate_bootstrap(strong, n_resamples=1000)["pass_gate"] is True
    assert gate_bootstrap(noise, n_resamples=1000)["pass_gate"] is False


def test_gate_pbo_wiring() -> None:
    rng = np.random.default_rng(8)
    matrix = rng.standard_normal((600, 20))  # 600 periods x 20 configs

    g = gate_pbo(matrix)

    assert 0.0 <= g["pbo"] <= 1.0
    assert g["pass_gate"] == (g["pbo"] < 0.5)
