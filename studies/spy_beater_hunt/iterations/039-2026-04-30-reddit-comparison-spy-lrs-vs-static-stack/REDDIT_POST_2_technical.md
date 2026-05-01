# [Deep dive v2] 14-config static stack sweep + Post 1 community feedback integrated — 4 follow-up tests + 7-gate anti-overfit framework

**TL;DR**: Follow-up to my [Post 1](https://www.reddit.com/r/LETFs/comments/1t0i3qm/) where I shared 4 boring static portfolios that beat SPY on **both** CAGR and Max DD over 1987-2026. The 4 candidates are simple buy-and-hold stacks built on capital-efficient ETFs — **NTSX** (90% SPY + 60% Treasury futures), **GDE** (90% SPY + 90% gold futures), **RSST** (100% SPY + 100% systematic managed futures) — plus a duration sleeve (TMF / ZROZ / TLT). No signals, no regime gates, no rebal whipsaw.

**This Post 2 is the methodology + the community-critique integration.** After Post 1 went up, you gave me 4 specific empirical critiques. I ran each one as a separate iteration:

- **u/perky_python** — "your sim ignores rebal cadence + ERs" → **monthly rebal + explicit ERs across all configs**
- **u/Fun-Sundae4060 + u/no_simpsons** — "TQQQ + 200d SMA gives ~10,000%" → **6 G3 regime-gate variants tested**
- **u/Grouchy_Release_2321 + u/perky_python** — "SPY-base is US-survivorship-bias" → **5 G4 international variants (NTSD / RSSB / VT)**
- **u/laurenthu** — "re-fit weights on rolling 5y windows" → **walk-forward max-Sharpe G8 gate**

Plus the full **7-gate anti-overfit battery** (PBO / DSR / Walk-Forward / OOS 70-30 / FWD stress / Bootstrap CI / Cross-library) + the new **G8 weight-drift gate**. Full data, full methodology, what changed, what survived, what didn't.

**Headline change from Post 1**: top-level rebalance is now **monthly** (not yearly) and **expense ratios are explicit**. This shifts the Pareto frontier in interesting ways — most notably, **Popular 50/25/25 SSO/GLD/ZROZ loses 10.71pp of MDD** (-39.84% → -50.55%) when you rebalance monthly. The capital-efficient stacks (NTSX/GDE/RSST) are virtually immune.

**Headline finding**: B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ) survived all 4 adversarial tests and replaces T1 as my pick. G4d (RSSB-based) breaks the MDD record at -22.56% — lowest in the entire study.

---

## What changed since Post 1 (4 community-driven follow-ups)

| Critic | Critique | Test | Verdict |
|---|---|---|---|
| u/perky_python | "Your sim ignores rebal cadence + ERs. Real CAGR is ~1pp lower." | **Re-ran with Monthly rebal + explicit ERs (NTSX 0.20%, GDE 0.20%, RSST 0.99%, KMLM 0.92%, GLD 0.40%, ZROZ 0.15%, etc).** | ⚠️ Partial. CAGR drops 0.5-0.9pp on stacks (less than 1pp). MDD on Popular 50/25/25 worsens **-10.71pp** (huge finding). |
| u/Fun-Sundae4060 + u/no_simpsons | "Try TQQQ/QQQ regime-gate × diversifiers above/below 200d SMA. ~10,000% return." | **Tested 6 G3 variants** (Fun-Sundae spec, NDX-heavy, with bonds, minimal, Gayed-NDX, pure TQQQ/QQQ swap). | ❌ None beat B4 Conservative. The "~10,000%" return is computed over 2012-2025 (cherry-picked window without dotcom). On 1987-2026 with 2000-2002 included, the regime gate fails badly. |
| u/Grouchy_Release_2321 + u/perky_python | "SPY-only base is US-survivorship-bias. Try VT/RSSB/NTSI." | **Tested 5 G4 variants** with NTSD, RSSB, mixed US/International. | ⚠️ US-bias accounts for **only ~4% of B4's Sharpe edge**. Best international variant (G4c with 50/50 US/Intl split) gets Sharpe 0.716 vs B4 0.745. **G4d (RSSB-based) breaks the MDD record at -22.56%** — the lowest in the entire study. |
| u/laurenthu | "Re-fit weights on rolling 5y windows. If they drift, edge is window-specific." | **Walk-forward max-Sharpe optimization on B4/B2/T1 universes.** | ✅ G8 PASS. Weights drift wildly (60-75pp range) BUT static portfolio Sharpe **beats** walk-forward in all 3 universes. Static = optimal shrinkage estimator (DeMiguel/Garlappi/Uppal 2009 RFS). |

