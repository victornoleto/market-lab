# BLOCKED-INVESTIGATE: leg_qld_only

**Generated:** 2026-04-20  
**Wave / Stage:** Wave 1 / Stage 1  
**Variant:** leg_qld_only (canonical window)  
**Trigger:** REFUTES from all libs (max_dd >> 25%)

## Observed results vs baseline

| lib | window | cagr | sharpe | max_dd | tier |
|-----|--------|------|--------|--------|------|
| **baseline** | canonical | 17.40% | 1.389 | -12.79% | — |
| bt | canonical | 11.7% | 0.613 | **-40.3%** | REFUTES |
| vectorbt | canonical | 11.7% | 0.613 | **-40.3%** | REFUTES |
| backtrader | canonical | 26.2% | 1.269 | **-30.3%** | REFUTES |

## Root cause

Same as `BLOCKED-plano_b_v4_threshold_10.md` — the QLD series has a 3.8× artificial price collapse at the 2006-06-21 stitching point (synthetic 3.75 → real 0.98). Backtrader also shows REFUTES here (max_dd -30.3% vs baseline -12.79%) because the QLD/QQQ data starts at inception with no synthetic pre-history needed (QQQ starts 2001), making the jump smaller but still materialy distorting.

## Verdict: BLOCKED — see BLOCKED-plano_b_v4_threshold_10.md for full analysis
