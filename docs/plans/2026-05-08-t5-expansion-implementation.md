# T5 Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand T5 (Carver vol-target tier) from 2 configs to ~20 across new iters 022-025, adding skipped sub-phases T5b (carry forecast) and T5d (HRP/ERC weighting), plus focused robustness grid. Re-compute DSR cumulative across all 426 configs and amend study reports.

**Architecture:** New modules (`signals_carry`, `data_loader_yields`, `strategies/hrp_weighter`, `run_iter_t5_extended`) layered on top of existing T5 infrastructure without modifying `run_iter_t5.py`. Spec: `docs/specs/2026-05-08-t5-expansion-design.md`.

**Tech Stack:** Python 3.12, pandas, numpy, scipy.cluster.hierarchy, scipy.optimize, yfinance, pyarrow (parquet), pytest.

---

## Pre-flight

- [ ] **Confirm baseline:** `cd /var/www/github/finances/market-lab && uv run pytest -q` — must show 813 passing tests before starting. If fewer/more, investigate before proceeding.
- [ ] **Confirm data dir:** `ls data/external/yields/ 2>/dev/null || mkdir -p data/external/yields && touch data/external/yields/.gitkeep` — create cache dir.
- [ ] **Confirm yfinance available:** `uv run python -c "import yfinance; print(yfinance.__version__)"`. If missing: `uv add yfinance`.

---

### Task 1: `data_loader_yields.load_constant_maturity_yield`

**Files:**
- Create: `studies/letf_rotation_hunt/data_loader_yields.py`
- Test: `studies/letf_rotation_hunt/tests/test_data_loader_yields.py`

- [ ] **Step 1: Write failing test for tenor mapping**

```python
# studies/letf_rotation_hunt/tests/test_data_loader_yields.py
"""Tests for data_loader_yields (yields data fetcher).

T5 expansion adds yield data sources (CMT and dividend yield) backing
the Carver carry forecast in signals_carry.

Citations: spec docs/specs/2026-05-08-t5-expansion-design.md §3.2.
"""
from __future__ import annotations

import pandas as pd
import pytest

from studies.letf_rotation_hunt import data_loader_yields as dly


def test_load_cmt_known_tenors_return_series(monkeypatch, tmp_path):
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    fake = pd.Series(
        [0.044, 0.045, 0.046],
        index=pd.date_range("2024-01-02", periods=3, freq="D"),
        name="^TNX",
    )
    monkeypatch.setattr(dly, "_yfinance_fetch_yield", lambda ticker: fake)
    s = dly.load_constant_maturity_yield("10y")
    assert isinstance(s, pd.Series)
    assert (s == fake).all()


def test_load_cmt_unknown_tenor_raises():
    with pytest.raises(ValueError, match="tenor"):
        dly.load_constant_maturity_yield("7y")
```

- [ ] **Step 2: Run test, verify failure**

```
uv run pytest studies/letf_rotation_hunt/tests/test_data_loader_yields.py -v
```
Expected: FAIL — `ModuleNotFoundError: data_loader_yields`.

- [ ] **Step 3: Implement minimal `load_constant_maturity_yield`**

```python
# studies/letf_rotation_hunt/data_loader_yields.py
"""Yield data sources for T5b carry forecast.

Loads constant-maturity Treasury yields (^IRX/^TNX/^TYX) and trailing
12m dividend yields for equity ETFs. Caches as parquet under
data/external/yields/.

Citations
---------
* spec §3.2 (docs/specs/2026-05-08-t5-expansion-design.md)
* yfinance ticker symbols ^IRX/^TNX/^TYX = 13w/10y/30y CMT
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_CACHE_DIR = Path("data/external/yields")
_TENOR_TO_TICKER = {"3m": "^IRX", "10y": "^TNX", "30y": "^TYX"}


def load_constant_maturity_yield(tenor: str) -> pd.Series:
    """Daily constant-maturity Treasury yield (decimal annual).

    Cache: data/external/yields/cmt_{tenor}.parquet.
    Source: yfinance ^IRX (3m) / ^TNX (10y) / ^TYX (30y).
    """
    if tenor not in _TENOR_TO_TICKER:
        raise ValueError(f"tenor must be one of {list(_TENOR_TO_TICKER)}, got {tenor!r}")
    ticker = _TENOR_TO_TICKER[tenor]
    cache_path = _CACHE_DIR / f"cmt_{tenor}.parquet"
    if cache_path.exists():
        return pd.read_parquet(cache_path).iloc[:, 0]
    series = _yfinance_fetch_yield(ticker)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    series.to_frame(name=tenor).to_parquet(cache_path)
    return series


def _yfinance_fetch_yield(ticker: str) -> pd.Series:
    """Fetch CMT yield from yfinance (decimal annual)."""
    import yfinance as yf  # local import: keep top-level light
    hist = yf.Ticker(ticker).history(period="max", auto_adjust=False)
    if hist.empty:
        raise RuntimeError(f"yfinance returned empty for {ticker}")
    # ^TNX etc. quote yield * 100 (e.g., 4.4 = 4.4%); convert to decimal
    return (hist["Close"] / 100.0).rename(ticker)
```

- [ ] **Step 4: Run test, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_data_loader_yields.py -v
```
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/data_loader_yields.py studies/letf_rotation_hunt/tests/test_data_loader_yields.py
git commit -m "feat(letf-t5): add CMT yield loader for carry forecast"
```

---

### Task 2: `data_loader_yields.load_dividend_yield`

**Files:**
- Modify: `studies/letf_rotation_hunt/data_loader_yields.py`
- Modify: `studies/letf_rotation_hunt/tests/test_data_loader_yields.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_data_loader_yields.py`:

```python
def test_load_dividend_yield_trailing_12m(monkeypatch, tmp_path):
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    dates = pd.date_range("2024-01-01", periods=400, freq="D")
    dividends = pd.Series(0.0, index=dates)
    # 4 quarterly dividends of $0.50 each → $2/yr
    for d in [dates[60], dates[150], dates[240], dates[330]]:
        dividends[d] = 0.50
    prices = pd.Series(100.0, index=dates)
    monkeypatch.setattr(dly, "_yfinance_fetch_dividends", lambda t: dividends)
    monkeypatch.setattr(dly, "_yfinance_fetch_adj_close", lambda t: prices)
    s = dly.load_dividend_yield("SPY")
    assert isinstance(s, pd.Series)
    # After full year of dividends, trailing 12m sum = $2 / $100 = 0.02
    last_year_yield = s.iloc[-1]
    assert 0.018 < last_year_yield < 0.022, last_year_yield
```

- [ ] **Step 2: Run test, verify failure**

```
uv run pytest studies/letf_rotation_hunt/tests/test_data_loader_yields.py::test_load_dividend_yield_trailing_12m -v
```
Expected: FAIL — `AttributeError: ... load_dividend_yield`.

- [ ] **Step 3: Implement**

Append to `data_loader_yields.py`:

```python
def load_dividend_yield(underlying: str) -> pd.Series:
    """Trailing 12m dividend yield for an underlying ETF (decimal).

    Cache: data/external/yields/{underlying}_divyield.parquet.
    Computation: rolling 365-day sum of dividends / current Adj Close.
    """
    cache_path = _CACHE_DIR / f"{underlying}_divyield.parquet"
    if cache_path.exists():
        return pd.read_parquet(cache_path).iloc[:, 0]
    dividends = _yfinance_fetch_dividends(underlying)
    prices = _yfinance_fetch_adj_close(underlying)
    common = dividends.index.intersection(prices.index)
    if len(common) == 0:
        raise RuntimeError(f"No overlapping dates for {underlying} dividends/prices")
    div_aligned = dividends.reindex(prices.index, fill_value=0.0)
    rolling_div = div_aligned.rolling("365D").sum()
    ttm_yield = (rolling_div / prices).rename(f"{underlying}_divyield")
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ttm_yield.to_frame().to_parquet(cache_path)
    return ttm_yield


def _yfinance_fetch_dividends(ticker: str) -> pd.Series:
    import yfinance as yf
    divs = yf.Ticker(ticker).dividends
    if divs.empty:
        raise RuntimeError(f"yfinance returned no dividends for {ticker}")
    divs.index = divs.index.tz_localize(None)
    return divs


def _yfinance_fetch_adj_close(ticker: str) -> pd.Series:
    import yfinance as yf
    hist = yf.Ticker(ticker).history(period="max", auto_adjust=True)
    if hist.empty:
        raise RuntimeError(f"yfinance returned empty for {ticker}")
    hist.index = hist.index.tz_localize(None)
    return hist["Close"].rename(ticker)
```

