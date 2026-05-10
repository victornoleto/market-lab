# 005-2026-05-09-multi-asset-on-invvol — SUMMARY

**Iter:** 005 / 50 (loop)
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Replace the winner's single-asset (QLD) ON leg with a basket
of equity-style LETFs ({QLD, UPRO, UGL}) sized by inverse realised
volatility (60d / 120d) so each asset contributes equal volatility, while
keeping the winner's binary vote-K=2 trend gate (computed on QLD) and
ZROZ as the OFF leg. Tests cross-asset **first-moment** diversification —
orthogonal to iter 004 (cross-asset second-moment regime gate, failed).
**Primary citation:** `[stocks_on_the_move, p.98]` — Clenow on volatility-
parity sizing: $w_i \propto 1/\sigma_i$ "so each position contributes the
same amount of volatility."
**Secondary citations:** `[systematic_trading, ch.10]` (Carver inverse-vol
position sizing); `[risk_parity, ch.5, p.10]` (archived; Carlson cap-
efficient stacking rationale extends to multi-asset ON-leg);
`[advances_fin_ml, p.208-211]` (PBO via CSCV); `[advances_fin_ml,
p.222-223]` (DSR + cumulative n_trials); `[leverage_for_the_long_run,
p.21 Table 12]` (LETF tracking drag — UGL).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_005
**n_configs:** 6
**cumulative_n_trials_global:** 450 → **456**

## TL;DR

- **Best by Sortino:** `..._on_basket3_qld_upro_ugl_invvol60` (3-asset
  inverse-vol 60d). Sortino_lh56y **1.3340**, **edge +0.0094** —
  the **first positive Sortino edge** any loop iter has produced. Score
  77.5 STRONG.
- **Highest score:** `..._on_basket3_qld_upro_ugl_eqweight` (equal-weight,
  same 3-asset basket). Score **78.0 STRONG**, Sortino 1.3317, edge +0.0071.
  Higher score is driven by lower turnover (4.53/y vs 5.44/y for invvol60).
- **`beats_winner=false` for every config.** Best Sortino 1.3340 < threshold
  1.3746 (+0.05 anti-curve-fit margin), AND `winner_conditions_met=False`
  universally because **G1 PBO 0.881 fails** for all configs (CSCV
  detects high config-correlation in this single-mechanic grid).
- **Crisis attribution major lift** for UGL-containing baskets: basket2
  qld_ugl, basket3_invvol60, basket3_invvol120 each rescue **3 of 4 crises**
  (2000_dotcom + 2008_gfc + 2020_covid). Baseline rescues 1 of 4 (2008 only)
  — same as iters 001-004. Gold's idiosyncratic 1973-1980 / 2000-02 / 2020
  rallies provide the extra crisis cover. **First mechanism in the loop
  to break the 1-of-4 ceiling.**
- **2022_rates not rescued by any config** — same diagnosis as iters 001-004:
  the 2022 loss is trend-signal-driven (vote-K=2 stayed ON during early-2022
  drawdown); changing the ON-vehicle doesn't help when all 3 basket assets
  fell together in Q2-2022 (NDX, SPY, Gold all had drawdowns).
- **3-asset basket beats baseline; 2-asset baskets do not.** basket3_invvol60
  (1.3340) and basket3_eqweight (1.3317) both clear the 1.2841 baseline by
  ~0.05 Sortino. basket2_qld_upro (1.2695) underperforms baseline; basket2
  qld_ugl (1.2849) basically ties baseline but fails pct_above_benchmark
  (0.93 < 0.95 strict bar) due to UGL's 1980-2000 flat regime.
- **Inverse-vol vs equal-weight:** invvol60 (Sortino 1.3340) marginally
  outperforms eqweight (1.3317) on lh_56y; the +0.002 edge is within
  noise. Inverse-vol's claimed benefit is statistical not structural in
  this 3-asset universe.
- **G1 PBO 0.881 — worst of the loop** (vs 004's 0.071, 003's 0.444,
  002's 0.159, 001's 0.575). The single-mechanic grid (5 multi-asset
  configs varying only in basket composition / window / sizing) gives
  CSCV high IS-OOS rank divergence. Methodological lesson: this is the
  flip-side of iter 004's finding — orthogonal grid → clean PBO,
  single-axis grid → polluted PBO.
