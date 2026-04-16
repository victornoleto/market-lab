# Volatility Expansion Breakout 1h — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver `VolExpansionBreakoutStrategy` — a Donchian channel breakout filtered by Yang-Zhang volatility cone (Sinclair `[volatility_trading, p.20-23, p.58-60]`), sized via Carver vol-targeting Half-Kelly (`[systematic_trading, p.144, p.159, ch.9-10]`), with 3 exit conditions (opposite channel, 48h hard cap, 4σ disaster stop) — running end-to-end as the 2nd entry in the post-pivot 1h intraday catalog.

**Architecture:** Package folder `src/ai_trade/backtest/strategies/vol_expansion_breakout/` with private sub-modules per spec §2.1 (`_regime_filter.py`, `_breakout_signal.py`, `_vol_target_sizer.py`, `_exit_manager.py`) plus orchestrator `_strategy.py`. Public API via `__init__.py` exports `VolExpansionBreakoutStrategy`. Per-symbol state in `context` dict (analogous to `chan_bollinger_pairs.py`). Multi-asset via `data: dict[str, pd.DataFrame]` keyed by ticker. Grid config `VolExpansionGridConfig` (4 trials), CLI `scripts/run_grid_vol_expansion.py` (multi-asset orchestration). Bundle β (SPY + XAU/USD + EUR/USD) primary; Bundle α (SPY + GLD + EURUSD) automatic fallback if FX retention < 3y.

**Tech Stack:** Python 3.12, pandas, numpy, pytest, existing `backtest/engine/`, `backtest/grid/`, `backtest/validation/`, `backtest/data/tiingo_source.py`. No new runtime deps.

**Spec:** `docs/superpowers/specs/2026-04-15-vol-expansion-breakout-1h-design.md` (commit `2591fab`).

**Spec note resolved during planning:** spec §2.1 listed both `vol_expansion_breakout.py` (file) and `vol_expansion_breakout/` (folder) — Python can't have both. **Plan uses folder pattern** with `__init__.py` exposing the strategy class. Private sub-modules with `_` prefix. Spec intent of component decomposition preserved.

---

## File Structure

**Create:**
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py` — exports `VolExpansionBreakoutStrategy`, `RegimeReading`.
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py` — `YangZhangCone` + `RegimeReading` dataclass.
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/_breakout_signal.py` — `DonchianBreakout`.
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/_vol_target_sizer.py` — `VolTargetSizer`.
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/_exit_manager.py` — `ExitManager` + `ExitReason` enum.
- `src/ai_trade/backtest/strategies/vol_expansion_breakout/_strategy.py` — `VolExpansionBreakoutStrategy` orchestrator.
- `src/ai_trade/backtest/grid/vol_expansion_config.py` — `VolExpansionGridConfig` + `vol_expansion_grid_configs()`.
- `scripts/run_grid_vol_expansion.py` — CLI runner.
- `tests/test_vol_expansion_regime_filter.py` (~8 tests).
- `tests/test_vol_expansion_breakout_signal.py` (~5 tests).
- `tests/test_vol_expansion_sizer.py` (~5 tests).
- `tests/test_vol_expansion_exit_manager.py` (~6 tests).
- `tests/test_vol_expansion_strategy_integration.py` (~3 tests).

**Modify:**
- `src/ai_trade/backtest/strategies/__init__.py` — re-export `VolExpansionBreakoutStrategy`.
- `src/ai_trade/backtest/grid/__init__.py` — re-export `VolExpansionGridConfig` + factory.

**Smoke-test only (no committed code):**
- Tiingo retention probe on `XAU/USD` and `EURUSD` 1h in Task 1 (pre-flight). Records result in `reports/vol_expansion_fx_retention_probe.md`.

---

## Task 1: Pre-flight smoke — Tiingo FX 1h retention probe

**Files:**
- Smoke script: ephemeral inline (`.venv/bin/python -c '...'`).
- Create: `reports/vol_expansion_fx_retention_probe.md` (auditable record).

**Rationale:** Spec §1.3 + §4.4 require ≥ 3y retention on `XAU/USD` and `EURUSD` for Bundle β. If either < 3y, automatic fallback Bundle α (XAU→GLD). If `EURUSD` < 3y, **abort and escalate** — premissa multi-asset não sobrevive.

- [ ] **Step 1: Probe XAU/USD and EURUSD 1h retention**

```bash
.venv/bin/python -c '
from datetime import date
from pathlib import Path
from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
end = date(2026, 4, 15)
start = date(2020, 4, 15)

for ticker in ("xauusd", "eurusd"):
    df = src.fetch(ticker, start, end, frequency="1hour", asset_class="forex")
    if df.empty:
        print(f"{ticker}: EMPTY")
        continue
    span = df.index.max() - df.index.min()
    print(f"{ticker}: {len(df)} bars, {df.index.min()} -> {df.index.max()} (span {span.days}d)")
'
```

Expected (approximate, depends on Tiingo plan):
```
xauusd: ~25000 bars, 2022-XX-XX -> 2026-04-14 (span ~1300d)
eurusd: ~25000 bars, 2022-XX-XX -> 2026-04-14 (span ~1300d)
```

- [ ] **Step 2: Decide bundle (β vs α vs ABORT)**

Apply gates:
- `EURUSD span < 1095d` → **ABORT plan** (escalate to user). Both Bundle β and α need EURUSD.
- `XAUUSD span < 1095d` AND `EURUSD span ≥ 1095d` → **Bundle α** (use GLD instead of XAU/USD).
- Both ≥ 1095d → **Bundle β** (primary).

Record decision and continue.

- [ ] **Step 3: Write retention record**

```bash
.venv/bin/python -c '
from datetime import date
from pathlib import Path
from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
end = date(2026, 4, 15)
start = date(2020, 4, 15)
lines = ["# Vol-Expansion FX 1h retention probe — " + str(end), ""]
for ticker in ("xauusd", "eurusd"):
    df = src.fetch(ticker, start, end, frequency="1hour", asset_class="forex")
    if df.empty:
        lines.append(f"- {ticker}: EMPTY")
    else:
        span = df.index.max() - df.index.min()
        lines.append(f"- {ticker}: {len(df)} bars, {df.index.min()} -> {df.index.max()}, span {span.days}d")
lines.append("")
lines.append("Decision: <fill manually after review>")
Path("reports/vol_expansion_fx_retention_probe.md").write_text("\n".join(lines) + "\n")
print("wrote reports/vol_expansion_fx_retention_probe.md")
'
```

- [ ] **Step 4: Commit**

```bash
git add reports/vol_expansion_fx_retention_probe.md
git commit -m "chore(probe): record XAU/USD and EURUSD 1h retention pre vol-expansion plan"
```

---

## Task 2: Scaffold package + RegimeReading + base import test

**Files:**
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py`
- Create: `tests/test_vol_expansion_regime_filter.py`
- Modify: `src/ai_trade/backtest/strategies/__init__.py`

- [ ] **Step 1: Write failing import test**

Create `tests/test_vol_expansion_regime_filter.py`:

```python
"""Tests for YangZhangCone + RegimeReading [volatility_trading, p.22-23, p.58-60]."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import (
    RegimeReading,
    YangZhangCone,
)


def test_regime_reading_dataclass_fields() -> None:
    r = RegimeReading(
        is_quiet=True,
        sigma_yz_annual=0.20,
        sigma_yz_percentile=12.0,
        bars_in_history=1700,
    )
    assert r.is_quiet is True
    assert r.sigma_yz_annual == pytest.approx(0.20)
    assert r.sigma_yz_percentile == pytest.approx(12.0)
    assert r.bars_in_history == 1700
```

- [ ] **Step 2: Run test, expect ImportError**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py::test_regime_reading_dataclass_fields -v
```

Expected: `ImportError: cannot import name 'RegimeReading'...`.

- [ ] **Step 3: Create scaffold modules**

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`:

