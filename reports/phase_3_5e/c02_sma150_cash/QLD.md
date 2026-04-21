# QLD daily — c02 SMA150+cash Binary Regime (iter 21) [SWING BROKER]

**Strategy:** SPY > SMA150 (prev day) → 100% QLD; else → cash (0%).
**Asset:** QLD (ProShares Ultra QQQ, 2× QQQ).
**Signal:** SPY SMA150 regime `[leverage_for_the_long_run, p.30]`.
**Off-leg:** cash (0%) — baseline regime-sensitivity test vs c01 SMA200.
**Tax:** 15% IR BR flat on CAGR.

**Window:** 2001-05-15 → 2026-04-14 (24.9y, 6264 bars)

## Results

| Metric | Value |
|--------|-------|
| CAGR% (gross) | 12.12% |
| CAGR% (net 15% IR) | 10.30% |
| Sharpe (gross) | 0.549 |
| Sharpe (net) | 0.467 |
| MaxDD | -49.4% |
| Calmar | 0.245 |
| WF positive splits | 8/8 |
| OOS Sharpe | 0.597 |
| FWD Sharpe | -0.395 |
| DSR p-value (n=13) | 0.1533 |

## Gate summary

| Gate | Result |
|------|--------|
| PBO | AGGREGATE_LEVEL (computed at aggregator) |
| DSR p<0.05 | ✗ FAIL (p=0.1533) |
| WF ≥6/8 | ✓ PASS (8/8) |
| OOS Sharpe ≥0.5×IS | ✓ PASS (0.597 vs IS 0.536) |
| FWD Sharpe >0 | ✗ FAIL (-0.395) |
| Beats SPY_net | ✓ PASS (strat=10.30% vs SPY=6.03%) |
| Calmar >0.5 | ✗ FAIL (0.245) |
| Sharpe_net >0.8 | ✗ FAIL (0.467) |
| **Pre-pass (pending PBO)** | ✗ NO — DSR, FWD, CALMAR, SHARPE_NET |

## SPY benchmark (same window)

- SPY CAGR gross: 7.09%
- SPY CAGR net (15% IR): 6.03%
- SPY Sharpe: 0.455
- SPY MaxDD: -56.5%
- Strategy vs SPY correlation: 0.505

## OOS details

- IS window: 2001-05-16 → 2021-04-16 (Sharpe=0.536)
- OOS window: 2021-04-19 → 2026-04-14 (Sharpe=0.597)

## FWD stress details

- FWD window: 2026-01-13 → 2026-04-14 (Sharpe=-0.395)
- FWD note: Jan-Apr 2026 tariff shock period

## WF splits

Sharpe per split: ['0.069', '0.043', '0.610', '0.903', '0.560', '0.879', '0.313', '1.107']
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

## Cross-lib concordance (bt library)

- ✗ DIVERGENT (ΔCAGR=3.04pp)

## Stage 2 — yfinance independent validation

- ✗ DIVERGENT (ΔCAGR=8.21pp)
