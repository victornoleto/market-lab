# Spec — Strategy D: Swing-trade BR ranking-based (ciclo mensal, isenção R$20k)

Executable plan for **Strategy D**, the 3rd active slot proposed
2026-04-22 after 29/29 honest validations FAIL across Strategy A+B. Each
task has a checkbox and a **Conclusion** field that must be filled before
the corresponding commit.

**Plan doc:** `/home/victor/.claude/plans/zazzy-booping-oasis.md`
**Jornada entry:** `jornada/2026-04-22-1734-strategy-d-open.md`
**Mandate override (awaiting signature):**
`docs/mandate_overrides/2026-04-22-strategy-d-open.md`

---

## 🎯 Context (for a new session)

### What happened before

- **Phases 3.5f-3.8 (2026-04-21 → 2026-04-22):** 29 leads total validated
  under honest engine (6 V2 Plano A + 10 Phase 3.6 + 8 Phase 3.7-3 + 5
  Phase 3.8-1). **29/29 FAIL.** Engine clean, cross-lib concordance ≤ 3pp
  CAGR in 23/24 strategies. The edge hunted in Strategy A (Pepperstone CFD)
  and Strategy B (Inter LETF rotation, Gayed-anchored) does not exist under
  honest gates.
- **Mandate override requested (2026-04-22):** user chose to open a new
  3rd active slot — **Strategy D** — targeting Brazilian stocks with
  monthly rebalanced ranking, exploiting R$20k/month tax exemption
  (art. 3º II Lei 11.033/2004).

### Hypothesis tested by Strategy D

> A cross-sectional ranking strategy on IBrX-100 Brazilian stocks, with
> monthly rebalance and R$20k exemption-aware cost model, has at least one
> signal family (Clenow momentum, Magic Formula, multi-factor V+M+Q, or
> low-vol+mom hybrid) that passes the 13 honest gates (PBO < 0.5 + DSR
> p < 0.05 adjusted for grid multiplicity + WF ≥ 6/8 + bootstrap 99.9% CI
> lower > 0 + cross-lib ±3pp + single-block OOS + FWD stress + cost stress
> + tax stress + sector concentration + liquidity stress).

**Abort-early gate:** if Phase D-MVP (leads D1 + D4, OHLCV-only) yields no
config with PBO < 0.5 AND DSR p < 0.1, stop before D-ampliada, save effort
on Fundamentus scrape.

### Non-negotiable principles (inherited)

- **Rule #1** (CLAUDE.md): every rule/parameter/gate cites `[book.slug, p.X]`.
- **Rule #2**: at most 4 parameters per strategy. Grid varies ≤ 4.
- **Rule #3**: PBO > 0.5 → reject.
- **Rule #4**: DSR p-value < 0.05 mandatory, **N_trials = sum of all grid
  configs across all D leads** (Bonferroni-like deflator for full D slot).
- **Rule #5**: walk-forward ≥ 8 windows, ≥ 6 profitable, max DD ≤ 25%.
- **Rule #6**: survivorship disclaimer mandatory in every yfinance report.
- **Rule #7**: strict TDD — RED test before implementation.

### Reused infra (no changes)

- `src/ai_trade/backtest/engine/` — Portfolio, Execution, Runner
- `src/ai_trade/backtest/validation/` — CPCV, PBO, DSR, WF, bootstrap
- `src/ai_trade/backtest/metrics/` — Sharpe, CAGR, MDD, report writer
- `src/ai_trade/backtest/data/yfinance_source.py` — OHLCV for `.SA` tickers
- `src/ai_trade/backtest/strategies/base.py` — Strategy abstract

### What is new