```python
"""Vol-Expansion Breakout strategy package.

See docs/superpowers/specs/2026-04-15-vol-expansion-breakout-1h-design.md.
"""

from __future__ import annotations

from ai_trade.backtest.strategies.vol_expansion_breakout._regime_filter import (
    RegimeReading,
    YangZhangCone,
)

__all__ = ["RegimeReading", "YangZhangCone"]
```

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py`:

```python
"""Yang-Zhang volatility estimator + cone percentile filter.

Sinclair [volatility_trading, p.22-23, Eq.2.17a] for YZ; [p.58-60] for cone.
Output API consumed by sizer (§3.3) and disaster stop (§3.4) of the spec.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeReading:
    """Single observation of regime state at one bar."""

    is_quiet: bool
    sigma_yz_annual: float
    sigma_yz_percentile: float
    bars_in_history: int


class YangZhangCone:
    """Stub — implementation in subsequent tasks."""

    def __init__(self, yz_window: int, cone_lookback: int, k_filter: float, bars_per_year: int) -> None:
        self.yz_window = yz_window
        self.cone_lookback = cone_lookback
        self.k_filter = k_filter
        self.bars_per_year = bars_per_year
```

- [ ] **Step 4: Run test, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py::test_regime_reading_dataclass_fields -v
```

Expected: PASS.

- [ ] **Step 5: Update strategies/__init__.py to re-export**

In `src/ai_trade/backtest/strategies/__init__.py`, add (preserving existing exports):

```python
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    RegimeReading,
    YangZhangCone,
)
```

Add to `__all__` if it's a list.

- [ ] **Step 6: Run full test suite to confirm baseline still green**

```bash
.venv/bin/pytest -q
```

Expected: 432+ tests pass (1 new = 433).

- [ ] **Step 7: Commit**

```bash
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/ src/ai_trade/backtest/strategies/__init__.py tests/test_vol_expansion_regime_filter.py
git commit -m "feat(vol-expansion): scaffold package + RegimeReading dataclass"
```

---

## Task 3: YangZhangCone — YZ estimator (no cone yet)

**Files:**
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py`
- Modify: `tests/test_vol_expansion_regime_filter.py`

**Reference formulas** (Sinclair `[p.22-23, Eq.2.17a]`):

```
σ²_o = variance of (log(O_i / C_{i-1}))   [overnight close-to-open]
σ²_c = variance of (log(C_i / O_i))       [open-to-close]
σ²_rs = mean over i of [
    log(H_i/C_i)·log(H_i/O_i) + log(L_i/C_i)·log(L_i/O_i)
]   [Rogers-Satchell-Yoon, Eq.2.16]
k = 0.34 / (1.34 + (N+1)/(N-1))
σ²_yz = σ²_o + k·σ²_c + (1-k)·σ²_rs
```

`σ_yz_per_bar = sqrt(σ²_yz)`. Annualization: `σ_yz_annual = σ_yz_per_bar × sqrt(bars_per_year)`.

- [ ] **Step 1: Write failing tests for YZ formula + k weighting**

Append to `tests/test_vol_expansion_regime_filter.py`:

```python
def _ohlc_df(opens, highs, lows, closes) -> pd.DataFrame:
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes})


def test_yz_k_weighting_factor_n20() -> None:
    """k = 0.34 / (1.34 + (N+1)/(N-1)) for N=20."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    expected_k = 0.34 / (1.34 + (20 + 1) / (20 - 1))
    assert cone._k() == pytest.approx(expected_k)


def test_yz_constant_prices_returns_zero() -> None:
    """Constant OHLC -> all variance components 0 -> sigma_yz=0."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    df = _ohlc_df([100.0]*30, [100.0]*30, [100.0]*30, [100.0]*30)
    sigma_per_bar = cone._yz_per_bar(df)
    assert sigma_per_bar == pytest.approx(0.0, abs=1e-12)


def test_yz_opening_jump_dominates_close_to_close() -> None:
    """Overnight gaps push YZ above close-to-close (Sinclair p.22 claim)."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    rng = np.random.default_rng(42)
    n = 30
    closes = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    opens = closes + rng.normal(0, 1.5, n)  # large overnight jumps
    highs = np.maximum(opens, closes) + 0.1
    lows = np.minimum(opens, closes) - 0.1
    df = _ohlc_df(opens, highs, lows, closes)
    yz = cone._yz_per_bar(df)
    log_returns = np.log(closes[1:] / closes[:-1])
    cc_per_bar = float(log_returns.std(ddof=0))
    assert yz > cc_per_bar


def test_yz_annualization_spy_bars_per_year() -> None:
    """sigma_yz_annual = sigma_per_bar × sqrt(bars_per_year). SPY=1638."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    annual = cone._annualize(0.01)
    assert annual == pytest.approx(0.01 * math.sqrt(1638))


def test_yz_annualization_fx_bars_per_year() -> None:
    """FX uses 6240 bars/year."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=6240)
    annual = cone._annualize(0.01)
    assert annual == pytest.approx(0.01 * math.sqrt(6240))
```

- [ ] **Step 2: Run, expect failures (`AttributeError: '_k'` etc.)**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py -v
```

Expected: 5 new tests fail.

- [ ] **Step 3: Implement `_k`, `_yz_per_bar`, `_annualize`**

Replace the `YangZhangCone.__init__` stub with the full class (keep imports at top of file):

```python
import math

import numpy as np
import pandas as pd


class YangZhangCone:
    """Yang-Zhang vol estimator + cone percentile."""

    def __init__(
        self,
        yz_window: int,
        cone_lookback: int,
        k_filter: float,
        bars_per_year: int,
    ) -> None:
        if yz_window < 2:
            raise ValueError("yz_window must be >= 2")
        if cone_lookback < yz_window:
            raise ValueError("cone_lookback must be >= yz_window")
        if not 0.0 < k_filter < 100.0:
            raise ValueError("k_filter must be in (0, 100)")
        if bars_per_year <= 0:
            raise ValueError("bars_per_year must be positive")
        self.yz_window = yz_window
        self.cone_lookback = cone_lookback
        self.k_filter = k_filter
        self.bars_per_year = bars_per_year

    def _k(self) -> float:
        n = self.yz_window
        return 0.34 / (1.34 + (n + 1) / (n - 1))

    def _yz_per_bar(self, df: pd.DataFrame) -> float:
        """Yang-Zhang per-bar sigma over the most recent yz_window bars.

        Requires len(df) >= yz_window + 1 (needs prior close for overnight).
        Returns 0.0 if data is degenerate (constant prices) or has NaNs.
        """
        if len(df) < self.yz_window + 1:
            return 0.0
        window = df.iloc[-(self.yz_window + 1):]
        opens = window["open"].to_numpy()
        highs = window["high"].to_numpy()
        lows = window["low"].to_numpy()
        closes = window["close"].to_numpy()

        # Overnight: log(O_i / C_{i-1}), i in [1, N]
        log_oc = np.log(opens[1:] / closes[:-1])
        var_o = float(np.var(log_oc, ddof=0))

        # Open-to-close: log(C_i / O_i), i in [1, N]
        log_co = np.log(closes[1:] / opens[1:])
        var_c = float(np.var(log_co, ddof=0))

        # Rogers-Satchell-Yoon: per-bar contribution then mean
        h = highs[1:]
        l = lows[1:]
        o = opens[1:]
        c = closes[1:]
        rs_terms = (
            np.log(h / c) * np.log(h / o)
            + np.log(l / c) * np.log(l / o)
        )
        var_rs = float(np.mean(rs_terms))

        k = self._k()
        var_yz = var_o + k * var_c + (1.0 - k) * var_rs
        if not np.isfinite(var_yz) or var_yz <= 0:
            return 0.0
        return math.sqrt(var_yz)

    def _annualize(self, sigma_per_bar: float) -> float:
        return sigma_per_bar * math.sqrt(self.bars_per_year)
```

- [ ] **Step 4: Run new tests, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py -v
```

Expected: 6 PASS (1 from Task 2 + 5 new).

- [ ] **Step 5: Run full suite**

```bash
.venv/bin/pytest -q
```

Expected: baseline + 6 new pass.

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py tests/test_vol_expansion_regime_filter.py
git commit -m "feat(vol-expansion): Yang-Zhang volatility estimator [volatility_trading, p.22-23, Eq.2.17a]"
```

---

## Task 4: YangZhangCone — Cone percentile + `read()` API

**Files:**
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py`
- Modify: `tests/test_vol_expansion_regime_filter.py`

- [ ] **Step 1: Write failing tests for cone + warmup + read()**

Append to `tests/test_vol_expansion_regime_filter.py`:

```python
def _synth_ohlc(n: int, seed: int = 0, scale: float = 1.0) -> pd.DataFrame:
    """Synthetic OHLC with controllable noise scale."""
    rng = np.random.default_rng(seed)
    closes = 100.0 + np.cumsum(rng.normal(0, 0.5 * scale, n))
    opens = closes + rng.normal(0, 0.2 * scale, n)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0, 0.3 * scale, n))
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0, 0.3 * scale, n))
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes})


def test_cone_warmup_returns_not_quiet() -> None:
    """Until cone_lookback bars accumulate, is_quiet=False, percentile=NaN."""
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    df = _synth_ohlc(50)
    reading = cone.read(df)
    assert reading.is_quiet is False
    assert reading.bars_in_history < 100
    assert math.isnan(reading.sigma_yz_percentile)


