# D3 Donchian Breakout — TQQQ+GLD (iter 7) [SWING BROKER]

**Strategy:** Long TQQQ on Donchian upper-channel breakout; GLD on lower-channel breakdown
**Window:** 2004-11-18 → 2026-04-15 (21.4yr, reference_prices.parquet Stage 1)
**Portfolio:** TQQQ (on-regime) + GLD (off-regime); signal on TQQQ close
**Best config:** `dc20_10` — **NO PASS**
**PBO:** 0.107 (PASS)

Citations: [trading_systems_methods, p.353], [stocks_on_the_move, p.81],
  [advances_fin_ml, p.208-211, p.298-299]

## Results

| Config | Entry | Exit | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-------|------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| dc20_10 | 20 | 10 | 23.94 | 20.35 | 0.795 | 0.676 | -47.2 | 0.507 | 7/8 | 0.96 | 1.02 | 0.107 | 0.005 | ✓ | ✓ | ✗ | ✗ |
| dc40_20 | 40 | 20 | 22.44 | 19.07 | 0.759 | 0.646 | -42.6 | 0.527 | 7/8 | 0.99 | 0.65 | 0.107 | 0.008 | ✓ | ✓ | ✗ | ✗ |
| dc60_30 | 60 | 30 | 13.85 | 11.77 | 0.542 | 0.461 | -54.8 | 0.253 | 8/8 | 0.93 | 0.63 | 0.107 | 0.076 | ✓ | ✗ | ✗ | ✗ |
| dc80_40 | 80 | 40 | 17.13 | 14.56 | 0.613 | 0.521 | -53.7 | 0.319 | 8/8 | 0.79 | 0.63 | 0.107 | 0.040 | ✓ | ✗ | ✗ | ✗ |

**SPY B&H net CAGR threshold:** 7.31% (15% IR BR applied)

## Cross-lib concordance (bt library)

- dc20_10: ✗ DIVERGENT (ΔCAGR=3.58pp)
- dc40_20: ✓ CONCORDANT (ΔCAGR=2.91pp)
- dc60_30: ✓ CONCORDANT (ΔCAGR=0.30pp)
- dc80_40: ✓ CONCORDANT (ΔCAGR=2.36pp)

## Stage 2 — yfinance independent validation

- dc20_10: ✓ CONCORDANT (ΔCAGR=1.08pp)
- dc40_20: ✓ CONCORDANT (ΔCAGR=1.96pp)
- dc60_30: ✓ CONCORDANT (ΔCAGR=1.71pp)
- dc80_40: ✗ DIVERGENT (ΔCAGR=3.14pp)
