# Flags — LETF EMA100/0%/3x synthetic (Phase 3.5b addendum Task B)

## Gate verdicts (reference only — addendum does not gate)

| Gate | Threshold | Measured | Verdict |
|------|-----------|----------|---------|
| CAGR > CDI (~13%/yr) | > 13% | 74.17% | ✅ PASS |
| Sharpe > 1.0 | > 1.0 | 1.910 | ✅ PASS |
| Full-window MaxDD | ≤ 25% | 28.45% | ⚠️ FAIL |
| WF MaxDD ≤ 25% (all windows) | ≤ 25% | see table | ⚠️ FAIL |

## Walk-forward MaxDD per window (8-block Phase 3 B1c schedule)

| Window | Start | End | Bars | MaxDD % | Flag |
|--------|-------|-----|------|---------|------|
| WF1 | 1970-01-02 | 1977-12-30 | 2021 | -28.45% | ⚠️ FAIL |
| WF2 | 1978-01-02 | 1985-12-31 | 2022 | -27.20% | ⚠️ FAIL |
| WF3 | 1986-01-02 | 1993-12-31 | 2024 | -23.32% | ✅ PASS |
| WF4 | 1994-01-03 | 2001-12-31 | 2015 | -24.49% | ✅ PASS |
| WF5 | 2002-01-02 | 2009-12-31 | 2015 | -19.39% | ✅ PASS |
| WF6 | 2010-01-04 | 2017-12-29 | 2013 | -22.17% | ✅ PASS |
| WF7 | 2018-01-02 | 2025-12-31 | 2011 | -26.67% | ⚠️ FAIL |
| WF8 | 2026-01-02 | 2026-04-14 | 70 | -12.64% | ✅ PASS |

## Summary vs Phase 3 winner (L=2x)

Reference: `reports/phase3_5b/letf_rotation_ema100_2x/summary.json`
(full-window CAGR 44.69%, Sharpe 1.848, MaxDD 20.55%).

- This variant CAGR: **74.17%**
- This variant Sharpe: **1.910**
- This variant MaxDD: **28.45%**
- This variant IR vs SPY: **1.963**

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
