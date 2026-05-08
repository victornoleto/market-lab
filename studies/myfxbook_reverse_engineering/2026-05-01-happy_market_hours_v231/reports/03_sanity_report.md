# Sanity report — Happy Market Hours v2.3.1 (id 1407880)

Generated: 2026-05-01

## Counts
- Trades (Buy/Sell): **3305**
- Deposits: 95
- Per symbol: {'GBPUSD': 898, 'USDCAD': 808, 'EURUSD': 703, 'EURCHF': 370, 'USDCHF': 287, 'EURGBP': 239}
- Per action: {'Sell': 1712, 'Buy': 1593}

## Temporal coverage
- First trade open: `2013-09-02 00:00:00+00:00`
- Last trade close: `2021-06-16 00:48:18+00:00`
- Max gap between trades: **33.9 days**
- Gaps > 30d: 1
  - after `2015-09-18 01:12:00+00:00`: gap 33.9d

## Lot sizing distribution (full sample)
- P50: **3.76** | P95: **15.16** | P99: **16.65** | max: **17.05**
- P95/P50 ratio: **4.03** (informational — reflects 8-yr equity growth, not martingale)
- Cross-check via 03b_lot_dynamics.py: per-month max/median P95 = 1.06 → no within-month doubling

## Martingale-sequence detection
- Trades flagged as 'next-after-loss with lot >= 1.7× prev': **0** (0.0% of all)
- Max consecutive doubling streak: 0 trades
- Streaks of 3+ doubling trades: 0

## Hold time (hours)
- P50: **1.02h** | P95: **3.20h** | P99: **4.80h** | max: **8.60h**

## K1 kill-switch verdict
### ✅ K1 PASS — proceed to P2 EDA
- Doubling-after-loss (sameday window): 0 (threshold: < 5% of 3305)
- Max consecutive doubling streak: 0 trades (threshold: < 5)
- Streaks of 3+ doubling trades: 0 (threshold: < 5)
- Lot P95/P50 = 4.03 but per-month ratio = 1.06 → equity scaling, not martingale