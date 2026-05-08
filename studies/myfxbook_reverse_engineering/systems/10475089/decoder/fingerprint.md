# Decoder fingerprint — system 10475089

Generated: 2026-05-02T02:07:02

## Sanity (martingale + lot dynamics)

- n_trades: **117**, deposits: 2
- pairs: {'GBPJPY': 117}
- actions: {'Buy': 72, 'Sell': 45}
- date range: 2023-06-19 00:00:11+00:00 → 2024-07-17 10:23:50+00:00
- max gap days: 24.9
- lot p50/p95/p99/max: 186.14 / 203.12 / 205.71 / 207.66
- lot p95/p50 ratio: 1.09
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 66.47 / 627.89 / 870.73

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 00:00 — 114 trades
  - 17:00 — 1 trades
  - 14:00 — 1 trades
  - 08:00 — 1 trades
  - 04:00 — 0 trades

Top entry hour:5min (UTC):
  - 00:00 — 114 trades
  - 08:50 — 1 trades
  - 14:45 — 1 trades
  - 17:00 — 1 trades

Exit kind distribution:
  - manual_or_time: 117

Direction by pair (Buy %):
  - GBPJPY: total=117, buy_pct=61.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=00: total=114, buy_pct=61.4%
  - hour=08: total=1, buy_pct=100.0%
  - hour=14: total=1, buy_pct=0.0%
  - hour=17: total=1, buy_pct=100.0%

## Feature extraction

- trades processed: 117
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.6154); Always-Sell = 0.3846 | 0.615 | — | 1.00 | — |
| 2 | univariate | ret_1_M1 > -0.0001779 ⇒ Buy | 0.650 | — | 0.79 | 0.392 |
| 3 | univariate | bb_pos_20_2_M5 > -0.5978 ⇒ Buy | 0.650 | — | 0.79 | 0.392 |
| 4 | univariate | ret_3_M15 > -0.0004039 ⇒ Buy | 0.650 | — | 0.79 | 0.392 |
| 5 | univariate | ret_1_M5 > -0.0003289 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |
| 6 | univariate | ret_3_M5 > -0.0003022 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |
| 7 | univariate | ret_10_M5 > -0.0003447 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |
| 8 | univariate | ema_dist_20_M5 > -0.9764 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |
| 9 | univariate | ema_dist_20_M15 > -0.7894 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |
| 10 | univariate | bb_pos_20_2_M15 > -0.5878 ⇒ Buy | 0.632 | — | 0.79 | 1.000 |

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
