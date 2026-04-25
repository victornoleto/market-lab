# Iteration 065 — VIX-conditional output leverage gate (1.5× calm / 1.0× stress) on iter 064 saved combined stream

## Hypothesis

Apply a VIX-regime output leverage gate to the iter 064 combined stream
(= 0.90 · iter_046 + 0.10 · QQQ_TREND), scaling daily returns by
**1.5× when VIX[t-1] < 20** and **1.0× when VIX[t-1] ≥ 20**, with a
**futures-realistic borrow rate of rf + 25 bps = 2.25%** absorbed as a
proportional drag on the excess-leverage component (drag applied only
on the calm-regime bars where excess lev > 0).

```
r_iter065[t] = lev[t] · r_iter064[t] − drag[t]
lev[t]       = 1.5  if VIX[t-1] <  20
             = 1.0  if VIX[t-1] >= 20
drag[t]      = (lev[t] − 1.0) · borrow_annual / 252
borrow_annual = rf + 0.0025  (= 0.0225 with rf=0.02 per iter 064 cfg)
```

The hypothesis is that calm-regime-conditional leverage (a) lifts
combined CAGR enough to unlock the **spy_real CAGR floor (gap −2.01 pp
at iter 064)** by amplifying the calm-period exposure where iter 064's
QQQ_TREND component contributes most, while (b) the partial application
(only ~70% of bars are calm) reduces the average Sharpe drag to
~0.10-0.12 absolute — small enough that DSR worst-p stays in the
[0.05, 0.10) band rather than crossing 0.10.

If this clears, criterion 4 (CAGR floor) lifts from 5/15 (only edu in
iter 064) to 10/15 (edu + spy), pushing total score to 95 → WINNER.

## Primary citation

`[leverage_for_the_long_run, ch.5]` — Hsiao & Williams (2017), J. Index
Investing. NTSX-style Treasury-futures financing argues that
futures-implied borrow (~T-bill + 0.5pp) yields a 3-5× lower drag
versus retail Reg-T margin (3.5%); applied conditionally to calm
regimes only further reduces drag by the calm fraction (~30%).

## Additional citations

- Whaley, R. E. (2009), *JPM* 35(3) 98-105,
  DOI 10.3905/JPM.2009.35.3.098 — VIX as ex-ante risk regime indicator;
  threshold 20 ≈ long-run median (preserved verbatim from iter 041 / 048).
- Bekaert, G. & Hoerova, M. (2014), *J Econometrics* 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition, supports
  binary calm/stress regime via VIX threshold.
