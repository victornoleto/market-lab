# Iteration 021 — Final Report

## Verdict

📉 **NEAR_FAIL** (score **28/100**, winner_conditions_met=False,
hold_time_gate=PASS, **kill #1 (no standalone edge) AND kill #2 (DSR
no-progress) BOTH fired**; kill #3 (IC-7 ineligibility vs iter 003)
did NOT fire — surprisingly the MM contrarian signal IS structurally
orthogonal to iter 003 RSI MR but its standalone edge is too weak to
justify any further IC-7 work)

The DCOT money-manager net-long contrarian z-score (window=156w, lag=1w,
z<−1 entry, z>0 exit, max_hold=30d) was tested as a structurally
distinct refinement of iter 018's legacy commercials bucket. The
hypothesis was that isolating speculative flow (post-2006 disaggregated
MM bucket) from producer hedging (legacy commercials) would expose a
*cleaner* contrarian edge.

The result **falsifies** that hypothesis decisively:

- **gld_long primary** (sliced 2009-06-09 → 2026-04-15 post-warmup,
  16.82y / 4 240 daily bars): standalone Sharpe **+0.073** (vs sliced
  GLD bench Sharpe **0.639** → Δ **−0.566**). This is *worse* than
  iter 018's legacy commercials bucket (+0.352, Δ −0.43). Standalone
  CAGR +0.25%, MDD 30.2% (still better than bench MDD 45.6% by 15.4 pp,
  but the strategy spends most calendar time flat which deflates
  absolute return without a meaningful Sharpe).
- **xauusd_real corroborating** (2020-01-02 → 2026-04-17, 6.29y):
  Sharpe **+0.277**, CAGR +1.38%, MDD 15.6%. Positive but does not
  clear corroborating relaxed gates (G2 DSR p=0.71 > 0.20; G6 boot
  CI low = −0.69 < 0).
- **ρ static vs iter 018 commercials** = **+0.853** on gld_long,
  **+0.825** on xauusd_real. The two buckets give qualitatively
  similar contrarian-positioning signals on gold despite mechanistic
  difference.
- **ρ static vs iter 003 RSI MR** = **+0.023** on gld_long (rolling-60d
  exceed 2.2%). Money-manager bucket IS structurally orthogonal to
  price-MR — the hypothesis's secondary prediction holds — but the
  standalone Sharpe is too weak (+0.073) for IC-7 composition to be
  productive: √(S₀₀₃² + S_MM²) = √(0.299² + 0.073²) ≈ 0.31, BELOW
  iter 003's standalone +0.30. The combined would actually hurt.

GS-21 closure: **DCOT money-manager contrarian on gold is weaker than
legacy commercials contrarian** (Sh +0.073 vs +0.352, Δ −0.28 in MM's
disfavor). Producer-hedging leverage embedded in legacy commercials
appears to *add* the contrarian edge, not contaminate it. The
"speculative bucket isolation" hypothesis is FALSIFIED for gold.

## Headline metrics (NET of Pepperstone CFD costs, single cfg)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold |
|---|---|---|---|---|---|
| gld_long (PRIMARY, sliced 2009-06+) | **+0.073** (Δ **−0.566**) | +0.25% (Δ −9.4) | **30.2%** (Δ −15.4 ↓ better) | **4/7** | 27.48 d |
| xauusd_real (CORROBORATING)         | +0.277 (Δ −0.761) | +1.38% (Δ −18.5) | 15.6% (Δ −4.8 ↓ better) | 3/7 | 27.50 d |

Bench (re-measured on sliced post-warmup window 2009-06-09 → 2026-04-15):
- gld_long sliced: Sh **0.639**, CAGR 9.63%, MDD 45.6% (vs full-21y bench 0.684 — slightly worse Sharpe in this slice because 2004-2008 GFC rally is excluded)
- xauusd_real (full 6.29y, unsliced): Sh 1.038, CAGR 19.93%, MDD 20.36%

Per-dataset gate detail (gld_long PRIMARY, threshold ≥ 5/7):
- G1 PBO: PASS by IC-8 convention (single cfg, PBO degenerate)
- G2 DSR p = **0.836** (n_trials=21) → **FAIL**
- G3 Walk-Forward 6+/8 windows: only 2/8 pass → **FAIL**
- G4 OOS 70/30 Sharpe > 0 → PASS
- G5 FWD post-2022 Sharpe > 0 → PASS
- G6 Bootstrap 99.9% CI low > 0 → CI low = −0.597 → **FAIL**
- G7 Cross-lib ±3 pp CAGR → PASS
- **4/7 < threshold 5 → primary fails gate count**

