# Rebalance modes — implementation notes

Module: `src/market_lab/backtest/metrics/rebalance_modes.py` (Tasks C1 + C4).
Tests: `tests/test_rebalance_modes.py` (**39 cases** — 28 for C1's 3
functions, 11 for C4's `apply_threshold_rebalance`).
Consumers: `scripts/run_phase3_5b_task_c2_rebalance_3leg.py` (C2),
`scripts/run_phase3_5b_task_c3_rebalance_2leg.py` (C3),
`scripts/run_phase3_5b_task_c4_threshold_rebalance.py` (C4).

This file documents the non-trivial algorithmic choices so a reader
of the two comparison reports does not have to reverse-engineer the
module.

## 1. Inputs & contracts

```python
apply_daily_rebalance(returns_df, target_weights, initial_capital)
apply_monthly_sell_rebalance(returns_df, target_weights,
                             initial_capital, tax_rate=0.15,
                             rebalance_freq="M")  # or "Y" for annual
apply_monthly_cashflow_rebalance(returns_df, target_weights,
                                 monthly_deposit, initial_capital)
apply_threshold_rebalance(returns_df, target_weights, threshold_pp,
                          initial_capital, tax_rate=0.15)
```

* `returns_df: DataFrame` — one column per leg, daily returns already
  net of per-trade friction (the Phase 3.5b winner legs arrive here
  with their own 15% BR IR on profitable trade exits already applied
  upstream via `portfolio_3leg.aggregate_leg_trades`; see C2 spec
  §Interpretation notes).
* `target_weights: dict[str, float]` — must sum to 1.0 ± 1e-9 and
  have the same keys as `returns_df.columns`. Validated on entry.
* `initial_capital: float` — starting notional. The daily baseline
  always starts at this value; monthly_cashflow starts at this and
  grows with deposits.

All three functions return a `RebalanceResult` dataclass exposing:
`equity`, `leg_equity` (DataFrame), `weights` (DataFrame), `drift`
(DataFrame of `actual_weight − target_weight`), `taxable_events`
(list[TaxableEvent]), `total_tax_paid`, `total_deposits`.

## 2. Month-end detection

The rebal trigger fires on the **last bar of each calendar month**,
not on a fixed-day-count cadence. Rationale:

* The daily returns index is the trading-day index (NYSE), which has
  21 ± 2 bars per month ⇒ a fixed-21-bar cadence would drift against
  the calendar.
* A BR swing-broker's monthly rebal script (quantopian/ib cron style)
  is typically end-of-month, matching the IR-recognition period.

Implementation: walk the index, compare `idx[i].month ≠ idx[i-1].month`
⇒ trigger on bar `i-1` (the last bar of the closing month). The
*current* bar (`i`) is the first bar of the new month, so its
returns are applied *after* the rebal fired.

## 3. Cost basis policy (monthly_sell)

Per-leg cost basis = **proportional average** (NOT FIFO):

* At leg-level, we track a running average cost. On a partial sell of
  fraction `f` of the leg's current equity, the realized gain is
  `f × (current_value − cost_basis)`, and `cost_basis ← cost_basis ×
  (1 − f)` (we sold a proportional slice of the basis). Buys at the
  receiving underweight leg add to the basis at current market price.

Why proportional and not FIFO?

1. FIFO matches broker tax-lot rules in many jurisdictions, but the
   module is not yet plugged into a real broker feed — FIFO would
   require per-lot bookkeeping that serves no current purpose.
2. Proportional is the conservative approximation for
   buy-and-hold-with-periodic-rebal strategies: it assumes every
   historical purchase contributed equally to the current position.
   For a daily-compounded strategy where the legs are the *returns of*
   other strategies (not buy-and-hold positions), this is a closer
   mental model than FIFO.
3. It allows a single scalar `cost_basis` per leg instead of a
   per-trade list, keeping the module self-contained.

Tax is `max(0, realized_gain) × tax_rate` — losses are not offset
against gains in the same period (consistent with BR swing-broker
monthly IR filing where each sell's gain/loss is computed
independently and losses carry forward separately; see Investment
Mandate §4).

## 4. Deposit allocation (monthly_cashflow)

Rule: **100% of the monthly deposit lands on the leg with the
largest negative drift** (most underweight vs target). Rationale:

1. **No-sell discipline** — the whole point of cashflow mode is to
   avoid triggering realized-gains IR. Splitting the deposit across
   legs diluted the rebalance effect *and* added no value.
2. **Most-underweight leg has the lowest recent return** — directing
   fresh cash there is the mechanical equivalent of value-averaging
   (buy more when cheap).
3. If *all* legs are positive-drift (no single leg is below target,
   e.g. early in the backtest before compounding separates the legs),
   the deposit goes to the leg with the smallest drift. This is a
   degenerate case that fires ~0 times in practice (verified in the
   C2/C3 runs — `n_deposit_events = n_months − 0`).

## 4.5. Threshold trigger (C4)

`apply_threshold_rebalance(threshold_pp)` replaces the calendar-driven
month-end trigger with a **post-return drift check**. On each bar:

1. Apply leg returns (buy-and-hold compounding).
2. Compute `max_drift = max_j |actual_w_j - target_w_j|` on the new
   leg equities.
3. If `max_drift * 100 > threshold_pp` → execute the same sell-overweight
   → buy-underweight mechanic as `apply_monthly_sell_rebalance` (same
   proportional cost basis, same 15% IR on realized gains). Otherwise
   let drift continue.

**Parameter semantics:** `threshold_pp` is in **percentage points** of
weight drift. Two degenerate cases documented in the tests:
* `threshold_pp = 0.0` → trigger every bar (differs from daily rebal in
  that it pays rebal-layer tax — arguably not useful in practice).
* `threshold_pp ≥ max-achievable-drift` (e.g. `1e9`) → never triggers,
  equivalent to pure buy-and-hold.

**Why strict `>` (not `≥`)?** A leg that lands *exactly* on the
threshold by chance should not trigger a tax event — the practitioner's
bar is "materially past the line", not "reached the line". Tests
`test_trigger_cross_is_strict_greater_than` pin this.

**No post-rebal residual drift (zero-tax case):** when `tax_rate=0.0`,
the rebal fully resets to target on the trigger bar (tests
`test_drift_resets_on_rebalance_dates`). With non-zero tax, post-rebal
drift equals `total_tax_this_bar / portfolio_value` — the same residual
documented for `apply_monthly_sell_rebalance`.

**Distinction vs calendar modes:** threshold is **information-driven**
(rebal when the book demands it), calendar is **time-driven** (rebal
on schedule regardless of drift). On the 3-leg winner's window,
threshold 5pp fires 28 unique dates across 21.36 yrs vs
`monthly_sell`'s 256 — a 9× reduction in DARFs/yr at the cost of
0.11 Sharpe. Citation: `[advances_fin_ml, p.275-278]` (institutional
drift-triggered trading rules).

## 5. Edge cases

* **Single-leg portfolio** (`len(target_weights) == 1`): daily and
  monthly modes degenerate to buy-and-hold; drift ≡ 0 always; tax ≡
  0 (no sells needed); deposit still adds to equity. Validated by
  `tests/test_rebalance_modes.py::test_single_leg_degenerates`.
* **Zero returns** (`returns_df` all zeros): all modes produce
  `equity = initial_capital` throughout for daily/sell; cashflow
  adds deposits linearly.
* **Non-sorted index**: rejected at validation with `ValueError`.
* **Weights do not sum to 1**: rejected at validation.
* **Mismatched columns vs weight keys**: rejected at validation.

## 6. Performance

On the C3 window (6266 bars × 2 legs), the entire 3-mode sweep runs
in **~265 ms** on a modern laptop. No vectorization shortcuts are
taken in the monthly loops (there are only 298 months to iterate);
the daily loop is a single `cumprod` of the weighted returns. No
Numba / no Cython — pure NumPy + Pandas.

## 7. Known limitations & open questions

1. **Re-entry timing:** the rebal fires on the *last bar* of the
   closing month, but a broker implementing this would execute
   on the *first bar* of the new month (T+1 settlement). We ignore
   T+1 — a 1-day lag would likely reduce all three monthly-mode
   Sharpes by ~0.01-0.02 at most.
2. **Cash drag:** monthly_sell holds zero cash between rebal dates —
   every "sold" notional is immediately re-deployed. A real broker
   would have 1-2 days of settlement cash drag. Not modeled.
3. **Tax deferral / carryforward:** we pay tax on each month's
   realized gain in the same month. BR law allows loss carryforward
   for up to 5 years with specific declarations. Not modeled —
   conservative (overstates tax bill).
4. **Deposit timing vs drift snapshot:** the deposit is allocated
   based on the drift *at month-end*, but a real DCA script might
   auto-deposit mid-month (e.g. payday). The drift snapshot rule is
   the cleanest proxy for a BR swing-broker user running a monthly
   rebalance Sunday-night script.

## 8. Citations

* Baseline daily EW reset: `[advances_fin_ml, p.298-299]` (ch.16,
  HRP motivation — EW is the Σ-estimation-error-immune baseline).
* DR (diversification ratio) formula: `[advances_fin_ml, p.310]`
  (used in Task A's DR=1.121 fail, not directly in this module).
* Drift vs tax tradeoff framing: `[leverage_for_the_long_run, p.17,
  Table 8]`.
* BR 15% IR on realized gains: Investment Mandate §4.

## 9. Related artefacts

* **Module:** `src/market_lab/backtest/metrics/rebalance_modes.py`
  (4 functions).
* **Tests:** `tests/test_rebalance_modes.py` (**39 cases**, pytest
  baseline 670 → 698 → 709 across C1 + C4).
* **Comparison reports:** `comparison_3leg.md` (C2),
  `comparison_2leg.md` (C3), `threshold_sweep.md` (C4).
* **Sub-index:** `README.md` (this directory).
