# D5 Volatility Targeting — TQQQ+GLD (iter 9) [SWING BROKER]

**Strategy:** Continuous vol-scaled TQQQ exposure; GLD fills remainder
  weight_TQQQ = min(1.0, target_vol / realized_vol_TQQQ)
**Window:** 2004-11-18 → 2026-04-15 (21.4yr, reference_prices.parquet Stage 1)
**Portfolio:** TQQQ (vol-scaled on-regime) + GLD (complement); daily rebalance
**Best config:** `vol15_lk20` — **NO PASS**
**PBO:** 0.599 (FAIL)

Citations: [advances_fin_ml, ch.14], [volatility_trading],
  [leverage_for_the_long_run, p.13], [advances_fin_ml, p.208-211, p.298-299]

## Results

| Config | TV% | LB | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-----|-----|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| vol15_lk10 | 15 | 10 | 19.99 | 16.99 | 0.928 | 0.789 | -37.3 | 0.537 | 8/8 | 1.06 | 0.22 | 0.599 | 0.002 | ✓ | ✓ | ✗ | ✗ |
| vol15_lk20 | 15 | 20 | 21.34 | 18.14 | 1.006 | 0.855 | -37.2 | 0.573 | 8/8 | 1.17 | 0.18 | 0.599 | 0.001 | ✓ | ✓ | ✓ | ✗ |
| vol15_lk30 | 15 | 30 | 20.63 | 17.53 | 0.988 | 0.840 | -37.7 | 0.548 | 8/8 | 1.18 | 0.22 | 0.599 | 0.001 | ✓ | ✓ | ✓ | ✗ |
| vol20_lk10 | 20 | 10 | 22.21 | 18.88 | 0.897 | 0.763 | -44.0 | 0.505 | 8/8 | 0.92 | 0.06 | 0.599 | 0.003 | ✓ | ✓ | ✗ | ✗ |
| vol20_lk20 | 20 | 20 | 23.95 | 20.36 | 0.977 | 0.830 | -43.9 | 0.545 | 8/8 | 1.03 | 0.01 | 0.599 | 0.001 | ✓ | ✓ | ✓ | ✗ |
| vol20_lk30 | 20 | 30 | 23.20 | 19.72 | 0.961 | 0.817 | -44.5 | 0.521 | 8/8 | 1.05 | 0.05 | 0.599 | 0.001 | ✓ | ✓ | ✓ | ✗ |
| best_sma200 | 15 | 20 | 19.50 | 16.57 | 0.956 | 0.813 | -30.2 | 0.646 | 8/8 | 1.17 | 0.14 | 0.599 | 0.001 | ✓ | ✓ | ✓ | ✗ |

**SPY B&H net CAGR threshold:** 7.31% (15% IR BR applied)

## Cross-lib concordance (bt library)

- vol15_lk10: ✓ CONCORDANT (ΔCAGR=0.65pp)
- vol15_lk20: ✓ CONCORDANT (ΔCAGR=0.15pp)
- vol15_lk30: ✓ CONCORDANT (ΔCAGR=0.07pp)
- vol20_lk10: ✓ CONCORDANT (ΔCAGR=0.60pp)
- vol20_lk20: ✓ CONCORDANT (ΔCAGR=0.06pp)
- vol20_lk30: ✓ CONCORDANT (ΔCAGR=0.04pp)
- best_sma200: ✓ CONCORDANT (ΔCAGR=0.08pp)

## Stage 2 — yfinance independent validation

- vol15_lk10: ✓ CONCORDANT (ΔCAGR=2.42pp)
- vol15_lk20: ✓ CONCORDANT (ΔCAGR=2.23pp)
- vol15_lk30: ✓ CONCORDANT (ΔCAGR=1.91pp)
- vol20_lk10: ✗ DIVERGENT (ΔCAGR=4.08pp)
- vol20_lk20: ✗ DIVERGENT (ΔCAGR=3.81pp)
- vol20_lk30: ✗ DIVERGENT (ΔCAGR=3.43pp)
- best_sma200: ✓ CONCORDANT (ΔCAGR=2.30pp)

## Average TQQQ weight (time-in-market proxy)

| Config | Avg TQQQ weight% | Min weight% | Max weight% |
|--------|------------------|-------------|-------------|
| vol15_lk10 | 35.5 | 0.0 | 100.0 |
| vol15_lk20 | 32.8 | 0.0 | 100.0 |
| vol15_lk30 | 31.7 | 0.0 | 94.1 |
| vol20_lk10 | 46.4 | 0.0 | 100.0 |
| vol20_lk20 | 43.6 | 0.0 | 100.0 |
| vol20_lk30 | 42.2 | 0.0 | 100.0 |
| best_sma200 | 27.5 | 0.0 | 100.0 |