Per-dataset gate detail (xauusd_real CORROBORATING, relaxed):
- G1 PASS, G2 p=0.71 > 0.20 → **FAIL relaxed**, G3 3/8 → FAIL, G4 PASS,
  G5 PASS, G6 boot=−0.69 → **FAIL relaxed**, G7 PASS — **3/7**
- Corroborating relaxed gate (G2 + G6 both pass): **FAIL** (both fail)

## Score breakdown (v2 scoring, rules_version=2026-04-26-relaxed-r1)

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 5 | 25 | primary not beat (Δ −0.566); corr Sh +0.277 > 0 → +5 |
| 2 Gates | 8 | 25 | primary 4/7 < threshold 5 but ≥ threshold−1 → +8; corroborating fails relaxed (G2+G6 both fail) → +0 |
| 3 DSR | 0 | 15 | primary p=0.836 > 0.20 → 0 |
| 4 CAGR floor | 0 | 15 | primary 0.25% < 0.8 × 9.63% = 7.7% → FAIL |
| 5 MDD ceiling | 15 | 15 | primary 30.2% ≤ 50.6% (bench + 5pp) → PASS |
| 6 Robustness bonus | 0 | 5 | not computed |
| **total** | **28** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | PASS | — | 27.48 d ∈ medium_swing [10, 30] |

## Configuration tested (single cfg, IC-8)

```yaml
cfg_id: dcot_mm_zscore_long_zentry_neg1_zexit_zero_window156w_lag1_max30d
signal: rolling_zscore(MM_NL, 156w) lagged 1w; LONG when z < -1.0; EXIT when z > 0 OR held >= 30d
data:
  source: CFTC DCOT futures-only Socrata 72hh-3qpy (gold code 088691)
  cache: data/external/macro/cftc_dcot_gold_weekly.parquet
  weekly_rows: 1037
  range: 2006-06-13 → 2026-04-21 (19.86y)
  bucket: m_money (long_all − short_all)
parameters:
  window_weeks: 156
  z_entry_below: -1.0
  z_exit_above: 0.0
  lag_weeks: 1
  max_hold_days: 30
cost_model:
  spread_bps_rt: 8.0
  swap_bps_per_calendar_night: 1.0
  track: pepperstone_cfd
universe: single_xau
hold_time_track: medium_swing
declared_primary: gld_long
declared_corroborating: [xauusd_real]
primary_slice_start: "2009-06-09"  # 156w warmup from DCOT 2006-06-13
```

Cumulative `n_trials` 20 → **21** (this iter increments by 1; IC-8
honored — single pre-committed cfg, no grid).

## What worked / what didn't

**Worked**:

1. **Structural orthogonality vs iter 003 confirmed**. Static ρ +0.023
   on gld_long (rolling-60d exceed 2.2%), +0.000 on xauusd_real
   (rolling 0.0%). DCOT MM contrarian and price-MR (RSI(2)+SMA(200))
   are nearly perfectly uncorrelated at daily granularity — IC-7
   eligible by both static and rolling metrics. *Useless* in this
   case because standalone Sharpe is too weak, but the structural
   property is validated for the COT family broadly (iter 018 had
   ρ +0.013 vs iter 003; this iter +0.023; both very low).
2. **DCOT data infra established**: 1037 weekly DCOT rows fetched
   from CFTC Socrata `72hh-3qpy` endpoint, cached to
   `data/external/macro/cftc_dcot_gold_weekly.parquet`. Schema
   validated (with the surprise that swap-short column has a double
   underscore typo: `swap__positions_short_all`). Available for any
   future iter that needs DCOT (producer-merchant, swap-dealer,
   other-reportables buckets all cached).
3. **TDD passed** (6 tests; all green): `mm_net_long`,
   `zscore_signal_long_when_z_below`, max-hold timeout, DCOT loader
   columns, rolling-z constant→0. Project pytest baseline unaffected
   (only iter-local tests added).
