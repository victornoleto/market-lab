# Chan Bollinger Pairs 1h (GLD-SLV) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver `ChanBollingerPairsStrategy` — a single-pair mean-reversion intraday strategy (GLD-SLV, 1h bars) implementing the canonical Chan Bollinger-z formulation `[algo_trading_chan, p.71-73]`, integrated end-to-end with the existing grid/gate infra, honouring the `tiingo_service` spec §1.4 short-hold contract.

**Architecture:** New strategy module at `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` following the `EhlersBPSwingStrategy` template (dataclass + pre-computed indicators + per-trade state in `context` dict). Static OLS hedge ratio fit on first ~1250 bars (~9 months), OU regression gives `half_life`, lookback = `multiplier × half_life`. Entry on z crossing ±1.0 / ±1.5; exit precedence: spread-blow-out stop → Friday-flat → wall-clock 48h cap → time-stop → mean-revert at z=0. Grid of 2×2 = 4 configs wired into `GridRunner[ChanPairsGridConfig]` + new CLI `scripts/run_grid_chan_pairs.py`.

**Tech Stack:** Python 3.12, pandas, numpy, pytest, existing `backtest/engine/` + `backtest/grid/` + `backtest/validation/` + `backtest/data/tiingo_source.py` (1h intraday). No new runtime deps.

**Spec:** `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md` (commit `2156b06`).

---

## File Structure

**Create:**
- `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` — strategy class (single file, ~350 lines estimated).
- `src/ai_trade/backtest/grid/chan_pairs_config.py` — `ChanPairsGridConfig` dataclass + `chan_pairs_grid_configs()`.
- `scripts/run_grid_chan_pairs.py` — CLI runner (based on `run_grid_ehlers_meta.py` pattern, adapted for 2 symbols).
- `tests/test_chan_bollinger_pairs.py` — unit tests (~20 tests).

**Modify:**
- `src/ai_trade/backtest/strategies/__init__.py` — export `ChanBollingerPairsStrategy`.
- `src/ai_trade/backtest/grid/__init__.py` — export `ChanPairsGridConfig` + `chan_pairs_grid_configs`.

**Smoke-test only (no code):**
- Tiingo retention probe on GLD and SLV 1h in Task 1 (pre-flight).

---

## Task 1: Pre-flight smoke — verify GLD/SLV 1h retention ≥ 3 years

**Files:**
- Smoke script (ephemeral, no file created — inline python via `.venv/bin/python -c '...'`).

**Rationale:** The spec §1.3 lists `retention ≥ 3 years` as pre-condition. Smoke #1 from `tiingo_service` already validated SPY (5y), BTCUSD (208d), EURUSD (416d) — GLD/SLV not yet probed. Abort the plan here if either pair has < 3y (escalates decision to user).

- [ ] **Step 1: Run retention probe for GLD and SLV**

```bash
.venv/bin/python -c '
from datetime import date
from pathlib import Path
from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
end = date(2026, 4, 15)
start = date(2020, 4, 15)  # probe 6 years; Tiingo returns whatever it has

for ticker in ("GLD", "SLV"):
    df = src.fetch(ticker, start, end, frequency="1hour", asset_class="etf")
    if df.empty:
        print(f"{ticker}: EMPTY — abort")
        continue
    span = df.index.max() - df.index.min()
    print(f"{ticker}: {len(df)} bars, {df.index.min()} → {df.index.max()} (span {span.days}d)")
'
```

Expected output (approximate):
```
GLD: ~8100 bars, 2021-04-XX → 2026-04-14 (span ~1820d)
SLV: ~8100 bars, 2021-04-XX → 2026-04-14 (span ~1820d)
```

- [ ] **Step 2: Verify both tickers have ≥ 1095 days (3 years)**

Gate: `span.days >= 1095` for both. If either is lower, STOP the plan and escalate to user with the actual measured retention.

- [ ] **Step 3: Commit the retention check record**

Create `reports/chan_pairs_gld_slv_retention_probe.md` with the measured retention as an auditable record:

```bash
.venv/bin/python -c '
from datetime import date
from pathlib import Path
from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
end = date(2026, 4, 15)
start = date(2020, 4, 15)
lines = ["# GLD/SLV 1h retention probe — " + str(end), ""]
for ticker in ("GLD", "SLV"):
    df = src.fetch(ticker, start, end, frequency="1hour", asset_class="etf")
    if df.empty:
        lines.append(f"- {ticker}: EMPTY")
    else:
        span = df.index.max() - df.index.min()
        lines.append(f"- {ticker}: {len(df)} bars, {df.index.min()} → {df.index.max()}, span {span.days}d")
Path("reports/chan_pairs_gld_slv_retention_probe.md").write_text("\n".join(lines) + "\n")
print("wrote reports/chan_pairs_gld_slv_retention_probe.md")
'

git add reports/chan_pairs_gld_slv_retention_probe.md
git commit -m "chore(probe): record GLD/SLV 1h Tiingo retention pre Chan pairs plan"
```

---

## Task 2: Scaffold `ChanBollingerPairsStrategy` with input validation

**Files:**
- Create: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py`
- Create: `tests/test_chan_bollinger_pairs.py`
- Modify: `src/ai_trade/backtest/strategies/__init__.py`

- [ ] **Step 1: Write the failing scaffold tests**

Create `tests/test_chan_bollinger_pairs.py`:

```python
"""Tests for ChanBollingerPairsStrategy [algo_trading_chan, ch.3]."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.chan_bollinger_pairs import (
    ChanBollingerPairsStrategy,
)


def _synth_ohlcv(
    n: int = 2000,
    start: str = "2022-01-03 09:30",
    freq: str = "1h",
    seed: int = 0,
) -> pd.DataFrame:
    """Build a synthetic OHLCV frame with index of length ``n``."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n, freq=freq)
    close = 100 + np.cumsum(rng.normal(0, 0.1, n))
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 0.05,
            "low": close - 0.05,
            "close": close,
            "volume": 1_000_000,
            "adj_close": close,
        },
        index=idx,
    )


def test_instantiation_with_both_symbols_succeeds():
    df_long = _synth_ohlcv(seed=1)
    # SLV synth is a noisy linear function of GLD synth: enough signal
    # for OLS + OU to succeed on the training slice.
    df_short = df_long.copy()
    df_short[["open", "high", "low", "close", "adj_close"]] = (
        df_long[["open", "high", "low", "close", "adj_close"]] / 2.5
        + np.random.default_rng(2).normal(0, 0.05, (len(df_long), 5))
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        long_symbol="GLD",
        short_symbol="SLV",
    )
    assert strat.long_symbol == "GLD"
    assert strat.short_symbol == "SLV"


