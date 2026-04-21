# SSO daily — c02 SMA150+Cash Binary Regime (iter 25) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% SSO; else → cash (0%).
**Asset:** SSO (ProShares Ultra S&P 500, 2× SPY).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — shorter MA sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.
**Window:** 2001-05-15 → 2026-04-17 (24.9y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 7.78% |
| CAGR net (15% IR) | 6.61% |
| Sharpe gross | 0.457 |
| Sharpe net | 0.388 |
| MaxDD | -44.3% |
| Calmar | 0.176 |
| WF | 8/8 |
| OOS Sharpe | 0.681 (IS=0.398) |
| FWD Sharpe | 0.261 |
| DSR p-value | 0.2971 (n_trials=14) |
| n_bars | 6267 |

## SPY benchmark (same window)

| SPY CAGR gross | 7.19% |
| SPY CAGR net | 6.11% |
| SPY Sharpe | 0.460 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.566 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.2971) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.681) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.261) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.176) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.388) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.170 | 0.083 | 0.277 | 0.753 | 0.242 | 0.659 | 0.190 | 1.159

OOS window: 2021-04-21 → 2026-04-17
FWD window: 2026-01-16 → 2026-04-17

## Stage-2 concordance (testfol.io SSOSIM)

| S1 CAGR (parquet) | 7.78% |
| S2 CAGR (SSOSIM) | 7.95% |
| ΔCAGR | 0.17pp — ✓ CONCORDANT (≤3pp) |

## Cross-lib concordance (bt)

| bt CAGR | 12.08% |
| ΔCAGR | 4.30pp — ✗ DIVERGENT |

## Citations

- `[leverage_for_the_long_run, p.30]` — SMA150 regime test (shorter MA sensitivity)
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c02 tests only the cash off-leg for SMA150. c03 tests EMA100+TLT as a separate lead.
- Stage-2 uses testfol.io SSOSIM (SPY 2× simulation) as independent price source.
- DSR n_trials = 14 (cumulative from trial_count.json).
- SSO pre-2006 data in Stage-1 is synthetic (leveraged SPX TR formula, see reference_prices.py).
