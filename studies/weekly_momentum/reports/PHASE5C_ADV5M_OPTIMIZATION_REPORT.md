# Phase 5c ADV5M Optimization Report

## TL;DR

The ADV5M optimization did not improve the frozen baseline. After adding a stale-price guard, the original ADV5M grid still produced the best headline result, but it remains blocked by PBO/bootstrap. Two focused neighborhood grids improved PBO but degraded DSR, bootstrap, CAGR, Sharpe or drawdown. The optimization result is therefore: keep the baseline as the research reference, do not promote it, and do not broaden the sweep `[advances_fin_ml, p.208-211]`.

## Method

- Data integrity fix: when a held symbol has no price on a trading date, its sleeve is left in cash instead of carrying a stale zero-return mark. This does not model delisting returns; it only prevents stale exposure from being counted as an active holding.
- Universe: all cached Tiingo equities with point-in-time tradability filters (`age>=252`, price >= $5, ADV20 >= $5M) `[stocks_on_the_move, p.81]`.
- Walk-forward: 3y train -> 1y test, selecting parameters only from prior training windows `[advances_fin_ml, p.208-211]`.
- Optimization was intentionally narrow. No 200-config broad sweep was run.

## Results

| run | grid | CAGR | MDD | Sharpe | PBO | PBO pass | DSR p | DSR pass | Bootstrap low | Bootstrap pass | 10bps + DARF CAGR | Verdict |
|:--|:--|--:|--:|--:|--:|:--|--:|:--|--:|:--|--:|:--|
| Baseline stale-guard | lookbacks 60/80/100, top_k 5/10/20, SMA200/250 | 48.09% | -36.26% | 1.184 | 0.579 | no | 0.024 | yes | -3.11% | no | 18.99% | best performance, still FAIL |
| Focused optimization | lookbacks 50/60/70/80, top_k 5/8/10/12, SMA200/250 | 43.89% | -38.15% | 1.075 | 0.381 | yes | 0.089 | no | -10.12% | no | 15.31% | worse |
| Aggressive neighborhood | lookbacks 40/50/60/70, top_k 3/4/5/6/8, SMA150/200/250 | 39.50% | -55.10% | 0.940 | 0.044 | yes | 0.260 | no | -13.54% | no | 8.11% | worse |

## Plots

The plots below compare SPY against the three final Phase 5/5b/5c ADV5M variants.
They are reporting artifacts only, generated from preserved aligned equity series;
no new parameter search is introduced `[advances_fin_ml, p.208-211]`.

![Phase 5 ADV5M performance vs SPY](../plots/phase5/phase5_adv5m_performance_vs_spy.png)

![Phase 5 ADV5M equity over SPY](../plots/phase5/phase5_adv5m_equity_over_spy.png)

![Phase 5 ADV5M rolling CAGR vs SPY](../plots/phase5/phase5_adv5m_rolling_cagr_1_3_5y.png)

![Phase 5 ADV5M rolling summary vs SPY](../plots/phase5/phase5_adv5m_rolling_summary_vs_spy.png)

## Interpretation

- The baseline remains the strongest economic run, but it still fails two hard gates: PBO and bootstrap.
- The focused optimization improves PBO below 0.5, but DSR fails and bootstrap gets worse. This is not a valid tradeoff because any hard-gate failure blocks promotion `[advances_fin_ml, p.196-202]`.
- The aggressive neighborhood strongly improves PBO, but the performance degrades too much: CAGR falls to 39.50%, MDD worsens to -55.10%, and DSR/bootstrap fail.
- This pattern suggests the high-return ADV5M result is parameter-sensitive. Robustifying the grid lowers the overfit signal but also removes the attractive risk-adjusted profile.

## Verdict

No deploy and no further local parameter optimization. The only useful next research step is data-quality work: survivorship-free all-listed universe, delisting returns, and execution-grade fills. Parameter search before that would mainly add trial penalty without solving the data defect `[advances_fin_ml, p.208-211]`.
