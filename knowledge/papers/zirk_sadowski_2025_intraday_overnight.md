# Intraday and Overnight Return Anomalies: Evidence from 11.6 Million Price Observations

## Metadata

- **Authors:** Jan Zirk-Sadowski, Aneta Hryckiewicz
- **Year:** 2025
- **Venue:** Finance Research Letters, v86 Part D, December 2025
- **Source URL (primary):** https://www.sciencedirect.com/science/article/abs/pii/S1544612325018926
- **Slug:** `paper.zirk_sadowski_2025_intraday_overnight`
- **Topic:** T3 — Intraday/overnight anomaly evidence (NYSE small-cap)
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch
- **Citation format:** `[paper.zirk_sadowski_2025_intraday_overnight, §findings]`

## Core thesis

Within NYSE small-cap equities, market efficiency is **horizon-dependent**. Very short horizons (30s–5 min) are efficient. **Horizons 45–60 min exhibit persistent anomalies that explain up to 63% of return variation**. Specific effects documented: "11 AM" anomaly Tue-Thu and "reversed Monday" at 10 AM.

## Methodology snapshot

- **Dataset:** 11.6–12 million intraday price observations, NYSE small-cap stocks
- **Period:** September–November 2022
- **Horizons analyzed:** 30 seconds to 60 minutes
- **Statistical approach:** bootstrapped ANOVA; no explicit cost model
- **Not a trading-strategy paper** — focus is statistical identification of the anomalies

## Key results

- 45–60 min horizons explain up to **63% of return variation** in tested universe
- "11 AM effect" (Tue-Thu) and "reversed Monday 10 AM effect" statistically significant
- No Sharpe / CAGR / cost-adjusted returns — not a tradable-strategy paper

## Applicability to ai-trade

- **LOW direct relevance.** Small-cap NYSE is NOT in Pepperstone CFD universe; short Sep-Nov 2022 window is narrow; minute data at small-cap granularity not efficiently served by Tiingo.
- **Indirect value:** confirms that mid-horizon intraday inefficiency exists in liquid-ish markets — complementary to Zarattini 2024 evidence on SPY-level liquid ETF.
- Not a Phase 3.7-3 lead on its own. Archive for supporting context only.

## Related knowledge-base entries

- `paper.zarattini_2024_intraday_spy` — primary intraday-signal source, targeting liquid ETF where Zirk-Sadowski effects would be weaker.
- `paper.glasserman_2024_overnight_news` — companion evidence on overnight returns.
