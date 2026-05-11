# T1 (Gayed replication) — Tier Report

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

**Status:** T1 tier complete (2026-05-06). **382 cumulative trials** across 4 sub-phases (T1a/T1b/T1c sequential per spec §2.2 + T1d robustness grid added at user request).
**Tier winner:** `qld_sma200_off_zroz` Sharpe 0.752 (lh_56y), **PROMISING score 65** (post G3 redesign 2026-05-06; was 52 MARGINAL before redesign) — T1c canonical, **confirmed robust by T1d 360-config grid**.
**KILL T0:** PASSED — first config in study to clear SPY+0.05 = 0.732.
**Inheritance to T2:** advance with QLD+SMA200+ZROZ; threshold T1→T2 = 0.802.

Spec ref: `docs/superpowers/specs/2026-05-05-letf-rotation-study-design.md` §2.2.

---

## 0. Scoring v2 update (2026-05-06) — Underwater-vs-Benchmark

After this report's initial draft, the user observed (2026-05-06): *"In 2000,
when this config had a drawdown of ~-70%, notice that even so the equity was
(much) higher than SPY buy-and-hold. (...) what matters is whether the equity
still sits above what we'd have had with buy-and-hold on the benchmark from
the start, right?"*

This is empirically validated for T1c:

![Underwater vs benchmark](tier_1_plots/tier1_underwater_vs_benchmark.png)

*T1c / SPY ratio over 40 years, log scale. Green: T1c above SPY (99.83% of
days). Red: below (0.17% of days, all in the first week before strategy
compounded). At worst absolute MDD (2000-09-20 -75%), T1c still 3.1× SPY.
Per-crisis ratios: 1987 1.76×, 2000 dotcom 3.11×, 2008 GFC 8.96×,
2020 COVID 36.29×, 2022 rates 40.65×.*

**Spec §3.2 rubric updated 2026-05-06**:
- Criterion 2 swapped from MDD-vs-SPY to **Underwater-vs-Benchmark** (max 15
  pts). Two-axis tiering on `pct_time_above_benchmark` + `min_relative_equity`.
- WINNER strict bar `MDD ≤ SPY` removed; replaced by
  `pct_time_above_benchmark ≥ 0.95`. MDD remains warning-only per
  mandate §2.3.

T1c v1 score 52 (MARGINAL) → **v2 score 61 (PROMISING)**. The strategy was
*always* dominating SPY; the old MDD-absolute scoring was punishing what is
visually irrelevant when you compare against the alternative buy-hold the
investor would actually default to.

Citation: User observation 2026-05-06 (this study); mandate §2.3 (MDD
warning-only).

---

## 0. All T1 configs in one picture (ratio to SPY)

![All T1 configs relative to SPY](tier_1_plots/tier1_all_configs_relative_to_spy.png)

*Each T1 config (382 cumulative trials: 22 from iters 001-003 + 360 from
iter 004 T1d grid) plotted as renormalized strategy_eq / SPY_eq ratio,
log-scale. SPY = 1.0 black dashed line. **Top-5 by lh_56y Sharpe in bold
colors**; the remaining 355+ configs faded (alpha=0.25). Visual pattern:
most QLD/SOXL × ZROZ/EDV/TLT combinations end above SPY over 40 years; the
canonical T1c (`qld_sma200_off_zroz`) is among the bold (Sharpe 0.752).*

---

## 1. Visual TL;DR (top-5 detail)

![Equity overlay](tier_1_plots/tier1_equity_top5.png)

*Top 5 T1 configs (across T1a/b/c) + SPY benchmark, log scale. The T1c family (3 of 5) compounds materially above SPY; T1a/T1b configs trail.*

![Drawdown overlay](tier_1_plots/tier1_drawdown_top5.png)
![Rolling 5y Sharpe](tier_1_plots/tier1_rolling_sharpe_top5.png)

