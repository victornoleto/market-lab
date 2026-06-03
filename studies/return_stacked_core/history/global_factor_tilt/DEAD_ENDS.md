# Dead ends — Global Factor-Tilt Loop

Read this before proposing a hypothesis. Any direction that matches
structurally with an entry below is **forbidden**.

This loop is freshly bootstrapped (2026-04-26). Carryover dead-ends
from `studies/strategy_hunt_loop/DEAD_ENDS.md` are read-only references
— they apply to a US-only universe and may or may not transfer to the
global universe. Re-test on global universe ONLY if the structural
mechanism is qualitatively different (otherwise document the link to
the US-only dead-end and skip).

---

## DE-001 — 2× single-asset global-equity LETF + binary SMA trend filter

**Iter**: 008 — wldu-gayed  
**Score**: 61/100 PROMISING  
**Date**: 2026-04-27

### What was tested

- WLDU = 2× VTSIM daily-resetting (75bps/y drag: financing + expense)
- Signal: SPYSIM 200-day SMA, checked monthly (Gayed canonical)
- Allocation: 100% WLDU (risk-on) or 100% CASHX (risk-off)
- Based on: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed (2021)

### Why it fails structurally

**Primary structural barrier**: Global equity (VTSIM b&h) already achieves Sharpe ≈ 0.61
through cross-country diversification. Gayed's LRS mechanism improves Sharpe from 0.32
(S&P 500 concentrated) → 0.61 (LRS target). When the starting index already has Sharpe 0.61,
the LRS cannot improve further — it merely doubles both returns and volatility proportionally.

**Quantitative proof** `[leverage_for_the_long_run, p.17, Table 8]`:
- S&P 500 b&h: Sharpe 0.32 → 2× LRS (200d): Sharpe 0.61 (+0.29)
- VTSIM b&h: Sharpe 0.61 → 2× LRS (200d): Sharpe 0.61 (+0.00) [iter 008 empirical]

**Secondary barrier**: 2022 grinding bear market. Monthly SMA check too slow for gradual
rate-regime-driven bear. Monthly exit fires in March 2022, but 2× LETF already absorbed
Jan-Feb 2022 decline → full-period MDD = 44.45% > 35% kill criterion.

### What CAN be tried instead

- This dead-end is SPECIFIC to: (a) global equity as underlying + (b) single-asset 2× LETF
- NOT a dead-end for:
  - Gayed LRS on US equity (SPYSIM/VTISIM, base Sharpe ~0.33) — different starting point
  - Multi-asset LRS (rotate across leveraged LETF alternatives when signal fires)
  - Gayed signal as INPUT to HAA canary (replace VWOSIM canary with SMA-based binary signal)

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (~40y) | 0.609 | 12.69% | 44.45% | 7/7 |
| vt_real (~18y) | 0.501 | 10.11% | 44.45% | 5/7 |
| ndx_real (~16y) | 0.473 | 9.44% | 44.45% | 6/7 |

Score breakdown: Sharpe 0/25, Gates 21/25, DSR 15/15, CAGR 10/15, MDD 10/15, Robustness 5/5 = 61

---

## DE-002 — VAA breadth with higher-notional equity asset in offensive (for Sharpe-max)

**Iter**: 010 — vaa-g3-pure-equity  
**Score**: 90/100 WINNER (formal) — Kill 1 triggered (no Pareto advance)  
**Date**: 2026-04-27

### What was tested

- VAA-G4 (iter 006) but replace BNDSIM (1x notional) in offensive with GDESIM (1.8x notional, 90% S&P + 90% gold)
- Offensive: NTSXSIM, NTSI, NTSE, GDESIM — all equity or equity+gold stacked
- Fixed sleeve: 10% KMLMSIM + 5% GLDSIM
- Based on: "bond contamination hypothesis" — BNDSIM in VAA-G4 offensive drags Sharpe; removing it should improve Sharpe

### Why it fails to advance the Pareto frontier

**Primary structural barrier**: GDESIM's 1.8x notional (vs BNDSIM's 1x) adds proportionally more
variance than return at the portfolio level. Net Sharpe effect: −0.071 on educational dataset
(0.9806 vs 1.052 for iter 006 VAA-G4). CAGR improved +2pp (bond drag removed) but Sharpe
fell −0.07 (variance increased faster than return).

**Pre-committed kill criterion**: edu Sharpe ≤ 1.052 (must beat iter 006 baseline) → TRIGGERED.

**Relationship to iter 009 (HAA+GLD, WINNER)**: iter 010 is Pareto-dominated by iter 009 on all
dimensions (S: 0.981 < 1.120; CAGR: 10.28% < 13.89%; MDD: 18.91% > 20.81%). No new candidate.

### Structural insight on VAA breadth vs HAA canary

The VAA breadth mechanism (4-asset vote, partial defensive when B < 4) produces lower Sharpe
than the HAA canary (binary VWOSIM trigger, full offensive or full defensive). The breadth
mechanism creates "mixed regime" states — partial equity + partial bonds simultaneously —
which increases realized variance vs HAA's clean binary switching.

**Generalizable lesson**: For Sharpe-maximization on a return-stacked equity offensive, the HAA
single-canary architecture dominates VAA multi-vote breadth. The breadth mechanism may be useful
for CAGR-maximization (when risk of full-defensive periods is the bigger concern) but is inferior
for Sharpe.

### What CAN be tried instead

- This dead-end is SPECIFIC to: (a) VAA breadth mechanism + (b) higher-notional equity in offensive
- NOT a dead-end for:
  - HAA canary architecture with different offensive assets (iter 011 direction)
  - VAA breadth with BNDSIM as one offensive asset (iter 006 VAA-G4 is not a dead end — it's STRONG)
  - CAGR-maximization contexts where VAA-G3+GDESIM's +2pp CAGR advantage is the goal

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates | Kill criterion |
|---|---|---|---|---|---|
| educational (~31y) | 0.9806 | 10.28% | 18.91% | 7/7 | **Kill 1 triggered** (0.981 ≤ 1.052) |
| vt_real (~17y) | 0.8491 | 8.91% | 18.91% | 7/7 | — |
| ndx_real (16y) | 0.7188 | 6.99% | 18.91% | 7/7 | — |

Score breakdown: Sharpe 20/25, Gates 25/25, DSR 15/15, CAGR 10/15, MDD 15/15, Robustness 5/5 = 90
