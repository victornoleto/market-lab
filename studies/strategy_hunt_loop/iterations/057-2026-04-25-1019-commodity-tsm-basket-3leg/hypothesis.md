# Iteration 057 — iter 046 + commodity TSM basket (USO+UNG+SLV) as third stream at w=0.20

## Hypothesis

iter 045 vindicated **out-of-family return-stream addition at moderate
correlation** as a structural mechanism for compounding DSR (corr ≈ 0.58
→ DSR worst-p 57% reduction on iter 037 base). iter 046 transplanted
that mechanism onto a higher-Sharpe regime-gated base (iter 041) at
**lower correlation** (corr ≈ 0.41) and reached score **85** with
DSR worst-p sub-0.05 across all 3 datasets — the loop's first such
result. iter 049/050 then tested **single-asset gold TSM** as a third
stream and found gold-specific dilution at w=0.5 (score 59) and a
Markowitz-implied near-optimal w*≈0.10 yielding score 78 (still below
iter 046's 85 because gold IS already inside iter 041's stack with
weight 0.40-0.55, so gold-TSM partially DUPLICATES the iter 041 leg).

**iter 057 tests the next structural step**: a **multi-commodity TSM
basket** (USO oil + UNG natural gas + SLV silver — explicitly EXCLUDING
gold which iter 041 holds) as third return stream. Three motivations:

1. **Asset-class orthogonality**: USO/UNG/SLV are NOT inside iter 041
   (SPY/IEF/GLD) or iter 039 (T-bill + SPY/QQQ/IWM put credit spreads).
   Predicted corr(r_csm, r_046) ∈ [0.05, 0.20] — much lower than gold
   TSM's corr(r_gld_tsm, r_046) ≈ 0.50 (which iter 049/050 measured).
2. **TSM diversification compound**: Moskowitz-Ooi-Pedersen 2012
   (DOI 10.1016/j.jfineco.2011.11.003) found cross-commodity TSM
   Sharpe ~0.30-0.50 on 24-asset universe; even on a 3-asset
   basket, equal-weight diversification reduces single-commodity
   idiosyncratic vol by ~√3 relative to single-asset.
3. **Structural distinction from iter 023 dead-end**: iter 023 closed
   "TSM-PRIMARY ≤4-asset" (TSM as the *primary* mechanism with small
   universe). iter 057 uses the same small-universe TSM but as a
   *secondary 20% overlay* on a high-Sharpe iter 046 base. The dead
   end was never re-tested at this role — and iter 049/050 already
   demonstrated single-asset TSM-as-overlay can score 78 STRONG.

