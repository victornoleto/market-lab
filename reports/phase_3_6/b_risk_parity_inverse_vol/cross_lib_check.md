# Phase 3.6 Family B — cross-lib concordance check

## Winner config
- slug: `N120_tvol15_rbd21`
- universe: ['SPY', 'TLT', 'GLD', 'EEM']
- vol_lookback: 120
- target_vol: 0.15

## Method

Since Family B is a **pure return-series strategy** (no bar-level engine, no `Portfolio`/`Order` machinery), an independent `(prev_weight × ret).sum(axis=1)` reconstruction IS the
vectorbt/backtrader analog — both libraries use the exact same arithmetic for weight-vector strategies. A full multi-lib reconciliation would be valuable if the strategy passed core edge gates; under FAIL we limit to the arithmetic sanity check.

## Results

- Canonical OOS CAGR (net FX + tax): **+1.311%**
- Independent OOS CAGR (gross, same weights × returns): **+4.683%**
- |Δ CAGR| = **3.372 pp** — the gap is the cost drag (FX spread + 15% BR tax), not an engine discrepancy.
- Daily-return correlation on non-rebal days: **1.000000**.

## Verdict on gate 9

**NOT EVALUATED** — Family B failed 8 of 13 core gates (see `AGGREGATE.md`). The cross-lib sanity check shows arithmetic consistency (corr ≈ 1 on non-rebal days) but is insufficient to upgrade the verdict. A full 3-library replication (bt + vectorbt + backtrader) is reserved for strategies that clear the edge-detection gates 1-8.

## Citations

- Clean return-series engine pattern: see `letf_rotation.py` docstring
  and `[advances_fin_ml, p.31-34]` (lookahead-bias timing).