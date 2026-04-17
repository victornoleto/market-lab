"""LETF Rotation grid — enumerate configs, run simulations, metric splits.

Thin orchestration layer around
:func:`ai_trade.backtest.strategies.letf_rotation.simulate_letf_rotation`.
Because LRS bypasses the bar engine, the generic
:class:`ai_trade.backtest.grid.runner.GridRunner` (which wraps
``BacktestResult``) is not a natural fit — we build a dedicated
iterator here.

Responsibilities
----------------

1. Expand the Phase 3 Lead B1 design grid into a list of
   :class:`ai_trade.backtest.strategies.letf_rotation.LETFRotationConfig`
   instances.
2. Given (spx_returns, spx_prices, optional gold_returns) and a list of
   date-indexed splits, run each config on each split and collect
   per-split metrics (Sharpe, CAGR, max DD, switches, final equity).
3. Leave gate evaluation (PBO / DSR / WF) to downstream CPCV + PBO
   steps (Lead B1c). This module just produces the raw per-split
   metrics matrix.

Citations
---------

* Split discipline (IS / OOS / Stress mutually exclusive):
  ``[advances_fin_ml, p.208-211]`` (CV leakage, PBO framework) and
  ``[leverage_for_the_long_run, p.13, Table 5]`` (Gayed's OOS test
  period 2001-2015).
* Pre-specified grid axes per mandate (filter/lookback/band/leverage/
  gold_weight): ``[leverage_for_the_long_run, p.14, Table 6]`` and
  ``[leverage_for_the_long_run, p.17, Table 8]``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, Literal, Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    RotationResult,
    simulate_letf_rotation,
)

log = logging.getLogger(__name__)

__all__ = [
    "GridAxes",
    "SplitDef",
    "SplitMetrics",
    "GridTrial",
    "build_grid",
    "run_letf_rotation_grid",
    "slice_returns",
]


@dataclass(frozen=True)
class GridAxes:
    """Axes for the LETF rotation grid (cartesian product).

    Default values reproduce the **smoke grid** (16 configs) used for
    Lead B1b-i validation. The **full 360-config grid** per mandate is:

    * filters = ("SMA", "EMA")
    * lookbacks = (100, 125, 150, 200)
    * bands = (0.0, 0.03, 0.05)
    * leverages = (1.0, 2.0, 3.0)
    * gold_weights = (0.0, 0.25, 0.50, 0.75, 1.0)

    2 × 4 × 3 × 3 × 5 = 360. Override the dataclass in the caller to
    switch between smoke and full grids without touching the library.
    """

    filters: tuple[Literal["SMA", "EMA"], ...] = ("SMA", "EMA")
    lookbacks: tuple[int, ...] = (125, 200)
    bands: tuple[float, ...] = (0.0, 0.05)
    leverages: tuple[float, ...] = (2.0, 3.0)
    gold_weights: tuple[float, ...] = (0.0,)

    def __post_init__(self) -> None:
        for name, axis in (
            ("filters", self.filters),
            ("lookbacks", self.lookbacks),
            ("bands", self.bands),
            ("leverages", self.leverages),
            ("gold_weights", self.gold_weights),
        ):
            if not axis:
                raise ValueError(f"{name} must be non-empty")

    @property
    def n_configs(self) -> int:
        return (
            len(self.filters)
            * len(self.lookbacks)
            * len(self.bands)
            * len(self.leverages)
            * len(self.gold_weights)
        )


@dataclass(frozen=True)
class SplitDef:
    """A date-indexed split of the simulation window.

    ``name`` is a human label ("IS", "OOS", "Stress"). ``start`` and
    ``end`` are inclusive pandas-parseable dates. Splits must be
    mutually exclusive — the caller is responsible for avoiding
    overlap (pipeline uses a ``check_mutual_exclusivity`` helper in
    downstream B1c when combined with CPCV).
    """

    name: str
    start: str
    end: str


@dataclass(frozen=True)
class SplitMetrics:
    """Performance metrics for a single (config, split) cell."""

    split_name: str
    n_bars: int
    sharpe: float
    cagr: float
    max_drawdown: float
    final_equity: float
    n_switches: int
    cum_cost_pct: float
    cum_tax_pct: float

    def to_dict(self) -> dict:
        return {
            "split_name": self.split_name,
            "n_bars": self.n_bars,
            "sharpe": self.sharpe,
            "cagr": self.cagr,
            "max_drawdown": self.max_drawdown,
            "final_equity": self.final_equity,
            "n_switches": self.n_switches,
            "cum_cost_pct": self.cum_cost_pct,
            "cum_tax_pct": self.cum_tax_pct,
        }


@dataclass
class GridTrial:
    """Result for one config across all splits."""

    config: LETFRotationConfig
    split_metrics: list[SplitMetrics] = field(default_factory=list)

    def by_split(self, name: str) -> SplitMetrics | None:
        for m in self.split_metrics:
            if m.split_name == name:
                return m
        return None

    def to_dict(self) -> dict:
        c = self.config
        return {
            "config": {
                "filter": c.filter,
                "lookback": c.lookback,
                "band_pct": c.band_pct,
                "leverage": c.leverage,
                "gold_weight": c.gold_weight,
                "annual_fee": c.annual_fee,
                "commission_bps": c.commission_bps,
                "spread_bps": c.spread_bps,
                "tax_rate": c.tax_rate,
                "cash_rate_annual": c.cash_rate_annual,
            },
            "splits": [m.to_dict() for m in self.split_metrics],
        }


def build_grid(
    axes: GridAxes,
    *,
    annual_fee: float | None = None,
    commission_bps: float = 10.0,
    spread_bps: float = 5.0,
    tax_rate: float = 0.15,
    cash_rate_annual: float = 0.0,
) -> list[LETFRotationConfig]:
    """Expand ``axes`` into the cartesian product of configs.

    Cost / tax knobs are **shared** across the grid; they are ablation
    inputs, not search parameters. Flip them in the script to run the
    grid with and without BR tax, with and without costs, etc.
    """
    configs: list[LETFRotationConfig] = []
    for flt, lb, band, lev, gw in product(
        axes.filters,
        axes.lookbacks,
        axes.bands,
        axes.leverages,
        axes.gold_weights,
    ):
        kwargs: dict = dict(
            filter=flt,
            lookback=lb,
            band_pct=band,
            leverage=lev,
            gold_weight=gw,
            commission_bps=commission_bps,
            spread_bps=spread_bps,
            tax_rate=tax_rate,
            cash_rate_annual=cash_rate_annual,
        )
        if annual_fee is not None:
            kwargs["annual_fee"] = annual_fee
        configs.append(LETFRotationConfig(**kwargs))
    return configs


def slice_returns(
    series: pd.Series, start: str, end: str
) -> pd.Series:
    """Return the inclusive ``[start, end]`` slice of a date-indexed series."""
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("series must have a DatetimeIndex")
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if start_ts > end_ts:
        raise ValueError(f"start {start} > end {end}")
    return series.loc[start_ts:end_ts]


def _metrics_from_result(
    result: RotationResult, split_name: str
) -> SplitMetrics:
    rets = result.daily_returns.dropna()
    n_bars = int(len(result.equity.dropna()))
    n_switches = int(result.switches.sum())
    final_eq = float(result.equity.dropna().iloc[-1]) if n_bars else float("nan")
    return SplitMetrics(
        split_name=split_name,
        n_bars=n_bars,
        sharpe=result.sharpe(),
        cagr=result.cagr(),
        max_drawdown=result.max_drawdown(),
        final_equity=final_eq,
        n_switches=n_switches,
        cum_cost_pct=float(result.cum_cost_pct),
        cum_tax_pct=float(result.cum_tax_pct),
    )


def run_letf_rotation_grid(
    spx_returns: pd.Series,
    spx_prices: pd.Series,
    splits: Sequence[SplitDef],
    configs: Sequence[LETFRotationConfig],
    gold_returns: pd.Series | None = None,
    progress: bool = False,
) -> list[GridTrial]:
    """Run every config on every split, collect per-cell metrics.

    For configs with ``gold_weight == 0`` the ``gold_returns`` argument
    is not required; for configs requesting gold exposure it **must**
    be supplied covering every split's window (missing values will
    raise inside :func:`simulate_letf_rotation`).

    Parameters
    ----------
    spx_returns, spx_prices : pd.Series
        Daily TR returns and price series (indexed by date). Must share
        the same index.
    splits : Sequence[SplitDef]
        One row per split window. Order preserved in the output.
    configs : Sequence[LETFRotationConfig]
        Grid cells to evaluate. Typically produced by :func:`build_grid`.
    gold_returns : pd.Series | None
        Optional daily gold returns aligned to ``spx_returns``. Required
        if **any** config has ``gold_weight > 0``.
    progress : bool
        If True, logs a ``config i/N split name`` line per cell at INFO
        level. Keep disabled for tests.

    Returns
    -------
    list[GridTrial]
        One entry per config, each holding a list of per-split metrics.
    """
    if not spx_returns.index.equals(spx_prices.index):
        raise ValueError("spx_returns and spx_prices must share the same index")
    any_gold = any(c.gold_weight > 0 for c in configs)
    if any_gold and gold_returns is None:
        raise ValueError(
            "gold_returns required — at least one config has gold_weight > 0"
        )

    trials: list[GridTrial] = []
    n_total = len(configs) * len(splits)
    k = 0
    for cfg in configs:
        trial = GridTrial(config=cfg)
        for split in splits:
            k += 1
            r_slice = slice_returns(spx_returns, split.start, split.end)
            p_slice = slice_returns(spx_prices, split.start, split.end)
            g_slice = (
                slice_returns(gold_returns, split.start, split.end)
                if gold_returns is not None
                else None
            )
            if progress:
                log.info(
                    "grid %d/%d  %s lb=%d band=%.3f lev=%.2f gw=%.2f  split=%s",
                    k, n_total, cfg.filter, cfg.lookback, cfg.band_pct,
                    cfg.leverage, cfg.gold_weight, split.name,
                )
            result = simulate_letf_rotation(
                r_slice, p_slice, cfg, gold_returns=g_slice
            )
            trial.split_metrics.append(_metrics_from_result(result, split.name))
        trials.append(trial)
    return trials
