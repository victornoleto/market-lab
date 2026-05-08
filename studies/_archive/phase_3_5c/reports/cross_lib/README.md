# Phase 3.5c — Plano B Cross-Library Validation

Validates Plano B V4 (3-leg EW SSO+QLD+UGL) by reproducing it in independent libraries.
Design spec: `docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`.

## Entry points
- `python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 1`
- `python -m reports.phase_3_5c.cross_lib.report` (generates VERDICT.md)

## Top-level output
- `VERDICT.md` — aggregate verdict matrix.
- `per_variant/<id>.md` — per-variant deep dives.
- `errors/` — adapter stacktraces (only on ERROR outcomes).
- `results/stage_{1,2}/<lib>/<variant>/<window>/result.json` — raw RunResult dumps.

Reference design spec is authoritative for tolerances, aggregation rules, and library rationale.
