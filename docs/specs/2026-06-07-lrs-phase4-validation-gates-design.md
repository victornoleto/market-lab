# Design — LRS Phase 4 (Mandate Validation Gates, Diagnostic)

- **Date:** 2026-06-07
- **Status:** Design approved (brainstorming). Research-only, **diagnostic**.
- **Scope:** Run the canonical mandate §5 overfit-gate suite on the LRS final
  geometry and record an honest pass/fail per base. This is **not** a promotion.
- **Mandate:** Maintenance mode. No deploy, no paper-trade label, no capital
  allocation, no mandate change — regardless of outcome `[advances_fin_ml,
  p.208-211]`.

---

## 1. Context & framing

The LRS restart established (Phases 0–3C) that **exposure geometry** (target
leverage + diversified risk-off + realized-vol throttle, Phase 2) is the real
driver; risk-on confirmation filters (3A), alternative regime forms (3A-2), and
lookback window/adaptivity (3C) do not beat the plain SMA200-level base. Phase 4
is the **diagnostic validation** step from `lrs/NEXT_STEPS.md`: *"Não é promoção;
é diagnóstico para saber se a família merece continuar."* Given the repo's
113/113 honest-FAIL history and 3C's fragility finding, the honest prior is that
the family **fails** the gates — most likely DSR at a high, honest `n_trials`.
Phase 4 records that verdict faithfully; it does not stop being research-only.

## 2. What is validated

