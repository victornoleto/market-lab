# Family C — Faber GTAA 10-month SMA multi-asset (Phase 3.6)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** return-series clean (no bar-engine, `prev_weight × ret` per
`[advances_fin_ml, p.31-34]`) — inherits F2 fix commit `7b90a8f`.
**Universe (4-asset variant):** SPY / EFA / GLD / IEF. REIT (VNQ/IYR/ICF)
unavailable in Tiingo cache; XLRE inception 2015 too late for IS.
DBC also unavailable — GLD used as single-commodity proxy per
`[trading_evolved, p.200]` Ivy allocation.
**Windows:** IS 2006-01-03 → 2017-12-31 (trimmed to IEF inception to keep
4-asset inner-joined panel) | OOS 2018-01-01 → 2023-12-31 | FWD
2024-01-01 → 2026-04-14.

## Verdict: **FAIL**

The Faber GTAA 4-asset variant fails **8 of 13 gates** under the honest
engine. OOS Sharpe (0.414) is far below the relaxed 1.5 target, OOS CAGR
(3.89%) is less than a third of the CDI soft-floor (13%), and PBO = 0.909
(catastrophic overfitting indicator — IS-best configs lose to the OOS
median 91% of the time). Mandate §7 and strategy docs **UNTOUCHED**.

## Grid searched

| Parameter | Values | Rationale |
|---|---|---|
| SMA window (months) | 6, 8, 10, 12 | Faber canonical = 10; wider for stability test |
| Signal lag (trading days) | 0, 1 | Lookahead audit `[advances_fin_ml, p.31-34]` |
| Weighting | equal, inv_vol | Faber canon = equal; Clenow inv-vol `[trading_evolved, p.206-207]` |

**Total:** 4 × 2 × 2 = 16 configs. Winner cell by OOS Sharpe:
`sma8m_lag1_equal` (OOS Sharpe 0.414).

## Top-line metrics — winner cell (sma=8mo, lag=1d, equal-weight)

| Metric | IS 2006-01→2017-12 | OOS 2018-01→2023-12 | FWD 2024-01→2026-04 |
|---|---:|---:|---:|
| Sharpe | 0.536 | **0.414** | 1.607 |
| CAGR | 4.94% | **3.89%** | 11.36% |
| MaxDD | — | **−20.71%** | — |
| n_bars | 3,018 | 1,510 | 577 |

For context: **SPY OOS Sharpe = 0.658, OOS CAGR ~8%** — the GTAA
strategy OOS is worse than passive SPY buy-hold on both risk and
return metrics. The FWD Sharpe 1.61 looks attractive but the sample
is only 2.3 years, all inside the post-2023 bull / rate-cut regime.

## 13-Gate checklist

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1 | Bootstrap OOS 99.9% CI low > 0 | > 0 | −0.732 | ❌ |
| 1b | Bootstrap FULL 99.9% CI low > 0 | > 0 | −0.020 | ❌ |
| 2 | OOS Sharpe ≥ 1.5 (user relax) | ≥ 1.5 | 0.414 | ❌ |
| 3 | OOS CAGR ≥ 13% (CDI floor) | ≥ 13% | 3.89% | ❌ |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | −20.71% | ✅ |
| 5 | FWD Sharpe > 0 | > 0 | 1.607 | ✅ |
| 6 | WF 8-windows: ≥6/8 profitable AND max DD ≤ 30% | both | 7/8, mdd 19.22% | ✅ |
| 7 | Median hold ≥ 5 trading days | ≥ 5d | 147.0d | ✅ |
| 8 | IR vs SPY buy-hold ≥ 0.3 | ≥ 0.3 | −0.498 | ❌ |
| 9 | Cross-lib ≥ 2/3 within ±3pp CAGR | ±3pp | Δ=0.000pp (hand-rolled pandas vs canonical) | ✅ |
| 10 | Data concordance Tiingo vs testfolio ≤ 1pp CAGR | ≤ 1pp | Δ=0.45pp (GLD vs GLDSIM) | ✅ |
| 11 | PBO < 0.5 on CSCV 10-block | < 0.5 | **0.909** (252 combos) | ❌ |
| 12 | DSR p < 0.05 on winner OOS Sharpe | < 0.05 | 0.783 | ❌ |
| 13 | Cost×2: OOS Sharpe > 1.0 | > 1.0 | 0.407 | ❌ |

