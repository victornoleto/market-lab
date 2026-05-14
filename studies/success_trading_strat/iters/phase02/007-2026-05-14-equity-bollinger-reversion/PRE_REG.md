# PRE_REG — 007-2026-05-14-equity-bollinger-reversion

## Hypothesis

Daily equity-index mean reversion may be cleaner when the pullback trigger is
volatility-normalized by Bollinger Bands instead of a raw percent loss. The rule
buys `SPY`/`QQQ` only above a lagged `SMA200`, enters after a close below the
lower Bollinger Band, and exits on mean reversion to the middle band or a short
time stop. Bollinger Bands use moving average plus/minus standard-deviation bands
`[trading_systems_methods, p.323-324]`; simple mean-reversion strategies are a
core independent-trader category but require strict bias controls
`[quant_trading_chan, p.51-53]`. Walk-forward, MCPT, PBO and DSR remain hard
guards against tuning noise `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

- Physical daily files required before testing: `SPY`, `QQQ`, `SHV` under
  `data/tiingo/daily/prices/`.
- Intraday audit required but no intraday test is planned unless physical 1h/15m
  files exist. If absent, record Track B as blocked and do not synthesize bars
  `[testing_tuning, p.327-335]`.
- Full available daily adjusted-close history after warmup; signals shifted one
  completed daily bar before returns are earned.

## Exact Configs

1. `spy_bb20_2_hold10`: `SPY`, `SMA200`, Bollinger `20 x 2.0`, max hold 10 bars.
2. `spy_bb30_2_hold15`: `SPY`, `SMA200`, Bollinger `30 x 2.0`, max hold 15 bars.
3. `qqq_bb20_2_hold10`: `QQQ`, `SMA200`, Bollinger `20 x 2.0`, max hold 10 bars.
4. `qqq_bb30_2_hold15`: `QQQ`, `SMA200`, Bollinger `30 x 2.0`, max hold 15 bars.

Exit rule: while in a trade, exit when close is back above the middle band or
when `max_hold` bars have elapsed. While flat, hold `SHV`.

## Benchmark

Primary benchmark is same-asset buy-and-hold (`SPY` or `QQQ`) over the aligned
window. `SPY` buy-and-hold is also reported as opportunity-cost context.

## Planned Gates

- Economic Sharpe versus same-asset buy-and-hold.
- IS MCPT with 200 reps, strict pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 reps, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` over the 4-config panel `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative strategy trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF windows: at least 8 total and at least 6 positive `[testing_tuning, p.148-150]`.
- OOS final 20% positive; latest 63 trading days positive; bootstrap 99.9% mean
  daily CI low > 0; vector parity CAGR delta <= 3pp.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` with
  `n_trials=0`.
- If 1h/15m files are absent, do not synthesize intraday bars and do not make an
  intraday claim.
- If strict gates fail, mark `fail` unless economics and a majority of gates meet
  the Phase 2 `candidate_watchlist` bar; no deploy either way.
- Do not tune local Bollinger lengths, standard-deviation multipliers or exits
  after seeing results in this iteration `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 124.
- Planned new strategy configs: 4.
- `cumulative_n_trials` after if data audit passes: 128.
