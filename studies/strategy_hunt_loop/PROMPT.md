# Strategy Hunt Loop — Iteration Prompt

You are Claude Code resuming the **Strategy Hunt Loop** for the ai-trade
project at `/var/www/pessoal/ai-trade`. Your conversation history is
empty — this prompt + files on disk are your only context.

---

## Mission (unchanged across iterations)

Find ONE trading strategy that **beats SPY 1x buy-hold in risk-adjusted
terms (Sharpe) on real data** and passes the 7-gate battery
cross-dataset. Exact criteria + scoring rubric in `WINNER_AND_RANKING.md`.

If this iteration finds a winner → set `status: winner` in
`BASE_MEMORY.md`, the shell loop halts.

If not → document HONESTLY what failed, update memory + dead-ends,
next iteration continues in a fresh session.

---

## FIRST ACTIONS (mandatory, in this order)

1. `studies/strategy_hunt_loop/BASE_MEMORY.md` — full read (state +
   iteration log + top-K ranked + promising directions + constraints)
2. `studies/strategy_hunt_loop/INFRASTRUCTURE.md` — available simulators,
   data loaders, validation, metrics, signals, data cache (reuse, don't
   rebuild)
3. `studies/strategy_hunt_loop/DEAD_ENDS.md` — structural dead-ends
   you must NOT re-test
4. `studies/strategy_hunt_loop/WINNER_AND_RANKING.md` — strict 5-condition
   winner test + 0-100 scoring rubric + tier system
5. `studies/strategy_hunt_loop/scoring.py` — the reusable scoring helper
   (import at end of Stage 4 to produce `verdict.json`)
6. `CLAUDE.md` + `.claude/CLAUDE.md` — project rules (mandate §1,
   citations, gates)
7. `jornada/README.md` — current project state
8. Last successful iteration's `final_report.md` (if any) — know what
   the prior session learned
9. `data/tiingo/manifest.json` — data availability (if it exists)
   — note which tickers and frequencies you have

---

## THE 5 STAGES (execute strictly in order)

### STAGE 1 — PROPOSE HYPOTHESIS

Propose **ONE** strategy structurally different from every entry in
`DEAD_ENDS.md`.

Requirements:

- **Cite ≥ 1 book** from `books/summaries/` as primary source (use
  slugs from `books/MAPPING.md`). Books cover 1934 (Graham) → 2022
  (modern AFML-family) — any era is fair game. Book citation is
  mandatory.
- **Web search for extra depth is open to any era**:
  - Classical papers (Fama-French 1993, Jegadeesh-Titman 1993,
    Campbell-Shiller 1988, Shiller 1981, Lo-MacKinlay 1988, Carhart
    1997, Asness 1997+, etc.) — **all valid citations**, no date
    floor.
  - Modern refinements (post-2015) for emerging techniques like
    meta-labeling, regime HMM, ML factor timing — preferred when the
    hypothesis hinges on newer methodology.
  - arXiv q-fin / SSRN / AQR / AEA publications — any year.
- Use WebFetch on a specific URL when you have one in mind; use
  WebSearch when you need to find relevant literature. Cite the
  paper's DOI/arxiv ID in the hypothesis spec.
- **Structurally different**: must not match any pattern in
  `DEAD_ENDS.md` "How to tell". New asset class, new timeframe, new
  regime definition, new risk mechanism, or new portfolio construction.
- **Edge hypothesis**: in ONE sentence, what does SPY 1x buy-hold
  fail to capture that this strategy exploits?
- **Kill criteria**: what result at end of STAGE 3 would falsify the
  hypothesis? (Pre-commit to this — prevents post-hoc rationalization.)

Pick from `BASE_MEMORY.md` `## Promising unexplored directions` unless
you have specific reason to propose outside the list (document the
reason).

Selection heuristics (use to choose between candidates, not to invent
new ones outside the list):

