# PRE_REG — 009 multi-asset EWMAC

## Hypothesis

Test a mechanism pivot away from volatility-ETP carry: fixed EWMAC trend forecasts
across liquid ETFs, allocated to the strongest positive forecast or to `SHV` when
no forecast is positive. Carver's EWMAC is a canonical trend-following forecast
with fixed fast/slow variants, and the iteration keeps the config count small to
avoid local overfit `[systematic_trading, p.118-119]`, `[testing_tuning, p.327-335]`.

## Data And Window

- Source: local Tiingo daily adjusted close parquet cache.
- Required files confirmed before pre-registration: `SPY`, `QQQ`, `TLT`, `IEF`,
  `GLD`, `SHV`.
- Common-window test starts at `2010-01-01` after joining required series.
- Signals are shifted one trading day before execution to avoid same-close
  lookahead `[quant_trading_chan, p.51]`.

## Exact Configs

Four fixed configs, no optimization inside the iteration:

| name | assets | EWMAC fast/slow | hold rule |
|---|---|---:|---|
| `ewmac_16_64_risk3` | `SPY,QQQ,TLT` | 16/64 | hold strongest positive forecast else `SHV` |
| `ewmac_32_128_risk3` | `SPY,QQQ,TLT` | 32/128 | hold strongest positive forecast else `SHV` |
| `ewmac_16_64_div5` | `SPY,QQQ,TLT,IEF,GLD` | 16/64 | hold strongest positive forecast else `SHV` |
| `ewmac_32_128_div5` | `SPY,QQQ,TLT,IEF,GLD` | 32/128 | hold strongest positive forecast else `SHV` |

Forecast definition: `EMA_fast(close) - EMA_slow(close)` divided by trailing
price volatility proxy `close.pct_change().rolling(25).std() * close`, clipped only
implicitly by ranking sign. The vol normalization is a scale control, not a new
selection grid `[systematic_trading, p.196-197]`.

## Benchmark

Primary benchmark: equal-weight buy-and-hold of the same risk assets for the best
config's asset set, rebalanced implicitly by daily return averaging. Secondary
benchmark: `SPY` buy-and-hold on the same dates.

## Planned Gates

- Economic: best config must beat same-universe equal-weight benchmark Sharpe and
  have positive CAGR.
- IS MCPT: fixed best config, 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: fixed best config, 100 permutations, 4y train / 1y test / 1y step,
  pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: 8-block CSCV over the four configs, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF windows: at least 6 positive windows out of at least 8
  `[testing_tuning, p.148-150]`.
- OOS: final 20% positive total return `[advances_fin_ml, p.196-202]`.
- FWD stress: last 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% mean daily CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Any failed hard gate blocks `winner`.
- If data are missing or common history is insufficient, stop as `data_blocked`.
- If EWMAC fails MCPT/PBO/DSR, add this exact family to dead ends and do not tune
  local EWMAC spans next without a new mechanism `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 20.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if tested: 24.
