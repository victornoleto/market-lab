# PHASE3_BH_BEATER_SPEC - Buy-And-Hold Beater

## Purpose

Phase 3 exists because Phase 2 answered a narrow question clearly: 30 daily
long/flat swing filters did not beat same-asset buy-and-hold in CAGR. Several
filters reduced drawdown or improved Sharpe, but they gave up too much exposure
to strong assets, especially `xauusd`. Phase 3 therefore changes the research
question from "can a defensive timing filter improve the ride?" to "can a
pre-registered mechanism beat buy-and-hold in terminal wealth and CAGR after
honest validation?" `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

This is research only. It does not authorize live deployment and does not modify
`docs/investment-mandate.md`; capital remains 100% Plano C until an explicit
human mandate override.

## Lessons From Phase 2

- Daily long/flat filters usually reduce exposure. In strong trends, reduced
  exposure loses CAGR even when MDD improves.
- Gold/XAUUSD daily timing was a poor target for generic filters because the
  aligned 2020-2026 `xauusd` buy-and-hold benchmark had high drift.
- MDD improvement alone is not useful for this study. A strategy that cannot beat
  buy-and-hold in CAGR cannot become `candidate_watchlist`, `paper_trade_candidate`
  or `strict_winner`.
- Intraday claims remain blocked until physical `1h` or `15m` parquet files are
  present and audited. Manifest entries alone are insufficient.
- The strongest Phase 1/2 near-misses had either high-beta exposure, crypto/LETF
  participation or VIX/crash-management structure. Phase 3 should start there,
  not with more daily oscillators.

## Core Hypothesis

To beat buy-and-hold, Phase 3 must test mechanisms that can increase upside or
select a stronger return engine, not just step aside into cash. Acceptable Phase
3 mechanisms are:

- controlled leverage or LETF exposure with explicit crash/path-dependency risk
  controls `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`;
- high-beta relative rotation that stays invested in the strongest eligible asset
  instead of defaulting to `SHV` `[stocks_on_the_move, p.66-67]`,
  `[trading_systems_methods, p.542-544]`;
- crash-rearmed exposure that uses drawdowns to re-risk rather than only to de-risk
  `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`;
- long/short or market-neutral rules only if gross exposure and financing are
  explicitly modeled, because unlevered market-neutral returns are unlikely to beat
  equity buy-and-hold in CAGR `[systematic_trading, p.137-148]`.

## Non-Goals

- Do not spend Phase 3 on another sequence of daily long/flat oscillators, channels
  or low-exposure filters unless they are embedded in an upside-increasing
  mechanism.
- Do not optimize parameters locally after a family fails. A retest requires a new
  mechanism, not a nearby lookback/threshold tweak `[testing_tuning, p.327-335]`.
- Do not treat low MDD, high Sharpe or high DSR as sufficient if CAGR and terminal
  wealth lose to the pre-registered buy-and-hold benchmark.
- Do not synthesize intraday tests from daily data.

## Classification

- `strict_winner`: beats the pre-registered buy-and-hold benchmark in CAGR and
  terminal wealth, and passes all strict validation gates.
- `economic_beater_not_validated`: beats buy-and-hold in CAGR and terminal wealth,
  but fails at least one hard validation gate. Research-only, no paper/live claim.
- `candidate_watchlist`: beats buy-and-hold in CAGR and terminal wealth, has no
  fatal data/lookahead caveat and passes a majority of robustness gates, but is
  not a strict winner. Human review only.
- `paper_trade_candidate`: human-selected forward-only candidate from the watchlist;
  no parameter changes during the paper window.
- `fail`: does not beat buy-and-hold economically, or fails core validation badly.
- `data_blocked`: required data are missing, stale or physically absent.

No label above `fail` is allowed unless the strategy beats the relevant
buy-and-hold benchmark in both CAGR and terminal wealth on the exact aligned dates.

## Economic Gates

Every iteration must pre-register the benchmark hierarchy before testing.

Hard economic gates:

- Strategy CAGR > primary buy-and-hold CAGR on the same aligned dates.
- Strategy terminal wealth > primary buy-and-hold terminal wealth on the same
  aligned dates.
