# spy_beater_hunt iter 006 — Final Report — `A2-tqqq-track-split`

**Gross tier**: **PROMISING** — `gross_score=67/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=60/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 17.33%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 49.73%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 15.20%)
- MDD bar: PASS (mean = 50.96%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate (asset-agnostic) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM transfer) + [advances_fin_ml, p.31-34] factor framework (NDX as US-Large-growth tilt)

---

## Selected config: `a6_tqqq_split_kmlm30_tlt10`

Spec:

```json
{
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
  "lag_days": 1
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.754 | 18.56% | 62.39% | 0.683 | 16.34% | 62.39% | 2.23 | 6/7 |
| **spy_real** | 0.763 | 16.09% | 37.07% | 0.683 | 14.07% | 39.54% | 2.02 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $490,824 (terminal $10,669), drag 2.23pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $28,486 (terminal $0), drag 2.02pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a6_tqqq_split_lrs | 0.652 | 0.665 |
| a6_tqqq_split_kmlm30 | 0.717 | 0.729 |
| a6_tqqq_split_kmlm30_tlt10 | 0.754 | 0.763 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 25 | 30 | mean = 17.33%, bar = 11.21% |
| 2. MDD vs SPY | 7 | 20 | mean = 49.73%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 3.05e-03, n_trials = 23 |
| 5. Sharpe | 2 | 10 | mean = 0.759 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 100.0% | 62.39% |
| 10y | 100.0% | 62.39% |
| 15y | 100.0% | 62.39% |
| 20y | 100.0% | 62.39% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
