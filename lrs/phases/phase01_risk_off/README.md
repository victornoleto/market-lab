# Phase 1 - Risk-Off Alternatives

Run:

```bash
uv run python -m lrs.phases.phase01_risk_off.run
```

Outputs:

- `REPORT.md`
- `../../results/phase01_risk_off.csv`
- `plots/`

This phase keeps the original SMA200 weekly LRS signal and changes only the
risk-off sleeve. The goal is to reduce drawdown before adding risk-on indicator
complexity `[leverage_for_the_long_run, p.4-7]`, `[leverage_for_the_long_run,
p.13]`.