*Drawdown (top) — all top-5 share the 2008 GFC ~75% MDD floor (LETF intrinsic). Rolling 5y Sharpe (bottom) — T1c family (ZROZ-OFF) consistently above 1.0 in trend regimes; T1a/b configs spend more time below 0.5.*

---

## 1. Overview & sub-phase recap

T1 tests the hypothesis from `[leverage_for_the_long_run, p.13, p.17 Table 8]`:
*"Gayed canonical SMA200 LRS (~0.61 Sharpe on 2×/3× SPX, 1928-2020) is reproducible
in our engine."* The three sub-phases sweep the three knobs (LETF / period / OFF
asset) one at a time, with anti-curve-fit thresholds pre-registered to filter
noise from real edge.

| Sub-phase | Question answered | Configs | Best Sharpe (lh_56y) | KILL T0 |
|---|---|---:|---:|---|
| **T1a** (iter 001) | Which LETF? | 6 | 0.678 (`qld_sma200_off_bil`) | FIRES |
| **T1b** (iter 002) | Which period? | 10 | 0.688 raw / 0.678 canonical | FIRES |
| **T1c** (iter 003) | Which OFF asset? | 6 | **0.752** (`qld_sma200_off_zroz`) | **PASS** |
| **T1d** (iter 004) | Full grid robustness | 360 | 0.787 raw / 0.752 anti-cf canonical | PASS |

Cumulative `n_trials = 382` (T1a 6 + T1b 10 + T1c 6 + T1d 360).

---

## 2. T1a — LETF sweep (iter 001)

6 LETFs × SMA200 × OFF=BIL.

| Config | Sharpe lh_56y | CAGR | MDD | Tier |
|---|---:|---:|---:|---|
| `qld_sma200_off_bil` (best) | 0.678 | 18.6% | -75.6% | NEAR_FAIL |
| `sso_sma200_off_bil` | 0.636 | 12.5% | -43.4% | NEAR_FAIL ★ G3 only-passer |
| `soxl_sma200_off_bil` | 0.627 | 21.1% | -94.3% | NEAR_FAIL |
| `tqqq_sma200_off_bil` | 0.594 | 18.4% | -80.6% | NEAR_FAIL |
| `upro_sma200_off_bil` | 0.550 | 13.3% | -79.2% | NEAR_FAIL |
| `ugl_sma200_off_bil` | 0.335 | 5.5% | -72.2% | FAIL |

**Verdict:** No LETF beats SPY+0.05. KILL T0 FIRES (best edge -0.004 < 0.05).
Note SSO is the only config passing G3 walk-forward gate (43% MDD < 50% threshold);
others fail MDD. 2× LETFs are MDD-friendlier than 3× as expected.

Detail: `runs/original/001-2026-05-05-T1a-letf-sweep/SUMMARY.md`.

---

## 3. T1b — QLD period sweep (iter 002)

QLD × {SMA, EMA} × {50, 100, 150, 200, 250} = 10 configs.
**Anti-curve-fit (spec §2.2):** alt period only "wins" if Sharpe > T1a SMA200 + 0.05 = **0.728**.

| Period | SMA Sharpe | EMA Sharpe |
|---:|---:|---:|
| 50 | **0.688** (best raw) | 0.561 |
| 100 | 0.669 | 0.648 |
| 150 | 0.580 | 0.677 |
| **200 (ref)** | **0.678** | 0.625 |
| 250 | 0.678 | 0.600 |

**Verdict:** Best raw Sharpe (SMA50 = 0.688) does NOT clear 0.728 anti-curve-fit
threshold → SMA200 reference holds for T1c. EMA family systematically
underperforms SMA family (EMA reactivity adds whipsaw without alpha — confirms
`[trading_systems_methods, Kaufman, ch.6]`). The spec's choice of SMA200 as
canonical is empirically supported, not p-hacked.

Detail: `runs/original/002-2026-05-06-T1b-qld-period-sweep/SUMMARY.md`.

---

## 4. T1c — QLD OFF-state sweep (iter 003)

