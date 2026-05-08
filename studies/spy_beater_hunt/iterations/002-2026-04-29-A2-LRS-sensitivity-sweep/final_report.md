# spy_beater_hunt iter 002 — Final Report — `A2-LRS-sensitivity-sweep`

**Gross tier**: **MARGINAL** — `gross_score=57/100`, `gross_winner_met=False`

**Net tier**: **MARGINAL** — `net_score=52/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 18.96%)
- MDD bar (mean ≤ 55.17%): FAIL (mean = 57.57%)
- Gates bar (≥ 2/3 datasets at threshold): FAIL

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 16.61%)
- MDD bar: FAIL (mean = 57.57%)
- Gates bar (same as gross): FAIL

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

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.682 | 19.92% | 57.57% | 0.625 | 17.48% | 57.57% | 2.44 | 5/7 |
| **spy_real** | 0.645 | 17.99% | 57.57% | 0.589 | 15.74% | 57.57% | 2.25 | 4/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 40 year-end settlements, total DARF $1,103,768 (terminal $0), drag 2.44pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $46,807 (terminal $0), drag 2.25pp

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
