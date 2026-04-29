# Iter 028 — Final Report — `AVUV-add`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 88/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 93/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.2, p.37-41]

---

## Selected config: `avuv_lite`

Weights:

```json
{
  "NTSXSIM": 0.225,
  "GDESIM": 0.25,
  "KMLMSIM": 0.325,
  "TLTSIM": 0.15,
  "AVUVSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.115 | 11.18% | 20.84% | 6/7 | 3.17e-09 |
| **vt_real** | 0.996 | 10.32% | 18.72% | 7/7 | 8.34e-04 |
| **ndx_real** | 1.140 | 10.95% | 13.14% | 7/7 | 2.47e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avuv_lite | 1.115 | 0.996 | 1.140 |
| avuv_mod | 1.113 | 0.981 | 1.132 |
| avuv_med | 1.103 | 0.961 | 1.117 |
| avuv_heavy | 1.089 | 0.937 | 1.098 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.115 | +0.435 | [OK] |
| vt_real | 0.900 | 0.950 | 0.996 | +0.096 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.140 | +0.240 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVUVSIM** = `VBRSIM + 75bps/y tilt premium` — INCOMPLETE. VBRSIM
  is Vanguard Russell 2000 Value (passive, market-cap weighted) and
  does NOT replicate Avantis's quality screening (size + value +
  profitability combined; junk-stock exclusion). 75bps/y is an
  estimate of the Avantis tilt premium net of fees from published
  factor regressions. Expect real AVUV to behave with similar but
  not identical profile (especially in 2018+ live history).

## Lesson

**KILL #1 narrowly survives, KILL #2 fires — sleeve marginal at 5%.**

- **KILL #1 (no-positive-config)**: best config (`avuv_lite`, 5% AVUV)
  beats iter 023 on **1/3 datasets**: ndx_real +0.005 marginal
  (criterion: >=1/3 — barely passes). lh_56y −0.074, vt_real −0.008.
  Mean Sharpe 1.084 < iter 023 mean 1.109. **KILL #1 does NOT fire**
  (threshold is >=1/3), but the edge is cosmetic at +0.005.
- **KILL #2 (monotonic regression) FIRES**: Sharpe falls
  monotonically with AVUV weight 5% -> 20% on all 3 datasets:
  - lh_56y 1.115 -> 1.089 (Δ −0.026)
  - vt_real 0.996 -> 0.937 (Δ −0.059)
  - ndx_real 1.140 -> 1.098 (Δ −0.042)
  Same structural pattern as iter 013 VBRSIM tilt — small-cap value
  factor underperforms the iter 023 mix at every weight tested.
- **Why score=STRONG 88/100**: NEW SPY-only mandate; iter 023 base
  still beats SPY on all 3 datasets when AVUV is included at 5%.
  Score reflects iter 023 base quality, not AVUV's marginal
  contribution.
- **Decision**: AVUV sleeve **marginal/closed**. The +0.005 ndx_real
  edge is below noise. AVUV at 5% may still be relevant for Phase 2
  Hybrid F3 (iter 034) under a mean-of-Sharpe-edges interpretation,
  but does not beat iter 023 substantively. F2 US Factor-only (iter
  033) probability of advance reduced to ~25% — VTI vanilla + AVUV
  at 1x notional unlikely to beat 1.5x-leveraged iter 023 stack.
- Citation `[risk_parity, ch.2, p.37-41]` Fama-French SCV is real but
  the size factor's 2010-2024 underperformance + the iter 023 base's
  KMLM crisis-alpha fully absorbs what AVUV would add. Confirms iter
  013's earlier VBRSIM finding.