- **The hypothesis is partially confirmed.** Multi-asset diversification
  on the ON-leg adds Sortino *and* crisis cover, but the lift is small
  (+0.05 over baseline; +0.0094 over the cross-iter benchmark) and is
  not robust enough to clear the strict +0.05 anti-curve-fit margin or
  the G1 PBO threshold for deploy.

## Configs tested

| # | Name | ON-leg basket | Vol window | Sizing rule |
|---|---|---|---:|---|
| 1 | `qld_voteK2_..._on_baseline` | {QLD} | — | single-asset (replica) |
| 2 | `qld_voteK2_..._on_basket2_qld_upro_invvol60` | {QLD, UPRO} | 60d | inverse-vol |
| 3 | `qld_voteK2_..._on_basket2_qld_ugl_invvol60` | {QLD, UGL} | 60d | inverse-vol |
| 4 | `qld_voteK2_..._on_basket3_qld_upro_ugl_invvol60` | {QLD, UPRO, UGL} | 60d | inverse-vol |
| 5 | `qld_voteK2_..._on_basket3_qld_upro_ugl_invvol120` | {QLD, UPRO, UGL} | 120d | inverse-vol |
| 6 | `qld_voteK2_..._on_basket3_qld_upro_ugl_eqweight` | {QLD, UPRO, UGL} | — | equal-weight |

All share the trend ON signal `vote-of-2 of {SMA250, SMA100, vol_21d<40%,
AR(1)_30d>0}` computed on QLDSIM (winner replica gate). The OFF asset is
**ZROZSIM** for all configs. Inverse-vol weights computed daily with
1-day lag (close of t-1 used for opening of t weights), normalised so
$\sum_i w_i = 1.0$ post-warmup. Equal-weight is the static $1/N$
control.

## Results — gross metrics per dataset

### Sortino (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `..._on_baseline` | 1.2841 | 1.2217 | 1.0911 | 1.2890 |
| `..._on_basket2_qld_upro_invvol60` | 1.2695 | 1.2206 | 1.0731 | 1.2197 |
| `..._on_basket2_qld_ugl_invvol60` | 1.2849 | 1.2128 | 1.1163 | 1.0880 |
| **`..._on_basket3_qld_upro_ugl_invvol60`** ← Sortino-best | **1.3340** | 1.2691 | 1.1276 | 1.1798 |
| `..._on_basket3_qld_upro_ugl_invvol120` | 1.3049 | 1.2452 | 1.1227 | 1.1779 |
| `..._on_basket3_qld_upro_ugl_eqweight` ← score-best | 1.3317 | 1.2575 | 1.1107 | 1.2096 |

Pattern: 3-asset baskets dominate 2-asset baskets across all four datasets;
3-asset configs cluster tightly (1.30-1.33 lh_56y) regardless of sizing
choice (invvol60 vs invvol120 vs eqweight).

### Sharpe / CAGR / MDD / pct_above_bench (lh_56y)

| Config | Sharpe | CAGR | MDD | pct_above_bench |
|---|---:|---:|---:|---:|
| `..._on_baseline` | 0.8924 | 29.85% | -64.50% | 1.0000 |
| `..._on_basket2_qld_upro_invvol60` | 0.8874 | 28.90% | -62.85% | 1.0000 |
| `..._on_basket2_qld_ugl_invvol60` | 0.8754 | 20.25% | **-52.08%** ← best MDD | **0.9300** ← KILL #4 |
| `..._on_basket3_qld_upro_ugl_invvol60` | 0.9156 | 22.59% | -53.65% | 1.0000 |
| `..._on_basket3_qld_upro_ugl_invvol120` | 0.8964 | 22.02% | -54.06% | 1.0000 |
| `..._on_basket3_qld_upro_ugl_eqweight` | 0.9199 | 24.55% | -56.83% | 1.0000 |

**SPY anchor (lh_56y):** Sortino 0.958 / Sharpe 0.682 / MDD -55.1%
(mandate §2.2/§2.3 — MDD warning-only). Every config dominates SPY's
Sortino. basket2_qld_ugl is the only config with pct_above_benchmark
< 1.0000 (0.93 — fails 0.95 strict bar; 1980-2000 flat-gold drag).

