# NEXT_STEPS - Static SPY Beater Portfolio

This study is still discovery-only. No portfolio below is validated, deployable, or a
mandate change. The internal core benchmark is now `35% GDESIM / 40% RSSTSIM /
25% ZROZSIM`; the objective is to find something better than this core by rolling
equity dominance, not by minimizing MDD alone `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.

## Current Core Benchmark

- Weights: `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`.
- Full-period 1988-2026: CAGR `15.70%`, MDD `-29.94%`, Calmar `0.524`, terminal
  wealth `265x`.
- Compared with B4 original (`25% NTSXSIM / 25% GDESIM / 25% RSSTSIM / 25% ZROZSIM`),
  it adds about `+1.27pp` CAGR and higher terminal wealth at about `2.02pp` worse MDD.
- Status: internal benchmark/core only, not validated and not deployable.

## Priority 1 - Core-Beater Static GA

Status update: the factor probe with `VBRSIM`, `MTUMSIM` and `EFVSIM` completed in
`results/ga_core_factor_momentum_beater/`. All three seeds selected the original
`35% GDESIM / 40% RSSTSIM / 25% ZROZSIM` core as exact rank 1; factor sleeves did not
improve rolling equity dominance. Treat factor sleeves as rejected for now unless a
new, pre-registered thesis changes the universe or objective `[ml_for_algo_trading,
ch.4 p.82-93]`, `[advances_fin_ml, p.222-223]`.

Run a no-margin monthly-rebalanced GA whose primary target is rolling equity dominance
versus the core.

Universe:

```text
GDESIM, RSSTSIM, KMLMSIM, ZROZSIM,
SPYSIM, SSOSIM, UPROSIM,
QQQSIM, QLDSIM, TQQQSIM,
IEFSIM, CASHX
```

Rules:

```text
Monthly rebalance
Long-only weights in 5% units
Weights sum to 100%
CASHX >= 0; no negative cash or external margin
Embedded ETF leverage allowed and reported
Max active assets: no hard preference for 6; use 8-12 if the GA benefits
```

Primary fitness:

```text
core_relative_wealth_dominance
```

Rank by rolling dominance versus `35/40/25`:

```text
rolling 1/3/5/10/15/20y win-rate vs core
rolling relative wealth p10/median/latest vs core
full-period CAGR spread vs core
Calmar spread vs core
MDD as penalty/guardrail, not primary objective
```

Do not require 95% win-rate in 1y/3y windows; that would likely reject good long-term
return engines. For first discovery, use 5y+ and 10y+ dominance as the real signal.

Expected result:

- Determine whether small sleeves of `SSOSIM/UPROSIM/QLDSIM/TQQQSIM`, `KMLMSIM`,
  `IEFSIM`, or `CASHX` improve rolling equity dominance versus the core.
- Factor proxy sleeves `VBRSIM`, `MTUMSIM` and `EFVSIM` have already been probed and
  did not beat the core.
- If no static candidate beats the core, keep `35/40/25` as the benchmark and move to
  implementation/sensitivity rather than forcing an overfit.

## Priority 2 - Exact Core-Beater Report

For top GA candidates, produce exact rolling/regime reports against:

```text
35/40/25 core
B4 original
SPYSIM buy-and-hold
GA robust historical lead
```

Metrics:

- Full-period CAGR, MDD, Sharpe, Sortino, Calmar, Ulcer index, terminal wealth.
- Rolling 1/3/5/10/15/20y relative wealth vs core: win-rate, min, p05, p10, median,
  latest.
- Rolling 3/5/10/15/20y MDD as diagnostic.
- Regime windows already used in `pareto_regime_report`.

## Priority 3 - Implementation Realism

Run only after a candidate beats the core in exact rolling diagnostics.

- Drag tests: `0.25%`, `0.50%`, `1.00%` annual drag.
- Rebalance frequency: monthly vs quarterly vs yearly.
- Start-date sensitivity: 1988, 1990, 1995, 2000, 2005.
- Remove-one-asset tests: remove `GDESIM`, `RSSTSIM`, `ZROZSIM`, `KMLMSIM`, levered
  equity sleeves, and cash.
- Confirm implementable tickers and tax/broker constraints.

## Priority 4 - Tactical/Swing Overlay Later

Cash can help static monthly rebalance buy assets after declines because rebalancing
restores target weights. Dynamic rules like increasing `TQQQ/UPRO` after drawdowns are
interesting, but they become swing/tactical overlays and should wait until the static
core-beater search is exhausted; otherwise overfit risk rises materially
`[advances_fin_ml, p.208-211]`.

## What Not To Do Next

- Do not use negative `CASHX`; external margin is not operationally available.
- Do not optimize directly for terminal wealth only.
- Do not promote a candidate based on full-period CAGR/MDD without rolling dominance.
- Do not use the leaked Testfol.io bearer token; treat it as compromised.
