# Phase 6C — Walk-Forward Forensics (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Run order note:** the Phase 6 round executes 6C → 6B → 6D → 6A (directory
> names sort differently; this file is the authority on order).

## Question

Phase 4 closed the LRS family with the walk-forward gate (G3) as the universal
binding failure: every base beats the underlying after-tax in *most* rolling
~3-year OOS windows, but never in ≥75% of them (SPY best `12/17` = 70.6%). This
phase asks **which** windows fail and **in what regime**, to decide whether the
miss is structural (timing always loses in calm bull markets, where a leveraged
buy-and-hold is unbeatable) or scattered (no pattern → noise / fragility)
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.211-216]`.

Pre-registered headline question: **do ≥2/3 of the failing windows fall in the
`bull × low-vol` regime cell?** If yes, the failure mode is the structurally
expected one — trend-timing pays its premium exactly when there is no downside
regime for the SMA to dodge `[leverage_for_the_long_run, p.7-8]` — which informs
Phase 6A's satellite framing. If no, the edge is regime-incoherent and the
family stays closed with stronger evidence. Either way this is report-only; no
pass/fail promotion, no reopening of the standalone line.

## Design (fixed before running)

- **Bases:** the exact 6 Phase 4 bases (`spy_top`, `spy_lower_lev`,
  `spy_alt_off`, `qqq_top`, `qqq_lower_lev`, `qqq_alt_vol`), each at its
  committed best-score lag (`phase04.best_lag_for_base`). No new configs —
  **+0 rows to the n_trials ledger** (cumulative lineage stays 3876).
- **Walk-forward splits:** identical to Phase 4 — `is=1764d / oos=756d /
  step=756d` over the aligned after-tax strategy/underlying pair, via the
  canonical `market_lab.backtest.validation.walk_forward_splits`
  `[testing_tuning, p.318-320]`.
- **Per-window row (the canonical per-window artifact Phase 4 never persisted):**
  OOS start/end dates, strategy OOS total return, underlying OOS total return,
  relative return, `beat` flag, strategy and underlying OOS MDD, mean annualized
  RV21 of the underlying inside the window, % of risk-on days (base signal =
  SMA200 & vol gate), and two regime labels.
- **Regime labels (pre-registered, descriptive only — not tradable signals):**
  - `regime_trend`: `bull` if the underlying after-tax total return in the OOS
    window is > 0, else `bear` — the sign convention of the window itself.
  - `regime_vol`: mean contemporaneous RV21 (annualized, `ddof=0`, same
    estimator family as Phase 2) cut at **<15% = low, 15–25% = mid, ≥25% =
    high**. Cuts anchored on the leverage-trap reading that high realized vol
    degrades leveraged compounding `[leverage_for_the_long_run, p.4-7]`,
    `[volatility_trading, p.39, p.53-54]`.
- **Output:** `lrs/results/phase06c_wf_forensics.csv` — one row per
  base × window (3×17 SPY + 3×11 QQQ = 84 rows), plus a regime-cell
  beat-rate table in the report.

## Plots

- Per-window relative-return bars per base, colored by regime cell, failing
  windows outlined.
- Scatter of window mean RV21 vs relative return.
- Base × window beat/fail heatmap with OOS start dates.

## Non-goals

No new strategy variants, no parameter search, no gate re-runs (PBO/DSR/etc.),
no mandate claims. Phase 4's verdict (family closed, 0/6) stands regardless of
what this forensic shows.
