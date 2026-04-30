# iter 001 — Meta walk-forward max-Sharpe — DEAD_END (kill K3)

**Status:** DEAD_END. Kill criterion K3 fires: turnover 177-222%/yr **without
Sharpe edge**. Sharpe edges 0/3 datasets clear the +0.05 hurdle. DSR fails
on 2/3 datasets (vt_real p=0.062, ndx_real p=0.101) at n_trials=157
cumulative.

## Numbers

| Dataset | meta Sharpe | S1 Sharpe | edge | meta CAGR | meta MDD | S1 MDD | MDD Δ pp | turnover/yr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lh_56y | **1.137** | 1.125 | +0.012 | 10.31% | 17.42% | 19.91% | -2.48 | 177.2% |
| vt_real | 1.106 | 1.118 | -0.012 | 9.81% | 12.73% | 14.62% | -1.88 | 215.7% |
| ndx_real | 1.102 | 1.128 | -0.026 | 9.90% | 12.73% | 14.62% | -1.88 | 222.0% |

Period (lh_56y intersection): 2003-01-31 .. 2026-02-27 (~23.1y OOS). Warm-up
2000-01..2003-01 not counted (strict 36mo lookback).

## Gates summary

| Gate | Threshold | Result | Verdict |
|---|---|---|---|
| Sharpe edge ≥+0.05 vs S1 | ≥ 2/3 | 0/3 | ❌ FAIL |
| MDD Δ ≤ +3pp vs S1 | ≥ 2/3 | 3/3 | ✅ PASS |
| WF 8-fold winners | ≥ 6/8 min | 7/8 min | ✅ PASS |
| Bootstrap 99.9% CI low > 0 | all 3 | all 3 | ✅ PASS |
| DSR p < 0.05 (n=157) | all 3 | 1/3 | ❌ FAIL |
| Weight concentration > 80% | < 80% of months | 0% | ✅ PASS |
| Turnover w/o edge (K3) | ≤ 100%/yr OR edge ≥ +0.10 | 177-222%, edge < +0.10 | 🛑 **K3 FIRES** |
| MDD blow (K4) | ≤ +5pp | -2.48 to -1.88pp | ✅ PASS |

## Average weights (lh_56y)

```
S1_F1_SPLIT     26.4%
S2_TLT_static   18.2%
S3_AllWeather   29.2%
S4_SPMO_hybrid  11.0%
S5_RSST_heavy   15.2%
```

The solver does **not** degenerate to a single sleeve (kill K2 PASS) — it
actively diversifies. But the diversified allocation is essentially
equivalent to F1+SPLIT in risk-adjusted terms, so the dynamic decision-making
rediscovers the static optimum monthly **at the cost of 177-222%/yr
turnover**.

## Why no edge

Three structural reasons:

1. **F1+SPLIT is already near-optimal in our universe.** The 5 sleeves were
   curated from the long_term_portfolio sweep where every contender was
   already gate-screened against SPY-only Sharpe edge ≥+0.05. The Sharpe
   density across sleeves is too tight (1.10-1.14 mean) for dynamic
   allocation to find systematic alpha.
2. **36-month lookback Sharpe-max is noisy.** With sleeves whose true
   risk-adjusted returns are within ±0.05 of each other, 36mo of daily
   data gives a Sharpe estimate with std ≈ √(2/(N×36/252)) ≈ 0.05 — same
   order as the inter-sleeve Sharpe gap. The WF solver mostly trades on
   noise.
3. **Bestfolio's claimed 19.8% (Aggressive WF) comes from leveraged
   sleeves and a different universe.** Reproducing the architecture on
   our (more conservative, gate-screened) universe washes out the edge.

## Implications

- **Validates F1+SPLIT FINAL PICK from long_term_portfolio.** Static beats
  dynamic on this universe under our gates. F1+SPLIT remains deploy-ready
  candidate; this iter does NOT change that.
- **Refutes the meta-WF hypothesis** for the SPEC's max-Sharpe variant.
  The methodology works (no degeneration, real diversification) but the
  edge is not there.
- **MDD improvement is real but not enough.** Meta MDD is 1.88-2.48pp
  lower than S1 across all 3 datasets. Pure-MDD investor would prefer
  meta; risk-adjusted (Sharpe) investor wouldn't. Per mandate framework
  (CAGR/MDD = warning-only tiers), this isn't enough to override S1.

## Decision

Per SPEC §7 decision logic, iter 001 failure (no edge) suggests iter 002
with subset 3 sleeves (drop S5). However, kill K3 fires at iter 001 already
and the failure is structural (Sharpe density too tight in this universe),
so iter 002 is unlikely to invert the result. **Recommend closing the
vertente at iter 001** rather than burning n_trials on iter 002 (DSR
deflator already biting).

If user wants iter 002 anyway:
- Drop S5_RSST_heavy (lowest weight 15.2-25.3%, highest decay risk)
- Keep S1-S4
- Same solver params

If close: F1+SPLIT FINAL PICK from long_term_portfolio remains the only
deploy candidate. No change to mandate §1 maintenance mode.

## Citations

- bestfolio.app/blog/walk-forward-portfolios — base methodology
- `[advances_fin_ml, p.105-108]` — embargoed CV (21d gap honored)
- `[advances_fin_ml, p.196-202]` — bootstrap CI 99.9%
- `[advances_fin_ml, p.222-223]` — DSR n_trials cumulative
- `[risk_parity, ch.5]` — sleeve thesis (F1+SPLIT incumbent)
- `[leverage_for_the_long_run]` — LETF decay (relevant to sleeve construction)
