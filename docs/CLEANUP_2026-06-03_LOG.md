# Cleanup Log — 2026-06-03 Partial Consolidation

Scope: first safe slim-down pass after the user request to make `market-lab`
smaller and more direct without losing research knowledge.

This is not the full aggressive cleanup from `docs/CLEANUP.md`. The working tree
already had thousands of pending `studies/` changes before this pass, so this run
intentionally avoided broad code moves, rewrites, git tags and commits. No
pre-existing user changes were reverted.

## Baseline Observations

| Item | Size or status |
|---|---:|
| Repository working directory | `1.9G` |
| `.venv/` | `880M` |
| `.git/` | `396M` |
| `studies/` | `578M` |
| `data/` | `70M` |
| `src/` | `1.7M` |
| `tests/` | `3.5M` |
| `git status --short` count before edits | `2806` entries |

Primary generated-artifact hotspot:

| Path | Size | Classification |
|---|---:|---|
| `studies/spy_sso_upro_replacement/results/phase1b_fine_local_summary.csv` | `473M` | Broad 1% local-grid triage, generated/regenerable. |
| `studies/spy_sso_upro_replacement/results/static_grid_summary.csv` | `47M` | Broad static monthly-grid triage, generated/regenerable. |
| `studies/spy_sso_upro_replacement/results/` | `526M` total | Keep final reports/finalists; remove broad grids after summary. |

## Preserved Knowledge

Created `studies/SUMMARY.md` as the compact canonical ledger for study cleanup.
It records:

- current RSC-US champion: `35% GDE / 40% RSST / 25% ZROZ`;
- RSC discovery lineage formerly split across `static_spy_beater_portfolio/`;
- local study status, best leads, metrics, verdicts and canonical files;
- migrated LETF lines and their new canonical home in `letf-lab`;
- condensed `success_trading_strat` family ledger;
- preservation/removal rules for future cleanup.

Updated public/index docs to point to the new ledger:

- `README.md`;
- `studies/README.md`;
- `docs/CURRENT_STATE.md`;
- `docs/PROJECT_HISTORY.md`.

## Removed Generated Artifacts

The broad grid CSVs below were removed because their conclusions are preserved in
`studies/SUMMARY.md`, `studies/spy_sso_upro_replacement/PHASE1B_REPORT.md`,
`studies/spy_sso_upro_replacement/EQUITY_DOMINANCE_REPORT.md`,
`studies/spy_sso_upro_replacement/PRACTICAL_TAXED_REPORT.md` and the smaller
finalist/candidate CSVs left in `results/`.

| Removed path | Approx. size | Recovery/regeneration |
|---|---:|---|
| `studies/spy_sso_upro_replacement/results/phase1b_fine_local_summary.csv` | `473M` | Regenerate with `uv run python studies/spy_sso_upro_replacement/run_phase1b_robustness.py` if the full broad grid is needed again. |
| `studies/spy_sso_upro_replacement/results/static_grid_summary.csv` | `47M` | Regenerate with `uv run python studies/spy_sso_upro_replacement/run_static_grid.py` if the full broad grid is needed again. |

## Compacted Static B4-v2 Workbench

`studies/static_spy_beater_portfolio/` was compacted after its discovery
knowledge was consolidated into `studies/return_stacked_core/EVOLUTION.md` and
`studies/return_stacked_core/history/source_reports/`.

Preserved facts include:

- final no-margin core: `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`;
- exact 1988-2026 metrics: CAGR `15.70%`, MDD `-29.94%`, Calmar `0.524`;
- rejected aggressive LETF/duration barbells with MDD around `-81%..-84%`;
- rejected GA robust/aggressive challengers that bought small CAGR gains with much
  worse drawdown;
- factor/momentum and stacked-ETF probes that converged back to the core.

The old broad optimizer scripts, generated reports and plot artifacts were removed
from the active tree. They remain recoverable from git history if a future
pre-registered hypothesis justifies restarting broad static optimization. More
local search without a new hypothesis would add multiple-testing risk
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Compacted SPY-Beater Legacy Studies

`studies/spy_beater_hunt/` was reduced to importable root helpers plus compact
docs. The old `iterations/` tree, session prompt and rerun script were removed
after adding `ITERATION_LEDGER.md` and replacing the large operational
`BASE_MEMORY.md` with a closed-state summary. Root Python helpers remain because
`tests/test_studies_spy_beater_hunt.py` imports them.

