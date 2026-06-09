# Return-Stacked Core Robustness Execution Report

Status: research-only robustness execution. This report does not authorize deployment, paper trading, or mandate change. The goal is to stress the RSC-US and RSC-Global variants after the publication-draft work.

Method references: start-date sensitivity, rolling-window checks, parameter/implementation stress and sequence-risk tests are used as robustness diagnostics rather than promotion gates `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. Stacked ETF leverage and risk-parity interpretation follow `[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`.

## Source Data And Scope

Analysis: This report is built from saved portfolio equity curves and Monte Carlo summaries, so the displayed tables are reproducible from the RSC artifacts without re-running the original portfolio search. The trade-off is that sleeve-level attribution is limited where only final equity curves are available.

Conclusion: Use this report as an audit and communication layer over the existing RSC outputs. Do not infer exact rebalance-frequency, sleeve-removal or threshold-band behavior from these portfolio-level curves alone.

| Item | Detail |
|---|---|
| US full curves | `us_core/series/full_equity_curves.csv` |
| US implementation curves | `us_core/series/implementation_equity_curves.csv` |
| Global selected curves | `global_variant/series/global_selected_equity.csv` |
| Monte Carlo summaries | `us_core/monte_carlo_sequence_risk.csv`, `global_variant/global_monte_carlo_sequence_risk.csv` |
| CSV audit tables | `robustness_tables/` |
| Adjusted RSC-US sleeve matrix | `us_core/series/return_stacked_core_sleeve_returns.parquet` |

Executed analyses: start-date sensitivity, rolling relative wealth/CAGR spread, relative-underperformance episodes, fee/drag stress, named-regime stress and Monte Carlo sequence-risk summaries. Global sections are benchmarked against both `66/34 VTI/VEA` and `100% VT`.

Partially executed exactly after 2026-06-09: the RSC-US core sleeves now exist locally for `GDESIM`, adjusted `RSSTSIM`, and `ZROZSIM`. Exact CTAP/RSSX/global remove-one and threshold-band checks still require broader sleeve matrices. The large historical tables below remain based on saved portfolio curves unless explicitly labeled as the adjusted sleeve-matrix rerun.

## Adjusted RSST Tracking Proxy Addendum

The current local RSC-US core rerun uses `RSSTSIM = SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`, equivalent to the user-provided Testfol.io payload `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`. Because `DBMFSIM` starts in 2000, this addendum is a 2000+ comparison, not a replacement for the saved 1988 curve `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.

| Portfolio | Window | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal | Terminal/SPY |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RSC-US `35/40/25` adjusted RSST proxy | 2000-01-04..2026-05-21 | 12.40% | -30.76% | 0.838 | 1.153 | 0.403 | 21.71x | 2.60x |
| SPYSIM buy-hold | 2000-01-04..2026-05-21 | 8.39% | -55.14% | 0.514 | 0.653 | 0.152 | 8.34x | 1.00x |

Reading: the adjusted RSST proxy lowers the headline CAGR versus the older saved RSC curve, but the core still beats SPYSIM materially on terminal wealth, drawdown and risk-adjusted metrics in the common 2000-2026 window.

## Executive Read

- US `35/40/25` remains the clean anchor: strong full-history edge versus SPY, and post-2010 results are closer to SPY on CAGR but materially better on drawdown.
- Implementation variants with `CTAP`/`RSSX` improve post-2010 terminal wealth in the existing proxy table, but the RSSX rows remain BTC-assumption-sensitive and should stay optional.
- Global variants improve drawdown versus `66/34 VTI/VEA` and `VT`, but they give up return versus RSC-US. Treat global as a diversification variant, not a replacement.
- Extra drag stress is important: the strategy survives moderate incremental drag, but high extra drag compresses the edge, especially for global variants.
- Sequence-risk Monte Carlo supports the same qualitative conclusion: RSC variants show better downside terminal wealth than benchmarks, but this is not a formal validation gate.

## US 35/40/25 Start-Date Sensitivity

Analysis: The no-margin `35/40/25` core is clearly stronger than the original B4 over the full sample and across most start dates. The important caveat is that the post-2010 edge versus SPY is much narrower, including one 2013 start where CAGR trails SPY by `0.44pp`, while drawdown remains materially better.

Conclusion: Keep `35/40/25` as the clean US anchor, but present it as a drawdown-efficient SPY challenger rather than a guaranteed CAGR beater in every modern start window.

| Start | Years | Portfolio | CAGR | Bench CAGR | Spread | MDD | Bench MDD | Terminal | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1988-01-04 | 38.28 | B4-v2 35/40/25 | 15.65% | 11.35% | +4.30pp | -29.94% | -55.14% | 261.33x | 4.26x | 0.523 |
| 1988-01-04 | 38.28 | B4 original 25/25/25/25 | 14.21% | 11.35% | +2.86pp | -28.14% | -55.14% | 161.85x | 2.64x | 0.505 |
| 1994-01-03 | 32.28 | B4-v2 35/40/25 | 15.04% | 10.87% | +4.17pp | -29.94% | -55.14% | 92.15x | 3.30x | 0.502 |
| 1994-01-03 | 32.28 | B4 original 25/25/25/25 | 13.47% | 10.87% | +2.61pp | -28.14% | -55.14% | 59.19x | 2.12x | 0.479 |
| 2000-01-03 | 26.29 | B4-v2 35/40/25 | 13.36% | 8.22% | +5.14pp | -29.94% | -55.14% | 26.99x | 3.38x | 0.446 |
| 2000-01-03 | 26.29 | B4 original 25/25/25/25 | 11.91% | 8.22% | +3.69pp | -28.14% | -55.14% | 19.25x | 2.41x | 0.423 |
| 2003-01-02 | 23.29 | B4-v2 35/40/25 | 15.22% | 11.34% | +3.88pp | -28.02% | -55.14% | 27.09x | 2.22x | 0.543 |
| 2003-01-02 | 23.29 | B4 original 25/25/25/25 | 13.56% | 11.34% | +2.22pp | -27.25% | -55.14% | 19.34x | 1.58x | 0.498 |
| 2008-01-02 | 18.29 | B4-v2 35/40/25 | 13.86% | 11.21% | +2.64pp | -28.02% | -51.83% | 10.73x | 1.54x | 0.494 |
| 2008-01-02 | 18.29 | B4 original 25/25/25/25 | 12.47% | 11.21% | +1.26pp | -27.25% | -51.83% | 8.58x | 1.23x | 0.458 |
| 2010-01-04 | 16.28 | B4-v2 35/40/25 | 15.06% | 14.06% | +1.00pp | -21.46% | -33.69% | 9.82x | 1.15x | 0.702 |
| 2010-01-04 | 16.28 | B4 original 25/25/25/25 | 13.85% | 14.06% | -0.21pp | -24.92% | -33.69% | 8.27x | 0.97x | 0.556 |
| 2010-10-18 | 15.5 | B4-v2 35/40/25 | 14.67% | 14.39% | +0.28pp | -21.46% | -33.69% | 8.34x | 1.04x | 0.684 |
| 2010-10-18 | 15.5 | B4 original 25/25/25/25 | 13.44% | 14.39% | -0.95pp | -24.92% | -33.69% | 7.06x | 0.88x | 0.539 |
| 2013-01-02 | 13.29 | B4-v2 35/40/25 | 14.27% | 14.70% | -0.44pp | -21.46% | -33.69% | 5.88x | 0.95x | 0.665 |
| 2013-01-02 | 13.29 | B4 original 25/25/25/25 | 12.81% | 14.70% | -1.90pp | -24.92% | -33.69% | 4.96x | 0.80x | 0.514 |
| 2020-01-02 | 6.29 | B4-v2 35/40/25 | 16.94% | 14.99% | +1.94pp | -21.46% | -33.69% | 2.68x | 1.11x | 0.789 |
| 2020-01-02 | 6.29 | B4 original 25/25/25/25 | 13.68% | 14.99% | -1.32pp | -24.92% | -33.69% | 2.24x | 0.93x | 0.549 |


## US Implementation Variant Start-Date Sensitivity

Analysis: The implementation variants improve the 2010 inception cohort, especially the `RSSX` versions, but their advantage is not uniform. The same variants lose momentum in later starts such as 2020 and 2022, where higher RSSX weight increases drawdown and can trail SPY on CAGR.

Conclusion: Treat `CTAP` and `RSSX` as optional implementation enhancements, not as a replacement for the simpler `35/40/25` core. The `RSSX` rows need stronger assumption disclosure because they are more path and BTC-proxy sensitive.

| Start | Years | Portfolio | CAGR | Bench CAGR | Spread | MDD | Bench MDD | Terminal | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|---|---|---|
| 2010-10-18 | 15.59 | 35/40/25 core | 14.72% | 14.63% | +0.09pp | -21.46% | -33.69% | 8.51x | 1.01x | 0.686 |
| 2010-10-18 | 15.59 | 35/20/20/25 MF split | 15.05% | 14.63% | +0.42pp | -23.45% | -33.69% | 8.90x | 1.06x | 0.642 |
| 2010-10-18 | 15.59 | 10% RSSX + MF split | 15.97% | 14.63% | +1.34pp | -24.28% | -33.69% | 10.08x | 1.20x | 0.658 |
| 2010-10-18 | 15.59 | 17.5% RSSX + MF split | 16.64% | 14.63% | +2.01pp | -25.28% | -33.69% | 11.01x | 1.31x | 0.658 |
| 2013-01-02 | 13.38 | 35/40/25 core | 14.33% | 14.98% | -0.65pp | -21.46% | -33.69% | 6.00x | 0.93x | 0.668 |
| 2013-01-02 | 13.38 | 35/20/20/25 MF split | 14.63% | 14.98% | -0.35pp | -23.45% | -33.69% | 6.21x | 0.96x | 0.624 |
| 2013-01-02 | 13.38 | 10% RSSX + MF split | 15.11% | 14.98% | +0.13pp | -24.28% | -33.69% | 6.57x | 1.02x | 0.622 |
| 2013-01-02 | 13.38 | 17.5% RSSX + MF split | 15.45% | 14.98% | +0.47pp | -25.28% | -33.69% | 6.83x | 1.06x | 0.611 |
| 2016-01-04 | 10.38 | 35/40/25 core | 15.25% | 15.39% | -0.14pp | -21.46% | -33.69% | 4.36x | 0.99x | 0.711 |
| 2016-01-04 | 10.38 | 35/20/20/25 MF split | 15.91% | 15.39% | +0.52pp | -23.45% | -33.69% | 4.63x | 1.05x | 0.679 |
| 2016-01-04 | 10.38 | 10% RSSX + MF split | 15.62% | 15.39% | +0.23pp | -24.28% | -33.69% | 4.51x | 1.02x | 0.643 |
| 2016-01-04 | 10.38 | 17.5% RSSX + MF split | 15.39% | 15.39% | -0.00pp | -25.28% | -33.69% | 4.42x | 1.00x | 0.609 |
| 2020-01-02 | 6.38 | 35/40/25 core | 17.03% | 15.57% | +1.46pp | -21.46% | -33.69% | 2.73x | 1.08x | 0.794 |
| 2020-01-02 | 6.38 | 35/20/20/25 MF split | 16.72% | 15.57% | +1.15pp | -23.45% | -33.69% | 2.68x | 1.07x | 0.713 |
| 2020-01-02 | 6.38 | 10% RSSX + MF split | 15.97% | 15.57% | +0.39pp | -24.28% | -33.69% | 2.57x | 1.02x | 0.658 |
| 2020-01-02 | 6.38 | 17.5% RSSX + MF split | 15.39% | 15.57% | -0.18pp | -25.28% | -33.69% | 2.49x | 0.99x | 0.609 |
| 2022-01-03 | 4.38 | 35/40/25 core | 13.49% | 12.20% | +1.29pp | -21.46% | -24.44% | 1.74x | 1.05x | 0.629 |
| 2022-01-03 | 4.38 | 35/20/20/25 MF split | 13.26% | 12.20% | +1.06pp | -21.93% | -24.44% | 1.72x | 1.04x | 0.605 |
| 2022-01-03 | 4.38 | 10% RSSX + MF split | 11.68% | 12.20% | -0.52pp | -23.86% | -24.44% | 1.62x | 0.98x | 0.490 |
| 2022-01-03 | 4.38 | 17.5% RSSX + MF split | 10.50% | 12.20% | -1.70pp | -25.28% | -24.44% | 1.55x | 0.94x | 0.415 |


## Global Variant Start-Date Sensitivity vs 66/34 VTI/VEA

Analysis: The global variants beat `66/34 VTI/VEA` over long histories and reduce drawdowns substantially, but the advantage compresses after 2010. RSC-US remains the highest-return row in nearly every start window, so global diversification is buying smoother geographic exposure at the cost of absolute return.

Conclusion: The global set is a defensible diversification sleeve, not the lead portfolio. Use `66/34 VTI/VEA` as the primary global balanced benchmark because it is tougher than `100% VT` in several modern windows.

| Start | Years | Portfolio | CAGR | Bench CAGR | Spread | MDD | Bench MDD | Terminal | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1988-01-04 | 38.38 | Global simple NTSD/RSIT | 13.10% | 9.88% | +3.22pp | -34.35% | -56.92% | 112.47x | 3.03x | 0.381 |
| 1988-01-04 | 38.38 | Global 66/34 lead | 12.93% | 9.88% | +3.05pp | -30.54% | -56.92% | 106.31x | 2.86x | 0.423 |
| 1988-01-04 | 38.38 | Global 60/40 lead | 12.46% | 9.88% | +2.58pp | -30.95% | -56.92% | 90.67x | 2.44x | 0.403 |
| 1988-01-04 | 38.38 | US B4-v2 35/40/25 | 14.30% | 9.88% | +4.42pp | -31.66% | -56.92% | 168.73x | 4.54x | 0.452 |
| 1994-01-03 | 32.38 | Global simple NTSD/RSIT | 12.55% | 9.53% | +3.02pp | -34.35% | -56.92% | 45.97x | 2.41x | 0.365 |
| 1994-01-03 | 32.38 | Global 66/34 lead | 12.43% | 9.53% | +2.90pp | -30.54% | -56.92% | 44.36x | 2.33x | 0.407 |
| 1994-01-03 | 32.38 | Global 60/40 lead | 11.87% | 9.53% | +2.35pp | -30.95% | -56.92% | 37.83x | 1.99x | 0.384 |
| 1994-01-03 | 32.38 | US B4-v2 35/40/25 | 13.93% | 9.53% | +4.41pp | -31.66% | -56.92% | 68.28x | 3.59x | 0.440 |
| 2000-01-03 | 26.38 | Global simple NTSD/RSIT | 10.85% | 7.47% | +3.38pp | -34.35% | -56.92% | 15.16x | 2.26x | 0.316 |
| 2000-01-03 | 26.38 | Global 66/34 lead | 11.06% | 7.47% | +3.58pp | -30.54% | -56.92% | 15.90x | 2.38x | 0.362 |
| 2000-01-03 | 26.38 | Global 60/40 lead | 10.46% | 7.47% | +2.98pp | -30.95% | -56.92% | 13.78x | 2.06x | 0.338 |
| 2000-01-03 | 26.38 | US B4-v2 35/40/25 | 12.53% | 7.47% | +5.06pp | -31.66% | -56.92% | 22.51x | 3.36x | 0.396 |
| 2003-01-02 | 23.38 | Global simple NTSD/RSIT | 13.01% | 10.64% | +2.38pp | -33.79% | -56.92% | 17.47x | 1.64x | 0.385 |
| 2003-01-02 | 23.38 | Global 66/34 lead | 12.91% | 10.64% | +2.27pp | -30.54% | -56.92% | 17.09x | 1.61x | 0.423 |
| 2003-01-02 | 23.38 | Global 60/40 lead | 12.25% | 10.64% | +1.62pp | -30.95% | -56.92% | 14.92x | 1.40x | 0.396 |
| 2003-01-02 | 23.38 | US B4-v2 35/40/25 | 14.48% | 10.64% | +3.84pp | -28.20% | -56.92% | 23.59x | 2.22x | 0.513 |
| 2008-01-02 | 18.38 | Global simple NTSD/RSIT | 11.07% | 9.29% | +1.78pp | -33.79% | -53.97% | 6.88x | 1.35x | 0.327 |
| 2008-01-02 | 18.38 | Global 66/34 lead | 11.05% | 9.29% | +1.76pp | -30.54% | -53.97% | 6.86x | 1.34x | 0.362 |
| 2008-01-02 | 18.38 | Global 60/40 lead | 10.23% | 9.29% | +0.94pp | -30.95% | -53.97% | 5.99x | 1.17x | 0.331 |
| 2008-01-02 | 18.38 | US B4-v2 35/40/25 | 13.29% | 9.29% | +4.00pp | -28.20% | -53.97% | 9.90x | 1.94x | 0.471 |
| 2010-01-04 | 16.38 | Global simple NTSD/RSIT | 12.42% | 11.84% | +0.58pp | -22.32% | -34.74% | 6.80x | 1.09x | 0.556 |
| 2010-01-04 | 16.38 | Global 66/34 lead | 12.10% | 11.84% | +0.26pp | -21.87% | -34.74% | 6.49x | 1.04x | 0.553 |
| 2010-01-04 | 16.38 | Global 60/40 lead | 11.26% | 11.84% | -0.59pp | -21.77% | -34.74% | 5.74x | 0.92x | 0.517 |
| 2010-01-04 | 16.38 | US B4-v2 35/40/25 | 14.45% | 11.84% | +2.61pp | -21.83% | -34.74% | 9.12x | 1.46x | 0.662 |
| 2010-10-18 | 15.59 | Global simple NTSD/RSIT | 12.06% | 12.04% | +0.02pp | -22.32% | -34.74% | 5.90x | 1.00x | 0.540 |
| 2010-10-18 | 15.59 | Global 66/34 lead | 11.64% | 12.04% | -0.40pp | -21.87% | -34.74% | 5.57x | 0.95x | 0.532 |
| 2010-10-18 | 15.59 | Global 60/40 lead | 10.80% | 12.04% | -1.24pp | -21.77% | -34.74% | 4.95x | 0.84x | 0.496 |
| 2010-10-18 | 15.59 | US B4-v2 35/40/25 | 14.03% | 12.04% | +1.99pp | -21.83% | -34.74% | 7.75x | 1.32x | 0.643 |
| 2013-01-02 | 13.38 | Global simple NTSD/RSIT | 11.77% | 12.48% | -0.71pp | -22.32% | -34.74% | 4.43x | 0.92x | 0.527 |
| 2013-01-02 | 13.38 | Global 66/34 lead | 11.23% | 12.48% | -1.25pp | -21.87% | -34.74% | 4.15x | 0.86x | 0.514 |
| 2013-01-02 | 13.38 | Global 60/40 lead | 10.41% | 12.48% | -2.07pp | -21.77% | -34.74% | 3.76x | 0.78x | 0.478 |
| 2013-01-02 | 13.38 | US B4-v2 35/40/25 | 13.54% | 12.48% | +1.06pp | -21.83% | -34.74% | 5.47x | 1.13x | 0.620 |
| 2020-01-02 | 6.38 | Global simple NTSD/RSIT | 13.09% | 13.60% | -0.51pp | -22.32% | -34.74% | 2.19x | 0.97x | 0.587 |
| 2020-01-02 | 6.38 | Global 66/34 lead | 12.82% | 13.60% | -0.78pp | -21.87% | -34.74% | 2.16x | 0.96x | 0.586 |
| 2020-01-02 | 6.38 | Global 60/40 lead | 11.63% | 13.60% | -1.97pp | -21.77% | -34.74% | 2.02x | 0.89x | 0.534 |
| 2020-01-02 | 6.38 | US B4-v2 35/40/25 | 15.73% | 13.60% | +2.13pp | -21.83% | -34.74% | 2.54x | 1.13x | 0.721 |


## Global Variant Start-Date Sensitivity vs 100% VT

Analysis: Against `100% VT`, the global variants look much stronger because VT suffered deeper full-history drawdowns and lower long-run CAGR. Even so, the recent windows show a more nuanced result: `Global 60/40 lead` can trail VT on CAGR, while `Global simple NTSD/RSIT` and `Global 66/34 lead` mostly preserve drawdown advantages.

Conclusion: `100% VT` is useful as a public baseline, but it is not sufficient alone. The stronger conclusion comes from surviving both VT and the tougher `66/34 VTI/VEA` comparison.

| Start | Years | Portfolio | CAGR | Bench CAGR | Spread | MDD | Bench MDD | Terminal | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1988-01-04 | 38.38 | 66/34 VTI/VEA | 9.88% | 8.77% | +1.11pp | -56.92% | -58.35% | 37.15x | 1.48x | 0.174 |
| 1988-01-04 | 38.38 | Global simple NTSD/RSIT | 13.10% | 8.77% | +4.33pp | -34.35% | -58.35% | 112.47x | 4.47x | 0.381 |
| 1988-01-04 | 38.38 | Global 66/34 lead | 12.93% | 8.77% | +4.16pp | -30.54% | -58.35% | 106.31x | 4.22x | 0.423 |
| 1988-01-04 | 38.38 | Global 60/40 lead | 12.46% | 8.77% | +3.69pp | -30.95% | -58.35% | 90.67x | 3.60x | 0.403 |
| 1988-01-04 | 38.38 | US B4-v2 35/40/25 | 14.30% | 8.77% | +5.53pp | -31.66% | -58.35% | 168.73x | 6.70x | 0.452 |
| 1994-01-03 | 32.38 | 66/34 VTI/VEA | 9.53% | 8.75% | +0.78pp | -56.92% | -58.35% | 19.04x | 1.26x | 0.167 |
| 1994-01-03 | 32.38 | Global simple NTSD/RSIT | 12.55% | 8.75% | +3.80pp | -34.35% | -58.35% | 45.97x | 3.04x | 0.365 |
| 1994-01-03 | 32.38 | Global 66/34 lead | 12.43% | 8.75% | +3.67pp | -30.54% | -58.35% | 44.36x | 2.93x | 0.407 |
| 1994-01-03 | 32.38 | Global 60/40 lead | 11.87% | 8.75% | +3.12pp | -30.95% | -58.35% | 37.83x | 2.50x | 0.384 |
| 1994-01-03 | 32.38 | US B4-v2 35/40/25 | 13.93% | 8.75% | +5.18pp | -31.66% | -58.35% | 68.28x | 4.51x | 0.440 |
| 2000-01-03 | 26.38 | 66/34 VTI/VEA | 7.47% | 7.09% | +0.38pp | -56.92% | -58.35% | 6.69x | 1.10x | 0.131 |
| 2000-01-03 | 26.38 | Global simple NTSD/RSIT | 10.85% | 7.09% | +3.76pp | -34.35% | -58.35% | 15.16x | 2.49x | 0.316 |
| 2000-01-03 | 26.38 | Global 66/34 lead | 11.06% | 7.09% | +3.97pp | -30.54% | -58.35% | 15.90x | 2.61x | 0.362 |
| 2000-01-03 | 26.38 | Global 60/40 lead | 10.46% | 7.09% | +3.37pp | -30.95% | -58.35% | 13.78x | 2.26x | 0.338 |
| 2000-01-03 | 26.38 | US B4-v2 35/40/25 | 12.53% | 7.09% | +5.44pp | -31.66% | -58.35% | 22.51x | 3.69x | 0.396 |
| 2003-01-02 | 23.38 | 66/34 VTI/VEA | 10.64% | 10.21% | +0.43pp | -56.92% | -58.35% | 10.63x | 1.09x | 0.187 |
| 2003-01-02 | 23.38 | Global simple NTSD/RSIT | 13.01% | 10.21% | +2.80pp | -33.79% | -58.35% | 17.47x | 1.80x | 0.385 |
| 2003-01-02 | 23.38 | Global 66/34 lead | 12.91% | 10.21% | +2.70pp | -30.54% | -58.35% | 17.09x | 1.76x | 0.423 |
| 2003-01-02 | 23.38 | Global 60/40 lead | 12.25% | 10.21% | +2.04pp | -30.95% | -58.35% | 14.92x | 1.54x | 0.396 |
| 2003-01-02 | 23.38 | US B4-v2 35/40/25 | 14.48% | 10.21% | +4.26pp | -28.20% | -58.35% | 23.59x | 2.43x | 0.513 |
| 2008-01-02 | 18.38 | 66/34 VTI/VEA | 9.29% | 8.07% | +1.22pp | -53.97% | -55.48% | 5.12x | 1.23x | 0.172 |
| 2008-01-02 | 18.38 | Global simple NTSD/RSIT | 11.07% | 8.07% | +3.00pp | -33.79% | -55.48% | 6.88x | 1.65x | 0.327 |
| 2008-01-02 | 18.38 | Global 66/34 lead | 11.05% | 8.07% | +2.98pp | -30.54% | -55.48% | 6.86x | 1.65x | 0.362 |
| 2008-01-02 | 18.38 | Global 60/40 lead | 10.23% | 8.07% | +2.16pp | -30.95% | -55.48% | 5.99x | 1.44x | 0.331 |
| 2008-01-02 | 18.38 | US B4-v2 35/40/25 | 13.29% | 8.07% | +5.22pp | -28.20% | -55.48% | 9.90x | 2.38x | 0.471 |
| 2010-01-04 | 16.38 | 66/34 VTI/VEA | 11.84% | 10.45% | +1.39pp | -34.74% | -34.22% | 6.25x | 1.23x | 0.341 |
| 2010-01-04 | 16.38 | Global simple NTSD/RSIT | 12.42% | 10.45% | +1.97pp | -22.32% | -34.22% | 6.80x | 1.34x | 0.556 |
| 2010-01-04 | 16.38 | Global 66/34 lead | 12.10% | 10.45% | +1.65pp | -21.87% | -34.22% | 6.49x | 1.27x | 0.553 |
| 2010-01-04 | 16.38 | Global 60/40 lead | 11.26% | 10.45% | +0.81pp | -21.77% | -34.22% | 5.74x | 1.13x | 0.517 |
| 2010-01-04 | 16.38 | US B4-v2 35/40/25 | 14.45% | 10.45% | +4.00pp | -21.83% | -34.22% | 9.12x | 1.79x | 0.662 |
| 2010-10-18 | 15.59 | 66/34 VTI/VEA | 12.04% | 10.60% | +1.45pp | -34.74% | -34.22% | 5.89x | 1.22x | 0.347 |
| 2010-10-18 | 15.59 | Global simple NTSD/RSIT | 12.06% | 10.60% | +1.47pp | -22.32% | -34.22% | 5.90x | 1.23x | 0.540 |
| 2010-10-18 | 15.59 | Global 66/34 lead | 11.64% | 10.60% | +1.05pp | -21.87% | -34.22% | 5.57x | 1.16x | 0.532 |
| 2010-10-18 | 15.59 | Global 60/40 lead | 10.80% | 10.60% | +0.20pp | -21.77% | -34.22% | 4.95x | 1.03x | 0.496 |
| 2010-10-18 | 15.59 | US B4-v2 35/40/25 | 14.03% | 10.60% | +3.44pp | -21.83% | -34.22% | 7.75x | 1.61x | 0.643 |
| 2013-01-02 | 13.38 | 66/34 VTI/VEA | 12.48% | 11.23% | +1.25pp | -34.74% | -34.22% | 4.82x | 1.16x | 0.359 |
| 2013-01-02 | 13.38 | Global simple NTSD/RSIT | 11.77% | 11.23% | +0.54pp | -22.32% | -34.22% | 4.43x | 1.07x | 0.527 |
| 2013-01-02 | 13.38 | Global 66/34 lead | 11.23% | 11.23% | +0.00pp | -21.87% | -34.22% | 4.15x | 1.00x | 0.514 |
| 2013-01-02 | 13.38 | Global 60/40 lead | 10.41% | 11.23% | -0.82pp | -21.77% | -34.22% | 3.76x | 0.91x | 0.478 |
| 2013-01-02 | 13.38 | US B4-v2 35/40/25 | 13.54% | 11.23% | +2.31pp | -21.83% | -34.22% | 5.47x | 1.32x | 0.620 |
| 2020-01-02 | 6.38 | 66/34 VTI/VEA | 13.60% | 12.82% | +0.78pp | -34.74% | -34.22% | 2.26x | 1.04x | 0.392 |
| 2020-01-02 | 6.38 | Global simple NTSD/RSIT | 13.09% | 12.82% | +0.27pp | -22.32% | -34.22% | 2.19x | 1.02x | 0.587 |
| 2020-01-02 | 6.38 | Global 66/34 lead | 12.82% | 12.82% | -0.00pp | -21.87% | -34.22% | 2.16x | 1.00x | 0.586 |
| 2020-01-02 | 6.38 | Global 60/40 lead | 11.63% | 12.82% | -1.19pp | -21.77% | -34.22% | 2.02x | 0.93x | 0.534 |
| 2020-01-02 | 6.38 | US B4-v2 35/40/25 | 15.73% | 12.82% | +2.91pp | -21.83% | -34.22% | 2.54x | 1.18x | 0.721 |


## US Rolling Relative Wealth Summary

Analysis: Rolling windows show the core trade-off better than the full-period CAGR. `35/40/25` wins most 5y, 10y and 15y windows and has positive 15y p10 relative wealth, but short 3y and some 10y windows still underperform SPY.

Conclusion: The edge is long-horizon and patience-dependent. It should not be marketed as a short-horizon SPY replacement.

| Horizon | Portfolio | Windows | Hit rate | Rel min | Rel p10 | Rel median | Rel latest | CAGR spread p10 | CAGR spread median | CAGR spread latest |
|---|---|---|---|---|---|---|---|---|---|---|
| 3y | B4-v2 35/40/25 | 8889 | 73.48% | -27.07% | -9.84% | 10.96% | -0.07% | -3.89pp | +4.04pp | -0.03pp |
| 3y | B4 original 25/25/25/25 | 8889 | 67.85% | -23.85% | -12.66% | 7.69% | -7.50% | -5.04pp | +2.82pp | -3.13pp |
| 5y | B4-v2 35/40/25 | 8385 | 80.32% | -22.58% | -8.59% | 17.97% | 8.72% | -2.07pp | +3.85pp | +1.91pp |
| 5y | B4 original 25/25/25/25 | 8385 | 71.27% | -29.70% | -12.19% | 12.36% | -7.14% | -2.99pp | +2.70pp | -1.66pp |
| 10y | B4-v2 35/40/25 | 7125 | 86.09% | -23.15% | -4.25% | 60.20% | -5.99% | -0.49pp | +5.34pp | -0.71pp |
| 10y | B4 original 25/25/25/25 | 7125 | 80.62% | -25.63% | -13.62% | 43.23% | -19.23% | -1.65pp | +4.03pp | -2.43pp |
| 15y | B4-v2 35/40/25 | 5865 | 95.50% | -18.59% | 12.87% | 109.54% | 7.24% | +0.92pp | +5.59pp | +0.53pp |
| 15y | B4 original 25/25/25/25 | 5865 | 89.51% | -25.92% | -2.39% | 76.96% | -7.59% | -0.18pp | +4.28pp | -0.60pp |


## US Implementation Rolling Relative Wealth Summary

Analysis: The implementation rows are less stable than the full-period table implies. RSSX-heavy variants improve median and hit-rate statistics over 10y windows, but their latest rolling windows are negative versus SPY, which matters for current investor expectations.

Conclusion: The implementation variants are promising but not clean enough to become the headline. They belong in an implementation appendix or optional variant discussion.

| Horizon | Portfolio | Windows | Hit rate | Rel min | Rel p10 | Rel median | Rel latest | CAGR spread p10 | CAGR spread median | CAGR spread latest |
|---|---|---|---|---|---|---|---|---|---|---|
| 3y | 35/40/25 core | 3166 | 40.11% | -27.07% | -15.10% | -4.58% | -1.27% | -6.19pp | -1.77pp | -0.53pp |
| 3y | 35/20/20/25 MF split | 3166 | 42.55% | -24.27% | -13.54% | -3.83% | 1.98% | -5.48pp | -1.48pp | +0.81pp |
| 3y | 10% RSSX + MF split | 3166 | 49.87% | -19.76% | -12.47% | -0.04% | -1.30% | -4.93pp | -0.02pp | -0.54pp |
| 3y | 17.5% RSSX + MF split | 3166 | 54.67% | -18.88% | -13.21% | 1.38% | -3.71% | -5.22pp | +0.51pp | -1.55pp |
| 5y | 35/40/25 core | 2662 | 49.14% | -22.58% | -16.59% | -0.30% | 1.59% | -4.09pp | -0.07pp | +0.36pp |
| 5y | 35/20/20/25 MF split | 2662 | 53.61% | -20.26% | -14.97% | 1.30% | 1.39% | -3.66pp | +0.30pp | +0.31pp |
| 5y | 10% RSSX + MF split | 2662 | 57.74% | -20.94% | -8.05% | 1.79% | -5.31% | -1.91pp | +0.41pp | -1.24pp |
| 5y | 17.5% RSSX + MF split | 2662 | 71.07% | -21.82% | -8.64% | 4.14% | -10.09% | -2.06pp | +0.93pp | -2.40pp |
| 10y | 35/40/25 core | 1402 | 37.45% | -23.15% | -14.38% | -3.03% | -7.34% | -1.76pp | -0.35pp | -0.88pp |
| 10y | 35/20/20/25 MF split | 1402 | 51.64% | -18.24% | -10.29% | 0.42% | -2.31% | -1.23pp | +0.05pp | -0.27pp |
| 10y | 10% RSSX + MF split | 1402 | 74.96% | -13.82% | -3.12% | 3.44% | -4.42% | -0.36pp | +0.38pp | -0.52pp |
| 10y | 17.5% RSSX + MF split | 1402 | 76.32% | -13.40% | -3.49% | 7.88% | -6.08% | -0.41pp | +0.86pp | -0.72pp |


## Global Rolling Relative Wealth Summary vs 66/34

Analysis: Global variants have strong long-horizon hit rates versus `66/34`, especially at 10y and 15y, but recent relative wealth is weak for the global-only rows. RSC-US remains the strongest rolling performer, including a 100% 15y hit rate in this table.

Conclusion: Global diversification improves robustness optics, but the current cycle has penalized non-US exposure. The report should frame global as diversification insurance, not as recent-performance leadership.

| Horizon | Portfolio | Windows | Hit rate | Rel min | Rel p10 | Rel median | Rel latest | CAGR spread p10 | CAGR spread median | CAGR spread latest |
|---|---|---|---|---|---|---|---|---|---|---|
| 3y | Global simple NTSD/RSIT | 8913 | 74.37% | -22.73% | -9.01% | 10.77% | -10.53% | -3.47pp | +3.83pp | -4.44pp |
| 3y | Global 66/34 lead | 8913 | 71.57% | -24.58% | -10.83% | 9.69% | -11.54% | -4.16pp | +3.51pp | -4.89pp |
| 3y | Global 60/40 lead | 8913 | 70.62% | -25.91% | -12.67% | 8.19% | -15.18% | -4.90pp | +3.01pp | -6.51pp |
| 3y | US B4-v2 35/40/25 | 8913 | 76.53% | -22.60% | -6.19% | 13.49% | -2.85% | -2.37pp | +4.70pp | -1.17pp |
| 5y | Global simple NTSD/RSIT | 8409 | 84.42% | -24.47% | -6.91% | 17.60% | -7.81% | -1.60pp | +3.65pp | -1.81pp |
| 5y | Global 66/34 lead | 8409 | 80.60% | -27.10% | -9.58% | 15.64% | -8.72% | -2.26pp | +3.24pp | -2.02pp |
| 5y | Global 60/40 lead | 8409 | 76.57% | -30.66% | -12.62% | 14.41% | -13.50% | -3.00pp | +3.04pp | -3.20pp |
| 5y | US B4-v2 35/40/25 | 8409 | 89.37% | -18.27% | -1.14% | 22.62% | 3.56% | -0.26pp | +4.56pp | +0.79pp |
| 10y | Global simple NTSD/RSIT | 7149 | 89.90% | -20.01% | -0.18% | 48.55% | -15.18% | -0.02pp | +4.42pp | -1.85pp |
| 10y | Global 66/34 lead | 7149 | 87.08% | -23.23% | -5.37% | 44.94% | -18.61% | -0.61pp | +4.14pp | -2.31pp |
| 10y | Global 60/40 lead | 7149 | 81.72% | -29.77% | -10.83% | 42.39% | -25.47% | -1.26pp | +3.93pp | -3.29pp |
| 10y | US B4-v2 35/40/25 | 7149 | 99.36% | -7.91% | 14.29% | 57.83% | 1.39% | +1.49pp | +5.09pp | +0.16pp |
| 15y | Global simple NTSD/RSIT | 5889 | 96.86% | -11.44% | 13.49% | 81.38% | 3.03% | +0.94pp | +4.40pp | +0.22pp |
| 15y | Global 66/34 lead | 5889 | 94.31% | -19.09% | 7.99% | 80.56% | -2.17% | +0.57pp | +4.33pp | -0.16pp |
| 15y | Global 60/40 lead | 5889 | 89.40% | -26.66% | -3.10% | 72.62% | -12.24% | -0.23pp | +4.01pp | -0.97pp |
| 15y | US B4-v2 35/40/25 | 5889 | 100.00% | 5.98% | 47.43% | 110.08% | 32.72% | +2.92pp | +5.49pp | +2.12pp |


## Global Rolling Relative Wealth Summary vs 100% VT

Analysis: The same global variants look more favorable versus VT, with very high 10y and 15y hit rates. However, recent 3y, 5y and 10y relative wealth is still negative for the global-only rows, so the benchmark choice changes the apparent strength of the result.

Conclusion: VT confirms the long-horizon diversification case, while `66/34` keeps the conclusion honest. Both benchmarks should remain in the report.

| Horizon | Portfolio | Windows | Hit rate | Rel min | Rel p10 | Rel median | Rel latest | CAGR spread p10 | CAGR spread median | CAGR spread latest |
|---|---|---|---|---|---|---|---|---|---|---|
| 3y | 66/34 VTI/VEA | 8913 | 73.65% | -8.57% | -4.71% | 2.34% | 1.46% | -1.71pp | +0.84pp | +0.59pp |
| 3y | Global simple NTSD/RSIT | 8913 | 79.29% | -21.18% | -6.90% | 13.15% | -9.23% | -2.63pp | +4.50pp | -3.86pp |
| 3y | Global 66/34 lead | 8913 | 76.47% | -23.70% | -8.83% | 12.71% | -10.26% | -3.36pp | +4.42pp | -4.30pp |
| 3y | Global 60/40 lead | 8913 | 75.89% | -24.75% | -10.51% | 11.22% | -13.94% | -3.99pp | +3.99pp | -5.93pp |
| 3y | US B4-v2 35/40/25 | 8913 | 80.99% | -20.63% | -5.77% | 16.26% | -1.44% | -2.22pp | +5.54pp | -0.58pp |
| 5y | 66/34 VTI/VEA | 8409 | 74.41% | -11.93% | -6.96% | 5.18% | 3.02% | -1.51pp | +1.07pp | +0.66pp |
| 5y | Global simple NTSD/RSIT | 8409 | 88.31% | -22.34% | -1.44% | 24.89% | -5.03% | -0.32pp | +4.88pp | -1.14pp |
| 5y | Global 66/34 lead | 8409 | 85.24% | -25.04% | -4.20% | 23.10% | -5.96% | -0.95pp | +4.60pp | -1.36pp |
| 5y | Global 60/40 lead | 8409 | 82.64% | -28.52% | -7.45% | 21.76% | -10.88% | -1.74pp | +4.40pp | -2.53pp |
| 5y | US B4-v2 35/40/25 | 8409 | 91.08% | -15.96% | 0.91% | 30.29% | 6.69% | +0.20pp | +5.90pp | +1.45pp |
| 10y | 66/34 VTI/VEA | 7149 | 75.98% | -14.44% | -9.17% | 10.15% | 5.97% | -1.00pp | +1.04pp | +0.66pp |
| 10y | Global simple NTSD/RSIT | 7149 | 95.03% | -15.84% | 12.60% | 61.38% | -10.12% | +1.31pp | +5.28pp | -1.20pp |
| 10y | Global 66/34 lead | 7149 | 93.43% | -19.24% | 6.21% | 60.47% | -13.76% | +0.66pp | +5.23pp | -1.66pp |
| 10y | Global 60/40 lead | 7149 | 90.31% | -26.12% | 0.80% | 56.16% | -21.03% | +0.09pp | +4.92pp | -2.63pp |
| 10y | US B4-v2 35/40/25 | 7149 | 100.00% | 0.22% | 27.51% | 75.09% | 7.43% | +2.67pp | +6.19pp | +0.81pp |
| 15y | 66/34 VTI/VEA | 5889 | 87.16% | -6.76% | -0.80% | 7.07% | 19.84% | -0.06pp | +0.49pp | +1.34pp |
| 15y | Global simple NTSD/RSIT | 5889 | 100.00% | 2.88% | 36.92% | 99.61% | 23.47% | +2.32pp | +5.08pp | +1.56pp |
| 15y | Global 66/34 lead | 5889 | 99.76% | -5.69% | 30.24% | 102.18% | 17.24% | +1.95pp | +5.14pp | +1.17pp |
| 15y | Global 60/40 lead | 5889 | 97.71% | -13.98% | 16.83% | 92.76% | 5.17% | +1.15pp | +4.81pp | +0.37pp |
| 15y | US B4-v2 35/40/25 | 5889 | 100.00% | 23.25% | 72.86% | 134.06% | 59.06% | +4.09pp | +6.23pp | +3.46pp |


## US Relative Underperformance Episodes

Analysis: Full-history underperformance episodes are short and rare for both B4 rows. The core spends only `2.60%` of days below SPY and has a latest relative wealth of `+325.96%`, which is a strong robustness point.

Conclusion: The US core has strong long-run relative persistence, but the max relative drawdown around `-33%` means investors still need tolerance for multi-year relative pain.

| Portfolio | Days below bench | Longest below | Max deficit | Latest rel wealth | Max rel DD |
|---|---|---|---|---|---|
| B4-v2 35/40/25 | 2.60% | 98 | -6.50% | 325.96% | -33.18% |
| B4 original 25/25/25/25 | 3.04% | 108 | -5.73% | 163.81% | -35.71% |


## US Implementation Relative Underperformance Episodes

Analysis: Since the implementation table starts in 2010, the simple core spends much more time below SPY, while RSSX variants dramatically reduce days below benchmark. This is the main empirical argument for RSSX, but it is also tied to the specific proxy and period.

Conclusion: RSSX improves this relative-underperformance diagnostic, but that improvement should be treated as provisional until the BTC/RSSX assumptions are independently stress-tested.

| Portfolio | Days below bench | Longest below | Max deficit | Latest rel wealth | Max rel DD |
|---|---|---|---|---|---|
| 35/40/25 core | 59.74% | 675 | -14.98% | 1.22% | -33.18% |
| 35/20/20/25 MF split | 48.44% | 476 | -12.60% | 5.90% | -30.07% |
| 10% RSSX + MF split | 2.63% | 38 | -4.36% | 19.91% | -24.12% |
| 17.5% RSSX + MF split | 1.10% | 26 | -1.94% | 31.05% | -24.12% |


## Global Relative Underperformance Episodes vs 66/34

Analysis: The global variants spend only about `3%` of days below `66/34`, but their max relative drawdowns remain meaningful. RSC-US has the highest latest relative wealth, while global rows trade some upside for geographic diversification.

Conclusion: Relative persistence is acceptable for all global candidates, with the strongest practical case for the variants that reduce drawdown without giving up too much terminal wealth.

| Portfolio | Days below bench | Longest below | Max deficit | Latest rel wealth | Max rel DD |
|---|---|---|---|---|---|
| Global simple NTSD/RSIT | 3.11% | 106 | -7.92% | 202.75% | -27.44% |
| Global 66/34 lead | 3.55% | 144 | -9.11% | 186.18% | -30.73% |
| Global 60/40 lead | 3.23% | 104 | -7.74% | 144.08% | -36.23% |
| US B4-v2 35/40/25 | 3.65% | 231 | -13.47% | 354.20% | -31.38% |


## Global Relative Underperformance Episodes vs 100% VT

Analysis: Versus VT, all B4-style variants show very large latest relative wealth, but the max relative drawdown is still non-trivial. `66/34 VTI/VEA` itself also beats VT over the sample, which shows that VT is a soft benchmark for this design.

Conclusion: The VT comparison is useful for public communication, but the investment-quality conclusion should lean more on the `66/34` benchmark.

| Portfolio | Days below bench | Longest below | Max deficit | Latest rel wealth | Max rel DD |
|---|---|---|---|---|---|
| 66/34 VTI/VEA | 2.35% | 109 | -4.19% | 47.57% | -15.67% |
| Global simple NTSD/RSIT | 2.97% | 113 | -10.45% | 346.77% | -27.29% |
| Global 66/34 lead | 3.32% | 147 | -11.59% | 322.32% | -29.59% |
| Global 60/40 lead | 3.02% | 131 | -10.22% | 260.19% | -32.28% |
| US B4-v2 35/40/25 | 3.53% | 224 | -15.84% | 570.26% | -31.33% |


## US Fee/Drag Stress

Analysis: The US core remains ahead of SPY even after `150 bps/yr` of extra drag, though the terminal advantage compresses materially. This means the full-history result is not purely an artifact of zero-friction assumptions.

Conclusion: Fee/drag resilience is good for the US core, but realistic implementation costs still matter and should be explicitly modeled before any future mandate discussion.

| Portfolio | Extra drag | CAGR | Bench CAGR | Spread | MDD | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|
| B4-v2 35/40/25 | 0 bps/yr | 15.65% | 11.35% | +4.30pp | -29.94% | 4.26x | 0.523 |
| B4-v2 35/40/25 | 25 bps/yr | 15.36% | 11.35% | +4.01pp | -30.27% | 3.87x | 0.507 |
| B4-v2 35/40/25 | 50 bps/yr | 15.07% | 11.35% | +3.72pp | -30.59% | 3.52x | 0.493 |
| B4-v2 35/40/25 | 100 bps/yr | 14.50% | 11.35% | +3.15pp | -31.24% | 2.91x | 0.464 |
| B4-v2 35/40/25 | 150 bps/yr | 13.93% | 11.35% | +2.57pp | -31.87% | 2.40x | 0.437 |
| B4 original 25/25/25/25 | 0 bps/yr | 14.21% | 11.35% | +2.86pp | -28.14% | 2.64x | 0.505 |
| B4 original 25/25/25/25 | 25 bps/yr | 13.92% | 11.35% | +2.57pp | -28.48% | 2.40x | 0.489 |
| B4 original 25/25/25/25 | 50 bps/yr | 13.64% | 11.35% | +2.29pp | -28.81% | 2.18x | 0.473 |
| B4 original 25/25/25/25 | 100 bps/yr | 13.07% | 11.35% | +1.72pp | -29.47% | 1.80x | 0.444 |
| B4 original 25/25/25/25 | 150 bps/yr | 12.51% | 11.35% | +1.16pp | -30.13% | 1.49x | 0.415 |


## US Implementation Fee/Drag Stress

Analysis: Post-2010 implementation variants have much less fee headroom than the full-history US core. The simple core loses its SPY spread with only `25 bps/yr` extra drag, while RSSX variants keep a positive spread longer but take higher drawdown.

Conclusion: Implementation details can erase the modern edge. If this ever moves beyond research, expense ratios, trading costs and tax drag must be modeled as first-class assumptions.

| Portfolio | Extra drag | CAGR | Bench CAGR | Spread | MDD | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|
| 35/40/25 core | 0 bps/yr | 14.72% | 14.63% | +0.09pp | -21.46% | 1.01x | 0.686 |
| 35/40/25 core | 25 bps/yr | 14.43% | 14.63% | -0.20pp | -21.57% | 0.97x | 0.669 |
| 35/40/25 core | 50 bps/yr | 14.15% | 14.63% | -0.48pp | -21.68% | 0.94x | 0.653 |
| 35/40/25 core | 100 bps/yr | 13.58% | 14.63% | -1.05pp | -21.90% | 0.87x | 0.620 |
| 35/40/25 core | 150 bps/yr | 13.01% | 14.63% | -1.62pp | -22.12% | 0.80x | 0.588 |
| 35/20/20/25 MF split | 0 bps/yr | 15.05% | 14.63% | +0.42pp | -23.45% | 1.06x | 0.642 |
| 35/20/20/25 MF split | 25 bps/yr | 14.77% | 14.63% | +0.14pp | -23.47% | 1.02x | 0.629 |
| 35/20/20/25 MF split | 50 bps/yr | 14.48% | 14.63% | -0.15pp | -23.48% | 0.98x | 0.617 |
| 35/20/20/25 MF split | 100 bps/yr | 13.91% | 14.63% | -0.72pp | -23.51% | 0.91x | 0.592 |
| 35/20/20/25 MF split | 150 bps/yr | 13.34% | 14.63% | -1.29pp | -23.54% | 0.84x | 0.567 |
| 10% RSSX + MF split | 0 bps/yr | 15.97% | 14.63% | +1.34pp | -24.28% | 1.20x | 0.658 |
| 10% RSSX + MF split | 25 bps/yr | 15.68% | 14.63% | +1.05pp | -24.30% | 1.15x | 0.646 |
| 10% RSSX + MF split | 50 bps/yr | 15.40% | 14.63% | +0.77pp | -24.31% | 1.11x | 0.633 |
| 10% RSSX + MF split | 100 bps/yr | 14.82% | 14.63% | +0.19pp | -24.34% | 1.03x | 0.609 |
| 10% RSSX + MF split | 150 bps/yr | 14.25% | 14.63% | -0.38pp | -24.49% | 0.95x | 0.582 |
| 17.5% RSSX + MF split | 0 bps/yr | 16.64% | 14.63% | +2.01pp | -25.28% | 1.31x | 0.658 |
| 17.5% RSSX + MF split | 25 bps/yr | 16.35% | 14.63% | +1.72pp | -25.39% | 1.26x | 0.644 |
| 17.5% RSSX + MF split | 50 bps/yr | 16.06% | 14.63% | +1.43pp | -25.49% | 1.21x | 0.630 |
| 17.5% RSSX + MF split | 100 bps/yr | 15.48% | 14.63% | +0.85pp | -25.79% | 1.12x | 0.600 |
| 17.5% RSSX + MF split | 150 bps/yr | 14.90% | 14.63% | +0.27pp | -26.14% | 1.04x | 0.570 |


## Global Fee/Drag Stress vs 66/34

Analysis: Global variants remain ahead of `66/34` under the tested drag levels, but the margin narrows as expected. `Global 66/34 lead` has the cleanest drawdown profile among global variants, while `Global simple NTSD/RSIT` keeps slightly higher return with deeper drawdown.

Conclusion: The global variants have acceptable drag tolerance versus `66/34`, but the best choice depends on whether the objective is return or drawdown control.

| Portfolio | Extra drag | CAGR | Bench CAGR | Spread | MDD | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|
| Global simple NTSD/RSIT | 0 bps/yr | 13.10% | 9.88% | +3.22pp | -34.35% | 3.03x | 0.381 |
| Global simple NTSD/RSIT | 25 bps/yr | 12.81% | 9.88% | +2.94pp | -34.65% | 2.75x | 0.370 |
| Global simple NTSD/RSIT | 50 bps/yr | 12.53% | 9.88% | +2.65pp | -34.96% | 2.50x | 0.358 |
| Global simple NTSD/RSIT | 100 bps/yr | 11.97% | 9.88% | +2.09pp | -35.56% | 2.06x | 0.337 |
| Global simple NTSD/RSIT | 150 bps/yr | 11.41% | 9.88% | +1.53pp | -36.16% | 1.70x | 0.316 |
| Global 66/34 lead | 0 bps/yr | 12.93% | 9.88% | +3.05pp | -30.54% | 2.86x | 0.423 |
| Global 66/34 lead | 25 bps/yr | 12.65% | 9.88% | +2.77pp | -30.62% | 2.60x | 0.413 |
| Global 66/34 lead | 50 bps/yr | 12.37% | 9.88% | +2.49pp | -30.70% | 2.36x | 0.403 |
| Global 66/34 lead | 100 bps/yr | 11.81% | 9.88% | +1.93pp | -31.21% | 1.95x | 0.378 |
| Global 66/34 lead | 150 bps/yr | 11.25% | 9.88% | +1.37pp | -31.85% | 1.61x | 0.353 |
| Global 60/40 lead | 0 bps/yr | 12.46% | 9.88% | +2.58pp | -30.95% | 2.44x | 0.403 |
| Global 60/40 lead | 25 bps/yr | 12.18% | 9.88% | +2.30pp | -31.03% | 2.22x | 0.393 |
| Global 60/40 lead | 50 bps/yr | 11.90% | 9.88% | +2.02pp | -31.10% | 2.01x | 0.383 |
| Global 60/40 lead | 100 bps/yr | 11.34% | 9.88% | +1.47pp | -31.25% | 1.66x | 0.363 |
| Global 60/40 lead | 150 bps/yr | 10.79% | 9.88% | +0.91pp | -31.40% | 1.37x | 0.344 |
| US B4-v2 35/40/25 | 0 bps/yr | 14.30% | 9.88% | +4.42pp | -31.66% | 4.54x | 0.452 |
| US B4-v2 35/40/25 | 25 bps/yr | 14.01% | 9.88% | +4.13pp | -31.98% | 4.13x | 0.438 |
| US B4-v2 35/40/25 | 50 bps/yr | 13.73% | 9.88% | +3.85pp | -32.30% | 3.75x | 0.425 |
| US B4-v2 35/40/25 | 100 bps/yr | 13.16% | 9.88% | +3.28pp | -32.93% | 3.09x | 0.400 |
| US B4-v2 35/40/25 | 150 bps/yr | 12.60% | 9.88% | +2.72pp | -33.55% | 2.55x | 0.375 |


## Global Fee/Drag Stress vs 100% VT

Analysis: Against VT, every global variant keeps a positive spread even at `150 bps/yr` extra drag. This confirms that the global B4-style construction is not fragile versus a broad global equity baseline.

Conclusion: VT drag stress is supportive but not decisive. The tougher `66/34` drag test should remain the primary implementation hurdle.

| Portfolio | Extra drag | CAGR | Bench CAGR | Spread | MDD | Terminal/Bench | Calmar |
|---|---|---|---|---|---|---|---|
| 66/34 VTI/VEA | 0 bps/yr | 9.88% | 8.77% | +1.11pp | -56.92% | 1.48x | 0.174 |
| 66/34 VTI/VEA | 25 bps/yr | 9.60% | 8.77% | +0.83pp | -57.07% | 1.34x | 0.168 |
| 66/34 VTI/VEA | 50 bps/yr | 9.33% | 8.77% | +0.56pp | -57.21% | 1.22x | 0.163 |
| 66/34 VTI/VEA | 100 bps/yr | 8.78% | 8.77% | +0.02pp | -57.50% | 1.01x | 0.153 |
| 66/34 VTI/VEA | 150 bps/yr | 8.24% | 8.77% | -0.53pp | -57.80% | 0.83x | 0.143 |
| Global simple NTSD/RSIT | 0 bps/yr | 13.10% | 8.77% | +4.33pp | -34.35% | 4.47x | 0.381 |
| Global simple NTSD/RSIT | 25 bps/yr | 12.81% | 8.77% | +4.04pp | -34.65% | 4.06x | 0.370 |
| Global simple NTSD/RSIT | 50 bps/yr | 12.53% | 8.77% | +3.76pp | -34.96% | 3.69x | 0.358 |
| Global simple NTSD/RSIT | 100 bps/yr | 11.97% | 8.77% | +3.20pp | -35.56% | 3.04x | 0.337 |
| Global simple NTSD/RSIT | 150 bps/yr | 11.41% | 8.77% | +2.64pp | -36.16% | 2.51x | 0.316 |
| Global 66/34 lead | 0 bps/yr | 12.93% | 8.77% | +4.16pp | -30.54% | 4.22x | 0.423 |
| Global 66/34 lead | 25 bps/yr | 12.65% | 8.77% | +3.88pp | -30.62% | 3.84x | 0.413 |
| Global 66/34 lead | 50 bps/yr | 12.37% | 8.77% | +3.60pp | -30.70% | 3.49x | 0.403 |
| Global 66/34 lead | 100 bps/yr | 11.81% | 8.77% | +3.04pp | -31.21% | 2.88x | 0.378 |
| Global 66/34 lead | 150 bps/yr | 11.25% | 8.77% | +2.48pp | -31.85% | 2.38x | 0.353 |
| Global 60/40 lead | 0 bps/yr | 12.46% | 8.77% | +3.69pp | -30.95% | 3.60x | 0.403 |
| Global 60/40 lead | 25 bps/yr | 12.18% | 8.77% | +3.41pp | -31.03% | 3.27x | 0.393 |
| Global 60/40 lead | 50 bps/yr | 11.90% | 8.77% | +3.13pp | -31.10% | 2.97x | 0.383 |
| Global 60/40 lead | 100 bps/yr | 11.34% | 8.77% | +2.57pp | -31.25% | 2.45x | 0.363 |
| Global 60/40 lead | 150 bps/yr | 10.79% | 8.77% | +2.02pp | -31.40% | 2.03x | 0.344 |
| US B4-v2 35/40/25 | 0 bps/yr | 14.30% | 8.77% | +5.53pp | -31.66% | 6.70x | 0.452 |
| US B4-v2 35/40/25 | 25 bps/yr | 14.01% | 8.77% | +5.24pp | -31.98% | 6.09x | 0.438 |
| US B4-v2 35/40/25 | 50 bps/yr | 13.73% | 8.77% | +4.96pp | -32.30% | 5.53x | 0.425 |
| US B4-v2 35/40/25 | 100 bps/yr | 13.16% | 8.77% | +4.39pp | -32.93% | 4.57x | 0.400 |
| US B4-v2 35/40/25 | 150 bps/yr | 12.60% | 8.77% | +3.83pp | -33.55% | 3.77x | 0.375 |


## US Named-Regime Stress

Analysis: The US core improves materially over SPY in the dot-com bust, GFC, Covid crash and 2022 rates shock. The weak spot is the recent recovery, where SPY rebounds harder and the core trails by `3.18pp`.

Conclusion: The core is a crisis-dampening design, not a maximum-beta recovery vehicle. That is consistent with the role of managed futures, gold and long-duration exposure.

| Regime | Window | Portfolio | Return | Bench return | Spread | MDD | Bench MDD |
|---|---|---|---|---|---|---|---|
| Dot-com bust | 2000-03-24..2002-10-09 | B4-v2 35/40/25 | -18.88% | -47.38% | +28.50pp | -29.94% | -47.38% |
| Dot-com bust | 2000-03-24..2002-10-09 | B4 original 25/25/25/25 | -18.56% | -47.38% | +28.82pp | -28.14% | -47.38% |
| GFC | 2007-10-09..2009-03-09 | B4-v2 35/40/25 | -13.76% | -55.14% | +41.38pp | -28.02% | -55.14% |
| GFC | 2007-10-09..2009-03-09 | B4 original 25/25/25/25 | -19.28% | -55.14% | +35.86pp | -27.25% | -55.14% |
| Covid crash | 2020-02-19..2020-03-23 | B4-v2 35/40/25 | -17.21% | -33.69% | +16.49pp | -20.00% | -33.69% |
| Covid crash | 2020-02-19..2020-03-23 | B4 original 25/25/25/25 | -17.62% | -33.69% | +16.07pp | -19.88% | -33.69% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | B4-v2 35/40/25 | -17.01% | -24.21% | +7.21pp | -20.90% | -24.44% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | B4 original 25/25/25/25 | -23.32% | -24.21% | +0.90pp | -23.65% | -24.44% |
| Recent recovery | 2022-10-14..2026-04-17 | B4-v2 35/40/25 | 105.62% | 108.80% | -3.18pp | -14.41% | -18.74% |
| Recent recovery | 2022-10-14..2026-04-17 | B4 original 25/25/25/25 | 92.33% | 108.80% | -16.47pp | -14.03% | -18.74% |


## US Implementation Named-Regime Stress

Analysis: Implementation variants also reduce crash-period losses versus SPY, but each additional sleeve split or RSSX allocation worsens the Covid and 2022 drawdowns relative to the simple core. In the recent recovery, all variants trail SPY, with RSSX-heavy rows trailing most.

Conclusion: The implementation variants add complexity and return potential, but the simple core has the cleaner regime profile.

| Regime | Window | Portfolio | Return | Bench return | Spread | MDD | Bench MDD |
|---|---|---|---|---|---|---|---|
| Covid crash | 2020-02-19..2020-03-23 | 35/40/25 core | -17.21% | -33.69% | +16.49pp | -20.00% | -33.69% |
| Covid crash | 2020-02-19..2020-03-23 | 35/20/20/25 MF split | -20.89% | -33.69% | +12.80pp | -23.45% | -33.69% |
| Covid crash | 2020-02-19..2020-03-23 | 10% RSSX + MF split | -21.89% | -33.69% | +11.81pp | -24.28% | -33.69% |
| Covid crash | 2020-02-19..2020-03-23 | 17.5% RSSX + MF split | -22.63% | -33.69% | +11.06pp | -24.90% | -33.69% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | 35/40/25 core | -17.01% | -24.21% | +7.21pp | -20.90% | -24.44% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | 35/20/20/25 MF split | -19.22% | -24.21% | +5.00pp | -21.82% | -24.44% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | 10% RSSX + MF split | -21.41% | -24.21% | +2.80pp | -23.68% | -24.44% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | 17.5% RSSX + MF split | -23.04% | -24.21% | +1.18pp | -25.06% | -24.44% |
| Recent recovery | 2022-10-14..2026-05-21 | 35/40/25 core | 109.71% | 118.40% | -8.69pp | -14.41% | -18.74% |
| Recent recovery | 2022-10-14..2026-05-21 | 35/20/20/25 MF split | 113.48% | 118.40% | -4.92pp | -15.29% | -18.74% |
| Recent recovery | 2022-10-14..2026-05-21 | 10% RSSX + MF split | 106.40% | 118.40% | -12.01pp | -16.07% | -18.74% |
| Recent recovery | 2022-10-14..2026-05-21 | 17.5% RSSX + MF split | 101.17% | 118.40% | -17.23pp | -16.73% | -18.74% |


## Global Named-Regime Stress vs 66/34

Analysis: Global variants improve outcomes across the large stress regimes versus `66/34`, especially GFC and Covid. The cost appears in the recent recovery, where global rows lag the benchmark by large margins.

Conclusion: The global designs are defensive and diversifying, but they can lag badly when US/global equities rebound strongly. That trade-off must be explicit.

| Regime | Window | Portfolio | Return | Bench return | Spread | MDD | Bench MDD |
|---|---|---|---|---|---|---|---|
| Dot-com bust | 2000-03-24..2002-10-09 | Global simple NTSD/RSIT | -27.91% | -48.34% | +20.43pp | -34.35% | -48.34% |
| Dot-com bust | 2000-03-24..2002-10-09 | Global 66/34 lead | -21.70% | -48.34% | +26.64pp | -29.91% | -48.34% |
| Dot-com bust | 2000-03-24..2002-10-09 | Global 60/40 lead | -21.55% | -48.34% | +26.78pp | -29.41% | -48.34% |
| Dot-com bust | 2000-03-24..2002-10-09 | US B4-v2 35/40/25 | -21.81% | -48.34% | +26.53pp | -31.66% | -48.34% |
| GFC | 2007-10-09..2009-03-09 | Global simple NTSD/RSIT | -25.68% | -56.90% | +31.22pp | -33.79% | -56.92% |
| GFC | 2007-10-09..2009-03-09 | Global 66/34 lead | -17.48% | -56.90% | +39.42pp | -30.54% | -56.92% |
| GFC | 2007-10-09..2009-03-09 | Global 60/40 lead | -18.54% | -56.90% | +38.36pp | -30.95% | -56.92% |
| GFC | 2007-10-09..2009-03-09 | US B4-v2 35/40/25 | -14.50% | -56.90% | +42.40pp | -28.20% | -56.92% |
| Covid crash | 2020-02-19..2020-03-23 | Global simple NTSD/RSIT | -19.59% | -34.68% | +15.08pp | -22.18% | -34.68% |
| Covid crash | 2020-02-19..2020-03-23 | Global 66/34 lead | -16.60% | -34.68% | +18.07pp | -19.95% | -34.68% |
| Covid crash | 2020-02-19..2020-03-23 | Global 60/40 lead | -16.31% | -34.68% | +18.37pp | -19.76% | -34.68% |
| Covid crash | 2020-02-19..2020-03-23 | US B4-v2 35/40/25 | -17.23% | -34.68% | +17.45pp | -20.02% | -34.68% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global simple NTSD/RSIT | -19.49% | -26.20% | +6.72pp | -21.83% | -26.32% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global 66/34 lead | -18.41% | -26.20% | +7.79pp | -21.16% | -26.32% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global 60/40 lead | -18.77% | -26.20% | +7.44pp | -21.01% | -26.32% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | US B4-v2 35/40/25 | -17.40% | -26.20% | +8.80pp | -21.26% | -26.32% |
| Recent recovery | 2022-10-14..2026-05-21 | Global simple NTSD/RSIT | 83.32% | 116.37% | -33.05pp | -16.18% | -16.62% |
| Recent recovery | 2022-10-14..2026-05-21 | Global 66/34 lead | 80.39% | 116.37% | -35.98pp | -14.73% | -16.62% |
| Recent recovery | 2022-10-14..2026-05-21 | Global 60/40 lead | 73.13% | 116.37% | -43.24pp | -15.23% | -16.62% |
| Recent recovery | 2022-10-14..2026-05-21 | US B4-v2 35/40/25 | 96.52% | 116.37% | -19.85pp | -14.60% | -16.62% |


## Global Named-Regime Stress vs 100% VT

Analysis: The same regime pattern holds versus VT: strong crisis protection, weaker recent recovery capture. `Global 66/34 lead` and `Global 60/40 lead` show the cleanest crisis drawdowns, while RSC-US keeps better recovery participation.

Conclusion: Global variants are best framed as drawdown-control portfolios. If the user wants maximum recovery capture, the US core remains superior.

| Regime | Window | Portfolio | Return | Bench return | Spread | MDD | Bench MDD |
|---|---|---|---|---|---|---|---|
| Dot-com bust | 2000-03-24..2002-10-09 | 66/34 VTI/VEA | -48.34% | -48.04% | -0.30pp | -48.34% | -48.04% |
| Dot-com bust | 2000-03-24..2002-10-09 | Global simple NTSD/RSIT | -27.91% | -48.04% | +20.13pp | -34.35% | -48.04% |
| Dot-com bust | 2000-03-24..2002-10-09 | Global 66/34 lead | -21.70% | -48.04% | +26.33pp | -29.91% | -48.04% |
| Dot-com bust | 2000-03-24..2002-10-09 | Global 60/40 lead | -21.55% | -48.04% | +26.48pp | -29.41% | -48.04% |
| Dot-com bust | 2000-03-24..2002-10-09 | US B4-v2 35/40/25 | -21.81% | -48.04% | +26.23pp | -31.66% | -48.04% |
| GFC | 2007-10-09..2009-03-09 | 66/34 VTI/VEA | -56.90% | -57.78% | +0.88pp | -56.92% | -58.35% |
| GFC | 2007-10-09..2009-03-09 | Global simple NTSD/RSIT | -25.68% | -57.78% | +32.10pp | -33.79% | -58.35% |
| GFC | 2007-10-09..2009-03-09 | Global 66/34 lead | -17.48% | -57.78% | +40.30pp | -30.54% | -58.35% |
| GFC | 2007-10-09..2009-03-09 | Global 60/40 lead | -18.54% | -57.78% | +39.24pp | -30.95% | -58.35% |
| GFC | 2007-10-09..2009-03-09 | US B4-v2 35/40/25 | -14.50% | -57.78% | +43.28pp | -28.20% | -58.35% |
| Covid crash | 2020-02-19..2020-03-23 | 66/34 VTI/VEA | -34.68% | -34.10% | -0.58pp | -34.68% | -34.10% |
| Covid crash | 2020-02-19..2020-03-23 | Global simple NTSD/RSIT | -19.59% | -34.10% | +14.51pp | -22.18% | -34.10% |
| Covid crash | 2020-02-19..2020-03-23 | Global 66/34 lead | -16.60% | -34.10% | +17.49pp | -19.95% | -34.10% |
| Covid crash | 2020-02-19..2020-03-23 | Global 60/40 lead | -16.31% | -34.10% | +17.79pp | -19.76% | -34.10% |
| Covid crash | 2020-02-19..2020-03-23 | US B4-v2 35/40/25 | -17.23% | -34.10% | +16.87pp | -20.02% | -34.10% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | 66/34 VTI/VEA | -26.20% | -26.09% | -0.11pp | -26.32% | -26.13% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global simple NTSD/RSIT | -19.49% | -26.09% | +6.60pp | -21.83% | -26.13% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global 66/34 lead | -18.41% | -26.09% | +7.68pp | -21.16% | -26.13% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | Global 60/40 lead | -18.77% | -26.09% | +7.32pp | -21.01% | -26.13% |
| Inflation/rates shock | 2022-01-03..2022-10-14 | US B4-v2 35/40/25 | -17.40% | -26.09% | +8.69pp | -21.26% | -26.13% |
| Recent recovery | 2022-10-14..2026-05-21 | 66/34 VTI/VEA | 116.37% | 112.44% | +3.93pp | -16.62% | -16.50% |
| Recent recovery | 2022-10-14..2026-05-21 | Global simple NTSD/RSIT | 83.32% | 112.44% | -29.12pp | -16.18% | -16.50% |
| Recent recovery | 2022-10-14..2026-05-21 | Global 66/34 lead | 80.39% | 112.44% | -32.05pp | -14.73% | -16.50% |
| Recent recovery | 2022-10-14..2026-05-21 | Global 60/40 lead | 73.13% | 112.44% | -39.31pp | -15.23% | -16.50% |
| Recent recovery | 2022-10-14..2026-05-21 | US B4-v2 35/40/25 | 96.52% | 112.44% | -15.92pp | -14.60% | -16.50% |


## US Monte Carlo Sequence-Risk Summary

Analysis: The 20-year block Monte Carlo shows much stronger p10 and median terminal wealth for RSC-US than SPY, with lower median max drawdown. The probability of terminal wealth below SPY is `6.2%` for the core, which is low but not zero.

Conclusion: Sequence-risk evidence supports the US core, but it is a diagnostic simulation, not formal proof of future superiority.

| Portfolio | Paths | Years | Terminal p10 | Terminal median | Terminal p90 | CAGR p10 | CAGR median | MDD median | Prob < bench |
|---|---|---|---|---|---|---|---|---|---|
| 100% SPY | 1000 | 20 | 3.17x | 7.93x | 19.91x | 5.93% | 10.91% | -35.62% | n/a |
| B4-v2 35/40/25 | 1000 | 20 | 7.91x | 18.81x | 39.90x | 10.89% | 15.80% | -24.49% | 6.2% |
| B4 original 25/25/25/25 | 1000 | 20 | 6.49x | 14.26x | 29.25x | 9.80% | 14.21% | -23.95% | 11.2% |


## Global Monte Carlo Sequence-Risk Summary

Analysis: Global variants also improve p10 terminal wealth and median drawdown versus `66/34`, but underperformance probabilities are higher than the US core. RSC-US remains the strongest Monte Carlo candidate in this table.

Conclusion: Global Monte Carlo results support diversification, not replacement. The global rows are viable if drawdown smoothing and geographic breadth are worth lower expected terminal wealth.

| Portfolio | Paths | Years | Terminal p10 | Terminal median | Terminal p90 | CAGR p10 | CAGR median | MDD median | Prob < bench |
|---|---|---|---|---|---|---|---|---|---|
| 66/34 VTI/VEA | 1000 | 20 | 2.59x | 6.68x | 17.03x | 4.87% | 9.96% | -37.61% | n/a |
| Global simple NTSD/RSIT | 1000 | 20 | 5.26x | 11.59x | 25.93x | 8.65% | 13.03% | -27.82% | 11.3% |
| Global 66/34 lead | 1000 | 20 | 5.36x | 11.21x | 24.75x | 8.76% | 12.85% | -26.11% | 14.7% |
| Global 60/40 lead | 1000 | 20 | 4.92x | 10.40x | 22.78x | 8.29% | 12.42% | -26.39% | 17.8% |
| US B4-v2 35/40/25 | 1000 | 20 | 6.68x | 14.45x | 31.93x | 9.96% | 14.29% | -25.73% | 7.8% |


## Data Blockers And Next Execution Step

Analysis: The blocked checks are not failed robustness tests; they are data-granularity limitations. Exact rebalance frequency, remove-one-sleeve and threshold-band analysis require daily constituent or sleeve return series, not just completed portfolio equity curves.

Conclusion: The next useful engineering artifact is a canonical sleeve-return matrix. Once that exists, this report can be rerun with exact implementation sensitivity instead of approximations.

| Check | Status | Reason | Required artifact |
|---|---|---|---|
| Rebalance frequency: monthly vs quarterly/semiannual/annual | Blocked | Current RSC exports store portfolio equity curves, not all underlying sleeve daily returns for each implementation variant. | Aligned daily return matrix for `GDE`, `RSST`, `ZROZ`, `CTAP`, `RSSX_RP`, `NTSD`, `RSIT`, `NTSI`, `VTI/VEA/VT`. |
| Remove-one-sleeve test | Blocked | Cannot recompute portfolio without a sleeve from only final equity curves. | Same aligned sleeve return matrix plus rebalance engine. |
| Exact rebalance threshold/tolerance bands | Blocked | Requires constituent-level drift and rebalance logic. | Same aligned sleeve return matrix plus weight-drift simulator. |

Recommended next step: export a canonical `return_stacked_core_sleeve_returns.parquet` with all sleeves used in US and global variants, then rerun this report with exact rebalance and remove-one sections.
