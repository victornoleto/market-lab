# BLOCKED-INVESTIGATE: leg_sso_only

**Generated:** 2026-04-20  
**Wave / Stage:** Wave 1 / Stage 1  
**Variant:** leg_sso_only (canonical + extended windows)  
**Trigger:** REFUTES from bt, vectorbt, quantstats_from_bt, quantstats_from_vectorbt

## Observed results vs baseline

| lib | window | cagr | sharpe | max_dd | tier |
|-----|--------|------|--------|--------|------|
| **baseline** | canonical | 44.69% | 1.848 | -20.55% | — |
| bt | canonical | 10.2% | 0.556 | **-43.8%** | REFUTES |
| vectorbt | canonical | 10.2% | 0.556 | **-43.8%** | REFUTES |
| backtrader | canonical | 27.0% | 1.297 | -18.6% | WARNING |

## Root cause

Same as `BLOCKED-plano_b_v4_threshold_10.md` — the reference_prices.parquet SSO series has a 42.5× artificial price collapse at the 2006-06-21 stitching point. The SSO-only single-leg variant amplifies the effect because there is no diversification from QLD or UGL.

## Verdict: BLOCKED — see BLOCKED-plano_b_v4_threshold_10.md for full analysis
