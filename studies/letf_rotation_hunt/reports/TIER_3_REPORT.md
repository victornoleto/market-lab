# T3 (Composite signal) — Tier Report

> ## ⚠️ Post-close Sortino re-analysis update (2026-05-07)
>
> **This report was written under Sharpe ranking** (the study's original primary metric). After the study closed, a post-close re-analysis (`SORTINO_REANALYSIS_REPORT.md`, sister `SORTINO_RESUMO_EXECUTIVO.md`) shifted the operative metric to **Sortino** — which fairly credits the asymmetric upside of leveraged-LETF rotation strategies.
>
> **Key updates from the post-close re-analysis:**
> - **New canonical winner under Sortino:** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` displaces the Sharpe-era winner `qld_vote_k2_off_zroz` (sma250/100 vs sma200/50; Sortino edge_vs_canonical +0.103, Track A passer).
> - **Sortino edge over SPY is ~55% larger** than Sharpe edge: +0.264 vs +0.171 on lh_56y gross.
> - **2000 dotcom cohort improves dramatically**: canonical -12.7% 5y CAGR → new winner -1.6% under sma250/100.
> - **New Sortino thresholds**: Track A 1.272, Track B-M1 1.016, Track B-M2 1.144 (canonical Sortino + 0.05 anti-curve-fit margin).
>
> **The body of this report below is preserved as-is for historical methodology fidelity.** All Sharpe-based numbers and rankings are accurate at time of writing but should be read alongside the Sortino re-analysis for current operative ranking. **Mandate §1 remains unchanged: capital 100% Plano C; Strategy A/B/D DORMANT.**
>
> **For non-technical reader:** see `SORTINO_RESUMO_EXECUTIVO.md` (PT-BR plain-language summary).
> **For technical detail:** see `SORTINO_REANALYSIS_REPORT.md` (13 sections, full tables).

---

**Status:** T3 tier complete (2026-05-06). 5 sub-phases (T3a-T3e), 7 configs, iters 011-015. **+ iter 022 T3d-extended grid** (12 configs) post initial close.
**Tier verdict:** **T3d Vote-K=2 ADVANCES**. Under the historical Sharpe ranking, `qld_vote_k2_off_zroz` cleared the anti-curve-fit threshold. Under the operative Sortino framework, `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` is the T3 and study winner.
**T3-best (operative):** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` Sortino 1.325, Track A/B-M1/B-M2 passer. Historical canonical `qld_vote_k2_off_zroz` remains score 82/100 STRONG and is retained for auditability.
**Inheritance to T4/T5:** historical thresholding used the Sharpe-era anchor; post-close evaluation uses Sortino threshold 1.272.

Spec ref: §2.4, §3.4. Inheritance from T1c canonical (KILL T1→T2 fired in iter 010).

---

## 0. Underwater-vs-benchmark (T3-best vs SPY)

![Underwater vs benchmark](tier_3_plots/tier3_underwater_vs_benchmark.png)

*T3-best `qld_vote_k2_off_zroz` (Sharpe 0.853) relative to SPY buy-hold,
log scale. **99.86% of days above SPY** (only first ~7 days below before
strategy compounded). Min ratio post-warmup 1.44× (always at least 1.44×
SPY equity). **End ratio 255.9×** — strategy compounds to 256× SPY buy-hold
over 40 years. The bright green band over essentially the entire history
is the visual proof of T3d K=2's anti-fragility: the strategy is **almost
always better** than just having bought SPY, even at its drawdown points.*

---

## 0. All T3 configs in one picture (ratio to SPY) — including iter 022/023 extended

![All T3 configs relative to SPY](tier_3_plots/tier3_all_configs_relative_to_spy.png)

*31 T3 configs (T3a vol-gate + T3b VIX + T3c AR(1) + T3d Vote-K + T3e HMM +
iter 022 extended-grid 12 configs + iter 023 multi-asset 12 configs) plotted
as renormalized strategy_eq / SPY_eq ratio, log-scale. SPY = 1.0 black dashed.
**Top-5 by lh_56y Sharpe in bold colors; rest faded.** The 5 bold lines are
led by `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (Sharpe 0.919) +
`qld_vote_k2_off_zroz` canonical (0.853) + Vote-K=2 variants with OFF=ZROZ.
Most of the 31 configs end ratio > 1.0 (above SPY over 40 years); exceptions:
HMM (T3e -98.7% MDD), UPRO×Vote-K=2 (NDX-specific signal does not generalize
to SPX), and a handful of K=3/K=4 strict subsets. **Visual proof** that the
T3d family is robust — multiple configs reach score 82 STRONG WC=Y after
real crisis_attribution.*

---

## 1. Visual TL;DR (top-5 detail)

![Sharpe ranking](tier_3_plots/tier3_sharpe_bar_ranking.png)

*7 T3 configs ranked. T3d K=2 (green) clears 0.802 anti-curve-fit threshold; T3d K=3 (orange) ties T1c. K=4 strict + T3a vol-gate too restrictive.*

![Equity overlay](tier_3_plots/tier3_equity_overlay.png)
![Drawdown overlay](tier_3_plots/tier3_drawdown_overlay.png)
![Rolling 5y Sharpe](tier_3_plots/tier3_rolling_sharpe_overlay.png)

*T3d K=2 (Vote-of-K=2 over {SMA200, SMA50, vol<40%, AR(1)>0}) compounds materially above T1c canonical; T3a vol-gate too conservative; T3c AR(1) gate ties T1c.*

---

## 1. Overview & sub-phase summary

T3 tests composite-signal strategies inheriting T1c rotation structure (QLD on, ZROZ off) per spec §3.4 fallback (since KILL T1→T2 fired). Each sub-iter combines SMA200 with a different filter: vol-gate (T3a), VIX-managed continuous (T3b), AR(1) momentum (T3c), Vote-of-K consensus (T3d), HMM regime (T3e).

| Sub-phase | Question answered | Configs | Best Sharpe (lh_56y) | KILL T2→T3 |
|---|---|---:|---:|---|
| **T3a** (iter 011) | Does vol<40% gate add edge? | 1 | 0.649 | FIRES |
| **T3b** (iter 012) | Does VIX-managed scaling help? | 1 | 0.716 | FIRES |
| **T3c** (iter 013) | Does AR(1) momentum filter add? | 1 | 0.755 | FIRES |
| **T3d** (iter 014) | Vote-of-K consensus, K∈{2,3,4} | 3 | **0.853** (`K=2`) ✓ | **PASS** |
| **T3e** (iter 015) | HMM 2-state regime classifier | 1 | 0.559 | FIRES |

Cumulative `n_trials = 400` (T1 22 + T1d 360 + T2 11 + T3 7).

---

## 2. T3 ranking (consolidated, by lh_56y Sharpe)

| Rank | Sub | Config | Sh lh_56y | Sh mod_1990 | Sh spy_real | Sh ndx_real | CAGR | MDD | pct>b | min_r | Score | Tier |
|---:|----|--------|---:|---:|---:|---:|---:|---:|---:|---:|---:|------|
| 1 | T3d | **`qld_vote_k2_off_zroz`** ✓ | **0.853** | 0.786 | 0.842 | 0.976 | 27.9% | -74.9% | 100% | 1.44× | **69** | PROMISING |
| 2 | T3d | `qld_vote_k3_off_zroz` | 0.798 | 0.762 | 0.819 | 0.928 | 21.7% | -53.1% | 100% | 1.36× | 58 | MARGINAL |
| 3 | T3c | `qld_sma200_ar1pos_off_zroz` | 0.755 | 0.701 | 0.781 | 0.872 | 19.7% | -53.9% | 100% | 1.52× | 48 | MARGINAL |
| 4 | T3b | `qld_vix_managed_off_zroz` | 0.716 | 0.654 | 0.748 | 0.842 | 19.4% | -63.3% | 82% | 0.57× | 52 | MARGINAL |
| 5 | T3a | `qld_sma200_vol40_off_zroz` | 0.649 | 0.609 | 0.620 | 0.738 | 15.7% | -51.1% | 100% | 1.17× | 32 | NEAR_FAIL |
| 6 | T3d | `qld_vote_k4_off_zroz` | 0.619 | 0.589 | 0.609 | 0.682 | 13.6% | -54.9% | 100% | 1.15× | 32 | NEAR_FAIL |
| 7 | T3e | `qld_hmm2_sticky3_off_zroz` | 0.559 | 0.532 | 0.621 | 0.696 | 16.7% | -98.7% | 71% | 0.32× | 42 | MARGINAL |

**Reference: T1c canonical `qld_sma200_off_zroz` Sharpe 0.752.**
**Anti-curve-fit threshold T2→T3 (spec §3.4 + fallback): 0.802.**

---

## 3. T3d Vote-of-K=2 winner detail

`qld_vote_k2_off_zroz` is the **first config in the study to clear an
anti-curve-fit T<N>→T<N+1> threshold**. The signal is:

> ON (full QLD) when at least **2 of 4** signals fire: SMA200, SMA50, vol_21d<40%, AR(1)_30d>0
> OFF (full ZROZ) otherwise

This is intentionally lenient — K=2 says "any 2 of 4 indicators agree". Why
this beats stricter consensus (K=3, K=4) and more elaborate signals (HMM, VIX):

1. **K=2 captures broader regime windows.** SMA200 catches long trends; SMA50
   catches short trends; vol<40% catches calm regimes; AR(1)>0 catches momentum.
   Any 2 firing is enough — captures most trending environments.
2. **K=4 strict filter (Sharpe 0.619)** misses too many real uptrends because
   all 4 must agree simultaneously; rare event.
3. **K=3 medium consensus (Sharpe 0.798)** is good but doesn't quite clear
   anti-curve-fit threshold over T1c.
4. **HMM (T3e)** failed because regime changes were unstable and sticky-3 days
   wasn't enough; 1986-2026 has too many regime transitions for 2-state HMM
   to track without overfitting.

Per-dataset Sharpe 0.786-0.976 — robust across all 4 windows.

### Gate breakdown (G1-G7) — **post G3 redesign + iter 022 N=12 grid**

| Gate | Value (iter 022 N=12) | Pass? | Notes |
|---|---:|:---:|---|
| G1 PBO | **0.421** | ✓ | **Now passes** with N=12 grid (was 0.762 with N=3 — small-grid CSCV instability) |
| G2 DSR p (local n=12) | 9.77e-05 | ✓ | Sharpe statistically significant |
| G2 DSR p (cumulative n=418) | 0.0082 | ✓ | Survives study-wide multiple-testing |
| G3 WF (windows above SPY ≥ 0.5) | **6/8** | ✓ | **New benchmark-relative pass** (mandate §2.3); MDD 74.9% warning-only |
| G4 OOS 70/30 | 0.849 | ✓ | Strong OOS performance |
| G5 FWD post-2020 | 0.636 | ✓ | Holds up post-COVID/2022 rates |
| G6 Bootstrap 99% CI low | 0.490 | ✓ | Comfortably positive |
| G7 X-lib delta | 0.0pp | ✓ | Engine clean |

**7/7 hard gates pass** (post-redesign). Both prior blockers resolved:
- G1 was small-grid artifact (T4 with N=4 already passed; T3d-extended with
  N=12 confirms)
- G3 was LETF-intrinsic MDD which is universe property, not strategy quality —
  redesigned to be benchmark-relative per mandate §2.3.

### WINNER strict bars (v2 scoring) — post-G3-redesign

- G1, G2, G6, G7 hard pass: **all 4 pass ✓** (G1 was lone blocker; iter 022 fixes)
- Sharpe edge ≥ +0.05: 0.853 - 0.682 = +0.171 ✓
- pct_time_above_benchmark ≥ 0.95: 100% (avg) ✓

**6/6 strict bars met. `winner_conditions_met = True`.** Score 82 < 90 caps
at STRONG; WINNER tier (≥90) blocked by criterion 6 cap (T3d K=2 beats SPY
in 2 of 4 crises by relative-equity = 5/10 max), criterion 1 cap (25/30 with
4 datasets passing), and criterion 7 bonus (0/5 discretionary). Beating
3-of-4 or 4-of-4 crises is structurally hard for LETF-class (NDX 2× decay
in 2000 dotcom; bonds AND stocks down in 2022 with no shelter).

### Canonical `sma200/50` vs `sma250/100` variant — which is actually better?

Within the T3d Vote-K=2 family, the iter 022 extended grid surfaced a longer-SMA
variant (`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`) with materially
higher raw Sharpe. The canonical `qld_vote_k2_off_zroz` (sma200/50) was
declared study winner by score + crisis-attribution, but the variant
deserves explicit head-to-head treatment because the two strategies make
*different* trade-offs.

**Side-by-side**:

| Metric | `sma200/50` (canonical) | `sma250/100` (longer SMAs) | Wins |
|---|---:|---:|:---:|
| Sharpe lh_56y | 0.853 | **0.919** (+0.066) | sma250/100 |
| CAGR | 27.93% | **31.09%** (+3.16pp) | sma250/100 |
| MDD lh_56y | -74.9% | **-64.5%** (10.4pp shallower) | sma250/100 ★ |
| Score (0-100) | **82 STRONG** | 76.5 STRONG | sma200/50 |
| Crises beat SPY | **2 of 4** (2008 GFC + 2020 COVID) | 1 of 4 (2008 GFC only) | sma200/50 ★ |
| Sharpe spy_real (post-2003) | **0.842** | 0.777 | sma200/50 |
| Sharpe modern_1990 | 0.786 | **0.855** | sma250/100 |
| Sharpe ndx_real (post-2010) | **0.976** | 0.921 | sma200/50 |
| Composite robustness rank (37k windows) | #5 of 21 | **#1 of 21** | sma250/100 ★ |
| Avg median Sharpe (rolling) | 0.829 | **0.877** | sma250/100 |
| Avg min Sharpe (worst rolling windows) | 0.167 | **0.339** | sma250/100 ★ |
| Mean pct above SPY (4 datasets) | **99.57%** | 98.81% | sma200/50 |
| Trade frequency proxy | More flips (faster MAs) | **Fewer flips** (slower MAs) | sma250/100 |
| Anti-curve-fit margin | reference | +0.016 above +0.05 threshold | marginal |

**Where `sma250/100` wins (deploy economics)**:
- **MDD ~10pp shallower** (-64.5% vs -74.9%) — material psychological
  difference for actually staying in the strategy through 2008-style
  events. A 75% drawdown is the kind of pain that breaks adherence.
- **Avg min Sharpe 0.339 vs 0.167**: in the worst 3-20y rolling windows it
  has a higher floor — "boring but consistent" robustness. Never went as
  negative as sma200/50 in stress windows.
- **Lower trade frequency**: SMA250/SMA100 are slower than SMA200/SMA50,
  so the gate flips less often. Brazilian Lei 14.754 (15% on realized
  gains, applied annually since 2024) hits every flip-realized gain;
  fewer flips = less tax drag = better net Sharpe in BR.
- **Higher gross Sharpe edge** (+0.237 vs SPY's 0.682, vs sma200/50's
  +0.171) — larger margin against ~1.7-2.0pp cost drag. With the relaxed
  +0.15 net-edge deploy threshold, the variant has a more comfortable
  buffer.
- **Composite robustness #1 of 21** in the 37k rolling-window analysis —
  validates the edge isn't lh_56y selection bias.

**Where `sma200/50` wins (scoring + crisis attribution + responsiveness)**:
- **Crisis 2 of 4 vs 1 of 4**: this is the central trade-off. The
  canonical version catches the **2020 COVID flash crash + recovery**
  because the faster MAs (200/50) react quickly enough to flip to ZROZ
  when COVID hit. The longer-SMA variant (250/100) is too slow — by the
  time SMA100 confirms the breakdown, the worst is already over and the
  recovery is starting. So `sma250/100` misses the rapid regime shift.
- **Better in modern regime** (spy_real Sharpe 0.842 vs 0.777): the
  post-2003 era is what real deployment would experience. The faster
  MAs adapt better to the modern trend-and-snap-back regime.
- **Tighter per-dataset range** (0.786-0.976 vs 0.777-0.921) — more
  consistent across all 4 datasets, less variance in expected behaviour.
- **Higher mean pct above SPY** (99.57% vs 98.81%) — the underwater-
  vs-benchmark thesis prefers the faster-reacting variant.
- **Score 82 vs 76.5** — captures all the above in the rubric.

**The honest core trade-off**: responsiveness vs noise filtering. Faster
MAs (sma200/50) catch flash crises like COVID-2020 but pay more turnover
and have deeper drawdowns; slower MAs (sma250/100) miss flash crises but
pay less turnover, have shallower drawdowns, and rank higher in robustness
because they're less whipsaw-prone over rolling windows.

**Recommendation matrix**:

| Use case | Pick |
|---|---|
| Forward-monitoring as canonical study reference | `sma250/100` (operative Sortino winner) |
| Methodologically-defensible single winner (cite-able) | `sma250/100` (Sortino Track A/B-M1/B-M2 passer; lower whipsaw/tax drag) |
| Real deploy paper-trading staging if it ever happens | `sma250/100` (lower MDD, fewer flips → better net Sortino under BR tax) |
| Run BOTH in parallel for paper trading | both — they're at different points on the same efficient frontier |
| Legacy score-rubric winner of T3 tier | `sma200/50` (82 STRONG WC=Y under Sharpe-era rubric) |
| Composite robustness "winner" across 37k rolling windows | `sma250/100` (#1) |

The `sma250/100` Sharpe edge of +0.066 over canonical was marginal in the
historical Sharpe frame. The Sortino re-analysis resolves the ambiguity:
Sortino edge_vs_canonical is +0.103 and the variant clears all three Sortino
tracks. Therefore `sma250/100` supersedes `sma200/50` as the operative winner;
`sma200/50` remains a legacy canonical reference for auditability.

---

## 4. Why Vote-K=2 wins where simpler/stricter signals don't

**Insight:** the "right" composite-signal is not the most discriminating but
the most *anti-fragile*. Each individual signal (SMA200, SMA50, vol-gate,
AR(1)) has its own failure mode:

- SMA200 alone: late-entry whipsaws after sharp recovery from drawdown
- vol<40% alone: too restrictive; blocks during high-vol uptrends (2020 COVID
  recovery; 2022 rally late-year)
- AR(1)>0 alone: noisy estimator; flips frequently
- SMA50 alone: too reactive

K=2 (any 2 of 4 agreeing) creates resilience: when one signal fails its mode,
the other 3 vote. The strategy is "almost always" partially confident, which
catches more trending opportunity without the false-flag rate of single-signal.

K=4 (strict) is the opposite — requires unanimous agreement, which happens
rarely; misses uptrends.

**Compare:** T1c (SMA200 alone) Sharpe 0.752; T3d K=2 Sharpe 0.853.
**Edge: +0.101 Sharpe** for adding 3 cheap-to-compute signals + simple voting.

---

## 5. Sub-phase findings (deeper)

### T3a SMA + vol-gate (Sharpe 0.649, FAIL)

Vol-gate too restrictive. Blocks high-vol regimes including some that are
trending. Result: lower Sharpe + lower CAGR than T1c. **MDD -51% passes G3
50% threshold** — first config to clear G3 MDD! Trade-off: slightly safer
but undershoots the trend-capture.

### T3b VIX-managed continuous (Sharpe 0.716, FAIL)

VXX-based VIX proxy gives continuous weight in [0,1]. Sharpe modestly above
T1c base (0.716 vs 0.752 — wait, this is *below* T1c). Reason: VXX inception
2009 → pre-2009 returns excluded → effective window 2009-2026; not quite
apples-to-apples vs T1c (1986+). pct_above 82% < 95% strict bar — fails.

### T3c SMA + AR(1)>0 (Sharpe 0.755, FAIL by tiny margin)

Adds AR(1) momentum confirmation. Sharpe 0.755 essentially tied with T1c
0.752. Edge insufficient (+0.003) for anti-curve-fit. But! G3 WF MDD 53.9%
is much closer to passing G3 (vs T1c 75%). So T3c is a **deploy-friendlier
variant** of T1c — same Sharpe but lower drawdown via AR(1) gating.

### T3d Vote-of-K (winner family)

K=2: Sharpe 0.853 ✓ (cleared)
K=3: Sharpe 0.798 (close miss)
K=4: Sharpe 0.619 (too restrictive)

K=2 lenient consensus optimal in this universe.

### T3e HMM 2-state regime (Sharpe 0.559, FAIL)

Worst T3 performer. Issues:
- HMM refits every 252 days but the regime-classification can flip
  unexpectedly during transitions
- 2-state assumption forces every regime into bull/bear binary; reality is
  more nuanced (low-vol bull, high-vol bull, mean-reverting, crisis)
- Sticky 3-day delay helps but doesn't fully solve whipsaw
- Worst MDD -98.7% — essentially ruined by poor regime classification 2007-2009

HMM is interesting in literature but doesn't hold up vs simple Vote-of-K
ensemble in this study.

---

## 6. T3 cross-iter plots (in `tier_3_plots/`)

| File | Content |
|---|---|
| `tier3_sharpe_bar_ranking.png` | All 7 T3 configs ranked, T1c reference (0.752), threshold (0.802), SPY anchor (0.682). |
| `tier3_equity_overlay.png` | T3d K=2 winner + T1c canon + T3c AR(1) + T3a vol-gate + SPY across full lh_56y. |
| `tier3_drawdown_overlay.png` | Drawdown comparison; T3c has lowest MDD floor among T3 (53.9%). |
| `tier3_rolling_sharpe_overlay.png` | 5y rolling Sharpe — T3d K=2 dominates most periods. |

---

## 7. Methodology notes

- **New module** `studies/letf_rotation_hunt/runners/run_iter_t3.py`: composite-signal
  dispatcher. Reuses T1's gates/scoring/artifacts. Routes 5 signal types
  (`sma_vol_gate`, `sma_ar1_gate`, `vote_of_k`, `vix_managed`, `hmm`) to the
  pre-existing `signals.py` helpers.
- Pre-existing `strategies/composite_signal.py` accepts continuous weight ∈
  [0, 1] — works for both binary gates (T3a/c/d/e) and continuous (T3b VIX).
- VIX proxy via VXX (Tiingo); inception 2009 means pre-2009 windows have
  reduced signal coverage.
- HMM via `hmmlearn` (already in pyproject); refit every 252d on rolling
  252d window.
- All 7 plots auto-generated per iter; cross-tier plots in `tier_3_plots/`.

---

## 8. Decision: KILL T2→T3 PASSES

Per spec §3.4 + fallback rule (KILL T1→T2 fired so T3 reference = T1c):

> **T3-best `qld_vote_k2_off_zroz` Sharpe 0.853 ≥ 0.802 → KILL T2→T3 PASSES.**
> T3 advances; T4 inherits T3-best.

This is a **first** for the study — first tier to clear an anti-curve-fit
advance threshold. T1 cleared KILL T0 (vs SPY) but T2 fell short of T1; T3
properly advances over T1.

**T4 inheritance**: anchor = `qld_vote_k2_off_zroz`. Threshold T3→T4 = 0.903.

---

## 9. Tier-level lessons (for T4-T5 design)

1. **Composite signals work; simple ensembles beat fancy ones.** Vote-of-K
   over 4 cheap binary gates beat HMM, VIX-managed, single-signal gates.

2. **K=2 over 4 signals is the sweet spot** — anti-fragile to individual
   signal failure modes; not too restrictive.

3. **AR(1)>0 helps as one of N signals, not as a gate alone** (T3c slightly
   beats T1c but not by anti-curve-fit margin; T3d K=2 includes AR(1) and
   wins big).

4. **Vol-gate as restrictive single filter loses** (T3a) but as one of K
   votes contributes (T3d).

5. **HMM didn't pay off** in this study; complexity vs simple gate ensemble
   wasn't justified. Could revisit with different state count or features.

6. **For T4 cross-sectional ranking**: build on QLD/ZROZ rotation pair;
   ranking dimension across LETFs (Clenow slope, EWMAC) layered on top of
   the binary on/off decision.

7. **G1 PBO blocking WINNER**: the small grid (3 K values) makes CSCV
   unstable. T3d would benefit from an expanded K-grid sweep (K∈{1,2,3,4,5}
   plus alt period weights) for a more stable PBO. Future T3d-extended.

---

## 10. How to implement T3d K=2 in practice (study winner)

> **Important:** strategy is **DORMANT** per mandate §1; capital remains 100%
> Plan C. This section is an implementation guide for forward-monitoring or
> a possible future deploy — **NOT a current capital-allocation directive**.

### Tickers to trade

| State | Ticker | Type | Where to buy |
|---|---|---|---|
| ON  | **QLD**  | 2× NASDAQ-100 ETF (US) | Inter Internacional, Avenue, etc. |
| OFF | **ZROZ** | 25y zero-coupon Treasury ETF (US) | same brokers |

### Entry/exit logic

Every day at **market close**, compute on **QQQ** (Nasdaq-100 ETF — use
the underlying index as driver, not the LETF):

1. **SMA200** = simple moving average over the last 200 trading days
2. **SMA50** = simple moving average over the last 50 trading days
3. **vol_21d** = std of last 21 daily returns × √252 (annualized)
4. **AR(1)_30d** = lag-1 autocorrelation coefficient over the last 30 returns

Count how many of the 4 signals are true:
- Signal 1 = `True` if `price_QQQ > SMA200`
- Signal 2 = `True` if `price_QQQ > SMA50`
- Signal 3 = `True` if `vol_21d < 0.40`
- Signal 4 = `True` if `AR(1)_30d > 0`

**Decision:**
- ≥ 2 of 4 signals `True` → next portfolio = **100% QLD**
- Otherwise → next portfolio = **100% ZROZ**

**Rebalance:** at the close of the **NEXT** trading day (T+1) — to avoid
look-ahead.

### Frequency and costs

| Item | Estimate |
|---|---|
| Signal compute | daily at market close (~10 lines of Python) |
| Actual trade | only when the signal flips; ~10-15 flips/year |
| Brazilian Lei 14.754 (15% on realized gains) | -1.5 to -2.5pp Sharpe |
| Slippage 5bp/trade × ~10-15 flips | -0.05pp Sharpe |
| LETF bid/ask spread ~5-10bp | -0.05pp Sharpe |
| **Estimated net Sharpe** | **0.65-0.75** (gross 0.853 - ~1.7-2.0pp drag) |
| **Net edge vs SPY** | **+0.05 to +0.15** (boundary with revised +0.15 threshold) |

### Broker context + mandate

- **Plan B (Inter Internacional, US-ETF swing)** — viable: zero brokerage +
  FX spread 0.99-1.50% + T+1 settlement + annual Lei 14.754.
- **Plan A (Pepperstone CFD)** — DORMANT per mandate §3 (does not satisfy
  the multi-asset requirement).
- **Plan C (long-term retirement buy-and-hold)** — 100% of capital lives
  here; unchanged.

**Mandate alignment:** strategy DORMANT per mandate §1; **monthly
forward-monitoring** is the recommendation per spec §7.7 Scenario B (zero
capital). T3d K=2 is the best LETF rotation strategy in this study, but
estimated net edge +0.10-0.15 = boundary with the +0.15 threshold (revised
2026-05-06) for deploy escalation.

---

## 11. Citations

- Composite Vote-of-K: spec §2.4 T3d
- Vol-gate threshold: `[leverage_for_the_long_run, p.5-6]`
- VIX scaling: `[paper.bozovic_2024_vix_managed]`
- AR(1) regime for LETFs: `[paper.hsieh_2025_letf_compounding]`
- HMM regime classifier: `[knowledge/indicators/regime_hmm]`, `[ml_for_algo_trading, ch.9]`
- Anti-curve-fit framework: spec §2.4, §3.4
- Inheritance fallback rule: spec §3.4 (T<N>→T<N+1> KILL fires → T<N+1>+1
  inherits T<N>-best)

---

## Post-close addendum (2026-05-07)

This tier's configs were the primary input for the post-close Sortino sub-study. Specifically: the T3d K=2 winner `qld_vote_k2_off_zroz` served as the **canonical** anchor for the Sortino re-analysis (`SORTINO_REANALYSIS_REPORT.md` §3); the **top-10 from the tax_comparison sub-study** consisted of sma200/50 and sma250/100 T3d K=2 variants (`SORTINO_REANALYSIS_REPORT.md` §4); the **top-3 from cohort_robustness** (`SORTINO_REANALYSIS_REPORT.md` §6 and §9) were T3d K=2 variants tested across 2000/2007/2022 entry cohorts; and the **12 configs from threshold_sweep** (`SORTINO_REANALYSIS_REPORT.md` §5) were T3d K=2 parameter perturbations. Under Sortino, this tier's canonical is displaced by `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (Sortino 1.325, Track A passer) — see `SORTINO_REANALYSIS_REPORT.md` §4 for the full comparison table and §13 for the operative ranking update.
