# Iteration 001 — Connors RSI(2) < 5 mean-reversion baseline (long-only) on gold

## Hypothesis

After a sharp 2-day pullback inside an established trend, **gold prices
mean-revert within 2-5 trading days**. Operationally: enter long when
RSI(2) drops below 5 (extreme short-term oversold) and exit when the
close crosses back above its SMA(5). The trade is long-only and pure
swing — no leverage, no shorting, no overlay.

This iteration deliberately tests the **simplest possible single-
mechanism baseline** for the gold swing loop. If the simplest
mean-reversion variant cannot beat gold buy-hold, no amount of regime-
switching or ML overlay on a structurally-dead mechanism will rescue
it. Kill the family before extending it.

## Primary citation

`[short_term_trading_strategies, p.74-86]` — Connors & Alvarez (2008)
"Short Term Trading Strategies That Work". RSI(2) is the canonical
2-day mean-reversion signal designed for short-horizon entries; the
authors document multi-decade edge on US-equity ETFs with the exact
RSI(2) < 5 + close > SMA(5) exit rule used here. The book's tests
were on equity index ETFs (SPY, QQQ); applying to GLD/XAUUSD spot
is a structural transfer test.

## Additional citations

- `[trading_systems_methods, p.301-310]` (Kaufman) — short-period RSI
  as oversold filter; documented mean-reversion at 2-3 day horizons
  across precious-metals futures.
- `[advances_fin_ml, p.31-34]` (López de Prado) — cost-realistic backtest
  is the only valid score for any short-hold strategy.
- Web (DEFERRED — no fetch needed for iter 001): Larry Williams' "%R"
  variants and Connors' subsequent "ConnorsRSI" composite are
  follow-ons to this baseline. Test those only after the simple variant
  passes.

## Edge source (one sentence)

XAUUSD buy-hold captures the long-term trend and macro-driven price
appreciation but ignores the **short-term overshoot/correction
oscillation** that follows fear-driven 2-day liquidations; entering
at RSI(2) < 5 and exiting at SMA(5) cross targets exactly that
oscillation, leaving the long-term trend untouched.

## Datasets

- **gld_long** (GLD daily 21.4y): primary OOS dataset — long enough to
  span 2008 GFC, 2011 peak, 2013 collapse, 2018-19 revival, COVID rally.
  Mixed-regime data is the right test for "does MR work outside a
  bull-only window".
- **xauusd_real** (XAUUSD spot daily 6.3y): real-instrument
  cost-realistic dataset. Only 6.3y, all in a strong bull regime
  (2020-2026), so MR is structurally disadvantaged here per
  DEAD_ENDS anti-pattern note.
- **xauusd_intraday** (XAUUSD spot 1h 6.3y): same calendar window
  resampled. **Daily-RSI strategy is computed on a daily resample of
  the 1h bars**, so this dataset effectively becomes a no-op
  duplicate of xauusd_real for this iteration. We include it so the
  scoring runs cross-dataset uniformly; future intraday MR iters
  (e.g., z-score MR on 1h) will use the 1h bars natively.

## Timeframes used

- **Daily** (1d): primary signal computation and entry/exit decisions
- For the **xauusd_intraday** dataset: bars are resampled 1h → 1d
  before signals run; intraday execution for 1h-native MR is deferred
  to a later iteration.

No 30m / 15m / 1m bars needed → no cTrader fetch required.

## Broker tracks targeted

`broker_track: "both"`

This is a **long-only** swing strategy with mean hold 2-5 days, so it
fits both:

- **Track A (Pepperstone XAUUSD CFD)** — XAUUSD spot CFD, 8 bps
  round-trip spread + −1 bps/night swap on long. Mean hold 3 days
  → expected swap drag ~3 bps/trade. Total trade cost ~11 bps.
- **Track B (Inter Internacional GLD ETF)** — GLD ETF, zero brokerage,
  100 bps FX RT, **DARF 15% on positive monthly net profits**. Mean
  hold 3 days fits T+1 settlement; long-only is the natural form.
  DARF cost ~10-15% of CAGR.

Per-track metrics will be reported in `verdict.json`. The "WINNER"
declaration would require Track A primary to clear all 6 conditions;
Track B is reported for comparison.

## Hold-time profile (HARD GATE)

- **Expected mean hold**: 2-5 trading days (Connors literature reports
  ~3 days median for SPY/QQQ; gold may differ)
- **Intraday-only?** No — Connors RSI(2) is a daily-bar swing strategy
- **Swap-free?** No (multi-night holds) — Track A pays ~3 bps/trade swap
- **Hold-time gate (≤ 5 days mean) compliance**: expected pass; gold's
  RSI(2) cluster behaviour might extend hold by 1-2 days vs SPY but
  unlikely to breach 5d. If breached, tier caps at STRONG with
  "swing-extended" tag.

## Kill criteria (pre-committed)

If, at end of testing on the **full** window of all 3 datasets:

