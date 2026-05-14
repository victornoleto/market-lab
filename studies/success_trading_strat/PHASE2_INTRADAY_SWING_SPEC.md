# PHASE2_INTRADAY_SWING_SPEC — 15m/1h/1d

## Purpose

Reopen `success_trading_strat` only as a new phase focused on liquid swing-trading
systems between 15m, 1h and 1d. Phase 1 proved that strict all-gate winners are
rare; Phase 2 keeps the strict validation record but adds pragmatic triage so good
strategies can be paper-traded instead of discarded automatically
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

## Classification

- `strict_winner`: passes all original hard gates: IS MCPT, WF MCPT, PBO, DSR,
  WF, OOS, FWD, bootstrap and cross-lib.
- `candidate_watchlist`: economically useful and robust enough for review, but
  missing/failing at least one strict research gate. No live deployment.
- `paper_trade_candidate`: selected by a human from the watchlist for forward
  paper trading only; no capital allocation.
- `reject`: weak economics or failed core robustness.
- `data_blocked`: required data unavailable or stale.

This classification does not change `docs/investment-mandate.md`; capital remains
100% Plano C until an explicit human mandate override.

## Economic Floor

Any long-only or partially defensive strategy must beat the relevant buy-and-hold
benchmark in CAGR over the same aligned window before it can be considered
interesting. A lower-CAGR strategy may reduce drawdown, but it is not acceptable
for `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` unless the
iteration pre-registers an explicitly different mandate such as hedging or cash
parking. This prevents promoting low-return filters that merely de-risk a strong
asset while sacrificing the main return engine `[systematic_trading, p.40]`,
`[testing_tuning, p.327-335]`.

Minimum economic gates for Phase 2:

- Strategy CAGR > same-asset buy-and-hold CAGR on the same dates.
- Strategy Sharpe > same-asset buy-and-hold Sharpe, unless the hypothesis is
  explicitly return-maximizing and pre-registers a different primary objective.
- Strategy MDD should improve versus same-asset buy-and-hold, but MDD improvement
  alone is never enough if CAGR fails.
- For cross-asset or cash-defensive systems, also report SPY buy-and-hold as an
  opportunity-cost benchmark.

## Tracks

### Track A — Daily Swing

- Timeframe: `1d` bars.
- Expected holding period: 1-12 weeks.
- Assets: `SPY`, `QQQ`, `GLD`, `XAUUSD`, liquid ETFs, selected crypto only if data
  freshness is explicitly audited.
- Purpose: slower swing systems with lower turnover and enough history for 5-15y
  rolling diagnostics.

### Track B — Short Swing

- Timeframes: signal on `1h` when available, optional daily regime filter.
- Expected holding period: intraday to 1-7 trading days.
- Assets: start with `XAUUSD`/`GLD`, `SPY`/`QQQ`, and only assets with confirmed
  intraday cache integrity.
- Purpose: capture shorter volatility/momentum/mean-reversion effects that daily
  bars may average away.

### Track C — Gold/XAUUSD Dedicated

- Timeframes: first `1d`, then `1h` if cache files exist and are audited.
- Assets: `XAUUSD` spot proxy and `GLD` ETF proxy.
- Initial families: trend breakout, volatility compression breakout, session/range
  expansion, mean-reversion after exhaustion, and daily-regime + 1h-entry hybrids.
- Benchmark: same-asset buy-and-hold plus `SPY` buy-and-hold for opportunity-cost
  context.

## Data Rules

- Before any 15m/1h test, run a cache audit that confirms physical parquet files,
  timestamp range, timezone/session convention, missing-bar rate and bid/ask/proxy
  limitations.
- Manifest entries alone are insufficient; Phase 1 found `1hour` manifest entries
  for `GLD`/`xauusd` but no files under `data/tiingo/1hour/prices/`.
- If 15m data are not locally available, do not synthesize them from 1h/daily data.
- If 1h data are unavailable, test the same mechanism on `1d` and mark intraday as
  `data_blocked`.

## Iteration Budget

- Next loop: 30 iterations.
- Suggested allocation: 10 gold/XAUUSD, 10 short-swing 1h/daily-hybrid, 10 daily
  swing or best-watchlist stress tests.
- Each iteration still pre-registers one family and preferably 1-6 configs.
- Every config increments `cumulative_n_trials` for DSR accounting.

## Gate Policy

- Strict winners still require all original gates.
- `candidate_watchlist` requires the Economic Floor above, no lookahead, clear
  benchmark comparison, and at least a majority of available robustness gates.
- DSR/PBO/MCPT failures must be recorded, not hidden; they can block
  `strict_winner` while still allowing paper-trading watchlist status.
- Any paper-trade promotion requires a separate forward-only plan with no parameter
  changes during the paper window.
