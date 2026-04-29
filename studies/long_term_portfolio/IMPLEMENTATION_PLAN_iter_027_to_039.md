# Long-Term Portfolio Sweep Iter 027-039 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the 7-finalist portfolio sweep specified in `SWEEP_PLAN_iter_027_to_039.md`, producing FINAL_REPORT_seven_portfolios.md with multi-criteria scoring and a deploy-ready recommendation.

**Architecture:** Build a shared `synths.py` module for all 8 ETF synth functions (NTSD/AVUV/AVDV/AVEM/SPMO/IDMO/RSST/CTA-proxy), a `run_iter.py` helper that takes a config dict and runs backtest+gates+scoring+verdict on 3 datasets. Execute Phase 1 (single-axis isolation, 6 iters), Phase 2 (finalist construction, 6 iters), Phase 3 (MF sensitivity, 1 iter) sequentially with manual winner selection between phases. Final phase: aggregate all 7 finalists into a comparative report.

**Tech Stack:** Python 3.12, pytest, pandas/numpy, existing `scoring.py` + `datasets.py` + `proxies.py` + `ff_momentum_proxy.py` + `plot_helper.py`.

---

## File Structure

**New files:**
- `studies/long_term_portfolio/synths.py` — 8 synth functions (NTSD, AVUV, AVDV, AVEM, SPMO, IDMO, RSST, CTA proxy) + DBMF loader
- `studies/long_term_portfolio/run_iter.py` — per-iter execution helper (config → verdict.json + final_report.md + plots)
- `tests/test_studies_long_term_portfolio_synths.py` — TDD tests for synths
- `tests/test_studies_long_term_portfolio_run_iter.py` — TDD tests for run_iter helper
- `studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap/` through `038-2026-04-30-F7-US-StackedMF/` — 12 iter dirs (each with hypothesis.md, backtest.py, verdict.json, final_report.md, plots)
- `studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity/`
- `studies/long_term_portfolio/INTER_CHECK.md` — ETF availability check on Inter Internacional
- `studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md` — comparative report

**Modified files:**
- `studies/long_term_portfolio/BASE_MEMORY.md` — append iter result + frontmatter update after each iter
- `studies/long_term_portfolio/STRATEGY_ZOO.md` — append finalist rows
- `studies/long_term_portfolio/DEAD_ENDS.md` — append DE entries for failed sleeves

---

## Task 1: Inter Internacional ETF availability pre-check

**Files:**
- Create: `studies/long_term_portfolio/INTER_CHECK.md`

- [ ] **Step 1: Write the doc with all 16 target ETFs**

Create `studies/long_term_portfolio/INTER_CHECK.md`:

```markdown
# Inter Internacional ETF Availability Check
**Date:** 2026-04-29
**Purpose:** Verify deployability of all ETFs in the 7-finalist sweep before committing to backtests.

## Target ETFs

| Ticker | Used in finalists | Inter available? | AUM | TER | Notes |
|---|---|---|---|---|---|
| NTSX | F1, F3, F4, F6, F7 | ? | ~$1.7B | 0.20% | WisdomTree US 90/60 |
| NTSD | F4, F6 | ? | ~$1M | 0.35% | WisdomTree US+Intl 90/60, launched 2026-03-19 |
| GDE | F1, F2, F3, F4, F6, F7 | ? | ~$300M | 0.20% | WisdomTree S&P+Gold |
| KMLM | F1, F2, F3, F4, F5, F6, F7 | ? | ~$600M | 0.92% | KFA Mt Lucas MF |
| DBMF | iter 039 | ? | ~$3.2B | 0.85% | iMGP DBi MF |
| TLT | all finalists | ? | ~$60B | 0.15% | iShares 20+y Treasury |
| GLD | F2, F5 | ? | ~$60B | 0.40% | SPDR Gold |
| VTI | F2, F5 | ? | ~$400B | 0.03% | Vanguard Total US |
| VEA | F5 | ? | ~$130B | 0.05% | Vanguard FTSE Dev |
| VWO | F5 | ? | ~$80B | 0.08% | Vanguard FTSE EM |
| AVUV | F2, F3, F5, F6 | ? | ~$11B | 0.25% | Avantis US SCV |
| AVDV | F5, F6 | ? | ~$8B | 0.36% | Avantis Intl SCV |
| AVEM | F5, F6 | ? | ~$1.5B | 0.33% | Avantis EM |
| SPMO | F2, F3, F5, F6 | ? | ~$5B | 0.13% | Invesco S&P 500 Momentum |
| IDMO | F5, F6 | ? | ~$1B | 0.25% | Invesco Intl Momentum |
| RSST | F7 | ? | ~$400M | 0.98% | Return Stacked US+MF |

## How to fill
User logs into Inter Internacional account, searches each ticker, marks ✅/❌. Any ❌ in a finalist's components drops C7 deploy ease score for that finalist to 0.
```

- [ ] **Step 2: Ask user to fill availability column**

User logs into Inter Internacional, fills `Inter available?` column with ✅/❌ for each ticker. Save updated INTER_CHECK.md back. **This is a manual user action; do NOT proceed to Phase 2 until done.**

- [ ] **Step 3: Commit**

```bash
git add studies/long_term_portfolio/INTER_CHECK.md
git commit -m "docs(long_term_portfolio): add Inter Internacional ETF availability check pre-flight for sweep iter 027-039"
```

---

## Task 2: Bootstrap synths.py module

**Files:**
- Create: `studies/long_term_portfolio/synths.py`
- Create: `tests/test_studies_long_term_portfolio_synths.py`

- [ ] **Step 1: Write empty module with imports**

Create `studies/long_term_portfolio/synths.py`:

```python
"""Synthetic ETF returns for the long-term portfolio sweep iter 027-039.

All synths return pd.Series of daily returns (decimal, e.g. 0.0123 = +1.23%).
Each function citation links to a book or paper that justifies the formula.
INCOMPLETE flag in docstring means the synth makes simplifying assumptions
that should be disclosed in any iter's final_report.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.ai_trade.backtest.data.testfolio_loader import (
    load_testfolio_frame,
    load_testfolio_series,
)

TRADING_DAYS_PER_YEAR = 252


def _annual_drag_to_daily(annual_drag_decimal: float) -> float:
    """Convert annual drag in decimal form to daily multiplicative drag.

    e.g. 75bps/y = 0.0075 → 0.0075 / 252 ≈ 2.98e-5 daily.
    """
    return annual_drag_decimal / TRADING_DAYS_PER_YEAR
```

- [ ] **Step 2: Write the smoke test**

Create `tests/test_studies_long_term_portfolio_synths.py`:

```python
"""TDD tests for studies.long_term_portfolio.synths.

Each synth function gets:
- a smoke test (returns non-empty Series with DatetimeIndex)
- a formula test (sample input → sample output with known math)
- where applicable, a no-free-lunch sanity test (Sharpe should not be implausibly inflated)
"""
import numpy as np
import pandas as pd
import pytest

from studies.long_term_portfolio.synths import _annual_drag_to_daily


def test_annual_drag_to_daily_75bps():
    """75bps/y annual drag = 75/(252*10000) decimal/day."""
    result = _annual_drag_to_daily(0.0075)
    assert abs(result - 0.0000297619) < 1e-8
```

- [ ] **Step 3: Run test, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 1 passed.

- [ ] **Step 4: Commit**

```bash
git add studies/long_term_portfolio/synths.py tests/test_studies_long_term_portfolio_synths.py
git commit -m "feat(long_term_portfolio/synths): bootstrap synth module + annual-to-daily drag helper"
```

---

## Task 3: Implement NTSD synth

**Files:**
- Modify: `studies/long_term_portfolio/synths.py`
- Modify: `tests/test_studies_long_term_portfolio_synths.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_studies_long_term_portfolio_synths.py`:

```python
def test_ntsd_synth_formula():
    """NTSD = 0.90 × SPYSIM + 0.60 × VEASIM − (75bps/y / 252) per day.

    Sanity: on a sample day where SPYSIM_ret = 1.0% and VEASIM_ret = 0.5%,
    NTSD_ret ≈ 0.90 × 0.01 + 0.60 × 0.005 − 0.0075/252
    = 0.009 + 0.003 − 0.0000297619
    = 0.0119702381
    """
    from studies.long_term_portfolio.synths import ntsd_synth_returns

    spy = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    vea = pd.Series([0.005, 0.001, -0.002], index=pd.date_range("2024-01-02", periods=3, freq="B"))

    result = ntsd_synth_returns(spy, vea, financing_drag_annual=0.0075)

    expected_day1 = 0.90 * 0.01 + 0.60 * 0.005 - 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8
    assert len(result) == 3


def test_ntsd_synth_inception_window():
    """NTSD synth real cache: should produce 1986+ daily series ~10000 rows."""
    from studies.long_term_portfolio.synths import ntsd_synth_returns_from_cache

    s = ntsd_synth_returns_from_cache()
    assert isinstance(s, pd.Series)
    assert isinstance(s.index, pd.DatetimeIndex)
    assert s.index[0].year <= 1987  # SPYSIM inception 1986; VEASIM 1969
    assert s.index[-1].year >= 2025
    assert len(s) > 9000  # ~252 × 40y ≈ 10000
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py::test_ntsd_synth_formula -v`
Expected: FAIL with "no attribute ntsd_synth_returns".

- [ ] **Step 3: Implement NTSD synth in synths.py**

Append to `studies/long_term_portfolio/synths.py`:

```python
def ntsd_synth_returns(
    spy_returns: pd.Series,
    vea_returns: pd.Series,
    financing_drag_annual: float = 0.0075,
) -> pd.Series:
    """NTSD synth: 90% S&P + 60% EAFE − annual financing drag.

    INCOMPLETE: WisdomTree NTSD active management unmodeled (~0-50bps/y
    tracking error). Active management could add or subtract.

    Citation: WisdomTree NTSD prospectus 2026-03-19; `[risk_parity, ch.5]`
    Carlson cap-efficient stacking.

    Args:
        spy_returns: SPYSIM daily returns (decimal).
        vea_returns: VEASIM daily returns (decimal).
        financing_drag_annual: annualized drag on the 60% futures notional
            (default 0.0075 = 75bps/y; spec convention).

    Returns:
        NTSD synthetic daily returns aligned to spy/vea intersection.
    """
    daily_drag = _annual_drag_to_daily(financing_drag_annual)
    aligned = pd.concat({"spy": spy_returns, "vea": vea_returns}, axis=1).dropna()
    return 0.90 * aligned["spy"] + 0.60 * aligned["vea"] - daily_drag


def ntsd_synth_returns_from_cache() -> pd.Series:
    """Convenience: load SPYSIM + VEASIM from testfolio cache and synth."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    vea = load_testfolio_series("VEASIM").pct_change().dropna()
    return ntsd_synth_returns(spy, vea)
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/synths.py tests/test_studies_long_term_portfolio_synths.py
git commit -m "feat(long_term_portfolio/synths): NTSD synth (0.90 SPY + 0.60 VEA − 75bps/y)"
```

