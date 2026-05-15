# PRE_REG - Phase 3 Iteration 014

## Hypothesis

Test a Track D gross-exposure spread: hold a leveraged equity engine (`UPRO`) and
short a defensive bond leg (`TLT`) only while the equity regime is risk-on. The
return engine is explicit leverage plus a negative bond hedge, not another
low-exposure defensive filter. Daily leverage requires volatility/regime control
because path dependency worsens in high-volatility periods
`[leverage_for_the_long_run, p.4-7]`; long/short rules must model gross exposure
and financing rather than assuming free leverage `[systematic_trading, p.137-148]`.
MCPT, PBO and DSR remain hard controls `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

Physical daily parquets required before testing:

- `SPY`, `UPRO`, `TLT`, `SHV`.
- Optional context: `GLD` only if present, not required for the rule.

Use the aligned daily adjusted-close window available across required tickers.
Signals are computed from completed bars and shifted one trading day before
execution.

## Exact Configs

Four pre-registered configs, each with annual financing/borrow drag of 5.0% on
gross exposure above 1.0 plus absolute short notional:

1. `upro100_tlt25_sma200`: risk-on if `SPY > SMA200`; weights `UPRO=1.00`, `TLT=-0.25`, `SHV=0.25`.
2. `upro125_tlt25_sma200`: risk-on if `SPY > SMA200`; weights `UPRO=1.25`, `TLT=-0.25`, `SHV=0.00`.
3. `upro125_tlt50_sma200`: risk-on if `SPY > SMA200`; weights `UPRO=1.25`, `TLT=-0.50`, `SHV=0.25`.
4. `upro100_tlt25_sma100`: risk-on if `SPY > SMA100`; weights `UPRO=1.00`, `TLT=-0.25`, `SHV=0.25`.

Risk-off allocation is `SHV=1.00`. SMA regime selection follows the leverage
rotation literature for avoiding high-volatility leveraged exposure
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`.

## Benchmarks

Primary Phase 3 benchmark hierarchy:

- `SPY` buy-and-hold on the aligned window.
- Equal-weight opportunity universe buy-and-hold: `UPRO/TLT/SHV`.

Context benchmarks:

- `UPRO` buy-and-hold.
- `TLT` buy-and-hold.
- `SHV` buy-and-hold.

SPY buy-and-hold is also the opportunity-cost benchmark. The strategy must beat
both primary benchmarks in CAGR and terminal wealth before any label above `fail`
is allowed.

## Gates Planned

- Economic CAGR and terminal wealth versus both primary B&H benchmarks.
- IS MCPT with 200 joint return-row permutations.
- WF MCPT with 100 permutations after initial train.
- PBO using 10 blocks across the 4 pre-registered configs.
- DSR using cumulative trials after this iteration.
- Walk-forward positive windows with train 756 / test 252 / step 252.
- Single-block OOS final 20% positive.
- Latest 63-trading-day FWD stress positive.
- Bootstrap 99.9% daily mean CI low > 0.
- Cross-lib/reference parity within +/-3pp CAGR.

## Kill Rules

- CAGR or terminal wealth <= `SPY` B&H => `fail`.
- CAGR or terminal wealth <= equal-weight `UPRO/TLT/SHV` B&H => `fail`.
- Any missing required physical parquet => `data_blocked`.
- PBO >= 0.5 or DSR p >= 0.05 blocks `strict_winner`.
- MCPT failure blocks `strict_winner`; MCPT does not replace PBO/DSR.
- MDD worse than 1.5x the worse primary benchmark MDD blocks `strict_winner`.

## Trial Accounting

- `cumulative_n_trials` before: 276.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 280.
