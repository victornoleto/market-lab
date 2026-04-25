# Iteration 071 — Add SPY short-term mean-reversion 3rd stream to iter 064 (Connors-Alvarez RSI(2) + Chan p.95 momentum filter)

## Hypothesis

Iter 064 (TOP-K #1 STRONG 90, ties iter 069 + iter 070) is a 2-leg
convex combo `0.90·r_046 + 0.10·r_qqqt` whose 90 ceiling is provably
*not* due to regime-classifier choice (iter 068/069/070 closed both
binary-equity-vol and continuous-macro-orthogonal axes at 90).

**Empirical pattern across iters 064/068/069/070**: both r_046 (risk-
parity vol-managed stack) and r_qqqt (Faber 200d-SMA on QQQ) have
HIGHER conditional Sharpe in stress than calm — i.e., both legs are
structurally **defensive**. The composition lacks a calm-aggressive
complement whose conditional Sharpe ordering is OPPOSITE.

This iteration adds a **third stream** with the structurally inverse
profile: a short-term mean-reversion (RSI(2)) buy-the-dip strategy on
SPY, gated by the 200-day SMA momentum filter. Per Chan
`[algo_trading_chan, p.95, ch.4]` the momentum gate ensures the
strategy is OFF in stress regimes (SPY < SMA200) where dip-buying
compounds losses, and ON in calm/bull regimes (SPY > SMA200) where
1-3 day dips driven by liquidity demands reliably revert. Per Chan
`[p.153-154, ch.6]` mean reversion and momentum are *explicitly
complementary* in a diversified portfolio.

```
SPY_t-1, SMA200_t-1, RSI2_t-1                 # all at t-1, no peek
gate[t]   = (SPY[t-1] > SMA200[t-1])            # Chan p.95 momentum filter
buy[t]    = gate[t] AND (RSI2[t-1] < th)        # Connors-Alvarez 2009
sell[t]   = (SPY[t-1] > SMA5[t-1])              # Connors-Alvarez exit rule
pos[t]    = state-tracking long iff buy w/o subsequent sell
r_mr[t]   = pos[t] · r_spy[t] + (1-pos[t]) · rf_d − cost[t]
cost[t]   = 5bp · |pos[t] − pos[t-1]|
```

3-leg blend (proportional reduction preserving iter 064's 9:1 ratio
between r_046 and r_qqqt):

```
w_046 = (1-w_mr) · 0.90
w_qqqt = (1-w_mr) · 0.10
w_mr  = (free param, swept ∈ {0.05, 0.10})
r_071[t] = w_046·r_046[t] + w_qqqt·r_qqqt[t] + w_mr·r_mr[t]
```

## Primary citation

`[algo_trading_chan, p.95, ch.4]` — Chan's RULE: "Apply a momentum
filter (price above long-term moving average) as a gate on a mean-
reversion entry signal. Drops caused by negative news are less likely
to revert than those caused by liquidity demands." This is the exact
calm-aggressive structural pattern needed.

## Additional citations

- `[algo_trading_chan, p.153-154, ch.6]` — Chan: mean-reverting and
  momentum strategies are complementary because mean-reversion has
  capped upside / unbounded drawdown, while momentum has limited
  downside / unlimited upside. The pair smooths the equity curve.
- `[algo_trading_chan, p.183-184, ch.8]` — Chan: NEVER impose stop
  losses on mean-reversion at levels that would trigger in backtest;
  set stop above max intraday backtest drawdown (used as a regime
  hedge, not as a tightener).
- `[quant_trading_chan, p.142-143]` — Chan: stop-loss is harmful for
  mean-reversion (exits at the worst moment). Exit must be via the
  opposite-of-entry signal (here: SPY > SMA5).
- Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies
  That Work*. TradingMarkets Publishing. ISBN 978-0-9755513-2-7.
  Canonical RSI(2) dip-buy strategy with 200-SMA momentum filter
  (referenced in `algo_trading_chan` p.95).
- Lo, A. W., & MacKinlay, A. C. (1988). "Stock Market Prices Do Not
  Follow Random Walks: Evidence from a Simple Specification Test."
  *Review of Financial Studies*, 1(1), 41-66.
  DOI: 10.1093/rfs/1.1.41 — empirical foundation for short-horizon
  mean-reversion in equity prices.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on signal (BOTH
  RSI and SMA at t-1, applied at t).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
- `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046
  base preserved verbatim (saved return stream).
- Faber (2007) SSRN 962461 — QQQ 200d SMA single-asset trend
  (preserved verbatim from iter 064).
- iter 064/070 final reports — TOP-K #1 baseline and the empirical
  evidence that both existing legs are defensively biased.

## Edge source

SPY's well-documented short-horizon (1-3 day) mean-reverting tendency
in calm regimes — driven by liquidity demands and dispersion in
intraday positioning — does NOT manifest in iter 064 (which is
defensively biased toward stress regimes). Combined at small weight,
the calm-aggressive complement provides incremental positive returns
during the 70-80% of the time the market is in calm/bull regimes,
without adding tail risk because the 200d-SMA gate cuts exposure
during stress.

## Datasets

- **educational** (2006-01-03 → 2026-04-15, bench=SPY, ~5100 bars):
  long enough to span the 2008 GFC, 2020 COVID, 2022 bear, plus
  multiple calm regimes — tests both calm-aggressive lift and
  stress-regime cash-out behaviour.
- **spy_real** (2009-06-25 → 2026-04-15, bench=SPY, ~4200 bars):
  post-GFC, dominated by calm regimes — the natural environment
  where calm-aggressive complement should shine.
- **ndx_real** (2010-02-12 → 2026-04-15, bench=QQQ, ~4080 bars):
  bench is QQQ but r_mr stream is on SPY (parallel to iter 064's
  use of QQQ_TREND on QQQ across all 3 datasets — single fixed
  asset for the leg). Tests whether SPY mean-reversion lifts the
  Sharpe of a QQQ-benchmarked composite.

## Configurations tested (4 cfgs, +4 to cumulative_n_trials)

| cfg_id | rsi_th | w_mr | exit | gate | rationale |
|---|---|---|---|---|---|
| `iter064_plus_spy_mr_rsi2_th5_w005` | RSI<5 | 0.05 | SMA5 | SMA200 | Connors-Alvarez canonical + small w |
| `iter064_plus_spy_mr_rsi2_th5_w010` | RSI<5 | 0.10 | SMA5 | SMA200 | Connors-Alvarez canonical + moderate w |
| `iter064_plus_spy_mr_rsi2_th3_w005` | RSI<3 | 0.05 | SMA5 | SMA200 | More selective (rarer entries) |
| `iter064_plus_spy_mr_rsi2_th10_w005` | RSI<10 | 0.05 | SMA5 | SMA200 | Looser entries (more time-in-market) |

cumulative_n_trials advance: 4340 → **4344** (+4).

## Kill criteria (pre-committed)

Pre-committed to prevent post-hoc rationalisation. If ANY of the
following fires on the primary cfg (`th5_w005`), the kill is recorded
in the verdict but doesn't auto-fail the iteration; the report
documents fired vs clean and ranks all 4 cfgs.

| # | kill | threshold | hypothesis falsified if fires |
|---|---|---|---|
| **A** | Sharpe lift vs iter 064 < +0.02 on ≥ 2 ds | Δ Sharpe < 0.02 | calm-aggressive complement hypothesis fails at this weight |
| **B** | r_mr standalone Sharpe < 0.5 on ≥ 2 ds | sub-stream lacks edge | Connors strategy lost edge in this regime sample |
| **C** | corr(r_mr, r_046) > 0.5 on ≥ 2 ds | not orthogonal | r_mr is structurally redundant with risk-parity stack |
| **D** | conditional Sharpe r_mr stress > calm on ≥ 2 ds | stream is defensive | structurally identical to existing legs (KILL = good info; redirects future iters) |
| **E** | G7 cross-lib > 0.5 pp on any ds | engine bug |
| **F** | Score < 75 (NEAR-FAIL or below) | iteration regresses below STRONG band |
| **G** | corr(071, 064) > 0.99 on ≥ 2 ds | 3rd stream inert (gate is decorative) |
| **H** | edu CAGR < 9.18% | drops below iter 064's non-LETF unlock floor |
| **I** | r_mr standalone MDD > 30% on any ds | too risky standalone |
| **J** | r_mr time-in-market > 30% on ≥ 2 ds | not the canonical Connors low-frequency profile |

## Expected budget

- Configs to test: **4** (sensitivity: 2 thresholds × 2 weights minus 1 redundant)
- Wall-time: ~60-90 min total (G7 + gates × 4 cfgs × 3 ds; loose target)
- Files to create:
  - `spy_mr.py` — pandas reference (~150 lines)
  - `numpy_reference_iter071.py` — pure-numpy reference for G7 (~100 lines)
  - `combined_046_qqqt_mr.py` — 3-leg convex combination helper
  - `tests/test_iter071_spy_mr.py` — TDD spec (~13-15 tests; RSI math, no-peek, signal correctness, cross-lib parity, edge cases)
  - `run_backtests.py` — 4 cfgs × 3 ds runner (mirrors iter 064)
  - `compute_gates_and_score.py` — 7-gate battery + scoring + verdict.json
  - `final_report.md`
  - 2 plots via `plot_helper.py`

## Implementation plan

1. **TDD first** — write `tests/test_iter071_spy_mr.py`:
   - `test_rsi2_known_values` — feed monotone-up / monotone-down / known oscillation, check RSI2 matches Wilder formula
   - `test_signal_no_peek_shift1` — perturb prices[t] and assert pos[t+1] unchanged (BOTH RSI and SMA at t-1)
   - `test_warmup_position_zero` — first 200 bars must be pos=0 (cash, in warmup)
   - `test_buy_only_when_gate_and_dip` — pos goes 0→1 only when SPY>SMA200 AND RSI2<threshold
   - `test_exit_when_above_sma5` — pos goes 1→0 only when SPY>SMA5 (cleared exit signal)
   - `test_cost_proportional_to_turnover` — cost = bps · |Δpos|
   - `test_cross_lib_parity` — pandas vs numpy max ret diff ≤ 1e-9
   - `test_invalid_params_raise` — th < 0 or > 100 raises; period <= 0 raises
   - `test_3leg_combo_inner_join` — combiner returns inner-join of 3 streams
   - `test_3leg_weights_validation` — negative or zero-sum raises
   - `test_3leg_proportional_preservation` — when w_mr=0, output ≡ iter 064 base on common index
2. Implement `spy_mr.py` — 2-period RSI via Wilder smoothing, state-tracking position, cost accounting.
3. Implement `numpy_reference_iter071.py` — pure-numpy mirror.
4. Implement `combined_046_qqqt_mr.py` — 3-leg blend on inner-joined index.
5. Run all tests; iterate until 100% pass.
6. Implement `run_backtests.py` — 4 cfgs × 3 ds, save `results.json` with `returns_series` per cfg per ds (for plot helper + Stage 5 gates).
7. Implement `compute_gates_and_score.py`:
   - G1 PBO via `validation/pbo.py` over the 4-cfg grid (per ds)
   - G2 DSR p-value via `validation/dsr.py` with `cumulative_n_trials=4344`
   - G3 walk-forward 8 windows
   - G4 OOS 70/30 split
   - G5 FWD post-2020 Sharpe
   - G6 bootstrap 99.9% CI
   - G7 cross-lib parity (pandas vs numpy)
   - Robustness: 9 sub-windows for the bonus
   - Call `score_strategy()` from `studies/strategy_hunt_loop/scoring.py`
8. Generate `verdict.json` for the BEST cfg by composite (Sharpe-weighted).
9. Run plot helper for spy_real + ndx_real.
10. Write `final_report.md` with all 10 kills + tier + score + lesson.
11. Update `BASE_MEMORY.md` (bump iter, n_trials, top-K, log entry, dead-ends if any) and `DEAD_ENDS.md` if structural closure.
12. **Auto-prune** BASE_MEMORY if > 18 KB.
