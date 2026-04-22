# Phase 3.6 Family E — Ehlers adaptive-cycle filters (honest validation)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Pepperstone Razor via cTrader (plan §3.1) —
equity-ETF CFD 0.05% one-way spread, 0.03%/night swap on levered
notional, zero commission (Razor micro-lot), no BR tax (non-BR source).
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 |
FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

The Ehlers adaptive-cycle swing strategy **fails 10 of the 13 gates**
under the honest engine on the 5-ETF liquid-basket universe. The core
problem is that the strategy's DSP machinery (roofing filter →
autocorrelation periodogram → adaptive RSI) successfully identifies
cycle mode but the **entry/exit oscillator produces no durable edge**
on a universe that spent 2018-2023 in a near-continuous bull-market
trend. OOS Sharpe is **−0.61** (gate 2 ≥ 1.5 → FAIL) with OOS CAGR
**−9.95%** (gate 3 CDI floor 13% → FAIL), and OOS MaxDD of **−53.4%**
spectacularly breaches gate 4 (≥ −25%). The bootstrap 99.9% OOS CI on
Sharpe is **[−1.86, +0.81]** (straddles zero → gate 1 FAIL), and gate
12 DSR p-value is **0.998** — the observed OOS edge is statistically
indistinguishable from random.

The two positives are **gate 5 FWD Sharpe 0.60 PASS** (the post-2024
regime shows intermittent mean-reversion cycles the strategy can trade)
and **gate 7 median hold = 6.0 bars PASS** (the hold-cap discipline
works as designed).

Cross-lib concordance (gate 9) passes at **Δ=0.000pp** — our two
independent implementations produce identical OOS CAGR. The *signal is
replicable*; it simply has no edge.

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`.

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS (2001-05-14 → 2017-12-31)   | 4185 | +0.066 |  −0.27% | −38.73% |
| OOS (2018-01-01 → 2023-12-31)  | 1509 | −0.613 |  −9.95% | −53.44% |
| FWD (2024-01-01 → 2026-04-14)  |  572 | +0.600 |  +8.13% | −12.38% |
| FULL (2001-05-14 → 2026-04-20) | 6270 | −0.044 |  −1.97% | −61.24% |
| **SPY OOS benchmark**          | 1509 | +0.658 | +12.00% | −33.70% |

Portfolio underperforms SPY buy-hold in OOS by **−22 pp CAGR** and
carries ~1.6× the drawdown; IR vs SPY OOS is **−1.39** (gate 8 ≥ 0.3 →
FAIL).

## Winner config (baseline)

```
hp_period            = 48           [cycle_analytics, p.77 — text example HP=48]
ss_period            = 10           [cycle_analytics, p.36, ch.3 — universal recommendation]
rsi_lower            = 0.30         [cycle_analytics, p.220-221, ch.17 RULE]
rsi_upper            = 0.70         [cycle_analytics, p.220-221, ch.17 RULE]
hold_cap_bars        = 20           [cycle_analytics, p.224, ch.17 — half-DC exit]
spread_one_way_pct   = 0.0005       [plan §3.1 — Pepperstone Razor ETF CFD]
swap_per_night_pct   = 0.0003       [plan §3.1 — mid-range −0.01 to −0.05%/night]
tax_rate             = 0.0          [plan §3.1 — Pepperstone non-BR]

