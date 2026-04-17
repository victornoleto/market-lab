# Rebalance modes — 3-leg EW (LETF+QQQ+GLD)

**Path tag:** [SWING BROKER]  
**Window:** 2004-11-18 → 2026-04-14 (21.36 yrs, 5383 bars ≈).  
**Target weights:** EW (1/3, 1/3, 1/3).  
**Initial capital:** $100,000.  
**Monthly deposit (cashflow mode):** $500 (0.50% of initial).  
**BR IR rate (realized gains on sells):** 15%.

## Comparative metrics

| Metric | Daily (winner) | Monthly sell | Monthly cashflow |
|---|---|---|---|
| Equity final | $12,940,149 | $9,569,237 | $142,231,703 |
| CAGR | 25.56% | 23.79% | 40.47% |
| Sharpe | 2.108 | 1.964 | 1.944 |
| Volatility (ann.) | 11.10% | 11.19% | 18.36% |
| MaxDD | 10.86% | 10.94% | 17.78% |
| Max drift (any leg) | 0.00% | 4.81% | 65.05% |
| Mean per-bar max drift | 0.00% | 0.82% | 40.10% |
| Taxable events / yr | 0.0 | 17.9 | 0.0 |
| IR paid / yr (rebal) | $0 | $30,740 | $0 |
| Total IR paid | $0 | $656,642 | $0 |
| Total deposits | $0 | $0 | $129,000 |

## Interpretation notes

* **Daily rebal tax = 0 by construction.** The module reuses the
  `portfolio_combiner` convention of every bar being a forced
  rebalance with no realized-gain accounting. Per-leg trade-level
  tax (the 15% BR IR on each profitable strategy exit) is already
  baked elsewhere in the Phase 3.5b winner reports; this comparison
  isolates the *rebalance-mechanic* tax incidence.
* **Monthly-sell tax is rebalance-level only.** It only fires on
  the end-of-month reset and pays 15% on the overweight legs' sold
  realized gain (cost basis = proportional average, not FIFO).
* **Monthly-cashflow is tax-free at the rebal layer.** The $500/mo
  deposit lands entirely on the most underweight leg — a discipline
  friendly to a BR swing broker that lets the user DCA without
  triggering realized-gains accounting.
* **Drift caveat:** The *max drift* figure is the worst single-bar
  deviation *before* rebalance. Daily mode resets to zero every
  bar ⇒ drift ≡ 0 by construction.

## Reference values

Winner (Phase 3.5b, daily rebal, tax_per_leg=15% via trade log):

| Ref | Value |
|---|---|
| Sharpe | 2.108 |
| CAGR | 25.56% |
| MaxDD | 10.86% |

The *Daily (winner)* column above reproduces these numbers from
the raw daily_returns cumprod (no per-leg trade tax applied at
the equity layer — matches `portfolio_3leg_ew/summary.json`).

## Citations

* Baseline reset: `[advances_fin_ml, p.298-299]`.
* Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17,
  Table 8]`.
* BR 15% IR: Investment Mandate §4.

## Artefacts

* `drift_3leg.png` — max |actual - target| weight across 3 legs
  for each mode, over the full window.
* `equity_3leg.png` — equity curves overlay (log scale).
* `summary_3leg.json` — structured snapshot.
