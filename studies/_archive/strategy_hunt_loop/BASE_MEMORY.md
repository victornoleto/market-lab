---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 79
winners_found: 1
status: winner
latest_iteration: "079-2026-04-26-1100"
cumulative_n_trials: 4573
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

```yaml
- iteration: "079-2026-04-26-1100-multi-asset-topk-momentum"
  best_cfg_id: "iter079_topk_lb06m_k3"
  config: {lookback_months: 6, top_k: 3, abs_threshold: 0.0, trans_cost_bps: 5.0,
           universe_selectable: [SPY, QQQ, EFA, TLT, GLD], fallback: AGG,
           rebalance: monthly_last_bday}
  score: 93
  tier: WINNER
  winner_conditions_met: 5/5
  kills_fired: 0/8
  metrics_per_ds:  # {sharpe, cagr, mdd, dsr_p, gates}
    educational: {S: 0.993, CAGR: 0.1201, MDD: 0.2474, dsr_p: 2.66e-3, gates: 6/7}
    spy_real:    {S: 1.094, CAGR: 0.1300, MDD: 0.2474, dsr_p: 1.84e-3, gates: 7/7}
    ndx_real:    {S: 1.086, CAGR: 0.1269, MDD: 0.2474, dsr_p: 2.66e-3, gates: 7/7}
  datasets_passing:
    {sharpe_edge: 3/3, gates_threshold: 3/3, cagr_floor: 2/3,
     mdd_ceiling: 3/3, dsr_alpha005: 3/3}
  citation_primary: "[stocks_on_the_move, p.21-30, p.81] + Antonacci 2014 + Faber 2007 + Jegadeesh-Titman 1993 + [advances_fin_ml, p.162-164]"
  honest_caveats:
    - "ndx_real CAGR floor missed (12.69% < 15.35%); rubric requires only 2/3"
    - "PBO 0.5714 edu marginal (spy 0.31 / ndx 0.41 clean)"
    - "Single-cfg winner: 1/9 strict (K=3 ridge 73/93/73)"
  iteration_dir: "iterations/079-2026-04-26-1100-multi-asset-topk-momentum/"
  status: "CANDIDATE — mandate §1 MAINTENANCE 100% Plano C in force; §7 override = user deliberation"
```

---

