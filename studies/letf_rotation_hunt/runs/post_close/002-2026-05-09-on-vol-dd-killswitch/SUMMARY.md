# 002-2026-05-09-on-vol-dd-killswitch — SUMMARY

**Iter:** 002 / 50 (loop)
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Vol-adjusted drawdown master-gate (Carver-style kill switch)
overlaid on top of the winner's vote-of-K trend signal. Force OFF when QLD's
drawdown from rolling 252d peak exceeds X × σ_price_21d, with half-threshold
re-arm hysteresis. Target: rescue 2022_rates loss without sacrificing
2008/2020 alpha. ON-leg intervention only; OFF leg fixed to ZROZ.
**Primary citation:** `[systematic_trading, p.212 ch.13]` — Carver
semi-automatic stop loss using `X × sigma_price_points` from tracking extreme.
**Secondary citations:** `[trading_systems_methods, p.352-353]` (Kaufman
trailing-stop family), `[advances_fin_ml, p.208-211]` (PBO),
`[advances_fin_ml, p.222-223]` (DSR cumulative),
`[volatility_trading, p.39]` (vol mean-reversion → 21d window choice).
**Datetime UTC:** 2026-05-09T20:47:54+00:00
**Engine version:** loop_iter_002
**n_configs:** 6
**cumulative_n_trials_global:** 432 → **438**

## TL;DR

- Best config (by Sortino): **`qld_voteK2_..._dd_off`** (no kill switch, winner
  replica). Score 76.5 / 100 STRONG, WC=Y.
