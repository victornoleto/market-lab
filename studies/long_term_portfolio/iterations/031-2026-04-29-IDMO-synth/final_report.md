# Iter 031 — Final Report — `IDMO-synth`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **WINNER 90/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 95/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `idmo_lite`

Weights:

```json
{
  "NTSXSIM": 0.225,
  "GDESIM": 0.25,
  "KMLMSIM": 0.325,
  "TLTSIM": 0.15,
  "IDMOSIM": 0.05
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.107 | 11.05% | 20.48% | 7/7 | 4.62e-09 |
| **vt_real** | 0.984 | 10.09% | 18.99% | 7/7 | 1.04e-03 |
| **ndx_real** | 1.140 | 10.88% | 12.43% | 7/7 | 2.63e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| idmo_lite | 1.107 | 0.984 | 1.140 |
| idmo_mod | 1.090 | 0.952 | 1.123 |
| idmo_med | 1.066 | 0.916 | 1.100 |
| idmo_heavy | 1.038 | 0.879 | 1.074 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.107 | +0.427 | [OK] |
| vt_real | 0.900 | 0.950 | 0.984 | +0.084 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.140 | +0.240 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **IDMOSIM** = `VEASIM + 0.60 × UMD_KF − 60bps/y` — INCOMPLETE.
  **Biggest caveat**: uses **US UMD_KF** as proxy for intl momentum
  factor (academic intl UMD daily data not in our cache). Real intl
  momentum factor has ~0.5-0.7 correlation with US UMD per Asness-
  Moskowitz-Pedersen 2013 — our synth may **overstate** IDMO's Sharpe
  contribution by 10-30%. Real IDMO live Sharpe ~0.5-0.7 since 2017
  inception (smaller AUM, less factor capture vs SPMO). Standalone
  synth Sharpe 0.726 is consistent with real IDMO live but should be
  interpreted with the US-UMD-as-intl-proxy caveat in mind.

## Lesson

**KILL #3 OK (0.726 < 1.5). KILL #1 cosmetic survival (1/3, +0.005).
KILL #2 FIRES.**

- **KILL #3 (no-free-lunch synth) PASS**: IDMO standalone Sharpe =
  **0.726** (well below 1.5). Matches real IDMO live Sharpe range
  0.5-0.7 since 2017 inception — synth scaling is honest despite
  the US-UMD-as-intl-proxy caveat.
- **KILL #1 (no-positive-config) survives narrowly**: best config
  (`idmo_lite`, 5%) Sharpe = 1.107 / 0.984 / 1.140 vs iter 023 baseline
  1.189 / 1.004 / 1.135. Beats iter 023 on **1/3 datasets**: ndx_real
  +0.005 (cosmetic), lh_56y −0.082, vt_real −0.020. Mean Sharpe 1.077
  < iter 023 mean 1.109. Threshold ≥1/3 narrowly passes.
- **KILL #2 (monotonic regression) FIRES**: Sharpe falls monotonically
  with IDMO weight 5% → 20% on ALL 3 datasets:
  - lh_56y 1.107 → 1.038 (Δ −0.069)
  - vt_real 0.984 → 0.879 (Δ −0.105)
  - ndx_real 1.140 → 1.074 (Δ −0.066)
  Different from SPMO (iter 030) which had non-monotonic ndx_real.
- **Why score=WINNER 90/100**: NEW SPY-only mandate; iter 023 base
  with 5% IDMO still beats SPY on all 3 datasets. Score reflects
  iter 023 base quality — NOT IDMO's contribution.
- **Decision**: IDMO sleeve **marginal/closed substantively**. The
  +0.005 ndx_real edge is cosmetic; KILL #2 monotonic decline says
  IDMO weight should be at most 5%, where the edge is below noise.
  Compared to SPMO (iter 030, +0.032 ndx_real edge, non-monotonic
  reward up to 15%): SPMO is empirically dominant in the deployable-
  momentum sleeve battle.
- For Phase 2: SPMO at 5-15% remains the recommended momentum sleeve
  for F2/F3/F6. IDMO **NOT** recommended for Phase 2 (substantively
  weaker than SPMO at every weight tested). F5/F6 finalists lose this
  sleeve too — only AVEM remains to be tested for Global side.
- Citation `[ilmanen_expected_returns, ch.19]` intl factor diversification
  not borne out empirically in this sleeve format. The intl momentum
  premium may be real (per AMP 2013), but the synth's US-UMD-as-intl
  proxy + 60bps drag + iter 023's KMLM crisis-alpha overlap leaves
  no isolable edge.