- `src/ai_trade/backtest/data/br_tickers.py` — IBrX-100 list + BR calendar
- `src/ai_trade/backtest/data/fundamentus_source.py` — scrape snapshot + hist
- `src/ai_trade/backtest/data/oceans14_source.py` — Playwright fallback
- `src/ai_trade/backtest/costs/br_cost_model.py` — corretagem + spread + tax
- `src/ai_trade/backtest/strategies/ranking_br.py` — MonthlyRankingStrategy
- `src/ai_trade/backtest/strategies/d1_clenow_br.py` — Lead D1 (momentum)
- `src/ai_trade/backtest/strategies/d2_magic_formula_br.py` — Lead D2
- `src/ai_trade/backtest/strategies/d3_multifactor_br.py` — Lead D3
- `src/ai_trade/backtest/strategies/d4_lowvol_mom_br.py` — Lead D4
- `src/ai_trade/backtest/strategies/d_combos.py` — Leads D5-D8 (regime filter, ensemble)
- `scripts/phase_d_mvp/d1_clenow_grid.py`
- `scripts/phase_d_mvp/d4_lowvol_mom_grid.py`
- `scripts/phase_d_mvp/orchestrator.py`
- `scripts/phase_d_ampliada/` (D2, D3, D5-D8 grids)

---

## 📖 How to use this file

1. Read this entire file + plan `/home/victor/.claude/plans/zazzy-booping-oasis.md`
   + jornada entry `jornada/2026-04-22-1734-strategy-d-open.md`.
2. Find the next task with `[ ]`.
3. Implement per "What to do" + acceptance criteria.
4. **BEFORE COMMITTING**, edit this file:
   - `[ ]` → `[x]`.
   - Fill **Conclusion** (2-4 lines): summary, files touched, `N passed`
     from pytest, non-obvious findings, citations.
5. Include this edit in the same commit as the implementation.
6. Final commit (after all tasks `[x]`) updates `ROADMAP.md` + `README.md` +
   this §"Verdict" with the final verdict.

---

## 🔨 Tasks

### Phase D-0 — Governance & setup (non-code)

#### Task D-0.1 — Mandate override signed by user

- [ ] User reads `docs/mandate_overrides/2026-04-22-strategy-d-open.md`
  and responds "aprovado" (or requests changes).
- [ ] If approved: apply the literal changes proposed to
  `docs/investment-mandate.md` (§1, §2.2, §2.3, §7 + new §5) and
  `CLAUDE.md` summary block. Mark override doc as `Status: ✅ Signed
  YYYY-MM-DD HH:MM`.
- [ ] If rejected: mark override doc `Status: ❌ Rejected` + reason, abort
  Strategy D work, pivot to R1-R5 options from Phase 3.8-1 closure.

**Acceptance:** `docs/investment-mandate.md` §1 explicitly mentions
Strategy D; `CLAUDE.md` summary item 1 mentions "up to 3 strategies ativas"
with D listed; override doc signed and immutable.

**Conclusion:** [fill after signature]

---

### Phase D-1 — Data layer BR

#### Task D-1.1 — br_tickers.py (IBrX-100 list + calendar)

**What to do:**

- [ ] Create `src/ai_trade/backtest/data/br_tickers.py`:
  - Constant `IBRX100_TICKERS: list[str]` — hand-curated from B3 official
    IBrX-100 composition (as of 2026-04, ~100 tickers with `.SA` suffix).
    Source URL logged in comment; rebuild when composition changes.
  - Function `bovespa_calendar(start: date, end: date) → pd.DatetimeIndex`
    — returns BR trading days using `pandas_market_calendars` if
    available, else hard-coded federal holidays (Carnaval, Corpus Christi,
    Tiradentes, etc.).
  - Function `filter_liquid_tickers(ohlcv: dict[str, pd.DataFrame], as_of:
    date, lookback: int = 60, min_median_volume_brl: float = 5_000_000)
    → list[str]` — applies rolling liquidity filter (dynamic universe
    proxy, Task D-1.6).
- [ ] Unit tests `tests/backtest/data/test_br_tickers.py`:
  - `IBRX100_TICKERS` length between 95-105, all end in `.SA`.
  - `bovespa_calendar(2024-01-01, 2024-12-31)` excludes 2024-02-12/13
    (Carnaval), 2024-05-30 (Corpus Christi).
  - `filter_liquid_tickers` correctly excludes ticker with median volume
    below threshold.

**Acceptance:** `pytest tests/backtest/data/test_br_tickers.py -v` passes;
no linter warnings; `python -c "from ai_trade.backtest.data.br_tickers
import IBRX100_TICKERS; print(len(IBRX100_TICKERS))"` prints ~100.

