# Iter 015 — equity-tilted-basket-cagr-recovery

**Phase:** 3 — performance-first beater hunt
**n_configs:** 6 (≤ 8 cap)
**cumulative_n_trials_global before:** 510
**cumulative_n_trials_global after:** 516

## Hypothesis

Iter 014 surfaced the structural blocker for the loop's "crisis-3/4
strict_superset": basket3-invvol (QLD/UPRO/UGL invvol60 — iter 007 anchor
Sortino 1.4637 → triple-stack 1.4689) delivers Sortino LOOP MAX +
crisis 3/4 (2000_dotcom + 2008_GFC + 2022_rates) but **CAGR_lh56y collapses
to 22.65%** (vs T3d-K2 31.08% Phase 3 floor). End-equity ratio vs baseline
0.056× — basket3 finishes at < 6% of baseline equity over 1970-2026
because invvol weighting structurally over-allocates to gold (lowest-vol
asset of the three legs) and gold's long-run real return is below
levered-equity. This mirrors Qian's example of naïve risk parity producing
**65% bonds, 22% stocks, 13% commodities** when applied to equity/bond/
commodity universes `[risk_parity, p.11, ch.1]`.

The hypothesis tests whether **fixed-weight equity-tilted baskets**
(2/3 QLD + 1/6 UPRO + 1/6 UGL family; 0.85/0.075/0.075 family;
or basket2 QLD/UPRO without UGL) can simultaneously:

1. **Recover CAGR_lh56y above the 31.08% Phase 3 floor** by structurally
   capping gold weight (≤ 16.7% in basket3-eqtilt66; 0% in basket2_QU).
2. **Preserve crisis 2/4 or 3/4** via the residual 16.7% UGL gold sleeve
   (gold cushion structurally captures 2000_dotcom and 2022_rates per
   iter 007/014 evidence).
3. **Maintain G1 PBO < 0.5** via mechanism-mix-diverse 6-config grid
   (5 distinct ON-leg topologies: single, basket3-invvol, basket3-eqtilt66,
   basket3-eqtilt85, basket2_QU-invvol; iter 014 PBO-0.4405 recipe).
4. **Maintain Sortino_lh56y ≥ 1.20** Phase 3 floor and `winner_conditions_
   met=True` so any equity-tilted variant that clears CAGR floor becomes
   the loop's first **crisis-≥2/4 strict_superset**.

**Theoretical motivation — Qian diversification return**
`[risk_parity, p.110, ch.5]`:

> $e_v = -0.5 \cdot w_1 w_2 \cdot 2\rho_{12}\sigma_1\sigma_2$
> ... "Always non-negative for long-only unlevered portfolios" — Qian.

A fixed-weight rebalanced basket captures positive diversification return
proportional to volatility × asset count × negative-correlation pairs.
For QLD/UPRO/UGL (correlations: QLD-UPRO ≈ +0.85, QLD-UGL ≈ -0.05,
UPRO-UGL ≈ -0.05), the dominant diversification return is on the QLD-UGL
and UPRO-UGL axes. **Fixed-weight equity-tilted basket retains those
diversification axes while structurally capping the over-allocation to
the lowest-vol asset** that invvol weighting produces. That is the
mechanical hypothesis.

This is parametric variation within Carlson cap-efficient stacking
`[risk_parity, ch.5, p.10]` (compatible with iter 014's stacking
framework) but with the basket-weighting primitive switched from
inverse-vol (Carver scalar `[systematic_trading, ch.10]` / Clenow
vol-parity `[stocks_on_the_move, p.98]`) to fixed-weight equity-tilt
(Qian diversification return).

## Primary citation

`[risk_parity, p.110, ch.5]` Qian — diversification return formula for
fixed-weight rebalanced basket; foundation for switching basket3 from
invvol to fixed-weight equity-tilted.

## Secondary citations

