# Decoder fingerprint — system 11504701

Generated: 2026-05-02T03:30:43

## Sanity (martingale + lot dynamics)

- n_trades: **314**, deposits: 1
- pairs: {'USDJPY': 103, 'GBPUSD': 96, 'EURUSD': 69, 'AUDUSD': 44, 'ARCHIV': 2}
- actions: {'Buy': 172, 'Sell': 142}
- date range: 2025-04-15 23:59:59+00:00 → 2026-04-23 11:30:01+00:00
- max gap days: 14.5
- lot p50/p95/p99/max: 1.34 / 156.43 / 158.80 / 159.67
- lot p95/p50 ratio: 116.63
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 119.47 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.00 / 0.06 / 0.57

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 172 trades
  - 17:00 — 63 trades
  - 09:00 — 17 trades
  - 16:00 — 12 trades
  - 21:00 — 10 trades

Top entry hour:5min (UTC):
  - 15:30 — 153 trades
  - 17:00 — 63 trades
  - 15:15 — 18 trades
  - 09:00 — 17 trades
  - 16:45 — 12 trades

Exit kind distribution:
  - manual_or_time: 314

Direction by pair (Buy %):
  - ARCHIV: total=2, buy_pct=100.0%
  - AUDUSD: total=44, buy_pct=68.2%
  - EURUSD: total=69, buy_pct=56.5%
  - GBPUSD: total=96, buy_pct=52.1%
  - USDJPY: total=103, buy_pct=49.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=172, buy_pct=57.0%
  - hour=17: total=63, buy_pct=44.4%
  - hour=09: total=17, buy_pct=47.1%
  - hour=16: total=12, buy_pct=50.0%
  - hour=21: total=10, buy_pct=70.0%

## Feature extraction

- trades processed: 312
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H1=0.68, ret_3_M1=0.14, ema_dist_20_H1=0.12, bb_pos_20_2_M5=0.07  \|--- ret_10... | 0.619 | 0.075 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=1.0^atr_ratio_M5=<0.22] V [prior_bar_sign_H4=1.0^ret_10_H1=0.004-0.0058] V [ret_10_H... | 0.572 | 0.050 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H1 > -0.5589 ⇒ Buy | 0.660 | — | 0.70 | 0.000 |
| 4 | univariate | ret_3_H4 > -0.001564 ⇒ Buy | 0.654 | — | 0.70 | 0.000 |
| 5 | baseline | Always-Buy (y_buy mean = 0.5449); Always-Sell = 0.4551 | 0.545 | — | 1.00 | — |
| 6 | univariate | ema_dist_20_H1 > -0.4419 ⇒ Buy | 0.676 | — | 0.60 | 0.000 |
| 7 | univariate | bb_pos_20_2_M15 > -0.1674 ⇒ Buy | 0.663 | — | 0.60 | 0.000 |
| 8 | univariate | bb_pos_20_2_H4 > -0.2217 ⇒ Buy | 0.631 | — | 0.60 | 0.001 |
| 9 | univariate | ret_10_H1 > 0.0002074 ⇒ Buy | 0.673 | — | 0.50 | 0.000 |
| 10 | univariate | close_vs_session_open_H1 > -1 ⇒ Buy | 0.633 | — | 0.52 | 0.001 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H1=0.68, ret_3_M1=0.14, ema_dist_20_H1=0.12, bb_pos_20_2_M5=0.07

|--- ret_10_H1 <= -0.00
|   |--- ema_dist_20_H1 <= -1.16
|   |   |--- class: 0
|   |--- ema_dist_20_H1 >  -1.16
|   |   |--- class: 0
|--- ret_10_H1 >  -0.00
|   |--- ret_3_M1 <= -0.00
|   |   |--- class: 1
|   |--- ret_3_M1 >  -0.00
|   |   |--- bb_pos_20_2_M5 <= 0.41
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M5 >  0.41
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M1=1.0^atr_ratio_M5=<0.22] V [prior_bar_sign_H4=1.0^ret_10_H1=0.004-0.0058] V [ret_10_H1=>0.0058]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