The **6 bases at SMA200** (the Phase 2 top + 2 one-lever neighbours per branch,
identical to Phase 3A/3A-2/3C `BASE_SPECS`): 3 SPY + 3 QQQ. Each base is taken at
its **own best-score lag** over `0..5` (re-derived at SMA200, fixed window 200).
- Gates **G2–G7** are per-base (7 series-level tests).
- Gate **G1 (PBO)** is per-branch (one value applied to that branch's 3 bases).
- Verdict per base = `G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6 ∧ G7` (hard-block, zero
  bypass). CAGR/MDD remain warning-only tiers `[advances_fin_ml, p.208-211]`.

## 3. The seven gates (canonical core, mandate §5)

All wrap `market_lab.backtest.validation` (canonical) via a thin
`lrs/lib/validation.py`; `lrs/` imports no `studies/` code.

| Gate | Definition | Pass condition | Source |
|---|---|---|---|
| **G1 PBO** | CSCV over the per-branch trial matrix (§4); `pbo(returns_matrix, n_blocks=10)` | `pbo < 0.5` | `[advances_fin_ml, p.208-211]` |
| **G2 DSR** | `dsr(returns, n_trials=3876)` → `p_value = 1 − DSR` | `p < 0.05` | `[advances_fin_ml, p.273-275]` |
| **G3 Walk-forward** | `walk_forward_splits` → ≥8 windows; per-window OOS **strategy minus underlying after-tax** total return; per-window MDD reported as **diagnostic only (no cap)** | `≥ 6/8` windows beat underlying | `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.211-216]` |
| **G4 OOS single-block** | last 30% of dates | OOS Sharpe > 0 **and** OOS after-tax beats underlying | `[testing_tuning, p.327-335]` |
| **G5 FWD stress** | post-`2020-01-01` block | Sharpe > 0 | `[testing_tuning, p.318-320]` |
| **G6 Bootstrap** | stationary block bootstrap of annualized Sharpe, **99.9% CI** (mandate, not gates_letf's 99%), block≈21, ≥5000 resamples, fixed seed | CI-low > 0 | `[advances_fin_ml, p.211-216]` |
| **G7 Cross-lib** | after-tax CAGR via pandas path vs an independent numpy path | `|Δ| ≤ 3pp` | `[advances_fin_ml, p.208-211]` |

WF design: `is_size`/`oos_size`/`step` chosen so the long series yields ≥8
non-overlapping OOS windows (e.g. is ≈ 8y, oos ≈ 4y, step = oos). G3 reuses the
core `walk_forward_gate` by passing the **relative** (strategy − underlying)
per-window returns with `max_drawdown=1.0` (cap disabled), so "profitable" means
"beat the underlying after-tax" `[testing_tuning, p.318-320]`.

## 4. PBO trial matrix (per branch)

Re-simulate the **Phase 2 exposure-geometry grid at SMA200** — the search where
the bases were selected: 8 target leverages × 5 risk-off sleeves × 5 vol filters
≈ 200 configs/branch, at a **single fixed lag** (lag = 0; lag is an execution
nuisance, not a selection dimension). This yields the `T×N` after-tax returns
matrix `pbo()` consumes; the 6 bases are members of it. PBO is reported per
branch and applied to that branch's bases.

## 5. DSR `n_trials` = 3876 (honesty lever)

Direct lineage that produced/refined the pick:
`Phase 2 (2400) + Phase 3A (324) + Phase 3A-2 (216) + Phase 3C (936) = 3876`.
Documented as a constant with the breakdown. Caveat recorded in the report: the
spun-off `studies/lrs/`/`letf-lab` lookback sweeps are **excluded** (separate
repo), so the truly-honest count is higher — 3876 is the defensible in-repo
lineage figure `[advances_fin_ml, p.273-275]`.

## 6. Reuse architecture

- **New** `lrs/lib/validation.py`: thin wrappers `gate_pbo`, `gate_dsr`,
  `gate_walk_forward`, `gate_oos`, `gate_fwd_stress`, `gate_bootstrap`,
  `gate_cross_lib`, and `run_gate_suite(...)` returning per-gate dicts +
  `overall_pass`. Imports `market_lab.backtest.validation` only (canonical); no
  `studies/` import (keeps `lrs/` self-contained from `studies/`).
- **New** `lrs/phases/phase04_validation_gates/` (`__init__.py`, `run.py`,
  `README.md`): reuses `lrs.lib.backtest` to re-simulate (a) each base's daily
  after-tax returns at SMA200/best-lag, and (b) the per-branch PBO grid; then
  calls the gate suite per base and aggregates the verdict.

## 7. Outputs

- `lrs/results/phase04_validation_gates.csv` — per base: G1–G7 values + pass
  flags + overall verdict + n_trials + key metrics.
- `lrs/phases/phase04_validation_gates/REPORT.md` — per-base gate table, overall
  verdict, the family-level conclusion, research-only disclaimer + citations.
- `plots/` — gate pass/fail heatmap (6 bases × 7 gates), WF per-window
  strategy-minus-underlying spread, bootstrap Sharpe distribution with the 99.9%
  CI marked.
- `tests/test_lrs_phase04.py` — TDD on each gate wrapper with synthetic
  pass/fail series (e.g. cross-lib ≈0 delta; DSR fails at high `n_trials`;
  WF passes when ≥6/8 windows beat benchmark; bootstrap CI-low sign).

## 8. Verification

```bash
uv run python -m lrs.phases.phase04_validation_gates.run
uv run pytest tests/test_lrs_phase04.py tests/test_lrs_phase00.py
```

Manual checks: CSV has 6 base rows; each gate value present; overall verdict
consistent with `G1 ∧ … ∧ G7`; DSR uses `n_trials=3876`; PBO matrix size ≈200/branch.

## 9. Decision rule (after run)

- If **no base passes all gates** (the honest prior): record the LRS family as a
  research-only, negative-leaning line and **close/shelve** it pending new
  literature or regime — no mandate change `[advances_fin_ml, p.208-211]`.
- If **some base passes**: re-examine that specific config (still no automatic
  promotion; promotion would need a separate explicit decision under the mandate).

## 10. Citations

- PBO / CSCV, deflated performance — `[advances_fin_ml, p.208-211]`.
- Deflated Sharpe Ratio, `E[max SR]` under `n_trials` — `[advances_fin_ml,
  p.273-275]`.
- Walk-forward / OOS discipline, never iterate after OOS — `[testing_tuning,
  p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.211-216]`.
- Leverage as the enemy of compounding (why these gates matter for an LETF line)
  — `[leverage_for_the_long_run, p.4-7]`.