- Sortino_lh56y: **1.2841** (edge **-0.0405** vs winner 1.3246 — same as iter
  001's baseline replica drift; KILL_LOOP #3 NOT FIRED).
- `beats_winner=false` (no kill-switch variant lifts Sortino above baseline
  let alone above 1.3746 threshold).
- Kill-switch family is **monotonically harmful** to Sortino on lh_56y:
  Sortino rises monotonically with X (2 → 5), approaching but never matching
  the no-gate baseline.
- KILL_LOOP #1, #2, #3, #4 all **NOT FIRED.**
- **G1 PBO=0.159 passes universally** (first iter in the loop where G1 is
  clean) — the kill-switch dimension is genuinely orthogonal to the trend
  signal, giving CSCV more hypothesis-space variation than iter 001's tight
  OFF-leg sweep.
- Honest read: vol-adjusted DD as a regime gate fires too often even at
  Carver's recommended X=4 (21.7% of days), eating into LETF's compounding.
  At every threshold, the gate exits AFTER the worst of a drawdown is
  already realised, then re-arms during recovery — net cost to compounding
  exceeds rare crisis-rescue benefit.

## Configs tested

| # | Name | Kind | Param | Killswitch active% | Turnover/y |
|---|---|---|--:|--:|--:|
| 1 | `qld_voteK2_..._dd_off` | no killswitch (winner replica) | — | 0.0% | 9.29 |
| 2 | `qld_voteK2_..._dd_x2_252_vol21` | vol-adjusted | X=2 | 38.1% | 4.91 |
| 3 | `qld_voteK2_..._dd_x3_252_vol21` | vol-adjusted | X=3 | 27.7% | 5.78 |
| 4 | `qld_voteK2_..._dd_x4_252_vol21` (Carver) | vol-adjusted | X=4 | 21.7% | 7.10 |
| 5 | `qld_voteK2_..._dd_x5_252_vol21` | vol-adjusted | X=5 | 17.5% | 7.51 |
| 6 | `qld_voteK2_..._dd_pct25_252` | absolute % | 25% | 31.2% | 5.01 |

All share the trend ON signal `vote-of-2 of {SMA250, SMA100, vol_21d<40%,
AR(1)_30d>0}` on QLD and OFF asset ZROZ. Re-arm hysteresis: 0.5 × threshold
(half-recovery rule). Signal lag 1 day.

## Results — gross metrics per dataset

### Sortino (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| **`..._dd_off` (baseline)** | **1.2841** ← best | 1.2217 | 1.0911 | 1.2890 |
| `..._dd_x2_252_vol21` | 1.0824 | 1.0512 | 0.9486 | 1.1729 |
| `..._dd_x3_252_vol21` | 1.1526 | 1.1170 | 1.0671 | 1.2210 |
| `..._dd_x4_252_vol21` | 1.1779 | 1.1456 | 1.0833 | 1.2581 |
| `..._dd_x5_252_vol21` | 1.2240 | 1.1818 | 1.1147 | 1.2879 |
| `..._dd_pct25_252` | 1.1365 | 1.0934 | 1.0327 | 1.2741 |

Monotonic in X (loosen kill switch → Sortino rises). The asymptotic limit
X=∞ is the no-gate baseline.

### Sharpe / CAGR / MDD (lh_56y)

| Config | Sharpe | CAGR | MDD | pct_time_above_bench |
|---|---:|---:|---:|---:|
| `..._dd_off` | 0.892 | 29.85% | -64.5% | 1.0000 |
| `..._dd_x2_252_vol21` | 0.754 | 22.25% | -54.0% | 0.9855 |
| `..._dd_x3_252_vol21` | 0.801 | 24.85% | -59.7% | 0.9931 |
| `..._dd_x4_252_vol21` | 0.819 | 25.80% | -59.7% | 0.9943 |
| `..._dd_x5_252_vol21` | 0.850 | 27.35% | -59.7% | 1.0000 |
| `..._dd_pct25_252` | 0.792 | 24.03% | -54.5% | 0.9962 |

**SPY anchor (lh_56y):** Sortino 0.958 / Sharpe 0.682 / MDD -55.1% (mandate
§2.2/§2.3 — MDD warning-only).

The kill switch reduces MDD modestly (e.g. -64.5% → -53.5% for X=2) but at a
larger Sortino cost — the LETF's recovery rallies happen precisely while the
kill switch is still suppressing equity exposure, so the strategy holds
duration (ZROZ) through what would have been the highest-momentum re-entry
days.

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G3 (≥5/8 windows) | G4 OOS S | G5 FWD S | G6 99% low | G7 |Δ pp| |
|---|---:|---:|---:|---:|---:|---:|---:|
| dd_off | 0.159 ✓ | 9.7e-06 ✓ | 7/8 ✓ | 0.825 ✓ | 0.708 ✓ | 0.519 ✓ | 0.000 ✓ |
| dd_x2 | 0.159 ✓ | 3.2e-04 ✓ | 5/8 ✓ | 0.723 ✓ | 0.544 ✓ | 0.428 ✓ | 0.000 ✓ |
| dd_x3 | 0.159 ✓ | 1.0e-04 ✓ | 7/8 ✓ | 0.778 ✓ | 0.657 ✓ | 0.457 ✓ | 0.000 ✓ |
| dd_x4 | 0.159 ✓ | 6.7e-05 ✓ | 7/8 ✓ | 0.793 ✓ | 0.697 ✓ | 0.475 ✓ | 0.000 ✓ |
| dd_x5 | 0.159 ✓ | 3.0e-05 ✓ | 7/8 ✓ | 0.821 ✓ | 0.697 ✓ | 0.496 ✓ | 0.000 ✓ |
| dd_pct25 | 0.159 ✓ | 1.3e-04 ✓ | 6/8 ✓ | 0.788 ✓ | 0.672 ✓ | 0.465 ✓ | 0.000 ✓ |

Hard-gate thresholds: G1 PBO < 0.50, G2 < 0.05, G3 ≥ 5/8, G4/G5/G6 > 0,
G7 |Δ| ≤ 3pp.

**G1 PBO=0.159 is a clean pass for ALL configs** — first time in the loop
that G1 is genuinely orthogonal. Adding the kill-switch dimension creates
real hypothesis-space variation (CSCV picks up that the IS top half of
{X=2,3,4,5,pct25} reorders meaningfully across OOS folds), unlike iter 001's
tight one-axis OFF-leg sweep where rank-correlation IS↔OOS was high enough
to flag PBO=0.575.

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_dotcom | 2008_GFC | 2020_COVID | 2022_rates |
|---|:---:|:---:|:---:|:---:|
| dd_off | ✗ | ✓ | ✗ | ✗ |
| dd_x2 | ✓ | ✓ | ✗ | ✗ |
| dd_x3 | ✗ | ✓ | ✗ | ✗ |
| dd_x4 | ✗ | ✓ | ✗ | ✗ |
| dd_x5 | ✗ | ✓ | ✗ | ✗ |
| dd_pct25 | ✓ | ✓ | ✗ | ✗ |

The kill switch **does** rescue 2000_dotcom for the most aggressive variants
(dd_x2 and dd_pct25) — exactly where the slow vote-of-K signal had let QLD
bleed for 30+ months. But it **does not** rescue 2022_rates, the originally
targeted crisis, because the 2022 NDX bear was a slow grinding decline that
respected vol-adjusted thresholds (each daily down move was within
1-2σ band; only cumulative DD crossed 4-5σ, by which time the equity damage
was already realised).

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
|---|---:|---:|:---:|---:|:---:|
| **`..._dd_off` (best)** | **1.2841** | **-0.0405** | T | 1.0000 | False |
| `..._dd_x2_252_vol21` | 1.0824 | -0.2422 | F | 0.9855 | False |
| `..._dd_x3_252_vol21` | 1.1526 | -0.1720 | T | 0.9931 | False |
| `..._dd_x4_252_vol21` | 1.1779 | -0.1467 | T | 0.9943 | False |
| `..._dd_x5_252_vol21` | 1.2240 | -0.1006 | T | 1.0000 | False |
| `..._dd_pct25_252` | 1.1365 | -0.1881 | F | 0.9962 | False |

The lh_56y `pct_time_above_benchmark` ≥ 0.95 for every config. WC=False
for dd_x2 and dd_pct25 stems from the *mean across all 4 datasets* dipping
below 0.95 (spy_real and ndx_real are weaker than lh_56y because the kill
switch fires more often during 2003-2026 than during the synth-flat
1970-1985 portion). WC scoring uses the mean, not the lh_56y value.

Replica baseline drift (-0.0405) matches iter 001 exactly (same data
loading path; warmup boundary differs by 248 days from canonical iter 022 —
documented in iter 001 SUMMARY). KILL_LOOP #3 NOT FIRED (0.0 absolute drift
vs iter 001 baseline 1.2841).

