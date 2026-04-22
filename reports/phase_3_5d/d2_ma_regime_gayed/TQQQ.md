# TQQQ daily — D2 MA Regime Gayed (iter 4) [SWING BROKER]

**Window:** 2010-02-11 → 2026-04-17 (16.2y, reference_prices.parquet Stage 1)
**Portfolio:** 100% TQQQ, MA regime filter on QQQ
**Best config:** `sma200_gld` — **NO PASS**
**PBO:** 0.115 (PASS)

Citations: [leverage_for_the_long_run, p.13, p.16, p.60]
  [advances_fin_ml, p.208-211, p.298-299]

## All configs tested

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Calmar>0.5 | Sharpe_net>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|-----------|----------------|------|
| sma200_cash | 30.56 | 25.98 | 0.824 | 0.700 | -54.8 | 0.558 | 7/8 | 1.19 | -0.05 | 0.115 | 0.024 | ✓ | ✓ | ✗ | ✗ |
| ema100_cash | 27.32 | 23.22 | 0.781 | 0.664 | -46.9 | 0.582 | 7/8 | 1.05 | -1.02 | 0.115 | 0.035 | ✓ | ✓ | ✗ | ✗ |
| sma200_tmf | 24.37 | 20.71 | 0.684 | 0.581 | -85.0 | 0.287 | 7/8 | 1.09 | 0.31 | 0.115 | 0.076 | ✓ | ✗ | ✗ | ✗ |
| ema100_tmf | 23.72 | 20.16 | 0.678 | 0.576 | -82.7 | 0.287 | 8/8 | 0.99 | -0.38 | 0.115 | 0.079 | ✓ | ✗ | ✗ | ✗ |
| sma200_gld | 36.66 | 31.16 | 0.918 | 0.780 | -60.3 | 0.608 | 7/8 | 1.31 | 0.38 | 0.115 | 0.010 | ✓ | ✓ | ✗ | ✗ |
| ema100_gld | 31.84 | 27.06 | 0.855 | 0.726 | -54.9 | 0.580 | 7/8 | 1.07 | -1.15 | 0.115 | 0.018 | ✓ | ✓ | ✗ | ✗ |

## SPY Benchmark (D1 reference)

| SPY CAGR% | SPY CAGR_net% | SPY Sharpe | SPY MaxDD% |
|-----------|--------------|------------|-----------|
| 12.22 | 10.39 | 0.756 | 34.1 |

## Cross-lib concordance (bt library)

- sma200_cash: ✓ CONCORDANT (ΔCAGR=2.30pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=1.32pp)
- sma200_tmf: ✗ DIVERGENT (ΔCAGR=3.50pp)
- ema100_tmf: ✓ CONCORDANT (ΔCAGR=0.84pp)
- sma200_gld: ✓ CONCORDANT (ΔCAGR=1.90pp)
- ema100_gld: ✗ DIVERGENT (ΔCAGR=3.03pp)

## Stage 2 — yfinance independent validation

- sma200_cash: ✓ CONCORDANT (ΔCAGR=0.28pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=0.88pp)
- sma200_tmf: ✓ CONCORDANT (ΔCAGR=0.38pp)
- ema100_tmf: ✓ CONCORDANT (ΔCAGR=0.07pp)
- sma200_gld: ✓ CONCORDANT (ΔCAGR=0.73pp)
- ema100_gld: ✓ CONCORDANT (ΔCAGR=1.22pp)
