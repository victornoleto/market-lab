# 002-2026-05-09-on-vol-dd-killswitch — HYPOTHESIS

**Iter:** 002 / 50 (loop)
**Slug:** on-vol-dd-killswitch
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 432
**cumulative_n_trials_global after:** 438

## Hypothesis

Iter 001 established that the 2022_rates loss of the study winner
`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` is an ON-leg mistake — the
vote-of-K trend signal stayed ON during a slow grinding NDX bear (peak-to-trough
~75% on QLD) while neither SMA250 nor SMA100 nor vol21<40% nor AR(1)>0 fired
fast enough to derisk. OFF-leg modifications cannot rescue what is structurally
an ON-signal latency problem.

This iter tests a **vol-adjusted drawdown master-gate** (kill switch) overlaid
on top of the winner's vote-of-K signal. Mechanic: track QLD's drawdown from
its trailing 252-day rolling high; force the strategy OFF (regardless of
vote-of-K) when that drawdown exceeds **X × σ_price**, where σ_price is the
21-day realized vol scaled to price points (`sigma_price = price × σ_21d_annual
× sqrt(21/252)` ≈ 1-month σ in price points). The gate stays OFF until QLD
recovers within `0.5 × X × σ_price` of the rolling peak (re-arm hysteresis),
preventing whipsaw re-entry inside the same drawdown.

Economic intuition: vote-of-K is a slow trend gate (250d/100d MAs); a
vol-normalized drawdown is a *fast* loss-magnitude gate that responds to the
size of the drop in standard-deviation units, not to a slow average. In 2022,
QLD's drawdown crossed 4-5σ levels weeks before SMA100 confirmed the
breakdown. The gate complements vote-of-K rather than replacing it.

This is Carver's semi-automatic stop loss [systematic_trading, p.212 ch.13]
(`stop_level = tracking_extreme − X × σ_price_points`) re-purposed as a regime
gate on top of an existing trend system, rather than a single-trade stop.

**Primary citation:** `[systematic_trading, p.212 ch.13]` — Carver semi-automatic
stop loss using `X × sigma_price_points` from tracking extreme. X=4 is Carver's
recommended default (selected by turnover profile, not performance fit).

**Secondary citations:**
- `[trading_systems_methods, p.352-353]` — Kaufman trailing-stop family
  (initial-low + break-even-trail + 50%-of-peak-profit pattern).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (global denom).
