# 007-2026-05-09 — compound: ratevol-OFF × invvol-ON-basket

**Iter:** 007 / 50 (loop)
**Slug:** `compound-ratevol-off-x-invvol-on-basket`
**n_configs:** 6 (≤ 8 budget; soft cap 6 hit)
**cumulative_n_trials_global before/after:** 462 → **468**
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** `loop_iter_007`

---

## Hypothesis

The two prior loop iters with positive Sortino edge over the closed-study
winner (T3d-K2 `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`, Sortino_lh56y
1.3246) operate on **structurally orthogonal** sides of the strategy:

- **Iter 005** (`multi-asset-on-invvol`) replaced the **ON leg** with a
  3-asset basket {QLD, UPRO, UGL} sized by inverse 60d realised vol —
  Sortino_lh56y **1.3340** (edge **+0.0094**). Cross-asset *first*-moment
  diversification on the equity side. Citation: `[stocks_on_the_move, p.98]`
  (Clenow vol-parity sizing) + `[systematic_trading, ch.10]` (Carver inverse
  vol).

- **Iter 006** (`bond-ratevol-regime`) replaced the **OFF leg** during
  bond-stress regimes (ZROZ realised-vol percentile > 70th of 5y trailing
  window) with CASHX (FFR proxy) — Sortino_lh56y **1.3386** (edge
  **+0.0140**, the loop's current maximum). Own-asset *second*-moment
  regime detection on the duration side. Citation:
  `[volatility_trading, p.58-60]` (Sinclair on the volatility cone).

Both also delivered **substantial G5 FWD post-2020 Sharpe lift** (iter 005:
0.86–0.90; iter 006: 0.86–0.94 vs winner-replica baseline 0.71) — two
independent evidences that the closed-study winner has a real published-
edge-decay problem in the 2020+ regime.

**Compound hypothesis:** if the two effects are genuinely orthogonal —
ON-leg diversification touches the *equity-bull regime contribution*,
OFF-leg ratevol gating touches the *bond-stress regime contribution* — they
should **compound** rather than conflict, producing a Sortino edge in the
neighbourhood of `+(0.0094 + 0.0140) ≈ +0.023` over the winner benchmark
(naive additive prior). Even a conservative half-additivity of ~+0.012 over
the winner benchmark would be the loop's new edge maximum.

**Secondary hypothesis (G1 PBO):** iter 005 G1 PBO was **0.881** (single
mechanic family), iter 006 was **0.798** (3-axis grid but single mechanic
family — pct × vol_window × alt-asset within the ratevol gate). Iter 004's
G1 PBO 0.071 — the cleanest of the loop — was achieved with three axes
including a **real mechanism switch** (offleg vs master scope). This iter's
**3-axis orthogonal grid spans a real mechanism switch (ON-side ↔ OFF-side
mechanic)**, which should drop PBO closer to iter 004 levels — a structural
break of the universal G1 ceiling that has blocked `winner_conditions_met=True`
for every loop iter so far.

**Citation chain:**
- `[stocks_on_the_move, p.98]` — Clenow vol-parity sizing (ON-leg basket).
- `[volatility_trading, p.58-60]` — Sinclair volatility cone (OFF-leg ratevol).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking rationale
  for compounding mechanically-orthogonal lifts.
- `[systematic_trading, ch.10]` — Carver inverse vol (basket sizing).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1 hypothesis).
- `[advances_fin_ml, p.222-223]` — DSR + cumulative n_trials (G2 global).

---

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility checklist")

1. **Citable book/paper:** YES — primary citation `[stocks_on_the_move,
   p.98]` plus `[volatility_trading, p.58-60]`. Both used in iters 005/006
   already; reuse is intentional (this iter is *the compound*).
2. **Distinct from `iterations/`:** YES — closed-study iters 014/022 use
   single-asset QLD ON + always-ZROZ OFF; iter 023 tested multi-asset
   {UPRO/QLD/TQQQ} but never with a regime-conditional OFF override. No
   closed-study config combines basket-ON + ratevol-OFF.
3. **Distinct from `loop_iterations/`:** YES — iter 005 is single-mechanic
   ON-only; iter 006 is single-mechanic OFF-only. This iter is the first
   **compound** test.
