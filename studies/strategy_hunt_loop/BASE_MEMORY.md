---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 76
winners_found: 0
status: iterating
latest_iteration: "076-2026-04-25-2356"
cumulative_n_trials: 4462
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
| **6** | **072** | 🥇 STRONG | **85** | `iter064_vix_cond_calm010_stress005` | `[algo_trading_chan, p.95, p.153-154]` + Whaley 2009 + Connors-Alvarez 2009 | TIES iter 058/076; 6/10 KILLS; KILL E inverted (r_064 calm-defensive); regime-cond 3rd-stream axis closed |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 076 — 2026-04-25 — iter064-plus-LEVERED-gld-tlt-trend-sleeve (🥇 STRONG, 85/100, 4/5 strict winner conds met)
- **Result:** Best cfg `iter076_lev_tv015_w015` (tv=0.15, w=0.15, leg_cap=3.0, borrow=4.5%); S edu/spy/ndx 1.231/1.325/1.352 (Δ064 +0.010/−0.006/−0.028 — no regress), CAGR 8.80/9.10/9.15% (floor 0/3 — same gap as iter 075), MDD 15.7/14.0/13.5%, **gates 7/7/7** (vs iter 075's 6/6/7), **PBO 0.048/0/0** (vs iter 075's 0.86/0.60/0.46 — wider 4×5 grid solved both axes), DSR p 1.31e-5/1.45e-5/1.21e-5 (v2 n=20), G7=0pp on all 20 cfgs, robust 9/9, 23/23 TDD. winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = **85**; 1/7 KILLS B (sleeve gross CAGR ≤6% at tv=0.30 on 3/3 ds = 5.45/3.94/2.65% — borrow drag eats CAGR scaling per pre-committed math). 20 cfgs × 3 ds = 60 trials; cumulative 4402→4462.
- **Lesson:** Borrow-Sharpe identity `[leverage_for_the_long_run, ch.5]` vindicated — 3× nominal leverage → only 1.7×/1.4×/1.1× CAGR scaling at 4.5% borrow on Sharpe-0.5 sleeve. **Closes iter-064 + leg-LEVERED Faber-trend non-equity sleeve ensemble axis at 85**. +4 vs iter 075 from grid-design (PBO + gates), NOT from leverage. **9-iter pattern (064/068-072 + 074 + 075 + 076) PROVES 90 ceiling across BOTH unlevered AND levered iter-064-anchored ensembles**. 90+→95 unlock now requires 2nd leg with naturally high pre-borrow Sharpe (≥0.7-1.0) — iter 077: download DBMF managed-futures OR MTUM-VLUE long-short. See `iterations/076-*/`.

### 075 — 2026-04-25 — iter064-plus-gld-tlt-trend-sleeve (🥇 STRONG, 81/100)
- **Result:** S edu/spy/ndx 1.238/1.340/1.373 (Δ064 +0.021/+0.008/−0.003), CAGR 8.58/8.91/9.01% (floor 0/3), MDD 15.4/13.7/13.2%, gates 6/6/7, corr(064,sleeve) 0.241 spy (3.4× lower than iter 074), DSR p 1.96e-5/3.03e-5/2.64e-5 (v2 n=7), PBO 0.86/0.60/0.46 (KILL F 2/3), G7=0pp, Markowitz res=0, robust 9/9, winner=4/5; score 1:25 2:21 3:15 4:0 5:15 6:5 = 81; 1/7 KILL F.
- **Lesson:** Non-SPY-co-exposed thesis vindicated (low ρ) but sleeve standalone CAGR 3% dilutes combined CAGR below floor. **Closes iter-064 + non-equity unlevered Faber-trend sleeve ensemble axis at 81**. JOINT constraint: 90→95 needs ρ<0.5 AND sleeve CAGR≥8-10% — iter 074 had CAGR/lacked ρ; iter 075 has ρ/lacks CAGR. See `iterations/075-*/`.

### 074 — 2026-04-25 — iter016-iter064-ensemble (🥇 STRONG, 89/100)
- **Result:** S edu/spy/ndx 1.11/1.24/1.30 (Δ064 −0.11/−0.09/−0.08), gates 6/6/6, DSR p 0.094/0.083/0.065 (n=4381), winner=4/5; score 1:25 2:19 3:10 4:15 5:15 6:5 = 89; ρ legs 0.79-0.84.
- **Lesson:** SPY-co-exposed ensemble has ρ floor 0.78-0.85 → linear-avg combined S < iter 064's 1.33. **Closes SPY-co-exposed saved-stream-ensemble axis at 89**. v2 retroactive = 95 WINNER but loop continues for structural-novelty robust winner. See `iterations/074-*/`.

