# Iter 020 — SPY drawdown-depth conditional rearm gate (mechanism-mix-diverse)

**Iter:** 020 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Slug:** `spy-mdd-rearm-gate`
**n_configs:** 6
**cumulative_n_trials_global:** 540 → **546**
**cumulative_n_trials_loop:** 114 → **120**

## Hypothesis (STRONG)

**Refining iter 017's only NOVEL strict_superset by gating its rearm activation
on SPY drawdown depth at the qualifying-flip moment.** Iter 017's
`single_K4lv25_g25_rvp70_cashx_T40D60` (LOOP MAX strict_superset Sortino
1.4030, CAGR 32.66%, end_eq 1.620×) opens a 60-day TQQQ harvest after every
master OFF→ON flip preceded by ≥ 40 days OFF — 16 qualified flips over
56 years. Not all 16 represent "real crashes"; some are seesaw-induced
shallow MA flips that lack the post-crash streak asymmetry that
[leverage_for_the_long_run, p.4-7, ch.2-3] identifies as the structural
source of LETF leverage harvest. The hypothesis: filtering qualifying
flips by SPY trailing 200d max drawdown ≤ -15% (or stricter -25%) at
t-1 should drop seesaw false positives, lifting Sortino above iter 017's
1.4030 anchor while preserving the Phase 3 perf candidacy floors.

**Mechanism (no look-ahead; all signals computable by close of day t):**

1. The master `on_signal` (vote-K=2 entry on QLD) flips OFF→ON at day t.
2. Prior contiguous OFF stretch ≥ T_crash = 40 days (iter 017's recipe).
3. **NEW (iter 020):** SPY 200d trailing max drawdown at day t-1
   `mdd_200d[t-1] ≤ -mdd_threshold` (e.g., -0.15 or -0.25).
4. If both (2) and (3), the flip is "MDD-qualified"; rearm gate is 1 for
   D_arm = 60 consecutive days starting at t (lag-shifted to t+1 inside
   the mechanism-mix returns helper, identical to iter 017).
5. The rearm gate is OR-combined with the K4_AND_QLDlv25 base upgrade
   (identical to iter 017 slot 5 composition).

The SPY 200d trailing MDD threshold is the regime-confirmation filter
analogous to the **B-Strict** decision rule in [regime_change, p.70-71]
(Chen-Tsang require posterior probability > 0.8 to conclude Regime 2 /
abnormal-volatility regime, i.e., post-crisis state; we require trailing
SPY MDD ≤ -15% as a deterministic analogue: the broader index has
materially drawn down, confirming the prior OFF stretch was a real
drawdown rather than a low-amplitude seesaw).

The 40-day OFF threshold from iter 017 catches the **time-on-the-wrong-
side-of-MA** signal; the 200d MDD threshold catches the **magnitude of
underlying decline**. Together they require BOTH duration AND depth
before declaring the flip a streak-onset event suitable for TQQQ
exposure.

## Direction expected

This is a **safety refinement** (filter, not amplifier). Three regimes:

1. **Filter correctly prunes false positives** → Sortino lifts +0.01 to
   +0.05 vs T40D60 (1.4030 → ~1.41-1.45); CAGR drops slightly (-0.5pp);
   end_eq similar. Strict_superset ACHIEVED beyond iter 017.
2. **Filter is too strict** (rejects real opportunities) → Sortino flat
   or down; CAGR drops materially (-1.5pp+); end_eq drops below iter 017.
3. **MDD-15 too permissive, MDD-25 too strict** → bracketing reveals
   monotonic structure; pick the local optimum.

## Configs (6, mechanism-mix-diverse — 5 distinct topologies)

| # | Name | ON-leg | Upgrade axis | Rearm gate | T_crash | D_arm | MDD threshold | Role |
|--:|---|---|---|---|--:|--:|---:|---|
| 1 | `..._mddgate_baseline_qld_zroz` | single QLD | none | — | — | — | — | Calibration anchor (11th-gen) |
| 2 | `..._mddgate_single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | K4_AND_QLDlv25 | — | — | — | — | Iter 014 strict_superset replica |
| 3 | `..._mddgate_basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 | K4_AND_QLDlv25 | — | — | — | — | Iter 014 triple-stack replica |
| 4 | `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60` | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 (no MDD) | 40 | 60 | — | Iter 017 NEW strict_superset replica (anchor) |
| 5 | `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60_mdd15` ← **PRIMARY** | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm_MDD | T40D60 + MDD≤-15% | 40 | 60 | -0.15 | NEW: -15% gate |
| 6 | `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60_mdd25` ← **STRICTER** | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm_MDD | T40D60 + MDD≤-25% | 40 | 60 | -0.25 | NEW: -25% gate |

**Topology distinctness for CSCV diversity:**

- Slot 1: single, no upgrade
- Slot 2: single, K4_AND_QLDlv25
- Slot 3: basket3-invvol60, K4_AND_QLDlv25
- Slot 4: single, K4_AND_QLDlv25 OR T40D60-rearm (no MDD gate)
- Slots 5+6: single, K4_AND_QLDlv25 OR (T40D60-rearm AND SPY-MDD-gate)
  — same topology, parametric variation on MDD threshold

5 distinct upgrade-axis topologies (slots 5+6 share topology with each
other but differ from slots 1-4). Mirrors iter 017/019 mechanism-mix-
diverse recipe → expected G1 PBO ~ 0.20-0.45 (loop's empirical floor).

## Datasets

Standard four — `lh_56y` (1970-01 → 2026-04, primary), `modern_1990`
(1990-01 → 2026-04), `spy_real` (2003-01 → 2026-04), `ndx_real` (2010-02
→ 2026-04). Same as iter 014/017/019 for direct comparability.

## Pre-registered KILL_LOOP conditions

- **#1 success_tag** — Any config achieves `beats_winner=True` (Sortino
  > 1.3746 AND `winner_conditions_met=True` AND `pct_above >= 0.95`).
- **#2 decisive_fail** — Best Sortino_lh56y < 1.20 (Phase 3 floor).
- **#3 replica_sanity_baseline** — Baseline Sortino deviates from iter
  011-019 baseline 1.3240 by > 0.005.
- **#4 replica_sanity_single_K4lv25_g25** — single anchor Sortino
  deviates from iter 013-019 strict_superset 1.3951 by > 0.005.
- **#5 replica_sanity_basket3invvol_K4lv25_g25** — triple-stack Sortino
  deviates from iter 014-019 1.4689 by > 0.005.
- **#6 replica_sanity_T40D60** — T40D60 anchor Sortino deviates from
  iter 017-019 1.4030 by > 0.005.
- **#7 PBO_blowup** — G1 PBO ≥ 0.55 (hard regression threshold).
- **#8 PBO_held** — G1 PBO < 0.50 (Phase 3 hard gate; POSITIVE TAG).
- **#9 mddgate_phase3_perf_candidate** — Any MDD-gated config (slot 5
  or 6) achieves `phase3_performance_candidate=True`. **CORE
  HYPOTHESIS TEST.**
