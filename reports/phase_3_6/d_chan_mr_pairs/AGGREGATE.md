# Phase 3.6 Family D — Chan-style cointegrated MR pairs (non-Kalman)

**Date:** 2026-04-22  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Pepperstone Razor CFD (plan §3.1) —
spread 5 bps/leg, commission $0.35/100k notional/leg, swap −0.02%/night/leg,
no BR 15% CG tax (non-BR-source).
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 |
FWD 2024-01-01 → 2026-04-14 (effective IS start 2007-04-11, HYG inception).

## Verdict: **FAIL**

The Chan-style **non-Kalman** pair MR strategy (rolling-OLS hedge ratio
+ Engle-Granger gate + z-score bands) fails **9 of 13 gates** under the
honest engine on 5 sector-peer ETF pairs. **Unlike the prior V2-L5
Kalman-variant failure (0 trades generated), this variant DOES trade**
(57 round-trips across the 2007-2026 span, median hold 10d) — so the
failure is edge-side, not structural-tradability-side. The edge is
statistically indistinguishable from zero: OOS Sharpe **−0.51**, OOS
CAGR **−0.33%**, bootstrap 99.9% CI **[−1.37, +0.50]** straddles zero,
DSR p-value **0.996** (gate 12 ≤ 0.05 → FAIL), IR vs SPY OOS **−0.67**.

Positive signals: median hold **10d** (gate 7 PASS), WF max-window DD
**−1.68%** (cap 30% — but only 2/8 windows profitable so gate 6 FAIL),
OOS MaxDD **−2.37%** (gate 4 PASS — strategy is at least not blowing
up), FWD Sharpe **+1.23** (gate 5 PASS — post-COVID regime hints at
possible regime-conditional edge), PBO **0.302** (gate 11 PASS — grid
is not overfit, the siblings are uniformly mediocre), cross-lib Δ
**0.37pp** (gate 9 PASS — canonical mechanics reconcile to independent
hand-rolled numpy impl).

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no pending draft in `docs/.pending/`.

## Top-line metrics

| Split                          | Bars | Sharpe |   CAGR |   MaxDD |
|--------------------------------|-----:|-------:|-------:|--------:|
| IS  (2007-04-11 → 2017-12-31)  | 2705 | −0.221 | −0.05% |  −0.63% |
| OOS (2018-01-01 → 2023-12-31)  | 1509 | −0.511 | −0.33% |  −2.37% |
| FWD (2024-01-01 → 2026-04-14)  |  570 | +1.233 | +0.25% |  −0.12% |
| FULL (2007-04-11 → 2026-04-15) | 4784 | −0.251 | −0.11% |  −2.46% |
| **SPY OOS benchmark**          | 1509 | +0.658 | 12.00% |    —    |

Portfolio returns are near-zero by construction (the strategy is
market-neutral per-pair and only 5 × 5% = 25% max gross when all pairs
are simultaneously signalling). The realized *volatility* is also near
zero (annualized ~0.7%), so even a small negative drift translates to a
decisively negative Sharpe. Against SPY OOS buy-hold's 12% CAGR /
0.658 Sharpe, the IR is **−0.67**.

## Winner config (baseline)

```
lookback                  = 126 trading days   [algo_trading_chan, p.47; half-life proxy]
entry_z                   = 2.0                [algo_trading_chan, p.71-72]
exit_z                    = 0.0                [algo_trading_chan, p.71-72; mean-cross]
stop_z                    = 4.0                [algo_trading_chan, p.183-184; above backtest DD]
coint_pvalue_gate         = 0.10               [algo_trading_chan, p.54; pragmatic threshold]
per_pair_gross_pct        = 0.05               [plan §5; 5% × 5 pairs × 2 legs ≤ 50% gross]
spread_one_way_pct        = 0.0005             [plan §3.1; Pepperstone sector-ETF CFD]
commission_per_trade_pct  = 0.000035           [plan §3.1; Razor $0.35/100k]
swap_per_night_pct        = 0.0002             [plan §3.1; Razor overnight]
tax_rate                  = 0.0                [plan §3.1; Pepperstone non-BR]
Pairs:
  (XLE, USO)    energy equity vs oil — commodity-beta factor  [algo_trading_chan, p.116-120]
  (TLT, IEF)    20y vs 10y Treasuries — duration factor        [algo_trading_chan, p.52-53]
  (HYG, LQD)    high-yield vs investment-grade — credit        [quant_trading_chan, ch.3]
  (GLD, SLV)    gold vs silver — precious-metals               [algo_trading_chan, p.52]
  (XLU, XLP)    utilities vs staples — defensive-equity        [algo_trading_chan, p.88-89]
```

