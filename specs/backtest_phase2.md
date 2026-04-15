# Spec — Phase 2: Backtest Module

Executable plan for the ai-trade backtest module. Each task has a checkbox
and a **Conclusion** field that must be filled in before the corresponding
commit. This file survives across sessions — when opening Claude Code, the
first thing to read is this file + `ROADMAP.md`.

---

## 📊 Phase 2 summary (completed 2026-04-14)

**Status:** ✅ All 5 tasks completed. 173 tests passing. 6 commits
(`517c221` → `f971c70`).

### What was delivered

Complete backtest module in `src/ai_trade/backtest/` — 5 independent
layers, each with its own tests verified numerically against the cited
source (AFML, Masters, Clenow).

| Layer | Files (LOC) | Tests (LOC) | Cited source |
|---|---|---|---|
| **Data** — `data/` | `yfinance_source.py` (150), `wikipedia_spx.py` (180) | 2 files (191) | — |
| **Engine** — `engine/` | `portfolio.py` (206), `execution.py` (120), `runner.py` (170) | `test_backtest_engine.py` (537) | `[advances_fin_ml]` generic |
| **Validation** — `validation/` | `cpcv.py` (127), `pbo.py` (118), `dsr.py` (136), `walk_forward.py` (89), `permutation.py` (106) | `test_validation.py` (596) | `[advances_fin_ml, ch.7/11/14]`, `[testing_tuning]`, `[stat_sound_indicators]` |
| **Metrics** — `metrics/` | `performance.py` (125), `report.py` (297) | `test_metrics.py` (469) | `[advances_fin_ml]`, Sortino (Estrada) |
| **Strategies** — `strategies/` | `base.py` (93), `clenow_momentum.py` (390) | 3 files (851) | `[stocks_on_the_move]` |

Total ≈ **2.3k LOC of implementation + 2.6k LOC of tests**. Plus: CLI
`scripts/run_clenow_replication.py` (250 LOC), doc
`reports/clenow_replication_notes.md`.

### Commits

| SHA | Content |
|---|---|
| `517c221` | Data sources — `yfinance_source` + `wikipedia_spx` (pre-Task 1) |
| `d8b43a4` | Task 1 — Engine core (portfolio + execution + runner) |
| `5d91212` | Task 2 — Validation framework (CPCV / PBO / DSR / WF / MCPT) |
| `d172ebe` | Task 3 — Metrics + report generator (Sharpe/Sortino/Calmar/CAGR/DD/VaR + MD+PNG) |
| `415e205` | Task 4 — Clenow momentum replication (strategies + CLI) |
| `f971c70` | Task 5 — Wrap-up (ROADMAP/README + reassessment of deferred decisions) |

### Clenow replication — real numbers

Run on 2026-04-14 (commit `415e205`):

- **Universe:** SPX 500 point-in-time via Wikipedia, window
  2023-07-01 → 2023-12-31 (6 months)
- **503 tickers** in the point-in-time composition; **17 skipped** (3.4%)
  due to residual survivorship (rename/delisting that `yfinance` does not
  resolve)
- **Cash:** $100k → $93 965 final
- **CAGR:** −11.79% · **Sharpe:** −0.79 · **Max DD:** 13.55%
- Result **within the expected noise** for choppy H2 2023; winners/losers
  composition (LLY/GOOG/AMGN vs NCLH/CMG/BKR) confirms ranking + regime
  filter logic is operating correctly. **Not a measure of edge** —
  single-trial with fixed parameters, no grid, no active gates.

### Key transferable decisions (pitfalls a future dev needs to know)

**Engine:**
- **Equity = `cash + Σ signed_market_value`**, not `cash + Σ unrealized_pnl`
  (the latter ignores the cost basis of open positions).
- **Spread in absolute price**, not pips — caller converts; engine stays
  symbol-agnostic.
- **Mark-to-close in two passes in the Runner** (before + after the strategy):
  before gives fresh equity for sizing, after removes the spread premium
  from the mark of freshly-opened positions.

**Validation:**
- **Purge uses the `pd.Series[t0→t1]` contract** (index=t0, values=t1). For
  labels with no overlap: `pd.Series(idx, index=idx)`.
- **Embargo in positions, not time** — `h = int(embargo_pct · len(times))`
  (AFML p.151), stable under irregular sampling.
- **CPCV: purge/embargo per block**, not over the union — each disjoint
  block in the test generates its own purge+embargo (replicates mlfinlab,
  avoids sub-purging).
- **E[SR_max] (AFML p.222-223) returns Z-score units**; multiply by
  `√V = 1/√(T-1)` under iid-null before comparing with PSR. Without that
  scaling, DSR rejects any Sharpe > 0 for N > 5.
- **Gumbel `√(2 ln N)` is asymptotic FOR THE UPPER LIMIT, not the mean** —
  tests use direct Monte Carlo against `mean(max(N_normals))`.
- **Single-seed PBO is noisy** (std ≈ 0.19 with N=50, T=500, 8 blocks);
  null-case test uses the mean of 20 independent matrices.
- **MCPT (Masters):** shuffle of the `n-1` changes preserving `prices[0]`
  and `prices[-1]` (invariant), re-anchoring `prices[-1]` after cumsum to
  erase floating-point drift.

**Metrics:**
- **Sortino with population downside-dev** (denominator = all
  observations, not just downside). Estrada formula; returns `+inf` when
  there are no returns below target.
- **Survivorship disclaimer is mandatory by contract** — `_needs_disclaimer`
  flags `yfinance`, `wikipedia`, `yahoo` + any source without an explicit
  survivorship-free marker. Cites ROADMAP §"Deferred decisions".
- **VaR floor at 0** — if the 5% quantile of returns is positive
  (strategy that never loses), VaR = 0 by convention.
- **2-panel PNG chart** (equity + underwater DD), `matplotlib.use("Agg")`
  headless (~70 KB).

**Strategy (Clenow):**
- **`self.data` carries the full history; Runner iterates a bounded slice.**
  The strategy needs 200d (SPX MA) + 90d (regression) of warmup before
  `--start`. The CLI passes `data_bounded` to the Runner but the full
  `data` to the strategy.
