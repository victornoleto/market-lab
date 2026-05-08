# QLD daily — c02 SMA150+Cash Binary Regime (iter 24) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% QLD; else → cash (0%).
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — shorter MA sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.
**Stage 2:** N/A — no QQQSIM from testfol.io; yfinance forbidden per spec §3.1.
**Window:** 2001-05-15 → 2026-04-17 (24.9y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 12.45% |
| CAGR net (15% IR) | 10.58% |
| Sharpe gross | 0.559 |
| Sharpe net | 0.475 |
| MaxDD | -49.4% |
| Calmar | 0.252 |
| WF | 8/8 |
| OOS Sharpe | 0.659 (IS=0.532) |
| FWD Sharpe | 0.713 |
| DSR p-value | 0.1414 (n_trials=13) |
| n_bars | 6267 |

## SPY benchmark (same window)

| SPY CAGR gross | 7.19% |
| SPY CAGR net | 6.11% |
| SPY Sharpe | 0.460 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.505 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1414) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.659) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.713) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.252) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.475) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.069 | 0.043 | 0.609 | 0.915 | 0.561 | 0.879 | 0.313 | 1.107

OOS window: 2021-04-21 → 2026-04-17
FWD window: 2026-01-16 → 2026-04-17

## Cross-lib concordance (bt)

| bt CAGR | 15.46% |
| ΔCAGR | 3.01pp — ✗ DIVERGENT |

## Citations

- `[leverage_for_the_long_run, p.30]` — SMA150 regime test (shorter MA sensitivity)
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c02 tests only the cash off-leg for SMA150. c03 tests EMA100+TLT as a separate lead.
- Stage-2 is N/A for QLD (QQQ 2× — no QQQSIM in testfol.io; yfinance forbidden by spec §3.1).
- DSR n_trials = 13 (cumulative from trial_count.json).
