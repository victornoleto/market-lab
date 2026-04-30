# spy_beater_hunt iter 010 — Final Report — `C1-vol-targeted`

**Gross tier**: **PROMISING** — `gross_score=60/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=57/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 13.54%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 41.86%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 11.83%)
- MDD bar: PASS (mean = 41.87%)
- Gates bar (same as gross): PASS

**Primary citation**: [systematic_trading, ch.10] Carver vol-targeting canonical + [advances_fin_ml, p.31-34] factor framework (vol as state variable) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking via dynamic weight + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale

---

## Selected config: `c1_vt20_sso`

Spec:

```json
{
  "type": "vol_target",
  "cash_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "vol_window": 60,
  "vol_lag_days": 1,
  "weight_min": 0.0,
  "weight_max": 1.0,
  "underlying_weights": {
    "SSOSIM": 1.0
  },
  "underlying_leverage_factor": 2.0,
  "target_vol_annual": 0.2
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.714 | 13.44% | 46.78% | 0.639 | 11.76% | 46.78% | 1.68 | 6/7 |
| **spy_real** | 0.728 | 13.64% | 36.94% | 0.650 | 11.91% | 36.97% | 1.72 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 40 year-end settlements, total DARF $130,461 (terminal $983), drag 1.68pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $17,877 (terminal $0), drag 1.72pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| c1_vt20_sso | 0.714 | 0.728 |
| c1_vt22_upro | 0.688 | 0.707 |
| c1_vt25_upro | 0.659 | 0.686 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 17 | 30 | mean = 13.54%, bar = 11.21% |
| 2. MDD vs SPY | 10 | 20 | mean = 41.86%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 5.02e-03, n_trials = 35 |
| 5. Sharpe | 1 | 10 | mean = 0.721 |
| 6. Robustness | 9 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 75.0% | 46.78% |
| 10y | 98.4% | 46.78% |
| 15y | 100.0% | 46.78% |
| 20y | 100.0% | 46.78% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 97.22%, n_windows = 36

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
