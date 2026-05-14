# PRE_REG — 028-2026-05-14-cmo-momentum-continuation

## Hypothesis

Test a daily Chande Momentum Oscillator continuation rule, not a pullback or exhaustion rule: hold the asset only when `CMO(20) >= 50` and price is above `SMA200`; exit when `CMO(20) <= 0` or after 20 bars. CMO is a bounded up/down momentum oscillator `[trading_systems_methods, p.388]`; the slow moving-average regime filter is a simple trend definition `[trading_systems_methods, p.284]`. All signals are shifted one completed daily bar before returns are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

This is a return-seeking daily swing hypothesis. It is not pre-registered as hedge/cash-parking, so lower drawdown cannot compensate for lower compound return `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Configs

Exactly 4 configs:

- `spy_cmo20_e50_x0_sma200_h20`: `SPY`, `CMO(20) >= 50`, exit `CMO <= 0`, `SMA200`, max hold 20 bars.
- `qqq_cmo20_e50_x0_sma200_h20`: `QQQ`, same rule.
- `gld_cmo20_e50_x0_sma200_h20`: `GLD`, same rule.
- `xau_cmo20_e50_x0_sma200_h20`: `xauusd`, same rule.

No tuning inside this iteration. If the family fails, do not locally tune CMO length, entry/exit thresholds, SMA length, or hold length `[testing_tuning, p.327-335]`.

## Data And Window

Data source: local Tiingo daily parquet cache under `data/tiingo/daily/prices/` for `SPY`, `QQQ`, `GLD`, `SHV` and `xauusd`.

Before testing, the runner must audit physical files, date range, timezone, columns and missing business-day rate. `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` are audited as blocking context only; no intraday data may be synthesized from daily bars.

## Benchmarks

Primary benchmark: same-asset buy-and-hold on the aligned post-warmup strategy window.

Opportunity benchmark: `SPY` buy-and-hold on the same aligned window.

Gold context benchmarks: `GLD` and `xauusd` buy-and-hold on the same aligned window when relevant.

## Kill Rules

- If any required daily physical file is missing or lacks required close data, close `data_blocked` with `n_trials=0`.
- If strategy CAGR is `<=` same-asset buy-and-hold CAGR, close `fail` and do not assign `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.
- If PBO `>= 0.5` or DSR `p >= 0.05`, close non-winner regardless of economics `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- If IS MCPT or WF MCPT fails, close non-`strict_winner`; MCPT is an additional gate, not a substitute `[testing_tuning, p.318-320]`.

## Planned Gates

- Same-asset CAGR and Sharpe vs buy-and-hold.
- IS MCPT with 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO with 10 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trials after this iteration, pass `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward windows: at least 8 windows and at least 6 positive `[testing_tuning, p.148-150]`.
- Single-block OOS positive, latest 63d FWD positive, bootstrap 99.9% mean-daily CI low > 0, cross-lib/vector parity within 3pp CAGR.

## Trial Accounting

- `cumulative_n_trials_before = 208`
- `n_trials = 4`
- `cumulative_n_trials_after = 212`
