# spy_beater_hunt iter 013 — Final Report — `D1-concentrated-growth-tsmom`

**Gross tier**: **MARGINAL** — `gross_score=59/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=54/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 12.83%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 35.27%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: FAIL (mean = 11.20%)
- MDD bar: PASS (mean = 36.23%)
- Gates bar (same as gross): PASS

**Primary citation**: Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 + Faber 2007 GTAA (10m TSMOM equivalent at monthly frequency) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate-family rationale + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `d1_qqq_6m_tsmom`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "QQQSIM": 1.0
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
| **lh_56y** | 0.791 | 14.10% | 36.49% | 0.705 | 12.33% | 36.49% | 1.77 | 5/7 |
| **spy_real** | 0.766 | 11.56% | 34.04% | 0.677 | 10.06% | 35.97% | 1.50 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 40 year-end settlements, total DARF $160,656 (terminal $483), drag 1.77pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $11,950 (terminal $0), drag 1.50pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| d1_qqq_6m_tsmom | 0.791 | 0.766 |
| d1_qqq_12m_tsmom | 0.792 | 0.704 |
| d1_qld_6m_tsmom | 0.652 | 0.684 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 16 | 30 | mean = 12.83%, bar = 11.21% |
| 2. MDD vs SPY | 12 | 20 | mean = 35.27%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.99e-03, n_trials = 41 |
| 5. Sharpe | 2 | 10 | mean = 0.779 |
| 6. Robustness | 8 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 62.5% | 36.49% |
| 10y | 76.6% | 36.49% |
| 15y | 81.7% | 36.49% |
| 20y | 100.0% | 36.49% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
