# Iter 010 — VAA-G3 Pure-Equity Offensive (no BNDSIM)

**Date**: 2026-04-27  
**Slug**: vaa-g3-pure-equity  
**Status**: in-progress

---

## Hypothesis

VAA-G4 SmartStack (iter 006, STRONG 85/100) failed to beat HAA SmartStack
on CAGR because BNDSIM appeared as one of its 4 offensive assets. This
"bond contamination" created two structural drags:

1. **Breadth inflation**: When bonds trend up (rate-cutting cycle), BNDSIM
   adds to B (count of positive-momentum offensives), keeping the strategy
   in a partial-bond allocation even when equity is running — missing pure-
   equity upside.
2. **Offensive drag in bond bear markets**: In 2022, BNDSIM fell hard.
   Any breadth allocation to BNDSIM while rates rose dragged total CAGR.

**Fix**: Replace BNDSIM in the offensive basket with GDESIM (90% S&P +
90% gold, capital-efficient stacked). Now all 4 offensive assets track equity
or equity+gold momentum, not interest-rate trends.

The resulting portfolio:
- Offensive (4 assets): NTSXSIM, NTSI, NTSE, GDESIM  ← same as HAA iter 005/009 offensive
- Defensive (3 assets): IEFSIM, CASHX, BNDSIM  ← unchanged
- Fixed sleeve: 10% KMLMSIM + 5% GLDSIM  ← same as iter 006/009
- Dynamic: 85%, allocated per VAA 13612W breadth rule
- Signal: 13612W (12·r1 + 4·r3 + 2·r6 + r12) / 19

This is an exact structural test of the claim that "bond contamination was
VAA's only weakness" — the offensive set is identical to HAA's, but the
signal mechanism is breadth voting (4 assets) vs single canary (1 asset).
If VAA-G3 matches or beats HAA (iter 009, S=1.120/CAGR=13.89%/MDD=20.81%),
it suggests the breadth mechanism is competitive with the canary approach.

---

## Primary citation

`[stocks_on_the_move, ch.6]` — HAA/VAA momentum mechanics, breadth signal
construction, 13612W weighting scheme.

**Supporting**: `[trading_evolved, p.197]` — MF free-lunch sleeve.
`[leverage_for_the_long_run, p.40-60]` — return-stacking justification.
`[advances_fin_ml, p.208-211/222-223/196-202/31-34]` — gate battery.

---

## Edge source

VAA-G4 (iter 006) achieves Sharpe 1.052 but fails CAGR floor on vt_real/ndx_real
because BNDSIM in the offensive basket acts as a return-drag when bonds underperform
equity. GDESIM (equity+gold) is always a positive-return proxy when equity is in a
bull regime, and its 13612W signal will align with equity momentum rather than
rate-regime momentum. This removes one of the two root causes of iter 006's CAGR gap.

HAA (iter 009) achieves this offensive lineup but uses a single canary (VWOSIM
binary switch). This iter tests whether the VAA breadth signal (more nuanced,
4-asset vote) provides similar or better risk-adjusted performance.

---

## Datasets

- `educational`: VTSIM proxy 1994-05 → 2026-04 (~31y, VWOSIM-binding)
- `vt_real`: VTSIM proxy 2008-06 → 2026-04 (~17y)
- `ndx_real`: QQQSIM proxy 2010-02 → 2026-04 (~16y)

---

## Pre-committed kill criteria

1. **Kill 1** — edu Sharpe ≤ 1.052: strategy is strictly subordinate to iter 006 VAA → discard
2. **Kill 2** — any WF G3' fail across 3 datasets → structural G3 weakness → report as dead end

---

## Expected budget

- Configs: 1 (single pre-committed config, n_trials=1 → DSR honest, PBO trivial)
- Wall-time: ~5 min (reuse iter 006 code, minimal delta)
- cumulative n_trials after this iter: 27

---

## Implementation plan

1. Copy iter 006 backtest.py
2. Change offensive = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"] (BNDSIM → GDESIM)
3. GDESIM is loaded directly from testfolio cache (1968-04-01, 58y)
4. Keep defensive = ["IEFSIM", "CASHX", "BNDSIM"] unchanged
5. Keep sleeve = 10% KMLM + 5% GLD unchanged
6. Update NOTIONAL_FACTOR to ~1.5 (GDESIM is 1.8x notional, vs BNDSIM 1.0x)
7. Run gate battery + score
8. Write final_report.md + verdict.json

Note on NOTIONAL_FACTOR: GDESIM is ~1.8x notional (90% S&P + 90% gold).
Average notional of offensive basket: (1.5 + 1.5 + 1.5 + 1.8) / 4 = 1.575.
Using 1.5 conservatively (HAA/iter006 baseline) since GDESIM appears only
when breadth is positive and its 1.8x is offset by other 1.5x assets in
equal-weight blend.
