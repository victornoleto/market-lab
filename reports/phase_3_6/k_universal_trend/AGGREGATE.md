# Phase 3.6 Family K — Penfold Universal Trend Tactics (honest validation)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Pepperstone Razor CFD (plan §3.1) — per-ticker
spread (2.5bps SPY/QQQ/EFA/EEM/TLT/IEF, 5bps GLD/SLV, 10bps USO),
$0.35/100k commission, −0.03%/night long swap. No BR CG tax (non-BR
jurisdiction).
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 |
FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

Penfold's Donchian-50 breakout + ATR(14)×3.0 trailing stop on a 9-ETF
P24-proxy basket (SPY/QQQ/EFA/EEM/TLT/IEF/GLD/SLV/USO), sized at 0.5%
risk per position with a 100% gross-exposure cap, **fails 10 of the 13
binding gates** under the honest engine and Pepperstone Razor retail
cost model. Two PASS (gates 4 and 7), one PASS (gate 5 marginal at
0.211), 2 deferred (gates 9 PASS, 10 N/A — see §Cross-lib).

OOS Sharpe **0.387**, OOS CAGR **+1.88%** (well below the CDI 13%
floor), OOS MaxDD **−9.87%** (gate 4 PASS — small, but only because
gross stays at 0.38× average), median hold **23 trading days** (gate 7
PASS — true swing horizon). Bootstrap 99.9% CI on OOS Sharpe **[−0.85,
+1.70]** straddles zero. PBO **0.964** (catastrophic — every winner cell
is bottom-half on its complementary block). DSR p-value **0.76** over 12
grid cells — statistically indistinguishable from noise. Cost×2 OOS
Sharpe **−0.22** (gate 13 requires > 1.0).

**Penfold UPI (supplementary diagnostic):** OOS UPI = **0.331** (Penfold
guideline: > 2 "very good", < 0.5 "low" `[universal_trend_tactics,
p.259]`). FULL-period UPI = −0.003. The strategy fails Penfold's own UPI
threshold by an order of magnitude, consistent with the Sharpe/CAGR
gate failures.

