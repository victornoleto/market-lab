# VIX Constant Maturity Futures Trading Strategy: A Walk-Forward Machine Learning Study

## Metadata

- **Authors:** Sangyuan Wang, Keran Li, Yaling Liu, Yijun Chen, Xianbo Tang
- **Year:** 2024
- **Venue:** PLoS One, v19(4), article e0302289
- **Source URL (primary):** https://pmc.ncbi.nlm.nih.gov/articles/PMC11029606/
- **Alt URL (PDF):** https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0302289
- **Code:** https://github.com/smangj/vix_option
- **Slug:** `paper.wang_2024_vix_cmf_ml`
- **Topic:** T2 — VIX term-structure / ML forecasting
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch of PMC page
- **Citation format:** `[paper.wang_2024_vix_cmf_ml, §walk_forward]`

## Core thesis

VIX **term-structure features** (roll yield, price changes) combined with seven ML models can forecast next-day returns on VIX constant-maturity futures (CMF). A novel **Constrained Mean-Variance Portfolio Optimization (C-MVO)** strategy integrating these predictions outperforms a benchmark long-short approach.

## Methodology snapshot

- **Assets:** 6 VIX CMFs, maturities 1–6 months (SPVXSP through SPVIX6ME)
- **Period:** 4,022 daily observations, December 20, 2005 – August 7, 2022
- **ML models:** LSTM, GRU, ALSTM (attention-based LSTM), XGBoost, LightGBM, Linear Regression, MLP
- **Key features:** constant-maturity prices, roll yield, price changes, roll yield changes + macro (SPY, TLT, VIX)
- **Walk-forward validation:** train Dec-2005 → Jun-2010, validate Jul-2010 → Dec-2010, test Jan-2011 → Aug-2022 with **expanding windows (no look-ahead)**
- **Cost model:** frictionless — NOT applicable for retail CFD mandate as-is

## Key results

- **Mean Information Coefficient 0.037 across seven models**; best performer Linear Regression at IC = 0.114
- **Four models exceeded IC > 0.02 threshold**
- C-MVO average IR = 0.623 (vs long-short benchmark 0.404)
- **Best config (LR C-MVO): IR 2.291, average annualized return 5.1%**
- Models incorporating both `μt` (price change) and `ΔRoll` (roll-yield change) beat simple-feature alternatives

## Applicability to ai-trade

- **MEDIUM relevance.** Frictionless cost model is a hard limiter for direct Pepperstone transport.
- **Feature-level insight usable as regime filter:** roll-yield sign (contango vs backwardation) can feed into SPX500 CFD entry logic without needing to trade VIX futures directly.
- Pepperstone-universe fit: **not direct** (no VIX futures CFD). VIX data feed required via Bloomberg / Cboe / third-party.

## Related knowledge-base entries

- `paper.bozovic_2024_vix_managed` — companion VIX regime paper, complementary (scaling vs prediction).
- `paper.hsieh_2025_letf_compounding` — theoretical autocorrelation/regime framing.
