# Gates §2.4 verdict — system 11504701 (PnL minus cost model)

Generated: 2026-05-01 (oos_cutoff=2025-12-01)

## Cost model (pips RT)
- Spreads: {'EURUSD': 0.13, 'GBPUSD': 0.5, 'USDCAD': 0.74, 'USDCHF': 0.75, 'EURGBP': 0.75, 'EURCHF': 1.2}
- Commission: 0.7 pips RT
- Total cost per trade range: 0.83 – 1.90 pips

## Full-period
- N trade days: 116
- N trades: 314
- Daily net pips mean: 9.93 | std: 25.91
- **Annualized Sharpe (full): 6.085**
- DSR p-value: 0.0000
- Bootstrap 99.9% CI: [2.711, 9.142]

## Gate 4 — Single-block OOS
- N days OOS: 40 | trades OOS: 90
- OOS daily mean: 5.33 | std: 19.48
- **OOS Sharpe: 4.346**
- OOS DSR p-value: 0.0000
- OOS bootstrap 99.9% CI: [-4.600, 10.084]
- **Gate 4 verdict: ❌ FAIL**

## Gate 6 — Bootstrap 99.9% CI low > 0 (full)
- 99.9% CI low (full): 2.711
- **Gate 6 verdict: ✅ PASS**

## Gate 3 — Walk-forward 8 windows (≥ 6/8 positive)
```
 window      start        end  n_days  sharpe  mean_net_pips
      1 2025-04-15 2025-05-22      15   2.107          2.405
      2 2025-05-29 2025-07-01      15   6.025          9.836
      3 2025-07-02 2025-08-12      15   8.816         19.338
      4 2025-08-14 2025-09-23      15  10.204         19.278
      5 2025-09-25 2025-11-21      14   6.425         13.111
      6 2025-11-25 2026-01-09      14   4.020          3.549
      7 2026-01-13 2026-02-19      14   5.096          7.749
      8 2026-02-20 2026-04-23      14   2.751          3.403
```
- Positive windows: 8/8
- **Gate 3 verdict: ✅ PASS**

## Gate 2 — DSR p < 0.05
- DSR p-value (full): 0.0000
- **Gate 2 verdict: ✅ PASS**

## Cost-model sensitivity (optimistic 50%)
- Sharpe under optimistic costs: 7.111

## Final verdict
- Passed: ['Gate 2 (DSR)', 'Gate 3 (WF)', 'Gate 6 (Bootstrap)']
- Failed: ['Gate 4 (OOS)']

### ❌ K4 TRIGGERED — gates §2.4 FAIL on observed PnL minus cost model