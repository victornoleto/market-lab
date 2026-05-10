# Weekly Momentum Deploy Candidates

## Status

These candidates are frozen for the next validation round. They are **research
candidates**, not deployable strategies. Promotion still requires point-in-time
universe work, costs/slippage/taxes, and hard statistical validation.

Update 2026-05-09: the first cost/slippage, annual DARF and ADV20 liquidity
stress was added to the generated candidate-validation bundle. The detailed CSV/plot bundle was removed during final cleanup; decision metrics are retained here and in `FINAL_REPORT.md`.
This completes the first pass of validation steps 2-3 and starts step 7, but the
stress remains proxy-level rather than broker-grade execution/tax accounting.

Update 2026-05-09: first-pass anti-overfit gates and required plots were added
to the same report. `dynamic_wf_all_stocks` fails family PBO (0.798),
`dynamic_wf_sp500` fails DSR (p=0.191), `fixed_balanced_sp500` fails DSR
(p=0.092), and `fixed_aggressive_sp500` is the only candidate passing PBO
context, DSR, OOS and bootstrap in this pass. This is not a final deploy verdict
because PIT universe, delisting handling and execution/tax precision remain
open.

## Candidate Set

| candidate | type | universe | rule |
|---|---|---|---|
| `fixed_aggressive_sp500` | fixed config | current S&P 500 | `lookback=60`, `top_k=3`, `SPY>SMA200`, cash if all momentum is non-positive |
| `fixed_balanced_sp500` | fixed config | current S&P 500 | `lookback=60`, `top_k=10`, `SPY>SMA100`, cash if all momentum is non-positive |
| `dynamic_wf_sp500` | dynamic walk-forward | current S&P 500 | every 1y test window, select the best config using the prior 3y train window |
| `dynamic_wf_all_stocks` | dynamic walk-forward | full Tiingo stock cache | same walk-forward selector over the broader stock cache |

The fixed candidates use the weekly/monthly cross-sectional momentum family
`[stocks_on_the_move, p.60]` with a defensive SPY trend-risk filter
`[stocks_on_the_move, p.66-67, p.81]`. The dynamic candidates are treated as
strategies only because the selection rule is frozen before validation; the
walk-forward structure is an overfit-control diagnostic
`[advances_fin_ml, p.208-211]`.

## Dynamic Selection Rule

The dynamic candidates use this frozen grid:

- lookbacks: `4,20,60,90,126`
- `top_k`: `3,5,10,20`
- market filters: `none,sma100,sma200,ema100,ema200`
- `allow_negative_momentum`: `0,1`
- train window: `3y`
- test window: `1y`
- score: train Sharpe + train CAGR - abs(train MDD)

## Validation Plan

1. Freeze the 4 candidates and candidate-selection rules.
2. Generate comparable reports for full period, subperiods, rolling 1/3/5/10y,
   trades, turnover, exposure and SPY benchmark.
3. Add realistic costs and slippage. First proxy stress done; broker-grade fills
   remain pending.
4. Run fixed-config walk-forward diagnostics for `fixed_aggressive_sp500` and
   `fixed_balanced_sp500`.
5. Run dynamic walk-forward diagnostics for `dynamic_wf_sp500` and
   `dynamic_wf_all_stocks`.
6. Build one comparison panel for all 4 candidates.
7. Review operational plausibility: liquidity, concentration, turnover, bad
   regimes and small-cap dependence. First ADV20/turnover pass done.
8. Run hard statistical validation: PBO, DSR, bootstrap, stress costs/slippage
   and temporal holdout `[advances_fin_ml, p.196-202]`. First pass done; deeper
   PIT/listing-aware rerun remains pending.

## Caveats

- `fixed_aggressive_sp500`, `fixed_balanced_sp500` and `dynamic_wf_sp500` use
  current S&P 500 membership, so they remain survivorship-biased.
- `dynamic_wf_all_stocks` is economically interesting because smaller companies
  can produce more convex winners, but it has higher coverage, delisting,
  liquidity and listing-bias risk.
- No candidate is deployable before PIT universe, costs/slippage/taxes and hard
  validation gates are complete.
