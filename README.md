# ai-trade — Systematic Trading (Dual Environment)

Automated systematic trading system targeting **two parallel deployment
paths**: short-hold via **Pepperstone CFD / cTrader Open API** (hours~few
days, swap cost) and swing via a **Brazilian stock broker** (days~weeks,
no swap, 15% capital-gains tax). Every strategy is labelled by the path
it fits and gated against the **path-specific cost model**.

Grounded in **16 actively-cited quantitative trading / ML books** (out
of 34 absorbed; 18 archived in 2026-04-16 cleanup — full list in
`books/CITATION_AUDIT.md`) exposed as a Claude Skill (citable knowledge
base). All code is deterministic; every decision cites `[book.slug, p.X]`.

**Golden rule:** no claim, strategy, parameter, or gate without a book
reference. Hallucination destroys the value of the knowledge base — and,
in live, destroys capital.

See [`ROADMAP.md`](ROADMAP.md) §"Two production environments" for the
dual-path framework and per-path constraints.

---

## Status

| Phase | Scope | Status |
|---|---|---|
| 0 | Knowledge base — 34 books → validated summaries (16 active + 18 archived) | ✅ Done |
| 0.5 | `build_skill.py` + skill sanity gate | ✅ Done |
| 1 | Pepperstone/cTrader infra + Postgres/Grafana | 🔄 Scaffold (awaiting Spotware OAuth approval) |
| 2 | Backtest engine + CPCV/PBO/DSR/WF/MCPT validation | ✅ Done — 918 tests green (cross-lib validated 1e-6) |
| 2.5 | Strategy search via self-improve loop | ✅ Done — initial winners deprecated in 3.5c/3.5f re-validations |
| 3 | Post-cleanup evolution: 5 leads (A1-A3 + B1-B2) | ✅ Done — consolidated in Phase 3.5b (Plano B V4 later rejected in 3.5c) |
| 3.5a V1 | Plano A short-hold 1h FX/metals retail (6 famílias) | ❌ Refuted 2026-04-18 (0/143 PASS, framework errado) |
| 3.5a V2 | Plano A daily multi-asset CFD Pepperstone (6 famílias novas) | ❌ **WINNER retracted 2026-04-22** — look-ahead bias in engine inflated baseline; honest re-validation fails gates in `reports/phase_3_5f/honest_revalidation/` |
| 3.5b | Plano B LETF rotation winners end-to-end validation | ❌ V4 baseline retracted 2026-04-20 (testfol.io synthetics divergence) — see 3.5c |
| 3.5c | Cross-lib validation (bt, vectorbt, backtrader) | ✅ Done 2026-04-20 — exposed Plano B V4 divergence; adapters clean + reusable |
| 3.5d | Plano B 3× LETF swing search | ❌ Closed 2026-04-21 — arbitration blocked E1 (PBO grid-shrinkage anti-pattern) |
| 3.5e | Plano B breadth-hunt c01-c12 | 🔄 Paused 2026-04-21 — c01/c02/c03/c05 DEAD, c06-c12 untested; engine now confirmed clean |
| 3.5f | Engine look-ahead fix + Plano A V2 honest re-validation | ✅ Done 2026-04-22→23 — bug fixed (commit `7b90a8f`); all 6 V2 leads FAIL honest gates |
| 3.6 | Broader swing-winner hunt over 33 books (broker-agnostic) | 🔄 Next — plan `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` |
| 4 | Paper trading dual-path 3 meses (cTrader demo A + Inter Global B) | ⏸️ Paused — no winner to paper-trade |
| 5 | Live trading ($1000 initial) | ⏳ Blocked on 4 |
| 6 | Monitoring + governance | ⏳ |
| 7 | Scaling | ⏳ |

