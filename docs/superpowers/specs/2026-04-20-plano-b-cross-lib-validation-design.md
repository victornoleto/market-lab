# Plano B Cross-Library Validation — Design Spec

> **Status:** Draft (brainstorming complete, awaiting user review before writing-plans).
> **Date:** 2026-04-20.
> **Owner:** ai-trade / Phase 3.5c.
> **Target:** validate Plano B V4 winner (3-leg EW SSO+QLD+UGL, OOS Sharpe 2.609 / CAGR 39.19% / MaxDD -12.22% on 2004-2026) by reproducing it in multiple independent backtesting libraries.
> **Companion jornada entry (post-execution):** `jornada/YYYY-MM-DD-HHmm-plano-b-cross-lib-verdict.md`.

---

## 1. Context and motivation

Plano B V4 was promoted to production on 2026-04-18 after passing the 5 formal gates (PBO-equivalent via DSR n_trials=4, WF 8/8, OOS Sharpe > 0, Stress Sharpe > 0, bootstrap 99.9% CI > 0) in two windows: canonical 2004-2026 (21.4y) and extended 1986-2026 (40y). See `reports/phase3_5b/PRODUCTION.md` §12.

The engine that produced these numbers is `src/ai_trade/backtest/strategies/letf_rotation.py` — a **return-series simulator** that bypasses the bar-level Portfolio/Bar machinery for speed. The strategy's claim ("real edge, not implementation artifact") depends on us trusting that this single engine implements the rules correctly.

This spec defines a cross-library validation project that reproduces the winner in independent libraries with independent paradigms (bar-level event-driven, bar-level vectorized, portfolio rebalance, analytics-only). If all libraries produce results within a tight tolerance band, the winner is scientifically validated. If any library refutes the result, Phase 4 paper trading is blocked until the cause is isolated.

Reproducibility across implementations is a standard check in quantitative finance. López de Prado `[advances_fin_ml, p.31-34]` recommends "same data, independent implementation" before "independent data, independent implementation" when replicating findings — this spec implements both stages.

---

## 2. Goals and non-goals

### Goals

1. **Validate (or refute)** Plano B V4 winner by independent reproduction.
2. **Surface hidden bugs** in our engine's signal, rebalance, or cost logic — by running paradigms that would have different bug surfaces.
3. **Produce an archival verdict document** (`reports/phase_3_5c/cross_lib/VERDICT.md`) that future contributors can read to understand what was tested, what passed, and what the tolerance bands were.
4. **Leave a minimal regression guard** (~5 pytest smoke tests) so future refactors of `letf_rotation.py` don't silently break reproducibility.
5. **Design interfaces so extension to Plano A is cheap** — shared `VariantConfig` shape, shared adapter contract, shared verdict engine. The Plano A project (Phase 3.5c-A) will reuse ~80% of this infrastructure.

### Non-goals

- This is **not** a new strategy search. We are not discovering new winners.
- This is **not** a pipeline migration. Our `letf_rotation.py` engine stays as-is.
- This does **not** re-run the 5 formal gates in each library. Gates stay pinned to our engine's numbers; we only cross-check metrics (CAGR / Sharpe / MaxDD / monthly ρ).
- This does **not** implement CFD/Plano A cross-validation now. Plano A gets its own follow-up spec (Phase 3.5c-A).
- No LLM SDK in runtime — all intelligence stays in Claude Code CLI as per CLAUDE.md convention.

---

## 3. Scope — 3 waves

Wave execution is sequential with gate between waves: if Wave 1 surfaces a REFUTES verdict, Waves 2 and 3 are **paused** pending investigation.

### Wave 1 — critical validation (must-have)

Reproduce the portfolio winner and each leg in isolation. Two windows × two stages:

| Variant | Window | Stage 1 (same-data) | Stage 2 (independent-data) |
|---------|--------|---------------------|----------------------------|
| `plano_b_v4_threshold_10` (flagship) | canonical 2004-2026 | yes | yes (post-2009 only) |
| `plano_b_v4_threshold_10` | extended 1986-2026 | yes | skip (pre-2009 has no real LETF) |
| `plano_b_v4_daily` (theoretical ceiling) | canonical | yes | yes (post-2009 only) |
| `leg_sso_only` (SPY EMA100 → SSO) | canonical + extended | yes | canonical post-2009 only |
| `leg_qld_only` (QQQ Donchian 20/10 → QLD) | canonical + extended | yes | canonical post-2009 only |
| `leg_ugl_only` (GLD Donchian 40/20 → UGL) | canonical + extended | yes | canonical post-2009 only |

