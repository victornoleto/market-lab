# Weekly Momentum Phase 4 Report

## Scope

Phase 4 tests whether the Phase 3 `lb80/k5` leads survive a better Tiingo price
layer for removed/delisted/renamed S&P 500 names. The validation change is
methodological: load the broad cached equity universe, then apply approximate
Wikipedia PIT S&P 500 membership at signal time. This lets removed constituents
participate when Tiingo has their historical prices `[advances_fin_ml, p.208-211]`.

## Tiingo Coverage Audit

Output preserved: `studies/weekly_momentum/evidence/phase4_tiingo_survivorship_audit/`.

Universe construction: current S&P 500, reconstructed start-date S&P 500, and
all Wikipedia selected-change added/removed tickers in the research window.

| metric | value |
|---|---:|
| Universe tickers | 769 |
| Available after online Tiingo backfill | 745 |
| Availability | 96.88% |
| Likely removed/renamed tickers | 260 |
| Likely removed/renamed available | 240 |
| Removed/renamed availability | 92.31% |

Interpretation: Tiingo materially improves the price layer versus the previous
current-member cache, but it is still not a perfect survivorship-free feed.
Twenty-four selected-change symbols remain unavailable or unresolved; ticker
rename/class mapping remains a residual risk.

## Expanded PIT Fixed Lead Rerun

Generated output: `studies/weekly_momentum/phase4_tiingo_pit_expanded_fixed/` (not retained after final cleanup; metrics and plots are consolidated in `FINAL_REPORT.md` and `plots/final/`).

| candidate | CAGR | MDD | Sharpe | SPY CAGR | SPY MDD | SPY Sharpe | DSR p | bootstrap low CAGR | 10 bps + DARF CAGR | OOS positive | rolling 5y beat SPY | rolling 10y beat SPY |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lb80/k5/SMA200` | 17.44% | -27.64% | 0.766 | 14.44% | -33.70% | 0.884 | 0.491 | -1.57% | -5.77% | 8/10 | 85.87% | 95.00% |
| `lb80/k5/SMA250` | 19.36% | -37.77% | 0.817 | 14.44% | -33.70% | 0.884 | 0.418 | -2.10% | 0.20% | 9/10 | 91.11% | 100.00% |

## Interpretation

- The leads still beat SPY on full-period CAGR, but the margin is much smaller
  once removed/delisted names can enter the PIT rank set.
- Both leads have lower Sharpe than SPY over the aligned period, so the apparent
  edge is not risk-adjusted enough for promotion.
- Both fail DSR and bootstrap lower-CAGR gates, so the hard validation stack
  rejects them `[advances_fin_ml, p.273-275]`, `[advances_fin_ml, p.196-202]`.
- `SMA250` keeps better long-window beat rates but pays with deeper drawdown than
  SPY and nearly flat tax-stressed CAGR.
- `SMA200` has a cleaner drawdown profile but too little excess return after
  costs/tax and fails the same statistical gates.

## Phase 4 Verdict

No weekly stock momentum strategy is valid after the improved Tiingo/PIT rerun.
The study should stop here unless a new, pre-registered hypothesis changes the
signal design or universe. More parameter search around this family is not
recommended because the best frozen leads weakened after the most important data
bias was reduced.

ETF replication remains lower priority: the stock signal did not transfer to
ETFs in prior tests, and the stock lead itself is no longer strong enough to
justify porting.
