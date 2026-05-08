# Long-Term Portfolio Loop — Iteration {{ITERATION_N}}

You are Claude Code (or Codex CLI) resuming the **Long-Term Portfolio Loop**
at `/var/www/github/finances/market-lab`. Conversation history is empty; this prompt
+ files on disk are your only context. CLAUDE.md (and AGENTS.md for codex)
is auto-loaded.

**Mission**: find ONE long-term portfolio strategy that **beats the
average of SPY 1× b&h and VT 1× b&h** (gross-of-tax) by **≥ 0.10 Sharpe
on ≥ 2 of 3 datasets**, while passing the 7-gate battery and respecting
CAGR floor / MDD ceiling per `scoring.py`. **Iter 011 is the incumbent
winner (NTSX+GDE+KMLM 35/25/40, score 91/100); your iteration "beats the
incumbent" only when score > incumbent OR Sharpe edge ≥ +0.10 vs iter 011
on ≥ 2 datasets** — see STAGE 5 below for how to flag that.

The "average benchmark" is computed inside `scoring.py` from per-dataset
named benchmarks (`vt`, `spy`, `qqq`). For the lh_56y dataset the
threshold is roughly **avg Sharpe 0.67 + 0.10 = 0.77**; for vt_real
**0.71 + 0.10 = 0.81**; for ndx_real **0.92 + 0.10 = 1.02**. Numbers
update if `BENCHMARKS` is edited.

**Halt semantics** (run_loop.sh):
  - `status: winner` (legacy) → halt
  - `beats_incumbent: true` (set at STAGE 5) → halt with NEW WINNER message
  - Otherwise → continue hunting, log iter, repeat.

If new strict winner → set `beats_incumbent: true` AND populate
`incumbent_winner_iter` / `incumbent_winner_score` to YOUR iter (you
become the new incumbent). If not → honest log + dead-end (if structural)
+ 2-3 next directions; leave incumbent fields untouched.

**Tax model** — separate from gating: report **both gross AND net-of-tax**
metrics in `final_report.md`. Net uses `AnnualDarfEngine` (Lei 14.754/2023)
from `studies/_shared/tax_engine.py`. **Gating runs on gross numbers**
(apples-to-apples vs benchmarks). Net is a deploy-readiness diagnostic.

---

## REQUIRED READS (in order)

1. `studies/long_term_portfolio/BASE_MEMORY.md` — state, top-K, log,
   promising directions, dead-end summaries, constraints
2. `studies/long_term_portfolio/INFRASTRUCTURE.md` — simulators,
   loaders, validation, cache, tax engine. **Reuse, don't rebuild.**
3. `studies/long_term_portfolio/DEAD_ENDS.md` — must NOT re-test
4. `studies/_archive/strategy_hunt_loop/FINAL_REPORT.md` "What we
   already explored — DON'T retest" section — 15 thematic dead-end
   families inherited from the predecessor loop (57 closures)
5. `studies/long_term_portfolio/WINNER_AND_RANKING.md` — strict 5
   conditions + scoring rubric + verdict.json schema
6. (only if exists) last `iterations/NNN-*/final_report.md`

CLAUDE.md, scoring.py, README.md — read on demand only when you need
them, do NOT read upfront.

---

## 5 STAGES (execute in order)

### STAGE 1 — propose ONE hypothesis

- Pick from `BASE_MEMORY.md`'s `## Promising unexplored directions`
  unless you have a documented reason to invent outside it.
- Must be structurally different from every `DEAD_ENDS.md` entry AND
  from the 15 inherited families in
  `studies/_archive/strategy_hunt_loop/FINAL_REPORT.md` "DON'T retest".
- **Cite ≥ 1 book** from `books/summaries/` (slug from `books/MAPPING.md`).
  Web search (SSRN/AQR/arXiv/bestfolio.app) optional, any era.
- Edge source: 1 sentence — what does the avg(SPY,VT) buy-hold miss
  that this captures?