4. **MDD compression carried through**: gld_long 30.2% vs bench 45.6%
   (15.4 pp better) and xauusd_real 15.6% vs bench 20.4% (4.8 pp).
   Smaller compression than iter 018 (which had 25.3% gld_long), but
   this iter spends most time flat (Sh +0.07 means almost no signal
   activation — only 42 trades in 16.82y vs iter 018's ~80 in 21y).
5. **Hold-time bucket matches declaration**: 27.48 d ∈ medium_swing
   [10, 30] PASS. Same realized hold-time as iter 018 (28.4 d) — the
   `max_hold_days=30` cap dominates the realized distribution.

**Didn't work**:

1. **Standalone gld_long Sharpe = +0.073 ≪ iter 018's +0.352** (kill
   #1 fired). The MM bucket has materially LESS contrarian edge than
   the legacy commercials bucket on gold. Counter-intuitive at first
   pass, but consistent with the literature on commercials being a
   "smarter money" bucket precisely because they include producer
   hedgers who short physical they own (predictable, mechanical
   short bias) — iter 018's edge is partly the producer-hedging
   leverage, NOT a "contaminated" signal. Removing producer hedging
   removes the edge.
2. **DSR p=0.836** at n_trials=21 (kill #2 fired). Worst DSR p in the
   loop's history; the signal is so weak that even a 16.82y sample
   doesn't raise it above the deflator wall.
3. **G6 bootstrap CI low = −0.597** on gld_long. The 99.9% CI low for
   bootstrapped Sharpe is deeply negative — even at 1000 bootstrap
   resamples, the lowest-tail Sharpe is far below 0. Signal lacks
   robust positive expectation under sampling variation.
4. **WF 2/8 windows pass on gld_long**, 3/8 on xauusd_real. The
   per-window Sharpe is mostly negative across the 16.82y window
   sequence. The full-sample +0.073 is a fragile aggregate.
5. **ρ static vs iter 018 = +0.85**. The MM bucket and legacy
   commercials bucket give *qualitatively similar* signals on gold
   (both positioning indicators, both fire in roughly the same regime
   episodes). The structural difference between buckets is smaller
   than the bucket-vs-iter-003-RSI-MR difference (+0.85 vs +0.02).
6. **Score did not exceed iter 020's 35**. Four iterations now
   in the 28-35 NEAR_FAIL band (017/018/019/020/021). The COT family
   ceiling on gold — across all bucket choices and transforms tested
   — is decisively at Sh ≈ +0.35 standalone, far below the +0.65
   minimum required to clear DSR at n_trials=21+.

## Main lesson (for future iterations)

**GS-21 — DCOT money-manager contrarian z-score on gold is materially
WEAKER than legacy commercials contrarian z-score**: standalone gld_long
Sh **+0.073** (Δ −0.566 vs sliced bench) vs iter 018's commercials
+0.352 (Δ −0.43). The "speculative bucket isolation" hypothesis is
FALSIFIED on gold. Two structural insights:

1. **Producer-hedging leverage is the edge in legacy commercials, not
   the noise.** Legacy commercials bucket = producers + merchants +
   swap dealers + other-reportables-on-the-commercial-side. Producers
   short physical they own with predictable mechanical bias; isolating
   the speculator side via DCOT MM removes this leverage and the
   resultant signal is dominated by noise.
2. **Two COT buckets (MM and commercials) give highly correlated
   signals on gold** (ρ static +0.85 on both ds). The structural
   distinction between buckets is smaller than expected; both are
   reading the same regime indicator (positioning extremes), and the
   weaker MM-bucket Sharpe is the cleaner read of how much edge that
   regime indicator delivers (which is small).

**Closes**: DCOT MM contrarian standalone path on gold. The "post-2006
data + cleaner speculator bucket" combination does NOT exit iter 018's
+0.35 single-stream plateau on gold COT positioning.

**Does NOT close**:

- DCOT producer-merchant net-short z-score (the hedger side, NOT the
  speculator side). If iter 018's edge comes from the producer-hedging
  leverage, isolating *just* prod-merc as a positive z-score signal
  may capture a cleaner edge than iter 018's mixed legacy commercials.
  Different mechanism than this iter (long-on-extreme-prod-shorting,
  not contrarian-to-MM). Untested.
- DCOT swap-dealer + other-reportables combined as a "smart money"
  proxy. Some literature (post-2008) argues swap dealers are the
  cleanest "lead the market" bucket on gold. Untested.
- COT positioning + price-momentum overlay (BASE_MEMORY priority 4,
  uses iter 003 as the gate filter). Different mechanism family.
- CME GVZ implied-vol regime gate (BASE_MEMORY priority 2). Options-
  derived family, structurally distinct from positioning + realized-vol.
- CME futures track A2 — re-test cost-dominated intraday MR
  (BASE_MEMORY priority 3). New cost path branch.
- Genuinely new mechanism families (cross-asset risk-off, gold-BTC
  ρ flip, multi-asset gold_complex universe with miners/silver).

The path of least resistance for iter 022+ is **CME GVZ priority 2** —
options-derived, structurally distinct from any positioning + realized-
vol family. Different from MM bucket (which is a refinement of iter
018) — GVZ is an entirely new mechanism family.

## Structural dead-ends discovered

**GS-21** — *DCOT money-manager net-long contrarian z-score (window=
156w, lag=1w, z<−1 LONG entry, z>0 exit, max_hold=30d) on gold spot,
single-asset, post-2006 disaggregated bucket*: gld_long primary
(2009-06-09 → 2026-04-15 post-warmup, 16.82y, 4 240 bars) standalone
Sh **+0.073** (Δ **−0.566** vs sliced GLD bench 0.639), CAGR +0.25%,
MDD 30.2% (15.4 pp better than bench but absolute return tiny);
xauusd_real corroborating Sh +0.277, MDD 15.6%, CAGR +1.38%; gates
4/7 + 3/7; DSR p = **0.836** (n_trials=21) — kill #2 fired; primary
WF 2/8 windows pass (kill-equivalent); G6 boot CI low = −0.597 →
G6 fails on primary; ρ static vs iter 003 = +0.023 (rolling-60d exceed
2.2%) → **IC-7 eligible vs iter 003 by both metrics** — kill #3 did
NOT fire — but standalone Sh +0.073 is too weak for productive IC-7
composition (combined ceiling √(0.30² + 0.07²) ≈ 0.31 below iter 003
alone). ρ static vs iter 018 = +0.853 / xauusd_real +0.825 → MM bucket
and legacy commercials bucket are highly correlated signals on gold
DESPITE mechanistic distinction (DCOT MM = pure speculator vs legacy
commercials = producers + merchants + swap dealers). Score 28 = NEAR_FAIL.

**Closes**: DCOT money-manager contrarian standalone path on gold. The
"isolate speculator flow" hypothesis is FALSIFIED — MM bucket Sh +0.073
is materially WEAKER than legacy commercials Sh +0.352 (iter 018).
Producer-hedging leverage embedded in legacy commercials APPEARS TO
ADD the edge, not contaminate it. Closes the COT-bucket-richness
question for the speculator-isolation direction.

**Does NOT close**:

- DCOT producer-merchant bucket as long-on-extreme-prod-shorting
  signal (the hedger-side mechanical-bias hypothesis). Different
  mechanism. Untested; data already cached.
- DCOT swap-dealer + other-reportables combined "smart money" proxy.
  Untested; data already cached.
- COT positioning × price-momentum overlay (BASE_MEMORY priority 4).
- CME GVZ implied-vol regime gate (BASE_MEMORY priority 2).
- CME futures track A2 cost re-evaluation (BASE_MEMORY priority 3).
- Multi-asset gold_complex universe (miners, silver, platinum).
- Cross-asset risk-off / BTC-gold / fine-TF microstructure.

## Citations used

- `[trading_systems_methods, p.640]` — primary, COT positioning
  extremes contrarian; DCOT money-manager bucket as the speculator
  proxy (vs legacy non-commercial which mixes swap dealers).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials=21.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (8 bps RT
  spread + −1 bps/calendar-night swap, single-cfg IC-8).
- de Roon, Nijman, Veld (2000) *J Finance* — "Hedging Pressure Effects
  in Futures Markets" — z-score positioning theoretical anchor (same
  paper iter 018 used; the bucket choice is the only structural
  novelty here).
- CFTC DCOT methodology page (https://www.cftc.gov/MarketReports/
  CommitmentsofTraders/ExplanatoryNotes/index.htm) — DCOT bucket
  definitions; gold series (CFTC code 088691) earliest 2006-06-13.
- IC-6 sister-loop empirical / GS-9 — pre-val ρ on PRIMARY at consistent
  daily granularity; rolling-60d exceedance metric.
- IC-8 sister-loop closure (046) — single pre-committed cfg, no grid.

## Correlation diagnostic (consistent daily granularity)

**iter 021 MM contrarian net-returns vs prior iter standalone returns**

| ref iter | gld_long ρ_static | gld_long rolling-60d exceed | xauusd_real ρ_static | xauusd_real rolling-60d exceed |
|---|---:|---:|---:|---:|
| iter 003 RSI(2)+SMA(200) MR | **+0.023** | **2.2%** | **−0.0002** | **0.0%** |
| iter 011 vol-regime inverse | +0.358 | 67.0% | +0.299 | 32.1% |
| iter 015 DXY trend gate     | +0.141 | 20.1% | +0.048 | 13.5% |
| iter 017 COT Briese 70/30  | **+0.810** | **93.2%** | +0.853 | 84.4% |
| iter 018 COT z-score (commercials) | **+0.853** | **68.5%** | +0.825 | 35.5% |

Key reads:

- **iter 003 ↔ iter 021 (MM)**: structurally orthogonal at daily
  granularity (ρ static +0.023, rolling exceed 2.2% on PRIMARY). IC-7
  eligible by both static and rolling thresholds. *But standalone Sh
  +0.073 is too weak for productive IC-7 composition*: √(0.30² +
  0.07²) ≈ 0.31 < iter 003 standalone +0.30 — the marginal lift is
  zero or negative.
- **iter 018 ↔ iter 021**: ρ +0.85 on both ds — same family.
  **The MM bucket and legacy commercials bucket give the same signal
  on gold** despite the mechanistic distinction between them. This is
  the cleanest empirical validation that COT-positioning-family
  ceiling on gold is a *family ceiling*, not a *bucket ceiling*.
- **iter 011 ↔ iter 021**: ρ static +0.36 (gld) / +0.30 (xau), rolling
  exceed 67% / 32%. The MM contrarian signal correlates with vol-
  regime-inverse at moderate strength; both fire in low-vol regimes.
  Not IC-7 eligible.
- **iter 017 (Briese stoch) ↔ iter 021**: ρ +0.81 / +0.85, rolling
  exceed 93% / 84%. Same family.

## Next iteration suggestions

1. **(NEW PRIORITY 1, PROMOTED) CME GVZ implied-vol regime gate** —
   options-derived family, FRED `GVZCLS` series 2008-06+ (~17.8y on
   gld_long, ~5.8y on xauusd_real). Long when GVZ z-score < −1
   (cheap implied vol → typical mean-revert into rising IV at gold
   rally start). Different from realized-vol (iter 011) and from
   positioning (iter 018/021). May be IC-7-orthogonal to iter 003 in
   a way iter 011/013 σ-regime aren't (different vol family entirely
   — options-implied-vol vs realized-vol). `[volatility_trading]`
   (Sinclair).

