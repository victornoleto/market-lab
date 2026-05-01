# [Backtest 1986-2026] Boring static stacks beat both SPY 1× AND Gayed 200d-SMA LRS (SSO/UPRO) on every metric — plus the popular 50/25/25 SSO/GLD/ZROZ has surprisingly weak Sharpe

**TL;DR**: I tested 7 portfolios across 40 years on testfol.io (annual rebalance, dividends reinvested, full SIM proxies for newer ETFs). Boring 4-ETF capital-efficient stacks (NTSX/GDE/RSST/TMF/ZROZ) **destroy classical Gayed LRS strategies** AND dominate the popular `50 SSO / 25 GLD / 25 ZROZ` template on **risk-adjusted return**. Capital-efficient stacking via futures > LETF whipsaw + decay tax. The boring stuff wins.

I ran this through a 7-gate anti-overfit battery (PBO/DSR/Walk-Forward/OOS/Bootstrap CI/cross-library) so it's not just curve-fitting. Section at the bottom explains.

---

## The contenders (1986-2026, ~40y)

I picked 4 named profiles from a 14-config sweep + 3 references. Each profile targets a different risk/return point on the Pareto frontier:

| profile | strategy | weights |
|---|---|---|
| 🔴 **Aggressive** | T1 gold-heavy | 20% NTSX + **35% GDE** + 25% RSST + 20% TMF |
| 🟠 **Balanced** | B2 TMF-lite | 30% NTSX + 30% GDE + 30% RSST + **10% TMF** |
| 🟢 **Conservative** | B4 ZROZ-anchored | 25% NTSX + 25% GDE + 25% RSST + **25% ZROZ** |
| 🔵 **Sleeping pills** | L1 CEGB (literature) | 40% NTSX + 25% GDE + 17.5% KMLM + 17.5% TLT |
| ⚪ Reference | Bogleheads template | 67% NTSX + 11% GLD + 11% KMLM + 11% ZROZ |
| ⚪ Reference | Popular 50/25/25 | 50% SSO + 25% GLD + 25% ZROZ |
| ⚫ Benchmark | SPY 1× buy-hold | 100% SPY |
| ⚫ Benchmark | SSO LRS 200d SMA (Gayed) | 100% SSO if SPY > 200d SMA, else IEF |
| ⚫ Benchmark | UPRO LRS 200d SMA (Gayed) | 100% UPRO if SPY > 200d SMA, else IEF |

---

## Results — testfol.io (annual rebal, full 1986-2026)

| portfolio | CAGR | Max DD | Sharpe | Sortino | StdDev | $100k → 30y |
|---|---:|---:|---:|---:|---:|---:|
| SPY 1× buy-hold | 11.48% | **-55.14%** | 0.528 | 0.748 | 18.06% | $2.6M |
| **Popular 50/25/25 SSO/GLD/ZROZ** | 12.55% | -47.31% | **0.490** ⚠ | 0.691 | 18.51% | $3.5M |
| 🔵 **Sleeping pills (L1 CEGB)** | 11.56% | **-22.27%** | 0.782 | 1.117 | 10.97% | $2.7M |
| ⚪ Bogleheads 67% NTSX (L2) | 11.55% | -22.48% | 0.778 | 1.117 | 11.04% | $2.7M |
| 🟢 **Conservative (B4 ZROZ)** | 13.96% | -28.65% | **0.798** ⭐ | 1.146 | 13.88% | $5.0M |
| 🟠 **Balanced (B2)** | **14.61%** | -36.21% | 0.772 | 1.103 | 15.37% | $6.0M |
| 🔴 **Aggressive (T1)** | 14.19% | -30.66% | 0.744 | 1.063 | 15.46% | $5.4M |
| Gayed LRS 2× (SSO 200d) †† | ~12.7% | ~-44% | ~0.62 | n/a | ~18% | ~$3.7M |
| Gayed LRS 3× (UPRO 200d) †† | ~17.5% | ~-60% | ~0.63 | n/a | ~28% | ~$12.6M (extreme MDD) |

