# studies/ — research loops & legacy archive

This directory holds **strategy-research loops** (active + frozen) and an
archive of closed studies.

## Active

### `long_term_portfolio/` (active 🟡 pending scoring rework)
- **Mission**: find an efficient long-term portfolio whose net-of-tax
  Sharpe beats SPY 1× b&h and VT 1× b&h on 2/3 datasets.
- **Status**: 10 iters run (codex-cli, 2026-04-28). 0 winners — but
  scoring.py uses iter-009 *gross* benchmarks vs candidate *net*-of-tax
  → apples-to-oranges. Needs rework before next iter.
- **Renamed from** `bestfolio_hunt_loop/` on 2026-04-28.
- Entry: `BASE_MEMORY.md` (frontmatter shows `status:
  pending_scoring_rework`), `PROMPT.md`, `README.md`, `RUN_WITH_CODEX.md`.

### `global_factor_tilt_loop/` (FROZEN ❄️)
- **Mission**: find global strategy beating VT 1× b&h + Plano C V3_1
  v3.5 + V_HYBRID+MF on real data.
- **Status**: 14 iters, 6 winners. iter 009 (HAA+Gold) = Sharpe Pareto
  frontier (S=1.120 edu, gross-of-tax). iter 013 (HAA+ZROZ) = CAGR
  frontier. iter 014 = annual-DARF rerun (proves rotation is tax-neutral
  under Lei 14.754).
- **Why kept active**: predecessor of `long_term_portfolio/`; iter 014's
  `tax_engine_v2.py` is the canonical source for `_shared/tax_engine.py`.
- Entry: `BASE_MEMORY.md`, `README.md`.

## Shared infrastructure

### `_shared/`
- `tax_engine.py` — `AnnualDarfEngine` (Lei 14.754/2023). Used by all
  net-of-tax analyses. See `_shared/README.md` for usage.

## Archive

### `_archive/strategy_hunt_loop/` (closed ✅ winner found)
- **Mission**: beat SPY 1× b&h Sharpe ≥ 0.10 on 17y window.
- **Status**: 78 iters, **1 strict winner (iter 079)** + 4 strong
  deploy candidates. **Loop self-halted at iter 079.**
- **Read**: `FINAL_REPORT.md` (1 100+ lines) — covers top strategies,
  deploy guide for 4 portfolios (V0 IBKR margin, V1 NTSX+GDE 67/33, V2
  2× LETF, V3 3× LETF), post-tax analysis, Lei 14.754 tax model,
  broker decision matrix, **and the full "DON'T retest" consolidated
  dead-ends section** (15 thematic groups covering 57 individual iter
  closures).
- 5 winning iters preserved verbatim under `WINNER/`:
  iter 006 (vol-managed 60/40), 016 (static-stack VM hybrid), 035
  (static-stack 90/60/30), 074 (016+064 ensemble), 079 (multi-asset
  top-K momentum).
- `deploy_studies/` retained — variant validators (iter 035 4-way,
  iter 079 leveraged) + aporte simulation.
- **Original 78 iter dirs deleted** (~248M, agg cleanup).

### `_archive/gold_swing_loop/` (paused ⏸️ structural ceiling)
- **Mission**: beat gold-complex buy-hold Sharpe by ≥0.10 across hold
  buckets and cost paths.
- **Status**: 25 iters across 2 phases (15 v1 + 10 v2 relaxed). 0 winners.
  Best score 50/100 (vol-regime-inverse axis, iters 011/012/013) —
  swing-extended hold (22-44d) failed legacy ≤5d gate. Phase 2 relaxation
  made scores LOWER on average — gold standalone is structurally limited.
- **Read**: `FINAL_REPORT.md` — full top-K, what-was-tested per phase,
  recommendation for future reactivation (pivot to gold-as-sleeve), state
  preservation for resume.
- **Original 25 iter dirs deleted**.

### `_archive/ema_sma_threshold_*` (Phase 1 legacy ❌ all FAIL)
4 dirs (`crash_protected`, `educational`, `nasdaq_real`, `spy_real`)
covering the EMA/SMA threshold trend-follow + LETF + crash-signal sweep
that opened the project. **0/4020 configs passed** the 7-gate cross-dataset
battery. Documented in detail under
`_archive/strategy_hunt_loop/DEAD_ENDS.md` "From iteration 001".
- **Read**: `phase3_FINAL.md` (`crash_protected/`), `FINAL.md` (others).
- **Heavy data deleted** (analyses/, configs/, deep_review/, sweep
  runners). Final summary docs preserved.

### `_archive/docs/`
- `crashes_sp500_e_indicadores_preditivos.md` — historical research note
  on SPY crash predictors.
- `SPEC_crash_protection_evolution.md` — spec lineage doc for the
  crash-protection family.

---

## How to navigate this directory

### "I want to understand what was tried so far"
Read `_archive/strategy_hunt_loop/FINAL_REPORT.md` first — it covers
both the strategies that worked AND the major dead-end families. Then
`_archive/gold_swing_loop/FINAL_REPORT.md` for the gold-standalone
side. Skip `ema_sma_threshold_*` unless investigating Phase 1
specifically.

### "I want to continue the long-term-portfolio search"
1. Read `long_term_portfolio/BASE_MEMORY.md` (frontmatter + log).
2. Read `long_term_portfolio/RUN_WITH_CODEX.md` (operational).
3. Read `_archive/strategy_hunt_loop/FINAL_REPORT.md` "DON'T retest"
   section to skip 57 already-closed dead-end families.
4. **Before relaunching**: rework `scoring.py` to use SPY/VT
   net-of-tax benchmarks (not iter 009 gross). See BASE_MEMORY.md
   `note:` field for the issue.

### "I want to find a specific iter result"
- Active loops: `long_term_portfolio/iterations/NNN-*/`,
  `global_factor_tilt_loop/iterations/NNN-*/`.
- Archived strategy_hunt_loop winners: `_archive/strategy_hunt_loop/WINNER/iter_NNN-*/`.
- All other archived iter dirs: **DELETED** (raw data not preserved;
  conclusions in FINAL_REPORT.md / DEAD_ENDS.md).

---

## Disk footprint (post-cleanup, 2026-04-28)

| dir | size | type |
|---|---:|---|
| `_archive/strategy_hunt_loop/` | 43M | docs + 5 winners + deploy_studies |
| `_archive/gold_swing_loop/` | <1M | docs only |
| `_archive/ema_sma_threshold_*` | <1M | summary docs only |
| `_archive/docs/` | <1M | loose specs |
| `_shared/` | <1M | tax engine |
| `global_factor_tilt_loop/` | 50M | FROZEN, full state preserved |
| `long_term_portfolio/` | 32M | active, 10 iter dirs |
| **Total** | **~126M** | (was ~390M before cleanup) |
