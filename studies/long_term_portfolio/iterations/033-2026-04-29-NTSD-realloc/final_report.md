# Iter 033 — Final Report — `NTSD-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 81/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 91/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.5, p.10]

---

## Selected config: `ntsd10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "NTSDSIM": 0.1,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.101 | 11.00% | 23.29% | 7/7 | 1.55e-09 |
| **vt_real** | 0.946 | 9.56% | 19.15% | 6/7 | 8.45e-04 |
| **ndx_real** | 1.109 | 10.33% | 12.43% | 6/7 | 1.83e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| ntsd10_subNTSX | 1.072 | 0.956 | 1.108 |
| ntsd10_subGDE | 1.101 | 0.946 | 1.109 |
| ntsd10_subKMLM | 1.023 | 0.937 | 1.115 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.101 | +0.421 | [OK] |
| vt_real | 0.900 | 0.950 | 0.946 | +0.046 | [--] |
| ndx_real | 0.900 | 0.950 | 1.109 | +0.209 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **NTSDSIM** = `0.90 SPYSIM + 0.60 VEASIM − 75bps/y`. INCOMPLETE — active management unmodeled (per WisdomTree NTSD prospectus 2026-03-19, NTSD allocates 90% to SPY equivalent + 60% to VEA-like intl developed futures with cash-collateral roll cost ~75bps/y).

## Substitution source comparison (fixed 10% NTSD weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.1008 | 0.9461 | 1.1089 | −0.088 / −0.058 / −0.026 |
| subNTSX | 15% | 25% | 35% | 1.0716 | 0.9562 | 1.1077 | −0.117 / −0.048 / −0.027 |
| subKMLM | 25% | 25% | 25% | 1.0225 | 0.9369 | 1.1149 | −0.166 / −0.067 / −0.020 |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on 0/3 datasets.**

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 027 best (`ntsd_lite_2055`, 5%, sub NTSX+KMLM 50/50) | Phase 1B iter 033 best (`ntsd10_subGDE`, 10%, sub GDE) |
|---|---|---|
| Sharpe lh_56y | 1.092 | 1.101 |
| Sharpe vt_real | 0.980 | 0.946 |
| Sharpe ndx_real | 1.125 | 1.109 |
| Δ vs iter 023 | −0.097 / −0.024 / −0.010 | −0.088 / −0.058 / −0.026 |
| Datasets beating 023 | 0/3 | 0/3 |

Phase 1B `subGDE` at 10% slightly improves lh_56y (+0.009) but **degrades both vt_real (−0.034) and ndx_real (−0.016)** vs Phase 1A best. Net: NO sub source under 10% NTSD beats iter 023 on any dataset.

## Lesson

**KILL #1 (no-positive-config) ✅ FIRED again under all 3 sub sources.** No config beats iter 023 on any dataset (criterion ≥1/3). Phase 1A failure is **not** a substitution-source artifact — it is structural sleeve subordination.

- **Best sub source**: `subGDE` (selected by max mean(Sharpe / SPY_Sharpe)). Reduces lh_56y drag relative to 1A by absorbing the NTSD cut from GDE rather than splitting NTSX/KMLM equally.
- **Worst sub source**: `subKMLM` (lh_56y −0.166, steepest drop). Confirms iter 023's KMLM 35% is the load-bearing crisis-alpha sleeve; cutting KMLM is structurally costly on long-history.
- **vt_real and ndx_real cluster within ~0.02 Sharpe** across sub sources — NTSD's intl-developed equity exposure is the binding cost on live windows regardless of which sleeve is reduced.
- **NTSD sleeve closure REAFFIRMED.** F4 Global Stacking finalist (iter 035) cannot proceed via NTSD-stacking alone; combined with iter 014 (VXUSSIM) and iter 015 (NTSI/NTSE) closures, intl-equity diversification at 1× notional is decisively dead in the lh_56y framework.
- Citation `[risk_parity, ch.5, p.10]` Carlson cap-efficient framework is honest; the issue is not the framework but the asset class.
