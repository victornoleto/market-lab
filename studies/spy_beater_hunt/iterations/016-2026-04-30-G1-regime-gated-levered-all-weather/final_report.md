# spy_beater_hunt iter 016 — Final Report — `G1-regime-gated-levered-all-weather`

**Gross tier**: **PROMISING** — `gross_score=61/100`, `gross_winner_met=False`

**Net tier**: **MARGINAL** — `net_score=57/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): FAIL (mean = 10.34%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 18.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: FAIL (mean = 9.01%)
- MDD bar: PASS (mean = 19.87%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate + Bridgewater All-Weather (Dalio 1996) F1-stack ON-state composition + Asness (1996) 'Why Not 100% Equities?' JPM leverage-balanced thesis + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (NTSX/GDE) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM defensive) + [advances_fin_ml, p.31-34] factor framework — gate x sleeve orthogonality explicitly tested at SECOND decay regime (1.41x stack, no decay) complementing iter 014 (3x LETF, decay-dominated) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `g1_f1_stack_sma200_ief`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "NTSXSIM": 0.35,
    "GDESIM": 0.3,
    "TLTSIM": 0.2,
    "KMLMSIM": 0.15
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.091 | 10.49% | 18.57% | 0.950 | 9.13% | 19.87% | 1.35 | 7/7 |
| **spy_real** | 1.070 | 10.20% | 18.57% | 0.931 | 8.88% | 19.87% | 1.32 | 7/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $41,079 (terminal $424), drag 1.35pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $8,749 (terminal $0), drag 1.32pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| g1_f1_stack_sma200_ief | 1.091 | 1.070 |
| g1_f1_stack_sma200_kmlm | 0.765 | 0.699 |
| g1_f1_stack_sma200_blend | 0.985 | 0.941 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 11 | 30 | mean = 10.34%, bar = 11.21% |
| 2. MDD vs SPY | 18 | 20 | mean = 18.57%, bar = 55.17% |
| 3. Gates | 15 | 20 | per_ds = {'lh_56y': 7, 'spy_real': 7}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.47e-05, n_trials = 50 |
| 5. Sharpe | 4 | 10 | mean = 1.080 |
| 6. Robustness | 3 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 33.3% | 18.57% |
| 10y | 38.5% | 18.57% |
| 15y | 50.0% | 18.57% |
| 20y | 0.0% | 18.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
