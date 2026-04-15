# GLD / SLV 1h Tiingo Retention Probe

**Date:** 2026-04-15  
**Plan:** Chan Bollinger Pairs 1h implementation  
**Spec reference:** `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md` §1.3

## Command

```python
from datetime import date
from pathlib import Path
from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
end = date(2026, 4, 15)
start = date(2020, 4, 15)  # probe 6 years; Tiingo returns whatever it has

for ticker in ("GLD", "SLV"):
    df = src.fetch(ticker, start, end, frequency="1hour", asset_class="etf")
    if df.empty:
        print(f"{ticker}: EMPTY — abort")
        continue
    span = df.index.max() - df.index.min()
    print(f"{ticker}: {len(df)} bars, {df.index.min()} → {df.index.max()} (span {span.days}d)")
```

## Results

| Ticker | Bars | Start | End | Span (days) | Gate (≥1095d) |
|--------|------|-------|-----|------------|---|
| GLD | 9396 | 2020-04-15 14:00:00 | 2026-04-15 19:00:00 | **2191** | ✅ PASS |
| SLV | 9396 | 2020-04-15 14:00:00 | 2026-04-15 19:00:00 | **2191** | ✅ PASS |

## Gate Verdict

**PASS** — Both GLD and SLV have ≥3 years (1095 days) of 1h bars available in Tiingo storage.  
Both exactly 2191 days (exactly 6 years, as expected from 2020-04-15 probe date).

Proceeding to Chan Bollinger Pairs 1h strategy implementation.

## Notes

- TiingoSource lazy-cache hit for both tickers (no fresh API calls required; data was pre-cached from prior `tiingo_bulk` run).
- No gaps detected in the reported date ranges.
