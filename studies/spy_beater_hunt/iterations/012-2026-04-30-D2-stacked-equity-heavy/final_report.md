# spy_beater_hunt iter 012 — Final Report — `D2-stacked-equity-heavy`

**Gross tier**: **MARGINAL** — `gross_score=52/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=50/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 12.23%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 52.65%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 11.64%)
- MDD bar: PASS (mean = 52.65%)
- Gates bar (same as gross): PASS

**Primary citation**: [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (AVUV SCV factor) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay (UPRO leg) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `d2_ntsx_avuv`

Spec:

```json
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.5,
    "AVUVSIM": 0.5
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.799 | 12.88% | 52.65% | 0.771 | 12.43% | 52.65% | 0.45 | 6/7 |
| **spy_real** | 0.678 | 11.59% | 52.65% | 0.639 | 10.86% | 52.65% | 0.73 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $196,860 (terminal $196,860), drag 0.45pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $16,352 (terminal $16,352), drag 0.73pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| d2_ntsx_avuv | 0.799 | 0.678 |
| d2_ntsx_upro_avuv | 0.625 | 0.608 |
| d2_upro_avuv | 0.586 | 0.572 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 14 | 30 | mean = 12.23%, bar = 11.21% |
| 2. MDD vs SPY | 6 | 20 | mean = 52.65%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 9.40e-03, n_trials = 38 |
| 5. Sharpe | 2 | 10 | mean = 0.738 |
| 6. Robustness | 7 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 58.3% | 52.65% |
| 10y | 65.6% | 52.65% |
| 15y | 81.7% | 52.65% |
| 20y | 81.0% | 52.65% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
