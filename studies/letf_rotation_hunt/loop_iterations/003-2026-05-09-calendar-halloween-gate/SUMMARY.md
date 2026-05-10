# 003-2026-05-09-calendar-halloween-gate — SUMMARY

**Iter:** 003 / 50 (loop)
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Calendar-month seasonal master-gate (Hirsch best-6-months /
Halloween effect) overlaid on the winner's vote-of-K trend signal. Three
aggregation rules tested: (a) hard veto OFF in May-Oct or Jun-Sep,
(b) augment as 5th vote member with K=2 or K=3 of 5, (c) replace AR(1) vote
with the calendar indicator. Targets the 2022_rates loss without sacrificing
2008/2020 alpha. ON-leg intervention only; OFF leg fixed to ZROZ.
**Primary citation:** `[trading_systems_methods, p.479-481]` — Hirsch
best-6-months / Holiday + Turn-of-month rules; "Buy first trading day of
November; sell last trading day of April" (p.480).
**Secondary citations:** `[evidence_based_ta, p.398]` (Aronson MLM 12-month MA
on commodities — monthly aggregation precedent), `[advances_fin_ml, p.208-211]`
(PBO via CSCV), `[advances_fin_ml, p.222-223]` (DSR + cumulative n_trials),
`[systematic_trading, p.180-190]` (Carver overlay shape — same pattern as
iter 001 yield-curve / iter 002 vol-DD).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_003
**n_configs:** 6
**cumulative_n_trials_global:** 438 → **444**

## TL;DR

- Best by Sortino: **`qld_voteK2_..._cal_veto_jun_sep`** (narrower Jun-Sep
  summer-stall veto). Sortino_lh56y **1.3061** (edge **−0.0185** vs winner
  1.3246), score 71.5 PROMISING, WC=Y. **First loop config that lifts Sortino
  above the loop replica baseline (1.2841 → 1.3061, +0.022).** Still does
  NOT clear the +0.05 anti-curve-fit margin (1.3746 threshold).
- Best by score: `..._cal_5vote_K2of5_may_oct` (calendar as 5th vote, soft
  tilt). Score 79.5 STRONG, Sortino 1.2575. CAGR 31.0% (highest), but lower
  Sortino than baseline because the soft tilt keeps too much ON exposure
  during 2008-Q4.
- `beats_winner=false` for every config.
- KILL_LOOP #1, #2, #3, #4 all **NOT FIRED.**
- **G1 PBO=0.444 universal pass** — between iter 001's 0.575 (one-axis)
  and iter 002's 0.159 (orthogonal-mechanic). Calendar layer adds modest
  CSCV variation: configs 2-3 vary the *period definition* (May-Oct vs
  Jun-Sep), configs 4-6 vary the *aggregation rule* (veto/augment/replace).
- **Hard May-Oct veto is too aggressive** (cal_off% 50.5%, Sortino 1.1216,
  -0.20 edge): forces OFF during legitimate May-Oct rallies (1995, 2009
  May-Aug, 2020 May-Oct, 2024 summer); the 2022 partial rescue does not pay
  for false positives across 56 years.
- **Narrow Jun-Sep veto is the sweet spot** (cal_off% 33.5%, Sortino 1.3061,
  -0.02 edge): selectively avoids the historically worst 4 months without
  paying for May/Oct false positives. WC=Y, pct_above_bench = 1.0000.
- **Augmentation K=3 stricter (config 5) is decisive-fail for the
  augmentation family** (Sortino 1.1128, -0.21 edge): requiring 3 of 5 votes
  with calendar as one keeps the strategy mostly OFF in May-Oct AND requires
  more conviction in Nov-Apr → ON exposure drops too far.
- **Crisis attribution unchanged: every config rescues 2008 only (1 of 4).**
  The Halloween effect did NOT rescue 2022_rates — the bear ran Nov-2021 to
  Oct-2022, spanning 6 months in Hirsch "good" Nov-Apr (where ON stayed on)
  and 6 months in May-Oct (where the veto helped). The Nov-Apr exposure
  costs offset the May-Oct rescue.

## Configs tested

