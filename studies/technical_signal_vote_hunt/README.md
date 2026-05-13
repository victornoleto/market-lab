# Technical Signal Vote Hunt

Research-only study for broad `n`-signal / `k`-vote risk-on gates, starting
from the LETF rotation findings in `studies/letf_rotation_hunt/`.

Current verdict: **no honest winner**. Stage 1, Stage 2 and Stage 3 validations all
closed with 0 candidates passing the full hard-gate stack. The recurring useful
signal is economic, not promotable: QQQ/LETF trend/momentum/volatility votes are
strong in modern samples and often pass OOS/FWD/WF/bootstrap, but fail DSR and PBO
after cumulative trial accounting `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

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
- Current research direction is documented in
  `reports/research_direction_review/REPORT.md`: do not run more unconstrained
  local GA/exact grids in the same technical-vote family; the next hypothesis
  should be regime-gated or panel-diversity-aware.

## Research Direction Review

The consolidated post-validation decision is in:

- `reports/research_direction_review/REPORT.md`

Summary:

- T3d-K2 and iter030 remain the robust long-history anchors.
- Stage 2 QLD/TQQQ cash+lag1 leaders remain modern-regime challengers only.
- Stage 3 testfolio GA and PBO-proxy follow-up did not solve PBO.
- The recommended Stage 4 is a regime-gated Tiingo/testfolio bridge, not more
  local optimization of the same vote family.

## Stage 4 Regime-Gated Bridge

Stage 4 supports an economic-first view requested by the user: PBO/DSR are kept
out of `economic_pass` and treated as deployment diagnostics, while OOS/FWD/WF,
bootstrap and rolling 3/5/10/15y cycle behavior remain visible.

Runner:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge \
  --branch QQQ \
  --risk-on QLD_2x \
  --off-leg CASH_USD \
  --extra-lag-days 1 \
  --bootstrap-n 500 \
  --out-name QQQ_QLD_CASH_USD_lag1

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge \
  --branch QQQ \
  --risk-on TQQQ_3x \
  --off-leg CASH_USD \
  --extra-lag-days 1 \
  --bootstrap-n 500 \
  --out-name QQQ_TQQQ_CASH_USD_lag1
```

Initial result report:

- `reports/stage4_regime_bridge/REPORT.md`

Observed result: the ungated base vote remains best. QLD and TQQQ base votes both
pass the economic-first screen with 100% positive sampled rolling 3y/5y/10y/15y
CAGR in the 2010+ Tiingo window. Simple regime overlays did not improve the
frontier; 252-day drawdown gates were near-neutral and passed, while long-MA,
volatility and QQQ/SPY relative-strength overlays failed WF.

Stage 4 equity/benchmark comparison:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.compare_stage4_equity
```

Report:

- `reports/stage4_equity_benchmark_comparison/REPORT.md`

This compares Stage 4 QLD/TQQQ base votes against SPY buy-hold, QQQ as NDX proxy,
T3d-K2 proxy and iter030-like proxy, including absolute equity and relative equity
plots.

Testfolio long-history reproduction:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.compare_stage4_testfolio --off-leg CASHX
uv run python -m studies.technical_signal_vote_hunt.runners.compare_stage4_testfolio \
  --off-leg ZROZSIM \
  --out-dir studies/technical_signal_vote_hunt/reports/stage4_testfolio_reproduction_zroz
```

Reports:

- `reports/stage4_testfolio_reproduction/REPORT.md`
- `reports/stage4_testfolio_reproduction_zroz/REPORT.md`

Observed result: the Stage 4 base vote is reproducible on testfolio, but it is not
superior to the canonical long-history anchors. With `ZROZSIM`, QLD reaches CAGR
19.38% / MDD -70.07% and TQQQ reaches CAGR 21.48% / MDD -87.69%, while canonical
T3d-K2 reaches CAGR 31.06% / MDD -64.50% and canonical iter030 reaches CAGR 36.66%
/ MDD -55.48%.

Stage4-inside-iter030 turbo test:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage4_inside_iter030
```

Report:

- `reports/stage4_inside_iter030/REPORT.md`

Observed result: using Stage4 as the QLD→TQQQ upgrade gate inside the iter030
defensive shell can raise CAGR/terminal equity, but worsens Sortino and drawdown.
`inside_rearm_or_stage4` reaches CAGR 38.46% vs iter030 36.66%, but MDD worsens to
-64.54% and Sortino falls to 1.0838; iter030 remains the better risk-adjusted
anchor.

Pareto hybrid search:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage4_pareto_hybrid_search
```

Report:

- `reports/stage4_pareto_hybrid_search/REPORT.md`

