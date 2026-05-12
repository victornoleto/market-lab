# Technical Signal Vote Hunt

Research-only study for broad `n`-signal / `k`-vote risk-on gates, starting
from the LETF rotation findings in `studies/letf_rotation_hunt/`.

Current Stage 1 verdict: **honest FAIL**. The full selected-candidate validation
ran with 12 candidates, 2,000 bootstrap paths, and DSR `n_trials=5,471,268`; no
candidate passed all hard gates. A later GA/local-search validation of the two
best QQQ candidates also failed DSR with cumulative `n_trials=7,554,054`.

Mandate reminder: this study does not authorize capital allocation. Strategy B
remains dormant and any candidate must pass the hard validation stack before it
can be considered outside research mode `[advances_fin_ml, p.208-211]`.

## Goal

Find whether a larger universe of technical signals can improve on branch-native
benchmarks:

| Stage | Data | Branch | Signal asset | Risk-on legs | Benchmark |
|---|---|---|---|---|---|
| 1 | testfolio close-only | SPY | `SPYSIM` | `SSOSIM`, `UPROSIM` | `SPYSIM` |
| 1 | testfolio close-only | QQQ | `QQQSIM` | `QLDSIM`, `TQQQSIM` | `QQQSIM` |
| 2 | Tiingo adjusted OHLC | SPY | `SPY` | `SPY?L=2`, `SPY?L=3` | `SPY` |
| 2 | Tiingo adjusted OHLC | QQQ | `QQQ` | `QQQ?L=2`, `QQQ?L=3` | `QQQ` |

Stage 1 is implemented first. Stage 2 is intentionally separate because OHLC
signals shorten the available window and require adjusted OHLC construction.

## Stage 1 Commands

### Slow Reference Runner

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only --max-n 2
```

Outputs land under `studies/technical_signal_vote_hunt/results/stage1_close_only/`.

Use `--max-n` to control the exhaustive combination size. The signal universe is
large enough that unrestricted exhaustive search can create millions of configs.
The initial implementation is suitable for `n<=2` full-universe exploratory
runs; `n>=3` should use a faster vectorized runner or a beam-search pass before
being treated as a routine command.

### Fast Exact-Grid Runner

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast --max-n 3 --progress-every 10000
```

Use `--estimate` before large runs:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast --max-n 0 --estimate
```

`--max-n 0` means all subset sizes, but with 33 signals this is billions of
subsets before the `k` dimension. Exact all-subset search is not practical;
use capped `--max-n` or a later beam-search layer.

Already validated run:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast \
  --max-n 4 \
  --progress-every 50000 \
  --top 40
```

Observed output: 724,548 configs in about 267 seconds. Results are in
`results/stage1_close_only_fast/`.

Completed exact-grid run used for Stage 1 candidate sourcing:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast \
  --max-n 5 \
  --allow-huge \
  --progress-every 100000 \
  --top 50
```

Observed size: 5,471,268 configs. This is an exploratory in-sample grid, not a
walk-forward validation. It sourced the 12 candidates used in the Stage 1
validation report.

Helpful variants:

```bash
# Print progress very frequently for monitoring.
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast \
  --max-n 5 \
  --allow-huge \
  --progress-every 10000

# Estimate the all-subset grid without running it.
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast \
  --max-n 0 \
  --estimate
```

The full `n=1..33` exact grid estimates at 566,935,683,072 configs across the
four branches, so it should not be run exhaustively.

### Genetic-Search Runner

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch QQQ \
  --risk-on QLD_2x \
  --population 256 \
  --generations 100 \
  --elite 20 \
  --seed 42
```

Outputs land in `results/stage1_ga/<BRANCH>_<RISK_ON>_seed<SEED>/` and are
updated during the run:

- `best_by_generation.csv`
- `population_history.csv`
- `final_candidates.csv`
- `REPORT.md`

Smoke test that has already passed:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch QQQ \
  --risk-on QLD_2x \
  --population 24 \
  --generations 5 \
  --elite 6 \
  --seed 7 \
  --max-n 8 \
  --top-final 20
```

Suggested first real GA batch, run one command at a time:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch QQQ --risk-on QLD_2x \
  --population 256 --generations 100 --elite 20 --seed 42

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch QQQ --risk-on TQQQ_3x \
  --population 256 --generations 100 --elite 20 --seed 42

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch SPY --risk-on SSO_2x \
  --population 256 --generations 100 --elite 20 --seed 42

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_ga \
  --branch SPY --risk-on UPRO_3x \
  --population 256 --generations 100 --elite 20 --seed 42
```

