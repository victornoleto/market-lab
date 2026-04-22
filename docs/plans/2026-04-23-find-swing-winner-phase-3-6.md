# Phase 3.6 — Open-ended hunt for a winning swing-trade strategy

**Created:** 2026-04-23 (user requested fresh start after V2 failed and Plano A has no winner under honest engine)
**Branch:** `phase3.6/swing-winner-hunt-20260423` (off `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422` to inherit engine fix commit `7b90a8f`)
**Baseline pytest:** 918 green at plan creation
**Author:** assistant (2026-04-22→23 overnight session)

---

## 0. Mission (single sentence)

**Find ONE swing-trade strategy that survives the 13 honest gates, from any candidate family across the 33 absorbed books — no loyalty to rejected V2 leads, no requirement to reuse past work, stop at first winner.**

"Swing" = median hold of **5-30 trading days**. Not intraday. Not buy-and-hold.

Broker-agnostic: winner can live on **Pepperstone/cTrader** (preferred for API optimization + non-BR jurisdiction) or **Banco Inter** (safer for larger balances, BR-tax bearing). Pick per-strategy based on cost fit.

---

## 1. Required reading (in this order, ~40 min total)

1. `jornada/2026-04-23-0700-overnight-summary.md` — what was just completed and the 4-option decision fork (you are Option E: fresh hunt, which effectively displaces A-D)
2. `jornada/README.md` — current state
3. `docs/investment-mandate.md` §1-5 + §7 — permanent rules, CDI floor, gate discipline, override history
4. `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` §5.5 — 13-gate definition (reused here with CDI soft-floor per user override 2026-04-22)
5. `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md` — 6 rejected V2 leads (do not re-test these)
6. `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` — engine bug scope (only `plano_a_leveraged_rotation.py:462` was affected; everything else is clean canon)
7. `knowledge/SKILL.md` — aggregator of the 33 books
8. `books/summaries/` + `books/summaries/_archive/` — 33 specific summaries (pick candidate families from here)

---

## 2. Hard constraints

### 2.1 Engine + data

