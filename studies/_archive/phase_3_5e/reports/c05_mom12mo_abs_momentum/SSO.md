# SSO daily — c05 Absolute Momentum 12-month (Antonacci) (iter 37) [SWING BROKER]

**Strategy:** 12-month trailing return of SSO > 0 → 100% SSO; else → off-leg.
**Asset:** SSO (ProShares Ultra S&P 500, 2× SPY).
**Signal:** Absolute momentum on SSO (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (SSO synthetic pre-2006: 2× SPX daily - drag - expense `[leverage_for_the_long_run, ch.2]`).

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 2001-05-14→2026-04-17 | 9.6% | 0.456 | -59.3% | 0.190 | 7/8 | 0.679 | 0.622 | 0.2461 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 13.2% | 0.543 | -59.3% | 0.262 | 8/8 | 0.521 | 0.196 | 0.1729 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 10.2% | 0.460 | -59.3% | 0.201 | 8/8 | 0.493 | 0.196 | 0.2708 | ✗ |

## Best config: c05_mom12mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 15.57% |
| CAGR net (15% IR) | 13.24% |
| Sharpe gross | 0.639 |
| Sharpe net | 0.543 |
| MaxDD | -59.3% |
| Calmar | 0.262 |
| WF | 8/8 |
| OOS Sharpe | 0.521 (IS=0.668) |
| FWD Sharpe | 0.196 |
| DSR p-value | 0.1729 (n_trials=25) |
| n_bars | 5383 |

### SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.693 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1729) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.521) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.196) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.262) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.543) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.942 | 0.316 | 0.310 | 1.492 | 0.913 | 0.317 | 0.600 | 0.852

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Stage 2 concordance (Tiingo real SSO vs Stage 1)

| Metric | Value |
|--------|-------|
| Stage 1 CAGR (full window) | 15.57% |
| Stage 1 CAGR (overlap 2006+) | 15.69% |
| Stage 2 CAGR (Tiingo SSO real) | 15.69% |
| ΔCAGR (Stage2 vs Stage1 overlap) | 0.00pp — ✓ CONCORDANT |
| Stage 2 window | 2006-06-21 → 2026-04-15 (4984 bars) |

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 13.67% |
| ΔCAGR | 1.91pp — ✓ CONCORDANT |

## Citations

- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter
- `[leverage_for_the_long_run, ch.2]` — SSO synthetic pre-2006: 2× SPX returns - drag - expense
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.
- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.
- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.
- DSR n_trials: cash=24, GLD=25, TLT=26 (cumulative from trial_count.json).
- Window constrained by SPY start (2001-05-14) for cash; off-leg first date for GLD/TLT.
- SSO pre-2006 uses synthetic data (2× SPX total return - drag). Stage 2 validates vs Tiingo real.
