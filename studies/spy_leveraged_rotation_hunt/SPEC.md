# SPEC — SPY Leveraged Rotation Hunt

## Research Question

Find whether an S&P 500 leveraged-ETF rotation family can beat `SPY buy_hold` on
CAGR, Sharpe/Sortino and MaxDD in long-history data, while preserving a clear
ranking by risk and temporal robustness.

## Data

Stage 0 uses testfolio long-history close series:

- `SPYSIM` as `SPY`
- `SSOSIM` as `SSO`
- `UPROSIM` as `UPRO`
- `CASHX` as cash / T-bill proxy
- `ZROZSIM` as long-duration bond diagnostic

This is discovery data. Any deploy claim requires independent real-inception
confirmation and cross-library checks.

## Baselines

Baseline strategies:

- `SPY buy_hold`
- `SSO buy_hold`
- `UPRO buy_hold`
- `LRS SPY->SSO`, `SPY > SMA200`, else `CASHX`
- `LRS SPY->UPRO`, `SPY > SMA200`, else `CASHX`
- T3d-style vote `SPY->SSO/UPRO`
- T3d-style vote `SSO->SSO/UPRO`

The 200-day SMA follows the canonical LRS source
`[leverage_for_the_long_run, p.13]`; Gayed reports broad MA robustness around the
same family and turnover rationale for 200 days `[leverage_for_the_long_run,
p.16]`. LETF volatility-decay filters use realized-volatility logic motivated by
the leverage drag mechanism `[leverage_for_the_long_run, p.5-7]`.

## GA Grammar

Each gene contains:

- signal asset: `SPY` or `SSO`
- normal risk-on mix: weight in `UPRO`; remainder in `SSO`
- rearm risk-on mix: weight in `UPRO` after a post-crash rearm event
- entry vote over four components: long SMA, short SMA, realized-vol gate, AR(1)
- post-crash rearm geometry: `T_crash`, `D_arm`
- risk-off bond mix: `CASHX`/`ZROZSIM`

Post-crash rearm follows the iter030-style state machine: open a rearm window
when the entry signal flips from OFF to ON after a sufficiently long OFF stretch
`[leverage_for_the_long_run, p.6-7]`.

## Evolutions

1. `evo01_spy_sso_repair`: `SPY` signal, mostly `SSO`, drawdown repair.
2. `evo02_spy_upro_performance`: `SPY` signal, `UPRO` performance-first.
3. `evo03_sso_self_balanced`: `SSO` self-signal, balanced score.
4. `evo04_execution_lag_robust`: average behavior under extra lag `0/1/2`.
5. `evo05_diversity_low_corr`: lower correlation to `SPY buy_hold`.
6. `evo06_conservative_drawdown`: conservative drawdown-focused variant.

GA fitness is discovery-only. PBO/DSR remain post-search hard gates
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Success Criterion

Initial success means at least one candidate beats `SPY buy_hold` on CAGR,
Sharpe/Sortino and MaxDD in the long-history panel, or the report documents that
the tested families did not produce such a candidate.

This is not a deployment criterion. Any promising candidate must then pass
OOS/FWD/WF/bootstrap/PBO/DSR with cumulative trial accounting
`[advances_fin_ml, p.222-223]`.
