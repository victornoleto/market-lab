# spy_beater_hunt iter 002 — Final Report — `A2-LRS-sensitivity-sweep`

**Tier**: **MARGINAL** — `score=57/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 18.96%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 57.57%)
- Gates bar (≥ 2/3 datasets at threshold): FAIL

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] + studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep)

---

## Selected config: `a2_sma200_th2_3xupro`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.02,
  "on_weights": {
    "UPROSIM": 1.0
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.682 | 19.92% | 57.57% | 5/7 | 1.43e-03 |
| **spy_real** | 0.645 | 17.99% | 57.57% | 4/7 | 4.16e-02 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a2_sma100_3xupro | 0.528 | 0.684 |
| a2_sma200_th2_3xupro | 0.682 | 0.645 |
| a2_sma200_th5_3xupro | 0.635 | 0.661 |
| a2_ema150_th2_3xupro | 0.583 | 0.614 |
| a2_sma150_2xsso | 0.649 | 0.630 |
| a2_ema100_th2_2xsso | 0.589 | 0.671 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 28 | 30 | mean = 18.96%, bar = 11.21% |
| 2. MDD vs SPY | 4 | 20 | mean = 57.57%, bar = 55.17% |
| 3. Gates | 4 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 4}, cross_met = False |
| 4. DSR | 10 | 10 | worst_p = 4.16e-02, n_trials = 10 |
| 5. Sharpe | 1 | 10 | mean = 0.663 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 84.7% | 57.57% |
| 10y | 100.0% | 57.57% |
| 15y | 100.0% | 57.57% |
| 20y | 100.0% | 57.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