The GA prints one status line per generation with fitness, Sortino, CAGR, MDD,
`n/k` and selected signals. It is a search method, not proof of robustness.

## Workflow Notes

- Exact grids and GA runs are candidate discovery only.
- The completed validation step took top candidates from `stage1_close_only_fast/`,
  deduplicated them, and ran walk-forward, OOS, FWD, bootstrap, PBO and DSR.
- DSR trial accounting must include every evaluated config/individual, not just
  the final candidates `[advances_fin_ml, p.222-223]`.
- Current Stage 1 off-leg default is `ZROZSIM`; rerun with `--off-leg CASHX` to
  isolate defensive-duration contribution.

## Stage 1 Validation Runner

Validate selected candidates from the top-strategy report:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.validate_stage1_candidates \
  --n-trials 5471268 \
  --bootstrap-n 2000 \
  --progress
```

Expected runtime for the current 12 selected candidates: a few minutes. Outputs:

- `reports/stage1_validation/REPORT.md`
- `reports/stage1_validation/tables/candidate_metrics.csv`
- `reports/stage1_validation/tables/gates.csv`
- `reports/stage1_validation/tables/walk_forward.csv`
- `reports/stage1_validation/tables/bootstrap.csv`
- `reports/stage1_validation/tables/pbo_panel.csv`

Observed full run: 12/12 candidates passed OOS, FWD, walk-forward and bootstrap,
but 12/12 failed DSR (`p=0.1890..0.4631`, required `<0.05`) and failed the
diagnostic top-k PBO panel (`0.8095..0.9921`, required `<0.5`). This leaves Stage
1 as in-sample economic leads only, not validated winners `[advances_fin_ml,
p.208-211]`, `[advances_fin_ml, p.222-223]`.

Post-GA/local-search validation of the two QQQ incumbents:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.validate_stage1_candidates \
  --candidates studies/technical_signal_vote_hunt/reports/stage1_ga_local_candidates/tables/qqq_final_candidates.csv \
  --out-dir studies/technical_signal_vote_hunt/reports/stage1_ga_local_validation \
  --off-leg ZROZSIM \
  --n-trials 7554054 \
  --bootstrap-n 2000 \
  --pbo-group branch \
  --progress
```

Observed run: both QQQ candidates passed OOS, FWD, walk-forward, bootstrap and
diagnostic branch-panel PBO, but both failed DSR: QLD `p=0.1444`, TQQQ
`p=0.2260`. The QQQ GA/local-search leads remain research-only and do not clear
the hard validation stack `[advances_fin_ml, p.196-202]`, `[advances_fin_ml,
p.222-223]`.

## Stage 1 Local Search Runner

Run an exact one-edit neighborhood around the current QQQ→QLD GA incumbent:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage1_local_search \
  --branch QQQ \
  --risk-on QLD_2x \
  --base-k 5 \
  --top 50
```

Default base signals are:

```text
px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0
```

Observed run: 216 one-edit subsets and 1,531 configs. The base incumbent remained
#1 by GA fitness: Sortino 1.3776, CAGR 32.79%, MDD -56.38%. This supports it as a
local in-sample optimum, not as a validated winner. Add these configs to later DSR
trial accounting `[advances_fin_ml, p.222-223]`.

Current post-validation candidate registry:

- `reports/stage1_ga_local_candidates/REPORT.md`

It records the current top tiers: QQQ→QLD+ZROZ balanced incumbent, QQQ→TQQQ+ZROZ
performance-first challenger, and CASHX diagnostics.

## Stage 2 Tiingo OHLC Runner

Stage 2 uses real Tiingo ETF daily bars and adjusts OHLC before computing
high/low indicators:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc \
  --branch QQQ \
  --risk-on QLD_2x \
  --off-leg ZROZ \
  --base-k 5 \
  --out-name QQQ_QLD_2x_ZROZ_local

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc \
  --branch QQQ \
  --risk-on TQQQ_3x \
  --off-leg ZROZ \
  --base-signals 'px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0' \
  --base-k 6 \
  --out-name QQQ_TQQQ_3x_ZROZ_local
```

Observed first Stage 2 diagnostic:

| Branch | Window | Base replay | Best one-edit OHLC local |
|---|---|---|---|
| QQQ→QLD + ZROZ | 2009-11-05..2026-04-14 | Sortino 1.2775, CAGR 26.31%, MDD -56.44% | `+atr14_pct_lt_3`, `n=8/k=6`, Sortino 1.2870, CAGR 26.38%, MDD -56.44% |
| QQQ→TQQQ + ZROZ | 2010-02-12..2026-04-14 | Sortino 1.2337, CAGR 34.75%, MDD -65.36% | `-roc120_gt_0+atr14_pct_lt_3`, `n=8/k=6`, Sortino 1.3307, CAGR 38.77%, MDD -62.06% |

Reports:

- `results/stage2_tiingo_ohlc/QQQ_QLD_2x_ZROZ_local/REPORT.md`
- `results/stage2_tiingo_ohlc/QQQ_TQQQ_3x_ZROZ_local/REPORT.md`
- `reports/stage2_grid_overnight/REPORT.md`

Interpretation: real-inception Tiingo reduces the long-history synthetic CAGR,
but the QQQ→TQQQ branch remains economically strong in-sample. `ATR14% < 3%`
is the first OHLC lead; it is still local discovery and needs a Stage 2 honest
validation runner before any claim `[trading_systems_methods, p.732-733]`,
`[advances_fin_ml, p.208-211]`.

Overnight exact grids (`QQQ+ZROZ n<=5`, `QQQ+BIL n<=5`, `SPY+ZROZ n<=5`,
`QQQ→TQQQ+ZROZ n=6`) evaluated 115,029,492 persisted configs. Top CAGRs were
mechanically reproduced by an independent pandas recompute, but remain
suspect-by-default due to massive trial count and close-to-close execution
sensitivity. See `reports/stage2_grid_overnight/REPORT.md`.

Operational Stage 2 grid support now includes `--off-leg CASH_USD`,
`--extra-lag-days`, and default same-config redundancy exclusion. Redundant groups
exclude equivalent MACD forms and nested threshold families such as ADX, ATR%,
RV percentile, stochastic, CCI, prior-high breakout and Elder power filters; this
keeps exact grids from selecting two versions of the same decision rule
`[advances_fin_ml, p.222-223]`.

Completed operational QQQ runs with `CASH_USD`, `extra_lag_days=1`, `n<=5`, and
redundancy exclusion:

| Branch | Configs | Best | Metrics |
|---|---:|---|---|
| QQQ→TQQQ | 7,067,694 | `n=5/k=3`, `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70` | Sortino 1.4124, CAGR 53.00%, MDD -51.03% |
| QQQ→QLD | 7,067,694 | `n=5/k=2`, `roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0` | Sortino 1.3181, CAGR 34.54%, MDD -53.09% |

Reports:

- `results/stage2_tiingo_ohlc/QQQ_TQQQ_CASH_USD_lag1_n1_5/REPORT.md`
- `results/stage2_tiingo_ohlc/QQQ_QLD_CASH_USD_lag1_n1_5/REPORT.md`

Deduped exact-grid estimates for QQQ QLD+TQQQ with `CASH_USD + extra_lag_days=1`:

| Max n | Estimated configs |
|---:|---:|
| 5 | 14,135,388 |
| 6 | 115,350,684 |
| 7 | 761,622,940 |
| 8 | 4,183,106,396 |

Interpretation: exact `n<=7/8` is possible only as a deliberate long run, not as
routine iteration. GA/beam search is the practical way to explore `n<=8+`; every
evaluated chromosome still counts toward later DSR trial accounting. PSR can be
reported as a useful single-strategy diagnostic, but it does not replace DSR as a
hard gate under the current mandate `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.222-223]`.

## Stage 1 Top-Strategy Report

After running the fast exact grid, generate a richer deep-dive report with plots:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.generate_stage1_top_report \
  --top-per-branch 3
```

Outputs:

- `reports/stage1_top_strategies/REPORT.md`
- `reports/stage1_top_strategies/plots/*.png`
- `reports/stage1_top_strategies/tables/headline_metrics.csv`
- `reports/stage1_top_strategies/tables/rolling_summary.csv`

The report compares the top candidates per branch/risk-on against native
benchmarks: buy-hold, LRS SMA200, T3d-K2 transplant and iter030-like transplant.