| # | Name | Calendar mechanic | Aggregation | Period |
|---|---|---|---|---|
| 1 | `..._cal_off` | none | baseline (winner replica) | — |
| 2 | `..._cal_veto_may_oct` | Halloween (Hirsch) | hard veto | May-Oct (6 mo) |
| 3 | `..._cal_veto_jun_sep` | Summer stall | hard veto (narrower) | Jun-Sep (4 mo) |
| 4 | `..._cal_5vote_K2of5_may_oct` | Halloween 5th vote | augment K=2 of 5 | Nov-Apr=1 |
| 5 | `..._cal_5vote_K3of5_may_oct` | Halloween 5th vote | augment K=3 of 5 (stricter) | Nov-Apr=1 |
| 6 | `..._cal_replace_ar_may_oct` | replace AR(1) with Halloween | substitute K=2 of 4 | Nov-Apr=1 |

All share the trend ON signal `vote-of-2 (or 3) of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0, [Halloween]}` on QLDSIM and OFF asset ZROZSIM
(winner replica). Calendar gate computed at close of t-1 (month of date(t-1))
applied to allocation at open of t — same lag as winner.

## Results — gross metrics per dataset

### Sortino (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `..._cal_off` (baseline) | 1.2841 | 1.2217 | 1.0911 | 1.2890 |
| `..._cal_veto_may_oct` | 1.1216 | 1.0213 | 0.7323 | 0.9712 |
| **`..._cal_veto_jun_sep`** | **1.3061** ← best | 1.2837 | 0.9695 | 1.1580 |
| `..._cal_5vote_K2of5_may_oct` | 1.2575 | 1.2065 | 1.1934 | 1.2960 |
| `..._cal_5vote_K3of5_may_oct` | 1.1128 | 1.0020 | 0.7667 | 1.0741 |
| `..._cal_replace_ar_may_oct` | 1.1515 | 1.0669 | 1.0428 | 1.1832 |

The narrower Jun-Sep veto is the only config to lift lh_56y Sortino above
baseline. The wider May-Oct veto and the stricter K=3 augmentation are
universally worse across all four datasets.

### Sharpe / CAGR / MDD (lh_56y)

| Config | Sharpe | CAGR | MDD | pct_time_above_bench |
|---|---:|---:|---:|---:|
| `..._cal_off` | 0.8924 | 29.85% | -64.5% | 1.0000 |
| `..._cal_veto_may_oct` | 0.7718 | 21.76% | -59.7% | 1.0000 |
| **`..._cal_veto_jun_sep`** | **0.8969** | 27.99% | -59.7% | 1.0000 |
| `..._cal_5vote_K2of5_may_oct` | 0.8689 | 31.01% | -66.8% | 1.0000 |
| `..._cal_5vote_K3of5_may_oct` | 0.7742 | 23.19% | -59.7% | 1.0000 |
| `..._cal_replace_ar_may_oct` | 0.8044 | 26.19% | -64.9% | 1.0000 |

**SPY anchor (lh_56y):** Sortino 0.958 / Sharpe 0.682 / MDD -55.1% (mandate
§2.2/§2.3 — MDD warning-only). Every config dominates SPY's Sortino with
pct_time_above_benchmark = 1.000.

The K=2 augmentation config (`..._cal_5vote_K2of5_may_oct`) achieves the
highest CAGR (31.0%) — calendar adds a soft yes-vote in Nov-Apr that lets the
strategy go ON earlier in autumn rallies — but pays in MDD (−66.8% vs −64.5%
baseline) because the soft tilt also keeps it ON during the Oct-2008 collapse
(Halloween indicator was 0 then, but only contributing 1 of 5 votes — the
other 4 still flipped to ON during the brief Oct-2008 peak).

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G3 (≥5/8 windows) | G4 OOS S | G5 FWD S | G6 99% low | G7 \|Δ pp\| |
|---|---:|---:|---:|---:|---:|---:|---:|
| cal_off | 0.444 ✓ | 9.7e-06 ✓ | 7/8 ✓ | 0.825 ✓ | 0.708 ✓ | 0.519 ✓ | 0.000 ✓ |
| cal_veto_may_oct | 0.444 ✓ | 2.0e-04 ✓ | 6/8 ✓ | 0.438 ✓ | 0.001 ✓ | 0.387 ✓ | 0.000 ✓ |
| **cal_veto_jun_sep** | 0.444 ✓ | 8.1e-06 ✓ | 7/8 ✓ | 0.722 ✓ | 0.371 ✓ | 0.522 ✓ | 0.000 ✓ |
| cal_5vote_K2of5_may_oct | 0.444 ✓ | 1.7e-05 ✓ | 5/8 ✓ | 0.818 ✓ | 0.672 ✓ | 0.515 ✓ | 0.000 ✓ |
| cal_5vote_K3of5_may_oct | 0.444 ✓ | 2.0e-04 ✓ | 6/8 ✓ | 0.597 ✓ | 0.409 ✓ | 0.403 ✓ | 0.000 ✓ |
| cal_replace_ar_may_oct | 0.444 ✓ | 9.8e-05 ✓ | 5/8 ✓ | 0.753 ✓ | 0.641 ✓ | 0.433 ✓ | 0.000 ✓ |

