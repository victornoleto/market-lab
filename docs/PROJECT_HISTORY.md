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
- `studies/weekly_momentum/` for weekly cross-sectional momentum diagnostics, including controlled sweeps, walk-forward validation, PIT approximation, Tiingo delisted backfill, and a final rejection after DSR/bootstrap gates `[advances_fin_ml, p.208-211]`;
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
