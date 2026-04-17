# Phase 3.5b Task 7a — B1c re-run with FFR-aware LETF cost

**Grid:** 72 configs (Phase 3 canonical axes, gold_weight=0.0).
**Window:** 1970-01-02 → 2026-04-14 (seam 2001-05-14, KF Mkt+RF pre, Tiingo SPY post).
**Cost model:** SW=1.1, SP=0.004/yr, ER=0.0095/yr, FFR daily = Ken French RF × 252.
**Splits:** IS 1970-01-02→2000-12-31 · OOS 2001-01-01→2015-12-31 · Stress 2016-01-01→2026-04-14.

## Grid-level verdict

- PBO (FFR-aware) = **0.000** (pass=YES, threshold <0.5).
- Passing configs: **13 / 72**.
- New top-passing config (by OOS Sharpe): cid=37 EMA100 band=0.00% lev=2.0x · OOS Sharpe 1.678, bootstrap 99.9% CI [0.985, 2.419].

## Phase 3 winner (cid=37: EMA100/2x/band 0%) — FFR-aware

- Verdict: **PASS**
- IS Sharpe: 1.644 (CAGR 37.49%, MDD -20.84%)
- OOS Sharpe: 1.678 (CAGR 39.65%, MDD -15.78%)
- Stress Sharpe: 1.916 (CAGR 49.72%, MDD -18.38%)
- WF profitable ratio: 1.000 (max window MDD 20.84%)
- DSR p-value (OOS, n_trials=72): 2.189e-05
- Bootstrap OOS 99.9% CI: [0.985, 2.419]

## Per-config Sharpe delta (top 15 by OOS_sh_new)

```
 cid filter  lb  band   lev  OOS_sh_base  OOS_sh_new  OOS_dSh verdict_base verdict_new
  38    EMA 100 0.000 3.000        1.781       1.718   -0.063         FAIL        FAIL
  37    EMA 100 0.000 2.000        1.724       1.678   -0.046         PASS        PASS
  36    EMA 100 0.000 1.000        1.592       1.595    0.003         PASS        PASS
   2    SMA 100 0.000 3.000        1.623       1.562   -0.061         FAIL        FAIL
  11    SMA 125 0.000 3.000        1.616       1.554   -0.061         FAIL        FAIL
  47    EMA 125 0.000 3.000        1.608       1.545   -0.063         FAIL        FAIL
   1    SMA 100 0.000 2.000        1.568       1.524   -0.045         PASS        PASS
  56    EMA 150 0.000 3.000        1.577       1.513   -0.064         FAIL        FAIL
  10    SMA 125 0.000 2.000        1.558       1.513   -0.045         PASS        PASS
  46    EMA 125 0.000 2.000        1.553       1.507   -0.046         PASS        PASS
  55    EMA 150 0.000 2.000        1.524       1.477   -0.046         PASS        PASS
  20    SMA 150 0.000 3.000        1.524       1.462   -0.062         FAIL        FAIL
   0    SMA 100 0.000 1.000        1.442       1.445    0.003         PASS        PASS
  45    EMA 125 0.000 1.000        1.426       1.429    0.003         PASS        PASS
   9    SMA 125 0.000 1.000        1.425       1.427    0.003         PASS        PASS
```

## Interpretation

✅ Phase 3 winner **survives** FFR-aware cost model on all gates. Flat-fee edge was not an artefact of cost under-modelling; allocation doc (Task 8) may cite a ~X%/yr CAGR haircut but no verdict change.

## Citations

- FFR-aware cost formula: `data/external/README.md` Task 7a section.
- Gayed flat-fee original (intact): `[leverage_for_the_long_run, p.16]`.
- Gate thresholds: `[advances_fin_ml, p.208-211]` (PBO<0.5), `[advances_fin_ml, p.196-202]` (DSR, bootstrap CI).
- Winner-immutability rule Phase 3.5b: constraint #4 of `docs/self_improvement/memory.md`.
