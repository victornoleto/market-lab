# Iteration 024 — Cross-cluster GLD+GDX (gold ETF + gold-miners ETF) 60/40 RSI(2)+SMA(200) basket

## Hypothesis

A 60/40 basket of GLD (spot gold ETF) and GDX (gold-miners ETF), where each
leg fires the iter 003 Connors RSI(2)<5 + SMA(5) exit + SMA(200) trend-filter
mean-reversion signal **independently**, exploits the partial **cross-cluster**
diversification between bullion and miners. GDX has a documented stock-market
beta (S&P 500 ρ ≈ 0.45) absent from spot gold, so miner-side oversold dips
fire on a partially-different macro driver (joint equity-stress + gold-price
move) than gold-side dips. If true, the basket position vector should
de-correlate from iter 003's pure-gold signal substantially more than
iter 023's GLD+SLV (which closed at IC-6 rolling-60d 96.8%, GS-23). Expected
target: rolling-60d exceed-frac ≤ 80% on PRIMARY, basket Sharpe lift ≥ +0.05
over iter 003 alone.

This is the explicit GS-23 priority-1 candidate: "every winner was multi-asset"
re-interpreted to require **cross-cluster** (gold+equity-bridge) diversification,
not within-cluster (gold+silver, both precious metals). Miners are the
closest cross-cluster bridge that still has a meaningful gold-loading.

## Primary citation

`[risk_parity, ch.7]` — multi-asset basket weighting and the principle that
heterogeneous risk drivers diversify when their factor exposures differ.
Gold (real-rates, USD, safe-haven) vs gold miners (gold-price + equity-beta
+ idiosyncratic operational/credit risk) are explicitly different exposure
profiles even within the broader "precious metals" theme.

## Additional citations

- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5 + SMA(200)
  trend-filter mean-reversion signal; SMA(200) regime gate `[p.106]`
- `[ilmanen_expected_returns, ch.10]` — gold complex (bullion vs miners)
  as separate factor exposures; gold-mining equities load on equity factor
  with a gold-leveraged residual
- `[advances_fin_ml, p.31-34]` — cost-realistic backtesting (cross-lib parity)
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 24 (this iter)
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low > 0 gate
- IC-6 `[sister loop iter 014/019]` — rolling-correlation pre-val mandatory

## Edge source

Spot gold buy-hold captures the metal's drift; miner ETF buy-hold captures
gold drift × miner leverage − operational/credit drag. A basket where each
leg fires its own RSI(2)+SMA(200) MR signal selectively enters only on
pullback days, skipping low-information drift bars; if equity-stress days
co-trigger GDX's RSI(2) without triggering GLD's, the basket entry timing
has additional information vs the pure-gold MR signal.

## Datasets

- **PRIMARY** `gld_gdx_basket_long` (60% GLD + 40% GDX daily, joint
  2006-05-22 → 2026-04-15, ~19.9y, ~5 010 bars). Long history covers
  2008 GFC, 2011 gold peak, 2013-2018 stagnation, 2019+ revival,
  2020 COVID, 2022 inflation/Ukraine, 2023+ all-time highs — full
  regime spectrum.
- **CORROBORATING** `xau_gdx_basket` (60% XAUUSD spot + 40% GDX daily,
  joint 2020-01-02 → 2026-04-15, ~6.3y, ~1 580 bars). Different regime
  + uses XAUUSD spot (the actual Pepperstone instrument) instead of
  GLD ETF. Lighter gate bar — `G6 bootstrap CI low > 0` + `G2 DSR p < 0.20`.

## Timeframes used

`["1d"]` — daily closing price for both legs. No 1h / 4h needed; basket
RSI(2) MR signals work cleanly on daily bars (per iter 003 / iter 023).

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (primary deploy track A).

- Track A applicability: GLD/GDX are both US ETFs; on Pepperstone the
  natural CFD instrument for gold is XAUUSD spot (used in corroborating
  via xau leg); GDX as a US-equity CFD is Pepperstone-supported but
  with a different cost/spread profile. For the BACKTEST, we treat the
  primary basket as a hypothetical "long ETF" basket with conservative
  CFD-like cost model, and the corroborating as "spot gold + miner
  ETF CFD" cost model:
  - Gold leg cost: 8 bps RT spread (Pepperstone XAUUSD CFD baseline)
  - GDX leg cost: 12 bps RT spread (US-equity CFD typical; ~1.5x gold's
    spread due to wider miner ETF bid-ask vs spot gold)
  - Swap: −1 bps/night per long, weekend 3x (same model as iter 023
    gold leg; conservative for both)
- Track B (Inter ETF) applicability: GLD + GDX both available on Inter
  Internacional. Long-only fits this strategy (RSI MR is long-only).
  T+1 settlement is OK since holds are 4-15 days. **Track B not
  scored in this iter — declared as "future Track B candidate"**;
  primary track is pepperstone_cfd to mirror iter 023's protocol.

