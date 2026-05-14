# PRE_REG — 027-2026-05-14-williams-r-exhaustion

## Hypothesis

Test a daily Williams %R exhaustion-reversal family on `SPY`, `QQQ`, `GLD` and
`xauusd`: enter after an extreme close-location oversold reading inside a broad
uptrend, then exit on mean reversion toward the range midpoint or after a short
time stop. Williams %R is a close-location oscillator for identifying overbought
and oversold positions inside the recent high-low range `[trading_systems_methods,
p.385-386]`; the slow `SMA200` trend filter prevents buying exhaustion against a
dominant downtrend `[trading_systems_methods, p.172]`. One completed daily bar of
signal lag is mandatory to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Data And Window

- Physical files to audit before testing: `data/tiingo/daily/prices/{SPY,QQQ,GLD,SHV,xauusd}.parquet`.
- Required columns: adjusted/close plus OHLC for range-location calculations.
- Intraday audit still required by Phase 2: report physical file counts for
  `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/`; no intraday bars
  will be synthesized if absent.
- Window: maximal common daily window after warmup per configured asset and `SHV`.

## Exact Configs

1. `spy_wr14_os90_x50_sma200_h10`: `SPY`, Williams %R lookback 14, enter `<= -90`, exit `>= -50`, `SMA200`, max hold 10 bars.
2. `qqq_wr14_os90_x50_sma200_h10`: `QQQ`, same parameters.
3. `gld_wr14_os90_x50_sma200_h10`: `GLD`, same parameters.
4. `xau_wr14_os90_x50_sma200_h10`: `xauusd`, same parameters.

No parameter tuning inside this iteration. If the family fails, do not tune
Williams %R length, entry/exit thresholds, hold length or trend filter locally
without a new mechanism `[testing_tuning, p.327-335]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold over the exact aligned return window.
- Opportunity-cost benchmark: `SPY` buy-and-hold over the same aligned window.
- Gold context: report `GLD` and `xauusd` buy-and-hold when the best config is not
  gold.

## Kill Rules

- Phase 2 hard economic kill: if best strategy CAGR `<=` same-asset buy-and-hold
  CAGR, close `fail`; it cannot receive `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner`.
- PBO `>= 0.5` hard-blocks strict promotion `[advances_fin_ml, p.208-211]`.
- DSR `p >= 0.05` hard-blocks strict promotion using cumulative trials after this
  iteration `[advances_fin_ml, p.222-223]`.
- IS MCPT `p > 0.01` and WF MCPT `p > 0.05` block strict promotion
  `[testing_tuning, p.318-320]`.
- WF requires at least 8 windows and at least 6 positive windows
  `[testing_tuning, p.148-150]`.
- OOS, latest 63d FWD, bootstrap 99.9% mean-daily CI low and cross-lib parity must
  pass for strict promotion `[advances_fin_ml, p.196-202]`.

## Trial Accounting

- `cumulative_n_trials` before: 204.
- New strategy/config trials planned: 4.
- `cumulative_n_trials` after if data are available: 208.
- MCPT repetitions are validation effort and do not increment strategy trial count.
