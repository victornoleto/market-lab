# 017 — post-crash re-arm to TQQQ (streak capture overlay)

**Iter:** 017 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Slug:** `postcrash-rearm-tqqq-streak`
**Engine version:** loop_iter_017
**n_configs:** 6
**cumulative_n_trials_global before/after:** 522 → 528

## Hypothesis

Post-crash re-arm overlay onto iter 014's strict_superset
(`single_K4lv25_g25_rvp70_cashx`, Sortino 1.3951 / CAGR 31.47% / crisis 1/4
[2008]) and onto iter 014's triple-stack (`basket3_K4lv25_g25_rvp70_cashx`,
Sortino 1.4689 / CAGR 22.65% / crisis 3/4 [2000+2008+2022]).

**Mechanism (TIME-domain, novel for the loop):**

1. Track every transition where the master `on_signal` (vote-K=2 entry on
   QLD) flips OFF→ON at day t.
2. If, at the flip, the prior contiguous OFF stretch lasted ≥ T_crash days
   (signaling a crash regime exit), open a **re-arm window** of D_arm days
   starting at day t.
3. During the re-arm window, **force the upgrade gate to 1** (i.e., swap
   QLD→TQQQ on single-asset, or swap to TQQQ-basket on basket3) — OR-combined
   with the base K4_AND_lv25 gate so the overlay strictly *adds* upgrade
   activation; it never suppresses it.
4. After D_arm days expire, the upgrade gate reverts to base K4_AND_lv25.

**Rationale.** Husson-Trifoni `[leverage_for_the_long_run, p.6-7, ch.3]`
empirically demonstrates that **above the moving average, the S&P 500
exhibits positive autocorrelation** (consecutive up-days more likely =
"streaks"); **below it, alternating seesawing dominates**. The MA flip from
below-to-above is therefore the empirical onset of the streak window — the
exact regime in which daily-rebalanced 3× LETFs (TQQQ) outperform 2× (QLD)
because of compounding asymmetry, *not* despite it (LRS thesis,
`[leverage_for_the_long_run, p.7]`). The longer the prior OFF stretch, the
more decisively a crash regime has flushed weak hands and reset volatility,
making the post-flip streak window more concentrated. T_crash is the proxy
for "real crash, not whipsaw"; D_arm is the streak harvesting horizon.

**Why this should improve Phase 3 over the other rejected paths:**

- **Iter 015 (eqtilt) and iter 016 (regsw) both failed** to clear the Phase 3
  CAGR floor by tweaking ON-leg basket composition. Both are *state-domain*
  mechanisms operating on continuous gates (vol percentile, K=4 vote).
- This iter introduces a *time-domain* mechanism (duration of OFF stretch,
  duration of re-arm window) that is mechanically orthogonal to all previous
  loop ON-leg / OFF-leg / gating mechanisms. The orthogonality should
  preserve PBO < 0.50 and the strict_superset frame of iter 014 single +
  K4lv25 + g25 + rvp70 cashx.
- The 2020 COVID rebound (March-Dec 2020) is the loop's lone "missed
  high-Sharpe streak" — TQQQ went +110% vs QLD's ~30% in March-December
  2020. Capturing 30-60 days of that rebound with TQQQ instead of QLD is
  the single highest-EV crisis-attribution improvement available (1/4 → 2/4
  on iter 014 strict_superset would lift score 76.5 → ~82).
- Other historical OFF→ON flips after long OFF stretches: 1974 (oil shock
  bottom), 1982 (Volcker disinflation), 2002 (post-dotcom), 2009 (post-GFC
  trough), 2020 March (COVID), 2023 January (post-2022 trough). Each is a
  candidate streak window.

**Slot 6 ablation (TRADE-OFF RESOLUTION ATTEMPT):** apply the same overlay
to the basket3 triple-stack. Hypothesis: the re-arm window swaps the
ON-leg from QLD/UPRO/UGL invvol to TQQQ-only for D_arm days, capturing
post-crash rebounds that the basket3-invvol composition smooths over (via
UGL gold weight ~45% drag during recovery). If successful, this would
deliver the loop's first crisis-≥2/4 strict_superset that iter 015/016 both
sought and missed. If unsuccessful, it confirms that the structural
basket3 CAGR ceiling (22.65% lh_56y) is fundamentally tied to the
~45% UGL weight and not unlockable by short-duration timed exposure swaps.

## Primary citation

