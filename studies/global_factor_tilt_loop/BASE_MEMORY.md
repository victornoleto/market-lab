---
mission: "find one global strategy beating VT 1x b&h + Plano C V3_1 v3.5 + V_HYBRID+MF on real data"
total_iterations: 6
winners_found: 3
status: iterating
latest_iteration: "006-2026-04-27-0838-vaa-smartstack"
cumulative_n_trials: 23
note: "3 winners (iter 002, 004, 005). iter 005 HAA SmartStack = Pareto frontier (S 1.112/C 14.14%/MDD 20.91%). iter 006 VAA-G4 SmartStack = STRONG 85 (S 1.052/C 8.26%/MDD 14.24% edu) — subordinate to HAA on Sharpe+CAGR, superior on MDD margin. Queue remaining: iter 007 (user portfolio+G3'), iter 008 (WLDU+Gayed)."
---

# Global Factor-Tilt Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

---

## Mission

Find ONE globally-diversified strategy that **beats ALL THREE** of:

1. **VT 1x buy-and-hold** — passive global cap-weighted baseline
   (Sharpe ≈ 0.51 on vt_real 17y, 0.66 on educational 56y)
2. **Plano C V3_1 v3.5** — current factor + global Plano C
   (Sharpe 0.671, CAGR 10.94%, MDD 52.43% on 32y)
3. **V_HYBRID + 10% MF** — deploy_studies portfolio_variants WINNER
   (Sharpe 0.743, CAGR 10.91%, MDD 44.71% on 32y;
   `P(rolling 10y CAGR < 5%) = 0.6%`)

The bar is **higher than VT-only** because deploy_studies already
identified strong factor + global + capital-efficiency combinations.
This loop must find something **structurally novel** vs those three.

Winner criteria live in `studies/global_factor_tilt_loop/WINNER_AND_RANKING.md`.
Dead-ends that must NOT be re-tried live in
`studies/global_factor_tilt_loop/DEAD_ENDS.md`.

**Hard context**: project is in mandate §1 **MAINTENANCE 100% Plano C**.
Even if this loop finds a winner, deployment requires a separate signed
override per mandate §7. Loop produces CANDIDATES, not live positions.

---

## Winners found

### Winner 001 — iter 002 — fixed-momentum-k2-lb6 (WINNER, 90/100) [superseded by iter 005]

edu S=0.991/C=12.0%/MDD=23.4% 7/7; vt S=0.838/C=11.0%/MDD=17.3% 7/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7.
Details: `iterations/002-*/`. `[stocks_on_the_move, p.21-30]` + `[ilmanen_expected_returns, ch.12]`

### Winner 003 — iter 005 — haa-smartstack (WINNER, 90/100) ← NEW PARETO FRONTIER

**Strategy**: HAA (Hybrid Asset Allocation — dual momentum + single canary VWOSIM).
Offensive: stacked universe (NTSXSIM, NTSI-synth, NTSE-synth, GDESIM). Defensive:
IEFSIM/BNDSIM/CASHX. Fixed 10% KMLMSIM sleeve. Monthly rebalance, single
pre-committed config.

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (31y, VWOSIM-binding) | 1.112 | 14.14% | 20.91% | 7/7 |
| vt_real (~17y) | 1.049 | 12.99% | 15.05% | 7/7 |
| ndx_real (16y) | 0.942 | 10.63% | 15.05% | 7/7 |

**31y comparison (vs benchmarks)**:
- vs VT b&h (S=0.55, C=8.64%, M=58.35%): +0.566 S / +5.5pp C / −37.4pp MDD → dominates
- vs Plano C V3_1 (S=0.671, C=10.94%, M=52.43%): +0.441 S / +3.2pp C / −31.5pp MDD → dominates
- vs V_HYBRID+MF (S=0.743, C=10.91%, M=44.71%): +0.369 S / +3.23pp C / −23.8pp MDD → dominates
- vs iter 002 WINNER (S=1.001): +0.111 Sharpe, better CAGR+MDD → supersedes

**Rolling robustness**: 26/26 rolling-5y windows positive (100%). Min 5y Sharpe: 0.654.

