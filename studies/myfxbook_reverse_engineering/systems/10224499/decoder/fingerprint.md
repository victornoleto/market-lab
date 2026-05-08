# Decoder fingerprint — system 10224499

Generated: 2026-05-02T01:34:29

## Sanity (martingale + lot dynamics)

- n_trades: **221**, deposits: 1
- pairs: {'USDCAD': 93, 'EURUSD': 66, 'GBPUSD': 62}
- actions: {'Sell': 114, 'Buy': 107}
- date range: 2023-04-19 23:04:18+00:00 → 2026-04-29 02:00:08+00:00
- max gap days: 41.0
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 1.74 / 5.03 / 12.38

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 23:00 — 127 trades
  - 22:00 — 50 trades
  - 00:00 — 44 trades
  - 01:00 — 0 trades
  - 04:00 — 0 trades

Top entry hour:5min (UTC):
  - 23:55 — 21 trades
  - 23:25 — 20 trades
  - 23:50 — 15 trades
  - 23:35 — 12 trades
  - 23:10 — 10 trades

Exit kind distribution:
  - manual_or_time: 221

Direction by pair (Buy %):
  - EURUSD: total=66, buy_pct=36.4%
  - GBPUSD: total=62, buy_pct=51.6%
  - USDCAD: total=93, buy_pct=54.8%

Direction by hour (Buy %, top 5 by activity):
  - hour=23: total=127, buy_pct=52.0%
  - hour=22: total=50, buy_pct=48.0%
  - hour=00: total=44, buy_pct=38.6%

## Feature extraction

- trades processed: 221
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.72, ret_10_H1=0.19, ret_10_M15=0.09  \|--- bb_pos_20_2_M15 <= 0.15 ... | 0.688 | 0.070 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[prior_bar_sign_H4=-1.0^ret_10_M15=<-0.00092] V [prior_bar_sign_H4=-1.0^hour_utc=23] V [ema_dist_20_M15=-1.08-... | 0.634 | 0.057 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H1 > -0.3409 ⇒ Sell | 0.674 | — | 0.70 | 0.000 |
| 4 | univariate | ret_10_H1 > -0.0007561 ⇒ Sell | 0.656 | — | 0.70 | 0.001 |
| 5 | univariate | ema_dist_20_H1 > -0.5853 ⇒ Sell | 0.656 | — | 0.70 | 0.001 |
| 6 | univariate | ema_dist_20_M15 > -0.1344 ⇒ Sell | 0.692 | — | 0.60 | 0.000 |
| 7 | baseline | Always-Buy (y_buy mean = 0.4842); Always-Sell = 0.5158 | 0.516 | — | 1.00 | — |
| 8 | univariate | ret_10_M15 > -0.0001688 ⇒ Sell | 0.602 | — | 0.70 | 0.808 |
| 9 | univariate | bb_pos_20_2_M15 > 0.0768 ⇒ Sell | 0.710 | — | 0.50 | 0.000 |
| 10 | univariate | ret_3_H4 > -0.0005204 ⇒ Sell | 0.638 | — | 0.60 | 0.013 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.72, ret_10_H1=0.19, ret_10_M15=0.09

|--- bb_pos_20_2_M15 <= 0.15
|   |--- ret_10_H1 <= 0.00
|   |   |--- class: 1
|   |--- ret_10_H1 >  0.00
|   |   |--- class: 1
|--- bb_pos_20_2_M15 >  0.15
|   |--- ret_10_M15 <= 0.00
|   |   |--- class: 0
|   |--- ret_10_M15 >  0.00
|   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[prior_bar_sign_H4=-1.0^ret_10_M15=<-0.00092] V [prior_bar_sign_H4=-1.0^hour_utc=23] V [ema_dist_20_M15=-1.08--0.5] V [range_norm_M5=0.92-1.03^ret_10_H4=>0.0061]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
