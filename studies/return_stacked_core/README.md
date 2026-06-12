# Return-Stacked Core

Status: **canonical consolidated research folder, discovery-only**.

This folder is the full map for the Return-Stacked Core (RSC) research line. It
collects the final RSC-US result, the global variant, the discussion/Reddit
explainers, the pre-registered improvement hunt, optimizer diagnostics, and the
legacy source material that led here.

No deployment, paper trading, capital reallocation or mandate change is authorized
by anything in this folder. The project remains in maintenance mode with capital
governed by `docs/investment-mandate.md`.

## What Replaced What

This folder replaces and summarizes the former research trees:

| Former tree | Current home for decision context |
|---|---|
| `studies/b4-v2/` | `STRATEGY.md`, `EVOLUTION.md`, `us_core/`, `ROBUSTNESS_REPORT.md`, `history/source_reports/` |
| `studies/static_spy_beater_portfolio/` | `EVOLUTION.md`, `history/source_reports/b4_v2_discovery_lineage.md` |
| `studies/spy_beater_hunt/` | `EVOLUTION.md`, `legacy_spy_beater/`, `history/source_reports/` |
| `studies/spy_beater_hunt_v2/` | `EVOLUTION.md`, `history/source_reports/` |
| `studies/long_term_portfolio/` | `EVOLUTION.md`, `history/source_reports/`, `history/old_b4/` |
| `studies/global_factor_tilt_loop/` | `global_variant/`, `history/global_factor_tilt/` |

The old labels `B4`, `B4-v2`, and `SPY beater` are retained only as historical
vocabulary in source reports and generated tables.

## Method Discipline

