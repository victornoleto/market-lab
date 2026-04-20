# BLOCKED-INVESTIGATE: plano_b_v4_threshold_10

**Generated:** 2026-04-20  
**Wave / Stage:** Wave 1 / Stage 1  
**Variant:** plano_b_v4_threshold_10 (canonical + extended windows)  
**Trigger:** REFUTES from bt, vectorbt, quantstats_from_bt, quantstats_from_vectorbt (max_dd ≥ 25%)

## Observed results vs baseline

| lib | window | cagr | sharpe | max_dd | tier |
|-----|--------|------|--------|--------|------|
| **baseline** | canonical | 37.92% | 1.973 | -16.91% | — |
| bt | canonical | 11.6% | 0.784 | **-28.8%** | REFUTES |
| vectorbt | canonical | 11.6% | 0.785 | **-28.8%** | REFUTES |
| backtrader | canonical | 26.4% | 1.761 | -18.2% | WARNING |
| **baseline** | extended | 26.96% | 2.028 | -10.12% | — |
| bt | extended | 6.0% | 0.534 | **-28.8%** | REFUTES |
| vectorbt | extended | 6.0% | 0.535 | **-28.8%** | REFUTES |
| backtrader | extended | 13.3% | 1.282 | -18.2% | REFUTES (max_dd > 10.12% baseline by >3pp but classifies REFUTES due to dsr/wf) |

## First divergent date

**2006-06-21** — SSO inception date (first real yfinance price entry in reference_prices.parquet).

The price series jumps discontinuously:
- Last synthetic close (2006-06-20): **154.94**  
- First real yfinance close (2006-06-21): **3.65**

This is a **42.5× artificial price collapse** at the stitching seam. The synthetic series started at 10.0 (arbitrary) and compounded to 154.94 by the SSO inception date. The yfinance real price begins at the actual market price of $3.65.

Similarly for QLD: synthetic 3.75 → real 0.98 (3.8× drop on 2006-06-21).  
For UGL: synthetic 20.20 → real 6.21 (3.3× drop on 2008-12-03).

## Root-cause hypothesis

**Bug: reference_prices.py — no level-normalization at synthetic/real stitch point.**

`_synthetic_pre_inception()` in `reports/phase_3_5c/cross_lib/data/reference_prices.py` (line 221):
```python
prices = (1.0 + synth_rets).cumprod() * 10.0  # arbitrary start value
```

The synthetic series uses an **arbitrary 10.0 start value** and grows independently. The `_real_post_inception()` function fetches yfinance prices at their actual market levels (e.g. SSO at $3.65 at inception). `build_reference_prices()` then concatenates the two series with `pd.concat([synthetic, real])` and deduplicates by date — without scaling the synthetic portion to connect smoothly at the splice.

This is **not** an adapter bug and **not** an engine paradigm difference. The same broken data is used by all three bar-level adapters (bt, vectorbt, backtrader). Backtrader shows less damage likely because its threshold-mode rebalance does not re-check portfolio value drift (it compares signal-derived target weights rather than actual portfolio weights), so it does not rebalance into the crashed position at the splice date.

## Required fix (out of scope for Task 22)

In `reference_prices.py :: _synthetic_pre_inception()`, scale the synthetic series so that its terminal value (at inception date - 1 day) equals the first real yfinance close price at inception. Specifically:

```python
# After computing prices from cumprod:
first_real_price = <fetch yfinance at inception date>
prices = prices * (first_real_price / prices.iloc[-1])
```

Alternatively, `build_reference_prices()` should apply a scalar adjustment to the synthetic segment after stitching: `scale = real.iloc[0]['close'] / synthetic.iloc[-1]['close']`.

## Impact

All Wave 1 variants are affected because all use SSO (every variant through plano_b legs) or QLD/UGL (multi-leg variants). The reference_prices.parquet must be rebuilt after fixing the stitching before re-running Wave 1.

## Verdict: BLOCKED — do not proceed to Wave 2

Per decision gate in Task 22: this constitutes an adapter/data bug that causes systematic REFUTES across bt and vectorbt for all variants. Must fix `reference_prices.py` and regenerate `reference_prices.parquet` before re-running.

**Citations:**
- Data integrity requirement for cross-lib validation: `[advances_fin_ml, p.31-34]`
- Price series stitching methodology: `[leverage_for_the_long_run, p.16]`