Observed result: 225 economic-first hybrids were tested over Stage4-derived turbo
gates, partial TQQQ blend weights and LRS factors. No candidate strictly beat
iter030 on all three target dimensions at once: CAGR, Sortino and MDD. The closest
variants either reduce LRS/TQQQ to improve Sortino/MDD with lower CAGR, or add
Stage4 turbo to improve CAGR with worse MDD/Sortino.

Constrained GA follow-up:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage4_hybrid_ga \
  --population 72 \
  --generations 35 \
  --elite 10 \
  --seed 42
```

Report:

- `reports/stage4_hybrid_ga/REPORT.md`

Observed result: the GA converged back to iter030 itself (`rearm`, full TQQQ
upgrade, LRS1.20). No discovered Stage4-conditioned turbo filter improved iter030
without worsening Sortino or MDD. This suggests GA is useful as a confirmation
tool here, but the current search grammar is not enough to create a strict Pareto
hybrid.

Iter030 parameter GA:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_iter030_param_ga \
  --population 36 \
  --generations 8 \
  --elite 8 \
  --seed 43

uv run python -m studies.technical_signal_vote_hunt.runners.analyze_iter030_param_ga_candidates

uv run python -m studies.technical_signal_vote_hunt.runners.validate_iter030_param_candidates
```

Reports:

- `reports/iter030_param_ga/REPORT.md`
- `reports/iter030_param_ga/CANDIDATE_DIAGNOSTICS.md`
- `reports/iter030_param_ga/validation/REPORT.md`

Observed result: the small GA evaluated 195 unique parameter genes and found 6
strict Pareto candidates in the top 30. The best candidate changes iter030 mainly
from `T35D60` to `T20D120`, reaching CAGR 39.01% vs iter030 36.66%, with similar
Sortino and unchanged full-period MDD. Rolling 5/10/15y minimum CAGR improves, but
the 3y minimum CAGR worsens and the result is a narrow full-history optimization;
honest validation of the 6 strict Pareto candidates plus baseline closed 0/7 PASS:
all pass OOS/FWD/WF/bootstrap, but all fail DSR (`p=0.2985..0.3711`) and the
195-gene PBO panel fails (`0.619`). It remains a useful economic sensitivity, not
a winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

Final local T/D sensitivity and study comparison:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_iter030_td_sensitivity
```

Report:

- `reports/iter030_td_sensitivity/REPORT.md`

Observed result: the constrained `T={20,35,45}` × `D={60,90,120}` grid shows that
the improvement comes from faster crash trigger plus longer rearm persistence.
`T20D120` is the best CAGR/terminal-equity variant (CAGR 39.01%, terminal 577.8k×),
while `T20D90` is the best balanced variant by Sortino (1.2278) with nearly the
same CAGR (38.99%) and identical full-period MDD. The cross-study comparison plots
include T3d-K2, iter030, Stage3 shared rules, Stage4 base votes, and Stage4-inside
iter030. Conclusion unchanged: stop this optimization branch; iter030 remains the
core anchor, and `T20D120`/`T20D90` remain economic sensitivities, not winners.

Interactive local webapp for the final T/D report:

Backend API:

```bash
uv run python -m studies.technical_signal_vote_hunt.webapp.api_server \
  --host 127.0.0.1 \
  --port 8765
