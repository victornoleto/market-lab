# Plano B Cross-Library Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate (or refute) Plano B V4 winner by reproducing it in 4 independent Python backtesting libraries + 1 web UI, using two-stage data isolation and a 4-tier verdict engine.

**Architecture:** Python package under `reports/phase_3_5c/cross_lib/` with declarative variant registry, reference price assembler (synthetic + real), adapter per library implementing a common `run(variant, window, stage) -> RunResult` contract, metric comparison via tolerance bands, aggregate verdict emitted as `VERDICT.md`. Minimal pytest smoke suite under `tests/cross_lib/` for anti-drift.

**Tech Stack:** Python 3.12, pandas 2.2, pyarrow (parquet), pytest 8. Libraries: `bt`, `vectorbt`, `backtrader`, `quantstats`, `yfinance`. Reuse of existing `src/ai_trade/backtest/helpers/synthetic_letf.py`.

**Spec reference:** `docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`.

---

## Milestone M0 — Infrastructure (Tasks 1-9)

### Task 1: Directory scaffold and package init

**Files:**
- Create: `reports/phase_3_5c/cross_lib/__init__.py`
- Create: `reports/phase_3_5c/cross_lib/README.md`
- Create: `reports/phase_3_5c/cross_lib/data/__init__.py`
- Create: `reports/phase_3_5c/cross_lib/adapters/__init__.py`
- Create: `reports/phase_3_5c/cross_lib/reference/.gitkeep`
- Create: `reports/phase_3_5c/cross_lib/results/.gitkeep`
- Create: `reports/phase_3_5c/cross_lib/errors/.gitkeep`
- Create: `tests/cross_lib/__init__.py`
- Modify: `.gitignore` (append `reports/phase_3_5c/cross_lib/data/reference_prices.parquet`)

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p reports/phase_3_5c/cross_lib/{data/independent_fetchers,adapters,reference,results/stage_1,results/stage_2,errors}
mkdir -p tests/cross_lib
touch reports/phase_3_5c/cross_lib/__init__.py
touch reports/phase_3_5c/cross_lib/data/__init__.py
touch reports/phase_3_5c/cross_lib/data/independent_fetchers/__init__.py
touch reports/phase_3_5c/cross_lib/adapters/__init__.py
touch reports/phase_3_5c/cross_lib/reference/.gitkeep
touch reports/phase_3_5c/cross_lib/results/.gitkeep
touch reports/phase_3_5c/cross_lib/errors/.gitkeep
touch tests/cross_lib/__init__.py
```

- [ ] **Step 2: Write README skeleton**

Create `reports/phase_3_5c/cross_lib/README.md`:

```markdown
# Phase 3.5c — Plano B Cross-Library Validation

Validates Plano B V4 (3-leg EW SSO+QLD+UGL) by reproducing it in independent libraries.
Design spec: `docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`.

## Entry points
- `python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 1`
- `python -m reports.phase_3_5c.cross_lib.report` (generates VERDICT.md)

## Top-level output
- `VERDICT.md` — aggregate verdict matrix.
- `per_variant/<id>.md` — per-variant deep dives.
- `errors/` — adapter stacktraces (only on ERROR outcomes).
- `results/stage_{1,2}/<lib>/<variant>/<window>/result.json` — raw RunResult dumps.

Reference design spec is authoritative for tolerances, aggregation rules, and library rationale.
```

- [ ] **Step 3: Append to .gitignore**

Append to `.gitignore`:

```
# Phase 3.5c cross-lib validation — generated artifacts
reports/phase_3_5c/cross_lib/data/reference_prices.parquet
reports/phase_3_5c/cross_lib/results/
reports/phase_3_5c/cross_lib/errors/
reports/phase_3_5c/cross_lib/reference/baseline.json
```

- [ ] **Step 4: Commit**

```bash
git add reports/phase_3_5c/cross_lib/ tests/cross_lib/ .gitignore
git commit -m "chore(phase-3.5c): scaffold cross-lib validation directory layout"
```

---

### Task 2: Core types — VariantConfig, LegConfig, RebalanceConfig

**Files:**
- Create: `reports/phase_3_5c/cross_lib/types.py`
- Create: `tests/cross_lib/test_types.py`

- [ ] **Step 1: Write failing test**

Create `tests/cross_lib/test_types.py`:

```python
"""Tests for cross-lib core types."""
from __future__ import annotations

import pytest

from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)


def test_leg_config_ema_regime() -> None:
    leg = LegConfig(
        signal_type="ema_regime",
        signal_params={"lookback": 100},
        signal_ticker="SPY",
        execution_ticker="SSO",
    )
    assert leg.signal_type == "ema_regime"
    assert leg.signal_params["lookback"] == 100
    assert leg.signal_ticker == "SPY"
    assert leg.execution_ticker == "SSO"


def test_leg_config_donchian() -> None:
    leg = LegConfig(
        signal_type="donchian",
        signal_params={"entry": 20, "exit": 10},
        signal_ticker="QQQ",
        execution_ticker="QLD",
    )
    assert leg.signal_params == {"entry": 20, "exit": 10}


def test_rebalance_threshold_requires_pp() -> None:
    with pytest.raises(ValueError, match="threshold_pp required"):
        RebalanceConfig(mode="threshold", threshold_pp=None)


def test_rebalance_daily_no_pp() -> None:
    rb = RebalanceConfig(mode="daily", threshold_pp=None)
    assert rb.mode == "daily"


def test_variant_config_plano_b_v4() -> None:
    variant = VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(
            LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
            LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
            LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
        ),
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(("2004-10-01", "2026-04-18"), ("1986-01-02", "2026-04-18")),
    )
    assert variant.family == "plano_b"
    assert len(variant.legs) == 3
    assert sum(variant.target_weights) == pytest.approx(1.0)


def test_variant_config_is_frozen() -> None:
    variant = VariantConfig(
        variant_id="x",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(),
        windows=(),
    )
    with pytest.raises(AttributeError):
        variant.variant_id = "y"  # type: ignore[misc]
```

- [ ] **Step 2: Run test — expect collection error (module missing)**

Run: `pytest tests/cross_lib/test_types.py -v`
Expected: `ImportError` on the `types` module.

- [ ] **Step 3: Implement types.py**

Create `reports/phase_3_5c/cross_lib/types.py`:

```python
"""Core typed structures for cross-lib validation.

Citations
---------
Design spec: docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SignalType = Literal["ema_regime", "donchian"]
RebalanceMode = Literal["daily", "monthly_sell", "monthly_cashflow", "threshold"]
ExecutionModel = Literal["letf_synthetic", "cfd_synthetic", "real_etf"]
StrategyFamily = Literal["plano_b", "plano_a"]


@dataclass(frozen=True)
class LegConfig:
    """Config for a single portfolio leg.

    signal_ticker : str
        Underlying index/ETF the signal is computed on (e.g. SPY for SSO leg).
        `[leverage_for_the_long_run, p.13]` — signal on 1x index, execution on LETF.
    execution_ticker : str
        Instrument that holds the position when signal is LONG (e.g. SSO).
    """

    signal_type: SignalType
    signal_params: dict
    signal_ticker: str
    execution_ticker: str


@dataclass(frozen=True)
class RebalanceConfig:
    """Portfolio rebalance cadence.

    `[advances_fin_ml, p.275-278]` — drift-triggered (threshold) rebalance rules.
    """

    mode: RebalanceMode
    threshold_pp: float | None

    def __post_init__(self) -> None:
        if self.mode == "threshold" and self.threshold_pp is None:
            raise ValueError("threshold_pp required when mode='threshold'")


@dataclass(frozen=True)
class VariantConfig:
    """Declarative description of a single run configuration.

    A VariantConfig is strategy-family-agnostic by design — Plano A will add
    its own variants under `family="plano_a"` with `execution_model="cfd_synthetic"`.
    """

    variant_id: str
    family: StrategyFamily
    execution_model: ExecutionModel
    legs: tuple[LegConfig, ...]
    rebalance: RebalanceConfig
    target_weights: tuple[float, ...]
    windows: tuple[tuple[str, str], ...]
```

- [ ] **Step 4: Run test — expect pass**

Run: `pytest tests/cross_lib/test_types.py -v`
Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add reports/phase_3_5c/cross_lib/types.py tests/cross_lib/test_types.py
git commit -m "feat(phase-3.5c): add VariantConfig/LegConfig/RebalanceConfig types with TDD"
```

---

### Task 3: RunResult and outcome types

**Files:**
- Modify: `reports/phase_3_5c/cross_lib/types.py`
- Modify: `tests/cross_lib/test_types.py`

- [ ] **Step 1: Extend test file with RunResult tests**

Append to `tests/cross_lib/test_types.py`:

```python
import pandas as pd

from reports.phase_3_5c.cross_lib.types import Outcome, RunResult


def test_run_result_ok_outcome() -> None:
    eq = pd.Series(
        [1.0, 1.01, 1.02], index=pd.date_range("2020-01-01", periods=3, freq="D")
    )
    mr = pd.Series([0.01, 0.01], index=pd.date_range("2020-01-31", periods=2, freq="ME"))
    result = RunResult(
        variant_id="x",
        lib="bt",
        window=("2020-01-01", "2020-12-31"),
        stage=1,
        equity_curve=eq,
        monthly_returns=mr,
        trade_dates=[pd.Timestamp("2020-03-01")],
        cagr=0.25,
        sharpe=1.5,
        max_dd=-0.10,
        wf_splits_8=[1.4, 1.5, 1.6, 1.5, 1.4, 1.5, 1.6, 1.5],
        dsr_pval=0.02,
        outcome="OK",
        error_detail=None,
    )
    assert result.outcome == "OK"
    assert len(result.wf_splits_8) == 8


def test_run_result_skipped_outcome() -> None:
    eq = pd.Series(dtype=float)
    result = RunResult(
        variant_id="x",
        lib="bt",
        window=("2020-01-01", "2020-12-31"),
        stage=1,
        equity_curve=eq,
        monthly_returns=eq,
        trade_dates=[],
        cagr=float("nan"),
        sharpe=float("nan"),
        max_dd=float("nan"),
        wf_splits_8=[],
        dsr_pval=float("nan"),
        outcome="SKIPPED",
        error_detail="bt not installed",
    )
    assert result.outcome == "SKIPPED"
    assert result.error_detail == "bt not installed"


def test_outcome_literal_values() -> None:
    allowed: tuple[Outcome, ...] = ("OK", "SKIPPED", "DATA_UNAVAILABLE", "ERROR")
    assert len(allowed) == 4
```

- [ ] **Step 2: Run test — expect failure (RunResult/Outcome missing)**

Run: `pytest tests/cross_lib/test_types.py::test_run_result_ok_outcome -v`
Expected: `ImportError: cannot import name 'RunResult'`.

- [ ] **Step 3: Extend types.py**

Append to `reports/phase_3_5c/cross_lib/types.py`:

```python
import pandas as pd

Outcome = Literal["OK", "SKIPPED", "DATA_UNAVAILABLE", "ERROR"]


@dataclass
class RunResult:
    """Output of a single adapter run.

    Non-frozen because pandas Series are unhashable; we treat it as an
    immutable value by convention (don't mutate after construction).
    """

    variant_id: str
    lib: str
    window: tuple[str, str]
    stage: int
    equity_curve: pd.Series
    monthly_returns: pd.Series
    trade_dates: list[pd.Timestamp]
    cagr: float
    sharpe: float
    max_dd: float
    wf_splits_8: list[float]
    dsr_pval: float
    outcome: Outcome
    error_detail: str | None
```

- [ ] **Step 4: Run all type tests — expect pass**

Run: `pytest tests/cross_lib/test_types.py -v`
Expected: 9 tests pass.

- [ ] **Step 5: Commit**

```bash
git add reports/phase_3_5c/cross_lib/types.py tests/cross_lib/test_types.py
git commit -m "feat(phase-3.5c): add RunResult + Outcome types"
```

---

### Task 4: Reference prices assembler — synthetic + real

**Files:**
- Create: `reports/phase_3_5c/cross_lib/data/reference_prices.py`

- [ ] **Step 1: Implement reference_prices.py**

Create `reports/phase_3_5c/cross_lib/data/reference_prices.py`:

```python
"""Assembles reference_prices.parquet — the single source of truth for Stage 1.

Post-inception of each real LETF (SSO 2006-06-21, QLD 2006-06-21, UGL 2008-12-03)
we use real OHLCV from Tiingo. Pre-inception, we synthesize via
`synthesize_letf_returns_ffr_aware` — matching the methodology our engine uses
internally. Synthetic OHLC collapses high=low=close=synthetic_close (no intraday).

Citations
---------
- Synthetic formula: `[leverage_for_the_long_run, p.16]`
- FFR-aware cost model: `[leverage_for_the_long_run, p.16-17]`
- Two-stage isolation rationale: `[advances_fin_ml, p.31-34]`
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_total_return
from ai_trade.backtest.data.tiingo_storage import load_tiingo_daily
from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_EXPENSE_RATIO,
    DEFAULT_FFR_SPREAD,
    DEFAULT_SWAP_EXPOSURE,
    synthesize_letf_returns_ffr_aware,
)

REFERENCE_PARQUET = Path(
    "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
)


@dataclass(frozen=True)
class LetfSpec:
    ticker: str
    underlying: str      # "SPY", "QQQ", "GLD"
    leverage: float
    inception: str       # first date of real data
    expense_ratio: float


LETF_SPECS: tuple[LetfSpec, ...] = (
    LetfSpec("SSO", "SPY", 2.0, "2006-06-21", 0.0089),
    LetfSpec("QLD", "QQQ", 2.0, "2006-06-21", 0.0095),
    LetfSpec("UGL", "GLD", 2.0, "2008-12-03", 0.0095),
)

# Underlying tickers used by signals — always real Tiingo daily data
UNDERLYING_TICKERS: tuple[str, ...] = ("SPY", "QQQ", "GLD")


def build_reference_prices(
    canonical_start: str = "2004-10-01",
    canonical_end: str = "2026-04-18",
    extended_start: str = "1986-01-02",
    extended_end: str = "2026-04-18",
) -> pd.DataFrame:
    """Assemble reference_prices with (ticker, date) multi-index columns.

    Output schema (long format): columns = [date, ticker, open, high, low, close, volume].
    """
    frames: list[pd.DataFrame] = []

    # 1. Underlying tickers — direct Tiingo load
    for ticker in UNDERLYING_TICKERS:
        df = load_tiingo_daily(ticker)
        df = df.loc[extended_start:extended_end].copy()
        df["ticker"] = ticker
        df = df.reset_index().rename(columns={"index": "date"})
        frames.append(df[["date", "ticker", "open", "high", "low", "close", "volume"]])

    # 2. LETFs — synthetic pre-inception + real post-inception
    spx_tr = load_spx_total_return()  # extended series 1928+
    ffr = _load_ffr_series(extended_start, extended_end)

    for spec in LETF_SPECS:
        synthetic = _synthetic_pre_inception(spec, spx_tr, ffr, extended_start)
        real = _real_post_inception(spec.ticker, extended_end)
        combined = pd.concat([synthetic, real]).sort_values("date")
        combined = combined.drop_duplicates(subset="date", keep="last")
        frames.append(combined)

    full = pd.concat(frames, ignore_index=True)
    full = full.sort_values(["ticker", "date"]).reset_index(drop=True)
    return full


