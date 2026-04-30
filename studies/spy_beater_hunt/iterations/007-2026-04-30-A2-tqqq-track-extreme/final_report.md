# spy_beater_hunt iter 007 — Final Report — `A2-tqqq-track-extreme`

**Gross tier**: **PROMISING** — `gross_score=67/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=61/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.08%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 42.33%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.09%)
- MDD bar: PASS (mean = 43.48%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate (asset-agnostic) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM/TLT extension) + [advances_fin_ml, p.31-34] factor framework (NDX as US-Large-growth tilt)

---

## Selected config: `a7_tqqq_split_kmlm40_tlt10`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "TQQQSIM": 0.25,
    "QLDSIM": 0.25,
    "KMLMSIM": 0.4,
    "TLTSIM": 0.1
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.807 | 17.45% | 51.12% | 0.725 | 15.32% | 51.12% | 2.13 | 6/7 |
| **spy_real** | 0.802 | 14.71% | 33.54% | 0.714 | 12.86% | 35.85% | 1.86 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $351,270 (terminal $10,826), drag 2.13pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $21,644 (terminal $0), drag 1.86pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a7_tqqq_split_kmlm35_tlt10 | 0.779 | 0.782 |
| a7_tqqq_split_kmlm40_tlt10 | 0.807 | 0.802 |
| a7_tqqq_split_kmlm30_tlt15 | 0.777 | 0.784 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 22 | 30 | mean = 16.08%, bar = 11.21% |
| 2. MDD vs SPY | 10 | 20 | mean = 42.33%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.72e-03, n_trials = 26 |
| 5. Sharpe | 2 | 10 | mean = 0.804 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 94.4% | 51.12% |
| 10y | 100.0% | 51.12% |
| 15y | 100.0% | 51.12% |
| 20y | 100.0% | 51.12% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
