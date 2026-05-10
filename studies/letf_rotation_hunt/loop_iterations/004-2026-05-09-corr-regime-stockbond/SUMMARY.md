# 004-2026-05-09-corr-regime-stockbond — SUMMARY

**Iter:** 004 / 50 (loop)
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Stock-bond correlation regime master-gate. When 60d/120d
rolling correlation between QLD daily returns and ZROZ daily returns
exceeds 0.00 / 0.20 / 0.30, redirect either the OFF leg or the entire
portfolio to CASHX, since the diversification hedge has structurally
broken (Qian RORO regime). Targets the 2022_rates loss directly via
cross-asset second-moment regime detection — orthogonal to iters 001
(yield-curve), 002 (vol-DD), 003 (calendar).
**Primary citation:** `[risk_parity, p.80-81, ch.4]` — Qian on RORO regime;
stocks/commodities reached corr 0.71 in 2009-2012 while USTs held -0.58
to -0.53 vs risky assets. Documents the mechanism by which stock-bond
correlation flips can eliminate diversification value.
**Secondary citations:** `[risk_parity, p.110, ch.5]` (Qian diversification
return collapse when ρ > 0); `[ml_for_algo_trading, ch.9]` (Jansen rolling
state features); `[advances_fin_ml, p.208-211]` (PBO via CSCV); `[advances_fin_ml,
p.222-223]` (DSR + cumulative n_trials); `[systematic_trading, p.180-190]`
(Carver carry/regime overlay shape).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_004
**n_configs:** 6
**cumulative_n_trials_global:** 444 → **450**

## TL;DR

- **Best by Sortino:** `..._corrgate_off_baseline` (winner replica). Sortino_lh56y
  **1.2841** (edge **−0.0405**). **No corr-gate variant beats baseline.**
- **Best corr-gate variant:** `..._corrgate_t030_60d_offleg_cashx`
  (strict threshold). Sortino_lh56y **1.2540**, edge **−0.0706**.
  -0.030 below baseline — corr-gate adds no Sortino value at any threshold.
- `beats_winner=false` for every config.
- KILL_LOOP #1, #2, #3, #5 all **NOT FIRED.** **KILL_LOOP #4 (over-suppression)
  FIRED for `..._master_cashx`** (lh_56y pct_above_bench 0.7039 << 0.85).
- **G1 PBO = 0.071 — best in the loop so far** (vs iter 001 0.575, iter 002
  0.159, iter 003 0.444). The orthogonal grid (threshold × window × scope)
  produces clean CSCV separation: corr-gate is a structurally distinct
  mechanic from prior iters, and the in-iter mechanic switch (offleg vs
  master) adds further dimensional diversity.
- **Crisis attribution unchanged: every config rescues 2008 only (1 of 4).**
  The corr-gate did NOT rescue 2022_rates. Why: the QLD↔ZROZ correlation
  flipped positive *after* the bear was already underway in 2022, and the
  offleg-only override cannot help when the strategy is in ON state during
  a falling market. Master_cashx does intervene during ON state but
  over-suppresses at all other times (lh_56y CAGR 17.3% vs 29.9% baseline).
- **The cross-asset second-moment regime is real but does not lift Sortino
  on this strategy.** Corrgate active% sweep (44.7% / 24.0% / 14.6%)
  shows the gate fires meaningfully often, but in a way that is *correlated
  with the trend signal already being OFF* — adding the override merely
  switches the OFF-leg vehicle (ZROZ → CASHX), giving up duration risk
  premium during normal defensive periods to gain a marginal benefit during
  rare RORO regimes. Net Sortino contribution: -0.03 to -0.11.
- **One structural positive:** `..._corrgate_t000_60d_offleg_cashx` reduces
  lh_56y MDD from -64.5% to -57.4% (cleanest MDD improvement of the loop)
  but at the cost of -0.063 Sortino. Useful for risk-budgeted overlays
  in future iters; not a stand-alone winner.

