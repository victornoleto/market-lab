# Iteration 002 — Final Report

## Verdict

❌ **FAIL** (score **11/100**, winner_conditions_met=False, hold_time_gate=FAIL — moot anyway)

Donchian-20/10 channel breakout (canonical "Turtle System 2 lite") is
**structurally dead on gold** across all three datasets and both broker
tracks. The pre-committed kill criterion (`Sharpe_strategy_net <
Sharpe_buyhold − 0.05` on ≥ 2/3 datasets) **triggers on 3/3 datasets**.

Combined with iter 001's GS-1 closure (short-RSI MR), this iteration
closes the **second** of the two opposite single-mechanism families.
**Both pure entry-direction families (mean-reversion AND trend-follow)
underperform gold buy-hold on a risk-adjusted basis** when run as
single-asset, single-mechanism, no-filter strategies — informing a
new structural dead-end **GS-3** ("simple symmetric entry-direction
strategies on single-asset gold are dominated by buy-hold's drift").

## Headline metrics (Track A — Pepperstone CFD, NET of costs)

| dataset | Sharpe (bench Δ)         | CAGR (bench Δ)          | MDD (bench Δ)         | gates | mean hold |
|---|---|---|---|---|---|
| gld_long         | −0.20 (Δ −0.88)  | −4.26% (Δ −15.58 pp) | 73.97% (Δ +28.4 pp) | 3/7 | 16.31 d |
| xauusd_real      | +0.24 (Δ −0.80)  | +2.79% (Δ −17.14 pp) | 28.16% (Δ +7.8 pp)  | 4/7 | 16.93 d |
| xauusd_intraday  | +0.24 (Δ −0.86)  | +2.76% (Δ −17.43 pp) | 28.84% (Δ +4.4 pp)  | 4/7 | 16.91 d |

Δ vs benchmark = strategy − buy-hold. Negative Δ on all three datasets
on Sharpe AND CAGR. **gld_long MDD doubled vs buy-hold** (74% vs 46%) —
the bidirectional Donchian got destroyed by long bull-rally counter-shorts
during 2007-2011 and 2018-2024. Mean hold ~17 days places this firmly in
"swing-extended" territory (HARD GATE failed regardless of score).

## Headline metrics (Track B — Inter ETF GLD, long-only, NET of FX + DARF)

| dataset         | Sharpe | CAGR    | MDD    | n_trades |
|---|---|---|---|---|
| gld_long        | −0.21  | −3.45%  | 72.86% | 123      |
| xauusd_real     | +0.13  | +0.97%  | 29.22% | 39       |
| xauusd_intraday | +0.13  | +0.94%  | 29.89% | 39       |

Track B is consistent with Track A directionally but the FX cost cliff
(GS-2) eats most of the small positive xauusd Sharpe, dropping it from
0.24 (Track A) to 0.13 (Track B). On gld_long, Track B is slightly
LESS bad than Track A only because long-only avoids the catastrophic
short-side drawdowns during bull rallies — but absolute return is still
negative.

## Score breakdown

| criterion                           | points | max | detail |
|---|---|---|---|
| 1. Sharpe edge                      | **0**  | 25 | datasets beating bench+0.10: **0/3** |
| 2. Gates                            | **6**  | 25 | per-dataset 3/4/4 vs thresholds 5/4/4; cross-dataset bonus FAIL (gld below threshold) |
| 3. DSR (cumulative n_trials=2)      | **0**  | 15 | worst p = **0.924** on gld_long (random noise; even xauusd p=0.46) |
| 4. CAGR floor (≥ 0.8 × bench)       | **0**  | 15 | datasets passing: **0/3** |
| 5. MDD ceiling (≤ bench + 5pp)      | **5**  | 15 | datasets passing: **1/3** (only intraday at 28.8% < 29.4% ceiling) |
| 6. Robustness                       | **0**  | 5  | not computed for FAIL-tier |
| **Total**                           | **11** | 100+5 | tier: **FAIL** |
| Hold-time gate (6th condition)      | **FAIL** | — | mean **16.31 d** on gld_long (cap 5 d) |

## Configuration tested

```python
config_id = "donchian_20_10_turtle"
params = {
    "entry_lookback": 20,
    "exit_lookback":  10,
    "long_only_track_a": False,   # bidirectional
    "long_only_track_b": True,    # ETF long-only enforced
    "swap_free": False,           # multi-night swing
}
cumulative_n_trials = 2  # iter 001 (1) + this iter (1)
```

## What worked / what didn't

**What "worked":**
- The strategy **does** generate small positive returns on the bull-only
  xauusd datasets (Sharpe 0.24, CAGR 2.8%) — meaning the Donchian
  breakout signal IS picking up *some* of gold's persistent-trend regime.
  But that small alpha is dwarfed by the cost drag and chop-loss cycles.
- The bidirectional implementation is mechanically sound: state machine
  validated by 7/7 unit tests, no look-ahead bias confirmed.
- Track B (long-only) marginally outperforms Track A on the catastrophic
  gld_long dataset — confirming bidirectional Donchian on mixed-regime
  gold is a **structural mistake** because shorts get eaten by the
  bull-rally tail risk.

**What didn't:**
- **The exit rule is too slow on gold's choppy regimes.** On gld_long
  (21.4y mixed regime), 232 trades over 21 years means ~11 trades/yr
  but the strategy is in the wrong direction or whipsawed on most of
  them. The 73.97% MDD vs 45.6% buy-hold MDD is the smoking gun —
  the strategy AMPLIFIED gold's natural drawdowns by being bidirectional
  on a non-mean-reverting asset.
- **The entry rule (close > 20-day high) ALSO has issues.** On bull
  regimes (xauusd_real / xauusd_intraday), the 20-day high triggers
  AFTER the breakout move has already played out, so the strategy
  enters at relative tops and gets stopped on the next correction.
- **Both directions of GS-1's failure mode are confirmed**: MR entered
  at oversold + exited too early (iter 001); trend-follow entered too
  late + exited at chop (iter 002). The structural defect is the
  **mismatch between simple-mechanism timeframes and gold's regime
  structure** (mix of trend + mean-rev + macro shocks within the
  21.4-year window).
- **G7 cross-lib check**: differences are within ±3pp tolerance because
  the numpy reference doesn't apply Pepperstone costs (just gross PnL ×
  position). The gap (~2.4pp on each dataset) IS the cost drag —
  consistent with ~280 bps/yr cost burden, slightly above hypothesis
  estimate of 302 bps/yr.