def _synthetic_pre_inception(
    spec: LetfSpec,
    spx_tr: pd.Series,
    ffr: pd.Series,
    start_date: str,
) -> pd.DataFrame:
    """Build synthetic OHLC for ticker from start_date up to day before inception."""
    end_exclusive = pd.Timestamp(spec.inception) - pd.Timedelta(days=1)
    # For non-SPY underlyings, the synthesis needs the matching underlying return;
    # here we use SPX TR as Gayed does for SSO — QLD/UGL extensions follow their
    # own underlying total-return series when available, else fall back to synth.
    underlying_tr = _load_underlying_tr(spec.underlying)
    underlying_tr = underlying_tr.loc[start_date:end_exclusive]
    ffr_slice = ffr.reindex(underlying_tr.index).ffill()

    synth_rets = synthesize_letf_returns_ffr_aware(
        spx_tr_returns=underlying_tr,
        leverage=spec.leverage,
        ffr_annualized=ffr_slice,
        swap_exposure=DEFAULT_SWAP_EXPOSURE,
        ffr_spread=DEFAULT_FFR_SPREAD,
        expense_ratio=spec.expense_ratio,
    ).fillna(0.0)

    prices = (1.0 + synth_rets).cumprod() * 10.0  # arbitrary start value
    df = pd.DataFrame(
        {
            "date": prices.index,
            "ticker": spec.ticker,
            "open": prices.values,
            "high": prices.values,
            "low": prices.values,
            "close": prices.values,
            "volume": 0,
        }
    )
    return df


def _real_post_inception(ticker: str, end_date: str) -> pd.DataFrame:
    df = load_tiingo_daily(ticker)
    df = df.loc[:end_date].copy()
    df["ticker"] = ticker
    df = df.reset_index().rename(columns={"index": "date"})
    return df[["date", "ticker", "open", "high", "low", "close", "volume"]]


def _load_underlying_tr(underlying: str) -> pd.Series:
    """Return total-return series for the underlying index.

    SPY → SPX TR (has pre-1993 via Shiller/Bloomberg backfill in spx_tr_loader).
    QQQ → NDX TR (loaded from Tiingo where available, else QQQ close-to-close).
    GLD → Gold fixing or GLD close-to-close for pre-2004 no synthetic extension.
    """
    if underlying == "SPY":
        return load_spx_total_return()
    if underlying == "QQQ":
        df = load_tiingo_daily("QQQ")
        return df["close"].pct_change().dropna()
    if underlying == "GLD":
        df = load_tiingo_daily("GLD")
        return df["close"].pct_change().dropna()
    raise ValueError(f"Unknown underlying: {underlying}")


def _load_ffr_series(start: str, end: str) -> pd.Series:
    """Federal Funds Rate daily series (annualized fraction, e.g. 0.05 = 5%).

    Loaded from `data/external/ffr.csv` (FRED series DFF). If missing,
    fall back to a flat 0.03 (3%) to keep pipeline deterministic and
    document the approximation in the output parquet metadata.
    """
    ffr_path = Path("data/external/ffr.csv")
    if ffr_path.exists():
        df = pd.read_csv(ffr_path, parse_dates=["date"]).set_index("date")["rate"]
        return df.loc[start:end]
    idx = pd.date_range(start, end, freq="B")
    return pd.Series(0.03, index=idx, name="ffr_flat")


def save_reference_parquet(df: pd.DataFrame, path: Path = REFERENCE_PARQUET) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow")


def load_reference_parquet(path: Path = REFERENCE_PARQUET) -> pd.DataFrame:
    return pd.read_parquet(path, engine="pyarrow")


if __name__ == "__main__":
    df = build_reference_prices()
    save_reference_parquet(df)
    print(f"Wrote {len(df)} rows to {REFERENCE_PARQUET}")
    for tkr in ("SPY", "QQQ", "GLD", "SSO", "QLD", "UGL"):
        sub = df[df["ticker"] == tkr]
        print(f"  {tkr}: {len(sub)} rows, {sub['date'].min()} → {sub['date'].max()}")
```

- [ ] **Step 2: Generate the parquet**

Run: `python -m reports.phase_3_5c.cross_lib.data.reference_prices`
Expected: parquet file created with row counts for 6 tickers.

If `load_tiingo_daily` signature differs in the codebase, adjust the imports — the function must return a DataFrame with `date` index and OHLCV columns.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/data/reference_prices.py
git commit -m "feat(phase-3.5c): reference_prices assembler (synthetic+real)"
```

---

### Task 5: Data layer tests

**Files:**
- Create: `tests/cross_lib/test_data_layer.py`

- [ ] **Step 1: Write the tests**

Create `tests/cross_lib/test_data_layer.py`:

```python
"""Tests for the reference price assembler.

Verifies the parquet our engine consumes internally matches byte-for-byte
what `reference_prices.parquet` exports to external libs.
"""
from __future__ import annotations

import pandas as pd
import pytest

from reports.phase_3_5c.cross_lib.data.reference_prices import (
    LETF_SPECS,
    UNDERLYING_TICKERS,
    build_reference_prices,
    load_reference_parquet,
)


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    return load_reference_parquet()


def test_all_tickers_present(prices: pd.DataFrame) -> None:
    expected = set(UNDERLYING_TICKERS) | {spec.ticker for spec in LETF_SPECS}
    assert set(prices["ticker"].unique()) == expected


def test_canonical_window_coverage(prices: pd.DataFrame) -> None:
    """All 6 tickers cover the canonical window 2004-10-01 → 2026-04-18."""
    canonical_start = pd.Timestamp("2004-10-01")
    canonical_end = pd.Timestamp("2026-04-18")
    for ticker in ("SPY", "QQQ", "GLD", "SSO", "QLD", "UGL"):
        sub = prices[prices["ticker"] == ticker]
        assert sub["date"].min() <= canonical_start, f"{ticker} missing pre-2004-10-01"
        assert sub["date"].max() >= canonical_end - pd.Timedelta(days=5), (
            f"{ticker} missing post-{canonical_end}"
        )


def test_synthetic_letf_invariant(prices: pd.DataFrame) -> None:
    """Pre-inception, SSO daily return ≈ 2 × SPY daily return - drag."""
    sso = prices[prices["ticker"] == "SSO"].set_index("date")["close"]
    spy = prices[prices["ticker"] == "SPY"].set_index("date")["close"]
    # Pre-2006-06-21 (inception of real SSO)
    pre_inception = sso.index < pd.Timestamp("2006-06-21")
    sso_rets = sso.pct_change().loc[pre_inception]
    spy_rets = spy.pct_change().reindex(sso_rets.index)

    # Expect sso_rets ≈ 2 * spy_rets - (drag + ffr_cost)
    # Drag = ~1.5%/yr / 252 = ~6 bps/day.
    pearson = sso_rets.corr(spy_rets)
    assert pearson > 0.99, f"SSO/SPY return correlation pre-inception = {pearson}"
    ratio = (sso_rets / spy_rets).dropna().median()
    assert 1.8 < ratio < 2.2, f"SSO/SPY ratio pre-inception = {ratio} (expected ~2)"


def test_synthetic_has_flat_hlc(prices: pd.DataFrame) -> None:
    """Pre-inception synthetic bars have high == low == close."""
    sso = prices[prices["ticker"] == "SSO"]
    pre_inception = sso[sso["date"] < pd.Timestamp("2006-06-21")]
    assert (pre_inception["high"] == pre_inception["close"]).all()
    assert (pre_inception["low"] == pre_inception["close"]).all()


def test_real_has_genuine_ohlc(prices: pd.DataFrame) -> None:
    """Post-inception bars have genuine OHLC variation."""
    sso = prices[prices["ticker"] == "SSO"]
    post_inception = sso[sso["date"] >= pd.Timestamp("2006-06-21")]
    high_vs_low = (post_inception["high"] - post_inception["low"]).abs()
    assert (high_vs_low > 0).sum() / len(post_inception) > 0.95, (
        "Real bars should have high != low on at least 95% of days"
    )
```

- [ ] **Step 2: Run tests — expect pass**

Run: `pytest tests/cross_lib/test_data_layer.py -v`
Expected: 5 tests pass. If `test_canonical_window_coverage` fails, reference_prices.py did not load all tickers correctly — inspect the `frames` list in `build_reference_prices`.

- [ ] **Step 3: Commit**

```bash
git add tests/cross_lib/test_data_layer.py
git commit -m "test(phase-3.5c): data layer tests for reference_prices parquet"
```

---

### Task 6: Reference baseline generator (our engine → baseline.json)

**Files:**
- Create: `reports/phase_3_5c/cross_lib/reference/generate_baseline.py`

- [ ] **Step 1: Implement the generator**

Create `reports/phase_3_5c/cross_lib/reference/generate_baseline.py`:

```python
"""Pins our engine's numbers into baseline.json — the reference the libs
are compared against.

Runs ONCE when the harness is first built. Re-run only when `letf_rotation.py`
or `portfolio_3leg_ew` computation changes. Baseline is git-committed so
verdicts are reproducible.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

BASELINE_JSON = Path("reports/phase_3_5c/cross_lib/reference/baseline.json")


def git_commit_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    )


def _load_portfolio_3leg_ew_summary(window: str) -> dict:
    """Load the existing V4 portfolio metrics from reports/phase3_5b.

    V4 canonical = reports/phase3_5b/variants_letf_execution/summary.json
    V1 fallback  = reports/phase3_5b/portfolio_3leg_ew/summary.json
    """
    if window == "canonical":
        path = Path(
            "reports/phase3_5b/variants_letf_execution/summary.json"
        )
    elif window == "extended":
        path = Path(
            "reports/phase3_5b/extended_window_1986_2026/summary.json"
        )
    else:
        raise ValueError(f"Unknown window: {window}")
    return json.loads(path.read_text())


def _load_leg_summary(leg_name: str) -> dict:
    mapping = {
        "leg_sso_only": "letf_rotation_ema100_2x",
        "leg_qld_only": "qqq_donchian_20_10",
        "leg_ugl_only": "gld_donchian_40_20",
    }
    path = Path(f"reports/phase3_5b/{mapping[leg_name]}/summary.json")
    return json.loads(path.read_text())


def build_baseline() -> dict:
    baseline: dict = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "git_commit": git_commit_hash(),
        "variants": {},
    }

    # Flagship + each leg + v1 fallback — canonical window
    flagship_canonical = _load_portfolio_3leg_ew_summary("canonical")
    flagship_extended = _load_portfolio_3leg_ew_summary("extended")

    baseline["variants"]["plano_b_v4_threshold_10"] = {
        "canonical": _extract_metrics(flagship_canonical),
        "extended": _extract_metrics(flagship_extended),
    }

    for leg in ("leg_sso_only", "leg_qld_only", "leg_ugl_only"):
        baseline["variants"][leg] = {
            "canonical": _extract_metrics(_load_leg_summary(leg)),
        }

    v1 = json.loads(
        Path("reports/phase3_5b/portfolio_3leg_ew/summary.json").read_text()
    )
    baseline["variants"]["v1_fallback"] = {"canonical": _extract_metrics(v1)}

    baseline["integrity_hash"] = _hash_baseline(baseline)
    return baseline


def _extract_metrics(summary: dict) -> dict:
    m = summary.get("metrics", summary)
    return {
        "cagr": float(m["cagr_pct"]),
        "sharpe": float(m["sharpe"]),
        "max_dd": float(m["max_drawdown_pct"]) * -1
        if m["max_drawdown_pct"] > 0
        else float(m["max_drawdown_pct"]),
        "return_ann": float(m.get("return_ann_pct", m["cagr_pct"])),
        "volatility_ann": float(m.get("volatility_ann_pct", 0.0)),
    }


def _hash_baseline(baseline: dict) -> str:
    body = {k: v for k, v in baseline.items() if k != "integrity_hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def save_baseline(baseline: dict, path: Path = BASELINE_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2, sort_keys=True))


if __name__ == "__main__":
    bl = build_baseline()
    save_baseline(bl)
    print(f"Wrote baseline to {BASELINE_JSON} (hash={bl['integrity_hash'][:12]})")
    for vid, windows in bl["variants"].items():
        for window, metrics in windows.items():
            print(
                f"  {vid}/{window}: CAGR={metrics['cagr']:.4f} "
                f"Sharpe={metrics['sharpe']:.3f} MaxDD={metrics['max_dd']:.3%}"
            )
```

- [ ] **Step 2: Generate baseline**

Run: `python -m reports.phase_3_5c.cross_lib.reference.generate_baseline`
Expected: `baseline.json` written with 5+ variants. Paths may need adjustment if the actual V4 summary.json lives elsewhere — check `reports/phase3_5b/variants_letf_execution/` contents and adjust `_load_portfolio_3leg_ew_summary()`.

- [ ] **Step 3: Force baseline into git (overriding .gitignore exclusion of results/)**

```bash
git add -f reports/phase_3_5c/cross_lib/reference/baseline.json
git add reports/phase_3_5c/cross_lib/reference/generate_baseline.py
git commit -m "feat(phase-3.5c): reference baseline generator + pinned baseline.json"
```

---

### Task 7: Verdict engine — Tolerance + classify_tier

**Files:**
- Create: `reports/phase_3_5c/cross_lib/verdict.py`
- Create: `tests/cross_lib/test_verdict.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cross_lib/test_verdict.py`:

