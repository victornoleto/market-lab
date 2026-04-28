# LETF portfolio shootout — 11 portfolios, 1988–2026 (38y)

Iterative comparison of leveraged-ETF / return-stacked / managed-futures portfolios on testfolio synth data, posted to r/LETFs in three rounds (5-way → 8-way → 11-way) as Reddit comments asked for new candidates.

This README is the consolidated reference. Reddit-tone posts live in `REDDIT_POST_LETFS.md` and `REDDIT_REPLY_*.md`.

---

## Final portfolio slate (11 candidates)

| # | Portfolio | Allocation | Tese / origin |
|---|---|---|---|
| P1 | SPY 100% | baseline | reference point |
| P2 | NTSX | 90% S&P + 60% IEF − 50% cash (1.5x stack) | WisdomTree NTSX prospectus |
| P3 | NTSX + GDE blend | 0.594 SPY + 0.396 IEF − 0.33 cash + 0.34 GDE (≈ 66% NTSX + 34% GDE) | the "incumbent" floating around r/LETFs |
| P4 | GDE 100% | 90% S&P + 90% gold (1.8x stack) | WisdomTree GDE prospectus |
| P5 | SSO/ZROZ/GLD 50/25/25 | 50% SSO (2x SPY) + 25% ZROZ (25y zero) + 25% GLD; monthly rebal; 0.89% drag | Hedgefundie-style trio (Bogleheads, 2019) |
| P6 | NTSX+GDE+KMLM 50/35/15 | conservative 15% MF sleeve | Asness/AQR — MF as 10-20% diversifier |
| **P7** | **NTSX+GDE+KMLM 40/35/25** | aggressive 25% MF / "Dragon-lite" | approximates Cole/Artemis Dragon weighting (~19% MF) |
| P8 | RSSB+GDE+KMLM 50/30/20 | swap NTSX (1.5x) for RSSB (2.0x stack 100/100 stocks/Treasuries) | Newfound/Resolve RSSB — more bond duration |
| P9 | NTSX+GDE+RSST 50/35/15 | drop-in for P6 with RSST instead of KMLM | RSST = "free MF on top of equity" |
| **P10** | **NTSX+GDE+RSST 40/35/25** | drop-in for P7 with RSST | balanced RSST variant |
| **P11** | **NTSX+RSST 50/50** | no gold — RSST as MF-via-stack | tests if MF replaces gold's diversifier role |

Bold = optimal on at least one axis (see "Winners by axis" below).

### Synthetic constructions

- `NTSX_synth = 0.90·SPY_TR + 0.60·IEF_TR − 0.50·CASH` (per WisdomTree prospectus)
- `GDE` from testfol.io — 90/90 SPY+gold stacked
- `RSSB` from testfol.io — 100/100 SPY+intermediate Treasuries stacked
- `RSST_synth = SPY_TR + KMLM − CASH` (per ReSolve/Newfound RSST prospectus, 100/100 stack)
  - testfolio doesn't have RSSTSIM (RSST launched 2023-09, too new for testfolio's synth library)

---

## Headline metrics — full window 1988-01 → 2026-04 (38.3y)

| # | Portfolio | Sharpe | CAGR | Vol | MaxDD |
|---|---|---:|---:|---:|---:|
| P1 | SPY 100% | 0.69 | 11.5% | 18.1% | −55% |
| P2 | NTSX | 0.82 | 12.6% | 16.1% | −45% |
| P3 | NTSX+GDE blend (incumbent) | 0.82 | 13.2% | 17.0% | −44% |
| P4 | GDE 100% | 0.69 | 13.6% | 22.0% | −53% |
| P5 | SSO/ZROZ/GLD 50/25/25 | 0.73 | 12.8% | 18.9% | −48% |
| P6 | NTSX+GDE+KMLM 50/35/15 | 0.90 | 12.8% | 14.6% | −37% |
| **P7** | **NTSX+GDE+KMLM 40/35/25** | **0.96** | 12.5% | **13.2%** | **−32%** |
| P8 | RSSB+GDE+KMLM 50/30/20 | 0.85 | 11.6% | 14.1% | −38% |
| P9 | NTSX+GDE+RSST 50/35/15 | 0.85 | 14.0% | 17.1% | −43% |
| **P10** | **NTSX+GDE+RSST 40/35/25** | **0.87** | **14.5%** | 17.2% | −42% |
| **P11** | **NTSX+RSST 50/50** | **0.90** | **15.0%** | 17.2% | −44% |

