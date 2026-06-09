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

Notable study areas include:

- `/var/www/victor/finances/letf-lab/studies/letf_rotation_hunt/` for the
  canonical LETF rotation research after the 2026-05-23 spin-off. This was
  formerly `market-lab/studies/letf_rotation_hunt/` and includes the T3d-K2
  closed-study anchor, the post-close `T35D60 + LRS1.20` research winner, the
  no-margin/tax diagnostics, and the tax-aware T3d-K2 conclusion. No capital
  reallocation followed from these results `[advances_fin_ml, p.222-223]`;
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
  balanced Sortino variant with nearly identical CAGR. A 2026-05-13 consolidated
  long-term review then reran the T/D comparison, audited the generated tables,
  and manually checked `T20D90` gates; it confirmed **iter030 canonical
  QLD/ZROZ LRS1.20** as the best long-term reference, with `T20D90/T20D120` kept
  as research-only economic sensitivities. The same-day underlying-signal audit
  then showed the family is QLD self-regime, not QQQ-underlying LRS: replacing
  QLD signals with QQQ signals degraded MDD to roughly `-91%..-94%`. A follow-on
  repair GA suite completed 6 evolutions: QQQ-signal repair reduced drawdown to
  roughly `-32%..-40%` at lower CAGR, while QLD-self-signal discovery found a new
  in-sample challenger `evo04` (Sortino 1.3751, CAGR 43.42%, MDD -52.73%). These
  results remain discovery-only pending cumulative DSR/PBO validation. The result
  remains economic sensitivity only, not a mandate winner, and the optimization
  branch should stop unless the next step is the pre-registered validation panel
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`;
- `/var/www/victor/finances/letf-lab/studies/spy_leveraged_rotation_hunt/`
  for a 2026-05-13 S&P 500 focused fork of the technical-vote/LETF-rotation
  work. It formerly lived under `market-lab/studies/` and compares clean `SPY`
  underlying signals against `SSO` LETF self-signals for execution in `SSO/UPRO`. The initial
  baseline found no simple buy-hold/LRS/T3d transplant that beats `SPY buy_hold`
  on CAGR, Sharpe/Sortino and MaxDD simultaneously, while a controlled 6-evolution
  GA evaluated 7,008 unique candidates and found initial economic beaters. The
  best first-pass candidate is an `SSO` self-signal, not a clean `SPY` signal, so
  the conceptual caveat from the QLD audit remains. No candidate is validated or
  deployable without OOS/FWD/WF/bootstrap/PBO/DSR and cumulative trial accounting
  `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.222-223]`;
- `/var/www/victor/finances/letf-lab/studies/lrs/` for a 2026-05-22 clean
  restart of the SMA-regime + LETF rotation lineage in a small, well-organized
  `phases/phase_N/` layout. It formerly lived under `market-lab/studies/`. Phase 0 was
  re-cast around a standardised scoring framework (cemented as the lrs
  evaluator for every later phase): each strategy is scored under two
  scenarios in parallel — tax-free and Brazil's **Lei 14.754/2023** (15%
  annual on net realised gain, indefinite loss carry-forward) — via
  rolling windows {1, 3, 5, 10, 15, 20}y at monthly step. The within-window
  composite is a signed `tanh`-squashed blend of `terminal_excess`,
  `time_above_excess`, `sortino_excess` and `calmar_excess` (B&H SPY is the
  universal benchmark); per-length aggregation is `0.60·mean + 0.40·p25`;
  across-length weighting puts ~70% on 10/15/20y. Modern-era window
  1980-01-02 → 2026-05-21 (pre-1980 bars kept only for SMA-200 warmup).
  In the tax-free world LRS-UPRO leads (+0.124); under Lei 14.754 the
  ranking flips and B&H SSO leads (+0.031) because annual tax penalises
  rotation turnover. Phase-1 then ran a 1,824-config sweep over filter
  (SMA/EMA) × lookback (20-300 step 5) × risk-off (CASH/GLD/IEF/ZROZ) ×
  on-leg (SSO/UPRO) × tax scenario. Headline finding: **the choice of
  risk-off asset dominates filter/lookback choices** — ZROZ wins all
  four panels, `SMA295/ZROZ` final score +0.43 tax-free and +0.35 under
  Lei 14.754. CASH (phase-0's default) is the worst off-leg in every
  panel. Top configs beat B&H SPY in 100% of 20-year rolling windows,
  but 912 untested configurations is significant overfit exposure;
  phase-2 will validate top-N via walk-forward + block bootstrap.
  Discovery-only under mandate §1 — no deploy claim
  `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.14, Table 6]`,
  `[leverage_for_the_long_run, p.21]`, Lei 14.754/2023 art. 5°/6°,
  `[advances_fin_ml, p.208-211]`;
- `studies/weekly_momentum/` for weekly cross-sectional momentum diagnostics, including controlled sweeps, walk-forward validation, PIT approximation, Tiingo delisted backfill, and a final rejection after DSR/bootstrap gates. A later ETF-specific post-close diagnostic improved WF metrics only when leveraged/inverse ETFs remained available, but still failed DSR; the branch was closed research-only with no further local sweeps `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`;
- `studies/return_stacked_core/` for the consolidated Return-Stacked Core (RSC)
  folder created on 2026-06-03. It replaces six previously separate trees:
  `b4-v2/`, `static_spy_beater_portfolio/`, `spy_beater_hunt/`,
  `spy_beater_hunt_v2/`, `long_term_portfolio/` and `global_factor_tilt_loop/`.
  The folder preserves the full intellectual path to RSC-US
  `35% GDE / 40% RSST / 25% ZROZ`: original SPY-beater no-winner hunts, old B4
  `25/25/25/25`, long-term static stack experiments, global factor-tilt evidence,
  static optimizer discovery, publication/robustness plots, old-B4 deep dives,
  B4+evo02 `70/30` satellite evidence and the RSC-Global branch
  `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`. RSC-US remains the clean
  US anchor (full-history CAGR about `15.65-15.70%`, MDD `-29.94%`), while
  RSC-Global is a diversification variant rather than a replacement. `CTAP` and
  `RSSX` remain optional implementation refinements. No mandate allocation changed.
  A 2026-06-09 partial canonical sleeve-return matrix for RSC-US core sleeves
  (`GDESIM/RSSTSIM/ZROZSIM` plus source sleeves) now unlocks exact US-core reruns;
  global/CTAP/RSSX sleeve matrices remain future artifacts. A same-day
  `us_core/four_asset_grid/` diagnostic then downloaded a separate Testfol.io
  payload for `NTSXSIM/GDESIM/ZROZSIM` plus `RSST70_30 = SPYSIM + 70% DBMFSIM +
  30% KMLMSIM - CASHX?E=-2`, evaluated `1,771` monthly-rebalanced `5%`-step
  portfolios, and ranked them by a Calmar/Sharpe/Sortino/CAGR/drawdown/volatility
  fitness blend. An earlier `CASHX?E=2` run was invalidated as a financing-sign
  error. The corrected top screen row is `40% GDESIM / 25% RSST70_30 / 35% ZROZSIM`
  (CAGR `12.15%`, MDD `-27.80%`, Sharpe `0.851`, Calmar `0.437`), while B4
  `25/25/25/25` scores lower (CAGR `11.23%`, MDD `-29.26%`) and the same-payload
  RSC-like `35/40/25` has CAGR `12.29%` with MDD `-30.76%`. A follow-up corrected
  `MARGIN_ANALYSIS.md` evaluated account-level IBKR-style leverage on the same top
  row: `1.25x` reached CAGR `13.97%` / MDD `-34.14%`, `1.50x` reached CAGR `15.66%`
  / MDD `-40.18%`, `2.00x` reached CAGR `18.69%` / MDD `-51.98%`, and `3.00x`
  reached CAGR `23.13%` / MDD `-71.40%`. The practical reading became more
  conservative: only `1.10x..1.25x` is worth any future research before real IBKR
  maintenance/financing/liquidation/tax checks; `1.50x+` is stress diagnostic. A
  subsequent corrected KMLM-only MF proxy diagnostic substituted `100% KMLMSIM` for
  the `70/30` DBMF/KMLM mix to gain the longer `1987-2026` window. It produced 1x
  CAGR `13.00%` / MDD `-26.70%`; at `1.25x` it reached CAGR `14.73%` with MDD
  `-33.01%`. That result is useful as a long-window managed-futures lens, but does
  not strengthen the case for external margin. A final same-day walk-forward
  anti-overfit pass (`8y` IS -> `2y` OOS, step `2y`) then selected the best weights
  only from prior data and held them in the next OOS block. It closed as a clear
  warning: WF-selected CAGR `12.57%`, MDD `-34.47%`, Sharpe `0.821`, terminal
  `8.37x`, versus fixed RSC-like `35/40/25` CAGR `12.63%`, MDD `-30.76%`, Sharpe
  `0.840`, terminal `8.45x`. The dynamic WF optimizer beat RSC-like in only `3/9`
  windows versus a `7/9` consistency threshold, selected `9/9` unique portfolios,
  and had mean train/test fitness Spearman `0.144`. A complementary robustness pass
  then ran WF sensitivity (`5y/1y`, `8y/2y`, `10y/2y`, `12y/3y`, expanding `8y/2y`),
  top-decile stability and CPCV/PBO on all `1,771` weights. It rejected the grid as
  a selection family: PBO `0.655`, CPCV beat RSC-like in only `7/28` splits versus a
  `21/28` consistency threshold, selected `20` unique portfolios, and had mean
  train/test Spearman `0.031`. The train top-decile map leaned toward high ZROZ and
  low RSST, but RSC-like still won the small fixed-rule OOS comparison by terminal
  wealth/CAGR. Therefore the full-sample top `40/25/35` remains a diagnostic screen,
  not a promoted allocation, and the defensible long-term rule remains a fixed thesis
  rather than grid reoptimization. This was implementation screening only; no mandate
  allocation changed, and metrics are not validation-gate evidence
  `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`,
  `[leverage_for_the_long_run, p.4-7]`, `[risk_parity, p.80-81]`,
  `[systematic_trading, p.185-188]`;
- a 2026-06-05 follow-up in
  `studies/return_stacked_core/us_core/reddit_leveraged_backtests/` compared 5
  Reddit/Testfol.io leveraged portfolio payloads against RSC-US. The best raw
  theoretical portfolio was 4-3-2-1 2x margin quarterly (CAGR `17.17%`, MDD
  `-27.98%`, Calmar `0.614`) but it requires explicit borrowing via negative
  cash. The best Reddit lead without explicit negative cash was the `mine`
  QQQ/TLT/GLD 3x mix (CAGR `16.11%`, MDD `-27.65%`, Calmar `0.583`) but it depends
  on synthetic 3x sleeves, especially Gold/TLT. The public verdict stayed
  unchanged: RSC-US `35/40/25` remains the implementable return-stacked anchor;
  the Reddit portfolios are seed ideas only unless translated to no-margin
  return-stacked exposures and validated through the repo gates
  `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`,
  `[advances_fin_ml, p.208-211]`;
- a second 2026-06-05 follow-up in
  `studies/return_stacked_core/us_core/factor_sleeve_diagnostics/` tested AVUV/SCV
  and SPMO as small factor sleeves funded from lower effective GDE/ZROZ exposure.
  Because Testfol.io did not accept `RSSTSIM`, the test used an effective-exposure
  proxy with `SPYSIM`, `GLDSIM`, managed-futures sims, `ZROZSIM`, factor sleeves
  and negative `CASHX` to represent embedded financing. Result: factor variants
  increased CAGR/terminal only marginally (`15.11%` baseline proxy to at most
  `15.33%`) while worsening MDD (`-27.47%` to as bad as `-31.08%`), beta,
  correlation to SPY and Calmar. No AVUV/SPMO variant replaced RSC-US `35/40/25`;
  factor sleeves remain sensitivity ideas rather than headline portfolio changes
  `[ml_for_algo_trading, ch.7 p.190-191]`, `[stocks_on_the_move, p.60]`,
  `[systematic_trading, p.185-188]`;
- a third 2026-06-05 follow-up in
  `studies/return_stacked_core/us_core/return_stacked_etf_universe/` screened the
  broader return-stacked/capital-efficient ETF universe using public issuer/search
  sources and three small no-Bearer Testfol.io wrapper payloads. The screen grouped
  current core components, US equity + managed-futures substitutes, stock/bond
  efficient-core funds, risk-parity products, bond/alt stacks, gold/inflation
  satellites and crypto/income wrappers. Verdict: no newly found ETF replaces
  RSC-US `35% GDE / 40% RSST / 25% ZROZ`; `CTAP` remains the only near-term
  optional manager/process split for the managed-futures sleeve, `RSSX` remains a
  small optional BTC-convexity sensitivity, and newer `MATE`/`JPFP`/`SPXP` products
  are watchlist only because their histories are too short. A same-day CTAP cost
  follow-up parsed Simplify holdings and estimated the visible non-SOFR drag at
  roughly `1.80%` current net / `1.98%` gross before taxes, tracking and exact
  collateral mechanics, so the CTAP split is documented as process diversification
  rather than a fee-efficiency claim. No mandate allocation changed
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
  `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`;
- `studies/spy_sso_upro_replacement/` for a 2026-05-25 static-first search for a
  low-turnover SPY replacement using `SPYSIM`, `SSOSIM`, `UPROSIM`, `ZROZSIM`,
  `GLDSIM`, `IEFSIM` and `CASHX`. Phase 1 evaluated a 5%-step static grid of
  `72,427` candidates on the 1968-2026 Testfol.io common window, triaged monthly
  portfolios, then recomputed finalists daily under monthly/quarterly/annual
  rebalance. Monthly static candidates did not pass the preferred target, but
  lower-frequency rebalance produced modest-leverage near-misses that pass the
  10y+ rolling-hit target. The current lead is `80% SPY / 5% SSO / 5% UPRO /
  5% ZROZ / 5% GLD` with quarterly rebalance: CAGR `11.47%`, MDD `-55.18%`,
  minimum 10y+ hit rate `93.3%`, terminal wealth `1.37x` versus SPY. The strict
  5y+ hit-rate target still fails, so the next work is Phase 1b implementation
  sensitivity rather than deployment. Phase 1b then ran a 1%-step local grid of
  `722,791` rows around the lead family, recomputed `1,260` exact cadence variants
  and found `647` preferred 10y+ rows but still `0` strict 5y+ rows. The best
  hit-rate row moved toward a very mild overlay (`89% SPY / 1% SSO / 4% UPRO /
  3% ZROZ / 3% GLD`, quarterly; CAGR `11.24%`, MDD `-55.13%`, min 10y+ hit
  `93.9%`, min 5y+ hit `79.8%`, terminal `1.21x` vs SPY). Conservative drag stress
  was the key negative: among exact preferred finalists, `70` survived 10 bps/year,
  but `0` survived 25 bps/year or 50 bps/year. The user then reframed the objective
  from SPY-like drawdown to benchmark-relative equity dominance. The next run removed
  redundant free `SPY/SSO/UPRO` mixes and used an explicit adjacent target-leverage
  ladder (`1x-2x = SPY/SSO`, `2x-3x = SSO/UPRO`), ranking `portfolio_equity / SPY_equity`
  with MDD as a diagnostic. This materially changed the result: `1,907` candidates,
  `173` dominance-pass rows after a 10y warmup and `0` full-period dominance rows;
  every pass was tactical SMA risk-on/risk-off, not static. The top row was
  `SMA200 L3.00 off 60 ZROZ / 40 GLD daily`, CAGR `19.38%`, MDD `-63.28%`, terminal
  `73.13x` versus SPY, minimum relative equity after 10y `1.31x`, and 10y+ rolling
  hit `95.1%`. The practical after-tax selection then excluded daily updates,
  used `AnnualDarfEngine` for Lei 14.754/2023 annual 15% realized-gain tax, and
  audited cadence masks by event count (monthly `698`, quarterly `233`, annual
  `59`). It evaluated `847` candidates: `280` active monthly/quarterly rows and
  `567` static monthly/quarterly/annual rows. Only 3 active rows passed practical
  after-tax dominance; static had 0 passes. The active lead became
  `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly` with after-tax CAGR `16.76%`, MDD
  `-73.74%`, terminal `23.75x` versus after-tax SPY, minimum relative equity after
  10y `1.28x`, and 10y+ hit `92.0%`. The best static row,
  `static L3.00 E60% GLD annual`, improved terminal wealth (`3.75x`) but failed
  dominance with min relative after 10y `0.68x` and 10y+ hit `53.1%`. No mandate
  allocation changed
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
  `[leverage_for_the_long_run, p.13]`;
- `studies/success_trading_strat/` for a 2026-05-14 research loop based on the
  Neurotrader/Masters strategy-development workflow: in-sample excellence,
  in-sample MCPT, walk-forward and WF-MCPT, added on top of the repository's
  PBO/DSR/bootstrap gates. Its first iteration was data-preservation only:
  final-day Tiingo audit, ETF/crypto/forex/NDX100 refresh, partial SPX500
  refresh and compressed backup `data/tiingo_backup_20260514-0311.tar.gz`.
  No strategy claim or mandate allocation change followed from this bootstrap.
  Iteration 002 then added reusable IS-MCPT/WF-MCPT scaffolding. Iterations
  003-006 tested small pre-registered families and all closed as `fail`: daily
  SPY/QQQ SMA-momentum failed PBO/MCPT; monthly cross-sectional ETF momentum
  passed PBO/DSR but failed MCPT, benchmark Sharpe and recent FWD stress;
  volatility-targeted static sleeves improved Sharpe/MDD versus 60/40 but failed
  IS-MCPT, WF-MCPT and PBO; and `RSI(2)` ETF mean reversion reduced drawdown but
  failed same-asset Sharpe plus IS/WF MCPT. Iteration 007 then pre-registered a
  volatility-carry proxy using `VIXY`, but closed `data_blocked` because the local
  Tiingo price file was absent; no substitution to `VXX` was made after
  pre-registration and no trials were consumed. Iteration 008 then
  pre-registered a new `VXX` proxy using confirmed local data. Best config
  `vxx_neg21_spy` improved Sharpe/MDD slightly versus SPY but lagged CAGR and
  failed IS MCPT (`p=0.145`), WF MCPT (`p=0.10`), PBO (`0.686`) and DSR
  (`p=0.0554`). Iteration 009 then pivoted to fixed multi-asset EWMAC over
  `SPY/QQQ/TLT/IEF/GLD` plus `SHV`; best config `ewmac_16_64_risk3` had positive
  CAGR and lower drawdown but lost Sharpe to equal-weight `SPY/QQQ/TLT` and failed
  IS MCPT (`p=0.165`), WF MCPT (`p=0.43`), PBO (`0.814`) and DSR (`p=0.1017`).
  Iteration 010 then pivoted to market-neutral ETF ratio z-score pairs
  (`GLD/SLV`, `TLT/IEF`, `SPY/QQQ`); best config `tlt_ief_z60_e1` had CAGR
  0.69%, Sharpe 0.183 and MDD -12.05%, but lost badly to SHV Sharpe and failed
  IS MCPT (`p=0.365`), WF MCPT (`p=0.53`), DSR (`p=0.9049`) and bootstrap.
  Iteration 011 then pivoted to VIX-managed equity exposure: best config
  `qqq_vix15_w21` had CAGR 14.10%, Sharpe 0.945 and MDD -27.01% versus QQQ
  buy-and-hold CAGR 18.94%, Sharpe 0.945 and MDD -35.12%. It passed IS MCPT
  (`p=0.000`), WF MCPT (`p=0.010`), PBO (`0.400`), DSR (`p=0.04697`), WF/OOS,
  bootstrap and cross-lib, but still closed `fail` because the last 63 trading
  days were negative (`-1.18%`). The study remains research-only with
  `cumulative_n_trials=32`; VIX is a promising mechanism for explicit stress, but
  not a winner while FWD stress fails `[paper.bozovic_2024_vix_managed,
  §methodology]`, `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`. Iteration 012
   then explicitly stressed the same VIX family with equity floors, a longer VIX
   window and a SPY/QQQ basket. Best `qqq_vix15_w21_floor50` improved to CAGR
   16.57% and Sharpe 0.954, but failed IS MCPT (`p=0.030`), PBO (`0.729`) and
   remained negative on the latest 63d FWD stress (`-0.41%`), so the VIX local
   stress branch also closed `fail` with `cumulative_n_trials=36`. Iteration 013
   then pivoted to BTC/ETH Donchian trend following using `SHV` as defensive
   sleeve. Best `eth_don20` had CAGR 66.12%, Sharpe 1.364 and MDD -35.51%,
   passing IS MCPT, WF MCPT, PBO (`0.286`), DSR (`p=0.00364`), OOS/bootstrap and
   cross-lib, but still closed `fail` because WF positives were 5/6 versus the
   pre-registered 6-positive requirement and latest 63d FWD stress was negative
   (`-6.85%`). `cumulative_n_trials=40`; mandate allocation remained unchanged
    `[paper.zarattini_2025_crypto_trends, §methodology]`, `[testing_tuning,
    p.318-320]`, `[advances_fin_ml, p.208-211]`. Iteration 014 then tested
    BTC/ETH volatility-targeted momentum as a non-Donchian pivot. Best
    `btc_mom63_vt20` improved Sharpe and drawdown versus BTC buy-and-hold but
    failed IS MCPT, WF MCPT, PBO and the required WF-positive count. Iteration 015
    pivoted away from crypto/VIX-local branches into realized-volatility
    compression plus positive momentum on `SPY/QQQ`; best `qqq_rv20_p60_m63`
    reduced drawdown versus QQQ buy-and-hold but lost Sharpe/CAGR and failed IS
    MCPT (`p=0.425`), WF MCPT (`p=0.490`), PBO (`0.514`), DSR (`p=0.2850`) and
    bootstrap. Iteration 016 tested a credit-risk appetite filter (`HYG/IEF`) and
    iteration 017 tested Carver-style diversified positive EWMAC forecasts; both
    reduced some drawdown diagnostics but failed benchmark Sharpe and/or
    MCPT/PBO/DSR. Iteration 018 then pivoted to an Ehlers cycle/Trend Mode overlay:
    best `qqq_ehlers_c30_t15` passed PBO, DSR, WF/OOS/FWD/bootstrap and beat QQQ
    Sharpe, but failed IS MCPT (`p=0.075`) and WF MCPT (`p=0.300`). Iteration 019
    tested yield/carry rotation and failed benchmark Sharpe, MCPT, PBO, DSR and
    recent FWD stress. Iteration 020 tested turn-of-month calendar seasonality;
    best `spy_tom_l1_f4` reduced drawdown but lost Sharpe/CAGR to SPY buy-hold
    and failed IS MCPT, WF MCPT, PBO and DSR. Iteration 021 tested adjusted-OHLC
    intraday/overnight decomposition; best `qqq_close_to_open` improved
    Sharpe/MDD but failed IS MCPT, WF MCPT and DSR. Iteration 022 tested
    KAMA/Efficiency Ratio adaptive timing; best `qqq_kama_er20` reduced drawdown
    but lost benchmark Sharpe and failed IS MCPT, WF MCPT and DSR. Iteration 023
    tested OBV volume-confirmation timing; best `qqq_obv21` improved Sharpe and
    drawdown versus QQQ buy-and-hold and passed PBO/DSR, WF/OOS/FWD, bootstrap
    and cross-lib, but failed IS MCPT (`p=0.020`) and WF MCPT (`p=0.180`).
    Iteration 024 then pivoted to close-location volume pressure via
    Accumulation/Distribution and Intraday Intensity. Best `qqq_ad21` had CAGR
    9.21%, Sharpe 0.700 and MDD -39.94% versus QQQ buy-and-hold CAGR 19.25%,
    Sharpe 0.958 and MDD -35.12%; it passed WF/OOS/FWD and cross-lib, but failed
    benchmark Sharpe, IS MCPT (`p=0.530`), WF MCPT (`p=0.830`), PBO (`0.900`),
    DSR (`p=0.3641`) and bootstrap. The study remained research-only with
    `cumulative_n_trials=84` and no mandate allocation change. Iteration 025 then
    pivoted to market breadth using a current large-cap constituent proxy. Best
    `spy_breadth_sma63_gt55` reduced MDD versus SPY buy-and-hold but lost Sharpe
    and failed IS MCPT (`p=0.210`), PBO (`0.829`) and DSR (`p=0.2173`), while the
    current-constituent survivorship caveat independently blocked promotion. The
    study remained research-only with `cumulative_n_trials=88` and no mandate
    allocation change. Iteration 026 tested sector relative-strength risk appetite
    (`XLY/XLP`, `XLK/XLU`) for `SPY/QQQ`; best `spy_xly_xlp_m126` reduced
    drawdown but failed benchmark Sharpe, IS/WF MCPT, PBO and DSR. Iteration 027
    pre-registered a commodity macro filter but closed `data_blocked` because
    `DBC.parquet` was unavailable, consuming zero trials. Iteration 028 tested a
    Gayed-style `QQQ` LETF rotation into `QLD/TQQQ` with `SHV` defense; best
    `qld_qqq_sma200_rv70` improved Sharpe/MDD versus QLD buy-and-hold and passed
    WF/OOS/FWD/bootstrap/cross-lib, but failed IS MCPT (`p=0.035`), PBO (`0.686`)
    and DSR (`p=0.0816`). Iteration 029 then tested equity/Treasury correlation
    breakdown as a separate risk filter; best `spy_corr63_lt0` lost to SPY
    buy-and-hold on Sharpe and failed IS MCPT (`p=0.810`), WF MCPT (`p=0.580`),
    DSR (`p=0.5240`) and bootstrap despite passing PBO (`0.103`), WF/OOS/FWD and
     cross-lib. The study reached `cumulative_n_trials=100` with no winner.
     Iteration 030 then performed the planned closure audit with no new strategy
     trials: all prior iteration directories had the required artifacts, summed
     prior `n_trials` matched 100, and no prior result had `winner=true`. The
     strict audit still closed `fail` because iteration 002 used a legacy
     infrastructure schema lacking the current `status`/`pre_registered` fields.
     The study is closed at the 30-iteration cap with no winner, no deploy
     implication and no mandate allocation change
     `[systematic_trading, p.40]`, `[volatility_trading, p.36]`,
    `[rocket_science, p.99-100]`, `[trading_systems_methods, p.479-481]`,
    `[trading_systems_methods, p.537]`, `[trading_systems_methods, p.540-541]`,
    `[trading_systems_methods, p.548-549]`, `[trading_systems_methods, p.941]`,
     `[trading_systems_methods, p.780-782]`,
     `[leverage_for_the_long_run, p.13]`,
     `[risk_parity, p.80-81]`, `[systematic_trading, p.170-171]`,
     `[advances_fin_ml, p.208-211]`. A consolidated post-loop review was then
     generated in `reports/overnight_30_iter_review/`, with summary tables,
     selected equity/drawdown/equity-over-SPY plots, rolling 1/3/5/10/15y
     diagnostics and gate-failure counts. It also introduced a pragmatic
     `candidate_watchlist` layer while preserving `strict_winner` as the original
     all-gates definition. `PHASE2_INTRADAY_SWING_SPEC.md` now documents the next
     intended focus: 15m/1h/1d swing tracks plus dedicated `GLD`/`XAUUSD` research,
     still requiring data-file audits before intraday tests and carrying no deploy
     implication. Phase 1 artifacts were moved to `iters/phase01/` and Phase 2 was
     prepared under `iters/phase02/`, resetting the active phase counter while
     preserving cumulative trial accounting at 100. Phase 2 iteration 001 then
     tested a daily `GLD`/`xauusd` Donchian-compression breakout after physical
     data audit. `GLD`/`xauusd` daily files existed, but `data/tiingo/1hour/prices/`
     had 0 parquet files, so intraday gold/XAUUSD remained blocked. Best
     `xau_dc100_rv20_p30` had CAGR 7.11%, Sharpe 0.726 and MDD -14.68% versus XAU
     buy-and-hold CAGR 18.17%, Sharpe 1.099 and MDD -20.36%; it closed `fail` on
     benchmark Sharpe, IS MCPT (`p=0.315`), WF MCPT (`p=0.220`), PBO (`0.615`),
      DSR (`p=0.7716`), WF sufficiency, FWD 63d and bootstrap, bringing cumulative
      trial accounting to 104 with no mandate allocation change
      `[testing_tuning, p.327-335]`, `[trading_systems_methods, p.353]`,
       `[trading_systems_methods, p.481]`, `[advances_fin_ml, p.208-211]`.
      Phase 2 iterations 002-023 then continued through daily gold/equity swing
      mechanisms while physical `1hour`/`15min` data remained unavailable. Iteration
      023 tested Money Flow Index pullbacks on `SPY`/`QQQ`/`GLD`; best
      `gld_mfi14_os20_x50_sma200_h10` had CAGR 1.90%, Sharpe 0.730 and MDD -4.88%
       versus GLD buy-and-hold CAGR 11.64%, Sharpe 0.693 and MDD -45.56%. It passed
       same-asset Sharpe, PBO, WF/OOS/FWD/bootstrap/cross-lib, but failed the Phase
       2 CAGR floor, IS MCPT, WF MCPT and DSR, leaving `cumulative_n_trials=192`,
       zero winners and no mandate allocation change `[trading_systems_methods,
       p.540]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`;
      Phase 2 iterations 024-029 continued daily swing mechanisms and all closed
      `fail`; iteration 030 then performed the planned closure audit with no new
      trials. The audit parsed 29 prior Phase 2 results, found all statuses `fail`,
      zero winners, zero watchlist/paper-trade promotions, complete required
      artifacts and local Phase 2 `n_trials=116` reconciled to global
      `cumulative_n_trials=216`. Phase 2 closed with no winner, no deploy implication
      and no mandate allocation change `[testing_tuning, p.318-320]`,
      `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`. A Phase 3
      spec was then created in `PHASE3_BH_BEATER_SPEC.md` to focus the next loop on
      buy-and-hold beating mechanisms rather than more defensive timing filters:
      LETF/controlled leverage, high-beta rotation, crash-rearmed exposure and
      explicitly modeled gross-exposure long/short tests. The spec makes CAGR and
      terminal wealth versus aligned B&H hard economic gates before any label above
      `fail`, while preserving MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib and no
      mandate allocation change. Phase 3 was then opened operationally with a
      fresh phase-local counter (`total_iterations=0`, `target_total_iterations=30`)
      while preserving global DSR trial accounting at `cumulative_n_trials=216`;
      `LOOP_PROMPT.md` now points future runs to `PHASE3_BH_BEATER_SPEC.md` and
      `iters/phase03/` `[systematic_trading, p.40]`,
      `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.222-223]`;
      Phase 3 iteration 001 then tested Nasdaq LETF volatility-targeted exposure
      over `QLD`/`TQQQ`. Best `qld_vt35_rv21_dd25_half` beat primary `QQQ`
      buy-and-hold economically (22.12% CAGR and 52.01x terminal wealth vs QQQ
      17.16% and 22.90x) but closed `economic_beater_not_validated` because IS
      MCPT (`p=0.050`), WF MCPT (`p=0.310`) and DSR (`p=0.1472`) failed; PBO,
      WF/OOS/FWD/bootstrap/cross-lib passed, cumulative trial accounting rose to
      222, and no mandate allocation change occurred `[leverage_for_the_long_run,
      p.13]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.222-223]`;
      Phase 3 iteration 002 then tested distinct S&P LETF volatility-targeted
      exposure over `SSO`/`UPRO`. Best `upro_vt40_rv63_dd30_half` beat primary
      `SPY` buy-and-hold economically (20.54% CAGR and 22.19x terminal wealth vs
      SPY 14.57% and 9.56x) but closed `economic_beater_not_validated` because IS
      MCPT (`p=0.565`), WF MCPT (`p=0.370`), DSR (`p=0.4551`) and bootstrap
       failed; PBO, WF/OOS/FWD/cross-lib passed, cumulative trial accounting rose
       to 228, and no mandate allocation change occurred `[leverage_for_the_long_run,
       p.5-7]`, `[leverage_for_the_long_run, p.13]`, `[systematic_trading,
       p.137-148]`, `[advances_fin_ml, p.222-223]`;
      Phase 3 iteration 003 then tested semiconductor/technology LETF volatility
      targeting over `SOXL`/`TECL`. Best `tecl_vt40_rv63` beat both primary
      benchmarks economically (`QQQ` and equal-weight `SMH/SOXX`) but closed
      `economic_beater_not_validated` because IS MCPT (`p=0.490`), WF MCPT
      (`p=0.670`) and DSR (`p=0.1636`) failed; PBO, WF/OOS/FWD/bootstrap/cross-lib
      passed and cumulative trial accounting rose to 234. Phase 3 iteration 004
      then tested Nasdaq crash-rearm (`QQQ` core plus temporary `QLD` booster).
      Best `qqq_qld_rearm_dd35_sma100_h189` beat `QQQ` buy-and-hold on CAGR and
      terminal wealth (18.64% and 27.79x vs 16.39% and 19.18x) but again closed
      `economic_beater_not_validated` because IS MCPT (`p=0.135`), WF MCPT
      (`p=0.550`) and DSR (`p=0.2006`) failed, with an additional joint-path MCPT
      caveat. PBO, WF/OOS/FWD/bootstrap/cross-lib passed, cumulative trial
      accounting rose to 240, and no mandate allocation change occurred. Phase 3
      iteration 005 then tested the S&P counterpart (`SPY` core plus temporary
      `SSO` booster). Best `spy_sso_rearm_dd35_sma100_h189` beat `SPY` buy-and-hold
      on CAGR and terminal wealth (13.05% and 10.87x vs 11.05% and 7.69x) but
      closed `economic_beater_not_validated` because IS MCPT (`p=0.095`), WF MCPT
      (`p=0.500`), PBO (`0.778`), DSR (`p=0.4147`) and bootstrap failed, with the
       same joint-path MCPT caveat. Cumulative trial accounting rose to 246, and no
       mandate allocation change occurred
       `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`,
       `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`. Phase 3
       iteration 006 tested high-beta relative rotation over `QQQ/SMH/SOXX/XLK`,
       and iteration 008 tested drawdown-adaptive gross exposure on the same
       universe; both beat the equal-weight opportunity benchmark economically but
       closed `economic_beater_not_validated` after MCPT/PBO/DSR failures.
        Iteration 007 attempted crypto/equity rotation but closed `data_blocked`
        because physical `BTCUSD`/`ETHUSD` daily parquets were absent. Iteration 009
        then tested explicitly financed high-beta long/short relative momentum;
        best `ls_m63_top1_bottom1_g100` lost badly to equal-weight buy-and-hold
        (CAGR -3.77%, terminal wealth 0.48x vs 19.18% and 28.26x), so it closed
        `fail` despite PBO pass, with cumulative trial accounting at 260 and no
        mandate allocation change `[stocks_on_the_move, p.66-67]`,
        `[trading_systems_methods, p.542-544]`, `[systematic_trading, p.137-148]`,
        `[testing_tuning, p.327-335]`;
        Phase 3 iterations 010-018 then investigated balanced LETF sleeves,
        HFEA-style sleeves, crash-rearmed Nasdaq exposure, gross `UPRO/TLT` spread
        exposure, and follow-up robustness audits. Several configs beat aligned
        buy-and-hold benchmarks economically, but none cleared the full validation
        stack. The final rolling 3y/5y economic audit of the iter 010-014 beaters
        found 128 failed candidate-window rows out of 534, confirming that the
        apparent economic beaters are not robust enough for promotion. Iteration
        018 then tested a distinct `VXX`-triggered Nasdaq crash-rearm and also
        beat `QQQ` buy-and-hold economically, but failed IS MCPT (`p=0.070`), WF
        MCPT (`p=0.070`), PBO (`0.790`) and DSR (`p=0.1111`). No winner,
        paper-trade label or mandate allocation change resulted; cumulative trial
        accounting reached 288
        `[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.4-7]`,
        `[advances_fin_ml, p.222-223]`. Phase 3 iterations 019-022 then tested
        LETF-light gross rotation, dynamic LETF risk parity, a consolidation audit,
        and a `QQQ` core plus conditional `QLD` overlay. Iteration 022's best overlay
        config beat `QQQ` buy-and-hold economically (23.19% CAGR and 56.02x
        terminal wealth vs 16.31% and 18.46x) but failed IS MCPT (`p=0.065`), WF
        MCPT (`p=0.260`), PBO (`0.738`), DSR (`p=0.2723`) and bootstrap. Phase 3
        therefore remained research-only at `cumulative_n_trials=300`, with zero
        strict winners and no mandate allocation change `[leverage_for_the_long_run,
        p.13]`, `[systematic_trading, p.137-148]`, `[testing_tuning, p.327-335]`,
        `[advances_fin_ml, p.222-223]`. Phase 3 iterations 023-030 then tested a
        sector-leadership overlay, `QLD/TLT/GLD` risk-migration and volatility-
        throttle sleeves, financing/rolling robustness stress, and two final
         closure audits. The strongest late beater (`QLD/TLT/GLD` volatility
         throttle) beat `QQQ` economically, but failed IS MCPT, WF MCPT and DSR;
         rolling 3y/5y stress also missed the 90% pass-rate threshold. Final closure
         parsed 29 prior Phase 3 results: 17 `economic_beater_not_validated`, 11
         `fail`, 1 `data_blocked`, zero winners and zero promotional labels. Phase 3
         closed at `cumulative_n_trials=312` with no paper trade, no deployment and
         no mandate allocation change. A consolidated review with CSV tables and
         comparative equity/drawdown/relative-performance plots was added at
         `studies/success_trading_strat/reports/phase3_bh_beater_review/`. A later
         economic-only Top 10 comparison across Phases 1-3 ranked strategies by
         terminal `equity/equity_SPY` and saved plots/tables under
         `studies/success_trading_strat/reports/top10_phase123_spy_relative/`, but
         did not change the no-deploy/no-winner verdict
         `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
         `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`;