Universe            = {SPY, QQQ, GLD, TLT, EFA}  (5 liquid ETFs)
```

## 13-gate checklist (plan §5; relaxations applied)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0       | > 0    | −1.8598 | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0      | > 0    | −0.5550 | FAIL |
| 2   | OOS Sharpe ≥ 1.5                     | ≥ 1.5  | −0.613 | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)           | ≥ 13%  | −9.95% | FAIL |
| 3t  | OOS CAGR ≥ 30% (target)              | ≥ 30%  | −9.95% | FAIL |
| 4   | OOS MaxDD ≥ −25%                     | ≥ −25% | −53.44% | FAIL |
| 5   | FWD Sharpe > 0                       | > 0    | +0.600 | PASS |
| 6   | WF 6/8 profitable AND mdd ≤ 30%      | both   | 3/8 mdd=45.22% | FAIL |
| 7   | Median hold ≥ 5 trading days         | ≥ 5d   |  6.0d  | PASS |
| 8   | IR vs SPY OOS ≥ 0.3                  | ≥ 0.3  | −1.394 | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp     | ≤ 3pp  | Δ=0.000pp | PASS |
| 10  | Stage-2 data concordance ±1pp        | deferred | only one data source (Tiingo) | N/A |
| 11  | PBO < 0.5 (CSCV 10-block)            | < 0.5  | 0.5159 | FAIL |
| 12  | DSR p < 0.05                         | < 0.05 | 0.9976 | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0  | > 1.0  | −1.043 | FAIL |

**Summary: 3 PASS / 10 FAIL / 1 deferred.** Gate 9 now PASSES at
**Δ=0.000pp** between the canonical simulator and a pure-pandas hand-
rolled re-implementation sharing the same DSP primitives. Gate 10 is
deferred (no independent data source for multi-asset Tiingo panel).
Binding FAILs span every edge-side metric (Sharpe, CAGR, DSR, IR,
bootstrap CI), the risk-side (MDD, WF), the overfit-side (PBO just above
0.5), and the cost-robustness (cost×2).

## Which gates killed it

### 1. OOS is worse than IS — strategy breaks in the 2018-2023 regime

IS Sharpe **+0.07** → OOS Sharpe **−0.61** is a severe degradation.
The 2018-2023 OOS contains:

- 2018 Q4 correction (short duration, strategy shorted the low).
- 2019 smooth bull trend (strategy whipsawed in/out of positions).
- 2020 COVID crash (strategy was out when the V-bottom launched).
- 2021 meme/crypto/growth bubble (strategy repeatedly bought the
  short-term dip, then exited at RSI > 0.70 before the real move).
- 2022 bear + 2023 AI rally (same whipsaw pattern).

Ehlers himself warns `[cycle_analytics, p.xi-xii]` that **cycles
cannot be the basis of trades all the time — when cyclic swings are
swamped by trends, using cycle tools is "folly."** The OOS window is
exactly the regime he warns about: strong directional trend, low
spectral power in the 10-48 bar band. The SNR is below the 6 dB floor
described in `[rocket_science, p.93]` most of the time, but our
strategy has no SNR-gating — it trades every cycle signal regardless of
spectral quality.

### 2. Cost drag is catastrophic — cum_cost 163% of starting equity

The strategy entered **697 trades** across 5 assets over 25 years
(~28 trades/year total, median hold 6 bars). With Pepperstone 0.05%
spread per weight change and 0.03%/night swap on aggregate long
notional, cumulative cost reaches **162.6%** of starting equity. Net
return is negative before OOS even begins. `[cycle_analytics, p.xi]`
and `[rocket_science, p.ix]` both emphasize lag minimization, but
Ehlers does not address round-trip transaction costs — his worked
examples are futures (lower spread) or pedagogical daily-bar equity
plots without spread/swap modeled.

**Cost×2 sensitivity** drops OOS Sharpe from −0.61 to **−1.04**, a
73% worsening. The strategy is not just unprofitable — it is
profoundly cost-fragile. Gate 13 FAILS at a floor of Sharpe > 1.0 with
a realized value of −1.04.

### 3. Anticipate-rule entries trigger prematurely in trends

`[cycle_analytics, p.220-221, ch.17]` advocates entering long when the
oscillator crosses **below** the lower threshold (anticipate the turn,
do not confirm). In cycle mode this recovers ~4 bars of lag. But in
**trend mode** the adaptive RSI rarely reaches the lower threshold
during pullbacks — when it does, the pullback is usually shallow, and
the strategy enters late in the uptrend. Then the upper threshold is
reached as the trend continues, the strategy exits the long, and the
price keeps rising without it. The strategy is structurally
anti-trend while trend is where most of the OOS return lived.

### 4. WF 3/8 profitable with 45% max window DD

Walk-forward on 8 equal-width windows: only 3/8 windows positive, and
the worst window had **−45.2% MDD**. Both exceed the gate 6 relaxed
thresholds (≥6/8 profitable, MDD ≤ 30%). The strategy's distribution
of outcomes is wide and asymmetric — bad windows are catastrophically
bad.

### 5. PBO 0.516 just above the 0.5 line

With 6 grid configs the PBO (probability of backtest overfitting)
comes in at **0.516**. Plan gate 11 threshold is strict < 0.5. The
grid is shallow (only 6 cells across 3 dimensions) so PBO estimation
has high variance — but the fact that PBO is not comfortably below
0.5 indicates the winner config's modest full-period Sharpe (−0.044)
does not dominate its siblings at out-of-sample ranks. Said
differently: *no config in the grid has edge; the winner is not a
meaningful winner*.

### 6. DSR p-value 0.998 — edge indistinguishable from noise

DSR (Deflated Sharpe Ratio, `[advances_fin_ml, p.273-275]`) returns
**p = 0.998** on the OOS Sharpe of −0.04 with 6 trials. Under any
multiple-testing correction, observed OOS Sharpe is not significantly
better than random — in fact, it is worse than null. Gate 12 FAILS
by a wide margin.

### 7. Positive: FWD (2024-2026) Sharpe 0.60 — cycle regime returns

The FWD window is the only bright spot: Sharpe +0.60, CAGR +8.1%,
MDD −12.4%. This suggests the post-2024 regime (higher volatility,
more chop, less one-way trend) is closer to what Ehlers' tools are
designed for. **But FWD alone cannot salvage the strategy** — it is
a stress check (gate 5 is binary > 0), not a primary gate.

## Data-source caveats

1. **Fixed 5-ETF universe — no survivorship issue** by construction.
   The basket is SPY, QQQ, GLD, TLT, EFA — all of which exist today
   and existed for the entire span tested.

2. **Warm-up effects on GLD/TLT/EFA.** GLD begins 2004-11, TLT begins
   2002-07, EFA begins 2003-08. For the first ~3 years of the IS
   window, those assets contribute zero to the portfolio (no signal
   yet). SPY and QQQ carry the IS start; gradually the basket
   expands. This is not a bug — it is a realistic reflection of
   instrument availability.

3. **Autocorrelation periodogram warm-up is ~100 bars.** The first
   ~100 bars of each asset's history yield NaN dominant-cycle
   estimates (Pearson correlation at lag 48 requires 48 bars of
   data + 3-bar averaging; plus ~48 bars of roofing-filter warm-up
   prior). The effective start of signal per asset is:

   - SPY: ~2001-10 (after 100 bars from 2001-05-14)
   - QQQ: ~2001-10
   - TLT: ~2002-12
   - EFA: ~2004-01
   - GLD: ~2005-04

## Grid sensitivity (6 configs for CPCV/PBO)

| Tag                                  | hp | ss | lo   | hi   | hold | Sharpe (full) |
|--------------------------------------|---:|---:|-----:|-----:|-----:|--------------:|
| hp48_ss10_lo30_hi70_hold20 (winner)  | 48 | 10 | 0.30 | 0.70 |   20 | −0.044 |
| hp48_ss10_lo25_hi75_hold20           | 48 | 10 | 0.25 | 0.75 |   20 | −0.168 |
| hp48_ss10_lo35_hi65_hold20           | 48 | 10 | 0.35 | 0.65 |   20 | +0.032 |
| hp60_ss10_lo30_hi70_hold20           | 60 | 10 | 0.30 | 0.70 |   20 | −0.089 |
| hp48_ss10_lo30_hi70_hold10           | 48 | 10 | 0.30 | 0.70 |   10 | +0.006 |
| hp48_ss10_lo30_hi70_hold40           | 48 | 10 | 0.30 | 0.70 |   40 | −0.014 |

Full-period Sharpe ranges **−0.17 to +0.03** — the entire grid
oscillates around zero. No config earns an edge; the "winner" is a
statistical tie. PBO 0.516 reflects this: the winner's OOS rank is
essentially random relative to its siblings.

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `daily_returns.parquet` — winner-config honest daily returns.
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 6-config sensitivity grid Sharpe.
- `cross_lib_check.md` + `.json` — gate 9 concordance (PASS, Δ=0.000pp).
- Logs: `logs/phase3_6_e_ehlers.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_e_ehlers_cycles.py`.
- Runner: `scripts/run_phase3_6_e_ehlers_cycles.py`.
- Cross-lib runner: `scripts/run_phase3_6_e_cross_lib.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion. No pending draft.

## Citations

- Ehlers DSP framework core (roofing filter + autocorrelation
  periodogram + adaptive RSI + anticipate-entry rule):
  `[cycle_analytics, p.77-82, p.102-106, p.137, p.220-221]`.
- Explicit deprecation of Hilbert Homodyne for dominant cycle in
  favour of autocorrelation periodogram: `[cycle_analytics, p.186]`.
- Cycle mode vs trend mode dichotomy + "cycles as folly in trend":
  `[cycle_analytics, p.xi-xii]`; `[rocket_science, p.113-114]`.
- Half-dominant-cycle hold-cap exit discipline: `[cycle_analytics,
  p.224, ch.17]`.
- SNR 6 dB minimum for cycle-mode trading: `[rocket_science, p.93]`.
- Simplicity requirement (avoid curve-fitting): `[cycle_analytics,
  p.217, ch.17]`.
- Lookahead audit + replication protocol: `[advances_fin_ml,
  p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- CSCV PBO: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward: `[advances_fin_ml, ch.11]`.
- Pepperstone CFD cost model: plan
  `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §3.1 +
  memory `project_broker_decision.md`.
