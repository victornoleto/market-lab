# Iteration 015 — Final Report

## Verdict

❌ **FAIL** (score **17/100**, winner_conditions_met=False, hold_time_gate=fail)

**The DXY 200d-MA-slope falling regime gate produces a real but weaker
signal than iter 014's DFII10 macro stream.** All 3 datasets deliver
positive Sharpe (+0.24 to +0.36) and per-trade gross is excellent
(+534-558 bps), but the strategy is *too slow* (mean hold 113-121 days
= 6 trades over xauusd's 6.3y window), gld_long Sharpe (0.24) falls
below the kill threshold (0.30), and **gld_long MDD 50.72% breaches the
benchmark+5pp ceiling (50.60%) by 12 bps** — the very risk profile this
strategy was hypothesized to *improve* via DXY downtrend filtering. The
cross-dataset kill (xauusd both Δ < 0) AND the gld_long-Sh kill BOTH
fire. **Iter 015 is the worst-tier outcome in the loop's first 15 iters.**

**However**, iter 015 produces the loop's most informative finding to
date: **GS-14's macro-generic same-clock corollary is confirmed**. The
DXY-slope stream's correlation with iter 014's DFII10 stream on gld_long
is **ρ = +0.513**, statistically the same as iter 014 vs iter 011
(+0.519) — meaning DXY-trend, real-rate-trend, and gold-vol-regime are
**all downstream of the same multi-month macro cycle**. This forecloses
a major chunk of the IC-7 candidate space on the long window: any
trend-style macro overlay at quarterly+ horizons will share the clock
and ρ-out at +0.50 against existing streams.

## Headline metrics (NET of Pepperstone CFD costs, Track A)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | DSR p | mean hold |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.240 (**−0.444**) | +2.09% (−9.23 pp) | **50.72%** (+5.16 pp ✗) | 4/7 | 0.733 | 121.3 d |
| xauusd_real       | +0.323 (**−0.716**) | +3.39% (−16.54 pp) | 20.69% (+0.33 pp) | 4/7 | 0.628 | 121.2 d |
| xauusd_intraday   | +0.356 (**−0.747**) | +3.63% (−16.56 pp) | 24.69% (+0.27 pp) | 4/7 | 0.523 | 113.1 d |

OOS / FWD-2022 / Bootstrap / WF detail:

| dataset | OOS-30% Sh | FWD-2022+ Sh | Boot CI low (99.9%) | WF 6/8? | G7 |
|---|---:|---:|---:|:---:|:---:|
| gld_long          | +0.493 ✓ | +0.477 ✓ | < 0 ✗ | ✗ | ✓ |
| xauusd_real       | +0.491 ✓ | +0.300 ✓ | < 0 ✗ | ✗ | ✓ |
| xauusd_intraday   | +0.547 ✓ | +0.316 ✓ | < 0 ✗ | ✗ | ✓ |

OOS / FWD positive everywhere — signal is consistent (not curve-fit) —
but Bootstrap 99.9% CI lower bound dips negative on every dataset (long
left tail of "false-trend" flips). DSR worst p=0.733 — at n_trials=15,
deflator drowns the signal even at +0.36 Sharpe.

## Per-trade attribution

| dataset | n_trades | gross/trade (bps) | cost/trade (bps) | net/trade (bps) | cost/gross |
|---|---:|---:|---:|---:|---:|
| gld_long          | 16 | +533.9 | +172.2 | +361.7 | 32% |
| xauusd_real       |  6 | +557.9 | +130.0 | +427.9 | 23% |
| xauusd_intraday   |  6 | +554.2 | +103.1 | +451.1 | 19% |

**Per-trade gross is the highest seen in any iter** — when a DXY-trend
flip fires, the average gold rally is ~5%, and net of swap (long hold +
weekend triple-swap multiplier) net is +3.6-4.5%. The signal is
*qualitatively* correct (catches USD-down → gold-up macro phase). The
problem is *quantitative*: only 6 trades on xauusd's 6.3y means the
signal can't be pure-noise-rejected (DSR p=0.523), and the strategy is
"off" 57% of the time — collapsing CAGR (3.4%) far below buy-hold's
+19.9%. The opportunity cost of being flat during 60% of the bull
window is structurally larger than the strategy's MDD avoidance.

## IC-7 correlation diagnostic (the loop's main finding this iter)

| dataset | ρ vs iter 003 (RSI MR + SMA200) | ρ vs iter 011 (vol-regime σ_60<σ_252) | ρ vs iter 013 (vol-regime + SMA200) | ρ vs iter 014 (DFII10 falling) |
|---|---:|---:|---:|---:|
| gld_long          | **+0.170** | +0.433 | +0.429 | **+0.513** |
| xauusd_real       | +0.218 | +0.363 | +0.343 | +0.382 |
| xauusd_intraday   | **−0.065** | +0.275 | +0.267 | +0.377 |

Two findings on this map:

1. **GS-14 corollary CONFIRMED at macro-generic level (gld_long
   vs_iter_014 = +0.513)**. Iter 014 already showed DFII10 ↔ vol-regime
   share a clock at ρ=+0.519. Now iter 015 shows DXY-trend ↔ DFII10
   share a clock at ρ=+0.513 on the same window. Three streams from
   three "different families" (vol, real-rates, FX-trend) **all
   correlate at ρ ≈ +0.5 on gld_long** — they are all downstream of a
   single underlying real-rate / macro-cycle clock that paces the long
   window. **Any quarterly+ macro overlay on gld_long will hit this
   ceiling**.

2. **iter 003's RSI-MR is the most-orthogonal-yet stream** (ρ vs 015 of
   +0.17 / +0.22 / −0.07 across datasets). This makes iter 003 (NEAR_FAIL,
   score 22) the prime candidate for IC-7 composition with DXY-trend or
   any future trend/macro stream. Specifically on xauusd_intraday, ρ is
   actually slightly *negative* (−0.07) — they trade in different
   regimes, anti-correlated. **The IC-7 path on xauusd_intraday with
   003+macro composition is the single most promising direction
   discovered by this iter.**

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | **0** | 25 | 0/3 ds beat bench Δ ≥ 0.10; trend-slope filters too aggressively |
| 2 Gates | **7** | 25 | gld 4/7 (1 pt < 5 threshold), real 4/7 (3 pt at threshold), intra 4/7 (3 pt at threshold); cross-ds bonus FAILS (gld below threshold) |
| 3 DSR | **0** | 15 | worst p = 0.733 on gld_long (n_trials=15; deflator demolishes weak signal) |
| 4 CAGR floor | **0** | 15 | All 3 ds fail floor (0.8 × bench): gld 2.09% < 9.05%, real 3.39% < 15.94%, intra 3.63% < 16.16% |
| 5 MDD ceiling | **10** | 15 | gld 50.72% > 50.6% ✗, real 20.69% ≤ 25.36% ✓, intra 24.69% ≤ 29.42% ✓ |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **17** | **100+5** | tier: **FAIL** |
| (hold-time gate) | **fail** | — | mean 113.1d on xauusd_intraday primary; cap at STRONG per condition #6 |

