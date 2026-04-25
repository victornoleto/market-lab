# Iteration 055 — Cross-region 5-leg VRP basket (T-bill + 1/5 SPY/QQQ/IWM/EFA/EEM short put-credit-spreads)

## Hypothesis

Extend iter 039's 3-leg US-only basket (SPY/QQQ/IWM at 1/3 each,
score 76 STRONG) to a **5-leg cross-region basket** that simultaneously
shorts the same 5/10 % OTM 21-DTE put credit spread on **SPY, QQQ, IWM,
EFA and EEM**, each at **1/5 of total notional**. T-bill stays at full
collateral; total spread notional sold per unit capital is unchanged at
1.0.

The mechanism: cross-region VRP harvest is structurally similar across
US large-cap (SPY), US tech (QQQ), US small-cap (IWM), developed-ex-US
(EFA), and emerging markets (EEM), but the 5-leg joint distribution has
lower variance than the 3-leg US-only one because ρ(US, EAFE) ≈ 0.6-0.7
and ρ(US, EM) ≈ 0.55-0.65 are materially below ρ(SPY, QQQ) ≈ 0.85 and
ρ(SPY, IWM) ≈ 0.88 within the iter 039 basket
(Asness-Moskowitz-Pedersen 2013 §V; Bakshi-Madan 2006 Table 4). Math
sketch (assuming average pairwise ρ̄_5 ≈ 0.65 vs ρ̄_3 ≈ 0.80):

> σ²_5leg ≈ (1/25) × Σᵢ σᵢ² + 2 × (1/25) × Σᵢ<ⱼ ρᵢⱼ σᵢ σⱼ
> ≈ (1/25) × (5 σ² + 2 × 10 × 0.65 × σ²)
> = (5 + 13)/25 × σ² = 18/25 σ² ≈ 0.72 σ²
> → σ_5leg ≈ 0.85 σ_single
>
> σ²_3leg ≈ (1/9) × (3 σ² + 2 × 3 × 0.80 × σ²) = 7.8/9 σ² ≈ 0.87 σ²
> → σ_3leg ≈ 0.93 σ_single

If mean harvest is preserved (each leg's expected variance risk premium
is positive — ~3-5 % of underlying notional per year per Bondarenko 2014
Table II — and all 5 indices are liquid enough to support spread
writing), basket Sharpe ≈ Sharpe_single / 0.85 = +18 % vs single-asset
iter 026 (Sharpe edu 1.13 → ~1.33), or +9 % vs 3-leg iter 039
(Sharpe edu 1.14 → ~1.24, where the iter 039 actual was 1.14). Edu DSR
worst-p ought to compress from 0.075 toward < 0.05 strict-PASS, lifting
DSR criterion from 10/15 → 15/15 (+5 score points → 81 STRONG).

Important: this iter does NOT attempt to break the **CAGR floor**
structural ceiling — adding more equal-notional legs cannot change the
underlying T-bill-collateral CAGR floor (~5-7 %/yr), which is documented
in BASE_MEMORY as "VRP-harvester family 76 ceiling … structural to
T-bill collateral". The kill criteria below are explicit about the 81
soft ceiling this prediction implies.

## Primary citation

`[volatility_trading, p.218]` — Sinclair (2013), *Volatility Trading*
2nd ed., Wiley, ch.7-8: "diversifying across multiple short-vol books
reduces idiosyncratic blow-up risk while preserving the systematic
short-vol premium." Foundational textual citation for cross-asset VRP
harvest, applied here in its broadest US+international form.

## Additional citations

- `[volatility_trading, ch.3, p.41, p.217]` — Sinclair (2013) — VRP
  mechanics + SPX kurtosis 21.3 + canonical short-vol-harvest rule
  (preserved from iter 026/039 base).
- **Bakshi & Madan (2006)**, *J. Financial Economics* 81(2): 471-518.
  DOI 10.1016/j.jfineco.2005.10.006. Cross-sectional implied-vol
  premia decomposition; Table 4 documents SPX/NDX/RUT/EAFE/EM
  realised-implied vol gaps and pairwise ρ ≈ 0.55-0.85 across these
  index families.