4. **Data feasibility:** YES — all data already loaded in iters 005/006
   (QLDSIM, UPROSIM, UGLSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM via testfolio
   cache). No new external dependencies.

---

## Configs (6, 3-axis orthogonal grid)

Naming convention shared with iters 005/006:
`qld_voteK2_sma250_100_vol21_40_ar30_<axis-summary>`. Variation moves along
**one mechanic axis at a time**; configs 3-6 isolate the compound effect.

| # | Name | ON leg | OFF leg | Axis varied vs prior |
|---|------|--------|---------|----------------------|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_compound_baseline` | single QLD | always ZROZ | — (winner replica anchor; bit-exact 1.2841 expected) |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_compound_ratevol_only` | single QLD | ratevol-p70-60d → CASHX | OFF mechanic ON (= iter 006 best) |
| 3 | `qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_only` | basket3 {QLD, UPRO, UGL} invvol60 | always ZROZ | ON mechanic ON (= iter 005 best) |
| 4 | **`qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_x_ratevol_p70_cashx`** | basket3 invvol60 | ratevol-p70-60d → CASHX | **KEY compound test (both ON)** |
| 5 | `qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_x_ratevol_p70_ief` | basket3 invvol60 | ratevol-p70-60d → IEFSIM | alt-OFF asset sensitivity |
| 6 | `qld_voteK2_sma250_100_vol21_40_ar30_compound_basket2_qld_ugl_x_ratevol_p70_cashx` | basket2 {QLD, UGL} invvol60 | ratevol-p70-60d → CASHX | basket-composition sensitivity |

**Why these 6 (and no more):**
- Configs 1-3 are mandatory as decomposition anchors so we can attribute
  any compound lift to the cross-product, not to either factor alone.
- Config 4 is the canonical compound test (both best mechanics from prior
  iters, paired together).
- Configs 5-6 vary one secondary axis each (alt-OFF asset; ON basket
  composition) — directly testing the robustness of the compound effect to
  structural choices. **Three real mechanism switches across the 6 configs:**
  (a) ON-leg type (single vs basket2 vs basket3), (b) OFF-mechanic
  (always vs ratevol), (c) alt-OFF asset (CASHX vs IEFSIM). This mirrors
  iter 004's clean 3-dim mechanism-switch grid that achieved G1 PBO 0.071.

**Trial budget:** local n=6 (within ≤ 8 cap; matches iters 005/006).

---

## Datasets

Same as iters 005/006 (same as closed-study winner, for direct
comparability):

| Dataset | Window | Notes |
|---------|--------|-------|
| lh_56y | 1970-01-01 → 2026-04-30 | Primary. Sortino headline metric. |
| modern_1990 | 1990-01-01 → 2026-04-30 | Pre-Tiingo modern era. |
| spy_real | 2003-01-01 → 2026-04-30 | Tiingo SPY real-data window. |
| ndx_real | 2010-02-01 → 2026-04-30 | Tiingo QQQ real-data window. |

---

## Pre-registered KILL conditions (KILL_LOOP for iter 007)

These are **anti-p-hacking pre-commits**. KILLs are informational; the
loop continues regardless. Numbered to match iter convention.

- **KILL_LOOP #1 (success-tag):** **FIRES** if and only if **best config**
  has `sortino_lh56y > 1.3746` AND `winner_conditions_met = True` AND
  `pct_time_above_benchmark_lh56y >= 0.95`. Triggers `beats_winner=true`
  in `verdict.json`. (Frozen loop-wide threshold per LOOP_PROTOCOL.)

- **KILL_LOOP #2 (decisive-fail):** **FIRES** if all 5 non-baseline
  configs have `sortino_lh56y < 1.10` (well below LETF rotation
  meaningful range). Would mean the compound family is dead. Floor 1.10
  is iter-level convention.

- **KILL_LOOP #3 (replica-sanity):** **FIRES** if config 1 (baseline,
  `compound_baseline`) Sortino_lh56y deviates from canonical 1.2841 (loop
  baseline) by > 0.005 absolute. Sanity check: a non-bit-exact baseline
  would invalidate cross-config delta comparisons.

