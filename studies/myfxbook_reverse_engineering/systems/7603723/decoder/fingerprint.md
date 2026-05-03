# Decoder fingerprint — system 7603723

Generated: 2026-05-02T08:09:51

## Sanity (martingale + lot dynamics)

- n_trades: **3558**, deposits: 2
- pairs: {'GBPUSD': 347, 'EURAUD': 296, 'GBPAUD': 246, 'GBPJPY': 205, 'USDCAD': 200, 'AUDUSD': 197, 'GBPCAD': 193, 'GBPCHF': 190, 'EURCAD': 172, 'EURGBP': 157, 'EURUSD': 139, 'NZDUSD': 135, 'AUDCHF': 124, 'AUDJPY': 121, 'NZDCHF': 119, 'NZDJPY': 116, 'CHFJPY': 101, 'AUDCAD': 95, 'USDCHF': 90, 'CADCHF': 84, 'AUDNZD': 77, 'EURJPY': 54, 'EURCHF': 48, 'CADJPY': 28, 'USDJPY': 24}
- actions: {'Sell': 1899, 'Buy': 1659}
- date range: 2020-12-15 15:31:10+00:00 → 2021-06-16 21:40:37+00:00
- max gap days: 3.1
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.02 / 0.06
- lot p95/p50 ratio: 1.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 5.10 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 5.55 / 274.20 / 2033.79

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 20:00 — 848 trades
  - 12:00 — 725 trades
  - 16:00 — 720 trades
  - 00:00 — 444 trades
  - 04:00 — 403 trades

Top entry hour:5min (UTC):
  - 20:00 — 848 trades
  - 12:00 — 725 trades
  - 16:00 — 720 trades
  - 00:05 — 444 trades
  - 04:00 — 403 trades

Exit kind distribution:
  - manual_or_time: 3558

Direction by pair (Buy %):
  - AUDCAD: total=95, buy_pct=50.5%
  - AUDCHF: total=124, buy_pct=25.0%
  - AUDJPY: total=121, buy_pct=34.7%
  - AUDNZD: total=77, buy_pct=68.8%
  - AUDUSD: total=197, buy_pct=46.7%
  - CADCHF: total=84, buy_pct=60.7%
  - CADJPY: total=28, buy_pct=67.9%
  - CHFJPY: total=101, buy_pct=47.5%
  - EURAUD: total=296, buy_pct=51.0%
  - EURCAD: total=172, buy_pct=41.3%
  - EURCHF: total=48, buy_pct=39.6%
  - EURGBP: total=157, buy_pct=44.6%
  - EURJPY: total=54, buy_pct=55.6%
  - EURUSD: total=139, buy_pct=46.8%
  - GBPAUD: total=246, buy_pct=50.4%
  - GBPCAD: total=193, buy_pct=45.1%
  - GBPCHF: total=190, buy_pct=48.9%
  - GBPJPY: total=205, buy_pct=43.9%
  - GBPUSD: total=347, buy_pct=52.4%
  - NZDCHF: total=119, buy_pct=45.4%
  - NZDJPY: total=116, buy_pct=35.3%
  - NZDUSD: total=135, buy_pct=38.5%
  - USDCAD: total=200, buy_pct=52.5%
  - USDCHF: total=90, buy_pct=38.9%
  - USDJPY: total=24, buy_pct=25.0%

Direction by hour (Buy %, top 5 by activity):
  - hour=20: total=848, buy_pct=45.4%
  - hour=12: total=725, buy_pct=46.8%
  - hour=16: total=720, buy_pct=47.1%
  - hour=00: total=444, buy_pct=39.6%
  - hour=04: total=403, buy_pct=51.9%

## Feature extraction

- trades processed: 3558
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H1=0.66, ret_3_H1=0.14, ema_dist_20_H4=0.05, bb_pos_20_2_H1=0.04, hour_utc=0.0... | 0.642 | 0.020 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^hour_utc=20^bb_pos_20_2_H1=0.016-0.3] V [close_vs_session_open_M5=1.0^ret_10_H1=... | 0.562 | 0.035 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4663); Always-Sell = 0.5337 | 0.534 | — | 1.00 | — |
| 4 | univariate | ret_10_H1 > -2.651e-05 ⇒ Buy | 0.634 | — | 0.50 | 0.000 |
| 5 | univariate | bb_pos_20_2_H1 > 0.01547 ⇒ Buy | 0.632 | — | 0.50 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > 0.01161 ⇒ Buy | 0.622 | — | 0.50 | 0.000 |
| 7 | univariate | ret_3_H4 > -9.83e-06 ⇒ Buy | 0.619 | — | 0.50 | 0.000 |
| 8 | univariate | ema_dist_20_H4 > 0.03174 ⇒ Buy | 0.579 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.01026 ⇒ Buy | 0.574 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > 0.0185 ⇒ Buy | 0.574 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H1=0.66, ret_3_H1=0.14, ema_dist_20_H4=0.05, bb_pos_20_2_H1=0.04, hour_utc=0.04

|--- ret_10_H1 <= -0.00
|   |--- hour_utc <= 2.00
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- ret_10_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- range_norm_H1 <= 0.72
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H1 >  0.72
|   |   |   |   |--- class: 0
|   |--- hour_utc >  2.00
|   |   |--- ret_10_H1 <= -0.00
|   |   |   |--- ret_3_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.00
|   |   |   |--- ret_3_H1 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_H1 >  -0.00
|   |   |   |   |--- class: 0
|--- ret_10_H1 >  -0.00
|   |--- ret_3_H1 <= 0.00
|   |   |--- ema_dist_20_H4 <= 1.66
|   |   |   |--- bb_pos_20_2_H1 <= -0.23
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H1 >  -0.23
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  1.66
|   |   |   |--- ret_10_M15 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_M15 >  -0.00
|   |   |   |   |--- class: 1
|   |--- ret_3_H1 >  0.00
|   |   |--- ret_10_H1 <= 0.00
|   |   |   |--- atr_ratio_M1 <= 0.09
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M1 >  0.09
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  0.00
|   |   |   |--- ret_10_H4 <= 0.01
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H4 >  0.01
|   |   |   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^hour_utc=20^bb_pos_20_2_H1=0.016-0.3] V [close_vs_session_open_M5=1.0^ret_10_H1=0.0032-0.0047] V [ret_10_H1=0.002-0.0032] V [close_vs_session_open_M15=1.0^ret_10_H1=0.001-0.002]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
