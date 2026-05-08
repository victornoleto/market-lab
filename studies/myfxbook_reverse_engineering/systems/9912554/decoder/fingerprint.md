# Decoder fingerprint — system 9912554

Generated: 2026-05-02T11:23:24

## Sanity (martingale + lot dynamics)

- n_trades: **103**, deposits: 1
- pairs: {'EURGBP': 103}
- actions: {'Buy': 59, 'Sell': 44}
- date range: 2022-05-17 17:45:52+00:00 → 2026-04-30 17:56:20+00:00
- max gap days: 63.3
- lot p50/p95/p99/max: 0.87 / 0.89 / 0.91 / 0.92
- lot p95/p50 ratio: 1.03
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 162.55 / 4930.81 / 12582.48

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 32 trades
  - 12:00 — 29 trades
  - 20:00 — 27 trades
  - 00:00 — 9 trades
  - 04:00 — 4 trades

Top entry hour:5min (UTC):
  - 16:00 — 32 trades
  - 12:00 — 29 trades
  - 20:00 — 27 trades
  - 00:00 — 9 trades
  - 04:00 — 4 trades

Exit kind distribution:
  - manual_or_time: 103

Direction by pair (Buy %):
  - EURGBP: total=103, buy_pct=57.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=32, buy_pct=59.4%
  - hour=12: total=29, buy_pct=65.5%
  - hour=20: total=27, buy_pct=59.3%
  - hour=00: total=9, buy_pct=33.3%
  - hour=04: total=4, buy_pct=25.0%

## Feature extraction

- trades processed: 103
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | univariate | ret_10_H1 > -0.00361 ⇒ Buy | 0.680 | — | 0.80 | 0.087 |
| 2 | baseline | Always-Buy (y_buy mean = 0.5728); Always-Sell = 0.4272 | 0.573 | — | 1.00 | — |
| 3 | univariate | ret_10_H4 > -0.006723 ⇒ Buy | 0.641 | — | 0.80 | 1.000 |
| 4 | univariate | ret_1_H4 > -0.001802 ⇒ Buy | 0.621 | — | 0.80 | 1.000 |
| 5 | univariate | bb_pos_20_2_H4 > -0.718 ⇒ Buy | 0.641 | — | 0.70 | 1.000 |
| 6 | univariate | ema_dist_20_H1 > -0.3328 ⇒ Buy | 0.660 | — | 0.60 | 0.380 |
| 7 | univariate | bb_pos_20_2_H1 > -0.2814 ⇒ Buy | 0.660 | — | 0.60 | 0.380 |
| 8 | univariate | ret_3_H4 > -0.0005887 ⇒ Buy | 0.660 | — | 0.60 | 0.380 |
| 9 | univariate | range_norm_H4 > 0.9974 ⇒ Buy | 0.641 | — | 0.60 | 1.000 |
| 10 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=1.00  \|--- ret_3_H4 <= 0.00 \|   \|--- class: 0 \|--- ret_3_H4 >  0.00 \|  ... | 0.482 | 0.225 | 1.00 | — |

### TREE full output (rank 10)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=1.00

|--- ret_3_H4 <= 0.00
|   |--- class: 0
|--- ret_3_H4 >  0.00
|   |--- class: 1

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
