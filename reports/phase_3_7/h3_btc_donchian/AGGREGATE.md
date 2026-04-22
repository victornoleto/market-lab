# Phase 3.7 H3.a — BTC Donchian ensemble independent signal (honest validation)

**Date:** 2026-04-23 | **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched `prev_weight × ret` alignment `[advances_fin_ml, p.31-34]`
**Broker path modelled:** Pepperstone BTCUSD CFD rota A — spread **5 bps/side**
(10 bps round-trip), commission **0**, **swap long −0.05556%/day (−20%/yr)**
applied daily on open notional, **swap short +0.02083%/day (+7.5%/yr)**
credited daily, **max leverage 2:1** (retail ASIC/CySEC/DFSA), **NO DARF**
(mandate §2.2 rota A + user decision 2026-04-22).
**Annualisation convention:** **365 days/year** (crypto 24/7, Tiingo BTC
parquet verified 28.57% weekend bars = 2/7 exact).
**Windows:** IS 2015-01-01 → 2019-12-31 (5y, incl 2018 bear) | OOS 2020-01-01
→ 2023-12-31 (4y, COVID + bull run + FTX) | FWD 2024-01-01 → 2026-04-14
(2.3y, ETF approval + post-halving).
**Data source:** `data/tiingo/daily/prices/btcusd.parquet` — 2014-01-01 →
2026-04-14, n=4483 bars, 1281 weekend bars, cross-validated vs Kraken in
Phase 3.7-2 data-sprint (mean diff 0.019%, 100% within 50 bps).

## Verdict: **FAIL (hard gates)**

The BTC Donchian ensemble (10/20/40 lookbacks, ATR-20 k=2 trail, 2-day time
stop) **fails 3 of 5 hard gates and 4 of 9 soft gates** under the honest
rota A engine + swap-aware 2-day hold constraint. OOS Sharpe is **0.181**
(gate 2 ≥ 1.3 → FAIL), OOS CAGR is **+0.52%** vs BTC buy-hold +55.68%
(gate 8 IR ≥ 0.2 → FAIL at −1.00, a full Sharpe unit of negative information).
The bootstrap 99.9% CI on OOS Sharpe is **[−1.34, 1.68]** (straddles zero by
more than a full Sharpe unit; gate 10 HARD → FAIL); on FULL, CI is
**[−0.50, 1.03]** (gate 10b HARD → FAIL). DSR p-value is **0.829**
(gate 12 HARD < 0.05 → FAIL) — well above the 5% threshold. Under cost×2
sensitivity the strategy **loses money**: OOS Sharpe −0.046, CAGR −0.19%
(gate 13 → FAIL).

**Why FAIL**: the 2-day hold cap that is structurally REQUIRED for
Pepperstone crypto CFD viability (long swap −20%/yr would kill any longer
hold) also **capsizes the trend edge**. BTC's 2020-2023 bull run (buy-hold
+55.68% CAGR) is almost entirely captured in runs longer than 2 days;
forcing exit at bar 2 systematically misses the fat right tail that makes
Donchian trend-following work. The strategy does survive as ALMOST-neutral
(cum_spread 4.12% of equity, cum_swap 1.38% of equity over 11 years → cost
drag is small) — the signal just doesn't generate enough per-trade edge to
beat its own friction envelope.

**Gates passed:** PBO 0.063 (well under 0.5 — grid cells are tightly
clustered), cross-lib Δ 0.48 pp OOS CAGR (well under 3 pp — vbt and pandas
agree), FWD Sharpe +0.515, walk-forward 6/8 profitable, median hold 2.0d
(swap-budget-compatible as designed). These confirm the implementation is
honest and the signal IS NOT noise-of-noise — it's just **too weak vs the
benchmark to be a winner**.

**Halt-contract status:** `n_trades` OOS = **78** (≥ 50 threshold — not
sparse-halted). No F2 regression (cross-lib Δ < 10 pp).

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS  (2015-01-01 → 2019-12-31)   | 1823 |  0.383 |  +0.87% |  −2.86% |
| **OOS** (2020-01-01 → 2023-12-31) | **1461** | **0.181** | **+0.52%** | **−5.89%** |
| FWD (2024-01-01 → 2026-04-14)   |  834 |  0.515 |  +1.45% |  −2.69% |
| FULL (2015-01-01 → 2026-04-14)  | 4483 |  0.309 |  +0.80% |  −5.89% |
| **BTC OOS buy-hold benchmark**  | 1461 |  **1.003** | **+55.68%** | **−76.66%** |

