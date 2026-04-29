# Iter 030 — Final Report — `SPMO-synth`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 84/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 89/100** — `winner_conditions_met=True`.

**Primary citation**: [stocks_on_the_move, p.21-30]

---

## Selected config: `spmo_lite`

Weights:

```json
{
  "NTSXSIM": 0.225,
  "GDESIM": 0.25,
  "KMLMSIM": 0.325,
  "TLTSIM": 0.15,
  "SPMOSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.117 | 11.29% | 20.75% | 6/7 | 3.15e-09 |
| **vt_real** | 1.009 | 10.39% | 18.27% | 6/7 | 7.17e-04 |
| **ndx_real** | 1.167 | 11.19% | 12.23% | 6/7 | 1.77e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| spmo_lite | 1.117 | 1.009 | 1.167 |
| spmo_mod | 1.113 | 1.003 | 1.175 |
| spmo_med | 1.106 | 0.993 | 1.179 |
| spmo_heavy | 1.096 | 0.980 | 1.177 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.117 | +0.437 | [OK] |
| vt_real | 0.900 | 0.950 | 1.009 | +0.109 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.167 | +0.267 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **SPMOSIM** = `SPYSIM + 0.60 × UMD_KF − 35bps/y` — INCOMPLETE.
  UMD_KF = Ken French momentum daily factor (long-short academic
  portfolio, full CRSP universe). 0.60 capture coefficient per
  Frazzini-Israel-Moskowitz 2018 long-only constraint estimate. Real
  SPMO uses S&P 500 universe (top-100 cross-sectional momentum
  filter) — narrower universe than KF UMD; capture coefficient may
  differ. 35bps/y = SPMO TER + estimated implementation drag. Since
  inception (2015-10) real SPMO live Sharpe is ~0.7-0.9 — directly
  comparable to standalone synth Sharpe 0.828 logged at runtime.

## Lesson

**KILL #3 OK (0.828 < 1.5). KILL #1 SURVIVES (2/3 beats iter 023).
KILL #2 does NOT fire (ndx_real non-monotonic).**

- **KILL #3 (no-free-lunch synth) PASS**: SPMO standalone Sharpe =
  **0.828** (well below 1.5 threshold). Matches real SPMO live Sharpe
  range 0.7-0.9 since 2015 inception — synth is honest.
- **KILL #1 (no-positive-config) SURVIVES**: best config (`spmo_lite`,
  5% SPMO) Sharpe = 1.117 / 1.009 / 1.167 vs iter 023 baseline 1.189
  / 1.004 / 1.135. Beats iter 023 on **2/3 datasets** (vt_real +0.005
  marginal, ndx_real **+0.032** substantive). lh_56y −0.072 (worst on
  long-history; KMLM-FFmom splice is the culprit).
- **KILL #2 (monotonic regression) DOES NOT FIRE**: ndx_real Sharpe
  is **non-monotonic** with SPMO weight: lite=1.167 → mod=1.175 →
  med=1.179 → heavy=1.177 (slight inverted-U, peak at 15%). lh_56y
  and vt_real do fall monotonically (1.117→1.096 and 1.009→0.980),
  but the criterion required **all 3 datasets** monotonic — KILL #2
  does not fire.
- **First positive sleeve in Phase 1.** Confirms iter 016 UMD-academic
  +signal in deployable form. Best ndx_real Sharpe across the grid
  is at SPMO 15% (1.179), suggesting the "right" weight for Phase 2
  is between 5-15%. Long-history (lh_56y) drag −0.072 is consistent
  with iter 016's findings — momentum factor lags KMLM crisis-alpha
  on the 1970-1986 window where KF UMD splice dominates KMLM.
- **Decision**: SPMO sleeve **WINS Phase 1** (first sleeve to survive
  both KILL #1 and KILL #2). Recommended for Phase 2:
  - F2 US Factor-only (iter 033): include SPMO at 10-15% weight
  - F3 US Hybrid (iter 034): include SPMO at 5-10% weight (smaller
    since stack already included)
  - F6 Global Hybrid (iter 037): include SPMO at low weight (5%)
- Citation `[stocks_on_the_move, p.21-30]` Clenow + Jegadeesh-Titman
  1993 confirmed empirically: cross-sectional momentum delivers a
  modest +signal at 1× notional even in the iter 023 wrapper-heavy
  context. Captures ~40% of iter 016's UMD-academic edge in
  deployable form (consistent with FIM 2018 capture estimates).