**Conclusion:** [fill after implementation]

---

#### Task D-1.2 — yfinance .SA smoke test

**What to do:**

- [ ] Write `tests/backtest/data/test_yfinance_br_smoke.py`:
  - Mark with `@pytest.mark.network` (skipped in CI by default, run
    locally).
  - Fetch PETR4.SA, VALE3.SA, ITUB4.SA from 2020-01-01 to 2026-04-01.
  - Assert canonical schema (`open, high, low, close, adj_close, volume`).
  - Assert ≥ 1000 rows (BR trading days ~250/yr × 6 yrs).
  - Assert timezone-naive DatetimeIndex named `date`.
- [ ] Verify cache works: run twice, second run does not hit network
  (mock `yfinance.download` to raise if called after first fetch).
- [ ] Document in comment: yfinance `.SA` does NOT handle delisted tickers
  (survivorship bias). Mitigation: limit universe to IBrX-100 current
  proxy.

**Acceptance:** `pytest tests/backtest/data/test_yfinance_br_smoke.py -v
-m network` passes locally; CI skips.

**Conclusion:** [fill after implementation]

---

#### Task D-1.3 — Fundamentus source (snapshot + historical)

**What to do:**

- [ ] Create `src/ai_trade/backtest/data/fundamentus_source.py`:
  - Class `FundamentusSource` with `cache_dir` field (default
    `data/fundamentus/`).
  - `fetch_snapshot(ticker: str) → dict[str, float]` — GET
    `https://www.fundamentus.com.br/detalhes.php?papel={TICKER}` with
    User-Agent "Mozilla/5.0 ...", parse HTML with `bs4`, extract P/L,
    P/VP, ROIC, ROE, Div Yield, Margem Líquida, Dívida Bruta/PL, Liq
    Corrente. Return dict keyed by canonical English names.
  - `fetch_historical(ticker: str) → pd.DataFrame` — scrape the
    quarterly financial history tables (page sections for
    "Demonstrativos de Resultados" and "Balanço Patrimonial") to build a
    time-indexed DataFrame with {revenue, ebit, net_income, equity,
    total_assets, debt} per quarter. Derive ROIC(t), ROE(t),
    Earnings_Yield(t) via helper.
  - Rate-limit: `time.sleep(1.1)` between requests, exponential backoff
    (1, 2, 4, 8, 16s) on 429.
  - Cache: write parquet per ticker `<cache_dir>/<TICKER>_snapshot.parquet`
    and `_historical.parquet` with `fetched_at` column.
- [ ] Unit tests `tests/backtest/data/test_fundamentus_source.py`:
  - Mock `requests.get` with fixture HTML (`tests/fixtures/fundamentus_petr4.html`).
  - Verify snapshot parsing for PETR4 returns ROIC ≈ 17.4, ROE ≈ 26.5,
    P/L ≈ 5.50 (match real page as of 2026-04).
  - Test rate-limit obeyed (call `fetch_snapshot` twice, measure elapsed
    with `freezegun`).

**Acceptance:** `pytest tests/backtest/data/test_fundamentus_source.py -v`
passes; schema matches scrape; 1-req/s rate limit respected.

**Conclusion:** [fill after implementation]

---

#### Task D-1.4 — Oceans14 Playwright fallback (only if Fundamentus blocks)

**What to do:**

- [ ] **Conditional:** only implement if D-1.3 scrape massive (80+ tickers)
  is blocked by Cloudflare / rate-limit. Decision gate after D-1.3 first
  batch run.
- [ ] Create `src/ai_trade/backtest/data/oceans14_source.py`:
  - Class `Oceans14Source` with Playwright-managed session.
  - `_bootstrap_session() → tuple[cookies, jwt_token]` — opens
    `https://www.oceans14.com.br/acoes/petrobras/petr4`, waits for XHR,
    extracts cookies `ASP.NET_SessionId`, `uid` and the JWT from the
    XHR query string `?token=...`.
  - `fetch_historical(ticker: str) → pd.DataFrame` — reuses the cached
    session to call `https://www.oceans14.com.br/rendaVariavel/acoes/
    respostaAjax/gHistoricoCotacao.aspx?papel={ticker}&periodo=5a&token=
    {jwt}` with all the headers user provided; refresh session on 401.
