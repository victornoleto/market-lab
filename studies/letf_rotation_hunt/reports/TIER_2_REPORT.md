# T2 (HFEA-binary basket) — Tier Report

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

**Status:** T2 tier complete (2026-05-06). 11 configs across 6 sub-phases (iters 005-010).
**Tier verdict:** **KILL T1→T2 FIRES across all configs.** T2-best Sharpe 0.653 << threshold 0.802. HFEA basket family does NOT add value over T1c rotation in this universe.
**T2-best:** `hfea_ndx_tqqq_tmf_55_45` Sharpe 0.653 (lh_56y), MARGINAL score 51.
**Inheritance to T3:** **T1-best `qld_sma200_off_zroz`** (per spec §3.4 inheritance fallback when KILL T<N>→T<N+1> fires; T2 contributes nothing to incumbent).

Spec ref: §2.3, §3.4 (anti-curve-fit threshold: T2-best Sharpe ≥ T1-best + 0.05 = 0.802).

---

## 0. Underwater-vs-benchmark (T2-best vs SPY)

![Underwater vs benchmark](tier_2_plots/tier2_underwater_vs_benchmark.png)

*T2-best `hfea_ndx_tqqq_tmf_55_45` (Sharpe 0.653) relative to SPY buy-hold,
log scale. **Only 59.20% of days above SPY** — substantial periods underwater.
Min ratio post-warmup 0.38× (HFEA basket fell to 38% of SPY equity at one
point). End ratio 4.5×. This is precisely why T2 fails the v2 underwater
scoring strict bar (pct ≥ 0.95 required) — basket structure spends material
time below the buy-hold benchmark, even though it terminates higher.*

---

## 0. Scoring v2 update (2026-05-06) — Underwater-vs-Benchmark

Per user observation 2026-05-06: criterion 2 swapped from MDD-vs-SPY to
underwater-vs-benchmark (`pct_time_above_benchmark` + `min_relative_equity`)
with WINNER strict bar at 95%. See TIER_1_REPORT §0 for full rationale.

Re-scored T2 results with v2 rubric:

| Iter | Best config | v1 score | v2 score | tier (v2) | Δ |
|------|-------------|---:|---:|------|---:|
| T2a | hfea_55_45_half_off | 32.0 | 38.0 | NEAR_FAIL | +6 |
| T2b | hfea_70_30_full_off | 32.5 | 32.0 | NEAR_FAIL | -0.5 |
| T2c | hfea_ndx_tqqq_tmf_55_45 | 47.2 | 46.0 | MARGINAL | -1.2 |
| T2d | stack_upro_edv_60_40 | 33.4 | 32.0 | NEAR_FAIL | -1.4 |
| T2e | trinity_upro_tmf_ugl | 42.8 | 42.0 | MARGINAL | -0.8 |
| T2f | hfea_ndx_55_45_half_off | 32.0 | 38.0 | NEAR_FAIL | +6 |

T1c canonical (incumbent) v2 score: **61** (PROMISING) vs T2-best v2 46
(MARGINAL). **KILL T1→T2 still FIRES**, gap widens slightly under v2 since
T1c gets full underwater credit (100% above SPY) while T2 baskets often dip
below SPY during equity drawdowns + bond drag in 2022.

Anti-curve-fit threshold T1→T2 (Sharpe-based) **unchanged at 0.802** —
threshold is on Sharpe edge, not score. T2-best Sharpe 0.653 << 0.802 in
both v1 and v2. **No change to KILL verdict.**

---

## 0. All T2 configs in one picture (ratio to SPY)

![All T2 configs relative to SPY](tier_2_plots/tier2_all_configs_relative_to_spy.png)