- `[volatility_trading, p.39]` — VIX/realized vol mean-reversion (motivates
  why a 21d σ window is suitable as the kill-switch normalizer).

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` on QLD and the OFF asset ZROZ (winner replica). The
kill switch is OVERLAID on top: if it fires, the strategy goes OFF (ZROZ)
regardless of vote-of-K. If it doesn't fire, vote-of-K controls as usual.

Drawdown reference window = 252 trading days for the rolling peak (matches
SMA250 timescale used by the winner's trend signal; intentionally same horizon
to avoid introducing an orthogonal lookback hyperparam).

| # | Name | DD gate rule | X | DD basis |
|---|---|---|--:|---|
| 1 | `qld_voteK2_..._dd_off` | no kill switch (winner replica) | — | — |
| 2 | `qld_voteK2_..._dd_x2_252_vol21` | OFF if DD_252d > 2 × σ_price | 2 | vol-adjusted |
| 3 | `qld_voteK2_..._dd_x3_252_vol21` | OFF if DD_252d > 3 × σ_price | 3 | vol-adjusted |
| 4 | `qld_voteK2_..._dd_x4_252_vol21` | OFF if DD_252d > 4 × σ_price (Carver default) | 4 | vol-adjusted |
| 5 | `qld_voteK2_..._dd_x5_252_vol21` | OFF if DD_252d > 5 × σ_price | 5 | vol-adjusted |
| 6 | `qld_voteK2_..._dd_pct25_252` | OFF if DD_252d > 25% (absolute, sanity check) | 25% | absolute |

Configs 2-5 sweep one dimension only (X) per protocol §"Symmetric naming".
Config 1 is the no-gate baseline; config 6 swaps the gate basis to absolute %
as a robustness probe.

Hysteresis (re-arm rule, applied to all kill-switch configs): once OFF, the
gate stays OFF until QLD recovers within `0.5 × threshold` of the rolling peak
(half-recovery rule). For dd_pct25_252, re-arm at DD < 12.5%.

Signal lag (1-day) is preserved consistently with the winner: kill switch
computed at close of day t-1, applied at open of day t.

## Datasets

Mirrors closed-study set for direct comparability:
- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/ZROZSIM/CASHX)
- `modern_1990`: 1990-01-01 → 2026-04-30 (eliminates pre-1990 synth uncertainty)
- `spy_real`: 2003-01-01 → 2026-04-30 (real SPY post-inception)
- `ndx_real`: 2010-02-01 → 2026-04-30 (real QQQ post-inception)

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner test").
- **KILL_LOOP #2 (decisive-fail):** if all 5 kill-switch configs return
  Sortino_lh56y < 1.10 → vol-adjusted drawdown gate is a net negative across
  the entire X sweep; mark family dead and pivot next iter to a different
  ON-signal mechanic (e.g., regime classifier).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (baseline replica)
  Sortino_lh56y differs from 1.2841 (iter 001 replica baseline) by > 0.05
  absolute → engine drift; flag INCOMPLETE and trust comparative deltas
  across configs only. Note: 1.2841 (not 1.3246) is the relevant anchor
  because we share iter 001's data-loading path (warmup boundary differs by
  248 days from canonical iter 022).
- **KILL_LOOP #4 (whipsaw-detector):** if any config's annualized turnover
  exceeds the baseline by > 3× (i.e. kill switch fires too often), tag the
  config "WHIPSAW" in SUMMARY — informational only, doesn't change verdict.

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.10–1.40 across all 6 configs.
- **Best plausible scenario:** dd_x4 or dd_x5 gains ~0.03–0.08 Sortino over
  baseline by clipping the worst LETF drawdowns (Oct 2008, Mar 2020,
  end-2022) without firing too often during normal pullbacks. Looser
  thresholds (dd_x2, dd_x3) likely whipsaw; absolute % gate (config 6)
  unlikely to outperform vol-adjusted because it ignores regime.
- **Plausible failure mode:** all kill switches reduce Sortino because (a)
  LETF natural vol means even non-crisis pullbacks routinely cross 3-4σ
  drawdowns intra-decade, generating whipsaw; (b) by the time DD has crossed
  X*σ, the worst of the drawdown is often behind us (gate-AFTER-loss
  problem).
- **Most realistic outcome:** tier PROMISING with sortino_edge_vs_winner in
  [-0.05, +0.05] band — useful negative result if no config beats; useful
  positive result if dd_x4/x5 confirm Carver's framework can be redeployed
  as a regime gate.
- **WC compliance:** trend ON signal unchanged; pct_time_above_benchmark
  may dip slightly because the kill switch can force OFF during benign
  periods where vote-of-K is ON. Expect ≥ 0.97 if gate is well-calibrated;
  < 0.90 if kill switch is too aggressive.
- **Beats-winner probability:** **~10-15%**. Best plausible Sortino edge ~0.05
  pre-G1, but G1 PBO again likely structural-fail with single-axis 6-config
  sweep — same artifact as iter 001. WC failure on G1 would block
  beats_winner regardless of Sortino.

## INCOMPLETE flags / caveats

- **Synth caveat:** lh_56y pre-1985 uses formula-derived QLDSIM; the rolling
  peak / vol-adjusted drawdown signal will fire essentially never pre-1985
  (constant-price era), reducing the gate to inactive for ~15 years of the
  56-year window. Comparative deltas focus on 1985+ behavior.
- **Re-arm hysteresis is a hyperparam (0.5):** intentionally fixed at
  half-threshold to avoid introducing a second sweep dimension. A future iter
  could sweep the re-arm fraction (0.25, 0.5, 0.75, 1.0) but that's out of
  scope here (eligibility checklist §"single-axis variation").
- **Vol window 21d is fixed:** matches winner's vol_21d gate to keep the
  vol-normalization horizon consistent with the existing signal stack. Not
  swept here.
- **Tax/fees:** gross only this iter (matching study convention; net layer
  is monotonic shift downstream — doesn't affect rankings or `beats_winner`
  test).
- **Carver's X=4 chosen by turnover** [systematic_trading p.271]: not a
  performance fit. We deliberately sweep X to test whether his
  turnover-anchored choice generalizes to a regime-gate context.

## Beats-winner test (frozen per protocol §"Beats-winner test")

```python
beats_winner = (
    sortino_lh56y > 1.3746              # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met
    and pct_time_above_benchmark_lh56y >= 0.95
)
sortino_edge_vs_winner = sortino_lh56y - 1.3246
```

`winner_benchmark_sortino = 1.3246`, `winner_benchmark_iter =
"022-2026-05-06-T3d-extended-grid"`, `winner_benchmark_config =
"qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"`.
