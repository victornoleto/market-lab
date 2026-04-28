---
mission: "beat avg(SPY 1× b&h, VT 1× b&h) gross-of-tax Sharpe by ≥0.10 on ≥2 of 3 datasets"
total_iterations: 13
winners_found: 1
status: hunting
latest_iteration: "013-2026-04-28-1814-factor-tilt-on-iter011"
latest_score: 91
beats_incumbent: false
cumulative_n_trials: 48
incumbent_winner_iter: "011-2026-04-28-1537-ntsx-gde-kmlm-static"
incumbent_winner_score: 91
note: "Renamed from bestfolio_hunt_loop on 2026-04-28. Mission redefined to 'beat avg(SPY,VT)' (gross-of-tax), scoring.py reworked accordingly. WINNER 2026-04-28: iter 011 NTSX+GDE+KMLM 35/25/40 static — 91/100, 5/5 strict, 3/3 +0.10 Sharpe edge. POST-WINNER OVERHAUL 2026-04-28: dataset registry centralized (datasets.py), educational dataset renamed lh_56y with KMLMSIM splice via FF MoM proxy pre-1988 (overstates pre-88 KMLM ~3×), plot_helper.py rewritten. Hunt resumes; halt only when an iter sets beats_incumbent=true. ITER 012 (RSSB injection) STRONG 88/100 but loses vs iter 011 on all 3 datasets — DE-013 (Treasury overlap). ITER 013 (factor tilt VBRSIM 10% on iter 011) — tier WINNER 91/100 5/5 conditions vs avg(SPY,VT), but TIES iter 011 score (91=91, not >) and edges only +0.080 on lh_56y while LOSING on vt (−0.037) / ndx (−0.029) — beats_incumbent=false; DE-014 added. Cross-config monotonic finding: factor tilt helps lh_56y (+0.060→+0.085 over VBRSIM 10%→30%) but hurts vt/ndx (−0.04→−0.13)."
---

# Long-Term Portfolio Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

---

## Mission

Find ONE long-term portfolio strategy that **beats the average of
SPY 1× b&h and VT 1× b&h** (gross-of-tax) by **≥ 0.10 Sharpe on ≥ 2
of 3 datasets**, while passing the 7-gate battery and respecting CAGR
floor / MDD ceiling.

**Per-dataset benchmarks** (from `scoring.py` BENCHMARKS dict):

| dataset | benchmarks averaged | avg Sharpe | avg CAGR | max MDD (ceiling base) |
|---|---|---:|---:|---:|
| **lh_56y** (1970+) | VTSIM 56y + SPYSIM 40y | **0.671** | 10.73% | 58.35% |
| vt_real (17y) | VTSIM 17y + SPY 17y | **0.707** | 11.88% | 50.21% |
| ndx_real (16y) | QQQ 16y + SPY 16y | **0.924** | 16.98% | 35.12% |

**Winner threshold (Sharpe edge gate)**: candidate must reach Sharpe
≥ **0.77 / 0.81 / 1.02** on ≥ 2 of 3 datasets (avg + 0.10).