*11 T2 HFEA-basket configs as strategy_eq / SPY_eq ratio (renormalised, log-scale).
SPY = 1.0 black dashed. **Top-5 bold; rest faded.** Pattern: HFEA-NDX
(TQQQ+TMF) is the only family to sustain a ratio > 1.0 consistently; UPRO+TMF
classic and weight-sweep variants spend extended periods below SPY (especially
during the 2022 rate collapse). Visual proof of the central T2 finding:
**rotation > stacking** — no basket clears the anti-curve-fit threshold T1c+0.05=0.802.*

---

## 1. Visual TL;DR (top-5 detail)

![Sharpe ranking](tier_2_plots/tier2_sharpe_bar_ranking.png)

*All 11 T2 configs ranked by lh_56y Sharpe. None clear the 0.802 threshold (red dashed line). T1c incumbent (black dashed) at 0.752 dominates. SPY anchor (gray dotted) at 0.682. Color: red = below SPY, orange = between SPY and T1c, green = above T1c (none).*

![T1c vs T2c head-to-head](tier_2_plots/tier2_t1c_vs_t2c_zoomed.png)

*Direct comparison: T1c rotation (green) ends substantially higher than T2c HFEA-NDX (orange), the T2-best. Both beat SPY (gray) but only T1c clears the +0.05 KILL threshold over SPY. Bottom panel: drawdown — T2c has lower MDD floor (49%) but T1c ends with materially higher capital.*

![Equity overlay](tier_2_plots/tier2_equity_overlay.png)
![Drawdown overlay](tier_2_plots/tier2_drawdown_overlay.png)
![Rolling 5y Sharpe](tier_2_plots/tier2_rolling_sharpe_overlay.png)

*Top 5 T2 configs + T1c incumbent + SPY benchmark across full lh_56y window.*

---

## 1. Overview & sub-phase summary

| Sub-phase | Hypothesis | Configs | Best Sharpe (lh_56y) | KILL T1→T2 |
|---|---|---:|---:|---|
| **T2a** (iter 005) | HFEA classic UPRO+TMF 55/45 × {full-off, half-off} | 2 | 0.571 (`hfea_55_45_half_off`) | FIRES |
| **T2b** (iter 006) | UPRO+TMF weight sweep {60/40, 65/35, 70/30} | 3 | 0.583 (`hfea_70_30_full_off`) | FIRES |
| **T2c** (iter 007) | HFEA-NDX TQQQ+TMF {55/45, 60/40} | 2 | **0.653** (`hfea_ndx_tqqq_tmf_55_45`) ← T2-best | FIRES |
| **T2d** (iter 008) | No-decay-bond UPRO+ZROZ 60/40, UPRO+EDV 60/40 | 2 | 0.628 (`stack_upro_edv_60_40`) | FIRES |
| **T2e** (iter 009) | HFEA-trinity UPRO+TMF+UGL 50/30/20 | 1 | 0.600 | FIRES |
| **T2f** (iter 010) | T2-best with half-off variant | 1 | 0.633 (worse than T2c full-off) | FIRES |

Cumulative `n_trials = 393` (T1 22 + T1d 360 + T2 11).

---

## 2. T2 ranking (consolidated, by lh_56y Sharpe)

| Rank | Sub | Config | Sh lh_56y | Sh mod_1990 | CAGR | MDD | Tier |
|---:|----|--------|---:|---:|---:|---:|------|
| 1 | T2c | **`hfea_ndx_tqqq_tmf_55_45`** ✓ T2-best | **0.653** | 0.696 | 15.7% | -49.4% | MARGINAL |
| 2 | T2c | `hfea_ndx_tqqq_tmf_60_40` | 0.652 | 0.690 | 16.4% | -52.9% | MARGINAL |
| 3 | T2f | `hfea_ndx_tqqq_tmf_55_45_half_off` | 0.633 | — | 18.5% | -79.0% | NEAR_FAIL |
| 4 | T2d | `stack_upro_edv_60_40` | 0.628 | 0.593 | 10.9% | -58.5% | NEAR_FAIL |
| 5 | T2d | `stack_upro_zroz_60_40` | 0.610 | 0.598 | 11.1% | -59.3% | NEAR_FAIL |
| 6 | T2e | `hfea_trinity_upro_tmf_ugl_50_30_20` | 0.600 | 0.594 | 10.1% | -58.5% | MARGINAL |
| 7 | T2b | `hfea_70_30_full_off` | 0.583 | 0.563 | 11.7% | -66.6% | NEAR_FAIL |
| 8 | T2b | `hfea_65_35_full_off` | 0.580 | 0.564 | 11.3% | -64.2% | NEAR_FAIL |
| 9 | T2b | `hfea_60_40_full_off` | 0.572 | 0.561 | 10.8% | -61.7% | NEAR_FAIL |
| 10 | T2a | `hfea_55_45_half_off` | 0.571 | 0.506 | 14.6% | -79.6% | NEAR_FAIL |
| 11 | T2a | `hfea_55_45_full_off_bil` | 0.559 | 0.552 | 10.2% | -59.2% | NEAR_FAIL |

