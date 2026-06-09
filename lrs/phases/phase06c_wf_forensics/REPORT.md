# Phase 6C - Walk-Forward Forensics (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change. Phase 4's verdict (family closed, 0/6 gates) stands regardless of this forensic.

Phase 4's binding gate was G3 walk-forward (>=75% of rolling ~3y OOS windows must beat the underlying after-tax). This phase persists the per-window detail (one row per base x window, the artifact Phase 4 never wrote) and labels each window with pre-registered regime tags, asking whether the failures concentrate where trend-timing structurally loses `[leverage_for_the_long_run, p.7-8]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.211-216]`.

Splits identical to Phase 4 (`is=1764d / oos=756d / step=756d`). Regime cuts pre-registered: trend = sign of underlying OOS return; vol = mean RV21 < 15% low, 15%-25% mid, >= 25% high `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39, p.53-54]`. No new configs: **+0 to the n_trials ledger** (lineage stays 3876).

## Executive Conclusion

Failing windows: **33** of 84 base-windows. In the `bull_low` cell: 16 (48.48%); in any `bull` cell: 30 (90.91%).

**Pre-registered headline question — do >=2/3 of failing windows fall in `bull x low-vol`? NO.** Failures are not concentrated enough in the calm-bull cell to call the miss purely structural; the per-cell table below shows where they actually sit. The family stays closed with this additional evidence.


## Plots

| Plot | File |
|---|---|
| Per-window relative return by regime cell | [plots/phase06c_window_bars.png](plots/phase06c_window_bars.png) |
| Window mean RV21 vs relative return | [plots/phase06c_rv_scatter.png](plots/phase06c_rv_scatter.png) |
| Beat/fail heatmap | [plots/phase06c_beat_heatmap.png](plots/phase06c_beat_heatmap.png) |

## Beat Rate By Regime Cell (pooled)

| Cell | Windows | Beat | Fail | Beat rate | Mean rel ret |
|---|---|---|---|---|---|
| bull_low | 39 | 23 | 16 | 58.97% | +11.54pp |
| bull_mid | 27 | 16 | 11 | 59.26% | +16.10pp |
| bull_high | 12 | 9 | 3 | 75.00% | +27.30pp |
| bear_mid | 3 | 0 | 3 | 0.00% | -18.82pp |
| bear_high | 3 | 3 | 0 | 100.00% | +154.18pp |

## Beat Rate By Regime Cell (SPY)

| Cell | Windows | Beat | Fail | Beat rate | Mean rel ret |
|---|---|---|---|---|---|
| bull_low | 33 | 23 | 10 | 69.70% | +16.30pp |
| bull_mid | 15 | 11 | 4 | 73.33% | +35.12pp |
| bear_mid | 3 | 0 | 3 | 0.00% | -18.82pp |

## Beat Rate By Regime Cell (QQQ)

| Cell | Windows | Beat | Fail | Beat rate | Mean rel ret |
|---|---|---|---|---|---|
| bull_low | 6 | 0 | 6 | 0.00% | -14.66pp |
| bull_mid | 12 | 5 | 7 | 41.67% | -7.68pp |
| bull_high | 12 | 9 | 3 | 75.00% | +27.30pp |
| bear_high | 3 | 3 | 0 | 100.00% | +154.18pp |

## All Failing Windows

