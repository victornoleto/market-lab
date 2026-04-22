# Lead V2-L3 — AFML triple-barrier + meta-label (honest revalidation)

**Phase:** 3.5f | **Lead:** V2-L3 — AFML triple-barrier + RandomForest meta-label
**Date:** 2026-04-22
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**F2 engine-fix commit:** `7b90a8f` (`fix(backtest): shift weight×return alignment to remove lookahead bias`)
**Tested:** 1 config × 12 tickers = 12 runs (frozen from Phase 3.5a-V2 aggregator iter 57)
**Path tag:** [SHORT-HOLD CFD]

---

## Verdict

**FAIL — RECONFIRMED. Engine was clean; previous numbers stand unchanged.**

- 0/12 tickers PASS the 13-gate framework (§5.5 of the plan).
- The V2-L3 family was ALREADY DEAD END under the original sweep (iter 57, 2026-04-19).
- **No re-simulation is required.** F1 scope audit (`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`) confirmed that `src/ai_trade/backtest/strategies/afml_tb_meta.py` is **single-ticker** meta-labeling: no multi-asset weight vector, no `w_i × r_i` pattern, no look-ahead bug to fix. The V2-L3 report was listed under **CLEAN** in F1 alongside L1/L5/L6. The F2 fix (commit `7b90a8f`) touched `plano_a_leveraged_rotation.py` only.
- The previous DEAD-END reasoning stands: meta-labeling is a **precision filter on an existing edge, not an edge generator** `[advances_fin_ml, p.50]`. The EMA-50 cross primary on single-asset ETFs is too thin; residual CAGR (best 2.50% XLF) is dwarfed by Pepperstone Razor round-trip + swap costs on 6-14d holds `[systematic_trading, p.185-188]`.

---

## Summary table (frozen from the original sweep)

Source: `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/AGGREGATE.md` (iter 57).
**These numbers are honest**: the underlying engine (`afml_tb_meta.py`) never carried the w×r look-ahead bug that was isolated in F1.

| Ticker | Window     | OOS Sharpe | OOS CAGR | OOS MaxDD | Median hold (d) | Events taken | PASS |
|--------|------------|-----------:|---------:|----------:|----------------:|-------------:|:----:|
| XLF    | 2003-2026  | **1.213**  | 2.50%    | -0.76%    | 7.5             | 14           |  No  |
| XLI    | 2014-2026  | 0.945      | 3.55%    | -6.61%    | 8.5             | 34           |  No  |
| QQQ    | 2001-2026  | 0.924      | 2.46%    | -3.07%    | 6.5             | -            |  No  |
| XLE    | 2003-2026  | 0.789      | 6.90%    | -9.12%    | 9.0             | -            |  No  |
| EFA    | 2003-2026  | 0.645      | 2.16%    | -3.06%    | 6.0             | -            |  No  |
| XLU    | 2003-2026  | 0.445      | 3.18%    | -7.23%    | 14.0            | 52           |  No  |
| SPY    | 2001-2026  | 0.147      | 0.60%    | -6.76%    | 7.0             | -            |  No  |
| XLY    | 2014-2026  | 0.116      | 0.66%    | -13.22%   | 6.0             | 24           |  No  |
| XLV    | 2014-2026  | 0.101      | 0.33%    | -5.87%    | 12.0            | 17           |  No  |
| XLK    | 2003-2026  | 0.000      | 0.00%    | 0.00%     | 7.0             | 7            |  No  |
| GLD    | 2004-2026  | -0.097     | -0.12%   | -2.17%    | 6.0             | -            |  No  |
| TLT    | 2002-2026  | -0.166     | -0.36%   | -4.14%    | 7.0             | -            |  No  |

**Best-Sharpe ticker (XLF):** OOS Sharpe 1.213 / OOS CAGR 2.50% / OOS MaxDD -0.76%.

---

## 13-gate checklist per §5.5 (CDI-floor soft-gate for gate 3 per 2026-04-22 override)

Applied to the **best-Sharpe config (XLF)** — the only ticker with a non-trivial positive Sharpe. If XLF fails, every other ticker fails a fortiori.

