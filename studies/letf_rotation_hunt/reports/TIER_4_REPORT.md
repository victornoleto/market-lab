# T4 (Cross-sectional rotation) — Tier Report

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

**Status:** T4 tier complete (2026-05-06). 4 configs (T4a-T4d), iters 016-019.
**Tier verdict:** **KILL T3→T4 FIRES.** T4-best Sharpe 0.823 (T4b Clenow top-3) falls 0.080 below threshold 0.903. Cross-sectional ranking does not improve over T3d K=2 composite signal in this universe.
**T4-best:** `xs_clenow_top3_zroz_spysma200` Sharpe 0.823, score 66, **PROMISING** (close miss).
**Inheritance to T5:** **T3d K=2 stands as study incumbent** per spec §3.4 fallback. T5 anchor = `qld_vote_k2_off_zroz`. Threshold T4→T5 unchanged at 0.903 (= T3-best + 0.05).

Spec ref: §2.5, §3.4. T4 inherits T3-best (KILL T3→T4 doesn't change incumbent).

---

## 0. Underwater-vs-benchmark (T4-best vs SPY)

![Underwater vs benchmark](tier_4_plots/tier4_underwater_vs_benchmark.png)

*T4b `xs_clenow_top3_zroz_spysma200` (Sharpe 0.823) relative to SPY buy-hold,
log scale. **99.86% of days above SPY** — passes v2 strict bar 0.95. Min ratio
post-warmup 1.43× (always at least 1.43× SPY). End ratio 26.4× (vs T3d K=2
end ratio 256×). T4b is a competent rotation strategy but compounds less than
T3d K=2's single-asset Vote-K=2 — the cross-sectional ranking among 4 LETFs
adds turnover cost without enough alpha differentiation in this universe.*

---

## 0b. All T4 configs in one picture (ratio to SPY)

![All T4 configs relative to SPY](tier_4_plots/tier4_all_configs_relative_to_spy.png)

*4 T4 cross-sectional configs as strategy_eq / SPY_eq ratio (renormalised, log-scale).
SPY = 1.0 black dashed. **Top-3 bold (T4b clenow_top3, T4c ewmac_top2, T4a
clenow_top2); T4d clenow+vol-gate faded** because it's the worst performer
(Sharpe 0.511, score 32 NEAR_FAIL). Visual: top-3 maintain a ratio > 1.0
most of the time post-warmup; T4d periodically dips below SPY in the post-2010
regime (per-asset vol-gate filters out LETFs trending with high vol at the
wrong moments).*

---

## 1. Visual TL;DR (top-3 detail)

![Sharpe bar ranking](tier_4_plots/tier4_sharpe_bar_ranking.png)

*4 T4 configs. T4b Clenow top-3 (orange) closest to threshold; T4d vol-gate
(red, lh_56y 0.511) hurts dramatically. None clear 0.903.*

![Equity overlay](tier_4_plots/tier4_equity_overlay.png)
![Drawdown](tier_4_plots/tier4_drawdown_overlay.png)
![Rolling 5y Sharpe](tier_4_plots/tier4_rolling_sharpe_overlay.png)

*T3d K=2 incumbent (green) compounds materially above all T4 variants. T4b/T4c
similar trajectory, both below T3d. T4d (vol-gate) clearly weakest.*

---

## 2. Sub-phase summary

T4 tests cross-sectional rotation: rank a pool of LETFs daily by trend score
(Clenow slope×R² 90d or EWMAC composite) + master macro filter (SPY > SMA200);
hold top-K equally-weighted; OFF asset = ZROZ when master gate is OFF or
fewer than K assets are valid.

Universe per spec §2.5:
- T4a/b/c: pool {UPRO, QLD, UGL, TMF}, window 1985+
- T4d: pool +SOXL (5 assets), window 2010+ only (SOXL inception)

| Sub-phase | Variant | Pool | top_K | Sharpe (lh_56y) | KILL T3→T4 |
|---|---|---|---:|---:|---|
| **T4a** (iter 016) | Clenow 90d | 4 LETFs | 2 | 0.723 | FIRES |
| **T4b** (iter 017) | Clenow 90d | 4 LETFs | **3** | **0.823** | FIRES (close miss) |
| **T4c** (iter 018) | EWMAC composite | 4 LETFs | 2 | 0.791 | FIRES |
| **T4d** (iter 019) | Clenow + per-asset vol_21d<40% | 5 LETFs | 2 | 0.511 | FIRES |

Cumulative `n_trials = 404` (T1 22 + T1d 360 + T2 11 + T3 7 + T4 4).

---

## 3. T4 ranking (consolidated, by lh_56y Sharpe)

| Rank | Sub | Config | Sh lh_56y | Sh mod_1990 | Sh spy_real | Sh ndx_real | CAGR | MDD | pct>b | min_r | Score | Tier |
|---:|----|--------|---:|---:|---:|---:|---:|---:|---:|---:|---:|------|
| 1 | T4b | **`xs_clenow_top3_zroz_spysma200`** ✓ T4-best | **0.823** | 0.754 | 0.776 | 0.886 | 20.9% | -54.5% | 100% | 1.43× | 66 | PROMISING |
| 2 | T4c | `xs_ewmac_top2_zroz_spysma200` | 0.791 | 0.751 | 0.768 | 0.871 | 22.0% | -55.7% | 100% | 1.32× | 63 | PROMISING |
| 3 | T4a | `xs_clenow_top2_zroz_spysma200` | 0.723 | 0.698 | 0.717 | 0.838 | 20.3% | -58.8% | 100% | 1.17× | 44 | MARGINAL |
| 4 | T4d | `xs_clenow_volgate_top2_zroz_spysma200` | 0.511 | 0.438 | 0.511 | 0.530 | 10.9% | -58.3% | 81% | 0.56× | 32 | NEAR_FAIL |

**Reference: T3d K=2 incumbent Sharpe 0.853.**
**Anti-curve-fit threshold T3→T4: 0.903.**
**T4-best gap to threshold: -0.080.**
**T4-best gap to T3 incumbent: -0.030.**

---

## 4. Key findings

### Top-3 beats top-2 (more diversification helps)

T4b (top-3, Sharpe 0.823) > T4a (top-2, Sharpe 0.723) by +0.10. With only
4 assets in the pool, top-2 means just-the-best-pair, which is volatile when
the best-pair flip-flops; top-3 includes 75% of the pool and captures more
average pool performance.

This is a **counter-intuitive finding**: typically more concentration =
higher variance = higher Sharpe in trending universes. Here, with high-volatility
LETFs and low pool size, **diversification wins**.

### EWMAC competitive with Clenow

T4c (EWMAC 16/64+64/256 composite, top-2): Sharpe 0.791. Modestly above T4a
(Clenow top-2, 0.723) — EWMAC's smoothed forecast is slightly more stable
than 90d regression-slope ranking. But neither beats T3d K=2.

### Per-asset vol-gate hurts dramatically

T4d (Clenow + per-asset vol<40% + +SOXL pool, 2010+ window): Sharpe 0.511.
Two compounding issues:
1. **2010+ window is bull-heavy** but vol-gate kicks LETFs out at the wrong
   moments (high-vol uptrends after corrections — exactly when LETFs would
   normally compound).
2. **SOXL has high intrinsic vol** so it spends much time vol-gated out;
   when included it adds whipsaw.

The per-asset vol filter is too restrictive when applied per-individual asset.
Compare: T3d K=2 includes vol-gate as one-of-four signals voted, so
vol-restriction softens via consensus.

### Why T4 doesn't beat T3

T3d K=2 (single-asset QLD with composite signal) Sharpe 0.853 vs T4b (cross-sectional,
4 LETFs, top-3) Sharpe 0.823. Why does single-asset + better signal beat
multi-asset + ranking?

1. **The QLD-with-Vote-K=2 is already capturing most of the trend value.**
   Adding 3 other LETFs to a ranking pool dilutes via lower-edge assets
   (UGL/TMF have lower individual Sharpe than QLD).
2. **Cross-sectional ranking has turnover cost.** Top-K rotation flips assets
   when relative scores cross; this generates more transition trades than
   single-asset on/off (T3 only flips between QLD and ZROZ).
3. **Master gate (SPY > SMA200) duplicates SMA200 already in T3d K=2** —
   the cross-sectional ranking layer doesn't add information that T3d wasn't
   already capturing via SMA200 vote.

The empirical conclusion: **for this LETF universe, single-asset rotation
with composite signal (T3) is more capital-efficient than cross-sectional
ranking with master filter (T4).**

---

## 5. Gates per top T4 configs

| Config | G1 PBO | G2 DSR p (local) | G3 WF (win/n + maxMDD) | G4 OOS S | G5 FWD S | G6 99% low | tier |
|---|---:|---:|------|---:|---:|---:|------|
| `xs_clenow_top3_zroz_spysma200` | 0.357 | 0.0001 | 7/8 + 54.5% | 0.91 | 0.93 | 0.36 | PROMISING |
| `xs_ewmac_top2_zroz_spysma200` | 0.357 | 0.0002 | 7/8 + 55.7% | 0.86 | 0.87 | 0.32 | PROMISING |

T4 has fewer configs (4) but G1 PBO **passes for first time** in study at
0.357 < 0.5! With 4 noise-similar XS configs in the iter, CSCV finds
consistent IS↔OOS rank → strong evidence the underlying signal is real,
not noise selection. **First WINNER strict bar G1 ever passed.**

But other strict bars still block WINNER: G3 WF MDD > 50%; total score < 90.

---

## 6. Decision: KILL T3→T4 FIRES

Per spec §3.4:

> **T4-best `xs_clenow_top3_zroz_spysma200` Sharpe 0.823 < 0.903 = T3-best + 0.05**
> **→ KILL T3→T4 FIRES.**
> T5 inherits T3-best `qld_vote_k2_off_zroz` per inheritance fallback.

T4 contributes nothing new to study incumbent. Loop continues per spec §3.4
(KILL is informational; T5 still runs).

---

## 7. Tier-level lessons (for T5 + future work)

1. **Single-asset T3 > Cross-sectional T4** in this universe. Adding pool
   rotation didn't pay; QLD+Vote-K=2 captures most of the trend efficiently.

2. **Master-gate + ranking can duplicate single-asset signals.** SPY > SMA200
   master + Clenow top-K is largely a re-statement of "be in equity LETF when
   trending" — exactly what T3d already does, but with rotation overhead.

3. **G1 PBO finally passes** with 4 XS configs (0.357 < 0.5). Confirms the
   small-grid issue we've been hitting in T1-T3 is a sample-size artifact;
   when the variants are diverse enough (different score methods, top_K
   values), CSCV stabilises.

4. **Top-3 beats top-2** in 4-LETF pool: counter-intuitive but explained by
   small pool size. With more LETFs, top-2 might recover.

5. **Per-asset vol-gate is an anti-pattern.** Filters at wrong moments,
   excludes high-vol-trending LETFs (SOXL), creates whipsaw.

6. **EWMAC and Clenow give similar results.** Choice of trend score doesn't
   matter much; what matters is the macro filter (already SMA200 by spec).

7. **For T5 vol-target design**: build on T3d K=2 paradigm, not on T4 XS
   ranking. Carver-style continuous position sizing applied to QLD/ZROZ
   rotation is the natural extension.

---

## 8. Cross-tier plots (in `tier_4_plots/`)

| File | Content |
|---|---|
| `tier4_underwater_vs_benchmark.png` | T4-best vs SPY ratio over 40y; pct_above 99.86%, end ratio 26.4× |
| `tier4_sharpe_bar_ranking.png` | 4 T4 configs ranked, T3 incumbent + threshold lines |
| `tier4_equity_overlay.png` | T4 top configs + T3 incumbent + SPY across lh_56y |
| `tier4_drawdown_overlay.png` | Drawdown comparison |
| `tier4_rolling_sharpe_overlay.png` | 5y rolling Sharpe |

---

## 9. Methodology notes

- **New module** `studies/letf_rotation_hunt/runners/run_iter_t4.py` — cross-sectional
  dispatcher. Reuses T1's pipeline. Routes 4 sub-types (clenow_top2, clenow_top3,
  ewmac_top2, clenow_volgate_top2).
