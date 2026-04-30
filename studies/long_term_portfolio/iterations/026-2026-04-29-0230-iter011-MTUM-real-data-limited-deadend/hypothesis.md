# Iter 026 — DATA-LIMITED DEAD-END (MTUM/SPMO/IDMO unavailable)

**Hypothesis slug**: `iter011-MTUM-real-investable-momentum`
**Status**: **DATA-LIMITED DEAD-END** — backtest never run.
**Cumulative n_trials at start**: 94 (post-iter 025)

## Original hypothesis (cancelled)

iter 016 found UMD academic momentum factor delivered Sharpe 1.223 lh_56y
loose / 1.133 strict — first +signal vs iter 011 since the substantive
incumbent was set. UMD is academic (long-short Fama-French, gross-of-cost),
NOT investable. Real-product proxies:
- **MTUM** (BlackRock iShares MSCI USA Momentum Factor ETF, live 2013-04+)
- **SPMO** (Invesco S&P 500 Momentum ETF, live 2015-10+)
- **IDMO** (Invesco S&P International Developed Momentum ETF, live 2015-08+)

Plan was to test 4 configs sweep MTUM 10/15/20/25% on iter 011 base
(substituting from KMLM, mirroring iter 016 grid). Expected edge to drop
from +0.088 lh_56y (UMD academic strict) to ~+0.02-0.05 (MTUM real),
quantifying the long-only + cost gap.

## Why data-limited dead-end

Pre-run inventory (2026-04-29 02:30 UTC):

| ticker | Tiingo cache | Testfolio synth | API pull |
|---|---|---|---|
| MTUM | ❌ MISSING | ❌ MISSING | ❌ TIINGO_API_KEY empty (subscription cancelled) |
| SPMO | ❌ MISSING | ❌ MISSING | ❌ same |
| IDMO | ❌ MISSING | ❌ MISSING | ❌ same |
| MTUMSIM | ❌ MISSING | ❌ MISSING | n/a (no testfolio synth) |

Tiingo bulk download script (`scripts/tiingo_bulk_download.py`) inventory:
broad ETFs (SPY/IVV/VOO/QQQ/IWM/DIA/VTI/EFA/EEM/VEA/VWO), sector SPDRs (XL*),
bonds (AGG/TLT/IEF/LQD/HYG/SHV), commodities/vol (GLD/SLV/USO/UNG/VXX),
leveraged (SSO/QLD/UPRO/TQQQ). **No factor ETFs** in any bucket.

Testfolio cache: VTSIM/SPYSIM/QQQSIM/VEASIM/VWOSIM/VBRSIM/IEFSIM/TLTSIM/
GLDSIM/KMLMSIM/DBMFSIM/EFVSIM/RSSBSIM/CASHX. **No momentum factor synth.**

Without API access (subscription gone), MTUM/SPMO/IDMO cannot be pulled
on-demand. Without testfolio synth, the legacy academic UMD proxy
(`ff_momentum_proxy.py` from iter 016) is the closest available — but that's
exactly what iter 016 already tested and yielded +0.088 academic edge.

## Implications

1. **iter 016 UMD academic edge (+0.088 lh_56y, +0.047 ndx_real, −0.016
   vt_real strict)** stays the best information we have on momentum factor
   for this universe.

2. **Gap to deployable**: per `[stocks_on_the_move, p.21-30]` Clenow + Frazzini-
   Israel-Moskowitz 2018 (Trading Costs of Asset Pricing Anomalies), MTUM/SPMO
   capture ~60-70% of UMD edge after long-only constraint + 10-30bp/yr turnover.
   Estimated MTUM real edge: ~+0.05 lh_56y, marginal but positive.

3. **Future reactivation**: if Tiingo subscription resumes OR if we add
   MTUMSIM testfolio synth (would need to construct from iShares prospectus
   + MSCI Momentum Index history), iter 026 can be re-run. Until then,
   B.5 momentum direction is **paused with iter 016 academic positive
   signal as the standing reference**.

## Comparison to iter 021 (other data-limited dead-end)

| iter | direction | data limit |
|---|---|---|
| 021 (C.4 sector rotation) | 4-sector restricted to XLE/XLF/XLK/XLU | Tiingo has 5 other sectors only since 2014 |
| 026 (B.4 MTUM real) | 0/3 momentum ETFs available | Tiingo cache + testfolio synth both missing |

iter 021 had a partial test (4 sectors did fail to outperform iter 011);
iter 026 has zero data, so no run was attempted.

## Citations

- iter 016 (UMD academic) — closest proxy; +0.088 lh_56y strict edge stays
  the standing momentum signal until investable data becomes available
- `[stocks_on_the_move, p.21-30]` Clenow time-series momentum
- Jegadeesh-Titman 1993 cross-sectional momentum
- Frazzini-Israel-Moskowitz 2018 (Trading Costs of Asset Pricing Anomalies)
  — quantifies long-only constraint + turnover cost on factor strategies

## Status

`status: data_limited`. No verdict.json produced — build_zoo_plot.py skips
iters without verdict.json so this entry is documentation-only.
