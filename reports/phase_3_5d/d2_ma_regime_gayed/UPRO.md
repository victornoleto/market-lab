# UPRO daily — D2 MA Regime Gayed (iter 5) [SWING BROKER]

**Window:** 2010-02-11 → 2026-04-17 (16.2y, reference_prices.parquet Stage 1)
**Portfolio:** 100% UPRO, MA regime filter on SPY
**Best config:** `sma200_gld` — **NO PASS**
**PBO:** 0.115 (PASS)

Citations: [leverage_for_the_long_run, p.13, p.16, p.60]
  [advances_fin_ml, p.208-211, p.298-299]

## All configs tested

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Calmar>0.5 | Sharpe_net>0.8 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|-----------|----------------|------|
| sma200_cash | 18.78 | 15.96 | 0.685 | 0.582 | -52.6 | 0.357 | 7/8 | 1.01 | -0.13 | 0.115 | 0.077 | ✓ | ✗ | ✗ | ✗ |
| ema100_cash | 17.71 | 15.05 | 0.660 | 0.561 | -55.6 | 0.318 | 6/8 | 1.10 | 0.53 | 0.115 | 0.092 | ✓ | ✗ | ✗ | ✗ |
| sma200_tmf | 13.50 | 11.48 | 0.511 | 0.434 | -83.2 | 0.162 | 7/8 | 0.96 | -0.25 | 0.115 | 0.227 | ✓ | ✗ | ✗ | ✗ |
| ema100_tmf | 11.34 | 9.64 | 0.467 | 0.397 | -86.8 | 0.131 | 6/8 | 0.65 | 0.25 | 0.115 | 0.283 | ✗ | ✗ | ✗ | ✗ |
| sma200_gld | 24.36 | 20.70 | 0.807 | 0.686 | -53.2 | 0.458 | 7/8 | 1.16 | 0.11 | 0.115 | 0.029 | ✓ | ✗ | ✗ | ✗ |
| ema100_gld | 22.74 | 19.33 | 0.772 | 0.656 | -51.1 | 0.445 | 7/8 | 1.12 | -0.53 | 0.115 | 0.039 | ✓ | ✗ | ✗ | ✗ |

## SPY Benchmark (D1 reference)

| SPY CAGR% | SPY CAGR_net% | SPY Sharpe | SPY MaxDD% |
|-----------|--------------|------------|-----------|
| 12.22 | 10.39 | 0.756 | 34.1 |

## Cross-lib concordance (bt library)

- sma200_cash: ✓ CONCORDANT (ΔCAGR=2.90pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=0.67pp)
- sma200_tmf: ✗ DIVERGENT (ΔCAGR=5.03pp)
- ema100_tmf: ✓ CONCORDANT (ΔCAGR=1.19pp)
- sma200_gld: ✓ CONCORDANT (ΔCAGR=2.60pp)
- ema100_gld: ✓ CONCORDANT (ΔCAGR=0.20pp)

## Stage 2 — yfinance independent validation

- sma200_cash: ✗ DIVERGENT (ΔCAGR=3.89pp)
- ema100_cash: ✓ CONCORDANT (ΔCAGR=2.70pp)
- sma200_tmf: ✗ DIVERGENT (ΔCAGR=4.86pp)
- ema100_tmf: ✗ DIVERGENT (ΔCAGR=3.82pp)
- sma200_gld: ✗ DIVERGENT (ΔCAGR=3.36pp)
- ema100_gld: ✓ CONCORDANT (ΔCAGR=1.56pp)
