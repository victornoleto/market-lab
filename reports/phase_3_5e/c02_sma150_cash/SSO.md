# SSO daily — c02 SMA150+cash Binary Regime (iter 22) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% SSO; else → cash (0%).
**Asset:** SSO (ProShares Ultra S&P500, 2× SPX).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — baseline regime-sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.

**Window:** 2001-05-14 → 2026-04-14 (24.9y, 6265 bars)

## Results

| Metric | Value |
|--------|-------|
| CAGR% (gross) | 7.51% |
| CAGR% (net 15% IR) | 6.39% |
| Sharpe (gross) | 0.445 |
| Sharpe (net) | 0.379 |
| MaxDD | -44.3% |
| Calmar | 0.170 |
| WF positive splits | 8/8 |
| OOS Sharpe | 0.620 |
| FWD Sharpe | -0.708 |
| DSR p-value (n=14) | 0.3169 |

## Gate summary

| Gate | Result |
|------|--------|
| PBO | AGGREGATE_LEVEL (computed at aggregator) |
| DSR p<0.05 | ✗ FAIL (p=0.3169) |
| WF ≥6/8 | ✓ PASS (8/8) |
| OOS Sharpe ≥0.5×IS | ✓ PASS (0.620 vs IS 0.400) |
| FWD Sharpe >0 | ✗ FAIL (-0.708) |
| Beats SPY_net | ✓ PASS (strat=6.39% vs SPY=6.04%) |
| Calmar >0.5 | ✗ FAIL (0.170) |
| Sharpe_net >0.8 | ✗ FAIL (0.379) |
| **Pre-pass (pending PBO)** | ✗ NO — DSR, FWD, CALMAR, SHARPE_NET |

## SPY benchmark (same window)

- SPY CAGR gross: 7.11%
- SPY CAGR net (15% IR): 6.04%
- SPY Sharpe: 0.456
- SPY MaxDD: -56.5%
- Strategy vs SPY correlation: 0.566

## OOS details

- IS window: 2001-05-15 → 2021-04-16 (Sharpe=0.400)
- OOS window: 2021-04-19 → 2026-04-14 (Sharpe=0.620)

## FWD stress details

- FWD window: 2026-01-13 → 2026-04-14 (Sharpe=-0.708)
- FWD note: Jan-Apr 2026 tariff shock period

## WF splits

Sharpe per split: ['0.152', '0.205', '0.191', '0.729', '0.234', '0.658', '0.207', '1.115']
Positive: 8/8

## Citations

- `[leverage_for_the_long_run, p.30]` — SMA150 binary regime (MA period sensitivity)
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.275]` — DSR gate
- `[advances_fin_ml, ch.12]` — walk-forward validation

## Notes

- PBO gate is aggregate-level (144 trials across Phase 3.5e). Not computed per-ticker.
- c02 uses shorter SMA150 vs c01 SMA200 — tests MA period sensitivity.
- Cash off-leg means 0% return in off-regime (no tail hedge).
- DSR n_trials = cumulative trial count from trial_count.json at sweep time.
- SSO synthetic data pre-2006 per reference_prices.parquet; joint window with SPY starts 2001-05-14.

## Cross-lib concordance (bt library)

- ✗ DIVERGENT (ΔCAGR=4.36pp)

## Stage 2 — yfinance independent validation

- ✗ DIVERGENT (ΔCAGR=5.24pp)
