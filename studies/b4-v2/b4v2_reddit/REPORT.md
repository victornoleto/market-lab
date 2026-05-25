# B4-v2 RSSX Risk-Parity Proxy Results

Status: discovery-only support for the Reddit post. This does not authorize deployment or change the mandate.

## Method

`RSSX_RP = 100% SPY + 100% Gold/BTC risk-parity sleeve - 100% CASHX - 0.67% ER`.

The Gold/BTC sleeve uses 63-trading-day lagged realized volatility. BTC receives its inverse-volatility risk-parity weight, clipped to `5%..25%`; Gold receives the rest. Weights are held monthly. This approximates RSSX's prospectus-level economics, not the proprietary live implementation `[risk_parity, p.80-81]`, `[advances_fin_ml, p.208-211]`.

BTC nerf scenarios shift BTC log-return drift to target CAGRs while preserving the historical volatility/crash path. This avoids relying on the non-repeatable 2010-2026 BTC adoption ramp `[testing_tuning, p.327-335]`.

## Canonical 1988 Context

| Portfolio               | Window                 | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:------------------------|:-----------------------|:-------|:--------|---------:|---------:|:-----------|
| 100% SPY                | 1988-01-04..2026-04-17 | 11.46% | -55.14% |    0.691 |    0.208 | 64x        |
| B4 original 25/25/25/25 | 1988-01-04..2026-04-17 | 14.43% | -27.92% |    1.018 |    0.517 | 174x       |
| B4-v2 35/40/25          | 1988-01-04..2026-04-17 | 15.70% | -29.94% |    1.04  |    0.524 | 265x       |

## Post-2010 Implementation Comparison

Common window is constrained by BTC and the 63-day volatility warmup. BTC scenario: `10%` target CAGR.

| Portfolio                                             | Window                 | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:------------------------------------------------------|:-----------------------|:-------|:--------|---------:|---------:|:-----------|
| 100% SPY                                              | 2010-10-18..2026-05-21 | 14.69% | -33.69% |    0.891 |    0.436 | 8.4x       |
| 35 GDE / 40 RSST / 25 ZROZ                            | 2010-10-18..2026-05-21 | 14.81% | -21.46% |    1.062 |    0.69  | 8.6x       |
| 35 GDE / 20 RSST / 20 CTAP / 25 ZROZ                  | 2010-10-18..2026-05-21 | 15.14% | -23.45% |    1.062 |    0.646 | 9.0x       |
| 25 GDE / 10 RSSX_RP / 20 RSST / 20 CTAP / 25 ZROZ     | 2010-10-18..2026-05-21 | 16.06% | -24.28% |    1.098 |    0.662 | 10.2x      |
| 17.5 GDE / 17.5 RSSX_RP / 20 RSST / 20 CTAP / 25 ZROZ | 2010-10-18..2026-05-21 | 16.73% | -25.28% |    1.115 |    0.662 | 11.1x      |

## Approximate Effective Exposure

| Version | US equity | MF Newfound | MF Simplify | Gold | BTC | ZROZ | Positive exposure | Gross leverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 35 GDE / 40 RSST / 25 ZROZ | 71.5% | 40.0% | 0.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| 35 GDE / 20 RSST / 20 CTAP / 25 ZROZ | 71.5% | 20.0% | 20.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| 25 GDE / 10 RSSX / 20 RSST / 20 CTAP / 25 ZROZ | 72.5% | 20.0% | 20.0% | 30.7% | 1.8% | 25.0% | 170.0% | 1.70x |
| 17.5 GDE / 17.5 RSSX / 20 RSST / 20 CTAP / 25 ZROZ | 73.3% | 20.0% | 20.0% | 30.2% | 3.1% | 25.0% | 171.5% | 1.72x |

## RSSX Replacement Grid

Keeps `40% RSST` and `25% ZROZ` fixed, replacing part of the `35% GDE` sleeve with `RSSX_RP`. BTC scenario: `10%` target CAGR.

| RSSX   | GDE   | CAGR   | MDD     |   Sharpe |   Calmar |
|:-------|:------|:-------|:--------|---------:|---------:|
| 0.0%   | 35.0% | 14.81% | -21.46% |    1.062 |    0.69  |
| 5.0%   | 30.0% | 15.27% | -22.44% |    1.083 |    0.681 |
| 10.0%  | 25.0% | 15.73% | -23.41% |    1.1   |    0.672 |
| 15.0%  | 20.0% | 16.18% | -24.37% |    1.113 |    0.664 |
| 17.5%  | 17.5% | 16.40% | -24.85% |    1.118 |    0.66  |
| 20.0%  | 15.0% | 16.61% | -25.37% |    1.122 |    0.655 |
| 25.0%  | 10.0% | 17.04% | -26.46% |    1.128 |    0.644 |
| 35.0%  | 0.0%  | 17.86% | -29.02% |    1.13  |    0.615 |

