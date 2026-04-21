# D6 Clenow Composite — TQQQ+GLD (iter 11) [SWING BROKER]

**Strategy:** Binary composite signal (z-scored slope_MA200 + mom_90d + inv_vol).
  Score > 0 → 100% TQQQ; Score ≤ 0 → 100% GLD.
  Binary switch (like D2) → PBO expected low (~0.115). Composite should improve Sharpe.
**Window:** 2010-02-11 → 2026-04-14 (16.2yr, effective from ~2011-12)
**Portfolio:** TQQQ (signal-weight 0 or 1) + GLD (complement); daily rebalance
**Best config:** `trend_heavy` — **NO PASS**
**PBO:** 0.341 (PASS)

**Citations:** [stocks_on_the_move, p.81, ch.6], [leverage_for_the_long_run, p.13],
  [advances_fin_ml, p.208-211, p.298-299]

## Signal components (all z-scored, 252-bar rolling window)

| Component | Formula | Warmup bars | Bullish when |
|-----------|---------|-------------|--------------|
| slope_MA200 | (SMA200_t − SMA200_{t−20}) / SMA200_{t−20}, z-scored | 472 | MA accelerating up |
| mom_90d | SPY.pct_change(90), z-scored | 342 | 90d return positive |
| inv_vol | 1/TQQQ_vol_20d, z-scored | 272 | TQQQ is calm/trending |

## Weight triplets

| # | Config | w_slope | w_mom | w_invvol |
|---|--------|---------|-------|----------|
| 1 | equal_weight | 1/3 | 1/3 | 1/3 |
| 2 | trend_heavy | 0.5 | 0.3 | 0.2 |
| 3 | mom_heavy | 0.2 | 0.6 | 0.2 |

## Results vs D2 baseline

D2 sma200_gld (iter 4): Sharpe=0.918 Sharpe_net=0.780 MaxDD=-60.3% Calmar=0.608 WF=7/8
D6 target: Sharpe_net > 0.800 (need gross > 0.941, gap +0.023 from D2)

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| equal_weight | 21.07 | 17.91 | 0.731 | 0.621 | -43.1 | 0.489 | 7/8 | 0.87 | -1.73 | 0.341 | 0.020 | ✓ | ✗ | ✗ | ✗ |
| trend_heavy | 31.01 | 26.36 | 0.938 | 0.797 | -42.4 | 0.731 | 7/8 | 1.25 | -1.14 | 0.341 | 0.002 | ✓ | ✓ | ✗ | ✗ |
| mom_heavy | 23.92 | 20.33 | 0.788 | 0.670 | -42.3 | 0.565 | 7/8 | 1.01 | -1.65 | 0.341 | 0.011 | ✓ | ✓ | ✗ | ✗ |

**SPY B&H net CAGR threshold:** 10.36% (15% IR BR applied)

## Cross-lib concordance (bt library)

- equal_weight: ✓ CONCORDANT (ΔCAGR=0.14pp)
- trend_heavy: ✓ CONCORDANT (ΔCAGR=0.72pp)
- mom_heavy: ✓ CONCORDANT (ΔCAGR=1.23pp)

## Stage 2 — yfinance independent validation

- equal_weight: ✓ CONCORDANT (ΔCAGR=0.44pp)
- trend_heavy: ✗ DIVERGENT (ΔCAGR=4.05pp)
- mom_heavy: ✓ CONCORDANT (ΔCAGR=1.52pp)

## TQQQ time-in-market (% of days in TQQQ)

| Config | Avg TQQQ weight% |
|--------|-----------------|
| equal_weight | 48.5% |
| trend_heavy | 51.5% |
| mom_heavy | 49.4% |

## Analysis

D6 hypothesis: adding momentum + inverse-vol z-scores to the pure SMA200 signal
produces a smarter binary switch. In regimes where SPY is just barely above SMA200
but momentum is negative or vol is high, the composite score goes negative → stays
in GLD → avoids whipsaw losses. The net effect should be +0.020 Sharpe_net.

Key difference from D2: D2 uses a single binary signal (SPY > SMA200).
D6 uses a composite of 3 signals, each z-scored for comparability.
Both are binary switches → should produce similar low PBO.
