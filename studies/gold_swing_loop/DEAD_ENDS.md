# Gold Swing Loop — Structural Dead-Ends

**Add patterns here when an iter closes a structural family.** Do NOT
re-test variants of anything listed below. Sister loop's full dead-end
catalog at `../strategy_hunt_loop/DEAD_ENDS.md` (5 KLOC of empirically
validated closures across 54+ iters).

---

## Inherited cross-loop closures (apply directly to gold)

These were validated empirically in the sister equity loop and are
**structurally portable** to single-asset gold day/swing context.

### IC-1 — Vol-target wrapper absorbs same-family overlays
*(sister iter 020/021/040)*

If you wrap a gold-vol-correlated overlay (e.g., gold-IV gate) in a
gold-vol-target sizing layer, the wrapper compresses position exactly
when the overlay's E[premium] is largest → Sharpe regresses to base
or worse. Closes any cfg of `gold-vol-overlay × gold-vol-scale-target`.

**How to tell**: signal correlation with σ²_position > 0.85 in pre-val
screen.

### IC-2 — Output regime gate = input regime gate (double-counts)
*(sister iter 048)*

Re-using the same regime classifier (e.g., VIX threshold) at signal
INPUT and at position-size OUTPUT eats ~30% of the linear envelope via
sub-multiplicative compounding. Closes any cfg of `regime_gate(input)
× regime_gate(output, same_signal)`.

**How to tell**: same VIX/regime signal feeding both entry rule and
position scaler.

### IC-3 — 50/50 composition only when Sharpes are similar
*(sister iter 049 — Markowitz identity validated to 4 decimals)*

Combining stream A (S=1.32) + stream B (S=0.69) at 50/50 gives combined
S ≤ max(S_A, S_B), even at ρ=0. Markowitz optimum is w_A ∝ S_A. Closes
any 50/50 additive composition where component Sharpes differ by > 30%.

**How to tell**: |S_A − S_B| / max(S_A, S_B) > 0.30.

### IC-4 — Modulation axes (input/weight/output/leverage) saturate
*(sister iter 042/043/044/047/048)*

Once a base strategy hits its rubric ceiling (sister loop: 84 STRONG),
modifying the entry signal, weight schedule, output leverage, or
gate-timing axis **does not break the ceiling** — the modification
trades variance for variance. Path to score-uplift is **additive new
uncorrelated streams**, NOT modulation.

**How to tell**: 3+ orthogonal modulation attempts on the same base
all regress DSR by different mechanisms.

### IC-5 — Survivorship-biased data destroys cross-sectional ranking
*(sister iter 003, 054)*

Tiingo cache only includes tickers that survived to 2014+. Cross-sectional
rankings on this universe correlate with the cap-weighted index
(survivorship → winner-tilt). Closes cross-sectional momentum/ranking
strategies on Tiingo equity universe **until CRSP/Norgate point-in-time
delisted coverage exists**.

**Gold relevance**: directly applies if testing `gold + miner basket`
or cross-sectional precious-metals strategies. Single-asset gold itself
is N/A.

### IC-6 — Pre-validation screen mandatory for overlays
*(sister iter 014/019)*

Before running full backtest on an overlay/composition candidate,
measure rolling-60d correlation of (overlay signal, base position size).
If `exceed_frac(|ρ| > 0.30)` > 20% across the test window, abort —
the overlay will be cointegrated structurally. Costs ~30s of pre-val,
saves ~90 min wasted compute + a wasted DSR trial.

**How to apply**: always run pre-val screen on overlay candidates
before Stage 3.

### IC-7 — Out-of-family composition at corr < 0.50 compounds DSR
*(sister iter 045/046 — TOP candidates)*

Two STRONG-tier streams from different families combined via Markowitz
weighting at correlation 0.40-0.60 deliver DSR uplift roughly proportional
to (1 − ρ²)^0.5. Best result: ρ=0.41 → DSR p 0.222 → 0.041 (−81%).

**How to apply**: the WINNER path likely involves combining gold-trend
(momentum-family) + gold-MR (mean-reversion-family) + macro-overlay
(fundamentals-family) at proportional-Sharpe weights, NOT amplifying
a single mechanism.

### IC-8 — DSR n_trials drains fast; pre-commit single cfg
*(sister iter 046/047/050)*

`cumulative_n_trials` deflator grows monotonically. Each grid-sweep
or weight-sweep increment moves DSR p worse by ~0.005-0.010 even when
the underlying Sharpe is identical. Once a candidate is at DSR p 0.04-0.08
(STRONG-tier), ANY further sweep on same base will cross 0.05 strict
threshold. **Pre-commit single cfg per iter** unless Bonferroni-justified.

**How to apply**: avoid grid-search on already-promising configurations.
Test ONE pre-committed config; if it works, deploy; if it fails,
pivot to NEW base.

---

## Gold-specific dead-ends (start empty; populate as iterations close paths)

### GS-1 — Daily Connors RSI(2) < 5 long-only MR with SMA(5) exit dies on gold across regimes
*(iter 001 — `iterations/001-2026-04-26-0151-connors-rsi2/`)*

Pure short-period RSI mean-reversion (period ≤ 4, threshold ≤ 10,
exit at close > SMA(N≤10)) is structurally dominated on gold by the
asset's persistent-trend drift profile.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

| dataset | Sharpe | bench Sh | Δ | CAGR | bench CAGR |
|---|---|---|---|---|---|
| gld_long (21.4y, mixed regime) | +0.04 | +0.68 | **−0.65** | +0.03% | +11.32% |
| xauusd_real (6.3y, bull only)  | −0.23 | +1.04 | **−1.27** | −1.30% | +19.93% |
| xauusd_intraday (6.3y, daily resample) | −0.20 | +1.10 | **−1.30** | −1.12% | +20.20% |

DSR/PSR p-values 0.43 / 0.73 / 0.70 → SR is statistical noise.

**Why structural** (not parameter-tweakable):
- Signal entry timing is correct (RSI(2) does identify oversold dips)
- Exit rule (close > SMA(5)) fires too early — captures the bounce
  but misses the trend-resumption rally
- Same defect appears on mixed-regime gld_long and bull-only xauusd
  → not a regime artifact

**Closes**: any cfg of `RSI(p≤4) < threshold(≤20) ∧ exit at close > SMA(N≤10)`
on any single-asset gold instrument. **Do not test parameter sweeps**
of {RSI period 2-4, threshold 5/10/20, SMA exit 3/5/10} — the structural
defect (early exit ignoring trend) is the same.

**How to escape (informs iter 002+)**:
1. Replace SMA exit with regime-aware exit (ATR trail after T+1, or
   vol-target-aware exit)
2. Add a TREND filter to entry side (long-only above SMA(200)) so MR
   only fires *with* the dominant trend, not against it
3. Pivot family entirely (trend-following or macro-overlay)

Connors himself documents this issue on commodity tests
`[short_term_trading_strategies, p.105-118]` and recommends a trend
filter — option 2 above.

### GS-3 — Single-mech standalone strategies on single-asset gold are dominated by buy-hold's drift (REFINED iter 003)
*(iter 002 — `iterations/002-2026-04-26-0214-donchian-20-10-turtle/`; refined iter 003 — `iterations/003-2026-04-26-0228-rsi2-sma200-filter/`)*

> **Iter 003 update**: Connors' SMA(200) regime-gate rescue (escape hatch
> #1 below) was tested empirically and **PARTIALLY VINDICATED**: it lifts
> the unfiltered MR's Sharpe by +0.26 to +0.44 across all 3 datasets and
> produces positive Track-A Sharpe on every dataset (first single-mech to
> do so). But the rescued strategy STILL trails buy-hold by 0.38-0.86
> Sharpe because gold's drift is too steep for any selective-entry signal
> to bridge alone. So GS-3 narrows to: "single-mech **standalone**
> (regardless of regime gate) cannot beat gold buy-hold; the path forward
> is **IC-7 Markowitz composition** of multiple low-correlation streams,
> not amplifying any single mechanism." Iter 003's MR-with-SMA(200) is
> Pareto-valid as a base stream for that future composition.


Combined with iter 001's GS-1 (mean-reversion family closed),
iter 002's Donchian-20/10 trend-follow result closes the **second
opposite single-mechanism family**. Both fail by ≥ 0.65 Sharpe vs
buy-hold across all 3 datasets, decisively.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

| family            | iter | gld_long Sharpe | xauusd_real Sharpe | xauusd_intraday Sharpe |
|---|---|---|---|---|
| MR (RSI(2)<5 + SMA(5) exit)   | 001 | +0.04 | −0.23 | −0.20 |
| Trend (Donchian-20/10)        | 002 | −0.20 | +0.24 | +0.24 |
| **Buy-hold (benchmark)**      |  —  | **+0.68** | **+1.04** | **+1.10** |

Critical finding: gld_long MDD on iter 002 was **73.97% — DOUBLE the
buy-hold MDD of 45.6%**. Bidirectional trend-following on gold's
mixed-regime 21.4y window is a STRUCTURAL TRAP — short signals get
destroyed by bull-rally tails, while long signals are too late for the
breakout move.

**Why structural** (not parameter-tweakable):
1. Single-mechanism timing has no information advantage over buy-hold's
   long-bias drift on a persistently-trending asset like gold.
2. Adding parameter sweeps (entry lookback ∈ {10, 15, 20, 25, 30}, exit
   lookback ∈ {5, 7, 10, 15}) cannot rescue this — the structural defect
   is the **lack of a regime gate**, not the parameter tuning.
3. IC-8 (DSR drains fast) means parameter-sweeping these single-mechs
   is *negative-EV*: each trial worsens the cumulative-DSR penalty
   while testing variants of an already-broken family.

**Closes**: any single-mechanism, single-asset, single-direction-family
day/swing strategy on gold WITHOUT a regime filter. Specifically:
- All RSI/Bollinger/Stochastic short-period MR variants (closes
  Strategy menu candidates 5-8 from BASE_MEMORY without trend filter)
- All Donchian/EMA-cross/momentum-channel breakout variants without
  regime gating (closes candidates 1-2, 11)
- Bidirectional trading on gld_long without regime filter is a TRAP
  (doubles MDD)

