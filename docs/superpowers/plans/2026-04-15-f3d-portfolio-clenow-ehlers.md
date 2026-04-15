# F3.D Portfolio Clenow + Ehlers — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an offline portfolio combination of Clenow momentum + Ehlers BP Swing (blend 50/50, no rebalance) and validate through existing PBO/DSR/walk-forward/CPCV gates, to test hypothesis H1 that orthogonality (ρ ≈ −0.01) lifts effective Sharpe ≥ 1.0 and clears DSR.

**Architecture:** Offline equity-curve merge. Re-run each sub-strategy (3 hardcoded top-3 configs) via existing `GridRunner` on the requested window, then combine pairwise (3 × 3 = 9 portfolios) by weighted daily returns. Wrap the 9 combined curves in a synthetic `GridResult[PortfolioConfig]` so the existing `GateEvaluator`, `DiagnosticAnalyzer`, `GridReportGenerator`, and `wf_for_grid` apply unchanged. Zero engine changes; ~350 new lines.

**Tech Stack:** Python 3.12, pandas/numpy, pytest. Reuses `ai_trade.backtest.{strategies,grid,validation,data,engine,metrics}`. No new dependencies in `pyproject.toml`.

**Spec:** `docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `src/ai_trade/backtest/portfolio/__init__.py` | Package marker + re-exports |
| `src/ai_trade/backtest/portfolio/combined.py` | `combine_equity_curves()`, `compute_portfolio_metrics()`, `make_portfolio_trial()` |
| `src/ai_trade/backtest/portfolio/configs.py` | `PortfolioConfig` dataclass + `portfolio_configs()` (returns 9 configs from top-3 Clenow × top-3 Ehlers) |
| `scripts/run_portfolio_combined.py` | CLI orchestrator (sub-grids → combine → validate → report) |
| `tests/test_portfolio_combined.py` | Unit tests for `combine_equity_curves` + `compute_portfolio_metrics` + `make_portfolio_trial` |
| `tests/test_portfolio_configs.py` | Unit tests for `PortfolioConfig` + `portfolio_configs()` |

### Modified files

| Path | Change |
|---|---|
| (none in phase 1-2) | All additions isolated to new package |

Post-run only (phase 3):

| Path | Change |
|---|---|
| `JORNADA.md` | New dated entry with verdict |
| `ROADMAP.md` §"Current status" | Update with F3.D outcome |

---

## Source of Truth: Top-3 configs

These are fixed constants derived from two diagnostic reports and must NOT be recomputed:

**Top-3 Clenow** (from `reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md`, ranked by Sharpe among 30 trials):

| rank | config_id | lookback_regression | top_pct | risk_factor | Sharpe |
|---|---|---|---|---|---|
| 1 | 8 | 75 | 0.20 | 0.001 | 0.618 |
| 2 | 19 | 105 | 0.10 | 0.002 | 0.581 |
| 3 | 10 | 75 | 0.30 | 0.001 | 0.517 |

**Top-3 Ehlers BP Swing** (from `reports/grid_ehlers_20260415-1353/diagnostic.md`, ranked by Sharpe among 24 trials):

| rank | config_id | hp_period | lp_period | pct_of_dcp | stop_pct | Sharpe |
|---|---|---|---|---|---|---|
| 1 | 6 | 48 | 20 | 0.80 | 0.02 | 0.639 |
| 2 | 18 | 80 | 20 | 0.80 | 0.02 | 0.606 |
| 3 | 19 | 80 | 20 | 0.80 | 0.05 | 0.603 |

---

## Task 0: Pre-flight verification

**Files:** (none modified)

- [ ] **Step 1: Verify clean working tree for the F3.D files to be added**

Run:
```bash
cd /var/www/pessoal/ai-trade
git status --short
```

Expected: the paths `src/ai_trade/backtest/portfolio/`, `scripts/run_portfolio_combined.py`, `tests/test_portfolio_combined.py`, `tests/test_portfolio_configs.py` MUST NOT appear. (Unrelated pre-existing `M`/`??` entries from earlier sessions are fine — don't touch them.)

- [ ] **Step 2: Verify baseline test count**

Run:
```bash
.venv/bin/pytest --collect-only -q 2>&1 | tail -3
```

Expected: `362 tests collected` (exact number; halt if different — investigate before proceeding).

- [ ] **Step 3: Verify baseline tests pass**

Run:
```bash
.venv/bin/pytest -q 2>&1 | tail -3
```

Expected: `362 passed` in under 2 minutes. If any test fails, halt and report — do NOT proceed with additions on top of a red baseline.

---

## Task 1: Package skeleton

**Files:**
- Create: `src/ai_trade/backtest/portfolio/__init__.py`
- Create: `src/ai_trade/backtest/portfolio/combined.py` (empty stub)

- [ ] **Step 1: Create empty package marker**

Create `src/ai_trade/backtest/portfolio/__init__.py` with:

```python
"""Portfolio combination primitives — offline equity-curve merge.

See ``docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md``
for the F3.D hypothesis. This package does NOT modify the engine: sub-
strategies run as standalone grids, then their equity curves are combined
by weighted daily returns. The result is wrapped in a synthetic
``GridResult`` so the existing PBO/DSR/walk-forward evaluators apply.
"""

from ai_trade.backtest.portfolio.combined import (
    combine_equity_curves,
    compute_portfolio_metrics,
    make_portfolio_trial,
)
from ai_trade.backtest.portfolio.configs import (
    PortfolioConfig,
    clenow_top3_grid_configs,
    ehlers_top3_grid_configs,
    portfolio_configs,
)

__all__ = [
    "PortfolioConfig",
    "clenow_top3_grid_configs",
    "combine_equity_curves",
    "compute_portfolio_metrics",
    "ehlers_top3_grid_configs",
    "make_portfolio_trial",
    "portfolio_configs",
]
```

- [ ] **Step 2: Create empty `combined.py`**

Create `src/ai_trade/backtest/portfolio/combined.py` with:

```python
"""combine equity curves + compute metrics + build synthetic trial.

Implemented incrementally by Tasks 2-5.
"""
```

- [ ] **Step 3: Create empty `configs.py`**

Create `src/ai_trade/backtest/portfolio/configs.py` with:

```python
"""PortfolioConfig + portfolio_configs() — 9 configs from top-3 × top-3.

Implemented by Task 6.
"""
```

- [ ] **Step 4: Verify the package imports (import will fail — expected)**

Run:
```bash
.venv/bin/python -c "from ai_trade.backtest.portfolio import combined" 2>&1 | head -5
```

Expected: import succeeds (module loads), but the `from ... import combine_equity_curves` in `__init__.py` will fail. That's OK — the next task implements it.

Run (to confirm the failure is in the re-export, not elsewhere):
```bash
.venv/bin/python -c "from ai_trade.backtest.portfolio import combine_equity_curves" 2>&1 | head -5
```

Expected: `ImportError: cannot import name 'combine_equity_curves'`. Halt if the error message is different.

- [ ] **Step 5: Do NOT commit yet** — commit after Task 5 when the utility is working.

---

## Task 2: `combine_equity_curves` — basic weighted average (TDD)

**Files:**
- Modify: `src/ai_trade/backtest/portfolio/combined.py`
- Create: `tests/test_portfolio_combined.py`

- [ ] **Step 1: Write the failing test — 2 curves, identical index, weighted combination**

Create `tests/test_portfolio_combined.py` with:

```python
"""Tests for ai_trade.backtest.portfolio.combined."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.portfolio.combined import (
    combine_equity_curves,
    compute_portfolio_metrics,
)


def _curve(returns: list[float], start: str = "2020-01-01") -> pd.Series:
    """Build an equity curve from a list of daily returns, starting at 100."""
    idx = pd.date_range(start, periods=len(returns) + 1, freq="B")
    equity = [100.0]
    for r in returns:
        equity.append(equity[-1] * (1.0 + r))
    return pd.Series(equity, index=idx, name="equity")


def test_combine_two_curves_equal_weight_same_index():
    # Curve A: +10% then -5%. Curve B: flat.
    a = _curve([0.10, -0.05])
    b = _curve([0.0, 0.0])
    combined = combine_equity_curves([a, b], [0.5, 0.5], initial_capital=100.0)

    # Day 0: capital = 100.
    # Day 1: return = 0.5*0.10 + 0.5*0.0 = 0.05 → equity = 105.
    # Day 2: return = 0.5*(-0.05) + 0.5*0.0 = -0.025 → equity = 105 * 0.975 = 102.375.
    assert combined.iloc[0] == pytest.approx(100.0)
    assert combined.iloc[1] == pytest.approx(105.0)
    assert combined.iloc[2] == pytest.approx(102.375)
    assert list(combined.index) == list(a.index)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py::test_combine_two_curves_equal_weight_same_index -v 2>&1 | tail -5
```

Expected: `ImportError` or `AttributeError` on `combine_equity_curves` (function not yet defined).

- [ ] **Step 3: Implement minimal `combine_equity_curves` in `combined.py`**

Replace the contents of `src/ai_trade/backtest/portfolio/combined.py` with:

```python
"""combine equity curves + compute metrics + build synthetic trial.

