# Rebalance modes — sub-index (Task C)

**Path tag:** [SWING BROKER]
**Phase:** 3.5b-addendum, Task C (C1 module / C2 3-leg / C3 2-leg / C4
threshold sweep).
**Module:** `src/market_lab/backtest/metrics/rebalance_modes.py`
(**4 pure functions, 39 unit tests** — see C1 + C4 jornadas).

The canonical Phase 3.5b portfolios — 3-leg `{LETF+QQQ+GLD}` (main
winner) and 2-leg `{LETF+QQQ}` (Task A variant) — were each run through
the 3 calendar-cadence rebalance modes the module implements; C4 adds a
**drift-triggered** cadence on the 3-leg winner:

1. **daily** — reset to target weights every bar (the Phase 3.5b
   convention); no realized-gain tax at the equity layer.
2. **monthly_sell** — drift + end-of-month reset; 15% BR IR on
   overweight-leg realized gains (proportional cost basis).
3. **monthly_cashflow** — drift + monthly $500 deposit directed at the
   most-underweight leg (0.5% of $100k initial); tax-free at this
   layer.
4. **threshold_Xpp** (C4) — drift + rebalance only when
   `max|actual - target| > X pp`; 15% IR on realized gains, same
   mechanic as `monthly_sell` but **event-driven, not calendar-driven**.
   Institutional standard `[advances_fin_ml, p.275-278]`.

Both variants were run on their *own* longest common window, not a
unified one — C2 used GLD-limited (2004-11-18 → 2026-04-14, 21.36 yrs),
C3 used QQQ-limited (2001-05-14 → 2026-04-14, 24.87 yrs). The delta in
window length must be kept in mind when reading absolute figures.

## Side-by-side comparison

Columns: CAGR / Sharpe / MaxDD / Max drift / Mean drift / Taxable
events-per-year / IR paid-per-year / Deposits-per-year.

### 3-leg `{LETF+QQQ+GLD}` — window 2004-11-18 → 2026-04-14 (21.36 yrs)

| Mode | CAGR | Sharpe | MaxDD | Max drift | Mean drift | Events/yr | IR/yr | Dep/yr |
|---|---|---|---|---|---|---|---|---|
| daily            | 25.56% | **2.108** | **10.86%** | 0.00% | 0.00% | 0.0 | $0 | $0 |
| monthly_sell     | 23.79% | 1.964 | 10.94% | 4.81% | 0.82% | 17.9 | $30,740 | $0 |
| monthly_cashflow | 40.47%* | 1.944 | 17.78% | 65.05% | 40.10% | 0.0 | $0 | $6,039 |

### 2-leg `{LETF+QQQ}` — window 2001-05-14 → 2026-04-14 (24.87 yrs)

| Mode | CAGR | Sharpe | MaxDD | Max drift | Mean drift | Events/yr | IR/yr | Dep/yr |
|---|---|---|---|---|---|---|---|---|
| daily            | 31.59% | **1.888** | **14.41%** | 0.00% | 0.00% | 0.0 | $0 | $0 |
| monthly_sell     | 29.94% | 1.800 | 14.46% | 5.23% | 0.60% | 12.1 | $144,794 | $0 |
| monthly_cashflow | 42.63%* | 1.881 | 18.15% | 49.30% | 32.69% | 0.0 | $0 | $6,033 |

*Cashflow CAGR is inflated by $6k/yr deposits compounding — it is
**not** pure return alpha; compare to the other two modes' CAGR which
are deposit-free.

## Hypothesis C3: "2-leg less sensitive to drift because ρ=0.555"

Partially confirmed, with a non-trivial twist:

| Metric | 2-leg | 3-leg | Δ (2-leg − 3-leg) | Verdict |
|---|---|---|---|---|
| Mean drift, monthly_sell | 0.60% | 0.82% | **−0.22pp** | ✅ 2-leg drifts less on average |
| Max drift, monthly_sell  | 5.23% | 4.81% | +0.42pp | ❌ 2-leg peaks slightly higher |
| Mean drift, monthly_cashflow | 32.69% | 40.10% | **−7.41pp** | ✅ 2-leg catches up faster on cashflow |
| Max drift, monthly_cashflow  | 49.30% | 65.05% | **−15.75pp** | ✅ large: $500 on 2 legs > $500 split over 3 |

