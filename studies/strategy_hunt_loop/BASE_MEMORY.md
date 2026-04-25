---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 59
winners_found: 0
status: iterating
latest_iteration: "059-2026-04-25-1107"
cumulative_n_trials: 4329
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

### 059 — 2026-04-25 — iter037-plus-hyg-tsm-w010 (🥇 STRONG, 79/100, 1/7 KILLS — B only)
- **Result:** S 0.98/1.17/1.18 (Δ frozen +0.30/+0.27/+0.23, Δ037 −0.001/+0.020/+0.009), CAGR 13.04/14.47/16.50% (Δ037 −1.1/−1.1/−1.3; **3/3 floor PASS** vs 058's 0/3), MDD 30.71/22.93/29.33% (3/3, Δ037 −2.6/−2.3/−2.9 DOWN), gates 6/6/6 (G2 DSR FAIL ×3), DSR worst-p 0.268/0.128/0.138 (edu rises vs 037's 0.222 from HYG-windowing 2006-07 loss), corr avg 0.42, Markowitz 0.0000, G7 0.0000pp, robustness 9/9, winner 4/5; score 25+19+0+15+15+5=79. Cites `[risk_parity, ch.5]` + Asvanunt-Richardson 2017 + `[systematic_trading]` + Markowitz 1952. n_trials 4328→4329.
- **Lesson:** Anchor substitution at fixed w=0.10 HYG_TSM trades CAGR-floor (15/15 here vs 058's 0/15) for DSR-pass (0/15 here vs 058's 15/15) — net 79 = bare iter 037. Saved-stream-pair Pareto traces 2 non-dominating points: 79 (CAGR-branch, 037) vs 85 (DSR-branch, 058). Path to WINNER 90+ needs NEW base anchor with Sharpe ≥ 1.20 AND CAGR ≥ 12% (none in iters 0-58). Levered iter 058 = iter 060 #1 direct attack. See `iterations/059-*/`.

