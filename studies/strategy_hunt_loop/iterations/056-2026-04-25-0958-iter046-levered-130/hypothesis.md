# Iteration 056 — Levered iter 046 1.3× notional with 3.5% retail borrow cost

## Hypothesis

iter 046 (TOP-K #1 at score 85, 0/6 kills) leaves **CAGR floor as the
sole gap to WINNER** (`c4 = 0/15` on frozen benchmarks; only edu was
0.02pp short). Sharpe (1.20/1.32/1.38), MDD (18/15/15%), DSR worst-p
(0.041), gates (7/7/7) all clear or exceed thresholds with margin. The
unexploited margin is **MDD slack**: ceilings allow up to 60.14/38.70/
40.12% MDD, but the strategy uses only 30/40/40% of that budget. A
uniform 1.3× notional on the iter 046 combined return stream — financed
at a realistic retail margin rate — converts that unused MDD slack into
CAGR while preserving all gates.

This is the **sole untested axis** on iter 046 (BASE_MEMORY closes 5
other axes: 044 input regime / 047 weight sweep / 048 output VIX gate /
049 additive gold TSM / 050 Markowitz w*≈0.10).

Mechanically `r_lev[t] = lev × r_046[t] - (lev - 1) × (1 + borrow)^{1/252}
- 1)` is a pure-leverage operation: Sharpe is preserved modulo a small
spread drag, σ scales linearly with `lev`, and CAGR scales by `lev` minus
geometric drag `lev(lev-1)σ²/2` minus borrow cost `(lev-1) × borrow`.

**Predicted metrics** (analytic, σ inferred from iter 046's measured
Sharpe and CAGR):

| dataset | Sharpe pred | CAGR pred (1.3× @ 3.5% borrow) | floor | MDD pred | ceiling |
|---|---|---|---|---|---|
| educational | 1.14 | 10.79% | 9.18 ✓ | 23.4% | 60.14 ✓ |
| spy_real | 1.26 | 11.17% | 11.98 ✗ (−0.81pp) | 19.8% | 38.70 ✓ |
| ndx_real | 1.32 | 11.58% | 15.35 ✗ (−3.77pp) | 18.9% | 40.12 ✓ |

**Predicted score** (frozen bench, with c6 robustness bonus likely 5/5):
- c1 Sharpe edge: 25 (3/3 still beat bench+0.10 with margin)
- c2 Gates: 25 (7/7×3 expected; G7 0.00pp; G2 DSR likely PASS at <0.05
  given Sharpe ~1.14 and n_trials 4326)
- c3 DSR: 15 (worst-p still <0.05 expected)
- c4 CAGR floor: 5 (1/3 PASS — edu only)
- c5 MDD ceiling: 15 (3/3 well under)
- c6 Robustness: 5 (rolling Sharpe scales linearly, sub-window
  positivity preserved)
- **Total predicted: 90 STRONG** (caps at STRONG because winner_conds
  fails: only 1/3 CAGR floor < 2/3 minimum).

**Edge over iter 046**: +5 pts on c4 (was 0, now 5). New TOP-K #1.

## Primary citation

`[risk_parity, ch.5]` — iter 046 base architecture inherited verbatim
(Asness-Frazzini-Pedersen risk-parity stack with regime-conditional
weight tilts at preserved leverage).

## Additional citations

- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline;
  the leverage transform must produce numpy/pandas parity.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with
  cumulative `n_trials` 4325 → 4326 (this iter adds 1).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate (G6).
- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  harvesting (iter 039 component, inherited via iter 046).
- `[advances_fin_ml, p.162-164]` — no-lookahead lag (iter 041 VIX[t-1]
  convention, inherited via iter 046).
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 — VIX
  as ex-ante risk regime indicator (iter 041 component).
- Markowitz (1952), JoF 7(1) 77-91 — convex-combination basis (inherited).
- Wermers (2003), "Are mutual fund shareholders compensated for active
  management 'bets'?", Working paper — broker margin spreads as part of
  realistic active-strategy cost models.
- IBKR Pro Tier 1 margin schedule (public), <https://www.interactivebrokers.com/en/trading/margin-rates.php> —
  T-bill benchmark + 1.5% institutional spread → 3.5% effective borrow
  rate at 2025 yields. Used as a conservative-honest borrow cost.
- Frazzini-Pedersen (2014), "Betting Against Beta", JFE 111(1) 1-25,
  DOI 10.1016/j.jfineco.2013.10.005 — leverage frictions (margin,
  borrow rate spreads) compress Sharpe of levered low-vol strategies.
  Justifies modeling spread cost rather than assuming risk-free
  borrowing.

## Edge source

SPY 1x buy-hold buys EXP(market) at 1.0× notional. iter 046 buys two
independently-positive-Sharpe streams (regime-gated 3-leg stack +
cross-asset VRP) at effective ~1× exposure with measured Sharpe
1.20/1.32/1.38. iter 056 levers that combined stream to 1.3× and
finances the borrow at retail margin rate. Because Sharpe is preserved
under leverage (modulo small spread drag), the levered strategy
preserves the iter 046 statistical edge while **converting MDD slack
into CAGR** — gaining ~1.5pp CAGR per 0.1× leverage unit at the cost
of ~0.5pp MDD increase. The mechanism is orthogonal to all prior
iter 046-family experiments (044/047-050).

## Datasets

- **educational** (2006-01-03 → 2026-04-15, ≈20y): inherited from
  iter 046; tests the levered stream against 2008+2020+2022 stress with
  the SPY-aligned synthetic benchmark (Sharpe 0.629).
- **spy_real** (2009-06-25 → 2026-04-15, ≈17y): primary frozen-bench
  window; tests whether 1.3× clears the 11.98% CAGR floor.
- **ndx_real** (2010-02-12 → 2026-04-15, ≈16y): bench QQQ at 19.18%
  CAGR; expected FAIL on CAGR floor at 1.3× (predicted 11.58 < 15.35);
  documents which leverage level would pass.

## Kill criteria (pre-committed)

| kill | observable | threshold | interpretation |
|---|---|---|---|
| **A** Sharpe regress | datasets where `Sharpe_056 < Sharpe_046 − 0.15` | ≥ 2 of 3 | borrow drag larger than spread model, or numerical noise |
| **B** Score regress | `score_056 < 85` | < 85 | leverage axis structurally inferior; iter 046 is Pareto-opt |
| **C** MDD breach | `MDD_056 > bench + 5pp` on any dataset | > 60.14 / 38.70 / 40.12% | leverage scales MDD super-linearly (path-dep tail risk) |
| **D** DSR regress | `worst_p_056 ≥ 0.05` | ≥ 0.05 | trial penalty (n+=1) + spread drag pushes p above winner-cond cutoff |
| **E** G7 cross-lib | `Δ pp > 3.0` on any dataset | > 3.0 pp | engine bug in leverage transform |
| **F** No CAGR gain on edu | `CAGR_056_edu < 0.0918` | < 9.18% | financing cost wipes leverage gain on the slowest-growth dataset |

If **2 or more** kills fire, hypothesis is falsified. If only kill B
fires (score < 85), iter 046 retains TOP-K #1 and iter 056 closes the
"external leverage on iter 046" axis at the predicted but un-confirmed
ceiling. If only kill F fires, the structural finding is "borrow cost
> raw CAGR on low-vol composition — leverage axis closed for any
iter 046-family strategy".

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid; matches
  iter 045/046/051/053 single-shot pattern).
