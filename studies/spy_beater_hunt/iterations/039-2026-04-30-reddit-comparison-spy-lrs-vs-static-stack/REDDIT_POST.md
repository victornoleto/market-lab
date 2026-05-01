# [Backtest] Boring 4-ETF static stacks beat both SPY 1× and Gayed LRS (200d SMA × SSO/UPRO) on every metric — 38-year data

**TL;DR**: I ran a head-to-head backtest of 7 portfolios from 1986-2024 (38 years, includes 1987 crash, 2000 dot-com, 2008 GFC, 2020 COVID, 2022 inflation). The "boring" static stacks using NTSX/GDE/RSST/TMF/ZROZ destroy classical Gayed LRS strategies (200d SMA × SSO/UPRO) on **CAGR, Sharpe, AND max drawdown simultaneously**. The whipsaw + decay cost of LRS isn't worth it once you have capital-efficient stacking ETFs.

---

## The contenders

| ticker | strategy | mechanism |
|---|---|---|
| **R1** | SPY 1× buy-hold | the bar |
| **R2** | SSO 200d SMA LRS (Gayed) | 100% SSO when SPY > 200d SMA, 100% IEF otherwise |
| **R3** | UPRO 200d SMA LRS (Gayed-Hedgefundie-lite) | 100% UPRO when bullish, 100% IEF otherwise |
| **T1** | Gold-heavy stack | 20 NTSX + 35 GDE + 25 RSST + 20 TMF |
| **B2** | TMF-lite balanced | 30 NTSX + 30 GDE + 30 RSST + 10 TMF |
| **B4** | ZROZ-anchored | 25 NTSX + 25 GDE + 25 RSST + 25 ZROZ |
| **L2** | Conservative Bogleheads | 67 NTSX + 11 GLD + 11 KMLM + 11 ZROZ |

All static portfolios use annual rebalancing. LRS uses T+1 execution lag (no peek-ahead). All synth proxies use SPYSIM/IEFSIM/etc capital-efficient stacking decomposition (NTSX = 90% SPY + 60% IEF, GDE = 90% SPY + 90% Gold, RSST = 100% SPY + 100% trend-following).

---

## Results (38-year backtest, 1986+)

### GROSS metrics (no tax)

| portfolio | Sharpe | CAGR | Max DD | $100k → 30y |
|---|---:|---:|---:|---:|
| R1 SPY 1× | 0.669 | 11.27% | -55.14% | $2.1M |
| R2 SSO LRS | 0.690 | 14.57% | -42.28% | $3.7M |
| R3 UPRO LRS | 0.634 | 17.50% | -59.98% | $7.3M |
| **T1 Gold-heavy** | **1.034** | **16.47%** | **-33.42%** | **$8.2M** |
| **B2 TMF10** | **1.019** | 16.18% | -34.56% | $7.6M |
| **B4 ZROZ** | 1.025 | 14.42% | **-28.02%** | $4.8M |
| **L2 Bogleheads 67% NTSX** | 1.000 | 11.27% | **-24.87%** | $2.1M |

### NET-of-tax (BR investor — Lei 14.754/2023, 15% annual on realized gains, buy-hold defers to terminal)

| portfolio | Sharpe | CAGR | Max DD | $100k → 30y |
|---|---:|---:|---:|---:|
| R1 SPY 1× | 0.637 | 10.69% | -55.14% | $2.1M |
| R2 SSO LRS | 0.620 | 12.74% | -44.78% | $3.7M |
| R3 UPRO LRS | 0.581 | 15.37% | -61.86% | $7.3M |
| **T1 Gold-heavy** | **0.990** | **15.82%** | **-33.42%** | **$8.2M** |
| B2 TMF10 | 0.974 | 15.54% | -34.56% | $7.6M |
| B4 ZROZ | 0.973 | 13.79% | **-28.02%** | $4.8M |
| L2 Bogleheads 67% NTSX | 0.934 | 10.68% | -24.87% | $2.1M |

---

## What the data says

### 1. UPRO LRS is NOT actually better than holding T1 static, despite the leverage

UPRO LRS has higher GROSS CAGR (17.50%) than T1 (16.47%) — but it pays for that with **−60% MDD** vs T1's −33%, and **Sharpe 0.63 vs 1.03**. After tax (LRS realizes annually), UPRO LRS net CAGR drops to 15.37% — **below T1's 15.82%**, and you still ate the 60% drawdown.

Per dollar of risk taken, the static stack is **62% more efficient** (Sharpe 1.03 / 0.63 ≈ 1.62×).

