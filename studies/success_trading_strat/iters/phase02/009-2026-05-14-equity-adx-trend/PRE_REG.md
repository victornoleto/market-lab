# PRE_REG — 009-2026-05-14-equity-adx-trend

## Hypothesis

Daily `SPY`/`QQQ` trend continuation gated by Wilder Directional Movement may avoid
some range-bound equity noise: hold the asset only when lagged `+DI > -DI` and
lagged `ADX` is above a fixed trend-strength threshold; otherwise hold `SHV`.
Directional Movement/ADX is a classical trend-strength tool
`[trading_systems_methods, p.387]`. The small fixed-config test is required to
avoid post-hoc tuning and selection bias `[testing_tuning, p.143-144]`, while
PBO/DSR remain hard gates `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Data And Window

- Daily adjusted OHLC from local Tiingo cache:
  - `data/tiingo/daily/prices/SPY.parquet`
  - `data/tiingo/daily/prices/QQQ.parquet`
  - `data/tiingo/daily/prices/SHV.parquet`
- Physical intraday audit before the run:
  - inspect `data/tiingo/1hour/prices/` file count and target files;
  - inspect `data/tiingo/15min/prices/` existence and target files;
  - do not synthesize intraday bars if files are absent.
- Date window: full overlapping local daily history per asset after indicator
  warmup, no favorable sub-window selection.
- Timezone/session: report parquet index timezone in `audit.json`; daily bars are
  treated as completed-session bars and signals are shifted by one bar before
  returns are earned `[advances_fin_ml, p.31-34]`.

## Exact Configs

1. `spy_adx14_t20`: `SPY`, ADX length 14, threshold 20.
2. `spy_adx14_t25`: `SPY`, ADX length 14, threshold 25.
3. `qqq_adx14_t20`: `QQQ`, ADX length 14, threshold 20.
4. `qqq_adx14_t25`: `QQQ`, ADX length 14, threshold 25.

No local threshold, length, exit, or filter tuning after results.

## Benchmark

- Primary: same-asset buy-and-hold over the exact strategy return window.
- Context: `SPY` buy-and-hold over the same window.
- Economic pass for strict winner requires strategy Sharpe above same-asset
  buy-and-hold; CAGR/MDD are reported as tiers, not hard gates per mandate.

## Planned Gates

- IS MCPT: fixed-rule close-path permutation, 200 reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: rolling fixed-rule permutation, 100 reps, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 10-block PBO over the 4 pre-registered config returns, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: best returns with cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: 3y train / 1y test / 1y step; at least 8 windows and at least 6
  positive windows `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean-daily CI low above zero `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: independent vector return path within 3pp CAGR
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required daily physical file is absent, stop as `data_blocked` with
  `n_trials=0`.
- If intraday files are absent, continue only with daily bars and record Track B as
  blocked; do not synthesize 1h/15m data.
- If PBO or DSR fails, no winner regardless of economic metrics.
- If MCPT fails, no `strict_winner`; at most `candidate_watchlist` if economics and
  most other gates are unusually strong.
- Do not tune ADX length/thresholds or add local filters after seeing results.

## Trial Accounting

- `cumulative_n_trials` before: 132.
- New strategy configs: 4.
- `cumulative_n_trials` after if all configs run: 136.
