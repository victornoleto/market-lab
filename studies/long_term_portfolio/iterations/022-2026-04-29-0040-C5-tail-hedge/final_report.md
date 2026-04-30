# Iter 022 — Final report: C.5 — Tail-hedge convexo (synthetic put on SPY) — ⚠️ MODEL-ARTIFACT WINNER

**Date**: 2026-04-29
**Slug**: `C5-tail-hedge`
**Selected**: `tail_15pct` = iter 011 base − 15% KMLM + 15% TAIL_HEDGE

---

## 🚨 CRITICAL CAVEAT — READ FIRST

The headline numbers (Sharpe 1.52/1.71/1.68, score 100/100) are
**SYNTHETIC-MODEL ARTIFACTS**, not a deployable result. The hedge model
in this iter is **biased upward by ~+0.5 to +1.0 Sharpe** vs realistic
options. Why:

1. **No vega cost**: real put options become MORE expensive as VIX rises
   — exactly when crashes happen and the hedge pays. My model only pays
   −0.04%/day premium during NON-drawdown periods, understating cost in
   crisis-rich years.
2. **Hindsight via 21d trigger**: the model "knows" we're in a drawdown
   via the 21d return threshold; in real life you must HOLD the put
   BEFORE the crash starts, paying premium throughout normal periods.
3. **Path-dependence wrong**: real options pay (strike − spot) at expiry,
   not 2× daily drops compounded. My model double-counts the convexity.
4. **No spread/liquidity drag**: real ATM puts cost ~6%/yr in premium
   net of slippage; my model uses ~10%/yr decay flat regardless of vol
   regime, which is much cheaper than reality during crisis years.

**Honest interpretation**: a real option-based tail hedge would likely
deliver **+0.05 to +0.15 Sharpe edge** (net of true premium drag) — maybe
enough to be tier WINNER on paper, **NOT** the +0.85 edge shown here.

**This iter is a methodological warning, not a strategy candidate.** The
score-100 result is an excellent **negative example** of how synthetic
hedge backtests can fool an unwary modeler.

---

## Headline metrics (synthetic model — DO NOT USE FOR DEPLOY)

| dataset | gross S | edge vs avg(SPY,VT) | gross CAGR | gross MDD | gates |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.520 | +0.849 ⚠️ | 14.71% | 17.86% | 7/7 |
| vt_real   | 1.710 | +1.004 ⚠️ | 18.57% | 9.54%  | 7/7 |
| ndx_real  | 1.684 | +0.760 ⚠️ | 16.58% | 7.33%  | 7/7 |

Per-config grid (all dominantly upward — itself a red flag):

| config | TAIL_HEDGE % | lh_56y | vt_real | ndx_real | lh MDD |
|---|---:|---:|---:|---:|---:|
| `tail_5pct`   | 5%   | 1.257 | 1.203 | 1.294 | 19.8% |
| `tail_7pct`   | 7.5% | 1.323 | 1.328 | 1.391 | 17.7% |
| `tail_10pct`  | 10%  | 1.389 | 1.455 | 1.489 | 17.2% |
| `tail_15pct` ✅ | 15%  | **1.520** | **1.710** | **1.684** | 17.9% |

**Monotonic improvement with hedge weight** is the classic signature of an
under-priced hedge. Real options would show diminishing returns as
allocation grows because premium accelerates non-linearly. Here, the
linear premium (−0.04%/day) means more hedge = more synthetic alpha
without realistic cost. **This is the bug, not the feature.**

---

## What was actually learned

1. **Synthetic hedge models are dangerous**: even with reasonable-looking
   parameters (5% drawdown trigger, 2× payoff multiplier, 10%/yr decay),
   the result is grossly inflated relative to real options. The 21d
   trigger introduces hindsight — the strategy "sees" the drawdown
   before paying for it.
2. **A proper deployable test would require**: (a) actual SPY put options
   data (Tiingo doesn't have it; would need OptionMetrics or similar),
   OR (b) VXX/VIXY futures returns as a proxy for vol-spike payoff (with
   their realistic ~−40%/yr decay in normal periods).
3. **The honest version of this thesis**: iter 011 + 5-10% VXX (not
   synthetic puts). VXX from Tiingo would give realistic tail-hedge
   behavior (massive crash payoff + brutal decay drag). Defer to a
   future iter if the user wants to pursue this seriously.

---

## Score breakdown (mechanical, but invalid)

| # | criterion | iter 022 / max |
|---|---|---:|
| 1 | Sharpe edge | 25/25 |
| 2 | Gates | 25/25 (cross-ds bonus) |
| 3 | DSR | 15/15 (effectively zero p) |
| 4 | CAGR floor | 15/15 |
| 5 | MDD ceiling | 15/15 |
| 6 | Robustness | 5/5 |
| **total** | | **100/100** |

Score is a perfect 100. **Score's perfection is itself the proof of model failure** — no real long-term portfolio strategy clears every gate at every threshold; if the model says 100, the model is wrong.

---

## Pre-committed kill criteria

KILL #1 (best-of-grid loses iter 011): NOT FIRED (synthetic alpha dominates).
KILL #2 (monotonic Sharpe regression with hedge weight): NOT FIRED — actually
**MONOTONIC IMPROVEMENT** which is itself a red flag (see above).

Neither kill catches the real failure mode: **the kill criteria assumed the
hedge model would be cost-realistic; my implementation isn't**. Lesson for
future iters: when adding a synthetic asset whose returns are MODELED rather
than measured, add a "no-free-lunch" sanity check (e.g., assert hedge
Sharpe < benchmark Sharpe alone, or assert monotonic worsening as weight
rises beyond optimal).

---

## Lesson — DE-022 logged as "methodological dead-end" not "strategy dead-end"

Cannot conclude tail hedging is good or bad in this universe — only that the
synthetic model used here is invalid. A proper test requires real options
data or VXX proxy.

**For the loop's user-facing summary**: iter 022's headline numbers must be
flagged as model artifact, NOT included in any "best strategy" comparison.
The only legitimate winners-substantively-positive in this loop remain:
- iter 011 (substantive incumbent, Sharpe 1.046/0.960/1.104)
- iter 014 (mechanical incumbent, Sharpe 1.055/0.885/1.052)
- iter 016 (UMD overlay, Sharpe 1.223/0.943/1.150 — first positive signal)

---

## Citations

- Spitznagel *Safe Haven* (2021) — convex tail-hedge framework (real, not modeled)
- `[risk_parity, ch.5]` Carlson — context for cap-eff core retained
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

---

## Next directions

iter 022 is the **last in fila 016-022**. Recommended next:
1. Build a proper VXX-based hedge sub-iter (real Tiingo data, real decay).
2. Synthesize the **breadth findings 016-022** into a strategy zoo report
   for the user to decide deploy direction.
3. Consider declaring iter 011 deploy-ready (or pursuing iter 016 UMD as
   secondary candidate) and starting paper trading.

*Generated 2026-04-29 by long_term_portfolio loop iter 022.*
*⚠️ Synthetic-model artifact: do not deploy or compare as substantive winner.*
