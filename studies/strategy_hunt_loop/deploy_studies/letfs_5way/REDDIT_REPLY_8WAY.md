# Follow-up: adding managed futures to NTSX+GDE — does the MF sleeve actually beat the blend? (1988–2026, 38y)

A bunch of you (correctly) pointed out the original 5-way was missing managed futures. Reran the same shootout with a 15-25% MF sleeve added on top of NTSX+GDE, plus a "throw RSSB at it instead of NTSX" variant. Window is bounded by KMLM synth (1988-01) — 38.3 years end-to-end. Same testfolio TR data, same daily-reweight, same 0.89% drag on the SSO/ZROZ/GLD trio.

## TL;DR

**A 25% KMLM sleeve on NTSX+GDE bumps Sharpe from 0.82 → 0.96 and cuts MDD from −44% to −32%, at the cost of ~70 bps of CAGR.** That's the cleanest "should I add managed futures?" answer I can give from this slate. RSSB-as-core (P8) is fine but doesn't dominate NTSX-as-core.

## Headline numbers, all 8 portfolios

| # | Portfolio | Sharpe | CAGR | Vol | MaxDD |
|---|---|---:|---:|---:|---:|
| P1 | SPY 100% | 0.69 | 11.5% | 18.1% | −55% |
| P2 | NTSX | 0.82 | 12.6% | 16.1% | −45% |
| P3 | NTSX+GDE blend (incumbent) | 0.82 | **13.2%** | 17.0% | −44% |
| P4 | GDE 100% | 0.69 | **13.6%** | 22.0% | −53% |
| P5 | SSO/ZROZ/GLD 50/25/25 | 0.73 | 12.8% | 18.9% | −48% |
| P6 | **NTSX+GDE+KMLM 50/35/15** | **0.90** | 12.8% | 14.6% | **−37%** |
| P7 | **NTSX+GDE+KMLM 40/35/25** | **0.96** | 12.5% | **13.2%** | **−32%** |
| P8 | RSSB+GDE+KMLM 50/30/20 | 0.85 | 11.6% | 14.1% | −38% |

(Note: window starts 1988-01 instead of 1986-01 because KMLM synth begins 1987-12. P3 numbers shift very slightly vs the original post but ranking is preserved.)

## What the MF sleeve actually does

The full-window CAGR doesn't move much (12.5–12.8% with MF vs 13.2% incumbent), but **vol drops from 17% to 13–15% and the worst drawdowns get cut nearly in half**. Stress periods are where this is most visible:

| Period | P3 incumbent | P6 (15% MF) | P7 (25% MF) |
|---|---:|---:|---:|
| Dot-com 2000–2002 | −36% | −29% | **−24%** |
| GFC 2007–09 | −42% | −31% | **−22%** |
| COVID Feb–Mar 2020 | −29% | −24% | **−20%** |
| 2022 full year | −23% | −15% | **−10%** |
| 2008 calendar | −27% | −18% | **−12%** |

That 2022 row is the obvious one — KMLM was up ~30% that year, so the more MF you carried, the less you got hosed. But it's the GFC and 2008 rows that surprised me most: the 25% MF sleeve cuts the GFC peak-to-trough roughly in half. Trend was on the right side of late-2008 oil collapse + Treasury rally.

## Rolling 10y CAGR (the floor question)

| Portfolio | mean | min | 5th pct | P(<5%) |
|---|---:|---:|---:|---:|
| P3 NTSX+GDE | 11.7% | 6.95% | 9.01% | 0.0% |
| P6 +15% KMLM | 11.5% | 8.26% | 9.31% | 0.0% |
| **P7 +25% KMLM** | 11.2% | **8.48%** | **9.39%** | 0.0% |
| P8 RSSB+GDE+KMLM | 10.8% | 8.24% | 9.15% | 0.0% |

Same picture: less mean, better floor. P7's worst rolling 10y window is +8.5%, vs +6.95% for the unhedged incumbent.

## Rolling 20y

| Portfolio | mean | min | 5th pct |
|---|---:|---:|---:|
| P3 NTSX+GDE | 11.6% | 8.5% | 9.5% |
| P6 +15% KMLM | 11.4% | 8.7% | 9.6% |
| **P7 +25% KMLM** | 11.2% | 8.4% | 9.4% |
| P8 RSSB+GDE+KMLM | 10.8% | 8.1% | 9.2% |

