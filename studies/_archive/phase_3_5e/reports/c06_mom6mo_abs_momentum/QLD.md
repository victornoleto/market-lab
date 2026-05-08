# QLD daily — c06 Absolute Momentum 6-month (Antonacci) (iter 42) [SWING BROKER]

**Strategy:** 6-month trailing return of QLD > 0 → 100% QLD; else → off-leg.
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** Absolute momentum on QLD (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 2:** N/A — no QQQSIM in testfol.io; yfinance forbidden per spec §3.1.

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 2001-05-15→2026-04-17 | 12.5% | 0.509 | -53.7% | 0.274 | 7/8 | 0.664 | -1.710 | 0.1938 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 14.6% | 0.547 | -51.7% | 0.332 | 8/8 | 0.598 | -1.549 | 0.2010 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 14.1% | 0.536 | -51.8% | 0.320 | 8/8 | 0.352 | -1.840 | 0.1779 | ✗ |

## Best config: c06_mom6mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 17.15% |
| CAGR net (15% IR) | 14.57% |
| Sharpe gross | 0.643 |
| Sharpe net | 0.547 |
| MaxDD | -51.7% |
| Calmar | 0.332 |
| WF | 8/8 |
| OOS Sharpe | 0.598 (IS=0.654) |
| FWD Sharpe | -1.549 |
| DSR p-value | 0.2010 (n_trials=34) |
| n_bars | 5383 |

### SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.603 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.2010) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.598) |
| Gate 5 — FWD stress | ✗ FAIL (FWD_S=-1.549) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.332) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.547) |
| **Pre-pass (no PBO)** | **✗ DSR, FWD, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.289 | 0.477 | 0.259 | 1.324 | 0.482 | 0.747 | 1.161 | 0.551

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 18.55% |
| ΔCAGR | 1.40pp — ✓ CONCORDANT |

## Citations

- `[dual_momentum, ch.6]` — Antonacci 6-month absolute momentum filter
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.
- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.
- 6-month lookback is shorter than Antonacci canonical 12-month; more sensitive to recent trends.
- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.
- DSR n_trials: cash=33, GLD=34, TLT=35 (cumulative from trial_count.json).
- Window differs per off-leg: constrained by earliest available off-leg data in parquet.
