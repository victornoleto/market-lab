# Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)

## Metadata

- **Authors:** Carlo Zarattini, Andrew Aziz, Andrea Barbon
- **Year:** 2024 (published May 10, 2024)
- **Venue:** SSRN working paper (abstract_id=4824172); also Swiss Finance Institute Research Paper N°24-97
- **Source URL (primary):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172
- **Alt URL (Alexandria):** https://www.alexandria.unisg.ch/entities/publication/71ef0a23-34e3-4b37-a8d7-d98285579662
- **Slug:** `paper.zarattini_2024_intraday_spy`
- **Topic:** T3 — Short-hold intraday momentum
- **Raw access:** N/A — no local raw; extraction based on abstract + secondary review
- **Citation format:** `[paper.zarattini_2024_intraday_spy, §results]`

## Core thesis

Intraday momentum in SPY can be exploited by initiating trend-following positions the moment price breaks out of **noise boundaries** defined as `open_price × (1 ± avg_absolute_intraday_return_last_14d)`. Unlike prior academic literature focused on the final 30 minutes (Gao-Han-Li-Zhou 2013), entries can trigger throughout the session when an abnormal demand/supply imbalance appears.

## Methodology snapshot

- **Asset:** SPY (S&P 500 ETF), intraday minute data
- **Period:** 2007 → early 2024 (~17 years)
- **Signal:** price touching either `open_t × (1 + boundary)` (long) or `open_t × (1 − boundary)` (short), where `boundary = mean absolute intraday return up to that minute, last 14 trading days`
- **Exit:** dynamic trailing stop; flat at close (overnight flat)
- **Cost model:** **$0.0035/share commission + $0.001/share slippage** (explicit)
- **Tests:** volatility-regime conditioning, dealer gamma imbalance, day-of-week effects, benchmarking vs canonical technical daily patterns

## Key results

- **Total return 1,985% net-of-costs** over 2007 → early 2024
- **Annualized return 19.6%**
- **Sharpe Ratio 1.33 (net)**
- Outperforms buy-and-hold materially with ~zero beta (−0.042 in a parallel opening-range-breakout framing)
- Statistical tests support robustness to volatility regimes

## Applicability to market-lab

- **HIGHEST relevance of the Phase 3.7-1 sprint.** This is the **lead candidate for Phase 3.7-3 hunt (hypothesis H1)**.
- **Pepperstone-universe fit: EXCELLENT** — SPX500 CFD has spread ~0.4-0.6 pts, zero commission on Razor standard, intraday-only design avoids swap overnight, retail tier-1 leverage 20:1 supports sizing.
- Single-asset (SPY) — does not violate mandate §3.1 if signal validated in QQQ/DIA/IWM as cross-asset confirmation.
- **Gap to close in Phase 3.7-3:** explicit CSCV/PBO and Deflated Sharpe Ratio validation — paper reports Sharpe 1.33 but no PBO/DSR in public abstract.

## Related knowledge-base entries

- `paper.maroy_2024_intraday_improvements` — direct extension with VWAP/Ladder exit strategies (reports Sharpe > 3 but high PBO risk).
- `paper.zirk_sadowski_2025_intraday_overnight` — complementary evidence that intraday anomalies exist at 45–60 min horizons in small-caps.
- `books/machine_trading.md` (Chan) — prior-art intraday mean-reversion baseline.
