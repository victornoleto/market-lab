# Iter 056 — `b4-reallocation-combined-scv-momentum-btc`

**Date:** 2026-05-05
**Engine:** testfol.io API
**Primary citation:** [risk_parity, ch.5, p.10] capital-efficient stacking + [risk_parity, ch.2, p.37-41] Fama-French SCV + [stocks_on_the_move, p.21-30] Clenow momentum

**Selected:** `P4b_btgd_10pct_reduce_gde` (10/10/10 with BTGD; GDE 20 (BTGD gold overlap))
  CAGR 20.48% / MDD -32.97% / Sharpe 1.017 on 2015-10-12 -> 2026-05-04 (10.56y)

## Ranking by Sharpe

| # | slug | window | CAGR | MDD | Sharpe | Calmar | drag |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `P4b_btgd_10pct_reduce_gde` | 2015-10-12 -> 2026-05-04 (10.56y) | 20.48% | -32.97% | 1.017 | 0.621 | 0.355% |
| 2 | `P3a_combo_spmo_btc` | 2015-10-12 -> 2026-05-04 (10.56y) | 20.99% | -34.30% | 1.006 | 0.612 | 0.323% |
| 3 | `P3b_combo_mtum_btc` | 2015-10-12 -> 2026-05-04 (10.56y) | 20.65% | -34.61% | 0.985 | 0.597 | 0.325% |
| 4 | `P2_B4_btc5_spot` | 2015-10-12 -> 2026-05-04 (10.56y) | 17.37% | -28.49% | 0.970 | 0.610 | 0.390% |
| 5 | `P5b_rssx_10pct_reduce_ntsx` | 2015-10-12 -> 2026-05-04 (10.56y) | 20.92% | -35.76% | 0.965 | 0.585 | 0.406% |
| 6 | `P4a_btgd_5pct` | 2015-10-12 -> 2026-05-04 (10.56y) | 19.11% | -33.51% | 0.942 | 0.570 | 0.338% |
| 7 | `P5a_rssx_5pct` | 2015-10-12 -> 2026-05-04 (10.56y) | 19.02% | -34.77% | 0.908 | 0.547 | 0.363% |
| 8 | `P3c_combo_no_btc` | 2015-10-12 -> 2026-05-04 (10.56y) | 16.38% | -31.88% | 0.838 | 0.514 | 0.318% |
| 9 | `P1_B4_base` | 2015-10-12 -> 2026-05-04 (10.56y) | 12.82% | -26.95% | 0.745 | 0.476 | 0.385% |
| 10 | `SPY_1x` | 2015-10-12 -> 2026-05-04 (10.56y) | 14.67% | -33.70% | 0.737 | 0.435 | 0.095% |

## % rolling-windows beating `SPY_1x` (Sharpe-strat > Sharpe-bench)

| slug | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| `P4b_btgd_10pct_reduce_gde` | 98.5% | 100.0% | 100.0% | n/a |
| `P3a_combo_spmo_btc` | 98.3% | 100.0% | 100.0% | n/a |
| `P3b_combo_mtum_btc` | 96.0% | 100.0% | 100.0% | n/a |
| `P2_B4_btc5_spot` | 65.1% | 80.3% | 100.0% | n/a |
| `P5b_rssx_10pct_reduce_ntsx` | 97.2% | 100.0% | 100.0% | n/a |
| `P4a_btgd_5pct` | 96.9% | 100.0% | 100.0% | n/a |
| `P5a_rssx_5pct` | 93.5% | 100.0% | 100.0% | n/a |
| `P3c_combo_no_btc` | 66.0% | 95.9% | 100.0% | n/a |
| `P1_B4_base` | 40.8% | 64.4% | 91.9% | n/a |
| `SPY_1x` | 0.0% | 0.0% | 0.0% | n/a |

## Caveats / INCOMPLETE flags

- BTGD synth uses spot BTC + spot Gold; real BTGD uses futures (roll cost ~3-5%/y in contango).
- RSSX synth: 100% SPY + 100% (Gold 0.65 + BTC 0.35 by inverse-vol) − 1% borrow. Inverse-vol weights are a 2026-05-05 snapshot — they drift with realized vol. Gold/BTC futures roll cost not modeled.
- IDMO/SPMO momentum overlay NOT modeled in static drag (uses real ETF history, limited to inception).
- AVUV/AVDV/AVEM tilts injected via constant negative drag per literature midpoints (75/100/125bps); real Avantis ER + tilt may differ in execution.
- AVNM synth blends VEASIM + VWOSIM at market-cap; ignores Avantis profitability + value tilts proprietary to AVNM.

## Lesson

(Append after manual review.)
