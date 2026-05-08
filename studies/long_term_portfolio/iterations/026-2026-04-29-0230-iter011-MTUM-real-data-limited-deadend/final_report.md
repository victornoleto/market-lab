# Iter 026 — Final Report — DATA-LIMITED DEAD-END

**Status**: `data_limited` — no backtest run. iter 026 was planned to test
investable momentum (MTUM/SPMO/IDMO) as a deployable substitute for iter 016's
academic UMD long-short factor, but **none of MTUM, SPMO, IDMO, or any
testfolio-style synth are available** in this environment.

See `hypothesis.md` for the full data-availability inventory.

---

## Summary

| ticker | Tiingo cache | Testfolio synth |
|---|:-:|:-:|
| MTUM (iShares MSCI USA Momentum) | ❌ | ❌ |
| SPMO (Invesco S&P 500 Momentum) | ❌ | ❌ |
| IDMO (Invesco S&P Intl Momentum) | ❌ | ❌ |
| MTUMSIM (testfolio synth) | n/a | ❌ |

Tiingo subscription cancelled (`TIINGO_API_KEY` empty) — no on-demand
pull available. Tiingo bulk download script inventory (32 ETFs across
broad/sector/bond/commodity/leveraged buckets) does not include factor
ETFs.

---

## What this means for the loop

1. **iter 016 UMD academic stays the standing momentum reference** —
   +0.088 lh_56y strict edge vs iter 011, +0.047 ndx_real, −0.016 vt_real.
   Best information available without investable data.

2. **B.5 direction is paused, not closed** — MTUM real test would have
   estimated edge ~+0.05 lh_56y (academic +0.088 × ~60% capture per
   Frazzini-Israel-Moskowitz 2018). That's a deferred reactivation
   dependent on Tiingo subscription resumption OR MTUMSIM synth being
   added to testfolio cache.

3. **Top-K standings unchanged** — substantive incumbent remains iter 011
   (NTSX+GDE+KMLM 35/25/40 static). Strongest non-iter-011 candidate from
   this batch is **iter 023 TLT-static 15%** (NEW STRONG 86, LEGACY WINNER 91,
   substantive +signal across 3/3 datasets vs iter 011).

---

## Citations

- iter 016 (UMD academic, B.5) — closest proxy result
- `[stocks_on_the_move, p.21-30]` Clenow time-series momentum
- Frazzini-Israel-Moskowitz 2018 — long-only constraint + turnover gap
