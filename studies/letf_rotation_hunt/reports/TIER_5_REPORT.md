# T5 (Carver vol-target) — Tier Report

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

> ## ⚠️ Post-close T5 expansion (2026-05-08)
>
> The original T5 tier ran 2 configs (T5a, T5c). Sub-phases T5b (carry forecast)
> and T5d (HRP/ERC weighting) were skipped per scope. After post-close review,
> T5 was reopened with a formal methodology amendment to add 20 new configs
> across iters 022-025:
>
> - **T5a sigma sweep** (iter_022): 5 configs sweeping σ_target ∈ {0.15..0.35}
> - **T5b carry forecast** (iter_023): 4 configs (carry_only + ewmac_carry, single + multi-asset)
> - **T5c grid** (iter_024): 7 configs (IDM × pool variants)
> - **T5d HRP/ERC** (iter_025): 4 configs (HRP × σ_target=0.25/0.30, ERC × σ_target=0.25/0.30)
>
> See §17 of `STUDY_FINAL_REPORT.md` for full disclosure.
>
> **Verdict update:** T5-expansion-best is `025-2026-05-08-T5d-hrp-erc/erc_multi4_sigma030` with Sortino
> = 1.1399 (Sharpe = 0.7993) on lh_56y. **KILL T5-expansion: FIRES**
> (threshold 1.272 = Track A canonical Sortino + 0.05 anti-curve-fit).
> Track A canonical winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` retains
> DSR PASS at N=426 (p_v2 = 0.0024). 22 early-tier T1 configs flipped PASS→FAIL
> with the higher cumulative N (none are winners).
>
> **Body of report below preserved as-is for historical fidelity.**

---

**Status:** T5 tier complete (2026-05-06). 2 sub-phases (T5a, T5c), 2 configs, iters 020-021.
**Tier verdict:** **KILL T4→T5 FIRES.** T5-best Sharpe 0.740 (T5c multi-asset) falls 0.163 below threshold 0.903. Continuous vol-targeting does not improve over T3d K=2 binary signal in this universe.
**T5-best:** `voltarget_multi4_sigma025_idm25_off_zroz` Sharpe 0.740, score 61, **PROMISING** — but pct_above 76% < 95% strict bar.
**Final tier — study closes.** T3d K=2 stands as definitive study winner.

Spec ref: §2.6, §3.4. T5 inherits T3-best (KILL T3→T4 fired in iter 019).
**Skipped per scope**: T5b carry forecast (yield-curve data unavailable),
T5d HRP (optional per spec).

---

## 0. Underwater-vs-benchmark (T5-best vs SPY)

![Underwater vs benchmark](tier_5_plots/tier5_underwater_vs_benchmark.png)

*T5c `voltarget_multi4_sigma025_idm25_off_zroz` (Sharpe 0.740) relative to
SPY buy-hold. **Only 76.6% of days above SPY** — fails v2 strict bar 0.95.
Min ratio post-warmup 0.56× (strategy fell to 56% of SPY equity at one point).
End ratio 15.9× (vs T3d K=2 end ratio 256×). Despite reasonable Sharpe,
continuous vol-targeting under-allocates during clear uptrends and ends well
below T3d K=2's compounding pace.*

---

## 0b. All T5 configs in one picture (ratio to SPY)

![All T5 configs relative to SPY](tier_5_plots/tier5_all_configs_relative_to_spy.png)

*All 22 T5 configs (2 original from iters 020-021 + 20 from T5 expansion
iters 022-025: T5a σ-sweep ×5, T5b carry ×4, T5c grid ×7, T5d HRP/ERC ×4)
as strategy_eq / SPY_eq ratio, log-scale. SPY = 1.0 black dashed. Top 5
by Sharpe lh_56y are highlighted (bold): `erc_multi4_sigma030` (T5d,
Sharpe 0.7993, T5-expansion-best), `erc_multi4_sigma025` (T5d, 0.7956),
`ewmac_carry_multi4_sigma025` (T5b, 0.7522), and the two original T5c
variants (`voltarget_multi4_sigma025_idm25_off_zroz` and
`voltarget_multi4_idm25`, both 0.7400). Remaining 17 configs faded gray.
**None clears the KILL T5-expansion threshold (Sortino 1.272 = Track A
canonical + 0.05 anti-curve-fit); T5-expansion-best Sortino 1.1399 falls
0.1321 short.** Most configs spend extended periods near or below SPY.
Visual proof of the reinforced T5 finding: **Carver framework does not
generalize to a small-pool LETF universe even with expanded coverage**
(carry forecast, HRP/ERC weighting, IDM and σ_target sweeps tried).
Designed for futures with 10+ uncorrelated instruments; small LETF pools
of correlated equity/bond/gold families do not realize Carver's
diversification benefits.*

---

## 1. Sub-phase summary

| Sub-phase | Variant | Pool | IDM | Sharpe (lh_56y) | KILL T4→T5 |
|---|---|---|---:|---:|---|
| **T5a** (iter 020) | Single-asset QLD vol-target | {QLD} | 1.0 | 0.587 | FIRES |
| **T5c** (iter 021) | Multi-asset 4-LETF vol-target | {UPRO, QLD, UGL, TMF} | 2.5 | **0.740** | FIRES |

(T5b carry forecast skipped — needs yield-curve data; T5d HRP optional.)

Cumulative `n_trials = 406` (T1 22 + T1d 360 + T2 11 + T3 7 + T4 4 + T5 2).

---

## 2. T5 ranking + comparison

| Rank | Sub | Config | Sh lh_56y | Sh mod_1990 | Sh spy_real | Sh ndx_real | CAGR | MDD | pct>b | min_r | Score | Tier |
|---:|----|--------|---:|---:|---:|---:|---:|---:|---:|---:|---:|------|
| 1 | T5c | `voltarget_multi4` | 0.740 | 0.744 | 0.768 | 0.844 | 19.4% | -62.9% | 76.1% | 0.56× | 61 | PROMISING |
| 2 | T5a | `voltarget_qld` | 0.587 | 0.567 | 0.625 | 0.683 | 13.9% | -55.8% | 98.3% | 0.87× | 32 | NEAR_FAIL |

**T3d K=2 incumbent: 0.853**. T5c gap: -0.113. T5a gap: -0.266.

---

## 3. Why T5 doesn't beat T3

**T5a single-asset (Sharpe 0.587)** is the surprise: it's WORSE than T3d K=2
(0.853) on the same QLD/ZROZ pair. Three reasons:

1. **Continuous sizing under-allocates during uptrends.** When EWMAC forecast
   magnitude is small (e.g., during early trend formation or near SMA200
   crossover), position sizing scales down. T3d K=2 binary signal commits 100%
   when ON; T5a allocates ~40-60%, missing the trend continuation.
2. **Vol-scaling kicks during recovery.** Post-drawdown, realized vol is high
   so daily_vol_target/vol gives small positions; you under-deploy exactly
   when uptrends restart.
3. **Position inertia 10% threshold** further dampens responsiveness.

**T5c multi-asset (Sharpe 0.740)** fares better via diversification:
- 4-LETF pool gives some uncorrelated exposure
- IDM=2.5 lifts effective leverage to compensate for under-allocation per asset
- But: pct_above 76% < 95% — strategy is below SPY equity 24% of the time
- Compare T3d K=2 pct_above 100% — T5 doesn't dominate SPY consistently

The Carver vol-target framework is designed for **liquid futures with Sharpe
0.5-1.0 across many uncorrelated instruments**. For LETFs in this study:
- 4-asset pool is too small for Carver's IDM machinery (designed for 10+)
- LETFs are highly correlated (UPRO, QLD, SOXL all trend with equity)
- Forecast magnitude scaling under-allocates during clear uptrends
- The simpler binary "all-in or all-out" of T3 captures more LETF-compounding
  upside than continuous sizing

---

## 4. Decision: KILL T4→T5 FIRES — study closes

T5-best Sharpe 0.740 << threshold 0.903. **No tier in T2-T5 advances over T3.**

Final study state:
- **Study winner**: T3d K=2 `qld_vote_k2_off_zroz` (Sharpe 0.853, score 82, STRONG WC=Y)
- T2 contributed nothing (KILL T1→T2)
- T3 was the breakthrough (only tier advance)
- T4 cross-sectional close miss but doesn't beat T3
- T5 vol-target plateaus around T3 territory or below

See `STUDY_FINAL_REPORT.md` for full study consolidation.

---

## 5. Methodology notes

- New module `studies/letf_rotation_hunt/run_iter_t5.py`: Carver vol-target
  dispatcher reusing T1's gates/scoring/artifacts pipeline.
- Pre-existing `signals.py:ewmac_forecast` + `strategies/vol_targeted.py:build_positions`
  used as-is. EWMAC composite (16,64) + (64,256) with FDM=1.41 per
  Carver Table 49 [p.285].
- Forecast cap ±20, σ_target=0.25 (Half-Kelly), IDM=1.0 (T5a) or 2.5 (T5c)
  per Carver [p.170-171], position inertia 10% [p.174].

## 6. How to implement T5c voltarget-multi in practice (tier winner — losing tier)

> **Caveat:** T5c (`voltarget_multi4`) is the T5 tier winner but
> **fails KILL T4→T5** (Sharpe 0.740 << 0.903). Crucially, it also **fails
> the underwater-vs-bench strict bar** (pct_above_SPY 76.6% < 95%) — strategy
> spends 24% of time below SPY equity. **Use T3d K=2** instead.
> Strategy is **DORMANT** per mandate §1.

### Tickers to trade

Pool of 4 LETFs running under the Carver vol-target framework + EWMAC
composite forecast.

| Sleeve | Ticker | Type |
|---|---|---|
| Equity | UPRO | 3× SPY |
| Equity | QLD | 2× NDX |
| Gold | UGL | 2× Gold |
| Bond | TMF | 3× 20yr Treasury |
| OFF | ZROZ | 25y zero-coupon |

### Entry/exit logic (simplified Carver framework)

T5c logic is more complex than other tiers — implementation requires more
infrastructure. Summary:

For each LETF in the pool, every day at market close:

1. **EWMAC forecast** = EMA fast (16d) − EMA slow (64d) normalized by
   volatility, scaled by scalar 3.75, capped at ±20. Also compute
   EWMAC(64,256) and take the average (FDM=1.41).
2. **Vol scaling**: target σ = 0.25 (Half-Kelly per Carver p.144); position
   raw weight = forecast/cap × σ_target / σ_realized × IDM (2.5 for
   multi-asset).
3. **Position inertia 10%** (Carver p.174): only re-balance if target
   position differs > 10% from current.
4. **Master gate**: SPY > SMA200 must be TRUE for any position; otherwise
   → 100% ZROZ (off-state).

Pool of 4 → each LETF has 0-25% weight (vol-targeted); ZROZ is the residual.

### Frequency and turnover

- Compute: daily (~150 lines of Python — uses `signals.py:ewmac_forecast`
  + `strategies/vol_targeted.py:build_positions`).
- Trade: high turnover (continuous rebalance) **but dampened** by the 10%
  position inertia (~30-50 rebalances/year per sleeve).

### Expected costs

Higher than T3d K=2 and T4b due to rebalance frequency and multi-LETF
structure:

| Cost | Sharpe drag |
|---|---|
| Brazilian Lei 14.754 | -1.5 to -2.5pp |
| Slippage × ~30-50 rebalances × 4 sleeves | -0.30pp |
| LETF spreads × frequency (UPRO, QLD, UGL, TMF) | -0.20pp |

**Estimated net Sharpe:** 0.40-0.50 (gross 0.740 - ~2.5-3.0pp drag).
**Net edge vs SPY:** **below zero** — not recommended.

### Why this is NOT the study winner

1. **Continuous sizing under-allocates during clear uptrends.** When the
   EWMAC forecast magnitude is small (early trend formation or near
   SMA200 crossover), position scaling reduces exposure. T3d K=2 binary
   commits 100% on-signal; T5a allocates ~40-60%, missing trend
   continuation.
2. **Carver framework was designed for liquid futures with 10+ uncorrelated
   instruments** — `[systematic_trading, ch.10-12]`. Here: a pool of 4
   highly correlated LETFs (UPRO and QLD trend together).
3. **IDM=2.5 does not compensate** the under-allocation per asset;
   sub-optimal vs binary all-in/all-out.
4. **pct_above_SPY 76% << 95% strict bar** — fails the critical v2
   scoring underwater-vs-bench criterion. T3d K=2 hits 100%.

**Critical takeaway**: Carver vol-target works best on **futures markets**
(e.g., systematic_trading) with 10+ uncorrelated instruments. For **LETF
rotation with a small pool**, simple binary all-in/all-out (T3d K=2)
beats continuous sizing.

### Mandate alignment

DORMANT per mandate §1. T5 is educational: confirms that the Carver
framework does not generalize to a small-pool LETF universe. Not
recommended for capital.

---

## 7. Citations

- Carver framework: `[systematic_trading, ch.7-12 p.98-202]`
  - Forecast cap p.133
  - Half-Kelly σ_target p.144
  - IDM ≤ 2.5 p.170-171
  - Position inertia 10% p.174
  - EWMAC scalars Table 49 p.285
- Spec §2.6 T5a/c definitions; §3.4 anti-curve-fit + inheritance
- Spec §7.5 honest expectation: T5 advance was lower-half probability;
  outcome materialized as no advance.

---

## Post-close addendum (2026-05-07)

Configs from this tier were not re-evaluated in the post-close Sortino sub-study; their Sharpe-based ranking remains the only available metric data. T5's Carver vol-targeting family (led by `voltarget_multi4_sigma025_idm25_off_zroz`, Sharpe 0.740) was eliminated by the KILL T4→T5 gate and did not participate in the Sortino re-analysis. As the final tier, T5 confirmed the study-closing incumbent `qld_vote_k2_off_zroz` (T3d K=2), which anchored the post-close Sortino re-analysis. See `SORTINO_REANALYSIS_REPORT.md` §3–§9 for the Sortino evaluation of the T3d K=2 lineage and the updated operative ranking under the new winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`.