## Configs tested

| # | Name | Threshold | Window | Override scope |
|---|---|---:|---:|---|
| 1 | `qld_voteK2_..._corrgate_off_baseline` | — | — | baseline |
| 2 | `qld_voteK2_..._corrgate_t000_60d_offleg_cashx` | ρ > 0.00 | 60d | OFF leg → CASHX |
| 3 | `qld_voteK2_..._corrgate_t020_60d_offleg_cashx` | ρ > 0.20 | 60d | OFF leg → CASHX |
| 4 | `qld_voteK2_..._corrgate_t030_60d_offleg_cashx` | ρ > 0.30 | 60d | OFF leg → CASHX (stricter) |
| 5 | `qld_voteK2_..._corrgate_t020_120d_offleg_cashx` | ρ > 0.20 | 120d | OFF leg → CASHX (slower) |
| 6 | `qld_voteK2_..._corrgate_t020_60d_master_cashx` | ρ > 0.20 | 60d | entire portfolio → CASHX |

All share the trend ON signal `vote-of-2 of {SMA250, SMA100, vol_21d<40%,
AR(1)_30d>0}` on QLDSIM. ZROZSIM is the canonical OFF asset for non-overridden
periods. CASHX (FFR proxy) is the override target. Correlation computed at
close of t-1 with 1-day lag — same convention as winner.

## Results — gross metrics per dataset

### Sortino (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `..._off_baseline` | **1.2841** ← best | 1.2217 | 1.0911 | 1.2890 |
| `..._t000_60d_offleg_cashx` | 1.2211 | 1.1904 | 1.0740 | 1.3054 |
| `..._t020_60d_offleg_cashx` | 1.2133 | 1.1791 | 1.0713 | 1.2831 |
| `..._t030_60d_offleg_cashx` | 1.2540 | 1.1932 | 1.0911 | 1.2890 |
| `..._t020_120d_offleg_cashx` | 1.2184 | 1.1799 | 1.0947 | 1.2904 |
| `..._t020_60d_master_cashx` | 0.9252 | 0.9190 | 1.0159 | 1.1963 |

The strict t030 variant nearly recovers baseline Sortino in the post-2003
windows (spy_real 1.0911 = baseline; ndx_real 1.2890 = baseline) because the
gate fires only during the few unambiguous RORO crossings (14.6% of days),
but loses 0.03 Sortino in lh_56y because pre-2003 RORO crossings are more
frequent and not all are profitable to gate.

### Sharpe / CAGR / MDD / pct_above_bench (lh_56y)

| Config | Sharpe | CAGR | MDD | pct_above_bench |
|---|---:|---:|---:|---:|
| `..._off_baseline` | 0.8924 | 29.85% | -64.50% | 1.0000 |
| `..._t000_60d_offleg_cashx` | 0.8547 | 27.47% | **-57.40%** ← best MDD | 1.0000 |
| `..._t020_60d_offleg_cashx` | 0.8493 | 27.41% | -64.50% | 1.0000 |
| `..._t030_60d_offleg_cashx` | 0.8725 | 28.71% | -64.50% | 1.0000 |
| `..._t020_120d_offleg_cashx` | 0.8523 | 27.63% | -64.50% | 1.0000 |
| `..._t020_60d_master_cashx` | 0.6572 | 17.28% | -64.79% | **0.7039** ← KILL #4 |

**SPY anchor (lh_56y):** Sortino 0.958 / Sharpe 0.682 / MDD -55.1% (mandate
§2.2/§2.3 — MDD warning-only). Every offleg config dominates SPY's Sortino
with pct_time_above_benchmark = 1.000 in lh_56y. Master_cashx is the only
config that drops below SPY-Sortino in lh_56y.

