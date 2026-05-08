# Gold Swing Loop — Available Infrastructure

**Reuse, don't rebuild.** Day/swing gold strategies should compose from
these modules. Build new modules only when the mechanism is qualitatively
new (then add a TDD spec under `tests/test_<slug>.py` first).

## Gold price data (Tiingo cache)

### Primary datasets (4-way cross-validation, post-relaxation 2026-04-26)

- `data/tiingo/daily/prices/GLD.parquet` — **gld_long** dataset
  - GLD ETF spot proxy, daily OHLCV, 5 384 bars, **2004-11-18 → 2026-04-15 (21.4y)**
  - longest available; covers 2008 GFC + 2011 peak + 2013-2018 stagnation + 2019+ revival
- `data/tiingo/daily/prices/xauusd.parquet` — **xauusd_real** dataset
  - XAUUSD spot, daily OHLCV, 1 700 bars, **2020-01-02 → 2026-04-17 (6.3y)**
  - shorter but is the actual instrument; cost-realistic
- `data/tiingo/1hour/prices/xauusd.parquet` — **xauusd_intraday** dataset
  - XAUUSD spot, 1-hour OHLCV, **32 195 bars**, 2020-01-02 04:00 → 2026-04-17 20:00 (6.3y)
  - For day/swing strategies that need intraday signals/exits
- **`gold_synth_40y` — DEFERRED, first iter constructs**
  - Target: gold spot daily, 1986-01 → 2026-04 (~40y, ~10 100 bars)
  - Source candidates: FRED `PCU2122212122` (gold producer price
    monthly), LBMA daily AM/PM fix series via Quandl/LBMA direct, or
    World Gold Council historical
  - Output cache: `data/external/macro/gold_fixing_daily.parquet`
  - Until built, declare without it — first iter that needs 40y window
    constructs as part of its Stage 3 work, then commits the dataset.

### Multi-timeframe support (current vs future)

| TF | status | source | notes |
|---|---|---|---|
| **1d** | ✅ available | Tiingo cache (GLD 21y + XAUUSD 6.3y) | full coverage |
| **4h** | ✅ resampleable | resample 1h → 4h (~8 050 bars) | clean integer ratio, no data loss |
| **1h** | ✅ available | Tiingo cache (XAUUSD 6.3y, ~32k bars) | direct |
| **30m / 15m / 1m** | 🟡 fetchable | cTrader Open API (`scripts/ctrader_oauth_bootstrap.py` already wired; creds in `.env` as `CTRADER_CLIENT_ID` + `CTRADER_CLIENT_SECRET` for app 25702 demo) | needs separate "data infra" iter to fetch + cache; XAUUSD symbol on PEP demo |

**For now (iter 001+): use 1d / 4h / 1h directly from Tiingo.** Fine-TF
strategies (30m / 15m / 1m) require a one-time **data-infra iter** that
fetches XAUUSD bars from cTrader Open API (using cached OAuth tokens in
`.env`) and writes parquet to `data/ctrader/<freq>/xauusd.parquet`.
Plan that iter when first hypothesis legitimately needs sub-1h bars
(e.g., scalping, microstructure-aware MR). **Do NOT block any iter on
missing fine-TF data — most day/swing strategies work fine on 1h+.**

**API access status**: cTrader Open API credentials are present in
project `.env` (gitignored) per Phase 4.0 setup
(`jornada/2026-04-20/02-phase4_0-T1-rate-card-empirico.md`). Re-running
`scripts/ctrader_oauth_bootstrap.py` refreshes tokens if expired.

A given strategy may operate on:
- **One TF only** (e.g., daily trend, intraday hourly momentum)
- **Multiple TFs** (e.g., daily entry / 1h trailing-stop)

Each iter's `hypothesis.md` must declare `timeframes_used: [1d, 4h, 1h]`
explicitly. Strategies needing TF not yet available are FROZEN with
"deferred (cTrader API)" tag.