### 073 — 2026-04-25 — gayed-ma-gate-on-iter016 (🥈 PROMISING, 62/100)
- **Result:** S 0.99/0.97/1.03 (Δcustom +0.36/+0.07/+0.08), gates 5/5/5, PBO 0.96/0.92/0.68 (KILL F), DSR p 0.24/0.41/0.35 (n=4360, KILL H), winner=1/5; score 1:10 2:17 3:0 4:15 5:15 6:5 = 62; 4/9 KILLS A+B+F+H.
- **Lesson:** Gayed's edge non-stationary (mega-bears absent from post-GFC Tiingo); gate net-harmful. **Closes Gayed-MA-gate-as-overlay axis at 62**. See `iterations/073-*/`.

### 072 — 2026-04-25 — iter064-vix-cond-r-mr-allocation (🥇 STRONG, 85/100)
- **Result:** S 1.23/1.35/1.39 (Δ064 +0.01-0.02), CAGR 9.08/9.57/9.72% (edu<9.18 KILL B), gates 7/7/7, DSR p=0.033 spy (n=4348), winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85; 6/10 KILLS A+B+C+D+E+I.
- **Lesson:** Closes regime-cond 3rd-stream allocation on iter 064. **5-iter pattern (064/068/069/070/071/072) PROVES 90 ceiling iter-064-anchored**. See `iterations/072-*/`.

### 071 — 2026-04-25 — iter064-plus-spy-mr-rsi2 (🥇 STRONG, 90/100, 4-way TIES iter 064/069/070)
- **Result:** S 1.23/1.35/1.39 (Δ064 +0.015 ×3), CAGR 9.27/9.76/9.93%, gates 7/7/7, DSR p=0.0335 spy (n=4344), winner=4/5; score 90; 2/10 KILLS A+G.
- **Lesson:** Calm-aggressive 3rd stream vindicated but saturates at 90 — composition's CAGR ceiling anchored in iter 046+r_qqqt. See `iterations/071-*/`.

### 070 — 2026-04-25 — iter064-t10y3m-cont-inner-weight (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 ≈0), CAGR 9.69/10.23/10.39%, gates 7/7/7, DSR p=0.0435 spy (n=4340), winner=4/5; score 90; 4/11 KILLS A/F/H/I.
- **Lesson:** Continuous T10Y3M ≈ binary VIX — both saturate at 90; closes regime-classifier × signal-orthogonality. See `iterations/070-*/`.

### 069 — 2026-04-25 — iter064-vix-inner-weight-reverse (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 ≈0, Δ068 +0.03-0.04), gates 7/7/7, DSR p=0.0429 spy (n=4339), winner=4/5; score 90; 1/9 KILLS A.
- **Lesson:** Reverse beats iter 068 original (KILL I generalises) but doesn't lift Sharpe above 064 static. Closes VIX-inner-swap BOTH directions at 90. See `iterations/069-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Result:** S 1.17/1.28/1.33 (Δ064 −0.04 to −0.05), CAGR 9.53/10.04/10.30%, gates 6/6/6, DSR p=0.059 spy, winner=3/5; score 79; 1/9 KILLS I.
- **Lesson:** Conditional-Sharpe ordering falsified — BOTH 064 sub-streams defensive in stress 3/3. See `iterations/068-*/`.