**The verdict on the entry-vs-exit question (the iter's primary
hypothesis):** Both sides of GS-1 are defective on a single-mechanism
basis. Neither MR nor trend-follow alone solves gold day/swing —
**something more structural is required** (regime filter, multi-mechanism
composition, or macro-overlay).

## Main lesson (for future iterations)

**Single-mechanism, single-asset, single-direction-family strategies
do NOT exhibit a structural edge over gold buy-hold on day/swing
horizons.** Both iter 001 (MR) and iter 002 (trend-follow) underperform
buy-hold on Sharpe by −0.8 to −1.3 across all three datasets. Gold's
regime structure (multi-year persistent trends interleaved with
multi-month chop) is **not exploitable by a single-cycle indicator**
without a regime-aware filter.

The path forward is now clearly forked:

1. **Add a regime filter** (Connors' own fix per
   `[short_term_trading_strategies, p.105-118]`): MR or trend-follow
   gated by SMA(200) or VIX-regime. **Direction #3 in BASE_MEMORY.**
2. **Pivot to a different family** (macro overlay — DXY, real yields):
   different signal source, low turnover, Track-B viable.
   **Direction #2 in BASE_MEMORY.**
3. **Compose two uncorrelated single-mech results via Markowitz
   weighting** (per IC-7) — but iter 001 + iter 002 are BOTH negative
   on most datasets, so there's nothing to compose yet. Tabled.

## Structural dead-ends discovered

### GS-3 — Symmetric simple-mechanism entry-direction strategies on single-asset gold are dominated by buy-hold's drift

*(iter 001 + iter 002 — both opposite single-mechanism families fail)*

**Empirical evidence**:

| family | iter | gld_long Sharpe | xauusd_real Sharpe | xauusd_intraday Sharpe |
|---|---|---|---|---|
| MR (RSI(2)<5 + SMA exit)        | 001 | +0.04 | −0.23 | −0.20 |
| Trend (Donchian-20/10)          | 002 | −0.20 | +0.24 | +0.24 |
| **Buy-hold (benchmark)**        |  —  | **+0.68** | **+1.04** | **+1.10** |

Neither family captures more than ~25% of buy-hold's risk-adjusted
edge on the bull-only xauusd window, and BOTH lose money on the mixed
gld_long window.

**Why structural** (not parameter-tweakable):

1. Single-mechanism timing has no information advantage over buy-hold's
   long-bias drift on a persistently-trending asset like gold.
2. Adding parameter sweeps (entry lookback ∈ {10, 15, 20, 25, 30}, exit
   lookback ∈ {5, 7, 10, 15}) cannot rescue this — the structural defect
   is the **lack of a regime gate**, not the parameter tuning.
3. IC-8 (DSR drains fast) means parameter-sweeping these single-mechs is
   *negative-EV* anyway — DSR p-value would only worsen with each trial.

**Closes**: any single-mechanism, single-asset, single-direction-family
day/swing strategy on gold without a regime filter. Specifically:
- All RSI/Bollinger/Stochastic short-period MR variants
  (closes "Strategy menu" candidates 5-8 from BASE_MEMORY)
- All Donchian/EMA-cross/momentum-channel breakout variants without
  regime gating (closes candidates 1-2, 11)
- All single-cycle-indicator-only strategies (closes 6, 7, 13, 14)

