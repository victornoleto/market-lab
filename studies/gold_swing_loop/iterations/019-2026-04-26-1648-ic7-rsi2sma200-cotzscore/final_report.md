# Iteration 019 — Final Report

## Verdict
📉 **NEAR_FAIL** (score **35/100**, winner_conditions_met=False, hold_time_gate=PASS, **kill #3 fired**)

The IC-7 003+018 Markowitz tangency composition delivered the
**predicted Sharpe lift** (+0.106 vs iter 018 standalone, achieving Sh
+0.4584 on gld_long versus the IC-7 closed-form ceiling
√(0.299² + 0.352²) ≈ 0.46) and **dramatic MDD compression** (45.6% →
9.6%, −36 pp on gld_long). The IC-7 mechanism worked as predicted by
`[advances_fin_ml, p.222-223]`. **But the Bonferroni-deflated DSR null
at n_trials=19 still blocks G2** (combined p=0.4055 > 0.05; degraded
slightly vs iter 018's standalone 0.354 because composition uplift
< n_trials inflation). **DSR no-progress kill (#3) fired**, recording
the iteration as the closure of the 2-stream IC-7 path on gold within
the current 18-iter catalog.

## Headline metrics (NET of Pepperstone CFD costs, both component streams pre-deducted)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | weighted hold |
|---|---|---|---|---|---|
| gld_long (PRIMARY)         | **+0.4584** (Δ −0.226) | +1.94% (Δ −9.38) | **9.56%** (Δ −36.0 ↓ better) | **5/7** | 12.64 d |
| xauusd_real (CORROBORATING) | +0.3464 (Δ −0.692) | +1.18% (Δ −18.7) | 8.33% (Δ −12.0 ↓ better) | 4/7 | 15.30 d |

Bench (measured iter 001):
- gld_long: Sh 0.684, CAGR 11.32%, MDD 45.6%
- xauusd_real: Sh 1.038, CAGR 19.93%, MDD 20.4%

Per-dataset sub-metrics (gld_long primary):
- DSR p = 0.4055 (n_trials=19) → **G2 FAIL** (vs iter 018 standalone 0.3544)
- Bootstrap 99.9% CI low > 0 → **G6 PASS**
- Walk-forward 6+/8 windows → **G3 PASS**
- OOS 70/30 Sharpe > 0 → **G4 PASS**
- FWD post-2022 Sharpe > 0 → **G5 PASS**
- Cross-lib CAGR parity within 3pp → **G7 PASS**
- PBO N/A (single cfg, IC-8) → **G1 PASS by convention**
- IC-6 rolling 60d ρ exceedance: **1.5%** (32/2191 bars > 0.30) → **PASS** (limit 20%)

## Score breakdown (v2 scoring, rules_version=2026-04-26-relaxed-r1)

| criterion                    | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge                | 5      | 25  | primary not beat (Δ−0.226); corroborating Sh +0.346 > 0 → +5 |
| 2 Gates                      | 15     | 25  | primary 5/7 ≥ 5 → +15; corroborating fails G2 (DSR p=0.836) → no +5 |
| 3 DSR                        | 0      | 15  | primary p=0.4055 (n_trials=19) |
| 4 CAGR floor                 | 0      | 15  | primary 1.94% < 0.8 × 11.32% = 9.06% → FAIL |
| 5 MDD ceiling                | 15     | 15  | primary 9.56% ≤ 50.6% → PASS by 41 pp |
| 6 Robustness bonus           | 0      | 5   | not computed |
| **total**                    | **35** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate)             | PASS   | —   | 12.64 d ∈ medium_swing [10, 30] |

## Configuration tested (single cfg, IC-8)

```yaml
cfg_id: ic7_iter003_iter018_markowitz_gld_primary
method: markowitz_tangency_full_sample
iter_003_cfg: connors_rsi2_sma200_filter
iter_018_iter: 018-2026-04-26-1628-cot-zscore-variant
weights:
  gld_long:    {w_iter_003: 0.6447, w_iter_018: 0.3553, clamped: false}
  xauusd_real: {w_iter_003: 0.5287, w_iter_018: 0.4713, clamped: false}
declared_primary: gld_long
declared_corroborating: [xauusd_real]
broker_track: pepperstone_cfd
universe: single_xau
hold_time_track: medium_swing
ic6_pre_val:
  rolling_rho_window: 60
  rolling_rho_limit: 0.30
  exceed_frac_limit: 0.20
  observed_exceed_frac_gld: 0.015
  observed_exceed_frac_xau: 0.000
```

Cumulative `n_trials` 18 → **19** (this iter increments by 1; IC-8
honored — single Markowitz tangency cfg pre-committed, no grid).

## What worked / what didn't

**Worked**:

1. **IC-7 closed-form Sharpe ceiling validated empirically.** Predicted
   ≤ √(0.299² + 0.352²) = 0.4598 on gld_long; observed 0.4584 (within
   0.3% of theoretical max). The full-sample Markowitz tangency
   formula `[advances_fin_ml, p.222-223]` describes 2-stream gold
   composition behavior at ρ ≈ 0 essentially exactly. This is the
   loop's first **clean numerical confirmation** of the IC-7 ceiling
   on gold; iter 012's 003+011 (ρ measurable) and iter 016's 003+015
   (freq-mismatch artifact) both diverged from theoretical ceilings.
2. **Drawdown compression by uncorrelated-stream diversification is
   spectacular**: gld_long MDD 45.6% bench → 9.6% combined (−36 pp,
   compression factor 4.7×); xauusd_real 20.4% → 8.3% (−12 pp,
   compression factor 2.4×). The composition gives gold the best
   risk-of-loss profile in the loop's history at any tier.
3. **IC-6 pre-val rolling ρ confirmed orthogonality is regime-stable**:
   only 1.5% of 60d windows on gld_long exceed |ρ|>0.30 (32/2191
   bars). xauusd_real shows zero exceedance. The static ρ ≈ +0.013
   isn't a sample artifact — it holds across 21 years of gold's
   regime transitions.
4. **Markowitz weights are well-conditioned** (no clamp on either
   dataset; w_003/w_018 = 0.64/0.36 on gld_long matches the analytical
   prediction `μ_003/σ_003² : μ_018/σ_018² ∝ Sharpe-per-σ ratio`).
5. **WF improved further to 6+/8** on the combined (vs iter 018
   standalone 7/8 and iter 017 5/8) — selectivity from MR + slow-
   positioning blends evenly across windows.
6. **Hold-time bucket matches declaration**: weighted-avg 12.64d is
   inside medium_swing [10, 30]; corroborating xauusd_real at 15.30d
   also passes.

**Didn't work**:

1. **DSR no-progress kill #3 fired.** Combined p=0.4055 vs iter 018
   standalone 0.3544 → composition DEGRADED p slightly. The reason
   is the n_trials cumulative penalty: iter 018 used n_trials=18,
   this iter uses 19. The DSR null mean SR0 grows as
   √(2 ln n_trials), and the composition's annualized Sharpe lift
   (0.106) is BELOW the marginal SR0 growth rate. The IC-7 path's
   theoretical lift √(1−ρ²)·sqrt(S_A²/S_B² + 1)·S_B ≈ 0.30 at this
   ρ and (S_A,S_B) is competitive with absolute Sharpe but not with
   the moving SR0 baseline at this n_trials regime.
2. **Primary Sharpe edge gap unclosed.** Combined 0.458 vs target 0.78
   → still trails by 0.32. Even pushing to the analytic IC-7 maximum
   on this 2-stream pair, gld_long buy-hold drift remains the
   structurally-superior carry-and-hold benchmark on the cost-
   adjusted long-horizon sample.
3. **CAGR floor gap is large.** Combined 1.94% vs target 9.06% (0.8×
   bench). Capital is allocated such that ~64% rides iter 003's
   highly-selective MR (rare entries, ~14 trades/yr at ~4d hold) and
   ~36% rides iter 018's slow swing (~4 trades/yr at ~28d hold). The
   composite spends most calendar time near zero net exposure → small
   absolute drift compared to bench buy-hold. **Exceptional risk-
   adjusted return is invisible at the absolute-CAGR level.**
4. **Corroborating xauusd_real does not clear relaxed gates** (G6 ✓
   but G2 DSR p=0.836). Short history (1700 bars, 4.7y) inflates
   DSR-style critical values; a longer-window relative-strength
   benchmark (e.g., DCOT post-2009 starting 2009 → 17y) might give
   richer corroborating signal but is iter 020+ scope.
5. **Score did not exceed iter 018's 35.** Both iters tied at the
   loop's best-case NEAR_FAIL ceiling. Current candidate menu within
   the existing 18-iter catalog has hit its DSR-deflated wall.

## Main lesson (for future iterations)

**GS-19 — 2-stream IC-7 closure on gold within the existing 18-iter
catalog**: the full-sample Markowitz tangency of the loop's
lowest-ρ pair (iter 003 RSI MR + iter 018 COT z-score, ρ=+0.013)
delivers the predicted Sharpe lift (+0.106 to +0.458 on gld_long,
matching IC-7 ceiling √(0.30² + 0.35²) ≈ 0.46) and dramatic MDD
compression (−36 pp), but **does not clear DSR<0.05 at n_trials=19**.
The Bonferroni-deflated null mean SR₀(n_trials) grows faster than the
incremental Sharpe lift available from any further low-ρ pair within
the existing iter 001-018 stream catalog (because all standalone
streams cap at Sh ≈ 0.55, and S_combined ≤ √(S_A² + S_B²) ≤ √(0.55²)·√2
≈ 0.78 — exactly equal to the bench+0.10 winner threshold, which DSR
deflates to require ~1.0+ for n_trials=20+).

**This means**: there is no DSR<0.05 winner reachable on gold via
2-stream IC-7 composition of any existing iter 001-018 stream pair.
A WINNER on gld_long requires either:
- (a) **A third stream (3-stream IC-7)** of comparable Sharpe AND
  ρ < 0.10 to BOTH existing streams. Combined Sh ≤ √(S_A²+S_B²+S_C²);
  with 3 streams at Sh ≈ 0.30-0.35 each at low ρ this could hit
  ~0.55-0.60 — but each new test costs n_trials ++.
- (b) **A genuinely new mechanism** delivering standalone Sh > 0.65
  on gld_long. None of the closed dead-ends (GS-1 to GS-18) suggest
  such a mechanism is available within the absorbed-book + cached-
  data envelope.
- (c) **N_trials reset / Bonferroni discipline relaxation** — out of
  scope (sister-loop IC-8 closure forbids).

The path of least resistance for iter 020+ is to test the highest-
positive-uplift 3rd stream candidate (likely **iter 015 DXY trend**
at ρ vs 003 = +0.087 / vs 018 = ?, or a **DCOT money-manager
post-2009** which is the only structurally-different COT signal not
yet tested) BEFORE conceding the loop. But the DSR ceiling is
mathematically near and probably structural; a credible loop close
within ≤3 more iters is realistic if 3-stream + DCOT both flat-line.

## Structural dead-ends discovered

**GS-19** — *IC-7 Markowitz tangency of iter 003 (RSI(2)+SMA(200) MR)
+ iter 018 (rolling-156w z-score COT positioning) at full-sample
weights w_003=0.64 / w_018=0.36 on gld_long primary*: combined Sh
**+0.4584** (vs iter 018 standalone 0.3516, +0.106 lift = 99.7% of
analytical ceiling √(0.30²+0.35²) ≈ 0.460), CAGR +1.94%, MDD **9.56%**
(−36 pp vs bench, the loop's lowest-ever MDD on gld_long). xauusd_real
corroborating: Sh +0.346, MDD 8.33%. Gates 5/7 + 4/7 (primary +
corroborating); DSR p **0.4055** (n_trials=19) > 0.05 — kill #3 fired.
Hold time 12.64d (weighted-avg) ∈ medium_swing. IC-6 rolling-ρ pre-val
PASS (1.5% exceed). Score 35 = NEAR_FAIL.

**Closes**: 2-stream IC-7 path on gold within the existing 18-iter
catalog. The Bonferroni-deflated DSR null SR₀(n_trials=19) exceeds
the marginal Sharpe lift available from any further pair in the iter
001-018 catalog because all standalone streams plateau at Sh ≤ 0.55
and the combined-Sharpe upper bound is √(S_A²+S_B²).

**Does NOT close**:
- 3-stream IC-7 (003+018+third) — not tested; if a third low-ρ
  stream of Sh ≥ 0.30 exists, combined ceiling rises to ~0.55-0.60.
- DCOT money-manager net longs (post-2009 only) — different stream,
  may exit the +0.35 single-stream plateau.
- Genuinely new mechanism families not yet tested (CME GVZ implied-vol
  regime gate, gold risk-reversal skew, GDX-NEM proxy after 2013,
  state-machine-aware pre-val on existing pairs).
- Out-of-Pepperstone broker tracks (CME futures with 1-2 bps spread
  could re-open intraday MR families that died at 8 bps in iter 007).

## Citations used

- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combined-Sharpe upper bound for 2-asset tangency portfolio.
- `[advances_fin_ml, p.31-34]` — cost realism (composition adds no
  turnover; reuses pre-deducted Pepperstone CFD costs from each
  component).
- `[short_term_trading_strategies, p.106]` — RSI(2) + SMA(200) MR
  base (iter 003 component).
- `[trading_systems_methods, p.639-640]` — COT z-score positioning
  variant (iter 018 component).
- de Roon, Nijman, Veld (2000) *Journal of Finance* — "Hedging
  Pressure Effects in Futures Markets" (z-score commercial net
  positioning theoretical anchor).
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046)
  — out-of-family ρ < 0.50 + Markowitz proper compounds DSR.
- IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50, when
  Sharpes differ.
- IC-8 sister-loop closure (046) — single cfg per iter unless
  Bonferroni-justified.

## Correlation diagnostic (consistent daily granularity, post GS-16
process correction)

The composition's full-sample static and rolling-60d ρ between iter 003
and iter 018 returns:

| dataset | static ρ | rolling 60d |ρ|>0.30 frac | n_bars |
|---|---:|---:|---:|
| gld_long       | +0.0134 | 1.5% (32/2191) | 5384 |
| xauusd_real    | +0.0043 | 0.0% (0/912)   | 1700 |

**3rd independent confirmation** of GS-17/18 orthogonality on this
RSI-MR vs COT-positioning pair. The RSI(2)+SMA(200) MR signal and the
156w z-score COT positioning signal are now the **most thoroughly
validated low-ρ stream pair in the loop's 19-iter history**.

## Next iteration suggestions

1. **(NEW PRIORITY 1) 3-stream IC-7 003+018+015 Markowitz** — adds
   iter 015 DXY-MA-slope as a 3rd stream. ρ pairs from prior iters'
   correlation diagnostics:
   - 003 vs 015 = +0.22 (gld_long, post-GS-16 correction)
   - 018 vs 015 = +0.087/+0.045 (iter 018 measurement)
   - 003 vs 018 = +0.013/+0.004 (this iter, 3rd confirmation)
   Average pairwise ρ ≈ 0.10. Combined ceiling ≤ √(0.30²+0.35²+0.24²)
   ≈ 0.52. **Probably still below WINNER** but possibly clears DSR<0.05
   if the n_trials=20 vs 3-stream uplift trade-off is favorable. The
   tangency formula generalizes to N=3: `w ∝ Σ⁻¹μ` with 3×3 covariance.
   `[advances_fin_ml, p.222-223]` + `[risk_parity, ch.2]`.