- [ ] **Step 4: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_data_loader_yields.py -v
```
Expected: 3 PASS (cumulative).

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/data_loader_yields.py studies/letf_rotation_hunt/tests/test_data_loader_yields.py
git commit -m "feat(letf-t5): add trailing-12m dividend yield loader"
```

---

### Task 3: Real data fetch + cache priming

**Files:**
- Run-only (writes to `data/external/yields/`).

- [ ] **Step 1: Prime cache for required assets**

```
uv run python -c "
from studies.letf_rotation_hunt import data_loader_yields as dly
for t in ['3m', '10y', '30y']:
    s = dly.load_constant_maturity_yield(t)
    print(f'CMT {t}: {len(s)} rows, {s.index.min().date()}..{s.index.max().date()}')
for u in ['SPY', 'QQQ']:
    s = dly.load_dividend_yield(u)
    print(f'DivYield {u}: {len(s)} rows, {s.index.min().date()}..{s.index.max().date()}')
"
```
Expected: 5 lines printed, all with row counts > 5000 (≥20y of data) for ^TNX/^TYX/SPY/QQQ; ^IRX may be shorter.

- [ ] **Step 2: Verify cache files written**

```
ls -la data/external/yields/
```
Expected: `cmt_3m.parquet`, `cmt_10y.parquet`, `cmt_30y.parquet`, `SPY_divyield.parquet`, `QQQ_divyield.parquet`.

- [ ] **Step 3: Commit cached data (small parquet files)**

```
git add data/external/yields/
git commit -m "data(letf-t5): cache CMT and dividend-yield series"
```

---

### Task 4: `signals_carry.compute_carry_forecast` — equity branch

**Files:**
- Create: `studies/letf_rotation_hunt/signals_carry.py`
- Test: `studies/letf_rotation_hunt/tests/test_signals_carry.py`

- [ ] **Step 1: Write failing test**

```python
# studies/letf_rotation_hunt/tests/test_signals_carry.py
"""Tests for signals_carry (Carver per-asset carry forecast).

Citation: spec §3.1 (docs/specs/2026-05-08-t5-expansion-design.md);
[systematic_trading, ch.9 p.180-190].
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.letf_rotation_hunt import signals_carry as sc


def _const_series(value: float, n: int = 500) -> pd.Series:
    return pd.Series(value, index=pd.date_range("2010-01-04", periods=n, freq="B"))


def test_equity_carry_positive_when_div_yield_exceeds_financing(monkeypatch):
    # SPY div yield 2%, FFR 0.5%, UPRO leverage 3 → carry_raw = 0.02 - 3*0.005 = +0.005
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.02),
    )
    ffr = _const_series(0.005)
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr)
    assert (f.dropna() > 0).all(), "expected positive forecast when div yield > 3*FFR"


def test_equity_carry_negative_when_financing_exceeds_div_yield(monkeypatch):
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.01),
    )
    ffr = _const_series(0.05)  # high rate regime
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr)
    assert (f.dropna() < 0).all(), "expected negative forecast when 3*FFR > div yield"


def test_carry_clipped_at_pm_20(monkeypatch):
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.50),
    )
    ffr = _const_series(0.0)
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr).dropna()
    assert (f.abs() <= 20.0).all()
```

- [ ] **Step 2: Run, verify failure**

```
uv run pytest studies/letf_rotation_hunt/tests/test_signals_carry.py -v
```
Expected: FAIL — `ModuleNotFoundError: signals_carry`.

- [ ] **Step 3: Implement equity-branch carry**

```python
# studies/letf_rotation_hunt/signals_carry.py
"""Per-asset carry forecast for T5b — Carver framework.

carry_raw[t]    = expected_yield[t] - leverage[asset] * FFR[t]
carry_norm[t]   = (carry_raw / rolling_std(carry_raw, 252)) * scalar
forecast[t]     = carry_norm.clip(-20, 20)

Citation: [systematic_trading, ch.9 p.180-190];
spec docs/specs/2026-05-08-t5-expansion-design.md §3.1.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt import data_loader_yields as dly


@dataclass(frozen=True)
class _AssetCarryConfig:
    yield_kind: str   # "equity_div", "bond_cmt", "none"
    yield_key: str    # e.g. "SPY", "30y", or ""
    leverage: float
    asset_class: str  # "equity", "bond", "gold"


_ASSET_CARRY_MAP: dict[str, _AssetCarryConfig] = {
    "UPRO": _AssetCarryConfig("equity_div", "SPY", 3.0, "equity"),
    "QLD":  _AssetCarryConfig("equity_div", "QQQ", 2.0, "equity"),
    "TQQQ": _AssetCarryConfig("equity_div", "QQQ", 3.0, "equity"),
    "TMF":  _AssetCarryConfig("bond_cmt",   "30y", 3.0, "bond"),
    "ZROZ": _AssetCarryConfig("bond_cmt",   "30y", 1.0, "bond"),
    "UGL":  _AssetCarryConfig("none",       "",    2.0, "gold"),
}

# Initial scalars; calibrated empirically in Task 11.
_CARRY_SCALAR_BY_CLASS: dict[str, float] = {
    "equity": 10.0,
    "bond": 10.0,
    "gold": 0.0,
}


def compute_carry_forecast(
    asset: str, asset_prices: pd.Series, ffr_daily: pd.Series, fdm: float = 1.0,
) -> pd.Series:
    if asset not in _ASSET_CARRY_MAP:
        raise ValueError(f"asset {asset!r} not in carry map; add to _ASSET_CARRY_MAP")
    cfg = _ASSET_CARRY_MAP[asset]
    if cfg.asset_class == "gold":
        return pd.Series(0.0, index=asset_prices.index, name=f"carry_{asset}")

    yield_series = _load_yield_for_asset(asset).reindex(asset_prices.index).ffill()
    ffr_annual = _ffr_daily_to_annual(ffr_daily).reindex(asset_prices.index).ffill()

    carry_raw = yield_series - cfg.leverage * ffr_annual
    carry_std = carry_raw.rolling(window=252, min_periods=126).std()
    scalar = _CARRY_SCALAR_BY_CLASS[cfg.asset_class]
    carry_norm = (carry_raw / carry_std) * scalar * fdm
    return carry_norm.clip(-20.0, 20.0).rename(f"carry_{asset}")


def _load_yield_for_asset(asset: str) -> pd.Series:
    cfg = _ASSET_CARRY_MAP[asset]
    if cfg.yield_kind == "equity_div":
        return dly.load_dividend_yield(cfg.yield_key)
    if cfg.yield_kind == "bond_cmt":
        return dly.load_constant_maturity_yield(cfg.yield_key)
    raise ValueError(f"yield_kind {cfg.yield_kind!r} not supported for asset {asset!r}")


def _ffr_daily_to_annual(ffr_daily: pd.Series) -> pd.Series:
    """ffr_daily is daily pct return ≈ FFR/252. Re-annualize."""
    return ffr_daily * 252.0
```

- [ ] **Step 4: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_signals_carry.py -v
```
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/signals_carry.py studies/letf_rotation_hunt/tests/test_signals_carry.py
git commit -m "feat(letf-t5): add equity-branch carry forecast (Carver ch.9)"
```

---

### Task 5: `signals_carry` — bond branch test + gold short-circuit

**Files:**
- Modify: `studies/letf_rotation_hunt/tests/test_signals_carry.py`

- [ ] **Step 1: Add bond + gold tests**

Append:

```python
def test_bond_carry_uses_30y_cmt(monkeypatch):
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.045),  # 30y at 4.5%
    )
    ffr = _const_series(0.005)  # FFR 0.5%
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("TMF", prices, ffr)
    # carry_raw = 0.045 - 3*0.005 = 0.030 > 0 → forecast positive
    assert (f.dropna() > 0).all()


def test_gold_carry_returns_zero():
    prices = _const_series(100.0)
    ffr = _const_series(0.02)
    f = sc.compute_carry_forecast("UGL", prices, ffr)
    assert (f == 0.0).all()


def test_unknown_asset_raises():
    prices = _const_series(100.0)
    ffr = _const_series(0.01)
    with pytest.raises(ValueError, match="not in carry map"):
        sc.compute_carry_forecast("XYZ", prices, ffr)
```

