# Phase 3.6 Family A — Clenow cross-sectional momentum (honest validation)

**Date:** 2026-04-22  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Banco Inter Internacional (plan §3.2) —
zero commission on US stocks, 0.05% one-way spread/slippage, BR 15% CG
tax on positive monthly net return.
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 |
FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

The Clenow swing-horizon top-20 cross-sectional momentum **fails 9 of the
13 gates** under the honest engine on the Tiingo-ADV-filtered universe.
OOS Sharpe collapses to **0.25** (gate 2 ≥ 1.5 → FAIL), OOS CAGR is
**2.67%** (gate 3 CDI floor 13% → FAIL), OOS MaxDD **−26.6%** just
breaches gate 4 (≥ −25%), and the bootstrap 99.9% CI on OOS Sharpe
includes zero (**[−1.02, 1.59]** → gate 1 FAIL). Gate 12 DSR
p-value is **0.72** (gate < 0.05 → FAIL).

Positive signals: FWD (2024-01-01 → 2026-04-14) Sharpe **1.18** / CAGR
**16.4%** / MDD **−12.9%** — gate 5 PASS. Median hold **37 trading days**
(gate 7 ≥ 5d → PASS). PBO **0.25** (gate 11 < 0.5 → PASS). But
forward-window strength alone does not overturn the OOS fail.

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`.

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS (2001-05-14 → 2017-12-31)   | 3020 | 0.264 |  1.87% | −24.35% |
| OOS (2018-01-01 → 2023-12-31)  | 1509 | 0.251 |  2.67% | −26.62% |
| FWD (2024-01-01 → 2026-04-14)  |  572 | 1.179 | 16.39% | −12.87% |
| FULL (2006-01-03 → 2026-04-20) | 5105 | 0.322 |  3.70% | −28.86% |
| **SPY OOS benchmark**          | 1509 | 0.658 | 12.00% |     —  |

Portfolio underperforms SPY buy-hold in OOS by **−9.3 pp CAGR** and
carries ~2× the drawdown; IR vs SPY is **−0.63** (gate 8 ≥ 0.3 → FAIL).

## Winner config (baseline)

```
top_n                 = 20
rebalance_days        = 21          [stocks_on_the_move, p.98; brief §design]
use_regime_filter     = True        [stocks_on_the_move, p.66-99]
regression_days       = 90          [stocks_on_the_move, p.73]
per_stock_ma_days     = 100         [stocks_on_the_move, p.81]
market_ma_days        = 200         [stocks_on_the_move, p.66]
gap_threshold         = 0.15        [stocks_on_the_move, p.82]
atr_days              = 20          [stocks_on_the_move, p.88]
atr_risk_factor       = 0.001       [stocks_on_the_move, p.88, p.228-229]
spread_one_way_pct    = 0.0005      [plan §3.2 — Inter stocks]
commission_per_trade  = 0           [plan §3.2 — Inter zero on US ETFs/stocks]
tax_rate              = 0.15        [mandate §1 + plan §3.2 BR CG rate]
adv_usd_floor         = $50M        [stocks_on_the_move, p.238-239 — liquid-large-cap proxy]
universe_size         = 1165 tickers after ADV filter
```

## 13-gate checklist (plan §5; relaxations applied)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0       | > 0    | −1.024 | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0      | > 0    | −0.205 | FAIL |
| 2   | OOS Sharpe ≥ 1.5                     | ≥ 1.5  |  0.251 | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)           | ≥ 13%  |  2.67% | FAIL |
| 3t  | OOS CAGR ≥ 30% (target)              | ≥ 30%  |  2.67% | FAIL |
| 4   | OOS MaxDD ≥ −25%                     | ≥ −25% | −26.62% | FAIL |
| 5   | FWD Sharpe > 0                       | > 0    |  1.179 | PASS |
| 6   | WF 6/8 profitable AND mdd ≤ 30%      | both   | 4/8 mdd=26.62% | FAIL |
| 7   | Median hold ≥ 5 trading days         | ≥ 5d   |  37.0d | PASS |
| 8   | IR vs SPY OOS ≥ 0.3                  | ≥ 0.3  | −0.627 | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp     | deferred | see `cross_lib_check.md` | N/A |
| 10  | Stage-2 data concordance ±1pp        | deferred | only one data source (Tiingo) | N/A |
| 11  | PBO < 0.5 (CSCV 10-block)            | < 0.5  |  0.246 | PASS |
| 12  | DSR p < 0.05                         | < 0.05 |  0.717 | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0  | > 1.0  |  0.226 | FAIL |

**Summary: 3 PASS / 9 FAIL / 2 deferred.** Gates 9 and 10 are deferred
(cross-lib unnecessary when OOS already FAIL; no independent data source
available for Tiingo stock panel). Binding FAILs span both edge-side
(Sharpe, CAGR, DSR, IR, bootstrap CI) and risk-side (MDD, WF, cost×2).

## Which gates killed it

The strategy exhibits a classic **"IS weak + OOS flat + FWD strong"**
profile with high OOS drawdown:

- **OOS 2018-2023** includes the 2022 bear (SPY drawdown −25%), and the
  strategy's SPY-200d regime filter went OFF multiple times. But when
  it went OFF, existing positions continued drifting down per Clenow's
  "do not exit on index breach, only on own criteria" rule
  [stocks_on_the_move, p.94-95], so the portfolio absorbed −26.6% MDD.
- **OOS edge is indistinguishable from noise:** DSR p=0.72 on 5 trials,
  bootstrap 99.9% CI = [−1.02, 1.59] straddles zero, OOS Sharpe 0.25
  is well within random-walk range for a long-only 20-stock basket.
- **Cost×2 (spread 10bps one-way) drops OOS Sharpe to 0.23** — strategy
  is not robust to doubled spreads, though it was never robust to begin with.
- **WF 4/8 profitable** with one window hitting −26.6% MDD — exceeds the
  relaxed 30% cap by less than 4pp, but still fails the 6/8 gate.

The **only encouraging signal is FWD 2024-2026 Sharpe 1.18**, which hints
the post-COVID regime may suit cross-sectional momentum. But FWD is not a
primary gate (stress check only, gate 5 binary > 0); it cannot salvage
the OOS collapse.

## Data-source caveats

1. **Universe is a liquidity proxy, not PIT S&P 500.** Tiingo bulk
   (1695 tickers) mixes surviving large-caps, delisted, mid-caps, and
   a few ADRs. After the ADV≥$50M + weekend-timestamp filter we retain
   1165 tickers. Some pre-2013 survivorship bias is likely (the panel
   is mostly "listed today + a few historical delisted"). Per
   [stocks_on_the_move, p.238-239], true IS validation would need a
   PIT S&P 500 membership panel — not available in this repo.

2. **Stock panel effective start date ≈ 2013-08-19.** Only ~35 of 1165
   tickers have data before 2013; the rest begin 2013 or 2014. This
   means the IS 2001-2017 window effectively delivers ~4.5 years of
   realistic-diversity signal (2014-2017) + ~8 years of degenerate
   low-breadth panel. The structural consequence: **the IS Sharpe 0.26
   is an optimistic upper bound; true pre-2014 Sharpe cannot be
   evaluated.** This is a general Tiingo-bulk limitation, not a bug.

3. **SPY adj_close goes back to 2001** so the 200d regime filter is
   fully honest for the OOS and FWD windows — no issue there.

## Grid sensitivity (5 configs for CPCV/PBO)

| Tag                         | top_n | rebal | regime | Sharpe (full) |
|-----------------------------|------:|------:|:------:|--------------:|
| top10_rebal21_regon         |    10 |   21d | on     |  0.370 |
| top20_rebal21_regon (winner)|    20 |   21d | on     |  0.322 |
| top30_rebal21_regon         |    30 |   21d | on     |  0.322 |
| top20_rebal10_regon         |    20 |   10d | on     |  0.494 |
| top20_rebal21_regoff        |    20 |   21d | off    |  0.382 |

PBO = **0.246** (PASS) — the grid is not overfit; the winner config is
not outperforming its siblings by statistical fluke. The *problem is
that none of the siblings earn an edge either.*

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `daily_returns.parquet` — winner-config honest daily returns.
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 5-config sensitivity grid Sharpe.
- `cross_lib_check.md` — deferral note (gate 9).
- Logs: `logs/phase3_6_a_clenow.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_a_clenow_momentum.py`.
- Runner: `scripts/run_phase3_6_a_clenow_momentum.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion. No pending draft.

## Citations

- Clenow core methodology (ranking, regime filter, sizing):
  `[stocks_on_the_move, p.60-111]`.
- 90-day regression × R² adjusted slope:
  `[stocks_on_the_move, p.75-77, p.81-82]`.
- 200d SPX regime filter: `[stocks_on_the_move, p.66-67, p.98-99]`.
- ATR-based risk-parity sizing: `[stocks_on_the_move, p.86-89, p.228-229]`.
- Anti-optimization discipline (we held Clenow's ranges):
  `[stocks_on_the_move, p.219-220]`.
- Survivorship bias + PIT universe requirement:
  `[stocks_on_the_move, p.238-239]`.
- Lookahead audit + replication protocol:
  `[advances_fin_ml, p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- CSCV PBO: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward: `[advances_fin_ml, ch.11]`.
- Inter broker model: plan `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §3.2
  + memory `project_plano_b_broker_inter.md`.
