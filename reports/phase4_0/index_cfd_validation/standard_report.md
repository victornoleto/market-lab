# Phase 4.0 T3 — Index CFD substitution backtest

**Status:** ✅ PASS T3 sanity gates
**Date:** 2026-04-20
**Window:** 2001-05-14 → 2026-04-14 (6266 bars)

## Substitution map

| Backtest label | V2-L2 share CFD data | Phase 4.0 Index CFD substitute |
|---|---|---|
| SPY | SPY `close` Tiingo parquet | SPX TR stitched (KF + SPY TR) |
| QQQ | QQQ `close` Tiingo parquet | QQQ `adj_close` Tiingo (≈ NDX TR) |
| gld | GLD `close` Tiingo parquet | GLD `adj_close` Tiingo (proxy for XAUUSD; XAUUSD data insufficient pre-2020) |

## Cost model comparison

| Parameter | V2-L2 (share CFD) | Phase 4.0 (Index CFD) | Rationale |
|---|---:|---:|---|
| spread_half_bps | 2.0 | 5.0 | Index CFD spread wider in bps |
| commission_round_trip_bps | 6.6 | 0.0 | Razor Index typically commission-free (pending T1) |
| slippage_bps_round_trip | 3.0 | 3.0 | Same |
| swap_daily_pct_long | -0.005 | -0.008 | Slightly worse (futures-basis drag) |

## Split metrics

| Split | Sharpe (this) | Sharpe (V2-L2) | CAGR (this) | CAGR (V2-L2) | MDD (this) | MDD (V2-L2) |
|---|---:|---:|---:|---:|---:|---:|
| IS | 1.860 | 1.856 | 54.26% | 53.42% | -22.61% | -22.67% |
| OOS | **2.400** | 2.285 | **85.76%** | 79.14% | **-21.51%** | -21.02% |
| FWD | 1.797 | 1.821 | 58.56% | 59.28% | -17.93% | -17.35% |

## T3 sanity gates

| Gate | Threshold | Observed | Pass |
|---|---:|---:|:--:|
| OOS Sharpe | ≥ 2.0 | 2.400 | ✅ |
| OOS CAGR | ≥ 60% | 85.76% | ✅ |
| OOS MDD | ≤ -25% | -21.51% | ✅ |
| WF 8-window profitable + max-DD | ≥ 6/8 + ≤ 25% | 1.000, 22.61% | ✅ |

**Overall T3 verdict: ✅ PASS.** Proceed to T4 (full gates battery).

## Switch behaviour comparison

- Total switches: **584** (V2-L2 baseline: 616)
- By ticker: {'SPY': 281, 'QQQ': 303}
- Median hold days: **5.00** (V2-L2 baseline: 6.0)
- Cum. transaction cost: **114.01%** (V2-L2: 125.8%)
- Cum. overnight swap: **-73.30%** (V2-L2: -44.93%)

## Known caveats

1. **GLD used as proxy for XAUUSD.** XAUUSD parquet starts 2020-01-02 (insufficient for V2 window). GLD inherits the silent-cash pre-2004 caveat from V2-L2 (14% of bars treated as 0% return when GLD data unavailable). Post-2004 behavior is authentic.
2. **Cost model assumes Razor Index commission-free.** Pending T1 empirical validation in live Pepperstone demo account. If T1 reveals commission > 0, T3 must be re-run.
3. **Dividend adjustment assumed perfect.** SPX TR and QQQ adj_close both include dividend reinvestment. If Pepperstone's Index CFD dividend-adjustment haircut is material (< 95%), actual live CAGR will be lower than this backtest.
4. **No PBO/DSR cross-config test here.** T3 is single-config; T4 runs bootstrap 99.9% CI + walk-forward as primary robustness gates (PBO/DSR trivialize at n_trials=1).