- [ ] **Step 2: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_signals_carry.py -v
```
Expected: 6 PASS (3 from Task 4 + 3 new).

- [ ] **Step 3: Commit**

```
git add studies/letf_rotation_hunt/tests/test_signals_carry.py
git commit -m "test(letf-t5): cover bond/gold/unknown branches of carry forecast"
```

---

### Task 6: `signals_carry.compose_ewmac_carry`

**Files:**
- Modify: `studies/letf_rotation_hunt/signals_carry.py`
- Modify: `studies/letf_rotation_hunt/tests/test_signals_carry.py`

- [ ] **Step 1: Write failing test**

Append to test file:

```python
def test_compose_ewmac_carry_50_50_blend_with_fdm():
    idx = pd.date_range("2010-01-04", periods=10, freq="B")
    ewmac = pd.Series(10.0, index=idx)
    carry = pd.Series(2.0, index=idx)
    composed = sc.compose_ewmac_carry(ewmac, carry, fdm=1.41)
    expected = ((10.0 + 2.0) / 2.0) * 1.41  # = 8.46
    np.testing.assert_allclose(composed.values, expected, rtol=1e-9)


def test_compose_ewmac_carry_clipped_at_pm_20():
    idx = pd.date_range("2010-01-04", periods=5, freq="B")
    ewmac = pd.Series(20.0, index=idx)
    carry = pd.Series(20.0, index=idx)
    composed = sc.compose_ewmac_carry(ewmac, carry, fdm=2.0)
    # ((20+20)/2)*2 = 40 → clip to 20
    assert (composed == 20.0).all()
```

- [ ] **Step 2: Run, verify fail**

Expected: AttributeError on `compose_ewmac_carry`.

- [ ] **Step 3: Implement**

Append to `signals_carry.py`:

```python
def compose_ewmac_carry(
    ewmac: pd.Series, carry: pd.Series, fdm: float = 1.41,
) -> pd.Series:
    """50/50 blend of EWMAC and carry forecasts with FDM (Carver ch.9 p.185).

    Both inputs must already be individually scaled to SD≈10.
    FDM=1.41 = 2-forecast diversification multiplier (Carver Table 49 [p.285]).
    """
    blended = (ewmac + carry) / 2.0 * fdm
    return blended.clip(-20.0, 20.0)
```

- [ ] **Step 4: Run, verify pass**

Expected: 8 PASS in `test_signals_carry.py`.

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/signals_carry.py studies/letf_rotation_hunt/tests/test_signals_carry.py
git commit -m "feat(letf-t5): add EWMAC+carry composition (FDM 1.41)"
```

---

### Task 7: `strategies/hrp_weighter.compute_hrp_weights`

**Files:**
- Create: `studies/letf_rotation_hunt/strategies/hrp_weighter.py`
- Test: `studies/letf_rotation_hunt/tests/test_hrp_weighter.py`

- [ ] **Step 1: Write failing tests**

```python
# studies/letf_rotation_hunt/tests/test_hrp_weighter.py
"""Tests for HRP and ERC weighting (López de Prado ch.16).

Citation: spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md);
[advances_fin_ml, ch.16 p.221-228].
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.letf_rotation_hunt.strategies import hrp_weighter as hw


def _gaussian_returns(seed: int, n: int, cols: list[str], cov: np.ndarray) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.multivariate_normal(np.zeros(len(cols)), cov, size=n)
    return pd.DataFrame(
        rets, columns=cols,
        index=pd.date_range("2010-01-04", periods=n, freq="B"),
    )


def test_hrp_weights_sum_to_one_and_positive():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=0, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last_row = w.iloc[-1]
    assert np.isclose(last_row.sum(), 1.0)
    assert (last_row >= 0).all()


def test_hrp_uncorrelated_equal_vol_yields_equal_weights():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=1, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1].values
    np.testing.assert_allclose(last, np.full(4, 0.25), atol=0.05)


def test_hrp_high_vol_asset_gets_lower_weight():
    cov = np.diag([0.01, 0.01, 0.01, 0.05]) ** 2
    rets = _gaussian_returns(seed=2, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert last["D"] < last[["A", "B", "C"]].min()
```

- [ ] **Step 2: Run, verify failure**

Expected: ModuleNotFoundError on `hrp_weighter`.

- [ ] **Step 3: Implement HRP**

```python
# studies/letf_rotation_hunt/strategies/hrp_weighter.py
"""HRP and ERC weighting schemes for T5d (multi-asset Carver vol-target).

Citations
---------
* HRP: López de Prado [advances_fin_ml, ch.16 p.221-228]
* ERC: Maillard, Roncalli, Teïletche (2010), 'Properties of Equally
  Weighted Risk Contribution Portfolios'
* spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform


def compute_hrp_weights(
    returns: pd.DataFrame, lookback: int = 252, min_periods: int = 126,
) -> pd.DataFrame:
    out = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    for i, date in enumerate(returns.index):
        if i + 1 < min_periods:
            continue
        window = returns.iloc[max(0, i + 1 - lookback): i + 1]
        if len(window) < min_periods:
            continue
        out.loc[date] = _hrp_single(window)
    return out


def _hrp_single(returns: pd.DataFrame) -> pd.Series:
    cov = returns.cov().values
    corr = returns.corr().values
    np.fill_diagonal(corr, 1.0)
    dist = np.sqrt(0.5 * (1.0 - np.clip(corr, -1.0, 1.0)))
    np.fill_diagonal(dist, 0.0)
    link = linkage(squareform(dist, checks=False), method="single")
    sort_ix = _quasi_diag(link, n=len(returns.columns))
    weights = _recursive_bisection(cov, sort_ix)
    return pd.Series(weights, index=[returns.columns[i] for i in sort_ix]).reindex(returns.columns)


def _quasi_diag(link: np.ndarray, n: int) -> list[int]:
    link = link.astype(int)
    sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
    while sort_ix.max() >= n:
        sort_ix.index = range(0, sort_ix.size * 2, 2)
        df0 = sort_ix[sort_ix >= n]
        i = df0.index
        j = df0.values - n
        sort_ix[i] = link[j, 0]
        df0 = pd.Series(link[j, 1], index=i + 1)
        sort_ix = pd.concat([sort_ix, df0]).sort_index()
        sort_ix.index = range(sort_ix.size)
    return sort_ix.tolist()


def _recursive_bisection(cov: np.ndarray, sort_ix: list[int]) -> np.ndarray:
    weights = np.ones(len(sort_ix))
    clusters = [sort_ix]
    while clusters:
        new_clusters = []
        for c in clusters:
            if len(c) <= 1:
                continue
            half = len(c) // 2
            left, right = c[:half], c[half:]
            var_l = _cluster_var(cov, left)
            var_r = _cluster_var(cov, right)
            alpha = 1.0 - var_l / (var_l + var_r)
            for idx in left:
                weights[sort_ix.index(idx)] *= alpha
            for idx in right:
                weights[sort_ix.index(idx)] *= (1.0 - alpha)
            new_clusters.extend([left, right])
        clusters = new_clusters
    return weights


def _cluster_var(cov: np.ndarray, indices: list[int]) -> float:
    sub = cov[np.ix_(indices, indices)]
    inv_diag = 1.0 / np.diag(sub)
    w = inv_diag / inv_diag.sum()
    return float(w @ sub @ w)
```

- [ ] **Step 4: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_hrp_weighter.py -v
```
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/strategies/hrp_weighter.py studies/letf_rotation_hunt/tests/test_hrp_weighter.py
git commit -m "feat(letf-t5): add HRP weighting (López de Prado ch.16)"
```

---

### Task 8: `hrp_weighter.compute_erc_weights`

**Files:**
- Modify: `studies/letf_rotation_hunt/strategies/hrp_weighter.py`
- Modify: `studies/letf_rotation_hunt/tests/test_hrp_weighter.py`

- [ ] **Step 1: Write failing test**

Append:

```python
def test_erc_weights_sum_to_one_and_positive():
    cov = np.diag([0.01, 0.02, 0.03, 0.04]) ** 2
    rets = _gaussian_returns(seed=3, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert np.isclose(last.sum(), 1.0, atol=1e-6)
    assert (last > 0).all()


def test_erc_equal_vol_yields_equal_weights():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=4, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1].values
    np.testing.assert_allclose(last, np.full(4, 0.25), atol=0.02)


def test_erc_higher_vol_asset_gets_lower_weight():
    cov = np.diag([0.01, 0.01, 0.01, 0.10]) ** 2
    rets = _gaussian_returns(seed=5, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert last["D"] < 0.10  # highest-vol asset gets <10%
```

