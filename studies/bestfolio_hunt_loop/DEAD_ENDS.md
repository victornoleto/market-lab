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

---

## DE-003 — Plain BAA-G12 Balanced in the current testfolio universe

**Origin**: bestfolio_hunt_loop iter 001 — baa-g12-balanced  
**Score**: 58/100 MARGINAL  
**Date**: 2026-04-28

### What was tested

- BAA-G12 Balanced, monthly.
- Canary: `SPYSIM`, `VEASIM`, `VWOSIM`, `BNDSIM`.
- Canary signal: 13612W absolute momentum.
- Offensive: top 6 of 12 by SMA(12) relative momentum.
- Defensive: top 3 defensive-risk assets by SMA(12), with `CASHX` replacement.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: Keller BAA SSRN 4166845 + `[stocks_on_the_move, ch.6]`.

### Why it fails structurally

BAA-G12 is a good drawdown reducer but too defensive for the current
Sharpe/CAGR frontier. Net Sharpe was **0.975 / 0.792 / 0.782**, below iter
009 HAA+Gold **1.120 / 1.061 / 0.954** on all datasets. Net CAGR missed the
0.8 x iter009 floor on all three datasets. Gross educational Sharpe reached
1.101, but AnnualDarfEngine tax drag reduced it to 0.975.

**Structural insight**: HAA+Gold already gets enough crash protection from
the `VWOSIM` canary plus fixed diversifier sleeves. BAA's broader canary
breadth buys lower MDD, but it pays for that with too much low-return
defensive exposure. For this objective, that is subordinate to HAA's cleaner
binary canary architecture.

### What CAN be tried instead

- Static capital-efficient stack with lower turnover/tax drag.
- Composite multi-lookback momentum, if kept simple and not just BAA breadth.
- HAA offensive-sleeve changes; do not re-test plain BAA-G12 Balanced without
  a materially different asset universe.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.975 | 10.60% | 16.34% | 7/7 |
| vt_real | 0.792 | 8.42% | 13.93% | 7/7 |
| ndx_real | 0.782 | 7.66% | 12.73% | 6/7 |