- Strategy CAGR > SPY buy-and-hold CAGR for any strategy that is not explicitly
  benchmarked to a higher-beta asset.
- Strategy MDD may be worse than buy-and-hold only if pre-registered and justified;
  any MDD worse than 1.5x the primary benchmark's MDD blocks `strict_winner` unless
  CAGR excess is extreme and a human explicitly reviews it.
- Report Sharpe, Sortino, Calmar and exposure time, but do not use them to override
  the CAGR/terminal-wealth gates.

Benchmark mapping:

- Nasdaq LETF or Nasdaq high-beta systems: primary `QQQ` buy-and-hold; context
  `QLD`/`TQQQ` buy-and-hold when those are traded.
- S&P LETF systems: primary `SPY` buy-and-hold; context `SSO`/`UPRO` buy-and-hold
  when those are traded.
- Semiconductor systems: primary `QQQ` plus equal-weight `SMH/SOXX` opportunity
  universe; context `SOXL`/`TECL` when traded.
- Crypto systems: primary `BTCUSD`, `ETHUSD` or equal-weight crypto buy-and-hold,
  matching the traded universe.
- Multi-asset rotation: primary `SPY` and equal-weight opportunity-universe
  buy-and-hold.
- Gold-only systems are deprioritized. If tested, primary is `xauusd` or `GLD`
  same-asset buy-and-hold plus `SPY` opportunity cost.

## Validation Gates

The existing gates remain hard controls for `strict_winner`:

- IS MCPT pass: preferred `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT pass: preferred `p <= 0.01`, acceptable `p <= 0.05` for shorter windows
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05`, using cumulative trial count `[advances_fin_ml, p.222-223]`.
- Walk-forward positives at or above the repo threshold.
- OOS positive.
- Latest FWD stress positive.
- Bootstrap 99.9% mean-return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity within +/-3pp CAGR where feasible `[advances_fin_ml,
  p.31-34]`.

`economic_beater_not_validated` may fail validation gates, but the failure must be
reported plainly and cannot be promoted to paper trading without a separate human
decision.

## Data Rules

- Before Phase 3 iteration 001, audit physical daily files for `SPY`, `QQQ`, `QLD`,
  `TQQQ`, `SSO`, `UPRO`, `SMH`, `SOXX`, `SOXL`, `TECL`, `XLK`, `IBIT`, `ETHA`,
  `BTCUSD`, `ETHUSD`, `GLD`, `TLT`, `IEF` and `SHV` where available.
- Record rows, first/last date, columns, timezone and missing-business-day rate in
  the iteration audit.
- If a required traded asset is missing, either close `data_blocked` or
  pre-register a smaller universe before testing. Do not substitute after seeing
  results.
- Intraday testing is disabled unless physical `data/tiingo/1hour/prices/*.parquet`
  or `data/tiingo/15min/prices/*.parquet` files exist and pass audit.
- ETF OHLC must be adjusted consistently with `adj_close / close` when OHLC-based
  rules are used `[advances_fin_ml, p.31-34]`.

## Iteration Budget

Phase 3 target: 30 iterations.

Suggested allocation:

- Iters 001-008: LETF and controlled leverage.
- Iters 009-016: high-beta relative rotation.
- Iters 017-022: crash-rearmed exposure.
- Iters 023-026: long/short or gross-exposure alpha tests.
- Iters 027-030: stress, consolidation and closure audit.

Each iteration should test one family with 1-6 pre-registered configs. Every config
increments `cumulative_n_trials` for DSR.

## Track A - LETF And Controlled Leverage

Purpose: use leverage as the return engine while controlling path dependency and
crash exposure.

Initial families:

- `QQQ` signal to `QLD`/`TQQQ` exposure with volatility targeting and crash filter.
- `SPY` signal to `SSO`/`UPRO` exposure with volatility targeting and crash filter.
- `SMH`/`SOXX` signal to `SOXL`/`TECL` exposure if data exist.
- LETF buy-and-hold plus dynamic de-risking only during extreme volatility.
- LETF volatility targeting with cap 1.0 of the LETF, not synthetic infinite
  leverage.

