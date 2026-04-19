"""Tests for :mod:`ai_trade.backtest.grid.letf_rotation_grid`."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.letf_rotation_grid import (
    GridAxes,
    GridTrial,
    SplitDef,
    SplitMetrics,
    build_grid,
    run_letf_rotation_grid,
    slice_returns,
)
from ai_trade.backtest.strategies.letf_rotation import LETFRotationConfig


def _synthetic_spx(n_days: int = 2500, seed: int = 42) -> tuple[pd.Series, pd.Series]:
    """Build a mild-drift synthetic SPX return/price pair over n_days trading days."""
    rng = np.random.default_rng(seed)
    # small positive drift + 1%/day vol so the MA signal actually flips.
    returns = rng.normal(loc=0.0003, scale=0.010, size=n_days)
    # Inject a regime break near the middle to exercise ON/OFF transitions.
    mid = n_days // 2
    returns[mid : mid + 150] -= 0.003
    dates = pd.bdate_range("2005-01-03", periods=n_days)
    ret = pd.Series(returns, index=dates, name="ret")
    price = pd.Series((1 + ret).cumprod() * 100, index=dates, name="price")
    return ret, price


class TestGridAxes:
    def test_default_axes_16_configs(self) -> None:
        axes = GridAxes()
        assert axes.n_configs == 2 * 2 * 2 * 2 * 1

    def test_full_mandate_360(self) -> None:
        axes = GridAxes(
            filters=("SMA", "EMA"),
            lookbacks=(100, 125, 150, 200),
            bands=(0.0, 0.03, 0.05),
            leverages=(1.0, 2.0, 3.0),
            gold_weights=(0.0, 0.25, 0.50, 0.75, 1.0),
        )
        assert axes.n_configs == 360

    def test_empty_axis_rejected(self) -> None:
        with pytest.raises(ValueError, match="filters"):
            GridAxes(filters=())


class TestBuildGrid:
    def test_default_grid_is_16(self) -> None:
        configs = build_grid(GridAxes())
        assert len(configs) == 16
        assert all(isinstance(c, LETFRotationConfig) for c in configs)

    def test_build_grid_propagates_costs(self) -> None:
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(200,), bands=(0.0,),
                     leverages=(3.0,), gold_weights=(0.0,)),
            commission_bps=7.5, spread_bps=3.5,
            tax_rate=0.10, cash_rate_annual=0.04,
        )
        assert len(configs) == 1
        cfg = configs[0]
        assert cfg.commission_bps == 7.5
        assert cfg.spread_bps == 3.5
        assert cfg.tax_rate == 0.10
        assert cfg.cash_rate_annual == 0.04

    def test_build_grid_uniqueness(self) -> None:
        configs = build_grid(GridAxes())
        keys = {
            (c.filter, c.lookback, c.band_pct, c.leverage, c.gold_weight)
            for c in configs
        }
        assert len(keys) == len(configs)


class TestSliceReturns:
    def test_inclusive_bounds(self) -> None:
        dates = pd.bdate_range("2005-01-03", periods=10)
        s = pd.Series(range(10), index=dates)
        sliced = slice_returns(s, "2005-01-04", "2005-01-07")
        assert len(sliced) == 4
        assert sliced.iloc[0] == 1
        assert sliced.iloc[-1] == 4

    def test_start_after_end_rejected(self) -> None:
        dates = pd.bdate_range("2005-01-03", periods=10)
        s = pd.Series(range(10), index=dates)
        with pytest.raises(ValueError):
            slice_returns(s, "2005-01-10", "2005-01-05")

    def test_non_datetime_index_rejected(self) -> None:
        s = pd.Series([1, 2, 3])
        with pytest.raises(TypeError):
            slice_returns(s, "2005-01-01", "2005-12-31")


class TestRunGrid:
    def test_runs_small_grid_cash_only(self) -> None:
        ret, price = _synthetic_spx(n_days=1500)
        splits = [
            SplitDef("IS", str(ret.index[0].date()),
                     str(ret.index[999].date())),
            SplitDef("OOS", str(ret.index[1000].date()),
                     str(ret.index[-1].date())),
        ]
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(125,), bands=(0.0,),
                     leverages=(2.0,), gold_weights=(0.0,)),
        )
        trials = run_letf_rotation_grid(ret, price, splits, configs)
        assert len(trials) == 1
        t = trials[0]
        assert len(t.split_metrics) == 2
        is_m = t.by_split("IS")
        oos_m = t.by_split("OOS")
        assert is_m is not None and oos_m is not None
        assert is_m.n_bars == 1000
        assert oos_m.n_bars == 500
        assert np.isfinite(is_m.sharpe) and np.isfinite(oos_m.sharpe)
        assert is_m.final_equity > 0

    def test_full_default_axes(self) -> None:
        ret, price = _synthetic_spx(n_days=1200)
        splits = [SplitDef("IS", str(ret.index[0].date()),
                           str(ret.index[-1].date()))]
        configs = build_grid(GridAxes())
        trials = run_letf_rotation_grid(ret, price, splits, configs)
        assert len(trials) == 16
        assert all(len(t.split_metrics) == 1 for t in trials)

    def test_gold_weight_without_gold_returns_raises(self) -> None:
        ret, price = _synthetic_spx(n_days=500)
        splits = [SplitDef("ALL", str(ret.index[0].date()),
                           str(ret.index[-1].date()))]
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(100,), bands=(0.0,),
                     leverages=(2.0,), gold_weights=(0.5,)),
        )
        with pytest.raises(ValueError, match="gold_returns required"):
            run_letf_rotation_grid(ret, price, splits, configs)

    def test_gold_returns_passthrough(self) -> None:
        ret, price = _synthetic_spx(n_days=1200)
        gold = pd.Series(
            np.random.default_rng(0).normal(0.0001, 0.008, len(ret)),
            index=ret.index,
        )
        splits = [SplitDef("ALL", str(ret.index[0].date()),
                           str(ret.index[-1].date()))]
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(100,), bands=(0.0,),
                     leverages=(2.0,), gold_weights=(0.5,)),
        )
        trials = run_letf_rotation_grid(ret, price, splits, configs,
                                        gold_returns=gold)
        assert len(trials) == 1
        m = trials[0].split_metrics[0]
        assert m.n_bars == 1200

    def test_misaligned_indices_rejected(self) -> None:
        ret, price = _synthetic_spx(n_days=400)
        price_shifted = price.shift(1).dropna()
        splits = [SplitDef("ALL", str(ret.index[0].date()),
                           str(ret.index[-1].date()))]
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(50,), bands=(0.0,),
                     leverages=(2.0,), gold_weights=(0.0,)),
        )
        with pytest.raises(ValueError, match="share the same index"):
            run_letf_rotation_grid(ret, price_shifted, splits, configs)

    def test_trial_to_dict_roundtrip(self) -> None:
        ret, price = _synthetic_spx(n_days=600)
        splits = [SplitDef("IS", str(ret.index[0].date()),
                           str(ret.index[-1].date()))]
        configs = build_grid(
            GridAxes(filters=("SMA",), lookbacks=(100,), bands=(0.03,),
                     leverages=(2.0,), gold_weights=(0.0,)),
        )
        trials = run_letf_rotation_grid(ret, price, splits, configs)
        d = trials[0].to_dict()
        assert "config" in d and "splits" in d
        assert d["config"]["filter"] == "SMA"
        assert d["config"]["band_pct"] == 0.03
        assert len(d["splits"]) == 1
        assert d["splits"][0]["split_name"] == "IS"
