# I backtested the return-stacked ETF lineup (GDE/RSST/NTSX/RSSX + ZROZ) through every major regime since 2000. Here's where the diversification actually comes from — and why the exact allocation matters less than you think

**This is not financial advice.** I'm sharing a research process, not a recommendation. Benchmark everywhere is **100% SPY**.

## Read this before the charts (methodology & limits)

- **Everything before each fund's real inception is a simulated proxy.** GDE launched 2022, RSST 2023, RSSX 2024. The long histories are built from index sims (testfol.io-style) and composition formulas, all disclosed below. Proxy ≠ live ETF: real funds add fees, tracking error and internal rebalance timing.
- Proxy formulas (daily returns): `GDE ≈ 0.9·SPY + 0.9·GLD − 0.8·CASH`, `RSST ≈ SPY + 0.7·DBMF + 0.3·KMLM − (CASH + 2%/yr)`, `NTSX ≈ 0.9·SPY + 0.6·IEF − 0.5·CASH`, `RSSX ≈ SPY + 0.8·GLD + 0.2·BTC − 0.8·CASH`, `TMF ≈ 3·(0.5·ZROZ + 0.5·IEF) − 2·CASH − 1.06%/yr`.
- **The managed-futures sleeve is the most proxy-sensitive piece.** With a different MF proxy, RSC's GFC drawdown moves several points (we measured −23% with this proxy vs −14% with an older one). Treat crisis numbers as directionally honest, not precise.
- **BTC pre-2017 carries massive survivorship/non-stationarity bias.** Any RSSX result is assumption-heavy, not evidence.
- The RSSY (futures yield) sleeve uses AQR's academic multi-asset carry series (monthly, scaled to 10% vol, minus 2%/yr drag) — a rough analog, evaluated at monthly frequency only. Attribution: AQR "Century of Factor Premia" dataset.
- Taxes, spreads, and rebalancing costs are ignored. Everything is gross, monthly-rebalanced, long-only at the fund level.
- The 1970+ chart uses an academic momentum factor as the MF stand-in pre-1988 **with a 50% haircut** (the raw splice is too flattering) and is labeled LOW FIDELITY.

## TL;DR

- A boring static mix — **35% GDE / 40% RSST / 25% ZROZ** — turned $1 into **$22.5 vs $8.7 for SPY** over 2000–2026 (CAGR 12.5% vs 8.5%) with a max drawdown of **−31% vs −55%** (simulated, gross).
- The win comes from **four return streams on one dollar** (~165% notional: stocks + gold + managed futures + long Treasuries), not from picking magic weights.
- In SPY's worst-decile months (avg −7.9%), the diversifiers averaged **gold +1.8%, managed futures +2.4%, ZROZ +3.8%** per month. That's the whole thesis in one number.
- 2022 was the stress test that mattered: stocks −24% **and** ZROZ −40%, while managed futures made +38%. The three-diversifier core lost −21%; HFEA lost −65%.
- I scanned **all 231 possible 5% allocations** of GDE/RSST/ZROZ: the top-Sharpe region is a **contiguous 60-node plateau**, and 35/40/25 sits inside it from every start date I tried. The "optimal" point wanders; the plateau doesn't. Arguing about 35/40/25 vs 40/35/25 is noise.
- Leverage source matters more than leverage amount: HFEA-style 3x LETFs (vol drag + one diversifier) vs stacked funds (carry-efficient + three diversifiers) is the real fork in the road.

## What these funds actually are

| Ticker | What $1 buys (look-through) | Live since |
|---|---|---|
| GDE | $0.90 US large cap + $0.90 gold | 2022 |
| RSST | $1.00 US large cap + $1.00 managed-futures strategy | 2023 |
| NTSX | $0.90 US large cap + $0.60 7-10y Treasuries | 2018 |
| RSSX | $1.00 US large cap + $0.80 gold + $0.20 bitcoin | 2024 |
| RSSY | $1.00 US large cap + $1.00 futures-yield (carry) strategy | 2023 |
| ZROZ | 25y+ zero-coupon Treasuries (duration ~27y, unlevered) | 2009 |