- **#10 mddgate_strict_superset** — Any MDD-gated config achieves
  `strict_superset=True`. **STRONGEST HYPOTHESIS TEST.**
- **#11 mddgate_dominates_T40D60** — Any MDD-gated Sortino > 1.4030
  (T40D60 anchor). Tests whether the depth filter materially lifts
  risk-adjusted return.
- **#12 mddgate_strict_superset_with_crisis_2plus** — Any MDD-gated
  config achieves `strict_superset=True` AND crisis count ≥ 2/4. Loop's
  first crisis-≥2/4 strict_superset target. **POSITIVE TAG.**

## Expected outcomes

- **Sortino_lh56y range:** 1.30 - 1.45 (best plausibly between slot 4
  T40D60 anchor 1.4030 and slot 5 MDD15).
- **CAGR_lh56y range:** 30.5% - 33.0% (slot 4 anchor 32.66%; slot 5
  expected 31.5-32.5%; slot 6 may dip below 30% if MDD-25 is too strict).
- **CAGR edge vs T3d-K2 (31.08%):** +0.5pp to +1.5pp expected for slot 5;
  uncertain for slot 6.
- **End_eq vs baseline ratio:** 1.10× - 1.65×.
- **Rolling-window 5y/10y:** slot 4 anchor 55.3%/38.0%; slot 5 expected
  similar; slot 6 may drop.
- **`beats_winner` plan:** for slot 5 to achieve True, need Sortino >
  1.3746 AND `winner_conditions_met=True` AND pct_above ≥ 0.95. Current
  T40D60 anchor (slot 4) already satisfies all three; slot 5 must
  preserve `winner_conditions_met` AND not drop Sortino below threshold.
- **Phase 3 perf candidate plan:** for slot 5 to achieve True, need
  CAGR > 0.3108 AND end_eq > 1.05× AND Sortino ≥ 1.20 AND PBO < 0.50
  AND DSR_global p < 0.05. Plausible for slot 5; slot 6 marginal.
- **Strict_superset plan:** slot 5 = beats_winner AND phase3 → if both
  fire, NEW non-replica strict_superset on the depth-filter axis.
- **Crisis ≥ 2/4 plan:** would require slot 5 to also beat SPY in 2
  of 4 crisis windows. Slot 4 anchor is 1/4 (only 2008 GFC); MDD-15 gate
  could plausibly flip COVID 2020 (deep V-bottom) but not 2022 (rates,
  no extreme MDD). MDD-25 gate would catch only 2008 GFC + COVID.
  Long-shot.

## Comparação plan vs winner

For slots 5/6 to count as `beats_winner`:
```
sortino_lh56y > 1.3746
AND winner_conditions_met (per scoring rubric)
AND pct_time_above_benchmark_lh56y >= 0.95
```

For slots 5/6 to count as `phase3_performance_candidate`:
```
cagr_lh56y > 0.3108  (T3d-K2 31.08% floor)
AND end_equity_ratio_vs_baseline > 1.05  (vs slot 1 baseline)
AND sortino_lh56y >= 1.20
AND g1_pbo < 0.50
AND g2_dsr_p_cumulative < 0.05  (n_trials_global = 546)
```