**Reference: T1c canonical winner `qld_sma200_off_zroz` Sharpe 0.752.**
**Anti-curve-fit threshold T1→T2 (spec §3.4): 0.802.**
**Distance T2-best to threshold: -0.149** (substantial, no realistic gap-closing).

---

## 3. Why HFEA underperforms T1c rotation in this universe

This is the **central finding of T2**, and it overturns the prior expectation
(strong hypothesis from T1d that T2d UPRO+ZROZ would win).

**The rotation vs. always-on contrast:**

- **T1c rotation** (qld_sma200_off_zroz): when QLD trending up, hold 100% QLD;
  when below SMA200, hold 100% ZROZ. Captures (a) equity upside during trends
  + (b) bond crisis-alpha during equity drawdowns.
- **HFEA** (always-on basket): always 55-70% UPRO + 30-45% TMF, with optional
  rotation of the *whole* basket to cash when signal=0. Captures (a) some
  equity upside + (b) some bond income, but eats LETF compounding decay
  through drawdowns when not rotated to cash.

**The numbers tell the story.** T1c qld_sma200_off_zroz CAGR 17.3% / MDD
-75.0% (rotation) vs T2d stack_upro_zroz_60_40 CAGR 11.1% / MDD -59.3%
(buy-hold-with-rotation): the HFEA-style basket has materially **lower**
CAGR. The basket bleeds through equity drawdowns in a way the rotation
doesn't, even with cash rotation gating the worst stretches.

**Why ZROZ helped in T1c but not T2d:**
- In T1c, ZROZ is held *only* during equity OFF (when SMA200 fires) — capturing
  ZROZ's positive crisis-alpha exactly when equity drawdowns happen
- In T2d, ZROZ is held *always* (60/40 stack), so it earns its base duration
  return ~5-7% CAGR but the UPRO compounding decay through 1986-2002 drags
  the basket below T1c's selective approach
- T1c times the duration exposure to crises; T2d holds duration through everything

**Why the equity-LETF-only rotation wins:**
- LETF compounding is convex on the way up, concave on the way down
- SMA200 rotation harvests the upside, gates much of the downside
- Adding bond-leveraged stack (TMF) brings bond-LETF tracking drag
  during 2022-style rate moves (`[leverage_for_the_long_run, p.21 Table 12]`)
- Adding bond-unleveraged stack (ZROZ/EDV) brings duration drag during
  rate-rising regimes (2022) without enough compensation
- Trinity (T2e adds UGL gold) adds the gold-LETF tracking-drag we calibrated
  in iter 000 v2

**Modern_1990 sanity:** T2c best still 0.696 in modern_1990 vs T1c canonical
0.695 (effectively equal). On the modern era, HFEA-NDX is competitive with
T1c on Sharpe but loses on CAGR (15.7% vs 23.4%) — the T1c QLD selection +
ZROZ as parking is more capital-efficient.

---

## 4. Sub-phase-level findings

### T2a: HFEA classic 55/45

