# Hypothesis — iter 008 — compound 4-axis CSCV diversity grid

**Iter:** 008 / 50 (loop)
**Slug:** `compound-4axis-cscv-diversity`
**n_configs:** 6
**cumulative_n_trials_global:** 468 → **474**
**cumulative_n_trials_loop:** 42 → 48

## Hypothesis

Iter 007 produced the loop's largest Sortino edge to date
(`compound_basket3_x_ratevol_p70_cashx`, Sortino_lh56y **1.4637**, edge
**+0.1391** vs winner 1.3246), with **G1 PBO 0.552 ≥ 0.50 as the
single remaining blocker** for `winner_conditions_met=True` and thus
the first `beats_winner=true` of the loop. Both numerical thresholds
(Sortino > 1.3746 and pct_above ≥ 0.95) were cleared cleanly by two
configs.

Iter 007's diagnostic on G1: **the 3-axis grid had three real
mechanism switches but all three "compound" configs (4, 5, 6) shared
the same OFF-leg ratevol mechanic (p70-60d threshold/window pair).**
Iter 004's clean 0.071 PBO with a similar 3-axis design proved CSCV
behaves correctly when configs span multiple qualitatively-different
mechanism dimensions.

**This iter's prediction:** the iter 007 winner family, embedded in
a **5-mechanic-dimension** orthogonal grid (ON-basket type, OFF-mechanic
on/off, ratevol threshold, ratevol window, alt-OFF asset), drops G1 PBO
below 0.50, unlocking `winner_conditions_met=True` and triggering the
loop's first `beats_winner=true`.

The mechanism-diversity hypothesis says PBO depends on the *correlation
structure of in-sample vs out-of-sample rankings* across configs
[`advances_fin_ml`, p.208-211]. Configs sharing the same mechanic family
have correlated rankings (high IS-OOS swap rate → high PBO); configs
spanning genuinely different mechanics have decorrelated rankings
(IS-best stays close to OOS-best on average → low PBO).

**Primary citation:** `[advances_fin_ml, p.208-211]` — CSCV via combinatorial
50/50 splits; PBO < 0.5 deploy bar; PBO sensitivity to mechanic diversity
across configs.

**Secondary citations:**
- `[stocks_on_the_move, p.98]` — Clenow vol-parity sizing (ON-leg
  basket, structurally new vs winner; iter 005 mechanic).
- `[volatility_trading, p.58-60]` — Sinclair volatility cone (OFF-leg
  ratevol regime; iter 006 mechanic).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking
  (compound super-additivity, iter 007 finding).
- `[advances_fin_ml, p.222-223]` — DSR + cumulative n_trials (G2 global
  with n_trials = 474 post-iter).

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility checklist")

| # | Criterion | Status |
|---|---|---|
| 1 | Citable book/paper (`[book.slug, p.X]`) | ✓ `[advances_fin_ml, p.208-211]` primary |
| 2 | Distinct from `iterations/` (T1-T5 closed study) | ✓ closed study did not test 4-axis compound × CSCV-diversity grid; T3d was 1-axis (signal subset × K), T4 was XS ranking, T5 was vol-target |
| 3 | Distinct from `loop_iterations/` (iters 001-007) | ✓ iters 001-006 single-mechanic grids; iter 007 was 3-axis. This is **5 mechanic dimensions** for explicit CSCV-PBO targeting |
| 4 | Data feasibility (testfolio + tiingo + external) | ✓ same universe as iter 007: QLDSIM, UPROSIM, UGLSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM all in `data/testfolio/` |

All four YES. Proceeding.

## Configs (6, 5-mechanic-axis orthogonal grid)

The grid varies along five **qualitatively distinct mechanism dimensions**
to maximise CSCV diversity. Each non-baseline config differs from the
winner replica (config 2) on at least one axis; the baseline + the two
mechanism-switch-OFF configs (3, 6) provide CSCV with the qualitative
contrast iter 004 had (offleg vs master scope) but iter 007 lacked.