def test_cone_post_warmup_emits_percentile() -> None:
    """Past warmup, percentile is in [0, 100]."""
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    df = _synth_ohlc(200, seed=7)
    reading = cone.read(df)
    assert reading.bars_in_history >= 100
    assert 0.0 <= reading.sigma_yz_percentile <= 100.0
    assert reading.sigma_yz_annual >= 0.0


def test_cone_quiet_when_current_yz_below_k_percentile() -> None:
    """If current YZ is in the bottom k_filter pct of history, is_quiet=True."""
    # Build history of "high vol" then end with "low vol" tail
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    high_vol = _synth_ohlc(150, seed=1, scale=3.0)
    low_vol = _synth_ohlc(30, seed=2, scale=0.3)
    # offset low_vol prices to continue from high_vol last close
    low_vol = low_vol + (high_vol["close"].iloc[-1] - low_vol["close"].iloc[0])
    df = pd.concat([high_vol, low_vol], ignore_index=True)
    reading = cone.read(df)
    assert reading.is_quiet is True
    assert reading.sigma_yz_percentile <= 33.0
```

- [ ] **Step 2: Run, expect AttributeError on `read`**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py -v
```

Expected: 3 new tests fail.

- [ ] **Step 3: Implement `read()` with cone history**

Append to `YangZhangCone` in `_regime_filter.py`:

```python
    def read(self, df: pd.DataFrame) -> RegimeReading:
        """Compute current sigma_yz and its percentile in the cone history.

        Builds the cone history by sliding YZ over all available bars
        (recomputed each call — caller is the strategy's per-bar buffer,
        which already trims to maxlen). For backtest scale (~10k bars)
        this is fast enough; live trading would use incremental update.
        """
        n = len(df)
        min_required = self.yz_window + 1
        if n < min_required:
            return RegimeReading(
                is_quiet=False,
                sigma_yz_annual=0.0,
                sigma_yz_percentile=float("nan"),
                bars_in_history=0,
            )

        # Roll YZ across all valid windows
        history: list[float] = []
        for end in range(min_required, n + 1):
            sigma = self._yz_per_bar(df.iloc[:end])
            history.append(sigma)

        sigma_now_per_bar = history[-1]
        sigma_now_annual = self._annualize(sigma_now_per_bar)
        bars_in_history = len(history)

        # Cap history at cone_lookback
        if bars_in_history > self.cone_lookback:
            history = history[-self.cone_lookback:]

        if bars_in_history < self.cone_lookback:
            return RegimeReading(
                is_quiet=False,
                sigma_yz_annual=sigma_now_annual,
                sigma_yz_percentile=float("nan"),
                bars_in_history=bars_in_history,
            )

        arr = np.asarray(history, dtype=float)
        # Percentile rank of current value (inclusive)
        pct = float((arr <= sigma_now_per_bar).sum()) / len(arr) * 100.0
        is_quiet = pct <= self.k_filter

        return RegimeReading(
            is_quiet=is_quiet,
            sigma_yz_annual=sigma_now_annual,
            sigma_yz_percentile=pct,
            bars_in_history=bars_in_history,
        )
```

- [ ] **Step 4: Run, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_regime_filter.py -v
```

Expected: 9 PASS.

- [ ] **Step 5: Run full suite**

```bash
.venv/bin/pytest -q
```

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_regime_filter.py tests/test_vol_expansion_regime_filter.py
git commit -m "feat(vol-expansion): cone percentile read() with k_filter regime gate [volatility_trading, p.58-60]"
```

---

## Task 5: DonchianBreakout signal

**Files:**
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_breakout_signal.py`
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`
- Create: `tests/test_vol_expansion_breakout_signal.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_vol_expansion_breakout_signal.py`:

```python
"""Tests for DonchianBreakout [trading_systems_methods, p.353]."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import (
    BreakoutDirection,
    DonchianBreakout,
)


def _ohlc(highs, lows, closes) -> pd.DataFrame:
    n = len(closes)
    opens = list(closes)  # opens unused by signal
    return pd.DataFrame({
        "open": opens, "high": list(highs), "low": list(lows), "close": list(closes),
    })


def test_long_fire_when_close_breaks_above_window_high() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.linspace(100, 105, 21)) + [110.0]  # last close is breakout
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    df = _ohlc(highs, lows, closes)
    assert sig.fire(df) == BreakoutDirection.LONG


def test_short_fire_when_close_breaks_below_window_low() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.linspace(100, 95, 21)) + [80.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    df = _ohlc(highs, lows, closes)
    assert sig.fire(df) == BreakoutDirection.SHORT


def test_no_fire_when_close_inside_channel() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.full(22, 100.0))
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    df = _ohlc(highs, lows, closes)
    assert sig.fire(df) is None


def test_no_fire_at_exact_boundary() -> None:
    """Strict greater-than: close == max(N) does NOT fire long."""
    sig = DonchianBreakout(n_entry=20)
    highs = [101.0] * 20 + [101.0, 101.0]  # last 2 bars also 101
    lows = [99.0] * 22
    closes = [100.0] * 21 + [101.0]  # last close == window high
    df = _ohlc(highs, lows, closes)
    assert sig.fire(df) is None


def test_returns_none_when_buffer_too_small() -> None:
    sig = DonchianBreakout(n_entry=20)
    df = _ohlc([100.0] * 5, [99.0] * 5, [99.5] * 5)
    assert sig.fire(df) is None
```

- [ ] **Step 2: Run, expect ImportError**

```bash
.venv/bin/pytest tests/test_vol_expansion_breakout_signal.py -v
```

Expected: ImportError on `BreakoutDirection`/`DonchianBreakout`.

- [ ] **Step 3: Implement `_breakout_signal.py`**

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/_breakout_signal.py`:

```python
"""Donchian channel breakout signal [trading_systems_methods, p.353].

Kaufman cites this as the basis of the Turtle method. Strict greater-than
on long, strict less-than on short — equality at the channel does not fire.
"""

from __future__ import annotations

from enum import Enum

import pandas as pd


class BreakoutDirection(str, Enum):
    LONG = "long"
    SHORT = "short"


class DonchianBreakout:
    """Channel-break entry signal."""

    def __init__(self, n_entry: int) -> None:
        if n_entry < 2:
            raise ValueError("n_entry must be >= 2")
        self.n_entry = n_entry

    def fire(self, df: pd.DataFrame) -> BreakoutDirection | None:
        """Return entry direction or None.

        Channel computed over the prior `n_entry` bars (excluding the
        current/last bar). Last bar's close compared to those bounds.
        """
        if len(df) < self.n_entry + 1:
            return None
        window = df.iloc[-(self.n_entry + 1):-1]  # exclude last bar
        last_close = float(df["close"].iloc[-1])
        high_window = float(window["high"].max())
        low_window = float(window["low"].min())
        if last_close > high_window:
            return BreakoutDirection.LONG
        if last_close < low_window:
            return BreakoutDirection.SHORT
        return None
```

- [ ] **Step 4: Update `__init__.py`**

In `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`, add:

```python
from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
    DonchianBreakout,
)
```

Add `BreakoutDirection`, `DonchianBreakout` to `__all__`.

- [ ] **Step 5: Run, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_breakout_signal.py -v
```

Expected: 5 PASS.

- [ ] **Step 6: Run full suite + commit**

```bash
.venv/bin/pytest -q
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_breakout_signal.py src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py tests/test_vol_expansion_breakout_signal.py
git commit -m "feat(vol-expansion): Donchian channel breakout signal [trading_systems_methods, p.353]"
```

---

## Task 6: VolTargetSizer (Carver vol-targeting)

**Files:**
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_vol_target_sizer.py`
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`
- Create: `tests/test_vol_expansion_sizer.py`

**Formula** (spec §3.3): `notional = target_vol_annual × equity / sigma_yz_annual`. Then `shares = notional / entry_price`.

- [ ] **Step 1: Write failing tests**

Create `tests/test_vol_expansion_sizer.py`:

