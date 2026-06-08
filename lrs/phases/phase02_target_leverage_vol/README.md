# Phase 2 - Target Leverage And Volatility Throttle

Run:

```bash
uv run python -m lrs.phases.phase02_target_leverage_vol.run
```

Outputs:

- `REPORT.md`
- `../../results/phase02_target_leverage_vol.csv`
- `plots/`

This phase keeps the SMA200 weekly LRS signal and selected Phase 1 risk-off
sleeves, then varies target leverage and simple realized-volatility throttles.
The goal is to reduce drawdown before adding broad technical-indicator votes
`[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`.
