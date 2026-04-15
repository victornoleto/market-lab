# Self-improvement loop

Autonomous loop that runs Claude Code in a fresh context window per iteration, using `memory.md` as the only continuity between iterations. The shell script (`scripts/self_improve_loop.sh`) handles process spawning; Claude does the thinking; the memory file accumulates state.

## Files in this directory

- `memory.template.md` — bootstrap state. Copied to `memory.md` on first run. Keep this file as the canonical reset-to baseline.
- `memory.md` — live state (gitignored — see below). Iteration N reads it, updates it, exits. Iteration N+1 reads the updated file.
- `README.md` — this file.

## Run it

```bash
# Default: 10 iterations, research-only scope, 15-min timeout each
bash scripts/self_improve_loop.sh

# Tighter budget (recommended for first try)
MAX_ITER=2 bash scripts/self_improve_loop.sh

# Allow code edits (still no git commits)
SCOPE=code MAX_ITER=5 bash scripts/self_improve_loop.sh

# Long-running with looser timeout
MAX_ITER=20 ITER_TIMEOUT=1800 bash scripts/self_improve_loop.sh
```

## How termination works

The loop exits when ANY of:

1. The memory file's frontmatter has `status: done` — set by Claude only when a config passed all 3 gates (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8).
2. `MAX_ITER` iterations completed without success.
3. An iteration exited non-zero (timeout, error, killed by user).

## Costs and safety

- Each iteration spawns `claude -p --dangerously-skip-permissions`. Claude can run any tool without confirming. Audit `logs/self_improve/iter_*.log` after each run.
- Token budget per iteration: depends on memory.md size and how much Claude reads/explores. Expect $1-5 per iteration on Opus 4.6, more if Claude runs many backtests.
- Start with `MAX_ITER=2` to verify the prompt + memory loop works end-to-end before scaling.

## Reset to bootstrap

```bash
cp docs/self_improvement/memory.template.md docs/self_improvement/memory.md
```

## Known limitations

- Loop cannot interact with the user mid-iteration. If Claude needs a decision, it must commit to one path or skip.
- Memory file pruning is Claude's responsibility (per the prompt). If Claude is sloppy, the file may grow unbounded — the prompt asks for ~50-entry cap, but is not enforced.
- Concurrency: do not run two loops in parallel against the same memory.md or the same storage root.
- The Tiingo bulk download in progress (2026-04-14) writes to `data/tiingo/`. Iterations should use `--storage-root data/tiingo_adhoc` while the bulk is alive (the memory file's "Constraints" section already documents this).
