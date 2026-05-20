# Final Report - 35/40/25 Core

Status: **internal research winner / discovery-only**. This report does not authorize
deployment, capital reallocation, or a mandate change. The repository remains under
maintenance mode; this study only identifies the best static no-margin benchmark found
so far `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

## Executive Verdict

The strongest practical static portfolio found in this study is:

```text
35% GDESIM / 40% RSSTSIM / 25% ZROZSIM
```

Why this is the internal winner:

- It is the best no-external-margin point found by the local B4-like Pareto search.
- It beats the original B4 reference on CAGR, Calmar and terminal wealth with only a
  modest full-period MDD increase.
- Follow-up GA searches trying to improve it with levered equity, cash, managed
  futures, SCV/value and momentum proxies converged back to this same core.
- Higher-CAGR challengers generally bought less than `~1pp-1.5pp` additional CAGR at
  the cost of much worse drawdown, often `~7pp-15pp` worse MDD.

Important caveat: this is not a formally validated strategy. It is a static benchmark
candidate built from simulated Testfol.io histories and synthetic/stacked ETF proxies.
Before any real-world use, it still needs implementation realism checks, tax/broker
constraints, fee/drag stress, rebalance sensitivity and formal validation discipline
`[advances_fin_ml, p.208-211]`.

## Visual Summary

![Equity curves](results/final_core_report/plots/equity_curves.png)

![Drawdowns](results/final_core_report/plots/drawdowns.png)

![Relative wealth versus SPY](results/final_core_report/plots/relative_wealth_vs_spy.png)

## Portfolio Definition

| Sleeve | Weight | Role |
|---|---:|---|
| `GDESIM` | 35% | Capital-efficient US equity + gold stack |
| `RSSTSIM` | 40% | US equity + managed futures stack |
| `ZROZSIM` | 25% | Long zero-coupon Treasury convexity |

Diagnostic effective exposure per $1 portfolio:

| Exposure family | Approx. notional |
|---|---:|
| US large equity | 0.715 |
| Managed futures | 0.400 |
| Gold | 0.315 |
| Zero-coupon Treasury | 0.250 |
| Embedded cash/financing | -0.680 |

The portfolio itself is long-only with gross weight `1.0` and no negative external
`CASHX`. The negative cash exposure shown above is embedded inside capital-efficient
ETF simulations, not an external margin sleeve `[leverage_for_the_long_run, p.13]`.

## Main Metrics

Common exact window: `1988-01-04..2026-04-17`.

| Portfolio | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal wealth |
|---|---:|---:|---:|---:|---:|---:|
| 35/40/25 core | 15.70% | -29.94% | 1.040 | 1.484 | 0.524 | 265x |
| B4 original | 14.43% | -27.92% | 1.018 | 1.449 | 0.517 | 174x |
| B4-like stacked reference | 13.75% | -28.42% | 0.981 | 1.400 | 0.484 | 139x |
| SPYSIM buy-hold | 11.46% | -55.14% | 0.691 | 0.884 | 0.208 | 64x |
| GA robust lead | 16.81% | -41.20% | 0.972 | 1.338 | 0.408 | 383x |
| GA aggressive lead | 17.97% | -49.37% | 0.972 | 1.351 | 0.364 | 558x |

Reading:

- Versus B4 original, the core adds `+1.27pp` CAGR and about `+52%` terminal wealth
  multiple (`265x` vs `174x`) while worsening MDD by only `~2.02pp`.
- Versus SPY, the core adds `+4.24pp` CAGR, cuts MDD by `~25.20pp`, and raises Calmar
  from `0.208` to `0.524`.
- GA robust/aggressive variants raise terminal wealth, but their MDD cost is large and
  their Calmar is worse; this fails the pragmatic trade-off preference for a durable
  static core.

![CAGR versus MDD](results/final_core_report/plots/cagr_vs_mdd.png)

## Rolling Behavior Versus SPY

The core does not dominate SPY in every short/medium rolling window. Its strength is
long-horizon compounding with materially shallower full-period drawdown.

| Horizon | CAGR p10 | CAGR median | MDD p10 | Relative wealth p10 vs SPY | Relative wealth median vs SPY | Latest relative wealth vs SPY |
|---|---:|---:|---:|---:|---:|---:|
| 3y | 6.42% | 14.28% | -28.02% | -9.84% | +10.97% | -0.07% |
| 5y | 8.71% | 14.55% | -29.89% | -8.59% | +17.97% | +8.72% |
| 10y | 11.49% | 14.42% | -29.94% | -4.25% | +60.20% | -5.99% |
| 15y | 12.37% | 14.46% | -29.94% | +12.88% | +109.54% | +7.24% |

Interpretation:

- The 3y/5y/10y p10 relative-wealth rows remain negative, so this is not a flawless
  rolling dominator.
- The 15y p10 turns positive, and the median 10y/15y relative wealth is strong.
- For a static portfolio, this is acceptable as an internal benchmark, but not enough
  for a validated deployment claim without further stress testing `[testing_tuning,
  p.327-335]`.

![Rolling relative wealth versus SPY](results/final_core_report/plots/rolling_relative_wealth_vs_spy.png)

## Regime Diagnostics

| Regime | Core terminal wealth | Core MDD | Wealth vs SPY |
|---|---:|---:|---:|
| Dot-com drawdown | 0.812x | -29.94% | 1.53x |
| GFC drawdown | 0.870x | -28.02% | 1.92x |
| QE bull | 3.699x | -14.61% | 1.04x |
| Covid crash | 0.832x | -20.00% | 1.25x |
| Inflation/rates shock | 0.822x | -21.46% | 1.05x |
| Recent recovery | 1.999x | -14.41% | 1.03x |

The core beat SPY wealth in every named regime in the exact Pareto/regime report. It
also beat B4 original in GFC, inflation shock and recent recovery, while B4 original
was slightly better in dot-com, QE bull and Covid crash.

![Regime relative wealth](results/final_core_report/plots/regime_relative_wealth.png)

## Why Other Candidates Lost

The study tested several attempts to improve the core.

### Negative-Cash Stacked Candidate

The local B4-like search found a stronger-return stacked point:

```text
35% GDESIM / 40% RSSTSIM / 5% SPYSIM / 45% ZROZSIM / -25% CASHX
```

It reached CAGR `17.35%`, MDD `-30.44%`, Calmar `0.570`, terminal wealth `456x`, but
it requires negative external cash. This violates the operational no-margin constraint,
so it is rejected for practical use.

### Levered-Equity Challengers

Core-beater GA runs repeatedly found small `QLDSIM`/`TQQQSIM` boosters. Examples:

| Challenger | CAGR | MDD | Calmar | Fitness vs core |
|---|---:|---:|---:|---:|
| `35 GDE / 40 RSST / 20 ZROZ / 5 QLD` | 16.56% | -40.04% | 0.414 | 0.135 |
| `35 GDE / 35 RSST / 25 ZROZ / 5 TQQQ` | 16.52% | -41.96% | 0.394 | 0.124 |
| `35 GDE / 45 RSST / 20 ZROZ` | 16.21% | -32.97% | 0.492 | 0.085 |

These do not beat the core objective. They either add too little return for too much
drawdown or reduce the core-relative dominance score.

### SCV, Value And Momentum Factors

The factor/momentum probe added `VBRSIM`, `MTUMSIM` and `EFVSIM` to the no-margin
universe. The common factor window was `1994-06-02..2026-04-17`.

All three seeds selected the original core as exact rank 1:

```text
35% GDESIM / 40% RSSTSIM / 25% ZROZSIM
```

Best non-core challenger in that run:

```text
35% GDESIM / 35% RSSTSIM / 25% ZROZSIM / 5% QLDSIM
```

It had CAGR `16.00%`, MDD `-37.31%`, Calmar `0.429`, fitness `0.134`. `VBRSIM` only
appeared in lower-ranked candidates; `MTUMSIM` did not survive into the top-10 exact
rows. Factor sleeves therefore failed to improve rolling dominance in this setup
`[ml_for_algo_trading, ch.4 p.82-93]`.

## Implementation Risks

This portfolio is not a final live recommendation. Key unresolved risks:

- Testfol.io series are simulated proxies for long pre-inception history.
- `GDESIM` and `RSSTSIM` are capital-efficient/stacked products; realized ETF tracking,
  financing, taxes and fund survival matter.
- BR investor implementation needs broker access, tax handling and product availability
  review.
- Monthly rebalance assumption needs sensitivity against quarterly/yearly schedules.
- Fee/drag stress has not yet been applied to the exact core report.
- Formal validation gates were not run because the study is currently selecting an
  internal static benchmark, not promoting a trading strategy.

## Recommended Next Step

Stop broad static optimization for now. Treat `35/40/25` as the study benchmark and run
implementation realism checks:

1. Annual drag stress: `0.25%`, `0.50%`, `1.00%`.
2. Rebalance frequency: monthly vs quarterly vs yearly.
3. Start-date sensitivity: 1988, 1990, 1995, 2000, 2005.
4. Remove-one-asset tests: no `GDESIM`, no `RSSTSIM`, no `ZROZSIM`.
5. Product mapping: live ETF equivalents, broker availability, expense ratios and BR tax
   treatment.

If those checks hold, the portfolio remains a strong long-term passive research core.
If they fail, the study should not force a more complex optimizer result; it should
either keep the core as a benchmark only or move to a separately pre-registered tactical
overlay study.

## Artifacts

- Exact Pareto/regime report: `results/pareto_regime_report/REPORT.md`.
- Final report plots: `results/final_core_report/plots/`.
- Core no-margin local search: `results/local_pareto_b4_no_margin/`.
- Core-beater GA: `results/ga_core_beater/`.
- Factor/momentum GA: `results/ga_core_factor_momentum_beater/`.
- Current study memory: `MEMORY.md`.
- Next steps: `NEXT_STEPS.md`.
