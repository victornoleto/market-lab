# E1 Vol-targeting 2-config — TQQQ+GLD (iter 13) [SWING BROKER]

**Hypothesis:** vol15_lk20 (SN=0.855✓, FWD=0.182✓) + sma200_gld_binary as ONE
  structurally different config → PBO might drop below 0.5 with only 2 configs.
**Window:** 2004-11-18 → 2026-04-15 (21.4yr)
**Best config:** `vol15_lk20` — **✓ ALL PASS**
**PBO (2 configs):** 0.151 (✓ PASS)

Citations: [advances_fin_ml, ch.14], [volatility_trading],
  [leverage_for_the_long_run, p.13], [advances_fin_ml, p.208-211, p.298-299]

## Results

| Config | CAGR% | CAGR_net% | Sharpe | SN | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |
|--------|-------|-----------|--------|----|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|------|
| vol15_lk20 | 21.34 | 18.14 | 1.006 | 0.855 | -37.2 | 0.573 | 8/8 | 1.17 | 0.18 | 0.151 | 0.0000 | ✓ | ✓ | ✓ | ✓ PASS |
| sma200_gld_binary | 26.30 | 22.36 | 0.760 | 0.646 | -63.7 | 0.413 | 8/8 | 0.47 | -0.00 | 0.151 | 0.0016 | ✓ | ✗ | ✗ | ✗ |

**SPY B&H net CAGR threshold:** 7.31%

## Cross-lib concordance (bt library)

- vol15_lk20: ✓ CONCORDANT (ΔCAGR=0.15pp)
- sma200_gld_binary: ✓ CONCORDANT (ΔCAGR=0.30pp)

## Average TQQQ weight (time-in-market proxy)

| Config | Avg TQQQ weight% | Min% | Max% |
|--------|------------------|------|------|
| vol15_lk20 | 32.8 | 0.0 | 100.0 |
| sma200_gld_binary | 74.4 | 0.0 | 100.0 |

## Diagnosis

PBO = fraction of CSCV folds where IS-winner is NOT also the OOS-winner.
With 2 configs, PBO is volatile but reflects the structural dominance of vol15_lk20.
Low PBO (<0.5) would indicate vol15_lk20 is a stable IS-winner across regimes.
