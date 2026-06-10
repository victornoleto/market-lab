# Phase 8 — Final Mandate Gate Suite on the Round Survivors (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change — **even a 7/7 pass** only makes the config
> eligible for a separate mandate §7 decision process. Mandate §1 unchanged.

## Trigger and configs (user decision, 2026-06-10)

The user chose the Phase 7 round's two natural survivors for validation:

1. **`spy_7a_ensemble`** — 7A ensemble multi-lookback on `spy_alt_off`
   (`L 2.00`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, vol `RV21 <= 30%`),
   window set `narrow {150,175,200,225}`, lag `2`. Round result: after-tax
   CAGR 14.49%, MDD −43.16%, WF 13/17 (76.5%).
2. **`qqq_7d_quadratic`** — 7D quadratic vol-target on the QQQ headline
   geometry (`L_max 1.75`, risk-off `40 ZROZ / 40 GLD / 20 IEF`),
   `σ_target 40% / RV21`, lag `2`. Round result: after-tax CAGR 19.53%,
   MDD −42.63%, WF 8/11 (72.7%).

**Honest prior, recorded before running:** QQQ at 8/11 (72.7%) is below the
G3 ≥75% bar and is expected to FAIL G3 as-is; it is validated for the record,
not because a pass is likely. SPY at 13/17 nominally clears G3 but must
survive the other six gates with the full-lineage trial count.

## Suite (mandate §5, hard-block, zero bypass)

Canonical wrappers from `lrs/lib/validation.run_gate_suite`, identical
thresholds and geometry to Phase 4 `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`:

| Gate | Definition |
|---|---|
| G1 PBO | CSCV PBO < 0.5; trial matrix = **the winning family grid of the branch** (SPY: the 7A grid restricted to SPY — 3 bases × 2 window sets × 6 lags = 36 configs; QQQ: the 7D grid restricted to QQQ — 3 σ × 2 RV × 6 lags = 36 configs) |
| G2 DSR | p < 0.05 with **n_trials = 4377** (the full in-repo lineage through Phase 7F; the letf-lab spin-off remains excluded and documented as an honest undercount) |
| G3 WF | `is=1764 / oos=756 / step=756`, ≥75% of OOS windows beat the underlying after-tax (Phase 4 geometry verbatim) |
| G4 OOS | last 30%: Sharpe > 0 AND beats underlying |
| G5 FWD | post-2020: Sharpe > 0 |
| G6 Bootstrap | stationary block (21d, 5000 resamples), 99.9% CI low of annualized Sharpe > 0 |
| G7 Cross-lib | pandas vs numpy CAGR within ±3pp |

## Trial accounting

**+0 trials — ledger stays 4377.** Both configs were already counted in the
7A/7D grids; this phase re-evaluates them under the gate suite, it does not
search. Built-in sanity (non-trial): each config's recomputed after-tax
CAGR/MDD must match its Phase 7 CSV row byte-for-byte (max abs diff reported).

## Pre-registered verdict rule

- **7/7 gates on a config** → the line's first formal gate pass, recorded as
  research-only; any allocation discussion is a separate mandate §7 process.
- **Any gate fails** → the config is re-closed with the ledger as-is; the
  family returns to the shelf pending new literature or regime.
- No re-runs, no threshold adjustments, no "quase lá".

## Outputs

`lrs/results/phase08_final_gates.csv`, `REPORT.md`, plots (gate heatmap, WF
OOS spread per config), `tests/test_lrs_phase08.py`.
