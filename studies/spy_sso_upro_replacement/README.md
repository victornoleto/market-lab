# SPY/SSO/UPRO Replacement Study

Research-only study for a static or low-turnover SPY replacement using `SPYSIM`, `SSOSIM`, `UPROSIM` and diversifiers from the Testfol.io cache.

Primary goal: beat SPY in long rolling windows, then test whether the result survives practical cadence and Brazil's annual 15% DARF model. The first phase was static because it is easier to maintain and generates less realized-tax turnover than swing strategies; the current verdict favors monthly active risk-on/off after static portfolios failed after-tax equity dominance.

Current practical-taxed verdict: `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly` is the best active row and one of 3 active practical after-tax dominance passes; the best static row is `static L3.00 E60% GLD annual`, but static has 0 dominance passes. A later user-directed static diagnostic (`USER_TESTFOLIO_STATIC_MIX_DIAGNOSTIC_2026-06-12.md`) found two monthly levered/diversified mixes that beat SPY over 1988-2026 but are unattractive versus the current RSC drawdown profile. This is selection only, not validation, deployment or a mandate change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.

Read order:

1. `SPEC.md`
2. `REPORT.md` after running the Phase 1 static grid
3. `PHASE1B_REPORT.md` after running focused robustness
4. `EQUITY_DOMINANCE_REPORT.md` after the objective pivot
5. `PRACTICAL_TAXED_REPORT.md` after practical cadence and annual DARF selection
6. `USER_TESTFOLIO_STATIC_MIX_DIAGNOSTIC_2026-06-12.md` for the user-provided Testfol.io static mixes
7. `results/static_exact_finalists.csv`
8. `results/phase1b_exact_finalists.csv`
9. `results/equity_dominance_candidates.csv`
10. `results/practical_taxed_candidates.csv`

No output here authorizes deployment or mandate changes.