2. **(NEW PRIORITY 2) CME futures track A2 — re-test cost-dominated
   intraday MR families** — iter 007 z-MR died at 8 bps RT spread on
   xauusd_intraday (gross +3.5 bps, net −5+ bps). At CME GC futures
   1-2 bps RT spread (per `INFRASTRUCTURE.md` A2), same z-MR signal
   has +1.5 to +2 bps net per trade — possibly intraday-MR-economic
   again. New cost-path branch (`cost_path: cme_futures`).

3. **(NEW PRIORITY 3) DCOT producer-merchant long-on-extreme-shorting**
   — the hedger-side mechanical-bias mirror of this iter. If iter 018's
   edge comes from producer-hedging leverage (as iter 021's GS-21
   suggests), isolating *just* prod-merc as a long-when-prod-merc-
   net-short-extreme signal may capture a cleaner edge. Different
   mechanism than iter 021 (long when prod-merc z<−1 = producers
   crowded short = bullish mechanical signal). Data already cached
   in `cftc_dcot_gold_weekly.parquet`.

4. **(LOWER PRIORITY) Multi-asset `gold_complex` universe extension**
   — extend a known single-asset signal (iter 003 RSI MR) to a
   gold-complex portfolio (60% XAU + 30% GDX + 10% XAG). Sister loop's
   evidence: every winner was multi-asset. The post-relaxation universe
   freedom is unused in iters 016-021 (all single_xau). May exit the
   single-asset Sharpe ceiling of ≈ +0.55 (per GS-13/GS-14).

5. **(LOWER PRIORITY) Concede loop closure** if priorities 1-3 also
   flat-line. Five iterations in NEAR_FAIL 28-35 band (017/018/019/020/
   021); the COT-positioning + IC-7 catalogue is decisively closed.
   PCBO/DSR with n_trials=21+ requires standalone Sh > 0.65 OR an
   IC-7 pair with both low static ρ AND stationary rolling-ρ AND
   strong-enough standalone Sharpes; none of these have been exhibited
   in 21 iterations.

The CME GVZ path (priority 1) has the highest informational value: it
tests a *qualitatively different* vol family (options-implied) than
iter 011/013 (realized-vol), and is the simplest non-positioning
single-mechanism family on the menu. If GVZ also flat-lines at Sh ≈
+0.30, the closure of all single-mechanism single-asset families on
gold within the cached-data envelope becomes a confident scientific
product.
