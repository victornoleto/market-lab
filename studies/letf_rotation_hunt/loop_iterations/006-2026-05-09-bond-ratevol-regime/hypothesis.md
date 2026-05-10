# 006-2026-05-09-bond-ratevol-regime — HYPOTHESIS

**Iter:** 006 / 50 (loop)
**Slug:** bond-ratevol-regime
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 456
**cumulative_n_trials_global after:** 462

## Hypothesis

The 2022_rates loss has been **the single unrescued crisis across iters
001–005** of the loop. Diagnosis from iter 005: the failure is duration
risk on the OFF leg — ZROZ (≈ 27y duration) lost ≈ -38% in 2022 even as
the trend signal correctly flipped OFF. Cross-asset overlays (correlation
gate iter 004; multi-asset basket iter 005 with UGL) cannot help because
during 2022 USD-strength + real-rate rebound the entire risk-asset complex
fell **including** gold, intermediate Treasuries, and TIPS.

The orthogonal angle is **own-asset second moment**: bond market vol
itself is the leading indicator of duration repricing stress
(`[volatility_trading, p.58-60]` Sinclair on volatility cones — current
realised vol placed against historical percentile is the canonical
regime-detection primitive; the same structural argument the MOVE-index
literature makes for Treasury vol). The 2022 episode was preceded by a
multi-month spike in ZROZ realised vol — by Q1-2022 ZROZ 60d vol was at
its 95th percentile of the trailing 5y window.

This iter tests whether a **bond rate-vol regime master-gate** that
monitors ZROZ realised vol percentile and **switches the OFF leg from
ZROZ (long-duration) to a shorter-duration alternative (CASHX or
IEFSIM)** can rescue 2022 without sacrificing 2008/2020 (where ZROZ
delivered its diversification benefit).

The mechanic is **orthogonal to all prior loop iters**:

| Iter | Mechanic | Information used |
|---|---|---|
| 001 | yield-curve OFF rotation | term-premium **level** (10y−3m slope) |
| 002 | vol-DD killswitch | own-strategy magnitude |
| 003 | calendar / Halloween | exogenous date function |
| 004 | ρ(QLD, ZROZ) regime | **cross-asset** second moment |
| 005 | multi-asset ON inverse-vol | cross-asset **first** moment (basket) |
| **006** | **ZROZ vol percentile gate** | **own-asset second moment of OFF leg** |

The closest cousin is iter 001 (also touches OFF-leg routing), but iter
001 used the *level* of the yield curve (10y−3m) — a cross-sectional
fundamental — whereas iter 006 uses *bond price volatility percentile* —
a time-series statistical regime. Different signal class entirely.

## Citations

**Primary:** `[volatility_trading, p.58-60]` — Sinclair on the volatility
cone: place current realised vol against the historical percentile
distribution. *"Selling one-month implied volatility at 35 percent
because this is in the 90th percentile for one-month volatility over the
past two years can form the basis of a sensible trading plan"*
(`[volatility_trading, p.60]`). This iter applies the same percentile-
threshold primitive to ZROZ realised vol.

**Secondary:**

- `[systematic_trading, p.212, ch.13]` — Carver semi-automatic stop using
  X*sigma from tracking extreme. Same structural pattern: vol-scaled
  threshold on a regime variable. Iter 002 already used Carver's
  X*sigma-DD on the *strategy* itself; this iter applies the same family
  of vol-scaled regime detection to the *OFF asset's own vol*.
- `[risk_parity, p.110, ch.5]` — Qian on diversification return:
  $e_v = -0.5 \cdot w_1 w_2 \cdot 2\rho_{12}\sigma_1\sigma_2$. When
  bond $\sigma_2$ spikes (2022-style), the diversification return drops
  even at fixed correlation — direct mechanism for why ZROZ-vol
  regime detection should add value separately from iter 004's
  correlation gate.
