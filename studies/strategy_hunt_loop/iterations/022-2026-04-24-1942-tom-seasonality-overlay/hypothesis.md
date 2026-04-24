# Iteration 022 — Turn-of-Month (TOM) seasonality overlay on iter 016 base

## Hypothesis

Iter 016's `ntsx_vm_vt15_L21_cap20` (fixed 60:40 SPY+IEF × Moreira-Muir
vol-target) saturates at Sharpe ~1.14-1.19 with DSR p=0.226 because
every overlay attempted so far (options long/short, ρ-regime, credit,
regional, momentum, EMA-T10Y3M) has been **algebraically absorbed by
σ²_port**. Iter 022 tests a **structurally different signal class** —
the turn-of-month (TOM) seasonality effect documented empirically since
Lakonishok & Smidt (1988) and mechanistically explained by Etula,
Rinne, Suominen & Vaittinen (2020, JF): institutional
liquidity-sensitive flows (pension rebalancing + Treasury auction
settlements) concentrate buying pressure at month-end, producing a
**conditional drift premium on TOM days that is orthogonal to realized
variance**. Unlike variance-overlay overlays, TOM is a calendar-timed
modulator of conditional E[R], not σ.

Modulation rule: eq_weight swings between 0.9 (TOM window: last 3 +
first 3 business days of each month) and 0.5 (mid-month); bd_weight
mirrors (0.1 TOM, 0.5 mid-month). The vol-target scale then computes
σ²_port[t-1] with w_eq[t]/w_bd[t] time-varying, and rescales the total
gross exposure bar-by-bar as in iter 016. Average eq_weight ≈ 0.617 —
preserves iter 016's 0.60 long-run equity tilt within 2 pp.

## Primary citation

`[trading_systems_methods, p.479-481]` — Kaufman catalogues the
turn-of-month, holiday, and Hirsch calendar-effect systems (buy Nov 1 /
sell Apr 30; buy 2 days before US holidays; TOM buy at T-3). Primary
anchor for calendar seasonality as a bona-fide systematic signal
separate from price/volatility signals.

## Additional citations

- `[trading_systems_methods, p.418]` — seasonal/calendar section: frames
  calendar effects as exogenous institutional-flow signals, not
  price-driven.
- `[risk_parity, p.10-11, ch.1]` — iter 016 base stack (fixed 60:40
  static weights with variance-target scaling).
- `[systematic_trading, p.40, ch.2]` — volatility standardisation
  primitive (inherited unchanged from iter 016).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline (no
  look-ahead in variance computation; TOM flag is known at t-1 since it
  is a calendar property of the next trading bar).
- Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling.

Web / papers:
- Lakonishok, J. & Smidt, S. (1988). "Are Seasonal Anomalies Real?
  A Ninety-Year Perspective." *Review of Financial Studies* 1(4),
  403-425. DOI: 10.1093/rfs/1.4.403. Original TOM empirical evidence
  1897-1986.
- Etula, E., Rinne, K., Suominen, M. & Vaittinen, L. (2020). "Dash for
  Cash: Monthly Liquidity Needs and the Cross-Section of Asset
  Returns." *Journal of Finance* 75(6), 3157-3203.
  DOI: 10.1111/jofi.12978. Institutional-flow mechanism; empirical
  persistence of TOM premium in post-crisis era.
- Kunkel, R.A., Compton, W.S. & Beyer, S. (2003). "The turn-of-the-month
  effect still lives: the international evidence." *International
  Review of Financial Analysis* 12(2), 207-221. Confirms persistence
  into 21st century across 19 countries.
- Ariel, R.A. (1987). "A Monthly Effect in Stock Returns." *Journal of
  Financial Economics* 18(1), 161-174. Seminal US evidence 1963-1981.

## Edge source

SPY 1x buy-hold receives **uniform, untilted daily exposure** — every
trading day earns equal allocation regardless of the conditional
expected return that day. The empirical TOM literature shows the
last-3 + first-3 business days of each month (~28% of trading days)
capture a structurally disproportionate share of monthly equity
returns due to institutional liquidity flows. A vol-managed stack that
**tilts equity allocation toward TOM days** concentrates exposure on
the conditionally-highest-E[R] subset of bars, extracting a premium
that is **orthogonal to σ²_port** because the signal is calendar-based,
not variance-based. This is the first iteration in the hunt loop to
test a non-price / non-variance exogenous signal.

## Datasets

- **educational (SPYSIM synth 40y, actually SPY+IEF 2006-2026 aligned
  with prior iters):** baseline sanity check on 20 years of real
  SPY+IEF with IEF inception constraint — TOM effect should manifest
  given overlap with Kunkel et al's post-2000 window.
- **spy_real (SPY+IEF 2009-06-25 → 2026-04-14):** primary test window;
  covers Etula et al's post-2000 empirical horizon + post-GFC regime.