- **Sells before buys in the same list** — Runner executes orders in
  insertion order; cash freed becomes available for buys on the same bar.
- **Buy gated by regime ON, sell NOT** — Clenow p.94-95: *"Do not sell a
  holding just because the index drops below the 200d MA."*
- **Sizing = `floor(equity × 0.001 / ATR20)` using `equity`** (not cash) —
  Clenow p.88 speaks of "account value".
- **CPCV/PBO/DSR skipped in the Clenow CLI** — single-trial (N=1) does not
  exercise the gates that compare N≥2. Walk-forward over realized equity
  is the only meaningful validation.

### Out of scope (and why)

- **Clenow parameter grid search:** that is the pain of Phase 2.5 / 3.
  Today runs single-trial (1 fixed configuration).
- **CPCV/PBO/DSR "in production":** the modules exist and have tests;
  what's missing is exercising them over a real grid. Unlocks in Phase 2.5 / 3.
- **Universe Selector + fundamented candidates (Ehlers, AFML meta, Chan):**
  original scope of "Phase 2 — Strategy Engine" in the ROADMAP, now Phase 2.5.
- **Migration to paid data (Tiingo/EOD/Norgate):** deferred until the first
  strategy survives grid + gates on yfinance+Wikipedia (detail in
  §"Post-Phase 2 reassessment").
- **vectorbt sandbox:** deferred until iteration friction becomes a
  measurable bottleneck (>30 min per variation).
- **`knowledge/SKILL.md` untouched:** Phase 2 insights are engineering,
  not citable trading rules; they live in the Conclusions of this spec.

### Next step

**Phase 2.5 / 3 — rigorous grid backtest with active gates.** Run
Clenow on a parameter grid (lookback 60/90/120, top 10%/20%/30%, ATR
risk budget 0.001/0.002) exercising CPCV/PBO/DSR with N≥20, to obtain
an honest distribution of Sharpe + PBO + DSR. **Gate to advance:**
PBO < 0.5 and DSR p-value < 0.05 and walk-forward ≥6/8 profitable on
yfinance+Wikipedia data. Only then does it make sense to do (a) migration
to paid data as ablation study, (b) second strategy, (c) vectorbt as sandbox.

Full rationale for the 3 deferred decisions: §"Post-Phase 2 reassessment"
at the end of this file. **Run 1 completed 2026-04-14** — see §"Phase
2.5/3 — Run 1" below for numbers and decision fork.

---

## 🔬 Phase 2.5/3 — Run 1 (Clenow grid, 2026-04-14)

**Status:** 🔄 Grid executed. **Gates fail**. Decision fork open
(paid data / universe shift / pivot). Artifacts in
`reports/grid_20260414-1813/diagnostic.md`.

### What was delivered (Commits 0-9 + fix)

New module `src/ai_trade/backtest/grid/` (6 files + CLI +
regression fix in the strategy). 11 small commits in strict TDD
(`082a41f` → `8d25e65`), 62 new tests (235/235 green).

| Layer | File | LOC | Tests |
|---|---|---|---|
| **Config** | `grid/config.py` | 57 | 8 |
| **Result + I/O** | `grid/result.py` | 244 | 10 |
| **Runner** | `grid/runner.py` | 151 | 7 |
| **Observers + log** | `grid/observers.py` | 161 | 6 |
| **Gates** | `grid/gates.py` | 127 | 8 |
| **Walk-forward** | `grid/walk_forward.py` | 111 | 7 |
| **Diagnostic** | `grid/diagnostic.py` | 188 | 8 |
| **Report** | `grid/report.py` | 280 | 6 |
| **CLI** | `scripts/run_grid_clenow.py` | 283 | — (smoke) |
| **Strategy fix** | `strategies/clenow_momentum.py` | +11 | 1 (regression) |

**Pre-existing fix discovered during the 1st real run (28/30 trials
failed):** `_sell_orders` created `Order(side="sell")` for positions
on tickers delisted mid-backtest (e.g., ANDV→MPC on 2018-10-03). In
the single-trial Clenow (2023-H2 window) this did not fire because
all relevant delistings were earlier. Over 9 years, ANDV/KR/WBA/
PXD/MRO/etc. trigger the crash. Fix: `_sell_orders` receives `bars`
and skips positions without a bar today — orphans wait for data to
return or for the backtest to end (equity tracking the last mark).
Commit `8d25e65`.

### Grid executed

- **Window:** 2015-01-01 → 2023-12-31 (9 years ≈ 2267 trading days)
- **Universe:** SPX 500 point-in-time via Wikipedia, 506 tickers on
  2015-01-01. 97 skipped (19%) due to residual survivorship (delistings
  that yfinance does not resolve). Data available: 410 tickers.
- **Grid:** 30 configs =
  `lookback_regression ∈ {60,75,90,105,120}` ×
  `top_pct ∈ {0.10, 0.20, 0.30}` ×
  `risk_factor ∈ {0.001, 0.002}`. Fixed: `rebalance_weekday=2`,
  `lookback_trend=100`, `lookback_index_trend=200`, `lookback_atr=20`,
  `lookback_gap=90`, `gap_threshold=0.15`.
- **Parallelism:** joblib `Parallel(n_jobs=4, backend="loky")` ≈ 15
  min wallclock for 30 configs after data fetch (7 min).
- **Walk-forward:** 8 contiguous windows on the equity curve (no
  re-optimization — fixed-config strategy).

### Gate verdict

| Gate | Value | Limit | Verdict |
|---|---|---|---|
| **PBO** | **0.524** | < 0.5 | ❌ reject (margin 2.4%) |
| **DSR** | 0/30 configs p < 0.05 | any | ❌ reject |
| **Walk-forward** | 4/30 configs pass | any | ✅ (4 pass) |

**Overall: FAIL.** Compound failure: PBO and DSR, not WF (4 configs
clear walk-forward individually). Failure modes:
`PBO_HIGH + DSR_ALL_FAIL + COMBINED`.

### Best config (ignoring gates)

