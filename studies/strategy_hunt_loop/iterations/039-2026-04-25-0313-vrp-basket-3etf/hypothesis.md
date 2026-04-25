# Iteration 039 — Cross-asset VRP basket (T-bill + 1/3 SPY/QQQ/IWM short put-credit-spreads)

## Hypothesis

Extend iter 026's single-asset VRP-primary harvester (T-bill collateral
+ short SPY 5/10 % OTM 21-DTE put credit spread, `harvest_notional=1.0`)
into a **3-leg basket** that simultaneously shorts the same 5/10 % OTM
21-DTE put credit spread on **SPY, QQQ, and IWM**, each at **1/3 of total
notional**. T-bill stays at full collateral; total spread notional sold
per unit capital is unchanged at 1.0.

The mechanism: cross-sectional VRP harvest is structurally similar
across large-cap (SPY), large-cap-tech (QQQ), and small-cap (IWM) but
the joint distribution has lower variance than any single leg because
ρ(VIX, VXN, RVX) ≈ 0.7-0.85 < 1.0 (Bakshi-Madan 2006 §V; Driessen-
Maenhout-Vilkov 2009 §III). Math:

> σ²_basket = (1/9) × Σᵢ σᵢ² + 2 × (1/9) × Σᵢ<ⱼ ρᵢⱼ σᵢ σⱼ
> ≈ (1/9) × (3 σ² + 2 × 3 × 0.75 × σ²)
> = (7.5/9) × σ² ≈ 0.83 σ²
> → σ_basket ≈ 0.91 σ_single

If mean harvest is preserved (each leg's expected variance risk premium
is positive and roughly 4-6 % of underlying notional per year per
Bondarenko 2014 Table II), basket Sharpe ≈ Sharpe_single / 0.91 ≈
+10 % vs iter 026 — pushing iter 026's edu Sharpe from 1.13 toward
~1.24 and edu DSR worst-p from 0.083 toward ~0.05 strict-PASS. The
ndx_real basket slightly reduces the QQQ-only Sharpe (because basket
includes lower-VRP IWM) but should preserve the iter 026 ndx 7/7 +
DSR PASS pattern.

## Primary citation

`[volatility_trading, p.218]` — Sinclair (2013), *Volatility Trading*
2nd ed., Wiley, ch.7-8: "diversifying across multiple short-vol books
reduces idiosyncratic blow-up risk while preserving the systematic
short-vol premium." This is the textual foundation for cross-asset
VRP harvest.

## Additional citations

- `[volatility_trading, ch.3, p.41, p.217]` — Sinclair (2013) — VRP
  mechanics + SPX kurtosis 21.3 + canonical short-vol-harvest rule
  (preserved from iter 026 base).
- **Bakshi & Madan (2006)**, *J. Financial Economics* 81(2): 471-518.
  DOI 10.1016/j.jfineco.2005.10.006. Cross-sectional implied-vol
  premia decomposition; ρ across SPX/NDX/RUT ≈ 0.75-0.85.
- **Bondarenko (2014)**, *Quarterly Journal of Finance* 4(3): 1450015.
  DOI 10.1142/S2010139214500153. "Why Are Put Options So Expensive?"
  — empirical VRP magnitude on SPX puts; same mechanism extends to
  liquid index options.
- **Carr & Wu (2009)**, *Review of Financial Studies* 22(3): 1311-1341.
  DOI 10.1093/rfs/hhn038. Variance risk premia, structural foundation
  preserved from iter 026.
- **Driessen, Maenhout & Vilkov (2009)**, *J. Finance* 64(4): 1377-1406.
  DOI 10.1111/j.1540-6261.2009.01467.x. "The Price of Correlation
  Risk: Evidence from Equity Options" — cross-sectional decomposition
  of index VRP into individual + correlation risk components.
- **Asness, Moskowitz & Pedersen (2013)**, *J. Finance* 68(3): 929-985.
  DOI 10.1111/jofi.12021. "Value and Momentum Everywhere" —
  cross-asset orthogonality framework; basket diversification rationale.
