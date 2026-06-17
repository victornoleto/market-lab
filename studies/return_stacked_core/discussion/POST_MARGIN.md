# Return-stacked core — the trend↔gold dial (RSST vs GDE, bonds fixed), why I skip NTSX, and what IBKR margin really does when your funds are already ~1.7x leveraged

**This is not financial advice.** I'm sharing a research process, not a recommendation, and definitely not telling anyone to use margin. Benchmark everywhere is **100% SPY**.

This came out of a DM: *"have you considered trading your permanent portfolio on margin? IBKR rates are reasonable."* Fair question, so I actually ran it. Three parts: (1) the **managed-futures (RSST) ↔ gold (GDE) dial** with long Treasuries (ZROZ) held fixed at 25%, (2) why I don't add **NTSX** as a 4th sleeve, and (3) what external margin does to a book that is **already internally leveraged**.

## Read this before the tables (methodology & limits)

- **Everything before each fund's real inception is a simulated proxy.** GDE launched 2022, RSST 2023, NTSX 2018, ZROZ 2009. Long histories are built from index sims (testfol.io-style) + composition formulas. Proxy ≠ live ETF: real funds add fees, tracking error, internal rebalance timing.
- Proxy formulas (daily): `GDE ≈ 0.9·SPY + 0.9·GLD − 0.8·CASH`, `RSST ≈ SPY + 0.7·DBMF + 0.3·KMLM − (CASH + 2%/yr)`, `NTSX ≈ 0.9·SPY + 0.6·IEF − 0.5·CASH`.
- **Financing is modeled per overlay, not one-size-fits-all.** Gold and Treasury futures roll at ≈ the risk-free rate (for Treasuries the excess cost is ~zero by design), so GDE/NTSX just pay T-bills on the borrowed notional. The *managed-futures* overlay in RSST is an active strategy, so it carries an extra **~2%/yr** (matches the ~1.8–2% drag measured on standalone CTA wrappers). On top of that, GDE and NTSX are taken **net of expense ratio + tracking** (~0.45%/yr and ~0.20%/yr, from checking each sim against its live fund); RSST's cost is already inside that 2% leg.
- **The managed-futures sleeve is the most proxy-sensitive piece** — treat crisis numbers as directionally honest, not precise. The 2000–2026 window is also **the gold decade**, which flatters the gold-heavy end of the dial.
- All numbers: **2000–2026, monthly rebalance, simulated, net of fund expense ratios but gross of taxes and your own trading costs.** $1 → terminal in the last column.
- The margin section borrows at **T-bills + 2%/yr** — a touch above IBKR's ~1.5% retail spread, so if anything conservative on the *rate*. The real understatement isn't the rate: the backtest models **no margin calls and no forced liquidation** — it assumes you hold through the entire drawdown. That assumption is the whole problem (section 4).

## TL;DR

- **The dial:** hold ZROZ at 25%, slide the other 75% from gold (GDE) to managed futures (RSST). It's a smooth CAGR↔drawdown trade — **gold-heavy 13.1% CAGR / −33% MDD / Sharpe 0.84 / $25**, **MF-heavy 11.8% / −29% / 0.82 / $19**. **Calmar is ~flat (0.39–0.41) across the 3-fund dial**, so risk-adjusted-by-drawdown the split barely matters; it just decides where you sit on return-vs-drawdown.
- **NTSX is dominated:** adding it as a 4th equal sleeve (25/25/25/25) gives the *worst* CAGR ($16.5) for basically the same drawdown as the MF-heavy 3-fund mix. Tilt toward MF instead of adding a 4th fund.
- **"Margin rates are reasonable" misses the point.** These funds are *already* ~1.65–1.70x gross per dollar. Put **1.5x account margin on top and you're at ~2.5x real exposure**, not 1.5x.
- Sharpe **falls monotonically** with leverage for every mix, and by 1.5x the *historical* drawdown already breaches a tight-maintenance margin-call line; by 1.75x it breaches even standard Reg-T. You buy CAGR with disproportionate drawdown and add ruin risk the backtest can't see.

## 1) What these funds are (look-through)

| Ticker | What $1 buys | Gross |
|---|---|---|
| GDE | $0.90 US large cap + $0.90 gold | 1.8x |
| RSST | $1.00 US large cap + $1.00 managed futures | 2.0x |
| NTSX | $0.90 US large cap + $0.60 7–10y Treasuries | 1.5x |
| ZROZ | 25y+ zero-coupon Treasuries (duration ~27y, unlevered) | 1.0x |