Rationale: isolated legs surface bugs that portfolio aggregation can mask. If, for example, `bt` produces a match on the full portfolio but diverges on `leg_sso_only`, aggregation hid a signal bug.

### Wave 2 — decision validation (must-have if Wave 1 passes)

Reproduce variants we previously **rejected** and the fallback we kept. Confirms our decisions were correct under an independent implementation.

| Variant | Purpose |
|---------|---------|
| `v1_fallback` (SSO+QQQ+GLD mixed 1×/2×) | Pre-V4 conservative fallback, documented but not promoted |
| `2leg_ew` (SSO+QLD, no gold) | Rejected — DR 1.121 FAIL |
| `leverage_sweep_L2` | Pre-specified, passes |
| `leverage_sweep_L2_5` | Rejected — over-leveraged, MaxDD gate fails |
| `leverage_sweep_L3` | Rejected — real-ETF catalog limit |
| `threshold_sweep_5pp` | Considered — slightly better Sharpe but 2× DARFs |
| `threshold_sweep_10pp` | Chosen (= flagship, already in Wave 1) |
| `threshold_sweep_15pp` | Considered — lower Sharpe |
| `threshold_sweep_25pp` | Rejected — MaxDD degrades |

Only canonical window for Wave 2 to keep scope bounded. Stage 1 same-data only.

### Wave 3 — stretch (run only if Waves 1-2 clean)

Reproduce rebalance modes we considered:

| Variant | Purpose |
|---------|---------|
| `rebalance_mode_daily` (= `plano_b_v4_daily`, already in Wave 1) | — |
| `rebalance_mode_monthly_sell` | Alternative considered |
| `rebalance_mode_monthly_cashflow` | Alternative considered |
| `rebalance_mode_threshold_10` (= flagship) | — |

Wave 3 executes **only if** the cross-lib harness is already healthy (Waves 1-2 passed). Its incremental value is validating our rebalance engine implementation, which is somewhat indirect to the main question.

---

## 4. Library matrix

Five libraries (4 backtesters + 1 analytics). Rationale for each in brackets:

1. **`bt` (Philippe Morissette)** — explicitly designed for portfolio rebalancing strategies. Best architectural match for 3-leg EW. Uses pandas DataFrames, event-iterated monthly/threshold rebalance.

2. **`vectorbt`** — vectorized signal-based backtester. Fastest in class. Architecturally closest to our return-series simulator — if `vectorbt` diverges, the bug is likely in our signal math, not in rebalance timing.

3. **`backtrader`** — event-driven, per-bar. Most different paradigm — each bar is a discrete event with fill timing. Surfaces fill-timing bugs the other two wouldn't.

4. **`quantstats` / `pyfolio-reloaded`** — analytics-only. Doesn't run strategies. Consumes an equity curve or return series and recomputes CAGR / Sharpe / Sortino / MaxDD / VaR / rolling stats independently. Validates our **metric computation** layer separately from strategy execution.

5. **`testfol.io` (manual UI rerun)** — web UI. Already used to produce extended-window stress test. Rerun V4 canonical in its UI, export CSV, parse. Validates that our testfol.io extended-window numbers weren't a fluke.

### Why not zipline / QuantConnect / R

- `zipline-reloaded`: institutional-grade but heavier to integrate; marginal additional signal over `backtrader` + `bt` + `vectorbt`.
- QuantConnect LEAN: C# core, Python wrapper; environment friction too high for a 3-week project.
- R (`quantstrat`): cross-language independence is the strongest signal, but effort ~2× any Python lib. Deferred — if Waves 1-3 all pass cleanly, R validation can be added as Phase 3.5c-B follow-up. If they surface issues, we focus on fixing first.

---

## 5. Two-stage data isolation

### Stage 1 — same-data (isolate strategy logic)

All libraries consume the **same** input series our engine uses:

- **Tiingo daily OHLCV** for SPY, QQQ, GLD (canonical split/div-adjusted).
- **Synthetic LETF prices** for SSO/QLD/UGL pre-real-ETF inception, generated by compounding returns from `ai_trade.backtest.helpers.synthetic_letf.synthesize_letf_returns_ffr_aware` (formula `r = L × r_index - fee/252 - FFR_drag × L`).
- Output: `reference_prices.parquet` — OHLC bars where high = low = close = synthetic close for pre-real-ETF portion, and real OHLCV post-inception.

**Inception dates** (used to switch synthetic → real):
- SSO: 2006-06-21
- QLD: 2006-06-21
- UGL: 2008-12-03

**Stage 1 windows:** canonical (2004-10-01 → 2026-04-18) and extended (1986-01-02 → 2026-04-18).

**Purpose:** if a library diverges in Stage 1, the bug is in strategy logic (signal, rebalance, cost application) — not in data.

### Stage 2 — independent-data (stress pipeline)

Each library fetches from its own ecosystem:
- `bt`, `vectorbt`: `yfinance.download` for SPY/QQQ/GLD/SSO/QLD/UGL.
- `backtrader`: yfinance or quantopian-quandl bundle.
- `quantstats`: consumes equity curves from the above.
- `testfol.io`: its own data source (proprietary, already validated on extended window).

**Stage 2 window:** post-2009-01-01 only (all three real LETFs exist, no synthetic needed). Roughly 17 years.

**Purpose:** if Stage 1 passes but Stage 2 diverges, the bug is in our data pipeline (split adjustment, dividend handling, survivorship). That is a separate, independent finding.

**Citation:** two-stage isolation follows López de Prado `[advances_fin_ml, p.31-34]`.

---

## 6. Verdict tiers and tolerance bands

### Per-library tier (per variant × window × stage)

All Δs are absolute deltas vs baseline. All "pp" denotes percentage points (absolute, not relative). ρ denotes **Pearson correlation** on monthly log returns.

| Tier | Criteria (all must hold) |
|------|--------------------------|
| **CONFIRMS-STRONG** | \|ΔCAGR\| < 0.5pp AND \|ΔSharpe\| < 0.05 AND \|ΔMaxDD\| < 1pp AND ρ(monthly log returns) > 0.99 |
| **CONFIRMS** | \|ΔCAGR\| < 2pp AND \|ΔSharpe\| < 0.15 AND \|ΔMaxDD\| < 3pp AND ρ(monthly log returns) > 0.95 AND same sign on all 5 formal gates |
| **WARNING** | Outside CONFIRMS bands but all 5 gates still pass (Sharpe > 0, MaxDD < 25%, WF 6/8+, PBO < 0.5, DSR p < 0.05) |
| **REFUTES** | Any gate flips (Sharpe ≤ 0, MaxDD ≥ 25%, WF < 6/8, PBO ≥ 0.5, DSR p ≥ 0.05) |

### Operational outcomes (handled alongside tiers)

| Outcome | Meaning |
|---------|---------|
| `SKIPPED` | Library not installed / version mismatch / adapter disabled. Ignored in aggregate. |
| `DATA_UNAVAILABLE` | Ticker/period not available (e.g. QLD pre-2006 in Stage 2). Expected, not an error. |
| `ERROR` | Adapter crashed. Investigation required. |

### Aggregate verdict (per variant × window)

| Verdict | Rule |
|---------|------|
| **VALIDATED** | Stage 1: ≥2 libs `CONFIRMS-STRONG`. Stage 2: ≥3 libs `CONFIRMS`. Zero `REFUTES` in either stage. |
| **VALIDATED-WITH-CAVEATS** | Stage 1 meets bar, Stage 2 has 1-2 `WARNING` (pipeline-diff, not strategy bug). |
| **BLOCKED-INVESTIGATE** | Any `REFUTES`, or Stage 1 fails minimum (<2 `CONFIRMS-STRONG`). |
| **INCONCLUSIVE** | More than 2 libs `SKIPPED` or `DATA_UNAVAILABLE`. Not pass, not fail. |

### Citations for tolerance bands

- Tolerance magnitudes (Sharpe ±0.15, CAGR ±2pp) align with López de Prado `[advances_fin_ml, p.208-211]` materiality thresholds for OOS-replication divergence.
- Monthly-returns correlation ρ > 0.95 follows Bailey & López de Prado `[advances_fin_ml, p.273-275]` treatment of strategy similarity under backtest perturbation.
- Same-sign-on-gates criterion follows the 5-gate framework `[advances_fin_ml, p.208-211, p.273-275, p.298-299]` already applied in Phase 3.5b.

