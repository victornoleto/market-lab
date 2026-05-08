# VIX-Managed Portfolios

## Metadata

- **Author:** Miloš Božović
- **Year:** 2024
- **Venue:** International Review of Financial Analysis (IRFA), v95 Part A, October 2024
- **Source URL (primary):** https://www.sciencedirect.com/science/article/abs/pii/S1057521924002850
- **Slug:** `paper.bozovic_2024_vix_managed`
- **Topic:** T2 — VIX term-structure / regime filter
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch
- **Citation format:** `[paper.bozovic_2024_vix_managed, §methodology]`

## Core thesis

**Scale portfolio exposure inversely to the cumulative previous-month VIX** — take less risk when the implied-vol index is elevated, more risk when it is subdued. The approach delivers superior Sharpe improvements relative to realized-volatility scaling **once transaction costs are accounted for**, because VIX-managed portfolios require the **least rebalancing** among tested strategies.

## Methodology snapshot

- **Data:** 8,431 daily VIX observations, January 2, 1990 – April 30, 2023
- **Test assets:** 10 equity factors (MKT, SMB, HML, etc.) + 6 mean-variance efficient portfolio classes + 176 anomaly portfolios
- **Cost model:** explicitly evaluates performance under realistic transaction costs — compares weight stability between VIX-based and realized-vol-based scaling
- **OOS:** addressed via dynamic scaling (look-ahead free); significant alphas reported in spanning regressions

## Key results

- Without frictions, VIX strategies display better raw performance but **only marginal Sharpe advantage** vs. realized-vol scaling
- **With transaction costs, the advantage becomes substantial** — VIX scaling wins on net Sharpe because it reduces turnover
- Specific Sharpe/CAGR/drawdown figures not in the public abstract; alpha significance is the reported metric

## Applicability to market-lab

- **HIGH relevance.** This is the science paper behind Phase 3.7-3 hypothesis H2 (VIX-gated LETF rotation).
- Can **substitute or augment the 200-day SMA filter** in Gayed 2016 — regime gate becomes `scale = L × clip(VIX_baseline / VIX_prior_month, 0, 1)`.
- Pepperstone-universe fit: high — VIX is observable (free via Cboe/FRED), does NOT need to be tradable. Underlying SPX500 / NAS100 CFDs give retail 20:1 leverage.
- **Gap:** no paper 2022+ combines VIX-scaling + LETF 2x/3x + retail CFD cost model honestly. Phase 3.7-3 can contribute.

## Related knowledge-base entries

- `books/leverage_for_the_long_run.md` (Gayed) — predecessor SMA-based regime filter, candidate for replacement/augmentation.
- `paper.wang_2024_vix_cmf_ml` — companion paper focused on VIX term-structure ML prediction rather than portfolio scaling.
- `paper.hsieh_2025_letf_compounding` — theoretical framing for why regime filters outperform static leverage.
