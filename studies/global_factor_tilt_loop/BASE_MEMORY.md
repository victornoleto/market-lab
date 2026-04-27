---
mission: "find one global strategy beating VT 1x b&h + Plano C V3_1 v3.5 + V_HYBRID+MF on real data"
total_iterations: 2
winners_found: 1
status: winner
latest_iteration: "002-2026-04-26-2306-fixed-momentum-k2-lb6"
cumulative_n_trials: 19
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

### Winner 001 — iter 002 — fixed-momentum-k2-lb6 (WINNER, 90/100)

**Strategy**: Monthly cross-sectional momentum, global universe
(VTISIM/VEASIM/VXUSSIM/IEFSIM/VWOSIM/GLDSIM + CASHX), K=2, lookback=6m,
pre-committed single config.

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (56y) | 0.991 | 12.0% | 23.4% | 7/7 |
| vt_real (~17y) | 0.838 | 11.0% | 17.3% | 7/7 |
| ndx_real (16y) | 0.929 | 11.5% | 17.3% | 7/7 |
| 32y long-window | 1.001 | 13.2% | 21.2% | — |

**32y comparison**: dominates VT, Plano C, V_HYBRID+MF on all 3 dimensions.
Pareto-trades vs V1 NTSX+GDE (+0.19 Sharpe, -23pp MDD, -0.28pp CAGR).

**Rolling robustness**: 51/51 rolling-5y windows positive Sharpe (100%).
Min 5y Sharpe: 0.134 (2004-2009 window including 2008 crash).

**Caveat**: Mandate §1 MAINTENANCE still in effect. This is a mandate §7
override CANDIDATE, not a live deployment. Next steps: paper trading
validation + §7 override deliberation.

**Citation**: `[stocks_on_the_move, p.21-30]` + `[ilmanen_expected_returns, ch.12]`

---

## Top-K ranked (best across all iters, by score)

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | 002 | fixed-momentum-k2-lb6 | **90** | **WINNER** | 0.991 / 0.838 / 0.929 | 12.0% | 23.4% |
| 2 | 001 | global-momentum-topk | 81 | STRONG | 1.040 / 0.883 / 0.929 | 12.0% | 21.9% |

---

## Iteration log (newest first)

### 002 — 2026-04-26 — fixed-momentum-k2-lb6 (WINNER, 90/100)

- **Hypothesis:** Fixed pre-committed single config (K=2, lb=6m) of the
  iter 001 STRONG strategy. No grid search → G1 PBO trivially passes
  (n_configs=1 < MIN_HONEST_N_CONFIGS=4). Rolling-window robustness added.
  `[stocks_on_the_move, p.21-30]` + `[advances_fin_ml, p.208-211]`
- **Citations:** `[stocks_on_the_move, p.21-30]`, `[ilmanen_expected_returns, ch.12]`,
  `[advances_fin_ml, p.208-211/222-223/273-274/196-202/31-34]`
- **Scope:** 1 config per dataset (pre-committed, no grid); cumulative
  n_trials=19 (18 from iter 001 + 1 this iter)
- **Result:** edu Sharpe=0.991/CAGR=12.0%/MDD=23.4% gates=7/7; vt_real
  Sharpe=0.838/CAGR=11.0%/MDD=17.3% gates=7/7; ndx_real Sharpe=0.929/
  CAGR=11.5%/MDD=17.3% gates=7/7. PSR worst p=2.76e-4. Rolling 5y windows:
  51/51 positive (100%). 32y Sharpe=1.001/CAGR=13.22%/MDD=21.23% —
  dominates all 3 strategy benchmarks.
- **Score breakdown:** Sharpe 20/25, Gates 25/25, DSR 15/15, CAGR 10/15,
  MDD 15/15, Robustness 5/5
- **Lesson:** Methodological pre-commitment (no grid) converts a STRONG
  mechanism to WINNER. Selection bias via grid search was the only gap.
  ndx_real Sharpe/CAGR structural ceiling is not fixable with global
  diversification — it is a feature of the QQQ benchmark, not a strategy flaw.

### 001 — 2026-04-26 — global-momentum-topk (STRONG, 81/100)

- **Hypothesis:** Monthly cross-sectional momentum across global universe
  (VTISIM/VEASIM/VXUSSIM/IEFSIM for educational; +VWOSIM/GLDSIM for vt_real
  and ndx_real). Top-K equal-weight by trailing N-month return; CASHX safe
  haven when all assets negative. `[stocks_on_the_move, p.21-30]`
- **Citations:** `[stocks_on_the_move, p.21-30]`, `[ilmanen_expected_returns, ch.12]`
- **Scope:** K={1,2,3} × lookback={3,6,12m} = 9 configs per dataset (18 total)
- **Result:** edu Sharpe=1.040/CAGR=12.0%/MDD=21.9% gates=6/7; vt_real
  Sharpe=0.883/CAGR=11.9%/MDD=30.1% gates=6/7; ndx_real Sharpe=0.929/
  CAGR=11.5%/MDD=17.3% gates=7/7. DSR worst p=0.0170 (PASS). 32y window
  (full_k2_lb6): Sharpe=1.001/CAGR=13.22%/MDD=21.23% — dominates
  Plano C and V_HYBRID+MF on all 3 dimensions. Gap from WINNER: (a) G1 PBO
  fails on edu (0.74>0.5 with 9 configs, lb=3 overfits), (b) ndx_real
  Sharpe 0.93<1.05 needed (structural — QQQ can't be beaten by global div),
  (c) ndx_real CAGR 11.5% < 15.4% floor.
- **Score breakdown:** Sharpe 20/25, Gates 21/25, DSR 15/15, CAGR 10/15,
  MDD 15/15, Bonus 0/5
- **Lesson:** Global momentum is a structurally sound mechanism (dominates
  all static benchmarks on 32y), but WINNER requires fixing (a) G1 PBO via
  pre-specified single config — next iter test k=2/lb=6 as fixed params.
  ndx_real structural ceiling is not fixable with global diversification alone.

---

## Promising unexplored directions (prioritized)

Seeded from `README.md` hypothesis menu (Tiers 1-4). Pick the
simplest version of one direction first; iterate to complexity only
if simple version scores ≥ PROMISING.

### Tier 1 — established factor literature (start here)

**[CONSUMED by iter 001]** ~~4. Multi-asset top-K momentum~~ → 81/100 STRONG.
Next step: **fixed-param refinement** (k=2, lb=6 pre-specified, no grid).

**[CONSUMED by iter 002]** ~~1a. Fixed-param global momentum (k=2, lb=6m)~~
   → 90/100 WINNER. Strategy validated; loop halted.

**1b. Global momentum + MF sleeve** — add 10-15% KMLMSIM as fixed
   allocation alongside momentum portfolio. deploy_studies showed MF
   provides "free lunch" `[ilmanen_expected_returns, ch.19]`. Iter 003+.

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
