# Roadmap — ai-trade

> Map of the project's next steps. Read this when resuming a session to know where you stopped and where to go.

---

## 📍 Current status (2026-04-15)

- ✅ **Phase 0 — Knowledge Base.** 33/33 books absorbed and validated (pipeline `books/raw/*.pdf` → `extracted/` → `summaries/<slug>.md`, autonomous 3-layer validation replacing human review). Global `check_citations.py`: 33/33 PASS. Quality: 🌟 12 Perfect · ✅ 20 Good · ⚠️ 1 Border, 0 real hallucinations.
- ✅ **Phase 0.5 — `knowledge/SKILL.md`.** `build_skill.py` aggregates the 33 summaries into a thematic Claude Skill (`knowledge/SKILL.md` + `books/`, `strategies/`, `indicators/`, `validation/`). Skill loadable via the `Skill` tool, inviolable rules #1-7 in production.
- 🔄 **Phase 1 — Pepperstone/cTrader infra.** Scaffold ready (docker-compose with Postgres 5435 + Grafana; `ctrader_oauth_bootstrap.py`; schemas). Blocked awaiting Spotware approval of the OAuth app.
- ✅ **Phase 2 — Backtest Module** (scope rewritten — see preamble below). Delivered 2026-04-14 via `specs/backtest_phase2.md`: data layer (yfinance + Wikipedia SPX point-in-time), engine (portfolio + CFD-aware execution + runner), validation framework (CPCV / PBO / DSR / walk-forward / MCPT), metrics + report (mandatory survivorship disclaimer), Clenow `stocks_on_the_move` replicated end-to-end. **173 tests passing**.
- 🔄 **Phase 2.5/3 — Run 1 (Clenow grid, 2026-04-14).** New `backtest/grid/` module + `scripts/run_grid_clenow.py` CLI ran 30 Clenow configs over 2015-2023 SPX point-in-time (410 tickers after 19% residual survivorship). **Gates fail:** PBO=0.524 (limit 0.5), DSR 0/30 p<0.05, walk-forward 4/30. Best config: `#15` (lookback=90, top=20%, risk=0.2%) with Sharpe 0.58, CAGR 8.87%, DD 19.86%, but underperforms SPY buy-and-hold and does not pass DSR. Bug fix along the way: `_sell_orders` for tickers delisted mid-backtest (regression test added). **235/235 tests green**. Details: `specs/backtest_phase2.md` §"Phase 2.5/3 — Run 1".
- 🔄 **Phase 2.5 — Run 2 (Ehlers Band-Pass Swing grid, 2026-04-14).** Pivot to a 2nd DSP-based strategy. New Ehlers primitives (SuperSmoother, HP, Roofing, Homodyne DCP, Band-pass) in `backtest/indicators/`. New `EhlersBPSwingStrategy` (anticipatory ±0.7 thresholds over AGC-normalised BPF). GridRunner generalised to `TypeVar ConfigT` — Clenow and Ehlers share the runner. Grid of 24 configs (hp_period × lp_period × pct_of_dcp × stop_pct = 2×2×3×2) over ^GSPC 2015-2023 (~3s wallclock n_jobs=4). **Mixed verdict:** PBO=0.468 **passes** (Ehlers is structurally less overfit than Clenow), DSR 0/24 reject, WF 2/24 pass. Best #6 Sharpe 0.31 CAGR 2.17% DD 14.65%. **Cross-correlation Clenow × Ehlers best equity curves = −0.0108** — orthogonal strategies → regime-aware portfolio is a candidate. **55 new tests (290/290 green).** Details: `specs/backtest_phase2_5_ehlers.md` §"Run — results and fork".
- ✅ **Phase 2.5 — Run 3 (Tiingo survivorship-free ablation, 2026-04-15).** Bulk 1660 tickers delivered (backup `data/tiingo_backup_20260415-0958.tar.gz`, 145.7 MB). Three concrete hypotheses tested on the same gate framework:
  - **Ehlers BP Swing, SPY 2015-2023, post-fix:** PBO=0.496 pass, DSR 0/24 reject (best p=0.332, from 0.852), WF 7/24 pass (from 2/24), best Sharpe 0.806 (from 0.310 yfinance Run 2). Verdict: FAIL (DSR only) — edge real but small vs N=24 trials.
  - **Ehlers multi-asset 2005-2023, post-fix:** 0/N PASS. Longer window kills WF across all ETFs (2008/2011/2015/2020 regime collision). Crypto barely clears WF intermittently. See `reports/ehlers_multi_asset_summary.md`.
  - **Clenow momentum, Tiingo SPX 506 tickers 2015-2023, post-fix:** PBO=0.603 fail (worsened vs 0.524), DSR 0/30 reject, WF 9/30 pass (from 4/30), best Sharpe 0.618 (from 0.583). Survivorship-honest universe is stricter than yfinance's filtered one. Verdict: FAIL (PBO + DSR).
  - **Code-level bugs fixed along the way:** (i) both strategies read raw `close` instead of `adj_close` — splits triggered Clenow's 15% gap filter and dividends spiked Ehlers' oscillator; new `adjust_ohlc` utility rebases OHLC to the total-return base (commit `5ca9410`). (ii) `TiingoSource._http_fetch` now returns an empty frame on 404 instead of crashing long universe fetches (commit `75f80de`). (iii) Tiingo bulk default `--start 1990-01-01` to capture widest history per ticker (commit `e0c95f1`). **351 tests green (+64 net vs Run 2 baseline 290).**

