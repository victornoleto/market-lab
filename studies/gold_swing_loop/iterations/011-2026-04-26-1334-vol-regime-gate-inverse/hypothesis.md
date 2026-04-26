# Iteration 011 — Inverse vol-regime gate: long XAUUSD when σ_60d < σ_252d

## Hypothesis

Long XAUUSD with full size whenever the **60-day realized volatility of
log returns falls BELOW the 252-day realized volatility**, flat
otherwise. This is the structural inverse of iter 010's gate (which
fired during vol-EXPANSION); iter 011 fires during **vol-COMPRESSION**
— low-vol bull regimes.

The hypothesis is grounded in the empirical pattern that gold's
strongest sustained drift periods (2009-2011 bull rally, 2018-2019
revival, 2023-2024 ATH cycle) coincide with REGIME-LOW realized vol —
gold "grinds higher" rather than spiking. Iter 010 captured the vol-
expansion half of the regime cycle (43% of bars; +Sh 3/3 but trailing
benchmark by 0.48-1.01 Sharpe). The inverse should capture roughly the
complementary 57% — including the long, drift-rich periods iter 010 sat
flat through.

The Sinclair vol-cone framework `[volatility_trading, p.58-59]` is
agnostic on which side of the cone is the signal: it's a tool for
placing CURRENT vol against the historical distribution. Whether
"current high" or "current low" is bullish for gold is an empirical
question, and Kaufman classifies metals as **low-noise → directional**
markets `[trading_systems_methods, p.13]`, where low-noise = sustained
trend = LOW realized vol. The hypothesis follows directly from this
classification.

The strategy is **single-asset, LONG-ONLY** — no shorts, no cross-asset
signal, no calendar event, no `|z|>kσ` entry trigger. Both broker
tracks are viable (same as iter 010): Track A natural fit, Track B
likely DARF-impacted but clean LONG-ONLY signal.

## Primary citation

`[volatility_trading, p.58-59]` — Sinclair's volatility cone framework.
Iter 010 used the same citation for σ_60>σ_252; iter 011 uses the
opposite side of the cone (σ_60<σ_252). The cone framework is
DIRECTIONALLY agnostic; iter 010 + iter 011 together exhaust the
binary partition of the cone-comparison space.

## Additional citations

- `[trading_systems_methods, p.13-14]` — Kaufman's noise classification
  (PRIMARY for inverse direction). "Low-noise markets (short-rates,
  long-maturity bonds, USD crossrates, energy, **metals**) → trend-
  following." Low-noise IS low-vol-relative-to-drift — the technical
  signature is precisely a sustained period where σ_short < σ_long.
  Metals (gold) classified as low-noise → trending periods are LOW
  vol, supporting the inverse signal direction.
- `[trading_systems_methods, p.131]` — Kaufman's **Efficiency Ratio** =
  `stdev(C,n) / stdev(C,m)`. Same family (vol-ratio across nested
  windows); the σ_60/σ_252 ratio captures the same structural
  information. Ratio < 1 = "efficient" / trending; ratio > 1 = "noisy"
  / mean-reverting. Iter 011 = ratio < 1.
- `[volatility_trading, p.249-251]` — vol clustering / persistence. Vol
  regimes last weeks-to-months (slow-moving), so 60d/252d framing
  identifies regime onset / decay reliably. Same support as iter 010.
- `[volatility_trading, p.217]` — robustness of regime-filter form vs
  threshold value: "Results are fairly robust with respect to the
  actual VIX level chosen." The form `σ_short < σ_long` is the load-
  bearing design choice, not the lookback choice.
- `[short_term_trading_strategies, p.106]` (Connors) — "Stocks above
  their 200-day MA tend to have lower volatility." Gold's bull-rally
  periods exhibit the same low-vol property (analogous regime).

## Edge source

Gold's buy-hold drift (~11.3% CAGR on 21y) is unevenly distributed
across vol regimes:

- **Vol-expansion regimes** (~43% of bars, captured by iter 010):
  drift is event-driven and clusters during stress events (2008 GFC,
  2011 Eurozone, Mar-2020 COVID, 2022 stagflation). Iter 010 produced
  +Sh 3/3 standalone but Δ −0.48 to −1.01 vs benchmark.
- **Vol-compression regimes** (~57% of bars, hypothesized to be
  captured by iter 011): drift accrues steadily during bull-trend
  episodes (2009-2011 multi-year bull, 2017-2019 revival, 2023-2024
  ATH cycle). These are the periods where iter 010 was FLAT, missing
  the cumulative drift.

