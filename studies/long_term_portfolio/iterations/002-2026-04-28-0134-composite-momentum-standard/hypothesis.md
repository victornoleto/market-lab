# Hypothesis — Composite Momentum Standard

Composite Momentum Standard can Pareto-advance iter 009 HAA+Gold by replacing HAA's 13612W canary/ranking stack with a simpler SPY 200-day regime filter, 8-month absolute/relative momentum, and inverse 3-month volatility sizing across broad asset sleeves. The pre-committed simple version uses monthly rebalancing: if `SPYSIM` is above its 200-day SMA, select the top 4 assets with positive 8-month return from `SPYSIM`, `QQQSIM`, `VEASIM`, `TLTSIM`, `IEFSIM`, `GLDSIM`, and `KMLMSIM`, weighted by inverse 63-day volatility; if `SPYSIM` is below its 200-day SMA or no asset passes absolute momentum, hold 60% `IEFSIM` + 40% `GLDSIM`. Momentum choices follow Clenow's cross-sectional momentum framing `[stocks_on_the_move, p.21-30]`; validation gates follow Lopez de Prado `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Primary Citation

- `[stocks_on_the_move, p.21-30]` — rank assets by momentum and hold the strongest names rather than forecasting exact returns.
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` — PBO, DSR, bootstrap, and cross-library validation gates.

## Edge Source

Iter 009 HAA+Gold uses one `VWOSIM` canary and 13612W ranking; Composite Momentum tests whether a broad SPY trend gate plus inverse-vol top-4 selection captures smoother cross-asset leadership while avoiding BAA's broader-canary defensiveness `[stocks_on_the_move, p.21-30]`.

## Datasets

- `educational`: VTSIM long-window proxy, constrained by `KMLMSIM`/`QQQSIM` history.
- `vt_real`: VTSIM proxy from 2008-06 because real VT is not pulled.
- `ndx_real`: QQQSIM stretch window from 2010-02.

## Pre-Committed Kill Criteria

Kill if educational net Sharpe <= 1.120. This strategy is BestFolio top-ranked for Sharpe, so it must at least match the existing iter 009 Sharpe frontier before variants deserve more budget.

## Expected Budget

- Configs: 1.
- Wall-time: under 10 minutes for simulation, gate battery, scoring, plots, and focused tests.

## Implementation Plan

1. Add a loop-local `composite_momentum.py` module with pandas simulator, AnnualDarfEngine tax pass, gates, results, and verdict generation.
2. Add focused tests first for risk-on top-4 inverse-vol selection, risk-off defensive sleeve, and numpy reference CAGR parity.
3. Run all three datasets, save `results.json` with `returns_series` for the single config per dataset.
4. Score with `studies/long_term_portfolio/scoring.py`, generate mandatory plots, then update `final_report.md`, `verdict.json`, `BASE_MEMORY.md`, `DEAD_ENDS.md` if structural fail, and `jornada/`.
