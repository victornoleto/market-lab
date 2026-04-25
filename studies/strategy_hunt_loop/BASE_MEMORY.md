---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 70
winners_found: 0
status: iterating
latest_iteration: "070-2026-04-25-1540"
cumulative_n_trials: 4340
---

# Strategy Hunt Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra: `INFRASTRUCTURE.md`.

---

## Mission

Find ONE trading strategy that:

1. **Beats SPY 1x buy-hold Sharpe by ≥ 0.10** on real data
2. **Passes the 7-gate battery** per `WINNER_CRITERIA.md` cross-dataset
3. **Is not a minor variation** of a known dead-end

Winner criteria live in `studies/strategy_hunt_loop/WINNER_CRITERIA.md`.
Dead ends that must NOT be re-tried live in
`studies/strategy_hunt_loop/DEAD_ENDS.md`.

**Hard context**: project is in mandate §1 **MAINTENANCE 100% Plano C**.
Even if this loop finds a winner, deployment requires a separate signed
override per mandate §7. Loop produces CANDIDATES, not live positions.

---

## Winners found

None yet. When found, append yaml block with iteration/hypothesis/config/score/datasets_passing/citation_primary/iteration_dir (template in `PROMPT.md`).

---

## Top-K ranked (best across all iters, by score)

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| **1** | **064** | 🥇 STRONG | **90** | `iter046_plus_qqq_trend_w010_lookback200` | Faber 2007 + `[stocks_on_the_move, p.21-30]` | TOP-K #1 (joint); 0/7 kills; 7/7×3; DSR<0.05×3; 4/5 winner; static `w=0.10` Sharpe-maximal |
| **1** | **069** | 🥇 STRONG | **90** | `iter064_vix_inner_w_calm005_stress020_vix20` | Faber 2007 + `[stocks_on_the_move, p.21-30]` + iter 068 KILL I | TIES iter 064; 1/9 KILLS A; 7/7×3; DSR<0.05×3; 4/5 winner; MDD −1 to −1.5pp vs 064 |
| **1** | **070** | 🥇 STRONG | **90** | `iter064_t10y3m_cont_alpha025_lb1260_w005_020` | `[advances_fin_ml, ch.17-18]` + Estrella-Mishkin 1998 + Faber 2007 | TIES iter 064/069; 4/11 KILLS A/F/H/I; 7/7×3; DSR<0.05×3; 4/5 winner; continuous T10Y3M ≈ binary VIX |
| **4** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 | 7/7×3; HYG carry; CAGR-dilutive (replaced in iter 064) |
| **4** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Sinclair | 1st 7/7×3 + DSR<0.05×3; iter 064's 90% anchor |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 070 — 2026-04-25 — iter064-t10y3m-cont-inner-weight (🥇 STRONG, 90/100, TIES iter 064 AND iter 069 for joint TOP-K #1)
- **Result:** S edu/spy/ndx 1.2144/1.3199/1.3578 (Δ frozen +0.53/+0.42/+0.40, Δ064 −0.003/−0.011/−0.018 KILL A 3/3, Δ069 +0.002/−0.002/+0.002 KILL K clean — TIES iter 069), CAGR 9.69/10.23/10.39% (edu unlock 9.69%>9.18%), MDD 17.09/14.87/14.12%, gates 7/7/7, DSR worst-p 0.0435 spy (n=4340), G7=0pp (3/3), robustness 9/9, corr(070,064) 0.996 KILL F 3/3, mean_w_qqqt 0.143-0.146 KILL I 3/3 (z mean −0.5 to −0.6, post-2009 curve compression), flips/yr 148-169 KILL H (continuous gate definitional), corr(z, VIX_lag) 0.22-0.24 KILL J clean — T10Y3M genuinely orthogonal to VIX, winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 4/11 kills (A/F/H/I; B/C/D/E/G/J/K clean).
- **Lesson:** STRUCTURAL CLOSURE of regime-classifier resolution × signal-orthogonality on iter 064 inner weight. Continuous resolution doesn't help (Δ069≈0 on 3/3); macro-orthogonal signal doesn't help (KILL J clean yet saturates at 90). iter 064 static `w=0.10` = global Sharpe-maximal under ANY single-axis regime-conditional inner-weight reweighting (binary equity-vol OR continuous macro-forward). 90→95+ requires calm-aggressive 3rd stream / hierarchical (VIX×T10Y3M) HMM / fresh anchor. See `iterations/070-*/`.

