# Weekly Momentum Phase 3 Report

## Scope

Phase 3 adds an approximate point-in-time S&P 500 membership layer using the
repository's Wikipedia SPX reconstruction. This improves on current-membership
ranking but is still **not** a survivorship-free/delisted price feed: removed
tickers only participate when they exist in the Tiingo cache, ticker-renames are
not fully reconciled, and Wikipedia selected changes are incomplete. Treat this
as an intermediate robustness screen before paid PIT/SF data.

PIT membership and anti-overfit gates follow the project validation rationale
`[advances_fin_ml, p.208-211]`; DSR and bootstrap follow `[advances_fin_ml,
p.273-275]`, `[advances_fin_ml, p.196-202]`.

## Implementation

- `simulate_weekly_momentum(..., universe_by_date=...)` now filters the ranking
  universe at signal time.
- `sp500_pit_universe_provider()` preloads cached Wikipedia current constituents
  and selected changes once, then serves date-specific membership.
- `validate_candidates.py --sp500-pit` and `sweep.py --sp500-pit` activate the
  PIT approximation for current S&P 500 studies.

## Promoted Fixed Candidates Under PIT

Original generated output: `studies/weekly_momentum/phase3/sp500_pit_fixed_promoted/` (not retained after final cleanup; metrics are summarized here and in `../FINAL_REPORT.md`).