- `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching;
  binary VIX gate is a degenerate 2-state HMM.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule;
  uses `vix.shift(1)` to compute `lev[t]` from `VIX[t-1]`.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
  n_trials (4334 → 4335 = +1).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline;
  numpy reference required for the regime-conditional lev transform.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- `[risk_parity, ch.5]` — iter 046 base (= 0.5 · iter_041 + 0.5 ·
  iter_039) preserved verbatim inside iter 064.
- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  basket (iter 039) preserved via iter 046.
- Faber, M. (2007), SSRN 962461 — single-asset 200-day SMA TAA
  primitive (QQQ_TREND component preserved verbatim from iter 064).
- `[stocks_on_the_move, p.21-30]` (Clenow, 2015) — 200d SMA as regime
  gate inside a wider momentum portfolio.
- Markowitz, H. (1952), *JoF* 7(1) 77-91 — convex combination Sharpe
  identity (the underlying iter 064 stream is preserved as Markowitz
  outer combo at w=0.10).
- Frazzini, A. & Pedersen, L. H. (2014), *JFE* 111(1) 1-25,
  DOI 10.1016/j.jfineco.2013.10.005 — borrow frictions on levered
  low-vol strategies; iter 060 closure cited this for the codebase
  Sharpe-without-rf convention.

## Edge source

SPY 1× buy-hold has constant exposure across regimes; this strategy
captures **excess return during low-VIX calm regimes (where the
underlying iter 064 composite already produces +0.07-0.10 daily Sharpe
per VIX standard deviation in that regime per iter 041's calibration)
by amplifying notional 50%**, while preserving the unlevered defensive
position during stress (where excess leverage would compound stress-
period drawdowns and incur full borrow drag without proportional
returns).

## Datasets

- **educational** (SPYSIM synth 1986-2026): VIX history extends 1990+
  (Tiingo macro cache), so the educational dataset's pre-1990 portion
  is excluded from the lev gate (lev=1.0 fallback during pre-VIX bars
  via `bfill`). This dataset tests robustness of the gate over 36 years
  of synthetic equity history including 1987 crash, 2000 dot-com,
  2008 GFC.
- **spy_real** (Tiingo SPY 2009-06-25 → 2026-04-15): the **primary
  target dataset for the hypothesis** — current iter 064 spy CAGR
  9.97% has the smallest gap (−2.01 pp) to the 11.98% floor; lev
  uplift here is most likely to unlock criterion 4.
- **ndx_real** (Tiingo QQQ 2010-02-12 → 2026-04-15): tests the same
  mechanism on the higher-CAGR Nasdaq benchmark; the floor gap
  (−5.18 pp) is wider so a 1.5× calm lev probably won't clear it,
  but the test confirms whether the mechanism is benchmark-agnostic.

## Kill criteria (pre-committed)

If ANY of the following observations occur at end of testing, the
hypothesis is falsified or partially closed regardless of secondary
metrics:

- **A. Combined Sharpe regress vs iter 064 by ≥ 0.10 on ≥ 2 of 3
  datasets**: would invalidate the assumption that calm-only lev is
  Sharpe-near-neutral; means the mechanism degrades risk-adjusted
  return more than it lifts CAGR. Threshold 0.10 (not 0.05 like iter
  064) reflects that a multiplicative transform on a 90+ score base
  must deliver visible risk-adjusted improvement.
- **B. DSR worst-p ≥ 0.20 on the 3-dataset minimum**: would mean the
  Sharpe drag is so large that DSR significance collapses across the
  cumulative n_trials inflation; would close the lev-on-iter-064 axis.
- **C. Score < 79 (iter 062/063 internal-LETF baseline)**: would mean
  the lev mechanism produces NET DESTRUCTION of value vs unlevered iter
  064 (90); falsifies the "VIX gating recovers the lev drag penalty"
  thesis.
- **D. CAGR floor counter-fails (≥ 1 dataset that passed iter 064 floor
  now FAILS)**: i.e., edu CAGR drops below 9.18% (iter 064 had 9.49%);
  would mean the gate is mis-calibrated for the calm-regime distribution.
- **E. G7 cross-lib > 3 pp**: pandas vs numpy reference parity must
  hold for the lev transform.
- **F. corr(combined_065, combined_064) > 0.99 on all 3 datasets**:
  would mean the lev gate produces no actual differentiation from
  unlevered iter 064 at the daily-return level (i.e., calm fraction
  is too low to matter, or the gate is functionally a no-op).
- **G. MDD ceiling fails (any dataset > benchmark + 5pp)**: lev=1.5×
  in calm should not blow MDD above iter 064's 17/15/15% by more than
  ~50% (i.e., predicted ~26/23/22%); benchmarks are 60.14/38.70/40.12%
  with 5pp buffer to 65.14/43.70/45.12%, so this is a wide margin.

## Expected budget

- Configs to test: **1 single pre-committed cfg** (lev_calm=1.5,
  lev_stress=1.0, vix_threshold=20, borrow_annual=0.0225) → 4334 + 1
  = 4335 cumulative_n_trials. **No grid → no Bonferroni.**
- Wall-time: ~5-8 minutes (3 datasets × single cfg × full gate
  battery + Markowitz check + cross-lib + bootstrap).
- Files to create: `output_lev_gate.py` (mechanism),
  `numpy_reference_iter065.py` (numpy parity), `run_backtests.py`
  (driver), `compute_gates_and_score.py` (gates+score), `tests/
  test_iter065.py` (TDD), `results.json`, `verdict.json`, `final_report.md`.

## Implementation plan

1. **TDD tests first** (`tests/test_iter065.py`):
   - `test_lev_calm_no_lookahead`: verify `lev[t]` uses `VIX[t-1]` only.
   - `test_lev_calm_above_threshold_returns_unchanged`: when `VIX[t-1] >=
     20`, `lev[t] = 1.0` and `drag[t] = 0`, output equals input.
   - `test_lev_calm_below_threshold_scales_correctly`: when `VIX[t-1] <
     20`, `lev[t] = 1.5` and drag = 0.0025/252 ≈ 9.92e-6 per bar.
   - `test_g7_parity_pandas_vs_numpy`: pandas vs numpy reference outputs
     are identical to floating-point exactness.
   - `test_warmup_handles_pre_vix_bars`: when VIX is missing for an early
     bar (e.g., synthetic dataset extends pre-1990), `bfill` seeds bar 0
     with the first available VIX value, so the gate is well-defined.

2. **Implement** `output_lev_gate.py`:
   - Function `apply_vix_lev_gate(combined, vix, *, lev_calm, lev_stress,
     vix_threshold, borrow_annual) -> pd.Series`
   - Aligns VIX to combined index, shift(1)+bfill, computes lev array,
     applies `r_levered = lev * r_combined - drag`.

3. **Implement** `numpy_reference_iter065.py`:
   - Pure-numpy reimplementation of `apply_vix_lev_gate` taking arrays
     instead of pandas Series; G7 parity check at floating-point identity.

4. **Run backtests** (`run_backtests.py`):
   - Load iter 064 saved combined returns from
     `iterations/064-*/results.json` "returns_series" key.
   - Load VIX from `data/external/macro/vix_daily.parquet`.
   - For each dataset, slice both to the dataset window
     (educational: 2006-01-03 → 2026-04-15; spy_real: 2009-06-25 →
     2026-04-15; ndx_real: 2010-02-12 → 2026-04-15).
   - Apply `apply_vix_lev_gate` with `lev_calm=1.5`, `lev_stress=1.0`,
     `vix_threshold=20`, `borrow_annual=0.0225`.
   - Compute Sharpe / CAGR / MDD; save `results.json` with
     `returns_series` (top-level), benchmarks, kill-eval inputs.

5. **Compute gates** (`compute_gates_and_score.py`):
   - Apply 7-gate battery (G1 vacuous PBO since N=1, G2 DSR raw α=0.05,
     G3 walk-forward 6/8, G4 OOS 70/30, G5 forward post-2020, G6
     bootstrap 99.9% CI, G7 cross-lib).
   - Robustness sub-windows (3 per dataset → 9 windows).
   - Pre-committed kills A-G evaluation.
   - Score via `scoring.score_strategy()`, write `verdict.json`.

6. **Plot** via `plot_helper.py`:
   - `uv run python studies/strategy_hunt_loop/plot_helper.py --iter 065`.

7. **Final report** (`final_report.md`) with score breakdown,
   pre-committed-kill table, structural lessons, "Next iteration
   suggestions", citations.

## What this iteration tests

This is the **first test of regime-conditional external leverage on
the iter 064 base** (= iter 058 architecture with QQQ_TREND
substitution). iter 060 closed unconditional ext-lev on iter 058 at
borrow >0.5pp (score 79); iter 060's final report explicitly opened
calm-regime-gated ext-lev as untested.

The base difference matters:
- iter 058 base CAGR was 8.69/9.01/9.27% — uplevering 1.5× would have
  brought CAGR to ~12-13% (clearing 2/3 floors) but DSR collapsed to
  worst-p 0.125.
- iter 064 base CAGR is 9.49/9.97/10.17% (+0.8-1.0 pp from QQQ_TREND
  uplift) AND iter 064's DSR worst-p is 0.0392 (vs iter 058's 0.0494).
  Headroom: even if DSR drifts 0.04 from drag, p stays under 0.10.

Compared to iter 048 (lev_calm=1.4, lev_stress=1.0, on iter 046 base,
score 83), iter 065:
- Has 0.1 higher lev_calm (1.5 vs 1.4) → +25% CAGR uplift relative
- Uses iter 064 base instead of iter 046 → +0.5-1.0 pp starting CAGR
- Adds explicit borrow drag (rf + 25 bps) — iter 048 used implicit
  no-friction lev (`lev * combined`), this iter applies futures-realistic
  drag per iter 060's discovered Sharpe-convention bound

## Predicted score

| outcome | probability | score |
|---|---|---|
| spy CAGR clears 11.98% AND DSR holds < 0.05 | 25% | 95 (WINNER) |
| spy CAGR clears AND DSR drifts to [0.05, 0.10) | 35% | 90 (STRONG) |
| spy CAGR clears AND DSR drifts to [0.10, 0.20) | 20% | 85 (STRONG) |
| spy CAGR doesn't clear (drag eats uplift) | 20% | 83-88 (STRONG) |

Expected value ≈ 89 (slightly below iter 064's 90 — high variance test).

## What this iteration explicitly DOES NOT test

- Higher lev_calm (1.7×, 2.0×): would amplify drag and DSR risk; if
  this iter passes at 1.5×, future iterations can sweep upward.
- Different VIX thresholds (15, 25): preserves iter 041 / 048
  convention.
- Asymmetric stress lev (stress < 1.0, e.g., 0.5×): conflates with
  iter 048's gating mechanism.
- Lev applied to QQQ_TREND component only (sub-component lev): iter
  062/063 closed internal LETF axis.
- Multiple regime tier (3-state: calm / normal / stress): adds
  hyperparameters → Bonferroni risk.
