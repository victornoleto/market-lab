# Rebalance modes — 2-leg EW (LETF+QQQ)

**Path tag:** [SWING BROKER]  
**Window:** 2001-05-14 → 2026-04-14 (24.87 yrs, 6266 bars ≈).  
**Target weights:** EW (1/2, 1/2).  
**Initial capital:** $100,000.  
**Monthly deposit (cashflow mode):** $500 (0.50% of initial).  
**BR IR rate (realized gains on sells):** 15%.

## Comparative metrics

| Metric | Daily (Task A ref) | Monthly sell | Monthly cashflow |
|---|---|---|---|
| Equity final | $92,077,312 | $67,314,147 | $682,672,059 |
| CAGR | 31.59% | 29.94% | 42.63% |
| Sharpe | 1.888 | 1.800 | 1.881 |
| Volatility (ann.) | 15.16% | 15.20% | 19.96% |
| MaxDD | 14.41% | 14.46% | 18.15% |
| Max drift (any leg) | 0.00% | 5.23% | 49.30% |
| Mean per-bar max drift | 0.00% | 0.60% | 32.69% |
| Taxable events / yr | 0.0 | 12.1 | 0.0 |
| IR paid / yr (rebal) | $0 | $144,794 | $0 |
| Total IR paid | $0 | $3,600,319 | $0 |
| Total deposits | $0 | $0 | $150,000 |

## 2-leg vs 3-leg drift — observation

Compare the drift figures above against `comparison_3leg.md` to
see whether the drift-hypothesis holds: 2-leg with ρ=0.555 should
exhibit smaller per-bar max drift than 3-leg because leg returns
co-move more (both long equity). A smaller drift ceiling translates
directly into fewer / smaller taxable rebalance trades.

The sub-index `rebalance_modes/README.md` surfaces the delta
drift / delta tax between the two variants.

## Interpretation notes

* **Daily rebal tax = 0 at this layer.** Matches the C2 convention:
  per-leg trade-level tax (15% BR IR on each profitable exit) is
  already in the Task A 2-leg report; here we isolate *rebalance-
  mechanic* tax incidence.
* **Monthly-sell:** fires at end-of-month only; 15% IR on the
  overweight leg's realized gain (proportional cost basis).
* **Monthly-cashflow:** tax-free at the rebal layer — the monthly
  deposit lands entirely on the most underweight leg.
* **Drift note:** max drift is the worst per-bar deviation *before*
  rebalance. Daily mode resets to zero every bar ⇒ drift ≡ 0.

## Reference values

Task A 2-leg (daily rebal, tax_per_leg=15% via trade log):

| Ref | Value |
|---|---|
| Sharpe | 1.888 |
| CAGR | 31.59% |
| MaxDD | 14.41% |

The *Daily (Task A ref)* column above reproduces these numbers
from the raw daily_returns cumprod (no per-leg trade tax applied
at the equity layer — matches `letf_qqq_2leg_ew/summary.json`).

## Citations

* Baseline reset: `[advances_fin_ml, p.298-299]`.
* Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17,
  Table 8]`.
* BR 15% IR: Investment Mandate §4.

## Artefacts

* `drift_2leg.png` — max |actual - target| weight across 2 legs
  for each mode, over the full window.
* `equity_2leg.png` — equity curves overlay (log scale).
* `summary_2leg.json` — structured snapshot.