| Base | Window | Rel ret | Under ret | Mean RV21 | Risk-on days | Cell |
|---|---|---|---|---|---|---|
| qqq_alt_vol | 1992-12-23 .. 1995-12-19 | -39.19pp | 57.34% | 17.91% | 80.03% | bull_mid |
| qqq_alt_vol | 2004-12-23 .. 2007-12-24 | -27.34pp | 32.74% | 14.72% | 81.35% | bull_low |
| qqq_alt_vol | 2010-12-27 .. 2013-12-26 | -41.92pp | 65.57% | 15.88% | 87.70% | bull_mid |
| qqq_alt_vol | 2013-12-27 .. 2016-12-27 | -2.08pp | 42.82% | 14.66% | 85.85% | bull_low |
| qqq_lower_lev | 1992-12-23 .. 1995-12-19 | -24.38pp | 57.34% | 17.91% | 84.13% | bull_mid |
| qqq_lower_lev | 1995-12-20 .. 1998-12-16 | -37.54pp | 204.34% | 26.05% | 89.29% | bull_high |
| qqq_lower_lev | 2004-12-23 .. 2007-12-24 | -25.26pp | 32.74% | 14.72% | 82.54% | bull_low |
| qqq_lower_lev | 2010-12-27 .. 2013-12-26 | -55.74pp | 65.57% | 15.88% | 88.10% | bull_mid |
| qqq_lower_lev | 2013-12-27 .. 2016-12-27 | -5.37pp | 42.82% | 14.66% | 86.11% | bull_low |
| qqq_lower_lev | 2019-12-31 .. 2022-12-29 | -2.24pp | 27.99% | 25.58% | 60.45% | bull_high |
| qqq_lower_lev | 2022-12-30 .. 2026-01-06 | -7.83pp | 138.18% | 18.15% | 91.40% | bull_mid |
| qqq_top | 1992-12-23 .. 1995-12-19 | -21.76pp | 57.34% | 17.91% | 84.13% | bull_mid |
| qqq_top | 1995-12-20 .. 1998-12-16 | -11.15pp | 204.34% | 26.05% | 89.29% | bull_high |
| qqq_top | 2004-12-23 .. 2007-12-24 | -26.30pp | 32.74% | 14.72% | 82.54% | bull_low |
| qqq_top | 2010-12-27 .. 2013-12-26 | -54.55pp | 65.57% | 15.88% | 88.10% | bull_mid |
| qqq_top | 2013-12-27 .. 2016-12-27 | -1.63pp | 42.82% | 14.66% | 86.11% | bull_low |
| spy_alt_off | 1975-05-08 .. 1978-05-04 | -9.63pp | 22.77% | 10.52% | 64.42% | bull_low |
| spy_alt_off | 1987-04-27 .. 1990-04-20 | -4.57pp | 31.52% | 16.97% | 75.93% | bull_mid |
| spy_alt_off | 1999-04-14 .. 2002-04-17 | -19.63pp | -13.43% | 19.99% | 45.90% | bear_mid |
| spy_alt_off | 2005-04-19 .. 2008-04-18 | -0.24pp | 28.13% | 12.37% | 82.54% | bull_low |
| spy_alt_off | 2014-04-23 .. 2017-04-21 | -8.44pp | 33.10% | 11.70% | 85.85% | bull_low |
| spy_lower_lev | 1975-05-08 .. 1978-05-04 | -11.76pp | 22.77% | 10.52% | 64.42% | bull_low |
| spy_lower_lev | 1987-04-27 .. 1990-04-20 | -1.57pp | 31.52% | 16.97% | 75.93% | bull_mid |
| spy_lower_lev | 1999-04-14 .. 2002-04-17 | -15.82pp | -13.43% | 19.99% | 45.90% | bear_mid |
| spy_lower_lev | 2005-04-19 .. 2008-04-18 | -4.31pp | 28.13% | 12.37% | 82.54% | bull_low |
| spy_lower_lev | 2014-04-23 .. 2017-04-21 | -12.25pp | 33.10% | 11.70% | 85.85% | bull_low |
| spy_lower_lev | 2020-04-24 .. 2023-04-25 | -7.10pp | 52.80% | 17.94% | 68.65% | bull_mid |
| spy_lower_lev | 2023-04-26 .. 2026-04-30 | -6.27pp | 84.44% | 13.14% | 92.20% | bull_low |
| spy_top | 1975-05-08 .. 1978-05-04 | -13.35pp | 22.77% | 10.52% | 64.42% | bull_low |
| spy_top | 1987-04-27 .. 1990-04-20 | -2.33pp | 31.52% | 16.97% | 75.93% | bull_mid |
| spy_top | 1999-04-14 .. 2002-04-17 | -21.00pp | -13.43% | 19.99% | 45.90% | bear_mid |
| spy_top | 2005-04-19 .. 2008-04-18 | -3.70pp | 28.13% | 12.37% | 82.54% | bull_low |
| spy_top | 2014-04-23 .. 2017-04-21 | -11.36pp | 33.10% | 11.70% | 85.85% | bull_low |

## Phase Verdict

| Question | Verdict |
|---|---|
| Failing windows concentrated in `bull_low` (>=2/3)? | No (48.48%). |
| Failing windows in any `bull` cell? | 90.91%. |
| New configs / trials added? | 0 — pure forensics on the Phase 4 bases. |
| Did we promote anything? | No - diagnostic only. Phase 4 verdict unchanged. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