- 🔄 **Phase 2.5 — Run 4 Step 2 (F3.D Portfolio Clenow+Ehlers, 2026-04-15) — FAIL v1.** v1 on SPY 2015-2023 (daily bars): PBO 0.849 ❌ (diversification uniformity paradox), DSR 0/9 reject (best p=0.190), **walk-forward 9/9 pass** ✅ (huge gain — Clenow regime filter subsidizes Ehlers DD in crises). Best Sharpe 0.804, CAGR 10.84%, DD 18.02%. v2 SKIPPED per go/no-go. Commits `872a9cf`/`c99bca3`/`36c0f57`/`ac00d6e`. Diagnostic: `reports/grid_portfolio_20260415-1541/diagnostic.md`. Spec+plan under `docs/superpowers/{specs,plans}/2026-04-15-f3d-portfolio-clenow-ehlers*.md`.

  Sub-result to keep: diversification solves the WF gate (9/9 from Ehlers 7/24 / Clenow 9/30). The `src/ai_trade/backtest/portfolio/` package is timeframe-agnostic — reusable for any future combination.

- ✅ **2026-04-15 (noite, pós-pivô) — `tiingo_service` lazy-cache ENTREGUE.** Refactor in place de `TiingoSource`/`TiingoStorage` com eixo `frequency`; migração de 1675 tickers daily para `data/tiingo/daily/` (backup preservado em `data/tiingo_premigrate_20260415-181358.tar.gz`, 149 MB); roteamento IEX 1h + split adjust via daily cache (reusa pattern de `adjust.py`); whitelist `{daily, 1hour}` × `{equity, etf, crypto, forex}`. Smoke #1 retention PASS (SPY 5a, btcusd 208d, eurusd 416d; threshold ≥ 6m). 377 → **405 testes verdes**. Spec v3.1 em `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` (2 rodadas `/judge-spec` + 1 smoke antes do impl). Plan em `docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md`. 3 commits: storage+migrate · source+adjust · smoke+docs.