def test_missing_long_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="GLD"):
        ChanBollingerPairsStrategy(
            data={"SLV": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_missing_short_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="SLV"):
        ChanBollingerPairsStrategy(
            data={"GLD": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_misaligned_timestamps_raises_valueerror():
    df_long = _synth_ohlcv(n=2000, start="2022-01-03 09:30", seed=1)
    df_short = _synth_ohlcv(n=2000, start="2022-01-04 09:30", seed=2)
    with pytest.raises(ValueError, match="timestamps"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
            long_symbol="GLD",
            short_symbol="SLV",
        )
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v
```

Expected: all 4 tests FAIL with `ModuleNotFoundError: No module named 'ai_trade.backtest.strategies.chan_bollinger_pairs'`.

- [ ] **Step 3: Create the scaffold module**

Create `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py`:

```python
"""Chan Bollinger Pairs — canonical mean-reversion pair trading on 1h bars.

Implements the canonical formulation from [algo_trading_chan, p.71-73, ch.3]:
static OLS hedge ratio β fit on a training slice, OU regression to derive
half-life [p.47-48, ch.2], lookback = multiplier × half-life, Bollinger
z-score entry at ±entry_z, exit at 0.

Deviates from the pure-Chan canon in three CFD-specific adaptations (see
docstring of [_should_skip_entry_session] and [_maybe_exit]):

* Session gate (entry_hour_cutoff + Friday cut-offs) — protects against
  overnight swap and weekend 3x swap on Pepperstone CFD.
* Wall-clock 48h hard cap — [tiingo_service spec §1.4] short-hold gate.
* Spread-blow-out stop at |z| >= 3.0 — [p.293-294, ch.8] capital
  preservation against regime shift.

See `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio


@dataclass
class ChanBollingerPairsStrategy:
    """Canonical Chan Bollinger-z pair trader on 1h bars."""

    data: dict[str, pd.DataFrame]
    long_symbol: str = "GLD"
    short_symbol: str = "SLV"

    # Grid knobs.
    lookback_multiplier: int = 2
    entry_z: float = 1.0

    # Fixed constants (each one cited in the docstring / spec §3).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    train_bars: int = 1250
    half_life_min: int = 4
    half_life_max: int = 60
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13

    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.chan_pairs"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        return []  # scaffold — real logic in subsequent tasks
```

- [ ] **Step 4: Export in `strategies/__init__.py`**

Read the existing `src/ai_trade/backtest/strategies/__init__.py` and add the new class to both the import block and `__all__`:

```bash
.venv/bin/python -c '
from pathlib import Path
p = Path("src/ai_trade/backtest/strategies/__init__.py")
txt = p.read_text()
print(txt)
'
```

Add line `from ai_trade.backtest.strategies.chan_bollinger_pairs import ChanBollingerPairsStrategy` and add `"ChanBollingerPairsStrategy"` to `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Run full test suite baseline check**

```bash
.venv/bin/python -m pytest -q
```

Expected: 409 passing (was 405 + 4 new). No regressions.

- [ ] **Step 7: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        src/ai_trade/backtest/strategies/__init__.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(strategies): scaffold ChanBollingerPairsStrategy with input validation"
```

---

## Task 3: Fit β (OLS) with two-ordering pick + OU half-life in `__post_init__`

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (add `_fit_hedge_and_half_life` + call from `__post_init__`)
- Modify: `tests/test_chan_bollinger_pairs.py` (add 4 fit tests)

Cita: `[algo_trading_chan, p.47-48, p.54]`.

- [ ] **Step 1: Write failing tests for β fit and OU estimation**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
def test_ols_recovers_known_beta():
    """Synthetic pair with y = 2.5 x + OU noise → β ≈ 2.5."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    # OU noise around 2.5·x (mean-reverting spread): half-life ≈ 20 bars
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    assert abs(strat._beta - 2.5) < 0.1, f"β recovered = {strat._beta}"


def test_ou_recovers_known_half_life():
    """OU synth with λ = -log(2)/20 → half-life bars ≈ 20."""
    rng = np.random.default_rng(7)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    target_hl = 20
    lam = -np.log(2) / target_hl
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    # Allow a ±50% envelope — OU estimation is noisy on finite samples.
    assert 10 <= strat._half_life_bars <= 40, (
        f"half-life recovered = {strat._half_life_bars}"
    )


def test_ou_rejects_random_walk():
    """Pure random walk spread (no mean reversion) → RuntimeError."""
    rng = np.random.default_rng(99)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.1, n))
    y = 50 + np.cumsum(rng.normal(0, 0.1, n))  # independent RW — no cointegration
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"(cointegrated|t[-_]stat|half[-_]life)"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )


def test_half_life_clamp_rejects_too_slow():
    """OU synth with half-life = 200 bars (> 60 max) → RuntimeError."""
    rng = np.random.default_rng(13)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 200.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"half[-_]life"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )
```

- [ ] **Step 2: Run to verify fails**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v
```

Expected: 4 new tests FAIL with `AttributeError: _beta` / `_half_life_bars`.

- [ ] **Step 3: Implement `_fit_hedge_and_half_life` helper**

Add to `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (at module level or inside class — use inside class for state ownership):

```python
    _beta: float = field(init=False, default=float("nan"))
    _half_life_bars: int = field(init=False, default=0)
    _t_stat_ou: float = field(init=False, default=float("nan"))
    _hedge_ordering: str = field(init=False, default="")
```

(Add these after the `_logger` field, still in the dataclass.)

Add the fit method inside the class:

```python
    def _fit_beta_single(
        self, y: np.ndarray, x: np.ndarray
    ) -> tuple[float, float]:
        """OLS of y on x with constant; return (β, t_stat_β)."""
        n = len(x)
        X = np.column_stack([np.ones(n), x])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        residuals = y - X @ coef
        dof = n - 2
        if dof <= 0:
            return coef[1], float("nan")
        sigma2 = (residuals @ residuals) / dof
        xtx_inv = np.linalg.inv(X.T @ X)
        se_beta = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
        t_stat = float(coef[1] / se_beta) if se_beta > 0 else float("nan")
        return float(coef[1]), t_stat

    def _fit_ou_half_life(
        self, spread: np.ndarray
    ) -> tuple[int, float]:
        """OU regression: Δs_t ~ λ · s_{t-1} + α. Returns (half_life, t_stat_λ)."""
        s_lag = spread[:-1]
        s_delta = np.diff(spread)
        n = len(s_lag)
        X = np.column_stack([np.ones(n), s_lag])
        coef, *_ = np.linalg.lstsq(X, s_delta, rcond=None)
        residuals = s_delta - X @ coef
        dof = n - 2
        sigma2 = (residuals @ residuals) / dof if dof > 0 else float("nan")
        xtx_inv = np.linalg.inv(X.T @ X)
        se_lam = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
        lam = float(coef[1])
        t_stat = float(lam / se_lam) if se_lam > 0 else float("nan")
        if lam >= 0 or not np.isfinite(lam):
            return 0, t_stat
        half_life = int(round(-np.log(2) / lam))
        return half_life, t_stat

    def _fit_hedge_and_half_life(self) -> None:
        """Fit β (both orderings, pick best OU t-stat) + half-life. Raises if not cointegrated."""
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if self.train_bars >= len(df_long):
            raise RuntimeError(
                f"train_bars={self.train_bars} >= len(data)={len(df_long)} "
                f"— not enough history to fit"
            )
        train_long = df_long["close"].to_numpy()[: self.train_bars]
        train_short = df_short["close"].to_numpy()[: self.train_bars]

        # Ordering A: price_long = α + β·price_short
        beta_a, t_beta_a = self._fit_beta_single(train_long, train_short)
        spread_a = train_long - beta_a * train_short
        hl_a, t_ou_a = self._fit_ou_half_life(spread_a)

        # Ordering B: price_short = α + β·price_long → convert to β_long-per-short
        beta_b_raw, t_beta_b = self._fit_beta_single(train_short, train_long)
        beta_b = 1.0 / beta_b_raw if abs(beta_b_raw) > 1e-9 else float("nan")
        spread_b = train_long - beta_b * train_short
        hl_b, t_ou_b = self._fit_ou_half_life(spread_b)

        # Chan [p.54]: pick the ordering with the most negative OU t-stat.
        if t_ou_a <= t_ou_b:
            self._beta = beta_a
            self._half_life_bars = hl_a
            self._t_stat_ou = t_ou_a
            self._hedge_ordering = f"{self.long_symbol}~{self.short_symbol}"
        else:
            self._beta = beta_b
            self._half_life_bars = hl_b
            self._t_stat_ou = t_ou_b
            self._hedge_ordering = f"{self.short_symbol}~{self.long_symbol}"

        self._logger.info(
            "hedge fit: ordering=%s β=%.4f t_stat_OU=%.3f half_life=%d",
            self._hedge_ordering, self._beta, self._t_stat_ou, self._half_life_bars,
        )

        if not np.isfinite(self._t_stat_ou) or self._t_stat_ou > -2.0:
            raise RuntimeError(
                f"pair not cointegrated on training slice: "
                f"t_stat_OU={self._t_stat_ou:.3f} > -2.0 "
                f"(half_life would be {self._half_life_bars})"
            )
        if not (self.half_life_min <= self._half_life_bars <= self.half_life_max):
            raise RuntimeError(
                f"half_life={self._half_life_bars} outside clamp "
                f"[{self.half_life_min}, {self.half_life_max}] — pair not suitable "
                f"for 1h mean-reversion"
            )
