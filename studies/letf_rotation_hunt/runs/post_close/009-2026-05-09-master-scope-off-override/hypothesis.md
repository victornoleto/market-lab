# Hypothesis — iter 009 — master-scope OFF override (compound family)

**Iter:** 009 / 50 (loop)
**Slug:** `master-scope-off-override`
**n_configs:** 6
**cumulative_n_trials_global:** 474 → **480**
**cumulative_n_trials_loop:** 48 → 54

## Hypothesis

Iter 008 produced a **clean negative result**: the 5-mechanic-axis grid
with parameter sweeps inside the OFF-leg ratevol mechanic family did
**not** crack G1 PBO < 0.50 (PBO = **0.5675**, *worse* than iter 007's
0.552). The diagnostic explicitly identified that **mechanism diversity
for CSCV is structural, not parametric**: parameter variants (threshold
p70/p80, window 60d/120d, alt-OFF cashx/ief) within one mechanic family
produce highly-correlated IS-OOS rank structures, which CSCV correctly
penalises [`advances_fin_ml`, p.208-211].

Iter 008's recommendation #1 (highest expected value) for breaking the
G1 PBO 0.55 ceiling: **substitute a qualitatively different mechanic
in at least one config — specifically, master-scope OFF override**
(whole-portfolio cash override regardless of trend state, mirroring
iter 004's `master_cashx` config that produced the loop's cleanest PBO
0.071). The iter 004 finding was that the offleg-only-vs-master-scope
contrast is the **structural-diversity primitive** that decorrelates
IS-OOS rankings across configs — the level of qualitative mechanism
diversity required to break PBO.

**This iter's prediction:** taking the iter 007/008 compound winner
family (basket3 invvol60 × ratevol-p70-60d → CASHX) and substituting
**master-scope** OFF override (when ratevol fires, route the WHOLE
portfolio to alt-OFF, regardless of on_signal) for **offleg-only** OFF
override produces a 6-config grid that mixes two qualitatively different
override scopes (4 offleg/none + 2 master-scope). This structural
mechanism contrast — the same primitive iter 004 used to achieve clean
PBO 0.071 — drops G1 PBO below 0.50, unlocking
`winner_conditions_met=True` for at least one offleg-family config and
triggering the loop's first `beats_winner=true`.

The CSCV mechanism: PBO measures the fraction of IS-best configs that
rank below the median in OOS [`advances_fin_ml`, p.208-211]. When all
configs share one mechanism family, IS-best and OOS-best track each
other only weakly (parameter noise dominates), but they do co-rank
within the family — high PBO. When configs span genuinely different
mechanics, IS-best in one mechanism is unrelated to OOS-best in another,
which decorrelates the cross-config rank matrix and pushes PBO toward
0.5 from above. Iter 004 confirmed: 5 offleg + 1 master = PBO 0.071.
Iter 007 had 5 ratevol-shared + 1 single = PBO 0.552. Iter 008 had 5
ratevol-shared (parameter sweep) + 1 single = PBO 0.5675 (no
improvement). This iter: **2 master-scope + 4 offleg/none = expected
PBO < 0.50** (the structural-diversity primitive applied to compound
family).

