# spy_beater_hunt Iteration Ledger

Status: compact ledger for the closed legacy `spy_beater_hunt` study.

The old per-iteration directories were removed from the active tree on 2026-06-03.
This file preserves the conclusions needed for navigation; full raw artifacts are
recoverable from git history.

## Core Verdict

No strict winner was found. The useful outcome was negative/structural knowledge
plus a historical B4 family that was later superseded by B4-v2.

## Iteration Families

| Iterations | Family | Best or anchor | Verdict |
|---|---|---|---|
| 001-010 | LRS, HFEA, vol-target and early static/levered controls. | Gayed/LRS and HFEA variants produced economic leads but failed robustness or drawdown requirements. | No winner; established need for stricter anti-overfit gates. |
| 011 | Impossibility/meta synthesis of the first block. | Best score below winner threshold. | Closed first direction; negative result preserved. |
| 012-017 | Concentrated growth, TSMOM, levered all-weather and gated HFEA variants. | Several CAGR passers, but path risk and gate instability remained binding. | No promotion. |
| 018-036 | Meta-ensemble axis over LRS/gated/all-weather constituents. | Best strategy-level score `74`; iter 035/036 replicated the apex but exposed PBO grid-composition noise. | Research ceiling below WINNER tier. |
| 037-039 | Sensitivity, static-stack sweep and Reddit comparison package. | Static capital-efficient stack family became the practical historical branch. | Useful public/reference material, not current champion. |
| 040-044 | Community feedback: monthly rebalance, real ERs, TQQQ regime gate, international stack, walk-forward weight drift and unified ranking. | B4 Conservative initially promoted as historical balanced pick with net CAGR `12.84%`, MDD `-28.94%`, Sharpe `0.745`. | Later superseded by RSST-corrected iter 045 and then B4-v2. |
| 045 | RSST proxy correction. | Corrected B4: CAGR `11.00%`, MDD `-29.60%`, Sharpe `0.671`; L1 CEGB: CAGR `9.66%`, MDD `-25.43%`, Sharpe `0.696`. | B4 stayed balanced; L1 CEGB became low-risk Sharpe reference. |
| 046 | Factor tilt and NDX deleveraged follow-up. | `B4_scv10_from_ntsx` mildly lifted CAGR to `11.23%` but worsened MDD to `-31.06%`; NDX variants kept MDD `-72%..-76%`. | No core improvement. |
| 047 | Bitcoin sleeve on corrected B4. | `B4 + 2.5% BTC` and `B4 + 5% BTC` improved 2010+ CAGR, but the window is BTC-constrained and favorable. | Optional/aggressive satellite only, not gate-equivalent. |
| 048-051 | B4 overlays and LETF risk-on variants with tax. | No-LETF overlay `SMA150` had small after-tax improvement; LETF variants bought CAGR with worse drawdown. | Watchlist only; static core retained. |
| 052-055 | Momentum, SCV and factor/crypto satellite funding. | SPMO/FMTM/VBR/MTUM/BTC satellites were interesting in short/proxy windows, but B4/B4+BTC5 remained better risk-adjusted. | Satellite preference, not core improvement. |

## What Was Removed

- `iterations/` per-run scripts, generated reports, JSON outputs and plots.
- `SESSION_PROMPT.md` and `rerun_all_iters.sh`, because the loop is closed.

## What Stayed

- Importable root helper modules used by tests.
- `TOP_STRATEGIES.md` and `WINNER_AND_RANKING.md` for historical rankings/rubric.
- This compact ledger and compact `BASE_MEMORY.md`.

## Recovery Policy

Use git history to recover a specific deleted run. Do not restart a local sweep or
parameter search from this lineage unless the new hypothesis is pre-registered and
has a distinct cited mechanism `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`.
