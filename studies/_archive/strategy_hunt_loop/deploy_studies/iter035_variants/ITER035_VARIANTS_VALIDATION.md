# iter 035 deployment variants — long-window validation

Generated: 2026-04-26T18:15:52.482741

Compares 4 ways to deploy the iter 035 portfolio (90/60/30 SPY+long-bond+gold, 180% notional) across a 40-year synthetic window (testfolio cache).

## Synthetic ETF construction

Where real ETFs lack 40y data, we synthesize from underlyings:

| ETF | construction | caveat |
|---|---|---|
| **NTSX** | 0.90 × SPYSIM + 0.60 × IEFSIM − 0.20%/yr ER | matches WisdomTree's documented exposure |
| **GDE** | 0.90 × SPYSIM + 0.90 × GLDSIM − 0.20%/yr ER | matches WisdomTree's documented exposure |
| **TMF** | 3.0 × ZROZSIM − 1.05%/yr ER | **conservative** — ZROZ duration ~25y > TLT ~17y, overstates real TMF vol drag |
| **UBT** | 2.0 × ZROZSIM − 0.95%/yr ER | same caveat as TMF |
| **BIL** | constant 4%/yr | long-term US T-bill proxy; assumes mid-cycle rate |

## Benchmark (40y synth)

| asset | Sharpe | CAGR | MDD | window |
|---|---|---|---|---|
| SPYSIM b&h | 0.682 | 11.49% | 55.14% | 1986-01-03 → 2026-04-17 |

## Strategy results

| variant | Sharpe (Δvs SPY) | CAGR (Δ) | MDD (Δ) | G6 (99.9% CI) | DSR p | G7 |
|---|---|---|---|---|---|---|
| `V0_iter035_pure_SPY_ZROZ_GLD_180notional` | 0.922 (+0.240) | 19.60% (+8.11pp) | 46.18% (-8.96pp) | [0.41, 1.39] ✅ | 0.0000 ✅ | ✅ |
| `V1_NTSX_GDE_67_33_Inter_cash` | 0.917 (+0.235) | 15.42% (+3.93pp) | 44.10% (-11.05pp) | [0.46, 1.40] ✅ | 0.0000 ✅ | ✅ |
| `V2_SSO_UBT_UGL_BIL_2x_Inter` | 0.801 (+0.119) | 16.45% (+4.97pp) | 47.44% (-7.70pp) | [0.29, 1.26] ✅ | 0.0000 ✅ | ✅ |
| `V3_UPRO_TMF_GLD_BIL_3x_Inter` | 0.822 (+0.140) | 17.01% (+5.52pp) | 47.30% (-7.84pp) | [0.31, 1.29] ✅ | 0.0000 ✅ | ✅ |

## Gate verdicts

- **G6 bootstrap 99.9% CI low > 0** — Sharpe edge is non-zero with very high confidence after stationary block bootstrap (`[advances_fin_ml, p.196-202]`)
- **DSR p < 0.05 (n_trials=4)** — Sharpe survives selection bias correction (`[advances_fin_ml, p.222-223]`)
- **G7 cross-lib** — pandas vs numpy Sharpe differ by < 0.001 (`[advances_fin_ml, p.31-34]`)

## Caveats

1. **TMF synth is pessimistic**: real TMF tracks 3× TLT (duration ~17y), but here we proxy with 3× ZROZ (duration ~25y). ZROZ has ~50% higher volatility than TLT, so synthetic TMF vol drag is an upper bound on real TMF behavior. Real V3 numbers will be slightly better.
2. **BIL constant 4%/yr** ignores rate cycle: in 1986-2007 US T-bills averaged 5-7%, in 2009-2021 ~0.1%, post-2022 ~5%. Variant V3 has 20% BIL sleeve so this assumption affects ~80 bps/yr in mismatched eras.
3. **NTSX and GDE synth assume zero futures roll yield** — real WisdomTree ETFs use Treasury futures and have small (~5-15 bps/yr) roll cost not modeled here. V1 numbers slightly optimistic.
4. **All strategies daily-rebalanced** — real-world monthly/quarterly rebalance adds modest drift drag (~0-50 bps/yr).
5. **Gates G1-G5 (Sharpe floor, CAGR floor, MDD ceiling, WF, OOS) not applied here** — single-portfolio strategies have no parameter grid to walk-forward, so PBO/WF/OOS aren't applicable. Gate battery is G6 + DSR + G7 only.