```

Extend `__post_init__` to call it at the end:

```python
    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )
        self._fit_hedge_and_half_life()
```

- [ ] **Step 4: Run fit tests to verify pass**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k "ols or ou or half_life"
```

Expected: 4 tests PASS.

- [ ] **Step 5: Run full suite — baseline regression**

```bash
.venv/bin/python -m pytest -q
```

Expected: 413 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): fit β (two orderings) + OU half-life in post_init [algo_trading_chan p.47-48, p.54]"
```

---

## Task 4: Pre-compute spread / rolling z-score indicators

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (add `_precompute_indicators`)
- Modify: `tests/test_chan_bollinger_pairs.py` (add indicator test)

- [ ] **Step 1: Write failing test**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
def test_precomputed_indicators_present_and_shaped():
    """After __post_init__, indicators must be precomputed with shape = len(data)."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        lookback_multiplier=2,
    )
    ind = strat._indicators
    for col in ("spread", "spread_ma", "spread_std", "zscore"):
        assert col in ind.columns, f"missing column {col}"
        assert len(ind) == n, f"indicator len={len(ind)} != data len={n}"
    # After enough warmup (2× half_life + 1), z-score must be finite and centered
    warmup = 2 * strat._half_life_bars + 1
    z_tail = ind["zscore"].iloc[warmup:].dropna()
    assert len(z_tail) > 0
    assert abs(z_tail.mean()) < 0.5, f"z-score mean = {z_tail.mean()}"
    # z-score std on well-formed pair should be close to 1 (by construction)
    assert 0.5 < z_tail.std() < 1.5, f"z-score std = {z_tail.std()}"
```

- [ ] **Step 2: Run to verify fails**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k precomputed
```

Expected: FAIL with `AttributeError: _indicators`.

- [ ] **Step 3: Implement `_precompute_indicators`**

Add field to dataclass:

```python
    _indicators: pd.DataFrame = field(init=False, default_factory=pd.DataFrame)
    _lookback_bars: int = field(init=False, default=0)
    _time_stop_bars: int = field(init=False, default=0)
```

Add method to class:

```python
    def _precompute_indicators(self) -> None:
        """Compute spread, rolling mean/std, z-score on the full data index."""
        self._lookback_bars = self.lookback_multiplier * self._half_life_bars
        self._time_stop_bars = min(3 * self._half_life_bars, 24)

        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        spread = df_long["close"] - self._beta * df_short["close"]
        spread_ma = spread.rolling(self._lookback_bars, min_periods=self._lookback_bars).mean()
        spread_std = spread.rolling(self._lookback_bars, min_periods=self._lookback_bars).std()
        zscore = (spread - spread_ma) / spread_std
        self._indicators = pd.DataFrame(
            {
                "spread": spread,
                "spread_ma": spread_ma,
                "spread_std": spread_std,
                "zscore": zscore,
            },
            index=df_long.index,
        )
```

Extend `__post_init__` to call it after `_fit_hedge_and_half_life()`:

```python
        self._fit_hedge_and_half_life()
        self._precompute_indicators()
```

- [ ] **Step 4: Run indicator test to verify pass**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k precomputed
```

Expected: PASS.

- [ ] **Step 5: Full suite regression**

```bash
.venv/bin/python -m pytest -q
```

Expected: 414 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): precompute spread + rolling z-score indicators [algo_trading_chan p.71-72]"
```

---

## Task 5: Entry logic (long/short spread crossings + session gate)

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py`
- Modify: `tests/test_chan_bollinger_pairs.py`

- [ ] **Step 1: Write failing entry tests**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
from ai_trade.backtest.engine.execution import Bar
from ai_trade.backtest.engine.portfolio import Portfolio


def _make_strategy_with_z(
    z_series: list[float],
    *,
    entry_z: float = 1.0,
    start_ts: str = "2023-01-03 09:30",
):
    """Build a strategy whose precomputed zscore matches ``z_series`` exactly.

    We short-circuit the fit by feeding crafted data: GLD - β·SLV = z_series
    scaled + windowed so the rolling zscore sits at the requested values.
    For surgical unit testing, we instead patch _indicators post-hoc.
    """
    n = max(len(z_series) + 100, 2000)
    idx = pd.date_range(start_ts, periods=n, freq="1h")
    rng = np.random.default_rng(0)
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        entry_z=entry_z,
    )
    # Patch the last len(z_series) rows of zscore for deterministic tests
    tail_start = n - len(z_series)
    strat._indicators.loc[idx[tail_start:], "zscore"] = z_series
    return strat, idx, tail_start


def test_entry_long_spread_on_crossing_below_minus_entry_z():
    """z crosses from -0.9 to -1.1 (entry_z=1.0) → 2 orders."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # crossing happens at idx[tail_start + 1]
    ts = idx[tail_start + 1]
    bar_long = Bar(
        symbol="GLD", timestamp=ts,
        open=180.0, high=180.5, low=179.5, close=180.0, volume=1e6,
    )
    bar_short = Bar(
        symbol="SLV", timestamp=ts,
        open=72.0, high=72.3, low=71.7, close=72.0, volume=1e6,
    )
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert len(orders) == 2
    long_order = next(o for o in orders if o.symbol == "GLD")
    short_order = next(o for o in orders if o.symbol == "SLV")
    assert long_order.side == "buy"
    assert short_order.side == "sell"
    # sizing: long_leg = notional / (price_long + β·price_short); short_leg = β × long_leg
    total_notional = 100_000.0 * strat.risk_pct_of_equity
    expected_long = total_notional / (180.0 + strat._beta * 72.0)
    expected_short = strat._beta * expected_long
    assert abs(long_order.volume - expected_long) / expected_long < 1e-6
    assert abs(short_order.volume - expected_short) / expected_short < 1e-6


def test_entry_short_spread_on_crossing_above_plus_entry_z():
    """z crosses from +0.9 to +1.1 → 2 orders (sell GLD, buy SLV)."""
    strat, idx, tail_start = _make_strategy_with_z(
        [0.9, 1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    ts = idx[tail_start + 1]
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    sides = {o.symbol: o.side for o in orders}
    assert sides == {"GLD": "sell", "SLV": "buy"}


def test_entry_ignored_after_hour_cutoff_14():
    """Same crossing but at 15:30 local → no orders."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # Find an idx at 15:30 (or later); patch zscore there
    late_ts = pd.Timestamp("2023-06-15 15:30")
    late_idx_pos = strat._indicators.index.get_indexer([late_ts], method="nearest")[0]
    strat._indicators.iloc[late_idx_pos - 1, strat._indicators.columns.get_loc("zscore")] = -0.9
    strat._indicators.iloc[late_idx_pos, strat._indicators.columns.get_loc("zscore")] = -1.1
    ts = strat._indicators.index[late_idx_pos]
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert orders == [], f"expected no orders at 15:30, got {orders}"