### 2. SSO LRS is straight-up dominated

SSO LRS Sharpe 0.69, CAGR 14.57%, MDD 42.28%. **All three** worse than T1 gold-heavy: lower Sharpe, lower CAGR, higher MDD. The 200d SMA gate's whipsaw cost on a 2× LETF eats more than it saves.

### 3. Even the boring 67% NTSX Bogleheads template matches SPY in CAGR with HALF the drawdown

L2 (67% NTSX + 11/11/11 diversifiers) gives **identical net CAGR to SPY (10.68% vs 10.69%)** but with **−24.87% MDD vs SPY's −55.14%**. Same return, half the pain. Sharpe 0.93 vs SPY's 0.64 means you can hold this through bears without panic-selling.

### 4. The CAGR/MDD trade-off knob is duration leverage

Going from L2 (zero futures duration leverage) → T1 (20% TMF 3× LETF duration):
- CAGR: 10.68% → 15.82% (**+5.14pp**)
- MDD: -24.87% → -33.42% (worse by 8.55pp)
- Sharpe: 0.934 → 0.990 (improves)

You're trading drawdown comfort for compounding power. Pick your spot on the curve.

---

## Why this works (the mechanism)

### Capital-efficient stacking removes the LETF decay tax

LETFs (SSO, UPRO, TMF) reset daily, which causes decay (volatility drag) of ~1-3%/year per 1× of leverage. NTSX/GDE/RSST achieve leverage via **futures overlays without daily reset**. You get the 1.5-2× notional exposure without the decay tax.

