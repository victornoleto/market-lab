# TQQQ daily — c01 SMA200 Binary Regime (iter 17) [SWING BROKER]

**Strategy:** SPY > SMA200 (prev day) → 100% TQQQ; else → off-leg.
**Asset:** TQQQ (ProShares UltraPro QQQ, 3× QQQ). Synthetic pre-2010.
**Signal:** SPY SMA200 regime `[leverage_for_the_long_run, ch.2]`.
**Off-legs:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.

**Per-ticker local PBO (informational, N=3 unreliable):** 0.008
  Note: N=3 — INFORMATIONAL ONLY (N<4, real PBO at aggregator). PBO=0.008

## Results table

| Config | Window | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | Pre-pass |
|--------|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-------|----------|---------|--------|----------|
| c01_sma200_cash | 24.9y | 19.35 | 16.45 | 0.634 | 0.539 | -63.2 | 0.306 | 7/8 | 0.52 | -0.63 | 0.0397 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_gld | 21.4y | 26.06 | 22.15 | 0.755 | 0.642 | -63.7 | 0.409 | 8/8 | 0.44 | -0.40 | 0.0225 | ✓ | ✗ | ✗ | ✗ |
| c01_sma200_tlt | 23.7y | 20.35 | 17.30 | 0.646 | 0.549 | -71.8 | 0.284 | 8/8 | 0.33 | -0.67 | 0.0544 | ✓ | ✗ | ✗ | ✗ |

## SPY benchmark (per-config, same window)

- **c01_sma200_cash** (24.9y): SPY CAGR=7.09% net=6.03% Sharpe=0.455 MaxDD=-56.5%
- **c01_sma200_gld** (21.4y): SPY CAGR=8.60% net=7.31% Sharpe=0.530 MaxDD=-56.5%
- **c01_sma200_tlt** (23.7y): SPY CAGR=9.23% net=7.85% Sharpe=0.562 MaxDD=-56.5%

## Cross-lib concordance (bt library)

- c01_sma200_cash: ✓ CONCORDANT (ΔCAGR=1.79pp)
- c01_sma200_gld: ✓ CONCORDANT (ΔCAGR=0.30pp)
- c01_sma200_tlt: ✓ CONCORDANT (ΔCAGR=1.35pp)

## Stage 2 — yfinance independent validation

- c01_sma200_cash: ✗ DIVERGENT (ΔCAGR=14.58pp)
- c01_sma200_gld: ✗ DIVERGENT (ΔCAGR=11.82pp)
- c01_sma200_tlt: ✗ DIVERGENT (ΔCAGR=12.57pp)

## Citations

- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR gate

## Notes

- PBO gate is aggregate-level (144 trials across Phase 3.5e). Per-ticker PBO with N=3 is
  unreliable (see Phase 3.5d E1 rejection — grid shrinkage artifact). Real PBO at aggregator.
- Pre-pass = all gates except PBO pass. Confirm at aggregator.
- TQQQ synthetic pre-2010 (r = 3×r_NDX_TR - drag - expense). Seam gap 2010-02-09/10 (not NaN).
- DSR n_trials = cumulative trial count from trial_count.json at sweep time.
