# Iteration 015 — DXY SMA-slope falling regime gate, gold long-only (FRED DTWEXBGS)

## Hypothesis

Gold rallies persistently when the broad trade-weighted USD index is in
a sustained falling regime — not at the *moment* USD turns weak (GS-5
closed that), but during the persistent multi-month phase where the
*200-day moving average itself* keeps drifting down. Operationalize as:
LONG gold when `SMA_200(DXY)[t] < SMA_200(DXY)[t - 20]`, else flat.
Pre-committed single config (lookback `sma_window=200, slope_lookback=20`)
per IC-8.

## Primary citation

`[stocks_on_the_move, p.100]` — Clenow's canonical 200-day SMA as the
trend-regime filter; rare-bull / persistent-trend logic translates to
"trade gold's bull regime when its macro-cause (USD weakness) itself is
in 200d trend".

## Additional citations

- `[trading_systems_methods, p.13-14]` — Kaufman: gold/USD inverse
  coupling as canonical macro driver for metals.
- `[ilmanen_expected_returns, ch.10]` — gold as USD-cycle hedge / safe
  haven; cited by iter 005 GS-5 as escape route for trend-continuation
  framings of FX-derived signals.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
  (Pepperstone XAUUSD spread + swap baked into all metrics).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative_n_trials = 15.