---

## 7. Components and interfaces

### Directory layout

```
reports/phase_3_5c/cross_lib/
├── data/
│   ├── reference_prices.py          # synthetic + real price assembler
│   ├── reference_prices.parquet     # generated artifact (gitignored, reproducible)
│   └── independent_fetchers/
│       ├── bt_fetcher.py
│       ├── vectorbt_fetcher.py
│       ├── backtrader_fetcher.py
│       └── ...
├── adapters/
│   ├── bt_adapter.py
│   ├── vectorbt_adapter.py
│   ├── backtrader_adapter.py
│   ├── quantstats_adapter.py
│   ├── testfolio_instructions.md    # manual UI recipe
│   └── testfolio_extract.py         # CSV parser from testfol.io export
├── variants.py                       # declarative registry
├── reference/
│   └── baseline.json                 # golden numbers pinned from our engine
├── verdict.py                        # tier + aggregate logic
├── run_wave.py                       # CLI orchestrator
├── report.py                         # generates VERDICT.md
├── results/
│   ├── stage_1/<lib>/<variant>/<window>/result.json
│   └── stage_2/<lib>/<variant>/<window>/result.json
├── errors/                           # populated only on ERROR outcomes
└── VERDICT.md                        # top-level output

tests/cross_lib/
├── test_data_layer.py                # ~5 tests
├── test_adapter_bt.py                # ~4 tests
├── test_adapter_vectorbt.py          # ~4 tests
├── test_adapter_backtrader.py        # ~4 tests
├── test_verdict.py                   # ~10 tests
└── test_harness_smoke.py             # ~5 tests (end-to-end, 1-year slice)
```

### Core types

```python
# variants.py
@dataclass(frozen=True)
class VariantConfig:
    variant_id: str
    family: Literal["plano_b", "plano_a"]               # extensibility hook
    execution_model: Literal[
        "letf_synthetic",                                # Plano B default, implemented
        "cfd_synthetic",                                 # Plano A future, stub raises NotImplementedError
        "real_etf",                                      # Stage 2
    ]
    legs: list[LegConfig]
    rebalance: RebalanceConfig
    target_weights: tuple[float, ...]
    windows: list[tuple[str, str]]

@dataclass(frozen=True)
class LegConfig:
    signal_type: Literal["ema_regime", "donchian"]
    signal_params: dict                                  # {"lookback": 100}, {"entry": 20, "exit": 10}
    signal_ticker: str                                   # SPY / QQQ / GLD
    execution_ticker: str                                # SSO / QLD / UGL

@dataclass(frozen=True)
class RebalanceConfig:
    mode: Literal["daily", "monthly_sell", "monthly_cashflow", "threshold"]
    threshold_pp: float | None                           # only for mode=threshold

# adapter contract
class Adapter(Protocol):
    name: str                                            # "bt", "vectorbt", ...
    def run(self, variant: VariantConfig, window: tuple[str, str], stage: int) -> RunResult: ...

@dataclass
class RunResult:
    variant_id: str
    lib: str
    window: tuple[str, str]
    stage: int
    equity_curve: pd.Series
    monthly_returns: pd.Series
    trade_dates: list[pd.Timestamp]
    cagr: float
    sharpe: float
    max_dd: float
    wf_splits_8: list[float]                             # WF Sharpe per split
    dsr_pval: float
    outcome: Literal["OK", "SKIPPED", "DATA_UNAVAILABLE", "ERROR"]
    error_detail: str | None
```

### Verdict engine

```python
# verdict.py
@dataclass(frozen=True)
class Tolerance:
    cagr_pp: float
    sharpe: float
    max_dd_pp: float
    monthly_rho: float

TOL_STRONG  = Tolerance(cagr_pp=0.5, sharpe=0.05, max_dd_pp=1.0, monthly_rho=0.99)
TOL_CONFIRM = Tolerance(cagr_pp=2.0, sharpe=0.15, max_dd_pp=3.0, monthly_rho=0.95)

def classify_tier(run: RunResult, baseline: Baseline) -> Tier: ...
def aggregate_verdict(tiers: dict[lib, Tier], stage: int) -> AggregateVerdict: ...
```

### Extensibility for Plano A