**Mean drift and cashflow drift confirm the hypothesis.** The high
LETF↔QQQ correlation (0.555) keeps the two legs moving together on a
typical bar, so the rebal pressure accumulates slowly — the 3-leg case
has GLD moving opposite, which creates more inter-leg dispersion on
average.

**Max drift on monthly_sell breaks the hypothesis:** 2-leg's 5.23%
peak exceeds 3-leg's 4.81%. During extreme windows (e.g. the QQQ
2001-2002 dotcom bust vs LETF-on-SPY regime filter staying flat in
cash), the 2-leg legs *can* decouple more than 3-leg because 3-leg
dilutes extremes across a third counter-cyclical leg. So:

> Correlation lowers the *typical* drift, not the *tail* drift.

## IR-per-year paradox: 2-leg pays 4.7× more

The most striking delta: monthly_sell pays **$144,794/yr IR** in
2-leg vs **$30,740/yr** in 3-leg. Drivers:

1. **Larger per-leg notional** — EW of 2 is 50% per leg vs 33% in
   EW of 3 ⇒ every rebal trade is ~1.5× the dollar size.
2. **Longer window with higher cumulative gains** — 2-leg window is
   3.5 yrs longer and the CAGR is ~6pp higher ⇒ more unrealized
   profit sitting inside each leg, so each partial sell realizes a
   bigger taxable slice.
3. **No tax-dragging diversifier** — GLD in 3-leg has near-zero long-
   run CAGR; rebals that touch GLD frequently realize losses or
   small gains, dampening total IR paid.

This alone says: **if the user insists on monthly_sell, 3-leg is
materially cheaper tax-wise**. The daily winner sidesteps this
entirely.

## Ranking per variant

* **3-leg:** `daily > monthly_sell > monthly_cashflow` (Sharpe).
  Daily is cleanly the best; monthly_sell drops 0.14 Sharpe with
  modest tax; cashflow's CAGR is misleading (deposits compound).

* **2-leg:** `daily ≈ monthly_cashflow > monthly_sell` (Sharpe).
  Daily 1.888 and cashflow 1.881 are statistically indistinguishable;
  cashflow *adds* $6k/yr of savings on top — so for a BR swing-broker
  user DCA-ing $500/mo, cashflow is operationally attractive **if
  they can tolerate MaxDD 18.15% vs daily's 14.41%**.

## Threshold-based rebalancing (Task C4)

C4 asked the operational question the calendar modes can't answer:
"If monthly means 12 DARFs/yr on top of ~12 inside-leg DARFs, what
threshold-triggered cadence preserves most of the daily Sharpe while
cutting rebal-layer DARFs to a handful per year?"

Sweep on the 3-leg winner (same GLD-limited window 2004-11-18 →
2026-04-14, 21.36 yrs, $100k initial):

| Mode | CAGR | Sharpe | ΔSharpe | MaxDD | Mean drift | Dates/yr | IR/yr |
|---|---|---|---|---|---|---|---|
| daily (winner)   | 25.56% | **2.108** | +0.000 | 10.86% | 0.00%  | 0.00 | $0      |
| threshold 5pp    | 24.66% | 2.002 | −0.106 | 11.10% | 2.27%  | 1.31 | $23,815 |
| threshold 10pp   | 25.47% | 1.990 | −0.118 | 11.12% | 4.08%  | 0.61 | $20,978 |
| threshold 15pp   | 26.35% | 1.972 | −0.136 | 12.24% | 7.64%  | 0.37 | $17,582 |
| threshold 20pp   | 27.15% | 1.972 | −0.136 | 12.32% | 9.46%  | 0.28 | $21,680 |
| annual only (Y)  | 25.07% | 1.967 | −0.141 | 11.56% | 3.36%  | 1.08 | $22,001 |
| never (BH)       | 40.33%* | 1.881 | −0.226 | 17.99% | 43.89% | 0.00 | $0      |