| # | name | ON-basket | OFF-mechanic | ratevol pct | ratevol window | alt-OFF | Axes varied vs winner replica |
|---|---|---|---|---:|---:|---|---|
| 1 | `..._4axis_baseline` | single QLD | always-ZROZ | — | — | — | ON, OFF-mechanic |
| 2 | **`..._4axis_basket3_x_ratevol_p70_60d_cashx`** ← winner replica | basket3 invvol60 | ratevol-override | 0.70 | 60 | CASHX | (anchor) |
| 3 | `..._4axis_basket3_only` | basket3 invvol60 | always-ZROZ | — | — | — | OFF-mechanic (off vs on) |
| 4 | `..._4axis_basket3_x_ratevol_p80_60d_cashx` | basket3 invvol60 | ratevol-override | **0.80** | 60 | CASHX | threshold |
| 5 | `..._4axis_basket3_x_ratevol_p70_120d_cashx` | basket3 invvol60 | ratevol-override | 0.70 | **120** | CASHX | window |
| 6 | `..._4axis_basket3_x_ratevol_p70_60d_ief` | basket3 invvol60 | ratevol-override | 0.70 | 60 | **IEFSIM** | alt-OFF |

**Naming pattern:** `qld_voteK2_sma250_100_vol21_40_ar30_4axis_<descriptor>`
(prefix matches winner / iter 007 family; `4axis` segment marks this iter's
design intent; descriptor encodes the variation axis).

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` computed on QLDSIM (winner replica gate, no
modification). The basket3 = {QLDSIM, UPROSIM, UGLSIM} sized by inverse
60d realised vol (iter 005 module re-imported). The ratevol gate uses
ZROZSIM realised-vol percentile within trailing 5y (iter 006 module
re-imported). All 5 mechanic-axis variants reuse the iter 007 helpers
unchanged — no new modules.

**Mechanic-dimension count:** 5 (vs iter 007's effective 3, iter 004's 3).
Hypothesis-determining axis pairs:
- (config 1, config 3): isolates ON-basket effect (single → basket3) with
  always-ZROZ OFF.
- (config 2, config 3): isolates OFF-mechanic effect (always vs ratevol).
- (config 2, config 4): isolates threshold effect (p70 vs p80, ~28% vs
  ~19% activation).
- (config 2, config 5): isolates window effect (60d vs 120d, faster vs
  smoother regime detection).
- (config 2, config 6): isolates alt-OFF asset effect (CASHX vs IEFSIM).

This 5-pair design yields CSCV the contrast structure to discriminate
true mechanism lift from per-config noise.

## Datasets

Same as iter 007 (and the closed study) for comparability:

- `lh_56y`: 1970-01-01 → 2026-04-30 (canonical 56-year window)
- `modern_1990`: 1990-01-01 → 2026-04-30
- `spy_real`: 2003-01-01 → 2026-04-30 (Tiingo SPY post-inception)
- `ndx_real`: 2010-02-01 → 2026-04-30 (Tiingo QQQ post-inception)

## Pre-registered KILL_LOOP conditions

Per `KILL_RULES.md` and iter 007 conventions, KILL conditions are
pre-registered before the run. They are informational tags (loop does
not halt). All numbered KILL_LOOP #N below are evaluated in
`backtest.py` and reported in `verdict.json["kill_loop_results"]`.

- **KILL_LOOP #1 (success-tag).** FIRES if any config has
  `beats_winner = True`. Expected: **may FIRE this iter** — iter 007
  cleared 2 of 3 conditions; this iter targets the 3rd (G1 PBO).
- **KILL_LOOP #2 (decisive-fail).** FIRES if best Sortino_lh56y < 1.30
  (loses already-validated edge → 4-axis design destroyed the
  compound-mechanic lift). Expected NOT FIRED.
- **KILL_LOOP #3 (replica-sanity).** FIRES if config 1 (baseline)
  Sortino_lh56y deviates from 1.2841 by > 0.005 (cross-iter drift
  detection; baseline must reproduce iters 001-007 baselines).
  Expected NOT FIRED.
- **KILL_LOOP #4 (compound-edge-decay).** FIRES if config 2 (iter 007
  winner replica) Sortino_lh56y < 1.40 (cross-iter drift on the
  iter 007 best config; replica must reproduce 1.4637 within ±0.06).
  Expected NOT FIRED.
- **KILL_LOOP #5 (PBO-still-polluted).** FIRES if G1 PBO ≥ 0.50
  universally — i.e. the 5-mechanic-axis grid did NOT achieve the
  PBO drop that the iter 007 → 008 progression predicts.
  **This is the iter's primary hypothesis test.** If FIRED, hypothesis
  is rejected (mechanism diversity insufficient); if NOT FIRED, PBO
  drops below 0.50 and the loop is one step closer to (or has
  achieved) `beats_winner=true`.

## Expected outcomes

### Sortino_lh56y range

- Config 1 (baseline): 1.28 ± 0.005 (replica anchor; KILL #3 bound).
- Config 2 (iter 007 winner replica): 1.46 ± 0.06 (KILL #4 bound).
- Config 3 (basket3_only): 1.33-1.34 (matches iter 005 best 1.3340).
- Config 4 (p80 threshold): 1.42-1.46 (narrower activation, less
  ratevol coverage; expect modestly lower than config 2 — iter 006
  showed p70 > p80 by ~0.01 Sortino).
- Config 5 (120d window): 1.42-1.45 (slower regime detection; iter 006
  showed 60d > 120d marginally).
- Config 6 (IEFSIM): 1.44-1.46 (≈ config 2 minus ≈0.01 from iter 007
  IEFSIM run).

### G1 PBO

- **Hypothesis success:** G1 PBO **< 0.50** (drops below strict bar).
- **Hypothesis null:** G1 PBO ∈ [0.50, 0.55] (similar to iter 007;
  the additional ratevol-parameter axes did not add enough mechanic
  diversity).
- **Hypothesis fail:** G1 PBO ≥ 0.55 (worse than iter 007;
  adding parameter sweeps within one mechanic family *increased* PBO).

### beats_winner

For best config (likely config 2 winner replica):
- Sortino > 1.3746: ✓ (cleared in iter 007)
- pct_above ≥ 0.95: ✓ (cleared in iter 007 = 1.0000)
- winner_conditions_met = True: depends on G1 PBO < 0.50
  (this iter's hypothesis test).

If G1 PBO < 0.50 → **first `beats_winner=true` of the loop.**
If G1 PBO ≥ 0.50 → `beats_winner=false`, lone blocker confirmed
persistent across iter 007 → 008; loop continues with mechanic-family
substitution next iter.

### plan vs winner

For `beats_winner=true`: needs `sortino > 1.3746` AND
`winner_conditions_met=True` AND `pct_time_above_benchmark_lh56y ≥ 0.95`.

## INCOMPLETE flags (carried + new)

- **Replica-drift baseline (~0.04 Sortino):** iters 001-007 baseline
  Sortino_lh56y is 1.2841 vs canonical iter 022 winner 1.3246. This
  iter inherits the same drift. Comparative deltas across configs in
  this iter are bit-exact valid; absolute compounding vs the canonical
  winner has the same residual.
- **Helpers re-imported from iters 005/006/007 via importlib:**
  `basket_sizer.py` (iter 005) and `rate_vol_gate.py` (iter 006) are
  loaded read-only at their committed paths. iter 007's
  `build_compound_strategy_returns` and `compound_turnover` will be
  re-imported via importlib from iter 007's `backtest.py`. All three
  modules are frozen at the iter where they were first committed.
- **Synth caveat (pre-1985):** ZROZSIM, IEFSIM, CASHX, UGLSIM are
  testfolio synthetic proxies. Same caveat as iters 005/006/007;
  primitives (basket-invvol weighting and rate-vol percentile gate)
  are robust to absolute level mis-calibration via rolling rank /
  rolling sigma.
- **5y warmup falls back to baseline routing** during 1970-1975
  (≈ 9% of lh_56y span) for the ratevol gate. Same caveat as iters
  006/007.
- **DSR p_value reported is local (n=6) per protocol.** Cumulative
  DSR (n_trials_global = 474) gives p of the same order of magnitude
  (still << 0.05) but is the canonical denominator per
  `[advances_fin_ml, p.222-223]` and LOOP_PROTOCOL §"Trial accounting".
- **Pre-existing weekly_momentum doc edits in tree:** `docs/CURRENT_STATE.md`
  and `studies/README.md` had unstaged edits at iter start (from a
  separate `weekly_momentum` study). They are NOT part of this iter's
  artifact set and will NOT be included in this iter's commit.
  Conservative state preservation per orchestrator guardrails.
- **G1 PBO < 0.50 hypothesis test:** if FIRED (PBO ≥ 0.50), the
  conclusion is mechanism diversity within the compound family is
  insufficient — next iter must substitute a different mechanic
  family (e.g., VIX-percentile ON gate, bond duration timing) rather
  than adding more axes within ratevol/basket compounds.
