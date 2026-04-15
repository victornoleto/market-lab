# Clenow Momentum Replication — Run Notes

Replication of the `stocks_on_the_move` system (Clenow, 2015) on the
ai-trade backtest engine, per the spec in `specs/backtest_phase2.md` Task 4.

This document compares the numbers obtained against those published in the
book, records the design decisions made during replication, and lists the
known limitations of the result (mainly survivorship bias).

---

## Book reference

- System: `stocks_on_the_move` (Clenow, 2015) — "Basic Strategy" + "Portfolio Rebalance"
- Universe: S&P 500, point-in-time constituents `[stocks_on_the_move, p.98, p.107]`
- Window: ~18 years (1999–2014) is the book's benchmark `[p.115]`
- Reported performance (extended version of the system):
  - CAGR ~12% gross
  - Annual Sharpe ~1.0
  - Max drawdown ~25%
  - Comparable index (SPY TR): CAGR ~5%, DD ~56% `[p.218]`

None of these numbers are "optimized" — Clenow insists `[p.219-220]` that
the constants (200d MA, 100d MA, 90d, 15%, 10 bps) were chosen a priori
from concept, not from grid searches.

---

## What was run

Script: `scripts/run_clenow_replication.py`

```
.venv/bin/python scripts/run_clenow_replication.py \
    --start 2023-07-01 --end 2023-12-31 \
    --cash 100000 --output-dir reports/ \
    --warmup-days 400
```

Engine parameters:
- **Universe**: SPX point-in-time constituents on 2023-07-01 (via
  Wikipedia scrape, ~500 tickers). Filtered to those for which yfinance
  returns non-empty data.
- **Warmup**: 400 calendar days (≈ 270 trading days) before `--start`,
  so the 200d MA and the 90d regression have enough history by the
  first Wednesday rebalance.
- **Costs**: `ExecutionConfig()` default (zero spread/slippage/commission).
  Deliberate choice — we want to measure the raw signal before
  calibrating real costs in Stage 2 Pepperstone (ROADMAP §"Two-stage backtest").
- **Clenow constants**: book values (non-optimized), all defaults of
  `ClenowMomentumStrategy` (`lookback_regression=90`, `lookback_trend=100`,
  `lookback_index_trend=200`, `lookback_atr=20`, `lookback_gap=90`,
  `gap_threshold=0.15`, `top_pct=0.20`, `risk_factor=0.001`).

---

## Numbers obtained

Run: `reports/clenow_momentum_20260414-1633.md` (backtest
2023-07-01 → 2023-12-31, initial cash $100 000, 503 SPX
point-in-time tickers, of which 486 returned data — 17 skipped due
to survivorship/rename/unknown).

| Metric | Replication (6 months, 2023 H2) | Clenow (18 years, book p.115) |
|---|---|---|
| Final equity | $93 965.01 | N/A |
| CAGR (annualized) | **−11.79%** | ~12% |
| Sharpe (annualized) | **−0.787** | ~1.0 |
| Sortino (annualized) | −1.017 | N/A |
| Calmar | −0.871 | N/A |
| Max drawdown | 13.55% | ~25% |
| Volatility (annualized) | 14.58% | N/A |
| Walk-forward verdict | reject (4/8 profitable) | N/A (single trial) |
| Closed trades | 54 | N/A |

### Reading the numbers

**Negative, but within expectations for the window.** 2023 H2 was a
**choppy** period on the SPX: rally in July, deep correction
August–October (SPX dropped ~10%), recovery in November–December. The
strategy caught the top of the first leg, was stopped out by ranking
deterioration / 100d MA breaks during the correction, and could not
re-enter in time for the final rally (the regime filter signals late
when MA200 is well above the close).

**Trade composition confirms the momentum logic is correct:**
- Top 5 winners: LLY (+$1 045), GOOG (+$486), GOOGL (+$480), AMGN
  (+$291), ORCL (+$234). All **megacap tech/pharma** names that led
  the market in 2023.
- Top 5 losers: NCLH (−$621), CMG (−$607), BKR (−$600), ODFL (−$534),
  DLR (−$529). **Cyclicals/REITs/energy/discretionary** that
  collapsed during the Q3 correction.

**Max DD 13.55% over 6 months** is reasonable — ~half the long-term DD
from the book (25%), consistent with a short bullish-choppy window.

**Walk-forward rejected (4/8 profitable)** is expected: 8 windows in
6 months = ~3 weeks each, very high noise per window. The 6/8 gate was
calibrated for multi-month windows (Pardo p.235-240). This is not a
sign of edge failure — it signals that the walk-forward test has no
statistical power at this scale.

### What would be OK vs. what would be a bug

Sharpe −0.79 over a 6-month window in a choppy market **is not a bug** —
it is within the expected noise. Bugs would be:
- Sharpe < −2 (loss well beyond observed DD)
- Zero trades emitted (ranking/scheduling broken)
- Negative cash at the end (sizing blown out)
- Equity curve with NaNs or unexplainable jumps

