# iter 001 — Meta walk-forward, max-Sharpe over S1-S5 universe

**Hypothesis:** A monthly walk-forward solver maximizing Sharpe over the
trailing 36 months across 5 pre-validated sleeves can produce a portfolio
whose Sharpe edge ≥ +0.05 vs F1+SPLIT (incumbent) in ≥ 2/3 datasets, with
MDD ≤ MDD(F1+SPLIT) + 3pp on ≥ 2/3 datasets.

If the WF allocation degenerates to ~constant weights identical to F1+SPLIT,
or the edge fails to materialize, this iter rules out the methodology under
the conservative (max-Sharpe) variant. iter 002 will then test the max-CAGR
(Aggressive) variant.

## Universe (locked, no synth introduction)

| ID | Source iter | selected_config | description |
|----|-------------|-----------------|-------------|
| S1 | iter 043 | `f1_split_baseline` | NTSX 25 / GDE 25 / KMLM 17.5 / DBMF 17.5 / TLT 15 — FINAL PICK incumbent |
| S2 | iter 023 | `tlt_mod_25_25_35_15` | NTSX 25 / GDE 25 / KMLM 35 / TLT 15 — substantive +signal vs iter 011 |
| S3 | iter 020 | `aw_browne_25252525` | Browne 4-asset 25/25/25/25 — defensive low-MDD |
| S4 | iter 040 | `f3_spmo_5_subKMLM` | F3 hybrid w/ SPMO US momentum tilt |
| S5 | iter 041 | `f7_lite` | F7 stacked managed futures heavy |

## Solver parameters (locked, bestfolio-canonical)

- Lookback: 36 months
- Rebalance: monthly (last trading day per month present)
- Bounds: 0 ≤ w_i ≤ 0.40
- Equality: ∑ w = 1
- Embargo: 21 calendar days (own addition vs bestfolio)
- Objective: max-Sharpe (Conservative variant)
- Strict lookback: True (skip warmup until 36mo data available)

## Datasets (3, parity with long_term_portfolio)

- `lh_56y` — full available (intersected: 2000-01-04 to 2026-02-27, ~26y)
- `vt_real` — VTSIM proxy 17y (2008-06+)
- `ndx_real` — QQQ Tiingo 16y (2010-02+)

## Gates

Per `SPEC.md` §5:

1. **Sharpe edge vs S1** ≥ +0.05 in ≥ 2/3 datasets — primary screen
2. **MDD vs S1** ≤ +3pp in ≥ 2/3 datasets
3. **DSR p-value** < 0.05 with cumulative n_trials (long_term_portfolio's
   156 + this iter's 1 = 157)
4. **Walk-forward 8-fold** ≥ 6/8 winners on portfolio returns
5. **Bootstrap 99.9% CI** for annualized return: low > 0
6. **PBO** — DEFERRED to iter 003 (requires K ≥ 2 configs; this iter has 1)
7. **Cross-lib (vectorbt vs bt)** — DEFERRED to iter 004

Decision logic:
- All §1-§5 pass → iter 002 max-CAGR variant
- §1 fails (no edge) → DEAD_END (kill criterion K1 partial)
- §2 fails but §1 passes → iter 002 with turnover/MDD penalty
- §4 fails (≤ 5/8 WF winners) → fragility flag, iter 002 with shorter
  lookback (24mo) to test stability

## Kill criteria explicit (from SPEC §8)

- **K2** weight degeneration: any sleeve > 80% > 80% of rebal months → kill
- **K3** turnover > 100%/yr **and** Sharpe edge < +0.10 → kill
- **K4** MDD > MDD(S1) + 5pp on any dataset → kill

## Expected pre-run intuition

Bestfolio's Aggressive WF claim (19.8% CAGR, Sharpe 1.27) is over a 30y
window with leveraged sleeves. Our universe is more conservative (S1
incumbent ~10.7% CAGR / Sharpe 1.109), so we expect:

- Sharpe meta in [1.10, 1.25] range — driven by S2/S3 hedging S1 in stress
- CAGR meta in [10%, 13%] range — bounded by sleeve CAGRs (no leverage gain)
- MDD meta likely in [13%, 18%] — between S3 (cleanest) and S1 (incumbent)

If meta lands at S1 ± noise (Sharpe 1.10 ± 0.03), the WF adds nothing —
F1+SPLIT static dominates. If meta lands at S1 + 0.10 with similar MDD,
strong evidence for the methodology.

## Citations

- bestfolio.app/blog/walk-forward-portfolios — base methodology
- `[advances_fin_ml, p.105-108]` — embargoed CV
- `[advances_fin_ml, p.196-202]` — bootstrap CI
- `[advances_fin_ml, p.222-223]` — DSR n_trials cumulative
- `[risk_parity, ch.5]` — sleeve thesis (S1, S2, S3)