*`never`'s CAGR is inflated by unbounded LETF drift — it rises to
~56% of the portfolio by the window's end, masquerading as
"return alpha" when it is actually concentration.

**Key findings:**

* **Threshold 5pp is the operational best-Sharpe variant:** 2.002
  Sharpe = **95.0% of daily's 2.108**, at 1.31 DARFs/yr from the rebal
  layer (≈ 13.3 total DARFs/yr when combined with ~12 inside-leg).
* **Threshold 10-15pp** are the aggressive-low-DARF variants: 0.4-0.6
  rebal-dates/yr at ~94% of daily Sharpe, and CAGR slightly *higher*
  than daily because the drift accumulates in the faster-compounding
  LETF leg.
* **`annual only`** (28 events / 23 rebal dates across 21 yrs)
  materially underperforms thresholded variants at the same DARF/yr
  burden — threshold is information-driven, annual is time-driven,
  so annual wastes trades when the portfolio is close to target and
  misses trades when it has drifted mid-year.
* **`never`** (pure BH) shows that abandoning rebalance entirely
  costs 0.23 Sharpe vs daily — the largest penalty in the table.
  Threshold rebal recovers most of that gap at a fraction of the
  calendar rebal's tax burden.

Artefacts: `threshold_sweep.md`, `threshold_sweep_summary.json`,
`threshold_sweep_events.png`.

## Production recommendation (updated)

**Default remains daily rebal on the 3-leg winner.** It's the Sharpe
leader (2.108) and the backtest's canonical convention.

For users who find daily rebalance operationally prohibitive (retail
BR swing investor balancing DARFs + bookkeeping):

* **Preferred operational fallback → `threshold_5pp` on 3-leg** —
  preserves 95% of daily Sharpe at 1.3 DARFs/yr from the rebal layer.
  Superior to `monthly_sell` (which pays ~$30k/yr IR and ~18 DARFs/yr
  for the same window, Sharpe 1.964) on every axis: more Sharpe, less
  tax, fewer DARFs.
* **Aggressive-low-DARF fallback → `threshold_10pp` or `threshold_15pp`**
  — 0.4-0.6 DARFs/yr from rebal layer, ~94% of daily Sharpe. Pick
  this if bookkeeping is the binding constraint.
* **Cashflow fallback on 2-leg** remains valid for a DCA-first user
  (see C3 recommendation) but now competes with threshold variants
  that don't require a cash inflow model.
* **Rejected:** `monthly_sell` (dominated by threshold on every
  metric); `annual_only` (dominated by threshold at the same DARF
  burden); `never` (worst Sharpe, concentration risk).

## Artefacts

| File | Description |
|---|---|
| `comparison_3leg.md` | 3-leg per-mode table + interpretation (C2). |
| `comparison_2leg.md` | 2-leg per-mode table + interpretation (C3). |
| `threshold_sweep.md` | 3-leg threshold sweep {5/10/15/20pp, annual, never} + DARF/yr table (C4). |
| `drift_3leg.png` / `drift_2leg.png` | Per-bar max drift time-series. |
| `equity_3leg.png` / `equity_2leg.png` | Equity curve overlays. |
| `threshold_sweep_events.png` | Bar/line plot — dates/yr vs Sharpe across cadences (C4). |
| `summary_3leg.json` / `summary_2leg.json` / `threshold_sweep_summary.json` | Structured snapshots. |
| `implementation_notes.md` | Module algorithm decisions (cost basis, month-end detection, deposit allocation, threshold trigger). |

## Citations

* Baseline daily reset (the Phase 3.5b winner convention):
  `[advances_fin_ml, p.298-299]`.
* Threshold rebalancing as institutional practice:
  `[advances_fin_ml, p.275-278]`.
* Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17, Table 8]`
  (infrequent rebal preserves compounding but drifts risk).
* EW blend robustness vs Σ-estimation error: `[advances_fin_ml,
  p.298-299]`.
* BR 15% IR on realized gains: Investment Mandate §4.

## Related jornadas

* `2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md` (C1).
* `2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md` (C2).
* `2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md` (C3).
* `2026-04-17-2315-phase3.5b-addendum-task-c4-threshold-rebalance.md` (C4).
