# Sanity report — system 11504701

Generated: 2026-05-01

## Counts
- Trades (Buy/Sell): **314**
- Deposits: 1
- Per symbol: {'USDJPY': 103, 'GBPUSD': 96, 'EURUSD': 69, 'AUDUSD': 44, 'ARCHIV': 2}
- Per action: {'Buy': 172, 'Sell': 142}

## Temporal coverage
- First trade open: `2025-04-15 23:59:59+00:00`
- Last trade close: `2026-04-23 11:30:01+00:00`
- Max gap between trades: **14.5 days**
- No gaps > 30 days ✓

## Lot sizing distribution (full sample)
- P50: **nan** | P95: **nan** | P99: **nan** | max: **nan**
- P95/P50 ratio: **inf** (informational — long-sample ratio reflects equity scaling, not martingale)
- Per-month max/median P95: **nan** (threshold 3.0); max-month: nan

## Martingale-sequence detection
- Trades flagged as 'next-after-loss with lot >= 1.7× prev': **0** (0.0% of all)
- Max consecutive doubling streak: 0 trades
- Streaks of 3+ doubling trades: 0

## Hold time (hours)
- P50: **0.00h** | P95: **0.07h** | P99: **0.27h** | max: **0.55h**

## K1 kill-switch verdict
### ✅ K1 PASS — proceed to P2 EDA
- Doubling-after-loss (sameday window): 0 (threshold: < 5% of 314)
- Max consecutive doubling streak: 0 trades (threshold: < 5)
- Streaks of 3+ doubling trades: 0 (threshold: < 5)
- Lot P95/P50 = inf but per-month ratio = nan → equity scaling, not martingale

⚠ N trades = 314 < 500 → DSR/PBO unreliable `[advances_fin_ml, p.208-211]`