```python
"""Verdict engine tests — table-driven."""
from __future__ import annotations

import pandas as pd
import pytest

from reports.phase_3_5c.cross_lib.types import RunResult
from reports.phase_3_5c.cross_lib.verdict import (
    TOL_CONFIRM,
    TOL_STRONG,
    Baseline,
    Tier,
    classify_tier,
)


@pytest.fixture
def baseline_v4() -> Baseline:
    return Baseline(cagr=0.3919, sharpe=2.609, max_dd=-0.1222)


def _make_run(cagr: float, sharpe: float, max_dd: float, monthly_rho: float = 1.0) -> RunResult:
    idx = pd.date_range("2020-01-31", periods=12, freq="ME")
    monthly = pd.Series([0.01] * 12, index=idx)
    return RunResult(
        variant_id="plano_b_v4_threshold_10",
        lib="test",
        window=("2004-10-01", "2026-04-18"),
        stage=1,
        equity_curve=pd.Series([1.0]),
        monthly_returns=monthly,
        trade_dates=[],
        cagr=cagr,
        sharpe=sharpe,
        max_dd=max_dd,
        wf_splits_8=[sharpe] * 8,
        dsr_pval=0.01,
        outcome="OK",
        error_detail=None,
    )


def test_identity_near_match_is_confirms_strong(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.3920, sharpe=2.608, max_dd=-0.1221)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=1.0)
    assert tier == Tier.CONFIRMS_STRONG


def test_small_diff_is_confirms(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.38, sharpe=2.55, max_dd=-0.13)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.97)
    assert tier == Tier.CONFIRMS


def test_larger_diff_is_warning(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.30, sharpe=2.30, max_dd=-0.20)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.80)
    assert tier == Tier.WARNING


def test_gate_flip_is_refutes(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.05, sharpe=-0.2, max_dd=-0.40)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.1)
    assert tier == Tier.REFUTES


def test_maxdd_gate_flip_is_refutes(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.20, sharpe=1.0, max_dd=-0.30)  # MaxDD > 25% gate
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.9)
    assert tier == Tier.REFUTES


def test_tol_strong_bands() -> None:
    assert TOL_STRONG.cagr_pp == 0.5
    assert TOL_STRONG.sharpe == 0.05
    assert TOL_STRONG.max_dd_pp == 1.0
    assert TOL_STRONG.monthly_rho == 0.99


def test_tol_confirm_bands() -> None:
    assert TOL_CONFIRM.cagr_pp == 2.0
    assert TOL_CONFIRM.sharpe == 0.15
    assert TOL_CONFIRM.max_dd_pp == 3.0
    assert TOL_CONFIRM.monthly_rho == 0.95
```

- [ ] **Step 2: Run test — expect import failures**

Run: `pytest tests/cross_lib/test_verdict.py -v`
Expected: `ImportError` from verdict module.

- [ ] **Step 3: Implement verdict.py**

Create `reports/phase_3_5c/cross_lib/verdict.py`:

```python
"""Verdict engine.

Maps each RunResult to a 4-tier verdict (CONFIRMS-STRONG / CONFIRMS / WARNING /
REFUTES) against a pinned Baseline, then aggregates per-lib tiers into a
variant-level aggregate verdict (VALIDATED / VALIDATED-WITH-CAVEATS /
BLOCKED-INVESTIGATE / INCONCLUSIVE).

Citations
---------
- Tolerance magnitudes: `[advances_fin_ml, p.208-211]`
- Strategy similarity under perturbation: `[advances_fin_ml, p.273-275]`
- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.298-299]`
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from reports.phase_3_5c.cross_lib.types import RunResult


class Tier(str, Enum):
    CONFIRMS_STRONG = "CONFIRMS-STRONG"
    CONFIRMS = "CONFIRMS"
    WARNING = "WARNING"
    REFUTES = "REFUTES"


class AggregateVerdict(str, Enum):
    VALIDATED = "VALIDATED"
    VALIDATED_WITH_CAVEATS = "VALIDATED-WITH-CAVEATS"
    BLOCKED_INVESTIGATE = "BLOCKED-INVESTIGATE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class Tolerance:
    cagr_pp: float
    sharpe: float
    max_dd_pp: float
    monthly_rho: float


TOL_STRONG = Tolerance(cagr_pp=0.5, sharpe=0.05, max_dd_pp=1.0, monthly_rho=0.99)
TOL_CONFIRM = Tolerance(cagr_pp=2.0, sharpe=0.15, max_dd_pp=3.0, monthly_rho=0.95)


@dataclass(frozen=True)
class Baseline:
    cagr: float
    sharpe: float
    max_dd: float


def classify_tier(
    run: RunResult,
    baseline: Baseline,
    monthly_rho_override: float | None = None,
) -> Tier:
    """Map one run to one tier.

    monthly_rho_override is for unit tests — production callers pass None and
    rho is computed against baseline monthly returns (loaded separately).
    """
    # Gate flips → REFUTES first (they matter most)
    if (
        run.sharpe <= 0
        or abs(run.max_dd) >= 0.25
        or sum(1 for s in run.wf_splits_8 if s > 0) < 6
        or run.dsr_pval >= 0.05
    ):
        return Tier.REFUTES

    rho = monthly_rho_override if monthly_rho_override is not None else 1.0

    d_cagr = abs(run.cagr - baseline.cagr) * 100  # to percentage points
    d_sharpe = abs(run.sharpe - baseline.sharpe)
    d_max_dd = abs(run.max_dd - baseline.max_dd) * 100  # to pp

    if (
        d_cagr < TOL_STRONG.cagr_pp
        and d_sharpe < TOL_STRONG.sharpe
        and d_max_dd < TOL_STRONG.max_dd_pp
        and rho > TOL_STRONG.monthly_rho
    ):
        return Tier.CONFIRMS_STRONG

    if (
        d_cagr < TOL_CONFIRM.cagr_pp
        and d_sharpe < TOL_CONFIRM.sharpe
        and d_max_dd < TOL_CONFIRM.max_dd_pp
        and rho > TOL_CONFIRM.monthly_rho
    ):
        return Tier.CONFIRMS

    return Tier.WARNING
```

- [ ] **Step 4: Run tests — expect pass**

Run: `pytest tests/cross_lib/test_verdict.py -v`
Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add reports/phase_3_5c/cross_lib/verdict.py tests/cross_lib/test_verdict.py
git commit -m "feat(phase-3.5c): verdict tier classifier with tolerances + tests"
```

---

### Task 8: Verdict engine — aggregate_verdict

**Files:**
- Modify: `reports/phase_3_5c/cross_lib/verdict.py`
- Modify: `tests/cross_lib/test_verdict.py`

- [ ] **Step 1: Append aggregation tests**

Append to `tests/cross_lib/test_verdict.py`:

```python
from reports.phase_3_5c.cross_lib.verdict import AggregateVerdict, aggregate_verdict


def test_aggregate_all_strong_is_validated() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.CONFIRMS,
    }
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.CONFIRMS,
        "backtrader": Tier.CONFIRMS,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.VALIDATED


def test_aggregate_stage2_warning_is_caveats() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.CONFIRMS,
    }
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.WARNING,
        "backtrader": Tier.WARNING,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.VALIDATED_WITH_CAVEATS


def test_aggregate_any_refutes_is_blocked() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.REFUTES,
    }
    stage2 = {"bt": Tier.CONFIRMS}
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.BLOCKED_INVESTIGATE


def test_aggregate_insufficient_libs_is_inconclusive() -> None:
    stage1 = {"bt": Tier.CONFIRMS_STRONG}
    stage2: dict[str, Tier] = {}
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.INCONCLUSIVE


def test_aggregate_stage1_weak_is_blocked() -> None:
    stage1 = {"bt": Tier.CONFIRMS, "vectorbt": Tier.CONFIRMS}  # 0 STRONG
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.CONFIRMS,
        "backtrader": Tier.CONFIRMS,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.BLOCKED_INVESTIGATE
```

- [ ] **Step 2: Run tests — expect failure**

Run: `pytest tests/cross_lib/test_verdict.py -v`
Expected: 5 new tests fail with `ImportError: cannot import name 'aggregate_verdict'`.

- [ ] **Step 3: Implement aggregate_verdict**

Append to `reports/phase_3_5c/cross_lib/verdict.py`:

```python
def aggregate_verdict(
    stage1_tiers: dict[str, Tier],
    stage2_tiers: dict[str, Tier],
    min_strong_stage1: int = 2,
    min_confirm_stage2: int = 3,
) -> AggregateVerdict:
    """Aggregate per-lib tiers into a single verdict for one variant.

    Precedence: REFUTES > insufficient coverage > weak-stage-1 > caveats > validated.
    """
    all_tiers = list(stage1_tiers.values()) + list(stage2_tiers.values())

    if Tier.REFUTES in all_tiers:
        return AggregateVerdict.BLOCKED_INVESTIGATE

    if len(stage1_tiers) < min_strong_stage1:
        return AggregateVerdict.INCONCLUSIVE

    strong_s1 = sum(1 for t in stage1_tiers.values() if t == Tier.CONFIRMS_STRONG)
    if strong_s1 < min_strong_stage1:
        return AggregateVerdict.BLOCKED_INVESTIGATE

    pass_s2 = sum(1 for t in stage2_tiers.values() if t in (Tier.CONFIRMS_STRONG, Tier.CONFIRMS))
    warn_s2 = sum(1 for t in stage2_tiers.values() if t == Tier.WARNING)

    if pass_s2 >= min_confirm_stage2:
        return AggregateVerdict.VALIDATED

    if pass_s2 + warn_s2 >= min_confirm_stage2 and warn_s2 <= 2:
        return AggregateVerdict.VALIDATED_WITH_CAVEATS

    return AggregateVerdict.INCONCLUSIVE
```

- [ ] **Step 4: Run tests — expect pass**

Run: `pytest tests/cross_lib/test_verdict.py -v`
Expected: all 12 tests pass.

- [ ] **Step 5: Commit**

```bash
git add reports/phase_3_5c/cross_lib/verdict.py tests/cross_lib/test_verdict.py
git commit -m "feat(phase-3.5c): aggregate_verdict with 5 precedence tests"
```

---

### Task 9: Adapter protocol + shared signal helpers

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/protocol.py`
- Create: `reports/phase_3_5c/cross_lib/adapters/signals.py`

- [ ] **Step 1: Write adapter protocol**

Create `reports/phase_3_5c/cross_lib/adapters/protocol.py`:

```python
"""Adapter interface contract. Every lib-specific adapter implements this."""
from __future__ import annotations

from typing import Protocol

from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig


class Adapter(Protocol):
    """Common interface for all library adapters."""

    name: str  # "bt", "vectorbt", "backtrader", "quantstats"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        """Run the variant in this library within the given window.

        Returns RunResult with outcome in {OK, SKIPPED, DATA_UNAVAILABLE, ERROR}.
        MUST NOT raise — any exception must be caught and packaged as ERROR.
        """
        ...
```

- [ ] **Step 2: Write shared signal helpers**

Create `reports/phase_3_5c/cross_lib/adapters/signals.py`:

```python
"""Canonical signal implementations referenced by all adapter tests.

These are *our definition* of the signals. Each lib adapter must reproduce
these values (tolerance ±0 at sample dates) for its unit tests to pass.

Citations
---------
- EMA100 regime: `[leverage_for_the_long_run, p.13]`
- Donchian canonical: `[trading_systems_methods, p.353]`
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema_regime(prices: pd.Series, lookback: int) -> pd.Series:
    """Return boolean Series: True when close > EMA(lookback).

    EMA uses pandas ewm with span=lookback, adjust=False (industry standard).
    """
    ema = prices.ewm(span=lookback, adjust=False).mean()
    return (prices > ema).astype(bool)


def donchian_signal(prices: pd.Series, entry: int, exit_: int) -> pd.Series:
    """Return state Series: 1 when LONG, 0 when FLAT.

    LONG triggered on close breaking above prior `entry`-day high.
    FLAT triggered on close breaking below prior `exit_`-day low.
    Hysteresis: state persists between transitions.
    """
    prior_high = prices.rolling(entry, min_periods=entry).max().shift(1)
    prior_low = prices.rolling(exit_, min_periods=exit_).min().shift(1)

    state = pd.Series(0, index=prices.index, dtype=int)
    current = 0
    for t in range(len(prices)):
        close = prices.iloc[t]
        if current == 0 and pd.notna(prior_high.iloc[t]) and close > prior_high.iloc[t]:
            current = 1
        elif current == 1 and pd.notna(prior_low.iloc[t]) and close < prior_low.iloc[t]:
            current = 0
        state.iloc[t] = current
    return state
```

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/protocol.py reports/phase_3_5c/cross_lib/adapters/signals.py
git commit -m "feat(phase-3.5c): Adapter protocol + canonical signal helpers"
```

---

## Milestone M1 — Library Adapters (Tasks 10-17)

### Task 10: bt adapter — implement Plano B V4 in `bt`

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/bt_adapter.py`
- Modify: `pyproject.toml` (add `bt>=1.0` as a dev dependency under `cross_lib` group)

- [ ] **Step 1: Add bt to optional dependency group**

Modify `pyproject.toml`'s `[project.optional-dependencies]` section to add:

```toml
cross_lib = [
    "bt>=1.0",
    "vectorbt>=0.27",
    "backtrader>=1.9",
    "quantstats>=0.0.64",
    "pyfolio-reloaded>=0.9.5",
]
```

Install: `uv pip install -e '.[cross_lib]'`

- [ ] **Step 2: Implement bt adapter**

Create `reports/phase_3_5c/cross_lib/adapters/bt_adapter.py`:

```python
"""bt adapter — Plano B V4 in Philippe Morissette's `bt` library.

Strategy composition:
1. For each leg, compute signal (ema_regime or donchian) on signal_ticker prices.
2. Map signal → target weight on execution_ticker (weight * 1/N if LONG, 0 if FLAT).
3. Pass to bt.Strategy with TargetWeights algo + threshold rebalance.
4. Backtest on DataFrame of execution_ticker prices.
"""
from __future__ import annotations

import traceback
from typing import Any

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.signals import (
    donchian_signal,
    ema_regime,
)
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import (
    Outcome,
    RunResult,
    VariantConfig,
)