Floors are basically tied at the long horizon — i.e. the MF sleeve doesn't cost you long-term safety, it just dampens volatility along the way.

## RSSB as core (P8) vs NTSX as core (P6/P7)

I expected P8 (RSSB instead of NTSX, so 100/100 stocks/bonds vs 90/60) to win on more diversification per dollar. It doesn't:

- P8 Sharpe 0.85 vs P6 0.90, P7 0.96
- P8 CAGR 11.6% vs P6 12.8%, P7 12.5%
- P8 MDD −38% vs P6 −37%, P7 −32%

The longer-duration bond exposure in RSSB hurt in 2022 specifically (RSSB down ~21% that year vs NTSX −25% — close, but RSSB doesn't have the gold cushion that the GDE leg adds elsewhere). Also RSSB's intermediate-Treasury sleeve duplicates some of NTSX's IEF sleeve, so swapping NTSX for RSSB doesn't add much new exposure once GDE is in the mix.

## DBMF vs KMLM as the MF leg (side-test, 2000-2026 only)

Some of you will ask "but DBMF tracks SocGen Trend more faithfully than KMLM" — fair. Reran P6/P7 with DBMF substituted for KMLM on the post-2000 window (DBMF synth only goes back to 2000):

| Portfolio | Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| P3 (no MF) | 0.73 | 12.1% | −44% |
| P6 KMLM 15% | 0.80 | 11.8% | −37% |
| P6 DBMF 15% | 0.79 | 12.0% | −39% |
| P7 KMLM 25% | 0.85 | 11.4% | −32% |
| P7 DBMF 25% | 0.84 | 11.8% | −35% |

DBMF gives ~30 bps more CAGR but ~3pp deeper MDD. They're close enough that the choice of MF synth doesn't change ordering. KMLM has a slight edge on drawdown control because it's a purer trend product (no carry/equity sleeves diluting the trend signal); DBMF has slightly higher CAGR because it's more diversified. Pick your poison.

## Charts (same 6 cuts as before)

* `LETFS_8WAY_equity.png` — log equity 1988–2026
* `LETFS_8WAY_drawdowns.png` — drawdowns from peak (this one is the most striking)
* `LETFS_8WAY_rolling10y.png` — rolling 10y CAGR
* `LETFS_8WAY_rolling5y_sharpe.png` — rolling 5y Sharpe (P7 sits at 1.0+ for most of the post-2000 sample)
* `LETFS_8WAY_rolling20y_hist.png` — 20y CAGR histogram
* `LETFS_8WAY_stress.png` — 4 stress windows side by side

## Caveats

* **KMLM synth pre-2010** is testfolio's reconstruction of SocGen Trend index returns — not a fund. Real KMLM launched 2020, real DBMF 2019. Both have ~6-12 months of meaningful tracking error vs the synth in real life.
* **No fee drag on the synthetic MF sleeves.** Real KMLM ER is ~0.92%, DBMF ~0.85%. Adding ~0.9% drag to the 25% MF sleeve in P7 = ~22 bps annual drag on the portfolio. Adjust the CAGRs above by roughly that much if you care.
* **Trend doesn't always win.** Trend had a multi-year drought 2011-2018 where MF dragged on returns. The CAGR cost (~70 bps vs the unhedged blend) is the price of admission for the Sharpe and MDD gains.
* **Daily reweight, not yearly rebalance.** Same caveat as the original — at this scale ranking is preserved but absolute numbers shift slightly.
* **All US, all USD.** Still no international.

## Open questions back to the sub

1. Anyone running NTSX+GDE+RSST instead of NTSX+GDE+KMLM/DBMF? (RSST = 100% S&P + 100% MF stacked.) On paper that's a free MF sleeve — should be even better than P7. testfolio doesn't have RSSTSIM in my cache; if anyone has it I'd love to plug it in.
2. Is there a case for splitting the MF sleeve between KMLM and DBMF (or KMLM + CTA) to diversify the trend-model risk? My side-test suggests KMLM and DBMF are pretty close so probably no, but curious if anyone's tested it.
3. Anyone sized MF higher than 25% on top of NTSX+GDE? At what point does it stop helping?

Happy to rerun specific allocations.