| # | Gate (§5.5) | Threshold | XLF value | Status |
|---|---|---|---|:---:|
| 1 | Bootstrap 99.9% CI low > 0 on OOS + full-period Sharpe `[advances_fin_ml, p.196-202]` | CI_low > 0 | N/A (not computed in original sweep; Sharpe 1.213 is modest and the sweep predates the bootstrap gate) | UNKNOWN → treat as FAIL |
| 2 | OOS Sharpe ≥ 2.0 (relaxable to ≥ 1.5 with user approval) | ≥ 2.0 | 1.213 | FAIL |
| 3 | OOS CAGR ≥ 30% (soft floor CDI BR ~13% per user override 2026-04-22) | ≥ 13% (soft) | 2.50% | FAIL (below CDI floor by ~10×) |
| 4 | OOS MaxDD ≥ -25% (binding, no relaxation) | ≥ -25% | -0.76% | PASS |
| 5 | FWD Sharpe > 0 on 2024-2026 | > 0 | Mixed (3/12 tickers FWD=0: GLD, TLT, XLK); XLF not isolated in original aggregator | UNKNOWN → treat as FAIL |
| 6 | Walk-forward 8 windows: ≥ 6/8 profitable, max window DD ≤ 25% | 6/8, DD ≤ 25% | Not computed (single-config per ticker, no WF grid) | FAIL |
| 7 | Median hold ≥ 3 trading days | ≥ 3d | 7.5d | PASS |
| 8 | IR vs SPY ≥ 0.5 on OOS | ≥ 0.5 | Not computed | UNKNOWN → treat as FAIL |
| 9 | Cross-lib concordance ≥ 2/3 of {bt, vectorbt, backtrader} within ±3pp CAGR | ≥ 2/3 | Not executed (engine is CLEAN per F1; cross-lib check unnecessary to confirm FAIL verdict) | N/A |
| 10 | Stage-2 data concordance Tiingo `adj_close` vs testfolio SIM within ±1pp CAGR OOS+FWD | ≤ 1pp | Not executed (same reason as #9) | N/A |
| 11 | PBO < 0.5 via CSCV 10-block (if grid ≥ 5 configs) `[advances_fin_ml, p.208-211]` | < 0.5 | Not applicable — 1 config × 12 tickers, grid is cross-sectional not parametric | N/A |
| 12 | DSR p < 0.05 on winner OOS Sharpe (if grid ≥ 5 configs) `[advances_fin_ml, p.196-202]` | < 0.05 | Not applicable (same reason) | N/A |
| 13 | Cost sensitivity: 2× cost bps still OOS Sharpe > 1.0 | > 1.0 at 2× cost | Not computed; at 1× cost XLF Sharpe is 1.213 with CAGR 2.50% — doubling costs ≈ −0.5pp CAGR drives Sharpe toward ~0.7 | FAIL (projected) |

**Gate counts:** PASS 2 (gates 4, 7) / FAIL 6 (gates 1, 2, 3, 5, 6, 8, 13 — 7 actually failing) / N/A 3 (gates 9, 10 unneeded; 11, 12 inapplicable).

Recount: PASS 2 / FAIL 7 / N/A 4. Either way: **VERDICT = FAIL**, zero bypass per `docs/investment-mandate.md §2.5`.

Gate 3 notes: even with the user-approved CDI-floor soft-gate (~13%/yr net per mandate §2), XLF's 2.50% OOS CAGR falls short by a factor of ~5×. The binding gate 4 (MaxDD ≥ -25%) passes cleanly — meta-labeling does deliver the AFML-promised low-drawdown profile `[advances_fin_ml, p.50-54]` — but precision without alpha does not clear the CDI floor.

---

## Why no re-simulation is required

Per `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` (F1, commit `7c280a2`):

- The engine module `src/ai_trade/backtest/strategies/afml_tb_meta.py` is **single-ticker**: it produces a labeled event-return series from a single primary+meta pipeline and compounds it directly. There is **no multi-asset weight vector** and thus no `w_i × r_i` multiplication at any bar, which is the specific shape of the F2-fixed bug in `plano_a_leveraged_rotation.py:462`.
- `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/` was explicitly categorized as **CLEAN** in the F1 inventory table (alongside V2-L1, V2-L5, V2-L6).
- The F2 fix (commit `7b90a8f`) shifted the weight×return alignment to `w_{i-1} × r_i` in `plano_a_leveraged_rotation.py` only — no other engine was touched, no V2-L3 code path was modified.
- Consequently, the original iter-57 numbers ARE the honest numbers for V2-L3. Running the sweep again would reproduce identical output within numerical noise.

The previous DEAD verdict (`jornada/2026-04-19/02-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`) is **not an artifact of a biased engine**: it was a genuine, meta-labeling-specific failure where the primary signal (EMA-50 cross on single-asset ETFs) is too thin for the RF precision filter to convert into a CAGR that survives Pepperstone Razor round-trip costs on 6-14d holds.

---

## Citation

- Triple-barrier + meta-labeling as a **precision filter on an existing edge** (not edge generator): `[advances_fin_ml, p.31-34, p.54-60]`. AFML is explicit that meta-labeling enhances recall/precision on a signal whose raw Sharpe must already be positive; it does not manufacture alpha where none exists.
- Timing / look-ahead detection protocol used in F0-F2: `[advances_fin_ml, p.31-34]`.
- Hold-length cost amortization ceiling (6-14d × Razor RT ≈ 11bps + swap): `[systematic_trading, p.185-188]`.
- Single-asset trend thinness (applies to the EMA-50 primary): `[stocks_on_the_move, p.81]`.

---

## Links

- Original DEAD jornada: `jornada/2026-04-19/02-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`.
- Original aggregate (iter 57, honest): `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/AGGREGATE.md`.
- F1 scope finding: `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`.
- F2 engine fix commit: `7b90a8f`.
- Plan: `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` §F3, §5.5.