## Configuration tested

```
config_id        : dxy_sma_slope_falling_200_20_long_only
sma_window       : 200 (Clenow trend-MA `[stocks_on_the_move, p.100]`)
slope_lookback   : 20  (1-month slope estimation; standard)
broker_track     : pepperstone_cfd  (Track A primary; Track B reported informational on daily)
costs A          : spread 8 bps RT + swap −1 bps/night long
costs B          : FX 100 bps RT + DARF 15% monthly
cumulative_n_trials : 15
DXY data source  : FRED DTWEXBGS (Nominal Broad USD Index, 2006-01-02 → 2026-04-17, 5087 bars)
```

Single pre-committed cfg per IC-8. No grid.

## Pre-validation summary

| dataset | p_active | μ active bps/bar | flips | passed |
|---|---:|---:|---:|:---:|
| gld_long          | 0.360 | +3.700 | 31 | ✓ |
| xauusd_real       | 0.428 | +3.958 | 11 | ✓ |
| xauusd_intraday   | 0.428 | +0.208 | 11 | ✓ |

3/3 pass. Signal IS active and directional (+3.7-4.0 bps/bar on daily
when on, slightly less per-bar on hourly). The disappointment is
magnitude: the active-when-on edge isn't enough to bridge gold's
buy-hold drift on the 60-65% of bars when signal is OFF.

