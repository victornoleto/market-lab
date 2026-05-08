# Iter 045 — RSST proxy 70/30 DBMF/KMLM rebaseline

**Date:** 2026-05-02
**Source:** testfol.io API
**Change vs iter 044:** `RSST = SPY + 70% DBMF + 30% KMLM - CASHX?E=-2` instead of `SPY + KMLM - CASHX`.

Because DBMFSIM starts in 2000, this run forces all portfolios onto the same common 2000-01-03 -> 2026-05-01 window. This is the apples-to-apples comparison for the corrected RSST proxy.

## Ranking By Sharpe

**Tax model:** no DARF applied. These are static buy-and-hold/lazy-rebal scenarios; tax is reserved for swing/tactical strategies that realize gains through position changes.

| # | strategy | window | CAGR (no tax) | MDD | Sharpe | Calmar |
|---:|---|---|---:|---:|---:|---:|
| 1 | L1_cegb_proxy | 2000-01-03 -> 2026-05-01 (26.32y) | 9.66% | -25.43% | 0.696 | 0.380 |
| 2 | B4_zroz_instead_of_tmf | 2000-01-03 -> 2026-05-01 (26.32y) | 11.00% | -29.60% | 0.671 | 0.372 |
| 3 | L2_bogleheads_67ntsx | 2000-01-03 -> 2026-05-01 (26.32y) | 8.97% | -26.30% | 0.653 | 0.341 |
| 4 | B3_tlt_instead_of_tmf | 2000-01-03 -> 2026-05-01 (26.32y) | 10.34% | -32.68% | 0.646 | 0.316 |
| 5 | T1_gold_heavy | 2000-01-03 -> 2026-05-01 (26.32y) | 11.65% | -35.80% | 0.643 | 0.325 |
| 6 | B2_tmf10_balanced | 2000-01-03 -> 2026-05-01 (26.32y) | 11.59% | -37.91% | 0.631 | 0.306 |
| 7 | T2_equity_heavy | 2000-01-03 -> 2026-05-01 (26.32y) | 11.08% | -34.46% | 0.627 | 0.321 |
| 8 | M2_dbmf_no_rsst | 2000-01-03 -> 2026-05-01 (26.32y) | 9.77% | -37.97% | 0.611 | 0.257 |
| 9 | M4_rsst_kmlm_blend | 2000-01-03 -> 2026-05-01 (26.32y) | 10.07% | -38.32% | 0.602 | 0.263 |
| 10 | M3_kmlm_dbmf_blend | 2000-01-03 -> 2026-05-01 (26.32y) | 9.56% | -36.94% | 0.601 | 0.259 |
| 11 | B1_user_baseline_25tmf | 2000-01-03 -> 2026-05-01 (26.32y) | 10.75% | -40.82% | 0.600 | 0.263 |
| 12 | B5_no_duration | 2000-01-03 -> 2026-05-01 (26.32y) | 12.00% | -44.56% | 0.599 | 0.269 |
| 13 | M1_kmlm_no_rsst | 2000-01-03 -> 2026-05-01 (26.32y) | 9.33% | -35.92% | 0.583 | 0.260 |
| 14 | T3_rssb_global | 2000-01-03 -> 2026-05-01 (26.32y) | 10.39% | -43.34% | 0.569 | 0.240 |
| 15 | spy_1x | 2000-01-03 -> 2026-05-01 (26.32y) | 8.06% | -55.26% | 0.400 | 0.146 |

## Beats SPY On CAGR And MDD

SPY benchmark: CAGR 8.06% / MDD -55.26%.

- L1_cegb_proxy: CAGR 9.66%, MDD -25.43%, Sharpe 0.696
- B4_zroz_instead_of_tmf: CAGR 11.00%, MDD -29.60%, Sharpe 0.671
- L2_bogleheads_67ntsx: CAGR 8.97%, MDD -26.30%, Sharpe 0.653
- B3_tlt_instead_of_tmf: CAGR 10.34%, MDD -32.68%, Sharpe 0.646
- T1_gold_heavy: CAGR 11.65%, MDD -35.80%, Sharpe 0.643
- B2_tmf10_balanced: CAGR 11.59%, MDD -37.91%, Sharpe 0.631
- T2_equity_heavy: CAGR 11.08%, MDD -34.46%, Sharpe 0.627
- M2_dbmf_no_rsst: CAGR 9.77%, MDD -37.97%, Sharpe 0.611
- M4_rsst_kmlm_blend: CAGR 10.07%, MDD -38.32%, Sharpe 0.602
- M3_kmlm_dbmf_blend: CAGR 9.56%, MDD -36.94%, Sharpe 0.601
- B1_user_baseline_25tmf: CAGR 10.75%, MDD -40.82%, Sharpe 0.600
- B5_no_duration: CAGR 12.00%, MDD -44.56%, Sharpe 0.599
- M1_kmlm_no_rsst: CAGR 9.33%, MDD -35.92%, Sharpe 0.583
- T3_rssb_global: CAGR 10.39%, MDD -43.34%, Sharpe 0.569

## Methodology Note

This run corrects the RSST proxy based on a live ETF tracking check, not on a new parameter search. The proxy follows return-stacking logic `[risk_parity, ch.5, p.10]` and uses diversified managed-futures engines `[ilmanen_expected_returns, ch.19]`.