**Overall**: B4 Conservative survives all 4 adversarial tests. Becomes the new "My pick" (replacing T1 from Post 1 — see Recommendation section).

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

## Updated results — Monthly rebal + ERs + terminal DARF (1987-12-31 → 2026-04-30, 38.33y)

**Tax model**: I assume the realistic deployment behavior — monthly contributions to whatever's most underweight (lazy rebal via aportes), **never selling during accumulation**. Therefore realized gains intra-year = 0 → DARF = 0 each year. DARF only applies at terminal liquidation (15% × cumulative profit). Formula: `net_final = 0.85 × gross_final + 0.15 × initial`.

This is the canonical methodology used across **all** numbers in this post (no more dual-table inconsistency).

### Main contenders (Pareto frontier)

| portfolio | gross CAGR | **net CAGR** | Max DD | Sharpe | Sortino | $100k → 30y (net) |
|---|---:|---:|---:|---:|---:|---:|
| SPY 1× buy-hold | 11.37% | **10.91%** | -55.20% | 0.523 | 0.740 | $2.3M |
| Popular 50/25/25 SSO/GLD/ZROZ | 12.58% | 12.11% | **-50.55%** ⚠️ | 0.576 | 0.818 | $3.0M |
| 🔵 **Sleeping pills (L1 CEGB)** | 11.06% | 10.60% | **-25.43%** | 0.729 | 1.044 | $2.0M |
| ⚪ Bogleheads 67% NTSX (L2) | 11.06% | 10.60% | -26.30% | 0.722 | 1.037 | $2.0M |
| 🟢 **Conservative (B4 ZROZ)** ⭐ | **13.31%** | **12.84%** | -28.94% | **0.745** | 1.071 | $3.7M |
| 🟠 **Balanced (T1 gold-heavy)** | 13.34% | 12.87% | -34.65% | 0.688 | 0.984 | $3.8M |
| 🔴 **Aggressive (B2 high-equity)** | 13.89% | 13.42% | -36.38% | 0.717 | 1.028 | $4.4M |
| Gayed LRS 2× (SSO 200d) ‡ | 16.01% | ~14.0% ‡ | -43.48% | 0.609 | 0.843 | ~$5.5M (after annual realize) |
| Gayed LRS 3× (UPRO 200d) ‡ | 19.61% | ~17.0% ‡ | -57.57% | 0.595 | 0.822 | ~$11M (after annual realize) |

‡ Gayed LRS strategies flip regimes 1-3×/year, forcing realized gains → annual DARF (~1.5-2pp drag). Net ranking penalty larger than buy-hold static stacks. Estimates based on iter 038 internal pipeline net classification.

**Equity curves** ($10k start, log scale, 1987-12-31 → 2026-04-30):

![Equity curves 1987-2026](testfolio_01_equity.png)
*Visual ranking by terminal value. Plot uses Post 1's testfol.io snapshot (yearly rebal, no ERs) — Post 2's monthly+ERs shifts the absolute terminal values down ~0.5pp CAGR but the structural ordering is preserved. Conservative (B4) and Aggressive (B2) lead the named profiles; the Sleeping pills (L1) curve runs nearly identical to Bogleheads 67% NTSX (L2). Gayed LRS 3× UPRO has the highest terminal but ate -57% drawdowns to get there.*

**Pareto frontier — CAGR vs Max DD** (the "interesting zone" is the upper-right quadrant, where CAGR > SPY AND |MaxDD| < SPY):

![Pareto CAGR vs MaxDD](testfolio_03_scatter.png)
*Green region = beats SPY on both axes. Red region = worse on both. The 4 named CE-stack profiles (B2/T1/B4/L1) all sit in the green quadrant, comfortably north-east of SPY. Popular 50/25/25 sits very close to the SPY MDD line on yearly basis but **crosses into the red on monthly rebal** (-50.55% MDD per Post 2 tables). Gayed LRS 2x/3x are in the lower-right (better CAGR, worse MDD) — they trade drawdown for return.*

**Key changes vs Post 1** (now using consistent Monthly + ERs + terminal DARF):
- B4 Sharpe: 0.798 → **0.745** (-0.053). Still highest among the 4 candidates.
- T1 Sharpe: 0.744 → **0.688** (-0.056). T1's TMF 20% × monthly rebal magnifies duration drawdowns.
- B2 Sharpe: 0.772 → **0.717** (-0.055). Still high but B4 widens its lead.
- Popular 50/25/25 MDD: -39.84% → **-50.55%** ⚠️. Broke much harder than expected.

