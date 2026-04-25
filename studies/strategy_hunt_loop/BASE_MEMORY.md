---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 68
winners_found: 0
status: iterating
latest_iteration: "068-2026-04-25-1758"
cumulative_n_trials: 4338
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
| **1** | **064** | 🥇 STRONG | **90** | `iter046_plus_qqq_trend_w010_lookback200` | Faber 2007 + `[stocks_on_the_move, p.21-30]` | TOP-K #1; 0/7 kills; 7/7×3; DSR <0.05×3; 4/5 winner conds; edu CAGR floor PASS |
| **2** | **058** | 🥇 STRONG | **85** | `iter046_plus_hyg_tsm_w010` | Asvanunt-Richardson 2017 | 7/7×3; HYG carry; CAGR-dilutive (replaced in iter 064) |
| **2** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Sinclair | 1st 7/7×3 + DSR<0.05×3; iter 064's 90% anchor |
| **4** | **053** | 🥇 STRONG | **84** | `iter037_plus_iter046_w070` | `[risk_parity, ch.5]` | corr 0.95 kill F pre-fired; 037-anchor exhausted |
| **4** | **051** | 🥇 STRONG | **84** | `iter037_plus_iter026_w080` | `[risk_parity, ch.5]` | 4/5 winner conds; DSR p=0.175 |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 068 — 2026-04-25 — iter064-vix-inner-weight-swap (🥇 STRONG, 79/100)
- **Hypothesis:** VIX-cond INNER Markowitz weight on iter 064 sub-streams: w_qqqt=0.20 calm / 0.05 stress; w_046=1−w_qqqt; total ≡ 1.0 (NO lev); cost 5bp×|Δw_qqqt|.
- **Citations:** `[stocks_on_the_move, p.21-30]` + Faber 2007 SSRN 962461 + `[risk_parity, ch.5]` + Whaley 2009 JPM 35(3) + `[advances_fin_ml, p.162-164/222-223/31-34]`.
- **Scope:** 1 cfg, 3 datasets, structurally orthogonal to iter 048/065 OUTPUT-scalar VIX gating and iter 067 σ⁻² overlay (operates on INNER Markowitz weight).
- **Result:** Sharpe edu/spy/ndx 1.17/1.28/1.33 (Δ frozen +0.49/+0.38/+0.37; Δ064 −0.043/−0.050/−0.049 — KILL A 1/3 only, NOT fired), CAGR 9.53/10.04/10.30% (Δ064 +0.04/+0.06/+0.13pp; edu unlock preserved), MDD 18.55/17.07/16.49% (Δ064 +1.28/+1.74/+1.75pp — grew), gates 6/6/6, DSR worst-p 0.0593 spy (Δ064 +0.020; n=4338), corr(068,064) 0.992-0.993, pct_calm 65-71%, flips/yr 14.5-16.3, max|Σw-1|=0 (3/3), G7 0pp (3/3), robustness 9/9, winner=3/5; score 1:25 2:19 3:10 4:5 5:15 6:5 = 79. 1/9 KILLS — only KILL I (cond Sharpe ordering falsified).
- **Score breakdown:** 1:25/25 2:19/25 3:10/15 4:5/15 5:15/15 6:5/5
- **Lesson:** Engine 100% clean (G7 0pp, Σw ≡ 1.0 strictly, 13/13 TDD pass) but DIRECTIONAL HYPOTHESIS empirically falsified — QQQ_TREND Sharpe stress (0.95-1.20) > calm (0.71-0.76) on 3/3 ds; r_046 stress (1.43-1.93) > calm (1.05-1.09) on 3/3. Both iter 064 sub-streams STRUCTURALLY DEFENSIVE in stress (QQQ_TREND parks cash via 200d-SMA; r_046 de-risks via inner iter_041 VIX gates). Closes calm-trend/stress-defensive inner-weight direction at 79. **REVERSE-direction swap (calm 0.05 / stress 0.20) is iter 069 #1 candidate** — directly tests iter 068's empirical evidence. See `iterations/068-*/`.

