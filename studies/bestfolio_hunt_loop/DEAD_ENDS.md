# Dead ends — Bestfolio Hunt Loop

Read this before proposing a hypothesis. Any direction that matches
structurally with an entry below is **forbidden**.

Carry-over dead-ends from `global_factor_tilt_loop` are included here.
They apply to the same universe (global equity + stacked ETFs via
testfolio synth) and transfer directly.

---

## DE-001 — 2× single-asset global-equity LETF + binary SMA trend filter

**Origin**: global_factor_tilt_loop iter 008 — wldu-gayed
**Score**: 61/100 PROMISING
**Date**: 2026-04-27

### What was tested

- WLDU = 2× VTSIM daily-resetting (75bps/y drag: financing + expense)
- Signal: SPYSIM 200-day SMA, checked monthly (Gayed canonical)
- Allocation: 100% WLDU (risk-on) or 100% CASHX (risk-off)
- Based on: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed (2021)

### Why it fails structurally

**Primary structural barrier**: Global equity (VTSIM b&h) already achieves
Sharpe ≈ 0.61 through cross-country diversification. Gayed's LRS mechanism
improves Sharpe from 0.32 (S&P 500 concentrated) → 0.61 (LRS target). When
the starting index already has Sharpe 0.61, the LRS cannot improve further —
it merely doubles both returns and volatility proportionally.

**Quantitative proof** `[leverage_for_the_long_run, p.17, Table 8]`:
- S&P 500 b&h: Sharpe 0.32 → 2× LRS (200d): Sharpe 0.61 (+0.29)
- VTSIM b&h: Sharpe 0.61 → 2× LRS (200d): Sharpe 0.61 (+0.00) [iter 008 empirical]

**Secondary barrier**: 2022 grinding bear market. Monthly SMA check too slow
for gradual rate-regime-driven bear.

### What CAN be tried instead

- Gayed LRS on US equity (SPYSIM/VTISIM, base Sharpe ~0.33) — different starting point
- Multi-asset LRS (rotate across leveraged LETF alternatives when signal fires)
- Gayed signal as INPUT to HAA canary (replace VWOSIM canary with SMA-based signal)

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (~40y) | 0.609 | 12.69% | 44.45% | 7/7 |
| vt_real (~18y) | 0.501 | 10.11% | 44.45% | 5/7 |
| ndx_real (~16y) | 0.473 | 9.44% | 44.45% | 6/7 |

---

## DE-002 — VAA breadth with higher-notional equity asset in offensive (for Sharpe-max)

**Origin**: global_factor_tilt_loop iter 010 — vaa-g3-pure-equity
**Score**: 90/100 WINNER (formal) — Kill 1 triggered (no Pareto advance vs iter 009)
**Date**: 2026-04-27

### What was tested

- VAA-G4 breadth (4-asset vote, partial defensive when B < 4)
- Offensive: NTSXSIM, NTSI, NTSE, GDESIM (all equity or equity+gold stacked)
- Replace BNDSIM (1x notional) in offensive with GDESIM (1.8x notional)
- Hypothesis: removing bond contamination from offensive improves Sharpe

### Why it fails to advance the Pareto frontier

GDESIM's 1.8x notional adds variance faster than returns at the portfolio
level. Net Sharpe effect: −0.071 vs iter 006 VAA-G4. CAGR improved +2pp
(bond drag removed) but Sharpe fell −0.07.

**Structural insight**: For Sharpe-maximization, HAA single-canary (binary
VWOSIM trigger) dominates VAA multi-vote breadth. The breadth mechanism
creates "mixed regime" states — partial equity + partial bonds simultaneously
— which increases realized variance vs HAA's clean binary switching.

### What CAN be tried instead

- HAA canary architecture with different offensive assets (iter 004 direction)
- VAA breadth with BNDSIM as one offensive asset (not a dead end)
- CAGR-maximization contexts where VAA+GDESIM's +2pp CAGR advantage is the goal

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates | Note |
|---|---|---|---|---|---|
| educational (~31y) | 0.9806 | 10.28% | 18.91% | 7/7 | Kill triggered (0.981 ≤ 1.052) |
| vt_real (~17y) | 0.8491 | 8.91% | 18.91% | 7/7 | — |
| ndx_real (16y) | 0.7188 | 6.99% | 18.91% | 7/7 | — |
