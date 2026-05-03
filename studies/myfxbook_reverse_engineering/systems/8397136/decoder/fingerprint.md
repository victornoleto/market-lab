# Decoder fingerprint — system 8397136

Generated: 2026-05-02T08:36:56

## Sanity (martingale + lot dynamics)

- n_trades: **432**, deposits: 1
- pairs: {'EURUSD': 216, 'USDCHF': 216}
- actions: {'Sell': 226, 'Buy': 206}
- date range: 2020-12-22 17:10:30+00:00 → 2021-06-16 21:01:04+00:00
- max gap days: 0.0
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 48.05 / 753.30 / 1303.90

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 13:00 — 282 trades
  - 15:00 — 18 trades
  - 19:00 — 16 trades
  - 10:00 — 16 trades
  - 09:00 — 14 trades

Top entry hour:5min (UTC):
  - 13:00 — 254 trades
  - 13:05 — 6 trades
  - 13:15 — 6 trades
  - 10:35 — 4 trades
  - 12:50 — 4 trades

Exit kind distribution:
  - manual_or_time: 432

Direction by pair (Buy %):
  - EURUSD: total=216, buy_pct=47.7%
  - USDCHF: total=216, buy_pct=47.7%

Direction by hour (Buy %, top 5 by activity):
  - hour=13: total=282, buy_pct=44.0%
  - hour=15: total=18, buy_pct=44.4%
  - hour=19: total=16, buy_pct=12.5%
  - hour=10: total=16, buy_pct=87.5%
  - hour=09: total=14, buy_pct=71.4%

## Feature extraction

- trades processed: 432
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[hour_utc=<10.1^dollar_index_proxy=1.0^prior_bar_sign_H1=-1.0]] | 0.527 | 0.172 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4769); Always-Sell = 0.5231 | 0.523 | — | 1.00 | — |
| 3 | tree | DecisionTree(max_depth=4) — top features: hour_utc=0.53, ema_dist_20_H4=0.23, range_norm_M15=0.15, ret_3_H4=0.10  \|--- hour_ut... | 0.511 | 0.048 | 1.00 | — |
| 4 | univariate | bb_pos_20_2_M1 > -0.6534 ⇒ Sell | 0.537 | — | 0.80 | 1.000 |
| 5 | univariate | range_norm_M15 > 0.8184 ⇒ Sell | 0.551 | — | 0.70 | 1.000 |
| 6 | univariate | bb_pos_20_2_H4 > -0.1559 ⇒ Buy | 0.572 | — | 0.60 | 0.856 |
| 7 | univariate | is_first_min_of_hour > 0 ⇒ Sell | 0.542 | — | 0.57 | 1.000 |
| 8 | univariate | ret_3_H4 > 0.0001512 ⇒ Buy | 0.551 | — | 0.50 | 1.000 |
| 9 | univariate | ret_1_H4 > 4.482e-05 ⇒ Buy | 0.542 | — | 0.50 | 1.000 |
| 10 | univariate | ema_dist_20_H4 > 0.5305 ⇒ Buy | 0.583 | — | 0.40 | 0.161 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[hour_utc=<10.1^dollar_index_proxy=1.0^prior_bar_sign_H1=-1.0]]
```

### TREE full output (rank 3)
```
DecisionTree(max_depth=4) — top features: hour_utc=0.53, ema_dist_20_H4=0.23, range_norm_M15=0.15, ret_3_H4=0.10

|--- hour_utc <= 12.50
|   |--- class: 1
|--- hour_utc >  12.50
|   |--- ema_dist_20_H4 <= -0.95
|   |   |--- class: 0
|   |--- ema_dist_20_H4 >  -0.95
|   |   |--- range_norm_M15 <= 0.84
|   |   |   |--- class: 1
|   |   |--- range_norm_M15 >  0.84
|   |   |   |--- ret_3_H4 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_H4 >  -0.00
|   |   |   |   |--- class: 0

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
