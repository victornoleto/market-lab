# Iter 013 Hypothesis — HAA SmartStack + ZROZSIM Defensive

**Date**: 2026-04-27  
**Slug**: haa-zero-coupon-defensive  
**Status**: IN_PROGRESS

---

## Hypothesis

HAA SmartStack (iter 009 WINNER, S=1.120) leaves crisis alpha on the table by
constraining its defensive palette to {IEFSIM, BNDSIM, CASHX}. Adding ZROZSIM
(25y zero-coupon bond, highest convexity bond in the testfolio cache) as a fourth
defensive option enables the HAA adaptive mechanism to capture **flight-to-safety
convexity** in deep equity bear markets — without any downside in inflationary bears,
because HAA's top-1 selection naturally falls back to CASHX when ZROZSIM is negative.

Structural change: defensive universe `{IEFSIM, BNDSIM, CASHX}` →
`{ZROZSIM, IEFSIM, BNDSIM, CASHX}`. All other parameters identical to iter 009.

---

## Primary citation

`[risk_parity, ch.5]` — Bridgewater's All-Weather framework: long-duration zero-coupon
bonds are the highest-convexity instrument in flight-to-safety environments; their
excess return during equity bear markets is a function of duration × rate-change,
making 25y zeros a natural tail hedge inside a well-diversified portfolio.

Secondary: `[stocks_on_the_move, ch.6]` (HAA canary unchanged),
`[advances_fin_ml, p.208-211/222-223/196-202/31-34]` (gate battery unchanged),
`[leverage_for_the_long_run, p.40-60]` (stacking offensive unchanged).

---

## Edge source

VT/Plano C/V_HYBRID all miss **adaptive crisis convexity**: static portfolios hold bond
allocations that don't scale with crisis severity, and HAA iter 009 caps its defensive
upside at IEFSIM (7-10y duration, ~17% in 2008). ZROZSIM (25y zero-coupon, ~64% in 2008,
~23% in 2020) captures the full flight-to-safety move. Because HAA's momentum-ranking
mechanism only selects ZROZSIM when it's the top-ranked defensive asset, the downside
in inflationary bear markets (ZROZSIM -39% in 2022) is automatically avoided —
HAA would select CASHX (+2%) instead.

Empirical basis (testfolio cache):
| Year | ZROZSIM | IEFSIM | CASHX | HAA would select |
|---|---|---|---|---|
| 2008 | **+63.78%** | +17.07% | +1.36% | ZROZSIM |
| 2020 | **+22.56%** | +9.50% | +0.35% | ZROZSIM |
| 2022 | −39.26% | −14.36% | **+2.05%** | CASHX (natural fallback) |

---

## Datasets to test

All three standard datasets:
- `educational`: VWOSIM-binding 1994-05 → 2026-04 (~31y)
- `vt_real`: 2008-06 → 2026-04 (~17y, contains 2008 GFC + 2020 COVID + 2022)
- `ndx_real`: 2010-02 → 2026-04 (~16y)

ZROZSIM starts 1986-01-02 → full coverage for all three datasets.

---

## Pre-committed kill criterion

**edu Sharpe ≤ 1.120** — must strictly advance the Pareto frontier beyond iter 009.

If the kill criterion triggers: structural insight is that ZROZSIM's 2008 convexity
bonus is outweighed by regime-specific volatility (even with HAA fallback to CASHX).
Document as DEAD_END for "adding convex defensive assets to HAA palette."

---

## Expected budget

- **Configs**: 1 (pre-committed, no grid)
- **n_trials**: 1 → PBO auto-pass, DSR minimal deflation
- **Wall-time estimate**: < 10 min (same infra as iter 009)

---

## Implementation plan

1. Copy iter 009's `backtest.py` to `013-*/backtest.py`
2. Modify:
   - Add `"ZROZSIM"` to `RAW_TICKERS`
   - In `simulate_haa_gold`: change `defensive = ["IEFSIM", "BNDSIM", "CASHX"]` to
     `defensive = ["ZROZSIM", "IEFSIM", "BNDSIM", "CASHX"]`
   - Same change in `simulate_haa_gold_numpy`
   - Update kill criterion comment to `≤ 1.120` (iter 009 Pareto frontier)
   - Update `hypothesis_slug` and file paths
3. Run on all 3 datasets
4. Gate battery + score via `scoring.py`
5. Save `results.json`, `verdict.json`
6. Write `final_report.md`
7. Update `BASE_MEMORY.md` + `DEAD_ENDS.md` if applicable
8. Run `plot_helper.py --iter 013`
