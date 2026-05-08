# V2-L6 Vol Breakout — Honest Reconfirmation (Phase 3.5f / F3 slice)

| Field | Value |
|---|---|
| **Lead** | V2-L6 Donchian vol-breakout (multi-asset 1/N, 10 ETFs, daily) |
| **Date** | 2026-04-22 |
| **F2 commit (engine fix)** | `7b90a8f` — `fix(backtest): shift weight×return alignment to remove lookahead bias` |
| **Branch** | `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422` |
| **Plan ref** | `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md §F3` + `§5.5` |
| **F1 inventory** | `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` (L6 listed CLEAN) |
| **Original report** | `reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md` (iter 80, 2026-04-19) |
| **Original narrative** | `jornada/2026-04-19/06-phase3.5a-v2-L6-vol-breakout-DEAD.md` |

---

## Verdict

**FAIL (reconfirmed — 12/12 OOS Sharpe negative, engine was clean).**

V2-L6 uses `src/market_lab/backtest/strategies/donchian_breakout.py`, which F1
confirmed **does NOT contain the `w_i × r_i` lookahead pattern** isolated to
`plano_a_leveraged_rotation.py:462` (fixed in F2 commit `7b90a8f`). The engine
driving L6 was honest from the start; therefore the original DEAD verdict
stands **structurally** — no re-simulation is warranted or performed.

Per plan §F3 L6 priority note: *"removing lookahead bias typically makes
negatives MORE negative, not positive"* — which is moot here since L6's
engine never had the bug.

---

## No re-simulation performed

**Justification:** F1 inventory (`2026-04-22-engine-lookahead-scope.md`,
Strategy Module Inventory table and "Clean Strategy Modules" §) explicitly
lists `donchian_breakout.py` under **NO** bug column and under the "modules
confirmed free of the look-ahead pattern and should not be modified in F2"
list. The F2 patch (commit `7b90a8f`) touched only
`plano_a_leveraged_rotation.py`, which L6 does not import. Running the
honest engine on L6 would produce numerically identical daily returns to the
original report (bit-exact, modulo RNG seeds for bootstrap which are fixed).

Re-executing 12 configs × 3088 daily bars purely to re-derive known-identical
numbers has zero epistemic value `[advances_fin_ml, p.31-34]` — the honest
verdict is inherited directly from the original run.

---

## Summary table — OOS Sharpe from original run (all 12 configs)

Source: `reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md` (ordered by
OOS Sharpe desc). OOS window = 2022-01-03 → 2024-12-31 (753 daily bars).

| Config | IS Sharpe | **OOS Sharpe** | OOS CAGR | FWD Sharpe | WF | OOS MDD | MedHold |
|---|---:|---:|---:|---:|:---|---:|---:|
| `vol_donch20_atr3x_long`  | +0.769 | **−0.217** | −1.8% | +1.527 | ✅ 0.88 | 15.9% | 20.5d |
| `vol_donch100_opp_long`   | +0.683 | **−0.238** | −1.5% | +1.064 | ✅ 0.88 | 12.1% | 56.8d |
| `vol_donch50_atr3x_long`  | +0.696 | **−0.249** | −1.5% | +1.945 | ✅ 0.75 | 13.3% | 21.2d |
| `vol_donch50_opp_long`    | +0.722 | **−0.254** | −2.0% | +1.756 | ✅ 0.88 | 15.1% | 44.2d |
| `vol_donch100_atr3x_long` | +0.630 | **−0.279** | −1.3% | +1.318 | ✅ 0.88 |  9.9% | 19.5d |
| `vol_donch20_opp_long`    | +0.904 | **−0.355** | −3.0% | +1.393 | ✅ 0.88 | 18.6% | 23.5d |
| `vol_donch100_opp_ls`     | +0.237 | **−0.550** | −3.2% | +0.945 | ❌ 0.75 | 26.8% | 52.2d |
| `vol_donch50_opp_ls`      | +0.265 | **−0.584** | −4.0% | +1.003 | ❌ 0.75 | 26.0% | 43.5d |
| `vol_donch20_atr3x_ls`    | +0.289 | **−0.621** | −4.5% | +0.968 | ❌ 0.75 | 27.8% | 24.0d |
| `vol_donch100_atr3x_ls`   | +0.239 | **−0.644** | −3.0% | +1.139 | ❌ 0.62 | 25.1% | 22.5d |
| `vol_donch50_atr3x_ls`    | +0.250 | **−0.677** | −3.9% | +0.851 | ✅ 0.75 | 24.0% | 23.0d |
| `vol_donch20_opp_ls`      | +0.316 | **−0.728** | −5.5% | +0.599 | ❌ 0.75 | 28.7% | 31.5d |

