# Hypothesis — Iter 010 HAA Volatility Throttle

## Hypothesis

Keep iter 009 HAA+Gold structurally intact and add only a simple volatility
throttle to the 85% dynamic sleeve. At each monthly rebalance, if the selected
dynamic sleeve's trailing 63-trading-day realized volatility is above a
pre-committed target, scale down the dynamic allocation and park the remainder
in `CASHX`. This follows Carver's volatility-standardized sizing principle:
position size should respond mechanically to instrument volatility rather than
letting realized risk drift unchecked `[systematic_trading, p.137-148]`.

## Primary Citation

- Volatility target and position sizing: `[systematic_trading, p.137-148]`.
- Longer volatility lookback for asset-allocation turnover control:
  `[systematic_trading, p.196-197]`.
- HAA monthly momentum shell: `[stocks_on_the_move, ch.6]`.
- Anti-overfit gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold misses a risk-budget control inside risk-on months: the
`VWOSIM` canary flips regimes, but it does not reduce exposure when the chosen
offensive sleeve is already in an elevated-volatility state.

## Datasets

- `educational`: VTSIM long synthetic window.
- `vt_real`: VTSIM proxy from 2008-06 because real VT is not pulled.
- `ndx_real`: QQQ stretch window.

All results are net of annual DARF via `AnnualDarfEngine`.

## Pre-Committed Kill Criteria

Kill the hypothesis if the selected volatility-throttle config does not beat
the baseline `no_throttle` config by at least +0.05 net Sharpe on the
educational dataset, or if zero datasets beat iter 009 by +0.10 Sharpe.

## Expected Budget

- Configs: 4 (`no_throttle`, `vol12`, `vol15`, `vol18`).
- Wall time: < 10 minutes using existing loop-local backtest script structure.
- New simulator: no. This is a small sizing overlay on existing HAA simulation.

## Implementation Plan

1. Reuse the iter 009 HAA+Gold implementation and validation battery.
2. Replace canary variants with a four-config volatility throttle grid.
3. Compute trailing 63-day realized volatility of the selected dynamic sleeve
   using data available at the month-end rebalance date.
4. Scale only the 85% dynamic sleeve down when volatility exceeds target;
   fixed 10% `KMLMSIM` and 5% `GLDSIM` sleeves stay unchanged.
5. Run all three datasets, write `results.json`, `verdict.json`, plots, final
   report, and update loop memory.