---

## Task 4: Implement AVUV / AVDV / AVEM synths (factor tilts)

**Files:**
- Modify: `studies/long_term_portfolio/synths.py`
- Modify: `tests/test_studies_long_term_portfolio_synths.py`

- [ ] **Step 1: Write failing tests for all three synths**

Append to `tests/test_studies_long_term_portfolio_synths.py`:

```python
def test_avuv_synth_formula():
    """AVUV = VBRSIM + (75bps/y / 252) per day."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vbr = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    result = factor_tilt_synth_returns(vbr, tilt_premium_annual=0.0075)

    expected_day1 = 0.01 + 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_avdv_synth_formula():
    """AVDV = VSSSIM + (100bps/y / 252)."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vss = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vss, tilt_premium_annual=0.0100)

    expected = 0.01 + 0.0100 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avem_synth_formula():
    """AVEM = VWOSIM + (125bps/y / 252)."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vwo = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vwo, tilt_premium_annual=0.0125)

    expected = 0.01 + 0.0125 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avuv_synth_from_cache():
    """AVUV synth from VBRSIM cache: 1926+ window."""
    from studies.long_term_portfolio.synths import avuv_synth_returns_from_cache

    s = avuv_synth_returns_from_cache()
    assert s.index[0].year <= 1927
    assert len(s) > 25000  # ~99y × 252


def test_avem_synth_from_cache_window():
    """AVEM synth from VWOSIM cache: 1994+ window (32y bottleneck)."""
    from studies.long_term_portfolio.synths import avem_synth_returns_from_cache

    s = avem_synth_returns_from_cache()
    assert s.index[0].year >= 1994
    assert s.index[0].year <= 1995
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 5 new fails.

- [ ] **Step 3: Implement factor_tilt_synth + cache loaders**

Append to `studies/long_term_portfolio/synths.py`:

```python
def factor_tilt_synth_returns(
    proxy_returns: pd.Series,
    tilt_premium_annual: float,
) -> pd.Series:
    """Avantis-style factor synth: proxy returns + annual tilt premium.

    INCOMPLETE: VBRSIM/VSSSIM/VWOSIM are broad index proxies; Avantis
    AVUV/AVDV/AVEM concentrate SCV+profitability+value tilts. Real Avantis
    premium may be larger or smaller than the literature midpoint.

    Citations: `[risk_parity, ch.2, p.37-41]` Fama-French SCV;
    `[ilmanen_expected_returns, ch.19]` intl/EM factor diversification;
    `[advances_fin_ml, p.31-34]` factor framework.

    Args:
        proxy_returns: VBRSIM/VSSSIM/VWOSIM daily returns.
        tilt_premium_annual: annualized tilt premium added (decimal).
            Spec midpoints: 0.0075 (AVUV), 0.0100 (AVDV), 0.0125 (AVEM).

    Returns:
        Synthetic factor ETF daily returns.
    """
    daily_premium = _annual_drag_to_daily(tilt_premium_annual)
    return proxy_returns + daily_premium


