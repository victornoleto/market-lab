# Strategy Hunt Loop — how to run

Self-improve loop to find a strategy that beats SPY 1x buy-hold Sharpe
on real data. Each iteration = one fresh Claude Code session.

## Files (top-level = hunt loop core)

| file | purpose |
|---|---|
| `BASE_MEMORY.md` | state between sessions (iteration log, winners, directions) |
| `PROMPT.md` | iteration prompt template (gets `{{ITERATION_N}}` / `{{STAMP}}` substituted) |
| `WINNER_AND_RANKING.md` | strict 5-condition winner definition + ranking rubric |
| `DEAD_ENDS.md` | structural failures from past iterations — forbidden zones |
| `INFRASTRUCTURE.md` | Tiingo cache + testfolio synth ticker inventory |
| `FINAL_REPORT.md` | post-halt consolidated report (iter 079 winner + deploy guide) |
| `SUMMARY_FOR_PHONE.md` | shorter version of FINAL_REPORT for casual reading |
| `run_loop.sh` | orchestrator: launches Claude CLI, auto-commits, halts on winner |
| `scoring.py` / `plot_helper.py` | hunt-loop infrastructure used by per-iter sessions |
| `cross_lib_validator.py` / `long_window_validator.py` | post-hunt validation drivers |
| `rescore_v2.py` / `RESCORE_V2_SUMMARY.md` | DSR re-score under relaxed n_trials convention |
| `post_tax_validation.py` / `POST_TAX_VALIDATION.md` | Lei 14.754 post-tax sims |
| `iterations/NNN-YYYY-MM-DD-HHmm-slug/` | per-iteration outputs |
| **`deploy_studies/`** | **post-hunt deploy-readiness studies (see deploy_studies/README.md)** |

## Deploy studies (`deploy_studies/`)

After the hunt loop halted at iter 079, several follow-up studies were
done to compare the winner candidates against external alternatives
(Plano C V3_1, NTSX+GDE, V_HYBRID variants). Each study is self-contained
in its own subdirectory:

- `iter035_variants/` — 4 deploy paths for iter 035 (V0/V1/V2/V3)
- `iter079_leveraged/` — 2× and 3× LETF substitution test (refuted)
- `aporte_simulation/` — DCA $10k+$1.5k/mo × 40y money-weighted IRR
- `v1_vs_planoc/` — V1 NTSX+GDE vs Plano C V3_1 v3.5 (32y comparison)
- `us_vs_global/` — academic US-vs-Global study with rolling 20y/30y
- `portfolio_4way/` — V1 vs V3_1 vs V_HYBRID vs V_HYBRID_SIMPLE
- `portfolio_variants/` — 6 V_HYBRID variants; **WINNER**: V_HYBRID + 10% MF
- `letfs_5way/` — Reddit post 5-portfolio shootout 1986-2026

See `deploy_studies/README.md` for index + final recommendation.

## How it works

1. Each iteration Claude reads `BASE_MEMORY.md` + `DEAD_ENDS.md` +
   `WINNER_CRITERIA.md`
2. Picks ONE direction from `## Promising unexplored directions`
3. Runs 5 stages: research → spec → implement+test → gates → report
4. Updates `BASE_MEMORY.md` with results + moves the direction to
   dead-ends if failed
5. Shell loop reads `status` field; if `status: winner` → halts

## Quick start

```bash
# Must be on a non-main branch
git checkout -b strategy-hunt/iter-002

# Dry run (just prints prompt, doesn't invoke claude)
DRY_RUN=1 bash studies/strategy_hunt_loop/run_loop.sh

# Real run — 1 iteration with default model (opus, 90min timeout)
MAX_ITER=1 bash studies/strategy_hunt_loop/run_loop.sh

# Real run — 5 iterations, 2h each, sonnet model
MAX_ITER=5 ITER_TIMEOUT=7200 CLAUDE_MODEL=sonnet bash studies/strategy_hunt_loop/run_loop.sh
```

## Env vars

| var | default | meaning |
|---|---|---|
| `MAX_ITER` | 5 | hard cap on iterations |
| `ITER_TIMEOUT` | 5400 (90 min) | seconds per iteration |
| `COOLDOWN` | 30 | seconds between iterations |
| `CLAUDE_MODEL` | opus | opus / sonnet / haiku |
| `DRY_RUN` | "" | if set, print prompt and exit |

## Cost considerations

Each iteration:
- ~1-2 hours of Claude Opus compute
- Reads ~20-50 KB of context (BASE_MEMORY + PROMPT + project files)
- Writes ~10-30 KB of artifacts per iteration

Rough budget per iteration at Opus pricing: USD 5-15 depending on
how much code + backtest it runs. Start with `MAX_ITER=1` to gauge.

