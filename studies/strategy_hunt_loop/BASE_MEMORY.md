---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 52
winners_found: 0
status: iterating
latest_iteration: "052-2026-04-25-0822"
cumulative_n_trials: 4319
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
| **1** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Whaley + Sinclair | TOP-K; corr 0.41; 1st EVER 7/7×3 + DSR sub-0.05×3; 0/6 kills; CAGR 0/15 sole gap to 90 |
| **2** | **051** | 🥇 STRONG | **84** | `iter037_plus_iter026_w080` | `[risk_parity, ch.5]` + Sinclair + Markowitz | **1st EVER 4/5 winner conds + 3/3 CAGR floor**; 25/19/5/15/15/5; DSR p=0.175 sole gap to 90 |
| **2** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley | 1st 84; DSR 0.222→0.168 escape; gate-mod axis closed (042/043/044); used in iter 046 |
| **4** | **045** | 🥇 STRONG | **81** | `iter039_on_iter037_50_50` | `[risk_parity, ch.5]` + Sinclair | out-of-family 50/50 037+039; ρ=0.58; DSR 0.222→0.096; ndx 7/7; 0/6 kills; superseded by 046 |
| **5** | **038** | 🥇 STRONG | **79** | `regime_lev_vix_lt20_lo10_hi17` | `[advances_fin_ml, ch.17-18]` + MM 2017 | VIX-gated 1.7/1.0× on 037; MDD −4/−8pp; DSR 0.204 |
| **5** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` | `[risk_parity, ch.5]` + AMP 2013 | 1st plain static-stack 79; Sharpe +0.30/+0.25/+0.22; **base for iter 051** |
| **5** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` | `[risk_parity, p.10-11]` + MM 2017 | 60:40 × MM vol-target; Sharpe +0.24-0.30; DSR 0.226 |
| **5** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` | `[risk_parity, p.80-84]` | 016 + funding cost (−93 to −148 bps/yr); ties 016 |
| **5** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` | `[volatility_trading, ch.3]` | 016 + short put-cs; MDD −1/−3pp; DSR 0.217 |
| **5** | **043** | 🥇 STRONG | **79** | `hysteretic_vix_low18_high22_w70_40_40_30_55_55` | `[advances_fin_ml, ch.17-18]` + Hamilton 1989 | Schmitt 041w; RT/yr 2.5 = halved; falsifies path-variance |
| **5** | **052** | 🥇 STRONG | **79** | `iter041_plus_iter026_w082` | `[risk_parity, ch.5]` + Whaley + Sinclair + Markowitz | DSR p 0.175→0.118 (−33%) but same bucket; iter 037 dominates iter 041 as anchor; ndx CAGR floor lost |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 052 — 2026-04-25 — iter041-plus-iter026-w082 (🥇 STRONG, 79/100, 1/6 KILLS)
- **Result:** Sharpe edu/spy/ndx 1.078/1.188/1.220 (Δ frozen +0.40/+0.29/+0.27), gates 6/6/6 (G2 fail 3/3), DSR p=0.1177/0.1162/0.1086 (n=4319, **−33% vs iter 051 but same [0.10, 0.20) bucket**), CAGR 11.61/12.03/**14.01%** (edu+spy PASS, ndx FAIL by 1.34pp vs iter 051's PASS by 0.16pp), MDD 24/21/26% (−5/−0/−1pp vs iter 051), corr(041,026)=0.370/0.373/0.447, Markowitz residual=0.0000 (4th consec; 12/12 ds cumulative), G7 0.0000pp, robust 9/9, winner 4/5 (DSR fails); score 1:25 2:19 3:5 4:**10** 5:15 6:5 = **79** (Δ iter 051 −5 entirely on c4). Kill B fired.
- **Lesson:** **iter 037 strictly dominates iter 041 as anchor**. iter 041's regime modulation trades CAGR for Sharpe; c1 already saturated at 25 (Sharpe lift yields 0 marginal score until DSR bucket crosses), while CAGR loss (15.63 vs 037's 17.76 ndx) costs 5 c4 pts. **iter 041+iter 026 family closes at Pareto-opt 79**; 4 saved-stream families now closed (037+039, 041+039, 037+026, 041+026). See `iterations/052-*/`.

### Iters 015-051 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **051** (🥇 84, 1/6 KILLS, iter037+026 w_037=0.80) S 1.02/1.20/1.22, DSR 0.175/0.109/0.109, CAGR 12.4/13.5/15.5 (3/3 floor), MDD 29/21/27 (Δ037 −4/−4/−5), corr 0.57/0.55/0.60, Markowitz res=0.0000 (3rd consec), score 25+19+5+15+15+5=84. **1st 4/5 winner conds. Pareto box bounded at 84 (edu DSR floor + ndx CAGR floor unbreakable on this stream pair).**
- **050** (🥇 78, 1/6 KILLS) 90/10 iter046+gold-TSM at Markowitz w*=0.10; n_trials+=1 → edu DSR 0.044→0.050 (c3 −5). Markowitz 1st-validated 4-decimal. **5 iter 046 axes closed (044/047/048/049/050).**
- **049** (🥉 59 MARGINAL, 4/6 KILLS) gold TSM @ w=0.5; S 0.92/1.02/1.03 (Δ046 −0.30 each), DSR 0.32 worst (8× iter 046). **Markowitz dilution at unequal Sharpes; w*≈0.09 not 0.50.**
- **048** (🥇 83, 3/6 KILLS) VIX-output-gate on 046; S 1.20/1.29/1.34, DSR 0.043/0.056/0.044, score 83. **Output regime gate = output analog of 044 input closure; re-uses VIX classifier → double-counts.**
- **047** (🥇 79 frozen/84 custom, 2/6 KILLS) 3-cfg sweep w_041 ∈ {0.5,0.65,0.8}; best=50/50 ≡ 046; Bonferroni destroys G2. **046's 50/50 IS Pareto-opt; ndx CAGR 15.35% unreachable.**
- **046** (🥇 85 TOP-K #1, 0/6 KILLS) 50/50 iter041+iter039 ρ=0.41; S 1.20/1.32/1.38, DSR 0.041/0.042/0.031 (1st sub-0.05×3, n=4311), gates 7/7/7, CAGR 9.16/9.45/9.76 (edu 0.02pp short), MDD 18/15/15, score 25+25+15+0+15+5=85. **Out-of-family composition score scales inversely with corr; 5pt gap to WINNER on CAGR-floor only.**
- **045** (🥇 81) 50/50 iter037+iter039 ρ=0.587; S 1.10/1.28/1.33, DSR 0.096/0.057/0.050, score 81. **Out-of-family at moderate corr compounds DSR; superseded by 046 at lower corr.**
- **044** (🥈 74, multifeature-regime-vix-t10y3m) score 1:25 2:19 3:**0** 4:10 5:15 6:5 = 74; DSR 0.240 worst-p DEEPEST 041-perturb. PRINCIPLE: 2-feat composite over-classifies stress + T10Y3M dilutes VIX; 041's 84-ceiling LOCAL PLATEAU; **045+ MUST go OUT-OF-FAMILY** (vindicated by 045/046).
- **043** (🥇 79, hysteretic-vix-regime-weights) DSR worst-p REGRESS 0.168→0.189 (Kill B); MDD best static-stack ever; PRINCIPLE: halving regime crossings introduces regime-lag variance > path-variance gain; localizes 84-ceiling on gate-timing axis.
- **042** (🥈 74, combined-regime-lev-weights) DSR REGRESS 0.168→0.216, MDD deepest-ever; PRINCIPLE: amplifying lev asymmetry adds path variance > mean return; "compose × leverage compound DSR" FALSIFIED.
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

### Iters 005-014 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **014** (❌ FAIL 0, Kill #PV) — EBP credit overlay on iter 008; pre-val rejects 3/3 (exceed 0.68-0.71); overlay family CLOSED on iter 008 blend.
- **013** (🥈 64, Kill #3) — LR meta-label ρ_60+vix_z on iter 008: Sharpe regress; vol-proxy meta REDUNDANT with variance-scaling.
- **012** (🥉 58, Kill #1+#3+#4) — 5d EMA asymmetric T10Y3M haircut iter 008: 100% overlap edu+spy; T10Y3M 2×2 family CLOSED.
- **011** (🥉 52, Kill #1+#3) — Weekly 3-leg blend: Sharpe regress 3/3, MDD +10-14pp; vol-targeting REQUIRES daily cadence.
- **010** (🥈 74) — 3-leg SPY+TLT+GLD daily: ties iter 008 at 74, 4/5 winner; blend family saturates Sharpe ~1.00 regardless of N=2 or 3.
- **009** (🥈 64, Kill #3) — 21d EMA symmetric T10Y3M haircut iter 008: 100% overlap at bottom-20%; smoothing destroys lead-time.
- **008** (🥈 74) — Single-cfg ex-ante vol-managed SPY+TLT `vt15_L21_cap20`: Sharpe 0.87/1.00/1.02, DSR p=0.332, 4/5 winner; iter 006's edge IS structural.
- **007** (🥉 50, Kill #1+#3) — 12-1 momentum overlay iter 006: Sharpe regress 2/3; momentum REDUNDANT with variance-scaling.
- **006** (🥈 67, Kill #3) — 12-cfg vol-managed SPY+TLT grid: first +0.10 Sharpe gate cross-ds; killed G1 PBO 0.69 (grid inflates).
- **005** (🥉 59) — Moreira-Muir σ⁻² single-asset SPY/QQQ: first DSR edu PASS; single-asset vol-adapt saturates +0.08-0.10.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**052**. iter 044/047/048/049/050 close **5 axes of iter 046**; iter 051 closes **iter 037+iter 026 family** at Pareto 84; iter 052 closes **iter 041+iter 026 family** at Pareto 79 (iter 037 dominates iter 041 as anchor). Markowitz formula validated to 4 decimals across iter 049/050/051/052 (4 consecutive iters, residual=0.0000 on 12/12 datasets). DSR is the binding constraint at n_trials > 4300: combined edu Sharpe ≥ ~1.10 needed to cross 0.10 score-bucket boundary; ≥ ~1.18 needed to cross 0.05 strict-winner gate.

### Iter 053 candidates (iter 052 confirms iter 037 dominates iter 041 as anchor)

- **#1 iter 037 + iter 046 reverse-weight Markowitz Pareto-opt (RECOMMENDED)** — use iter 046 (TOP-K #1) instead of iter 026 as 2nd component; w_037 ≈ 0.40-0.60 may keep edu Sharpe ≥ 1.20 (DSR<0.05) + CAGR from iter 037 (14-17%) for 2-3/3 floor. Risk: iter 046 DSR knife-edge. Pre-screen mandatory. `[risk_parity, ch.5]` + Markowitz.
- **#2 Plano C sleeve eval (mandate-aligned)** — factor-tilted passive (GDE/AVUV/AVDE/AVEM/BTGD); different paradigm; low n_trials → DSR easy. Data: factor ETFs inception 2018+; need AQR/FF proxies for edu window. `[fact_based_investing]` + Fama-French 1993.
- **#3 New base edu Sharpe ≥ 1.20 standalone** — implement from scratch; VRP on RUT/EFA, carry+value AMP 2013, single-stock Tiingo momentum (cache 2013-08+, partial coverage). 60-90 min.

DEAD-LETTER: iter 037+026/041+026 at any weight (Pareto 84/79); iter 046-family enhancements (044/047/048/049/050); HYG-in-041; HMM-2; FX carry; MTUM/QUAL/USMV (not in cache).
NOT recommended: perturbations of 037/041/046; σ⁻¹/σ⁻²/term-spread/MOVE/EBP gates on 037/041; 4-5-leg in 046 family; VIX/DTE/strike sweeps; MM σ⁻² on short-vol (040); gate-enrichment on 041; corr>0.85 (032); N>1 cfg on 046 (047); 046 modulation/additive (044-050); **iter 041 substitution for iter 037 as anchor (closed by 052; iter 037 strictly dominates Sharpe-CAGR trade-off)**.

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
- **iter 047 closure**: 50/50 IS Pareto-optimum on iter 046; Bonferroni N=3 cost > grid gain; ndx CAGR 15.35% unreachable from iter 041 composites.
- **iter 048 closure**: output-side regime gate is OUTPUT-LEVEL ANALOG of iter 044's input closure — re-using same VIX classifier double-counts.
- **iter 049 closure**: 50/50 additive 3rd stream on iter 046 with S_3rd < 1.10 fails by Markowitz identity regardless of ρ; gold TSM (S=0.69, ρ=0.53) at w=0.5 → combined S=1.03, score 59 (Δ-26). Markowitz optimum w*≈0.09, NOT 0.50.
- **iter 050 closure**: iter 046 DSR knife-edge (p=0.044, headroom 0.006); n_trials+=1 deflator alone crosses gate. 5th iter 046 axis closed: input/weight/output/additive-50/50/additive-low-w (044-050). Markowitz formula 1st-validated 4-decimal.
- **iter 051 closure (Pareto 84; 1st 4/5 winner + 3/3 CAGR)**: iter 037+026 at w_037=0.80 hits 3/3 CAGR + Sharpe edge + MDD + Markowitz 0.0000 residual; capped 84 because edu S 1.02 < 1.10 (DSR floor at n=4318). Two-constraint Pareto (ndx CAGR≥15.35 sets w_037≥0.78; edu DSR needs S≥1.10) unbreakable.
- **iter 052 closure (Pareto 79; iter 037 strictly dominates iter 041 as anchor)**: iter 041+026 at w_041=0.82 — edu S +0.057 + DSR 0.175→0.118 (−33%) but same [0.10, 0.20) bucket → c3 unchanged; iter 041's lower ndx CAGR (15.63 vs 037's 17.76) → ndx combined 14.01 < 15.35 floor → c4 −5. Net 84→79. **Generalised: regime modulation trades CAGR for Sharpe, but c1 already saturated → Sharpe lift yields 0 score until bucket cross; CAGR loss costs 5pts/floor. 4 saved-stream families closed (037+039/041+039/037+026/041+026).** Markowitz residual=0.0000 4th consec, 12/12 datasets.

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