- **Bondarenko (2014)**, *Quarterly Journal of Finance* 4(3): 1450015.
  DOI 10.1142/S2010139214500153. "Why Are Put Options So Expensive?"
  — empirical SPX VRP magnitude; cross-index extension is plausible
  per Bakshi-Madan §V.
- **Carr & Wu (2009)**, *Review of Financial Studies* 22(3): 1311-1341.
  DOI 10.1093/rfs/hhn038. Variance risk premia, structural foundation
  preserved from iter 026/039.
- **Driessen, Maenhout & Vilkov (2009)**, *J. Finance* 64(4): 1377-1406.
  DOI 10.1111/j.1540-6261.2009.01467.x. "The Price of Correlation
  Risk: Evidence from Equity Options" — cross-sectional decomposition
  of index VRP into individual + correlation risk components,
  motivating cross-region diversification of short-vol books.
- **Asness, Moskowitz & Pedersen (2013)**, *J. Finance* 68(3): 929-985.
  DOI 10.1111/jofi.12021. "Value and Momentum Everywhere" — cross-
  region orthogonality framework; Table 1 documents EAFE/EM equity
  return diversification benefits vs US-only baskets.
- **Israelov & Klein (2016)**, AQR working paper SSRN 2784825. "Risk
  and Return of Equity Index Collar Strategies" — practical multi-leg
  short-vol pricing/turnover considerations applicable to international
  index ETFs.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule preservation.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).

## Edge source

SPY 1× buy-and-hold extracts equity-risk-premium only on the US large-
cap factor; cross-region 5-leg VRP basket extracts variance-risk-premium
across **five uncorrelated stress clusters** (US-broad, US-tech,
US-small, EAFE, EM), generating positive expected return uncorrelated
with directional equity drift while diversifying across distinct tail-
event clusters (e.g., 2000-tech-bust hits NDX hardest; 2008-financial
hits all 5 simultaneously; 2018-Q4 small-caps; 2010-12 EU sovereign
hits EFA; 2015 China hits EEM). This is conceptually orthogonal to
iter 037/038's diversified-equity-stack mechanism — VRP is a fee for
insurance-writing service, not a directional bet — and orthogonal to
iter 039's US-only basket via the additional EAFE/EM legs whose
pairwise ρ with US ≈ 0.55-0.70 < 0.80-0.88 within US-only set.

## Datasets

- **educational** (SPY/QQQ/IWM/EFA/EEM + VIX from 2006-01-04 to
  2026-04-14): ~20y window. EFA/EEM start 2003-08-20 in Tiingo cache;
  joint window with VIX is 2006-01-04 onwards (matches iter 039 start
  date for direct comparability). Includes 2008 GFC + 2020 COVID + 2022
  rate-hike. VIX scaled by 1.0 (SPY), 1.10 (QQQ as VXN proxy), 1.25
  (IWM as RVX proxy), 1.05 (EFA as VXEFA proxy), 1.30 (EEM as VXEEM
  proxy). Scales for EFA/EEM derived from historical CBOE VXEFA/VXEEM
  vs VIX ratios (CBOE archives 2008-2018: VXEFA/VIX ≈ 0.95-1.10
  median 1.05; VXEEM/VIX ≈ 1.20-1.40 median 1.30).
- **spy_real** (same SPY/QQQ/IWM/EFA/EEM + VIX from 2009-06-26): 17y
  post-GFC. Cleaner test of basket Sharpe edge in the modern regime
  where iter 039 already cleared 6/7 cross-dataset.
- **ndx_real** (same SPY/QQQ/IWM/EFA/EEM + VIX from 2010-02-16): 16y
  window. Benchmark is QQQ (Sharpe 0.955); basket includes QQQ but
  adds 4 cross-region legs — tests whether basket preserves iter 039's
  ndx 7/7 + DSR PASS while improving spy/edu DSR via diversification.

