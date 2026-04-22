# D7 QQQ-signal Composite — TQQQ+GLD (iter 12) [SWING BROKER]

**Strategy:** Binary composite signal (z-scored slope_MA200_QQQ + mom_90d_QQQ + inv_vol_TQQQ).
  Score > 0 → 100% TQQQ; Score ≤ 0 → 100% GLD.
  Key change from D6: QQQ replaces SPY as signal source.
  QQQ = TQQQ's direct underlying → faster detection of tech-sector stress.
**Window:** 2010-02-11 → 2026-04-14 (16.2yr, effective from ~2011-12)
**Portfolio:** TQQQ (signal-weight 0 or 1) + GLD (complement); daily rebalance
**Best config:** `trend_heavy` — **NO PASS**
**PBO:** 0.437 (PASS)

**Citations:** [stocks_on_the_move, p.81, ch.6], [leverage_for_the_long_run, p.13],
  [advances_fin_ml, p.208-211, p.298-299]

## Signal components (all z-scored, 252-bar rolling window)

| Component | Index | Formula | Warmup bars | Bullish when |
|-----------|-------|---------|-------------|--------------|
| slope_MA200 | **QQQ** | (SMA200_t − SMA200_{t−20}) / SMA200_{t−20}, z-scored | 472 | MA accelerating up |
| mom_90d | **QQQ** | QQQ.pct_change(90), z-scored | 342 | 90d return positive |
| inv_vol | TQQQ | 1/TQQQ_vol_20d, z-scored | 272 | TQQQ is calm/trending |

## Weight triplets

| # | Config | w_slope | w_mom | w_invvol | Note |
|---|--------|---------|-------|----------|------|
| 1 | equal_weight | 1/3 | 1/3 | 1/3 | balanced |
| 2 | trend_heavy | 0.5 | 0.3 | 0.2 | slope dominant |
| 3 | mom_heavy | 0.2 | 0.6 | 0.2 | momentum dominant |
| 4 | slope_dominant | 0.6 | 0.25 | 0.15 | D6 near-winner (SN=0.847 with SPY) |

## D6 comparison (SPY signals)

D6 best was trend_heavy: Sharpe=0.938 SN=0.797 MaxDD=-42.4% Calmar=0.731 WF=7/8 FWD_S=-1.14 (FAIL FWD)
D6 slope_dominant (not tested in D6 but extrapolated): SN≈0.847 (SPY version) — fails FWD same reason
D7 target: slope_dominant must pass FWD (QQQ exits TQQQ earlier during tariff shock)

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | FWD_start | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----------|-----|-------|----------|---------|--------|------|
| equal_weight | 22.57 | 19.18 | 0.764 | 0.649 | -42.4 | 0.532 | 7/8 | 1.35 | -1.68 | 2026-01-13 | 0.437 | 0.024 | ✓ | ✓ | ✗ | ✗ |
| trend_heavy | 26.27 | 22.33 | 0.834 | 0.709 | -54.6 | 0.481 | 6/8 | 1.29 | -1.51 | 2026-01-13 | 0.437 | 0.012 | ✓ | ✗ | ✗ | ✗ |
| mom_heavy | 12.94 | 11.00 | 0.532 | 0.452 | -56.4 | 0.229 | 6/8 | 1.17 | -2.09 | 2026-01-13 | 0.437 | 0.143 | ✓ | ✗ | ✗ | ✗ |
| slope_dominant | 23.30 | 19.80 | 0.769 | 0.653 | -60.3 | 0.386 | 6/8 | 1.11 | -1.73 | 2026-01-13 | 0.437 | 0.023 | ✓ | ✗ | ✗ | ✗ |

**SPY B&H net CAGR threshold:** 10.36% (15% IR BR applied)

## Cross-lib concordance (bt library)

- equal_weight: ✓ CONCORDANT (ΔCAGR=1.65pp)
- trend_heavy: ✓ CONCORDANT (ΔCAGR=1.16pp)
- mom_heavy: ✓ CONCORDANT (ΔCAGR=2.38pp)
- slope_dominant: ✓ CONCORDANT (ΔCAGR=0.66pp)

## Stage 2 — yfinance independent validation

- equal_weight: ✓ CONCORDANT (ΔCAGR=0.02pp)
- trend_heavy: ✓ CONCORDANT (ΔCAGR=0.03pp)
- mom_heavy: ✓ CONCORDANT (ΔCAGR=0.12pp)
- slope_dominant: ✓ CONCORDANT (ΔCAGR=0.82pp)

## TQQQ time-in-market (% of days in TQQQ)

| Config | Avg TQQQ weight% |
|--------|-----------------|
| equal_weight | 47.0% |
| trend_heavy | 47.3% |
| mom_heavy | 45.5% |
| slope_dominant | 45.6% |

## FWD window analysis (tariff shock period)

The FWD gate covers the last 63 trading days. In D6, this included the
Jan-Apr 2026 tariff shock where TQQQ fell -3.8% while SPY-based signals
remained bullish (SPY is more diversified, reacted slower). QQQ signals
should exit TQQQ earlier because QQQ tracks tech directly.

- equal_weight: FWD Sharpe=-1.677 CAGR=nan% (2026-01-13 → 2026-04-14) ✗ FAIL
- trend_heavy: FWD Sharpe=-1.511 CAGR=nan% (2026-01-13 → 2026-04-14) ✗ FAIL
- mom_heavy: FWD Sharpe=-2.085 CAGR=nan% (2026-01-13 → 2026-04-14) ✗ FAIL
- slope_dominant: FWD Sharpe=-1.734 CAGR=nan% (2026-01-13 → 2026-04-14) ✗ FAIL
