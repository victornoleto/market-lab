# PRE_REG — 002-2026-05-14-gold-rsi-exhaustion

## Hypothesis

Daily gold mean reversion after short-term downside exhaustion can improve
risk-adjusted returns versus same-asset buy-and-hold by entering `GLD` only after
`RSI(2)`/`RSI(3)` oversold readings while a slow trend filter is positive.
RSI-style short-horizon reversion is a classical countertrend setup, but it is
suspect without explicit anti-overfit controls `[quant_trading_chan, p.51]`,
`[quant_trading_chan, p.142-143]`. The slow filter keeps the rule from buying
prolonged downtrends, consistent with trend/regime filtering guidance
`[trading_systems_methods, p.13]`.

## Data And Window

- Primary asset: `GLD` daily physical file from `data/tiingo/daily/prices/GLD.parquet`.
- Defensive sleeve: `SHV` daily physical file.
- Context benchmark: `SPY` daily physical file.
- Intraday audit: check `data/tiingo/1hour/prices/` physical file count and `GLD`/`xauusd`
  presence; do not synthesize intraday bars if missing.
- Use full available aligned daily window after indicator warmup.

## Exact Configs

1. `gld_rsi2_e5_x60_sma200`: buy after `RSI(2) <= 5` and `price > SMA200`; exit at `RSI(2) >= 60`.
2. `gld_rsi2_e10_x70_sma200`: buy after `RSI(2) <= 10` and `price > SMA200`; exit at `RSI(2) >= 70`.
3. `gld_rsi3_e10_x60_sma150`: buy after `RSI(3) <= 10` and `price > SMA150`; exit at `RSI(3) >= 60`.
4. `gld_rsi3_e15_x70_sma150`: buy after `RSI(3) <= 15` and `price > SMA150`; exit at `RSI(3) >= 70`.

All signals are close-only and shifted one bar before execution to avoid same-close
lookahead `[advances_fin_ml, p.31-34]`.

## Planned Gates

- Benchmark: same-window `GLD` buy-and-hold on Sharpe, with `SPY` as opportunity-cost context.
- IS MCPT: 200 permutations, pass only if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: 100 permutations, pass only if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: pass if `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- WF windows: require at least 8 windows and 6 positive `[testing_tuning, p.148-150]`.
- OOS, latest 63d FWD stress, bootstrap 99.9% daily-mean CI, and vector parity.

## Kill Rules

- If required daily physical files are absent, stop as `data_blocked` with `n_trials=0`.
- If intraday files are absent, do not run 1h/15m tests or synthesize them.
- If best config fails MCPT, PBO or DSR, mark the family as a dead end unless a future
  mechanism changes materially `[testing_tuning, p.327-335]`.
- No capital allocation; mandate remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 104.
- Planned new strategy configs: 4.
- `cumulative_n_trials` after, if all configs run: 108.