For slots 5/6 to count as `strict_superset`:
```
beats_winner AND phase3_performance_candidate
```

## Citations

**Primary:** `[leverage_for_the_long_run, p.4-7, ch.2-3]` — Husson-Trifoni
streak-vs-seesawing thesis; deeper crashes precede stronger streaks; "high
volatility and seesawing action are the enemies of leverage while low
volatility and streaks in performance are its friends" [p.4]. SPY 200d
MDD threshold filters MA flip-ups that occurred without a real drawdown
preceding them.

**Secondary:**
- `[regime_change, p.5-6, ch.2]` Chen-Tsang regime-change definition
  (collective trading-behaviour shift, observable through statistical
  property changes); MDD breach ≤ -15% as deterministic analogue to
  HMM regime-2 confirmation.
- `[regime_change, p.44-46, ch.4]` Abnormal regime (Regime 2) follows
  significant external events (financial crises, political shocks);
  MDD ≤ -15% empirically marks such episodes for the broader US equity
  index.
- `[regime_change, p.70-71, ch.5]` B-Strict decision rule (require
  p > 0.8 to conclude Regime 2); analogous to requiring MDD breach
  to exceed a threshold before declaring "post-crash regime onset".
- `[stocks_on_the_move, p.98]` Clenow trend re-establishment after
  long OFF stretch.
- `[volatility_trading, p.58-60]` Sinclair vol cone (low-vol regime
  onset is structurally tied to drawdown recovery).
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate.
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[systematic_trading, p.212, ch.13]` Carver re-arm hysteresis
  (slot 5/6 inherits iter 017 mechanism with depth gate added).
- `[advances_fin_ml, p.208-211]` CSCV PBO via mechanism-mix-diversity.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials (n_global=546).
- `[advances_fin_ml, p.196-202]` Bootstrap CI / DSR.

## INCOMPLETE flags

- **Synth caveat:** SPY 1968+ from SPYSIM (Testfolio). 200d MDD requires
  ~1968-Q4 onset (i.e., loses 200 trading days at the very start of
  lh_56y; warmup-trim handled via standard `windowed_returns` slicing).
- **Tax/fees:** turnover may shift slightly vs slot 4 (rearm fires on
  fewer flips); deferred net diagnostic per LOOP_PROTOCOL §"Config
  budget".
- **MDD threshold space:** only -15% and -25% tested; -10%, -20%, -30%
  variants deferred to a follow-up iter if hypothesis confirmed.
- **No look-ahead:** SPY MDD computed on lagged window; gate decision
  uses `mdd_200d[t-1]`. Verified explicitly in `mdd_gate.py`.
- **Cross-asset coverage:** T_crash / D_arm computed on QLD `on_signal`;
  MDD computed on SPY (broader index). Both align in the lh_56y window
  (no missing data).

## Strategy eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility checklist")

- (a) **Citable [book.slug, p.X]:** ✅ `[leverage_for_the_long_run, p.4-7, ch.2-3]` PRIMARY + `[regime_change, p.44-46, ch.4]` secondary. Both books exist in `books/summaries/` (LFLR direct; regime_change in `_archive/`).
- (b) **Distinct from `iterations/` (T1-T5):** ✅ The closed study covered T1 single-LETF Gayed, T2 HFEA, T3 composite signal, T4 cross-sectional, T5 Carver vol-target. None used a TIME-domain post-crash rearm with depth gate.
- (c) **Distinct from `loop_iterations/`:** ✅ Iter 017 used T40D60 rearm without MDD gate. Iter 018 graded D_arm by T_off length (a different, also-mechanism-internal variation). Iter 019 used SPY-RV-pct25 percentile gate (ADDITIVE OR-combine, not depth-filter on rearm). No prior loop iter combines T40D60-rearm × SPY-200d-MDD-depth filter.
- (d) **Data feasibility:** ✅ SPY 200d trailing MDD requires SPYSIM (Testfolio cache, 1968+) — already in load_universe. No new external data needed.

All YES → proceed.

## Next iter ideas (post-execution)

- (a) If MDD15 wins: sweep depth threshold {-10%, -12%, -15%, -18%, -20%}
  to find local optimum; combine with iter 017 D_arm sweep {30, 60, 90}
  for the joint maximum.
- (b) If MDD25 wins: pivot to even-stricter regime gates (e.g., SPY
  -30% or VIX-percentile > 90th).
- (c) If MDD15/25 both fail: T40D60 mechanism plateaus near 1.40 Sortino;
  pivot to entirely different family per iter 018/019 family-change
  recommendation (e.g., calendar/seasonality, cross-asset correlation
  regime, currency carry).
- (d) If MDD15 wins AND crisis ≥ 2/4 flips for COVID: investigate why
  the depth gate aligns with V-recovery onset (mechanism-level diagnosis
  for next iter's hypothesis design).
