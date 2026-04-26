# Iteration 004 — VIX recovery flight-to-quality drift, 5d hold (cross-asset risk-off entry)

## Hypothesis

Gold realizes a tactical safe-haven premium during the **recovery phase**
of equity-vol stress events (NOT during the stress event itself). The
canonical "VIX > 25 long gold" framing fails on short windows because
markets sell-everything (including gold) at the peak of stress; the
real flow comes after fear peaks and money rotates back into hard
assets while equities are still fragile.

Operationalized as an event-driven signal on daily VIX:

- Compute `vix_z = (VIX − rolling60_mean(VIX)) / rolling60_std(VIX)`
- **Trigger** at bar `t`: `vix_z[t] < +1.0` AND `vix_z[t-1] ≥ +1.0`
  AND `max(vix_z[t-30..t-1]) > +2.0`. Plain English: VIX z-score crosses
  *down* through +1 (recovery from elevated regime) AND there was a
  spike above +2σ in the last 30 days (qualifies the recovery as
  post-stress, not random noise).
- **Hold**: long gold (binary {0, 1}, no leverage) for exactly 5
  trading days from trigger.
- **Cooldown**: 10 days after exit before a new trigger is eligible
  (avoids back-to-back retriggers during sustained recovery).
- **Exit**: at `T+5` (fixed) or end of dataset.
- Long-only.

## Primary citation

`[leverage_for_the_long_run, p.13]` — Gayed's flight-to-quality framing
identifies VIX regimes where gold systematically outperforms equities
for the safe-haven premium reason. The "z down-cross from peak" trigger
is a documented refinement vs the simple "VIX > 25" gate; it isolates
the **recovery phase** of the regime (when capital rotates back to risk
assets but with a gold tilt for hedging).

## Additional citations

- `[ilmanen_expected_returns, ch.10]` — Gold as carry / safe-haven
  asset in the multi-asset risk-premia framework.
- Erb & Harvey 2006 "The Strategic and Tactical Value of Commodity
  Futures" *Financial Analysts Journal* 62(2), pp.69-97 — documents
  gold's post-stress drift premium (positive 1-month forward return
  conditional on equity-stress event resolution).
- Baur & Lucey 2010 "Is Gold a Hedge or a Safe Haven? An Analysis of
  Stocks, Bonds and Gold" *Financial Review* 45(2) — gold acts as a
  safe-haven *during* extreme stress; hedge property weaker
  in mid-recovery, hence the asymmetric "after the peak" timing.
- DEAD_ENDS GS-3 escape hatch #2 ("switch to fundamentally-different
  signal source") — VIX is the canonical cross-asset risk-off signal,
  structurally distinct from iter 003's gold-momentum-derived MR base.

## Edge source

XAUUSD buy-hold captures the secular long drift but does NOT
preferentially position-size during the post-equity-stress recovery
window when safe-haven flow is largest. This strategy isolates the
tactical premium associated with the down-cross of VIX z-score from
peak — buying at the moment fear is *receding* (not at the peak,
not at the calm baseline). Pre-validation on raw 5-day forward gold
returns (2004-2026 GLD): the post-recovery subset realizes
**+0.465 % avg 5-d fwd return** vs **+0.244 % unconditional** — i.e.
~+90 % per-event lift; ~4 events per year conditional on cooldown.

## Datasets

- **gld_long** (GLD daily 21.4 y, 2004-2026): long history, mixed
  regime (2008 GFC + 2011 Eurozone + 2018 Q4 + 2020 COVID + 2022
  inflation panic) — primary stat-power source.
- **xauusd_real** (XAUUSD daily 6.3 y, 2020-2026): cost-realistic
  instrument; covers COVID + 2022 + 2024 ATH cycles. Will sample
  fewer events (~25 trades over 6.3 y) but is the actual underlying.
- **xauusd_intraday** (XAUUSD 1 h 6.3 y): resampled to daily for this
  iter (signal is daily VIX, no intraday signal benefit). Reported
  for cross-dataset replication consistency with iter 003.

## Timeframes used

`1d` only. VIX is daily; gold daily-bar entry/exit is sufficient.
Intraday VIX would need cTrader feed (deferred to a separate
data-infra iter).

## Broker tracks targeted

`broker_track: "both"`.

- **Track A** (Pepperstone CFD): primary track. Long-only by
  construction so swap drag accrues over 5-day hold (~5 nights × −1
  bps = −5 bps per trade); spread 8 bps RT × 4 trades/yr ≈ 32 bps/yr;
  total cost drag ~50-60 bps/yr.
- **Track B** (Inter ETF): viable per GS-2 — strategy fires ~4 trades/yr,
  well below the 15 tr/yr cliff. FX RT 100 bps × 4 = 400 bps/yr drag,
  plus 15 % DARF on positive months. Will compute formally in the
  cost model; expected ~30-50 % CAGR drag vs Track A.

## Hold-time profile (HARD GATE)