- **Engine:** only the F2-patched engine (commit `7b90a8f`). Any new strategy in `src/ai_trade/backtest/strategies/` must use `prev_weights × ret` alignment OR be a clean return-series strategy (like `letf_rotation.py`).
- **Cross-lib concordance gate 9 is mandatory** — 2/3 of {bt, vectorbt, backtrader} must agree with canonical within ±3pp CAGR on OOS before declaring winner. Reuse `scripts/run_phase3_5f_cross_lib.py` as template.
- **Data:** Tiingo `data/tiingo/daily/prices/{TICKER}.parquet` (1678 tickers). For ETFs, also reconcile with `data/testfolio/cache/history.parquet` (testfolio synthetics for pre-inception periods).
- **Windows (fixed):** IS 2001-05-14 → 2017-12-31, OOS 2018-01-01 → 2023-12-31, FWD 2024-01-01 → 2026-04-14. Do **not** cherry-pick.
- **Survivorship:** for single-name equity strategies, use PIT universe reconstruction — do **not** use current S&P 500 as IS universe (that's future info). Reference: `books/summaries/stocks_on_the_move.md` or the Tiingo fundamentals snapshots if present.

### 2.2 Frozen files (do NOT touch, per mandate §2.2)

- `docs/self_improvement/memory.md`, `trial_count.json`
- All of `reports/phase_3_5e/*`, `phase_3_5b/*`, `phase_3_5d/*`
- Existing buggy baseline reports in `reports/phase3_5a_v2/v2_l2_*` (forensic banners around them OK, don't edit contents)
- The 6 F3 AGGREGATE.md files in `reports/phase_3_5f/honest_revalidation/`
- Pending drafts in `docs/.pending/`

### 2.3 Engineering discipline

- **Pytest baseline 918 green after every commit.** Never red.
- **Citations (CLAUDE.md Regra 2):** every parameter choice cites `[book.slug, p.X]` or `[book.slug, ch.Y]`. Not optional.
- **JORNADA entries (CLAUDE.md Regra 1):** every PASS/FAIL verdict writes a `jornada/YYYY-MM-DD-HHmm-<slug>.md` + updates `jornada/README.md` index.
- **Conventional Commits:** `feat(phase3_6):`, `fix:`, `test:`, `docs:`, `chore:`.
- **Preserve forensic record:** never overwrite a failed candidate's report. If re-running with different parameters, write to a new sibling directory.

---

## 3. Broker cost models (use whichever fits the strategy family)

### 3.1 Pepperstone Razor via cTrader (preferred for API + non-BR)

- CFD spread: ~0.03-0.05% for SPY/QQQ; 0.5-1 pip for FX majors; wider for commodities (GLD ~8-12 cents).
- Swap overnight: −0.01 to −0.05% per night on levered notional (kills holds > 20d at 2-3× leverage).
- Commission: $0.35 per 100k USD notional per side on Razor account.
- Tax: NOT BR-source (Pepperstone PTY Ltd / EU entity depending on KYC). Modal net return = gross net of spread/swap/commission only.
- Position size elasticity: micro-lots available (→ testable at $1k notional).
- Reference: `project_broker_decision.md` memory.

### 3.2 Banco Inter Internacional (safer, BR-tax)

- Commission: zero on US ETFs.
- FX spread: 0.99-1.50% on BRL↔USD at entry AND exit (round-trip ~2-3%).
- Settlement: T+1 on ETFs; FX settled same-day.
- Tax: 15% on BR-source capital gains (apply to realized gains, net of losses in same month).
- Catalog: SPY, QQQ, GLD, TLT, IVV, VTI, SSO (confirmed 2026-04-18), UPRO (verify), most SPDRs, major iShares. Leveraged ETFs (UPRO/SSO) have limit-order restrictions.
- Reference: `project_plano_b_broker_inter.md` memory.

### 3.3 Pick per strategy

- Intraday/short-hold CFD strategies → Pepperstone.
- Monthly-rebal ETF swing → Inter (tax-model net return).
- Multi-asset basket (FX + commodities + equities) → Pepperstone (Inter doesn't offer commodities directly).
- Single-asset leveraged rotation → Either; compare net returns under both cost models.

---

## 4. Candidate family menu (pick 5-10, one per subagent)

Diversified across 33 books. **EXCLUDE** the 6 V2 leads (TSMOM time-series, Gayed EMA regime, AFML meta-label, Carver RP blend, Kalman pairs, Donchian vol-breakout) — already rejected.

| # | Family | Source book(s) | Broker fit | Horizon | Priority |
|---|---|---|---|---|---|
| A | **Clenow cross-sectional momentum top-N stocks** | `stocks_on_the_move.md` | Inter (stocks) | 21d rebal | HIGH |
| B | **Risk Parity inverse-vol rotation** | `risk_parity.md` (_archive), `systematic_trading.md` | Inter (ETFs) | 21d | HIGH |
| C | **GTAA 10-month SMA (Faber)** | `trading_evolved.md`, `systematic_trading.md` | Inter (ETFs) | 21d | HIGH |
| D | **Chan-style MR pairs (non-Kalman)** | `algo_trading_chan.md`, `quant_trading_chan.md` | Pepperstone (CFD pair) | 5-15d | MED |
| E | **Ehlers adaptive-cycle filters** | `cycle_analytics.md`, `rocket_science.md` | Pepperstone (FX/commodity) | 5-10d | MED |
| F | **Vol-targeting managed futures basket** | `systematic_trading.md`, `volatility_trading.md` | Pepperstone (multi-asset CFD) | 10-20d | MED |
| G | **Aronson evidence-based TA (screened indicators)** | `evidence_based_ta.md`, `testing_tuning.md` | Either | 10-20d | LOW |
| H | **Adaptive Markets regime-switching** | `adaptive_markets.md` (_archive), `regime_change.md` | Inter | 21d | MED |
| I | **Statistical-sound indicators (Sharpe-significant at 0.001)** | `stat_sound_indicators.md` (_archive) | Either | 5-15d | MED |
| J | **ML-for-algo classical (Jansen / López de Prado)** | `ml_for_algo_trading.md`, `ml_for_asset_managers.md` (_archive) | Either | 10-20d | LOW |
| K | **Universal trend tactics** | `universal_trend_tactics.md` (_archive) | Either | 10-20d | LOW |
| L | **Sentiment + earnings-surprise (PEAD)** | `sentiment_analysis_handbook.md` (_archive), academic | Inter (stocks) | 5-15d | LOW |

Start with HIGH-priority (A, B, C) — most tractable, best-documented, most likely to yield edge under honest backtest.

---

## 5. 13-gate definition (with user-locked relaxations)

Per plan 3.5f §5.5 with these swing-specific adjustments:

| # | Gate | Threshold | Rationale |
|---|---|---|---|
| 1 | Bootstrap 99.9% CI low > 0 | OOS Sharpe AND full-period Sharpe | `[advances_fin_ml, p.196-202]` |
| 2 | OOS Sharpe ≥ **1.5** | relaxed from V2's 2.0 — swing strategies typically lower Sharpe than short-hold | user override 2026-04-22 |
| 3 | OOS CAGR ≥ **13% (CDI floor)** | strict ≥30% is target; CDI soft-floor per user override 2026-04-22 | mandate §2 with user relaxation |
| 4 | OOS MaxDD ≥ −25% | binding cap, no relaxation | mandate §5 |
| 5 | FWD Sharpe > 0 | 2024-2026 stress | plan §5.5 |
| 6 | WF 8-windows | ≥6/8 profitable, max-window DD ≤ **30%** (relaxed from 25% for swing long-hold) | `[advances_fin_ml, ch.11]` |
| 7 | Median hold ≥ **5 trading days** | swing discipline (up from V2's 3d) | this plan |
| 8 | IR vs SPY buy-hold ≥ **0.3** | relaxed from V2's 0.5 for non-leveraged | this plan |
| 9 | Cross-lib ≥ 2/3 within ±3pp CAGR | bt, vectorbt, backtrader | plan §5.5 |
| 10 | Stage-2 data concordance ≤1pp CAGR | Tiingo adj vs testfolio (for ETF strategies) | plan §5.5 |
| 11 | PBO < 0.5 (if grid ≥5 configs) | CSCV 10-block | `[advances_fin_ml, p.208-211]` |
| 12 | DSR p < 0.05 (if grid ≥5 configs) | on winner OOS Sharpe | `[advances_fin_ml, p.196-202]` |
| 13 | Cost×2 sensitivity: OOS Sharpe > 1.0 | robust to cost-model variance | plan §5.5 |

**Winner = ALL 13 pass** (with user-override relaxations applied to gates 2, 3, 6, 7, 8).

**PARTIAL = 12/13 pass** (escalate to user for review).

**FAIL = any missed gate not covered by a listed relaxation.**

---

## 6. Loop protocol

### 6.1 Execution architecture

Main orchestrator (future Claude session or self-improve loop) dispatches **2-3 candidate subagents in parallel per wave** (token discipline).

Per candidate, the subagent:

1. Read 1-2 source book summaries
2. Design hypothesis: single paragraph + parameter choices with citations
3. Implement: new strategy class in `src/ai_trade/backtest/strategies/` OR reuse existing clean engine (letf_rotation.py, tsmom_multi_asset.py, etc.)
4. Runner: `scripts/run_phase3_6_<family_slug>.py` wiring config × splits
5. Full pipeline: backtest IS/OOS/FWD + cost model (per §3) + WF + bootstrap + CPCV (if ≥5 configs)
6. Cross-lib check: at least one independent lib agrees within ±3pp
7. Report: `reports/phase_3_6/<family_slug>/AGGREGATE.md` with 13-gate checklist
8. JORNADA entry: `jornada/YYYY-MM-DD-HHmm-phase3.6-<slug>-<verdict>.md`
9. Commit: `feat(phase3_6): <family_slug> honest validation — <VERDICT>`

### 6.2 Stopping rule — stop at first winner

As soon as **one candidate passes all 13 gates** (with relaxations), STOP. Do **NOT** auto-promote. Write:
- `jornada/YYYY-MM-DD-HHmm-phase3.6-WINNER-<slug>.md`
- `reports/phase_3_6/WINNER.md` — full package: 13-gate evidence, broker recommendation, projected live config, cost sensitivity table, cross-lib replication, next steps for user approval
- Flag mandate §7 entry as `docs/.pending/phase3_6_winner_mandate_entry.md` — user reviews before applying

### 6.3 Escalation rule — after 10 FAIL or 3+ PARTIAL

If 10 candidates are evaluated without any PASS, OR if 3+ candidates are PARTIAL (12/13), STOP and write:
- `reports/phase_3_6/BREADTH_NO_WINNER.md` — comparison table of everything tried, reasons for failure, recommendations:
  - Broaden universe (add BR Ibov ETFs, emerging markets)
  - Soften gates further with mandatory user sign-off
  - Pivot to passive (Plano C only, no active)
  - Re-run self_improve_loop on fresh book-driven hypotheses
- jornada entry summarizing

---

## 7. Output file tree

```
reports/phase_3_6/
├── README.md                          # running index of candidates tried
├── <family_slug>/
│   ├── AGGREGATE.md                   # 13-gate checklist + verdict
│   ├── AGGREGATE.json                 # structured metrics
│   ├── daily_returns.parquet          # local, gitignored
│   ├── config_grid.csv                # grid enumeration (if multi-config)
│   └── cross_lib_check.md             # bt/vectorbt/backtrader comparison
├── WINNER.md                          # only if winner found
└── BREADTH_NO_WINNER.md               # only if escalation fires

src/ai_trade/backtest/strategies/
└── phase3_6_<family_slug>.py          # new strategy class per candidate

scripts/
└── run_phase3_6_<family_slug>.py      # runner per candidate
```

---

## 8. Questions already locked (no need to re-ask user)

| Question | Locked answer | Source |
|---|---|---|
| CAGR soft-floor | CDI (13%) | 2026-04-22 Q&A |
| Stop at first winner | YES, always halt before promotion | 2026-04-22 Q&A + CLAUDE.md Regra 1 |
| Reuse rejected V2 leads | NO (fresh families only) | user 2026-04-23 message |
| Broker choice | per-strategy best fit | user 2026-04-23 message |
| Tax model | 15% BR if Inter; skip if Pepperstone | mandate §1 |
| Windows | IS/OOS/FWD as in V2 | plan 3.5f §5.4 |
| Preserve forensic record | yes, never overwrite | mandate §2.2 |

---

## 9. What "done" looks like

### 9.1 Winner found (≥1 candidate passes all 13 gates)

- `reports/phase_3_6/WINNER.md` committed
- `jornada/YYYY-MM-DD-phase3.6-WINNER-<slug>.md` committed
- Mandate §7 entry drafted in `docs/.pending/`, awaiting user approval
- Strategy doc banner drafted in `docs/strategies/<family_slug>.md` (or appended if file exists)
- Pytest 918+ green
- No frozen files touched
- Branch ready for user review + merge decision

### 9.2 No winner (escalation fires)

- `reports/phase_3_6/BREADTH_NO_WINNER.md` with comparison table + 4 recommendations
- Jornada summary entry committed
- User reviews + picks next move

### 9.3 Invariants (apply in both cases)

- Every candidate has a committed AGGREGATE.md + JORNADA entry (even fails)
- Every parameter choice cites `[book.slug, p.X]`
- Every commit follows Conventional Commits
- Cross-lib concordance verified on the winner (not optional)

---

## 10. Citations glossary (use as candidates get evaluated)

- **Look-ahead bias audit + timing convention:** `[advances_fin_ml, p.31-34]` (López de Prado)
- **CSCV / PBO:** `[advances_fin_ml, p.208-211]`
- **DSR / bootstrap CI:** `[advances_fin_ml, p.196-202]`
- **Walk-forward:** `[advances_fin_ml, ch.11]`
- **Kelly / leverage-space:** `[math_money_mgmt, Vince]`, `[leverage_space, Vince]`
- **Vol-targeting:** `[systematic_trading, p.~175]` (Carver)
- **Retail cost/hold discipline:** `[systematic_trading, p.185-188]` (Carver)
- **Cross-sectional momentum 90d:** `[stocks_on_the_move, p.81]` (Clenow)
- **Regime filter 200d SMA:** `[stocks_on_the_move, p.~100]` (Clenow)
- **Ehlers dominant cycle:** `[cycle_analytics]`, `[rocket_science]`
- **Chan MR / pairs:** `[algo_trading_chan]`, `[quant_trading_chan]`
- **Evidence-based TA:** `[evidence_based_ta]` (Aronson)
- **Aronson OOS testing:** `[testing_tuning]`

---

## 11. Final notes for the executing session

- You are inheriting clean state: engine honest (commit `7b90a8f`), pytest 918, V2 closed as DEAD.
- User wants SOMETHING to win, but NOT at the cost of honest gates. Soft-floor is CDI 13%, not below.
- If all 10+ candidates fail, the mandate §4.7 "Plano C passive only" fallback is explicit user-approved terminal state — don't be afraid to escalate there.
- Commits on this branch stay OFF main until user reviews.
- User may wake at any point and want a status update. Keep `reports/phase_3_6/README.md` current as a running index.
- User prefers terse updates + clear escalation at each gate (not mid-run commentary).

---

**End of plan.**