The 35/40/25 core holds ~75% stocks, ~32% gold, ~40% managed futures, ~25% long Treasuries per dollar — leverage embedded inside the funds, no margin account, no daily-reset decay on the stack.

## 1) The building blocks, alone (fig 1-2)

Stocks compound the most but with −55% drawdowns. Gold and managed futures go nowhere for years, then pay exactly when stocks burn. ZROZ is a rate bet with equity-sized volatility. None of them is a "good investment" alone — that's precisely why stacking them works.

The stacked products track SPY's growth while each carrying a different shock absorber. The core (red) compounds above SPY with visibly shallower valleys.

## 2) Regime behavior — who shows up when (fig 3-5)

| Episode | SPY | Gold | Mgd futures | ZROZ | CORE 35/40/25 | HFEA 55/45 |
|---|---|---|---|---|---|---|
| Dot-com bust (2000-02) | −47% | +12% | +44% | +50% | **−21%** | −57% |
| GFC (2007-09) | −55% | +25% | +34% | +50% | **−23%** | −68% |
| 2022 inflation shock | −24% | −9% | **+38%** | **−40%** | **−21%** | **−65%** |
| AI bull (2022-26) | +118% | +177% | +5% | −19% | +105% | +98% |

Three different crises, three different heroes: 2000-02 trend+duration, 2008 duration+gold+trend, 2022 **trend only** — bonds were the problem, not the hedge. A portfolio leaning on a single diversifier (HFEA on Treasuries) got destroyed exactly once a decade; a portfolio with three of them never lost more than ~23% (in this simulated history).

The honesty rows: in pure risk-on equity bulls the core lags — taper tantrum 2013: SPY +17.5%, core **−2.4%**. QE decade: HFEA +3,183% vs core +478%. If stocks-only-up is your base case forever, all of this is drag.

## 3) The decorrelation, quantified (fig 6-7)

Monthly correlations vs SPY (2000–2026): **gold +0.06, managed futures −0.22, ZROZ −0.15**. The pairs among the diversifiers are ≤ +0.19 — four genuinely different return streams.

