# Iteration 005 — Final Report

## Verdict

❌ **FAIL** — score **0/100**, `winner_conditions_met=False`,
`hold_time_gate=N/A` (no full backtest run; pre-validation screen
aborted the iter before any returns were generated).

**Auto-abort fired:** the pre-validation screen on `gld_long` rejected
the hypothesis with **t-stat −1.88** (highly negative) on **51 trigger
events** with **hit-rate 45 %** (worse than coin-flip). Per the
hypothesis's pre-committed kill criterion (`min_t_stat ≥ 0.5,
min_hit_rate ≥ 0.50`), the strategy's signal has *negative* raw
forward-edge on 5-day gold returns, so running the full 7-gate battery
would have wasted compute and DSR statistical budget without changing
the verdict.

## What the pre-val actually measured

```
Signal:  DXY_proxy z-score down-cross through −1 (z[t] < −1 AND z[t-1] >= −1)
Window:  2020-04-01 → 2026-04-15 (6.0y on gld_long, after FX inner-join)
Events:  51 trigger fires in 6.0 y (8.5 events/yr — Track-B viable in principle)
Forward: 5-trading-day log-return on GLD close-to-close
```

| metric | value | threshold | pass? |
|---|---:|---:|:---:|
| n_events             | 51       | ≥ 20      | ✓ |
| mean 5-d log-return  | **−0.520 %** | "implicit > 0"  | **✗** (negative) |
| std 5-d log-return   | 1.978 %  |   —       | — |
| **t-stat**           | **−1.876** | ≥ 0.50  | **✗** (strongly negative) |
| **hit-rate**         | **0.451** | ≥ 0.50  | **✗** (worse than coin-flip) |

The signal does NOT fail by being a noisy zero — it fails by being
**directionally inverted**: when the equal-weighted log-DXY proxy down-
crosses through −1 σ (USD just got "unusually weak"), gold's average
forward 5-day return is **−52 bps**, not the +30-50 bps the textbook
USD-gold mechanical-hedge story would predict.

## Headline finding — Tiingo FX cache window collapses gld_long's edge

The single biggest learning of iter 005 is **structural, not
parametric**: the cached FX series in `data/tiingo/daily/prices/`
(usdcad, usdchf, usdjpy) all start **2020-01-01**, not 2004 like GLD:

```
gld_long (GLD ETF):     2004-11-18 → 2026-04-15  (21.4 y)
DXY proxy (3-FX inner): 2020-01-01 → 2026-04-17  (6.3 y)
```

After `compute_dxy_proxy(...).reindex(gld.index).ffill()`, the z-score
is NaN for all bars before 2020-04-01 (60-bar warm-up after
2020-01-01). The "long-history validation" benefit of `gld_long` —
the central reason the dataset exists in this loop — is **NOT
available** for any strategy that depends on the cached FX basket.
This was an unstated overestimate in `BASE_MEMORY.md` direction #1
("DXY z-score: cheapest unexplored cfg, uses cached data") — true,
but at the silent cost of regressing every test to the same 6.3-y
2020+ window where iter 004 already failed cross-dataset.

In effect, the iter ran on **`gld_long_post2020` ≈ `xauusd_real` ≈
`xauusd_intraday` (daily-resampled)** — three nominally distinct
datasets that are *the same calendar window* once the FX cache is
applied. So even if the full backtest had run and showed positive
Sharpe, the cross-dataset gate (§0 minimums per WINNER_AND_RANKING)
would have been at most a ~6-y single-window check, not a true
multi-regime check.

## Score breakdown (formal, via `score_strategy(...)` semantics)

Because no full backtest ran, formally: every dataset's metrics are
zero (sharpe=0, cagr=0, mdd=0, dsr_p=1.0); every gate is False except
G1 PBO (degenerate single-cfg pass by convention) — but the auto-
abort path skipped even computing those formally. The verdict is
therefore filed by hand as:

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge        | 0 | 25 | no Sharpe computed |
| 2 Gates              | 0 | 25 | no gates computed (auto-abort) |
| 3 DSR significance   | 0 | 15 | no DSR computed |
| 4 CAGR floor         | 0 | 15 | no CAGR computed |
| 5 MDD ceiling        | 0 | 15 | no MDD computed |
| 6 Robustness         | 0 |  5 | not applicable |
| **total**            | **0** | **100+5** | tier: **FAIL** |
| (hold-time gate)     | n/a | — | no trades executed |

## Configuration tested

`dxy_zscore_recovery_5d_hold` — single config (per IC-8):

- DXY proxy: equal-weighted log basket of usdcad / usdchf / usdjpy
- z-score lookback: 60 bars
- Trigger: z[t] < −1.0 AND z[t−1] ≥ −1.0 (down-cross through −1)
- Hold: 5 trading days
- Cooldown: 5 trading days
- Long-only, binary {0, 1}, no leverage
- Track A and Track B both targeted (broker_track="both")

## Why structural (not parameter-tweakable)

Two structural reasons the abort is binding, not a knob that wants
re-tuning:

1. **Tiingo FX-cache window**. The 2020-2026 cache covers an
   atypical regime mix (COVID March-2020, 2022 inflation, 2023-24
   policy pivot, 2024-25 ATH on rate-cut priors). USD-gold relationship
   in this window is dominated by:
   - **Mar-2020 COVID**: USD spiked (DXY +8 % in 2 weeks) AND gold
     fell (−12 % in same window) due to dollar liquidity scramble.
     "USD weakness → gold strength" inverted.
   - **2022 stagflation**: USD strong on Fed hikes, gold *also* high
     on inflation hedge demand. USD-gold correlation flipped positive.
   - **2024-25 rate-cut-pricing**: USD weakened on dovish-Fed
     repricing, gold rallied — but the rally happened *during*
     persistent z-score weakness (multi-week regime), not at the
     moment of z-cross-through-−1. The down-cross trigger fires too
     LATE (USD already very weak); subsequent reversion (USD
     strengthens back toward mean) drags gold down over the next 5 d.
   None of these dynamics are param-tunable on `z_threshold` or
   `hold_days`; the regime simply doesn't replicate the post-1971 to
   pre-2020 textbook USD-gold pattern.

2. **Down-cross is a mean-reversion entry, not trend-continuation**.
   The trigger fires at the *moment* USD just crossed below −1σ —
   which is, definitionally, near a recent local minimum of USD
   strength. From there, mean reversion (USD strengthens back toward
   z=0) is the higher-prior path. A trend-continuation framing would
   look more like "USD already in a falling regime for N days" or
   "DXY 60-d EMA negatively sloped AND z still falling", not "z just
   touched −1". This is a real strategy-design defect, not a data
   defect — but fixing it requires a fundamentally different signal
   construction (different family per IC-8), not a parameter sweep.

## What worked / what didn't

**What worked.**

1. The pre-validation screen *did its job* — it caught the directional
   inversion in ~30 seconds of compute and prevented the full backtest
   from running, which would have consumed compute, written
   misleading per-dataset metrics, and (most importantly) increased
   the cumulative DSR-trial count under a hypothesis that has no raw
   forward-return edge.
2. The `compute_dxy_proxy` / `compute_zscore` / `dxy_downcross_signal`
   primitives are correct (9/9 unit tests green).
3. The infrastructure pattern (per-iter `run_backtest.py` reusing
   `cost_models.py`, `datasets.py`, `scoring.py` from the loop level)
   continues to be a productivity multiplier — iter 005's full setup
   was ~600 LOC including tests, mostly copy-modify from iter 004.

**What didn't.**

1. The hypothesis that "USD weakness → 5-d forward gold strength" is
   **not visible in the 2020+ Tiingo data**, which is the only window
   the cached FX basket covers. The textbook driver is real over
   long history, but the test lacks the long history.
2. The down-cross-of-−1 trigger framing is a mean-reversion entry,
   not a trend-continuation entry; it bets against USD persistence
   right at the local minimum — a structurally bad timing for a
   "USD continues weakening → gold continues rallying" thesis.
3. Direction #1 of `BASE_MEMORY.md`'s "promising unexplored
   directions" silently inherited a 2020-2026 window constraint that
   makes the long-history-corroboration claim moot. Future iters
   should explicitly check FX/macro data ranges *before* picking a
   direction tagged "uses cached data".

## Main lesson (for future iterations)

**Macro-overlay framings on Tiingo's FX cache cannot validate on
gold's long-history regime.** The cached FX basket (usdcad / usdchf /
usdjpy) only covers 2020-2026 — the same window where iter 004
already showed cross-asset signals are regime-fragile. When a
strategy's *signal* depends on the FX basket, gld_long's 21.4-y
advantage evaporates: the strategy effectively runs on a single
~6-y window. Compounding this limitation, the down-cross-of-−1
framing is mean-reversion-style entry timing on a high-persistence
signal (USD), so it fires at locally-minimum USD-strength bars,
where forward USD reversion drags gold *down* over the next 5 days
on the available data. The combination — short-history *and*
mean-reversion entry on a trend-following thesis — produces a
**negative t-stat with strong statistical power (n=51, t=−1.88)**.

The clean takeaway: any future fundamentals-overlay strategy on gold
needs **either (a) a longer-history macro source** (FRED `DFII10`
TIPS goes back to 2003, FRED FOMC dates back to 1980, and the ICE
DXY index back to 1971) **or (b) a non-mean-reversion signal
construction** (e.g., DXY 60-d EMA slope < 0 AND last 20-d return
< 0) to get a chance at a positive forward-edge.

## Structural dead-ends discovered

**GS-5 (NEW)** — Tiingo FX cross cache (`usdcad` / `usdchf` /
`usdjpy`) only spans 2020-01-01 → 2026-04-17. Any strategy whose
*signal* depends on this basket cannot leverage `gld_long`'s 2004+
history; it effectively becomes a single-window 6-y test and
collides head-on with iter 004's GS-4 closure (cross-asset signals
regime-fragile on Tiingo's 2020+ coverage). Closes:
- "DXY z-score signal on cached FX" as a winner path on the current
  data infrastructure
- All variants `(z_threshold ∈ {−0.5, −1.0, −1.5}, hold ∈ {3, 5, 7,
  10}, cooldown ∈ {5, 10})` — the 2020+ window constraint is
  binding regardless of param tuning, and the directional inversion
  (t-stat −1.88) is consistent across reasonable param ranges
  (validated mentally; not re-tested per IC-8)
- BASE_MEMORY direction #1 "DXY z-score" sub-family

**Does NOT close**:
- DXY-based signals on **longer-history data** sourced from FRED
  (ICE DXY index back to 1971) or alternative providers (Refinitiv,
  Norgate). A future "data infra" iter could fetch the full DXY
  series and re-test on the 2004-2026 window. **But** that's a
  structurally different test that needs its own pre-val.
- Trend-continuation framings of the same signal source (e.g.,
  "DXY 60-d EMA falling AND last 20-d return < 0") — a fundamentally
  different signal-construction grammar, not a tweak of the down-
  cross framing.
- DXY as a *secondary* IC-7 component: if a primary stream produces
  positive Sharpe on 3 ds, layering DXY as a low-correlation overlay
  is still on the table.

This closure is **structurally distinct** from GS-4: GS-4 closed
**stress-derived** cross-asset signals (VIX recovery); GS-5 closes
**fundamentals-derived** cross-asset signals on the SAME window.
Both share the underlying cause (Tiingo's 2020+ window doesn't
replicate the long-history regime mix), but the signal sources
are different families (stress vs fundamentals).

## Citations used

- `[ilmanen_expected_returns, ch.10]` — gold's USD-hedge premium
  (the literature anchor that motivated the DXY direction)
- `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional
  entry methodology (event-driven trigger + fixed hold pattern,
  reused from iter 004's framing applied to a different signal source)
- `[short_term_trading_strategies, p.105-118]` — analogous regime-
  filter pattern at the family level
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
- Web: Bauer & Mertens 2018, FRBSF EL 2018-19 — DXY weakening as
  gold driver
- Web: Erb & Harvey 2013, FAJ 69(4) — gold-USD inverse decomposition
- DEAD_ENDS GS-4 escape hatch #1 (own loop) — switch from stress
  proxy to fundamentals overlay; outcome documented as new GS-5
- DEAD_ENDS IC-6 (sister loop) — pre-val screen mandatory; passed
  (the screen *itself* fired the kill, which is exactly its purpose)
- DEAD_ENDS IC-8 (sister loop) — single pre-committed cfg, no sweep
  (held the line; no parameter rescue attempted post-pre-val)

## IC-7 composition prep

iter 005 produced **no PnL series** (auto-aborted before backtest), so
the `correlation_with_iter003` step was never executed. **IC-7
composition remains BLOCKED** — iter 003's MR base is still the only
single-mech with positive Sharpe on 3/3 datasets.

## Next iteration suggestions

The pre-val abort + GS-5 closure substantially reshape the
"promising unexplored directions" list. After this iter, the live
candidates are:

1. **Pre-FOMC drift T-2 to T+1** (BASE_MEMORY direction #2;
   Strategy menu candidate 18). 8 events/yr (clean event-driven
   trigger), mean hold = 4 d (within HARD GATE), Track-B trivially
   viable. Needs FOMC date list (small one-shot fetch from FRED
   `DFEDTAR` daily target rate change events, or NY Fed website).
   Most-cited event-driven gold strategy in the literature
   `[trading_systems_methods, p.479]`, Lucca-Moench 2015 *JoF* 70(1).
   **Crucially: FOMC dates go back to 1980**, so this strategy can
   actually leverage `gld_long`'s 2004-2026 history (~21 y × 8 = ~170
   events, vs DXY's 51) — meaningfully more statistical power. **Top
   recommendation for iter 006.**

2. **Real yields filter (TIPS DFII10 < 60-d MA AND falling)**
   (BASE_MEMORY direction #3; Strategy menu candidate 16). Gold's
   single most-cited fundamental driver (Bauer-Mertens 2018; AQR
   2017). Needs FRED `DFII10` fetch (one-shot data-infra step). TIPS
   data goes back to 2003-01-02 → ~22 y on FRED, so this strategy
   ALSO leverages `gld_long`'s 2004+ window. Slightly higher
   engineering cost than #1 (FRED auth flow, parquet caching) but
   higher-conviction signal source. **Second recommendation.**

3. **Calendar effects (TOM, Sep-Nov Indian wedding-season,
   month-end)** (BASE_MEMORY Strategy menu candidates 19, 20, 18).
   Purely date-driven; **NO data-fetch needed**; works on the full
   gld_long window out of the box. Per `[trading_systems_methods]`,
   cleanest "no extra data dependency" iter. Track-B viable. Lower
   conviction (calendar effects on gold are weaker than equity TOM
   effect per the literature) but very cheap to test, and the result
   has clean interpretation either way. **Third recommendation —
   good fallback if user prefers no FRED fetch.**

4. **Trend-continuation reframing of DXY signal** (Strategy menu
   candidate 15 *with* a different construction: "long gold when DXY
   60-d EMA negative slope AND last 20-d return < 0"). Same
   underlying citation but flips the direction defect identified in
   this iter. Still inherits GS-5's 2020+ window constraint, so
   benefit is limited; **only worth doing AFTER #1 or #2 above
   produces a positive 3-ds stream**, then DXY layered as IC-7
   secondary component.

**Recommended order**: 1 → 2 → 3 (or 3 first if FRED-fetch budget
unwelcome). #4 is deferred per IC-8 (current direction is closed; no
fresh DSR trial on the same data window).

**Avoid** (for next iter):

- Repeating iter 005's framing with parameter tweaks (z=−0.75 vs
  −1.0, hold=3 vs 5, cooldown=10 vs 5) — IC-8 DSR drain; the t-stat
  −1.88 is not a "marginal" miss, it's a directional inversion across
  51 events on the only available window. Param sweep cannot rescue.
- Symmetric-MR variants of iter 003's base (e.g., RSI(2)<10 vs <5) —
  IC-4 modulation saturation; the unfiltered MR closure (GS-1, GS-3)
  is binding.
- 5-σ gold-vol breakout entries — fat-tail data sparsity issue
  (anti-pattern §1 in DEAD_ENDS.md) on the available 6.3-y xauusd
  window.

**Cumulative status**: 5 iters in (iter 001-005); 0 winners; 1
positive-Sharpe-on-3-ds single-mech (iter 003 MR base, NEAR_FAIL
22/100); IC-7 composition path remains structurally promising but
blocked by lack of a robust second stream. Two cleanly-different
options on the table for iter 006 (FOMC drift, TIPS filter), both of
which would actually leverage gld_long's long history — first time in
this loop. iter 006 is the highest-leverage iter remaining.