- [ ] **Step 2: Run, verify fail**

Expected: AttributeError on `compute_erc_weights`.

- [ ] **Step 3: Implement ERC**

Append to `hrp_weighter.py`:

```python
def compute_erc_weights(
    returns: pd.DataFrame, lookback: int = 252, min_periods: int = 126,
    max_iter: int = 100, tol: float = 1e-8,
) -> pd.DataFrame:
    out = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    for i, date in enumerate(returns.index):
        if i + 1 < min_periods:
            continue
        window = returns.iloc[max(0, i + 1 - lookback): i + 1]
        if len(window) < min_periods:
            continue
        cov = window.cov().values
        out.loc[date] = _erc_single(cov, max_iter, tol)
    return out


def _erc_single(cov: np.ndarray, max_iter: int, tol: float) -> np.ndarray:
    n = cov.shape[0]
    w = np.full(n, 1.0 / n)
    for _ in range(max_iter):
        port_vol = np.sqrt(w @ cov @ w)
        marginal = (cov @ w) / port_vol
        rc = w * marginal  # risk contributions
        target = port_vol / n
        # gradient step toward equal RC
        delta = (target - rc) / marginal
        w_new = w + 0.5 * delta
        w_new = np.clip(w_new, 1e-8, None)
        w_new /= w_new.sum()
        if np.max(np.abs(w_new - w)) < tol:
            return w_new
        w = w_new
    return w
```

- [ ] **Step 4: Run, verify pass**

Expected: 6 PASS in `test_hrp_weighter.py`.

- [ ] **Step 5: Commit**

```
git add studies/letf_rotation_hunt/strategies/hrp_weighter.py studies/letf_rotation_hunt/tests/test_hrp_weighter.py
git commit -m "feat(letf-t5): add ERC weighting via Newton iteration"
```

---

### Task 9: `build_positions` external_weights parameter

**Files:**
- Modify: `studies/letf_rotation_hunt/strategies/vol_targeted.py`
- Test: `studies/letf_rotation_hunt/tests/test_vol_targeted_external_weights.py`

- [ ] **Step 1: Write failing test (new file)**

```python
# studies/letf_rotation_hunt/tests/test_vol_targeted_external_weights.py
"""Tests for build_positions with external_weights (T5d HRP/ERC integration).

Citation: spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.strategies.vol_targeted import build_positions


def _frame(value: float, idx, cols):
    return pd.DataFrame(value, index=idx, columns=cols)


def test_external_weights_replaces_idm_uniform_allocation():
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    pool = ["A", "B", "C", "D"]
    forecasts = _frame(10.0, idx, pool)
    vols = _frame(0.01, idx, pool)
    # Skewed weights favoring asset A
    weights = pd.DataFrame(
        np.tile([0.5, 0.2, 0.2, 0.1], (len(idx), 1)),
        index=idx, columns=pool,
    )
    pos = build_positions(
        forecasts=forecasts, vol_per_asset=vols,
        sigma_target=0.25, idm=1.0, position_inertia=0.0,
        off_asset="OFF", external_weights=weights,
    )
    last = pos.iloc[-1].drop("OFF")
    # Asset A should have largest weight (after renormalization to ≤1)
    assert last["A"] > last["B"]
    assert last["A"] > last["D"]


def test_no_external_weights_matches_baseline_behavior():
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    pool = ["A", "B", "C"]
    forecasts = _frame(10.0, idx, pool)
    vols = _frame(0.01, idx, pool)
    pos_baseline = build_positions(
        forecasts=forecasts, vol_per_asset=vols, sigma_target=0.25,
        idm=2.5, position_inertia=0.0, off_asset="OFF",
    )
    pos_explicit_none = build_positions(
        forecasts=forecasts, vol_per_asset=vols, sigma_target=0.25,
        idm=2.5, position_inertia=0.0, off_asset="OFF",
        external_weights=None,
    )
    pd.testing.assert_frame_equal(pos_baseline, pos_explicit_none)
```

- [ ] **Step 2: Run, verify fail**

Expected: TypeError — `external_weights` not a valid kwarg.

- [ ] **Step 3: Modify `build_positions`**

Edit `studies/letf_rotation_hunt/strategies/vol_targeted.py:20-93` to add `external_weights` parameter. Replace function signature and body:

```python
def build_positions(
    forecasts: pd.DataFrame,
    vol_per_asset: pd.DataFrame,
    sigma_target: float,
    idm: float,
    position_inertia: float,
    off_asset: str,
    external_weights: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Carver vol-targeted positions (long-only).

    When ``external_weights`` is provided, it replaces the ``idm`` uniform
    multiplier per asset. Each asset's allocation is multiplied by
    ``external_weights[asset, t]`` instead of ``idm``. Weights must sum
    to 1 across the pool (will be normalized). See spec §3.3.
    """
    if external_weights is None and idm > 2.5:
        raise ValueError(f"idm must be ≤ 2.5 per Carver [p.170-171], got {idm}")

    assets = list(forecasts.columns)
    if off_asset not in assets:
        assets.append(off_asset)

    daily_vol_target = sigma_target / np.sqrt(TRADING_DAYS_PER_YEAR)
    positions = pd.DataFrame(0.0, index=forecasts.index, columns=assets)
    prev_positions = pd.Series(0.0, index=assets)

    for date in forecasts.index:
        target_row = pd.Series(0.0, index=assets)
        for a in forecasts.columns:
            f = forecasts.loc[date, a]
            v = vol_per_asset.loc[date, a]
            if pd.isna(f) or pd.isna(v) or v <= 0 or f <= 0:
                target_row[a] = 0.0
                continue
            vol_scalar = daily_vol_target / v
            if external_weights is not None:
                w = external_weights.loc[date, a] if date in external_weights.index else 0.0
                if pd.isna(w):
                    w = 0.0
                # Per-asset allocation: vol_scalar * f/10 * weight * N_assets
                # The N_assets factor maintains parity with IDM=N case under equal weights
                multiplier = w * len(forecasts.columns)
            else:
                multiplier = idm
            target_row[a] = vol_scalar * f / 10.0 * multiplier

        long_total = target_row.sum()
        if long_total > 1.0:
            target_row *= 1.0 / long_total
        target_row[off_asset] = max(0.0, 1.0 - target_row.sum())

        for a in assets:
            if abs(target_row[a] - prev_positions[a]) < position_inertia * abs(target_row[a]):
                target_row[a] = prev_positions[a]

        s = target_row.sum()
        if s > 0:
            target_row /= s

        positions.loc[date] = target_row
        prev_positions = target_row.copy()

    return positions
```

- [ ] **Step 4: Run new + existing vol_targeted tests**

```
uv run pytest studies/letf_rotation_hunt/tests/test_vol_targeted_external_weights.py studies/letf_rotation_hunt/tests/ -k "vol_targeted" -v
```
Expected: All PASS — 2 new + any pre-existing T5 tests still passing.

- [ ] **Step 5: Run full T5 baseline regression**

```
uv run pytest studies/letf_rotation_hunt/tests/ -v
```
Expected: All PASS, no regressions.

- [ ] **Step 6: Commit**

```
git add studies/letf_rotation_hunt/strategies/vol_targeted.py studies/letf_rotation_hunt/tests/test_vol_targeted_external_weights.py
git commit -m "feat(letf-t5): add external_weights param to build_positions for HRP/ERC"
```

---

### Task 10: `run_iter_t5_extended` dispatcher

**Files:**
- Create: `studies/letf_rotation_hunt/run_iter_t5_extended.py`
- Test: `studies/letf_rotation_hunt/tests/test_run_iter_t5_extended.py`

- [ ] **Step 1: Write failing test (backward compat)**

```python
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
        "tier": "T5a",
        "configs_tested": [_minimal_config("baseline")],
        "datasets": ["lh_56y"],
        "cumulative_n_trials_at_iter": 0,
    }
    verdict_a: dict = {"results": []}
    verdict_b: dict = {"results": []}
    run_iter_t5.run(cfg, verdict_a, tmp_path / "a")
    run_iter_t5_extended.run(cfg, verdict_b, tmp_path / "b")
    sharpe_a = verdict_a["results"][0]["metrics_gross"]["lh_56y"]["sharpe"]
    sharpe_b = verdict_b["results"][0]["metrics_gross"]["lh_56y"]["sharpe"]
    assert abs(sharpe_a - sharpe_b) < 1e-9, (sharpe_a, sharpe_b)
```