### Updated full sweep — 14 iter 038 configs + G3/G4 variants (consistent Monthly + ERs + terminal DARF)

| config | family | gross CAGR | **net CAGR** | Max DD | Sharpe | Notes |
|---|---|---:|---:|---:|---:|---|
| **Conservative (B4 ZROZ)** | B/Static | 13.31% | **12.84%** | -28.94% | **0.745** ⭐ | canonical winner |
| B3 TLT instead of TMF | B/Static | 12.44% | 11.98% | -30.06% | 0.735 | TLT 1× backup if ZROZ unavailable |
| Sleeping pills (L1 CEGB) | L/Static | 11.06% | 10.60% | -25.43% | 0.729 | low-risk reference |
| Bogleheads 67 NTSX (L2) | L/Static | 11.06% | 10.60% | -26.30% | 0.722 | low-risk reference |
| **Balanced (B2 TMF10)** | B/Static | 13.89% | 13.42% | -36.38% | 0.717 | high-CAGR alternative |
| **G4c (mixed US/Intl 50/50)** 🆕 | G4/Static | 13.31% | 12.84% | -32.65% | 0.716 | best international |
| T2 equity-heavy | B/Static | 13.40% | 12.93% | -33.14% | 0.708 | NTSX 35% |
| G3c (with bonds) 🆕 | G3/RegimeGate | 13.36% | 12.89% | -42.63% | 0.703 | best G3, still loses to B4 |
| **Aggressive (T1 gold-heavy)** | B/Static | 13.34% | 12.87% | -34.65% | 0.688 | demoted from Post 1 |
| B5 no duration | B/Static | **14.22%** | **13.74%** | -41.12% | 0.687 | high CAGR, high MDD |
| G4a (NTSD swap) 🆕 | G4/Static | 13.29% | 12.82% | -36.24% | 0.684 | full swap US→Intl |
| **G4d (RSSB+GDE+ZROZ+KMLM)** 🆕 | G4/Static | 10.54% | 10.10% | **-22.56%** ⭐ | 0.678 | **best MDD/Calmar in entire study** |
| B1 user baseline 25 TMF | B/Static | 12.93% | 12.46% | -38.78% | 0.665 | original spec — TMF 25% costs MDD |
| G3a (Fun-Sundae 33/33/33) 🆕 | G3/RegimeGate | 15.60% | 15.05% | -58.53% | 0.661 | TQQQ × KMLM × GLD |
| M4 RSST+KMLM blend | M/Static | 11.85% | 11.38% | -37.27% | 0.645 | dual MF source |
| G3d (TQQQ/KMLM 50/50) 🆕 | G3/RegimeGate | 18.58% | 17.86% | -75.47% | 0.629 | minimal |
| T3 RSSB global | B/Static | 12.31% | 11.85% | -41.39% | 0.623 | global stack, MDD inflado |
| G3b (NDX-heavy 50/25/25) 🆕 | G3/RegimeGate | 18.34% | 17.63% | -75.98% | 0.621 | high CAGR, brutal MDD |
| G4b (RSSB-heavy) 🆕 | G4/Static | 10.59% | 10.15% | -34.35% | 0.610 | RSSB ER drag |
| M2 DBMF no RSST ⚠ | M/Static | 9.76% | 9.15% | -37.97% | 0.610 | 26y window only (DBMFSIM start 2000) |
| M1 KMLM no RSST | M/Static | 10.74% | 10.29% | -35.92% | 0.610 | KMLM-only stack |
| Gayed LRS 2× | LRS | 16.01% | ~14.0%‡ | -43.48% | 0.609 | annual realize → tax drag |
| M3 KMLM+DBMF blend ⚠ | M/Static | 9.56% | 8.95% | -36.94% | 0.600 | 26y window only |
| Gayed LRS 3× | LRS | 19.61% | ~17.0%‡ | -57.57% | 0.595 | extreme LRS |
| Popular 50/25/25 SSO/GLD/ZROZ | Reference | 12.58% | 12.11% | -50.55% | 0.576 | hurt by monthly rebal |
| **G3f (pure TQQQ/QQQ swap)** 🆕 | G3/RegimeGate | **19.97%** | 19.18% | **-96.90%** ⚠️ | 0.556 | highest CAGR, worst MDD |
| G4e (full Intl) 🆕 | G4/Static | 11.57% | 11.11% | -48.52% | 0.555 | no US, no duration — bad combo |
| G3e (Gayed-NDX 100/IEF) 🆕 | G3/RegimeGate | 18.61% | 17.88% | -90.05% | 0.535 | NDX analog of canonical Gayed |
| SPY 1× | Benchmark | 11.37% | **10.91%** | -55.20% | 0.523 | floor |

