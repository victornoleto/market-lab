# Decoder fingerprint — system 10716398

Generated: 2026-05-02T02:40:00

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'USDJPY': 1224, 'GBPUSD': 662, 'EURUSD': 493, 'EURJPY': 465, 'USDCAD': 386, 'USDCHF': 293, 'AUDUSD': 174, 'EURGBP': 163, 'EURCHF': 140}
- actions: {'Buy': 2001, 'Sell': 1999}
- date range: 2024-07-19 08:45:00+00:00 → 2026-05-01 09:55:32+00:00
- max gap days: 2.8
- lot p50/p95/p99/max: 1.37 / 173.65 / 177.39 / 178.78
- lot p95/p50 ratio: 126.96
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 139.40 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 3.39 / 311.92 / 8134.39

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 522 trades
  - 10:00 — 325 trades
  - 18:00 — 270 trades
  - 17:00 — 251 trades
  - 15:00 — 236 trades

Top entry hour:5min (UTC):
  - 03:00 — 297 trades
  - 18:35 — 64 trades
  - 15:35 — 51 trades
  - 19:35 — 51 trades
  - 10:15 — 40 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - AUDUSD: total=174, buy_pct=24.7%
  - EURCHF: total=140, buy_pct=62.1%
  - EURGBP: total=163, buy_pct=47.9%
  - EURJPY: total=465, buy_pct=55.5%
  - EURUSD: total=493, buy_pct=50.5%
  - GBPUSD: total=662, buy_pct=60.1%
  - USDCAD: total=386, buy_pct=46.9%
  - USDCHF: total=293, buy_pct=40.6%
  - USDJPY: total=1224, buy_pct=48.0%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=522, buy_pct=48.9%
  - hour=10: total=325, buy_pct=53.2%
  - hour=18: total=270, buy_pct=46.3%
  - hour=17: total=251, buy_pct=47.0%
  - hour=15: total=236, buy_pct=47.5%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.48, ema_dist_20_H4=0.20, atr_ratio_M15=0.09, atr_ratio_M5=0.05, ema_... | 0.569 | 0.015 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M15=1.0^bb_pos_20_2_H1=>0.96^hour_utc=8.0-10.0]] | 0.531 | 0.032 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.5002); Always-Sell = 0.4998 | 0.500 | — | 1.00 | — |
| 4 | univariate | ret_10_M15 > -0.0005766 ⇒ Buy | 0.546 | — | 0.70 | 0.000 |
| 5 | univariate | ema_dist_20_M15 > -0.2199 ⇒ Buy | 0.571 | — | 0.60 | 0.000 |
| 6 | univariate | ret_3_H4 > -0.0006963 ⇒ Buy | 0.569 | — | 0.60 | 0.000 |
| 7 | univariate | ema_dist_20_H1 > -0.369 ⇒ Buy | 0.566 | — | 0.60 | 0.000 |
| 8 | univariate | close_vs_session_open_H1 > -1 ⇒ Buy | 0.567 | — | 0.57 | 0.000 |
| 9 | univariate | bb_pos_20_2_M15 > 0.06628 ⇒ Buy | 0.579 | — | 0.50 | 0.000 |
| 10 | univariate | close_vs_session_open_M15 > -1 ⇒ Buy | 0.564 | — | 0.53 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.48, ema_dist_20_H4=0.20, atr_ratio_M15=0.09, atr_ratio_M5=0.05, ema_dist_20_H1=0.04

|--- bb_pos_20_2_H1 <= 0.54
|   |--- bb_pos_20_2_H1 <= -0.63
|   |   |--- bb_pos_20_2_H1 <= -1.20
|   |   |   |--- ret_1_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_H1 >  -1.20
|   |   |   |--- ret_3_M15 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_M15 >  0.00
|   |   |   |   |--- class: 0
|   |--- bb_pos_20_2_H1 >  -0.63
|   |   |--- ema_dist_20_H4 <= 0.15
|   |   |   |--- atr_ratio_M15 <= 0.55
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M15 >  0.55
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H4 >  0.15
|   |   |   |--- ret_3_H1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H1 >  0.00
|   |   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  0.54
|   |--- ema_dist_20_H4 <= 2.35
|   |   |--- ema_dist_20_H1 <= 1.91
|   |   |   |--- bb_pos_20_2_M15 <= 0.69
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M15 >  0.69
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  1.91
|   |   |   |--- bb_pos_20_2_H1 <= 0.91
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_H1 >  0.91
|   |   |   |   |--- class: 1
|   |--- ema_dist_20_H4 >  2.35
|   |   |--- atr_ratio_M5 <= 0.39
|   |   |   |--- ret_1_M15 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_M15 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M5 >  0.39
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M15=1.0^bb_pos_20_2_H1=>0.96^hour_utc=8.0-10.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