Weighted-returns offline combination — zero engine changes.
Citations: `[systematic_trading, Carver — capital allocation]`,
`[risk_parity, Qian — risk-parity math]`.
"""

from __future__ import annotations

import pandas as pd


def combine_equity_curves(
    curves: list[pd.Series],
    weights: list[float],
    initial_capital: float,
) -> pd.Series:
    """Combine N equity curves into one via weighted daily returns.

    Steps:
    1. Align all curves on their DatetimeIndex intersection.
    2. Compute per-curve daily returns (pct_change, drop NaN row).
    3. Portfolio return = sum(weights[i] * returns[i]).
    4. Rebuild equity curve from ``initial_capital`` by cumprod(1+r).

    The first bar of the output equals ``initial_capital`` (no returns
    yet); subsequent bars reflect the weighted cumulative return.
    """
    if not curves:
        raise ValueError("curves must be non-empty")
    if len(curves) != len(weights):
        raise ValueError(
            f"len(curves)={len(curves)} != len(weights)={len(weights)}"
        )

    # Step 1: align on intersection
    common = curves[0].index
    for c in curves[1:]:
        common = common.intersection(c.index)
    if len(common) < 2:
        raise ValueError(
            f"aligned index too short ({len(common)} bars) — curves do not overlap enough"
        )
    aligned = [c.reindex(common).ffill() for c in curves]

    # Step 2 + 3: weighted returns
    returns = [c.pct_change() for c in aligned]
    port_ret = sum(w * r for w, r in zip(weights, returns))

    # Step 4: rebuild equity
    port_ret.iloc[0] = 0.0  # first bar has no return
    equity = initial_capital * (1.0 + port_ret).cumprod()
    equity.name = "equity"
    return equity
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py::test_combine_two_curves_equal_weight_same_index -v 2>&1 | tail -5
```

Expected: `1 passed`. Halt if not green.

---

## Task 3: `combine_equity_curves` — temporal alignment (TDD)

**Files:**
- Modify: `tests/test_portfolio_combined.py`
- (`combined.py` already handles alignment, this just tests it)

- [ ] **Step 1: Write the failing test — curves with different start dates**

Append to `tests/test_portfolio_combined.py`:

```python
def test_combine_curves_with_different_start_dates_uses_intersection():
    # Curve A: 5 bars from 2020-01-01.
    a = pd.Series(
        [100.0, 101.0, 102.0, 103.0, 104.0],
        index=pd.date_range("2020-01-01", periods=5, freq="B"),
        name="equity",
    )
    # Curve B: 5 bars from 2020-01-03 (overlaps with A on last 3).
    b = pd.Series(
        [100.0, 110.0, 121.0, 133.1, 146.41],
        index=pd.date_range("2020-01-03", periods=5, freq="B"),
        name="equity",
    )
    combined = combine_equity_curves([a, b], [0.5, 0.5], initial_capital=1000.0)

    # Intersection: 2020-01-03 (Fri), 2020-01-06 (Mon), 2020-01-07 (Tue).
    # 3 bars → 2 returns computed.
    assert len(combined) == 3
    assert combined.index[0] == pd.Timestamp("2020-01-03")
    assert combined.index[-1] == pd.Timestamp("2020-01-07")
    assert combined.iloc[0] == pytest.approx(1000.0)
```

- [ ] **Step 2: Run test**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py::test_combine_curves_with_different_start_dates_uses_intersection -v 2>&1 | tail -5
```

Expected: `1 passed` (already handled by the intersection logic in Task 2's implementation).

If it fails: the intersection code in Task 2 is broken — fix it before proceeding. Do NOT move to Task 4 on red.

---

## Task 4: `combine_equity_curves` — input validation (TDD)

**Files:**
- Modify: `tests/test_portfolio_combined.py`
- Modify: `src/ai_trade/backtest/portfolio/combined.py`

- [ ] **Step 1: Write failing tests for empty input and mismatched lengths**

Append to `tests/test_portfolio_combined.py`:

```python
def test_combine_empty_curves_raises():
    with pytest.raises(ValueError, match="non-empty"):
        combine_equity_curves([], [], initial_capital=100.0)


def test_combine_mismatched_weights_raises():
    a = _curve([0.0])
    with pytest.raises(ValueError, match="len"):
        combine_equity_curves([a], [0.5, 0.5], initial_capital=100.0)


def test_combine_weights_must_sum_to_one():
    a = _curve([0.1])
    b = _curve([0.2])
    # Weights [0.5, 0.6] sum to 1.1 — invalid.
    with pytest.raises(ValueError, match="sum"):
        combine_equity_curves([a, b], [0.5, 0.6], initial_capital=100.0)


def test_combine_insufficient_overlap_raises():
    a = pd.Series(
        [100.0, 101.0],
        index=pd.date_range("2020-01-01", periods=2, freq="B"),
        name="equity",
    )
    b = pd.Series(
        [100.0, 101.0],
        index=pd.date_range("2020-01-15", periods=2, freq="B"),
        name="equity",
    )
    with pytest.raises(ValueError, match="overlap"):
        combine_equity_curves([a, b], [0.5, 0.5], initial_capital=100.0)
```

- [ ] **Step 2: Run tests — `weights_must_sum_to_one` should fail**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py -v 2>&1 | tail -10
```

Expected: `test_combine_weights_must_sum_to_one` fails (current impl does not validate sum). Others pass.

- [ ] **Step 3: Add weights-sum validation to `combine_equity_curves`**

In `src/ai_trade/backtest/portfolio/combined.py`, modify the validation block at the top of `combine_equity_curves` to add:

```python
    if not curves:
        raise ValueError("curves must be non-empty")
    if len(curves) != len(weights):
        raise ValueError(
            f"len(curves)={len(curves)} != len(weights)={len(weights)}"
        )
    weight_sum = sum(weights)
    if not (0.999 <= weight_sum <= 1.001):
        raise ValueError(
            f"weights must sum to 1.0 (got {weight_sum:.4f})"
        )
```

(The existing `common = curves[0].index` block and everything below stays.)

- [ ] **Step 4: Run all 4 validation tests**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py -v 2>&1 | tail -10
```

Expected: all 4 validation tests pass plus the 2 from Tasks 2-3 (6 total).

---

## Task 5: `compute_portfolio_metrics` + `make_portfolio_trial` (TDD)

**Files:**
- Modify: `tests/test_portfolio_combined.py`
- Modify: `src/ai_trade/backtest/portfolio/combined.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_portfolio_combined.py`:

```python
def test_compute_portfolio_metrics_basic():
    # 252 trading days of 0.1% daily return = ~28% annual.
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    curve = pd.Series(100.0 * (1.001 ** np.arange(len(dates))), index=dates, name="equity")

    metrics = compute_portfolio_metrics(curve, periods_per_year=252)

    assert "sharpe" in metrics
    assert "cagr" in metrics
    assert "max_drawdown" in metrics
    assert metrics["cagr"] > 0.25  # near 28%
    assert metrics["cagr"] < 0.35
    # Sharpe for a monotonic curve with constant return is +inf (std=0).
    # Our `_safe_sharpe` helper returns 0.0 in that case — accept either.
    assert metrics["sharpe"] == 0.0 or np.isinf(metrics["sharpe"])
    assert metrics["max_drawdown"] == pytest.approx(0.0, abs=1e-9)


def test_make_portfolio_trial_wraps_curve_into_trial_result():
    from ai_trade.backtest.grid.result import TrialResult
    from ai_trade.backtest.portfolio.combined import make_portfolio_trial
    from ai_trade.backtest.portfolio.configs import PortfolioConfig

    curve = _curve([0.01, -0.005, 0.02])
    cfg = PortfolioConfig(
        clenow_config_id=8,
        ehlers_config_id=6,
        clenow_lookback=75,
        clenow_top_pct=0.20,
        clenow_risk_factor=0.001,
        ehlers_hp=48,
        ehlers_lp=20,
        ehlers_pct_of_dcp=0.80,
        ehlers_stop_pct=0.02,
    )

    trial = make_portfolio_trial(
        config_id=0,
        config=cfg,
        equity_curve=curve,
        initial_cash=100.0,
    )

    assert isinstance(trial, TrialResult)
    assert trial.config_id == 0
    assert trial.config is cfg
    assert trial.status == "ok"
    assert trial.result is not None
    assert list(trial.result.equity_curve.values) == list(curve.values)
    assert trial.result.initial_cash == 100.0
    assert trial.result.final_equity == pytest.approx(curve.iloc[-1])
```

- [ ] **Step 2: Run tests — both should fail (functions undefined)**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py::test_compute_portfolio_metrics_basic tests/test_portfolio_combined.py::test_make_portfolio_trial_wraps_curve_into_trial_result -v 2>&1 | tail -10
```

Expected: both fail with `ImportError`/`AttributeError`.

- [ ] **Step 3: Implement both functions**

Append to `src/ai_trade/backtest/portfolio/combined.py`:

```python
import numpy as np

from ai_trade.backtest.engine.runner import BacktestResult
from ai_trade.backtest.grid.result import TrialResult
from ai_trade.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
)


def compute_portfolio_metrics(
    equity_curve: pd.Series,
    periods_per_year: int = 252,
) -> dict[str, float]:
    """Compute Sharpe / CAGR / max DD for a portfolio equity curve.

    Matches the helper semantics used by :class:`GridRunner` so the
    numbers are comparable with sub-strategy per-trial metrics.
    """
    if len(equity_curve) < 2:
        return {"sharpe": 0.0, "cagr": 0.0, "max_drawdown": 0.0}
    rets = returns_from_equity(equity_curve)
    sh = float(sharpe(rets, periods_per_year=periods_per_year))
    cg = float(cagr(equity_curve, periods_per_year=periods_per_year))
    dd = float(max_drawdown(equity_curve))
    return {"sharpe": sh, "cagr": cg, "max_drawdown": dd}


def make_portfolio_trial(
    config_id: int,
    config,
    equity_curve: pd.Series,
    initial_cash: float,
    periods_per_year: int = 252,
) -> TrialResult:
    """Wrap a combined equity curve into a synthetic TrialResult.

    The produced TrialResult has empty ``trades`` and ``fills`` lists
    (we're working at the equity-curve level, not per-trade). That is
    fine — the existing gate pipeline uses ``equity_curve`` and the
    scalar metrics; it never iterates trades for PBO/DSR/WF.
    """
    result = BacktestResult(
        equity_curve=equity_curve,
        trades=[],
        fills=[],
        initial_cash=float(initial_cash),
        final_equity=float(equity_curve.iloc[-1]),
    )
    metrics = compute_portfolio_metrics(
        equity_curve, periods_per_year=periods_per_year,
    )
    sh = metrics["sharpe"]
    if not np.isfinite(sh):
        sh = 0.0
    return TrialResult(
        config_id=config_id,
        config=config,
        result=result,
        sharpe=float(sh),
        cagr=float(metrics["cagr"]),
        max_drawdown=float(metrics["max_drawdown"]),
        status="ok",
    )
```

- [ ] **Step 4: Note: `test_make_portfolio_trial` depends on `PortfolioConfig` — implement it first in Task 6 before re-running that test**

Skip re-running `test_make_portfolio_trial_wraps_curve_into_trial_result` for now. Run only the metrics test:

Run:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py::test_compute_portfolio_metrics_basic -v 2>&1 | tail -5
```

Expected: `1 passed`.

Run full file to check others still pass:
```bash
.venv/bin/pytest tests/test_portfolio_combined.py -v 2>&1 | tail -15
```

Expected: 6 passes + 1 error (the `test_make_portfolio_trial...` test — will fix in Task 6).

---

## Task 6: `PortfolioConfig` + `portfolio_configs()` (TDD)

**Files:**
- Create: `tests/test_portfolio_configs.py`
- Modify: `src/ai_trade/backtest/portfolio/configs.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_portfolio_configs.py` with:

```python
"""Tests for ai_trade.backtest.portfolio.configs."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ai_trade.backtest.portfolio.configs import (
    PortfolioConfig,
    portfolio_configs,
)