The t000 (any-positive-corr-fires) variant gives the cleanest MDD reduction
of the loop (-7.1pp absolute, -11% relative), but its Sortino loss (-0.063)
indicates the trade is unfavourable on the deploy-relevant metric.

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G3 ≥5/8 | G4 OOS S | G5 FWD S | G6 99% low | G7 \|Δ\| pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| off_baseline | 0.071 ✓ | 9.7e-06 ✓ | 7/8 ✓ | 0.825 ✓ | 0.708 ✓ | 0.519 ✓ | 0.000 ✓ |
| t000_60d_offleg | 0.071 ✓ | 7.5e-05 ✓ | 7/8 ✓ | 0.751 ✓ | 0.727 ✓ | 0.448 ✓ | 0.000 ✓ |
| t020_60d_offleg | 0.071 ✓ | 7.7e-05 ✓ | 7/8 ✓ | 0.738 ✓ | 0.698 ✓ | 0.434 ✓ | 0.000 ✓ |
| t030_60d_offleg | 0.071 ✓ | 1.6e-05 ✓ | 7/8 ✓ | 0.785 ✓ | 0.708 ✓ | 0.482 ✓ | 0.000 ✓ |
| t020_120d_offleg | 0.071 ✓ | 7.4e-05 ✓ | 7/8 ✓ | 0.728 ✓ | 0.710 ✓ | 0.439 ✓ | 0.000 ✓ |
| **t020_60d_master** | 0.071 ✓ | 9.7e-04 ✓ | 5/8 ✓ | 0.516 ✓ | 0.504 ✓ | 0.183 ✓ | 0.000 ✓ |

Hard-gate thresholds: G1 PBO < 0.50, G2 < 0.05, G3 ≥ 5/8, G4/G5/G6 > 0,
G7 |Δ| ≤ 3pp.

**G1 PBO = 0.071 is the cleanest PBO of the loop**, beating iter 001 (0.575
single-axis fail), iter 002 (0.159), iter 003 (0.444). The orthogonal grid
design (threshold × window × scope) produces strong CSCV separation —
corr-gate is structurally distinct from baseline, AND the offleg-vs-master
mechanism switch differentiates internally. CSCV behaves correctly.

**G5 FWD post-2020 Sharpe** is informative: all offleg configs cluster
0.698-0.727 (essentially baseline 0.708), so post-2020 edge is preserved.
Master_cashx drops to 0.504 — confirming over-suppression in the
post-2020 sample where corr regimes were frequent.

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_dotcom | 2008_GFC | 2020_COVID | 2022_rates |
|---|:---:|:---:|:---:|:---:|
| off_baseline | ✗ | ✓ | ✗ | ✗ |
| t000_60d_offleg | ✗ | ✓ | ✗ | ✗ |
| t020_60d_offleg | ✗ | ✓ | ✗ | ✗ |
| t030_60d_offleg | ✗ | ✓ | ✗ | ✗ |
| t020_120d_offleg | ✗ | ✓ | ✗ | ✗ |
| t020_60d_master | ✗ | ✓ | ✗ | ✗ |

**Identical 1-of-4 across all 6 configs** — the corr-gate did NOT rescue
any additional crisis. Diagnosis:

- **2022_rates not rescued.** The QLD↔ZROZ 60d corr crossed +0.20 around
  Mar-2022, but by then NDX was already down ~13% from its Nov-2021 peak
  *while the trend signal was still ON*. Offleg override doesn't fire
  during ON state, so the early-2022 losses are not avoided. The override
  *does* fire later in 2022 (when trend flips OFF), but by then the
  rotation is into ZROZ which is also falling — and CASHX yielded ~1-2%
  in early/mid 2022 (FFR was still near zero), a negligible improvement.
- **2020_COVID not rescued.** The crash was mechanically too fast (peak Feb
  19 to trough Mar 23) for a 60d-window correlation to flip into RORO
  before the strategy already exited. Stocks and bonds *both* rallied in
  late Feb / early Mar 2020, then bonds rallied more — corr stayed
  negative through the worst of the crash.