The same single basket strategy runs on all 3 windows. Each dataset
differs only by the window cut and the benchmark mapped in scoring.py
(`educational` → SPYSIM 0.68; `spy_real` → SPY 0.90; `ndx_real` → QQQ
0.955). This convention matches iter 026/027/028/039.

## Kill criteria (pre-committed)

If at the end of Stage 3 ANY of the following holds, this hypothesis is
falsified regardless of secondary metrics (do NOT post-hoc tune
parameters):

- **Kill A (basket-corrupts-Sharpe)**: 5-leg Sharpe < iter 039 Sharpe
  by ≥ 0.10 on **≥ 2 of 3 datasets**. Indicates that the IV scaling
  proxies for EFA (×1.05) and EEM (×1.30) introduce harvest-net drag
  larger than the diversification benefit (e.g., EM volatility
  asymmetry kills EEM leg's net harvest).
- **Kill B (DSR-no-improvement)**: edu DSR worst-p > 0.075 (no
  improvement over iter 039's edu p=0.075) AND ndx DSR p > iter 039's
  0.0059 (regression on ndx). Diversification did not break the DSR
  ceiling AND damaged the prior best.
- **Kill C (MDD-blows-out)**: any dataset's MDD > 35 % (same threshold
  as iter 039). Indicates basket aggregates equity tail risk instead
  of diversifying it (would imply joint-stress ρ ≈ 1).
- **Kill D (G7-cross-lib)**: max abs |CAGR_pandas − CAGR_numpy| > 3 pp
  on any dataset. Numerics broken; reject regardless.
- **Kill E (score-regression-vs-iter-039)**: score < 73 (iter 039 was
  76; threshold = 76 − 3 = 73). Iteration is materially worse than
  the 3-leg base.
- **Kill F (sub-window-collapse)**: < 6/9 sub-windows Sharpe > 0
  across 3 datasets × 3 sub-windows each. Robustness collapse.

If multiple kills fire, document all but classify per the most
conservative tier in scoring.

**Soft ceiling acknowledgement**: based on iter 039's 76 score with full
Sharpe edge / full MDD ceiling / full robustness / G7 perfect, the only
score axes left are DSR (10 → 15, +5 = 81) and CAGR (0 → 5/10/15, +5 to
+15). The 5-leg basket cannot break CAGR floor structurally
(T-bill-collateral cap), so the predicted score range is **76-81**
(STRONG, not WINNER). If the iter scores < 76, the broader-VRP path is
fully closed; if it scores 79-81, the path is confirmed at the same
ceiling as iter 039 with cross-region diversification benefit
quantified.

## Expected budget

- **Configs to test**: **1** (single pre-committed cfg
  `vrp_basket_eq5_5_10_1m_5regions`); cumulative_n_trials advances
  4324 → 4325.
- **Wall-time estimate**: ~30-60 min (5× iter 026 pricer cost,
  pure-numpy, ~5100 bars × 5 legs ≈ 25,500 BS evaluations per dataset).
- **Files to create**:
  1. `vrp_basket_5leg.py` — pandas implementation; 5-leg generalization
     of iter 039's `compute_vrp_basket_returns` (same signature, just
     more keys in `prices`/`weights`/`iv_scales`).
  2. `numpy_reference_basket_5leg.py` — pure-numpy reference for G7
     parity (mirror iter 039 numpy).
  3. `run_backtests.py` — single pre-committed cfg, 3 datasets,
     writes `results.json` with `returns_series` populated for plot
     helper compatibility.
  4. `compute_gates_and_score.py` — 7-gate battery + scoring + writes
     `verdict.json`.
  5. `final_report.md` + plot PNGs (auto-generated from
     `plot_helper.py --iter 055`).
