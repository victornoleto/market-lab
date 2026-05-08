# TQQQ daily — c03 EMA100+TLT Binary Regime (iter 32) [SWING BROKER]

**Strategy:** SPY > EMA100 (prev day) → 100% TQQQ; else → 100% TLT.
**Asset:** TQQQ (ProShares UltraPro QQQ, 3× QQQ).
**Signal:** SPY EMA100 regime `[leverage_for_the_long_run, p.31]` — Gayed TLT variant.
**Off-leg:** TLT (iShares 20+ Year Treasury Bond ETF).
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (Tiingo-first; TQQQ pre-2010 synthetic 3×QQQ_TR).
**Window:** 2002-07-26 → 2026-04-15 (23.7y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 17.95% |
| CAGR net (15% IR) | 15.26% |
| Sharpe gross | 0.594 |
| Sharpe net | 0.505 |
| MaxDD | -76.3% |
| Calmar | 0.235 |
| WF | 8/8 |
| OOS Sharpe | 0.251 (IS=0.685) |
| FWD Sharpe | 0.066 |
| DSR p-value | 0.1581 (n_trials=19) |
| n_bars | 5967 |

## SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 9.27% |
| SPY CAGR net | 7.88% |
| SPY Sharpe | 0.564 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.458 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1581) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✗ FAIL (OOS_S=0.251) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.066) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.235) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.505) |
| **Pre-pass (no PBO)** | **✗ DSR, OOS, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.186 | 0.180 | 0.905 | 0.998 | 0.931 | 0.594 | 0.280 | 0.951

OOS window: 2021-07-14 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt)

| Metric | Value |
|--------|-------|
| bt CAGR | 17.96% |
| ΔCAGR | 0.01pp — ✓ CONCORDANT |

## Stage-2 concordance (Tiingo real TQQQ)

| Metric | Value |
|--------|-------|
| Stage-2 CAGR (Tiingo real) | 27.08% |
| Stage-1 CAGR (overlap window) | 26.35% |
| ΔCAGR | 0.73pp — ✓ CONCORDANT |
| Window | 2010-02-11 → 2026-04-15 |

## Citations

- `[leverage_for_the_long_run, p.31]` — EMA100+TLT Gayed variant
- `[leverage_for_the_long_run, ch.2]` — 3× synthetic pre-2010 TQQQ construction
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c03 tests EMA100+TLT. TLT off-leg is the 'flight-to-safety' variant — [leverage_for_the_long_run, p.31].
- TQQQ pre-2010-02-11: synthetic 3×QQQ_TR in Stage-1 reference_prices.parquet.
- DSR n_trials = 19 (cumulative from trial_count.json; 18 completed + 1 this iter).
- Window constrained by TLT first date (2002-07-26) and TLT last date (2026-04-15).
