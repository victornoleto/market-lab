# Decoder fingerprint — system 7942220

Generated: 2026-05-02T08:28:36

## Sanity (martingale + lot dynamics)

- n_trades: **3910**, deposits: 1
- pairs: {'GBPUSD': 372, 'EURAUD': 347, 'GBPAUD': 268, 'GBPCAD': 247, 'GBPJPY': 245, 'AUDUSD': 225, 'GBPCHF': 224, 'USDCAD': 215, 'EURCAD': 194, 'EURGBP': 177, 'NZDUSD': 150, 'AUDJPY': 145, 'NZDJPY': 125, 'CHFJPY': 123, 'AUDCHF': 123, 'NZDCHF': 120, 'EURUSD': 111, 'AUDCAD': 104, 'USDCHF': 93, 'CADCHF': 92, 'AUDNZD': 62, 'EURCHF': 49, 'USDJPY': 43, 'EURJPY': 39, 'CADJPY': 17}
- actions: {'Sell': 2125, 'Buy': 1785}
- date range: 2020-11-27 17:13:27+00:00 → 2021-06-16 21:40:37+00:00
- max gap days: 3.2
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.02 / 0.07
- lot p95/p50 ratio: 1.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 5.95 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 5.44 / 330.32 / 2390.08

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 20:00 — 935 trades
  - 12:00 — 814 trades
  - 16:00 — 796 trades
  - 00:00 — 506 trades
  - 08:00 — 417 trades

Top entry hour:5min (UTC):
  - 20:00 — 935 trades
  - 12:00 — 814 trades
  - 16:00 — 796 trades
  - 00:05 — 506 trades
  - 08:00 — 417 trades

Exit kind distribution:
  - manual_or_time: 3910

Direction by pair (Buy %):
  - AUDCAD: total=104, buy_pct=49.0%
  - AUDCHF: total=123, buy_pct=29.3%
  - AUDJPY: total=145, buy_pct=38.6%
  - AUDNZD: total=62, buy_pct=22.6%
  - AUDUSD: total=225, buy_pct=49.8%
  - CADCHF: total=92, buy_pct=64.1%
  - CADJPY: total=17, buy_pct=35.3%
  - CHFJPY: total=123, buy_pct=45.5%
  - EURAUD: total=347, buy_pct=50.1%
  - EURCAD: total=194, buy_pct=50.0%
  - EURCHF: total=49, buy_pct=24.5%
  - EURGBP: total=177, buy_pct=44.6%
  - EURJPY: total=39, buy_pct=25.6%
  - EURUSD: total=111, buy_pct=41.4%
  - GBPAUD: total=268, buy_pct=45.1%
  - GBPCAD: total=247, buy_pct=45.3%
  - GBPCHF: total=224, buy_pct=44.6%
  - GBPJPY: total=245, buy_pct=46.9%
  - GBPUSD: total=372, buy_pct=52.4%
  - NZDCHF: total=120, buy_pct=36.7%
  - NZDJPY: total=125, buy_pct=33.6%
  - NZDUSD: total=150, buy_pct=40.7%
  - USDCAD: total=215, buy_pct=54.9%
  - USDCHF: total=93, buy_pct=55.9%
  - USDJPY: total=43, buy_pct=39.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=20: total=935, buy_pct=46.0%
  - hour=12: total=814, buy_pct=44.5%
  - hour=16: total=796, buy_pct=46.5%
  - hour=00: total=506, buy_pct=39.1%
  - hour=08: total=417, buy_pct=47.0%

## Feature extraction

- trades processed: 3910
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H1=0.64, ret_3_H1=0.10, ema_dist_20_H1=0.08, ret_10_H4=0.05, ema_dist_20_H4=0.... | 0.630 | 0.028 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^hour_utc=20^bb_pos_20_2_M15=0.0065-0.2^prior_bar_sign_H1=1.0^prior_bar_sign_M15=... | 0.582 | 0.018 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4565); Always-Sell = 0.5435 | 0.543 | — | 1.00 | — |
| 4 | univariate | ret_10_H1 > 5.941e-05 ⇒ Buy | 0.635 | — | 0.50 | 0.000 |
| 5 | univariate | bb_pos_20_2_H1 > 0.02276 ⇒ Buy | 0.634 | — | 0.50 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > 0.0265 ⇒ Buy | 0.619 | — | 0.50 | 0.000 |
| 7 | univariate | close_vs_session_open_M15 > -1 ⇒ Buy | 0.569 | — | 0.51 | 0.000 |
| 8 | univariate | close_vs_session_open_M5 > 0 ⇒ Buy | 0.574 | — | 0.49 | 0.000 |
| 9 | univariate | close_vs_session_open_M1 > 0 ⇒ Buy | 0.570 | — | 0.49 | 0.000 |
| 10 | univariate | close_vs_session_open_H4 > -1 ⇒ Buy | 0.558 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H1=0.64, ret_3_H1=0.10, ema_dist_20_H1=0.08, ret_10_H4=0.05, ema_dist_20_H4=0.05

|--- ret_10_H1 <= -0.00
|   |--- ret_3_H1 <= -0.00
|   |   |--- ret_10_H1 <= -0.00
|   |   |   |--- ret_3_H4 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H4 >  -0.01
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.00
|   |   |   |--- dollar_index_proxy <= -0.07
|   |   |   |   |--- class: 1
|   |   |   |--- dollar_index_proxy >  -0.07
|   |   |   |   |--- class: 0
|   |--- ret_3_H1 >  -0.00
|   |   |--- ret_10_H4 <= 0.00
|   |   |   |--- ret_10_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H4 >  0.00
|   |   |   |--- class: 0
|--- ret_10_H1 >  -0.00
|   |--- ret_3_H1 <= 0.00
|   |   |--- bb_pos_20_2_H1 <= -0.30
|   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_H1 >  -0.30
|   |   |   |--- ema_dist_20_H4 <= 1.14
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  1.14
|   |   |   |   |--- class: 1
|   |--- ret_3_H1 >  0.00
|   |   |--- ema_dist_20_H1 <= 1.34
|   |   |   |--- atr_ratio_H4 <= 1.63
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_H4 >  1.63
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  1.34
|   |   |   |--- ret_10_H4 <= 0.01
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H4 >  0.01
|   |   |   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^hour_utc=20^bb_pos_20_2_M15=0.0065-0.2^prior_bar_sign_H1=1.0^prior_bar_sign_M15=-1.0] V [close_vs_session_open_M5=1.0^hour_utc=20] V [close_vs_session_open_M15=1.0^ret_10_H1=0.0021-0.0032] V [ret_10_H1=5.9e-05-0.0011]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