**Gap to bestfolio**: −0.07 Sharpe (1.112 vs 1.18 reference). Likely closes with gold sleeve variant.

**Citations**: `[stocks_on_the_move, ch.6]` + `[ilmanen_expected_returns, ch.19]`
+ `[leverage_for_the_long_run, p.40-60]`

**Caveat**: Mandate §1 MAINTENANCE still in effect. §7 override required for deployment.

### Winner 002 — iter 004 — momentum-mf-sleeve (WINNER, 90/100) [superseded by iter 005]

edu S=0.885/C=9.51%/MDD=20.77% 7/7; vt S=0.842/C=10.14%/MDD=16.06% 7/7; ndx S=0.943/C=10.72%/MDD=16.06% 7/7.
Details: `iterations/004-*/`. `[ilmanen_expected_returns, ch.19]` + `[stocks_on_the_move, p.21-30]`

---

## Top-K ranked (best across all iters, by score)

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | 005 | haa-smartstack | **90** | **WINNER** | 1.112 / 1.049 / 0.942 | 14.14% | 20.91% |
| 1= | 002 | fixed-momentum-k2-lb6 | **90** | **WINNER** | 0.991 / 0.838 / 0.929 | 12.0% | 23.4% |
| 1= | 004 | momentum-mf-sleeve | **90** | **WINNER** | 0.885 / 0.842 / 0.943 | 9.51% | 20.77% |
| 4 | 006 | vaa-smartstack | 85 | STRONG | 1.052 / 0.850 / 0.733 | 8.26% | 14.24% |
| 5 | 003 | capital-efficient-static | 84 | STRONG | 0.773 / 0.656 / 0.826 | 11.65% | 44.54% |

---

## Iteration log (newest first)

### 006 — 2026-04-27 — vaa-smartstack (STRONG, 85/100)

- **Hypothesis:** VAA-G4 (Keller & Keuning 2017, SSRN 3002624) breadth momentum on stacked
  offensive universe (NTSXSIM, NTSI, NTSE, BNDSIM) + 15% fixed sleeve (KMLMSIM 10% + GLDSIM 5%).
  B = count(offensive assets with 13612W > 0) drives offensive/defensive split. Single pre-committed config.
  `[stocks_on_the_move, ch.6]` + `[leverage_for_the_long_run, p.40-60]`
- **Citations:** `[stocks_on_the_move, ch.6]`, `[ilmanen_expected_returns, ch.19]`,
  `[leverage_for_the_long_run, p.40-60]`, `[advances_fin_ml, p.208-211/222-223/196-202/31-34]`,
  VAA SSRN 3002624 (primary)
- **Scope:** 1 config, pre-committed; 3 datasets; cumulative n_trials=23
- **Result:** edu S=1.052/C=8.26%/MDD=14.24% 7/7; vt_real S=0.850/C=6.53%/MDD=14.24% 7/7;
  ndx_real S=0.733/C=5.23%/MDD=14.24% 7/7. DSR worst p=2.44e-3. Rolling 5y: 26/26 (100%).
  Kill 1 triggered: edu Sharpe 1.052 ≤ HAA 1.112 → subordinate to HAA. Winner condition 4
  (CAGR floor) fails: vt_real 6.53% < 7.04% floor; ndx_real 5.23% << 15.19%.
- **Score breakdown:** Sharpe 20/25, Gates 25/25, DSR 15/15, CAGR 5/15, MDD 15/15, Robustness 5/5
- **Lesson:** VAA breadth + BNDSIM as 4th offensive = chronic partial-defensive allocation
  when equities and bonds diverge. B=3 (bonds negative) routes 25% to defensive even in bull
  runs → CAGR sacrifice vs HAA. VAA's MDD advantage (14.24% vs HAA 20.91%) is the only edge.
  HAA canary architecture remains superior. Next: iter 007 user portfolio + G3'.