- **Start simplest version (Occam's razor)** — if the simple version
  can't beat SPY, no amount of complexity will. Defer ML/HMM/multi-
  signal compositions until a single-mechanism baseline scores at
  least PROMISING.
- **Think about what SPY doesn't capture** — sector rotation? factor
  tilt? non-equity? timing? regime? cross-asset correlation? credit?
  The structurally new direction usually answers this question first
  and picks a mechanism second.

Red flags (means you should pick differently):

- "I'll tweak params of a known approach" → that's overfit, not novel
- "I'll combine 3 strategies from iter 001" → combination of
  dead-ends is still a dead-end
- "I can't find a book citation" → go back to `books/summaries/` and
  pick a different direction

### STAGE 2 — WRITE HYPOTHESIS SPEC

Create directory: `studies/strategy_hunt_loop/iterations/{{ITERATION_N}}-{{STAMP}}-<slug>/`

Write `hypothesis.md`:

```markdown
# Iteration {{ITERATION_N}} — <one-line hypothesis>

## Hypothesis
<1 paragraph: what the strategy does + why it should work>

## Primary citation
`[book.slug, p.X]` — <one-line what this cites justifies>

## Additional citations
- `[book.slug, p.Y]` — ...
- Web: <URL + paper title + arxiv id if applicable>

## Edge source
<1 sentence: what SPY 1x misses that this captures>

## Datasets
- educational (SPYSIM synth 40y): <reason to test here>
- spy_real (SPY/UPRO 17y): <reason>
- ndx_real (QQQ/TQQQ 16y): <reason>

## Kill criteria (pre-committed)
If <specific observable at end of testing> happens, this hypothesis
is falsified regardless of secondary metrics.

## Expected budget
- Configs to test: ~N
- Wall-time: ~M minutes
- Files to create: ...

## Implementation plan
1. ...
2. ...
```

### STAGE 3 — IMPLEMENT + TEST

Implement in `src/ai_trade/backtest/strategies/` if the strategy is
genuinely new, OR in a lightweight script inside `iterations/NNN-*/`
if it's primarily config-of-existing-infra.

Rules:

- **Reuse existing infra** (see `INFRASTRUCTURE.md`). Only build new
  modules when the mechanism is qualitatively new.
- **TDD**: write tests FIRST for any new simulator logic.
  `tests/test_<slug>.py`. Baseline pytest must stay green (currently
  ~796 collected; never reduce passing count).
- **Run on all 3 datasets**: educational synth + spy_real + ndx_real.
  Cross-dataset is non-negotiable.
- **Save results** to `iterations/{{ITERATION_N}}-*/results.json`
  with per-dataset metrics.
- **Cross-lib G7**: if you wrote a new simulator, also write a
  hand-rolled numpy reference to confirm ±3 pp CAGR parity.

### STAGE 4 — EVALUATE GATES + COMPUTE SCORE

**Step 4a — Gate battery** (per dataset, run on top-5 by composite):

- G1 PBO (grid-level per dataset) < 0.5
- G2 DSR p-value < 0.05 with **n_trials = cumulative from
  `BASE_MEMORY.md` frontmatter + configs tested this iteration**
- G3 Walk-Forward 6/8 + MDD<25% per window
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0
- G7 Cross-lib ±3 pp CAGR (mandatory if new simulator)

Benchmarks (hardcoded in `scoring.BENCHMARKS`):
- educational: Sharpe 0.68, CAGR 11.47%, MDD 55.14%
- spy_real: Sharpe 0.90, CAGR 14.97%, MDD 33.70%
- ndx_real: Sharpe 0.955, CAGR 19.18%, MDD 35.12%

**Step 4b — Score using `scoring.py`**:

```python
import sys
sys.path.insert(0, "studies/strategy_hunt_loop")
from scoring import score_strategy, DatasetMetrics, Gates

metrics = {
    "educational": DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    "spy_real":    DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    "ndx_real":    DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
}
gates = {
    "educational": Gates(g1_pbo=..., g2_dsr=..., g3_wf=..., g4_oos=..., g5_fwd=..., g6_bootstrap=..., g7_crosslib=...),
    "spy_real":    Gates(...),
    "ndx_real":    Gates(...),
}
# cumulative_n_trials = BASE_MEMORY.md frontmatter value + configs tested this iter
result = score_strategy(metrics, gates, cumulative_n_trials=NNNN)
# result.total_score (0-100 int)
# result.tier (Tier enum: WINNER / STRONG / PROMISING / MARGINAL / NEAR_FAIL / FAIL)
# result.winner_conditions_met (bool — strict check)
# result.criteria (dict with points per criterion)
```

**Score rubric summary** (full detail in `WINNER_AND_RANKING.md`):
- 25 pts: Sharpe edge across datasets
- 25 pts: Gate pass per dataset + cross-dataset bonus
- 15 pts: DSR significance (cumulative n_trials)
- 15 pts: CAGR floor per dataset (≥ 0.8 × benchmark)
- 15 pts: MDD ceiling per dataset (≤ benchmark + 5pp)
- 5 pts bonus: robustness (caller may add rolling-window consistency)

**Tier interpretation**:
- 🏆 **WINNER** — score ≥ 90 AND all 5 strict conditions hold
- 🥇 **STRONG** — score 75-89 (very close, investigate further)
- 🥈 **PROMISING** — score 60-74 (has edge on some axis)
- 🥉 **MARGINAL** — score 40-59 (weak but some credit)
- 📉 **NEAR_FAIL** — score 20-39 (close to noise)
- ❌ **FAIL** — score < 20 (add to DEAD_ENDS.md)

### STAGE 5 — FINAL REPORT + UPDATE MEMORY

Write `iterations/{{ITERATION_N}}-*/final_report.md` (prose, honest):

```markdown
# Iteration {{ITERATION_N}} — Final Report

## Verdict
🏆 WINNER | 🥇 STRONG | 🥈 PROMISING | 🥉 MARGINAL | 📉 NEAR_FAIL | ❌ FAIL
(score X/100, winner_conditions_met=true|false)

## Headline metrics (top candidate)
| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates |
|---|---|---|---|---|
| educational | X (+/−Y vs 0.68) | ... | ... | N/7 |
| spy_real    | ...              | ... | ... | N/7 |
| ndx_real    | ...              | ... | ... | N/7 |

## Score breakdown
| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | X | 25 | ... |
| 2 Gates | X | 25 | edu N/7 + spy N/7 + ndx N/7, cross-bonus? |
| 3 DSR | X | 15 | worst p=... with n_trials=... |
| 4 CAGR floor | X | 15 | datasets passing: ... |
| 5 MDD ceiling | X | 15 | datasets passing: ... |
| 6 Robustness | X | 5 | ... |
| **total** | **X** | **100+5** | tier: **...** |

## Configuration tested
<exact cfg_id + full param list>

## What worked / what didn't
<2-4 paragraphs honest>

## Main lesson (for future iterations)
<1 paragraph — this is what goes into BASE_MEMORY>

## Structural dead-ends discovered
<patterns to add to DEAD_ENDS.md if any>

## Citations used
<list of [book.slug, p.X] + papers>

## Next iteration suggestions
<2-3 structurally different directions that this iteration's findings
point toward>
```

**Write `iterations/{{ITERATION_N}}-*/verdict.json`** using the result
of `score_strategy()`:

```python
import json
from pathlib import Path

verdict = result.to_dict()
verdict["configs_tested"] = <int>
verdict["primary_citation"] = "[book.slug, p.X]"
verdict["hypothesis_slug"] = "<slug>"

Path(f"studies/strategy_hunt_loop/iterations/{{ITERATION_N}}-*/verdict.json").write_text(
    json.dumps(verdict, indent=2, default=str),
    encoding="utf-8",
)
```

**Update `BASE_MEMORY.md`**:

1. Bump `total_iterations` in frontmatter
2. Update `latest_iteration`
3. Update `cumulative_n_trials` += configs tested this iteration
4. Append a **full 6-field entry** to `## Iteration log` (newest first):
   ```markdown
   ### NNN — YYYY-MM-DD — <one-line hypothesis> (TIER, score X/100)
   - **Hypothesis:** <...>
   - **Citations:** <...>
   - **Scope:** N configs, 3 datasets
   - **Result:** Sharpe edu/spy/ndx, gates edu/spy/ndx, DSR p=...
   - **Score breakdown:** 1:X/25 2:X/25 3:X/15 4:X/15 5:X/15 6:X/5
   - **Lesson:** <one line>
   ```
5. **Update `## Top-K strategies ranked`** — maintain top-5 ever-scored
   across all iterations. Insert this iteration's top candidate if its
   score enters top-5; demote/drop lowest. Keep the `headline` cell
   ≤ 1 line / ≤ 120 chars (full detail belongs in the iteration log
   entry below).
6. If WINNER (tier=WINNER): set `status: winner` in frontmatter,
   populate `## Winners found`
7. If FAIL with new structural dead-end: append section to `DEAD_ENDS.md`,
   plus a **1-line** entry to BASE_MEMORY's `## Structural dead-ends`
   section (full text lives in `DEAD_ENDS.md`)
8. If direction consumed, move it from `## Promising unexplored
   directions` to consumed/dead state

**Auto-prune rule (byte-aware)**: after writing your new entry, run
`wc -c studies/strategy_hunt_loop/BASE_MEMORY.md`. **If > 18000 bytes**,
compress every entry in `## Iteration log` EXCEPT the latest one
(the one you just wrote) down to the 3-line format:

```markdown
### NNN — YYYY-MM-DD — <slug> (TIER, X/100)
- **Result:** Sharpe edu/spy/ndx X.X/X.X/X.X (Δ ±X.XX/±X.XX/±X.XX), gates N/N/N, DSR p=X.XXX (n=NNNN), winner=N/5; score 1:X 2:X 3:X 4:X 5:X 6:X.
- **Lesson:** <1-2 sentences strategic takeaway>. See `iterations/NNN-*/`.
```

The old `Hypothesis` / `Citations` / `Scope` fields stay recoverable
from `iterations/NNN-*/hypothesis.md` + `verdict.json` +
`final_report.md`. After compression, re-run `wc -c` and confirm file
is under 18 000 bytes; if not, compress the latest entry too.

---

## HARD RULES

- **NEVER modify mandate §1** (`docs/investment-mandate.md`). It stays
  MAINTENANCE 100% Plano C. Even a winner is a CANDIDATE, not
  auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2) — `[book.slug, p.X]`
  for every decision.