## 13-gate checklist (plan §5; user-locked relaxations)

| # | Gate                                    | Threshold | Value                | Pass |
|---|-----------------------------------------|-----------|---------------------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0        | > 0       | −1.3650              | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0       | > 0       | −0.7942              | FAIL |
| 2   | OOS Sharpe ≥ 1.5                      | ≥ 1.5     | −0.511               | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)            | ≥ 13%     | −0.33%               | FAIL |
| 3t  | OOS CAGR ≥ 30% (target)               | ≥ 30%     | −0.33%               | FAIL |
| 4   | OOS MaxDD ≥ −25%                      | ≥ −25%    | −2.37%               | PASS |
| 5   | FWD Sharpe > 0                        | > 0       | +1.233               | PASS |
| 6   | WF 6/8 profitable AND mdd ≤ 30%       | both      | 2/8, mdd=−1.68%      | FAIL |
| 7   | Median hold ≥ 5 trading days          | ≥ 5d      | 10.0d                | PASS |
| 8   | IR vs SPY OOS ≥ 0.3                   | ≥ 0.3     | −0.6728              | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp      | ≤ 3pp     | Δ=0.371pp (canonical↔hand) | PASS |
| 10  | Stage-2 data concordance ±1pp         | deferred  | only Tiingo          | N/A  |
| 11  | PBO < 0.5 (CSCV 10-block)             | < 0.5     | 0.3016               | PASS |
| 12  | DSR p < 0.05                          | < 0.05    | 0.9959               | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0   | > 1.0     | −0.738               | FAIL |

**Summary: 5 PASS / 8 FAIL / 1 deferred.** Gate 10 is deferred (no
independent data source for Tiingo ETF adj_close — would need
testfolio/Yahoo triangulation). The binding FAILs span every edge-side
gate (Sharpe, CAGR, DSR, bootstrap, IR, WF profitability) plus the
cost×2 stress, while the risk-side gates (MDD, FWD) and overfit
sanity (PBO, cross-lib) all PASS. The profile is **"no edge, small
exposure"** — the strategy is not dangerous, it's just inert.

## Which gates killed it

The strategy exhibits a **"no-edge-after-costs"** profile:

- **Cointegration gate is restrictive in modern data.** Only 10-21% of
  bars per pair pass EG p ≤ 0.10 (totals: XLE/USO 504, TLT/IEF 441,
  HYG/LQD 1008, GLD/SLV 483, XLU/XLP 736 of 4784 bars). When the gate
  is OFF the pair sits flat — zero contribution. When it's ON the
  z-score signal fires ~2-3 entries per year per pair. Chan's caveat
  `[algo_trading_chan, p.88-89]` is vindicated: ETF pair cointegration
  is a structurally-compressing phenomenon.
- **Edge is indistinguishable from zero:** DSR p=0.996 on 6 trials,
  bootstrap 99.9% CI [−1.37, +0.50] straddles zero. OOS Sharpe −0.51
  is negative but well inside single-block noise.
- **Cost×2 (spread 10 bps/leg + swap 4 bps/night/leg) drops OOS Sharpe
  to −0.74** — not a black swan, just the same edge-free signal with a
  slightly bigger cost penalty.
- **WF 2/8 profitable** despite tiny drawdowns — profitability is the
  binding failure, not risk. The strategy simply doesn't generate enough
  favorable-z entries to overcome the cumulative small drags.
- **FWD Sharpe +1.23** is the only bright spot. If this persists it
  would hint at a 2024-2026 regime where ETF pair cointegration is
  partly restored (post-rate-hike normalization?). But a single
  2.3-year stress window is not a primary gate — it cannot salvage OOS.

## Contrast vs V2-L5 (Kalman variant, phase 3.5f)

V2-L5 FAILED structurally: 0/6 pairs passed ADF `p ≤ 0.05` → 0 trades.
Family D (non-Kalman, this report) trades 57 round-trips but the trades
don't produce edge. **The two families share a single root cause:** the
liquid-ETF pair space is too efficient for classical stat-arb methods
(regardless of whether the hedge ratio is static/rolling or Kalman-
adaptive). Chan already flagged this in 2013 `[algo_trading_chan, p.88-89]`:
"Stock pairs trading has become very difficult: stocks rarely remain
cointegrated out-of-sample because corporate fundamentals change
rapidly. Large losses from pairs that 'go bad' overwhelm gains from
good pairs." ETF pairs are strictly worse than stock pairs on this
dimension because ETFs aggregate fundamentals.

## Data-source caveats

