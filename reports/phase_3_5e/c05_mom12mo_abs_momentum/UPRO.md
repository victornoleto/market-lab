# UPRO daily — c05 Absolute Momentum 12-month (Antonacci) (iter 39) [SWING BROKER]

**Strategy:** 12-month trailing return of UPRO > 0 → 100% UPRO; else → off-leg.
**Asset:** UPRO (ProShares UltraPro S&P 500, 3× SPY).
**Signal:** Absolute momentum on UPRO (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 1:** reference_prices.parquet (UPRO synthetic pre-2009: 3× SPY daily - drag - expense `[leverage_for_the_long_run, ch.2]`). Synthetic range: 1986-01-02.

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 1986-01-02→2026-04-17 | 10.2% | 0.419 | -84.8% | 0.142 | 8/8 | 0.278 | 0.575 | 0.1518 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 13.7% | 0.485 | -83.1% | 0.194 | 7/8 | 0.480 | 0.147 | 0.2939 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 11.0% | 0.430 | -84.6% | 0.153 | 7/8 | 0.500 | 0.147 | 0.3600 | ✗ |

## Best config: c05_mom12mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 16.16% |
| CAGR net (15% IR) | 13.74% |
| Sharpe gross | 0.570 |
| Sharpe net | 0.485 |
| MaxDD | -83.1% |
| Calmar | 0.194 |
| WF | 7/8 |
| OOS Sharpe | 0.480 (IS=0.594) |
| FWD Sharpe | 0.147 |
| DSR p-value | 0.2939 (n_trials=31) |
| n_bars | 5383 |

### SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.698 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.2939) |
| Gate 3 — WF ≥6/8 | ✓ PASS (7/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.480) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.147) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.194) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.485) |
| **Pre-pass (no PBO)** | **✗ DSR, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.950 | 0.559 | 0.191 | 1.487 | 0.951 | -0.111 | 0.595 | 0.800

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Stage 2 concordance (Tiingo real UPRO vs Stage 1 synthetic)

| Metric | Value |
|--------|-------|
| Stage 1 CAGR (full window) | 16.16% |
| Stage 1 CAGR (overlap 2009+) | 19.30% |
| Stage 2 CAGR (Tiingo UPRO real) | 19.30% |
| ΔCAGR (Stage2 vs Stage1 overlap) | 0.00pp — ✓ CONCORDANT |
| Stage 2 window | 2009-06-25 → 2026-04-15 (4226 bars) |

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 13.95% |
| ΔCAGR | 2.21pp — ✓ CONCORDANT |

## Citations

- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter
- `[leverage_for_the_long_run, ch.2]` — UPRO synthetic pre-2009: 3× SPY returns - drag - expense
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=3 local PBO meaningless.
- Monthly signal with daily-granular portfolio: forward-fill ensures only month-end rebalances.
- Cash off-leg = 0% yield (conservative). GLD/TLT provide flight-to-safety alternatives.
- DSR n_trials: cash=30, GLD=31, TLT=32 (cumulative from trial_count.json).
- UPRO synthetic range 1986-01-02 → 2026-04-17 in reference_prices.parquet (3× SPY - drag).
- Stage 2 uses Tiingo real UPRO from 2009-06-25; Stage 1 window extends to 1986 via synthetic.
- UPRO (3× SPY) vs TQQQ (3× QQQ): SPY index used vs QQQ; different beta, lower CAGR expected.