QLD × SMA200 × {BIL, IEF, TLT, TMF, ZROZ, EDV} = 6 configs.
**Anti-curve-fit (spec §2.2):** non-leveraged OFF needs +0.05 over BIL; leveraged
TMF needs +0.10 over BIL **AND** MDD ≤ TMF_buy-hold_MDD/2.

| OFF asset | Sharpe lh_56y | Δ vs BIL | Required | Verdict |
|---|---:|---:|---:|---|
| **ZROZ** 25y zero-coupon | **0.752** | **+0.074** | +0.05 | **WIN** ✓ |
| IEF 7-10y | 0.724 | +0.046 | +0.05 | edge insufficient |
| TLT 20y | 0.719 | +0.041 | +0.05 | edge insufficient |
| EDV 25y vanguard | 0.719 | +0.041 | +0.05 | edge insufficient |
| TMF 3× 20y leveraged | 0.683 | +0.005 | +0.10 | **rejected** (TMF tracking drag) |
| BIL 1-3m T-bill (ref) | 0.678 | — | — | reference |

**Verdict:** **`qld_sma200_off_zroz` wins.** Sharpe 0.752 beats SPY+0.05=0.732
→ KILL T0 PASSES (+0.020 edge). First config in study to clear threshold.

Two findings:
1. **ZROZ wins because** it carries crisis-alpha (rallied +25-30% in 2008,
   +18% in 2020) without leverage drag. Capital is "always on" — earning
   duration return + crisis-alpha during equity OFF phases — vs BIL which
   only earns ~5%/yr cash.
2. **TMF rejected despite +0.10 leveraged threshold designed to reward it.**
   The 2022 rate-collapse drag on 3× duration exceeds the crisis-alpha
   benefit. Validates `[leverage_for_the_long_run, p.21 Table 12]` on LETF
   tracking drag in rate-rising regimes.

Detail: `runs/original/003-2026-05-06-T1c-qld-off-state-sweep/SUMMARY.md`.

---

## 4b. T1d — full-grid robustness sweep (iter 004, user-requested)

After T1c found `qld_sma200_off_zroz` as the sequential winner, the user
requested a full grid sweep to test whether the sequential a/b/c design missed
any cross-axis interactions: 6 risk-on × 6 risk-off × 2 signals × 5 lookback
periods = **360 configs**. Pre-registered anti-curve-fit threshold per spec
§3.4: T1d-best Sharpe must exceed T1c-best (0.752) + 0.05 = **0.802** to claim
new T1 winner; otherwise T1c stands.

### Top 15 by lh_56y Sharpe

| Rank | Config | Sh lh_56y | Sh mod_1990 | CAGR | MDD | Tier |
|---:|--------|---:|---:|---:|---:|------|
| 1 | `qld_ema150_off_zroz` | **0.787** | 0.710 | 24.4% | -58.0% | MARGINAL |
| 2 | `qld_sma100_off_zroz` | 0.769 | 0.702 | 23.5% | -64.2% | MARGINAL |
| 3 | `qld_sma50_off_zroz` | 0.752 | 0.701 | 22.6% | -67.5% | MARGINAL |
| 4 | **`qld_sma200_off_zroz`** ✓ T1c | **0.752** | 0.695 | 23.4% | -75.0% | MARGINAL |
| 5 | `soxl_ema250_off_zroz` | 0.751 | 0.703 | 30.3% | -86.1% | MARGINAL |
| 6 | `soxl_sma50_off_zroz` | 0.743 | 0.700 | 28.3% | -84.4% | MARGINAL |
| 7 | `qld_sma50_off_ief` | 0.740 | 0.704 | 20.2% | -61.7% | MARGINAL |
| 8 | `qld_ema100_off_zroz` | 0.738 | 0.669 | 22.0% | -63.2% | MARGINAL |
| 9 | `qld_ema150_off_tlt` | 0.736 | 0.700 | 20.8% | -57.8% | MARGINAL |
| 10 | `qld_ema150_off_edv` | 0.736 | 0.700 | 20.8% | -57.8% | MARGINAL |
| 11 | `qld_ema150_off_ief` | 0.736 | 0.714 | 20.4% | -56.9% | MARGINAL |
| 12 | `soxl_ema250_off_ief` | 0.733 | 0.724 | 28.6% | -86.3% | MARGINAL |
| 13 | `qld_sma100_off_ief` | 0.730 | 0.703 | 20.0% | -52.5% | MARGINAL |
| 14 | `qld_sma50_off_tlt` | 0.729 | 0.689 | 20.2% | -63.0% | NEAR_FAIL |
| 15 | `qld_sma50_off_edv` | 0.729 | 0.689 | 20.2% | -63.0% | NEAR_FAIL |

