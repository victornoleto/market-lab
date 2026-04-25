---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 65
winners_found: 0
status: iterating
latest_iteration: "065-2026-04-25-1341"
cumulative_n_trials: 4335
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
| **1** | **064** | 🥇 STRONG | **90** | `iter046_plus_qqq_trend_w010_lookback200` | Faber 2007 SSRN 962461 + `[stocks_on_the_move, p.21-30]` | **NEW TOP-K #1, breaks 85 ceiling**; 0/7 kills; 7/7×3; DSR <0.05×3; 1st-ever 4/5 winner conds + edu CAGR floor PASS without LETF |
| **2** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 + `[risk_parity, ch.5]` | 0/6 kills; 7/7×3; iter 046 + HYG carry (Sharpe-additive but CAGR-dilutive — REPLACED in iter 064) |
| **2** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Whaley + Sinclair | corr 0.41; 1st EVER 7/7×3 + DSR sub-0.05×3; 0/6 kills; preserved as 90% anchor in iter 064 |
| **4** | **053** | 🥇 STRONG | **84** | `iter037_plus_iter046_w070` | `[risk_parity, ch.5]` + Sinclair + Markowitz | 3-way tie; 3/3 CAGR (ndx +0.04pp); corr 0.95 Kill F PRE-FIRED; iter 037 anchor exhausted |
| **4** | **051** | 🥇 STRONG | **84** | `iter037_plus_iter026_w080` | `[risk_parity, ch.5]` + Sinclair + Markowitz | 4/5 winner conds + 3/3 CAGR floor; 25/19/5/15/15/5; DSR p=0.175 sole gap to 90 |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100, 2/7 KILLS A+C — REGRESSION −16)
- **Result:** Sharpe edu/spy/ndx 1.12/1.19/1.23 (Δ064 −0.097/−0.138/−0.144 KILL A 2/3 ≥0.10), CAGR 10.96/11.47/11.80% (Δ064 +1.47/+1.49/+1.63pp; spy gap −2.01→−0.51pp NOT CLEARED), gates 6/7×3, DSR worst-p 0.1140 (n=4335; tripled from iter 064's 0.0392, all 3 fail 0.05 cut), G7 0.000000pp×3, pct_calm 65/68/71%, avg_lev 1.33-1.35, winner_conds=3/5; score 1:25 2:19 3:5 4:5 5:15 6:5 = **74**.
- **Lesson:** **iter 060's Sharpe-convention closure GENERALIZES to calm-only application** — empirical drag 0.10-0.14 is 1.5-2× the calm-fraction-discounted prediction (0.06-0.08); calm regime contributes most of realised variance, blunting the calm-fraction discount. Closes "regime-conditional ext lev" axis at lev=1.5× / borrow=rf+25bps. iter 064's 90 is strict LOCAL OPTIMUM under linear/scalar transforms; iter 066 must use fundamentally different mechanism (meta-labeling). Citations: Hsiao-Williams 2017 + Whaley 2009 JPM + Frazzini-Pedersen 2014. See `iterations/065-*/`.

### Iters 015-064 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **064** (🥇 90 TOP-K #1, 0/7 KILLS, iter058-qqq-trend-substitution) S 1.22/1.33/1.38, CAGR 9.49/9.97/10.17% (1/3 floor — edu 1st-ever non-LETF unlock), MDD 17/15/15%, gates 7/7×3, DSR worst-p 0.0392 spy. **NEW TOP-K #1, breaks 85 ceiling held since iter 046.** Faber 2007 QQQ-200d-trend (S~0.80, CAGR~12-14%) at w=0.10 strictly Pareto-dominant over HYG_TSM (iter 058) for iter 046 anchor. Path 95+ = close spy (−2.01pp) or ndx (−5.18pp) CAGR floor.
- **063** (🥇 81, 1/6 KILLS A, iter058-internal-letf-iter041-only) S 1.17/1.26/1.35 (Δ058 −0.05/−0.09/−0.06 KILL A 3/3), CAGR 9.46/9.67/11.12% (1/3 floor — edu 1st unlock on 058 family), MDD 17.51/15.51/18.01%, DSR worst-p 0.0762 REGRESSED from 058's 0.0494 (ndx 0.0426 PASS only). **Internal-LETF axis EXHAUSTED across both Pareto branches** (037-anchor → 79; 058-anchor → 81). Drag per-unit-LETF-weight INVARIANT across base Sharpe regimes; Sharpe-headroom thesis FALSIFIED. Path 90+ → novel anchor (S≥1.20 ∧ CAGR≥12%) OR CAGR-additive 3rd stream (S≥0.7 ∧ CAGR≥9.5%) — **SOLVED in iter 064 via QQQ-200d-trend**.
- **062** (🥇 79, 1/6 KILLS B, iter037-upro-substitution-internal-letf) S 0.95/1.07/1.10, CAGR 16.26/17.08/19.07% (3/3 floor PASS, +1.3-2.1pp uplift vs 037), MDD 35.90/30.51/37.33%, DSR worst-p 0.263 REGRESSED vs 037's 0.222. **Internal-LETF on iter 037 anchor delivers SAME 79 — 4× replication of iter 037-family ceiling (037, 059, 061, 062). Vol decay + financing drag invariant under (a)(b)(c).**
- **061** (🥇 79, 1/6 KILLS B, iter037-eq075-plus-hyg-tsm) S 0.93/1.16/1.17, CAGR 13.85/15.98/18.57% (3/3 floor PASS), MDD 35.97/24.84/32.48%, DSR worst-p 0.341 REGRESSED vs 037's 0.222. **Closes iter 037-family weight-tuning**: canonical 0.60/0.45/0.45 is Sharpe-optimal; equity-overweight LOWERS Sharpe because bond/gold legs are Sharpe-positive contributors. ΔCAGR/ΔSharpe ≈ 16 pp/Sharpe-unit.
- **060** (🥇 79, 2/6 KILLS A+B, iter058-levered-150-futures-borrow) S 1.10/1.22/1.28, CAGR 11.7/12.2/12.6% (2/3 floor), MDD 25/21/20%, DSR worst-p 0.125. **Closes external-leverage axis on iter 058 at borrow > 0.5pp above rf**: rf=0 → absolute borrow is drag.
- **059** (🥇 79, 1/7 KILLS B, iter037-plus-hyg-tsm-w010) S 0.98/1.17/1.18, CAGR 13.0/14.5/16.5% (3/3 floor vs 058's 0/3), MDD 31/23/29%, DSR worst-p 0.268, corr 0.42. **Anchor substitution trades CAGR-floor for DSR-pass; saved-stream-pair Pareto bounded 79-85.**
- **058** (🥇 85 TOP-K #1 tied, 0/6 KILLS, hyg-credit-carry-3rd-stream) S 1.22/1.35/1.40, gates 7/7/7, DSR 0.049/0.034/0.026, CAGR 8.7/9.0/9.3% (0/3 floor), MDD 17/14/13%, corr 0.44. **3rd-stream-Sharpe thesis vindicated; CAGR floor 0/15 binding on iter-046 anchor.**
- **057** (🥈 64, commodity-tsm-basket-3leg) S 1.05/1.08/1.14, CAGR 8/8/8% (0/3 floor), DSR 0.223, corr 0.30. **Closes multi-commodity TSM 3rd-stream on iter 046; basket S 0.13-0.29 too low for Markowitz-positive.**
- **056** (🥈 74, iter046-levered-130) S 1.10/1.21/1.27, CAGR 10.8/11.2/11.6% (1/3 floor), DSR 0.10. **External 1.3× lev at 3.5% borrow closes external-lev axis on iter 046 at borrow ≥ 3%.**
- **055** (🥈 73, vrp-basket-5etf-cross-region) S 1.07/1.40/1.60, CAGR 5/5/6% (0/3 floor). **EFA/EEM hurt pre-GFC edu; iter 039 Pareto-opt at 76; broader-VRP axis closed.**
- **054** (🥉 47, tiingo-cross-sectional-12-1) S 0.655 < SPY 0.680, DSR 0.811, PBO=1.0. **DATA-LAYER closure: survivorship-biased Tiingo cache → closes all cross-sectional ranking until CRSP/Norgate.**
- **053** (🥇 84, iter037+iter046 w=0.70) S 1.03/1.19/1.22, CAGR 12.7/13.7/15.4 (3/3 floor), corr 0.93-0.96 Kill F pre-fired. **037-anchor saved-stream-pair Pareto = 84; path 90+ needs base edu S ≥ 1.20.**
- **052** (🥇 79, iter041+026 w=0.82) S 1.08/1.19/1.22, CAGR 11.6/12.0/14.0 (2/3, ndx FAIL), corr 0.37-0.45, Markowitz 0.0000. **iter 037 dominates iter 041 as anchor.**
- **051** (🥇 84, iter037+026 w_037=0.80) S 1.02/1.20/1.22, DSR 0.175/0.109/0.109, CAGR 12.4/13.5/15.5 (3/3 floor), corr 0.57-0.60. **1st 4/5 winner conds; Pareto bounded at 84.**
- **050** (🥇 78) 90/10 iter046+gold-TSM at Markowitz w*=0.10; edu DSR 0.044→0.050. **5 iter 046 axes closed.**
- **049** (🥉 59, 4/6 KILLS) gold TSM @ w=0.5; S Δ046 −0.30, DSR 0.32. **Markowitz dilution at unequal Sharpes; w*≈0.09 not 0.50.**
- **048** (🥇 83) VIX-output-gate on 046; S 1.20/1.29/1.34, DSR 0.043/0.056/0.044. Output regime gate dupes 044 input closure.
- **047** (🥇 79/84) 3-cfg w_041 sweep; best=50/50≡046; Bonferroni destroys G2.
- **046** (🥇 85 TOP-K, 0/6 KILLS) 50/50 iter041+iter039 ρ=0.41; S 1.20/1.32/1.38, DSR 0.041/0.042/0.031, gates 7/7/7, CAGR 9.16/9.45/9.76. **5pt gap to WINNER = CAGR floor only.**
- **045** (🥇 81) 50/50 iter037+iter039 ρ=0.587; superseded by 046.
- **042-044** (🥈 74-79) regime amp/freq/input perturbations on 041; DSR 0.168→0.189-0.240 regress; static-stack 84-ceiling = LOCAL DSR PLATEAU.
- **041** (🥇 84 prior TOP-K, regime-weights-vix) S 1.03/1.13/1.16, DSR 0.168 (1st static-stack escape from 037's 0.222); calm 0.70/0.40/0.40 (1.50×) / stress 0.30/0.55/0.55 (1.40×).
- **037-040** (🥇/🥈 69-79) 3-leg preserved-lev (037 used as 045 component, S 0.98/1.15/1.17 DSR 0.222) → +VIX gate (038, MDD-additive Sharpe-neutral) → 1.8× additive (036, ndx MDD breach) → 039 VRP basket (S 1.14/1.29/1.56, DSR 0.075/0.061/0.006, used as 045/046 component, VRP-family 76 ceiling) → vol-target on 039 (040, σ⁻² absorbs short-vol).
- **033-036** (🥈 72-77) 3-leg variants (bond-carry sleeve, IEF→TLT, GLD substitution); 77 ceiling asset-class-agnostic; edge = DIVERSIFICATION not bond-carry.
- **026-032** (🥇/🥈 54-79) VRP harvester family on iter 026 (stand-alone VRP T-bill + SPY put cs, S 1.05/1.07/1.09, ndx 1st 7/7 + 1st DSR PASS, 76 ceiling); +overlays (021 put-cs VRP overlay 79; 022 TOM modulator 54; 023 TSM 3-ETF vol-target 28; 024 bond-curve carry 72; 025 slow-EWMAC long-only 39; 027 N=3.5 lev 74); +VIX gates (028 const 71, 029 persist 71, 030 z-score 71); 031 AND-composite (76, 1st all-3 DSR<0.10); 032 layered 015+031 (72, anchor for kill F corr<0.85).
- **015-020** (🥇/🥈/🥉 39-79) static synthetic NTSX 90/60 (015, 77, 1st clearing +0.10 cross-ds); 016 60:40×MM vol-target (79, fixed×vol-target ADDITIVE); 017 12-1 regional N=3 (52, US Sharpe dominance); 018 funding-cost 016 replay (79, 100bps ≈ −0.07 Sharpe); 019 HMM stock-bond ρ (0, pre-val reject); 020 monthly put-spread tail hedge (79, long-gamma redundant w/ vol-target).

### Iters 001-014 (heavily compressed; full detail in iter dirs)

- **001-004** (NEAR_FAIL/FAIL): crash-protected LETF trend (35); Clenow ATR-risk-parity (17); Clenow adj-slope (7); single-asset σ⁻¹ (51).
- **005** (🥉 59) MM σ⁻² single-asset; first DSR edu PASS; single-asset ceiling +0.08-0.10.
- **006-008** (🥈 67/🥉 50/🥈 74) vol-managed SPY+TLT grid → 12-1 momentum overlay (regress) → vt15_L21_cap20 4/5 winner.
- **009-013** (🥈 ≤74) T10Y3M EMA overlays (smoothing destroys lead), 3-leg daily blend, weekly cadence (vol-targeting needs daily), LR meta-label (redundant with variance-scaling).
- **014** (❌ 0) EBP credit overlay pre-val; overlay family CLOSED.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed/closed: 002-005/007/009-014/017/019-**065**. **Iter 064 still TOP-K #1 STRONG 90, 0/7 KILLS.** Iter 065 attempted VIX-calm-conditional ext lev 1.5× on iter 064 → 74 PROMISING regression (−16). iter 060's Sharpe-convention closure GENERALIZES to calm-only application: empirical drag 0.10-0.14 absolute (1.5-2× the calm-fraction-discounted prediction). **Path to WINNER 95-100 is even narrower**: all linear/scalar transforms on iter 064 (saved-stream-pair recombination, ext lev, internal LETF, calm-conditional lev, weight sweep on QQQ_TREND output) close at score ≤ 84-90. iter 064's 90 is a strict LOCAL OPTIMUM in the iter 058-derived Pareto space.

### Iter 066 candidates (iter 064 still TOP-K #1; iter 065 closed calm-cond ext lev axis)

- **#1 Meta-labeling on iter 064** (RF / GBM classifier on rolling features → binary trade/cash gate per bar): structurally novel; iter 013 closed LR meta-label (redundant w/ variance-scaling) but tree-based with non-linear features untested. `[advances_fin_ml, ch.3]` canonical. **Predicted 85-95 if gate informative; 75-85 if noise. RECOMMENDED for iter 066** — most distinct from closed axes.
- **#2 Variance-targeting on iter 064** (σ_target=σ_064 dynamic sizing, nominal lev ≤ 1.0): 2nd-order CAGR uplift via compounding (Moreira-Muir 2017). iter 016/040 closed simpler bases. Predicted 85-92.
- **#3 Regime-conditional QQQ_TREND WEIGHT** (vary w_qqqt by VIX regime, not output lev): tests sub-component regime conditioning vs iter 060/065 output-lev closure. Predicted 88-93.
- **#4 QQQ-trend weight sweep w=0.15 or 0.20**: CAGR uplift ~0.5pp per 10%, won't close spy floor until w≈0.65 (Sharpe blows kill A). Predicted 88-92.
- **#5 Plano C sleeve** (≤ 70). **#6 CRSP/Norgate** (not feasible without budget).

DEAD-LETTER: saved-stream-pairs 037+026/041+026/037+046/041+039 (045/051/052/053 Pareto 79-85); 046-family 044/047-050; HYG 3rd stream (058 Pareto 85, 059=79); HMM-2; FX carry; MTUM/QUAL/USMV not cached; cross-sectional mom on Tiingo (054 data layer); broader-region VRP 5-leg (055=73); ext lev on 046 (056=74); commodity TSM basket (057=64); ext lev on 058 (060=79); eq075 037 (061=79); internal-LETF on 037 (062=79); internal-LETF on 058 (063=81; axis EXHAUSTED both branches); QQQ-200d Faber sub at w=0.10 (064=90 TOP-K #1); **VIX-calm-cond ext lev 1.5× on 064 base, borrow 2.25% (065=74 — iter 060 closure GENERALIZES; empirical drag 1.5-2× predicted)**.

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
- **iter 064 NEW TOP-K #1 (QQQ-200d-trend Faber 2007 sub for HYG_TSM at w=0.10)**: 90 (0/7 KILLS, first 90+). qqqt standalone S 0.80-0.91 / CAGR 11.6-13.9%. Combined Δ058: Sharpe −0.005/−0.016/−0.027, CAGR +0.79/+0.96/+0.91pp, edu 9.49%>9.18% floor 1st-ever non-LETF unlock. Validates iter 063 diagnosis (iter 058 binding = CAGR floor not Sharpe). Closes single-asset-equity-trend-3rd-stream axis at w=0.10.
- **iter 065 (VIX-calm-conditional ext lev 1.5× on iter 064 base, borrow 2.25%)**: 74 PROMISING regression −16; 2/7 KILLS A+C. CAGR uplift +1.47/+1.49/+1.63pp (spy gap −0.51 not cleared) but Sharpe drag −0.10/−0.14/−0.14 / DSR tripled 0.039→0.114 (all 3 fail 0.05). iter 060's Sharpe-convention closure GENERALIZES to calm-only application — empirical drag 1.5-2× calm-fraction-discounted prediction. iter 064's 90 confirmed as strict LOCAL OPTIMUM under linear/scalar transforms.

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