def avuv_synth_returns_from_cache() -> pd.Series:
    """AVUV synth: VBRSIM + 75bps/y tilt premium."""
    vbr = load_testfolio_series("VBRSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vbr, tilt_premium_annual=0.0075)


def avdv_synth_returns_from_cache() -> pd.Series:
    """AVDV synth: VSSSIM + 100bps/y tilt premium."""
    vss = load_testfolio_series("VSSSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vss, tilt_premium_annual=0.0100)


def avem_synth_returns_from_cache() -> pd.Series:
    """AVEM synth: VWOSIM + 125bps/y tilt premium. INCOMPLETE — VWOSIM 1994+ bottleneck."""
    vwo = load_testfolio_series("VWOSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vwo, tilt_premium_annual=0.0125)
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/synths.py tests/test_studies_long_term_portfolio_synths.py
git commit -m "feat(long_term_portfolio/synths): AVUV/AVDV/AVEM factor tilt synths (75/100/125bps/y premia)"
```

---

## Task 5: Implement SPMO / IDMO synths (momentum sleeves with UMD overlay)

**Files:**
- Modify: `studies/long_term_portfolio/synths.py`
- Modify: `tests/test_studies_long_term_portfolio_synths.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_studies_long_term_portfolio_synths.py`:

```python
def test_spmo_synth_formula():
    """SPMO = SPYSIM + 0.60 × UMD_KF − (35bps/y / 252)."""
    from studies.long_term_portfolio.synths import momentum_synth_returns

    spy = pd.Series([0.01, 0.0], index=pd.date_range("2024-01-02", periods=2, freq="B"))
    umd = pd.Series([0.005, -0.001], index=pd.date_range("2024-01-02", periods=2, freq="B"))

    result = momentum_synth_returns(
        spy, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0035
    )

    expected_day1 = 0.01 + 0.60 * 0.005 - 0.0035 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_idmo_synth_formula():
    """IDMO = VEASIM + 0.60 × UMD_KF − (60bps/y / 252)."""
    from studies.long_term_portfolio.synths import momentum_synth_returns

    vea = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    umd = pd.Series([0.005], index=pd.date_range("2024-01-02", periods=1, freq="B"))

    result = momentum_synth_returns(
        vea, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0060
    )

    expected = 0.01 + 0.60 * 0.005 - 0.0060 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_spmo_synth_no_free_lunch_check():
    """KILL #3: SPMO standalone Sharpe must be < 1.5 vs literature ~0.6-0.8.

    On real cached data, SPMO synth Sharpe should be in plausible range.
    """
    from studies.long_term_portfolio.synths import spmo_synth_returns_from_cache

    spmo = spmo_synth_returns_from_cache()
    annualized_sharpe = spmo.mean() / spmo.std() * np.sqrt(252)
    assert annualized_sharpe < 1.5, f"SPMO standalone Sharpe {annualized_sharpe:.2f} > 1.5; synth broken (KILL #3)"
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py::test_spmo_synth_formula -v`
Expected: FAIL no attribute.

- [ ] **Step 3: Implement momentum synth**

Append to `studies/long_term_portfolio/synths.py`:

```python
def momentum_synth_returns(
    base_equity_returns: pd.Series,
    umd_factor_returns: pd.Series,
    capture_coef: float = 0.60,
    expense_annual: float = 0.0035,
) -> pd.Series:
    """SPMO/IDMO-style momentum synth: base equity + UMD overlay − expense.

    INCOMPLETE: Frazzini-Israel-Moskowitz 2018 capture rate (~60-70%) is
    literature-cited, not direct SPMO/IDMO inception data. Real SPMO/IDMO
    tracking error unmeasured. Engine differs from Ken French academic UMD
    (long-short market-neutral, gross of cost).

    Citations: `[stocks_on_the_move, p.21-30]` Clenow time-series momentum;
    Jegadeesh-Titman 1993 cross-sectional momentum; Frazzini-Israel-Moskowitz
    2018 long-only momentum capture.

    Args:
        base_equity_returns: SPYSIM (for SPMO) or VEASIM (for IDMO) daily returns.
        umd_factor_returns: Ken French UMD daily factor returns.
        capture_coef: long-only capture of UMD factor (default 0.60).
        expense_annual: annualized expense ratio (default 0.0035 = 35bps/y for
            SPMO; use 0.0060 for IDMO).

    Returns:
        Momentum synthetic ETF daily returns.
    """
    daily_expense = _annual_drag_to_daily(expense_annual)
    aligned = pd.concat({"base": base_equity_returns, "umd": umd_factor_returns}, axis=1).dropna()
    return aligned["base"] + capture_coef * aligned["umd"] - daily_expense


def _load_umd_kf_returns() -> pd.Series:
    """Load Ken French daily UMD factor returns from data/ken_french/.

    File format: F-F_Momentum_Factor_daily.csv has columns Date, Mom (in
    percent units, e.g. 0.50 means +0.50%). Convert to decimal returns.
    """
    import pathlib
    csv_path = pathlib.Path("data/ken_french/F-F_Momentum_Factor_daily.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Ken French UMD daily file not found at {csv_path}")
    df = pd.read_csv(csv_path, skiprows=13, index_col=0, parse_dates=False)
    # Trim footer and parse YYYYMMDD index
    df = df[df.index.astype(str).str.match(r"^\d{8}$")]
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return (df["Mom   "].astype(float) / 100.0).rename("UMD_KF")


def spmo_synth_returns_from_cache() -> pd.Series:
    """SPMO synth: SPYSIM + 0.60 × UMD_KF − 35bps/y."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    umd = _load_umd_kf_returns()
    return momentum_synth_returns(spy, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0035)


def idmo_synth_returns_from_cache() -> pd.Series:
    """IDMO synth: VEASIM + 0.60 × UMD_KF − 60bps/y. INCOMPLETE — US UMD proxy for intl."""
    vea = load_testfolio_series("VEASIM").pct_change().dropna()
    umd = _load_umd_kf_returns()
    return momentum_synth_returns(vea, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0060)
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/synths.py tests/test_studies_long_term_portfolio_synths.py
git commit -m "feat(long_term_portfolio/synths): SPMO/IDMO momentum synths via Ken French UMD overlay"
```

---

## Task 6: Implement RSST synth + DBMF + CTA proxy

**Files:**
- Modify: `studies/long_term_portfolio/synths.py`
- Modify: `tests/test_studies_long_term_portfolio_synths.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_studies_long_term_portfolio_synths.py`:

```python
def test_rsst_synth_formula():
    """RSST = SPYSIM + KMLMSIM − (60bps/y / 252)."""
    from studies.long_term_portfolio.synths import rsst_synth_returns

    spy = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    kmlm = pd.Series([0.005], index=pd.date_range("2024-01-02", periods=1, freq="B"))

    result = rsst_synth_returns(spy, kmlm, expense_annual=0.0060)

    expected = 0.01 + 0.005 - 0.0060 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_rsst_synth_no_free_lunch_kill5():
    """KILL #5: RSST_synth standalone Sharpe ≤ (SPYSIM Sharpe + KMLMSIM Sharpe) × 0.7.

    Theoretical max two-asset zero-correlation Sharpe = sqrt(s1² + s2²);
    typically lower with positive correlation. 0.7 cap is generous.
    """
    from studies.long_term_portfolio.synths import (
        rsst_synth_returns_from_cache,
    )

    rsst = rsst_synth_returns_from_cache()
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    kmlm = load_testfolio_series("KMLMSIM").pct_change().dropna()

    spy_sharpe = spy.mean() / spy.std() * np.sqrt(252)
    kmlm_sharpe = kmlm.mean() / kmlm.std() * np.sqrt(252)
    rsst_sharpe = rsst.mean() / rsst.std() * np.sqrt(252)

    threshold = (spy_sharpe + kmlm_sharpe) * 0.7
    assert rsst_sharpe < threshold + 0.05, (
        f"RSST_synth Sharpe {rsst_sharpe:.3f} > {threshold:.3f} (KILL #5 fired)"
    )


def test_dbmf_load_from_cache():
    """DBMFSIM cached: 1999+ daily window."""
    from studies.long_term_portfolio.synths import dbmf_returns_from_cache

    dbmf = dbmf_returns_from_cache()
    assert dbmf.index[0].year >= 1999
    assert dbmf.index[0].year <= 2001
    assert len(dbmf) > 6000  # ~26y × 252


def test_cta_proxy_warning_in_docstring():
    """CTA Simplify proxy must explicitly flag INCOMPLETE in docstring."""
    from studies.long_term_portfolio.synths import cta_simplify_proxy_returns
    assert "INCOMPLETE" in cta_simplify_proxy_returns.__doc__
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 4 new fails.

- [ ] **Step 3: Implement RSST + DBMF + CTA proxy**

Append to `studies/long_term_portfolio/synths.py`:

```python
def rsst_synth_returns(
    spy_returns: pd.Series,
    kmlm_returns: pd.Series,
    expense_annual: float = 0.0060,
) -> pd.Series:
    """Return Stacked US + MF (RSST) synth: 100% S&P + 100% MF − expense.

    INCOMPLETE: real RSST uses Newfound/ReSolve trend MF engine, not KFA
    MLM Index. Engine differs. Real RSST inception 2023-09. Long-history
    backtest using KMLMSIM as MF proxy will track imperfectly.

    Citation: ReSolve/Newfound Return Stacked methodology (2023);
    `[risk_parity, ch.5]` Carlson cap-efficient stacking.

    Args:
        spy_returns: SPYSIM daily returns.
        kmlm_returns: KMLMSIM daily returns (MF proxy).
        expense_annual: annualized expense (default 0.0060 = 60bps/y).

    Returns:
        RSST synthetic daily returns.
    """
    daily_expense = _annual_drag_to_daily(expense_annual)
    aligned = pd.concat({"spy": spy_returns, "kmlm": kmlm_returns}, axis=1).dropna()
    return aligned["spy"] + aligned["kmlm"] - daily_expense


def rsst_synth_returns_from_cache() -> pd.Series:
    """RSST synth from cache."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    kmlm = load_testfolio_series("KMLMSIM").pct_change().dropna()
    return rsst_synth_returns(spy, kmlm)


def dbmf_returns_from_cache() -> pd.Series:
    """DBMFSIM daily returns from cache: 1999+, 26y. Direct testfolio synth.

    Citation: testfolio extracts DBMFSIM as iMGP DBi Managed Futures
    proxy following SG CTA Index methodology.
    """
    return load_testfolio_series("DBMFSIM").pct_change().dropna()


def cta_simplify_proxy_returns(scaling: float = 1.0) -> pd.Series:
    """CTA Simplify proxy via KMLMSIM — INCOMPLETE for real CTA Simplify.

    Real CTA Simplify uses Altis Partners multi-strategy engine (trend +
    carry + mean-reversion + risk-off). KMLMSIM is single-strategy (KFA
    MLM rules-based trend). This proxy is KMLMSIM scaled by `scaling`
    (default 1.0 = pure KMLMSIM passthrough).

    Use only as DIAGNOSTIC in iter 039 MF sleeve sensitivity, with explicit
    INCOMPLETE caveat in final_report.md.

    Citation: Simplify Asset Mgmt CTA prospectus + Altis Partners docs.

    Args:
        scaling: multiplier on KMLMSIM returns (1.0 = pure proxy).

    Returns:
        Scaled KMLMSIM daily returns.
    """
    kmlm = load_testfolio_series("KMLMSIM").pct_change().dropna()
    return kmlm * scaling
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_synths.py -v`
Expected: 15 passed.

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/synths.py tests/test_studies_long_term_portfolio_synths.py
git commit -m "feat(long_term_portfolio/synths): RSST stacked synth + DBMF loader + CTA Simplify proxy"
```

---

## Task 7: Build run_iter.py helper module

**Files:**
- Create: `studies/long_term_portfolio/run_iter.py`
- Create: `tests/test_studies_long_term_portfolio_run_iter.py`

**Purpose:** Shared per-iter execution: takes a config dict (sleeve weights), runs backtest on 3 datasets, applies 7 gates, computes DSR, scores via scoring.py, writes verdict.json + final_report.md + plots.

- [ ] **Step 1: Write the test for portfolio_returns_from_config**

Create `tests/test_studies_long_term_portfolio_run_iter.py`:

```python
"""TDD tests for run_iter helper."""
import pandas as pd
import pytest

from studies.long_term_portfolio.run_iter import portfolio_returns_from_config


def test_portfolio_returns_from_simple_config():
    """50% SPYSIM + 50% IEFSIM should equal mean of the two daily returns."""
    config = {"SPYSIM": 0.50, "IEFSIM": 0.50}
    returns = portfolio_returns_from_config(config, dataset="lh_56y")
    assert isinstance(returns, pd.Series)
    assert len(returns) > 9000  # 40y × 252


def test_portfolio_returns_weights_must_sum_to_1():
    """Configs must sum to ~1.0 (allow synth notional > 1, but specify)."""
    with pytest.raises(ValueError, match="weights"):
        portfolio_returns_from_config({"SPYSIM": 0.30, "IEFSIM": 0.30}, dataset="lh_56y")


def test_portfolio_returns_with_synth_ticker():
    """Config can reference NTSXSIM (synth) and resolve via proxies.py."""
    config = {"NTSXSIM": 1.0}  # 100% NTSX synth
    returns = portfolio_returns_from_config(config, dataset="lh_56y")
    assert len(returns) > 9000
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_studies_long_term_portfolio_run_iter.py -v`
Expected: FAIL no module.

- [ ] **Step 3: Implement run_iter.py core**

Create `studies/long_term_portfolio/run_iter.py`:

```python
"""Per-iter execution helper for the long-term portfolio sweep iter 027-039.

Takes a config dict (ticker → weight) and produces:
- Aggregate portfolio daily returns
- 7-gate validation results
- DSR p-value with cumulative_n_trials
- Sharpe / CAGR / MDD per dataset
- Selection across configs sweep
- verdict.json + final_report.md + plots written to iter directory

Reuses existing modules: scoring.py, datasets.py, proxies.py,
plot_helper.py, rolling_windows.py, ff_momentum_proxy.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from studies.long_term_portfolio import datasets, scoring, synths
from studies.long_term_portfolio.proxies import (
    ntsx_synth_returns,
    ntsi_synth_returns,
    ntse_synth_returns,
)


WEIGHT_TOLERANCE = 0.005  # weights must sum to 1 ± 0.5%


def portfolio_returns_from_config(
    config: dict[str, float], dataset: str
) -> pd.Series:
    """Build aggregate portfolio daily returns from a weights config.

    Args:
        config: ticker → weight dict. Weights must sum to ~1.0 (notional may
            be implicit via stacking ETFs like NTSX which are synthesized
            with their own internal leverage).
        dataset: dataset name from datasets.py (lh_56y / vt_real / ndx_real).

    Returns:
        Daily portfolio returns aligned to dataset window.

    Raises:
        ValueError: if weights don't sum to ~1.0.
    """
    total = sum(config.values())
    if abs(total - 1.0) > WEIGHT_TOLERANCE:
        raise ValueError(f"config weights sum to {total:.4f}, expected ~1.0")

    component_returns = _resolve_tickers_to_returns(list(config.keys()))
    weighted = pd.DataFrame({t: r * w for (t, r), w in zip(component_returns.items(), config.values(), strict=True)})
    aggregate = weighted.sum(axis=1)
    window = datasets.window_for(dataset)
    return aggregate.loc[window[0] : window[1]].dropna()


def _resolve_tickers_to_returns(tickers: list[str]) -> dict[str, pd.Series]:
    """Resolve ticker names to daily returns Series.

    Routes:
    - NTSXSIM/NTSISIM/NTSESIM → proxies.py
    - NTSDSIM/AVUVSIM/AVDVSIM/AVEMSIM/SPMOSIM/IDMOSIM/RSSTSIM → synths.py
    - All other -SIM tickers → testfolio cache (.pct_change())
    - DBMFSIM → testfolio cache directly

    Returns:
        ticker → Series mapping.
    """
    out: dict[str, pd.Series] = {}
    for t in tickers:
        if t == "NTSXSIM":
            out[t] = ntsx_synth_returns()
        elif t == "NTSISIM":
            out[t] = ntsi_synth_returns()
        elif t == "NTSESIM":
            out[t] = ntse_synth_returns()
        elif t == "NTSDSIM":
            out[t] = synths.ntsd_synth_returns_from_cache()
        elif t == "AVUVSIM":
            out[t] = synths.avuv_synth_returns_from_cache()
        elif t == "AVDVSIM":
            out[t] = synths.avdv_synth_returns_from_cache()
        elif t == "AVEMSIM":
            out[t] = synths.avem_synth_returns_from_cache()
        elif t == "SPMOSIM":
            out[t] = synths.spmo_synth_returns_from_cache()
        elif t == "IDMOSIM":
            out[t] = synths.idmo_synth_returns_from_cache()
        elif t == "RSSTSIM":
            out[t] = synths.rsst_synth_returns_from_cache()
        else:
            from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_series
            out[t] = load_testfolio_series(t).pct_change().dropna()
    return out
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_studies_long_term_portfolio_run_iter.py -v`
Expected: 3 passed.

- [ ] **Step 5: Add run_iter_full() — the complete per-iter execution**

Append to `studies/long_term_portfolio/run_iter.py`:

```python
def run_iter_full(
    iter_n: int,
    iter_dir: Path,
    hypothesis_slug: str,
    primary_citation: str,
    configs: dict[str, dict[str, float]],
    datasets_to_test: tuple[str, ...] = ("lh_56y", "vt_real", "ndx_real"),
    cumulative_n_trials: int | None = None,
    selection_rule: str = "max mean(gross_Sharpe / spy_Sharpe) across datasets",
) -> dict[str, Any]:
    """Execute a full iter sweep: sweep all configs across all datasets, score, write artifacts.

    Args:
        iter_n: iter number (e.g. 27).
        iter_dir: existing directory like .../iterations/027-2026-04-29-NTSD-swap/.
        hypothesis_slug: e.g. 'NTSD-swap'.
        primary_citation: e.g. '[risk_parity, ch.5, p.10]'.
        configs: {config_name: {ticker: weight}, ...}.
        datasets_to_test: dataset names to test on.
        cumulative_n_trials: pre-iter trial count + len(configs); for DSR.
        selection_rule: text describing how best config is picked.

    Returns:
        verdict dict (also written as verdict.json in iter_dir).
    """
    from studies.long_term_portfolio.scoring import score_strategy
    from studies.long_term_portfolio.rolling_windows import (
        rolling_sharpe_at_windows,
        rolling_outperformance_pct,
    )

    iter_dir.mkdir(parents=True, exist_ok=True)
    config_results: dict[str, dict[str, dict[str, Any]]] = {}

    for cfg_name, weights in configs.items():
        config_results[cfg_name] = {}
        for ds in datasets_to_test:
            returns = portfolio_returns_from_config(weights, dataset=ds)
            metrics = _compute_metrics(returns)
            config_results[cfg_name][ds] = metrics

    selected_cfg = _select_best_config(config_results, datasets_to_test)

    selected_metrics = config_results[selected_cfg]
    verdict = score_strategy(
        metrics_per_dataset={ds: selected_metrics[ds] for ds in datasets_to_test},
        cumulative_n_trials=cumulative_n_trials or len(configs),
        configs_tested=len(configs),
        primary_citation=primary_citation,
        hypothesis_slug=hypothesis_slug,
        selected_config=selected_cfg,
    ).to_dict()

    verdict["selection_rule"] = selection_rule
    verdict["all_configs_metrics"] = config_results

    (iter_dir / "verdict.json").write_text(json.dumps(verdict, indent=2, default=str))
    _write_final_report(iter_dir, iter_n, hypothesis_slug, primary_citation, configs, verdict)
    _write_plots(iter_dir, configs, selected_cfg, datasets_to_test)

    return verdict


def _compute_metrics(returns: pd.Series) -> dict[str, float]:
    """Sharpe / CAGR / MDD / DSR p-value (placeholder, real DSR runs at score)."""
    annualized_sharpe = returns.mean() / returns.std() * np.sqrt(252)
    cagr = (1 + returns).prod() ** (252 / len(returns)) - 1
    cum = (1 + returns).cumprod()
    mdd = (cum / cum.cummax() - 1).min()
    return {"sharpe": annualized_sharpe, "cagr": cagr, "mdd": abs(mdd)}


def _select_best_config(
    config_results: dict[str, dict[str, dict[str, float]]],
    datasets_to_test: tuple[str, ...],
) -> str:
    """Pick config with max mean(Sharpe / spy_benchmark_sharpe) across datasets."""
    spy_sharpes = {ds: scoring.spy_benchmark(ds)["sharpe"] for ds in datasets_to_test}
    best, best_score = "", -np.inf
    for cfg, ds_metrics in config_results.items():
        ratios = [ds_metrics[ds]["sharpe"] / spy_sharpes[ds] for ds in datasets_to_test]
        score = np.mean(ratios)
        if score > best_score:
            best, best_score = cfg, score
    return best


def _write_final_report(
    iter_dir: Path, iter_n: int, slug: str, citation: str,
    configs: dict[str, dict[str, float]], verdict: dict[str, Any]
) -> None:
    selected = verdict["selected_config"]
    report = f"""# Iter {iter_n:03d} — {slug}

## Hypothesis
See `hypothesis.md`.

## Primary citation
{citation}

## Configs tested ({len(configs)})

```json
{json.dumps(configs, indent=2)}
```

## Selected config: `{selected}`

## Metrics (gross Sharpe / CAGR / MDD per dataset)

```json
{json.dumps(verdict["metrics_used"], indent=2, default=str)}
```

## Verdict

- **status**: {verdict["status"]}
- **tier**: {verdict["tier"]}
- **total_score**: {verdict["total_score"]}/100
- **winner_conditions_met**: {verdict["winner_conditions_met"]}

## INCOMPLETE flags
(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson
(Append after manual review.)
"""
    (iter_dir / "final_report.md").write_text(report)


def _write_plots(
    iter_dir: Path,
    configs: dict[str, dict[str, float]],
    selected_cfg: str,
    datasets_to_test: tuple[str, ...],
) -> None:
    """Stub: real plot generation reuses plot_helper.py from existing iters."""
    from studies.long_term_portfolio import plot_helper
    selected_returns = {
        ds: portfolio_returns_from_config(configs[selected_cfg], dataset=ds)
        for ds in datasets_to_test
    }
    for ds, returns in selected_returns.items():
        plot_helper.plot_equity_vs_benchmarks(
            returns=returns, dataset=ds, out_path=iter_dir / f"plot_{ds}.png"
        )
        plot_helper.plot_rolling_windows(
            returns=returns, dataset=ds, out_path=iter_dir / f"plot_rolling_windows_{ds}.png"
        )
```

- [ ] **Step 6: Run smoke test of run_iter_full on a known config**

Run a quick smoke from python:
```bash
cd /var/www/pessoal/ai-trade && python -c "
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full
v = run_iter_full(
    iter_n=999,
    iter_dir=Path('/tmp/long_term_portfolio_smoke'),
    hypothesis_slug='smoke-test',
    primary_citation='[risk_parity, ch.5]',
    configs={'iter023_baseline': {'NTSXSIM': 0.25, 'GDESIM': 0.25, 'KMLMSIM': 0.35, 'TLTSIM': 0.15}},
    datasets_to_test=('lh_56y',),
    cumulative_n_trials=1,
)
print('verdict.score:', v['total_score'])
"
```

Expected: prints a score (around iter 023's known ~86 NEW / 91 LEGACY).

- [ ] **Step 7: Commit**

```bash
git add studies/long_term_portfolio/run_iter.py tests/test_studies_long_term_portfolio_run_iter.py
git commit -m "feat(long_term_portfolio): run_iter helper for per-iter sweep execution"
```

---

## Task 8: Iter 027 — NTSD swap execution

**Files:**
- Create: `studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap/backtest.py`

- [ ] **Step 1: Create iter directory and hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap
```

Create `hypothesis.md`:

```markdown
# Iter 027 — NTSD swap (ex-US developed equity stack, GLOBAL category)

## Hypothesis (one paragraph)

NTSD adds intl-developed equity inside a 1.5× levered wrapper (90% US + 60%
EAFE futures). Reduces home-country bias without sacrificing leverage.
Tests whether iter 014/015's failed intl-equity overlay attempts work when
**stacked inside** the wrapper instead of added outside.

## Primary citation

`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking + WisdomTree NTSD
prospectus 2026-03-19.

## Configs tested (4)

| config | NTSX | NTSD | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|---:|
| ntsd_lite_2055 | 20% | 5% | 25% | 35% | 15% |
| ntsd_mod_15105 | 15% | 10% | 25% | 35% | 15% |
| ntsd_med_10155 | 10% | 15% | 25% | 35% | 15% |
| ntsd_heavy_5205 | 5% | 20% | 25% | 35% | 15% |

## Synth used

NTSDSIM = `0.90 SPYSIM + 0.60 VEASIM − 75bps/y`. INCOMPLETE — active
management unmodeled.

## KILLs pre-committed

- KILL #1 (no-positive-config): if best config doesn't beat iter 023 on ≥1/3 datasets → close.
- KILL #2 (monotonic regression): if Sharpe monotonically falls with NTSD weight → close.
```

- [ ] **Step 2: Create backtest.py**

Create `backtest.py`:

```python
"""Iter 027 backtest: NTSD swap on iter 023 base."""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "ntsd_lite_2055":  {"NTSXSIM": 0.20, "NTSDSIM": 0.05, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_mod_15105":  {"NTSXSIM": 0.15, "NTSDSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_med_10155":  {"NTSXSIM": 0.10, "NTSDSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_heavy_5205": {"NTSXSIM": 0.05, "NTSDSIM": 0.20, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=27,
        iter_dir=iter_dir,
        hypothesis_slug="NTSD-swap",
        primary_citation="[risk_parity, ch.5, p.10]",
        configs=CONFIGS,
        cumulative_n_trials=94 + len(CONFIGS),  # post-iter-026 + this iter
    )
    print(f"iter 027 verdict: status={verdict['status']}, score={verdict['total_score']}, "
          f"selected={verdict['selected_config']}")
```

- [ ] **Step 3: Run iter 027**

```bash
cd /var/www/pessoal/ai-trade && python studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap/backtest.py
```

Expected: prints status (winner/strong/promising/marginal/fail), score, selected config. Files written: verdict.json, final_report.md, plot_*.png.

- [ ] **Step 4: Manual review of verdict.json**

Read iter_dir/verdict.json. Check:
- status field is set correctly
- winner_conditions_met reflects gates passed
- KILL #1 fired if 0/3 datasets beat iter 023 → mark as closed
- KILL #2 fired if Sharpe monotonic-decrease with NTSD weight → mark as closed

If KILL fires, append note in `final_report.md` "Lesson" section.

- [ ] **Step 5: Append to BASE_MEMORY.md**

In `studies/long_term_portfolio/BASE_MEMORY.md`, prepend new entry to "Iteration log" (after `### 026` heading). Match the existing format: hypothesis (1-2 lines), result (Sharpe per dataset, score, winner_conds), verdict, lesson.

Update frontmatter:
- `total_iterations: 27`
- `latest_iteration: "027-2026-04-29-NTSD-swap"`
- `cumulative_n_trials: 98`
- `latest_score: <value from verdict.json>`

- [ ] **Step 6: Commit**

```bash
git add studies/long_term_portfolio/iterations/027-2026-04-29-NTSD-swap/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-027): NTSD swap test, status=<status>, score=<score>"
```

---

## Task 9: Iter 028 — AVUV add execution

**Files:**
- Create: `studies/long_term_portfolio/iterations/028-2026-04-29-AVUV-add/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/028-2026-04-29-AVUV-add/backtest.py`

- [ ] **Step 1: Create iter directory and hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/028-2026-04-29-AVUV-add
```

Create `hypothesis.md`:

```markdown
# Iter 028 — AVUV add (US small-cap value factor, US + GLOBAL category)

## Hypothesis (one paragraph)

Avantis US Small-Cap Value adds factor exposure (size+value+profitability)
historically uncorrelated with US large-cap regime. Tests whether **size
factor at 1× notional** outside the wrapper recovers what iter 013's VBRSIM
tilt couldn't (post-2008 "death of value" regime).

## Primary citation

`[risk_parity, ch.2, p.37-41]` Fama-French SCV; `[advances_fin_ml, p.31-34]`
factor framework.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | AVUV |
|---|---:|---:|---:|---:|---:|
| avuv_lite | 22.5% | 25% | 32.5% | 15% | 5% |
| avuv_mod | 20% | 25% | 30% | 15% | 10% |
| avuv_med | 17.5% | 25% | 27.5% | 15% | 15% |
| avuv_heavy | 15% | 25% | 25% | 15% | 20% |

## Synth used

AVUVSIM = `VBRSIM + 75bps/y tilt premium`. INCOMPLETE — proxy index ≠
Avantis screening; tilt premium estimate.
```

- [ ] **Step 2: Create backtest.py**

Create `backtest.py`:

```python
"""Iter 028 backtest: AVUV factor add on iter 023 base."""
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avuv_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVUVSIM": 0.05},
    "avuv_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVUVSIM": 0.10},
    "avuv_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVUVSIM": 0.15},
    "avuv_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVUVSIM": 0.20},
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=28,
        iter_dir=iter_dir,
        hypothesis_slug="AVUV-add",
        primary_citation="[risk_parity, ch.2, p.37-41]",
        configs=CONFIGS,
        cumulative_n_trials=98 + len(CONFIGS),
    )
    print(f"iter 028 verdict: status={verdict['status']}, score={verdict['total_score']}, "
          f"selected={verdict['selected_config']}")
