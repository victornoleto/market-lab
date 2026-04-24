# Top crash-protected candidate — deep dive

> **`EMA_N150_th5_bL3_sL0` + `sl30_rec10_cape05`** — the best crash-protected variant on the educational top-1 base inside the ΔCAGR ≥ −5 pp corridor. Data window: **1986-01-03→2026-04-17**.

> ⚠️ **Educational only.** This config passes 6/7 gates in the 40 y synth but **3/7 in spy_real** — it does **not** meet spec §0 cross-dataset validation. Mandate §1 MAINTENANCE continues.

## Configuration

| component | value |
|---|---|
| MA filter | EMA |
| lookback | 150 bars |
| threshold | ±5% |
| buy leg | 3× long synth UPRO |
| sell leg | cash (`0`) |
| stop-loss | 30% drawdown from peak |
| re-entry | `recovery_trigger` at +10% off local bottom |
| risk indicator | **`cape`** (Shiller CAPE z-score sigmoid) |
| λ de-lever | 0.5 |
| fee | 0.95%/yr |
| switch cost | 15 bps |


Citations: synth LETF formula `[leverage_for_the_long_run, p.16, fn.22]`; regime filter `[leverage_for_the_long_run, p.13]`; CAPE framing Campbell & Shiller 1988; sigmoid threshold anti-2010s-over-delevering spec §8.3; recovery-trigger mode spec §3.1.

## Headline metrics

| metric | Candidate (stop + CAPE) | Baseline (no overlay) | SPY buy-hold |
|---|---|---|---|
| CAGR | +24.01% | +27.67% | +11.47% |
| Sharpe | 0.87 | 0.84 | 0.68 |
| Sortino | 1.22 | 1.18 | 0.96 |
| MDD | +44.55% | +53.98% | +55.14% |
| Calmar | 0.54 | 0.51 | 0.21 |
| Volatility | +30.15% | +37.35% | +18.46% |
| Final equity (start=1.0) | 5806.45× | 18738.55× | 79.36× |

### Deltas (Candidate minus ...)

| metric | vs Baseline (3x no overlay) | vs SPY buy-hold |
|---|---|---|
| ΔCAGR | -3.66% | +12.54% |
| ΔSharpe | 0.02 | 0.18 |
| ΔMDD (magnitude) | +9.43% (smaller = better) | +10.59% |
| ΔCalmar | 0.03 | 0.33 |
| Final equity (start=1) | 5806.45× vs 18738.55× baseline | vs 79.36× SPY |


## Stop events

**9 stops fired** over 1986-01-03→2026-04-17. Every event tracked below — see `stop_events.csv` for full detail.

| # | stop date | re-entry | bars stopped | equity at stop | peak before | DD at stop |
|---|---|---|---|---|---|---|
| 1 | 1987-10-15 | 1987-10-21 | 4 | 1.79 | 2.59 | -31.13% |
| 2 | 1990-08-21 | 1990-12-03 | 72 | 3.12 | 4.71 | -33.66% |
| 3 | 2008-01-08 | 2008-05-01 | 79 | 212.70 | 307.15 | -30.75% |
| 4 | 2010-05-20 | 2010-08-02 | 50 | 298.88 | 441.98 | -32.38% |
| 5 | 2011-08-04 | 2011-10-14 | 50 | 329.15 | 480.73 | -31.53% |
| 6 | 2016-06-27 | 2016-11-17 | 101 | 923.85 | 1354.17 | -31.78% |
| 7 | 2020-03-09 | 2020-03-25 | 12 | 1257.14 | 1917.43 | -34.44% |
| 8 | 2023-03-01 | 2023-06-02 | 65 | 1979.77 | 2853.07 | -30.61% |
| 9 | 2025-04-03 | 2025-04-09 | 4 | 3580.28 | 5206.67 | -31.24% |

## De-leveraging activity (CAPE signal)

- **% of long-regime days with de-lever active (pos < 1.0)**: 73.3%
- **% of long-regime days with deep de-lever (pos < 0.5)**: 2.2%
- CAPE z-score crosses +1σ when valuation is ≥ 1 standard deviation above its 10-year rolling mean — historically periods like late 1990s, late 2010s, and 2020-2022.


## Per-crash comparison