`[leverage_for_the_long_run, p.6-7, ch.3]` — Husson-Trifoni: above the MA,
positive autocorrelation/streaks; below the MA, seesawing. Volatility
regime, not time, governs leveraged ETF performance. The MA flip-ON is the
empirical regime onset for streak harvesting.

## Secondary citations

- `[leverage_for_the_long_run, p.4, ch.2]` — "High volatility and seesawing
  action are the enemies of leverage while low volatility and streaks in
  performance are its friends." Direct empirical motivation for the re-arm
  window.
- `[leverage_for_the_long_run, p.7, ch.3]` — "performance over time has
  nothing to do with time itself, but rather: 1) the behavior of the
  underlying asset in its overall trend, 2) the path of daily returns
  (streaks versus seesawing action), and 3) whether the regime under which
  leverage is utilized is high or low volatility." T_crash and D_arm are
  the operational primitives encoding "trend re-establishment" and
  "streak harvesting horizon" respectively.
- `[stocks_on_the_move, p.98]` — Clenow trend-strength filter (post-crash
  trend re-establishment via prior K=4 vote retained as base upgrade gate).
- `[volatility_trading, p.58-60]` — Sinclair vol cone (lowvol25 percentile
  retained as base upgrade gate; re-arm window is the vol-regime onset
  detector).
- `[risk_parity, p.80-81, ch.4]` — Qian RORO graded master-gate (gamma=0.25
  retained as iter 014 strict_superset base).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking (re-arm
  overlay stacks on K4_AND_lv25 + ratevol-OFF cashx + graded blend without
  conflict — disjoint state cells).
- `[systematic_trading, p.212, ch.13]` — Carver semi-automatic stop re-arm
  hysteresis (conceptual analogue: stop EXIT logic; this iter applies the
  re-arm idea to ENTRY leverage instead — same time-domain memory pattern).
- `[advances_fin_ml, p.208-211]` — CSCV PBO with mechanism-mix-diverse
  topology grid.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials_global=528.

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility")

1. ✅ **Citable book/paper.** Primary `[leverage_for_the_long_run, p.6-7,
   ch.3]` Husson-Trifoni; full lineage above.
2. ✅ **Distinct from `iterations/`.** T1-T5 closed study covered Gayed
   single-LETF, HFEA basket, T3d composite signal, T4 cross-sectional
   Clenow, T5 Carver vol-target. **No T1-T5 iter introduced a
   time-domain re-arm overlay** — all gates were state-domain (signals on
   t-th day, no memory of regime duration).
3. ✅ **Distinct from `loop_iterations/`.** Loop iters 001-016 covered
   adaptive OFF / vol-DD kill / calendar / corr regime / multi-asset invvol
   / bond ratevol / compound ratevol-x-invvol-basket / 4-axis CSCV / master
   scope / graded master / conditional TQQQ leverage / compound TQQQ-K4 /
   triple-stack K4lv25 / mechanism-mix-diverse graded blend / equity-tilted
   basket / regime-switch ON-leg basket. **None tracked time since the
   last OFF→ON transition or imposed a fixed-duration upgrade window.**
   Iter 011 conditioned the upgrade on K=4 / lowvol25 (state-domain).
   Iter 016 conditioned the ON-leg composition on a regime gate
   (state-domain). Iter 017's re-arm window is state-transition-time-
   domain — orthogonal axis.
4. ✅ **Data feasibility.** All series already loaded in iter 014:
   QLDSIM, TQQQSIM, UPROSIM, UGLSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM. No
   new data sources required. T_crash and D_arm are integer-valued
   parameters computed from the existing master `on_signal` series.

