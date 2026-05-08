# Iter 041 — Final Report — `F7-US-Stacked-MF`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **WINNER 91/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 91/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.5] + Return Stacked methodology (ReSolve/Newfound 2023)

---

## Selected config: `f7_lite`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "RSSTSIM": 0.15,
  "GDESIM": 0.25,
  "KMLMSIM": 0.2,
  "TLTSIM": 0.15
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.072 | 12.73% | 26.65% | 5/7 | 1.43e-08 |
| **vt_real** | 0.978 | 11.90% | 22.97% | 7/7 | 1.05e-03 |
| **ndx_real** | 1.144 | 12.86% | 15.58% | 7/7 | 2.29e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| f7_lite | 1.072 | 0.978 | 1.144 |
| f7_balanced | 1.068 | 0.958 | 1.121 |
| f7_rsst_heavy | 1.058 | 0.942 | 1.108 |
| f7_pure_stack | 1.057 | 0.925 | 1.080 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.072 | +0.392 | [OK] |
| vt_real | 0.900 | 0.950 | 0.978 | +0.078 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.144 | +0.244 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
