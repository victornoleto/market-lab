---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 71
winners_found: 0
status: iterating
latest_iteration: "071-2026-04-25-1606"
cumulative_n_trials: 4344
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
| **5** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 | 7/7×3; HYG carry; CAGR-dilutive (replaced in iter 064) |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 071 — 2026-04-25 — iter064-plus-spy-mr-rsi2 (🥇 STRONG, 90/100, 4-way TIES iter 064/069/070 for joint TOP-K #1)
- **Result:** Best cfg `iter064_plus_spy_mr_rsi2_th10_w005` — S edu/spy/ndx 1.2339/1.3491/1.3901 (Δ frozen +0.55/+0.45/+0.44, Δ064 +0.016/+0.018/+0.015 KILL A 3/3 under +0.02), CAGR 9.27/9.76/9.93% (Δ064 −0.21 to −0.24pp), MDD 16.41/14.67/14.11% (Δ064 tighter −0.6 to −0.9pp), gates 7/7/7×3, PBO 0.08/0.25/0.31, DSR p=0.0335 spy (n=4344), G7 0pp×3, robustness 9/9, 15/15 TDD. KILL D **vindicated cross-cfg cross-ds**: r_mr calm S 0.82/0.88/0.80 > stress 0.68/0.70/0.70 on 3/3. KILL G fires: corr(071,064_static)=0.999×3 (3rd stream inert). 4 cfgs sweep RSI∈{3,5,10}×w_mr∈{0.05,0.10}: th5_w005=90, th10_w005=90 (best by Sharpe-sum tiebreak), th5_w010=85 (KILL H edu 8.95%<9.18%), th3_w005=85; winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 2/10 KILLS A+G.
- **Lesson:** Calm-aggressive 3rd stream thesis EMPIRICALLY VINDICATED (KILL D clean 3/3 × 4 cfgs) but saturates at 90 ceiling. **4-iter pattern (064/069/070/071) confirms 90 ceiling anchored in iter 046+r_qqqt base's CAGR profile, NOT in mechanism choice** — regime reweighting / continuous regime / orthogonal 3rd stream all saturate at 90. Pareto-front binding: w_mr=0.10 lifts Δ064>+0.02 but drops edu CAGR below 9.18% unlock (KILL H). 90→95+ requires either (a) hierarchical regime allocation of validated r_mr or (b) fresh higher-CAGR anchor (NOT iter 046 family). See `iterations/071-*/`.

### 070 — 2026-04-25 — iter064-t10y3m-cont-inner-weight (🥇 STRONG, 90/100)
- **Result:** S edu/spy/ndx 1.21/1.32/1.36 (Δ frozen +0.53/+0.42/+0.40, Δ064 −0.003/−0.011/−0.018 KILL A 3/3, Δ069 ≈ 0 KILL K clean), CAGR 9.69/10.23/10.39%, MDD 17.09/14.87/14.12%, gates 7/7/7, DSR p=0.0435 spy (n=4340), G7=0pp 3/3, robustness 9/9, KILL J clean (T10Y3M orthogonal to VIX, corr 0.22-0.24); winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 4/11 kills A/F/H/I.
- **Lesson:** Continuous resolution AND macro-orthogonal signal both saturate at 90 — closes regime-classifier-resolution × signal-orthogonality axis on iter 064. iter 064 static `w=0.10` = global Sharpe-maximal under ANY single-axis regime-conditional inner-weight reweighting. See `iterations/070-*/`.

### 069 — 2026-04-25 — iter064-vix-inner-weight-reverse (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 −0.005/−0.010/−0.020 KILL A 3/3, Δ068 +0.029-0.041 KILL I clean), CAGR 9.36/9.89/9.97%, MDD 15.77/14.38/13.33% (Δ064 −1.5/−0.95/−1.42pp), gates 7/7/7, DSR p=0.0429 spy (n=4339), robustness 9/9; winner=4/5; score 1:25 2:25 3:15 4:5 5:15 6:5 = 90; 1/9 KILLS A.
- **Lesson:** Reverse VIX inner-weight beats iter 068 original direction (KILL I generalises) but doesn't lift Sharpe above iter 064 static. CLOSES VIX-binary-inner-weight-swap BOTH DIRECTIONS at 90 ceiling. See `iterations/069-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Result:** S 1.17/1.28/1.33 (Δ064 −0.04/−0.05/−0.05 KILL A 1/3), CAGR 9.53/10.04/10.30%, MDD 18.55/17.07/16.49% (+1.3-1.7pp vs 064), gates 6/6/6, DSR p=0.059 spy (n=4338); winner=3/5; score 1:25 2:19 3:10 4:5 5:15 6:5 = 79; 1/9 KILLS I.
- **Lesson:** Engine clean (G7=0pp, Σw≡1, 13/13 TDD) but conditional-Sharpe ordering falsified: BOTH 064 sub-streams (r_046 and QQQ_TREND) defensive in stress on 3/3. Reverse-swap is iter 069's natural test. See `iterations/068-*/`.

### 067 — 2026-04-25 — iter064-vol-target-cap10 (🥈 PROMISING, 74/100)
- **Result:** S 1.17/1.26/1.28 (Δ064 −0.05/−0.08/−0.09 KILL A 2/3), CAGR 7.61/7.93/7.93% (Δ064 −1.9/−2.0/−2.2pp KILL D edu), MDD 13/13/12%, gates 6/6/6, DSR p=0.076 spy (n=4337); winner=3/5; score 1:25 2:19 3:10 4:0 5:15 6:5 = 74; 3/8 KILLS A+C+D.
- **Lesson:** Moreira-Muir σ⁻² cap-1.0 overlay on saturated 064 hits same 74 ceiling as iter 065 — mean-exposure cap drops mean faster than variance since inner stack already vol-managed. See `iterations/067-*/`.

### 066 — 2026-04-25 — meta-label-rf-iter064 (📉 NEAR_FAIL, 37/100)
- **Result:** S 0.66/0.81/0.65 (Δ064 −0.52 to −0.72 KILL A 3/3), CAGR 4.10/4.54/3.28% KILL D, gates 5/6/5, DSR p=0.85 ndx (n=4336), AUC 0.50 KILL H 3/3; winner=1/5; score 1:0 2:17 3:0 4:0 5:15 6:5 = 37; 5/8 KILLS A+B+C+D+H.
- **Lesson:** Bar-level 1-day sign of Markowitz-saturated composite informationally null regardless of model class — extends iter 013 LR closure to tree models. See `iterations/066-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100)
- **Result:** S 1.12/1.19/1.23 (Δ064 −0.10/−0.14/−0.14 KILL A 2/3), CAGR 10.96/11.47/11.80% (Δ064 +1.47-1.63pp), gates 6/6/6, DSR p=0.114 spy (n=4335); winner=3/5; score 1:25 2:19 3:5 4:5 5:15 6:5 = 74; 2/7 KILLS A+C.
- **Lesson:** Closes calm-cond ext-lev at 1.5×/borrow=rf+25bps — iter 060 Sharpe-convention closure generalises to calm-only application. See `iterations/065-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-**071**. **iter 064 still TOP-K #1 STRONG 90 (NOW 4-WAY TIED with iter 069/070/071), 0/7 KILLS.** iter 071 (Connors RSI(2) MR + Chan p.95 momentum gate as calm-aggressive 3rd stream on iter 064) → 90, 2/10 KILLS A/G; KILL D **vindicated** (calm-aggressive thesis empirically confirmed cross-cfg cross-ds). The 90 ceiling now provably anchored in iter 046+r_qqqt base's CAGR profile (NOT mechanism choice) — confirmed across 4 fundamentally different structural mechanisms. **10-axis-closed strict LOCAL OPTIMUM**: saved-stream-pair / internal-LETF / weight-sweep / output-VIX / calm-cond-ext-lev / bar-meta-label / σ⁻² cap / VIX inner-weight BOTH dirs / continuous T10Y3M inner weight / **calm-aggressive RSI(2) 3rd stream**.

### Iter 072 candidates (064/069/070/071 4-way joint TOP-K #1; calm-aggressive-3rd-stream axis CLOSED but THESIS VINDICATED for composition with regime classifier; need either regime-conditional allocation of validated r_mr or fresh higher-CAGR anchor)

- **#1 Hierarchical 3-stream regime allocation: iter 064 base + r_mr from iter 071 with VIX (069) or T10Y3M (070) regime classifier**. RECOMMENDED — composes the 3 prior 90-tied iterations. r_mr (calm-aggressive, S calm 0.82-0.93 / stress 0.32-0.70) gets up-weighted in calm regime, zeroed in stress; iter 064 base stays defensive throughout. Predicted **75-92** if regime-conditional allocation amplifies r_mr's calm Sharpe over the unconditional 0.77-0.84. Risk: 6+ free params (regime threshold, calm-allocation, stress-allocation × 2 streams), overfit risk at n_trials=4344. Mitigation: pre-commit allocation rules from literature (Chan p.95 binary; Markowitz inverse-variance bounded).
- **#2 Fresh higher-CAGR anchor (NOT iter 046 family)** — cross-asset Hurst-regime trend; credit-spread regime as primary signal; single-asset levered base with embedded calm-aggr + defensive components. Predicted 70-95, high variance. High cost (5+ iterations to build).
- **#3 Forward 5-day Sharpe meta-label on 064** (~120 flips/yr; orthogonal cadence). Predicted 60-85.
- **#4 Plano C sleeve** (≤70). **#5 CRSP/Norgate** (data budget).

DEAD-LETTER (saved-stream-pairs / 046-family / HYG / HMM-2 / FX carry / MTUM-QUAL-USMV not cached / cross-sectional mom Tiingo / broader-region VRP 5-leg / ext-lev / commodity TSM basket / eq075 / internal-LETF / Faber QQQ-200d / VIX-calm-cond ext lev / bar-level RF meta-label / σ⁻² cap-1.0 overlay / VIX-cond inner-weight BOTH DIRECTIONS / continuous T10Y3M z-score inner weight / **Connors RSI(2) calm-aggressive 3rd stream on iter 064 base at small w_mr**): see iters 045/047-058/059/061/062/063/064/065/066/067/068/069/070/**071** entries.

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
- **iter 071 (Connors RSI(2) MR + Chan p.95 200d gate, calm-aggressive 3rd stream on 064; 4 cfgs RSI∈{3,5,10}×w_mr∈{0.05,0.10})**: 90 TIES 064/069/070 4-way TOP-K #1, 2/10 KILLS A/G. 7/7×3 gates, PBO 0.08-0.31, DSR p=0.0335 spy (n=4344), robustness 9/9, G7=0pp×3, 15/15 TDD. **KILL D vindicated cross-cfg cross-ds**: r_mr calm S 0.82/0.88/0.80 > stress 0.68/0.70/0.70 on 3/3 — calm-aggressive thesis EMPIRICALLY CONFIRMED. Δ064 Sharpe +0.016/+0.018/+0.015 KILL A 3/3 under +0.02. corr(071,064_static)=0.999×3 KILL G. Pareto-binding: w_mr=0.10 lifts Δ064>+0.02 but drops edu CAGR<9.18% (KILL H, score 85). **Closes calm-aggressive-3rd-stream axis on iter 064 at 90 ceiling**. 4-iter pattern (064/069/070/071) provably anchors 90 ceiling in iter 046+r_qqqt base's CAGR profile. 10-axis closed local optimum.

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