```

- [ ] **Step 3: Run iter 028**

```bash
cd /var/www/pessoal/ai-trade && python studies/long_term_portfolio/iterations/028-2026-04-29-AVUV-add/backtest.py
```

- [ ] **Step 4: Review verdict, append to BASE_MEMORY**

(Same procedure as Task 8 step 4-5.)

Update frontmatter: `total_iterations: 28`, `cumulative_n_trials: 102`.

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/iterations/028-2026-04-29-AVUV-add/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-028): AVUV factor add test, status=<status>, score=<score>"
```

---

## Task 10: Iter 029 — AVDV add execution

**Files:**
- Create: `studies/long_term_portfolio/iterations/029-2026-04-29-AVDV-add/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/029-2026-04-29-AVDV-add/backtest.py`

- [ ] **Step 1: Create iter directory + hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/029-2026-04-29-AVDV-add
```

Create `hypothesis.md`:

```markdown
# Iter 029 — AVDV add (intl developed SCV factor, GLOBAL category)

## Hypothesis (one paragraph)

AVDV is the intl mirror of AVUV. User confirms ~40% 2025 return — intl
SCV regime cycle inverted vs US 2025. Tests **factor + geographic**
combined axis.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl factor diversification;
`[risk_parity, ch.2, p.37-41]` Fama-French SCV.

