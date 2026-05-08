# spy_beater_hunt — Infrastructure (reuse from long_term_portfolio)

**Principle**: don't rebuild what works. Reuse + extend.

---

## Reused as-is from `studies/long_term_portfolio/`

### Synth functions — `synths.py`

```python
from studies.long_term_portfolio.synths import (
    ntsd_synth_returns_from_cache,
    avuv_synth_returns_from_cache,
    avdv_synth_returns_from_cache,
    avem_synth_returns_from_cache,
    spmo_synth_returns_from_cache,
    idmo_synth_returns_from_cache,
    rsst_synth_returns_from_cache,
    dbmf_returns_from_cache,
)
```

15 tests passing in `tests/test_studies_long_term_portfolio_synths.py`.

### Proxies — `proxies.py`

NTSX/NTSI/NTSE synth via `PROXY_LEGS` blueprint. Used internally by run_iter.

### Per-iter execution helper — `run_iter.py`

```python
from studies.long_term_portfolio.run_iter import (
    portfolio_returns_from_config,
    run_iter_full,
)
```

`run_iter_full(iter_n, iter_dir, hypothesis_slug, primary_citation, configs, datasets_to_test, cumulative_n_trials)` produces verdict.json + final_report.md + plots.

**For spy_beater_hunt**: extend with CAGR-anchored scoring (see "New required modules" below).

### Datasets — `datasets.py`

```python
from studies.long_term_portfolio.datasets import load_prices, get_meta

prices_lh = load_prices("lh_56y")
prices_vt = load_prices("vt_real")
prices_ndx = load_prices("ndx_real")
```

### Plot helper — `plot_helper.py`

```python
from studies.long_term_portfolio.plot_helper import (
    plot_dataset,
    plot_rolling_windows,
)
```

Reads `results.json` from iter dir.

---

## NEW modules required for spy_beater_hunt

### 1. TMF synth (HFEA leveraged barbell)

Add to `studies/long_term_portfolio/synths.py` OR create `studies/spy_beater_hunt/synths_extras.py`:

```python
def tmf_synth_returns(
    tlt_returns: pd.Series,
    leverage: float = 3.0,
    daily_reset_decay_annual: float = 0.015,  # 1.5%/y
) -> pd.Series:
    """TMF synth: 3x LTT (TLT) with daily-reset decay.
    
    INCOMPLETE: real TMF (Direxion Daily 20+ Year Treasury Bull 3X) tracks
    daily 3x SPY TLT return; daily-reset decay ~1-2%/y depending on vol.
    
    Citation: [leverage_for_the_long_run, ch.3-4] LETF decay rationale.
    """
    daily_decay = daily_reset_decay_annual / 252
    return leverage * tlt_returns - daily_decay


def tmf_synth_returns_from_cache() -> pd.Series:
    """TMF synth from TLTSIM cache."""
    tlt = load_testfolio_series("TLTSIM").pct_change().dropna()
    return tmf_synth_returns(tlt)
```

### 2. LRS (Leveraged Rotation Strategy) engine — Gayed 200d SMA gate

Create `studies/spy_beater_hunt/lrs_engine.py`:

