# Iter 017 — Hypothesis: B.6 — VBRSIM regime-gated factor tilt

## Hypothesis (one paragraph)

iter 013 (constant-weight VBRSIM US small-cap value tilt) hit tier WINNER but
**failed substantively** because the value premium was dormant 2010-2024
("death of value"). However, iter 013 also revealed that VBRSIM's
performance was **regime-dependent** — strong in lh_56y (1970-2007 bull
value era), weak post-2008. This iter tests whether **a regime-conditional
weighting** of VBRSIM can recover the structural advantage iter 013 found
on lh_56y while avoiding the live-window drag. The signal: **factor
momentum (12-1 VBRSIM trailing return)** — VBRSIM weight = 25% if signal
positive, 0% (substituted by KMLM) if negative, monthly rebalance. The
hypothesis: a simple binary regime gate captures the value premium when
it's "live" and avoids it when dormant, recovering most of iter 013's
lh_56y Sharpe edge without the live-window cost.

## Primary citation

- `[advances_fin_ml, p.208-211]` — López de Prado: PBO discipline (key risk
  is "regime gate on existing winner" DSR-regression trap; pre-commit ≤ 3
  configs to mitigate).
- `[risk_parity, ch.2, p.37-41]` — Carlson: factor framework + regime
  awareness.
- `[stocks_on_the_move, p.21-30]` — Clenow: time-series momentum as factor
  selection signal.
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge source (1 sentence)

avg(SPY, VT) buy-hold misses **(a)** capital-efficient stacking (NTSX+GDE);
**(b)** crisis-alpha (KMLM); AND **(c)** value premium captured ONLY when
the regime favors it (factor momentum signal positive), avoided when
dormant.

## Datasets to test

- `lh_56y` — VBRSIM has a ~1972 inception in testfolio cache; effective
  window 1986+ via NTSX bottleneck (~40y eff).
- `vt_real` (2008-06+) — full data on all legs.
- `ndx_real` (2010-02+) — full data.

## Pre-committed kill criteria

**KILL #1 (regime gate doesn't work)**: If best-of-grid loses iter 011 on
≥ 2 of 3 datasets AND fails to match iter 013's +0.080 lh_56y advantage,
regime-gating doesn't recover the value factor. Closes B.6 entirely.

**KILL #2 (DSR-regression trap)**: If gate ON/OFF flips dominate the
Sharpe — i.e., the in-sample regime calibration is overfitting (PBO > 0.5
on all 3 datasets), the regime gate is a fitting artifact. Documented
risk; ≤3 configs is the mitigation.

## Configs (pre-committed grid — STRICT 3 configs to limit DSR penalty)

All weights sum to 100%. VBRSIM weight is regime-conditional via factor
momentum signal; weight goes 0% (KMLM substituted in) when signal off.

| config | NTSX | GDE | VBRSIM (when on) | KMLM | regime signal | rationale |
|---|---:|---:|---:|---:|---|---|
| `vbrsim_mom12_25_KMLM`  | 35% | 25% | 25% / 0% | 15% / 40% | VBRSIM 12-1 trailing return > 0 | momentum-on-momentum, simplest |
| `vbrsim_value_25_KMLM`  | 35% | 25% | 25% / 0% | 15% / 40% | VBRSIM trailing 36m Sharpe > 0.5 | medium-term performance gate |
| `vbrsim_dual_25_KMLM`   | 35% | 25% | 25% / 0% | 15% / 40% | (signal_1 OR signal_2) above | dual-signal robust |

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.
**N_CONFIGS = 3** → DSR n_trials = 3 (smaller penalty than 4).

## Implementation plan

Adapt iter 016 backtest.py. Key changes:
1. **Regime signal computation**: monthly compute VBRSIM 12-1m return AND
   36m Sharpe; produce binary mask per date.
2. **Dynamic weight expansion**: per date, if signal=ON use {35/25/25/15};
   if OFF use {35/25/0/40} (KMLM absorbs VBRSIM weight).
3. Configs differ in signal definition (vbrsim_mom12 / vbrsim_value /
   vbrsim_dual) but same weight skeleton.
4. Pipeline still uses gross_returns()/dropna() but weights vary by date —
   need a small per-date weighting helper.

This is the FIRST iter with **dynamic weights** (vs iter 011-016 all
static). Per-date weight expansion adds modest complexity but reuses all
gate / scoring / robustness logic. Pytest baseline (461 tests) unchanged.

## Expected budget

- Implementation: ~20 min (regime signal + dynamic weight expansion).
- Run wall-time: ~5-8 min.
- Plots + report: ~10 min.
- Total: ~40 min.

## Probability assessment (honest)

- **P(strict ADVANCE vs iter 011)**: ~15% — regime-gating is exactly the
  type of "fit-the-history" trap that DSR penalizes; 3 configs limits
  the multi-trial penalty but doesn't remove it.
- **P(positive signal but no ADVANCE)**: ~20% — likely if regime gate
  helps lh_56y modestly but live windows are short enough that the gate
  ON/OFF flips contaminate signal.
- **P(tier WINNER, no ADVANCE)**: ~20%.
- **P(STRONG, no winner conds)**: ~20%.
- **P(FAIL/kill fires)**: ~25% — DSR-regression trap is the dominant risk.

This iter has high diagnostic value because it tests whether B-direction
regime-gating is viable. If it fails, all of B is closed except B.5 (UMD
overlay, iter 016).