- `[ml_for_algo_trading, ch.9]` — Jansen on rolling state features /
  time-series regime classification. Rolling percentile of realised vol
  is a canonical feature.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (G2 / global denominator = 456 + 6 = 462 after this iter).

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` on QLDSIM (winner replica). The OFF asset and
the rate-vol regime override differ per config across **3 orthogonal
mechanic axes** (mirrors iter 004's clean-PBO grid design):

| # | Name | Vol pct | Vol window | Alt OFF |
|---|---|---:|---:|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_ratevol_off_baseline` | — | — | (none / always ZROZ) |
| 2 | `qld_voteK2_..._ratevol_p70_60d_to_cashx` | 70th | 60d | CASHX |
| 3 | `qld_voteK2_..._ratevol_p80_60d_to_cashx` | 80th | 60d | CASHX |
| 4 | `qld_voteK2_..._ratevol_p80_120d_to_cashx` | 80th | 120d | CASHX |
| 5 | `qld_voteK2_..._ratevol_p70_60d_to_ief` | 70th | 60d | IEFSIM |
| 6 | `qld_voteK2_..._ratevol_p80_60d_to_ief` | 80th | 60d | IEFSIM |

The grid varies along **3 mechanic axes** (not single-axis): percentile
threshold (p70 vs p80), vol-measurement window (60d vs 120d), and
alt-OFF asset (CASHX vs IEFSIM). This is the design lesson from iter
004 (PBO 0.071, the loop's cleanest) and iter 005 (single-axis grid →
PBO 0.881, polluted).

**Gate definition:** at close of t-1, compute ZROZ daily-return realised
vol over `vol_window` days, then compute its percentile within the
trailing 5y (1260d) window. Gate fires (`=1`) iff percentile > threshold.
At open of t: if OFF state AND gate fired → route to alt OFF; if OFF
state AND gate not fired → ZROZ; if ON state → QLD. Master-scope is
explicitly **NOT** tested (iter 004 confirmed master overrides destroy
Sortino — KILL #4 over-suppression fired).

5y warmup: gate is NaN before 1975-01-01 in lh_56y (1970 + 1260d). For
that warmup window the strategy uses the baseline rule (no override).

Signal lag (1-day) preserved: vol-percentile computed at close of t-1
applies at open of t — same convention as the winner's other gates.

## Datasets

Mirrors closed-study set for direct comparability:

- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/ZROZSIM/CASHX/IEFSIM)
- `modern_1990`: 1990-01-01 → 2026-04-30
- `spy_real`: 2003-01-01 → 2026-04-30
- `ndx_real`: 2010-02-01 → 2026-04-30

The bond rate-vol regime is most informative in 1979-1981 (Volcker
disinflation), 1994 (Greenspan rate shock), 2008-2009 (flight-to-quality
+ MBS dislocation), 2013 (taper tantrum), and 2022 (rate-hike shock) —
multiple high-vol regime crossings within lh_56y provide statistical
content. Pre-1985 ZROZSIM synth-prior'd vols are mechanically tied to
the synth assumptions but the *percentile-rank* structure is preserved.

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner
  test"). Probability assessed below.
- **KILL_LOOP #2 (decisive-fail):** if all 5 ratevol-gate variants return
  Sortino_lh56y < 1.10 → bond rate-vol regime gating is dead in this LETF
  context; pivot next iter to a fundamentally different mechanic
  (e.g. VIX-percentile / VRP overlay, breadth indicators, equity factor
  tilts).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (baseline replica)
  Sortino_lh56y differs from 1.2841 (iters 001/002/003/004/005 baseline)
  by > 0.05 absolute → engine drift; flag INCOMPLETE and trust comparative
  deltas across configs only.
- **KILL_LOOP #4 (over-suppression):** if any ratevol-gate variant's
  pct_time_above_benchmark_lh56y drops below 0.85 → gate routes to
  shorter-duration too aggressively. Tag config "OVER_SUPPRESS"
  informationally.
- **KILL_LOOP #5 (ratevol-non-event):** if all 5 ratevol-gate variants
  have `ratevol_active_pct_lh56y < 5%` (gate fires < 5% of trading
  days post-warmup) → unfalsifiable; tag UNDERPOWERED.

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.20–1.40 across all 6 configs.
- **Best plausible scenario:** config 5 (`ratevol_p70_60d_to_ief`) gains
  +0.04–0.08 Sortino over baseline by sidestepping 2022 (ZROZ vol was at
  its 95th-percentile from late-2021 onwards) without giving up too much
  in 2008/2020 (where ZROZ vol also spiked but the OFF leg was
  benefiting from the duration rally). IEF (≈ 7y duration) retains
  partial duration exposure, so it captures *some* flight-to-quality in
  2008/2020 while limiting 2022 damage. CASHX configs likely
  under-perform because they give up all bond carry during gate-fire
  periods, and 2008-Q4 / 2020-Q1 ZROZ vol spikes were *up* moves
  (sharp duration rally) that CASHX would miss.
