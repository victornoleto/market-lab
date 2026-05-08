# UPRO daily — c03 EMA100+TLT Binary Regime (iter 33) [SWING BROKER]

**Strategy:** SPY > EMA100 (prev day) → 100% UPRO; else → 100% TLT.
**Asset:** UPRO (ProShares UltraPro S&P500, 3× S&P500).
**Signal:** SPY EMA100 regime `[leverage_for_the_long_run, p.31]` — Gayed TLT variant.
**Off-leg:** TLT (iShares 20+ Year Treasury Bond ETF).
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (Tiingo-first; UPRO pre-2009 synthetic 3×S&P500_TR).
**Window:** 2002-07-26 → 2026-04-15 (23.7y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 10.39% |
| CAGR net (15% IR) | 8.83% |
| Sharpe gross | 0.460 |
| Sharpe net | 0.391 |
| MaxDD | -68.5% |
| Calmar | 0.152 |
| WF | 7/8 |
| OOS Sharpe | 0.211 (IS=0.522) |
| FWD Sharpe | -0.182 |
| DSR p-value | 0.3697 (n_trials=20) |
| n_bars | 5967 |

## SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 9.27% |
| SPY CAGR net | 7.88% |
| SPY Sharpe | 0.564 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.495 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.3697) |
| Gate 3 — WF ≥6/8 | ✓ PASS (7/8) |
| Gate 4 — OOS holdout | ✗ FAIL (OOS_S=0.211) |
| Gate 5 — FWD stress | ✗ FAIL (FWD_S=-0.182) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.152) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.391) |
| **Pre-pass (no PBO)** | **✗ DSR, OOS, FWD, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.300 | -0.356 | 0.742 | 0.846 | 0.272 | 0.414 | 0.247 | 1.014

OOS window: 2021-07-14 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt)

| Metric | Value |
|--------|-------|
| bt CAGR | 12.40% |
| ΔCAGR | 2.01pp — ✓ CONCORDANT |

## Stage-2 concordance (Tiingo real UPRO)

| Metric | Value |
|--------|-------|
| Stage-2 CAGR (Tiingo real) | 16.98% |
| Stage-1 CAGR (overlap window) | 16.28% |
| ΔCAGR | 0.69pp — ✓ CONCORDANT |
| Window | 2009-06-25 → 2026-04-15 |

## Citations

- `[leverage_for_the_long_run, p.31]` — EMA100+TLT Gayed variant
- `[leverage_for_the_long_run, ch.2]` — 3× synthetic pre-2009 UPRO construction
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c03 tests EMA100+TLT. TLT off-leg is the 'flight-to-safety' variant — [leverage_for_the_long_run, p.31].
- UPRO pre-2009-06-25: synthetic 3×S&P500_TR in Stage-1 reference_prices.parquet.
- DSR n_trials = 20 (cumulative from trial_count.json; 19 completed + 1 this iter).
- Window constrained by TLT first date (2002-07-26) and TLT last date (2026-04-15).
