"""Grid orchestrator for EMA/SMA Threshold Crossover educational sweep.

Produces the cartesian product of axes, runs per-config simulation,
computes per-config metrics, applies 7 informational gates, and ranks
by a composite CAGR/Sharpe/MDD score.

Citations and signal definition live in
:mod:`market_lab.backtest.strategies.ema_sma_threshold_educational` and
:doc:`specs/ema_sma_threshold_educational.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

import numpy as np
import pandas as pd
from scipy import stats as _stats

from market_lab.backtest.grid.letf_rotation_b1c import bootstrap_sharpe_ci
from market_lab.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    sharpe,
    sortino,
    volatility,
)
from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    ThresholdResult,
    compute_threshold_regime,
    simulate_ema_sma_threshold,
    TRADING_DAYS_PER_YEAR,
)
from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from market_lab.backtest.validation.walk_forward import (
    walk_forward_gate,
    walk_forward_splits,
)

__all__ = [
    "EMASMAThresholdAxes",
    "ConfigMetrics",
    "GateFlags",
    "cartesian_configs",
    "compute_config_metrics",
    "compute_composite_scores",
    "evaluate_gates",
    "run_sweep",
    "SweepOutput",
]


# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EMASMAThresholdAxes:
    """Parameter sweep axes. Default = 384 configs, full = 1512.

    Axes chosen to match the educational spec — see
    ``specs/ema_sma_threshold_educational.md``.
    """

    filters: tuple[str, ...] = ("SMA", "EMA")
    lookbacks: tuple[int, ...] = (50, 100, 150, 200)
    thresholds: tuple[float, ...] = (0.00, 0.02, 0.05, 0.10)
    buy_leverages: tuple[float, ...] = (1.0, 2.0, 3.0)
    sell_leverages: tuple[float, ...] = (0.0, -1.0, -2.0, -3.0)

    @property
    def n_configs(self) -> int:
        return (
            len(self.filters)
            * len(self.lookbacks)
            * len(self.thresholds)
            * len(self.buy_leverages)
            * len(self.sell_leverages)
        )

    @classmethod
    def full(cls) -> "EMASMAThresholdAxes":
        """Widened grid (1512 configs) — flag `--full` in CLI."""
        return cls(
            filters=("SMA", "EMA"),
            lookbacks=(20, 50, 75, 100, 125, 150, 175, 200, 250),
            thresholds=(0.00, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10),
            buy_leverages=(1.0, 2.0, 3.0),
            sell_leverages=(0.0, -1.0, -2.0, -3.0),
        )

    @classmethod
    def smoke(cls) -> "EMASMAThresholdAxes":
        """Tiny grid (8 configs) for smoke test."""
        return cls(
            filters=("SMA", "EMA"),
            lookbacks=(200,),
            thresholds=(0.05,),
            buy_leverages=(1.0, 2.0),
            sell_leverages=(0.0, -1.0),
        )


def cartesian_configs(axes: EMASMAThresholdAxes) -> list[EMASMAThresholdConfig]:
    configs: list[EMASMAThresholdConfig] = []
    for f, n, th, bl, sl in product(
        axes.filters,
        axes.lookbacks,
        axes.thresholds,
        axes.buy_leverages,
        axes.sell_leverages,
    ):
        configs.append(
            EMASMAThresholdConfig(
                filter=f,  # type: ignore[arg-type]
                lookback=n,
                threshold_pct=th,
                buy_leverage=bl,
                sell_leverage=sl,
            )
        )
    return configs


# ---------------------------------------------------------------------------
# Per-config metrics
# ---------------------------------------------------------------------------


@dataclass
class ConfigMetrics:
    cfg_id: str
    cfg: EMASMAThresholdConfig
    cagr: float
    sharpe: float
    max_drawdown: float  # positive magnitude
    calmar: float
    sortino: float
    volatility: float
    n_switches: int
    cum_cost_pct: float


def compute_config_metrics(
    cfg: EMASMAThresholdConfig, result: ThresholdResult
) -> ConfigMetrics:
    eq = result.equity
    rets = result.daily_returns
    mdd = max_drawdown(eq)
    return ConfigMetrics(
        cfg_id=cfg.cfg_id,
        cfg=cfg,
        cagr=cagr(eq, TRADING_DAYS_PER_YEAR),
        sharpe=sharpe(rets, TRADING_DAYS_PER_YEAR),
        max_drawdown=mdd,
        calmar=calmar(eq, TRADING_DAYS_PER_YEAR),
        sortino=sortino(rets, TRADING_DAYS_PER_YEAR),
        volatility=volatility(rets, TRADING_DAYS_PER_YEAR),
        n_switches=result.n_switches,
        cum_cost_pct=result.cum_cost_pct,
    )


# ---------------------------------------------------------------------------
# Composite ranking
# ---------------------------------------------------------------------------


def compute_composite_scores(metrics: list[ConfigMetrics]) -> np.ndarray:
    """Percentile-ranked composite score: 0.4·CAGR + 0.4·Sharpe + 0.2·(1/|MDD|).

    Rank-based so outliers (catastrophic configs with CAGR ≈ −1) don't
    distort the scale. Returns array of scores indexed same as `metrics`.
    """
    n = len(metrics)
    if n == 0:
        return np.array([])
    cagrs = np.array([m.cagr for m in metrics])
    sharpes = np.array([m.sharpe for m in metrics])
    mdds = np.array([m.max_drawdown for m in metrics])  # positive magnitude
    rank_cagr = _stats.rankdata(cagrs) / n
    rank_sharpe = _stats.rankdata(sharpes) / n
    # For MDD, smaller is better. Rank by -|MDD| so higher = better.
    rank_mdd = _stats.rankdata(-np.abs(mdds)) / n
    return 0.4 * rank_cagr + 0.4 * rank_sharpe + 0.2 * rank_mdd


# ---------------------------------------------------------------------------
# Gates (informational — NOT blocking)
# ---------------------------------------------------------------------------


@dataclass
class GateFlags:
    g1_pbo: bool
    g2_dsr: bool
    g3_walk_forward: bool
    g4_oos_sharpe: bool
    g5_fwd_stress: bool
    g6_bootstrap_ci: bool
    g7_cross_lib: bool

    @property
    def n_passed(self) -> int:
        return sum(
            [
                self.g1_pbo,
                self.g2_dsr,
                self.g3_walk_forward,
                self.g4_oos_sharpe,
                self.g5_fwd_stress,
                self.g6_bootstrap_ci,
                self.g7_cross_lib,
            ]
        )


def _cagr_from_returns(rets: pd.Series, periods_per_year: int = 252) -> float:
    r = rets.dropna()
    if len(r) < 2:
        return 0.0
    total = float((1.0 + r).prod())
    if total <= 0:
        return -1.0
    years = len(r) / periods_per_year
    if years <= 0:
        return 0.0
    return total ** (1.0 / years) - 1.0


def _evaluate_g1_pbo_group(
    returns_matrix: np.ndarray, n_blocks: int = 10
) -> bool:
    """PBO applied ONCE to the entire grid — the same verdict for all configs.

    PBO is a property of the grid, not per-config. We return the boolean
    ``PBO < 0.5`` and stamp it on every config's gate flags as an
    honesty marker (everyone shares the same overfit-risk verdict).
    """
    try:
        result = pbo(returns_matrix, n_blocks=n_blocks)
    except Exception:
        return False
    return bool(result.pbo < 0.5)


def _evaluate_g2_dsr(rets: pd.Series, n_trials: int) -> bool:
    r = rets.dropna().values
    if len(r) < 30:
        return False
    try:
        result = dsr(r, n_trials=n_trials)
    except Exception:
        return False
    return bool(result.p_value < 0.05)


def _evaluate_g3_walk_forward(
    rets: pd.Series,
    *,
    is_days: int = 504,  # 2y
    oos_days: int = 126,  # 6mo
    step_days: int = 126,  # 6mo
) -> bool:
    r = rets.dropna()
    n = len(r)
    if n < is_days + oos_days:
        return False
    oos_totals: list[float] = []
    oos_dds: list[float] = []
    for _train, test in walk_forward_splits(
        n_obs=n, is_size=is_days, oos_size=oos_days, step=step_days
    ):
        window = r.iloc[list(test)]
        if window.empty:
            continue
        eq = (1.0 + window).cumprod()
        oos_totals.append(float(eq.iloc[-1] - 1.0))
        peak = eq.cummax()
        dd = 1.0 - (eq / peak).min()
        oos_dds.append(float(dd))
    if len(oos_totals) < 8:
        return False
    verdict = walk_forward_gate(
        oos_totals,
        oos_dds,
        min_windows=8,
        min_profitable_ratio=6 / 8,
        max_drawdown=0.25,
    )
    return verdict == "pass"


def _evaluate_g4_oos_sharpe(rets: pd.Series, split_frac: float = 0.7) -> bool:
    r = rets.dropna()
    n = len(r)
    if n < 100:
        return False
    cut = int(n * split_frac)
    oos = r.iloc[cut:]
    return bool(sharpe(oos, TRADING_DAYS_PER_YEAR) > 0)


def _evaluate_g5_fwd_stress(
    rets: pd.Series, stress_start: str = "2020-01-01"
) -> bool:
    r = rets.dropna()
    if r.empty:
        return False
    window = r.loc[r.index >= pd.Timestamp(stress_start)]
    if len(window) < 60:
        return False
    return bool(sharpe(window, TRADING_DAYS_PER_YEAR) > 0)


def _evaluate_g6_bootstrap(rets: pd.Series, n_resamples: int = 500) -> bool:
    """99.9% CI via stationary bootstrap. 500 resamples keeps the sweep fast
    while still flagging configs whose Sharpe is robustly above zero —
    passing this gate at 500 is not weaker than 2000 for a binary verdict,
    just noisier near the boundary. Cite ``[advances_fin_ml, p.196-202]``.
    """
    r = rets.dropna()
    if len(r) < 100:
        return False
    lo, _hi = bootstrap_sharpe_ci(
        r, alpha=0.001, block_mean=5, n_resamples=n_resamples, seed=42
    )
    if np.isnan(lo):
        return False
    return bool(lo > 0)


def _evaluate_g7_cross_lib(
    cfg: EMASMAThresholdConfig,
    spx_prices: pd.Series,
    spx_returns: pd.Series,
    reference_cagr: float,
    tolerance_pp: float = 0.03,
) -> bool:
    """Compare vectorised pandas regime vs pure-numpy hand-rolled regime.

    Both paths are independent implementations of the same signal. CAGR
    diff ≤ 3pp (`[advances_fin_ml, p.31-34]`) = pass.
    """
    # Hand-rolled MA (pure numpy loop, no pandas rolling/ewm).
    px = spx_prices.astype(float).values
    n = len(px)
    if cfg.filter == "SMA":
        ma = np.full(n, np.nan)
        for i in range(cfg.lookback - 1, n):
            ma[i] = px[i - cfg.lookback + 1 : i + 1].mean()
    else:  # EMA: iterative alpha-weighted
        alpha = 2.0 / (cfg.lookback + 1.0)
        ma = np.full(n, np.nan)
        # Seed at lookback-1 with SMA of first `lookback` values.
        if n >= cfg.lookback:
            seed = px[: cfg.lookback].mean()
            ma[cfg.lookback - 1] = seed
            ema = seed
            for i in range(cfg.lookback, n):
                ema = alpha * px[i] + (1.0 - alpha) * ema
                ma[i] = ema

    upper = ma * (1.0 + cfg.threshold_pct)
    lower = ma * (1.0 - cfg.threshold_pct)
    regime = np.full(n, np.nan)
    prev = None
    for i in range(n):
        if np.isnan(upper[i]):
            continue
        if px[i] > upper[i]:
            prev = 1
        elif px[i] < lower[i]:
            prev = -1
        regime[i] = prev if prev is not None else -1

    # Apply leg returns and compound.
    ret_vals = spx_returns.reindex(spx_prices.index).values
    daily_drag = cfg.fee / TRADING_DAYS_PER_YEAR
    long_leg = cfg.buy_leverage * ret_vals - daily_drag
    if cfg.sell_leverage == 0.0:
        cash_daily = cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
        short_leg = np.full(n, cash_daily)
    else:
        short_leg = cfg.sell_leverage * ret_vals - daily_drag

    # HONEST alignment matching simulate_ema_sma_threshold:
    # yesterday's regime earns today's return, switch cost applied at
    # close after today's return is realised.
    # ``[advances_fin_ml, p.31-34]``.
    eq = 1.0
    prev_regime = None
    switch_cost = cfg.switch_cost_pct
    for i in range(n):
        cur = regime[i]
        if np.isnan(cur):
            continue
        cur_int = int(cur)
        if prev_regime is not None:
            r = long_leg[i] if prev_regime == 1 else short_leg[i]
            if np.isnan(r):
                r = 0.0
            eq *= 1.0 + r
        if prev_regime is not None and cur_int != prev_regime:
            eq -= switch_cost * eq
        prev_regime = cur_int

    # Count usable bars (after warmup) for CAGR.
    valid = int(np.sum(~np.isnan(regime)))
    if valid < 2 or eq <= 0:
        return False
    hand_cagr = eq ** (TRADING_DAYS_PER_YEAR / valid) - 1.0
    return abs(hand_cagr - reference_cagr) <= tolerance_pp


def evaluate_gates(
    metrics: list[ConfigMetrics],
    results: list[ThresholdResult],
    spx_prices: pd.Series,
    spx_returns: pd.Series,
    *,
    n_trials: int | None = None,
) -> list[GateFlags]:
    """Apply 7 gates to each config. Returns list of GateFlags same order."""
    if len(metrics) != len(results):
        raise ValueError("metrics and results must be same length")
    n_trials = n_trials if n_trials is not None else max(len(metrics), 2)

    # G1 is grid-wide (PBO on returns_matrix of all configs).
    if len(results) >= 2:
        # Align all returns to the same (intersection) index.
        common_idx = results[0].daily_returns.index
        for res in results[1:]:
            common_idx = common_idx.intersection(res.daily_returns.index)
        mat = np.column_stack(
            [res.daily_returns.reindex(common_idx).fillna(0.0).values for res in results]
        )
        g1_group = _evaluate_g1_pbo_group(mat)
    else:
        g1_group = False

    flags: list[GateFlags] = []
    for m, res in zip(metrics, results):
        rets = res.daily_returns
        flags.append(
            GateFlags(
                g1_pbo=g1_group,
                g2_dsr=_evaluate_g2_dsr(rets, n_trials),
                g3_walk_forward=_evaluate_g3_walk_forward(rets),
                g4_oos_sharpe=_evaluate_g4_oos_sharpe(rets),
                g5_fwd_stress=_evaluate_g5_fwd_stress(rets),
                g6_bootstrap_ci=_evaluate_g6_bootstrap(rets),
                g7_cross_lib=_evaluate_g7_cross_lib(
                    m.cfg, spx_prices, spx_returns, m.cagr
                ),
            )
        )
    return flags


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@dataclass
class SweepOutput:
    configs: list[EMASMAThresholdConfig]
    results: list[ThresholdResult]
    metrics: list[ConfigMetrics]
    composite: np.ndarray
    gate_flags: list[GateFlags]
    benchmark_metrics: ConfigMetrics | None = None  # SPY buy-hold reference


def run_sweep(
    spx_prices: pd.Series,
    spx_returns: pd.Series,
    axes: EMASMAThresholdAxes,
    *,
    apply_gates: bool = True,
) -> SweepOutput:
    """Run the full sweep: configs → results → metrics → composite + gates."""
    configs = cartesian_configs(axes)
    results: list[ThresholdResult] = []
    metrics: list[ConfigMetrics] = []
    for cfg in configs:
        res = simulate_ema_sma_threshold(spx_prices, spx_returns, cfg)
        results.append(res)
        metrics.append(compute_config_metrics(cfg, res))

    composite = compute_composite_scores(metrics)

    flags: list[GateFlags]
    if apply_gates:
        flags = evaluate_gates(
            metrics, results, spx_prices, spx_returns, n_trials=len(configs)
        )
    else:
        flags = [
            GateFlags(False, False, False, False, False, False, False)
            for _ in configs
        ]

    return SweepOutput(
        configs=configs,
        results=results,
        metrics=metrics,
        composite=composite,
        gate_flags=flags,
    )


def benchmark_spy_buy_hold(
    spx_prices: pd.Series, spx_returns: pd.Series
) -> ConfigMetrics:
    """SPY buy-and-hold baseline — equity from raw SPYSIM TR."""
    eq = spx_prices.reindex(spx_returns.index).dropna()
    # Normalize to 1.0 at start.
    eq = eq / eq.iloc[0]
    rets = eq.pct_change().dropna()
    return ConfigMetrics(
        cfg_id="BENCHMARK_SPY_BH",
        cfg=EMASMAThresholdConfig(
            filter="SMA",
            lookback=2,
            threshold_pct=0.0,
            buy_leverage=1.0,
            sell_leverage=0.0,
            fee=0.0,
        ),
        cagr=cagr(eq, TRADING_DAYS_PER_YEAR),
        sharpe=sharpe(rets, TRADING_DAYS_PER_YEAR),
        max_drawdown=max_drawdown(eq),
        calmar=calmar(eq, TRADING_DAYS_PER_YEAR),
        sortino=sortino(rets, TRADING_DAYS_PER_YEAR),
        volatility=volatility(rets, TRADING_DAYS_PER_YEAR),
        n_switches=0,
        cum_cost_pct=0.0,
    )