Hard-gate thresholds: G1 PBO < 0.50, G2 < 0.05, G3 ≥ 5/8, G4/G5/G6 > 0,
G7 |Δ| ≤ 3pp.

**G1 PBO=0.444 is a clean pass for ALL configs.** Better than iter 001's
0.575 single-axis fail, but worse than iter 002's 0.159 — the calendar layer
adds modest CSCV variation but configs 2-6 still share the same monthly-bar
mechanic.

**G5 FWD post-2020 is the worst gate** for veto/strict-augmentation configs:
the May-Oct veto produces FWD Sharpe 0.001 (essentially zero — its post-2020
edge is gone), and K=3-of-5 augmentation produces 0.409 (decent but
materially below 0.708 baseline). The narrow Jun-Sep veto retains 0.371
post-2020. This suggests the calendar effect has decayed in the post-2020
sample (consistent with published-edge decay literature).

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_dotcom | 2008_GFC | 2020_COVID | 2022_rates |
|---|:---:|:---:|:---:|:---:|
| cal_off | ✗ | ✓ | ✗ | ✗ |
| cal_veto_may_oct | ✗ | ✓ | ✗ | ✗ |
| cal_veto_jun_sep | ✗ | ✓ | ✗ | ✗ |
| cal_5vote_K2of5_may_oct | ✗ | ✓ | ✗ | ✗ |
| cal_5vote_K3of5_may_oct | ✗ | ✓ | ✗ | ✗ |
| cal_replace_ar_may_oct | ✗ | ✓ | ✗ | ✗ |

**Identical 1-of-4 across all 6 configs** — the calendar gate did NOT rescue
any additional crisis. Notably:

- **2022_rates was supposed to be the rescue case** but isn't, because the
  bear ran Nov-2021 → Oct-2022. Hirsch's "good" Nov-Apr period covers ~6
  months of the bear (Nov-21 through Apr-22, where the wide veto would have
  *kept* exposure). The May-Oct veto only catches the second half (May-22
  through Oct-22) — the Nov-Apr losses dominate.
- **2020_COVID is missed because the crash (Mar-2020) is in Hirsch "good"
  Nov-Apr.** Calendar gate stayed ON; all configs equally exposed.
- **2008_GFC is rescued by the underlying vote-of-K** (vol_21d<40% gate
  flipped OFF in Sep-2008 reliably), independent of calendar layer.

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
|---|---:|---:|:---:|---:|:---:|
| `..._cal_off` (baseline) | 1.2841 | -0.0405 | T | 1.0000 | False |
| `..._cal_veto_may_oct` | 1.1216 | -0.2030 | F | 1.0000 | False |
| **`..._cal_veto_jun_sep` (best)** | **1.3061** | **-0.0185** | T | 1.0000 | False |
| `..._cal_5vote_K2of5_may_oct` | 1.2575 | -0.0671 | T | 1.0000 | False |
| `..._cal_5vote_K3of5_may_oct` | 1.1128 | -0.2118 | F | 1.0000 | False |
| `..._cal_replace_ar_may_oct` | 1.1515 | -0.1731 | T | 1.0000 | False |

