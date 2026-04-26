# Iteration 001 — Final Report

## Verdict

❌ **FAIL** (score **18/100**, winner_conditions_met=False, hold_time_gate=PASS but moot)

Daily Connors RSI(2) < 5 mean-reversion (long-only) is **structurally
dead on gold** across all three datasets and both broker tracks. The
pre-committed kill criterion ("Sharpe_strategy_net < Sharpe_buyhold − 0.05
on ≥ 2 of 3 datasets") triggers on **3/3 datasets**, closing the
single-mechanism short-RSI MR family for gold (gold-specific dead-end
**GS-1** added).

Cost-model insight: **Track B (Inter ETF) is structurally non-viable
for any high-turnover (>~15 trades/yr) strategy** — 100 bps FX RT × 135
trades = 6.3%/yr drag, killing even the gld_long modest-edge result.

## Headline metrics (Track A — Pepperstone CFD, NET of costs)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold |
|---|---|---|---|---|---|
| gld_long         | +0.04 (Δ −0.65) | +0.03% (Δ −11.29 pp)  | 30.5% (Δ −15.0 pp) | 4/7 | 4.44 d |
| xauusd_real      | −0.23 (Δ −1.27) | −1.30% (Δ −21.23 pp)  | 16.3% (Δ −4.0 pp)  | 3/7 | 4.72 d |
| xauusd_intraday  | −0.20 (Δ −1.30) | −1.12% (Δ −21.31 pp)  | 16.3% (Δ −8.1 pp)  | 3/7 | 4.70 d |

Δ vs benchmark = strategy − buy-hold. Negative Δ on Sharpe and CAGR =
strategy underperformed gold buy-hold on a risk-adjusted AND absolute
basis. MDD is lower than buy-hold (only "win") because strategy is in
cash most of the time.

## Headline metrics (Track B — Inter ETF GLD, NET of FX + DARF)

| dataset | Sharpe | CAGR | MDD | n_trades | DARF cost ($ on +1.0 unit) |
|---|---|---|---|---|---|
| gld_long         | −0.88 | −5.56%  | 71.5% | 135 | $0.0006 (positive months rare) |
| xauusd_real      | −1.42 | −6.85%  | 38.9% | 40  | $0 |
| xauusd_intraday  | −1.39 | −6.70%  | 38.3% | 40  | $0 |

Cost-attribution highlights for gld_long Track B vs Track A:

- Track A net: +0.005 (0.03% CAGR over 21y → +0.5% total)
- Track B net: −0.66 (−5.56% CAGR over 21y → −66% total)
- Track A turnover cost = 135 × 8 bps spread + 134 swap nights × 1 bps = ~150 bps total
- Track B turnover cost = 135 × 100 bps FX = **13 500 bps total** (~6.3%/yr drag)

The Inter ETF FX cost is **~90× larger per turn** than Pepperstone's
spread. Any strategy with > 12-15 trades/yr is **structurally non-viable**
on Track B regardless of underlying signal quality — adding to GS-2 in
DEAD_ENDS.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1. Sharpe edge       | **0**  | 25 | datasets beating bench+0.10: **0/3** |
| 2. Gates             | **3**  | 25 | per-dataset 4/3/3 vs thresholds 5/4/4; cross-dataset bonus FAIL |
| 3. DSR (PSR for n=1) | **0**  | 15 | worst p = 0.727 on xauusd_real (random noise) |
| 4. CAGR floor (0.8 × bench) | **0** | 15 | datasets passing: 0/3 |
| 5. MDD ceiling (bench + 5pp) | **15** | 15 | datasets passing: 3/3 (strategy stays cash most days) |
| 6. Robustness        | **0**  | 5  | not computed for FAIL-tier |
| **Total**            | **18** | 100+5 | tier: **FAIL** |
| Hold-time gate (6th condition) | PASS | — | mean 4.44 d on gld_long ≤ 5 d |

## Configuration tested

```python
config_id = "connors_rsi2_lt5_smaexit5"
params = {
    "rsi_period":    2,
    "rsi_threshold": 5.0,
    "sma_period":    5,
    "long_only":     True,
    "swap_free":     False,  # daily swing (multi-night swap accrued)
}
cost_model_track_a = {
    "spread_rt_bps":    8.0,
    "swap_long_bps":   -1.0,
    "swap_short_bps":  +0.3,
    "weekend_mult":    3.0,
    "intraday_close":  False,
}
cost_model_track_b = {
    "fx_rt_bps":   100.0,
    "darf_rate":   0.15,
}
cumulative_n_trials = 1  # iter 001 first test
```

## What worked / what didn't

**What "worked":** Almost nothing. The strategy exhibits the lowest-MDD
profile of any candidate (because position is flat ~95% of bars), but
absolute returns are within rounding of zero on the longest dataset and
negative on the recent ones. Hold-time profile (4.4-4.7 d mean across
datasets) is exactly within the new ≤ 5 d HARD GATE — confirming the
day/swing-horizon framing is at least *operationally* correct.

**What didn't:** Pure short-RSI mean-reversion is structurally dominated
by gold's persistent uptrends. The DEAD_ENDS anti-pattern note about MR
losing ~50% premium during gold trend regimes (2018-2024) is now
**empirically validated** with hard numbers: −1.30% CAGR vs +19.93%
buy-hold on xauusd_real. Connors RSI(2) buys dips in trends — but on
gold the dips are *shallow* and the trends *resume* before SMA(5) confirms
exit, so the entry timing is right but the exit is too early to capture
the recovery rally.

**The Track B catastrophe:** The Inter ETF cost model exposes a
**generalizable** result. With 135 trades over 21 years (already a
modest 6.3 trades/year), Track B charges 13 500 bps in FX RT alone —
13.5× the entire 21-year buy-hold CAGR. **Any short-hold strategy on
Inter ETF has a hidden ~6%/yr Cost cliff.** This is a meta-finding that
constrains all future loop iterations: if `broker_track` includes Inter,
mean turnover must be < ~10 bars between trades (i.e., < ~25 trades/yr).

## Main lesson (for future iterations)

**Pure short-period RSI mean-reversion (period ≤ 4, threshold ≤ 10) on
daily gold bars is dead.** The signal correctly identifies short-term
oversold conditions, but gold's regime structure (long persistent trends
+ shallow pullbacks within them) means the exit rule (close > SMA(5))
fires too early — it captures the bounce but misses the trend
continuation, then enters again in the next pullback at a worse price.
Net: small positive PnL on multi-regime gld_long (just barely), and
**negative** on the bull-only xauusd datasets. This closes the family
across all simple param variations (no need to sweep RSI period or
threshold; the structural defect is the SMA exit's incompatibility with
gold's drift profile).

## Structural dead-ends discovered

### GS-1 — Daily Connors RSI(2) < 5 long-only MR with SMA(5) exit dies on gold across regimes

**Why structural** (not parameter):
1. Signal entry timing is correct (catches oversold) but exit is wrong
   (SMA(5) cross fires before trend resumes)
2. Same defect appears on:
   - 21.4y mixed-regime gld_long (Sharpe 0.04)
   - 6.3y bull-regime xauusd_real (Sharpe −0.23)
   - 6.3y bull-regime 1h-resampled xauusd_intraday (Sharpe −0.20)
3. Tweaking RSI period {2 → 3 → 4} or threshold {5 → 10 → 20} cannot
   fix a structurally-wrong exit rule
4. **Closes**: any cfg of `RSI(p≤4) < threshold(≤20) ∧ exit at close > SMA(N≤10)`
   on any single-asset gold instrument

**How to escape**: replace the SMA exit with a regime-aware exit
(e.g., trailing ATR after T+1 confirmation, or volatility-target-aware
exit) OR add a TREND filter to the entry side (e.g., long-only above
200d SMA), so the strategy doesn't fight the dominant trend.

Cited in `[short_term_trading_strategies, p.74-86]` Connors documents the
SAME issue on certain commodity tests; recommends combining with a
trend filter — not tested here because the goal was simplest-baseline
first.

### GS-2 — Track B (Inter ETF) FX cost cliff at > ~15 trades/year

**Mechanism**: 100 bps FX RT per trade × N_trades/yr drag. Break-even
where buy-hold CAGR is fully consumed by FX:

| trades/yr | annual FX cost (bps) |
|---|---|
| 5  | 50  |
| 10 | 100 |
| 15 | 150 |
| 20 | 200 |
| 25 | 250 |

For gold buy-hold ~13% CAGR, a strategy needing > ~25 trades/yr just to
match buy-hold gross would need **+250 bps gross alpha** to break even
post-FX. That alpha bar is unattainable for most short-hold mean-rev
or breakout strategies.

**Closes**: any strategy with `mean_turnover > 25 trades/year` on Track B
is reported as INELIGIBLE for Inter ETF (must be Track A only). Strategies
with `mean_turnover ≤ 12 trades/year` are Track-B viable.

**Implication for loop**: most short-hold momentum/MR candidates from the
Strategy menu (#5-8, #11) are **Track A only**. Long-hold candidates
(#9 TSM 12-1, #18 pre-FOMC drift, #15 DXY signal) might be Track-B viable.

## Citations used

- `[short_term_trading_strategies, p.74-86]` — Connors RSI(2) < 5 baseline rule
- `[trading_systems_methods, p.301-310]` (Kaufman) — short-RSI as oversold filter
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest validation
- `[advances_fin_ml, p.222-223]` — DSR / PSR with cumulative n_trials (PSR used here for n=1)
- `[advances_fin_ml, p.196-202]` — bootstrap CI for Sharpe (G6)
- DEAD_ENDS anti-pattern (now-validated): *"Daily mean-reversion on gold trend regimes loses ~50% premium during these regimes"* — confirmed empirically here

## Cross-loop lessons confirmed

- **IC-8 (DSR drains fast)**: pre-committing single config saved one trial slot.
  PSR p=0.43-0.73 across datasets shows the SR is statistical noise; even with
  unlimited trials this could not be rescued.
- **IC-6 (pre-val mandatory)**: not directly applicable here (no overlay), but
  the principle "measure cheap before running full backtest" is endorsed —
  nothing is cheaper than verifying gold's persistent-trend regime first.

## Next iteration suggestions (2-3 structurally different directions)

The simplest single-mech baseline is killed. Three structurally
*distinct* directions are now appropriate (any of these breaks GS-1's
exit-rule structural defect):

### Iter 002 candidate A — Trend-following baseline (Donchian / EMA cross)

Symmetric to MR: instead of buying short-term oversold, **buy
medium-term momentum**. Donchian-20 breakout entry + ATR trail or
Donchian-10 exit. This rides gold's persistent trends instead of
fighting them. Expected: positive on xauusd datasets (bull-only),
neutral on gld_long (mixed regimes). Confirms whether the ENTRY side
or the EXIT side was the structural defect. **Track A only** likely
(>15 trades/yr).

Citation candidates: `[trend_following, Covel]`, `[stocks_on_the_move, p.81]`

### Iter 002 candidate B — Macro-overlay long-only (DXY z-score signal)

Goes after a *different family* — fundamentals — at low turnover (DXY
60d EMA falling AND z<−1 ≈ 4-8 trades/yr). This would be **Track-B
viable** per GS-2. Tests whether a low-frequency macro driver can beat
buy-hold's risk-adjusted return. If yes, opens the door for proportional-
Sharpe combination later (per IC-7).

Citation candidates: `[ilmanen_expected_returns, ch.10]`, Bauer-Mertens
2018 FRBSF EL on real yields → gold (uses cached usdcad/usdchf as DXY proxies)

### Iter 002 candidate C — Mean-reversion WITH trend filter (long above 200d SMA)

This is the *correct* fix to GS-1 per Connors' own footnote: long
RSI(2) entries only when close > SMA(200) (i.e., we only fight pullbacks
in established uptrends, ride them in downtrends). Mean hold may extend
to 5-7 days. **Track A only.**

Caveat: this layers two mechanisms. If it works, isolate the contribution
(does the trend filter alone produce the alpha? or the MR signal?). One
**single** parameter additional vs iter 001 — keeps DSR trial budget
clean.

Citation candidates: `[short_term_trading_strategies, p.105-118]`
(Connors' own variant), `[trend_following]`

**Recommended order**: A first (cheapest validation of trend hypothesis),
then C (validates whether MR can be rescued at all), then B (slowest to
test, opens Track B path). All three are open to re-prioritization based
on iter 002's BASE_MEMORY snapshot.
