# Flags — LETF EMA100/0%/2_5x synthetic (Phase 3.5b addendum Task B)

## ⚠️ FLAG: SINTÉTICO

L=2.5x **does not correspond to any listed US LETF**
(2024-04). The industry offers 1x/2x/3x only (SSO=2x, UPRO=3x,
SPXL=3x) — there is no 2.5x ETF. Implementation options:

1. **Daily-rebalanced total-return swap** (Pepperstone/IBKR
   swap desk). Feasible for accounts ≥ $25k with sign-off.
2. **Stacking 2x + 1x** (50% SSO + 50% SPY). Gets L_effective
   = 1.5x, not 2.5x — NOT equivalent.
3. **Stacking 2x + 3x** in weights (0.5, 0.5) → L=2.5x but
   each leg rebalances daily. Tracking error vs theoretical
   ~0.5-1.0% annual drag above Gayed's 1% flat-fee baseline.

The backtest below uses the theoretical Gayed formula
`r_synth[t] = L·r_SPX_TR[t] - 0.01/252` (`[leverage_for_the_long_run, p.16]`). Real-world deployment
must budget for the implementation gap above.

## Gate verdicts (reference only — addendum does not gate)

| Gate | Threshold | Measured | Verdict |
|------|-----------|----------|---------|
| CAGR > CDI (~13%/yr) | > 13% | 58.89% | ✅ PASS |
| Sharpe > 1.0 | > 1.0 | 1.882 | ✅ PASS |
| Full-window MaxDD | ≤ 25% | 24.65% | ✅ PASS |
| WF MaxDD ≤ 25% (all windows) | ≤ 25% | see table | ✅ PASS |

## Walk-forward MaxDD per window (8-block Phase 3 B1c schedule)

| Window | Start | End | Bars | MaxDD % | Flag |
|--------|-------|-----|------|---------|------|
| WF1 | 1970-01-02 | 1977-12-30 | 2021 | -24.65% | ✅ PASS |
| WF2 | 1978-01-02 | 1985-12-31 | 2022 | -23.38% | ✅ PASS |
| WF3 | 1986-01-02 | 1993-12-31 | 2024 | -20.17% | ✅ PASS |
| WF4 | 1994-01-03 | 2001-12-31 | 2015 | -21.14% | ✅ PASS |
| WF5 | 2002-01-02 | 2009-12-31 | 2015 | -16.74% | ✅ PASS |
| WF6 | 2010-01-04 | 2017-12-29 | 2013 | -19.07% | ✅ PASS |
| WF7 | 2018-01-02 | 2025-12-31 | 2011 | -22.58% | ✅ PASS |
| WF8 | 2026-01-02 | 2026-04-14 | 70 | -10.80% | ✅ PASS |

## Summary vs Phase 3 winner (L=2x)

Reference: `reports/phase3_5b/letf_rotation_ema100_2x/summary.json`
(full-window CAGR 44.69%, Sharpe 1.848, MaxDD 20.55%).

- This variant CAGR: **58.89%**
- This variant Sharpe: **1.882**
- This variant MaxDD: **24.65%**
- This variant IR vs SPY: **1.837**

Higher leverage buys marginal CAGR at disproportionate MaxDD cost
(Gayed p.17, Table 8 — 3x outperforms 2x on CAGR by <5pp but
doubles worst-decade MaxDD). The 2x winner is the
Sharpe-maximising pick; higher leverage is risk-seeking.

## Citations

- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`.
- Leverage grid (1.25/2/3): `[leverage_for_the_long_run, p.17,
  Table 8]`.
- WF MaxDD ≤ 25% gate: Phase 3 B1c
  (`reports/letf_rotation_b1c_verdict.json`).
- Winner immutability rule: memory.md §Constraints §4.