- **KILL_LOOP #4 (compound-non-additivity):** **FIRES** if the canonical
  compound config (config 4, `basket3_x_ratevol_p70_cashx`) Sortino_lh56y
  is **lower than max(config 2 ratevol-only, config 3 basket3-only)** by
  more than 0.02 (i.e., the compound is *worse* than either isolated
  mechanic by a meaningful margin). This is the central scientific test
  of the iter: are the two effects orthogonal (compound) or do they
  conflict (one over-trumps the other)?

- **KILL_LOOP #5 (PBO-still-polluted):** **FIRES** if G1 PBO ≥ 0.50 for
  any config (i.e., the 3-axis mechanism-switch grid did not break the
  ceiling). This contradicts the secondary hypothesis above, suggesting
  a 4th orthogonal axis is needed for clean PBO. (Iters 005 0.881 / 006
  0.798 / 003 0.444 / 004 **0.071** baseline.)

---

## Expected outcomes

- **Sortino_lh56y range (best config):** [1.32, 1.36] under naive
  additivity (1.2841 baseline + 0.014 ratevol + 0.009 basket3 ≈ 1.307;
  generous additivity could reach 1.34+); under sub-additivity / partial
  conflict [1.30, 1.34]; under positive interaction (cross-asset basket
  + duration-stress dodge mutually reinforce) up to 1.37+. **Worth
  flagging:** even the optimistic prior 1.37 would marginally clear
  beats_winner_threshold_sortino 1.3746.

- **G1 PBO:** under hypothesis, [0.05, 0.30] — drop closer to iter 004's
  0.071 because the grid spans a real mechanism switch (ON-side ↔
  OFF-side). Under null (compound is just another single-mechanic
  family), [0.50, 0.85] — same range as iters 005/006.

- **G5 FWD post-2020 Sharpe:** [0.85, 1.05]. Naive expectation is that
  both mechanics' independent G5 lifts (each ≈ +0.15-0.20 over baseline
  0.71) compound. If only one effect survives, [0.85, 0.95] band; if
  both compound additively, [0.95, 1.05]+.

- **Crisis attribution (count of 4):** likely 1/4 to 2/4. The
  basket3 mechanic adds 2020_COVID rescue (iter 005 finding via UGL gold
  complement during USD-strength); ratevol adds NO canonical-window
  rescue (iter 006 found it improves daily downside variance, not
  binary crisis flags). So compound config likely 2/4 (2008 + 2020),
  matching iter 005's crisis count.

- **Compounding signature:** if config 4 Sortino > both isolated
  configs (2, 3) AND > baseline (1) by a sum-of-deltas margin, the
  effects compound. If config 4 ≤ max(2, 3), they conflict (one dominates
  or substitutes). The decisive answer requires the 3-anchor decomposition
  (configs 1-3-4, with config 2 as the OFF-only branch).

- **Comparison plan vs winner:**
  ```
  beats_winner = (
      sortino_lh56y > 1.3746
      AND winner_conditions_met = True
      AND pct_time_above_benchmark_lh56y >= 0.95
  )
  ```
  Best chance: config 4 if compounding holds. Realistic expectation:
  positive edge (likely loop maximum) but PBO blocker remains; if PBO
  drops below 0.50 AND Sortino > 1.3746, **first beats_winner=true** in
  the loop. Subjective probability: ~10-15% (compound prior gives ~30%
  chance to clear Sortino threshold AND 30% chance to clear PBO; joint
  ~9% under independence assumption).

---

## INCOMPLETE flags

- **Replica drift baseline (≈ -0.04 Sortino vs canonical):** carried
  over from iters 001-006. Loop's baseline Sortino_lh56y is 1.2841 vs
  canonical iter 022 winner 1.3246. Documented cause: loop's data-loading
  warmup boundary differs from iter 022 by ~248 days. **All comparative
  deltas across configs in this iter are bit-exact valid** (same loader);
  cross-iter comparison vs winner uses 1.3246 anchor as protocol
  mandates.
- **Helpers re-imported from iters 005/006:** `basket_sizer.py` (iter 005)
  and `rate_vol_gate.py` (iter 006) are imported via `importlib.util` at
  their committed paths. Both modules are frozen (committed in iters
  005/006); iter 007 does not modify them. If a future iter modifies them
  in their original paths, iter 007's results would change accordingly —
  but since prior iters are committed and read-only by convention, this
  is acceptable.