Rolling correlations show the catch: none of these is a *constant* hedge. SPY-ZROZ flipped positive in 2022 (that's the HFEA killer); SPY-gold spends years mildly positive. The portfolio case rests on the *average* being near zero and the **conditional** behavior:

| In SPY's 32 worst months (avg −7.9%/mo) | Mean monthly return |
|---|---|
| Gold | **+1.8%** |
| Managed futures | **+2.4%** |
| ZROZ | **+3.8%** |
| BTC | −4.4% |
| Carry (RSSY sleeve) | −0.8% |

Note the last two rows: BTC and carry are *return* stacks, not *crisis* stacks. They diversify the good times, not the bad ones.

## 4) Is 35/40/25 special? No — and that's the point (fig 8-9)

I ran every 5%-step combination of GDE/RSST/ZROZ — 231 portfolios, monthly rebalanced, 2000–2026:

- Best Sharpe: 0.866 at **45/25/30**. The core's Sharpe: 0.847 (88th percentile).
- The region within 95% of max Sharpe is a **contiguous 60-node plateau** covering roughly GDE 30-60%, RSST 10-45%, ZROZ 20-40%.
- Re-running from 8 different start dates (2000→2014): the argmax wanders all over (45/25/30 → 50/20/30 → 60/30/10…), but **35/40/25 stays inside the plateau in 8 of 8 windows**.

So I will not tell you 35/40/25 is optimal — claiming the argmax of 231 backtests would be textbook overfitting. The defensible claim is the opposite: **within a wide region around equal-ish weights with 20-40% ZROZ, allocation precision barely matters.** Spend your decision budget on whether you want the strategy at all, not on the third decimal of the weights.

The frontier chart makes the trade visible: ZROZ weight slides you along CAGR-vs-drawdown; removing it entirely (top-right) buys +1.4pp CAGR for −15pp deeper drawdowns and a Sharpe drop.

## 5) Ablations — what each piece buys (fig 12)

2000–2026, monthly rebalance, all simulated:

| Variant | CAGR | MDD | Sharpe |
|---|---|---|---|
| **CORE 35/40/25** | **12.5%** | **−30.8%** | **0.85** |
| Equal-weight 33/33/33 | 12.1% | −26.3% | 0.86 |
| No ZROZ (47/53 GDE/RSST) | 13.9% | −45.5% | 0.74 |
| ZROZ → cash | 11.1% | −35.9% | 0.76 |
| NTSX swap (35 NTSX/40 RSST/25 ZROZ) | 9.8% | −28.1% | 0.74 |
| DIY with SSO (35 SSO/20 GLD/25 MF/20 ZROZ) | 10.4% | −33.0% | 0.81 |
| 100% SSO | 9.9% | −88.3% | 0.44 |
| 100% UPRO | 7.2% | −98.3% | 0.41 |
| HFEA 55/45 (monthly reb.) | 12.1% | −69.4% | 0.53 |
| HFEA 55/45 (quarterly reb.) | 15.3% | −69.1% | 0.62 |
| 100% SPY | 8.5% | −55.1% | 0.52 |

Takeaways:

- **ZROZ's job is the left tail, not returns.** Dropping it adds 1.4pp CAGR and 15pp of drawdown.
- **It's duration, not just "less stocks":** swapping ZROZ for cash loses both return *and* Sharpe.
- **Gold > more bonds in the equity sleeve:** NTSX-for-GDE swap costs 2.7pp CAGR (gold crushed 7-10y Treasuries over this window — fair to note this is partly a gold-decade artifact).
- **The DIY replica with SSO works but trails** (~2.1pp CAGR): 2x daily-reset leverage + external sleeves is less efficient than the embedded stack at ~1.7x gross.
- **Pure LETFs are vol-drag machines** at these horizons: 100% UPRO underperformed plain SPY with a −98% drawdown.

Extensions (separate windows, weaker evidence):

- **RSSX** (BTC window 2010-07+): swapping GDE→RSSX jumps CAGR 15.0%→26.2% with Sharpe 1.47 vs 1.04. That is **entirely BTC's monster decade** talking — and RSSX lost −41% in 2022 (worse than SPY). I'd treat it as a small optional satellite, not a core sleeve.
- **RSSY** (monthly, academic carry proxy, 2000–2026): swapping RSST→RSSY *reduced* Sharpe (0.88 vs 0.96) and deepened drawdown. Carry didn't defend in 2008/2022 the way trend did. A 50/50 split (A13) lands in between.

## 6) The 1970 extension — stagflation test (fig 11, LOW fidelity)

With the haircut MF proxy: 1970–2026, core-style mix compounds at **13.9% vs SPY 11.1%**, MDD **−40% vs −55%**, and HFEA hits **−90%** in the Volcker years (3x long bonds + 20% rates). In the 1973-74 stagflation bear: SPY −45%, **gold +139%**, trend +65%, ZROZ −30%. The 1970s are exactly the decade 60/40-style portfolios and bond-levered strategies cannot survive — and the decade gold/trend stacking is built for. Again: academic proxies, administered gold price before 1971, read as a sanity check, not a backtest.

## What I am NOT claiming

- Not claiming these CAGRs forward. The gold and duration tailwinds of this sample may not repeat; the MF sleeve is fee-heavy and proxy-flattered.
- Not claiming 35/40/25 is optimal — explicitly the opposite.
- Not claiming the live ETFs will track these sims (fund closures, tracking error, and 0.8-1.0% ERs are real risks; several of these funds are small).
- Not claiming this beats SPY in every regime — it reliably lags in melt-ups (2013, the QE decade vs anything levered).

## Questions for the sub

1. For those holding RSST/GDE live: how has tracking been vs your expectations?
2. Anyone replacing the ZROZ sleeve with GOVZ/EDV — meaningful difference in practice?
3. Is a 5-10% RSSX satellite defensible, or is BTC-in-a-wrapper just vol tourism?
4. What would change your mind on managed futures — how many flat years before you capitulate?

*All data/figures from a reproducible offline pipeline (testfol.io-style sims + Ken French + AQR data). Happy to share methodology details in comments.*