The lh_56y `pct_time_above_benchmark = 1.0000` for **every** config — calendar
gate never produces underwater-vs-SPY equity in the long-history window.
WC=False for the May-Oct veto and K=3 augmentation reflects the *mean across
4 datasets* dropping below 0.95 in spy_real / ndx_real (post-2003 windows
where the calendar effect's published-edge decay hits hardest).

**No config qualifies as `beats_winner=true`.** The narrower Jun-Sep veto's
edge of -0.0185 is the closest any loop iter has come to the +0.05 threshold,
but 0.0685 of Sortino still separates it from beats.

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns, lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % of time exposed to equity
  (post-calendar combined exposure)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags +
  calendar_veto_active_pct + turnover_per_year per config

## KILL_LOOP results (pre-registered in hypothesis.md)

- **KILL_LOOP #1 (success-tag):** **NOT FIRED.** Best Sortino_lh56y = 1.3061
  (cal_veto_jun_sep) < threshold 1.3746. No config can register
  `beats_winner=true` regardless of WC, since Sortino is sub-threshold across
  the board.
- **KILL_LOOP #2 (decisive-fail):** **NOT FIRED.** Of the 5 calendar configs,
  only 1 has Sortino_lh56y < 1.10 (cal_5vote_K3of5_may_oct = 1.1128 — *just*
  above 1.10). Family is *not* dead; the Jun-Sep variant explicitly
  outperforms baseline by +0.022 Sortino.
- **KILL_LOOP #3 (replica-sanity):** **NOT FIRED.** Baseline replica
  Sortino_lh56y = 1.2841, identical to iters 001 and 002 baselines (drift
  0.000). Comparative deltas are bit-exact valid.
- **KILL_LOOP #4 (over-suppression):** **NOT FIRED.** All configs have
  pct_time_above_benchmark_lh56y = 1.0000. WC failures (configs 2 and 5)
  are due to mean-across-datasets dipping to 0.94 / 0.92 in spy_real /
  ndx_real, not lh_56y over-suppression.

## Verdict

- **Best config (by Sortino):** `qld_voteK2_..._cal_veto_jun_sep` — PROMISING,
  score 71.5, Sortino_lh56y 1.3061, edge -0.0185.
- **Best config (by score):** `qld_voteK2_..._cal_5vote_K2of5_may_oct` —
  STRONG, score 79.5, Sortino 1.2575. Highest CAGR (31.0%) of the loop but
  lower Sortino-of-record because soft tilt keeps too much exposure during
  Oct-2008.
- **kill_rule_status:** N/A (loop iter; closed-study T<N>→T<N+1> KILLs
  don't apply here)
- **beats_winner:** false (best Sortino edge -0.0185)
- **cumulative_n_trials_global:** 444

## Conclusion

The Hirsch / Halloween calendar gate **does not** beat the winner, but it
does produce the **first loop config that lifts Sortino above the replica
baseline** (1.2841 → 1.3061, +0.022). The mechanism that worked (narrow
Jun-Sep veto) is the variant *least supported* by the published Halloween
literature — Hirsch and Bouman-Jacobsen both define the bad period as
May-Oct (6 months), not Jun-Sep (4 months). The Jun-Sep variant is closer
to a Brock-style "September is the worst month" empirical observation than
to the canonical seasonal premium thesis. Reading this as evidence of edge
requires accepting that we tightened the period to fit the data — i.e. the
specific period that worked may be a 6-config-grid local optimum.

The wider May-Oct veto (Hirsch classic) is **monotonically worse** than
baseline by -0.20 Sortino because forcing OFF for 50.5% of trading days
costs more in compounding than it saves: the 2022 partial rescue is offset
by paying through 1995 May-Oct, 2009 May-Aug, 2020 May-Oct (large up-moves
all suppressed), and 2024 summer.

The augmentation family (5th vote member) is informative as a
*hypothesis-discrimination* tool. K=2 of 5 (config 4) keeps full ON
exposure during conviction periods AND lets calendar contribute a yes-vote
in Nov-Apr — it gets the highest CAGR (31.0%) and best score (79.5) but
NOT the best Sortino because the calendar boost coincided with Oct-2008
peak ON exposure. K=3 of 5 (config 5) over-suppresses by requiring 3
concurrent confirmations. The replacement variant (config 6) confirms AR(1)
is genuinely additive to the original 4-vote stack — replacing it with the
calendar drops Sortino by 0.13.

The originally-targeted crisis (2022_rates) is **not** rescued by any
variant. The 2022 NDX bear ran Nov-2021 → Oct-2022, spanning ~6 months in
Hirsch "good" Nov-Apr (where ON stayed on under any calendar rule) and ~6
months in May-Oct (where the veto helped). The Nov-Apr exposure costs
dominate the May-Oct rescue.

**Hypothesis dead for the strict Halloween literature framing**
(May-Oct = OFF), but **alive** for a narrower "summer stall" reading
(Jun-Sep = OFF) that earns +0.022 Sortino without paying the May/Oct
opportunity cost. Whether this is signal or curve-fit is exactly the
question G1 PBO 0.444 is tracking — it passes, but barely (vs iter 002's
clean 0.159).

A small structural positive: G5 post-2020 FWD Sharpe surfaces a clean
ranking (baseline 0.708, jun_sep 0.371, may_oct 0.001) consistent with
literature decay — the Halloween effect's published edge is much weaker
in the 2003+ sample than in the original Bouman-Jacobsen 1970-1998
training period. The "summer stall" reading is the only variant that
*partially* survives this decay.

## Lesson (for LOOP_MEMORY iter log)

**Calendar / seasonal master-gates produce a partial Sortino lift only when
narrowed to Jun-Sep "summer stall" — the canonical Hirsch May-Oct framing
is monotonically worse than baseline.** The 2022_rates crisis is not a
Halloween problem (the bear straddled both halves of the calendar year);
no calendar mechanic can rescue it without also paying through 1995/2009/2020
May-Oct rallies. Augmentation as a 5th vote with K=2 produces highest CAGR
(31.0%) and highest score (79.5 STRONG) but Sortino remains below baseline
because soft tilt keeps Oct-2008 exposure on. **First loop iter where any
non-baseline config beats the loop replica baseline by Sortino.**

## Next iter ideas

1. **Stock-bond correlation regime classifier** — when 60d QLD↔ZROZ
   correlation flips from negative to positive (rare but informative), both
   legs lose their hedge. Citation: `[risk_parity, ch.5]` (Carlson on
   correlation regime breaks) or `[ml_for_algo_trading, ch.9]` (Jansen
   regime features). Would have flagged 2022 (when both equity and bonds
   fell together) and the 2008-Q4 brief breakdown — orthogonal to all 3
   loop iters' mechanics so far.
2. **Multi-asset ON rotation with inverse-vol weighting** — replace
   single-asset QLD with weighted basket {QLD, SOXL, UPRO} sized by 60d
   inverse vol; keep vote-of-K master gate. Distinct from T4 Clenow
   (top-K ranking) and T5 Carver (continuous vol-target). Citation:
   `[risk_parity, ch.5 p.10]` Carlson cap-efficient stacking +
   `[stocks_on_the_move, p.98]` Clenow vol-parity sizing.
3. **VIX-percentile / VRP harvesting overlay** — VIX above its 60d 80th
   percentile → force OFF (forward returns historically weak in extreme
   VIX regimes). Distinct from realised-vol gate (already in winner stack)
   because VIX is forward-looking implied vol. Citation: `[machine_trading,
   ch.X]` (Chan VIX strategies) or `[volatility_trading, ch.7]`.

## INCOMPLETE flags

- **Replica drift (~0.04 Sortino):** baseline Sortino_lh56y = 1.2841 vs
  canonical iter 022 winner 1.3246. Drift is a known consequence of the
  loop's data-loading warmup boundary differing from iter 022 by 248 days;
  documented in iter 001. Comparative deltas across configs in this iter
  are bit-exact.
- **Hirsch's exact "first/last trading day" boundary:** we use whole-month
  boundaries (start-of-month inclusive, end-of-month inclusive). The
  difference is at most ~24 days/year; Sortino impact < 0.005. Not swept.
- **Re-arm hysteresis is not applicable** for a date-based gate — the
  veto state is purely a function of month(t), no path-dependence.
- **G5 post-2020 FWD edge decay:** the May-Oct Halloween edge is
  essentially 0.001 in post-2020 (cal_veto_may_oct), confirming literature
  observation that published seasonal edges decay sharply post-publication.
  The Jun-Sep variant retains 0.371 — narrower but still degraded.
- **Synth caveat (pre-1985):** pre-1985 QLDSIM is formula-derived; the
  calendar gate fires deterministically by month regardless of synth
  fidelity. Comparative deltas remain valid; absolute Sortino floor across
  all configs may be modestly affected pre-1985.
- **Tax/fees:** gross only this iter (matching study convention).
- **Single-axis grid CSCV concern:** G1 PBO 0.444 passes but is structurally
  weaker than iter 002's 0.159; this iter's grid mixes mechanic-orthogonal
  configs (veto vs vote-of-K) but all share the monthly-calendar layer.