- [ ] Unit tests `tests/backtest/data/test_oceans14_source.py` with
  requests-mock for the AJAX endpoint.
- [ ] Document in `README.md` §"Data sources": scraping third-party, fragile.

**Acceptance:** if triggered, Oceans14 scrape retrieves at least 1 yr of
OHLCV for PETR4; automated session refresh works across JWT expiry.

**Conclusion:** [fill after decision gate]

---

#### Task D-1.5 — br_cost_model.py (corretagem + spread + tax R$20k isento)

**What to do:**

- [ ] Create `src/ai_trade/backtest/costs/br_cost_model.py`:
  - `@dataclass BRCostConfig`: `corretagem_per_side: float = 0.0`,
    `emolumentos_pct: float = 0.00025` (B3 0.025%),
    `spread_bps_top30: float = 15.0`, `spread_bps_smalls: float = 50.0`,
    `top30_tickers: frozenset[str]` (hard-coded top 30 IBrX-100 by
    market cap 2026-04).
  - `transaction_cost(ticker: str, volume_brl: float, side: str) →
    float` — corretagem + emolumentos + spread (half the bid-ask).
  - `@dataclass TaxConfig`: `monthly_exemption_brl: float = 20_000.0`,
    `swing_rate: float = 0.15`.
  - `monthly_tax(month_sells: list[tuple[date, float]], month_pnl_brl:
    float) → float`:
    ```python
    gross_sales = sum(amount for (_, amount) in month_sells)
    if gross_sales <= 20_000.0:
        return 0.0
    return max(0.0, month_pnl_brl) * 0.15
    ```
    Apply on equity curve at month-end.
- [ ] Unit tests `tests/backtest/costs/test_br_cost_model.py`:
  - Cost top30 ticker at R$100k volume: corretagem 0 + emol 25 + spread
    75 (half of 15 bps) = R$100.
  - Tax with R$18k sales, R$5k pnl → 0.
  - Tax with R$25k sales, R$5k pnl → R$750 (15% × R$5k).
  - Tax with R$25k sales, -R$1k pnl → 0 (no tax on loss).
  - Tax with R$25k sales, R$0 pnl → 0.

**Acceptance:** `pytest tests/backtest/costs/test_br_cost_model.py -v`
passes all 5+ cases; integrates with `BacktestEngine` via `cost_fn` hook.

**Conclusion:** [fill after implementation]

---

#### Task D-1.6 — Dynamic universe proxy (volume-based IBrX-100)

**What to do:**

- [ ] Extend `src/ai_trade/backtest/data/br_tickers.py` with:
  - `get_universe_on(as_of: date, ohlcv_all: dict[str, pd.DataFrame],
    n: int = 100, lookback: int = 60, min_vol_brl: float = 5_000_000)
    → list[str]` — returns the top N tickers from `IBRX100_TICKERS` whose
    median (close × volume) over `[as_of - lookback, as_of]` exceeds
    `min_vol_brl`. Documents as "IBrX-100 proxy, not exact B3 composition".
- [ ] Unit tests: with synthetic OHLCV, verify:
  - Ticker with zero volume excluded.
  - Ticker with exactly min_vol_brl included.
  - Top N ordering by median value correct.

**Acceptance:** `pytest tests/backtest/data/test_br_tickers.py::test_universe_on
-v` passes; function used by D-MVP strategies.

**Conclusion:** [fill after implementation]

---

### Phase D-MVP — OHLCV-only leads (D1 + D4)