Cumulative friction breakdown (FULL): **spread 4.12%** of equity, **swap
1.38%** of equity, commission 0%. Total cost drag ≈ 5.5% over 11 years —
material but not catastrophic. MDD is **tiny** (−5.89% OOS) because the
sizing (risk=1% per trade × 2-bar holds × gross ≤ 1.0) keeps exposure
microscopic most of the time. Running at leverage=2.0 would **not
significantly change** the Sharpe (the ratio is scale-invariant for
deterministic weighting); grid cells at lev=1.0 vs lev=2.0 return
identical Sharpe because the `min(size, max_leverage)` clip is never
binding at this risk level.

## Winner config

```python
H3BTCDonchianConfig(
    lookbacks              = (10, 20, 40),   # Donchian ensemble
    atr_period             = 20,
    atr_multiplier         = 2.0,
    max_hold_days          = 2,              # Pepperstone swap-budget cap
    risk_per_trade         = 0.010,          # 1% per trade
    max_leverage           = 1.0,            # unleveraged base
    spread_bps_per_side    = 5.0,            # Pepperstone BTC proxy
    commission_bps         = 0.0,            # crypto CFD free
    swap_long_daily        = -0.0005556,     # Pepperstone −20%/yr
    swap_short_daily       = +0.0002083,     # Pepperstone +7.5%/yr
    allow_short            = True,
)
```

**Signal rule.** At close(t):
```
upper[t-1] = max_over_N_in_{10,20,40}( high.rolling(N).max().shift(1) )
lower[t-1] = min_over_N_in_{10,20,40}( low.rolling(N).min().shift(1) )
if flat:
    if close[t] > upper[t-1]:   long at close[t],  size = 0.01 · c / (2 · ATR_20[t-1])
    elif close[t] < lower[t-1]: short at close[t], size = −0.01 · c / (2 · ATR_20[t-1])
if long and close[t] < trailing_max − 2 · ATR_20[t-1]:   exit (atr_trail)
if long  and bars_open >= 2:                              exit (time_stop)
if short, symmetric
```

Signal and sizing **cite** `[zarattini_pagani_barbon_2025]` for the
ensemble Donchian + vol-based sizing framing, `[universal_trend_tactics,
p.295-299, p.338-343]` for the Donchian-breakout + ATR-trail canonical
pattern (same as Phase 3.6 Family K).

## 13-gate checklist (rota A Pepperstone, mandate §2.4 + 3.7-3 recalib)

| # | Gate | Level | Threshold | Value | Pass |
|---|------|:-----:|-----------|------:|:----:|
| 1   | IS Sharpe > 0.5                                 | soft    | > 0.5  | 0.383 | **FAIL** |
| 2   | OOS Sharpe ≥ 1.3                                | soft    | ≥ 1.3  | 0.181 | **FAIL** |
| 3   | OOS CAGR tier (rota A)                          | warning | classify | +0.52% → **Folclore** | WARN |
| 4   | OOS MaxDD tier (rota A)                         | warning | classify | −5.89% → **Excelente** | WARN |
| 5   | FWD Sharpe > 0                                  | soft    | > 0    | 0.515 | **PASS** |
| 6   | Walk-forward 6/8 profitable                     | soft    | ≥ 6/8  | 6/8  max_mdd=4.76% | **PASS** |
| 7   | Median hold ≤ 2d AND > 0 (swap-budget)          | soft    | ≤ 2d & > 0 | 2.00d | **PASS** |
| 8   | IR vs BTC buy-hold OOS ≥ 0.2                    | soft    | ≥ 0.2  | −1.00 | **FAIL** |
| 9   | Cross-lib concordance ±3 pp OOS CAGR            | **hard** | ≤ 3 pp | 0.48 pp (vbt vs pandas) | **PASS** |
| 10  | Bootstrap OOS 99.9% CI low > 0                  | **hard** | > 0    | −1.34 | **FAIL** |
| 10b | Bootstrap FULL 99.9% CI low > 0                 | **hard** | > 0    | −0.50 | **FAIL** |
| 11  | PBO < 0.5                                       | **hard** | < 0.5  | 0.0635 | **PASS** |
| 12  | DSR p < 0.05                                    | **hard** | < 0.05 | 0.829 | **FAIL** |
| 13  | Cost×2 OOS Sharpe > 1.0 (unleveraged)           | soft    | > 1.0  | −0.046 | **FAIL** |

**Hard gate summary:** 2/5 pass (cross-lib + PBO). 3/5 hard fail — the
bootstrap CIs straddle zero and DSR p=0.83 says "observed Sharpe is
almost certainly luck given 6 trials". Under the 3.7-3 hunt rule
(bootstrap OBRIGATÓRIO on crypto due to high vol + fresh data), these
are dispositive.

**Soft gate summary:** 4/9 fail. Gate 5/6/7 pass (strategy is stable
across FWD and across walk-forward windows; holds are clean 2-day).
Gate 8 (IR vs BTC) is the most damning: −1.00 means the strategy
underperforms BTC buy-hold by **one full standard deviation of daily
excess returns, annualised**. The 2-day hold cap gives up 55 pp CAGR
to avoid the −20%/yr long-swap tax.