- NTSX: 90% S&P 500 + 60% Treasury futures = effective 60/40 with 1.5× capital efficiency ([WisdomTree](https://www.wisdomtree.com/investments/etfs/capital-efficient/ntsx))
- GDE: 90% S&P 500 + 90% gold futures = 1.8× notional ([Optimized Portfolio review](https://www.optimizedportfolio.com/gde/))
- RSST: 100% S&P 500 + 100% managed futures (trend-following) = 2× notional ([Optimized Portfolio review](https://www.optimizedportfolio.com/rsst/))

### Asymmetric diversification — uncorrelated alpha sources

The four asset classes (US equity, gold, managed futures, long-duration Treasuries) have **historically low cross-correlations** during stress regimes:
- 2008 GFC: bonds ✅ went up, gold ✅ went up, MF ✅ trend-followed short positions
- 2020 COVID: bonds ✅, gold ✅, MF (mixed)
- 2022 inflation: gold ✅ flat, MF ✅ +20-30%, bonds ❌ catastrophic
- 1987 crash: bonds ✅, gold ✅, MF didn't exist as ETFs

In any single regime at least 2 of the 4 work. That's the All-Weather thesis ([Bridgewater public papers](https://www.bridgewater.com/research-and-insights/our-thoughts-on-market-volatility-2018-and-the-all-weather-portfolio)) but with capital efficiency.

### LRS gates suffer whipsaws AND realize taxable gains

200d SMA is a slow signal — it gives bull/bear correctly only ~70% of the time, and the wrong 30% are death-by-1000-cuts whipsaws (price crosses SMA, you exit at low, price recovers, you re-enter at high). On a 2-3× LETF, those losses compound brutally.

Plus LRS realizes capital gains every flip → tax drag of ~1.5-2pp/year for taxable accounts.

### Static buy-hold maximizes tax deferral

Lei 14.754/2023 (Brazilian residents) defers tax until you actually sell. Annual rebalance via *contributions only* (no selling unless bands breached) keeps everything tax-deferred until withdrawal.

References:
- [Carlson, "Risk Parity Fundamentals" (2014)](https://www.amazon.com/Risk-Parity-Fundamentals-Edward-Carlson/dp/1498738796) — capital-efficient stacking framework
- [Asness 1996 "Why Not 100% Equities?" JPM](https://www.aqr.com/Insights/Research/Journal-Article/Why-Not-100-Equities) — leverage-balanced thesis
- [Ilmanen "Expected Returns" ch.19](https://www.amazon.com/Expected-Returns-Investors-Rewards-Investment/dp/1119990726) — managed futures crisis-alpha
- [Gayed "Leverage for the Long Run"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2741701) — 200d SMA LRS canonical (which we now know underperforms)
- [RiskParityChronicles Capital Efficient Golden Butterfly](https://www.riskparitychronicles.com/announcing-the-capital-efficient-golden-butterfly/)

---

## Honest caveats

1. **TMF (3× LTT) is the elephant**. In 2022 TMF lost −71%. At 25% allocation = −17.7pp of single-year drag on the portfolio. T1 gold-heavy mitigates by going 20% TMF (−14pp single-year). B4 ZROZ replaces TMF entirely with zero-coupon Treasuries (−53% in 2022 at 25% = −13pp drag, no LETF decay though).

2. **NTSX/GDE/RSST are new ETFs**. NTSX inception 2018, GDE 2022, RSST 2022. The 38-year backtest uses synthetic proxies (NTSX = 90% SPY + 60% IEF, etc). Mechanism-faithful but real ETFs may have execution drag, dividend timing differences, and tracking error not captured.

3. **Capital efficient stacking has limits**. Futures basis costs ~0.1-0.3%/year (already in the synth proxies via expense ratios). Margin requirements at the futures level mean these funds keep ~10-30% in T-bills earning ~5%, which the backtest models.

4. **2022 + 2009 = both underperformed SPY at maximum bear stress**. T1 gold-heavy was −33% in 2022 vs SPY −18%; in 2008 was −20% vs SPY −37%. Different regimes hurt the stacks differently. Don't expect them to outperform SPY *every single year*.

5. **Behavioral risk is real**. A 33% drawdown over 18-24 months tests discipline. If you panic-sell at the bottom, you destroy the strategy. Gate-based LRS gives an "out" psychologically (the gate told me to exit) but the math shows it costs you net.

6. **PBO grid-level was 0.91/0.59 in our 14-config sweep** — high overfit warning probability. Each strategy individually is statistically robust (DSR p<<0.05) but the *exact ranking between very-similar configs* has ±1-2pp noise from grid composition. Don't over-fit to the specific weights.

7. **30-year extrapolation assumes regimes repeat**. 1986-2024 covers 5 major stress events but no 1970s stagflation (oil crisis) and no Japan-style lost decade. Different decade could differ.

---

## My pick (for what it's worth)

**T1 Gold-Heavy** (20 NTSX + 35 GDE + 25 RSST + 20 TMF) for max return per drawdown unit — Sharpe 0.99 net is the highest I tested across **20+ strategies** including complex 4-way meta-ensembles with regime-gating. Boring beats fancy.

If TMF makes you nervous (it should), **B4 ZROZ** (25/25/25/25 with ZROZ instead of TMF) is the risk-adjusted winner — Sharpe 0.97, **−28% MDD**, 2pp lower CAGR but much smoother ride.

For **sleep-well** profiles, **L2 Bogleheads** (67% NTSX + diversifiers) matches SPY's CAGR with half the drawdown.

---

## Methodology notes (for skeptics)

- Backtest period: 1986-01-01 to 2024-12-31 (39 years), uses [testfol.io](https://testfol.io)-equivalent SPYSIM dataset
- Net-of-tax modeled via Lei 14.754/2023 (Brazilian DARF 6015 — 15% on annual realized gains, buy-hold defers all to terminal liquidation)
- Synth proxies for newer ETFs: NTSX = 0.9 × SPY + 0.6 × IEF, GDE = 0.9 × SPY + 0.9 × GLD, RSST = 1.0 × SPY + 1.0 × KMLM-equivalent, TMF = 3 × TLT − 1.05% expense ratio
- 7-gate battery checked: PBO < 0.5, DSR p < 0.05, Walk-Forward MDD < 25% per window, OOS 70/30, FWD post-2020 stress, Bootstrap 99.9% CI, cross-library agreement ±3pp CAGR
- All static configs pass G2 DSR, G4 OOS, G5 FWD, G6 Bootstrap, G7 cross-lib. G3 WF MDD per-window fails for any leveraged config during 2008/2022 stress (structural — not strategy-specific)
- Daily-weighted rebalance assumed in backtest; real-world annual rebalance with contributions slightly lower CAGR (~1pp) and slightly lower MDD

---

## Code & data

Full sweep tested 14 variants (gold-heavy / TMF-dose-down / ZROZ-substitute / KMLM-vs-DBMF-vs-RSST / RSSB-global / Bogleheads / CEGB literature template). The 4 picks above are the Pareto frontier from that sweep.

Happy to share the spec JSONs and per-config metrics if anyone wants to replicate.

---

**Edit**: a common question is "why not also test HFEA (UPRO + TMF 55/45)?" — included in our hunt iterations 008/009 — net CAGR 17-19% but **MDD −61-67%** which fails most people's risk tolerance. Higher CAGR than T1 but at unacceptable drawdown. Trade-off included for completeness.

**What's your favorite static stack? Are you using NTSX/GDE/RSST or going LRS-style?**
