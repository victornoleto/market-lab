# AI-Trade — Knowledge Base Audit (22 + 9 = 31 books)

## 1. Thematic Coverage Map

| Area | Books that cover it | Depth |
|---|---|---|
| **Financial ML / feature engineering / validation (CPCV, purging)** | #1 López de Prado (AFML) ★★★, #2 López de Prado (ML Asset Mgrs) ★★, #3 Jansen (ML Algo Trading) ★★★ | **Excellent** — AFML is the definitive reference for triple barrier, meta-labeling, purged k-fold, CPCV. Jansen complements with end-to-end pipelines in Python. |
| **DSP / cycle analysis / filters** | #12 Ehlers (Cybernetic Analysis) ★★★, #14 Ehlers (Cycle Analytics) ★★★, #15 Ehlers (Rocket Science) ★★★ | **Excellent** — three Ehlers books = full coverage of MESA, adaptive filters, Hilbert Transform, DSP indicators. |
| **Money management / position sizing / Kelly** | #16 Vince (Math of Money Mgmt) ★★★, #17 Vince (Leverage Space) ★★★ | **Very good** — Vince is the canonical reference for optimal-f, generalized Kelly, drawdown control. |
| **Trend following / momentum / rotation** | #7 Carver (Systematic Trading) ★★, #8 Clenow (Trading Evolved) ★★★, #9 Clenow (Stocks on the Move) ★★★, #20 Universal Trend Tactics ★ | **Very good** — Clenow covers trend following with code, Carver adds a portfolio framework. |
| **Evidence-based / statistical testing / overfit control** | #4 Aronson (Evidence-Based TA) ★★★, #5 Masters (Stat. Sound Indicators) ★★, #6 Masters (Testing & Tuning) ★★★ | **Very good** — Aronson is the gold standard in bootstrap, White's Reality Check, data-mining bias. Masters complements with practical permutation testing. |
| **Generic trading systems / encyclopedia** | #10 Kaufman (Trading Systems & Methods) ★★★, #11 Bulkowski (patterns) ★★ | **Good** — Kaufman is the most complete encyclopedia on the market. Bulkowski is the reference on chart patterns with statistics. |
| **Regime detection / HMM / change-point** | #18 Regime Change ★★, #19 Peterson (Trading on Sentiment) ★ | **Partial** — #18 covers the topic directly, but lacks academic rigor in HMM / Bayesian switching. |
| **Behavioral / sentiment / alternative data** | #19 Peterson (Trading on Sentiment) ★★ | **Basic** — Peterson covers sentiment scoring, but does not go deep into modern NLP, alt-data pipelines, or satellite / web-scraping. |
| **Math / DSP / numerical methods (support)** | #21 Brunton/Kutz (Data-Driven Science) ★★★, #22 Numerical Recipes ★★★ | **Excellent as support** — DMD, SVD, Sparse Sensing (Brunton) + full numerical reference (NR). |
| **Cybernetic trading (classical neural nets)** | #13 Ruggiero (Cybernetic Trading) ★ | **Dated** — focuses on 1990s neural networks, useful mainly as historical context. |
| **Market microstructure / execution / slippage** | — | **❌ MISSING** → ✅ Harris (draft) |
| **Options / volatility surface / Greeks** | — | **❌ MISSING** → ✅ Sinclair |
| **Risk parity / formal portfolio construction** | Carver (#7) touches on it superficially | **⚠️ WEAK** → ✅ Qian |
| **Financial time-series econometrics (GARCH, cointegration, state-space)** | — | **❌ MISSING** → ✅ Tsay 3e + Hamilton |
| **Walk-forward analysis / rigorous backtesting** | Masters (#6) covers partially, AFML (#1) brings CPCV | **⚠️ PARTIAL** → ✅ Pardo |
| **Mean reversion / pairs / stat-arb** | — | **❌ MISSING** → ✅ Chan (Algo Trading) |
| **Volatility modeling (realized, implied, GARCH)** | — | **❌ MISSING** → ✅ Tsay 3e + Sinclair |

---

## 2. Critical Gaps Identified

### 🔴 MUST-HAVE gaps (directly impact system robustness)

**L1 — Market microstructure and execution**
Without understanding order flow, bid-ask dynamics and transaction costs, any backtest is illusory. Especially critical on FX via MT5/XM where spread and slippage are real.

**L2 — Financial time-series econometrics**
GARCH, EGARCH, formal cointegration (Johansen), state-space models, Kalman filter applied to finance are missing. These are the building blocks for modelling volatility and detecting regimes in a statistically rigorous way.

**L3 — Walk-forward analysis and formal backtesting**
Masters (#6) and AFML (#1) cover pieces, but the full treatment is missing: walk-forward optimization, Monte Carlo validation, robustness profiling. Pardo is the canonical framework.

**L4 — Mean reversion / pairs trading / stat-arb**
The library is strong in trend/momentum but has no book dedicated to mean reversion. Chan (Algorithmic Trading) is the practical reference with code.

### 🟡 NICE-TO-HAVE gaps (expand the arsenal)

**L5 — Volatility trading / options**
Even without trading options directly, understanding the volatility surface, variance premium and vol forecasting is essential for regime detection and risk management.

**L6 — Formal portfolio construction / risk parity**
Carver (#7) is good as a practical framework, but the quantitative foundation is missing: mean-variance, Black-Litterman, risk parity, López de Prado's hierarchical risk parity (HRP).

**L7 — Forex-specific microstructure**
Most books are equity-centric. For FX via MT5, understanding liquidity provision, quote-driven markets and carry/momentum in currencies has its own nuances.

---

## 3. Prioritized Recommendation List (9 titles acquired)

### 🏆 #1 — MUST-HAVE

**Ernest P. Chan — *Algorithmic Trading: Winning Strategies and Their Rationale***
- **Year/Ed:** 2013, Wiley, 1st edition
- **Gap:** L4 (mean reversion / stat-arb) + complements L3 (practical backtesting)
- **Why canonical:** Chan is one of the most cited practitioners on QuantStackExchange and quant blogs. Covers mean reversion (ADF, Hurst, cointegration, Kalman filter), momentum, and practical Kelly with MATLAB/Python code that adapts easily. Extensively cited by López de Prado and Jansen.
- **Level:** Intermediate
- **Overlap:** Some with Jansen (#3) on general concepts, but Chan is much deeper specifically on stat-arb and pairs trading. Worth it.
- **Link:** [Amazon](https://www.amazon.com/Algorithmic-Trading-Winning-Strategies-Rationale/dp/1118460146)

---

### 🏆 #2 — MUST-HAVE

**Ruey S. Tsay — *Analysis of Financial Time Series*, 3rd edition**
- **Year/Ed:** 2010, Wiley, 3rd edition
- **Gap:** L2 (time-series econometrics — GARCH, cointegration, state-space, VaR)
- **Why canonical:** Tsay is a professor at Chicago Booth, Fellow of ASA and IMS. The book is the standard textbook in master's/PhD programs in quantitative finance. Covers GARCH/EGARCH, stochastic volatility, multivariate models, MCMC, Kalman filter — all with real data and R code.
- **Level:** Intermediate-advanced (requires a statistics background)
- **Overlap:** Almost none — the books you have do not cover formal financial econometrics. Brunton/Kutz (#21) is DSP/dynamics, not econometrics.
- **Link:** [Wiley](https://www.wiley.com/en-us/Analysis+of+Financial+Time+Series,+3rd+Edition-p-9780470414354) · [Amazon](https://www.amazon.com/Analysis-Financial-Time-Ruey-Tsay/dp/0470414359)

---

### 🏆 #3 — MUST-HAVE

**Robert Pardo — *The Evaluation and Optimization of Trading Strategies*, 2nd edition**
- **Year/Ed:** 2008, Wiley
- **Gap:** L3 (walk-forward analysis, robustness profiling, overfit detection)
- **Why canonical:** Pardo literally coined the term "Walk-Forward Analysis". The 1st edition (1992, *Design, Testing, and Optimization of Trading Systems*) is a landmark in the field. Perry Kaufman (author of your #10) wrote the endorsement. Goldman Sachs and Daiwa are consulting clients of Pardo. Widely cited on forums like Elite Trader and Wilmott.
- **Level:** Intermediate
- **Overlap:** Complements Masters (#6) which focuses on permutation testing. Pardo focuses on walk-forward optimization and profiling — different pieces of the anti-overfit puzzle.
- **Link:** [Amazon](https://www.amazon.com/Evaluation-Optimization-Trading-Strategies/dp/0470128011) · [Wiley](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119196969)

---

### 🏆 #4 — MUST-HAVE

**Larry Harris — *Trading and Exchanges: Market Microstructure for Practitioners***
- **Year/Ed:** 2003, Oxford University Press
- **File:** `trading-and-exchanges-market-microstructure-for-practitioners` (2,551 KB) — ⚠️ pre-publication draft version (Mar 2002). Substantive content identical to the final edition; the published edition was not found as a text PDF.
- **Gap:** L1 (market microstructure, execution, transaction costs)
- **Why canonical:** Harris was Chief Economist of the SEC and holds the Fred V. Keenan chair at USC. The *Journal of Investment Management* considers the book indispensable. It is the standard microstructure textbook in MBA/MFE programs. Covers order types, bid-ask spread economics, market maker behavior, transaction cost analysis — everything you need to model realistic slippage in MT5.
- **Level:** Intermediate (written in accessible prose, little heavy math)
- **Overlap:** Zero with your current library. None of the 22 books covers microstructure.
- **Link:** [Oxford UP](https://global.oup.com/academic/product/trading-and-exchanges-9780195144703) · [Amazon](https://www.amazon.com/Trading-Exchanges-Market-Microstructure-Practitioners/dp/0195144708)

---

### 🥈 #5 — HIGHLY RECOMMENDED

**Ernest P. Chan — *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*, 2nd edition**
- **Year/Ed:** 2021, Wiley, 2nd edition
- **Gap:** Complements L4 + L6 (end-to-end trading frameworks, regime-aware optimization, factor models)
- **Why canonical:** The 2nd edition (2021) includes updated material on applied ML, regime shifts, and capital allocation — more modern than the 2009 1st edition. Widely recommended on QuantStart as the first book for retail quant.
- **Level:** Intro-intermediate
- **Overlap:** Some with Chan #1 above and Jansen (#3). The 2nd edition brings regime change and ML that justify the acquisition even if you own #1.
- **Link:** [Amazon](https://www.amazon.com/Quantitative-Trading-Build-Algorithmic-Business/dp/1119800064)

---

### 🥈 #6 — HIGHLY RECOMMENDED

**Euan Sinclair — *Volatility Trading*, 2nd edition**
- **Year/Ed:** 2013, Wiley, 2nd edition
- **Gap:** L5 (volatility modeling, variance premium, vol forecasting)
- **Why canonical:** Sinclair has a PhD in physics (Bristol) and 15+ years as a professional options trader at Bluefin Trading. The book is considered the most practical treatment of volatility trading available, praised by Jesper Andreasen (Danske Markets) and Steve Crutchfield (NYSE Euronext). Covers realized vs implied vol, Kelly sizing for options, and vol surface dynamics.
- **Level:** Intermediate
- **Overlap:** Complements Vince (#16/#17) on sizing, but the volatility focus is completely new to your library.
- **Link:** [Wiley](https://www.wiley.com/en-us/Volatility+Trading,+++Website,+2nd+Edition-p-9781118416723) · [Amazon](https://www.amazon.com/Volatility-Trading-Website-Euan-Sinclair/dp/1118347137)

---

### ~~#7 — REMOVED~~

**Barry Johnson — *Algorithmic Trading and DMA: An Introduction to Direct Market Access Trading Strategies***
- **Status:** ❌ **NOT ACQUIRED** — the only PDF found was an image scan (non-OCR), unusable for knowledge-base ingestion without a heavy OCR pipeline.
- **Year/Ed:** 2010, 4Myeloma Press
- **Gap:** L1 + L7 (execution algorithms, DMA, market impact modeling)
- **Decision:** Skipped. Harris (#4) already covers the conceptual foundation of microstructure. Specific topics on execution algorithms (VWAP, TWAP, implementation shortfall) are less critical for FX swing trading via MT5 than they would be for equities in institutional DMA. If needed in the future, it can be complemented with standalone papers from SSRN.

---

### 🥉 #8 — NICE-TO-HAVE

**Marcos López de Prado — papers on HRP (Hierarchical Risk Parity)**
- **Concrete alternative title:** Edward Qian — *Risk Parity Fundamentals*
- **Year/Ed:** 2016, CRC Press
- **Gap:** L6 (formal portfolio construction / risk parity)
- **Why canonical:** Qian is Managing Director at PanAgora Asset Management and the name most associated with the risk-parity concept in the industry. The book formalizes risk budgeting, equal risk contribution, and portfolio construction without depending on expected return estimates.
- **Level:** Intermediate-advanced
- **Overlap:** Carver (#7) touches on the topic pragmatically, but Qian is the formal mathematical treatment.
- **Link:** [Amazon](https://www.amazon.com/Risk-Parity-Fundamentals-Edward-Qian/dp/1498738796)

---

### 🥉 #9 — NICE-TO-HAVE

**Stefan Jansen — consider complementing with Hamilton — *Time Series Analysis***
- **Title:** James D. Hamilton — *Time Series Analysis*
- **Year/Ed:** 1994, Princeton University Press
- **Gap:** L2 complementary (HMM, state-space, regime switching — Hamilton's chapter 22 is *the* reference for Markov switching models)
- **Why canonical:** Hamilton is the creator of the Markov-Switching model (Hamilton, 1989), the seminal paper on econometric regime detection. The book has 800+ pages and is the most cited textbook in time-series econometrics (17,000+ citations on Google Scholar).
- **Level:** Advanced (math-heavy)
- **Overlap:** Complements Tsay (#2 above) — Tsay is more applied/finance, Hamilton is more theoretical/econometric. If you have to pick one, Tsay is more practical for trading.
- **Link:** [Princeton UP](https://press.princeton.edu/books/hardcover/9780691042893/time-series-analysis) · [Amazon](https://www.amazon.com/Time-Analysis-James-Douglas-Hamilton/dp/0691042896)

---

### 🥉 #10 — NICE-TO-HAVE

**Ernest P. Chan — *Machine Trading: Deploying Computer Algorithms to Conquer the Markets***
- **Year/Ed:** 2017, Wiley
- **Gap:** Complements L3 + L4 (automated execution, factor models, intraday momentum, ML applied to regime detection)
- **Why canonical:** Third book in Chan's trilogy, focuses on real deployment: automation, factor models, and mean reversion/momentum with ML. Less cited than the first two, but brings practical topics like Bayesian optimization of parameters and risk indicators.
- **Level:** Intermediate
- **Overlap:** Significant with Chan #1 and #2 above — if you already bought the first two, this one is incremental.
- **Link:** [Amazon](https://www.amazon.com/Machine-Trading-Deploying-Computer-Algorithms/dp/1119219604)

---

## 4. Priority Visual Summary

| # | Book | File | Gap | Status |
|---|---|---|---|---|
| 🏆 1 | Chan — *Algorithmic Trading* | `Algorithmic Trading - Winning Strategies and Their Rationale 2013` (9.0 MB) | Mean reversion / stat-arb | ✅ |
| 🏆 2 | Tsay — *Analysis of Financial Time Series* 3e | `Analysis of Financial Time Series Third Edition By Ruey S.Tsay` (7.2 MB) | GARCH / econometrics / vol | ✅ |
| 🏆 3 | Pardo — *Evaluation & Optimization* | `the-evaluation-and-optimization-of-trading-strategies` (3.3 MB) | Walk-forward / anti-overfit | ✅ |
| 🏆 4 | Harris — *Trading and Exchanges* | `trading-and-exchanges-market-microstructure-for-practitioners` (2.5 MB) | Microstructure / slippage | ✅ (draft) |
| 🥈 5 | Chan — *Quantitative Trading* 2e | `Quantitative Trading How to Build Your Own Algorithmic Trading Business` (3.6 MB) | End-to-end framework | ✅ |
| 🥈 6 | Sinclair — *Volatility Trading* | `Volatility Trading, + Website-Wiley (2013)` (3.3 MB) | Vol modeling / options | ✅ |
| ~~7~~ | ~~Johnson — *Algo Trading & DMA*~~ | — | ~~Execution algorithms~~ | ❌ Removed |
| 🥉 8 | Qian — *Risk Parity Fundamentals* | `Risk_Parity_Fundamentals` (6.2 MB) | Portfolio construction | ✅ |
| 🥉 9 | Hamilton — *Time Series Analysis* | `Hamilton Time Series Analysis` (13.3 MB) | HMM / regime switching | ✅ |
| 🥉 10 | Chan — *Machine Trading* | `Machine Trading_ Deploying Computer Algorithms to Conquer The Markets (Ernest Chan 2017)` (1.4 MB) | Deployment / practical ML | ✅ |

---

## 5. Note on Reading Strategy

Given the project's 7-layer anti-overfit framework, the suggested absorption order is:

1. **First: Chan (Algorithmic Trading)** — opens the mean-reversion arsenal the library lacks, with practical code you can use immediately
2. **Second: Pardo** — closes the walk-forward gap before you start coding backtests in Phase 1
3. **Third: Harris** — calibrates transaction cost and slippage assumptions on MT5/XM before any simulation is trustworthy
4. **Fourth: Tsay** — econometrically grounds the volatility and regime models that will feed the strategies

Books 5-10 can be absorbed in parallel as the need arises during development.

---

## 6. Acquisition Notes

- **9 of 10 books acquired** as text PDFs (direct knowledge-base ingestion)
- **1 removed** (Johnson — *Algo Trading & DMA*): the only available PDF was an image scan, unusable without OCR. The execution-algorithms gap is secondary for FX swing trading and can be covered with standalone papers if needed.
- **Harris** acquired as the draft version (Mar 2002), content equivalent to the published edition (Oxford, 2003). Citations must reference the published edition.
- **Final knowledge base total: 22 original + 9 new = 31 books**

---

## 7. Data Sources for Backtest (FX via MT5)

### Core principle

Bad data invalidates any backtest, regardless of framework sophistication. For FX, the problem is compounded by the fact that it is a decentralized market — no "official price" exists, each dealer has its own feed, and the "volume" reported in MT5 is broker tick volume, not real interbank volume.

### Data source tiers

**Tier 1 — MT5/XM (free, already available)**

MetaTrader5 itself provides historical data via `copy_rates_from` in the Python API. Advantage: reflects exactly the spreads and conditions of the broker where trades will be executed. Disadvantages: limited historical depth (typically 2-5 years depending on timeframe), dealer data (not interbank), and tick volume does not represent real volume. For swing trading at 1H/4H/Daily, it is acceptable as a starting point — but not as the sole source.

**Tier 2 — Free sources of reasonable quality**

| Source | Data | History | Notes |
|---|---|---|---|
| **Dukascopy** (JForex) | Tick + 1min | 2003+ | Considered superior to FXCM by the quant community. Good quality. |
| **Histdata.com** | Tick + 1min | 2000+ | Most-used free source among retail quants. FXCM/Gain Capital feed (dealer bias). |
| **OANDA API** | Candlestick (REST) | Variable | Clean, well-documented API. Reasonable history. |
| **TrueFX** | Interbank tick | Variable | Real interbank data for older history (free); real-time is paid. |

**Tier 3 — Paid / institutional sources**

Refinitiv (ex-Thomson Reuters), Bloomberg, TickData. Institutional quality, but cost incompatible with $1,000 capital. Overkill for the project's Phase 0/1.

### Recommended strategy: two-layer validation

1. **Strategy development and validation:** use Dukascopy or Histdata data — greater historical depth, more data for cross-validation and walk-forward (Pardo).
2. **Final pre-live validation:** run the backtest on the MT5/XM data itself — reflects the real conditions of the broker where execution will happen, including spreads, gaps and quirks.

This two-source approach works as a **robustness check**: if the strategy works on Dukascopy data but not on XM data (or vice versa), it is a signal of fragility and dependence on the specific feed.

### Critical caveats (grounded in the knowledge base)

| Caveat | Reference book | Concept |
|---|---|---|
| Data pre-processing and stationarity | Tsay (*Analysis of Financial Time Series*) | Unit-root tests, differencing, transformations |
| Train/validation/test window structure | Pardo (*Evaluation & Optimization*) | Walk-forward analysis, robustness profiling |
| Slippage and transaction cost assumptions | Harris (*Trading and Exchanges*) | Bid-ask spread economics, market maker behavior |
| Purging and embargo in temporal cross-validation | López de Prado (*AFML*, #1) | Purged k-fold, CPCV, leakage prevention |
| Carry costs (overnight swap) | Chan (*Algorithmic Trading*) | Financing cost impact on holding periods |

### Inviolable rule

**Never trust a single data source, and always include realistic transaction costs (spread + swap + slippage) in the backtest. A backtest without costs is fiction.**