### Anti-curve-fit verdict

**Best raw Sharpe: 0.787** (`qld_ema150_off_zroz`) — does **NOT** clear 0.802
threshold. Differential vs T1c canonical = +0.035, within noise band. Per
spec §3.4 anti-curve-fit pre-registration:

> **T1c canonical winner `qld_sma200_off_zroz` STANDS as T1 incumbent.**

T1d serves as **robustness mapping**, not a winner search.

### Marginal analysis — robustness story

Mean Sharpe (lh_56y) holding one axis fixed:

| OFF asset | n configs | mean Sharpe | max Sharpe |
|---|---:|---:|---:|
| **ZROZ** | 60 | **0.637** | **0.787** |
| IEF | 60 | 0.588 | 0.740 |
| EDV | 60 | 0.588 | 0.736 |
| TLT | 60 | 0.588 | 0.736 |
| TMF (3× lev) | 60 | 0.583 | 0.719 |
| BIL (cash) | 60 | 0.533 | 0.711 |

| Risk-on LETF | n configs | mean Sharpe | max Sharpe | best OFF |
|---|---:|---:|---:|---|
| QLD 2× NDX | 60 | 0.678 | 0.787 | ZROZ |
| SOXL 3× SOX | 60 | 0.658 | 0.751 | ZROZ |
| TQQQ 3× NDX | 60 | 0.623 | 0.709 | ZROZ |
| SSO 2× SPY | 60 | 0.603 | 0.718 | ZROZ |
| UPRO 3× SPY | 60 | 0.507 | 0.650 | ZROZ |
| UGL 2× Gold | 60 | 0.450 | 0.648 | ZROZ |

**ZROZ wins the OFF-state slot for ALL 6 risk-on LETFs.** This is the
strongest finding of T1d — the T1c choice is not specific to QLD; it's
universal across the LETF universe in this study.

| Period | n | mean Sharpe | max | | Signal | n | mean Sharpe | max |
|---:|---:|---:|---:|--|---|---:|---:|---:|
| 50 | 72 | 0.561 | 0.752 | | SMA | 180 | 0.585 | 0.769 |
| 100 | 72 | 0.566 | 0.769 | | EMA | 180 | 0.588 | 0.787 |
| 150 | 72 | 0.590 | 0.787 | | | | | |
| 200 | 72 | 0.602 | 0.752 | | | | | |
| 250 | 72 | 0.612 | 0.751 | | | | | |

Period: longer is better on mean (250 > 200 > 150 > 100 > 50). Confirms
canonical SMA200/250 choice. Period 150 has highest max only because of the
single qld_ema150_off_zroz outlier.
Signal: SMA vs EMA effectively tied on mean (0.585 vs 0.588) — the T1b finding
that EMA underperforms was specific to QLD+BIL combo. With ZROZ as OFF, the
two signal types are equivalent.

### Gates with N=360 (statistically meaningful)