| candidate | CAGR | MDD | Sharpe | 10 bps CAGR | 10 bps + DARF CAGR | DSR p | OOS positive | bootstrap low CAGR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fixed_aggressive_sp500` (`lb60/k3/sma200`) | 14.26% | -38.91% | 0.608 | 12.45% | -8.45% | 0.728 | 5/9 | -8.47% |
| `phase2_fixed_lb80_k5_sma200` | 25.20% | -28.45% | 1.030 | 23.46% | -1.27% | 0.185 | 7/9 | 4.95% |
| `phase2_fixed_lb80_k5_sma250` | 26.57% | -32.24% | 1.053 | 24.82% | 4.68% | 0.165 | 7/9 | 3.16% |

Interpretation: the original `lb60/k3/sma200` was substantially dependent on
current-membership bias. The `lb80/k5` variants survive much better: they retain
SPY-beating CAGR, lower MDD than SPY, positive OOS structure and positive
bootstrap lower CI. However, they fail DSR after the 200-trial penalty and the
tax proxy is still a major drag.

## PIT Neighborhood Sweep

Original generated output: `studies/weekly_momentum/sweeps/stocks/phase3_sp500_pit_fixed_aggressive_neighborhood/` (not retained after final cleanup).

| config | CAGR | MDD | Sharpe | rolling 1y beat SPY | rolling 3y beat SPY |
|---|---:|---:|---:|---:|---:|
| `lb80_k5_sma250` | 26.57% | -32.24% | 1.053 | 70.10% | 82.77% |
| `lb80_k5_sma200` | 25.20% | -28.45% | 1.030 | 71.06% | 83.80% |
| `lb80_k5_sma175` | 24.10% | -28.45% | 1.000 | 69.11% | 82.23% |
| `lb80_k4_sma200` | 25.54% | -31.14% | 0.988 | 63.79% | 85.57% |
| `lb80_k4_sma250` | 27.16% | -38.55% | 1.015 | 63.28% | 84.42% |

Interpretation: under PIT approximation, the robust island moved clearly toward
`lookback=80`, `top_k=4-5`, and `SMA175-250`, with `k=5` giving the cleanest
drawdown/stability tradeoff. This is a real evolution versus the original
`lb60/k3` lead.

## Dynamic S&P Context Under PIT

Original generated output: `studies/weekly_momentum/phase3/sp500_pit_dynamic_context/` (not retained after final cleanup).

| candidate | CAGR | MDD | Sharpe | PBO | DSR p | OOS positive | bootstrap low CAGR |
|---|---:|---:|---:|---:|---:|---:|---:|
| `dynamic_wf_sp500` | -3.33% | -63.14% | -0.003 | 0.623 | 0.997 | 4/9 | -22.34% |

Interpretation: the dynamic WF process that looked attractive under
current-membership data collapses under PIT membership. It is removed from the
promotion path unless a materially different, pre-registered dynamic selection
rule is proposed.

## Phase 3 Verdict

- The study did evolve: the original lead was weakened by PIT, but the Phase 2
  neighborhood produced stronger candidates (`lb80/k5/sma200-250`) that survive
  the PIT approximation better.
- No strategy is deployable yet. The promoted candidates pass several practical
  screens but fail DSR under the conservative 200-trial penalty and remain
  exposed to delisted-price/feed limitations.
- Next useful step is not more broad sweeping; it is paid survivorship-free/PIT
  data or a delisting-aware data reconstruction, then rerun only the frozen
  `lb80/k5` candidates.
- Final consolidation lives in `STRATEGY_TESTED_SUMMARY.md`, with top-6
  decision-relevant strategy comparison and plots versus SPY.

## PIT Coverage Audit

Original generated output: `studies/weekly_momentum/phase3/pit_coverage_audit/` (not retained after final cleanup; conclusion is summarized here).

The Wikipedia PIT membership layer was audited weekly against the local Tiingo
stock cache:

- Dates sampled: `639`.
- Mean PIT member coverage in cache: `98.27%`.
- Median PIT member coverage in cache: `98.03%`.
- Worst PIT member coverage in cache: `96.85%`.
- Mean missing members per sampled date: `8.8`.

Interpretation: cache coverage is high enough for the PIT approximation to be a
useful intermediate screen. The deterioration from current-membership results to
PIT results is therefore unlikely to be caused by broad cache gaps; it is more
likely the expected removal of current-constituent survivorship bias. Residual
missing tickers still matter, especially ticker-class/rename cases such as
`BRK-B`/`BF-B` and removed/delisted constituents, so paid survivorship-free data
remains the final blocker.

## lb80/k5/SMA250 Deep Dive

Original generated output: `studies/weekly_momentum/phase3/lb80_k5_sma250_deep_dive/` (not retained after final cleanup; conclusion is summarized here).

The current best PIT candidate was decomposed for DSR and tested across every
possible 1/3/5/10/15/20y entry window.

DSR decomposition:

| n_trials | test | p-value | pass? | annual Sharpe benchmark |
|---:|---|---:|---|---:|
| 1 | PSR no trial penalty | 0.00009 | yes | 0.000 |
| 10 | DSR | 0.01520 | yes | 0.443 |
| 25 | DSR | 0.04068 | yes | 0.562 |
| 50 | DSR | 0.07159 | no | 0.641 |
| 100 | DSR | 0.11312 | no | 0.712 |
| 200 | DSR | 0.16466 | no | 0.778 |

Interpretation: the strategy fails DSR at `n_trials=200` because its observed
annual Sharpe (~1.05) is not sufficiently above the expected best Sharpe after a
broad 200-config search. With no trial penalty, or with a small pre-registered
family (`<=25` trials), the same return stream would pass. This is a
multiple-testing penalty issue, not a standalone PSR issue `[advances_fin_ml,
p.273-275]`.

Entry-window robustness:

| window | possible windows | pct beating SPY | worst strategy CAGR | worst CAGR edge vs SPY |
|---:|---:|---:|---:|---:|
| 1y | 2931 | 70.01% | -23.94% | -41.11pp |
| 3y | 2427 | 82.74% | 2.15% | -10.31pp |
| 5y | 1923 | 100.00% | 15.48% | +2.39pp |
| 10y | 663 | 100.00% | 20.36% | +7.77pp |
| 15y | 0 | n/a | n/a | n/a |
| 20y | 0 | n/a | n/a | n/a |

Interpretation: the strategy is not entry-timing independent at short horizons:
there are bad 1y and 3y starts. It is much more robust at 5y and 10y horizons,
where every available start beats SPY on CAGR. 15y/20y cannot be measured with
the current 2013-2026 candidate history.