- the former `studies/long_term_portfolio/` evidence now preserved inside
  `studies/return_stacked_core/history/`, including iter 058 `70% B4 + 30% evo02`
  (20.01% CAGR / -21.60% MDD / 19.74% XIRR vs B4 14.62% / -28.38% / 14.17%).
  These satellite compositions remain research-only until the GA sleeves clear hard
  validation `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`;
- `studies/_shared/` for reusable study infrastructure;
- `studies/_archive/` for closed or historical work.

## LETF Spin-Off

On 2026-05-23 the three canonical LETF rotation study trees moved out of
`market-lab` and into the sibling repository `/var/www/victor/finances/letf-lab`:
`lrs/`, `letf_rotation_hunt/` and `spy_leveraged_rotation_hunt/`. The new repo
keeps the CLI workbench and adds the FastAPI/Angular monitoring webapp. This
repository now keeps only shared helpers, non-LETF studies, historical references
and migration notes. See `MIGRATED.md` for the exact inventory and residual path
references.

## LRS Restart

On 2026-06-07 a new root-level `lrs/` folder reopened a research-only restart
of the Gayed/SMA leverage-rotation line inside `market-lab`, while the prior
canonical LETF study trees remain migrated to `/var/www/victor/finances/letf-lab`.
The restart begins from the original rule: risk-on in leveraged equity when the
underlying is above SMA200 and risk-off otherwise `[leverage_for_the_long_run,
p.13]`. The operating design is weekly execution, lag sensitivity `n=0..5`,
Brazil annual DARF modeling, later risk-off alternatives, sparse risk-on filters
and a possible bear-market inverse-ETF sleeve.

