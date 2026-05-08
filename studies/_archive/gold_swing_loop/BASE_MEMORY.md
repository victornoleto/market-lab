---
mission: "beat gold-complex buy-hold Sharpe by ≥0.10 on declared primary dataset (single XAU or multi-asset gold-complex), with positive Sharpe on corroborating datasets, across declared hold-time bucket (intraday/short_swing/medium_swing) and cost path (pep_cfd/cme_futures/inter_etf)"
total_iterations: 25
winners_found: 0
status: paused
paused_at: "2026-04-26 19:05"
paused_reason: "user decision; 0 winners after 25 iters across 2 phases (15 v1 + 10 v2 relaxed); plateau at MARGINAL/50 v1 → NEAR_FAIL/35 v2; structurally limited problem; deferred to future revisit"
latest_iteration: "025-2026-04-26-2147-gld-btc-cross-cluster-basket"
cumulative_n_trials: 25
rules_version: "2026-04-26-relaxed-r1"
final_report: "FINAL_REPORT.md"
---

# Gold Swing Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this file +
`iterations/NNN-*/` are the only continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`. Sister loop reference: `../strategy_hunt_loop/`.

---

## Mission (UPDATED 2026-04-26 — relaxed rules round 1)

After 15 iters with score cap at MARGINAL/50 (vol-regime-inverse axis,
iters 011/012/013), the rules were relaxed to give strategies more
freedom. Full rationale + diff: `## Rule changes 2026-04-26` below.

Find ONE strategy on the **gold complex** that:

1. **Beats declared primary benchmark Sharpe by ≥ 0.10** (after declared
   cost path), with positive Sharpe on at least 1 corroborating dataset.
2. **Passes 5/7 gates on primary** (4/7 on shorter datasets) +
   relaxed corroborating check (G6 bootstrap CI low > 0, G2 DSR p < 0.20).
3. **Declares hold-time bucket** (`intraday` ≤1d / `short_swing` 2-10d /
   `medium_swing` 10-30d). Observed mean hold must match bucket. Bucket
   determines realistic broker (intraday → Pepperstone/futures;
   medium → Inter ETF).
4. **Declares universe** (`single_xau` or `gold_complex` with XAU≥40%)
   and **cost path** (`pep_cfd` / `cme_futures` / `inter_etf`).
5. **Is not a minor variation of a known dead-end** (own list + sister
   loop closures).

**Hard context:** project is in mandate §1 **MAINTENANCE 100% Plano C**.
This loop produces research output, not live positions. Even a winner
is a CANDIDATE — deployment requires override §7 + paper-trade 3-6
months. Multi-asset gold_complex universe is now allowed at the loop
level; mandate §3's "Plano A multi-asset extension" requirement is
preserved for actual deploy.

---

## Rule changes 2026-04-26 (relaxed round 1)

Decision context: after 15 iters under the original rules, score cap
was MARGINAL/50 on a single axis (vol-regime-inverse, iters 011/012/013).
Most failures attributable to structural restrictions, not lack of
ideas. User authorized the following relaxations, NOT touching DSR
n_trials policy or citation discipline.

**What changed:**

1. **Universe (`#1`)** — `single_xau` ⟶ also allow `gold_complex`
   (XAU ≥ 40% + any of {XAG/SLV, GDX/GDXJ, PT/PL/PPLT, IAU, RGLD}).
   Sister loop's empirical evidence: every winner was multi-asset.
   Don't replicate the single-asset ceiling here.
2. **Hold-time (`#2`)** — `mean_hold ≤ 5d HARD GATE` ⟶ 3 declared
   tracks (`intraday` ≤1d / `short_swing` 2-10d / `medium_swing` 10-30d).
   Each track wins on its own bucket. Medium-swing winners route to
   Inter ETF deploy track instead of Pepperstone — both are valid.
3. **Cost path (`#3`)** — `pep_cfd` only ⟶ also `cme_futures` (1-2 bps
   via IBKR, intraday-friendly) and `inter_etf` (long-only + DARF).
   Tighter spread enables strategies that died at 8 bps.
4. **Datasets (`#5`)** — added `gold_synth_40y` (DEFERRED — first iter
   needing it constructs from FRED/LBMA fixing series, caches
   `data/external/macro/gold_fixing_daily.parquet`). Modeled on
   sister loop's testfolio synth — long-window robustness check.
5. **Cross-dataset (`#6`)** — `pass gates on all 3` ⟶ `primary +
   corroborating`. Primary dataset gets full gate count (≥5/7 or 4/7
   per dataset); corroborating just needs G6 bootstrap CI low > 0
   + G2 DSR p < 0.20. Single-regime strategies are now valid winners.

**What did NOT change** (deliberate):

- DSR n_trials policy (sister IC-8): single cfg per iter unless
  Bonferroni. Relaxing here would re-pollute DSR after sister loop's
  control work.
- Citation policy: book primary + paper secondary remains mandatory.
- Bench thresholds: Sharpe edge ≥ +0.10, gates 5/7, MDD/CAGR floors.
  Those define real deploy bar; relaxing them makes the loop
  meaningless.

**Cumulative state preserved**: `total_iterations=15`,
`cumulative_n_trials=15`. Iters 001-015 logged under original rules
(pre-relaxation); their dead-ends still apply.

**Iter 016+ runs under relaxed rules**: scoring + winner check use the
new spec. Do NOT re-test original-rules dead-ends as new ideas — iter
006/008/009 (FOMC drift, XAG MR/trend) closed at FAIL/0; iters 011-013
plateaued at MARGINAL/50; macro angles (TIPS, DXY) regressed. Use the
new freedoms (multi-asset, longer hold, futures spread) on
qualitatively different mechanisms, not the same ones at deeper params.

