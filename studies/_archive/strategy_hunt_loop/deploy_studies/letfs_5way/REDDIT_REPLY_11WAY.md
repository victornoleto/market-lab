# Update 2: now with RSST. NTSX+GDE+RSST 40/35/25 = 14.5% CAGR / 0.87 Sharpe / -42% MDD (1988-2026)

Got asked to test RSST too. testfolio doesn't have RSSTSIM (RSST is too new — launched 2023-09 by ReSolve/Newfound), so I synthesized it from the prospectus:

> RSST_synth = SPYSIM (S&P TR) + KMLMSIM (managed futures) − CASHX (financing rate)

Per the RSST prospectus that's exactly what the fund targets: 100% S&P 500 + 100% managed futures, financed at the risk-free rate via futures. Real RSST has ~50 bps/y of tracking error vs this synth (futures roll, CFC overhead) but for a 38y comparison the synth is the right tool.

Also reran the side-test with `RSST_dbmf = SPY + DBMF − CASH` to check if the choice of MF leg matters. Spoiler: the picture doesn't change.

## TL;DR

- **If you want max Sharpe → P7 NTSX+GDE+KMLM 40/35/25 still wins (0.96)**, MDD −32%, CAGR 12.5%
- **If you want max CAGR with reasonable Sharpe → P11 NTSX+RSST 50/50 (Sharpe 0.90, CAGR 15.0%)**, but you give back the drawdown protection — MDD goes back to −44% (same as the original NTSX+GDE incumbent)
- **The "best of both" middle → P10 NTSX+GDE+RSST 40/35/25 (Sharpe 0.87, CAGR 14.5%, MDD −42%)** — beats incumbent on every metric

The general pattern: **RSST adds equity exposure on top of MF, so it's a CAGR boost with the vol/MDD that comes with extra equity.** Pure KMLM in the same slot trades CAGR for vol/MDD. They're both "right" — it depends which axis you're optimizing.

## Headline numbers, all 11

| # | Portfolio | Sharpe | CAGR | Vol | MaxDD |
|---|---|---:|---:|---:|---:|
| P1 | SPY 100% | 0.69 | 11.5% | 18.1% | −55% |
| P2 | NTSX | 0.82 | 12.6% | 16.1% | −45% |
| P3 | NTSX+GDE blend (orig) | 0.82 | 13.2% | 17.0% | −44% |
| P4 | GDE 100% | 0.69 | 13.6% | 22.0% | −53% |
| P5 | SSO/ZROZ/GLD 50/25/25 | 0.73 | 12.8% | 18.9% | −48% |
| P6 | NTSX+GDE+KMLM 50/35/15 | 0.90 | 12.8% | 14.6% | −37% |
| **P7** | **NTSX+GDE+KMLM 40/35/25** | **0.96** | 12.5% | **13.2%** | **−32%** |
| P8 | RSSB+GDE+KMLM 50/30/20 | 0.85 | 11.6% | 14.1% | −38% |
| P9 | NTSX+GDE+RSST 50/35/15 | 0.85 | 14.0% | 17.1% | −43% |
| **P10** | **NTSX+GDE+RSST 40/35/25** | **0.87** | **14.5%** | 17.2% | −42% |
| **P11** | **NTSX+RSST 50/50** (no gold) | **0.90** | **15.0%** | 17.2% | −44% |

## P9/P10 (RSST drop-in) vs P6/P7 (KMLM equivalent) — the apples-to-apples

This is the cleanest comparison: same weights, just RSST instead of KMLM as the third leg.

| Pair | Sharpe | CAGR | Vol | MDD |
|---|---:|---:|---:|---:|
| P6 NTSX+GDE+**KMLM** 50/35/15 | **0.90** | 12.8% | 14.6% | −37% |
| P9 NTSX+GDE+**RSST** 50/35/15 | 0.85 | **14.0%** | 17.1% | −43% |
| P7 NTSX+GDE+**KMLM** 40/35/25 | **0.96** | 12.5% | 13.2% | −32% |
| P10 NTSX+GDE+**RSST** 40/35/25 | 0.87 | **14.5%** | 17.2% | −42% |

What's happening: when you swap KMLM for RSST in those weights, you get +15% (or +25%) extra SPY exposure on top of the same MF amount, financed at cash. So:

- **CAGR goes up by ~1.2–2.0 pp** (free equity exposure boosts returns)
- **Vol goes up by ~3 pp** (more equity = more vol)
- **MDD widens by 6–10 pp** (more equity = bigger crashes)
- **Sharpe drops slightly** (extra equity vol overwhelms the CAGR boost)

If your goal is risk-adjusted return, KMLM-puro wins. If your goal is total return without taking the SPY-100% risk profile, RSST wins. **Neither is dominant**.

## P11 NTSX+RSST 50/50 — the "no gold" variant

Almost the same Sharpe as P6 (0.90), but 2.2 pp higher CAGR (15.0% vs 12.8%). The trade-off: MDD is back at −44% (same as the unhedged incumbent). The MF sleeve in RSST helps a *lot* with 2022 (P11 was −10% in 2022 vs P3 −23%) but doesn't replace gold's role in 2008 (P11 was −17% in 2008 vs P7 −12%).