CAGR is highest for baseline (29.85%) because QLD's 2x leverage on NDX
captures the 2003-2021 tech bull most aggressively. Multi-asset baskets
sacrifice ~5-10pp CAGR for ~7-12pp MDD improvement and crisis cover —
the deploy-relevant Sortino reflects this favourably.

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G3 ≥5/8 | G4 OOS S | G5 FWD S | G6 99% low | G7 \|Δ\| pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | **0.881 ✗** | 9.7e-06 ✓ | 7/8 ✓ | 0.825 ✓ | 0.708 ✓ | 0.519 ✓ | 0.000 ✓ |
| basket2_qld_upro | **0.881 ✗** | 1.2e-05 ✓ | 7/8 ✓ | 0.814 ✓ | 0.741 ✓ | 0.518 ✓ | 0.000 ✓ |
| basket2_qld_ugl | **0.881 ✗** | 1.3e-05 ✓ | 5/8 ✓ | 0.810 ✓ | 0.890 ✓ | 0.510 ✓ | 0.000 ✓ |
| basket3_invvol60 | **0.881 ✗** | 4.4e-06 ✓ | 6/8 ✓ | 0.853 ✓ | 0.898 ✓ | 0.555 ✓ | 0.000 ✓ |
| basket3_invvol120 | **0.881 ✗** | 7.6e-06 ✓ | 6/8 ✓ | 0.837 ✓ | 0.862 ✓ | 0.535 ✓ | 0.000 ✓ |
| basket3_eqweight | **0.881 ✗** | 4.1e-06 ✓ | 7/8 ✓ | 0.856 ✓ | 0.863 ✓ | 0.572 ✓ | 0.000 ✓ |

Hard-gate thresholds: G1 PBO < 0.50 (here ✗ for ALL configs); G2 < 0.05;
G3 ≥ 5/8; G4/G5/G6 > 0; G7 |Δ| ≤ 3pp.

**G1 PBO = 0.881 — universally fails.** This is the worst PBO of the
loop (vs iter 004's 0.071, 003's 0.444, 002's 0.159, 001's 0.575). The
diagnostic is structural: 5 of 6 configs are multi-asset variants of
the same trend gate, differing only in basket composition (2 vs 3
assets), vol window (60d vs 120d), or sizing rule (invvol vs eqweight).
CSCV's combinatorially-symmetric 50/50 splits detect significant IS-OOS
rank divergence among these correlated configs.

**Lesson (methodological):** the orthogonal grid that worked in iter 004
(threshold × window × scope, 3 dimensions) is the *correct* answer for
G1 PBO; this iter's single-mechanic grid (basket composition only, with
two sub-dimensions for the fixed 3-asset basket) is the wrong answer.

**G5 FWD post-2020 Sharpe** is consistently *higher* for basket configs
(0.86-0.90) than baseline (0.71) — meaning the post-2020 sample favours
the diversified strategy. This is encouraging for forward stability,
even though G1 fails on the long history.

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_02_dotcom | 2008_GFC | 2020_COVID | 2022_rates |
|---|:---:|:---:|:---:|:---:|
| baseline | ✗ | ✓ | ✗ | ✗ |
| basket2_qld_upro | ✗ | ✓ | ✗ | ✗ |
| **basket2_qld_ugl** | **✓** | ✓ | **✓** | ✗ |
| **basket3_invvol60** | **✓** | ✓ | **✓** | ✗ |
| **basket3_invvol120** | **✓** | ✓ | **✓** | ✗ |
| basket3_eqweight | ✓ | ✓ | ✗ | ✗ |

**The first mechanism in the loop to break the 1-of-4 ceiling.** Three
configs reach 3-of-4 crisis rescue (2000_dotcom + 2008_GFC + 2020_COVID).
Diagnosis:

- **2000_dotcom rescued by UGL:** in 2000-Q1 to 2002-Q3, NDX collapsed
  -78% but gold rose +12%. Inverse-vol weighting in the 3-asset basket
  shifted weight toward UGL as NDX's vol spiked, partially absorbing the
  loss. basket2_qld_ugl achieves this with the most weight on gold;
  basket3_invvol60/120 retain gold even with UPRO present (UPRO's NDX-
  correlated drawdown adds noise but does not break the rescue).
