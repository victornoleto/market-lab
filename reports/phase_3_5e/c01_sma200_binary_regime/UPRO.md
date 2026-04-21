# UPRO daily — c01 SMA200 Binary Regime (iter 18) [SWING BROKER]

**Strategy:** SPY > SMA200 (prev day) → 100% UPRO; else → off-leg.
**Asset:** UPRO (ProShares UltraPro S&P 500, 3× SPX). Synthetic pre-2009.
**Signal:** SPY SMA200 regime `[leverage_for_the_long_run, ch.2]`.
**Off-legs:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.

**Per-ticker local PBO (informational, N=3 unreliable):** 0.056
  Note: N=3 — INFORMATIONAL ONLY (N<4, real PBO at aggregator). PBO=0.056

## Results table

| Config | Window | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | Pre-pass |
|--------|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-------|----------|---------|--------|----------|
| c01_sma200_cash | 24.9y | 13.82 | 11.74 | 0.564 | 0.480 | -55.7 | 0.248 | 7/8 | 0.58 | -1.07 | 0.1112 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_gld | 21.4y | 17.16 | 14.58 | 0.630 | 0.536 | -53.2 | 0.323 | 8/8 | 0.50 | -0.72 | 0.1020 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_tlt | 23.7y | 13.79 | 11.72 | 0.551 | 0.468 | -64.3 | 0.214 | 8/8 | 0.33 | -1.12 | 0.1583 | ✓ | ✗ | ✗ | ✗ |

## SPY benchmark (per-config, same window)

- **c01_sma200_cash** (24.9y): SPY CAGR=7.11% net=6.04% Sharpe=0.456 MaxDD=-56.5%
- **c01_sma200_gld** (21.4y): SPY CAGR=8.60% net=7.31% Sharpe=0.530 MaxDD=-56.5%
- **c01_sma200_tlt** (23.7y): SPY CAGR=9.23% net=7.85% Sharpe=0.562 MaxDD=-56.5%

## Cross-lib concordance (bt library)

- c01_sma200_cash: ✓ CONCORDANT (ΔCAGR=1.51pp)
- c01_sma200_gld: ✓ CONCORDANT (ΔCAGR=1.36pp)
- c01_sma200_tlt: ✓ CONCORDANT (ΔCAGR=1.76pp)

## Stage 2 — yfinance independent validation

- c01_sma200_cash: ✗ DIVERGENT (ΔCAGR=9.77pp)
- c01_sma200_gld: ✗ DIVERGENT (ΔCAGR=9.94pp)
- c01_sma200_tlt: ✗ DIVERGENT (ΔCAGR=8.91pp)

## Citations

- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR gate

## Notes

- PBO gate is aggregate-level (144 trials across Phase 3.5e). Per-ticker PBO with N=3 is
  unreliable (see Phase 3.5d E1 rejection — grid shrinkage artifact). Real PBO at aggregator.
- Pre-pass = all gates except PBO pass. Confirm at aggregator.
- UPRO synthetic pre-2009 (r = 3×r_SPX_TR - drag - expense).
- DSR n_trials = cumulative trial count from trial_count.json at sweep time.