### 065-067 — 2026-04-25 — iter064-anchored variants (compressed batch)
- **065** (🥈 74, vix-output-lev-gate at 1.5×/borrow=rf+25bps) S 1.12/1.19/1.23 (Δ064 −0.10 to −0.14), gates 6/6/6, DSR p=0.114; closes calm-cond ext-lev. **066** (📉 37, RF meta-label) S 0.66/0.81/0.65, AUC 0.50 (KILL H 3/3) — bar-level 1-day sign null on Markowitz-saturated composite; extends iter 013 LR closure to trees. **067** (🥈 74, σ⁻² overlay) S 1.17/1.26/1.28, gates 6/6/6 — MM σ⁻² drops mean faster than variance on already-vol-managed 064. See `iterations/065-067-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-**076**. **iter 064 still TOP-K #1 STRONG 90 (4-WAY TIED with iter 069/070/071), 0/7 KILLS.** iter 076 (iter 064 + LEVERED GLD/TLT trend sleeve ensemble, 20 cfgs at tv∈{0.15,0.20,0.25,0.30}×w∈{0.15,0.25,0.35,0.45,0.50}, leg_cap=3.0, borrow=4.5%) → **85 STRONG, 4/5 strict winner conds met** (CAGR floor sole gap), 1/7 KILL B (sleeve gross CAGR ≤6% at tv=0.30 on 3/3 ds — borrow drag eats CAGR scaling per `[leverage_for_the_long_run, ch.5]` identity). +4 vs iter 075 from grid-design (PBO 0.05, gates 7/7/7); leverage hypothesis FALSIFIED. **9-iter pattern (064/068-072 + 074 SPY-co-exposed + 075 unlevered + 076 levered) PROVES 90 ceiling across BOTH unlevered AND levered iter-064-anchored ensemble families.**

### Iter 077 candidates (joint constraint: 2nd leg with naturally high pre-borrow Sharpe ≥ 0.7-1.0)

- **#1 DBMF managed-futures Tiingo download — RECOMMENDED** (mechanical fix from iter 076). DBMF (iMGP DBi Managed Futures Strategy ETF, inception 2019-05-08) tracks SocGen CTA Trend Index. Historical Sharpe 0.5-0.7, CAGR 7-10%, ρ ≈ 0.0-0.2 with SPY (AMP 2013). **REQUIRES Tiingo download (5-10 min)** + acceptance of the post-2019 sleeve start-date asymmetry on full-window iter 064 ensemble. Boundary case for joint-constraint test. If sleeve Sharpe holds the iter-076 borrow-Sharpe identity predicts post-drag Sharpe ~0.4-0.5 still — close to iter 075's unlevered case but with materially higher CAGR. Citations: AMP (2013) JoF 68(3) DOI 10.1111/jofi.12021.
- **#2 Long-short MTUM-VLUE factor sleeve Tiingo download** — MTUM (iShares MSCI USA Momentum, 2013-05) and VLUE (iShares MSCI USA Value, 2013-05) — 13y history, fits all 3 datasets cleanly. Dollar-neutral long-short construction yields ρ ≈ 0.0-0.3 with SPY by construction; standalone Sharpe 0.4-0.7. **Requires Tiingo download** (smaller risk than DBMF — both ETFs liquid). If Sharpe ≥ 0.7 holds on long-short construction, cleanest test of high-Sharpe-2nd-leg hypothesis. Citations: Carhart (1997) JoF 52(1) + AMP (2013).
- **#3 Multi-asset Hurst-regime adaptive trend** (Mandelbrot/Peters/Lo-MacKinlay) — continuous adaptive regime via Hurst exponent on multi-asset universe. Structurally novel mechanism class (continuous-regime memory-based trend) vs binary SMA-regime. Higher implementation cost. Predicted 65-85.
- **#4 Forward 5-day Sharpe meta-label on iter 064** (open from iter 067). Structurally distinct from iter 066's 1-day sign meta-label. Predicted 65-85.
- **#5 CRSP/Norgate cross-sectional momentum** (data budget; iter 054 closed Tiingo cross-sectional due to survivorship).

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
- **iter 074-076 (iter 064 ensemble closures)**: 074 (iter 016 SPY-co-exposed) → 89 v1 / 95 v2 retro, ρ legs 0.79-0.84, **closes SPY-co-exposed axis at 89**. 075 (UNLEVERED GLD/TLT, 7 cfgs) → 81, ρ=0.24 ✓, sleeve CAGR 3% dilutes, **closes unlevered non-equity axis at 81**. 076 (LEG-LEVERED GLD/TLT @4.5% borrow, 20 cfgs) → 85, gates 7/7/7, PBO 0.05 (wider 4×5 grid), borrow-Sharpe identity vindicated (3× lev→1.7×/1.4×/1.1× CAGR), **closes levered non-equity axis at 85**. **JOINT CONSTRAINT**: 90+→95 needs 2nd leg with both ρ<0.5 AND naturally high pre-borrow Sharpe ≥0.7-1.0 — DBMF / MTUM-VLUE long-short are next candidates. **9-iter pattern (064/068-072 + 074-076) PROVES 90 ceiling across iter-064-anchored ensemble family**.

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