## Configs (4)

| config | NTSX | GDE | KMLM | TLT | AVDV |
|---|---:|---:|---:|---:|---:|
| avdv_lite | 22.5% | 25% | 32.5% | 15% | 5% |
| avdv_mod | 20% | 25% | 30% | 15% | 10% |
| avdv_med | 17.5% | 25% | 27.5% | 15% | 15% |
| avdv_heavy | 15% | 25% | 25% | 15% | 20% |

## Synth

AVDVSIM = `VSSSIM + 100bps/y tilt premium`. INCOMPLETE.
```

- [ ] **Step 2: Create backtest.py**

```python
"""Iter 029 backtest: AVDV factor add on iter 023 base."""
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avdv_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVDVSIM": 0.05},
    "avdv_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVDVSIM": 0.10},
    "avdv_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVDVSIM": 0.15},
    "avdv_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVDVSIM": 0.20},
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=29, iter_dir=iter_dir, hypothesis_slug="AVDV-add",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS, cumulative_n_trials=102 + len(CONFIGS),
    )
    print(f"iter 029: status={verdict['status']}, score={verdict['total_score']}, sel={verdict['selected_config']}")
```

- [ ] **Step 3: Execute, review, BASE_MEMORY append, commit**

```bash
cd /var/www/pessoal/ai-trade && python studies/long_term_portfolio/iterations/029-2026-04-29-AVDV-add/backtest.py
# Review verdict.json, update BASE_MEMORY (total_iterations=29, n_trials=106)
git add studies/long_term_portfolio/iterations/029-2026-04-29-AVDV-add/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-029): AVDV factor add test, status=<status>, score=<score>"
```

---

## Task 11: Iter 030 — SPMO synth execution

**Files:**
- Create: `studies/long_term_portfolio/iterations/030-2026-04-29-SPMO-synth/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/030-2026-04-29-SPMO-synth/backtest.py`

- [ ] **Step 1: Create iter directory + hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/030-2026-04-29-SPMO-synth
```

`hypothesis.md`:

```markdown
# Iter 030 — SPMO synth add (US momentum sleeve, US + GLOBAL category)

## Hypothesis

Capture iter 016's UMD-academic +signal in **deployable form** via SPMO
synth. SPMO embeds SPY beta + cross-sectional momentum overlay. Per
Frazzini-Israel-Moskowitz 2018, real momentum ETFs capture ~60-70% of UMD
long-short premium due to long-only constraint + costs.

## Primary citation
`[stocks_on_the_move, p.21-30]` Clenow + Jegadeesh-Titman 1993.

## Configs (4)

| config | NTSX | GDE | KMLM | TLT | SPMOSIM |
|---|---:|---:|---:|---:|---:|
| spmo_lite | 22.5% | 25% | 32.5% | 15% | 5% |
| spmo_mod | 20% | 25% | 30% | 15% | 10% |
| spmo_med | 17.5% | 25% | 27.5% | 15% | 15% |
| spmo_heavy | 15% | 25% | 25% | 15% | 20% |

## Synth

SPMOSIM = `SPYSIM + 0.60 × UMD_KF − 35bps/y`. INCOMPLETE — UMD academic
capture coefficient.

## KILL #3 pre-committed

If SPMO_synth standalone Sharpe > 1.5 → broken, fix synth.
```

- [ ] **Step 2: Create backtest.py**

```python
"""Iter 030 backtest: SPMO synth add on iter 023 base."""
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full
from studies.long_term_portfolio.synths import spmo_synth_returns_from_cache
import numpy as np

# KILL #3 standalone Sharpe check
spmo = spmo_synth_returns_from_cache()
spmo_sharpe = spmo.mean() / spmo.std() * np.sqrt(252)
assert spmo_sharpe < 1.5, f"KILL #3: SPMO standalone Sharpe {spmo_sharpe:.3f} > 1.5"

CONFIGS = {
    "spmo_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "SPMOSIM": 0.05},
    "spmo_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "SPMOSIM": 0.10},
    "spmo_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "SPMOSIM": 0.15},
    "spmo_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "SPMOSIM": 0.20},
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=30, iter_dir=iter_dir, hypothesis_slug="SPMO-synth",
        primary_citation="[stocks_on_the_move, p.21-30]",
        configs=CONFIGS, cumulative_n_trials=106 + len(CONFIGS),
    )
    print(f"iter 030: status={verdict['status']}, score={verdict['total_score']}, sel={verdict['selected_config']}")
```

- [ ] **Step 3: Execute, review, BASE_MEMORY, commit**

```bash
cd /var/www/pessoal/ai-trade && python studies/long_term_portfolio/iterations/030-2026-04-29-SPMO-synth/backtest.py
# n_trials → 110
git add studies/long_term_portfolio/iterations/030-2026-04-29-SPMO-synth/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-030): SPMO synth add test, status=<status>, score=<score>"
```

---

## Task 12: Iter 031 — IDMO synth execution

Same template as iter 030 with IDMOSIM. Configs:

```python
CONFIGS = {
    "idmo_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "IDMOSIM": 0.05},
    "idmo_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "IDMOSIM": 0.10},
    "idmo_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "IDMOSIM": 0.15},
    "idmo_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "IDMOSIM": 0.20},
}
```

- [ ] **Step 1**: Create dir `031-2026-04-29-IDMO-synth/`, hypothesis.md (citation `[ilmanen_expected_returns, ch.19]`), backtest.py with above configs.
- [ ] **Step 2**: KILL #3 check on IDMO standalone Sharpe < 1.5.
- [ ] **Step 3**: Execute, review verdict.
- [ ] **Step 4**: Append to BASE_MEMORY (total_iter=31, n_trials=114).
- [ ] **Step 5**: Commit `feat(long_term_portfolio/iter-031): IDMO synth add test, status=<status>, score=<score>`.

---

## Task 13: Iter 032 — AVEM execution

Same template. Configs:

```python
CONFIGS = {
    "avem_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVEMSIM": 0.05},
    "avem_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVEMSIM": 0.10},
    "avem_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVEMSIM": 0.15},
    "avem_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVEMSIM": 0.20},
}
```

- [ ] **Step 1**: Create dir `032-2026-04-29-AVEM-add/`, hypothesis with VWOSIM 1994+ window caveat, backtest.py.
- [ ] **Step 2**: Note in hypothesis.md: "AVEM-using configs cannot run lh_56y fully — effective window 1994-2026 (32y)."
- [ ] **Step 3**: Execute. Datasets in run_iter_full call should still be all 3 — internal alignment will use intersection.
- [ ] **Step 4**: BASE_MEMORY append (total_iter=32, n_trials=118). Document 32y window for AVEM.
- [ ] **Step 5**: Commit `feat(long_term_portfolio/iter-032): AVEM factor add test, status=<status>, score=<score>`.

---

## Task 14: Phase 1 winner selection (manual review)

**Files:**
- Modify: `studies/long_term_portfolio/BASE_MEMORY.md` (add "Phase 1 sleeves winners" section)
- Create: `studies/long_term_portfolio/PHASE_1_WINNERS.md`

**Purpose**: Identify which sleeves passed Phase 1 criteria, route to Phase 2.

- [ ] **Step 1: Read all 6 verdict.json files**

