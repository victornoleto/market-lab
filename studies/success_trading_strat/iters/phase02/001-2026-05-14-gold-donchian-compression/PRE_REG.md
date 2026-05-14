# PRE_REG — 001-2026-05-14-gold-donchian-compression

## Hypothesis

Gold can trend after range/volatility compression. Test a daily Donchian breakout
entry on `GLD` and `xauusd`, gated by low realized volatility, then hold until a
short Donchian exit. Donchian/Turtle breakout lengths are published but curve-fit
risky, so this iteration uses only two conventional breakout horizons and treats
PBO/DSR/MCPT as hard controls `[trading_systems_methods, p.353]`,
`[trading_systems_methods, p.481]`, `[advances_fin_ml, p.208-211]`,
`[testing_tuning, p.318-320]`.

Phase 2 intraday audit rule: `data/tiingo/1hour/prices/` is physically empty, so
`1h` gold/XAUUSD is marked blocked for this iteration. Manifest entries alone are
not sufficient `[testing_tuning, p.327-335]`.

## Data And Window

- Physical files to audit before testing:
- `data/tiingo/daily/prices/GLD.parquet`
- `data/tiingo/daily/prices/xauusd.parquet`
- `data/tiingo/daily/prices/SHV.parquet`
- `data/tiingo/daily/prices/SPY.parquet`
- Intraday audit paths:
- `data/tiingo/1hour/prices/GLD.parquet`
- `data/tiingo/1hour/prices/xauusd.parquet`
- Expected test window: common daily overlap after warmup, no manual date trimming
  after results `[trading_systems_methods, p.941]`.
- Timezone/session audit: report index timezone and bar timestamp convention from
  parquet index. Daily data are expected to be midnight timestamps.

## Configs

All signals use adjusted close if present. Entry uses yesterday's available
close-only information and strategy returns are lagged one bar. Flat sleeve is
`SHV` for ETF/cash opportunity cost. Parameters are limited to breakout lookback,
exit lookback and volatility-compression percentile to preserve parsimony
`[trading_systems_methods, p.939]`.

| config | asset | breakout_lookback | exit_lookback | rv_lookback | rv_percentile |
|---|---|---:|---:|---:|---:|
| `gld_dc55_rv20_p40` | `GLD` | 55 | 20 | 20 | 0.40 |
| `gld_dc100_rv20_p30` | `GLD` | 100 | 20 | 20 | 0.30 |
| `xau_dc55_rv20_p40` | `xauusd` | 55 | 20 | 20 | 0.40 |
| `xau_dc100_rv20_p30` | `xauusd` | 100 | 20 | 20 | 0.30 |

## Benchmark

- Primary benchmark: same-asset buy-and-hold over aligned window.
- Context benchmark: `SPY` buy-and-hold over aligned window.
- Economic screen: best config must beat same-asset buy-and-hold Sharpe to be more
  than a defensive timing artifact; CAGR/MDD are warning tiers, not hard gates.

## Gates Planned

- IS MCPT: 200 permutations, pass if `p <= 0.01` for strict winner; failure blocks
  strict winner `[testing_tuning, p.318-320]`.
- WF MCPT: 100 permutations, rolling 3y train / 1y test / 1y step, pass if
  `p <= 0.05` `[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`.
- PBO: CSCV over 4 configs, 10 blocks, pass if `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: best config with cumulative trials after this iteration (`104`), pass if
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- WF windows: same rolling 3y/1y scheme, require at least 6 positive windows when
  at least 8 windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% of aligned observations positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 daily observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of mean daily returns > 0 via stationary/bootstrap-like
  resampling `[testing_tuning, p.246-247]`.
- Cross-lib: independent vector formula vs stateful loop CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If physical daily files are absent or unreadable, stop as `data_blocked`.
- If `1h` files are absent, do not synthesize intraday bars; proceed only with the
  pre-registered daily version and record intraday as blocked.
- Do not add replacement assets or new parameters after seeing results.
- Any PBO/DSR/MCPT failure blocks `strict_winner`.
- No deploy implication; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials_before = 100`
- `n_trials = 4`
- `cumulative_n_trials_after = 104`
