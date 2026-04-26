# Iteration 014 — Final Report

## Verdict

📉 **NEAR_FAIL** (score **26/100**, winner_conditions_met=False, hold_time_gate=fail)

**The cross-family pivot to TIPS DFII10 macro stream produced a STANDALONE strategy that
"works" in absolute terms but cannot beat gold buy-hold.** All 3 datasets deliver positive
Sharpe (+0.32 to +0.82) and reasonable MDD (all below benchmark + 5pp), but every dataset
trails buy-hold by Δ −0.28 to −0.50 — the cross-dataset kill criterion (xauusd both Δ < 0)
fired. **The macro family is now empirically demonstrated to share gld_long's structural
ceiling with the vol-regime family** via partial overlap (ρ = +0.52 on gld_long vs iter 011)
— the IC-7 orthogonality assumption from iter 013's "Next iteration suggestions" is REJECTED
on the long window.

**Silver lining**: ρ on xauusd_real (+0.32) and xauusd_intraday (+0.28) sits inside IC-7's
0.40-0.60 sweet spot — composition could still unlock DSR uplift on those datasets in iter
015+, just NOT on gld_long. The macro stream also has the cleanest "always-positive 7-gate
diagnostic" of any iter so far: G2 DSR, G3 WF, G6 Bootstrap fail (the gates that test
"is the edge real and big enough?"), but G4 OOS (Sh 0.60-1.40), G5 FWD post-2022 (Sh 0.67-1.10),
and G7 cross-lib (exact 0.00e+00 pp) all pass — the macro signal is real, just too weak vs
the buy-hold benchmark.

## Headline metrics (NET of Pepperstone CFD costs, Track A)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | DSR p | mean hold |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.319 (**−0.366**) | +3.30% (−8.02 pp) | **41.16%** (−4.40 pp ✓) | 4/7 | 0.604 | 16.2 d |
| xauusd_real       | +0.537 (**−0.502**) | +6.78% (−13.15 pp) | 21.94% (+1.58 pp) | 5/7 | 0.653 | 18.0 d |
| xauusd_intraday   | +0.820 (**−0.283**) | +10.52% (−9.67 pp) | **19.04%** (−5.38 pp ✓) | 5/7 | 0.350 | 16.8 d |

OOS / FWD-2022 / Bootstrap detail:

| dataset | OOS-30% Sharpe | FWD-2022+ Sharpe | Bootstrap CI low (99.9%) |
|---|---:|---:|---:|
| gld_long          | +0.603 ✓ | +0.707 ✓ | −0.289 ✗ |
| xauusd_real       | +1.031 ✓ | +0.672 ✓ | −0.822 ✗ |
| xauusd_intraday   | +1.396 ✓ | +1.098 ✓ | −0.259 ✗ |

The OOS / FWD picture is the most encouraging part of the run: in the last 30% of bars
(OOS) AND in the post-2022 stress window, the strategy's Sharpe is 1.0-1.4× — meaningfully
above its full-sample number on every dataset. This is the OPPOSITE of the iter 011/013
profile where OOS lagged full-sample. So the macro signal is not a curve-fit to early data
— if anything, it's strongest in the most recent regime. **G6 Bootstrap fails because the
99.9% lower CI captures the bottom of the distribution which is heavily negative on a
long-only single-asset strategy with high variance.**

## Comparison vs iter 011 / iter 013 (the apples-to-apples pivot test)

The hypothesis was that DFII10 would be **fundamentally different** from the vol-regime
family. The IC-7 ρ result tells a more nuanced story:

| dataset | ρ vs iter 011 (vol-regime σ_60<σ_252) | ρ vs iter 013 (iter 011 + SMA(200)) | ρ vs iter 003 (RSI MR + SMA(200)) |
|---|---:|---:|---:|
| gld_long          | **+0.519** | **+0.492** | +0.184 |
| xauusd_real       | +0.321 | +0.332 | +0.170 |
| xauusd_intraday   | +0.275 | +0.287 | −0.018 |

**On the long window (gld_long), the macro family is NOT orthogonal** to the vol-regime
family — ρ ≈ 0.50 means the two signals are partially capturing the same regimes. **This
is the empirical refutation of iter 013's "Next iteration suggestion" #1 IC-7 hypothesis
on gld_long**. Why? When real rates fall, gold rallies → gold's realized vol contracts
relatively faster than its long-window vol → vol-regime gate switches on. The two streams
are co-moved through the gold-rally feedback loop.