Phase 0 evaluated 24 baseline rows over SPY/QQQ 2x/3x branches with
`risk-off=CASHX`. The top score row was `SPY_3x` lag `2`, after-tax CAGR
`16.91%`, MDD `-88.33%`, Calmar `0.191`, terminal `8798.16x` vs after-tax SPY;
the best QQQ row was `QQQ_3x` lag `0`, after-tax CAGR `21.34%`, MDD `-91.97%`,
terminal `10.95x` vs after-tax QQQ. The conclusion is deliberately modest: the
baseline has long-run return, but drawdown remains too severe, so the next phase
should improve risk-off before adding indicator complexity. No deployment,
paper-trading label or mandate allocation change followed `[leverage_for_the_long_run,
p.4-7]`, `[advances_fin_ml, p.208-211]`.

Phase 1 then changed only the defensive sleeve while preserving weekly SMA200
signals and lag `n=0..5`. It evaluated 264 rows across cash, underlying,
GLD/IEF/ZROZ, fixed defensive baskets and momentum off-legs. The result changed
the local research direction: SPY 2x left ruin territory. The top score row was
`SPY_2x` with risk-off `40 ZROZ / 40 GLD / 20 IEF`, lag `5`, after-tax CAGR
`15.23%`, MDD `-41.34%`, Calmar `0.368`, terminal `11.03x` vs after-tax SPY.
`34` rows met the restart's practical `<=50%` drawdown target while beating the
underlying after tax, but they were all SPY 2x rows. SPY 3x remained warning-tier
and QQQ 2x/3x remained ruin-tier, so the next acceptable path is lower target
leverage, volatility throttling or bear-market sleeves before broad technical
indicator votes. No deployment, paper-trading label or mandate allocation change
followed `[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`.

