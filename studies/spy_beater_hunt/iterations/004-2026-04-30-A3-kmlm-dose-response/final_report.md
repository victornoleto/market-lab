# spy_beater_hunt iter 004 — Final Report — `A3-kmlm-dose-response`

**Gross tier**: **PROMISING** — `gross_score=66/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=60/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 14.39%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 36.79%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 12.59%)
- MDD bar: PASS (mean = 39.49%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking

---

## Selected config: `a4_lrs_split_kmlm30`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "UPROSIM": 0.35,
    "SSOSIM": 0.35,
    "KMLMSIM": 0.3
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
| **lh_56y** | 0.765 | 15.13% | 37.39% | 0.685 | 13.25% | 39.49% | 1.88 | 6/7 |
| **spy_real** | 0.722 | 13.65% | 36.20% | 0.645 | 11.94% | 39.49% | 1.71 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $174,231 (terminal $602), drag 1.88pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $18,197 (terminal $0), drag 1.71pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a4_lrs_split_kmlm25 | 0.741 | 0.706 |
| a4_lrs_split_kmlm30 | 0.765 | 0.722 |
| a4_lrs_split_tlt20 | 0.724 | 0.698 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 19 | 30 | mean = 14.39%, bar = 11.21% |
| 2. MDD vs SPY | 12 | 20 | mean = 36.79%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 5.56e-03, n_trials = 17 |
| 5. Sharpe | 2 | 10 | mean = 0.744 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 37.39% |
| 10y | 100.0% | 37.39% |
| 15y | 100.0% | 37.39% |
| 20y | 100.0% | 37.39% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