### Multi-asset gold-complex universe (UPDATED 2026-04-26 — now portfolio-eligible)

Strategies declaring `universe = "gold_complex"` may build portfolios
from these instruments (XAU weight ≥ 40% required):

- `data/tiingo/daily/prices/GLD.parquet` — primary gold ETF (anchor)
- `data/tiingo/daily/prices/IAU.parquet` — gold ETF (cheaper EER, swap-friendly)
- `data/tiingo/daily/prices/xauusd.parquet` — gold spot (Pepperstone)
- `data/tiingo/daily/prices/xagusd.parquet` — silver spot
- `data/tiingo/daily/prices/SLV.parquet` — silver ETF (verify presence; fetch if missing)
- `data/tiingo/daily/prices/GDX.parquet` — gold miners (verify; fetch if missing)
- `data/tiingo/daily/prices/GDXJ.parquet` — junior gold miners (verify; fetch if missing)
- `data/tiingo/daily/prices/PPLT.parquet` or platinum proxy (verify; fetch if missing)
- `data/tiingo/daily/prices/RGLD.parquet` — gold royalty company (caution: stock-specific risk)

If any ticker is missing, single-fetch via existing Tiingo helper
(`scripts/tiingo_fetch.py` or equivalent in `src/market_lab/backtest/data/`).
Cheap (1 request each, < 1 min total).

### Cross-asset overlays (signal sources, not portfolio members)

- `data/tiingo/daily/prices/usdcad|usdchf|usdjpy.parquet` — DXY proxies
- `data/tiingo/daily/prices/SPY|QQQ|IWM.parquet` — equity for correlation/risk-off
- `data/tiingo/daily/prices/btcusd.parquet` — BTC for cross-asset risk-off

## Macro data (cached)

- `data/external/macro/vix_daily.parquet` — VIX (equity vol regime)
- `data/external/macro/t10y3m_daily.parquet` — yield curve slope
- `data/external/macro/cape_monthly.parquet` — Shiller CAPE
- `data/external/macro/ebp_monthly.parquet` — Gilchrist-Zakrajšek EBP

## Macro data NOT cached (would need fetch in iter 001+)

- **10y TIPS yield** (FRED `DFII10`) — gold's primary fundamental driver
- **Real yields** (5y/10y inflation breakevens)
- **DXY index** (ICE DXY, not single-cross proxies)
- **FOMC announcement dates** (FRED or manual)
- **CPI surprises** (Bloomberg/Refinitiv)
- **CFTC COT non-comm net longs** for gold

If a strategy needs any of these, iter must include data-fetch step + cache the result before backtest.

## Existing simulator infrastructure (reusable)

### Single-asset backtesters (sister loop's)

- `src/market_lab/backtest/strategies/ema_sma_threshold_educational.py`
- `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`

### Multi-asset stack simulators (sister loop's)

- `studies/strategy_hunt_loop/iterations/037-*/` — 3-leg static stack engine (could host gold as one leg in future multi-asset reactivation)
- `studies/strategy_hunt_loop/iterations/039-*/run_backtests.py` — VRP basket harvest engine

### Validation modules

- `src/market_lab/backtest/validation/pbo.py` (PBO via CSCV)
- `src/market_lab/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/market_lab/backtest/validation/walk_forward.py`
- `src/market_lab/backtest/validation/cpcv.py`
- `src/market_lab/backtest/validation/permutation.py`

### Metrics + signals

- `src/market_lab/backtest/metrics/performance.py` — CAGR / Sharpe / MDD
- `src/market_lab/backtest/signals/risk_score.py` — z-score sigmoid composite

### Data loaders

- `src/market_lab/backtest/data/macro_data_loader.py` — EBP / T10Y3M / CAPE / VIX

## Dual-broker execution paths

This loop's research output must specify which broker path applies.
Some strategies work on BOTH; many work on only one.

### Track A1 — Pepperstone XAUUSD CFD (Plano A reactivation)

