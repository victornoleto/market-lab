# PRE_REG — 013-2026-05-14-gold-relative-strength

## Hypothesis

Daily gold exposure may be more efficient when gold has positive own momentum and
outperforms equities on a rolling relative-strength basis. The rule holds `GLD` or
`xauusd` only when the asset is above a long relative-strength average versus
`SPY` and its own trailing return is positive; otherwise it holds `SHV`.
Relative-strength/intermarket filters are a classical regime tool
`[trading_systems_methods, p.542-544]`, `[trading_systems_methods, p.939]`, and
trend/momentum should be lagged to avoid lookahead `[stocks_on_the_move, p.76-77]`.

## Data And Window

- Daily physical files required before testing: `GLD`, `xauusd`, `SPY`, `SHV`.
- Audit physical intraday cache before any short-swing claim: `data/tiingo/1hour/prices/`
  and `data/tiingo/15min/prices/`. Manifest-only availability is insufficient.
- Use each config's aligned post-warmup window only.
- No 1h/15m synthesis from daily data.

## Exact Configs

1. `gld_rs100_m63`: `GLD`, relative-strength SMA 100, own momentum 63d.
2. `gld_rs200_m126`: `GLD`, relative-strength SMA 200, own momentum 126d.
3. `xau_rs100_m63`: `xauusd`, relative-strength SMA 100, own momentum 63d.
4. `xau_rs200_m126`: `xauusd`, relative-strength SMA 200, own momentum 126d.

Signals are shifted one completed daily bar before returns are earned
`[advances_fin_ml, p.31-34]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold (`GLD` or `xauusd`) on the same
  aligned window.
- Opportunity-cost benchmark: `SPY` buy-and-hold on the same aligned window.

## Kill Rules

- CAGR <= same-asset buy-and-hold CAGR => `fail`, with no `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner` promotion.
- Any PBO >= 0.5 or DSR p >= 0.05 blocks strict promotion
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- IS MCPT p > 0.01 or WF MCPT p > 0.05 blocks strict promotion
  `[testing_tuning, p.318-320]`.
- WF requires at least 8 windows and at least 6 positive windows
  `[testing_tuning, p.148-150]`.
- Bootstrap 99.9% CI low must be positive; cross-lib/vector parity must stay
  within +/-3pp CAGR `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## Planned Gates

- Same-asset CAGR and Sharpe comparison.
- IS MCPT, 200 reps.
- WF MCPT, 100 reps.
- PBO with 10 blocks across the 4 configs.
- DSR using cumulative trials after this iteration.
- WF windows, OOS final 20%, latest 63d FWD, bootstrap and cross-lib parity.

## Trial Accounting

- `cumulative_n_trials` before: 148.
- New strategy configs: 4.
- `cumulative_n_trials` after planned run: 152.
