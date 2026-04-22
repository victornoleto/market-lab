# Lead D2 — MA regime filter homogeneous (Gayed canonical) (aggregate)

**Phase:** phase3_5d | **Lead:** D2 | **Status:** DEAD END (0/3 PASS)
**Period:** 2010-02-11 → 2026-04-17 (16.2y, reference_prices.parquet Stage-1 + yfinance Stage-2)
**Tested:** 3 tickers × 6 configs = 18 runs
**Aggregation iter:** 6

## Summary

The Gayed canonical MA regime filter `[leverage_for_the_long_run, p.13, p.16]` applied to all
three target portfolios — TQQQ (3× QQQ), UPRO (3× SPY), and EW 50/50 UPRO+TQQQ — failed to
pass all five overfit gates on any ticker. The consistent blocker is the `Sharpe_net > 0.8`
gate: the best configuration (`sma200_gld`) achieves Sharpe_net 0.773–0.780 on the two
stronger portfolios, failing by 0.020–0.027.

The near-miss pattern is systematic: `sma200_gld` achieves 8/9 gate passes on TQQQ and
EW_UPRO_TQQQ — seven of eight WF windows pass (7/8), PBO is 0.115–0.119 (well below 0.5),
DSR_p is 0.010–0.029 (well below 0.05), and forward-window stress Sharpe is positive (+0.26
to +0.38). The sole structural blockers are (a) Sharpe_net 0.020–0.027 below threshold on
TQQQ/EW portfolios, and (b) UPRO failing both Sharpe_net (0.686) and Calmar (0.458).

Three structural findings from D2:

1. **TQQQ > UPRO everywhere** — QQQ (NASDAQ-100) at 3× leverage produces materially higher
   risk-adjusted returns than SPY (S&P 500) at 3× across all 18 runs. UPRO is the weaker
   asset unconditionally over this 16-year window.

2. **GLD off-leg > cash >> TMF** — Gold as off-regime refuge dominates. TMF (3× long bonds)
   produced catastrophic drawdowns of -82% to -87% in 2022 due to the rate-hike cycle
   `[leverage_for_the_long_run, p.60]`. TMF is permanently out of the D-series off-leg
   candidates.

3. **Sharpe_net gap is tax-drag, not signal weakness** — The 15% IR BR flat tax converts
   gross Sharpe ~0.918 (TQQQ sma200_gld) to net Sharpe ~0.780. The regime filter is
   operating correctly (MaxDD reduced from ~73% B&H to 53–60%), but the tax drag creates
   a persistent ~0.12 Sharpe penalty that narrows the margin below the 0.800 gate.

**Verdict:** DEAD END for D2 as specified. The MA regime architecture (SMA200/EMA100 on
SPY/QQQ → 3× LETF + GLD off-leg) is structurally sound but cannot clear the 0.800
net-Sharpe gate. Next lead: **D3 Donchian breakout** on TQQQ — a different entry mechanism
that may compensate for the tax drag through higher gross Sharpe or better timing efficiency.

## Cross-ticker table

| Ticker | Best config | Sharpe IS | Sharpe_net | CAGR_net% | MaxDD% | Calmar | OOS_S | FWD_S | WF | PBO | DSR_p | Beat_SPY | Calmar>0.5 | Sharpe_net>0.8 | PASS |
|--------|-------------|-----------|------------|-----------|--------|--------|-------|-------|----|-----|-------|----------|-----------|----------------|------|
| TQQQ | sma200_gld | 0.918 | 0.780 | 31.16 | -60.3 | 0.608 | 1.31 | +0.38 | 7/8 | 0.115 | 0.010 | ✓ | ✓ | ✗ | **NO** |
| EW_UPRO_TQQQ | sma200_gld | 0.909 | 0.773 | 26.74 | -56.3 | 0.559 | 1.28 | +0.26 | 7/8 | 0.119 | 0.011 | ✓ | ✓ | ✗ | **NO** |
| UPRO | sma200_gld | 0.807 | 0.686 | 20.70 | -53.2 | 0.458 | 1.16 | +0.11 | 7/8 | 0.115 | 0.029 | ✓ | ✗ | ✗ | **NO** |

**SPY B&H reference (same window):** CAGR 12.22%, CAGR_net 10.38%, Sharpe 0.756, MaxDD -34.1%

## All-config cross-ticker summary (sma200_gld vs runner-ups)

| Config | TQQQ Sharpe_net | EW Sharpe_net | UPRO Sharpe_net | Pattern |
|--------|----------------|---------------|-----------------|---------|
| sma200_gld | **0.780** | **0.773** | **0.686** | Best across all tickers |
| ema100_gld | 0.726 | 0.731 | 0.656 | Second best; EMA100 slightly worse |
| sma200_cash | 0.700 | 0.680 | 0.582 | Baseline regime; ~0.08 below sma200_gld |
| ema100_cash | 0.664 | 0.650 | 0.561 | Weakest non-TMF variant |
| sma200_tmf | 0.581 | 0.544 | 0.434 | TMF off-leg: structural fail |
| ema100_tmf | 0.576 | 0.522 | 0.397 | TMF: worst across all tickers |

## Citations

- `[leverage_for_the_long_run, p.13]` — SMA200 on broad index as canonical regime indicator
- `[leverage_for_the_long_run, p.16]` — EMA as alternative regime indicator (tested here as EMA100)
- `[leverage_for_the_long_run, p.60]` — Bond tail risk in leveraged portfolios; off-leg asset selection
- `[advances_fin_ml, p.208-211]` — PBO gate (combinatorial purged cross-validation)
- `[advances_fin_ml, p.298-299]` — DSR gate (probabilistic Sharpe ratio)

## Links

- Per-ticker reports:
  - `reports/phase_3_5d/d2_ma_regime_gayed/EW_UPRO_TQQQ.md`
  - `reports/phase_3_5d/d2_ma_regime_gayed/TQQQ.md`
  - `reports/phase_3_5d/d2_ma_regime_gayed/UPRO.md`
- Registry: `reports/phase_3_5d/d2_ma_regime_gayed/registry.json`
- Jornada: `jornada/2026-04-21/02-d2-ma-regime-gayed-aggregate-dead.md`
