# Iteration 010 — Realized-vol regime gate: long XAUUSD when σ_60d > σ_252d

## Hypothesis

Long XAUUSD with full size whenever the **60-day realized volatility of
log returns exceeds the 252-day realized volatility**, flat otherwise.
The signal is a slow, binary regime indicator that captures "vol-expansion
phases" — periods where shorter-window vol exceeds longer-window vol.
Sinclair's volatility cone framework `[volatility_trading, p.58-59]`
places current vol against a longer historical percentile; here, the
60d-vs-252d ratio is a 2-window simplification of the same idea: the
short window IS the "current" vol, the long window IS the historical
baseline.

The strategy is **single-asset, LONG-ONLY** — no shorts, no
cross-asset signal, no calendar event, no `|z|>kσ` entry trigger. Both
broker tracks are viable for the first time since iter 003 because:

- Track A (Pepperstone CFD, 8 bps RT, intraday-close optional) — trivial,
  long position with overnight swap drag
- Track B (Inter ETF GLD/IAU, 100 bps FX RT + 15% DARF, T+1, long-only)
  — natural fit because the gate IS long-only by construction

## Primary citation

`[volatility_trading, p.58-59]` — "Volatility cone — a plot of
realized volatility percentiles (min, 25th pct, median, 75th pct, max)
across multiple time horizons (e.g., 20, 40, 60, 120, 240 days), used
to place current implied volatility in historical context." The σ_60d
> σ_252d ratio is the binary degenerate of the vol cone (current vs
historical median); the framework is canonical Sinclair.

## Additional citations

- `[volatility_trading, p.217]` — VIX = 35 used as regime filter:
  "Results are fairly robust with respect to the actual VIX level chosen
  — the threshold serves as a regime filter; not highly sensitive to
  exact value." Same structural argument applies to vol-cone regime
  thresholds: the FORM of the filter (binary on cross-window ratio) is
  the load-bearing design choice; the lookback choice is secondary.
- `[trading_systems_methods, p.131]` — Kaufman's **Efficiency Ratio** =
  `stdev(C,n) / stdev(C,m)`, default `n=9, m=30`. Same family
  (vol-ratio across nested windows); validates ratio-of-vols as a
  signal grammar. Our (60, 252) is the longer-horizon version of
  Kaufman's (9, 30).
- `[trading_systems_methods, p.13]` — "Low-noise markets (short-rates,
  long-maturity bonds, USD crossrates, energy, **metals**) → trend-
  following." Metals (gold) classified as low-noise → directional
  signals (including vol-gated long-bias) are structurally appropriate.
- Andersen-Bollerslev (1998) *International Economic Review* 39 — realized
  volatility as a stationary, mean-reverting process with persistence;
  validates the 60d/252d framing as estimating two points on the same
  underlying RV process.
- Sinclair `[volatility_trading, p.249-251]` — vol clustering /
  persistence: vol regimes last weeks-to-months, not days, so a 60d
  rolling window is short enough to reflect regime onset and long enough
  to filter noise.

## Edge source

Gold buy-hold absorbs both **vol-expansion drift** (safe-haven flows,
inflation hedge demand, geopolitical / monetary shocks) AND **low-vol
drawdown periods** (e.g., 2013-2018 bear-market stagnation, −45% MDD).
The hypothesis is that a vol-regime gate captures the strong-rally
periods while staying flat during low-vol stagnation, **shrinking MDD
materially without proportionally shrinking CAGR**. The win condition
(vs buy-hold) is a Sharpe edge driven by reduced vol/MDD rather than
higher gross drift.

## Datasets

- **gld_long** (GLD daily 21.4y) — 21 years gives the regime gate
  multiple full vol cycles (2008 GFC, 2011 peak, 2013 collapse, 2020
  COVID, 2022 stagflation, 2024 ATH). Primary cross-validation dataset.
- **xauusd_real** (XAUUSD daily 6.3y) — 2020+ window includes COVID
  + stagflation + ATH cycle. Tests whether the same regime gate
  generalizes from 21-y mixed-regime to 6-y recent-regime — the GS-4/5/6
  cross-dataset failure mode is the central risk here.
