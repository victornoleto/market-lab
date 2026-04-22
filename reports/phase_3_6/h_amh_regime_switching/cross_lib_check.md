# Cross-lib concordance — Family H AMH regime-switching

- Winner cell: **n_states=2, feature_set=sigma, rebalance_cadence_days=21, no costs/tax (isolated mechanics)**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **+14.080%**
- Hand-rolled (pure-pandas, replayed from regime_labels) OOS CAGR: **+14.080%**
- |Δ|: **0.000pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

The hand-rolled path replays the exact same regime labels
produced by the canonical HMM fit — it isolates the
weight/allocation/rebalance-cadence mechanics from the HMM
fitting logic. Any Δ > 0 would indicate a bug in the weight
shifting or cadence alignment. The HMM fitting itself is not
independently replicated (no hmmlearn in .venv) — this gate
therefore verifies the allocation pipeline, not the HMM.
The Family verdict (FAIL) is dominated by OOS Sharpe/CAGR
undercut, not by mechanics.