## Grid sensitivity (6 configs — PBO basis)

| Tag | risk | max_lev | allow_short | n_trades | Sharpe_full |
|---|---:|---:|:---:|---:|---:|
| r005_lev1_short     | 0.005 | 1.0 | ✓ | 161 | 0.309 |
| r010_lev1_short     | 0.010 | 1.0 | ✓ | 161 | 0.309 |
| r015_lev1_short     | 0.015 | 1.0 | ✓ | 161 | 0.309 |
| r010_lev2_short     | 0.010 | 2.0 | ✓ | 161 | 0.309 |
| r010_lev1_longonly  | 0.010 | 1.0 | ✗ | 104 | **0.497** |
| r010_lev2_longonly  | 0.010 | 2.0 | ✗ | 104 | **0.497** |

Observations: (a) Sharpe is **invariant to `risk_per_trade` and
`max_leverage`** because the ratio is scale-invariant and the max-lev
clip is non-binding at 1% per-trade risk. (b) Disabling shorts
**improves** full-period Sharpe from 0.31 to 0.50 — the 57 short
trades in the full-series degrade the edge (consistent with crypto
bull-bias over 2015-2026; shorts get whipsawed). (c) Six cells give
PBO=0.0635 (very low — the grid doesn't find one "lucky cell"; all
cells agree on the weak edge).

## Bootstrap CIs (99.9% stationary block, n_resamples=2000, block_mean=5)

| Split | Annual Sharpe 99.9% CI | Midpoint | Pass (>0 lower) |
|-------|-----------------------:|---------:|:---------------:|
| OOS   | [−1.3374, +1.6780]     |  +0.17   | **FAIL**        |
| FULL  | [−0.5015, +1.0332]     |  +0.27   | **FAIL**        |

The CIs are **dominated by BTC's raw daily volatility**: crypto daily
σ ≈ 4% vs SPY's ≈ 1%, so 99.9% CIs are ~4× as wide as they would be
on an equity strategy of equal Sharpe. Even at Sharpe 1.0 on crypto,
the 99.9% CI width ≈ 1.4 units; at Sharpe 0.18 we're nowhere near
clearing zero.

## DSR (deflated Sharpe, 6 trials)

| Quantity | Value |
|---|---:|
| Observed Sharpe (OOS, periodic) | 0.0095 |
| Benchmark Sharpe (E[max] under 6 iid trials) | ≈ 0.05 |
| DSR (= PSR at benchmark) | 0.171 |
| **p-value** | **0.829** |
| Pass (< 0.05) | **FAIL** |

Reading: there is an 83% probability that the observed OOS Sharpe
reflects **selection/luck among 6 related configurations** rather than
true skill. This is consistent with the grid cells clustering tightly
(5/6 share Sharpe 0.31, 2/6 share 0.50) — there is no dominant winner,
only a family of weak-edge variants.

## Cross-library concordance (vbt vs pandas reference, OOS)

| Library | CAGR OOS | Δ vs pandas |
|---|---:|---:|
| pandas (reference) | +0.52% | — |
| vectorbt `Portfolio.from_signals` | +1.00% | **0.48 pp** |

Gate 9 threshold is 3.0 pp → **PASS**. The 0.48 pp drift comes from
vbt applying fees as percent-of-notional (fees=spread/10,000 per side)
and using its internal target-percent sizing aggregation, which differs
from our additive F2 alignment + daily swap accrual. Neither library
handles swap identically, so 0.48 pp is the residual implementation
difference — well within tolerance and not pathological.

## PBO (CSCV, 10 blocks, 6 configs, 252 combinations)

| Quantity | Value |
|---|---:|
| PBO | **0.0635** |
| n_blocks | 10 |
| n_combinations | 252 |
| Pass (< 0.5) | **PASS** |

Only ~6.35% of CSCV pair-splits rank the IS-winner below OOS median —
the configs really ARE homogeneous (no cherry-picking benefit). This
is the cleanest gate in the whole sheet, and it's consistent with the
DSR reading: the grid isn't finding noise, it's finding a weak-but-
real edge that is **too weak to beat its cost envelope on this
asset at this hold horizon**.

## Stress-period breakdown

| Period | Window | n | Sharpe | Total return |
|---|---|---:|---:|---:|
| **2018 bear** (BTC −73% buy-hold)     | 2018-01-01 → 2018-12-31 | 365 | +0.47 | +0.35% |
| **COVID crash** (BTC −50% in 8 days)  | 2020-02-01 → 2020-04-30 |  90 | +1.22 | +1.07% |
| **FTX collapse** (BTC −22%)            | 2022-11-01 → 2022-12-31 |  61 | −2.14 | −1.01% |
| **ETF rally** (BTC +61% Q1 2024)      | 2024-01-01 → 2024-03-31 |  91 | +1.18 | +1.48% |