Cross-lib concordance (gate 9) **PASS** (Δ = 0.000pp) — the engine is
wired correctly; the strategy simply has no cost-net edge after
diversification across 9 ETFs at 0.5%-risk-per-leg sizing.

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`.

## Penfold differentiators (mandatory per brief)

Family K's raison d'être is testing Penfold's *specific* operational
recipe, distinct from the Carver / Clenow / Faber / Chan / Ehlers / ML
families that preceded it. Three Penfold-specific differentiators are
present:

| Axis | Family K (Penfold) | Prior families (D/E/F/H/J etc.) |
|---|---|---|
| **Exit rule** | ATR(14) **trailing-distance stop** on close — long exits when `close_t < trailing_max − k × ATR_{t-1}` (golden tenets 2+3, "cut losses short / let profits run" `[universal_trend_tactics, p.68-69, p.338-343]`) | Signal-reversal exits — F: forecast sign change; H: HMM regime flip; D: cointegration unwind; J: classifier prediction. None applies an explicit ATR-distance trail. |
| **Universe selection** | **P24 ETF proxy** — 9 liquid Tiingo ETFs across 5 of Penfold's 8 sectors, chosen by **diversity + ADV only** (NO performance optimization on which markets to trade) `[universal_trend_tactics, p.168-169, p.261-262]` | F: 6 ETFs picked for vol-target tractability; A: top-N stocks ranked by momentum (performance-driven); H: 3 ETFs hand-picked for HMM separability. |
| **Diagnostic metric** | **Ulcer Performance Index (UPI)** = (CAGR − R_f) / UI alongside Sharpe — Penfold's preferred risk-adjusted metric for trend strategies because it measures depth × duration of drawdown vs. standard deviation `[universal_trend_tactics, p.245-246, p.251-255, p.259]` | Sharpe / Sortino only. UPI not previously computed in Phase 3.6. |

The three required differentiators are all present. Family K is **not** a
restatement of Family F (no Carver continuous EWMAC, no portfolio-level
vol target, no IDM), Family A (no top-N momentum ranking, basket-wide),
or Family C (no monthly SMA filter, event-driven entries).

## Top-line metrics (winner config: don50 / k3.0 / risk 0.5% / 1d)

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS  (2001-05-14 → 2017-12-31)  | 4185 | −0.154 |  −0.86% | −21.38% |
| OOS (2018-01-01 → 2023-12-31)  | 1509 |  0.387 |  +1.88% |  −9.87% |
| FWD (2024-01-01 → 2026-04-14)  |  572 |  0.211 |  +1.18% |  −9.70% |
| FULL (2001-05-14 → 2026-04-20) | 6270 |  0.024 |  +0.04% | −23.22% |
| **SPY OOS benchmark**          | 1509 |  0.658 | 12.00% |     —   |

Portfolio underperforms SPY buy-hold OOS by **−10.1pp CAGR** with one
quarter of the drawdown. IR vs SPY OOS is **−0.564** (gate 8 ≥ 0.3 →
FAIL). Despite passing MDD and FWD gates, the basket is essentially
SPY-minus over the OOS window.

## Penfold UPI diagnostic (supplementary, NOT a gate)

| Window | UI | UPI | Penfold guideline |
|---|---:|---:|---|
| OOS | 5.665 | **0.331** | < 0.5 = "low" `[p.259]` |
| FULL | 9.842 | **−0.003** | < 0.5 = "low" |

Penfold's own threshold (UPI > 2 "very good") would also reject this
configuration — consistent with the 12-gate failure. The basket exhibits
trend-trader pathology: shallow drawdowns spread over long durations
(UI 5.7%) accumulate without offsetting CAGR.

## Winner config (canonical)

```
donchian_lookback   = 50              [universal_trend_tactics, p.295-299 — between Turtle 20 and slow 80]
atr_period          = 14              [universal_trend_tactics, p.338-343, Wilder canonical]
atr_multiplier      = 3.0             [universal_trend_tactics, p.295-299, Turtle stop tradition]
risk_per_position   = 0.005           [universal_trend_tactics, p.291 — 2% scaled to 0.5% for 9-leg basket]
rebalance_days      = 1               [event-driven entries; trail always live per p.68-69]
max_gross_exposure  = 1.0             [Penfold money-management discipline, p.272 — avoids Family F swap-drag trap]
spread_one_way      = 2.5bps SPY/QQQ/EFA/EEM/TLT/IEF, 5bps GLD/SLV, 10bps USO  [plan §3.1]
commission_rt       = 3.5e-5           [plan §3.1 — $0.35/100k Razor]
swap_daily_long     = −0.0003          [plan §3.1 — −0.03%/night levered]
tax_rate            = 0.0              [plan §3.1 — Pepperstone non-BR]
universe            = SPY, QQQ, EFA, EEM, TLT, IEF, GLD, SLV, USO  (9-asset P24 proxy, 5 sectors)
```

## 13-gate checklist (plan §5; relaxations applied)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0      | > 0     | −0.8518 | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0     | > 0     | −0.5863 | FAIL |
| 2   | OOS Sharpe ≥ 1.5                    | ≥ 1.5   |  0.387 | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)          | ≥ 13%   | +1.88% | FAIL |
| 3t  | OOS CAGR ≥ 30% (target)             | ≥ 30%   | +1.88% | FAIL |
| 4   | OOS MaxDD ≥ −25%                    | ≥ −25%  | −9.87% | **PASS** |
| 5   | FWD Sharpe > 0                      | > 0     |  0.211 | **PASS** |
| 6   | WF 6/8 profitable AND mdd ≤ 30%     | both    | 5/8 mdd=15.81% | FAIL |
| 7   | Median hold ≥ 5 trading days        | ≥ 5d    |  23.0d | **PASS** |
| 8   | IR vs SPY OOS ≥ 0.3                 | ≥ 0.3   | −0.5641 | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp    | ≤ 3pp   |  0.000pp | **PASS** |
| 10  | Stage-2 data concordance ±1pp       | deferred | only one data source (Tiingo) | N/A |
| 11  | PBO < 0.5 (CSCV 10-block)           | < 0.5   |  0.9643 | FAIL |
| 12  | DSR p < 0.05                        | < 0.05  |  0.7609 | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0 | > 1.0   | −0.224 | FAIL |

**Summary: 4 PASS / 10 FAIL / 1 N/A.** Gates 4 (MDD) / 5 (FWD Sharpe) /
7 (median hold 23d — true swing horizon) / 9 (cross-lib) pass. Binding
FAILs span every edge metric (Sharpe, CAGR, bootstrap CI, DSR, IR-vs-
SPY), the WF stability gate, the PBO overfit gate, and the cost-
sensitivity gate.

## Grid sensitivity (12 cells for CPCV/PBO)

| Tag | Donchian N | ATR k | Sharpe (full) | n_trades |
|-----|----:|----:|--------------:|--------:|
| don20_k2.0_r0050bp_rb1   |  20 | 2.0 |  0.039 | 1050 |
| don20_k3.0_r0050bp_rb1   |  20 | 3.0 |  0.010 |  786 |
| don20_k4.0_r0050bp_rb1   |  20 | 4.0 |  0.018 |  605 |
| don50_k2.0_r0050bp_rb1   |  50 | 2.0 |  0.033 |  740 |
| **don50_k3.0_r0050bp_rb1 (winner)** | **50** | **3.0** | **0.024** | **550** |
| don50_k4.0_r0050bp_rb1   |  50 | 4.0 | −0.009 |  434 |
| don80_k2.0_r0050bp_rb1   |  80 | 2.0 |  0.037 |  619 |
| don80_k3.0_r0050bp_rb1   |  80 | 3.0 |  0.030 |  456 |
| don80_k4.0_r0050bp_rb1   |  80 | 4.0 | −0.015 |  360 |
| don120_k2.0_r0050bp_rb1  | 120 | 2.0 |  0.074 |  526 |
| don120_k3.0_r0050bp_rb1  | 120 | 3.0 |  0.055 |  389 |
| don120_k4.0_r0050bp_rb1  | 120 | 4.0 |  0.044 |  301 |

All 12 configs Sharpe-positive on full-period are still well below the
1.5 gate (best is don120_k2.0 at 0.074). PBO = **0.964** — astronomical:
of 252 CSCV combinations, the IS-best cell ranks bottom-half on the OOS
complement 96% of the time. The grid provides **no stable winner cell**;
ranking is essentially random across IS halves.

## Which gates killed it — diagnostic

The strategy generates a **gross-return Sharpe of ~0.10 pre-cost** (pre-
cost not separately reported here, but inferable from the breakeven
analysis below). Even with a pure ATR-trail discipline that prevents
catastrophic drawdowns (gate 4 PASS at −9.87%), three structural
mechanisms erase the edge:

1. **Trade selection failure on diversified ETF basket.** Penfold's
   3-tenets recipe is calibrated for a 24-instrument futures basket
   where the highest-conviction trends offset the many small losses
   from the kurtosis "fat tails" (`[universal_trend_tactics, p.87-99]`).
   On a 9-ETF basket dominated by US equity, bond, and commodity ETFs,
   the cross-asset correlation rises sharply during regime shifts (2018
   Q4, 2020 Mar, 2022 H1) — so simultaneous breakouts or simultaneous
   stops across multiple legs amplify the cost burden without capturing
   compensating large winners. The 9-ETF basket has ~50% effective
   independence vs Penfold's P24 (~12).

2. **Donchian breakout signal degradation in low-volatility regimes.**
   2018-2023 had two sustained low-vol regimes (2018 Q1-Q3, 2019 H2-2020
   Q1) where Donchian-N breakouts are dominated by mean-reverting
   noise. The strategy enters 550 trades over 25 years (median hold 23d)
   — far too many for a "follow the trend" rule that Penfold's MWDT
   (`[p.358-361]`) targets at ~15-30 trades/decade. Each excess entry
   pays the 2.5-10bp spread plus 23×0.03% = 0.7% swap on the held
   leg.

3. **Cumulative cost drag (swap dominant).** `cum_swap = 71.6%` over 25
   years, `cum_spread = 5.9%`, `cum_commission = 0.65%`. Total cost drag
   ~78% of equity over 25y at the 0.38× average gross. Pre-cost CAGR
   would be ~3.2%/year vs. cost ~3.1%/year — the basket is essentially
   trading at break-even on the gross signal. Any small parameter shift
   (k=4.0 example: Sharpe drops to −0.009) crosses break-even into
   net-negative territory. This is the **same swap-drag mechanism that
   killed Family F** at higher leverage; here the lower 0.38× gross
   protects MDD at the price of unable to recover costs.

4. **Bootstrap CI [−0.85, +1.70] on OOS Sharpe** confirms the signal
   is statistically indistinguishable from zero. PBO 0.96 confirms
   no parameter cell is reliably better.

## Mechanism — why this is FAIL even at lower gross or longer Donchian

Three rescue paths are conceptually possible but none clears the gates:

- **Lower per-leg risk (0.25%):** would halve cost drag but also halve
  per-trade payoff — still net-zero edge, lower MDD, lower CAGR. No
  CDI clearance.
- **Longer Donchian (200d+):** would reduce trade count, but Penfold's
  own equity-curve-stability review (`[p.140, p.145-157]`) shows a
  multi-variable strategy on a basket gets fragile; 200d Donchian on
  a 9-ETF basket would likely have ≤30 trades over 25y, no
  statistical significance, and tail-risk concentration in the 1-2
  trades that matter.
- **Restoring full P24 (24-instrument futures):** would address the
  diversification deficit but requires futures broker (not Pepperstone
  CFD ETFs) and falls outside the Tiingo-bulk universe and brief.
  Pepperstone CFD universe is ETF/FX/CFD-equity dominated; commodities
  spread is wide and futures-roll mechanics differ from ETF total
  return.

None of these rescues is a clean "Family K variant" — they become new
candidate families. The verdict here is that **Penfold's Donchian +
ATR-trail recipe on a 9-ETF Tiingo P24-proxy basket does not clear
Pepperstone retail costs at any (donchian, atr_k) ∈ {20,50,80,120} ×
{2.0,3.0,4.0}**.

## Data caveats

1. **P24 sector coverage gap.** Penfold's canonical P24 spans 8 sectors
   (indices, rates, currencies, metals, energy, grains, livestock,
   softs `[universal_trend_tactics, p.168-169]`). Tiingo bulk only
   provides the first 4: equities (SPY/QQQ/EFA/EEM), bonds (TLT/IEF),
   metals (GLD/SLV), energy (USO). DBA (agriculture) stops trading
   2023-12-29 — unusable for the FWD window. UUP/FXE/DBE absent from
   the Tiingo bulk. Consequently we test 9 instruments across 5
   sectors, not 24 across 8 — this is a **structural diversification
   handicap** vs Penfold's design but is documented honestly. See
   §Penfold differentiators.

2. **Universe inception truncation.** The 9-asset panel is only
   simultaneously populated from 2006-04-28 (SLV inception) onward.
   Earlier bars use dynamic-inclusion (asset enters when it has 14d ATR
   warm-up + 50d Donchian warm-up). SPY 2001-05-14; QQQ 2001-05-14; TLT
   2002-07-26; EFA/EEM 2003-08-20; GLD 2004-11-18; IEF 2006-01-03; USO
   2006-04-10; SLV 2006-04-28. IS window has reduced breadth pre-2006.
   OOS and FWD windows have the full 9-asset panel.

3. **Pepperstone CFD underliers assumed.** Tiingo provides ETF prices;
   Pepperstone CFDs track the underlying cash/futures. Minor basis
   noise (~1-3 bp/day on commodity CFDs vs ETFs) is NOT modeled — this
   is conservative for gate evaluation since real-CFD returns should be
   slightly better than ETF returns.

4. **No futures roll yield.** Penfold tests on actual futures contracts
   where roll yield (positive or negative depending on contango/
   backwardation) materially affects long-horizon trend captures. Our
   ETF basket abstracts this: USO replicates rolling crude futures with
   its own roll drag (well-documented negative carry); GLD/SLV are
   physical-backed (no roll); TLT/IEF distribute coupons via adj_close
   reinvestment. The mismatch is in Penfold's favor (his real-futures
   tests benefit from roll yield in trending commodities); we
   under-model edge.

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `daily_returns.parquet` — winner-config honest daily returns (local,
  gitignored by pattern).
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 12-config sensitivity grid Sharpe.
- `cross_lib_check.md` + `cross_lib_check.json` — gate 9 PASS (Δ=0.000pp).
- Logs: `logs/phase3_6_k_universal_trend.log`, `logs/phase3_6_k_cross_lib.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_k_universal_trend.py`.
- Runner: `scripts/run_phase3_6_k_universal_trend.py`.
- Cross-lib runner: `scripts/run_phase3_6_k_cross_lib.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion. No pending draft.

