# Rescore v2 — relaxed DSR convention (2026-04-25)

DSR n_trials switched from cumulative-loop-budget to per-iteration configs_tested. See `WINNER_AND_RANKING.md` §3 for rationale.

**Winner_conditions met under v2: 2/72 iters**

## Iters meeting all 5 strict winner conditions (v2)

| iter | v1→v2 score | tier | slug |
|---|---|---|---|
| 74 | 89→95 | WINNER | `iter016-iter064-ensemble` |
| 6 | 67→86 | STRONG | `vol-managed-60-40` |

## Top-25 by v2 score

| rank | iter | v1 | **v2** | tier | winner_met (v2) | slug |
|---|---|---|---|---|---|---|
| 1 | 74 | 89 | **95** | WINNER | ✅ | `iter016-iter064-ensemble` |
| 2 | 6 | 67 | **86** | STRONG | ✅ | `vol-managed-60-40` |
| 3 | 64 | 90 | **85** | STRONG | — | `iter058-qqq-trend-substitution` |
| 4 | 69 | 90 | **85** | STRONG | — | `iter064-vix-inner-weight-reverse` |
| 5 | 70 | 90 | **85** | STRONG | — | `iter064-t10y3m-cont-inner-weight` |
| 6 | 71 | 90 | **85** | STRONG | — | `iter064-plus-spy-mr-rsi2` |
| 7 | 46 | 85 | **80** | STRONG | — | `iter039-overlay-on-iter041` |
| 8 | 58 | 85 | **80** | STRONG | — | `iter046-plus-hyg-tsm-w010` |
| 9 | 72 | 85 | **80** | STRONG | — | `iter064-vix-cond-r-mr-allocation` |
| 10 | 41 | 84 | **79** | STRONG | — | `regime-weights-vix-static-stack` |
| 11 | 51 | 84 | **79** | STRONG | — | `iter037-plus-iter026-w080` |
| 12 | 53 | 84 | **79** | STRONG | — | `iter037-plus-iter046-w070` |
| 13 | 5 | 59 | **78** | STRONG | — | `variance-managed-spy` |
| 14 | 48 | 83 | **78** | STRONG | — | `iter046-output-lev-gate` |
| 15 | 4 | 51 | **76** | STRONG | — | `vol-managed-spy` |
| 16 | 45 | 81 | **76** | STRONG | — | `iter039-overlay-on-iter037` |
| 17 | 63 | 81 | **76** | STRONG | — | `iter058-internal-letf-iter041-only` |
| 18 | 16 | 79 | **74** | PROMISING | — | `static-stack-vm-hybrid` |
| 19 | 18 | 79 | **74** | PROMISING | — | `funding-cost-modeled-replay` |
| 20 | 20 | 79 | **74** | PROMISING | — | `put-spread-tail-hedge` |
| 21 | 21 | 79 | **74** | PROMISING | — | `short-credit-spread-vrp-harvest` |
| 22 | 37 | 79 | **74** | PROMISING | — | `ntsx-3leg-preserved-lev` |
| 23 | 38 | 79 | **74** | PROMISING | — | `regime-lev-vix` |
| 24 | 43 | 79 | **74** | PROMISING | — | `hysteretic-vix-regime-weights` |
| 25 | 52 | 79 | **74** | PROMISING | — | `iter041-plus-iter026-w082` |
