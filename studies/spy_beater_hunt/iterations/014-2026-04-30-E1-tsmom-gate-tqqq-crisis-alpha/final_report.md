# spy_beater_hunt iter 014 — Final Report — `E1-tsmom-gate-tqqq-crisis-alpha`

**Gross tier**: **PROMISING** — `gross_score=65/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=59/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 17.20%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 47.48%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 15.04%)
- MDD bar: PASS (mean = 48.66%)
- Gates bar (same as gross): PASS

**Primary citation**: Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate-family rationale + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM transfer) + [advances_fin_ml, p.31-34] factor framework — gate axis × sleeve axis orthogonality assumption explicitly tested + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `e1_tqqq_split_kmlm30_tlt10_tsmom6m`

Spec:

```json
{
  "type": "lrs",
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
  "filter": "momentum",
  "lookback_days": 126,
  "lag_days": 1
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.755 | 18.85% | 51.57% | 0.683 | 16.53% | 51.57% | 2.32 | 5/7 |
| **spy_real** | 0.738 | 15.55% | 43.40% | 0.660 | 13.56% | 45.75% | 1.99 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $522,348 (terminal $6,369), drag 2.32pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $25,849 (terminal $0), drag 1.99pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| e1_tqqq_split_kmlm30_tlt10_tsmom6m | 0.755 | 0.738 |
| e1_tqqq_split_kmlm30_tlt10_tsmom12m | 0.786 | 0.696 |
| e1_tqqq_pure_tsmom6m | 0.603 | 0.654 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 24 | 30 | mean = 17.20%, bar = 11.21% |
| 2. MDD vs SPY | 8 | 20 | mean = 47.48%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 4.44e-03, n_trials = 44 |
| 5. Sharpe | 2 | 10 | mean = 0.746 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 51.57% |
| 10y | 100.0% | 51.57% |
| 15y | 100.0% | 51.57% |
| 20y | 100.0% | 51.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