- `[risk_parity, p.11, ch.1]` Qian — naïve risk parity over-allocates to
  lowest-vol asset (≈ basket3-invvol's gold over-allocation pathology).
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate (preserved
  ON-blend cell at gamma=0.25).
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking (preserved
  K4_AND_lv25 × ratevol-OFF stacking).
- `[stocks_on_the_move, p.98]` Clenow vol-parity (basket3-invvol baseline
  contrast).
- `[systematic_trading, ch.10]` Carver inverse-vol scalar (same).
- `[volatility_trading, p.58-60]` Sinclair vol cone (ratevol gate, K4 vote).
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS
  leverage scaling (TQQQ swap on K4_AND_lv25 upgrade gate).
- `[advances_fin_ml, p.208-211]` PBO via CSCV — mechanism-mix-diversity
  grid composition.
- `[advances_fin_ml, p.222-223]` DSR cumulative; n_global=510→516.

## Eligibility checklist

- (a) **Citable book/paper** — YES: `[risk_parity, p.110, ch.5]` Qian primary
  + 9 supporting citations.
- (b) **Distinct from `runs/original/`** — YES: closed study T2 HFEA basket
  tested only fixed 55/45 NDX-TQQQ/TMF; never tested QLD/UPRO/UGL
  equity-tilt with K4_AND_lv25 upgrade gate.
- (c) **Distinct from `runs/post_close/`** — YES: iters 005-014 use
  single-asset OR basket3-invvol60 ONLY. Fixed-weight equity-tilted
  basket3 has not been tested. iter 014 explicitly recommends this as
  "Next iter idea (a) — HIGHEST EXPECTED VALUE: addresses structural
  CAGR blocker."
- (d) **Data feasibility** — YES: QLDSIM, UPROSIM, UGLSIM, TQQQSIM, ZROZSIM,
  IEFSIM, CASHX, SPYSIM all available in `data/testfolio/cache/history.parquet`
  back to 1885; tested in iters 007-014.

All YES → proceed.

## Six configs (mechanism-mix-diverse — vary ON-leg type primarily)

Naming: `qld_voteK2_sma250_100_vol21_40_ar30_eqb_<topology>` (eqb =
equity-tilted basket). All preserve T3d-K2 winner signal (K=2 of
{SMA250, SMA50, vol_21d<40, AR(1)>0.30}) at the entry layer.

| # | Slug suffix | ON-leg | upgrade | gamma | ratevol | alt-OFF | Role |
|---|---|---|---|--:|---|---|---|
| 1 | `baseline_qld_zroz` | single QLD | none | 0.00 | none | — | calibration anchor (iter 011-014 baseline 1.3240 — KILL_LOOP #3) |
| 2 | `single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | K4_AND_lv25 | 0.25 | p70 | CASHX | iter 014 strict_superset replica anchor (Sortino 1.3951 — KILL_LOOP #4) |
| 3 | `basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 (QLD/UPRO/UGL) with QLD↔TQQQ on upgrade | K4_AND_lv25 | 0.25 | p70 | CASHX | iter 014 triple-stack anchor (Sortino 1.4689 / CAGR 22.65% — KILL_LOOP #5) |
| 4 | `basket3eq66_K4lv25_g25_rvp70_cashx` ← **PRIMARY** | basket3-eqtilt66 (fixed 2/3 QLD + 1/6 UPRO + 1/6 UGL) with QLD↔TQQQ on upgrade | K4_AND_lv25 | 0.25 | p70 | CASHX | NEW — primary equity-tilted variant |
| 5 | `basket3eq85_K4lv25_g0_rvp80_ief` | basket3-eqtilt85 (fixed 0.85 QLD + 0.075 UPRO + 0.075 UGL) | K4_AND_lv25 | 0.00 | p80 | IEFSIM | NEW — high equity tilt + orthogonal mix (different gamma + ratevol + alt-off) |
| 6 | `basket2QU_K4lv25_g25_rvp70_cashx` | basket2-invvol60 (QLD/UPRO; no UGL) with QLD↔TQQQ on upgrade | K4_AND_lv25 | 0.25 | p70 | CASHX | NEW — pure-equity ablation: removes UGL entirely; tests if gold cushion is necessary for crisis rescue |

**Mechanism-mix-diversity audit:**
- ON-leg type: 5 distinct (single, basket3-invvol, basket3-eqtilt66,
  basket3-eqtilt85, basket2-QU-invvol)
- upgrade gate: 2 distinct (none, K4_AND_lv25)
- gamma: 2 distinct (0, 0.25)
- ratevol threshold: 3 distinct (none, p70, p80)
- alt-OFF: 3 distinct (none, CASHX, IEFSIM)

5 distinct ON-leg topology buckets across 6 configs (vs iter 014's 5
buckets / PBO 0.4405). Should preserve PBO < 0.5.

## Calibration anchors (cross-iter bit-exact)

- **Config 1** (`baseline_qld_zroz`): Sortino_lh56y = 1.3240 ± 0.005 (vs
  iter 011/012/013/014 anchor; iter 011 helper baseline). KILL_LOOP #3.
- **Config 2** (`single_K4lv25_g25_rvp70_cashx`): Sortino_lh56y = 1.3951 ±
  0.005 (vs iter 013 g25 + iter 014 strict-superset). KILL_LOOP #4.
- **Config 3** (`basket3invvol_K4lv25_g25_rvp70_cashx`): Sortino_lh56y =
  1.4689 ± 0.005 (vs iter 014 triple-stack basket3 — KILL_LOOP #5).

If any calibration anchor fires (drift > 0.005 abs), it indicates a
silent regression in iter 015's helper modules — must investigate before
trusting the new equity-tilted basket variants.

## Pre-registered KILL_LOOP conditions

These do NOT halt the loop (LOOP_PROTOCOL §"Mandate §1 reinforcement");
they are diagnostic tags appended to `verdict.json["kill_loop_results"]`.

- **KILL_LOOP #1 (success_tag):** any config has `beats_winner=True`
  (Sortino > 1.3746 AND winner_conditions_met=True AND pct_above ≥ 0.95).
- **KILL_LOOP #2 (decisive_fail):** best Sortino_lh56y < 1.20 (Phase 3
  floor). Hypothesis dead.
- **KILL_LOOP #3 (replica_sanity_baseline):** baseline Sortino deviates
  from 1.3240 by > 0.005 abs.
- **KILL_LOOP #4 (replica_sanity_single_K4lv25_g25):** single
  K4lv25_g25_rvp70_cashx Sortino deviates from 1.3951 by > 0.005.
- **KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25):** basket3-
  invvol K4lv25_g25_rvp70_cashx Sortino deviates from iter 014 anchor
  1.4689 by > 0.005.
- **KILL_LOOP #6 (PBO_blowup):** G1 PBO ≥ 0.55 (hard regression vs iter
  014 0.4405). POSITIVE TAG inverted (this would be a NEGATIVE finding).
- **KILL_LOOP #7 (PBO_held):** G1 PBO < 0.50 (PBO recipe held). POSITIVE
  TAG.
- **KILL_LOOP #8 (phase3_perf_candidate_eqtilt):** ANY equity-tilted
  variant (configs 4, 5, or 6) achieves
  `phase3_performance_candidate=True`. POSITIVE TAG. **CORE
  HYPOTHESIS — does fixed-weight equity-tilt clear the Phase 3 CAGR
  floor that invvol-basket3 fails?**
- **KILL_LOOP #9 (strict_superset_eqtilt):** ANY equity-tilted variant
  (configs 4, 5, or 6) achieves `strict_superset=True` (beats_winner AND
  phase3_performance_candidate). POSITIVE TAG. **STRONGEST
  HYPOTHESIS — does an equity-tilted basket simultaneously beat T3d-K2
  on Sortino AND on CAGR?**
- **KILL_LOOP #10 (eqtilt_crisis_2or3_of_4):** basket3-eqtilt66 (config
  4) OR basket3-eqtilt85 (config 5) achieves crisis count ≥ 2/4
  (i.e., retains gold cushion benefit at reduced UGL weight). POSITIVE
  TAG.
