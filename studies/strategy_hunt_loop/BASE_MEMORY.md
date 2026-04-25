---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 55
winners_found: 0
status: iterating
latest_iteration: "055-2026-04-25-0938"
cumulative_n_trials: 4325
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
| **2** | **053** | 🥇 STRONG | **84** | `iter037_plus_iter046_w070` | `[risk_parity, ch.5]` + Sinclair + Markowitz | 3-way tie #2; 3/3 CAGR (ndx +0.04pp); corr 0.95 Kill F PRE-FIRED; iter 037 anchor exhausted |
| **2** | **051** | 🥇 STRONG | **84** | `iter037_plus_iter026_w080` | `[risk_parity, ch.5]` + Sinclair + Markowitz | **1st EVER 4/5 winner conds + 3/3 CAGR floor**; 25/19/5/15/15/5; DSR p=0.175 sole gap to 90 |
| **2** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley | 1st 84; DSR 0.222→0.168 escape; gate-mod axis closed (042/043/044); used in iter 046 |
| **5** | **045** | 🥇 STRONG | **81** | `iter039_on_iter037_50_50` | `[risk_parity, ch.5]` + Sinclair | out-of-family 50/50 037+039; ρ=0.58; DSR 0.222→0.096; ndx 7/7; 0/6 kills; superseded by 046 |
| **5** | **038** | 🥇 STRONG | **79** | `regime_lev_vix_lt20_lo10_hi17` | `[advances_fin_ml, ch.17-18]` + MM 2017 | VIX-gated 1.7/1.0× on 037; MDD −4/−8pp; DSR 0.204 |
| **5** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` | `[risk_parity, ch.5]` + AMP 2013 | 1st static-stack 79; base for iter 051 |
| **5** | **016/018/021/043/052** | 🥇 STRONG | **79** | various | various | 60:40×MM (016), funded (018), put-cs (021), hysteretic VIX (043), 041+026 w=0.82 (052) |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### Iters 015-055 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **055** (🥈 73 PROMISING, 0/6 KILLS, vrp-basket-5etf-cross-region) S 1.07/1.40/1.60 (Δ frozen +0.39/+0.50/+0.64; Δ iter039 −0.07/+0.12/+0.04), CAGR 4.74/5.38/6.20% (0/3 floor; T-bill cap unchanged), MDD 16.18/5.99/4.70% (3/3 ceiling), gates 6/7/7, DSR worst-p edu 0.130 (10→5pts vs 039), G7 0.0000pp, winner 0/5; score 25+23+5+0+15+5=73. **Cross-region VRP basket NET NEGATIVE: EFA/EEM legs help post-GFC (Sharpe +0.04 to +0.12) but hurt 2006-2010 edu (−0.07) due to EM tail asymmetry not captured by static VXEEM/VIX=1.30 proxy. iter 039 confirmed Pareto-opt within VRP family at 76 STRONG; broader-region extension axis closed.**
- **054** (🥉 47 MARGINAL, 2/3 KILLS, tiingo-cross-sectional-12-1) S 0.655 single-univ (Δ window-matched SPY/QQQ −0.025/−0.098; Δ fixed bench −0.025/−0.245/−0.300), CAGR 16.60% (3/3 floor PASS) > SPY 13.46% same-window but worse Sharpe, MDD 28.25% (3/3 ceiling), DSR p=0.811 (n=4324), PBO=1.000 (grid noise), G7 0.0000pp, winner 0/5; score 0+17+0+15+15+0=47. **DATA-LAYER closure: survivorship-biased Tiingo cache (422 names ≥2014) correlates with cap-weighted index — closes ALL cross-sectional ranking (12-1/6-1/adj-slope/low-vol/value/quality) until CRSP/Norgate point-in-time delisted coverage exists.**
- **053** (🥇 84, 2/6 KILLS, iter037+iter046 w_037=0.70) S 1.029/1.193/1.220 (Δ +0.35/+0.29/+0.27), gates 6/6/6, DSR 0.165/0.112/0.108, CAGR 12.71/13.73/15.39 (3/3 floor PASS, ndx 0.04pp margin), MDD 29/22/27, corr 0.93-0.96 (Kill F pre-fired), Markowitz 0.0000 (5th consec, 15/15 ds), G7 0.0000pp, robust 9/9, winner 4/5; score 25+19+5+15+15+5=84. **Saved-stream-pair-on-iter-037-anchor EXHAUSTED at Pareto 84 (3 tested: 037+026→84, 037+039→81, 037+046→84). Path to 90+ requires NEW base edu Sharpe ≥ 1.20.**
- **052** (🥇 79, iter041+026 w=0.82) S 1.08/1.19/1.22, DSR 0.118/0.116/0.109 (same bucket as 051), CAGR 11.6/12.0/14.0 (2/3, ndx FAIL 1.34pp), corr 0.37-0.45, Markowitz 0.0000 (4th), score 79. **iter 037 dominates iter 041 anchor.**
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

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**055**. iter 044/047-050 close 5 iter-046 axes; iter 051/053 close 037+026/046 families at Pareto 84; iter 052 closes 041+026 at Pareto 79 (037 dominates 041 as anchor); iter 055 closes broader-region VRP at 73 (iter 039 Pareto-opt at 76). Saved-stream-pair Pareto exhausted: ceiling = 85 (iter 046). DSR binding at n_trials > 4300: edu Sharpe ≥ 1.10 to cross 0.10 bucket, ≥ 1.18 for strict-winner. iter 054 closes single-stock cross-sectional at DATA LAYER (survivorship-biased Tiingo cache).

### Iter 056 candidates (iter 055 closed broader-region VRP at 73 PROMISING)

- **#1 Levered iter 046 1.2-1.3× notional (RECOMMENDED)** — sole untested axis (closed: 044/047/048/049/050). At 1.3× CAGR 9.16/9.45/9.76 → ~11.6/12.0/12.3 (edu vs floor 9.18 marginal PASS, spy ≈ 11.98 marginal, ndx 15.35 MISS); MDD 18/15/15 → 23/20/20 (under ceilings). Distinct from iter 027 (closed harvest_notional > 1 on T-bill VRP). Predicted 85-92 (potential WINNER if 2/3 CAGR PASS). `[advances_fin_ml, p.31-34]` + `[risk_parity, ch.5]`. ~30-45 min.
- **#2 AMP 2013 global value-momentum overlay** — long-only top-K composite 8-10 macro ETFs (equity/bond/commodity), CAPE-style value + 12-1 mom. Distinct from iter 023 (HOP needs 67 markets) + iter 054 (data-layer closure). ~90 min, predicted 70-80.
- **#3 Plano C sleeve eval (mandate-aligned)** — GDE/AVUV/AVDE/AVEM/BTGD passive factor-tilted; ETFs young (2018-2024), need FF93 proxies for edu. Documents maintenance baseline. ~60-90 min, predicted ≤ 70.
- **#4 Bring in delisted-aware data source** — long-term unblock of cross-sectional family (CRSP/Norgate/Quotemedia). Not feasible without budget.

DEAD-LETTER: iter 037+026/041+026/037+046/041+039 at any weight (Pareto 79-85 exhausted); iter 046-family enhancements (044/047/048/049/050); HYG-041; HMM-2; FX carry; MTUM/QUAL/USMV (not in cache); **all saved-stream-pair compositions on iter 037 anchor (closed by iter 045/051/053; ceiling 84)**; **iter 041 substitution for iter 037 (closed by 052)**; **single-stock cross-sectional 12-1 momentum (any K, any lookback) on Tiingo cache (closed by iter 054 at data layer)**; **broader-region VRP basket 5-leg US+EAFE+EM equal-weight (closed by iter 055 at score 73 < iter 039's 76)**.

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
- **iter 054 closure (DATA LAYER)**: 12-1 cross-sectional on 422-name Tiingo — Sharpe 0.655 < SPY 0.680, DSR 0.811, PBO=1.0; score 47. Survivorship-biased cache correlates with cap-weighted bench → no dispersion at any K. Closes ALL cross-sectional ranking on `data/tiingo/` until CRSP/Norgate delisted coverage.
- **iter 055 closure (broader-region VRP)**: 5-leg SPY+QQQ+IWM+EFA+EEM equal-weight; Δ039 Sharpe −0.07/+0.12/+0.04, CAGR floor 0/3 (T-bill cap unchanged), edu DSR 0.130 (vs 039's 0.075); score 73. Cross-region diversification asymmetric: helps post-GFC, hurts pre-GFC edu (EM tail not captured by VXEEM/VIX=1.30 proxy). iter 039 Pareto-opt at 76 STRONG; broader-VRP axis closed.

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
