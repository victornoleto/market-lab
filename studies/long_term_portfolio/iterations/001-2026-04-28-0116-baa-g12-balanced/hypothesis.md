# Hypothesis — BAA-G12 Balanced

## Hypothesis

Bold Asset Allocation G12 Balanced can Pareto-advance iter 009 HAA+Gold by using broader canary breadth and a wider offensive universe than HAA. The simple version tests monthly BAA-G12 with four canaries (`SPYSIM`, `VEASIM`, `VWOSIM`, `BNDSIM`), 13612W absolute momentum for risk regime, top-6 offensive assets by SMA(12) relative momentum in offensive mode, and top-3 defensive assets by SMA(12) with `CASHX` replacement when an asset underperforms cash. This keeps the mechanism simple before any ML/HMM/multi-signal composition, consistent with the project rule that momentum choices must cite book support `[stocks_on_the_move, ch.6]`.

## Primary Citation

- Keller, W.J. (2022), *Relative and Absolute Momentum in Times of Rising/Low Yields: Bold Asset Allocation (BAA)*, SSRN 4166845.
- Clenow supports cross-sectional momentum ranking as the book citation for the rotation mechanism `[stocks_on_the_move, ch.6]`.
- PBO, DSR, bootstrap, and cross-library gates follow López de Prado `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold uses one canary (`VWOSIM`) and four offensive assets; BAA-G12 tests whether broader canary breadth plus a wider cross-asset opportunity set captures crisis/offensive rotations HAA misses `[stocks_on_the_move, ch.6]`.

## Datasets

- `educational`: `VTSIM` proxy, 1994-05-01 to 2026-04-24, constrained by `VWOSIM` canary history.
- `vt_real`: `VTSIM` proxy, 2008-06-01 to 2026-04-24, until real `VT` is pulled per `INFRASTRUCTURE.md`.
- `ndx_real`: `QQQSIM` stretch test, 2010-02-01 to 2026-04-24.

## Pre-Committed Kill Criteria

Kill if educational Sharpe is `<= 1.120`, because the strategy then fails to advance the iter 009 Sharpe frontier before considering the shorter real/proxy windows.

## Expected Budget

- Configs: 1 pre-committed config.
- Wall-time: < 10 minutes for simulation, gates, scoring, plots, and focused tests.
- Tests: add focused TDD coverage for BAA signal mechanics, then run that test file plus the repository pytest baseline if feasible.

## Implementation Plan

1. Add a loop-local BAA simulator under this iteration directory only.
2. Reuse `load_testfolio_frame`, `sharpe`, `cagr`, `max_drawdown`, DSR, walk-forward helpers, and bestfolio `scoring.py`.
3. Add a numpy-pure BAA reference for G7 CAGR parity `[advances_fin_ml, p.31-34]`.
4. Run all three datasets, save `results.json` with `returns_series` for the top config per dataset.
5. Score via `score_strategy(...)`, save `verdict.json`, generate mandatory plots, then update `BASE_MEMORY.md`, `DEAD_ENDS.md` if structural fail, and `jornada/`.
