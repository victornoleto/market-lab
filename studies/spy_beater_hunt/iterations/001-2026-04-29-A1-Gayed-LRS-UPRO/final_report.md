# spy_beater_hunt iter 001 — Final Report — `A1-Gayed-LRS-UPRO`

**Gross tier**: **PROMISING** — `gross_score=60/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=55/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.23%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 51.60%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.22%)
- MDD bar: PASS (mean = 53.59%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60]

---

## Selected config: `a1_lrs_split`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "UPROSIM": 0.5,
    "SSOSIM": 0.5
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "lag_days": 1
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.670 | 16.91% | 54.70% | 0.609 | 14.83% | 55.40% | 2.08 | 6/7 |
| **spy_real** | 0.643 | 15.55% | 48.50% | 0.583 | 13.62% | 51.78% | 1.94 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 40 year-end settlements, total DARF $405,063 (terminal $0), drag 2.08pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $27,550 (terminal $0), drag 1.94pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a1_pure_lrs | 0.641 | 0.627 |
| a1_lrs_cash | 0.605 | 0.618 |
| a1_lrs_split | 0.670 | 0.643 |
| a1_lrs_kmlm_off | 0.606 | 0.609 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 22 | 30 | mean = 16.23%, bar = 11.21% |
| 2. MDD vs SPY | 6 | 20 | mean = 51.60%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.42e-02, n_trials = 4 |
| 5. Sharpe | 1 | 10 | mean = 0.657 |
| 6. Robustness | 9 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 84.7% | 54.70% |
| 10y | 96.8% | 54.70% |
| 15y | 98.1% | 54.70% |
| 20y | 100.0% | 54.70% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