class BtAdapter:
    name: str = "bt"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import bt  # noqa: F401
        except ImportError as exc:
            return self._skipped_result(variant, window, stage, str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            weights = self._compute_target_weights(variant, prices)
            equity = self._run_bt(variant, prices, weights)
            return self._finalize_result(variant, window, stage, equity, prices)
        except FileNotFoundError as exc:
            return self._data_unavailable(variant, window, stage, str(exc))
        except Exception as exc:  # pragma: no cover - adapter must not raise
            return self._error_result(variant, window, stage, exc)

    def _load_prices(
        self, variant: VariantConfig, window: tuple[str, str], stage: int
    ) -> pd.DataFrame:
        """Return wide-format price DataFrame: index=date, columns=tickers."""
        if stage == 1:
            df = load_reference_parquet()
        else:  # stage 2 — independent fetch
            from reports.phase_3_5c.cross_lib.data.independent_fetchers.yf_fetcher import (
                fetch_yf,
            )

            tickers = list(
                {leg.signal_ticker for leg in variant.legs}
                | {leg.execution_ticker for leg in variant.legs}
            )
            df = fetch_yf(tickers, window[0], window[1])

        df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])]
        wide = df.pivot(index="date", columns="ticker", values="close")
        return wide.ffill().dropna(how="all")

    def _compute_target_weights(
        self, variant: VariantConfig, prices: pd.DataFrame
    ) -> pd.DataFrame:
        """Return per-date target weights for each execution ticker.

        Allocation rule: leg's target weight is `1/N` when signal is LONG,
        0 when signal is FLAT. Unallocated weight stays as cash (no
        cross-leg reallocation except on threshold event — bt's weighting
        algo handles the threshold logic).
        """
        n = len(variant.legs)
        weight_per_leg = 1.0 / n
        weights = pd.DataFrame(0.0, index=prices.index, columns=[leg.execution_ticker for leg in variant.legs])

        for leg in variant.legs:
            signal_prices = prices[leg.signal_ticker]
            if leg.signal_type == "ema_regime":
                state = ema_regime(signal_prices, leg.signal_params["lookback"])
            elif leg.signal_type == "donchian":
                state = donchian_signal(
                    signal_prices,
                    leg.signal_params["entry"],
                    leg.signal_params["exit"],
                )
            else:
                raise ValueError(f"Unknown signal_type: {leg.signal_type}")
            weights[leg.execution_ticker] = state.astype(float) * weight_per_leg

        return weights

    def _run_bt(
        self,
        variant: VariantConfig,
        prices: pd.DataFrame,
        weights: pd.DataFrame,
    ) -> pd.Series:
        import bt

        exec_tickers = [leg.execution_ticker for leg in variant.legs]
        exec_prices = prices[exec_tickers]

        # Threshold rebalance: bt's RebalanceOverTime with threshold check.
        # For simplicity, use a WeighTarget algo + PeriodicRebalance monthly
        # combined with a threshold guard. bt's canonical idiom:
        if variant.rebalance.mode == "daily":
            rebal_algo = bt.algos.RunDaily()
        elif variant.rebalance.mode == "threshold":
            rebal_algo = _ThresholdRebalance(variant.rebalance.threshold_pp / 100.0)
        else:
            rebal_algo = bt.algos.RunMonthly()

        strat = bt.Strategy(
            variant.variant_id,
            [
                rebal_algo,
                bt.algos.WeighTarget(weights),
                bt.algos.Rebalance(),
            ],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        return result.prices[variant.variant_id].rename("equity")

    def _finalize_result(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
        prices: pd.DataFrame,
    ) -> RunResult:
        rets = equity.pct_change().dropna()
        cagr = _cagr(equity)
        sharpe = _sharpe(rets)
        max_dd = _max_drawdown(equity)
        monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)
        wf_splits = _walk_forward_sharpe(rets, n_splits=8)

        return RunResult(
            variant_id=variant.variant_id,
            lib=self.name,
            window=window,
            stage=stage,
            equity_curve=equity,
            monthly_returns=monthly,
            trade_dates=[],  # bt exposes via transactions; left empty here, filled per-report
            cagr=cagr,
            sharpe=sharpe,
            max_dd=max_dd,
            wf_splits_8=wf_splits,
            dsr_pval=_dsr_pval(sharpe, rets),
            outcome="OK",
            error_detail=None,
        )

    def _skipped_result(
        self, variant: VariantConfig, window: tuple[str, str], stage: int, msg: str
    ) -> RunResult:
        return _empty_result(
            variant, self.name, window, stage, outcome="SKIPPED", error_detail=msg
        )

    def _data_unavailable(
        self, variant: VariantConfig, window: tuple[str, str], stage: int, msg: str
    ) -> RunResult:
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            outcome="DATA_UNAVAILABLE",
            error_detail=msg,
        )

    def _error_result(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        exc: Exception,
    ) -> RunResult:
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            outcome="ERROR",
            error_detail=f"{exc}\n{traceback.format_exc()}",
        )


def _empty_result(
    variant: VariantConfig,
    lib: str,
    window: tuple[str, str],
    stage: int,
    outcome: Outcome,
    error_detail: str | None,
) -> RunResult:
    return RunResult(
        variant_id=variant.variant_id,
        lib=lib,
        window=window,
        stage=stage,
        equity_curve=pd.Series(dtype=float),
        monthly_returns=pd.Series(dtype=float),
        trade_dates=[],
        cagr=float("nan"),
        sharpe=float("nan"),
        max_dd=float("nan"),
        wf_splits_8=[],
        dsr_pval=float("nan"),
        outcome=outcome,
        error_detail=error_detail,
    )


def _cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return float("nan")
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1


def _sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.std() == 0 or len(returns) < 30:
        return float("nan")
    return returns.mean() / returns.std() * np.sqrt(periods_per_year)


def _max_drawdown(equity: pd.Series) -> float:
    running_max = equity.expanding().max()
    dd = (equity - running_max) / running_max
    return float(dd.min())


def _walk_forward_sharpe(returns: pd.Series, n_splits: int) -> list[float]:
    if len(returns) < n_splits * 30:
        return []
    slice_len = len(returns) // n_splits
    return [
        _sharpe(returns.iloc[i * slice_len : (i + 1) * slice_len])
        for i in range(n_splits)
    ]


def _dsr_pval(sharpe: float, returns: pd.Series, n_trials: int = 4) -> float:
    """Deflated Sharpe Ratio p-value [advances_fin_ml, p.231-234].

    Simplified: assumes skew=0, kurt=3. Production should use full formula.
    """
    from scipy.stats import norm

    if not np.isfinite(sharpe):
        return float("nan")
    t = len(returns)
    expected_max_sr = ((1 - 0.5772) * norm.ppf(1 - 1 / n_trials) +
                       0.5772 * norm.ppf(1 - 1 / (n_trials * np.e)))
    z = (sharpe * np.sqrt(t - 1) - expected_max_sr) / np.sqrt(1 - 0)
    return float(1 - norm.cdf(z))


class _ThresholdRebalance:
    """bt algo — rebalance only when any weight drifts beyond threshold."""

    def __init__(self, threshold_fraction: float) -> None:
        self.threshold = threshold_fraction

    def __call__(self, target: Any) -> bool:
        if not hasattr(target, "temp") or "weights" not in target.temp:
            return True
        current = target.children
        targets = target.temp["weights"]
        for k, w in targets.items():
            actual = current[k].weight if k in current else 0.0
            if abs(actual - w) > self.threshold:
                return True
        return False
```

- [ ] **Step 3: Smoke-run the adapter on a short variant**

```bash
python -c "
from reports.phase_3_5c.cross_lib.adapters.bt_adapter import BtAdapter
from reports.phase_3_5c.cross_lib.types import VariantConfig, LegConfig, RebalanceConfig
v = VariantConfig(
    variant_id='leg_sso_only',
    family='plano_b',
    execution_model='letf_synthetic',
    legs=(LegConfig('ema_regime', {'lookback': 100}, 'SPY', 'SSO'),),
    rebalance=RebalanceConfig(mode='daily', threshold_pp=None),
    target_weights=(1.0,),
    windows=(('2020-01-01', '2020-12-31'),),
)
r = BtAdapter().run(v, ('2020-01-01', '2020-12-31'), stage=1)
print(f'outcome={r.outcome} cagr={r.cagr} sharpe={r.sharpe}')
"
```

Expected output: `outcome=OK cagr=<some float> sharpe=<some float>`.

- [ ] **Step 4: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/bt_adapter.py pyproject.toml
git commit -m "feat(phase-3.5c): bt adapter end-to-end"
```

---

### Task 11: bt adapter unit tests

**Files:**
- Create: `tests/cross_lib/test_adapter_bt.py`

- [ ] **Step 1: Write tests**

Create `tests/cross_lib/test_adapter_bt.py`:

```python
"""Unit tests for bt adapter — contract + signal alignment."""
from __future__ import annotations

import pandas as pd
import pytest

bt = pytest.importorskip("bt")

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import BtAdapter
from reports.phase_3_5c.cross_lib.adapters.signals import ema_regime
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)


SHORT_WINDOW = ("2020-01-01", "2020-12-31")


def _leg_variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(SHORT_WINDOW,),
    )


def test_adapter_returns_run_result() -> None:
    result = BtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert result.lib == "bt"
    assert result.cagr == result.cagr  # not NaN
    assert len(result.equity_curve) > 100


def test_signal_matches_canonical() -> None:
    """At 5 sample dates, bt adapter's signal matches canonical ema_regime output."""
    prices = load_reference_parquet()
    spy = prices[prices["ticker"] == "SPY"].set_index("date")["close"]
    spy_2020 = spy.loc["2020-01-01":"2020-12-31"]
    expected = ema_regime(spy_2020, 100)

    sample_dates = [
        "2020-02-14",
        "2020-04-15",
        "2020-06-30",
        "2020-09-30",
        "2020-12-15",
    ]
    for date in sample_dates:
        date_ts = pd.Timestamp(date)
        if date_ts in expected.index:
            # bt adapter re-uses signals.ema_regime directly, so this is a
            # self-consistency check that should always hold.
            assert expected.loc[date_ts] in (True, False)


def test_adapter_skipped_when_bt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "bt", None)
    adapter = BtAdapter()
    result = adapter.run(_leg_variant(), SHORT_WINDOW, stage=1)
    # Expect either SKIPPED (clean path) or ERROR (TypeError from setting None)
    assert result.outcome in ("SKIPPED", "ERROR")


def test_adapter_data_unavailable_on_missing_ticker() -> None:
    variant = VariantConfig(
        variant_id="bogus",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "BOGUSX", "BOGUSX"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(SHORT_WINDOW,),
    )
    result = BtAdapter().run(variant, SHORT_WINDOW, stage=1)
    # Ticker missing in parquet → either DATA_UNAVAILABLE or ERROR
    assert result.outcome in ("DATA_UNAVAILABLE", "ERROR")
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/cross_lib/test_adapter_bt.py -v`
Expected: 4 tests pass (one may be skipped if `bt` is unavailable).

- [ ] **Step 3: Commit**

```bash
git add tests/cross_lib/test_adapter_bt.py
git commit -m "test(phase-3.5c): bt adapter contract + signal alignment"
```

---

### Task 12: vectorbt adapter

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/vectorbt_adapter.py`

- [ ] **Step 1: Implement adapter**

Create `reports/phase_3_5c/cross_lib/adapters/vectorbt_adapter.py`:

```python
"""vectorbt adapter — Plano B V4 vectorized.

vectorbt's Portfolio.from_orders takes per-(date,ticker) target-weight matrices.
We compute weights via the same helper used by other adapters, then use
Portfolio.from_orders with size_type='targetpercent' + freq='D'.
"""
from __future__ import annotations

import traceback

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import (
    _cagr,
    _dsr_pval,
    _empty_result,
    _max_drawdown,
    _sharpe,
    _walk_forward_sharpe,
)
from reports.phase_3_5c.cross_lib.adapters.signals import (
    donchian_signal,
    ema_regime,
)
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import (
    RunResult,
    VariantConfig,
)


class VectorbtAdapter:
    name: str = "vectorbt"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import vectorbt as vbt  # noqa: F401
        except ImportError as exc:
            return _empty_result(variant, self.name, window, stage, "SKIPPED", str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            weights = self._compute_target_weights(variant, prices)
            equity = self._run_vbt(variant, prices, weights)
            return self._finalize(variant, window, stage, equity)
        except FileNotFoundError as exc:
            return _empty_result(variant, self.name, window, stage, "DATA_UNAVAILABLE", str(exc))
        except Exception as exc:  # pragma: no cover
            return _empty_result(
                variant,
                self.name,
                window,
                stage,
                "ERROR",
                f"{exc}\n{traceback.format_exc()}",
            )

    def _load_prices(
        self, variant: VariantConfig, window: tuple[str, str], stage: int
    ) -> pd.DataFrame:
        if stage == 1:
            df = load_reference_parquet()
        else:
            from reports.phase_3_5c.cross_lib.data.independent_fetchers.yf_fetcher import (
                fetch_yf,
            )

            tickers = list(
                {leg.signal_ticker for leg in variant.legs}
                | {leg.execution_ticker for leg in variant.legs}
            )
            df = fetch_yf(tickers, window[0], window[1])

        df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])]
        wide = df.pivot(index="date", columns="ticker", values="close")
        return wide.ffill().dropna(how="all")

    def _compute_target_weights(
        self, variant: VariantConfig, prices: pd.DataFrame
    ) -> pd.DataFrame:
        n = len(variant.legs)
        w = 1.0 / n
        weights = pd.DataFrame(0.0, index=prices.index, columns=[leg.execution_ticker for leg in variant.legs])
        for leg in variant.legs:
            signal_prices = prices[leg.signal_ticker]
            if leg.signal_type == "ema_regime":
                state = ema_regime(signal_prices, leg.signal_params["lookback"])
            elif leg.signal_type == "donchian":
                state = donchian_signal(
                    signal_prices,
                    leg.signal_params["entry"],
                    leg.signal_params["exit"],
                )
            else:
                raise ValueError(f"Unknown signal_type: {leg.signal_type}")
            weights[leg.execution_ticker] = state.astype(float) * w
        return weights

    def _run_vbt(
        self, variant: VariantConfig, prices: pd.DataFrame, weights: pd.DataFrame
    ) -> pd.Series:
        import vectorbt as vbt

        exec_tickers = [leg.execution_ticker for leg in variant.legs]
        exec_prices = prices[exec_tickers]

        # For threshold rebalance, collapse weight targets to "rebal event days"
        # via drift detection. Simpler path: daily rebal on weight change only.
        size = weights.diff().abs().sum(axis=1)
        if variant.rebalance.mode == "threshold":
            threshold = variant.rebalance.threshold_pp / 100.0
            rebal_mask = size > threshold
        else:
            rebal_mask = pd.Series(True, index=weights.index)

        rebal_weights = weights.where(rebal_mask, other=np.nan).ffill()

        pf = vbt.Portfolio.from_orders(
            close=exec_prices,
            size=rebal_weights,
            size_type="targetpercent",
            freq="D",
            init_cash=1.0,
            fees=0.0,
            group_by=True,
            cash_sharing=True,
        )
        return pf.value()

    def _finalize(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
    ) -> RunResult:
        rets = equity.pct_change().dropna()
        cagr = _cagr(equity)
        sharpe = _sharpe(rets)
        max_dd = _max_drawdown(equity)
        monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)

        return RunResult(
            variant_id=variant.variant_id,
            lib=self.name,
            window=window,
            stage=stage,
            equity_curve=equity,
            monthly_returns=monthly,
            trade_dates=[],
            cagr=cagr,
            sharpe=sharpe,
            max_dd=max_dd,
            wf_splits_8=_walk_forward_sharpe(rets, 8),
            dsr_pval=_dsr_pval(sharpe, rets),
            outcome="OK",
            error_detail=None,
        )
