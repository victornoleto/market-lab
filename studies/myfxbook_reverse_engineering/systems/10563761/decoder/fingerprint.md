# Decoder fingerprint — system 10563761

Generated: 2026-05-02T02:14:15

## Sanity (martingale + lot dynamics)

- n_trades: **436**, deposits: 0
- pairs: {'BTCUSD': 436}
- actions: {'Buy': 238, 'Sell': 198}
- date range: 2024-05-13 10:04:19+00:00 → 2026-01-29 16:36:11+00:00
- max gap days: 7.8
- lot p50/p95/p99/max: 93659.47 / 117728.50 / 121127.37 / 125705.20
- lot p95/p50 ratio: 1.26
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.18 / 1.23

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 70 trades
  - 16:00 — 60 trades
  - 15:00 — 38 trades
  - 18:00 — 35 trades
  - 19:00 — 30 trades

Top entry hour:5min (UTC):
  - 16:45 — 12 trades
  - 15:30 — 12 trades
  - 16:40 — 10 trades
  - 16:35 — 10 trades
  - 17:55 — 9 trades

Exit kind distribution:
  - manual_or_time: 436

Direction by pair (Buy %):
  - BTCUSD: total=436, buy_pct=54.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=70, buy_pct=51.4%
  - hour=16: total=60, buy_pct=46.7%
  - hour=15: total=38, buy_pct=55.3%
  - hour=18: total=35, buy_pct=54.3%
  - hour=19: total=30, buy_pct=60.0%

## Feature extraction

- trades processed: 436
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.89, bb_pos_20_2_M5=0.07, ema_dist_20_H1=0.03, ema_dist_20_H4=0.01, a... | 0.858 | 0.036 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^bb_pos_20_2_H1=>1.07] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.89-1.07] ... | 0.812 | 0.021 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H4 > -0.1814 ⇒ Buy | 0.842 | — | 0.60 | 0.000 |
| 4 | univariate | ret_3_H4 > -0.003261 ⇒ Buy | 0.819 | — | 0.60 | 0.000 |
| 5 | univariate | ret_10_H4 > -0.005562 ⇒ Buy | 0.810 | — | 0.60 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > 0.2043 ⇒ Buy | 0.867 | — | 0.50 | 0.000 |
| 7 | univariate | ema_dist_20_H1 > 0.3319 ⇒ Buy | 0.862 | — | 0.50 | 0.000 |
| 8 | univariate | ret_10_H1 > 0.002135 ⇒ Buy | 0.849 | — | 0.50 | 0.000 |
| 9 | univariate | ema_dist_20_H4 > 0.1738 ⇒ Buy | 0.835 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -0.2118 ⇒ Buy | 0.727 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.89, bb_pos_20_2_M5=0.07, ema_dist_20_H1=0.03, ema_dist_20_H4=0.01, atr_ratio_H4=0.00

|--- bb_pos_20_2_H1 <= 0.23
|   |--- bb_pos_20_2_M5 <= -0.31
|   |   |--- class: 0
|   |--- bb_pos_20_2_M5 >  -0.31
|   |   |--- ema_dist_20_H4 <= -0.49
|   |   |   |--- class: 0
|   |   |--- ema_dist_20_H4 >  -0.49
|   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  0.23
|   |--- ema_dist_20_H1 <= 0.90
|   |   |--- class: 1
|   |--- ema_dist_20_H1 >  0.90
|   |   |--- atr_ratio_H4 <= 1.89
|   |   |   |--- class: 1
|   |   |--- atr_ratio_H4 >  1.89
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^bb_pos_20_2_H1=>1.07] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.89-1.07] V [bb_pos_20_2_H1=0.67-0.89] V [bb_pos_20_2_H1=0.48-0.67^prior_bar_sign_M15=-1.0] V [bb_pos_20_2_H1=0.2-0.48^prior_bar_sign_H1=-1.0] V [bb_pos_20_2_H1=0.48-0.67^prior_bar_sign_M1=-1.0] V [bb_pos_20_2_H4=0.82-1.03] V [bb_pos_20_2_H1=-0.29-0.2^prior_bar_sign_H1=-1.0] V [ema_dist_20_H4=1.03-1.51^bb_pos_20_2_H4=0.65-0.82] V [bb_pos_20_2_H1=0.89-1.07] V [atr_ratio_H4=2.42-2.69^ema_dist_20_M1=0.86-1.28]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