#### Task D-MVP.1 — MonthlyRankingStrategy base class

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/ranking_br.py`:
  - Class `MonthlyRankingStrategy(Strategy)` — base for D1/D2/D3/D4.
  - Constructor: `n_top: int`, `sector_cap_pct: float | None`,
    `position_inertia_pct: float = 0.10` (Carver
    `[systematic_trading, p.174]`).
  - Abstract method `compute_scores(universe: list[str], as_of: date,
    ohlcv: dict, fundamentals: dict | None) → dict[str, float]`.
  - Concrete method `rebalance(as_of: date, ...)`:
    1. Get `universe = get_universe_on(as_of, ...)`.
    2. Call `compute_scores(universe, ...)`.
    3. Rank descending, take top `n_top`.
    4. Apply `sector_cap_pct` if set (GICS sector mapping from
       hard-coded `SECTOR_MAP` in `br_tickers.py`).
    5. Equal-weight within cesta (ATR-sizing in D1/D4 variants).
    6. Apply position inertia: hold current positions that are still in
       top `n_top × 1.1`; swap only the ones that fell out.
- [ ] Unit tests `tests/backtest/strategies/test_ranking_br.py`:
  - Synthetic scores → top N correctly selected.
  - Sector cap enforced.
  - Position inertia: ticker ranked N+1 is still held from last month.

**Acceptance:** `pytest tests/backtest/strategies/test_ranking_br.py -v`
passes; class reusable by all D leads.

**Conclusion:** [fill after implementation]

---

#### Task D-MVP.2 — Lead D1 Clenow momentum (grid 24 configs)

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/d1_clenow_br.py`:
  - Class `D1ClenowBR(MonthlyRankingStrategy)`.
  - `compute_scores()`:
    - For each ticker, compute **Adjusted Slope** =
      `annualized_slope(log_price, lookback_d) × R²`
      `[stocks_on_the_move, p.76-77]`.
    - Filter: drop if `close < SMA(close, 100)`
      `[stocks_on_the_move, p.81-82]`.
    - Filter: drop if `max_abs_gap_in_window > 0.15`
      `[stocks_on_the_move, p.82]`.
    - Return dict {ticker: Adjusted_Slope}.
  - ATR-based position sizing: `shares = (capital × 0.001) / ATR(20)`
    `[stocks_on_the_move, p.88]`, then normalize to N top cap.
- [ ] Create `scripts/phase_d_mvp/d1_clenow_grid.py`:
  - Grid: `lookback ∈ {90, 180}`, `n_top ∈ {15, 20, 25, 30}`,
    `sector_cap_pct ∈ {0.20, 0.25, 0.30}`. **24 configs.**
  - IS: 2010-01 → 2019-12 (10 yrs). OOS: 2020-01 → 2023-12 (4 yrs).
    FWD Stress: 2024-01 → 2026-04 (2.3 yrs). Windows driven by
    yfinance `.SA` data availability per ticker.
  - Write per-config report in `reports/phase_d_mvp/d1_<cfg>/`.
- [ ] Unit tests `tests/backtest/strategies/test_d1_clenow_br.py`:
  - Adjusted_Slope ≥ 0 for monotonic up series.
  - SMA filter rejects stock below SMA 100.
  - Gap filter rejects 16% gap, accepts 14% gap.

**Acceptance:** `pytest tests/backtest/strategies/test_d1_clenow_br.py -v`
passes; `python scripts/phase_d_mvp/d1_clenow_grid.py --config 0 --quick`
produces equity curve + Sharpe + CAGR in
`reports/phase_d_mvp/d1_90d_20_25pct/`.

**Conclusion:** [fill after implementation]

---