### 067 — 2026-04-25 — iter064-vol-target-cap10 (🥈 PROMISING, 74/100)
- **Result:** S 1.17/1.26/1.28 (Δ064 −0.05/−0.08/−0.09 KILL A 2/3), CAGR 7.61/7.93/7.93% (Δ064 −1.9/−2.0/−2.2pp KILL D edu), MDD 13/13/12% (✓), gates 6/6/6, DSR worst-p 0.076 spy (n=4337), scale_mean 0.88, pct_at_cap 65-67%, corr 0.94-0.96, winner=3/5; score 1:25 2:19 3:10 4:0 5:15 6:5=74. 3/8 KILLS A+C+D.
- **Lesson:** Moreira-Muir σ⁻² cap-1.0 overlay on saturated 064 hits same 74 ceiling as iter 065's +1.5× calm-lev — mean-exposure cap (0.88) drops mean faster than variance because inner stack already vol-managed. See `iterations/067-*/`.

### 066 — 2026-04-25 — meta-label-rf-iter064 (📉 NEAR_FAIL, 37/100)
- **Result:** S 0.66/0.81/0.65 (Δ064 −0.56/−0.52/−0.72 KILL A 3/3), CAGR 4.10/4.54/3.28% (Δ064 −5.4/−5.4/−6.9pp KILL D), gates 5/6/5, DSR worst-p 0.85 ndx (n=4336), AUC 0.503/0.503/0.492 (KILL H 3/3), winner=1/5; score 1:0 2:17 3:0 4:0 5:15 6:5=37. 5/8 KILLS A+B+C+D+H.
- **Lesson:** Bar-level 1-day sign of Markowitz-saturated composite is informationally null in standard regime/vol/momentum canon regardless of model class — extends iter 013 LR closure to tree models. See `iterations/066-*/`.

