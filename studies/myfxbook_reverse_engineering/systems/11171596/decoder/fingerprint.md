# Decoder fingerprint — system 11171596

Generated: 2026-05-02T03:10:08

## Sanity (martingale + lot dynamics)

- n_trades: **1083**, deposits: 1
- pairs: {'EURUSD': 542, 'USDCHF': 541}
- actions: {'Sell': 1083}
- date range: 2024-03-15 15:34:12+00:00 → 2026-03-13 10:18:14+00:00
- max gap days: 8.0
- lot p50/p95/p99/max: 1.02 / 1.17 / 1.19 / 1.20
- lot p95/p50 ratio: 1.15
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 23.33 / 560.65 / 1782.09

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 13:00 — 591 trades
  - 15:00 — 54 trades
  - 16:00 — 54 trades
  - 14:00 — 46 trades
  - 17:00 — 42 trades

Top entry hour:5min (UTC):
  - 13:00 — 537 trades
  - 13:05 — 12 trades
  - 13:40 — 12 trades
  - 15:30 — 12 trades
  - 16:30 — 12 trades

Exit kind distribution:
  - manual_or_time: 1083

Direction by pair (Buy %):
  - EURUSD: total=542, buy_pct=0.0%
  - USDCHF: total=541, buy_pct=0.0%

Direction by hour (Buy %, top 5 by activity):
  - hour=13: total=591, buy_pct=0.0%
  - hour=15: total=54, buy_pct=0.0%
  - hour=16: total=54, buy_pct=0.0%
  - hour=14: total=46, buy_pct=0.0%
  - hour=17: total=42, buy_pct=0.0%

## Feature extraction

- trades processed: 1083
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.0000); Always-Sell = 1.0000 | 1.000 | — | 1.00 | — |
| 2 | univariate | dow > 0 ⇒ Sell | 0.804 | — | 0.80 | 0.000 |
| 3 | univariate | ret_1_M1 > -9.634e-05 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 4 | univariate | ret_3_M1 > -0.000182 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 5 | univariate | ret_10_M1 > -0.0003248 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 6 | univariate | ema_dist_20_M1 > -1.197 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 7 | univariate | atr_ratio_M1 > 0.1005 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 8 | univariate | bb_pos_20_2_M1 > -0.6141 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 9 | univariate | range_norm_M1 > 0.6474 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |
| 10 | univariate | ret_1_M5 > -0.0002109 ⇒ Sell | 0.800 | — | 0.80 | 0.000 |

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