UPRO+TMF 55/45 with full-off vs half-off:
- full-off: Sharpe 0.559, MDD -59.2%
- half-off: Sharpe 0.571, MDD -79.6% (better Sharpe via less-conservative
  exit, much worse drawdown — not free lunch)

Both well below T1c 0.752. The **canonical HFEA portfolio is strictly
worse than rotation** in this universe.

### T2b: weight sweep

UPRO+TMF at 60/40, 65/35, 70/30 (more equity-tilted than canonical 55/45):
- 70/30 best Sharpe 0.583
- Higher equity tilts modestly improve Sharpe (LETF-friendly trend regime)
  but stay well below T1c

### T2c: HFEA-NDX

TQQQ+TMF replaces UPRO+TMF — the **best T2 family**:
- 55/45 Sharpe 0.653 (T2-best overall)
- 60/40 Sharpe 0.652

Still 0.10 below T1c. Why TQQQ+TMF beats UPRO+TMF: NDX has higher
trend-friendly Sharpe than SPX in 1986-2026; combined with bond stack
gives marginal lift, but doesn't close the gap.

### T2d: no-decay-bond (the disappointment)

Strong-prior hypothesis from T1d was that ZROZ universal preference would
make T2d win. **It didn't.**
- UPRO+ZROZ 60/40 Sharpe 0.610
- UPRO+EDV 60/40 Sharpe 0.628

The lesson: ZROZ helps **when timed to equity OFF state** (T1c), not when
held continuously alongside equity LETF (T2d).

### T2e: HFEA-trinity

UPRO+TMF+UGL 50/30/20 — adding gold-LETF for diversification:
- Sharpe 0.600 (worst T2 family)
- UGL adds the calibrated gold-LETF tracking drag without enough
  diversification benefit; correlation with SPX is too low to help in
  drawdowns but high enough to drag during recoveries

### T2f: half-off explicit on T2-best

`hfea_ndx_tqqq_tmf_55_45_half_off` Sharpe 0.633 vs full-off equivalent
0.653: half-off is **worse**. Keeping TMF at full weight during equity
OFF means absorbing 2022 rate-collapse with 45% of capital. Full-off
to cash is structurally safer here.

---

## 5. Gates per top T2 configs

| Config | G1 PBO | G2 DSR p | G3 WF (win/n + maxMDD) | G4 OOS S | G5 FWD S | G6 99% low | tier |
|---|---:|---:|------|---:|---:|---:|------|
| `hfea_ndx_tqqq_tmf_55_45` | 0.560 | ~0.005 | 7/8 + 49% | ~0.95 | ~1.0 | ~0.32 | MARGINAL |
| `hfea_ndx_tqqq_tmf_60_40` | 0.560 | ~0.006 | 7/8 + 53% | ~0.95 | ~1.0 | ~0.31 | MARGINAL |

Top T2c configs **pass G3** (49% MDD < 50% threshold for 55/45 case) — the
NDX HFEA configuration sometimes clears the 50% MDD ceiling thanks to
TMF's positive contribution during 2008/2020 (TMF rallied like ZROZ in
those windows). This is interesting: **T2c is the only T2 config where
G3 walk-forward passes**, vs T1c which fails G3 (75% MDD).

Net: T2c HFEA-NDX is more **deploy-friendly** (lower MDD floor, G3 passes)
but lower-Sharpe than T1c rotation. A real efficient-frontier tradeoff.

---

## 6. Decision: KILL T1→T2 FIRES

Per spec §3.4:
> KILL T1→T2: T2-best Sharpe < T1-best + 0.05 → Basket adds no value.
> T3 inherits T1-best.

**T2-best `hfea_ndx_tqqq_tmf_55_45` Sharpe 0.653** vs **threshold 0.802**:
distance -0.149. KILL FIRES decisively.

**T3 inheritance fallback per spec §3.4:** T3 starts from `qld_sma200_off_zroz`
(T1c canonical incumbent, Sharpe 0.752). T2 contributes nothing to the
incumbent rank.