## Citations

- Penfold 3 golden tenets (follow trend / cut losses / let profits run):
  `[universal_trend_tactics, p.68-69]` (Ricardo 1800; print 1838).
- P24 portfolio = diversity + ADV across 8 sectors:
  `[universal_trend_tactics, p.168-169, p.261-262]`.
- Donchian / Turtle channel breakout entry:
  `[universal_trend_tactics, p.295-299, p.210-217]`.
- Two-stop trade plan (initial + ATR-distance trail):
  `[universal_trend_tactics, p.338-343, p.361]`.
- Fixed-fraction position sizing:
  `[universal_trend_tactics, p.271-272, p.291]`.
- Ulcer Index / UPI (supplementary diagnostic):
  `[universal_trend_tactics, p.245-246, p.251-255, p.259]`.
- Equity-curve stability / minimal-variable design:
  `[universal_trend_tactics, p.46-47, p.140, p.145-157, p.266-267,
  p.274-279]`.
- Fat-tail empirical validation of trend trading:
  `[universal_trend_tactics, p.87-99]`.
- Lookahead audit + alignment: `[advances_fin_ml, p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- PBO CSCV 10-block: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward 6/8: `[advances_fin_ml, ch.11]`.
- Pepperstone Razor cost model: plan
  `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §3.1.
- Family F swap-drag failure mechanism (cross-reference): `reports/
  phase_3_6/f_vol_target_managed_futures/AGGREGATE.md`.
