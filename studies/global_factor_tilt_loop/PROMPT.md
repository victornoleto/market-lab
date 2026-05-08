# Global Factor-Tilt Loop — Iteration {{ITERATION_N}}

You are Claude Code resuming the **Global Factor-Tilt Loop** at
`/var/www/github/finances/market-lab`. Conversation history is empty; this prompt
+ files on disk are your only context. CLAUDE.md is auto-loaded.

**Mission**: find ONE global strategy that beats VT 1x b&h **and**
Plano C V3_1 v3.5 (S 0.671/CAGR 10.94%/MDD 52.43%, 32y) **and**
V_HYBRID+10%MF (S 0.743/CAGR 10.91%/MDD 44.71%, 32y;
P(rolling-10y<5%)=0.6%). Bar is HIGHER than VT-only — must be
structurally novel vs all 3.

If winner → set `status: winner` in `BASE_MEMORY.md` frontmatter (shell
loop halts). If not → honest log + dead-end + 2-3 next directions.

---

## REQUIRED READS (in order)

1. `studies/global_factor_tilt_loop/BASE_MEMORY.md` — state, top-K, log,
   promising directions, dead-end summaries, constraints
2. `studies/global_factor_tilt_loop/INFRASTRUCTURE.md` — simulators,
   loaders, validation, cache. **Reuse, don't rebuild.**
3. `studies/global_factor_tilt_loop/DEAD_ENDS.md` — must NOT re-test
4. `studies/global_factor_tilt_loop/WINNER_AND_RANKING.md` — strict 5
   conditions + scoring rubric + verdict.json schema
5. (only if exists) last `iterations/NNN-*/final_report.md`

CLAUDE.md, scoring.py, README.md — read on demand only when you need
them, do NOT read upfront.

---

## 5 STAGES (execute in order)

### STAGE 1 — propose ONE hypothesis

- Pick from `BASE_MEMORY.md`'s `## Promising unexplored directions`
  unless you have a documented reason to invent outside it.
- Must be structurally different from every `DEAD_ENDS.md` entry AND
  from VT/Plano C V3_1/V_HYBRID+MF.
- **Cite ≥ 1 book** from `books/summaries/` (slug from `books/MAPPING.md`).
  Web search (arXiv/SSRN/AQR/AEA) optional, any era.
- Edge source: 1 sentence — what do VT/Plano C/V_HYBRID miss that this
  captures?
- Pre-commit kill criteria: 1 specific observable that falsifies it.
- Occam first: simple version before ML/HMM/multi-signal compositions.

### STAGE 2 — write hypothesis spec

Create `studies/global_factor_tilt_loop/iterations/{{ITERATION_N}}-{{STAMP}}-<slug>/hypothesis.md`
with: hypothesis paragraph, primary citation, edge source, datasets to
test, pre-committed kill criteria, expected budget (configs, wall-time),
implementation plan. See iter 001 (when it exists) for canonical format.

### STAGE 3 — implement + test

- **Reuse infra** per `INFRASTRUCTURE.md`. Build new modules ONLY when
  the mechanism is qualitatively new — then TDD first
  (`tests/test_<slug>.py`); pytest baseline (461) must stay green.
- Test all 3 datasets: `educational` (VTSIM 56y), `vt_real` (VTSIM
  proxy 17y), `ndx_real` (QQQ 16y stretch).
- Save `iterations/NNN-*/results.json` with
  `results["returns_series"][dataset][cfg_id] = {"index": [...],
  "net_returns": [...]}` for at least the top cfg per dataset (plot
  helper depends on this).
- New simulator → also write numpy-pure reference for G7 ±3pp CAGR
  parity.

### STAGE 4 — gate battery + score

7 gates per dataset (top-5 cfgs):
- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p < 0.05 with **n_trials = configs tested THIS iter** (relaxed
  per `WINNER_AND_RANKING.md` §3) `[p.222-223]`
- G3 WF 6/8 windows + per-window MDD<25%
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 cross-lib ±3pp CAGR (mandatory for new simulators) `[p.31-34]`

Score:

```python
import sys; sys.path.insert(0, "studies/global_factor_tilt_loop")
from scoring import score_strategy, DatasetMetrics, Gates
metrics = {ds: DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...)
           for ds in ("educational", "vt_real", "ndx_real")}
gates   = {ds: Gates(g1_pbo=..., g2_dsr=..., g3_wf=..., g4_oos=..., g5_fwd=..., g6_bootstrap=..., g7_crosslib=...)
           for ds in ("educational", "vt_real", "ndx_real")}
result = score_strategy(metrics, gates, cumulative_n_trials=NNNN)
```

Tier: WINNER (≥90 + all 5 strict) / STRONG (75-89) / PROMISING (60-74)
/ MARGINAL (40-59) / NEAR_FAIL (20-39) / FAIL (<20).

### STAGE 5 — final report + memory update

- `iterations/NNN-*/final_report.md` (prose, honest): verdict, headline
  metrics table (per dataset Sharpe/CAGR/MDD vs benchmark + Δ), score
  breakdown table, long-window comparison vs VT/Plano C/V_HYBRID+MF
  (REQUIRED for STRONG+), config tested, what worked/didn't, lesson,
  citations, 2-3 next directions.
- `iterations/NNN-*/verdict.json` from `result.to_dict()` plus
  `configs_tested`, `primary_citation`, `hypothesis_slug`.
- `BASE_MEMORY.md` updates:
  1. bump `total_iterations` + `latest_iteration` + `cumulative_n_trials`
  2. append 6-field log entry to `## Iteration log` (newest first):
     `### NNN — DATE — slug (TIER, X/100)` then bullets
     `- Hypothesis:` `- Citations:` `- Scope:` `- Result:` (Sharpe
     edu/vt/ndx, gates N/N/N, DSR p) `- Score breakdown:` `- Lesson:`
  3. update `## Top-K strategies ranked` if score enters top-5
  4. WINNER → `status: winner` + populate `## Winners found`
  5. FAIL with structural insight → append to `DEAD_ENDS.md` + 1-line
     summary in BASE_MEMORY's `## Structural dead-ends`
  6. consume the `## Promising unexplored directions` entry you used
- Auto-prune: if `wc -c BASE_MEMORY.md` > 18000, compress every log
  entry except the latest to 3-line format (Result + Lesson only;
  Hypothesis/Citations/Scope recoverable from `iterations/NNN-*/`).
- Run `uv run python studies/global_factor_tilt_loop/plot_helper.py
  --iter NNN` to generate `plot_vs_benchmark_vt_real.png` +
  `plot_vs_benchmark_ndx_real.png` (mandatory).

---

## HARD RULES

- **NEVER modify `docs/investment-mandate.md`** — even a winner is a
  candidate, not auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2): every decision cites
  `[book.slug, p.X]`.
- **Pytest baseline (461) stays green** — revert breaking changes.
- **NEVER `git commit`** — `run_loop.sh` handles commits.
- **Max ~90 min wall-time per iter** — partial save + INCOMPLETE
  status if longer.
- **Cross-dataset non-negotiable** — synth-only edge ≠ winner.
- **Stop at STAGE 5** — no paper-trading scaffolding.
- **DO NOT touch** `studies/strategy_hunt_loop/` or
  `studies/gold_swing_loop/` — parallel sessions own those.

---

Begin: read BASE_MEMORY.md, then INFRASTRUCTURE.md, DEAD_ENDS.md,
WINNER_AND_RANKING.md. Then Stage 1.