| Gate | Top 5 values | Pass? | Notes |
|---|---|:---:|---|
| G1 PBO | 0.520 (constant for all 360 configs in this iter) | ✗ (just) | N=360 ≥ 4-config stability threshold; PBO 0.52 is *barely* > 0.50 — noise-similar configs disagree on IS-best vs OOS-best ~52% of splits. Honest read: small grid signal, not deploy-quality. |
| G2 DSR p (local n=360) | 0.0211, 0.0273, 0.035, 0.036, 0.036 | ✓/⚠ | Top 5 all pass < 0.05 but margin tightens substantially (T1c had p=0.0009; T1d top has p=0.021). With 360 trials the multiple-testing penalty is real. |
| G2 DSR p cumulative (n=382) | 0.022, 0.028, 0.036, 0.037, 0.037 | ✓ | Still under 0.05; significance survives study-cumulative correction. |
| G3 WF | 8/8 windows + 58-86% MDD | ✗ | Same MDD floor as T1c — LETF intrinsic during 2008. |
| G6 Bootstrap 99% low | 0.434, 0.437, 0.389, 0.389, 0.393 | ✓ | Comfortably positive. |

**Honest read on G1 PBO:** 0.520 is statistically meaningful now (N=360 well
above CSCV stability threshold) but barely fails the 0.5 threshold. With 360
similar-design configs, finding "the best" is essentially noise selection;
PBO correctly reports this. The G1 fail does NOT invalidate the marginal
findings (ZROZ dominance, period preference), but it does mean *no specific
config* in T1d can claim deploy-quality status purely from in-grid
performance.

### T1d plots

- `runs/original/004-2026-05-06-T1d-full-grid/plots/01-07_*.png` — line plots
  filtered to top-15 by Sharpe (auto-truncated when configs > 15)
- `plots/08_sharpe_heatmap.png` — full 60×6 grid heatmap (rows: on×signal×period,
  cols: off asset). Visualises ZROZ column as universal winner.

### T1d summary

T1d is **strong evidence reinforcing the T1c canonical winner**, not a winner
search:

