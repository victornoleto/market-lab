# Decoder fingerprint — system 8599392

Generated: 2026-05-02T10:16:53

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'GBPUSD': 1142, 'EURUSD': 914, 'USDCAD': 654, 'AUDUSD': 533, 'EURCHF': 509, 'EURGBP': 248}
- actions: {'Buy': 2114, 'Sell': 1886}
- date range: 2023-11-22 17:03:00+00:00 → 2026-05-01 15:18:18+00:00
- max gap days: 18.4
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 3.84
- lot p95/p50 ratio: 1.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 209.40 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 5.34 / 679.77 / 13758.69

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 431 trades
  - 17:00 — 335 trades
  - 10:00 — 295 trades
  - 18:00 — 292 trades
  - 15:00 — 282 trades

Top entry hour:5min (UTC):
  - 03:00 — 300 trades
  - 02:00 — 129 trades
  - 18:30 — 75 trades
  - 15:30 — 66 trades
  - 19:30 — 44 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - AUDUSD: total=533, buy_pct=56.5%
  - EURCHF: total=509, buy_pct=53.4%
  - EURGBP: total=248, buy_pct=56.5%
  - EURUSD: total=914, buy_pct=52.7%
  - GBPUSD: total=1142, buy_pct=56.7%
  - USDCAD: total=654, buy_pct=41.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=431, buy_pct=51.5%
  - hour=17: total=335, buy_pct=51.3%
  - hour=10: total=295, buy_pct=50.5%
  - hour=18: total=292, buy_pct=51.7%
  - hour=15: total=282, buy_pct=53.2%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.49, atr_ratio_M15=0.14, ema_dist_20_H4=0.13, ret_10_M5=0.07, hour_ut... | 0.586 | 0.027 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^ema_dist_20_H1=>2.51] V [close_vs_session_open_M5=1.0^ret_1_H4=0.0014-0.0025^ret... | 0.531 | 0.053 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.5285); Always-Sell = 0.4715 | 0.528 | — | 1.00 | — |
| 4 | univariate | bb_pos_20_2_H4 > -0.8063 ⇒ Buy | 0.557 | — | 0.80 | 0.000 |
| 5 | univariate | bb_pos_20_2_H1 > -0.5444 ⇒ Buy | 0.588 | — | 0.70 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > -0.9961 ⇒ Buy | 0.580 | — | 0.70 | 0.000 |
| 7 | univariate | ret_10_H1 > -0.000814 ⇒ Buy | 0.593 | — | 0.60 | 0.000 |
| 8 | univariate | ret_3_H4 > -0.0008216 ⇒ Buy | 0.593 | — | 0.60 | 0.000 |
| 9 | univariate | bb_pos_20_2_M15 > -0.1587 ⇒ Buy | 0.586 | — | 0.60 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -0.2955 ⇒ Buy | 0.582 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.49, atr_ratio_M15=0.14, ema_dist_20_H4=0.13, ret_10_M5=0.07, hour_utc=0.06

|--- bb_pos_20_2_H1 <= 0.46
|   |--- bb_pos_20_2_H1 <= -0.75
|   |   |--- hour_utc <= 6.50
|   |   |   |--- class: 1
|   |   |--- hour_utc >  6.50
|   |   |   |--- atr_ratio_M15 <= 0.49
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M15 >  0.49
|   |   |   |   |--- class: 0
|   |--- bb_pos_20_2_H1 >  -0.75
|   |   |--- ema_dist_20_H4 <= 0.83
|   |   |   |--- ret_10_M5 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_M5 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H4 >  0.83
|   |   |   |--- is_first_5min_of_hour <= 0.50
|   |   |   |   |--- class: 0
|   |   |   |--- is_first_5min_of_hour >  0.50
|   |   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  0.46
|   |--- atr_ratio_M15 <= 0.55
|   |   |--- ema_dist_20_H1 <= 2.76
|   |   |   |--- ema_dist_20_H4 <= 1.49
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  1.49
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  2.76
|   |   |   |--- class: 1
|   |--- atr_ratio_M15 >  0.55
|   |   |--- ret_10_M1 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M1 >  -0.00
|   |   |   |--- ret_1_M15 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_M15 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^ema_dist_20_H1=>2.51] V [close_vs_session_open_M5=1.0^ret_1_H4=0.0014-0.0025^ret_3_M1=-0.00023--0.00014] V [close_vs_session_open_M5=1.0^dow=0^ret_1_M1=8.3e-05-0.00015]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
