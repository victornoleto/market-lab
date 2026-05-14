# PRE_REG — 006-2026-05-14-equity-momentum-pullback

## Hypothesis

Daily equity-index pullbacks inside a long-term uptrend can capture short swing
mean reversion without buying structural downtrends. The trend filter uses a
lagged `SMA200`, and the pullback trigger uses a short rolling loss threshold;
both are classical trend/mean-reversion building blocks and remain intentionally
parsimonious `[trading_systems_methods, p.172]`, `[quant_trading_chan, p.142-143]`,
`[testing_tuning, p.327-335]`.

This is research only. Capital remains 100% Plano C per
`docs/investment-mandate.md`.

## Data And Window

- Physical daily Tiingo parquet files required before testing: `SPY`, `QQQ`,
  `SHV`.
- Audit required: file existence, timestamp range, timezone, columns and missing
  business-day rate.
- Intraday audit required before any short-swing claim: `data/tiingo/1hour/prices/`
  and `data/tiingo/15min/prices/` physical parquet counts. Manifest-only evidence
  is insufficient.
- No 1h/15m data will be synthesized from daily data.

## Exact Configs

All signals are computed on completed daily bars and shifted one bar before
returns are earned `[advances_fin_ml, p.31-34]`.

| name | ticker | trend | pullback | hold |
|---|---|---:|---:|---:|
| `spy_pb3_m2_hold5` | `SPY` | close > SMA200 | 3-day return <= -2% | 5 bars |
| `spy_pb5_m3_hold10` | `SPY` | close > SMA200 | 5-day return <= -3% | 10 bars |
| `qqq_pb3_m3_hold5` | `QQQ` | close > SMA200 | 3-day return <= -3% | 5 bars |
| `qqq_pb5_m5_hold10` | `QQQ` | close > SMA200 | 5-day return <= -5% | 10 bars |

When no position is active, hold `SHV` as cash proxy.

## Benchmark

Primary benchmark is same-asset buy-and-hold on the identical window. `SPY`
buy-and-hold is reported as opportunity-cost context.

## Planned Gates

- Economic Sharpe must beat same-asset buy-and-hold.
- IS MCPT: `p <= 0.01`, 200 reps smoke gate `[testing_tuning, p.318-320]`.
- WF MCPT: `p <= 0.05`, 100 reps smoke gate `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF windows: at least 8 windows and at least 6 positive
  `[testing_tuning, p.148-150]`.
- OOS final 20% positive, latest 63d FWD positive, bootstrap 99.9% mean-daily CI
  low > 0, and vector parity CAGR delta <= 3pp.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` with
  `n_trials=0`.
- If intraday files remain unavailable, record Track B as blocked and do not infer
  intraday behavior from daily bars.
- Do not tune thresholds after seeing validation output.
- Any PBO/DSR/MCPT failure blocks `strict_winner`; `candidate_watchlist` is only
  possible if economics and most robustness diagnostics are strong.

## Trial Accounting

- `cumulative_n_trials` before: 120.
- New strategy configs: 4.
- `cumulative_n_trials` after if data audit passes: 124.
