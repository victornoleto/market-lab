# spy_beater_hunt iter 017 — Final Report — `G2-regime-gated-levered-all-weather-letf2x`

**Gross tier**: **PROMISING** — `gross_score=64/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=58/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 14.02%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.72%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 12.22%)
- MDD bar: PASS (mean = 35.06%)
- Gates bar (same as gross): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate + Bridgewater All-Weather (Dalio 1996) F1 LETF 2x ON-state composition + Asness (1996) 'Why Not 100% Equities?' JPM leverage-balanced thesis at moderate decay + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking baseline + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM defensive) + [advances_fin_ml, p.31-34] factor framework - gate x sleeve orthogonality explicitly tested at THIRD decay regime (2.25x LETF, moderate decay) complementing iter 014 (3x LETF, decay-dominated) and iter 016 (1.41x stack, no decay) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `g2_f1_letf_2x_sma200_ief`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "UPROSIM": 0.3,
    "TMFSIM": 0.25,
    "IEFSIM": 0.15,
    "UGLSIM": 0.15,
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
| **lh_56y** | 0.967 | 14.14% | 33.72% | 0.852 | 12.34% | 35.06% | 1.80 | 6/7 |
| **spy_real** | 0.973 | 13.90% | 33.72% | 0.855 | 12.10% | 35.06% | 1.80 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $127,297 (terminal $90), drag 1.80pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $18,593 (terminal $0), drag 1.80pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| g2_f1_letf_2x_sma200_ief | 0.967 | 0.973 |
| g2_f1_letf_2x_sma200_kmlm | 0.797 | 0.766 |
| g2_f1_letf_2x_sma200_blend | 0.914 | 0.906 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 18 | 30 | mean = 14.02%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.72%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 9.50e-05, n_trials = 53 |
| 5. Sharpe | 3 | 10 | mean = 0.970 |
| 6. Robustness | 7 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 50.0% | 33.72% |
| 10y | 61.5% | 33.72% |
| 15y | 75.0% | 33.72% |
| 20y | 100.0% | 33.72% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