**How to escape** (informs iter 003+):
1. **Layer a regime filter** (Connors' published fix): MR or trend-follow
   gated by `close > SMA(200)` for long-bias OR VIX-regime gate. Most-cited
   fix; one extra param vs base; preserves DSR budget. `[short_term_trading_strategies, p.105-118]`
2. **Switch to fundamentally-different signal source** (macro: DXY,
   real yields, COT positioning). Different family avoids the
   single-mech-timing defect entirely. `[ilmanen_expected_returns, ch.10]`,
   Bauer-Mertens 2018.
3. **Compose multiple single-mech streams via Markowitz** (per IC-7) —
   currently NOT viable because both base streams (iter 001 + iter 002)
   are net-negative. Tabled.

### GS-4 — Cross-asset volatility-derived (VIX) signals on single-asset gold are regime-fragile on short windows
*(iter 004 — `iterations/004-2026-04-26-0400-vix-recovery-5d/`)*

The post-VIX-recovery flight-to-quality framing (long gold for fixed
5 d after VIX z-score crosses *down* through +1 from a recent peak
> +2σ) delivers **positive Track-A Sharpe (+0.23) on the 21-y mixed-
regime gld_long dataset** but **flips negative (−0.16) on both 6.3-y
xauusd datasets**. The cross-dataset failure is structural, not a
parameter-tuning issue.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

| dataset | Sharpe | bench Sh | Δ | CAGR | gates | mean hold |
|---|---:|---:|---:|---:|---:|---:|
| gld_long (21.4y, mixed regime)        | +0.23 | +0.68 | −0.45 | +1.17% | 4/7 | 5.00d |
| xauusd_real (6.3y, 2020+ regime)      | −0.16 | +1.04 | −1.20 | −1.03% | 2/7 | 5.00d |
| xauusd_intraday (6.3y, 2020+ regime)  | −0.16 | +1.10 | −1.26 | −1.04% | 2/7 | 5.00d |

DSR p-values: 0.49 / 0.93 / 0.93 → SR is statistical noise on every
dataset; G6 bootstrap CI lower bound is also negative on every
dataset (−0.37, −1.33, −1.33).

**Why structural** (not parameter-tweakable):

1. **Regime conditionality**. The 2004-2020 sample is dominated by
   equity-stress events (2008 GFC, 2010 Flash Crash, 2011 Eurozone,
   2018 Q4) where the "VIX peak → VIX recovery → gold rallies on
   safe-haven flow" pattern is the dominant dynamic. The 2020-2026
   sample mixes inflation-stress (2022) + central-bank-driven (2024
   ATH on rate-cut priors) regimes where the cross-asset stress
   signal misfires (gold can fall *during* VIX spikes, e.g., March
   2020 COVID).
2. **Insufficient stress events on short data**. ~5-7 distinct
   recovery cross events fire in the 6.3-y window (vs 90 in 21 y);
   the strategy needs many low-probability events for the law of
   large numbers to express the premium. G2 DSR p=0.93 confirms
   pure noise.
3. **Cross-asset signal regime-shifts faster than gold's own**.
   VIX-gold correlation flips with macro regime (positive during
   equity-only stress; negative during dollar/inflation shocks).
   Single-asset signals (e.g., iter 003's gold-MR) suffer less from
   this because they read the asset's own dynamics, which are
   stationary at a slower timescale.

**Closes**: VIX-derived signals as **primary** entry triggers for
single-asset gold day/swing strategies on Tiingo's available 6.3-y
xauusd data. Specifically:
- VIX z-score recovery cross + fixed hold (this iter)
- VIX > 25 absolute regime gate (Variant 5 in pre-val; pre-cost
  Sharpe 0.32 with 30+ d mean hold = swing-extended)
- VIX z > 2σ spike + fixed hold (Variant 3 in pre-val; t-stat ~0.4
  on 5-d fwd → near-zero edge on raw data)
- VIX-flight-to-quality variants from BASE_MEMORY direction #1
  (consumed)

**Does NOT close**:
- VIX as a *secondary* component of a multi-stream Markowitz
  composition (per IC-7), where a primary robust-cross-dataset
  stream carries the load and VIX adds diversification at near-zero
  correlation.
- VIX-derived signals on **longer-history data sources** (e.g., if
  Tiingo XAUUSD coverage ever extends to pre-2020).

**How to escape** (informs iter 005+):
1. Switch to **fundamentally-driven** overlays (DXY, real yields, FOMC)
   that capture gold's macro drivers DIRECTLY rather than indirectly
   via cross-asset stress proxies. Most likely candidates: DXY
   60-d EMA + z-score (BASE_MEMORY #2), TIPS DFII10 < 60-d MA falling
   (BASE_MEMORY #3), pre-FOMC drift (BASE_MEMORY #4).
2. **Defer IC-7 composition** until at least one more single-mech
   stream delivers positive Sharpe across all 3 datasets simultaneously
   (iter 003's MR base is the only such stream so far).

### GS-5 — Tiingo FX cross cache window (2020-2026) collapses gld_long's 21-y advantage for any cached-FX strategy
*(iter 005 — `iterations/005-2026-04-26-0500-dxy-zscore-recovery/`)*

The cached FX cross series in `data/tiingo/daily/prices/` —
`usdcad.parquet`, `usdchf.parquet`, `usdjpy.parquet` — all start
**2020-01-01 → 2026-04-17 (6.3 y)**, NOT 2004 like GLD daily. Any
strategy whose *signal* depends on this basket inherits the 2020+
window via inner-join and cannot leverage `gld_long`'s 21.4-y
long-history validation. The strategy therefore reduces to a single
~6-y window that collides head-on with **GS-4** (cross-asset signals
regime-fragile on 2020+ Tiingo coverage).

**Empirical evidence** (iter 005's pre-validation screen on `gld_long`,
post FX inner-join 2020-04 → 2026-04, 51 trigger events):

| metric | value | min threshold | pass? |
|---|---:|---:|:---:|
| n_events             | 51       | 20    | ✓ |
| mean 5-d log-return  | **−0.520 %** | (implicit > 0) | **✗** |
| t-stat               | **−1.876** | 0.50  | **✗** |
| hit-rate             | **0.451** | 0.50  | **✗** |

The forward 5-d gold return after a DXY-proxy z-down-cross-through-−1
is **directionally inverted** vs the textbook USD-weak→gold-strong
prediction. The auto-abort fired before any 3-dataset backtest ran;
no Sharpe / CAGR / MDD / gates were computed.

**Why structural** (not parameter-tweakable):

1. **Window constraint is binding regardless of params**. The
   `(z_threshold, hold_days, cooldown_days)` parameters cannot extend
   the FX history; the strategy is calendar-locked to 2020+. Any
   sweep on params remains tested on the same ~6-y window where
   GS-4 already showed cross-asset framings fail.

2. **The 2020+ regime mix is qualitatively different from the
   1971-2019 textbook period**. Three identifiable mechanisms invert
   the USD-gold relationship in this window:
   - **Mar-2020 COVID**: USD spiked +8 % in 2 weeks AND gold fell
     −12 % in same window (dollar liquidity scramble overrode safe-
     haven flow).
   - **2022 stagflation**: USD strong on Fed hikes, gold *also* high
     on inflation hedge demand — USD-gold correlation flipped
     positive for the year.
   - **2024-25 rate-cut-pricing**: USD weakened on dovish-Fed
     repricing AND gold rallied — but the rally happened *during*
     persistent z-score weakness (multi-week regime), not at the
     z-cross-through-−1 moment. The down-cross fires too LATE
     (USD already very weak); subsequent USD reversion drags gold
     down.

3. **Down-cross-of-−1 is mean-reversion entry timing, not trend-
   continuation**. The trigger fires at the *moment* USD just crossed
   below −1 σ — by definition near a recent local minimum of USD
   strength. From there, mean reversion (USD strengthens back toward
   z=0) is the higher-prior path. A trend-continuation framing
   would look like "DXY 60-d EMA negative slope AND last 20-d
   return < 0", not "z just touched −1". This is a strategy-design
   defect, not a data defect — but fixing it requires a different
   signal-construction grammar (different family per IC-8), not a
   parameter sweep.

**Closes**: any cfg of `DXY-derived signal × cached FX basket
(usdcad/usdchf/usdjpy)` on the gold swing loop. Specifically:
- DXY z-score down-cross + fixed N-day hold (this iter, all reasonable
  N ∈ {3, 5, 7, 10})
- DXY z-score up-cross + short gold (signal inversion of this iter;
  not re-tested per IC-8 but the same window-constraint applies)
- DXY rolling-mean filter ("long when DXY < 60-d MA") on cached FX
  (BASE_MEMORY direction #1 framing)
- All `(z_threshold ∈ {−0.5, −1.0, −1.5}, hold ∈ {3, 5, 7, 10},
  cooldown ∈ {5, 10})` param sweeps on cached FX

**Does NOT close**:
- DXY-based signals on **longer-history data** sourced from FRED
  (ICE DXY index `DTWEXBGS` or `DTWEXM` back to 1971), Refinitiv,
  Norgate, or other providers. A future "data infra" iter could
  fetch the full DXY series and re-test on the 2004-2026 window.
  **But** that's a structurally different test — the pre-val needs
  to be re-run on the longer series.
- Trend-continuation framings of FX-derived signals (e.g., "long
  gold when DXY 60-d EMA negative slope AND last 20-d cumulative
  return < 0"). Different signal-construction grammar; needs its
  own pre-val + IC-8 trial budget.
- DXY as a *secondary* IC-7 component once a primary stream exists
  (per the same logic that GS-4 doesn't close VIX as secondary).

**How to escape** (informs iter 006+):

1. Switch to **fundamentals signals with longer-history sources**:
   - **Pre-FOMC drift** — FOMC dates back to 1980 via FRED `DFEDTAR`
     change events or NY Fed press-release calendar. Leverages
     gld_long's 2004-2026 window with ~170 events. `[trading_systems_methods,
     p.479]`, Lucca-Moench 2015 *JoF* 70(1).
   - **Real yields filter (TIPS DFII10)** — FRED data back to
     2003-01-02 → ~22 y, leverages gld_long. Bauer-Mertens 2018
     FRBSF EL.
2. Switch to **pure date-driven signals** that don't need any data
   beyond the gold price series:
   - **Calendar effects** (TOM, month-end, Sep-Nov Indian wedding-
     season). `[trading_systems_methods]`. Track-B trivially viable.
3. **Reframe** the DXY signal entirely (different grammar):
   - "long gold when DXY 60-d EMA slope < 0 AND last 20-d return < 0"
     — trend-continuation, not mean-reversion. Still inherits 2020+
     window so usable only as IC-7 secondary onto a long-history
     primary.

### GS-6 — Calendar-event signals (pre-FOMC drift) on single-asset gold are too weak vs Pepperstone CFD costs even with empirically positive raw drift
*(iter 006 — `iterations/006-2026-04-26-1135-pre-fomc-drift/`)*

The Lucca-Moench 2015 pre-FOMC drift on SPX (~+49 bps over the 24-h
pre-announcement window) was hypothesized to port to gold via Ilmanen
ch.10's USD/real-yield channels. The strategy entered long at close
T-2 and exited at close T+1 (4 trading day hold) on every scheduled
FOMC announcement 2004-2026 (178 hardcoded dates from federalreserve.gov;
171 fully-contained events on gld_long).

**Empirical evidence**:

Pre-validation screen on gld_long (long-history dataset) — **PASSED**:

| metric | value | min threshold |
|---|---:|---:|
| n_events                | 171      | 50    |
| mean 4-d log-return     | +0.151%  | > 0   |
| t-stat                  | +0.764   | 0.50  |
| hit-rate                | 0.5205   | 0.50  |

Drift IS empirically positive on 21.4 y of GLD: 52% of FOMC events
followed by positive 4-day gold returns, mean cumulative drift +15 bps,
t-stat 0.76. **The signal exists.**

Full backtest (Track A net of Pepperstone CFD costs):

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates |
|---|---:|---:|---:|---:|
| gld_long          | −0.04 (−0.72) | −0.64% (−11.96 pp) | 36.0% (−9.6 pp) | 2/7 |
| xauusd_real       | −0.23 (−1.27) | −2.12% (−22.05 pp) | 20.5% (+0.1 pp) | 2/7 |
| xauusd_intraday   | −0.23 (−1.34) | −2.11% (−22.31 pp) | 20.5% (−3.9 pp) | 2/7 |

DSR p-values: 0.93 / 0.98 / 0.98 (cumulative_n_trials=6) → noise on
every dataset. Kill criterion fired (3/3 datasets net-negative Sharpe).

Cost attribution on gld_long (over 21.4 y):
- Gross PnL = +13.9% (171 events × +15 bps each ≈ +25.6%; some negative
  events drag actual gross to +13.9%)
- Spread cost = −13.7% (171 round-trips × 8 bps RT = 1370 bps)
- Swap cost = −5.0% (avg 3 nights × −1 bps × 171 trades ≈ 513 bps)
- **Net PnL = −7.3%** → drift ~5× too small vs round-trip costs

**Why structural** (not parameter-tweakable):

1. **Cost cliff at the trade frequency**. Per-trade gross drift = 15 bps,
   per-trade Pepperstone cost = ~83 bps round-trip (8 bps spread + 3
   nights × 1 bps swap + occasional weekend mult). Net edge per trade
   = −68 bps. No reasonable parameter sweep on `(bars_before, bars_after)`
   ∈ {(1,0), (2,0), (3,0), (1,1), (2,1), (3,1), (2,2), (3,2)} can raise
   the per-trade gross above the ~83 bps cost — the underlying drift is
   the asset's pre-announcement directional bias, which is bounded by
   gold's daily volatility (~75-100 bps/day). Per IC-8, parameter sweeps
   here are negative-EV.

2. **Time-out-of-market opportunity cost dominates on gold's 11.3%/yr
   drift**. Strategy holds long 12.7% of the time. Selective-entry
   signals must produce ≥ 30 bps per active day to even tie buy-hold's
   unconditional drift. FOMC drift produces ~3.8 bps per active day
   (15 bps / 4 days) — a full order of magnitude too low.

3. **Macro-regime non-stationarity hits xauusd 2020+ AGAIN**. Same
   closure pattern as **GS-4 (VIX)** and **GS-5 (DXY)**: signal
   positive on 21-y mixed-regime gld_long, inverts on 6.3-y 2020+
   xauusd. Mechanisms in 2020+:
   - **2022 stagflation hike cycle**: USD strengthened post-FOMC
     → gold fell post-FOMC despite hike-cycle-end priors.
   - **2024-25 rate-cut anticipation**: "buy rumour, sell news" →
     gold fell post-announcement after pre-meeting rallies.
   These dominate the 43 events in the 6.3-y window → mean negative,
   net Sharpe negative, gates 2/7.

**Closes**:
- Pre-FOMC drift T-2 to T+1 (this iter)
- Variants {T-3 to T+0, T-1 to T+2, T-1 to T+0, T-3 to T+1, T-2 to T+0}
  on the same FOMC date list (covered by IC-8: parameter sweeps within
  closed family are negative-EV)
- Other US-equity-literature calendar events with similar 4-bar
  horizons applied to single-asset gold (Lucca-Moench pre-FOMC drift,
  monthly TOM, options-expiry effect — all ported from equity)

**Does NOT close**:
- FOMC-driven gold signals at LONGER horizons (full month after
  rate-cut announcement vs rate-hike: directional gating, not raw
  drift) — different mechanism, different cost amortization.
- FOMC as SECONDARY component of an IC-7 composition (the 0.11
  correlation with iter 003's MR base is IC-7-attractive if either
  base improves to cross-dataset positive).
- Calendar effects on instruments with much LOWER costs than 8 bps
  Pepperstone CFD (e.g. direct gold futures, retirement account with
  no per-trade cost).

**How to escape** (informs iter 007+):

1. **Pure price-action signals** that don't depend on macro regime
   (z-score MR on 1h, realized-vol regime gate, Bollinger squeeze
   release). These sidestep the GS-4/5/6 cross-dataset failure mode
   entirely because the 2020+ window IS the asset's own price action
   at higher frequency.

2. **Refine FOMC into directional gate** (futures-implied rate-cut
   probability). Long gold ONLY when implied-cut > 0 (dovish bias);
   otherwise flat. Adds a directional conditioner that addresses
   the 2020+ regime-flip mechanism. **Compounds DSR cost** so defer
   until a regime-stationary baseline exists.

3. **Acknowledge cross-dataset gate is the binding constraint**.
   3 consecutive iters (GS-4/5/6) hit this. Either (a) accept that
   any non-stationary macro signal will fail loop's gate regardless
   of merit, or (b) reduce dependence on the short xauusd window via
   pure price-action signals validated on 21-y gld_long.

### GS-7 — Pure z-score MR on single-asset gold (1h or 1d, no regime gate) is structurally dominated by Pepperstone CFD cost cliff
*(iter 007 — `iterations/007-2026-04-26-1157-zscore-mr-1h/`)*

Pure z-score mean-reversion (z = (close − rolling_mean(lookback)) /
rolling_std(lookback); long when z < −2; exit z ≥ 0 OR N-bar timeout)
on single-asset gold delivers **net-negative Sharpe on all 3 datasets
across both 1h and daily timeframes** despite a nominally-passing
pre-validation screen on the primary intraday dataset. The mechanism
is the **same cost-cliff pattern as GS-6** but with a different
signal source — confirming that cost cliff is the binding constraint
for ANY mean-reversion-style signal whose per-trade gross edge is
< ~12 bps on the Pepperstone CFD cost stack.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

Pre-validation on `xauusd_intraday` (60-bar lookback, 24-bar timeout):

| metric | value | min threshold | pass? |
|---|---:|---:|:---:|
| n_events                | 1940     | 50    | ✓ |
| mean fwd-24h log-return | +0.0177% (= +1.76 bps) | > 0 | ✓ |
| t-stat                  | +0.667   | 0.50  | ✓ |
| hit-rate                | 0.5531   | 0.45  | ✓ |

**Pre-val PASSED nominally** — but the +1.76 bps mean fwd-return is
**~5× smaller than the 8 bps round-trip Pepperstone spread floor**.

Full backtest:

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | gates | mean hold | n trades |
|---|---:|---:|---:|---:|---:|
| gld_long (21.4y, 1d, lookback=20) | −0.05 (−0.74) | −0.50% (−11.82 pp) | 4/7 | 4.69 d | 111 |
| xauusd_real (6.3y, 1d, lookback=20) | −0.19 (−1.22) | −0.92% (−20.85 pp) | 2/7 | 4.82 d | 28  |
| xauusd_intraday (6.3y, 1h, lookback=60) | −0.31 (−1.41) | −2.69% (−22.89 pp) | 2/7 | **0.99 d** | 285 |

Per-trade attribution on `xauusd_intraday` (285 trades over 6.29 y):

| component | per-trade (bps) | annualized (% of equity) |
|---|---:|---:|
| Gross edge (early-exit-weighted realized hold-period return) | +3.5 | +1.59%/yr |
| Spread (8 bps RT) | −8.0 | −3.62%/yr |
| Swap (continuous accrual at 1/24 bps/bar over ~24-bar hold) | −0.84 | −0.38%/yr |
| **Net per trade** | **−5.3** | **−2.42%/yr** |

DSR p-values 0.95 / 0.97 / 0.99 (cumulative_n_trials=7) — pure noise.
Kill criterion fired (3/3 datasets net-negative on Track A).

Notably, `xauusd_real` (daily 2020+ window) is **gross-NEGATIVE before
costs** (per-trade gross −5.7 bps on 28 trades) — same cross-dataset
failure pattern as **GS-4 (VIX) / GS-5 (DXY) / GS-6 (FOMC)**. This
is now the **fourth consecutive iter** to confirm that signals
gross-positive on long-history `gld_long` invert on the 2020+
`xauusd_real` window, but unlike GS-4/5/6 the source is purely
price-based (no macro / cross-asset / calendar input).

**Why structural** (not parameter-tweakable):

1. **Per-trade gross edge floor**. The pre-val measured fwd-24h drift
   is +1.76 bps (intraday) and the early-exit-weighted realized
   per-trade gross is +3.5 bps. The Pepperstone cost stack on a
   round-trip is 8 bps (spread) + ~1 bps (24h swap) = 9 bps minimum.
   Per-trade net is structurally negative regardless of (z_entry,
   z_exit, lookback, timeout) parameter choices because the **gross
   edge magnitude is bounded by gold's intraday vol-normalized
   pullback amplitude** (~1-5 bps per signal event), which is too
   small to overcome the cost stack.

2. **Same closure pattern across all 3 datasets** — the cost-cliff
   arithmetic holds on 1d (gld_long: +8.4 bps gross / 12.7 bps cost
   per trade) AND 1h (xauusd_intraday: +3.5 bps / 8.8 bps). Different
   timescales sample different reversion processes but BOTH are
   bounded below the cost floor.

3. **Pre-val template is COST-BLIND**. The current screen
   (`mean > 0 AND t-stat > 0.5 AND hit-rate > 0.45`) admits any
   signal with statistical significance > 0 vs zero; it does NOT
   compare gross edge magnitude to cost floor. Iter 005 was caught
   (signal directionally inverted on 2020+ window). Iter 006 was
   admitted (gross +15 bps but ~5× too weak vs 83 bps cost). Iter
   007 was admitted (gross +1.76 bps, ~5× too weak vs 9 bps cost).
   **The template needs a cost-magnitude gate**.

**Closes**:

- z-score MR with z<-2 entry, z>=0 exit, 24h/5d timeout (this iter)
- Variants on (z_entry ∈ {−1.5, −2.0, −2.5}, z_exit ∈ {0, +0.5, +1.0},
  lookback ∈ {30, 40, 60, 90, 120}, timeout ∈ {5, 12, 24, 48})
  on the same single-asset z-score grammar — covered by IC-8.
- Bollinger %B re-entry (BASE_MEMORY candidate #7) — same z-score
  family with a different boundary; cost cliff arithmetic identical.
- Asia-session fade (BASE_MEMORY candidate #8) — single-asset
  intraday MR; same cost-cliff structure unless gap-fill events
  deliver > 12 bps expected reversion (rare; deferred).

**Does NOT close**:

- z-score MR + REGIME GATE (e.g., long only when realized vol
  σ_60d > σ_252d, vol-expansion phase). Different mechanism family
  (regime-conditional, not signal-conditional). Candidate #13.
- Pair / spread MR on a STATIONARY spread (Chan's actual framework
  — gold-silver ratio z-score, candidate #17). The cointegrated
  spread can have per-trade reversion magnitudes much larger than
  12 bps if the spread is empirically stationary (ADF reject).
  Worth testing in a STRUCTURALLY different iter.
- z-score MR as a SECONDARY component of an IC-7 composition once
  a primary stream lifts above the cost cliff. But iter 007's
  −0.16 to +0.52 correlations with iter 003 are mixed (same-family
  on daily, uncorrelated on intraday) — not the out-of-family
  ρ ∈ [0.40, 0.60] that IC-7 needs.
- Lower-cost execution paths (gold futures via different broker,
  retirement account with no per-trade cost). Out of scope for
  this loop's Pepperstone Track A target.

**Methodology corollary**:

The pre-validation screen template should be augmented with a
cost-magnitude gate before iter 008:

```python
# Augmented pre-val gate (target for iter 008+):
cost_floor_bps = 8.0  # Pepperstone spread RT
mean_fwd_bps = mean_fwd_log_return * 1e4
required_edge_bps = 1.5 * cost_floor_bps  # 12 bps margin
passed = (
    mean_fwd_bps > required_edge_bps   # NEW magnitude gate
    and t_stat > 1.0                   # tighter (was 0.5)
    and hit_rate > 0.50                # tighter (was 0.45)
    and n_events >= 50
)
```

This would have correctly rejected iter 007 (1.76 bps < 12 bps),
iter 006 (15 bps < 12 bps × 1.5 with cost margin), and saved 2
DSR trials.

**How to escape** (informs iter 008+):

1. **Switch to stationary-spread MR** (gold-silver ratio, candidate #17).
   Chan p.51-58, p.71-73: cointegrated spreads admit much larger
   per-trade reversion magnitudes than single-asset price series.
   Pre-val ADF test on the ratio + cost-aware magnitude gate.
2. **Switch to regime-gating signal** (realized-vol regime gate,
   candidate #13). Long when σ_60d > σ_252d; mean hold = vol-
   regime duration (longer); per-trade cost amortizes over the
   longer hold. Different mechanism family (regime, not entry).
3. **Pre-val infrastructure upgrade** (Option C in iter 007 final
   report): land cost-aware pre-val helper before iter 008.

### GS-8 — XAU/XAG ratio mean-reversion is non-stationary AND directionally inverted on Tiingo's 2020+ window
*(iter 008 — `iterations/008-2026-04-26-1223-xau-xag-pair-mr/`)*

The Chan-canonical pair-MR formulation (`z = (log_ratio − rolling_mean(60))
/ rolling_std(60)`; short ratio at z>+2, long ratio at z<−2; |z|≤0.5 exit
OR 10-bar timeout) on the gold-silver ratio (XAU/XAG) was hypothesized to
escape the **GS-7 cost cliff** by replacing single-asset per-trade edge
(~1-9 bps) with stationary-spread reversion magnitudes that — per Chan's
GLD-USO worked example — can be 50-500 bps per trade.

**Empirical evidence** (pre-validation on all 3 datasets BEFORE backtest):

| dataset | ADF p (log-ratio) | n entries (\|z\|>2) | mean signed-fwd-N-bar (bps) | t-stat | hit-rate |
|---|---:|---:|---:|---:|---:|
| gld_long (1d, fwd-10d, 60d lookback)        | **0.0516** | 671  | **−41.55** | −1.00  | 45.5% |
| xauusd_real (1d, fwd-10d, 60d lookback)     | **0.2012** | 215  | **−97.64** | **−3.05** | 45.1% |
| xauusd_intraday (1h, fwd-24h, 60h lookback) | **0.2003** | 4346 | **−7.67**  | **−2.93** | 49.2% |

The "signed fwd-N-bar" column is the return on the position the
hypothesis would take: `signed_fwd = -sign(z) × (log_ratio[t+timeout] −
log_ratio[t])`. **A negative value means the ratio EXTENDED** (trend
continuation, opposite of MR). All 3 datasets are negative, with
|t-stat| ≥ 2.9 on the 2 short-window datasets (n_events 215 + 4346).

Auto-abort fired at pre-val; no full backtest. Score 0/100 (FAIL),
DSR trial counted (cumulative_n_trials = 8).

**Why structural** (not parameter-tweakable):

1. **ADF stationarity rejected on all 3 datasets**. The p-values
   (0.052 / 0.20 / 0.20) span just-borderline (gld_long, 5022 obs,
   ADF stat −2.85 vs 5% crit ≈ −2.86) to clearly-non-stationary on
   the 2020+ datasets (ADF stats ≈ −2.21 vs 5% crit ≈ −2.86). Chan's
   pair-MR framework requires **empirical stationarity** of the
   spread; without it, the z-score grammar applies to a drifting
   process and the "mean to revert to" itself wanders. Parameter
   sweeps on `(lookback, z_entry, z_exit, timeout)` cannot create
   stationarity that isn't in the data.

2. **Directional inversion is robust across timescales**. The
   signed-fwd inversion fires on daily AND intraday data — different
   sampling frequencies but same behavior. The 1h signal magnitude
   (−7.67 bps) is small but statistically very significant (t=−2.93,
   n=4346); the 1d signal magnitudes (−41.55 / −97.64 bps) are
   large with t=−1.00 / −3.05. This is not a small-sample artifact;
   it's a regime property of the 2020+ XAU/XAG data.

3. **2020+ regime breaks the historical relationship**. Three
   identifiable mechanisms invert the standard MR prediction in
   this window:
   - **Mar-2020 COVID**: silver crashed 35% in 3 weeks while gold
     stayed flat → ratio spiked +50%; over the next 6 months silver
     rallied 75% while gold rose 30% → ratio normalized over 6
     months, NOT 10 days.
   - **Jan-2021 Reddit silver squeeze**: silver +25% in 2 days,
     gold flat → z-score swung from +1 to −2 in 48h, then ratio
     resumed pre-squeeze trend over weeks → 10-bar fwd window
     sees continued silver outperformance.
   - **2022-2026 macro divergence**: gold = ATH on safe-haven /
     CB buying flows; silver = lagging on industrial-demand
     weakness. Multi-year ratio drift downward; |z|>2 events fire
     during the drift, ratio extends in same direction.

**Closes**:

- z-score MR with z>±2 entry, |z|≤0.5 exit, 10-d/24-bar timeout on
  XAU/XAG ratio (this iter)
- Variants on `(z_entry ∈ {1.5, 2.0, 2.5}, z_exit ∈ {0, 0.5, 1.0},
  lookback ∈ {30, 60, 90, 120}, timeout ∈ {5, 10, 15, 20})` —
  covered by IC-8 (parameter sweeps in a closed family are
  negative-EV; ADF rejection is parameter-invariant).
- Bollinger-band reformulation of XAU/XAG ratio (band-edge re-entry;
  same z-score family, same stationarity prerequisite).
- Half-life-fitted lookback variants — half-life only matters when
  the spread is empirically stationary; ADF rejected on all 3 datasets.

**Does NOT close**:

- **TREND-FOLLOWING the same XAU/XAG signal** at extreme z: same
  data, same lookback, sign-flipped position. Pre-val empirical
  evidence already collected by this iter (just flip sign):
  +41.55 / +97.64 / +7.67 bps mean fwd-N-bar. xauusd_real magnitude
  (97.6 bps) clears 1.5× cost margin (45 bps) and is statistically
  significant (t=+3.05). gld_long borderline (1.39× cost vs 1.5×
  required). **Iter 009 PROMOTED candidate** — different signal-
  construction grammar (momentum vs MR), structurally novel vs
  GS-1..GS-8.
- **Pair MR on a DIFFERENT asset combo** — e.g., gold vs gold-miner
  ETF (GLD/RGLD or GLD/GDX). Miner is a leveraged equity claim on
  the underlying, structurally different from a 1:1 spot pair;
  might cointegrate where XAU/XAG didn't. Requires a fresh ADF
  test on the actual pair before any backtest.
- **Pair MR with a Kalman-filtered hedge ratio** (Chan p.81-87,
  Engle-Granger 2-step OLS). This iter used a 1:1 hedge ratio
  (raw log of price ratio). A Kalman-filtered β might restore
  stationarity if the true hedge ratio drifts ≠ 1 over the window.
  Higher complexity; defers DSR cost.
- **Multi-spread Markowitz composition** (XAU/XAG + GLD/GDX + ...) —
  combining multiple non-stationary spreads might net out to an
  approximately stationary aggregate. Out of scope until at least
  one single-spread base works.

**How to escape** (informs iter 009+):

1. **Trend-follow the inverted signal** (per "Does NOT close" #1
   above) — leverages this iter's pre-val data directly; cheap to
   re-test (same engine, sign-flipped).
2. **Realized-vol regime gate** (BASE_MEMORY candidate #13): long
   gold ONLY when σ_60d > σ_252d. Single-asset, LONG-ONLY,
   sidesteps both GS-4/5/6/8 cross-dataset failure (no cross-asset
   data) AND the cost cliff (regime IS the signal — buy-hold drift
   captured during regime, flat outside).
3. **Augmented pre-val helper** as shared module (Option C from
   iter 007): lift `cost_aware_pre_val_gate` + ADF helper from
   iter 008's `run_backtest.py` into
   `studies/gold_swing_loop/pre_val_helpers.py`. Pays back at
   every iter 009+; ~30 min refactor.

**Methodology corollary** (vindicates iter 007 Option C):

The augmented cost-aware pre-val template introduced in this iter
(`cost_aware_pre_val_gate` with magnitude > 1.5 × cost floor +
t-stat > 1.0 + hit-rate > 0.50 + n_events ≥ 30, plus ADF
stationarity check) **caught the failure in 6 seconds of compute**
vs the ~30-45 min a full backtest would have taken. It also saved
1 DSR trial that would otherwise have inflated the deflator and
penalized future iters' p-values. **Adopt as standard pre-val for
iter 009+ on any spread/pair/MR candidate.**

### GS-9 — Pair TREND-FOLLOW on XAU/XAG ratio fails despite positive pre-val (entry-dilution methodology gap)
*(iter 009 — `iterations/009-2026-04-26-1246-xau-xag-pair-trend/`)*

The sign-flipped twin of iter 008's MR signal — entering LONG ratio
when `z>+2`, SHORT ratio when `z<−2`, with timeout-only exit at 10
bars (1d) / 24 bars (1h) — **passed augmented cost-aware pre-val
on 1 of 3 datasets** (xauusd_real: +97.64 bps mean fwd-10d, t=+3.05,
n=215, 2.17× the 1.5× cost margin) but **all 3 datasets net-negative
on Track A backtest**. The closure mechanism is a methodology gap
in the augmented pre-val template — not a regime-inversion failure.

**Empirical evidence** (Track A net of pair Pepperstone CFD costs;
30 bps RT spread + 0.8 bps/night swap):

| dataset | Sharpe | bench Sh | Δ | per-trade gross (bps) | pre-val mean (bps) | gross/pre-val | per-trade net (bps) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gld_long          | −0.18 | +0.68 | −0.87 | **−29.78** | +41.55 | **−0.72×** | −68.70 |
| xauusd_real       | −0.06 | +1.04 | −1.10 | +25.14 | +97.64 | 0.26× | −11.53 |
| xauusd_intraday   | −1.41 | +1.10 | −2.51 | +4.65  | +7.67  | 0.61× | −25.98 |

Per-trade GROSS edge is **5-15× smaller than the pre-val mean**
on every dataset. On gld_long the realised gross is even
**directionally INVERTED** vs the pre-val sign. Gates 3/3/2 vs
thresholds 5/4/4 — every dataset under threshold-1 except xauusd_real
which barely reaches threshold-1. DSR p=0.999/0.954/1.000 (cumulative
n_trials=9). xauusd_real OOS Sharpe of +1.005 is captured in a
narrow ~1.9-y window (Apr-2024 → Apr-2026, gold ATH); FWD-2022
Sharpe is −0.039 — no out-of-sample generalisability.

**Why structural** (not parameter-tweakable):

1. **Entry-dilution mismatch between pre-val and state machine.**
   The augmented pre-val computes `signed_fwd_bps` at EVERY bar
   where `|z|>z_entry`, treating each as an independent entry.
   The state machine only enters when the prior bar was FLAT and
   holds for exactly `timeout` bars before re-evaluating. During a
   sustained `|z|>z_entry` run, the state machine takes one entry
   per `timeout`-bar slot; the pre-val averages over ALL bars in
   the run. Later entries (deeper into the run, closer to trend
   exhaustion) catch the reversion and dilute the realised mean.
   The pre-val is therefore an **upper bound** on per-trade gross,
   not an unbiased estimator.

2. **Gold-silver ratio at extreme z is a NEAR-EXHAUSTION signal**
   on the 2020+ window. Silver's industrial-demand cycle and the
   Reddit-squeeze, COVID, and 2022-stagflation regimes all
   produce extreme-z events that LOOK trending in pre-val (because
   the average of the next N bars is positive on the entry-side
   of the run) but ACTUALLY revert at higher frequency than the
   bar-average suggests. The pre-val captures the early-run drift;
   the state machine catches both the early-run drift AND the
   late-run reversion, with the reversion dominating.

3. **Cost cliff still binding** at the realised-gross level. Even
   on xauusd_real where the pre-val's claimed +97.64 bps was
   2.17× the 1.5× cost margin, the realised per-trade gross
   (+25.14 bps) is below the 30 bps RT cost floor before any
   swap or weekend multiplier. The other 2 datasets have realised
   gross below 5 bps — well into GS-7 / GS-8 territory.

**Closes**:

- Pair trend-follow with z>±2 entry, timeout-only exit (this iter)
- Variants on `(z_entry ∈ {1.5, 2.0, 2.5}, timeout ∈ {5, 10, 15, 20},
  lookback ∈ {30, 60, 90, 120})` — IC-8: parameter-invariant failure
- Bollinger-band reformulation of trend-follow on the same XAU/XAG
  ratio (band-edge re-entry; same z-score family)
- Pair trend-follow with z-based exit (z_exit>0): the entry-dilution
  pattern is independent of exit choice
- Pair trend-follow on the inverse asset combo (XAG/XAU) — perfectly
  equivalent under sign-flip; no new info

**Combined with GS-7 + GS-8, this closes BOTH MR and TREND-FOLLOW
directions for `|z|>k σ` entry grammar on commodity-spot data**
(at least with bar-averaged pre-val as the screening tool). The
remaining viable directions either (a) drop `|z|>k σ` as a primary
timing trigger, OR (b) add a regime conditioner that restricts
entries to the narrow sub-windows where the signal generalises.

**Does NOT close**:

- **Regime-gated XAU/XAG trend-follow** — only enter the trade
  when an additional macro regime conditioner agrees (e.g., gold
  > SMA(200) for LONG ratio entries, or `realized_vol_60d >
  realized_vol_252d`). One additional parameter, one extra DSR
  trial; potentially restores the narrow-window edge seen in
  xauusd_real's last-30% OOS (+1.00 Sharpe).
- **Pair MR / trend-follow on a DIFFERENT asset combo** — GLD/GDX
  (gold vs miner ETF), where the leverage-claim relationship MAY
  cointegrate where 1:1 commodity-spot didn't. Requires fresh ADF
  + augmented-pre-val + state-machine-aware-pre-val.
- **Pair MR with Kalman-filtered hedge ratio** (Chan p.81-87) on
  XAU/XAG. Higher complexity; defers DSR cost.
- **Single-asset (gold-only) directional-momentum bet using
  XAU/XAG z as gating signal** — different P&L driver: trade
  outright XAUUSD long when ratio z>+2 (cost stack 8 bps RT
  instead of 30 bps). Worth testing iter 010+.

**Methodology corollary** (vindicates iter 007 Option C extension):

The augmented cost-aware pre-val template should be extended with
a **state-machine-aware variant** that measures fwd-N return ONLY
at bars where the state machine would actually transition from flat
to ±1 (i.e., first bar of each `|z|>z_entry` run after a low-z gap
of ≥ N bars, given the timeout). The realised per-trade gross on
this filtered sample would have correctly predicted iter 009's
failure (xauusd_real realised gross ~+25 bps in the state-machine-
aware sample, NOT +97 bps as the bar-averaged sample claimed).

Lift before iter 010+ as Option D (highest-priority infra task).

**How to escape** (informs iter 010+):

1. **Realized-vol regime gate** (BASE_MEMORY candidate #13):
   `long XAUUSD when σ_60d > σ_252d`. No `|z|>k σ` trigger →
   sidesteps GS-7/9 entry-dilution failure mode. Single-asset,
   LONG-ONLY → both Track A and Track B viable for first time
   since iter 003.
2. **Single-asset gold directional via XAU/XAG z gate** — trade
   outright XAUUSD (8 bps RT cost) using ratio z as macro signal.
   Different P&L driver; gold's drift compounds on LONG entries.
   Pre-val needs re-measurement on XAU outright fwd return (NOT
   ratio's).
3. **State-machine-aware pre-val helper** (INFRA, urgent) — lift
   from iter 008/009 into shared module + add the filtered-entry
   variant per the methodology corollary above.

### GS-10 — Realized-vol regime gate (σ_60>σ_252) standalone is NEAR_FAIL on gold but is the 2nd viable IC-7 base
*(iter 010 — `iterations/010-2026-04-26-1314-vol-regime-gate-60-252/`)*

The Sinclair vol-cone framework `[volatility_trading, p.58-59]` was
ported to a binary degenerate: long XAUUSD whenever `σ_60d(log_returns)
> σ_252d(log_returns)` at close[t], flat otherwise. Single-asset,
LONG-ONLY, both broker tracks viable. The hypothesis was that vol-
expansion regimes capture safe-haven / inflation / shock-driven gold
rallies while the gate sits flat during low-vol stagnation, **shrinking
MDD materially without proportionally shrinking CAGR**.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

Pre-validation gate (cost-amortization template specific to slow-regime
signals — different from iter 008/009's bar-averaged fwd-N):

| dataset | p_active | μ_active (bps/yr active) | n_flips/yr | cost (bps/yr) | passed? |
|---|---:|---:|---:|---:|:---:|
| gld_long          | 0.426 | +849 | 5.19 | 178 | ✓ (cost 178 < 0.5×849×0.426 = 181) |
| xauusd_real       | 0.436 | +243 | 4.61 | 178 | ✗ (cost 178 ≥ 0.5×243×0.436 = 53) |
| xauusd_intraday   | 0.436 | +270 | 4.61 | 178 | ✗ (cost 178 ≥ 0.5×270×0.436 = 59) |

1/3 datasets passed (gld_long marginally; cost-amortization ratio
178/181 = 0.98). Backtest ran on all 3 with cross-dataset risk flagged.

Full backtest (Track A net of Pepperstone CFD costs, 8 bps RT spread +
−1 bps/night swap long):

| dataset | Sharpe (Δ vs bench) | CAGR (Δ vs bench) | MDD (Δ vs bench) | gates | mean hold | per-trade gross/cost/net (bps) |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.21 (−0.48) | +1.96% (−9.36 pp) | 37.9% (**−7.6 pp** ✓) | 4/7 | 40.96 d | +176/+64/+112 |
| xauusd_real       | +0.04 (−1.00) | −0.24% (−20.17 pp) | 24.0% (+3.6 pp ✗) | 4/7 | 49.47 d | +81/+58/+23 |
| xauusd_intraday   | +0.09 (−1.01) | +0.33% (−19.86 pp) | 27.6% (+3.2 pp ✗) | 4/7 | 46.04 d | +93/+47/+46 |

DSR p-values: 0.728 / 0.928 / 0.912 (cumulative_n_trials = 10) — pure
noise on every dataset. OOS Sharpe positive on all 3 (+0.31 / +0.03
/ +0.09); FWD-2022 also positive on all 3 (+0.31 / +0.04 / +0.09).
G2 / G3 / G6 fail because absolute Sharpe is small. Identical 4/7
gate fingerprint to iter 003 (RSI(2)+SMA(200)).

IC-7 correlation diagnostic vs iter 003's net returns:
- gld_long: ρ = +0.235 (n=5384)
- xauusd_real: ρ = +0.197 (n=1700)
- xauusd_intraday: ρ = −0.067 (n=1401)

Both bases sit in the IC-7 sweet spot (sister 045/046 best result was
ρ=0.41 → DSR p 0.222 → 0.041). **First viable IC-7 pair in this loop.**

**Why structural** (not parameter-tweakable):

1. **Opportunity cost dominates against gold's drift profile.** The
   regime fires ~43% of bars — meaning the gate is FLAT 57% of the
   time, including long stretches where buy-hold accrues steady drift
   (e.g., 2009-2011 low-vol bull rally, 2023-2024 low-vol ATH cycle).
   No reasonable parameter tuning of `(σ_short, σ_long)` lookbacks
   recovers the missed-drift cost — the structural defect is that
   "vol-expansion" and "positive drift" are imperfectly correlated
   on gold (vol-expansion can be DOWN-vol-expansion, e.g., March 2020
   COVID crash, Cyprus 2013).

2. **Cross-dataset failure mode bifurcates differently from
   GS-4/5/6/7/8/9.** Where prior iters had signal-INVERSION on the
   2020+ window (gld_long +Sh, xauusd_real −Sh), iter 010 has
   directionally-CONSISTENT +Sh on all 3 (smaller magnitude on the
   short window because cost amortization is worse). The strategy is
   robust in sign, weak in magnitude. This is qualitatively different
   from GS-4..GS-9 — and it's exactly the iter 003 pattern.

3. **MDD-claim partial vindication only on long history.** gld_long's
   −7.6 pp MDD reduction confirms the mechanism CAN reduce drawdowns
   when the sample contains true vol-driven crashes (2008 GFC,
   Mar-2020 COVID). But on the 2020+ window, the gate's vol-
   expansion-active phase coincides with the 2022 stagflation drawdown
   (gold fell while vol expanded), giving +3.6 pp WORSE MDD than
   buy-hold. Asymmetric variants (with drawdown filter) would
   address this — open for iter 011+.

**Closes**:

- σ_60 > σ_252 single-asset gold standalone LONG-ONLY (this iter)
- Variants on `(σ_short ∈ {20, 30, 60, 90, 120}, σ_long ∈ {120, 180, 252,
  504})` provided σ_short < σ_long — covered by IC-8 (parameter sweeps
  in closed family negative-EV; the structural defect is the
  drift-correlation mismatch, not lookback choice)
- Bollinger-band-σ-cross variants (same comparison grammar; same
  defect)
- Equivalent KAMA-ER threshold gates `[trading_systems_methods, p.131]`
  with single-direction gate

**Does NOT close**:

- **Inverse signal** (σ_60 < σ_252, "low-vol bull regime", LONG-ONLY)
  — different hypothesis, captures the trending-bull stretches iter
  010 missed. Mechanically opposite; pre-val expects different
  μ_active distribution. Iter 011 PROMOTED.
- **Asymmetric vol regime** (`σ_60>σ_252 AND drawdown_60d < 10%`):
  filters out high-vol-DOWN regimes, keeps only high-vol-UP. Adds
  one parameter; MAY resolve MDD-claim failure on 2020+. Worth
  iter 012 test.
- **Multi-window gates** (e.g., `σ_30>σ_120 AND σ_60>σ_252`) — different
  signal grammar; restricts to strongest vol-expansion phases only.
- **Vol regime as IC-7 SECONDARY** stream on top of a primary
  +Sharpe-edge stream. Specifically, IC-7 composition with iter 003's
  RSI(2)+SMA(200) base is structurally viable (ρ ≈ +0.20 in IC-7 sweet
  spot), but BLOCKED until ≥1 base achieves Sharpe edge over benchmark
  (currently both NEAR_FAIL).

**How to escape** (informs iter 011+):

1. **Inverse vol-regime gate** (PROMOTED). Tests the "low-vol bull
   regime" hypothesis: gold's strongest drift periods are
   directionally-LOW-vol. `[volatility_trading, p.58-59]` (vol cone)
   + `[trading_systems_methods, p.13-14]` (metals = low-noise
   trend-conducive market). Single-asset, LONG-ONLY, structurally
   different from iter 010 (opposite signal direction).
2. **Asymmetric vol regime with drawdown filter** as the next iter
   if #1 also lands NEAR_FAIL — it directly addresses the MDD-claim
   failure on 2020+ datasets.
3. **Different family entirely** (TIPS DFII10 directional, gold-only
   directional via XAU/XAG z): if both vol-regime variants land
   NEAR_FAIL, the gold-only-LONG-ONLY single-mech family is
   structurally exhausted on this loop's data, and macro overlays
   become the only remaining single-mech direction.

**Methodology corollary** (cost-amortization pre-val for slow-regime
signals):

Iter 010's pre-val gate template (`p_active ∈ [0.15, 0.70]`; `μ_active
> 0`; `n_flips/yr ≤ 8`; `cost_yr_bps < 0.5 × μ_yr_active × p_active`)
correctly flagged the 2020+ datasets as marginal-cost-coverage. This
template is the slow-regime analog of iter 008's bar-averaged `mean
fwd > 1.5 × cost_floor` gate (which is for `|z|>kσ` triggers). Both
should be available in `pre_val_helpers.py`. Lift before iter 012+
when slow-regime candidates re-appear.

### GS-11 — Inverse vol-regime gate (σ_60<σ_252) STANDALONE is MARGINAL — BUT first base above benchmark on 2/3 ds, unblocks IC-7
*(iter 011 — `iterations/011-2026-04-26-1334-vol-regime-gate-inverse/`)*

The structural inverse of iter 010 (σ_60>σ_252) — long XAUUSD when
`σ_60d < σ_252d` (low-vol bull regime). Sinclair vol cone is
directionally agnostic; iter 010 + iter 011 partition the cone-comparison
space exactly (XOR=1 on non-warmup bars verified by test). The inverse
direction is grounded in Kaufman's classification of metals as **low-noise
markets** `[trading_systems_methods, p.13-14]` — low-noise = sustained
trend = LOW realized vol — so gold's bull-trend drift should cluster in
the σ_60<σ_252 half of the partition.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

Pre-validation (cost-aware, 3/3 datasets pass — first iter since 003):

| dataset | p_active | μ_active (bps/yr active) | n_flips/yr | cost (bps/yr) | passed? |
|---|---:|---:|---:|---:|:---:|
| gld_long          | 0.527 | +1 274 | 5.14 | 213 | ✓ |
| xauusd_real       | 0.415 | +3 266 | 4.77 | 171 | ✓ |
| xauusd_intraday   | 0.415 | +3 266 | 4.77 | 171 | ✓ |

Iter 011's xauusd μ_active is **13× larger** than iter 010's (+243 bps/yr)
— direct evidence that gold's bull-trend drift clusters in vol-compression
regimes (Kaufman vindication).

Full backtest (Track A net of Pepperstone CFD costs, 8 bps RT spread +
−1 bps/night swap long; cumulative_n_trials=11):

| dataset | Sharpe (Δ vs bench) | CAGR (Δ vs bench) | MDD (Δ vs bench) | gates | DSR p | mean hold | gross/cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.481 (−0.203) | +4.80% (−6.52 pp) | 46.3% (+0.7 pp) | 4/7 | 0.275 | 51.6 d | 3.63× |
| xauusd_real       | **+1.418 (+0.380)** | +14.15% (−5.78 pp) | 10.4% (**−9.93 pp** ✓) | **7/7** | **0.018** | 47.1 d | 11.36× |
| xauusd_intraday   | **+1.592 (+0.489)** | +14.24% (−5.96 pp) | 11.1% (**−13.33 pp** ✓) | **7/7** | **0.009** | 44.1 d | 13.66× |

**This is the first strategy in 11 iterations to satisfy WINNER condition #1
(Sharpe edge ≥ +0.10 over benchmark on ≥ 2 of 3 datasets).** OOS-30%
Sharpe +1.00/+2.53/+3.04; FWD-2022+ Sharpe +1.45/+1.66/+1.88; bootstrap
99.9% CI low +0.18/+0.32 on xauusd (only −0.18 on gld_long). Walk-forward
6/8 windows pass on both xauusd datasets.

Score 50/100 = MARGINAL (winner_conditions_met=False). Held back by:

- **gld_long structural leak**: Sharpe +0.48 vs bench +0.68 (Δ −0.20); the
  21-y window contains 2013-2018 low-vol bear-drift periods where the
  signal fires but gold drifts DOWN. Single-mech inverse-vol cannot
  distinguish low-vol-bull from low-vol-bear; needs SMA(200) regime
  filter (Connors fix `[short_term_trading_strategies, p.106]`).
- **CAGR floor missed all 3 ds** (4.80/14.15/14.24% vs bench 11.32/19.93/
  20.20%; floors 9.05/15.94/16.16%). Strategy stays flat ~50-60% of bars,
  trading absolute return for risk-adjusted return.
- **Worst-DSR-p = 0.275** (gld_long, where Sharpe edge is weak); n_trials=11.
  Drives c3 = 0 in scoring even though both xauusd datasets pass DSR < 0.05.
- **Hold 44-52 d (swing-extended)** caps tier at STRONG even at score 90+.

**Why structural for STANDALONE** (not parameter-tweakable):

1. **gld_long bear-regime leak is window-deep, not lookback-deep**.
   Variants on `(σ_short ∈ {30, 60, 90, 120}, σ_long ∈ {180, 252, 504})`
   cannot resolve that "low vol AND bullish drift" must be conditioned
   on a SECOND signal (price/MA gate). Per IC-8 (DSR drains fast),
   parameter sweeps inside this closed-standalone family are negative-EV.

2. **CAGR/Sharpe trade-off is mechanical**. The gate stays flat ~50% of
   the time; CAGR is bounded above by buy-hold × p_active × selection_lift.
   No reasonable lookback choice raises p_active above ~0.55-0.60 without
   diluting selection lift. Standalone single-mech CANNOT close the CAGR
   gap; only IC-7 composition or modest leverage can.

3. **Swing-extended hold is intrinsic** to the slow-regime mechanism;
   compressing it would defeat the purpose. Mission-fit issue, not
   strategy-quality issue — surfaces as a candidate base for IC-7
   composition with a faster partner stream.

**Closes**:

- σ_60 < σ_252 STANDALONE single-asset gold LONG-ONLY (this iter)
- Variants on `(σ_short ∈ {20, 30, 60, 90, 120}, σ_long ∈ {180, 252, 504})`
  with σ_short < σ_long — covered by IC-8 (parameter-sweep negative-EV;
  the structural gld_long leak is lookback-invariant)
- Bollinger-band-σ-cross variants (same comparison grammar)
- KAMA-ER < threshold gates with single direction (same family)

**Does NOT close** — actively OPEN paths informed by this iter:

1. **IC-7 composition: iter 003 (RSI(2)+SMA(200)) + iter 011 (this)**
   — HIGHEST PRIORITY iter 012. ρ ≈ +0.10 / +0.10 / 0.00 sits in IC-7
   sweet spot (sister 045/046: ρ=0.41 → DSR p 0.222→0.041, −81%
   reduction). Markowitz proportional-Sharpe weights; expected DSR
   uplift on xauusd: 0.018→~0.005, 0.009→~0.002. May lift gld_long DSR
   above 0.05 threshold (currently 0.275). If passes, score climbs to
   75+ → STRONG with swing-extended tag.
2. **Inverse vol-regime + SMA(200) regime filter** (gld_long bear-leak fix).
   One added parameter, one DSR trial. Targeted at closing gld_long's
   structural weak link. Becomes redundant if path #1 already lifts
   gld_long DSR above 0.05.
3. **Asymmetric high-vol gate** (`σ_60>σ_252 AND drawdown_60d<10%`) —
   captures iter 010's high-vol-UP rallies separately from high-vol-DOWN
   drawdowns. Completes the regime partition; potential 3-stream IC-7
   with iter 003 + iter 011.
4. **Inverse vol-regime as IC-7 SECONDARY** stream on top of any future
   primary stream that lifts CAGR floor. The MDD-halving property is
   complementary to most directional signals.
5. **Modest leverage (1.5×) on Track A**. Mandate §3 allows up to 1:200;
   1.5× would lift CAGR floor pass count from 0/3 to 2/3 on xauusd
   without raising MDD above ceiling (10.4% × 1.5 = 15.6%, still below
   bench + 5pp = 25.4%).

**Methodology corollary**:

The XOR=1 complementarity of iter 010 (σ_60>σ_252) + iter 011 (σ_60<σ_252)
is structural — they tile the partition exactly. Their per-trade gross
asymmetry (iter 011 is **1.6×–7.7× more economically dense** than iter
010) directly tests Kaufman's "metals = low-noise → trending" hypothesis
on real data over 21 years (gld_long) and 6 years (xauusd). Result:
**vindicated** for xauusd (3/3 datasets show inverse direction wins by
6×–13×); **partial** on gld_long (1.6× ratio; bear-drift leak makes the
signal less clean on multi-decade window).

**How to escape** (informs iter 012+):

1. **IC-7 composition** — iter 012 PROMOTED #1 candidate. The sister
   loop's IC-7 framework is now empirically actionable in this loop
   for the first time.
2. **gld_long bear-regime fix** — parallel candidate; trivially testable.
3. **Asymmetric variants** — completes regime partition; longer horizon.
4. **Track B (Inter ETF) for xauusd_real**: standalone Track B post-DARF
   Sharpe = +0.996 — almost matches buy-hold's pre-tax Sharpe. With
   iter 011's MDD halving, Track B becomes a deployable Plano B
   candidate even before IC-7 lift. Worth modeling separately in iter
   013+.

### GS-12 — IC-7 composition iter_003 (RSI(2)+SMA(200)) + iter_011 (vol_regime_inverse_60_252) at full-sample Markowitz tangency cannot lift gld_long DSR<0.05
*(iter 012 — `iterations/012-2026-04-26-1353-ic7-rsi2-volregime-composition/`)*

The first IC-7-viable composition the loop ever ran (per iter 011's
ρ ≈ +0.10 / +0.10 / 0.00 measurement against iter 003) was the
explicitly-promoted iter 012 candidate. Composition was implemented
correctly: 14/14 TDD tests pass on Markowitz tangency formula, return
linearity, intraday-aggregation; full-sample weights computed without
clamping; ρ re-verified on the joined daily series. **Result: same
MARGINAL 50/100 score as iter 011 standalone, with a fundamentally
different shape of strengths/weaknesses.**

**Empirical evidence** (Track A net of Pepperstone CFD costs; both
component net-returns already cost-included; composition is
allocation-only, no extra costs):

| dataset | Sharpe (Δ vs bench) | DSR p (n=12) | gates | MDD (Δ vs bench) | weights (w_011, w_003) |
|---|---:|---:|---:|---:|---|
| gld_long          | +0.542 (−0.142)  | 0.201        | 4/7 | 25.1% (**−20.45 pp** ✓) | 0.420, 0.580 |
| xauusd_real       | +1.419 (**+0.381**) | **0.020**   | **7/7** | 9.5% (−10.89 pp ✓) | 0.906, 0.094 |
| xauusd_intraday   | +1.424 (**+0.321**) | **0.020**   | **7/7** | 8.8% (−15.64 pp ✓) | 0.827, 0.173 |

**Composition vs iter 011 standalone**:

| dataset | Sh iter011 | Sh iter012 | Δ | DSR p iter011 | DSR p iter012 |
|---|---:|---:|---:|---:|---:|
| gld_long          | +0.481 | +0.542 | +0.060 | 0.275 | 0.201 |
| xauusd_real       | +1.418 | +1.419 | +0.001 | 0.018 | 0.020 |
| xauusd_intraday   | +1.592 | +1.424 | **−0.168** | 0.009 | 0.020 |

**Why structural** (not weight-tuning-fixable):

1. **Quadrature ceiling on combined Sharpe**. The two-asset Markowitz
   optimum gives `S_comb² = (S_A² + S_B² − 2ρ·S_A·S_B) / (1−ρ²)`. On
   gld_long with S_A=0.481, S_B=0.299, ρ=0.104, this is
   `(0.232 + 0.089 − 0.030) / 0.989 = 0.294 → S_comb = 0.543`. Empirical
   measurement is +0.542 — exact match (validates the Markowitz
   implementation). **The combined Sharpe ceiling is set by the streams'
   quadrature, not by any weighting choice.** Lifting gld_long DSR
   p<0.05 at n_obs=5384, n_trials=12 needs Sharpe ≥ ~0.65 — neither
   stream nor their quadrature reaches there.

2. **Markowitz weights concentrate on dominant-Sharpe stream when
   |S_A − S_B| / max(S) > 0.5**. On xauusd, `S_011 / S_003 = 1.4 / 0.2 =
   7×` → IC-3 closure says 50/50 is wrong; Markowitz formula correctly
   gives w_011 = 0.83-0.91 → iter 003 contributes only 9-17% of capital
   → the composition is "iter 011 with a tiny RSI(2) overlay" on xauusd,
   which adds essentially zero Sharpe (Δ +0.001 on real, NEGATIVE
   −0.168 on intraday due to daily-resampling).

3. **Cross-frequency composition forces daily granularity**. iter 011's
   1h-frequency gain on xauusd_intraday (Sharpe +1.59 at 1h) cannot be
   preserved in a composition with iter 003 (daily-only signal). The
   common timeframe is daily; aggregating iter 011's 1h net returns to
   daily recovers Sharpe ~+1.42 (consistent with xauusd_real daily).
   **The intraday composition is fundamentally a daily test**.

4. **DSR cannot be manufactured from 2 DSR-failing components**. Both
   iter 003 and iter 011 individually fail gld_long DSR (p=0.30 and
   0.275 respectively). The combined Sharpe lift (+0.06) × n_obs=5384
   is insufficient to cross n_trials=12 deflator threshold. **Boundary
   condition for IC-7**: at least one base must be standalone-DSR-passing
   on the target dataset; otherwise correlation reduction alone cannot
   manufacture significance.

5. **No kill criterion fired**. Value-destruction kill threshold required
   2/3 ds with Sh < iter011 − 0.10; only intraday hit it (1/3). DSR
   no-progress kill required gld!<0.05 AND xauusd_real degrades ≥0.020;
   xauusd_real degraded only +0.002. Total gates 18/21 well above 14/21
   collapse threshold. **The composition is not value-destructive — it
   just isn't value-additive in DSR-terms either.**

**Closes**:

- IC-7 composition of iter_003 + iter_011 at **full-sample Markowitz
  tangency** for the goal "lift gld_long DSR<0.05".
- IC-7 composition of any pair where BOTH bases fail standalone DSR on
  the target dataset; correlation reduction alone (at ρ ≈ +0.10) cannot
  bridge the deflated-Sharpe gap.
- Variants of the same composition at proportional-Sharpe (no covariance
  term) weights — would concentrate even more on iter 011 and deliver
  even less iter 003 effect.
- Cross-frequency IC-7 compositions where one stream is intraday-native
  (1h) and the other is daily-native — the daily-aggregation cost
  destroys the higher-frequency stream's Sharpe density.

**Does NOT close**:

- IC-7 composition where at least ONE base is DSR-passing standalone
  on every target dataset. iter 013's planned single-stream `iter 011 +
  SMA(200)` (BASE_MEMORY direction #1) might lift gld_long DSR < 0.05
  standalone; in that case, a future iter could compose THAT improved
  iter 011 with iter 003 and the IC-7 framework should compound DSR
  via correlation reduction (this iter's null result) per sister 045/046.
- 3-stream IC-7 (asymmetric vol-regime per BASE_MEMORY direction #2 +
  iter 011 + iter 003) — adds a third orthogonal stream; quadrature
  ceiling moves up by S_3/√3; could exceed 0.65 on gld_long if asymmetric
  variant scores comparably to iter 003 standalone.
- IC-7 composition with a fundamentally-different family second stream
  (TIPS DFII10, gold-silver z, COT extremes) — these are different
  Sharpe distributions across datasets; could complement iter 011's
  weak-on-gld profile by contributing where iter 011 is weakest.
- Markowitz **rolling OOS** weights (1y trailing window) instead of
  full-sample fit — could rescue some n_trials deflator penalty by
  reducing in-sample-fit overstatement, but same fundamental quadrature
  ceiling.

**How to escape** (informs iter 013+):

1. **Single-stream gld_long bear-regime fix** (iter 013 PROMOTED): add
   SMA(200) trend filter to iter 011's σ_60<σ_252 signal. Position[t] = 1
   iff (σ_60 < σ_252) AND (close > SMA_200). One added parameter, one
   new DSR trial. Targets gld_long's 2013-2018 bear-stagnation regime
   directly. If this lifts gld_long Sharpe to ≥ 0.65 standalone, all 5
   strict winner conditions clear (except hold-time gate, which is
   unfixable for regime-gate mechanics → STRONG-with-swing-extended tag).
   Connors `[short_term_trading_strategies, p.106]`.

2. **Asymmetric vol-regime variant** (BASE_MEMORY direction #2): the
   high-vol-UP partition `σ_60>σ_252 AND drawdown_60d<10%`. Completes
   the partition started by iter 010 + iter 011. If standalone passes
   gates, opens 3-stream IC-7 path (asymmetric + iter 011 + #1 above) —
   3 orthogonal streams compound by S_3/√3 in quadrature ceiling.

3. **Different-family second stream**: TIPS DFII10 / DXY trend
   continuation / COT positioning. Each has different Sharpe distribution
   across datasets — could complement iter 011 where iter 003 didn't.
   Multi-iter investment (data fetch first), lower priority.

**Boundary condition addition for IC-7 framework** (apply to future
loops): "IC-7 composition compounds DSR proportionally to (1−ρ²)^0.5
**ONLY IF** at least one base is standalone-DSR-passing on the target
dataset. Composing two non-passing bases lifts combined Sharpe via
quadrature but cannot bridge the deflated-Sharpe-deflator gap when
both standalone Sharpes are too low."

### GS-13 — iter 011 (σ_60<σ_252) + Connors SMA(200) trend gate STANDALONE cannot lift gld_long DSR<0.05; bear-leak is the MDD problem, not the Sharpe problem
*(iter 013 — `iterations/013-2026-04-26-1413-volregime-inverse-sma200/`)*

The hypothesis (BASE_MEMORY direction #1, promoted iter 013): adding
Connors' SMA(200) trend gate to iter 011's σ_60<σ_252 long-only signal
would remove the 2013-2018 bear-stagnation regime where the σ ratio
fires (because vol IS compressed) but gold drifts down. Diagnosis was
correct on direction, wrong on magnitude:

**Magnitude of effect on gld_long**:

| metric | iter 011 standalone | iter 013 (+SMA200) | Δ |
|---|---:|---:|---:|
| Sharpe | +0.481 | +0.514 | **+0.033** |
| DSR p (n_trials=13 vs 11) | 0.275 | 0.253 | −0.022 |
| MDD | 46.29% | **36.78%** | **−9.51 pp** ✓ |
| n_trades | 22 | **95** | **+73** (4×) |
| mean_hold_days | 51 | **18.7** | **−32.3** (4× faster) |
| CAGR | 4.80% | 4.38% | −0.42 pp |
| p_active | ~0.50 | 0.330 | −0.17 |

**The hypothesis target was lift Sharpe by ≥ +0.18 to clear DSR
p<0.05.** Achieved +0.033. **Margin off by ~6×**. DSR p dropped only
0.022 — would need ~0.225 reduction to clear 0.05 from 0.275.

**Why the Sharpe lift was so small** (the structural finding):
1. The 2013-2018 bear-leak is concentrated in **drawdown depth**, not
   in **mean drift**: iter 011 had high downside variance during those
   years (large negative excursions) but the cumulative mean was only
   moderately negative. Removing those bars slashes MDD by 9.5 pp but
   leaves the Sharpe ratio nearly unchanged because Sharpe is
   variance-normalized. Sortino-style metrics (downside variance only)
   would show larger improvement.
2. **gld_long's true Sharpe deficit lives elsewhere**: 2008-2009 GFC
   recovery (σ_60<σ_252 fires AFTER GFC vol normalizes but the recovery
   already happened); 2018-2019 sideways drift (σ_60<σ_252 fires AND
   close>SMA(200) but gold chops sideways at low momentum); 2022 Fed
   inversion (vol-regime gate flickers as σ ratio crosses repeatedly).
   None of these regimes are addressable by a slow SMA(200) trend
   filter — they need either VIX-tail filters (closed by GS-4) or
   macro-fundamental signals (deferred to iter 014+).
3. **The 4× n_trades increase erodes per-trade economics**: SMA(200)
   crossings break iter 011's quarterly regime episodes into shorter
   pieces. Per-trade gross drops from ~660 bps (iter 011) to +139 bps
   (iter 013) on gld_long; per-trade cost from ~80 to +33 bps; net per
   trade from ~580 to +106 bps. Cost-to-gross ratio worsens from 12%
   to 24%.

**Effects on xauusd_real / xauusd_intraday** (the +Sharpe-edge datasets):

| metric | iter 011 → iter 013 (xauusd_real) | iter 011 → iter 013 (xauusd_intraday) |
|---|---|---|
| Sharpe | +1.418 → +1.463 (Δ +0.045) | **+1.592 → +1.693 (Δ +0.101)** |
| DSR p | 0.018 → 0.017 (cleaner) | 0.009 → 0.006 (cleaner) |
| MDD | 10.43% → 8.78% | 11.09% → 8.93% |
| Gates | 7/7 → 7/7 | 7/7 → 7/7 |
| mean_hold | 47d → 23.4d | 44d → 21.9d |

The SMA(200) gate is **net-positive on the working datasets too**: trims
a few mid-2022 down-bars, halving hold and improving all metrics. **The
intraday Sharpe RECOVERED from iter 012's daily-resampling-induced loss**
(iter 011: 1.59 → iter 012: 1.42 → iter 013: 1.69). iter 013 operates
single-stream so SMA(200) is computed on natively daily-resampled flag
(same as iter 011) and the 1h Sharpe density is preserved.

**Score**: 50/100 MARGINAL (1:20 + 2:15 + 3:0 + 4:0 + 5:15 + 6:0). Same
absolute score as iter 011 (50) and iter 012 (50) — **third consecutive
MARGINAL on the gld_long DSR-uplift axis**.

**Closes**:

- iter 011 + SMA(200) STANDALONE on gld_long for the
  gld-DSR<0.05-standalone goal at any window_short ∈ {30, 60, 90} ×
  window_long ∈ {180, 252, 365} × sma_trend ∈ {100, 150, 200, 250}
  combinations (the deficit isn't where these filters address — same
  ceiling).
- Variants with EMA(200) substituted for SMA(200) — smoother but same
  diagnostic cap (same bars filtered + same Sharpe ceiling).
- Variants with SMA(50) or SMA(100) (faster) — would produce more
  crossings, worse cost ratio, lower Sharpe.
- Implicitly **any single-stream filter on σ_60<σ_252 base** for
  gld_long Sharpe ≥ 0.65: the bear-leak diagnosis is wrong-magnitude,
  not wrong-direction; no filter alone closes the gap.
- GS-3 + GS-11 + GS-13 jointly establish: **single-asset gold
  vol-regime family has a Sharpe ceiling of ~+0.55 on the gld_long
  21y window**, regardless of filter parameterization.

**Does NOT close**:

1. **IC-7 composition with iter 013 as one base + a fundamentally
   different family as the other** (TIPS DFII10 macro / cross-asset
   risk-off / miner-spot divergence / volume-confirmed). The
   GS-12 boundary condition still requires ≥1 base be DSR-passing
   on every target dataset; iter 013 doesn't add that for gld_long
   (still p=0.253) but a macro stream might (different family
   distribution).
2. **iter 011 + drawdown_60d<10% gate** (BASE_MEMORY direction #2
   variant, σ_60<σ_252 side). Drawdown filter is a more direct
   bear-leak detector than SMA(200); should remove similar bars but
   may have lower n_trades-multiplier effect (fewer false crossings
   during chop). Worth iter 014 IF operator wants to drain single-mech
   filter axis before macro pivot.
3. **iter 013's MDD-reduction value as a portfolio component**. The
   −9.5 pp gld_long MDD improvement is real and reproducible; for a
   future risk-prioritized portfolio of gold strategies, iter 013
   strictly dominates iter 011 (same Sharpe, much lower MDD). It also
   strictly dominates iter 012 on the intraday axis (Sharpe +0.27).
4. **VIX-as-IC-7-secondary on iter 013 base** (GS-4 left this open).
   Iter 013's gld_long bar set is now well-trimmed; adding a VIX
   filter as IC-7 secondary may compound DSR via cross-family ρ
   without re-introducing GS-4's PRIMARY-mode failure. Multi-iter:
   first need a better xauusd VIX joint dataset.
5. **iter 011 with TF higher than 1d** (e.g., σ_60w on weekly gld_long)
   — different sampling frequency might capture different bear-leak
   structure. Lower priority (data-resampling investment with unclear
   payoff).

**Implications for iter 014+ candidate prioritization**:

- **HIGHEST**: TIPS DFII10 macro stream (BASE_MEMORY direction #3,
  promoted iter 014). Different family ⇒ different Sharpe distribution
  across datasets ⇒ structurally different shape from vol-regime trio
  (010/011/013). Multi-iter investment (FRED fetch first), but the
  only direction with a credible path to gld_long Sharpe ≥ 0.65
  beyond what regime-gating can deliver.
- **MEDIUM**: σ_60<σ_252 + drawdown_60d filter (single-mech variant
  of #2 above). Tests whether the direct-bear-leak filter behaves
  better than SMA(200) trend filter on n_trades-multiplier axis.
  If it does, may reach Sharpe ~+0.60 standalone (still below 0.65
  but worth knowing).
- **MEDIUM**: GDX/GLD divergence (cross-asset within gold complex,
  no FRED fetch). Different family without the macro-data
  investment.
- **LOWER**: SPY-GLD risk-off overlay — gold-equity coupling has been
  weakening; signal-to-noise unclear in 2020+ regime.

### GS-14 — TIPS DFII10 macro stream (real-rate falling, lookback=60d) does NOT have IC-7-required orthogonality to vol-regime family on gld_long; the rate cycle and vol cycle ride the same macro clock
*(iter 014 — `iterations/014-2026-04-26-1431-tips-dfii10-macro-stream/`)*

The hypothesis (BASE_MEMORY direction #1, PROMOTED iter 014, iter 013
"Next iteration suggestions" #1): real rates (10y TIPS yield via FRED
DFII10) are gold's fundamental driver and are **exogenous** to gold
prices — therefore a DFII10-falling regime gate should be roughly
orthogonal to iter 011's price-derived σ_60<σ_252 gate, unlocking IC-7
composition uplift on gld_long where iter 012's same-family Markowitz
hit the GS-12 boundary. **Empirically REJECTED at lookback=60d**.

**Single-stream backtest (iter 014, Track A net of Pepperstone costs)**:

| dataset | Sharpe (bench Δ) | DSR p (n=14) | gates | mean hold | per-trade net |
|---|---:|---:|---:|---:|---:|
| gld_long          | +0.319 (−0.366) | 0.604 | 4/7 | 16.2 d | +50.6 bps |
| xauusd_real       | +0.537 (−0.502) | 0.653 | 5/7 | 18.0 d | +116.5 bps |
| xauusd_intraday   | +0.820 (−0.283) | 0.350 | 5/7 | 16.8 d | +170.5 bps |

Score = 26/100 NEAR_FAIL. The signal is REAL (pre-val 3/3 pass; OOS
Sh 0.60-1.40 actually exceeds full-sample Sh; FWD-2022 Sh 0.67-1.10
positive in stress regime; G7 cross-lib EXACT 0.00e+00 pp parity) but
its Sharpe magnitude (0.32-0.82) is **insufficient to beat gold's
buy-hold drift** (0.68-1.10) on any dataset. **Cross-dataset kill #3
fired** (xauusd_real Δ AND xauusd_intraday Δ both < 0).

**The structural finding** (orthogonality refutation):

| dataset | ρ vs iter 011 (σ_60<σ_252) | ρ vs iter 013 (+SMA200) | ρ vs iter 003 (RSI MR) |
|---|---:|---:|---:|
| gld_long          | **+0.519** | **+0.492** | +0.184 |
| xauusd_real       | +0.321 | +0.332 | +0.170 |
| xauusd_intraday   | +0.275 | +0.287 | −0.018 |

**On gld_long, ρ ≈ +0.50 EXCEEDS the IC-7 sweet spot (sister 045/046
best at ρ=0.41)**. The two streams are partially co-moved through the
real-rate-cycle feedback loop:

1. Real rates fall (DFII10 → ↓) → DFII10-falling gate ON
2. Gold's discount-rate compresses → gold rallies
3. Gold's realized vol contracts (σ_60 drops faster than σ_252)
4. Vol-regime gate ON

The two signals ride the **same underlying macro clock** with a 30-90d
lag. They are NOT structurally independent on gold's long window.
**This refutes iter 013's "Next iteration suggestions" #1 IC-7
orthogonality assumption** for any 60-day-window macro signal.

**Why the deficit lives where it does**:

- All 3 datasets pass G4 OOS / G5 FWD-2022 / G7 cross-lib — the strategy
  isn't curve-fit, isn't broken in stress regimes, isn't a math bug.
- All 3 datasets fail G6 Bootstrap (99.9% CI low ∈ {−0.26, −0.82, −0.29})
  — the bottom of the resampling distribution dips negative because
  long-only single-asset gold strategies have fat negative tails when
  the regime gate is wrong.
- All 3 datasets fail G2 DSR with worst p=0.65 — at n_trials=14, the
  deflator demands ~Sharpe 1.5 for p<0.05, and macro delivers 0.32-0.82.
- gld_long n_trades=172 is high for "swing" — DFII10 has 30-90d
  mini-cycles inside the bigger trend, breaking the 60d gate frequently.

**Closes**:

- **IC-7 composition with iter 014 + iter 011/013 on gld_long**
  predicated on macro orthogonality: ρ ≈ 0.50 means combined Sharpe
  uplift is too small (~5-10%) to offset the +1 increment in
  cumulative_n_trials deflator.
- **TIPS DFII10 falling 60d STANDALONE on gold**: Sh ceiling ~+0.55
  on gld_long (matching the vol-regime family ceiling per GS-13);
  cannot beat buy-hold on any of the 3 datasets at this lookback.
- The "fundamentally different family" claim for **any 60-day-window
  macro signal** that derives directly from the rate cycle. The
  60-day window is the same time-scale as iter 011's σ_60 — both
  are quarterly horizons sampling the same rate-cycle / vol-cycle
  oscillation.

**Does NOT close**:

1. **DFII10 at different lookbacks** (1y, 3y) — slower lookbacks
   probe different cycle frequencies; ρ vs iter 011's σ_60 may drop
   substantially at 252d+ lookback. Caveat: longer lookback → even
   slower regime, even worse for day/swing horizon (already
   swing-extended at 60d).
2. **Different macro signal classes** that are NOT downstream of the
   rate cycle: DXY LEVEL (currency cycles ≠ rate cycles directly),
   CFTC COT positioning extremes (microstructure, not macro), gold
   lease rates (gold-supply dynamics), Indian rupee strength (real
   demand cycle).
3. **IC-7 composition on xauusd datasets** where ρ ≈ +0.30 sits
   inside IC-7 sweet spot. BUT xauusd was already at 7/7 gates on
   iter 013 — IC-7 uplift those datasets need is "Sharpe edge ≥ +0.10
   above buy-hold", not "DSR < 0.05". Iter 014's macro Sharpe edge on
   xauusd is **negative** (−0.50, −0.28), so composition would
   DILUTE not amplify. The IC-7 path on xauusd needs a stream with
   POSITIVE Sharpe edge AND ρ < 0.50, which neither vol-regime
   variants (already at ρ ≈ 1 with each other) nor macro at this
   lookback satisfy.
4. **Cross-asset overlays that don't ride the real-rate clock**:
   BTC-as-risk-off, GDX/GLD divergence, copper-gold ratio. These
   probe gold's role in different macro regimes.
5. **DFII10 as a SECONDARY filter** in a future composition where
   the primary stream has ρ < 0.30 vs both DFII10 AND vol-regime —
   DFII10 then operates as a 3rd-axis confirmation, where its
   moderate same-clock overlap with vol-regime is an asset (regime
   confirmation), not a liability (DSR drain).

**Implications for iter 015+ priorities**:

- **HIGHEST priority**: DXY LEVEL regime gate. Cached USDCAD/USDCHF/
  USDJPY proxies sufficient (no FRED fetch). Tests the corollary
  question: is the same-macro-clock problem **rate-specific** (then
  DXY may be more orthogonal) or **macro-generic** (then DXY too
  will hit ρ ≈ 0.50 vs vol-regime, and the entire macro-overlay path
  on gld_long is closed)?
- **MEDIUM priority**: CFTC COT non-comm net longs. Weekly cadence;
  positioning extremes are a different mechanism class entirely.
  Small infra investment (CFTC fetch). If COT also hits ρ ≈ 0.50, the
  problem is gold-cycle-generic (gold IS one cycle; everything
  correlates with it on gld_long's 21y window).
- **ACCEPTANCE option**: declare gld_long as "context check only" and
  refocus the loop on xauusd_real/xauusd_intraday as the primary
  evaluation target. Both datasets are 6.3y windows where vol-regime
  family ALREADY clears Sharpe-edge-to-bench (iter 013 7/7 gates).
  The "real" mission of beating Pepperstone-cost-realistic XAUUSD
  buy-hold is largely solved on those windows; gld_long was always
  the ambitious cross-validation target.

### GS-2 — Track B (Inter ETF) FX cost cliff at > ~15 trades/year
*(iter 001 cost-model meta-finding)*

The Inter Internacional cost model (100 bps FX RT per trade) is
**~12× larger per turn** than Pepperstone's CFD spread (8 bps). Above
~15 trades/yr, FX RT consumes the entire buy-hold CAGR:

| trades/yr | annual FX cost (bps) |
|---|---|
| 5  | 50  |
| 10 | 100 |
| **15** | **150** ← break-even with ~13% CAGR gold buy-hold |
| 20 | 200 |
| 25 | 250 |
| 50 | 500 |

**Closes**: any strategy with `mean_turnover > 25 trades/year` is
**INELIGIBLE for Track B** (must be tagged Track A only). Strategies
with `mean_turnover ≤ 12 trades/year` are Track-B viable; in between
is marginal and should be reported with caveats.

**Implication for the strategy menu in BASE_MEMORY**:
- Most short-hold MR/breakout candidates (#5-8, #11) → Track A only
- Long-hold candidates (#9 TSM 12-1, #15 DXY signal, #18 pre-FOMC drift)
  → Track-B viable

### GS-15 — DXY 200d-MA-slope falling regime gate on FRED DTWEXBGS does NOT bridge gold's drift on day/swing horizon AND confirms GS-14 same-macro-clock corollary at the macro-generic level
*(iter 015 — `iterations/015-2026-04-26-1455-dxy-sma-slope-trend-gate/`)*

The slope-grammar pivot from GS-5's level-vs-MA closure (long gold when
`SMA_200(DXY)[t] < SMA_200(DXY)[t - 20]` — DXY's 200d MA in 1-month
falling trend) was hypothesized to break GS-14's "rate-cycle and
vol-cycle ride the same clock" by introducing FX-trend as a
fundamentally different cycle. The empirical result is the loop's
**third independent measurement of pairwise ρ ≈ +0.5 between trend-
style macro/regime signals on gld_long** — closing the macro-generic
same-clock corollary.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

| dataset | Sharpe | bench Sh | Δ | CAGR | bench CAGR | MDD | bench MDD | gates | mean hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gld_long (21.4y, mixed regime) | +0.240 | +0.6844 | **−0.444** | +2.09% | +11.32% | **50.72%** | 45.56% (✗ +0.12pp) | 4/7 | 121.3 d |
| xauusd_real (6.3y, bull only)  | +0.323 | +1.0382 | **−0.716** | +3.39% | +19.93% | 20.69% | 20.36% | 4/7 | 121.2 d |
| xauusd_intraday (6.3y, 1h)     | +0.356 | +1.1028 | **−0.747** | +3.63% | +20.20% | 24.69% | 24.42% | 4/7 | 113.1 d |

DSR p-values: 0.733 / 0.628 / 0.523 with cumulative_n_trials=15. G6
Bootstrap 0/3 (CI lower bound negative). G3 Walk-Forward 0/3 (too
sparse). G7 cross-lib EXACT 0.00e+00 pp parity 3/3 (numpy reference
matches pandas bit-for-bit on cumsum-based 200d MA). Score 17/100 = FAIL.

**Pre-validation 3/3 PASS** — signal IS active and directional:
| dataset | p_active | μ active bps/bar | flips |
|---|---:|---:|---:|
| gld_long          | 0.360 | +3.700 | 31 |
| xauusd_real       | 0.428 | +3.958 | 11 |
| xauusd_intraday   | 0.428 | +0.208 | 11 |

**IC-7 ρ correlation map** (the loop's main finding this iter):

| dataset | vs iter 003 (RSI MR + SMA200) | vs iter 011 (vol-regime σ_60<σ_252) | vs iter 013 (vol-regime + SMA200) | vs iter 014 (DFII10 falling) |
|---|---:|---:|---:|---:|
| gld_long          | **+0.170** | +0.433 | +0.429 | **+0.513** |
| xauusd_real       | +0.218 | +0.363 | +0.343 | +0.382 |
| xauusd_intraday   | **−0.065** | +0.275 | +0.267 | +0.377 |

**Per-trade economics (cost-favorable but n_trades-starved)**:

| dataset | n_trades | gross/trade (bps) | cost/trade (bps) | net/trade (bps) |
|---|---:|---:|---:|---:|
| gld_long          | 16 | +533.9 | +172.2 | +361.7 |
| xauusd_real       |  6 | +557.9 | +130.0 | +427.9 |
| xauusd_intraday   |  6 | +554.2 | +103.1 | +451.1 |

Per-trade gross +534-558 bps is the **highest seen in any iter** —
when the gate fires, the captured rally averages ~5%. The problem is
*frequency*: only 6 trades on xauusd's 6.3y means DSR's deflator at
n_trials=15 cannot reach significance even at +0.36 Sharpe.

**Why structural** (not parameter-tweakable):

1. **GS-14 corollary CONFIRMED at macro-generic level**. Iter 014
   already showed DFII10-trend ↔ vol-regime ρ=+0.519 on gld_long. Iter
   015 adds DXY-trend ↔ DFII10 ρ=+0.513 on gld_long. **Three streams
   from three "different families" (vol-regime, real-rates, FX-trend)
   all correlate at ρ ≈ +0.5 pairwise on the long window.** The
   underlying mechanism is a single multi-month real-rate / macro-cycle
   clock that paces all three: real-rates fall → gold rallies → gold-
   vol contracts AND USD weakens → all three flag-on simultaneously
   during macro-easing phases. Any future quarterly+ trend-style macro
   overlay built on rates / FX / vol will share this clock.

2. **Slope-grammar smoothing kills reactivity at the swing horizon**.
   200d-MA + 20d-slope means the gate flips ~1× every 12-18 months.
   The strategy has 5-10 trades over a 6.3y dataset → DSR n=6 is
   structurally too small. Smaller windows (50d/5d, 100d/10d) make
   the slope-flag indistinguishable from noise (closes IC-8 on
   parameter sweeps of this grammar).

3. **gld_long MDD breaches ceiling by 0.12 pp (50.72% vs 50.60%)**.
   The hypothesized "filter USD-up drawdown phases" mechanism FAILS on
   the long window — the strategy holds through gold's 2013-2018
   drawdown because DXY's 200d MA was not consistently rising during
   that period (it had multiple "USD pause" phases that turned the
   gate back on). The gate is too coarse to distinguish "USD strong
   trend" from "USD trendless".

4. **Off-time opportunity cost dominates filtered MDD savings**. The
   strategy is "off" 57-64% of bars; gold's bull regimes are
   concentrated, so missing 60% of bars collapses CAGR (2-4%) far
   below buy-hold's drift. The CAGR gap of ~10-17 percentage points
   per year is structurally larger than any reasonable MDD savings.

**Closes**:
- DXY-MA-slope filter at sma_window=200, slope_lookback ∈ {5, 10, 20,
  30, 60} on FRED DTWEXBGS for gold day/swing — IC-8 closure for the
  parameter family because the binding constraint (signal-flips ~5-10
  per window → DSR drained) is structural to the smoothing mechanism
- IC-7 composition `iter_015 × iter_011/013/014` on gld_long — ρ at
  +0.43 to +0.51 exceeds the productive band (sister 045/046 best at
  ρ=0.41 with both bases STRONG-tier; both here are MARGINAL or worse)
- BASE_MEMORY direction #1 "DXY LEVEL regime gate" in slope grammar
- The macro-generic same-clock corollary at the gld_long single-stream
  level: any quarterly+ macro-trend signal will hit Sharpe ≈ +0.55
  pairwise-ρ ≈ +0.5 vs existing macro-trend streams on gld_long

**Does NOT close**:
- DXY-derived signals at *non-trend* grammars: positioning extremes
  (CFTC COT) and z-score mean-reversion at MUCH shorter horizons (1-3d)
  are different signal-construction families, NOT closed by GS-15
- IC-7 composition involving iter 003 (RSI MR + SMA200) which sits
  at ρ = +0.17 / +0.22 / **−0.07** vs iter 015 — the most-orthogonal-
  yet pair the loop has found. **iter 016 priority #1: IC-7(003+015)
  on xauusd_intraday at ρ ≈ 0** (cheapest cross-orthogonality test)
- DXY at much SHORTER horizons (slope_lookback=3-5 days) — likely
  noise but not formally tested
- Different macro families that are *responses to* the macro clock
  rather than *on* it: CFTC COT (positioning extremes weekly cadence,
  CFTC legacy reports back to 1986) is the next structural candidate

**How to escape** (informs iter 016+):

1. **IC-7 composition iter_003 + iter_015 on xauusd_intraday at ρ ≈ 0**
   — directly tests whether IC-7 unlocks anything when ρ is near zero
   on a real pair from this loop's data. Cheapest direction (no new
   data fetch). Even if combined Sharpe is bounded by √(S_A² + S_B²)
   ≈ 0.43 below intraday bench 1.10, the test informs every future
   composition decision.
2. **CFTC COT non-comm net longs gold** — positioning is RESPONSE to
   macro, not on the macro clock itself. Weekly cadence; CFTC legacy
   reports back to 1986 → full gld_long coverage. Cordero (2017) "What
   COT Tells Us About Gold" + de Roon-Nijman-Veld (2000) *J Finance*
   "Hedging Pressure Effects in Futures Markets" + `[trading_systems_methods,
   p.700+]`. Higher infra cost but only direction with structural
   prior to break gld_long ceiling at single-stream level.

### GS-16 — IC-7 composition cannot lift DSR within the existing 15-stream catalog; the iter 015 "ρ = −0.07 on xauusd_intraday" claim was a frequency-mismatch artifact

*(iter 016 — `iterations/016-2026-04-26-1847-ic7-rsi2sma200-dxytrend/`)*

Composing iter 003 (`connors_rsi2_sma200_filter`, RSI(2)+SMA(200) MR)
with iter 015 (`dxy_sma_slope_falling_200_20_long_only`) at full-sample
Markowitz tangency weights — the BASE_MEMORY-priority-1 IC-7 candidate
chosen specifically because iter 015's `ic7_diagnostic` reported
ρ = −0.07 on `xauusd_intraday`, the lowest |ρ| ever measured in this
loop — produced a NEAR_FAIL/35 result and triggered ALL THREE
pre-committed kill criteria:

| dataset | observed ρ (this iter) | iter 015 diagnostic ρ | combined Sharpe (Δ vs bench) | DSR p (n=16) | gates | mean hold |
|---|---|---|---|---|---|---|
| gld_long | +0.170 | +0.43 (vs iter 011!) ↔ this iter's +0.17 vs iter 003 | +0.355 (Δ −0.329) | 0.5619 | 4/7 | 43.4d |
| xauusd_real | +0.218 | +0.43 vs iter 011 ↔ +0.22 vs iter 003 | +0.346 (Δ −0.692) | 0.8113 | 4/7 | 38.0d |
| **xauusd_intraday** (PRIMARY) | **+0.220** | **−0.07 (claimed)** | +0.381 (Δ −0.722) | 0.7844 | 4/7 | 37.9d |

**Why the −0.07 figure was wrong**: iter 015's `ic7_diagnostic` (in
`run_backtest.py::ic7_diagnostic`) joined iter 015's 32195-bar 1h
returns directly with iter 003's 1700-bar daily-resampled returns via
inner-join on the timestamp index, then computed Pearson correlation
on the resulting (sparse, frequency-mismatched) overlap. Since iter
003's daily-resampled intraday returns are stored at midnight (00:00:00)
timestamps, but iter 015's hourly returns span 24 hour-of-day stamps,
the inner-join only retained one timestamp per day at most — and the
resulting per-day "correlation" picked up frequency-aliasing noise that
appeared as ρ ≈ 0.

When BOTH series are aggregated to consistent daily granularity
(iter 015's 1h returns first summed via `resample("D").sum()` keeping
only days with ≥ 1 input bar), ρ on xauusd_intraday is **+0.220** —
identical to xauusd_real's +0.218 and consistent with the macro-generic
same-clock floor (GS-15) of ρ ≈ +0.17-0.50.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

The combined Sharpe stayed within the √(S_A² + S_B²) ≈ 0.41-0.42
envelope on all 3 datasets, exactly as IC-3 predicts. Tangency weights
all stayed in positive corner (no shorting); MR base (iter 003) got
0.60-0.78 weight on every dataset due to its lower σ.

DSR p-values were WORSE than the individual streams' values for
intraday primary — composition pulled p from 0.523 (iter 015 alone) to
0.784, because cumulative_n_trials at 16 deflated harder than the tiny
ρ ≈ +0.22 diversification benefit (`(1 − 0.22²)^0.5 ≈ 0.976`, only
2.4% uplift).

**Why structural** (not parameter-tweakable):

1. **Same macro clock**: GS-14/GS-15 already established that
   single-stream gold strategies in price/macro/FX families share
   ρ ≈ +0.5 within and ≈ +0.17 across families. There is **no
   sub-0.20 pair** in the existing 15-stream inventory at consistent
   frequency. Mixing iter 003 (MR family) with iter 015 (USD-trend
   family) is the most cross-family pairing available, and it sits
   at +0.17-0.22.
2. **Sharpe ceiling**: individual stream Sharpes max at ~0.55 on
   gld_long and ~0.36 on intraday (iter 015 best). Any 2-stream
   tangency combines to S_combined ≤ √(S_A² + S_B²) at orthogonal
   limit; with realistic ρ ≈ +0.22 the Markowitz-optimal combined
   Sharpe is < 0.42 — **structurally below the +1.20 needed to clear
   intraday-bench-edge** (xauusd_intraday bench Sh = 1.10 + 0.10 edge).
3. **DSR deflator binding**: cumulative_n_trials = 16 means the DSR
   threshold has tightened to roughly +0.65 raw Sharpe (per López de
   Prado's deflator). Combined Sharpe of 0.38 is well below; further
   composition with current catalog cannot escape this ceiling no
   matter the weighting scheme.

**Closes**: any further IC-7 composition attempt within the existing
15-stream catalog of gold strategies (iters 001-015). Includes:
003+014, 011+014, 011+015, 013+014, 013+015, 003+011 (already iter 012),
003+013 (variant), and any 50/50 or Markowitz combinations of pairs
from {001, 003, 010, 011, 013, 014, 015}. All share the macro-clock-floor
ρ ≥ +0.17 and have S < 0.55 individually.

**Closes also**: the "highest-orthogonality intraday pair" claim from
iter 015 BASE_MEMORY entry. Future iters that compute IC-7 diagnostic
correlations MUST aggregate to consistent frequency before joining.

**Does NOT close**:
- IC-7 with a fundamentally orthogonal NEW stream (CFTC COT positioning,
  options-implied vol/skew, or microstructure on sub-1h bars). Those
  are different families that haven't been tested yet; the closure
  applies only to the current 15-stream catalog.

**How to escape** (informs iter 017+):

1. **CFTC COT non-comm net longs gold (PROMOTED to PRIORITY 1)**.
   Positioning is RESPONSE to macro, not on the macro clock — provides
   genuine structural orthogonality. Weekly cadence; CFTC legacy reports
   back to 1986 (full gld_long coverage). Single signal: long when
   non-comm net long z-score < threshold (commercials extreme short →
   non-comm overweight → mean-revert toward neutral). Cordero 2017 +
   de Roon-Nijman-Veld 2000 *J Finance* + `[trading_systems_methods,
   p.700+]`.
2. **Options-implied: CME GVZ regime gate or risk-reversal skew**
   (FRED `GVZCLS` series back to 2008). Different family entirely;
   tests whether implied-vol regime is orthogonal to realized-vol
   regime (iter 011's σ_60/σ_252 family).
3. **Microstructure / time-of-day intraday** on 30m / 15m / 1m bars
   (requires a "data infra" iter to fetch from cTrader Open API first;
   credentials in `.env`, bootstrap script wired). Defer until earlier
   priorities exhaust the daily-frequency search space.

**Honesty correction propagated to BASE_MEMORY**: the iter 015 entry's
"highest-orthogonality found: vs iter 003 ρ=+0.17/+0.22/−0.07" is
amended to "+0.17/+0.22/+0.22" (consistent-frequency re-measurement).

---

## Anti-patterns to watch for in gold day/swing

These are NOT yet empirically closed but have strong theoretical reasons
to be likely-dead-end. **DO NOT auto-close** without empirical iter,
but include explicit pre-val:

- **Overnight gap as entry signal** — gold gaps Sun open with 2-day weekend
  news; overnight strategies face execution gap risk + 3× swap on Friday hold
- **Bollinger band z > 3σ entries** — gold has fat-tailed daily returns;
  3σ entries fire only ~5×/yr, insufficient for DSR statistical power on
  6-year datasets (xauusd_real / xauusd_intraday)
- **VIX as primary gold signal** — gold-VIX correlation is positive ONLY
  during equity-stress regimes (~10-15% of bars); using VIX as primary
  gold signal IS NOT the same as IC-1 (vol-target absorption) but suffers
  similar low-coverage issue
- **Daily mean-reversion on gold trend regimes** — 2001-2011 and 2018-2024
  were strong gold uptrends; pure MR strategies lose ~50% premium during
  these regimes; need regime-aware MR-vs-trend switch (which compounds
  parameters → DSR cost)
- **Single-leg leverage > 2×** — gold MDD historically 45% (2011 peak →
  2015 trough, −45%); 2× lev = 90% MDD = liquidation. Day/swing strategies
  with persistent positions need lev cap ≤ 1.5× to respect MDD ceiling

### GS-17 — CFTC COT Briese / Ruggiero canonical thresholds on gold (NEAR_FAIL, 28/100) — but family is structurally orthogonal
*(iter 017 — `iterations/017-2026-04-26-1610-cftc-cot-briese-ruggiero/`)*

Briese COT Index (156-week stochastic of net longs) + Ruggiero
canonical rule (Comm > 70 AND Small < 30 entry, exit at neutral 50,
lag 1 week) on CFTC Legacy Futures-Only Gold COMEX (code 088691, weekly
1986-01-15 → 2026-04-21, 1913 records).

**Empirical evidence** (Track A, Pepperstone CFD net of costs):

| dataset | Sharpe | bench Sh | Δ | CAGR | bench CAGR | MDD | gates |
|---|---:|---:|---:|---:|---:|---:|---:|
| gld_long PRIMARY (21.4y) | +0.137 | +0.684 | **−0.547** | +0.83% | +11.32% | 31.8% (vs 45.6%) | 4/7 |
| xauusd_real CORROB (6.3y) | +0.310 | +1.038 | −0.728 | +1.51% | +19.93% | 13.0% (vs 20.4%) | 3/7 |

DSR p 0.732 / 0.675 (n_trials = 17, annualized-Sharpe formula).
Bootstrap 99.9% CI low −0.512 / −1.104. WF 5/8 / 2/8.
38 / 9 trades; mean hold 28.3 / 29.3 trading days (PASS medium_swing).
Cross-lib numpy reference: exact CAGR match.
Pre-committed kill criterion #2 (primary Sharpe ≥ 0.30) FIRES at 0.137.

**Why structural** (not parameter-tweakable at canonical thresholds):

- Trade flow is too sparse: ~1.8 round-trip trades per year on
  gld_long. Most years have 0-1 trade. The signal is not frequent
  enough to compound the underlying gold drift, even when individual
  trades are profitable on average.
- Walk-forward windows show clear regime dependence: the strategy
  works when commercials are contrarian to crowd (1992-2008,
  2015-2019), fails when commercials chase a top (2010-2014, when
  hedgers reloaded long into the 2011 peak).
- MDD reduction (31.8% vs bench 45.6%) is genuinely the only
  structural advantage. The signal sidesteps the worst gold
  drawdowns by being flat ~80% of the time, but at the cost of
  also missing the bullish drift.
- Re-tuning thresholds (e.g., 75/25 or 80/20) would burn
  cumulative_n_trials (IC-8) without bridging the Δ −0.55 Sharpe gap.

**★ The high-value finding (separate from the strategy outcome)**:

ρ at consistent daily granularity (GS-16 process correction):

| pair | ρ on gld_long (5384 bars) | ρ on xauusd_real (1700 bars) |
|---|---:|---:|
| iter 017 vs iter 003 RSI(2)+SMA(200) MR | **+0.003** | **−0.0002** |
| iter 017 vs iter 011 σ_60<σ_252 vol-regime | +0.237 | +0.292 |
| iter 017 vs iter 015 DXY-SMA-slope trend | +0.100 | +0.050 |

This is the **first sub-0.20 ρ pair** the gold loop has produced in 17
iterations of catalog measurement. The ρ ≈ 0 against iter 003 (RSI
mean-reversion) confirms the structural prior: positioning is RESPONSE
to macro / price, not on the macro / price clock. **GS-16's "no sub-0.20
ρ pair exists in iters 001-015 catalog" is now superseded by GS-17.**

**Closes (within COT-positioning family)**:

- Canonical Briese / Ruggiero parameter set: Comm > 70 AND Small < 30,
  exit 50, lag 1 week, stochastic window 156 weeks. Closed at the
  ~0.137 / 0.31 Sharpe ceiling under pep_cfd costs.
- Single-stream COT as path to Sharpe > bench + 0.10 on gld_long.
  Sparse trade flow caps Sharpe regardless of threshold tuning.

**Does NOT close (open paths in same family)**:

1. **COT z-score variant** (priority 1 for iter 018): rolling 156w z
   of (commercials_NL − smalltrader_NL); enter long when z < −1.0;
   exit z > 0 OR 30d timeout. Z compresses tails less than the
   stochastic; canonical thresholds may rediscover trade flow.
2. **Disaggregated COT (DCOT) money-manager net longs** — post-2009
   only (xauusd_real becomes primary); tighter "smart money"
   definition than legacy commercials.
3. **COT + price-momentum overlay** — gate Ruggiero entries by
   12-3-1 month momentum (only enter when COT extreme AND price
   already turning). IC-6 pre-val mandatory.
4. **IC-7 composition iter 003 + iter 017** at confirmed ρ ≈ 0.003.
   Combined Sharpe ceiling √(0.30² + 0.137²) ≈ 0.33 on gld_long is
   below bench + 0.10, but DSR uplift is now meaningful at near-zero
   correlation. Worth running once a *stronger* positioning-derived
   component exists (priority 2 for iter 019+).

**Process notes (for future iters)**:

- DSR formula must use ANNUALIZED Sharpe consistently in both SR0 and
  var(SR). Mixed annualized/per-period units produce spurious near-zero
  p-values (a Sharpe 0.137 yielding p = 3 e-16 is a smell test failure).
  Detected and fixed mid-iter; final p = 0.732 dimensionally consistent.
- IC-7 ρ diagnostics must be computed at consistent daily granularity
  (GS-16) — confirmed reproducibly across 5384-bar gld_long and
  1700-bar xauusd_real.
- Pre-committed kill criteria + IC-8 single-cfg discipline preserved
  through structural-finding excitement. The orthogonality discovery
  does NOT override kill #2; iter is honestly NEAR_FAIL.


### GS-18 — Rolling 156-week z-score of (NL_comm − NL_small) on CFTC Legacy Futures-Only Gold lifts the canonical Briese stochastic but the COT-positioning STANDALONE family ceiling on gold plateaus at Sh ≈ 0.35 across both transforms

*(iter 018 — `iterations/018-2026-04-26-1628-cot-zscore-variant/`)*

Iter 018 tested the priority-1 follow-up to GS-17: the same data
(CFTC code 088691, Legacy weekly, 1986+) and the same window (156w)
but with the tail-clipped Briese stochastic replaced by an unbounded
Gaussian z-score on the differential `NL_comm − NL_small`. The
hypothesis was that the stochastic's min-max compression ceiling on
extreme positioning weeks was the binding constraint; an unbounded
z preserves tail magnitude.

**Empirical evidence** (Track A net of Pepperstone CFD costs):

| dataset | Sharpe | bench Sh | Δ | CAGR | bench CAGR | MDD | bench MDD | n_trades | mean hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gld_long (PRIMARY, 21.4y)             | **+0.352** | +0.684 | −0.33 | +2.92% | +11.32% | **25.3%** | 45.6% | 46 | 28.4d |
| xauusd_real (CORROBORATING, 6.3y)     | +0.289     | +1.038 | −0.75 | +1.53% | +19.93% | 16.0%     | 20.4% | 11 | 30.0d |

Gates: gld_long **5/7** (G1 N/A, G3 WF 7/8 ↑, G4 OOS+, G5 FWD+, G7
crosslib OK; G2 DSR p=0.354 fail, G6 boot −0.348 fail). xauusd_real 3/7
(G6 boot −0.80; thin-history instability). Score 35/100 = NEAR_FAIL.

**Key structural finding** (compare to GS-17 canonical Briese):

| transform | gld_long Sh | xauusd_real Sh | gld_long MDD | n_trades gld | mean hold gld |
|---|---:|---:|---:|---:|---:|
| Briese stochastic (iter 017, GS-17) | +0.137 | +0.310 | 31.8% | 38 | 28.3 d |
| Gaussian z-score (iter 018, GS-18)  | **+0.352 (+0.215)** | +0.289 | **25.3% (−6.5pp)** | 46 | 28.4 d |

The z-score variant lifts gld_long Sharpe by **+0.215** (≈2.5×) and
reduces MDD by 6.5pp. xauusd_real is essentially flat (+0.310 →
+0.289). This validates the hypothesis that Briese's tail-clipping
*is* a binding constraint on the long-history dataset where positioning
extremes wave large enough to saturate the 156w max — but xauusd_real's
6.3y history doesn't span enough cycles for this to matter.

**Why structural** (not parameter-tweakable):

The +0.215 lift was meaningful but does not bridge the buy-hold-Δ gap
(−0.43 on gld_long). With 24% of bars in long position and gold's
+11.3% annualized buy-hold drift, selective long-only entries pay
opportunity cost in basis points per year that the COT-positioning
information advantage cannot overcome at any single-stream transform.
**Across BOTH the Briese stochastic AND the Gaussian z-score, the
standalone family ceiling sits at Sh ≈ 0.35 on gold's longest dataset**
— a 2-transform plateau established at independent measurements with
the same DSR-cumulative discipline.

Tuning the entry threshold further (z > +1.5, +2.0, ...) or the
window (104w, 208w) trades trade-count for selectivity along an
already-saturated dimension; IC-4 modulation closure applies.

**Closes (within COT-positioning STANDALONE family)**:

- COT z-score with canonical 156w window (any z_entry, z_exit thresholds)
  as path to Sharpe > bench + 0.10 on gld_long.
- Standalone single-stream COT-positioning approach broadly: both the
  Briese stochastic AND the Gaussian z-score reach the same ~0.35
  Sharpe ceiling. Further single-transform variants (tanh, percentile-
  rank, Yeo-Johnson, etc.) are IC-4 modulation that will plateau at
  the same ceiling.

**Does NOT close (open paths)**:

1. **IC-7 003 + 018 Markowitz composition** at confirmed ρ +0.013
   (gld_long, n=5384) / +0.004 (xauusd_real, n=1700). Both standalone
   Sh positive (003: +0.30 / +0.19, 018: +0.35 / +0.29). Tangency
   weights w ∝ Σ⁻¹ μ. Combined ceiling √(0.30² + 0.35²) ≈ 0.46 on
   gld_long. **First loop iteration with both standalone streams
   positive AND ρ < 0.05** — is the most thoroughly validated 2-stream
   IC-7 candidate in the loop's history. Citation: `[advances_fin_ml,
   p.222-223]` (DSR uplift formula at low ρ).
2. **Disaggregated COT (DCOT) money-manager net longs** — post-2009
   only (xauusd_real becomes primary; gld_long downgrades to
   corroborating due to short overlap). Money-manager bucket isolates
   speculative flow from producer hedging that contaminates the legacy
   commercials category. Different distribution may exit the +0.35
   plateau if legacy "commercials" was the binding pool.
3. **COT + price-momentum overlay** — gate canonical Briese 70/30
   entries by 12-3-1 month price momentum (only enter when COT extreme
   AND price already turning). Different mechanism (entry filter not
   signal transform); IC-6 pre-val mandatory.
4. **3-stream IC-7 003 + 011 + 018 Markowitz** — defer to iter 020+;
   adds vol-regime as 3rd low-ρ stream once 2-stream uplift confirmed.
   ρ pairs: 011-018 = +0.27, 003-018 = +0.013, 003-011 already measured.

**GS-17 orthogonality replicated at 2nd independent measurement**:

| ref iter | gld_long ρ (iter 017) | gld_long ρ (iter 018) | xauusd_real ρ (iter 017) | xauusd_real ρ (iter 018) |
|---|---:|---:|---:|---:|
| iter 003 RSI MR | +0.003 | **+0.013** | −0.0002 | **+0.004** |

The COT-positioning family vs RSI-MR ρ is sub-0.02 on BOTH datasets
at BOTH the canonical Briese transform AND the Gaussian z-score
transform. This survives any future "freq-mismatch artifact" concern
(GS-16 process correction). **The RSI-MR + COT-positioning pair is
the most thoroughly empirically validated low-ρ 2-stream candidate in
the loop's history**; it's the path of least conjecture for the next
IC-7 composition test.

**Process notes**:

- IC-8 single-cfg discipline preserved (cumulative_n_trials 17 → 18).
- Hold-time bucket gate passed cleanly (28.4d, 30.0d both inside
  medium_swing [10, 30]). The 30-day cap on xauusd_real binds at
  exactly the bucket ceiling — future iter could test a 21-day cap
  to keep clearance, but mean-hold parametric robustness check is a
  modulation axis (IC-4 closure). Defer.
- iter 018 reused iter 017's `apply_costs`, `compute_metrics`,
  `deflated_sharpe_p_value`, `bootstrap_ci_low`, `walk_forward_split`,
  `cross_lib_check`, `load_cot`, `load_prices` verbatim — well-tested,
  no dimensional inconsistency carried forward. The DSR formula
  correction documented in GS-17 is the version in production.

### GS-19 — IC-7 Markowitz tangency 003 + 018 on gold validates closed-form ceiling but DSR-deflator wall holds at n_trials=19 — closes the 2-stream IC-7 path on the existing iter 001-018 stream catalog

**Iter:** `019-2026-04-26-1648-ic7-rsi2sma200-cotzscore`
**Closes:** 2-stream IC-7 path on gold within the existing iter 001-018 catalog. Any further pair has S_combined ≤ √(2)·max(S_standalone) ≤ √(2)·0.55 ≈ 0.78 = bench+0.10 (the WINNER threshold), and the Bonferroni-deflated DSR null SR₀(n_trials) deflates this further as n_trials grows — so even the analytic ceiling never clears DSR<0.05 within the existing stream catalog.

**Pre-committed setup**:
- Streams: A = iter 003 (RSI(2)+SMA(200) MR, daily, Sh +0.299/+0.193 gld/xauusd, hold ~4d), B = iter 018 (rolling-156w z-score COT positioning, daily, Sh +0.352/+0.289, hold ~28d).
- Both component returns pre-deducted Pepperstone CFD costs (8 bps spread RT + −1 bps/cal-night swap); composition adds zero turnover (`[advances_fin_ml, p.31-34]`).
- Datasets: gld_long PRIMARY (5 384 daily bars) + xauusd_real CORROBORATING (1 700 bars). xauusd_intraday NOT AVAILABLE because iter 018's `run_backtest.py` did not run on intraday (would require re-running iter 018 with 1h pipeline first).
- Method: full-sample Markowitz tangency `w ∝ Σ⁻¹μ` with corner-clamp fallback if either weight goes negative (clamps to (1.0, 0.0) or (0.0, 1.0)).
- IC-8 honored: 1 cfg, n_trials cumulative 18 → 19.
- IC-6 pre-val: rolling-60d Pearson ρ exceedance check with limit `exceed_frac(|ρ|>0.30) > 20% → ABORT`. Static ρ from iter 018 was +0.013/+0.004; rolling check is the safety augment.

**Key results (Track A pep_cfd net, gld_long PRIMARY)**:
- Combined Sharpe **+0.4584** (Δ −0.226 vs bench 0.684; vs analytic ceiling √(0.299² + 0.352²) = 0.4598 → **99.7% of theoretical max**, the loop's first numerical confirmation of `[advances_fin_ml, p.222-223]` 2-stream tangency formula on gold).
- CAGR +1.94% (Δ −9.38 vs 11.32% bench; Δ −7.12 vs 0.8×bench=9.06% floor → fails CAGR floor by 7.12 pp).
- **MDD 9.56%** (Δ −36.0 pp vs bench 45.6% — **the loop's lowest MDD ever on gld_long**, compression factor 4.77×). xauusd_real MDD 8.33% (Δ −12.0 pp vs bench 20.4%, compression 2.45×). Combined positions inherit the full diversification benefit of ρ ≈ 0 streams; from a risk-of-loss perspective, this composition is exceptional even though absolute returns lag.
- Markowitz tangency weights: w_003 = 0.6447, w_018 = 0.3553 on gld_long (analytic prediction `μ_003/σ_003² : μ_018/σ_018² = (μ/σ²)_A : (μ/σ²)_B` matches exactly). On xauusd_real: w_003 = 0.5287, w_018 = 0.4713. **No weight clamp required on either dataset** — well-conditioned tangency.
- 7-gate battery on gld_long: G1 PASS by IC-8 convention, G2 FAIL (DSR p=0.4055 vs 0.05), G3 PASS (WF 6+/8), G4 PASS (OOS Sharpe>0), G5 PASS (FWD post-2022 Sharpe>0), G6 PASS (bootstrap 99.9% CI low > 0), G7 PASS (cross-lib CAGR ±3pp). **5/7 ≥ primary threshold 5** → primary gate counts pass.
- 7-gate battery on xauusd_real: 4/7 (passes primary threshold but fails G2 with p=0.836; iter 018 standalone showed similar DSR drag from short window 1700 bars).
- **IC-6 rolling-ρ pre-val**: gld_long 1.5% exceed-frac (32/2191 valid bars > |0.30|), xauusd_real 0.0% (0/912). **PASS by 18+ pp on both datasets** → orthogonality is regime-stable across 21+ years of gold cycles. **3rd independent confirmation** of GS-17/18 finding (iter 017 +0.003 / iter 018 +0.013 / iter 019 rolling 1.5% exceedance).

**Per-stream component diagnostics (joined index, gld_long)**:
- iter 003 standalone (on joined index, n=2191): Sh +0.299, σ_per_bar = small-MR characteristic.
- iter 018 standalone (on joined index, n=2191): Sh +0.352, σ_per_bar slightly larger (more days exposed, longer holds).
- Static joined-sample ρ: **+0.0134** on gld_long, **+0.0043** on xauusd_real.

**Score breakdown (v2 scoring, rules_version=2026-04-26-relaxed-r1)**:
1. Sharpe edge: 5/25 — primary not beat (Δ−0.226); corroborating xauusd_real +0.346 > 0 → +5.
2. Gates: 15/25 — primary 5/7 ≥ threshold 5 → +15; corroborating fails G2 → no +5; no legacy 3/3 cross-bonus possible (xauusd_intraday absent).
3. DSR: 0/15 — primary p=0.4055 (n_trials=19); not in any of the rubric tiers (<0.05/<0.10/<0.20).
4. CAGR floor: 0/15 — primary 1.94% < 0.8×11.32% = 9.06%.
5. MDD ceiling: 15/15 — primary 9.56% ≤ 50.6% by 41 pp.
6. Robustness: 0/5 (not computed).
**Total: 35/100 = NEAR_FAIL.**

**Hold-time gate**: weighted-avg `0.6447·3.95 + 0.3553·28.41 = 12.64 d` ∈ medium_swing [10, 30] → **PASS**. Corroborating xauusd_real weighted-avg = 15.30 d, also medium_swing.

**Kill criteria**:
1. Sharpe destruction (combined < max(component) − 0.05): **NO** (combined 0.458 > best 0.352 + 0.05 ✓ — IC-7 lift was real).
2. Markowitz weight collapse (|negative weight| > 0.05): **NO** (no weight clamp on either dataset).
3. **DSR no-progress (combined p > 0.20): YES — KILL FIRED** (gld_long primary p=0.4055; iter 018 standalone was 0.354 → **DSR DEGRADED slightly**). The ρ ≈ 0 uplift `√(1 − ρ²) ≈ 1` did not produce the expected DSR p drop because n_trials=19 vs 18 increment in SR₀(n_trials) baseline absorbed the +0.106 marginal Sharpe lift.
4. Pre-val rolling-ρ violation (`exceed_frac(|ρ_60d|>0.30) > 20%`): **NO** (1.5% on primary, 0.0% on corroborating).

**Why DSR degraded (the structural insight)**:

López de Prado's DSR null mean (Bonferroni-adjusted expected max of n_trials i.i.d. Sharpes under H₀: μ=0) is

```
SR₀(n_trials, T) ≈ (1/√T) · {(1 − γ_E)·Φ⁻¹(1 − 1/n_trials) + γ_E·Φ⁻¹(1 − 1/(n_trials·e))}
                ≈ (1/√T) · √(2 ln n_trials)  for large n_trials
```

where T is the sample size, γ_E ≈ 0.5772 is the Euler-Mascheroni constant. Going from n_trials = 18 (iter 018) to n_trials = 19 (this iter) increases the deflator's `√(2 ln n_trials)` term by `(√(2·ln 19) − √(2·ln 18)) / √(2·ln 18)` ≈ 1.95% — a meaningful step at the 0.05 critical-value boundary. The composition's annualized Sharpe lift was 0.106 absolute (vs iter 018 standalone), but the relevant comparison is with `iter-018 SR₀(18)` vs `iter-019 SR₀(19)`, and the lift was insufficient. **Going to n_trials=20 (iter 020) makes the threshold even stricter; passing G2 requires the composition's annualized Sharpe to exceed roughly 0.78 on gld_long for the n=5384 sample, far above the analytic ceiling of any 2-stream pair in the iter 001-018 catalog.**

This is a **mathematical wall, not a strategy weakness**. The 2-stream IC-7 path is closed for further exploration on this catalog.

**Does NOT close** (still open paths):
- 3-stream IC-7 003+018+015 (priority 1 for iter 020) — adds DXY-MA-slope as 3rd low-ρ stream (ρ vs 003 = +0.22 corrected by GS-16; ρ vs 018 = +0.087/+0.045 from iter 018 measurement). Combined-Sharpe ceiling ≤ √(0.30²+0.35²+0.24²) ≈ 0.52. **Probably still below WINNER even at theoretical max**, but this iteration is the loop's **single most informative test**: if the ceiling holds and DSR p > 0.10 even with 3 streams, the catalog's mathematical exhaustion is confirmed and the loop's structural close is justifiable.
- DCOT money-manager net longs (post-2009) — different speculative bucket, may exit the standalone Sh ≈ 0.35 plateau. xauusd_real becomes natural primary.
- CME GVZ implied-vol regime gate — options-derived family, FRED `GVZCLS` 2008+. Different from realized-vol (iter 011) and positioning (iter 018).
- COT + price-momentum overlay (gate Briese 70/30 entries by 12-3-1 momentum filter).
- gold risk-reversal skew (options) — 25-delta call/put skew gate, options data feed needed.
- GDX/GLD via NEM proxy (NEM 2013-08+).
- BTC-gold risk-off (BTCUSD cached).
- CME futures track A2 (1-2 bps spread vs CFD's 8 bps) — could resurrect cost-dominated dead-ends like iter 007 z-MR 1h (GS-7).
- State-machine-aware pre-val (GS-9 corollary, INFRA).
- Sub-1h microstructure (cTrader fetch infra iter required).

**Citations**:
- `[advances_fin_ml, p.222-223]` — DSR; combined-Sharpe upper bound for 2-asset tangency portfolio.
- `[advances_fin_ml, p.31-34]` — cost realism (composition introduces no new turnover).
- `[short_term_trading_strategies, p.106]` — RSI(2) + SMA(200) MR (iter 003 base).
- `[trading_systems_methods, p.639-640]` — COT z-score positioning (iter 018 base).
- de Roon, Nijman, Veld (2000) *Journal of Finance* — z-score commercial net positioning theoretical anchor.
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046).
- IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50.
- IC-8 sister-loop closure (046) — single cfg per iter.

**Process notes**:
- Iter 019 reused iter 012's composition primitives (`markowitz_tangency_weights`, `compose_returns`, weight-clamp fallback) verbatim, plus iter 016's IC-6 rolling-ρ pre-val pattern. TDD coverage: 13 tests in `test_composition.py` (all pass). Cross-loop reuse: `ai_trade.backtest.validation.dsr.dsr`, `bootstrap.stationary_bootstrap_trades`, `walk_forward.walk_forward_gate`.
- Schema awareness: iter 019 handles both Schema A (`returns_series[ds][cfg_id]`, used by iter 003) and Schema B (`datasets[ds].returns_series`, used by iter 018) loaders. Future iters reading mixed-vintage components should reuse this dual-loader pattern.
- xauusd_intraday absence is structural (iter 018 didn't store intraday returns); not an iter 019 omission. Future composition iters that need intraday will require either re-running iter 018 or a different intraday-capable stream as the second component.

### GS-20 — 3-stream IC-7 Markowitz tangency 003 + 018 + 015 on gold validates the analytical √(Σ Sᵢ²) ceiling at 93.6% but BOTH the DSR-deflator wall AND IC-6 rolling-ρ pre-val on PRIMARY fail — closes the 3-stream IC-7 path on the existing iter 001-019 catalog when the 3rd stream is macro-FX-derived

*(iter 020 — `iterations/020-2026-04-26-1705-3stream-ic7-rsi2-cot-dxytrend/`)*

The 3-stream extension of iter 019's pair (003 RSI(2)+SMA(200) MR + 018
COT z-score) with iter 015 DXY-MA-slope falling 200/20 trend gate as
the 3rd stream, composed at full-sample 3-asset Markowitz tangency
weights (`w ∝ Σ⁻¹μ` with 3×3 covariance), confirms the analytical
combined-Sharpe ceiling `S_combined ≤ √(S²₀₀₃ + S²₀₁₈ + S²₀₁₅) ≈ 0.520`
on gld_long PRIMARY (observed +0.4865 = 93.6% of ceiling). However
**TWO pre-committed kills fired simultaneously**:

- **Kill #3 (DSR no-progress, primary p > 0.20)**: combined p = 0.3646
  at `n_trials = 20` (iter 019 was 19 + this composition increments
  by 1). Marginal improvement vs iter 019's standalone 0.4055 (Δ
  −0.04) but ~7× too high vs G2 threshold p < 0.05. The 3rd-stream
  Sharpe lift from +0.4584 (2-stream) to +0.4865 (3-stream) = +0.028
  is below the Bonferroni deflator growth rate `SR₀(n_trials)` from
  19 → 20. **Same DSR-wall as GS-19**: the existing catalog cannot
  reach DSR < 0.05 within the n_trials regime regardless of stream
  count.
- **Kill #4 (IC-6 rolling-60d ρ pre-val on PRIMARY) — NEW failure
  mode**: the (003, 015) pair on gld_long has |ρ_60d| > 0.30 on 21.9%
  of overlapping bars (459/2093 60d windows) — exceeding the IC-6
  20% limit. Static ρ ≈ +0.17 (post-GS-16 corrected) is the
  AVERAGE; the 21.4-year sample contains substantial regime-driven
  episodes where both signals coincide:
  - 2008 GFC liquidity crisis (gold drawdown → RSI MR entries; DXY
    drop → trend-falling signal active)
  - 2011 sovereign-debt + dollar weakness (same)
  - 2020 COVID-shock March drawdown (same)

  The pair is "low-ρ in expectation but regime-correlated in stress" —
  the worst possible profile for IC-7 because the diversification
  benefit collapses precisely in regimes where it would matter most.

**Empirical evidence** (Track A net of Pepperstone CFD costs, all
component streams pre-deducted):

| dataset | combined Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | DSR p (n=20) | weights 003/018/015 |
|---|---|---|---|---|---|---|
| gld_long (PRIMARY) | **+0.4865** (Δ −0.198) | +2.06% (Δ −9.26) | **10.95%** (Δ −34.6 ↓) | 5/7 | 0.3646 | 0.547/0.320/0.133 |
| xauusd_real (CORROBORATING) | +0.4422 (Δ −0.596) | +1.86% (Δ −18.07) | **9.76%** (loop-best EVER) | 4/7 | 0.7728 | 0.346/0.434/0.220 |

3-stream pairwise ρ on full-sample joined index:

| pair | gld_long static | gld_long 60d \|ρ\|>.30 frac | xauusd_real static | xauusd_real 60d \|ρ\|>.30 frac |
|---|---:|---:|---:|---:|
| (003, 018) | +0.0134 | 1.5% (32/2191) PASS | +0.0043 | 0.0% (0/912) PASS |
| (003, 015) | **+0.1698** | **21.9%** (459/2093) **FAIL** ← kill #4 | +0.2176 | 29.6% (193/653) FAIL |
| (018, 015) | +0.0869 | 18.0% (435/2412) PASS | +0.0450 | 15.3% (105/688) PASS |

**Why structural** (not parameter-tweakable):
1. The (003, 018) pair remains the loop's most thoroughly validated
   low-ρ pair (4th confirmation here). But its 2-stream ceiling is
   `√(S²₀₀₃ + S²₀₁₈) ≈ 0.46` (validated at 99.7% by iter 019), below
   bench + 0.10 = 0.78. **2-stream IC-7 cannot win** within catalog.
2. Adding any 3rd stream that has both low static ρ AND low rolling-ρ
   variance is necessary for IC-7 to reach a higher ceiling. iter 015
   DXY trend has the former but not the latter — the macro-FX clock
   non-stationarily co-triggers with the price-MR regime in stress.
3. The remaining catalog candidates (iter 011 σ-regime, iter 013
   σ-regime+SMA, iter 014 DFII10) all measure pairwise ρ ≥ +0.20 or
   ρ > +0.50 to iter 011/014 — disqualified by IC-7 0.50 upper bound.
4. iter 017 canonical Briese COT and iter 018 z-score are same-family
   (ρ vs each other +0.80) — not IC-7-eligible against each other.

**Closes**: 3-stream IC-7 path on gold within the existing iter 001-019
catalog when the 3rd stream is macro-FX-derived (DXY family). Path of
least resistance for iter 021+ is **structurally NEW mechanism families**
that have not yet been measured against the 003/018 pair:

- **DCOT money-manager net longs (post-2009)** — different positioning
  bucket from iter 018; possibly stationary rolling-ρ.
- **CME GVZ implied-vol regime gate** — options-vol family,
  different from realized-vol (iter 011) and from positioning (iter 018).
- **CME futures track A2 cost re-evaluation** — re-test cost-dominated
  intraday MR (iter 007) at 1-2 bps RT spread.

**Does NOT close**:

- Above 3 priority directions remain candidates.
- 3-stream IC-7 with a 3rd stream that has BOTH stationary rolling-ρ
  AND low static ρ AND standalone Sh ≥ 0.30 — but no such stream is
  visible in iter 001-019 catalog.

**How to escape this dead-end** (informs iter 021+):
1. Test DCOT money-manager AS A STANDALONE first (post-2009 only) to
   measure its standalone Sh AND rolling-ρ vs iter 003. If it passes
   IC-6 with stationary rolling-ρ AND static ρ < 0.20, it is the next
   candidate for 2-stream IC-7 003 + DCOT (replacing iter 018 in iter
   019's pairing) — and possibly 3-stream 003 + 018 + DCOT.
2. Test CME GVZ regime AS A STANDALONE first; same protocol.
3. Concede loop closure if priorities 1-3 also flat-line. The
   mathematical argument (PCBO/DSR with n_trials=21+ requires
   standalone Sh > 0.65 OR an IC-7 pair satisfying both ρ conditions)
   is converging toward the absorbed-book + cached-data envelope being
   exhausted.

**Process correction validated**: IC-6 rolling-ρ pre-val IS NECESSARY,
not just sufficient — static ρ alone (the iter 015 ic7_diagnostic
post-correction) DOES NOT GUARANTEE IC-7 eligibility. Future
composition iters MUST measure rolling-ρ on PRIMARY before composing,
not just static. iter 020 is the first iteration to find a pair where
static ρ is acceptable but rolling-ρ exceeds IC-6 — establishing the
need for both screens.

**Citations**:

- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`;
  multi-asset tangency formula `w ∝ Σ⁻¹μ`; combined-Sharpe upper
  bound `S_combined ≤ √(Σ Sᵢ²)` for orthogonal streams.
- `[advances_fin_ml, p.31-34]` — cost realism (composition adds zero
  turnover; reuses pre-deducted Pepperstone CFD costs).
- `[risk_parity, ch.2]` — multi-asset efficient frontier; tangency
  generalization to N=3.
- `[short_term_trading_strategies, p.106]` — RSI(2) + SMA(200) MR
  base (iter 003 component).
- `[trading_systems_methods, p.639-640]` — COT z-score positioning
  (iter 018 component).
- `[trading_systems_methods, p.13-14]` — vol-regime + macro overlay
  conceptual grounding (iter 015 component family).
- de Roon, Nijman, Veld (2000) *Journal of Finance* — z-score
  commercial net positioning theoretical anchor.
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046).
- IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50/50.
- IC-6 sister-loop closure (014/019) — rolling-ρ pre-val mandatory.
- IC-8 sister-loop closure (046) — single cfg per iter.

**Process notes**:

- Iter 020 reused iter 019's primitives (`markowitz_tangency_weights`,
  `compose_returns`, weight-clamp fallback, IC-6 rolling-ρ pre-val
  pattern), generalized to 3-asset (`markowitz_tangency_weights_3asset`,
  `compose_returns_3stream`). TDD coverage: 12 tests in
  `test_composition.py` (all pass). Cross-loop reuse:
  `ai_trade.backtest.validation.dsr.dsr`,
  `bootstrap.stationary_bootstrap_trades`, `walk_forward.walk_forward_gate`.
- Schema awareness: iter 020 handles both Schema A (iter 003 + iter
  015) and Schema B (iter 018) loaders identical to iter 019.
- 3-asset corner-clamp: if any component yields negative tangency
  weight, drop the most-negative-weight asset and re-solve the
  residual 2-asset corner (TDD-covered). On iter 020 actual data,
  no clamp triggered on either dataset.
- xauusd_intraday absence is structural (iter 018 didn't store
  intraday returns). Iter 020's 3-stream is daily-only by inheritance.

---

### GS-21 — DCOT money-manager net-long contrarian z-score on gold is materially WEAKER than legacy commercials z-score (iter 018) — "isolate speculator flow" hypothesis FALSIFIED on gold contrarian-positioning family

**Iter**: 021-2026-04-26-1800-dcot-mm-zscore. **Tier**: NEAR_FAIL (28/100).

**Configuration tested (single cfg, IC-8)**:

```yaml
cfg_id: dcot_mm_zscore_long_zentry_neg1_zexit_zero_window156w_lag1_max30d
signal: rolling_zscore(MM_NL = m_money_long_all − m_money_short_all, 156w) lagged 1w
entry: LONG when z < −1.0
exit: when z > 0 OR held >= 30 days
data_source: CFTC DCOT Socrata 72hh-3qpy (gold code 088691)
data_range: 2006-06-13 → 2026-04-21 (1 037 weekly rows)
cost_model: 8 bps RT spread + −1 bps/calendar-night swap on long
universe: single_xau (XAUUSD spot for xauusd_real, GLD ETF for gld_long)
declared_primary: gld_long (sliced 2009-06-09+ post-warmup, 16.82y)
declared_corroborating: [xauusd_real]
```

**Result (cost-net, 2 datasets)**:

| dataset | Sharpe (Δ vs sliced bench) | CAGR | MDD (Δ better) | gates | DSR p (n=21) | mean hold |
|---|---|---|---|---|---|---|
| gld_long primary (sliced 2009-06-09→2026-04-15) | **+0.073** (Δ −0.566 vs bench 0.639) | +0.25% | 30.2% (Δ −15.4 ↓) | **4/7** | **0.836** | 27.48 d |
| xauusd_real corroborating (2020-01→2026-04) | +0.277 (Δ −0.761 vs bench 1.038) | +1.38% | 15.6% (Δ −4.8 ↓) | **3/7** | 0.714 | 27.50 d |

**Pre-committed kills check**:

- **Kill #1 (no standalone edge, Sh < +0.20 on primary)**: **FIRED** — gld_long Sh +0.073.
- **Kill #2 (DSR no-progress, p > 0.30 on primary)**: **FIRED** — primary p=0.836 (worst DSR p in loop history at n_trials=21).
- **Kill #3 (IC-7 ineligibility vs iter 003, ρ_static ≥ +0.50 OR rolling-60d exceed ≥ 20%)**: **NOT FIRED** — ρ_static +0.023 (gld), 0.000 (xau); rolling-60d exceed 2.2% (gld), 0.0% (xau). MM contrarian IS structurally orthogonal to iter 003 RSI MR by both metrics. *But* standalone Sh +0.073 is too weak for productive IC-7 composition: combined ceiling √(0.30² + 0.07²) = 0.31 < iter 003 alone +0.30 — marginal lift is zero or negative.

**Closure logic (3 tiers)**:

1. **The hypothesis is FALSIFIED.** DCOT money-manager bucket Sh +0.073 is materially WEAKER than iter 018's legacy commercials bucket +0.352 on gld_long (Δ −0.28 in MM's disfavor). The expected-direction prediction was that isolating speculator flow would EXPOSE a cleaner contrarian edge by removing producer-hedging "noise" — observed effect is the opposite.
2. **Two COT buckets give qualitatively similar signals on gold.** ρ static MM ↔ commercials = +0.853 on gld_long, +0.825 on xauusd_real. Both buckets are reading the same regime indicator (positioning extremes); the structural distinction between buckets is smaller than the distinction between COT family and any non-COT family (e.g., ρ MM ↔ iter 003 = +0.023 only). The COT positioning family ceiling on gold is approximately Sh +0.35 standalone REGARDLESS of bucket choice.
3. **The interpretation: producer-hedging leverage is the edge in legacy commercials, not the noise.** Legacy commercials = producers + merchants + swap dealers + other-reportables-on-the-commercial-side. Producers SHORT physical they own with predictable mechanical bias; isolating the speculator side via DCOT MM REMOVES this leverage and the resultant signal is dominated by random fluctuation. This finding is consistent with classical hedging-pressure theory `[de Roon-Nijman-Veld 2000]` — the "smart money" narrative fits the producer side, not the speculator side, of gold positioning.

**Closes**:

- DCOT money-manager contrarian standalone path on gold (single asset, post-2006 disaggregated bucket, contrarian-to-MM direction).
- The COT-bucket-richness question for the **speculator-isolation** direction: refining the legacy non-commercial bucket into a cleaner speculator subset does NOT exit iter 018's +0.35 single-stream plateau on gold COT positioning.

**Does NOT close**:

- DCOT producer-merchant long-on-extreme-shorting (the *hedger-side mechanical-bias mirror* of this iter): if iter 018's edge comes from producer-hedging leverage as GS-21 suggests, isolating just prod-merc as a long-when-prod-merc-net-short-extreme signal may capture cleaner edge than iter 018's mixed legacy commercials. Different mechanism than this iter — long when prod-merc z<−1 = producers crowded short = bullish mechanical signal. **Data already cached** in `cftc_dcot_gold_weekly.parquet` (`prod_merc_positions_long`, `prod_merc_positions_short`).
- DCOT swap-dealer + other-reportables combined as a "smart money" proxy. Some literature argues swap dealers are the cleanest "lead the market" bucket on gold post-2008. Untested.
- COT positioning × price-momentum overlay (BASE_MEMORY priority 5). Gating canonical Briese 70/30 entries by 12-3-1 momentum filter.
- CME GVZ implied-vol regime gate (BASE_MEMORY priority 1). Options-derived family — structurally distinct from realized-vol (iter 011/013) and from positioning (iter 018/021). FRED `GVZCLS` 2008-06+.
- CME futures track A2 cost-path branch (BASE_MEMORY priority 2). At 1-2 bps RT spread (vs CFD's 8 bps), strategies that died as cost-dominated (iter 007 z-MR) may survive.
- Multi-asset gold_complex universe extension (60% XAU + 30% GDX + 10% XAG). Sister loop's evidence: every winner was multi-asset. Iters 016-021 all single_xau — relaxation freedom unused.
- Cross-asset risk-off, BTC-gold ρ flip, fine-TF microstructure (cTrader fetch needed).

**Process artifacts (reusable)**:

- `data/external/macro/cftc_dcot_gold_weekly.parquet` — 1037 weekly DCOT rows for gold, 2006-06-13 → 2026-04-21. Schema: `m_money_positions_long_all`, `m_money_positions_short_all`, `prod_merc_positions_long`, `prod_merc_positions_short`, `swap_positions_long_all`, `swap__positions_short_all` (NB: API typo with double underscore on swap-short), `other_rept_positions_long`, `other_rept_positions_short`, `nonrept_positions_long_all`, `nonrept_positions_short_all`, `open_interest_all`. Available for any iter that needs DCOT.
- `iterations/021-*/fetch_dcot.py` — adaptable Socrata fetch (CFTC `72hh-3qpy` resource). Modify `KEEP_COLS` for additional DCOT fields if needed.
- `iterations/021-*/run_backtest.py` — `mm_net_long`, `zscore_signal_long_when_z_below` (sign-flipped vs iter 018), `apply_costs`, full 7-gate pipeline. Bucket-swappable: replace `MM_NL` derivation with `prod_merc_long − prod_merc_short` for the priority-3 hedger-mirror iter.
- TDD coverage in `iterations/021-*/test_dcot.py` (6 tests; all green).

**Citations**:

- `[trading_systems_methods, p.640]` — Kaufman: COT positioning extremes contrarian; DCOT money-manager bucket as the speculator proxy.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest.
- de Roon, Nijman, Veld (2000) *Journal of Finance* — "Hedging Pressure Effects in Futures Markets" — the result here is consistent with the paper's prediction that hedger positions (producer side), NOT speculator positions, contain the persistent risk-premium signal.
- CFTC DCOT methodology (https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm) — bucket definitions; gold series earliest 2006-06-13.
- IC-6 / GS-9 — pre-val on PRIMARY at consistent daily granularity (this iter measured both static and rolling).
- IC-8 sister-loop closure (046) — single pre-committed cfg, no grid.

**Process notes**:

- Iter 021 reused iter 018's pipeline (`zscore_signal`, `apply_costs`, `compute_metrics`, `deflated_sharpe_p_value`, `bootstrap_ci_low`, `walk_forward_split`, `cross_lib_check`) with a sign-flipped state machine (`zscore_signal_long_when_z_below`) and the new `mm_net_long` derivation. Only meaningful new logic was the bucket choice + entry direction; the rest is inherited.
- Schema awareness: DCOT API has a quirk — `swap__positions_short_all` (double underscore) is a CFTC schema typo on the source side. Documented inline in `fetch_dcot.py`.
- Primary slice handling (`primary_slice_start: "2009-06-09"`) is the cleanest way to keep the rolling-z warmup honest while still using the ~17y post-DCOT window. Bench is re-measured on the same sliced window for the report's Sharpe-edge accounting (sliced Sh 0.639 vs full-21y 0.684 — slice slightly understates GLD's typical risk-adjusted return because 2004-2008 GFC rally is excluded).


### GS-22 — CBOE GVZ implied-vol z-score gate is a vol-regime family RE-SKIN of σ_60/σ_252 ratio at the position-vector level on gold
*(iter 022 — `iterations/022-2026-04-26-1820-gvz-implied-vol-regime/`)*

**Hypothesis**: Buy gold (long-only) when the CBOE Gold ETF Volatility
Index (GVZ) z-score over a 252-day rolling window drops below −1.0σ;
exit when z reverts above 0 OR after `max_hold_days = 30`. Edge thesis:
when the option market is pricing implied vol at multi-year lows, the
variance-risk-premium argument predicts a high probability of upward IV
mean-reversion, and on gold IV expansions historically coincide with
bullish price moves (stress-driven flight-to-quality, real-rate
compressions). The "forward-looking" framing of options-implied vol was
expected to provide structural orthogonality to the backward-looking
realized-vol regime family (iter 011/013).

**Pre-committed configuration** (single cfg, IC-8):

| param | value |
|---|---|
| z_entry_below | −1.0σ |
| z_exit_above | 0.0σ |
| window_days | 252 (1y rolling) |
| lag_days | 1 (use yesterday's GVZ to avoid lookahead) |
| max_hold_days | 30 (medium_swing upper bound) |
| spread_bps_rt | 8.0 (Pepperstone Track A) |
| swap_bps_per_calendar_night | 1.0 (long-side drag) |
| track | pepperstone_cfd |
| universe | single_xau |
| hold_time_track | medium_swing |
| declared_primary | gld_long (sliced 2009-06-04→2026-04-15, 16.83y) |
| declared_corroborating | xauusd_real (6.29y) |

**Citations**:

- `[volatility_trading, p.32-37]` — Sinclair: implied-vol indices,
  variance-risk-premium framework, low-IV mean-reversion thesis (PRIMARY).
- `[trading_systems_methods, p.13-14]` — Kaufman: vol regime classifier.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 22`.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest.
- CBOE GVZ methodology white paper.
- Bollerslev, Tauchen, Zhou (2009) RFS — VRP-as-predictor framework.
- Web (FRED) — `GVZCLS` series 2008-06-03→2026-04-23 (4 503 daily obs);
  cached to `data/external/macro/gvzcls_daily.parquet`.

**Result table**:

| dataset | Sharpe (Δ vs sliced bench) | CAGR | MDD | gates | DSR p (n=22) | G6 boot CI low | mean hold | track-bound |
|---|---|---|---|---|---|---|---|---|
| gld_long (PRIMARY, 16.83y) | +0.246 (Δ −0.383) | +1.54% | 30.85% | 4/7 | 0.608 | −0.47 fail | 24.6d | medium_swing PASS |
| xauusd_real (CORROBORATING, 6.29y) | +0.333 (Δ −0.706 vs full bench 1.038) | +1.75% | 12.93% | 4/7 | 0.662 | −1.02 fail | 25.9d | medium_swing PASS |

OOS Sharpe (last 30%): gld +0.31 / xau +1.82 (xau OOS notably stronger
than full-sample — strategy improved post-2018 gold regime). FWD
post-2022 +0.35/+0.33. Walk-forward 5/8 windows pass on both. Cross-lib
G7: pandas vs numpy CAGR difference < 1e-6 (clean parity).

**Pre-committed kills check**:

- **Kill #1 (no standalone edge, Sh < +0.20 on primary)**: NOT FIRED —
  gld_long Sh +0.246 just clears the threshold. But materially weak
  vs DSR-deflator requirement (~+0.65 at n=22, ~17y).
- **Kill #2 (DSR no-progress, p > 0.30 on primary)**: **FIRED** —
  primary p = 0.608 (well above threshold).
- **Kill #3 (IC-6 rolling-60d ρ vs iter 011 > 30% on PRIMARY)**:
  **FIRED HARD** — rolling exceed = **59.7%** on gld_long primary
  (vs 30% threshold), nearly double. xauusd_real rolling 45.3%
  (also fail). Static ρ +0.55 on gld, +0.33 on xau.
- **Kill #4 (primary G6 bootstrap 99.9% CI low ≤ 0)**: **FIRED** —
  primary boot CI low = −0.47.

3 of 4 kills fired. The one survivor (Kill #1) only just survives
(Sh +0.246 vs threshold +0.20). The strategy is dead by pre-commitment.

**Closure logic**:

1. **The mechanism is real but small**: GVZ z<−1 entries DO produce
   positive raw Sharpe on both datasets. State-machine generates
   sensible holds (24-26d ∈ medium_swing). OOS slice is materially
   stronger than full-sample on xau (+1.82). The directional thesis
   (low-IV → mean-revert → ride the vol-pickup-driven gold rally) is
   empirically supported.
2. **But IC-6 fails decisively**: the GVZ-z position vector and iter
   011's σ_60/σ_252 position vector have rolling-60d ρ = 59.7% on
   PRIMARY. Forward-looking option-IV and backward-looking realized-vol
   ratio are MEASURING THE SAME phenomenon at the position-vector
   level on gold. They fire long entries on overlapping regimes
   (low-vol windows) and exit on overlapping regimes (vol expansions).
3. **DSR-deflator fails at standalone Sh +0.246**: at `n_trials = 22`
   over ~17y, the DSR-deflator-cleared Sharpe threshold is approximately
   +0.65; our Sharpe is 38% of that.
4. **Bootstrap CI fails at −0.47**: 17-year daily-return series has a
   fat lower tail because the strategy's positive return is
   concentrated in a handful of vol-cheap → vol-pickup episodes
   (2009, 2011, 2018, 2019, 2024). At α = 0.001 the lower bound
   captures "what if those few good episodes hadn't happened" —
   heavily negative.

**Closes**:

- **Option-implied vol family on gold as a structurally novel
  direction**. Forward-looking option-IV (Sinclair `[volatility_trading,
  p.32-37]`, Bollerslev-Tauchen-Zhou 2009 RFS) and backward-looking
  realized-vol-ratio (iter 011) ride the same low-vol-regime macro
  clock on gold; the "forward-looking" framing was theoretically
  appealing but empirically the two signals are vol-regime family
  members. **Pattern matches GS-14** (TIPS DFII10 ρ=+0.52 vs iter 011)
  **and GS-15** (DXY-MA-slope ρ=+0.51 vs iter 014) — yet another
  ostensibly-orthogonal family riding gold's macro stress clock.
- **GVZ as IC-7 secondary on iter 011 base** (would be near-redundant
  given ρ static +0.55 / rolling 59.7%).

**Does NOT close**:

- **GVZ as IC-7 secondary on iter 003 base** (RSI(2)+SMA200): ρ vs
  iter 003 = +0.08 static / 10% rolling — comfortably orthogonal
  by both metrics. *But* combined ceiling √(0.30² + 0.246²) = 0.388
  is still well below the DSR-deflator-cleared 0.65 at n=22+ — not
  productive.
- **25-delta gold option risk-reversal skew**: different option-derived
  signal (asymmetric demand vs absolute level). May not collapse onto
  the realized-vol cycle the way absolute-IV does. Caution: data
  acquisition non-trivial.
- **CME futures track A2 intraday MR** (1-2 bps spread, different
  cost regime; closes nothing about that family).
- **DCOT producer-merchant hedger-side mirror** (mechanical-bias
  long-when-prod-merc-net-short-extreme).
- **Multi-asset gold_complex universe extension** (60% XAU + 30%
  GDX + 10% XAG).

**Process artifacts (reusable)**:

- `fetch_gvz.py` — FRED `GVZCLS` ingestion. Pattern reusable for any
  CBOE/FRED-published volatility index (OVX = oil, VXEEM = EM equity,
  VXTYN = treasury, etc.).
- `gvz_zscore_signal_long_when_z_below()` — daily-bar state machine
  with `lag_days` and `max_hold_days` (clean reusable for any
  daily-bar threshold-crossing signal).
- TDD: 7 tests in `test_gvz.py` covering rolling-z numerical
  correctness, no-lookahead lag-1 property, max_hold cap, cost-model
  parity. Pattern reusable across iters.

**Process notes**:

- Iter 022 reused iter 021's pipeline (`apply_costs`, `compute_metrics`,
  `deflated_sharpe_p_value`, `bootstrap_ci_low`, `walk_forward_split`,
  `cross_lib_check`) with the only new logic being
  `gvz_zscore_signal_long_when_z_below()` (daily-bar variant of iter
  021's weekly-bar state machine). The signal is qualitatively new
  (option-IV vs COT positioning) but the engine reuse is total.
- Primary slice handling (`primary_slice_start: "2009-06-04"`) gives
  the rolling-z window 1y of warmup post-GVZ-inception (2008-06-03)
  — the cleanest way to honor the warmup constraint while keeping
  the 16.83y post-warmup window. Sliced bench Sh 0.629 (vs full-21y
  0.684).
- IC-6 measurement (`correlation_diagnostic`) confirmed both static
  and rolling-60d ρ values; rolling exceedance fraction is the more
  conservative kill criterion (signal-by-signal regime overlap)
  vs static ρ (period-averaged).


### GS-23 — Within-precious-metals multi-asset basket (60% GLD + 40% SLV) extension of single-asset RSI(2)+SMA(200) MR is NOT structurally distinct from the single-asset version — silver leg adds essentially zero diversification on the position-vector level

**Iter**: 023-2026-04-26-1900-multi-asset-gld-slv-basket. **Tier**: NEAR_FAIL (35/100).

**Configuration tested (single cfg, IC-8)**:

```yaml
cfg_id: multi_asset_rsi2_sma200_gld60_slv40_basket
weights: {gold: 0.60, silver: 0.40}        # XAU >= 40% per spec
spreads_rt_bps: {gold: 8.0, silver: 20.0}  # XAG ~2.5x wider in practice
swap_long_bps_per_night: -1.0              # both legs Pepperstone Track A
signal_per_asset: connors_rsi2_sma200_filter  # identical to iter 003
broker_track: pepperstone_cfd
universe: gold_complex
hold_time_track: short_swing
declared_primary: gld_slv_basket_long      # 60% GLD + 40% SLV daily, 2006-04-28→2026-04-15 (19.97y)
declared_corroborating: [xau_xag_basket]   # 60% XAU + 40% XAG daily, 2020-01-02→2026-04-17 (6.29y)
```

**Result (cost-net per-leg, 2 datasets)**:

| dataset | Sharpe (basket bench Δ) | CAGR | MDD (Δ vs bench) | gates | DSR p (n=23) | mean hold |
|---|---|---|---|---|---|---|
| gld_slv_basket_long PRIMARY (60/40, 19.97y) | **+0.2954** (Δ −0.137 vs 0.4323) | +1.17% | **9.19%** (Δ −52.50% vs 61.69% bench) | **4/7** | 0.737 | 4.15d |
| xau_xag_basket CORROBORATING (60/40, 6.29y) | +0.2569 (Δ −0.633 vs 0.8903) | +0.98% | **7.13%** (Δ −21.30%) | 4/7 | 0.897 | 4.00d |

**Pre-committed kills check (6 of 6 fired)**:

- **Kill #1 (Sh < +0.30 on primary)**: **FIRED** — primary Sh +0.2954 just below threshold. Even matching iter 003's single-asset gold Sh (+0.30) was the bar; basket fails by 0.005.
- **Kill #2 (Sh lift < +0.05 vs iter 003)**: **FIRED** — lift = **−0.0046** (basket adds essentially zero edge over single-asset MR).
- **Kill #3 (IC-6 rolling vs iter003 > 95%)**: **FIRED** — rolling-60d ρ = **96.8% on PRIMARY** (vs 95% threshold); static ρ = +0.714.
- **Kill #3b (IC-6 rolling vs iter011 > 30%)**: **FIRED** — rolling-60d ρ = **33.1% on PRIMARY** (vs 30% threshold); static ρ +0.163 LOW but stress-window rolling exceeds the bar.
- **Kill #4 (G6 boot fail)**: **FIRED** — primary G6 99.9% CI low = **−0.378**; corroborating CI low = −0.865.
- **Kill #5 (DSR p > 0.30 on primary)**: **FIRED** — primary p = **0.737** ≫ 0.30.

**Closure logic (3 tiers)**:

1. **The mechanism is real but redundant.** Silver leg's RSI(2)<5 + SMA(200) signal triggers on the SAME bars as gold leg's signal because (a) both metals are above SMA(200) at the same times (joint precious-metals bull regime — they share the same macro driver) and (b) both have RSI(2) oversold dips on the same days (joint stress-driven 1-2 bar pullbacks within the bull regime). The result is a basket position vector with 96.8% rolling-60d overlap with the single-asset version — not multi-asset at the position-vector level.
2. **MDD reduction is the only structural improvement.** Basket MDD on PRIMARY = 9.19% vs single-asset gold benchmark's 45.6% — the loop's lowest MDD ever on a 20-year window. But this is a portfolio-construction property (signal selectivity gates exposure during high-vol bear regimes) orthogonal to the Sharpe-edge requirement. CAGR drops to 1.17% / 0.98% (silver underperformed gold, dragging basket bench Sh from 0.68 to 0.43; strategy still doesn't beat the lowered bench by +0.10).
3. **DSR-deflator wall holds at n_trials=23**: standalone Sh +0.295 with deflator-cleared threshold ~+0.65 → p=0.737. The basket's near-identical position vector to iter 003 (DSR p=0.43) means it inherits iter 003's DSR weakness with no lift.

**Closes**:

- Any **within-precious-metals** multi-asset gold_complex basket extension of a single-asset MR or trend signal as a "structurally novel" direction. Specifically: GLD+SLV, IAU+SLV, XAU+XAG, GLD+SLV+PPLT (any composition of gold/silver/platinum-group ETFs or spot pairs at static or near-static weights). Position-vector overlap with single-asset signal is too high for the basket to escape the single-asset DSR-deflator wall at n_trials=23+.
- The interpretation of sister-loop's "every winner was multi-asset" lesson on this loop: it must specifically refer to baskets with **cross-cluster diversification** (precious metals + equities, precious metals + crypto, precious metals + bonds), NOT within-cluster extension. Within-cluster basket extension is empirically not structural diversification.

**Does NOT close**:

- **Cross-cluster basket extension** (GLD + GDX miners): GDX has stock-market beta (S&P 500 ρ ~0.45) absent from spot gold; miner MR signal fires on a partially-different macro driver. Requires single Tiingo fetch for GDX (cheap). Expected ρ_static vs gold-MR signal: ~0.55-0.65, rolling exceed-frac < 80%. **Promoted to BASE_MEMORY priority 1**.
- **Gold + BTC** (GLD + BTCUSD): different macro driver entirely (digital scarcity). BTCUSD cached. Position-vector overlap likely < 0.20. **New BASE_MEMORY priority 4**.
- **Gold + LQD/TLT** (bonds basket): duration + inflation drivers. Need Tiingo fetch for LQD/TLT. **New BASE_MEMORY priority 5**.
- **GLD + SLV with DIFFERENT signals per leg** (e.g., gold MR + silver breakout): not the same hypothesis as iter 023; structurally legit.
- **CME futures track A2 intraday MR** (1-2 bps RT spread; structurally different cost regime). **BASE_MEMORY priority 3**.
- **DCOT producer-merchant hedger-side mirror** (BASE_MEMORY priority 2).

**Process artifacts (reusable)**:

- `studies/gold_swing_loop/iterations/023-*/run_backtest.py` — multi-asset basket engine: `build_basket_position()`, `compute_basket_pnl()` (per-leg cost application with distinct spread tiers), `basket_buyhold_returns()` (continuous-rebalance benchmark), `ic6_rolling_correlation_diagnostic()` (rolling-window ρ exceed-frac vs another series), `compute_basket_mean_hold()` (weighted-position aware). Reusable for any 2+ asset basket with per-leg signal + per-leg spread.
- `test_basket_signal.py` (7 tests, all green) — TDD coverage for per-asset signal byte-equivalence to iter 003, basket aggregation correctness, per-leg cost separation, buy-hold benchmark formula, IC-6 diagnostic, weighted mean-hold.
- Pattern validated: future cross-cluster baskets (gold+GDX, gold+BTC, gold+TLT) can clone iter 023's engine and just swap the silver path for the new asset path; rest of pipeline (signals, costs, gates, IC-6, scoring) carries over unchanged.

**Citations**:

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY).
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)+SMA(200).
- `[ilmanen_expected_returns, ch.10]` — precious metals as defensive basket.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 23`.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (per-leg spread).
- IC-6 (sister-loop closure 014/019) — rolling-correlation pre-val on PRIMARY.
- IC-7 (sister-loop closure 045/046) — Markowitz proportional-Sharpe weighting at ρ < 0.50; this iter shows ρ = 0.96 is the wrong basket composition for IC-7.

**Process notes**:

- TDD-first: 7 tests written before run_backtest.py production code. All green on first run; no signal-implementation defects.
- Per-leg cost model is the correct architecture for multi-asset baskets: silver leg gets 20 bps RT spread (Pepperstone XAGUSD wider than XAUUSD's 8 bps), aggregated via `net_pnl = sum(per_leg_net_pnl)`. Verified by direct comparison to per-leg `apply_pepperstone_costs` calls in test_per_leg_cost_applied_separately_with_distinct_spreads.
- Joint-window inner-join: GLD has 5384 daily bars (2004-11-18+), SLV has 5025 (2006-04-28+); inner-join yields 4779 bars 2006-04-28→2026-04-15. SLV's launch date is the binding constraint.
- Cross-lib G7 parity: numpy hand-roll of basket aggregation (per-leg position × shifted return − per-side spread on |position diff| − weekend-aware swap) reproduces pandas CAGR to 1e-6 on both datasets. Engine is correct; the result is the strategy's, not a bug.


### GS-24 — Cross-cluster gold-complex multi-asset basket (60% GLD + 40% GDX miners) extension of single-asset RSI(2)+SMA(200) MR ALSO collapses — gold-mining ETFs are gold-derivative, not orthogonal cross-cluster

**Iter**: 024-2026-04-26-1930-gld-gdx-cross-cluster-basket. **Tier**: NEAR_FAIL (30/100). **Cumulative n_trials = 24**.

**Configuration tested (single cfg, IC-8 mandate)**:

```yaml
cfg_id: cross_cluster_rsi2_sma200_gld60_gdx40_basket
weights: {gold: 0.60, gdx: 0.40}            # GLD/XAU >= 40% per spec
spreads_rt_bps: {gold: 8.0, gdx: 12.0}      # GDX as US-equity CFD ~1.5x wider than XAUUSD spot
swap_long_bps_per_night: -1.0               # both legs Pepperstone Track A (per-leg)
weekend_swap_mult: 3.0
signal_per_asset: connors_rsi2_sma200_filter  # identical to iter 003
broker_track: pepperstone_cfd
universe: gold_complex
hold_time_track: short_swing
declared_primary: gld_gdx_basket_long       # 60% GLD + 40% GDX daily, 2006-05-22→2026-04-15 (~19.9y, 5006 bars)
declared_corroborating: [xau_gdx_basket]    # 60% XAUUSD + 40% GDX daily, 2020-01-02→2026-04-15 (~6.3y)
```

**Result (cost-net per-leg, 2 datasets)**:

| dataset | Sharpe (basket bench Δ) | CAGR | MDD | gates | DSR p (n=24) | mean hold |
|---|---|---|---|---|---|---|
| gld_gdx_basket_long PRIMARY (60/40, ~19.9y) | **+0.2022** (Δ −0.267 vs 0.469) | +0.85% (vs 9.15%) | **13.94%** (vs 61.68% bench) | 4/7 | 0.860 | 4.91d |
| xau_gdx_basket CORROBORATING (60/40, ~6.3y) | **−0.1064** (Δ −1.071 vs 0.964) | −0.45% (vs 21.44%) | 10.33% (vs 31.64%) | 3/7 | 0.988 | 4.70d |

**Pre-committed kills check (5 of 6 fired)**:

- **Kill #1 (Sh < +0.30 on primary)**: **FIRED** — primary Sh = +0.2022, well below. Iter 003's single-asset gold Sh +0.30 is the comparison bar.
- **Kill #2 (Sh lift vs iter003 < +0.05)**: **FIRED** — lift = **−0.0978** (basket Sh +0.20 is BELOW single-asset +0.30). The basket aggregation actively DEGRADES Sharpe.
- **Kill #3 (IC-6 rolling vs iter003 > 80%)**: **FIRED HARD** — rolling-60d ρ = **94.9% on PRIMARY** (only 1.9 pp better than iter 023's 96.8% with SLV); static ρ = +0.668. Far short of the ≤ 80% bar to validate cross-cluster diversification.
- **Kill #3b (IC-6 rolling vs iter011 > 30%)**: **NOT FIRED** — rolling-60d ρ = 27.4% on PRIMARY (below 30% threshold); static ρ +0.144. Basket position vector is not a vol-regime family re-skin (different mechanism than GS-22).
- **Kill #4 (G6 boot fail)**: **FIRED** — primary G6 99.9% CI low = **−0.454**; corroborating CI low = −1.197.
- **Kill #5 (DSR p > 0.30 on primary)**: **FIRED** — primary p = **0.860** ≫ 0.30.

**Why it failed (3 tiers)**:

1. **GDX is gold-derivative, not cross-cluster.** Gold-mining ETFs hold equity in mining companies whose cash flows are levered ~2× to gold price. Ilmanen `[expected_returns, ch.10]` documents that mining stocks correlate ρ ~0.7-0.8 with spot gold and only ρ ~0.3-0.4 with broad equities — so GDX's S&P 500 beta (~0.45) is a *secondary* driver while gold-price loading is *dominant*. Empirically: when gold dips 1-2 days, GDX dips even more (leverage), and RSI(2) on GDX fires on essentially the same days as on GLD. Basket position vector overlap with iter 003 single-asset gold-MR signal is **94.9% rolling-60d** — only 1.9 pp lower than iter 023's GLD+SLV (96.8%). The cross-cluster hypothesis is decisively falsified for this asset class.

2. **Higher GDX volatility actively drags Sharpe.** GDX has ~2× the daily vol of GLD (miner equity beta + gold beta = leveraged exposure). When the basket triggers an entry on a gold dip, the GDX leg amplifies losses if the dip extends; the SMA(5) exit is too short to ride a recovery. Net: 40% GDX allocation adds noise without adding edge. Basket Sh (+0.20) is below single-asset (+0.30) — **iter 024 is the first iteration in 24 to produce a basket extension that is materially WORSE than its base mechanism**.

3. **DSR-deflator wall holds at n_trials=24**: standalone Sh +0.20 with deflator-cleared threshold ~+0.65 → p=0.860 (almost certainty of false positive). The basket's near-identical position vector to iter 003 (DSR p=0.43) inherits all of iter 003's DSR weakness with negative lift.

**Closes**:

- Any **gold-complex multi-asset basket** extension of a single-asset MR/trend signal where the 2nd leg is a gold-derivative asset:
  - GLD + GDX (this iter, ρ rolling 94.9% PRIMARY)
  - GLD + GDXJ (junior miners; even higher gold beta, ~1.5× GDX leverage)
  - GLD + RGLD (gold royalty/streaming company; cash flows are nearly pure gold exposure)
  - GLD + SIL / SILJ (silver miners; same pattern with silver-loading)
  - GLD + PPLT (platinum group metals; PGM correlation to gold ~0.65-0.75)
  - GLD + SLV (within-precious-metals, GS-23)
- The interpretation of sister-loop's "every winner was multi-asset" lesson (jointly with GS-23): **must mean baskets where the 2nd asset cluster has GENUINELY orthogonal macro drivers — not gold-complex-universe assets which all ride the gold-stress macro clock at MR-trigger frequency**.
- All "PM-adjacent equity-bridge" basket constructions when paired with iter-003-style RSI(2)+SMA(200) MR signal per leg.

**Does NOT close**:

- **GLD + BTCUSD 60/40** — BTC has a genuinely orthogonal macro driver (digital scarcity, crypto adoption cycles, halving events, regulatory news). BTC-gold ρ historically ~0.10-0.30. BTCUSD cached (2014-01+, ~12y). Position-vector overlap with iter 003 expected < 60% rolling. Promoted to **iter 025 priority 1**.
- **GLD + TLT 60/40** — bonds add duration + inflation drivers. TLT-gold ρ ~0.20-0.40 (positive but moderate). TLT cached. May need asymmetric SMA windows per leg (gold SMA(200), TLT SMA(60-100)) given different vol regimes. Promoted to **iter 025 priority 2**.
- **GLD + SPY 60/40** — broad-equity orthogonal driver (without miner amplification). SPY cached (~21y). Promoted to **iter 025 priority 5**.
- **CME futures track A2 intraday MR** at 1-2 bps RT spread (vs 8 bps Pepperstone CFD). Genuinely different cost regime. iter 007 z-MR died at 8 bps; revisit at futures cost. **Iter 025 priority 4**.
- **DCOT producer-merchant long-on-extreme-shorting** mirror — different family entirely (positioning, not basket). **Iter 025 priority 3**.
- **GLD + GDX with DIFFERENT signals per leg** (e.g., gold MR + miner trend-following). Not the same hypothesis as iter 024 — could break the position-vector overlap.

**Process artifacts (reusable, mostly cloned from iter 023)**:

- `studies/gold_swing_loop/iterations/024-*/run_backtest.py` — same multi-asset basket engine as iter 023; only data ingestion differs. Engine: `build_basket_position()`, `compute_basket_pnl()` (per-leg cost application, distinct spread tiers), `basket_buyhold_returns()`, `ic6_rolling_correlation_diagnostic()`, `compute_basket_mean_hold()`. Per-leg spread for GDX = 12 bps RT (US-equity CFD typical, ~1.5× XAUUSD's 8 bps).
- `test_basket_signal.py` (7 tests, all green) — TDD coverage adapted from iter 023.
- GDX added to Tiingo cache: `data/tiingo/daily/prices/GDX.parquet` (5013 rows, 2006-05-22→2026-04-24).

**Citations**:

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY citation; predicted heterogeneous risk drivers should diversify; GDX hypothesized as PM-adjacent equity with stock-beta — empirically falsified).
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)+SMA(200) per leg.
- `[ilmanen_expected_returns, ch.10]` — gold complex factor exposures; **explicit confirmation that mining stocks ρ ~0.7-0.8 with spot gold dominates equity beta ~0.3-0.4**, consistent with iter 024's empirical IC-6 finding.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 24`.
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low > 0 gate.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest, per-leg spread, cross-lib parity (G7 = 0.000 pp diff).
- IC-6 (sister-loop closure 014/019) — rolling-correlation pre-val on PRIMARY.
- GS-23 — within-precious-metals basket extension closure (motivated this cross-cluster test, which now extends GS-23 to GS-24 covering all gold-complex-universe baskets).

**Process notes**:

- TDD-first: 7 tests adapted from iter 023, all green after one substitution-bug fix (test was checking total-cost inequality which can coincide; replaced with explicit per-leg rate verification).
- Cross-lib G7 parity: 0.000 pp diff (basket aggregation engine cloned from iter 023, so parity carried over).
- Joint-window inner-join: GLD has 5384 daily bars (2004-11-18+), GDX has 5013 (2006-05-22+); inner-join yields ~5006 bars 2006-05-22→2026-04-15. GDX's launch date is the binding constraint.
- Iter 024 is the FIRST basket-extension iter to produce a primary basket Sharpe materially **below** the single-asset base mechanism (lift = −0.098). Iter 023's lift was −0.005 (essentially zero). This is a stronger empirical refutation of the "gold-complex basket helps" hypothesis than iter 023 alone provided.

### GS-25 — Cross-cluster GLD+BTCUSD 60/40 fixed-weight basket of iter 003 RSI(2)+SMA(200) MR signal: ★ FIRST IC-6 break in 25 iters (rolling-60d ρ vs iter003 = 68.1% PRIMARY) but Sharpe lift −0.13 due to cost-and-signal asymmetry; closes fixed-weight cross-cluster GLD+BTC same-MR basket but UNBLOCKS IC-7 Markowitz tangency + asymmetric-per-leg-signal compositions
*(iter 025 — `iterations/025-2026-04-26-2147-gld-btc-cross-cluster-basket/`)*

> **Iter 024 follow-up + corollary**: GS-23 (GLD+SLV within-PM) and GS-24 (GLD+GDX PM-adjacent miner) closed at IC-6 rolling-60d ρ vs iter003 of 96.8% / 94.9% respectively, leaving open the question whether the IC-6 ceiling was a property of "all gold-anchored baskets" or specifically "gold-anchored baskets with gold-derivative 2nd legs". Iter 025 substitutes the 2nd leg with BTCUSD — documented BTC-gold ρ historically ~0.10-0.30, with macro drivers (crypto-adoption cycles, halving supply shocks, regulatory/banking events, funding-rate liquidations) structurally orthogonal to gold's drivers (real rates, DXY, central-bank reserve flows, safe-haven). Empirical result: **rolling-60d ρ vs iter 003 dropped to 68.1% on PRIMARY (12.3y window 2014-01-02→2026-04-14, 3 085 bars), a drop of −27 pp vs iter 023/024**. Static ρ also collapsed from +0.71/+0.67 to **+0.258**. The cross-cluster diversification thesis is empirically validated AT THE POSITION-VECTOR LEVEL — BTC's MR signal genuinely fires on different days than gold's. **However**, IC-6 break alone does NOT translate to Sharpe lift: basket Sh +0.1725 is BELOW iter 003 single-asset +0.30 (lift −0.1275). Decomposition: BTC leg's higher costs (25 bps RT spread + −5 bps/night swap = ~3× gold's per-leg cost burden) + weaker BTC RSI(2) standalone post-cost Sharpe drag the 40% allocation. This is a structural failure mode different from GS-23/24: not "the assets are correlated" but "the cost-signal asymmetry under fixed weights".

**Empirical evidence** (Track A net of Pepperstone CFD costs, per-leg spread + per-leg overnight swap):

| dataset | window | basket Sharpe (Δ vs basket bench) | basket CAGR | basket MDD | gates | mean basket hold |
|---|---|---|---|---|---|---|
| gld_btc_basket_long (60% GLD + 40% BTCUSD daily, joint) | 2014-01-02 → 2026-04-14 (~12.28y, 3 085 bars) PRIMARY | **+0.1725** (Δ −0.901) | +1.14% (vs bench 31.11%) | **15.45%** (vs bench 47.50%) | **4/7** | 4.65d |
| xau_btc_basket (60% XAUUSD + 40% BTCUSD daily, joint) | 2020-01-02 → 2026-04-14 (~6.28y, 1 696 bars) CORROBORATING | **+0.6689** (Δ −0.084) | +3.49% (vs bench 39.87%) | **5.69%** (vs bench 43.24%) — **loop-best ever** | **5/7** | 3.85d |

**Per-leg trade activity (PRIMARY ~12.3y joint window, 60% gold / 40% BTC weights, RSI(2)<5 + SMA(200) regime gate)**:
- **gold leg**: 34 trades (~2.8/yr) — fewer than iter 024's 63/19.9y because the 12.3y window contains the 2014-2018 gold bear-stagnation where SMA(200) gating blocks most RSI(2) entries
- **BTC leg**: 37 trades (~3.0/yr) — comparable cadence despite BTC's much higher volatility (BTC's persistent uptrend keeps SMA(200) gate open most of the time, then RSI(2)<5 fires on each oversold dip)
- **basket trades (any leg in)**: 65 — substantial NON-overlap (34+37=71 total per-leg, basket=65 → ~85% leg-trade-distinctness, vs iter 023 SLV ~60% distinct, iter 024 GDX ~65%). The cross-cluster property is real at the trade-event level too.

**Per-leg cost totals (PRIMARY ~12.3y)**:
- gold spread: $0.0163 cumulative ≈ 16 bps total → 4.8 bps avg/trade RT (matches 8 bps RT × half-roundtrip × weight)
- BTC spread:  $0.0370 cumulative ≈ 37 bps total → 10.0 bps avg/trade RT (matches 25 bps RT × half-roundtrip × weight)
- gold swap:   $0.0115 cumulative drag (matches −1 bps/night × n_overnight × weight)
- BTC swap:    $0.0476 cumulative drag (matches −5 bps/night × n_overnight × weight; ~4× gold's, as expected)

**IC-6 rolling correlation breakthrough**:

| iter | basket | IC-6 rolling-60d vs iter003 PRIMARY | static ρ | drop vs preceding |
|---|---|---|---|---|
| 023 | GLD+SLV (within-PM) | 96.8% | +0.71 | (baseline) |
| 024 | GLD+GDX (PM-adjacent miner) | 94.9% | +0.67 | −1.9 pp |
| **025** | **GLD+BTCUSD (cross-cluster)** | **68.1%** | **+0.258** | **−26.8 pp ★** |

This is the **first iter in the 25-iter loop history** to drop below 80% rolling-ρ on PRIMARY. The 27 pp delta is structurally significant — it confirms that cross-cluster ρ is a real property of asset-driver heterogeneity, not just measurement noise. Iter 023's GLD+SLV and iter 024's GLD+GDX 95+% rolling ρ was a property of "PM-adjacent 2nd legs sharing gold's macro clock" (silver as monetary metal + miners as gold-cash-flow leverage), not a universal property of all gold-anchored baskets.

**Pre-committed kill criteria (4 of 6 fired; #3 cross-cluster IC-6 NOT fired — historic first)**:
- ✗ Kill #1 — primary basket Sh +0.1725 < 0.30 (FIRED): basket fails to even reach iter 003's standalone level
- ✗ Kill #2 — basket Sh − iter003 Sh = −0.1275 < +0.05 (FIRED): basket aggregation actively drags
- ✓ Kill #3 — IC-6 rolling-60d ρ vs iter003 = 68.1% ≤ 80% threshold (**NOT FIRED** — first time in 25 iters)
- ✗ Kill #4 — G6 bootstrap CI low = −0.566 ≤ 0 (FIRED): Sharpe is statistical noise
- ✓ Kill #3b — IC-6 vs iter011 rolling = 14.8% < 30% (NOT FIRED): basket is not a vol-regime re-skin
- ✗ Kill #5 — DSR p = 0.918 > 0.30 (FIRED): far from <0.05 (n_trials=25 needs Sh > ~0.65)

**Score breakdown**: 1 Sharpe edge 5/25 (corroborating positive) + 2 Gates 15/25 (primary 4/7 meets v2 threshold) + 3 DSR 0/15 + 4 CAGR floor 0/15 (basket-bh dominated by BTC bull) + 5 MDD ceiling 15/15 (loop-best on corroborating) + 6 Robustness 0/5 = **35/100, NEAR_FAIL**.

**Why structural** (not parameter-tweakable):

1. **Cost asymmetry under fixed weights**. BTC's CFD cost burden (25 bps RT spread + −5 bps/night swap) is ~3× gold's. RSI(2)+SMA(200) on BTC produces a similar trade cadence but with much higher per-trade transaction drag and overnight carry, leaving little post-cost edge for the BTC leg to contribute. The 40% allocation amplifies BTC's negative-EV signal contribution; reducing BTC weight to ~10-15% would mitigate this but at the cost of reducing the cross-cluster diversification benefit. Sweet-spot weight cannot be parameter-tuned without violating IC-8 (DSR n_trials drains fast).

2. **Signal asymmetry**. The same RSI(2)<5 + SMA(200) signal works on gold (iter 003 +0.30 Sharpe) but not equally on BTC. BTC's regime is more trend-persistent than mean-reverting historically (long bull legs separated by sharp 30-50% corrections). Connors' RSI(2) framework was designed for equity index MR; applying it unchanged to BTC with same threshold (5) and same exit (close > SMA(5)) doesn't capture BTC's distinct regime structure. Gold-MR + BTC-trend would likely be better matched.

3. **IC-3 (sister loop iter 049) extension violated**. IC-3 closes 50/50 composition when component Sharpes differ by > 30%. iter 025's 60/40 fixed weight has gold Sh ≈ 0.30 vs BTC Sh ~0.05-0.10 (post-cost) — a > 3× ratio difference. Markowitz proportional-Sharpe weighting (IC-7) would weight gold ~85% and BTC ~15%, recovering most of gold's standalone Sharpe with marginal cross-cluster lift; that's the natural follow-up (priority 1 for iter 026).

**Closes**: any cfg of `cross_cluster_basket(GLD, BTCUSD, w_gold ∈ [40%, 70%], w_btc ∈ [30%, 60%], same_signal=RSI(2)<5+SMA(200))` under Pepperstone CFD cost regime (Track A). Specifically:
- Different weight configurations (50/50, 70/30, etc.) tested in this iter's spirit are blocked by IC-8 (DSR n_trials drains fast); each weight sweep is a separate trial.
- Different RSI thresholds (RSI<3, RSI<10) on the same signal architecture are minor parameter variations with same structural defect (cost-and-signal asymmetry).
- Different SMA-trend periods (SMA(100), SMA(150)) are also minor variations.

**Does NOT close**:

1. **IC-7 Markowitz GLD+BTC tangency** — let the data choose proportional-Sharpe weights. Expected outcome: weights ~85% gold / 15% BTC, combined Sharpe upper bound = √(S²_gold + S²_btc · (1 − ρ²)) ≈ √(0.09 + 0.01 · 0.93) ≈ 0.31. Marginal lift over gold-only ~0.30, but a clean numerical test of IC-7 framework on the loop's first low-ρ pair confirmed by IC-6 evidence.
2. **Asymmetric per-leg signal**: gold MR (RSI(2)+SMA(200)) + BTC trend (Donchian-200, Clenow ATR-trend, or Carhart 12-1 momentum). Different family per leg may exploit each asset's natural regime structure.
3. **GLD + TLT 60/40 cross-cluster basket** — bonds add duration + inflation drivers. TLT-gold ρ historically ~0.20-0.40 (not as orthogonal as BTC but still cross-cluster). Bond regime is slower; may need asymmetric SMA windows per leg.
4. **GLD + SPY 60/40 cross-cluster basket** — broad-equity orthogonal driver (without miner amplification). SPY's drift is steeper than gold; SMA(200) regime gate may need adjustment.
5. **CME futures track A2 (1-2 bps RT spread)** — re-test cost-dominated intraday MR. Iter 007 z-MR died at 8 bps; at 2 bps RT, same z-MR may survive.
6. **DCOT producer-merchant mirror** — different family entirely (positioning data).

**How to escape** (informs iter 026+):

The IC-6 break in iter 025 makes the cross-cluster framework the most-promising direction in the gold loop. Two structurally-different follow-ups are now equally valid:

1. **Refine the same hypothesis** (IC-7 Markowitz on GLD+BTC) — small mechanical follow-up; tells us whether cross-cluster diversification is large enough to clear DSR even at proportional weights.
2. **Generalize to other cross-cluster pairs** (GLD+TLT, GLD+SPY) — tests whether the IC-6 break is BTC-specific or a general cross-cluster property. If GLD+TLT also shows < 80% rolling ρ with positive Sharpe lift, the loop has found a robust cross-cluster framework; if GLD+TLT shows > 90% rolling ρ (i.e., bonds and gold share macro clock at MR-trigger frequency due to common rate-cycle drivers), then cross-cluster only works with BTC's truly-non-traditional driver set.

**Citations used** (full text in `iterations/025-*/final_report.md`):

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY citation; thesis predicted heterogeneous-driver assets should diversify; iter 025 empirically validates the IC-6 floor break, but reveals that Sharpe lift requires proportional-Sharpe weighting, not fixed weights — IC-3 extension)
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5 + SMA(200) trend-filter; same per-leg as iter 003/023/024; reveals that the same signal does not work equally well on different-driver assets (cost-and-signal asymmetry)
- `[ilmanen_expected_returns, ch.10]` — gold-complex factor exposures; Ilmanen's caveat that crypto/digital-stores-of-value are weakly correlated to gold for asset-allocation purposes is empirically validated by iter 025's 0.258 static-ρ measurement
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 25`; deflator at this n requires standalone Sh > ~0.65 to clear, basket Sh +0.17 isn't even a candidate
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low > 0 gate (FAIL on basket: CI low −0.566)
- `[advances_fin_ml, p.31-34]` — cross-lib parity (G7 = 0.000000 pp diff)
- IC-3 (sister loop iter 049) — fixed-weight composition only when standalone Sharpes are similar; iter 025 violates this (gold +0.30 vs BTC much weaker post-cost) and the violation is structurally observable as Sharpe drag
- IC-6 (sister loop iter 014/019) — rolling-correlation pre-val mandate; iter 025 is the FIRST gold-loop iter to break the 80% floor (achieved 68.1%)
- IC-7 (sister loop iter 045/046) — Markowitz proportional-Sharpe framework; unblocked for iter 026 as priority 1

**Process notes**:

- TDD-first: 8 tests (one new vs iter 024 — `test_btc_swap_is_five_times_gold_swap_per_unit_overnight` — explicitly validates per-leg swap parameterization). All green first run.
- Cross-lib G7 parity: 0.000000 pp diff on both datasets (per-leg swap correctly factored into hand-rolled numpy reference).
- Engine reuse: ran from `iterations/024-*/run_backtest.py` with substitutions: GDX → BTCUSD path, dataset names, per-leg swap dict added to `compute_basket_pnl` signature. The existing `apply_pepperstone_costs` already supported per-leg swap rates via the `swap_long_bps` keyword argument; no changes to `cost_models.py` needed.
- Joint-window inner-join: GLD has 5 384 daily bars (2004-11-18+), BTC has 4 483 daily bars (2014-01-01+); inner-join yields **3 085 bars 2014-01-02→2026-04-14**. BTC's 2014 launch is the binding constraint (Tiingo's historical BTC data starts then).
- BTC trades 24/7 but Tiingo daily prices align to UTC end-of-day; inner-join on dates produces a clean 3 085-bar trading-day calendar driven by GLD's NYSE schedule.
- Iter 025 is the FIRST iter in 25 to break the IC-6 rolling-ρ floor — this is **structurally significant** and is the loop's first empirically-confirmed cross-cluster pair. Iter 026's priority 1 (IC-7 Markowitz GLD+BTC) is the natural mechanical follow-up; if even that doesn't clear DSR, the loop's strategic conclusion approaches: cross-cluster diversification is real but insufficient to bridge gold's persistent buy-hold drift under cost-realistic execution.
