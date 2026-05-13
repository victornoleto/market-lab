# Stage 3 Testfolio Price-Only Validation

Status: honest validation verdict for the first Stage 3 GA leads.

## Verdict

**0/400 candidates passed all hard gates.**

The first Stage 3 GA leads are economically strong in-sample, and they pass the
basic temporal checks, but they do not survive the project validation stack. The
blocking gates are DSR and PBO, which is exactly the expected failure mode for a
dense GA neighborhood with many near-duplicate technical votes
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Trial Accounting

Validation used conservative cumulative DSR accounting:

- Prior exact/GA/local Stage 1 plus Stage 2 known search count baseline:
  `>=122,583,546`.
- Stage 3 minimum GA trials: `61,440` from two runs of `256 × 120`.
- Validation `n_trials`: `122,644,986`.

## Runs Validated

| Run | Candidates | OOS pass | FWD pass | WF pass | Bootstrap pass | DSR pass | PBO pass | All pass | PBO | DSR p range |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `QQQ_QLD_2x_ZROZSIM_seed42_top200` | 200 | 200 | 200 | 191 | 200 | 0 | 0 | 0 | 0.9881 | 0.3118..0.4673 |
| `QQQ_TQQQ_3x_ZROZSIM_seed42_top200` | 200 | 200 | 200 | 200 | 200 | 0 | 0 | 0 | 0.9643 | 0.3863..0.5915 |

## Best In-Sample Leads

| Run | Top rule | Sortino | CAGR | MDD | Signals |
|---|---|---:|---:|---:|---|
| QLD | `n=8/k=6` | 1.3747 | 32.06% | -57.81% | `px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50` |
| TQQQ | `n=8/k=6` | 1.2680 | 40.28% | -64.24% | same signal set |

These top leads beat their branch-native T3d-K2 and iter030-like anchors
in-sample on Sortino, CAGR and MDD, but that does not promote them because DSR
and PBO are hard gates.

## Interpretation

The shared best rule is economically meaningful: a strict trend/momentum vote
requiring six of eight conditions. It is not obviously nonsensical, and the fact
that the same signal set appears for both QLD and TQQQ is a useful research clue.

However, the validation panel shows a very high PBO because the top-200 candidates
are a concentrated neighborhood around the same trend/momentum structure. The DSR
failure also says the observed Sharpe is not exceptional after accounting for the
large accumulated search budget. Therefore the correct status is:

- Keep the rule as a **fixed challenger** for Tiingo confirmation.
- Do not call it better than T3d-K2/iter030 yet.
- Do not expand GA locally on the same testfolio signal family without a new
  hypothesis, because it will mostly add correlated trials.

## Artifacts

QLD validation:

- `QQQ_QLD_2x_ZROZSIM_seed42_top200/REPORT.md`
- `QQQ_QLD_2x_ZROZSIM_seed42_top200/tables/gates.csv`
- `QQQ_QLD_2x_ZROZSIM_seed42_top200/tables/candidate_metrics.csv`
- `QQQ_QLD_2x_ZROZSIM_seed42_top200/tables/walk_forward.csv`
- `QQQ_QLD_2x_ZROZSIM_seed42_top200/tables/bootstrap.csv`
- `QQQ_QLD_2x_ZROZSIM_seed42_top200/tables/pbo_panel.csv`

TQQQ validation:

- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/REPORT.md`
- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/tables/gates.csv`
- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/tables/candidate_metrics.csv`
- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/tables/walk_forward.csv`
- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/tables/bootstrap.csv`
- `QQQ_TQQQ_3x_ZROZSIM_seed42_top200/tables/pbo_panel.csv`

## Next Step

Proceed to Tiingo real-ETF confirmation and indicator expansion using the shared
Stage 3 rule as a fixed challenger. Tiingo should be used next to test whether
real OHLC indicators can improve the fixed long-history lead, but any new grid or
GA must increment cumulative trial accounting.

## PBO-Proxy Follow-Up

User requested one final Stage 3 check that makes the GA care about PBO-like
behavior while ignoring DSR for selection. True PBO is a panel/ranking statistic,
so it cannot be optimized directly as an individual fitness term. The runner now
supports a practical proxy via `--pbo-proxy-weight`: it rewards broad
walk-forward Sharpe consistency, positive windows and lower cross-window
dispersion `[advances_fin_ml, p.208-211]`.

Runs:

- `QQQ_QLD_2x_ZROZSIM_seed52`, `--pbo-proxy-weight 0.75`, `n=8..14`.
- `QQQ_TQQQ_3x_ZROZSIM_seed52`, `--pbo-proxy-weight 0.75`, `n=8..14`.

Validation outcome:

| Run | Candidates | OOS pass | FWD pass | WF pass | Bootstrap pass | DSR pass | PBO pass | All pass | PBO | DSR p range | Top Sortino | Top CAGR | Top MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| PBO-proxy QLD | 200 | 200 | 200 | 194 | 200 | 0 | 0 | 0 | 0.9960 | 0.3703..0.5730 | 1.3200 | 32.09% | -57.78% |
| PBO-proxy TQQQ | 200 | 200 | 200 | 200 | 200 | 0 | 0 | 0 | 0.9365 | 0.3933..0.6245 | 1.2680 | 40.28% | -64.24% |

Interpretation: the stability proxy did not solve PBO. QLD PBO worsened and
TQQQ remained high. This suggests the failure is driven by the candidate panel
being a dense cluster of highly similar trend/momentum votes, not merely by
single-window instability. Further local GA on this signal family is unlikely to
turn PBO without a genuinely different hypothesis or explicit panel-diversity
selection.

Artifacts:

- `pbo_proxy_QQQ_QLD_2x_ZROZSIM_seed52_top200/REPORT.md`
- `pbo_proxy_QQQ_TQQQ_3x_ZROZSIM_seed52_top200/REPORT.md`
