# Phase 5b Dynamic All-Stocks Robustness Report

## TL;DR

`dynamic_wf_all_stocks` remains research-only. The branch keeps attractive CAGR under several pre-registered robustness variants, but it still does not clear the hard validation stack: PBO/DSR/bootstrap are not jointly stable, stricter liquidity weakens the result, and the single-block holdout beats SPY on CAGR but loses badly on Sharpe and drawdown quality.

## Setup

- Hypothesis: weekly cross-sectional momentum over all cached Tiingo equities, not S&P 500 membership.
- Point-in-time tradability filters: observed age >= 252 bars, adjusted price >= $5, ADV20 thresholds of $5M/$10M/$20M `[stocks_on_the_move, p.81]`.
- Dynamic parameter grid: lookbacks 60/80/100, top_k 5/10/20, market filters SMA200/SMA250, allow_negative=0.
- Walk-forward variants: 2y/3y/4y train -> 1y test, selecting parameters only from prior train windows `[advances_fin_ml, p.208-211]`.
- Gates: PBO < 0.5, DSR p < 0.05, OOS windows, bootstrap 99.9% CAGR CI low > 0 `[advances_fin_ml, p.196-202]`.

## Robustness Matrix

| run | train -> test | ADV20 min | CAGR | MDD | Sharpe | PBO | PBO pass | DSR p | DSR pass | OOS | Bootstrap low | Bootstrap pass | 10bps + DARF CAGR | Verdict |
|:--|:--|--:|--:|--:|--:|--:|:--|--:|:--|:--|--:|:--|--:|:--|
| ADV5M base | 3y -> 1y | $5M | 48.09% | -36.26% | 1.184 | 0.579 | no | 0.024 | yes | 9/10 | -3.11% | no | 18.99% | FAIL |
| ADV10M base | 3y -> 1y | $10M | 37.31% | -36.26% | 0.976 | 0.516 | no | 0.101 | no | 8/10 | -9.78% | no | 10.65% | FAIL |
| ADV20M | 3y -> 1y | $20M | 41.06% | -42.79% | 1.019 | 0.385 | yes | 0.079 | no | 8/10 | -8.53% | no | 14.42% | FAIL |
| ADV5M WF2Y | 2y -> 1y | $5M | 31.84% | -41.03% | 0.979 | 0.579 | no | 0.082 | no | 9/11 | -1.02% | no | 0.50% | FAIL |
| ADV5M WF4Y | 4y -> 1y | $5M | 47.46% | -36.31% | 1.153 | 0.579 | no | 0.047 | yes | 8/9 | 0.12% | yes | 17.57% | FAIL |
| ADV10M WF2Y | 2y -> 1y | $10M | 30.76% | -42.46% | 0.857 | 0.516 | no | 0.154 | no | 8/11 | -6.75% | no | 0.01% | FAIL |
| ADV10M WF4Y | 4y -> 1y | $10M | 43.51% | -36.31% | 1.074 | 0.516 | no | 0.078 | no | 8/9 | -2.86% | no | 14.18% | FAIL |

## Single-Block Holdout

- Train block: 2013-01-02..2022-12-31.
- Test block: 2023-01-01..2025-12-31.
- ADV20 min: $5M.
- Selected once from train: `lb60_sig3_sell1_sd0_k5_neg0_defcash_mfsma200`.
- Output: `phase5_single_holdout_adv5m/HOLDOUT_REPORT.md`.

| series | CAGR | MDD | Sharpe | Sortino | Calmar |
|:--|--:|--:|--:|--:|--:|
| Selected strategy | 30.60% | -32.29% | 0.816 | 1.250 | 0.948 |
| SPY | 23.18% | -18.76% | 1.426 | 2.147 | 1.236 |

The single holdout is not a clean promotion signal. It beats SPY on CAGR, but the excess return comes with worse drawdown and materially worse risk-adjusted quality.

## Interpretation

- Liquidity sensitivity is real. ADV5M is the strongest base result; ADV10M weakens; ADV20M improves PBO but fails DSR/bootstrap and takes the worst drawdown.
- Window sensitivity is real. The 4y ADV5M variant is the only one that passes DSR and bootstrap together, but it still fails PBO, so the family gate remains blocked.
- Tax drag is large. ADV5M WF2Y and ADV10M WF2Y collapse to near-zero after 10 bps + annual DARF stress.
- The cached-equity universe is still not a complete point-in-time all-listed US universe. The tradability filters are point-in-time, but the available ticker set can still carry listing/survivorship limitations.

## Verdict

No deploy. No promotion to mandate Strategy B/D. The branch can remain archived as a research lead, but the next valid step would need a true survivorship-free all-listed universe plus delisting returns before any broader sweep. Expanding parameter search now would increase trial penalty without fixing the failed gates `[advances_fin_ml, p.208-211]`.
