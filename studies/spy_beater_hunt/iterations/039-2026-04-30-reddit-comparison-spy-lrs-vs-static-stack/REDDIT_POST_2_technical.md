# [Deep dive v2] 14-config static stack sweep + Post 1 community feedback integrated — 4 follow-up tests + 7-gate anti-overfit framework

**TL;DR**: Follow-up to my [Post 1](https://www.reddit.com/r/LETFs/comments/1t0i3qm/) where I shared 4 boring static portfolios that beat SPY on **both** CAGR and Max DD over 1987-2026. The 4 candidates are simple buy-and-hold stacks built on capital-efficient ETFs — **NTSX** (90% SPY + 60% Treasury futures), **GDE** (90% SPY + 90% gold futures), **RSST** (100% SPY + 100% systematic managed futures) — plus a duration sleeve (TMF / ZROZ / TLT). No signals, no regime gates, no rebal whipsaw.

**2026-05-02 methodology note before posting:** I made one tax correction and one explicit proxy choice. First, for static buy-and-hold/lazy-rebal portfolios I should **not** apply terminal DARF in the comparison; tax drag belongs in swing/tactical strategies that realize gains through position changes, not in these buy-and-hold stacks. Second, this post intentionally uses the longer-window RSST proxy `SPY + KMLM - cash` so the main study can run back to 1987. A live RSST tracking check suggests real RSST is closer to `SPY + 70% DBMF + 30% KMLM - cash`, but DBMFSIM starts in 2000, which would cut the study to 26 years. I prefer the longer backtest for the main post and treat the 70/30 DBMF/KMLM version as a final caveat/sensitivity check. Return stacking rationale: `[risk_parity, ch.5, p.10]`; diversified managed-futures engine rationale: `[ilmanen_expected_returns, ch.19]`.

**This Post 2 is the methodology + the community-critique integration.** After Post 1 went up, you gave me 4 specific empirical critiques. I ran each one as a separate iteration:

- **u/perky_python** — "your sim ignores rebal cadence + ERs" → **monthly rebal + explicit ERs across all configs**
- **u/Fun-Sundae4060 + u/no_simpsons** — "TQQQ + 200d SMA gives ~10,000%" → **6 G3 regime-gate variants tested**
- **u/Grouchy_Release_2321 + u/perky_python** — "SPY-base is US-survivorship-bias" → **5 G4 international variants (NTSD / RSSB / VT)**
- **u/laurenthu** — "re-fit weights on rolling 5y windows" → **walk-forward max-Sharpe G8 gate**

Plus the full **7-gate anti-overfit battery** (PBO / DSR / Walk-Forward / OOS 70-30 / FWD stress / Bootstrap CI / Cross-library) + the new **G8 weight-drift gate**. Full data, full methodology, what changed, what survived, what didn't.

**Headline change from Post 1**: top-level rebalance is now **monthly** (not yearly) and **expense ratios are explicit**. This shifts the Pareto frontier in interesting ways — most notably, **Popular 50/25/25 SSO/GLD/ZROZ loses 10.71pp of MDD** (-39.84% → -50.55%) when you rebalance monthly. The capital-efficient stacks (NTSX/GDE/RSST) are virtually immune.

**Headline finding**: on the longer 1987-2026 window, B4 Conservative (25 NTSX / 25 GDE / 25 RSST-like KMLM trend stack / 25 ZROZ) is still the best balanced pick: high enough CAGR, materially lower drawdown than SPY, and the best Sharpe among the long-window static stacks. L1 CEGB remains the lower-stress alternative; B5/B2/T1 buy more CAGR with materially deeper drawdowns.

---

## What changed since Post 1 (4 community-driven follow-ups)

| Critic | Critique | Test | Verdict |
|---|---|---|---|
| u/perky_python | "Your sim ignores rebal cadence + ERs. Real CAGR is ~1pp lower." | **Re-ran with Monthly rebal + explicit ERs (NTSX 0.20%, GDE 0.20%, RSST 0.99%, KMLM 0.92%, GLD 0.40%, ZROZ 0.15%, etc).** | ⚠️ Partial. CAGR drops 0.5-0.9pp on stacks (less than 1pp). MDD on Popular 50/25/25 worsens **-10.71pp** (huge finding). |
| u/Fun-Sundae4060 + u/no_simpsons | "Try TQQQ/QQQ regime-gate × diversifiers above/below 200d SMA. ~10,000% return." | **Tested 6 G3 variants** (Fun-Sundae spec, NDX-heavy, with bonds, minimal, Gayed-NDX, pure TQQQ/QQQ swap). | ❌ The "~10,000%" return is computed over 2012-2025 (cherry-picked window without dotcom). On 1987-2026 with 2000-2002 included, the regime gate produces much worse drawdowns than B4. |
| u/Grouchy_Release_2321 + u/perky_python | "SPY-only base is US-survivorship-bias. Try VT/RSSB/NTSI." | **Tested 5 G4 variants** with NTSD, RSSB, mixed US/International. | ⚠️ In the long-window table, US-bias accounted for only ~4% of B4's Sharpe edge. This is directional because synthetic international/stacked proxies add their own uncertainty. **G4d (RSSB-based) breaks the MDD record at -22.56%** — the lowest in the broader study. |
| u/laurenthu | "Re-fit weights on rolling 5y windows. If they drift, edge is window-specific." | **Walk-forward max-Sharpe optimization on B4/B2/T1 universes.** | ✅ G8 PASS. Weights drift wildly (60-75pp range) BUT static portfolio Sharpe **beats** walk-forward in all 3 universes. Static = optimal shrinkage estimator (DeMiguel/Garlappi/Uppal 2009 RFS). |

**Overall**: B4 Conservative survives the critique process as the balanced pick on the long-window study. The final caveat is that live RSST may be better approximated by a 70/30 DBMF/KMLM trend sleeve, which starts only in 2000 and produces somewhat different absolute numbers.

---

## Methodology — Monthly rebal + explicit ERs (refresh from Post 1)

Post 1 used `rebalance_freq: Yearly` with no ER drag. Per perky_python's critique, that's an idealized backtest. Realistic deployment would:

- **Top-level rebal: monthly** (matches monthly contribution cadence; what most retail investors actually do).
- **Internal ETF rebal**: NTSX/GDE quarterly (5% threshold), RSST daily — **not our concern** (vendor's responsibility).
- **Real ERs applied as `drag`** on each portfolio: weighted average per portfolio.

ERs used (per issuer prospectus):

| ETF | ER (% / yr) |
|---|---:|
| NTSX | 0.20 |
| GDE | 0.20 |
| RSST | 0.99 |
| KMLM | 0.92 |
| GLD | 0.40 |
| ZROZ / TLT / IEF | 0.15 each |
| GOVZ | 0.10 |
| SPY | 0.0945 |
| SSO (= SPYSIM?L=2&E=0.89) | 0.89 |
| UPRO (= SPYSIM?L=3&E=0.91) | 0.91 |
| TMF (= TLTSIM?L=3&E=1.05) | 1.05 |

Per-portfolio drag (weighted ER):
- B4 Conservative: 0.385%
- B2 Balanced: 0.417%
- T1 Aggressive: 0.358%
- L1 Sleeping pills: 0.317%
- L2 Bogleheads: 0.296%
- Popular 50/25/25: 0.138% (SSO ER baked into the leveraged SIM)

---

## Updated results — Monthly rebal + ERs, no DARF for buy-and-hold (long 1987-2026 window)

**Tax model**: no DARF applied for the static buy-and-hold/lazy-rebal portfolios in this section. Taxes should be modeled for swing/tactical strategies that realize gains through position changes, not for static stacks that are accumulated and held.

**RSST proxy for this main study**: `SPY + KMLM - CASHX`. This is not the closest live RSST tracking proxy; it is the longer-history managed-futures proxy that lets the study run from `1987-12-30 → 2026-04-29`.

Why use KMLM-only here? Because DBMFSIM starts in 2000. A 70/30 DBMF/KMLM trend sleeve probably tracks live RSST better, but it removes 12+ years of useful stress history. For this post I prefer the longer regime sample and explicitly caveat that the absolute RSST-containing results may shift under the shorter 70/30 proxy.

This is the main long-window methodology for the post. The 2000+ `70% DBMF / 30% KMLM` version is a tracking-sensitivity check, not the headline table.

### Main contenders (Pareto frontier)

| portfolio | CAGR | Max DD | Sharpe | Sortino | Calmar |
|---|---:|---:|---:|---:|---:|
| SPY 1× buy-hold | 11.37% | -55.20% | 0.523 | 0.740 | 0.206 |
| 🔵 **Sleeping pills (L1 CEGB)** | 11.06% | **-25.43%** | 0.729 | 1.044 | 0.435 |
| ⚪ Bogleheads 67% NTSX (L2) | 11.06% | -26.30% | 0.722 | 1.037 | 0.420 |
| 🟢 **Conservative (B4 ZROZ)** ⭐ | **13.31%** | -28.94% | **0.745** | **1.071** | **0.460** |
| 🟠 **T1 gold-heavy** | 13.34% | -34.65% | 0.688 | 0.984 | 0.385 |
| 🔴 **B2 TMF10** | 13.89% | -36.38% | 0.718 | 1.028 | 0.382 |
| B5 no duration | **14.22%** | -41.12% | 0.687 | 0.981 | 0.346 |

Tax note: Gayed/LRS strategies still need a separate after-tax model because regime flips realize gains. The static stacks above do not get recurring DARF in this comparison.

**Equity curves** ($10k start, log scale, long-window proxy `1987-12-30 → 2026-04-29`):

![Equity curves 1987-2026 long-window RSST proxy](testfolio_01_equity.png)
*Visual ranking by terminal value using the longer-history RSST proxy (`SPY + KMLM - cash`), monthly rebalance, explicit ERs, and no DARF for static buy-and-hold/lazy-rebal. B5 has the highest terminal value but much higher drawdown; B4 remains the best Sharpe/CAGR/MDD compromise; L1 has the smoothest ride.*

**Pareto frontier — CAGR vs Max DD** (the "interesting zone" is the upper-right quadrant, where CAGR > SPY AND |MaxDD| < SPY):

![Pareto CAGR vs MaxDD](testfolio_03_scatter.png)
*Green region = beats SPY on both axes. This chart shows the long-window static-stack universe; DBMF-only/blend variants are omitted from the scatter because DBMFSIM starts in 2000 and is not directly comparable. The practical frontier is L1/L2 for lowest stress, B4 for balanced Sharpe/CAGR/MDD, and B5/B2/T1 if you accept progressively larger drawdowns.*

**Key changes vs Post 1** (after monthly ERs + explicit long-window RSST proxy):
- B4 remains the **highest-Sharpe balanced pick**: CAGR 13.31%, MDD -28.94%, Sharpe 0.745 over ~38.3y.
- L1 CEGB remains the **lowest-stress reference**: CAGR 11.06%, MDD -25.43%, Sharpe 0.729.
- B2/T1/B5 still offer more CAGR than B4, but require accepting much deeper drawdowns (34.6-41.1%).
- Popular 50/25/25's monthly-rebal MDD blowup remains an important caution from the earlier monthly/ER test.

### Updated full sweep — long-window static stack table (Monthly + ERs, no DARF)

| config | family | CAGR | Max DD | Sharpe | Notes |
|---|---|---:|---:|---:|---|
| **Conservative (B4 ZROZ)** | B/Static | 13.31% | -28.94% | **0.745** ⭐ | balanced pick: best Sharpe, sub-30% MDD |
| B3 TLT instead of TMF | B/Static | 12.44% | -30.06% | 0.735 | second-line backup if ZROZ/GOVZ unavailable |
| Sleeping pills (L1 CEGB) | L/Static | 11.06% | **-25.43%** | 0.729 | lowest stress |
| Bogleheads 67 NTSX (L2) | L/Static | 11.06% | -26.30% | 0.722 | low-risk reference |
| **B2 TMF10** | B/Static | 13.89% | -36.38% | 0.718 | high-CAGR alternative |
| T2 equity-heavy | B/Static | 13.40% | -33.14% | 0.707 | NTSX 35% |
| **T1 gold-heavy** | B/Static | 13.34% | -34.65% | 0.688 | more CAGR, worse drawdown |
| B5 no duration | B/Static | **14.22%** | -41.12% | 0.687 | highest CAGR, high MDD |
| B1 user baseline 25 TMF | B/Static | 12.93% | -38.78% | 0.665 | original spec — TMF 25% costs MDD |
| M4 RSST+KMLM blend | M/Static | 11.85% | -37.27% | 0.645 | dual MF source, still long-window |
| T3 RSSB global | B/Static | 12.31% | -41.39% | 0.623 | global stack, MDD inflated |
| M1 KMLM no RSST | M/Static | 10.74% | -35.92% | 0.610 | KMLM-only stack |
| M2 DBMF no RSST | M/Static | 9.76% | -37.97% | 0.610 | DBMF-only MF source; 2000+ window only |
| M3 KMLM+DBMF blend | M/Static | 9.56% | -36.94% | 0.600 | split MF no RSST; 2000+ window only |
| SPY 1× | Benchmark | 11.37% | -55.20% | 0.523 | floor |

All rows except M2/M3 share the same ~38.3y window. M2/M3 contain DBMF directly and are shown for context only because DBMFSIM starts in 2000. Regime-gated LRS and G3 variants are omitted from this long-window static-stack table because their tax treatment differs and must include realization drag.

---

## What we learned (4 main findings)

### 1. Monthly rebal hurts SSO-based portfolios; capital-efficient stacks shrug it off

The biggest surprise was **Popular 50/25/25 SSO/GLD/ZROZ losing 10.71pp of MDD** when switching from yearly to monthly rebal (-39.84% → -50.55%). Why?

In bear markets:
- SSO 2× falls ~2× the SPY drawdown.
- **Monthly rebal forces re-buying SSO** every month at the new (lower) price to maintain 50% target weight.
- This **accelerates the bleed**: you keep adding to a falling position.
- Yearly rebal naturally "lets SSO die" through the year and only restores weight at year-end — accidentally protective.

**Capital-efficient stacks (NTSX/GDE/RSST) are virtually immune** because they don't have a single 2× LETF that's leveraging-against-trend on its own. Each stack contains multiple asset classes natively (NTSX = SPY + bonds; GDE = SPY + gold; RSST = SPY + managed futures); the internal balance is the diversification.

| portfolio | ΔMDD (Yearly → Monthly) |
|---|---:|
| Popular 50/25/25 SSO/GLD/ZROZ | **-10.71pp** |
| Aggressive (T1 gold-heavy) | -3.99pp |
| Bogleheads 67% NTSX (L2) | -3.83pp |
| Sleeping pills (L1 CEGB) | -3.16pp |
| Conservative (B4 ZROZ) | **-0.29pp** |
| Balanced (B2 high-equity) | -0.17pp |
| Gayed LRS variants (signal-driven) | ±0pp |

**Underwater chart** (peak-to-trough drawdown, long-window proxy `1987-12-30 → 2026-04-29`):

![Drawdown 1987-2026 long-window RSST proxy](testfolio_02_drawdown.png)
*SPY still hits roughly -55% in the GFC. L1/B4 keep drawdowns materially shallower, while B2/T1/B5 buy more CAGR by accepting deeper stress. The deepest drawdowns cluster around 2000-2002, 2008, and 2022; the 2022 joint stock/bond shock is where duration-heavy sleeves show their main weakness.*

**Implication**: if you're a real investor making monthly contributions (which most are), the popular 50/25/25 SSO mix is **strictly dominated** by every capital-efficient stack — both on Sharpe AND on realized MDD.

### 2. The TQQQ + 200d SMA regime-gate doesn't survive 1987-2026 (vs. cherry-picked 2012-2025)

Tested 6 variants (G3a-G3f) per Fun-Sundae4060 + no_simpsons specs:

| variant | bull | bear | CAGR | MDD | Sharpe |
|---|---|---|---:|---:|---:|
| G3a Fun-Sundae | TQQQ 34 / KMLM 33 / GLD 33 | QQQ 34 / KMLM 33 / GLD 33 | 15.60% | -58.53% | 0.661 |
| G3b NDX-heavy | TQQQ 50 / KMLM 25 / GLD 25 | QQQ 50 / KMLM 25 / GLD 25 | 18.34% | -75.98% | 0.621 |
| **G3c with bonds** ⭐ | TQQQ/KMLM/GLD/IEF 25/25/25/25 | QQQ/KMLM/GLD/IEF 25/25/25/25 | 13.36% | -42.63% | **0.703** |
| G3d minimal | TQQQ 50 / KMLM 50 | QQQ 50 / KMLM 50 | 18.58% | -75.47% | 0.629 |
| G3e Gayed-NDX | TQQQ 100 | IEF 100 | 18.61% | -90.05% | 0.535 |
| G3f pure swap | TQQQ 100 | QQQ 100 | **19.97%** | **-96.90%** | 0.556 |

**Best G3 = G3c (with bonds) with Sharpe 0.703, but with MDD -42.63%.** This is a different risk profile from B4's -28.94% MDD, and G3/LRS variants need separate after-tax treatment because they realize gains through regime flips.

The community-cited "~10,000% return on TQQQ + 200d SMA" comes from Bogleheads/Petrou backtests over **2012-2025** — a cherry-picked window without a dotcom-equivalent crash. On 1987-2026 (which includes 2000-2002):
- TQQQ standalone buy-hold MDD: -99.98% (you lost ~99% of capital in 2002).
- G3f pure swap (TQQQ → QQQ regime-gate): MDD -96.90%. Gate saved only **3pp** of drawdown.
- G3e Gayed-NDX (TQQQ → IEF): MDD -90.05%. Gate saved **10pp** because bonds are uncorrelated to equity in bear.
- Gayed canonical SSO (SPY 2× → IEF): MDD -43.48%. Works well because SPX vol is much lower than NDX vol.

**Lesson**: regime-gate works only if the bear sleeve is **uncorrelated** to the bull sleeve. Pure equity-on-equity swap (G3f) gives basically no cushion. NDX-leveraged is too volatile for the SMA gate to handle gracefully — by the time the 200d signal fires, you've already taken a 25-35% hit, and whipsaws around the boundary compound it.

### 3. US-bias accounts for only ~4% of B4's Sharpe edge — structural diversification is the real driver

Tested 5 G4 variants per Grouchy_Release_2321 + perky_python:

| variant | allocation | CAGR | MDD | Sharpe |
|---|---|---:|---:|---:|
| **G4c mixed US/Intl** ⭐ | 12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ | 13.31% | -32.65% | **0.716** |
| G4a NTSD swap | 25 NTSD / 25 GDE / 25 RSST / 25 ZROZ | 13.29% | -36.24% | 0.684 |
| **G4d 4-sleeve global** ⭐ | 25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM | **10.54%** | **-22.56%** | 0.678 |
| G4b RSSB-heavy | 50 RSSB / 25 GDE / 25 KMLM | 10.59% | -34.35% | 0.610 |
| G4e full Intl | 50 NTSD / 25 GDE / 25 KMLM | 11.57% | -48.52% | 0.555 |

Two findings here:

(a) **G4c (50/50 US/Intl split) got Sharpe 0.716 in the long-window table** — only 0.029 below B4's Sharpe of 0.745. Read this as directional rather than final because RSSB/NTSD synthetic histories add uncertainty, but the structural diversification (capital-efficient stacking via NTSX/GDE/RSST embedding leverage across asset classes) still appears to be the dominant driver.

(b) **G4d (RSSB-based 4-sleeve) breaks the MDD record at -22.56%** — the lowest of any portfolio in the entire study. Calmar ratio 0.467 (also a record). Trade-off: CAGR 10.54% (below SPY's 11.37%). For a CAGR-flexible investor with strong MDD aversion, G4d is a new top-tier candidate.

**Caveat**: RSSB only has ~2 years of live data (launched Jan 2024). RSSBSIM extends back to 1987 via simulation. Take G4d with extra skepticism until 5+ years of live track record.

### 4. Walk-forward weight optimization — drift is real but doesn't translate to better OOS performance (G8 PASS)

Per laurenthu's critique: re-fit max-Sharpe weights on rolling 5y windows; if optimal weights drift wildly, the structural edge is window-specific.

**Step 1 — drift magnitude** (rolling 5y max-Sharpe, scipy SLSQP, ~400 windows per universe):

| universe | NTSX range | GDE range | RSST range | ZROZ/TMF range | Max drift vs static |
|---|---|---|---|---|---|
| B4 | 0-87pp | 0-86pp | 0-100pp | ZROZ 0-75pp | **75pp** |
| B2 | 0-92pp | 0-86pp | 0-100pp | TMF 0-59pp | 70pp |
| T1 | 0-92pp | 0-86pp | 0-100pp | TMF 0-59pp | 75pp |

Optimal weights pick **corner solutions** (0% or 100% in many windows). On the surface, this looks bad — laurenthu's prediction is right.

**Step 2 — what realized OOS performance does this drift produce?**

| universe | CAGR static | CAGR walk-fwd | MDD static | MDD walk-fwd | Sharpe static | Sharpe walk-fwd | ΔSharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| B4 | 11.47% | 11.92% | -26.53% | -27.96% | **0.940** | 0.879 | **-0.061** |
| B2 | 11.86% | 12.22% | -31.75% | -34.37% | **0.886** | 0.824 | **-0.062** |
| T1 | 11.86% | 12.22% | -36.19% | -34.37% | **0.853** | 0.824 | **-0.029** |

(Note: these Sharpes use raw mean/vol, not the Rf-adjusted Sharpe testfol.io uses; the absolute values differ from earlier sections but the DELTA between static and walk-forward is fair.)

**Static beats walk-forward in all 3 universes** despite walk-forward picking up +0.36-0.45pp of CAGR. Walk-forward's gain in returns is more than eaten by the higher MDD it incurs.

**Why?** Three structural effects:
1. 5-year window is too short for stable covariance estimation — out-of-sample noise dominates.
2. Max-Sharpe optimization picks corner solutions (0%/100%), causing high turnover, which costs MDD.
3. Equal-weight (B4 25/25/25/25) is the **shrinkage estimator** — known optimum for n_assets ~ 4 with modest correlation (DeMiguel/Garlappi/Uppal 2009 RFS, *"Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?"*).

**G8 verdict: PASS. Static weights are not curve-fit.** Drift is real; curve-fit is not.

**Rolling CAGR consistency** (5y / 10y / 15y / 20y windows, named static contenders):

![Rolling CAGR grid](testfolio_04_rolling_grid.png)
*The CE stacks (B2/T1/B4/L1) maintain positive rolling CAGR across virtually all windows >=10y. SPY dips negative in rolling-10y around 2008-2010, while B4/L1 stay materially steadier. The static stacks aren't just better in aggregate — they're more **consistent** across overlapping windows, which is the practical definition of "non-curve-fit."*

---

## Why this works (the mechanism — unchanged from Post 1)

### Capital-efficient stacking removes the LETF decay tax

Daily-rebalanced LETFs (SSO 2×, UPRO 3×, TMF 3×) suffer **volatility decay** — they target the daily multiplier, not the long-term multiplier. In choppy markets (2022, 2000-2003), this can eat 5-10%/year of return.

Capital-efficient ETFs use **futures overlays** instead of daily-reset leverage:
- [**NTSX**](https://www.optimizedportfolio.com/ntsx/): 90% S&P 500 + 60% Treasury futures = 1.5× notional, no daily decay
- [**GDE**](https://www.wisdomtree.com/investments/etfs/capital-efficient/gde): 90% S&P 500 + 90% gold futures = 1.8× notional
- [**RSST**](https://www.optimizedportfolio.com/rsst/): 100% S&P 500 + 100% systematic managed futures = 2× notional

You get the leverage; you don't pay the daily-reset decay tax.

### Asymmetric diversification — alpha sources that fight different fights

- **2008 GFC**: bonds ✅ rallied, gold ✅ rallied, MF ✅ trend-followed shorts
- **2020 COVID flash**: bonds ✅, gold ✅, MF mixed (too fast)
- **2022 inflation**: gold ✅ flat, MF ✅ +20-30%, bonds ❌ catastrophic
- **2000-2003 dot-com**: value ✅, bonds ✅, gold ✅ slow

**No regime kills more than 2 of 4 simultaneously.**

---

## How I tested for overfit (the 7-gate battery + new G8)

| gate | what it tests | threshold |
|---|---|---|
| G1 PBO (CSCV) | Probability of backtest overfit | < 0.5 |
| G2 DSR | Deflated Sharpe with Bonferroni | p < 0.05 |
| G3 Walk-Forward | Rolling 8 windows, MDD < 25% per | 6+/8 windows |
| G4 OOS 70/30 | Train 70%, test 30% Sharpe > 0 | Sharpe > 0 |
| G5 FWD stress | Post-2020 OOS Sharpe > 0 | Sharpe > 0 |
| G6 Bootstrap CI | 99.9% CI low > 0 | CI low > 0 |
| G7 Cross-library | Same backtest in 2 libs ±3pp | ±3pp |
| **G8 Walk-forward weight drift** 🆕 | Re-fit max-Sharpe rolling 5y; static portfolio Sharpe ≥ walk-forward Sharpe | static ≥ WF |

Gates pass:
- ✅ G2 DSR: p < 0.001 across both datasets
- ✅ G4 OOS 70/30: stable post-2003
- ✅ G5 FWD: survived COVID + 2022 inflation
- ✅ G6 Bootstrap: CI low > 0
- ✅ G7 Cross-lib: ±3pp agreement testfol.io vs internal Python
- ✅ **G8 walk-forward**: static ≥ walk-forward on ALL universes (this Post 2 addition)
- ⚠️ G1 PBO: grid-level inflated 0.5-0.9 because configs are similar (Principle M from López de Prado AFML — PBO is grid-composition-dependent)
- ⚠️ G3 Walk-Forward 25% per-window: fails for any leveraged strategy in 2008/2022 stress — structural, not overfit

**Bottom line**: edge is real (G2/G4/G5/G6/G8 confirm), per-window stress is structural for leveraged exposure (G3 expected fail), grid noise means don't fine-tune weights (G1 warning).

---

## Honest caveats (updated)

1. **TMF (3× LTT) lost -71% in 2022 alone**. At 25% allocation = -17.7pp portfolio drag. Aggressive (B2) reduces to 10% (-7pp drag). Conservative (B4 ZROZ) replaces TMF entirely with zero-coupon Treasuries (-53% in 2022 at 25% = -13pp drag, but no LETF decay).

2. **NTSX/GDE/RSST are recent ETFs**. NTSX 2018, GDE 2022, RSST 2022. The main table and charts use synthetic proxies over 1987-2026, including `RSST = SPY + KMLM - cash`. Real ETFs have execution drag and tracking error not fully captured (see u/perky_python's critique addressed in this post).

3. **RSSB has only ~2 years of live data** (launched Jan 2024). G4d (which has the best MDD in the study) is partially synthetic. Take with extra skepticism.

4. **Bear markets in NDX-3× are catastrophic**. G3e/G3f confirm: the 200d SMA gate doesn't save you from -90% to -97% MDD on TQQQ-leveraged regime gates in 1987-2026. The "10,000% TQQQ" backtest claims you'll see online are over 2012-2025. Don't extrapolate.

5. **40-year backtest assumes regimes repeat**. 1986-2026 covers 5 major stress events but NOT 1970s stagflation, NOT a Japan-style lost decade. Different decade could differ.

6. **Behavioral risk is real**. A 30% drawdown over 18-24 months tests discipline. If you panic-sell at the bottom, you destroy the strategy.

7. **Pre-1987 data limitation**: backtest can't extend before KMLM SIM start. u/Fit-Librarian279 correctly pointed out that 1980-1982 was a tough drawdown for both gold and ZROZ (verified: gold -53% peak-to-trough, long-bonds bottomed 1981-82 with negative real returns through 1979). The Hurst/Ooi/Pedersen 2017 "Century of Evidence" extends MF data further back; backfilling is on the roadmap but won't be in this Post 2.

8. **ZROZ/GOVZ are duration bets, not guaranteed crisis hedges.** A commenter correctly flagged the forward-looking risk: deficits, rising term premia, sticky inflation, or central-bank reserve shifts could make long STRIPS fail to rally in a future equity crisis. I still prefer ZROZ/GOVZ over TMF because they avoid daily-reset decay and give more convexity than TLT, but this sleeve is not magic insurance.

9. **RSST proxy caveat**: the longer-window study uses `SPY + KMLM - cash` because KMLMSIM lets us start in 1987. A live tracking check suggests actual RSST is closer to `SPY + 70% DBMF + 30% KMLM - cash`; using that proxy cuts the common window to 2000+ and shifts B4 to roughly CAGR 11.00% / MDD -29.60% / Sharpe 0.671. I use the KMLM-only proxy here to gain 12+ years of regime history, not because it is a perfect RSST reconstruction.

---

## My pick — what I'd actually hold for the next 30 years (UPDATED)

**Post 1 had T1 gold-heavy as my pick. Post 2 update: switching to B4 Conservative, with L1 CEGB as the higher-Sharpe low-risk alternative.**

| candidate | CAGR | MDD | Sharpe | 30y verdict |
|---|---:|---:|---:|---|
| 🏆 **Conservative (B4 ZROZ)** | **13.31%** | -28.94% | **0.745** | **MY PICK**: best Sharpe in the long-window static sweep and the cleanest CAGR/MDD compromise. |
| 🔵 Sleeping pills (L1 CEGB) | 11.06% | **-25.43%** | 0.729 | Lowest stress. Give up 2.25pp CAGR vs B4. Pick this if drawdown tolerance is the binding constraint. |
| B2 TMF10 | 13.89% | -36.38% | 0.718 | Higher CAGR, much larger drawdown. |
| T1 gold-heavy | 13.34% | -34.65% | 0.688 | Was Post 1 pick; demoted because B4 has similar CAGR with materially lower MDD. |
| 🛡️ G4d (RSSB+GDE+ZROZ+KMLM) 🆕 | 10.54% | **-22.56%** | 0.678 | **Best MDD in entire study.** Lower CAGR (below SPY) is the trade-off. Consider as complement, not substitute, to B4. |

**Why B4 wins now:**

1. **Best balanced trade-off on the long-window study**: B4 adds +2.25pp CAGR over L1 while keeping MDD below 30%.
2. **ZROZ instead of TMF removes the LETF decay tax** — same duration role, no daily-reset decay. `GOVZ` is an operationally close substitute for `ZROZ` because both target long Treasury STRIPS / zero-coupon duration.
3. **Small CAGR/MDD penalty from monthly rebal** in the prior cadence test (B4 was much less sensitive than T1 or Popular 50/25/25).
4. **Survives G8 walk-forward gate**: static B4 25/25/25/25 beats rolling max-Sharpe optimization on the same universe. Equal-weight is the optimum shrinkage.
5. **Structural diversification holds geographically**: G4c (50/50 US/Intl swap) only lost modest Sharpe vs B4 in the prior G4 test. The edge isn't purely a US-equity-premium curve fit.

### Single-portfolio commitment for next 30y: 🟢 B4 Conservative

```
25% NTSX  (90% SPY  + 60% Treasury futures = 1.5x notional)
25% GDE   (90% SPY  + 90% Gold futures      = 1.8x notional)
25% RSST  (100% SPY + 100% Trend            = 2.0x notional)
25% ZROZ  (zero-coupon 25y Treasuries, no LETF decay; GOVZ is a close substitute)
=========
100% capital, ~163% notional exposure, ~74.5% equity beta
```

Monthly rebalance via contributions only (don't sell unless ±10pp drift). No regime gates, no signals to watch, no whipsaw cost. Boring buy-and-hold.

**Validate ZROZ/GOVZ availability at your broker.** `GOVZ` (iShares 25+ Year Treasury STRIPS Bond ETF) is a close operational substitute for `ZROZ` (PIMCO 25+ Year Zero Coupon U.S. Treasury Index ETF). In quick testfol.io checks their behavior was practically the same because both are long-duration STRIPS/zero-coupon Treasury exposure. If `ZROZ` is unavailable but `GOVZ` is available with acceptable spread/liquidity, I would use `GOVZ` before falling back to `TLT`. `TLT` is the second-line fallback because it changes the sleeve more: lower duration/convexity than STRIPS, even if still long Treasury exposure.

### Optional MDD-extreme tier: 🛡️ G4d (RSSB + GDE + ZROZ + KMLM)

```
25% RSSB  (100% global stocks + 100% global bonds via futures = 2.0x notional)
25% GDE
25% ZROZ
25% KMLM  (KFA MLM Index, rules-based managed futures)
```

CAGR 10.54% (below SPY's 11.37%) but MDD only -22.56% — lowest in the entire study. **Caveat**: RSSB has ~2y live track record. Use as complement, not core.

---

## Replicate (testfol.io)

Set rebalance "Monthly", invest_dividends=true. Apply ER drag per portfolio (sum of weighted ERs).

Long-window `RSST` expansion used in the main table:

```
RSST proxy = 100 SPYSIM + 100 KMLMSIM - 100 CASHX
B4 Conservative = 47.5 SPYSIM + 25 GDESIM + 25 KMLMSIM + 25 ZROZSIM + 15 IEFSIM - 37.5 CASHX  (drag 0.385%)
B2 TMF10        = 57 SPYSIM + 30 GDESIM + 30 KMLMSIM + 18 IEFSIM + 10 TLTSIM?L=3&E=1.05 - 45 CASHX  (drag 0.417%)
T1 gold-heavy   = 43 SPYSIM + 35 GDESIM + 25 KMLMSIM + 20 TLTSIM?L=3&E=1.05 + 12 IEFSIM - 35 CASHX  (drag 0.358%)
G4d MDD-extreme = 25 RSSBSIM + 25 GDESIM + 25 ZROZSIM + 25 KMLMSIM  (drag 0.490%)
```

The 70/30 DBMF/KMLM tracking-sensitivity version is:

```
RSST tracking proxy = 100 SPYSIM + 70 DBMFSIM + 30 KMLMSIM - 100 CASHX?E=-2
```

The capital-efficient SIMs (NTSX/GDE/RSST/RSSB/NTSD) decompose into base equity + leveraged sleeves via CASHX (the -X% leg models the implicit T-bill borrow funding the futures notional).

For LRS strategies, use the [testfol.io tactical builder](https://testfol.io/tactical):

```
Signal: SMA(SPYSIM, 200) < Price(SPYSIM)  tolerance: 2%
  IF TRUE:  100% SPYSIM?L=2 (SSO) or SPYSIM?L=3 (UPRO)
  IF FALSE: 100% IEFSIM
Rebal: Daily. Trading freq: Daily.
```

---

## What I want from this post

**Primary**: share the **methodology + community-driven feedback integration** so others can replicate. Post 1's data was good but Post 2 reflects 4 substantive corrections from the community.

**Secondary**: get more **honest critique**. Specifically:

- **Did I miss something in the G4 international tests?** I tested NTSD/RSSB/VT-base but didn't run NTSI (US+Intl combined stack) since NTSI isn't a SIM on testfol.io.
- **The G3 NDX regime-gate finding is uncomfortable.** TQQQ does very well on cherry-picked windows but breaks on full 1987-2026. Is there a version (with smarter signal, shorter MA, dual-signal like u/no_simpsons suggested) I should test?
- **If you posted a screenshot that beats B4, please share weights or a testfol.io link.** One LOWDDPORT screenshot looked excellent (roughly 12.7% CAGR / -26.6% MDD / 0.84 Sharpe), but without allocation details it isn't replicable.
- **G4d (RSSB+GDE+ZROZ+KMLM) is the new MDD record (-22.56%).** Anyone running this live? Does the synthetic backfill of RSSB pre-2024 trustworthy?
- **Is there a known issue with the "static beats walk-forward" finding in G8?** This is documented in DeMiguel et al. 2009 RFS for 1/N portfolios but I want to make sure nothing's wrong with my SLSQP implementation.

**What I would NOT find useful**: "just hold VTI bro" / "leverage is gambling" / "this won't work". I've heard those. Specific empirical critiques only.

Happy to share the spec JSONs, full per-config metrics tables, and the Python pipeline if anyone wants to replicate.

**Anyone holding something not in my expanded sweep that lands in the upper-right quadrant of the long-window Pareto frontier (CAGR > B4 13.31% AND |MaxDD| < B4 28.94%)? Or something with MDD < G4d 22.56% AND CAGR > G4d 10.54%?**
