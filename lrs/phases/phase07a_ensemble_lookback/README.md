# Phase 7A — Ensemble Multi-Lookback Fractional Position (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Round order note:** the Phase 7 round executes 7A → 7B → 7C → 7D → 7E →
> (7F conditional) → Phase 8. Phases 7A–7E are independent.

## Question

Phase 4's binding gate is G3 walk-forward (SPY 12/17, QQQ 6-7/11 vs the ≥75%
bar), and Phase 6C showed 90.9% of the failing windows are bull windows plus
`bear_mid` whipsaw. Phase 3C established that no *single* window beats 200 and
that 200 sits on a narrow peak, not a robust plateau — i.e. part of the WF
dispersion is timing luck of one specification. The untested, citable family is
the **combined forecast**: run N copies of the same SMA-level rule at different
speeds and hold the *average* of their states as a fractional position
`[systematic_trading, p.118-119, p.129-133]`. The paper itself reports that all
tested MA windows carry similar Sharpe (0.58–0.68), which justifies equal
weighting instead of fitted forecast weights `[leverage_for_the_long_run, p.14,
Table 6]`. Hypothesis under test: averaging reduces whipsaw and window-luck and
improves **walk-forward consistency** without giving up headline CAGR.

This is NOT a rerun of Phase 3C (which tested single windows in isolation,
argmax-style) and NOT an AND-filter (Phase 3A's failure mode): the members are
combined by averaging (OR-fractional), so a member disagreement scales exposure
instead of vetoing it `[trading_systems_methods, p.939]`.

## Mechanism (one family — fractional ensemble replaces the binary SMA gate)

- `f_t = (1/N) · Σ_w 1[P.shift(1) > SMA_w.shift(1)]` over a pre-registered
  window set (helper `lrs/lib/indicators.sma_ensemble_fraction`; each member
  uses the exact `build_sma_signal` convention, warmup → 0).
- Binary vol gate of the base kept verbatim: effective fraction
  `g_t = f_t · vol_gate_t`.
- Daily desired weights: `g_t · risk_on_ladder(L_base) + (1 − g_t) · risk_off`.
- Weekly cadence, lag-through-CASHX convention, `AnnualDarfEngine` tax, ladder
  weights and risk-off sleeves all unchanged from the Phase 2/4 bases.

## Pre-registered grid — 72 rows (+72 to the n_trials ledger → 4005 + 72 = 4077)

| Axis | Values | Anchor |
|---|---|---|
| Bases | the 6 Phase 4 bases (3 SPY + 3 QQQ, geometry verbatim) | Phase 2/4 |
| Window set | `S_narrow = {150,175,200,225}`; `S_wide = {100,150,200,250,300}` | narrow = Phase 3C adequate region; wide = speed-spaced set where the long member is diluted to 1/5 `[systematic_trading, p.118-119]`, `[leverage_for_the_long_run, p.14, Table 6]` |
| lag | `0..5` | restart convention |

Plus 6 non-trial baseline rows: each binary base at its committed best-score
lag, recomputed in-run for exact comparability.

**Built-in sanity (non-trial):** the degenerate set `{200}` at the headline
base/lag must reproduce the Phase 4 binary base byte-for-byte (max abs diff
reported in the REPORT).

## Pre-registered screen (per branch, on the best trial row by WF beats, tie-break Calmar)

1. WF beat count **strictly greater** than the best binary baseline of the
   branch (SPY > 12/17, QQQ > 7/11), on the exact Phase 4 splits
   (`is=1764 / oos=756 / step=756`). (The actual G3 gate level ≥13/17 and
   ≥9/11 is reported, not claimed.)
2. After-tax CAGR ≥ branch headline − 1pp.
3. MDD ≥ −50% (round constraint).

All three → diagnostic SUCCESS (feeds the 7F composition slot). Any miss →
honest FAIL recorded. Either way: no deployment, no paper-trade label, no
mandate change `[advances_fin_ml, p.208-211]`.

## Outputs

`lrs/results/phase07a_ensemble_lookback.csv`, `REPORT.md`, plots (fraction
series of best rows, equity/DD vs binary baseline, WF beats comparison,
CAGR×MDD frontier), `tests/test_lrs_phase07a.py`.