- DEAD_ENDS GS-5 — explicitly leaves trend-continuation FX framings
  open: "DXY-based signals on longer-history data sourced from FRED
  (DTWEXBGS or DTWEXM)" + "trend-continuation framings (e.g., 'long
  gold when DXY 60-d EMA negative slope')" are NOT closed.
- DEAD_ENDS GS-14 — corollary test: same-macro-clock = rate-specific or
  macro-generic? FX cycles vs real-rate cycles.
- IC-7 (sister 045/046) — ρ < 0.40 vs iter 011 unlocks DSR uplift.
- IC-8 — single pre-committed cfg; deflator already at 14 → 15.
- Web — Pukthuanthong & Roll (2011) "Gold and the Dollar: Hedge,
  Haven, or Neither?" *J Banking Finance* 35(11): 2876-2892. Empirical
  inverse relationship strongest during persistent USD downtrends, not
  intermittent weakness.
- Web — Capie, Mills & Wood (2005) "Gold as a Hedge against the
  Dollar." *J Int Fin Markets, Inst & Money* 15(4): 343-352. ~30y data
  showing gold-USD long-run hedge mechanics.

## Edge source

Gold buy-hold captures the asset's full long-term drift but holds during
USD-strengthening drawdowns (e.g., 2013-2018 −44% gold drawdown
coincides with broad USD up-trend). The DXY 200d-MA-falling gate
**filters out** those drawdown-prone phases by going flat → MDD reduction
without sacrificing the bull-regime upside (when USD weakens
persistently, gold rallies). The hypothesized edge is captured almost
entirely on **MDD ceiling and risk-adjusted return**, not raw CAGR.

## Datasets

- **gld_long** (GLD daily 2004-11-18 → 2026-04-15, 21.4y): primary
  long-history test. DTWEXBGS coverage starts 2006-01-02 → ~14-month
  warmup loss at series start, but still ~19.5y of post-warmup signal
  active period. Tests the macro-generic vs rate-specific corollary.
- **xauusd_real** (XAUUSD daily 2020-01-02 → 2026-04-17, 6.3y): full
  signal coverage; bull-only regime; cost-realistic.
- **xauusd_intraday** (XAUUSD 1h 2020-01-02 → 2026-04-17, 6.3y): same
  daily DXY signal forward-filled across 1h bars (no intraday DXY
  decision-making).

## Timeframes used

`1d` for the DXY signal; `1d` for GLD/XAUUSD daily datasets;
`1h` for xauusd_intraday (signal forward-filled). All required TFs
cached. No cTrader fetch needed.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (primary). Track B (Inter ETF) reported
informationally on daily datasets only — expected catastrophic on long
window per GS-2 (DARF + FX cliff erodes marginal edge).

## Hold-time profile (HARD GATE)

- Expected mean hold: **30-60 trading days** on daily datasets (200d-MA
  slope persists multi-month). On 1h dataset the same daily flag forward-
  filled gives ~750-1500 hours of continuous holding ≈ 30-60 daily-days.
- **swing-extended** tag — tier ceiling = STRONG (no WINNER possible).
- Justification: macro/USD cycle persistence is intrinsically multi-month;
  a slope-based regime gate cannot be "fast" without becoming noise (a
  daily-flip gate is exactly what GS-5 closed).

## Kill criteria (pre-committed)

1. **Pre-val auto-abort**: if pre-val gate fails on all 3 datasets
   (mu_active_bps_per_bar ≤ 0 OR p_active ∉ [0.10, 0.90] OR n_flips < 5)
   → strategy is degenerate; no full backtest.
2. **Sharpe kill (any of)**:
   - `xauusd_intraday` (primary) Sharpe ≤ 0
   - 2+ of 3 datasets net-negative Sharpe after costs
3. **gld_long ceiling broken**: Sharpe < 0.30 on gld_long → DXY-trend
   family fails the long-window test entirely; close direction.
4. **Cross-dataset kill**: xauusd_real Δ < 0 AND xauusd_intraday Δ < 0
   → strategy has gld-only (long-window) edge structure, not robust
   across windows.
5. **n_trades collapse**: gld_long n_trades < 5 → signal too sparse to
   characterize statistically.
6. **IC-7 boundary check** (informational): if ρ vs iter 011 on gld_long
   ≥ +0.50 the corollary test confirms macro-generic same-clock failure
   (parallel to GS-14); IC-7 composition path on gld_long stays closed.
   If ρ < +0.40 on any dataset, IC-7 path opens for that dataset.

## Pre-validation screen (mandatory IC-6)

Standard signal-sanity pre-val (mirrors iter 014):

- p_active ∈ [0.10, 0.90] (signal not degenerate)
- mu_active_bps_per_bar > 0 (signal carries positive bias when on)
- n_flips ≥ 5 (enough trades for statistical characterization)

3-dataset; if 0/3 pass → auto-abort.

In addition, an IC-7 ρ diagnostic vs iter 003, iter 011, iter 013 is
computed at backtest time (not pre-val) to test the macro-generic
corollary directly.

## Cost model (Track A primary)

Pepperstone XAUUSD CFD baseline:

- spread 8 bps round-trip
- swap long −1 bps/night (per night per lot; lot value $2100)
- swap short +0.3 bps/night (informational; this strategy is long-only)
- intraday: NOT applied (multi-month hold by design; weekend triple-swap
  eats ~3 nights × 1 bps = 3 bps every Fri close)

Track B (informational only, daily datasets):

- FX 100 bps round-trip
- DARF 15% on monthly net profits
- ETF EER netted from price (GLD 40 bps/y, IAU 25 bps/y)

## Expected budget

- Configs to test: **1** (per IC-8 single pre-committed cfg)
- Wall-time: ~10-15 min (signal + 3 backtests + bootstrap + WF + DSR)
- Files to create: hypothesis.md, run_backtest.py, pre_val.json,
  results.json, final_report.md, verdict.json
- Cumulative_n_trials after this iter: **15**

## Implementation plan

1. ✅ Cache FRED DTWEXBGS via `scripts/data_sprint/ingest_dtwexbgs_fred.py`
   (5087 daily bars 2006-01-02 → 2026-04-17).
2. ✅ Implement `src/ai_trade/backtest/strategies/dxy_trend_gold.py`
   with `dxy_sma_falling_flag` (pandas) + numpy parity reference.
3. ✅ TDD: 11 tests in `tests/test_dxy_trend_gold.py`; all pass.
4. Run backtest in `iterations/015-*/run_backtest.py` mirroring iter 014:
   - Stage 3a: pre-val per dataset
   - Stage 3b: full backtest, 7 gates, per-track metrics, per-trade
     attribution, IC-7 ρ diagnostic
   - Stage 4: scoring via `scoring.py`
   - Stage 5: final_report.md + verdict.json
5. Update `BASE_MEMORY.md` (iter log + frontmatter + top-K + dead-ends).
