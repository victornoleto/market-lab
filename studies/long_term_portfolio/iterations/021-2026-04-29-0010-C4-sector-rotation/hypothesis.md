# Iter 021 — Hypothesis: C.4 — Sector rotation top-K monthly momentum

## Hypothesis

Test sector-level momentum rotation: monthly top-K from a sector universe by
trailing 6m momentum, equal-weight, abs-mom fallback to TLT when all top-K
have negative trailing momentum.

**Universe (data limitation):** Tiingo cache has only 4 SPDR sectors with
2003-08 inception (XLE Energy, XLF Financials, XLK Tech, XLU Utilities).
Other sectors (XLB Materials, XLI Industrials, XLP Staples, XLV Health,
XLY Discretionary) start 2014-01-02 in our cache — too short to include
without sacrificing the lh_56y window. Iter 021 uses the **4-sector core
universe** + TLT (Treasury fallback). Documented limitation: a 9-sector
sweep would require backfilling the 2014-only sectors via Yahoo Finance
(deferred).

## Pre-committed kill criteria

KILL #1: Best-of-grid loses iter 011 on ≥ 2/3 datasets.

KILL #2: 4-sector momentum signal converges to "always XLK" in 2010-2024
(US-tech dominance) — i.e., effectively a leveraged QQQ play, not a true
rotation. Diagnostic: pct_on per sector should not exceed ~50% for any
single sleeve.

## Configs (4)

| config | universe | K | fallback |
|---|---|---:|---|
| `sec4_K1_TLT`  | XLE/XLF/XLK/XLU | 1 | TLT (concentrated, risky) |
| `sec4_K2_TLT`  | XLE/XLF/XLK/XLU | 2 | TLT (balanced) |
| `sec4_K2_KMLM` | XLE/XLF/XLK/XLU | 2 | KMLMSIM (crisis-alpha fallback) |
| `sec4_K3_TLT`  | XLE/XLF/XLK/XLU | 3 | TLT (most diversified) |

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.

## Citations

- `[stocks_on_the_move, ch.6]` Clenow — sector momentum
- `[advances_fin_ml, p.208-211]` PBO discipline
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Probability assessment

- P(strict ADVANCE): ~10% — sector momentum has been studied extensively;
  4-sector universe is too narrow for diversification benefit.
- P(positive signal): ~20%.
- P(STRONG/PROMISING): ~50%.
- P(FAIL): ~20%.