## Halt conditions

The loop stops when:

1. `BASE_MEMORY.md` has `status: winner` in frontmatter (iteration found one)
2. `MAX_ITER` reached without winner (resume with higher MAX_ITER)
3. An iteration times out (`ITER_TIMEOUT`) or exits non-zero
4. An iteration tries to run on main/master (branch guard)

## Safety

- `--dangerously-skip-permissions` is passed to `claude` so the loop runs
  unattended. **Audit `logs/strategy_hunt_loop/iter_NNN_*.log` after
  each iteration.** Especially first few.
- Branch guard refuses to run on main/master. Iterations create code +
  commits; they should be on a feature branch.
- No code is pushed to remote. Shell loop only commits locally.
- Mandate §1 (MAINTENANCE 100% Plano C) is explicit in the prompt as
  DO NOT MODIFY. Even a winner is a candidate, not auto-deployed.

## Example flow (starting iteration 002)

```bash
# 1. Create branch
git checkout -b strategy-hunt/iter-002-sector-momentum

# 2. Dry-run first to inspect prompt
DRY_RUN=1 bash studies/strategy_hunt_loop/run_loop.sh 2>&1 | less

# 3. Run 1 iteration
MAX_ITER=1 bash studies/strategy_hunt_loop/run_loop.sh

# 4. Inspect outputs
cat studies/strategy_hunt_loop/iterations/002-*/final_report.md
cat studies/strategy_hunt_loop/BASE_MEMORY.md | head -50

# 5. If not winner, run more iterations
MAX_ITER=5 bash studies/strategy_hunt_loop/run_loop.sh

# 6. When winner found (status: winner), inspect + decide
cat studies/strategy_hunt_loop/BASE_MEMORY.md
# ... produce override per mandate §7 if going live
```

## Backlog (orchestrator hardening)

- **Retry on transient API errors before fail-fast.** Today
  `run_loop.sh` aborts the entire loop on **any** non-zero exit from
  `claude -p` (lines 160-163). That includes Anthropic-side transients
  like `529 overloaded_error` (API congestion) and `429 rate_limit`,
  which killed the iter 008 run on 2026-04-24 14:11 right after the
  iteration had already produced full artifacts and was on the final
  bookkeeping step. Plan: wrap the `claude -p` call in a 3-attempt
  retry-with-backoff (60s / 180s / 600s) that distinguishes infra
  errors (parse stderr for `overloaded_error` / `rate_limit` / network
  timeout) from real model errors, and only aborts the loop on
  persistent failure. Keep current fail-fast behaviour for any other
  non-zero exit. Tracked here, not in `ROADMAP.md`, because the
  project is in mandate §1 MAINTENANCE — this is hunt-loop tooling
  debt, not a roadmap deliverable.

## Resuming after interruption

If the loop is interrupted (Ctrl-C, crash, timeout):

1. `BASE_MEMORY.md` is updated incrementally per iteration — any
   completed iteration is recorded there
2. Resume with another `bash run_loop.sh` invocation — it reads the
   next iteration number from `iterations/` directory
3. If an iteration was partially complete (dir exists but no
   `final_report.md`), delete that dir first:
   `rm -rf studies/strategy_hunt_loop/iterations/NNN-*/`

## Pruning `BASE_MEMORY.md`

If `BASE_MEMORY.md` grows past ~20 KB the shell will warn. Prune by:

1. Keep latest 10 iteration log entries + all winners
2. Move older detailed notes to an `_archive/` subdirectory
3. Keep `## Promising unexplored directions` and
   `## Structural dead-ends` sections current

The shell does NOT auto-prune — human judgment needed to decide what
to keep.

## When to stop running the loop manually

- 5+ consecutive iterations fail in the same structural way (signal
  that the current "promising unexplored directions" list is
  fundamentally wrong — needs human-led refresh)
- Cumulative n_trials passes 10 000 without winner (DSR penalty
  becomes prohibitive; future winners need to be VERY strong)
- Review each iteration's `final_report.md` for any patterns the
  loop is missing — sometimes the lesson is "we need a different
  class of hypothesis"

## If the loop finds a winner

1. Inspect `BASE_MEMORY.md` `## Winners found` section + iteration dir
2. Run `studies/ema_sma_threshold_crash_protected/deep_review_rolling.py`
   equivalent for the winner — deep rolling-window validation
3. Synth → real gap check (iter 001 showed -3.4 pp/yr drag)
4. **Manually draft an override** per mandate §7 in
   `docs/mandate_overrides/YYYY-MM-DD-<winner-slug>-open.md`
5. Paper-trade for 3-6 months before any real capital
6. ONLY THEN consider deployment
