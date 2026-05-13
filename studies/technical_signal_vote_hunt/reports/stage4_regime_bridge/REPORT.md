# Stage 4 Regime-Gated Bridge

Status: first economic-first regime-gate pass for the modern QQQ/LETF vote.

## Framing

This pass follows the user's explicit research preference: temporarily treat PBO
and DSR as diagnostics instead of strategy-discard rules. The runner therefore
reports two separate concepts:

| Verdict | Meaning |
|---|---|
| `economic_pass` | OOS, FWD, WF, bootstrap and rolling-cycle checks pass. PBO/DSR ignored for this exploratory view. |
| `mandate_pass` | Deployment-style verdict. Always false in this runner because PBO/DSR are not computed here. |

The separation avoids discarding strong cycle behavior while preserving the public
mandate boundary: no result here authorizes deployment without the full gate stack
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Setup

| Item | Value |
|---|---|
| Data | Tiingo daily adjusted OHLC / adjusted close |
| Window | `2010-02-12..2026-04-14` |
| Signal asset | `QQQ` |
| Risk-on legs | `QLD`, `TQQQ` |
| Off-leg | `CASH_USD` |
| Execution | `extra_lag_days=1` |
| Base rule | `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3` |
| Bootstrap | 500 block-bootstrap paths |

Regime gates tested were deliberately small and interpretable: long-MA trend,
MA slope, distance from 252-day high, realized-vol percentile and QQQ/SPY relative
strength. Trend and volatility choices follow the leverage-for-the-long-run
rationale that leveraged exposure works best when trend is favorable and
volatility drag is controlled `[leverage_for_the_long_run, p.5-7]`,
`[leverage_for_the_long_run, p.13]`.

## Headline Results

| Risk-on | Gate | Economic pass | Sortino | CAGR | MDD | WF pass windows | Rolling 3/5/10/15y positive CAGR |
|---|---|---:|---:|---:|---:|---:|---|
| QLD | none | yes | 1.4209 | 36.26% | -37.54% | 7/8 | 100% / 100% / 100% / 100% |
| QLD | `dd252_gt_m30` | yes | 1.4157 | 36.08% | -37.54% | 7/8 | 100% / 100% / 100% / 100% |
| QLD | `dd252_gt_m20` | yes | 1.3467 | 33.83% | -37.54% | 7/8 | 100% / 100% / 100% / 100% |
| TQQQ | none | yes | 1.4124 | 53.00% | -51.03% | 7/8 | 100% / 100% / 100% / 100% |
| TQQQ | `dd252_gt_m30` | yes | 1.4060 | 52.79% | -51.03% | 7/8 | 100% / 100% / 100% / 100% |
| TQQQ | `dd252_gt_m20` | yes | 1.3370 | 49.17% | -51.03% | 7/8 | 100% / 100% / 100% / 100% |

Other gates did not improve the base rule. Long-MA overlays, volatility overlays
and relative-strength overlays still had positive rolling profiles, but failed the
WF threshold used for `economic_pass`.

## Interpretation

The first Stage 4 result is counterintuitive: the best economic result is the
ungated base vote. Adding simple regime gates mostly removes good risk-on days
without improving drawdown. The 252-day drawdown gates are nearly neutral and pass,
but they do not beat the base rule.

For the user's cycle-based criterion, the base vote is strong in the Tiingo 2010+
sample:

- QLD base vote: every sampled rolling 3y/5y/10y/15y window has positive CAGR.
- TQQQ base vote: every sampled rolling 3y/5y/10y/15y window has positive CAGR.
- Both pass OOS, FWD, WF 7/8 and bootstrap in this economic-first view.

That is a meaningful research result even though it remains non-deploy under the
strict mandate. The risk is not obvious temporal failure; the risk is that the
2010+ regime itself may be the selected favorable regime.

## Artifacts

Runner:

- `studies/technical_signal_vote_hunt/runners/run_stage4_regime_bridge.py`

Result reports:

- `../../results/stage4_regime_bridge/QQQ_QLD_CASH_USD_lag1/REPORT.md`
- `../../results/stage4_regime_bridge/QQQ_TQQQ_CASH_USD_lag1/REPORT.md`

Tables:

- `../../results/stage4_regime_bridge/QQQ_QLD_CASH_USD_lag1/tables/metrics.csv`
- `../../results/stage4_regime_bridge/QQQ_TQQQ_CASH_USD_lag1/tables/metrics.csv`
- `../../results/stage4_regime_bridge/QQQ_QLD_CASH_USD_lag1/tables/rolling_windows.csv`
- `../../results/stage4_regime_bridge/QQQ_TQQQ_CASH_USD_lag1/tables/rolling_windows.csv`

## Next Step

Do not add more one-off overlays yet. The useful next test is to bridge this exact
base vote back to the longer 1986+ testfolio window and ask a narrower question:
can an explicit crisis/off-leg rule preserve the excellent Tiingo rolling profile
without collapsing in 1987/2000/2008? If not, the current base vote should be
classified as a modern-regime monitor candidate rather than a long-history anchor.