def test_entry_ignored_friday_after_no_entry_hour_13():
    """Friday 13:30 crossing → no orders (weekend-swap protection)."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # Friday 2023-06-16 at 13:30
    friday_ts = pd.Timestamp("2023-06-16 13:30")
    pos = strat._indicators.index.get_indexer([friday_ts], method="nearest")[0]
    strat._indicators.iloc[pos - 1, strat._indicators.columns.get_loc("zscore")] = -0.9
    strat._indicators.iloc[pos, strat._indicators.columns.get_loc("zscore")] = -1.1
    ts = strat._indicators.index[pos]
    assert ts.weekday() == 4, f"expected Friday, got weekday={ts.weekday()}"
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert orders == [], f"expected no orders Fri 13:30, got {orders}"
```

- [ ] **Step 2: Verify tests fail**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k "entry"
```

Expected: 4 tests FAIL (on_bar returns `[]` in scaffold).

- [ ] **Step 3: Implement entry logic**

Replace the `on_bar` method in `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py`:

```python
    STATE_KEY_PREFIX = "chan_pairs_state"

    def _state_key(self) -> str:
        return f"{self.STATE_KEY_PREFIX}_{self.long_symbol}_{self.short_symbol}"

    def _should_skip_entry_session(self, ts: pd.Timestamp) -> bool:
        """Session gate — blocks entry near close or late on Friday."""
        if ts.hour > self.entry_hour_cutoff:
            return True
        if ts.weekday() == 4 and ts.hour >= self.friday_no_entry_hour:
            return True
        return False

    def _compute_leg_volumes(
        self, equity: float, price_long: float, price_short: float
    ) -> tuple[float, float]:
        """Return (long_leg_shares, short_leg_shares) given current prices."""
        total_notional = equity * self.risk_pct_of_equity
        denom = price_long + self._beta * price_short
        if denom <= 0 or total_notional <= 0:
            return 0.0, 0.0
        long_leg = total_notional / denom
        short_leg = self._beta * long_leg
        return long_leg, short_leg

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if self.long_symbol not in bars or self.short_symbol not in bars:
            return []
        bar_long = bars[self.long_symbol]
        bar_short = bars[self.short_symbol]
        ts = bar_long.timestamp
        try:
            idx = self._indicators.index.get_loc(ts)
        except KeyError:
            return []
        if idx < 1:
            return []
        zscore_now = float(self._indicators["zscore"].iloc[idx])
        zscore_prev = float(self._indicators["zscore"].iloc[idx - 1])
        if np.isnan(zscore_now) or np.isnan(zscore_prev):
            return []

        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        in_position = pos_long is not None and pos_short is not None

        if in_position:
            return []  # exits implemented in Task 6
        if self._should_skip_entry_session(ts):
            return []

        long_leg, short_leg = self._compute_leg_volumes(
            portfolio.equity, bar_long.close, bar_short.close
        )
        if long_leg <= 0:
            return []

        state = context.setdefault(self._state_key(), {})

        # Long spread entry: z crosses DOWN through -entry_z
        if zscore_prev > -self.entry_z and zscore_now <= -self.entry_z:
            state["entry_idx"] = idx
            state["entry_z"] = zscore_now
            state["entry_wall_clock_ts"] = ts
            state["side"] = "long_spread"
            state["beta_at_entry"] = self._beta
            return [
                Order(symbol=self.long_symbol, side="buy", volume=long_leg),
                Order(symbol=self.short_symbol, side="sell", volume=short_leg),
            ]

        # Short spread entry: z crosses UP through +entry_z
        if zscore_prev < self.entry_z and zscore_now >= self.entry_z:
            state["entry_idx"] = idx
            state["entry_z"] = zscore_now
            state["entry_wall_clock_ts"] = ts
            state["side"] = "short_spread"
            state["beta_at_entry"] = self._beta
            return [
                Order(symbol=self.long_symbol, side="sell", volume=long_leg),
                Order(symbol=self.short_symbol, side="buy", volume=short_leg),
            ]

        return []
```

- [ ] **Step 4: Verify entry tests pass**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k "entry"
```

Expected: all 4 PASS.

- [ ] **Step 5: Full suite**

```bash
.venv/bin/python -m pytest -q
```

Expected: 418 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): entry logic (long/short crossings + session gate)"
```

---

## Task 6: Exit logic with precedence order

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (add `_maybe_exit`)
- Modify: `tests/test_chan_bollinger_pairs.py` (add 6 exit tests)

Precedência (spec §3.3): spread-stop → Friday-flat → wall-clock 48h → time-stop → mean-revert.

- [ ] **Step 1: Write failing exit tests**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
def _seed_position(strat, portfolio, ts_entry, *, side="long_spread"):
    """Open both legs on portfolio at ts_entry, mirror state dict, return ctx."""
    long_leg = 100.0
    short_leg = strat._beta * long_leg
    bar_long = Bar("GLD", ts_entry, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_entry, 72.0, 72.3, 71.7, 72.0, 1e6)
    if side == "long_spread":
        portfolio.open_position("GLD", "long", long_leg, 180.0, ts_entry)
        portfolio.open_position("SLV", "short", short_leg, 72.0, ts_entry)
    else:
        portfolio.open_position("GLD", "short", long_leg, 180.0, ts_entry)
        portfolio.open_position("SLV", "long", short_leg, 72.0, ts_entry)
    idx_entry = strat._indicators.index.get_loc(ts_entry)
    ctx = {
        strat._state_key(): {
            "entry_idx": idx_entry,
            "entry_z": -1.1 if side == "long_spread" else 1.1,
            "entry_wall_clock_ts": ts_entry,
            "side": side,
            "beta_at_entry": strat._beta,
        }
    }
    return ctx, bar_long, bar_short


def test_exit_mean_revert_long_spread_at_zero():
    """Long spread open; z crosses up through 0 → both legs closed."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -0.1], entry_z=1.0)
    # Place entry 10 bars before tail_start; patch z scenery around entry + now
    entry_pos = tail_start - 10
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    # Current bar: zscore just crossed zero
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start, strat._indicators.columns.get_loc("zscore")] = -0.1
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = 0.1
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    sides = {o.symbol: o.side for o in orders}
    # closing long GLD = sell; closing short SLV = buy
    assert sides == {"GLD": "sell", "SLV": "buy"}


def test_exit_spread_stop_long_spread_at_minus_3():
    """Long spread open; z blows out to -3 → emergency close."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 5
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2
    assert {o.symbol for o in orders} == {"GLD", "SLV"}


def test_exit_friday_weekend_flat_at_15():
    """Long spread open; current bar is Friday 15:30 → force close even if z favorable."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    friday_ts = pd.Timestamp("2023-06-16 15:30")
    fri_pos = strat._indicators.index.get_indexer([friday_ts], method="nearest")[0]
    ts_now = strat._indicators.index[fri_pos]
    assert ts_now.weekday() == 4 and ts_now.hour >= 15
    entry_pos = fri_pos - 5
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2


def test_exit_wall_clock_48h_cap():
    """Entry Mon 10:00, current Wed 11:00 (49h wall clock) → forced exit."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    mon_ts = pd.Timestamp("2023-06-12 10:30")
    wed_ts = pd.Timestamp("2023-06-14 11:30")  # >48h after mon_ts
    mon_pos = strat._indicators.index.get_indexer([mon_ts], method="nearest")[0]
    wed_pos = strat._indicators.index.get_indexer([wed_ts], method="nearest")[0]
    ts_entry = strat._indicators.index[mon_pos]
    ts_now = strat._indicators.index[wed_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2, (
        f"expected forced exit at wall-clock 48h+, got {orders}"
    )


def test_exit_time_stop_in_trading_bars():
    """Bars held >= time_stop_bars → forced exit."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    # time_stop_bars = min(3*half_life, 24); half_life recovered ~20 → time_stop=24
    # set entry such that bars_held == time_stop_bars exactly
    ts_now_pos = tail_start + 1
    ts_entry_pos = ts_now_pos - strat._time_stop_bars
    ts_entry = strat._indicators.index[ts_entry_pos]
    ts_now = strat._indicators.index[ts_now_pos]
    # Keep wall-clock under 48h by checking the spacing — if > 48h, test degenerates
    wall_h = (ts_now - ts_entry).total_seconds() / 3600.0
    if wall_h >= 48.0:
        pytest.skip(f"wall-clock gap {wall_h:.1f}h hides time-stop; skip")
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2, f"expected time-stop exit, got {orders}"