The win condition: **inverse gate produces +Sharpe edge over benchmark
on ≥ 2 of 3 datasets**, driven by capturing the sustained-trend bull
periods and avoiding the high-vol volatility-tax periods. If
hypothesis holds, iter 010 + iter 011 together would tile gold's
regime cycle; iter 011 standalone could be the first +Sharpe-3-of-3
strategy in this loop, OR (more likely) another NEAR_FAIL where the
two halves of the cone partition both fall short individually but
together set up an IC-7 base structure (with iter 003's RSI(2)+SMA(200)
as the third stream).

## Datasets

- **gld_long** (GLD daily 21.4y) — 21y allows multiple vol-compression
  cycles. Contains the 2009-2011 bull, 2017-2019 revival, 2023+ ATH
  cycle as natural target episodes. Primary cross-validation.
- **xauusd_real** (XAUUSD daily 6.3y) — 2020+ window includes the
  2023-2024 ATH cycle (peak vol-compression bull-trend regime). Tests
  whether the inverse gate generalizes from 21y to 6y. The
  GS-4/5/6/7/10 cross-dataset failure mode is the central risk.
- **xauusd_intraday** (XAUUSD 1h 6.3y) — same calendar window as
  xauusd_real. Sanity-check execution precision: regime gate is daily
  by construction, so intraday Sharpe should ≈ xauusd_real.

## Timeframes used

`[1d, 1h]`. Both cached in Tiingo. No 30m / 15m / 1m needed → no
cTrader Open API fetch.

## Broker tracks targeted

`broker_track: "both"`.

- **Track A (Pepperstone CFD)**: 8 bps RT spread + −1 bps/night swap
  long. Overnight hold intrinsic to slow regime gate; weekend mult 3×
  swap on Friday→Monday.
- **Track B (Inter ETF GLD)**: 100 bps FX RT + DARF 15% on positive
  monthly net. T+1 settlement no issue (regime episodes span weeks).

Per-track metrics reported separately. Track B expected to score 5-15
points lower (DARF + FX cliff).

## Hold-time profile (HARD GATE)

