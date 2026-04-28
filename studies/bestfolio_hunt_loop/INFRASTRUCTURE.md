# Bestfolio Hunt Loop — Available Infrastructure

**Reuse, don't rebuild.** Each iteration should compose from these
modules. Build new modules only when the mechanism is qualitatively new
(then add a TDD spec under `tests/test_<slug>.py` first).

## Simulators

- `src/ai_trade/backtest/strategies/ema_sma_threshold_educational.py`
- `src/ai_trade/backtest/strategies/stop_loss_and_risk_signals.py`

## Data loaders

- `src/ai_trade/backtest/data/testfolio_loader.py` (synth long-window)
- `src/ai_trade/backtest/data/macro_data_loader.py` (EBP / T10Y3M / CAPE / VIX)

## Validation

- `src/ai_trade/backtest/validation/pbo.py` (PBO via CSCV)
- `src/ai_trade/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/ai_trade/backtest/validation/walk_forward.py`
- `src/ai_trade/backtest/validation/cpcv.py`
- `src/ai_trade/backtest/validation/permutation.py`

## Metrics

- `src/ai_trade/backtest/metrics/performance.py` (CAGR / Sharpe / MDD / etc.)

## Tax engine (MANDATORY — Lei 14.754/2023)

- `studies/global_factor_tilt_loop/tax_engine_v2.py` — `AnnualDarfEngine`

  **ALWAYS use this for any net-of-tax analysis.** Never use the old
  `DarfCostBasisEngine` (monthly DARF — incorrect per Lei 14.754/2023).
  Key rule: DARF settled once per calendar year, indefinite loss carryforward.

  ```python
  import sys; sys.path.insert(0, "studies/global_factor_tilt_loop")
  from tax_engine_v2 import AnnualDarfEngine
  ```

## Loop-local helpers (this directory)

- `scoring.py` — score rubric + tier classification
  (BENCHMARKS = iter 009 HAA+Gold: edu S=1.120, vt S=1.061, ndx S=0.954)
- `plot_helper.py` — equity-vs-benchmark plotting (mirrors global_factor_tilt_loop)
- `studies/global_factor_tilt_loop/cross_lib_validator.py` — 4-method metric parity
- `studies/global_factor_tilt_loop/rescore_v2.py` — DSR per-iter convention rescoring

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
| **VT**   | Total World | ❌ NOT PULLED — TODO |
| **VXUS** | Total Intl ex-US | ❌ NOT PULLED — TODO |

Until VT is pulled, `vt_real` benchmark uses VTSIM (testfolio synth)
truncated to 2008-06+. Document this assumption in any iter that uses
the `vt_real` slot.

### Testfolio synthetic cache (`data/testfolio/cache/history.parquet`)

| ticker | inception in cache | role |
|---|---|---|
| **VTSIM** | 1969-12-31 (56y) | Total World — educational benchmark + vt_real proxy |
| **VTISIM** | 1926-07-01 (99y) | US Total Market |
| **VBRSIM** | 1926-07-01 (99y) | US Small-Cap Value (proxy for AVUV) |
| **VEASIM** | 1969-12-31 (56y) | Intl Developed |
| **VWOSIM** | 1994-05-04 (32y) | Emerging Markets (HAA canary) |
| **VXUSSIM** | 1969-12-31 (56y) | Total Intl ex-US |
| **VSSSIM** | (pulled 2026-04-26) | Intl Developed Small-Cap |
| **EFVSIM** | (pulled 2026-04-26) | EAFE Value |
| **GDESIM** | 1968-04-01 (58y) | 90% S&P + 90% gold (capital efficient) — GDE synth |
| **RSSBSIM** | 1969-12-31 (56y) | Global Eq + Treasury return-stacked — RSSB synth |
| **KMLMSIM** | 1987-12-31 (38y) | KFA Mount Lucas managed futures |
| **DBMFSIM** | 2000-01-03 (26y) | iMGP DBi Managed Futures |
| **IEFSIM** | 1962-01-02 (64y) | 7-10y Treasury |
| **TLTSIM** | (pulled 2026-04-26) | 20+y Treasury |
| **BNDSIM** | 1986-12-11 (40y) | Aggregate Bond |
| **CASHX** | 1885-03-20 (140y) | T-bill / cash collateral |
| **ZROZSIM** | (existing) | 25y Zero-coupon |
| **GLDSIM** | (existing) | Gold |
| **SPYSIM/QQQSIM/SSOSIM/QLDSIM/UPROSIM/TQQQSIM** | 1986+ | US LETF bundle (carryover) |

NTSXSIM formula: `0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX`
(validated 2026-04-26 in deploy_studies).

RSIT synth (pending launch ~mai/2026):
`VEASIM × 1.0 + KMLMSIM × 1.0 − 50bps/y financing`
Mark as INCOMPLETE synth when used.

---

## Knowledge base

- `books/summaries/` — 33 absorbed books (slug ↔ title in `books/MAPPING.md`)
- `knowledge/SKILL.md` — aggregated quick-reference

---

## Reference — global_factor_tilt_loop (FROZEN, predecessor)

- `studies/global_factor_tilt_loop/iterations/009-*/` — iter 009 HAA+Gold (benchmark)
  Sharpe frontier: edu 1.120 / vt 1.061 / ndx 0.954
- `studies/global_factor_tilt_loop/iterations/013-*/` — iter 013 HAA+ZROZSIM
  CAGR frontier: edu 16.35% / S=1.011
- `studies/global_factor_tilt_loop/iterations/014-*/` — iter 014 annual-DARF rerun
  Net-of-tax HAA hybrid: vt S≈1.04
- `studies/global_factor_tilt_loop/deploy_studies/` — V_HYBRID+MF (Sharpe 0.743)
  and Plano C comparisons (READ-ONLY).

---

## Iteration-specific code (reusable across iters)

*(empty — loop not started; reusable modules from winning iters will be listed here)*
