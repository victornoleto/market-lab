# Iteration 018 — COT z-score variant (rolling 156w z of NL_comm − NL_small)

## Hypothesis

Iter 017 closed the canonical Briese/Ruggiero **stochastic** COTI
(70/30/50/156w) on gold (Sh +0.137 gld_long, +0.310 xauusd_real, NEAR_FAIL
28). The Briese stochastic is min-max-normalized — extreme weeks where
commercial net-long blows past prior tails get clipped at 100, so the
strategy treats a "+3 σ commercial bull pressure" identically to a
"+1 σ commercial bull pressure" once both saturate the 156w max.

**Replace the stochastic with a Gaussian z-score on the same data**:
rolling 156w z-score of `(NL_comm − NL_small)` (where NL = positions_long
− positions_short). z is unbounded — extreme positioning weeks register
their full magnitude, plausibly generating fewer-but-better trade
signals. Same data, same window, different transform → **structurally
new test of whether Briese's tail-clipping is the binding ceiling**.

Sign convention (Briese's canonical directionality, Kaufman p.639-640):
high z(NL_comm − NL_small) = commercials bullish relative to small
traders = "smart money long" → **enter LONG on z > +1.0**, exit when
`z < 0` (positioning normalized) OR `30d max hold` cap.

Note on BASE_MEMORY phrasing: the priority-1 entry says "enter when
z < −1.0", which reverses Briese's hedging-pressure logic
([de Roon-Nijman-Veld 2000] — commercials bullish ⟹ small traders
bearish ⟹ NL_comm − NL_small ≫ 0 ⟹ z ≫ 0). I treat that as a
phrasing/sign typo and use **z > +1.0** entry — this is the directional
formulation faithful to both Kaufman and de Roon-Nijman-Veld.

## Primary citation

`[trading_systems_methods, p.639-640]` — Kaufman documents Briese COT
Index + Ruggiero rule with the 156w window; explicitly notes z-score
as the canonical alternative when "the stochastic squeezes recent
extremes against historical tails".

## Additional citations

- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (n=18 this iter)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (reuse iter 017's spread+swap model)
- de Roon, Nijman, Veld (2000) *Journal of Finance* — "Hedging Pressure
  Effects in Futures Markets" — z-score of commercial net positioning as
  primary positioning measure in commodity futures (gold, copper, soybeans)

## Edge source

XAUUSD buy-hold misses **regime-conditional positioning extremes**:
gold's drift has long stretches (2013-2018) where buy-hold is roughly
flat but commercial-net-long extreme weeks identify selectively
profitable swing entries. The Briese stochastic blunts that signal
on the right tail; z-score restores it.

## Datasets

- **PRIMARY**: `gld_long` (GLD daily 21.4y, 2004-11-18 → 2026-04-15)
  - longest available; spans 2008 GFC, 2011 peak, 2013-2018 stagnation,
    2019+ revival → most regime variety to test signal robustness
  - COT data available since 1986; clean overlap with full price history
- **CORROBORATING**: `xauusd_real` (XAUUSD daily 6.3y, 2020-01-02 → 2026-04-17)
  - actual instrument for Track A; relaxed gate check (G6 + G2 < 0.20)
- `xauusd_intraday` not used — COT is weekly, intraday adds no signal granularity

## Timeframes used

- **1d** only on gld_long + xauusd_real (COT is weekly, daily resampling
  is the natural granularity for swing entries; intraday TF irrelevant)

## Broker tracks targeted

- **Track A (Pepperstone XAUUSD CFD)**: long-only (matches signal direction);
  spread 8 bps RT + swap −1 bps/calendar night long. Mean hold ~15-25d
  expected ⟹ ~15-25 swap nights drag, ~15-25 bps cumulative night cost
  per trade.
- Track B not modeled this iter (Inter ETF would clean DARF model but
  the underlying signal is identical; if WINNER, future iter rescores).

## Hold-time profile

- **Declared track**: `medium_swing` (10 ≤ mean_hold_days ≤ 30)
- **Expected mean hold**: ~15-25 days (z-score signal is selective; with
  z>+1.0 entry threshold and z<0 exit, typical regime cycle ≈ 4-6 weeks)
- Same as iter 017 (28-29d observed); z-score variant should produce
  similar hold profile or slightly shorter (more selective entry).

## Kill criteria (pre-committed)

If ANY of these fire at end of STAGE 3, hypothesis is FALSIFIED and
this closes the COT-z-standalone path (GS-18):

1. **Kill #1 (catastrophic)**: gld_long Sharpe ≤ 0.0 → COT z-score is
   informationless on gold; closes z-variant family unconditionally.
2. **Kill #2 (no progress vs canonical)**: gld_long Sharpe ≤ 0.30 AND
   xauusd_real Sharpe ≤ 0.40 → z-score does not lift Briese's
   compressed-tail Sharpe (canonical was 0.137 / 0.310); standalone
   COT-positioning family ceiling on gold ≈ 0.3 Sh regardless of
   transform → closes COT-standalone path, leaves IC-7 003+017
   composition (BASE_MEMORY priority 2) as next move.
3. **Kill #3 (declaration mismatch)**: observed mean_hold_days < 10 OR > 30
   on either dataset → declaration error, downgrade to NEAR_FAIL.

If the strategy *does* lift Sharpe meaningfully (gld_long > 0.40 +
xauusd_real > 0.50), it becomes the next IC-7 composition base — even
if standalone still trails buy-hold by Sharpe Δ.

## Pre-validation screen

Not an overlay (standalone signal); IC-6 pre-val screen N/A. The
"correlation diagnostic vs prior iters at consistent freq" (process
correction from GS-16) IS computed in Stage 5 to inform IC-7 path.

## Cost model

**Track A (Pepperstone XAUUSD CFD)** (reuse iter 017's `apply_costs`):

- spread 8 bps round-trip, split half on entry / half on exit
- swap −1 bps per calendar night long (3× swap on Friday close)
- no commission (built into spread)
- intraday-close not applicable (medium_swing hold)

DARF not applied (offshore SCB Bahamas Tier-3, mandate §4.8).

## Expected budget

- **Configs to test**: 1 (single cfg, IC-8 — z>+1.0 entry, z<0 exit,
  156w window, 1w lag, 30d max hold, 8 bps spread, −1 bps swap)
- **Wall-time**: ~5 min (small dataset, single cfg, no grid)
- **Files to create**:
  - `iterations/018-*/hypothesis.md` (this file)
  - `iterations/018-*/test_zscore.py` (TDD)
  - `iterations/018-*/run_backtest.py` (reuses iter 017's helpers, swaps signal generator)
  - `iterations/018-*/score_and_verdict.py`
  - `iterations/018-*/results.json`
  - `iterations/018-*/verdict.json`
  - `iterations/018-*/final_report.md`

## Implementation plan

1. Write `test_zscore.py` with TDD tests for `cot_zscore_signal` (rolling
   z-score endpoints, lag handling, entry/exit/timeout state machine).
2. Implement `cot_zscore_signal` in `run_backtest.py`. Reuse iter 017's
   `apply_costs`, `compute_metrics`, `deflated_sharpe_p_value`,
   `bootstrap_ci_low`, `walk_forward_split`, `cross_lib_check`,
   `load_cot`, `load_prices` verbatim (well-tested, correct).
3. Run backtest on gld_long + xauusd_real, write `results.json`.
4. Run `score_and_verdict.py` → score_strategy_v2 with declared_primary=
   gld_long, declared_corroborating=[xauusd_real]. Compute hold-time
   gate. Write `verdict.json`.
5. Compute correlation diagnostic vs iter 003 (RSI MR), iter 011
   (vol-regime), iter 015 (DXY trend), iter 017 (canonical Briese) for
   future IC-7 path inputs.
6. Write `final_report.md` honestly; update `BASE_MEMORY.md` (iteration
   log, top-K, total_iterations=18, cumulative_n_trials=18) and
   `DEAD_ENDS.md` (GS-18 if structural closure).
