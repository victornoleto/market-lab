# Long-window iter 079 — winner partial validation

iter 079 uses universe {SPY, QQQ, EFA, TLT, GLD} + AGG. Synth data lacks EFA + AGG analogs. Two substitution scenarios:

## Scenario `A_4asset`

- Selectable: ['SPY', 'QQQ', 'TLT', 'GLD']
- Synth substitutions: `{'SPY': 'SPYSIM', 'QQQ': 'QQQSIM', 'TLT': 'ZROZSIM', 'GLD': 'GLDSIM', 'AGG': 'ZROZSIM'}`
- Config: top_k=1, lookback=12m, abs_threshold=0.0, cost=10.0bps

| metric | value | Δ vs SPYSIM b&h |
|---|---|---|
| Sharpe | 0.523 | -0.159 |
| CAGR | 10.03% | -1.45pp |
| MDD | 49.52% | -5.62pp |

## Scenario `B_5asset_qqq_as_efa`

- Selectable: ['SPY', 'QQQ', 'EFA', 'TLT', 'GLD']
- Synth substitutions: `{'SPY': 'SPYSIM', 'QQQ': 'QQQSIM', 'EFA': 'QQQSIM', 'TLT': 'ZROZSIM', 'GLD': 'GLDSIM', 'AGG': 'ZROZSIM'}`
- Config: top_k=1, lookback=12m, abs_threshold=0.0, cost=10.0bps

| metric | value | Δ vs SPYSIM b&h |
|---|---|---|
| Sharpe | 0.523 | -0.159 |
| CAGR | 10.03% | -1.45pp |
| MDD | 49.52% | -5.62pp |

## Reading the results

- Both scenarios are partial. Scenario A drops the international leg (EFA), so it tests the 4-asset variant rather than the original 5-asset. Scenario B uses QQQSIM as a stand-in for EFA, which is wrong (QQQ is US large-tech, not international developed) but at least preserves the 5-asset structure.
- ZROZSIM substitutes for both TLT and AGG (long-bond proxy). AGG is shorter duration, so this overstates the bond leg's volatility contribution.
- Treat as **directional evidence**, not exact validation.