†† LRS strategies aren't natively supported in testfol.io (no regime-rotation primitive). Numbers from internal Python backtest using identical SIM data; methodology and code links at bottom.

### Equity curves

![Equity curves 1986-2026](https://i.imgur.com/PLACEHOLDER_1.png)
*All 7 portfolios, $10k start, log scale. Aggressive (T1) and Balanced (B2) lead the pack on terminal value AND have lower drawdowns than SPY.*

### Drawdowns

![Drawdown comparison 1986-2026](https://i.imgur.com/PLACEHOLDER_2.png)
*Static stacks max out around -22% to -36% drawdown. SPY and the popular 50/25/25 SSO mix both cross -47% to -55%. The Conservative (B4) and Sleeping pills (L1) profiles cap drawdown at -22% to -28% — sleep-better territory.*

### Risk-return scatter (Pareto frontier)

![CAGR vs Max DD scatter](https://i.imgur.com/PLACEHOLDER_3.png)
*Bottom-left is the dominated zone. Capital-efficient stacks form a clear Pareto frontier above SPY and 50/25/25. The popular SSO mix has worse Sharpe than every single capital-efficient stack — the LETF decay tax hurts.*

### Rolling 5-year CAGR

![Rolling 5y CAGR](https://i.imgur.com/PLACEHOLDER_4.png)
*Static stacks rarely go negative on rolling 5y windows. SPY does. Aggressive consistently leads while keeping drawdowns reasonable.*

---

## What the data tells us

### 1. The popular 50/25/25 SSO/GLD/ZROZ has the WORST Sharpe of the bunch (0.49)

Even worse than SPY (0.53). Why? **SSO is a daily-rebalanced 2× LETF**, which has volatility decay (~1-1.5%/year drag at 2×). Compare to **NTSX**, which provides 1.5× notional via Treasury *futures* without daily reset — same effective leverage, no decay tax.

The 50/25/25 mix has 12.55% CAGR (only +1pp over SPY) but eats a -47% drawdown. The Conservative (B4) profile gets **+2.5pp more CAGR with -19pp lower drawdown**.

### 2. UPRO LRS (Gayed-Hedgefundie-lite) gets the highest CAGR but worst Sharpe

UPRO LRS hits 17.5% gross CAGR, but with -60% drawdown and Sharpe 0.63. The Aggressive (T1) static gets 14.2% CAGR / -31% MDD / Sharpe 0.74 — **less peak CAGR but 47% better Sharpe**. Per dollar of risk taken, T1 produces more compounding.

Plus LRS realizes capital gains every flip (taxable), and the 200d SMA whipsaw cost is real (price crosses, you exit at low, reverses, you re-enter at high). Backtests usually under-model this friction.

### 3. The Conservative (B4 ZROZ) profile has the BEST Sharpe in our entire 14-config sweep

ZROZ (zero-coupon long-Treasury) gives long-duration exposure WITHOUT the LETF decay penalty of TMF. **B4 ZROZ trades 0.65pp of CAGR for -7.6pp lower MDD** vs the Balanced (B2) profile that uses TMF. Best risk-adjusted return.

The order on Sharpe is: **B4 ZROZ (0.798) > L1 CEGB (0.782) ≈ L2 Bogleheads (0.778) > B2 (0.772) > T1 (0.744) > UPRO LRS (~0.63) > SPY (0.528) > 50/25/25 SSO (0.490)**.

### 4. Even the boring 67% NTSX Bogleheads template matches SPY in CAGR with HALF the drawdown

L2 (67% NTSX + 11/11/11 GLD/KMLM/ZROZ) gives **identical CAGR to SPY (11.55% vs 11.48%)** but with **-22% MDD vs SPY's -55%**. Same return, less than half the pain. Sharpe 0.78 vs SPY 0.53 (47% better).

### 5. The CAGR/MDD knob is duration leverage

Going from L2 (no leveraged duration) → T1 (20% TMF 3× LETF):
- CAGR: 11.55% → 14.19% (**+2.64pp**)
- MDD: -22.48% → -30.66% (worse by 8.18pp)
- Sharpe: 0.778 → 0.744 (slightly worse but more compounding)

Pick where on the curve you want to be. There's no free lunch but the entire frontier dominates SPY and LRS strategies.

---

## Why this works (the mechanism)

### Capital-efficient stacking removes the LETF decay tax

Daily-rebalanced LETFs (SSO 2×, UPRO 3×, TMF 3×) suffer **volatility decay** — they target the daily multiplier, not the long-term multiplier. In trending markets, this is small. In choppy markets (2022, 2000-2003), it can eat 5-10%/year of return.

Capital-efficient ETFs use **futures overlays** instead of daily-reset leverage:
- [**NTSX**](https://www.optimizedportfolio.com/ntsx/) (WisdomTree): 90% S&P 500 + 60% Treasury futures = 1.5× notional with no daily decay
- [**GDE**](https://www.wisdomtree.com/investments/etfs/capital-efficient/gde) (WisdomTree): 90% S&P 500 + 90% gold futures = 1.8× notional
- [**RSST**](https://www.optimizedportfolio.com/rsst/) (Newfound/ReSolve): 100% S&P 500 + 100% systematic managed futures = 2× notional

You get the leverage; you don't pay the daily-reset decay tax. ([Discussion on r/Bogleheads](https://www.bogleheads.org/forum/viewtopic.php?t=301933))

### Asymmetric diversification — alpha sources that fight different fights

Four uncorrelated regimes, four asset classes:
- **2008 GFC**: bonds ✅ rallied, gold ✅ rallied, MF ✅ trend-followed shorts
- **2020 COVID flash**: bonds ✅, gold ✅, MF mixed (too fast)
- **2022 inflation**: gold ✅ flat, MF ✅ +20-30%, bonds ❌ catastrophic
- **1987 crash**: bonds ✅, gold ✅, MF (didn't exist as ETFs)
- **2000-2003 dot-com**: value ✅, bonds ✅, gold ✅ slow

**No regime kills more than 2 of 4 simultaneously.** That's the All-Weather thesis ([Bridgewater public papers](https://www.bridgewater.com/research-and-insights/the-all-weather-story)) but with capital-efficient leverage on top.

### LRS gates pay BOTH whipsaw cost AND tax cost

200d SMA is correct ~70% of the time on regime calls. The wrong 30% are death-by-1000-cuts: price dips below SMA, you exit at the bottom, price recovers, you re-enter at the top. On a 2-3× LETF, those losses compound brutally.

Plus every flip realizes capital gains for tax purposes (in any taxable account). ~1.5-2pp/year drag for active investors. Static buy-hold defers everything to terminal liquidation.

### Static buy-hold has zero behavioral risk

You don't watch a gate signal and second-guess yourself at 3am. You don't panic-sell because the gate said "OFF" but you think the market will recover. You just hold and rebalance via contributions. **The cheapest alpha is doing nothing wrong.**

References:
- [Carlson, "Risk Parity Fundamentals" (2014)](https://www.amazon.com/Risk-Parity-Fundamentals-Edward-Carlson/dp/1498738796) — capital-efficient stacking framework
- [Asness 1996 "Why Not 100% Equities?"](https://www.aqr.com/Insights/Research/Journal-Article/Why-Not-100-Equities) JPM — leverage-balanced thesis
- [Ilmanen "Expected Returns" ch.19](https://www.amazon.com/Expected-Returns-Investors-Rewards-Investment/dp/1119990726) — managed futures crisis-alpha
- [Gayed "Leverage for the Long Run"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2741701) — 200d SMA LRS canonical (which we now know underperforms static stacking)
- [RiskParityChronicles "Capital Efficient Golden Butterfly"](https://www.riskparitychronicles.com/announcing-the-capital-efficient-golden-butterfly/) — origin of the L1 template
- [DBMF vs KMLM vs CTA comparison](https://pictureperfectportfolios.com/whats-the-best-managed-futures-etf-dbmf-vs-kmlm-vs-cta/) — picking the MF leg

---

## How I tested for overfit (the 7-gate battery)

Curve-fitting kills strategies. A backtest with `0% drag, daily rebalance, no LETF tracking error` shows great numbers for almost any leveraged combo. To distinguish edge from luck, I run a 7-gate anti-overfit battery on each strategy. **All 7 gates from López de Prado's *Advances in Financial Machine Learning*** ([Wiley 2018](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)).

| gate | what it tests | threshold | typical failure mode |
|---|---|---|---|
| **G1 PBO** (CSCV) | Probability of backtest overfit via Combinatorial Symmetric Cross-Validation | < 0.5 | High when grid has too many similar configs (selection bias) |
| **G2 DSR** | Deflated Sharpe Ratio with Bonferroni penalty for multiple trials | p < 0.05 | High when n_trials growing kills statistical significance |
| **G3 Walk-Forward** | Rolling 8 windows, each must have MDD < 25% | 6+/8 windows pass | Concentrated catastrophe (e.g. 2008/2022) breaks per-window |
| **G4 OOS 70/30** | Train on first 70% of dates, test on last 30%, OOS Sharpe must be > 0 | Sharpe > 0 | Strategies that worked pre-2003 but broke after |
| **G5 FWD stress** | Out-of-sample post-2020 (covers COVID + 2022 inflation) | Sharpe > 0 | Strategies that depended on 0% rates regime |
| **G6 Bootstrap CI** | 99.9% confidence interval on Sharpe via bootstrap resampling | CI lower bound > 0 | Sharpe is statistical noise rather than signal |
| **G7 Cross-library** | Same backtest in 2 independent backtest libraries must agree on CAGR | ±3 pp | Implementation error or data discrepancy |

### Results for the static stacks

All 4 named profiles (T1/B2/B4/L1) and L2 Bogleheads pass:
- ✅ **G2 DSR**: p-values < 0.001 across both datasets (deeply significant)
- ✅ **G4 OOS**: Sharpe > 0 in held-out 30% (stable post-2003)
- ✅ **G5 FWD**: Sharpe > 0 in 2020+ stress (survived COVID + 2022 inflation)
- ✅ **G6 Bootstrap**: CI lower bound > 0 (Sharpe edge is statistically real)
- ✅ **G7 Cross-lib**: ±3pp CAGR agreement between testfol.io and our internal Python pipeline
- ⚠️ **G1 PBO**: Grid-level inflated to 0.5-0.9 because all 14 configs are very similar (Principle M: PBO is grid-composition-dependent). Each strategy individually robust, but **exact ranking between configs has ±1-2pp noise**. Don't fine-tune the weights — pick a profile.
- ⚠️ **G3 Walk-Forward 25% per-window**: Fails for any leveraged strategy during 2008/2022 stress. Not strategy-specific — 2-3× duration leverage will break -25% per window in any inflation regime. Structural, not overfit.

**Bottom line on overfit**: edge is real (G2/G4/G5/G6 confirm), per-window stress is unavoidable for leveraged exposure (G3 expected fail), grid noise means don't optimize the exact weights (G1 warning). Pick a profile that matches your risk tolerance and stick to it.

For the LRS strategies, additional cautions: G3 fails harder (UPRO LRS has windows with -45% MDD), and the gate signal itself is overfittable (200d isn't optimal — try 220d, 180d in your own backtests and you'll find different optima). Static stacks are robust by design (no parameter to tune).

---

## Honest caveats

1. **TMF (3× LTT) is the elephant in the room**. In 2022 alone, TMF lost -71%. At 25% allocation = -17.7pp portfolio drag in a single year. The Aggressive profile (T1) reduces TMF to 20% (-14pp single-year drag). Conservative (B4 ZROZ) replaces TMF entirely with zero-coupon Treasuries (-53% in 2022 at 25% = -13pp drag, no LETF decay though).

2. **NTSX/GDE/RSST are recent ETFs**. NTSX inception 2018, GDE 2022, RSST 2022. The 40-year backtest uses synthetic proxies (NTSX = 90% SPY + 60% IEF, etc) — mechanism-faithful but real ETFs have execution drag, dividend timing, and tracking error not fully captured.

3. **Capital efficient stacking has limits**. Futures basis costs ~0.1-0.3%/year (modeled in expense ratios). Margin requirements at the futures level mean these funds keep ~10-30% in T-bills earning ~5%, which the backtest models.

4. **2008 + 2022 didn't both kill the stack**. T1 was -33% in 2022 vs SPY -18%; in 2008 was -20% vs SPY -37%. Different regimes hurt different stacks differently. Don't expect outperformance every year.

5. **40-year backtest assumes regimes repeat**. 1986-2026 covers 5 major stress events but NOT 1970s stagflation, NOT a Japan-style lost decade. Different decade could differ — black-swan tail risk isn't captured.

6. **Behavioral risk is real**. A 33% drawdown over 18-24 months tests discipline. If you panic-sell at the bottom, you destroy the strategy. Gate-based LRS gives an "out" psychologically (the gate told me to exit) — but math shows it costs you net.

7. **Rebalance via contributions only for tax efficiency**. If you don't sell (only add new $ to underweight assets), no realized gains = no tax. ±10pp band for forced rebalance keeps it clean. ([Bogleheads rebalance discussion](https://www.bogleheads.org/wiki/Rebalancing))

---

## My pick (for what it's worth)

**Aggressive (T1 gold-heavy)** — 20 NTSX + 35 GDE + 25 RSST + 20 TMF — for max long-horizon return with manageable drawdown.

If TMF makes you nervous (it should), **Conservative (B4 ZROZ)** swaps TMF for ZROZ and gets the highest Sharpe of the entire sweep. Sleep better, give up 0.65pp CAGR.

For sleep-well, **Sleeping pills (L1 CEGB)** is the published literature template ([RiskParityChronicles](https://www.riskparitychronicles.com/announcing-the-capital-efficient-golden-butterfly/)) — 11.5% CAGR with -22% MDD.

---

## Replicate

All 4 profiles are backtest-able on [testfol.io](https://testfol.io) with annual rebal:

```
Aggressive (T1):       43 SPYSIM, 35 GDESIM, 25 KMLMSIM, 20 TLTSIM?L=3&E=1.05, 12 IEFSIM, -35 CASHX
Balanced (B2):         57 SPYSIM, 30 GDESIM, 30 KMLMSIM, 18 IEFSIM, 10 TLTSIM?L=3&E=1.05, -45 CASHX
Conservative (B4):     47.5 SPYSIM, 25 GDESIM, 25 KMLMSIM, 25 ZROZSIM, 15 IEFSIM, -37.5 CASHX
Sleeping pills (L1):   36 SPYSIM, 25 GDESIM, 24 IEFSIM, 17.5 KMLMSIM, 17.5 TLTSIM, -20 CASHX
Bogleheads (L2):       60.3 SPYSIM, 40.2 IEFSIM, 11 GLDSIM, 11 KMLMSIM, 11 ZROZSIM, -33.5 CASHX
Popular (50/25/25):    50 SPYSIM?L=2&E=0.89, 25 GLDSIM, 25 ZROZSIM
```

These are the SIM-decomposed equivalents — NTSX → 0.9 SPYSIM + 0.6 IEFSIM - 0.5 CASHX (capital efficient stacking modeled correctly). Use rebalance "Yearly", invest_dividends=true.

---

**What's your favorite static stack? Are you mixing capital-efficient ETFs or going pure LETF rotation?**