Reading: the strategy **protects capital in bear markets** (2018 +0.35%
vs buy-hold −73%; COVID +1.07% vs buy-hold flat by end-of-April) but
**gets whipsawed in fast regime transitions** (FTX Nov 2022 Sharpe
−2.14 — Donchian breaks trigger short entries on the dump and then
time-stop-out at mini-rebounds). In the ETF rally it captures some
upside (+1.48%) but at a fraction of buy-hold (+61%) because the 2-day
cap releases the trade before the trend develops.

## Halt-contract audit

1. **Sparse-signal halt** — n_trades OOS = **78** (threshold: ≥ 50).
   **NOT TRIGGERED**. Signal has adequate trade frequency on OOS.
2. **F2 engine regression halt** — cross-lib Δ = **0.48 pp** (threshold:
   ≤ 10 pp). **NOT TRIGGERED**. Engine is consistent with vectorbt.
3. **PBO ≥ 0.5 / DSR p > 0.05 / cross-lib > 3 pp** — PBO PASS, DSR
   **FAIL**, cross-lib PASS. DSR alone is dispositive per gate 12 HARD.

## Why the signal weakness is structural, not engineering

The Zarattini-Pagani-Barbon 2025 paper reports Sharpe > 1.5 net-of-fees
+ alpha 10.8%/yr vs BTC buy-hold in their **rotational top-20 crypto
portfolio**. Our reformulation to an **independent signal per asset**
(forced by Pepperstone's BTC-only universe per Phase 3.7-2 data-sprint
§6.3) removes two load-bearing components of the paper's edge:

1. **Cross-sectional diversification** across 20 assets — each asset
   contributes moderate Sharpe; portfolio Sharpe benefits from low
   inter-asset correlation. N=1 loses this entirely.
2. **Relative-strength selection** — rotational picks the top-momentum
   names and discards laggards. With N=1 fixed, every signal is taken
   regardless of relative rank.

PLUS our additional constraint — the **2-day hold cap** mandated by
Pepperstone's −20%/yr long swap — is materially more aggressive than
the paper's implicit hold (not specified, but their rotation cadence
is weekly→monthly based on Donchian 40d). The paper isn't burdened with
our swap structure.

Net: the paper result **may well be real**, but our broker-constrained
reformulation doesn't preserve it. This is a clean "structural FAIL,
not implementation FAIL" — gates 9/11 PASS confirm the engine.

## What could be tried next (NOT promoted to a winner)

The following are **hypotheses for a future Phase 3.7-4**, not
recommendations to promote H3.a:

1. **Relax `max_hold_days` to 5 and 10** — test whether the long-swap
   loss (−0.28% to −0.56% per trade) is more than offset by additional
   trend-capture. If 5-day net Sharpe > 1.0, the 2-day cap is the
   binding friction; if not, the signal is weak regardless.
2. **Long-only Donchian with 40-day single lookback** — the ensemble
   filter's slowest channel is 40; test whether the ensemble actually
   improves on Turtle-40 alone (grid shows long-only helps +0.19 Sharpe
   points already).
3. **Combine with H3.b ETH** as a 2-asset allocation — if the ETH leg
   passes individually and correlations are moderate, the combination
   could give Sharpe > 1.0 even with each leg below. Caveat: Phase
   3.7-2 data-sprint §6.3 warned that N=2 has minimal rotation benefit.

All three are **research leads**, not validation runs; they require
re-specifying the pre-registered grid and re-running CSCV/DSR on the
expanded grid to avoid snooping the OOS window we just looked at.

## Files

| File | Purpose |
|---|---|
| `AGGREGATE.json`                         | Structured machine-readable audit log. |
| `AGGREGATE.md` (this file)               | Narrative report. |
| `daily_returns_winner.parquet`           | F2-aligned net daily returns, full series. |
| `daily_returns_cost2x.parquet`           | Cost×2 sensitivity daily returns. |
| `config_grid.csv`                        | 6-config grid meta + Sharpe_full. |
| `src/ai_trade/backtest/strategies/phase3_7_h3_btc_donchian.py` | Strategy module. |
| `scripts/phase3_7/run_h3_btc_donchian.py` | Runner. |
| `tests/test_phase3_7_h3_btc_donchian.py`  | 4 smoke tests (Donchian, time-stop, ATR, ATR warmup). |

**Commit will be atomic** regardless of verdict per hunt prompt.
Mandate §7 and strategy docs remain UNTOUCHED. FAIL = no promotion.
