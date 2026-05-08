# LETF Threshold Sweep — T3d K=2 with hysteresis buffers

_Generated 2026-05-07T04:17:42.367523+00:00_

Spec: `docs/superpowers/specs/2026-05-07-letf-threshold-sweep-design.md`

## 1. Methodology

- Universe: 12 variants of `qld_vote_k2_off_zroz` (canonical T3d K=2)
- Track A threshold (gross Sharpe): **0.903** (canonical 0.853 + 0.05)
- Track B M1 threshold (per-swing 15%): **0.737** (canonical 0.687 + 0.05)
- Track B M2 threshold (annual 15%): **0.818** (canonical 0.768 + 0.05)

## 2. Track A — Gross results

![Gross Sharpe](threshold_sweep/sharpe_bar_gross.png)

| name                 |   gross_sharpe |   gross_cagr |   gross_mdd |   trade_count_m1 |   gross_edge_vs_canonical | track_a_pass   |
|:---------------------|---------------:|-------------:|------------:|-----------------:|--------------------------:|:---------------|
| t3d_k2_baseline      |          0.853 |        0.279 |      -0.749 |              206 |                     0.000 | False          |
| t3d_k2_smabuf_05pct  |          0.865 |        0.285 |      -0.714 |              194 |                     0.012 | False          |
| t3d_k2_smabuf_1pct   |          0.845 |        0.275 |      -0.697 |              184 |                    -0.008 | False          |
| t3d_k2_smabuf_2pct   |          0.838 |        0.272 |      -0.739 |              174 |                    -0.015 | False          |
| t3d_k2_smabuf_3pct   |          0.852 |        0.279 |      -0.695 |              167 |                    -0.001 | False          |
| t3d_k2_smabuf_5pct   |          0.903 |        0.303 |      -0.700 |              145 |                     0.050 | False          |
| t3d_k2_hyst_2on_0off |          0.865 |        0.282 |      -0.741 |              196 |                     0.012 | False          |
| t3d_k2_hyst_3on_0off |          0.869 |        0.283 |      -0.679 |              192 |                     0.016 | False          |
| t3d_k2_hyst_5on_0off |          0.895 |        0.294 |      -0.655 |              181 |                     0.042 | False          |
| t3d_k2_ar1buf_05     |          0.808 |        0.256 |      -0.697 |              211 |                    -0.045 | False          |
| t3d_k2_ar1buf_10     |          0.835 |        0.264 |      -0.593 |              216 |                    -0.018 | False          |
| t3d_k2_ar1buf_15     |          0.838 |        0.262 |      -0.545 |              202 |                    -0.015 | False          |

**Track A winners: 0 of 12** (Sharpe ≥ 0.903).

## 3. Track B — Net results (M1 / M2)

![Net M1 Sharpe](threshold_sweep/sharpe_bar_net_m1.png)

![Net M2 Sharpe](threshold_sweep/sharpe_bar_net_m2.png)

![Trade count](threshold_sweep/trade_count_bar.png)

| name                 |   m1_sharpe |   m2_sharpe |   trade_count_m1 |   m1_edge_vs_canonical |   m2_edge_vs_canonical | track_b_m1_pass   | track_b_m2_pass   |
|:---------------------|------------:|------------:|-----------------:|-----------------------:|-----------------------:|:------------------|:------------------|
| t3d_k2_baseline      |       0.687 |       0.768 |              206 |                  0.000 |                  0.000 | False             | False             |
| t3d_k2_smabuf_05pct  |       0.702 |       0.779 |              194 |                  0.015 |                  0.011 | False             | False             |
| t3d_k2_smabuf_1pct   |       0.687 |       0.762 |              184 |                  0.000 |                 -0.006 | False             | False             |
| t3d_k2_smabuf_2pct   |       0.683 |       0.755 |              174 |                 -0.004 |                 -0.013 | False             | False             |
| t3d_k2_smabuf_3pct   |       0.701 |       0.768 |              167 |                  0.014 |                 -0.000 | False             | False             |
| t3d_k2_smabuf_5pct   |       0.759 |       0.812 |              145 |                  0.072 |                  0.044 | True              | False             |
| t3d_k2_hyst_2on_0off |       0.700 |       0.777 |              196 |                  0.013 |                  0.009 | False             | False             |
| t3d_k2_hyst_3on_0off |       0.704 |       0.781 |              192 |                  0.017 |                  0.013 | False             | False             |
| t3d_k2_hyst_5on_0off |       0.734 |       0.804 |              181 |                  0.047 |                  0.036 | False             | False             |
| t3d_k2_ar1buf_05     |       0.643 |       0.729 |              211 |                 -0.044 |                 -0.039 | False             | False             |
| t3d_k2_ar1buf_10     |       0.666 |       0.752 |              216 |                 -0.021 |                 -0.016 | False             | False             |
| t3d_k2_ar1buf_15     |       0.672 |       0.754 |              202 |                 -0.015 |                 -0.014 | False             | False             |

**Track B-M1 winners: 1 of 12** (M1 Sharpe ≥ 0.737).
**Track B-M2 winners: 0 of 12** (M2 Sharpe ≥ 0.818).

## 4. Synthesis

![Equity overlay top-4](threshold_sweep/equity_overlay_top4.png)

**Track B only:** ['t3d_k2_smabuf_5pct'] — net deploy improvement, gross neutral. Document but do NOT replace canonical (per spec §3.3).

## Citations

- `[trading_systems_methods, Kaufman ch.6, ch.21]` — signal smoothing, regime sensitivity.
- `[systematic_trading, Carver p.122-133, p.174]` — EWMAC smoothing, asymmetric exit.
- `[advances_fin_ml, p.208-211, p.275]` — CSCV PBO, deflated SR.
- Parent: `STUDY_FINAL_REPORT.md` §3.4.