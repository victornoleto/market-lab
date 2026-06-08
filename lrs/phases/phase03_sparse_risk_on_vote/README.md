# Phase 3A - Sparse Risk-On Confirmation Vote

Run:

```bash
uv run python -m lrs.phases.phase03_sparse_risk_on_vote.run
```

Outputs:

- `REPORT.md`
- `../../results/phase03_sparse_risk_on_vote.csv`
- `plots/`

This phase keeps the Phase 2 exposure geometry (SMA200 weekly LRS signal +
realized-vol throttle, target leverage, diversified risk-off sleeves) fixed and
asks a single question: does adding *one* structurally distinct risk-on
confirmation filter improve the frontier versus a `none` control?

Signal per row:

```
signal = sma_signal & vol_gate(base.vol) & confirm_gate(filter)
```

Grid (pre-registered): 2 branches x 3 branch-specific bases x 9 filters x lag
`0..5` = 324 rows. Filters are tested one-at-a-time (no vote-of-K combination
yet); that is deferred to a later phase only if more than one family beats the
control `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.

Filter families and citations:

- `clenow` - annualized exp-regression slope x R^2 > 0 `[stocks_on_the_move, p.70-77, p.98]`
- `roc` - N-day rate of change > 0 `[stocks_on_the_move, p.58, p.60]`
- `hysteresis` - asymmetric SMA200 entry/exit band to filter whipsaws `[trading_systems_methods, p.383]`
- `adx` - close-only ADX trend-strength proxy `[trading_systems_methods, p.387]`

ADX caveat: the cache stores close-only equity curves (no intraday high/low), so
ADX is a degraded proxy. See `lrs/lib/indicators.adx_close_only` for the exact
approximation. Research-only: no deploy, no paper-trade label, no mandate change.
