# QLD daily — c01 SMA200 Binary Regime (iter 15) [SWING BROKER]

**Strategy:** SPY > SMA200 (prev day) → 100% QLD; else → off-leg.
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** SPY SMA200 regime `[leverage_for_the_long_run, ch.2]`.
**Off-legs:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.

**Per-ticker local PBO (informational, N=3 unreliable):** 0.032
  Note: N=3 — INFORMATIONAL ONLY (N<4, real PBO at aggregator). PBO=0.032

## Results table

| Config | Window | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | Pre-pass |
|--------|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-------|----------|---------|--------|----------|
| c01_sma200_cash | 24.9y | 15.43 | 13.11 | 0.653 | 0.555 | -46.6 | 0.331 | 7/8 | 0.54 | -0.59 | 0.0034 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_gld | 21.4y | 20.64 | 17.55 | 0.776 | 0.660 | -51.6 | 0.400 | 8/8 | 0.51 | -0.25 | 0.0012 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_tlt | 23.7y | 15.97 | 13.57 | 0.646 | 0.549 | -61.6 | 0.259 | 8/8 | 0.29 | -0.66 | 0.0116 | ✓ | ✗ | ✗ | ✗ |

## SPY benchmark (per-config, same window)

- **c01_sma200_cash** (24.9y): SPY CAGR=7.09% net=6.03% Sharpe=0.455 MaxDD=-56.5%
- **c01_sma200_gld** (21.4y): SPY CAGR=8.60% net=7.31% Sharpe=0.530 MaxDD=-56.5%
- **c01_sma200_tlt** (23.7y): SPY CAGR=9.23% net=7.85% Sharpe=0.562 MaxDD=-56.5%

## Cross-lib concordance (bt library)

- c01_sma200_cash: ✓ CONCORDANT (ΔCAGR=1.31pp)
- c01_sma200_gld: ✓ CONCORDANT (ΔCAGR=0.10pp)
- c01_sma200_tlt: ✓ CONCORDANT (ΔCAGR=1.15pp)

## Stage 2 — yfinance independent validation

- c01_sma200_cash: ✗ DIVERGENT (ΔCAGR=7.37pp)
- c01_sma200_gld: ✗ DIVERGENT (ΔCAGR=5.26pp)
- c01_sma200_tlt: ✗ DIVERGENT (ΔCAGR=6.62pp)

## Citations

- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR gate

## Notes

- PBO gate is aggregate-level (144 trials across Phase 3.5e). Per-ticker PBO with N=3 is
  unreliable (see Phase 3.5d E1 rejection — grid shrinkage artifact). Real PBO at aggregator.
- Pre-pass = all gates except PBO pass. Confirm at aggregator.
- DSR n_trials = cumulative trial count from trial_count.json at sweep time.