- `Sharpe_strategy_net < Sharpe_buyhold − 0.05` on **≥ 2 of 3 datasets**

then the **single-mechanism mean-reversion family is structurally dead
on XAUUSD/GLD** in this loop's universe and goes into `DEAD_ENDS.md`
as gold-specific closure GS-1 ("daily Connors RSI(2) MR fails on
strong-bull and mixed-regime gold; structural"). Subsequent iters will
not test variants of pure short-RSI MR (no parameter sweeps on RSI
period, threshold, or SMA exit length) on the same instrument.

If the strategy partially works (Sharpe edge on 1 of 3 datasets), this
is **PROMISING** and informs the Connors-RSI-with-regime-overlay path
(future iter — likely combined with VIX > 25 macro filter per book
candidate #12).

## Pre-validation screen (mandatory for overlays per IC-6)

Connors RSI(2) is a **single signal**, not an overlay. IC-6 pre-val
screen is therefore **N/A** (the signal is the strategy; there is no
base position to compute correlation against). For comparison:

- Trade entries are sparse (RSI(2) < 5 fires roughly once per 30 days
  on equity ETFs per Connors literature)
- Position is binary 0 or 1 (no continuous overlay)

## Cost model (per track)

### Track A (Pepperstone XAUUSD CFD)

- Spread: **8 bps round-trip** (4 bps per side on entry + 4 bps per
  side on exit)
- Swap long: **−1 bps/night** (pay)
- Weekend Friday-close hold: **3× swap** = −3 bps that night
- Slippage on stops: **5 bps** when triggered (this strategy uses no
  stops; SMA(5) close exit only — slippage modelled at 0)

Mean trade: ~3 nights × −1 bps + 1 weekend per ~5 trades × −3 bps
≈ **−4 bps swap drag per trade**. Plus 8 bps spread → **~12 bps total
cost per trade**.

### Track B (Banco Inter Internacional, GLD ETF)

- Brokerage: 0
- FX RT: **100 bps** round-trip (50 bps per side, applied on each
  position turn)
- ETF EER: 40 bps/yr (already in NAV, no double-count)
- Settlement: T+1 (compatible with mean hold ≥ 2 days)
- **DARF 15%** on positive monthly net profits (allocated to last bar
  of month in backtest)

Mean trade: 100 bps FX + DARF. DARF eats 10-15% of CAGR over the year.

## Expected budget

- **Configs to test: 1** — pre-committed (RSI period=2, threshold=5,
  exit=close>SMA(5), no other knobs). IC-8 compliant: no grid search.
- **Wall-time**: ~3-5 minutes for backtest + gates + report
- **Files to create**:
  - `iterations/001-*/hypothesis.md` (this file)
  - `iterations/001-*/run_backtest.py` (lightweight per-iter simulator)
  - `iterations/001-*/run_benchmarks.py` (one-time benchmark measurement;
    code already used to update `scoring.py`)
  - `iterations/001-*/architecture_note.md` (simulator-arch decision)
  - `iterations/001-*/results.json`
  - `iterations/001-*/verdict.json`
  - `iterations/001-*/final_report.md`

## Implementation plan

1. Lightweight per-iter simulator `run_backtest.py`:
   - Load each dataset via `studies.gold_swing_loop.datasets.load_dataset`
   - Resample 1h → 1d for `xauusd_intraday`
   - Compute RSI(2) and SMA(5) on close
   - Generate position series: enter long at next-bar open when
     RSI(2) < 5 and close < SMA(5); exit at next-bar open when
     close > SMA(5). Position is 0 or +1.
   - Compute gross bar-PnL via `cost_models._bar_pnl` semantics
     (position[t-1] × ret[t])
   - Apply Track A cost model via `apply_pepperstone_costs`
   - Apply Track B cost model via `apply_inter_costs_with_darf`
     (long-only enforced; will pass since position ≥ 0 by construction)
2. Compute per-dataset metrics: Sharpe (annualized), CAGR, MDD,
   mean hold days, trade count
3. Run 7-gate battery:
   - G1 PBO via CSCV on rolling-window subsamples (single config so
     PBO is degenerate — report N/A as PASS by convention since no
     overfitting risk on single pre-committed config)
   - G2 DSR with `cumulative_n_trials = 1` (this is iter 001's first
     and only test)
   - G3 Walk-forward 8 windows
   - G4 OOS 70/30 Sharpe > 0
   - G5 FWD post-2022 Sharpe > 0
   - G6 Bootstrap 99.9% CI low > 0
   - G7 Cross-lib: hand-roll a numpy-pure version + verify ±3pp CAGR
4. Score via `scoring.score_strategy`
5. Check hold-time gate (mean_hold ≤ 5 days)
6. Write `results.json`, `verdict.json`, `final_report.md`
7. Update `BASE_MEMORY.md` (frontmatter + iteration log + top-K)
8. If FAIL with structural finding → append to `DEAD_ENDS.md`
