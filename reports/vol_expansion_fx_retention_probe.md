# Vol-Expansion FX 1h retention probe — 2026-04-15

## FX (Bundle β candidates — FAILED)

- xauusd: 10307 bars total, BUT massive gap 2021-06-04 → 2025-01-01 (~3.5y). Two fragments: 2020-08-18→2021-06-04 (290d) + 2025-01-01→2026-04-15 (470d). Neither ≥ 3y. **INVIÁVEL.**
- eurusd: 15076 bars total, SAME gap 2021-06-04 → 2025-01-01. Fragments: 2020-04-15→2021-06-04 (415d) + 2025-01-01→2026-04-15 (470d). **INVIÁVEL.**

Root cause: Tiingo FX 1h data has a ~3.5y hole (mid-2021 → early-2025), likely subscription tier change.

## ETF (all verified ≥ 6y)

- SPY: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- GLD: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- SLV: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- QQQ: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- IWM: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- TLT: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- XLE: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- XLF: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- XLK: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- DIA: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- EEM: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅
- EFA: 9396 bars, 2020-04-15 → 2026-04-15, span 2191d ✅

## Decision

Bundle β (SPY + XAU/USD + EUR/USD) → **ABORT** (FX gap).
Bundle α (SPY + GLD + EUR/USD) → **ABORT** (EUR/USD same gap).

Pivot recomendado: **SPY + GLD + TLT** (ETF multi-asset class).
