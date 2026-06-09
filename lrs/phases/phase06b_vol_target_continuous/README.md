# Phase 6B — Continuous Vol-Targeting (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Run order note:** the Phase 6 round executes 6C → 6B → 6D → 6A.

## Question

Phase 2 expressed volatility control as a **binary** gate (`RV <= threshold` →
full ladder leverage, else risk-off). Phase 4 then failed on walk-forward
consistency, and the Phase 6C forensics show the strategy bleeding in `bear_mid`
windows (whipsaw without a deep crash) and paying its timing premium in bull
windows. The one citable mechanism family not yet tested in this restart is
**continuous vol-targeted sizing**: scale the risk-on sleeve exposure as
`L_t = clip(σ_target / RV_t, 0, L_max)` so exposure shrinks smoothly as realized
vol rises, instead of toggling `[systematic_trading, p.137-148]`,
`[systematic_trading, p.159]`. The economic rationale is the same leverage-trap
reading the restart is built on: high realized vol degrades leveraged
compounding `[leverage_for_the_long_run, p.4-7]`. Hypothesis under test: smooth
sizing improves **walk-forward consistency** (the binding Phase 4 gate) without
giving up the headline CAGR.

## Mechanism (one family — sizing replaces the binary vol gate)

- The SMA200 weekly trend gate, risk-off sleeves, lag convention, weekly
  cadence, and `AnnualDarfEngine` tax are all unchanged from the headline bases.
- On risk-on days the ladder leverage is `L_t` instead of the fixed target;
  there is **no binary vol gate** in these rows (vol acts through sizing only).
- `L_t` raw value `σ_target / RV_t`, clipped to `[0, L_max]`.
- **Quantization + inertia:** holdings move only when the raw `L_t` deviates
  from the held level by ≥ `0.25`; the new held level is the raw value rounded
  to the `0.25` ladder grid. This is the position-inertia discipline that keeps
  turnover sane `[systematic_trading, p.174]`, and is operationally required
  here because every weekly target change routes through CASHX for `lag` days.
- For `1.0 ≤ L ≤ 3.0` the ladder reuses `phase04.target_leverage_weights`
  (mix of underlying / 2x / 3x). For `0 ≤ L < 1.0` the sleeve is
  `{underlying: L, CASHX: 1−L}` (deleveraged risk-on; cash is the un-invested
  remainder of the vol-target scalar `[systematic_trading, p.137-148]`).
- RV estimator identical to Phase 2: `returns.rolling(w).std(ddof=0).shift(1)
  · sqrt(252)` — no lookahead `[testing_tuning, p.327-335]`.

## Pre-registered grid — 72 rows (+72 to the n_trials ledger → 3948)

| Axis | Values | Anchor |
|---|---|---|
| Branch (headline geometry fixed) | SPY: `L_max 2.00`, off `50 ZROZ / 25 GLD / 25 CASH`; QQQ: `L_max 1.75`, off `40 ZROZ / 40 GLD / 20 IEF` | Phase 2/4 headline bases |
| `σ_target` | `20%, 30%, 40%` annualized | brackets the Phase 2 binary thresholds (30/40%) and Gayed's vol-trap zone `[leverage_for_the_long_run, p.4-7]` |
| RV window | `21, 63` | the two Phase 2 estimator windows |
| lag | `0..5` | restart convention |

Plus 2 non-trial baseline rows: the binary headline base per branch
(`spy_top` lag 3, `qqq_top` lag 0), recomputed in-run for exact comparability.

## Pre-registered screen (per branch, on the best row by WF beats, tie-break Calmar)

1. WF beat count **strictly greater** than the binary baseline (SPY > 12/17,
   QQQ > 6/11), on the exact Phase 4 splits (`is=1764 / oos=756 / step=756`).
   (The actual gate level would need ≥13/17 and ≥9/11 — reported, not claimed.)
2. After-tax CAGR ≥ headline − 1pp.
3. MDD ≥ −50% (user constraint for this round).

All three → diagnostic SUCCESS (a lead for Phase 6A's satellite set — still not
a gate pass, not a promotion). Any miss → honest FAIL, family stays closed.

## Outputs

`lrs/results/phase06b_vol_target_continuous.csv`, `REPORT.md`, plots
(L_t exposure series, equity/DD vs binary headline, WF beats comparison,
CAGR×MDD frontier), `tests/test_lrs_phase06b.py`.