- [ ] **Step 2: Run, verify fail**

Expected: ModuleNotFoundError on `run_iter_t5_extended`.

- [ ] **Step 3: Implement extended dispatcher**

```python
# studies/letf_rotation_hunt/run_iter_t5_extended.py
"""Extended T5 dispatcher with forecast_type and weighting_scheme.

Routes per-config based on optional keys:
  - forecast_type ∈ {"ewmac", "ewmac_carry", "carry_only"} (default "ewmac")
  - weighting_scheme ∈ {"idm", "hrp", "erc"} (default "idm")

When both default, behavior is identical to run_iter_t5._run_single_voltarget_config.
Citation: spec §3.4 (docs/specs/2026-05-08-t5-expansion-design.md).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt import run_iter_t5, signals_carry
from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.gates import g1_pbo, g2_dsr_p_value
from studies.letf_rotation_hunt.run_iter_t1 import (
    DATASET_WINDOWS, LETF_TESTFOLIO, SPY_ANCHOR_SHARPE, SPY_MDD,
    _NAN_METRICS, _write_iter_artifacts,
)
from studies.letf_rotation_hunt.run_iter_t5 import (
    _compute_ewmac_composite_forecast, _resolve_asset_returns,
    _run_single_voltarget_config,
)
from studies.letf_rotation_hunt.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.strategies.hrp_weighter import (
    compute_erc_weights, compute_hrp_weights,
)
from studies.letf_rotation_hunt.strategies.vol_targeted import build_positions


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Mirror of run_iter_t5.run with extended config keys."""
    tier = config["tier"]
    if not tier.startswith("T5"):
        raise ValueError(f"run_iter_t5_extended expects T5*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            if _is_extended_config(cfg):
                result = _run_single_extended(
                    cfg, config["datasets"], ffr_daily,
                    n_trials_local=n_trials_local,
                )
            else:
                result = _run_single_voltarget_config(
                    cfg, config["datasets"], ffr_daily,
                    n_trials_local=n_trials_local,
                )
            results.append(result)
        except Exception as exc:
            results.append({
                "config_name": cfg.get("name", "unknown"),
                "error": str(exc),
                "metrics_gross": {}, "metrics_net": {},
                "score_breakdown": {}, "tier_label": "ERROR",
            })

    valid = [r for r in results if "error" not in r]
    per_cfg_returns = {
        r["config_name"]: r["_strategy_returns"]
        for r in valid if "_strategy_returns" in r
    }
    g1_result = g1_pbo(per_cfg_returns) if per_cfg_returns else {
        "pbo": float("nan"), "n_combinations": 0, "pass_gate": True,
    }
    for r in valid:
        r["gates"]["g1_pbo"] = float(g1_result["pbo"])
        r["gates"]["g1_pbo_n_combinations"] = int(g1_result["n_combinations"])
        if "_strategy_returns" in r:
            g2_cum = g2_dsr_p_value(
                r["_strategy_returns"], n_trials=max(2, n_trials_cumulative),
            )
            r["gates"]["g2_dsr_p_cumulative"] = float(g2_cum["p_value"])
        cached = r.pop("_score_inputs")
        score = score_strategy(
            cached["metrics"], cached["anchors"], cached["spy_mdds"],
            r["gates"], cached["crisis"],
        )
        r["score_breakdown"] = score
        r["tier_label"] = score["tier_label"]
        r["winner_conditions_met"] = bool(score.get("winner_conditions_met", False))

    if not valid:
        verdict.update({"best_config": "", "best_score": 0.0, "best_tier": "FAIL"})
    else:
        best = max(
            valid,
            key=lambda r: r["metrics_gross"].get("lh_56y", {}).get("sharpe", -999),
        )
        verdict.update({
            "best_config": best["config_name"],
            "best_score": best.get("score_breakdown", {}).get("total", 0.0),
            "best_tier": best.get("tier_label", "FAIL"),
        })

    verdict["kill_rule_status"] = run_iter_t5._evaluate_kill_t4_t5(valid)
    verdict["advance_to_next_tier"] = False

    if valid:
        _write_iter_artifacts(config, verdict, valid, out_dir, verdict["kill_rule_status"])

    for r in valid:
        for k in ("_strategy_returns", "_equity", "_signal", "_positions",
                  "_asset_returns_aligned"):
            r.pop(k, None)

    verdict["results"] = results
    return verdict


def _is_extended_config(cfg: dict) -> bool:
    return ("forecast_type" in cfg) or ("weighting_scheme" in cfg)


def _run_single_extended(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    forecast_type = cfg.get("forecast_type", "ewmac")
    weighting_scheme = cfg.get("weighting_scheme", "idm")
    name = cfg["name"]
    pool = cfg["pool"]
    off_asset = cfg["off_asset"]
    sigma_target = float(cfg.get("sigma_target", 0.25))
    idm = float(cfg.get("idm", 1.0))
    position_inertia = float(cfg.get("position_inertia", 0.10))
    vol_window = int(cfg.get("vol_window", 21))

    asset_returns: dict[str, pd.Series] = {}
    asset_prices: dict[str, pd.Series] = {}
    for a in list(pool) + [off_asset]:
        rets, pr = _resolve_asset_returns(a, ffr_daily)
        asset_returns[a] = rets
        asset_prices[a] = pr

    forecasts_dict: dict[str, pd.Series] = {}
    vols_dict: dict[str, pd.Series] = {}
    for a in pool:
        forecasts_dict[a] = _compute_forecast(
            forecast_type, a, asset_prices[a], ffr_daily,
        )
        vols_dict[a] = asset_returns[a].rolling(window=vol_window, min_periods=vol_window).std()

    forecasts_df = pd.DataFrame(forecasts_dict)
    vols_df = pd.DataFrame(vols_dict)
    common_idx = forecasts_df.dropna(how="all").index.intersection(
        vols_df.dropna(how="all").index
    )
    forecasts_df = forecasts_df.loc[common_idx]
    vols_df = vols_df.loc[common_idx]

    external_weights = _compute_external_weights(
        weighting_scheme, asset_returns, pool, common_idx,
    )

    positions = build_positions(
        forecasts=forecasts_df, vol_per_asset=vols_df,
        sigma_target=sigma_target, idm=idm,
        position_inertia=position_inertia, off_asset=off_asset,
        external_weights=external_weights,
    )

    # Reuse the rest of run_iter_t5 single-config metrics/gates pipeline
    # by manually replicating the scoring tail (cannot import as it lives
    # inline in _run_single_voltarget_config). The simplest reliable path:
    # delegate to the baseline _run_single_voltarget_config helper for
    # metrics, but pass our pre-built positions via a thin shim.
    return _finalize_extended(
        cfg, positions, asset_returns, datasets, n_trials_local, name, pool,
        sigma_target, idm,
    )


def _compute_forecast(
    forecast_type: str, asset: str, prices: pd.Series, ffr_daily: pd.Series,
) -> pd.Series:
    if forecast_type == "ewmac":
        return _compute_ewmac_composite_forecast(prices, fdm=1.41)
    if forecast_type == "carry_only":
        return signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
    if forecast_type == "ewmac_carry":
        ewmac = _compute_ewmac_composite_forecast(prices, fdm=1.0)
        carry = signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
        return signals_carry.compose_ewmac_carry(ewmac, carry, fdm=1.41)
    raise ValueError(f"unknown forecast_type {forecast_type!r}")


def _compute_external_weights(
    scheme: str, asset_returns: dict[str, pd.Series], pool: list[str],
    common_idx: pd.Index,
) -> pd.DataFrame | None:
    if scheme == "idm":
        return None
    rets = pd.DataFrame({a: asset_returns[a] for a in pool}).reindex(common_idx).dropna()
    if scheme == "hrp":
        return compute_hrp_weights(rets)
    if scheme == "erc":
        return compute_erc_weights(rets)
    raise ValueError(f"unknown weighting_scheme {scheme!r}")


def _finalize_extended(
    cfg, positions, asset_returns, datasets, n_trials_local, name, pool,
    sigma_target, idm,
):
    """Tail of metrics/gates/scoring; replicates the latter half of
    run_iter_t5._run_single_voltarget_config for our pre-built positions.
    """
    from studies.letf_rotation_hunt.gates import (
        g3_walk_forward, g4_oos_70_30, g5_fwd_post_2020,
        g6_bootstrap_ci, g7_xlib_cagr_delta,
    )

    asset_returns_df = pd.DataFrame(
        {c: asset_returns[c] for c in positions.columns}
    )
    aligned = positions.join(
        asset_returns_df, lsuffix="_w", rsuffix="_r", how="inner",
    ).dropna()
    if len(aligned) < 252:
        raise ValueError(f"Insufficient aligned data: {len(aligned)} for {name!r}")

    cols = positions.columns.tolist()
    strategy_returns = sum(
        aligned[f"{c}_w"].shift(1) * aligned[f"{c}_r"] for c in cols
    ).dropna()
    equity = (1.0 + strategy_returns).cumprod() * 10_000.0

    spy_full = load_testfolio_series("SPYSIM").dropna()
    metrics_per_dataset: dict[str, dict] = {}
    for ds in datasets:
        win = DATASET_WINDOWS.get(ds)
        if win is None:
            ds_eq, ds_ret, ds_bench = equity, strategy_returns, spy_full
        else:
            start, end = win
            ds_eq = equity[(equity.index >= start) & (equity.index <= end)]
            ds_ret = strategy_returns[(strategy_returns.index >= start) & (strategy_returns.index <= end)]
            ds_bench = spy_full[(spy_full.index >= start) & (spy_full.index <= end)]
        if len(ds_ret) < 252 or len(ds_eq) < 2:
            metrics_per_dataset[ds] = dict(_NAN_METRICS)
        else:
            metrics_per_dataset[ds] = compute_metrics(ds_eq, ds_ret, benchmark_equity=ds_bench)

    g2 = g2_dsr_p_value(strategy_returns, n_trials=max(2, n_trials_local))
    spy_returns_full = spy_full.pct_change().dropna()
    g3 = g3_walk_forward(strategy_returns, benchmark_returns=spy_returns_full)
    g4 = g4_oos_70_30(strategy_returns)
    g5 = g5_fwd_post_2020(strategy_returns)
    g6 = g6_bootstrap_ci(strategy_returns)
    g7 = g7_xlib_cagr_delta(strategy_returns)
    gates = {
        "g1_pbo": float("nan"), "g1_pbo_n_combinations": 0,
        "g2_dsr_p_local": float(g2["p_value"]),
        "g2_dsr_p_cumulative": float("nan"),
        "g2_observed_sharpe": float(g2["observed_sharpe"]),
        "g3_wf_windows_pass": int(g3["windows_pass"]),
        "g3_wf_windows_pass_pct_above_benchmark": int(g3["windows_pass_pct_above_benchmark"]),
        "g3_wf_windows_pass_sharpe_positive": int(g3["windows_pass_sharpe_positive"]),
        "g3_wf_n_windows": int(g3["n_windows"]),
        "g3_wf_max_mdd": float(g3["max_mdd"]) if not pd.isna(g3["max_mdd"]) else float("nan"),
        "g3_wf_warmup_used_days": int(g3.get("warmup_used_days", 0)),
        "g3_wf_benchmark_relative": bool(g3.get("benchmark_relative", False)),
        "g4_oos_sharpe": float(g4["oos_sharpe"]),
        "g5_fwd_post2020_sharpe": float(g5["fwd_sharpe"]),
        "g5_fwd_n_obs": int(g5["n_obs_post_2020"]),
        "g6_bootstrap_99_low": float(g6["ci_low_sharpe"]),
        "g7_xlib_cagr_delta": float(g7["delta_pp"] / 100.0),
    }
    crisis = crisis_beats_benchmark(equity, spy_full)
    anchors = {ds: SPY_ANCHOR_SHARPE.get(ds, 0.7) for ds in datasets}
    spy_mdds = {ds: SPY_MDD.get(ds, -0.50) for ds in datasets}
    score_result = score_strategy(metrics_per_dataset, anchors, spy_mdds, gates, crisis)
    pool_weights = positions[pool].sum(axis=1)
    signal_idx = pool_weights.reindex(strategy_returns.index).fillna(0).astype(float)
    asset_returns_aligned = pd.DataFrame(
        {c: aligned[f"{c}_r"] for c in positions.columns}
    ).reindex(strategy_returns.index).dropna()
    positions_aligned = positions.reindex(strategy_returns.index).dropna()
    return {
        "config_name": name,
        "metrics_gross": metrics_per_dataset, "metrics_net": {},
        "rolling_pct_beat_spy": {"3y": None, "5y": None, "10y": None},
        "crisis_mdd": {}, "crisis_beats_benchmark": dict(crisis),
        "gates": gates,
        "score_breakdown": score_result,
        "tier_label": score_result["tier_label"],
        "winner_conditions_met": score_result.get("winner_conditions_met", False),
        "pool": list(pool), "sigma_target": sigma_target, "idm": idm,
        "_positions": positions_aligned,
        "_asset_returns_aligned": asset_returns_aligned,
        "_strategy_returns": strategy_returns,
        "_equity": equity, "_signal": signal_idx,
        "_score_inputs": {
            "metrics": metrics_per_dataset, "anchors": anchors,
            "spy_mdds": spy_mdds, "crisis": crisis,
        },
    }
```

