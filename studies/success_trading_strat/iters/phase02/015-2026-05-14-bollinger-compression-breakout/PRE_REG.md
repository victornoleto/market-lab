# PRE_REG — 015-2026-05-14-bollinger-compression-breakout

## Hypothesis

Daily upper-Bollinger breakout after realized-volatility compression may capture
volatility expansion while avoiding ordinary noisy breakouts. Bollinger bands are
used as volatility-adjusted breakout envelopes `[trading_systems_methods, p.323-324]`,
and volatility clustering/compression motivates requiring the current realized
volatility percentile to be low before entry `[volatility_trading, p.36]`,
`[volatility_trading, p.58-59]`. Signals are lagged one completed daily bar to
avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

This is a different mechanism from Phase 2 lower-band mean reversion, gold
Donchian compression, Keltner/ATR breakout, MACD trend, ADX trend and VIDYA trend.

## Data And Window

- Physical data required before testing: `data/tiingo/daily/prices/{SPY,QQQ,GLD,xauusd,SHV}.parquet`.
- Intraday audit required but no intraday test will be run unless physical `1hour`
  or `15min` files exist; manifest-only entries are insufficient.
- Backtest window: max common daily window available after indicator warmup for
  each tested asset.
- Timezone/session audit: record parquet index timezone, first/last timestamp and
  missing business-day rate in `audit.json`.

## Exact Configs

1. `spy_bb20_2_rv20_p30_exit_mid`: `SPY`, Bollinger length 20, sigma 2.0,
   realized-volatility length 20, compression percentile 30, exit when prior close
   falls below middle band.
2. `qqq_bb20_2_rv20_p30_exit_mid`: same rule on `QQQ`.
3. `gld_bb20_2_rv20_p30_exit_mid`: same rule on `GLD`.
4. `xau_bb20_2_rv20_p30_exit_mid`: same rule on `xauusd`.

All configs hold `SHV` while flat. Entry requires prior close > prior upper band
and prior realized-volatility percentile <= threshold. Exit uses prior close <
prior middle band. A loop state machine is used so exposure persists between entry
and exit.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold on the exact aligned dates.
- Opportunity-cost benchmark: `SPY` buy-and-hold on the exact aligned dates.
- Phase 2 kill rule: if best strategy CAGR <= same-asset buy-and-hold CAGR, close
  `fail` and do not assign `candidate_watchlist`, `paper_trade_candidate` or
  `strict_winner` `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates Planned

- Economic CAGR and Sharpe versus same-asset buy-and-hold.
- IS MCPT with 200 permutations, pass only if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass only if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` using the four pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 8 windows and at least 6 positive windows `[testing_tuning, p.148-150]`.
- OOS, latest 63d FWD stress, bootstrap 99.9% mean-daily CI low > 0 and cross-lib/vector parity within 3pp CAGR `[advances_fin_ml, p.196-202]`.

## Kill Rules

- Missing required daily physical file before testing => `data_blocked`, `n_trials=0`.
- Missing intraday physical files => record intraday blocked; do not synthesize bars.
- Best CAGR <= same-asset buy-and-hold CAGR => `fail` regardless of lower drawdown.
- Any failed strict gate => not `strict_winner`.
- Do not locally tune Bollinger length, sigma, compression percentile or exit rule after results.

## Trial Accounting

- `cumulative_n_trials` before: 156.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 160.