```python
"""Tests for VolTargetSizer [systematic_trading, p.144, p.159, ch.9-10]."""

from __future__ import annotations

import logging
import math

import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import VolTargetSizer


def test_sizer_canonical_carver_formula() -> None:
    """sigma_yz=0.20, target=0.10, equity=$100k -> notional=$50k, shares=100."""
    sizer = VolTargetSizer(target_vol_annual=0.10)
    notional, shares = sizer.size(
        equity=100_000.0, sigma_yz_annual=0.20, entry_price=500.0,
    )
    assert notional == pytest.approx(50_000.0)
    assert shares == pytest.approx(100.0)


def test_sizer_sigma_floor_zero_returns_zero(caplog) -> None:
    """sigma below 1e-6 -> notional=0, shares=0, warning logged."""
    sizer = VolTargetSizer(target_vol_annual=0.10)
    with caplog.at_level(logging.WARNING):
        notional, shares = sizer.size(
            equity=100_000.0, sigma_yz_annual=1e-9, entry_price=500.0,
        )
    assert notional == 0.0
    assert shares == 0.0
    assert any("sigma" in rec.message.lower() for rec in caplog.records)


def test_sizer_consumes_annualized_input_directly() -> None:
    """Sizer does not re-scale input. Input is already annualized."""
    sizer = VolTargetSizer(target_vol_annual=0.10)
    n1, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    n2, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.40, entry_price=100.0)
    # Doubling sigma halves notional
    assert n2 == pytest.approx(n1 / 2.0)


def test_sizer_equity_scaling_linear() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    n1, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    n2, _ = sizer.size(equity=200_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    assert n2 == pytest.approx(n1 * 2.0)


def test_sizer_shares_scales_inversely_with_price() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    _, sh1 = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    _, sh2 = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=200.0)
    assert sh2 == pytest.approx(sh1 / 2.0)
```

- [ ] **Step 2: Run, expect ImportError**

```bash
.venv/bin/pytest tests/test_vol_expansion_sizer.py -v
```

- [ ] **Step 3: Implement `_vol_target_sizer.py`**

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/_vol_target_sizer.py`:

```python
"""Carver volatility-targeting sizer [systematic_trading, p.144, p.159, ch.9-10].

Half-Kelly intuition: target_vol = SR_realistic / 2. We use 0.10 (~SR=0.2,
conservative); Carver caps at 0.25 for semi-auto staunch [p.146].
"""

from __future__ import annotations

import logging

logger = logging.getLogger("ai_trade.strategy.vol_expansion.sizer")

SIGMA_FLOOR = 1e-6


class VolTargetSizer:
    def __init__(self, target_vol_annual: float) -> None:
        if not 0.0 < target_vol_annual < 1.0:
            raise ValueError("target_vol_annual must be in (0, 1)")
        self.target_vol_annual = target_vol_annual

    def size(
        self,
        equity: float,
        sigma_yz_annual: float,
        entry_price: float,
    ) -> tuple[float, float]:
        """Return (notional_dollars, shares).

        sigma_yz_annual is the **annualized** YZ output from RegimeFilter
        (single annualization happens in the filter; sizer does not rescale).
        """
        if sigma_yz_annual < SIGMA_FLOOR:
            logger.warning(
                "sigma_yz_annual=%.3e below floor %.0e — sizing to 0",
                sigma_yz_annual, SIGMA_FLOOR,
            )
            return 0.0, 0.0
        if entry_price <= 0:
            logger.warning("entry_price<=0 — sizing to 0")
            return 0.0, 0.0
        if equity <= 0:
            return 0.0, 0.0

        notional = self.target_vol_annual * equity / sigma_yz_annual
        shares = notional / entry_price
        return notional, shares
```

- [ ] **Step 4: Update `__init__.py` to export `VolTargetSizer`**

- [ ] **Step 5: Run, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_sizer.py -v
```

Expected: 5 PASS.

- [ ] **Step 6: Full suite + commit**

```bash
.venv/bin/pytest -q
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_vol_target_sizer.py src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py tests/test_vol_expansion_sizer.py
git commit -m "feat(vol-expansion): Carver volatility-targeting sizer [systematic_trading, p.144, p.159]"
```

---

## Task 7: ExitManager (3 conditions, primeiro-disparo)

**Files:**
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_exit_manager.py`
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`
- Create: `tests/test_vol_expansion_exit_manager.py`

Spec §3.4 disaster stop unit conversion:
```
sigma_pp_per_bar = entry_price × sigma_yz_annual / sqrt(bars_per_year)
sigma_pp_ref = sigma_pp_per_bar × sqrt(REF_HOLD_BARS)   # REF_HOLD_BARS=24
disaster_threshold = 4 × sigma_pp_ref
```

- [ ] **Step 1: Write failing tests**

Create `tests/test_vol_expansion_exit_manager.py`:

```python
"""Tests for ExitManager [trading_systems_methods, p.353; systematic_trading, p.212]."""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import (
    BreakoutDirection,
    ExitManager,
    ExitReason,
    PositionState,
)


def _ohlc(highs, lows, closes) -> pd.DataFrame:
    return pd.DataFrame({
        "open": list(closes), "high": list(highs),
        "low": list(lows), "close": list(closes),
    })


def _pos(direction: BreakoutDirection, entry_price: float = 500.0,
         entry_ts: datetime = datetime(2024, 1, 1, 9, 30),
         sigma_yz_annual: float = 0.20, bars_per_year: int = 1638) -> PositionState:
    return PositionState(
        direction=direction,
        entry_price=entry_price,
        entry_timestamp=entry_ts,
        sigma_yz_at_entry_annual=sigma_yz_annual,
        bars_per_year_at_entry=bars_per_year,
    )


def test_opposite_channel_exit_long() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 10 + [95.0]   # last close < min(prior 10) trough
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    lows[-2] = 99.5  # ensure prior-low > last close
    df = _ohlc(highs, lows, closes)
    pos = _pos(BreakoutDirection.LONG, entry_price=100.0)
    now = datetime(2024, 1, 1, 10, 30)
    reason = em.should_exit(df=df, position=pos, now=now)
    assert reason == ExitReason.OPPOSITE_CHANNEL


def test_opposite_channel_exit_short() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 10 + [110.0]
    highs = [c + 0.5 for c in closes]
    highs[-2] = 100.5
    lows = [c - 0.5 for c in closes]
    df = _ohlc(highs, lows, closes)
    pos = _pos(BreakoutDirection.SHORT, entry_price=100.0)
    now = datetime(2024, 1, 1, 10, 30)
    reason = em.should_exit(df=df, position=pos, now=now)
    assert reason == ExitReason.OPPOSITE_CHANNEL


def test_time_stop_at_48h() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 11
    df = _ohlc([c + 0.5 for c in closes], [c - 0.5 for c in closes], closes)
    pos = _pos(BreakoutDirection.LONG, entry_ts=datetime(2024, 1, 1, 0, 0))
    now = datetime(2024, 1, 3, 0, 0)  # exactly 48h
    reason = em.should_exit(df=df, position=pos, now=now)
    assert reason == ExitReason.TIME_STOP


def test_disaster_stop_long_triggers_at_4_sigma_loss() -> None:
    """Entry $500, sigma_yz_annual=0.20, bars_per_year=1638, REF_HOLD=24
       -> sigma_pp_per_bar = 500*0.2/sqrt(1638) ~ 2.47
       -> sigma_pp_ref = 2.47*sqrt(24) ~ 12.10
       -> threshold = 4 * 12.10 ~ 48.40
    Close $451 should trigger; $452 should not."""
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.LONG, entry_price=500.0,
               sigma_yz_annual=0.20, bars_per_year=1638)
    now = datetime(2024, 1, 1, 10, 30)

    # Build 11-bar df for opposite-channel evaluation; constant prices except last close
    closes = [500.0] * 10 + [451.0]
    df = _ohlc([c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    reason = em.should_exit(df=df, position=pos, now=now)
    assert reason == ExitReason.DISASTER_STOP

    closes2 = [500.0] * 10 + [452.0]
    df2 = _ohlc([c + 0.1 for c in closes2], [c - 0.1 for c in closes2], closes2)
    reason2 = em.should_exit(df=df2, position=pos, now=now)
    assert reason2 != ExitReason.DISASTER_STOP


def test_disaster_stop_short_triggers_at_4_sigma_gain() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.SHORT, entry_price=500.0,
               sigma_yz_annual=0.20, bars_per_year=1638)
    closes = [500.0] * 10 + [549.0]
    df = _ohlc([c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    now = datetime(2024, 1, 1, 10, 30)
    reason = em.should_exit(df=df, position=pos, now=now)
    assert reason == ExitReason.DISASTER_STOP


def test_exit_priority_disaster_beats_opposite_channel() -> None:
    """When both fire same bar, ordering: opposite_channel evaluated first
    (Donchian is the primary expected exit). But disaster is a safety net.
    Order is documented in implementation; test pins the chosen order."""
    em = ExitManager(n_exit=10, max_hold_hours=48.0,
                     disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.LONG, entry_price=500.0,
               sigma_yz_annual=0.20, bars_per_year=1638)
    # Last close is both below opposite channel AND triggers 4 sigma stop
    closes = [500.0] * 10 + [400.0]  # huge drop: triggers both
    df = _ohlc([c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    now = datetime(2024, 1, 1, 10, 30)
    reason = em.should_exit(df=df, position=pos, now=now)
    # Opposite-channel is checked first (canonical Donchian behavior)
    assert reason == ExitReason.OPPOSITE_CHANNEL
```

