# PRE_REG - 027 commodity macro filter

## Hypothesis

Commodity strength can act as a simple macro regime filter for equity/bond
allocation: broad commodity momentum may identify inflationary or risk-on/risk-off
conditions that change whether `SPY` or `TLT` should be held. This uses a distinct
intermarket information source rather than tuning prior sector, breadth, volume,
VIX, trend or calendar families. The design is intentionally sparse because robust
systems should have four or fewer parameters and a sound premise before testing
`[trading_systems_methods, p.939]`, `[trading_systems_methods, p.1109]`.

The lookbacks are natural quarterly and semiannual horizons, not optimized after
validation feedback `[trading_systems_methods, p.285]`. Idle/off capital holds
`SHV` as a cash proxy. Signals are lagged one bar to avoid same-close lookahead
`[advances_fin_ml, p.196-202]`.

## Data And Window

- Local Tiingo adjusted daily close parquet files under `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `TLT`, `SHV`, `DBC`, `GLD`.
- Window: common daily history from `2010-01-01` through latest common date.
- Data freshness block: fail as `data_blocked` if latest common date is before
  `2026-03-31` or any required file is unavailable.

## Exact Configs

1. `spy_dbc_m63`: hold `SPY` when lagged 63d `DBC` momentum is positive, else `SHV`.
2. `spy_dbc_m126`: hold `SPY` when lagged 126d `DBC` momentum is positive, else `SHV`.
3. `tlt_dbc_m63_inv`: hold `TLT` when lagged 63d `DBC` momentum is negative, else `SHV`.
4. `tlt_gld_m126_inv`: hold `TLT` when lagged 126d `GLD` momentum is negative, else `SHV`.

These are four fixed trials. No thresholds other than zero momentum, no local grid,
and no post-result substitutions.

## Benchmark

- `SPY` configs compare against same-window `SPY` buy-and-hold.
- `TLT` configs compare against same-window `TLT` buy-and-hold.
- Economic pass requires strategy Sharpe > same-asset benchmark Sharpe. CAGR and
  MDD are reported but are not hard gates per mandate.

## Planned Gates

- IS MCPT: 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: 8 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: 4y train / 1y test / 1y step; require at least 6 positive windows
  when 8+ windows are available `[testing_tuning, p.148-150]`.
- OOS: final 20% return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy path CAGR within +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required commodity/ETF data are missing or stale, stop as `data_blocked` with
  `n_trials=0`; do not substitute different commodity proxies after preregistration.
- If any hard gate fails, verdict is `fail`; do not tune commodity lookbacks,
  thresholds or proxy tickers locally `[testing_tuning, p.327-335]`.
- No deploy claim; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials_before = 92`.
- `n_trials = 4` if data are available.
- `cumulative_n_trials_after = 96` if tested; unchanged if data-blocked.
