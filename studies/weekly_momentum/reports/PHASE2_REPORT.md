# Weekly Momentum Phase 2 Report

## Scope

Phase 2 continues the deploy-candidate funnel after the first PBO/DSR/OOS/
bootstrap screen. It follows two tracks:

- main track: improve `fixed_aggressive_sp500`, the only candidate that passed
  the first statistical screen;
- exploratory track: retest `dynamic_wf_all_stocks` with liquidity/listing-age
  filters because small/mid-cap convexity is economically plausible but the
  original family failed PBO.

Momentum ranking and SPY trend-risk filters remain sourced to
`[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.66-67, p.81]`. PBO/DSR/
bootstrap gates follow `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
p.273-275]`, `[advances_fin_ml, p.196-202]`.

## Main Track: Fixed Aggressive Neighborhood

Grid:

- lookbacks: `40,50,60,70,80`
- `top_k`: `2,3,4,5`
- market filters: `sma150,sma175,sma200,sma225,sma250`
- universe: current S&P 500
- original generated output: `studies/weekly_momentum/sweeps/stocks/phase2_fixed_aggressive_neighborhood/` (not retained after final cleanup)

Top neighborhood configs:

| config | CAGR | MDD | Sharpe | rolling 1y beat SPY | rolling 3y beat SPY |
|---|---:|---:|---:|---:|---:|
| `lb80_k5_sma200` | 41.96% | -38.56% | 1.313 | 74.44% | 95.71% |
| `lb60_k3_sma200` original | 47.43% | -48.30% | 1.244 | 75.70% | 98.60% |
| `lb80_k4_sma200` | 45.88% | -44.13% | 1.329 | 72.42% | 91.88% |
| `lb80_k5_sma250` | 42.74% | -39.68% | 1.303 | 72.18% | 89.45% |

Validation panel:
`studies/weekly_momentum/phase2/main_fixed_aggressive/CANDIDATE_VALIDATION_REPORT.md` (generated bundle not retained after final cleanup).

| candidate | CAGR | MDD | Sharpe | 10 bps CAGR | 10 bps + DARF CAGR | DSR p | OOS positive | bootstrap low CAGR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fixed_aggressive_sp500` | 47.43% | -48.30% | 1.244 | 45.25% | 16.64% | 0.046 | 7/9 | 8.15% |
| `phase2_fixed_lb80_k4_sma200` | 45.88% | -44.13% | 1.329 | 44.07% | 15.73% | 0.024 | 7/9 | 9.19% |
| `phase2_fixed_lb80_k5_sma200` | 41.96% | -38.56% | 1.313 | 40.17% | 12.15% | 0.028 | 8/9 | 8.45% |
| `phase2_fixed_lb80_k5_sma250` | 42.74% | -39.68% | 1.303 | 40.93% | 19.13% | 0.032 | 8/9 | 7.13% |

Interpretation: the edge is not a single-parameter spike. The `lb80/k5`
variants materially reduce drawdown while preserving DSR/OOS/bootstrap pass.
The best operational lead is now ambiguous:

- `lb80_k5_sma200` is the drawdown/OOS-improvement lead;
- `lb80_k5_sma250` has slightly worse drawdown but much better 10 bps + DARF
  CAGR in this proxy model;
- original `lb60_k3_sma200` still maximizes gross CAGR but keeps larger drawdown.

## Exploratory Track: Filtered All-Stocks Dynamic WF

Two all-stock filters were tested to reduce liquidity/listing noise before any
PIT universe work:

| filter | output | CAGR | MDD | Sharpe | PBO | DSR p | OOS positive | bootstrap low CAGR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| age `>=756` bars, median ADV20 `>= $5m` | generated bundle not retained | 60.53% | -56.31% | 1.219 | 0.865 | 0.177 | 7/9 | -0.80% |
| age `>=1260` bars, median ADV20 `>= $10m` | generated bundle not retained | 47.77% | -46.82% | 1.036 | 0.508 | 0.364 | 8/9 | 0.18% |

Interpretation: filtering confirms that the all-stocks dynamic family has real
gross convexity, but it still fails the PBO/DSR promotion screen. The stricter
filter nearly fixes PBO but loses Sharpe/DSR. This track remains exploratory and
should not displace the fixed-aggressive main track until PIT/listing/delisting
robustness is implemented.

## Current Phase 2 Verdict

- Promote the fixed-aggressive neighborhood, especially `lb80_k5_sma200` and
  `lb80_k5_sma250`, to the next validation round.
- Keep `dynamic_wf_all_stocks` as an exploratory research lead only.
- Do not deploy any candidate before point-in-time universe, delisting handling,
  execution-grade costs and broker/tax modeling are complete.