**Beat-incumbent threshold (additional gate after 2026-04-28)**: a NEW iter
becomes the incumbent winner only if `total_score > 91` (iter 011's score)
OR Sharpe edge ≥ +0.10 vs iter 011 on ≥ 2 of 3 datasets — i.e., lh_56y
≥ 1.121, vt_real ≥ 1.060, ndx_real ≥ 1.204.

**Context from related research (read alongside)**:
- `_archive/strategy_hunt_loop/FINAL_REPORT.md` — 78 iters, 1 strict
  winner (iter 079 multi-asset top-K momentum). The "DON'T retest"
  section consolidates 57 closed dead-end families.
- `_archive/strategy_hunt_loop/WINNER/iter_035-*` and `iter_079-*` —
  best long-window-validated strategies on 40y synth (iter 035 CAGR
  19.6%, iter 079 strict 5/5 winner). These ARE referenced when
  comparing Pareto frontier — but our mission is now SPY+VT, not iter 035.
- `global_factor_tilt_loop/iterations/009-*` — HAA+Gold reference,
  Sharpe frontier of the predecessor loop (gross 1.120 edu).

**Tax model**: gating uses gross-of-tax. Net-of-tax via
`studies/_shared/tax_engine.py` (`AnnualDarfEngine`, Lei 14.754/2023)
is computed and reported in `final_report.md` as deploy-readiness
diagnostic only — does NOT influence tier or winner status.

Winner criteria live in `WINNER_AND_RANKING.md`.
Dead-ends live in `DEAD_ENDS.md`.

**Hard context**: mandate §1 MAINTENANCE MODE (2026-04-23) applies to
short-hold strategies (Plano A/B/D dormant). The long-term portfolio
thesis is the LIVE workstream — any winner here is a candidate
requiring mandate §7 override before deployment.

---

## Incumbent winner (the bar to beat)

| iter | slug | score | edu/lh_56y S/CAGR/MDD | vt S/CAGR/MDD | ndx S/CAGR/MDD | note |
|---|---|---|---|---|---|---|
| **011** | ntsx-gde-kmlm-static | **91/100 🏆** | 1.021 / 11.58% / 26.04% (1995-2026 31y) | 0.960 / 10.95% / 21.22% | 1.104 / 11.64% / 14.12% | Static 35% NTSX + 25% GDE + 40% KMLM stack. All 5 strict conditions met. 3/3 datasets beat avg(SPY,VT) +0.10 Sharpe edge (edu +0.350, vt +0.253, ndx +0.180). Family-level robust (all 4 weight variants pass). Caveats: tested on legacy `educational` window (1995-2026, 31y) NOT lh_56y (1970-2026); G1 PBO fails on real-data slots (within-family weight noise); KMLMSIM synth pre-2020. **Pending retro re-backtest on lh_56y** (FF MoM proxy 1970-87, expected to overstate Sharpe slightly). |

---

## Top-K strategies ranked

Original score earned on legacy `educational` window (1995-2026, 31y). After
retro re-backtest 2026-04-28, every iter also has lh_56y numbers — note the
ranking shifts substantially under lh_56y (iters using KMLM benefit from the
FF-MoM splice 1986-1988, an academic equity-momentum proxy with Sharpe ~1.9
vs KMLM's long-run ~0.5; pre-1988 KMLM-heavy returns are ~3× overstated).

| rank | iter | slug | score | tier | legacy edu Sharpe | **lh_56y gross Sharpe** | lh_56y window |
|---|---|---|---|---|---|---|---|
| 1 | **011** | **ntsx-gde-kmlm-static** | **91 🏆** | **WINNER** | 1.021 (gross) | **1.046** | 1986-2026 (40y) |
| 2 | **013** | factor-tilt-on-iter011 | **91** | WINNER (tier) ⚠️ | n/a | **1.126** ⭐ | 1986-2026 (40y eff) |
| 3 | **012** | ntsx-gde-rssb-kmlm-global-stack | **88** | STRONG | 1.011 (gross) | 1.011 | 1986-2026 (40y eff) |
| — | 007 | haa-defensive-kmlm-cash | 75 | STRONG | 0.983 (net) | **1.150** ⭐ | 1994-2026 (32y) |
| — | 008 | haa-dual-canary | 73 | PROMISING | 0.983 (net) | 1.120 | 1994-2026 (32y) |
| — | 009 | haa-gayed-trend-canary | 73 | PROMISING | 0.983 (net) | 1.120 | 1994-2026 (32y) |
| — | 006 | haa-rsit-synth | 71 | PROMISING | 0.869 (net) | **1.154** ⭐ | 1994-2026 (32y) |
| — | 005 | haa-rsst-rssb-cta | 70 | PROMISING | 0.953 (net) | **1.253** ⭐ | 1994-2026 (32y) |
| — | 004 | haa-global-factor-tilt | 69 | PROMISING | 0.990 (net) | **1.117** ⭐ | 1994-2026 (32y) |
| — | 010 | haa-vol-throttle | 60 | PROMISING | 1.020 (net) | **1.179** ⭐ | 1994-2026 (32y) |
| — | 001 | baa-g12-balanced | 58 | MARGINAL | 0.975 (net) | 1.094 | 1995-2026 (31y) |
| — | 002 | composite-momentum-standard | 55 | MARGINAL | 0.940 (net) | 1.024 | 1994-2026 (32y) |
| — | 003 | global-factor-cta-stack | 54 | MARGINAL | 0.823 (net) | 0.839 | 1994-2026 (32y) |

⭐ = retro lh_56y gross Sharpe ABOVE iter 011 (1.046). Caveat: iter 011 has
40y window (8y more than HAA-style iters bottlenecked by VWOSIM 1994). The
1986-1994 KMLM portion uses FF MoM proxy → expected to slightly overstate
iter 011's lh_56y Sharpe; iter 011 is still likely competitive but not
dominant on lh_56y. Apples-to-apples comparison requires same-window cropping
(future work: align all to 1994-2026 or use a non-KMLM-dependent benchmark).

⚠️ = tier WINNER per scoring rubric (≥90 + winner_conds_met=true vs avg(SPY,VT))
but does NOT advance the iter 011 incumbent (ties on score 91=91, fails the
+0.10 Sharpe edge gate on all 3 datasets). Listed alongside iter 011 in top-K
because rubric says WINNER, but BASE_MEMORY's `incumbent_winner_iter` stays 011.

---

## Iteration log (newest first)

### 013 — 2026-04-28 — factor-tilt-on-iter011 (WINNER tier, 91/100, beats_incumbent=false)

- Hypothesis: Inject US small-cap value factor (`VBRSIM` = AVUV synth proxy) into iter 011's NTSX+GDE+KMLM stack at 4 intensity levels (10/20/25/30%). Tests Direction B from BASE_MEMORY (factor tilts on iter 011 base) — iter 011 has zero factor exposure, and the user's literature thesis explicitly includes AVUV/AVDE/SPMO factor ETFs. VBRSIM is 1× notional and zero Treasury → qualitatively different mechanism from the iter 012 RSSB failure mode.
- Citations: `[risk_parity, ch.5, p.10]` (cap-efficient core); `[risk_parity, ch.2, p.37-41]` (factor premium framework); `[stocks_on_the_move, ch.6, p.21-30]` (cross-sectional ranking edges); gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs (`factor_lite_30253510`, `factor_moderate_25253020`, `factor_balanced_25202530`, `factor_heavy_20203030`); selected `factor_lite_30253510` (10% VBRSIM) by max mean(gross_Sharpe / avg(SPY,VT)_Sharpe). Datasets: lh_56y / vt_real / ndx_real (1986-2026 / 17y / 16y eff windows).
- Result: gross Sharpe **1.126 / 0.923 / 1.075** (edges vs avg(SPY,VT) **+0.454 / +0.216 / +0.152** — 3/3 datasets clear +0.10); gates **5/7 / 7/7 / 7/7**; DSR p **2.86e-13 / 2.29e-3 / 6.24e-4**. **All 5 strict winner conditions met vs avg(SPY,VT) → tier WINNER.** But Sharpe vs **iter 011 incumbent**: **+0.080 / −0.037 / −0.029** (BEATS only on lh_56y, LOSES on both live windows). Score 91 = score 91 of iter 011 (NOT greater). 0/3 datasets clear +0.10 incumbent edge. **beats_incumbent=false.**
- Net (informational): Sharpe **1.126 / 0.923 / 1.075** ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral).
- Score breakdown: Sharpe edge 25/25 (3/3 +0.10 vs avg); gates 21/25 (lh_56y G3 WF fails — 1986-2026 long-history has more drawdown windows in GFC/2022); DSR 15/15; CAGR floor 10/15 (ndx_real 12.06% < 13.58% = 0.8 × bench); MDD ceiling 15/15; robustness 5/5 (52/52 rolling-5y Sharpe positive, min 0.43 max 2.13).
- Lesson: factor tilt monotonically helps lh_56y (+0.060→+0.085 across VBR 10%→30%) but monotonically hurts vt_real (−0.04→−0.14) and ndx_real (−0.03→−0.13). The size+value premium IS alive on long-history but post-2008 windows are in the well-documented "death of value" regime. **Constant-weight factor tilt is structurally subordinate to iter 011 on the deploy-relevant live windows.** Closing direction B (constant-weight factor) → DE-014. Future factor work needs a regime filter (factor momentum / value spread) — naive constant-weight VBRSIM is not the answer.

### 012 — 2026-04-28 — ntsx-gde-rssb-kmlm-global-stack (STRONG, 88/100, DE-013)

- 4 configs RSSB injection on iter 011 base; selected `rssb_moderate_25252525`. Gross S 1.011/0.851/1.021 — all 5 strict winner conds met vs avg(SPY,VT) but LOSES iter 011 on all 3 datasets (−0.035/−0.109/−0.083). `[risk_parity, ch.5, p.10]`
- Lesson: RSSB's Treasury overlay duplicates NTSX's IEF; intl-equity sleeve dragged in post-2010 regime.

### 011 — 2026-04-28 — ntsx-gde-kmlm-static (🏆 WINNER, 91/100)

- 4 configs static NTSX/GDE/KMLM stack; selected `mf_tilted_352540` (35/25/40). Gross S 1.021/0.960/1.104 — 3/3 datasets +0.10 edge vs avg(SPY,VT). `[risk_parity, ch.5, p.10]`
- Lesson: capital-efficient stack (NTSX+GDE) + KMLM crisis-alpha is the only winner architecture across this loop and predecessor.

### 010 — 2026-04-28 — haa-vol-throttle (PROMISING, 60/100, DE-012)

- HAA+Gold with 63d vol throttle on 85% dyn sleeve. Sharpe 1.020/0.955/0.881; 7/7 × 3 but 0 datasets +0.10 vs iter009. `[systematic_trading, p.137-148]`
- Lesson: vol throttle reduces MDD but converts HAA into low-CAGR defensive.

### 009 — 2026-04-28 — haa-gayed-trend-canary (PROMISING, 73/100, DE-011)

- HAA+Gold with SPYSIM/VTSIM 10-mo trend canary modes; original VWOSIM re-selected. S 0.983/0.954/0.860. `[leverage_for_the_long_run, p.40-60]`
- Lesson: simple broad-equity trend not a better state classifier than VWO momentum.

### 008 — 2026-04-28 — haa-dual-canary (PROMISING, 73/100, DE-010)

- VWOSIM/VTISIM dual canary; vwo_only selected. S 0.983/0.954/0.860; ndx PBO 0.552 fails. `[stocks_on_the_move, p.63-65]`
- Lesson: second broad-equity canary did not improve state classification.

### 007 — 2026-04-28 — haa-defensive-kmlm-cash (STRONG, 75/100, DE-009)

- Swap HAA defensive variants; original IEF/BND/CASH re-selected. S 0.983/0.954/0.860; 7/7 × 3. `[stocks_on_the_move, ch.6]`
- Lesson: missing edge is canary timing, not defensive assets.

### 006 — 2026-04-28 — haa-rsit-synth (PROMISING, 71/100, DE-008)

- Synthetic RSIT_PROXY=VEASIM+KMLMSIM−50bps inside HAA. S 0.869/0.897/0.837; PBO 0.714/0.845 fails. `[risk_parity, ch.5]`
- Lesson: more embedded MF on intl-equity worsened Sharpe/PBO; defer until live RSIT.

### 005 — 2026-04-28 — haa-rsst-rssb-cta (PROMISING, 70/100, DE-007)

- RSST/RSSB/CTA offensive substitution in HAA. S 0.953/1.028/0.946; 7/7 × 3 but no +0.10 edge. `[risk_parity, ch.5]`
- Lesson: extra stacked diversifiers traded CAGR for MDD.

### 004 — 2026-04-28 — haa-global-factor-tilt (PROMISING, 69/100, DE-006)

- Intl small/value tilt inside HAA offensive. S 0.990/0.955/0.861; PBO 0.885/0.869/0.694 fails. `[stocks_on_the_move, ch.6]`
- Lesson: reshuffled risk-on equity exposure; unstable tilt selection.

### 003 — 2026-04-28 — global-factor-cta-stack (MARGINAL, 54/100, DE-005)

- Static global/factor/CTA stack; stack_gde_heavy selected. S 0.823/0.742/0.910; MDD 27-42%. `[risk_parity, p.1-2]`
- Lesson: low turnover preserved CAGR but lost HAA drawdown control.

### 002 — 2026-04-28 — composite-momentum-standard (MARGINAL, 55/100, DE-004)

- SPY200 top-4 inverse-vol composite momentum. S 0.940/0.958/0.957; 7/7 × 3 but return-capped. `[stocks_on_the_move, p.21-30]`
- Lesson: defensive 60/40 IEF/gold sleeve too low-return; annual DARF drag.

### 001 — 2026-04-28 — baa-g12-balanced (MARGINAL, 58/100, DE-003)

- BAA-G12 Balanced. S 0.975/0.792/0.782; 7/7, 7/7, 6/7. `[stocks_on_the_move, ch.6]`
- Lesson: too defensive/tax-dragged; never beats HAA+Gold.

---

## Promising unexplored directions (prioritized)

**Loop status: HUNTING past incumbent iter 011.** The user's explicit thesis
is "exposição global + fatores" — iter 011 has zero international equity and
zero factor tilt. Next iters should attack that gap.

### A. Global capital-efficient stack (iter 011 architecture, internationalized)

Replace pure-US NTSX with intl variants. Candidate:

1. **NTSX + NTSI + NTSE + GDE + KMLM** (5-asset capital-efficient global stack)
   — NTSI is intl-developed 1.5× stacked, NTSE is EM 1.5× stacked. This is
   the literal "global+factor" thesis. Citation: `[risk_parity, ch.5]` + WisdomTree
   prospectus 2024. Test 35/15/10/20/20 starting weight + 4 sensitivity variants.
   **Status: INFEASIBLE without NTSI/NTSE proxy synthesis** (not in testfolio cache).
2. ~~**NTSX + GDE + RSSB + KMLM**~~ — **CLOSED iter 012 (DE-013)**: RSSB sleeve
   regresses Sharpe vs iter 011 across all 3 datasets (−0.030 / −0.109 / −0.083).
   RSSB's Treasury overlay overlaps NTSX's IEF exposure; intl-equity sleeve dragged
   in 2010-2026 regime. STRONG vs avg(SPY,VT) but does not advance incumbent.
3. **NTSX + VXUS overlay + GDE + KMLM** — simpler: keep NTSX core, add ~25%
   VXUS for explicit intl, drop GDE weight. Tests pure intl tilt without
   adding extra leverage. **Now higher priority** after iter 012 DE-013 — VXUS
   is 1× notional (no Treasury duplication issue) and isolates the intl-equity
   tilt from RSSB's Treasury overlap.

### B. Factor tilts on the iter 011 base — partially CLOSED

iter 011 has zero factor tilt. Constant-weight US factor tilt CLOSED iter 013
(DE-014). Remaining sub-axes:

4. ~~**Iter 011 + AVUV/AVDV core (constant weight)**~~ — **CLOSED iter 013
   (DE-014)**: VBRSIM 10/20/25/30% sweep on iter 011 base improves lh_56y
   monotonically (+0.060 → +0.085) but degrades vt_real / ndx_real
   monotonically (−0.04 → −0.14, −0.03 → −0.13). Selected lightest config
   (10%) is tier WINNER vs avg(SPY,VT) but does not advance iter 011
   incumbent. Constant-weight factor tilt is structurally subordinate
   on post-2008 windows (well-documented "death of value" regime).
5. **Iter 011 + UMD (Fama-French momentum) overlay** (now higher priority
   after iter 013) — 20% direct UMD factor exposure as Sharpe enhancer.
   UMD daily 1926+ on disk now. Different factor (momentum vs size+value),
   different post-2008 behavior (momentum had multiple positive years
   2017-2024 while value lagged). `[stocks_on_the_move, ch.6]` +
   Fama-French (1993).
6. **Iter 011 + factor with regime filter** (NEW direction emerging from
   iter 013's structural finding) — factor weight conditional on a
   value-spread (CAPE differential) or factor-momentum signal (12-1
   factor return). VBRSIM only when premium is "live"; KMLM/GDE
   otherwise. Pre-commit ≤ 3 configs to avoid the prior loop's
   "regime gate on existing winner" DSR-regression trap
   (`_archive` strategy_hunt_loop dead-ends 3-4).
7. ~~**NTSX + GDE + KMLM + AVUV + AVDV**~~ — would be a superset of iter
   013's grid; expected to fail by the same regime-mismatch logic.
   Defer until either #5 (UMD) or #6 (regime-filtered factor) shows
   positive signal.

### C. Live-data validation (deferred until A or B winner)

Run only if a candidate from A/B beats iter 011 — then validate on
post-2020 live KMLM, post-2018 live NTSX, post-live VT (when pulled).
This is the deploy-readiness gate, not a hunt direction.

### Closed by iter 011

- ~~NTSX + GDE + RSST static~~ — superseded by iter 011; sensitivity question.
- ~~NTSX + GDE + KMLM 40/30/30 (user primary)~~ — same family as iter 011's
  35/25/40 winner (passes too); not a fresh direction.

---

## Structural dead-ends (carry-over from global_factor_tilt_loop)

These were proven dead-ends in the predecessor loop. Same universe:
full text in `DEAD_ENDS.md`.

1. **2× single-asset global-equity LETF + binary SMA**: VTSIM base Sharpe
   (0.61) already matches Gayed LRS target → zero improvement. `[leverage_for_the_long_run, p.17]`
2. **VAA breadth with higher-notional equity (for Sharpe-max)**: GDESIM
   in offensive adds variance faster than returns; HAA canary dominates
   VAA breadth on Sharpe.
3. **Plain BAA-G12 Balanced in current universe**: robust drawdown reducer
   but too defensive/tax-dragged; net Sharpe 0.975/0.792/0.782 and CAGR
   below 0.8× iter009 on all datasets. `[stocks_on_the_move, ch.6]`
4. **Composite Momentum Standard with SPY200 top-4 inverse-vol**: robust
   7/7 gates × 3 but return-capped; net Sharpe 0.940/0.958/0.957, CAGR
   below HAA+Gold on all datasets, MDD too high on vt/ndx.
5. **Plain static global/factor/CTA stack**: low turnover restores CAGR
   floors but gives up HAA canary drawdown control; net Sharpe
   0.823/0.742/0.910 and MDD 27-42% fail the Sharpe/MDD frontier.
6. **Simple HAA international small/value tilt**: preserves HAA MDD but
   sacrifices Sharpe/CAGR; net Sharpe 0.990/0.955/0.861 and PBO
   0.885/0.869/0.694 show unstable tilt selection. `[stocks_on_the_move, ch.6]`
7. **Simple HAA RSST/RSSB/CTA offensive substitution**: robust 7/7 gates but
   lower-return; net Sharpe 0.953/1.028/0.946 and zero +0.10 Sharpe edges.
   Extra stacked diversifiers trade CAGR for MDD after iter009. `[risk_parity, ch.5]`
8. **Synthetic HAA RSIT offensive sleeve**: clears CAGR/MDD and DSR but loses
   Sharpe badly; net Sharpe 0.869/0.897/0.837 and PBO 0.714/0.845 on global
   windows. More embedded MF on international equity is not the missing edge.
   `[risk_parity, ch.5]`
9. **Simple HAA KMLM/CASH defensive swaps**: statistically robust but no
   improvement; original `IEFSIM/BNDSIM/CASHX` defense was selected with net
   Sharpe 0.983/0.954/0.860, while KMLM-heavy defense raised MDD to 27.49%.
   The next edge must change canary timing, not defensive assets.
   `[stocks_on_the_move, ch.6]`
10. **Simple HAA dual broad-equity canary (`VWOSIM` + `VTISIM`)**: original
   `VWOSIM` canary was selected again; `VTISIM` variants lowered Sharpe and
   the ndx_real PBO failed at 0.552. The next timing edge must use a
   qualitatively different trend/regime input. `[stocks_on_the_move, p.63-65]`
11. **Simple Gayed SPY/VT trend input as HAA canary**: original `VWOSIM`
    selected again; SPY/VT trend filters either cut CAGR or raised real-window
    MDD, with net Sharpe 0.983/0.954/0.860 and no +0.10 Sharpe edge.
    `[leverage_for_the_long_run, p.40-60]`
12. **Simple HAA dynamic-sleeve volatility throttle**: `vol12` passed 7/7
    gates across all datasets and reduced MDD, but failed every CAGR floor
    and produced net Sharpe 1.020/0.955/0.881 with zero +0.10 Sharpe edges.
    Drawdown throttling is not the missing return source. `[systematic_trading, p.137-148]`
13. **NTSX+GDE+RSSB+KMLM 4-asset global stack (iter 011 internationalized)**:
    selected `rssb_moderate_25252525` produced gross Sharpe 1.011/0.851/1.021
    — STRONG 88/100 vs avg(SPY,VT) (5/5 strict conditions met) but LOSES vs
    iter 011 incumbent on Sharpe across all 3 datasets (−0.030 / −0.109 / −0.083).
    Pre-committed kill #1 fired. RSSB's Treasury overlay overlaps NTSX's IEF;
    intl-equity sleeve dragged in 2010-2026 regime. `[risk_parity, ch.5, p.10]`
14. **Constant-weight US factor tilt on iter 011 base (NTSX + GDE + KMLM +
    VBRSIM 10/20/25/30%)**: selected `factor_lite_30253510` (10% VBRSIM)
    hit tier WINNER 91/100 vs avg(SPY,VT) — all 5 strict conditions met,
    3/3 +0.10 edge vs passive baseline. But ties iter 011's score (91=91,
    not >) and only +0.080 on lh_56y while LOSING on vt_real (−0.037)
    and ndx_real (−0.029). Cross-config monotonic finding: factor tilt
    helps lh_56y (+0.060→+0.085 over 10%→30%) but hurts both live
    windows (−0.04→−0.14, −0.03→−0.13). Post-2008 "death of value"
    regime makes constant-weight factor tilt structurally subordinate
    to iter 011 on deploy-relevant windows. `[risk_parity, ch.2, p.37-41]`,
    `[stocks_on_the_move, ch.6, p.21-30]`

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify `docs/investment-mandate.md`** — even a winner is a
  candidate, not auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2): every decision cites
  `[book.slug, p.X]`.
- **7-gate battery** mandatory per `WINNER_AND_RANKING.md`
- **AnnualDarfEngine only** for net-of-tax: `tax_engine_v2.py`
  (`studies/global_factor_tilt_loop/`). NEVER use `DarfCostBasisEngine`.
- **Pytest baseline (461) stays green** — never reduce passing count
- **Max 2h wall-time** per iteration
- **NEVER `git commit`** — `run_loop.sh` handles commits
- **DO NOT touch** `studies/strategy_hunt_loop/`, `studies/gold_swing_loop/`,
  `studies/global_factor_tilt_loop/` — parallel sessions / frozen loop