- **Baseline pytest must stay green** — revert any change that breaks.
  Never reduce the passing count.
- **NEVER commit to git** — shell `run_loop.sh` handles commits.
- **Max 2 h wall-time per iteration** — if running longer, save
  partial results + write final_report.md with "INCOMPLETE" status.
- **Cross-dataset non-negotiable** — synth-only edge does NOT count.
- **Stop at STAGE 5** — do NOT suggest / build paper-trading
  scaffolding (that's outside the hunt loop).
- **If STAGE 3 fails** (implementation can't be done cleanly in
  budget), pivot to alternative direction or mark iteration as
  aborted. Don't force bad code to pass tests.

---

## IF WINNER FOUND

1. `status: winner` in `BASE_MEMORY.md` frontmatter
2. Full details in `## Winners found` section
3. Final report clearly marked "🏆 WINNER"
4. `verdict.json` has `"status": "winner"`

Shell loop `run_loop.sh` reads the flag and halts.

**Do NOT propose deployment, override, or paper trading.** That is a
user decision, made separately with the full evidence in hand.

---

## IF NOT WINNER

1. `status: iterating` in `BASE_MEMORY.md`
2. 6-field entry appended to `## Iteration log` (then auto-prune if > 18 KB)
3. `DEAD_ENDS.md` updated if structural (plus 1-line summary in BASE_MEMORY)
4. `## Promising unexplored directions` refreshed (remove tried,
   possibly add new ones discovered during research)
5. Suggest 2-3 structurally different directions explicitly in the
   final_report.md's "Next iteration suggestions" section

---

Now begin with **FIRST ACTIONS** — read BASE_MEMORY.md, then
INFRASTRUCTURE.md, then DEAD_ENDS.md, then WINNER_AND_RANKING.md,
then proceed to Stage 1.