**No config qualifies as `beats_winner=true`.** The best edge is the baseline
(no kill switch) at -0.0405. The kill-switch family adds nothing to Sortino;
it trades a small MDD reduction for a larger CAGR reduction.

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns, lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % of time exposed to equity
  (post-killswitch combined exposure)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags +
  killswitch_active_pct + turnover_per_year per config

## KILL_LOOP results (pre-registered in hypothesis.md)

- **KILL_LOOP #1 (success-tag):** **NOT FIRED.** Best Sortino_lh56y = 1.2841
  (baseline) < threshold 1.3746. No config can register `beats_winner=true`
  regardless of WC, since Sortino is sub-threshold across the board.
- **KILL_LOOP #2 (decisive-fail):** **NOT FIRED.** Of the 5 kill-switch
  configs, 4 have Sortino_lh56y > 1.10 (1.153, 1.178, 1.224, 1.137); only
  dd_x2 dips to 1.08. The "all 5 < 1.10" condition is not met → family is
  *not* dead, just dominated by the no-gate baseline.
- **KILL_LOOP #3 (replica-sanity):** **NOT FIRED.** Baseline replica
  Sortino_lh56y = 1.2841, identical to iter 001's baseline (same warmup
  boundary). Drift vs canonical iter 022 (1.3246) is -0.0405 absolute,
  unchanged from iter 001 — a property of the shared loop loader path, not a
  new artifact.
- **KILL_LOOP #4 (whipsaw-detector):** **NOT FIRED.** Baseline turnover
  = 9.29 state changes/y; kill-switch configs are LOWER (4.9-7.5/y) because
  forcing OFF for sustained periods reduces switching frequency overall.
  No config crosses the 3× baseline threshold.

## Verdict

- **Best config:** `qld_voteK2_sma250_100_vol21_40_ar30_dd_off` (no kill
  switch, winner replica) — STRONG, score 76.5