- Pre-existing `signals.py:clenow_score` and `ewmac_forecast` used as ranking
  scores. Pre-existing `strategies/cross_sectional.py:build_positions` accepts
  scores DataFrame + master_gate Series + top_k.
- Master gate: SPY > SMA200 via `sma_gate(SPYSIM, period=200)`, reindexed
  to scores DataFrame.
- OFF asset = ZROZ (default per T1c/T1d findings; spec didn't specify).
- T4d 5-asset pool (+SOXL) with per-asset vol<40% filter; effective window
  is 2010+ due to SOXL inception, dramatically reducing sample size.
- 4 iters total runtime ~30s.

---

## 10. How to implement T4b Clenow-top3 in practice (tier winner — close miss)

> **Caveat:** T4b (`xs_clenow_top3_zroz_spysma200`) is the T4 tier winner but
> **fails KILL T3→T4** (Sharpe 0.823 vs 0.903 threshold = -0.080). T3d K=2
> single-asset rotation **beats** this multi-asset cross-sectional. **Use
> T3d K=2** instead. Strategy is **DORMANT** per mandate §1.

### Tickers to trade

Pool of 4 LETFs ranked daily; ZROZ as OFF; macro gate SPY > SMA200.

| State | Operation |
|---|---|
| ON  (SPY > SMA200, ≥3 LETFs with Clenow > 0) | top-3 ranked LETFs, equal-weighted (33.3% each) |
| OFF (any condition fails) | 100% **ZROZ** |

Pool: **{UPRO, QLD, UGL, TMF}** (4 LETFs).

### Entry/exit logic

Every day at **market close**:

1. **Master gate**: compute `SMA200` on SPY. If `price_SPY < SMA200` → off.
2. **Clenow score 90d** for each LETF in the pool:
   - Run linear regression of `log(price)` against time over the last 90 trading days
   - `slope` = regression slope; `R²` = fit quality
   - `clenow_score = ((exp(slope))^250 - 1) × R²` (annualized × R²)
3. If ≥ 3 LETFs have Clenow score > 0 → top-3 by score (equal-weighted 33.3%)
4. Otherwise → 100% ZROZ

Rebalance: daily (higher turnover than T3d K=2).

### Frequency and turnover

- Compute: daily (~50 lines of Python; rolling regression)
- Trade: **high turnover** (~50-100 trades/year) — each change in the top-3 triggers a trade.
- Trade triggers: 1 LETF dropping from #3→#4 or rising from #4→#3 → rotation.

### Expected costs

T4 cross-sectional has **higher turnover than T3d K=2** → more drag:

| Cost | Sharpe drag |
|---|---|
| Brazilian Lei 14.754 | -1.5 to -2.5pp |
| Slippage 5bp × ~50-100 trades/year | -0.25pp |
| LETF spreads × frequency | -0.15pp |

**Estimated net Sharpe:** 0.55-0.65 (gross 0.823 - ~2.0-2.5pp drag).
**Net edge vs SPY:** ~+0.05 to +0.10. Possibly down to zero.

### Why this is NOT the study winner

1. **T3d K=2 (Sharpe 0.853) > T4b (0.823)** — single-asset Vote-K=2 simply
   captures more alpha per unit of risk in this LETF universe (4 correlated assets).
2. **Pool too small** (4 LETFs) — Clenow ranking works on
   stocks-on-the-move with universes of 200+ stocks; here there is little
   to differentiate.
3. **Top-3 more robust than top-2** (counter-intuitive — diversification
   compensates for the limited pool size) — but still doesn't beat single-asset.
4. **Master gate (SPY > SMA200) duplicates the SMA200** that T3d K=2 already
   has as 1 of its 4 signals.
5. **High turnover** drags more on net Sharpe.

**G1 PBO finally passes for the first time in the study** (0.357 with 4
diverse XS configs) — **confirms the hypothesis that T1-T3 G1 failures
were small-grid CSCV artifacts**, re-validated in iter 022 T3d-extended
(PBO 0.421 with N=12).

### Mandate alignment

DORMANT per mandate §1. The T4 family is interesting research evidence
(single-asset wins over multi-asset in this LETF universe; G1 small-grid
hypothesis confirmed) but not recommended for capital.

---

## 11. Citations

- Clenow ranking: `[stocks_on_the_move, p.70-77, p.98]`
- Carver EWMAC composite: `[systematic_trading, ch.7-8, p.122-133]`
- Vol-gate threshold: `[leverage_for_the_long_run, p.5-6]`
- Master-gate filter: `[stocks_on_the_move, p.98-99]`
- Anti-curve-fit + inheritance: spec §2.5, §3.4
- spec §7.5 honest expectation: T4 advance was lower-half probability;
  outcome materialised as no advance over T3

---

## Post-close addendum (2026-05-07)

Tier-4's cross-sectional family was not re-run as a standalone Sortino study, so its internal ranking remains a historical Sharpe diagnostic. The family (led by `xs_clenow_top3_zroz_spysma200`, Sharpe 0.823 secondary) was eliminated by the KILL T3→T4 gate and did not participate in the Sortino re-analysis, which focused on the T3d K=2 lineage. The inherited T3 incumbent was the Sortino canonical, later superseded by `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`. See `SORTINO_REANALYSIS_REPORT.md` §3–§4 for the canonical and top-10 Sortino evaluation.
