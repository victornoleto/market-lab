---
mission: "find one global strategy beating VT 1x b&h + Plano C V3_1 v3.5 + V_HYBRID+MF on real data"
total_iterations: 0
winners_found: 0
status: iterating
latest_iteration: ""
cumulative_n_trials: 0
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

(None yet — first iter pending.)

---

## Top-K ranked (best across all iters, by score)

(Empty — first iter pending.)

---

## Iteration log (newest first)

(Empty — first iter pending.)

---

## Promising unexplored directions (prioritized)

Seeded from `README.md` hypothesis menu (Tiers 1-4). Pick the
simplest version of one direction first; iterate to complexity only
if simple version scores ≥ PROMISING.

### Tier 1 — established factor literature (start here)

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

4. **Multi-asset top-K momentum** (port of iter 079 to global).
   Universe: VTISIM + VEASIM + VWOSIM + IEFSIM + GLDSIM with BNDSIM
   fallback. Deploy: AVUS + AVDE + AVEM + IEF + GLD with BND fallback.

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

(None yet — DEAD_ENDS.md empty initially. Carryover dead-ends from
`studies/strategy_hunt_loop/DEAD_ENDS.md` are read-only references; do
not duplicate them here unless this loop independently confirms them on
the global universe.)

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
