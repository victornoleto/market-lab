# PRE_REG — 020 turn-of-month seasonality

## Hypothesis

Equity index returns may cluster around the turn of the month because of calendar-linked flows and recurring institutional behavior. This iteration tests a parsimonious turn-of-month exposure rule rather than tuning another local price, VIX, credit, carry or Ehlers overlay. Calendar effects are a documented classical strategy class, and the specific month-end rule of buying the last/second-to-last trading day and exiting around the fourth trading day of the next month is cited by Kaufman `[trading_systems_methods, p.479-481]`, `[trading_systems_methods, p.422]`. Because seasonal rules are vulnerable to data mining, promotion remains blocked unless MCPT, PBO and DSR pass `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

- Source: local Tiingo daily adjusted prices in `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV`.
- Window: common adjusted-close history from `2010-01-01` through the latest common date.
- Execution lag: signal calendar membership is known before the close, but returns are still applied with a one-bar conservative lag via shifted exposure.
- Data freshness kill threshold: common data end must be at least `2026-03-31`.

## Exact Configs

Four configs, all long-only and flat-to-`SHV` outside the calendar window:

1. `spy_tom_l1_f4`: hold `SPY` from the last 1 trading day of each month through the first 4 trading days of the next month.
2. `spy_tom_l2_f4`: hold `SPY` from the last 2 trading days of each month through the first 4 trading days of the next month.
3. `qqq_tom_l1_f4`: hold `QQQ` from the last 1 trading day of each month through the first 4 trading days of the next month.
4. `qqq_tom_l2_f4`: hold `QQQ` from the last 2 trading days of each month through the first 4 trading days of the next month.

No additional windows, assets or thresholds may be added after seeing results.

## Benchmark

- `SPY` configs compare against `SPY` buy-and-hold over the same aligned dates.
- `QQQ` configs compare against `QQQ` buy-and-hold over the same aligned dates.
- Winner requires higher Sharpe than the same-asset buy-and-hold benchmark; CAGR/MDD are reported as tiers/warnings, not hard gates per mandate.

## Planned Gates

- Data not stale: latest common date >= `2026-03-31`.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT on best config: 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT on best config: 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO across the 4 configs with 8 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR on best config with cumulative `n_trials=68`, pass `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: 4y train, 1y test, 1y step; require at least 6 positive windows if 8+ windows are available, otherwise all windows positive `[testing_tuning, p.148-150]`.
- OOS: final 20% return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean-daily-return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy-style implementation CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required price files are missing or stale, close `data_blocked` with `n_trials=0`.
- If the best config fails any hard gate, status is `fail`; no winner claim.
- Do not tune the calendar window, add holidays, add leverage or change benchmark after results.
- If this calendar family fails MCPT/PBO/DSR, add it to dead ends and do not locally tune calendar offsets without a new, externally motivated hypothesis `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 64.
- New tested strategy configs: 4.
- `cumulative_n_trials` after if data loads: 68.