Tag for BASE_MEMORY: T2 = `KILL_T1_T2_FIRES`. Loop continues per spec; T2
is informational evidence that always-on basket structure does not help
single-LETF rotation in this universe.

---

## 7. Tier-level lessons (for T3-T5 design)

1. **Selectivity beats stacking** in the LETF universe. Any T3+ design
   should build on T1c's "equity LETF when ON, ZROZ when OFF" pattern,
   not on basket stacking.

2. **TMF is structurally weaker than ZROZ** as bond exposure — confirmed
   in T1c, T1d, AND now T2 (T2d ZROZ stack lost to T2c TMF stack but only
   because of the NDX vs SPX equity choice; if compared like-for-like
   UPRO+ZROZ vs UPRO+TMF, ZROZ wins). Future tiers should default to
   ZROZ as bond exposure.

3. **Half-off doesn't help** unless the bond sleeve has crisis-alpha *and*
   the OFF asset has positive carry. Both fail in current universe.

4. **HFEA-NDX (TQQQ-based) outperforms HFEA-SPX (UPRO-based)** in this
   window — relevant if T3 composite signals re-attempt basket structure.

5. **For T3 composite-signal design** (SMA + vol-gate, SMA + VIX, etc.):
   keep the "rotation between equity LETF and ZROZ" base; layer the
   composite signal on top of the SMA200 rotation, not on a basket.

---

## 7b. Cross-tier plots (in `reports/tier_2_plots/`)

| File | Content |
|---|---|
| `tier2_sharpe_bar_ranking.png` | All 11 T2 configs ranked horizontally by lh_56y Sharpe with reference lines for T1c (incumbent 0.752), threshold (0.802), SPY (0.682). Color-coded by tier band. |
| `tier2_t1c_vs_t2c_zoomed.png` | Head-to-head equity (log scale top) + drawdown (bottom) of T1c rotation vs T2c HFEA-NDX (T2-best) vs SPY. The clearest visual answer to "why does rotation beat the basket". |
| `tier2_equity_overlay.png` | Equity curves (log scale) — top 5 T2 configs + T1c + SPY across full lh_56y window. |
| `tier2_drawdown_overlay.png` | Peak-to-trough drawdown for the same configs. |
| `tier2_rolling_sharpe_overlay.png` | 5y rolling Sharpe (annualised) for the same configs. |

Per-iter SUMMARY.md + 7 plots also auto-generated in each
`runs/original/00{5..10}-*/` directory.

---

## 8. Methodology notes

- New module `studies/letf_rotation_hunt/runners/run_iter_t2.py` — basket dispatcher
  reusing T1's gates/scoring/artifacts pipeline. Differs only in strategy
  (calls `hfea_binary.build_positions` instead of single_letf_gayed).
- Existing `strategies/hfea_binary.py` and its tests (test_hfea_binary.py)
  unchanged — well-covered already from Phase 0 TDD.
- 11 configs across 6 sub-phases. Total runtime ~5 minutes wall-clock.
- All 11 generated `verdict.json`, `SUMMARY.md`, 7 plots, 2 CSVs per iter.

---

## 9. How to implement T2c HFEA-NDX in practice (tier winner — losing tier)

> **Caveat:** T2c (`hfea_ndx_tqqq_tmf_55_45`) is the T2 tier winner but
> **fails the KILL T1→T2 anti-curve-fit threshold** (Sharpe 0.653 << 0.802).
> The whole T2 family LOST to T1c rotation; basket structure does not add
> value in this universe. **Use T3d K=2** instead (study winner).
> Strategy is **DORMANT** per mandate §1; capital 100% Plan C.

### Tickers to trade (HFEA-NDX 55/45)

| Sleeve | Ticker | Type | Weight |
|---|---|---|---:|
| Equity | **TQQQ** | 3× NASDAQ-100 ETF (US) | 55% |
| Bond | **TMF** | 3× 20yr Treasury ETF (US) | 45% |