**On the xauusd datasets, the IC-7 path is still alive** at ρ ≈ 0.30 — within the 0.40-0.60
sweet spot the sister loop iter 045/046 documented. But xauusd_real and xauusd_intraday were
already at 7/7 gates on iter 013 (DSR p=0.017 / 0.006). The IC-7 uplift those datasets need
is not "DSR < 0.05" (already there) but "Sharpe edge > 0.10 vs bench" (needs more).

## Per-trade attribution (cost ratio is healthy, but per-trade gross is small)

| dataset | n_trades | gross/trade (bps) | cost/trade (bps) | net/trade (bps) | cost/gross |
|---|---:|---:|---:|---:|---:|
| gld_long          | 172 | +80.6  | +30.0 | +50.6  | 37% |
| xauusd_real       |  40 | +142.6 | +26.1 | +116.5 | 18% |
| xauusd_intraday   |  40 | +192.6 | +22.1 | +170.5 | 11% |

Cost-to-gross is healthier than iter 013 (24% on gld_long → 37% here, but per-trade gross
is 60% smaller — the macro signal triggers more often AND smaller moves). On xauusd, only
40 trades over 6.3y (annual cycle frequency) makes per-trade economics excellent (170 bps
net per trade) but volume insufficient to clear DSR's deflator at n_trials=14.

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | **0** | 25 | 0/3 ds beat bench Δ ≥ 0.10; macro signal cannot bridge gold's drift |
| 2 Gates | **11** | 25 | gld 4/7 (1 pt), real 5/7 (5 pts), intra 5/7 (5 pts); cross-ds bonus FAILS (gld 4 < 5 threshold) |
| 3 DSR | **0** | 15 | worst p = 0.653 on xauusd_real (n_trials=14 — DSR deflator severe even with positive Sharpe) |
| 4 CAGR floor | **0** | 15 | All 3 ds fail floor (0.8 × bench): gld 3.30% < 9.05%, real 6.78% < 15.94%, intra 10.52% < 16.16% |
| 5 MDD ceiling | **15** | 15 | All 3 ds pass ceiling (bench + 5 pp): gld 41.16% ≤ 50.6%, real 21.94% ≤ 25.4%, intra 19.04% ≤ 29.4% |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **26** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | **fail** | — | mean 16.78d on xauusd_intraday primary; cap at STRONG per condition #6 |

## Configuration tested

```
config_id        : macro_dfii10_falling_60d_long_only
lookback         : 60        (trading days, quarterly horizon per Kaufman p.285)
broker_track     : pepperstone_cfd  (Track A primary; Track B reported on daily ds)
costs A          : spread 8 bps RT + swap −1 bps/night long
costs B          : FX 100 bps RT + DARF 15% monthly (informational; Track B FAILS catastrophically on long window with 70% MDD)
cumulative_n_trials : 14
```

Single pre-committed cfg per IC-8. No grid. Lookback 60 = canonical Kaufman quarterly.

## Pre-validation summary

| dataset | p_active | μ active bps/bar | flips | passed |
|---|---:|---:|---:|:---:|
| gld_long          | 0.516 | +4.36  | 342 | ✓ |
| xauusd_real       | 0.424 | +7.18  |  79 | ✓ |
| xauusd_intraday   | 0.423 | +0.53  |  79 | ✓ |