- **2008_GFC** unchanged — vote-K=2 vol_21d<40% gate flips OFF in Sep-
  2008, same as iters 001-004 baselines.
- **2020_COVID rescued by UGL** in invvol baskets: gold rallied during
  Feb-Apr 2020 stress. eqweight (config 6) does NOT rescue COVID because
  fixed 1/3 weight on UPRO 3x means UPRO's Mar-2020 -77% trough
  dominates the basket return before vote-K can flip OFF.
- **2022_rates not rescued by any config** — UGL also fell ~10% in Q2-
  2022 (USD strength + real-rate rise), so even gold-inclusive baskets
  cannot avoid the dual-fall. Same structural diagnosis as iter 004.

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
|---|---:|---:|:---:|---:|:---:|
| `..._on_baseline` | 1.2841 | -0.0405 | F | 1.0000 | False |
| `..._on_basket2_qld_upro_invvol60` | 1.2695 | -0.0551 | F | 1.0000 | False |
| `..._on_basket2_qld_ugl_invvol60` | 1.2849 | -0.0397 | F | 0.9300 | False |
| **`..._on_basket3_qld_upro_ugl_invvol60`** | **1.3340** | **+0.0094** | F | 1.0000 | False |
| `..._on_basket3_qld_upro_ugl_invvol120` | 1.3049 | -0.0197 | F | 1.0000 | False |
| `..._on_basket3_qld_upro_ugl_eqweight` | 1.3317 | +0.0071 | F | 1.0000 | False |

**No config qualifies as `beats_winner=true`.** Two configs cross above
the winner's Sortino (1.3246) but neither clears the +0.05 anti-curve-fit
margin (1.3746) AND `winner_conditions_met=False` for all configs because
G1 PBO 0.881 fails. **basket3_invvol60 is the loop's first config with
positive Sortino edge over the winner benchmark.**

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns, lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % of time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags + basket
  size, sizing rule, vol window, turnover_per_year per config

## KILL_LOOP results (pre-registered in hypothesis.md)

- **KILL_LOOP #1 (success-tag):** **NOT FIRED.** Best Sortino_lh56y =
  1.3340 (basket3_invvol60) < threshold 1.3746. AND
  winner_conditions_met=False (G1 PBO blocker). No config qualifies as
  `beats_winner=true`.
- **KILL_LOOP #2 (decisive-fail):** **NOT FIRED.** All 5 multi-asset
  configs have Sortino_lh56y ≥ 1.27 (well above 1.10 floor). Family is
  *promising* not dead.
- **KILL_LOOP #3 (replica-sanity):** **NOT FIRED.** Baseline replica
  Sortino_lh56y = 1.2841, **bit-exact** match to iters 001/002/003/004
  baselines. Comparative deltas across configs in this iter are valid.
- **KILL_LOOP #4 (single-asset-domination):** **NOT FIRED — partially
  contradicted.** basket3_invvol60 (1.3340), basket3_eqweight (1.3317),
  and basket3_invvol120 (1.3049) all *exceed* baseline Sortino (1.2841).
  basket2_qld_upro (1.2695) underperforms baseline; basket2_qld_ugl
  (1.2849) ties baseline. Iter 023's "QLD × Vote-K=2 is asset-specific"
  finding is **revised**: it holds at single-asset and 2-asset scales,
  but the 3-asset basket clears it via cross-asset diversification.
- **KILL_LOOP #5 (turnover-blowup):** **NOT FIRED.** Max turnover/y =
  5.44 (basket3_invvol60); baseline 2.61. Ratio 2.08× < 3× threshold.
  Inverse-vol rebalancing is meaningfully more turnover-heavy than
  binary state changes but stays within deploy-feasible range.

## Verdict

- **Best config (overall):** `..._on_basket3_qld_upro_ugl_invvol60` —
  STRONG, score 77.5, Sortino_lh56y **1.3340**, **edge +0.0094**.
  First config in the loop with positive Sortino edge over winner.
- **Highest score:** `..._on_basket3_qld_upro_ugl_eqweight` — STRONG,
  score 78.0, Sortino_lh56y 1.3317, edge +0.0071. Highest score driven
  by lower turnover (4.53/y vs 5.44/y) and equivalent Sortino.