**Current reality (2026-04-23):** no winner is currently confirmed for
Plano A or Plano B. Phase 3.6 is a fresh broad hunt across the 33
books to find one. See [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
for the canonical status snapshot.

Phase-by-phase details + dual-environment framework + autonomous loop
discipline in [`ROADMAP.md`](ROADMAP.md).

---

## High-level architecture

```
         Phase 0 — knowledge base (done)                   Phase 1+ — runtime (partial)

books/raw/    ─▶ summaries/    ─▶ knowledge/               cTrader Open API ◀──▶ src/ai_trade/
(33 PDFs)        (33 MD, 9 sec)    SKILL.md                (Protobuf/OAuth2)      (Python/Twisted)
                                   + books/                                             │
                                   + strategies/                                        ▼
                                   + indicators/                                  Postgres + Grafana
                                   + validation/                                  (docker-compose)
```

- Python does NOT use any LLM SDK. All LLM intelligence runs inside the
  **Claude Code CLI** (subagents + slash commands).
- Scripts in `scripts/` and modules in `src/ai_trade/` are deterministic.

---

## Repository structure

```
ai-trade/
├── books/                           # Raw knowledge base (Phase 0)
│   ├── raw/                         # 34 PDFs with canonical slugs
│   ├── summaries/                   # 16 active MD (18 archived under _archive/)
│   ├── code/                        # Complementary C++ code (Timothy Masters)
│   ├── MAPPING.md                   # "Original name → slug" inventory
│   ├── CITATION_AUDIT.md            # USED / ARCHIVED / PROTECTED audit
│   └── README.md                    # Catalog + quality + absorption pipeline
├── knowledge/                       # Aggregated Claude Skill (Phase 0.5)
│   ├── SKILL.md                     # Entry point + inviolable rules
│   ├── books/                       # Per-book summaries (validated copy)
│   ├── strategies/                  # Thematic aggregations (momentum, cycles, ...)
│   ├── indicators/                  # Ehlers DSP, momentum, HMM
│   └── validation/                  # CPCV, permutation, DSR, walk-forward
├── src/ai_trade/                    # Python runtime (Phase 1+)
│   ├── __init__.py
│   ├── config.py                    # Typed config (pydantic-settings)
│   └── backtest/                    # Phase 2 — backtest module
│       ├── data/                    #   tiingo + yfinance + Wikipedia SPX point-in-time
│       ├── engine/                  #   portfolio + CFD-aware execution + runner
│       ├── validation/              #   CPCV / PBO / DSR / walk-forward / MCPT
│       ├── metrics/                 #   Sharpe/Sortino/Calmar + MD+PNG report
│       ├── grid/                    #   parameter-grid runner + gate evaluator
│       ├── helpers/                 #   pure-function helpers (momentum.py)
│       └── strategies/              #   base + 2 production winners (bollinger_mr + etf_rotation)
├── scripts/                         # Deterministic utilities (no LLM)
│   ├── extract_pdfs.py              # PDF → text + chapters + metadata
│   ├── validate_summary.py          # Structural gate for summaries
│   ├── check_citations.py           # Check PDF↔printed offset + citations
│   ├── build_page_index.py          # Generate per-book _page_index.json
│   ├── aggregate_judges.py          # Aggregate adversarial judges (Layer-3)
│   ├── build_skill.py               # Summaries → knowledge/
│   ├── compress_pdfs.py             # Ghostscript compressor (reversible)
│   ├── rename_books.py              # Normalize slugs in books/raw/
│   ├── ctrader_oauth_bootstrap.py   # OAuth2 one-time bootstrap (local browser)
│   ├── run_grid_bollinger_mr.py     # Path A winner — BollingerMR SPY 1h grid
│   ├── run_oos_bollinger_mr.py      # Path A winner — OOS validation
│   ├── run_etf_rotation.py          # Path B winner — Monthly ETFRotation
│   ├── run_oos_etf_rotation.py      # Path B winner — OOS validation
│   ├── run_*_phase_b.py             # Phase B validation scripts (cost ablation, MC, regime)
│   ├── self_improve_loop.sh         # Autonomous self-improve loop driver
│   └── clean_intraday_orphans.py    # Tiingo IEX placeholder-bar defense
├── db/
│   └── init.sql                     # Postgres schemas: market_data, trades, ...
├── docker-compose.yml               # Postgres 16 + Grafana 11
├── .env.example                     # Credentials/tokens template
├── pyproject.toml                   # Deps + hatch config
├── ROADMAP.md                       # Phase map + non-negotiable principles
└── README.md                        # this file
```

---

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`
- Docker + Docker Compose (for local Postgres/Grafana)
- Claude Code CLI (to expand the knowledge base or re-absorb books via
  `/absorb-book`; not required for the Phase 1+ runtime)

---

## Setup

### Python

```bash
uv sync
# or: python -m venv .venv && .venv/bin/pip install -e .
```

### Local infra (Postgres + Grafana)

```bash
docker compose up -d postgres grafana
docker compose exec postgres psql -U ai_trade -d ai_trade -c "\dn"
# should list: market_data, trades, features, logs, backtest_runs
```

**Ports:**
- Postgres: `localhost:5435` (maps → container 5432; `5432` local is left for a native Postgres, if any)
- Grafana: `http://localhost:3000` (login `admin` / `ai_trade`)

Stop without wiping data: `docker compose down`. Wipe everything: `docker compose down -v`.

### cTrader OAuth (one-time, after Spotware approves the app)

```bash
cp .env.example .env
# fill in CTRADER_CLIENT_ID and CTRADER_CLIENT_SECRET (from the Spotware portal)
python scripts/ctrader_oauth_bootstrap.py
# opens browser → consent screen → captures refresh_token → writes to .env
```

The app must be approved by Spotware (manual, hours to days after submission
at `openapi.ctrader.com`). Until approved, the bootstrap fails with
*"OA client is not in active state"*.

---

## How to run a backtest

Phase 2 delivered the complete backtest module in `src/ai_trade/backtest/`:
engine (portfolio + CFD-aware execution + bar-by-bar runner), validation
framework (CPCV / PBO / DSR / walk-forward / MCPT), metrics (Sharpe /
Sortino / Calmar / CAGR / max DD / VaR) and a markdown + PNG report
generator. After Phase 2.5 cleanup (2026-04-16) only the 2 production
winners remain in `strategies/`.

**Winner #1 — BollingerMR GARCH SPY 1h [SHORT-HOLD CFD, Path A]**
(IS Sharpe 0.995, OOS 0.945):

```bash
.venv/bin/python scripts/run_grid_bollinger_mr.py \
    --data-source tiingo --symbol SPY --asset-class etf \
    --storage-root data/tiingo \
    --start 2019-12-02 --end 2026-04-15 \
    --frequency 1hour --output-dir reports/ --n-jobs 4 \
    --run-id grid_bollinger_mr_spy_1h_<id>
```

**Winner #2 — ETFRotation Monthly Top-1 [SWING BROKER, Path B]**
(IS Sharpe 0.708, OOS 1.477, 22 anos histórico):

```bash
.venv/bin/python scripts/run_etf_rotation.py
```

Outputs land in `reports/<run_id>/`:
- `summary.md` (gates pass) OR `diagnostic.md` (gates fail) — both
  include survivorship disclaimer when source is yfinance/Wikipedia
  (Tiingo storage releases the disclaimer)
- `assets/*.png` — equity curve + underwater drawdown
- `.cache/grid_runs/<run_id>/trial_*/` — per-trial checkpoints
  (parquet + JSON, resume-friendly)

Components (covered by **345 tests** post-cleanup with numerical
verification against the source books):
- `backtest/engine/` — `portfolio.py` / `execution.py` / `runner.py`
- `backtest/validation/` — `cpcv.py` / `pbo.py` / `dsr.py` /
  `walk_forward.py` / `permutation.py`
- `backtest/metrics/` — `performance.py` / `report.py`
- `backtest/grid/` — `runner.py` / `result.py` / `gates.py` /
  `walk_forward.py` / `bollinger_mr_config.py` (only surviving config)
- `backtest/helpers/` — `momentum.py` (pure functions: `adjusted_slope`,
  `atr`, `max_gap`)
- `backtest/strategies/` — `base.py` / `bollinger_mr.py` /
  `etf_rotation.py` (the 2 winners)

Executable Phase 2 spec with a Conclusion field per task:
[`specs/backtest_phase2.md`](specs/backtest_phase2.md). Production
readiness summary of the 2 winners:
[`jornada/2026-04-16/10-production-readiness-summary.md`](jornada/2026-04-16/10-production-readiness-summary.md).
Investment Mandate (regras invioláveis):
[`docs/investment-mandate.md`](docs/investment-mandate.md).

**Critical gate:** every report generated from `yfinance`/`wikipedia`
sources includes a mandatory survivorship-bias disclaimer (inviolable
rule from the ROADMAP). Migration to a paid source (Tiingo/EOD/Norgate)
is deferred until the first strategy survives a grid with PBO < 0.5 and
DSR p-value < 0.05 — see
[`specs/backtest_phase2.md`](specs/backtest_phase2.md#post-phase-2-reassessment-deferred-decisions-from-the-roadmap).

---

## How to run the grid (Phase 2.5)

The `src/ai_trade/backtest/grid/` module extends Phase 2 with
infrastructure to run a grid of strategy configurations with anti-
overfit gates active (PBO / DSR / walk-forward). After the 2026-04-16
cleanup only `BollingerMRGridConfig` remains as a registered grid
config; the runner is generic, so Phase 3 leads can plug in their own
frozen dataclasses.

Follow execution in real time (unified log — a single `tail -f` for
any run):

```bash
tail -f logs/grid.log
cat logs/grid_latest_status.md  # high-level snapshot of the last run
```

**Outputs:** `reports/<run_id>/summary.md` (gates pass) OR
`diagnostic.md` (gates fail), `assets/*.png`, and resume-friendly
checkpoints in `.cache/grid_runs/<run_id>/trial_*/`.

**Phase 2.5 result (2026-04-16 evening):** 2 production winners
(BollingerMR SPY 1h GO-WITH-CAVEATS + ETFRotation monthly top-1 GO).
Detailed verdicts: [`jornada/2026-04-16/10-production-readiness-summary.md`](jornada/2026-04-16/10-production-readiness-summary.md).

---

## Tiingo bulk dataset (Phase 2.5 Run 3)

Survivorship-free OHLCV cache for the planned Run 3 ablation. Persisted
under `data/tiingo/` so backtests work offline after the Tiingo Power
subscription is cancelled.

```bash
# 1) Set the API key (one-time)
echo "TIINGO_API_KEY=<your-key>" >> .env

# 2) Bulk-download the universe (~30-40 min for --bucket all)
.venv/bin/python scripts/tiingo_bulk_download.py \
    --bucket all --start 2014-01-01 --end 2026-04-14

# 3) Backup the dataset to a portable .tar.gz (~150 MB)
.venv/bin/python scripts/tiingo_backup.py
# → data/tiingo_backup_<YYYYMMDD-HHMM>.tar.gz

# 4) Run grids against the local cache (no API needed after step 2)
.venv/bin/python scripts/run_grid_clenow.py --data-source tiingo \
    --start 2015-01-01 --end 2023-12-31 --n-jobs 4
.venv/bin/python scripts/run_grid_ehlers.py --data-source tiingo \
    --start 2015-01-01 --end 2023-12-31 --n-jobs 4
```

Buckets: `spx500` (Wikipedia point-in-time, ~800 unique inc. delistings),
`spx400` / `spx600` (current snapshot), `etf` (32 hand-picked broad/
sector/bond/commodity/vol), `crypto` (top-10 by liquidity),
`forex` (10 majors + crosses), `all` (union, ~1700 unique).

Tiingo does not serve raw indices — `--data-source tiingo` auto-swaps
`^GSPC` → `SPY` (and Ehlers `--symbol` similarly). Heavy parquet files
under `data/tiingo/prices/` are gitignored; `manifest.json` is
force-tracked so collaborators see what's been downloaded.

Rationale for the ablation: [`docs/tiingo_ablation_rationale.md`](docs/tiingo_ablation_rationale.md).

---

## Books

**34 books absorbed; 16 active + 18 archived (cleanup 2026-04-16)** as a
Claude Skill (Phase 0 done). Per-book importance (⭐⭐⭐ critical, ⭐⭐
important, ⭐ complementary) and absorption quality (🌟 perfect, ✅ good,
⚠️ borderline) are in the full catalog at
[`books/README.md`](books/README.md).

**Canonical inventory** (slug → title/author/year): [`books/MAPPING.md`](books/MAPPING.md).
**Citation audit** (USED / ARCHIVED / PROTECTED): [`books/CITATION_AUDIT.md`](books/CITATION_AUDIT.md).

### Raw PDFs are not versioned

The source PDFs **are not in the repository** (copyright + size). If you
cloned this repo and want to run the extraction pipeline
(`scripts/extract_pdfs.py`) locally, you have to provide the files
manually under `books/raw/<slug>.pdf` using the slugs listed in
[`books/MAPPING.md`](books/MAPPING.md). The markdown summaries already
versioned in `books/summaries/` cover most use cases (knowledge base +
citations); raw extraction is only needed to re-absorb or validate.
Expected tree:

```
books/
├── raw/              # your PDFs (gitignored)
├── extracted/        # output of extract_pdfs.py (gitignored)
└── summaries/        # versioned markdown (in repo)
```

To re-absorb a book or add a new one:

```
# inside Claude Code
/absorb-book <slug>
```

Full pipeline documented in [`books/README.md#pipeline`](books/README.md#pipeline-como-reproduzir--re-absorver).

---

## Anti-overfit key concepts (CPCV / PBO / DSR)

Three tests from López de Prado (`advances_fin_ml`) that act as **mandatory
gates** for every backtest in this project. They appear in inviolable
rules #3-5 of `knowledge/SKILL.md` and will be ported into
`src/ai_trade/backtest/validation/` in Phases 2/3. Together, they close
the loop against "high-Sharpe strategy that dies in live":

- **CPCV** → you get an honest *distribution* of performance, not a point.
- **PBO** → you know whether the *selection process* is biased.
- **DSR** → you know whether the observed Sharpe survives multiple-hypothesis testing.

**None are available in a maintained open library** (mlfinlab had them,
went commercial). Implementation will be custom but direct — cross-reference
in `knowledge/validation/cpcv.md`, `knowledge/validation/deflated_sharpe.md`
and `knowledge/validation/permutation.md`.

### CPCV — Combinatorial Purged Cross-Validation

**What:** cross-validation adapted for financial time series.

**Why it matters:** standard k-fold **leaks information** in time series —
training and test features overlap in time. Sharpe looks good; in
production it collapses.

**Three components:**
1. **Purged**: removes training samples whose labels overlap the test period.
2. **Embargo**: inserts a *buffer* after each test block (serial correlation does not respect fold boundaries).
3. **Combinatorial**: instead of K folds → K test sets, generates C(K, N) combinations. K=10 with N=2 = 45 paths. You now get a **distribution** of Sharpes, not an isolated number.

**Useful output:** *"over 45 simulations, Sharpe was 1.2 ± 0.4 — worst case 0.3"*.
Much more honest than *"Sharpe = 1.5 in backtest"*.

Ref: `advances_fin_ml.md`, ch.7 `[p.104-117]`.

### PBO — Probability of Backtest Overfitting

**What:** probability that the **strategy selection process**
(pick the best in-sample) produces one that underperforms out-of-sample.

**How it's computed:** shuffles multiple IS/OOS partitions. For each
partition, takes the strategy with the best IS Sharpe and checks whether
it ended above or below the OOS median. If it **frequently** ends below
the median → your backtest process is biased.

**Practical gate (inviolable rule #3):** PBO > 0.5 ⇒ **discard**. Your
"winning strategy" is more likely to be overfit than valid.

**Intuition:** if you test 100 parameter combinations, some will hit
Sharpe 2 **by pure luck**. PBO quantifies that risk.

Ref: `advances_fin_ml.md`, ch.11 `[p.208-211]`. Reference implementation:
`books/code/masters-testing-tuning/CSCV_MKT/CSCV.CPP` (Masters' C++).

### DSR — Deflated Sharpe Ratio

**What:** Sharpe "deflated" by the number of strategies tested.

**Why it matters:** if you tried **1 strategy** and got Sharpe 2, it's
impressive. If you tried **1000 strategies** and the best got Sharpe 2,
that's expected **by pure chance** — the tail of the Sharpe distribution
over N trials concentrates high values.

**Formula (high-level):** deflates the observed Sharpe by:
- N (number of trials)
- skewness and kurtosis of returns
- sample size
- cross-sectional variance of tested Sharpes

Produces a p-value: *"given I tested N strategies, what is the probability
that this SR is genuinely > 0?"*

**Practical gate (inviolable rule #4):** report DSR whenever N > 1. Never
cite raw Sharpe in a PR without the DSR alongside.

Ref: `advances_fin_ml.md`, ch.14 `[p.261-270]`.

---

## Clenow universe and survivorship bias

Concept complementary to the 3 above — attacks the same disease (lying
backtest) from another angle: the **data**, not the statistical tests.

### What the "Clenow universe" is

Andreas Clenow's momentum strategy (`stocks_on_the_move`) operates over
**SPX 500**, re-ranking weekly. But "SPX 500" **depends on the historical
date being simulated** — it is not the current list.

Between 2005 and 2026, dozens of companies entered the index (NVDA in
2001, TSLA in 2020) and left (Lehman Brothers, Enron pre-collapse,
Washington Mutual, General Motors 2009, Sears, etc.). A backtest using
the **current** SPX 500 list is testing a reality that never existed.

### Survivorship bias

Systematic backtest error caused by using **only current survivors**
instead of historical constituents.

Testing momentum 2000-2020 with the current SPX list is cheating: you
removed every company that went bankrupt, was demoted, or merged. The
backtest shows a high Sharpe because the sample is already **filtered by
winners**. Equivalent to interviewing billionaires about "the rules of
success" — the sampling is biased by construction.

Clenow is explicit about the size of the effect `[stocks_on_the_move, p.238-239]`:

> *"Survivorship bias kills simulations. Using current S&P 500 constituents
> for a 10-year backtest creates fake outperformance because current members
> are selected BECAUSE they rose. You MUST use point-in-time membership and
> include delisted stocks."*

### Correct solution

**Point-in-time constituents + delisted stocks.** Sources:
- **Norgate Data** (~US$85/mo) — Clenow's own recommended source
- **EOD Historical Data** (~US$20/mo) — survivorship-free daily
- **Tiingo** (paid plan ~US$10/mo) — affordable
- **CRSP** — academic gold standard, but expensive license
- **Wikipedia scrape** — brittle but free; this is where we start

### How we handle it in this phase

The initial backtest phase uses `yfinance` + Wikipedia scrape (free,
residual bias). **Every backtest report explicitly documents the caveat** —
results are optimistic until we migrate to a paid source. When the first
strategy passes the CPCV/PBO/DSR gates, the investment in survivorship-free
data becomes justified.

See [`ROADMAP.md`](ROADMAP.md) section "Backtest em duas etapas" for how
the universe (and the data) evolve between research and Pepperstone
calibration.

---

## References

- **Roadmap / phase status:** [`ROADMAP.md`](ROADMAP.md)
- **Book catalog + absorption pipeline:** [`books/README.md`](books/README.md)
- **Generated Claude Skill:** [`knowledge/SKILL.md`](knowledge/SKILL.md)
- **Active plan (Phase 0):** `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