1. **IS is truncated ~6 years left.** The plan's IS starts 2001-05-14,
   but HYG inception is 2007-04-11 so the intersection of all 5 pairs
   starts there. This is documented per the brief's instruction
   ("trim IS honestly, do not backfill with proxies silently"). The
   strategy has 2705 IS bars (~10.75 years) — sufficient for statistical
   assessment but not for the full intended span.

2. **Cointegration estimated at stride=21 bars** (monthly refresh),
   then forward-filled until next evaluation. `statsmodels.tsa.stattools.coint`
   on rolling windows is computationally expensive; the stride is a
   principled approximation since EG p-values on 126-bar windows move
   slowly. Documented for reproducibility.

3. **Pepperstone swap assumption (−2 bps/night/leg)** is the Oct-2024
   reference from `project_broker_decision.md`. Actual swap varies by
   the funding-rate differential; a period of ultra-low rates (2010-2021)
   would have had tighter swaps and marginally improved the cost
   sensitivity. Per plan §3.1 this is the standardized assumption.

## Grid sensitivity (6 configs for CPCV/PBO + DSR)

| tag                                  | lookback | entry_z | exit_z | stop_z | Sharpe (full) |
|--------------------------------------|---------:|--------:|-------:|-------:|--------------:|
| lb60_enter2.0_exit0.0_stop4.0        |    60    |   2.0   |   0.0  |   4.0  |    −0.542     |
| lb126_enter2.0_exit0.0_stop4.0 (winner) | 126   |   2.0   |   0.0  |   4.0  |    −0.251     |
| lb252_enter2.0_exit0.0_stop4.0       |   252    |   2.0   |   0.0  |   4.0  |    −0.468     |
| lb126_enter1.5_exit0.0_stop4.0       |   126    |   1.5   |   0.0  |   4.0  |    −0.484     |
| lb126_enter2.5_exit0.5_stop4.0       |   126    |   2.5   |   0.5  |   4.0  |    −0.162     |
| lb126_enter2.0_exit0.5_stop3.5       |   126    |   2.0   |   0.5  |   3.5  |    −0.172     |

PBO = **0.3016** (PASS) — the winner is not overfit; every sibling
produces similarly unimpressive numbers. The *problem is that no config
generates positive edge.*

## Per-pair cointegration + trade counts (winner cfg)

| pair                 |  y  |  x  | total_bars | coint_bars | coint % | trades |
|----------------------|:---:|:---:|-----------:|-----------:|--------:|-------:|
| energy_xle_uso       | XLE | USO |       4784 |        504 |   10.5% |     13 |
| bonds_tlt_ief        | TLT | IEF |       4784 |        441 |    9.2% |      9 |
| credit_hyg_lqd       | HYG | LQD |       4784 |       1008 |   21.1% |     14 |
| metals_gld_slv       | GLD | SLV |       4784 |        483 |   10.1% |      6 |
| defensives_xlu_xlp   | XLU | XLP |       4784 |        736 |   15.4% |     15 |

Note how HYG/LQD is the most-often cointegrated (21%) — makes economic
sense (same underlying credit/rate factor) — but still fails to generate
edge. Even in the "best" pair, 79% of bars sit flat.

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `daily_returns.parquet` — winner-config honest daily returns.
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 6-config sensitivity grid Sharpe.
- `cross_lib_check.md` + `cross_lib_check.json` — canonical vs
  hand-rolled-numpy reconciliation (Δ 0.37pp, PASS).
- Logs: `logs/phase3_6_d_chan_mr_pairs.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_d_chan_mr_pairs.py`.
- Runner: `scripts/run_phase3_6_d_chan_mr_pairs.py`.
- Cross-lib runner: `scripts/run_phase3_6_d_cross_lib.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** Verdict is FAIL. No promotion, no pending draft.

## Citations

- Chan pairs methodology (cointegration test, z-score bands, Bollinger
  entry/exit): `[algo_trading_chan, p.51-73, p.94]`.
- Rolling OLS hedge ratio vs Kalman contrast:
  `[algo_trading_chan, ch.3 p.65-80]`.
- Half-life lookback heuristic: `[algo_trading_chan, p.47-48]`.
- Sector-peer pair selection: `[algo_trading_chan, p.52, p.88-89]`.
- ETF pair-edge compression caveat: `[algo_trading_chan, p.88-89]`.
- Stop-loss above backtest max DD: `[algo_trading_chan, p.183-184]`.
- Lookahead audit + replication protocol:
  `[advances_fin_ml, p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- CSCV PBO: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward: `[advances_fin_ml, ch.11]`.
- Pepperstone broker model: plan `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §3.1
  + memory `project_broker_decision.md`.
- V2-L5 Kalman-variant DEAD reconfirm:
  `reports/phase_3_5f/honest_revalidation/v2_l5_kalman/AGGREGATE.md`.