Required reporting:

- traded LETF B&H context;
- underlying ETF B&H primary benchmark;
- exposure time;
- annual turnover;
- max consecutive drawdown days;
- path-dependency caveat.

## Track B - High-Beta Relative Rotation

Purpose: beat B&H by owning the strongest return engine, not by going to cash.

Initial universes:

- Equity growth: `QQQ`, `SMH`, `SOXX`, `XLK`, `IGV`, `IYW` if available.
- LETF-light: `QLD`, `SSO`, `SMH`, `SOXX`, with `SHV` only as a rare risk-off asset.
- Crypto/equity: `BTCUSD`, `ETHUSD`, `QQQ`, `GLD`, with explicit data-window caveats.

Initial families:

- top-1 and top-2 dual momentum;
- volatility-adjusted momentum;
- Clenow adjusted-slope ranking;
- relative strength with absolute-momentum floor;
- inverse-vol weighted basket of top-ranked high-beta assets.

`SHV` allocation should be rare. If the best config spends too much time in cash and
loses to the opportunity universe, close `fail` rather than tuning.

## Track C - Crash-Rearmed Exposure

Purpose: remain exposed during normal bull markets and use large drawdowns as
re-risking opportunities.

Initial families:

- buy-and-hold core plus crash rearm after a fixed drawdown trigger;
- `QQQ` or `SPY` core with temporary `QLD`/`SSO` booster after crash recovery;
- volatility spike de-risk followed by scheduled re-risk;
- dynamic sizing that increases risk after large drawdowns and decreases risk as
  equity grows, preserving the mandate's dynamic sizing concept.

Hard rule: these systems must not become ordinary SMA200 long/flat filters. Their
purpose is to preserve or enhance upside after stress, not to sit in cash.

## Track D - Long/Short With Gross Exposure

Purpose: test alpha independent of market beta only when gross exposure and
financing are explicit.

Initial families:

- sector relative momentum: long winner, short loser;
- equity versus bond/commodity relative spread;
- high-beta pair residual momentum;
- beta-neutral residual trend with gross exposure target.

Required reporting:

- gross exposure;
- net exposure;
- financing/borrow proxy;
- turnover;
- beta to SPY and QQQ;
- long-only comparator.

Unlevered market-neutral systems should be closed early if their expected CAGR is
structurally below the buy-and-hold benchmark.

## Pre-Registration Template

Each Phase 3 `PRE_REG.md` must include:

- thesis: why this mechanism can beat buy-and-hold rather than merely reduce risk;
- exact benchmark hierarchy;
- exact configs and trial count;
- data audit and caveats;
- economic gates;
- validation gates;
- leverage/gross exposure assumptions if applicable;
- kill rules;
- cumulative trial count before and after.

## Stop Rules

- If the first 12 Phase 3 iterations produce zero economic beaters, stop testing
  defensive timing and restrict remaining iterations to LETF, rotation or crash
  rearm mechanisms.
- If 20 Phase 3 iterations produce zero economic beaters, run a closure audit unless
  there is a pre-registered reason to continue.
- If a family beats buy-and-hold economically but fails validation, record it as
  `economic_beater_not_validated` and either stress it in a new pre-registered
  iteration or pivot. Do not locally tune.
- If a family fails the economic gates, do not tune its nearby parameters.

## First Eight Recommended Iterations

1. `QQQ -> QLD/TQQQ` volatility-targeted exposure.
2. `SPY -> SSO/UPRO` volatility-targeted exposure.
3. `SMH/SOXX -> SOXL/TECL` semis LETF exposure if files exist.
4. Nasdaq crash-rearm rule using `QQQ` core and `QLD` booster.
5. S&P crash-rearm rule using `SPY` core and `SSO` booster.
6. High-beta top-1/top-2 momentum over `QQQ/SMH/SOXX/XLK`.
7. Crypto/equity rotation over confirmed `BTCUSD/ETHUSD/QQQ/GLD` data.
8. Drawdown-adaptive sizing on the strongest validated high-beta universe.

If any required data are missing, close the iteration as `data_blocked` or shrink
the universe before testing. Do not substitute after results are known.
