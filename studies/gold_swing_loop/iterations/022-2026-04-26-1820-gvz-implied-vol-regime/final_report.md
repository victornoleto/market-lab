# Iteration 022 — Final Report

## Verdict

📉 **NEAR_FAIL** — score **28/100**, `winner_conditions_met=false`,
`hold_time_gate_pass=true` (mean hold 24.6d ∈ medium_swing 10-30d).

3 of 4 pre-committed kill criteria fired:

- ❌ **Kill #2** — primary DSR p = **0.608** > 0.30 threshold.
- ❌ **Kill #3** — IC-6 rolling-60d ρ vs iter 011 (`vol_regime_inverse`)
  on PRIMARY = **59.7%**, vs 30% threshold. **GVZ implied-vol z-score
  is a vol-regime family re-skin of iter 011's σ_60/σ_252 ratio**.
- ❌ **Kill #4** — primary G6 bootstrap 99.9% CI low = **−0.47** (failed).
- ✅ Kill #1 NOT fired — primary Sharpe = +0.246 (just above the +0.20
  threshold, but materially weak).

## Headline metrics (top candidate, NET of Pepperstone Track A costs)

| dataset | Sharpe (sliced bench Δ) | CAGR (bench Δ) | MDD | gates | mean hold | DSR p |
|---|---|---|---|---|---|---|
| gld_long (PRIMARY, sliced 2009-06-04→2026-04-15, 16.83y) | +0.246 (Δ −0.383 vs 0.629) | +1.54% (Δ −7.92%) | 30.85% | 4/7 | 24.6d | 0.608 |
| xauusd_real (CORROBORATING, 6.29y) | +0.333 (Δ −0.706 vs 1.038) | +1.75% (Δ −18.18%) | 12.93% | 4/7 | 25.9d | 0.662 |

Gates passed per dataset: G1_PBO ✓ G2_DSR ✗ G3_WF ✗ G4_OOS ✓ G5_FWD ✓
G6_boot ✗ G7_crosslib ✓ (4/7 on both datasets, identical pattern).

Cross-lib G7 ±3pp parity check: gld CAGR pandas=0.015438 vs numpy=0.015438
(diff < 1e-6 — clean parity); xau identical. Engine clean.

## Score breakdown (rules_version `2026-04-26-relaxed-r1`)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 5 | 25 | primary Δ −0.44 (full bench) → 0pts; corroborating Sharpe +0.33 > 0 → +5 |
| 2 Gates | 8 | 25 | primary 4/7 < threshold 5/7, but ≥ th−1 → +8; corroborating G6 fail + G2 p=0.66 fails relaxed (p<0.20) → 0 |
| 3 DSR | 0 | 15 | primary p=0.608 ≫ 0.20 → 0 |
| 4 CAGR floor | 0 | 15 | primary CAGR 1.5% < 0.8 × 11.32% = 9.05% → fail |
| 5 MDD ceiling | 15 | 15 | primary MDD 30.85% ≤ 45.55% + 5pp = 50.55% → pass |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **28** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | pass | — | mean hold 24.6d ∈ medium_swing 10-30d ✓ |

## Configuration tested

```python
cfg_id = "gvz_zscore_long_zentry_neg1_zexit_zero_window252d_lag1d_max30d"
z_entry_below = -1.0      # enter LONG when GVZ z < −1.0σ (cheap implied vol)
z_exit_above  = 0.0       # exit when z > 0 (vol normalizes)
window_days   = 252       # 1-year rolling z-score
lag_days      = 1         # use yesterday's GVZ to avoid lookahead
max_hold_days = 30        # cap at medium_swing upper bound
spread_bps_rt = 8.0       # Pepperstone Track A
swap_bps_per_calendar_night = 1.0
track = "pepperstone_cfd", universe = "single_xau", hold_time_track = "medium_swing"
declared_primary = "gld_long", declared_corroborating = ["xauusd_real"]
primary_slice_start = "2009-06-04"  # 252-day warmup from GVZ inception 2008-06-03
```

Cumulative `n_trials = 22` (was 21 after iter 021).

## What worked / what didn't

**The mechanism is real but small.** GVZ z<−1 entries do produce
positive raw Sharpe on both datasets (gld +0.246, xau +0.333) and tight
MDDs (12.9-30.8% vs 45.6-22% benchmarks). The state-machine generates
sensible mean holds (24-26d) and the long-only contrarian thesis is
directionally correct — gold tends to rally during periods of IV
expansion that follow IV exhaustion. OOS slice (last 30%) Sharpe is
**+0.31 on gld_long and +1.82 on xauusd_real**, which is materially
better than the full-sample number — the strategy has improved post-2018
gold regime.

**But it doesn't survive the IC-6 orthogonality test.** GVZ implied vol
and σ_60/σ_252 realized-vol ratio are measuring the same underlying
phenomenon at the position-vector level on gold. Rolling-60d ρ between
iter 022 and iter 011 net returns is **59.7% on gld_long primary** —
nearly double the 30% IC-6 threshold. Static ρ is +0.55. This is the
core finding: option-implied vol (forward-looking, options market
participants) and realized-vol-ratio (backward-looking, price-derived)
trigger long entries on essentially the same gold periods. The
"forward-looking" framing was theoretically appealing but empirically the
two signals fire on overlapping regimes.

**Why DSR fails hard at p=0.608**: standalone Sharpe +0.246 is below the
DSR-deflator threshold for `n_trials=22`. The deflated-Sharpe required
to clear p<0.05 at 22 trials over ~17 years is approximately +0.65 — the
GVZ standalone Sharpe is 38% of that. Even at the better OOS slice
(+0.31), the strategy is far from significance.