#### Task D-MVP.3 — Lead D4 Low-vol + Momentum hybrid (grid 18 configs)

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/d4_lowvol_mom_br.py`:
  - `compute_scores()`:
    - Step 1: compute Adjusted Slope 180d (same as D1), keep top `pre_n`
      (grid param {30, 40, 50}).
    - Step 2: re-rank the `pre_n` by **realized vol** over `vol_lookback`
      (grid param {60, 90}) ascending (lowest vol wins).
    - Return dict of top `n_top` (grid param {15, 20, 25}).
    - Total grid: 3 × 2 × 3 = **18 configs.**
- [ ] Create `scripts/phase_d_mvp/d4_lowvol_mom_grid.py` following same
  pattern as D1 grid script.
- [ ] Unit tests `tests/backtest/strategies/test_d4_lowvol_mom_br.py`.

**Acceptance:** similar to D-MVP.2.

**Conclusion:** [fill after implementation]

---

#### Task D-MVP.4 — MVP Orchestrator + reports

**What to do:**

- [ ] Create `scripts/phase_d_mvp/orchestrator.py`:
  - Runs D1 grid (24 cfg) + D4 grid (18 cfg) = 42 configs total.
  - For each config: compute PBO, DSR (with N_trials = 42 initially;
    revised after D-ampliada to 42 + D2+D3+combos), WF, bootstrap, cost
    stress, tax stress, all 13 gates.
  - Aggregates to `reports/phase_d_mvp/SUMMARY.md` with gate-pass matrix.
  - Flags **early-abort** if zero configs satisfy `PBO < 0.5 AND
    DSR_p < 0.1`.
- [ ] Integration test `tests/phase_d_mvp/test_orchestrator.py` with
  synthetic data (3 tickers, 300 bars) verifying end-to-end pipeline
  runs without error.

**Acceptance:** `python scripts/phase_d_mvp/orchestrator.py --dry-run`
prints execution plan; full run produces SUMMARY.md.

**Conclusion:** [fill after implementation]

---

#### Task D-MVP.5 — Early-abort decision gate

**What to do:**

- [ ] Read `reports/phase_d_mvp/SUMMARY.md`. Three possible outcomes:
  1. **No config passes PBO < 0.5 AND DSR_p < 0.1** → stop. Document in
     `jornada/YYYY-MM-DD-HHmm-strategy-d-mvp-abort.md`, mark this task
     and all D-ampliada tasks as DELETED. Escalate to user for pivot
     (R1-R5 Phase 3.8-1 style).
  2. **At least 1 config passes both** → proceed to D-ampliada.
  3. **All configs pass (unlikely)** → flag for investigation (engine
     bug likely; compare cross-lib before proceeding).
- [ ] Register decision in `jornada/`.

**Acceptance:** decision recorded; downstream tasks updated.

**Conclusion:** [fill after decision]

---

### Phase D-ampliada — Fundamentals-based leads (D2 + D3 + combos)

*Only execute after D-MVP.5 outcome #2.*

#### Task D-amp.1 — Lead D2 Magic Formula (grid 4 configs)

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/d2_magic_formula_br.py`:
  - `compute_scores()` uses fundamentals from `FundamentusSource`:
    - Compute ROIC(t-quarter) and Earnings_Yield(t-quarter) = EBIT /
      Enterprise_Value.
    - Rank each ascending, sum: `score = rank(ROIC) + rank(EY)` (lower
      is better) `[quant_trading_chan, ch.1, p.7]`.
  - Caveat: monthly rebal atypical (original Magic Formula is annual).
    Document in spec.
- [ ] Grid: `n_top ∈ {15, 20, 25, 30}` (4 configs).
- [ ] Script + tests.

**Acceptance:** similar pattern.

**Conclusion:** [fill after implementation]

---