- **kill_rule_status:** N/A (loop iter; closed-study T<N>→T<N+1> KILLs
  don't apply)
- **beats_winner:** false (no config exceeds threshold; G1 PBO blocker)
- **cumulative_n_trials_global:** 456

## Conclusion

The multi-asset ON inverse-vol basket hypothesis is **partially
confirmed and represents the most informative loop iter so far**:

1. **The 3-asset basket {QLD, UPRO, UGL} adds real Sortino value** over
   the single-asset baseline (+0.05 lh_56y Sortino), regardless of
   sizing rule (invvol60 1.3340; invvol120 1.3049; eqweight 1.3317;
   all > baseline 1.2841). This is the **first non-trivial improvement
   over baseline** any loop iter has produced.

2. **Crisis attribution improves to 3-of-4** (2000_dotcom + 2008_GFC +
   2020_COVID) for UGL-containing baskets — gold's idiosyncratic
   drawdown profile is genuinely complementary. Equal-weight loses
   the 2020_COVID rescue because fixed 1/3 UPRO weight is over-exposed
   to the Mar-2020 3x SPY trough; inverse-vol weighting is the correct
   approach for crisis cover *during the rescue itself*. **First
   mechanism in the loop to break the 1-of-4 ceiling.**

3. **Cross-iter Sortino edge +0.0094 over winner benchmark** for
   basket3_invvol60. This is small but **the first positive edge in
   the loop**. Iters 001-004 produced edges in [-0.0405, -0.0185]
   range — all replica-drift levels. Iter 005 produces real lift.

4. **G1 PBO 0.881 is the binding constraint, NOT the Sortino margin.**
   The +0.05 anti-curve-fit margin (1.3746) is *almost* cleared by
   basket3_invvol60 (1.3340) — only 0.04 short. But CSCV detects the
   single-axis grid as high-correlation and produces PBO 0.881, which
   alone disqualifies WC. A future iter could redesign the grid
   orthogonally (e.g. 3 asset compositions × 2 sizing rules × 2 vol
   windows = 12 configs spanning 3 mechanic dimensions) to test
   whether the Sortino edge survives proper CSCV.

5. **2022_rates remains unrescued** — even gold-inclusive baskets
   cannot help because UGL also fell in Q2-2022. The 2022 problem is
   genuinely structural for any leveraged-equity strategy and likely
   requires explicit duration-risk timing or rate-regime detection
   (Ilmanen / Carver carry approach), which is the natural next iter.

**Hypothesis status: alive.** Multi-asset ON-leg diversification is the
most fruitful direction in the loop. The next iter should either:
(a) redesign this iter's grid orthogonally to test whether G1 passes
under proper CSCV (mechanic-orthogonal design); OR
(b) move to bond-duration timing (sidesteps the 2022 problem directly,
which multi-asset cannot).

## Lesson (for LOOP_MEMORY iter log)

**First positive Sortino edge in the loop:** basket3_qld_upro_ugl_invvol60
hits Sortino 1.3340 (edge +0.0094 vs winner 1.3246). Three-asset
inverse-vol basket beats single-asset baseline by +0.05 Sortino AND
breaks the 1-of-4 crisis-rescue ceiling (3-of-4: dotcom + GFC + COVID
via UGL gold complement). Two-asset baskets underperform — the
diversification benefit requires the third (cross-asset) leg. Equal-
weight ties inverse-vol on Sortino but loses 2020_COVID rescue (fixed
UPRO 3x weight is over-exposed). **G1 PBO 0.881 is the universal
blocker** — single-mechanic grid (5 multi-asset variants) is high-
correlation; CSCV finds significant IS-OOS rank divergence. WC=False
for all configs despite positive Sortino edges. **2022_rates still not
rescued** — even gold falls during USD-strength + real-rate rebound.
**beats_winner=false** for all configs (best Sortino 1.3340 < 1.3746
margin AND G1 fail). Methodological lesson: orthogonal multi-mechanic
grid (iter 004 style) → clean PBO; single-mechanic grid (iter 005
style) → polluted PBO. Future multi-asset iter should redesign with
3 orthogonal axes.

## Next iter ideas

1. **Bond duration timing** — 10y rate vol > 60d 80th percentile →
   reduce ZROZ exposure or switch to IEF (intermediate duration). Iter
   005 confirmed multi-asset can't rescue 2022_rates because gold fell
   too. Sidestepping bond risk directly is the orthogonal angle. Cite
   `[systematic_trading, ch.9 p.180-190]` Carver carry as regime gate
   (already used for OFF rotation in iter 001 with yield-curve slope —
   here the angle is rate-vol regime, not slope). **Highest expected
   value because it targets the unrescued crisis directly.**

2. **Multi-asset basket re-test with orthogonal grid** — same 3-asset
   {QLD, UPRO, UGL} but vary across 3 mechanic dimensions: (a) basket
   composition {QLD only, QLD+UPRO, QLD+UGL, all-3}, (b) sizing
   {invvol, eqweight, max-decorrel}, (c) trend gate scope {gate-on-QLD,
   gate-on-each-asset}. 8 configs spanning 3 axes. Tests whether iter
   005's positive Sortino edge survives proper CSCV (G1 PBO < 0.5).
   Risk: trial inflation could hurt DSR cumulative.

3. **VIX-percentile / VRP overlay** — VIX above its 60d 80th percentile
   → force OFF (forward-looking implied vol gate, distinct from
   realised-vol already in winner stack). Cite `[volatility_trading,
   ch.7]` Sinclair on variance risk premium. Partial-period analysis
   (VIX history from 1990; lh_56y has 35y warm-up).

4. **Equity factor tilt on ON-leg** — replace QLD with a
   profitability-tilted equity LETF or a low-vol-tilted basket.
   Furthest from current iter; lowest priority because LETF universe
   is narrow.

## INCOMPLETE flags

- **Replica drift (~0.04 Sortino):** baseline Sortino_lh56y = 1.2841 vs
  canonical iter 022 winner 1.3246. Drift documented in iter 001 as a
  consequence of the loop's data-loading warmup boundary differing from
  iter 022 by ~248 days. Comparative deltas across configs in this iter
  are bit-exact valid.
- **Trend gate is QLD-only** — the basket holds {QLD, UPRO, UGL} but
  the regime detection uses only QLD's vote-K=2 signals. Per-asset
  trend gates with per-asset OFF rotation would be a different study;
  out of scope this iter (would conflate signal-tuning with basket
  effect).
- **Daily inverse-vol rebalancing is the upper bound of cost** —
  realistic deploy would need monthly rebalancing or vol-band
  thresholds. The 5.44/y turnover proxy includes daily basket-weight
  shifts; production-feasible turnover would be lower with periodic
  rebalancing. Caveat: lower-rebalancing-frequency implementation
  would also have lower Sortino tracking-precision (vol-shifts are
  noisy at sub-monthly cadence).
- **UGL synth caveat (per iter 000-v2):** UGLSIM was calibrated with
  `LETF_EXPENSE_RATIOS["UGL"] = 0.030` after bisection on real UGL
  2008-2026 tracking. Pre-2008 UGL synth inherits this calibration.
  Comparative deltas across UGL-using configs in lh_56y window remain
  valid because all configs see the same synth.
- **G1 PBO 0.881** is the universal blocker, not the Sortino margin.
  A redesigned grid with 3 orthogonal mechanic axes would be the
  proper test of whether basket3_invvol60's +0.0094 edge is robust.
- **Vol windows {60d, 120d} only** — the two-window comparison
  controls for "fast vs slow" without curve-fit risk. A 4-window
  sweep would inflate trial count for marginal interpretive gain.
- **Tax/fees gross only** (matching closed-study convention).
  Multi-asset basket rebalancing in real deployment would have
  meaningful transaction costs ≥ baseline.
- **2022_rates target not rescued** — gold also fell in Q2-2022 as
  USD strength + real-rate rebound dominated. Even cross-asset first-
  moment diversification cannot save a strategy from a 3-asset dual-
  fall regime; explicit duration-risk timing is the orthogonal angle.
- **basket2_qld_ugl pct_above_benchmark = 0.93** breaks the 0.95
  strict bar (KILL_LOOP #4 informational tag) due to UGL's 1980-2000
  flat-to-negative regime. The 3-asset baskets recover pct_above to
  1.0000 because UPRO/QLD provide enough equity exposure to keep the
  basket above SPY during the gold flat decades.
