# spy_beater_hunt iter 001 — Final Report — `A1-Gayed-LRS-UPRO`

**Tier**: **PROMISING** — `score=67/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 19.01%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 50.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

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

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.670 | 16.91% | 54.70% | 6/7 | 7.91e-04 |
| **vt_real** | 0.784 | 20.68% | 48.50% | 6/7 | 1.34e-02 |
| **ndx_real** | 0.753 | 19.43% | 48.50% | 5/7 | 2.63e-02 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| a1_pure_lrs | 0.641 | 0.770 | 0.741 |
| a1_lrs_cash | 0.605 | 0.761 | 0.743 |
| a1_lrs_split | 0.670 | 0.784 | 0.753 |
| a1_lrs_kmlm_off | 0.606 | 0.752 | 0.728 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 28 | 30 | mean = 19.01%, bar = 13.80% |
| 2. MDD vs SPY | 0 | 20 | mean = 50.57%, bar = 40.85% |
| 3. Gates | 17 | 20 | per_ds = {'lh_56y': 6, 'vt_real': 6, 'ndx_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.63e-02, n_trials = 4 |
| 5. Sharpe | 2 | 10 | mean = 0.736 |
| 6. Robustness | 10 | 10 | input_bonus = 10 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts (5-scale): 5/5
- bonus_pts (10-scale): 10/10
- pct_positive_sharpe: 100.00%
- n_windows: 36
- anchor_dataset: lh_56y

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