- **kill_rule_status:** N/A (loop iter; closed-study T<N>→T<N+1> KILLs
  don't apply here)
- **beats_winner:** false (best Sortino edge -0.0405 — same as iter 001's
  replica drift; no kill-switch variant adds Sortino)
- **cumulative_n_trials_global:** 438

## Conclusion

The vol-adjusted drawdown master-gate (Carver semi-automatic stop) **does not**
improve Sortino as a regime overlay on top of the winner's vote-of-K trend
signal. Across the entire X sweep (2,3,4,5) plus the absolute-percent
sanity check (25%), Sortino_lh56y is monotonically below the no-gate baseline
(1.0824 → 1.2240 vs 1.2841). Even at Carver's recommended X=4, the kill
switch is active 21.7% of trading days — too often for an LETF where high
vol means routine pullbacks regularly cross 4σ thresholds. By the time the
gate fires, the worst of the drawdown is realised, and the gate stays OFF
through recovery rallies, costing more in compounding than it saves in
crisis avoidance.

The crisis-attribution table reveals one nuanced positive: the most
aggressive variants (dd_x2 and dd_pct25) **do** rescue 2000_dotcom by
forcing OFF during the multi-year tech bear that the slow vote-of-K signal
mishandled. But this comes paired with a -0.18 to -0.24 Sortino cost from
1980s-2010s false positives, so it doesn't earn its keep.

The originally-targeted crisis (2022_rates) is **not** rescued by any
variant. The 2022 bear was *too gradual* for vol-adjusted DD: each daily
down move stayed within 1-2σ, and the gate's response is by construction
proportional to vol-normalised loss size. A different mechanic is needed
for slow-grinding bears — perhaps a regime classifier that reads
correlation/breadth shifts rather than price drawdown magnitude alone.

**Hypothesis dead for vol-adjusted DD as an ON-leg overlay.** Carver's
sigma-price stop is well-suited to single-trade single-asset position
management (which is its actual use in `systematic_trading`), but does not
generalise to a regime gate on a leveraged trend-following composite.

A small structural positive for the loop framework: G1 PBO=0.159 passes
cleanly for the first time in any loop iter, because the kill-switch
dimension introduces real hypothesis-space variation. Future iters that
include genuinely orthogonal mechanics (regime classifier, multi-asset
rotation, calendar gates) should also see clean G1 — iter 001's universal
G1=0.575 fail was a tight-sweep artifact, not a structural problem.

## Lesson (for LOOP_MEMORY iter log)

**Carver semi-automatic stops do not generalise to regime overlays on
leveraged trend systems.** LETF natural vol means even normal pullbacks
cross 3-4σ DD thresholds; the kill switch fires too frequently and locks
out compounding rallies. The 2022_rates crisis was not a magnitude problem
but a duration problem (slow grinding bear), so a magnitude-triggered gate
cannot rescue it. **G1 PBO clean (0.159) confirms loop framework works
when configs vary in genuinely distinct mechanics.**

## Next iter ideas

1. **Regime classifier on equity-bond correlation** — when 60d
   QLD-vs-ZROZ correlation flips from negative to positive, equity selling
   no longer hedges via duration → derisk. Citation: `[regime_change, ch.X]`
   (Chen/Tsang regime detection) or `[ml_for_algo_trading, ch.X]` (Jansen
   correlation features). Would have flagged 2022 (when both equity and
   bonds fell together) early.
2. **Multi-asset ON rotation with inverse-vol weighting** — replace
   single-asset QLD with a weighted basket {QLD, SOXL, UPRO} sized by 60d
   inverse vol; keep vote-of-K master gate. Distinct from T4 Clenow
   (top-K hard ranking) and T5 Carver (continuous vol-target). Citation:
   `[risk_parity, ch.5 p.10]` Carlson cap-efficient stacking +
   `[stocks_on_the_move, p.98]` Clenow vol-parity sizing.
3. **Calendar/seasonal master-gate** as a 5th vote member — month-of-year
   filter (Sell-in-May "May-Oct = OFF unless trend confirmed by all 4 other
   votes"). Citation: `[trading_systems_methods, p.388 ch.27]` (Kaufman
   seasonality) or `[evidence_based_ta, ch.7]` (Aronson seasonality tests).

## INCOMPLETE flags

- **Replica drift (~0.04 Sortino):** baseline Sortino_lh56y = 1.2841 vs
  canonical winner 1.3246. Drift is a known consequence of the loop's data
  loading warmup boundary differing from iter 022 by 248 days; documented
  in iter 001. Comparative deltas across configs in this iter are bit-exact.
- **Hysteresis re-arm fraction (0.5) is not swept** — fixed to avoid
  introducing a second sweep dimension. A future iter could sweep
  {0.25, 0.5, 0.75, 1.0}.
- **Vol window 21d is fixed** — matches winner's vol_21d gate. Sweeping
  vol window (10d, 21d, 60d) would test whether the gate response is
  vol-window-sensitive, but that's a 4× config grid — exceeds protocol cap.
- **Tax/fees:** gross only (matches study convention; net layer is
  monotonic shift downstream).
- **Pre-1985 LETF synth caveat:** kill switch is essentially inactive
  pre-1985 (constant-price QLDSIM era → rolling peak ≈ price → DD ≈ 0).
  This pulls the 56y Sortino baseline down for all configs equally;
  comparative deltas remain valid.