def test_portfolio_config_is_frozen():
    cfg = PortfolioConfig(
        clenow_config_id=8,
        ehlers_config_id=6,
        clenow_lookback=75,
        clenow_top_pct=0.20,
        clenow_risk_factor=0.001,
        ehlers_hp=48,
        ehlers_lp=20,
        ehlers_pct_of_dcp=0.80,
        ehlers_stop_pct=0.02,
    )
    with pytest.raises(FrozenInstanceError):
        cfg.clenow_config_id = 999  # type: ignore[misc]


def test_portfolio_configs_returns_9_unique_pairs():
    configs = portfolio_configs()
    assert len(configs) == 9
    # All pairs (clenow_config_id, ehlers_config_id) distinct.
    pairs = [(c.clenow_config_id, c.ehlers_config_id) for c in configs]
    assert len(set(pairs)) == 9


def test_portfolio_configs_top_3_clenow_ids_are_8_19_10():
    """Top-3 by Sharpe from grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md."""
    configs = portfolio_configs()
    clenow_ids = sorted({c.clenow_config_id for c in configs})
    assert clenow_ids == [8, 10, 19]


def test_portfolio_configs_top_3_ehlers_ids_are_6_18_19():
    """Top-3 by Sharpe from grid_ehlers_20260415-1353/diagnostic.md."""
    configs = portfolio_configs()
    ehlers_ids = sorted({c.ehlers_config_id for c in configs})
    assert ehlers_ids == [6, 18, 19]