- Pre-commit kill criteria: 1 specific observable that falsifies it.
- Occam first: simple version before ML/HMM/multi-signal compositions.

**User-flagged priorities** (read once at session start —
`memory/project_long_term_portfolio_thesis.md`):
- **NTSX + GDE + KMLM static** (untested in 10 prior iters, user's
  primary preference) — 40/30/30 capital-efficient stack via
  WisdomTree + ReSolve futures overlays
- **NTSX + GDE + RSST static** (US variant)
- **NTSX + GDE + RSIT** (intl + MF variant, RSIT pre-launch ~mai/2026)
- Factor-tilt experiments (AVUS/AVDE/SPMO/IDMO/AVUV) — open question
  per user

### STAGE 2 — write hypothesis spec

Create `studies/long_term_portfolio/iterations/{{ITERATION_N}}-{{STAMP}}-<slug>/hypothesis.md`
with: hypothesis paragraph, primary citation, edge source, datasets to
test, pre-committed kill criteria, expected budget (configs, wall-time),
implementation plan.

### STAGE 3 — implement + test

- **Reuse infra** per `INFRASTRUCTURE.md`. Build new modules ONLY when
  the mechanism is qualitatively new — then TDD first
  (`tests/test_<slug>.py`); pytest baseline must stay green.
- Test all 3 datasets via `studies/long_term_portfolio/datasets.py`:
  `lh_56y` (1970-2026, KMLMSIM splice-aware via FF MoM proxy pre-1988),
  `vt_real` (VTSIM proxy 17y), `ndx_real` (QQQ 16y stretch). Use
  `from studies.long_term_portfolio.datasets import load_prices, DATASETS`
  — do NOT hardcode dataset start dates in your backtest.
- **lh_56y caveat**: any strategy using KMLM (or KMLMSIM) has its
  pre-1988 KMLM weight tracking the Ken French UMD+RF (academic equity
  momentum proxy). UMD's 1970-87 Sharpe is ~1.9, much higher than KMLM's
  long-run ~0.5 — so pre-1988 returns of KMLM-heavy strategies are
  OVERSTATED by ~3×. Disclose this in `final_report.md`'s "lh_56y caveats"
  section. Strategies WITHOUT KMLM run on lh_56y unaffected.
- Save `iterations/NNN-*/results.json` with
  `results["returns_series"][dataset][cfg_id] = {"index": [...],
  "gross_returns": [...], "net_returns": [...]}` for at least the top
  cfg per dataset. Report **BOTH** gross and net.
- Compute net using:
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path("studies").resolve()))
  from _shared.tax_engine import AnnualDarfEngine
  ```
- New simulator → also write numpy-pure reference for G7 ±3pp CAGR
  parity.

### STAGE 4 — gate battery + score (GROSS)

7 gates per dataset (top-5 cfgs), all evaluated on gross-of-tax metrics:
- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p < 0.05 with **n_trials = configs tested THIS iter**
  (relaxed per `WINNER_AND_RANKING.md` §3) `[p.222-223]`
- G3 WF 6/8 windows + per-window MDD<25% (use G3' for stacked notional > 1.05)
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 cross-lib ±3pp CAGR (mandatory for new simulators) `[p.31-34]`

Score:

```python
import sys; sys.path.insert(0, "studies/long_term_portfolio")
from scoring import score_strategy, DatasetMetrics, Gates

