# 003-2026-05-09-calendar-halloween-gate — HYPOTHESIS

**Iter:** 003 / 50 (loop)
**Slug:** calendar-halloween-gate
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 438
**cumulative_n_trials_global after:** 444

## Hypothesis

The Halloween / "best 6 months" seasonal pattern (Hirsch *Stock Trader's Almanac*;
Bouman & Jacobsen 2002) documents that US equities have historically realized
the bulk of their risk premium between **November 1 and April 30**, with May-Oct
returning materially less and bearing a disproportionate share of crashes
(1929, 1987, 2008-Sep, 2020-Mar, 2022-Sep). The calendar gate is a slow,
exogenous (date-only) overlay that does not depend on price/vol — making it
mechanically orthogonal to the winner's existing vote-of-K signal stack
(SMA250, SMA100, vol_21d<40%, AR(1)_30d>0).

This iter tests three aggregation rules for incorporating a **monthly Halloween
gate** on top of the winner's vote-of-2 trend signal:

1. **Hard veto (configs 2, 3):** force OFF (ZROZ) for the seasonal-weak window
   regardless of vote-of-K. Two period definitions: classical Hirsch May-Oct
   (config 2) and a tighter "summer stall" Jun-Sep (config 3).
2. **Augmentation (configs 4, 5):** add the Halloween indicator (Nov-Apr = 1,
   May-Oct = 0) as a 5th vote member. Same K=2 (config 4: easier ON; calendar
   contributes a yes-vote in Nov-Apr) or stricter K=3 (config 5: calendar must
   concur with two other signals to go ON).
3. **Replacement (config 6):** swap AR(1)_30d>0 (the noisiest of the four
   votes) for the Halloween indicator while keeping K=2 of 4. Tests whether
   the seasonal signal is genuinely additive or just a worse copy of an
   existing fast vote.

Economic rationale (per [trading_systems_methods, p.479-481]): the seasonal
pattern is grounded in (a) tax-loss selling unwinds in late October, (b)
year-end pension/401k flows in November-December, (c) summer dispersion of
institutional decision-making and reduced liquidity. Bouman & Jacobsen
documented the effect in 36 of 37 markets studied — robustness across
geographies argues against pure data mining.

The 2022_rates loss (which iter 002 failed to rescue) is a Halloween-window
event: NDX peaked Nov-21, fell continuously through Oct-22 — a calendar gate
forced OFF in May-Oct 2022 would have escaped the worst of the bear.
Conversely, the 2020 COVID crash (Mar-2020) is *inside* the Nov-Apr "good"
period — calendar gate would have stayed ON, missing the rescue. So the
hypothesis is asymmetric: rescue 2022 at the cost of paying through 2020.
Net Sortino contribution depends on which crisis-cost dominates.

## Citations

**Primary:** `[trading_systems_methods, p.479-481]` — Hirsch best-6-months
calendar rules; Holiday/Turn-of-month strategies; "buy Nov 1, sell Apr 30."

**Secondary:**
- `[trading_systems_methods, p.480]` — Hirsch rule: "Buy first trading day of
  November; sell last trading day of April."
- `[evidence_based_ta, p.398]` — Aronson MLM Index (12-month MA on 25
  commodities) as evidence that monthly-aggregation seasonal rules can be
  deployed without curve-fitting when grounded in economic rationale (risk
  premium for service to hedgers).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2/global
  denominator = 438 + 6 = 444 after this iter).
- `[systematic_trading, p.180-190]` — Carver carry / regime filter as the
  shape-of-overlay precedent (this iter applies a date-based overlay; iter 001
  applied a yield-curve overlay; iter 002 applied a vol-DD overlay).

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` on QLDSIM and the OFF asset ZROZSIM (winner replica).
The calendar layer is applied on top per config rule.

| # | Name | Calendar rule | Aggregation | Period |
|---|---|---|---|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_cal_off` | none | baseline | — |
| 2 | `qld_voteK2_..._cal_veto_may_oct` | force OFF May-Oct | hard veto | May-Oct |
| 3 | `qld_voteK2_..._cal_veto_jun_sep` | force OFF Jun-Sep | hard veto (narrower) | Jun-Sep |
| 4 | `qld_voteK2_..._cal_5vote_K2of5_may_oct` | Nov-Apr=1, May-Oct=0 as 5th vote | augment K=2 of 5 | May-Oct |
| 5 | `qld_voteK2_..._cal_5vote_K3of5_may_oct` | same 5th vote | augment K=3 of 5 (stricter) | May-Oct |
| 6 | `qld_voteK2_..._cal_replace_ar_may_oct` | swap AR(1) vote for Halloween | replacement K=2 of 4 | May-Oct |

The single sweep dimension is "**how to inject the Halloween signal**":
veto (over-rules vote-of-K), augment (joins vote-of-K), or replace (substitutes
a weaker vote member).

