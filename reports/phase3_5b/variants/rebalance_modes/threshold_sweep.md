# Threshold rebalance sweep — 3-leg EW (LETF+QQQ+GLD)

**Path tag:** [SWING BROKER]  
**Phase:** 3.5b-addendum, Task C4 (drift-triggered variant).  
**Window:** 2004-11-18 → 2026-04-14 (21.36 yrs).  
**Target weights:** EW (1/3, 1/3, 1/3).  
**Initial capital:** $100,000.  
**BR IR rate (realized gains on sells):** 15%.

## Cadences

| Mode | Rule |
|---|---|
| daily            | reset to target every bar (no rebal-layer tax) |
| threshold 5pp    | rebal only when any leg drifts > 5 pp |
| threshold 10pp   | rebal only when any leg drifts > 10 pp |
| threshold 15pp   | rebal only when any leg drifts > 15 pp |
| threshold 20pp   | rebal only when any leg drifts > 20 pp |
| annual only      | monthly-sell mechanic, freq='Y' (year-end only) |
| never            | pure buy-and-hold (threshold 1e9) |

## Comparative metrics

| Mode | CAGR | Sharpe | ΔSharpe vs daily | MaxDD | Max drift | Mean drift | Events | Dates/yr | IR paid / yr | Total IR |
|---|---|---|---|---|---|---|---|---|---|---|
| daily (winner) | 25.56% | 2.108 | +0.000 | 10.86% | 0.00% | 0.00% | 0 | 0.00 | $0 | $0 |
| threshold 5pp | 24.66% | 2.002 | -0.106 | 11.10% | 4.99% | 2.27% | 31 | 1.31 | $23,815 | $508,715 |
| threshold 10pp | 25.47% | 1.990 | -0.118 | 11.12% | 10.00% | 4.08% | 14 | 0.61 | $20,978 | $448,116 |
| threshold 15pp | 26.35% | 1.972 | -0.136 | 12.24% | 14.97% | 7.64% | 8 | 0.37 | $17,582 | $375,579 |
| threshold 20pp | 27.15% | 1.972 | -0.136 | 12.32% | 19.99% | 9.46% | 6 | 0.28 | $21,680 | $463,099 |
| annual only (Y) | 25.07% | 1.967 | -0.141 | 11.56% | 13.39% | 3.36% | 28 | 1.08 | $22,001 | $469,973 |
| never (BH) | 40.33% | 1.881 | -0.226 | 17.99% | 65.62% | 43.89% | 0 | 0.00 | $0 | $0 |

## DARFs/yr — operational translation

A Brazilian retail investor must file a DARF for each month in
which realized capital gains exceed zero. **DARFs/yr ≈ unique
rebalance dates per year**, because multiple legs sold on the
same date consolidate to a single monthly filing. The 'Dates/yr'
column above is therefore the practical DARF burden from the
rebalance layer — the **inside-leg** trade-level DARFs (~12/yr
from LETF regime flips + QQQ/GLD Donchian breakouts) are
additive and unchanged across cadences.

| Mode | DARFs/yr (rebal layer) | Total DARFs/yr est. |
|---|---|---|
| daily (winner) | 0.00 | 12.0 |
| threshold 5pp | 1.31 | 13.3 |
| threshold 10pp | 0.61 | 12.6 |
| threshold 15pp | 0.37 | 12.4 |
| threshold 20pp | 0.28 | 12.3 |
| annual only (Y) | 1.08 | 13.1 |
| never (BH) | 0.00 | 12.0 |

## Interpretation

* **Higher thresholds → fewer events, higher drift.** The
  5 → 20 pp progression trades tax events for weight drift; at
  20 pp the rebalance layer contributes only a handful of
  events over the full ~21-year window.
* **`never` (pure BH)** is the natural lower bound: zero
  rebalance-layer tax, max drift at the maximum observed value.
  Compare its Sharpe to the thresholded variants to see the
  risk-budget erosion from abandoning rebalance.
* **Best threshold (by Sharpe):** `threshold 5pp` at Sharpe=2.002, 1.31 dates/yr. This is the operational compromise point.
* **Annual-only** incurs ~1 DARF/yr from the rebal layer; its
  Sharpe (1.967) vs `never` (1.881)
  quantifies the value of the single end-of-year reset.

## Operational recommendation

For a BR retail swing investor using the 3-leg EW winner, the
`threshold 5pp` cadence minimises DARFs/yr from the
rebalance layer to ~1.3 while preserving
95.0% of the
winner's daily Sharpe. It is the recommended **fallback** for
users who find daily rebalance operationally prohibitive. The
**production default remains daily rebalance on the 3-leg**
winner, per the Phase 3.5b summary; this sweep documents a
principled, lower-friction alternative rather than a new winner.

## Citations

* Threshold rebalancing as institutional practice:
  `[advances_fin_ml, p.275-278]`.
* Daily reset baseline: `[advances_fin_ml, p.298-299]`.
* Drift vs tax tradeoff framing: `[leverage_for_the_long_run,
  p.17, Table 8]`.
* BR 15% IR on realized gains: Investment Mandate §4.

## Artefacts

* `threshold_sweep_summary.json` — structured snapshot.
* `threshold_sweep_events.png` — events/yr vs threshold plot.
