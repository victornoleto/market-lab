# LOOP_PROTOCOL — success_trading_strat

This protocol lets `loop.sh` run repeated clean OpenCode/GPT-5.5 sessions. Each
session performs exactly one iteration and stops.

## Required Reads

At the start of every iteration, read in this order:

1. `CLAUDE.md`
2. `docs/PUBLIC_SUMMARY.md`
3. `docs/CURRENT_STATE.md`
4. `docs/investment-mandate.md`
5. `studies/success_trading_strat/MEMORY.md`
6. `studies/success_trading_strat/SPEC.md`
7. `studies/success_trading_strat/LOOP_PROTOCOL.md`
8. `studies/success_trading_strat/PHASE2_INTRADAY_SWING_SPEC.md` when running Phase 2
9. `studies/success_trading_strat/PHASE3_BH_BEATER_SPEC.md` when running Phase 3
10. Latest `studies/success_trading_strat/iters/<phase>/*/SUMMARY.md`, if any
11. One relevant book summary for the hypothesis

## Iteration Artifacts

Each iteration writes under:

`studies/success_trading_strat/iters/<phase>/NNN-YYYY-MM-DD-<slug>/`

For Phase 2, use `<phase> = phase02`. For Phase 3, use `<phase> = phase03`.
Phase 1 historical artifacts live under `studies/success_trading_strat/iters/phase01/`.

Required files:

- `PRE_REG.md` before testing;
- `RESULTS.json` after testing;
- `SUMMARY.md` with verdict and lessons;
- local scripts/tables/plots as needed.

## Pre-Registration

`PRE_REG.md` must include:

- hypothesis and citations;
- data sources and date ranges;
- exact configs before running;
- benchmark comparison target;
- gates to compute, including IS MCPT and WF MCPT when feasible;
- kill rules for the iteration;
- `cumulative_n_trials` before and after.

No pre-registration means the result cannot be promotional.

## Scope Rules

- One family per iteration.
- Prefer 1-6 configs.
- No large grids until MCPT/WF-MCPT infrastructure is proven.
- New code specific to one iteration stays inside the iteration folder.
- Reusable helpers may live in `studies/success_trading_strat/scripts/`.
- Do not modify `docs/investment-mandate.md`.
- Do not commit or push.
- A `winner` does not end the study by default. The following iteration should
  either stress/optimize that family with explicit new trial accounting or pivot
  to a different mechanism if the result looks fragile `[testing_tuning, p.327-335]`.
- Phase 2 should follow `PHASE2_INTRADAY_SWING_SPEC.md`: prioritize gold/XAUUSD,
  short-swing 1h/daily hybrids and daily swing systems; audit physical 15m/1h
  data files before any intraday test.
- Phase 2 economic floor: CAGR must beat same-asset buy-and-hold on the aligned
  window before any `candidate_watchlist`, `paper_trade_candidate` or
  `strict_winner` label. Drawdown reduction alone is insufficient unless the
  iteration pre-registers a hedge/cash-parking mandate.
- Phase 3 should follow `PHASE3_BH_BEATER_SPEC.md`: only test mechanisms with a
  plausible buy-and-hold beating return engine, such as controlled leverage,
  high-beta rotation, crash-rearmed exposure or explicitly modeled gross-exposure
  long/short rules.
- Phase 3 economic floor: CAGR and terminal wealth must both beat the
  pre-registered primary buy-and-hold benchmark on aligned dates before any label
  above `fail` is allowed.

## Verdict Labels

- `winner`: beats benchmark and passes all gates.
- `strict_winner`: synonym for all original hard gates passing.
- `candidate_watchlist`: economically useful but not a strict winner; eligible
  only for human review or paper trading, never live deployment.
- `paper_trade_candidate`: human-selected forward-only paper trade candidate.
- `promising_not_validated`: economically interesting but at least one hard gate
  missing or failed.
- `fail`: tested and did not beat benchmark or failed key gates.
- `infrastructure_only`: audit/scaffold result, no strategy claim.
- `data_blocked`: hypothesis could not be tested honestly with available data.

## MEMORY Update

At the end of every iteration, update `MEMORY.md`:

- increment `total_iterations`;
- increment `cumulative_n_trials` by tested strategy configs;
- update latest fields;
- append a short note under `Hypotheses Tested`;
- add dead-end families when appropriate.

## Mandate Guard

This study cannot authorize live deployment. PBO/DSR remain hard controls, and
MCPT is an additional anti-overfit screen, not a replacement
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
