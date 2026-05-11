# Iter 019 — SPY-RV-pct25 forward-vol upgrade gate (mechanism-mix-diverse)

**Iter:** 019 / 50 (loop) — Phase 3 performance-first beater hunt
**Slug:** `spyrv-pct25-upgrade-mechmix`
**Date (UTC):** 2026-05-10
**n_configs:** 6
**cumulative_n_trials_global before:** 534
**cumulative_n_trials_global after:** 540
**cumulative_n_trials_loop before:** 108
**cumulative_n_trials_loop after:** 114
**closed_study_cumulative_n_trials:** 426

## Hypothesis (1 sentence)

Add SPY 21d realised-vol percentile (< 25th vs trailing 1260-day window)
as an ALTERNATIVE upgrade-gate trigger that is OR-combined with iter
014's K4_AND_QLDlv25 (asset-trend × asset-vol composite) — testing
whether broader-market vol-regime onsets unlock additional upgrade
activation that asset-specific QLD-vol misses, citing Sinclair vol cone
`[volatility_trading, p.58-60]` and Husson-Trifoni "low volatility ⇒
streaks" `[leverage_for_the_long_run, p.4-7, ch.2-3]`.

## Why now (Phase 3 motivation)

After iter 018's PBO blowup (0.8135) caused by 5/6 configs sharing the
T40D60 base topology (`single/K4_AND_lv25/g25/p70-cashx`) with rearm
parametric variation, the loop's 3rd-time methodological lesson was
reconfirmed: **mechanism diversity for CSCV is structural, not parametric**
`[advances_fin_ml, p.208-211]`. Iter 019 returns to a 4–5 distinct
mechanism-family grid AND introduces a NEW orthogonal upgrade-axis
(forward-volatility-regime onset on SPY) that has not appeared in any
prior loop iter. The new axis aims for Phase 3 performance lift via
EXPANSION of upgrade activation (additional TQQQ exposure during
broader-market low-vol regimes), not de-risking.

iter 014's QLD-asset-vol-pct (lv25) is one specific frame; SPY-realised-
vol-pct on the broader index is conceptually distinct because (a) SPY is
a less leveraged index → smoother vol signal less dominated by single-
asset event noise, (b) the 5-year trailing percentile window captures
macro vol regimes that 21d local QLD-vol can miss, (c) SPY-RV cycles can
lead or lag QLD-RV cycles depending on dispersion. Sinclair's
**volatility cone** `[volatility_trading, p.58-60]` directly motivates
percentile-based vol-regime gates; the cone framework places current
realised-vol within its historical distribution to identify regime
states. Husson-Trifoni's "low volatility ⇒ streaks" thesis
`[leverage_for_the_long_run, p.4]` predicts that low-vol regimes are
positive-autocorrelation streak harvest windows — the upgrade gate
empirically opens during exactly those regimes.

The composite (slot 6) stacks all three orthogonal triggers:
- **State-domain:** K4_AND_QLDlv25 (iter 014; trend × asset-vol)
- **Time-domain:** T40D60 post-crash rearm (iter 017; OFF-stretch length × harvest window)
- **Forward-vol-domain:** SPY-RV-pct25 (NEW; broader-market low-vol regime)

Each trigger is in a different mechanism axis → CSCV-PBO diversity should
hold; combined activation maximizes upgrade frequency while no single
trigger dominates the firing distribution.

## Configs (6 — mechanism-mix-diverse with 5 distinct upgrade-axis topologies)