Every interface accepts `family: Literal["plano_b", "plano_a"]` and `execution_model`. Plano A adds:
- `execution_model="cfd_synthetic"` implemented in a future `cfd_cost.py` (analogous to `synthetic_letf.py`).
- New variants in `variants.py` using `family="plano_a"`.
- No changes to adapters' `run()` signatures, to verdict engine, or to runner/report.

Phase 3.5c-A (Plano A cross-lib validation) will be authored as a separate spec that adds the `cfd_synthetic` implementation and Plano A variants, reusing the rest.

---

## 8. Failure handling

### Adapter-level

| Failure | Outcome | Action |
|---------|---------|--------|
| `ImportError` on lib | `SKIPPED` | Logged, aggregation ignores |
| Missing ticker in Stage 2 | `DATA_UNAVAILABLE` | Logged, aggregation ignores |
| Any other exception | `ERROR` | Stacktrace → `errors/{lib}_{variant}.log`, aggregation marks `BLOCKED-INVESTIGATE` for that cell |

Zero silent failures. If an adapter cannot produce a valid `RunResult`, it must emit one of the three explicit outcomes above.

### Aggregate-level

`BLOCKED-INVESTIGATE` triggers:

1. **Freeze** — Phase 4 paper trading does not proceed until resolved.
2. **Forensic diff** — produce trade-by-trade comparison between our engine and the refuting lib. Identify first divergent trade date and first divergent signal evaluation date.
3. **Root cause classification:**
   - **Adapter bug** → fix adapter, re-run.
   - **Our engine bug** → this is a real scientific finding. Fix `letf_rotation.py` / `synthetic_letf.py`, re-run entire Phase 3.5b pipeline (full gate recomputation). Possibly a new or disqualified winner.
   - **Legitimate paradigm difference** (fill timing, rebalance granularity) → document as caveat in `VERDICT.md`, retain current winner.
4. **`jornada/` entry** — human-language explanation with citation to the offending lib + excerpt of divergent trade log.

---

## 9. Reporting

Three-layer output hierarchy:

### Top — `VERDICT.md`

- Executive summary: 1 paragraph, VALIDATED / VALIDATED-WITH-CAVEATS / BLOCKED / INCONCLUSIVE for the flagship variant.
- Aggregate matrix: rows = variants, columns = libs per stage, cells = tier.
- Per-variant 1-paragraph human summary with citation of relevant book page for the signal/rebalance logic.
- Links to per-variant deep-dive files and to error logs.

### Mid — `per_variant/<variant_id>.md`

- Full metric table: baseline vs each lib, with Δs highlighted.
- Equity curve comparison chart (PNG): our engine vs each lib, overlaid.
- Monthly-return correlation heat map if N libs ≥ 3.
- Trade-date divergence analysis (table of dates where any lib disagreed on entry/exit).

### Bottom — `errors/` and `results/`

- Raw `RunResult` JSON per run (machine-readable, for post-hoc queries).
- Stacktraces per `ERROR` outcome.

### Companion `jornada/` entry

Human-language narrative: "We reproduced Plano B V4 in 4 libraries. bt and vectorbt matched strongly; backtrader matched within event-driven noise; quantstats confirmed metric computation; testfol.io rerun agreed. Plano B V4 is VALIDATED. Phase 4 paper trading proceeds." Or the inverse if BLOCKED.

---

## 10. Testing

Four layers of pytest tests; total ~32 new tests; baseline 783 → ~815 (+4%).

### 10.1 Data layer — `tests/cross_lib/test_data_layer.py` (~5 tests)

- Parquet hash equals hash of the series our engine consumes.
- Canonical and extended windows align with `backtest/validation/splits.py`.
- Synthetic LETF invariant: `price[t]/price[t-1] ≈ L × r_index[t] - fee/252` within 1e-8.

### 10.2 Adapter units — `tests/cross_lib/test_adapter_<lib>.py` (~4 each × 3 libs)

Per adapter:
- `run()` returns `RunResult` with all required fields populated.
- Signal implementation matches reference at 5 deterministically-chosen dates (seed-fixed random sample).
- Rebalance triggers fire on the same dates (±1 day tolerance for fill timing).
- `SKIPPED` outcome is emitted when lib is force-uninstalled (monkeypatch).

### 10.3 Verdict engine — `tests/cross_lib/test_verdict.py` (~10 tests)

