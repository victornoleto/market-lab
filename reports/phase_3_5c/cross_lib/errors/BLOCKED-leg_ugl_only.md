# BLOCKED-INVESTIGATE: leg_ugl_only

**Generated:** 2026-04-20  
**Wave / Stage:** Wave 1 / Stage 1  
**Variant:** leg_ugl_only (canonical window)  
**Trigger:** REFUTES from all libs (max_dd >> 25%, sharpe ≤ 1)

## Observed results vs baseline

| lib | window | cagr | sharpe | max_dd | tier |
|-----|--------|------|--------|--------|------|
| **baseline** | canonical | 11.46% | 0.937 | -14.35% | — |
| bt | canonical | 8.2% | 0.448 | **-51.9%** | REFUTES |
| vectorbt | canonical | 8.3% | 0.448 | **-51.9%** | REFUTES |
| backtrader | canonical | 11.0% | 0.561 | **-41.5%** | REFUTES |

## Root cause

Same as `BLOCKED-plano_b_v4_threshold_10.md` — the UGL series has a 3.3× artificial price collapse at the 2008-12-03 stitching point (synthetic 20.20 → real 6.21). UGL is especially sensitive because the synthetic phase covers 2004-2008 and the splice occurs right at the peak of the financial crisis.

## Verdict: BLOCKED — see BLOCKED-plano_b_v4_threshold_10.md for full analysis
