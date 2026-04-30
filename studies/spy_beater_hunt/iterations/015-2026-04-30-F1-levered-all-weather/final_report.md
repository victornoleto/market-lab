# spy_beater_hunt iter 015 — Final Report — `F1-levered-all-weather`

**Gross tier**: **PROMISING** — `gross_score=61/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=60/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 11.95%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 26.82%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 11.35%)
- MDD bar: PASS (mean = 26.82%)
- Gates bar (same as gross): PASS

**Primary citation**: Bridgewater All-Weather (Dalio 1996, public papers 2011) risk-parity foundation + Asness (1996) 'Why Not 100% Equities?' JPM — leverage-balanced thesis + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (NTSX/GDE rationale) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay magnitude + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM diversification) + [advances_fin_ml, p.31-34] factor framework (risk-parity construction) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `f1_aw_stack_15x`

Spec:

```json
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.35,
    "GDESIM": 0.3,
    "TLTSIM": 0.2,
    "KMLMSIM": 0.15
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.004 | 11.60% | 26.82% | 0.953 | 11.14% | 26.82% | 0.47 | 5/7 |
| **spy_real** | 1.032 | 12.30% | 26.82% | 0.956 | 11.56% | 26.82% | 0.74 | 7/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $100,200 (terminal $100,200), drag 0.47pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $19,136 (terminal $19,136), drag 0.74pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| f1_aw_baseline_1x | 0.985 | 0.895 |
| f1_aw_stack_15x | 1.004 | 1.032 |
| f1_aw_letf_2x | 0.897 | 0.910 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 14 | 30 | mean = 11.95%, bar = 11.21% |
| 2. MDD vs SPY | 15 | 20 | mean = 26.82%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 7}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.66e-05, n_trials = 47 |
| 5. Sharpe | 3 | 10 | mean = 1.018 |
| 6. Robustness | 6 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 33.3% | 26.82% |
| 10y | 46.2% | 26.82% |
| 15y | 62.5% | 26.82% |
| 20y | 100.0% | 26.82% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
