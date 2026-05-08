# Decoder fingerprint — system 11628637

Generated: 2026-05-02T04:21:32

## Sanity (martingale + lot dynamics)

- n_trades: **232**, deposits: 1
- pairs: {'BTCUSD': 232}
- actions: {'Buy': 117, 'Sell': 115}
- date range: 2025-06-25 12:07:48+00:00 → 2026-05-01 15:34:00+00:00
- max gap days: 6.0
- lot p50/p95/p99/max: 95890.00 / 119045.47 / 122865.34 / 125739.59
- lot p95/p50 ratio: 1.24
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.01 / 0.23 / 2.08

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 35 trades
  - 16:00 — 33 trades
  - 18:00 — 21 trades
  - 15:00 — 16 trades
  - 11:00 — 15 trades

Top entry hour:5min (UTC):
  - 16:40 — 7 trades
  - 16:50 — 6 trades
  - 17:10 — 6 trades
  - 15:30 — 5 trades
  - 17:00 — 5 trades

Exit kind distribution:
  - manual_or_time: 232

Direction by pair (Buy %):
  - BTCUSD: total=232, buy_pct=50.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=35, buy_pct=54.3%
  - hour=16: total=33, buy_pct=45.5%
  - hour=18: total=21, buy_pct=33.3%
  - hour=15: total=16, buy_pct=50.0%
  - hour=11: total=15, buy_pct=73.3%

## Feature extraction

- trades processed: 232
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.93, bb_pos_20_2_H1=0.06, atr_ratio_M5=0.01  \|--- ema_dist_20_H1 <= ... | 0.874 | 0.045 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^ema_dist_20_H1=1.63-2.28] V [close_vs_session_open_M15=1.0^ema_dist_20_H1=1.14-1... | 0.745 | 0.041 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -0.4477 ⇒ Buy | 0.871 | — | 0.60 | 0.000 |
| 4 | univariate | ret_10_H1 > -0.004225 ⇒ Buy | 0.845 | — | 0.60 | 0.000 |
| 5 | univariate | ret_3_H4 > -0.004338 ⇒ Buy | 0.828 | — | 0.60 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > 0.09176 ⇒ Buy | 0.866 | — | 0.50 | 0.000 |
| 7 | univariate | ema_dist_20_H4 > -0.07155 ⇒ Buy | 0.823 | — | 0.50 | 0.000 |
| 8 | univariate | bb_pos_20_2_H4 > -0.03148 ⇒ Buy | 0.823 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_M15 > -0.1307 ⇒ Buy | 0.741 | — | 0.60 | 0.000 |
| 10 | univariate | ret_10_H4 > 5.078e-06 ⇒ Buy | 0.789 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.93, bb_pos_20_2_H1=0.06, atr_ratio_M5=0.01

|--- ema_dist_20_H1 <= 0.46
|   |--- bb_pos_20_2_H1 <= -0.53
|   |   |--- class: 0
|   |--- bb_pos_20_2_H1 >  -0.53
|   |   |--- class: 0
|--- ema_dist_20_H1 >  0.46
|   |--- atr_ratio_M5 <= 0.28
|   |   |--- class: 1
|   |--- atr_ratio_M5 >  0.28
|   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^ema_dist_20_H1=1.63-2.28] V [close_vs_session_open_M15=1.0^ema_dist_20_H1=1.14-1.63] V [close_vs_session_open_M15=1.0^ema_dist_20_H1=>2.28] V [ema_dist_20_H1=0.75-1.14] V [bb_pos_20_2_H1=0.41-0.64] V [bb_pos_20_2_H1=-0.34-0.093^prior_bar_sign_H1=-1.0] V [ema_dist_20_H1=0.19-0.75^bb_pos_20_2_M15=-0.13-0.019] V [ret_3_H4=0.013-0.021] V [ret_3_M15=0.00025-0.001^ret_3_M1=0.00027-0.00054]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
