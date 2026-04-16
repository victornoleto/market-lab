# Execution Plan: Deep Validation of Bollinger MR Winners + Dual-Environment Architecture

**Use this document as the starting prompt in a clean Claude Code session.** It is self-contained.

---

## 🚀 Quick start for clean session

Paste this to Claude at session start:

> Read `docs/superpowers/plans/2026-04-16-winners-deep-validation.md` in full, then `jornada/README.md`, then `docs/self_improvement/memory.md`. Run `.venv/bin/pytest -q` to confirm 501 tests green. Then tell me which task we should start with based on my direction.

---

## 📍 Current state (2026-04-16)

- **Branch:** `self-improve/overnight-20260415` (not main; all work commits here)
- **Tests:** 501 green (`.venv/bin/pytest -q`)
- **Winners found:** 3 (all same family — Bollinger MR 1h long-only)
  - SPY: Sharpe 1.314 IS / 1.312 OOS 2025 / 2.585 Q1-2026
  - XLK: Sharpe 1.930 IS / 1.781 OOS 2025 / 2.341 Q1-2026 (best)
  - XLE: Sharpe 1.584 IS / 1.200 OOS 2025 / 1.879 Q1-2026
  - Config (all): `window=20, std_mult=1.5, stop_pct=0.02, max_hold=24` (1h bars = 1 day hold)
- **Demoted:** EEM (failed Q1-2026 stress), Kalman Pairs SPY-IWM (failed OOS 2025)
- **Loop:** NOT running. Last iteration = 17. Do NOT launch `self_improve_loop.sh` for this work — execution is manual/synchronous.

---

## 🎯 Project philosophy (IMMUTABLE)

1. **Target ~5-10 robust strategies**, deep expertise > breadth. Quality over quantity.
2. **Every strategy MUST pass CPCV/PBO/DSR.** Non-negotiable — this is the project's scientific gate.
3. **Two production environments run in parallel:**
   - **[CFD/Pepperstone]** short-hold (hours~few days), swap cost. Primary focus. Winners here: Bollinger MR.
   - **[Stock broker]** long-hold (weeks~months), 15% BR tax on profit monthly. Secondary — for strategies that need daily/monthly timeframes where swap would kill them.
4. **Don't lose the winners.** No refactor of frozen winner code.
5. **All technical decisions cite `[book.slug, p.X]`** from `books/summaries/`.

---

## 🔒 Invariants — DO NOT TOUCH

These files are frozen. Any new work extends around them, never modifies:

- `src/ai_trade/backtest/strategies/bollinger_mr.py`
- `src/ai_trade/backtest/grid/bollinger_mr_config.py`
- `scripts/run_grid_bollinger_mr.py`
- `reports/grid_bollinger_mr_spy_1h_8wf_20260415-235041/` (original PASS report)
- `reports/grid_bollinger_mr_{XLK,XLE}_1h_iter15/`
- `src/ai_trade/backtest/validation/{cpcv,dsr,pbo,permutation,walk_forward}.py`

