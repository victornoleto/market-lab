---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 74
winners_found: 0
status: iterating
latest_iteration: "074-2026-04-25-1724"
cumulative_n_trials: 4381
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
| **6** | **072** | 🥇 STRONG | **85** | `iter064_vix_cond_calm010_stress005` | `[algo_trading_chan, p.95, p.153-154]` + Whaley 2009 + Connors-Alvarez 2009 | TIES iter 058; 6/10 KILLS; KILL E inverted (r_064 calm-defensive); regime-cond 3rd-stream axis closed |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 074 — 2026-04-25 — iter016-iter064-ensemble (🥇 STRONG, 89/100, 4/5 strict winner conds met, DSR sole gap)
- **Result:** Best cfg `iter074_ensemble_w016_050` — S edu/spy/ndx 1.112/1.241/1.298 (Δ frozen +0.43/+0.34/+0.34 winner #1 3/3, Δ064 −0.11/−0.09/−0.08 KILL A 3/3), CAGR 12.41/13.93/15.47% (floor 3/3), MDD 21.5/21.0/18.5%, gates 6/6/6×3 (cross-ds bonus), **PBO 0.04/0.13/0.17 best-of-hunt-loop**, DSR p 0.094/0.083/0.065 (KILL B 3/3 above 0.05, n=4381), corr legs 0.79/0.84/0.79, Markowitz res=0, G7=0pp, robust 9/9 (+5 bonus), 15/15 TDD. winner=4/5; score 1:25 2:19 3:10 4:15 5:15 6:5 = **89**; 3/9 KILLS A+B+C.
- **Lesson:** SPY-co-exposed saved-stream ensemble has hard ρ floor 0.78-0.85 (both legs carry SPY beta) → combined S ≈ linear avg ≈ 1.24 < iter 064's 1.33 → DSR doesn't crack at n=4381. **Closes SPY-co-exposed saved-stream-ensemble axis at 89.** 7-iter pattern (064/068-072 overlays + 074 ensemble) confirms 90 ceiling persists across mechanisms AND ensembles. iter 075 must use 2nd leg ρ<0.5 vs 064 (non-equity) OR S>1.30 OR market-beta-neutral. See `iterations/074-*/`.

### 073 — 2026-04-25 — gayed-ma-gate-on-iter016 (🥈 PROMISING, 62/100)
- **Result:** S edu/spy/ndx 0.99/0.97/1.03 (Δcustom +0.36/+0.07/+0.08 KILL A 2/3), CAGR 16.0/15.7/19.2%, MDD 31/31/27%, gates 5/5/5×3, PBO 0.96/0.92/0.68 (KILL F), DSR p 0.24/0.41/0.35 (n=4360, KILL H), G7 ≤0.144pp, 13/13 TDD. vs iter 016 Sharpe −0.16 spy/ndx, MDD +4-5pp — gate net harmful post-GFC. winner=1/5; score 1:10 2:17 3:0 4:15 5:15 6:5 = 62; 4/9 KILLS A+B+F+H.
- **Lesson:** Gayed's edge non-stationary (mega-bears absent from post-GFC Tiingo). **Closes Gayed-MA-gate-as-overlay axis at 62**. See `iterations/073-*/`.

### 072 — 2026-04-25 — iter064-vix-cond-r-mr-allocation (🥇 STRONG, 85/100)
- **Result:** S 1.23/1.35/1.39 (Δ064 +0.01-0.02 KILL A 3/3), CAGR 9.08/9.57/9.72% (edu<9.18 KILL B), MDD 16/14/14%, gates 7/7/7×3, PBO 0.03/0.23/0.32, DSR p=0.033 spy (n=4348), G7=0pp×3, 16/16 TDD; KILL E INVERTED 3/3. winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85; 6/10 KILLS A+B+C+D+E+I.
- **Lesson:** Closes regime-cond 3rd-stream allocation on iter 064. **5-iter pattern (064/068/069/070/071/072) PROVES 90 ceiling iter-064-anchored**. See `iterations/072-*/`.

### 071 — 2026-04-25 — iter064-plus-spy-mr-rsi2 (🥇 STRONG, 90/100, 4-way TIES iter 064/069/070)
- **Result:** S 1.234/1.349/1.390 (Δ064 +0.015 ×3), CAGR 9.27/9.76/9.93%, MDD 16/15/14%, gates 7/7/7×3, DSR p=0.0335 spy (n=4344), G7 0pp×3, robust 9/9; KILL D vindicated, KILL G fires (corr=0.999). winner=4/5; score 90; 2/10 KILLS A+G.
- **Lesson:** Calm-aggressive 3rd stream EMPIRICALLY VINDICATED but saturates at 90 — composition's CAGR ceiling anchored in iter 046+r_qqqt. See `iterations/071-*/`.

### 070 — 2026-04-25 — iter064-t10y3m-cont-inner-weight (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 ≈0 KILL A 3/3), CAGR 9.69/10.23/10.39%, gates 7/7/7, DSR p=0.0435 spy (n=4340); winner=4/5; score 90; 4/11 KILLS A/F/H/I.
- **Lesson:** Continuous T10Y3M ≈ binary VIX — both saturate at 90; closes regime-classifier-resolution × signal-orthogonality. See `iterations/070-*/`.

### 069 — 2026-04-25 — iter064-vix-inner-weight-reverse (🥇 STRONG, 90/100)
- **Result:** S 1.21/1.32/1.36 (Δ064 ≈0, Δ068 +0.03-0.04 KILL I clean), CAGR 9.36/9.89/9.97%, gates 7/7/7, DSR p=0.0429 spy (n=4339); winner=4/5; score 90; 1/9 KILLS A.
- **Lesson:** Reverse beats iter 068 original (KILL I generalises) but doesn't lift Sharpe above 064 static. Closes VIX-inner-swap BOTH directions at 90. See `iterations/069-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Result:** S 1.17/1.28/1.33 (Δ064 −0.04 to −0.05), CAGR 9.53/10.04/10.30%, MDD +1-2pp, gates 6/6/6, DSR p=0.059 spy; winner=3/5; score 79; 1/9 KILLS I.
- **Lesson:** Conditional-Sharpe ordering falsified — BOTH 064 sub-streams defensive in stress 3/3. See `iterations/068-*/`.

### 067 — 2026-04-25 — iter064-vol-target-cap10 (🥈 PROMISING, 74/100)
- **Result:** S 1.17/1.26/1.28 (Δ064 −0.05 to −0.09), CAGR 7.61/7.93/7.93% (edu KILL D), gates 6/6/6, DSR p=0.076; winner=3/5; score 74; 3/8 KILLS A+C+D.
- **Lesson:** MM σ⁻² cap-1.0 overlay on saturated 064 drops mean faster than variance — inner stack already vol-managed. See `iterations/067-*/`.

### 066 — 2026-04-25 — meta-label-rf-iter064 (📉 NEAR_FAIL, 37/100)
- **Result:** S 0.66/0.81/0.65 (Δ064 −0.52 to −0.72), AUC 0.50 KILL H 3/3, gates 5/6/5; winner=1/5; score 37; 5/8 KILLS A+B+C+D+H.
- **Lesson:** Bar-level 1-day sign of Markowitz-saturated composite informationally null. Extends iter 013 LR closure to tree models. See `iterations/066-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100)
- **Result:** S 1.12/1.19/1.23 (Δ064 −0.10 to −0.14 KILL A 2/3), CAGR +1.5pp vs 064, gates 6/6/6, DSR p=0.114; winner=3/5; score 74; 2/7 KILLS A+C.
- **Lesson:** Closes calm-cond ext-lev at 1.5×/borrow=rf+25bps. See `iterations/065-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-**074**. **iter 064 still TOP-K #1 STRONG 90 (4-WAY TIED with iter 069/070/071), 0/7 KILLS.** iter 074 (iter 016 + iter 064 saved-stream ensemble, 7 weight cfgs) → **89 STRONG, 4/5 strict winner conds met (DSR sole gap)**, 3/9 KILLS A+B+C; engine perfect (15/15 TDD, G7=0pp, Markowitz res=0, PBO 0.04-0.17 best-of-hunt-loop, robustness 9/9). **Empirical ρ legs 0.79-0.84 > BASE_MEMORY's 0.6-0.8 prediction** — both streams carry SPY market beta substantially → variance reduction insufficient. Combined Sharpe ≈ linear avg (1.24 spy < iter 064 standalone 1.33). **7-iter pattern (064/068/069/070/071/072 + 074 ensemble) PROVES 90 ceiling persistent across BOTH overlay mechanisms AND SPY-co-exposed ensembles.** Direction shift: 90→95 unlock requires either (a) 2nd leg ρ < 0.5 vs iter 064 (non-equity anchor: commodities/FX/international/crypto) OR (b) 2nd leg standalone Sharpe > 1.30 OR (c) long-short market-beta-neutral overlay.

### Iter 075 candidates (SPY-co-exposed ensemble closed at 89; remaining lever = NON-SPY-CO-EXPOSED 2nd leg)

- **#1 Plano C sleeve as 2nd leg — RECOMMENDED** (BASE_MEMORY direction #5 promoted). Build passive factor-tilted Plano C ETF sleeve (GDE/AVUV/AVDE/AVEM/BTGD per `portfolio-aposentadoria.md`) as 2nd leg, ensemble with iter 064. International + small-cap value + emerging + crypto-gold = structurally divergent from SPY beta. Predicted ρ < 0.5; CAGR floor preserved (Plano C targets 7-10% net). Doubly useful: composability finding + Plano C tilt research signal. Citations: AVUV/AVDE/AVEM Avantis prospectuses; Erb-Harvey (2006) FAJ 62(2). Cost: medium (Tiingo factor-ETF cache verify needed).
- **#2 BTC/Gold (DBMF/GLD) as 2nd leg.** Managed futures or gold-and-crypto overlay structurally orthogonal to SPY. Tiingo cache likely has GLD; BTC via overlay parquet. Predicted ρ < 0.4. Citations: Erb-Harvey (2006), Asness-Moskowitz-Pedersen (2013) JoF 68(3).
- **#3 Long-short market-beta-neutral factor sleeve** (HML/UMD long-short on factor ETFs MTUM-VLUE / IWF-IWD) sized to net ~0% market beta. Mechanism: long-short cancellation decorrelates by construction. Predicted ρ < 0.3. **Requires Tiingo factor-ETF cache.**
- **#4 Multi-asset Hurst-regime trend** (Mandelbrot/Peters/Lo-MacKinlay) — continuous adaptive regime vs Gayed binary. Higher cost. Predicted 65-85.
- **#5 Forward 5-day Sharpe meta-label on iter 064** (open from iter 067). Predicted 65-85.
- **#6 CRSP/Norgate** (data budget).

DEAD-LETTER (all iter 064 base regime-allocation axes / saved-stream-pairs / 046-family / HYG / HMM-2 / FX carry / MTUM-QUAL-USMV not cached / cross-sectional mom Tiingo / broader-region VRP 5-leg / ext-lev / commodity TSM basket / eq075 / internal-LETF / Faber QQQ-200d / VIX-calm-cond ext lev / bar-level RF meta-label / σ⁻² cap-1.0 overlay / VIX-cond inner-weight BOTH DIRECTIONS / continuous T10Y3M z-score inner weight / Connors RSI(2) calm-aggressive 3rd stream / VIX-binary regime-conditional 3rd-stream allocation / **Gayed (2016) 200-day MA regime gate on iter 016 vol-managed stack**): see iters 045/047-073 entries.

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
- **iter 064 (TOP-K #1, Faber QQQ-200d sub for HYG_TSM at w=0.10)**: 90, 0/7 KILLS, first 90+. edu 9.49%>9.18% (1st non-LETF unlock). Closes single-asset-equity-trend-3rd-stream axis at w=0.10.
- **iter 065-073 closures**: 065 VIX-calm ext-lev → 74; 066 RF meta-label → 37 (AUC≈0.50, extends iter 013 closure to trees); 067 σ⁻² overlay → 74 (σ⁻² family saturates); 068 VIX inner-swap → 79 (KILL I 3/3 — both sub-streams defensive in stress); 069 REVERSE inner-swap → 90 TIES 064 (closes inner-swap both directions); 070 continuous T10Y3M inner weight → 90 TIES 064 (closes regime-classifier resolution × signal-orthogonality); 071 Connors RSI(2) MR 3rd stream → 90 TIES 064 (calm-aggressive vindicated, saturates 90); 072 VIX-cond r_mr allocation → 85 (KILL E inverted 3/3, closes regime-cond axis); 073 Gayed-MA-gate on iter 016 → 62 (gate net-harmful post-GFC, edge non-stationary).
- **iter 074 (iter 016 + iter 064 saved-stream ensemble; 7 weight cfgs)**: 🥇 STRONG **89, 4/5 strict winner conds met** (DSR sole gap), 3/9 KILLS A+B+C. Engine perfect (15/15 TDD, Markowitz res=0, G7=0pp, PBO 0.04/0.13/0.17 best-of-hunt, robust 9/9). Best cfg `iter074_ensemble_w016_050`: S 1.11/1.24/1.30 (Δ frozen +0.43/+0.34/+0.34, Δ064 −0.11/−0.09/−0.08), CAGR 12.41/13.93/15.47% (floor 3/3), MDD 21.5/21.0/18.5%, gates 6/6/6×3, DSR p 0.094/0.083/0.065. **Empirical ρ legs 0.79-0.84 > BASE_MEMORY's 0.6-0.8** (both carry SPY beta) → variance reduction insufficient. **Closes SPY-co-exposed saved-stream-ensemble axis at 89**. 7-iter pattern (064/068/069/070/071/072 overlays + 074 ensemble) confirms 90 ceiling persists across BOTH mechanisms AND SPY-co-exposed ensembles. iter 075 must use 2nd leg with ρ<0.5 vs iter 064 (non-equity) OR standalone S>1.30 OR market-beta-neutral overlay.

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