def test_portfolio_configs_parameter_values_match_reports():
    """Verify the hardcoded parameter values match the reports exactly."""
    configs = portfolio_configs()

    # Pick the (clenow=8, ehlers=6) pair — Sharpe rank 1 × rank 1.
    cfg = next(
        c for c in configs
        if c.clenow_config_id == 8 and c.ehlers_config_id == 6
    )
    # Clenow rank-1 (config_id=8): lookback=75, top_pct=0.20, risk=0.001.
    assert cfg.clenow_lookback == 75
    assert cfg.clenow_top_pct == pytest.approx(0.20)
    assert cfg.clenow_risk_factor == pytest.approx(0.001)
    # Ehlers rank-1 (config_id=6): hp=48, lp=20, pct=0.80, stop=0.02.
    assert cfg.ehlers_hp == 48
    assert cfg.ehlers_lp == 20
    assert cfg.ehlers_pct_of_dcp == pytest.approx(0.80)
    assert cfg.ehlers_stop_pct == pytest.approx(0.02)


def test_clenow_top3_grid_configs_returns_3_ClenowGridConfigs():
    from ai_trade.backtest.grid.config import ClenowGridConfig
    from ai_trade.backtest.portfolio.configs import (
        clenow_top3_grid_configs,
    )
    configs = clenow_top3_grid_configs()
    assert len(configs) == 3
    assert all(isinstance(c, ClenowGridConfig) for c in configs)
    # Rank 1: lookback=75, top_pct=0.20, risk_factor=0.001.
    assert configs[0].lookback_regression == 75
    assert configs[0].top_pct == pytest.approx(0.20)
    assert configs[0].risk_factor == pytest.approx(0.001)


def test_ehlers_top3_grid_configs_returns_3_EhlersGridConfigs():
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
    from ai_trade.backtest.portfolio.configs import (
        ehlers_top3_grid_configs,
    )
    configs = ehlers_top3_grid_configs()
    assert len(configs) == 3
    assert all(isinstance(c, EhlersGridConfig) for c in configs)
    # Rank 1: hp=48, lp=20, pct=0.80, stop=0.02.
    assert configs[0].hp_period == 48
    assert configs[0].lp_period == 20
    assert configs[0].pct_of_dcp == pytest.approx(0.80)
    assert configs[0].stop_pct == pytest.approx(0.02)
```

- [ ] **Step 2: Run tests — all should fail**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_configs.py -v 2>&1 | tail -10
```

Expected: 5 failures (functions not implemented).

- [ ] **Step 3: Implement `configs.py`**

Replace contents of `src/ai_trade/backtest/portfolio/configs.py` with:

```python
"""PortfolioConfig + portfolio_configs() — 9 configs from top-3 × top-3.

Top-3 configs are sourced from the two existing diagnostic reports:

* Clenow (Run 3 Tiingo SPX 2015-2023): top-3 by Sharpe from
  ``reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md``.
* Ehlers BP Swing (long-history SPY 2005-2023): top-3 by Sharpe from
  ``reports/grid_ehlers_20260415-1353/diagnostic.md``.

The choice of "top-3 by Sharpe" (rather than just top-1) honours
:class:`DSR` deflation semantics — see
``docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md``
§3.1 "N_trials = 9 portfolios".
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


# ---- Top-3 Clenow by Sharpe (Run 3 Tiingo SPX 2015-2023) ----
# Source: reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md
_CLENOW_TOP3 = (
    # (config_id, lookback_regression, top_pct, risk_factor, sharpe_from_report)
    (8, 75, 0.20, 0.001, 0.618),
    (19, 105, 0.10, 0.002, 0.581),
    (10, 75, 0.30, 0.001, 0.517),
)

# ---- Top-3 Ehlers BP Swing by Sharpe (long-history SPY 2005-2023) ----
# Source: reports/grid_ehlers_20260415-1353/diagnostic.md
_EHLERS_TOP3 = (
    # (config_id, hp_period, lp_period, pct_of_dcp, stop_pct, sharpe_from_report)
    (6, 48, 20, 0.80, 0.02, 0.639),
    (18, 80, 20, 0.80, 0.02, 0.606),
    (19, 80, 20, 0.80, 0.05, 0.603),
)


@dataclass(frozen=True)
class PortfolioConfig:
    """Parameter bundle for one F3.D portfolio trial.

    Fields identify which top-3 config of each sub-strategy is paired
    AND inline the parameters so the dataclass is self-contained
    (readable in diagnostic reports without cross-referencing).
    """

    clenow_config_id: int
    ehlers_config_id: int

    # Clenow parameters (mirrored from ClenowGridConfig).
    clenow_lookback: int
    clenow_top_pct: float
    clenow_risk_factor: float

    # Ehlers parameters (mirrored from EhlersGridConfig).
    ehlers_hp: int
    ehlers_lp: int
    ehlers_pct_of_dcp: float
    ehlers_stop_pct: float


def portfolio_configs() -> list[PortfolioConfig]:
    """Return the 9 portfolio configs (3 × 3 cartesian product).

    Order: outer loop = Clenow rank (1, 2, 3), inner loop = Ehlers
    rank (1, 2, 3). This gives a deterministic mapping
    ``config_id = i`` for checkpoint/report stability.
    """
    return [
        PortfolioConfig(
            clenow_config_id=c[0],
            ehlers_config_id=e[0],
            clenow_lookback=c[1],
            clenow_top_pct=c[2],
            clenow_risk_factor=c[3],
            ehlers_hp=e[1],
            ehlers_lp=e[2],
            ehlers_pct_of_dcp=e[3],
            ehlers_stop_pct=e[4],
        )
        for c, e in itertools.product(_CLENOW_TOP3, _EHLERS_TOP3)
    ]


def clenow_top3_grid_configs():
    """Return the 3 top-3 Clenow configs as ClenowGridConfig instances.

    Public helper for script callers — keeps the ``_CLENOW_TOP3`` tuple
    encoding private to this module.
    """
    from ai_trade.backtest.grid.config import ClenowGridConfig
    return [
        ClenowGridConfig(
            lookback_regression=c[1], top_pct=c[2], risk_factor=c[3],
        )
        for c in _CLENOW_TOP3
    ]


def ehlers_top3_grid_configs():
    """Return the 3 top-3 Ehlers configs as EhlersGridConfig instances."""
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
    return [
        EhlersGridConfig(
            hp_period=e[1], lp_period=e[2], pct_of_dcp=e[3], stop_pct=e[4],
        )
        for e in _EHLERS_TOP3
    ]
```

- [ ] **Step 4: Run all config + combined tests**

Run:
```bash
.venv/bin/pytest tests/test_portfolio_configs.py tests/test_portfolio_combined.py -v 2>&1 | tail -20
```

Expected: all 7 config tests + all 7 combined tests (including the previously-deferred `test_make_portfolio_trial_wraps_curve_into_trial_result`) = **14 passed**.

- [ ] **Step 5: Verify baseline is now 362 + 14 = 376 tests**

Run:
```bash
.venv/bin/pytest --collect-only -q 2>&1 | tail -3
```

Expected: `376 tests collected`.

- [ ] **Step 6: Commit Phase 1 (core utility)**

Run:
```bash
cd /var/www/pessoal/ai-trade
git add \
  src/ai_trade/backtest/portfolio/__init__.py \
  src/ai_trade/backtest/portfolio/combined.py \
  src/ai_trade/backtest/portfolio/configs.py \
  tests/test_portfolio_combined.py \
  tests/test_portfolio_configs.py
git commit -m "$(cat <<'EOF'
feat(portfolio): core offline combination utility for F3.D

Adds src/ai_trade/backtest/portfolio/ with:
- combine_equity_curves() — N curves → weighted daily-return merge
- compute_portfolio_metrics() — Sharpe/CAGR/MaxDD matching GridRunner
- make_portfolio_trial() — wraps combined curve in a synthetic TrialResult
- PortfolioConfig + portfolio_configs() — 9 top-3 × top-3 pairs hardcoded
  from reports/grid_clenow_tiingo_postfix_20260415-1005 and
  reports/grid_ehlers_20260415-1353 diagnostic.md

Citations: [systematic_trading, Carver ch.5], [risk_parity, Qian],
[advances_fin_ml ch.11] (N=9 DSR deflation rationale).

Refs: docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md

14 new tests (376 total).
EOF
)"
git status --short | head -5
```