### Iters 015-058 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **058** (🥇 85 TOP-K #1 tied, 0/6 KILLS, hyg-credit-carry-3rd-stream) S 1.22/1.35/1.40 (Δ046 +0.02 each), gates 7/7/7, DSR 0.049/0.034/0.026, CAGR 8.69/9.01/9.27% (0/3 floor), MDD 16.74/13.71/13.12% (3/3, Δ046 −1.2/−1.5/−1.5), corr 0.44, Markowitz 0.0000, score 85. **3rd-stream-Sharpe thesis vindicated (HYG_TSM S~0.9 → 85 > gold 78 > commodity 64); CAGR floor 0/15 binding on iter-046 anchor.**
- **057** (🥈 64, 4/6 KILLS, commodity-tsm-basket-3leg) S 1.05/1.08/1.14 (Δ046 −0.16/−0.24/−0.24), CAGR 8.10/7.87/8.22% (0/3 floor), MDD 15.78/10.53/11.24% (Δ046 −2/−5/−3 pp), gates 6/6/6, DSR worst-p 0.223, corr 0.30, score 64. **Closes multi-commodity TSM 3rd-stream on iter 046; standalone basket Sharpe 0.13-0.29 too low for Markowitz-positive contribution.**
- **056** (🥈 74, 2/4 KILLS, iter046-levered-130) S 1.10/1.21/1.27 (Δ046 −0.11/−0.11/−0.11), CAGR 10.79/11.20/11.61% (1/3 floor), gates 6/6/6 G2 FAIL ×3, DSR worst-p 0.10, score 74. **External 1.3× lev at 3.5% borrow trades CAGR for Sharpe; closes external-lev axis on iter 046 at borrow ≥ 3%.**
- **055** (🥈 73, 0/6 KILLS, vrp-basket-5etf-cross-region) S 1.07/1.40/1.60 (Δ039 −0.07/+0.12/+0.04), CAGR 4.74/5.38/6.20% (0/3 floor), MDD 16/6/5%, DSR edu 0.130, score 73. **EFA/EEM help post-GFC, hurt pre-GFC edu (EM tail miss); iter 039 Pareto-opt at 76; broader-VRP axis closed.**
- **054** (🥉 47, tiingo-cross-sectional-12-1) S 0.655 single-univ < SPY 0.680, CAGR 16.6% (3/3 floor), DSR 0.811, PBO=1.0, G7 0.0000pp, score 47. **DATA-LAYER closure: survivorship-biased Tiingo cache → no cross-sectional dispersion at any K; closes all cross-sectional ranking until CRSP/Norgate delisted coverage.**
- **053** (🥇 84, 2/6 KILLS, iter037+iter046 w=0.70) S 1.03/1.19/1.22, CAGR 12.71/13.73/15.39 (3/3 floor), corr 0.93-0.96 Kill F pre-fired, winner 4/5. **037-anchor saved-stream-pair Pareto = 84 (3 tested); path 90+ needs base edu S ≥ 1.20.**
- **052** (🥇 79, iter041+026 w=0.82) S 1.08/1.19/1.22, CAGR 11.6/12.0/14.0 (2/3, ndx FAIL), corr 0.37-0.45, Markowitz 0.0000. **iter 037 dominates iter 041 as anchor.**
- **051** (🥇 84, 1/6 KILLS, iter037+026 w_037=0.80) S 1.02/1.20/1.22, DSR 0.175/0.109/0.109, CAGR 12.4/13.5/15.5 (3/3 floor), corr 0.57-0.60, score 84. **1st 4/5 winner conds; Pareto bounded at 84 on this pair.**
- **050** (🥇 78, 1/6 KILLS) 90/10 iter046+gold-TSM at Markowitz w*=0.10; n_trials+=1 → edu DSR 0.044→0.050 (c3 −5). Markowitz 1st-validated 4-decimal. **5 iter 046 axes closed (044/047/048/049/050).**
- **049** (🥉 59 MARGINAL, 4/6 KILLS) gold TSM @ w=0.5; S 0.92/1.02/1.03 (Δ046 −0.30 each), DSR 0.32 worst (8× iter 046). **Markowitz dilution at unequal Sharpes; w*≈0.09 not 0.50.**
- **048** (🥇 83, 3/6 KILLS) VIX-output-gate on 046; S 1.20/1.29/1.34, DSR 0.043/0.056/0.044, score 83. **Output regime gate = output analog of 044 input closure; re-uses VIX classifier → double-counts.**
- **047** (🥇 79 frozen/84 custom, 2/6 KILLS) 3-cfg sweep w_041 ∈ {0.5,0.65,0.8}; best=50/50 ≡ 046; Bonferroni destroys G2. **046's 50/50 IS Pareto-opt; ndx CAGR 15.35% unreachable.**
- **046** (🥇 85 TOP-K #1, 0/6 KILLS) 50/50 iter041+iter039 ρ=0.41; S 1.20/1.32/1.38, DSR 0.041/0.042/0.031, gates 7/7/7, CAGR 9.16/9.45/9.76 (edu 0.02pp short), MDD 18/15/15, score 85. **Out-of-family score scales inversely with corr; 5pt gap to WINNER = CAGR-floor only.**
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

### Iters 005-014 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **014** (❌ 0, Kill #PV) EBP credit overlay; pre-val rejects 3/3; overlay family CLOSED.
- **013** (🥈 64, Kill #3) LR meta-label on 008: Sharpe regress; vol-proxy meta REDUNDANT with variance-scaling.
- **012** (🥉 58) 5d EMA asymmetric T10Y3M on 008: 100% overlap; T10Y3M 2×2 family CLOSED.
- **011** (🥉 52) Weekly 3-leg blend: Sharpe regress 3/3, MDD +10-14pp; vol-targeting REQUIRES daily.
- **010** (🥈 74) 3-leg SPY+TLT+GLD daily: ties iter 008; blend family saturates Sharpe ~1.00.
- **009** (🥈 64) 21d EMA symmetric T10Y3M on 008: 100% overlap; smoothing destroys lead-time.
- **008** (🥈 74) Vol-managed SPY+TLT `vt15_L21_cap20`: Sharpe 0.87/1.00/1.02, 4/5 winner.
- **007** (🥉 50) 12-1 momentum overlay 006: regress; momentum REDUNDANT with variance-scaling.
- **006** (🥈 67) 12-cfg vol-managed SPY+TLT grid: first +0.10 cross-ds; killed G1 PBO 0.69.
- **005** (🥉 59) Moreira-Muir σ⁻² single-asset: first DSR edu PASS; single-asset saturates +0.08-0.10.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed/closed: 002-005/007/009-014/017/019-**059**. **Iter 059 closed 037-anchor + HYG_TSM at w=0.10 → 79 (CAGR floor unlocked 3/3 but DSR didn't improve).** Saved-stream-pair Pareto traces 2 non-dominating points: 79 (CAGR-branch, 037) vs 85 (DSR-branch, 058). **NO anchor in iter 0-58 has Sharpe ≥ 1.20 AND CAGR ≥ 12% simultaneously; saved-stream-pair frontier capped at 85.**

### Iter 060 candidates (iter 058 = TOP-K #1 stays; 037 anchor closed via 059)

- **#1 Levered iter 058 at 1.2-1.3× external borrow (RECOMMENDED)**: direct attack on CAGR floor 0/15; iter 056 pattern on 058 stream. Predicted 78-92; path to WINNER if borrow ≤ 3%.
- **#2 Equity-overweight 037 (0.75/0.40/0.40) + HYG_TSM**: trades MDD for Sharpe; predicted 82-87.
- **#3 Regime-aware leverage on iter 015 base**: VIX-z-score 2-state HMM, lever 1.7× calm / 1.0× stress. `[advances_fin_ml, ch.17-18]`. Predicted 80-95.
- **#4 Plano C sleeve eval** (predicted ≤ 70). **#5 CRSP/Norgate delisted** (not feasible without budget).

DEAD-LETTER: 037+026/041+026/037+046/041+039 any weight (Pareto 79-85); 046-family 044/047-050; **HYG_TSM 3rd stream on 046 at w=0.10 (058 = 85; family Pareto)**; **HYG_TSM 3rd stream on 037 at w=0.10 (059 = 79; CAGR floor unlocked but DSR not improved)**; HYG-041 substitution (UNTESTED, distinct); HMM-2; FX carry; MTUM/QUAL/USMV (not in cache); all 037-anchor saved-stream-pairs (045/051/053, ceil 84); 041 substitution for 037 (052); cross-sectional momentum on Tiingo cache (054 data layer); broader-region VRP 5-leg (055 at 73); external lev on 046 at borrow ≥ 3% (056 at 74); multi-commodity TSM basket on 046 (057 at 64).

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
- **iter 047-050 closures**: 5 iter-046 axes closed (047 50/50 Pareto-opt + Bonferroni; 048 output VIX dupes 044 input; 049 additive low-S fails Markowitz id; 050 knife-edge DSR n+=1).
- **iter 051-053 closures**: 037+026 (84, edu S 1.02 < 1.10 DSR cap), 041+026 (79, ndx CAGR lost), 037+046 (84 corr 0.93-0.96 Kill F). Saved-stream-pair ceiling = 85 (iter 046); path 90+ needs NEW base edu Sharpe ≥ 1.20.
- **iter 054 closure (DATA LAYER)**: 12-1 cross-sectional on Tiingo cache survivorship-biased; closes ALL cross-sectional ranking until CRSP/Norgate delisted coverage.
- **iter 055 closure (broader-region VRP)**: 5-leg SPY+QQQ+IWM+EFA+EEM equal-weight scored 73 < iter 039's 76; iter 039 Pareto-opt; broader-region axis closed.
- **iter 056 closure (external leverage on iter 046)**: 1.3× borrow at 3.5% loses 0.1 Sharpe, fails G2 DSR; iter 046's 85 = Pareto ceiling on this family.
- **iter 057 closure (multi-commodity TSM 3rd-stream)**: USO+UNG+SLV at w=0.20 scored 64; standalone basket Sharpe 0.13-0.29 too low (Markowitz dilution at unequal Sharpes); orthogonality vindicated (corr 0.30) but absolute Sharpe matters more.
- **iter 049/050/057/058 STRUCTURAL FINDING**: 3rd-stream Sharpe ≥ ~0.5 is binding for Markowitz-positive contribution, NOT correlation alone. Vindicated constructively by 058 (HYG_TSM S~0.9, w=0.10 → 85 STRONG; ties 046 at TOP-K #1 with better Sharpe + MDD). CAGR floor 0/15 now binding ceiling on iter-046-family.
- **iter 059 closure (037+HYG at w=0.10)**: CAGR floor 3/3 unlocked but DSR worst-p 0.268 ≥ iter 037 baseline 0.222 → score 79 = bare iter 037. **CAGR-DSR dual constraint structural finding**: at n_trials=4329 and w_HYG=0.10, NO anchor in iters 0-58 has Sharpe ≥ 1.20 AND CAGR ≥ 12% simultaneously; saved-stream-pair Pareto frontier capped at 79-85.

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