**`config_id=15`** — `lookback_regression=90, top_pct=0.20,
risk_factor=0.002`:
- **Sharpe (annualized):** 0.583
- **CAGR:** 8.87%
- **Max drawdown:** 19.86%
- **Walk-forward:** 6/8 profitable (passes rule #5)
- **DSR p-value:** 0.627 (fails rule #4 by a wide margin)
- **Inside the gate only if we drop PBO and DSR.**

### Interpretation

**Clenow on the yfinance SPX 2015-2023 window does NOT exhibit
statistical edge** after correcting for multiple hypotheses. Three
pieces of evidence:

1. **CAGR 8.87% of the best config underperforms SPY buy-and-hold** over
   the same window (~11-12%). Against a survivorship-biased benchmark.
2. **DSR for N=30 trials, T=2267 bars:** E[SR_max] under iid null
   ≈ 0.054 periodic (= annualized Sharpe ~0.86). Best observed
   annualized Sharpe 0.583 = 0.037 periodic. **Observed < benchmark
   → does not reject H0 (no edge).**
3. **PBO 0.524** (logits mean −0.20, std 1.94): IS-best configs do not
   preserve rank OOS → overfit inherent in the grid.

**Two readings of the result:**

- **Literal:** yfinance SPX 2015-2023 has no Clenow edge after gates.
  What looks like alpha (Sharpe 0.58) is indistinguishable from best-of-30
  under null hypothesis.
- **Data-hypothesis:** yfinance inflates the SPY benchmark (survivorship
  bias includes only survivors, no failures — real SPY would have had
  lower CAGR). Removing the bias could lower SPY to ~9% and raise Clenow
  to a relative edge. **Needs paid-data ablation to know.**

### Decision fork (open)

The plan prescribes: do NOT pivot automatically. The diagnostic
surfaces the data, the user decides. Four plausible options:

1. **Paid-data ablation.** Tiingo SF / Norgate / EOD. Rerun the
   same grid on survivorship-free data. **Direct answer:** either
   the edge is real and masked by the bias, or it does not exist.
   Cost: setup + free-trial or purchase ($30-50/month Tiingo SF).
   Time: 2-3 days of integration + 1-2h re-run.
2. **Pivot to 2nd strategy** (Ehlers DSP, AFML meta-label, Chan
   mean-reversion). Clenow is weekly slow; Ehlers is
   complementary (short holding, CFD-native). Cost: 1-2 weeks.
3. **Universe shift** (Nasdaq100 instead of SPX500). Fewer tickers =
   fewer configs needed = smaller DSR benchmark. But introduces
   sector bias (tech). Cost: low (reuse infra).
4. **Accept the result as is** — Clenow does not work in the
   2015-2023 yfinance regime. Document and move on to the next
   experiment.

**Recommendation (mine, not pre-decided):** option **1 (paid data)**
first. It is the **most informative answer** — if edge appears in
Norgate, everything else unlocks. If it does not, the pivot is
better-grounded (Clenow still fails after removing data uncertainty;
now it makes sense to move to Ehlers/AFML).

### Grid run references

- **Diagnostic report:** `reports/grid_20260414-1813/diagnostic.md`
  (versioned? no — directory in `.gitignore`; material numbers
  inlined in this spec)
- **Heatmap PNG:** `reports/grid_20260414-1813/assets/heatmap_sharpe.png`
- **Per-trial checkpoints:** `.cache/grid_runs/grid_20260414-1813/trial_*/`
  (parquet + JSON; human-inspectable)
- **Unified log:** `logs/grid.log`
- **JSONL machine-readable:** `.cache/grid_runs/grid_20260414-1813/trials.jsonl`

### Key transferable decisions (Phase 2.5)

- **`return_as="list"` in `Parallel` blocks observers until ALL
  tasks finish.** The user sees no progress during the parallel run
  even with tqdm — switch to `return_as="generator_unordered"` in a
  future iteration if UX becomes a bottleneck.
- **Residual survivorship 3% (6m 2023) → 19% (9y 2015-2023).** Scales
  approximately linearly with backtest length. The older the start,
  the more tickers are orphaned from the Wikipedia scrape.
- **Delisted-ticker sell crash** (ANDV 2018): latent bug that only
  showed up in windows crossing delistings. Fix: `_sell_orders`
  filters by `bars`. Regression test in
  `tests/test_clenow_strategy.py::TestSellCriteria::test_skips_sell_for_delisted_symbol_with_no_bar_today`.
- **DSR p-value under null with N=30, T=2267:** E[SR_max] ≈ 0.054
  periodic (≈ 0.86 annualized). Strategies below this bar do not
  pass DSR even with a positive absolute Sharpe.
- **Checkpoint I/O via parquet + JSON** works: 30 trials written in
  ~10 MB, human-inspectable, robust to rename/schema changes.
- **Joblib workers `loky`: 4 workers × ~150 MB data = ~600 MB RSS
  total.** No memory pressure on a 16 GB machine. `n_jobs=-1` safe.

---

## 🔬 Phase 2.5 — Run 3 (Clenow grid on Tiingo, 2026-04-?)

**Status:** 🔄 _data layer ready (Tiingo Power $30 subscribed
2026-04-14); bulk download in progress; re-run pending._

### What's different vs Run 1

Same Clenow grid (30 configs), same window (2015-01-01 → 2023-12-31),
same gates, same checkpoint/observer plumbing — **only the data source
changes**: yfinance → Tiingo (storage-backed at `data/tiingo/`).
Survivorship-free coverage confirmed empirically — `ANDV` (delisted
2018-10-03) returned 42 OHLCV bars up to the delisting date in the
smoke test; the same will hold for the ~97 SPX 500 tickers that
yfinance silently dropped in Run 1.

Index proxy: Tiingo does not serve `^GSPC`. The CLI auto-swaps to
`SPY` when `--data-source=tiingo`. SPY tracks SPX with ≥99% return
correlation — material for absolute SPX 200-day MA values, not
material for the regime-mode boolean (above/below MA) used by Clenow.

### Verdict (template — fill after re-run)

| Gate | Run 1 (yfinance) | Run 3 (tiingo) | Δ |
|---|---|---|---|
| PBO | 0.524 fail | _tbd_ | _tbd_ |
| DSR best p | 0.627 (cfg #15) | _tbd_ | _tbd_ |
| WF pass | 4/30 | _tbd_ | _tbd_ |
| Best Sharpe | 0.583 | _tbd_ | _tbd_ |
| Best CAGR | 8.87% | _tbd_ | _tbd_ |
| Universe (avg per rebal) | 410 (after 19% drops) | _tbd_ | _tbd_ |
| Tickers with delisted history served | 0 | _tbd_ | _tbd_ |
| Overall | FAIL | _tbd_ | _tbd_ |

### Fork resolution (template)

* If Run 3 **passes** all 3 gates → Run 1 verdict was data-mediated;
  yfinance survivorship masked a real edge. Phase 3 unblocks for
  Clenow.
* If Run 3 **fails on DSR alone** but **passes PBO** → similar profile
  to Run 2 (Ehlers); the edge is small but the structure is sound;
  consider Option 3 (regime-aware Clenow+Ehlers portfolio) given the
  cross-corr ≈ 0 already established.
* If Run 3 **fails on PBO too** → confirms Run 1's structural reading;
  the edge is absent in the SPX 2015-2023 window irrespective of data
  bias. Pivot to a 3rd strategy or universe shift.

### Reused infra

- `src/ai_trade/backtest/data/tiingo_storage.py` — parquet+manifest
  layer (`data/tiingo/`).
- `src/ai_trade/backtest/data/tiingo_source.py` — storage-first;
  Tiingo API on miss; ticker `BF.B` ↔ `BF-B` Bloomberg/Yahoo mapping.
- `scripts/tiingo_bulk_download.py` — one-time bulk, idempotent.
- `scripts/tiingo_backup.py` — tar.gz the dataset for portability.
- `scripts/run_grid_clenow.py --data-source tiingo` — single-flag
  re-route, no other changes.

---

## 📖 How to use this file

1. **When starting a session**, read this entire file + `ROADMAP.md` §"Two-stage backtest".
2. Find the next task with `[ ]`.
3. Implement per the "What to do" section and the acceptance criteria.
4. **BEFORE COMMITTING**, edit this file:
   - Swap `[ ]` for `[x]` on the task.
   - Fill in the task's **Conclusion** field (2-4 lines) with:
     - What was done (summary, not a copy of the description)
     - Files created/modified (paths)
     - Test count (`N passed` in pytest)
     - Findings/surprises/non-obvious decisions (if any)
5. **Include this edit in the same commit** as the implementation.
6. When **all** tasks are `[x]`, the final commit updates
   `ROADMAP.md` marking Phase 2 ✅ Completed.

**Do not:**
- Never remove or rewrite completed tasks — history is part of the value.
- Never skip the **Conclusion** field — it is the resumability contract.
- Never start a new task without marking the previous one `[x]` in the same commit.

**Example of a filled-in Conclusion field:**
> Portfolio tracking + P&L accounting implemented in `engine/portfolio.py`
> with 12 tests (`12 passed`). Decision: store positions in `dict[symbol, Position]`
> rather than a DataFrame — O(1) access and avoids reindexing. Unrealized P&L uses
> the last known mark (`mark_price` field updated via `update_mark()`).

---

## 🎯 Quick context (for a new session)

- **Phase 0 / 0.5 completed.** 33 books absorbed, `knowledge/SKILL.md` generated, running.
- **Phase 1 partially scaffolded.** docker-compose (postgres+grafana) OK;
  cTrader client blocked awaiting Spotware approval of the OAuth app.
- **Phase 2 (this spec) kicked off** with data layer ready (commit `517c221`).
- **Non-negotiable principles** (from `knowledge/SKILL.md`):
  - Every rule/parameter/gate cites `[book.slug, p.X]`.
  - Survivorship bias explicit in every report until migrating to a paid source.
  - CPCV/PBO/DSR are **mandatory gates**, not "nice to have" (rules #3-5).
- **Stage 1 only** — data via `yfinance` + Wikipedia scrape, no cTrader.
- **First replication target:** Clenow `stocks_on_the_move` (2 parameters, well specified).

---

## ✅ Prerequisites completed

- [x] **Data layer — yfinance + Wikipedia SPX** (commit `517c221`, 2026-04-14)

  **Conclusion:** Created `src/ai_trade/backtest/data/yfinance_source.py`
  (OHLCV daily with parquet cache + `_normalize` that flattens MultiIndex/strip-tz)
  and `wikipedia_spx.py` (scrape of the 2 SPX tables + `constituents_on(date)` via
  the undo-changes-walking-backwards algorithm). 15 new tests (`33 passed`
  total). Conflict detected in `ctrader-open-api 0.9.2` which hard-pins
  `protobuf==3.20.1` + `Twisted==21.7.0` — moved to
  `[project.optional-dependencies.ctrader]` to avoid contaminating the stack.

---

## 🔨 Pending tasks

### Task 1 — Engine core: portfolio + execution + runner

**What to do:**

- [x] **Portfolio** — `src/ai_trade/backtest/engine/portfolio.py`
  - Tracks positions (long/short, volume, `avg_entry_price`, `mark_price`).
  - Realized and unrealized P&L per symbol and total.
  - Events: `open_position`, `close_position`, `update_mark`, `apply_cash_flow`.
  - Equity curve as `pd.Series` indexed by timestamp.
  - Operates in base currency (USD for simplicity now; multi-currency CFD
    comes later once cTrader is unblocked).

- [x] **Execution simulator** — `src/ai_trade/backtest/engine/execution.py`
  - CFD-aware: applies bid/ask spread (fill = quote ± spread/2) + slippage.
  - Swap/overnight: `SwapModel` debits pct/day per open position on rollover.
  - Interface: `simulate_fill(order, bar) → Fill | None`.
  - Config via `ExecutionConfig(spread_pips, slippage_pips, commission_per_lot)`.

- [x] **Runner** — `src/ai_trade/backtest/engine/runner.py`
  - Bar-by-bar event loop.
  - `Strategy` protocol: `on_bar(bar, portfolio, context) → list[Order]`.
  - Orchestrates: for each timestamp, feed bars → strategy → orders →
    execution → portfolio update → mark update.
  - Emits `BacktestResult` (equity curve, trades, fills, rejected orders).

- [x] **Tests** — `tests/test_backtest_engine.py`
  - Portfolio: open/close trade in a synthetic scenario, verifies P&L.
  - Execution: fill with known spread → verifies embedded cost.
  - Runner: "buy-and-hold" strategy → equity curve matches gross return − costs.

**Accepted when:** the full suite passes; the engine runs a synthetic
scenario (e.g., buy 100 AAPL on 2020-01-02, mark for 10 days, close)
end-to-end with no errors and with hand-verifiable numbers.

**Conclusion:** Engine core complete in `src/ai_trade/backtest/engine/`
(`portfolio.py`, `execution.py`, `runner.py`, `__init__.py`) with 29 new tests
in `tests/test_backtest_engine.py` (`62 passed` total). Developed in strict
TDD: tests failed with `ModuleNotFoundError` before each implementation.

Non-obvious decisions:
- **Correct equity formula:** during TDD the naive `cash + Σ unrealized_pnl`
  formula proved wrong (ignores the cost basis of open positions);
  corrected to `cash + Σ signed_market_value` where signed_market_value =
  ±volume×mark (+long, −short). Two Portfolio tests had their expectations
  adjusted.
- **Spread in absolute price units, not pips:** `ExecutionConfig.half_spread`/
  `slippage` as direct price (caller converts pips/bps), keeps the engine
  symbol-agnostic — AAPL $0.005 and EURUSD 0.0001 use the same interface.
- **Two-pass mark-to-close:** the Runner marks before and after the strategy
  (before: fresh equity for sizing; after: removes the spread premium from
  the mark of freshly-opened positions, reflects the immediate cost in
  equity).
- **Minimal order dispatch:** buy becomes open_long OR close_short; sell
  becomes close_long OR open_short. Long-only (Clenow) exercises half the
  paths; shorts have coverage via Portfolio unit tests.
- **Equity = 10_200 hand-verifiable:** buy 10 @ 100, mark→120, cash 9_000 +
  position 1_200 = 10_200 ✓ (test_buy_and_hold_no_costs_equity_matches_position_value).

---

### Task 2 — Anti-overfit validation: CPCV + PBO + DSR + walk-forward + permutation

**What to do:**

- [x] **CPCV** — `src/ai_trade/backtest/validation/cpcv.py`
  - Algorithm from `[advances_fin_ml, ch.7, p.104-117]`: generates C(K, N_test) combinations.
  - `purge(labels, train_idx, test_idx, embargo_pct)` removes overlap.
  - Returns `Iterator[tuple[train_idx, test_idx]]` — compatible with the sklearn API.

- [x] **PBO** — `src/ai_trade/backtest/validation/pbo.py`
  - CSCV (Combinatorially Symmetric Cross-Validation) from
    `[advances_fin_ml, ch.11, p.208-211]`.
  - Input: matrix of returns (T × N_strategies).
  - Output: `pbo: float` ∈ [0, 1].
  - **Gate**: `pbo > 0.5 → reject` (rule #3).
  - Cross-check against `books/code/masters-testing-tuning/CSCV_MKT/CSCV.CPP`.

- [x] **DSR** — `src/ai_trade/backtest/validation/dsr.py`
  - Deflated Sharpe from `[advances_fin_ml, ch.14, p.261-270]`.
  - Input: observed SR, N trials, skew, kurt, sample size, cross-sectional SR variance.
  - Output: `(dsr_value, p_value)`.
  - **Gate**: report whenever N > 1 (rule #4).

- [x] **Walk-forward** — `src/ai_trade/backtest/validation/walk_forward.py`
  - Sliding splits with reoptimization (`[eval_opt_strategies]` +
    `[testing_tuning]`).
  - Config: in-sample size, out-of-sample size, step.
  - Returns `list[tuple[train_range, test_range]]`.
  - **Gate**: ≥8 windows, ≥6 profitable, DD ≤ 25% in all (rule #5).

- [x] **Permutation tests** — `src/ai_trade/backtest/validation/permutation.py`
  - Monte Carlo Permutation Test from `[stat_sound_indicators]`.
  - Cross-check against `books/code/masters-testing-tuning/MCPT_BARS/` and
    `MCPT_TRN/`.
  - p-value: frac. of permutations with Sharpe ≥ observed.

- [x] **Tests with numerical verification** — `tests/test_validation.py`
  - AFML toy examples (cited chapters) where the expected number is known.
  - Controlled returns-matrix fixtures.
  - Exercise the gates: matrix with obvious overfit → PBO > 0.5; inflated SR →
    DSR high p-value.

**Accepted when:** 5 modules implemented, numerically verified against at
least 1 canonical example from the source, tests pass, gates documented.

**Conclusion:** Anti-overfit framework complete in
`src/ai_trade/backtest/validation/` (`cpcv.py`, `pbo.py`, `dsr.py`,
`walk_forward.py`, `permutation.py`, `__init__.py`) with 52 new tests in
`tests/test_validation.py` (`114 passed` total). Added `scipy>=1.11` in
`pyproject.toml` for `norm.cdf/ppf` via `scipy.special.ndtr/ndtri`. Strict
TDD: each module had its tests created + verified RED before
implementation.

Non-obvious decisions:
- **Purge uses the `pd.Series[t0→t1]` contract:** index = t0, values = t1.
  For labels without overlap just use `pd.Series(idx, index=idx)`; for
  triple-barrier with overlap the caller passes the t1-series from
  `getEvents` (AFML p.50). Purge keeps training obs *i* if
  `t1_i < test_t0_min` or `t0_i > test_t1_max`.
- **Embargo in positions, not time:** `h = int(embargo_pct · len(times))`,
  replicating the `getEmbargoTimes` formula in AFML p.151 — more stable
  than embargo-by-duration when sampling is irregular.
- **CPCV: purge/embargo per block, not over the union:** combinations
  like (0, 5) have two disjoint blocks → each generates its own
  purge+embargo. Replicates the mlfinlab reference impl, avoids
  training sub-purge.
- **CSCV: single-trial PBO for an iid matrix is noisy.** With N=50, T=500,
  8 blocks, std(PBO) ≈ 0.19 across seeds (confirmed empirically). The
  null-case test now uses the mean of 20 independent matrices. Pragmatic
  choice to keep the test deterministic without losing statistical
  significance.
- **PBO "mirror" case gives PBO≈0.91, not 1.0:** with
  `returns[T/2:] = -returns[:T/2]` and 8 blocks, 6 of 70 partitions are
  unions of mirror-pairs (IS mean = 0 for all) → do not contribute.
  64/70 = 0.914, hand-verified. Test uses `>= 0.90`.
- **E[SR_max] has a SCALE, not just a value:** formula AFML p.222-223
  returns Z-score units (Var(SR)=1). To compare with the PSR
  `sharpe_periodic`, multiply by `√V = 1/√(T-1)` under iid-null. Without
  that scaling, DSR rejects every Sharpe >0 for N>5.
  `expected_max_sharpe(n, var_sharpe=…)` carries the parameter
  explicitly; `dsr()` default applies `1/(T-1)`.
- **Gumbel √(2 ln N) is the asymptotic UPPER LIMIT, not the mean.**
  Replaced the original test (tolerance ±15% against √(2 ln N)) with a
  direct Monte Carlo check: formula matches mean(max(N_normals))
  within ±5% for N ∈ {5, 10, 100, 1000}.
- **MCPT uses Masters `prepare_permute`/`do_permute`:** shuffle the
  `n-1` changes preserving prices[0] and prices[-1] (invariant),
  re-anchoring prices[-1] after cumsum to erase floating-point drift.
  An AR(1) test with φ=0.5 confirms the permutation destroys
  autocorrelation as expected.

---

### Task 3 — Metrics + report generator

**What to do:**

- [x] **Performance metrics** — `src/ai_trade/backtest/metrics/performance.py`
  - Pure functions: `sharpe`, `sortino`, `calmar`, `cagr`, `max_drawdown`, `volatility`, `var`.
  - Input: `pd.Series` of returns or equity curve.
  - Annualization by configurable factor (252 daily, 52 weekly, etc.).

- [x] **Report generator** — `src/ai_trade/backtest/metrics/report.py`
  - Takes `BacktestResult` + validation outputs.
  - Emits markdown to `reports/<strategy>_<YYYYMMDD-HHMM>.md` with sections:
    - Header + run date
    - **Survivorship bias disclaimer** if source is yfinance/wikipedia (mandatory)
    - Performance summary (all metrics)
    - **CPCV** distribution: mean/std/min Sharpe across all paths + histogram
    - **PBO** + verdict (pass/reject)
    - **DSR** + p-value + verdict
    - Walk-forward summary (N windows, N profitable, max DD)
    - Equity curve + drawdown chart (matplotlib PNG in `reports/assets/`)
    - Trades list (top 10 winners / losers)

**Accepted when:** a synthetic `BacktestResult` generates a valid
markdown report, with all sections, no crashes, PNG generated, survivorship
disclaimer present.

**Conclusion:** Metrics + report generator in
`src/ai_trade/backtest/metrics/` (`performance.py`, `report.py`, `__init__.py`)
with 30 new tests in `tests/test_metrics.py` (`144 passed` total). Strict
TDD — each module had tests created and verified RED (ModuleNotFoundError)
before implementation. Added `matplotlib>=3.8` in `pyproject.toml` for
the report's PNG charts.

Non-obvious decisions:
- **Survivorship disclaimer is mandatory by contract, not optional.**
  `_needs_disclaimer(source)` flags `yfinance`, `wikipedia`, `yahoo` as
  *biased* and **any other source** that does not contain an explicit
  survivorship-free marker. Rule replicates the inviolable ROADMAP rule
  (*never hide the bias from the report*). The disclaimer text includes
  "bias", "overstated", and cites ROADMAP §"Deferred decisions" for
  traceability.
- **Sortino with population downside-dev (denominator = all observations,
  not just downside ones).** Estrada formula: `√(mean(min(r−target, 0)²))`.
  When there is no return below target, returns `+inf` instead of raising —
  the report surface must always print something. Specific test checks this.
- **`_dataframe_to_markdown` inline** instead of `pd.DataFrame.to_markdown()` —
  the latter requires `tabulate` as an optional dep. Writing ~10 lines of a
  GFM writer avoids adding a dependency just to format the trades table.
- **Two `max_drawdown` passes: always positive magnitude.** Formula
  `(peak − equity) / peak` ensures DD=0 when monotone and DD=0.5 when the
  price halves. Calmar receives this raw value (not `abs()`), and divides
  CAGR by it — no risk of division by a negative.
- **VaR with `alpha=0.05` returns positive magnitude floored at 0.** If the
  5% quantile of returns is positive (strategy that never loses), VaR = 0 by
  convention — avoids reporting "gain of 1.7%" as negative VaR, which is
  confusing.
- **2-panel PNG chart (equity + underwater DD)**, `matplotlib.use("Agg")`
  for headless backend (VPS). 1200×720 RGBA dimensions, ~70KB per chart.
  Pillow-free (PNG straight from the Agg backend).

---

### Task 4 — Strategy: Clenow momentum replication

**What to do:**

- [x] **Strategy base** — `src/ai_trade/backtest/strategies/base.py`
  - Protocol/ABC: `Strategy.on_bar(bar, portfolio, context) → list[Order]`.
  - Optional callback: `on_rebalance(date, portfolio, context)`.
  - Context carries active universe, parameters, logger.

- [x] **Clenow momentum** — `src/ai_trade/backtest/strategies/clenow_momentum.py`

  Verbatim rules from `stocks_on_the_move` (mandatory citations in the docstring):

  - Rank by **90-day exponential regression slope × R²** `[p.70-72, p.77, p.98]`
  - Universe: SPX 500 point-in-time via `wikipedia_spx.constituents_on(date)`
  - Regime filter: only buy if SPX > 200d MA `[p.66-67, p.98-99]`
  - Top 20% cutoff (rank ≤ 100 in SPX) `[p.95, p.110]`
  - ATR position sizing `[p.82]`
  - Weekly rebalance (Wednesday) `[p.99, p.110]`
  - NEVER rank by "% above 200d MA" alone `[p.68]`

- [x] **CLI script** — `scripts/run_clenow_replication.py`
  - Args: `--start`, `--end`, `--cash`, `--output-dir`
  - Loads data via `YFinanceSource` + `WikipediaSPX`
  - Runs backtest via `engine.Runner`
  - Validates via `cpcv`, `pbo`, `dsr`, `walk_forward`
  - Generates report via `metrics.report`

- [x] **Integration test** — `tests/test_clenow_integration.py`
  - Short range (e.g., 2020-01-01 to 2021-12-31) for a fast test
  - Runs end-to-end on cached data (in-repo fixtures, no network)
  - Verifies: non-empty equity curve, finite metrics, report generated

- [x] **Replication document** — `reports/clenow_replication_notes.md`
  - Numbers obtained vs book numbers (Clenow reports ~CAGR 12% / Sharpe ~1.0
    in the extended version of the system) — we expect **inflation**
    from residual survivorship.
  - If directionally compatible (e.g., Sharpe > 0.5, positive CAGR), engine OK.
  - If drastically different (e.g., negative Sharpe, CAGR < 0), bug —
    investigate before advancing.

**Accepted when:** script runs without errors, report generated, integration
test passes, numbers are sane, replication doc written.

**Conclusion:** Clenow replication complete in
`src/ai_trade/backtest/strategies/` (`base.py`, `clenow_momentum.py`,
`__init__.py`), CLI script `scripts/run_clenow_replication.py` and doc
`reports/clenow_replication_notes.md`. 29 new tests in
`tests/test_strategy_base.py` (8) + `tests/test_clenow_strategy.py` (19) +
`tests/test_clenow_integration.py` (2) → **173 passed** total. Strict TDD
(each module had RED tests with `ModuleNotFoundError` before
implementation). Replication run over 2023-07-01 → 2023-12-31 with
503 point-in-time SPX tickers (17 skipped due to survivorship/rename);
final equity $93 965 (CAGR −11.79%, Sharpe −0.79, max DD 13.55%) —
within the noise expected for a choppy 6-month 2023 H2 window, winners/losers
composition (LLY/GOOG/AMGN vs NCLH/CMG/BKR) confirms that the ranking +
regime filter logic is operating correctly.

Non-obvious decisions:
- **Strategy base = Protocol re-export + ABC rebalance-dispatcher, not a
  hierarchy.** The Runner already defines `Strategy` as a Protocol in
  `runner.py`; `base.py` re-exports (same object, not duplication) +
  adds `StrategyBase` (ABC with `should_rebalance` + `on_rebalance`
  no-op-by-default) and `StrategyContext` (typed dataclass, optional).
  Keeps 99% of Protocol flexibility without forcing subclassing.
- **`self.data` carries the full history; Runner iterates the
  `[start, end]` slice.** During the first Wed after `--start`, the
  strategy needs to look 200 days back (SPX MA) and 90 days (regression).
  If only the bounded slice were passed to the Runner, there would be no
  warmup. CLI passes `data_bounded` to the Runner but the full `data` to
  the strategy.
- **Sells before buys in the same list.** The Runner executes orders in
  insertion order (see `runner.py:114-122`). Sells first → cash released
  is available for subsequent buys on the same bar, no need for a
  two-phase mechanism.
- **Buy gated by regime ON, sell NOT.** Literally replicates Clenow
  p.94-95: *"Do not sell a holding just because the index drops below
  the 200d MA — only stop adding new positions."* Synthetic tests
  `test_regime_filter_blocks_buys_when_below_ma` and
  `test_strategy_respects_regime_filter_during_index_drawdown` cover this.
- **Sizing = `floor(equity × 0.001 / ATR20)` with `equity` (not cash).**
  Clenow always talks in "account value" (p.88), not cash. Cash-insuff
  handled via `break` in the top-down loop (p.99 verbatim).
- **Wikipedia scrape bug fixed in passing.** `pd.read_html`
  returned 403 Forbidden (default UA blocked) and failed with "Date"
  vs "Effective Date" in the header. Fix: `urllib.request` with
  `User-Agent: ai-trade/0.1 research`, + case-insensitive substring
  matching in `_flatten_changes_table`. Unblocked the real CLI.
- **CPCV/PBO/DSR skipped in the CLI (single-trial).** The 3 gates compare
  N≥2 strategies — a fixed Clenow replication is 1 trial. Walk-forward
  over the realized equity curve (8 windows) is the only meaningful
  validation; reports `reject` with 4/8 profitable in 6 months (expected
  — 3 weeks per window is pure noise). Full gate requires a parameter
  grid, a Phase 3 task.
- **Auto-generated reports → `.gitignore`.** `reports/<strategy>_<stamp>.md`
  and `reports/assets/` ignored. Hand-written doc (`clenow_replication_
  notes.md`) is versioned.

---

### Task 5 — Phase 2 wrap-up

**What to do:**

- [x] **ROADMAP.md** — mark Phase 2 ✅ Completed in the status table.
- [x] **Root README.md** — add a "How to run a backtest" section with an
      example of `run_clenow_replication.py`.
- [x] **knowledge/SKILL.md** — if we discover a rule or pitfall during
      the work that would strengthen the skill, record it (via re-absorption
      of the relevant book or justified manual update).
- [x] **Reassess** (in a new section here in the spec or in `specs/backtest_phase3.md`):
      the 3 deferred decisions from ROADMAP §"Deferred decisions" — paid data?
      vectorbt? next strategy? — now informed by the Clenow findings.

**Accepted when:** docs updated, project state reflects Phase 2 completed,
Phase 3 (rigorous backtest / validation in production) starts with new
decisions made.

**Conclusion:** Phase 2 closed — `ROADMAP.md` §Status marks Phase 2 ✅ and
renames the scope to "Backtest Module" (delivered reality) with a preamble
explaining that the original Strategy Engine (Universe Selector + fundamented
candidates) goes to Phase 2.5. The root README.md got a "How to run a
backtest" section with a CLI example + output layout + link to the
replication notes. `knowledge/SKILL.md` **was not changed** — the insights
from Tasks 1-4 are engineering/implementation (equity formula, mark-to-close
two-pass, E[SR_max] Z-score units, single-seed-noisy PBO), not citable
trading rules; they live in the Conclusions of this spec by design (knowledge
= book rules with `[slug, p.X]` citation; spec = engineering decisions).
Reassessment of the 3 deferred decisions below — all **kept deferred** with
updated gates in light of what Clenow showed.

---

### Post-Phase 2 reassessment: deferred decisions from the ROADMAP

Informed by the Clenow replication findings (Task 4). Original reference:
`ROADMAP.md` §"Decisions deferred for reassessment".

#### 1. Data source (yfinance → Tiingo/EOD/Norgate)

**Original gate:** "Reassess when the first strategy passes the anti-overfit
gates (CPCV + PBO + DSR)."

**Clenow findings:** the engine ran on 503 SPX point-in-time tickers in the
2023-07-01 → 2023-12-31 window; 17 tickers skipped due to survivorship/rename =
**3.4%** of the universe. In this regime (choppy H2 2023), the residual bias
was *sampleable* but not dominant — a 3-4% residual bias does not explain a
CAGR of −11.79%; the winners/losers composition (LLY/GOOG/AMGN vs
NCLH/CMG/BKR) is coherent with the regime. Original gate not yet reached:
CPCV/PBO/DSR have no discriminatory power in single-trial (one Clenow with
fixed parameters = N=1).

**Decision: kept deferred.** Updated gate:

> Migrate to a paid source when **at least one strategy exists whose
> edge has survived a parameter grid in the custom engine with
> PBO < 0.5, DSR p-value < 0.05 and walk-forward with ≥6/8 profitable
> windows on yfinance+Wikipedia data**. Migration serves as an *ablation
> study* of the edge itself: if the edge survives on the paid source,
> Phase 4 proceeds; if it dies once survivorship is removed, the edge
> was an artifact.

#### 2. vectorbt (fast-triage sandbox)

**Original gate:** "Reassess when iterating on indicator/parameter
hypotheses has measurable friction (>30 min to test a simple variation)."

**Clenow findings:** the custom engine ran Clenow end-to-end in minutes
(bound by data fetch, not compute). **Grid search not yet attempted** —
Task 4 was single-trial with fixed parameters. Iteration friction has
not become a bottleneck because we have not iterated.

**Decision: kept deferred.** Updated gate:

> Reassess when the first grid search in the custom engine (minimum:
> 20 parameter combinations of Clenow or the next strategy) takes
> >30 min per variation OR prototyping an indicator variation requires
> >3 new code files. In those scenarios vectorbt enters as a sandbox;
> the custom engine remains the source of truth for the final backtest.

#### 3. Second strategy after Clenow

**Original gate:** "Reassess when Clenow runs and the engine passes the
gates. Candidates: AFML meta-label, Ehlers DSP, Chan mean-reversion."

**Clenow findings:** Clenow ran. The engine delivered: portfolio,
CFD-aware execution, a validation framework with 5 modules (CPCV/PBO/DSR/
walk-forward/MCPT), metrics + report with mandatory survivorship
disclaimer. 173 tests green. **But the engine did not pass the gates in
the sense the ROADMAP imagined** — because gates measure a distribution
over multiple trials, and single-trial Clenow does not exercise them.
The Phase 2 problem **was not to detect edge**; it was to build and
validate the infra. Phase 3 needs to **close the Clenow loop with a
real grid + gates** before adding a new strategy.

**Decision: kept deferred.** Revision:

> First pay down the Clenow technical debt: grid search over defensible
> parameters (lookback 60/90/120, top 10%/20%/30%, ATR risk budget
> 0.001/0.002), exercise CPCV/PBO/DSR with N≥20, report the real
> distribution. **Only then** choose the second strategy, informed by:
> (a) which failure mode Clenow exposed (entry? exit? regime?);
> (b) whether we want to diversify by mechanic (mean-reversion vs trend)
> or by timeframe (swing vs intraday).
>
> Candidates still valid (ordered by CFD compatibility):
> 1. **Ehlers DSP** `[rocket_science, cycle_analytics]` — short holding,
>    CFD-native, attacks entry/exit (complements Clenow whose
>    weekly rebalance is a fixed rhythm).
> 2. **AFML meta-labeling** `[advances_fin_ml, ch.3]` — overlay on
>    Clenow (primary) with ML confidence (secondary); attacks overfitting
>    via trade selection, not via parameters.
> 3. **Chan mean-reversion / pairs** `[algo_trading_chan]` — opposite of
>    Clenow, good to diversify regime; but cointegration in CFD requires
>    care with carry costs.

#### Strategic synthesis

The 3 decisions were deferred with the **same rationale**: what unlocks
each is **running Clenow on a parameter grid with active gates**. This
defines the natural scope of **Phase 2.5** (or the start of Phase 3 in
the ROADMAP, if you prefer linear numbering): operate the anti-overfit
gates over Clenow itself, across multiple trials, to obtain an honest
distribution of Sharpe and PBO. Phase 2 delivered the **ammunition**
(engine + validation); Phase 2.5 will **use it**.

---

## 📌 References

- `ROADMAP.md` — phase status + deferred decisions + 2-stage model
- `README.md` — CPCV/PBO/DSR concepts + Clenow universe + survivorship
- `knowledge/SKILL.md` — inviolable rules #1-7
- `knowledge/books/advances_fin_ml.md` — primary CPCV/PBO/DSR source
- `knowledge/books/stocks_on_the_move.md` — primary Clenow source
- `books/code/masters-testing-tuning/` — reference C++ (MCPT, CSCV)