**DO NOT:**
- Run `scripts/self_improve_loop.sh` for this work (it's for overnight, not interactive day work).
- Modify validation gate logic (CPCV/PBO/DSR/WF thresholds are frozen — part of scientific contract).
- Commit to `main` directly — all work on `self-improve/overnight-20260415`.
- Skip `pytest -q` after any code change.

---

## 📋 Tasks (ordered by priority)

Each task is self-contained. User drives pace — review after each, commit, move on.

### Task 0A — Tiingo cache audit 🔍

**Priority:** CRITICAL (blocks all other tasks — if data is silently stale, every backtest is suspect)
**Estimated time:** 30-45 min
**Type:** Research + possible code fix

**Objective:** Confirm that (a) cache doesn't serve stale 1h data for recent dates, (b) the Q1-2026 forward-stress tests actually used fresh 2026 data and weren't look-ahead, (c) the lazy-cache logic is working as designed.

**Inputs (read these first):**
- `src/ai_trade/backtest/data/tiingo_source.py` — fetch logic
- `src/ai_trade/backtest/data/tiingo_storage.py` — cache logic
- `data/tiingo/manifest.json` — cache index
- `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` — intended design

**Steps:**
1. Map cache-hit vs cache-miss logic. When does it fetch fresh? When does it return cached?
2. Check file mtimes for SPY/XLK/XLE daily + 1h parquets: `ls -la data/tiingo/{daily,1hour}/prices/{SPY,XLK,XLE}*.parquet`
3. For each winner's grid run + OOS + Q1-2026 report, cross-reference: what was the cache mtime vs the report timestamp?
4. Active test: fetch SPY 1h for last 7 days via `tiingo_service`. Confirm it calls Tiingo API (not just returns cache) when trailing window is requested.
5. If stale: describe the bug, propose fix.

**Outputs:**
- `jornada/2026-04-16-HHMM-tiingo-cache-audit.md` — findings + fix plan
- If fix needed: separate commit editing `tiingo_source.py` / `tiingo_storage.py` with new tests

**Validation:**
- Tests stay green (501+)
- Audit report answers clearly: "Is Q1-2026 forward test trustworthy?" (yes/no/with caveat)

**Commit:**
```
chore(tiingo): audit cache freshness — <1-line summary of finding>
```

---

### Task 1A — Monte Carlo bootstrap on winner trades 📊

**Priority:** CRITICAL (gives honest CI on each winner's metrics)
**Estimated time:** 60-90 min
**Type:** Code + backtest

**Objective:** For each of SPY/XLK/XLE, produce 95% confidence intervals on Sharpe/CAGR/MaxDD via stationary bootstrap of the trade sequence. Current reports give point estimates; we need bands.

**Inputs:**
- Trade logs from winner backtests (may need to re-run to emit them — see step 1)
- `src/ai_trade/backtest/validation/permutation.py` for random-state pattern

**Steps:**
1. Edit `scripts/run_oos_bollinger_mr.py`: add `--emit-trades` flag that writes `trades.csv` (entry_ts, exit_ts, pnl, side, price_entry, price_exit).
2. Re-run OOS with `--emit-trades` for SPY, XLK, XLE (2021-2024 training + 2025 OOS + Q1-2026 forward).
3. Create `src/ai_trade/backtest/validation/bootstrap.py` — stationary bootstrap with geometric block length (mean block=5 trades) per Politis & Romano (1994). Implement:
   - `stationary_bootstrap_trades(trades: np.ndarray, block_mean: int = 5, n_resamples: int = 10000, seed: int = 42) -> np.ndarray`
   - Returns resampled trade arrays.
4. Create `scripts/run_mc_bootstrap_bollinger_mr.py` — reads trades.csv, runs bootstrap, computes Sharpe/CAGR/MaxDD per resample, outputs 95% CI.
5. Run for each of SPY/XLK/XLE.

**Outputs:**
- `reports/bollinger_mr_mc_bootstrap/{spy,xlk,xle}_ci.json` — CI numbers
- `reports/bollinger_mr_mc_bootstrap/summary.md` — tables with point + CI
- `reports/bollinger_mr_mc_bootstrap/assets/sharpe_hist_{spy,xlk,xle}.png` — distribution histograms

**Citations required:** `[advances_fin_ml, p.196-202, ch.11]` on statistical significance of Sharpe. Politis & Romano (1994) for stationary bootstrap (book: to verify which summary covers it; `masters_permutation_tests` likely).

**Validation:**
- Tests stay green
- CI lower bound for SPY Sharpe must be >0 (else edge not significant even before deflation)

**Commit(s):** 2 commits
```
feat(validation): stationary bootstrap for trade sequences [advances_fin_ml, p.196-202]
feat(reports): MC bootstrap CI for Bollinger MR winners on SPY/XLK/XLE
```

---

### Task 1B — Cross-asset trade overlap 🔗

**Priority:** CRITICAL (determines if 3 "winners" = 1 edge × 3 tickers)
**Estimated time:** 30-45 min
**Type:** Analysis only (no new strategy)

**Objective:** Are SPY/XLK/XLE winners independent edges, or correlated? If they trade on same days with same direction, portfolio diversification is illusory.

**Inputs:**
- Trade logs from Task 1A (emit-trades output)
- `src/ai_trade/backtest/portfolio/combined.py` — existing multi-asset combiner

**Steps:**
1. Create `scripts/run_trade_overlap_bollinger_mr.py`.
2. Align SPY/XLK/XLE trade timestamps at 1h bar granularity.
3. Compute:
   - Jaccard similarity of entry bars (SPY∩XLK / SPY∪XLK, etc.)
   - Pearson correlation of daily P&L (resampled to daily from 1h)
   - Effective N via Ledoit-Wolf shrunk correlation
   - Equal-weight portfolio Sharpe vs mean-of-3 — the diversification lift
4. Output heatmap.

**Outputs:**
- `reports/bollinger_mr_overlap/summary.md` — decision: are they really independent?
- `reports/bollinger_mr_overlap/assets/daily_pnl_corr.png`

**Validation:**
- If correlation > 0.7: document that "3 winners" is really 1 edge; plan must adapt (phase 3 dual-env design should reflect this)
- If correlation < 0.4: genuine diversification — confirm with portfolio simulation

**Commit:**
```
feat(reports): cross-asset trade overlap — SPY/XLK/XLE independence check
```

---

### Task 1C — $1k sizing + risk_pct sensitivity 💰

**Priority:** CRITICAL (user's concern: 0.95 is too aggressive for live)
**Estimated time:** 60-90 min
**Type:** Code + simulation

**Objective:** Simulate actual Pepperstone $1k account execution. Find realistic risk_pct for live (user suggested 0.2-0.5). Compare Sharpe/MaxDD/CAGR at 5 risk levels.

**Inputs:**
- Pepperstone SPX500 CFD specs (document in report):
  - 1 contract = $1/pt × index value (~$6k notional at 6000)
  - Margin: 1% (minimum at Razor account)
  - Commission: $3.50/side (Razor) or spread-only (Standard)
  - Min lot: 0.01
  - Minimum stop: 1 point (for most index CFDs)
- Winner config: w=20, std=1.5, stop=0.02, max_hold=24

**Steps:**
1. Create `src/ai_trade/backtest/execution/cfd_broker.py`:
   - `CFDBrokerCostModel(spread_pt, commission_per_side, margin_pct, min_lot)`
   - `compute_lot_size(equity, risk_pct, stop_distance_pts, contract_value)` returning rounded-to-min lot or 0 if under-size
   - `compute_trade_cost(lot, entry, exit, bars_held, swap_pct_per_day)` returning net P&L after costs
2. Create `scripts/run_pepperstone_sizing_bollinger_mr.py`:
   - Takes winner config + risk_pct from {0.20, 0.35, 0.50, 0.75, 0.95}
   - Simulates $1k account start, 2021-2025, using CFDBrokerCostModel
   - Outputs: final equity, Sharpe (post-cost), MaxDD, # rejected trades (under min lot), months with 0 trades
3. Add unit tests in `tests/test_cfd_broker.py` (~5 tests for sizing edge cases)

**Outputs:**
- `reports/bollinger_mr_pepperstone_sizing/summary.md` — table of 5 risk_pct levels × SPY/XLK/XLE
- Equity curves overlay
- Final recommendation: X% risk_pct for live

**Validation:**
- Tests green (501 + new CFD broker tests)
- At risk_pct=0.20: $1k can still execute >80% of trades? (otherwise capital too low — user needs to know)
- Sharpe at 0.35 risk_pct vs 0.95: how much degradation? (if negligible, use 0.35 for live)

**Commit(s):**
```
feat(execution): CFD broker cost model with Pepperstone specs [systematic_trading, p.144]
feat(reports): $1k account sizing + risk_pct sensitivity for Bollinger MR winners
```

---

### Task 1D — Regime decomposition 📈

**Priority:** HIGH
**Estimated time:** 45-60 min
**Type:** Analysis

**Objective:** Break winner performance by year and VIX quintile. Identify where strategy breaks.

**Inputs:**
- Trade logs from 1A
- VIX daily data (fetch via `src/ai_trade/backtest/data/tiingo_service.py` if not cached)

**Steps:**
1. Create `scripts/run_regime_decomp_bollinger_mr.py`.
2. For each winner, assign each trading day a VIX quintile bucket (Q1 calm → Q5 panic) based on VIX close.
3. Compute Sharpe/PnL/WR per year × per quintile (20 buckets, 5y × 4 year groups or 5y × 5 quintiles).
4. Plot heatmap.

**Outputs:**
- `reports/bollinger_mr_regime_decomp/summary.md` — which regimes kill the strategy?
- `reports/bollinger_mr_regime_decomp/assets/heatmap_year_x_vix_{spy,xlk,xle}.png`

**Validation:**
- Report flags any VIX quintile where Sharpe is < 0
- 2022 bear should be isolated — is strategy still profitable that year?

**Commit:**
```
feat(reports): regime decomposition (year × VIX quintile) for Bollinger MR winners
```

---

### Task 1E — Long-history daily stress test (2008, 2018, 2020) 📜

**Priority:** HIGH (user concern: 2021-2025 too narrow)
**Estimated time:** 45-60 min
**Type:** Backtest on existing daily data

**Objective:** Run same Bollinger MR logic on **daily** SPY 1993-2026 (strategy is bar-agnostic — reuses code as-is with different input). Test if edge existed in 2008 GFC, 2018 vol spikes (Feb and Q4), 2020 COVID crash, 2022 bear.

**Important caveat:** Daily is INCOMPATIBLE with Pepperstone swap. This is a pure **sanity check** — if edge exists in daily long history, strategy is fundamental, not regime-lucky.

**Inputs:**
- `data/tiingo/daily/prices/SPY.parquet` (1993-2026, already cached)
- Existing `BollingerMRStrategy` (bar-agnostic — reuse directly)
- Existing grid runner infrastructure

**Steps:**
1. Create `scripts/run_bollinger_mr_daily_longhistory.py` — reuses `run_grid_bollinger_mr.py` pattern but with `--frequency daily` and longer date range.
2. Run full grid with N=4 configs (same {w, std} axes).
3. Run era-by-era single-config backtest for best config:
   - 1993-2000 (pre-dotcom)
   - 2000-2009 (dotcom + GFC)
   - 2010-2019 (long bull)
   - 2020-2026 (COVID + tariffs)
   - Zoom: 2018 vol spikes, 2020 COVID crash
4. For max_hold, scale from 24 bars (1h = 1 day) to 5 bars (daily = 5 days) — verify the "short-hold" semantics survive.

**Outputs:**
- `reports/bollinger_mr_daily_longhistory/summary.md` — per-era Sharpe/CAGR/MaxDD
- `reports/bollinger_mr_daily_longhistory/assets/equity_curve_1993_2026.png`
- `reports/bollinger_mr_daily_longhistory/assets/zoom_{2008_gfc,2018_vol,2020_covid}.png`

**Validation:**
- Report clearly states: did edge exist in all eras? In which did it break?
- If edge exists even in 2008: strong evidence the strategy is fundamental
- If edge is only 2021+: confirms user's concern, strategy is regime-dependent

**Commit:**
```
feat(reports): long-history daily stress test (1993-2026) for Bollinger MR
```

---

### Task 1F — Parameter perturbation 📐

**Priority:** MEDIUM
**Estimated time:** 45-60 min
**Type:** Backtest (no gate)

**Objective:** Is (w=20, std=1.5) an isolated peak (overfit) or a plateau (robust)? Visualize stability surface.

**Inputs:**
- 1h cached data for SPY/XLK/XLE

**Steps:**
1. Create `scripts/run_perturbation_bollinger_mr.py`.
2. 25-cell grid: `w ∈ {18, 19, 20, 21, 22}` × `std ∈ {1.3, 1.4, 1.5, 1.6, 1.7}`.
3. IS-only (no WF, no PBO, no DSR — purely visualization).
4. Heatmap of Sharpe for each asset.

**Outputs:**
- `reports/bollinger_mr_perturbation/summary.md`
- `reports/bollinger_mr_perturbation/assets/heatmap_{spy,xlk,xle}.png`

**Validation:**
- Report annotates: is neighborhood of (20, 1.5) a plateau (similar Sharpes within ±1 step) or isolated peak?

**Commit:**
```
feat(reports): parameter perturbation sensitivity for Bollinger MR winners
```

---

### Task 1H — GARCH vol-sizing overlay 🧮

**Priority:** HIGH (user suggestion for safer live sizing)
**Estimated time:** 90-120 min
**Type:** Code + new strategy + full CPCV/PBO/DSR gate

**Objective:** Create GARCH-sized Bollinger MR — same entry/exit, but position sized by GARCH-forecasted σ. Gate through full 3 layers. If passes, it's a safer live variant (dynamic risk vs 0.95 static).

**Inputs:**
- `arch` Python package — add to `pyproject.toml [dependency-groups] dev`, run `uv sync`
- `src/ai_trade/backtest/strategies/bollinger_mr.py` (reuse signals)
- Citation: `[machine_trading, p.126-127, ch.4]`

**Steps:**
1. Add `arch` to pyproject.toml, run `uv sync`, verify install.
2. Create `src/ai_trade/backtest/indicators/garch.py`:
   - `GarchForecaster(p=1, q=1, rescale=True)` — rolling fit on last N bars, forecast σ_{t+1}
   - Unit tests with synthetic data
3. Create `src/ai_trade/backtest/strategies/bollinger_mr_garch.py`:
   - Wraps/subclasses `BollingerMRStrategy` entry/exit
   - Overrides `_maybe_enter` — instead of `risk_pct_of_equity × equity / price`, use `(target_vol / σ_forecast) × equity / price`
   - New params: `target_vol_annual` (e.g., 0.12 = 12% target vol)
4. Create `src/ai_trade/backtest/grid/bollinger_mr_garch_config.py`:
   - N=4 configs: target_vol ∈ {0.08, 0.12, 0.16, 0.20}, rest fixed
5. Create `scripts/run_grid_bollinger_mr_garch.py` — full gated grid.
6. Unit tests in `tests/test_bollinger_mr_garch.py` (~8 tests).
7. Run on SPY 1h 2021-2025 with 8 WF windows.

**Outputs:**
- `reports/grid_bollinger_mr_garch_spy_1h_<ts>/` — full grid verdict (PASS/FAIL)
- If passes: run OOS 2025 + Q1-2026 stress

**Validation:**
- Tests green
- If PASS: 4th winner in the family with safer sizing
- If FAIL: document reason — GARCH forecast too noisy at 1h? target_vol grid wrong?

**Commit(s):**
```
deps: add arch package for GARCH forecasting
feat(indicators): GARCH(1,1) forecaster [machine_trading, p.126-127]
feat(strategies): Bollinger MR with GARCH vol-sizing [machine_trading, p.126-127]
feat(grid): Bollinger MR GARCH grid config (N=4 target_vol sweep)
feat(reports): Bollinger MR GARCH grid result
```

---

### Task 1G — Production-readiness decision doc 🏁

**Priority:** CRITICAL (final deliverable for Phase 1)
**Estimated time:** 60-90 min (synthesis + writing)
**Type:** Documentation only

**Objective:** Integrate all Phase 1 findings into a go/no-go verdict for demo trading.

**Inputs:** Reports from 0A, 1A, 1B, 1C, 1D, 1E, 1F, 1H.

**Content (sections):**
1. **Verdict** (one line): READY / READY-WITH-CAVEATS / NOT-READY
2. **What we know with 95% confidence** — CI bands from 1A, consistency across regimes from 1D/1E
3. **Expected live performance at $1k** — table from 1C at risk_pct=0.20 or 0.35
4. **Known weak points** — user's concerns addressed:
   - 0.95 risk_pct is too aggressive → use 0.35 (from 1C)
   - 2021-2025 narrow → long-history says X (from 1E)
5. **Pause triggers** (monitoring):
   - VIX > Qk from 1D
   - X consecutive losing months
   - Live Sharpe < threshold after N trades
   - Regime indicators from 1D
6. **Independence of 3 assets** — from 1B (if they correlate > 0.7, treat as 1 strategy not 3)
7. **Recommended next steps:**
   - If READY: move to Phase 2 (GLD/XAU/USD) + Phase 3 (architecture) + paper trading
   - If NOT-READY: specific remediation tasks

**Output:**
- `jornada/2026-04-16-HHMM-bollinger-mr-production-readiness.md`

**Update:**
- `jornada/README.md` — add entry at top

**Commit:**
```
docs(jornada): Bollinger MR production-readiness verdict — <VERDICT>
```

---

### Task 2A — GLD 1h validation 🏆

**Priority:** MEDIUM (answers "XLK arbitrário?" concern)
**Estimated time:** 15-30 min (no new code)
**Type:** Run existing grid on new asset

**Steps:**
1. `.venv/bin/python scripts/run_grid_bollinger_mr.py --data-source tiingo --symbol GLD --asset-class etf --storage-root data/tiingo --start 2021-01-01 --end 2025-12-31 --frequency 1hour --output-dir reports/ --n-jobs 4 --run-id grid_bollinger_mr_GLD_1h_iter18`
2. If PASS: `scripts/run_oos_bollinger_mr.py --symbol GLD --oos-start 2025-01-01 --oos-end 2025-12-31` and `--oos-start 2026-01-01 --oos-end 2026-04-15`
3. Document in `jornada/2026-04-16-HHMM-bollinger-mr-gld-validation.md`

**Commit:**
```
docs(jornada): Bollinger MR GLD 1h validation — <PASS/FAIL>
```

---

### Task 2B — XAU/USD 1h validation 🏅

**Priority:** MEDIUM
**Estimated time:** 30-45 min (may need forex handling fix)
**Type:** Adapt existing grid for forex

**Steps:**
1. Check `scripts/run_grid_bollinger_mr.py` — does `--asset-class forex` skip `adjust_ohlc` (which assumes equity splits/dividends)?
2. If not: add branch in strategy or runner to skip adjust for forex.
3. Run: `.venv/bin/python scripts/run_grid_bollinger_mr.py --symbol xauusd --asset-class forex --frequency 1hour --start 2021-01-01 --end 2025-12-31 ...`
4. If passes: OOS + Q1-2026 stress
5. Compare to GLD result (from 2A) — should agree if edge is real on gold.
6. Document: `jornada/2026-04-16-HHMM-bollinger-mr-xauusd-validation.md`

**Commit:**
```
docs(jornada): Bollinger MR XAU/USD 1h validation vs GLD
```

---

### Task 3A — Dual-environment architecture design 🏗️

**Priority:** MEDIUM (design doc, no code)
**Estimated time:** 90 min
**Type:** Documentation only

**Objective:** Design how to organize the codebase for 2 production paths (CFD Pepperstone + stock broker). No implementation yet — just the contract.

**Content:**
- Strategy metadata contract: `broker_scenario: "cfd" | "stock_broker"` on each strategy
- Cost models: `CFDCostModel` (swap, spread, commission) vs `StockBrokerCostModel` (commission + 15% BR monthly tax)
- Directory structure: where do the 2 cost models live? Where do strategies declare their scenario?
- Report tagging: jornada/ subdirectories? diagnostic header field?
- Impact on existing code: BollingerMR → "cfd"; future Gayed LRS → "stock_broker"
- Explicit: **no refactor yet.** Just the contract.

**Outputs:**
- `docs/superpowers/specs/2026-04-16-dual-environment-design.md`
- `ROADMAP.md` — new "Dual-environment production model" section

**Commit:**
```
docs(specs): dual-environment architecture design (CFD + stock broker)
```

---

### Task 4 — Gayed LRS + leveraged ETFs 📈 (AFTER Phase 1+2+3)

Only start after 1-3 complete. This is Phase 4 of the master plan. See parent plan at `/home/victor/.claude/plans/abstract-juggling-wombat.md` §Phase 4 for the 4 sub-tasks (implementation + grid + tax + real-SSO validation). Do not start until a prior review gate.

---

## 🔁 Standard workflow per task

1. **Read the task section in full** above.
2. **Confirm baseline:** `.venv/bin/pytest -q` → 501+ green
3. **Confirm clean branch:** `git status` clean or understood
4. **Execute the steps.** Write code iteratively, run tests as you go.
5. **Generate outputs** (reports, jornada entries).
6. **Re-run tests.**
7. **Review with user** — paste key findings/numbers.
8. **Commit** with the template commit message.
9. **Update memory** if significant finding: edit `docs/self_improvement/memory.md` (keep it < 15KB).

---

## 🚨 Escape hatches

- **Tests break after change:** revert the offending file via `git checkout -- <file>`, investigate, retry.
- **Grid run fails:** check `logs/grid.log` and `.cache/grid_runs/<run_id>/debug.log`. Most common: missing data or wrong frequency flag.
- **OOS stress FAILS for a winner:** that winner is demoted. Update memory.md, document in jornada/. Don't hide the result.
- **Tiingo API error:** check `.env` TIINGO_API_KEY, check rate limits. Cache should cover most cases after first fetch.

---

## 📚 Required reading for the new session

Must-read, in order:
1. This file (you are here)
2. `jornada/README.md` — project state + entry index
3. `docs/self_improvement/memory.md` — loop state + winners summary
4. `jornada/2026-04-15-2350-bollinger-mr-1h-PASS.md` — original winner doc
5. `jornada/2026-04-16-0100-bollinger-mr-sector-etfs-PASS.md` — XLK/XLE winners
6. `jornada/2026-04-16-0059-bollinger-mr-2026q1-stress-test.md` — Q1-2026 stress (+EEM demotion)

Reference (read when touching a specific area):
- `ROADMAP.md` — phase map, non-negotiables
- `.claude/CLAUDE.md` — collaboration rules
- `knowledge/SKILL.md` — knowledge base entry
- `src/ai_trade/backtest/strategies/bollinger_mr.py` — frozen winner code
- `src/ai_trade/backtest/grid/gates.py` — gate evaluator (frozen)

---

## ✅ Completion criteria per phase

| Phase | Done when |
|-------|-----------|
| 0A | Tiingo audit doc exists in jornada/; any fixes committed + tests green |
| 1A-1H | All reports in reports/; tests green; winners not touched |
| 1G | Production-readiness doc answers GO/NO-GO clearly |
| 2A-2B | GLD + XAU/USD results documented (PASS → new winners, FAIL → reasoning) |
| 3A | Architecture spec doc + ROADMAP updated |
| 4 | Gayed LRS gated + BR-tax comparison vs Bollinger MR |

**Full-plan completion:** production-readiness verdict says GO, OR we have concrete remediation plan for NO-GO items.
