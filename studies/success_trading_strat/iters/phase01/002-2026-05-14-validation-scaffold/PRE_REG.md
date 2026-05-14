# PRE_REG — 002 validation scaffold

## Hypothesis

Infrastructure-only iteration: add a reusable validation scaffold for IS MCPT and
WF-MCPT so future strategy iterations can pre-register one hypothesis family and
run the same anti-overfit process consistently. This tests plumbing, not market
edge `[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`.

## Data

No market data is required for the iteration verdict. Unit tests use synthetic
positive price paths only.

## Configs

No strategy configs are evaluated. `cumulative_n_trials` remains `0` before and
after this iteration `[advances_fin_ml, p.222-223]`.

## Gates

- Static checks: Python compile of the new helper.
- Unit checks: focused pytest for scaffold behavior.
- Full-suite smoke: pytest collection.

## Kill Rules

- If the scaffold cannot preserve no-overlap walk-forward windows, stop.
- If MCPT/WF-MCPT p-values are not deterministic under seed, stop.
- If this iteration accidentally evaluates a strategy hypothesis, mark the result
  invalid and increment trial accounting.

## Expected Verdict

`infrastructure_only` unless the scaffold fails verification.