⚠ M2 / M3 = janela 26y (DBMFSIM start 2000) — não comparáveis em CAGR absoluto. ‡ LRS net CAGR estimado considerando ~1.5-2pp/yr drag de annual realization (regime flips force realized gains).

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

**Underwater chart** (peak-to-trough drawdown, all portfolios, 1987-2026):

![Drawdown 1987-2026](testfolio_02_drawdown.png)
*Notice how SSO 2× / UPRO 3× buy-hold (not in chart but referenced) and the Gayed LRS 3× UPRO punch through -50%. SPY hits -55% in 2008. The CE stacks (B2/T1/B4/L1) all stay above -36% even in the worst stress. Popular 50/25/25 looks similar at the yearly basis but the monthly rebal pushes it to -50.55% — about as bad as SPY. The deepest drawdowns cluster in 2000-2002 (dotcom) and 2008 (GFC); 2022 (joint stock+bond crash) shows up as a smaller but ugly synchronized dip.*

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

**Best G3 = G3c (with bonds) with Sharpe 0.703 — still 0.042 below B4's 0.745.**

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

(a) **G4c (50/50 US/Intl split) gets Sharpe 0.716** — only 0.029 below B4's 0.745. **US-equity premium contributes ~4% of the edge**, not 50%+. The structural diversification (capital-efficient stacking via NTSX/GDE/RSST embedding leverage across asset classes) is the dominant driver.

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

**Rolling CAGR consistency** (5y / 10y / 15y / 20y windows, all portfolios):

![Rolling CAGR grid](testfolio_04_rolling_grid.png)
*The CE stacks (B2/T1/B4/L1) maintain positive rolling CAGR across virtually all windows ≥10y — even the worst rolling-10y for B4 stays around +5%. SPY dips negative in rolling-10y around 2008-2010. Gayed LRS strategies show wild rolling-5y swings (high variance from regime flips). The static stacks aren't just optimal in aggregate — they're more **consistent** across overlapping windows, which is the practical definition of "non-curve-fit."*

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

