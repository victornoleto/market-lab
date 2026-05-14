# PRE_REG — 003-2026-05-14-gold-cci-breakout

## Hypothesis

Gold daily swing may respond better to a commodity-style trend impulse than to the
prior Donchian-compression or RSI-exhaustion variants. This iteration tests a
close-only Commodity Channel Index breakout on `GLD` and `xauusd`, holding `SHV`
when flat. CCI is a classical commodity oscillator measuring price deviation from
its average deviation `[trading_systems_methods, p.172]`; trend/impulse rules must
stay pre-registered and small because unconstrained optimization creates data-mining
bias `[trading_systems_methods, p.939]`, `[testing_tuning, p.327-335]`.

## Data And Window

- Physical daily files required before testing: `GLD`, `xauusd`, `SHV`, `SPY` under
  `data/tiingo/daily/prices/`.
- Physical intraday audit required but not used if absent: `data/tiingo/1hour/prices/`
  and `data/tiingo/15min/prices/`; manifest entries alone are insufficient.
- Use each asset's full available local daily range after indicator warmup and date
  alignment with `SHV`/`SPY`.
- Signals are shifted one bar before execution to avoid same-close lookahead
  `[advances_fin_ml, p.196-202]`.

## Exact Configs

Four configs, no local tuning after results:

| name | asset | CCI lookback | entry | exit | trend SMA |
|---|---|---:|---:|---:|---:|
| `gld_cci20_e100_x0_sma200` | `GLD` | 20 | `CCI > 100` | `CCI < 0` or close < SMA200 | 200 |
| `gld_cci40_e100_x0_sma200` | `GLD` | 40 | `CCI > 100` | `CCI < 0` or close < SMA200 | 200 |
| `xau_cci20_e100_x0_sma200` | `xauusd` | 20 | `CCI > 100` | `CCI < 0` or close < SMA200 | 200 |
| `xau_cci40_e100_x0_sma200` | `xauusd` | 40 | `CCI > 100` | `CCI < 0` or close < SMA200 | 200 |

CCI is computed on close-only prices so the fixed rule can be evaluated on MCPT
permuted price paths without fabricating high/low bars. This is a conservative
implementation choice recorded before testing `[testing_tuning, p.318-320]`.

## Benchmark

- Primary: same-asset buy-and-hold (`GLD` for `GLD`, `xauusd` for `xauusd`) over the
  aligned strategy window.
- Context: `SPY` buy-and-hold over the aligned strategy window.

## Planned Gates

- Economic Sharpe versus same-asset buy-and-hold.
- IS MCPT with 200 reps; pass only if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 reps; pass only if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the 4-config panel `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward windows: at least 8 windows and at least 6 positive
  `[testing_tuning, p.148-150]`.
- OOS final 20% total return positive `[advances_fin_ml, p.196-202]`.
- Latest 63-observation FWD stress positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% CI low for mean daily return > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: loop and vectorized CAGR delta <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required daily physical file is absent, stop as `data_blocked` and consume
  zero trials.
- If intraday files are absent, do not synthesize 1h/15m bars; continue only as a
  daily test and record the intraday block.
- If the family fails PBO, DSR, MCPT or benchmark Sharpe, do not tune CCI thresholds
  locally in this iteration.
- `candidate_watchlist` is not deploy; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 108.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 112.