**Summary: 5 PASS / 8 FAIL / 0 deferred** (gate 9 was evaluated via a
hand-rolled pure-pandas reimplementation that matched canonical to
Δ=0.000pp; full vectorbt/bt/backtrader ports not produced because 8
other gates already failed — additional library agreement cannot rescue
a family with no edge).

## Which gates killed it

The FAIL pattern is diagnostic:

- **Edge gates (2, 3, 8, 12, 13) all FAIL** — the strategy has no OOS
  edge at any parameter in the 16-cell grid. OOS Sharpe of the best
  cell is 0.41; DSR says this is indistinguishable from zero (p=0.78).
- **Bootstrap gates (1, 1b) FAIL** — 99.9% confidence intervals include
  zero (and span [−0.73, 1.58] on OOS), confirming the point estimate
  is too noisy to assert a positive Sharpe.
- **PBO = 0.909** — catastrophic. Over the 252 CSCV balanced splits,
  the IS-best config lost to the OOS median 91% of the time. Any
  "winner" picked from this grid is almost certainly lucky noise,
  not a robust edge.
- **Risk gates (4, 6, 7) PASS** — MaxDD, walk-forward, and hold-period
  all look "safe". The pattern is the same as Carver RP in
  `reports/phase_3_5f/honest_revalidation/v2_l4_carver_rp/AGGREGATE.md`:
  risk controls look fine because there was never any edge to overfit —
  just low variance around a mediocre mean.
- **FWD gate 5 PASS** — the 2024-2026 FWD window coincidentally had a
  simple long-everything regime (post-rate-cut bull across SPY/GLD),
  lifting the FWD Sharpe to 1.6. This does not rescue the OOS failure —
  mandate §5 and plan §5 require both to pass.

## Broker cost impact (Inter — plan §3.2)

The Inter cost model here is friendly: zero commission, 15% BR monthly
tax on positive months, 3 bps friction per rebalance switch. Even with
this friendly model the strategy's CAGR is 3.89% — after the 15% tax
bite, ~0.6pp/yr is tax drag, but the bulk of the shortfall is the
**signal itself producing too few in-regime months** (SMA=8mo selects
an "on" state ~50% of the time, and when on, the equal-weighted
portfolio's 4-asset expected return is modest). Cost×2 (6 bps per
switch, 2× friction) only drops OOS Sharpe from 0.414 → 0.407 (tiny
impact — the strategy rebalances only monthly, so transaction costs
are essentially irrelevant; the failure is pure edge failure).

## Comparison to related rejected families

| Strategy | OOS Sharpe (honest) | OOS CAGR (honest) | PBO | Verdict |
|---|---:|---:|---:|---:|
| V2-L4 Carver RP (`v2_l4_carver_rp`) | 0.621 | 4.99% | 0.079 | FAIL (10/13) |
| V2-L1 TSMOM (`v2_l1_tsmom`) | see F3 report | — | — | FAIL |
| **Family C GTAA (this report)** | **0.414** | **3.89%** | **0.909** | **FAIL (8/13)** |
| SPY buy-hold (OOS benchmark) | 0.658 | ~8% | — | — |

