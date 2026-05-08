# Decoder fingerprint — system 11155858

Generated: 2026-05-02T03:03:35

## Sanity (martingale + lot dynamics)

- n_trades: **197**, deposits: 2
- pairs: {'EURGBP': 197}
- actions: {'Buy': 159, 'Sell': 38}
- date range: 2024-03-20 17:56:19+00:00 → 2026-04-23 12:36:35+00:00
- max gap days: 48.2
- lot p50/p95/p99/max: 0.85 / 0.88 / 0.88 / 0.89
- lot p95/p50 ratio: 1.03
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 115.26 / 972.58 / 1642.79

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 57 trades
  - 20:00 — 51 trades
  - 12:00 — 50 trades
  - 04:00 — 17 trades
  - 00:00 — 13 trades

Top entry hour:5min (UTC):
  - 16:00 — 57 trades
  - 20:00 — 51 trades
  - 12:00 — 50 trades
  - 04:00 — 17 trades
  - 00:00 — 13 trades

Exit kind distribution:
  - manual_or_time: 197

Direction by pair (Buy %):
  - EURGBP: total=197, buy_pct=80.7%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=57, buy_pct=84.2%
  - hour=20: total=51, buy_pct=80.4%
  - hour=12: total=50, buy_pct=86.0%
  - hour=04: total=17, buy_pct=70.6%
  - hour=00: total=13, buy_pct=61.5%

## Feature extraction

- trades processed: 197
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_1_H4=1.00  \|--- ret_1_H4 <= -0.00 \|   \|--- class: 1 \|--- ret_1_H4 >  -0.00 \|... | 0.808 | 0.162 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.8071); Always-Sell = 0.1929 | 0.807 | — | 1.00 | — |
| 3 | univariate | hour_utc > 4 ⇒ Buy | 0.756 | — | 0.85 | 0.000 |
| 4 | univariate | ret_10_M1 > -0.0003101 ⇒ Buy | 0.726 | — | 0.80 | 0.000 |
| 5 | univariate | ret_1_M1 > -7.891e-05 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |
| 6 | univariate | range_norm_M1 > 0.6922 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |
| 7 | univariate | ret_3_M5 > -0.0003163 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |
| 8 | univariate | ret_10_M5 > -0.0004647 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |
| 9 | univariate | ret_1_M15 > -0.0002898 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -1.047 ⇒ Buy | 0.716 | — | 0.80 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_1_H4=1.00

|--- ret_1_H4 <= -0.00
|   |--- class: 1
|--- ret_1_H4 >  -0.00
|   |--- ret_1_H4 <= 0.00
|   |   |--- class: 1
|   |--- ret_1_H4 >  0.00
|   |   |--- class: 1

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
