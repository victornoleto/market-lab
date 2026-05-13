# Research Direction Review

Status: post-validation direction memo for `technical_signal_vote_hunt`.

## Verdict

The study has not produced a deployable replacement for T3d-K2 or iter030. It has
produced a repeatable economic clue: QQQ/LETF trend, momentum and volatility votes
are strong in the modern Tiingo window and often survive OOS/FWD/WF/bootstrap, but
they repeatedly fail the hard overfit controls once cumulative trial accounting and
candidate-panel PBO are applied `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

Do not continue with unconstrained local GA or exact grids in the same signal
family. That path has already shown the same failure mode: dense clusters of
similar trend/momentum votes, high PBO, and DSR p-values far above the mandate
threshold.

## Evidence Summary

| Panel | Candidates | Result | Blocking gates | Notes |
|---|---:|---|---|---|
| Stage 1 close-only exact top | 12 | 0 pass | DSR, PBO | All passed OOS/FWD/WF/bootstrap. |
| Stage 1 GA/local QQQ | 2 | 0 pass | DSR | PBO improved, but cumulative DSR still blocked. |
| Stage 2 Tiingo Stage-3-rule neighborhood | 80 | 0 pass | DSR, PBO, partial WF | Did not beat existing Stage 2 frontier. |
| Stage 2 Tiingo operational top grids | 400 | 0 pass | DSR, PBO | Best modern economic leads, still not honest winners. |
| Stage 3 testfolio GA | 400 | 0 pass | DSR, PBO | Long-history leads passed temporal checks but clustered heavily. |
| Stage 3 PBO-proxy GA | 400 | 0 pass | DSR, PBO | Individual stability proxy did not reduce panel PBO. |

The most useful positive evidence is not a single strategy. It is the recurring
structure of the best leads:

| Component | Recurring examples | Interpretation |
|---|---|---|
| Long trend | `sma100_gt_sma250`, `px_gt_ema200`, `px_gt_sma250` | Avoids the worst prolonged bear regimes. |
| Momentum | `roc10_gt_0`, `roc20_gt_0`, `roc60_gt_0`, `roc120_gt_0` | Captures persistent QQQ/LETF upside regimes. |
| Oscillator confirmation | `stochrsi14_gt_50`, `rsi14_gt_50` | Helps timing but is not sufficient alone. |
| Volatility filter | `rv21_pct_lt_70`, `atr14_pct_lt_3`, `atr14_pct_lt_5` | Penalizes LETF decay/crash regimes `[leverage_for_the_long_run, p.5-7]`. |
| OHLC context | `ADX14`, `CCI20`, `bear_power`, breakouts | Useful in Tiingo, but unavailable in 1986+ close-only stress. |

## Current Best References

T3d-K2 and iter030 remain the robust long-history anchors. The Stage 2 technical
vote leaders remain modern-regime challengers, not replacements:

| Reference | Role | Current status |
|---|---|---|
| T3d-K2 canonical QLD/ZROZ | Closed-study anchor | Preserved reference; not displaced. |
| iter030 canonical QLD/ZROZ LRS1.20 | Post-close research anchor | Strongest long-history reference in this comparison. |
| QLD common vote `k=3` | Modern Tiingo lead | Excellent 2010+ economics; failed PBO/DSR. |
| TQQQ common vote `k=3` | Modern Tiingo performance lead | Higher CAGR, higher drawdown; failed PBO/DSR. |
| Stage 3 shared `n=8/k=6` rule | Bridge clue | Useful diagnostic, weak Tiingo confirmation. |

## Decision

The next hypothesis must change the problem, not merely add more combinations.
Acceptable next work must do at least one of these:

1. Add an interpretable regime gate that decides when the modern QQQ/LETF vote
   family is valid versus when T3d-K2/iter030-style defense is required.
2. Build panel-diversity selection before PBO so the validation panel is not just
   top-200 variants of the same vote structure.
3. Add PSR diagnostics for economic readability, while keeping DSR and PBO as hard
   gates `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Recommended Stage 4

Stage 4 should be a **Regime-Gated Tiingo/Testfolio Bridge**:

| Design item | Default choice |
|---|---|
| Risk-on universe | QQQ to QLD/TQQQ |
| Operational off-leg | `CASH_USD` for Tiingo, `CASHX`/`ZROZSIM` stress on testfolio |
| Execution timing | `extra_lag_days=1` baseline; lag 0 remains theoretical upper bound |
| Seed rule | `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3` |
| Anchor comparison | T3d-K2 and iter030 canonical returns |
| Candidate gates | OOS, FWD, WF, bootstrap, PBO, DSR with cumulative trials |

Candidate regime gates should be simple enough to pre-register before sweeping:

| Gate family | Examples | Rationale |
|---|---|---|
| Trend regime | QQQ above long MA, long MA slope positive | Aligned with LRS trend gating `[leverage_for_the_long_run, p.13]`. |
| Crash distance | drawdown from ATH, rearm threshold | Tests whether old crisis regimes need separate handling. |
| Volatility regime | realized-vol percentile, ATR percentile | LETF decay increases with volatility `[leverage_for_the_long_run, p.5-7]`. |
| Relative strength | QQQ/SPY ratio trend | Separates NDX leadership regimes from broad-market regimes. |
| Defense selection | CASH versus ZROZ by rate/trend proxy | Tests whether duration off-leg is structural or regime-specific. |

## Stop Conditions

Stop Stage 4 early if any of these happens:

| Condition | Action |
|---|---|
| PBO remains above 0.5 across a diverse panel | Stop the family; overfit not solved. |
| DSR p remains far above 0.05 after conservative trial accounting | Keep as diagnostic only. |
| Testfolio 1986+ improvement requires sacrificing Tiingo execution realism | Reject as historical artifact. |
| Tiingo improvement collapses under `extra_lag_days=1` | Reject as execution-timing artifact. |
| Best rule is too complex to explain pre-trade | Reject or simplify before validation. |

## Practical Next Steps

1. Implement a small Stage 4 runner that evaluates pre-registered regime gates
   around the QLD/TQQQ common vote and writes comparison tables versus T3d-K2 and
   iter030.
2. Add PSR columns to the Stage 1/2/3 validators for diagnostics only; do not use
   PSR to override DSR or PBO.
3. Add a panel-diversity selector before validation reports: one candidate per
   signal-family cluster, plus equity-curve correlation limits.
4. Do not run exact `n<=7/8` Tiingo grids unless a Stage 4 hypothesis first
   improves PBO behavior; enumeration alone is not a research advance.