### Entry/exit logic

Every day at **market close**, compute on **QQQ**:
- **SMA200** = 200-day moving average

**Decision:**
- If `price_QQQ > SMA200` → portfolio = **55% TQQQ + 45% TMF** (full HFEA on)
- Otherwise → portfolio = **100% cash (BIL)** (full-off variant)

Rebalance at the close of the **NEXT** trading day (T+1) when the signal
flips; no internal re-balance between TQQQ and TMF (they drift until the
next flip).

### Trade frequency

- Compute: daily; flips ~5-8/year (same as T1c)
- TQQQ/TMF re-allocation is not incremental (only on flip)

### Expected costs

Higher than T1c due to the dual-LETF structure + higher TMF spread:

| Cost | Sharpe drag |
|---|---|
| Brazilian Lei 14.754 (15%) | -1.5 to -2.5pp |
| Slippage 5bp × 2 LETFs × ~5-8 flips/year | -0.10pp |
| TMF spread (3× leveraged bond) ~10-15bp | -0.10pp |
| LETF expense ratios (TQQQ 0.95% + TMF 1.06%) | -0.20pp internal drag |

**Estimated net Sharpe:** 0.40-0.50 (gross 0.653 - ~2.0-2.5pp drag).
**Net edge vs SPY:** below zero — **NOT recommended** for deploy.

### Why this is NOT the study winner (and shouldn't be implemented)

1. **T1c rotation > T2c basket** in Sharpe (0.752 vs 0.653). Core T2
   reason: ZROZ has **positional/temporal alpha** (T1c times the duration
   exposure to crises) — not carry alpha (T2 holds it always; bleeds
   during equity drawdowns).
2. **TMF tracking drag**: a 3× leveraged 20y bond LETF has prohibitive
   drag in rate-rising regimes (2022 duration collapse). Validates
   `[leverage_for_the_long_run, p.21 Table 12]`.
3. **T3d K=2 > T1c > T2c** — uses QLD (2× NDX) + ZROZ rotation with a
   4-signal vote. Sharpe 0.853, MDD 74.9% but pct_above_SPY 100%.

**Practical recommendation:** if you're considering implementing an HFEA-
style strategy, use **simple T1c rotation** (QLD/ZROZ + SMA200) instead
of the T2c basket; or, even better, **T3d K=2**, which adds +0.10 Sharpe
over T1c.

### Mandate alignment

DORMANT per mandate §1; capital 100% Plan C. The T2 family is educational
(why-rotation-beats-HFEA-in-LETF-universe) — not recommended for capital.

---

## 10. Citations

- Carlson HFEA basis: `[risk_parity, ch.5, p.10]` — capital-efficient
  stacking foundation
- LETF tracking drag for duration: `[leverage_for_the_long_run, p.21 Table 12]`
- Anti-curve-fit framework: spec §2.2, §3.4
- T2 inheritance fallback rule: spec §3.4 (KILL T<N>→T<N+1> fires →
  T<N+1>+1 inherits T<N>-best)
- Spec §7.5 honest expectation: T2 outcome (no advance over T1) was
  considered plausible (~MEDIUM probability) — basket complexity not
  guaranteed to add value over rotation simplicity

---

## Post-close addendum (2026-05-07)

Tier-2's full HFEA basket set was not re-run as a standalone Sortino study, so its internal ranking remains a historical Sharpe diagnostic. The family (led by `hfea_ndx_tqqq_tmf_55_45`, Sharpe 0.653 secondary) was eliminated by the KILL T1→T2 gate and did not feed into the T3-derived canonical that anchored the Sortino re-analysis. The post-close Sortino evaluation focused on the T3d K=2 descendant lineage. See `SORTINO_REANALYSIS_REPORT.md` §3–§4 for Sortino evaluation of the canonical and top-10 strategies from the tax_comparison sub-study.
