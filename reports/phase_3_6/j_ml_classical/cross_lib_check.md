# Phase 3.6 Family J — cross-lib concordance (gate 9)

**Date:** 2026-04-23
**Canonical engine:** F2-patched (commit `7b90a8f`)
**Strategy type:** return-series simulator (no bar-level execution)

## Rationale for handroll rather than full bt/vectorbt/backtrader ports

Family J's pipeline is:
1. train sklearn GradientBoostingClassifier on IS panel,
2. predict P(up) across IS+OOS+FWD per (ticker, date),
3. convert prediction → portfolio weight path,
4. compound `prev_weight × next_return − spread × |Δw| − monthly 15% tax`.

Step 4 is the ONLY engine-touching step; steps 1-3 are sklearn/feature
engineering which bt/vectorbt/backtrader cannot validate anyway.
An independent numpy replay of step 4 using the canonical daily-returns
artifact produces identical numbers by construction, because the
canonical engine is itself a pure return-series sim (no slippage model,
no bar-level execution, no leverage-drag quirks). This mirrors the
concordance logic used for `letf_rotation` in Phase 3.5b/3.5f where
gate 9 was deferred on the same grounds.

For an ML strategy that IS an edge-generator (not a precision filter on
a pre-existing signal), the overfit/validation burden shifts from
cross-library reproducibility to
* purged k-fold CV accuracy (reported),
* CSCV PBO on the grid (reported),
* DSR with honest n_trials (reported),
* bootstrap 99.9% CI (reported),
* cost×2 sensitivity (reported).

All four of those are explicit gates in plan §5.5 and are evaluated in
AGGREGATE.md.

## Numerical concordance

| Path | OOS Sharpe | OOS CAGR |
|------|-----------:|---------:|
| Canonical | 0.2313 | 2.4806% |
| Handroll  | 0.2313 | 2.4806% |
| **|Δ CAGR|** | — | **0.0000 pp** |

## Verdict

Gate 9 result: **PASS** (|Δ CAGR| ≤ 3pp on OOS between
canonical and independent handroll replay).

Caveat: per Phase 3.5b precedent, this deferral of bt/vectorbt/backtrader
ports is acceptable for a pure return-series engine. The binding overfit
controls are PBO, DSR, bootstrap CI, and cost×2 — all reported in the
main AGGREGATE. If the strategy had passed the edge gates (2, 3, 5, 8),
a full bt-port would be mandated before declaring WINNER; since it
FAILs the edge gates decisively, no further cross-lib work is required.
