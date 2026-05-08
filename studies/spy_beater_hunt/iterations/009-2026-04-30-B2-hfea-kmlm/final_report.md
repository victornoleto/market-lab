# spy_beater_hunt iter 009 — Final Report — `B2-hfea-kmlm`

**Gross tier**: **PROMISING** — `gross_score=63/100`, `gross_winner_met=False`

**Net tier**: **PROMISING** — `net_score=62/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 18.65%)
- MDD bar (mean ≤ 55.17%): FAIL (mean = 61.51%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 17.98%)
- MDD bar: FAIL (mean = 61.51%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + [ilmanen_expected_returns, ch.19] MF crisis-alpha role + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (TMF and KMLM as distinct factors)

---

## Selected config: `b2_hfea_kmlm20`

Spec:

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.5,
    "TMFSIM": 0.3,
    "KMLMSIM": 0.2
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.785 | 19.21% | 61.51% | 0.768 | 18.70% | 61.51% | 0.51 | 5/7 |
| **spy_real** | 0.756 | 18.09% | 61.51% | 0.728 | 17.26% | 61.51% | 0.82 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $1,309,212 (terminal $1,309,212), drag 0.51pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $62,170 (terminal $62,170), drag 0.82pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b2_hfea_kmlm15 | 0.787 | 0.754 |
| b2_hfea_kmlm20 | 0.785 | 0.756 |
| b2_hfea_kmlm25 | 0.780 | 0.754 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 27 | 30 | mean = 18.65%, bar = 11.21% |
| 2. MDD vs SPY | 3 | 20 | mean = 61.51%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 3.07e-03, n_trials = 32 |
| 5. Sharpe | 2 | 10 | mean = 0.771 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 61.51% |
| 10y | 100.0% | 61.51% |
| 15y | 100.0% | 61.51% |
| 20y | 100.0% | 61.51% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
