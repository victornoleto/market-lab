# spy_beater_hunt iter 037 — Final Report — `sensitivity-h6-buffer-lag`

**Gross tier**: **PROMISING** — `gross_score=69/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=63/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.03%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.02%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 13.99%)
- MDD bar: PASS (mean = 34.93%)
- Gates bar (same as gross): PASS

**Primary citation**: iter 026 H6 baseline (closest-to-winner Tier A, PBO 0.00) + iter 002 KILL #8 (buffer >=5% worsens MDD; 2% empirical sweet spot for UPRO 3x) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed canonical 200d SMA + [advances_fin_ml, p.31-34] gate framework + Lei 14.754/2023 DARF anual

---

## Selected config: `h6_lag2`

Spec:

```json
{
  "type": "blend",
  "constituents": [
    {
      "weight": 0.3,
      "spec": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "QQQSIM",
        "lag_days": 2
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
          "UPROSIM": 0.3,
          "TMFSIM": 0.25,
          "IEFSIM": 0.15,
          "UGLSIM": 0.15,
          "KMLMSIM": 0.15
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "SPYSIM",
        "lag_days": 2
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "static",
        "weights": {
          "NTSXSIM": 0.35,
          "GDESIM": 0.3,
          "TLTSIM": 0.2,
          "KMLMSIM": 0.15
        }
      }
    },
    {
      "weight": 0.2,
      "spec": {
        "type": "lrs",
        "filter": "momentum",
        "lookback_days": 126,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "QQQSIM",
        "lag_days": 2
      }
    }
  ]
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.952 | 16.92% | 33.02% | 0.844 | 14.79% | 34.93% | 2.13 | 5/7 |
| **spy_real** | 0.965 | 15.14% | 33.02% | 0.850 | 13.20% | 34.93% | 1.94 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $294,141 (terminal $4,353), drag 2.13pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $23,507 (terminal $0), drag 1.94pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h6_baseline | 0.942 | 0.970 |
| h6_buffer2 | 0.928 | 0.937 |
| h6_lag2 | 0.952 | 0.965 |
| h6_buffer2_lag2 | 0.948 | 0.957 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 22 | 30 | mean = 16.03%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.02%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.53e-04, n_trials = 144 |
| 5. Sharpe | 3 | 10 | mean = 0.959 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 33.02% |
| 10y | 100.0% | 33.02% |
| 15y | 100.0% | 33.02% |
| 20y | 100.0% | 33.02% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