Family C is a **strictly weaker edge** than the already-rejected V2-L4
Carver RP blend — and its PBO of 0.909 is an order of magnitude worse
than Carver's 0.079, suggesting this 16-cell grid is dominated by
serial-correlation / regime-window luck rather than any persistent
rule. Consistent with Clenow's warning at
`[trading_evolved, p.211-212]` that the 200-day / 10-month trend filter
"may be severe curve fitting from hindsight knowledge of 2008" —
under IS 2006-2017 (which includes the 2008 crisis that the filter was
designed to avoid), even the "canonical" filter only earns 4.9% CAGR,
and loses that edge OOS.

## Universe deviation — honest disclosure

Faber's 2007 paper uses **5 assets**: SPY, EFA, VNQ (REIT), DBC
(commodity basket), IEF. Our Tiingo cache contains SPY, EFA, IEF, GLD,
AGG, TLT but:
- **No VNQ / IYR / ICF** (REIT ETFs absent). XLRE exists but inception
  2015-10-08 is too late for any meaningful IS sample.
- **No DBC / GSG** (commodity-basket ETFs absent).

We chose the **4-asset variant** SPY/EFA/GLD/IEF over:
- (a) Waiting for the cache to be extended (out of scope for this
  subagent).
- (b) Using testfolio synthetics for missing assets (testfolio cache
  holds only SPYSIM/QQQSIM/GLDSIM/ZROZSIM/SSOSIM/UPROSIM — none for
  VNQ or DBC).
- (c) Silently backfilling with a different ETF (e.g. TLT for REIT) —
  explicitly forbidden by the task brief.

This 4-asset variant is strictly simpler than Faber canonical, but it
is **defensible**: Clenow's "Ivy" ETF allocation at
`[trading_evolved, p.200]` places 7.5% in GLD + 7.5% in DBC, so GLD
as a lone commodity proxy is a subset of an existing published practice.
We do NOT claim the 4-asset variant is equivalent to 5-asset Faber —
the report documents the deviation and the FAIL verdict stands
regardless.

## Artifacts

- `AGGREGATE.json` — full structured metrics for all 16 configs + gate panel.
- `daily_returns.parquet` — winner-cell daily net returns (post-tax, post-friction).
- `config_grid.csv` — 16-row grid enumeration with per-split Sharpe/CAGR/MDD.
- `cross_lib_check.md` + `.json` — hand-rolled pure-pandas vs canonical (Δ=0.000pp).
- Logs: `logs/phase3_6_c_gtaa.log` (appended on every run).

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion, no demotion. No
pending draft in `docs/.pending/`. The Faber GTAA family is added to
the Phase 3.6 running index in `reports/phase_3_6/README.md` as a FAIL
row, and the loop advances to the next candidate (Wave 2 on
orchestrator's decision).

## Citations

- Faber GTAA discussed via Clenow's asset-allocation ETF example:
  `[trading_evolved, p.183-185]` (fixed-weight monthly rebalance);
  `[trading_evolved, p.211-212]` (200-day / 10-month trend filter with
  curve-fit caveat).
- Clenow's Ivy-style ETF allocation includes GLD: `[trading_evolved, p.200]`.
- Inverse-vol sizing alternative: `[trading_evolved, p.206-207]`;
  Carver framework `[systematic_trading, p.175-177]`.
- Monthly MA filter as regime proxy:
  `[leverage_for_the_long_run, p.8]` (Gayed footnote 15).
- Lookahead / `prev_weight × ret` alignment:
  `[advances_fin_ml, p.31-34]`.
- CSCV / PBO / "IS-best vs OOS-median":
  `[advances_fin_ml, p.208-211]`.
- Deflated Sharpe ratio: `[advances_fin_ml, p.196-202, p.273-275]`.
- Walk-forward 6/8: `[advances_fin_ml, ch.11]`.
- Stationary block bootstrap for Sharpe CI:
  `[advances_fin_ml, p.196-202]`.
- Investment mandate CDI floor (13%): `docs/investment-mandate.md §2`.
- Broker cost model (Inter, 0% commission + 15% BR tax): plan §3.2 +
  mandate §1.
