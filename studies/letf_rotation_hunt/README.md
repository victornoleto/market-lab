# LETF Rotation Hunt

Closed LETF rotation research study plus post-close diagnostics. The public
record is research-only: no capital reallocation is authorized and mandate §1
remains 100% Plano C `[advances_fin_ml, p.222-223]`.

## Canonical Status

| Area | Status | Canonical reference |
|---|---|---|
| Original 5-tier study | CLOSED | `reports/STUDY_FINAL_REPORT.md` |
| Sortino-first winner | T3d-K2 `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | `docs/state/WINNER_AND_RANKING.md` |
| Post-close loop 001-030 | CLOSED continuation | `reports/POST_CLOSE_LOOP_REPORT.md` |
| Tax-aware conclusion | Research-only ranking | `reports/T3D_K2_TAX_AWARE_CONCLUSION.md` |
| QQQ/NDX supplement | Benchmark criticism response | `reports/STUDY_QQQ_BENCHMARK_REPORT.md` |

## Structure

| Path | Purpose | Keep policy |
|---|---|---|
| `docs/state/BASE_MEMORY.md` | Original study state and iteration log | Canonical text |
| `docs/state/LOOP_MEMORY.md` | Post-close loop state and findings | Canonical text, can be summarized later |
| `docs/protocol/*.md` | Study and loop protocols | Keep |
| `configs/*.yaml` | Reproducible original study configs | Keep |
| `runs/original/*/SUMMARY.md` | Original iteration findings | Keep |
| `runs/post_close/*/{SUMMARY,REPORT,hypothesis}.md` | Post-close iteration findings | Keep |
| `runs/post_close/*/backtest.py` | Per-iteration reproduction script | Keep |
| `reports/*.md` | Human-readable reports | Keep |
| `core/` | Study engine, gates, scoring, signals, schemas and strategies | Keep |
| `runners/` | Original tier and loop entry points | Keep |
| `analyses/` | Side analyses: Sortino, tax, threshold, cohort, SOXL sweeps | Keep |
| `scripts/` | Report/regeneration utilities | Keep if referenced by reports |
| `tests/` | Study-specific regression tests | Keep |

## Generated Artifacts

Generated CSV/PNG outputs are intentionally not canonical. They are ignored or
removed when reports already preserve the relevant metrics and conclusions.

Regenerable examples:

- `*_strategy_returns.csv`
- `plots/`, `*_plots/`, `post_close_loop/plots/`
- `tables/*.csv` when duplicated in a report or `verdict.json`
- `annual_tax_events*.csv`, `realized_sale_events*.csv`
- `__pycache__/`, empty `logs/`

If a generated artifact becomes evidence, summarize it in a Markdown report or
promote a compact JSON/CSV table explicitly before cleanup.

## Original Tier Overview

| Tier | Hypothesis |
|---|---|
| T1 | Gayed replication: single LETF + SMA/EMA + binary OFF |
| T2 | HFEA-binary basket: multi-asset risk-on |
| T3 | Composite signal: SMA + VIX/AR1/vol-gate/Vote-K/HMM |
| T4 | Cross-sectional rotation: Clenow / EWMAC ranking |
| T5 | Continuous vol-target: Carver-style EWMAC |

## Regeneration Entry Points

```bash
# Original tier iterations
python -m studies.letf_rotation_hunt.runners.run_iter --iter 001 --config studies/letf_rotation_hunt/configs/iter_001_t1a_letf_sweep.yaml

# Post-close summary reports
python studies/letf_rotation_hunt/scripts/generate_loop_10_iter_report.py
python studies/letf_rotation_hunt/scripts/generate_loop_phase3_report.py
python studies/letf_rotation_hunt/scripts/generate_post_close_loop_report.py
```

Use `docs/CURRENT_STATE.md` for the public project snapshot and
`docs/investment-mandate.md` for capital-allocation constraints.