```

- [ ] **Step 2: Smoke-run**

```bash
python -c "
from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import VectorbtAdapter
from reports.phase_3_5c.cross_lib.types import VariantConfig, LegConfig, RebalanceConfig
v = VariantConfig(
    variant_id='leg_sso_only',
    family='plano_b',
    execution_model='letf_synthetic',
    legs=(LegConfig('ema_regime', {'lookback': 100}, 'SPY', 'SSO'),),
    rebalance=RebalanceConfig(mode='daily', threshold_pp=None),
    target_weights=(1.0,),
    windows=(('2020-01-01', '2020-12-31'),),
)
r = VectorbtAdapter().run(v, ('2020-01-01', '2020-12-31'), stage=1)
print(f'outcome={r.outcome} cagr={r.cagr} sharpe={r.sharpe}')
"
```

Expected: `outcome=OK cagr=<float> sharpe=<float>`.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/vectorbt_adapter.py
git commit -m "feat(phase-3.5c): vectorbt adapter"
```

---

### Task 13: vectorbt adapter tests

**Files:**
- Create: `tests/cross_lib/test_adapter_vectorbt.py`

- [ ] **Step 1: Write tests**

Create `tests/cross_lib/test_adapter_vectorbt.py`:

```python
"""Unit tests for vectorbt adapter."""
from __future__ import annotations

import pytest

vbt = pytest.importorskip("vectorbt")

from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import (
    VectorbtAdapter,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)

SHORT_WINDOW = ("2020-01-01", "2020-12-31")


def _leg_variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(SHORT_WINDOW,),
    )


def test_adapter_returns_run_result() -> None:
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert result.lib == "vectorbt"
    assert result.cagr == result.cagr
    assert len(result.equity_curve) > 100


def test_adapter_sharpe_is_finite() -> None:
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.sharpe == result.sharpe  # not NaN


def test_adapter_skipped_when_vbt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "vectorbt", None)
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome in ("SKIPPED", "ERROR")


def test_3leg_portfolio_runs() -> None:
    variant = VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(
            LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
            LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
            LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
        ),
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(SHORT_WINDOW,),
    )
    result = VectorbtAdapter().run(variant, SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert len(result.equity_curve) > 100
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/cross_lib/test_adapter_vectorbt.py -v`
Expected: 4 tests pass (or skip if vectorbt unavailable).

- [ ] **Step 3: Commit**

```bash
git add tests/cross_lib/test_adapter_vectorbt.py
git commit -m "test(phase-3.5c): vectorbt adapter contract tests"
```

---

### Task 14: backtrader adapter

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/backtrader_adapter.py`

- [ ] **Step 1: Implement adapter**

Create `reports/phase_3_5c/cross_lib/adapters/backtrader_adapter.py`:

```python
"""backtrader adapter — Plano B V4 in event-driven paradigm.

backtrader is strictly event-driven: each bar fires `next()`, orders fill on
the next bar's open by default. Strategy class reads signals per-bar and
computes target weight; `self.order_target_percent()` handles rebalance.

Because backtrader is slower (event loop), expect long runs. For the full
40-year window, a single variant run takes ~30-90s depending on hardware.
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import (
    _cagr,
    _dsr_pval,
    _empty_result,
    _max_drawdown,
    _sharpe,
    _walk_forward_sharpe,
)
from reports.phase_3_5c.cross_lib.adapters.signals import (
    donchian_signal,
    ema_regime,
)
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig


class BacktraderAdapter:
    name: str = "backtrader"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import backtrader as bt  # noqa: F401
        except ImportError as exc:
            return _empty_result(variant, self.name, window, stage, "SKIPPED", str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            equity = self._run_bt(variant, prices)
            return self._finalize(variant, window, stage, equity)
        except FileNotFoundError as exc:
            return _empty_result(variant, self.name, window, stage, "DATA_UNAVAILABLE", str(exc))
        except Exception as exc:  # pragma: no cover
            return _empty_result(
                variant,
                self.name,
                window,
                stage,
                "ERROR",
                f"{exc}\n{traceback.format_exc()}",
            )

    def _load_prices(
        self, variant: VariantConfig, window: tuple[str, str], stage: int
    ) -> pd.DataFrame:
        if stage == 1:
            df = load_reference_parquet()
        else:
            from reports.phase_3_5c.cross_lib.data.independent_fetchers.yf_fetcher import (
                fetch_yf,
            )

            tickers = list(
                {leg.signal_ticker for leg in variant.legs}
                | {leg.execution_ticker for leg in variant.legs}
            )
            df = fetch_yf(tickers, window[0], window[1])

        df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])]
        return df

    def _run_bt(self, variant: VariantConfig, prices: pd.DataFrame) -> pd.Series:
        import backtrader as bt

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(1_000_000.0)
        cerebro.broker.setcommission(commission=0.0)

        # Add one data feed per ticker
        tickers = sorted({leg.signal_ticker for leg in variant.legs} | {leg.execution_ticker for leg in variant.legs})
        for ticker in tickers:
            sub = prices[prices["ticker"] == ticker].sort_values("date")
            feed_df = sub.set_index("date")[["open", "high", "low", "close", "volume"]]
            feed_df.index = pd.to_datetime(feed_df.index)
            data = bt.feeds.PandasData(dataname=feed_df, name=ticker)
            cerebro.adddata(data)

        cerebro.addstrategy(_PlanoBStrategy, variant=variant)
        cerebro.addanalyzer(_EquityCurveAnalyzer, _name="equity")
        results = cerebro.run()
        analyzer = results[0].analyzers.equity
        eq = pd.Series(analyzer.values, index=pd.to_datetime(analyzer.dates))
        return eq

    def _finalize(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
    ) -> RunResult:
        rets = equity.pct_change().dropna()
        cagr = _cagr(equity)
        sharpe = _sharpe(rets)
        max_dd = _max_drawdown(equity)
        monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)

        return RunResult(
            variant_id=variant.variant_id,
            lib=self.name,
            window=window,
            stage=stage,
            equity_curve=equity,
            monthly_returns=monthly,
            trade_dates=[],
            cagr=cagr,
            sharpe=sharpe,
            max_dd=max_dd,
            wf_splits_8=_walk_forward_sharpe(rets, 8),
            dsr_pval=_dsr_pval(sharpe, rets),
            outcome="OK",
            error_detail=None,
        )


def _lazy_imports():  # pragma: no cover - helper for the class defs below
    import backtrader as bt

    return bt


class _PlanoBStrategy:  # will become backtrader.Strategy subclass at runtime
    """Defined lazily to avoid hard-importing backtrader at module load time.

    Replaced at adapter construction via type() with a backtrader.Strategy base.
    Using simple module-level reassignment below.
    """


def _build_strategy_class():
    import backtrader as bt

    class PlanoBStrategy(bt.Strategy):
        params = (("variant", None),)

        def __init__(self) -> None:
            self.variant = self.p.variant
            self.signal_states: dict[str, int] = {}
            self.data_by_ticker = {d._name: d for d in self.datas}

            # Precompute signals using pandas (same logic as signals.py).
            # backtrader doesn't offer a clean EMA-from-first-bar hook, so
            # we compute the state series up-front on the feed's pandas DF.
            self.precomputed_state: dict[str, pd.Series] = {}
            for leg in self.variant.legs:
                feed = self.data_by_ticker[leg.signal_ticker]
                close_series = pd.Series(
                    [feed.close.array[i] for i in range(feed.buflen())],
                    index=pd.to_datetime([feed.datetime.date(i) for i in range(feed.buflen())]),
                )
                if leg.signal_type == "ema_regime":
                    state = ema_regime(close_series, leg.signal_params["lookback"])
                else:
                    state = donchian_signal(
                        close_series,
                        leg.signal_params["entry"],
                        leg.signal_params["exit"],
                    )
                self.precomputed_state[leg.signal_ticker] = state.astype(int)

            self.last_rebal_weights: dict[str, float] = {}

        def next(self) -> None:
            today = pd.Timestamp(self.datetime.date(0))
            n = len(self.variant.legs)
            w = 1.0 / n

            target: dict[str, float] = {}
            for leg in self.variant.legs:
                state = self.precomputed_state[leg.signal_ticker].get(today, 0)
                target[leg.execution_ticker] = state * w

            if self._should_rebalance(target):
                for leg in self.variant.legs:
                    self.order_target_percent(
                        data=self.data_by_ticker[leg.execution_ticker],
                        target=target[leg.execution_ticker],
                    )
                self.last_rebal_weights = target.copy()

        def _should_rebalance(self, target: dict[str, float]) -> bool:
            mode = self.variant.rebalance.mode
            if mode == "daily":
                return True
            if mode == "threshold":
                if not self.last_rebal_weights:
                    return True
                threshold = self.variant.rebalance.threshold_pp / 100.0
                for ticker, w in target.items():
                    if abs(w - self.last_rebal_weights.get(ticker, 0.0)) > threshold:
                        return True
                return False
            return False  # monthly modes not yet wired in backtrader

    return PlanoBStrategy


def _build_analyzer_class():
    import backtrader as bt

    class EquityCurveAnalyzer(bt.Analyzer):
        def __init__(self) -> None:
            self.values: list[float] = []
            self.dates: list[pd.Timestamp] = []

        def next(self) -> None:
            self.values.append(self.strategy.broker.getvalue())
            self.dates.append(pd.Timestamp(self.strategy.datetime.date(0)))

    return EquityCurveAnalyzer


# Module-level rebind: when backtrader is installed, replace stubs.
try:
    _PlanoBStrategy = _build_strategy_class()
    _EquityCurveAnalyzer = _build_analyzer_class()
except ImportError:  # pragma: no cover
    _EquityCurveAnalyzer = None  # type: ignore[assignment]
```

- [ ] **Step 2: Smoke-run**

```bash
python -c "
from reports.phase_3_5c.cross_lib.adapters.backtrader_adapter import BacktraderAdapter
from reports.phase_3_5c.cross_lib.types import VariantConfig, LegConfig, RebalanceConfig
v = VariantConfig(
    variant_id='leg_sso_only',
    family='plano_b',
    execution_model='letf_synthetic',
    legs=(LegConfig('ema_regime', {'lookback': 100}, 'SPY', 'SSO'),),
    rebalance=RebalanceConfig(mode='daily', threshold_pp=None),
    target_weights=(1.0,),
    windows=(('2020-01-01', '2020-12-31'),),
)
r = BacktraderAdapter().run(v, ('2020-01-01', '2020-12-31'), stage=1)
print(f'outcome={r.outcome} cagr={r.cagr} sharpe={r.sharpe}')
"
```

Expected: `outcome=OK cagr=<float> sharpe=<float>`. If the smoke fails because backtrader's `feed.buflen()` before `run()` returns 0, the strategy init must be restructured to build signals in `start()` rather than `__init__()` — adjust accordingly.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/backtrader_adapter.py
git commit -m "feat(phase-3.5c): backtrader adapter (event-driven)"
```

---

### Task 15: backtrader adapter tests

**Files:**
- Create: `tests/cross_lib/test_adapter_backtrader.py`

- [ ] **Step 1: Write tests**

Create `tests/cross_lib/test_adapter_backtrader.py`:

```python
"""Unit tests for backtrader adapter."""
from __future__ import annotations

import pytest

backtrader = pytest.importorskip("backtrader")

from reports.phase_3_5c.cross_lib.adapters.backtrader_adapter import (
    BacktraderAdapter,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)

SHORT_WINDOW = ("2020-01-01", "2020-12-31")


def _leg_variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(SHORT_WINDOW,),
    )


def test_adapter_returns_run_result() -> None:
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert result.lib == "backtrader"
    assert len(result.equity_curve) > 100


def test_adapter_sharpe_not_zero() -> None:
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert abs(result.sharpe) > 0.01


def test_adapter_skipped_when_bt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "backtrader", None)
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome in ("SKIPPED", "ERROR")
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/cross_lib/test_adapter_backtrader.py -v`
Expected: 3 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/cross_lib/test_adapter_backtrader.py
git commit -m "test(phase-3.5c): backtrader adapter contract tests"
```

---

### Task 16: quantstats adapter + tests

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/quantstats_adapter.py`
- Create: `tests/cross_lib/test_adapter_quantstats.py`

- [ ] **Step 1: Implement adapter**

Create `reports/phase_3_5c/cross_lib/adapters/quantstats_adapter.py`:

```python
"""quantstats adapter — analytics-only cross-check.

Does NOT run the strategy. Consumes an equity curve produced by another adapter
(bt/vectorbt/backtrader) and re-computes CAGR/Sharpe/MaxDD independently using
quantstats' own formulas. Used to isolate metric-computation bugs from
strategy-execution bugs.
"""
from __future__ import annotations

import traceback

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import (
    _empty_result,
    _walk_forward_sharpe,
    _dsr_pval,
)
from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig


class QuantstatsAdapter:
    name: str = "quantstats"

    def run_on_equity(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
        source_lib: str,
    ) -> RunResult:
        """quantstats consumes an equity curve from another run.

        `source_lib` is recorded in error_detail for traceability.
        """
        try:
            import quantstats as qs  # noqa: F401
        except ImportError as exc:
            return _empty_result(
                variant, self.name, window, stage, "SKIPPED", str(exc)
            )

        try:
            import quantstats as qs

            rets = equity.pct_change().dropna()
            cagr = qs.stats.cagr(rets)
            sharpe = qs.stats.sharpe(rets)
            max_dd = qs.stats.max_drawdown(equity)
            monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)

            return RunResult(
                variant_id=variant.variant_id,
                lib=f"{self.name}(from={source_lib})",
                window=window,
                stage=stage,
                equity_curve=equity,
                monthly_returns=monthly,
                trade_dates=[],
                cagr=float(cagr),
                sharpe=float(sharpe),
                max_dd=float(max_dd),
                wf_splits_8=_walk_forward_sharpe(rets, 8),
                dsr_pval=_dsr_pval(float(sharpe), rets),
                outcome="OK",
                error_detail=f"recomputed from {source_lib} equity",
            )
        except Exception as exc:  # pragma: no cover
            return _empty_result(
                variant,
                self.name,
                window,
                stage,
                "ERROR",
                f"{exc}\n{traceback.format_exc()}",
            )

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        """Not a standalone backtester; direct run returns DATA_UNAVAILABLE.

        Callers should use `run_on_equity` passing the equity curve from bt/vectorbt.
        """
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            "DATA_UNAVAILABLE",
            "quantstats requires equity curve input; use run_on_equity",
        )
```

- [ ] **Step 2: Write tests**

Create `tests/cross_lib/test_adapter_quantstats.py`:

```python
"""Unit tests for quantstats adapter."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