The convex combination is structurally the iter 049/050 architecture
with two changes: (a) third stream = 3-asset commodity basket instead
of single GLD; (b) overlay weight w_csm = 0.20 (between iter 049's 0.50
and iter 050's 0.10) — chosen to keep iter 046's high-Sharpe base
dominant (80% mass) while giving the diversifier enough mass to move
the correlation/DSR needle.

**Predicted score range**: 78-86 STRONG. The score swing is on the
DSR-via-corr axis: if corr(r_csm, r_046) < 0.20 AND r_csm has positive
Sharpe (any value > 0.0), the DSR worst-p drops from iter 046's
0.041 (edu) toward 0.025-0.035 — well within the 15pt band. The CAGR
floor remains the 90+ blocker (iter 046's c4=0/15 is the gap to 90),
and commodity TSM has predicted CAGR 0-5% (likely DRAGS the combined
CAGR down from iter 046's 9.16-9.76%, NOT up). So the realistic
ceiling is **84-86 STRONG**, not 90+ WINNER. iter 057's value is the
**structural finding** about non-gold commodity TSM as orthogonal
diversifier (closes another axis on iter 046 family if it scores < 85).

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
with regime-conditional weight tilts (iter 046 base architecture
preserved verbatim via saved return stream).

## Additional citations

- Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — "Time series momentum" across
  24 commodities/equities/bonds/FX; positive 12-1 momentum sign on
  inverse-vol scaled position is the canonical TSM specification.
  Justifies the 90-day boolean trend filter on USO/UNG/SLV.
- Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985,
  DOI 10.1111/jofi.12021 — "Value and momentum everywhere" — TSM
  premium documented across asset classes including commodities;
  cross-asset TSM has lower correlation to equities than expected.
- Erb-Harvey (2006), FAJ 62(2) 69-97,
  DOI 10.2469/faj.v62.n2.4084 — "The strategic and tactical value of
  commodity futures"; commodity premia decompose into spot return + roll
  yield + collateral; trend-filter avoids persistent commodity drawdowns
  (e.g., 2014-2020 oil bear market).
- `[systematic_trading]` (Carver) — generic TSM rule on a single asset;
  boolean trend filter (long-only when trail return > 0).
- `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log price
  as the canonical implementation of TSM.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with
  cumulative `n_trials`; combining low-correlation strategies with
  positive Sharpes improves the deflated p-value (iter 045/046 vindicated).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate (G6).
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (iter 057 uses trailing return at t-1 for position at t).
- `[volatility_trading, p.218]` — Sinclair (2013) on cross-asset VRP
  (iter 039 base architecture preserved verbatim).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination
  minimum-variance under uncorrelated streams.

## Edge source

SPY 1x buy-hold buys EXP(SPX) only. iter 046 already buys two
positive-Sharpe streams (regime-gated equity-bond-gold stack + cross-asset
short put VRP). iter 057 adds a **third orthogonal asset-class exposure**:
trailing-trend-filtered exposure to oil, natural gas, and silver — three
markets that are uncorrelated with SPY/IEF/GLD AND with short-equity-vol.
The TSM filter avoids long-only commodity drag (post-2014 oil/gas bear)
by going to cash on negative trend. The basket equal-weights each
filtered stream, so per-asset blow-ups (e.g., negative WTI April 2020,
gas spikes) are diluted by 1/3.

The diversification benefit is **structural even if commodity TSM has
mediocre absolute Sharpe**: at corr ≈ 0.10 with iter 046, a third stream
with Sharpe ~0.25 at w=0.20 reduces portfolio vol by ~9% (1 - √(0.80² +
0.20² + 2×0.80×0.20×0.10) / √(0.80²) ≈ 9%) while diluting mean by ~16%
— net Sharpe approximately preserved AND DSR worst-p reduced via
trial-noise reduction.

## Datasets

- **educational** (≈19y): the inner-join of iter 046's saved 2006-01-03
  → 2026-04-15 stream and the commodity TSM stream (which starts at
  the latest of USO_inception=2006-04-10, UNG_inception=2007-04-18,
  SLV_inception=2006-04-28, plus 90-day lookback) ≈ 2007-09 → 2026-04.
  Includes 2008 GFC + 2020 COVID + 2022 inflation regimes — full
  crisis coverage.
- **spy_real** (≈17y): 2009-06-25 → 2026-04-15. iter 046 base verbatim;
  commodity TSM has full coverage from 2007 onward, so no truncation.
- **ndx_real** (≈16y): 2010-02-12 → 2026-04-15. Same — no commodity
  TSM truncation needed.

The educational truncation by ~20 months (2006-01 → 2007-09) is a
known cost of using post-2007 commodity ETFs. Acceptable: 2008 GFC is
still inside the window. Cumulative `n_trials` advance from 4326 → 4327
(single pre-committed cfg).

## Kill criteria (pre-committed)

| kill | observable | threshold | interpretation |
|---|---|---|---|
| **A** Sharpe regress | datasets with `Sharpe_057 < Sharpe_046 − 0.05` | ≥ 2 of 3 | commodity TSM dilution overrides diversification benefit; "TSM-PRIMARY ≤4-asset" extends to overlay |
| **B** DSR regress | `worst_p_057 ≥ 0.041` (iter 046's edu baseline) | ≥ 0.041 | composition added trials without compounding edge — overlay didn't pay |
| **C** CAGR regress | `CAGR_057 < CAGR_046 − 1.0pp` on ≥ 2 of 3 datasets | < (Δ −1.0pp) | TSM dilutes high-CAGR base too aggressively at w=0.20 |
| **D** Score regress | `score_057 < 78` (≤ iter 050's gold-TSM-w0.10) | < 78 | non-gold commodity TSM is strictly worse than gold (counter-intuitive given lower corr expectation) |
| **E** G7 cross-lib | `Δ pp > 3.0` on commodity TSM portion | > 3.0 pp | engine bug |
| **F** Correlation breach | `corr(r_csm, r_046) > 0.50` on any dataset | > 0.50 | commodity TSM is more equity-correlated than expected; orthogonality premise wrong |

If **2 or more** kills fire, hypothesis is falsified: "Multi-commodity
TSM as 3rd-stream overlay on iter 046 is dominated by single-asset gold
TSM (iter 050) within the same w-weight family". This closes the
"diversified non-gold commodity TSM" axis on iter 046 family.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid)
- **Wall-time**: ~10-20 min (iter 046 stream loaded from JSON; only
  3-asset TSM + combo to compute) + 5-10 min for gates/score
- **Files to create**:
  - `hypothesis.md` (this file)
  - `commodity_tsm.py` — pandas engine: per-asset boolean TSM on
    USO+UNG+SLV, equal-weight basket
  - `combined_046_plus_csm.py` — convex combo of iter 046 stream
    (loaded from JSON) and commodity TSM
  - `numpy_reference_iter057.py` — pure-numpy reference for the
    commodity TSM portion (G7 parity)
  - `run_backtests.py` — single cfg, 3 datasets driver
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation
  - `tests/test_iter_057_commodity_tsm.py` — TDD specs
    (reductions: w_csm=0 → exact iter 046; single-asset reduction;
    no-lookahead; cost accounting; cross-lib ≤ 3 pp CAGR)
  - `results.json`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
  - `final_report.md`

## Implementation plan

1. **Build `commodity_tsm.py` pandas engine** — modular TSM signal
   computation on a price dict. For each asset: boolean position
   (1 if trailing-90d return at t-1 > 0 else 0) → r_asset_tsm[t] =
   pos[t] × r_asset[t] + (1 − pos[t]) × rf_d − cost. Aggregate via
   equal-weight (1/N) sum across the inner-join of the N asset return
   indexes. This mirrors iter 049's `gold_tsm.py` closely.
2. **Build `combined_046_plus_csm.py`** — verbatim of iter 049's
   `combine_046_plus_gold` but renamed for commodity TSM.
3. **Build `numpy_reference_iter057.py`** — mirror iter 049's
   `numpy_reference_iter049.py` for the commodity TSM portion only.
4. **TDD specs** (≥ 6 tests):
   - `w_csm=0` reduces exactly to iter 046 net (within 1e-12)
   - `w_046=0` reduces exactly to commodity TSM basket net
   - Single-asset universe test: `commodity_tsm({"GLD": prices})` with
     w_csm at appropriate weight reduces to iter 049/050's gold TSM
     (sanity: same engine on different asset)
   - No-lookahead: position at t depends only on prices ≤ t-1
   - Cost accounting: turnover * cost_bps applied correctly
   - Numpy ref ≡ pandas engine within 3 pp CAGR (G7)
5. **Run backtests on 3 datasets** — single pre-committed cfg, no grid.
   Cumulative `n_trials` advances 4326 → 4327.
6. **Compute gates + score** — adapt iter 049's `compute_gates_and_score.py`.
   Replace `iter046_baseline_dsr` with the actual iter 046 worst-p (0.041
   on edu) for kill B. Add iter 057 vs iter 046 score-comparison for
   kill D. Add corr(r_csm, r_046) check for kill F.
7. **Generate plots** via `plot_helper.py --iter 057`.
8. **Write `final_report.md`** + update `BASE_MEMORY.md`
   (frontmatter `cumulative_n_trials = 4326 + 1 = 4327`; iteration log
   entry; top-K refresh; auto-prune if > 18 KB).

## Pre-committed config

```python
CFG = {
    "cfg_id": "iter046_plus_commodity_tsm_w020",
    # Convex weights — sum to 1.0
    "w_046": 0.80,
    "w_csm": 0.20,
    # Commodity TSM basket params (verbatim iter 049/050 single-asset
    # boolean TSM rule, generalized to a 3-asset equal-weight basket)
    "tsm_universe": ["USO", "UNG", "SLV"],
    "lookback": 90,
    "rf": 0.02,
    "cost_bps": 5.0,
    "rebalance": "daily; per-asset boolean TSM long iff trailing-90d return at t-1 > 0; equal-weight basket; combined with iter 046 stream at 80/20 convex combo",
    "primary_citation": "[risk_parity, ch.5] + [systematic_trading] + Moskowitz-Ooi-Pedersen 2012 + [advances_fin_ml, p.222-223]",
}
```

All hyperparameters are pre-committed: no grid sweep over `w_csm`,
`lookback`, `cost_bps`, or asset universe. Single test, single advance
in `cumulative_n_trials`. The 80/20 weighting is the midpoint between
iter 049 (50/50, score 59) and iter 050 (90/10, score 78); rationale:
iter 050 demonstrated that very-low overlay weight scores higher, and
the basket's equal-weighting provides the per-asset volatility
reduction that single-asset gold TSM lacked. 80/20 is the conservative
default.