metrics = {
    ds: DatasetMetrics(
        sharpe=..., cagr=..., mdd=..., dsr_p_value=...,   # gross
        net_sharpe=..., net_cagr=..., net_mdd=...,         # net (informational)
    )
    for ds in ("lh_56y", "vt_real", "ndx_real")
}
gates = {
    ds: Gates(g1_pbo=..., g2_dsr=..., g3_wf=..., g4_oos=...,
              g5_fwd=..., g6_bootstrap=..., g7_crosslib=...)
    for ds in ("lh_56y", "vt_real", "ndx_real")
}
result = score_strategy(metrics, gates, cumulative_n_trials=NNNN)
```

Tier: WINNER (≥90 + all 5 strict) / STRONG (75-89) / PROMISING (60-74)
/ MARGINAL (40-59) / NEAR_FAIL (20-39) / FAIL (<20).

### STAGE 5 — final report + memory update

- `iterations/NNN-*/final_report.md` (prose, honest):
  - verdict + tier
  - **TWO headline tables**: gross metrics vs avg(SPY,VT) per dataset,
    AND net-of-tax metrics vs gross-equivalent benchmarks (informational)
  - score breakdown
  - Pareto comparison vs SPY b&h, VT b&h, and (when applicable) the
    iter 035 / iter 079 winners from `_archive/strategy_hunt_loop/`
    (REQUIRED for STRONG+)
  - configs tested, what worked/didn't, lesson, citations, 2-3 next directions
- `iterations/NNN-*/verdict.json` from `result.to_dict()` plus
  `configs_tested`, `primary_citation`, `hypothesis_slug`,
  `net_metrics` (per dataset).
- `BASE_MEMORY.md` updates:
  1. bump `total_iterations` + `latest_iteration` + `cumulative_n_trials`
  2. set frontmatter `latest_score: NN` (your iter's total_score)
  3. set frontmatter `beats_incumbent: true` ONLY if BOTH:
     (a) `latest_score > incumbent_winner_score` OR Sharpe edge ≥ +0.10
         vs the incumbent on ≥ 2 of 3 datasets,
     (b) winner_conditions_met (5 strict gates pass per scoring.py).
     Otherwise leave it `false`.
  4. append 6-field log entry to `## Iteration log` (newest first):
     `### NNN — DATE — slug (TIER, X/100)` then bullets
     `- Hypothesis:` `- Citations:` `- Scope:` `- Result:` (Sharpe gross
     lh_56y/vt/ndx + Δ vs avg, gates N/N/N, DSR p) `- Net (informational):`
     (Sharpe net) `- Score breakdown:` `- Lesson:`
  5. update `## Top-K strategies ranked` if score enters top-5
  6. NEW WINNER (beats_incumbent=true) → update `## Incumbent winner` to
     YOUR iter; promote prior incumbent into `## Top-K strategies ranked`
  7. FAIL with structural insight → append to `DEAD_ENDS.md` + 1-line
     summary in BASE_MEMORY's `## Structural dead-ends`
  8. consume the `## Promising unexplored directions` entry you used
- Auto-prune: if `wc -c BASE_MEMORY.md` > 18000, compress every log
  entry except the latest to 3-line format.
- Run `uv run python studies/long_term_portfolio/plot_helper.py
  --iter NNN` to generate `plot_<dataset>.png` +
  `plot_rolling_windows_<dataset>.png` for each of lh_56y/vt_real/ndx_real
  (6 PNGs total, mandatory).

---

## HARD RULES

- **NEVER modify `docs/investment-mandate.md`** — even a winner is a
  candidate, not auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2): every decision cites
  `[book.slug, p.X]`.
- **Pytest baseline stays green** — revert breaking changes.
- **NEVER `git commit`** — `run_loop.sh` handles commits.
- **Max ~90 min wall-time per iter** — partial save + INCOMPLETE
  status if longer.
- **Cross-dataset non-negotiable** — synth-only edge ≠ winner.
- **Stop at STAGE 5** — no paper-trading scaffolding.
- **Net-of-tax via `_shared/tax_engine.py`** (AnnualDarfEngine, Lei
  14.754/2023). Net is informational; gating uses gross.
- **DO NOT touch** `studies/_archive/`, `studies/_shared/`, or
  `studies/global_factor_tilt_loop/` — archive is read-only;
  `_shared/` is canonical infra; `global_factor_tilt_loop/` is FROZEN.

---

Begin: read BASE_MEMORY.md, then INFRASTRUCTURE.md, DEAD_ENDS.md,
WINNER_AND_RANKING.md, plus the "DON'T retest" section in
`studies/_archive/strategy_hunt_loop/FINAL_REPORT.md`. Then Stage 1.