- **KILL_LOOP #11 (basket2_QU_no_crisis):** basket2_QU (config 6) with
  no UGL achieves crisis count ≤ 1/4 (confirms UGL is necessary for
  multi-crisis rescue). POSITIVE TAG (validates ablation expectation).
- **KILL_LOOP #12 (eqtilt_crisis_strict_superset):** basket3-eqtilt66 or
  basket3-eqtilt85 achieves strict_superset AND crisis ≥ 2/4 — i.e.,
  loop's first **crisis-≥2/4 strict_superset**. POSITIVE TAG (highest
  expected-value outcome of this iter).

## Expected outcomes

**Config 1 (baseline_qld_zroz)** — Sortino_lh56y ≈ 1.3240 (iter 011-014
anchor); CAGR ≈ 31.08%; crisis 1/4; pure replica.

**Config 2 (single_K4lv25_g25_rvp70_cashx)** — Sortino ≈ 1.3951
(iter 013/014 anchor); CAGR ≈ 31.47%; crisis 1/4; iter 014 strict_
superset replica.

**Config 3 (basket3invvol_K4lv25_g25_rvp70_cashx)** — Sortino ≈ 1.4689
(iter 014 triple-stack anchor); CAGR ≈ 22.65%; crisis 3/4; iter 014
anchor (NOT phase3 candidate).