- **5y warmup falls back to baseline routing** during 1970-1975 (≈ 9% of
  lh_56y span). The override is genuinely active only over 1975-2026.
  Same caveat as iter 006.
- **Synth caveat (pre-1985):** ZROZSIM, IEFSIM, CASHX are testfolio
  synthetic treasury proxies. Pre-1985 vol structure inherits the synth
  assumptions; the percentile-rank primitive (rate-vol gate) and the
  inverse-vol weighting primitive (ON-leg basket) are both robust to
  absolute level mis-calibration (they use rolling rank / rolling sigma).
- **G1 PBO 3-axis design:** the grid intentionally spans 3 mechanism
  switches (ON-leg type, OFF-mechanic, alt-OFF asset). However, all 3
  compound-active configs (4, 5, 6) share the OFF mechanism (ratevol-p70-
  60d). If PBO remains high it would suggest CSCV is detecting the shared
  ratevol mechanic across rotations even with the 3-axis design.
- **Tax/fees:** gross only this iter (matching closed-study convention).
  The compound config has both basket-rebalance turnover AND
  ratevol-state-change turnover; gross-Sortino lift may compress
  meaningfully under net analysis. Reported as diagnostic but not gating.
- **Naive additive prior may overstate:** the additive +0.023 prior
  assumes linear-independence of the two mechanics. In reality, the
  ratevol gate fires only during OFF state (28% of post-warmup days)
  AND those days are typically high-stress regimes where multi-asset
  diversification's benefit is also peak — so the two effects may have
  some shared statistical power, leading to sub-additivity in practice.

---

## Reuse and scope

- **Imports (read-only):**
  - `studies.letf_rotation_hunt.gates` — G1-G7 (frozen).
  - `studies.letf_rotation_hunt.scoring` — `compute_metrics`,
    `score_strategy`, `crisis_beats_benchmark` (frozen).
  - `studies.letf_rotation_hunt.data_loader` — testfolio loader (frozen).
  - `studies.letf_rotation_hunt.signals` — winner replica primitives
    (`sma_gate`, `realized_vol_gate`, `ar1_coefficient`, `vote_of_k`)
    (frozen).
  - `studies.letf_rotation_hunt.plot_helper` — 7 standard plots (frozen).
  - `studies.letf_rotation_hunt.sortino_reanalysis.sortino_metric` (frozen).
  - **Prior iter helpers (committed, read-only):**
    - `loop_iterations/005-.../basket_sizer.py` — inverse-vol + equal
      weights + basket returns.
    - `loop_iterations/006-.../rate_vol_gate.py` — rolling realised vol +
      percentile rank + binary regime gate.

- **New code (lives inside iter 007 dir):**
  - `backtest.py` — compound build (combines ON-leg basket + OFF-leg
    ratevol override into a single strategy returns series). Tested in
    `tests/test_letf_rotation_hunt_loop_007.py`.

- **No changes to closed-study modules:** zero modifications to
  `gates.py`, `scoring.py`, `data_loader.py`, `signals.py`,
  `signals_carry.py`, `synths.py`, `tax_layer.py`, `plot_helper.py`,
  `kill_rules.py`, `verdict_schema.json`, `loop_verdict_schema.json`,
  prior `iterations/`, prior `loop_iterations/`, BASE_MEMORY.md. Per
  LOOP_PROTOCOL §"Scope limits".

---

## Cross-references

- Iter 005 SUMMARY: `loop_iterations/005-2026-05-09-multi-asset-on-invvol/SUMMARY.md`
- Iter 006 SUMMARY: `loop_iterations/006-2026-05-09-bond-ratevol-regime/SUMMARY.md`
- Winner anchor: `iterations/022-2026-05-06-T3d-extended-grid/`
- Winner config: `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`
  (Sortino_lh56y 1.3246, frozen loop benchmark)
- LOOP_PROTOCOL: `studies/letf_rotation_hunt/LOOP_PROTOCOL.md`
- Beats threshold: 1.3246 + 0.05 = **1.3746** (frozen).
