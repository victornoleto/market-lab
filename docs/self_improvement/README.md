# Self-improvement loop — operations guide

Autonomous loop that drives Claude Code through a queue of research/code
tasks overnight, using a single Markdown file (`memory.md`) as the only
continuity between iterations. Each iteration is a **fresh** Claude
session with zero conversation history — the file is the brain.

- **Script:** `scripts/self_improve_loop.sh`
- **Live state:** `docs/self_improvement/memory.md` (gitignored)
- **Template:** `docs/self_improvement/memory.template.md` (committed — reset baseline)
- **Logs:** `logs/self_improve/loop_<ts>.log` (per-run) and `logs/self_improve/iter_NNNN_<ts>.log` (per iteration)

---

## When to use (and when NOT to)

**Use it for:**

- Overnight research sweeps (re-run grids with new data, benchmark variants, ablations).
- Incremental code work on a **well-scoped** backlog (the `Promising leads` section in `memory.md`).
- Any task you can describe in one sentence and finish in ≤15 min wallclock per iteration.

**Do not use it for:**

- Open design discussions (the loop can't ask you questions mid-run — use an interactive Claude Code session).
- Multi-step refactors across more than 3-4 files (break them into separate leads first).
- Anything that needs `git push`, deploys, or external-service writes (the loop scope forbids commits).

---

## First-time setup

One-time (already done if `memory.md` exists):

```bash
cp docs/self_improvement/memory.template.md docs/self_improvement/memory.md
```

Then edit `memory.md`:

- **Goal** — what "done" means (usually: a config that passes all 3 gates).
- **Project state anchor** — one paragraph summarising where the repo is NOW. Update only when the baseline shifts (new strategy landed, dataset refreshed, bug fix committed).
- **Known dead ends** — what NOT to repeat. Grows over time.
- **Promising leads** — ordered queue. The loop consumes them top-down. Claude moves consumed leads to "Known dead ends" (with a one-line reason) when exhausted.
- **Constraints** — hard rules (citation requirement, no concurrent writers to Tiingo storage, pytest must stay green, etc.).

---

## Run it

```bash
# Quick smoke (RECOMMENDED for the first run after any change to the script
# or prompt) — 1 iteration, 2-minute timeout, research-only.
MAX_ITER=1 ITER_TIMEOUT=120 SCOPE=research bash scripts/self_improve_loop.sh

# Default overnight run — 10 iterations, 15-min timeout each, research-only.
bash scripts/self_improve_loop.sh

# Medium overnight — 20 iterations, 30-min timeout each.
MAX_ITER=20 ITER_TIMEOUT=1800 bash scripts/self_improve_loop.sh

# Code-allowed scope (creates new src/ files, edits tests). Still no commits.
SCOPE=code MAX_ITER=10 bash scripts/self_improve_loop.sh
```

Environment variables:

| Var | Default | Meaning |
|---|---|---|
| `MAX_ITER` | 10 | Hard cap on iterations. |
| `ITER_TIMEOUT` | 900 (15 min) | Seconds per iteration before the loop aborts. |
| `SCOPE` | research | `research` = read-only on `src/` + `tests/`; can write `reports/` and `docs/self_improvement/`. `code` = also allowed to add/modify `src/` + `tests/`. |
| `COOLDOWN` | 5 | Seconds to sleep between iterations. |

**Background runs:** the loop is blocking by design (sequential iterations). To run it detached:

```bash
nohup bash scripts/self_improve_loop.sh > /dev/null 2>&1 &
echo $! > /tmp/self_improve.pid
```

---

## Monitor a running loop

**Top-line progress** (latest iteration status):

```bash
tail -F logs/self_improve/loop_*.log
```

**Current iteration's thinking** (what Claude is doing RIGHT NOW):

```bash
tail -F logs/self_improve/iter_*.log | tail -F
```

Or the most recent:

```bash
ls -t logs/self_improve/iter_*.log | head -1 | xargs tail -F
```

**Memory-file snapshot** (what the loop "knows"):

```bash
awk '/^---$/{f++; next} f==1' docs/self_improvement/memory.md
# → prints just the YAML frontmatter (status, iteration, best_*)
```

**Is a loop still running?**

```bash
pgrep -af self_improve_loop.sh
```

---

## Stop / interrupt

**Gracefully** (let the current iteration finish, skip the rest):

```bash
# Find the loop PID and kill only the outer shell (the inner claude finishes
# and then the shell detects EOF on its stdin and exits).
pkill -f self_improve_loop.sh
```

**Hard stop** (kills the current Claude iteration too):

```bash
pkill -f 'claude -p'        # kills the in-flight Claude process
pkill -f self_improve_loop.sh
```

The script is idempotent and resumable — it reads the `iteration:` counter
from `memory.md` on the next run and picks up from `iteration + 1`. No state
is lost, but the killed iteration produces no record unless Claude already
wrote to `memory.md` before being killed.

---

## Resume after interruption

Just run the same command again:

```bash
bash scripts/self_improve_loop.sh
```

The loop:

1. Reads `iteration: N` from `memory.md`.
2. Starts at `N+1`, runs `N+1 … N+MAX_ITER`.
3. Respects the same `status: done` early-exit.

---

## Understanding `memory.md`

```yaml
---
status: in_progress | done         # only "done" triggers early-exit
iteration: N                       # counter, incremented by Claude each iter
best_verdict: PASS | None          # best config found so far (gate-passing)
best_sharpe: 0.58                  # Sharpe of best_verdict (null if none)
best_asset: SPY                    # symbol of best_verdict
best_config: "{hp_period: 48, ...}"  # JSON-ish dump of best config
---
```

Sections below the frontmatter:

- `## Goal` — do NOT modify between runs.
- `## Project state anchor` — update when baseline shifts.
- `## Known dead ends` — append-only; Claude adds entries when a lead is
  ruled out. Never delete.
- `## Promising leads not yet explored` — consume in listed order unless
  Claude has a documented reason to deviate.
- `## Constraints` — hard rules. Kept short. Edit manually when a
  constraint lifts (e.g. "Tiingo bulk done → drop the adhoc-storage rule").
- `## Tools / commands cheatsheet` — copy-paste recipes. Update when a
  script interface changes.
- `## History` — per-iteration log written by Claude. Target ≤50 entries;
  Claude prunes past that. The shell loop emits a warning when the file
  exceeds 60 KB.

---

## Cost management (R$200 Claude Code plan)

Per iteration (Opus 4.6, empirically):

| Work | Tokens | USD | BRL |
|---|---|---|---|
| Read memory + decide + trivial action (ls, tail) | ~5k | $0.10 | R$0.50 |
| Read memory + run one grid (tqdm output) + update memory | ~20k | $0.40 | R$2.00 |
| Read memory + write new strategy module + tests + grid | ~80k | $1.60 | R$8.00 |
| Deep research iteration (multiple subagents) | ~150k | $3.00 | R$15.00 |

Rough budget:

- **10 iterations, research-only:** R$5-20 per run.
- **10 iterations, code-scope with real grids:** R$20-80 per run.
- **R$200/month = ~10-40 full overnight runs depending on workload.**

Token hygiene:

- Keep `memory.md` under 60 KB (the loop warns above that). Every iteration
  re-sends the full file.
- Avoid leaving long verbatim backtest outputs in `## History` — summarise.
- Prefer one large SCOPE=code run with 10 focused leads over 30 tiny iterations.

---

## Troubleshooting

### `=== Iteration N HIT TIMEOUT (900s) — aborting loop ===`

An iteration exceeded `ITER_TIMEOUT`. Causes:

- A grid is bigger than expected (raise `ITER_TIMEOUT` or split the lead).
- Claude is looping on a failed edit (check the iter log for repeated errors).
- Network-bound work (should be rare — the Tiingo backend is storage-first after bulk).

Fix: `tail logs/self_improve/iter_NNNN_*.log` to see what the iteration was doing. If the work was legitimate, rerun with `ITER_TIMEOUT=1800`. If it was stuck, add the failure to `memory.md` under "Known dead ends" so the next iteration avoids it.

### `=== Iteration N exited code=X — aborting loop ===`

Non-zero exit from Claude. Usually a permission block (`--dangerously-skip-permissions` is set by the loop, so this should be rare) or a shell error inside the prompt. Check the iter log's last 50 lines.

### Bloated `memory.md` (loop warns "> 60k bytes")

Run the loop one more time with a pruning instruction added to `## Promising leads` (top priority): *"Prune `## History` to the newest 20 entries plus any PASS entries; document the pruning."*

### `pytest` regressions after a loop iteration

The `## Constraints` section requires green `pytest -q`. If an iteration landed broken code:

1. `git diff` to see the damage.
2. Either revert selectively or run the next iteration with a lead that says *"Revert iteration N's changes to `src/...` because pytest is red."*
3. The loop never `git reset`s on its own — you drive this.

### The loop keeps producing "None" verdicts

Check `best_*` in the frontmatter. If still null after N iterations, the leads may be mis-framed (they pass but no config passes the 3-gate). Edit `memory.md` manually to:

- Add a new, more tractable lead at position 1.
- Move exhausted leads to "Known dead ends".

The loop is cooperative, not autonomous — you steer via `memory.md` edits between runs.

### Accidentally started TWO loops against the same memory

Both will read + write the same file → interleaved iterations → garbled frontmatter. `pkill -f self_improve_loop.sh`, then:

```bash
git show HEAD:docs/self_improvement/memory.template.md > /tmp/template.md
# OR restore from your last good backup
```

Edit `memory.md` to reconcile the state. This is rare; the single-writer convention is by discipline, not enforcement.

---

## Reset to bootstrap

Drops all accumulated history. Use when starting a fundamentally new research direction:

```bash
cp docs/self_improvement/memory.template.md docs/self_improvement/memory.md
```

---

## Known limitations

- The loop cannot interact with the user mid-iteration. Decisions must be pre-encoded in `memory.md`.
- Pruning `## History` is Claude's responsibility per the prompt; the shell only warns.
- Concurrency: **never** run two loops against the same `memory.md` or the same Tiingo storage root.
- `--dangerously-skip-permissions` is set so Claude can run any shell command without asking. Audit the per-iteration logs.
- The script assumes `claude`, `timeout`, and `awk` are on `PATH`. No cross-shell portability beyond bash.