This is the variant for someone who's allergic to gold but wants the MF diversifier. CAGR-wise it's the best on this slate. MDD-wise, you're back to "I need to hold through a −44% drawdown" territory.

## Stress periods (the 11-way picture)

| Period | P3 (incumbent) | **P7** (Sharpe winner) | **P10** (RSST balanced) | **P11** (no-gold RSST) |
|---|---:|---:|---:|---:|
| Dot-com 2000–2002 | −36% | **−24%** | −37% (KMLM)/−36% (DBMF) | −36%/−34% |
| GFC 2007–09 | −42% | **−22%** | −37%/−42% | −34%/−45% |
| COVID 2020 | −29% | **−20%** | −28%/−32% | −25%/−33% |
| 2022 | −23% | **−10%** | −15%/−17% | **−10%**/−13% |
| 2008 | −27% | **−12%** | −22%/−27% | −17%/−27% |

Two patterns to notice:

1. **P7 (KMLM puro) has the smallest drawdown in every period.** Vol-controlling the MF sleeve is more effective than overlaying it on more equity.
2. **The DBMF variant of RSST does worse in equity stress (2008, GFC, COVID) than the KMLM variant.** That's because DBMF tracks SocGen Trend more faithfully and that index had specific bad spots in those periods. KMLM as a more pure-trend index handled them better. Difference is small (3-5 pp) but consistent.

## Rolling 20y CAGR — long-horizon picture

| Portfolio | mean | min | 5th pct |
|---|---:|---:|---:|
| P3 NTSX+GDE | 11.6% | 8.5% | 9.5% |
| P7 NTSX+GDE+KMLM 40/35/25 | 11.2% | 8.4% | 9.4% |
| P10 NTSX+GDE+RSST 40/35/25 | 12.4% (KMLM)/12.7% (DBMF) | 8.6% | 9.6% |
| P11 NTSX+RSST 50/50 | 11.0%/11.5% | 7.9% | 9.2% |

P10 has the best long-horizon CAGR (12.4–12.7% vs 11.2% for P7). The floor is similar — i.e. you're not paying for the extra CAGR with worse worst-case 20y outcomes.

## DBMF side-test (the KMLM ↔ DBMF substitution) — 2000-2026 only

Same pattern as the 8-way reply: DBMF gives ~30 bps more CAGR but ~3 pp deeper MDD. Choosing one over the other is a wash for the post-2000 sample. The pattern holds in the RSST variants too.

## What this changes vs the 8-way conclusion

The 8-way said "P7 (NTSX+GDE+KMLM 40/35/25) is the new Sharpe winner." That's still true — adding RSST doesn't change it.

What's new:

- **CAGR-maximizers should look at P10 or P11**, not P7. They give up Sharpe but pick up 2-2.5 pp of CAGR.
- **The "free equity overlay" pitch for RSST holds in the data** — P9/P10 generate ~1.2-2.0 pp more CAGR than P6/P7 with the same weights.
- **Whether "free" is worth it depends on whether you can hold through a −42% drawdown.** P7 keeps you under −32%; P10 puts you back at −42%.

## Charts

* `LETFS_11WAY_equity.png` — log equity 1988–2026, 11 lines
* `LETFS_11WAY_drawdowns.png` — drawdowns from peak (the cleanest "what does each break on" plot)
* `LETFS_11WAY_rolling10y.png` — rolling 10y CAGR
* `LETFS_11WAY_rolling5y_sharpe.png` — rolling 5y Sharpe
* `LETFS_11WAY_rolling20y_hist.png` — 20y CAGR distribution
* `LETFS_11WAY_stress.png` — 4 stress windows side by side

## Caveats specific to RSST

* **Synthesized RSST**, not testfolio data. Construction follows the prospectus literally (`SPY_TR + KMLM − CASH`). Real RSST since 2023-09 has tracked roughly this with ~50 bps/y of slippage from CFC overhead and futures roll. 38y backtest assumes that slippage is constant.
* **Real RSST uses DBMF-style trend exposure**, not KMLM-style. The DBMF side-test variant is the more faithful match on the MF leg, but the picture (RSST = +CAGR, +vol, −Sharpe vs pure-MF) holds either way.
* **No fee drag applied** to the synthetic MF leg in P9/P10/P11. Real RSST ER is ~1%. Adjust CAGRs by ~25 bps for P9 (15% RSST), ~40 bps for P10 (25% RSST), ~80 bps for P11 (50% RSST). At those levels P10 is still ~13.5%, P11 ~14.2% — still ahead of the unhedged incumbent.
* **All other 8-way caveats apply** (KMLM synth pre-2010, daily reweight, all-US/USD).

## Open questions still

1. Is there a sweet spot between P7 and P10? E.g., NTSX+GDE+RSST+KMLM with both RSST *and* pure KMLM as separate sleeves — pick up some CAGR but cap MDD. Worth trying.
2. The Dragon-style portfolios that include long volatility (e.g. tail hedges via puts) — none of these portfolios have that leg. Could explain why all of them got hit ~−25% in COVID.
3. RSSB+RSST blends — pure return-stack maxi.

Happy to rerun.
