# Gates §2.4 verdict — observed PnL minus Pepperstone Razor 2025 costs

Generated: 2026-05-01

Methodology: gates applied to (realized pips - spread - commission) per trade,
aggregated daily. Skips P3 replicator since the question is edge persistence
after current costs, not rule-understanding fidelity.

## Cost model (Pepperstone Razor 2025, pips RT)
- Spreads: {'EURUSD': 0.13, 'GBPUSD': 0.5, 'USDCAD': 0.74, 'USDCHF': 0.75, 'EURGBP': 0.75, 'EURCHF': 1.2}
- Commission: 0.7 pips RT (≈ $7/lot)
- Total cost per trade range: 0.83 – 1.90 pips

## Full-period (2013-09 → 2021-06, 7.8 years)
- N trade days: 1289
- N trades: 3305
- Daily net pips mean: 3.01 | std: 19.04
- **Annualized Sharpe (full): 2.507**
- DSR p-value (n_trials=1): 0.0000
- Bootstrap 99.9% CI: [1.075, 4.013]

## Gate 4 — Single-block OOS (last 12 months: 2020-06 → 2021-06)
- N days OOS: 192 | trades OOS: 397
- OOS daily mean: 1.40 | std: 11.73
- **OOS Sharpe: 1.894**
- OOS DSR p-value: 0.0000
- OOS bootstrap 99.9% CI: [-1.668, 8.114]
- **Gate 4 verdict: ❌ FAIL** (require Sharpe > 0 AND CI low > 0)

## Gate 6 — Bootstrap 99.9% CI low > 0 (full sample)
- 99.9% CI low (full): 1.075
- **Gate 6 verdict: ✅ PASS**

## Gate 3 — Walk-forward 8 janelas (≥ 6/8 positivas)
- Window split: 8 equal-time blocks of full sample
```
 window      start        end  n_days  sharpe  mean_net_pips
      1 2013-09-02 2015-05-12     162   1.475          2.208
      2 2015-05-15 2016-04-12     161   3.283          5.248
      3 2016-04-13 2017-01-30     161   5.389          7.907
      4 2017-02-03 2018-01-08     161   3.917          4.190
      5 2018-01-09 2018-12-13     161   3.454          3.426
      6 2018-12-14 2019-10-29     161   1.306          0.937
      7 2019-10-30 2020-08-06     161  -1.077         -1.169
      8 2020-08-07 2021-06-16     161   1.727          1.313
```
- Positive windows: 7/8
- **Gate 3 verdict: ✅ PASS** (require ≥ 6/8)

## Gate 2 — DSR p-value < 0.05
- DSR p-value (full): 0.0000
- **Gate 2 verdict: ✅ PASS** (require p < 0.05)

## Cost-model sensitivity (optimistic: 50% of estimated cost)
- Sharpe under optimistic costs: 3.844
- Even optimistic still: 3.84

## Final verdict
- Passed: ['Gate 2 (DSR)', 'Gate 3 (WF)', 'Gate 6 (Bootstrap)']
- Failed: ['Gate 4 (OOS)']

### ❌ K4 TRIGGERED — gates §2.4 FAIL on observed PnL minus Pepperstone costs
- Strategy does not maintain edge after current real costs in current OOS regime