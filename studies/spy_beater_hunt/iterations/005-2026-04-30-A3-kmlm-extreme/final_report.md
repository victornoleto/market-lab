# spy_beater_hunt iter 005 — Final Report — `A3-kmlm-extreme`

**Gross tier**: **PROMISING** — `gross_score=63/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=58/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 13.57%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 32.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 11.86%)
- MDD bar: PASS (mean = 35.64%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking

---

## Selected config: `a5_lrs_split_kmlm30_tlt10`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "UPROSIM": 0.3,
    "SSOSIM": 0.3,
    "KMLMSIM": 0.3,
    "TLTSIM": 0.1
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
| **lh_56y** | 0.818 | 14.36% | 32.57% | 0.727 | 12.56% | 35.64% | 1.80 | 5/7 |
| **spy_real** | 0.768 | 12.78% | 32.57% | 0.682 | 11.16% | 35.64% | 1.62 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $137,529 (terminal $807), drag 1.80pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $15,198 (terminal $0), drag 1.62pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a5_lrs_split_kmlm35 | 0.791 | 0.739 |
| a5_lrs_split_kmlm40 | 0.820 | 0.756 |
| a5_lrs_split_kmlm30_tlt10 | 0.818 | 0.768 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 17 | 30 | mean = 13.57%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 32.57%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.93e-03, n_trials = 20 |
| 5. Sharpe | 2 | 10 | mean = 0.793 |
| 6. Robustness | 9 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 66.7% | 32.57% |
| 10y | 92.3% | 32.57% |
| 15y | 100.0% | 32.57% |
| 20y | 100.0% | 32.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