- ⚠️ **2026-04-15 (noite) — PIVOT: intraday short-hold + `tiingo_service` lazy-cache.** All five Phase 2.5 cycles above ran on **daily bars**, with actual trade durations (from the F3.D run's persisted trades): Clenow median **56-63 days** (max 378), Ehlers BP Swing median 1-22 days but with outlier positions held up to 4 years. This is fundamentally incompatible with the project's real goal — **short, punctual CFD trades on Pepperstone**. Even while swap is ignored in the backtest for now, strategy *selection* must respect "short and punctual" going forward, otherwise we're optimizing the wrong thing. Two decisions:

  1. **`tiingo_service` lazy-cache** replaces the eager bulk download as primary data path. Each API call memoized by `(endpoint, params)` hash: cache-hit returns immediately, cache-miss fetches + persists + returns. Unlocks intraday endpoints (Tiingo IEX 1min/5m/1h) without needing a pre-bulk. Existing `TiingoStorage`/`manifest.json` becomes a special case of this layer, not the primary protocol.
  2. **Strategy catalog re-prioritized** around short-hold intraday. Clenow leaves the production path (keeps its role as "engine exerciser" in the historical record). Incoming: Chan mean-reversion / cointegration pairs `[algo_trading_chan]`, Ehlers BP Swing on 1h bars (same logic, new timeframe), volatility breakouts `[volatility_trading, Sinclair]`. **AFML sophisticated** — previously promoted as "path B" — is DEFERRED: it re-enters later as a secondary filter over an intraday strategy that shows edge.

- 🔄 **Phase 2.5 — Run 4 Step 1 (AFML meta-labeling simple, 2026-04-15) — FAIL.** See JORNADA.md changelog.
- ✅ **Phase 2.5 — Run 4 Step 1 prep (long-history Ehlers, 2026-04-15) — FAIL** (mixed signals). See JORNADA.md changelog.

- ⏳ **Next steps (in order, post-pivot):**
    1. ✅ **`tiingo_service` lazy-cache** — DELIVERED 2026-04-15 (noite). See entry above.
    2. **Intraday strategy catalog — 1h first** (sweet spot between noise and frequency). Chan mean-reversion pairs is the strongest fit `[algo_trading_chan]`; Ehlers BP Swing ported to 1h (recalibrate thresholds); Sinclair-style volatility breakouts `[volatility_trading]`. Each strategy gets the same anti-overfit gate battery (CPCV/PBO/DSR/WF). Expand to 15m / 5m only after 1h gives useful signal.
    3. **AFML sophisticated** — re-enters here, as a meta-label layer over whichever intraday strategy shows edge in (2). Same plan as the deferred path: walk-forward CV with purge/embargo `[advances_fin_ml, ch.7]`, rich features, asymmetric triple-barrier.
    4. **Carver multi-asset trend / other multi-day families** — only if nothing intraday delivers. These don't fit the short-hold goal either, so they're effectively a last-resort pivot.
    5. **Cancel Tiingo subscription** — pushed out until `tiingo_service` is verified working against live endpoints (can't evaluate without fresh intraday data).

  Diagnostics still relevant: `reports/grid_portfolio_20260415-1541/diagnostic.md` (F3.D v1), `reports/grid_ehlers_spy_postfix_20260415-0958/diagnostic.md`, `reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md`, `reports/grid_ehlers_20260415-1353/diagnostic.md`.

---

## 🛤️ Phases — detail

### Phase 1 — Pepperstone/cTrader infrastructure + data (24/7 Ubuntu VPS)

**Decision:** broker = **Pepperstone**; platform = **cTrader**; API = **cTrader Open API** (Protobuf over TCP with OAuth2, official Spotware Python SDK `ctrader_open_api`). Alpaca, OANDA, IBKR and XM/MT5 discarded — see `/home/victor/.claude/plans/delightful-bubbling-crab.md` for the full rationale. Demo and live use the same protocol; only the endpoint changes.

**Stack:**
- Ubuntu VPS (2 vCPU / 4 GB RAM, Frankfurt or London for latency to Spotware servers in Europe). Options: Hetzner CX22, Contabo VPS S.
- `docker-compose` with 3 services (zero Wine, zero VNC):
  - `app` — Python 3.12 with `ctrader_open_api` (Twisted-based). Hosts strategies, scheduler, logging, the cTrader Open API client, Universe Selector.
  - `postgres` — schemas: `trades`, `features`, `logs`, `backtest_runs`, `market_data` (OHLCV cache).
  - `grafana` — dashboards for equity curve, drawdown, degradation.
- **One-time OAuth bootstrap (off the VPS because it requires a browser for the cTID consent screen):** register the app at `openapi.ctrader.com` → run the auth script on the dev's local machine → browser opens consent → callback at `localhost:8080` captures `authorization_code` → exchange for `access_token` + `refresh_token` → persist `refresh_token` in `.env` → copy to the VPS via rsync/scp. Alternative: SSH tunnel `localhost:8080` from the VPS to local during consent.
- **VPS runtime:** `app` uses the `refresh_token` to get a new `access_token` when it expires (~30 days). Rotation behavior (whether it is rotating or static) to be confirmed in the Phase 1 smoke test.
- `restart: always` + healthcheck: TCP ping on `demo.ctraderapi.com:5035` + successful `ProtoOAApplicationAuthReq` validation.
- `.env` with `CTRADER_CLIENT_ID`, `CTRADER_CLIENT_SECRET`, `CTRADER_REFRESH_TOKEN`, `CTRADER_DEMO_ACCOUNT_ID`, `CTRADER_LIVE_ACCOUNT_ID`, `DATABASE_URL`.
- Recommended Pepperstone account: **Razor** (raw spread + transparent commission $3.50/side — best for accurate cost backtesting). Standard is an acceptable fallback.

**Market data pipeline:** cTrader Open API Protobuf → Postgres. Key messages: `ProtoOASymbolsListReq` (symbol list), `ProtoOAGetTrendbarsReq` (historical OHLCV per timeframe M1/M5/H1/D1), `ProtoOASubscribeSpotsReq` (real-time bid/ask tick stream). Cover timeframes M1/M5/H1/D1 for instruments selected in Phase 2.

### Phase 2 — Backtest Module ✅ Done (2026-04-14) + Strategy Engine (2.5, pending)

**⚠️ Scope rewritten.** The original Phase 2 plan was "Strategy Engine (Universe Selector + candidate strategies)". In practice, it became clear that **no strategy could be calibrated without first having the rigorous backtest module** — CPCV/PBO/DSR are inputs to the Universe Selector, not outputs. Phase 2 was then re-scoped to deliver the **backtest module** (`src/ai_trade/backtest/`), with Clenow `stocks_on_the_move` as the calibration strategy (exercises point-in-time universe, ATR sizing, regime filter, survivorship). Executable spec with a Conclusion field per task: [`specs/backtest_phase2.md`](specs/backtest_phase2.md).

**Phase 2 delivery (commits `517c221` → `415e205`):**
- `backtest/data/` — `yfinance_source` + `wikipedia_spx` point-in-time
- `backtest/engine/` — portfolio + CFD-aware execution + bar-by-bar runner
- `backtest/validation/` — CPCV / PBO / DSR / walk-forward / MCPT (5 modules)
- `backtest/metrics/` — Sharpe/Sortino/Calmar/CAGR/DD/VaR + MD+PNG report
- `backtest/strategies/` — base + Clenow momentum replicated end-to-end
- **173 tests passing.** Mandatory survivorship disclaimer on every report.

**Phase 2.5 (pending) — Strategy Engine + Universe Selector:** the original content of this section (Design constraint / Universe Selector / grounded candidates) remains as future work, now **much better equipped** — with a validated engine, "build infra + design strategy" are no longer mixed. Phase 2.5 opens after Clenow runs on a grid (see §"Post-Phase 2 reassessment" in `specs/backtest_phase2.md`).

---

#### Original Phase 2 content (now Phase 2.5 — Strategy Engine + Universe Selector)

**Design constraint #1 — short holding:** Pepperstone operates everything as **CFD**, with swap/overnight charged daily. Strategies should have a typical holding period of **minutes to a few days** (ideally closing the position before rollover — Pepperstone's exact time to be confirmed on the Phase 1 bootstrap; likely 22h GMT as with most CFD brokers). Multi-month buy-and-hold is out of scope — swap becomes material drag on alpha.

**Design constraint #2 — dynamic, limited universe:** instead of scanning hundreds of CFDs, the app operates over an **active universe of 5-15 instruments re-selected periodically** by the Universe Selector (sub-phase 2.0). Natural candidates: SPX500, NAS100, US30, XAUUSD, BTCUSD, ETHUSD, EURUSD, GBPUSD, USDJPY + high-liquidity share CFDs (AAPL, TSLA, NVDA, etc.).

**Instruments available on Pepperstone cTrader (for reference):** forex (~90 pairs), index CFDs (SPX500, NAS100, US30, GER40, UK100, JP225 etc.), share CFDs (global majors — smaller coverage than XM but enough for a curated universe), crypto CFDs (BTC, ETH, SOL, etc.), commodities (gold, silver, oil, gas). **Exact list obtained via `ProtoOASymbolsListReq`** on the first dev connection (start of Phase 2) — document in `docs/instruments_pepperstone.md` when available.

#### Sub-phase 2.0 — Universe Selector (dynamic universe selection / tradability screening)

**Concept:** a periodic agent/job that ranks a candidate pool and returns the K most "tradable" instruments right now — those where the active strategy has the highest probability of producing positive expectancy net of costs. The Strategy Engine operates **exclusively** on the returned list until the next round.

**Literature grounding:** central and well-documented concept. Formal names: *cross-sectional momentum ranking*, *liquidity/tradability filtering*, *regime-conditioned asset selection*, *instrument rotation*.

| Selector layer | Source book | Role |
|---|---|---|
| 1. Hard liquidity filter | Kaufman `trading_systems_methods`, Carver `systematic_trading` | Average spread, volume, minimum ATR, relative cost. Discards where edge dies in costs. |
| 2. Per-instrument regime classification | Chen `regime_change` | Detects trend/chop/high-vol; enables only instruments in the regime favorable to the strategy. |
| 3. Tradability / momentum score | Clenow `stocks_on_the_move`, Masters `stat_sound_indicators` | Ranking by adjusted momentum, Hurst, or a metric specific to the strategy. |
| 4. Statistical screening | Masters `permutation_tests` | Tests whether recent return under the strategy is significantly ≠ from noise. |
| 5. Conditional expectancy meta-label | López de Prado `advances_fin_ml` | Secondary model: "given current state, does the primary strategy have P(profit) > threshold?" |
| 6. Final ranking + cap at top K | Clenow | Cap at K instruments (retail $1k sweet spot: K=5-15). |

**Architecture:**

```
┌─ Universe Selector (runs every N days) ─────────────┐
│ Input:  candidate pool (~30-50 Pepperstone instrs)   │
│         pre-approved by minimum liquidity            │
│ Output: top K active instruments + score,            │
│         valid until next round                       │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌─ Strategy Engine operates ONLY on this universe ────┐
└──────────────────────────────────────────────────────┘
```

**Parameters to calibrate (via backtest in Phase 3):**
- **N (re-selection period):** weekly is the literature default (Clenow). Daily tends toward noise; monthly is too slow to adapt.
- **K (active universe size):** 5-15. $1k capital + risk budget cap K from above.
- **Transition rule:** open positions in instruments that left the ranking — keep until stop/target (Clenow, avoids churn) or close immediately? Default: keep.
- **Candidate pool:** define a fixed list of ~30-50 Pepperstone instruments pre-filtered by absolute liquidity (obtained via `ProtoOASymbolsListReq` and filtered by spread/ATR/volume). Does not change every round; only revisited quarterly.

**⚠️ Anti-overfit gate:** the Universe Selector is itself a strategy. It must pass the **same 7-layer framework from Phase 3** (CPCV, PBO, DSR, permutation). Without this, overfit is just pushed up a level — instead of overfitting strategy parameters, you overfit selector parameters.

Every implemented strategy must cite the source book/section. Prioritized candidates for the Pepperstone universe (filtered by the short-holding constraint):

| Strategy | Source book | Typical holding | CFD fit |
|---|---|---|---|
| Cycle analysis / DSP (intraday and short swing) | Ehlers — `rocket_science`, `cycle_analytics`, `cybernetic_analysis` | hours to 2-3 days | ⭐⭐⭐ native |
| Regime detection (filter over other strategies) | Chen — `regime_change` | overlay | ⭐⭐⭐ agnostic |
| Intraday cross-sectional momentum on the curated universe | Clenow — `stocks_on_the_move` (adapted) | 1-5 days | ⭐⭐ adapted |
| ML meta-labeling / triple-barrier | López de Prado — `advances_fin_ml` | defined by the barrier | ⭐⭐⭐ agnostic |
| Position sizing / fractional Kelly | Vince — `leverage_space`, `math_money_mgmt` | overlay | ⭐⭐⭐ agnostic |
| Sentiment overlay (news/social) | Peterson — `trading_on_sentiment` | overlay | ⭐⭐ requires extra data feed |

**Long-holding strategies (buy-and-hold, pure monthly rebalance) are out of scope** while the broker is CFD-based (Pepperstone or similar).

### Phase 3 — Rigorous backtest (7-layer anti-overfit framework)

Heart of the anti-overfit plan. Each layer comes from a book; real implementation in `src/ai_trade/backtest/validation/` with synthesis in `knowledge/validation/`:

1. **CPCV** (Combinatorial Purged Cross-Validation) — López de Prado. Distribution of Sharpes, not a single point.
2. **PBO** (Probability of Backtest Overfitting) — López de Prado. PBO > 0.5 ⇒ reject.
3. **DSR** (Deflated Sharpe Ratio) — López de Prado. Corrects Sharpe by N trials (mandatory when N > 1).
4. **Permutation tests** — Masters (`permutation_tests`). Tests whether edge ≠ chance; p < 0.05.
5. **Multi-regime walk-forward** — Kaufman / Masters. ≥ 8 windows, ≥ 6 profitable, DD ≤ 25% on each.
6. **Parameter parsimony** (max 2-4, each economically justified) — Aronson / Carver.
7. **Production degradation monitoring** — Aronson (`evidence_based_ta`). Continuous live vs. backtest audit.

### Phase 4 — Paper trading via cTrader demo account (real-time validation)
30-90 days running on the **Pepperstone cTrader demo account**, linked to the user's cTID. Execution identical to real — same SDK, same Protobuf protocol, only `CTRADER_DEMO_ACCOUNT_ID` and endpoint change (`demo.ctraderapi.com:5035`). Parity with live is native to the cTrader Open API design. Log every trade in Postgres, compare return distribution vs expected backtest, detect divergence (slippage, spreads, execution gaps).

### Phase 5 — Live trading on Pepperstone ($1000 initial)
Swap `CTRADER_LIVE_ACCOUNT_ID` and endpoint (`live.ctraderapi.com:5035`) in `.env`, same infra, same containers. Funding via PIX (Pepperstone supports it since 2024 for BR customers). Production gate: a strategy only passes if it clears the anti-overfit checklist (§6.4 of the plan). If PBO > 50% → discard. If DSR < 1.0 → discard.

### Phase 6 — Monitoring + governance
Claude receives weekly metrics, detects degradation, recommends pause / re-optimization / discontinuation.

### Phase 7 — Scaling
Only after Phase 6 has been solid for months.

---

## 🔖 Decisions deferred for reassessment (Phase 2-3)

**Intentionally minimalist** choices in the backtest module, recorded here
so they are not lost when it is time to revisit.

### Market data source (daily OHLCV)

**Initial decision:** `yfinance` + Wikipedia (scrape of historical SPX
constituents). Free, with **survivorship bias documented explicitly in
every backtest report**.

**Reassess when:** the first strategy passes the anti-overfit gates
(CPCV + PBO + DSR). Migrate to a paid survivorship-free source (Tiingo
~$10/mo, EOD Historical ~$20/mo, Norgate $85/mo if you want to replicate
Clenow rigorously). Migration is just a new adapter in
`src/ai_trade/backtest/data/`; it does not break existing code.

### Fast-prototyping lab (vectorbt)

**Initial decision:** do not add it. The rigorous custom engine is enough
while learning the engine itself is the main source of friction.

**Reassess when:** iteration over indicator/parameter hypotheses has
measurable friction (e.g. >30 min to test a simple variation). At that
point, `vectorbt` enters as a **sandbox to triage ideas before** they
are taken to the rigorous engine — it does not replace the rigorous one.

### Second strategy to replicate (after Clenow)

**Initial decision:** do not pre-select. Clenow `stocks_on_the_move` is
the sole target of the initial Phase 2/3 — it already forces the engine
to cover point-in-time universe, ATR sizing, cross-sectional ranking,
index regime filter and survivorship bias.

**Reassess when:** Clenow runs and the engine passes the gates. Documented
candidates:
- **AFML meta-labeling** `[advances_fin_ml, ch.3]` — direction primary + ML confidence secondary
- **Ehlers DSP** `[rocket_science, cycle_analytics]` — MAMA/Fisher/Cyber Cycle as filters/timing
- **Chan mean-reversion / pairs** `[algo_trading_chan]` — cointegration, pairs trading

The choice becomes informed by Clenow's findings (e.g.: if the problem is
regime change → AFML meta-label; if it is entry/exit → Ehlers DSP; if it
is timing on trend-follow → Chan mean-reversion as overlay).

---

## 🧪 Two-stage backtest: research vs. calibration

Design principle (not a deferred decision — this is how the backtest works
across all phases):

### Stage 1 — Research / edge detection (Phase 2-3)

- **Question:** does the strategy have edge on clean equity data?
- **Data:** external survivorship-aware sources — `yfinance`+Wikipedia (initial, free, documented bias), then Tiingo/EOD/Norgate.
- **Why external:** cTrader/Pepperstone only provides the broker's own data, limited history and **no** point-in-time constituents. Edge detection requires academic-quality cross-broker data.
- **Gates:** CPCV + PBO + DSR + permutation + walk-forward. ~80% of bad ideas die here.

### Stage 2 — Calibration in Pepperstone reality (pre-Phase 4)

- **Question:** does this edge survive the real CFD costs on Pepperstone?
- **Data:** trendbars history via `ProtoOAGetTrendbarsReq` (cTrader Open API, available when Spotware approves the app).
- **Applied adjustments:**
  - Real per-symbol spread (measured, not estimated)
  - Per-symbol swap/overnight
  - Reduced universe (Pepperstone does not list the full 500; offers index CFD + selected share CFDs + forex/crypto/commodities)
- **Expected result:** Sharpe lower than in Stage 1. If the edge evaporates here, the strategy dies before paper trading.

### What changes in code when cTrader unblocks

**Nothing in the engine architecture** (CPCV/PBO/DSR/strategy logic). Only
a new adapter is added:

```
src/ai_trade/backtest/data/
├── yfinance_source.py            # Stage 1 (start, free)
├── wikipedia_spx.py              # SPX constituents (Stage 1)
├── tiingo_source.py              # (future) Stage 1 survivorship-free
└── ctrader_historical_source.py  # (future) Stage 2, Pepperstone calibration
```

**Underlying principle:** never use broker data as the sole research
source — only as final validation against real execution. Broker data has
survivorship bias (only products the broker still offers), selection bias
(broker-specific), and history bias (variable depth).

---

## 🔑 Key principle (non-negotiable)

This system treats trading as a **statistics and signal-processing problem**
— quantifiable algorithms that pass rigorous validation
(CPCV/PBO/DSR/permutation). The LLM enters as a **complementary qualitative
judgment layer** (rationality audit, drift detection in live, contextual
second opinion), never as a primary trade reasoner. Every decision
(indicator, parameter, sizing, production gate) requires a
`[book.slug, p.X]` citation from the knowledge base — "vibes-based LLM
trading" is explicitly rejected. That is why Phase 0 comes first: without
it, the agent operates with no grounding.

**Summary:** Phase 0 = intellectual ammunition. Phases 1-7 = build and
operate the system using that ammunition.

---

## 🔄 How to resume a session

Paste this prompt when opening Claude Code:

```
Resuming development of the ai-trade project at /var/www/pessoal/ai-trade.

Current state (2026-04-15, post-pivot):
- Phase 2 (backtest engine) + Phase 2.5 Runs 1-4 complete (all on daily
  bars). Last cycle F3.D Portfolio Clenow+Ehlers: FAIL v1 (PBO 0.849 —
  diversification uniformity paradox, DSR 0/9 best p=0.190) but
  WF 9/9 ✅ as a genuine sub-result. Commits 872a9cf/c99bca3/36c0f57/
  ac00d6e/e7c2254 + pivot commit on main.
- Pivot decided 2026-04-15 noite: all Phase 2.5 strategies had
  multi-day holds (Clenow median 56-63d, Ehlers median 1-22d w/ 4y
  outliers) — incompatible with CFD short-hold goal. Going forward:
  intraday bars (1h primary, 15m/5m later) + tiingo_service lazy-cache
  replaces bulk download. AFML sophisticated DEFERRED (re-enters as
  meta-layer over intraday strategy later).
- src/ai_trade/backtest/portfolio/ package is timeframe-agnostic —
  reusable for intraday combinations.
- 377 tests green (375 passed + 2 skipped).

Read first:
1. JORNADA.md — top sections ("Onde estamos hoje", "O que vem a seguir")
   + last two changelog entries (pivô + F3.D v1 FAIL).
2. ROADMAP.md §"Current status" (has the pivot block marked ⚠️) +
   §"Next steps (post-pivot)".
3. reports/grid_portfolio_20260415-1541/diagnostic.md (F3.D v1 — PBO
   paradox; useful to understand why diversification alone isn't enough
   when configs are too uniform).
4. src/ai_trade/backtest/data/{tiingo_source.py,tiingo_storage.py} —
   starting points for the new tiingo_service lazy-cache layer.
5. docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md
   — the F3.D spec shows the brainstorm→spec→plan→SDD pattern to mirror.

Next step per ROADMAP: brainstorming of tiingo_service (lazy-cache
layer). Cache key = hash(endpoint, asset_class, ticker, start, end,
frequency, ...); cache root data/cache/; on miss hit Tiingo API,
persist (parquet), return. Must co-exist with current
TiingoSource/TiingoStorage (daily bulk is already on disk). Unlocks
intraday endpoints (Tiingo IEX 1min/5m/1h) on demand. Use the loop:
superpowers:brainstorming → writing-plans → subagent-driven-development,
same pattern as this session's F3.D. Citation rule inviolable
([book.slug, p.X]). JORNADA.md updated on each meaningful progress.
Commit only when asked.
```

---

## 📚 Books in the knowledge base (33/33 absorbed and validated)

Summarized status — full details in `books/README.md` (the "Book catalog" table with per-book Review columns):

| # | Book | Slug | Importance | Quality |
|---|---|---|---|---|
| 1 | Adaptive Markets (Lo) | `adaptive_markets` | ⭐ | ⚠️ |
| 2 | Advances in Financial Machine Learning (López de Prado) | `advances_fin_ml` | ⭐⭐⭐ | 🌟 |
| 3 | Algorithmic Trading (Chan) | `algo_trading_chan` | ⭐⭐ | 🌟 |
| 4 | Big Data and ML in Quantitative Investment (Guida ed.) | `big_data_ml_quant` | ⭐ | ✅ |
| 5 | Cybernetic Analysis for Stocks and Futures (Ehlers) | `cybernetic_analysis` | ⭐⭐ | ✅ |
| 6 | Cybernetic Trading Strategies (Ruggiero) | `cybernetic_trading` | ⭐ | ⚠️ |
| 7 | Cycle Analytics for Traders (Ehlers) | `cycle_analytics` | ⭐ | ✅ |
| 8 | Data-Driven Science and Engineering (Brunton/Kutz) | `data_driven_science` | ⭐ | 🌟 |
| 9 | The Evaluation and Optimization of Trading Strategies (Pardo) | `eval_opt_strategies` | ⭐⭐⭐ | 🌟 |
| 10 | Evidence-Based Technical Analysis (Aronson) | `evidence_based_ta` | ⭐⭐ | 🌟 |
| 11 | Financial Time Series Analysis (Tsay) | `fin_time_series_tsay` | ⭐⭐ | ✅ |
| 12 | Leverage Space Trading Model (Vince) | `leverage_space` | ⭐⭐ | 🌟 |
| 13 | Machine Trading (Chan) | `machine_trading` | ⭐⭐ | ✅ |
| 14 | Mathematics of Money Management (Vince) | `math_money_mgmt` | ⭐⭐ | ✅ |
| 15 | ML for Algorithmic Trading (Jansen) | `ml_for_algo_trading` | ⭐⭐⭐ | ✅ |
| 16 | ML for Asset Managers (López de Prado) | `ml_for_asset_managers` | ⭐ | ✅ |
| 17 | Numerical Recipes (Press et al.) | `numerical_recipes` | ⭐ | ✅ |
| 18 | Quantitative Trading (Chan) | `quant_trading_chan` | ⭐⭐⭐ | 🌟 |
| 19 | Detecting Regime Change in Computational Finance (Chen) | `regime_change` | ⭐⭐⭐ | ✅ |
| 20 | Risk Parity Fundamentals (Qian) | `risk_parity` | ⭐ | ✅ |
| 21 | Rocket Science for Traders (Ehlers) | `rocket_science` | ⭐ | ✅ |
| 22 | Handbook of Sentiment Analysis in Finance (Mitra & Yu) | `sentiment_analysis_handbook` | ⭐ | 🌟 |
| 23 | Statistically Sound Indicators (Aronson/Masters) | `stat_sound_indicators` | ⭐⭐ | 🌟 |
| 24 | Stocks on the Move (Clenow) | `stocks_on_the_move` | ⭐⭐⭐ | 🌟 |
| 25 | Systematic Trading (Carver) | `systematic_trading` | ⭐⭐⭐ | 🌟 |
| 26 | Technical Analysis for Algorithmic Pattern Recognition (Tsinaslanidis) | `tech_analysis_patterns` | ⭐ | ✅ |
| 27 | Testing and Tuning Market Trading Systems (Masters) | `testing_tuning` | ⭐⭐ | ✅ |
| 28 | Time Series Analysis (Hamilton) | `time_series_hamilton` | ⭐ | 🌟 |
| 29 | Trading Evolved (Clenow) | `trading_evolved` | ⭐⭐ | ✅ |
| 30 | Trading and Exchanges (Harris) | `trading_exchanges` | ⭐⭐ | ✅ |
| 31 | Trading Systems and Methods (Kaufman) | `trading_systems_methods` | ⭐⭐⭐ | 🌟 |
| 32 | Universal Tactics of Successful Trend Trading (Penfold) | `universal_trend_tactics` | ⭐ | ✅ |
| 33 | Volatility Trading (Sinclair) | `volatility_trading` | ⭐⭐ | ✅ |

**Legend:** ⭐⭐⭐ Critical (7) · ⭐⭐ Important (12) · ⭐ Complementary (14). 🌟 Perfect (12) · ✅ Good (20) · ⚠️ Border (1).

**Not absorbed (out of current scope, historical note):**
- `permutation_tests` (Masters) — relevant content already covered by `stat_sound_indicators` + `testing_tuning` (same author, strong overlap).
- `assessing_prediction` (Masters) — same.
- `trading_on_sentiment` (Peterson) — superseded by `sentiment_analysis_handbook` (Mitra & Yu, broader coverage).
- `new_tech_trader` (LeBeau & Lucas) — referenced by `cycle_analytics` as the origin of VIDYA; documented decision not to absorb, cross-ref kept with N/A.

The pipeline is idempotent: missing PDFs are skipped without breaking execution.

---

## 📎 Quick references

- Phase 0 approved plan: `/home/victor/.claude/plans/mighty-mixing-porcupine.md`
- Active plan: `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
- **Detailed per-book status:** `books/README.md` ("Book catalog" section with Review table)
- Validated summaries: `books/summaries/*.md`
- Validation audit: `books/summaries/.validation/` (gitignored)
- Absorption logs: `books/summaries/.logs/` (gitignored)
