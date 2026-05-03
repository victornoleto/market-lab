# Iter 047 — Bitcoin sleeve on corrected B4

**Date:** 2026-05-03
**Source:** testfol.io API (`BTCSIM` for Bitcoin).
**Window:** common window determined by BTCSIM + corrected RSST proxy.
**Tax model:** no DARF applied; crypto ETF/ETP tax treatment and availability must be checked separately.

## Ranking By Sharpe

| # | strategy | window | CAGR | MDD | Sharpe | Calmar |
|---:|---|---|---:|---:|---:|---:|
| 1 | B4_btc10_from_zroz | 2010-07-19 -> 2026-05-01 (15.78y) | 30.30% | -29.85% | 1.453 | 1.015 |
| 2 | B4_btc5_from_zroz | 2010-07-19 -> 2026-05-01 (15.78y) | 22.01% | -27.90% | 1.311 | 0.789 |
| 3 | B4_btc5_from_rsst | 2010-07-19 -> 2026-05-01 (15.78y) | 21.29% | -30.25% | 1.305 | 0.704 |
| 4 | B4_btc5_from_ntsx | 2010-07-19 -> 2026-05-01 (15.78y) | 21.40% | -28.82% | 1.303 | 0.743 |
| 5 | B4_btc2p5_from_zroz | 2010-07-19 -> 2026-05-01 (15.78y) | 17.80% | -26.97% | 1.151 | 0.660 |
| 6 | B4_base | 2010-07-19 -> 2026-05-01 (15.78y) | 13.55% | -26.42% | 0.911 | 0.513 |
| 7 | SPY_1x | 2010-07-19 -> 2026-05-01 (15.78y) | 14.86% | -33.70% | 0.814 | 0.441 |

## Findings

Corrected B4 baseline in this Bitcoin-constrained window: 13.55% CAGR / -26.42% MDD / 0.911 Sharpe.

1. **Bitcoin sleeve massively improves realized CAGR/Sharpe in the available 2010+ window.** This is expected because the test starts near Bitcoin's early monetization phase. A 2.5% sleeve from ZROZ lifts CAGR from 13.55% to 17.80% while MDD worsens only from -26.42% to -26.97%. A 5% sleeve from ZROZ lifts CAGR to 22.01% with MDD -27.90%.

2. **Strict B4-dominance is not met because every BTC variant has slightly worse MDD than B4.** But the 2.5-5% sleeves are economically compelling if the investor accepts +0.55pp to +1.48pp MDD for +4.25pp to +8.46pp CAGR in this sample.

3. **10% BTC is too aggressive for a retirement core despite attractive backtest.** CAGR 30.30% is dominated by Bitcoin's historical path; this is not a robust expectation. Treat 10% as speculation-heavy, not baseline.

4. **Best practical crypto candidate:** `B4_btc2p5_from_zroz` or, if explicitly accepting a speculative sleeve, `B4_btc5_from_zroz`. Funding from ZROZ is better than funding from RSST/NTSX because it preserves the return-stacked core and uses the defensive sleeve as the risk budget donor.

## Caveats

- BTCSIM is spot Bitcoin simulation, not IBIT/BTGD live history.
- The window begins in 2010 and is structurally favorable to Bitcoin; it excludes any pre-adoption failure path. Do not extrapolate 17-30% CAGR as a forward expectation.
- Bitcoin has short history versus equities/bonds and extreme regime dependence.
- A 5-10% sleeve is a speculation sleeve; size must be capped ex ante. 2.5% is the cleaner retirement-compatible test size.