---

## Sister loop transferable lessons (DO NOT re-derive empirically)

`strategy_hunt_loop/` ran 54+ iters; cross-loop principles:

1. **DSR n_trials drains fast** — single cfg per iter unless Bonferroni-justified (sister 046).
2. **Out-of-family composition at ρ<0.50 compounds DSR** — Markowitz proportional-Sharpe weighting, NOT 50/50 (sister 049).
3. **Vol-target wrappers absorb same-family overlays** (sister 020/021/040).
4. **Modulation axes (input/weight/output/leverage) saturate** at base ceiling (sister 042-048); additive new streams beat modulation.
5. **Survivorship-biased data destroys cross-sectional ranking** (sister 003/054); applies if testing gold + miner basket.
6. **Pre-val mandatory for overlays** — corr w/ base before backtest. **Iter 007/008**: cost-magnitude gate (`mean_fwd_bps > 1.5 × spread_RT_bps`) + ADF. **Iter 009 (GS-9)**: augmented gate necessary but NOT sufficient — bar-avg pre-val OVERESTIMATES state-machine realised gross when entries timeout-spaced. Add `state_machine_aware_fwd_n_bar` (iter 010+).

Sister `BASE_MEMORY.md` + `DEAD_ENDS.md` for full catalog.

---

## Winners found

None yet. When found, append yaml block:

```yaml
winner:
  iteration: NNN
  hypothesis: "<one-line hypothesis>"
  config: "<cfg_id>"
  score: 100  # 90+ AND winner_conditions_met=True
  datasets_passing:
    - gld_long: {sharpe: X, cagr: Y%, mdd: Z%, gates: N/7}
    - xauusd_real: {...}
    - xauusd_intraday: {...}
  citation_primary: "[book.slug, p.X]"
  iteration_dir: "iterations/NNN-YYYY-MM-DD-HHMM-slug/"
  cost_model: "spread X bps + swap Y bps/night, mean hold M days"
```

---