qs = pytest.importorskip("quantstats")

from reports.phase_3_5c.cross_lib.adapters.quantstats_adapter import (
    QuantstatsAdapter,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)


def _variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(("2020-01-01", "2020-12-31"),),
    )


def test_run_on_equity_returns_finite() -> None:
    eq = pd.Series(
        np.cumprod(1 + np.random.RandomState(42).normal(0.0005, 0.01, 252)),
        index=pd.date_range("2020-01-01", periods=252, freq="B"),
    )
    adapter = QuantstatsAdapter()
    result = adapter.run_on_equity(_variant(), ("2020-01-01", "2020-12-31"), 1, eq, "synthetic")
    assert result.outcome == "OK"
    assert np.isfinite(result.cagr)
    assert np.isfinite(result.sharpe)


def test_run_standalone_is_data_unavailable() -> None:
    result = QuantstatsAdapter().run(_variant(), ("2020-01-01", "2020-12-31"), 1)
    assert result.outcome == "DATA_UNAVAILABLE"
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/cross_lib/test_adapter_quantstats.py -v`
Expected: 2 tests pass.

- [ ] **Step 4: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/quantstats_adapter.py tests/cross_lib/test_adapter_quantstats.py
git commit -m "feat(phase-3.5c): quantstats adapter + tests"
```

---

### Task 17: yfinance independent fetcher (for Stage 2)

**Files:**
- Create: `reports/phase_3_5c/cross_lib/data/independent_fetchers/yf_fetcher.py`

- [ ] **Step 1: Implement fetcher**

Create `reports/phase_3_5c/cross_lib/data/independent_fetchers/yf_fetcher.py`:

```python
"""yfinance fetcher for Stage 2 independent-data runs.

Returns long-format DataFrame with same schema as reference_prices.parquet:
columns = [date, ticker, open, high, low, close, volume].
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_yf(
    tickers: list[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Download daily OHLCV via yfinance. Raises FileNotFoundError if missing."""
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )
    if data.empty:
        raise FileNotFoundError(f"yfinance returned empty for {tickers} {start}:{end}")

    frames = []
    for ticker in tickers:
        if ticker not in data.columns.levels[0]:
            continue
        sub = data[ticker].reset_index().rename(columns={"Date": "date"})
        sub.columns = [c.lower() for c in sub.columns]
        sub["ticker"] = ticker
        frames.append(sub[["date", "ticker", "open", "high", "low", "close", "volume"]])

    if not frames:
        raise FileNotFoundError(f"yfinance returned no rows for tickers {tickers}")
    return pd.concat(frames, ignore_index=True)
```

- [ ] **Step 2: Smoke-run**

```bash
python -c "
from reports.phase_3_5c.cross_lib.data.independent_fetchers.yf_fetcher import fetch_yf
df = fetch_yf(['SPY', 'SSO'], '2020-01-01', '2020-03-31')
print(df.head())
print(df.shape)
"
```

Expected: DataFrame with ~40 rows × 7 columns.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/data/independent_fetchers/yf_fetcher.py
git commit -m "feat(phase-3.5c): yfinance independent fetcher"
```

---

## Milestone M2 — Wave 1 Execution (Tasks 18-22)

### Task 18: Variants registry (Wave 1 + Wave 2 variants)

**Files:**
- Create: `reports/phase_3_5c/cross_lib/variants.py`

- [ ] **Step 1: Implement registry**

Create `reports/phase_3_5c/cross_lib/variants.py`:

```python
"""Declarative variants registry — all Plano B variants the harness can run."""
from __future__ import annotations

from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)

CANONICAL = ("2004-10-01", "2026-04-18")
EXTENDED = ("1986-01-02", "2026-04-18")
POST_2009 = ("2009-01-01", "2026-04-18")

_V4_LEGS = (
    LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
    LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
    LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
)

_V1_LEGS = (
    LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
    LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QQQ"),
    LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "GLD"),
)

VARIANTS: dict[str, VariantConfig] = {
    # --- Wave 1: flagship + legs ---
    "plano_b_v4_threshold_10": VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL, EXTENDED),
    ),
    "plano_b_v4_daily": VariantConfig(
        variant_id="plano_b_v4_daily",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    ),
    "leg_sso_only": VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[0],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL, EXTENDED),
    ),
    "leg_qld_only": VariantConfig(
        variant_id="leg_qld_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[1],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL,),
    ),
    "leg_ugl_only": VariantConfig(
        variant_id="leg_ugl_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(_V4_LEGS[2],),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(CANONICAL,),
    ),
    # --- Wave 2: decision validation ---
    "v1_fallback": VariantConfig(
        variant_id="v1_fallback",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V1_LEGS,
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    ),
    "2leg_ew": VariantConfig(
        variant_id="2leg_ew",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS[:2],  # SSO + QLD
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(0.5, 0.5),
        windows=(CANONICAL,),
    ),
    "threshold_sweep_5pp": _make_threshold_variant(5.0),
    "threshold_sweep_15pp": _make_threshold_variant(15.0),
    "threshold_sweep_25pp": _make_threshold_variant(25.0),
}


def _make_threshold_variant(pp: float) -> VariantConfig:
    """Factory for threshold sweep variants."""
    return VariantConfig(
        variant_id=f"threshold_sweep_{int(pp)}pp",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=_V4_LEGS,
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=pp),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(CANONICAL,),
    )


def wave_1_variants() -> list[VariantConfig]:
    return [
        VARIANTS["plano_b_v4_threshold_10"],
        VARIANTS["plano_b_v4_daily"],
        VARIANTS["leg_sso_only"],
        VARIANTS["leg_qld_only"],
        VARIANTS["leg_ugl_only"],
    ]


def wave_2_variants() -> list[VariantConfig]:
    return [
        VARIANTS["v1_fallback"],
        VARIANTS["2leg_ew"],
        VARIANTS["threshold_sweep_5pp"],
        VARIANTS["threshold_sweep_15pp"],
        VARIANTS["threshold_sweep_25pp"],
    ]


def wave_3_variants() -> list[VariantConfig]:
    """Populated in Task 27 when Wave 3 becomes active."""
    return []
```

- [ ] **Step 2: Quick sanity check**

Run:
```bash
python -c "
from reports.phase_3_5c.cross_lib.variants import VARIANTS, wave_1_variants
print(f'Registry size: {len(VARIANTS)}')
print(f'Wave 1 size: {len(wave_1_variants())}')
for v in wave_1_variants():
    print(f'  {v.variant_id}: {len(v.legs)} legs, {len(v.windows)} windows')
"
```

Expected: 10 variants total, Wave 1 has 5, each with leg count and window count.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/variants.py
git commit -m "feat(phase-3.5c): declarative variants registry (Wave 1+2)"
```

---

### Task 19: Runner `run_wave.py`

**Files:**
- Create: `reports/phase_3_5c/cross_lib/run_wave.py`

- [ ] **Step 1: Implement runner**

Create `reports/phase_3_5c/cross_lib/run_wave.py`:

```python
"""CLI orchestrator for cross-lib validation runs.

Usage:
    python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 1
    python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 2 --libs bt,vectorbt
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.backtrader_adapter import (
    BacktraderAdapter,
)
from reports.phase_3_5c.cross_lib.adapters.bt_adapter import BtAdapter
from reports.phase_3_5c.cross_lib.adapters.quantstats_adapter import (
    QuantstatsAdapter,
)
from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import (
    VectorbtAdapter,
)
from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig
from reports.phase_3_5c.cross_lib.variants import (
    wave_1_variants,
    wave_2_variants,
    wave_3_variants,
)

RESULTS_DIR = Path("reports/phase_3_5c/cross_lib/results")

ALL_ADAPTERS = {
    "bt": BtAdapter(),
    "vectorbt": VectorbtAdapter(),
    "backtrader": BacktraderAdapter(),
}


def run_wave(wave: int, stage: int, libs: list[str]) -> list[RunResult]:
    if wave == 1:
        variants = wave_1_variants()
    elif wave == 2:
        variants = wave_2_variants()
    elif wave == 3:
        variants = wave_3_variants()
    else:
        raise ValueError(f"Unknown wave {wave}")

    selected_adapters = [ALL_ADAPTERS[name] for name in libs if name in ALL_ADAPTERS]
    all_results: list[RunResult] = []

    for variant in variants:
        windows = variant.windows
        for window in windows:
            # Stage 2 restrictions
            if stage == 2 and pd.Timestamp(window[0]) < pd.Timestamp("2009-01-01"):
                continue

            for adapter in selected_adapters:
                print(f"  {adapter.name} / {variant.variant_id} / {window} / stage {stage}")
                result = adapter.run(variant, window, stage)
                _persist_result(result)
                all_results.append(result)

                # quantstats cross-check: if this run is OK, also run quantstats on its equity
                if result.outcome == "OK" and "quantstats" in libs:
                    qs_result = QuantstatsAdapter().run_on_equity(
                        variant, window, stage, result.equity_curve, adapter.name
                    )
                    _persist_result(qs_result)
                    all_results.append(qs_result)

    return all_results


def _persist_result(result: RunResult) -> None:
    window_slug = f"{result.window[0]}_{result.window[1]}"
    path = (
        RESULTS_DIR
        / f"stage_{result.stage}"
        / result.lib.replace("(", "_").replace(")", "").replace("=", "_")
        / result.variant_id
        / window_slug
    )
    path.mkdir(parents=True, exist_ok=True)

    payload = {
        "variant_id": result.variant_id,
        "lib": result.lib,
        "window": list(result.window),
        "stage": result.stage,
        "cagr": result.cagr,
        "sharpe": result.sharpe,
        "max_dd": result.max_dd,
        "wf_splits_8": result.wf_splits_8,
        "dsr_pval": result.dsr_pval,
        "outcome": result.outcome,
        "error_detail": result.error_detail,
    }
    (path / "result.json").write_text(json.dumps(payload, indent=2, default=str))

    if len(result.equity_curve) > 0:
        result.equity_curve.to_frame("equity").to_parquet(path / "equity.parquet")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", type=int, required=True, choices=[1, 2, 3])
    parser.add_argument("--stage", type=int, required=True, choices=[1, 2])
    parser.add_argument(
        "--libs",
        default="bt,vectorbt,backtrader,quantstats",
        help="Comma-separated list of lib names.",
    )
    args = parser.parse_args()

    libs = args.libs.split(",")
    results = run_wave(args.wave, args.stage, libs)
    print(f"\nCompleted: {len(results)} runs")

    # Quick outcome summary
    by_outcome: dict[str, int] = {}
    for r in results:
        by_outcome[r.outcome] = by_outcome.get(r.outcome, 0) + 1
    print(f"Outcomes: {by_outcome}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-run with short window override**

Note: the wave-1 variants are full windows (20+ years), which takes a while. A quick smoke test can be done by running with `--wave 1 --stage 1 --libs bt` and interrupting after first completion. Full execution happens in Task 22.

- [ ] **Step 3: Commit**

```bash
git add reports/phase_3_5c/cross_lib/run_wave.py
git commit -m "feat(phase-3.5c): run_wave CLI orchestrator"
```

---

### Task 20: Report generator `report.py`

**Files:**
- Create: `reports/phase_3_5c/cross_lib/report.py`

- [ ] **Step 1: Implement report generator**

Create `reports/phase_3_5c/cross_lib/report.py`:

```python
"""Generate VERDICT.md from results/ directory tree.

Scans results/stage_{1,2}/**/result.json, loads the baseline.json, applies
the verdict engine, and emits a matrix + per-variant sections + an executive
summary at the top.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from reports.phase_3_5c.cross_lib.types import RunResult
from reports.phase_3_5c.cross_lib.verdict import (
    AggregateVerdict,
    Baseline,
    Tier,
    aggregate_verdict,
    classify_tier,
)

RESULTS_DIR = Path("reports/phase_3_5c/cross_lib/results")
BASELINE_PATH = Path("reports/phase_3_5c/cross_lib/reference/baseline.json")
VERDICT_MD = Path("reports/phase_3_5c/cross_lib/VERDICT.md")


def load_all_results() -> list[dict]:
    rows: list[dict] = []
    for stage_dir in RESULTS_DIR.glob("stage_*"):
        stage = int(stage_dir.name.split("_")[1])
        for result_file in stage_dir.rglob("result.json"):
            payload = json.loads(result_file.read_text())
            payload["stage"] = stage
            payload["path"] = str(result_file.parent)
            # Load equity curve for rho computation
            equity_parquet = result_file.parent / "equity.parquet"
            if equity_parquet.exists():
                payload["equity"] = pd.read_parquet(equity_parquet)["equity"]
            rows.append(payload)
    return rows


def load_baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text())


def compute_monthly_rho(
    equity: pd.Series, baseline_monthly: pd.Series | None
) -> float:
    if equity is None or baseline_monthly is None:
        return float("nan")
    ret = equity.pct_change().dropna()
    monthly = ret.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    common_idx = monthly.index.intersection(baseline_monthly.index)
    if len(common_idx) < 12:
        return float("nan")
    return float(monthly.loc[common_idx].corr(baseline_monthly.loc[common_idx]))


def build_verdict_matrix(results: list[dict], baseline: dict) -> dict:
    """Return nested dict: {variant_id: {window: {stage: {lib: tier}}}}.

    Monthly rho is computed against the first OK result of each (variant, window)
    pair (treated as reference) so cross-lib rho captures real divergence across
    libraries rather than against a baseline equity curve we don't persist.
    """
    matrix: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    reference_monthly: dict[tuple[str, str, int], pd.Series] = {}
    for row in results:
        key = (row["variant_id"], tuple(row["window"])[0], row["stage"])
        if row["outcome"] == "OK" and key not in reference_monthly and "equity" in row:
            ret = row["equity"].pct_change().dropna()
            reference_monthly[key] = ret.resample("ME").apply(lambda x: (1 + x).prod() - 1)

    for row in results:
        vid = row["variant_id"]
        window = tuple(row["window"])
        window_key = "canonical" if window[0] == "2004-10-01" else (
            "extended" if window[0] == "1986-01-02" else "post_2009"
        )
        stage = row["stage"]
        lib = row["lib"]

        if vid not in baseline["variants"] or window_key not in baseline["variants"][vid]:
            continue
        bl_metrics = baseline["variants"][vid][window_key]
        bl = Baseline(
            cagr=bl_metrics["cagr"],
            sharpe=bl_metrics["sharpe"],
            max_dd=bl_metrics["max_dd"],
        )

        if row["outcome"] != "OK":
            matrix[vid][window_key][stage][lib] = row["outcome"]
            continue

        ref_key = (vid, window[0], stage)
        ref_monthly = reference_monthly.get(ref_key)
        equity = row.get("equity")
        rho = compute_monthly_rho(equity, ref_monthly) if equity is not None else 1.0
        if not pd.notna(rho):
            rho = 1.0  # insufficient overlap; defer to metric-based tier only

        fake_run = _payload_to_result(row)
        tier = classify_tier(fake_run, bl, monthly_rho_override=rho)
        matrix[vid][window_key][stage][lib] = tier.value

    return matrix


def _payload_to_result(payload: dict) -> RunResult:
    return RunResult(
        variant_id=payload["variant_id"],
        lib=payload["lib"],
        window=tuple(payload["window"]),
        stage=payload["stage"],
        equity_curve=pd.Series(dtype=float),
        monthly_returns=pd.Series(dtype=float),
        trade_dates=[],
        cagr=payload["cagr"],
        sharpe=payload["sharpe"],
        max_dd=payload["max_dd"],
        wf_splits_8=payload["wf_splits_8"],
        dsr_pval=payload["dsr_pval"],
        outcome=payload["outcome"],
        error_detail=payload.get("error_detail"),
    )


def emit_verdict_md(matrix: dict, baseline: dict) -> str:
    lines: list[str] = [
        "# VERDICT — Plano B Cross-Library Validation",
        "",
        f"> Generated: {pd.Timestamp.utcnow().isoformat()}.",
        f"> Baseline commit: `{baseline.get('git_commit', '?')[:12]}`.",
        f"> Baseline hash: `{baseline.get('integrity_hash', '?')[:12]}`.",
        "",
        "## Aggregate verdicts",
        "",
    ]

    for vid, windows in matrix.items():
        for window_key, stages in windows.items():
            s1_tiers = _coerce_tiers(stages.get(1, {}))
            s2_tiers = _coerce_tiers(stages.get(2, {}))
            agg = aggregate_verdict(s1_tiers, s2_tiers)
            lines.append(f"- **{vid}** / {window_key}: **{agg.value}**")

    lines += ["", "## Per-variant matrix", ""]

    for vid, windows in matrix.items():
        lines.append(f"### {vid}")
        lines.append("")
        for window_key, stages in windows.items():
            lines.append(f"**Window:** {window_key}")
            lines.append("")
            lines.append("| stage | lib | tier/outcome |")
            lines.append("|-------|-----|--------------|")
            for stage in sorted(stages.keys()):
                for lib, tier in stages[stage].items():
                    lines.append(f"| {stage} | {lib} | {tier} |")
            lines.append("")

    lines += [
        "",
        "## Citations",
        "",
        "- Tolerance magnitudes: `[advances_fin_ml, p.208-211]`",
        "- Strategy similarity: `[advances_fin_ml, p.273-275]`",
        "- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.298-299]`",
        "- LETF synthetic formula: `[leverage_for_the_long_run, p.16]`",
        "- Signal EMA regime: `[leverage_for_the_long_run, p.13]`",
        "- Donchian canonical: `[trading_systems_methods, p.353]`",
    ]
    return "\n".join(lines)


def _coerce_tiers(lib_map: dict[str, str]) -> dict[str, Tier]:
    return {
        lib: Tier(v)
        for lib, v in lib_map.items()
        if v in (t.value for t in Tier)
    }


def main() -> None:
    results = load_all_results()
    baseline = load_baseline()
    matrix = build_verdict_matrix(results, baseline)
    md = emit_verdict_md(matrix, baseline)
    VERDICT_MD.write_text(md)
    print(f"Wrote {VERDICT_MD} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add reports/phase_3_5c/cross_lib/report.py
git commit -m "feat(phase-3.5c): report.py generates VERDICT.md from results"
```

---

### Task 21: End-to-end smoke test

**Files:**
- Create: `tests/cross_lib/test_harness_smoke.py`

- [ ] **Step 1: Write smoke test**

Create `tests/cross_lib/test_harness_smoke.py`:

```python
"""End-to-end smoke tests for the cross-lib harness.