## Top-K ranked (best across all iters, by score)

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| **1** | **079** | 🏆 WINNER | **93** | `iter079_topk_lb06m_k3` | `[stocks_on_the_move, p.21-30, p.81]` + Antonacci 2014 + Faber 2007 + Jegadeesh-Titman 1993 | **FIRST WINNER in 79 iters; 5/5 strict conds; 0/8 kills; S 0.99/1.09/1.09; CAGR 12/13/12.7%; spy CAGR floor cleared 1st time** |
| **2** | **064** | 🥇 STRONG | **90** | `iter046_plus_qqq_trend_w010_lookback200` | Faber 2007 + `[stocks_on_the_move, p.21-30]` | prior TOP-K #1 (joint); 0/7 kills; 7/7×3; DSR<0.05×3; 4/5 winner; static `w=0.10` Sharpe-maximal |
| **2** | **069** | 🥇 STRONG | **90** | `iter064_vix_inner_w_calm005_stress020_vix20` | Faber 2007 + `[stocks_on_the_move, p.21-30]` + iter 068 KILL I | TIES iter 064; 1/9 KILLS A; 7/7×3; DSR<0.05×3; 4/5 winner |
| **2** | **070** | 🥇 STRONG | **90** | `iter064_t10y3m_cont_alpha025_lb1260_w005_020` | `[advances_fin_ml, ch.17-18]` + Estrella-Mishkin 1998 + Faber 2007 | TIES iter 064/069; 4/11 KILLS A/F/H/I; 7/7×3; continuous T10Y3M ≈ binary VIX |
| **2** | **071** | 🥇 STRONG | **90** | `iter064_plus_spy_mr_rsi2_th10_w005` | `[algo_trading_chan, p.95, p.153-154]` + Connors-Alvarez 2009 + Lo-MacKinlay 1988 | 4-way TIES iter 064/069/070; 2/10 KILLS A/G; 7/7×3; calm-aggr 3rd stream KILL D vindicated cross-cfg cross-ds |
| **6** | **074** | 🥇 STRONG | **89** | `iter074_ensemble_w016_050` | Markowitz (1952) + `[risk_parity, ch.5]` + Moreira-Muir (2017) + Faber 2007 | iter 016+064 saved-stream blend 50/50; 4/5 strict winner conds met (DSR sole gap); 6/6/6×3 + bonus; PBO 0.04/0.13/0.17 best-of-hunt; ρ 0.79-0.84 |
| **7** | **076** | 🥇 STRONG | **85** | `iter076_lev_tv015_w015` | `[leverage_for_the_long_run, ch.5]` + Faber 2007 + Frazzini-Pedersen 2014 | iter 064 + LEG-LEVERED GLD/TLT @ 4.5% borrow; 4/5 winner conds (CAGR floor sole gap); 7/7/7 gates + PBO 0.05 |
| **7** | **077** | 🥇 STRONG | **85** | `iter077_lsfac_tv006_w010` | Carhart 1997 + AMP 2013 + `[advances_fin_ml, ch.3]` + McLean-Pontiff 2016 | iter 064 + LS MTUM-VLUE factor sleeve; 4/5 winner conds (CAGR floor sole gap); 7/7/7 gates |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 079 — 2026-04-26 — multi-asset-topk-momentum-5plus1-cross-class (🏆 **WINNER**, 93/100)
- **Result:** Best cfg `iter079_topk_lb06m_k3` (lb=6mo, k=3, abs_th=0%); S edu/spy/ndx 0.993/1.094/1.086 (Δ_bench +0.31/+0.19/+0.13, **3/3 Sharpe edge — first iter**), CAGR 12.01/13.00/12.69% (floor 2/3 — edu+spy; **first iter clearing spy 11.98% floor**), MDD 24.74% × 3, gates 6/7/7 (PBO edu 0.57 marginal; spy 0.31; ndx 0.41), DSR p≤2.66e-3 (v2 n=9), G7=0.0000pp 27cfgs, robust 9/9, winner_conds **5/5**, **0/8 KILLS**; score 1:25 2:23 3:15 4:10 5:15 6:5 = 93. Universe SPY/QQQ/EFA/TLT/GLD selectable + AGG fallback; per-asset weights 22/25/14/12/16/12%.
- **Lesson:** **FIRST WINNER in 79 iters.** CAGR floor 2009-2026 is NOT sample-level binding (iter 078 thesis falsified) — it's UNIVERSE-level binding; cross-asset-class top-K destrava o teto via K=3 mantendo ~67% equity-equivalent (selection step modulates classe ATIVA, NOT exposure size). Caveats: ndx CAGR floor still misses (rubric 2/3 sufficient); PBO edu 0.57 marginal; single-cfg winner (K=3 ridge 73/93/73). Mandate §1 inalterado; §7 override é deliberação humana. Full detail: `iterations/079-*/`. Citações primárias: `[stocks_on_the_move, p.21-30, p.81]` + Antonacci 2014/2017 + Faber 2007 + Jegadeesh-Titman 1993 + AMP 2013 + Markowitz 1952 + `[advances_fin_ml, p.162-164, p.31-34, p.222-223, p.196-202, p.208-211]` + `[systematic_trading, ch.2]` + `[risk_parity, ch.5]`.

### 078 — 2026-04-26 — antonacci-3-asset-GEM-base (🥇 STRONG, 75/100)
- **Result:** Best lb03m_thzero; S 0.81/0.88/0.84 (Δ +0.13/−0.02/−0.12, 1/3), CAGR 10.79/11.42/10.71% (floor 1/3), MDD 21% × 3 (best MDD edge to that point), gates 7/7/7, PBO 0.15/0.06/0.12, DSR p≤2.97e-2 (v2 n=8), winner 3/5; score 1:10 2:25 3:15 4:5 5:15 6:5 = 75; 1/8 KILL H.
- **Lesson:** Antonacci 1974-2014 S 0.85-1.0 / CAGR 12-14% does NOT replicate 2009-2026 (US dominance + AGG drag). Hypothesised "sample-level CAGR floor binding" but iter 079 superseded this — floor is universe-level. See `iterations/078-*/`.