### 005 — 2026-04-27 — haa-smartstack (WINNER, 90/100) ← PARETO FRONTIER
- **Result:** edu S=1.112/C=14.14%/MDD=20.91% 7/7; vt S=1.049/C=12.99%/MDD=15.05% 7/7; ndx S=0.942/C=10.63%/MDD=15.05% 7/7. 26/26 rolling. Score 20+25+15+10+15+5=90.
- **Lesson:** HAA canary (VWOSIM) + stacked offensive (NTSXSIM/NTSI/NTSE/GDESIM) + 10% KMLMSIM = dominant architecture. Canary eliminates 2008/2020/2022 spikes. Details: `iterations/005-*/`.

### 004 — 2026-04-27 — momentum-mf-sleeve (WINNER, 90/100)
- **Result:** edu S=0.885/C=9.51%/MDD=20.77% 7/7; vt S=0.842/C=10.14%/MDD=16.06% 7/7; ndx S=0.943/C=10.72%/MDD=16.06% 7/7. 33/33 rolling. Score 90.
- **Lesson:** MF "free lunch" confirmed. 10% KMLMSIM improves Sharpe+MDD. Superseded by iter 005. Details: `iterations/004-*/`.

### 003 — 2026-04-26 — capital-efficient-static (STRONG, 84/100)
- **Result:** edu S=0.773/C=11.65%/MDD=44.54% 6/7; vt S=0.656/C=10.56%/MDD=43.13% 5/7; ndx S=0.826/C=12.10%/MDD=28.83% 6/7. Score 84.
- **Lesson:** Static stacking fails G3 nominal in crisis windows. G3' adapted gate invented here — used in all stacked iters thereafter. Details: `iterations/003-*/`.

### 002 — 2026-04-26 — fixed-momentum-k2-lb6 (WINNER, 90/100)
- **Result:** edu S=0.991/C=12.0%/MDD=23.4% 7/7; vt S=0.838/C=11.0%/MDD=17.3% 7/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7. Score 90.
- **Lesson:** Pre-commitment (single config) converts STRONG→WINNER. Superseded by iter 005. Details: `iterations/002-*/`.

### 001 — 2026-04-26 — global-momentum-topk (STRONG, 81/100)
- **Result:** edu S=1.040/C=12.0%/MDD=21.9% 6/7; vt S=0.883/C=11.9%/MDD=30.1% 6/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7. Score 81.
- **Lesson:** Grid-search PBO kills edu gate. Fix: pre-commit (iter 002). Details: `iterations/001-*/`.

---

## Promising unexplored directions (prioritized)

Seeded from `README.md` hypothesis menu (Tiers 1-4). Pick the
simplest version of one direction first; iterate to complexity only
if simple version scores ≥ PROMISING.

### Tier 0 — USER_DIRECTIVE 2026-04-27 — exhaustive testing queue

User authorized exhaustive testing (no rush, no token-budget cap). Iters
005-008 should consume these 4 hypotheses **in order**. All hypotheses
are **single config, n_trials=1, pre-committed** (DSR honest, PBO trivial).
All use **G3' adapted gate** for stacked portfolios — see "G3' rule"
in `## Binding constraints` below.

**Reference target**: VAA-G4 SmartStack on bestfolio.app (Sharpe 1.18 / 33.4y)
per `references/REFERENCE_PORTFOLIOS.md`. Iter winners must have Sharpe
≥ iter 002 (1.00, 32y) at minimum; aspire to ≥ 1.10 to be considered
"structurally novel" given the reference target.

#### ~~iter 005 — HAA SmartStack equivalent~~ [CONSUMED → WINNER 90/100]
HAA canary VWOSIM + stacked (NTSXSIM/NTSI/NTSE/GDESIM) + 10% KMLMSIM. Details: `iterations/005-*/`.

#### ~~iter 006 — VAA-G4 SmartStack equivalent~~ [CONSUMED → STRONG 85/100]
VAA-G4 breadth (NTSXSIM/NTSI/NTSE/BNDSIM offensive) + 15% KMLM+GLD sleeve. CAGR floor fails (bonds-as-4th drag). Details: `iterations/006-*/`.

#### iter 007 — User static portfolio + G3' adapted (reality check)

