# SSO daily — c01 SMA200 Binary Regime (iter 16) [SWING BROKER]

**Strategy:** SPY > SMA200 (prev day) → 100% SSO; else → off-leg.
**Asset:** SSO (ProShares Ultra S&P 500, 2× SPX).
**Signal:** SPY SMA200 regime `[leverage_for_the_long_run, ch.2]`.
**Off-legs:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Note:** SSO pre-2006 data is synthetic via r = L × r_SPX_TR - drag - expense.

**Per-ticker local PBO (informational, N=3 unreliable):** 0.183
  Note: N=3 — INFORMATIONAL ONLY (N<4, real PBO at aggregator). PBO=0.183

## Results table

| Config | Window | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | Pre-pass |
|--------|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-------|----------|---------|--------|----------|
| c01_sma200_cash | 24.9y | 10.75 | 9.14 | 0.582 | 0.495 | -39.0 | 0.276 | 7/8 | 0.62 | -1.01 | 0.0343 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_gld | 21.4y | 13.83 | 11.76 | 0.647 | 0.550 | -42.4 | 0.326 | 8/8 | 0.59 | -0.49 | 0.0380 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_tlt | 23.7y | 10.61 | 9.02 | 0.543 | 0.462 | -54.0 | 0.196 | 8/8 | 0.28 | -1.08 | 0.0920 | ✓ | ✗ | ✗ | ✗ |

## SPY benchmark (per-config, same window)

- **c01_sma200_cash** (24.9y): SPY CAGR=7.11% net=6.04% Sharpe=0.456 MaxDD=-56.5%
- **c01_sma200_gld** (21.4y): SPY CAGR=8.60% net=7.31% Sharpe=0.530 MaxDD=-56.5%
- **c01_sma200_tlt** (23.7y): SPY CAGR=9.23% net=7.85% Sharpe=0.562 MaxDD=-56.5%

## Cross-lib concordance (bt library)

- c01_sma200_cash: ✓ CONCORDANT (ΔCAGR=0.92pp)
- c01_sma200_gld: ✓ CONCORDANT (ΔCAGR=0.89pp)
- c01_sma200_tlt: ✓ CONCORDANT (ΔCAGR=1.18pp)

## Stage 2 — yfinance independent validation

- c01_sma200_cash: ✗ DIVERGENT (ΔCAGR=3.05pp)
- c01_sma200_gld: ✓ CONCORDANT (ΔCAGR=2.85pp)
- c01_sma200_tlt: ✗ DIVERGENT (ΔCAGR=3.00pp)

## Citations

- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR gate

## Notes

- PBO gate is aggregate-level (144 trials across Phase 3.5e). Per-ticker PBO with N=3 is
  unreliable (see Phase 3.5d E1 rejection — grid shrinkage artifact). Real PBO at aggregator.
- Pre-pass = all gates except PBO pass. Confirm at aggregator.
- SSO pre-2006 synthetic data per mandate §4: r = L × r_SPX_TR - drag - expense.
- DSR n_trials = cumulative trial count from trial_count.json at sweep time.