**Important caveat (iter 004 lesson):** master-scope OFF override
risks **over-suppression** — iter 004's `master_cashx` config (corr-
gate firing 24% of days) collapsed Sortino by 28% because forcing
whole-portfolio cash during equity-positive regimes destroys
compounding (KILL_LOOP #4 fired with pct_above 0.7039 < 0.85). The
ratevol gate fires ~28% of days at p70-60d; expectation is similar
over-suppression risk. Pre-registered KILL_LOOP #6 catches this:
master-scope configs (4, 5) with pct_above_lh56y < 0.85 are tagged.
**Even if the master-scope configs themselves under-perform, their
presence in the grid is what should drop G1 PBO, allowing the offleg
configs (winner replica, threshold/window variants) to clear
`winner_conditions_met=True`.** This is the structural-diversity goal
of the iter, not a goal that the master-scope configs themselves win.

**Primary citation:** `[advances_fin_ml, p.208-211]` — CSCV via
combinatorial 50/50 splits; PBO < 0.5 deploy bar; PBO sensitivity to
**structural** mechanism diversity (vs parametric, per iter 008
finding).

**Secondary citations:**
- `[risk_parity, p.80-81, ch.4]` — Qian RORO master-gate (whole-
  portfolio risk-on/risk-off; iter 004's primary citation, providing
  the master-scope structural primitive).
- `[volatility_trading, p.58-60]` — Sinclair volatility cone (OFF-leg
  ratevol mechanic from iter 006).
- `[stocks_on_the_move, p.98]` — Clenow vol-parity sizing (ON-basket
  from iter 005).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking
  (compound super-additivity, iter 007 finding).
- `[advances_fin_ml, p.222-223]` — DSR + cumulative n_trials (G2
  global with n_trials = 480 post-iter).

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility checklist")

| # | Criterion | Status |
|---|---|---|
| 1 | Citable book/paper (`[book.slug, p.X]`) | ✓ `[advances_fin_ml, p.208-211]` primary; `[risk_parity, p.80-81, ch.4]` Qian master-gate primitive |
| 2 | Distinct from `runs/original/` (T1-T5 closed study) | ✓ closed study did not test master-scope OFF override on a compound (basket × ratevol) family; T3d was 1-axis (signal subset × K), T4 was XS ranking, T5 was vol-target |
| 3 | Distinct from `runs/post_close/` (iters 001-008) | ✓ iter 004 tested master-scope on **single-asset** trend system with **corr-gate**; this iter applies the master-scope primitive to a **multi-asset basket** with a **ratevol-gate** (compound family from iters 005/006/007). New mechanism × scope combination. |
| 4 | Data feasibility (testfolio + tiingo + external) | ✓ same universe as iters 005/006/007/008: QLDSIM, UPROSIM, UGLSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM all in `data/testfolio/` |

All four YES. Proceeding.

## Configs (6, mechanism-mix structural-diversity grid)

The grid mixes **two qualitatively different OFF-override scopes** —
4 offleg-only/none + 2 master-scope — to maximise CSCV diversity. The
6-config layout intentionally mirrors iter 004's design (5 offleg + 1
master) but applied to the compound family with 2 master configs (one
basket3, one single) to test whether master-scope alone provides
structural diversity AND whether basket+master compounds.