- **Hypothesis**: Same EXACT 9-sleeve portfolio as iter 003 (RSSB 25%, RSST 15%,
  AVUV 10%, AVDV 7%, AVEM 8%, SPMO 8%, IDMO 7%, GDE 12%, KMLM 8%). Only
  difference: use **G3' adapted gate (Opção C)** instead of G3 nominal.
- **Goal**: validate whether iter 003's STRONG 84 was actually a hidden WINNER
  blocked only by gate calibration. If iter 007 scores ≥ 90 with G3' → portfolio
  vindicated. If still < 90 → real performance issue, not gate.
- **Synth + citations**: identical to iter 003 (see CONSUMED entry above for
  full table). Notional ~1.45×.
- **Constraint**: Iter MUST test the EXACT weights as given. No grid, no
  optimization, no rebalance variations. The portfolio's exact spec is
  preserved in iter 003 — re-read it.
- **Kill criteria**: if MDD per WF window with G3' STILL > reference (`MAX(VT_MDD × 1.45, V_HYBRID+MF_MDD)`) → fail. Then portfolio is genuinely too leveraged.

#### iter 008 — WLDU + Gayed 200d SMA gate (LETF managed)

- **Mechanism**: 2× global equity LETF managed by 200d SMA trend filter (Gayed canonical)
- **Synth WLDU**: `VTSIM × 2` daily-resetting with 0.75%/y drag + financing cost
  (use IEFSIM 3m yield as proxy for SOFR). Document daily-rebalanced compounding.