## BTC Drift Sensitivity

Portfolio: `25% GDE / 10% RSSX_RP / 20% RSST / 20% CTAP / 25% ZROZ`.

| BTC scenario   | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:---------------|:-------|:--------|---------:|---------:|:-----------|
| historical_btc | 17.65% | -24.21% |    1.191 |    0.729 | 12.6x      |
| btc_0          | 15.87% | -24.29% |    1.086 |    0.653 | 9.9x       |
| btc_6          | 15.99% | -24.29% |    1.093 |    0.658 | 10.1x      |
| btc_10         | 16.06% | -24.28% |    1.098 |    0.662 | 10.2x      |
| btc_14         | 16.14% | -24.28% |    1.102 |    0.665 | 10.3x      |

## RSSX_RP BTC Weight Diagnostics

| Scenario       | Window                 | BTC sleeve avg   | Portfolio BTC avg @10% RSSX   | Portfolio BTC avg @17.5% RSSX   | BTC sleeve p10   | BTC sleeve p90   |
|:---------------|:-----------------------|:-----------------|:------------------------------|:--------------------------------|:-----------------|:-----------------|
| historical_btc | 2010-10-18..2026-05-21 | 17.57%           | 1.76%                         | 3.07%                           | 9.02%            | 25.00%           |
| btc_0          | 2010-10-18..2026-05-21 | 17.61%           | 1.76%                         | 3.08%                           | 9.05%            | 25.00%           |
| btc_6          | 2010-10-18..2026-05-21 | 17.61%           | 1.76%                         | 3.08%                           | 9.05%            | 25.00%           |
| btc_10         | 2010-10-18..2026-05-21 | 17.60%           | 1.76%                         | 3.08%                           | 9.04%            | 25.00%           |
| btc_14         | 2010-10-18..2026-05-21 | 17.60%           | 1.76%                         | 3.08%                           | 9.04%            | 25.00%           |

## Reading

- The canonical 35/40/25 core remains the clean result and should lead the Reddit post.
- The risk-parity RSSX proxy keeps portfolio-level BTC exposure small. At `10% RSSX`, the average portfolio BTC notional is about `1.76%`; at `17.5% RSSX`, about `3.08%`.
- Under a nerfed `10%` BTC drift, `10% RSSX_RP` improves the post-2010 implementation table but does not dominate enough to become the central claim.
- `17.5% RSSX_RP` is a cleaner 50/50 GDE/RSSX sleeve split, but it is more BTC-convexity expression than mandatory portfolio improvement.
- The post should present RSSX as optional and explicitly reject raw historical BTC CAGR as a forward assumption.
- Monte Carlo sequence-risk simulation was added for the Reddit drafts: 1,000 paired 20-year paths via 21-trading-day block bootstrap. B4-v2 terminal wealth p10/median/p90 was `7.91x / 18.81x / 39.90x` with median MDD `-24.49%`; SPY was `3.17x / 7.93x / 19.91x` with median MDD `-35.62%`. This is a sequence-risk diagnostic, not a formal validation gate `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

## Plots

## Chart attachments

Suggested gallery order:

1. `plots/01_full_equity_log.png` - 1988+ equity curves: SPY vs B4 equal-weight vs B4-v2 35/40/25.
2. `plots/02_full_equity_vs_spy.png` - 1988+ relative wealth vs SPY.
3. `plots/03_implementation_equity_log.png` - post-2010 implementation variants, BTC drift nerfed to 10%.
4. `plots/04_implementation_equity_vs_spy.png` - post-2010 relative wealth vs SPY.
5. `plots/05_implementation_drawdowns.png` - post-2010 drawdowns.
6. `plots/06_rolling_relative_wealth_2x2.png` - 3/5/10/15-year rolling relative wealth vs SPY.
7. `plots/07_rolling_cagr_spread_2x2.png` - 3/5/10/15-year rolling CAGR spread vs SPY.
8. `plots/08_monte_carlo_20y_sequence_risk.png` - 20-year Monte Carlo sequence-risk simulation.

## Artifacts

- `metrics.csv`
- `rssx_weights.csv`
- `btc_weight_stats.csv`
- `monte_carlo_sequence_risk.csv`