- **ndx_real (QQQ+IEF 2010-02-12 → 2026-04-14):** TOM effect in NDX
  may be attenuated (tech-heavy, more retail flow) — this is the
  natural stress test dataset.

## Kill criteria (pre-committed)

1. **Kill #1 — TOM premium absent in data.** If standalone mean
   equity return on TOM days ≤ mean return on non-TOM days on ≥ 2 of
   3 datasets (i.e., the conditional-drift premium simply does not
   exist in the observed sample), the mechanism is falsified
   regardless of overlay metrics. This must be checked BEFORE running
   the full backtest — if it fails, the iter is aborted with that
   single finding.
2. **Kill #2 — No Sharpe advance over iter 016.** If Δ Sharpe vs iter
   016 ≤ 0.00 on ≥ 2 of 3 datasets, the overlay is Sharpe-neutral
   (same pathology as iter 020/021). Still would be a structural
   finding ("calendar overlays also absorbed") — FAIL rather than
   win, but informative.
3. **Kill #3 — DSR ceiling not penetrated.** If DSR worst p ≥ 0.20
   (i.e., no improvement over iter 016's 0.226), the overlay is not
   a winner candidate regardless of Sharpe gain — DSR remains the
   universal ceiling.
4. **Kill #4 — MDD regression.** If MDD > iter 016 + 5 pp on ≥ 2 of
   3 datasets, the overlay concentrates tail risk unacceptably.

Winner condition: all 5 strict conditions of
`WINNER_AND_RANKING.md` hold **AND** score ≥ 90.

## Expected budget

- Configs to test: **1** (single pre-committed cfg; no grid, no sweep).
- Cumulative n_trials advance: 4270 → 4271.
- Wall-time estimate: ~10 min (data load + 3 backtests + 7 gates × 3
  datasets + plotting).
- Files to create:
  - `tom_seasonality_overlay.py` — TOM-modulated static stack
    vol-managed primitive.
  - `numpy_reference_tom.py` — hand-rolled numpy parity check (G7).
  - `run_backtests.py` — 3-dataset runner (mirrors iter 016 structure).
  - `compute_gates_and_score.py` — 7-gate battery + scoring.
  - `tests/test_tom_seasonality_overlay.py` — TDD for the primitive.

## Implementation plan

1. **TDD first**: write `tests/test_tom_seasonality_overlay.py`
   covering: (a) TOM flag correctness (calendar logic on known
   month-boundary dates including Jan/Dec edge), (b) eq_weight
   modulation correctness (0.9 on TOM, 0.5 elsewhere), (c) vol-target
   identity preservation when TOM boost = 0 (must reproduce iter 016
   exactly), (d) σ̂_{t-1} lag preservation (no look-ahead from TOM
   flag timing), (e) G7 numpy-pure parity ≤ 3 pp CAGR.
2. Implement `apply_tom_static_stack_vm` in
   `tom_seasonality_overlay.py` as a thin wrapper over iter 016's
   `apply_static_stack_vol_managed`: time-varying w_eq[t]/w_bd[t]
   based on TOM flag, with the same σ̂_{t-1} machinery.
3. Implement `numpy_reference_tom.py` as a standalone numpy-only
   recomputation (for G7 parity).
4. Implement `run_backtests.py` mirroring iter 016's structure — same
   3 datasets (SPY+IEF educational/spy_real, QQQ+IEF ndx_real), same
   cost model (2 bps per leg), single pre-committed cfg.
5. **Early gate — Kill #1 check**: before running full backtest, log
   TOM-day vs non-TOM-day mean equity returns for all 3 datasets.
   If Kill #1 triggers, abort and document.
6. Run 3 backtests → `results.json`.
7. `compute_gates_and_score.py`: 7-gate battery per dataset with cumulative
   n_trials = 4271 (BASE_MEMORY 4270 + 1 this iter), then `scoring.py` →
   `verdict.json`.
8. `plot_helper.py --iter 022` → vs-benchmark PNGs.
9. Write `final_report.md` (honest verdict: WINNER / STRONG /
   PROMISING / MARGINAL / NEAR_FAIL / FAIL).
10. Update BASE_MEMORY + DEAD_ENDS per Stage 5 rules.

## Pre-committed config

```python
CFG = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20_tom_b90_m50",
    # iter 016 inheritance (unchanged)
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    "rebalance": "daily",
    "funding_cost_modeled": False,
    # TOM modulator (NEW)
    "tom_window_last_n": 3,   # last 3 business days of month
    "tom_window_first_n": 3,  # first 3 business days of month
    "eq_weight_tom": 0.9,     # equity tilt during TOM window
    "bd_weight_tom": 0.1,     # bond counterweight during TOM
    "eq_weight_mid": 0.5,     # equity during non-TOM
    "bd_weight_mid": 0.5,     # bond during non-TOM
}
```

Long-run average weight: ~0.617 equity / ~0.383 bonds — preserves iter
016's 60:40 long-run tilt within ~2 pp.