### 069 — 2026-04-25 — iter064-vix-inner-weight-reverse (🥇 STRONG, 90/100, TIES iter 064 for TOP-K #1)
- **Result:** S edu/spy/ndx 1.21/1.32/1.36 (Δ frozen +0.53/+0.42/+0.40, Δ064 −0.005/−0.010/−0.020 KILL A 3/3, Δ068 +0.038/+0.041/+0.029 KILL I clean), CAGR 9.36/9.89/9.97% (edu unlock preserved), MDD 15.77/14.38/13.33% (Δ064 −1.5/−0.95/−1.42pp), gates 7/7/7, DSR worst-p 0.0429 spy (n=4339), mean_w_qqqt 0.094-0.102, robustness 9/9, winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 1/9 KILLS A only.
- **Lesson:** iter 068's KILL I lesson generalises at blend level (reverse beats original 3/3) but does NOT lift Sharpe above iter 064 static `w=0.10`. CLOSES inner-weight-swap axis BOTH DIRECTIONS at 90 ceiling: in stress BOTH r_046 and r_qqqt have higher Sharpe → differential noise → regime reallocation Sharpe-flat. See `iterations/069-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Result:** S 1.17/1.28/1.33 (Δ064 −0.04/−0.05/−0.05 KILL A 1/3), CAGR 9.53/10.04/10.30%, MDD 18.55/17.07/16.49% (+1.3-1.7pp vs 064), gates 6/6/6, DSR worst-p 0.059 spy (n=4338), winner=3/5; score 1:25 2:19 3:10 4:5 5:15 6:5 = 79; 1/9 KILLS I.
- **Lesson:** Engine clean (G7=0pp, Σw≡1, 13/13 TDD) but conditional-Sharpe ordering falsified: QQQ_TREND stress S>calm on 3/3 (200d-SMA defensive), r_046 stress S>calm on 3/3. Both 064 sub-streams structurally defensive in stress → reverse-direction swap is iter 069's natural test. See `iterations/068-*/`.

### 067 — 2026-04-25 — iter064-vol-target-cap10 (🥈 PROMISING, 74/100)
- **Result:** S 1.17/1.26/1.28 (Δ064 −0.05/−0.08/−0.09 KILL A 2/3), CAGR 7.61/7.93/7.93% (Δ064 −1.9/−2.0/−2.2pp KILL D edu), MDD 13/13/12%, gates 6/6/6, DSR worst-p 0.076 spy (n=4337), winner=3/5; score 1:25 2:19 3:10 4:0 5:15 6:5=74; 3/8 KILLS A+C+D.
- **Lesson:** Moreira-Muir σ⁻² cap-1.0 overlay on saturated 064 hits same 74 ceiling as iter 065's +1.5× calm-lev — mean-exposure cap (0.88) drops mean faster than variance since inner stack already vol-managed. See `iterations/067-*/`.

