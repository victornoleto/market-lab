# Draft Post For r/ETF

**Title option 1:** I tested a capital-efficient ETF portfolio with BTC, small-cap value, and momentum satellites. Looking for criticism.

**Title option 2:** 15% NTSX / 25% GDE / 25% RSST / 10% ZROZ / 10% AVUV / 5% SPMO / 5% FMTM / 5% BTC: interesting or overfit?

---

I have been researching a long-term ETF portfolio that tries to combine capital-efficient diversification with a small return-seeking satellite.

The base portfolio is a static “B4” stack:

```text
25% NTSX
25% GDE
25% RSST
25% ZROZ
```

My current more aggressive idea is:

```text
15% NTSX
25% GDE
25% RSST
10% ZROZ
10% AVUV   # small-cap value sleeve
5%  SPMO   # momentum sleeve
5%  FMTM   # faster momentum sleeve
5%  BTC    # Bitcoin satellite
```

Because AVUV/SPMO/FMTM have limited live history and BTC is the limiting asset anyway, I tested the longer proxy version from 2010 onward. Since FMTM does not have long history, I used MTUMSIM as a proxy for the combined 10% momentum sleeve:

```text
15% NTSX
25% GDE
25% RSST
10% ZROZ
10% VBRSIM   # proxy for small-cap value
10% MTUMSIM  # proxy for SPMO + FMTM momentum sleeve
5%  BTCSIM
```

Monthly rebalance, dividends reinvested, explicit estimated ETF expense drag. I am not claiming this is tradable history for every sleeve; this is a proxy stress test.

## Results: 2010-2026

| Portfolio | CAGR | Max DD | Sharpe |
|---|---:|---:|---:|
| SPY | 14.71% | -33.70% | 0.893 |
| B4 base | 14.64% | -25.84% | 1.091 |
| B4 + 5% BTC | 23.18% | -27.26% | 1.472 |
| B4 + BTC + SCV + Momentum | 24.40% | -29.90% | 1.412 |
| ZROZ-only funding variant | 25.49% | -33.57% | 1.351 |

Images:

- Growth of $10k: `post_plots/01_equity_log.png`
- Drawdowns: `post_plots/02_drawdown.png`
- Rolling CAGR: `post_plots/03_rolling_cagr.png`
- CAGR vs Max DD: `post_plots/04_cagr_mdd_scatter.png`

## Main takeaway

The satellite version slightly increases CAGR versus B4 + 5% BTC, but it does **not** improve risk-adjusted return:

```text
B4 + 5% BTC:                  23.18% CAGR / -27.26% MDD / 1.472 Sharpe
B4 + BTC + SCV + Momentum:    24.40% CAGR / -29.90% MDD / 1.412 Sharpe
```

So this is not a clean “better portfolio”. It is more like: if I want to push for higher CAGR, I can add SCV/momentum, but I pay with worse drawdown and lower Sharpe.

The most aggressive funding version was to take the whole satellite out of ZROZ. That produced the highest CAGR, but I dislike it structurally because it almost removes the long-duration convexity sleeve:

```text
ZROZ-only funding: 25.49% CAGR / -33.57% MDD / 1.351 Sharpe
```

My preferred funding version keeps RSST and GDE intact and funds mostly from NTSX + ZROZ:

```text
15% NTSX / 25% GDE / 25% RSST / 10% ZROZ / 10% SCV / 10% Momentum / 5% BTC
```

## No-BTC check

I also tested the factor satellite without BTC over a longer 2000+ window to see whether SCV/momentum improves the B4 core by itself.

| Portfolio | CAGR | Max DD | Sharpe |
|---|---:|---:|---:|
| B4 base | 12.27% | -29.02% | 0.881 |
| B4 + SCV/Momentum, NTSX+ZROZ funded | 12.68% | -37.74% | 0.836 |
| B4 + SCV/Momentum, pro-rata funded | 11.98% | -34.79% | 0.844 |
| B4 + SCV/Momentum, ZROZ funded | 12.78% | -43.34% | 0.774 |
| SPY | 8.28% | -55.20% | 0.509 |

This makes me more cautious. Without BTC, the factor satellite adds a bit of CAGR in some versions, but worsens drawdown and Sharpe. So the portfolio’s strong 2010+ performance is heavily helped by BTC.

## Caveats

- BTC history starts after Bitcoin survived its earliest failure modes.
- VBRSIM/MTUMSIM are proxies, not AVUV/SPMO/FMTM live history.
- GDE and RSST also need proxy assumptions before their actual ETF launch dates.
- This is gross of taxes other than ETF expense drag.
- Monthly rebalancing is assumed; in taxable accounts I would probably rebalance mostly with contributions.
- This is not a recommendation. I am trying to stress-test the idea.

## Questions for the sub

1. Would you keep the factor satellite, or just use B4 + BTC?
2. If using the satellite, would you fund it from NTSX, ZROZ, GDE, or pro-rata?
3. Is SPMO a reasonable live momentum sleeve, or would you use something else?
4. Would you replace VBR/AVUV with a different small-cap value ETF?
5. Is 5% BTC too much, too little, or reasonable in this kind of portfolio?

My current leaning: B4 + 5% BTC is cleaner. The SCV/momentum satellite is interesting if I explicitly want a more aggressive CAGR tilt, but I do not think it is objectively superior.
