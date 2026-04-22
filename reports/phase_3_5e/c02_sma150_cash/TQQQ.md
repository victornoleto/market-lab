# TQQQ daily — c02 SMA150+Cash Binary Regime (iter 26) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% TQQQ; else → cash (0%).
**Asset:** TQQQ (ProShares UltraPro QQQ, 3× QQQ).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — shorter MA sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.
**Window:** 2001-05-15 → 2026-04-17 (24.9y)
**Note:** TQQQ pre-2010-02-11 is synthetic in reference_prices.parquet.

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 14.56% |
| CAGR net (15% IR) | 12.37% |
| Sharpe gross | 0.536 |
| Sharpe net | 0.456 |
| MaxDD | -65.5% |
| Calmar | 0.222 |
| WF | 8/8 |
| OOS Sharpe | 0.635 (IS=0.510) |
| FWD Sharpe | 0.671 |
| DSR p-value | 0.1854 (n_trials=15) |
| n_bars | 6267 |

## SPY benchmark (same window)

| SPY CAGR gross | 7.19% |
| SPY CAGR net | 6.11% |
| SPY Sharpe | 0.460 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.504 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1854) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.635) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.671) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.222) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.456) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.056 | 0.026 | 0.487 | 0.895 | 0.565 | 0.879 | 0.321 | 1.062

OOS window: 2021-04-21 → 2026-04-17
FWD window: 2026-01-16 → 2026-04-17

## Stage-2 concordance (testfol.io TQQQSIM)

| S1 CAGR (parquet) | 14.56% |
| S2 CAGR (TQQQSIM) | 14.60% |
| ΔCAGR | 0.05pp — ✓ CONCORDANT (≤3pp) |

## Cross-lib concordance (bt)

| bt CAGR | 19.30% |
| ΔCAGR | 4.74pp — ✗ DIVERGENT |

## Citations

- `[leverage_for_the_long_run, p.30]` — SMA150 regime test (shorter MA sensitivity)
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c02 tests only the cash off-leg for SMA150. c03 tests EMA100+TLT as a separate lead.
- Stage-2 uses testfol.io TQQQSIM (QQQSIM?L=3) as independent price source.
- DSR n_trials = 15 (cumulative from trial_count.json).
- TQQQ pre-2010-02-11 data in Stage-1 is synthetic (leveraged QQQ TR formula, see reference_prices.py).
- bt divergence (if any) likely from synthetic pre-inception data handling differences.
