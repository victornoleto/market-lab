# Phase 4 - Mandate Validation Gates (DIAGNOSTIC)

Research-only / diagnostic. Runs the canonical mandate §5 overfit-gate suite on
the 6 SMA200 bases (3 SPY + 3 QQQ, each at its best-score lag) and records an
honest pass/fail. Per `lrs/NEXT_STEPS.md`: not a promotion - a diagnostic to
decide whether the family deserves to continue. No deploy, no paper-trade label,
no mandate change, regardless of outcome `[advances_fin_ml, p.208-211]`.

Gates (hard-block, zero bypass): G1 PBO<0.5, G2 DSR p<0.05, G3 walk-forward
>=6/8 OOS windows beat underlying (per-window MDD diagnostic, no cap), G4
single-block OOS (last 30%) Sharpe>0 and beats underlying, G5 FWD stress
(post-2020) Sharpe>0, G6 stationary-bootstrap 99.9% CI low of annualized Sharpe
>0, G7 cross-lib CAGR |delta|<=3pp. Verdict = G1 AND ... AND G7. CAGR/MDD are
warning-only tiers, not gates.

- Gate wrappers: `lrs/lib/validation.py` (thin layer over the canonical
  `market_lab.backtest.validation`; no `studies/` import).
- DSR `n_trials = 3876` (direct lineage: Phase 2 2400 + 3A 324 + 3A-2 216 + 3C 936).
- PBO trial matrix = Phase 2 geometry grid at SMA200 (8 leverages x 5 risk-off x
  5 vol = 200 configs/branch, fixed lag) - the search where the bases were chosen.

Run:

```bash
uv run python -m lrs.phases.phase04_validation_gates.run
uv run pytest tests/test_lrs_phase04.py tests/test_lrs_phase00.py
```

Outputs: `REPORT.md`, `../../results/phase04_validation_gates.csv`, `plots/`.

This phase does not authorize deployment, paper trading or a mandate change.