- **2008_GFC rescued by underlying vote-of-K** (vol_21d<40% gate flipped
  OFF reliably in Sep-2008), independent of the corr-gate layer.
- **Master_cashx, despite being most aggressive, doesn't add crisis
  rescues** — confirming the issue is not "we don't act fast enough"
  but "the corr-regime signal is mostly redundant with the trend signal
  in crisis windows."

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
|---|---:|---:|:---:|---:|:---:|
| `..._off_baseline` (best) | **1.2841** | -0.0405 | T | 1.0000 | False |
| `..._t000_60d_offleg_cashx` | 1.2211 | -0.1035 | T | 1.0000 | False |
| `..._t020_60d_offleg_cashx` | 1.2133 | -0.1113 | T | 1.0000 | False |
| `..._t030_60d_offleg_cashx` | 1.2540 | -0.0706 | T | 1.0000 | False |
| `..._t020_120d_offleg_cashx` | 1.2184 | -0.1062 | T | 1.0000 | False |
| `..._t020_60d_master_cashx` | 0.9252 | -0.3994 | F | 0.7039 | False |

**No config qualifies as `beats_winner=true`.** Among corr-gate variants,
the strict t030 threshold has the smallest Sortino loss (-0.0301 vs
baseline; -0.0706 vs winner), but no variant adds Sortino. Iter 003's
Jun-Sep calendar veto (-0.0185) remains the loop's closest approach to
the winner.

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns, lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % of time in equity (post-corrgate)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags +
  corrgate_active_pct + turnover_per_year per config

## KILL_LOOP results (pre-registered in hypothesis.md)

- **KILL_LOOP #1 (success-tag):** **NOT FIRED.** Best Sortino_lh56y = 1.2841
  (baseline) < threshold 1.3746. No corr-gate variant produces an above-baseline
  Sortino, so no config can register `beats_winner=true`.
- **KILL_LOOP #2 (decisive-fail):** **NOT FIRED.** Of the 5 corr-gate configs,
  only 1 (master_cashx) is below 1.10 (Sortino 0.9252). Offleg variants
  cluster 1.21-1.25 — family is *underwhelming* but not dead.
- **KILL_LOOP #3 (replica-sanity):** **NOT FIRED.** Baseline replica
  Sortino_lh56y = 1.2841, **bit-exact** match to iters 001/002/003 baselines.
  Comparative deltas across configs are valid.
- **KILL_LOOP #4 (over-suppression):** **FIRED for `..._master_cashx`.**
  lh_56y pct_time_above_benchmark = 0.7039 << 0.85 threshold; modern_1990
  pct_above_bench = 0.7272 also below. The whole-portfolio override forces
  CASHX during many ON-state periods (corrgate fires 24% of days), giving
  up substantial compounding for marginal RORO protection. Configuration
  tagged "OVER_SUPPRESS" — informational only per hypothesis.md.
- **KILL_LOOP #5 (corr-regime-non-event):** **NOT FIRED.** Corrgate fires
  14.6%-44.7% of days across the 5 corr-gate variants — well above the 5%
  underpowered threshold. The hypothesis is testable; it just doesn't lift
  Sortino on this strategy.

## Verdict

- **Best config (overall):** `..._corrgate_off_baseline` — STRONG, score
  76.5, Sortino_lh56y 1.2841, edge -0.0405. Replica drift only.
- **Best corr-gate variant:** `..._corrgate_t030_60d_offleg_cashx` —
  STRONG, score 76.5, Sortino_lh56y 1.2540, edge -0.0706. Strict
  threshold + offleg-only fires sparingly (14.6% of days), reduces lh_56y
  Sortino by 0.030 vs baseline but recovers exactly to baseline in
  post-2003 windows (spy_real 1.0911 = baseline; ndx_real 1.2890 = baseline).