### 066 — 2026-04-25 — meta-label-rf-iter064 (📉 NEAR_FAIL, 37/100)
- **Result:** S 0.66/0.81/0.65 (Δ064 −0.56/−0.52/−0.72 KILL A 3/3), CAGR 4.10/4.54/3.28% KILL D, gates 5/6/5, DSR worst-p 0.85 ndx (n=4336), AUC 0.50 KILL H 3/3, winner=1/5; score 1:0 2:17 3:0 4:0 5:15 6:5=37; 5/8 KILLS A+B+C+D+H.
- **Lesson:** Bar-level 1-day sign of Markowitz-saturated composite informationally null in standard regime/vol/momentum canon regardless of model class — extends iter 013 LR closure to tree models. See `iterations/066-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100)
- **Result:** S 1.12/1.19/1.23 (Δ064 −0.10/−0.14/−0.14 KILL A 2/3), CAGR 10.96/11.47/11.80% (Δ064 +1.47/+1.49/+1.63pp), gates 6/6/6, DSR worst-p 0.114 spy (n=4335), winner=3/5; score 1:25 2:19 3:5 4:5 5:15 6:5=74; 2/7 KILLS A+C.
- **Lesson:** iter 060 Sharpe-convention closure generalises to calm-only application — closes regime-conditional ext-lev at lev=1.5× / borrow=rf+25bps. See `iterations/065-*/`.

### Iters 001-064 (heavily compressed; full detail in `iterations/NNN-*/`)
- **064** (🥇 90 TOP-K #1, 0/7 KILLS, iter058-qqq-trend-sub) S 1.22/1.33/1.38, CAGR 9.49/9.97/10.17%, MDD 17/15/15%, 7/7×3, DSR 0.039 spy. Faber QQQ-200d at w=0.10 Pareto-dominates HYG_TSM. Path 95+ = close spy/ndx CAGR floor.
- **058-063** (79-85): 058 (🥇 85 prior TOP-K, hyg-credit-carry, 3rd-stream-S vindicated, CAGR 0/3 floor); 059-063 anchor/lev/eq075/internal-LETF saturate 79-81 (Internal-LETF axis exhausted both branches; SOLVED in 064 via QQQ-200d).
- **046, 051-057** (64-85): 046 (🥇 85 prior TOP-K, 50/50 iter041+iter039 ρ=0.41, 7/7×3, 5pt gap = CAGR floor); 051-053 (84 saved-stream-pair Pareto cap, Kill F corr 0.93-0.96); 054 cross-sect Tiingo CRSP-blocked; 055-057 VRP 5-leg / ext-lev / commodity all 64-74.
- **037-050** (69-83): 037-040 3-leg preserved-lev / VIX / VRP-basket / σ⁻²; 041 (🥇 84, regime-weights-vix); 042-050 regime-perturb / Pareto / output-gate / Markowitz dilution. **Static-stack 84 ceiling = LOCAL DSR PLATEAU**.
- **026-036** (54-79): VRP harvester family on 026 (76 ceiling, ndx 1st 7/7); +overlays / +VIX gates / AND / layered; 033-036 3-leg variants (77 ceiling asset-class-agnostic).
- **015-025** (39-79): 015 static NTSX 90/60 (77, 1st +0.10); 016 60:40×MM (79 additive); 017-021 12-1 / ρ-overlay / options closures; 022-025 TOM / TSM / bond-carry / EWMAC closures.
- **001-014**: 001-005 single-asset LETF trend / Clenow ATR / σ⁻¹ / σ⁻² (5 first DSR edu pass); 006-013 vol-managed SPY+TLT / 12-1 / weekly / LR meta-label; 014 EBP credit (overlay family closed).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed/closed: 002-005/007/009-014/017/019-**070**. **iter 064 still TOP-K #1 STRONG 90 (now TIED with iter 069 AND iter 070), 0/7 KILLS.** iter 070 (continuous T10Y3M z-score inner weight on 064) → 90, 4/11 KILLS A/F/H/I; KILL J clean (T10Y3M genuinely orthogonal to VIX). Both hypotheses about 90 ceiling falsified: continuous resolution AND orthogonal macro signal both saturate at 90. **iter 064 static `w=0.10` = global Sharpe-maximal under ANY single-axis regime-conditional inner-weight reweighting**. **9-axis-closed strict LOCAL OPTIMUM**: saved-stream-pair / internal-LETF / weight-sweep / output-VIX / calm-cond-ext-lev / bar-meta-label / σ⁻² cap / VIX inner-weight BOTH dirs / **continuous T10Y3M inner weight**.

### Iter 071 candidates (064+069+070 tied TOP-K #1; regime-classifier-on-existing-streams axis CLOSED comprehensively; need structurally novel ingredient OUTSIDE 9 closed axes)

- **#1 Calm-aggressive 3rd stream** (single-asset short-vol / convexity-buying / VRP harvest with HIGH calm Sharpe LOW stress Sharpe). Empirical evidence from iters 064/068/069/070: BOTH iter 046 and r_qqqt are STRUCTURALLY DEFENSIVE in stress; missing piece is calm-aggressive complement whose conditional Sharpe ordering is OPPOSITE. **NEWLY RECOMMENDED**. Predicted 75-92. Risk: short-vol blow-up dynamics require careful sizing.
- **#2 Hierarchical 3-state HMM on (VIX × T10Y3M)** — combine signals from iter 069/070 into joint regime model: calm-expansion / stress-expansion / stress-recession. Each state triggers different `(w_qqqt, w_046)` pair. Predicted 80-90, novel granularity. Risk: state-discovery overfit at n_trials=4340.
- **#3 Forward 5-day Sharpe meta-label on 064** (~120 flips/yr vs 700/yr iter 066, vs 148-169/yr iter 070 continuous). Predicted 60-85, high variance.
- **#4 Fresh anchor (not 046-derived)** — cross-asset trend on Hurst regime, credit-spread regime as primary signal. High cost.
- **#5 Plano C sleeve** (≤70). **#6 CRSP/Norgate** (data budget).

DEAD-LETTER (saved-stream-pairs / 046-family / HYG / HMM-2 / FX carry / MTUM-QUAL-USMV not cached / cross-sectional mom Tiingo / broader-region VRP 5-leg / ext-lev / commodity TSM basket / eq075 / internal-LETF / Faber QQQ-200d / VIX-calm-cond ext lev / bar-level RF meta-label / σ⁻² cap-1.0 overlay / VIX-cond inner-weight BOTH DIRECTIONS / **continuous T10Y3M z-score inner weight (macro-orthogonal signal × continuous resolution)**): see iters 045/047-058/059/061/062/063/064/065/066/067/068/069/**070** entries.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Carry + value composite AMP 2013 — orthogonal axes vs iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-014**: daily EMA/SMA × LETF; drawdown-stops; CAPE/EBP/VIX standalone; Clenow ATR/adj-slope ≤20-asset; single-asset σ⁻¹/σ⁻²; TSM overlay; T10Y3M EMA haircut; weekly/monthly cadence; meta-LR; EBP credit.
- **Iter 017/019-021**: 12-1 top-K=1 ≤3 regions; ρ stock-bond overlay; options-on-equity-leg on vol-managed stack.
- **Iter 022-025**: TOM modulator; TSM-PRIMARY ≤4-asset; bond-curve carry-as-ALLOCATION; slow-EWMAC long-only 6-asset.
- **VRP-harvester family 76 ceiling (026/031/039/040)**: CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral.
- **Static-stack 84-STRONG ceiling = LOCAL DSR PLATEAU**: iter 042 amp / 043 freq / 044 input all regress DSR.
- **Out-of-family composition VINDICATED**: iter 045 (81, ρ=0.58) → iter 046 (85, ρ=0.41) TOP-K #1; score scales inversely with corr.
- **iter 047-053 closures**: 5 iter-046 axes (047 Pareto-opt+Bonf; 048 output-VIX dupes 044; 049 low-S Markowitz; 050 DSR knife-edge); 037+026/041+026/037+046 saved-stream-pairs (84 ceil, Kill F corr 0.93-0.96). Saved-stream-pair ceiling = 85 (iter 046).
- **iter 054-057 closures**: 054 DATA LAYER (Tiingo survivorship → cross-sectional dead until CRSP); 055 broader-region VRP 5-leg (73<039's 76); 056 external lev on 046 (74); 057 commodity-basket (64, S 0.13-0.29 dilution).
- **3rd-stream-S binding (049/050/057/058)**: standalone S ≥ ~0.5 binding for Markowitz-positive at any practical weight, NOT corr alone. 058 vindicates with HYG_TSM (S~0.9, w=0.10) → 85.
- **iter 059-063 closures (037-anchor + leverage axes)**: 059 037+HYG → 79 (CAGR-DSR dual constraint: NO anchor 0-58 has S≥1.20 ∧ CAGR≥12%); 060 ext-lev 1.5× on 058 → 79 (rf=0 borrow=drag); 061 eq075 → 79 (canonical 0.60/0.45/0.45 Sharpe-optimal); 062 internal-LETF on 037 → 79 (drag invariant); 063 internal-LETF iter 041 within 058 → 81 (Sharpe-headroom thesis FALSIFIED). **Internal-LETF axis EXHAUSTED both branches** (037→79; 058→81).
- **iter 064 (TOP-K #1, Faber QQQ-200d sub for HYG_TSM at w=0.10)**: 90, 0/7 KILLS, first 90+. Combined Δ058: Sharpe −0.005-0.027, CAGR +0.79-0.96pp, edu 9.49%>9.18% (1st non-LETF unlock). Closes single-asset-equity-trend-3rd-stream axis at w=0.10.
- **iter 065 (VIX-calm-cond ext lev 1.5× on 064)**: 74, 2/7 KILLS. CAGR +1.5pp but Sharpe drag −0.10-0.14 + DSR tripled. Closes calm-cond ext-lev at 1.5×/borrow=rf+25bps.
- **iter 066 (RF meta-label on 064 daily, 5 feat)**: 37 NEAR_FAIL, 5/8 KILLS. AUC ~0.50 × 3 ds. Bar-level 1-day sign of Markowitz-saturated composite informationally null regardless of model class (extends iter 013 LR closure to trees).
- **iter 067 (MM σ⁻² overlay on 064, cap=1.0)**: 74, 3/8 KILLS. With iter 065, σ⁻² overlay family saturates at 74 ceiling cap∈[1.0, 1.5×]. Generalises iter 016's MM 79 to mean-exposure-cap-drag on saturated composite.
- **iter 068 (VIX-cond INNER swap on 064, calm 0.20 / stress 0.05)**: 79, 1/9 KILLS I. Cond Sharpe stress>calm on BOTH r_046 and r_qqqt (3/3) — both sub-streams structurally defensive in stress.
- **iter 069 (REVERSE VIX-cond INNER swap, calm 0.05 / stress 0.20)**: 90 TIES iter 064 TOP-K #1, 1/9 KILLS A. Reverse Δ068 +0.029-0.041 Sharpe (KILL I generalises) but Δ064 −0.005 to −0.020 (KILL A). **Closes binary-VIX inner-weight-swap BOTH DIRECTIONS at 90**: regime reallocation between two defensive streams Sharpe-flat.
- **iter 070 (continuous T10Y3M z-score INNER weight on 064, w∈[0.05, 0.20], α=0.25, lookback 5y)**: 90 TIES iter 064/069 TOP-K #1, 4/11 KILLS A/F/H/I (B/C/D/E/G/J/K clean). 7/7×3 gates, DSR 0.0435 spy (n=4340), robustness 9/9, G7=0pp 3/3, 11/11 TDD. Δ064 Sharpe −0.003/−0.011/−0.018 (KILL A); Δ069 ≈ 0 (KILL K clean — TIES iter 069 binary). corr(070,064) 0.996 KILL F. corr(z, VIX_lag) 0.22-0.24 KILL J clean — T10Y3M genuinely macro-orthogonal yet saturates at same 90. **Decisively closes regime-classifier-resolution × signal-orthogonality**: continuous AND orthogonal both fail to break 90. **iter 064 static `w=0.10` = global Sharpe-maximal under ANY single-axis regime-conditional inner-weight reweighting**. Now 9-axis-closed local optimum.

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **DSR n_trials cumulative** — increment `cumulative_n_trials` in this memory's frontmatter each iteration (add this iter's config count)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** — never reduce passing count (~796 collected post-iter-011, varies as iters add specs)
- **Max 2 h wall-time** per iteration
- **NEVER commit to git** — the shell `run_loop.sh` handles it
