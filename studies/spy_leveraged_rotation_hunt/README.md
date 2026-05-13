# SPY Leveraged Rotation Hunt

Research-only study for S&P 500 leveraged-ETF rotation strategies using
`SPY`, `SSO` and `UPRO` long-history testfolio series.

The study is a conceptual fork of `studies/technical_signal_vote_hunt/`, but its
first-order question is narrower: can an S&P 500 based rotation beat `SPY`
buy-and-hold on return, risk and temporal robustness without relying on Nasdaq
100 exposure?

No candidate in this folder is deploy-authorized. Any promising candidate must
pass OOS/FWD/WF/bootstrap/PBO/DSR with cumulative trial accounting before it can
be treated as more than discovery evidence `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Scope

Primary benchmark:

- `SPY buy_hold`

Secondary benchmarks:

- `SSO buy_hold`
- `UPRO buy_hold`
- canonical LRS `SPY > SMA200 -> SSO/UPRO`, else `CASHX`
- T3d-style vote variants using `SPY` as underlying signal
- T3d-style vote variants using `SSO` as LETF self-signal

## Commands

Baseline report:

```bash
uv run python -m studies.spy_leveraged_rotation_hunt.runners.run_baseline_report
```

GA evolutions:

```bash
uv run python -m studies.spy_leveraged_rotation_hunt.runners.run_spy_repair_ga_evolutions \
  --case all \
  --population 96 \
  --generations-per-case 35 \
  --elite 16 \
  --seed 91
```

Outputs:

- `reports/baseline/REPORT.md`
- `reports/GA_EVOLUTION_REPORT.md`
- `results/ga_evolutions/*/tables/`

## Interpretation Rule

The study explicitly separates two mechanisms:

- **Underlying-signal:** signal on `SPY`, execution in `SSO`/`UPRO`.
- **LETF-self-signal:** signal on `SSO`, execution in `SSO`/`UPRO`.

The former is conceptually closer to Gayed's LRS framing
`[leverage_for_the_long_run, p.13]`. The latter may be economically useful, but
must be labeled as self-regime because the levered ETF's own price/volatility
state drives exposure `[leverage_for_the_long_run, p.5-7]`.