- **kill_rule_status:** N/A (loop iter; closed-study T<N>→T<N+1> KILLs
  don't apply)
- **beats_winner:** false (no config exceeds threshold)
- **cumulative_n_trials_global:** 450

## Conclusion

The stock-bond correlation regime hypothesis is **well-grounded in theory**
(`risk_parity, ch.4`) and **mechanically novel within the loop** (cross-asset
second moment, distinct from yield-curve / vol-DD / calendar mechanics of
prior iters), but **does not lift Sortino** on the winner's strategy:

1. **The signal is most active when the trend signal is already OFF.**
   Stock-bond correlation flips positive primarily during stress regimes
   when the vote-of-K already detects equity weakness via vol_21d / SMA250.
   The corr-gate's marginal information content is therefore *the choice
   of OFF vehicle* (ZROZ vs CASHX) during defensive periods — not whether
   to be defensive at all.

2. **ZROZ → CASHX swap loses duration risk premium without compensating
   gains.** Across 56 years, the OFF leg in ZROZ accumulates substantial
   bond-bull-market gains (1981-2020 long-rate decline). CASHX yields the
   short rate — meaningfully positive in 1979-1982 / 2007 / 2024 but
   modest in 2009-2015 / 2020-2022. The expected value of the swap is
   negative because the gate fires *more often* during periods when ZROZ
   is rallying defensively (early-2008, 2020-Q1, 2023-Q1) than during the
   rare 2022-style dual-falls.

3. **Master_cashx demonstrates over-suppression cost.** Forcing the entire
   portfolio to CASHX during 24% of trading days (corrgate firing rate at
   threshold 0.20 / 60d) gives up too much compounding for too little
   protection. Lh_56y Sortino collapses from 1.2841 to 0.9252 (-28%) and
   pct_time_above_benchmark drops to 0.7039 (vs 1.0000 baseline) —
   structurally below SPY for ~30% of trading days, breaking WC.

4. **G1 PBO 0.071 is the cleanest of the loop.** Even though no config
   wins on Sortino, the iter is methodologically informative: the
   orthogonal grid design (threshold × window × scope) produces clean
   CSCV behaviour. This makes the negative result strong — the corr-gate
   is *not* helping, full stop, with no curve-fit ambiguity.

5. **The 2022_rates rescue thesis fails for a specific reason.** The
   QLD↔ZROZ correlation flipped positive *after* the bear was already
   underway, AND the offleg-only override doesn't fire during ON state
   (when the early-2022 NDX losses accumulated). A configuration that
   *both* keeps trend signal *and* uses corr to flip ON→cash earlier
   would require knowing the price drop was correlation-driven (it
   wasn't fully — Q1-2022 was rate-driven primarily, with stocks falling
   first and bonds joining later).

**Hypothesis dead** for this strategy structure. The cross-asset
second-moment regime is real (and corrgate fires meaningfully often)
but its information is largely redundant with the trend signal already
in the winner's stack.

## Lesson (for LOOP_MEMORY iter log)

**Stock-bond correlation regime gating produces no Sortino lift on the
winner's two-leg structure** — the corr-flip is most active when the
trend signal is already defensive, so the gate's marginal contribution
is just OFF-leg vehicle choice (ZROZ vs CASHX). Across 56 years, ZROZ's
duration risk premium > CASHX's short-rate yield in expectation, so the
swap loses Sortino. **Master-cashx variant is the loop's first FIRED
KILL_LOOP** (#4 over-suppression: lh_56y pct_above_bench 0.7039 < 0.85)
— forcing whole-portfolio cash during 24% of days collapses Sortino by
28%. **G1 PBO=0.071 is the cleanest PBO of the loop** (vs 003's 0.444,
002's 0.159, 001's 0.575): orthogonal grid design pays off
methodologically even when the strategy hypothesis fails. Best variant
`..._corrgate_t030_60d_offleg_cashx` recovers to baseline in post-2003
windows but not in lh_56y; useful diagnostic for future iters.

## Next iter ideas

1. **Multi-asset ON rotation with inverse-vol weighting** — replace
   single-asset QLD with a weighted basket {QLD, SOXL, UPRO} sized by 60d
   inverse vol; keep vote-of-K master gate. Distinct from T4 Clenow
   (top-K ranking), T5 Carver (continuous vol-target), and the iter 023
   multi-asset grid (which used K=2 fixed × 4 OFF assets but *one* ON asset
   per config). This iter's negative result on cross-asset second moment
   suggests the more promising direction is *cross-asset first moment*
   diversification on the ON leg. Citation: `[risk_parity, p.10, ch.1]`
   Carlson cap-efficient stacking (in spec quotation) +
   `[stocks_on_the_move, p.98]` Clenow vol-parity sizing. **Highest
   expected value of remaining shortlist.**

2. **VIX-percentile / Variance-Risk-Premium overlay** — VIX above its 60d
   80th percentile → force OFF (extreme implied vol historically
   anti-correlates with forward returns). Distinct from realised-vol
   gate (already in winner stack) because VIX is forward-looking implied
   vol. Citation: `[volatility_trading, ch.7]` (Sinclair on variance risk
   premium) or `[machine_trading]` (Chan VIX strategies). VIX history only
   from 1990, so lh_56y has 35 years of warm-up before signal becomes
   active — partial-period analysis.

3. **Bond duration timing** — when curve-stress regimes hit (10y vol > 60d
   80th percentile), reduce ZROZ exposure or switch to IEF. Targets the
   2022 problem differently from this iter: sidestep the *bond risk*
   directly rather than the cross-asset correlation. Citation: Ilmanen
   2003 / 2011 (not in books/) — would need to find proxy citation in
   `systematic_trading` ch.9 (Carver carry).

4. **Equity factor tilts** — overlay quality / low-beta filter on top of
   QLD via SQQQ ratios or sector spreads. Most distant from current iter
   but lowest priority because LETF universe is narrow.

## INCOMPLETE flags

- **Replica drift (~0.04 Sortino):** baseline Sortino_lh56y = 1.2841 vs
  canonical iter 022 winner 1.3246. Drift is a known consequence of the
  loop's data-loading warmup boundary differing from iter 022 by 248 days;
  documented in iter 001. Comparative deltas across configs in this iter
  are bit-exact valid.
- **60d window choice not swept beyond {60, 120}d.** A more comprehensive
  window grid (30 / 60 / 90 / 120 / 252 d) would inflate trial count and
  G1 PBO. The two-window comparison (60d vs 120d at fixed threshold 0.20)
  is sufficient to test "faster vs slower regime detection" without
  curve-fit risk; result shows window matters less than threshold.
- **Threshold values are interpretable, not arbitrary:** 0.00 = sign flip,
  0.20 ≈ Qian's "meaningful positive" benchmark, 0.30 ≈ classical RORO
  threshold. Sweep covers the interpretable range.
- **ZROZ → CASHX swap implicitly trades duration premium for short-rate
  yield.** A future iter could test the inverse: route to TIP (real
  yield) or IEF (intermediate duration) instead of CASHX, preserving
  some duration exposure during corr-flips. Out of scope this iter.
- **Synth caveat (pre-1985):** ZROZSIM is a duration-aware long-treasury
  proxy; QLDSIM is formula-derived NDX 2x. Pre-1985 correlations are
  mechanically tied to synth assumptions, but corrgate fires deterministically
  on the synth correlation series — comparative deltas across configs in
  the lh_56y window remain valid.
- **Tax/fees:** gross only this iter (matching closed-study convention).
  CASHX returns are FFR-tracked.
- **Master_cashx WC failure** is by design (forced whole-portfolio cash
  exposure 24% of days). Tag "OVER_SUPPRESS" — not a curve-fit failure.