#### Task D-amp.2 — Lead D3 Multi-factor V+M+Q (grid 8 configs)

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/d3_multifactor_br.py`:
  - `compute_scores()`: `rank(Adjusted_Slope_180d) + rank(1/PB) + rank(ROE)`
    equal-weighted `[quant_trading_chan, ch.1, p.7]`.
  - Alt weighting: 50% mom, 25% value, 25% quality.
  - Grid: `n_top ∈ {15, 20, 25, 30}` × `weighting ∈ {equal, mom_heavy}` = 8.
- [ ] Script + tests.

**Conclusion:** [fill after implementation]

---

#### Task D-amp.3 — Leads D5-D8 combos

**What to do:**

- [ ] Create `src/ai_trade/backtest/strategies/d_combos.py`:
  - D5 = D1 + IBOV SMA(200) regime filter (long when IBOV > SMA, cash off).
  - D6 = D3 + IBOV SMA(200) regime filter.
  - D7 = equal-weight ensemble of top-N from D1 ∩ D4 ∩ D3 intersection.
  - D8 = rotation D1/D3/D4 based on realized vol of IBOV (low vol → D1,
    mid → D3, high → D4).
- [ ] Grid estimated: D5 (4), D6 (4), D7 (2 variants), D8 (4 thresholds) = 14.
- [ ] Script + tests per variant.

**Conclusion:** [fill after implementation]

---

### Phase D-gate — Final validation

#### Task D-gate.1 — Cross-lib validation of top-3 configs

**What to do:**

- [ ] Pick top 3 configs (ranked by OOS Sharpe) across all leads D1-D8.
- [ ] Run each in:
  - Our `BacktestEngine` (canonical).
  - `vectorbt` (parallel, numpy-backed).
  - `backtrader` (event-driven).
- [ ] Assert CAGR delta ≤ 3pp across all 3 libs (gate #7). If any lib
  differs > 3pp, investigate engine bug (Phase 3.5f style).
- [ ] Document in `reports/phase_d_gate/cross_lib/<config>.md`.

**Acceptance:** cross-lib concordance < 3pp for the top 3 configs, else
engine audit required.

**Conclusion:** [fill after runs]

---

#### Task D-gate.2 — Bootstrap 99.9% CI + DSR deflator final

**What to do:**

- [ ] For each top-3 config:
  - Stationary block bootstrap (block size optimized per Politis-White
    `[advances_fin_ml, p.273-275]`) with 10k resamples.
  - Sharpe distribution 99.9% CI lower bound > 0 (gate #6).
- [ ] DSR with `N_trials = total grid count = 42 (MVP) + 4 + 8 + 14 = 68`.
  Gate #2: `p_DSR < 0.05`.
- [ ] Document in `reports/phase_d_gate/bootstrap/<config>.md`.

**Conclusion:** [fill after runs]

---

#### Task D-gate.3 — Cost + Tax + Liquidity stress

**What to do:**

- [ ] Apply 2× cost model and verify top-3 configs still hit tier Válido.
- [ ] Apply 15% DARF always (capital-large scenario) — verify tier ≥ Marginal.
- [ ] Apply linear slippage 10 bps/turnover — verify tier Válido still.
- [ ] Apply sector concentration stress: cap at 20% max per sector — verify
  Sharpe does not collapse.
- [ ] Document in `reports/phase_d_gate/stress/<config>.md`.

**Conclusion:** [fill after runs]

---

#### Task D-gate.4 — Final Winner / Breadth-No-Winner verdict

**What to do:**

- [ ] If at least 1 config passes **all 13 gates**:
  - Mark as **Winner D** in `reports/phase_d_gate/WINNER.md`.
  - Proceed to D-promotion.
- [ ] If zero configs pass all 13:
  - Write `reports/phase_d_gate/BREADTH_NO_WINNER_D.md` with table
    showing all failures, root cause per family, recommendations (similar
    to Phase 3.6/3.7-3/3.8-1).
  - Escalate to user: does Strategy D close like A and B did, or is
    there a revision path (different universe, different rebalance
    cadence, different cost model assumption)?

**Conclusion:** [fill after final verdict]

---

### Phase D-promotion — Broker BR + paper-trade (only if Winner D)

#### Task D-prom.1 — Broker BR selection

**What to do:**

- [ ] Compare: XP Investimentos / Clear / Rico / Inter DTVM / BTG Pactual /
  Nubank Invest.
- [ ] Criteria: zero corretagem (or lowest), API/OFX for execution,
  emolumentos B3 transparent, custody safety (Tier rating), extrato
  export for tax ledger.
- [ ] User opens account manually (non-technical prerequisite).
- [ ] Document choice in `docs/brokers/br_broker_choice.md`.

**Conclusion:** [fill after choice]

---

#### Task D-prom.2 — Paper-trade plan

**What to do:**

- [ ] Draft 3-month paper-trade plan: sizes, monitoring dashboard, sanity
  ledger for R$20k tax threshold tracking, stop criteria (if live OOS
  Sharpe drops > 0.5 below backtest, pause and investigate).
- [ ] Document in `docs/plans/2026-MM-strategy-d-paper-trade.md`.
- [ ] Update `ROADMAP.md` with Phase D-live schedule.

**Conclusion:** [fill after draft]

---

## 🏁 Verdict (fill after all tasks complete)

**Status:** [PENDING / WINNER D / BREADTH_NO_WINNER_D]

**Final winner config:** [config name or N/A]

**Files touched (total):** [count]

**Tests (start → end):** 908 → [N]

**Non-obvious findings:**
- [finding 1 with citation]
- [finding 2]

**Next step:**
- [D-promotion / pivot decision / close Strategy D]
