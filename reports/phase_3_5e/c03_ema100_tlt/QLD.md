# QLD daily — c03 EMA100+TLT Binary Regime (iter 30) [SWING BROKER]

**Strategy:** SPY > EMA100 (prev day) → 100% QLD; else → 100% TLT.
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** SPY EMA100 regime `[leverage_for_the_long_run, p.31]` — Gayed TLT variant.
**Off-leg:** TLT (iShares 20+ Year Treasury Bond ETF).
**Tax:** 15% IR BR flat on CAGR.
**Stage 2:** N/A — no QQQSIM from testfol.io; yfinance forbidden per spec §3.1.
**Window:** 2002-07-26 → 2026-04-15 (23.7y)

## Results

| Metric | Value |
|--------|-------|
| CAGR gross | 14.15% |
| CAGR net (15% IR) | 12.02% |
| Sharpe gross | 0.583 |
| Sharpe net | 0.496 |
| MaxDD | -64.8% |
| Calmar | 0.218 |
| WF | 8/8 |
| OOS Sharpe | 0.175 (IS=0.693) |
| FWD Sharpe | 0.064 |
| DSR p-value | 0.1579 (n_trials=17) |
| n_bars | 5967 |

## SPY benchmark (same window)

| Metric | Value |
|--------|-------|
| SPY CAGR gross | 9.27% |
| SPY CAGR net | 7.88% |
| SPY Sharpe | 0.564 |
| SPY MaxDD | -56.5% |
| Correlation vs SPY | 0.417 |

## Gate summary

| Gate | Result |
|------|--------|
| Gate 1 — PBO | AGGREGATE_LEVEL (real PBO at 144-trial aggregator) |
| Gate 2 — DSR p<0.05 | ✗ FAIL (p=0.1579) |
| Gate 3 — WF ≥6/8 | ✓ PASS (8/8) |
| Gate 4 — OOS holdout | ✗ FAIL (OOS_S=0.175) |
| Gate 5 — FWD stress | ✓ PASS (FWD_S=0.064) |
| Eco 1 — beats SPY net | ✓ PASS |
| Eco 2 — Calmar>0.5 | ✗ FAIL (Cal=0.218) |
| Eco 3 — Sharpe_net>0.8 | ✗ FAIL (SN=0.496) |
| **Pre-pass (no PBO)** | **✗ DSR, OOS, CALMAR, SHARPE_NET** |

## WF split Sharpes

0.193 | 0.161 | 0.945 | 1.008 | 0.898 | 0.628 | 0.160 | 0.947

OOS window: 2021-07-14 → 2026-04-15
FWD window: 2026-01-14 → 2026-04-15

## Cross-lib concordance (bt)

| Metric | Value |
|--------|-------|
| bt CAGR | 14.33% |
| ΔCAGR | 0.19pp — ✓ CONCORDANT |

## Citations

- `[leverage_for_the_long_run, p.31]` — EMA100+TLT Gayed variant
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials Phase 3.5e). Per-ticker N=1 is trivially meaningless.
- c03 tests EMA100+TLT. TLT off-leg is the 'flight-to-safety' variant — [leverage_for_the_long_run, p.31].
- Stage-2 is N/A for QLD (QQQ-based 2×; no QQQSIM in testfol.io; yfinance forbidden by spec §3.1).
- DSR n_trials = 17 (cumulative from trial_count.json).
- Window constrained by TLT first date (2002-07-26) and TLT last date (2026-04-15).