```python
"""Gayed LRS engine — 200d SMA gate on leveraged equity.

Citation: [leverage_for_the_long_run, ch.3-4, p.40-60].
"""
from __future__ import annotations
import pandas as pd


def gayed_200d_sma_gate(
    signal_prices: pd.Series,
    window: int = 200,
    lag_days: int = 1,
) -> pd.Series:
    """Generate boolean ON/OFF series based on 200d SMA gate.
    
    Args:
        signal_prices: prices to compute MA on (e.g. SPY total-return)
        window: SMA window (default 200 trading days)
        lag_days: T+1 execution lag to avoid peek-ahead
    
    Returns:
        bool Series (True = bullish regime, allocate to leveraged equity)
    """
    sma = signal_prices.rolling(window=window, min_periods=window).mean()
    on_off = signal_prices > sma
    return on_off.shift(lag_days).fillna(False)


def lrs_strategy_returns(
    on_returns: pd.Series,  # leveraged equity returns when ON (e.g. UPRO)
    off_returns: pd.Series,  # safe asset returns when OFF (e.g. IEF)
    gate: pd.Series,  # bool series from gayed_200d_sma_gate
) -> pd.Series:
    """Apply LRS gate to alternate between on/off return streams.
    
    Returns:
        Daily strategy returns.
    """
    aligned = pd.concat({"on": on_returns, "off": off_returns, "gate": gate}, axis=1).dropna()
    return aligned.apply(lambda row: row["on"] if row["gate"] else row["off"], axis=1)
```

TDD: test that gate doesn't peek ahead (signal at t-1 used for return at t).

### 3. CAGR-anchored scoring — `scoring.py` extension

Create `studies/spy_beater_hunt/scoring.py`:

```python
"""CAGR-anchored scoring for spy_beater_hunt.

Distinct from long_term_portfolio scoring (which is Sharpe-edge anchored).
"""
from __future__ import annotations

# SPY 3-dataset benchmark (from BASE_MEMORY.md)
SPY_CAGR_MEAN = 0.1380
SPY_MDD_MEAN = 0.4085
SPY_SHARPE_MEAN = 0.827

CAGR_BAR = SPY_CAGR_MEAN
MDD_BAR = SPY_MDD_MEAN


def score_strategy_spy_beater(metrics, gates, ...):
    """Score per WINNER_AND_RANKING.md rubric.
    
    Returns dict with 'status', 'tier', 'total_score', 'bars', 'criteria'.
    """
    # ... implement per WINNER_AND_RANKING.md spec
```

### 4. Stress period validation

Create `studies/spy_beater_hunt/stress_tests.py`:

```python
"""Stress period validation — 2008/2020/2022 critical regimes."""

STRESS_PERIODS = {
    "2008_gfc": ("2008-09-01", "2009-03-31"),
    "2020_covid": ("2020-02-15", "2020-04-30"),
    "2022_inflation": ("2022-01-01", "2022-12-31"),
    "2000_dotcom": ("2000-03-01", "2002-10-31"),
}

def stress_test_strategy(returns: pd.Series) -> dict:
    """For each stress period, compute total return + MDD."""
    # ...
```

---

## Loop runner

Create `studies/spy_beater_hunt/run_iter.py` (thin wrapper around long_term_portfolio's run_iter_full with spy_beater scoring):

```python
"""spy_beater_hunt per-iter execution helper.

Reuses studies.long_term_portfolio.run_iter for portfolio aggregation and
3-dataset evaluation; applies spy_beater-specific scoring/winner logic.
"""
from studies.long_term_portfolio.run_iter import (
    portfolio_returns_from_config,
    _resolve_tickers_to_returns,
)
from studies.spy_beater_hunt.scoring import score_strategy_spy_beater
# ... etc
```

---

## Bash command examples (next session)

```bash
cd /var/www/github/finances/market-lab
source .venv/bin/activate

# Verify foundation in place
ls studies/spy_beater_hunt/

# Run TDD on TMF synth (build first)
pytest tests/test_studies_spy_beater_synths.py -v

# Run iter 001 (A1 Gayed LRS UPRO)
python studies/spy_beater_hunt/iterations/001-2026-04-XX-A1-Gayed-LRS-UPRO/backtest.py
```

---

## Citations

- `[leverage_for_the_long_run, ch.3-4]` Gayed — LRS engine + LETF decay
- `[advances_fin_ml]` — gate framework (PBO/DSR/WF/Bootstrap)
- HFEA Bogleheads 2019 — TMF synth rationale
- `[risk_parity, ch.5]` — capital-efficient stacking baseline (long_term_portfolio incumbent fallback)
