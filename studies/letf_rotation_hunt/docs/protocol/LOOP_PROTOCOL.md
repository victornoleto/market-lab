# LOOP PROTOCOL — letf_rotation_hunt post-close strategy hunt

Operational rules for the autonomous loop driven by `loop.sh` + `LOOP_PROMPT.md`.
Read once before designing/extending the loop; per-iter agents read this in
PASSO 1 of the prompt.

## Naming

- **Iter dir:** `runs/post_close/NNN-YYYY-MM-DD-<slug>/`
  - `NNN` zero-padded 3 digits (001, 002, …, 099, 100). Loop targets 50 iters
    cumulative (`target_total_iterations` in `LOOP_MEMORY.md` frontmatter).
  - `YYYY-MM-DD` = UTC date the iter was started.
  - `<slug>` = kebab-case, max ~40 chars, descriptive of strategy family
    (e.g., `gold-momo-monthly`, `vix-percentile-on-spy`, `cross-asset-trend`).
- **Per-iter required artifacts** (mirror of `runs/original/014-2026-05-06-T3d-vote-of-k/`):
  - `hypothesis.md` (pre-commit: written BEFORE running anything)
  - `backtest.py` (per-iter custom; imports shared modules)
  - `verdict.json` (validates against `loop_verdict_schema.json`)
  - `SUMMARY.md` (mirrors `runs/original/014.../SUMMARY.md` structure +
    new "Comparação vs winner" section)
  - `plots/01_equity_curves.png` … `07_crisis_attribution.png`
  - `tables/per_config_metrics.csv`
  - `tables/gates_pass_fail.csv`
  - `logs/` (optional; per-config debug logs)

## Strategy eligibility checklist (PASSO 3 of prompt)

Before pre-committing `hypothesis.md`, the agent must answer YES to all four:

1. **Citable book/paper:** primary citation in `[book.slug, p.X]` or `[ch.Y]`
   format. Source must be in `books/summaries/<slug>.md` or `knowledge/`.
   No citation → reject.
2. **Distinct from `runs/original/`:** the strategy family is not already covered
   by the closed study (T1 single-LETF Gayed, T2 HFEA basket, T3 composite
   signal, T4 cross-sectional Clenow/EWMAC, T5 Carver vol-target). Variants
   inside those families that were *not* tested in iters 001-025 are allowed
   only if they introduce a genuinely new signal mechanic.
3. **Distinct from `runs/post_close/`:** read `LOOP_MEMORY.md` iter log; list
   slugs/tiers already explored. Avoid trivial variants of recent iters.
4. **Data feasibility:** universe and required series are available in
   `data/testfolio/`, `data/tiingo/daily/`, or `data/external/`. New external
   data sources must be documented (provenance, license, date range).

## Config budget (anti-DSR-inflation)

- **n_configs per iter ≤ 8.** Soft cap ≤ 6 preferred. DSR penalty grows with
  cumulative trials `[advances_fin_ml, p.222-223]`; a small grid that
  unambiguously decides the hypothesis beats a large grid that triggers
  DSR-fail by construction.
- **DSR trial denominator is global.** `LOOP_MEMORY.md` starts from the closed
  study count (`closed_study_cumulative_n_trials: 426`) and each iter adds its
  config count to `cumulative_n_trials_loop` and `cumulative_n_trials_global`.
  Local-only DSR can be reported as diagnostic, but `beats_winner=true` requires
  the global-trials DSR to pass.
- **Symmetric naming** within the iter (e.g.,
  `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` style) so configs differ in
  exactly one dimension at a time (param sweep, not multi-axis).

## Beats-winner test (FROZEN)

Hard-coded in every iter's `backtest.py`:

```python
beats_winner = (
    sortino_lh56y > 1.3746          # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met       # all WINNER strict bars met
    and pct_time_above_benchmark_lh56y >= 0.95
)
```

`sortino_edge_vs_winner = sortino_lh56y - 1.3246` (raw edge; can be negative).

`winner_benchmark_sortino = 1.3246` (immutable for the duration of the loop;
if the user later wants to advance the benchmark, requires explicit edit
of `LOOP_MEMORY.md` frontmatter + this protocol).

Every `verdict.json` must include the evidence fields that make this auditable:
`sortino_lh56y`, `winner_conditions_met`,
`pct_time_above_benchmark_lh56y`, `sortino_edge_vs_winner`,
`winner_benchmark_sortino`, and `beats_winner_threshold_sortino`.

## Phase 3 objective — performance-first (iters 011+)

Phase 3 starts after the first 10-loop report. The user preference is explicit:
T3d-K2 already has acceptable safety, so the next loop phase must not optimize
for lower drawdown or higher Sortino at the cost of weaker compounding. The
objective is to find a strategy that remains statistically robust while also
beating T3d-K2 on performance.

Phase 3 diagnostics required in every iter 011+:

- `cagr_lh56y` and `cagr_edge_vs_winner` against T3d-K2 CAGR 31.08%.
- `end_equity_ratio_vs_winner` against T3d-K2 terminal equity.
- Rolling end-equity win rates vs T3d-K2 over 1y/3y/5y/10y.
- `phase3_performance_candidate = true/false`, where true means at minimum:
  `cagr_lh56y > 0.3108`, `end_equity_ratio_vs_winner > 1.05`,
  `sortino_lh56y >= 1.20`, PBO < 0.5, and global DSR p < 0.05.

These are performance diagnostics and research prioritization criteria, not a
mandate override. Any later deployment still requires user-driven mandate §7.
The statistical controls remain anchored in CSCV/PBO and global DSR
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Phase 4 objective — focused iter 017 validation/refinement (iters 021+)

