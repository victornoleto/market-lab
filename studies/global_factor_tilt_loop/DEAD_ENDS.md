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