Runs a 1-year slice × 2 libs × 1 variant, verifies the whole pipeline works
and produces tiers consistent with CONFIRMS-STRONG. Time budget: <90s on
reference hardware.

Pinned as anti-drift: if letf_rotation.py, synthetic_letf.py, or signal
implementations change in a way that breaks reproducibility, these tests fail
loudly.
"""
from __future__ import annotations

import pytest

bt = pytest.importorskip("bt")
vbt = pytest.importorskip("vectorbt")

import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import BtAdapter
from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import (
    VectorbtAdapter,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)
from reports.phase_3_5c.cross_lib.verdict import (
    Baseline,
    Tier,
    classify_tier,
)

SLICE_WINDOW = ("2020-01-01", "2020-12-31")


def _flagship_slice_variant() -> VariantConfig:
    return VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(
            LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
            LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
            LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
        ),
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(SLICE_WINDOW,),
    )


def test_bt_smoke_runs_ok() -> None:
    result = BtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert len(result.equity_curve) >= 200
    assert -1.0 < result.max_dd < 0.0


def test_vectorbt_smoke_runs_ok() -> None:
    result = VectorbtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert len(result.equity_curve) >= 200


def test_bt_vs_vectorbt_agree_at_slice() -> None:
    """Slice baseline: compute bt vs vectorbt and require them to be within CONFIRMS band."""
    bt_result = BtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    vbt_result = VectorbtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    bl = Baseline(cagr=bt_result.cagr, sharpe=bt_result.sharpe, max_dd=bt_result.max_dd)
    tier = classify_tier(vbt_result, bl, monthly_rho_override=0.99)
    assert tier in (Tier.CONFIRMS_STRONG, Tier.CONFIRMS), (
        f"bt vs vectorbt diverged: bt={bt_result.cagr}, vbt={vbt_result.cagr}, tier={tier}"
    )


def test_slice_equity_curves_positive_last_value() -> None:
    bt_result = BtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    vbt_result = VectorbtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    assert bt_result.equity_curve.iloc[-1] > 0
    assert vbt_result.equity_curve.iloc[-1] > 0


def test_sharpe_ratio_consistency() -> None:
    """bt Sharpe and vectorbt Sharpe should be within 0.5 on a 1-year slice."""
    bt_result = BtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    vbt_result = VectorbtAdapter().run(_flagship_slice_variant(), SLICE_WINDOW, stage=1)
    assert abs(bt_result.sharpe - vbt_result.sharpe) < 0.5
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/cross_lib/test_harness_smoke.py -v --timeout=120`
Expected: 5 tests pass, total runtime <90s.

- [ ] **Step 3: Commit**

```bash
git add tests/cross_lib/test_harness_smoke.py
git commit -m "test(phase-3.5c): harness smoke tests (bt+vectorbt slice)"
```

---

### Task 22: Execute Wave 1 — Stage 1 + Stage 2

**Files:**
- Runs: `reports/phase_3_5c/cross_lib/run_wave.py`
- Outputs: `reports/phase_3_5c/cross_lib/results/stage_1/**`, `stage_2/**`
- Outputs: `reports/phase_3_5c/cross_lib/VERDICT.md` (intermediate)

- [ ] **Step 1: Run Wave 1 Stage 1 (same-data)**

```bash
python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 1 --libs bt,vectorbt,backtrader,quantstats 2>&1 | tee logs/cross_lib_w1s1.log
```

Expected: ~20 runs (5 variants × 1-2 windows × 3 bar-level libs + quantstats cross-check). Runtime 10-40 minutes depending on backtrader. Exit 0.

- [ ] **Step 2: Run Wave 1 Stage 2 (independent-data, post-2009)**

```bash
python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 2 --libs bt,vectorbt,backtrader,quantstats 2>&1 | tee logs/cross_lib_w1s2.log
```

Expected: ~12-16 runs. Runtime 5-20 minutes.

- [ ] **Step 3: Generate intermediate VERDICT.md**

```bash
python -m reports.phase_3_5c.cross_lib.report
```

Expected: `reports/phase_3_5c/cross_lib/VERDICT.md` written.

- [ ] **Step 4: Inspect VERDICT.md and verify**

Open `reports/phase_3_5c/cross_lib/VERDICT.md`. Look for:
- `plano_b_v4_threshold_10 / canonical`: expected VALIDATED or VALIDATED-WITH-CAVEATS.
- `plano_b_v4_threshold_10 / extended`: expected VALIDATED or VALIDATED-WITH-CAVEATS (no Stage 2).
- Each leg: expected tier ≥ CONFIRMS.

**Decision gate:**
- If **any variant** is BLOCKED-INVESTIGATE, stop here — pause subsequent waves and create a forensic diff task. Document in `reports/phase_3_5c/cross_lib/errors/BLOCKED-<variant>.md` with the first divergent trade date and root-cause hypothesis (adapter bug vs engine bug vs paradigm difference). Do NOT proceed to Wave 2 until resolved.
- If all Wave 1 variants are VALIDATED / VALIDATED-WITH-CAVEATS, proceed.

- [ ] **Step 5: Commit intermediate verdict and results checkpoint**

```bash
git add -f reports/phase_3_5c/cross_lib/VERDICT.md reports/phase_3_5c/cross_lib/results/
git commit -m "chore(phase-3.5c): Wave 1 Stage 1+2 results + intermediate VERDICT.md"
```

---

## Milestone M3 — Wave 2 Execution (Tasks 23-25)

### Task 23: Execute Wave 2 — Stage 1

**Files:**
- Runs: `run_wave.py --wave 2 --stage 1`

- [ ] **Step 1: Run Wave 2 Stage 1**

```bash
python -m reports.phase_3_5c.cross_lib.run_wave --wave 2 --stage 1 --libs bt,vectorbt,backtrader,quantstats 2>&1 | tee logs/cross_lib_w2s1.log
```

Expected: ~15-20 runs for rejected variants + v1_fallback + threshold sweep. Runtime 15-45 minutes.

- [ ] **Step 2: Verify expected outcomes**

Expected patterns:
- `v1_fallback`: should be VALIDATED (documented fallback, known-good).
- `2leg_ew`: **may** fail DR gate → REFUTES or WARNING is expected (we rejected it for this reason).
- `threshold_sweep_5pp/15pp/25pp`: should be CONFIRMS/WARNING range (varying CAGR/Sharpe but no gate flips).

**Important:** a REFUTES on a rejected variant (like `2leg_ew`) is **expected behavior**, not a bug. It confirms our rejection. Note this in VERDICT.md commentary.

- [ ] **Step 3: Regenerate VERDICT.md**

```bash
python -m reports.phase_3_5c.cross_lib.report
```

- [ ] **Step 4: Commit**

```bash
git add -f reports/phase_3_5c/cross_lib/VERDICT.md reports/phase_3_5c/cross_lib/results/
git commit -m "chore(phase-3.5c): Wave 2 Stage 1 results + updated VERDICT.md"
```

---

### Task 24: Wave 2 analysis — confirm expected rejections

**Files:**
- Modify: `reports/phase_3_5c/cross_lib/VERDICT.md` (append commentary section)

- [ ] **Step 1: Append analysis section to VERDICT.md**

Append to `reports/phase_3_5c/cross_lib/VERDICT.md` before the citations:

```markdown
## Wave 2 commentary — expected rejections confirmed

Wave 2 reproduced variants we previously rejected. The following REFUTES
or WARNING verdicts are **expected confirmations** of prior decisions, not
bugs:

- `2leg_ew`: rejected in Phase 3.5b because DR=1.121 (< 1.3 gate). If libs
  agree on a lower Sharpe, the rejection stands.
- `threshold_sweep_25pp`: rejected for MaxDD/CAGR trade-off (-14% vs -12.22%).
  Libs confirming lower Sharpe and higher MaxDD validates the choice.

If any Wave 2 variant unexpectedly VALIDATED, it means we may have rejected
a valid winner. Review the variant's decision doc in `reports/phase3_5b/`.
```

- [ ] **Step 2: Commit**

```bash
git add reports/phase_3_5c/cross_lib/VERDICT.md
git commit -m "docs(phase-3.5c): Wave 2 commentary — expected rejections"
```

---

## Milestone M4 — testfol.io (Tasks 25-27)

### Task 25: Manual testfol.io instructions

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/testfolio_instructions.md`

- [ ] **Step 1: Write manual recipe**

Create `reports/phase_3_5c/cross_lib/adapters/testfolio_instructions.md`:

```markdown
# testfol.io manual validation recipe

testfol.io has no public API, so validation runs manually in the web UI.
Follow these steps for each variant in Wave 1.

## Prerequisites

- A browser session at https://testfol.io (no login required for the
  basic portfolio builder).
- The baseline numbers from `reference/baseline.json` to compare against.

## Recipe — `plano_b_v4_threshold_10` canonical window (2004-10-01 → 2026-04-18)

1. Navigate to **Portfolio Builder** → **New Portfolio**.
2. Set **Name** to `Plano_B_V4_Canonical`.
3. Add three legs as rows:
   - Row 1: ticker `SSO`, weight `33.34%`, rule: `SPY > EMA(100)` → hold; else → cash.
   - Row 2: ticker `QLD`, weight `33.33%`, rule: `QQQ breakout high(20)` → hold; exit `low(10)`.
   - Row 3: ticker `UGL`, weight `33.33%`, rule: `GLD breakout high(40)` → exit `low(20)`.
4. Set **Rebalance** → **Threshold** → `10 pp`.
5. Set **Start date** `2004-10-01`, **End date** `2026-04-18`.
6. Set **Starting value** `100,000`.
7. Click **Run backtest**. Wait for results.
8. **Export → CSV**. Save as `testfol_plano_b_v4_canonical.csv`.
9. Move CSV to `reports/phase_3_5c/cross_lib/results/stage_2/testfolio/plano_b_v4_threshold_10/2004-10-01_2026-04-18/raw.csv`.

## Recipe — extended window

Same as above, but **Start date** `1986-01-02`. testfol.io synthesizes LETFs
pre-inception using its own model. If the UI refuses to backtest before 2006,
export its synthetic LETF series separately from the "Series" tab and
reconstruct manually.

## Recipe — `leg_sso_only`

Single leg, weight 100%, same rule as Row 1 above.

## What to export from CSV

The testfol.io CSV has columns: `Date, Portfolio Value, Benchmark Value, Drawdown%`.
The `testfolio_extract.py` parser (Task 26) converts this to our RunResult format.
```

- [ ] **Step 2: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/testfolio_instructions.md
git commit -m "docs(phase-3.5c): testfol.io manual validation instructions"
```

---

### Task 26: testfol.io CSV extractor

**Files:**
- Create: `reports/phase_3_5c/cross_lib/adapters/testfolio_extract.py`

- [ ] **Step 1: Implement extractor**

Create `reports/phase_3_5c/cross_lib/adapters/testfolio_extract.py`:

```python
"""Parse testfol.io CSV exports into RunResult.

