# Phase 7B - Multi-Asset Portfolio of SMA200 Rotations (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Equal-weight portfolio of single-asset Gayed SMA200 rotations with a UNIFORM grammar (shared L, ZROZ risk-off, shared vol-gate choice; no per-leg recipe fitting) `[systematic_trading, p.42]`, `[systematic_trading, p.170-171]`, `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`. IWM/XLK/GLD legs use in-memory synthetic 2x (`r = 2*r_u - r_cash - 0.95%/252`) `[leverage_for_the_long_run, p.16, fn.22-23]` - a DISCLOSED limitation: synthetic legs understate real-ETF tracking frictions.

Pre-registered grid: 3 compositions x 2 leverages x 2 vol gates x 6 lags = 72 rows. **n_trials ledger: 4077 + 72 = 4149.** EW B&H benchmarks and standalone-leg controls are comparisons, not trials.

**Built-in sanity ({SPY}-only composition vs `phase04.simulate_returns`):** max abs diff 0.

## Executive Conclusion

Pre-registered screen (best trial row per composition by WF ratio, tie-break Calmar): **0/3 compositions SUCCESS**. Criteria: WF ratio (vs EW-underlying B&H) strictly above the max standalone-leg WF ratio AND CAGR > EW B&H bench AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.


## Plots

| Plot | File |
|---|---|
| Equity/drawdown vs EW B&H benchmark | [plots/phase07b_equity_dd.png](plots/phase07b_equity_dd.png) |
| WF ratio: portfolio vs standalone legs | [plots/phase07b_wf_ratio.png](plots/phase07b_wf_ratio.png) |
| CAGR x MDD frontier | [plots/phase07b_frontier.png](plots/phase07b_frontier.png) |
| Fraction of legs risk-on (best rows) | [plots/phase07b_legs_on_fraction.png](plots/phase07b_legs_on_fraction.png) |

## Screen Results

### EW5 — best row `L 2.00 / none / lag 2` (window 1986-01-03..2026-05-21)

- Portfolio WF 9/11 (81.8%) vs max standalone leg 81.8% (XLK): F
- CAGR 17.44% vs EW B&H bench 11.69%: P
- MDD -53.08% >= -50%: F
- **Screen: FAIL**

Standalone-leg controls (same L/vol/lag/window, WF vs own underlying B&H):

| Leg | WF | CAGR | MDD |
|---|---|---|---|
| SPY | 7/11 (63.6%) | 16.82% | -48.18% |
| QQQ | 8/11 (72.7%) | 20.82% | -68.88% |
| IWM | 6/11 (54.5%) | 10.25% | -71.31% |
| XLK | 9/11 (81.8%) | 19.40% | -69.61% |
| GLD | 7/11 (63.6%) | 10.07% | -69.68% |

### EW4_no_qqq — best row `L 2.00 / none / lag 4` (window 1979-01-02..2026-05-21)

- Portfolio WF 8/13 (61.5%) vs max standalone leg 61.5% (IWM): F
- CAGR 16.50% vs EW B&H bench 11.11%: P
- MDD -57.38% >= -50%: F
- **Screen: FAIL**

Standalone-leg controls (same L/vol/lag/window, WF vs own underlying B&H):

| Leg | WF | CAGR | MDD |
|---|---|---|---|
| SPY | 7/13 (53.8%) | 17.99% | -50.18% |
| IWM | 8/13 (61.5%) | 13.49% | -74.19% |
| XLK | 8/13 (61.5%) | 18.67% | -66.48% |
| GLD | 6/13 (46.2%) | 7.65% | -85.58% |

### EW3_spy_qqq_gld — best row `L 2.00 / none / lag 1` (window 1986-01-03..2026-05-21)

- Portfolio WF 8/11 (72.7%) vs max standalone leg 72.7% (QQQ): F
- CAGR 18.19% vs EW B&H bench 12.16%: P
- MDD -47.50% >= -50%: P
- **Screen: FAIL**

Standalone-leg controls (same L/vol/lag/window, WF vs own underlying B&H):

