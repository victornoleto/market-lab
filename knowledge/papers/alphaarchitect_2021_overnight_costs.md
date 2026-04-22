# Trading Costs Wipe Out the Overnight Return Anomaly

## Metadata

- **Publisher:** Alpha Architect (Larry Swedroe / Jack Vogel contributor, practitioner-rigorous blog)
- **Year:** 2021
- **Venue:** Alpha Architect research blog (not peer-reviewed; transparent methodology)
- **Source URL (primary):** https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/
- **Slug:** `paper.alphaarchitect_2021_overnight_costs`
- **Topic:** T9 — Overnight anomaly (cost destruction)
- **Raw access:** N/A — extraction based on WebSearch summary
- **Citation format:** `[paper.alphaarchitect_2021_overnight_costs, §cost_analysis]`

## Core thesis

The overnight anomaly in SPY **does not survive realistic retail transaction costs** once bid-ask spreads and commission are properly modeled. Statistical robustness is also weak: overnight > intraday only 53% of days despite large cumulative-return differential.

## Methodology snapshot

- **Asset:** SPY (SPDR S&P 500 ETF)
- **Period:** January 1993 → January 2020 (≈ 27 years, 6,800 trading days)
- **Strategy modeled:** buy at close, sell at open (overnight long)
- **Cost model:** 25+ years of bid-ask spread reconstruction + commission $0.01/share (realistic retail 2021)
- **Caveat:** overnight strategies can use single-price auction at open/close to avoid spread — but other frictions remain

## Key results

- Gross cumulative: overnight 717%, buy-hold 627%, intraday 12% (Jan-1993 → Jan-2020)
- **Net of costs: edge disappears** at retail scale
- Only 53% of days have `overnight return > intraday return` — weak statistical persistence
- Research argues "anomaly is more random walk than repeatable strategy"

## Applicability to ai-trade

- **HIGH relevance as anti-pattern reference.** Definitively disqualifies overnight-only trade of SPY (and by extension SPX500 CFD) as a retail Pepperstone strategy.
- Reinforces Glasserman 2024 academic finding.
- Can be used as supporting citation for Phase 3.7-3 decision to **exclude overnight anomaly as a standalone Tier 1 lead**.

## Related knowledge-base entries

- `paper.glasserman_2024_overnight_news` — peer-adjacent academic companion.
- `paper.zarattini_2024_intraday_spy` — shows where retail intraday edge DOES exist (when paired with cost-aware design).
