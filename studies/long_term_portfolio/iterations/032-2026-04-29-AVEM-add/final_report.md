# Iter 032 — Final Report — `AVEM-add`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **WINNER 90/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 95/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `avem_lite`

Weights:

```json
{
  "NTSXSIM": 0.225,
  "GDESIM": 0.25,
  "KMLMSIM": 0.325,
  "TLTSIM": 0.15,
  "AVEMSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.082 | 11.05% | 21.86% | 7/7 | 2.44e-07 |
| **vt_real** | 0.969 | 10.05% | 20.27% | 7/7 | 1.19e-03 |
| **ndx_real** | 1.115 | 10.64% | 12.53% | 7/7 | 3.54e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avem_lite | 1.082 | 0.969 | 1.115 |
| avem_mod | 1.053 | 0.928 | 1.083 |
| avem_med | 1.017 | 0.883 | 1.046 |
| avem_heavy | 0.975 | 0.836 | 1.005 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.082 | +0.402 | [OK] |
| vt_real | 0.900 | 0.950 | 0.969 | +0.069 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.115 | +0.215 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 27
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVEMSIM** = `VWOSIM + 125bps/y tilt premium` — INCOMPLETE.
  VWOSIM is Vanguard FTSE Emerging Markets (passive, no quality
  screen). 125bps/y tilt premium is published Avantis EM estimate
  (highest of AV* family, reflecting EM market inefficiency).
  Stacks 3 caveats: (1) VWOSIM as EM proxy, (2) 125bps tilt assumption,
  (3) EM data quality / survivorship issues 1994-2010 era.
- **WINDOW CAVEAT (CRITICAL)**: VWOSIM starts **1994-05-04**. Effective
  lh_56y window in this iter: **1994-05-05 → 2026-04-17 = 32y**, NOT
  56y. Comparisons vs iter 023's 56y lh_56y Sharpe (1.189) are on
  **different time windows**. Verified at runtime: returns series for
  selected config has 8042 daily obs for lh_56y (32y), 4498 for vt_real,
  4078 for ndx_real. The vt_real (2008+) and ndx_real (2010+) windows
  are unaffected by the bottleneck.

## Lesson

**Both KILL #1 and KILL #2 fire — sleeve closed (with window caveat).**

- **KILL #1 (no-positive-config) FIRES**: best config (`avem_lite`,
  5% AVEM) Sharpe = 1.082 / 0.969 / 1.115 vs iter 023 baseline 1.189
  / 1.004 / 1.135. Loses on **3/3 datasets** (Δ −0.107 / −0.035 /
  −0.020). Mean Sharpe 1.055 < iter 023 mean 1.109.
  - **Window caveat**: AVEM iter's lh_56y is 32y (1994-2026), vs iter
    023's 56y. To make a fair lh_56y comparison would require re-
    running iter 023 on the same 32y intersection. Worth flagging:
    1994-2026 is a regime where US large-cap dominated EM by ~3-4pp/yr
    CAGR, so this 32y window is biased against EM-tilted portfolios.
    Even with that caveat, the vt_real (−0.035) and ndx_real (−0.020)
    losses are on identical windows to iter 023 — those losses are
    apples-to-apples.
- **KILL #2 (monotonic regression) FIRES**: Sharpe falls monotonically
  with AVEM weight 5% → 20% on ALL 3 datasets:
  - lh_56y 1.082 → 0.975 (Δ −0.107)
  - vt_real 0.969 → 0.836 (Δ −0.133)
  - ndx_real 1.115 → 1.005 (Δ −0.110)
  Steepest monotonic decline of all 6 Phase 1 sleeves tested.
- **Why score=WINNER 90/100**: NEW SPY-only mandate; 5% AVEM in iter
  023 base still beats SPY on all 3 datasets — base quality drives
  the score.
- **Decision**: AVEM sleeve **CLOSED**. Combined with iter 029 AVDV
  closure, **all 3 Avantis factor sleeves (AVUV/AVDV/AVEM) failed to
  improve iter 023**. F5 Global Factor-only (iter 036) effectively
  cannot proceed with non-momentum factors — only SPMO/IDMO momentum
  remain (and IDMO failed too). **F5 should be skipped or scaled
  back to a thin SPMO-only construction.**
- F6 Global Hybrid (iter 037): only the 5% momentum sleeve from SPMO
  remains as a positive contributor — geographic diversification
  (NTSD, AVDV, AVEM) all failed independently. F6 likely degenerates
  to "iter 023 + 5-15% SPMO" which is essentially F3.
- Citation `[ilmanen_expected_returns, ch.19]` EM diversification not
  borne out empirically against the iter 023 levered stack on the
  available 32y window. EM 2000-2007 boom (the regime where AVEM
  would shine) is not captured by VWOSIM's 1994 start adequately +
  iter 023 already has GDE gold-equity hybrid which provides
  alternative-asset diversification.