Tables in this folder use CAGR, MDD, Sharpe, Sortino, Calmar, terminal wealth,
rolling windows, start-date sensitivity, walk-forward checks, CPCV/PBO,
block-bootstrap tests, and fee/drag stress as research diagnostics. These are not
deployment gates by themselves; they are anti-overfit and robustness lenses
`[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

The RSC idea is a capital-efficiency design: preserve equity participation while
stacking diversifiers such as managed futures, gold, and duration inside fund or
simulation wrappers. Embedded leverage is treated differently from account-level
negative cash or retail margin `[leverage_for_the_long_run, p.13]`,
`[risk_parity, p.80-81]`.

## One-Page Verdict

| Question | Current answer |
|---|---|
| What is the canonical result? | **RSC-US `35% GDE / 40% RSST / 25% ZROZ`**, monthly rebalanced, long-only at fund-weight level, no external negative cash. |
| Is RSC-US deployed? | No. It is the strongest preserved research anchor, not an investment mandate change. |
| Did the later hunt find something definitively better? | No. `evolution/` is a terminal honest FAIL: `0` promoted candidates after eight pre-registered rounds. |
| Is `45/25/30 + 20% tolerance bands` promoted? | No. It is the strongest near-miss only; it fails the deep-validation battery and has cap-fragile neighbors. |
| Is RSC-Global better than RSC-US? | No on historical return. It is a diversification variant for geographic policy preference, not a replacement. |
| Did the four-asset optimizer replace the core? | No. Full-sample top rows were rejected by walk-forward instability and PBO `0.655`. |
| Did margin leverage become attractive? | No. Corrected financing sign (`CASHX?E=-2`) makes practical external leverage unattractive beyond roughly `1.10x..1.25x`, and even that remains unvalidated. |
| Did factor sleeves, Reddit portfolios, or new stacked ETFs replace RSC-US? | No. They produced useful diagnostics/watchlists, but no headline replacement. |

## Current Branches

| Branch | Allocation | Role | Standing |
|---|---|---|---|
| **RSC-US** | `35% GDE / 40% RSST / 25% ZROZ` | Clean US-centric return-stacked core. | Canonical research anchor. |
| **RSC-Global** | `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ` | Maximum-diversification global expression from the original global branch. | Diversification-first variant, not replacement. |
| **Balanced global** | `27.5% GDE / 7.5% NTSD / 30% RSST / 10% RSIT / 25% ZROZ` | Lower-cost globalness tier from the discussion package. | Preferred global expression if accepting moderate ex-US exposure. |

These allocation choices are research representatives of a plateau, not optimizer
argmax promotions. The anti-overfit rationale is documented in
`discussion/REPORT.md`, `discussion/REPORT_GLOBAL.md`, and `evolution/REPORT.md`
`[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

## Canonical RSC-US Metrics

Historical saved-curve backtest window: `1988-01-04..2026-04-17`.

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal wealth |
|---|---:|---:|---:|---:|---:|
| RSC-US `35/40/25` | `15.70%` | `-29.94%` | `1.040` | `0.524` | `265x` |
| Old B4 `25/25/25/25` | `14.43%` | `-27.92%` | `1.018` | `0.517` | `174x` |
| SPYSIM buy-hold | `11.46%` | `-55.14%` | `0.691` | `0.208` | `64x` |

Current local rerun with the adjusted RSST tracking proxy starts in 2000 because
`DBMFSIM` is the limiting sleeve.

| Portfolio | Window | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal wealth |
|---|---|---:|---:|---:|---:|---:|---:|
| RSC-US `35/40/25` adjusted RSST proxy | `2000-01-04..2026-05-21` | `12.40%` | `-30.76%` | `0.838` | `1.153` | `0.403` | `21.71x` |
| SPYSIM buy-hold | `2000-01-04..2026-05-21` | `8.39%` | `-55.14%` | `0.514` | `0.653` | `0.152` | `8.34x` |

Adjusted RSC terminal wealth is `2.60x` SPYSIM on the common window; the CAGR
spread is `+4.01pp/year`, and MDD improves by `+24.38pp`. Interpretation: RSC-US
remains a strong long-horizon, drawdown-efficient SPY challenger, but the adjusted
proxy should be read as a 2000+ tracking rerun, not as the old 1988 saved curve.

## RSC-US Mechanics

Canonical research expression:

```text
35% GDE / 40% RSST / 25% ZROZ
```

| Sleeve | Weight | Role | Embedded exposure |
|---|---:|---|---|
| `GDESIM` | `35%` | Capital-efficient US equity plus gold stack. | About `90% SPY + 90% Gold`. |
| `RSSTSIM` | `40%` | US equity plus managed-futures stack. | About `100% SPY + 70% DBMF + 30% KMLM - financing proxy`. |
| `ZROZSIM` | `25%` | Long zero-coupon Treasury convexity. | 25+ year duration. |

Approximate effective exposure is `71.5%` US large equity, `40.0%` managed
futures, `31.5%` gold, and `25.0%` zero-coupon Treasury exposure, for `168.0%`
positive exposure and about `1.68x` gross embedded exposure. This is fund-wrapper
or simulation leverage, not account-level margin
`[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`.

The current local `RSSTSIM` is reconstructed as:

```text
SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)
```

This is equivalent to the Testfol.io tracking payload:

```text
100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2
```

It is a repository tracking proxy, not a live ETF backfill. Because `DBMFSIM`
starts in 2000, this matrix no longer reproduces the older saved RSC curve;
expect non-trivial differences versus the historical 1988 saved series
`[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.

## Global Branch Verdict

`global_variant/REPORT.md` preserves the original clean RSC-Global branch:

```text
20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ
```

`discussion/REPORT_GLOBAL.md` later asked a stricter question: what is the best
possible global portfolio? Its answer is that the unconstrained historical optimum
is US-only, so the honest output is a price curve for globalness rather than a new
argmax strategy `[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

| Tier | Allocation | Primary read |
|---|---|---|
| Performance-first | US CORE `35 GDE / 40 RSST / 25 ZROZ` | Highest historical return in the tested universe. |
| Balanced global | `27.5 GDE / 7.5 NTSD / 30 RSST / 10 RSIT / 25 ZROZ` | Recommended global expression if accepting modest ex-US exposure. |
| Diversification-first | CORE-GLOBAL `20 GDE / 15 NTSD / 20 RSST / 20 RSIT / 25 ZROZ` | Maximizes the geography-policy expression; lower Sharpe plateau standing. |

The global work also found that international equity is mostly equity-risk
issuer diversification, not a crisis diversifier. RSIT-style international equity
plus managed futures is preferred over NTSD-only international exposure when an
ex-US sleeve is forced `[risk_parity, ch.5]`.

## Major Study Verdicts

| Study | Main files | Scope | Verdict |
|---|---|---|---|
| Canonical strategy | `STRATEGY.md`, `EVOLUTION.md` | Consolidated allocation, exposure map, implementation refinements, and lineage. | Keep RSC-US `35/40/25` as the research anchor. |
| Robustness audit | `ROBUSTNESS_REPORT.md`, `robustness_tables/` | Start-date, rolling, fee/drag, regime, and Monte Carlo diagnostics. | RSC-US is strong long-horizon research, but not a short-horizon SPY dominator. |
| US publication package | `us_core/REPORT.md` | Plots, saved series, implementation variants, RSSX risk-parity proxy, Monte Carlo. | RSC-US remains headline; CTAP/RSSX are optional implementation/satellite ideas. |
| Allocation plateau discussion | `discussion/REPORT.md` | 231-node `GDE/RSST/ZROZ` simplex, regimes, correlations, ablations, safe portfolios. | No single best node; `35/40/25` sits inside a robust plateau in `8/8` start windows. |
| Global discussion | `discussion/REPORT_GLOBAL.md` | 10,626-node global simplex, globalness price curve, constrained US/ex-US ratios. | US-only wins by backtest; global exposure is a policy choice with priced cost. |
| Pre-registered improvement hunt | `evolution/REPORT.md`, `evolution/TESTS_SUMMARY.md` | Eight rounds, `95,601` static trials, about `131,000` band/frequency/ballast configs, deep validation. | Terminal honest FAIL; nothing promoted. |
| Four-asset optimizer | `us_core/four_asset_grid/REPORT.md`, `WF_REPORT.md`, `ROBUSTNESS_REPORT.md` | `1,771` monthly grid portfolios over `NTSXSIM/GDESIM/RSST70_30/ZROZSIM`. | Full-grid top is not promoted; WF and PBO reject optimizer selection. |
| Margin and KMLM-only sweeps | `us_core/four_asset_grid/MARGIN_ANALYSIS.md`, `KMLM_ONLY_ANALYSIS.md` | Corrected external-leverage sweeps with `CASHX?E=-2`. | External margin is diagnostic only; unlevered remains the clean research profile. |
| Factor sleeve diagnostics | `us_core/factor_sleeve_diagnostics/REPORT.md` | AVUV/SPMO/VBR/momentum and managed-futures factor tests. | No factor variant dominates; SCV/momentum can be future tests, not core changes. |
| Stacked ETF universe | `us_core/return_stacked_etf_universe/REPORT.md` | Public-web ETF inventory, Testfol.io availability, CTAP fee/swap-cost note. | No new ETF replaces RSC-US; CTAP is a possible manager/process split, not a cost win. |
| Reddit leveraged portfolios | `us_core/reddit_leveraged_backtests/REPORT.md` | User-provided Testfol.io leveraged/margin portfolio comparisons. | Best raw leads need explicit margin or synthetic 3x assumptions; RSC-US remains cleaner. |

## Discussion Package

Path: `discussion/`.

The discussion package answers the external-explanation questions: whether
`35/40/25` is optimal, why the sleeves work, what happens in regimes, and why
common alternatives such as HFEA, SSO/UPRO, no-ZROZ, RSSX, RSSY, NTSX, and safe
unlevered portfolios do not replace the core.

| Area | Files/artifacts | What is preserved |
|---|---|---|
| Method and plan | `PLAN.md`, `METHODS.md`, `README.md` | Study charter, assumptions, methodology, limitations. |
| US analysis | `REPORT.md`, `s00_*.py` through `s08_*.py` | Anchor verification, series construction, episodes, correlations, simplex, ablations, 1970 extension, figures, safe-portfolio fetch. |
| Global analysis | `REPORT_GLOBAL.md`, `g00_*.py` through `g08_*.py` | Global anchor verification, global series, episodes, correlations, simplex, ablations, 1970 extension, figures, ratio-constrained analysis. |
| Generated tables | `tables/` | `35` CSVs covering simplex grids, plateaus, starts, correlations, episodes, ablations, global constrained grids, safe portfolios, and verification. |
| Generated series | `series/` | Primary/extended returns, global returns, portfolio equity files, metadata, and safe-portfolio equity. |
| Generated figures | `figures/` | `24` PNGs: US and global equity curves, underwater plots, episodes, rolling correlations, down-month behavior, frontiers, extensions, and ablation summaries. |
| Public drafts | `POST.md`, `POST_rETFs.md`, `POST_rLETFs.md`, `POST_GLOBAL_EXUS_FUTURE.md`, `IMAGE_CAPTIONS.md` | Reddit/posting drafts and caption support. |

Key facts from `discussion/REPORT.md`:

| Diagnostic | Result |
|---|---|
| 3-asset simplex | `231` 5%-step nodes over `GDE/RSST/ZROZ`. |
| Full-window argmax | `45/25/30`, Sharpe `0.866`. Not promoted. |
| CORE row | `35/40/25`, Sharpe `0.847`, 88th percentile. |
| Robust plateau | `60` contiguous nodes within `95%` of max Sharpe. |
| Start sensitivity | Argmax wanders, but CORE stays in the plateau in `8/8` starts. |
| ZROZ removal | Buys about `1.4pp` CAGR but deepens MDD by about `15pp`. |
| HFEA/SSO/UPRO | Higher leverage families are drawdown-dominated for this objective. |
| Safe portfolios | Golden Butterfly/Permanent/All Weather style mixes validate the diversifiers but trade away growth. |

## Evolution Improvement Hunt

Path: `evolution/`.

This is the most important anti-cherry-picking folder. It attempted to find a
portfolio or rebalance adjustment that definitively beats RSC-US while respecting
the user-chartered drawdown cap. The study was pre-registered in `PLAN.md`, run
by `make_all.py`, and summarized in `REPORT.md` and `TESTS_SUMMARY.md`.

| Item | Count/result |
|---|---:|
| Static grid trials | `95,601` raw / `74,193` unique |
| Band/frequency/ballast configs | about `131,700` |
| Pre-registered rounds | `8` |
| Deep-validation tests on unique candidate | `4` |
| Gauntlet finalists | `0` |
| Promoted allocation | `0` |

The unique near-miss is:

```text
45% GDE / 25% RSST / 30% ZROZ + 20% tolerance bands
```

It scored `5/6` gauntlet gates and `2/4` battery tests, but is not promoted. The
kill findings are ZROZ-neighborhood drawdown fragility and block-bootstrap failure;
the edge lives in the historical multi-month trend sequence and evaporates when
that sequence is resampled `[advances_fin_ml, p.222-223]`.

`OVERRIDE_DRAFT.md` is preserved only as an unsigned draft. It has no mandate or
allocation effect.

## Four-Asset Grid And Optimizer Diagnostics

Path: `us_core/four_asset_grid/`.

This folder tested whether adding `NTSXSIM` and optimizing a monthly four-asset
grid improves the core. It also corrected the financing sign on the RSST tracking
payload. The current canonical sign is `CASHX?E=-2`; older `CASHX?E=2` results are
invalid/stale `[systematic_trading, p.185-188]`.

| Diagnostic | Result |
|---|---|
| Grid scope | `1,771` portfolios over `NTSXSIM/GDESIM/RSST70_30/ZROZSIM`, 5% increments. |
| Full-grid top | `40% GDESIM / 25% RSST70_30 / 35% ZROZSIM`, CAGR `12.15%`, MDD `-27.80%`, Sharpe `0.851`. |
| Fixed RSC-like row | `35% GDESIM / 40% RSST70_30 / 25% ZROZSIM`, CAGR `12.29%`, MDD `-30.76%`. |
| Walk-forward | Selected optimizer beats fixed RSC-like in `3/9` windows; FAIL. |
| PBO | `0.655`; reject when PBO >= `0.5` `[advances_fin_ml, p.208-211]`. |
| CPCV | Beat fixed RSC-like in `7/28` splits, below the `21/28` consistency read. |
| Optimizer verdict | Useful stress map; do not reselect weights from the grid. |

Generated artifacts are in `results/`: full grid, asset curves, walk-forward
windows/equity/summary/stability, CPCV splits, PBO summary, fixed rules,
top-decile maps, margin sweep, and KMLM-only sweep.

## Implementation Refinements

Implementation refinements do not change the canonical backtest thesis. They are
product-risk or manager-risk diversification ideas, not claims of superior expected
return `[testing_tuning, p.327-335]`.

| Refinement | Working allocation | Standing |
|---|---|---|
| Split MF manager risk | `35% GDE / 22% RSST / 18% CTAP / 25% ZROZ` | Optional implementation refinement; CTAP is a manager/process split, not a fee win. |
| Split gold stack risk | `17.5% GDE / 17.5% RSSX / 22% RSST / 18% CTAP / 25% ZROZ` | Optional RSSX/BTC-sensitive refinement. |
| Global diversification | `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ` | Diversification-first variant. |
| Balanced global | `27.5% GDE / 7.5% NTSD / 30% RSST / 10% RSIT / 25% ZROZ` | Preferred moderate-global tier from `discussion/REPORT_GLOBAL.md`. |

## Folder Inventory

| Path | Contents |
|---|---|
| `README.md` | This map and verdict inventory. |
| `STRATEGY.md` | Canonical RSC-US allocation, adjusted RSST proxy, implementation split notes, RSSX/CTAP rationale. |
| `EVOLUTION.md` | Intellectual lineage from the old source folders to RSC-US and RSC-Global. |
| `ROBUSTNESS_REPORT.md` | Audit report over saved curves, Monte Carlo summaries, and adjusted sleeve matrix. |
| `datasets.py` | Data loading helpers for local study artifacts. |
| `proxies.py` | Proxy construction helpers used by the RSC study. |
| `synths.py` | Synthetic series helpers. |
| `ff_momentum_proxy.py` | Fama-French/momentum proxy helper for factor diagnostics. |
| `scoring.py` | Scoring helpers inherited from the legacy search work. |
| `rolling_windows.py` | Rolling-window utility code. |
| `run_iter.py` | Legacy iteration runner retained for compatibility/history. |
| `plot_helper.py`, `regenerate_color_plots.py` | Plotting utilities and color-plot regeneration helpers. |
| `export_sleeve_returns.py` | Deterministic exporter for the canonical RSC-US sleeve-return matrix. |
| `generate_robustness_report.py` | Rebuilds the robustness report/tables from preserved artifacts. |
| `us_core/` | US RSC report package, series, plots, implementation variants, Reddit support, factor diagnostics, ETF universe, four-asset grid. |
| `global_variant/` | Original RSC-Global package, selected series, grids, plots, and global Reddit draft. |
| `discussion/` | External discussion package: methods, US/global reports, scripts, tables, figures, series, Reddit posts. |
| `evolution/` | Pre-registered improvement hunt and terminal FAIL evidence. |
| `history/` | Source reports and preserved historical artifacts from the merged folders. |
| `legacy_spy_beater/` | Importable legacy helper modules from the SPY-beater hunt. |
| `legacy_algorithms/` | BAA G12 and composite momentum scripts retained for tests/history. |
| `robustness_tables/` | CSV audit tables generated by `generate_robustness_report.py`. |

## `us_core/` Inventory

| Path | Contents |
|---|---|
| `REPORT.md` | US publication package, adjusted RSST addendum, RSSX risk-parity proxy, implementation comparison, Monte Carlo summary. |
| `metrics.csv` | Canonical metric table for saved US curves. |
| `monte_carlo_sequence_risk.csv` | 20-year sequence-risk bootstrap summary. |
| `plot_manifest.csv` | Plot manifest for the US package. |
| `plots/` | Eight PNGs: full equity, relative wealth, implementation curves, drawdowns, rolling relative wealth/CAGR spread, Monte Carlo. |
| `series/full_equity_curves.csv` | Saved full-window US equity curves. |
| `series/implementation_equity_curves.csv` | Saved implementation-variant equity curves. |
| `series/remote_prices.parquet` | Downloaded/source price cache for US package work. |
| `series/return_stacked_core_sleeve_returns.parquet` | Canonical adjusted RSC-US sleeve-return matrix. |
| `series/return_stacked_core_sleeve_returns.meta.json` | Metadata for the sleeve-return matrix. |
| `series/rssx_rp_btc_weight_btc10.csv` | RSSX risk-parity BTC-weight path under the 10% BTC drift scenario. |
| `rssx_weights.csv`, `btc_weight_stats.csv` | RSSX/BTC weight diagnostics. |
| `REDDIT_POST_equity_mf_return_stacked_etfs.md`, `REDDIT_POST_rETFs.md`, `REDDIT_POST_rLETFs.md`, `REDDIT_IMAGE_CAPTIONS.md` | Public-draft support files. |
| `factor_sleeve_diagnostics/` | AVUV/SPMO/VBR/MF diagnostics with payloads, raw responses, derived CSVs. |
| `reddit_leveraged_backtests/` | User-provided Reddit portfolio comparisons with payloads, raw responses, derived CSVs. |
| `return_stacked_etf_universe/` | ETF universe triage with public-web notes, payloads, raw responses, derived CSVs, and plots. |
| `four_asset_grid/` | Monthly four-asset grid, WF, PBO/CPCV, margin and KMLM-only diagnostics. |

## `global_variant/` Inventory

| Path | Contents |
|---|---|
| `REPORT.md` | Original RSC-Global research report and candidate comparison. |
| `global_grid_candidates.csv` | Candidate grid rows for global branch selection. |
| `global_manual_metrics.csv` | Manual global candidate metrics. |
| `global_monte_carlo_sequence_risk.csv` | Global sequence-risk bootstrap summary. |
| `series/global_selected_equity.csv` | Saved selected global equity curves. |
| `series/remote_prices.parquet` | Downloaded/source price cache for global package work. |
| `plots/` | Six PNGs: global equity, benchmark comparisons, drawdowns, rolling relative wealth, Monte Carlo. |
| `REDDIT_POST_GLOBAL.md` | Public-draft global post. |

## `history/` Inventory

| Path | Contents |
|---|---|
| `history/source_reports/` | `24` original compact reports from old B4, long-term portfolio, SPY-beater, and related work. |
| `history/old_b4/` | Five old-B4 iteration reports, including NTSX/GDE/KMLM, global stack, international tilt, and TLT-sleeve reports. |
| `history/b4_evo02_70_30/` | B4+evo02 70/30 report, runner, plots, and tables. |
| `history/global_factor_tilt/` | Preserved global-factor source memory, dead ends, external instruments, selected iterations, tax engine, and winner/ranking notes. |

## Sleeve-Return Artifacts

| Artifact | Scope | Status |
|---|---|---|
| `us_core/series/return_stacked_core_sleeve_returns.parquet` | RSC-US core sleeves: `GDESIM`, `RSSTSIM`, `ZROZSIM`, plus source/helper sleeves. | Created 2026-06-09; revised to adjusted RSST tracking proxy. |
| `us_core/series/return_stacked_core_sleeve_returns.meta.json` | Source window, columns, and construction metadata. | Read with the parquet. |
| `export_sleeve_returns.py` | Deterministic exporter for the RSC-US sleeve matrix. | Rebuilds parquet and metadata. |

Current matrix caveat: it is the adjusted 2000+ RSST tracking-proxy matrix. It is
not a complete implementation matrix for CTAP, RSSX, NTSD, RSIT, NTSI, VTI, VEA,
or VT.

## Reproducibility Entry Points

| Command | Purpose |
|---|---|
| `uv run python studies/return_stacked_core/export_sleeve_returns.py` | Rebuild canonical adjusted RSC-US sleeve-return parquet and metadata. |
| `uv run python studies/return_stacked_core/generate_robustness_report.py` | Regenerate robustness audit tables/report from preserved artifacts. |
| `uv run python studies/return_stacked_core/discussion/make_all.py` | Rebuild the discussion package. Some optional network fetches depend on external availability. |
| `uv run python studies/return_stacked_core/evolution/make_all.py` | Rebuild the pre-registered evolution hunt outputs. |

Generated CSVs and PNGs are audit/support artifacts. The narrative verdicts live
in the reports, and those reports should be read before using a table row as a
claim.

## Open Blockers

The useful next engineering artifact is a broader canonical sleeve-level daily
return matrix for `CTAP`, `RSSX_RP`, `NTSD`, `RSIT`, `NTSI`, `VTI`, `VEA` and
`VT`. The core US `GDE/RSST/ZROZ` matrix already exists.

That broader matrix is required before exact checks for:

- monthly versus quarterly/semiannual/annual rebalance;
- remove-one-sleeve attribution;
- threshold/tolerance-band rebalancing;
- cleaner implementation drag and tax stress.

Until that matrix exists, implementation variants remain optional refinements and
not new research winners.
