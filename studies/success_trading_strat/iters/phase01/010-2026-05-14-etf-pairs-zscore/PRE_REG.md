# PRE_REG — 010 ETF pairs z-score

## Hypothesis

Test a small market-neutral ETF pairs family using fixed ratio z-score mean
reversion. Chan frames cointegration/stationarity as the economic basis for pairs
trading and warns to keep models simple because data-snooping creeps into trading
rules `[algo_trading_chan, p.5-6]`, `[algo_trading_chan, p.51]`. The z-score entry
and zero exit follow the Bollinger pairs template `[algo_trading_chan, p.71-73]`.
This is a mechanism pivot away from trend, long-only momentum, volatility targeting,
RSI mean reversion and VXX carry; if it fails MCPT/PBO/DSR, do not tune local
windows `[testing_tuning, p.327-335]`.

## Data And Window

- Source: local Tiingo daily adjusted-close parquet files in `data/tiingo/daily/prices/`.
- Required tickers: `GLD`, `SLV`, `TLT`, `IEF`, `SPY`, `QQQ`, `SHV`.
- Window: common adjusted-close history from 2010-01-01 onward.
- Execution: signals are computed on close `t` and traded on return `t+1` via one-bar shift to avoid same-close lookahead `[quant_trading_chan, p.51]`.

## Configs

Exactly four configs are consumed as trials:

1. `gld_slv_z60_e1`: ratio `GLD/SLV`, lookback 60 trading days, entry z-score 1.0, exit z-score 0.0.
2. `gld_slv_z120_e1`: ratio `GLD/SLV`, lookback 120 trading days, entry z-score 1.0, exit z-score 0.0.
3. `tlt_ief_z60_e1`: ratio `TLT/IEF`, lookback 60 trading days, entry z-score 1.0, exit z-score 0.0.
4. `spy_qqq_z60_e1`: ratio `SPY/QQQ`, lookback 60 trading days, entry z-score 1.0, exit z-score 0.0.

Position rule: if ratio z-score is above +entry, short leg A and long leg B at
equal notional; if below -entry, long leg A and short leg B; exit to flat/SHV cash
when z-score crosses zero. Equal-notional log-ratio style avoids fitting hedge
ratios in this first smoke `[algo_trading_chan, p.65-66]`.

## Benchmark

Primary benchmark is `SHV` cash-like buy-and-hold over the same dates, because the
strategy is market-neutral/flat-capable rather than long-only equity. Secondary
diagnostic benchmark is SPY buy-and-hold for opportunity cost `[algo_trading_chan, p.23]`.

## Planned Gates

- Economic: best config Sharpe must exceed SHV Sharpe and CAGR must be positive.
- IS MCPT: fixed best config, 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: fixed best config, 100 permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8 blocks over the 4-config panel, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05`, using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6 positive windows out of 8 or more
  `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: final 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% mean daily CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required data are missing, stop as `data_blocked` and consume `n_trials=0`.
- If PBO or DSR fails, no winner claim regardless of economics.
- If MCPT fails, do not retune z-score/lookback in the same iteration.
- If performance depends only on a single favorable recent window, close as fail.

## Trial Accounting

- `cumulative_n_trials` before: 24.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if data are available: 28.
