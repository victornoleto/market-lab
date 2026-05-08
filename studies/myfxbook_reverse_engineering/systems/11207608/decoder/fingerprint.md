# Decoder fingerprint — system 11207608

Generated: 2026-05-02T03:21:59

## Sanity (martingale + lot dynamics)

- n_trades: **202**, deposits: 1
- pairs: {'XAUUSD': 202}
- actions: {'Buy': 104, 'Sell': 98}
- date range: 2024-07-15 14:20:02+00:00 → 2025-07-30 16:33:34+00:00
- max gap days: 7.8
- lot p50/p95/p99/max: 2728.83 / 3372.14 / 3402.58 / 3416.40
- lot p95/p50 ratio: 1.24
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.06 / 0.32

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 31 trades
  - 15:00 — 27 trades
  - 08:00 — 17 trades
  - 11:00 — 16 trades
  - 10:00 — 15 trades

Top entry hour:5min (UTC):
  - 16:35 — 7 trades
  - 15:35 — 6 trades
  - 08:45 — 5 trades
  - 15:30 — 5 trades
  - 16:30 — 5 trades

Exit kind distribution:
  - manual_or_time: 202

Direction by pair (Buy %):
  - XAUUSD: total=202, buy_pct=51.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=31, buy_pct=45.2%
  - hour=15: total=27, buy_pct=48.1%
  - hour=08: total=17, buy_pct=58.8%
  - hour=11: total=16, buy_pct=43.8%
  - hour=10: total=15, buy_pct=60.0%

## Feature extraction

- trades processed: 202
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.95, ema_dist_20_H1=0.05  \|--- bb_pos_20_2_H1 <= -0.19 \|   \|--- cl... | 0.896 | 0.058 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^ret_3_H4=>0.01] V [close_vs_session_open_H1=1.0^ret_10_H1=0.004-0.0064] V [close... | 0.770 | 0.102 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -0.2736 ⇒ Buy | 0.886 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > -0.3145 ⇒ Buy | 0.886 | — | 0.60 | 0.000 |
| 5 | univariate | ret_10_H1 > -0.001282 ⇒ Buy | 0.876 | — | 0.60 | 0.000 |
| 6 | univariate | ret_3_H4 > 0.0004186 ⇒ Buy | 0.876 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.001877 ⇒ Buy | 0.837 | — | 0.50 | 0.000 |
| 8 | univariate | ema_dist_20_H4 > 0.4255 ⇒ Buy | 0.807 | — | 0.50 | 0.000 |
| 9 | univariate | ema_dist_20_M15 > 0.2993 ⇒ Buy | 0.777 | — | 0.50 | 0.000 |
| 10 | univariate | close_vs_session_open_M15 > -1 ⇒ Buy | 0.747 | — | 0.54 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.95, ema_dist_20_H1=0.05

|--- bb_pos_20_2_H1 <= -0.19
|   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.19
|   |--- ema_dist_20_H1 <= 1.42
|   |   |--- class: 1
|   |--- ema_dist_20_H1 >  1.42
|   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^ret_3_H4=>0.01] V [close_vs_session_open_H1=1.0^ret_10_H1=0.004-0.0064] V [close_vs_session_open_H1=1.0^bb_pos_20_2_H1=0.81-0.98] V [close_vs_session_open_M5=1.0^ret_10_H4=0.0055-0.0092] V [bb_pos_20_2_H4=0.68-0.89] V [close_vs_session_open_M5=1.0^ret_3_M15=-0.00031-0.00016] V [bb_pos_20_2_H1=0.52-0.81] V [ret_1_M15=<-0.0013^ema_dist_20_H1=-0.26-0.37] V [bb_pos_20_2_H4=>1.11] V [ret_10_H4=0.0092-0.012^ret_3_M1=-0.0004--0.00024]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