**How to escape** (informs iter 003+):

- **Layer a regime filter** (e.g., SMA(200) trend filter for MR; VIX
  flight-to-quality gate for breakout; macro driver as input).
  This is Connors' own published fix and the most-cited resolution.
- **Switch to fundamentally-different signal source** (macro: DXY,
  real yields, COT positioning).
- **Compose multiple single-mech streams via Markowitz** (per IC-7) —
  needs ≥ 2 streams with positive Sharpe first, currently 0.

### GS-3 sub-finding: Bidirectional trading on gld_long is a trap

The 73.97% MDD on Track A's gld_long (vs 45.6% buy-hold) is **double
the natural drawdown**. Gold is a long-bias asset with bull-rally tails;
naive short trades (without macro/regime gating) get destroyed by these
tails. **Closes**: bidirectional single-mech on gld_long unless paired
with a regime filter that turns shorts off during bull regimes.

## Citations used

- `[trend_following, Covel]` — Donchian channel-breakout philosophy
- `[stocks_on_the_move, p.81]` — Clenow ATR-scaled trend (analogous to
  Donchian channel logic)
- `[trading_systems_methods, Kaufman, ch.20]` — channel breakout systems
  documentation; "20/10" as standardized fast-Turtle variant
- `[short_term_trading_strategies, p.105-118]` (Connors) — own
  documentation that single-mech MR fails on commodities; recommends
  trend-filter (cited as iter 003 candidate)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest validation
- `[advances_fin_ml, p.222-223]` — DSR/PSR with cumulative n_trials
- `[advances_fin_ml, p.196-202]` — bootstrap CI for Sharpe (G6)

## Cross-loop lessons confirmed

- **IC-8 (DSR drains fast)**: pre-committed single config; cumulative
  n_trials advanced 1→2. Worst-case DSR p-value on this iter is
  **0.92** on gld_long — the candidate is statistically indistinguishable
  from random walk regardless of trial count. Confirms that parameter
  sweeps on this base would be wasted budget.
- **IC-4 (modulation saturates)**: Iter 001 was MR with one direction
  of "modulation" (SMA exit); iter 002 is its symmetric trend-follow
  with channel exit. Different mechanism, same negative ceiling — the
  base-effect ceiling is **negative or zero** on this asset class for
  single-mech, so modulation has nothing to amplify. Pivots are required,
  not modulations.
- **GS-2 cost-cliff confirmed again**: 232 trades/21y = 11 trades/yr on
  gld_long Track A, but Track B's 100 bps FX RT × 123 trades = 12 300
  bps total drag. Same dynamics as iter 001's 13 500 bps drag.

## Next iteration suggestions (2-3 structurally different directions)

The single-mech direct-entry families (MR + trend-follow) are now
empirically closed. Iter 003 must pick from one of these:

### Iter 003 candidate A — MR with 200d-SMA trend filter (Connors' own fix)

**Direction #3 from BASE_MEMORY's promising list.** Layer GS-1's RSI(2)<5
entry with a `close > SMA(200)` precondition — fight pullbacks ONLY in
established uptrends, ride the trend in downtrends. Citation:
`[short_term_trading_strategies, p.105-118]` Connors' own published
variant. Mean hold likely 5-10 days (still swing-extended on gld_long
where downtrends are long). Track A only (high turnover).

This **directly tests** GS-3's escape hatch #1. Cheapest validation.

### Iter 003 candidate B — Macro-overlay (DXY z-score)

**Direction #2 from BASE_MEMORY.** Long gold when DXY 60d EMA falling
AND z<−1 (using cached usdcad/usdchf/usdjpy proxies; DXY itself not
cached). 4-8 trades/yr → **Track-B viable** per GS-2 cost-cliff rule.
Tests fundamentally-different signal source. Citation:
`[ilmanen_expected_returns, ch.10]`, Bauer-Mertens 2018 FRBSF EL on
real-rate → gold link.

This **directly tests** GS-3's escape hatch #2. Slowest to test but
opens Track-B path (the only one viable for Inter ETF reactivation).

### Iter 003 candidate C — Regime-aware composition (deferred)

Markowitz combo of (iter 001 + iter 002) — currently NOT viable
because both base streams are net-negative. **Tabled** until ≥ 2
positive-Sharpe streams exist. Per IC-7, composition compounds DSR
only when components are individually positive. Requires iter 003 +
004 to produce two independent winners first.

### Recommended iter 003 order

**Pick A first.** It's:
1. The cheapest to implement (one line of code added to iter 001's
   `connors_rsi2_signal` function)
2. The most-cited fix (Connors documents it himself)
3. Highest-info — directly tests whether GS-1's failure was the
   ENTRY (no, MR is fine) or the LACK OF REGIME GATE (yes, this iter
   would prove it)

If A also fails → strong signal that single-asset gold is genuinely
unexploitable on day/swing, must pivot to macro overlay (B) or accept
swing-extended STRONG-tier ceiling.
