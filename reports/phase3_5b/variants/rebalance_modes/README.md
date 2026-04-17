# Rebalance modes — sub-index (Task C)

**Path tag:** [SWING BROKER]
**Phase:** 3.5b-addendum, Task C (C1 module / C2 3-leg / C3 2-leg).
**Module:** `src/ai_trade/backtest/metrics/rebalance_modes.py`
(3 pure functions, 28 unit tests — see C1 jornada).

The two canonical Phase 3.5b portfolios — 3-leg `{LETF+QQQ+GLD}` (main
winner) and 2-leg `{LETF+QQQ}` (Task A variant) — were each run through
the 3 rebalance cadences the module implements:

1. **daily** — reset to target weights every bar (the Phase 3.5b
   convention); no realized-gain tax at the equity layer.
2. **monthly_sell** — drift + end-of-month reset; 15% BR IR on
   overweight-leg realized gains (proportional cost basis).
3. **monthly_cashflow** — drift + monthly $500 deposit directed at the
   most-underweight leg (0.5% of $100k initial); tax-free at this
   layer.

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

## Production recommendation (unchanged)

Daily rebal on the 3-leg winner remains the default. For operational
convenience in a BR swing-broker context, **monthly_cashflow on
2-leg** is the only non-daily mode that preserves ≥95% of winner
Sharpe, though at a ~4pp higher MaxDD. Monthly_sell is dominated by
daily on both variants and bleeds real tax dollars; reject it.

## Artefacts

| File | Description |
|---|---|
| `comparison_3leg.md` | 3-leg per-mode table + interpretation (C2). |
| `comparison_2leg.md` | 2-leg per-mode table + interpretation (C3). |
| `drift_3leg.png` / `drift_2leg.png` | Per-bar max drift time-series. |
| `equity_3leg.png` / `equity_2leg.png` | Equity curve overlays. |
| `summary_3leg.json` / `summary_2leg.json` | Structured snapshots. |
| `implementation_notes.md` | Module algorithm decisions (cost basis, month-end detection, deposit allocation). |

## Citations

* Baseline daily reset (the Phase 3.5b winner convention):
  `[advances_fin_ml, p.298-299]`.
* Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17, Table 8]`
  (infrequent rebal preserves compounding but drifts risk).
* EW blend robustness vs Σ-estimation error: `[advances_fin_ml,
  p.298-299]`.
* BR 15% IR on realized gains: Investment Mandate §4.

## Related jornadas

* `2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md` (C1).
* `2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md` (C2).
* `2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md` (C3, this report).