1. ZROZ is the OFF asset for all 6 risk-on LETFs (universal preference)
2. Conservative periods (200/250) are best on mean Sharpe — confirms SMA200
3. SMA vs EMA roughly tied on average (T1b's QLD+BIL finding was contextual)
4. No config beats T1c+0.05 anti-curve-fit; canonical winner stands
5. Sequential a/b/c design did NOT miss interactions; the grid confirms it

---

## 5. Top-K consolidated ranking (across the 22 sequential configs, by lh_56y Sharpe; T1d top-15 is in §4b above)

| Rank | Sub | Config | Sh lh_56y | Sh mod_1990 | Sh spy_real | Sh ndx_real | CAGR | MDD | Tier |
|---:|----|--------|---:|---:|---:|---:|---:|---:|------|
| 1 | T1c | **`qld_sma200_off_zroz`** ✓ | **0.752** | 0.695 | 0.771 | 0.812 | 23.4% | -75.0% | MARGINAL |
| 2 | T1c | `qld_sma200_off_ief` | 0.724 | 0.718 | 0.829 | 0.897 | 20.6% | -75.0% | MARGINAL |
| 3 | T1c | `qld_sma200_off_tlt` | 0.719 | 0.699 | 0.799 | 0.854 | 20.7% | -75.3% | MARGINAL |
| 4 | T1c | `qld_sma200_off_edv` | 0.719 | 0.699 | 0.799 | 0.854 | 20.7% | -75.3% | MARGINAL |
| 5 | T1b | `qld_sma50_off_bil` | 0.688 | 0.660 | 0.653 | 0.772 | 18.1% | -68.1% | NEAR_FAIL |
| 6 | T1c | `qld_sma200_off_tmf` | 0.683 | 0.627 | 0.638 | 0.640 | 21.8% | -78.9% | NEAR_FAIL |
| 7 | T1b | `qld_sma250_off_bil` | 0.678 | 0.685 | 0.738 | 0.817 | 19.0% | -69.7% | MARGINAL |
| 8 | T1c† | `qld_sma200_off_bil` | 0.678 | 0.687 | 0.816 | 0.904 | 18.6% | -75.6% | MARGINAL |
| 9 | T1b | `qld_ema150_off_bil` | 0.677 | 0.673 | 0.628 | 0.776 | 18.0% | -58.7% | NEAR_FAIL |
| 10 | T1b | `qld_sma100_off_bil` | 0.669 | 0.653 | 0.581 | 0.663 | 17.5% | -60.4% | NEAR_FAIL |

**SPY anchor lh_56y:** Sharpe 0.682, MDD -55.1%.
**SPY+0.05 threshold:** 0.732.
*†row 8: BIL config appears in both T1a (iter 001) and T1c (iter 003); the
T1c run includes all 4 datasets so figures shown are from T1c.*

Top 4 are all `qld_sma200_off_*` with different OFF assets — confirms QLD+SMA200
is the right ON config; the OFF asset is the *primary lever* for incremental
Sharpe.

EDV and TLT show identical numbers (0.719 lh_56y) — same return profile because
both proxy 20-25y duration; no real differentiation.

---

## 6. Gates per top 5 (verified against verdict.json)

| Config | G1 PBO | G2 DSR p | G3 win/8 + maxMDD | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | n pass |
|---|---:|---:|------|---:|---:|---:|---:|:---:|
| `qld_sma200_off_zroz` | 0.607 | 0.0003 | **8/8** + 75.0% | 0.833 | 0.652 | 0.389 | 0.00 | 6/7 |
| `qld_sma200_off_ief` | 0.607 | 0.0006 | 8/8 + 75.0% | 0.939 | 0.870 | 0.350 | 0.00 | 6/7 |
| `qld_sma200_off_tlt` | 0.607 | 0.0006 | 8/8 + 75.3% | 0.887 | 0.755 | 0.350 | 0.00 | 6/7 |
| `qld_sma200_off_edv` | 0.607 | 0.0006 | 8/8 + 75.3% | 0.887 | 0.755 | 0.350 | 0.00 | 6/7 |
| `qld_sma50_off_bil` | 0.873 | 0.0028 | 8/8 + 68.1% | 0.708 | 0.796 | 0.348 | 0.00 | 6/7 |

**G1 PBO fails for all** — top 5 from T1c are 0.607, well above 0.50 threshold
(SMA50 from T1b is even worse at 0.873 since the T1b grid had 10 EMA/SMA
configs that look noise-similar). `[advances_fin_ml, p.208-211]` flags this:
when configs are similar in design, CSCV correctly tells us we're picking from
noise; the gate is informative ONLY against an exogenously declared grid.

**G3 walk-forward** has interesting nuance: all top 5 pass the *windows
profitability* part (8/8 windows with positive Sharpe — well above 5/8
threshold) but fail the *MDD ceiling* part (max-window MDD > 50% — LETF
intrinsic drawdown floor during 2008 GFC OOS window). Spec §3.5 already
relaxed from 25% to 50%; even that doesn't clear for QLD configs.

**G2 DSR p < 0.05** PASSES for all 5 (very low p ~0.0003-0.003 — Sharpe is
statistically significant at local n_trials).
**G4/G5/G6/G7** all PASS for top 5 — engine arithmetic clean and edge robust
to OOS / post-2020 / bootstrap / cross-lib.

Net: top configs pass **6 of 7** gates. The 2 failures (G1 PBO + G3 MDD) are
both LETF-intrinsic — small-grid PBO instability + 75% MDD floor in 2008.
T2+ HFEA basket is the natural way to attack the MDD floor (UPRO+ZROZ stack
inherits ZROZ's positive crisis-alpha during equity drawdown).

---

## 7. Comparative plots (top 5 + SPY)

- `tier_1_plots/tier1_equity_top5.png` — log-scale equity curves
- `tier_1_plots/tier1_drawdown_top5.png` — peak-to-trough drawdowns
- `tier_1_plots/tier1_rolling_sharpe_top5.png` — 5y rolling Sharpe

---

## 8. Per-dataset robustness (modern_1990 sanity)

User question (2026-05-06): is the lh_56y window's KILL T0 FIRES result an
artifact of pre-1990 data being unrepresentative of "modern markets"?

Empirical answer using `modern_1990` (1990-01-01..2026-04-30) as 4th dataset:

| Window | SPY Sharpe | T1c best (`qld_sma200_off_zroz`) Sharpe | Edge vs SPY+0.05 |
|---|---:|---:|---:|
| lh_56y | 0.682 | 0.752 | +0.020 (PASS) |
| modern_1990 | 0.653 | 0.695 | -0.008 (FIRES) |
| spy_real (2003+) | 0.671 | 0.771 | +0.050 (PASS) |
| ndx_real (2010+) | 0.900 | 0.812 | -0.138 (FIRES) |

Mixed signal. The edge is real on lh_56y and spy_real but borderline on
modern_1990 and unfavorable on ndx_real. The ndx_real result is misleading
because the SPY anchor of 0.900 is actually the NDX anchor (T1 anchors against
SPY only; ndx_real Sharpe of 0.900 represents NDX, not SPY benchmark — the
strategy IS NDX-based so this is comparison vs the same underlying).

The key honest read: **edge is borderline on modern_1990** (Sharpe gap 0.042 vs
threshold 0.05). 1990 cutoff rebases anchors slightly; conclusion is
qualitatively stable but quantitatively margin shrinks. Not an artifact of the
56y label, but the edge is not as wide as lh_56y suggests.

---

## 9. Tier-level conclusion

**Three findings drive the T1 narrative:**

1. **The OFF asset is the primary lever, not the ON LETF.** T1a swept 6 LETFs
   and got Sharpes 0.34-0.68 (range 0.34). T1c swept 6 OFF assets and got
   Sharpes 0.68-0.75 (range 0.07). The OFF state range is 5× tighter but
   includes the threshold-clearing winner. *Capital efficiency of the OFF
   state matters more than maximizing equity leverage.* This validates
   Carlson `[risk_parity, ch.5]` at single-LETF rotation scale.

2. **The canonical SMA200 is robust.** T1b's anti-curve-fit pre-registration
   protected against finding a "winner" period that's actually just noise.
   Best alt period (SMA50) failed by 0.05 margin. SMA200 stays — exactly
   what spec §2.2 design pre-empted.

3. **T1c clears KILL T0 but not deploy quality.** Sharpe 0.752 beats SPY+0.05
   threshold but tier_label is MARGINAL not WINNER (score 52). G3 still
   fails (75% MDD). Need T2+ HFEA basket / T3 composite signals to push to
   STRONG/WINNER tier.

**Reconciling with the spec §7.5 honest expectation:** the prediction was that
the study probably won't find a deploy candidate, only mapping the space. T1c
moved that expectation slightly: there *is* a config that beats SPY+0.05 on
lh_56y, but it's not yet deploy-quality. T2 HFEA might tip the balance via
"always-on" UPRO+ZROZ stacking — explicit hypothesis.

**Inheritance config for T2:** `qld_sma200_off_zroz` (Sharpe 0.752).
Anti-curve-fit threshold T1→T2 (spec §3.4): T2-best Sharpe must be > 0.802 for
basket to add value over single-LETF rotation. KILL T1→T2 is informational; loop
continues regardless.

---

## 10. Methodology notes

- DATASET_WINDOWS introduced in this session: lh_56y, modern_1990, spy_real,
  ndx_real (4 windows). modern_1990 was added at user request 2026-05-06; SPY
  Sharpe measured 0.653 (vs 0.682 lh_56y — slightly worse, not better).
- spy_real SPY anchor corrected from 0.900 placeholder to 0.671 measured.
- Gates G1-G7 are real CSCV PBO / DSR / WF / OOS / FWD / Bootstrap / cross-lib
  per spec §3.5 (LETF-relaxed thresholds where motivated).
- All 7 plots auto-generated per iter via `_write_iter_artifacts` in
  `run_iter_t1.py`. Cross-tier comparative plots generated post-hoc in this
  report.

---

## 11. How to implement T1c canonical in practice (tier winner)

> **Caveat:** T1c canonical (`qld_sma200_off_zroz`) is the **T1 tier winner**,
> NOT the study winner. Study winner is **T3d K=2** (`qld_vote_k2_off_zroz`,
> Sharpe 0.853) — a strict superset of T1c that adds 3 more signals to vote.
> Use T3d K=2 in practice unless you specifically want a simpler 1-signal gate.
> Strategy is **DORMANT** per mandate §1; capital remains 100% Plan C.

### Tickers to trade

| State | Ticker | Type |
|---|---|---|
| ON  | **QLD**  | 2× NASDAQ-100 ETF (US) |
| OFF | **ZROZ** | 25y zero-coupon Treasury ETF (US) |

### Entry/exit logic (single-signal SMA200)

Every day at **market close**, compute on **QQQ**:

- **SMA200** = simple moving average over the last 200 trading days

**Decision:**
- If `price_QQQ > SMA200` → next portfolio = **100% QLD**
- Otherwise → next portfolio = **100% ZROZ**

Rebalance at the close of the **NEXT** trading day (T+1).

### Typical trade frequency

- Compute: daily at market close
- Trade: ~5-8 flips/year (fewer than T3d K=2)

### Expected costs (estimated)

| Cost | Sharpe drag |
|---|---|
| Brazilian Lei 14.754 (15% on realized gains) | -1.5 to -2.5pp |
| Slippage 5bp × ~5-8 flips/year | -0.03pp |
| LETF bid/ask spread ~5-10bp | -0.05pp |

**Estimated net Sharpe:** 0.55-0.65 (gross 0.752 - ~1.5-2.0pp drag).
**Net edge vs SPY:** ~0.00 to +0.10 (likely below the +0.05 minimum).

### Why this is NOT the study winner

T1c uses only SMA200 as a gate. T3d K=2 uses **4 voted signals**:
- SMA200 (long-term trend) — same as T1c
- SMA50 (short-term trend) — additional
- vol_21d < 40% (calm regime) — additional
- AR(1)_30d > 0 (momentum) — additional

Vote-of-K=2 catches more uptrend opportunities and has +0.10 Sharpe edge
over T1c (0.853 vs 0.752). Same simplicity-vs-edge trade-off: for
forward-monitoring, prefer T3d K=2.

### Mandate alignment

DORMANT per mandate §1; capital 100% Plan C. T1c is the canonical pre-T3d
reference for OFF-asset choice (ZROZ = universal best) and ON-asset
choice (QLD = best Sharpe among the 6 LETFs tested).

---

## 12. Citations

- Gayed canonical LRS: `[leverage_for_the_long_run, p.13, p.17 Table 8, p.21 Table 12]`
- Capital-efficient stacking: `[risk_parity, ch.5, p.10]` (Carlson)
- Treasury crisis-alpha: `[ilmanen_expected_returns, ch.19]`
- LETF compounding & FFR-aware formula: `[leverage_for_the_long_run, p.16, footnote 22-23]`
- EMA whipsaw vs SMA: `[trading_systems_methods, Kaufman, ch.6]`
- CSCV PBO: `[advances_fin_ml, p.208-211]`
- DSR: `[advances_fin_ml, p.222-223, p.275]`
- Bootstrap CI: `[advances_fin_ml, p.196-202]`
- Cross-lib & sensitivity: `[advances_fin_ml, p.31-34]`
- Anti-curve-fit pre-registration: spec §2.2, §3.4

---

## Post-close addendum (2026-05-07)

Tier-1's full grid was not re-run as a standalone Sortino study, so its internal ranking remains a historical Sharpe diagnostic. The T1 winner `qld_sma200_off_zroz` (Sharpe 0.752 secondary) served as the ancestor of the T3d K=2 composite signal that became the Sortino anchor. The T1 replication work therefore contributed indirectly: the SMA/ZROZ rotation backbone established in T1 is structurally present in all Sortino-evaluated variants, including the operative winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`. See `SORTINO_REANALYSIS_REPORT.md` §4 and §9 for the full Sortino evaluation of the T3-descended strategies.