- [ ] **Step 2: Run, expect ImportError**

```bash
.venv/bin/pytest tests/test_vol_expansion_exit_manager.py -v
```

- [ ] **Step 3: Implement `_exit_manager.py`**

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/_exit_manager.py`:

```python
"""ExitManager — three exit conditions, first-fires.

1. Opposite Donchian channel [trading_systems_methods, p.353]
2. 48h hard cap [chan-pairs-1h-design §1.4 + tiingo-service spec §1.4]
3. Disaster stop 4 sigma_price_points [systematic_trading, p.212, ch.13]

Order: opposite-channel -> time-stop -> disaster. Opposite-channel first
because it's the canonical Donchian exit (spec §3.4). Time-stop next
because it's wall-clock and unambiguous. Disaster last as the safety net.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd

from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
)


class ExitReason(str, Enum):
    OPPOSITE_CHANNEL = "opposite_channel"
    TIME_STOP = "time_stop"
    DISASTER_STOP = "disaster_stop"


@dataclass(frozen=True)
class PositionState:
    direction: BreakoutDirection
    entry_price: float
    entry_timestamp: datetime
    sigma_yz_at_entry_annual: float
    bars_per_year_at_entry: int


class ExitManager:
    def __init__(
        self,
        n_exit: int,
        max_hold_hours: float,
        disaster_n_sigma: float,
        ref_hold_bars: int,
    ) -> None:
        if n_exit < 2:
            raise ValueError("n_exit must be >= 2")
        if max_hold_hours <= 0:
            raise ValueError("max_hold_hours must be positive")
        if disaster_n_sigma <= 0:
            raise ValueError("disaster_n_sigma must be positive")
        if ref_hold_bars < 1:
            raise ValueError("ref_hold_bars must be positive")
        self.n_exit = n_exit
        self.max_hold_hours = max_hold_hours
        self.disaster_n_sigma = disaster_n_sigma
        self.ref_hold_bars = ref_hold_bars

    def disaster_threshold(self, position: PositionState) -> float:
        sigma_pp_per_bar = (
            position.entry_price
            * position.sigma_yz_at_entry_annual
            / math.sqrt(position.bars_per_year_at_entry)
        )
        sigma_pp_ref = sigma_pp_per_bar * math.sqrt(self.ref_hold_bars)
        return self.disaster_n_sigma * sigma_pp_ref

    def should_exit(
        self,
        df: pd.DataFrame,
        position: PositionState,
        now: datetime,
    ) -> ExitReason | None:
        if len(df) < self.n_exit + 1:
            return None
        last_close = float(df["close"].iloc[-1])
        window = df.iloc[-(self.n_exit + 1):-1]
        high_window = float(window["high"].max())
        low_window = float(window["low"].min())

        # 1. Opposite Donchian channel
        if position.direction == BreakoutDirection.LONG and last_close < low_window:
            return ExitReason.OPPOSITE_CHANNEL
        if position.direction == BreakoutDirection.SHORT and last_close > high_window:
            return ExitReason.OPPOSITE_CHANNEL

        # 2. 48h wall-clock hard cap
        elapsed = now - position.entry_timestamp
        if elapsed >= timedelta(hours=self.max_hold_hours):
            return ExitReason.TIME_STOP

        # 3. Disaster stop
        threshold = self.disaster_threshold(position)
        if position.direction == BreakoutDirection.LONG:
            if (position.entry_price - last_close) >= threshold:
                return ExitReason.DISASTER_STOP
        else:
            if (last_close - position.entry_price) >= threshold:
                return ExitReason.DISASTER_STOP

        return None
```

- [ ] **Step 4: Update `__init__.py`**

Add to `__init__.py`:

```python
from ai_trade.backtest.strategies.vol_expansion_breakout._exit_manager import (
    ExitManager,
    ExitReason,
    PositionState,
)
```

Add to `__all__`.

- [ ] **Step 5: Run new tests, expect PASS**

```bash
.venv/bin/pytest tests/test_vol_expansion_exit_manager.py -v
```

Expected: 6 PASS.

- [ ] **Step 6: Full suite + commit**

```bash
.venv/bin/pytest -q
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_exit_manager.py src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py tests/test_vol_expansion_exit_manager.py
git commit -m "feat(vol-expansion): ExitManager — opposite channel + 48h cap + 4σ disaster [systematic_trading, p.212]"
```

---

## Task 8: VolExpansionBreakoutStrategy orchestrator

**Files:**
- Create: `src/ai_trade/backtest/strategies/vol_expansion_breakout/_strategy.py`
- Modify: `src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py`
- Modify: `src/ai_trade/backtest/strategies/__init__.py`
- Create: `tests/test_vol_expansion_strategy_integration.py`

The orchestrator implements the `Strategy` Protocol (`on_bar(bars, portfolio, context) -> list[Order]`). It maintains per-symbol state in `context` and emits `Order` objects.

- [ ] **Step 1: Write failing integration tests**

Create `tests/test_vol_expansion_strategy_integration.py`:

```python
"""Integration tests for VolExpansionBreakoutStrategy [spec §1, §3]."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.engine.execution import Bar
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    VolExpansionBreakoutStrategy,
)


def _synth_quiet_then_breakout(n: int, breakout_at: int, seed: int = 0) -> pd.DataFrame:
    """First `breakout_at` bars: low vol noise. After: trend break."""
    rng = np.random.default_rng(seed)
    quiet = 100.0 + np.cumsum(rng.normal(0, 0.05, breakout_at))
    trend = quiet[-1] + np.cumsum(np.full(n - breakout_at, 0.5))
    closes = np.concatenate([quiet, trend])
    opens = closes + rng.normal(0, 0.02, n)
    highs = np.maximum(opens, closes) + 0.05
    lows = np.minimum(opens, closes) - 0.05
    ts = pd.date_range("2023-01-01 09:30", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes,
         "adj_close": closes, "volume": [1000.0] * n},
        index=ts,
    )


def _bar(symbol: str, ts: pd.Timestamp, row: pd.Series) -> Bar:
    return Bar(
        symbol=symbol, timestamp=ts.to_pydatetime(),
        open=float(row["open"]), high=float(row["high"]),
        low=float(row["low"]), close=float(row["close"]),
        volume=float(row.get("volume", 1000.0)),
    )


def test_quiet_regime_then_breakout_emits_long() -> None:
    """1300 bars quiet + 50 bars breakout -> at least 1 long order."""
    df = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=1)
    strat = VolExpansionBreakoutStrategy(
        data={"SPY": df},
        symbol_specs={"SPY": {"bars_per_year": 1638}},
        n_entry=20, n_exit=10,
        cone_lookback=800, yz_window=20, k_filter=33.0,
        target_vol_annual=0.10,
        max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24,
    )
    portfolio = Portfolio(cash=100_000.0)
    context: dict = {}
    saw_long = False
    for ts, row in df.iterrows():
        bars = {"SPY": _bar("SPY", ts, row)}
        orders = strat.on_bar(bars, portfolio, context)
        if any(o.side == "buy" for o in orders):
            saw_long = True
            break
    assert saw_long


def test_pure_high_vol_emits_zero_orders() -> None:
    """Always-noisy regime never satisfies is_quiet -> zero orders."""
    rng = np.random.default_rng(2)
    n = 1100
    closes = 100.0 + np.cumsum(rng.normal(0, 2.0, n))  # high vol throughout
    opens = closes + rng.normal(0, 1.0, n)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0, 0.5, n))
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0, 0.5, n))
    ts = pd.date_range("2023-01-01 09:30", periods=n, freq="h", tz="UTC")
    df = pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes,
         "adj_close": closes, "volume": [1000.0] * n},
        index=ts,
    )
    strat = VolExpansionBreakoutStrategy(
        data={"SPY": df},
        symbol_specs={"SPY": {"bars_per_year": 1638}},
        n_entry=20, n_exit=10,
        cone_lookback=500, yz_window=20, k_filter=5.0,  # very strict
        target_vol_annual=0.10,
        max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24,
    )
    portfolio = Portfolio(cash=100_000.0)
    context: dict = {}
    total_orders = 0
    for ts, row in df.iterrows():
        bars = {"SPY": _bar("SPY", ts, row)}
        orders = strat.on_bar(bars, portfolio, context)
        total_orders += len(orders)
    assert total_orders == 0