Phase 2 then changed exposure geometry before adding broad indicator votes. It
evaluated 2,400 rows over SPY/QQQ, target leverage `1.25x..3.00x`, five selected
risk-off sleeves, five realized-volatility filters and lag `n=0..5`. The top
score row was `SPY` L`2.00` with risk-off `50 ZROZ / 25 GLD / 25 CASH`,
`RV21 <= 30%`, lag `3`, after-tax CAGR `15.44%`, MDD `-39.28%`, Calmar `0.393`
and terminal `12.28x` vs after-tax SPY. There were `875` practical-pass rows
(`MDD >= -50%` plus after-tax underlying outperformance) and `394` preferred
drawdown rows (`MDD >= -40%`). QQQ also left ruin territory: the best QQQ row
was L`1.75`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`, lag `0`,
after-tax CAGR `19.46%`, MDD `-42.58%`, Calmar `0.457` and terminal `5.82x` vs
after-tax QQQ. This remains exposure-geometry discovery only; no deployment,
paper-trading label or mandate allocation change followed
`[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`,
`[advances_fin_ml, p.208-211]`.

Phases 3A, 3A-2 and 3C then tested whether the Phase 2 geometry could be improved
by sparse confirmation filters, alternative regime forms or different SMA/EMA
lookbacks. The answer was negative for standalone LRS: no filter/form/window
reliably beat the SMA200-level base, and adaptive lookback lost net of turnover.
Phase 4 ran the mandate-style gate suite on six SMA200 bases and closed with
`0/6` passing all seven gates. Walk-forward robustness was the binding failure;
QQQ also failed PBO and DSR. LRS standalone was recorded as research-only and
closed, with no deployment, paper-trading label or mandate allocation change
`[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`.

On 2026-06-08/09 Phase 5 added a post-close core/satellite diagnostic and then
reran it with a rebuilt RSC-US `35/40/25` sleeve matrix. The matrix lives at
`studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`
and now reconstructs `RSSTSIM` from the user-requested Testfol.io tracking proxy:
`SPYSIM + 70% DBMFSIM + 30% KMLMSIM - (CASHX + 200 bps/year)`, equivalent to
`100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`. A no-auth Testfol.io audit
over the live RSST window showed terminal ratio `1.0025` and daily return
correlation `0.9275` versus RSST. Because `DBMFSIM` starts in 2000, the rebuilt
core window is now 2000+. Phase 5 tested `90/10`, `80/20` and `70/30` overlays
with local LRS SPY, local LRS QQQ and saved T3d-K2 satellites, including
underwater/recovery and relative-drawdown metrics. Result: `0/9` overlays passed
the strict rebuilt-sleeve screen. The rebuilt RSC same-window benchmark itself
was CAGR `12.40%`, MDD `-30.76%`, terminal `21.71x`, versus SPYSIM CAGR
`8.39%`, MDD `-55.14%`, terminal `8.34x` (`2.60x` ending wealth). The
highest-CAGR overlay was `70% RSC / 30% T3d-K2`, CAGR `14.24%`, MDD `-48.65%`.
A separate `lrs/TOP20_BY_CAGR.md` ranked `4183` LRS rows by CAGR with
no drawdown filter; top row was QQQ L`3.00`/ZROZ/RV63<=40%/lag5, CAGR `25.84%`,
MDD `-71.05%`. These are diagnostic leads only; account-level tax/friction and
mandate gates remain prerequisites before any promotion claim `[testing_tuning,
p.327-335]`, `[systematic_trading, p.185-188]`, `[risk_parity, p.80-81]`,
`[advances_fin_ml, p.208-211]`.

## Repository Slim-Down

On 2026-06-03 the cleanup/restructuring pass started by creating
`studies/SUMMARY.md`, a compact ledger of local studies, migrated LETF lines,
best leads, key metrics, verdicts and preservation/removal rules. The goal is to
make `market-lab` smaller and more direct while preserving the research record:
canonical reports, memories, specs and finalist tables stay; broad grids, GA
populations, caches and generated plots can be removed after their conclusions
are summarized. No strategy was promoted and the maintenance-mode mandate did
not change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

The same pass then consolidated six overlapping long-horizon/static-stack trees
into `studies/return_stacked_core/`, preserving reports, plots, CSV tables,
source ledgers and importable helpers while removing the old top-level folders.

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
