---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 72
winners_found: 0
status: iterating
latest_iteration: "072-2026-04-25-1633"
cumulative_n_trials: 4348
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
| **1** | **069** | 🥇 STRONG | **90** | `iter064_vix_inner_w_calm005_stress020_vix20` | Faber 2007 + `[stocks_on_the_move, p.21-30]` + iter 068 KILL I | TIES iter 064; 1/9 KILLS A; 7/7×3; DSR<0.05×3; 4/5 winner |
| **1** | **070** | 🥇 STRONG | **90** | `iter064_t10y3m_cont_alpha025_lb1260_w005_020` | `[advances_fin_ml, ch.17-18]` + Estrella-Mishkin 1998 + Faber 2007 | TIES iter 064/069; 4/11 KILLS A/F/H/I; 7/7×3; continuous T10Y3M ≈ binary VIX |
| **1** | **071** | 🥇 STRONG | **90** | `iter064_plus_spy_mr_rsi2_th10_w005` | `[algo_trading_chan, p.95, p.153-154]` + Connors-Alvarez 2009 + Lo-MacKinlay 1988 | 4-way TIES iter 064/069/070; 2/10 KILLS A/G; 7/7×3; calm-aggr 3rd stream KILL D vindicated cross-cfg cross-ds |
| **5** | **072** | 🥇 STRONG | **85** | `iter064_vix_cond_calm010_stress005` | `[algo_trading_chan, p.95, p.153-154]` + Whaley 2009 + Connors-Alvarez 2009 | TIES iter 058; 6/10 KILLS; KILL E inverted (r_064 calm-defensive); regime-cond 3rd-stream axis closed |
| **5** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 | 7/7×3; HYG carry; CAGR-dilutive (replaced in iter 064) |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 072 — 2026-04-25 — iter064-vix-cond-r-mr-allocation (🥇 STRONG, 85/100, ties iter 058 at TOP-K #5; regression from joint TOP-K #1 of 90)
- **Hypothesis:** VIX-binary regime-conditional allocation of validated calm-aggressive r_mr (iter 071) on iter 064 base — composes iter 069 classifier + iter 071 r_mr (direction #1 from iter 071 final).
- **Citations:** `[algo_trading_chan, p.95, p.153-154, ch.6]` + Whaley 2009 JPM DOI 10.3905/JPM.2009.35.3.098 + Bekaert-Hoerova 2014 SSRN 2294327 + Connors-Alvarez 2009 + Faber 2007 SSRN 962461 + iter 064/071 final reports.
- **Scope:** 4 cfgs sweep w_calm × w_stress ∈ {(0.10,0.00), (0.15,0.00), (0.10,0.05), (0.20,0.00)}; 3 datasets; RSI fixed at iter 071 best (10); vix_threshold=20.
- **Result:** Best cfg `iter064_vix_cond_calm010_stress005` — S edu/spy/ndx 1.2300/1.3502/1.3912 (Δ064 +0.013/+0.019/+0.016 KILL A 3/3 under +0.02, Δ071 −0.004/+0.001/+0.001 KILL C 3/3), CAGR 9.08/9.57/9.72% (edu BELOW 9.18% unlock by 10bps KILL B), MDD 16.33/14.34/13.77% (Δ064 −0.94 to −0.99pp tighter), gates 7/7/7×3, PBO 0.03/0.23/0.32, DSR p=0.0333 spy (n=4348), G7=0pp×3, robustness 9/9, 16/16 TDD. **KILL E INVERTED 3/3**: r_072 calm_S/stress_S < 1.0; r_064 calm 1.04-1.07 < stress 1.48-1.95 — **iter 064 base itself calm-defensive at bar level**. All 4 cfgs score 85 (Pareto-flat). Winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85; 6/10 KILLS A+B+C+D+E+I.
- **Lesson:** STRUCTURAL CLOSURE of regime-conditional 3rd-stream allocation on iter 064. KILL E inversion reveals iter 064 base is CALM-DEFENSIVE at bar level — up-weighting r_mr in calm regime concentrates exposure in iter 064's WORST conditional segment. Static (iter 071) > regime-cond (iter 072) because uniform captures iter 064 stress-S (1.95) AND r_mr calm-S (0.82) additively. **5-iter pattern (064/068/069/070/071/072) PROVES 90 ceiling is hard-anchored in iter 064 base, NOT mechanism choice**. ALL 5 regime-allocation axes CLOSED. **Direction #2 (fresh higher-CAGR anchor, NOT iter 046 family) is now ONLY remaining structural lever.** See `iterations/072-*/`.

### 071 — 2026-04-25 — iter064-plus-spy-mr-rsi2 (🥇 STRONG, 90/100, 4-way TIES iter 064/069/070 for joint TOP-K #1)
- **Result:** Best cfg `iter064_plus_spy_mr_rsi2_th10_w005` — S edu/spy/ndx 1.2339/1.3491/1.3901 (Δ064 +0.016/+0.018/+0.015 KILL A 3/3), CAGR 9.27/9.76/9.93%, MDD 16.41/14.67/14.11%, gates 7/7/7×3, PBO 0.08/0.25/0.31, DSR p=0.0335 spy (n=4344), G7 0pp×3, robustness 9/9, 15/15 TDD. KILL D **vindicated** (r_mr calm S 0.82/0.88/0.80 > stress 0.68/0.70/0.70 on 3/3); KILL G fires (corr=0.999). winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 2/10 KILLS A+G.
- **Lesson:** Calm-aggressive 3rd stream thesis EMPIRICALLY VINDICATED but saturates at 90 — composition's CAGR ceiling anchored in iter 046+r_qqqt. See `iterations/071-*/`.

### 070 — 2026-04-25 — iter064-t10y3m-cont-inner-weight (🥇 STRONG, 90/100)
- **Result:** S edu/spy/ndx 1.21/1.32/1.36 (Δ064 −0.003/−0.011/−0.018 KILL A 3/3), CAGR 9.69/10.23/10.39%, gates 7/7/7, DSR p=0.0435 spy (n=4340), winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 4/11 KILLS A/F/H/I.
- **Lesson:** Continuous T10Y3M ≈ binary VIX — both saturate at 90 — closes regime-classifier-resolution × signal-orthogonality axis on iter 064. See `iterations/070-*/`.

### 069 — 2026-04-25 — iter064-vix-inner-weight-reverse (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 −0.005/−0.010/−0.020 KILL A 3/3, Δ068 +0.029-0.041 KILL I clean), CAGR 9.36/9.89/9.97%, gates 7/7/7, DSR p=0.0429 spy (n=4339), winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 1/9 KILLS A.
- **Lesson:** Reverse VIX inner-weight beats iter 068 original (KILL I generalises) but doesn't lift Sharpe above iter 064 static. Closes VIX-binary-inner-weight-swap BOTH DIRECTIONS at 90. See `iterations/069-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Result:** S 1.17/1.28/1.33 (Δ064 −0.04/−0.05/−0.05 KILL A 1/3), CAGR 9.53/10.04/10.30%, MDD +1.3-1.7pp vs 064, gates 6/6/6, DSR p=0.059 spy, winner=3/5; score 79; 1/9 KILLS I.
- **Lesson:** Engine clean but conditional-Sharpe ordering falsified — BOTH 064 sub-streams defensive in stress on 3/3. Reverse-swap is iter 069's natural test. See `iterations/068-*/`.

### 067 — 2026-04-25 — iter064-vol-target-cap10 (🥈 PROMISING, 74/100)
- **Result:** S 1.17/1.26/1.28 (Δ064 −0.05/−0.08/−0.09 KILL A 2/3), CAGR 7.61/7.93/7.93% (KILL D edu), gates 6/6/6, DSR p=0.076 spy, winner=3/5; score 74; 3/8 KILLS A+C+D.
- **Lesson:** MM σ⁻² cap-1.0 overlay on saturated 064 — mean-exposure cap drops mean faster than variance since inner stack already vol-managed. See `iterations/067-*/`.

### 066 — 2026-04-25 — meta-label-rf-iter064 (📉 NEAR_FAIL, 37/100)
- **Result:** S 0.66/0.81/0.65 (Δ064 −0.52 to −0.72), CAGR 4.10/4.54/3.28% KILL D, AUC 0.50 KILL H 3/3, gates 5/6/5, DSR p=0.85 ndx, winner=1/5; score 37; 5/8 KILLS A+B+C+D+H.
- **Lesson:** Bar-level 1-day sign of Markowitz-saturated composite informationally null regardless of model class — extends iter 013 LR closure to tree models. See `iterations/066-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100)
- **Result:** S 1.12/1.19/1.23 (Δ064 −0.10/−0.14/−0.14 KILL A 2/3), CAGR +1.47-1.63pp vs 064, gates 6/6/6, DSR p=0.114 spy, winner=3/5; score 74; 2/7 KILLS A+C.
- **Lesson:** Closes calm-cond ext-lev at 1.5×/borrow=rf+25bps — iter 060 Sharpe-convention closure generalises. See `iterations/065-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-**072**. **iter 064 still TOP-K #1 STRONG 90 (4-WAY TIED with iter 069/070/071), 0/7 KILLS.** iter 072 (VIX-binary regime-conditional r_mr allocation on iter 064) → 85, 6/10 KILLS A+B+C+D+E+I; KILL E **INVERTED** (r_064 itself calm-defensive at bar level, calm_S 1.04-1.07 < stress_S 1.48-1.95). **5-iter pattern (064/068/069/070/071/072) PROVES 90 ceiling hard-anchored in iter 064 base's calm-defensive bar-level distribution, NOT mechanism choice** — regime reweighting / continuous regime / static 3rd stream / regime-conditional 3rd stream all saturate or regress. **11-axis-closed strict LOCAL OPTIMUM**: saved-stream-pair / internal-LETF / weight-sweep / output-VIX / calm-cond-ext-lev / bar-meta-label / σ⁻² cap / VIX inner-weight BOTH dirs / continuous T10Y3M inner weight / calm-aggressive RSI(2) 3rd stream / **VIX-binary regime-cond 3rd-stream allocation**.

### Iter 073 candidates (5-iter pattern on iter 064 base proves 90 ceiling is base-anchored, NOT mechanism-choice; ALL regime-allocation axes on iter 064 base CLOSED; ONLY remaining structural lever is fresh higher-CAGR base anchor)

- **#1 Fresh higher-CAGR anchor (NOT iter 046 family) — RECOMMENDED, ONLY remaining structural lever.** 5-iter pattern (064/068/069/070/071/072) provably PROVES iter 064 base anchor is binding constraint. Sub-options: (a) NTSX 90/60 leveraged stack at higher vol target ~14% (Asvanunt-Richardson 2017); (b) **vol-targeted SPY+TLT at HIGHER target with TSM overlay (Moreira-Muir 2017 + Asness-Moskowitz-Pedersen 2013)** — RECOMMENDED sub-option, lowest implementation cost (reuses iter 016/024 infra); (c) multi-asset Hurst-regime trend follower 5-asset basket (Mandelbrot 1971, Peters 1991, Lo-MacKinlay 1988). Predicted 70-95, high variance; cost ~3-5 iterations to build new anchor before composing iter 071's r_mr.
- **#2 Forward 5-day Sharpe meta-label on iter 064** — different cadence than bar-level regime; ~120 flips/yr at weekly horizon. Predicted 65-85, lower priority (same iter 064 base constraint).
- **#3 Plano C sleeve** (≤70 ceiling). **#4 CRSP/Norgate** (data budget).

DEAD-LETTER (all iter 064 base regime-allocation axes / saved-stream-pairs / 046-family / HYG / HMM-2 / FX carry / MTUM-QUAL-USMV not cached / cross-sectional mom Tiingo / broader-region VRP 5-leg / ext-lev / commodity TSM basket / eq075 / internal-LETF / Faber QQQ-200d / VIX-calm-cond ext lev / bar-level RF meta-label / σ⁻² cap-1.0 overlay / VIX-cond inner-weight BOTH DIRECTIONS / continuous T10Y3M z-score inner weight / Connors RSI(2) calm-aggressive 3rd stream / **VIX-binary regime-conditional 3rd-stream allocation**): see iters 045/047-072 entries.

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
- **iter 065-070 closures (compressed)**: 065 VIX-calm-cond ext lev 1.5× → 74 (2/7 KILLS); 066 RF meta-label → 37 (AUC~0.50, 5/8 KILLS, extends iter 013 closure to trees); 067 MM σ⁻² overlay cap=1.0 → 74 (3/8 KILLS, σ⁻² family saturates 74); 068 VIX inner-swap original → 79 (KILL I 3/3 — both sub-streams defensive in stress); 069 REVERSE VIX inner-swap → 90 TIES 064 (1/9 KILLS A; closes inner-swap BOTH DIRECTIONS at 90); 070 continuous T10Y3M z-score INNER weight → 90 TIES 064/069 (4/11 KILLS A/F/H/I; KILL J clean — T10Y3M orthogonal to VIX yet saturates 90). Decisively closes regime-classifier resolution × signal-orthogonality.
- **iter 071 (Connors RSI(2) MR calm-aggressive 3rd stream on 064; 4 cfgs)**: 90 TIES 064/069/070, 2/10 KILLS A/G. KILL D vindicated (r_mr calm S 0.82/0.88/0.80 > stress 0.68/0.70/0.70). Pareto-binding: w_mr=0.10 lifts Δ064>+0.02 but drops edu CAGR<9.18%. Closes calm-aggressive-3rd-stream axis at 90.
- **iter 072 (VIX-binary regime-conditional r_mr allocation on 064; 4 cfgs)**: 🥇 STRONG 85 — REGRESSION vs joint TOP-K #1 of 90. 6/10 KILLS A+B+C+D+E+I. Engine perfect (16/16 TDD, G7=0pp). **KILL E INVERTED 3/3**: r_064 itself calm-defensive at bar level (calm S 1.04-1.07 < stress 1.48-1.95). Best cfg edu CAGR 9.08% < 9.18% unlock (KILL B). Δ064 +0.013/+0.019/+0.016 KILL A 3/3; Δ071 ≈ 0 KILL C 3/3 (no benefit over static). **5-iter pattern (064/068/069/070/071/072) PROVES 90 ceiling hard-anchored in iter 064 base, NOT mechanism choice — ALL 5 regime-allocation axes closed**. Direction #2 (fresh higher-CAGR anchor) is now ONLY remaining lever.

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