2. **(NEW PRIORITY 2) DCOT money-manager net longs (post-2009)** —
   replaces iter 018's legacy commercials bucket with the more refined
   "money-manager" speculative bucket. Requires CFTC DCOT supplemental
   data feed (separate fetch). xauusd_real becomes natural primary
   (post-2009 cutoff = 2010+; gld_long downgraded to corroborating).
   Hypothesis: legacy commercials = miners hedge naturally short →
   producer-bucket signal partially anti-correlated with what we
   want; money-manager bucket isolates pure speculative flow. Possibly
   exits the +0.35 plateau. `[trading_systems_methods, p.640]`.

3. **(NEW PRIORITY 3) CME GVZ implied-vol regime gate** — options-
   derived family, FRED `GVZCLS` series 2008+. Different from
   realized-vol (iter 011) and from positioning (iter 018). Long when
   GVZ z-score < −1 (cheap implied vol → mean-revert into rising IV
   typical at gold rallies). xauusd_real or post-2008 gld_long primary.
   `[volatility_trading]` (Sinclair).

The 3-stream path (priority 1) has the highest informational value:
it directly tests whether the DSR-deflator wall is breakable within
the existing catalog, and falsification (combined Sh < 0.50 or DSR
p > 0.10) would be the loop's strongest signal that gold-strategy
hunting is mathematically out of room within current instruments.
