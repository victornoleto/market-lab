# PRE_REG — 005-carver-ewmac-trend

## Hypothesis

Test whether a non-LRS Carver EWMAC trend-following forecast on `SPYSIM`, applied
as partial long exposure to `UPROSIM` and otherwise `CASHX`, can beat SPY
buy-and-hold and pass hard overfit gates. EWMAC is a distinct trend-following
mechanism from SMA-threshold LRS, using volatility-adjusted moving-average
crossover forecasts capped at +/-20 `[systematic_trading, p.112-119]`,
`[systematic_trading, p.282-285]`.

## Exact Configs

- `ewmac_16_64_upro_cash`: fast EWMA 16, slow EWMA 64, scalar 3.75, forecast cap
  +/-20 `[systematic_trading, p.285]`.
- `ewmac_32_128_upro_cash`: fast EWMA 32, slow EWMA 128, scalar 2.65, forecast
  cap +/-20 `[systematic_trading, p.285]`.

For each config, raw forecast is `(EWMA_fast - EWMA_slow) / 25-day price-point
volatility`, scaled by the cited scalar and clipped to +/-20. The portfolio uses
`max(forecast, 0) / 20` as the next-day `UPROSIM` weight and allocates the
remainder to `CASHX`. Negative forecasts are cash-only; no shorting. The 25-day
volatility lookback is Carver's default for systems trading `[systematic_trading,
p.155-157]`. All forecasts and volatility estimates are shifted one trading day
before return application to avoid same-close look-ahead `[advances_fin_ml,

## Data And Window

- Source: `data/testfolio/cache/history.parquet` via existing
  `load_testfolio_series`.
- Required labels: `SPYSIM`, `UPROSIM`, `CASHX`.
- Expected common long-history window: approximately 1986-01-02..2026-04-17,
  subject to available overlap.
- Benchmark: same-window `SPYSIM` buy-and-hold.

## Planned Gates

- Economic: CAGR > SPY and terminal equity ratio > 1.0.
- PBO `< 0.5` using 10 blocks; unstable with only two pre-registered configs but
  still recorded `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trial count after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 equal chronological windows beat SPY
  `[testing_tuning, ch.12]`.
- OOS: final 25% CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- FWD stress: final 3y CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of daily excess-return mean annualized > 0
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized implementation and explicit loop implementation CAGR
  within +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If best config does not beat SPY CAGR and terminal equity, verdict is `fail`
  even if some statistical gates pass.
- If any hard gate fails, `winner=false`.
- Do not add more EWMAC speeds after seeing results; additional speeds would be a
  local grid inside a failed family unless a later iteration pre-registers a new
  mechanism `[systematic_trading, p.60]`.
- If required labels are unavailable, mark `data_blocked` and do not substitute.

## Trial Accounting

- `cumulative_n_trials` before: 8.
- Current iteration `n_trials`: 2.
- `cumulative_n_trials` after: 10.

## Conservative Ambiguity Handling

Public docs already have pre-existing unstaged edits outside this iteration.
This iteration will preserve them and update only required v2 artifacts plus
`MEMORY.md`, unless a mandate guard blocks execution.