- Mean hold: **5 trading days exactly** (by construction — fixed
  hold per trigger).
- Intraday-only: NO (multi-day swing).
- Hold-time gate: **PASS by design** (5 ≤ 5).
- Tier ceiling: WINNER attainable.

## Kill criteria (pre-committed)

If the strategy's Track-A Sharpe on `gld_long` (the highest-stat-power
dataset) is **below +0.10** in the live backtest, the hypothesis is
falsified — pre-val showed +0.465 % per-event 5-d edge but if cost
drag fully erodes that to zero or negative, the recovery-trade
framing is structurally identical to iter 003's MR base in *outcome*
(positive in-sample, near-zero out-of-cost) and the family is closed.

Specifically, kill if BOTH hold:
- `track_a_sharpe[gld_long] < 0.10` AND
- `n_datasets_with_track_a_sharpe_above_zero < 2` (i.e., at most 1
  of 3 datasets shows positive Track-A Sharpe).

## Pre-validation screen (IC-6 mandatory for overlay candidates)

Pre-val executed on 2026-04-26 (in `run_pre_val.py` notes; computed
inline here because it's a very small calculation):

| metric | value | interpretation |
|---|---:|---|
| `corr(vix_z, gold_vol_60d)`         | +0.006 | zero — IC-1 absorption N/A |
| `corr(vix_z, gold_daily_ret)`       | −0.021 | zero — different family |
| `corr(vix_z, gold_z_60d)`           | +0.070 | ~zero — different price-info source |
| 5-d fwd gold ret @ baseline         | +0.244 % | unconditional |
| 5-d fwd gold ret @ vix_z>2 spike    | +0.071 % | LOWER (anti-edge during peak) |
| 5-d fwd gold ret @ recovery cross   | **+0.465 %** | **+90 % vs baseline; the actual edge** |

IC-6 verdict: **pass** (signal correlations all ≪ 0.30, no
co-integration risk). IC-1 N/A (no vol-target wrapper). The pre-val
re-frames the entry timing from the original BASE_MEMORY direction #1
("vix_z > 2 long while elevated") to the cleaner recovery-cross
framing — same family, refined timing.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**:
- Spread 8 bps RT per trade × ~4 tr/yr = 32 bps/yr
- Swap −1 bps/night × ~5 nights/trade × ~4 trades/yr = ~20 bps/yr
- Estimated total drag: ~50 bps/yr
- Weekend hold multiplier: applied if T+5 spans Sat-Sun

**Track B (Inter ETF, GLD/IAU substitution)**:
- FX RT 100 bps × 4 = 400 bps/yr drag
- DARF 15 % on positive months, allocated to last bar of month
- ETF EER (40 bps/yr GLD, 25 bps/yr IAU) — implicit in NAV, not modelled here
- Expected post-tax CAGR ~50 % below Track A

## Expected budget

- Configs to test: **1** (single pre-committed cfg per IC-8: `z_peak=2.0,
  z_exit=1.0, peak_window=30, hold=5, cooldown=10`)
- Wall-time: ~3 min (vectorisable, single pass)
- Files to create:
  - `iterations/004-*/hypothesis.md` ✅
  - `iterations/004-*/run_backtest.py`
  - `iterations/004-*/results.json`, `verdict.json`, `final_report.md`
  - `tests/test_vix_recovery_signal.py` (TDD spec for the signal logic)

## Implementation plan

1. **TDD first**: write `tests/test_vix_recovery_signal.py` with toy
   VIX/gold series + asserted entry/exit pattern. Run pytest, confirm
   it fails (signal fn not implemented).
2. **Implement signal** (`vix_recovery_signal`) inside the iter dir's
   `run_backtest.py`. Mirror iter 003's structure: load → resample →
   signal → cost model A + B → metrics → 7 gates → score.
3. **Pre-load VIX**: `pd.read_parquet("data/external/macro/vix_daily.parquet")`
   relative to repo root; align with each price dataset's index.
4. **Apply cost models** Track A (`apply_pepperstone_costs`) and
   Track B (`apply_inter_costs_with_darf`); long-only by construction
   so Inter constraints satisfied automatically.
5. **Run gates** identical to iter 003:
   - G1 PBO: single-cfg degenerate → pass by convention
   - G2 DSR with `cumulative_n_trials=4` (3 prior + 1 this iter)
   - G3 Walk-forward 8 windows
   - G4 OOS 70/30
   - G5 FWD post-2022
   - G6 Bootstrap 99.9 % CI low > 0
   - G7 Cross-lib (numpy reference)
6. **Score** via `scoring.score_strategy()` + hold-time gate (= 5d by
   construction).
7. **Compute correlation** with iter 003's MR base position series
   (loaded from `iterations/003-*/results.json`) — needed for IC-7
   composition planning in iter 005.
8. **Write outputs** + **update memory** + **dead-end if applicable**.

## Status

DRAFT — implementation pending.
