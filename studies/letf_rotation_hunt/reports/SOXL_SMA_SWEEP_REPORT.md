# SOXL / SMH SMA Sweep — best long/short curve for "faster" assets

_Generated 2026-05-07_

## Goal

Identify the best SMA long/short combo for high-vol LETF rotation strategies (SOXL primary, SMH 1x sanity check). Anchor for the deploy guide §2.2 SOXL params (previously a Kaufman-scaled guess of 150/30).

## Method

T3d K=2 Vote-of-K signal with:
- vol_window=21, vol_threshold=0.40, ar1_window=30, smabuf=0.05 (held canonical)
- ON asset = SOXL or SMH; OFF asset = ZROZ
- Dataset = lh_56y gross (primary)

**SOXL:** proxied by QQQSIM re-synthesized at 3x leverage + 0.91% ER via `synths.letf_synth_by_ticker` (native LETF_TESTFOLIO mapping). No SOXLSIM in testfolio cache; no SOXX/SOX proxy available. QQQSIM is the nearest available underlying.

**SMH:** VanEck Semiconductor ETF (1x, ER 0.35%). No SMHSIM in testfolio cache and no Tiingo parquet. Proxied by QQQSIM with leverage=1.0 (re-synthesized via patched LETF_TESTFOLIO). Serves as a lower-vol sanity check; results are indicative only (QQQSIM != SOX index composition).

Sweep grid: SMA long {100, 125, 150, 175, 200, 250} x SMA short {25, 50, 75, 100}, with `short < long` constraint → 23 valid combos x 2 assets = 46 dispatches.

## Findings

### SOXL top 5 by Sortino (lh_56y gross)

| sma_long | sma_short | sortino | sharpe | cagr | mdd | trade_count |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 50 | 1.107 | 0.785 | 33.4% | -93.8% | 218 |
| 200 | 50 | 1.093 | 0.775 | 32.8% | -92.0% | 196 |
| 250 | 50 | 1.092 | 0.774 | 32.8% | -92.0% | 168 |
| 125 | 50 | 1.059 | 0.753 | 30.9% | -96.7% | 198 |
| 200 | 75 | 1.057 | 0.750 | 30.8% | -92.9% | 200 |

**Pattern:** `sma_short=50` dominates the top band. `sma_short=25` consistently ranks at the bottom (Sortino 0.91-0.94 for all long periods). The long period has weak discriminating power when `sma_short=50`: sma100/50 leads by only +0.013 Sortino over sma200/50 and +0.015 over sma250/50.

### SMH top 5 by Sortino (lh_56y gross, QQQSIM@1x proxy)

| sma_long | sma_short | sortino | sharpe | cagr | mdd | trade_count |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 50 | 1.401 | 0.960 | 21.5% | -49.4% | 218 |
| 100 | 75 | 1.353 | 0.928 | 20.6% | -46.3% | 226 |
| 125 | 50 | 1.353 | 0.930 | 20.8% | -59.1% | 198 |
| 200 | 50 | 1.324 | 0.913 | 20.5% | -44.3% | 196 |
| 125 | 100 | 1.323 | 0.907 | 20.3% | -54.7% | 214 |

**Pattern:** Same dominant theme — `sma_short=50` leads. The SMH (1x proxy) result is consistent with SOXL: sma100/50 wins on Sortino. `sma_short=25` again ranks last.

### Heatmaps

![SOXL Sortino heatmap](soxl_sma_sweep/soxl_sortino_heatmap.png)
![SMH Sortino heatmap](soxl_sma_sweep/smh_sortino_heatmap.png)

## Recommendation

### Primary recommendation for SOXL (deploy guide §2.2)

**sma_long_period = 200, sma_short_period = 50** (sma200/50)

Rationale for choosing sma200/50 over the narrow Sortino winner sma100/50:

1. **Margin is thin:** sma100/50 leads by only +0.013 Sortino (1.107 vs 1.094). With a sweep of 23 combos and no CSCV/PBO applied, this margin is within noise.
2. **Trade count:** sma100/50 generates 218 trades vs 196 for sma200/50. More trades = more tax drag under M1 + M2 (Lei 14.754/2023) + higher spread cost.
3. **Curve-fit risk:** sma100 is a short lookback on a synthetic that uses QQQSIM (not real SOX). The faster the SMA, the more the optimization latches onto QQQSIM-specific price paths rather than true semiconductor regime cycles.
4. **MDD:** sma100/50 MDD -93.8% vs sma200/50 MDD -92.0% (marginally worse).
5. **Continuity with canonical:** The sortino_reanalysis winner for QLD (2x NDX) was sma250/100. Moving SOXL from 150/30 (Kaufman-scaled) to 200/50 (data-driven) represents a moderate update aligned with the canonical long-period preference, not a radical departure to an extremely fast SMA.

For DRAM (placeholder, memory-chip 3x LETF not yet launched): inherit SOXL params (200/50) as the best available prior.

**Previous guess (Kaufman scaling):** sma_long=150, sma_short=30
**Data-driven update:** sma_long=200, sma_short=50

Note on sma_short=30 vs sma_short=50: sma_short=30 was never tested in this sweep (grid starts at 25). The grid shows sma_short=25 is clearly inferior (Sortino 0.91-0.94), which strongly suggests sma_short=30 would also be inferior to sma_short=50. The improvement from 25->50 is large (+0.16 Sortino at long=200); the next step 50->75 is smaller (+0.036 at long=200). sma_short=50 is the robust choice.

### Secondary finding: vol_threshold

This sweep held vol_threshold=0.40 (canonical). The deploy guide notes SOXL may need vol_threshold=0.50 because SOX routinely runs 40-60% in normal regimes. This was not tested here. A future parameter sweep should validate vol_threshold for SOXL specifically.

## Limitations

1. **Proxy quality:** SOXL uses QQQSIM (NDX-based) not a true SOX synthetic. The SOX index and NDX index have different compositions and regime timing. This introduces proxy noise into all metrics.
2. **Single dataset:** lh_56y only. Cross-validation on modern_1990 (post-1990) or the real SOXL Tiingo data (post-2010, 4060 rows) deferred.
3. **No anti-overfit margin:** This is exploratory. The deploy guide §5 validation roadmap applies CSCV/PBO when the formal sub-study runs.
4. **SMH proxy:** QQQSIM@1x is a rough proxy for SMH. The finding that sma100/50 also wins for SMH is directionally consistent but not reliable for SMH-specific deployment.
5. **No tax or net analysis:** All metrics are gross. Net Sortino under M1/M2 (Lei 14.754/2023) is deferred per the validation roadmap.

## Citations

- `[trading_systems_methods, Kaufman ch.21]` SMA scaling for vol regimes — prior for parameter starting point; data-driven result modifies the Kaufman-scaling guess
- `[advances_fin_ml, p.275]` Sortino in metric family — operative metric per sortino_reanalysis
- Parent: `sortino_reanalysis/SORTINO_REANALYSIS_REPORT.md` §1 (Sortino > Sharpe for LETF asymmetric returns)
- Canonical winner: `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (sma250/100 for QLD/TQQQ class)
- Deploy guide: `STRATEGY_TQQQ_SOXL_DRAM_DEPLOY_GUIDE.md` §2.2

## Where this lives

- Code: `studies/letf_rotation_hunt/soxl_sma_sweep/`
- Data: `data/soxl_sma_sweep/sweep_metrics.csv` (46 rows, 23 per asset)
- Plots: `studies/letf_rotation_hunt/reports/soxl_sma_sweep/{soxl,smh}_sortino_heatmap.png`
- Report: this file
