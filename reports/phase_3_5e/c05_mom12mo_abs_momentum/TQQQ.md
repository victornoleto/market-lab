# TQQQ daily — c05 Absolute Momentum 12-month (Antonacci) (iter 38) [SWING BROKER]

**Strategy:** 12-month trailing return of TQQQ > 0 → 100% TQQQ; else → off-leg.
**Asset:** TQQQ (ProShares UltraPro QQQ, 3× QQQ).
**Signal:** Absolute momentum on TQQQ (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (TQQQ synthetic pre-2010: 3× QQQ daily - drag - expense `[leverage_for_the_long_run, ch.2]`).

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 2001-05-15→2026-04-17 | 13.6% | 0.470 | -81.3% | 0.197 | 8/8 | 0.579 | 0.807 | 0.2356 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 17.4% | 0.532 | -79.3% | 0.259 | 8/8 | 0.447 | 0.305 | 0.2016 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 14.6% | 0.485 | -81.0% | 0.211 | 8/8 | 0.434 | 0.305 | 0.2393 | ✗ |

## Best config: c05_mom12mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 20.50% |
| CAGR net (15% IR) | 17.42% |
| Sharpe gross | 0.625 |
| Sharpe net | 0.532 |
| MaxDD | -79.3% |
| Calmar | 0.259 |
| WF | 8/8 |
| OOS Sharpe | 0.447 (IS=0.673) |
| FWD Sharpe | 0.305 |
| DSR p-value | 0.2016 (n_trials=28) |
| n_bars | 5383 |

### SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.672 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.2016) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.447) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.305) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.259) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.532) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.200 | 0.232 | 0.655 | 1.668 | 0.715 | 0.371 | 0.415 | 0.837

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Stage 2 concordance (Tiingo real TQQQ vs Stage 1 synthetic)

| Metric | Value |
|--------|-------|
| Stage 1 CAGR (full window) | 20.50% |
| Stage 1 CAGR (overlap 2010+) | 25.88% |
| Stage 2 CAGR (Tiingo TQQQ real) | 25.88% |
| ΔCAGR (Stage2 vs Stage1 overlap) | 0.00pp — ✓ CONCORDANT |
| Stage 2 window | 2010-02-11 → 2026-04-15 (4067 bars) |

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 20.34% |
| ΔCAGR | 0.16pp — ✓ CONCORDANT |

## Citations

- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter
- `[leverage_for_the_long_run, ch.2]` — TQQQ synthetic pre-2010: 3× QQQ returns - drag - expense
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.
- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.
- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.
- DSR n_trials: cash=27, GLD=28, TLT=29 (cumulative from trial_count.json).
- TQQQ seam gap: 2010-02-09/10 missing in Tiingo real; synthetic parquet clean from 2001-05-15.
- Stage 2 uses Tiingo real TQQQ from 2010-02-11; Stage 1 window extends to 2001-05-15 via synthetic.