3/3 pass — the signal IS active in healthy fraction (40-50%) and DOES carry positive bias
when on. The strategy is genuinely capturing real-rate-falling regimes. The disappointment
is that the **active-when-on edge** isn't sufficient to overcome the **always-on benchmark**
(gold's 0.68/1.04/1.10 Sharpe across datasets is high to begin with — even capturing all
positive-bar regimes would only ~match benchmark, and the macro signal doesn't catch them all).

## What worked

1. **Signal is real, not noise**. Pre-val 3/3 pass; OOS Sharpe 0.60-1.40 ≥ full-sample
   Sharpe on every dataset; FWD post-2022 Sharpe 0.67-1.10 (positive in the most stressed
   regime). The 60-day-falling-rate flag is genuinely identifying gold's bullish macro
   regime.

2. **MDD reduction across all 3 datasets (G5 passes 3/3)**. gld_long MDD 41.16% (vs
   bench 45.56%, −4.40 pp), xauusd_intraday MDD 19.04% (vs bench 24.42%, −5.38 pp). Only
   xauusd_real has slightly worse MDD (+1.58 pp vs bench's 20.36%) — driven by the few
   times the signal switched off mid-bull-leg in 2024-25.

3. **Cross-lib G7 EXACT 0.00e+00 pp parity** on all 3 datasets. The TDD numpy reference
   for `dfii10_falling_flag_numpy` matches the pandas implementation bit-for-bit.

4. **The macro mechanism IS exogenous to gold prices** — yet the regimes it identifies
   coincide partially with vol-regime states because both are downstream of the same
   real-rate-cycle clock. Useful structural insight for IC-7 boundary modeling.

5. **All 11 TDD tests pass**. `tests/test_macro_dfii10_gold.py` exercises:
   `dfii10_falling_flag` basic descending/ascending/warmup/strict-inequality/index-preserved;
   numpy parity for random + descending; alignment to daily/intraday/missing-day/pre-signal
   indices.

6. **No look-ahead bug**. Position[t] uses signal[t-1] (1-bar lag at execution).

7. **FRED ingester clean**. `scripts/data_sprint/ingest_dfii10_fred.py` mirrors the VIX
   ingester pattern; idempotent, no auth, 5831 bars cached covering 2003-01-02 → 2026-04-23.

## What didn't work

1. **The macro stream cannot beat buy-hold on any dataset**. Δ Sharpe vs bench: gld_long
   −0.366, xauusd_real −0.502, xauusd_intraday −0.283. Score criterion 1 = 0/25.

2. **Cross-dataset kill #3 fired**: xauusd_real Δ AND xauusd_intraday Δ both < 0 → strategy
   has gld-only edge structure. Hypothesis is that the 60-day macro window is **too slow**
   for the xauusd 6.3-y window — cycles aren't long enough to give the signal time to
   work. This contradicts the original premise (real-rate cycles are quarterly+); the
   actual problem is that gold rallies during xauusd's 6.3y window were so explosive
   (2020 COVID, 2024 ATH cycle) that an "off X% of the time" gate gives up too much
   absolute return.

3. **DSR 0/3 fail**. Worst p=0.653 on xauusd_real. With n_trials=14, the deflator is so
   severe that even Sharpe 0.82 (xauusd_intraday) gets p=0.350 — far from 0.05. Per IC-8,
   DSR drains fast; even at +0.5 Sharpe-edge zones, 14-trial penalty is killing significance.

4. **CAGR floor 0/3 fail**. Strategy is "off" 50-60% of the time → cumulative CAGR collapses
   despite per-trade economics being positive. Same shape as iter 010/011/013 swing-extended
   long-only strategies.

5. **G6 Bootstrap 0/3 fail**. The 99.9% CI lower bound dips into negative territory across
   all datasets. The macro Sharpe distribution has a fat negative tail (early-cycle false
   signals).

6. **gld_long ρ vs iter 011 = +0.519**. **The IC-7 boundary (sister 045/046 best at ρ=0.41)
   is exceeded** on gld_long. The macro family is partially overlapping with vol-regime
   on the long window — they're both downstream of the same real-rate cycle. **The IC-7
   composition path on gld_long predicted by iter 013's "Next iteration suggestions" is
   EMPIRICALLY REJECTED at the 60-day lookback.**

7. **Hold-time gate still fails** (mean 16.8d on xauusd_intraday primary; threshold 5d).
   Real-rate cycles cluster on quarterly-or-longer scales. Same swing-extended cap as
   iter 011/012/013.

8. **Track B catastrophic on long window**: gld_long Track B Sharpe −0.30, CAGR −4.58%,
   **MDD 70.20%**. The DARF 15% monthly + FX 100bps RT compound destroys the marginal
   edge. Track A is the only viable broker path for this strategy. Reaffirms GS-2 closure.

9. **gld_long n_trades = 172 (high frequency for swing)**. Real-rate cycles flip 60-day
   gate ~16 times/year on the long window because DFII10 has 30-90-day mini-cycles
   embedded in the bigger trend. This thins per-trade gross to +80.6 bps and worsens
   cost-ratio to 37% — comparable to iter 013's gld_long thinning (+106 bps net per
   trade).

## Main lesson (for future iterations)

**The TIPS DFII10 macro stream is not the structural family-orthogonal lever iter 013's
suggestion #1 hoped for — at least not on gld_long.** Empirically, ρ vs vol-regime is
+0.52 on the long window; the two signals partially share the same real-rate-cycle
information. **GS-14 closes the IC-7-on-gld_long path predicated on macro orthogonality
at lookback=60d**. Future iters can probe:

(a) **Different lookback** (1y, 3y) for DFII10 — slower lookbacks may decouple from
    vol-regime's 60-252 frequencies. Caveat: longer lookback = even slower regime, even
    worse for the day/swing horizon.

(b) **Different macro signal** that is genuinely orthogonal to gold-vol cycles. Candidates:
    DXY level (not z-score; iter 005 closed z-score), CFTC COT positioning extremes,
    Indian rupee strength (Indian wedding season demand cycle), gold-lease rate spikes.
    All require additional data fetches. None have prior literature as strong as DFII10.

(c) **Accept gld_long as a "context check" only** and chase IC-7 composition on xauusd
    datasets where ρ vs iter 011 is +0.32 (xauusd_real) and +0.28 (xauusd_intraday) —
    inside IC-7 sweet spot. But xauusd is already at 7/7 gates on iter 013; the IC-7
    uplift those datasets need is "Sharpe edge > +0.10 above buy-hold", not "DSR < 0.05",
    and the macro stream provides NEGATIVE Sharpe edge there.

(d) **Pivot family entirely** — try cross-asset within gold complex (NEM/RGLD divergence;
    cached but starts only 2013) or BTC-as-risk-off (cached). Both have weaker priors
    than DFII10 had.

The macro path SHIPPED a working signal but the empirical ceiling on **single-stream
gold strategies on the gld_long 21y window appears to be Sharpe ~0.55** regardless of
family — vol-regime, regime-gated MR, and now macro all hit the same ceiling. **The
deficit between Sharpe-0.55 and benchmark-0.68 is structural to gold's mixed-regime
21y window; no single-stream signal we've tried can bridge it.**

**Strategic recommendation**: stop chasing gld_long Sharpe ≥ 0.65 standalone — IC-7 is
the only remaining mechanical path, and it requires a base with ρ < 0.40 vs iter 011/013.
Iter 015 should TEST that hypothesis directly: pick a candidate with maximum prior
orthogonality (e.g., COT positioning or DXY level — both involve data fetch but COT is
already roughly weekly cadence and fetch-trivial). If iter 015's best ρ vs iter 011 is
still > 0.40, gld_long Sharpe ≥ 0.65 is structurally unreachable on this loop.

## Structural finding (DEAD_ENDS GS-14)

**GS-14 closes the assumption** that macro/real-rate-derived signals are orthogonal to
price-derived vol-regime signals on gold's long window. Iter 014 empirically demonstrates
ρ ≈ +0.50 on gld_long between DFII10-falling and σ_60<σ_252 — sufficient to violate
IC-7's <0.50 boundary condition for cross-family DSR uplift. The mechanism is the
real-rate-cycle feedback loop: real-rate falls → gold rallies → gold-vol contracts →
vol-regime gate switches on. Both streams ride the same macro clock.

**Closes**:
- IC-7 composition iter_014 + iter_011 (or iter_013) for gld_long DSR<0.05 uplift —
  predicted gain at ρ=0.50 is too small to clear deflator at n_trials=15+
- The "fundamentally different family" assumption for ANY 60-day-window macro signal
  on gold (lookback=60d will share the same real-rate cycle clock as 60-252-day vol
  regime)
- Specifically: iter 013 "Next iteration suggestions" #1 and BASE_MEMORY direction #1
  (PROMOTED iter 014) at lookback=60d configuration

**Does NOT close**:
- DFII10 macro stream itself as a standalone diagnostic — it does work, just weaker
  than buy-hold. Could be a regime-confirmation overlay for a higher-Sharpe base.
- IC-7 composition on xauusd datasets where ρ ≈ +0.30 still fits IC-7 boundary; but
  xauusd Sharpe edge from macro is NEGATIVE so composition would dilute, not amplify.
- Different macro signal classes (DXY level, COT positioning, gold-lease rates) that
  may have lower ρ vs vol-regime via different mechanism.
- DFII10 at *different* lookbacks (1y, 3y) which probe different cycle frequencies.
- Cross-asset overlays that don't ride the real-rate clock (BTC-risk-off, GDX/GLD).

## Citations used

- `[trading_systems_methods, p.13]` — Kaufman: metals are low-noise → trend-following
  with macro driver (PRIMARY). Empirically: directional effect confirmed (signal is
  active on positive-bias regimes); magnitude insufficient to beat buy-hold's drift.
- `[trading_systems_methods, p.285]` — quarterly = 60-63 trading days (lookback choice).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative_n_trials = 14; deflator demonstrably
  punishing even +0.5 Sharpe-edge zones.
- Web — Erb & Harvey (2013) "The Golden Dilemma" FAJ — empirical inverse correlation of
  gold returns with real-rate level. Validated: signal does carry positive bias when on.
- Web — Bauer & Mertens (2018) FRBSF Working Paper — TIPS-implied real-rate dynamics.
  Confirmed: DFII10 information content is real, but doesn't translate to gold-buy-hold
  outperformance at 60-day cycle scale.
- DEAD_ENDS GS-12 / IC-7 — assumed orthogonality refuted; ρ=+0.52 on gld_long.
- IC-8 (sister 046/047/050) — single pre-committed cfg; deflator increment 13 → 14
  contributed to all 3 datasets failing G2 even at +0.32 to +0.82 Sharpe.

## Next iteration suggestions (priorities updated by iter 014's findings)

iter 014 closes the macro-as-IC-7-orthogonal-base hypothesis on gld_long. The structural
ceiling for **single-stream** gold strategies on gld_long looks like Sharpe ≈ 0.55.
**The remaining viable directions**:

1. **(NEW PRIORITY 1) DXY level (not z-score) regime gate**. Iter 005 closed DXY z-score
   recovery at lookback=5 because it flipped sign on 2020+. **DXY LEVEL** (e.g., long
   gold when DXY < 100 OR DXY 200-day-MA falling) operates on a different cycle than
   real rates and may have lower ρ vs vol-regime. Cached data sufficient (USDCAD/USDCHF/
   USDJPY proxies); no FRED fetch. Family: cross-asset macro (different from rates).
2. **(PRIORITY 2) CFTC COT non-comm net longs gold**. Weekly cadence; needs CFTC COT
   data fetch (similar shape to FRED fetch). Positioning extremes are mechanically
   different from price-action and from real rates. Citation in books: weak (COT in
   Kaufman briefly p.700+ but no specific gate). Web: Cordero (2017) "COT-as-momentum"
   on metals.
3. **(PRIORITY 3) Asymmetric vol-regime σ_60<σ_252 AND drawdown_60d<10%** (BASE_MEMORY
   direction #2). Drawdown filter is more direct than SMA(200). Probably hits same ~0.55
   ceiling but worth burning the LAST single-mech filter test. Same family as iter 011/013
   so warning: 4th consecutive iter on vol-regime axis means clear over-spend. Skip
   unless directions 1 + 2 are blocked.
4. **(PRIORITY 4) GDX/GLD divergence via NEM proxy** (BASE_MEMORY direction #4 with
   adjustment for cache contents). NEM data starts 2013-08; only 12y window for gld_long
   replication. Single-name (NEM) proxy for GDX basket has high tracking error. Lower
   priority because the prior is weaker AND data window is shortened.
5. **(PRIORITY 5) BTC-gold flight-to-quality** (BASE_MEMORY direction #23). BTCUSD cached;
   tests "long gold when BTC drawdown > 20%". Different family entirely (crypto-as-risk-on),
   though gold-BTC ρ has been historically unstable.

iter 015 should pursue priority #1 (DXY LEVEL) — minimum data investment, structurally
different cycle (FX cycles ≠ rate cycles ≠ vol cycles), and tests the GS-14 corollary
that the *same-macro-clock* problem is rate-specific not macro-generic. If iter 015's
ρ vs iter 011 < 0.40 on gld_long, IC-7 path is alive. If still > 0.40, gld_long is
structurally capped at ~0.55 single-stream and the loop should accept that and shift
focus to **xauusd-only** evaluation criteria (the cost-realistic actual instrument anyway).