- **Israelov & Klein (2016)**, AQR working paper ssrn=2784825. "Risk
  and Return of Equity Index Collar Strategies" — practical multi-leg
  short-vol pricing/turnover considerations.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule preservation.

## Edge source

SPY 1× buy-and-hold extracts equity-risk-premium only; cross-asset VRP
basket extracts variance-risk-premium across **three uncorrelated stress
profiles** (large-cap broad, tech-heavy, small-cap), generating positive
expected return uncorrelated with directional equity drift while
diversifying across distinct tail-event clusters (e.g., 2000-tech-bust
hits NDX hardest; 2008-financial-stress hits all 3; 2018-Q4 affected
small-caps disproportionately). This is conceptually orthogonal to
iter 037/038's diversified-equity-stack mechanism — VRP is a fee for
insurance-writing service, not a directional bet.

## Datasets

- **educational** (SPY/QQQ/IWM + VIX from 2006-01-03 to 2026-04-14):
  ~20y window includes 2008 GFC + 2020 COVID + 2022 rate-hike. Tests
  whether basket harvest survives the worst-known vol stress event
  (2008 Q4 cluster). VIX scaled by 1.0 (SPY), 1.10 (QQQ as VXN proxy),
  1.25 (IWM as RVX proxy — historical RVX/VIX ratio ≈ 1.20-1.30).
- **spy_real** (same SPY/QQQ/IWM + VIX from 2009-06-25): 17y post-GFC.
  Cleaner test of basket Sharpe edge in the modern regime where iter
  026 already cleared 7/7+DSR PASS on ndx alone.
- **ndx_real** (same SPY/QQQ/IWM + VIX from 2010-02-12): 16y window.
  This dataset's benchmark is QQQ (Sharpe 0.955); basket includes QQQ
  but adds SPY+IWM diversification — tests whether basket preserves
  iter 026's ndx 7/7+DSR PASS (p=0.038) while improving spy/edu DSR.

The same single basket strategy runs on all 3 windows. Each dataset
differs only by the window cut and the benchmark mapped in scoring.py
(`educational` → SPYSIM 0.68; `spy_real` → SPY 0.90; `ndx_real` → QQQ
0.955). This convention matches iter 026/027/028.

## Kill criteria (pre-committed)

If at the end of Stage 3 ANY of the following holds, this hypothesis is
falsified regardless of secondary metrics (do NOT post-hoc tune
parameters):

- **Kill A (basket-corrupts-Sharpe)**: basket Sharpe < iter 026 Sharpe
  by ≥ 0.10 on **≥ 2 of 3 datasets**. Indicates that the IV scaling
  proxies (VIX×1.10 for QQQ, VIX×1.25 for IWM) introduce harvest-net
  drag larger than the diversification benefit.
- **Kill B (DSR-no-improvement)**: DSR worst-p > 0.10 across the 3
  datasets (i.e., no dataset shows DSR PASS, regression vs iter 026's
  ndx p=0.038). Diversification did not break the DSR ceiling.
- **Kill C (MDD-blows-out)**: any dataset's MDD > 35 % (over 4× iter
  026's worst MDD of 16.8 %). Indicates basket aggregates equity tail
  risk instead of diversifying it (would imply ρ(stress) ≈ 1).
- **Kill D (G7-cross-lib)**: max abs |CAGR_pandas − CAGR_numpy| > 3 pp
  on any dataset. Numerics broken.
- **Kill E (score-regression-vs-iter-026)**: score < 70 (iter 026 was 76).
  Iteration is strictly worse than the single-asset base.
- **Kill F (sub-window-collapse)**: < 6/9 sub-windows Sharpe > 0
  across 3 datasets × 3 sub-windows each. Robustness collapse.

If multiple kills fire, document all but classify per the most
conservative tier in scoring.

## Expected budget

- **Configs to test**: **1** (single pre-committed cfg
  `vrp_basket_eq3_5_10_1m`); cumulative_n_trials advances 4303 → 4304.
- **Wall-time estimate**: ~30-60 min (3× iter 026 pricer cost, all
  pure-numpy, ~6300 bars × 3 legs ≈ 18,900 BS evaluations per dataset).