## Top-K strategies ranked

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| 1 | 013 | MARGINAL | **50** | vol_regime_inverse_sma200_long_only | `[short_term_trading_strategies, p.106]` + `[volatility_trading, p.58-59]` | iter 011 + Connors SMA(200); gld MDD 46→37%; gld DSR p=0.253>0.05; 22d swing-ext; GS-13 |
| 2 | 011 | MARGINAL | **50** | vol_regime_inverse_60_252_long_only | `[volatility_trading, p.58-59]` + `[trading_systems_methods, p.13-14]` | 1st +Sh edge bench 2/3 ds; gates 7/7 xauusd; gld weak; 44d swing-ext; GS-11 |
| 3 | 012 | MARGINAL | **50** | composition_iter_003_iter_011_markowitz | `[advances_fin_ml, p.222-223]` | IC-7 Markowitz 003+011; gld MDD halved 46→25%; gld DSR p=0.201; GS-12 |
| 4 | 020 | NEAR_FAIL | **35** | ic7_3stream_iter003_iter018_iter015_markowitz_gld_primary | `[advances_fin_ml, p.222-223]` + `[risk_parity, ch.2]` | 3-stream IC-7 hits 93.6% of √(S²₀₀₃+S²₀₁₈+S²₀₁₅)=0.520; MDD xau 9.76% loop-lowest ever; DSR p=0.36; IC-6 rolling-ρ on (003,015)=21.9% PRIMARY → fail; GS-20 closes 3-stream IC-7 on catalog when 3rd stream is macro-FX |
| 5 | **025** | **NEAR_FAIL** | **35** | **cross_cluster_rsi2_sma200_gld60_btc40_basket** | `[risk_parity, ch.7]` + `[ilmanen_expected_returns, ch.10]` | **★ 1st cross-cluster IC-6 BREAK in 25 iters: GLD+BTC 60/40 RSI(2)+SMA(200) basket; rolling-60d ρ vs iter003 = 68.1% PRIMARY (drop −27pp vs GS-23 96.8% / GS-24 94.9%, static ρ +0.26 vs +0.71/+0.67)**; corroborating MDD **5.69%** (loop-best ever); basket Sh +0.17 BELOW iter003 +0.30 (lift −0.13) due to BTC cost asymmetry (25 bps RT + −5 bps/night swap) + signal asymmetry; 4/6 kills fired (#3 cross-cluster did NOT fire — historic first); **GS-25 closes fixed-weight cross-cluster GLD+BTC same-MR basket but UNBLOCKS IC-7 Markowitz GLD+BTC + asymmetric-per-leg-signals as next priorities** |

(iter 019 score=35, iter 018 score=35, iter 016 score=35, iter 024 score=30, iter 017 score=28, iter 021 score=28, iter 022 score=28, iter 014 score=26, iter 010 score=22, iter 003 score=22, iter 023 displaced from top-5 by iter 025's IC-6 break, iter 001 score=18, iter 015 score=17, iter 004 score=16, iter 007 score=16, iter 006 score=15, iter 009 score=1, iter 008 score=0 → all below top-5 floor.)

**Ten iters now in NEAR_FAIL 28-35 band** (017/018/019/020/021/022/016/023/024/**025**). **Iter 025 (60/40 GLD+BTC genuinely cross-cluster basket on iter 003 signal) is partial breakthrough: ★ FIRST IC-6 ROLLING BREAK below 80% in 25 iters (achieved 68.1%, −27 pp vs iter023/024)**. The cross-cluster diversification thesis is empirically validated at the position-vector level — BTC's MR signal genuinely fires on different days than gold's MR (static ρ +0.26 vs PM-adjacent +0.7). However, cross-cluster IC-6 break alone does NOT translate to Sharpe edge: basket Sh +0.17 is BELOW iter 003 +0.30 because BTC's higher costs (25 bps RT spread + −5 bps/night swap, ~3× gold's per-leg cost) + weaker standalone post-cost Sharpe drag the 40%-weighted leg. **GS-25 closes fixed-weight 60/40 cross-cluster GLD+BTC same-MR-signal basket** but UNBLOCKS the IC-7 Markowitz GLD+BTC tangency framework (proportional-Sharpe weighting) and asymmetric-per-leg-signal compositions. The cross-cluster framework remains the most-promising direction for iter 026+.

---

## Iteration log (newest first)

### 025 — 2026-04-26 — cross_cluster_rsi2_sma200_gld60_btc40_basket (NEAR_FAIL, 35)
- **Result:** Sh basket/xau +0.1725/+0.6689 (Δ −0.901/−0.084), gates 4/5 of 7, DSR p 0.918/0.608 (n=25), MDD 15.45/5.69% (xau loop-best EVER), lift vs iter003 −0.1275 BELOW single-asset; ★ **IC-6 ρ vs iter003 rolling = 68.1% PRIMARY** (★ FIRST sub-80% in 25 iters; static ρ +0.258 vs GS-23 96.8% / GS-24 94.9% ⇒ −27pp drop); IC-6 vs iter011 = 14.8% (not vol-regime); per-leg trades gold 34 / btc 37 over 12.3y; hold 4.65d short_swing PASS; 4/6 kills fired (#3 cross-cluster NOT fired — historic first); score 1:5 2:15 3:0 4:0 5:15 6:0.
- **Lesson:** ★ **Cross-cluster IC-6 floor IS breakable** when 2nd leg has truly orthogonal macro drivers (BTC crypto-adoption/halving/regulatory vs gold real-rates/DXY/safe-haven). However IC-6 break alone does NOT yield Sharpe edge under fixed weights when leg Sharpes + costs are asymmetric (BTC 25 bps RT + −5 bps/night swap ~3× gold's). **GS-25 closes fixed-weight 60/40 cross-cluster GLD+BTC same-MR-signal basket** but UNBLOCKS IC-7 Markowitz GLD+BTC tangency + asymmetric-per-leg-signal compositions for iter 026+. See `iterations/025-*/`.

### 024 — 2026-04-26 — cross_cluster_rsi2_sma200_gld60_gdx40_basket (NEAR_FAIL, 30)
- **Result:** Sh basket/xau +0.2022/−0.1064 (Δ −0.267/−1.071), gates 4/3 of 7, DSR p 0.860/0.988 (n=24), MDD 13.94/10.33%, lift vs iter003 −0.098 BELOW single-asset; IC-6 ρ vs iter003 rolling 94.9% PRIMARY (vs 96.8% iter023, ρ static +0.67), kill #3b vs iter011 rolling 27.4% PASS; hold 4.91d short_swing PASS; 5/6 kills fired; score 1:0 2:15 3:0 4:0 5:15 6:0.
- **Lesson:** GDX is gold-derivative (Ilmanen ch.10: ρ ~0.7-0.8 spot gold, ~0.3-0.4 broad equities); RSI(2) on miners fires same days as bullion. **GS-24 closes ALL gold-complex-universe basket extensions** (GDX/GDXJ/RGLD/SIL/SILJ/PPLT). Cross-cluster requires GENUINELY orthogonal driver (BTC, TLT, SPY-not-miners). See `iterations/024-*/`.

### 023 — 2026-04-26 — multi_asset_rsi2_sma200_gld60_slv40_basket (NEAR_FAIL, 35)
- **Result:** Sh basket/xau +0.295/+0.257 (Δ −0.137/−0.633), gates 4/4 of 7, DSR p 0.737/0.897 (n=23), MDD **9.19%/7.13%** (loop-best ever on 20y), hold 4.15d short_swing PASS; ALL 6/6 kills fired (IC-6 ρ vs iter003 rolling 96.8% PRIMARY); ρ static vs iter003 +0.71/+0.76; score 1:5 2:15 3:0 4:0 5:15 6:0.
- **Lesson:** Within-PM basket (GLD+SLV) extension functionally identical to single-asset on position-vector level (both metals above SMA200 + RSI(2) dip same days). MDD reduction is portfolio-construction, not Sharpe edge. **GS-23 closes within-precious-metals basket extensions**; sister-loop "every winner was multi-asset" reinterpreted as needing cross-CLUSTER (PMs+crypto/bonds/equities). See `iterations/023-*/`.

### 022 — 2026-04-26 — gvz_zscore (NEAR_FAIL, 28) — Sh gld/xau +0.246/+0.333 (Δ −0.383/−0.706), gates 4/4 of 7, DSR p 0.608/0.662 (n=22), MDD 30.9/12.9%, hold 24.6d ∈ medium_swing PASS; 3/4 kills fired (#3 IC-6 ρ vs iter011 rolling 59.7% PRIMARY HARD); ρ static vs iter011 = +0.55, vs iter003 = +0.08; score 1:5 2:8 3:0 4:0 5:15 6:0. **GS-22**: GVZ implied-vol z-score gate is a vol-regime family RE-SKIN of iter 011 σ_60/σ_252 ratio at position-vector level on gold; forward-looking IV and backward-looking realized-vol-ratio fire entries on overlapping low-vol-regime windows; closes option-implied vol family as structurally novel direction. See `iterations/022-*/`.

### 021 — 2026-04-26 — dcot_mm_zscore (NEAR_FAIL, 28) — Sh +0.073/+0.277 (Δ −0.566/−0.761), gates 4/3 of 7, DSR p 0.836/0.714 (n=21), MDD 30.2/15.6%, hold 27.5d ∈ medium_swing PASS; kills #1+#2 fired; ρ vs iter 018 = +0.85 BOTH ds; score 1:5 2:8 3:0 4:0 5:15 6:0. **GS-21**: DCOT MM contrarian Sh +0.073 materially WEAKER than commercials Sh +0.352 (Δ −0.28); producer-hedging leverage in commercials ADDS edge, not contaminates; "speculative bucket isolation" FALSIFIED. ρ vs iter 003 +0.02 IC-7-eligible but standalone too weak (combined ceiling 0.31). See `iterations/021-*/`.

### 020 — 2026-04-26 — ic7_3stream_003_018_015_markowitz (NEAR_FAIL, 35) — Sh +0.487/+0.442 (Δ −0.198/−0.596), gates 5/4 of 7, DSR p 0.365/0.773 (n=20), MDD 10.95/9.76% (xau loop-best EVER), weights gld 0.55/0.32/0.13, hold 26.30d; kills #3 DSR + #4 IC-6 rolling-ρ on (003,015)=21.9% PRIMARY FIRED; score 1:5 2:15 3:0 4:0 5:15 6:0. **GS-20**: 3-stream IC-7 ceiling 93.6% of √(S²₀₀₃+S²₀₁₈+S²₀₁₅)=0.520; (003,015) low static ρ +0.17 but non-stationary rolling — drawdown regimes co-trigger RSI-MR + DXY-trend.

### 019 — 2026-04-26 — ic7_003_018_markowitz (NEAR_FAIL, 35) — Sh +0.458/+0.346 (Δ −0.226/−0.692), gates 5/4 of 7, DSR p 0.41/0.84 (n=19), MDD 9.56/8.33% (gld −36pp), IC-6 ρ60d 1.5/0.0% PASS, hold 12.64d; kill #3 fired; score 1:5 2:15 3:0 4:0 5:15 6:0. **GS-19**: 2-stream IC-7 hit 99.7% of √(S²A+S²B)=0.460 on lowest-ρ pair; DSR-deflator at n=19 exceeds marginal Sharpe lift.

### 018 — cot_zscore_w156_lag1_max30d (NEAR_FAIL, 35) — Sh gld/spot +0.352/+0.289 (Δ −0.43/−0.75), gates 5/3, DSR p 0.354/0.696 (n=18), MDD 25.3/16.0%, hold 28.4/30d PASS medium_swing; score 1:5 2:15 3:0 4:0 5:15 6:0. **GS-18**: z-score lifts Briese Sh +0.137→+0.352 (+0.215) but standalone trails Δ −0.43 → COT-positioning standalone family ceiling ≈ Sh 0.35; ρ vs iter003 +0.013/+0.004 (orthogonal). IC-7 003+018 unblocked. See `iterations/018-*/`.
### 017 — cot_briese_ruggiero_70_30 (NEAR_FAIL, 28) — Sh gld/spot +0.137/+0.310 (Δ −0.547/−0.728), gates 4/3, DSR p 0.732/0.675 (n=17), MDD 31.8/13.0%, hold 28.3/29.3d; kill #2; score 1:5 2:8 3:0 4:0 5:15 6:0. **GS-17**: ρ vs iter003 +0.003/−0.0002 (1st sub-0.20 ρ at consistent daily) → COT-positioning structurally orthogonal to price/macro/FX. Supersedes GS-16. See `iterations/017-*/`.
### 016 — ic7_iter003_iter015_markowitz_intra_primary (NEAR_FAIL, 35) — Sh +0.355/+0.346/+0.381, gates 4/4/4, DSR p 0.56/0.81/0.78 (n=16), MDD intra halved 24→12%, hold 43d ∉ medium_swing → mismatch; score 1:5 2:15 3:0 4:0 5:15 6:0. **GS-16**: iter015 ρ=−0.07 on intra was freq-mismatch artifact; true daily ρ=+0.22. SUPERSEDED by GS-17/18. See `iterations/016-*/`.
### 015 — dxy_sma_slope_falling_200_20 (FAIL, 17) — Sh +0.24/+0.32/+0.36 (Δ −0.44/−0.72/−0.75), gates 4/4/4, DSR p 0.73/0.63/0.52 (n=15), hold 113-121d, gld MDD 50.72% breaches; score 1:0 2:7 3:0 4:0 5:10 6:0. **GS-15**: macro-generic same-clock CONFIRMED ρ vs iter011=+0.513 on gld_long. See `iterations/015-*/`.
### 014 — macro_dfii10_falling_60d (NEAR_FAIL, 26) — Sh +0.32/+0.54/+0.82 (Δ −0.37/−0.50/−0.28 trails 3/3), gates 4/5/5, DSR p 0.60/0.65/0.35 (n=14), hold 16-18d, G6 Boot ✗ 3/3; score 1:0 2:11 3:0 4:0 5:15 6:0. **GS-14**: ρ vs iter011=+0.52 on gld_long EXCEEDS IC-7 0.50 (rate-cycle feedback); closes IC-7-on-gld_long via macro at lookback=60d. See `iterations/014-*/`.

### 013 — vol_regime_inverse_sma200_long_only (MARGINAL, 50) — Sh +0.51/+1.46/+1.69 (Δ −0.17/+0.43/+0.59), gates 4/7/7, DSR p=0.253/0.017/0.006 (n=13), hold 18.7/23.4/21.9d swing-ext, gld MDD 46→37% (−9.5pp); score 1:20 2:15 3:0 4:0 5:15 6:0. **GS-13**: bear-leak is MDD-problem not Sharpe; vol-regime ceiling ≈ +0.55.
### 012 — composition_iter_003_iter_011_markowitz (MARGINAL, 50) — Sh +0.54/+1.42/+1.42, gates 4/7/7, DSR p=0.201/0.020/0.020 (n=12), hold 31.7/43.0/37.1d swing-ext, gld MDD halved 46→25%; score 1:20 2:15 3:0 4:0 5:15 6:0. **GS-12**: IC-7 Markowitz can't lift DSR<0.05 from 2 DSR-failing bases (combined Sh ≤ √(S_A²+S_B²) ≈0.567).
### 011 — vol_regime_inverse_60_252_long_only (MARGINAL, 50) — Sh +0.48/+1.42/+1.59 (Δ −0.20/+0.38/+0.49), gates 4/7/7, DSR p=0.275/0.018/0.009 (n=11), hold 51/47/44d, winner=4/5; score 1:20 2:15 3:0 4:0 5:15 6:0. **GS-11**: σ_60<σ_252 STANDALONE MARGINAL; first +Sh-edge bench-beat 2/3 ds; unblocks IC-7.
### 010 — vol_regime_gate_60_252 (NEAR_FAIL, 22) — Sh +0.21/+0.04/+0.09, gates 4/4/4, DSR p=0.728/0.928/0.912, hold 41-49d, MDD 38/24/28%; pre-val 1/3; score 1:0 2:7 3:0 4:0 5:15 6:0. **GS-10**: σ_60>σ_252 STANDALONE 2nd +Sh-3/3 BLOCKED; inverse (iter 011) breakthrough.
### 009 — xau_xag_pair_trend_lb60_z2 (FAIL, 1) — Sh −0.18/−0.06/−1.41, gates 3/3/2, DSR p≥0.95, hold 10/10/1.18d; gross −30/+25/+5 vs pre-val +42/+98/+8 (gld INVERTED). **GS-9**: bar-avg pre-val OVERESTIMATES state-machine gross under timeout-spaced entries; closes MR+TF for `|z|>kσ`.

### 008 — xau_xag_pair_mr_lb60_z2 (FAIL, 0, AUTO-ABORT) — pre-val 3/3 abort; ADF p=0.052/0.20/0.20; |z|>2 fwd=−41/−98/−7.7 bps (t=−1.0/−3.0/−2.9). **GS-8**: XAU/XAG MR non-stationary + trend-cont at extreme z.
### 007 — zscore_mr_1h_lb60 (FAIL, 16) — Sh −0.05/−0.19/−0.31 (Δ −0.74/−1.22/−1.41), gates 4/2/2, p=0.95/0.97/0.99; gross +3.5 vs cost ~9 bps. **GS-7**: z-MR cost-dominated.
### 006 — pre_fomc_drift_t2_to_t1 (FAIL, 15) — Sh −0.04/−0.23/−0.23 (Δ −0.72/−1.27/−1.34), gates 2/2/2; drift +15 bps/event ~5× too weak vs 83 bps cost. **GS-6**: calendar events too weak.
### 005 — dxy_zscore_recovery_5d (FAIL, 0, AUTO-ABORT) — pre-val gld_long FAIL (n=51, t=−1.88, mean −52 bps inverted). **GS-5**: Tiingo FX 2020+ collapses gld_long.
### 004 — vix_recovery_5d_hold (FAIL, 16) — Sh +0.23/−0.16/−0.16 (Δ −0.45/−1.20/−1.26), gates 4/2/2. **GS-4**: VIX +Sh on 21y, neg on 2020+ xauusd.
### 003 — connors_rsi2_sma200 (NEAR_FAIL, 22) — Sh +0.30/+0.19/+0.24 (Δ −0.38/−0.85/−0.86), gates 4/4/4, MDD slashed 25-33pp. **GS-3 escape**: 1st +Sh 3/3 single-mech; IC-7 base.
### 002 — donchian_20_10_turtle (FAIL, 11) — Sh −0.20/+0.24/+0.24, gates 3/4/4, hold 16d HARD GATE FAIL; gld_long MDD 74% DOUBLED. **GS-3**: single-mech bidir trapped.
### 001 — connors_rsi2_lt5_smaexit5 (FAIL, 18) — Sh +0.04/−0.23/−0.20, Track B catastrophic. **GS-1+GS-2**: RSI MR dies on gold; Track B FX cliff >15 tr/yr.

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iters AND
vs sister loop closures.

**Iter 026 candidates** (iter 025 PARTIALLY CONSUMED Priority 1 with **mixed result: ★ 1st cross-cluster IC-6 break in 25 iters (68.1% rolling vs iter003 — drop of −27pp vs GS-23/24 ceiling)** but Sharpe lift = −0.13 because BTC's higher costs + weaker standalone-Sharpe drag the 40%-weighted leg under fixed-weight composition; **GS-25 closes specifically "fixed-weight 60/40 GLD+BTC same-MR-signal basket"** but DOES NOT close the cross-cluster basket family — IC-7 Markowitz tangency on GLD+BTC and asymmetric-per-leg-signal variants are now the natural mechanical follow-ups):

1. **(NEW PRIORITY 1, PROMOTED via GS-25) IC-7 Markowitz GLD+BTC tangency** — let the data choose proportional-Sharpe weights instead of fixed 60/40. With gold-MR Sh ≈ 0.30 (iter 003) and BTC-MR Sh likely ~0.05-0.15 (post-cost on iter 025's evidence), Markowitz tangency expects weights ~85/15 (gold-heavy), with combined Sharpe upper bound = √(S²_gold + S²_btc · (1−ρ²)) × adjustment. The cross-cluster ρ ~0.26 evidence makes this a FIRST clean numerical test of IC-7 on a truly low-ρ pair within the gold loop. Engine reusable — only weight calculation changes. `[advances_fin_ml, p.222-223]` + `[risk_parity, ch.7]`.
2. **(NEW PRIORITY 2, PROMOTED via GS-25) Asymmetric per-leg signal: gold MR + BTC trend** — Connors RSI(2)+SMA(200) on gold leg, Donchian-200 (or Clenow ATR-trend) breakout on BTC leg. BTC's regime is more trend-persistent than mean-reverting historically (long bull legs separated by sharp corrections). Different family per leg may exploit each asset's natural regime. `[trend_following]` (Covel) on BTC leg + `[short_term_trading_strategies, p.105-118]` on gold leg.
3. **(PRIORITY 3, RETAINED) Cross-cluster basket: GLD + TLT 60/40** — bonds add duration + inflation drivers; TLT ρ to gold historically ~0.20-0.40 (positive but moderate; not as orthogonal as BTC but still cross-cluster). TLT cached. Bond trend regimes slower than gold; may need asymmetric SMA windows per leg (gold SMA(200), TLT SMA(60-100)). `[risk_parity, ch.7]` + `[ilmanen_expected_returns, ch.7-bonds]`.
4. **(PRIORITY 4, RETAINED) DCOT producer-merchant long-on-extreme-shorting** — hedger-side mechanical-bias mirror of iter 021; positioning family entirely. Data cached. `[trading_systems_methods, p.640]`.
5. **(PRIORITY 5, RETAINED) CME futures track A2 cost-path** — iter 007 z-MR died at 8 bps RT. At CME GC futures 1-2 bps RT (per INFRASTRUCTURE.md A2), same z-MR is +1.5-2 bps net per trade — possibly intraday-MR-economic again. Genuinely different cost regime (4× tighter spread).
6. **(PRIORITY 6, RETAINED) Cross-cluster basket: GLD + SPY 60/40** — broad-equity orthogonal driver (without miner amplification of gold). SPY cached (~21y). Caveat: SPY's drift is steeper than gold; SMA(200) regime gate validated by sister loop. `[short_term_trading_strategies, p.105-118]` + `[risk_parity, ch.7]`.
7. **COT + price-momentum overlay** — gate canonical Briese 70/30 entries by 12-3-1 momentum filter. IC-6 mandatory. `[trading_systems_methods, p.640]` + `[carhart97]`.
8. **25-delta gold option risk-reversal skew** — different option-derived family than absolute IV (which GS-22 closed). Caution: data acquisition non-trivial — would require a data infra iter.
9. **State-machine-aware pre-val** (INFRA, GS-9 corollary; deferred).
10. **Microstructure / 30m / 15m / 1m intraday** — requires cTrader fetch infra iter first.
11. **(LOWER) Concede loop closure** if priorities 1-6 flat-line. PCBO/DSR with n_trials=25+ requires standalone Sh > 0.65 OR an IC-7 pair/triplet with both low static ρ AND stationary rolling-ρ AND strong-enough standalone Sharpes. Iter 025's IC-6 break (68% rolling, ρ +0.26 static) is the first IC-7-eligible pair confirmed in the gold loop; Priority 1 will tell us whether it's enough.

**Order**: 1→2→3→4→5→6→7→8→9→10→11. **CONSUMED**: iter 011-019 (GS-11..GS-19), iter 020 (GS-20 — 3-stream IC-7 macro-FX), iter 021 (GS-21 — DCOT MM contrarian materially weaker than commercials), iter 022 (GS-22 — option-implied-vol family is realized-vol-regime re-skin on gold), iter 023 (GS-23 — within-precious-metals basket extension is functionally identical to single-asset on position-vector level), iter 024 (GS-24 — cross-cluster PM-adjacent miner basket extension is gold-derivative, not orthogonal — closes all gold-complex-universe basket extensions), iter 025 (GS-25 — fixed-weight 60/40 cross-cluster GLD+BTC same-MR basket: ★ FIRST IC-6 break in 25 iters but Sharpe lift −0.13 due to cost+signal asymmetry; UNBLOCKS IC-7 Markowitz on GLD+BTC + asymmetric-per-leg-signals as next priorities).

## Broker tracks (every iter must declare which)

| track | instrument | costs | leverage | short-side | tax |
|---|---|---|:---:|:---:|---|
| **A — Pepperstone XAUUSD CFD** | XAU spot CFD | 8 bps spread + ~−1 bps/night swap | 1:200 | ✅ | none (offshore SCB Bahamas) |
| **B — Banco Inter ETF** | GLD/IAU long | ~100 bps FX RT + 25-40 bps EER | 1:1 | ❌ | **DARF 15%** monthly net profit |

Strategy may target **A only**, **B only**, or **both**; declare in hypothesis as `broker_track: ...` + per-track metrics. Inter (B) = LONG-ONLY + T+1 (no intraday); DARF model in `INFRASTRUCTURE.md`.

## Strategy menu (test broadly — one per iter, broker-tagged)

The mission says **"maximize strategies tested"**. Below is a wide menu
across families. Pick one per iter; mark closed paths in DEAD_ENDS.md
as you go. Add new candidates discovered during research.

### Strategy candidate menu (broad, 1 per iter — pick structurally novel direction)

Format: `# — TF|track|brief`. Closed entries have `(GS-N)` tag; full text in `DEAD_ENDS.md`.

- **Trend/momentum**: #3 EWMAC 1d|A+B `[systematic_trading, ch.11]`; #4 intraday breakout 1h/4h|A swap-free; #9 TSM 12-1 30-60d swing-ext; #10 3d post-breakout `[carhart97]`; #11 vol breakout `[volatility_trading]`. CLOSED #1-2 Donchian/EMA (GS-3).
- **MR**: CLOSED #5-5b RSI(2)<5±SMA (GS-1 / 003 IC-7 base); CLOSED #6-8 z-MR/Boll%B/Asia (GS-7).
- **Vol-regime**: CLOSED #13 σ_60>σ_252 (GS-10), σ_60<σ_252 (GS-11), σ_60<σ_252+SMA200 (GS-13); #14 Boll squeeze (caution GS-7); CLOSED #12 VIX PRIMARY (GS-4; OK IC-7 secondary).
- **Macro**: CLOSED #16 TIPS DFII10 falling 60d (GS-14 — ρ=0.52 vs iter 011 EXCEEDS IC-7); CLOSED #16b DXY-MA-slope 200d/20d on FRED DTWEXBGS (GS-15 — ρ=0.51 vs iter 014; macro-generic clock confirmed); #16c CFTC COT positioning extremes (PROMOTED iter 016+); CLOSED #15 DXY z-score down-cross (GS-5); CLOSED #17/17b XAU/XAG (GS-8/9).
- **Calendar/event**: CLOSED #18 pre-FOMC (GS-6); #19 month-end/opex (GS-6 cliff risk); #20 Indian wedding (swing-ext).
- **Cross-asset**: #21 SPY-GLD ρ flip `[leverage_for_the_long_run]`; #22 GDX/GLD divergence `[risk_parity, ch.7]`; #23 BTC-gold DD>−20%.
- **Composite/ML** (post-IC-7): CLOSED #24 Markowitz iter_003+iter_011 (GS-12); #25 AFML meta-label macro features; #26 HMM 2-state on (vol, DXY).

**Backlog**: COT/CFTC; CPI surprise; tick microstructure/jump (1m via cTrader fetch); Kalman trend `[ehlers, MAMA]`; AFML triple-barrier.

---

## Structural dead-ends (inherits sister loop cross-applicable closures)

See `DEAD_ENDS.md` for full text. Cross-loop closures inherited:

- Vol-target wrapper absorbs same-family overlays (don't wrap gold-vol with gold-vol-target)
- Cross-sectional ranking on survivorship-biased baskets (gold = single asset, N/A but watch miner baskets)
- Output regime gate = input regime gate (don't double-count VIX/regime signal)
- 50/50 composition only when Sharpes similar; use Markowitz proportional weighting
- Pre-val screen mandatory for overlay candidates (correlation pre-check)
- Modulation axes saturate at base ceiling — additive new streams beat modulation

Gold-specific dead-ends (1-line summaries; full text in `DEAD_ENDS.md`):

- **GS-1 (001/003)** RSI(p≤4)+SMA(N≤10) MR no-regime dead; SMA(200) rescue +Sh 3/3 trails bh.
- **GS-2 (001)** Track B FX cliff >15 tr/yr drains CAGR; DARF asymmetry compounds.
- **GS-3 (002/003)** Single-mech standalone trails bh drift; bidir gld_long doubles MDD. Path = IC-7.
- **GS-4 (004)** VIX as PRIMARY trigger fails 2020+; OK as IC-7 secondary.
- **GS-5 (005)** DXY-z-down-cross−1 inverted on FX 2020+; LEVEL gate untested.
- **GS-6 (006)** Pre-FOMC drift +15 bps ~5× too weak vs 83 bps RT cost.
- **GS-7 (007)** z-MR single-asset cost-dominated; pre-val needs `mean_fwd_bps > 1.5 × spread_RT`.
- **GS-8 (008)** XAU/XAG MR non-stationary 2020+; inverted at |z|>2.
- **GS-9 (009)** Pair TF: bar-avg pre-val OVERESTIMATES state-machine gross under timeout-spaced entries. Closes MR+TF for `|z|>kσ` commodity-spot.
- **GS-10 (010)** σ_60>σ_252 STANDALONE +Sh 3/3 BLOCKED trails-bench; inverse iter 011 = breakthrough.
- **GS-11 (011)** σ_60<σ_252 STANDALONE: 1st +Sh-bench-beat 2/3 ds; gld weak; MARGINAL 50. Unblocks IC-7.
- **GS-12 (012)** IC-7 Markowitz(003+011) MARGINAL 50; cannot lift DSR<0.05 from 2 DSR-failing bases (combined Sh ≤ √(S_A²+S_B²) ≈0.567 < deflator-cleared 0.65).
- **GS-13 (013)** iter 011 + SMA(200): Sh +0.48→+0.51 (Δ+0.03), DSR p 0.275→0.253 still>0.05. Bear-leak is MDD-problem not Sharpe; vol-regime family ceiling on gld_long ≈ +0.55.
- **GS-14 (014)** DFII10 falling 60d: +Sh 3/3 (0.32/0.54/0.82) trails bh Δ −0.37/−0.50/−0.28; G6 Boot 0/3 fail. **ρ vs iter 011 = +0.52 on gld_long EXCEEDS IC-7 0.50** (rate-cycle feedback loop: same macro clock). Closes IC-7-on-gld_long via macro at lookback=60d. **Single-stream gold ceiling on gld_long ≈ Sh 0.55 regardless of family**.
- **GS-15 (015)** DXY-MA-slope falling 200d/20d trails bh Δ −0.44/−0.72/−0.75; gld MDD breaches; macro-generic same-clock confirmed (ρ vs iter 014 = +0.513). Score 17 = FAIL. Full text in DEAD_ENDS.md.
- **GS-16 (016)** IC-7 003+015 with ρ corrected to +0.22 (was freq-mismatch artifact): combined Sh trails 3/3, all kill criteria fired. ⚠️ SUPERSEDED by GS-17. Score 35.
- **GS-17 (017)** Briese canonical 70/30/50/156w COT: Sh +0.137/+0.310 trails; **★ ρ vs iter 003 = +0.003/−0.0002** — 1st sub-0.20 ρ pair at consistent daily, breaks GS-16 floor. Closes canonical thresholds. Does NOT close z-score / DCOT / COT+price overlay. Score 28.
- **GS-18 (018)** COT z-score (156w window) lifts canonical Sh +0.215 (gld 0.137→0.352); **ρ vs iter 003 = +0.013/+0.004 (2nd confirmation)**; standalone trails Δ−0.43; closes COT-standalone family ceiling ≈ Sh 0.35. Score 35.
- **GS-19 (019)** IC-7 003+018 Markowitz at full-sample tangency: combined Sh +0.458/+0.346, hits **99.7% of analytic √(S²A+S²B)=0.460** — first clean numerical confirmation of 2-asset tangency on gold; MDD 9.56/8.33% (loop-best 2-stream); DSR p 0.41/0.84 (n=19) — kill #3 fired. Closes 2-stream IC-7 path on iter 001-018 catalog. Score 35.
- **GS-20 (020)** 3-stream IC-7 Markowitz 003+018+015 on gld_long: combined Sh +0.4865/+0.4422 (93.6% of √(S²₀₀₃+S²₀₁₈+S²₀₁₅)=0.520); MDD 10.95/9.76% (xau loop-best EVER); DSR p 0.365/0.773 (n=20). **NEW failure mode**: IC-6 rolling-60d ρ on (003,015) = 21.9% PRIMARY (vs 20% limit); static ρ +0.17 average but drawdown regimes co-trigger RSI-MR + DXY-trend. Closes 3-stream IC-7 with macro-FX 3rd stream. Full text in DEAD_ENDS.md.
- **GS-21 (021)** DCOT money-manager z-score on gold post-2006: Sh +0.073/+0.277 trails; ρ vs iter 018 = +0.85 BOTH ds → MM and commercials same family at position level; "speculative bucket isolation" FALSIFIED. Closes DCOT MM contrarian standalone. Full text in DEAD_ENDS.md.
- **GS-22 (022)** CBOE GVZ implied-vol z-score gate on gold post-2009: Sh +0.246/+0.333 trails; **ρ vs iter 011 rolling 59.7% PRIMARY HARD (static +0.55)** → option-implied IV ≡ realized vol-regime family at position level. Closes option-implied vol family. Full text in DEAD_ENDS.md.
- **GS-24 (024)** 60/40 GLD+GDX cross-cluster (PM + miners) basket extension of iter 003: Sh +0.2022 BELOW iter003 alone (lift −0.098); **IC-6 ρ vs iter003 rolling = 94.9% PRIMARY** (only 1.9 pp better than GS-23 96.8%); ρ static +0.67. Ilmanen ch.10: miners ρ ~0.7-0.8 to spot gold (gold-loading dominates equity beta ~0.45). **Closes ALL gold-complex-universe basket extensions** (GDX/GDXJ/RGLD/SIL/SILJ/PPLT/SLV). Joins GS-23. Does NOT close: GLD+BTC/TLT/SPY-not-miners, futures A2, DCOT prod-merc. Full text in DEAD_ENDS.md.
- **GS-23 (023)** 60/40 GLD+SLV within-PM basket extension of iter 003: PRIMARY Sh +0.295 (Δ −0.137), MDD 9.19% loop-best, ALL 6/6 kills fired; **IC-6 ρ vs iter003 rolling 96.8% PRIMARY** → both metals above SMA(200) same times + RSI(2) dips same days. Closes within-precious-metals basket extensions; reinterprets sister-loop "every winner was multi-asset" as needing CROSS-CLUSTER. Full text in DEAD_ENDS.md.
- **GS-25 (025)** 60/40 GLD+BTCUSD cross-cluster fixed-weight basket of iter 003 RSI(2)+SMA(200) signal: **★ 1st IC-6 break in 25 iters — rolling-60d ρ vs iter003 = 68.1% PRIMARY (drop −27pp vs GS-23/24), static ρ +0.26**. Cross-cluster diversification empirically validated at position-vector level. However basket Sh +0.17 BELOW iter003 +0.30 (lift −0.13) due to BTC cost asymmetry (25 bps RT spread + −5 bps/night swap, ~3× gold's per-leg) + signal asymmetry (BTC standalone post-cost Sh weak). 4/6 kills fired (#3 cross-cluster did NOT fire — historic first; #1, #2, #4, #5 fired); MDD corroborating 5.69% loop-best ever. **Closes fixed-weight 60/40 GLD+BTC same-MR-signal basket** but UNBLOCKS IC-7 Markowitz GLD+BTC tangency (proportional-Sharpe weighting) + asymmetric-per-leg-signal compositions as iter 026+ priorities. Full text in DEAD_ENDS.md.

---

## Binding constraints (mandate §1, §3, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C; this loop = Plano A reactivation research, not deploy)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]` for every decision
- **7-gate battery** mandatory cross-dataset
- **DSR n_trials cumulative** — increment in frontmatter each iter
- **Cost model mandatory**: Pepperstone XAUUSD CFD baseline = spread 8 bps round-trip + swap −1 bps/night per lot. Intraday-close = swap-free. Justify deviations.
- **Benchmark**: XAUUSD buy-hold (or GLD ETF for gld_long dataset)
- **Day/swing horizon**: mean hold ≤ 5 trading days. If longer, justify explicitly + flag as "swing-extended"
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green**
- **Max 2 h wall-time** per iteration
- **NEVER commit to git** — the shell `run_loop.sh` handles it
- **Do NOT touch sister loop** (`studies/strategy_hunt_loop/`) — it runs in parallel