- **Rule**:
  - Hold synth-WLDU when SPYSIM close > SMA(200d) of SPYSIM
  - Hold CASHX when SPYSIM close ≤ SMA(200d)
  - Monthly rebalance check (Gayed canonical is monthly; daily check possible variant)
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` PRIMARY, `[stocks_on_the_move, p.21-30]` (trend filter rationale)
- **Kill criteria**: 32y CAGR < 12% → fail (LETF must justify decay risk); max single-window MDD > 35% → fail; whipsaw cost > 1%/y → fail

---

### Tier 0 — [CONSUMED by iter 003]

**~~0. Capital-efficient 9-sleeve static portfolio~~** → STRONG 84/100.
G3 structural failure (1.45× stacking → crisis MDD > 25%). Details in `iterations/003-*/`.
Follow-ups (0b-1/0b-2/0b-3) deprioritized — HAA SmartStack (iter 005) supersedes.

### Tier 1 — established factor literature (start here)

**[CONSUMED iter 001]** ~~top-K grid~~ → STRONG 81. **[CONSUMED iter 002]** ~~fixed K=2/lb=6m~~ → WINNER 90. **[CONSUMED iter 004]** ~~+MF sleeve~~ → WINNER 90. All superseded by iter 005.

1. **Static return-stack: VTI + VBR + VEA + VWO + bonds + gold**.
   `[risk_parity, ch.5]` extended globally. Direct port of
   `strategy_hunt_loop` iter 035 to global universe. Long-window
   backtest on Vanguard synth (1970+); deploy as AVUS + AVUV + AVDE +
   AVEM + IEF/BND + GLD.

2. **Vol-managed VTSIM + bonds/gold mix**. Direct port of iter 016
   (vol-target overlay) to global universe. `[systematic_trading,
   ch.11]` + Moreira-Muir 2017.

3. **VTSIM vs (VTISIM + VXUSSIM 60/40) rotation**. When US
   outperforms by N pp on rolling 12m → tilt to VTISIM; when ex-US
   outperforms → tilt to VXUSSIM. Cross-region momentum.
   `[stocks_on_the_move, p.21-30]`.

### Tier 2 — regional + style rotation

5. **Top-K country rotation** (Faber 2007 style on country ETFs).
   Universe: SPY, EWJ, EWG, EZU, EWU, MCHI, EWZ, INDA. (No synth analogs
   — 17y window only.)

6. **Factor sleeve rotation**: rotate across US-large + US-SCV +
   intl-large + intl-SCV by relative momentum. Long-window via
   VTISIM/VBRSIM/VEASIM/VSSSIM.

### Tier 3 — explicit currency / hedge layer

7. **VT + currency hedge overlay**. Hedge USD/EUR/JPY exposure when
   carry signal flips. `[ilmanen_expected_returns, ch.fx-carry]`.

8. **VT + commodity exposure** (DBA, DBC, GLD). Adds inflation hedge
   orthogonal to equity beta.

### Tier 4 — multi-stacking (priority, deploy_studies follow-up)

9. **Global return-stacked all-weather**: e.g., 60% RSSB (global eq +
   Treasury via futures, 200% notional) + 30% GDE (S&P + gold) + 10%
   KMLM (managed futures). Total notional ~270% via futures stacking,
   zero margin loan. Tests: does this dominate V_HYBRID+MF in
   long-window Sharpe + MDD? Reference cell already in
   `long_window_validator.py` as `ref_global_returnstacked_allweather`.

10. **Synthetic NTSI/NTSE re-evaluation**: Plano C V3.5 rejected based
    on real 2021-2026 data only. Test with 32-56y synth. Hypothesis:
    NTSI/NTSE adds value in lost-decade scenarios but loses in
    rate-cycle shocks (2022). If true, **conditional** allocation
    (e.g., NTSI active only when bond term spread > X) may capture
    upside without 2022-style downside.

11. **Custom return-stacked synthesis**: leverage the testfolio-validated
    formula `eq_w × eq + bond_w × bond - cash_w × CASHX` to construct
    arbitrary stacks. E.g., "global 90/60 stack" = 0.90 VTSIM + 0.60
    IEFSIM - 0.50 CASHX (a synth NTSG that doesn't exist as real ETF).

12. **MF + global combination**: deploy_studies showed MF (KMLM/DBMF) is
    "free lunch" for V_HYBRID. Test MF integration in global-only
    portfolios — does adding MF to VT improve Sharpe/MDD as much as it
    did to V_HYBRID?

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

(None yet — iter 001 produced STRONG, not a dead-end. No direction consumed permanently.)

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **Per-iter DSR n_trials** convention (relaxed; see `WINNER_AND_RANKING.md` §3)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** — never reduce passing count (461 per CLAUDE.md)
- **Max 2 h wall-time** per iteration
- **NEVER commit to git** — the shell `run_loop.sh` handles it
- **DO NOT TOUCH** `studies/strategy_hunt_loop/` or `studies/gold_swing_loop/`
  — parallel sessions own those directories.

### G3' adapted gate (added 2026-04-27 by user directive)

**Problem**: G3 nominal (per-WF MDD ≤ 25%) is calibrated for 1× equity.
Stacked portfolios (1.4-1.5× notional) systematically fail it in
systemic crashes (2001/2008/2022) — see iter 003 lesson.

**G3' rule (Opção C — benchmark-comparative)**:

For each WF window:
```
notional_factor = total_notional / 1.0           # e.g., 1.5 for stacked
ref_mdd = max(VT_window_MDD * notional_factor,
              V_HYBRID_MF_window_MDD)
g3_prime_pass = portfolio_window_MDD <= ref_mdd
```

**Application logic**:
- If portfolio `notional_factor ≤ 1.05` (effectively unleveraged) → use G3 nominal (legacy)
- If `notional_factor > 1.05` (stacked) → use G3' adapted; compute and report BOTH
- The iter passes `gates.g3_wf = True/False` based on whichever rule applies
- **Verdict.json must record both** `g3_nominal_pass` and `g3_prime_pass` plus `notional_factor` for transparency

**Rationale**: anchors gate to real-world benchmarks (VT b&h, V_HYBRID+MF)
rather than absolute thresholds. A stacked portfolio passing G3' means it
contained MDD as well as a leveraged-VT would, and at least as well as
the stronger benchmark V_HYBRID+MF. Citation: `[advances_fin_ml, p.196-202]`
(bootstrap-based gate calibration), `[testing_tuning, ch.5-6]` (multi-asset
robustness profiling).

**Backward compat**: iter 002 + iter 004 winners (notional ~1.0×) used G3
nominal — they remain valid winners. Re-scoring under G3' would not change
their status.
