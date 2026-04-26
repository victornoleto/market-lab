---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 77
winners_found: 0
status: iterating
latest_iteration: "077-2026-04-26-0023"
cumulative_n_trials: 4522
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
| **5** | **074** | 🥇 STRONG | **89** | `iter074_ensemble_w016_050` | Markowitz (1952) + `[risk_parity, ch.5]` + Moreira-Muir (2017) + Faber 2007 | iter 016+064 saved-stream blend 50/50; 4/5 strict winner conds met (DSR sole gap); 6/6/6×3 + bonus; PBO 0.04/0.13/0.17 best-of-hunt; ρ 0.79-0.84 |
| **6** | **076** | 🥇 STRONG | **85** | `iter076_lev_tv015_w015` | `[leverage_for_the_long_run, ch.5]` + Faber 2007 + Frazzini-Pedersen 2014 | iter 064 + LEG-LEVERED GLD/TLT @ 4.5% borrow; 4/5 winner conds (CAGR floor sole gap); 7/7/7 gates + PBO 0.05; KILL B (sleeve gross CAGR ≤6% at tv=0.30 — borrow eats lev) |
| **6** | **077** | 🥇 STRONG | **85** | `iter077_lsfac_tv006_w010` | Carhart 1997 + AMP 2013 + `[advances_fin_ml, ch.3]` + McLean-Pontiff 2016 | iter 064 + LS MTUM-VLUE factor sleeve; 4/5 winner conds (CAGR floor sole gap); 7/7/7 gates + PBO 0.24/0.19/0.06; KILLS B+H (sleeve Sharpe 0.18 not 0.7 — factor decay) |
| **6** | **072** | 🥇 STRONG | **85** | `iter064_vix_cond_calm010_stress005` | `[algo_trading_chan, p.95, p.153-154]` + Whaley 2009 + Connors-Alvarez 2009 | TIES iter 058/076; 6/10 KILLS; KILL E inverted (r_064 calm-defensive); regime-cond 3rd-stream axis closed |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 077 — 2026-04-26 — iter064-plus-LS-mtum-vlue-factor-sleeve (🥇 STRONG, 85/100, 4/5 strict winner conds met)
- **Hypothesis:** dollar-neutral long-short MTUM (long, momentum) − VLUE (short, value) factor pair as 3rd-stream sleeve to iter 064; tests joint-constraint (`ρ < 0.5` AND pre-borrow Sharpe ≥ 0.7) per iter 076 final-report recommendation #2.
- **Citations:** Carhart (1997) JoF 52(1) DOI 10.1111/j.1540-6261.1997.tb03808.x + Asness-Moskowitz-Pedersen (2013) JoF 68(3) DOI 10.1111/jofi.12021 + `[advances_fin_ml, ch.3, p.222-223]` + McLean-Pontiff (2016) JoF 71(1) DOI 10.1111/jofi.12365 + Frazzini-Pedersen (2014) JFE 111(1).
- **Scope:** 20 cfgs (5 target_vol × 4 w_sleeve), leg_cap=1.5, short_borrow=1%/yr, trans_cost=5 bps; 3 datasets × 20 cfgs = 60 trials; cumulative 4462→4522. MTUM/VLUE downloaded via Tiingo (3271 bars 2013-04-18 → 2026-04-20). Phase-in combine logic for pre-2013 dates.
- **Result:** Best cfg `iter077_lsfac_tv006_w010` (tv=0.06, w=0.10); S edu/spy/ndx 1.208/1.333/1.373 (Δ064 −0.013/+0.002/−0.007 — TIED with iter 064), CAGR 8.95/9.34/9.48% (floor 0/3 — same gap as iter 075/076), MDD 17.27/14.24/13.70%, **gates 7/7/7** (matches iter 076 best), PBO 0.242/0.194/0.060 (clean), DSR p 2.57e-4/2.51e-4/2.00e-4 (v2 n=20), G7=0pp on all 20 cfgs, robust 9/9, 22/22 TDD. winner=4/5. **Sleeve standalone Sharpe 0.13-0.22 across 5 tv values × 3 ds (vs hypothesised 0.6-0.8)**. corr(sleeve, SPY)=0.062, corr(sleeve, QQQ)=0.199, corr(sleeve, iter064)=0.118-0.141 — low-ρ thesis vindicated.
- **Score breakdown:** 1:25 2:25 3:15 4:0 5:15 6:5 = **85**; 2/8 KILLS fired (B — sleeve Sharpe 0.18 << 0.40 threshold; H — combined CAGR 0/3 clears strict floor).
- **Lesson:** **MTUM-VLUE long-short Sharpe in 2013-2026 is 0.18, NOT 0.6-0.8** — McLean-Pontiff (2016) factor-anomaly post-publication decay vindicated; cross-sectional academic deciles spread (AMP 2013) does NOT translate to factor-ETF long-short pair. **KILL H establishes CAGR floor as STRUCTURAL TO iter 064 ANCHOR, not to sleeve selection**: 3 independent sleeve mechanisms (unlevered non-equity iter 075, levered non-equity iter 076, factor LS iter 077) all hit ~9.5% combined CAGR ceiling. **Closes iter-064 + 2nd-leg-ensemble axis at 85 STRONG across ALL 3 sleeve classes**. **10-iter pattern (064/068-072 + 074-077) PROVES iter-064-anchored family caps at 90 single / 85 ensemble**. 90+→95 unlock now requires ABANDONING iter 064 anchor for higher-CAGR base. Iter 078 candidates: (1) Antonacci dual-momentum SPY/EFA/cash standalone; (2) DBMF-as-base post-2019; (3) Hurst-regime adaptive trend multi-asset. See `iterations/077-*/`.

