# SSO daily — c06 Absolute Momentum 6-month (Antonacci) (iter 43) [SWING BROKER]

**Strategy:** 6-month trailing return of SSO > 0 → 100% SSO; else → off-leg.
**Asset:** SSO (ProShares Ultra S&P500, 2× SPY).
**Signal:** Absolute momentum on SSO (self) `[dual_momentum, ch.6]`.
**Off-legs tested:** cash (0%), GLD, TLT.
**Tax:** 15% IR BR flat on CAGR.
**Stage 2:** N/A — SSOSIM in testfol.io flagged as artifact source; yfinance forbidden per spec §3.1.
**Note:** SSO synthetic pre-2006-06-21 via r=2×r_SPX_TR-drag (mandate §4). Longest window used.

## Summary across 3 off-legs

| Off-leg | Window | CAGR net | Sharpe net | MaxDD | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass |
|---------|--------|----------|------------|-------|--------|----|-------|-------|-------|----------|
| cash | 1986-01-02→2026-04-17 | 7.0% | 0.371 | -68.1% | 0.120 | 7/8 | 0.119 | -1.828 | 0.2713 | ✗ |
| GLD | 2004-11-18→2026-04-15 | 10.7% | 0.474 | -66.3% | 0.189 | 7/8 | 0.324 | -1.480 | 0.3390 | ✗ ← BEST |
| TLT | 2002-07-26→2026-04-15 | 9.6% | 0.449 | -66.9% | 0.168 | 7/8 | 0.230 | -1.858 | 0.3462 | ✗ |

## Best config: c06_mom6mo_gld (off-leg: GLD)

**Window:** 2004-11-18 → 2026-04-15 (21.4y)

### Results

| Metric | Value |
|--------|-------|
| CAGR gross | 12.54% |
| CAGR net (15% IR) | 10.66% |
| Sharpe gross | 0.558 |
| Sharpe net | 0.474 |
| MaxDD | -66.3% |
| Calmar | 0.189 |
| WF | 7/8 |
| OOS Sharpe | 0.324 (IS=0.610) |
| FWD Sharpe | -1.480 |
| DSR p-value | 0.3390 (n_trials=37) |
| n_bars | 5383 |

### SPY benchmark (same window — available from 2001-05-14 onward)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 8.64% |
| SPY CAGR net | 7.35% |
| SPY Sharpe | 0.532 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.648 |

### Gate summary (best config)

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.3390) |
| Gate 3 — WF ≥6/8 | ✓ PASS (7/8) |
| Gate 4 — OOS holdout | ✓ PASS (OOS_S=0.324) |
| Gate 5 — FWD stress | ✗ FAIL (FWD_S=-1.480) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.189) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.474) |
| **Pre-pass (no PBO)** | **✗ DSR, FWD, CALMAR, SHARPE_NET** |

### WF split Sharpes

0.546 | 0.841 | 0.133 | 1.492 | 0.910 | -0.058 | 0.773 | 0.545

OOS window: 2021-12-29 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt) — best config

| Metric | Value |
|--------|-------|
| bt CAGR | 11.02% |
| ΔCAGR | 1.52pp — ✓ CONCORDANT |

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
- SSO synthetic pre-2006 from r=2×r_SPX_TR-drag (mandate §4). Cash window extended to 1986.
- SPY benchmark for cash window computed over 2001-05-14→2026-04-17 overlap (SPY NaN before).
- DSR n_trials: cash=36, GLD=37, TLT=38 (cumulative from trial_count.json).
- Window differs per off-leg: constrained by earliest available off-leg data in parquet.