### 077 — 2026-04-26 — iter064-plus-LS-mtum-vlue-factor-sleeve (🥇 STRONG, 85/100)
- **Result:** S 1.208/1.333/1.373 (Δ064 −0.013/+0.002/−0.007), CAGR 8.95/9.34/9.48% (floor 0/3), MDD 17.27/14.24/13.70%, gates 7/7/7, PBO 0.24/0.19/0.06, DSR p≤2.57e-4 (v2 n=20), G7=0pp 20cfgs, robust 9/9, winner=4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85; 2/8 KILLS B+H fired.
- **Lesson:** MTUM-VLUE Sharpe 0.13-0.22 in 2013-2026 (NOT 0.6-0.8 hypothesised); McLean-Pontiff (2016) factor decay vindicated. Closes iter-064 + LS-factor-sleeve axis at 85; 3 sleeve classes (unlev/lev/factor) converge at ~9.5% combined CAGR — CAGR floor structural to iter 064 ANCHOR. See `iterations/077-*/`.

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

🏆 **HUNT LOOP HALTED** — iter 079 → WINNER (93/100, 5/5 strict conds, 0/8 kills). Shell loop reads `status: winner` in frontmatter and stops. **Iter 079 falsifies iter 078's "sample-level CAGR floor" thesis**: floor is UNIVERSE-level (single-equity universe binding) — multi-asset-class top-K rotation breaches it via K=3 holding ~67% equity-equivalent.

Consumed/closed: 002-005/007/009-014/017/019-**079**.

### Confirmation studies (NOT new iters — outside hunt loop scope)

User-deliberation aids:

- **Wider param grid sweep** on iter 079: lb {4,5,7,8 mo} × top_k {2,3,4}. Confirm WINNER cell sits in score-ridge ≥ 75 across 4-8 neighbors.
- **Paper trading 3-6 months** on iter 079 best cfg before §7 override.
- **Cross-sample validation** on different broker data feed or pre-2009 history if available.

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
- **iter 074-077 (iter-064 ensemble/sleeve closures)**: 074 (016 SPY-co-exposed) → 89; 075 (UNLEV GLD/TLT) → 81 ρ=0.24; 076 (LEV GLD/TLT @4.5% borrow) → 85 gates 7/7/7; 077 (LS MTUM-VLUE) → 85 (factor decay AMP 2013→McLean-Pontiff 2016 OOS gap). 10-iter pattern (064/068-072 + 074-077) caps at 90 single / 85 ensemble — abandons iter-064 anchor. JOINT CONSTRAINT: 90+→95 needs 2nd leg with ρ<0.5 AND pre-borrow S≥0.7. See `DEAD_ENDS.md`.
- **iter 078 (Antonacci canonical GEM standalone-base SPY/EFA/AGG, 8 cfgs)**: → 75 STRONG (best cfg 3-mo lb, 0% th), 3/5 strict winner conds (gates 7/7/7, DSR<0.05, MDD clear; Sharpe edge+CAGR floor fail cross-ds). 1/8 KILL H. Antonacci 12-mo only 42 MARGINAL — **published 1974-2014 S 0.85-1.0/CAGR 12-14% does NOT replicate 2009-2026** (US dominance + AGG drag ~1-2.5pp/yr). MDD 21% vs SPY 33.7% strongest MDD edge to that point but CAGR cost too high. Pattern hypothesised at iter 078 was "2009-2026 CAGR floor is SAMPLE-LEVEL binding"; **SUPERSEDED by iter 079 evidence — the floor is UNIVERSE-LEVEL, not sample-level**. **Closes Antonacci-canonical-standalone-base at 75**.
- **iter 079 🏆 WINNER (multi-asset top-K relative+absolute momentum, 5+1-asset cross-class universe, 9 cfgs)**: → **93/100, 5/5 strict winner conds, 0/8 KILLS**. Best cfg `iter079_topk_lb06m_k3` (lb=6mo, k=3): S 0.99/1.09/1.09 (Δ_bench +0.31/+0.19/+0.13 — **3/3 Sharpe edge, first iter**), CAGR 12.01/13.00/12.69% (**first iter to clear spy 11.98% floor**), MDD 24.74% × 3, gates 6/7/7 (PBO edu 0.57; spy 0.31; ndx 0.41), DSR p≤2.66e-3 (v2 n=9). **Falsifies iter 078's sample-level binding thesis**: cross-classe universo destrava o teto via K=3 mantendo ~67% equity-equivalent. Caveats: ndx CAGR floor still misses (2/3 sufficient); PBO 0.57 edu marginal; single-cfg winner (K=3 ridge 73/93/73). Mandate §1 inalterado; §7 override é deliberação do usuário. Full detail: `iterations/079-*/` + `DEAD_ENDS.md`.

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