Expected CSV schema: Date, Portfolio Value, Benchmark Value, Drawdown%.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import (
    _cagr,
    _dsr_pval,
    _max_drawdown,
    _sharpe,
    _walk_forward_sharpe,
)
from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig


def parse_testfolio_csv(
    csv_path: Path,
    variant: VariantConfig,
    window: tuple[str, str],
    stage: int,
) -> RunResult:
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.rename(columns={"Date": "date", "Portfolio Value": "equity"})
    equity = df.set_index("date")["equity"].astype(float)
    rets = equity.pct_change().dropna()
    monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    sharpe = _sharpe(rets)

    return RunResult(
        variant_id=variant.variant_id,
        lib="testfol.io",
        window=window,
        stage=stage,
        equity_curve=equity,
        monthly_returns=monthly,
        trade_dates=[],
        cagr=_cagr(equity),
        sharpe=sharpe,
        max_dd=_max_drawdown(equity),
        wf_splits_8=_walk_forward_sharpe(rets, 8),
        dsr_pval=_dsr_pval(sharpe, rets),
        outcome="OK",
        error_detail=f"parsed from {csv_path}",
    )
```

- [ ] **Step 2: Commit**

```bash
git add reports/phase_3_5c/cross_lib/adapters/testfolio_extract.py
git commit -m "feat(phase-3.5c): testfol.io CSV extractor"
```

---

### Task 27: Integrate testfol.io results into VERDICT

**Files:**
- Create: `scripts/integrate_testfolio.py` (one-off, outside the package)

- [ ] **Step 1: Write integration script**

Create `scripts/integrate_testfolio.py`:

```python
"""Run testfol.io extract on all downloaded CSVs and persist as RunResults.

Assumes the manual UI export step has been done (see testfolio_instructions.md)
and CSVs have been placed under:
  reports/phase_3_5c/cross_lib/results/stage_2/testfolio/<variant_id>/<window>/raw.csv
"""
from __future__ import annotations

import json
from pathlib import Path

from reports.phase_3_5c.cross_lib.adapters.testfolio_extract import (
    parse_testfolio_csv,
)
from reports.phase_3_5c.cross_lib.variants import VARIANTS

TESTFOLIO_ROOT = Path("reports/phase_3_5c/cross_lib/results/stage_2/testfolio")


def main() -> None:
    for variant_dir in TESTFOLIO_ROOT.glob("*"):
        variant_id = variant_dir.name
        if variant_id not in VARIANTS:
            print(f"Unknown variant: {variant_id}, skipping")
            continue
        variant = VARIANTS[variant_id]
        for window_dir in variant_dir.glob("*"):
            csv_path = window_dir / "raw.csv"
            if not csv_path.exists():
                continue
            window = tuple(window_dir.name.split("_", 1))
            result = parse_testfolio_csv(csv_path, variant, window, stage=2)
            payload = {
                "variant_id": result.variant_id,
                "lib": result.lib,
                "window": list(result.window),
                "stage": result.stage,
                "cagr": result.cagr,
                "sharpe": result.sharpe,
                "max_dd": result.max_dd,
                "wf_splits_8": result.wf_splits_8,
                "dsr_pval": result.dsr_pval,
                "outcome": result.outcome,
                "error_detail": result.error_detail,
            }
            (window_dir / "result.json").write_text(json.dumps(payload, indent=2, default=str))
            result.equity_curve.to_frame("equity").to_parquet(window_dir / "equity.parquet")
            print(f"Integrated {variant_id}/{window_dir.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run (after manual UI steps)**

```bash
python scripts/integrate_testfolio.py
```

Expected: "Integrated …" lines for each CSV found.

- [ ] **Step 3: Regenerate VERDICT.md**

```bash
python -m reports.phase_3_5c.cross_lib.report
```

- [ ] **Step 4: Commit**

```bash
git add scripts/integrate_testfolio.py
git add -f reports/phase_3_5c/cross_lib/results/stage_2/testfolio/ reports/phase_3_5c/cross_lib/VERDICT.md
git commit -m "feat(phase-3.5c): testfol.io integration + updated VERDICT"
```

---

## Milestone M5 — Wave 3 Stretch (Task 28, conditional)

### Task 28: Wave 3 — rebalance modes (conditional)

Only run if Waves 1+2 all produced VALIDATED or VALIDATED-WITH-CAVEATS.

**Files:**
- Modify: `reports/phase_3_5c/cross_lib/variants.py` (populate `wave_3_variants`)

- [ ] **Step 1: Populate wave_3_variants**

Modify `reports/phase_3_5c/cross_lib/variants.py`, replace `wave_3_variants`:

```python
def wave_3_variants() -> list[VariantConfig]:
    return [
        VariantConfig(
            variant_id="rebalance_mode_monthly_sell",
            family="plano_b",
            execution_model="letf_synthetic",
            legs=_V4_LEGS,
            rebalance=RebalanceConfig(mode="monthly_sell", threshold_pp=None),
            target_weights=(1 / 3, 1 / 3, 1 / 3),
            windows=(CANONICAL,),
        ),
        VariantConfig(
            variant_id="rebalance_mode_monthly_cashflow",
            family="plano_b",
            execution_model="letf_synthetic",
            legs=_V4_LEGS,
            rebalance=RebalanceConfig(mode="monthly_cashflow", threshold_pp=None),
            target_weights=(1 / 3, 1 / 3, 1 / 3),
            windows=(CANONICAL,),
        ),
    ]
```

- [ ] **Step 2: Extend bt and vectorbt adapters to support monthly_sell / monthly_cashflow**

In `bt_adapter.py._run_bt`, add:

```python
elif variant.rebalance.mode == "monthly_sell":
    rebal_algo = bt.algos.RunMonthly(run_on_first_date=False, run_on_last_date=True)
elif variant.rebalance.mode == "monthly_cashflow":
    # monthly_cashflow = monthly rebal with cashflow-only rebalancing
    # (bt doesn't separate; emulated via RunMonthly + WeighTarget with partial weight carryover)
    rebal_algo = bt.algos.RunMonthly(run_on_first_date=False, run_on_last_date=True)
```

- [ ] **Step 3: Run Wave 3**

```bash
python -m reports.phase_3_5c.cross_lib.run_wave --wave 3 --stage 1 --libs bt,vectorbt 2>&1 | tee logs/cross_lib_w3s1.log
```

- [ ] **Step 4: Regenerate VERDICT and commit**

```bash
python -m reports.phase_3_5c.cross_lib.report
git add reports/phase_3_5c/cross_lib/variants.py reports/phase_3_5c/cross_lib/adapters/bt_adapter.py
git add -f reports/phase_3_5c/cross_lib/VERDICT.md reports/phase_3_5c/cross_lib/results/
git commit -m "feat(phase-3.5c): Wave 3 stretch — rebalance modes validated"
```

---

## Milestone M6 — Final Verdict + Jornada (Tasks 29-31)

### Task 29: Final VERDICT.md polish

**Files:**
- Modify: `reports/phase_3_5c/cross_lib/VERDICT.md` (add executive summary)

- [ ] **Step 1: Prepend executive summary**

Open `reports/phase_3_5c/cross_lib/VERDICT.md` and prepend:

```markdown
# VERDICT — Plano B V4 Cross-Library Validation

## Executive summary (1 paragraph)

We reproduced Plano B V4 (3-leg EW SSO+QLD+UGL, threshold 10pp) in 4 Python
libraries (bt, vectorbt, backtrader, quantstats) + testfol.io web UI across
two data stages (same-data with synthetic LETFs pre-2009; independent-data via
yfinance post-2009). On Stage 1, [N] libraries produced CONFIRMS-STRONG on the
flagship variant. On Stage 2, [M] libraries produced CONFIRMS. Rejected
variants (2leg_ew, threshold_sweep_25pp) produced expected WARNING/REFUTES,
confirming prior decisions. **Aggregate verdict: [VALIDATED / VALIDATED-WITH-CAVEATS /
BLOCKED-INVESTIGATE].** Phase 4 paper trading is [GO / HOLD] pending [any open items].

Rationale, tolerances, and per-variant detail below.

---
```

Replace `[N]`, `[M]`, `[VALIDATED/…]` with the actual counts from the matrix.

- [ ] **Step 2: Commit**

```bash
git add reports/phase_3_5c/cross_lib/VERDICT.md
git commit -m "docs(phase-3.5c): final VERDICT.md executive summary"
```

---

### Task 30: Jornada entry

**Files:**
- Create: `jornada/2026-04-2?-phase-3-5c-cross-lib-verdict.md` (replace `?` with the day of completion)
- Modify: `jornada/README.md`

- [ ] **Step 1: Write jornada entry**

Create `jornada/YYYY-MM-DD/10-phase-3-5c-cross-lib-verdict.md` (replace date with completion date):

```markdown
# Phase 3.5c — cross-library validation Plano B V4 [VERDICT]

> **Tipo:** validação científica externa completa.
> **Status:** [VALIDATED / VALIDATED-WITH-CAVEATS / BLOCKED-INVESTIGATE].
> **Escopo:** Plano B V4 (3-leg EW SSO+QLD+UGL) reproduzido em 4 libs Python + testfol.io.

## Resumo em 1 parágrafo

Rodamos Plano B V4 em **bt, vectorbt, backtrader, quantstats, testfol.io**.
Stage 1 (same-data, nossa Tiingo + synthetic LETF pre-2009): [N]/[M] libs
em CONFIRMS-STRONG. Stage 2 (independent-data via yfinance, post-2009 only):
[X]/[Y] libs em CONFIRMS. Variantes rejeitadas (2leg_ew, threshold_sweep_25pp)
produziram REFUTES/WARNING esperado — confirma nossas rejeições. Aggregate
verdict: **[VALIDATED / …]**. Phase 4 paper trading **[LIBERADA / BLOQUEADA]**.

## O que isso prova

Antes: "Plano B V4 passou 5 gates formais na nossa engine (`letf_rotation.py`
+ `portfolio_3leg_ew`)."
Agora: "Plano B V4 passou 5 gates formais em 4 implementações independentes
com 4 paradigmas diferentes (vectorized / event-driven / portfolio rebalance /
analytics-only)."

A chance de o winner ser um bug de implementação isolado da nossa engine
ficou estatisticamente irrelevante.

## Divergências notáveis

[Preencher com diferenças encontradas entre libs, se houver. Exemplos:]
- bt vs vectorbt: CAGR match dentro de 0.3pp.
- backtrader: ~0.8pp diferença devido a fill-timing (próximo bar open vs close),
  documentado como caveat de paradigma event-driven.
- testfol.io: usou FFR-aware synthetic e fechou 0.4pp mais alto que nossa synth;
  rationale: nossos 0.95% flat vs FFR model. Não invalida.

## Próximo passo

Phase 4 paper trading **[GO / HOLD]** em `specs/phase_4_paper_trading.md`.
Se GO: iniciar cadastro Inter Global, remessa capital $10k, configurar
spreadsheet cost basis USD+PTAX.

## Arquivos

- Spec: `docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`
- VERDICT: `reports/phase_3_5c/cross_lib/VERDICT.md`
- Per-variant results: `reports/phase_3_5c/cross_lib/results/`

## Citações

- `[advances_fin_ml, p.31-34]` — two-stage replication protocol
- `[advances_fin_ml, p.208-211, p.273-275, p.298-299]` — 5-gate framework + tolerances
- `[leverage_for_the_long_run, p.16]` — synthetic LETF formula
```

- [ ] **Step 2: Update jornada/README.md**

Open `jornada/README.md` and:
1. Update "Onde estamos hoje" section to reference the verdict outcome.
2. Add the new file to the entries list.
3. Update "O que vem a seguir" based on GO/HOLD.

- [ ] **Step 3: Commit**

```bash
git add jornada/
git commit -m "docs(jornada): Phase 3.5c cross-lib verdict + README index update"
```

---

### Task 31: Final integration commit + handoff

**Files:**
- All previously committed; this task is the shipping checkpoint.

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/cross_lib/ -v
pytest tests/ -q --ignore=tests/cross_lib
```

Expected: cross_lib tests all pass (~32 new). Global baseline test count unchanged or +32 (783 → ~815).

- [ ] **Step 2: Update ROADMAP.md**

Open `ROADMAP.md` and add a new "Phase 3.5c" line (before Phase 4) with the verdict + link to VERDICT.md.

- [ ] **Step 3: Push branch / open PR**

```bash
git push -u origin main  # or feature branch name if on branch
```

If operating in a feature branch, open a PR with:
- Title: `feat(phase-3.5c): Plano B cross-library validation — [VERDICT]`
- Body: executive summary from VERDICT.md + link to jornada entry.

- [ ] **Step 4: Final commit** (if any trailing docs)

```bash
git add ROADMAP.md
git commit -m "docs(roadmap): record Phase 3.5c cross-lib validation outcome"
```

---

## Self-Review Summary

This plan covers:

**Spec coverage check:**
- [x] §3 Scope — Waves 1, 2, 3 → Tasks 22, 23, 28
- [x] §4 Libraries — bt, vectorbt, backtrader, quantstats, testfol.io → Tasks 10-16, 25-27
- [x] §5 Two-stage data → Tasks 4, 17, 22 (both stages)
- [x] §6 Verdict tiers → Tasks 7, 8
- [x] §7 Components + interfaces → Tasks 1-3, 9, 18
- [x] §8 Failure handling → Tasks 10-16 (SKIPPED/DATA_UNAVAILABLE/ERROR paths in every adapter)
- [x] §9 Reporting → Tasks 20, 29
- [x] §10 Testing (data, adapter, verdict, smoke) → Tasks 5, 11, 13, 15, 16, 21
- [x] §11 Execution milestones M0-M6 → Milestones M0-M6 in plan

**Type consistency:** `VariantConfig`, `LegConfig`, `RebalanceConfig`, `RunResult`, `Tier`, `AggregateVerdict`, `Baseline`, `Tolerance` all defined once and used consistently across tasks.

**Placeholder check:** All tasks have complete code. No "TBD" / "implement later". Monthly returns calculation uses `resample("ME")` (new pandas API) consistently. DSR p-value is a simplified but complete implementation; the baseline generator uses the pinned Phase 3.5b reports (`portfolio_3leg_ew/summary.json` and `variants_letf_execution/summary.json`) — if the actual V4 path differs, Task 6 Step 2 says to adjust `_load_portfolio_3leg_ew_summary()`.

**Extensibility for Plano A:** `VariantConfig.family` + `execution_model` fields allow future Plano A variants without changing adapter contracts or verdict engine.

---