- **Plausible failure mode (most likely):** ZROZ vol-percentile is
  *correlated* with own-strategy regime (vol_21d<40% gate already flips
  OFF→ON during equity high-vol; ZROZ vol spikes often coincide with
  equity vol spikes). The marginal information may be small after the
  vote-K=2 gate is already considering equity vol. In that case all
  configs cluster within ±0.03 Sortino of baseline.
- **Most realistic outcome:** tier PROMISING/STRONG with
  sortino_edge in [-0.05, +0.05] band. The single 2022 rescue (which
  would gain ≈ 0.03-0.04 lh_56y Sortino if successful) can plausibly
  clear the +0.05 anti-curve-fit margin **only** if the gate doesn't
  simultaneously sacrifice the 2008/2020 ZROZ rally.
- **WC compliance:** OFF-leg-only configs likely preserve WC because
  the override fires only during defensive periods. No master-scope
  configs tested (lesson from iter 004 KILL #4).
- **Beats-winner probability:** **~10-15%**. The mechanism is genuinely
  new (own-asset OFF vol regime) and Sinclair's volatility-cone primitive
  is well-grounded. BUT the conjunction (Sortino > 1.3746 AND WC met
  AND pct_above ≥ 0.95) is hard. Most likely outcome is a small
  positive Sortino edge that doesn't clear the +0.05 margin —
  informative for hypothesis-discrimination but not deploy candidate.

## INCOMPLETE flags / caveats

- **Rate-vol percentile gate is computed at close of t-1 with 1-day
  lag** — no forward-looking leakage by construction. The 5y rolling
  percentile means the gate state in early-2022 reflects the
  pre-Jan-2022 vol distribution; partial warmup is expected for the
  2022 rescue specifically.
- **5y warmup:** lh_56y dataset starts 1970-01-01 but rolling-percentile
  rank requires 1260d (5y) of vol history. Gate is NaN until ~1975, so
  the strategy uses baseline (always-ZROZ) routing for that period
  (≈ 5/56 ≈ 9% of lh_56y window). Comparative deltas across configs
  remain valid because all configs see the same warmup baseline.
- **Synth caveat (pre-1985):** ZROZSIM is a duration-aware synthetic
  long-treasury proxy from testfolio. The pre-1985 ZROZ vol is
  mechanically tied to synth assumptions, but its *rank* within a
  rolling 5y window is preserved by construction. IEFSIM same caveat.
- **Tax/fees:** gross only this iter (matching closed-study convention).
  CASHX returns FFR-tracked; rotation to CASHX during high-rate periods
  earns substantial yield (e.g. 2007 5%, 2024 5.5%). IEFSIM tracks
  intermediate Treasury total return.
- **Threshold values are not arbitrary:** 70th and 80th percentile are
  Sinclair's classical regime cutoffs in vol-cone literature
  (`[volatility_trading, p.60]`). Sweep covers 2 interpretable cuts at
  fixed window 60d, plus 1 window-extension test at p80 fixed. We
  do **NOT** sweep finer percentiles (p65/p75/p85) — that would inflate
  trial count without adding interpretive value.
- **Window choice (60d vs 120d):** 60d is the standard regime-detection
  window; 120d is half-year, slower, more stable. Sinclair's vol cone
  uses 20/40/60/120/240 — we test 60 and 120 only.
- **Single 2022_rates target:** ratevol-regime is hypothesis-targeted
  at the 2022 dual-fall, NOT a pan-crisis rescue. Modest 1979-1981
  improvement (Volcker) plausible because ZROZ vol was extreme;
  modest 1994-rate-shock improvement plausible; 2008/2020 may *suffer*
  if gate fires during ZROZ rally (potential trade-off).
- **No master-scope tested** — iter 004 confirmed master overrides fire
  KILL_LOOP #4 universally (Sortino collapse). Save trial budget by
  skipping that mechanism class.

## Beats-winner test (frozen per protocol §"Beats-winner test")

```python
beats_winner = (
    sortino_lh56y > 1.3746              # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met
    and pct_time_above_benchmark_lh56y >= 0.95
)
sortino_edge_vs_winner = sortino_lh56y - 1.3246
```

`winner_benchmark_sortino = 1.3246`,
`winner_benchmark_iter = "022-2026-05-06-T3d-extended-grid"`,
`winner_benchmark_config = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"`.