### 065 — 2026-04-25 — iter064-vix-output-lev-gate (🥈 PROMISING, 74/100)
- **Result:** S 1.12/1.19/1.23 (Δ064 −0.10/−0.14/−0.14 KILL A 2/3), CAGR 10.96/11.47/11.80% (Δ064 +1.47/+1.49/+1.63pp), gates 6/6/6, DSR p=0.114 worst-spy (n=4335, tripled from 064's 0.039), winner=3/5; score 1:25 2:19 3:5 4:5 5:15 6:5=74. 2/7 KILLS A+C.
- **Lesson:** iter 060 Sharpe-convention closure GENERALIZES to calm-only application — closes regime-conditional ext-lev at lev=1.5× / borrow=rf+25bps. See `iterations/065-*/`.

### Iters 015-064 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **064** (🥇 90 TOP-K #1, 0/7 KILLS, iter058-qqq-trend-substitution) S 1.22/1.33/1.38, CAGR 9.49/9.97/10.17% (1/3 floor — edu 1st-ever non-LETF unlock), MDD 17/15/15%, gates 7/7×3, DSR worst-p 0.0392 spy. **NEW TOP-K #1, breaks 85 ceiling. Faber 2007 QQQ-200d-trend at w=0.10 Pareto-dominates HYG_TSM. Path 95+ = close spy/ndx CAGR floor.**
- **063** (🥇 81, internal-letf-iter041-only on 058) S 1.17/1.26/1.35 (Δ058 −0.05/−0.09/−0.06 KILL A 3/3), 1/3 CAGR floor (edu unlock), DSR 0.076 spy regressed from 058's 0.049. **Internal-LETF axis EXHAUSTED both branches (037→79, 058→81); Sharpe-headroom thesis FALSIFIED. SOLVED in 064 via QQQ-200d-trend.**
- **062** (🥇 79, internal-letf-iter037) Internal-LETF on 037 anchor → SAME 79; 4× replication of iter 037-family ceiling. Vol decay + financing drag invariant.
- **061** (🥇 79, eq075+hyg-tsm) Closes iter 037-family weight-tuning; canonical 0.60/0.45/0.45 Sharpe-optimal.
- **060** (🥇 79, 058-levered-150) Closes external-leverage on 058 at borrow > 0.5pp above rf.
- **059** (🥇 79, 037+hyg-tsm-w010) Anchor substitution trades CAGR-floor for DSR-pass; saved-stream-pair Pareto bounded 79-85.
- **058** (🥇 85 prior TOP-K tied, hyg-credit-carry) S 1.22/1.35/1.40, DSR 0.049/0.034/0.026, CAGR 8.7/9.0/9.3% (0/3 floor). 3rd-stream-Sharpe thesis vindicated.
- **054-057**: 054 cross-sectional Tiingo S 0.66 (DATA closure → CRSP); 055 broader-region VRP 5-leg 73 < 039's 76; 056 ext 1.3× lev on 046 → 74; 057 commodity-basket 64 (basket S too low).
- **051-053** (🥇 79-84): 053 037+046 w=0.70 (84, corr 0.93-0.96 Kill F); 052 041+026 (79); 051 037+026 (84, 1st 4/5 winner conds). **Saved-stream-pair Pareto bounded 84.**
- **046** (🥇 85 prior TOP-K, 50/50 iter041+iter039) ρ=0.41; S 1.20/1.32/1.38, DSR 0.041/0.042/0.031, gates 7/7/7, CAGR 9.16/9.45/9.76. **5pt gap to WINNER = CAGR floor.**
- **042-050**: 042-044 regime perturbations regress DSR; 045 037+039 ρ=0.59 (81 superseded); 047 w_041 sweep (Bonferroni); 048 VIX output gate (83); 049 gold TSM 0.5 (Markowitz dilution); 050 90/10 046+gold (78).
- **041** (🥇 84 prior TOP-K, regime-weights-vix) S 1.03/1.13/1.16, DSR 0.168 (1st escape from 037's 0.222).
- **037-040** (69-79): 037 3-leg preserved-lev → 038 +VIX gate → 039 VRP basket (used in 045/046, family 76 ceiling) → 040 σ⁻² on 039.
- **033-036** (72-77): 3-leg variants (bond-carry/IEF/GLD); 77 ceiling asset-class-agnostic.
- **026-032** (54-79): VRP harvester family on 026 (76 ceiling, ndx 1st 7/7); +overlays (021/022/024/025/027); +VIX gates (028-030 → 71); 031 AND (76); 032 layered (72).
- **015-020** (39-79): 015 static NTSX 90/60 (77, 1st +0.10); 016 60:40×MM (79, ADDITIVE); 017 12-1 regional (52); 018 funding-cost (79); 019 HMM (0); 020 put-spread (79).

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

Consumed/closed: 002-005/007/009-014/017/019-**068**. **iter 064 still TOP-K #1 STRONG 90, 0/7 KILLS.** iter 068 (VIX-cond INNER-weight swap on 064, calm 0.20 / stress 0.05) → 79 STRONG, only KILL I (directional hypothesis empirically falsified — QQQ_TREND Sharpe is HIGHER in stress, 0.95-1.20 vs calm 0.71-0.76; r_046 also higher in stress 1.43-1.93 vs calm 1.05-1.09 — both sub-streams are STRUCTURALLY DEFENSIVE in stress). **iter 064's 90 = 8-axis-closed strict LOCAL OPTIMUM** (saved-stream-pair / internal-LETF / weight-sweep / output-VIX-gate / calm-cond-ext-lev / bar-level-meta-label / σ⁻² cap-1.0 / VIX-cond inner-weight calm-trend direction).

### Iter 069 candidates (iter 064 still TOP-K #1; iter 068 closed inner-weight calm-trend axis at 79; REVERSE-direction swap is the empirical-evidence-backed next test)

- **#1 REVERSE inner weight swap** (calm `w_qqqt = 0.05` / stress `w_qqqt = 0.20`, total ≡ 1.0). Direct test of iter 068's empirically-derived conditional Sharpe ordering (QQQ_TREND stress > calm on 3/3 ds). **Predicted 80-90 if ordering generalises OOS. RECOMMENDED — cleanest information-theoretic test; either confirms lesson (Sharpe lift +0.04-0.07 → potential 85-90 break) or refutes generalisation (closes inner-weight axis in BOTH directions).**
- **#2 Fresh AGGRESSIVE 3rd stream** (short-vol / VRP / convexity-buying with HIGH calm Sharpe and LOW stress Sharpe — opposite profile from QQQ_TREND, providing the missing aggressive complement to iter 064's defensive basin). Predicted 75-90. Harder to find (VRP universe limited; iter 057 closed commodity basket).
- **#3 Higher-resolution regime classifier** (T10Y3M continuous score replacing binary VIX gate, or HMM 3-state on returns). Predicted 78-87 — novel granularity could expose conditional Sharpe patterns invisible to binary VIX-20.
- **#4 Forward 5-day Sharpe meta-label** (still open from iter 067 final report; ~120 flips/yr vs 700/yr in iter 066). Predicted 60-85, high variance.
- **#5 Fresh anchor (not iter 046-derived)** — cross-asset trend on Hurst-based regime, or credit-spread regime as primary signal. High exploration cost.
- **#6 Plano C sleeve** (≤ 70). **#7 CRSP/Norgate** (data budget required).

DEAD-LETTER (saved-stream-pairs / 046-family / HYG / HMM-2 / FX carry / MTUM-QUAL-USMV not cached / cross-sectional mom Tiingo / broader-region VRP 5-leg / ext-lev / commodity TSM basket / eq075 / internal-LETF / Faber QQQ-200d / VIX-calm-cond ext lev / bar-level RF meta-label / σ⁻² cap-1.0 overlay / **VIX-cond inner-weight calm-trend direction**): see iters 045/047-058/059/061/062/063/064/065/066/067/068 entries.

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
- **iter 065 (VIX-calm-cond ext lev 1.5× on 064)**: 74 PROMISING −16, 2/7 KILLS A+C. CAGR +1.47/+1.49/+1.63pp but Sharpe drag −0.10/−0.14/−0.14 + DSR tripled. Closes calm-conditional ext-lev axis at lev=1.5×/borrow=rf+25bps.
- **iter 066 (RF meta-label on 064 daily 1-day sign, 5 features)**: 37 NEAR_FAIL −53, 5/8 KILLS. AUC 0.49-0.50 at chance × 3 ds. Bar-level 1-day sign of Markowitz-saturated composite is informationally null in standard regime/vol/momentum canon regardless of model class (extends iter 013 LR closure to trees). 700 flips × 5 bps ≈ 30 pp friction.
- **iter 067 (MM σ⁻² overlay on 064, cap=1.0)**: 74 PROMISING, 3/8 KILLS A+C+D. Combined with 065's +1.5× calm-lev, σ⁻² overlay family saturates at **74 ceiling for cap ∈ [1.0, 1.5×]**. Generalises iter 016's MM 79 ceiling to saturated-composite with mean-exposure-cap-drag.
- **iter 068 (VIX-cond INNER weight swap on 064, calm 0.20 / stress 0.05)**: 79 STRONG, only 1/9 KILLS (I — directional hypothesis falsified). Engine clean (G7=0pp, Σw≡1.0, 13/13 TDD). Sharpe Δ064 −0.04 to −0.05 (KILL A misses by margin), DSR p 0.059 fails. **Conditional Sharpe: QQQ_TREND stress 0.95-1.20 > calm 0.71-0.76 on 3/3; r_046 stress 1.43-1.93 > calm 1.05-1.09 on 3/3** — both 064 sub-streams STRUCTURALLY DEFENSIVE in stress. Closes calm-trend/stress-defensive direction at 79; **reverse swap (calm 0.05 / stress 0.20) is iter 069 #1**.

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
