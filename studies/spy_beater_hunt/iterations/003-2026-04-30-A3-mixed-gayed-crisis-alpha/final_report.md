# spy_beater_hunt iter 003 — Final Report — `A3-mixed-gayed-crisis-alpha`

**Gross tier**: **PROMISING** — `gross_score=64/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=59/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 14.99%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 41.87%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 13.12%)
- MDD bar: PASS (mean = 43.87%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking

---

## Selected config: `a3_lrs_split_kmlm20`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "UPROSIM": 0.4,
    "SSOSIM": 0.4,
    "KMLMSIM": 0.2
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
| **lh_56y** | 0.719 | 15.58% | 43.22% | 0.647 | 13.66% | 43.87% | 1.93 | 6/7 |
| **spy_real** | 0.692 | 14.39% | 40.53% | 0.621 | 12.59% | 43.87% | 1.80 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $201,427 (terminal $0), drag 1.93pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $21,348 (terminal $0), drag 1.80pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a3_lrs_split_kmlm10 | 0.681 | 0.665 |
| a3_lrs_split_kmlm20 | 0.719 | 0.692 |
| a3_lrs_split_tlt15 | 0.709 | 0.682 |
| a3_lrs_split_blend | 0.713 | 0.696 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 20 | 30 | mean = 14.99%, bar = 11.21% |
| 2. MDD vs SPY | 10 | 20 | mean = 41.87%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.39e-02, n_trials = 14 |
| 5. Sharpe | 1 | 10 | mean = 0.705 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 43.22% |
| 10y | 100.0% | 43.22% |
| 15y | 100.0% | 43.22% |
| 20y | 100.0% | 43.22% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