Drawdown and total return during each major crash window. `cand_MDD` vs `base_MDD` shows how much MDD the overlay saved;`cand_total_return` vs `bench` shows whether the candidate beat buy-hold through the crash.

| crash | window | cand MDD | base MDD | bench MDD | cand total | base total | bench total | stops in window |
|---|---|---|---|---|---|---|---|---|
| 1987_black_monday | 1987-08-01 → 1988-06-30 | +35.23% | +45.21% | +32.89% | -18.78% | -31.30% | -11.15% | 1 |
| 2000_dotcom | 2000-03-01 → 2003-12-31 | +23.31% | +37.24% | +47.38% | +57.79% | +48.34% | -14.75% | 0 |
| 2008_gfc | 2007-10-01 → 2010-06-30 | +44.55% | +44.99% | +55.14% | +1.18% | -6.52% | -28.73% | 2 |
| 2020_covid | 2020-01-01 → 2020-09-30 | +39.75% | +53.98% | +33.69% | -13.05% | -28.97% | +4.67% | 1 |
| 2022_bear | 2022-01-01 → 2023-01-31 | +18.45% | +32.44% | +24.44% | -18.45% | -32.44% | -13.44% | 0 |

Per-crash plots: `crash_1987_black_monday.png`, `crash_2000_dotcom.png`, `crash_2008_gfc.png`, `crash_2020_covid.png`, `crash_2022_bear.png`.


## Plots

- **`equity_vs_benchmarks.png`** — candidate + baseline + SPY (log scale).
- **`drawdown.png`** — running drawdown of all three series with stop markers.
- **`risk_signal_trace.png`** — CAPE raw → z-score → risk → effective position.
- **`crash_<label>.png`** — normalized equity during each crash window.


## Strengths (40y synth only)

On the 40-year synthetic window, the candidate actually beats SPY buy-hold on **every** headline metric:

* CAGR: 24.01% vs SPY 11.47% (**+12.54 pp**).
* Sharpe: 0.87 vs SPY 0.68 (**+0.18**).
* MDD: 44.55% vs SPY 55.14% (**better by 10.59 pp**).
* Calmar: 0.54 vs SPY 0.21.
* Final equity (1986→2026): 5806× vs SPY 79×.


Vs the no-overlay baseline (3x UPRO synth): the overlay sacrifices 3.66 pp CAGR to recover 9.43 pp of MDD — a decent trade-off, but insufficient to clear the spec target of MDD ≤ 40 %.


## Honest verdict — why this doesn't ship

Despite beating SPY on every 40y metric, this candidate is **not deployable**:

1. **MDD still 4.5 pp above the 40 % spec target.** 44.55 % is a career-ending drawdown for a retail portfolio; the spec chose 40 % as the *weakest* acceptable threshold precisely because larger drawdowns cause behavioural abandonment.
2. **G3 Walk-Forward fails universally** (MDD < 25 % per 6-month OOS window is violated in every split). The 40y aggregate MDD is only 44.55 % because good years mask bad ones; inside a single WF window the overlay cannot prevent the crash from producing a ≥ 25 % window-local drawdown.
3. **SPY real data (17 y) gives only 3/7 gates** for this same parameter set. Real-data MDD reaches levels the synth path dampens (Gayed `[p.21, Table 12]`). The 40y synth number is an upper bound on what real data would deliver.
4. **CAPE is stale at 2023-09** (Shiller cutoff). For a live 2024-2026 deployment there's no risk signal — the overlay degrades to stop-only.
5. **CAPE chronic-high decade (2010s)**: realized spec §8.3 warning — signal spends 73 % of bull-regime bars de-levering but only 2.2 % deeply de-levered. In a quiet decade this leaks CAGR without saving MDD, because the crash never comes.


**Why this config doesn't ship**:
1. MDD 44.55% is still **4.5 pp above the 40 % spec target** despite the overlay.
2. G3 Walk-Forward fails universally (MDD < 25 % per 6-month OOS window is violated).
3. In SPY real data the equivalent config reproduces only 3/7 gates — not portable.
4. CAPE z-score collapses in the 2010s because CAPE was chronically high for a decade without a crash (spec §8.3 warning realized).


**Reference**: full Phase 3 verdict in `../phase3_FINAL.md`; cross-dataset gate matrix in `../phase3/cross_dataset_gates.md`.
