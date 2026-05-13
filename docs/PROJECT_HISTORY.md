# Project History

This file replaces the former personal `jornada/` notebook with a concise public
history. The original notebook was intentionally removed from the public-ready
tree because it contained session-level narrative and personal context.

## Phase 0: Knowledge Base

The project started by building a curated research knowledge base from trading,
portfolio construction, and financial machine-learning books. The operating rule
became: strategy choices, indicators, parameters and validation gates must cite
source material such as `[advances_fin_ml, p.208-211]`.

Raw copyrighted PDFs are not part of the public repository. Summaries and derived
knowledge notes remain when redistributable.

## Phase 1: Runtime Scaffold

Initial runtime infrastructure targeted broker/API integration, local database
storage, and monitoring. This remained mostly scaffold-level because research
validation did not justify live deployment.

## Phase 2: Backtest Engine

The core Python backtest stack was implemented under `src/market_lab/backtest/`:

- data sources and storage adapters;
- execution and portfolio accounting;
- metrics and reports;
- grid runners;
- validation methods including CPCV/PBO, DSR, walk-forward, bootstrap and
  cross-library checks.

The key engineering lesson was that strategy research must be reproducible across
independent implementations, not just one custom backtester.

## Phase 3: Strategy Research

Multiple strategy families were tested: trend-following, LETF rotation,
multi-asset allocation, volatility targeting, factor tilts, BR equity ranking,
and reverse-engineering public track records.

Most candidates failed because of one or more robustness gates:

- high probability of backtest overfitting;
- weak deflated Sharpe after accounting for trials;
- poor walk-forward stability;
- bootstrap confidence intervals crossing zero;
- cross-library disagreement or data-source sensitivity.

A look-ahead issue was found and fixed during the research process. After the
fix, previously attractive candidates were revalidated and rejected.

## Later Studies

Later work moved toward better organized research loops under `studies/`. The
most important convention is that each study should contain its own hypothesis,
scripts, outputs, reports and verdicts instead of writing to a global `reports/`
folder.

Notable preserved study areas include:

- `studies/letf_rotation_hunt/` for LETF rotation research;
- `studies/letf_rotation_hunt/runs/post_close/` for isolated post-close LETF
  research loops that benchmark against the frozen T3d-K2 winner without
  changing the closed study record or mandate allocation `[advances_fin_ml, p.222-223]`;
- `studies/letf_rotation_hunt/reports/POST_CLOSE_LOOP_REPORT.md` for the
  30-iteration post-close loop continuation. It documents the current research
  winner `T35D60 + LRS1.20` (Sortino 1.3839, CAGR 36.68%, PBO 0.0357), while
  preserving the mandate conclusion that no capital is reallocated;
- `studies/letf_rotation_hunt/runs/post_close/031-2026-05-10-tqqq-cash-proxy-annual-tax/`
  for the execution-realism diagnostic comparing taxed T3d-K2, a no-margin
  `80% TQQQ + 20% CASHX` turbo proxy with annual 15% realized-gain tax, and
  static SPY/NDX buy-and-hold. The proxy modestly beats taxed T3d-K2 but is not
  deploy-equivalent to the iter 030 gross research result;
- `studies/letf_rotation_hunt/runs/post_close/032-2026-05-10-taxed-underlying-riskon-variants/`
  for tax-aware underlying/risk-on variants and plots comparing equity,
  benchmark-relative equity, and rolling windows across TQQQ, SPY/SSO and
  SPY/UPRO variants;
- `studies/letf_rotation_hunt/reports/T3D_K2_TAX_AWARE_CONCLUSION.md` for the
  consolidated T3d-K2 tax-aware conclusion: simple baseline, balanced iter 30
  proxy, performance-first TQQQ variant, and rejected SPY transplants;