def test_multi_symbol_independent_state() -> None:
    """3 symbols processed independently in one strategy instance."""
    df_a = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=10)
    df_b = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=20)
    df_c = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=30)
    strat = VolExpansionBreakoutStrategy(
        data={"A": df_a, "B": df_b, "C": df_c},
        symbol_specs={
            "A": {"bars_per_year": 1638},
            "B": {"bars_per_year": 6240},
            "C": {"bars_per_year": 6240},
        },
        n_entry=20, n_exit=10,
        cone_lookback=800, yz_window=20, k_filter=33.0,
        target_vol_annual=0.10,
        max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24,
    )
    portfolio = Portfolio(cash=100_000.0)
    context: dict = {}
    symbols_with_trades = set()
    for i, ts in enumerate(df_a.index):
        bars = {
            "A": _bar("A", ts, df_a.iloc[i]),
            "B": _bar("B", ts, df_b.iloc[i]),
            "C": _bar("C", ts, df_c.iloc[i]),
        }
        orders = strat.on_bar(bars, portfolio, context)
        for o in orders:
            symbols_with_trades.add(o.symbol)
    assert len(symbols_with_trades) >= 2  # at least 2 of 3 should breakout
```

- [ ] **Step 2: Run, expect ImportError**

```bash
.venv/bin/pytest tests/test_vol_expansion_strategy_integration.py -v
```

- [ ] **Step 3: Implement `_strategy.py`**

Create `src/ai_trade/backtest/strategies/vol_expansion_breakout/_strategy.py`:

```python
"""VolExpansionBreakoutStrategy — orchestrator.

Composes RegimeFilter + DonchianBreakout + VolTargetSizer + ExitManager.
Single instance handles N symbols; per-symbol state lives in context dict.

Spec: docs/superpowers/specs/2026-04-15-vol-expansion-breakout-1h-design.md.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
    DonchianBreakout,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._exit_manager import (
    ExitManager,
    ExitReason,
    PositionState,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._regime_filter import (
    YangZhangCone,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._vol_target_sizer import (
    VolTargetSizer,
)


STATE_KEY_PREFIX = "vol_expansion_state"
DIAG_KEY = "vol_expansion_diagnostics"


@dataclass
class VolExpansionBreakoutStrategy:
    """Multi-asset Donchian breakout filtered by Yang-Zhang vol cone."""

    data: dict[str, pd.DataFrame]
    symbol_specs: dict[str, dict]   # {ticker: {"bars_per_year": int}}

    # Grid knobs.
    n_entry: int = 20
    n_exit: int = 10

    # Fixed (per spec §3.5).
    cone_lookback: int = 1700
    yz_window: int = 20
    k_filter: float = 33.0
    target_vol_annual: float = 0.10
    max_hold_hours: float = 48.0
    disaster_n_sigma: float = 4.0
    ref_hold_bars: int = 24

    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.vol_expansion"),
        repr=False,
    )
    _signal: DonchianBreakout = field(init=False)
    _sizer: VolTargetSizer = field(init=False)
    _exit_manager: ExitManager = field(init=False)
    _filters: dict[str, YangZhangCone] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        for sym in self.data:
            if sym not in self.symbol_specs:
                raise KeyError(f"symbol_specs missing entry for {sym!r}")
            if "bars_per_year" not in self.symbol_specs[sym]:
                raise KeyError(f"symbol_specs[{sym!r}] missing 'bars_per_year'")

        self._signal = DonchianBreakout(n_entry=self.n_entry)
        self._sizer = VolTargetSizer(target_vol_annual=self.target_vol_annual)
        self._exit_manager = ExitManager(
            n_exit=self.n_exit,
            max_hold_hours=self.max_hold_hours,
            disaster_n_sigma=self.disaster_n_sigma,
            ref_hold_bars=self.ref_hold_bars,
        )
        self._filters = {
            sym: YangZhangCone(
                yz_window=self.yz_window,
                cone_lookback=self.cone_lookback,
                k_filter=self.k_filter,
                bars_per_year=self.symbol_specs[sym]["bars_per_year"],
            )
            for sym in self.data
        }

    def _state_key(self, symbol: str) -> str:
        return f"{STATE_KEY_PREFIX}_{symbol}"

    def _record_diag(
        self,
        context: dict,
        symbol: str,
        event: str,
        **kwargs,
    ) -> None:
        diag = context.setdefault(DIAG_KEY, {})
        sym_diag = diag.setdefault(symbol, {"events": []})
        sym_diag["events"].append({"event": event, **kwargs})

    def _slice_to_now(self, symbol: str, ts: pd.Timestamp) -> pd.DataFrame:
        """Return data[symbol] up to and including ts. Empty if ts unknown."""
        df = self.data[symbol]
        try:
            idx = df.index.get_loc(ts)
        except KeyError:
            return df.iloc[:0]
        return df.iloc[: idx + 1]

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        orders: list[Order] = []
        for symbol, bar in bars.items():
            if symbol not in self.data:
                continue
            df_so_far = self._slice_to_now(symbol, pd.Timestamp(bar.timestamp, tz="UTC"))
            if df_so_far.empty:
                continue

            position = portfolio.positions.get(symbol)
            state_key = self._state_key(symbol)

            if position is not None:
                pos_state: PositionState | None = context.get(state_key)
                if pos_state is None:
                    # External state loss; cannot evaluate exits → skip this bar.
                    continue
                reason = self._exit_manager.should_exit(
                    df=df_so_far, position=pos_state, now=bar.timestamp,
                )
                if reason is not None:
                    close_side = "sell" if pos_state.direction == BreakoutDirection.LONG else "buy"
                    orders.append(Order(symbol=symbol, side=close_side, volume=position.volume))
                    self._record_diag(
                        context, symbol, "exit", reason=reason.value,
                        hold_hours=(bar.timestamp - pos_state.entry_timestamp).total_seconds() / 3600.0,
                    )
                    context.pop(state_key, None)
                continue

            # No position: evaluate entry
            reading = self._filters[symbol].read(df_so_far)
            if not reading.is_quiet:
                continue
            direction = self._signal.fire(df_so_far)
            if direction is None:
                continue
            entry_price = float(bar.close)
            notional, shares = self._sizer.size(
                equity=portfolio.equity,
                sigma_yz_annual=reading.sigma_yz_annual,
                entry_price=entry_price,
            )
            if shares <= 0:
                continue
            side = "buy" if direction == BreakoutDirection.LONG else "sell"
            orders.append(Order(symbol=symbol, side=side, volume=shares))
            context[state_key] = PositionState(
                direction=direction,
                entry_price=entry_price,
                entry_timestamp=bar.timestamp,
                sigma_yz_at_entry_annual=reading.sigma_yz_annual,
                bars_per_year_at_entry=self.symbol_specs[symbol]["bars_per_year"],
            )
            self._record_diag(
                context, symbol, "entry",
                direction=direction.value, entry_price=entry_price, shares=shares,
                sigma_yz_annual=reading.sigma_yz_annual,
                yz_percentile=reading.sigma_yz_percentile,
            )
        return orders
```

- [ ] **Step 4: Update `__init__.py`**

In `vol_expansion_breakout/__init__.py`:

```python
from ai_trade.backtest.strategies.vol_expansion_breakout._strategy import (
    VolExpansionBreakoutStrategy,
)
```

Add `VolExpansionBreakoutStrategy` to `__all__`.

In `src/ai_trade/backtest/strategies/__init__.py`:

```python
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    VolExpansionBreakoutStrategy,
)
```

- [ ] **Step 5: Run integration tests**

```bash
.venv/bin/pytest tests/test_vol_expansion_strategy_integration.py -v
```

Expected: 3 PASS.

- [ ] **Step 6: Full suite + commit**

```bash
.venv/bin/pytest -q
git add src/ai_trade/backtest/strategies/vol_expansion_breakout/_strategy.py src/ai_trade/backtest/strategies/vol_expansion_breakout/__init__.py src/ai_trade/backtest/strategies/__init__.py tests/test_vol_expansion_strategy_integration.py
git commit -m "feat(vol-expansion): VolExpansionBreakoutStrategy multi-asset orchestrator"
```

---

## Task 9: VolExpansionGridConfig + factory

**Files:**
- Create: `src/ai_trade/backtest/grid/vol_expansion_config.py`
- Modify: `src/ai_trade/backtest/grid/__init__.py`
- Create: `tests/test_vol_expansion_grid_config.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_vol_expansion_grid_config.py`:

```python
"""Tests for VolExpansionGridConfig [spec §3.5]."""

from __future__ import annotations

import pytest

from ai_trade.backtest.grid.vol_expansion_config import (
    VolExpansionGridConfig,
    vol_expansion_grid_configs,
)


def test_grid_returns_4_configs() -> None:
    configs = vol_expansion_grid_configs()
    assert len(configs) == 4


def test_grid_axes_are_n_entry_and_n_exit() -> None:
    configs = vol_expansion_grid_configs()
    pairs = {(c.n_entry, c.n_exit) for c in configs}
    assert pairs == {(20, 10), (20, 20), (55, 10), (55, 20)}


def test_grid_fixed_constants() -> None:
    """All non-gridded params have spec §3.5 defaults."""
    c = vol_expansion_grid_configs()[0]
    assert c.k_filter == 33.0
    assert c.target_vol_annual == 0.10
    assert c.disaster_n_sigma == 4.0
    assert c.ref_hold_bars == 24
    assert c.cone_lookback == 1700
    assert c.yz_window == 20
    assert c.max_hold_hours == 48.0
```

- [ ] **Step 2: Run, expect ImportError**

- [ ] **Step 3: Implement `vol_expansion_config.py`**

Create `src/ai_trade/backtest/grid/vol_expansion_config.py`:

```python
"""Vol-Expansion Breakout parameter grid [spec §3.5].