Phase 4 is not a broad hunt. The research incumbent is iter 017's post-crash
rearm family (`T40D60`). Each iter must test the anchor's robustness or a small
mechanistically justified improvement.

Required Phase 4 diagnostics:

- Compare every best config against both T3d-K2 and the iter 017 anchor.
- Report `cagr_edge_vs_iter017`, `sortino_edge_vs_iter017`,
  `end_equity_ratio_vs_iter017`, and rolling 1y/3y/5y/10y win rates vs iter 017.
- Include at least one anchor replica unless the iter is explicitly an
  independent implementation/cross-check.
- Prefer mechanism-diverse grids; avoid pure param sweeps that cluster ranks and
  inflate PBO, as seen in iter 018 `[advances_fin_ml, p.208-211]`.
- A candidate is a Phase 4 improvement only if it improves CAGR or terminal
  equity versus iter 017 while keeping Sortino >= 1.35, PBO < 0.5, and global
  DSR p < 0.05.
- Lower drawdown alone is not a Phase 4 success.

Allowed Phase 4 families:

- `T_crash` / `D_arm` local sensitivity with 6-8 max configs.
- Ablation of rearm vs TQQQ vs OFF-duration vs crash-depth mechanics.
- Event-level flip audits and subperiod robustness.
- Independent implementation parity of the iter 017 return stream.
- Small performance overlays during the rearm window only, if pre-registered and
  cited.

## Soft-halt hint (advisory; not enforced by shell)

If 5 consecutive iters all return tier_label ∈ {NEAR_FAIL, FAIL} AND no config
in any of those 5 had `sortino_edge_vs_winner > -0.1` (i.e., not even close),
the next iter's agent should:

1. Note the run of failures in `LOOP_MEMORY.md` iter log.
2. Pick a deliberately different strategy family (regime change — if last 5
   were trend-based, try mean-reversion; if last 5 were equity-only, try
   cross-asset).
3. If 10 consecutive failures, write a brief `runs/post_close/.PAUSE_HINT.md`
   recommending the user stop the loop and reassess. The shell does not act
   on this file; it's advisory for the next human review.

The shell loop runs MAX_ITER no matter what — only timeouts (exit 124) or
hard errors (exit ≠ 0) abort.

## Mandate §1 reinforcement

**Never** treat `beats_winner=true` as a deploy signal. Capital remains 100%
Plano C per mandate §1 (MAINTENANCE MODE since 2026-04-23). Even if multiple
iters bat the threshold, the loop only:

- Records `beats_winner: true` in `verdict.json` and `LOOP_MEMORY.md`.
- Appends to `loop_winner_iter` list in frontmatter.
- Optionally adds a one-line note in `docs/CURRENT_STATE.md` under "Active
  Hunts" if a candidate is genuinely promising (score ≥ 90 + WC=Y +
  beats_winner=true).

Promotion to deploy ⇒ user-driven mandate §7 override request, exactly as
`spy_beater_hunt/SESSION_PROMPT.md` deploy escalation note. The loop never
short-circuits this.

## Scope limits (anti-scope-creep)

- Each iter = ONE strategy family + its configs. No "test 3 unrelated
  hypotheses in one iter."
- **No refactors of the closed study.** `gates.py`, `scoring.py`,
  `plot_helper.py`, `data_loader.py`, `signals.py`, `signals_carry.py`, `synths.py`,
  `tax_layer.py`, `kill_rules.py`, `verdict_schema.json` are all read-only
  from the loop's perspective. If a bug is found in those, file a separate
  issue/PR — do not patch mid-iter.
- New helpers/signals introduced by an iter live INSIDE the iter dir
  (e.g., `runs/post_close/003-.../my_signal.py`) unless promoted later by a
  separate user-driven decision.
- Tests for new modules go in `tests/test_letf_rotation_hunt_loop_NNN.py`
  and must NOT regress the baseline (mandate §3: ≥ 813 tests passing).

## Commit conventions

- Conventional Commits: `feat(letf-loop): iter NNN — <slug> — Sortino X.XXX (edge ±YY) [tier_label]`
- Body must include:
  - KILL pre-conditions disparadas (FIRED) / não-disparadas (NOT FIRED)
  - `beats_winner: true/false`
  - 1-2 lines on next-iter ideas (closed direction or open variants)
  - Citations in `[book.slug, p.X]` form
- `git add` specific paths only — never `-A` or `.` (avoids accidental
  inclusion of secrets / artifacts).

## When to extend / pause this loop

- **Extend `target_total_iterations`** beyond 50 only if (a) ≥ 1 iter has
  `beats_winner=true` AND (b) the user explicitly approves. Default is to
  stop at 50 and write a final `runs/post_close/FINAL_REPORT.md`.
- **Pause** anytime — the loop is fully resumable. State lives in
  `LOOP_MEMORY.md` frontmatter (`total_iterations`) and the numbered iter
  dirs. Re-running `bash loop.sh` picks up at the next safe number from
  `total_iterations + 1`, skipping any higher-numbered partial iter directory
  to avoid collisions.

## References

- `BASE_MEMORY.md` — closed study record (read-only)
- `runs/original/014-2026-05-06-T3d-vote-of-k/SUMMARY.md` — canonical iter
  report template
- `runs/original/022-2026-05-06-T3d-extended-grid/` — winner iter (benchmark)
- `WINNER_AND_RANKING.md` — scoring rubric (criterion 1 Sortino-first)
- `KILL_RULES.md` — study-level KILLs (informational for loop)
- `studies/spy_beater_hunt/SESSION_PROMPT.md` — sister-loop reference
- `studies/day_swing_strategy_hunt/loop.sh` — multi-backend shell pattern
