# Phase 4.0 — Cost sensitivity matrix (Caminho 3 Index CFD)

**Baseline:** commission=0 bps RT, spread_half=5 bps, swap=-0.008%/day, div_haircut=0% (Caminho 3 T3 config, all optimistic).

Each sweep holds the other 3 axes at baseline. Joint worst-case stresses all 4 simultaneously. Gate threshold (T3 sanity): OOS Sharpe ≥ 2.0, CAGR ≥ 30%, MDD ≤ -25%.

## Axis 1 — Commission (bps RT)

| Commission (bps RT) | $/side @ $1k notional | OOS Sharpe | OOS CAGR | OOS MDD | Gates |
|---:|---:|---:|---:|---:|:--:|
| 0 | $0.00 | 2.400 | 85.76% | -21.51% | ✅ |
| 5 | $0.03 | 2.335 | 82.29% | -21.51% | ✅ |
| 10 | $0.05 | 2.268 | 78.88% | -21.51% | ✅ |
| 20 | $0.10 | 2.134 | 72.24% | -21.51% | ✅ |
| 40 | $0.20 | 1.858 | 59.65% | -21.51% | ❌ |

## Axis 2 — Spread (half bps)

| Spread half (bps) | Total RT (bps) | OOS Sharpe | OOS CAGR | OOS MDD | Gates |
|---:|---:|---:|---:|---:|:--:|
| 5 | 10 | 2.400 | 85.76% | -21.51% | ✅ |
| 10 | 20 | 2.268 | 78.88% | -21.51% | ✅ |
| 15 | 30 | 2.134 | 72.24% | -21.51% | ✅ |
| 25 | 50 | 1.858 | 59.65% | -21.51% | ❌ |

## Axis 3 — Swap daily rate

| Swap daily (%) | Annualized (%) | OOS Sharpe | OOS CAGR | OOS MDD | Gates |
|---:|---:|---:|---:|---:|:--:|
| -0.5000% | -126.00% | 2.441 | 87.86% | -21.44% | ✅ |
| -0.8000% | -201.60% | 2.400 | 85.76% | -21.51% | ✅ |
| -1.5000% | -378.00% | 2.305 | 80.96% | -21.67% | ✅ |
| -2.5000% | -630.00% | 2.168 | 74.31% | -21.89% | ✅ |
| -4.0000% | -1008.00% | 1.963 | 64.80% | -22.22% | ❌ |

## Axis 4 — Dividend haircut

| Div haircut (%) | ~Annual drag | OOS Sharpe | OOS CAGR | OOS MDD | Gates |
|---:|---:|---:|---:|---:|:--:|
| 0% | 0.00%/yr | 2.400 | 85.76% | -21.51% | ✅ |
| 10% | 0.11%/yr | 2.397 | 85.61% | -21.52% | ✅ |
| 25% | 0.27%/yr | 2.393 | 85.39% | -21.52% | ✅ |
| 50% | 0.55%/yr | 2.385 | 85.01% | -21.54% | ✅ |
| 100% | 1.10%/yr | 2.370 | 84.25% | -21.56% | ✅ |

## Joint scenarios

| Scenario | Commission | Spread ½ | Swap | Div HC | OOS Sharpe | OOS CAGR | OOS MDD | Gates |
|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| baseline | 0 bps | 5 bps | -0.8000%/d | 0% | 2.400 | 85.76% | -21.51% | ✅ |
| joint_worst_case | 40 bps | 25 bps | -2.5000%/d | 50% | 1.042 | 28.07% | -29.65% | ❌ |
| middle_pessimistic | 10 bps | 10 bps | -1.5000%/d | 25% | 2.031 | 67.44% | -21.68% | ✅ |

## Viability envelope

- Total scenarios tested: 22
- Passing: 18
- Failing: 4

### Failing scenarios (where Caminho 3 breaks)

- **commission=40bps:** Sharpe=1.858, CAGR=59.65%, MDD=-21.51%
- **spread_half=25bps:** Sharpe=1.858, CAGR=59.65%, MDD=-21.51%
- **swap=-0.040/day:** Sharpe=1.963, CAGR=64.80%, MDD=-22.22%
- **joint_worst_case:** Sharpe=1.042, CAGR=28.07%, MDD=-29.65%


## Interpretation for $1k live trading

The matrix above answers: **'if Pepperstone Razor Index tier is worse than assumed, does the strategy still work at $1k?'**

### What a realistic 'pessimistic' case looks like

- Commission 10 bps RT = $0.50/side at $1k notional
- Spread half 10 bps = 20 bps RT (2× baseline)
- Swap -1.5000%/day = -378.00%/yr
  (~2× baseline, realistic for elevated Fed rates)
- Dividend haircut 25% (assumes Pepperstone captures 75% of yield)

→ OOS Sharpe **2.031** (threshold 2.0 for winner), CAGR **67.44%** (threshold 30%), MDD -21.68% (cap -25%).
→ Verdict: **STILL PASSES** at realistic pessimistic assumptions.
