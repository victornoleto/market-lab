# PRE_REG — 019-2026-05-14-force-index-volume-impulse

## Hypothesis

Daily volume impulse can identify short swing continuation only when price is
already in an uptrend. Elder's Force Index combines volume with close-to-close
price change, with short EMA smoothing commonly used to detect buying/selling
pressure `[trading_systems_methods, p.836]`. A slow trend filter avoids forcing a
high-noise equity/commodity ETF into countertrend exposure `[trading_systems_methods,
p.13]`.

This is a Phase 2 daily swing test, not an intraday test. `xauusd` spot is not a
primary traded config because the cache does not provide reliable spot volume;
`GLD` is used as the gold ETF proxy. This conservative choice is recorded because
volume indicators require trustworthy volume fields.

## Configs

Exactly 4 configs, all signals lagged by one completed daily bar before returns
are earned `[advances_fin_ml, p.31-34]`:

| name | ticker | force_ema | z_window | entry_z | exit_z | trend_sma | max_hold |
|---|---:|---:|---:|---:|---:|---:|---:|
| `spy_fi2_z63_e1_x0_sma200_h10` | `SPY` | 2 | 63 | 1.0 | 0.0 | 200 | 10 |
| `qqq_fi2_z63_e1_x0_sma200_h10` | `QQQ` | 2 | 63 | 1.0 | 0.0 | 200 | 10 |
| `gld_fi2_z63_e1_x0_sma200_h10` | `GLD` | 2 | 63 | 1.0 | 0.0 | 200 | 10 |
| `gld_fi13_z126_e05_x0_sma200_h20` | `GLD` | 13 | 126 | 0.5 | 0.0 | 200 | 20 |

Rule: enter long when smoothed Force Index z-score is above `entry_z` and close is
above `SMA200`; stay long until Force Index z-score is below/equal `exit_z`, close
falls below `SMA200`, or `max_hold` completed bars elapse. While flat, hold `SHV`.

## Data And Window

- Required daily physical files: `SPY`, `QQQ`, `GLD`, `SHV`, `xauusd`.
- Intraday audit still required: inspect `data/tiingo/1hour/prices/` and
  `data/tiingo/15min/prices/` physical file counts; do not synthesize missing
  intraday data.
- Use each config's full aligned daily window after indicator warmup.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold on the exact aligned return dates.
- Gold context: report `xauusd` buy-and-hold when the selected config is `GLD`.
- Opportunity benchmark: `SPY` buy-and-hold on the same aligned return dates.

## Gates

- Economic CAGR vs same-asset buy-and-hold: strategy CAGR must be greater.
- Economic Sharpe vs same-asset buy-and-hold: strategy Sharpe should be greater.
- IS MCPT with 200 permutations, pass threshold `p <= 0.01` `[testing_tuning,
  p.318-320]`.
- WF MCPT with 100 permutations, pass threshold `p <= 0.05` `[testing_tuning,
  p.318-320]`.
- PBO `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF: at least 8 windows and at least 6 positive windows `[testing_tuning,
  p.148-150]`.
- OOS last 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean-daily CI low greater than zero `[testing_tuning,
  p.246-247]`.
- Cross-lib/vector parity within 3pp CAGR `[advances_fin_ml, p.31-34]`.

## Kill Rules

- CAGR <= same-asset buy-and-hold => `fail`; no `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner`.
- Missing required daily files => `data_blocked` before tests.
- Missing volume for a configured asset => `data_blocked` for the family rather
  than substituting another volume proxy after pre-registration.
- Any PBO/DSR/MCPT failure blocks `strict_winner`; do not locally tune Force Index
  EMA length, z-window, z-threshold or hold length after failure.

## Trial Accounting

- `cumulative_n_trials` before: 172.
- New strategy configs: 4.
- `cumulative_n_trials` after if data are available: 176.