| # | Slot name (config) | ON-leg | Upgrade axis | Rearm? | Family | Role |
|---|---|---|---|---|---|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_baseline_qld_zroz` | single QLD | none | no | A | calibration anchor |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | K4_AND_QLDlv25 | no | B | iter 014 strict_superset replica |
| 3 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 | K4_AND_QLDlv25 | no | C | iter 014 triple-stack replica |
| 4 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_g25_rvp70_cashx_T40D60` | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T=40 D=60 | D | iter 017 NEW strict_superset replica |
| 5 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx` ← PRIMARY | single QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 | no | E | NEW: forward-vol orthogonal upgrade |
| 6 | `qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60` ← STRONGEST | single QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 OR rearm | T=40 D=60 | F | NEW: 3-way OR composite (state×time×forward-vol) |

All 6 configs share: graded master gamma=0.25, ratevol p70/cashx
override, single-asset ON-leg (slot 3 swaps to basket3 invvol60).
Variation is along the upgrade-axis (slots 1/2/3/4/5/6) and rearm-overlay
(slots 4/6). Slot 5 is the primary new mechanism; slot 6 is the maximum
combination.

## Datasets

- `lh_56y`  (1970-01-01 → 2026-04-30) — full sample, primary
- `modern_1990` (1990-01-01 → 2026-04-30) — out-of-pre-LETF-era
- `spy_real` (2003-01-01 → 2026-04-30) — Tiingo real-LETF era
- `ndx_real` (2010-02-01 → 2026-04-30) — TQQQ real era

## Pre-registered KILL_LOOP conditions

1. **KILL_LOOP #1 (success_tag) — POSITIVE TAG** — fires if any config
   has `beats_winner=True` (Sortino_lh56y > 1.3746 AND
   `winner_conditions_met=True` AND `pct_time_above_benchmark_lh56y >=
   0.95`).
2. **KILL_LOOP #2 (decisive_fail)** — fires if best Sortino_lh56y across
   all 6 configs < 1.20 (Phase 3 floor).
3. **KILL_LOOP #3 (replica_sanity_baseline)** — fires if baseline
   Sortino_lh56y deviates from iter 011-018 baseline 1.3240 by > 0.005.
   Should NOT fire (10th-generation cross-iter reproducibility check).
4. **KILL_LOOP #4 (replica_sanity_single_K4lv25_g25)** — fires if slot 2
   Sortino_lh56y deviates from iter 013-018 strict_superset replica
   1.3951 by > 0.005. Should NOT fire.
5. **KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25)** — fires if
   slot 3 Sortino_lh56y deviates from iter 014-017 triple-stack 1.4689
   by > 0.005. Should NOT fire.
6. **KILL_LOOP #6 (replica_sanity_T40D60)** — fires if slot 4
   Sortino_lh56y deviates from iter 017 LOOP MAX strict_superset 1.4030
   by > 0.005. Should NOT fire (2nd-generation reproducibility check on
   the iter 017 NEW strict_superset).
7. **KILL_LOOP #7 (PBO_blowup)** — fires if G1 PBO ≥ 0.55 hard
   regression threshold. Should NOT fire (the 5-distinct-mechanism-
   topology grid is designed to avoid the iter 018 0.8135 outcome).
8. **KILL_LOOP #8 (PBO_held) — POSITIVE TAG** — fires if G1 PBO < 0.50
   Phase 3 hard gate. SHOULD FIRE (target).
9. **KILL_LOOP #9 (spyrv_phase3_perf_candidate)** — fires if any spyrv
   config (slot 5 or 6) achieves `phase3_performance_candidate=True`.
   **CORE HYPOTHESIS TEST.** Pre-registered expectation: ≥1 of slot 5/6
   passes Phase 3 (CAGR > 31.08%, end_eq > 1.05×, Sortino ≥ 1.20, PBO <
   0.5, DSR_global p < 0.05).
10. **KILL_LOOP #10 (spyrv_strict_superset)** — fires if any spyrv
    config (slot 5 or 6) achieves `strict_superset=True`. **STRONGEST
    HYPOTHESIS TEST.** Pre-registered expectation: slot 6 (3-way OR
    composite) is most likely to achieve given it inherits both iter
    014 and iter 017 mechanisms.
11. **KILL_LOOP #11 (spyrv_2020_covid_rescue)** — fires if any spyrv
    config beats SPY in 2020_covid window. Pre-registered: SPY-RV-pct25
    onset signals during May-Dec 2020 might catch the V-recovery that
    iter 017 T40D60 missed (its rearm-window opened too late for the
    fast SPY V-bounce).
12. **KILL_LOOP #12 (spyrv_strict_superset_with_crisis_2plus)** —
    fires if any spyrv config achieves both `strict_superset=True` AND
    `crisis_count >= 2`. **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET
    TARGET** — would be the loop's most decisive Phase 3 result if
    achieved.

## Expected outcomes (pre-registered)

### Sortino_lh56y range
- Slot 1 (baseline): 1.3240 (anchor; ±0.005)
- Slot 2 (single anchor): 1.3951 (anchor; ±0.005)
- Slot 3 (basket3 anchor): 1.4689 (anchor; ±0.005)
- Slot 4 (T40D60 anchor): 1.4030 (anchor; ±0.005)
- Slot 5 (PRIMARY single+spyrv25): 1.36 to 1.45 (range — SPY-RV expansion
  may add upgrade activation that K4_AND_QLDlv25 misses; depends on
  fire-rate overlap)
- Slot 6 (STRONGEST 3-way OR): 1.40 to 1.50 (range — combines slot 4 +
  slot 5 mechanisms; theoretically max upgrade activation)

### CAGR_lh56y range
- Slot 5: 31.0% to 33.5% — should clear Phase 3 floor (31.08%)
- Slot 6: 32.5% to 34.5% — should beat slot 4's 32.66%

### Terminal end_eq vs baseline
- Slot 5: 1.10× to 1.55×
- Slot 6: 1.50× to 2.00× (combined effect)

### Rolling-window vs baseline (1y/3y/5y/10y)
- Slot 5: 5y win-rate 45-65%, 10y win-rate 30-50%
- Slot 6: 5y win-rate 50-70%, 10y win-rate 35-55%

### G1 PBO
- Target: < 0.50 (Phase 3 hard gate)
- Pre-registered range: 0.30 to 0.50 (5 distinct topology families)
- If G1 ≥ 0.55: KILL_LOOP #7 fires; HYPOTHESIS REJECTED (mechanism
  diversity inadequate).

### G2 DSR_local / DSR_global
- DSR_local p (n=6): expected p < 0.001 for slots 4/5/6
- DSR_global p (n=540): expected p < 0.05 for slots 5/6 if Sortino > 1.40

### Crisis attribution (per config)
- Slot 1: 1/4 (only 2008 GFC) — same as iter 017 baseline
- Slot 2-4: 1/4 (per iter 014/017 calibration)
- Slot 3: 3/4 (basket3 invvol crisis cushion)
- Slot 5: 1/4 to 2/4 (SPY-RV onset MAY catch 2020_covid if it triggers
  during May-Dec 2020 low-vol periods; CAVEAT: may also miss if
  SPY-RV-pct stayed elevated post-March 2020)
- Slot 6: 1/4 to 3/4 (combined effect; depends on rearm window timing
  and SPY-RV firing during recovery)

### Beats-winner / Phase 3 / strict_superset
- Pre-registered probability of slot 5 strict_superset: ~30%
- Pre-registered probability of slot 6 strict_superset: ~40%
- Pre-registered probability of slot 6 strict_superset WITH crisis ≥
  2/4: ~15% (loop's first such config; the contingent KILL_LOOP #12).

## INCOMPLETE flags / caveats

- **SPY-RV-pct vs QLD-vol-pct correlation:** if these signals are
  highly correlated in firing pattern, slot 5 may show only marginal
  return-series difference vs slot 2 → CSCV ranking-cluster → PBO
  regression. Pre-registered expectation: SPY-RV-pct will fire
  ~30-50% of the time slot 2's K4_AND_QLDlv25 fires, plus ~5-15%
  additional standalone fires (broader-market low-vol that QLD-vol
  misses). If overlap > 80%, slot 5 won't unlock new behavior.
- **Synth caveat:** SPYSIM (1962+) provides full lh_56y coverage for
  21d RV + 1260d (5y) percentile (first valid date ~1968). No data
  gap.
- **Look-ahead check:** SPY-RV-pct uses ONLY past data (rolling 21d std
  + rolling 1260d percentile rank). The strategy lag-shift convention
  (signals lagged 1 day inside `build_mechanism_mix_strategy_returns`)
  guarantees no look-ahead.
- **Tax/fees:** Gross returns only this iter; tax/fees stress deferred
  to a later diagnostic iter.
- **Turnover:** OR-combine across 3 upgrade triggers may increase
  turnover for slot 6. Will report and compare to iter 017 slot 5
  (5.32/y).
- **Replica-anchor coverage:** 4 of 6 slots are calibration anchors —
  slots 5 and 6 carry the actual hypothesis. The 4-anchor base is
  necessary for cross-iter reproducibility (KILL_LOOP #3, #4, #5, #6).

## Comparison with winner (T3d-K2)

To bat T3d-K2 (Sortino 1.3246), a config must clear:
- `sortino_lh56y > 1.3746` (anti-curve-fit margin +0.05)
- `winner_conditions_met = True` (all WINNER strict bars met)
- `pct_time_above_benchmark_lh56y >= 0.95`

To be `phase3_performance_candidate=True`:
- `cagr_lh56y > 0.3108`
- `end_equity_ratio_vs_winner > 1.05` (vs baseline; iter 017 convention)
- `sortino_lh56y >= 1.20`
- `g1_pbo < 0.50`
- `g2_dsr_p_cumulative < 0.05`

To be `strict_superset=True`:
- `beats_winner=True` AND `phase3_performance_candidate=True`

Loop's strict_superset roster (4 configs after iter 017):
1. iter 012 `..._tqqq_K4_AND_lv25_rvp70_cashx`
2. iter 014 `..._mmix_K4lv25_g0_rvp70_cashx` (iter 012 replica)
3. iter 014 `..._mmix_K4lv25_g25_rvp70_cashx`
4. iter 017 `..._rearm_single_K4lv25_g25_rvp70_cashx_T40D60` (NEW)

Iter 019 targets a 5th strict_superset (slot 5 or 6) on a NEW axis.

## Citations

**Primary:** `[volatility_trading, p.58-60]` Sinclair — volatility cone
framework: place current realised-vol within trailing distribution to
identify regime states. p.60 RULE: "Selling one-month implied volatility
at 35 percent because this is in the 90th percentile for one-month
volatility over the past two years can form the basis of a sensible
trading plan." (Same percentile-based regime gate logic, applied to
upgrade timing rather than option pricing.)

**Secondary:**
- `[leverage_for_the_long_run, p.4-7, ch.2-3]` Husson-Trifoni — "high
  volatility and seesawing action are the enemies of leverage while
  low volatility and streaks in performance are its friends." Low-vol
  regimes structurally favor LETF leverage harvesting.
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS leverage rotation
  rationale.
- `[volatility_trading, p.217-218]` Sinclair VIX-level filter (vol-
  regime gate analogue applied here at percentile level).
- `[stocks_on_the_move, p.98]` Clenow trend-strength (re-establishment
  of trend after low-vol regime onset).
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate (γ=0.25).
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[systematic_trading, p.212, ch.13]` Carver re-arm hysteresis (time-
  domain memory analogue applied to ENTRY leverage; iter 017 mechanism
  inherited in slot 6).
- `[advances_fin_ml, p.208-211]` PBO via CSCV — mechanism-mix-diversity
  recipe to maintain PBO < 0.50.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials
  (n_global=540).
- `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
