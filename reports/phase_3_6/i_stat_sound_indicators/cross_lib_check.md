# Phase 3.6 Family I — cross-lib concordance check

**Date:** 2026-04-23  |  **Verdict upstream:** FAIL-structural (0 survivors)

## Method

Family I is a pure return-series strategy (0 survivor(s) / 8 candidates). For Families A-C (FAIL verdicts), the cross-lib protocol collapses to confirming that canonical daily returns equal `(prev_weight × ret).sum(axis=1)` — an arithmetic identity given the clean return-series engine pattern (see `letf_rotation.py`, `[advances_fin_ml, p.31-34]`). A full 3-library replication (bt + vectorbt + backtrader) is reserved for strategies that clear the edge gates.

## Verdict on gate 9

**DEFERRED / NOT EVALUATED** — 0 indicators survived the Bonferroni-corrected MCPT screen at p<0.001, so no ensemble exists to cross-lib reconcile. Under plan §5 gate 9, cross-lib is mandatory only on winner candidacies; a **structural FAIL at the screening layer** (upstream of any engine arithmetic) cannot be cured by cross-lib replication, and we document the gate as non-applicable.

## Why a cross-lib run would not change the verdict

The FAIL is **upstream of any engine** — it happens at the statistical screening layer, before a trading simulation runs. The verdict says: even if we assume the best-possible engine arithmetic, the candidate indicators do not carry p<0.001 (Bonferroni) edge on the 5-ETF universe over IS 2004-2017. Cross-lib replication tests engine purity, not statistical significance.

## Citations

- Clean return-series engine pattern: `letf_rotation.py` docstring + `[advances_fin_ml, p.31-34]` (lookahead-bias timing).
- Plan §5 gate 9 mandate for winner-only cross-lib: `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`.
