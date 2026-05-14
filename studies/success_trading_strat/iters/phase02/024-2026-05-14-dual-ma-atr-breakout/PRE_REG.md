# PRE_REG — 024-2026-05-14-dual-ma-atr-breakout

## Hypothesis

Test a daily dual moving-average ATR breakout: enter long when the close is above both a short and long moving average plus one lagged ATR, exit when either corresponding lower band is violated. The rule is a sparse trend-continuation mechanism based on Kaufman's Donchian-style MA+ATR breakout template `[trading_systems_methods, p.352-353]`; ATR/true range is the volatility scale `[trading_systems_methods, p.107]`. Signals are shifted one completed daily bar before returns are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Configs

Exactly 4 configs, no local tuning after seeing results:

- `spy_ma5_20_atr20_k1`: `SPY`, short MA 5, long MA 20, ATR 20, multiplier 1.0.
- `qqq_ma5_20_atr20_k1`: `QQQ`, short MA 5, long MA 20, ATR 20, multiplier 1.0.
- `gld_ma5_20_atr20_k1`: `GLD`, short MA 5, long MA 20, ATR 20, multiplier 1.0.
- `xau_ma5_20_atr20_k1`: `xauusd`, short MA 5, long MA 20, ATR 20, multiplier 1.0.

## Data And Window

- Daily Tiingo cache files: `SPY`, `QQQ`, `GLD`, `xauusd`, `SHV`.
- Audit must record physical file existence, first/last timestamp, timezone, missing business-day rate and OHLC availability.
- Intraday audit must record physical `1hour/prices` and `15min/prices` availability. Manifest-only entries are insufficient; if files remain unavailable, this iteration stays daily only.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold over the aligned post-warmup strategy window.
- Opportunity benchmark: `SPY` buy-and-hold over the aligned window.
- For `GLD`, also report `xauusd` spot context; for `xauusd`, report `GLD` ETF context when aligned.

## Gates Planned

- Economic CAGR vs same-asset buy-and-hold: hard Phase 2 kill rule.
- Same-asset Sharpe comparison.
- IS MCPT on the fixed best rule, 200 reps, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT, 100 reps, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the 4 configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward at least 8 windows and at least 6 positive `[testing_tuning, p.148-150]`.
- Single-block OOS positive and latest 63d FWD stress positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean-daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity within 3pp CAGR `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required daily OHLC file is missing, close `data_blocked` with `n_trials=0`.
- If strategy CAGR <= same-asset buy-and-hold CAGR, close `fail`; do not assign `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.
- If strict gates fail, close `fail` unless the Phase 2 economic floor and most robustness gates pass; DSR/PBO failures still block `strict_winner`.
- Do not tune MA lengths, ATR length or multiplier inside this iteration after seeing results `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 192.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if tested: 196.