- **Files to create**:
  1. `vrp_basket.py` — pandas implementation (3-leg version of iter
     026's `compute_vrp_primary_returns`).
  2. `numpy_reference_basket.py` — pure-numpy reference for G7 parity.
  3. `run_backtests.py` — single pre-committed cfg, 3 datasets,
     writes `results.json` with `returns_series` populated for plot
     helper compatibility.
  4. `compute_gates_and_score.py` — 7-gate battery + scoring + writes
     `verdict.json`.
  5. `final_report.md` + plot PNGs (auto-generated from
     `plot_helper.py`).
- **TDD**: a small unit test verifying `compute_vrp_basket_returns`
  reduces to iter 026's single-asset case when `weights = (1, 0, 0)`
  and one leg's iv_scale=1.0 (sanity-check on architecture).

## Implementation plan

1. Create `vrp_basket.py` exposing
   `compute_vrp_basket_returns(prices_dict, vix, *, rf, harvest_notional,
   weights, iv_scales, k_long_pct, k_short_pct, dte_days,
   cost_bps_per_roll)` — calls iter 020's
   `compute_put_spread_daily_returns` 3 times (one per ticker), aligns
   on inner-join, weighted-sum the overlays with sign-flip for
   short-writer, adds T-bill daily.
2. Mirror iter 026's `numpy_reference_vrp.py` for cross-lib parity
   (G7) — pure numpy + `math.erf`, 3-leg version.
3. `run_backtests.py` — load SPY/QQQ/IWM Tiingo + VIX macro; align;
   run 1 cfg on 3 datasets; persist `results.json` with the canonical
   `returns_series` schema (per existing iters 015/016/021/026/035/037).
4. Add a `tests/test_vrp_basket_iter039.py` minimal TDD spec (≥ 3
   test cases: shape, single-asset reduction, sign-flip identity).
5. Run `compute_gates_and_score.py` (mirrors iter 026 verbatim modulo
   `CUMULATIVE_N_TRIALS = 4303 + 1 = 4304`).
6. Run `plot_helper.py --iter 039` to generate
   `plot_vs_benchmark_*.png` for spy_real and ndx_real.
7. Author `final_report.md` honestly — use `score_strategy` result, do
   NOT post-hoc rationalize if kill criteria fire.

## Why this is structurally novel vs DEAD_ENDS.md

- **Not a static-stack family** (closed iter 015/035/036/037/038): no
  fixed equity:bond:gold weights, no leverage on equity, no regime gate.
- **Not iter 026/027/028/029/030/031** (single-asset SPY VRP family
  closed at 76 ceiling per BASE_MEMORY): basket is **structurally
  multi-underlying**, not a tweak of harvest_notional/leverage/gate
  parameters of single-asset SPY VRP.
- **Not iter 032** (composed iter 015 + iter 031 VRP overlay closed at
  72 due to put-spread ρ_SPY ≈ 0.97 absorbing into σ²_port): this iter
  has NO equity stack underneath; the basket IS the strategy. The
  σ²_port absorption mechanism is structurally absent.
- **Open path explicitly listed in DEAD_ENDS.md (lines 2529-2531)**:
  "C-VRP IWM (Russell 2000 small-cap put-credit-spread VRP) on iter
  015 base — small-cap stress decorrelated from large-cap. Citation:
  KMPV 2018 + AMP 2013."  This iter generalises that pointer to a
  3-asset basket WITHOUT the iter-015 base (which would re-trigger
  σ²_port absorption per iter 032).

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "vrp_basket_eq3_5_10_1m",
    "rf": 0.02,
    "harvest_notional": 1.0,           # total spread notional sold = 1.0
    "weights": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,                # 5 % OTM long (preserved from iter 026)
    "k_short_pct": 0.90,               # 10 % OTM short (preserved)
    "dte_days": 21,                    # monthly roll (preserved)
    "cost_bps_per_roll": 5.0,          # bps per leg per roll (preserved)
}
```

This is the **only** configuration that will be tested. No grid, no
sweep, no post-hoc parameter tuning. If kill criteria fire, the
hypothesis is falsified — DEAD_ENDS.md gets a new section.
