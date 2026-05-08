# Long-window iter 079 — winner partial validation

iter 079 uses universe {SPY, QQQ, EFA, TLT, GLD} + AGG. Synth data lacks EFA + AGG analogs. Two substitution scenarios:

## Scenario `A_5asset_real_proxies`

- Selectable: ['SPY', 'QQQ', 'EFA', 'TLT', 'GLD']
- Synth substitutions: `{'SPY': 'SPYSIM', 'QQQ': 'QQQSIM', 'EFA': 'VEASIM', 'TLT': 'IEFSIM', 'GLD': 'GLDSIM', 'AGG': 'BNDSIM'}`
- Config: top_k=1, lookback=12m, abs_threshold=0.0, cost=10.0bps

| metric | value | Δ vs SPYSIM b&h |
|---|---|---|
| Sharpe | 0.707 | +0.025 |
| CAGR | 13.08% | +1.59pp |
| MDD | 46.82% | -8.33pp |

## Scenario `B_5asset_zroz_long_bond`

- Selectable: ['SPY', 'QQQ', 'EFA', 'TLT', 'GLD']
- Synth substitutions: `{'SPY': 'SPYSIM', 'QQQ': 'QQQSIM', 'EFA': 'VEASIM', 'TLT': 'ZROZSIM', 'GLD': 'GLDSIM', 'AGG': 'BNDSIM'}`
- Config: top_k=1, lookback=12m, abs_threshold=0.0, cost=10.0bps

| metric | value | Δ vs SPYSIM b&h |
|---|---|---|
| Sharpe | 0.614 | -0.068 |
| CAGR | 12.13% | +0.64pp |
| MDD | 49.52% | -5.62pp |

## Scenario `C_4asset_no_efa`

- Selectable: ['SPY', 'QQQ', 'TLT', 'GLD']
- Synth substitutions: `{'SPY': 'SPYSIM', 'QQQ': 'QQQSIM', 'TLT': 'IEFSIM', 'GLD': 'GLDSIM', 'AGG': 'BNDSIM'}`
- Config: top_k=1, lookback=12m, abs_threshold=0.0, cost=10.0bps

| metric | value | Δ vs SPYSIM b&h |
|---|---|---|
| Sharpe | 0.685 | +0.003 |
| CAGR | 12.51% | +1.02pp |
| MDD | 46.82% | -8.33pp |

## Reading the results

- Both scenarios are partial. Scenario A drops the international leg (EFA), so it tests the 4-asset variant rather than the original 5-asset. Scenario B uses QQQSIM as a stand-in for EFA, which is wrong (QQQ is US large-tech, not international developed) but at least preserves the 5-asset structure.
- ZROZSIM substitutes for both TLT and AGG (long-bond proxy). AGG is shorter duration, so this overstates the bond leg's volatility contribution.
- Treat as **directional evidence**, not exact validation.
