# spy_beater_hunt iter 008 — Final Report — `B1-hfea-classical`

**Gross tier**: **PROMISING** — `gross_score=63/100`, `gross_winner_met=False`

**Net tier**: **PROMISING** — `net_score=61/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 19.68%)
- MDD bar (mean ≤ 55.17%): FAIL (mean = 67.48%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 19.02%)
- MDD bar: FAIL (mean = 67.48%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + HFEA Bogleheads 2019 canonical 55/45 + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (leveraged duration as distinct factor)

---

## Selected config: `b1_balanced_5050`

Spec:

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.5,
    "TMFSIM": 0.5
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.755 | 20.62% | 67.48% | 0.741 | 20.14% | 67.48% | 0.49 | 6/7 |
| **spy_real** | 0.724 | 18.73% | 67.48% | 0.699 | 17.90% | 67.48% | 0.83 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $2,873,889 (terminal $2,873,889), drag 0.49pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $70,224 (terminal $70,224), drag 0.83pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b1_classic_5545 | 0.737 | 0.723 |
| b1_modern_6040 | 0.713 | 0.713 |
| b1_balanced_5050 | 0.755 | 0.724 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 29 | 30 | mean = 19.68%, bar = 11.21% |
| 2. MDD vs SPY | 0 | 20 | mean = 67.48%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 4.91e-03, n_trials = 29 |
| 5. Sharpe | 2 | 10 | mean = 0.739 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 86.1% | 67.48% |
| 10y | 100.0% | 67.48% |
| 15y | 100.0% | 67.48% |
| 20y | 100.0% | 67.48% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