## What worked

1. **Signal is real, not curve-fit**. Pre-val 3/3 pass, OOS Sharpe
   ≥ full-sample Sharpe everywhere, FWD post-2022 all positive.
2. **Per-trade economics excellent** (gross 553-558 bps; net 362-451 bps).
3. **MDD reduction on xauusd both datasets** — gld_long aside, the
   strategy DOES filter risk on the cost-realistic instrument. xauusd_real
   MDD 20.69% (vs bench 20.36%, +0.33 pp basically tied); xauusd_intraday
   24.69% (vs 24.42%, +0.27 pp tied). On these datasets the strategy
   captures ~30% of bench Sharpe with similar MDD — reasonable but not
   edge-bearing.
4. **G7 cross-lib EXACT 0.00e+00 pp parity** all 3 datasets. The numpy
   reference for `dxy_sma_falling_flag_numpy` matches pandas bit-for-bit
   (cumsum-based 200d MA construction).
5. **No look-ahead bug** (position[t] uses signal[t-1]).
6. **All 11 TDD tests pass**; baseline preserved.
7. **FRED DTWEXBGS ingester clean** (mirrors DFII10 pattern; idempotent;
   5087 bars cached covering 2006-01-02 → 2026-04-17).

## What didn't work

1. **gld_long Sharpe 0.240 breaks the family kill threshold** (0.30).
   The DXY-MA-slope grammar is *less* discriminative than iter 014's
   direct lag on DFII10 (Sh 0.319 there). The 200d-MA smoothing slows
   reactivity below useful resolution.
2. **gld_long MDD 50.72% > ceiling 50.60%**. The hypothesized "filter
   USD-up drawdown phases" mechanism FAILS on the long window — strategy
   takes a 50%+ DD anyway. Why: the 2013-2018 gold drawdown was multi-
   year, and DXY's 200d MA slope wasn't always falling during the worst
   of gold's losses; the strategy entered the drawdown during the
   "USD pause" phases that interleaved the broader USD strength cycle.
3. **All 3 datasets fail Sharpe-edge criterion** (0/3 datasets beat
   bench Δ ≥ 0.10).
4. **DSR 0/3 fail**. Worst p=0.733 on gld_long (n_trials=15; even at
   +0.36 intraday Sharpe, p=0.523).
5. **CAGR floor 0/3 fail** — strategy "off" 60% of the time → cumulative
   CAGR collapses (2-4% vs benchmark 11-20%).
6. **G6 Bootstrap 0/3 fail**. The 99.9% lower CI captures the bottom of
   trend-flip distribution, which is heavily negative.
7. **G3 Walk-Forward 0/3 fail** — strategy too sparse / unevenly active
   to satisfy 6/8 windows + MDD<25%.
8. **Mean hold 113-121 days** — far past the 5-day hold gate.
   Swing-extended; tier ceiling = STRONG even before scoring kill.
9. **Track B catastrophic on long window** (informational): gld_long
   Sh +0.144, MDD 53.78%; reaffirms GS-2 closure for any DARF-bound
   long-hold strategy.
10. **gld_long ρ vs iter 014 = +0.513** confirms GS-14 macro-generic
    corollary — DXY trend and DFII10 trend are *not* IC-7-orthogonal on
    gld_long. Closes IC-7 composition (DXY, DFII10) on the long window.
11. **gld_long ρ vs iter 011/013 = +0.43**, just below IC-7 0.50
    boundary. Marginal IC-7 candidate but DSR uplift would be ~10% per
    sister-loop scaling — not enough to clear deflator at n_trials=15+.
    On xauusd ρ is +0.34-0.36, in IC-7 sweet spot — but DXY-trend has
    NEGATIVE Sharpe edge on xauusd, so composition would dilute base.