2. **NTSX/GDE/RSST are recent ETFs**. NTSX 2018, GDE 2022, RSST 2022. The 38-year backtest uses synthetic proxies. Real ETFs have execution drag and tracking error not fully captured (see u/perky_python's critique addressed in this post).

3. **RSSB has only ~2 years of live data** (launched Jan 2024). G4d (which has the best MDD in the study) is partially synthetic. Take with extra skepticism.

4. **Bear markets in NDX-3× are catastrophic**. G3e/G3f confirm: the 200d SMA gate doesn't save you from -90% to -97% MDD on TQQQ-leveraged regime gates in 1987-2026. The "10,000% TQQQ" backtest claims you'll see online are over 2012-2025. Don't extrapolate.

5. **40-year backtest assumes regimes repeat**. 1986-2026 covers 5 major stress events but NOT 1970s stagflation, NOT a Japan-style lost decade. Different decade could differ.

6. **Behavioral risk is real**. A 30% drawdown over 18-24 months tests discipline. If you panic-sell at the bottom, you destroy the strategy.

7. **Pre-1987 data limitation**: backtest can't extend before KMLM SIM start. u/Fit-Librarian279 correctly pointed out that 1980-1982 was a tough drawdown for both gold and ZROZ (verified: gold -53% peak-to-trough, long-bonds bottomed 1981-82 with negative real returns through 1979). The Hurst/Ooi/Pedersen 2017 "Century of Evidence" extends MF data further back; backfilling is on the roadmap but won't be in this Post 2.

---

## My pick — what I'd actually hold for the next 30 years (UPDATED)

**Post 1 had T1 gold-heavy as my pick. Post 2 update: switching to B4 Conservative.**

| candidate | CAGR | MDD | Sharpe | 30y verdict |
|---|---:|---:|---:|---|
| 🏆 **Conservative (B4 ZROZ)** | **13.31%** | -28.94% | **0.745** | **NEW PICK**: Highest Sharpe in study. ZROZ removes LETF decay. Survived all 4 community critiques: monthly+ERs (-0.05 Sharpe vs Post 1), G8 walk-forward (static beats WF), G3 NDX regime-gate (none beat B4), G4 international (only 4% of edge from US-bias). |
| Aggressive (B2 high-equity) | 13.89% | -36.38% | 0.717 | Highest CAGR static. -36% MDD over 18-24 months is brutal. 84% net equity = SPY-correlated downside. |
| Balanced (T1 gold-heavy) | 13.34% | -34.65% | 0.688 | Was Post 1 pick; lost relatively to Monthly+ERs. T1's TMF 20% × monthly rebal magnified duration drawdowns. |
| 🛡️ G4d (RSSB+GDE+ZROZ+KMLM) 🆕 | 10.54% | **-22.56%** | 0.678 | **Best MDD in entire study.** Lower CAGR (below SPY) is the trade-off. Consider as complement, not substitute, to B4. |
| Sleeping pills (L1 CEGB) | 11.06% | -25.43% | 0.729 | Lowest risk. Give up 2.25pp CAGR vs B4 — over 30y that's $4.5M vs $2.4M on $100k. Only worth it if you're genuinely fragile. |

**Why B4 wins now:**

1. **Highest Sharpe in the study (0.745)** even after 4 adversarial tests.
2. **ZROZ instead of TMF removes the LETF decay tax** — same notional duration exposure, no daily-reset decay.
3. **Smallest CAGR/MDD penalty from monthly rebal** (ΔMDD only -0.29pp; T1 went -3.99pp). Monthly cadence is the *real* deployment cadence for retail aporters.
4. **Survives G8 walk-forward gate**: static B4 25/25/25/25 has Sharpe 0.940 vs walk-forward 0.879 on the same universe. Equal-weight is the optimum shrinkage.
5. **Structural diversification holds geographically**: G4c (50/50 US/Intl swap) only loses 0.029 Sharpe vs B4. The edge isn't a US-equity-premium curve fit.

### Single-portfolio commitment for next 30y: 🟢 B4 Conservative

```
25% NTSX  (90% SPY  + 60% Treasury futures = 1.5x notional)
25% GDE   (90% SPY  + 90% Gold futures      = 1.8x notional)
25% RSST  (100% SPY + 100% Trend            = 2.0x notional)
25% ZROZ  (zero-coupon 25y Treasuries, no LETF decay)
=========
100% capital, ~163% notional exposure, ~74.5% equity beta
```

Monthly rebalance via contributions only (don't sell unless ±10pp drift). No regime gates, no signals to watch, no whipsaw cost. Boring buy-and-hold.

**Validate ZROZ availability at your broker.** It's less common than TLT. If unavailable, fallback to B3 (TLT 1×) — slight CAGR drop but similar MDD profile.

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

```
B4 Conservative:    47.5 SPYSIM, 25 GDESIM, 25 KMLMSIM, 25 ZROZSIM, 15 IEFSIM, -37.5 CASHX  (drag 0.385%)
B2 Aggressive:      57 SPYSIM, 30 GDESIM, 30 KMLMSIM, 18 IEFSIM, 10 TLTSIM?L=3&E=1.05, -45 CASHX  (drag 0.417%)
T1 Balanced:        43 SPYSIM, 35 GDESIM, 25 KMLMSIM, 20 TLTSIM?L=3&E=1.05, 12 IEFSIM, -35 CASHX  (drag 0.358%)
G4d MDD-extreme:    25 RSSBSIM, 25 GDESIM, 25 ZROZSIM, 25 KMLMSIM  (drag 0.490%)
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
- **G4d (RSSB+GDE+ZROZ+KMLM) is the new MDD record (-22.56%).** Anyone running this live? Does the synthetic backfill of RSSB pre-2024 trustworthy?
- **Is there a known issue with the "static beats walk-forward" finding in G8?** This is documented in DeMiguel et al. 2009 RFS for 1/N portfolios but I want to make sure nothing's wrong with my SLSQP implementation.

**What I would NOT find useful**: "just hold VTI bro" / "leverage is gambling" / "this won't work". I've heard those. Specific empirical critiques only.

Happy to share the spec JSONs, full per-config metrics tables, and the Python pipeline if anyone wants to replicate.

**Anyone holding something not in my expanded sweep that lands in the upper-right quadrant of the Pareto frontier (CAGR > B4 13.31% AND |MaxDD| < B4 28.94%)? Or something with MDD < G4d 22.56% AND CAGR > G4d 10.54%?**
