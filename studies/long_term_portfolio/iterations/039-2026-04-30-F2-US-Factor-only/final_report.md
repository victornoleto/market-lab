# Iter 039 — Final Report — `F2-US-Factor-only`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 85/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 95/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.2, p.37-41] + [stocks_on_the_move, p.21-30]

---

## Selected config: `f2_spmo_heavy`

Weights:

```json
{
  "VTISIM": 0.3,
  "AVUVSIM": 0.1,
  "SPMOSIM": 0.2,
  "KMLMSIM": 0.2,
  "TLTSIM": 0.1,
  "GLDSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.086 | 11.38% | 24.82% | 7/7 | 1.14e-08 |
| **vt_real** | 0.874 | 9.79% | 24.45% | 7/7 | 4.55e-03 |
| **ndx_real** | 1.087 | 11.35% | 18.87% | 7/7 | 6.03e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| f2_balanced | 1.065 | 0.857 | 1.056 |
| f2_factor_heavy | 1.040 | 0.818 | 1.022 |
| f2_avuv_heavy | 1.057 | 0.828 | 1.013 |
| f2_spmo_heavy | 1.086 | 0.874 | 1.087 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.086 | +0.406 | [OK] |
| vt_real | 0.900 | 0.950 | 0.874 | -0.026 | [--] |
| ndx_real | 0.900 | 0.950 | 1.087 | +0.187 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## Lesson

(Append after manual review.)