## Main lesson (for future iterations)

**The same-macro-clock observation from GS-14 generalizes: on
gld_long's 21y window, trend-style macro signals (rates, FX,
gold-vol-regime) all ride a single underlying real-rate / macro-cycle
clock at ρ ≈ +0.5. Iter 015 gives the third independent measurement of
this ceiling from a different family.** The implication is binding for
the loop's remaining IC-7 candidate space:

- DXY-trend, DFII10-trend, vol-regime, and any quarterly+ trend signal
  built on macro variables will pairwise-correlate at ρ ≈ +0.5 on
  gld_long. **None of them can compose in pairs to break the gld_long
  ceiling Sh ≈ 0.55.**
- The only *high-orthogonality* base discovered so far is **iter 003
  (RSI-MR + SMA200)**, which sits at ρ = +0.17 / +0.22 / −0.07 across
  datasets. iter 003's family (price-action mean-reversion + drift
  filter) is genuinely orthogonal to macro-trend signals. **iter 016
  could test IC-7(003 + 015) on xauusd_intraday where ρ is near zero
  (−0.07) — this is the highest-orthogonality pair the loop has
  discovered**.
- The remaining structurally novel direction with ANY chance of breaking
  the gld_long ceiling on a *single stream* is **CFTC COT positioning
  extremes** — *not* a price/macro trend signal but a *response-to-
  macro* signal. Positioning shifts on weeks, not on macro-clock months;
  weekly cadence; strong literature (Cordero 2017; de Roon-Nijman-Veld
  2000). Requires CFTC fetch (one-time data infra cost, ~30 min).

**Strategic recommendation**: iter 016 should pursue **EITHER** (a)
IC-7 composition iter 003 + iter 015 on xauusd_intraday (highest-
orthogonality pair, smallest infra cost, but potential gld_long-only
edge limit), **OR** (b) CFTC COT positioning extremes (different family
entirely, larger infra cost, but addresses gld_long ceiling head-on).

## Structural finding (DEAD_ENDS GS-15)

**GS-15 closes the DXY-MA-slope family on gold day/swing.** The 200d-MA-
slope-falling gate at 20-day slope lookback fails on:
- Sharpe edge (0/3 ds beat bench Δ ≥ 0.10)
- gld_long Sh < 0.30 family threshold (0.240)
- gld_long MDD ceiling (50.72% > 50.60%)
- DSR n_trials=15 deflator (0/3 ds clear p<0.05)
- WF, Bootstrap (0/3 ds each)

**Closes**:
- DXY trend-slope filter at SMA(200) + slope(N) for N ∈ {5, 10, 20, 30, 60} —
  sensitivity to slope_lookback won't break the Sh-0.36 ceiling because
  the underlying constraint is "signal flips ~5×/window → DSR drained"
- DXY-trend × any iter 011/013/014 IC-7 composition on gld_long — ρ = +0.43-0.51,
  predicted DSR uplift too small to clear n_trials=15 deflator
- BASE_MEMORY direction #1 (DXY LEVEL regime gate) at lookback=200d
  with Slope grammar

**Confirms** GS-14 corollary at the macro-generic level: "same-macro-
clock" applies to FX-trend signals as well as real-rate-trend. The
gld_long single-stream ceiling at Sharpe ≈ 0.55 is robust across at
least 4 distinct families (vol-regime, regime-gated MR, real-rate
trend, FX trend).

**Does NOT close**:
- DXY-derived signals at *non-trend* grammars (z-score MR closed by
  GS-5; positioning signals NOT closed)
- DXY × non-macro-trend IC-7 composition (e.g., DXY × iter 003 RSI-MR
  on xauusd_intraday at ρ = −0.07 — orthogonal pair preserved)
- DXY at much SHORTER horizons (slope_lookback=3-5 days) — but those
  are likely noise; not currently prioritized

## Citations used