Grid axes (gridded):
* n_entry in (20, 55) — Turtles canonical vs Donchian original [trading_systems_methods, p.353]
* n_exit  in (10, 20) — Turtles canonical (5/20) vs symmetric with entry

Fixed (a priori, NOT gridded — see spec §3.1, §3.3, §3.4):
* k_filter=33, target_vol_annual=0.10, disaster_n_sigma=4, ref_hold_bars=24,
  cone_lookback=1700, yz_window=20, max_hold_hours=48.

Total: 2 × 2 = 4 configs. Per-asset → 12 trials in the full grid.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


N_ENTRY = (20, 55)
N_EXIT = (10, 20)


@dataclass(frozen=True)
class VolExpansionGridConfig:
    n_entry: int
    n_exit: int

    # Fixed.
    k_filter: float = 33.0
    target_vol_annual: float = 0.10
    disaster_n_sigma: float = 4.0
    ref_hold_bars: int = 24
    cone_lookback: int = 1700
    yz_window: int = 20
    max_hold_hours: float = 48.0


def vol_expansion_grid_configs() -> list[VolExpansionGridConfig]:
    """Cartesian product (n_entry, n_exit), stable order."""
    return [
        VolExpansionGridConfig(n_entry=ne, n_exit=nx)
        for ne, nx in itertools.product(N_ENTRY, N_EXIT)
    ]
