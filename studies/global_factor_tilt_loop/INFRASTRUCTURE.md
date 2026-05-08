# Global Factor-Tilt Loop — Available Infrastructure

**Reuse, don't rebuild.** Each iteration should compose from these
modules. Build new modules only when the mechanism is qualitatively new
(then add a TDD spec under `tests/test_<slug>.py` first).

## Simulators

- `src/market_lab/backtest/strategies/ema_sma_threshold_educational.py`
- `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`
  (stop + risk + combined + numpy cross-lib)

## Data loaders

- `src/market_lab/backtest/data/testfolio_loader.py` (synth long-window)
- `src/market_lab/backtest/data/macro_data_loader.py` (EBP / T10Y3M / CAPE / VIX)
- `src/market_lab/backtest/grid/real_etf_regime_runner.py` (SPY/UPRO, QQQ/TQQQ bundles)

## Validation

- `src/market_lab/backtest/validation/pbo.py` (PBO via CSCV)
- `src/market_lab/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/market_lab/backtest/validation/walk_forward.py`
- `src/market_lab/backtest/validation/cpcv.py`
- `src/market_lab/backtest/validation/permutation.py`

## Metrics

- `src/market_lab/backtest/metrics/performance.py` (CAGR / Sharpe / MDD / etc.)

## Signals

- `src/market_lab/backtest/signals/risk_score.py` (z-score sigmoid composite)

## Loop-local helpers (this directory)

- `scoring.py` — score rubric + tier classification (the `BENCHMARKS`
  dict has VT/VTSIM/QQQ benchmark numbers)
- `plot_helper.py` — equity-vs-benchmark plotting (vt_real uses VTSIM
  testfolio cache; ndx_real uses QQQ Tiingo)
- `cross_lib_validator.py` — 4-method metric parity check
- `rescore_v2.py` — DSR per-iter convention rescoring
- `long_window_validator.py` — 56y synth re-validation, seeded with
  V_HYBRID+MF and global-return-stacked-allweather reference cells

---

## Data cache — global universe

### Tiingo daily prices (`data/tiingo/daily/prices/`)

| ticker | role | status |
|---|---|---|
| **VTI**  | US Total Market | ✅ pulled |
| **VEA**  | Intl Developed | ✅ pulled |
| **VWO**  | Emerging Markets | ✅ pulled |
| **EFA**  | MSCI EAFE | ✅ pulled |
| **GLD**  | Gold | ✅ pulled |
| **TLT**  | 20+y Treasury | ✅ pulled |
| **IEF**  | 7-10y Treasury | ✅ pulled |
| **AGG**  | Aggregate Bond | ✅ pulled |
| **SPY/UPRO/SSO/QQQ/QLD/TQQQ** | US LETF bundle | ✅ existing |
| **VT**   | Total World | ❌ **NOT PULLED** — TODO |
| **VXUS** | Total Intl ex-US | ❌ NOT PULLED — TODO |
| **VBR**  | US Small-Cap Value | ❌ NOT PULLED — TODO |
| **VSS**  | Intl Developed Small-Cap | ❌ NOT PULLED — TODO |
| **AVUS / AVDE / AVEM / AVNM** | Avantis broad | ❌ NOT PULLED — TODO |
| **AVUV / AVDV / AVES** | Avantis sleeves | ❌ NOT PULLED — TODO |

Until VT is pulled, `vt_real` benchmark uses VTSIM (testfolio synth)
truncated to 2008-06+. Document this assumption in any iter that uses
the `vt_real` slot.

### Testfolio synthetic cache (`data/testfolio/cache/history.parquet`)

Long-window synths (testfolio quality, ETF-grade methodology):

| ticker | inception in cache | role |
|---|---|---|
| **VTSIM** | 1969-12-31 (56y) | Total World — **the educational benchmark** |
| **VTISIM** | 1926-07-01 (99y) | US Total Market |
| **VBRSIM** | 1926-07-01 (99y) | US Small-Cap Value (proxy for AVUV) |
| **VEASIM** | 1969-12-31 (56y) | Intl Developed |
| **VWOSIM** | 1994-05-04 (32y) | Emerging Markets |
| **VXUSSIM** | 1969-12-31 (56y) | Total Intl ex-US |
| **VSSSIM** | (newly pulled 2026-04-26) | Intl Developed Small-Cap |
| **EFVSIM** | (newly pulled 2026-04-26) | EAFE Value |
| **GDESIM** | 1968-04-01 (58y) | 90% S&P + 90% gold (capital efficient) |
| **RSSBSIM** | 1969-12-31 (56y) | Global Eq + Treasury return-stacked |
| **KMLMSIM** | 1987-12-31 (38y) | KFA Mount Lucas managed futures |
| **DBMFSIM** | 2000-01-03 (26y) | iMGP DBi Managed Futures |
| **IEFSIM** | 1962-01-02 (64y) | 7-10y Treasury |
| **TLTSIM** | (newly pulled 2026-04-26) | 20+y Treasury |
| **BNDSIM** | 1986-12-11 (40y) | Aggregate Bond |
| **CASHX** | 1885-03-20 (140y) | T-bill / cash collateral |
| **ZROZSIM** | (existing) | 25y Zero-coupon |
| **GLDSIM** | (existing) | Gold |
| **SPYSIM/QQQSIM/SSOSIM/QLDSIM/UPROSIM/TQQQSIM** | 1986+ | US LETF bundle (carryover) |

NTSX_synth via testfolio formula (validated 2026-04-26):
`0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX`. Use this for any "global
return-stack" experimental allocations.

### Macro (`data/external/macro/`)

EBP / T10Y3M / CAPE / VIX — same as strategy_hunt_loop carryover.

---

## Knowledge base

- `books/summaries/` — 33 absorbed books (slug ↔ title in `books/MAPPING.md`)
- `knowledge/SKILL.md` — aggregated quick-reference

---

## deploy_studies references (sibling loop)

The companion `studies/strategy_hunt_loop/deploy_studies/` directory
contains validated portfolio variants with empirical numbers:

- `deploy_studies/portfolio_variants/PORTFOLIO_VARIANTS_REPORT.md` —
  V_HYBRID+MF (Sharpe 0.743, CAGR 10.91%, MDD 44.71%, 32y) is the
  WINNER and reference benchmark.
- `deploy_studies/v1_vs_planoc/V1_VS_PLANOC_REPORT.md` —
  V1 NTSX+GDE 67/33 (Sharpe 0.809, CAGR 13.50%, MDD 44.37%, 32y)
  vs Plano C V3_1 v3.5 (Sharpe 0.671, CAGR 10.94%, MDD 52.43%, 32y).

These are READ-ONLY references — do not modify.

---

## Iteration-specific code (reusable across iters)

This loop has no carryover iteration code yet. Iter winners may
contribute reusable modules, in which case add them here with a
1-line description.