### 076 — 2026-04-25 — iter064-LEV-gld-tlt-sleeve (🥇 STRONG, 85/100)
- **Result:** S 1.231/1.325/1.352 (Δ064 +0.010/−0.006/−0.028), CAGR 8.80/9.10/9.15% (floor 0/3), gates 7/7/7, PBO 0.05/0/0, DSR p=1.45e-5 spy (v2 n=20), winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85; 1/7 KILL B (sleeve gross CAGR ≤6% at tv=0.30 — borrow eats lev).
- **Lesson:** Borrow-Sharpe identity `[leverage_for_the_long_run, ch.5]` vindicated; 3× lev → 1.7×/1.4×/1.1× CAGR. Closes iter-064 + LEG-LEV non-equity sleeve at 85. See `iterations/076-*/`.

### 075 — 2026-04-25 — iter064-gld-tlt-sleeve (🥇 STRONG, 81/100)
- **Result:** S 1.238/1.340/1.373 (Δ064 +0.021/+0.008/−0.003), CAGR 8.58/8.91/9.01% (floor 0/3), gates 6/6/7, PBO 0.86/0.60/0.46 (KILL F 2/3), DSR p≤3.03e-5 (v2 n=7), winner=4/5; score 81; 1/7 KILL F.
- **Lesson:** Low-ρ vindicated, sleeve CAGR 3% dilutes. Closes unlevered non-equity sleeve at 81. See `iterations/075-*/`.

### 074 — 2026-04-25 — iter016-iter064-ensemble (🥇 STRONG, 89/100)
- **Result:** S 1.11/1.24/1.30 (Δ064 −0.11/−0.09/−0.08), gates 6/6/6, DSR p≤0.094 (n=4381), winner=4/5; score 89; ρ legs 0.79-0.84.
- **Lesson:** SPY-co-exposed ensemble ρ floor 0.78-0.85; v2 retro = 95 WINNER but loop continues. Closes SPY-co-exposed saved-stream-ensemble axis at 89. See `iterations/074-*/`.

### 073 — 2026-04-25 — gayed-ma-gate-iter016 (🥈 PROMISING, 62/100)
- **Result:** S 0.99/0.97/1.03, gates 5/5/5, PBO 0.96/0.92/0.68 (KILL F), DSR p≥0.24 (KILL H), winner=1/5; score 62; 4/9 KILLS.
- **Lesson:** Gayed edge non-stationary post-GFC; gate net-harmful. Closes Gayed-MA-overlay at 62. See `iterations/073-*/`.

