# LOOP_PROTOCOL — spy_beater_hunt_v2

This protocol lets `loop.sh` run repeated clean OpenCode/GPT-5.5 sessions. Each
session performs exactly one iteration and stops.

## Required Reads

At the start of every iteration, read in this order:

1. `CLAUDE.md`
2. `docs/PUBLIC_SUMMARY.md`
3. `docs/CURRENT_STATE.md`
4. `docs/investment-mandate.md`
5. `studies/spy_beater_hunt_v2/MEMORY.md`
6. `studies/spy_beater_hunt_v2/SPEC.md`
7. `studies/spy_beater_hunt_v2/LOOP_PROTOCOL.md`
8. Latest `studies/spy_beater_hunt_v2/iterations/*/SUMMARY.md`, if any
9. One relevant book summary for the hypothesis

## Iteration Artifacts

Each iteration writes under:

`studies/spy_beater_hunt_v2/iterations/NNN-YYYY-MM-DD-<slug>/`

Required files:

- `PRE_REG.md` before testing;
- `RESULTS.json` after testing;
- `SUMMARY.md` with verdict and lessons;
- local scripts/tables/plots as needed.

## Pre-Registration

`PRE_REG.md` must include:

- hypothesis and citation;
- data sources and date ranges;
- exact configs before running;
- expected benchmark comparison vs SPY;
- gates to compute;
- kill rules for the iteration;
- `cumulative_n_trials` before and after.

No pre-registration means the result cannot be promotional.

## Scope Rules

- One family per iteration.
- Prefer 1-6 configs. Avoid large grids unless the goal is explicitly an audit.
- Do not modify legacy study files unless the iteration is explicitly an audit
  report and the change is documentation-only.
- New code should live inside the iteration directory unless it is obviously
  reusable and tested.
- Do not commit or push.
- Do not update `docs/investment-mandate.md`.

## Verdict Labels

- `winner`: beats SPY and passes all hard gates.
- `promising_not_validated`: economically interesting but at least one hard gate
  missing or failed.
- `fail`: tested and did not beat SPY or failed key gates.
- `infrastructure_only`: audit/scaffold result, no strategy claim.
- `data_blocked`: hypothesis could not be tested honestly with available data.

## MEMORY Update

At the end of every iteration, update `MEMORY.md`:

- increment `total_iterations`;
- increment `cumulative_n_trials` by tested configs;
- update latest fields;
- append a short note under `Hypotheses Tested`;
- add dead-end families when appropriate.

## Stop Conditions

The shell stops if:

- `MEMORY.md status: winner`;
- `total_iterations >= target_total_iterations`;
- an iteration exits non-zero or times out.

## Mandate Guard

This study cannot authorize live deployment. Any future winner requires explicit
human review and mandate override. PBO/DSR are hard statistical controls, not
optional diagnostics `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
