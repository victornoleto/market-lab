# Iter 029 — Final Report — `AVDV-add`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 88/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 93/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `avdv_lite`

Weights:

```json
{
  "NTSXSIM": 0.225,
  "GDESIM": 0.25,
  "KMLMSIM": 0.325,
  "TLTSIM": 0.15,
  "AVDVSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.081 | 10.91% | 21.01% | 6/7 | 3.58e-07 |
| **vt_real** | 0.985 | 10.09% | 19.51% | 7/7 | 9.69e-04 |
| **ndx_real** | 1.123 | 10.72% | 12.96% | 7/7 | 3.15e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avdv_lite | 1.081 | 0.985 | 1.123 |
| avdv_mod | 1.075 | 0.963 | 1.102 |
| avdv_med | 1.063 | 0.936 | 1.076 |
| avdv_heavy | 1.046 | 0.907 | 1.047 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.081 | +0.401 | [OK] |
| vt_real | 0.900 | 0.950 | 0.985 | +0.085 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.123 | +0.223 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 27
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVDVSIM** = `VSSSIM + 100bps/y tilt premium` — INCOMPLETE. VSSSIM
  is Vanguard FTSE All-World ex-US Small-Cap (passive, no quality
  screen). 100bps/y is the published Avantis intl tilt premium est.
  vs Vanguard benchmark (intl SCV historically richer than US SCV due
  to less crowded factor exposure). User-cited 2025 ~40% AVDV return
  is heavily concentrated in a single-year regime — NOT generalizable
  to long-history.

## Lesson

**Both KILL #1 and KILL #2 fire — sleeve closed.**

- **KILL #1 (no-positive-config) FIRES**: best config (`avdv_lite`,
  5% AVDV) Sharpe = 1.081 / 0.985 / 1.123 vs iter 023 baseline 1.189
  / 1.004 / 1.135. Loses on **3/3 datasets** (Δ −0.108 / −0.019 /
  −0.012). Mean Sharpe 1.063 < iter 023 mean 1.109. Best config beats
  iter 023 on 0/3 datasets — KILL #1 fires hard.
- **KILL #2 (monotonic regression) FIRES**: Sharpe falls monotonically
  with AVDV weight 5% -> 20% on ALL 3 datasets:
  - lh_56y 1.081 -> 1.046 (Δ −0.035)
  - vt_real 0.985 -> 0.907 (Δ −0.078)
  - ndx_real 1.123 -> 1.047 (Δ −0.076)
- **Why score=STRONG 88/100**: iter 023 base still beats SPY when
  AVDV at 5% included — base quality drives the score, NOT AVDV.
- **Decision**: AVDV sleeve **CLOSED**. Worse than AVUV (iter 028)
  and NTSD (iter 027) on the long-history datasets. F5 Global
  Factor-only (iter 036) probability significantly reduced — both
  AVUV and AVDV failed; only momentum factors (SPMO/IDMO) and AVEM
  remain to test. F6 Global Hybrid (iter 037) likewise weakened.
- The user-cited 2025 ~40% AVDV return is a single-year regime
  artifact. Long-history (lh_56y) tells a different story: intl SCV
  factor at 1× notional underperforms the iter 023 levered stack in
  every weight tested. Citation `[ilmanen_expected_returns, ch.19]`
  remains valid theoretically, but empirical edge does not survive
  the comparison vs iter 023's KMLM-anchored crisis-alpha.