### 068-072 — 2026-04-25 — iter064-anchored variants (compressed batch)
- **068** (🥇 79, vix-inner-swap) Δ064 −0.04/−0.05, gates 6/6/6, KILL I (BOTH sub-streams defensive in stress). **069** (🥇 90, vix-inner-reverse) Δ064 ≈0, gates 7/7/7. **070** (🥇 90, t10y3m-cont) Δ064 ≈0, gates 7/7/7 (T10Y3M ≈ binary VIX). **071** (🥇 90, +spy-MR-RSI2) Δ064 +0.015, gates 7/7/7. **072** (🥇 85, vix-cond r-MR) Δ064 +0.01-0.02, gates 7/7/7, edu CAGR<9.18 KILL B. **5-iter pattern PROVES 90 ceiling iter-064-anchored**. See `iterations/068-072-*/`.

### 065-067 — 2026-04-25 — iter064-anchored variants (compressed batch)
- **065** (🥈 74, vix-output-lev-gate 1.5×) Δ064 −0.10 to −0.14; closes calm-cond ext-lev. **066** (📉 37, RF meta-label) AUC 0.50 (KILL H 3/3); extends iter 013 LR closure. **067** (🥈 74, σ⁻² overlay) — MM σ⁻² drops mean faster than variance on vol-managed 064. See `iterations/065-067-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-**077**. **iter 064 still TOP-K #1 STRONG 90 (4-WAY TIED with iter 069/070/071), 0/7 KILLS.** iter 077 (iter 064 + LS MTUM-VLUE factor sleeve, 20 cfgs at tv∈{0.06,0.08,0.10,0.12,0.15}×w∈{0.10,0.20,0.30,0.40}, leg_cap=1.5, short_borrow=1%/yr) → **85 STRONG, 4/5 strict winner conds met** (CAGR floor sole gap, same as iter 075/076), 2/8 KILLS (B — MTUM-VLUE Sharpe 0.13-0.22 << 0.40 threshold; H — combined CAGR 0/3 clears strict floor). MTUM-VLUE in 2013-2026 has Sharpe 0.18, NOT 0.6-0.8 (McLean-Pontiff 2016 factor decay vindicated). **10-iter pattern (064/068-072 + 074-077) PROVES iter-064-anchored family caps at 90 single / 85 ensemble across ALL 3 sleeve mechanism classes (unlevered non-equity, levered non-equity, factor LS).** Hunt loop's deepest finding: **CAGR floor is structural to iter 064 ANCHOR, not to sleeve selection** — 3 independent sleeve mechanisms converge at ~9.5% combined CAGR ceiling regardless of sleeve correlation or borrow regime.

### Iter 078 candidates (path: ABANDON iter 064 anchor for higher-CAGR base)

- **#1 Antonacci Dual Momentum (BASE, not sleeve) — RECOMMENDED**. SPY/EFA/cash absolute+relative momentum. All ETFs cached. Documented Sharpe 0.85-1.0 + CAGR 12-14% on 1974-2014 (Antonacci 2014 + JoPM 16(1)). Structurally novel as STANDALONE base. Predicted 85-95.
- **#2 DBMF managed-futures as STANDALONE base** — Tiingo download required (~6.5y post-2019). Tests "does CTA trend natively deliver Sharpe ≥ 1.0 + CAGR ≥ 8%?". Predicted 65-90.
- **#3 Multi-asset Hurst-regime adaptive trend** (Mandelbrot/Peters/Lo-MacKinlay) on SPY/EFA/EEM/GLD/TLT. Continuous-regime memory-based vs binary SMA. Predicted 65-85.
- **#4-6 backlog**: forward-Sharpe meta-label on iter 064 (likely 85 per pattern); Carver multi-asset slow-trend N≥10 (iter 023/025 closed at smaller N); CRSP cross-sectional (Tiingo blocked by survivorship per iter 054).

DEAD-LETTER (full list in `## Structural dead-ends` below + `DEAD_ENDS.md`).

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Carry + value composite AMP 2013 — orthogonal axes vs iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-025 closures**: daily EMA/SMA×LETF; drawdown-stops; CAPE/EBP/VIX standalone; Clenow ATR ≤20-asset; single-asset σ⁻¹/σ⁻²; TSM overlay; T10Y3M EMA haircut; weekly/monthly cadence; meta-LR; EBP credit; 12-1 top-K=1 ≤3 regions; ρ overlay; options-on-equity-leg; TOM modulator; TSM-PRIMARY ≤4-asset; bond-curve carry; slow-EWMAC ≤6-asset.
- **VRP-harvester family 76 ceiling (026/031/039/040)**: CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral.
- **Static-stack 84-STRONG ceiling = LOCAL DSR PLATEAU**: iter 042 amp / 043 freq / 044 input all regress DSR.
- **Out-of-family composition VINDICATED**: iter 045 (81, ρ=0.58) → iter 046 (85, ρ=0.41) TOP-K #1; score scales inversely with corr.
- **iter 047-057 closures (iter-046 family + saved-stream-pair + cross-region/lev/commodity)**: 047 Pareto+Bonf / 048 output-VIX dupes 044 / 049 low-S Markowitz / 050 DSR knife-edge / 051-053 saved-stream-pairs ceiling=85 (Kill F corr 0.93-0.96) / 054 Tiingo cross-sectional CRSP-blocked / 055 5-leg VRP (73) / 056 ext-lev 046 (74) / 057 commodity basket (64). 3rd-stream-S binding rule emerged: standalone S ≥ ~0.5 needed for Markowitz-positive.
- **iter 058-063 closures (3rd-stream + 037-anchor + lev axes)**: 058 HYG-credit-carry (85, S~0.9 vindicates 3rd-stream-S binding); 059-063 saturate 79-81; **Internal-LETF axis EXHAUSTED** (037→79; 058→81) — SOLVED in 064 via QQQ-200d trend sub at w=0.10.
- **iter 064 TOP-K #1**: 90, 0/7 KILLS, 1st 90+. Faber QQQ-200d sub for HYG_TSM. edu 9.49%>9.18% (1st non-LETF CAGR unlock). Path 95+ = close spy/ndx CAGR floor.
- **iter 065-073 closures (iter-064-anchored variants)**: 065 VIX-calm ext-lev (74); 066 RF meta-label (37, AUC≈0.50 extends iter 013); 067 σ⁻² overlay (74); 068 VIX inner-swap (79, KILL I 3/3); 069-071 reverse-swap/T10Y3M cont/Connors RSI(2) all → 90 TIES 064 (close inner-weight + regime-classifier + calm-aggressive 3rd-stream axes); 072 VIX-cond r_mr (85, closes regime-cond axis); 073 Gayed-MA-gate on iter 016 (62, gate net-harmful post-GFC).
- **iter 074-076 (iter 064 ensemble closures)**: 074 (iter 016 SPY-co-exposed) → 89 v1 / 95 v2 retro, ρ legs 0.79-0.84, **closes SPY-co-exposed axis at 89**. 075 (UNLEVERED GLD/TLT, 7 cfgs) → 81, ρ=0.24 ✓, sleeve CAGR 3% dilutes, **closes unlevered non-equity axis at 81**. 076 (LEG-LEVERED GLD/TLT @4.5% borrow, 20 cfgs) → 85, gates 7/7/7, PBO 0.05 (wider 4×5 grid), borrow-Sharpe identity vindicated (3× lev→1.7×/1.4×/1.1× CAGR), **closes levered non-equity axis at 85**. **JOINT CONSTRAINT**: 90+→95 needs 2nd leg with both ρ<0.5 AND naturally high pre-borrow Sharpe ≥0.7-1.0 — DBMF / MTUM-VLUE long-short were next candidates.
- **iter 077 (LS MTUM-VLUE factor sleeve, 20 cfgs)**: → 85, gates 7/7/7, PBO 0.24/0.19/0.06, low-ρ vindicated (corr(sleeve,SPY)=0.06, corr(sleeve,iter064)=0.13), but **MTUM-VLUE Sharpe 0.13-0.22 in 2013-2026 (NOT 0.6-0.8 hypothesised)** — McLean-Pontiff 2016 factor decay vindicated; cross-sectional academic deciles spread (AMP 2013) does NOT translate to factor-ETF LS pair. **Closes LS factor sleeve axis at 85**. KILL H establishes **CAGR floor structural to iter 064 ANCHOR**: 3 independent sleeve mechanisms (unlevered, levered, factor LS) all converge at ~9.5% combined CAGR ceiling. **10-iter pattern (064/068-072 + 074-077) PROVES iter-064-anchored family caps at 90 single / 85 ensemble across ALL 3 sleeve mechanism classes**. Path forward: ABANDON iter 064 anchor.

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