Every mix below runs **~1.65–1.70x gross** with the leverage embedded inside the funds — no margin account, no daily-reset decay on the stack. The dial just changes *what fills it*: more GDE = more gold, more RSST = more managed futures. ZROZ (long-duration Treasuries) stays fixed at 25% throughout.

## 2) The trend↔gold dial (unlevered)

ZROZ fixed at 25%; the other 75% slides from gold (GDE) to managed futures (RSST):

![Growth of $1, the dial vs SPY, 2000–2026, log scale](figures/20_dial_equity_log.png)
*All four mixes compound above SPY (black) with far shallower valleys; the gold-heavy end compounds the highest. Growth of $1, log scale, simulated.*

| Portfolio | gross | CAGR | MDD | Sharpe | Sortino | Calmar | $1 → |
|---|---|---|---|---|---|---|---|
| **RSST25 / GDE50** (gold-heavy) | 1.65x | **13.1%** | −33.1% | **0.844** | **1.16** | 0.394 | **$25.4** |
| RSST37.5 / GDE37.5 (balanced) | 1.68x | 12.5% | −31.2% | 0.839 | 1.16 | 0.400 | $22.2 |
| **RSST50 / GDE25** (MF-heavy) | 1.70x | 11.8% | **−29.3%** | 0.819 | 1.13 | **0.405** | $19.2 |
| RSST25 / NTSX25 / GDE25 / ZROZ25 (+NTSX) | 1.58x | 11.2% | −29.4% | 0.816 | 1.13 | 0.382 | $16.5 |
| 100% SPY | 1.0x | 8.5% | −55.1% | 0.52 | 0.66 | 0.155 | $8.7 |

What the dial says:

- **Gold (GDE) is the return knob.** More of it → higher CAGR, Sharpe and Sortino, but a deeper drawdown. **Managed futures (RSST) is the drawdown knob** — more of it → shallower MDD and a slightly higher Calmar, at the cost of CAGR. The move is smooth and monotonic; there's no magic interior optimum.
- **Calmar barely moves (0.394 → 0.405).** Adjusted for the drawdown you take, every point on this dial is about the same trade. So the RSST↔GDE split isn't "which is better" — it's *how much crisis insurance (trend) you want to pay for in CAGR*. Over the gold decade, gold won on raw return; that may not repeat.
- **The +NTSX 4-fund mix is dominated.** It posts the lowest CAGR and terminal ($16.5) while its drawdown (−29.4%) is no better than the MF-heavy 3-fund mix (−29.3%), which compounds faster (11.8% vs 11.2%) with a higher Sharpe. A separate weight-selection robustness check (walk-forward + PBO on the full 4-asset grid) also flagged NTSX-inclusive mixes as overfit — they won only 3 of 9 out-of-sample windows. NTSX's 90/60 stock+Treasury exposure just overlaps what the stack + ZROZ already do. Tilt toward MF, don't add a 4th fund.

![The dial as CAGR vs max drawdown, unlevered](figures/22_dial_cagr_vs_mdd.png)
*The dial is a near-straight trade-off: sliding toward gold buys CAGR and Sharpe at the cost of a deeper drawdown. The +NTSX mix sits **below** the line — same drawdown as MF-heavy, less return. SPY is the lonely dot bottom-right.*

![Underwater chart: each mix vs SPY, drawdown from running peak](figures/21_dial_underwater.png)
*Each panel: one mix vs SPY (black/shaded). SPY spends years 40–55% underwater in 2002/2008; every point on the dial bottoms out around −29% to −33%. This is what you're buying with the diversifiers — and what margin gives back (section 4).*

## 3) Margin = leverage-on-leverage (the part people underestimate)

Because the funds are already ~1.67x, account margin **multiplies** the embedded leverage. The "modest" 1.5x is really ~2.5x gross exposure on *your* equity:

| Account margin L | gold-heavy gross | balanced gross | MF-heavy gross |
|---|---|---|---|
| 1.00x | 1.65x | 1.68x | 1.70x |
| 1.25x | 2.06x | 2.09x | 2.13x |
| 1.50x | **2.48x** | **2.51x** | **2.55x** |
| 2.00x | 3.30x | 3.35x | 3.40x |

The whole dial just shifts deeper as you lever it (monthly-reset leverage, 2%/yr financing):