## Hold-time profile (HARD GATE)

- Expected mean hold (per leg, per RSI(2)+SMA(200) signal): 4-7 trading
  days based on iter 003 / iter 023 priors
- Track: **`short_swing` (2-10 trading days)** — same as iter 023
- If basket mean hold falls outside [2, 10]: tier downgraded to NEAR_FAIL
  per spec (declaration mismatch is process bug, not strategy result)

Rationale: each leg's RSI(2)<5 condition typically clears within 4-6
days as RSI mean-reverts upward; basket-level "any leg in" mean hold is
expected ~4-5 days. Definitely not intraday (no sub-1d signals); not
medium_swing (RSI(2) is a 2-period oscillator, not a multi-week filter).

## Pre-validation screen (mandatory for overlay candidates per IC-6)

This iter is NOT an overlay (iter 023 also wasn't). It's a basket
*aggregation* of two single-asset signals with structurally
**identical mechanism per leg** — the IC-6 concern is whether the basket
position vector fires on near-identical days as the iter 003 single-asset
signal. We measure this **post-hoc** (rolling-60d ρ on PRIMARY) as part
of the kill battery, mirroring iter 023's audit:

- Computed: rolling-60d Pearson correlation of (basket_net_pnl,
  iter003_gld_long_net_pnl) over the joint window
- Threshold: exceed-frac > 80% (**relaxed from iter 023's 95% bar
  given cross-cluster expectation**) → kill #3 fires
- Explicitly: if GDX RSI(2) and GLD RSI(2) co-fire > 80% of the time on
  rolling 60-bar windows, then GDX leg adds nothing → cross-cluster
  hypothesis falsified

Static IC-6 ρ also computed; expected static ρ_basket_vs_iter003
~0.55-0.65 (basket is 60% gold so retains heavy gold loading).

## Kill criteria (pre-committed before backtest)

If ANY of the following fires at the end of testing, the cross-cluster
basket hypothesis is **falsified** regardless of secondary metrics:

1. **#1 Primary basket Sharpe < 0.30** — i.e., basket fails to even
   match iter 003 alone (Sharpe +0.30 on gld_long). If basket Sh < 0.30,
   the GDX leg actively drags the strategy (miner equity-beta dominates
   the gold-MR edge).
2. **#2 Sharpe lift vs iter 003 < +0.05** — basket must add at least
   +0.05 Sharpe over iter 003 alone, or the basket aggregation is
   not a genuine alpha source (just risk redistribution).
3. **#3 IC-6 rolling-60d ρ vs iter 003 > 80% on PRIMARY** — silver-leg
   equivalent miner-leg fires same days as gold leg, cross-cluster
   hypothesis falsified per GS-23 logic.
4. **#3b IC-6 rolling-60d ρ vs iter 011 > 30% on PRIMARY** — basket
   inadvertently rides vol-regime signal (GS-22 family).
5. **#4 G6 Bootstrap 99.9% CI low ≤ 0** on PRIMARY — Sharpe is not
   significantly distinguishable from zero.
6. **#5 PRIMARY DSR p > 0.30** — strategy fails badly even on relaxed
   significance test (DSR_n_trials=24 deflator is meaningful here).
7. **#6 Mean basket hold ∉ [2, 10]** — hold-time bucket mismatch;
   declaration was wrong, downgrade to NEAR_FAIL.

If kills 1, 2, AND 3 all fire (basket Sharpe weak + no lift + high
co-trigger): **cross-cluster basket extension family CLOSES** (GS-24).
This would be a major dead-end — it would mean miners aren't structurally
different enough from gold for basket aggregation to add edge, and
cross-cluster diversification would need to look at genuinely orthogonal
clusters (BTC, bonds — priorities 4 and 5).

## Cost model (per leg)

**Track A — Pepperstone CFD-equivalent**:
- Gold leg (GLD): 8 bps RT spread, −1 bps/night swap on long, weekend 3x
- GDX leg: 12 bps RT spread (US-equity CFD typical), −1 bps/night swap on
  long, weekend 3x. Conservative (Pepperstone US-equity CFDs typical
  spread is 5-15 bps RT depending on liquidity; GDX is liquid)
- Mean hold ~5 days × −1 bps/night × 0.6/0.4 weight basket = ~−3 bps
  per trade swap drag
- Round-trip transaction cost per round-trip basket trade: ~12 bps
  weighted (0.6×8 + 0.4×12 = 9.6 bps, plus swap drag)

Per-trade economics: target signal gross > 10 bps to be net-positive
after costs. RSI(2) MR on gold has ~50-100 bps gross per trade (per
iter 003 priors), so cost overhead is acceptable.

## Expected budget

- Configs to test: **1** (single pre-committed cfg, mirrors iter 023;
  no Bonferroni grid sweep — IC-8 closure mandatory single-cfg)
- Wall-time: ~3-5 minutes (iter 023 took ~2 min; this iter slightly
  longer due to fetching GDX via Tiingo HTTP on first run, but GDX
  is now cached so no API call)
- Files to create: `iterations/024-*/{hypothesis.md, run_backtest.py,
  results.json, verdict.json, final_report.md, test_basket_signal.py}`
- Files to modify: `BASE_MEMORY.md` (iter log, top-K, candidates,
  cumulative_n_trials, latest_iteration), `DEAD_ENDS.md` (append
  GS-24 if cross-cluster fails or pivots family closure), GDX added
  to Tiingo cache (already done as Stage-1 prep)

## Implementation plan

1. **Reuse iter 023's `run_backtest.py` engine** — copy as the iter 024
   base and substitute:
   - Asset key `silver` → `gdx`
   - Path `data/tiingo/daily/prices/SLV.parquet` → `GDX.parquet`
   - Path `data/tiingo/daily/prices/xagusd.parquet` → corroborating
     uses XAUUSD + GDX (no XAU silver)
   - Spread RT: silver 20 bps → GDX 12 bps
   - Dataset names: `gld_slv_basket_long` → `gld_gdx_basket_long`,
     `xau_xag_basket` → `xau_gdx_basket`
   - Weights stay 60/40 (GLD/GDX, with GLD ≥ 40% per universe rule)
2. **Reuse `cost_models.py`** unchanged (same Pepperstone model)
3. **Reuse `scoring.py`** v2 unchanged
4. **TDD**: write `test_basket_signal.py` mirroring iter 023's test,
   substituting GDX for SLV; verify per-leg signal correctness on
   synthetic data + smoke test on real GLD+GDX joint window
5. **Run backtest**: `python run_backtest.py` → produces `results.json`
6. **Compute kill criteria** (in-script, mirrors iter 023 logic with
   relaxed kill #3 threshold 80% vs 95%)
7. **Score with `score_strategy_v2()`**: declare primary
   `gld_gdx_basket_long`, corroborating `["xau_gdx_basket"]`
8. **Hold-time gate**: bucket = short_swing [2, 10]
9. **Write `verdict.json`**, `final_report.md` (honest verdict)
10. **Update `BASE_MEMORY.md`**: bump `total_iterations=24`,
    `cumulative_n_trials=24`, append iter log entry, refresh top-K,
    refresh "Promising unexplored directions" (consume priority 1,
    promote next candidates), append GS-24 1-line if structural
    closure
11. **Append GS-24 full text to `DEAD_ENDS.md`** if cross-cluster basket
    extension closes; otherwise note "still open" and document edge
    profile measured

## Cross-lib G7

The basket aggregation engine in iter 023's `cross_lib_check_basket()`
is reused unchanged — same numpy-only re-implementation with leg-specific
spread + swap. Cross-lib parity check applies identically.

## Why this is structurally different from iter 023

| dimension | iter 023 (GLD+SLV) | iter 024 (GLD+GDX) |
|---|---|---|
| 2nd-leg asset class | precious metal (silver) | gold-mining equity ETF |
| 2nd-leg macro driver | same as gold (real rates, USD, safe-haven) | **gold-price + equity-beta + idiosyncratic** |
| Expected static ρ vs iter 003 | +0.71 (basket=60% gold) | ~0.55-0.65 (lower due to GDX equity beta) |
| Expected rolling-60d exceed-frac | 96.8% (measured) | < 80% (hypothesis) |
| Cluster | within-precious-metals | **cross-cluster (PM + equity bridge)** |
| Sister-loop precedent | within-cluster (CLOSED iter 023) | cross-cluster (NEVER tested) |

If GLD+GDX rolling exceed-frac comes in close to GLD+SLV's 96.8%,
that would mean miners aren't structurally different enough from gold
for basket aggregation — a non-trivial finding closing **all
"PM-adjacent equity" cross-cluster paths**. If it comes in materially
lower (say 70-80%) AND basket Sharpe lift > +0.05, this iter **breaks the
GS-23 ceiling and provides the first cross-cluster validation** —
unblocking 4 (GLD+BTC), 5 (GLD+TLT), and the broader cross-cluster
direction.

## Track B (Inter ETF) — declared not scored

GLD and GDX are both US ETFs available on Inter Internacional. The
strategy is long-only per leg (RSI MR), so Track B applicability is
trivially YES. T+1 settlement is fine for 4-7 day mean holds. The
DARF 15% drag would convert basket Sharpe by approximately:
`Sh_after_DARF ≈ Sh_pretax × (1 − 0.15 × win_month_frac)`. Not modeled
here; future iter can run Track B independently if Track A passes.