## Configs (6, mechanism-mix-diverse — 4 distinct ON-leg-overlay topologies)

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_rearm_`) | ON-leg | upgrade base | gamma | ratevol | alt-OFF | re-arm T_crash | re-arm D_arm |
|---|---|---|---|--:|---|---|--:|--:|
| 1 | `baseline_qld_zroz` | single QLD | none | 0.00 | none | — | — | — |
| 2 | `single_K4lv25_g25_rvp70_cashx` ← iter 014 strict_superset replica | single QLD/TQQQ | K4_AND_lv25 | 0.25 | p70 | CASHX | disabled | disabled |
| 3 | `basket3invvol_K4lv25_g25_rvp70_cashx` ← iter 014 triple-stack replica | basket3-invvol60 | K4_AND_lv25 | 0.25 | p70 | CASHX | disabled | disabled |
| 4 | **`single_K4lv25_g25_rvp70_cashx_T20D30`** ← PRIMARY | single QLD/TQQQ | K4_AND_lv25 OR re-arm | 0.25 | p70 | CASHX | 20 days | 30 days |
| 5 | `single_K4lv25_g25_rvp70_cashx_T40D60` ← sensitivity | single QLD/TQQQ | K4_AND_lv25 OR re-arm | 0.25 | p70 | CASHX | 40 days | 60 days |
| 6 | **`basket3invvol_K4lv25_g25_rvp70_cashx_T20D30`** ← TRADE-OFF RESOLUTION | basket3-invvol60 | K4_AND_lv25 OR re-arm | 0.25 | p70 | CASHX | 20 days | 30 days |

**Mechanism-mix audit:**

- ON-leg topology: 4 distinct (single, basket3-invvol, single+reentry,
  basket3+reentry).
- Re-arm T_crash threshold: 3 distinct (none, 20 days, 40 days).
- Re-arm D_arm duration: 3 distinct (none, 30 days, 60 days).
- Upgrade base gate: 2 distinct (none, K4_AND_lv25).
- All 5 non-baseline configs share K4_AND_lv25 / g=0.25 / p70 / CASHX axis
  (iter 014 strict_superset frame; calibration constraint).

## Datasets (4)

Same as study + iter 014 / 015 / 016: `lh_56y` (1970-01..2026-04, SPYSIM
synth), `modern_1990` (1990-01..2026-04), `spy_real` (2003-01..2026-04,
Tiingo SPY post-inception), `ndx_real` (2010-02..2026-04, Tiingo QQQ
post-inception).

## Pre-registered KILL_LOOP conditions

| # | Rule | Direction |
|---|---|---|
| 1 | success_tag — any config achieves `beats_winner=True` | POSITIVE; expect FIRED |
| 2 | decisive_fail — best Sortino_lh56y < 1.20 | NEGATIVE; expect NOT FIRED |
| 3 | replica_sanity_baseline — baseline drift from iter 011-016 anchor (1.3240) > 0.005 | NEGATIVE; expect NOT FIRED ✅ |
| 4 | replica_sanity_single_K4lv25_g25 — slot 2 drift from iter 014/015/016 anchor (1.3951) > 0.005 | NEGATIVE; expect NOT FIRED ✅ |
| 5 | replica_sanity_basket3invvol_K4lv25_g25 — slot 3 drift from iter 014/015/016 anchor (1.4689) > 0.005 | NEGATIVE; expect NOT FIRED ✅ |
| 6 | PBO_blowup — G1 PBO ≥ 0.55 | NEGATIVE; expect NOT FIRED |
| 7 | PBO_held — G1 PBO < 0.50 | POSITIVE; expect FIRED |
| 8 | rearm_phase3_perf_candidate — any of slots 4/5/6 achieves `phase3_performance_candidate=True` | POSITIVE; CORE HYPOTHESIS TEST |
| 9 | rearm_strict_superset — any of slots 4/5/6 achieves `strict_superset=True` | POSITIVE; STRONGEST HYPOTHESIS TEST |
| 10 | rearm_2020_covid_rescue — any of slots 4/5/6 beats SPY in 2020_covid window | POSITIVE; targeted crisis test |
| 11 | rearm_strict_superset_with_crisis_2plus — any of slots 4/5/6 achieves `strict_superset=True` AND crisis ≥ 2/4 | POSITIVE; loop's first crisis-≥2/4 strict_superset |
| 12 | rearm_basket3_unlocks_phase3 (DIAGNOSTIC) — slot 6 achieves `phase3_performance_candidate=True` (basket3 + reentry resolves CAGR ↔ crisis trade-off) | POSITIVE; expect NOT FIRED (basket3 CAGR ceiling believed structural) |

## Expected outcomes

- **Sortino_lh56y range:**
  - baseline: 1.3240 (calibration replica, KILL_LOOP #3)
  - single anchor (slot 2): 1.3951 (calibration replica, KILL_LOOP #4)
  - basket3 anchor (slot 3): 1.4689 (calibration replica, KILL_LOOP #5)
  - single + reentry (slots 4, 5): 1.38–1.42 (mild Sortino lift if rebound
    days have positive Sortino; Sortino floor preserved by overlay's
    strict-additive nature)
  - basket3 + reentry (slot 6): 1.45–1.50 (rebound days replace
    basket-during-recovery returns with TQQQ-during-recovery; expect
    higher upside skew → Sortino lift if downside vol stays bounded)

- **CAGR_lh56y vs T3d-K2 31.08% floor:**
  - baseline / slot 2 / slot 3: same as iter 014 (31.08% / 31.47% / 22.65%)
  - slot 4 (T20D30 single): expect 32.0% – 34.0% — primary path; ~6 OFF→ON
    flips after 20+ day OFF stretches over 56 years × 30 days × +1-2%
    daily TQQQ-vs-QLD outperformance during streak windows ≈ 1-3pp CAGR
    lift over baseline anchor.
  - slot 5 (T40D60 single): expect 31.5% – 33.5% — fewer events (T=40
    rejects whipsaw OFF stretches) but longer harvest window (D=60).
  - slot 6 (T20D30 basket3): expect 23.5% – 25.5% — modest lift over
    basket3 anchor 22.65%; remains well below 31.08% floor (structural
    basket3 ceiling believed durable).

- **Terminal equity ratio vs T3d-K2 (baseline):** slot 4: 1.20 – 1.50;
  slot 5: 1.10 – 1.40; slot 6: 0.06 – 0.12 (basket3 floor unchanged).

- **Rolling-window win-rate vs baseline (1y/3y/5y/10y):** slot 4 expected
  60-75% across windows (rebound capture creates concentrated lifts); slot
  6 expected 5-25% (basket3 base loses most windows during equity-bull).

- **Crisis attribution:**
  - slots 4/5: hope to add 2020_covid (+1 crisis → 2/4); maybe also
    1974 oil shock (only resolved on lh_56y window) and 1982 Volcker
    bottom — these don't show in the 4-window benchmark crisis grid.
  - slot 6: should retain 3/4 (2000+2008+2022); may flip 2022 to
    2020 depending on timing of OFF→ON in 2022 (rolling drawdown without
    clean flip-ON).

- **Plan vs winner (beats_winner criterion):** for slots 4/5 to beat,
  need Sortino > 1.3746 ✓ AND winner_conditions_met (G1 PBO < 0.50, all
  G2-G7 pass) ✓ AND pct_time_above_benchmark_lh56y ≥ 0.95 ✓. Expected:
  slots 4/5 should beat.

- **Phase 3 performance candidate:** for slots 4/5 to qualify, need
  CAGR_lh56y > 31.08% AND end_eq_ratio_vs_baseline > 1.05 AND Sortino ≥
  1.20 AND PBO < 0.50 AND DSR_global p < 0.05. Expected: slot 4 most
  likely candidate; slot 5 borderline.

- **Strict_superset (LOOP'S 1st crisis-≥2/4):** slot 4 with
  beats_winner ✓ + phase3 ✓ + crisis ≥ 2/4 (2008 + 2020 COVID rescue) =
  the loop's first crisis-≥2/4 strict_superset. This is the headline
  prediction and the highest-EV outcome of iter 017.

## INCOMPLETE / caveats

- **Synth data assumption.** TQQQSIM is a Gayed-method synthetic 3× NDX
  before TQQQ inception (2010). Pre-2010 streak windows use synthetic
  TQQQ behavior; rebound-day mechanics rely on synthetic accuracy. UGL
  synth inception ~1985 truncates basket3 to that window for slot 3/6.
  No NEW synth caveats vs iter 014.
- **Transaction costs ignored** (gross metrics only; tax_layer.py
  available but not applied — matches iter 014/015/016 convention).
- **T_crash measured from `on_signal.shift(1)` series with K=2 entry
  warmup**; if `on_signal` is NaN (warmup), the OFF stretch counter
  resets to 0. Edge case: warmup transitions don't trigger re-arm.
- **D_arm is calendar-trading-days (252-day-year basis), not real
  calendar days.** Matches all other rolling windows in the study.
- **Re-arm OR-combine.** Overlay strictly *adds* upgrade activation.
  Never suppresses the base K4_AND_lv25 (which can stay active across
  re-arm window expiry; not exclusive).
- **No re-arm parameter sweep beyond {T20D30, T40D60, T20D30-basket3}.**
  Anti-DSR-inflation: 6 configs total (LOOP_PROTOCOL n_configs ≤ 8 cap).
  Slot 4 is the primary; slot 5 sensitivity; slot 6 ablation.