```

- [ ] **Step 4: Update `grid/__init__.py`**

Add:

```python
from ai_trade.backtest.grid.vol_expansion_config import (
    VolExpansionGridConfig,
    vol_expansion_grid_configs,
)
```

Add to `__all__`.

- [ ] **Step 5: Run, expect PASS + full suite**

```bash
.venv/bin/pytest tests/test_vol_expansion_grid_config.py -v
.venv/bin/pytest -q
```

- [ ] **Step 6: Commit**

```bash
git add src/ai_trade/backtest/grid/vol_expansion_config.py src/ai_trade/backtest/grid/__init__.py tests/test_vol_expansion_grid_config.py
git commit -m "feat(grid): VolExpansionGridConfig — 4 configs (2 N_entry × 2 N_exit) [spec §3.5]"
```

---

## Task 10: CLI runner `scripts/run_grid_vol_expansion.py`

**Files:**
- Create: `scripts/run_grid_vol_expansion.py`

The runner mirrors `scripts/run_grid_chan_pairs.py` structure. Key differences:
- Multi-symbol orchestration (3 symbols per Bundle β, with α fallback wired by symbol args).
- Per-symbol `bars_per_year` derived from asset_class arg.
- Each symbol runs independently (not a basket), but report aggregates.

- [ ] **Step 1: Read existing pattern**

Read `scripts/run_grid_chan_pairs.py` end-to-end as the template. Identify (a) data fetch loop, (b) GridRunner construction, (c) gates evaluation, (d) report emission.

- [ ] **Step 2: Implement runner**

Create `scripts/run_grid_vol_expansion.py`:

```python
#!/usr/bin/env python3
"""Run the Vol-Expansion Breakout grid (Phase 2.5 second intraday entry).

End-to-end pipeline:

1. Fetch 1h OHLCV per symbol via TiingoSource (lazy-cache).
2. Build the 4 VolExpansionGridConfig configs.
3. For each (symbol, config) execute backtest → 12 total trials.
4. Walk-forward per config (anchored, ≥3 segments).
5. Evaluate gates: PBO < 0.5, DSR p < 0.05, WF positive, MCPT p < 0.05.
6. Emit report (PASS) or diagnostic (FAIL).

Bundle β:
    --symbol SPY --asset-class etf --bars-per-year 1638
    --symbol xauusd --asset-class forex --bars-per-year 6240
    --symbol eurusd --asset-class forex --bars-per-year 6240

Bundle α fallback (XAU→GLD):
    --symbol SPY --asset-class etf --bars-per-year 1638
    --symbol GLD --asset-class etf --bars-per-year 1638
    --symbol eurusd --asset-class forex --bars-per-year 6240

Smoke (1 config, 1 symbol, short range):
    .venv/bin/python scripts/run_grid_vol_expansion.py --dry-run \\
        --symbol SPY --asset-class etf --bars-per-year 1638 \\
        --start 2024-01-01 --end 2024-12-31 \\
        --output-dir /tmp/grid_vol_expansion_smoke
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.vol_expansion")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Vol-Expansion Breakout 1h grid with anti-overfit gates.",
    )
    ap.add_argument(
        "--symbol", action="append", required=True,
        help="Repeat for each symbol (Bundle β: SPY, xauusd, eurusd).",
    )
    ap.add_argument(
        "--asset-class", action="append", required=True,
        choices=["equity", "etf", "index", "crypto", "forex"],
        help="Asset class per symbol (same order as --symbol).",
    )
    ap.add_argument(
        "--bars-per-year", action="append", type=int, required=True,
        help="bars_per_year per symbol (1638 for US equity 1h, 6240 for FX 1h).",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--warmup-days", type=int, default=365)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _setup_logging(level: str, run_dir: Path) -> None:
    log_path = Path("logs/grid.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stderr),
    ]
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=handlers, force=True,
    )


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.engine.portfolio import Portfolio
    from ai_trade.backtest.grid.vol_expansion_config import (
        vol_expansion_grid_configs,
    )
    from ai_trade.backtest.strategies.vol_expansion_breakout import (
        VolExpansionBreakoutStrategy,
    )

    args = _parse_args(argv)
    if not (len(args.symbol) == len(args.asset_class) == len(args.bars_per_year)):
        log.error("--symbol, --asset-class, --bars-per-year must have same count")
        return 2

    run_id = args.run_id or f"grid_vol_expansion_{datetime.utcnow():%Y%m%d-%H%M}"
    run_dir = args.output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _setup_logging(args.log_level, run_dir)

    log.info("Vol-Expansion grid run_id=%s symbols=%s start=%s end=%s",
             run_id, list(zip(args.symbol, args.asset_class)),
             args.start, args.end)

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))

    # 1. Fetch all symbols up-front
    data: dict[str, pd.DataFrame] = {}
    symbol_specs: dict[str, dict] = {}
    for sym, ac, bpy in zip(args.symbol, args.asset_class, args.bars_per_year):
        log.info("fetch %s (%s) %s..%s 1h", sym, ac, args.start, args.end)
        df = src.fetch(sym, args.start, args.end, frequency="1hour", asset_class=ac)
        if df.empty:
            log.error("symbol %s returned EMPTY — abort", sym)
            return 3
        data[sym] = df
        symbol_specs[sym] = {"bars_per_year": bpy}

    # 2. Configs
    configs = vol_expansion_grid_configs()
    if args.dry_run:
        configs = configs[:1]
    log.info("running %d configs × %d symbols = %d trials",
             len(configs), len(data), len(configs) * len(data))

    # 3. Per-(symbol, config) backtest. Independent runs.
    results: list[dict] = []
    for cfg in tqdm(configs, desc="configs"):
        for sym in data:
            strat = VolExpansionBreakoutStrategy(
                data={sym: data[sym]},
                symbol_specs={sym: symbol_specs[sym]},
                n_entry=cfg.n_entry, n_exit=cfg.n_exit,
                cone_lookback=cfg.cone_lookback, yz_window=cfg.yz_window,
                k_filter=cfg.k_filter,
                target_vol_annual=cfg.target_vol_annual,
                max_hold_hours=cfg.max_hold_hours,
                disaster_n_sigma=cfg.disaster_n_sigma,
                ref_hold_bars=cfg.ref_hold_bars,
            )
            portfolio = Portfolio(cash=args.cash)
            sim = ExecutionSimulator(ExecutionConfig())
            runner = Runner(
                data=data[sym], strategy=strat,
                portfolio=portfolio, simulator=sim,
                symbols=[sym],
            )
            result = runner.run()
            results.append({
                "symbol": sym, "config": cfg,
                "metrics": result.metrics, "n_trades": len(result.trades),
            })
            log.info("symbol=%s config=%s sharpe=%.3f trades=%d",
                     sym, cfg, result.metrics.get("sharpe", float("nan")),
                     len(result.trades))

    # 4. Write raw results dump for downstream gates
    results_df = pd.DataFrame([
        {"symbol": r["symbol"], "n_entry": r["config"].n_entry,
         "n_exit": r["config"].n_exit, "n_trades": r["n_trades"],
         **r["metrics"]}
        for r in results
    ])
    results_df.to_csv(run_dir / "results.csv", index=False)
    log.info("wrote %s", run_dir / "results.csv")

    # 5. Emit minimal diagnostic markdown (gate evaluation hook for follow-up)
    diag_lines = [
        f"# Vol-Expansion Breakout grid {run_id}", "",
        f"- start: {args.start}", f"- end: {args.end}",
        f"- symbols: {list(data.keys())}",
        f"- n_configs: {len(configs)}",
        f"- n_trials: {len(results)}",
        "",
        "## Per-symbol/config results (raw)", "",
        "See `results.csv`.",
        "",
        "## Next manual steps", "",
        "- Run gate battery (CPCV/PBO/DSR/WF/MCPT) over results.csv",
        "- Verify §1.4 hard-cap usage per symbol (`pct_trades_exited_by_hard_cap`)",
        "- Check `n_trades_per_symbol >= 30` (else trigger K=50 retry per spec §5.4)",
    ]
    (run_dir / "diagnostic.md").write_text("\n".join(diag_lines) + "\n")
    log.info("wrote %s", run_dir / "diagnostic.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Make executable**

```bash
chmod +x scripts/run_grid_vol_expansion.py
```

- [ ] **Step 4: Smoke run with --dry-run on 1 symbol short range**

```bash
.venv/bin/python scripts/run_grid_vol_expansion.py --dry-run \
    --symbol SPY --asset-class etf --bars-per-year 1638 \
    --start 2024-01-01 --end 2024-06-30 \
    --output-dir /tmp/grid_vol_expansion_smoke
```

Expected: completes without exception, writes `/tmp/grid_vol_expansion_smoke/grid_vol_expansion_*/results.csv` and `diagnostic.md`. (May warn cone warmup — short range insufficient — but should not crash.)

- [ ] **Step 5: Commit**

```bash
git add scripts/run_grid_vol_expansion.py
git commit -m "feat(scripts): run_grid_vol_expansion CLI runner [spec §1.2 Bundle β]"
```

---

## Task 11: Full grid run (Bundle from Task 1) + diagnostic + commit reports

**Files:**
- Create: `reports/grid_vol_expansion_<timestamp>/results.csv`
- Create: `reports/grid_vol_expansion_<timestamp>/diagnostic.md`

- [ ] **Step 1: Run full grid using bundle decided in Task 1**

If Task 1 selected Bundle β:

```bash
.venv/bin/python scripts/run_grid_vol_expansion.py \
    --symbol SPY     --asset-class etf   --bars-per-year 1638 \
    --symbol xauusd  --asset-class forex --bars-per-year 6240 \
    --symbol eurusd  --asset-class forex --bars-per-year 6240 \
    --start 2022-04-15 --end 2026-04-15 \
    --cash 100000 --n-jobs 4 \
    --output-dir reports/
```

If Bundle α:

```bash
.venv/bin/python scripts/run_grid_vol_expansion.py \
    --symbol SPY    --asset-class etf   --bars-per-year 1638 \
    --symbol GLD    --asset-class etf   --bars-per-year 1638 \
    --symbol eurusd --asset-class forex --bars-per-year 6240 \
    --start 2022-04-15 --end 2026-04-15 \
    --cash 100000 --n-jobs 4 \
    --output-dir reports/
```

Expected wall-clock: < 60s. Output dir like `reports/grid_vol_expansion_20260415-XXXX/`.

- [ ] **Step 2: Inspect `diagnostic.md` and `results.csv`**

Read both files. Cross-check vs spec §5.3 obligatory metrics. If any obligatory metric is missing, list the gap and update the runner (Task 10) to emit it, then re-run.

Verify per spec §5.4 gates:
- `n_trades_per_symbol >= 30` for each symbol → if violated, **trigger K=50 retry**:

```bash
# Edit vol_expansion_config.py temporarily: K_FILTER = (50.0,) instead of 33.0
# OR add a CLI override --k-filter 50; for v1, just edit config + re-run + revert
```

Document the retry decision in `diagnostic.md` Notes section.

- [ ] **Step 3: Apply gate battery (CPCV/PBO/DSR/WF/MCPT)**

If gate runner is parameterized via CLI:

```bash
.venv/bin/python -m ai_trade.backtest.grid.gates \
    --results-csv reports/grid_vol_expansion_<timestamp>/results.csv \
    --output reports/grid_vol_expansion_<timestamp>/gates.md
```

(If no such CLI exists, hand-call the gate functions; consult `backtest/grid/gates.py`.)

- [ ] **Step 4: Write verdict block to diagnostic**

Append to `diagnostic.md`:

```markdown
## Verdict

PROCEED / PROCEED-WITH-CHANGES / BLOCK

- PBO: <value> (gate ≤ 0.5)
- DSR p: <value> (gate ≤ 0.05)
- WF segments positive: <x>/<n> (gate ≥ 50%)
- MCPT p: <value> (gate ≤ 0.05)
- median_hold_hours per symbol: ...
- pct_trades_exited_by_hard_cap per symbol: ...

Citation: [advances_fin_ml, p.156-160, p.205-211, ch.7]
```

- [ ] **Step 5: Commit reports**

```bash
git add reports/grid_vol_expansion_*/
git commit -m "chore(reports): vol-expansion 1h grid run — Bundle <β|α>, verdict <PROCEED|BLOCK>"
```

---

## Task 12: JORNADA + ROADMAP update

**Files:**
- Modify: `JORNADA.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Append JORNADA changelog entry**

Add a `## 2026-04-15 — <verdict-emoji> Vol-Expansion Breakout 1h: <verdict>` section. Brief summary, link to spec + plan + diagnostic. Update `## Onde estamos hoje` and `## O que vem a seguir` sections.

Use existing entries (especially the Chan pair entry) as the template. Cite `[volatility_trading, Sinclair]`, `[trading_systems_methods, Kaufman, p.353]`, `[systematic_trading, Carver, p.144, p.159, p.212]`.

- [ ] **Step 2: Update ROADMAP**

In `ROADMAP.md §Current status`, mark item 2 of "Next steps (post-pivot)" with the verdict and link to spec/plan/diagnostic. Update "Next steps" list — if PROCEED, item 3 (AFML meta-label) is now actionable; if BLOCK, item 3 of Next steps becomes "Ehlers BP Swing 1h" (third strategy in the catalog).

- [ ] **Step 3: Commit**

```bash
git add JORNADA.md ROADMAP.md
git commit -m "docs(jornada): vol-expansion breakout 1h verdict — <PASS|FAIL>"
```

---

## Self-Review Checklist

After implementing the plan, verify:

**Spec coverage:**
- §1 Contexto → Tasks 1, 12
- §2 Arquitetura → Tasks 2, 8 (package structure)
- §3.1 RegimeFilter → Tasks 3, 4
- §3.2 BreakoutSignal → Task 5
- §3.3 VolTargetSizer → Task 6
- §3.4 ExitManager → Task 7
- §3.5 Grid → Task 9
- §4 Dados → Tasks 1, 10
- §5 Gates + diagnostic → Task 11
- §6 Tests → embedded in Tasks 3-9
- §7 Hooks v2 → not implemented (deferred per spec)
- §8 YAGNI → respected (no pyramiding/GARCH/EWMA/multi-horizon/etc.)
- §9 Dependencies → all resolved (none missing in current repo)

**Type consistency:**
- `RegimeReading` fields used identically across `_regime_filter.py`, `_strategy.py`, tests
- `BreakoutDirection` enum used in `_breakout_signal.py`, `_exit_manager.py`, `_strategy.py`
- `PositionState` fields match between `_exit_manager.py` constructor and `_strategy.py` instantiation
- `bars_per_year` integer convention across filter, sizer, exit
- `sigma_yz_annual` annualized in all consumers (single annualization in filter)

**Citations propagated:**
- Spec citations (Sinclair, Kaufman, Carver, López de Prado) appear in module docstrings + commit messages

**Test coverage:**
- 8 + 5 + 5 + 6 + 3 + 3 = 30 new tests target. Spec promised ~27. Slightly over.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-15-vol-expansion-breakout-1h.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for bite-sized TDD where each task is self-contained.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review.

**Which approach?**
