# Rescore v2 — relaxed DSR convention (2026-04-25)

DSR n_trials switched from cumulative-loop-budget to per-iteration configs_tested. See `WINNER_AND_RANKING.md` §3 for rationale.

**Winner_conditions met under v2: 3/77 iters**

## Iters meeting all 5 strict winner conditions (v2)

| iter | v1→v2 score | tier | slug |
|---|---|---|---|
| 74 | 89→95 | WINNER | `iter016-iter064-ensemble` |
| 79 | 93→93 | WINNER | `iter079-multi-asset-topk-momentum` |
| 6 | 67→86 | STRONG | `vol-managed-60-40` |

## Top-25 by v2 score

| rank | iter | v1 | **v2** | tier | winner_met (v2) | slug |
|---|---|---|---|---|---|---|
| 1 | 74 | 89 | **95** | WINNER | ✅ | `iter016-iter064-ensemble` |
| 2 | 79 | 93 | **93** | WINNER | ✅ | `iter079-multi-asset-topk-momentum` |
| 3 | 6 | 67 | **86** | STRONG | ✅ | `vol-managed-60-40` |
| 4 | 64 | 90 | **85** | STRONG | — | `iter058-qqq-trend-substitution` |
| 5 | 69 | 90 | **85** | STRONG | — | `iter064-vix-inner-weight-reverse` |
| 6 | 70 | 90 | **85** | STRONG | — | `iter064-t10y3m-cont-inner-weight` |
| 7 | 71 | 90 | **85** | STRONG | — | `iter064-plus-spy-mr-rsi2` |
| 8 | 76 | 85 | **85** | STRONG | — | `iter064-plus-levered-gld-tlt-trend-sleeve` |
| 9 | 77 | 85 | **85** | STRONG | — | `iter077-iter064-mtum-vlue-ls-sleeve` |
| 10 | 75 | 81 | **81** | STRONG | — | `iter064-plus-gld-tlt-trend-sleeve` |
| 11 | 46 | 85 | **80** | STRONG | — | `iter039-overlay-on-iter041` |
| 12 | 58 | 85 | **80** | STRONG | — | `iter046-plus-hyg-tsm-w010` |
| 13 | 72 | 85 | **80** | STRONG | — | `iter064-vix-cond-r-mr-allocation` |
| 14 | 41 | 84 | **79** | STRONG | — | `regime-weights-vix-static-stack` |
| 15 | 51 | 84 | **79** | STRONG | — | `iter037-plus-iter026-w080` |
| 16 | 53 | 84 | **79** | STRONG | — | `iter037-plus-iter046-w070` |
| 17 | 5 | 59 | **78** | STRONG | — | `variance-managed-spy` |
| 18 | 48 | 83 | **78** | STRONG | — | `iter046-output-lev-gate` |
| 19 | 4 | 51 | **76** | STRONG | — | `vol-managed-spy` |
| 20 | 45 | 81 | **76** | STRONG | — | `iter039-overlay-on-iter037` |
| 21 | 63 | 81 | **76** | STRONG | — | `iter058-internal-letf-iter041-only` |
| 22 | 78 | 75 | **75** | STRONG | — | `iter078-antonacci-dual-momentum-base` |
| 23 | 16 | 79 | **74** | PROMISING | — | `static-stack-vm-hybrid` |
| 24 | 18 | 79 | **74** | PROMISING | — | `funding-cost-modeled-replay` |
| 25 | 20 | 79 | **74** | PROMISING | — | `put-spread-tail-hedge` |