| Account margin | gold-heavy CAGR / MDD | balanced CAGR / MDD | MF-heavy CAGR / MDD |
|---|---|---|---|
| 1.00x | 13.1% / −33% | 12.5% / −31% | 11.8% / −29% |
| 1.25x | 15.1% / −40% | 14.4% / −38% | 13.6% / −36% |
| 1.50x | 16.9% / −47% | 16.1% / −44% | 15.2% / −42% |
| 1.75x | 18.7% / −53% | 17.8% / −50% | 16.8% / −47% |
| 2.00x | 20.3% / −58% | 19.3% / −55% | 18.2% / −53% |

**Sharpe falls at every notch for every mix** (gold-heavy 0.84 → 0.73, MF-heavy 0.82 → 0.70 from 1.0x to 2.0x). The terminal-wealth gains are seductive precisely because they ignore the next table.

## 4) The margin call is the real risk, and the backtest hides it

Approximate portfolio drop that triggers a call at maintenance margin `m`: `drop = (1 − m·L)/(L·(1 − m))`. Against the dial's *historical* drawdown at each leverage (range across gold-heavy → MF-heavy):

| Account margin | Call @25% maint | @30% | @50% | dial historical MDD | verdict |
|---|---|---|---|---|---|
| 1.25x | −73% | −71% | −60% | −40% … −36% | safe |
| 1.50x | −56% | −52% | **−33%** | −47% … −42% | **breaches 50%-maint gate** |
| 1.75x | **−43%** | **−39%** | −14% | −53% … −47% | **breaches all three gates** |
| 2.00x | −33% | −29% | ~0% | −58% … −53% | **breaches everything by a wide margin** |

![When does margin call you? Book drawdown vs maintenance gates](figures/23_margin_call_danger.png)
*The trap in one chart: as you add account margin, the book's historical drawdown (red, rising) deepens while the margin-call threshold (dashed, falling) shrinks. They cross around **1.45–1.5x** under 50% maintenance and **~1.75x** under standard Reg-T — past those points, the 2008/2022 paths in this sim would have been force-liquidated.*

The tables in section 3 assume you ride the full −47% (gold-heavy at 1.5x) or −58% (at 2.0x) and recover. In a real margin account you don't — the broker **liquidates you at the bottom** when equity breaches maintenance, and you never get the rebound. At **1.5x** under tight (50%) maintenance, and at **1.75x+** under *standard Reg-T*, the 2008/2022-style paths in this very sim would have triggered forced selling. GDE/RSST may not even get plain-vanilla ETF margin treatment (concentration + fund type can push maintenance higher). That risk is **invisible** in every CAGR number above.

## Practical read

- **Unlevered (1.0x) is the clean story.** ~1.67x embedded, ~12% CAGR (net of fund costs), ~−30% MDD, no liquidation risk, no financing drag, no 3am margin-call timezone problem. Pick your point on the trend↔gold dial and stop.
- The RSST↔GDE choice is a *risk-character* decision (gold = more CAGR + deeper DD; trend = shallower DD), not a "which wins" decision — Calmar says they're about equal.
- If you insist on leverage, the only band I'd even *research* is **1.10–1.25x**, and only with *real* IBKR maintenance + financing + explicit forced-liquidation logic — not the hold-through-anything backtest here. 1.5x+ is diagnostic stress, not a plan. The cheap leverage is *already inside the funds*; stacking a margin loan on top mostly buys tail risk.

## What I am NOT claiming

- Not claiming these CAGRs forward — the gold + duration tailwinds of 2000–2026 may not repeat, and the MF sleeve is fee-heavy and proxy-flattered.
- Not claiming any single point on the dial is *optimal* — the whole range is one Calmar-flat trade-off; I'm only claiming the 4th NTSX sleeve didn't earn its place.
- Not claiming the live ETFs track these sims (fees 0.8–1%, tracking error, closure risk — several of these funds are small and young).
- Not endorsing margin on this book. The honest finding is that it's unattractive once financing and forced-liquidation risk are taken seriously.

## Questions for the sub

1. Where do you sit on the trend↔gold dial, and why — do you want the CAGR (gold) or the drawdown control (managed futures)?
2. Anyone running RSST/GDE/ZROZ on **Portfolio Margin** at IBKR — what maintenance % do these actually get in practice?
3. Has anyone been margin-called on a capital-efficient stack in 2022? How fast did it move?
4. NTSX holders — do you see a role for it *alongside* GDE/RSST/ZROZ, or does it just dilute?

*Reproducible offline pipeline (testfol.io-style sims). Sweep script + matched CSV available; happy to share methodology in comments.*