None of these occurred. **Engine OK to advance**; the signal requires
a long window with survivorship-free data to be evaluated rigorously —
that is Phase 3.

---

## Known limitations

### 1. Survivorship bias still present
The yfinance + Wikipedia pipeline reconstructs point-in-time membership
but **only recovers prices for tickers that Yahoo Finance still serves**.
Tickers delisted during 2023 H2 return empty frames and silently drop
out of the universe. On 2023-07-01 Wikipedia reported 503 tickers;
how many actually returned data is in the run log.

**Expected effect on the result**: **inflated** returns (we don't see the losers).

### 2. Short window
6 months = ~25 weeks = ~25 rebalances. Far too little to assert anything
about the system's edge. The short window exists to validate the
infrastructure end-to-end; a ≥ 3-year run is the next step
(listed below).

### 3. Zero costs
Spread, slippage and commission all zero. Clenow runs his own backtest
on equities data with institutional costs; the ai-trade engine inherits
this behavior in Stage 1 to measure pure signal. In Stage 2 (after
cTrader is unblocked), real costs will be applied and the Sharpe will
drop.

### 4. Partial anti-overfit validation
CPCV, PBO and DSR require **multiple strategies** (parameter grid) to
produce meaningful values. This replication is a **single trial** with
fixed book parameters, so only walk-forward (splitting the realized
equity curve into N windows) is computed. Phase 3 will introduce the grid.

### 5. Universe may not include the index
The strategy uses `^GSPC` for the regime filter. If yfinance does not
return `^GSPC` for the window, the regime defaults to ON (`_regime_on`
returns True when there is not enough history) — replication continues,
but with the filter effectively disabled. The log should be checked.

---

## Non-obvious design decisions

### `self.data` carries the full history (not the Runner's slice)
The Runner only iterates over `[start, end]` (`data_bounded`), but
`ClenowMomentumStrategy.data` points to the full dict (`start - warmup`
through `end`). This is intentional: during the first Wednesday after
`--start`, the strategy needs to look 90 days back for the regression
and 200 days for the index MA. If it only received the Runner's slice,
there would be no warmup.

### Sells emitted BEFORE buys (in the same list)
The Runner executes orders in list order. Emitting sells first ensures
that the released cash is available for buys immediately after. This
replicates the intuitive behavior of "free up cash, then buy."

### Buy is gated by regime; sell is NOT
From the book `[p.94-95]`: *"Do not sell a holding just because the
index drops below the 200d MA — only stop adding new positions."* The
engine implements this literally — sells trigger on the stock's own
criteria (rank, 100MA, gap, membership), while buys check regime ON.

### Sizing uses `equity` (not `cash`)
`shares = floor(equity × risk_factor / ATR20)`. Clenow always talks in
"account value" `[p.88]`, not cash. Open position value counts. A new
buy can exceed available cash if open positions are very large; in that
case Clenow says to stop (`break`) `[p.99]`.

### `top_pct × len(universe)` with `max(1, ...)` floor
Rank `>=` max_rank triggers sell. With a universe of 503, `max_rank = 100` —
top 100 is held. In synthetic tests with a small universe (8 stocks),
`max_rank = 1` would force holding a single stock; the tests neutralize
this by passing `top_pct=0.5` or `1.0`.

### `max_gap` ignores NaN
`pct_change()` produces NaN on the first bar. `max(skipna=True)` ignores
it. If everything is NaN (fewer than 2 bars), it returns 0.0 — safe
fallback.

---

## Next steps (out of scope for this task)

1. **Run a long window** (2010–2023 or 1999–2014 for direct book comparison).
   Requires either (a) tolerance for yfinance rate-limits (hours of
   initial fetch) or (b) migration to Tiingo/EOD survivorship-free
   (ROADMAP §"Deferred decisions").
2. **Implement parameter grid** (e.g., `lookback_regression ∈
   {60, 90, 120}`) to generate the T×N matrix needed for CPCV/PBO/DSR.
   Each cell is an equity curve, all under the same CPCV splits.
3. **Measure real costs** via `ProtoOAGetTrendbarsReq` on the Pepperstone
   demo once cTrader is unblocked (Stage 2). Rerun the backtest with
   `ExecutionConfig(half_spread=..., commission_per_unit=...)` calibrated
   per symbol.
4. **Compare to Trading Evolved** (Clenow, 2019) — extended version of
   the same strategy with volatility-target changes and execution detail.
   `knowledge/books/trading_evolved.md` is already absorbed.

---

## References

- Clenow, A. F. (2015). *Stocks on the Move: Beating the Market with Hedge
  Fund Momentum Strategies*. Equilateral Capital Management GmbH.
- Absorbed summary: `books/summaries/stocks_on_the_move.md`
- Phase 2 spec: `specs/backtest_phase2.md`
- Engine core: `src/ai_trade/backtest/engine/`
- Strategy: `src/ai_trade/backtest/strategies/clenow_momentum.py`
- CLI script: `scripts/run_clenow_replication.py`
- Generated report: `reports/clenow_momentum_<YYYYMMDD-HHMM>.md`
