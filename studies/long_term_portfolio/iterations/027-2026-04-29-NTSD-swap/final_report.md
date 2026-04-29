# Iter 027 — Final Report — `NTSD-swap`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **WINNER 90/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 95/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.5, p.10]

---

## Selected config: `ntsd_lite_2055`

Weights:

```json
{
  "NTSXSIM": 0.2,
  "NTSDSIM": 0.05,
  "GDESIM": 0.25,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.092 | 11.09% | 22.20% | 7/7 | 7.05e-09 |
| **vt_real** | 0.980 | 10.19% | 19.03% | 7/7 | 1.03e-03 |
| **ndx_real** | 1.125 | 10.86% | 12.40% | 7/7 | 3.05e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| ntsd_lite_2055 | 1.092 | 0.980 | 1.125 |
| ntsd_mod_15105 | 1.072 | 0.956 | 1.108 |
| ntsd_med_10155 | 1.049 | 0.931 | 1.089 |
| ntsd_heavy_5205 | 1.025 | 0.905 | 1.069 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.092 | +0.412 | [OK] |
| vt_real | 0.900 | 0.950 | 0.980 | +0.080 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.125 | +0.225 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **NTSDSIM** = `0.90 SPYSIM + 0.60 VEASIM - 75bps/y` — INCOMPLETE.
  Active management (sub-advisor selection of intl-developed equity vs
  pure MSCI EAFE futures) and any tracking error from WisdomTree's
  rebalancing schedule are unmodeled. The 75bps/y drag is a TER-only
  estimate (real may differ).

## Lesson

**Both KILL #1 and KILL #2 fire — sleeve closed.**

- **KILL #1 (no-positive-config)**: best config (`ntsd_lite_2055`, 5%
  NTSD) Sharpe = 1.092 / 0.980 / 1.125 vs iter 023 baseline 1.189 /
  1.004 / 1.135. Loses on **3/3 datasets** (Δ −0.097 / −0.024 / −0.010).
  Mean Sharpe 1.066 < iter 023 mean 1.109. Best config beats iter 023
  on **0/3** datasets — KILL #1 fires hard (criterion required ≥1/3).
- **KILL #2 (monotonic regression)**: Sharpe falls monotonically with
  NTSD weight 5% → 20% on **all 3 datasets** (lh_56y 1.092→1.025,
  vt_real 0.980→0.905, ndx_real 1.125→1.069). Same structural failure
  mode as iter 014 VXUSSIM intl-equity overlay.
- **Why score=WINNER 90/100 anyway**: NEW SPY-only mandate scores
  versus SPY (not iter 023). The portfolio still beats SPY on all 3
  datasets — but the **sleeve substitution fails**, taking iter 023
  backwards. The 90 score reflects the iter 023 base's quality, not
  NTSD's contribution.
- **Decision**: NTSD sleeve **CLOSED** for Phase 2. F4 Global Stacking
  finalist (iter 035) **cannot proceed** — recommended fallback per
  SWEEP_PLAN §"Phase 2 fallback rules": skip iter 035, F4 = "global
  stacking not viable", consistent with iter 014/015 closures.
- The iter 023 wrapper's NTSX 60% IEF leg already provides duration
  diversification; adding NTSD's 60% VEA leg means stacking ex-US
  equity beta inside the wrapper, but the synth shows no Sharpe edge
  — VEA's risk-adjusted returns since 1986 don't outperform SPY+IEF
  on the long-history split. Citation `[ilmanen_expected_returns,
  ch.19]` intl diversification is dataset-dependent; the lh_56y window
  rewards US large-cap.