`studies/spy_beater_hunt_v2/` was compacted from an open loop into a no-winner
reference. The autonomous loop scripts and per-iteration artifacts were removed;
`MEMORY.md`, `SPEC.md` and `reports/STRATEGY_COMPARISON.md` preserve the 10/10 fail
verdict. Reopening requires a distinct cited mechanism and strict trial budget.

## Consolidated Old B4 Deep Dive

The 2026-05-05 B4 deep-dive branch under `studies/long_term_portfolio/` was
compacted into `studies/return_stacked_core/history/source_reports/` because it
analyzed the old `25% NTSX / 25% GDE / 25% RSST / 25% ZROZ` B4 base rather than
the current `35% GDE / 40% RSST / 25% ZROZ` RSC-US core.

Preserved facts include:

- iter056 short-window ranking where `P4b BTGD 10%` had Sharpe `1.017`, while the
  corrected `RSSX` proxy fell behind after replacing the wrong `100% SPY + 100% BTC`
  assumption with `100% SPY + 65% Gold + 35% BTC`;
- iter057 global-fork ranking where old B4 US-only had Sharpe `1.027` and the
  best `70/30` global variant had Sharpe `0.925`;
- the conclusion that these are lineage/sensitivity results, not replacements for
  the canonical RSC-US `35/40/25` core.

Removed active-tree artifacts:

| Removed path | Reason |
|---|---|
| `studies/long_term_portfolio/B4_DEEP_DIVE_2026-05-05.md` | Superseded by compact legacy note; old plot links pointed to absent PNGs. |
| `studies/long_term_portfolio/B4_GLOBAL_FORK_ANALYSIS.md` | Superseded by compact legacy note. |
| `studies/long_term_portfolio/B4_GLOBAL_FORK_compare_table.md` | Key table rows preserved in compact legacy note. |
| `scripts/long_term_portfolio/*` | Stale regeneration helpers for iter056/057; not imported by tests after runner removal. |
| `studies/long_term_portfolio/iterations/056-*` and `057-*` run/report files | Conclusions preserved; details recoverable from git history if a new cited hypothesis requires them. |

## Consolidated Return-Stacked Core Folder

Follow-up consolidation merged six overlapping folders into one canonical strategy
folder: `studies/return_stacked_core/`.

Merged source folders:

- `studies/b4-v2/`;
- `studies/static_spy_beater_portfolio/`;
- `studies/spy_beater_hunt/`;
- `studies/spy_beater_hunt_v2/`;
- `studies/long_term_portfolio/`;
- `studies/global_factor_tilt_loop/`.

Preserved in the new folder:

- RSC-US strategy report, robustness report and evolution ledger;
- RSC-US plots/series/CSV artifacts under `us_core/`;
- RSC-Global plots/series/CSV artifacts under `global_variant/`;
- robustness CSV audit tables under `robustness_tables/`;
- old B4 `25/25/25/25`, B4+evo02 `70/30`, global factor-tilt and no-winner hunt
  source reports under `history/`;
- importable long-term and legacy SPY-beater helpers under the new package;
- BAA G12 and composite momentum legacy algorithms needed by tests.

The consolidated strategy name is **Return-Stacked Core (RSC)**. RSC-US is
`35% GDE / 40% RSST / 25% ZROZ`; RSC-Global is
`20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`. No mandate impact.

## Residual Cleanup Candidates

These were not removed in this pass:

| Candidate | Reason deferred |
|---|---|
| `data/testfolio/*.json` raw API dumps | Keep until confirming `data/testfolio/cache/history.parquet` plus metadata are sufficient for every current runner. |
| `studies/return_stacked_core/**/remote_prices.parquet` | Small enough; RSC is the current research package, so avoid touching until canonical sleeve-return matrix work is resolved. |
| Dormant Python strategy/grid modules | Low size impact and import coupling with tests/studies; remove only in a later src+tests cleanup pass. |
| Runners still pointing at migrated `studies/letf_rotation_hunt` paths | Need either explicit archive or redirect to `/var/www/victor/finances/letf-lab`; no runtime behavior changed in this pass. |

## Verification Plan

Minimum verification after this partial pass:

- `uv run pytest --collect-only -q` is the preferred safety check for import breakage.
- Full `uv run pytest` is recommended only after the pre-existing dirty working tree is reconciled, because `MIGRATED.md` already documents pre-existing test failures unrelated to this pass.

## Mandate Impact

None. No strategy was promoted. `market-lab` remains in maintenance mode and the
cleanup follows the same robustness/overfit discipline used by the studies:
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
