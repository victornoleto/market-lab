# UPRO daily — c02 SMA150+Cash Binary Regime (iter 27) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% UPRO; else → cash (0%).
**Asset:** UPRO (ProShares UltraPro S&P 500, 3× SPX).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — shorter MA sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.
**Window:** 2001-05-15 → 2026-04-17 (24.9y)
**Note:** UPRO pre-2009-06-25 is synthetic in reference_prices.parquet.

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 8.90% |
| CAGR net (15% IR) | 7.57% |
| Sharpe gross | 0.428 |
| Sharpe net | 0.364 |
| MaxDD | -61.6% |
| Calmar | 0.145 |
| WF | 8/8 |
| OOS Sharpe | 0.639 (IS=0.373) |
| FWD Sharpe | 0.221 |
| DSR p-value | 0.3706 (n_trials=16) |
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
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.3706) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.639) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.221) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.145) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.364) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.146 | 0.068 | 0.203 | 0.723 | 0.242 | 0.641 | 0.186 | 1.097

OOS window: 2021-04-21 → 2026-04-17
FWD window: 2026-01-16 → 2026-04-17

## Stage-2 concordance (testfol.io UPROSIM)

| Metric | Value |
|--------|-------|
| S1 CAGR (parquet) | 8.90% |
| S2 CAGR (UPROSIM) | 9.02% |
| ΔCAGR | 0.12pp — ✓ CONCORDANT (≤3pp) |

## Cross-lib concordance (bt)

| Metric | Value |
|--------|-------|
| bt CAGR | 15.60% |
| ΔCAGR | 6.70pp — ✗ DIVERGENT |

## Citations

- `[leverage_for_the_long_run, p.30]` — SMA150 regime test (shorter MA sensitivity)
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c02 tests only the cash off-leg for SMA150. c03 tests EMA100+TLT as a separate lead.
- Stage-2 uses testfol.io UPROSIM (3× SPX simulation) as independent price source.
- DSR n_trials = 16 (cumulative from trial_count.json).
- UPRO pre-2009-06-25 data in Stage-1 is synthetic (leveraged SPX TR formula, see reference_prices.py).
- bt divergence (if any) likely from synthetic pre-inception data handling differences.
- This is the LAST ticker of c02 sweep; registry will advance to 'aggregating' after this iter.