- `[stocks_on_the_move, p.100]` — Clenow's 200-day SMA as canonical
  trend-regime filter (PRIMARY). Empirically: signal is binary-active
  in correct phase, gross per-trade is real, but slope smoothing kills
  reactivity on the swing horizon.
- `[trading_systems_methods, p.13-14]` — Kaufman: gold/USD inverse
  coupling. Empirically confirmed (correct sign of edge when active).
  Magnitude insufficient vs gold's persistent drift.
- `[ilmanen_expected_returns, ch.10]` — gold as USD-cycle hedge / safe
  haven. Cited as escape route from GS-5; partially supported (per-trade
  gross 5%+) but cycle frequency too slow.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative_n_trials = 15;
  deflator demonstrably crushing even +0.36 Sharpe at n=6 trades.
- DEAD_ENDS GS-5 (iter 005) — leaves trend-continuation FX framings on
  FRED data open. Iter 015 demonstrates this open path produces a
  qualitatively-correct but quantitatively-insufficient signal.
- DEAD_ENDS GS-14 (iter 014) — corollary verified at macro-generic
  level. Same-macro-clock applies to FX-trend.
- IC-7 (sister 045/046) — gld_long IC-7 candidate space narrowing.
- IC-8 (sister 046/047/050) — n_trials=15 deflator; single pre-committed
  cfg.
- Web — Pukthuanthong & Roll (2011) *J Banking Finance* — gold-USD
  inverse strongest during persistent USD downtrends. Empirically: this
  IS the regime captured (p_active 36-43%; per-trade gross 5%+) but the
  off-regime opportunity cost dominates.
- Web — Capie, Mills & Wood (2005) *J Int Fin Markets, Inst & Money* —
  gold as long-run USD hedge. Confirmed at long-horizon mechanics; not
  a profitable swing/quarterly trading signal alone.

## Next iteration suggestions (priorities updated by iter 015's findings)

iter 015 confirms the macro-generic same-clock corollary — the
gld_long single-stream ceiling at Sharpe ≈ 0.55 is robust across ALL
macro-trend families tested. Two structurally novel directions remain:

1. **(NEW PRIORITY 1) IC-7 composition iter 003 (RSI-MR + SMA200) +
   iter 015 (DXY-trend) on xauusd_intraday** at ρ = −0.07. Highest-
   orthogonality pair the loop has discovered. **Markowitz proportional-
   Sharpe weighting per IC-3** (S_003=+0.24 / S_015=+0.36 → roughly
   40/60 split). Risk: combined Sharpe still bounded by √(S_A² + S_B²) ≈
   0.43 — below intraday bench 1.10 — composition can lift DSR but
   probably not Sharpe edge. Worth testing because (a) cheap (no new
   data), (b) demonstrates whether IC-7 actually unlocks anything when
   ρ is near zero on a real pair.
2. **(PRIORITY 2) CFTC COT non-comm net longs gold** — different family
   entirely (positioning extremes, response-to-macro vs the macro-clock
   itself). Weekly cadence; CFTC legacy reports back to 1986 → full
   gld_long coverage. Cordero (2017) "What COT Tells Us About Gold" + de
   Roon-Nijman-Veld (2000) *J of Finance*. Higher infra cost (CFTC fetch
   + parser) but only direction with structural prior to break gld_long
   ceiling.
3. **(PRIORITY 3) σ_60<σ_252 AND drawdown_60d<10%** (BASE_MEMORY direction
   #2 / vol-regime axis #4) — only relevant if 1 + 2 blocked. Same
   family as iter 011/013, expected hit on +0.55 ceiling.
4. **(DEFERRED) GDX/GLD via NEM proxy** — short window + tracking error;
   weak prior. Skip unless 1-3 all closed.
5. **(DEFERRED) BTC-gold flight-to-quality** — gold-BTC ρ historically
   unstable; weak prior.

iter 016 should pursue priority **#1 (IC-7 003 + 015 xauusd_intraday)**
because it directly tests whether IC-7 pays off when ρ ≈ 0 on a true
pair from this loop's data — a finding that informs ALL future
composition decisions cheaply (no new data fetch).
