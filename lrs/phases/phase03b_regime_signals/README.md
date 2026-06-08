# Phase 3A-2 - Alternative Regime Signals (Replacement)

Research-only. Tests alternative regime signals as **replacements** for the
Gayed `price > SMA200` trend gate, head-to-head against the SMA200 control over
the Phase 2 exposure geometry. Motivated by the Phase 3A finding that a
trend-hold filter ANDed onto `price > SMA200` can only further restrict risk-on
(a hysteresis band was identical to `none` in 36/36 configs); to test a trend
mechanism it must REPLACE the SMA gate `[trading_systems_methods, p.939]`.

Signal per row: `G(underlying) & vol_gate(base.vol)`, where `G` is the regime
form. Lookback fixed at 200 across all forms to isolate signal form from window
(the window question is Phase 3C's).

Grid: 2 branches x 3 branch-specific bases x 6 regime forms x lag `0..5` = 216
rows. Regime forms: SMA200 control `[leverage_for_the_long_run, p.13]`, EMA200
`[systematic_trading, p.283]`, hyst200 band5%/8% `[trading_systems_methods,
p.383]`, ROC200>0 `[stocks_on_the_move, p.58, p.60]`, Clenow200>0
`[stocks_on_the_move, p.70-77, p.98]`.

Run:

```bash
uv run python -m lrs.phases.phase03b_regime_signals.run
uv run pytest tests/test_lrs_phase03b.py tests/test_lrs_phase00.py
```

Outputs: `REPORT.md`, `../../results/phase03b_regime_signals.csv`, `plots/`.

This phase does not authorize deployment, paper trading or a mandate change.
