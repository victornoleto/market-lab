# Phase 0 - Original Gayed Weekly Baseline

Status: research-only baseline. This report does not authorize deployment, paper trading or a mandate change.

Method references: original LRS rule from Gayed uses leveraged equity when the underlying closes above its moving average and defensive exposure otherwise `[leverage_for_the_long_run, p.13]`. SMA200 is used as the starting point because Gayed recommends it for low turnover practicality `[leverage_for_the_long_run, p.16]`. Weekly execution, lag sensitivity and rolling-window diagnostics are implementation robustness checks `[testing_tuning, p.327-335]`.

## Executive Conclusion

Phase 0 evaluated `24` baseline rows across `QQQ_2x, QQQ_3x, SPY_2x, SPY_3x` and settlement lags `0..5`. The top score row is `SPY_3x` with lag `2`: after-tax CAGR 16.91%, MDD -88.33%, Calmar 0.191, terminal 8798.16x vs its underlying and 9800.65x vs leveraged buy-and-hold. Rows beating underlying terminal wealth after tax: `24` of `24`.

Practical read: this is the original baseline only. It establishes the comparison surface for future risk-off, sparse indicator and bear-market sleeves; it is not a validation claim.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` |
| Signal | `underlying.shift(1) > SMA200.shift(1)` |
| Cadence | first trading day of each week |
| Risk-off | `CASHX` |
| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |
| Tax | annual 15% DARF on realized net gains plus final liquidation |
| XLK status | deferred until leveraged XLK/TECL synthetic series is present |


## Test Windows

Analysis: SPY and QQQ use different history lengths because the Testfol.io cache has long SPY synthetic history but QQQ starts in 1986. Cross-branch comparisons should account for this window difference.

| Branch | Start | End | Years | Underlying CAGR | Underlying MDD | LETF B&H CAGR | LETF B&H MDD |
|---|---|---|---|---|---|---|---|
| QQQ_2x | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% | 17.30% | -98.85% |
| QQQ_3x | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% | 12.44% | -99.98% |
| SPY_2x | 1885-03-23 | 2026-05-21 | 140.3 | 9.58% | -83.65% | 11.29% | -98.42% |
| SPY_3x | 1885-03-23 | 2026-05-21 | 140.3 | 9.58% | -83.65% | 9.49% | -99.91% |

## Plots

Each phase should emit plots as the study evolves. Phase 0 saves best-branch panels and lag sensitivity under `plots/`.

| Plot | File |
|---|---|
| SPY_3x best lag 2 | [plots/phase00_spy_3x_lag2.png](plots/phase00_spy_3x_lag2.png) |
| QQQ_3x best lag 0 | [plots/phase00_qqq_3x_lag0.png](plots/phase00_qqq_3x_lag0.png) |
| QQQ_2x best lag 0 | [plots/phase00_qqq_2x_lag0.png](plots/phase00_qqq_2x_lag0.png) |
| SPY_2x best lag 2 | [plots/phase00_spy_2x_lag2.png](plots/phase00_spy_2x_lag2.png) |
| Lag sensitivity | [plots/phase00_lag_sensitivity.png](plots/phase00_lag_sensitivity.png) |

## Ranked Baselines

Analysis: ranking uses after-tax CAGR vs underlying, Calmar, Sortino, rolling hit-rate and relative drawdown. Leveraged buy-and-hold is not the target to beat on CAGR; it is the risk-of-ruin comparator.

| Branch | Lag | CAGR | MDD | Calmar | Sortino | Spread vs U | Terminal/U | Terminal/LETF | Hit 10y | Rel DD U | Risk-On | Turn/Yr | Tax Paid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY_3x | 2 | 16.91% | -88.33% | 0.191 | 0.667 | +7.33pp | 8798.16x | 9800.65x | 88.6% | -80.29% | 69.6% | 2.79 | 51700501788.1% |
| QQQ_3x | 0 | 21.34% | -91.97% | 0.232 | 0.719 | +6.98pp | 10.95x | 21.70x | 84.2% | -80.13% | 73.7% | 3.10 | 39564.6% |
| SPY_3x | 3 | 16.65% | -88.71% | 0.188 | 0.657 | +7.07pp | 6490.95x | 7230.55x | 88.3% | -81.43% | 69.0% | 2.79 | 38255114885.7% |
| SPY_3x | 0 | 16.76% | -88.11% | 0.190 | 0.667 | +7.18pp | 7404.26x | 8247.93x | 84.6% | -80.66% | 70.7% | 2.79 | 43769137894.1% |
| SPY_3x | 5 | 16.05% | -88.20% | 0.182 | 0.637 | +6.47pp | 3142.01x | 3500.02x | 86.7% | -83.05% | 67.9% | 2.10 | 18489743866.2% |
| QQQ_2x | 0 | 18.69% | -78.85% | 0.237 | 0.743 | +4.33pp | 4.48x | 1.61x | 75.4% | -58.95% | 73.7% | 3.10 | 15919.5% |
| SPY_2x | 2 | 13.67% | -72.72% | 0.188 | 0.706 | +4.09pp | 170.51x | 19.31x | 86.6% | -67.67% | 69.6% | 2.79 | 991135603.4% |
| SPY_3x | 4 | 16.30% | -89.98% | 0.181 | 0.645 | +6.73pp | 4261.79x | 4747.40x | 87.4% | -86.03% | 68.5% | 2.67 | 25102560391.7% |
| SPY_3x | 1 | 16.22% | -89.41% | 0.181 | 0.651 | +6.64pp | 3861.79x | 4301.82x | 84.3% | -80.97% | 70.1% | 2.79 | 22755600908.5% |
| SPY_2x | 0 | 13.61% | -72.15% | 0.189 | 0.707 | +4.03pp | 159.74x | 18.09x | 83.6% | -66.04% | 70.7% | 2.79 | 932611001.1% |
| QQQ_3x | 1 | 20.41% | -90.77% | 0.225 | 0.700 | +6.05pp | 8.02x | 15.89x | 78.9% | -80.39% | 73.0% | 3.10 | 28879.8% |
| SPY_2x | 3 | 13.49% | -73.35% | 0.184 | 0.697 | +3.91pp | 136.53x | 15.46x | 86.1% | -67.41% | 69.0% | 2.79 | 795216620.7% |
| QQQ_3x | 5 | 19.24% | -90.76% | 0.212 | 0.669 | +4.88pp | 5.41x | 10.72x | 80.0% | -81.57% | 70.6% | 2.30 | 19370.3% |
| SPY_2x | 5 | 13.07% | -72.55% | 0.180 | 0.677 | +3.49pp | 81.14x | 9.19x | 82.2% | -70.47% | 67.9% | 2.10 | 472084167.8% |
| QQQ_3x | 2 | 19.70% | -91.27% | 0.216 | 0.685 | +5.34pp | 6.32x | 12.53x | 78.6% | -78.57% | 72.4% | 3.10 | 22682.3% |
| SPY_2x | 1 | 13.24% | -74.32% | 0.178 | 0.691 | +3.66pp | 100.69x | 11.40x | 82.3% | -67.84% | 70.1% | 2.79 | 586497537.1% |
| SPY_2x | 4 | 13.24% | -75.30% | 0.176 | 0.685 | +3.66pp | 100.55x | 11.39x | 84.9% | -72.92% | 68.5% | 2.67 | 585428195.2% |
| QQQ_2x | 1 | 18.07% | -76.87% | 0.235 | 0.724 | +3.71pp | 3.63x | 1.30x | 67.1% | -63.42% | 73.0% | 3.10 | 12856.9% |
| QQQ_2x | 5 | 17.15% | -77.06% | 0.223 | 0.693 | +2.79pp | 2.65x | 0.95x | 66.0% | -61.79% | 70.6% | 2.30 | 9330.6% |
| QQQ_2x | 2 | 17.58% | -77.75% | 0.226 | 0.709 | +3.22pp | 3.07x | 1.10x | 65.2% | -62.45% | 72.4% | 3.10 | 10842.4% |
| QQQ_3x | 4 | 18.51% | -91.57% | 0.202 | 0.658 | +4.15pp | 4.22x | 8.36x | 79.2% | -81.61% | 71.2% | 3.00 | 15121.9% |
| QQQ_2x | 4 | 16.70% | -78.40% | 0.213 | 0.682 | +2.34pp | 2.27x | 0.81x | 68.9% | -61.76% | 71.2% | 3.00 | 7997.4% |
| QQQ_3x | 3 | 18.12% | -92.65% | 0.196 | 0.653 | +3.76pp | 3.69x | 7.31x | 74.8% | -81.06% | 71.8% | 3.10 | 13244.6% |
| QQQ_2x | 3 | 16.53% | -80.22% | 0.206 | 0.678 | +2.18pp | 2.14x | 0.77x | 67.3% | -68.28% | 71.8% | 3.10 | 7563.6% |

## Lag Sensitivity

Analysis: `n` models settlement or operational delay. With `risk-off=CASHX`, the main drag appears on re-entry from cash into the leveraged sleeve.

| Branch | Best Lag | Best CAGR | Lag0 CAGR | Lag5 CAGR | Lag5-Lag0 | Best MDD | Best Terminal/U |
|---|---|---|---|---|---|---|---|
| QQQ_2x | 0 | 18.69% | 18.69% | 17.15% | -1.54pp | -78.85% | 4.48x |
| QQQ_3x | 0 | 21.34% | 21.34% | 19.24% | -2.10pp | -91.97% | 10.95x |
| SPY_2x | 2 | 13.67% | 13.61% | 13.07% | -0.55pp | -72.72% | 170.51x |
| SPY_3x | 2 | 16.91% | 16.76% | 16.05% | -0.71pp | -88.33% | 8798.16x |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did we implement the original Gayed baseline? | Yes: SMA200, leveraged risk-on, `CASHX` risk-off. |
| Is weekly execution implemented? | Yes, first trading day of week, signal lagged one bar. |
| Is settlement lag implemented? | Yes, `n=0..5`. |
| Is Brazil annual tax modeled? | Yes, via `AnnualDarfEngine`. |
| Is this a deployable strategy? | No. This is only the restart baseline. |

Next step: Phase 1 should replace `CASHX` with defensive sleeves and momentum off-leg candidates before adding risk-on indicators.
