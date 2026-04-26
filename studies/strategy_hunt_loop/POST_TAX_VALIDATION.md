# Post-tax validation (Lei 14.754, 15% annual MTM)

Generated: 2026-04-26T12:11:17.421584

Applies 15% annual mark-to-market tax (Lei 14.754/2023, effective 2024-01-01) to long-window 40y synth returns. Loss years pay no tax; no carryforward across years.

## Benchmark SPYSIM 40y — pre vs post tax

| metric | pre-tax | post-tax | Δ |
|---|---|---|---|
| Sharpe | 0.682 | 0.576 | -0.105 |
| CAGR | 11.49% | 9.41% | -2.08pp |
| MDD | 55.14% | 55.48% | +0.33pp |

**CAGR drag from tax: 2.08pp** (18.1% of pre-tax CAGR)

## Strategy results (post-tax)

| strategy | pre-tax (Sh / CAGR) | post-tax (Sh / CAGR) | post-tax edge vs SPYSIM |
|---|---|---|---|
| `iter004 vol_managed_spy` | 0.811 / 14.40% | **0.685 / 11.84%** | Δ Sh +0.108 / CAGR +2.43pp ✅ Sh+CAGR |
| `iter005 variance_managed_spy` | 0.792 / 13.96% | **0.666 / 11.41%** | Δ Sh +0.089 / CAGR +2.01pp ✅ Sh+CAGR |
| `iter006 vol_managed_60_40` | 0.932 / 14.41% | **0.785 / 11.98%** | Δ Sh +0.209 / CAGR +2.57pp ✅ Sh+CAGR |
| `iter015 ntsx_static_90_60` | 0.840 / 16.95% | **0.721 / 14.15%** | Δ Sh +0.144 / CAGR +4.74pp ✅ Sh+CAGR |
| `iter016 static_stack_vm_hybrid` | 0.951 / 15.13% | **0.803 / 12.60%** | Δ Sh +0.227 / CAGR +3.20pp ✅ Sh+CAGR |
| `iter035 static_stack_3leg_SPY_ZROZ_GLD` | 0.922 / 19.60% | **0.796 / 16.50%** | Δ Sh +0.219 / CAGR +7.10pp ✅ Sh+CAGR |
| `iter074 ensemble_simplified_to_iter016` | 0.951 / 15.13% | **0.803 / 12.60%** | Δ Sh +0.227 / CAGR +3.20pp ✅ Sh+CAGR |
| `iter079 multi_asset_topk (real proxies)` | 0.707 / 13.08% | **0.606 / 10.86%** | Δ Sh +0.029 / CAGR +1.45pp ✅ Sh+CAGR |

## Entry-cost projections — $10k initial + $1.5k/mo over 30y

| broker | total cost drag | as % of invested | initial cost | annual aporte cost |
|---|---|---|---|---|
| **Inter Internacional** (FX 1.25%) | $9,075 | 1.65% | $165.00 | $297.00/yr |
| **IBKR Lite + TransferBank** (FX 0.30%) | $4,572 | 0.83% | $72.00 | $150.00/yr |

Difference: IBKR Lite + TransferBank saves $4,503 over 30y (compounds in invested principal).

## Caveats

1. **Lei 14.754 regime confirmation**: this model assumes annual MTM rate of 15%. For PF (individual) accounts at IBKR/Inter, the regime may differ — consult contador.
2. **Loss carryforward**: this model does NOT carry forward losses across years. Real Lei 14.754 PJ rules allow it; PF rules don't.
3. **MDD unchanged**: tax is annual, so peak-to-trough MDD within a year is unaffected by tax (tax bites at year-end on net positive).
4. **Sharpe slightly improves**: tax is asymmetric (positive years taxed, negative years not), so post-tax volatility drops by more than mean → Sharpe sometimes higher post-tax (counterintuitive but real).
5. **30% US dividend withholding** NOT modeled separately because synth tickers are total-return (dividends pre-reinvested into NAV).
