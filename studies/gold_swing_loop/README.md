# Gold Swing Loop — how to run

Self-improve loop to find a **day/swing trading strategy on XAUUSD (gold spot)**
that beats gold buy-hold Sharpe risk-adjusted, after Pepperstone CFD costs.
Each iteration = one fresh Claude Code session.

## Sister loop

This runs **in parallel** with `studies/strategy_hunt_loop/` (which targets
equity SPY/QQQ static stacks + VRP). The two loops share architecture and
cross-loop lessons via inherited dead-ends in `DEAD_ENDS.md`. Keep both
sessions hands-off of each other's directories.

## How it differs from sister loop

| axis | strategy_hunt_loop | **gold_swing_loop** |
|---|---|---|
| asset universe | SPY+IEF+GLD baskets, multi-leg | **XAUUSD spot only (single asset)** |
| timeframe | daily rebalance, hold months-years | **intraday→swing, mean hold ≤ 5 days** |
| benchmark | SPY 1x buy-hold | **XAUUSD buy-hold** |
| cost model | ETF expense + 2 bps slippage | **CFD spread 8 bps round-trip + swap −1 bps/night** |
| broker target slot | dormant (mandate §1) | **Plano A reactivation (Pepperstone CFD)** |
| dataset triple | educational/spy_real/ndx_real | **gld_long/xauusd_real/xauusd_intraday** |

## Files

| file | purpose |
|---|---|
| `BASE_MEMORY.md` | state between sessions (iter log, winners, candidates) |
| `PROMPT.md` | iteration prompt template (orchestrator substitutes `{{ITERATION_N}}` / `{{STAMP}}`) |
| `WINNER_AND_RANKING.md` | strict 5-condition winner test + 0-100 scoring rubric |
| `INFRASTRUCTURE.md` | available simulators, data loaders, cost models for gold |
| `DEAD_ENDS.md` | structural dead-ends (inherits cross-loop closures) |
| `scoring.py` | reusable scoring helper with gold benchmarks |
| `run_loop.sh` | orchestrator: launches Claude CLI, auto-commits, halts on winner |
| `iterations/NNN-YYYY-MM-DD-HHmm-slug/` | per-iteration outputs |

## Quick start

```bash
# Must be on a non-main branch (orchestrator auto-creates if on main)
git checkout -b gold-swing/iter-001

# Dry run (just prints prompt, doesn't invoke claude)
DRY_RUN=1 bash studies/gold_swing_loop/run_loop.sh

# Real run — 1 iteration with default model (opus, 90min timeout)
MAX_ITER=1 bash studies/gold_swing_loop/run_loop.sh

# Real run — 50 iterations, 90 min/iter
MAX_ITER=50 bash studies/gold_swing_loop/run_loop.sh
```

## Iter 001 mandatory tasks (different from sister loop)

The first iter MUST:

1. **Measure exact buy-hold benchmarks** for the 3 datasets (gld_long, xauusd_real, xauusd_intraday) and **update `scoring.py BENCHMARKS` dict** with measured values. Current values are placeholders.
2. **Calibrate Pepperstone cost model** — verify spread + swap assumptions against Pepperstone live spec or recent fills (default: 8 bps round-trip spread + −1 bps/night swap; intraday-close = swap-free).
3. **Pre-commit dataset slicing** — gld_long 2004-2024 (15y train), xauusd_real 2020-2024 walk-forward, xauusd_intraday 4h-resampled or 1h-direct.
4. **Decide simulator architecture** — extend `src/ai_trade/backtest/strategies/` for single-asset day/swing OR use lightweight per-iter scripts.

After iter 001, the loop runs identically to the sister loop.

## Halt conditions

1. `BASE_MEMORY.md` has `status: winner` in frontmatter (iteration found one)
2. `MAX_ITER` reached without winner (resume with higher MAX_ITER)
3. An iteration times out (`ITER_TIMEOUT`) or exits non-zero
4. An iteration tries to run on main/master (branch guard)

## Mandate context (CRITICAL)

- Project is in mandate §1 **MAINTENANCE 100% Plano C**.
- This loop targets **Plano A reactivation slot** (Pepperstone CFD short-hold).
- Per mandate §3, Plano A reactivation **requires multi-asset** (SPY/QQQ/Gold/BTC/ETH/FX). Single-asset XAUUSD candidates are RESEARCH OUTPUT, not deployable until extended to multi-asset basket.
- A WINNER from this loop does NOT auto-deploy. Requires override §7 + paper-trade 3-6 months + multi-asset extension test.

## Cost considerations

Each iteration:
- ~1-2 hours of Claude Opus compute (matches sister loop pace)
- Reads ~20-50 KB of context (BASE_MEMORY + PROMPT + project files)
- Writes ~10-30 KB of artifacts per iteration

Rough budget per iteration at Opus pricing: USD 5-15. Run `MAX_ITER=1` first
to gauge before committing to long runs.

## When to stop manually

- 5+ consecutive iterations fail in same structural way (signal that current
  candidate list is fundamentally wrong — needs human-led refresh)
- Cumulative `n_trials` passes 5 000 without winner (DSR penalty becomes
  prohibitive given gold's narrower data window vs SPY)
- Sister loop's mapped Pareto frontier (iter 046 = 85 STRONG) suggests gold
  loop ceiling may sit below 90 too — set realistic STRONG-tier expectations

## If the loop finds a winner

1. Inspect `BASE_MEMORY.md` `## Winners found` section + iteration dir
2. Verify on out-of-sample window not used in training
3. Run extended walk-forward (CPCV with 6+ embargoed splits)
4. **Manually draft an override** per mandate §7 in `docs/mandate_overrides/YYYY-MM-DD-<winner-slug>-open.md`
5. **Multi-asset extension test** (mandate §3): adapt to SPY/QQQ/BTC/FX too — single-asset XAUUSD edge does NOT count for Plano A reactivation
6. Paper-trade 3-6 months on Pepperstone demo before any real capital
7. ONLY THEN consider deployment
