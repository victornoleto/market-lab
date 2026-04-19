# [SHORT-HOLD CFD] V2-L2 iter 35 — `gayed_lrs_L2_off_tlt` FAIL (WF, Sharpe<2, MDD>25%)

**Phase:** 3.5a-V2 — Plano A LAST ATTEMPT · Lead **V2-L2** · Registry 20/27
**Path tag:** [SHORT-HOLD CFD] (Pepperstone Razor CFD; swap -0.005%/d long, comm $3.50/side, spread 2bp half, slip 2bp round)
**Window:** 2001-05-14 → 2026-04-14 (25y, 6266 bars, 578 switches)

## Result

| Split | Sharpe | CAGR | MaxDD |
|-------|-------:|-----:|------:|
| IS (2001–2017) | 2.171 | 59.14% | -17.75% |
| **OOS (2018–2023)** | **1.911** | **64.11%** | **-26.15%** |
| FWD (2024–2026-04) | 1.760 | 53.00% | -14.72% |
| WF (8 win) | 1.00 profitable, max-win-DD 26.2% | — | ❌ cap 25% |
| Median hold | 5.5d | — | — |

**Subset gates:** 4/7 PASS. Failed: `wf_pass`, `oos_sharpe_ge_2`, `oos_maxdd_le_25pct`.

## Iter 34 prediction vs actual

| Metric | Predicted | Actual | Δ |
|--------|----------:|-------:|---:|
| OOS Sharpe | ~2.0 | 1.911 | -4.5% |
| OOS MDD | ~-27% | -26.15% | +3.1% |
| WF | FAIL | FAIL | HIT |

**Predição iter 34 HIT** (3/3 dimensions within 5%). LRS+TLT colapsa exatamente onde EMA100+TLT e SMA200+TLT colapsaram — TLT está correlacionado com SPY em rate-shock regimes `[systematic_trading, ch.8]`.

## Cross-signal ranking (off_tlt L2)

| Signal | OOS Sharpe | OOS MDD | WF |
|--------|-----------:|--------:|----|
| EMA100 | 2.017 | -27.7% | FAIL |
| **LRS** | **1.911** | **-26.2%** | **FAIL** |
| SMA200 | 1.467 | -36.6% | FAIL |

Ranking Sharpe: EMA100 > LRS > SMA200 (mesmo padrão de off_cash e off_gld).
Mas TLT off-regime **fails gates em todos os signals** cross-signal — não é problema
de signal, é problema de asset pair: TLT-SPY correlation em crises de juros
(2018-Q4, 2022 inflation shock) anula o hedge `[leverage_for_the_long_run, p.16]`
(Gayed usa Treasury mas SHV/TLT mix; Treasury longo é mais correlacionado com risk-on
em rate-shock episodes).

## Cross-off-regime (LRS L2)

| Off-regime | OOS Sharpe | OOS MDD | WF | Verdict |
|------------|-----------:|--------:|----|---------|
| cash | 2.072 | -21.9% | PASS | ★ SUBSET PASS |
| **tlt** | **1.911** | **-26.2%** | **FAIL** | FAIL |
| gld | pending | — | — | — |

LRS L2 replicates EMA100 L2 pattern: cash/gld are valid off-regime, tlt fails gates.
**Off-regime asset choice > signal choice** at L2 ceiling.

## Progression EMA100 vs LRS (L2, off_cash)

| Signal | OOS Sharpe | OOS MDD | Switches |
|--------|-----------:|--------:|---------:|
| SMA200 | 1.545 | -21.9% | 319 |
| **LRS (composite)** | **2.072** | **-21.9%** | **578** |
| EMA100 | 2.171 | -20.1% | 616 |

LRS sits between the two rigid signals — exactly as hypothesized. Composite vote
of {SMA200, EMA100, drawdown-from-high} is more reactive than SMA200 but more
stable than raw EMA100 `[leverage_for_the_long_run, p.13]`.

## Next

- `gayed_lrs_L2_off_gld` (iter 36). Predict: OOS Sharpe ~2.15-2.20 (gld > cash > tlt
  pattern from EMA100 L2 triplet), OOS MDD ~-20-22%, WF PASS. Candidate for 4th
  V2 ★ SUBSET PASS.

## Artefatos

- Config JSON: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_lrs_L2_off_tlt.json`
- Config MD: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_lrs_L2_off_tlt.md`
- Registry: 20/27 done, 7 LRS pending
- Iter: 35
- Jornada anterior: `2026-04-18-2220-phase3.5a-v2-L2-lrs-L2-cash-PASS.md` (LRS triplet started)

## Citations

- `[leverage_for_the_long_run, p.13, p.16, p.17]` — Gayed signal composite + off-regime asset choice
- `[systematic_trading, ch.8]` — TLT-SPY rate-shock correlation break
- `[advances_fin_ml, ch.11]` — WF 6/8 gate + 25% DD cap
- `[leverage_space, Vince]` — L2 Kelly f/2 PoR cap (MDD -26% > f/2 cushion on TLT)