**Instrument**: XAUUSD spot CFD (cTrader Open API for live, when available).

**Capabilities**:
- Long AND short
- Intraday (no day-trade pattern restrictions)
- Leverage up to 1:200 retail
- Asia / London / NY sessions all tradable
- No DARF (account is offshore SCB Bahamas Tier-3 per mandate §4.8)

**Cost model defaults** (verify in iter 001):

| component | value | rationale |
|---|---:|---|
| spread (round-trip) | 8 bps | Pepperstone Razor avg 30 cents per oz @ $2 100 = ~1.4 bps single-leg, 8 bps round-trip with execution slip; conservative |
| swap long (per night per lot) | −1 bps | Pepperstone overnight ≈ −5 USD/lot × 100 oz @ $2 100 = ~−2.4 bps; conservative −1 bps |
| swap short (per night per lot) | +0.3 bps | Short usually receives small positive swap at PEP (verify) |
| commission | 0 | Built into spread on standard XAUUSD CFD |
| slippage on stops | 5 bps | Stop execution beyond limit; gold has gap-prone weekends |

**Intraday-only (close before NY close)**: zero swap; only spread per turn.

**Weekend hold**: 3× swap on Friday close (covers Sat+Sun+Mon).

### Track A2 — CME GC futures via IBKR (NEW 2026-04-26)

**Instrument**: CME COMEX Gold futures (GC), front-month or specific
contract; auto-roll on volume crossover (typically 5-10 days before
delivery).

**Capabilities**:
- Long AND short
- Intraday (no day-trade pattern restrictions for futures)
- Leverage via SPAN margin (~$10k-15k margin per contract @ $2 100 gold;
  ~14× notional)
- Sun 18:00 ET → Fri 17:00 ET (near 24h)
- IBKR Brazil-resident accounts: futures supported (verify current
  policy at iter 001 of futures-track)
- DARF on futures: 15% on monthly net profit (same rule as ETFs)

**Cost model defaults** (verify when first iter uses this track):

| component | value | rationale |
|---|---:|---|
| spread (round-trip) | 1-2 bps | GC bid-ask typically $0.10-0.20 @ $2 100 = ~0.5-1 bps single-leg, 2 bps RT conservative |
| commission | $1-2 per contract per side | IBKR Pro tier ~$0.85; conservative $2 RT/contract on $210k notional = ~1 bp |
| roll cost (quarterly) | ~5-10 bps per roll | bid-ask + slippage on calendar spread; 4 rolls/year = ~30-40 bps annual drag |
| slippage on stops | 3 bps | tighter than CFD due to deeper book |
| margin financing | implicit | SPAN-based; no direct overnight financing charge (vs CFD swap) |