- `studies/technical_signal_vote_hunt/` for a follow-on research scaffold that
  generalizes T3d-K2 into `n`-signal / `k`-vote technical-indicator grids across
  branch-native SPY and QQQ LETF variants. Stage 1 uses long-history testfolio
  close-only signals and closed with 0/12 honest passes after global DSR trial
  accounting and diagnostic top-k PBO. A later GA/local-search pass found a
  stronger QQQ→QLD in-sample incumbent, and a QQQ→TQQQ performance-first
  challenger, but post-GA validation also closed 0/2 after cumulative DSR trial
  accounting. Stage 2 Tiingo OHLC was then implemented for real-inception ETF
  diagnostics; first QQQ pass found only marginal QLD improvement and a stronger
  TQQQ local lead using `ATR14% < 3%`, still discovery-only pending Stage 2
  honest validation. Overnight exact grids then evaluated 115M+ persisted
  configs and found mechanically reproducible but unvalidated high-CAGR leads
  across QQQ/TQQQ, QQQ/QLD, and SPY/UPRO; close-to-close execution sensitivity
  and cumulative DSR trial count remain the primary blockers. The next Stage 2
  operational pass added `CASH_USD`, explicit extra execution lag, and same-config
  redundant-signal exclusion; QQQ cash+lag1 exact `n<=5` grids found stronger
  discovery leads for TQQQ and QLD, while estimates showed exact `n<=7/8` grids
  require GA/beam search rather than routine enumeration. A follow-up window audit
  showed the original TQQQ-vs-QLD comparison was affected by inception windows:
  same-window QLD used the same top rule as TQQQ with lower CAGR but much lower
  MDD, while the close-only 1986+ testfolio proxy materially weakened the result
  versus T3d-K2 and iter030; a dedicated comparison report therefore classifies
  the selected Cfg01-Cfg05 leads as modern-regime challengers rather than robust
  long-history replacements. The follow-up priority is now Stage 3: search
  testfolio 1986+ price-only candidates against T3d-K2/iter030 first, use Tiingo
  2006/2010+ only as modern confirmation, and defer Tiingo `n>=8` GA/beam search
  until a long-history candidate exists. The initial Stage 3 GA runner produced
  first in-sample long-history leads for `QQQ→QLD+ZROZSIM` and
  `QQQ→TQQQ+ZROZSIM` that beat their branch-native anchors, but they remain
  discovery-only pending the full validation stack. Their first honest validation
  closed 0/400 pass after DSR and PBO failures, leaving the shared top rule only
  as a fixed Tiingo challenger. The subsequent Tiingo confirmation and one-edit
  OHLC expansion also closed 0/80 pass and did not improve on the existing Stage
  2 Tiingo frontier. Honest validation of the actual Stage 2 operational top-200
  QLD/TQQQ leads also closed 0/400 pass after DSR/PBO failures, while a final
  Stage 3 PBO-proxy GA follow-up failed to reduce PBO materially. A consolidated
  direction review in `studies/technical_signal_vote_hunt/reports/research_direction_review/REPORT.md`
  therefore stops unconstrained local optimization in the same technical-vote
  family and frames the next acceptable hypotheses as regime gating, explicit
  panel diversity, or PSR diagnostics that do not override DSR/PBO. After the
  user explicitly chose an economic-first research lens that temporarily treats
  PBO/DSR as diagnostics, Stage 4 added
  `studies/technical_signal_vote_hunt/runners/run_stage4_regime_bridge.py` and
  `reports/stage4_regime_bridge/REPORT.md`: QQQ→QLD/TQQQ `CASH_USD lag1` base
  vote passed OOS/FWD/WF/bootstrap plus rolling 3/5/10/15y cycle diagnostics in
  Tiingo 2010+, while simple regime overlays did not improve the frontier
  `[trading_systems_methods, p.732-733]`, `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.5-7]`.
  Follow-on Stage4/iter030 hybrid work found no strict Pareto improvement in a
  225-combo search or a constrained GA, but a broader iter030 parameter GA smoke
  evaluated 195 genes and found 6 economic-first strict Pareto candidates. The
  best candidate changes the post-crash rearm geometry from `T35D60` to
  `T20D120`, raising full-period CAGR from 36.66% to 39.01% with essentially
  unchanged Sortino/MDD; candidate diagnostics show better rolling 5/10/15y
  minima but a slightly worse rolling 3y minimum. Formal validation of the 6
  strict Pareto candidates plus baseline then closed 0/7 PASS: all passed
  OOS/FWD/WF/bootstrap, but all failed DSR and the 195-gene PBO panel failed
  (`0.619`). A final constrained `T={20,35,45}` × `D={60,90,120}` sensitivity
  then showed that faster crash trigger plus longer rearm persistence explains
  the gain: `T20D120` wins by CAGR/terminal equity, while `T20D90` is the best
  balanced Sortino variant with nearly identical CAGR. The result remains
  economic sensitivity only, not a mandate winner, and the optimization branch
  should stop with iter030 preserved as anchor `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`;
- `studies/weekly_momentum/` for weekly cross-sectional momentum diagnostics, including controlled sweeps, walk-forward validation, PIT approximation, Tiingo delisted backfill, and a final rejection after DSR/bootstrap gates. A later ETF-specific post-close diagnostic improved WF metrics only when leveraged/inverse ETFs remained available, but still failed DSR; the branch was closed research-only with no further local sweeps `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`;
- `studies/long_term_portfolio/` for long-horizon allocation experiments;
- `studies/_shared/` for reusable study infrastructure;
- `studies/_archive/` for closed or historical work.

## Maintenance Mode

The final public state is a research toolkit and historical lab, not a deployment
recommendation. Active strategy slots are dormant unless a future hypothesis is
explicitly re-opened and passes the hard validation gates documented in
`docs/investment-mandate.md`.

## Publication Cleanup

Before publication, personal content was moved out of this repository:

- the independent portfolio tracker app moved to `/var/www/pessoal/portfolio-tracker`;
- personal investment planning moved to `victor-ia/verticals/investments/`;
- Reddit drafts moved to `victor-ia/verticals/reddit/`;
- local session narrative was summarized here and removed;
- raw books, generated caches, private data and non-redistributable reference
  code were excluded.