- **xauusd_intraday** (XAUUSD 1h 6.3y) — same calendar window as
  xauusd_real with 5119 bars/yr. Used as **execution-precision sanity check**:
  the regime gate is daily by construction, so intraday execution should
  give Sharpe ≈ xauusd_real. Material divergence would indicate a bug
  rather than an edge.

## Timeframes used

`[1d, 1h]`. Both cached in Tiingo (`INFRASTRUCTURE.md`). No 30m / 15m
/ 1m needed → no cTrader Open API fetch required.

## Broker tracks targeted

`broker_track: "both"`.

- **Track A (Pepperstone CFD)**: 8 bps RT spread + −1 bps/night swap
  long. Overnight hold is intrinsic to the strategy (regime episodes
  span weeks-months); intraday-close not applicable. Weekend hold
  multiplier 3× swap on Friday→Monday.
- **Track B (Inter ETF GLD)**: 100 bps FX RT + 40 bps/yr GLD ER (netted
  in price) + **DARF 15% on positive monthly net profits**. T+1
  settlement, but regime episodes span weeks → no daytrade restriction
  binds.

Per-track metrics reported separately. Top-K ranks the better-of-two.
Track B expected to score 5-15 points lower due to DARF + FX cliff;
turnover is the load-bearing variable.

## Hold-time profile (HARD GATE)

