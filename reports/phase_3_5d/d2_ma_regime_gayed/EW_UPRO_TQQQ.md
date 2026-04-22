# EW_UPRO_TQQQ daily — D2 MA Regime Gayed (iter 3) [SWING BROKER]

**Window:** 2010-02-11 → 2026-04-17 (16.2y, reference_prices.parquet Stage 1)
**Portfolio:** 50% UPRO + 50% TQQQ, MA regime filter on SPY→UPRO, QQQ→TQQQ
**Best config:** `sma200_gld` — **NO PASS**
**PBO:** 0.119 (PASS)

Citations: [leverage_for_the_long_run, p.13, p.16, p.60]
  [advances_fin_ml, p.208-211, p.298-299]

## All configs tested

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Calmar>0.5 | Sharpe_net>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|-----------|----------------|------|
| sma200_cash | 25.57 | 21.74 | 0.800 | 0.680 | -51.0 | 0.502 | 7/8 | 1.14 | -0.09 | 0.119 | 0.030 | ✓ | ✓ | ✗ | ✗ |
| ema100_cash | 23.40 | 19.89 | 0.765 | 0.650 | -47.0 | 0.498 | 7/8 | 1.11 | -0.34 | 0.119 | 0.041 | ✓ | ✗ | ✗ | ✗ |
| sma200_tmf | 20.38 | 17.33 | 0.640 | 0.544 | -83.8 | 0.243 | 7/8 | 1.07 | 0.06 | 0.119 | 0.104 | ✓ | ✗ | ✗ | ✗ |
| ema100_tmf | 18.81 | 15.99 | 0.614 | 0.522 | -82.3 | 0.229 | 6/8 | 0.88 | -0.10 | 0.119 | 0.124 | ✓ | ✗ | ✗ | ✗ |
| sma200_gld | 31.46 | 26.74 | 0.909 | 0.773 | -56.3 | 0.559 | 7/8 | 1.28 | 0.26 | 0.119 | 0.011 | ✓ | ✓ | ✗ | ✗ |
| ema100_gld | 28.29 | 24.04 | 0.860 | 0.731 | -46.7 | 0.606 | 7/8 | 1.13 | -0.89 | 0.119 | 0.017 | ✓ | ✓ | ✗ | ✗ |

## SPY Benchmark (D1 reference)

| SPY CAGR% | SPY CAGR_net% | SPY Sharpe | SPY MaxDD% |
|-----------|--------------|------------|-----------|
| 12.22 | 10.39 | 0.756 | 34.1 |

## Cross-lib concordance (bt library)

- sma200_cash: ✓ CONCORDANT (ΔCAGR=0.54pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=0.95pp)
- sma200_tmf: ✓ CONCORDANT (ΔCAGR=1.11pp)
- ema100_tmf: ✓ CONCORDANT (ΔCAGR=0.23pp)
- sma200_gld: ✓ CONCORDANT (ΔCAGR=0.58pp)
- ema100_gld: ✓ CONCORDANT (ΔCAGR=1.51pp)

## Stage 2 — yfinance independent validation

- sma200_cash: ✓ CONCORDANT (ΔCAGR=1.86pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=1.83pp)
- sma200_tmf: ✓ CONCORDANT (ΔCAGR=2.26pp)
- ema100_tmf: ✓ CONCORDANT (ΔCAGR=1.99pp)
- sma200_gld: ✓ CONCORDANT (ΔCAGR=1.36pp)
- ema100_gld: ✓ CONCORDANT (ΔCAGR=1.36pp)