- **Expected mean hold**: ~30-90 trading days per regime episode
  (vol regimes are slow-moving by Sinclair's stationarity arguments).
  Symmetrical to iter 010 (which had 41-49d holds).
- **swing-extended tag** — mean hold > 5 trading days is essentially
  guaranteed. Per WINNER_AND_RANKING.md, this caps tier at STRONG and
  disqualifies WINNER. Justified explicitly: the regime-gate mechanism
  IS slow by design; trying to compress it to mean-hold ≤ 5 days
  would defeat the purpose. A STRONG-tier inverse-vol gold strategy
  with materially favorable MDD/CAGR vs iter 010 is a candidate base
  for future IC-7 composition.

## Pre-validation screen (cost-aware, gold-loop standard)

Same shape as iter 010 (no `|z|>kσ` trigger → GS-9 state-machine-
aware fwd-N concern does NOT apply). Standard cost-aware pre-val:

| metric | symbol | pass condition |
|---|---:|---|
| pct_active (fraction of bars with σ_60 < σ_252)   | `p_active`  | 0.15 ≤ `p_active` ≤ 0.70 |
| mean log return when flag=True (annualized %)     | `μ_active`  | `μ_active > 0` |
| n_flips per year (regime transitions / year)      | `n_flips`   | `n_flips ≤ 8/yr` |
| annualized cost drag per year (bps)               | `cost_yr_bps` | `cost_yr_bps < 0.5 × μ_active_bps × p_active` |

`cost_yr_bps = (n_flips/2) × spread_RT_bps + p_active × 365 ×
|swap_long_bps_per_night|`

**Predicted p_active**: ~57% (1 − 0.43 from iter 010). Within
[0.15, 0.70] → passes. **n_flips/yr**: ~5/yr (same boundaries as iter
010, just different "on" vs "off" labels). Passes. **μ_active**: this
is the empirical question — does gold's drift in σ_60 < σ_252 regime
exceed its drift in σ_60 > σ_252 regime? Iter 010 measured μ_active
(σ_60>σ_252) at +849/+243/+270 bps/yr active; if gold's drift is
roughly evenly distributed, μ_active for inverse will be (full_drift
× n_total − iter_010_active_drift × n_active_010) / n_active_011 —
small but positive on long history. **cost_yr_bps**: ~178 bps/yr
(symmetric to iter 010). Pass conditional on μ.

Pass threshold: at least 2/3 datasets must satisfy ALL 4 conditions. If
0/3 → auto-abort.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**: spread 8 bps RT + −1 bps/night
swap long + 3× weekend mult. Symmetric to iter 010.

**Track B (Inter ETF GLD)**: 100 bps FX RT + DARF 15% × max(0, monthly
pre-tax net). Symmetric to iter 010.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if any of these hold at end of Stage 4:

1. **Insufficient exposure**: `p_active < 0.15` on ≥ 2 of 3 datasets
   at pre-val (gate doesn't fire enough — unlikely given iter 010's
   complement is ~57%).
2. **No active drift**: `μ_active ≤ 0` on ≥ 2 datasets (the regime
   captures the wrong half of the drift distribution — this is the
   primary structural test of the hypothesis).
3. **Sharpe collapse**: `Sharpe_strategy < Sharpe_benchmark − 0.50`
   on ≥ 2 datasets after Pepperstone CFD costs (Track A). Tighter
   than iter 010's −0.30 because iter 010 already failed at that
   threshold; iter 011 must clear a higher bar to be useful.
4. **MDD claim broken**: `MDD_strategy > MDD_benchmark + 5pp` on ≥ 2
   datasets. Vol-compression-only entries should AVOID the high-vol
   crash episodes that drove gold's historical 45% MDD; if MDD does
   NOT improve, the regime mechanism doesn't work.
5. **Inverted vs iter 010**: if Sharpe(011) < Sharpe(010) on ≥ 2
   datasets at the same hold horizon, the inverse hypothesis is
   directly contradicted (drift IS biased toward vol-expansion).

## Expected budget

- Configs to test: **1** (single pre-committed cfg `vol_regime_inverse_60_252`).
  No grid sweep — IC-8. Single-cfg keeps DSR cumulative_n_trials at 11.
- Wall-time: ~30-45 min (single signal, simple state machine, no ML).
  Reuses iter 010 infrastructure with 1-character sign flip.
- Files to create:
  - `iterations/011-*/hypothesis.md` (this file)
  - `iterations/011-*/run_backtest.py` — pre-val + signal + state machine + 7-gate
  - `iterations/011-*/test_vol_regime_signal.py` — TDD spec for inverse signal
  - `iterations/011-*/pre_val.json` + `results.json` + `final_report.md` + `verdict.json`

## Implementation plan

1. **Signal function** `compute_vol_regime_inverse_flag(prices,
   window_short=60, window_long=252)`:
   ```python
   sigma_short = realized_vol(prices, window_short, ann_factor)
   sigma_long  = realized_vol(prices, window_long,  ann_factor)
   flag = (sigma_short < sigma_long).astype(int)  # NOTE: < not >
   flag = flag.where(sigma_long.notna(), 0).astype(int)
   ```
   For xauusd_intraday: resample 1h → 1d for computation, propagate
   daily flag with shift(1) (no look-ahead).

2. **TDD test** in `test_vol_regime_inverse_signal.py`:
   - Hand-rolled fixture: synthetic price series with known σ_60/σ_252
     ratio, assert flag fires when σ_60 < σ_252.
   - Edge case: insufficient data (first 252 bars) → flag=False.
   - Cross-lib parity: hand-rolled numpy vs pandas-rolling.
   - Complementarity: iter 011 flag XOR iter 010 flag = 1 in non-warmup
     bars (both can't be active or inactive simultaneously) — this is
     the structural binding between the two iters.

3. **Pre-validation** runs first; auto-abort if 0/3 pass.

4. **State machine**: position[t] = flag[t]; held into bar t+1.
   No exit logic beyond regime change.

5. **Cost models**: apply both `apply_pepperstone_costs` (Track A) and
   `apply_inter_costs_with_darf` (Track B) to the gross PnL series.

6. **7-gate battery** per dataset, separately for Track A.

7. **Cross-lib**: hand-rolled numpy backtest assertion ±3 pp CAGR vs
   pandas implementation (G7).

## Anti-pattern checks (sanity)

- ❌ NOT IC-1 (vol-target wrapper absorption): the gate is a binary
  {0, 1} position, not vol-scaled. The σ comparison is on the SIGNAL
  side before sizing.
- ❌ NOT IC-2 (input/output regime double-count): no second regime
  gate applied to position size.
- ❌ NOT a re-test of GS-10: iter 010 closed σ_60 > σ_252 STANDALONE.
  Iter 011's σ_60 < σ_252 is the **structural complement** — different
  fired-bars, different active drift distribution. DEAD_ENDS.md GS-10
  explicitly documents this case as "Does NOT close" (item 1: "Inverse
  signal — different hypothesis, captures the trending-bull stretches
  iter 010 missed").
- ✅ Different family from iter 003's MR (this is regime, not entry-MR);
  potentially IC-7 secondary if a primary +Sharpe-3-of-3 stream
  emerges (ρ between iter 011 ↔ iter 003 will be measured this iter).
- ✅ Different from GS-7/8/9: no `|z|>kσ` trigger.
