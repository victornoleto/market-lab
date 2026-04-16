# Grid run `grid_chan_pairs_20260415-2109` — Diagnostic

**Verdict:** FAIL — pair not cointegrated on 1h timeframe (gate upstream of backtest).

## Configuration

- Strategy: `ChanBollingerPairsStrategy` (Phase 2.5, first intraday entry).
- Pair: GLD (long) / SLV (short).
- Window: 2022-04-15 → 2026-04-15 (4 years).
- Data: Tiingo IEX 1h, 6258 bars after inner-join on overlapping timestamps.
- Cash: $100,000.
- Configs: 4 (2 × 2 grid: `lookback_multiplier ∈ {1, 2}` × `entry_z ∈ {1.0, 1.5}`).
- Walk-forward: not evaluated (no OK trials).
- Gates: not evaluated (no OK trials).

## Trial outcomes

| config_id | lookback_mult | entry_z | status | error |
|-----------|---------------|---------|--------|-------|
| 0 | 1 | 1.0 | error | t_stat_OU=-2.956 > -3.4 (half_life=55) |
| 1 | 1 | 1.5 | error | t_stat_OU=-2.956 > -3.4 (half_life=55) |
| 2 | 2 | 1.0 | error | t_stat_OU=-2.956 > -3.4 (half_life=55) |
| 3 | 2 | 1.5 | error | t_stat_OU=-2.956 > -3.4 (half_life=55) |

(Note: cfg_id 0 from the first dry-run smoke against [2023-01-01, 2024-12-31] reported t_stat_OU=-2.145, half_life=98. Both windows fail the cointegration gate.)

## Diagnosis

The cointegration gate fires at strategy construction time, **before** any
bar is processed:

```
src/ai_trade/backtest/strategies/chan_bollinger_pairs.py:189
RuntimeError: pair not cointegrated on training slice:
  t_stat_OU=-2.956 > -3.4 (half_life would be 55)
```

The OU regression on the spread `S = log(GLD) - β · log(SLV)` (β fit by OLS
two-ordering per `[algo_trading_chan, p.54, ch.2]`) gives a half-life of 55
bars (≈8.5 trading days at 6.5h/day) **but** the OU mean-reversion t-stat
is only -2.956, above the -3.4 critical value used as the cointegration
gate. The half-life is in the acceptable [4, 60] range, but the
mean-reversion *strength* (t-stat) is insufficient to call the spread
cointegrated.

Practical reading:
- GLD-SLV co-move (correlation high) but the spread is not strongly
  mean-reverting on the 1h timeframe over this 4-year window.
- The 2022-2024 silver squeeze + 2023-2026 gold rally to all-time-highs
  decoupled the structural ratio enough that OU mean-reversion strength
  drops below the gate.

## Hooks (per spec §7)

This is the "no genuine cointegration" outcome. Closest spec hook is **§7.5
FAIL v1 por MCPT** — but the gate is *upstream* of MCPT (we never reached
permutation testing because no trial produced an equity curve).

Chan's warning `[algo_trading_chan, p.88-89, ch.4]` — that pair-trading
edge is unreliable for unrelated stocks — extends to ETFs on intraday
timeframes too.

Per spec §7.5: **pivot to the next intraday catalogue item — volatility
breakouts** `[volatility_trading]` Sinclair.

## Counters reported by trial

- `pct_exited_by`: not produced (no trades).
- `median_hold_hours`: not produced.
- `max_hold_hours`: not produced.
- `pct_trades_overnight`: not produced.

## Reports infra notes

- `DiagnosticAnalyzer.analyze()` raises `ValueError("grid has no OK trials
  — cannot compute best_config")` when all trials erred. This means the
  CLI runner never wrote a report under `reports/<run_id>/` in this case;
  this `diagnostic.md` was written manually to capture the verdict. Future
  improvement: have `DiagnosticAnalyzer` return a degenerate diagnostic
  when 100% of trials erred at construction time (gate-upstream fail).

## Citations

- OU half-life regression and cointegration t-stat gate:
  `[algo_trading_chan, p.47-48, ch.2]`
- β via OLS two-ordering: `[algo_trading_chan, p.54, ch.2]`
- Pair-trading reliability warning: `[algo_trading_chan, p.88-89, ch.4]`
- Pivot to volatility-breakouts on intraday-pairs failure:
  `[volatility_trading]` (Sinclair), spec §7.5.
