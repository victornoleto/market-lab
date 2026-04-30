# Iter 040 — Final Report — `F3-US-Hybrid-SPMO`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 88/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 93/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.5, p.10] + [stocks_on_the_move, p.21-30]

---

## Selected config: `f3_spmo_5_subKMLM`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.25,
  "KMLMSIM": 0.3,
  "TLTSIM": 0.15,
  "SPMOSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.107 | 11.40% | 21.00% | 7/7 | 4.48e-09 |
| **vt_real** | 1.008 | 10.63% | 19.27% | 7/7 | 7.23e-04 |
| **ndx_real** | 1.173 | 11.49% | 13.26% | 6/7 | 1.62e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| f3_spmo_5_subKMLM | 1.107 | 1.008 | 1.173 |
| f3_spmo_10_subKMLM | 1.087 | 0.994 | 1.179 |
| f3_spmo_15_subKMLM | 1.060 | 0.973 | 1.174 |
| f3_spmo_20_subKMLM | 1.028 | 0.947 | 1.162 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.107 | +0.427 | [OK] |
| vt_real | 0.900 | 0.950 | 1.008 | +0.108 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.173 | +0.273 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