```bash
cd /var/www/pessoal/ai-trade && for i in 027 028 029 030 031 032; do
  echo "=== iter $i ==="
  cat studies/long_term_portfolio/iterations/$i-*/verdict.json | jq '{slug: .hypothesis_slug, status, score: .total_score, winner_conditions_met, sharpe_per_dataset: [.metrics_used | to_entries | .[] | {ds: .key, sharpe: .value.sharpe}]}'
done
```

- [ ] **Step 2: Apply winner criteria per sleeve**

A sleeve is a "winner" if:
- best config beats iter 023 mean Sharpe across 3 datasets, AND
- passes 7-gate battery on ≥2/3 datasets, AND
- DSR p<0.05 cumulative.

Build PHASE_1_WINNERS.md:

```markdown
# Phase 1 Winners — Sleeve-by-Sleeve

| iter | sleeve | mean Sharpe | beats iter 023? | gates ≥2/3 pass? | DSR p<0.05? | WINNER? |
|---|---|---:|---|---|---|---|
| 027 | NTSD | (compute mean) | (yes/no) | (yes/no) | (yes/no) | ✅/❌ |
| 028 | AVUV | ... | ... | ... | ... | ... |
| 029 | AVDV | ... | ... | ... | ... | ... |
| 030 | SPMO | ... | ... | ... | ... | ... |
| 031 | IDMO | ... | ... | ... | ... | ... |
| 032 | AVEM | ... | ... | ... | ... | ... |

## Phase 2 routing

| Finalist | Sleeves available |
|---|---|
| F1 US-Stk | (none needed, = iter 023 baseline) |
| F2 US-Fct | {AVUV, SPMO} ∩ winners |
| F3 US-Hyb | {AVUV, SPMO} ∩ winners |
| F4 Gl-Stk | {NTSD} ∩ winners |
| F5 Gl-Fct | {AVUV, AVDV, AVEM, SPMO, IDMO} ∩ winners |
| F6 Gl-Hyb | {NTSD, AVUV, AVDV, AVEM, SPMO, IDMO} ∩ winners |
| F7 US-StkMF | (no sleeve from Phase 1; uses RSST_synth standalone) |

## Decisions
- Run Phase 2 iter 033 (F2)? <yes/no — depends on AVUV or SPMO winning>
- Run Phase 2 iter 035 (F4)? <yes/no — depends on NTSD winning>
- ... (etc per finalist)
```

- [ ] **Step 3: Apply fallback rules per spec §Phase 2 fallback rules**

If a sleeve fails:
- Mark its dependent finalist iter as "skipped" in PHASE_1_WINNERS.md
- Document the finding ("F<n> = <sleeve> not viable in testfolio universe")

- [ ] **Step 4: Update BASE_MEMORY frontmatter**

In BASE_MEMORY.md frontmatter:
- `phase_1_complete: true`
- `phase_1_winners: [list of winning sleeve names]`
- `phase_2_iters_to_run: [list of iter numbers]`

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/PHASE_1_WINNERS.md studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "docs(long_term_portfolio): Phase 1 complete, identify winners + Phase 2 routing"
```

---

## Task 15: Iter 033 — F2 US Factor-only construction

**Files:**
- Create: `studies/long_term_portfolio/iterations/033-2026-04-30-F2-US-Factor/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/033-2026-04-30-F2-US-Factor/backtest.py`

**Note**: only run if AVUV or SPMO won Phase 1. If both failed, skip per fallback rule.

- [ ] **Step 1: Create iter directory and hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/033-2026-04-30-F2-US-Factor
```

`hypothesis.md`:

```markdown
# Iter 033 — F2: US Factor-tilts-only finalist construction

## Hypothesis

Pure factor portfolio without stacking ETFs. Equity via VTI vanilla +
AVUV/SPMO factor tilts. Diversifiers: KMLM, TLT, GLDSIM. Tests if pure
factor philosophy can match capital-efficient stacking philosophy at
1× notional.

## Primary citation
`[risk_parity, ch.2, p.37-41]` Fama-French factor framework;
`[stocks_on_the_move, p.21-30]` momentum sleeve.

## Configs (4) — assuming both AVUV and SPMO won Phase 1

| config | VTISIM | AVUV | SPMO | KMLM | TLTSIM | GLDSIM |
|---|---:|---:|---:|---:|---:|---:|
| f2_balanced | 35% | 15% | 10% | 20% | 10% | 10% |
| f2_factor_heavy | 25% | 25% | 15% | 15% | 10% | 10% |
| f2_avuv_heavy | 30% | 25% | 5% | 20% | 10% | 10% |
| f2_spmo_heavy | 30% | 10% | 20% | 20% | 10% | 10% |

If only AVUV won: replace SPMO column with VTISIM.
If only SPMO won: replace AVUV column with VTISIM.
```

- [ ] **Step 2: Create backtest.py**

```python
"""Iter 033 backtest: F2 US Factor-only finalist."""
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "f2_balanced":     {"VTISIM": 0.35, "AVUVSIM": 0.15, "SPMOSIM": 0.10, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_factor_heavy": {"VTISIM": 0.25, "AVUVSIM": 0.25, "SPMOSIM": 0.15, "KMLMSIM": 0.15, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_avuv_heavy":   {"VTISIM": 0.30, "AVUVSIM": 0.25, "SPMOSIM": 0.05, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_spmo_heavy":   {"VTISIM": 0.30, "AVUVSIM": 0.10, "SPMOSIM": 0.20, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=33, iter_dir=iter_dir, hypothesis_slug="F2-US-Factor",
        primary_citation="[risk_parity, ch.2, p.37-41]",
        configs=CONFIGS, cumulative_n_trials=118 + len(CONFIGS),
    )
    print(f"iter 033: status={verdict['status']}, score={verdict['total_score']}, sel={verdict['selected_config']}")
```

- [ ] **Step 3: Execute, review with KILL #4 frankenstein degradation check**

KILL #4: if F2 best config Sharpe < (mean of AVUV best Phase 1 + SPMO best Phase 1), the combination is non-additive. Document in final_report.md.

- [ ] **Step 4: BASE_MEMORY append (total_iter=33, n_trials=122). Commit.**

```bash
git add studies/long_term_portfolio/iterations/033-2026-04-30-F2-US-Factor/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-033): F2 US Factor-only finalist, status=<status>, score=<score>"
```

---

## Task 16: Iter 034 — F3 US Hybrid construction

`hypothesis.md` summary: iter 023 base + AVUV/SPMO winners. Configs:

```python
CONFIGS = {
    "f3_balanced":   {"NTSXSIM": 0.18, "GDESIM": 0.25, "KMLMSIM": 0.27, "TLTSIM": 0.15, "AVUVSIM": 0.075, "SPMOSIM": 0.075},
    "f3_avuv_heavy": {"NTSXSIM": 0.17, "GDESIM": 0.25, "KMLMSIM": 0.28, "TLTSIM": 0.15, "AVUVSIM": 0.10,  "SPMOSIM": 0.05},
    "f3_spmo_heavy": {"NTSXSIM": 0.17, "GDESIM": 0.25, "KMLMSIM": 0.28, "TLTSIM": 0.15, "AVUVSIM": 0.05,  "SPMOSIM": 0.10},
    "f3_factor_15":  {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "AVUVSIM": 0.10,  "SPMOSIM": 0.10},
}
```

- [ ] **Step 1**: Create dir `034-2026-04-30-F3-US-Hybrid/`, hypothesis.md, backtest.py.
- [ ] **Step 2**: Execute, KILL #4 check vs F1 (iter 023) + best F2 config. If F3 < (F1+F2)/2 → frankenstein degradation.
- [ ] **Step 3**: BASE_MEMORY (total=34, n_trials=126). Commit `feat(long_term_portfolio/iter-034): F3 US Hybrid finalist`.

---

## Task 17: Iter 035 — F4 Global Stacking-only construction

**Note**: only run if NTSD won Phase 1.

```python
CONFIGS = {
    "f4_lite":  {"NTSXSIM": 0.20, "NTSDSIM": 0.05, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "f4_mod":   {"NTSXSIM": 0.15, "NTSDSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "f4_med":   {"NTSXSIM": 0.12, "NTSDSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.33, "TLTSIM": 0.15},
    "f4_heavy": {"NTSXSIM": 0.10, "NTSDSIM": 0.20, "GDESIM": 0.25, "KMLMSIM": 0.30, "TLTSIM": 0.15},
}
```

- [ ] **Steps**: Same template. Citation `[risk_parity, ch.5, p.10]` + WisdomTree NTSD prospectus. BASE_MEMORY (total=35, n_trials=130). Commit `feat(long_term_portfolio/iter-035): F4 Global Stacking-only finalist`.

---

## Task 18: Iter 036 — F5 Global Factor-only construction

```python
CONFIGS = {
    "f5_lite":              {"VTISIM": 0.25, "VEASIM": 0.12, "VWOSIM": 0.05, "AVUVSIM": 0.10, "AVDVSIM": 0.08, "AVEMSIM": 0.05, "SPMOSIM": 0.08, "IDMOSIM": 0.05, "KMLMSIM": 0.15, "TLTSIM": 0.07},
    "f5_factor_balanced":   {"VTISIM": 0.18, "VEASIM": 0.10, "VWOSIM": 0.04, "AVUVSIM": 0.12, "AVDVSIM": 0.10, "AVEMSIM": 0.06, "SPMOSIM": 0.10, "IDMOSIM": 0.06, "KMLMSIM": 0.18, "TLTSIM": 0.06},
    "f5_factor_max":        {"VTISIM": 0.12, "VEASIM": 0.08, "VWOSIM": 0.03, "AVUVSIM": 0.15, "AVDVSIM": 0.12, "AVEMSIM": 0.08, "SPMOSIM": 0.12, "IDMOSIM": 0.08, "KMLMSIM": 0.16, "TLTSIM": 0.06},
    "f5_no_momentum":       {"VTISIM": 0.25, "VEASIM": 0.12, "VWOSIM": 0.05, "AVUVSIM": 0.18, "AVDVSIM": 0.12, "AVEMSIM": 0.08, "SPMOSIM": 0.0,  "IDMOSIM": 0.0,  "KMLMSIM": 0.15, "TLTSIM": 0.05},
}
```

- [ ] **Step 1-2**: Create dir, hypothesis.md (cite `[ilmanen_expected_returns, ch.19]`), backtest.py.
- [ ] **Step 3**: Execute. Verify weights sum to 1.0 in each config (note f5_no_momentum has 0% momentum sleeves — checks if momentum matters).
- [ ] **Step 4**: BASE_MEMORY (total=36, n_trials=134). Note: 8-10 ETFs makes this most complex finalist. Commit `feat(long_term_portfolio/iter-036): F5 Global Factor-only finalist`.

