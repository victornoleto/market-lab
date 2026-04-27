# Global Factor-Tilt Loop — Iteration Prompt

You are Claude Code resuming the **Global Factor-Tilt Loop** for the
ai-trade project at `/var/www/pessoal/ai-trade`. Your conversation
history is empty — this prompt + files on disk are your only context.

---

## Mission (unchanged across iterations)

Find ONE globally-diversified strategy that beats **ALL THREE** of:

1. **VT 1x buy-and-hold** — cap-weighted global passive baseline
   (`scoring.BENCHMARKS["vt_real"]` ≈ Sharpe 0.51 / CAGR 8.8% / MDD
   50.2% on 17y; `["educational"]` ≈ Sharpe 0.66 / CAGR 10.0% / MDD
   58.4% on 56y).
2. **Plano C V3_1 v3.5** — current factor + global Plano C
   (Sharpe ≈ 0.671, CAGR ≈ 10.94%, MDD ≈ 52.43% on 32y).
3. **V_HYBRID + 10% MF** — deploy_studies portfolio_variants WINNER
   (Sharpe ≈ 0.743, CAGR ≈ 10.91%, MDD ≈ 44.71% on 32y;
   `P(rolling 10y < 5%) = 0.6%`).

The bar is **higher than VT-only** because deploy_studies already
identified strong factor + global + capital-efficiency combinations.
This loop must find something **structurally novel** vs those three.

If this iteration finds a winner → set `status: winner` in
`BASE_MEMORY.md`, the shell loop halts.

If not → document HONESTLY what failed, update memory + dead-ends,
next iteration continues in a fresh session.

---

## FIRST ACTIONS (mandatory, in this order)

1. `studies/global_factor_tilt_loop/BASE_MEMORY.md` — full read (state +
   iteration log + top-K ranked + promising directions + constraints)
2. `studies/global_factor_tilt_loop/INFRASTRUCTURE.md` — available simulators,
   data loaders, validation, metrics, signals, data cache (reuse, don't
   rebuild)
3. `studies/global_factor_tilt_loop/DEAD_ENDS.md` — structural dead-ends
   you must NOT re-test
4. `studies/global_factor_tilt_loop/WINNER_AND_RANKING.md` — strict 5-condition
   winner test + 0-100 scoring rubric + tier system
5. `studies/global_factor_tilt_loop/scoring.py` — the reusable scoring helper
   (import at end of Stage 4 to produce `verdict.json`)
6. `studies/global_factor_tilt_loop/README.md` — bifurcation rationale,
   universe, hypothesis menu (Tier 1-4)
7. `CLAUDE.md` + `.claude/CLAUDE.md` — project rules (mandate §1,
   citations, gates)
8. `jornada/README.md` — current project state
9. Last successful iteration's `final_report.md` (if any) — know what
   the prior session learned
10. `data/testfolio/cache/history.meta.json` + `data/tiingo/manifest.json` —
    data availability — note which tickers and frequencies you have

---

## THE 5 STAGES (execute strictly in order)

### STAGE 1 — PROPOSE HYPOTHESIS

Propose **ONE** strategy structurally different from every entry in
`DEAD_ENDS.md` and from the 3 benchmark strategies above.

Requirements:

- **Cite ≥ 1 book** from `books/summaries/` as primary source (use
  slugs from `books/MAPPING.md`). Books cover 1934 (Graham) → 2022
  (modern AFML-family) — any era is fair game. Book citation is
  mandatory.
- **Web search for extra depth is open to any era**:
  - Classical papers (Fama-French 1993, Asness 1997+ via AQR,
    Antonacci 2014, Faber 2007, Jegadeesh-Titman 1993, Avantis
    methodology Repetto 2019, etc.) — **all valid citations**, no date
    floor.
  - Modern refinements (post-2015) for emerging techniques like
    return-stacking, regional rotation, currency hedge, multi-asset
    multi-region momentum — preferred when the hypothesis hinges on
    newer methodology.
  - arXiv q-fin / SSRN / AQR / AEA publications — any year.
- Use WebFetch on a specific URL when you have one in mind; use
  WebSearch when you need to find relevant literature.
- **Structurally different**: must not match any pattern in
  `DEAD_ENDS.md` "How to tell". New universe, new timeframe, new
  regime definition, new risk mechanism, or new portfolio construction.
- **Edge hypothesis**: in ONE sentence, what does VT 1x buy-hold
  AND V_HYBRID+MF AND Plano C V3_1 fail to capture that this strategy
  exploits?
- **Kill criteria**: what result at end of STAGE 3 would falsify the
  hypothesis? (Pre-commit to this.)