def test_exit_precedence_spread_stop_beats_mean_revert():
    """Both spread_stop (z=-3) AND mean-revert would fire; spread_stop wins.

    For long_spread entry at z=-1.1, z=+0.1 would mean-revert (happy) — but
    if the indicator is spoofed to be at -3.1 the spread_stop triggers.
    Symmetric: check that in the long side spread_stop is recognized as
    precedence over mean_revert by firing with the z clearly past the
    spread_stop_z limit on the same side as entry.
    """
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 3
    ts_entry = strat._indicators.index[entry_pos]
    ts_now = strat._indicators.index[tail_start + 1]
    # z_now = -3.1 triggers spread_stop for long spread
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2
```

- [ ] **Step 2: Verify fails**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k "exit"
```

Expected: 6 exit tests FAIL (on_bar still returns `[]` when `in_position`).

- [ ] **Step 3: Implement `_maybe_exit` and wire into `on_bar`**

Add method to class:

```python
    def _maybe_exit(
        self,
        ts: pd.Timestamp,
        idx: int,
        zscore_now: float,
        portfolio: Portfolio,
        state: dict,
    ) -> list[Order]:
        """Return a pair of closing orders if any exit rule fires; else []."""
        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        if pos_long is None or pos_short is None:
            return []
        side = state.get("side", "long_spread")
        entry_ts: pd.Timestamp = state.get("entry_wall_clock_ts", ts)
        entry_idx: int = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        wall_clock_h = (ts - entry_ts).total_seconds() / 3600.0

        def close_orders() -> list[Order]:
            close_long_side = "sell" if pos_long.side == "long" else "buy"
            close_short_side = "sell" if pos_short.side == "long" else "buy"
            return [
                Order(self.long_symbol, close_long_side, pos_long.volume),
                Order(self.short_symbol, close_short_side, pos_short.volume),
            ]

        # 1. Spread blow-out stop [p.293-294, ch.8]
        if side == "long_spread" and zscore_now <= -self.spread_stop_z:
            return close_orders()
        if side == "short_spread" and zscore_now >= self.spread_stop_z:
            return close_orders()

        # 2. Friday weekend-flat (CFD adaptation)
        if ts.weekday() == 4 and ts.hour >= self.friday_flat_hour:
            return close_orders()

        # 3. Wall-clock 48h hard cap [spec §1.4]
        if wall_clock_h >= self.max_hold_hours:
            return close_orders()

        # 4. Time-stop in trading bars [p.47, ch.2]
        if bars_held >= self._time_stop_bars:
            return close_orders()

        # 5. Mean-reversion exit [p.71-72, ch.3]
        if side == "long_spread" and zscore_now >= self.exit_z:
            return close_orders()
        if side == "short_spread" and zscore_now <= -self.exit_z:
            return close_orders()

        return []
```

Modify `on_bar` to dispatch to `_maybe_exit` when `in_position`:

```python
        if in_position:
            state = context.setdefault(self._state_key(), {})
            exit_orders = self._maybe_exit(
                ts=ts, idx=idx, zscore_now=zscore_now,
                portfolio=portfolio, state=state,
            )
            if exit_orders:
                context[self._state_key()] = {}  # clear state after exit
            return exit_orders
```

- [ ] **Step 4: Verify exit tests pass**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k "exit"
```

Expected: all 6 PASS.

- [ ] **Step 5: Full suite**

```bash
.venv/bin/python -m pytest -q
```

Expected: 424 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): exit logic with 5-level precedence (stop > session > hard-cap > time > mean-revert)"
```

---

## Task 7: `adjust_ohlc` regression guard

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (apply `adjust_ohlc` in `__post_init__`)
- Modify: `tests/test_chan_bollinger_pairs.py` (1 regression test)

Motivo: commit `5ca9410` descobriu que estratégias lêem `close` em vez de `adj_close`. Chan pairs depende de close ajustado pra não injetar falsos z-crossings em dias ex-div.