**OOS Sharpe spread:** −0.217 (best) → −0.728 (worst). **Median:** ≈ −0.467.
**Positive count:** 0 / 12. All negative, under-water by at least 0.217 Sharpe.

---

## 13-gate checklist (§5.5, filled from original report)

Applied to the **best** V2-L6 config (`vol_donch20_atr3x_long`, OOS Sharpe
−0.217). All other 11 configs fail by strictly larger margins.

| # | Gate (§5.5) | Threshold | Best L6 value | Verdict |
|---|---|---|---|:---:|
| 1 | Bootstrap 99.9% CI low > 0 (OOS + full) | > 0 | CI low < 0 (point estimate −0.217) | **FAIL** |
| 2 | OOS Sharpe ≥ 2.0 | ≥ 2.0 | **−0.217** | **FAIL (margin −2.217)** |
| 3 | OOS CAGR ≥ 30% | ≥ 30% | −1.8% | **FAIL** |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | 15.9% | ✅ (moot) |
| 5 | FWD Sharpe > 0 | > 0 | +1.527 | ✅ (moot) |
| 6 | WF 8 windows ≥ 6/8 profitable, DD ≤ 25% | ≥ 6/8 | 0.88 | ✅ (moot) |
| 7 | Median hold ≥ 3 trading days | ≥ 3d | 20.5d | ✅ (moot) |
| 8 | IR vs SPY ≥ 0.5 (OOS) | ≥ 0.5 | < 0 (OOS Sharpe negative) | **FAIL** |
| 9 | Cross-lib concordance ≥ 2/3 within ±3pp CAGR | ≥ 2/3 | Not run (moot — gate 2 vetoes) | **moot** |
| 10 | Stage-2 data concordance ±1pp OOS+FWD | ±1pp | Not run (moot) | **moot** |
| 11 | PBO < 0.5 (grid = 12 ≥ 5) | < 0.5 | Not computed; all configs OOS-negative → max PBO (1.0) structurally | **moot / FAIL** |
| 12 | DSR p-value < 0.05 (grid ≥ 5) | < 0.05 | No positive OOS Sharpe candidate to test | **moot / FAIL** |
| 13 | Cost × 2 → OOS Sharpe > 1.0 | > 1.0 | Baseline already < 0; doubling costs can only worsen | **FAIL** |

**Binding gate:** Gate 2 (OOS Sharpe ≥ 2.0) **FAILS by margin −2.217** on
the best config and by −2.728 on the worst. Gates 1, 3, 8, 11, 12, 13 also
fail. Gates 4, 5, 6, 7 passing are informational only and do not rescue the
verdict. Zero-bypass per mandate §2.5.

---

## Economic rationale (inherited, unchanged)

Per original AGGREGATE + narrative, the OOS 2022-2024 regime (fast 6-month
bear + Q1-2023 reversal + 2023 choppy range with narrow MAG7 leadership +
2024 moderate bull with 3 corrections + UNG 2022 squeeze + Fed hike-cycle
breaking TLT/HYG duration) is structurally hostile to Donchian trend-break
on a 10-ETF 1/N universe. Covel's trend-follow discipline requires 3-5
regime-defining trades to pay accumulated whipsaw
`[trend_following_covel, ch.3-5]`; none occurred in OOS. Universe of 10 is
sub-scale vs Winton (50+ futures) / Clenow (200+ stocks)
`[stocks_on_the_move]`. Retail CFD cost stack dominates at small universe
`[systematic_trading, p.185-188]`. None of these findings are engine-bug
artifacts — they are genuine regime + universe-size effects.

---

## Citation

`[advances_fin_ml, p.31-34]` — Look-ahead bias detection via cross-library
replication and timing-convention audit. Inheritance of a structural DEAD
verdict from a provably clean engine requires no re-simulation; the
epistemic chain is: (F1 inventory evidence) → (donchian_breakout.py clean)
→ (F2 patch irrelevant to L6) → (honest numbers identical to original) →
(original 12/12 OOS-negative verdict stands).

---

## Links

- F1 inventory: `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`
- Original AGGREGATE: `reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md`
- Original narrative: `jornada/2026-04-19/06-phase3.5a-v2-L6-vol-breakout-DEAD.md`
- Plan §F3 / §5.5: `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- F2 fix commit: `7b90a8f`
- Per-config reports (12): `reports/phase3_5a_v2/v2_l6_vol_breakout/vol_donch{20,50,100}_{atr3x,opp}_{long,ls}.md`
