# SOXL SMA Sweep v2 — corrected with SMH signals + real Tiingo SOXL (post-2010)

_Generated 2026-05-07_

## Methodological correction over v1

V1 (commit today) used QQQSIM as a proxy for SOXL signals because the parent
study's `LETF_TESTFOLIO` mapping has `SOXL -> QQQSIM` (a proxy historical
artifact, not a deliberate methodological choice). This v2 sweep corrects that
by:

- **Signal computation:** real SMH (1x SOX ETF, Tiingo data from 2000-06-05)
- **Position returns:** real SOXL (3x SOX ETF, Tiingo data from 2010-03-11)
- **Off-state:** ZROZ (testfolio sim)
- **Window:** 2010-03-12 to 2026-04-17 (constrained by SOXL inception + SMH SMA warmup)

This matches the methodological pattern used elsewhere in the project (TQQQ
signals from QQQ, UPRO signals from SPY). V1's QQQSIM-proxy signals were
methodologically wrong for the SOXL deploy guide use case: NDX/QQQ momentum
does not capture true SOX-class regime dynamics.

## Method

T3d K=2 Vote-of-K with:
- vol_window=21, **vol_threshold=0.30** (calibrated for SMH 1x SOX class, vs canonical 0.40 for QLD 2x NDX per `[leverage_for_the_long_run, p.5-6]`)
- ar1_window=30 (canonical, per `[paper.hsieh_2025_letf_compounding]`)
- smabuf=0.05 (5%, per `THRESHOLD_SWEEP_REPORT.md` §3.3 — winner candidate under Sortino)
- ON when K>=2 of {SMA(long), SMA(short), vol<0.30, AR1>0}

4 sub-signals computed on **SMH prices** (not SOXL, not QQQSIM):
- s1: SMH price > SMA(long) with 5% hysteresis buffer
- s2: SMH price > SMA(short) with 5% hysteresis buffer
- s3: SMH realized_vol(21d) < 0.30
- s4: SMH AR(1)(30d) > 0

Sweep grid: SMA long in {100, 125, 150, 175, 200, 250} x SMA short in {25, 50, 75, 100},
with `short < long` constraint -> 23 combos.

Citations:
- `[trading_systems_methods, Kaufman ch.21]` SMA scaling for vol regimes
- `[leverage_for_the_long_run, p.5-6]` realized vol gate, 40% canonical for 2x NDX; scaled to 30% for 1x SOX
- `[advances_fin_ml, p.275]` Sortino in metric family

## Top-5 by Sortino

| sma_long | sma_short | Sortino | Sharpe | CAGR  | MDD    | Trades | Window |
|---|---|---|---|---|---|---|---|
| 200 | 50  | 1.087 | 0.765 | 33.1% | -81.2% | 84 | 2010-03-12..2026-04-17 |
| 200 | 75  | 1.071 | 0.754 | 32.2% | -79.9% | 84 | 2010-03-12..2026-04-17 |
| 200 | 25  | 1.063 | 0.747 | 31.4% | -81.4% | 96 | 2010-03-12..2026-04-17 |
| 175 | 50  | 1.055 | 0.745 | 31.3% | -80.1% | 82 | 2010-03-12..2026-04-17 |
| 175 | 75  | 1.051 | 0.741 | 31.0% | -79.3% | 82 | 2010-03-12..2026-04-17 |

**Winner: sma200/50, Sortino=1.087.**

Margin to runner-up (sma200/75): +0.016 Sortino. Thin margin — note both sma200/50 and
sma200/75 have identical trade counts (84), so the long-period 200 is robust; the short-period
difference (50 vs 75) produces only marginal Sortino gap.

![Sortino heatmap](soxl_sma_sweep_v2/sortino_heatmap.png)

## Recommendation

Best combo for SOXL/ZROZ rotation on real Tiingo data (2010-04 to 2026-04):
**sma200/50** with Sortino 1.087, CAGR 33.1% gross, MDD -81.2%, 84 trade events.

Translation to deploy guide §2.2:
- SOXL params: sma_long_period=200, sma_short_period=50, vol_threshold=0.30 (SMH 1x class)
- DRAM mirrors SOXL until launched

**Note on winning combo consistency:** sma200 appears in the top-3 winners across all short
periods (25, 50, 75), confirming the long-SMA is the dominant parameter. The 50-bar short SMA
provides a moderate momentum-filter without excessive whipsaw, consistent with the canonical
result (sma200/50 was also the v1 winner on QQQSIM proxy), lending robustness confidence to
the long-period choice.

## Critical limitations

1. **Post-2010 only** — 16 years, predominantly bull market (QE era, 2010-2022 bull,
   2022-2023 correction, 2023-2025 bull). Does NOT capture 2000 dotcom or 2008 GFC
   stress regimes where SOXL-class assets (semiconductors) would have faced -85% to -95%
   drawdowns. Recommendation may not generalize to extended bear cycles.

2. **No anti-overfit margin applied** — exploratory sweep without CSCV/PBO.
   `[advances_fin_ml, p.208-211]`: real deploy needs PBO < 0.5 gate + full §5 validation
   roadmap from the deploy guide.

3. **vol_threshold=0.30 chosen by analogy** to canonical 0.40 (QLD 2x class), not
   empirically tuned from SMH realized-vol distribution. Future sub-study should
   sweep vol_threshold independently (0.20/0.25/0.30/0.35/0.40) on SMH.

4. **MDD range -79% to -87%** across all combos confirms SOXL is structurally extreme-drawdown.
   Any deploy must use position-sizing rules per mandate §7 (dynamic sizing: position size
   decreases with equity).

## Comparison with v1

| | v1 (QQQSIM proxy) | v2 (real SMH + SOXL) |
|---|---|---|
| Signal source | QQQSIM (NDX proxy) | SMH (1x SOX, real Tiingo) |
| Position source | SOXL (Tiingo, but via testfolio synth path) | SOXL (direct Tiingo adj_close) |
| vol_threshold | 0.40 | 0.30 |
| Best combo | sma200/50, Sortino=1.093 | sma200/50, Sortino=1.087 |
| Window | lh_56y (testfolio sim, pre-2010 NDX extrapolated) | 2010-03-12 to 2026-04-17 (real only) |

The best combo is consistent (sma200/50 wins in both). The Sortino difference (1.093 vs 1.087)
is negligible and reflects a different evaluation window (v1 includes pre-2010 simulated data;
v2 is real-data only). **Use v2 numbers in the deploy guide, not v1**, because v2 avoids both
the proxy-signal contamination and the synthetic-history path-dependence.

## Citations

- `[trading_systems_methods, Kaufman ch.21]` SMA scaling for vol regimes
- `[leverage_for_the_long_run, p.5-6]` realized vol gate calibration
- `[advances_fin_ml, p.275]` Sortino in metric family
- `[paper.hsieh_2025_letf_compounding]` AR(1) regime filter
- Sister: `sortino_reanalysis/SORTINO_REANALYSIS_REPORT.md` §1 (Sortino vs Sharpe)
- Sister: `SOXL_SMA_SWEEP_REPORT.md` (v1, with proxy caveat — superseded by this report)
- Sister: `THRESHOLD_SWEEP_REPORT.md` §3.3 (smabuf 5% rationale)