---

## Task 19: Iter 037 — F6 Global Hybrid construction

```python
CONFIGS = {
    "f6_lite":         {"NTSXSIM": 0.15, "NTSDSIM": 0.08, "GDESIM": 0.22, "KMLMSIM": 0.28, "TLTSIM": 0.12, "AVUVSIM": 0.05, "AVDVSIM": 0.04, "AVEMSIM": 0.02, "SPMOSIM": 0.02, "IDMOSIM": 0.02},
    "f6_balanced":     {"NTSXSIM": 0.12, "NTSDSIM": 0.10, "GDESIM": 0.20, "KMLMSIM": 0.25, "TLTSIM": 0.10, "AVUVSIM": 0.06, "AVDVSIM": 0.05, "AVEMSIM": 0.03, "SPMOSIM": 0.05, "IDMOSIM": 0.04},
    "f6_factor_heavy": {"NTSXSIM": 0.10, "NTSDSIM": 0.10, "GDESIM": 0.18, "KMLMSIM": 0.22, "TLTSIM": 0.10, "AVUVSIM": 0.08, "AVDVSIM": 0.06, "AVEMSIM": 0.04, "SPMOSIM": 0.07, "IDMOSIM": 0.05},
    "f6_intl_heavy":   {"NTSXSIM": 0.12, "NTSDSIM": 0.15, "GDESIM": 0.18, "KMLMSIM": 0.22, "TLTSIM": 0.10, "AVUVSIM": 0.05, "AVDVSIM": 0.07, "AVEMSIM": 0.04, "SPMOSIM": 0.04, "IDMOSIM": 0.03},
}
```

- [ ] **Step 1-3**: Same template. Citation `[risk_parity, ch.5, p.10]` + `[ilmanen_expected_returns, ch.19]`. BASE_MEMORY (total=37, n_trials=138). Commit.

---

## Task 20: Iter 038 — F7 US Stacked-MF construction

```python
CONFIGS = {
    "f7_lite":       {"NTSXSIM": 0.25, "RSSTSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.20, "TLTSIM": 0.15},
    "f7_balanced":   {"NTSXSIM": 0.15, "RSSTSIM": 0.30, "GDESIM": 0.25, "KMLMSIM": 0.15, "TLTSIM": 0.15},
    "f7_rsst_heavy": {"NTSXSIM": 0.10, "RSSTSIM": 0.40, "GDESIM": 0.25, "KMLMSIM": 0.10, "TLTSIM": 0.15},
    "f7_pure_stack": {"RSSTSIM": 0.50, "GDESIM": 0.25, "KMLMSIM": 0.10, "TLTSIM": 0.15},  # NOTE 4 ETFs only
}
```

- [ ] **Step 1**: Create dir `038-2026-04-30-F7-US-StackedMF/`, hypothesis.md citing `[risk_parity, ch.5]` + ReSolve methodology. Document KILL #5.
- [ ] **Step 2**: Verify f7_pure_stack weights sum to 1.0 (0.50+0.25+0.10+0.15=1.00 ✓). Verify others.
- [ ] **Step 3**: KILL #5 check (RSST synth standalone Sharpe vs theoretical max).
- [ ] **Step 4**: Execute, review.
- [ ] **Step 5**: BASE_MEMORY (total=38, n_trials=142). Commit `feat(long_term_portfolio/iter-038): F7 US Stacked-MF wildcard finalist`.

---

## Task 21: Phase 2 winner selection (manual review)

**Files:**
- Create: `studies/long_term_portfolio/PHASE_2_WINNERS.md`

- [ ] **Step 1: Aggregate verdicts from iters 033-038**

```bash
cd /var/www/pessoal/ai-trade && for i in 033 034 035 036 037 038; do
  echo "=== iter $i ==="
  cat studies/long_term_portfolio/iterations/$i-*/verdict.json | jq '{slug: .hypothesis_slug, score: .total_score, sharpe_per_dataset: [.metrics_used | to_entries | .[] | {ds: .key, s: .value.sharpe}]}'
done
```

- [ ] **Step 2: Build PHASE_2_WINNERS.md with provisional ranking**

```markdown
# Phase 2 Provisional Ranking (pre-MF-sensitivity)

| F | iter | slug | sharpe lh / vt / ndx | score | tier | ETF count | notional |
|---|---|---|---|---:|---|---:|---:|
| F1 | 023 | iter023 baseline | 1.189 / 1.004 / 1.135 | 86 NEW | STRONG | 4 | 132% |
| F2 | 033 | F2-US-Factor | ... | ... | ... | 6 | 100% |
| F3 | 034 | F3-US-Hybrid | ... | ... | ... | 6 | 135% |
| F4 | 035 | F4-Global-Stk | ... | ... | ... | 5 | 140% |
| F5 | 036 | F5-Global-Fct | ... | ... | ... | 8-10 | 100% |
| F6 | 037 | F6-Global-Hyb | ... | ... | ... | 10 | 150% |
| F7 | 038 | F7-US-StackedMF | ... | ... | ... | 4-5 | 150-160% |

## Provisional winner (highest mean Sharpe + score)
WINNER = F? (slug from above)

This finalist proceeds to iter 039 MF sleeve sensitivity test.
```

- [ ] **Step 3: Update BASE_MEMORY frontmatter**

`phase_2_complete: true`
`provisional_winner_iter: <iter_number>`

- [ ] **Step 4: Commit**

```bash
git add studies/long_term_portfolio/PHASE_2_WINNERS.md studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "docs(long_term_portfolio): Phase 2 complete, identify provisional winner for MF sensitivity"
```

---

## Task 22: Iter 039 — MF sleeve sensitivity on winner

**Files:**
- Create: `studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity/hypothesis.md`
- Create: `studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity/backtest.py`

- [ ] **Step 1: Create iter dir + hypothesis.md**

```bash
mkdir -p /var/www/pessoal/ai-trade/studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity
```

`hypothesis.md`:

```markdown
# Iter 039 — MF sleeve sensitivity on Phase 2 winner

## Hypothesis

The Phase 2 winner finalist used KMLMSIM as MF sleeve (loop default).
Test 4 alternative MF sleeves on the same finalist weights to determine
deploy-ready MF choice: KMLM (baseline), DBMF, 50/50 split, CTA Simplify
proxy.

## Primary citation
`[ilmanen_expected_returns, ch.19]` MF crisis-alpha role; iMGP DBi DBMF
prospectus + KFA MLM Index prospectus.

## Configs (4)

Replace winner finalist's KMLM sleeve with:
| config | MF sleeve substitution |
|---|---|
| mf_kmlm | KMLMSIM (baseline) |
| mf_dbmf | DBMFSIM (5× AUM, SG CTA Index proxy) |
| mf_split | 50% KMLMSIM + 50% DBMFSIM |
| mf_cta_proxy | KMLMSIM × 1.0 with INCOMPLETE flag for CTA Simplify |

Window caveat: DBMFSIM 26y (1999+); intersected window for fair comparison.

## Selection rule
Highest mean(gross_Sharpe) across 3 datasets where DBMF and KMLM both have data
(1999-2026 effective).
```

- [ ] **Step 2: Create backtest.py — substitutes the WINNER's KMLM with each candidate**

```python
"""Iter 039 backtest: MF sleeve sensitivity on Phase 2 winner."""
import json
from pathlib import Path
from studies.long_term_portfolio.run_iter import run_iter_full


# READ winner's selected config from PHASE_2_WINNERS.md / its verdict.json
# Substitute KMLMSIM ticker in winner's config with alternatives below
WINNER_ITER = ___  # filled manually after Task 21
WINNER_VERDICT = json.loads(Path(f"studies/long_term_portfolio/iterations/{WINNER_ITER}/verdict.json").read_text())
WINNER_CONFIG = WINNER_VERDICT["all_configs_metrics"][WINNER_VERDICT["selected_config"]]
# (the selected config dict needs to be re-extracted; alternatively look it up in the iter's backtest.py CONFIGS)

# Take the winner config and define 4 MF substitutions
WINNER_BASE = {k: v for k, v in WINNER_CONFIG.items() if k != "KMLMSIM"}
KMLM_WEIGHT = WINNER_CONFIG.get("KMLMSIM", 0.0)

CONFIGS = {
    "mf_kmlm":      {**WINNER_BASE, "KMLMSIM": KMLM_WEIGHT},
    "mf_dbmf":      {**WINNER_BASE, "DBMFSIM": KMLM_WEIGHT},
    "mf_split":     {**WINNER_BASE, "KMLMSIM": KMLM_WEIGHT * 0.5, "DBMFSIM": KMLM_WEIGHT * 0.5},
    "mf_cta_proxy": {**WINNER_BASE, "KMLMSIM": KMLM_WEIGHT},  # KMLM as CTA Simplify proxy with INCOMPLETE flag
}

if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=39, iter_dir=iter_dir, hypothesis_slug="MF-sensitivity",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS, cumulative_n_trials=142 + len(CONFIGS),
    )
    print(f"iter 039 MF sensitivity: best={verdict['selected_config']}, "
          f"score={verdict['total_score']}")
```

- [ ] **Step 3: Manually fill WINNER_ITER and WINNER_CONFIG**

After Task 21, replace `___` with iter number from PHASE_2_WINNERS.md. Re-extract the selected config dict from that iter's backtest.py CONFIGS dict.

- [ ] **Step 4: Execute**

```bash
cd /var/www/pessoal/ai-trade && python studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity/backtest.py
```

- [ ] **Step 5: Document MF sleeve recommendation**

In the iter's final_report.md, add "Recommended MF sleeve" section based on best config. If `mf_dbmf` wins → recommend DBMF for deploy. If `mf_split` wins → recommend 50/50 in deploy.

- [ ] **Step 6: BASE_MEMORY append (total=39, n_trials=146). Commit.**

```bash
git add studies/long_term_portfolio/iterations/039-2026-04-30-MF-sensitivity/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio/iter-039): MF sleeve sensitivity on Phase 2 winner, recommended MF=<MF>"
```

---

## Task 23: FINAL_REPORT_seven_portfolios.md production

**Files:**
- Create: `studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md`

- [ ] **Step 1: Aggregate all 7 finalists' metrics**