```

Frontend React/Vite:

```bash
cd studies/technical_signal_vote_hunt/webapp/frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api/*` to the Python backend.
The frontend uses React + TypeScript, uPlot for high-performance equity/drawdown
charts, and custom Canvas heatmaps for rolling A/B diagnostics. The backend is a
dependency-free Python JSON API with in-memory series caching.

Legacy single-file app remains available:

```bash
uv run python -m studies.technical_signal_vote_hunt.webapp.iter030_td_report_app \
  --host 127.0.0.1 \
  --port 8765
```

Open `http://127.0.0.1:8765` for the legacy no-build HTML version.

Endpoints:

- `/api/strategies` for available strategies and date bounds.
- `/api/report?start=YYYY-MM-DD&end=YYYY-MM-DD&a=...&b=...` for metrics, equity,
  drawdowns and initial A/B summary.
- `/api/heatmap?...` remains available as a backend diagnostic, but the UI no
  longer calls it for normal A/B changes.

UI notes:

- `Overview` has uPlot equity/drawdown charts optimized for many curves, with
  short aliases and show/hide buttons.
- `Rolling A/B Heatmap` has two Plotly heatmaps side-by-side: `% days A>B` and
  window-end `equity_A/equity_B`.
- `Metrics` columns are sortable by click.
- `Strategies` uses accordion sections with implementation details for each
  strategy.

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

## Stage 3 Testfolio Price-Only GA

After the Tiingo comparison showed exceptional 2010+ results but weak 1986+
transplants, the next priority is long-history-first discovery. Stage 3 searches
testfolio 1986+ using only close-derived price signals and explicitly scores
candidates against T3d-K2 and iter030-like anchors before any Tiingo confirmation
`[advances_fin_ml, p.222-223]`.

Runner:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ \
  --risk-on QLD_2x \
  --off-leg ZROZSIM \
  --min-n 8 \
  --max-n 14 \
  --population 256 \
  --generations 120 \
  --elite 24 \
  --seed 42
```

Outputs land under
`results/stage3_testfolio_price_ga/<BRANCH>_<RISK_ON>_<OFF>_seed<SEED>/`:

- `anchors.csv`
- `best_by_generation.csv`
- `population_history.csv`
- `final_candidates.csv`
- `REPORT.md`
- `manifest.json`

Smoke test already passed:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ \
  --risk-on QLD_2x \
  --off-leg ZROZSIM \
  --population 12 \
  --generations 2 \
  --elite 4 \
  --min-n 8 \
  --max-n 8 \
  --signal-limit 12 \
  --seed 7 \
  --top-final 10
```

Suggested first real batch, one process at a time unless CPU budget is explicit:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ --risk-on QLD_2x --off-leg ZROZSIM \
  --min-n 8 --max-n 14 --population 256 --generations 120 --elite 24 --seed 42

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ --risk-on TQQQ_3x --off-leg ZROZSIM \
  --min-n 8 --max-n 14 --population 256 --generations 120 --elite 24 --seed 42

uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ --risk-on QLD_2x --off-leg CASHX \
  --min-n 8 --max-n 14 --population 256 --generations 120 --elite 24 --seed 43
```

Research order from here:

1. Testfolio 1986+ price-only hunt.
2. Tiingo 2006/2010+ confirmation for fixed long-history candidates.
3. Only then GA/beam search Tiingo `n>=8`.

Any Stage 3 survivor is still discovery-only until it clears WF/OOS/FWD,
bootstrap, PBO and DSR with cumulative trial accounting `[advances_fin_ml,
p.196-202]`, `[advances_fin_ml, p.208-211]`.

First full Stage 3 GA runs completed:

| Run | Unique candidates | Best Sortino | Best CAGR | Best MDD | Best rule |
|---|---:|---:|---:|---:|---|
| `QQQ_QLD_2x_ZROZSIM_seed42` | 6,250 | 1.3747 | 32.06% | -57.81% | `n=8/k=6` |
| `QQQ_TQQQ_3x_ZROZSIM_seed42` | 5,576 | 1.2680 | 40.28% | -64.24% | `n=8/k=6` |

Both best rules beat their branch-native T3d-K2 and iter030-like anchors on
Sortino, CAGR and MDD in-sample. They are promising long-history leads, but the
next step is validation, not promotion.

PBO-proxy GA follow-up:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_stage3_testfolio_price_ga \
  --branch QQQ --risk-on QLD_2x --off-leg ZROZSIM \
  --min-n 8 --max-n 14 --population 256 --generations 120 --elite 24 --seed 52 \
  --pbo-proxy-weight 0.75 --pbo-proxy-windows 8
```

This adds a walk-forward stability proxy to the GA fitness. It is not true PBO,
because true PBO is a panel/ranking statistic. The follow-up validation still
closed 0/400 pass and did not improve PBO materially; see
`reports/stage3_validation/REPORT.md`.

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

Stage 2 validator for selected Tiingo candidates:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.validate_stage2_tiingo_candidates \
  --candidates studies/technical_signal_vote_hunt/results/stage2_tiingo_ohlc/<RUN>/tables/stage2_local_results.csv \
  --out-dir studies/technical_signal_vote_hunt/reports/stage2_tiingo_validation/<VALIDATION_RUN> \
  --off-leg CASH_USD \
  --extra-lag-days 1 \
  --n-trials 122648244 \
  --bootstrap-n 2000 \
  --top 40 \
  --progress
```

Stage 3 fixed-rule Tiingo validation completed 2026-05-12:

- `reports/stage2_tiingo_validation/REPORT.md`
- Verdict: 0/80 pass.
- Existing Stage 2 Tiingo operational leads remain better than the Stage 3-derived
  local OHLC candidates.

Operational Stage 2 top-200 validation completed 2026-05-12:

- `reports/stage2_tiingo_validation/REPORT.md`
- `QQQ→QLD + CASH_USD lag1` top-200: 0/200 pass; OOS/FWD/bootstrap all pass,
  WF 187/200, DSR/PBO 0/200.
- `QQQ→TQQQ + CASH_USD lag1` top-200: 0/200 pass; OOS/FWD/bootstrap all pass,
  WF 186/200, DSR/PBO 0/200.

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