- **Expected mean hold**: ~30-90 trading days per regime episode
  (vol regimes are slow-moving by Sinclair's stationarity arguments).
- **swing-extended tag** — mean hold > 5 trading days is highly likely.
  Per WINNER_AND_RANKING.md, this caps tier at STRONG and disqualifies
  WINNER. Justified explicitly: the regime-gate mechanism IS slow by
  design; trying to compress it to mean-hold ≤ 5 days would defeat the
  purpose. The day/swing mission's secondary goal — find a strategy
  worth tracking even if not WINNER — still applies, and a STRONG-tier
  gold strategy with materially lower MDD is a candidate base for
  future IC-7 composition with a faster signal.

## Pre-validation screen (cost-aware, gold-loop standard)

The strategy has **no `|z|>kσ` entry trigger**, so the GS-9
state-machine-aware fwd-N-bar concern does NOT apply (no entry-dilution
during sustained extreme regimes — entries flip on bar where σ_60
crosses σ_252, not during a sustained run). Standard cost-aware pre-val
suffices:

For each dataset, compute regime flag history and measure:

| metric | symbol | pass condition |
|---|---:|---|
| pct_active (fraction of bars with flag=True)   | `p_active`  | 0.15 ≤ `p_active` ≤ 0.70 |
| mean log return when flag=True (annualized %)  | `μ_active`  | `μ_active > 0` |
| n_flips per year (regime transitions / year)   | `n_flips`   | `n_flips ≤ 8/yr` |
| annualized cost drag per year (bps)             | `cost_yr_bps` | `cost_yr_bps < 0.5 × μ_active_bps × p_active` |

`cost_yr_bps = n_flips × spread_RT_bps + p_active × 365 × |swap_long_bps_per_night|`

Pass threshold: at least 2/3 datasets must satisfy ALL 4 conditions. If
1/3 passes (esp. gld_long alone) → run backtest with explicit cross-
dataset risk flagged in final_report. If 0/3 pass → auto-abort.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**:

- Spread: 8 bps round-trip per regime flip (turnover = `n_flips × 2`
  bar transitions = `n_flips` round-trips, since flat→long is 1 turn,
  long→flat is 1 turn).
- Swap: −1 bps/night when long; 0 when flat.
- Weekend mult: 3× swap on Mon-after-Fri-long bars.
- No slippage modeled (regime-edge fills, not stops).

Annualized cost on gld_long with hypothetical p_active=0.40 + 4
flips/yr: `4 × 8 + 0.4 × 252 × 1 = 32 + 100.8 = ~133 bps/yr` =
~1.3% drag. Versus gold buy-hold +11.3% CAGR, this is small.

**Track B (Inter ETF GLD)**:

- FX RT: 100 bps per regime flip (round-trip).
- DARF: 15% × max(0, monthly_net_profit_pretax) per fiscal month,
  allocated to the last bar of each month per `cost_models.py`.
- ER: 40 bps/yr (already netted in GLD price; not double-counted).

Annualized cost with same p_active=0.40 + 4 flips/yr: `4 × 100 = 400
bps/yr` from FX alone, plus DARF on positive months. This is ~5×
Track A's cost; expect 5-15 score-pt gap.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if any of these hold at end of Stage 4:

1. **Insufficient exposure**: `p_active < 0.15` on ≥ 2 of 3 datasets at
   pre-val. The strategy must trade enough of the time to compound a
   meaningful CAGR.
2. **No active drift**: `μ_active ≤ 0` on ≥ 2 datasets (regime captures
   the wrong half of the distribution).
3. **Sharpe collapse**: `Sharpe_strategy < Sharpe_benchmark − 0.30` on
   ≥ 2 datasets after Pepperstone CFD costs (Track A).
4. **MDD claim broken**: `MDD_strategy > MDD_benchmark` on ≥ 2 datasets.
   The core hypothesis is that vol gating reduces MDD; if it doesn't,
   the entire mechanism is rejected.

## Expected budget

- Configs to test: **1** (single pre-committed cfg `vol_regime_60_252`).
  No grid sweep — IC-8 closure prohibits parameter-sweep on a candidate
  with strong prior; single-cfg keeps DSR cumulative_n_trials at 10.
- Wall-time: ~30-45 min (single signal, simple state machine, no ML).
- Files to create:
  - `iterations/010-*/hypothesis.md` (this file)
  - `iterations/010-*/run_backtest.py` — pre-val + signal + state machine + 7-gate
  - `iterations/010-*/test_vol_regime_signal.py` — TDD spec for signal computation
  - `iterations/010-*/pre_val.json` + `results.json` + `final_report.md` + `verdict.json`

## Implementation plan

1. **Signal function** `compute_vol_regime_flag(prices, window_short=60, window_long=252)`:
   ```python
   log_ret = np.log(prices / prices.shift(1))
   sigma_short = log_ret.rolling(window_short).std() * sqrt(252)
   sigma_long = log_ret.rolling(window_long).std() * sqrt(252)
   flag = (sigma_short > sigma_long).fillna(False).astype(int)
   ```
   For xauusd_intraday: resample 1h → 1d for computation, propagate
   daily flag to all 1h bars within day.

2. **TDD test** in `test_vol_regime_signal.py`:
   - Hand-rolled fixture: synthetic price series with known σ_60/σ_252
     ratio, assert flag flips at correct boundary.
   - Edge case: insufficient data (first 252 bars) → flag=False
     (NaN-handling).
   - Cross-lib parity: hand-rolled numpy vs pandas-rolling, assert ±1e-10.

3. **Pre-validation** runs first; auto-abort if 0/3 pass.

4. **State machine**: position[t] = flag[t]; held into bar t+1.
   No exit logic beyond regime change; flag flips ARE entry/exit signals.

5. **Cost models**: apply both `apply_pepperstone_costs` (Track A) and
   `apply_inter_costs_with_darf` (Track B) to the gross PnL series.

6. **7-gate battery** per dataset, separately for Track A and Track B
   (the score's "primary" track is A; B is secondary metric).

7. **Cross-lib**: hand-rolled numpy backtest assertion ±3 pp CAGR vs
   pandas implementation (G7).

## Anti-pattern checks (sanity)

- ❌ NOT IC-1 (vol-target wrapper absorption): the gate produces a
  binary {0, 1} position, not a vol-scaled continuous one. No vol-target
  wrapper. The "σ_60 > σ_252" comparison happens on the SIGNAL side
  before sizing, not on the OUTPUT side.
- ❌ NOT IC-2 (input/output regime double-count): no second regime gate
  applied to position size; sizing is the regime gate itself.
- ✅ Different family from iter 003's MR (this is regime, not entry-MR);
  potentially IC-7 secondary if a primary +Sharpe-3-of-3 stream emerges.
- ✅ Different from GS-7/8/9: no `|z|>kσ` trigger → state-machine-aware
  pre-val not needed.