Signal lag (1-day) preserved: the calendar gate computed at close of t-1 (i.e.
month-of-date(t-1)) applies to allocation at open of t. This is mechanically
identical to the lag convention used by all other gates in the winner.

## Datasets

Mirrors closed-study set for direct comparability:
- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/ZROZSIM/CASHX)
- `modern_1990`: 1990-01-01 → 2026-04-30
- `spy_real`: 2003-01-01 → 2026-04-30 (real SPY post-inception)
- `ndx_real`: 2010-02-01 → 2026-04-30 (real QQQ post-inception)

The Halloween effect was studied primarily on monthly cash-equity total returns
1970-2000 (Bouman-Jacobsen sample). lh_56y has a clean overlap with that
training period AND extends out-of-sample into 2001-2026 — directly addresses
post-publication decay concerns.

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner test").
- **KILL_LOOP #2 (decisive-fail):** if all 5 calendar variants return
  Sortino_lh56y < 1.10 → calendar/seasonal master-gate family is dead in this
  context; pivot next iter to a fundamentally different mechanic (e.g.
  cross-asset correlation regime, multi-asset rotation, breadth indicator).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (baseline replica)
  Sortino_lh56y differs from 1.2841 (iter 001/002 replica baseline) by > 0.05
  absolute → engine drift; flag INCOMPLETE and trust comparative deltas
  across configs only.
- **KILL_LOOP #4 (over-suppression):** if any calendar variant's
  pct_time_above_benchmark_lh56y drops below 0.85 → calendar-OFF is too
  aggressive (forcing OFF for half the year leaves SPY ahead too often).
  Tag config "OVER_SUPPRESS" in SUMMARY — informational only.

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.05–1.40 across all 6 configs.
- **Best plausible scenario:** config 4 (`5vote_K2of5_may_oct`) gains
  ~0.02–0.06 Sortino over baseline by acting as a soft tilt — calendar adds
  a yes-vote in Nov-Apr (relaxing K=2 boundary) without forcing OFF in
  benign May-Oct periods. Config 6 (replacement) is also plausible if AR(1)
  is genuinely the noisiest existing vote.
- **Plausible failure mode (most likely):** hard-veto configs (2, 3) reduce
  Sortino because they force OFF during legitimate May-Oct rallies (1995,
  2009 May-Aug, 2020 May-Oct, 2024 summer); the 2022 rescue does not pay for
  the false positives across 56 years.
- **Most realistic outcome:** tier PROMISING/STRONG with sortino_edge
  in [-0.10, +0.05] band — useful negative result if no veto config beats;
  useful positive result if augmentation (configs 4-5) shows clean tilt.
- **WC compliance:** veto configs (2-3) likely break WC (mean
  pct_time_above_benchmark < 0.95 because hard-OFF in May-Oct accumulates
  underwater periods vs SPY); augment/replace configs (4-6) more likely to
  preserve WC.
- **Beats-winner probability:** **~10-15%**. The Halloween effect's
  in-sample Sortino bump is well-documented (~0.10) but published edges decay
  post-publication. To clear the +0.05 anti-curve-fit margin AND maintain
  pct_time_above_benchmark ≥ 0.95 is a conjunction event. G1 PBO is the
  binding constraint as in iter 001 (single-axis 6-config sweep).

## INCOMPLETE flags / caveats

- **Calendar gate is an exogenous date function — robust to look-ahead.**
  Implementation uses `index.month` of t-1 to determine the gate at t. No
  forward-looking information leakage possible by construction.
- **Hirsch's exact definition is "first/last trading day"; we use
  whole-month boundaries.** Inserting/removing the boundary days would change
  the gate value on at most ~24 days/year — material impact on annualised
  metrics is < 0.005 Sortino. Not swept here.
- **Synth caveat (pre-1985):** pre-1985 QLDSIM is formula-derived; calendar
  gate fires deterministically regardless of synth quality, so the gate
  contributes the same on/off pattern across all configs — comparative
  deltas remain valid.
- **Tax/fees:** gross only this iter (matching closed-study convention).
- **Single-axis G1 PBO concern:** the 6-config grid varies along
  one axis (calendar aggregation rule + period), so G1 PBO ≈ iter 001's
  0.575 is plausible. We accept this; iter 002 demonstrated G1 cleans up
  when the calendar gate's mechanic is structurally orthogonal to other
  configs' mechanics. Within iter 003 alone, configs 2-6 share a calendar
  layer but vary the *interaction rule* with vote-of-K — modest CSCV
  variation expected.
- **Hirsch vs Bouman-Jacobsen period definitions match (May-Oct vs Nov-Apr
  endpoints)**; the Jun-Sep "summer stall" variant is not in the canonical
  literature but is a tighter definition that targets the
  Aug-Sept-historically-worst-pair without the May-Apr edges.

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