**Config 4 (basket3eq66_K4lv25_g25_rvp70_cashx) ← PRIMARY** —
- Expected Sortino_lh56y range: **1.36-1.46** (between single 1.3951
  and basket3-invvol 1.4689; gold cushion at 1/6 weight smaller than
  basket3-invvol's ~45% gold weight).
- Expected CAGR_lh56y: **27-32%** (much higher than basket3-invvol's
  22.65% because gold weight cut from ~45% to 16.7%; below single QLD
  31.08% by ~1-3pp due to UPRO/UGL drag at 1/3 of capital).
- Expected end_equity_ratio_vs_baseline: **0.6-1.2×** (much higher than
  basket3-invvol's 0.056×).
- Expected crisis: **2/4** (retains 2022_rates rescue via 1/6 UGL gold
  cushion; possibly retains 2000_dotcom).
- Expected `phase3_performance_candidate`: **maybe TRUE** if CAGR clears
  31.08% floor (depends on whether 1/6 gold drag is offset by
  diversification return at K4lv25 ON-leg level).
- Expected `beats_winner`: **TRUE** (Sortino likely > 1.3746;
  WC=True if PBO/DSR pass).
- Expected `strict_superset`: **possibly TRUE** — if both Phase 3 strict
  bar AND beats_winner cleared, this is the **highest expected-value
  config of the iter** — first crisis-≥2/4 strict_superset.

**Config 5 (basket3eq85_K4lv25_g0_rvp80_ief)** —
- Expected Sortino: **1.30-1.40** (gamma=0 + IEFSIM alt-off; less
  protection than gamma=0.25 + CASHX).
- Expected CAGR: **30-33%** (very close to single QLD; UGL only 7.5%).
- Expected crisis: **1-2/4** (smaller UGL weight reduces crisis cushion).
- Distinct topology (different gamma + ratevol + alt-off) for PBO
  diversity.

**Config 6 (basket2QU_K4lv25_g25_rvp70_cashx)** —
- Expected Sortino: **1.30-1.40** (no gold cushion; pure equity diversification
  on 2 levered NDX/SPY axes).
- Expected CAGR: **30-33%** (close to single QLD; UPRO partial weight).
- Expected crisis: **1/4** (no UGL → no 2022_rates rescue → only 2008_GFC).
- Pure-equity ablation control.

## Comparison plan vs winner T3d-K2 (1.3246 Sortino / 31.08% CAGR)

For each config, report and append to `verdict.json`:

- `sortino_edge_vs_winner = sortino_lh56y - 1.3246`
- `cagr_edge_vs_winner = cagr_lh56y - 0.3108`
- `end_equity_ratio_vs_baseline` (vs config 1 baseline; iter 014 convention)
- `rolling_win_rates_vs_baseline` for 1y/3y/5y/10y windows.
- `winner_conditions_met` (per scoring rubric).
- `pct_time_above_benchmark_lh56y`.
- `beats_winner = (sortino > 1.3746) AND winner_conditions_met AND
  (pct_above >= 0.95)`.
- `phase3_performance_candidate = (cagr > 0.3108) AND
  (end_eq_ratio > 1.05) AND (sortino >= 1.20) AND (PBO < 0.5) AND
  (DSR_global p < 0.05)`.
- `strict_superset = beats_winner AND phase3_performance_candidate`.

For best config (sort by `strict_superset` first, then `phase3_perf`,
then Sortino, then CAGR, then total_score), include the
`sortino_edge_vs_winner`, `cagr_edge_vs_winner`,
`end_equity_ratio_vs_baseline`, and `rolling_win_rates_vs_baseline` in
the top-level `verdict.json`.

## INCOMPLETE flags / caveats

- **UGLSIM, UPROSIM, TQQQSIM are synthetic** (testfolio FFR-aware
  reconstructions back to 1885). Cross-library parity tested in iter
  005/007 (G7 ≤ 0.03pp delta). G7 must continue to pass.
- **Fixed-weight basket diversification return depends on rebalancing
  frequency.** Iter 015 uses **daily rebalancing** (matches basket3-
  invvol convention); turnover impact at fixed-weight is
  approximately equal to invvol-rebalancing (small daily drift correction)
  and is approximated by mechanism_mix_turnover() per categorical state
  count (basket3 daily re-weighting NOT counted, same convention as
  iter 007/010/014).
- **Gold realized vol regime varies dramatically** (1970s-1980s gold bull
  run had σ ≈ 30-40% annualized; 2000s-2020s gold σ ≈ 15-20%). Fixed-
  weight basket cannot adapt; that's the design trade-off.
- **K4_AND_lv25 upgrade gate active% ~ 7.1%** (iter 011-014 measurement);
  basket3-eqtilt configs activate the QLD→TQQQ swap on the same gate;
  this introduces a small TQQQ exposure at the upgrade-active days.
- **Calibration anchor preservation is critical:** if KILL_LOOP #3
  (baseline 1.3240) or #5 (basket3-invvol 1.4689) fires, must
  investigate before trusting the eqtilt variants — the helper module
  may have a silent bug.