- [ ] **Step 4: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_run_iter_t5_extended.py -v
```
Expected: 1 PASS (backward-compat test).

- [ ] **Step 5: Add forecast/weighting test**

Append:

```python
def test_extended_carry_only_runs(tmp_path):
    cfg = {
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
```

Run:
```
uv run pytest studies/letf_rotation_hunt/tests/test_run_iter_t5_extended.py -v
```
Expected: 3 PASS.

- [ ] **Step 6: Commit**

```
git add studies/letf_rotation_hunt/run_iter_t5_extended.py studies/letf_rotation_hunt/tests/test_run_iter_t5_extended.py
git commit -m "feat(letf-t5): add extended dispatcher with forecast_type and weighting_scheme"
```

---

### Task 11: Calibrate carry scalars empirically

**Files:**
- Create: `scripts/calibrate_carry_scalars.py`
- Modify: `studies/letf_rotation_hunt/signals_carry.py:36-40` (`_CARRY_SCALAR_BY_CLASS`)

- [ ] **Step 1: Write calibration script**

```python
# scripts/calibrate_carry_scalars.py
"""Calibrate _CARRY_SCALAR_BY_CLASS per Carver [systematic_trading, ch.9 p.183].

Target: carry forecast SD = 10 over the full lh_56y window.
For each class (equity, bond), compute the median SD of (carry_raw / rolling_std)
across representative assets, then scalar = 10.0 / median_sd.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt import signals_carry as sc
from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series


CALIBRATION_ASSETS_BY_CLASS: dict[str, list[str]] = {
    "equity": ["UPRO", "QLD"],
    "bond": ["TMF"],
}


def main() -> None:
    ffr = load_ffr_daily()
    suggested: dict[str, float] = {"gold": 0.0}
    for cls, assets in CALIBRATION_ASSETS_BY_CLASS.items():
        sds: list[float] = []
        for a in assets:
            tf_ticker, _ = sc._ASSET_CARRY_MAP[a].yield_kind, None  # noqa
            # Build raw normalized signal with scalar=1, fdm=1, then measure SD
            prices = load_testfolio_series("SPYSIM" if a == "UPRO" else
                                            "NDXSIM" if a in ("QLD", "TQQQ") else
                                            "ZROZSIM").dropna()
            yield_series = sc._load_yield_for_asset(a).reindex(prices.index).ffill()
            ffr_annual = sc._ffr_daily_to_annual(ffr).reindex(prices.index).ffill()
            cfg = sc._ASSET_CARRY_MAP[a]
            carry_raw = yield_series - cfg.leverage * ffr_annual
            carry_std = carry_raw.rolling(252, min_periods=126).std()
            normalized = (carry_raw / carry_std).dropna()
            sds.append(float(normalized.std()))
        median_sd = float(np.median(sds))
        scalar = 10.0 / median_sd if median_sd > 0 else 10.0
        suggested[cls] = round(scalar, 4)
        print(f"{cls}: median SD={median_sd:.4f} → scalar={scalar:.4f}")
    print("\nSuggested _CARRY_SCALAR_BY_CLASS:")
    for k, v in suggested.items():
        print(f"  {k!r}: {v},")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run calibration**

```
uv run python scripts/calibrate_carry_scalars.py
```
Expected: prints per-class SDs and suggested scalar values. Sample output:
```
equity: median SD=0.95 → scalar=10.5263
bond: median SD=1.02 → scalar=9.8039
Suggested _CARRY_SCALAR_BY_CLASS:
  'gold': 0.0,
  'equity': 10.5263,
  'bond': 9.8039,
```

- [ ] **Step 3: Update `_CARRY_SCALAR_BY_CLASS` with empirical values**

Edit `studies/letf_rotation_hunt/signals_carry.py:36-40` replacing:

```python
_CARRY_SCALAR_BY_CLASS: dict[str, float] = {
    "equity": 10.0,
    "bond": 10.0,
    "gold": 0.0,
}
```

with values from Step 2 output (concrete numbers, not placeholders). Add a comment:

```python
# Empirically calibrated 2026-05-08 via scripts/calibrate_carry_scalars.py
# Target: carry forecast SD ≈ 10 (Carver convention).
_CARRY_SCALAR_BY_CLASS: dict[str, float] = {
    "equity": <value_from_step_2>,
    "bond": <value_from_step_2>,
    "gold": 0.0,
}
```

- [ ] **Step 4: Re-run carry tests with new scalars**

```
uv run pytest studies/letf_rotation_hunt/tests/test_signals_carry.py -v
```
Expected: All 8 still PASS (sign tests are scalar-invariant; clipping test still bounded by ±20).

- [ ] **Step 5: Commit**

```
git add scripts/calibrate_carry_scalars.py studies/letf_rotation_hunt/signals_carry.py
git commit -m "feat(letf-t5): calibrate carry scalars per Carver SD≈10 convention"
```

---

### Task 12: Configs iter_022..025 + dispatch hookup

**Files:**
- Create: `studies/letf_rotation_hunt/configs/iter_022_t5a_sigma_sweep.yaml`
- Create: `studies/letf_rotation_hunt/configs/iter_023_t5b_carry.yaml`
- Create: `studies/letf_rotation_hunt/configs/iter_024_t5c_grid.yaml`
- Create: `studies/letf_rotation_hunt/configs/iter_025_t5d_hrp_erc.yaml`
- Modify: `studies/letf_rotation_hunt/run_iter.py` (or wherever tier dispatch lives)

- [ ] **Step 1: Locate dispatch router**

```
grep -rn "run_iter_t5\|tier.startswith\|T5a\|T5b" studies/letf_rotation_hunt/run_iter.py studies/letf_rotation_hunt/run_loop.sh 2>/dev/null
```
Read the matched file to find where tier-string → dispatcher mapping happens.

- [ ] **Step 2: Add T5b/T5d dispatch + extended override**

In the dispatch logic, add:

```python
# Use extended dispatcher when config has forecast_type or weighting_scheme,
# OR when tier is T5b/T5d (always extended).
def _select_t5_dispatcher(config: dict):
    tier = config.get("tier", "")
    has_extended_keys = any(
        ("forecast_type" in c) or ("weighting_scheme" in c)
        for c in config.get("configs_tested", [])
    )
    if tier in {"T5b", "T5d"} or has_extended_keys:
        from studies.letf_rotation_hunt import run_iter_t5_extended
        return run_iter_t5_extended.run
    from studies.letf_rotation_hunt import run_iter_t5
    return run_iter_t5.run
```

Wire this where the existing `run_iter_t5.run` is selected for T5* tiers.

- [ ] **Step 3: Write the 4 YAML configs**

Create `iter_022_t5a_sigma_sweep.yaml` (5 configs), `iter_023_t5b_carry.yaml` (4 configs), `iter_024_t5c_grid.yaml` (7 configs), `iter_025_t5d_hrp_erc.yaml` (4 configs) — exact contents per spec §4.1-§4.4.

(Engineer: copy each YAML block from `docs/specs/2026-05-08-t5-expansion-design.md` §4 verbatim.)

- [ ] **Step 4: Smoke-validate iter_022 end-to-end (smallest config first)**

```
uv run python -m studies.letf_rotation_hunt.run_iter --iter 022 --config studies/letf_rotation_hunt/configs/iter_022_t5a_sigma_sweep.yaml 2>&1 | tail -30
```
The project's `run_iter` requires both `--iter NNN` and `--config <path>` (no dry-run mode).
Expected: 5 configs processed under `iterations/022-2026-05-08-T5a-sigma-sweep/`, verdict.json + SUMMARY.md present, no Python tracebacks.

- [ ] **Step 5: Commit configs + dispatcher wiring**

```
git add studies/letf_rotation_hunt/configs/iter_022_t5a_sigma_sweep.yaml \
        studies/letf_rotation_hunt/configs/iter_023_t5b_carry.yaml \
        studies/letf_rotation_hunt/configs/iter_024_t5c_grid.yaml \
        studies/letf_rotation_hunt/configs/iter_025_t5d_hrp_erc.yaml \
        studies/letf_rotation_hunt/run_iter.py
git commit -m "feat(letf-t5): add iter_022-025 configs (T5a-grid, T5b, T5c-grid, T5d)"
```

---

### Task 13: `scripts/dsr_recompute_cumulative.py`

**Files:**
- Create: `scripts/dsr_recompute_cumulative.py`
- Test: `studies/letf_rotation_hunt/tests/test_dsr_recompute_cumulative.py`

- [ ] **Step 1: Write failing test**

```python
# studies/letf_rotation_hunt/tests/test_dsr_recompute_cumulative.py
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
```

- [ ] **Step 2: Run, verify fail**

Expected: ModuleNotFoundError on `scripts.dsr_recompute_cumulative`.

- [ ] **Step 3: Implement script**

```python
# scripts/dsr_recompute_cumulative.py
"""Re-compute G2 DSR p-value cumulative across all study iterations.

Trigger: after T5 expansion (iter_025) completes, n_trials_cumulative
becomes 426. Walks every iter directory, reads stored strategy_returns,
re-runs g2_dsr_p_value with new N, and writes back under a v2 key.

Citation: spec §5.3 (docs/specs/2026-05-08-t5-expansion-design.md);
[advances_fin_ml, p.208-211].
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt.gates import g2_dsr_p_value

logger = logging.getLogger(__name__)


def recompute_all(
    iters_root: Path, n_trials_new: int,
    v2_key: str = "g2_dsr_p_cumulative_v2_post_t5_expansion",
) -> dict[str, dict]:
    """Walk every iter dir under iters_root, recompute G2 cumulative.

    Returns a dict {iter_name: {config_name: {old_p, new_p, flipped}}}.
    Writes new key into verdict.json in place; preserves old keys.
    """
    summary: dict[str, dict] = {}
    for iter_dir in sorted(iters_root.iterdir()):
        if not iter_dir.is_dir():
            continue
        verdict_path = iter_dir / "verdict.json"
        if not verdict_path.exists():
            continue
        verdict = json.loads(verdict_path.read_text())
        iter_summary: dict = {}
        changed = False
        for r in verdict.get("results", []):
            csv_rel = r.get("_strategy_returns_csv")
            if not csv_rel:
                continue
            rets = pd.read_csv(iter_dir / csv_rel, index_col=0)["ret"]
            new_p = float(g2_dsr_p_value(rets, n_trials=n_trials_new)["p_value"])
            old_p = float(r.get("gates", {}).get("g2_dsr_p_cumulative", float("nan")))
            r.setdefault("gates", {})[v2_key] = new_p
            iter_summary[r.get("config_name", "?")] = {
                "old_p": old_p, "new_p": new_p,
                "flipped_to_fail": (old_p < 0.05) and (new_p >= 0.05),
            }
            changed = True
        if changed:
            verdict_path.write_text(json.dumps(verdict, indent=2))
        if iter_summary:
            summary[iter_dir.name] = iter_summary
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters-root", type=Path,
                        default=Path("studies/letf_rotation_hunt/iterations"))
    parser.add_argument("--n-trials-new", type=int, required=True)
    args = parser.parse_args()
    summary = recompute_all(args.iters_root, args.n_trials_new)
    flipped = [
        f"{i}/{c}" for i, configs in summary.items()
        for c, info in configs.items() if info["flipped_to_fail"]
    ]
    print(f"Re-computed DSR for {sum(len(v) for v in summary.values())} configs.")
    if flipped:
        print(f"⚠ {len(flipped)} configs flipped PASS→FAIL: {flipped[:10]}")
    else:
        print("No configs flipped PASS→FAIL.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run, verify pass**

```
uv run pytest studies/letf_rotation_hunt/tests/test_dsr_recompute_cumulative.py -v
```
Expected: 1 PASS.

- [ ] **Step 5: Commit**

```
git add scripts/dsr_recompute_cumulative.py studies/letf_rotation_hunt/tests/test_dsr_recompute_cumulative.py
git commit -m "feat(letf-t5): add DSR cumulative re-computation script"
```

---

### Task 14: End-to-end run + acceptance gate

**Files:**
- Run-only (writes to `studies/letf_rotation_hunt/iterations/`).

- [ ] **Step 1: Run iter_022 (T5a sigma sweep)**

```
uv run python -m studies.letf_rotation_hunt.run_iter --iter 022 --config studies/letf_rotation_hunt/configs/iter_022_t5a_sigma_sweep.yaml 2>&1 | tee logs/iter_022_run.log
```
Expected: 5 configs processed; verdict.json + SUMMARY.md written under `iterations/022-2026-05-08-T5a-sigma-sweep/`.

- [ ] **Step 2: Run iter_023 (T5b carry)**

```
uv run python -m studies.letf_rotation_hunt.run_iter --iter 023 --config studies/letf_rotation_hunt/configs/iter_023_t5b_carry.yaml 2>&1 | tee logs/iter_023_run.log
```
Expected: 4 configs processed.

- [ ] **Step 3: Run iter_024 (T5c grid)**

```
uv run python -m studies.letf_rotation_hunt.run_iter --iter 024 --config studies/letf_rotation_hunt/configs/iter_024_t5c_grid.yaml 2>&1 | tee logs/iter_024_run.log
```
Expected: 7 configs processed.

- [ ] **Step 4: Run iter_025 (T5d HRP/ERC)**

```
uv run python -m studies.letf_rotation_hunt.run_iter --iter 025 --config studies/letf_rotation_hunt/configs/iter_025_t5d_hrp_erc.yaml 2>&1 | tee logs/iter_025_run.log
```
Expected: 4 configs processed.

- [ ] **Step 5: Run DSR recomputation across all 426 configs**

```
uv run python scripts/dsr_recompute_cumulative.py --n-trials-new 426 2>&1 | tee logs/dsr_recompute.log
```
Expected output ends with either "No configs flipped PASS→FAIL." (acceptance pass) or "⚠ N configs flipped..." (acceptance fail).

- [ ] **Step 6: Acceptance gate — Track A winner check**

```
uv run python -c "
import json
from pathlib import Path
target = 'qld_voteK2_sma250_100_vol21_40_ar30_off_zroz'
for d in Path('studies/letf_rotation_hunt/iterations').iterdir():
    vp = d / 'verdict.json'
    if not vp.exists():
        continue
    v = json.loads(vp.read_text())
    for r in v.get('results', []):
        if r.get('config_name') == target:
            new_p = r['gates'].get('g2_dsr_p_cumulative_v2_post_t5_expansion')
            print(f'{d.name}: new_p={new_p}')
            assert new_p < 0.05, f'ACCEPTANCE FAIL: Track A winner DSR p={new_p} ≥ 0.05'
            print('ACCEPTANCE PASS')
"
```
Expected: prints `ACCEPTANCE PASS`. **If FAIL: stop and surface to user before any further commits.** (Per spec §5.3: "If Track A winner does not remain PASS, the expansion is documented as having invalidated the canonical winner and the user is asked to re-evaluate before any further work.")

- [ ] **Step 7: Commit run artifacts**

```
git add studies/letf_rotation_hunt/iterations/022-2026-05-08-T5a-sigma-sweep/ \
        studies/letf_rotation_hunt/iterations/023-2026-05-08-T5b-carry/ \
        studies/letf_rotation_hunt/iterations/024-2026-05-08-T5c-grid/ \
        studies/letf_rotation_hunt/iterations/025-2026-05-08-T5d-hrp-erc/ \
        logs/iter_022_run.log logs/iter_023_run.log logs/iter_024_run.log logs/iter_025_run.log logs/dsr_recompute.log
git commit -m "data(letf-t5): run iter_022-025 + DSR cumulative recompute (N=426)"
```

---

### Task 15: Reports amendment + CURRENT_STATE update

**Files:**
- Modify: `studies/letf_rotation_hunt/reports/TIER_5_REPORT.md`
- Modify: `studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md`
- Modify: `docs/CURRENT_STATE.md`
- Modify: `docs/PROJECT_HISTORY.md` (only if the expansion materially changes the public narrative)

- [ ] **Step 1: Add post-close note to `TIER_5_REPORT.md`**

Read current top of the file (lines 1-20) and insert immediately after the existing `> ## ⚠️ Post-close Sortino re-analysis update (2026-05-07)` block:

```markdown
> ## ⚠️ Post-close T5 expansion (2026-05-08)
>
> Original T5 ran 2 configs (iters 020-021). Sub-phases T5b (carry) and
> T5d (HRP) were skipped per scope. After post-close review, T5 was
> reopened with a formal methodology amendment to add 20 new configs
> across iters 022-025. See §17 of `STUDY_FINAL_REPORT.md` for the full
> disclosure.
>
> **Verdict update:** [fill from acceptance gate output: T5-expansion-best
> Sortino = X vs threshold 1.272 → KILL T5-expansion {FIRES|PASSES}.
> Track A canonical winner G2 DSR p_v2 = Y < 0.05 → PASS]
>
> **Body of report below preserved as-is for historical fidelity.**
```

Replace `[fill from acceptance gate output ...]` with the actual numbers from Task 14 logs.

- [ ] **Step 2: Add §17 to `STUDY_FINAL_REPORT.md`**

Append a new section following the same shape as §14, §15, §16. Required sub-sections:

- 17.1 Trigger and rationale (cite this spec, link to `docs/specs/2026-05-08-t5-expansion-design.md`)
- 17.2 What was added (the 20 configs across 4 iters)
- 17.3 Cumulative DSR impact (N: 406 → 426, list any flipped configs from Task 14 log; 0 if acceptance passed)
- 17.4 T5-expansion verdict (best config + Sortino + KILL outcome)
- 17.5 Updated cross-tier comparison table (extend §2 table with new T5-expansion row)
- 17.6 Mandate alignment (explicit statement: capital 100% Plano C unchanged; Strategy B DORMANT unchanged)
- 17.7 Closing — does the T3d K=2 winner still stand?

- [ ] **Step 3: Update `docs/CURRENT_STATE.md`**

Add a bullet under whatever the current "active work" or "history" section is (per CLAUDE.md Regra 1):

```markdown
- **2026-05-08 — T5 expansion of letf_rotation_hunt** (post-close
  methodology amendment). Added 20 configs across iters 022-025
  (T5a-grid, T5b carry, T5c-grid, T5d HRP/ERC). DSR cumulative
  re-computed for all 426 configs. Track A canonical winner retained.
  Spec: `docs/specs/2026-05-08-t5-expansion-design.md`; §17 disclosure
  in `studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md`.
```

- [ ] **Step 4: PROJECT_HISTORY.md (conditional)**

Only update if the expansion materially changed the narrative (e.g., if Track A winner had flipped). If acceptance passed without flips → skip this step (per CLAUDE.md Regra 1: "Não conta: refactor interno, conteúdo que não muda o entendimento público do projeto"). The §17 disclosure is sufficient.

- [ ] **Step 5: Run full test suite — final regression check**

```
uv run pytest -q
```
Expected: 813 baseline + new tests (≥18 added across Tasks 1-13) all PASS.

- [ ] **Step 6: Commit reports**

```
git add studies/letf_rotation_hunt/reports/TIER_5_REPORT.md \
        studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md \
        docs/CURRENT_STATE.md
git commit -m "docs(letf-t5): amend study reports with T5 expansion §17 disclosure"
```

---

## Self-Review Checklist (run before handing off plan)

- [ ] Spec coverage: every §1-§11 of `docs/specs/2026-05-08-t5-expansion-design.md` has at least one task implementing it.
- [ ] No placeholders in step bodies (TBD/TODO/etc.). Step 1 of Task 15 contains an intentional `[fill from acceptance gate output...]` — that's a runtime substitution from Task 14's output, not a plan-writing placeholder, and it's the only one.
- [ ] Type/name consistency: `compute_carry_forecast`, `compose_ewmac_carry`, `compute_hrp_weights`, `compute_erc_weights`, `_CARRY_SCALAR_BY_CLASS`, `_ASSET_CARRY_MAP` referenced consistently across tasks.
- [ ] Frequent commits: 14 logical commits across the plan (one per task, plus Task 11 which has its own).

---

## Out of scope (do NOT implement)

- T1/T2/T3/T4 expansion or re-execution.
- Live deployment / mandate §1 changes.
- New gates beyond G1-G7.
- Strategy A/D work.