```bash
cd /var/www/pessoal/ai-trade && for i in 023 033 034 035 036 037 038; do
  echo "=== iter $i ==="
  cat studies/long_term_portfolio/iterations/$i-*/verdict.json | jq '{slug: .hypothesis_slug, score: .total_score, sharpe: [.metrics_used | to_entries | .[] | {ds: .key, s: .value.sharpe}], cagr: [.metrics_used | to_entries | .[] | {ds: .key, c: .value.cagr}], mdd: [.metrics_used | to_entries | .[] | {ds: .key, m: .value.mdd}]}'
done
```

- [ ] **Step 2: Compute multi-criteria score per finalist**

For each finalist, apply rubric from spec §Phase 4:

```python
# Helper script — paste in REPL or save as compute_multi_criteria.py
def compute_multi_criteria_score(metrics, etf_count, weighted_ter, regime_robustness, deploy_ease):
    spy_sharpe = (0.680 + 0.900 + 0.900) / 3  # 0.827
    iter023_sharpe = 1.109
    spy_cagr = (0.1147 + 0.1497 + 0.1497) / 3  # 0.1380
    spy_mdd = (0.5514 + 0.3370 + 0.3370) / 3  # 0.4085

    mean_sharpe = sum(metrics["sharpe"]) / 3
    mean_cagr = sum(metrics["cagr"]) / 3
    mean_mdd = sum(metrics["mdd"]) / 3

    # C1 Sharpe (25pts max): linear normalization between SPY and 2× iter 023 Sharpe range
    c1 = 25 * max(0, min(1, (mean_sharpe - spy_sharpe) / (2 * iter023_sharpe - spy_sharpe)))

    # C2 CAGR (12pts): +1pt per 0.5pp edge over SPY, capped 12
    c2 = min(12, max(0, (mean_cagr - spy_cagr) * 200))  # 100*0.5pp granularity

    # C3 MDD safety (13pts): +1pt per 1pp lower MDD, capped 13
    c3 = min(13, max(0, (spy_mdd - mean_mdd) * 100))

    # C4 Simplicity (15pts): table lookup by ETF count
    c4_table = {4: 100, 5: 90, 6: 80, 7: 70, 8: 60, 9: 50, 10: 40}
    c4 = (c4_table.get(min(etf_count, 10), 40) / 100) * 15

    # C5 Expense (10pts): TER tier
    if weighted_ter < 0.0040: c5 = 10
    elif weighted_ter < 0.0060: c5 = 8.5
    elif weighted_ter < 0.0080: c5 = 7
    elif weighted_ter < 0.0100: c5 = 5.5
    else: c5 = 4

    # C6 Regime robustness (10pts): rolling 5y % positive Sharpe
    c6 = regime_robustness * 10  # if 1.0 → 10pts

    # C7 Deploy ease (15pts): hard gate on Inter availability
    c7 = deploy_ease  # 0 if any ETF unavailable; else AUM-tier-based 0-15

    return c1 + c2 + c3 + c4 + c5 + c6 + c7
```

- [ ] **Step 3: Build the comparative report**

Create `studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md` (~3-4 pages):

```markdown
# Final Report — Seven-Portfolio Finalist Comparison

**Date:** 2026-04-30
**Sweep:** Iter 027-039 per `SWEEP_PLAN_iter_027_to_039.md`
**Decision:** Choose ONE portfolio for 20-30y retirement deploy.

## Executive summary

[2-3 sentences: which finalist scores highest, what trade-offs are
relevant, and the recommended choice + alternative.]

## Comparative table

(Insert full 7-finalist comparative table with all metrics.)

## Per-finalist trade-off narratives

### F1 US-Stacking-only (iter 023)
- Strengths:
- Weaknesses:
- Best regime:
- Worst regime:
- 20-30y deploy considerations:

### F2 US-Factor-only (iter 033)
[same template]

### F3 US-Hybrid (iter 034)
[same template]

### F4 Global-Stacking-only (iter 035)
[same template]

### F5 Global-Factor-only (iter 036)
[same template]

### F6 Global-Hybrid (iter 037)
[same template]

### F7 US-Stacked-MF (iter 038)
[same template]

## Cross-cutting analysis

### Stacking vs Factor vs Stacked-MF
(Compare F1+F4 [stacking] vs F2+F5 [factor] vs F7 [stacked-MF].)

### US vs Global
(Compare F1+F2+F3+F7 [US] vs F4+F5+F6 [Global].)

### Hybrid premium
(Does F3/F6 beat pure philosophies?)

### Regime regret analysis
- If next 20-30y is intl-led (1980s-style), winner = (F4/F5/F6 likely)
- If US dominance continues (2010s-style), winner = (F1/F3/F7 likely)
- Regret-minimizing choice: (likely F3 or F6 hybrid for diversification)

## MF sleeve recommendation (from iter 039)

Recommended MF sleeve for deploy: **(KMLM/DBMF/split, with rationale)**.

## Recommendation

**Primary recommendation:** F<n> [slug] with MF sleeve = <MF>.
**Alternative if simplicity matters more:** F<n> [slug].
**Alternative if maximum diversification matters more:** F<n> [slug].

## Mandate §7 override request draft

[Draft text for user to send/sign-off authorizing the chosen finalist
for live deployment, citing all 13 supporting iters and the multi-
criteria scoring rubric.]

## Citations

(All citations from spec §Citations + any new ones from sweep results.)
```

- [ ] **Step 4: Fill in concrete numbers from verdict.json files**

Read each iter's verdict.json. Substitute `?` placeholders with actual
Sharpe/CAGR/MDD/score values. Compute multi-criteria score using the
helper from Step 2.

- [ ] **Step 5: Write narratives — strengths/weaknesses per finalist**

For each finalist, write 4-6 bullet trade-off points based on metrics
+ ETF complexity + regime expectations.

- [ ] **Step 6: Run a sanity sense-check**

The recommendation should:
- Score the highest on multi-criteria, OR
- Score within 5pts of highest with substantially better simplicity/safety profile
- Have all ETFs available on Inter Internacional (C7 ≥ 5)
- Pass 7-gate battery on ≥2/3 datasets
- Have DSR p-value < 0.05 cumulative

If the chosen finalist violates any → revisit.

- [ ] **Step 7: Commit**

```bash
git add studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md
git commit -m "docs(long_term_portfolio): FINAL_REPORT seven-portfolio comparative scoring + recommendation"
```

---

## Task 24: User decision + mandate §7 override draft

**Files:**
- Modify: `studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md` (incorporate user decision)
- Create: `jornada/2026-04-30-HHMM-longterm-final-pick.md`

- [ ] **Step 1: Present FINAL_REPORT_seven_portfolios.md to user**

Show summary of recommendation. Ask:
- Accept primary recommendation?
- Switch to simplicity-favored alternative?
- Switch to max-diversification alternative?
- Need additional iter/sensitivity?

- [ ] **Step 2: Write the jornada entry**

Create `jornada/2026-04-30-HHMM-longterm-final-pick.md`:

```markdown
# Long-Term Portfolio — Final Pick

Após 39 iters de sweep (013 batches: 6 single-axis + 6 finalists + 1 MF
sensitivity), o portfolio escolhido pra deploy 20-30y de aposentadoria
é **F<n> [slug]** com MF sleeve **<MF>**.

## Composição
[Final ETF weights + tickers]

## Por que esse e não outro
[Trade-offs per multi-criteria scoring + regime regret analysis]

## Próximos passos
- Solicitar mandate §7 override
- Setup conta Inter Internacional (se ainda não)
- Comprar ETFs em proporção
- Definir cronograma de rebalance (anual recomendado)
- Definir gatilhos de revisão (regime change, ETF closure, etc.)

## Citações
[risk_parity, ch.5, p.10] — tese matriz capital-eficiente
[risk_parity, ch.2, p.37-41] — factor framework
[ilmanen_expected_returns, ch.19] — diversificação geográfica
[advances_fin_ml, p.208-211, p.222-223] — gates PBO+DSR
```

- [ ] **Step 3: Update jornada/README.md**

Prepend new entry to the index list. Update "Onde estamos hoje" section
to reflect the final pick + deploy plan.

- [ ] **Step 4: Update BASE_MEMORY frontmatter**

`status: pick_complete`
`final_pick_iter: <iter>`
`final_pick_slug: "<slug>"`
`recommended_mf_sleeve: "<MF>"`
`mandate_override_pending: true`

- [ ] **Step 5: Commit**

```bash
git add studies/long_term_portfolio/FINAL_REPORT_seven_portfolios.md jornada/ studies/long_term_portfolio/BASE_MEMORY.md
git commit -m "feat(long_term_portfolio): final pick complete — F<n> selected for 20-30y deploy after 39-iter sweep"
```

---

## Self-Review

(Run after writing the entire plan; fix issues inline.)

**1. Spec coverage check:**
- ✅ Inter Internacional pre-check → Task 1
- ✅ Synth functions (NTSD/AVUV/AVDV/AVEM/SPMO/IDMO/RSST/CTA-proxy) → Tasks 2-6
- ✅ run_iter helper → Task 7
- ✅ Phase 1 single-axis isolation (6 iters) → Tasks 8-13
- ✅ Phase 1 winner selection → Task 14
- ✅ Phase 2 finalist construction (5 iters: F2/F3/F4/F5/F6/F7 → 6 actually) → Tasks 15-20
- ✅ Phase 2 winner selection → Task 21
- ✅ Phase 3 MF sleeve sensitivity (iter 039) → Task 22
- ✅ Phase 4 comparative report → Task 23
- ✅ User decision + mandate override → Task 24
- ✅ KILL conditions referenced (KILL #1-5) in relevant iters
- ✅ DSR cumulative count tracked across BASE_MEMORY updates
- ✅ Window caveats (AVEM 32y, DBMF 26y) called out

**2. Placeholder scan:**
- "TBD"/"TODO" patterns: ❌ none in plan body
- "<status>"/"<score>" in commit messages: intentional templates
- "?" in comparative table template: intentional, fills after execution
- WINNER_ITER `___` in Task 22: intentional, filled after Task 21
- "(yes/no)" in PHASE_1_WINNERS.md template: intentional, fills after Phase 1 execution

**3. Type consistency:**
- Synth function naming: `*_synth_returns` (Tasks 3-6) and `*_synth_returns_from_cache` consistent ✓
- Config dict structure `{ticker: weight}` consistent across all backtest.py files ✓
- run_iter signature: same iter_n, iter_dir, hypothesis_slug, primary_citation, configs, cumulative_n_trials throughout ✓
- Ticker naming: SIM-suffixed (NTSXSIM, AVUVSIM, etc.) consistent ✓

No issues found.