- **TDD**: a small unit test (`tests/test_vrp_basket_5leg_iter055.py`)
  verifying that calling `compute_vrp_basket_returns` from iter 039's
  `vrp_basket.py` with 5 tickers + matching weights/iv_scales produces
  the SAME daily returns as the new 5-leg implementation (architectural
  identity), AND a single-asset reduction case (weights = (1,0,0,0,0)
  + spy iv_scale=1.0 reduces to iter 026 single-asset case).

## Implementation plan

1. Reuse iter 039's `compute_vrp_basket_returns` directly — its
   signature already accepts `dict[str, pd.Series]` for prices,
   weights and iv_scales. The function is generic over arbitrary leg
   count. **No new pandas implementation needed**, just a thin run
   script that wires 5 tickers instead of 3.
2. Mirror iter 039's `numpy_reference_basket.py` adapted to accept N
   tickers (parameterized over `len(tickers)` rather than hard-coded 3).
3. `run_backtests.py` — load SPY/QQQ/IWM/EFA/EEM Tiingo + VIX macro;
   align on inner-join (start = 2006-01-04 educational; later starts
   for spy_real/ndx_real); run 1 cfg on 3 datasets; persist
   `results.json` with the canonical `returns_series` schema.
4. Add `tests/test_vrp_basket_5leg_iter055.py` minimal TDD spec (≥ 3
   test cases: shape parity vs iter 039 with 3-leg subset; single-
   asset reduction; sign-flip identity).
5. Run `compute_gates_and_score.py` (mirror iter 039's verbatim modulo
   `CUMULATIVE_N_TRIALS = 4324 + 1 = 4325`).
6. Run `plot_helper.py --iter 055` to generate
   `plot_vs_benchmark_*.png` for spy_real and ndx_real.
7. Author `final_report.md` honestly — use `score_strategy` result, do
   NOT post-hoc rationalize if kill criteria fire.

## Why this is structurally novel vs DEAD_ENDS.md

- **Not a static-stack family** (closed iter 015/035/036/037/038): no
  fixed equity:bond:gold weights, no leverage on equity, no regime
  gate.
- **Not iter 026/027/028/029/030/031** (single-asset SPY VRP family
  closed at 76): basket is **structurally multi-underlying**, not a
  tweak of harvest_notional/leverage/gate parameters.
- **Not iter 039** (3-leg US-only basket closed at 76): adds 2
  cross-region legs (EFA + EEM) with materially lower pairwise ρ vs
  US legs (0.55-0.70 vs 0.80-0.88), structurally different universe.
- **Not iter 040** (vol-target on 039 closed at 69): no σ⁻² overlay
  applied; preserves raw VRP harvest mechanics.
- **Not iter 032** (composed iter 015 + iter 031 VRP overlay closed at
  72 due to ρ_SPY=0.97): this iter has **NO equity stack underneath**;
  basket IS the strategy. The σ²_port absorption mechanism is
  structurally absent.
- **Not iter 054** (cross-sectional momentum on Tiingo): VRP is NOT
  cross-sectional ranking; mechanism is cross-asset variance-risk-
  premium harvest, not relative momentum on stocks.

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "vrp_basket_eq5_5_10_1m_5regions",
    "rf": 0.02,
    "harvest_notional": 1.0,           # total spread notional sold = 1.0
    "weights": {"SPY": 1/5, "QQQ": 1/5, "IWM": 1/5, "EFA": 1/5, "EEM": 1/5},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25, "EFA": 1.05, "EEM": 1.30},
    "k_long_pct": 0.95,                # 5 % OTM long (preserved from iter 026/039)
    "k_short_pct": 0.90,               # 10 % OTM short (preserved)
    "dte_days": 21,                    # monthly roll (preserved)
    "cost_bps_per_roll": 5.0,          # bps per leg per roll (preserved)
}
```

This is the **only** configuration that will be tested. No grid, no
sweep, no post-hoc parameter tuning. If kill criteria fire, the
hypothesis is falsified — DEAD_ENDS.md gets a new section (broader-
region VRP basket joins iter 039 in confirming the family ceiling).
