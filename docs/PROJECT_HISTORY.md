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
- `studies/spy_leveraged_rotation_hunt/` for a 2026-05-13 S&P 500 focused fork of
  the technical-vote/LETF-rotation work. It compares clean `SPY` underlying
  signals against `SSO` LETF self-signals for execution in `SSO/UPRO`. The initial
  baseline found no simple buy-hold/LRS/T3d transplant that beats `SPY buy_hold`
  on CAGR, Sharpe/Sortino and MaxDD simultaneously, while a controlled 6-evolution
  GA evaluated 7,008 unique candidates and found initial economic beaters. The
  best first-pass candidate is an `SSO` self-signal, not a clean `SPY` signal, so
  the conceptual caveat from the QLD audit remains. No candidate is validated or
  deployable without OOS/FWD/WF/bootstrap/PBO/DSR and cumulative trial accounting
  `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.222-223]`;
- `studies/weekly_momentum/` for weekly cross-sectional momentum diagnostics, including controlled sweeps, walk-forward validation, PIT approximation, Tiingo delisted backfill, and a final rejection after DSR/bootstrap gates. A later ETF-specific post-close diagnostic improved WF metrics only when leveraged/inverse ETFs remained available, but still failed DSR; the branch was closed research-only with no further local sweeps `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`;
- `studies/static_spy_beater_portfolio/` for a 2026-05-15 static-portfolio GA
  bootstrap. It searches long-only monthly-rebalanced ETF portfolios with 5%
  weight increments across `core_1986`, `mf_1988`, `global_1994` and `full_2000`
  universes. The scoring design combines full-period metrics with rolling
  1/3/5/10/15/20y relative scores versus `SPYSIM` and `QQQSIM`, weighting 10-20y
  windows most heavily and re-ranking GA finalists with all possible rolling starts.
  Initial work created the scaffold, universe audit, rolling scorer, GA runner and
  pareto report generator; the first `core_1986` smoke evaluated 7 portfolios for
  infrastructure only, with no winner/deploy claim `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`. Later same-day
  local B4-like work established `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM` as the
  no-margin internal core benchmark (CAGR `15.70%`, MDD `-29.94%`), stronger than
  the equal-weight B4 reference on CAGR/Calmar but still discovery-only. The study
  then pivoted to finding portfolios that beat this core by rolling equity dominance,
  with MDD treated as a guardrail rather than the main objective. A later
  factor/momentum probe added `VBRSIM`, `MTUMSIM` and `EFVSIM`; 3 GA seeds over the
  `1994-2026` common window all selected the original `35/40/25` core as exact rank 1,
  while factor sleeves failed to improve rolling equity dominance. The result supports
  retaining the core benchmark and moving to implementation/sensitivity checks, still
  with no winner/deploy claim. `FINAL_REPORT_35_40_25_CORE.md` then consolidated this
  internal research winner and documented that broad static optimization should stop in
  favor of drag/rebalance/start-date/remove-one-asset sensitivity checks
  `[ml_for_algo_trading, ch.4 p.82-93]`, `[advances_fin_ml, p.222-223]`;
- `studies/spy_beater_hunt_v2/` for a new 2026-05-13 autonomous hunt whose explicit goal is to beat SPY buy-and-hold while preserving hard overfit gates. It uses a short `MEMORY.md` plus a clean-session `loop.sh` orchestrator for OpenCode/GPT-5.5 iterations; initial status is bootstrap/audit only, with no mandate allocation change `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`;
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
- `studies/long_term_portfolio/` for long-horizon allocation experiments;
  On 2026-05-13, iter 058 combined the B4 core with repair-GA satellites under
  monthly rebalance plus USD 10k initial / USD 1k monthly contributions. The
  selected research allocation became `70% B4 + 30% evo02` after it beat 75/25
  on CAGR, MDD, Sharpe and XIRR (20.01% CAGR / -21.60% MDD / 19.74% XIRR vs B4
  14.62% / -28.38% / 14.17%). `75% B4 + 25% evo02` remains the more conservative
  alternative and `75% B4 + 25% evo01` had the highest Sharpe. The focused
  implementation guide lives at `studies/long_term_portfolio/B4_EVO02_70_30_IMPLEMENTATION.md`.
  These are still research-only portfolio compositions until the GA sleeves clear hard validation
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`;
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
