# D5b Vol-targeting Structural Diversity — TQQQ+GLD (iter 10) [SWING BROKER]

**Strategy:** 3 structurally diverse configs to test PBO hypothesis.
  D5 PBO=0.599 FAIL caused by 7 homogeneous vol-targeting configs.
  D5b uses 3 maximally diverse config families to push PBO < 0.5.
**Window:** 2004-11-18 → 2026-04-15 (21.4yr, reference_prices.parquet Stage 1)
**Portfolio:** TQQQ (signal-weighted) + GLD (complement); daily rebalance
**Best config:** `vol15_lk20` — **NO PASS**
**PBO:** 0.651 (FAIL)

Citations: [advances_fin_ml, ch.14], [volatility_trading],
  [leverage_for_the_long_run, p.13], [advances_fin_ml, p.208-211, p.298-299]

## Config families tested

| # | Name | Type | TV% | LB |
|---|------|------|-----|-----|
| 1 | sma200_gld | Binary MA-regime (no vol-scale) | — | — |
| 2 | vol15_lk20 | Pure vol-targeting | 15 | 20 |
| 3 | vol15_lk20_sma200 | Combo (vol-target × SMA200) | 15 | 20 |

## Results

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| sma200_gld | 26.30 | 22.36 | 0.760 | 0.646 | -63.7 | 0.413 | 8/8 | 0.47 | -0.00 | 0.651 | 0.004 | ✓ | ✗ | ✗ | ✗ |
| vol15_lk20 | 21.34 | 18.14 | 1.006 | 0.855 | -37.2 | 0.573 | 8/8 | 1.17 | 0.18 | 0.651 | 0.000 | ✓ | ✓ | ✓ | ✗ |
| vol15_lk20_sma200 | 19.50 | 16.57 | 0.956 | 0.813 | -30.2 | 0.646 | 8/8 | 1.17 | 0.14 | 0.651 | 0.000 | ✓ | ✓ | ✓ | ✗ |

**SPY B&H net CAGR threshold:** 7.31% (15% IR BR applied)

## Cross-lib concordance (bt library)

- sma200_gld: ✓ CONCORDANT (ΔCAGR=0.30pp)
- vol15_lk20: ✓ CONCORDANT (ΔCAGR=0.15pp)
- vol15_lk20_sma200: ✓ CONCORDANT (ΔCAGR=0.08pp)

## Stage 2 — yfinance independent validation

- sma200_gld: ✗ DIVERGENT (ΔCAGR=12.03pp)
- vol15_lk20: ✓ CONCORDANT (ΔCAGR=2.23pp)
- vol15_lk20_sma200: ✓ CONCORDANT (ΔCAGR=2.30pp)

## Average TQQQ weight (time-in-market proxy)

| Config | Avg TQQQ weight% | Min weight% | Max weight% |
|--------|------------------|-------------|-------------|
| sma200_gld | 74.4 | 0.0 | 100.0 |
| vol15_lk20 | 32.8 | 0.0 | 100.0 |
| vol15_lk20_sma200 | 27.5 | 0.0 | 100.0 |

## D5b Hypothesis analysis

D5 had 7 configs from the same family (vol-targeting, TV=15/20%, LB=10/20/30d).
With similar configs, any of the 7 can be the IS-best by small random differences,
but the OOS performance is nearly identical → PBO reflects selection noise.

D5b uses 3 config families with qualitatively different signal structures:
- Binary regime (sma200_gld): signal is 0 or 1, no continuous vol-scaling
- Pure vol-target (vol15_lk20): continuous weight, no regime gate
- Combo (vol15_lk20_sma200): vol-target dampened by regime gate

If vol15_lk20 dominates both sma200_gld and vol15_lk20_sma200 in OOS
consistently across CSCV blocks, PBO should be low (< 0.5).
