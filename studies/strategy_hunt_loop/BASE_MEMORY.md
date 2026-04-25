---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 63
winners_found: 0
status: iterating
latest_iteration: "063-2026-04-25-1246"
cumulative_n_trials: 4333
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
| **1** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 + `[risk_parity, ch.5]` | NEW TOP-K (tie); 0/6 kills; 7/7×3; Sharpe ↑/MDD ↓ vs iter 046; vindicates 3rd-stream-Sharpe thesis |
| **1** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Whaley + Sinclair | TOP-K (tie); corr 0.41; 1st EVER 7/7×3 + DSR sub-0.05×3; 0/6 kills; CAGR 0/15 sole gap to 90 |
| **3** | **053** | 🥇 STRONG | **84** | `iter037_plus_iter046_w070` | `[risk_parity, ch.5]` + Sinclair + Markowitz | 3-way tie; 3/3 CAGR (ndx +0.04pp); corr 0.95 Kill F PRE-FIRED; iter 037 anchor exhausted |
| **3** | **051** | 🥇 STRONG | **84** | `iter037_plus_iter026_w080` | `[risk_parity, ch.5]` + Sinclair + Markowitz | **1st EVER 4/5 winner conds + 3/3 CAGR floor**; 25/19/5/15/15/5; DSR p=0.175 sole gap to 90 |
| **3** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley | 1st 84; DSR 0.222→0.168 escape; gate-mod axis closed (042/043/044); used in iter 046 |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 063 — 2026-04-25 — iter058-internal-letf-iter041-only (🥇 STRONG, 81/100, 1/6 KILLS A)
- **Result:** Sharpe edu/spy/ndx 1.17/1.26/1.35 (Δ frozen +0.49/+0.36/+0.39, Δ058 −0.05/−0.09/−0.06; kill A FIRES 3/3), CAGR 9.46/9.67/11.12% (1/3 floor — edu 9.46%>9.18% **1st time on iter 058 family**), MDD 17.51/15.51/18.01% (3/3≤ceiling), gates 6/6/7, DSR worst-p 0.0762 (REGRESSED from 058's 0.0494; ndx 0.0426 PASS only) (n=4333), G7 0.000000pp×3 + Markowitz outer 0/0/0 (perfect closed-form), winner=3/5; score 1:25 2:21 3:10 4:5 5:15 6:5 = **81**.
- **Lesson:** Internal-LETF axis EXHAUSTED across both Pareto branches (iter 037-anchor → 79 from 062; iter 058-anchor → 81 here). Drag is **per-unit-LETF-weight INVARIANT across base Sharpe regimes** — "Sharpe-headroom absorbs drag" thesis FALSIFIED. Path 90+ requires (a) novel anchor with Sharpe ≥ 1.20 AND CAGR ≥ 12% simultaneously (no iter 0-63 has this) OR (b) novel CAGR-additive 3rd stream beyond HYG with Sharpe ≥ 0.7 AND CAGR ≥ iter 046's 9.5%/yr. See `iterations/063-*/`.

### Iters 015-062 (compressed 1-line; full detail in `iterations/NNN-*/`)
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
- **048** (🥇 83) VIX-output-gate on 046; S 1.20/1.29/1.34, DSR 0.043/0.056/0.044. **Output regime gate dupes 044 input closure.**
- **047** (🥇 79 frozen/84 custom) 3-cfg sweep w_041 ∈ {0.5,0.65,0.8}; best=50/50 ≡ 046; Bonferroni destroys G2. **046's 50/50 IS Pareto-opt.**
- **046** (🥇 85 TOP-K #1, 0/6 KILLS) 50/50 iter041+iter039 ρ=0.41; S 1.20/1.32/1.38, DSR 0.041/0.042/0.031, gates 7/7/7, CAGR 9.16/9.45/9.76, MDD 18/15/15. **Out-of-family score scales inversely with corr; 5pt gap to WINNER = CAGR-floor only.**
- **045** (🥇 81) 50/50 iter037+iter039 ρ=0.587; DSR 0.096/0.057/0.050, score 81. **Out-of-family at moderate corr; superseded by 046.**
- **044** (🥈 74, vix+t10y3m composite) DSR 0.240 worst (deepest 041-perturb); 2-feat over-classifies + T10Y3M dilutes; **forces 045+ out-of-family**.
- **043** (🥇 79, hysteretic-vix-regime) DSR 0.168→0.189 regress; halving regime crossings adds regime-lag variance.
- **042** (🥈 74, combined-regime-lev-weights) DSR 0.168→0.216 regress; "compose × lev compounds DSR" FALSIFIED.
- **041** (🥇 84 prior TOP-K #1, regime-weights-vix) Sharpe 1.03/1.13/1.16, DSR 0.168 (1st static-stack escape from 037's 0.222), calm 0.70/0.40/0.40 (1.50×) / stress 0.30/0.55/0.55 (1.40×). 84 ceiling held until iter 046 → 85.
- **040** (🥈 69, vrp-basket-vol-target) MM σ⁻² on 039: ALL DEGRADE; σ⁻² ABSORBS short-vol harvest.
- **039** (🥇 76, basket 3etf 1/3-eq) Sharpe 1.14/1.29/1.56, DSR 0.075/0.061/0.006 (ndx loop-record), MDD 14/7/7%; VRP family ceiling 76 (CAGR 0/15 structural). **Used as iter 045/046 component**.
- **038** (🥇 79, regime-lev-vix) DSR 0.204 best static-stack > 0.20; binary VIX-gate MDD-additive + Sharpe-neutral.
- **037** (🥇 79, 3-leg preserved-lev) Sharpe 0.98/1.15/1.17, DSR 0.222, MDD 33/25/32%; AMP 2013 orthogonality. **Used as iter 045 component**.
- **036** (🥈 72) 3-leg additive 1.8×; +0.30 lev breaks ndx MDD; subsumed by 037.
- **035** (🥇 77) GLD substitution on 015; 77 ceiling asset-class-agnostic; edge was DIVERSIFICATION not bond-carry.
- **034** (🥈 72) 3-leg bond-carry sleeve; subsumed by 035.
- **033** (🥈 72) IEF→TLT swap; bond-duration is CAGR-MDD trade-off NOT Sharpe lever.
- **032** (🥈 72) Layered iter 015 + iter 031 VRP; corr_SPY=+0.97 put-spread amplifies eq DD; **anchor for iter 045/046 corr<0.85 kill F**.
- **031** (🥇 76) AND-composite R-1∧R-2 on iter 026; 1st all-3 DSR<0.10; CAGR floor structural to harvest_notional=1.0.
- **030** (🥈 71) Z-score VIX gate on 026; spy passes but edu/ndx fail. Closes z-score gates.
- **029** (🥈 71) Persistence VIX gate on 028; edu DSR 0.0251 record but worst-p 0.1003.
- **028** (🥈 71) Constant `VIX<35` filter on 026; closes constant-threshold gates.
- **027** (🥈 74) N=3.5 levered iter 026; rf-bonus diluted by leverage.
- **026** (🥇 76) Stand-alone VRP T-bill + SPY 5/10 put cs; ndx 1st 7/7 + 1st DSR PASS.
- **025** (📉 39) Slow-EWMAC long-only 6-asset; long-only sacrifices 50% trend premium.
- **024** (🥈 72) Bond-curve carry static stack; DSR worst 0.586 binds.
- **023** (📉 28) TSM 3-ETF vol-target; turnover dominates √3; HOP needs 67 markets.
- **022** (🥉 54) TOM eq:bd modulator; σ²_port quadratic absorbs calendar premium.
- **021** (🥇 79) Short put-cs VRP overlay on 016; DSR 0.217.
- **020** (🥇 79) Monthly put-spread tail hedge; long-gamma REDUNDANT with vol-target.
- **019** (❌ 0) HMM stock-bond ρ; pre-val rejects 3/3.
- **018** (🥇 79) Funding-cost 016 replay; 100bps ≈ −0.07 Sharpe.
- **017** (🥉 52) 12-1 regional rotation N=3; US Sharpe dominance.
- **016** (🥇 79) Static 60:40 × MM vol-target; fixed × vol-target ADDITIVE.
- **015** (🥇 77) Static synthetic NTSX 90/60 SPY+IEF; 1st iter clearing +0.10 cross-ds.

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

Consumed/closed: 002-005/007/009-014/017/019-**063**. **Iter 063 closed internal-LETF axis on iter 058 (DSR-clearing) anchor at preserved-equity weighting → 81 STRONG (1/6 KILLS A).** Internal-LETF axis is now EXHAUSTED across both Pareto branches: iter 037-anchor → 79 (062) and iter 058-anchor → 81 (063). The drag magnitude (−0.05 to −0.09 Sharpe) is **per-unit-LETF-weight INVARIANT across base Sharpe regimes**; "Sharpe-headroom absorbs drag" thesis falsified. Path 90+ requires (a) novel anchor with simultaneous Sharpe ≥ 1.20 AND CAGR ≥ 12% (no iter 0-63 has this) or (b) novel CAGR-additive 3rd stream beyond HYG with Sharpe ≥ 0.7 AND CAGR ≥ iter 046's 9.5%/yr.

### Iter 064 candidates (iter 058 = TOP-K #1 stays; internal-LETF axis exhausted)

- **#1 Higher-CAGR 3rd stream non-equity on iter 058 anchor** (NEW, informed by 063): break 85 ceiling requires 3rd stream with **S ≥ 0.7 AND CAGR ≥ iter 046's 9.5%/yr**. Candidates: QQQ-200d-trend (S~0.8, CAGR~12-14%, kill F risk corr~0.7); EFA+EEM TSM (S≤0.5, dilution); QMOM/VLUE/USMV (verify cache); gold-spread momentum. **Predicted 80-92 — RECOMMENDED for iter 064.**
- **#2 4-stream composite** (saved-stream-pair gen): iter 058 + iter 037 50/50, or 3-way + gold-TSM. Saved-stream-pair Pareto 79-85; predicted 83-89.
- **#3 Equity-UNDERWEIGHT iter 037 (0.45/0.55/0.55) + HYG_TSM**: opposite of 061. Predicted S↑ to 1.05-1.20 at cost of CAGR. Low priority post-062 (037-anchor 79 ceiling 4× structural).
- **#4 Plano C sleeve** (predicted ≤ 70). **#5 CRSP/Norgate delisted** (not feasible without budget).

DEAD-LETTER: 037+026/041+026/037+046/041+039 any weight (Pareto 79-85); 046-family 044/047-050; HYG_TSM 3rd stream on 046 at w=0.10 (058 = 85; family Pareto); HYG_TSM 3rd stream on 037 at w=0.10 with CANONICAL weights (059 = 79); HYG-041 substitution (UNTESTED, distinct); HMM-2; FX carry; MTUM/QUAL/USMV (not in cache); all 037-anchor saved-stream-pairs (045/051/053, ceil 84); 041 substitution for 037 (052); cross-sectional momentum on Tiingo cache (054 data layer); broader-region VRP 5-leg (055 at 73); external lev on 046 at borrow ≥ 3% (056 at 74); multi-commodity TSM basket on 046 (057 at 64); external lev on 058 at any borrow > 0.5pp above rf (060 at 79); iter 037 family equity-overweight at 0.75/0.40/0.40 + HYG_TSM at w=0.10 (061 at 79); internal-LETF UPRO substitution on iter 037 anchor at preserved-equity weighting (062 at 79); **internal-LETF UPRO substitution on iter 058 anchor (iter 041 sub-component only) at preserved-equity weighting calm 0.2333/0.6333/0.6333 + stress 0.10/0.65/0.65 (063 at 81; internal-LETF axis EXHAUSTED across both Pareto branches — drag invariant per-unit-LETF-weight regardless of base Sharpe regime)**.

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
- **iter 059 (037+HYG)**: CAGR-floor 3/3 PASS but DSR 0.268≥037's 0.222 → 79. **CAGR-DSR dual constraint**: NO anchor 0-58 has S≥1.20 AND CAGR≥12% simultaneously.
- **iter 060 (external lev 1.5× on 058 at 2.5% borrow)**: 79. rf=0 → absolute borrow is drag. Closes external-leverage axis on 058 at borrow > 0.5pp above rf.
- **iter 061 (eq075 + HYG_TSM)**: 79. eq075 standalone S 0.91 < 037's 0.96 (bond/gold are S-positive contributors). DSR REGRESSED to 0.341. **Closes 037-family weight-tuning** — canonical 0.60/0.45/0.45 is Sharpe-optimal.
- **iter 062 closure (internal-LETF on iter 037 anchor at 0.20/0.65/0.65)**: 79 (1/6 KILLS B). Sharpe LOWER on 3/3 (Δ −0.03/−0.09/−0.07) due to LETF vol decay + visible swap+expense drag. CAGR +1.3-2.1pp via diversifier overweight but DSR worst-p REGRESSED to 0.263. **Iter 037-anchor 79 ceiling 4× confirmed structurally invariant** under (a) weights, (b) lev type, (c) 3rd stream.
- **iter 063 closure (internal-LETF on iter 041 sub-component within iter 058 anchor)**: 81 (1/6 KILLS A — Sharpe regress 3/3). Drag magnitude (−0.05/−0.09/−0.06) MATCHES iter 062's (−0.03/−0.09/−0.07) — drag is **per-unit-LETF-weight INVARIANT across base Sharpe regimes**. Sharpe-headroom thesis FALSIFIED. CAGR +0.66/+0.66/+1.85pp; edu CAGR-floor unlocks 1st time on 058 family. DSR REGRESSED 2/3 (only ndx clears 0.0426). **Internal-LETF axis EXHAUSTED across both Pareto branches** (037 → 79; 058 → 81). Path 90+ requires novel anchor (S≥1.20 AND CAGR≥12%) OR novel CAGR-additive 3rd stream (S≥0.7 AND CAGR≥9.5%).

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