- **Wall-time**: ~15-25 min (3-dataset run reuses iter 046's compute
  flow + a thin leverage transform; gates ~10 min for bootstrap).
- **Files to create**:
  - `hypothesis.md` (this file)
  - `levered_iter046.py` — pandas leverage wrapper around iter 046's
    `compute_combined_returns`
  - `numpy_reference_levered_046.py` — pure-numpy reference
    (composes iter 046 numpy ref + identical leverage transform)
  - `run_backtests.py` — single cfg, 3 datasets driver
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation
    (adapted from iter 046)
  - `tests/test_iter_056_levered.py` — TDD specs
  - `results.json`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
  - `final_report.md`

## Implementation plan

1. **Build `levered_iter046.py`** — defines `apply_leverage(r, lev,
   borrow_rate_annual)` and `compute_levered_returns(...)` that calls
   iter 046's `compute_combined_returns` then applies leverage.
2. **Build `numpy_reference_levered_046.py`** — identical leverage
   transform on the numpy reference output.
3. **TDD specs** (≥6 tests):
   - `lev=1.0` reduces exactly to iter 046 net (within 1e-12)
   - `lev=1.0` → identity regardless of `borrow_rate_annual`
   - `lev <= 0` raises `ValueError`
   - `borrow_rate_annual < 0` raises `ValueError`
   - leverage transform: `apply_leverage([0.01, -0.005], lev=2,
     borrow=0)` equals `[0.02, -0.01]`
   - leverage transform with borrow: subtract `(lev-1) × ((1+borrow)^(1/252)-1)`
     per bar
   - numpy ref ≡ pandas engine within 3 pp CAGR (G7)
4. **Run backtests on 3 datasets** — single cfg, no grid. Cumulative
   n_trials advances 4325 → 4326.
5. **Compute gates + score** — adapted from iter 046's
   `compute_gates_and_score.py`. Replace iter 045 baseline with iter 046
   baseline for kill B (< 85 instead of < 81).
6. **Generate plots** via `plot_helper.py --iter 056`.
7. **Write `final_report.md`** + update `BASE_MEMORY.md`
   (cumulative_n_trials = 4326; iteration log entry; top-K refresh
   if score ≥ 79).

## Pre-committed config

```python
CFG = {
    "cfg_id": "iter046_levered_130_borrow_350bps",
    # External leverage on the iter 046 combined stream
    "lev": 1.3,
    "borrow_rate_annual": 0.035,  # T-bill 2.0% + IBKR Pro Tier 1 spread 1.5%
    # iter 046 sub-strategy params (verbatim — no inheritance perturbation)
    "w_041": 0.5,
    "w_039": 0.5,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # 1.50× total
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # 1.40× total
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights_039": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales":   {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "rebalance": "daily, 1.3× notional on iter 046 50/50 combined stream, financed at 3.5%",
    "funding_cost_modeled": True,
    "primary_citation": "[risk_parity, ch.5] + [advances_fin_ml, p.31-34]",
}
```

All sub-strategy hyperparameters are VERBATIM from iter 046's
TOP-K #1 cfg `iter039_on_iter041_50_50` — only `lev` and
`borrow_rate_annual` are new. The 3.5% borrow rate is fixed from IBKR
Pro Tier 1 (T-bill + 1.5% spread) and is NOT optimized — pre-committed
to a realistic retail-broker rate, not a synthetic favorable choice.