Expected: clean commit, `git status` shows the 5 new files are gone (now tracked) plus any pre-existing WIP untouched.

- [ ] **Step 7: Log progress**

Run:
```bash
printf '[2026-04-15 session] Phase 1 complete — portfolio core utility committed (%s)\n' \
  "$(git rev-parse --short HEAD)" >> logs/f3d.log
```

---

## Task 7: CLI — argument parsing + data source wiring

**Files:**
- Create: `scripts/run_portfolio_combined.py` (partial — only argparse + helpers)

- [ ] **Step 1: Write the CLI skeleton**

Create `scripts/run_portfolio_combined.py` with:

```python
#!/usr/bin/env python3
"""Run the F3.D combined portfolio grid with active anti-overfit gates.

Orchestrates the end-to-end pipeline for a "two books offline" portfolio
combining Clenow momentum + Ehlers BP Swing:

1. Load OHLCV (Tiingo storage-first): Clenow needs SPX 500 universe,
   Ehlers needs SPY.
2. Build 3 Clenow top-3 configs + 3 Ehlers top-3 configs = 9 pairs.
3. Run each sub-strategy as its own GridRunner pass (3 trials each),
   obtaining 3 Clenow equity curves + 3 Ehlers equity curves.
4. For each (c, e) pair: combine_equity_curves([c, e], [0.5, 0.5]).
5. Wrap 9 combined curves as TrialResult and bundle into a synthetic
   GridResult[PortfolioConfig].
6. Run walk-forward per combined portfolio (8 windows each).
7. Apply GateEvaluator against PBO/DSR/walk-forward rules.
8. Write diagnostic.md + PNGs via GridReportGenerator.

Typical invocation:

    .venv/bin/python scripts/run_portfolio_combined.py \\
        --start 2015-01-01 --end 2023-12-31 \\
        --cash 100000 \\
        --output-dir reports/

Logs: unified append-only log at ``logs/grid.log`` + per-session log
at ``logs/f3d.log``. Per-run checkpoint detail under
``.cache/grid_runs/{run_id}/``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


log = logging.getLogger("ai_trade.grid.f3d")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="F3.D combined-portfolio grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument(
        "--run-id",
        default=None,
        help="Defaults to grid_portfolio_<YYYYMMDD-HHMM>. Resume a prior run "
        "by reusing its run_id.",
    )
    ap.add_argument(
        "--n-jobs", type=int, default=-1,
        help="-1 = all cores (default); 1 = sequential",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Skip validation/report and just print the 9 portfolio Sharpes.",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
        help="Tiingo parquet+manifest root. Default: data/tiingo.",
    )
    ap.add_argument(
        "--warmup-days", type=int, default=500,
        help="Calendar days of history before --start (default: 500).",
    )
    ap.add_argument(
        "--index-symbol", default="SPY",
        help="Index trend-filter symbol for Clenow (also Ehlers instrument). "
        "Tiingo convention is SPY (not ^GSPC).",
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _build_tiingo_source(storage_root: Path):
    """Construct a TiingoSource with storage-first semantics."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    return TiingoSource(storage=TiingoStorage(root=storage_root))


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    run_id = args.run_id or f"grid_portfolio_{datetime.now().strftime('%Y%m%d-%H%M')}"
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    from ai_trade.backtest.grid import setup_grid_logging
    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"),
        level=getattr(logging, args.log_level),
    )
    log.info("=== F3.D portfolio run %s ===", run_id)
    log.info(
        "start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        args.start, args.end, args.cash, args.n_jobs, args.dry_run,
    )

    # Remaining steps wired in Tasks 8-11.
    log.warning("main() stub — Tasks 8-11 extend this")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the CLI skeleton runs (prints help)**

Run:
```bash
.venv/bin/python scripts/run_portfolio_combined.py --help 2>&1 | tail -25
```

Expected: argparse help output with `--start`, `--end`, `--cash`, etc. No Python error.

- [ ] **Step 3: Do NOT commit yet** — commit after Task 11 when the script is complete.

---

## Task 8: CLI — sub-strategy grid runners (Clenow + Ehlers)

**Files:**
- Modify: `scripts/run_portfolio_combined.py`

- [ ] **Step 1: Add a helper that runs the Clenow top-3 grid**

Append to `scripts/run_portfolio_combined.py` (above `main`, below `_build_tiingo_source`):

```python
def _run_clenow_top3(
    data: dict[str, pd.DataFrame],
    constituents_provider,
    index_symbol: str,
    start: date,
    end: date,
    cash: float,
    n_jobs: int,
    checkpoint_dir: Path,
    run_id: str,
):
    """Run the 3 top-3 Clenow configs; return a list of 3 equity curves.

    The strategy needs a point-in-time ``constituents_provider`` and the
    ``index_symbol`` that drives Clenow's regime filter — both mirror how
    ``scripts/run_grid_clenow.py`` wires its trial_fn.
    """
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.grid import ClenowGridConfig, GridRunner
    from ai_trade.backtest.portfolio.configs import clenow_top3_grid_configs
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    clenow_configs = clenow_top3_grid_configs()

    data_bounded = {
        sym: df.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        for sym, df in data.items()
    }

    def trial_fn(cfg: ClenowGridConfig):
        strategy = ClenowMomentumStrategy(
            data=data,
            constituents_provider=constituents_provider,
            index_symbol=index_symbol,
            lookback_regression=cfg.lookback_regression,
            top_pct=cfg.top_pct,
            risk_factor=cfg.risk_factor,
            rebalance_weekday=cfg.rebalance_weekday,
            lookback_trend=cfg.lookback_trend,
            lookback_index_trend=cfg.lookback_index_trend,
            lookback_atr=cfg.lookback_atr,
            lookback_gap=cfg.lookback_gap,
            gap_threshold=cfg.gap_threshold,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

    log.info("Running Clenow top-3 grid (3 configs)")
    grid = GridRunner(
        checkpoint_dir=checkpoint_dir,
        n_jobs=n_jobs,
        config_cls=ClenowGridConfig,
    ).run(
        configs=clenow_configs, trial_fn=trial_fn,
        run_id=f"{run_id}_clenow",
    )
    ok = grid.ok_trials
    if len(ok) != 3:
        raise RuntimeError(
            f"Expected 3 OK Clenow trials; got {len(ok)}. Error msgs: "
            f"{[t.error_msg for t in grid.trials if t.status == 'error']}"
        )
    return [t.result.equity_curve for t in ok]
```

- [ ] **Step 2: Add a similar helper for Ehlers top-3**

Append to `scripts/run_portfolio_combined.py` (below `_run_clenow_top3`):

```python
def _run_ehlers_top3(
    spy_data: pd.DataFrame,
    start: date,
    end: date,
    cash: float,
    n_jobs: int,
    checkpoint_dir: Path,
    run_id: str,
):
    """Run the 3 top-3 Ehlers configs on SPY; return a list of 3 equity curves."""
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.grid import EhlersGridConfig, GridRunner
    from ai_trade.backtest.strategies.ehlers_bp_swing import (
        EhlersBPSwingStrategy,
    )

    from ai_trade.backtest.portfolio.configs import ehlers_top3_grid_configs
    ehlers_configs = ehlers_top3_grid_configs()

    data = {"SPY": spy_data}
    data_bounded = {
        "SPY": spy_data.loc[pd.Timestamp(start) : pd.Timestamp(end)]
    }

    def trial_fn(cfg: EhlersGridConfig):
        strategy = EhlersBPSwingStrategy(
            data=data,
            symbol="SPY",
            hp_period=cfg.hp_period,
            lp_period=cfg.lp_period,
            pct_of_dcp=cfg.pct_of_dcp,
            stop_pct=cfg.stop_pct,
            upper_threshold=cfg.upper_threshold,
            lower_threshold=cfg.lower_threshold,
            agc_decay=cfg.agc_decay,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
            period_min=cfg.period_min,
            period_max=cfg.period_max,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

    log.info("Running Ehlers top-3 grid (3 configs)")
    grid = GridRunner(
        checkpoint_dir=checkpoint_dir,
        n_jobs=n_jobs,
        config_cls=EhlersGridConfig,
    ).run(
        configs=ehlers_configs, trial_fn=trial_fn,
        run_id=f"{run_id}_ehlers",
    )
    ok = grid.ok_trials
    if len(ok) != 3:
        raise RuntimeError(
            f"Expected 3 OK Ehlers trials; got {len(ok)}. Error msgs: "
            f"{[t.error_msg for t in grid.trials if t.status == 'error']}"
        )
    return [t.result.equity_curve for t in ok]
```

- [ ] **Step 3: Verify the file parses**

Run:
```bash
.venv/bin/python -c "import ast; ast.parse(open('scripts/run_portfolio_combined.py').read())" 2>&1
```

Expected: no output (syntax valid).

---

## Task 9: CLI — data loading wiring

**Files:**
- Modify: `scripts/run_portfolio_combined.py`

- [ ] **Step 1: Add a helper that loads SPY + SPX universe via Tiingo**

Append to `scripts/run_portfolio_combined.py` (above the sub-grid helpers):

```python
def _load_data(
    start: date,
    end: date,
    index_symbol: str,
    storage_root: Path,
    warmup_days: int,
):
    """Load Clenow SPX point-in-time universe + index proxy + Ehlers SPY.

    Mirrors ``scripts/run_grid_clenow.py`` lines 116-195: uses
    :class:`WikipediaSPX` for point-in-time constituents, Tiingo storage
    for OHLCV, and returns the ``constituents_provider`` closure that
    intersects Wikipedia membership with actually-loaded tickers (so
    Clenow doesn't attempt to trade a ticker with no data).

    Returns
    -------
    clenow_data : dict[ticker, OHLCV DataFrame]
        Point-in-time universe + index proxy (SPY). Input to
        ``_run_clenow_top3``.
    spy_data : pd.DataFrame
        SPY OHLCV slice — passed to Ehlers as its sole instrument.
    constituents_provider : Callable[[date], set[str]]
        Closure: given a date, returns the subset of the SPX
        point-in-time constituents that we actually have data for on
        that date. Required by ``ClenowMomentumStrategy``.
    """
    from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX

    src = _build_tiingo_source(storage_root)
    fetch_start = start - timedelta(days=warmup_days)

    log.info("Loading Wikipedia SPX point-in-time membership")
    wiki = WikipediaSPX()
    universe_at_start = wiki.constituents_on(start)
    log.info(
        "Point-in-time universe on %s: %d tickers",
        start, len(universe_at_start),
    )

    tickers = sorted(universe_at_start)
    if index_symbol not in tickers:
        tickers.append(index_symbol)

    log.info(
        "Fetching %d tickers %s → %s via Tiingo",
        len(tickers), fetch_start, end,
    )
    raw = src.fetch_many(tickers, fetch_start, end, asset_class="equity")
    clenow_data = {t: df for t, df in raw.items() if not df.empty}
    dropped = len(raw) - len(clenow_data)
    if dropped:
        log.warning(
            "Tiingo returned no data for %d tickers (survivorship-honest: "
            "these are absent from the manifest on purpose)",
            dropped,
        )
    if index_symbol not in clenow_data:
        raise RuntimeError(
            f"No Tiingo data for index proxy {index_symbol} — abort"
        )

    # SPY used by Ehlers as its sole instrument. It's in clenow_data already
    # because it's also the Clenow index proxy.
    spy_df = clenow_data[index_symbol]

    available = set(clenow_data.keys())

    def constituents_provider(d: date) -> set[str]:
        return wiki.constituents_on(d) & available

    log.info(
        "Data ready: %d Clenow tickers (post-drop), SPY bars=%d",
        len(clenow_data), len(spy_df),
    )
    return clenow_data, spy_df, constituents_provider
```

- [ ] **Step 2: Verify the file still parses**

Run:
```bash
.venv/bin/python -c "import ast; ast.parse(open('scripts/run_portfolio_combined.py').read())" 2>&1
```

Expected: no output.

---

## Task 10: CLI — portfolio generation + validation wiring

**Files:**
- Modify: `scripts/run_portfolio_combined.py`

- [ ] **Step 1: Add portfolio-assembly helper**

Append to `scripts/run_portfolio_combined.py` (below `_run_ehlers_top3`):

```python
def _build_portfolio_grid(
    clenow_curves: list[pd.Series],
    ehlers_curves: list[pd.Series],
    initial_cash: float,
    run_id: str,
):
    """Combine 3 Clenow × 3 Ehlers equity curves into 9 portfolios.

    Returns a synthetic GridResult[PortfolioConfig] with 9 TrialResults,
    ready for the existing gate pipeline.
    """
    from ai_trade.backtest.grid.result import GridResult
    from ai_trade.backtest.portfolio.combined import (
        combine_equity_curves,
        make_portfolio_trial,
    )
    from ai_trade.backtest.portfolio.configs import portfolio_configs

    configs = portfolio_configs()
    assert len(configs) == 9

    trials = []
    for i, cfg in enumerate(configs):
        # Map config IDs back to the index in the top-3 tuples.
        # portfolio_configs() order: outer=Clenow ranks, inner=Ehlers ranks.
        clenow_rank = i // 3
        ehlers_rank = i % 3
        c_curve = clenow_curves[clenow_rank]
        e_curve = ehlers_curves[ehlers_rank]
        combined = combine_equity_curves(
            [c_curve, e_curve],
            [0.5, 0.5],
            initial_capital=initial_cash,
        )
        trials.append(
            make_portfolio_trial(
                config_id=i,
                config=cfg,
                equity_curve=combined,
                initial_cash=initial_cash,
            )
        )

    return GridResult(trials=trials, run_id=run_id)
```

- [ ] **Step 2: Add main-function orchestration to tie it all together**

In `scripts/run_portfolio_combined.py`, **replace** the stub `main()` function (the one with `log.warning("main() stub...")`) with:

```python
def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    run_id = args.run_id or f"grid_portfolio_{datetime.now().strftime('%Y%m%d-%H%M')}"
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    from ai_trade.backtest.grid import (
        DiagnosticAnalyzer, GateEvaluator, GridReportGenerator,
        setup_grid_logging, wf_for_grid,
    )

    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"),
        level=getattr(logging, args.log_level),
    )
    log.info("=== F3.D portfolio run %s ===", run_id)
    log.info(
        "start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        args.start, args.end, args.cash, args.n_jobs, args.dry_run,
    )

    # 1. Load data.
    clenow_data, spy_data, constituents_provider = _load_data(
        start=args.start, end=args.end,
        index_symbol=args.index_symbol,
        storage_root=args.storage_root,
        warmup_days=args.warmup_days,
    )

    # 2. Run sub-grids (3 Clenow + 3 Ehlers).
    clenow_curves = _run_clenow_top3(
        data=clenow_data,
        constituents_provider=constituents_provider,
        index_symbol=args.index_symbol,
        start=args.start, end=args.end, cash=args.cash,
        n_jobs=args.n_jobs,
        checkpoint_dir=checkpoint_dir, run_id=run_id,
    )
    ehlers_curves = _run_ehlers_top3(
        spy_data=spy_data,
        start=args.start, end=args.end, cash=args.cash,
        n_jobs=args.n_jobs,
        checkpoint_dir=checkpoint_dir, run_id=run_id,
    )

    # 3. Combine 9 portfolios.
    portfolio_grid = _build_portfolio_grid(
        clenow_curves=clenow_curves,
        ehlers_curves=ehlers_curves,
        initial_cash=args.cash,
        run_id=run_id,
    )
    log.info(
        "9 portfolios built: Sharpes=%s",
        [f"{t.sharpe:.3f}" for t in portfolio_grid.ok_trials],
    )

    if args.dry_run:
        log.info("--dry-run: skipping validation/report")
        for t in portfolio_grid.ok_trials:
            log.info(
                "cfg %d (clenow=%d, ehlers=%d): Sharpe %.3f CAGR %.2f%% DD %.2f%%",
                t.config_id,
                t.config.clenow_config_id,
                t.config.ehlers_config_id,
                t.sharpe, t.cagr * 100, t.max_drawdown * 100,
            )
        return 0

    # 4. Walk-forward per combined portfolio.
    log.info("Running walk-forward per portfolio (n_windows=8)")
    wf_results = wf_for_grid(portfolio_grid, n_windows=8, n_jobs=args.n_jobs)

    # 5. Gate evaluation.
    log.info("Evaluating gates (PBO, DSR, walk-forward)")
    verdict = GateEvaluator().evaluate(
        grid=portfolio_grid,
        wf_verdicts={cid: wf.verdict for cid, wf in wf_results.items()},
    )
    pbo_val = (
        float(verdict.pbo_result.pbo)
        if verdict.pbo_result else float("nan")
    )
    log.info(
        "Gate verdict: overall_pass=%s best_config_id=%s "
        "pbo=%.3f dsr_pass=%d/%d wf_pass=%d/%d",
        verdict.overall_pass, verdict.best_config_id, pbo_val,
        len(verdict.dsr_pass_ids), len(verdict.dsr_results),
        len(verdict.wf_pass_ids), len(verdict.wf_verdicts),
    )

    # 6. Report.
    report_gen = GridReportGenerator()
    if verdict.overall_pass:
        path = report_gen.write_pass_report(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("FAIL diagnostic report: %s", path)
        log.info(
            "Failure modes: %s",
            [m.label for m in diagnostic.failure_modes],
        )

    log.info("=== F3.D portfolio run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2
```

- [ ] **Step 3: Verify the file parses + `--help` still works**

Run:
```bash
.venv/bin/python -c "import ast; ast.parse(open('scripts/run_portfolio_combined.py').read())"
.venv/bin/python scripts/run_portfolio_combined.py --help 2>&1 | head -5
```

Expected: first command silent; second prints argparse help with `usage:` line.

---

## Task 11: Commit Phase 2 (CLI script)

**Files:** (no new edits — just commit)

- [ ] **Step 1: Stage the CLI + commit**

Run:
```bash
cd /var/www/pessoal/ai-trade
git add scripts/run_portfolio_combined.py
git commit -m "$(cat <<'EOF'
feat(portfolio): CLI orchestrator for F3.D combined portfolio grid

scripts/run_portfolio_combined.py runs the 9-portfolio pipeline
end-to-end: load Tiingo SPX+SPY → run Clenow top-3 grid → run Ehlers
top-3 grid → combine 9 portfolios via weighted daily returns → walk-
forward → PBO/DSR gate → diagnostic report.

Mirrors the pattern of scripts/run_grid_clenow.py and run_grid_ehlers.py:
unified logs/grid.log, per-run .cache/grid_runs/{run_id}/ checkpoints,
tiingo storage-first, argparse with --start/--end/--cash/--dry-run.

Refs: docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md
EOF
)"
printf '[2026-04-15 session] Phase 2 complete — CLI committed (%s)\n' \
  "$(git rev-parse --short HEAD)" >> logs/f3d.log
```

Expected: clean commit.

---

## Task 12: Smoke test (short 2-year window)

**Files:** (none modified — just verify the pipeline works end-to-end)

- [ ] **Step 1: Dry-run smoke test over a short window (2022-2023, 2 years)**

Run:
```bash
cd /var/www/pessoal/ai-trade
.venv/bin/python scripts/run_portfolio_combined.py \
    --start 2022-01-01 --end 2023-12-31 \
    --cash 100000 \
    --dry-run \
    --output-dir /tmp/f3d_smoke 2>&1 | tail -30
```

Expected output last lines:
- `9 portfolios built: Sharpes=['...', '...', ...]` (9 numeric values)
- 9 lines like `cfg 0 (clenow=8, ehlers=6): Sharpe 0.XXX CAGR X.XX% DD X.XX%`
- `F3.D portfolio run ... done`
- Exit code 0

If smoke run crashes: fix the error, re-run until clean. Do NOT proceed to v1 on a broken smoke.

- [ ] **Step 2: Log smoke success**

Run:
```bash
printf '[2026-04-15 session] Smoke test passed — 9 portfolios built on 2022-2023 window\n' \
  >> logs/f3d.log
```

---

## Task 13: Run v1 — 2015-2023 (baseline window)

**Files:** (generates output under `reports/grid_portfolio_*/`)

- [ ] **Step 1: Full run on 2015-2023**

Run:
```bash
cd /var/www/pessoal/ai-trade
.venv/bin/python scripts/run_portfolio_combined.py \
    --start 2015-01-01 --end 2023-12-31 \
    --cash 100000 \
    --output-dir reports/ 2>&1 | tee -a logs/f3d.log
```

Expected: exit code 0 (PASS) or 2 (FAIL gates). Crash (exit 1) means investigate — do NOT proceed.

Expected wallclock: < 10 minutes on a multi-core box (3 Clenow configs on SPX 500 is the slowest part; Ehlers is seconds).

- [ ] **Step 2: Inspect the diagnostic report**

Run:
```bash
ls -lt reports/ | head -5
# Note the most recent grid_portfolio_* directory:
REPORT_DIR=$(ls -dt reports/grid_portfolio_* | head -1)
echo "Report: $REPORT_DIR"
head -80 "$REPORT_DIR/diagnostic.md"
```

Expected: gate verdict block (PASS or FAIL) plus per-config metrics table with 9 rows.

- [ ] **Step 3: Extract v1 verdict into logs/f3d.log**

Run:
```bash
REPORT_DIR=$(ls -dt reports/grid_portfolio_* | head -1)
VERDICT=$(grep -m1 "Gate verdict" "$REPORT_DIR/diagnostic.md" | head -1)
printf '[2026-04-15 session] v1 (2015-2023) complete — %s\n[2026-04-15 session]   Report: %s\n' \
  "$VERDICT" "$REPORT_DIR" >> logs/f3d.log
```

---

## Task 14: Go/no-go decision — Run v2 (2005-2023) if v1 passed

**Files:** (generates `reports/grid_portfolio_*/` for v2)

- [ ] **Step 1: Read v1 verdict and decide**

Inspect the v1 `diagnostic.md` under the `Gate verdict` heading:

- If **`PASS`**: proceed to Step 2 (run v2).
- If **`FAIL`**: skip to Task 15 (postmortem + docs). Do NOT run v2 — v1 is the cheaper test and a fail there already rejects H1.

- [ ] **Step 2 (only if v1 PASS): Full run on 2005-2023**

Run:
```bash
cd /var/www/pessoal/ai-trade
.venv/bin/python scripts/run_portfolio_combined.py \
    --start 2005-01-01 --end 2023-12-31 \
    --cash 100000 \
    --output-dir reports/ 2>&1 | tee -a logs/f3d.log
```

Expected wallclock: ~3× the v1 run (longer window, more bars).

- [ ] **Step 3: Extract v2 verdict**

Run:
```bash
REPORT_DIR=$(ls -dt reports/grid_portfolio_* | head -1)
VERDICT=$(grep -m1 "Gate verdict" "$REPORT_DIR/diagnostic.md" | head -1)
printf '[2026-04-15 session] v2 (2005-2023) complete — %s\n[2026-04-15 session]   Report: %s\n' \
  "$VERDICT" "$REPORT_DIR" >> logs/f3d.log
```

---

## Task 15: Document verdict — JORNADA.md + ROADMAP.md

**Files:**
- Modify: `JORNADA.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Add a dated changelog entry to `JORNADA.md`**

Open `JORNADA.md`. Below the line `# Changelog (entradas datadas)` and above the most recent existing entry (`## 2026-04-15 (tarde, segundo round) — Long-history Ehlers SPY...`), insert:

```markdown
## 2026-04-15 (noite) — F3.D Portfolio Clenow+Ehlers — {PASS|FAIL} v1, {PASS|FAIL|N/A} v2

**Hipótese:** se Clenow e Ehlers têm correlação de equity ≈ −0.01 (Run 2 verdict),
combiná-los num portfolio 50/50 "dois livros" pode elevar o Sharpe efetivo o
suficiente pra passar DSR (~1.0 pela matemática de diversificação) sem
inflacionar N_trials (9 configs fixas vs 24-48 de grids monolíticos).

**O que rodamos:** top-3 Clenow (Tiingo 2015-2023) × top-3 Ehlers (long-history
2005-2023) = 9 portfolios; merge offline via retornos ponderados; sem rebalance;
gates CPCV/PBO/DSR/WF inalterados.

**Resultado v1 (2015-2023):**
- PBO: {VALOR} ({PASS/FAIL})
- DSR: {N/9} passam p<0.05 (best p={VALOR})
- WF: {N/9} passam (≥6/8 profitable, DD≤25%)
- Best Sharpe: {VALOR} ({nome da config})
- σ_Clenow / σ_Ehlers observado: {VALOR} (caveat vol mismatch da spec §5)

{Se v1 PASS, acrescentar bloco resultado v2; se v1 FAIL, pular}

**Conclusão leiga:** {preencher com 3-5 linhas de interpretação — se passou,
qual o próximo passo realista (Phase 3? Phase 4 prep? regime filter no Ehlers?);
se falhou, qual a postmortem honesta — crash correlation em crises? vol mismatch?
selection bias residual? — e qual o próximo passo da lista: AFML sofisticado vs
outro}.

**Próximo passo recomendado:** {preencher}

**Arquivos gerados:**
- `reports/grid_portfolio_YYYYMMDD-HHMM/diagnostic.md` (v1 — 9 configs)
- {v2 se aplicável}
- Código novo em `src/ai_trade/backtest/portfolio/` (commits {sha1}+{sha2})

---

```

Then fill in the `{placeholders}` with the actual values from the two diagnostic reports. Do NOT leave any `{}` in the final file.

- [ ] **Step 2: Update `ROADMAP.md` §"Current status"**

In `ROADMAP.md`, find the section `🔄 Phase 2.5 — Run 4 prep (post-mortem + AFML rescue attempt, 2026-04-15)` and **replace** it (or add a new `✅`/`🔄` bullet below it) with a status bullet describing F3.D outcome.

If F3.D **passed both windows:**
- Change the status to `✅ Phase 2.5 — Run 4 Step 2 (F3.D Portfolio Clenow+Ehlers, 2026-04-15). {PASS summary}. Next step: Phase 3 (Universe Selector) or Phase 4 prep.`
- Update `⏳ Next steps` ordered list to remove items 1-6 and put Phase 3 entry as item 1.

If F3.D **failed v1 or v2:**
- Add `🔄 Phase 2.5 — Run 4 Step 2 (F3.D Portfolio Clenow+Ehlers, 2026-04-15) — FAIL. {reason}. Path B (AFML sophisticated) enters next cycle.`
- Update `⏳ Next steps` to promote "AFML sophisticated with walk-forward CV + rich features" to item 1.

- [ ] **Step 3: Commit docs + finalize**

Run:
```bash
cd /var/www/pessoal/ai-trade
git add JORNADA.md ROADMAP.md
git commit -m "$(cat <<'EOF'
docs(jornada,roadmap): F3.D portfolio verdict — {PASS|FAIL}

v1 (2015-2023): {1-line summary with PBO/DSR/WF numbers}
v2 (2005-2023): {1-line summary or N/A if v1 failed}

Full diagnostic: reports/grid_portfolio_<run_id>/diagnostic.md
Design: docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md

{If PASS:} Next step advances to Phase 3 / Phase 4 prep.
{If FAIL:} Next step pivots to AFML sophisticated (path B).
EOF
)"

printf '[2026-04-15 session] F3.D session complete — docs committed (%s)\n' \
  "$(git rev-parse --short HEAD)" >> logs/f3d.log
```

Expected: clean commit. Fill in the placeholders with real verdict values from the reports.

- [ ] **Step 4: Final sanity — ensure 374+ tests still green**

Run:
```bash
.venv/bin/pytest -q 2>&1 | tail -3
```

Expected: `374 passed` (or more if verification added more tests along the way). Any regression halts the session — investigate immediately.

---

## Appendix A — Risk and fallback paths

### If a sub-grid produces < 3 OK trials

`_run_clenow_top3` and `_run_ehlers_top3` raise `RuntimeError` with the error messages. Most likely culprits:
- Missing warmup data for a Tiingo ticker → check TiingoStorage manifest for the symbol
- Grid config mismatch with strategy signature → compare the constructor of `ClenowMomentumStrategy` / `EhlersBPSwingStrategy` against what the helpers pass

Fix the underlying cause; do NOT lower the assertion to "≥ 1" or similar — all 9 portfolios are required for a clean DSR N=9 deflation.

### If the CPCV / PSR gate is missing from the existing `GateEvaluator`

The spec §3.2 mentions **CPCV PSR > 0.95** as an additional gate. Check whether `GateEvaluator.evaluate` already computes PSR — if not, that is a **spec scope change** that should NOT be added to this plan. File a follow-up task: "Add CPCV+PSR gate to GateEvaluator (applies to all grids, not just F3.D)". The current plan relies on the existing 3 gates (PBO, DSR, WF), which match the framework used by Runs 1-3.

### If `_load_data` diverges from `scripts/run_grid_clenow.py` conventions

The `_load_data` helper in Task 9 mirrors `scripts/run_grid_clenow.py` lines 116-195 (WikipediaSPX point-in-time + Tiingo fetch + available-intersection `constituents_provider`). If the existing Clenow script has drifted in a newer commit, update `_load_data` to match — do NOT diverge.

---

## Appendix B — Commit hygiene

Per `.claude/CLAUDE.md` (Convenções de código): Conventional Commits with prefixes `feat:` / `fix:` / `docs:` / `chore:`.

This plan produces **3-4 commits**:
1. `feat(portfolio): core offline combination utility for F3.D` (Task 6)
2. `feat(portfolio): CLI orchestrator for F3.D combined portfolio grid` (Task 11)
3. (optional) `fix(portfolio): <anything caught during smoke test Task 12>`
4. `docs(jornada,roadmap): F3.D portfolio verdict — {PASS|FAIL}` (Task 15)

Do NOT amend or squash — each commit stands on its own. Pre-commit hooks may exist; do NOT skip them.