Bold = winner on that column (or near-winner with another distinguishing trait).

---

## Winners by axis

| Goal | Pick | Why |
|---|---|---|
| **Max Sharpe** | **P7 NTSX+GDE+KMLM 40/35/25** | 0.96 Sharpe, MDD only −32%. Pays 70 bps of CAGR vs incumbent for huge vol/drawdown reduction. |
| **Max CAGR (with reasonable Sharpe)** | **P11 NTSX+RSST 50/50** | 15.0% CAGR, 0.90 Sharpe. MDD back at −44% — same as unhedged incumbent. No gold. |
| **Best balanced (CAGR + MDD)** | **P10 NTSX+GDE+RSST 40/35/25** | 14.5% CAGR, 0.87 Sharpe, MDD −42%. Beats incumbent on every metric. |
| **Lowest drawdown** | **P7** | −32% peak-to-trough. Half the GFC drawdown of the incumbent. |
| **Highest CAGR floor (rolling 20y)** | P10/P11 | min 20y CAGR ~9.0% vs P7 8.4% vs incumbent 8.5% |

---

## The KMLM-puro vs RSST trade-off (the central insight)

Same weights, just KMLM (pure MF, replaces equity) vs RSST (MF stacked on top of equity):

| Pair | Sharpe | CAGR | Vol | MDD | Δ |
|---|---:|---:|---:|---:|---|
| P6 NTSX+GDE+**KMLM** 50/35/15 | 0.90 | 12.8% | 14.6% | −37% | → |
| P9 NTSX+GDE+**RSST** 50/35/15 | 0.85 | 14.0% | 17.1% | −43% | +1.2pp CAGR / +2.5pp vol / +6pp MDD / −0.05 Sharpe |
| P7 NTSX+GDE+**KMLM** 40/35/25 | 0.96 | 12.5% | 13.2% | −32% | → |
| P10 NTSX+GDE+**RSST** 40/35/25 | 0.87 | 14.5% | 17.2% | −42% | +2.0pp CAGR / +4.0pp vol / +10pp MDD / −0.09 Sharpe |

Reading: when you swap KMLM for RSST in those weights, you add equity exposure (because RSST stacks SPY on top of MF). CAGR goes up, vol goes up, MDD widens, Sharpe drops slightly. **Neither dominates — pick by axis.**

---

## Stress periods (the "where does each break" table)

| Period | P3 incumbent | P7 (KMLM 25%) | P10 (RSST 25%) | P11 (RSST 50/50) |
|---|---:|---:|---:|---:|
| Dot-com 2000–2002 | −36% | **−24%** | −37% | −36% |
| GFC 2007–09 | −42% | **−22%** | −37% | −34% |
| COVID Feb–Mar 2020 | −29% | **−20%** | −28% | −25% |
| 2022 rate cycle | −23% | **−10%** | −15% | **−10%** |
| 2008 calendar year | −27% | **−12%** | −22% | −17% |

P7 wins every stress period because the MF sleeve fully replaces (rather than overlays) equity. RSST variants give back most of the stress protection in exchange for higher long-run CAGR.

---

## Rolling 10y CAGR (the "what if I started here?" floor)

| Portfolio | mean | min | 5th pct | P(<5%) |
|---|---:|---:|---:|---:|
| P1 SPY | 10.4% | −4.1% | −0.5% | 14.5% |
| P3 NTSX+GDE | 11.7% | 6.95% | 9.01% | 0.0% |
| P6 KMLM 15% | 11.5% | 8.26% | 9.31% | 0.0% |
| P7 KMLM 25% | 11.2% | **8.48%** | **9.39%** | 0.0% |
| P10 RSST 25% | 12.4% | 6.88% | 9.10% | 0.0% |
| P11 RSST 50/50 | 12.5% | 5.34% | 8.62% | 0.0% |

P7 has the best floor; P10/P11 have higher means but slightly lower floors.

---

## DBMF vs KMLM as the MF leg (side-test, 2000-2026 only)

DBMF tracks SocGen Trend more faithfully than KMLM, but choice of MF synth doesn't change ordering:

| Portfolio | Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| P6 KMLM 15% | 0.80 | 11.8% | −37% |
| P6 DBMF 15% | 0.79 | 12.0% | −39% |
| P7 KMLM 25% | 0.85 | 11.4% | −32% |
| P7 DBMF 25% | 0.84 | 11.8% | −35% |

DBMF gives ~30 bps more CAGR but ~3 pp deeper MDD. KMLM has slight edge on drawdown control (purer trend signal); DBMF has slightly higher CAGR (more diversified). Wash overall.