**Why this matters**: tight spreads (1-2 bps RT vs CFD's 8 bps RT) make
intraday MR / scalping economically viable. Strategies that died on CFD
8 bps may survive on futures 2 bps.

**Setup constraint**: requires user to open/maintain IBKR Pro account.
Not part of current Plano A roadmap — declare `cost_path: cme_futures`
only if hypothesis specifically benefits from sub-5-bps execution.

### Track B — Banco Inter Internacional (GLD/IAU ETF, Plano B-style)

**Instrument**: GLD or IAU ETF (gold-backed US-listed; Inter Internacional supports US ETFs via FINRA broker-dealer subsidiary).

**Capabilities**:
- LONG ONLY (no shorting US ETFs for Brazilian retail)
- Daily settlement only — **NO INTRADAY SAME-DAY ROUND-TRIP** for Brazilian retail US accounts (T+1 settlement, day-trade rule restrictive)
- 1× leverage (cash buy/sell only — no margin for Brazilian retail US accounts)
- US session only (when NYSE open)
- **DARF 15% on profits** (Brazilian capital-gains tax on US-equity sales for residents)
- R$20k/month exemption on US-equity sales — not modeled (assume all sales taxable for backtest conservatism)

**Cost model defaults** (verify in iter 001):

| component | value | rationale |
|---|---:|---|
| brokerage | 0 | Inter Internacional charges zero brokerage on US ETFs |
| FX spread (round-trip BRL→USD→BRL) | 99-150 bps | Inter Câmbio adds 0.99-1.50% per leg; mid 125 bps × 2 = 250 bps round-trip; conservative 100 bps assuming partial USD hold |
| settlement T+1 | implicit | Cannot day-trade; min hold is overnight |
| **DARF 15% on profits** | 15% × max(0, sum_monthly_profit) | Brazilian fiscal rule; applied per fiscal month, not per trade |
| ETF expense ratio | 40 bps/yr (GLD) or 25 bps/yr (IAU) | Already netted from ETF NAV |

**Track B cost model formula** (in backtest):
```python
gross_returns = ... # from strategy
net_pretax = gross_returns - fx_spread_per_turn * turnover - eer_per_bar
monthly_pretax = net_pretax.resample('M').sum()
darf_per_month = 0.15 * monthly_pretax.clip(lower=0)
net_after_tax = (monthly_pretax - darf_per_month).resample(orig_freq).ffill() / bars_per_month
```

### Strategy / track applicability matrix

| strategy class | Track A (PEP CFD) | Track B (Inter ETF) | notes |
|---|:---:|:---:|---|
| Daily trend following (EMA cross, Donchian) | ✅ | ✅ (long-only) | Track B's no-short halves trend captures |
| Daily mean-reversion (RSI, BB) | ✅ | ⚠️ (only long entries) | MR on uptrend regimes only via Track B |
| Intraday momentum (open-to-close) | ✅ | ❌ | T+1 blocks intraday on Track B |
| Macro overlay (DXY, real rates) | ✅ | ✅ (long-only) | Same signal, different sizing |
| Pre-FOMC drift event | ✅ | ⚠️ (long-only entries) | Often long-biased anyway |
| Gold-silver ratio mean-reversion | ✅ (XAUUSD vs XAGUSD shorts) | ❌ | Needs short capability |
| Long-only swing (weekly hold) | ✅ | ✅ | DARF impact: ~15% drag on positive years |
| VIX flight-to-quality | ✅ | ✅ (long entries) | Long-only is the natural fit anyway |

**Reporting requirement**: every iter's `verdict.json` must include
`broker_track: "pepperstone_cfd" | "inter_etf" | "both"` and per-track
metrics if both are applicable.

## What's NOT yet built (likely needed by iter 001-003)

- **Single-asset day/swing simulator** — neither sister loop's stack engine nor signal-overlay engine handle single-asset entry/exit cleanly. Probably need a lightweight per-iter `iterations/001-*/run_backtest.py` for first few iters, then refactor into a shared module if pattern stabilizes.
- **Pepperstone CFD cost model module** — encode spread + swap + slippage in a `cost_model.py` helper; reuse across iters.
- **Intraday session segmentation** — Asia/London/NY session boundaries on 1h bars (gold has different liquidity per session).

## Knowledge base

- `books/summaries/` — 33 absorbed books (slug ↔ title in `books/MAPPING.md`)
- `knowledge/SKILL.md` — aggregated quick-reference

Gold-relevant book references:
- `[trend_following]` (Covel) — momentum/breakout discipline
- `[stocks_on_the_move]` (Clenow) — relative strength + ATR sizing
- `[short_term_trading_strategies]` (Connors) — RSI(2), 2-day pullbacks
- `[volatility_trading]` (Sinclair) — VRP, vol regimes, options pricing
- `[trading_systems_methods]` (Kaufman) — intraday momentum, calendar effects
- `[ilmanen_expected_returns]` — gold as carry + safe-haven asset
- `[leverage_for_the_long_run]` (Gayed) — regime indicators, flight-to-quality
- `[risk_parity]` — multi-asset weighting (for future Plano A multi-asset extension)
- `[advances_fin_ml]` (López de Prado) — PBO, DSR, CPCV, meta-labeling
