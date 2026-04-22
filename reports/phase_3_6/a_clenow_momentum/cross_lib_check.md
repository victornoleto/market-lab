# Cross-lib concordance — deferred (verdict already FAIL)

**Gate 9:** 2/3 of {bt, vectorbt, backtrader} within ±3pp CAGR on OOS.

**Status:** DEFERRED.

**Rationale:** This strategy's OOS CAGR is 2.67% (FAIL gate 3 CDI floor
13%) and OOS Sharpe is 0.25 (FAIL gate 2 threshold 1.5). Even if all
three independent libraries reproduced the same 2.67% CAGR exactly,
the verdict would remain FAIL. Running bt / vectorbt / backtrader on
a multi-asset panel cross-section (1165 stocks × 5105 bars × 5
configs) costs ~30 min compute and adds no information to the pass/
fail verdict because the OOS edge is already below CDI.

**If a future iteration of Family A passes gates 1-8, 11-13:** run
cross-lib per the phase 3.5f template (`scripts/run_phase3_5f_cross_lib.py`)
adapted to cross-sectional weights. Spec:
`docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`.

**Engine independence signal (proxy for gate 9):** the canonical
simulation uses `prev_weight × next_return` alignment (strictly
post-`7b90a8f`), no bar-engine, vectorized numpy rolling. Any clean
external library operating on the same close-panel + weights matrix
must produce the same gross CAGR by linear arithmetic. The per-config
sanity check in `config_grid.csv` shows consistent Sharpe structure
(0.18-0.49 full-period across 5 configs) with no anomalous outliers
suggesting a wrong alignment.

## Citations

- `[advances_fin_ml, p.31-34]` — two-stage replication protocol.
- `[advances_fin_ml, ch.11]` — walk-forward + engine robustness.
