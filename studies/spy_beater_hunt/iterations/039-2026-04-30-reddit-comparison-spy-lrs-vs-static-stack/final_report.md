# spy_beater_hunt iter 039 — Final Report — `reddit-comparison-spy-lrs-vs-static-stack`

**Gross tier**: **PROMISING** — `gross_score=71/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=69/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.47%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.42%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 15.82%)
- MDD bar: PASS (mean = 33.42%)
- Gates bar (same as gross): PASS

**Primary citation**: Reddit r/LETFs comparison post + [leverage_for_the_long_run, ch.3-4] Gayed 200d SMA LRS canonical + iter 038 sweep results (capital-efficient stacking) + Bridgewater All-Weather (Dalio) + RiskParityChronicles CEGB

---

## Selected config: `T1_gold_heavy`

Spec:

```json
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.2,
    "GDESIM": 0.35,
    "RSSTSIM": 0.25,
    "TMFSIM": 0.2
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.045 | 16.54% | 33.42% | 1.011 | 16.04% | 33.42% | 0.49 | 6/7 |
| **spy_real** | 1.023 | 16.40% | 33.42% | 0.969 | 15.60% | 33.42% | 0.80 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $533,281 (terminal $533,281), drag 0.49pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $44,846 (terminal $44,846), drag 0.80pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| R1_spy_1x_buy_hold | 0.682 | 0.656 |
| R2_sso_lrs_200sma | 0.714 | 0.666 |
| R3_upro_lrs_200sma | 0.641 | 0.627 |
| T1_gold_heavy | 1.045 | 1.023 |
| B2_tmf10_balanced | 1.024 | 1.013 |
| B4_zroz_instead | 1.027 | 1.024 |
| L2_bogleheads_67ntsx | 1.015 | 0.985 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.47%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.42%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.66e-04, n_trials = 165 |
| 5. Sharpe | 4 | 10 | mean = 1.034 |
| 6. Robustness | 9 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 77.8% | 33.42% |
| 10y | 76.9% | 33.42% |
| 15y | 100.0% | 33.42% |
| 20y | 100.0% | 33.42% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
