# Iter 052 — Momentum/SCV sleeves on B4

**Date:** 2026-05-03
**Source:** testfol.io API; monthly rebalance; explicit estimated ER drag.
**Status:** screening only, not full PBO/DSR/WF/bootstrap gate-equivalent.

## Verdict

Momentum is a credible research direction, but the evidence splits into three
quality tiers:

1. **SPMO live is genuinely interesting but still short-window.** From
   2015-10-12 to 2026-05-01 it beat SPY on both CAGR and drawdown: 18.49% /
   -30.94% / Sharpe 0.848 versus SPY 14.72% / -33.70% / 0.740. It also beat
   SSO on risk-adjusted quality: SSO had 22.79% CAGR but -59.34% MDD and lower
   Sharpe 0.696.
2. **FMTM is not promotable yet.** It won the 2025-03-20 -> 2026-05-01 common
   window, but 1.11 years is not a retirement-horizon sample. Monthly
   constituent rotation is mechanically appealing, but it increases turnover,
   tax sensitivity, and live-regime dependence.
3. **Long synthetic momentum confirms the factor but not a free lunch.**
   MTUMSIM beat SPYSIM over 1994-2026 on CAGR/Sharpe, but had essentially the
   same crash profile: 13.35% / -56.10% / 0.602 versus SPYSIM 10.96% / -55.20%
   / 0.517.

For B4 specifically, the cleanest screening result is **small SPMO funded from
ZROZ**, not FMTM or LCG. In the 2022+ SPMO-limited window, B4 + 10% SPMO from
ZROZ improved B4 from 10.01% / -24.65% / 0.417 to 13.88% / -22.76% / 0.619.
For the selected B4+BTC5, 5% SPMO from remaining ZROZ improved 12.28% /
-25.98% / 0.531 to 14.23% / -25.15% / 0.625. This is promising but still not
gate-equivalent because the window starts in 2022.

Practical implication: **do not replace B4/BTC5 yet**. If the user wants a
CAGR-maximizing satellite, the next pre-registered candidate should be:

```text
NTSX 25% / GDE 25% / RSST 25% / ZROZ 15% / BTC 5% / SPMO 5%
```

Treat `FMTM` as watchlist-only until it has enough live history or a reliable
index backfill/prospectus methodology can be reconstructed.

## standalone_spmo_live

Window: 2015-10-12 -> 2026-05-01 (10.55y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| SPMO | 18.49% | -30.94% | 0.848 | 0.598 |
| SCHG | 17.38% | -34.62% | 0.758 | 0.502 |
| SPY | 14.72% | -33.70% | 0.740 | 0.437 |
| SSO | 22.79% | -59.34% | 0.696 | 0.384 |

## standalone_fmtm_live

Window: 2025-03-20 -> 2026-05-01 (1.11y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| FMTM | 50.84% | -12.13% | 1.740 | 4.191 |
| SPMO | 38.48% | -15.37% | 1.379 | 2.503 |
| SPY | 25.93% | -13.72% | 1.125 | 1.889 |
| SSO | 44.87% | -26.18% | 1.110 | 1.714 |
| SCHG | 26.87% | -16.42% | 1.012 | 1.636 |

## standalone_sim

Window: 1994-06-01 -> 2026-05-01 (31.92y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| MTUMSIM | 13.35% | -56.10% | 0.602 | 0.238 |
| SPYSIM | 10.96% | -55.20% | 0.517 | 0.199 |
| VBRSIM | 11.26% | -61.99% | 0.500 | 0.182 |

## b4_screen_a

Window: 2022-03-17 -> 2026-05-01 (4.12y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| B4_spmo10_from_zroz | 13.88% | -22.76% | 0.619 | 0.610 |
| B4_mtum10_from_zroz | 13.17% | -23.31% | 0.578 | 0.565 |
| B4_spmo5_from_zroz | 11.94% | -23.62% | 0.521 | 0.505 |
| B4_spmo2p5_from_zroz | 10.98% | -24.06% | 0.470 | 0.456 |
| B4_base | 10.01% | -24.65% | 0.417 | 0.406 |

## b4_screen_b

Window: 2025-03-20 -> 2026-05-01 (1.11y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| B4_fmtm5_from_zroz | 31.46% | -11.65% | 1.373 | 2.700 |
| B4_vbr10_from_zroz | 31.94% | -12.47% | 1.363 | 2.562 |
| B4_avuv5_from_zroz | 30.69% | -11.97% | 1.340 | 2.565 |
| B4_fmtm2p5_from_zroz | 29.88% | -11.56% | 1.322 | 2.584 |
| B4_base | 28.31% | -11.48% | 1.267 | 2.467 |

## b4_btc_screen_a

Window: 2022-03-17 -> 2026-05-01 (4.12y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| B4_btc5_spmo5_from_zroz | 14.23% | -25.15% | 0.625 | 0.566 |
| B4_btc5_mtum5_from_zroz | 13.87% | -25.41% | 0.606 | 0.546 |
| B4_btc5_vbr5_from_zroz | 13.54% | -25.25% | 0.589 | 0.536 |
| B4_btc5_spmo2p5_from_zroz | 13.26% | -25.57% | 0.579 | 0.518 |
| B4_btc5 | 12.28% | -25.98% | 0.531 | 0.473 |

## b4_btc_screen_b

Window: 2025-03-20 -> 2026-05-01 (1.11y)

| strategy | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| B4_btc5_fmtm5_from_zroz | 32.03% | -12.11% | 1.347 | 2.645 |
| B4_btc5_avuv5_from_zroz | 31.25% | -12.46% | 1.315 | 2.508 |
| B4_btc5_fmtm2p5_from_zroz | 30.44% | -11.96% | 1.299 | 2.546 |
| B4_btc5_schg5_from_zroz | 30.91% | -12.46% | 1.296 | 2.481 |
| B4_btc5 | 28.87% | -11.81% | 1.249 | 2.445 |

## Caveats

- Live `SPMO`, `FMTM`, `AVUV`, and `SCHG` rows are inception-limited; do not compare them to 1987+/2000+ stress windows as if they were equivalent.
- `MTUMSIM` and `VBRSIM` are long synthetic factor proxies and are useful for stress shape, but they are not identical to live SPMO/FMTM/AVUV products.
- Replacing ZROZ with equity-like factor exposure mechanically raises equity beta and usually weakens crisis convexity.
