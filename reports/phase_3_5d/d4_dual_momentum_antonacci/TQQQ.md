# D4 Absolute Momentum (Antonacci) — TQQQ+GLD (iter 8) [SWING BROKER]

**Strategy:** Monthly absolute momentum filter. Long TQQQ if trailing N-month return > 0; else hold GLD.
**Window:** 2004-11-18 → 2026-04-15 (21.4yr, reference_prices.parquet Stage 1)
**Portfolio:** TQQQ (on-regime) + GLD (off-regime); signal on QQQ or TQQQ
**Best config:** `mom12_qqq` — **NO PASS**
**PBO:** 0.778 (FAIL)

Citations: [antonacci_dual_momentum, p.62], [leverage_for_the_long_run, p.13],
  [advances_fin_ml, p.208-211, p.298-299]

## Results

| Config | LB | Sig | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-----|-----|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| mom6_qqq | 6 | QQQ | 17.18 | 14.61 | 0.571 | 0.486 | -76.2 | 0.226 | 8/8 | 0.28 | -1.70 | 0.778 | 0.093 | ✓ | ✗ | ✗ | ✗ |
| mom9_qqq | 9 | QQQ | 21.57 | 18.34 | 0.641 | 0.545 | -69.9 | 0.309 | 8/8 | 0.54 | 0.31 | 0.778 | 0.050 | ✓ | ✗ | ✗ | ✗ |
| mom12_qqq | 12 | QQQ | 23.54 | 20.01 | 0.665 | 0.565 | -69.9 | 0.337 | 8/8 | 0.41 | 0.31 | 0.778 | 0.039 | ✓ | ✗ | ✗ | ✗ |
| mom6_tqqq | 6 | TQQQ | 18.72 | 15.91 | 0.603 | 0.512 | -69.9 | 0.268 | 8/8 | 0.53 | -1.70 | 0.778 | 0.071 | ✓ | ✗ | ✗ | ✗ |
| mom9_tqqq | 9 | TQQQ | 19.18 | 16.31 | 0.609 | 0.518 | -69.9 | 0.274 | 8/8 | 0.59 | 0.31 | 0.778 | 0.067 | ✓ | ✗ | ✗ | ✗ |
| mom12_tqqq | 12 | TQQQ | 20.50 | 17.42 | 0.625 | 0.532 | -79.3 | 0.259 | 8/8 | 0.45 | 0.31 | 0.778 | 0.058 | ✓ | ✗ | ✗ | ✗ |

**SPY B&H net CAGR threshold:** 7.31% (15% IR BR applied)

## Cross-lib concordance (bt library)

- mom6_qqq: ✓ CONCORDANT (ΔCAGR=1.81pp)
- mom9_qqq: ✓ CONCORDANT (ΔCAGR=0.90pp)
- mom12_qqq: ✓ CONCORDANT (ΔCAGR=0.83pp)
- mom6_tqqq: ✓ CONCORDANT (ΔCAGR=1.10pp)
- mom9_tqqq: ✓ CONCORDANT (ΔCAGR=0.65pp)
- mom12_tqqq: ✓ CONCORDANT (ΔCAGR=0.16pp)

## Stage 2 — yfinance independent validation

- mom6_qqq: ✗ DIVERGENT (ΔCAGR=8.52pp)
- mom9_qqq: ✗ DIVERGENT (ΔCAGR=10.10pp)
- mom12_qqq: ✗ DIVERGENT (ΔCAGR=13.98pp)
- mom6_tqqq: ✗ DIVERGENT (ΔCAGR=8.13pp)
- mom9_tqqq: ✗ DIVERGENT (ΔCAGR=7.88pp)
- mom12_tqqq: ✗ DIVERGENT (ΔCAGR=5.07pp)