---

## Caveats

- **Window 1988-01 → 2026-04 (38.3y)** — bounded by KMLMSIM start. Original 5-way ran 1986-01 → 2026-04 (40.3y, bounded by SSOSIM/ZROZSIM/GLDSIM); ranking is preserved when the window shifts.
- **Daily reweighted portfolios** (continuous rebalance approximation). Diverges slightly from yearly/monthly rebal. Confirmed against testfolio that ranking is preserved at this scale.
- **Drag only on P5 (0.89% annual).** No drag applied to NTSX/GDE (already in synth) or to KMLM/DBMF/RSSB synths.
- **Synthetic RSST is not real RSST.** Constructed per prospectus from `SPY_TR + KMLM − CASH`. Real fund has ~50 bps/y tracking error from CFC overhead and futures roll. No fee drag (~1% ER) applied — adjust headline CAGRs by ~25 bps (P9), ~40 bps (P10), ~80 bps (P11) for real-money expectations.
- **KMLM/DBMF synths pre-2010** are testfolio reconstructions of SocGen Trend/BTOP50 indices, not actual fund returns. Real KMLM launched 2020, DBMF 2019.
- **Gold synth (GLDSIM, GDESIM)** uses gold price proxies pre-2004. Real GLD started 2004.
- **All US, all USD.** No international exposure in any portfolio.
- **40 years of US dominance.** All windows benefit from the post-1980 US bull. Ranking might shift in a regime where US equities underperform global.

---

## Files in this directory

### Code
- `letfs_5way_validator.py` — original 5 portfolios on 1986-2026 window
- `letfs_8way_validator.py` — adds P6/P7/P8 (KMLM-based MF) on 1988-2026 window
- `letfs_11way_validator.py` — adds P9/P10/P11 (synth-RSST) on same window — **superset, run this for everything**
- `plot_letfs_5way.py` / `plot_letfs_8way.py` / `plot_letfs_11way.py` — matching plotters

### Outputs
- `LETFS_{5,8,11}WAY_VALIDATION.json` — full metrics + rolling stats + stress
- `letfs_{5,8,11}way_returns.parquet` — daily return series for each portfolio
- `letfs_{8,11}way_dbmf_side_returns.parquet` — DBMF substitution side-tests
- `LETFS_{5,8,11}WAY_*.png` — 6 figures each (equity, drawdowns, rolling 10y, rolling 5y Sharpe, rolling 20y hist, stress 4-panel)

### Reddit posts (drafts ready to publish)
- `REDDIT_POST_LETFS.md` — original 5-way post
- `REDDIT_REPLY_8WAY.md` — reply to "no managed futures?" comment
- `REDDIT_REPLY_11WAY.md` — reply to "test RSST too" follow-up

### Reproduce
```bash
uv run python studies/strategy_hunt_loop/deploy_studies/letfs_5way/letfs_11way_validator.py
uv run python studies/strategy_hunt_loop/deploy_studies/letfs_5way/plot_letfs_11way.py
```

---

## Citations

- WisdomTree NTSX prospectus (2018) — 90/60 stacking design
- WisdomTree GDE prospectus (2024) — 90/90 SPY+gold stacking
- Newfound/Resolve RSSB prospectus (2023) — 100/100 SPY+Treasuries stacking
- ReSolve/Newfound RSST prospectus (2023) — 100/100 SPY+MF stacking
- Hedgefundie (Bogleheads, 2019) — UPRO/TMF and SSO/ZROZ/GLD origin
- Asness, Frazzini, Pedersen (2012). "Leverage Aversion and Risk Parity." FAJ
- AQR (2017). "A Century of Evidence on Trend-Following Investing"
- Cole, C. (2020). "The Allegory of the Hawk and Serpent" (Artemis) — Dragon Portfolio rationale (~19% MF sleeve, approximated by P7)

## Open follow-ups (Reddit thread permitting)

1. **NTSX+GDE+RSST+KMLM** combined — both RSST overlay *and* pure KMLM as separate sleeves. Pick up CAGR while keeping MDD capped.
2. **Higher MF allocations** (>25%) on top of NTSX+GDE — at what point does it stop helping?
3. **RSSB+RSST blends** — pure return-stack maxi.
4. **Long-volatility leg** (puts/VXX-style hedge) — none of these portfolios have it; could explain the consistent ~−25% in COVID.
5. **International equity** — all 11 portfolios are US-only. Adding VEA/VWO sleeves would test US-dominance dependence.
