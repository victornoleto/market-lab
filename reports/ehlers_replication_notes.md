# Ehlers Band-Pass Swing Trader — replication notes

Replication baseline for the **Fase 2.5 Execução 2** Ehlers Band-Pass
Swing strategy. Single-instrument run on `^GSPC` daily from Yahoo Finance
before launching the 24-config grid. Purpose: catch engine-level bugs
while still on known ground, and set sensible expectations for the grid.

All rules/parameters cited verbatim against
`knowledge/books/cycle_analytics.md` (Ehlers, *Cycle Analytics for
Traders*, 2013) — primary source of record for this execution.

## Configuration (literature defaults)

| Parameter     | Value | Source |
|---------------|-------|--------|
| `hp_period`   | 48    | Text example [p.77, ch.7] (Code Listing 7-3 default is 80 — 48 preferred for the roofing filter alone) |
| `lp_period`   | 10    | Universal SuperSmoother cutoff [p.36, ch.3] |
| `pct_of_dcp`  | 0.90  | Tuning rule for 60° phase lead [p.152-153, ch.11] |
| `bandwidth`   | 0.30  | "Relatively good compromise" [p.53, ch.5] |
| `stop_pct`    | 0.05  | Mid-range of 2-5% for stocks [p.225-226, ch.17] |
| `upper/lower` | ±0.70 | Anticipatory thresholds combined with AGC-normalised BPF as oscillator [p.220-221, ch.17] |

`risk_pct_of_equity = 0.95` — single-instrument swing trader deploys near
full equity per trade. Engine supports fractional share sizes.

## Run — `^GSPC` 2022-01-01 → 2023-12-31

```
.venv/bin/python scripts/run_ehlers_replication.py \
    --start 2022-01-01 --end 2023-12-31 \
    --cash 100000 --output-dir reports/ --warmup-days 500
```

| Metric                  | Value      |
|-------------------------|------------|
| Initial cash            | $100,000   |
| Final equity            | $97,472    |
| Cumulative return       | **−2.53%** |
| Trades (round-trips)    | 27         |
| Fills                   | 54         |
| Walk-forward (8 windows)| 3/8 profitable, max DD 6.51% → **reject** |

- **Report:** `reports/ehlers_bp_swing_20260414-1931.md` (gitignored —
  numbers materialised here).
- **Equity PNG:** `reports/assets/ehlers_bp_swing_20260414-1931.png`.

## Interpretation

1. **Engine is correct.** The strategy emits orders, Runner fills them,
   Portfolio accounts P&L, report renders. No silent failure. Equity
   neither zeroes nor runs away. ~27 round-trips is a reasonable swing
   cadence for 2 years of daily SPX (≈ 1 trade / 3 weeks).

2. **Signal is weak — but not absent.** −2.5% over 2 years vs SPY's
   ~0% total return in that window is a small underperformance; Sharpe
   is effectively indistinguishable from zero on this sample.
   Max drawdown 6.5% is materially lower than SPY's (-25% intra-2022)
   — the strategy does a competent job of stepping out of the worst
   drawdowns via the safety-valve trend break.

3. **Walk-forward verdict: reject.** 3/8 windows profitable falls below
   the rule #5 gate of ≥6/8. This is expected on a single trial without
   parameter search — the 24-config grid (Commit 9) is where we stress-
   test against `PBO < 0.5 AND DSR p < 0.05 AND WF ≥ 6/8`.

4. **Book-vs-paper fidelity.** Ehlers applied the Band-Pass Swing
   system to EUR/USD (H1), T-Bonds, and currencies in [ch.19, p.236+];
   he does not claim edge on equity indices. The −2.53% cumulative on
   SPX daily is consistent with the *a priori* risk that the system is
   tuned for faster, more persistently cyclic instruments than a
   broad-market equity index. This is one of the documented risks in
   `specs/backtest_phase2_5_ehlers.md` §"Riscos conhecidos" (bullet 1).

## Synthetic pure-sine counter-test

A separate integration test (`tests/test_ehlers_integration.py`) runs
the strategy on a noise-free 1500-bar 20-period sinusoid with amplitude
5 on a baseline of 100. In that regime the strategy *loses* significant
equity because:

* Anticipatory entries fire on the way down (crossing below −0.7),
  not at the cycle bottom — the strategy is consistently early.
* With `risk_pct_of_equity = 0.95` and `stop_pct = 0.05`, each stopped
  trade costs ~4.75% of equity. A handful of whipsaws quickly compound.

Pure sinusoids are not a model of real market behaviour (they have
zero noise and a constant period); real ^GSPC performed closer to
flat (−2.5%) because real cycles are evanescent and the roofing
filter correctly attenuates the dominant trend noise. The synthetic
regression therefore reports a guardrail only ("equity nonzero and
bounded") rather than a profitability claim.

## Decision: proceed to grid

The engine check passes on both synthetic and real data. We advance to
`Commit 9 — scripts/run_grid_ehlers.py` to run the full 24-config grid
over the same 2015-2023 SPX window used by the Clenow Execução 1,
enabling direct comparability.

If the grid also rejects (PBO ≥ 0.5 or DSR p ≥ 0.05), the fork in
`specs/backtest_phase2_5_ehlers.md` §Task 5 offers four branches:
paid-data ablation, 3rd strategy (AFML / Chan), regime-aware combination
with Clenow, or stop.

> ⚠️ **Survivorship bias warning.** `^GSPC` is an index price — less
> affected by single-constituent survivorship than individual-stock
> backtests (Execução 1), but the index itself is maintained with
> continuous-constituent weighting that still tilts the series. The
> auto-generated report carries the standard `yfinance` disclaimer.