Pick from `BASE_MEMORY.md` `## Promising unexplored directions` (seeded
from README's hypothesis menu Tiers 1-4) unless you have specific reason
to propose outside the list (document the reason).

Selection heuristics:

- **Start simplest version (Occam's razor)** — if the simple version
  can't beat the 3 benchmarks, no amount of complexity will. Defer
  ML/HMM/multi-signal compositions until a single-mechanism baseline
  scores at least PROMISING.
- **Think about what VT/V_HYBRID/Plano C don't capture** — currency
  hedge? regional rotation? country-level momentum? emerging-market
  small value? global return-stacking? managed-futures correlation
  with global equity (vs US-only)? regime-conditional global tilts?

Red flags:

- "I'll tweak weights of V_HYBRID by 1pp" → that's overfit, not novel
- "I'll combine 3 dead-ends" → still a dead-end
- "I can't find a book citation" → go back to `books/summaries/`

### STAGE 2 — WRITE HYPOTHESIS SPEC

Create directory: `studies/global_factor_tilt_loop/iterations/{{ITERATION_N}}-{{STAMP}}-<slug>/`

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
<1 sentence: what VT/V_HYBRID/Plano C miss that this captures>

## Datasets
- educational (VTSIM synth 56y): <reason to test here>
- vt_real (VTSIM 17y proxy for VT live): <reason>
- ndx_real (QQQ 16y, carryover stretch test): <reason>

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
  `tests/test_<slug>.py`. Baseline pytest must stay green
  (currently 461 collected per CLAUDE.md; never reduce passing count).
- **Run on all 3 datasets**: educational + vt_real + ndx_real.
- **Save results** to `iterations/{{ITERATION_N}}-*/results.json`
  with per-dataset metrics. Schema must include
  `results["returns_series"][dataset][cfg_id] = {"index": [ISO dates],
  "net_returns": [daily net returns]}` for at least the top candidate
  of each dataset.
- **Cross-lib G7**: if you wrote a new simulator, also write a
  hand-rolled numpy reference to confirm ±3 pp CAGR parity.

### STAGE 4 — EVALUATE GATES + COMPUTE SCORE

**Step 4a — Gate battery** (per dataset, run on top-5 by composite):

- G1 PBO (grid-level per dataset) < 0.5
- G2 DSR p-value < 0.05 with **n_trials = configs tested THIS iteration
  only** (per-iteration hypothesis budget — relaxed convention; see
  `WINNER_AND_RANKING.md` §3 for rationale).
- G3 Walk-Forward 6/8 + MDD<25% per window
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0
- G7 Cross-lib ±3 pp CAGR (mandatory if new simulator)

Benchmarks (hardcoded in `scoring.BENCHMARKS`):
- educational: Sharpe 0.6626, CAGR 9.99%, MDD 58.35%
- vt_real:    Sharpe 0.5132, CAGR 8.80%, MDD 50.21%
- ndx_real:   Sharpe 0.9472, CAGR 18.99%, MDD 35.12%

**Step 4b — Score using `scoring.py`**:

```python
import sys
sys.path.insert(0, "studies/global_factor_tilt_loop")
from scoring import score_strategy, DatasetMetrics, Gates

metrics = {
    "educational": DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    "vt_real":     DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    "ndx_real":    DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
}
gates = {
    "educational": Gates(g1_pbo=..., g2_dsr=..., g3_wf=..., g4_oos=..., g5_fwd=..., g6_bootstrap=..., g7_crosslib=...),
    "vt_real":     Gates(...),
    "ndx_real":    Gates(...),
}
result = score_strategy(metrics, gates, cumulative_n_trials=NNNN)
# result.total_score (0-100 int)
# result.tier (Tier enum: WINNER / STRONG / PROMISING / MARGINAL / NEAR_FAIL / FAIL)
# result.winner_conditions_met (bool — strict check)
# result.criteria (dict with points per criterion)
```

**Score rubric summary** (full detail in `WINNER_AND_RANKING.md`):
- 25 pts: Sharpe edge across datasets
- 25 pts: Gate pass per dataset + cross-dataset bonus
- 15 pts: DSR significance (per-iter n_trials)
- 15 pts: CAGR floor per dataset (≥ 0.8 × benchmark)
- 15 pts: MDD ceiling per dataset (≤ benchmark + 5pp)
- 5 pts bonus: robustness (caller may add rolling-window consistency)

**Tier interpretation**:
- 🏆 **WINNER** — score ≥ 90 AND all 5 strict conditions hold AND
  beats V_HYBRID+MF + Plano C V3_1 in long-window comparison
- 🥇 **STRONG** — score 75-89
- 🥈 **PROMISING** — score 60-74
- 🥉 **MARGINAL** — score 40-59
- 📉 **NEAR_FAIL** — score 20-39
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
| educational | X (+/−Y vs 0.6626) | ... | ... | N/7 |
| vt_real     | ...                | ... | ... | N/7 |
| ndx_real    | ...                | ... | ... | N/7 |

## Long-window comparison (REQUIRED for STRONG+)
| reference | Sharpe | CAGR | MDD | strategy beats? |
|---|---|---|---|---|
| VT 1x b&h | 0.51 | 8.8% | 50.2% | ... |
| Plano C V3_1 v3.5 | 0.67 | 10.94% | 52.43% | ... |
| V_HYBRID + 10% MF | 0.74 | 10.91% | 44.71% | ... |

## Score breakdown
| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | X | 25 | ... |
| 2 Gates | X | 25 | ... |
| 3 DSR | X | 15 | ... |
| 4 CAGR floor | X | 15 | ... |
| 5 MDD ceiling | X | 15 | ... |
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
<2-3 structurally different directions>
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

Path(f"studies/global_factor_tilt_loop/iterations/{{ITERATION_N}}-*/verdict.json").write_text(
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
   - **Result:** Sharpe edu/vt/ndx, gates edu/vt/ndx, DSR p=...
   - **Score breakdown:** 1:X/25 2:X/25 3:X/15 4:X/15 5:X/15 6:X/5
   - **Lesson:** <one line>
   ```
5. **Update `## Top-K strategies ranked`** — maintain top-5 ever-scored
   across all iterations. Insert this iteration's top candidate if its
   score enters top-5.
6. If WINNER (tier=WINNER): set `status: winner` in frontmatter,
   populate `## Winners found`
7. If FAIL with new structural dead-end: append section to `DEAD_ENDS.md`,
   plus a **1-line** entry to BASE_MEMORY's `## Structural dead-ends`
   section
8. If direction consumed, move it from `## Promising unexplored
   directions` to consumed/dead state

**Generate equity-vs-benchmark plots** (mandatory for every iteration,
winner or not):

```bash
uv run python studies/global_factor_tilt_loop/plot_helper.py --iter {{ITERATION_N}}
```

Auto-detects top config per dataset; writes
`iterations/{{ITERATION_N}}-*/plot_vs_benchmark_vt_real.png` and
`...ndx_real.png`. Educational dataset is skipped by helper.
Depends on the `returns_series` key from Stage 3.

**Auto-prune rule (byte-aware)**: after writing your new entry, run
`wc -c studies/global_factor_tilt_loop/BASE_MEMORY.md`. **If > 18000 bytes**,
compress every entry in `## Iteration log` EXCEPT the latest one
to the 3-line format:

```markdown
### NNN — YYYY-MM-DD — <slug> (TIER, X/100)
- **Result:** Sharpe edu/vt/ndx X.X/X.X/X.X (Δ ±X.XX/±X.XX/±X.XX), gates N/N/N, DSR p=X.XXX (n=NNNN), winner=N/5; score 1:X 2:X 3:X 4:X 5:X 6:X.
- **Lesson:** <1-2 sentences strategic takeaway>. See `iterations/NNN-*/`.
```

---

## HARD RULES

- **NEVER modify mandate §1** (`docs/investment-mandate.md`). It stays
  MAINTENANCE 100% Plano C. Even a winner is a CANDIDATE, not
  auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2) — `[book.slug, p.X]`
  for every decision.
- **Baseline pytest must stay green** — revert any change that breaks.
- **NEVER commit to git** — shell `run_loop.sh` handles commits.
- **Max 2 h wall-time per iteration** — if running longer, save
  partial results + write final_report.md with "INCOMPLETE" status.
- **Cross-dataset non-negotiable** — synth-only edge does NOT count.
- **Stop at STAGE 5** — do NOT suggest / build paper-trading
  scaffolding (that's outside the hunt loop).
- **DO NOT TOUCH `studies/strategy_hunt_loop/` or `studies/gold_swing_loop/`** —
  parallel sessions own those directories.

---

## IF WINNER FOUND

1. `status: winner` in `BASE_MEMORY.md` frontmatter
2. Full details in `## Winners found` section
3. Final report clearly marked "🏆 WINNER"
4. `verdict.json` has `"status": "winner"`
5. Long-window comparison vs V_HYBRID+MF and Plano C V3_1 must show
   strict dominance OR explicit Pareto trade-off documentation

Shell loop `run_loop.sh` reads the flag and halts.

**Do NOT propose deployment, override, or paper trading.** That is a
user decision, made separately with the full evidence in hand.

---

## IF NOT WINNER

1. `status: iterating` in `BASE_MEMORY.md`
2. 6-field entry appended to `## Iteration log` (then auto-prune if > 18 KB)
3. `DEAD_ENDS.md` updated if structural (plus 1-line summary in BASE_MEMORY)
4. `## Promising unexplored directions` refreshed
5. Suggest 2-3 structurally different directions explicitly in the
   final_report.md's "Next iteration suggestions" section

---

Now begin with **FIRST ACTIONS** — read BASE_MEMORY.md, then
INFRASTRUCTURE.md, then DEAD_ENDS.md, then WINNER_AND_RANKING.md,
then proceed to Stage 1.