**Why bootstrap CI fails at −0.47**: 1000-sample bootstrap of the
17-year daily return series has a fat lower tail (the strategy's positive
return is concentrated in a handful of vol-cheap → vol-pickup episodes —
2009, 2011, 2018, 2019, 2024). At α=0.001 the lower bound captures
"what if those few good episodes hadn't happened" — and the answer is
heavily negative.

## Main lesson (for future iterations)

★ **GS-22**: GVZ implied-vol z-score gate (252d window, z<−1 entry, z>0
exit, lag=1d, max_hold=30d) on gold spot, post-2009 (1y warmup): primary
gld_long Sh +0.246 (Δ −0.38), corroborating xau Sh +0.333. **IC-6
rolling-60d ρ vs iter 011 (vol_regime_inverse) = 59.7% on PRIMARY**
(static ρ = +0.55). Closes the **option-implied vol family on gold as a
structurally novel direction — it is the same family as realized
vol-regime (iter 011/013) at the position-vector level**, just measured
from option premia instead of price returns. The forward-looking
framing was theoretically appealing (Sinclair `[volatility_trading,
p.32-37]`, Bollerslev-Tauchen-Zhou 2009 RFS) but on gold the IV and
realized-vol cycles ride the same macro clock during low-vol windows,
fire entries on overlapping regimes, and produce position vectors with
60% rolling correlation. Closes also the "GVZ as IC-7 secondary" path
on the iter 011 base — it would be near-redundant.

**Does NOT close**: GVZ as IC-7 secondary on iter 003 (RSI(2)+SMA200) —
ρ vs iter 003 is +0.08 static / 10% rolling, comfortably orthogonal.
But standalone GVZ Sharpe +0.246 is too weak to be a meaningful 2nd
stream (combined ceiling with iter 003's Sh +0.30 = √(0.30² + 0.246²) =
0.388, well below the DSR-deflator-cleared 0.65). Not productive.

## Structural dead-ends discovered

GS-22 added below to DEAD_ENDS.md and BASE_MEMORY's "Structural
dead-ends" section. Pattern matches GS-14 (TIPS DFII10 ρ=+0.52 vs iter
011) and GS-15 (DXY-MA-slope ρ=+0.51 vs iter 014) — yet another macro/
vol family stream that ostensibly looks orthogonal but rides the same
gold-stress macro clock as the original vol-regime base.

## Citations used

- `[volatility_trading, p.32-37]` — Sinclair: implied-vol indices,
  variance-risk-premium framework, low-IV mean-reversion thesis (PRIMARY).
- `[trading_systems_methods, p.13-14]` — Kaufman: vol regime classifier.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials=22.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (Track A).
- CBOE GVZ methodology white paper — `https://www.cboe.com/us/indices/dashboard/gvz/`.
- Bollerslev, Tauchen, Zhou (2009) RFS — VRP-as-predictor framework.
- Web (FRED) — `GVZCLS` series 2008-06-03→2026-04-23 (4 503 daily obs).

## Next iteration suggestions

(Update for `## Promising unexplored directions` in BASE_MEMORY.)

1. **(NEW PRIORITY 1, PROMOTED) CME futures track A2 — re-test
   cost-dominated intraday MR** — iter 007 z-MR died at 8 bps RT
   spread. At CME GC futures 1-2 bps RT (per INFRASTRUCTURE.md A2),
   same z-MR is +1.5-2 bps net per trade — possibly intraday-MR-economic
   again. New cost-path branch (`cost_path: cme_futures`). After GS-22's
   negative result on options-implied-vol and GS-21's negative on COT
   speculator isolation, intraday on tighter cost path is the next
   genuinely structurally different mechanism.

2. **(NEW PRIORITY 2, PROMOTED) DCOT producer-merchant long-on-extreme-shorting** —
   hedger-side mechanical-bias mirror of iter 021 (currently priority 3).
   GS-21's finding that producer-hedging leverage in legacy commercials
   *adds* the edge means the hedger-side direct-bias trade may be the
   richest COT signal we haven't tested. Different mechanism than iter
   021 (it was contrarian to MM, this is mirror-of-producer-hedging).
   Data already cached.

3. **(NEW PRIORITY 3, PROMOTED) Multi-asset `gold_complex` universe
   extension** — extend known single-asset signal (iter 003 RSI MR) to
   gold-complex portfolio (60% XAU + 30% GDX + 10% XAG). Sister loop's
   evidence: every winner was multi-asset. Iters 016-022 all single_xau —
   relaxation freedom unused. May exit the single-asset Sharpe ceiling
   ≈ +0.55 (per GS-13/GS-14/GS-22). `[risk_parity, ch.7]`.

4. **gold risk-reversal skew (options)** — 25-delta gold call/put skew
   gate. Different option-derived signal than implied-level (which we
   just closed via GS-22). RR skew measures asymmetric option demand
   (call-bias vs put-bias) and may not collapse onto the realized-vol
   cycle the way absolute-IV does. `[volatility_trading]`. Caution:
   data acquisition non-trivial — would require a data infra iter to
   compute 25Δ skew from a CBOE option-chain history.

5. **(LOWER PRIORITY) Concede loop closure** if priorities 1-3 flat-line.
   PCBO/DSR with `n_trials=22` requires standalone Sh > 0.65 OR an
   IC-7 pair with both low static ρ AND stationary rolling-ρ AND
   strong-enough standalone Sharpes; none exhibited in 22 iterations
   on this single-asset XAU universe.