| Leg | WF | CAGR | MDD |
|---|---|---|---|
| SPY | 7/11 (63.6%) | 16.66% | -47.65% |
| QQQ | 8/11 (72.7%) | 21.48% | -67.75% |
| GLD | 7/11 (63.6%) | 10.42% | -66.07% |

## Top EW5 Rows (by WF ratio, then Calmar)

| L | Vol | Lag | WF | CAGR | Bench CAGR | MDD | Sharpe | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 2.00 | none | 2 | 9/11 (81.8%) | 17.44% | 11.69% | -53.08% | 0.756 | 0.329 | 6.87 |
| 2.00 | RV63 <= 40% | 1 | 8/11 (72.7%) | 18.04% | 11.69% | -51.95% | 0.782 | 0.347 | 6.72 |
| 2.00 | none | 1 | 8/11 (72.7%) | 18.01% | 11.69% | -51.92% | 0.767 | 0.347 | 6.86 |
| 2.00 | none | 0 | 8/11 (72.7%) | 18.19% | 11.69% | -52.81% | 0.770 | 0.345 | 3.31 |
| 2.00 | RV63 <= 40% | 0 | 8/11 (72.7%) | 18.13% | 11.69% | -52.77% | 0.780 | 0.344 | 3.22 |
| 1.75 | none | 1 | 8/11 (72.7%) | 16.89% | 11.69% | -50.30% | 0.777 | 0.336 | 6.86 |

## Top EW4_no_qqq Rows (by WF ratio, then Calmar)

| L | Vol | Lag | WF | CAGR | Bench CAGR | MDD | Sharpe | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 2.00 | none | 4 | 8/13 (61.5%) | 16.50% | 11.11% | -57.38% | 0.726 | 0.288 | 6.64 |
| 2.00 | RV63 <= 40% | 2 | 7/13 (53.8%) | 17.32% | 11.11% | -56.74% | 0.752 | 0.305 | 6.95 |
| 2.00 | RV63 <= 40% | 3 | 7/13 (53.8%) | 17.12% | 11.11% | -56.72% | 0.749 | 0.302 | 6.95 |
| 2.00 | none | 2 | 7/13 (53.8%) | 17.22% | 11.11% | -57.83% | 0.743 | 0.298 | 7.01 |
| 1.75 | RV63 <= 40% | 2 | 7/13 (53.8%) | 16.39% | 11.11% | -55.11% | 0.757 | 0.297 | 6.94 |
| 2.00 | none | 3 | 7/13 (53.8%) | 17.01% | 11.11% | -57.74% | 0.739 | 0.295 | 7.01 |

## Top EW3_spy_qqq_gld Rows (by WF ratio, then Calmar)

| L | Vol | Lag | WF | CAGR | Bench CAGR | MDD | Sharpe | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 2.00 | none | 1 | 8/11 (72.7%) | 18.19% | 12.16% | -47.50% | 0.791 | 0.383 | 7.00 |
| 2.00 | RV63 <= 40% | 1 | 8/11 (72.7%) | 18.05% | 12.16% | -47.47% | 0.800 | 0.380 | 6.92 |
| 2.00 | none | 0 | 7/11 (63.6%) | 18.11% | 12.16% | -48.89% | 0.785 | 0.371 | 3.37 |
| 2.00 | RV63 <= 40% | 0 | 7/11 (63.6%) | 17.75% | 12.16% | -48.68% | 0.787 | 0.365 | 3.31 |
| 2.00 | none | 2 | 7/11 (63.6%) | 17.73% | 12.16% | -49.18% | 0.781 | 0.360 | 7.00 |
| 2.00 | RV63 <= 40% | 2 | 7/11 (63.6%) | 17.65% | 12.16% | -49.14% | 0.793 | 0.359 | 6.93 |

## Phase Verdict

| Question | Verdict |
|---|---|
| EW5: EW portfolio beats every standalone leg on WF ratio? | No (81.8% vs 81.8%). |
| EW4_no_qqq: EW portfolio beats every standalone leg on WF ratio? | No (61.5% vs 61.5%). |
| EW3_spy_qqq_gld: EW portfolio beats every standalone leg on WF ratio? | No (72.7% vs 72.7%). |
| Screen successes? | 0/3. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