Table-driven fixtures:
- Baseline + near-match → `CONFIRMS-STRONG`.
- Baseline + within-CONFIRMS-band → `CONFIRMS`.
- Baseline + WARNING-band (gates still pass) → `WARNING`.
- Baseline + gate-flipping divergence → `REFUTES`.
- Identity check: baseline vs itself → `CONFIRMS-STRONG`.
- Aggregate: 3 CONFIRMS-STRONG → `VALIDATED`.
- Aggregate: 2 CONFIRMS-STRONG + 1 REFUTES → `BLOCKED-INVESTIGATE`.
- Aggregate: 3 SKIPPED → `INCONCLUSIVE`.

### 10.4 Smoke end-to-end — `tests/cross_lib/test_harness_smoke.py` (~5 tests)

Minimal slice: 1-year window (2020-01 → 2020-12), 2 libs (bt + vectorbt), 1 variant (`plano_b_v4_threshold_10`).
- Each lib's smoke run produces tier ≥ `CONFIRMS-STRONG` against baseline_slice.
- Harness completes in < 60s on reference hardware.

### Not tested (YAGNI)

- Stage 2 independent-data is not covered in CI (flaky due to external fetches). Runs only on-demand via `run_wave.py`.
- Wave 3 variants have no dedicated smoke test — smoke covers flagship only.
- `testfol.io` adapter has no smoke test (manual UI step).

---

## 11. Execution plan (waves → work items)

Decomposition for `writing-plans` to expand:

- **Milestone M0 — infra (1 wk):** data layer, variants registry, reference baseline generation, verdict engine, runner + report skeleton, smoke tests for verdict + data layer.
- **Milestone M1 — Wave 1 adapters (1 wk):** bt + vectorbt + backtrader + quantstats adapters. Signal logic pinned to reference. Adapter unit tests.
- **Milestone M2 — Wave 1 execution (2-3 days):** run Stage 1 + Stage 2 for all Wave 1 variants. Gate: if any `REFUTES`, stop and investigate.
- **Milestone M3 — Wave 2 (2-3 days):** reuse adapters, run Wave 2 variants. Stage 1 only.
- **Milestone M4 — testfol.io manual + extract (1 day):** run flagship in UI, export CSV, parse, compare.
- **Milestone M5 — Wave 3 stretch (2 days, conditional):** if M2-M4 clean, run rebalance mode variants.
- **Milestone M6 — VERDICT.md + jornada entry + commit (1 day):** final report, human narrative, commit + push.

Total: ~3 weeks; Wave 3 adds 2 days conditionally.

---

## 12. Open questions (resolved before writing-plans)

None outstanding. Clarifying questions covered during brainstorming:

- Scope: C with D as stretch, executed in waves. ✓
- Libs: Tier 1 core + analytics cross-check. ✓
- Data: two-stage (same-data → independent-data). ✓
- Tolerance: 4-tier with specified bands. ✓
- Repo integration: hybrid (scripts + smoke tests). ✓
- Plano A extensibility: strategy-agnostic interfaces, `cfd_synthetic` stub deferred. ✓

---

## 13. Citations

- `[advances_fin_ml, López de Prado, p.31-34]` — two-stage replication protocol.
- `[advances_fin_ml, p.208-211]` — materiality bands for CAGR / Sharpe divergence.
- `[advances_fin_ml, p.273-275]` — strategy similarity under perturbation.
- `[advances_fin_ml, p.275-278]` — drift-triggered rebalance rules (threshold).
- `[advances_fin_ml, p.298-299]` — 5-gate framework composition.
- `[leverage_for_the_long_run, Gayed 2016/2020, p.7, p.11, p.13, p.16, p.21]` — SMA regime filter, synthetic LETF formula, ETF cash-off allocation.
- `[trading_systems_methods, p.353]` — Donchian canonical breakout parameters.

---

## 14. Future work

- **Phase 3.5c-A:** Plano A cross-library validation. Reuses this harness with `cfd_synthetic` execution model. Separate spec, executed after Plano B paper trading Phase 4.
- **R cross-check (optional):** if this project's verdict is clean and appetite remains, add `quantstrat` adapter for cross-language independence. Low priority.
- **Live-vs-backtest cross-check:** once paper trading begins, compare paper results against the winner's expected equity curve on the same period. Separate from this project.
