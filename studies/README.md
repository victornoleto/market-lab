# studies/ - Research Index

This directory holds market-lab research studies, their scripts, outputs and
verdicts. The repository remains in maintenance mode: no study here authorizes
capital allocation or live trading without a future mandate override.

On 2026-05-23 the canonical LETF rotation work moved to the sibling repository
`/var/www/victor/finances/letf-lab`. See `../MIGRATED.md` before reviving any
LETF benchmark, runner or webapp work from this tree.

## Canonical Summary

Read `SUMMARY.md` first for the compact ledger of all local studies, migrated
LETF lines, best leads, key metrics, verdicts and cleanup preservation rules.

## Current And Reference Studies

| study | status | canonical read | notes |
|---|---|---|---|
| `return_stacked_core/` | canonical consolidated RSC folder, concluded | `README.md`, `STRATEGY.md`, `EVOLUTION.md`, `ROBUSTNESS_REPORT.md` | Replaces `b4-v2/`, `static_spy_beater_portfolio/`, `spy_beater_hunt/`, `spy_beater_hunt_v2/`, `long_term_portfolio/` and `global_factor_tilt_loop/`. Current anchor is RSC-US `35% GDE / 40% RSST / 25% ZROZ`; RSC-Global is the diversification branch. Research-only, no deploy. |

## Closed Studies Kept In Place

These directories remain top-level because they still contain useful audit trails,
reports, scripts or importable helpers. Do not move them without checking tests and
imports first.

| study | status | canonical read | notes |
|---|---|---|---|
| `weekly_momentum/` | closed, no deploy | `FINAL_REPORT.md`, `README.md` | Stock and ETF weekly momentum failed DSR/PBO/bootstrap after PIT/backfill improvements `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`. |
| `success_trading_strat/` | closed, no winner | `MEMORY.md` | Three phases, 312 cumulative trials, no strict winner or paper-trade candidate. |
| `day_swing_strategy_hunt/` | closed/dead-end | `MEMORY.md`, latest `iterations/*/SUMMARY.md` | Reopen only with an explicit new multi-asset, literature-backed thesis or reliable carry/rates data. |
| `bestfolio_meta_wf_hunt/` | closed/dead-end | `SPEC.md` | Iter 001 closed the bestfolio-style meta-WF branch; no iter 002 was run. |
| `myfxbook_reverse_engineering/` | closed/no operable edge | `README.md`, `ROADMAP.md` | MyFxBook/HappyForex reverse-engineering code and tests are retained; no Plano A implication. |
| `technical_signal_vote_hunt/` | closed/research-only LETF-adjacent | `README.md`, `reports/long_term_strategy_review/REPORT.md` | Generalized QQQ/SPY technical-vote LETF work; no honest winner after DSR/PBO, residual benchmarks now point to `letf-lab`. |
| `qld_nasdaq_ath_gate/` | quick diagnostic, not validated | `README.md`, `results/default/report.md` | QQQ high-watermark gate into QLD/CASHX; no costs, taxes or robustness gates. Treat as LETF-adjacent historical evidence. |

## Migrated LETF Studies

Canonical copies now live in `letf-lab`:

| former market-lab path | new canonical path |
|---|---|
| `studies/lrs/` | `/var/www/victor/finances/letf-lab/studies/lrs/` |
| `studies/letf_rotation_hunt/` | `/var/www/victor/finances/letf-lab/studies/letf_rotation_hunt/` |
| `studies/spy_leveraged_rotation_hunt/` | `/var/www/victor/finances/letf-lab/studies/spy_leveraged_rotation_hunt/` |

Market-lab keeps only shared infrastructure and historical references that other
non-LETF studies still import. If a runner needs iter030/T3d-K2 artifacts, either
point it explicitly at `letf-lab` or copy a small canonical artifact bundle back
under the consuming study with a clear README.

## Shared And Archive

| path | role |
|---|---|
| `_shared/` | Reusable study helpers such as tax, signals, scoring, plotting, gates and walk-forward utilities. |
| `_archive/` | Historical studies already compacted or intentionally archived. |

## Navigation Rules

- Latest public state: read `../docs/CURRENT_STATE.md`.
- Compact strategy/study ledger: read `SUMMARY.md`.
- Historical narrative: read `../docs/PROJECT_HISTORY.md`.
- LETF spin-off inventory: read `../MIGRATED.md`.
- Study-specific truth: prefer each study's final report, `MEMORY.md`, `BASE_MEMORY.md` or `SPEC.md` over this index.
- Validation gates remain hard-blocks unless the mandate changes: PBO, DSR, walk-forward, OOS/FWD stress, bootstrap and cross-library checks `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- When a public status changes, update `../docs/CURRENT_STATE.md`; update `../docs/PROJECT_HISTORY.md` too if the change is historical or narrative.