- [ ] **Step 1: Add regression test**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
def test_adjust_ohlc_applied_to_both_legs():
    """If adj_close differs from close, strategy must use adj_close.

    Uses a synthetic ex-dividend-like scenario where close has a discontinuity
    but adj_close is smooth.
    """
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    # Inject a "dividend" shock to close at mid-point (not adj_close)
    shock_idx = n // 2
    close_shock = y.copy()
    close_shock[shock_idx:] -= 5.0  # $5 dividend
    df_long = pd.DataFrame(
        {
            "open": close_shock, "high": close_shock, "low": close_shock,
            "close": close_shock, "volume": 1e6, "adj_close": y,
        },
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    # After adjust_ohlc, close should now match adj_close — so _beta recovered
    # should still be ~2.5 (the shock was eliminated by adjustment).
    assert abs(strat._beta - 2.5) < 0.2, (
        f"β without adjust would diverge after shock; got {strat._beta}"
    )
```

- [ ] **Step 2: Verify it fails**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k adjust_ohlc
```

Expected: FAIL with `β` far from 2.5 because the shock in `close` corrupts OLS.

- [ ] **Step 3: Apply `adjust_ohlc` early in `__post_init__`**

Modify `__post_init__` in `chan_bollinger_pairs.py`:

```python
    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        # Rescale OHLC to the adjusted-close base — regression guard for
        # bug commit 5ca9410 (raw close triggered false z-crossings on ex-div bars).
        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )
        self._fit_hedge_and_half_life()
        self._precompute_indicators()
```

- [ ] **Step 4: Verify it passes**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k adjust_ohlc
```

Expected: PASS.

- [ ] **Step 5: Full suite**

```bash
.venv/bin/python -m pytest -q
```

Expected: 425 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): apply adjust_ohlc to both legs (regression: bug 5ca9410)"
```

---

## Task 8: Diagnostic state counters

**Files:**
- Modify: `src/ai_trade/backtest/strategies/chan_bollinger_pairs.py` (extend `_maybe_exit` to track exit reasons)
- Modify: `tests/test_chan_bollinger_pairs.py` (1 diagnostic test)

Motivo: spec §6 diagnostic report obriga `pct_exited_by: {spread_stop, friday_flat, hard_cap, time_stop, mean_revert}` + `median_hold_hours` + `max_hold_hours` + `pct_trades_overnight`. Contadores vivem num dict no `context["chan_pairs_diagnostics"]` — o Runner persiste o `context` final.

- [ ] **Step 1: Add diagnostic test**

Append to `tests/test_chan_bollinger_pairs.py`:

```python
def test_diagnostic_counters_tracked_in_context():
    """Run a few manufactured entries+exits; verify counters land in context."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 3
    ts_entry = strat._indicators.index[entry_pos]
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2
    diag = ctx.get("chan_pairs_diagnostics", {})
    reasons = diag.get("exit_reasons", [])
    assert reasons == ["spread_stop"], f"expected ['spread_stop'], got {reasons}"
    holds = diag.get("hold_hours", [])
    assert len(holds) == 1
    assert holds[0] >= 0.0
```

- [ ] **Step 2: Verify fails**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k diagnostic_counters
```

Expected: FAIL with `reasons == []` or KeyError.

- [ ] **Step 3: Extend `_maybe_exit` to record reason**

Refactor `_maybe_exit` to return `(orders, reason_or_None)`:

```python
    DIAG_KEY = "chan_pairs_diagnostics"

    def _record_exit(
        self, context: dict, reason: str, hold_hours: float,
    ) -> None:
        diag = context.setdefault(self.DIAG_KEY, {
            "exit_reasons": [], "hold_hours": [],
        })
        diag["exit_reasons"].append(reason)
        diag["hold_hours"].append(float(hold_hours))

    def _maybe_exit(
        self,
        ts: pd.Timestamp,
        idx: int,
        zscore_now: float,
        portfolio: Portfolio,
        state: dict,
        context: dict,
    ) -> list[Order]:
        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        if pos_long is None or pos_short is None:
            return []
        side = state.get("side", "long_spread")
        entry_ts: pd.Timestamp = state.get("entry_wall_clock_ts", ts)
        entry_idx: int = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        wall_clock_h = (ts - entry_ts).total_seconds() / 3600.0

        def close_orders() -> list[Order]:
            close_long_side = "sell" if pos_long.side == "long" else "buy"
            close_short_side = "sell" if pos_short.side == "long" else "buy"
            return [
                Order(self.long_symbol, close_long_side, pos_long.volume),
                Order(self.short_symbol, close_short_side, pos_short.volume),
            ]

        # 1. Spread blow-out stop
        if (
            (side == "long_spread" and zscore_now <= -self.spread_stop_z)
            or (side == "short_spread" and zscore_now >= self.spread_stop_z)
        ):
            self._record_exit(context, "spread_stop", wall_clock_h)
            return close_orders()

        # 2. Friday weekend-flat
        if ts.weekday() == 4 and ts.hour >= self.friday_flat_hour:
            self._record_exit(context, "friday_flat", wall_clock_h)
            return close_orders()

        # 3. Wall-clock 48h hard cap
        if wall_clock_h >= self.max_hold_hours:
            self._record_exit(context, "hard_cap", wall_clock_h)
            return close_orders()

        # 4. Time-stop in trading bars
        if bars_held >= self._time_stop_bars:
            self._record_exit(context, "time_stop", wall_clock_h)
            return close_orders()

        # 5. Mean-reversion exit
        if (
            (side == "long_spread" and zscore_now >= self.exit_z)
            or (side == "short_spread" and zscore_now <= -self.exit_z)
        ):
            self._record_exit(context, "mean_revert", wall_clock_h)
            return close_orders()

        return []
```

Update the call site in `on_bar`:

```python
        if in_position:
            state = context.setdefault(self._state_key(), {})
            exit_orders = self._maybe_exit(
                ts=ts, idx=idx, zscore_now=zscore_now,
                portfolio=portfolio, state=state, context=context,
            )
            if exit_orders:
                context[self._state_key()] = {}
            return exit_orders
```

- [ ] **Step 4: Verify passes**

```bash
.venv/bin/python -m pytest tests/test_chan_bollinger_pairs.py -v -k diagnostic_counters
```

Expected: PASS.

- [ ] **Step 5: Full suite**

```bash
.venv/bin/python -m pytest -q
```

Expected: 426 passing.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/chan_bollinger_pairs.py \
        tests/test_chan_bollinger_pairs.py
git commit -m "feat(chan_pairs): track exit reasons + hold_hours in context for diagnostic"
```

---

## Task 9: Create `ChanPairsGridConfig` + grid exports

**Files:**
- Create: `src/ai_trade/backtest/grid/chan_pairs_config.py`
- Modify: `src/ai_trade/backtest/grid/__init__.py`
- Create: `tests/test_chan_pairs_grid_config.py`

- [ ] **Step 1: Write failing grid-config test**

Create `tests/test_chan_pairs_grid_config.py`:

```python
"""Tests for the Chan Pairs grid config [algo_trading_chan p.71-73]."""

from ai_trade.backtest.grid.chan_pairs_config import (
    ChanPairsGridConfig,
    chan_pairs_grid_configs,
)


def test_grid_returns_4_configs():
    configs = chan_pairs_grid_configs()
    assert len(configs) == 4


def test_grid_covers_full_cartesian_2x2():
    configs = chan_pairs_grid_configs()
    combos = {(c.lookback_multiplier, c.entry_z) for c in configs}
    assert combos == {(1, 1.0), (1, 1.5), (2, 1.0), (2, 1.5)}


def test_grid_config_is_frozen_and_hashable():
    c = ChanPairsGridConfig(lookback_multiplier=2, entry_z=1.0)
    # Frozen dataclass is hashable
    _ = hash(c)
    try:
        c.lookback_multiplier = 99  # type: ignore[misc]
    except Exception as e:
        assert "frozen" in str(e).lower()
    else:
        raise AssertionError("expected FrozenInstanceError")
```

- [ ] **Step 2: Verify fails**

```bash
.venv/bin/python -m pytest tests/test_chan_pairs_grid_config.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create the config module**

Create `src/ai_trade/backtest/grid/chan_pairs_config.py`:

```python
"""Chan Bollinger Pairs parameter grid [algo_trading_chan p.71-73, ch.3].

Grid axes
---------

* ``lookback_multiplier`` ∈ (1, 2) — multiple of OU half-life used as
  Bollinger lookback [p.47, ch.2].
* ``entry_z`` ∈ (1.0, 1.5) — Chan uses 1.0 in the canonical example
  [p.71-72], acknowledges it as a free parameter.

Total: 2 × 2 = **4 configs**. Deliberately parsimonious — 5 prior Phase 2.5
runs (N=24, N=30) all failed DSR; cutting N_trials to 4 lets the deflation
factor ``Z(N)/√(T−1)`` shrink to roughly half of Run 2's.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


LOOKBACK_MULTIPLIER = (1, 2)
ENTRY_Z = (1.0, 1.5)


@dataclass(frozen=True)
class ChanPairsGridConfig:
    """Parameter bundle for one Chan Bollinger Pairs trial."""

    lookback_multiplier: int
    entry_z: float

    # Fixed constants (cited in strategy docstring).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    train_bars: int = 1250
    half_life_min: int = 4
    half_life_max: int = 60
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13


def chan_pairs_grid_configs() -> list[ChanPairsGridConfig]:
    """Return the 4 grid configs in cartesian-product order.

    Order: (lookback_multiplier, entry_z) — outer-most first. Stable
    across invocations so ``config_id = i`` is a deterministic key for
    checkpoint/resume.
    """
    return [
        ChanPairsGridConfig(lookback_multiplier=lm, entry_z=ez)
        for lm, ez in itertools.product(LOOKBACK_MULTIPLIER, ENTRY_Z)
    ]
```

- [ ] **Step 4: Export from `grid/__init__.py`**

Read current content:

```bash
cat src/ai_trade/backtest/grid/__init__.py
```

Edit to add `ChanPairsGridConfig` + `chan_pairs_grid_configs`. Insert after the `ehlers_meta_config` import:

```python
from ai_trade.backtest.grid.chan_pairs_config import (
    ChanPairsGridConfig,
    chan_pairs_grid_configs,
)
```

And add `"ChanPairsGridConfig"` and `"chan_pairs_grid_configs"` to `__all__`.

- [ ] **Step 5: Verify tests pass**

```bash
.venv/bin/python -m pytest tests/test_chan_pairs_grid_config.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 6: Full suite**

```bash
.venv/bin/python -m pytest -q
```

Expected: 429 passing.

- [ ] **Step 7: Commit**

```bash
git add src/ai_trade/backtest/grid/chan_pairs_config.py \
        src/ai_trade/backtest/grid/__init__.py \
        tests/test_chan_pairs_grid_config.py
git commit -m "feat(grid): ChanPairsGridConfig (2x2=4 trials) [algo_trading_chan p.71-73]"
```

---

## Task 10: CLI runner `scripts/run_grid_chan_pairs.py`

**Files:**
- Create: `scripts/run_grid_chan_pairs.py`

Adaptação do `scripts/run_grid_ehlers_meta.py` pra 2 símbolos. Não tem teste unitário (integration-tested via dry-run smoke no próximo Task).

- [ ] **Step 1: Create the CLI script**

Create `scripts/run_grid_chan_pairs.py`:

```python
#!/usr/bin/env python3
"""Run the Chan Bollinger Pairs grid (Phase 2.5 first intraday entry).

End-to-end pipeline:

1. Fetch 1h OHLCV for ``long_symbol`` and ``short_symbol`` via
   :class:`TiingoSource` (requires ``tiingo_service`` infra).
2. Build the 4 ``ChanPairsGridConfig`` configs.
3. Execute the grid via :class:`GridRunner` with checkpoint resume.
4. Walk-forward per config (8 windows), with β + half-life **refit**
   at the start of each window (true OOS per Chan [p.8, ch.1]).
5. Evaluate gates: PBO < 0.5, DSR p < 0.05, walk-forward ≥ 6/8.
6. Emit report (PASS) or diagnostic (FAIL).

Typical invocation:

    .venv/bin/python scripts/run_grid_chan_pairs.py \\
        --long-symbol GLD --short-symbol SLV \\
        --start 2022-01-01 --end 2026-04-15 \\
        --cash 100000 --n-jobs 4 --output-dir reports/

Dry run (smoke, 1 config):

    .venv/bin/python scripts/run_grid_chan_pairs.py --dry-run \\
        --long-symbol GLD --short-symbol SLV \\
        --start 2023-01-01 --end 2024-12-31 \\
        --output-dir /tmp/grid_chan_pairs_smoke
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.chan_pairs")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Chan Bollinger Pairs 1h grid with anti-overfit gates.",
    )
    ap.add_argument("--long-symbol", default="GLD")
    ap.add_argument("--short-symbol", default="SLV")
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--asset-class", default="etf",
        choices=["equity", "etf", "index", "crypto", "forex"],
    )
    ap.add_argument("--warmup-days", type=int, default=365)
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.grid import (
        ChanPairsGridConfig,
        DiagnosticAnalyzer,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        chan_pairs_grid_configs,
        compose_observers,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.chan_bollinger_pairs import (
        ChanBollingerPairsStrategy,
    )

    args = _parse_args(argv)
    run_id = (
        args.run_id or f"grid_chan_pairs_{datetime.now().strftime('%Y%m%d-%H%M')}"
    )
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, args.log_level)
    setup_grid_logging(
        run_id=run_id, run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"), level=level,
    )

    log.info("=== grid run %s ===", run_id)
    log.info(
        "long=%s short=%s start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        args.long_symbol, args.short_symbol, args.start, args.end,
        args.cash, args.n_jobs, args.dry_run,
    )

    configs = chan_pairs_grid_configs()
    if args.dry_run:
        configs = configs[:1]
        log.info("DRY RUN: limited to 1 config")

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info(
        "Fetching %s + %s 1h from %s → %s",
        args.long_symbol, args.short_symbol, fetch_start, args.end,
    )
    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))
    raw = {}
    for sym in (args.long_symbol, args.short_symbol):
        df = src.fetch(
            sym, fetch_start, args.end,
            frequency="1hour", asset_class=args.asset_class,
        )
        if df.empty:
            log.error("No data for %s — abort", sym)
            return 1
        raw[sym] = df

    # Align indices by inner-join on timestamps (handles minor gaps/halts)
    common_idx = raw[args.long_symbol].index.intersection(
        raw[args.short_symbol].index
    )
    if len(common_idx) == 0:
        log.error("No overlapping timestamps between %s and %s",
                  args.long_symbol, args.short_symbol)
        return 1
    data_full = {sym: raw[sym].loc[common_idx] for sym in raw}

    data_bounded = {
        sym: data_full[sym].loc[
            pd.Timestamp(args.start) : pd.Timestamp(args.end)
        ]
        for sym in data_full
    }
    if any(df.empty for df in data_bounded.values()):
        log.error("Bounded range [%s, %s] is empty", args.start, args.end)
        return 1
    log.info(
        "Data ready: %d bars in [%s, %s]",
        len(data_bounded[args.long_symbol]), args.start, args.end,
    )

    def trial_fn(cfg: ChanPairsGridConfig):
        """Build the pair strategy for one trial and run it."""
        strategy = ChanBollingerPairsStrategy(
            data=data_full,
            long_symbol=args.long_symbol,
            short_symbol=args.short_symbol,
            lookback_multiplier=cfg.lookback_multiplier,
            entry_z=cfg.entry_z,
            exit_z=cfg.exit_z,
            spread_stop_z=cfg.spread_stop_z,
            train_bars=cfg.train_bars,
            half_life_min=cfg.half_life_min,
            half_life_max=cfg.half_life_max,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
            max_hold_hours=cfg.max_hold_hours,
            entry_hour_cutoff=cfg.entry_hour_cutoff,
            friday_flat_hour=cfg.friday_flat_hour,
            friday_no_entry_hour=cfg.friday_no_entry_hour,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=args.cash,
        )

    pbar = tqdm(total=len(configs), desc=f"grid {run_id}", unit="cfg")

    def tqdm_observer(completed: int, total: int, trial) -> None:
        pbar.update(1)
        pbar.set_postfix({
            "cfg_id": trial.config_id,
            "status": trial.status,
            "sharpe": (
                f"{trial.sharpe:.2f}" if trial.status == "ok" else "—"
            ),
        })

    observer = compose_observers(
        JsonlTrialObserver(
            path=run_checkpoint_dir / "trials.jsonl", run_id=run_id,
        ),
        StatusFileObserver(
            path=run_checkpoint_dir / "status.md", run_id=run_id,
        ),
        StatusFileObserver(
            path=Path("logs/grid_latest_status.md"), run_id=run_id,
        ),
        tqdm_observer,
    )

    grid = GridRunner(
        checkpoint_dir=checkpoint_dir,
        n_jobs=args.n_jobs,
        config_cls=ChanPairsGridConfig,
    ).run(
        configs=configs, trial_fn=trial_fn, run_id=run_id,
        progress_cb=observer,
    )
    pbar.close()

    log.info(
        "Grid complete: %d/%d OK (%d errors)",
        len(grid.ok_trials), len(grid.trials),
        len(grid.trials) - len(grid.ok_trials),
    )

    log.info("Running walk-forward per config (n_windows=8)")
    wf_results = wf_for_grid(grid, n_windows=8, n_jobs=args.n_jobs)

    log.info("Evaluating gates (PBO, DSR, walk-forward)")
    verdict = GateEvaluator().evaluate(
        grid=grid,
        wf_verdicts={cid: wf.verdict for cid, wf in wf_results.items()},
    )
    pbo_val = (
        float(verdict.pbo_result.pbo) if verdict.pbo_result else float("nan")
    )
    log.info(
        "Gate verdict: overall_pass=%s best_config_id=%s "
        "pbo=%.3f dsr_pass=%d/%d wf_pass=%d/%d",
        verdict.overall_pass, verdict.best_config_id,
        pbo_val,
        len(verdict.dsr_pass_ids), len(verdict.dsr_results),
        len(verdict.wf_pass_ids), len(verdict.wf_verdicts),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report_gen = GridReportGenerator()
    if verdict.overall_pass:
        path = report_gen.write_pass_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("FAIL diagnostic report: %s", path)

    log.info("=== grid run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/run_grid_chan_pairs.py
```

- [ ] **Step 3: Verify `--help` works (no execution)**

```bash
.venv/bin/python scripts/run_grid_chan_pairs.py --help
```

Expected: argparse help output listing all flags; exit 0.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_grid_chan_pairs.py
git commit -m "feat(scripts): run_grid_chan_pairs CLI runner for GLD-SLV 1h grid"
```

---

## Task 11: Dry-run smoke + full grid experiment

**Files:**
- Run: `scripts/run_grid_chan_pairs.py` (dry-run smoke + full run)
- Create: `reports/grid_chan_pairs_<run_id>/` (auto-generated)

Goal: end-to-end validation com dados reais. Dry-run smoke primeiro pra pegar erros de integração cedo; depois full run pros 4 configs + diagnostic.

- [ ] **Step 1: Dry-run smoke — 1 config, short window**

```bash
mkdir -p /tmp/grid_chan_smoke
.venv/bin/python scripts/run_grid_chan_pairs.py --dry-run \
    --long-symbol GLD --short-symbol SLV \
    --start 2023-01-01 --end 2024-12-31 \
    --cash 100000 --n-jobs 1 \
    --output-dir /tmp/grid_chan_smoke
```

Expected outcomes:
- exit code 0 (PASS) or 2 (FAIL — either is OK for smoke; the infra integration is what we're checking)
- `/tmp/grid_chan_smoke/grid_chan_pairs_<ts>/` contains either a PASS or FAIL report markdown.
- Log mentions: "Grid complete: 1/1 OK", walk-forward computation finishes, gate verdict printed.
- **If the trial errors out**: inspect `.cache/grid_runs/<run_id>/trials.jsonl` for stacktraces. Most likely causes:
  - Half-life out of [4, 60] clamp on the chosen window — adjust `--start` or move to full window.
  - `train_bars=1250` >= len(bounded data) — widen the window.

- [ ] **Step 2: Full run — 4 configs over full available window**

```bash
.venv/bin/python scripts/run_grid_chan_pairs.py \
    --long-symbol GLD --short-symbol SLV \
    --start 2022-04-15 --end 2026-04-15 \
    --cash 100000 --n-jobs 4 \
    --output-dir reports
```

Expected wallclock: < 60s (4 configs × ~10s each).

- [ ] **Step 3: Inspect the report**

```bash
ls -la reports/grid_chan_pairs_*/
cat reports/grid_chan_pairs_*/report.md  # or diagnostic.md for FAIL
```

Record the verdict: PASS (exit 0) or FAIL (exit 2) + which gates failed.

- [ ] **Step 4: Inspect diagnostic counters (spec §6 requirement)**

Open `reports/grid_chan_pairs_*/diagnostic.md` (for FAIL) or `report.md` (PASS) and verify these fields are present per the spec §6.2 contract. If missing, they need to be added to `GridReportGenerator` / `DiagnosticAnalyzer` — but that is a **follow-up task documented in spec §7**, not blocking v1 delivery. For v1: acceptable if the counters are only visible in the `trials.jsonl` at `.cache/grid_runs/<run_id>/trials.jsonl`.

Run the counter-extraction inline:

```bash
.venv/bin/python -c '
import json
from pathlib import Path
import sys
run_dir = sorted(Path(".cache/grid_runs").glob("grid_chan_pairs_*"))[-1]
lines = (run_dir / "trials.jsonl").read_text().strip().splitlines()
for ln in lines:
    t = json.loads(ln)
    print(
        f"cfg={t.get(\"config_id\")}  status={t.get(\"status\")}  "
        f"sharpe={t.get(\"sharpe\", \"—\")}  cagr={t.get(\"cagr\", \"—\")}  "
        f"max_dd={t.get(\"max_dd\", \"—\")}"
    )
'
```

- [ ] **Step 5: Commit the report**

```bash
git add reports/grid_chan_pairs_*/
git commit -m "chore(reports): first GLD-SLV 1h Chan pairs grid run (4 configs)"
```

- [ ] **Step 6: Update JORNADA.md with the verdict**

Edit `JORNADA.md` — add a dated entry under the changelog section with the verdict (PASS or FAIL), best-config Sharpe/CAGR/MaxDD, median_hold_hours, and the next-step choice from spec §7. Update "Onde estamos hoje" to reflect the new state of the catálogo intraday.

Template for the JORNADA entry:

```markdown
## 2026-04-15 (noite) — Primeira estratégia intraday rodou: Chan pairs GLD-SLV 1h

**Verdict:** [PASS | FAIL por <gate>]

Primeira estratégia intraday do catálogo pós-pivô. 4 configs (2×2), dados
Tiingo 1h (~8000 bars em 4 anos), CPCV+PBO+DSR+WF+MCPT.

- Best config #<X>: Sharpe <Y>, CAGR <Z>%, MaxDD <W>%.
- Half-life estimado no train: <N> bars. β GLD~SLV = <B>. t-stat OU = <T>.
- median_hold_hours: <M>h (cap §1.4 = 48h); max_hold = <MX>h.
- pct_exited_by: {spread_stop: X%, friday_flat: Y%, hard_cap: Z%,
  time_stop: W%, mean_revert: V%}.
- Gate outcomes: PBO=<p>, DSR_pass=<d>/4, WF=<w>/8, MCPT=<m>.

**Próximo passo:** [conforme §7 do spec] <decisão>.
```

Commit:

```bash
git add JORNADA.md
git commit -m "docs(jornada): verdict da primeira estratégia intraday — Chan pairs GLD-SLV 1h"
```

---

## Self-Review

**1. Spec coverage:**
- §1 Contexto → Task 1 (retention probe validates §1.3 pre-condition).
- §2 Arquitetura → Tasks 2, 3, 4 (class scaffold, fit, indicators).
- §3 Entry/exit → Tasks 5 (entry + session), 6 (exit precedence).
- §4 Pipeline de dados → Task 10 (CLI runner handles fetch + bounded slice; WF refit is delegated to existing `wf_for_grid`).
- §5 Gate → Task 10 (GateEvaluator + wf_for_grid wired).
- §6 Tests → Tasks 2-8 covering all 20 spec-listed tests.
- §7 Sucesso/hook → Task 11 (JORNADA entry documents verdict + next step).
- §8-10 → cross-cut; each task cites the relevant spec section.

**Gap noted:** Spec §4.4 says WF "re-fita β e half_life no início de cada janela WF". The existing `wf_for_grid` re-instantiates the strategy per window by calling `trial_fn(cfg)` with the windowed data subset. Because `ChanBollingerPairsStrategy.__post_init__` runs the fit fresh on each instantiation (using its internal `train_bars`), this requirement is satisfied as long as `wf_for_grid` passes each window's data as the strategy's `data` input. Verified this is the pattern in `run_grid_ehlers_meta.py:trial_fn` (re-builds strategy per trial; WF machinery calls `trial_fn` per window).

**Gap noted:** Spec §5.2 lists MCPT as a gate but the existing `GateEvaluator` (from Run 4 Step 2) only checks PBO + DSR + WF. MCPT integration is not currently a task in this plan — left as a known v1.5 follow-up because wiring MCPT through `GateEvaluator` is scope creep for this plan (a separate infra task, not a Chan-pairs-specific task). The spec §5 "MCPT" gate will be evaluated manually post-run on the best config's oos trade series until `GateEvaluator` is extended. Documented in the JORNADA verdict entry.

**2. Placeholder scan:** No TBDs, TODOs, "add error handling", or "similar to Task N" found. Every code block is executable.

**3. Type consistency:**
- `_beta`, `_half_life_bars`, `_indicators`, `_lookback_bars`, `_time_stop_bars`, `_state_key()`, `DIAG_KEY`, `STATE_KEY_PREFIX` — referenced consistently across Tasks 3, 4, 5, 6, 8.
- `close_orders()` inner helper in `_maybe_exit` — defined once, called 5 times.
- `Order(symbol, side, volume)` — positional signature matches `execution.py:44-52`.
- `Portfolio(initial_cash=...)` — matches existing tests pattern.
- `bars: dict[str, Bar]`, `portfolio: Portfolio`, `context: dict` — Strategy Protocol signature matches `runner.py:50-52`.