| # | name | ON-basket | OFF-scope | ratevol pct | ratevol window | alt-OFF | Axes varied vs winner replica |
|---|---|---|---|---:|---:|---|---|
| 1 | `..._mscope_baseline` | single QLD | none | — | — | — | ON, OFF-scope |
| 2 | **`..._mscope_winner_replica`** ← anchor (= iter 007/008 winner) | basket3 invvol60 | offleg-only | 0.70 | 60 | CASHX | (anchor) |
| 3 | `..._mscope_basket3_only` | basket3 invvol60 | none | — | — | — | OFF-scope |
| 4 | **`..._mscope_master_basket3_x_ratevol_p70_60d_cashx`** ← **NEW MECHANIC (master-scope)** | basket3 invvol60 | **master-scope** | 0.70 | 60 | CASHX | OFF-scope (master vs offleg) |
| 5 | `..._mscope_master_single_x_ratevol_p70_60d_cashx` | single QLD | **master-scope** | 0.70 | 60 | CASHX | ON, OFF-scope (master vs offleg) |
| 6 | `..._mscope_alt_off_ief` (= iter 007/008 alt_off_ief) | basket3 invvol60 | offleg-only | 0.70 | 60 | **IEFSIM** | alt-OFF |

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` computed on QLDSIM (winner replica gate).
basket3 = {QLDSIM, UPROSIM, UGLSIM} sized by inverse 60d realised vol
(iter 005 module re-imported via `importlib`). ratevol gate uses
ZROZSIM realised-vol percentile within trailing 5y at threshold 0.70 /
window 60d (iter 006 best gate, re-imported). Offleg-only compound
assembly delegated to iter 007's `build_compound_strategy_returns` and
`compound_turnover` helpers (re-imported via `importlib`). Master-scope
behaviour adds **one new helper** inside this iter dir
(`master_scope_strategy.py`) that mirrors iter 004's `master_cashx`
override semantics applied to the compound multi-asset basket.

## Datasets (frozen — same as study + iters 001-008)

| Dataset | Window | Notes |
|---|---|---|
| `lh_56y` | 1970-01-01 .. 2026-04-30 | primary (Sortino comparison vs winner) |
| `modern_1990` | 1990-01-01 .. 2026-04-30 | post-FFR-cap regime |
| `spy_real` | 2003-01-01 .. 2026-04-30 | post-Tiingo SPY |
| `ndx_real` | 2010-02-01 .. 2026-04-30 | post-Tiingo QQQ |

## Pre-registered KILL_LOOP conditions

Per `LOOP_PROTOCOL.md` §"Strategy eligibility checklist" + iter 008
pattern. KILL conditions are **informational tags** — loop continues
regardless of any KILL firing.

| # | Tag | Rule | Interpretation if FIRED |
|---|---|---|---|
| 1 | `success_tag` | Any config has `beats_winner=True` | **First beats_winner=true of the loop** ⇒ master-scope structural primitive validated. Append to `loop_winner_iter`. Capital STILL stays Plan C per mandate §1. |
| 2 | `decisive_fail` | Best Sortino_lh56y < 1.30 | Master-scope substitution destroyed compound-mechanic lift; family dies. |
| 3 | `replica_sanity` | Baseline (config 1) Sortino_lh56y deviates from 1.2841 by > 0.005 | Implementation drift in iter 007 helper or signals layer. |
| 4 | `iter007_replica_sanity` | Winner replica (config 2) Sortino_lh56y deviates from **1.4637** by > 0.005 | Iter 007 finding fails to replicate; iter 008 replication broke. |
| 5 | **`PBO_cracks`** ← positive tag | G1 PBO < 0.50 | **Hypothesis confirmed**: master-scope structural primitive is what CSCV needs. Methodologically the cleanest possible result of this iter, even without `beats_winner=true`. |
| 6 | `master_overshoot` | Master-scope configs (4 OR 5) `pct_above_lh56y` < 0.85 | Iter 004 lesson confirmed: forcing whole-portfolio cash during ratevol regime over-suppresses equity exposure. Master-scope configs themselves underperform but their **presence in the grid** still drops PBO. |

KILL_LOOP #5 (`PBO_cracks`) is intentionally a **positive tag** —
firing means the hypothesis is confirmed. KILL_LOOP #1 (`success_tag`)
fires only if a config additionally clears Sortino > 1.3746 AND
pct_above ≥ 0.95 (typically the offleg configs given iter 008's
universal pct_above 1.0000).

Both KILLs #5 and #6 firing simultaneously is the **expected outcome**
and would be the cleanest scientific result: structural-diversity
primitive cracks PBO (#5) AND master-scope itself over-suppresses (#6),
meaning the offleg-only compound configs (winner replica, alt_off_ief)
are the operative `beats_winner` candidates while the master-scope
configs are the necessary "diversity ballast" in the CSCV grid.

## Expected outcomes

### Sortino_lh56y range (gross)

| Config | Expected Sortino_lh56y | Rationale |
|---|---|---|
| 1 baseline | ~1.2841 (bit-exact iters 001-008) | sanity replica of single-QLD/ZROZ |
| 2 winner_replica | ~1.4637 (bit-exact iter 007) | iter 007 helper deterministic |
| 3 basket3_only | ~1.3340 (bit-exact iter 007) | basket3 + always-ZROZ |
| 4 master_basket3 | **1.10-1.30** (over-suppressed) | iter 004 master_cashx had Sortino 0.9252 with corr-gate at 24%; ratevol at 28% is similar activation; basket3 may partly offset gold/UPRO diversification |
| 5 master_single | **1.05-1.25** (over-suppressed) | sans basket cushion; expected closer to iter 004 master baseline |
| 6 alt_off_ief | ~1.4524 (bit-exact iter 008) | iter 008 helper deterministic |

### Comparação plan vs winner

For each non-baseline config:
- `sortino_lh56y > 1.3746` (anti-curve-fit margin)
- `winner_conditions_met=True` (G1/G2/G3/G6/G7 all pass)
- `pct_time_above_benchmark_lh56y >= 0.95`
All three must hold for `beats_winner=True`.

**G1 PBO target:** < 0.50 (the structural-diversity goal of this iter).
**G1 PBO floor (anti-disaster):** > 0.20 (iter 004 hit 0.071; if this
iter under-shoots iter 004, suspect implementation bug).

| config | sortino_lh56y target | edge_vs_winner | WC | beats_winner |
|---|---|---|:---:|:---:|
| baseline | ~1.28 | ~-0.04 | F (single-mechanic family + over-suppression) | F |
| winner_replica | ~1.46 | +0.14 | **T (target)** | **T (target)** |
| basket3_only | ~1.33 | +0.01 | F (single-mechanic) | F |
| master_basket3 | ~1.20 | -0.13 | F (over-suppressed) | F |
| master_single | ~1.10 | -0.22 | F (over-suppressed) | F |
| alt_off_ief | ~1.45 | +0.13 | **T (target)** | **T (target)** |

If 2 configs hit `beats_winner=True`, this is the loop's first such
finding. Capital remains 100% Plan C per mandate §1; outcome is
recorded in `loop_winner_iter` list and one-line note may be added to
`docs/CURRENT_STATE.md` only if score ≥ 90 + WC=Y + beats_winner=true
(per LOOP_PROTOCOL §"Mandate §1 reinforcement").

## INCOMPLETE flags (carried into iter)

- **Replica drift baseline (~0.04 Sortino):** carried over from iters
  001-008. Loop's baseline Sortino_lh56y = 1.2841 vs canonical iter
  022 winner 1.3246. Comparative deltas in this iter are bit-exact
  valid.
- **Helpers re-imported via importlib:** `basket_sizer.py` (iter 005),
  `rate_vol_gate.py` (iter 006), iter 007's `backtest.py` (compound
  assembly + turnover), iter 008's `backtest.py` (5-axis spec
  patterns) — all loaded read-only at their committed paths. New
  helper this iter: `master_scope_strategy.py`.
- **Synth caveat (pre-1985):** ZROZSIM, IEFSIM, CASHX, UGLSIM are
  testfolio synthetic proxies. Same caveat as iters 005/006/007/008;
  primitives (basket-invvol weighting, rate-vol percentile gate, master-
  scope override) are robust to absolute level mis-calibration via
  rolling rank / rolling sigma / categorical state machine.
- **5y warmup falls back to baseline routing** during 1970-1975
  (~9% of lh_56y span) for the ratevol gate. Same caveat as iters
  006/007/008. Master-scope override inherits the same warmup behaviour
  (when ratevol NaN, no master fires; baseline ON/OFF routing applies).
- **DSR p_value reported is local (n=6) per protocol.** Cumulative
  DSR (n_trials_global = 480) is the canonical denominator per
  `[advances_fin_ml, p.222-223]` and LOOP_PROTOCOL §"Trial accounting".
- **Tax / fees stress not run.** Compound configs have turnover ~15.6/y
  (vs baseline 9.3/y); master-scope configs may have higher turnover
  (gate fires regardless of trend state, so more transitions). Net-of-
  tax Sortino impact remains diagnostic, not gating.
- **Pre-existing weekly_momentum doc edits in tree:** `docs/CURRENT_STATE.md`
  and `studies/README.md` had unstaged edits at iter start (from a
  separate `weekly_momentum` study). They are NOT part of this iter's
  artifact set and will NOT be included in this iter's commit.
  Conservative state preservation per orchestrator guardrails.
- **Pre-registered hypothesis is bidirectional**: either KILL_LOOP #5
  (PBO_cracks) FIRES (structural-diversity primitive validated) or it
  doesn't (the primitive is more nuanced than iter 004 suggested).
  Both outcomes are scientifically informative; the "decisive_fail"
  KILL_LOOP #2 only fires on a complete strategy collapse.
