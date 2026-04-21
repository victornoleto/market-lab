# SSO daily — c03 EMA100+TLT Binary Regime (iter 31) [SWING BROKER]

**Strategy:** SPY > EMA100 (prev day) → 100% SSO; else → 100% TLT.
**Asset:** SSO (ProShares Ultra S&P 500, 2× SPY).
**Signal:** SPY EMA100 regime `[leverage_for_the_long_run, p.31]` — Gayed TLT variant.
**Off-leg:** TLT (iShares 20+ Year Treasury Bond ETF).
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (SSO synthetic pre-2006: 2× SPX daily - drag - expense `[leverage_for_the_long_run, ch.2]`).
**Window:** 2002-07-26 → 2026-04-15 (23.7y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 8.46% |
| CAGR net (15% IR) | 7.19% |
| Sharpe gross | 0.457 |
| Sharpe net | 0.389 |
| MaxDD | -57.9% |
| Calmar | 0.146 |
| WF | 7/8 |
| OOS Sharpe | 0.118 (IS=0.543) |
| FWD Sharpe | -0.172 |
| DSR p-value | 0.3566 (n_trials=18) |
| n_bars | 5967 |

## SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 9.27% |
| SPY CAGR net | 7.88% |
| SPY Sharpe | 0.564 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.436 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.3566) |
| Gate 3 — WF ≥6/8 | ✓ PASS (7/8) |
| Gate 4 — OOS holdout | ✗ FAIL (OOS_S=0.118) |
| Gate 5 — FWD stress | ✗ FAIL (FWD_S=-0.172) |
| Eco 1 — beats SPY net | ✗ FAIL |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.146) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.389) |
| **Pre-pass (no PBO)** | **✗ DSR, OOS, FWD, SPY_BEAT, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.313 | -0.353 | 0.796 | 0.870 | 0.256 | 0.486 | 0.103 | 1.003

OOS window: 2021-07-14 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Stage 2 concordance (Tiingo real SSO)

Stage 2 data unavailable — Tiingo SSO parquet missing or too short.

## Cross-lib concordance (bt)

| Metric | Value |
|--------|-------|
| bt CAGR | 9.81% |
| ΔCAGR | 1.34pp — ✓ CONCORDANT |

## Citations

- `[leverage_for_the_long_run, p.31]` — EMA100+TLT Gayed variant
- `[leverage_for_the_long_run, ch.2]` — SSO synthetic pre-2006: 2× SPX returns - drag - expense
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c03 tests EMA100+TLT. TLT off-leg is the 'flight-to-safety' variant — [leverage_for_the_long_run, p.31].
- SSO pre-2006: synthetic from reference_prices.parquet (2× SPX total return).
- Stage 2 uses Tiingo real SSO (2006-06-21 onwards) — overlap with Stage 1 real SSO data.
- DSR n_trials = 18 (cumulative from trial_count.json).
- Window constrained by TLT first date (2002-07-26) and TLT last date (2026-04-15).
