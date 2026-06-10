# Phase 7F — Composition of the Round Winners (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Trigger:** the round pre-condition IS met — ≥2 SUCCESS among {7A, 7B, 7C,
> 7D}: 7A SPY (ensemble, WF 13/17) and 7D QQQ (quadratic vol-target, WF 8/11).

## Question

7A showed that averaging SMA window speeds lifts SPY's walk-forward; 7D showed
that inverse-variance sizing lifts QQQ's. The two mechanisms are orthogonal
(signal smoothing vs exposure sizing) and individually citable
`[systematic_trading, p.118-119, p.129-133]`, `[volatility_trading, p.135,
p.138-140]`. This phase tests their composition — and nothing else. Parameters
are FROZEN at the per-mechanism winners; only the lag is swept (restart
convention). No new parameter search `[advances_fin_ml, p.208-211]`.

## Mechanism (one family — composition, parameters frozen)

Daily desired weights: `f_t · ladder(L_t) + (1 − f_t) · risk_off`, where

- `f_t` = SMA ensemble fraction over the 7A-winning `narrow {150,175,200,225}`
  set (helper `sma_ensemble_fraction`, conventions verbatim);
- `L_t` = 7D quadratic vol-target scalar `clip(σ² / RV², 0, L_max)` with the
  7D-winning `σ = 40% / RV21`, 0.25-ladder + inertia verbatim;
- risk-off sleeve, weekly cadence, lag-through-CASHX, `AnnualDarfEngine`
  verbatim from the branch headline bases.

Two pre-registered variants:

1. `ens_x_quad` — as above (vol acts through sizing only; no binary vol gate).
2. `ens_x_quad_gated` — same, with the branch's binary headline vol gate
   additionally zeroing `f_t` (belt-and-suspenders variant).

## Pre-registered grid — 24 rows (+24 to the n_trials ledger → 4353 + 24 = 4377)

| Axis | Values |
|---|---|
| Branch | SPY (`L_max 2.00`, headline sleeve/gate), QQQ (`L_max 1.75`, headline sleeve/gate) |
| Variant | `ens_x_quad`, `ens_x_quad_gated` |
| lag | `0..5` |

**Built-in sanity (non-trial):** forcing `f_t ≡ 1` in `ens_x_quad` must
reproduce the 7D quadratic row (σ40/RV21, same lag) byte-for-byte (max abs
diff reported).

## Pre-registered screen (per branch, on the best trial row by WF beats, tie-break Calmar)

1. WF beat count **strictly greater** than the branch's best round result so
   far (SPY > 13/17 from 7A; QQQ > 8/11 from 7D).
2. After-tax CAGR ≥ branch headline − 1pp.
3. MDD ≥ −50% (round constraint).

All three → diagnostic SUCCESS. Any miss → honest FAIL (the 7A/7D winners
remain the round's survivors). Either way the round closes into the
consolidated decision table for the user's Phase 8 pick. No deployment, no
paper-trade label, no mandate change `[advances_fin_ml, p.208-211]`.

## Outputs

`lrs/results/phase07f_composition.csv`, `REPORT.md`, plots (exposure series
f_t·L_t, equity/DD vs 7A/7D winners, WF comparison, frontier),
`tests/test_lrs_phase07f.py`.
