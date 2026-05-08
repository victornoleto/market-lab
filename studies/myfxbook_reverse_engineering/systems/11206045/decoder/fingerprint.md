# Decoder fingerprint — system 11206045

Generated: 2026-05-02T03:18:13

## Sanity (martingale + lot dynamics)

- n_trades: **212**, deposits: 2
- pairs: {'GBPJPY': 212}
- actions: {'Buy': 118, 'Sell': 94}
- date range: 2024-08-26 00:00:11+00:00 → 2026-05-01 09:47:20+00:00
- max gap days: 23.5
- lot p50/p95/p99/max: 195.67 / 212.43 / 214.21 / 215.13
- lot p95/p50 ratio: 1.09
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 37.01 / 396.39 / 918.16

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 00:00 — 209 trades
  - 19:00 — 1 trades
  - 16:00 — 1 trades
  - 09:00 — 1 trades
  - 04:00 — 0 trades

Top entry hour:5min (UTC):
  - 00:05 — 200 trades
  - 00:00 — 9 trades
  - 09:45 — 1 trades
  - 16:55 — 1 trades
  - 19:15 — 1 trades

Exit kind distribution:
  - manual_or_time: 212

Direction by pair (Buy %):
  - GBPJPY: total=212, buy_pct=55.7%

Direction by hour (Buy %, top 5 by activity):
  - hour=00: total=209, buy_pct=55.0%
  - hour=09: total=1, buy_pct=100.0%
  - hour=16: total=1, buy_pct=100.0%
  - hour=19: total=1, buy_pct=100.0%

## Feature extraction

- trades processed: 212
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.62, ret_10_H1=0.38  \|--- ret_10_H4 <= 0.00 \|   \|--- ret_10_H1 <= -0.00... | 0.571 | 0.030 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5566); Always-Sell = 0.4434 | 0.557 | — | 1.00 | — |
| 3 | ripper | RIPPER ruleset: [[range_norm_M1=0.66-0.81] V [atr_ratio_M15=0.31-0.36] V [ret_10_H4=0.0047-0.0067] V [ret_3_H1=-0.0012--0.00055]] | 0.481 | 0.032 | 1.00 | — |
| 4 | univariate | bb_pos_20_2_H4 > 0.182 ⇒ Buy | 0.613 | — | 0.50 | 0.302 |
| 5 | univariate | ret_10_H4 > 0.001374 ⇒ Buy | 0.604 | — | 0.50 | 0.772 |
| 6 | univariate | ema_dist_20_H4 > 0.271 ⇒ Buy | 0.594 | — | 0.50 | 1.000 |
| 7 | univariate | ret_3_H1 > 0.0003219 ⇒ Sell | 0.585 | — | 0.50 | 1.000 |
| 8 | univariate | ret_1_M1 > 7.225e-05 ⇒ Sell | 0.599 | — | 0.40 | 1.000 |
| 9 | univariate | ret_1_H1 > 0.0003282 ⇒ Sell | 0.590 | — | 0.40 | 1.000 |
| 10 | univariate | ret_1_M15 > 0.0003504 ⇒ Sell | 0.585 | — | 0.30 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.62, ret_10_H1=0.38

|--- ret_10_H4 <= 0.00
|   |--- ret_10_H1 <= -0.00
|   |   |--- class: 1
|   |--- ret_10_H1 >  -0.00
|   |   |--- class: 0
|--- ret_10_H4 >  0.00
|   |--- class: 1

```

### RIPPER full output (rank 3)
```
RIPPER ruleset:
[[range_norm_M1=0.66-0.81] V [atr_ratio_M15=0.31-0.36] V [ret_10_H4=0.0047-0.0067] V [ret_3_H1=-0.0012--0.00055]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
