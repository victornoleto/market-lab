# QLD daily — c05 Absolute Momentum 12-month (Antonacci) (iter 36) [SWING BROKER]

**Strategy:** 12-month trailing return of QLD > 0 → 100% QLD; else → off-leg.
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** Absolute momentum on QLD (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 2:** N/A — no QQQSIM in testfol.io; yfinance forbidden per spec §3.1.

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 2001-05-15→2026-04-17 | 12.3% | 0.489 | -55.9% | 0.259 | 7/8 | 0.585 | 0.852 | 0.1735 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 15.9% | 0.560 | -52.4% | 0.356 | 8/8 | 0.457 | 0.347 | 0.1370 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 12.6% | 0.488 | -56.7% | 0.262 | 7/8 | 0.434 | 0.347 | 0.2042 | ✗ |

## Best config: c05_mom12mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 18.66% |
| CAGR net (15% IR) | 15.86% |
| Sharpe gross | 0.659 |
| Sharpe net | 0.560 |
| MaxDD | -52.4% |
| Calmar | 0.356 |
| WF | 8/8 |
| OOS Sharpe | 0.457 (IS=0.717) |
| FWD Sharpe | 0.347 |
| DSR p-value | 0.1370 (n_trials=22) |
| n_bars | 5383 |

### SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.682 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1370) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.457) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.347) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.356) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.560) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.047 | 0.364 | 0.651 | 1.664 | 0.755 | 0.584 | 0.437 | 0.778

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 18.52% |
| ΔCAGR | 0.14pp — ✓ CONCORDANT |

## Citations

- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.
- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.
- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.
- DSR n_trials: cash=21, GLD=22, TLT=23 (cumulative from trial_count.json).
- Window differs per off-leg: constrained by earliest available off-leg data in parquet.
